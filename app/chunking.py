from app.config import settings


def chunk_text(text: str, max_chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """
    Split text into overlapping chunks.

    Why this matters:
    - embeddings work better on smaller pieces of content
    - search results are more precise
    - overlap helps preserve nearby context between chunks
    """
    max_chunk_size = max_chunk_size or settings.MAX_CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP

    clean_text = " ".join(text.split())
    if not clean_text:
        return []

    chunks = []
    start = 0
    text_length = len(clean_text)

    while start < text_length:
        end = min(start + max_chunk_size, text_length)
        chunks.append(clean_text[start:end])

        if end == text_length:
            break

        start = end - overlap

    return chunks
