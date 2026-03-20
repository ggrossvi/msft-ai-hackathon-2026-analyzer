from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from app.config import settings
from app.embeddings import generate_embedding

# Shared Azure AI Search client.
search_client = SearchClient(
    endpoint=settings.AZURE_SEARCH_ENDPOINT,
    index_name=settings.AZURE_SEARCH_INDEX_NAME,
    credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY),
)


def upload_chunk_documents(documents: list[dict]) -> None:
    """
    Push a list of chunk documents into Azure AI Search.
    Each chunk becomes one searchable record.
    """
    if not documents:
        return
    search_client.upload_documents(documents=documents)


def hybrid_search(query: str, top_k: int | None = None) -> list[dict]:
    """
    Run hybrid retrieval:
    - keyword search with search_text
    - vector search with the embedding of the query

    This is a strong default for hackathon demos because it usually returns
    better results than keyword-only or vector-only search.
    """
    top_k = top_k or settings.TOP_K_RESULTS
    query_vector = generate_embedding(query)

    results = search_client.search(
        search_text=query,
        vector_queries=[
            {
                "kind": "vector",
                "vector": query_vector,
                "fields": "content_vector",
                "k": top_k,
            }
        ],
        top=top_k,
    )

    return list(results)
