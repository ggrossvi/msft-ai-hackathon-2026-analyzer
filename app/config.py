import os
from dotenv import load_dotenv

# Load environment variables from .env into the process.
load_dotenv()


def require_env(name: str) -> str:
    """
    Read a required environment variable.
    Fail early with a clear message if it is missing.
    """
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


class Settings:
    """
    Central configuration object.
    Keeping config in one place makes the project easier to maintain.
    Make Search/OpenAI env vars optional so app startup only requires Blob connection string.
    """


    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING = require_env("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_BLOB_DOCUMENTS_CONTAINER = os.getenv("AZURE_BLOB_DOCUMENTS_CONTAINER", "documents")
    AZURE_BLOB_IMAGES_CONTAINER = os.getenv("AZURE_BLOB_IMAGES_CONTAINER", "images")
    AZURE_BLOB_VIDEOS_CONTAINER = os.getenv("AZURE_BLOB_VIDEOS_CONTAINER", "videos")
    AZURE_BLOB_RAW_CONTAINER = os.getenv("AZURE_BLOB_RAW_CONTAINER", "raw")

    # Azure AI Search (optional in Blob-only mode)
    AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
    AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

    # Azure OpenAI (optional in Blob-only mode)
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    AZURE_OPENAI_EMBEDDING_DIMENSIONS = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", "1536"))

    # App behavior
    APP_ENV = os.getenv("APP_ENV", "dev")
    MAX_CHUNK_SIZE = int(os.getenv("MAX_CHUNK_SIZE", "1200"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))


settings = Settings()
