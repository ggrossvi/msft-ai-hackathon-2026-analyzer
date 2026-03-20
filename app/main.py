from fastapi import FastAPI, File, HTTPException, UploadFile
from app.blob_service import upload_stream_to_blob
from app.ingest_service import ingest_file_into_search
from app.models import SearchRequest, SearchResponse, SearchResultItem
from app.search_index import hybrid_search

app = FastAPI(
    title="Azure RAG Pipeline Starter",
    description="Upload files to Blob Storage, index them into Azure AI Search, and search with hybrid retrieval.",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    """Basic endpoint to verify the API is running."""
    return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to Azure Blob Storage and then index it into Azure AI Search.

    This endpoint gives you a very simple hackathon workflow:
    one upload call stores the file and makes it searchable.
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing uploaded filename.")

        # Step 1: stream the raw file into Blob Storage.
        # NOTE: upload_blob consumes the stream, so we rewind before reading bytes for ingestion.
        if getattr(file.file, "seekable", lambda: False)():
            file.file.seek(0)
        blob_info = upload_stream_to_blob(
            original_filename=file.filename,
            stream=file.file,
            content_type=file.content_type,
        )

        # Step 2: read bytes for parsing/chunking/embedding (needed by your current ingestion pipeline).
        if getattr(file.file, "seekable", lambda: False)():
            file.file.seek(0)
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Step 2: parse the file, chunk it, embed it, and push it into Search.
        ingest_result = ingest_file_into_search(
            file_name=file.filename,
            file_bytes=file_bytes,
            blob_url=blob_info["blob_url"],
        )

        return {
            "message": "Upload and indexing completed.",
            "blob": blob_info,
            "indexing": ingest_result,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/search", response_model=SearchResponse)
def search_documents(payload: SearchRequest):
    """
    Search the RAG index.

    Results come back at the chunk level because chunk retrieval is the normal
    building block for downstream RAG chat flows.
    """
    try:
        raw_results = hybrid_search(query=payload.query, top_k=payload.top_k)
        results = []

        for item in raw_results:
            results.append(
                SearchResultItem(
                    id=item.get("id", ""),
                    file_name=item.get("file_name", ""),
                    source_url=item.get("source_url", ""),
                    content=item.get("content", ""),
                    chunk_number=item.get("chunk_number", 0),
                    score=item.get("@search.score"),
                )
            )

        return SearchResponse(query=payload.query, results=results)

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
