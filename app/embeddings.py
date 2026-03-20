from openai import AzureOpenAI
from app.config import settings

# Shared Azure OpenAI client for embedding requests.
embedding_client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_KEY,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
)


def generate_embedding(text: str) -> list[float]:
    """
    Convert text into a dense vector embedding.

    In Azure OpenAI, the 'model' argument should be the name of your Azure deployment.
    """
    response = embedding_client.embeddings.create(
        model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        input=text,
    )
    return response.data[0].embedding
