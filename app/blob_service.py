import os
import uuid
from typing import BinaryIO

from azure.storage.blob import BlobServiceClient

from app.config import settings

# One shared BlobServiceClient for the entire app.
blob_service_client = BlobServiceClient.from_connection_string(
    settings.AZURE_STORAGE_CONNECTION_STRING
)


def choose_container(file_name: str, content_type: str | None = None) -> str:
    """
    Decide which container to use.

    Blob Storage can store any file type. We split files into separate containers
    to keep the project organized and make the pipeline easier to reason about.
    """
    lower_name = file_name.lower()
    content_type = (content_type or "").lower()

    document_exts = (".pdf", ".docx", ".doc", ".txt", ".md", ".pptx", ".xlsx")
    image_exts = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
    video_exts = (".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm")

    if lower_name.endswith(document_exts):
        return settings.AZURE_BLOB_DOCUMENTS_CONTAINER
    if lower_name.endswith(image_exts):
        return settings.AZURE_BLOB_IMAGES_CONTAINER
    if lower_name.endswith(video_exts):
        return settings.AZURE_BLOB_VIDEOS_CONTAINER

    # Fallback to MIME type if the extension is not helpful.
    if content_type.startswith("image/"):
        return settings.AZURE_BLOB_IMAGES_CONTAINER
    if content_type.startswith("video/"):
        return settings.AZURE_BLOB_VIDEOS_CONTAINER

    return settings.AZURE_BLOB_RAW_CONTAINER


def ensure_container_exists(container_name: str) -> None:
    """
    Create the container if it does not already exist.
    Safe to call many times.
    """
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()


def make_blob_name(original_filename: str) -> str:
    """
    Create a collision-resistant blob name while preserving the original extension.
    """
    safe_basename = os.path.basename(original_filename or "upload") or "upload"
    return f"{uuid.uuid4()}_{safe_basename}"


def upload_bytes_to_blob(
    *, original_filename: str, data: bytes, content_type: str | None = None
) -> dict:
    """
    Upload raw bytes into Azure Blob Storage and return metadata about the upload.
    """
    blob_name = make_blob_name(original_filename)
    container_name = choose_container(blob_name, content_type)
    ensure_container_exists(container_name)

    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name,
    )

    blob_client.upload_blob(
        data,
        overwrite=True,
        content_type=content_type,
    )

    return {
        "container": container_name,
        "blob_name": blob_name,
        "blob_url": blob_client.url,
    }


def upload_stream_to_blob(
    *,
    original_filename: str,
    stream: BinaryIO,
    content_type: str | None = None,
) -> dict:
    """
    Upload a file stream into Azure Blob Storage and return metadata about the upload.

    This avoids loading the entire file into memory at the upload step.
    """
    blob_name = make_blob_name(original_filename)
    container_name = choose_container(blob_name, content_type)
    ensure_container_exists(container_name)

    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name,
    )

    # upload_blob consumes the stream, so callers should rewind if they need it later.
    blob_client.upload_blob(
        stream,
        overwrite=True,
        content_type=content_type,
    )

    return {
        "container": container_name,
        "blob_name": blob_name,
        "blob_url": blob_client.url,
    }
