from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.blob_service import upload_stream_to_blob
from app.config import settings
from app.ingest_service import ingest_file_into_search
from app.models import SearchRequest, SearchResponse, SearchResultItem
from app.search_index import hybrid_search


app = FastAPI(
    title="Azure Blob Upload API (Blob + optional Search)",
    description="Upload files to Azure Blob Storage and optionally index into Azure AI Search.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _search_configured() -> bool:
    """True when env vars for Azure AI Search + embedding calls are all set."""
    return all(
        [
            settings.AZURE_SEARCH_ENDPOINT,
            settings.AZURE_SEARCH_KEY,
            settings.AZURE_SEARCH_INDEX_NAME,
            settings.AZURE_OPENAI_ENDPOINT,
            settings.AZURE_OPENAI_KEY,
            settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        ]
    )


@app.get("/health")
def health_check():
    """Basic endpoint to verify the API is running."""
    search_enabled = _search_configured()
    return {
        "status": "ok",
        "search_enabled": search_enabled,
        "mode": "search-enabled" if search_enabled else "blob-only",
    }

    #return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
def search_documents(body: SearchRequest):
    """
    Hybrid keyword + vector search over indexed chunks.
    Requires Search + OpenAI embedding env vars; returns 503 if not configured.
    """
    if not _search_configured():
        raise HTTPException(
            status_code=503,
            detail="Search is not configured. Set Azure AI Search and OpenAI embedding env vars.",
        )
    q = (body.query or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="query must not be empty.")
    top_k = body.top_k if body.top_k is not None else settings.TOP_K_RESULTS
    if top_k < 1 or top_k > 50:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 50.")

    raw = hybrid_search(q, top_k=top_k)
    items: list[SearchResultItem] = []
    for r in raw:
        # Azure SDK returns dict-like rows with document fields + @search.score
        items.append(
            SearchResultItem(
                id=str(r.get("id", "")),
                file_name=str(r.get("file_name", "")),
                source_url=str(r.get("source_url", "")),
                content=str(r.get("content", "")),
                chunk_number=int(r.get("chunk_number", 0)),
                score=r.get("@search.score"),
            )
        )
    return SearchResponse(query=q, results=items)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing uploaded filename.")

        search_enabled = _search_configured()

        blob_info = None
        indexing_info = None

        if search_enabled:
            # Read uploaded bytes once (so we can upload + index).
            file_bytes = await file.read()

            # Upload using the same bytes.
            blob_info = upload_stream_to_blob(
                original_filename=file.filename,
                stream=BytesIO(file_bytes),
                content_type=file.content_type,
            )

            # Index only after upload succeeds.
            indexing_info = ingest_file_into_search(
                file_name=file.filename,  # used to choose parser by extension
                file_bytes=file_bytes,  # used for text extraction + embedding
                blob_url=blob_info["blob_url"],  # used as source_url in Search docs
            )
        else:
            # Blob-only path (keep it streaming to avoid reading everything).
            # Note: upload_stream_to_blob handles streaming; we only seek/reset
            # if the underlying stream supports it.
            if getattr(file.file, "seekable", lambda: False)():
                file.file.seek(0)

            blob_info = upload_stream_to_blob(
                original_filename=file.filename,
                stream=file.file,
                content_type=file.content_type,
            )

        return {
            "message": "Upload completed.",
            "blob": blob_info,
            "indexing": indexing_info,  # null/None when search is disabled
            "search_enabled": search_enabled,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))