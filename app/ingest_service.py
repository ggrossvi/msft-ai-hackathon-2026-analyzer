import os
import uuid
from app.parsers import extract_text
from app.chunking import chunk_text
from app.embeddings import generate_embedding
from app.search_index import upload_chunk_documents


def ingest_file_into_search(*, file_name: str, file_bytes: bytes, blob_url: str) -> dict:
    """
    Full ingestion pipeline for one file.

    Steps:
    1. Extract text from the file
    2. Break the text into chunks
    3. Embed each chunk
    4. Upload chunk documents to Azure AI Search
    """
    extracted_text = extract_text(file_name, file_bytes)
    chunks = chunk_text(extracted_text)

    if not chunks:
        return {
            "file_name": file_name,
            "chunks_indexed": 0,
            "message": "No text content was extracted from the file.",
        }

    file_ext = os.path.splitext(file_name)[1].lower().replace(".", "")
    documents_to_upload = []

    for i, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)

        documents_to_upload.append(
            {
                "id": str(uuid.uuid4()),
                "file_name": file_name,
                "file_type": file_ext,
                "source_url": blob_url,
                "chunk_number": i,
                "content": chunk,
                "content_vector": embedding,
            }
        )

    upload_chunk_documents(documents_to_upload)

    return {
        "file_name": file_name,
        "chunks_indexed": len(documents_to_upload),
        "message": "File parsed, chunked, embedded, and indexed successfully.",
    }
