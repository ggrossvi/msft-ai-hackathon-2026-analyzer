import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Load environment variables from .env
load_dotenv()

# Get connection string securely
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

if not conn_str:
    raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING in .env")

# Create Blob client
blob_service = BlobServiceClient.from_connection_string(conn_str)

# Choose container
container_name = "documents"

# Create blob client
blob_client = blob_service.get_blob_client(
    container=container_name,
    blob="test.txt"
)

# Upload test content
blob_client.upload_blob(b"Hello from .env setup!", overwrite=True)

print("✅ Upload successful!")