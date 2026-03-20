from typing import List, Optional
from pydantic import BaseModel


class SearchRequest(BaseModel):
    """Request body for a search call."""

    query: str
    top_k: Optional[int] = 5


class SearchResultItem(BaseModel):
    """One chunk-level search result."""

    id: str
    file_name: str
    source_url: str
    content: str
    chunk_number: int
    score: Optional[float] = None


class SearchResponse(BaseModel):
    """Structured response returned by the search endpoint."""

    query: str
    results: List[SearchResultItem]
