from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from app.config import settings


def create_index() -> None:
    """
    Create or update the Azure AI Search index used by the app.

    The important design choice here is that each chunk is its own document.
    That gives you much more precise retrieval later.
    """
    client = SearchIndexClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY),
    )

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="file_name", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="file_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="source_url", type=SearchFieldDataType.String),
        SimpleField(name="chunk_number", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=settings.AZURE_OPENAI_EMBEDDING_DIMENSIONS,
            vector_search_profile_name="my-vector-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="my-hnsw-config")],
        profiles=[
            VectorSearchProfile(
                name="my-vector-profile",
                algorithm_configuration_name="my-hnsw-config",
            )
        ],
    )

    index = SearchIndex(
        name=settings.AZURE_SEARCH_INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
    )

    result = client.create_or_update_index(index)
    print(f"Created or updated index: {result.name}")


if __name__ == "__main__":
    create_index()
