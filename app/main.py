from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.blob_service import upload_stream_to_blob
from app.config import settings
from app.ingest_service import ingest_file_into_search


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


@app.get("/health")
def health_check():
    """Basic endpoint to verify the API is running."""
    search_enabled = all(
        [
            settings.AZURE_SEARCH_ENDPOINT,
            settings.AZURE_SEARCH_KEY,
            settings.AZURE_SEARCH_INDEX_NAME,
            settings.AZURE_OPENAI_ENDPOINT,
            settings.AZURE_OPENAI_KEY,
            settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        ]
    )
    return {
        "status": "ok",
        "search_enabled": search_enabled,
        "mode": "search-enabled" if search_enabled else "blob-only",
    }

    #return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing uploaded filename.")

        search_enabled = all(
            [
                settings.AZURE_SEARCH_ENDPOINT,
                settings.AZURE_SEARCH_KEY,
                settings.AZURE_SEARCH_INDEX_NAME,
                settings.AZURE_OPENAI_ENDPOINT,
                settings.AZURE_OPENAI_KEY,
                settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            ]
        )

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