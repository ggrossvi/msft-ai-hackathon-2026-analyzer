"""
Smoke-test Azure OpenAI embeddings + Azure AI Search using env from app/config.

Run from repository root (with venv active):

    python scripts/verify_ai_services.py

Exits non-zero if required variables are missing or a service call fails.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Repo root on sys.path so `import app.*` matches uvicorn layout
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from app.config import settings

    required = [
        ("AZURE_SEARCH_ENDPOINT", settings.AZURE_SEARCH_ENDPOINT),
        ("AZURE_SEARCH_KEY", settings.AZURE_SEARCH_KEY),
        ("AZURE_SEARCH_INDEX_NAME", settings.AZURE_SEARCH_INDEX_NAME),
        ("AZURE_OPENAI_ENDPOINT", settings.AZURE_OPENAI_ENDPOINT),
        ("AZURE_OPENAI_KEY", settings.AZURE_OPENAI_KEY),
        ("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT),
    ]
    missing = [name for name, val in required if not val]
    if missing:
        print("Missing or empty:", ", ".join(missing))
        print("Add them to repo root `.env`. See `.env.example`.")
        return 1

    print("Calling Azure OpenAI embeddings...")
    from app.embeddings import generate_embedding

    vec = generate_embedding("connection test")
    print(f"  Embedding length: {len(vec)} (config AZURE_OPENAI_EMBEDDING_DIMENSIONS={settings.AZURE_OPENAI_EMBEDDING_DIMENSIONS})")
    if len(vec) != settings.AZURE_OPENAI_EMBEDDING_DIMENSIONS:
        print("  WARNING: length does not match AZURE_OPENAI_EMBEDDING_DIMENSIONS — fix env or Search index vector size.")

    print("Calling Azure AI Search (hybrid, may return 0 hits if index is empty)...")
    from app.search_index import hybrid_search

    results = hybrid_search("test", top_k=3)
    print(f"  Search returned {len(results)} hit(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
