from fastapi import FastAPI, File, HTTPException, UploadFile
from app.blob_service import upload_stream_to_blob
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title="Azure Blob Upload API (Blob-only)",
    description="Upload files to Azure Blob Storage without search/indexing.",
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
    search_enabled = all([
    settings.AZURE_SEARCH_ENDPOINT,
    settings.AZURE_SEARCH_KEY,
    settings.AZURE_SEARCH_INDEX_NAME,
    settings.AZURE_OPENAI_ENDPOINT,
    settings.AZURE_OPENAI_KEY,
    settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    ])
    return {
    "status": "ok",
    "search_enabled": search_enabled,
    "mode": "search-enabled" if search_enabled else "blob-only"
    }

    #return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to Azure Blob Storage only (no AI Search/OpenAI indexing).
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing uploaded filename.")

        # Stream upload directly to Blob to avoid loading whole file into memory.
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
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))