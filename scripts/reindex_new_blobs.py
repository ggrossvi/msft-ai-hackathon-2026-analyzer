#!/usr/bin/env python3
"""
Reindex only new blobs into Azure AI Search (same index name).

What it does:
1) Ensures index schema exists (create_or_update).
2) Scans configured blob containers.
3) Skips blobs already indexed (by source_url).
4) Ingests only new blobs.

Run:
    python scripts/reindex_new_blobs.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _is_indexed(blob_url: str) -> bool:
    safe_url = blob_url.replace("'", "''")
    results = search_client.search(
        search_text="*",
        filter=f"source_url eq '{safe_url}'",
        select=["id"],
        top=1,
    )
    return any(True for _ in results)


def main() -> int:
    create_index()

    containers = [
        settings.AZURE_BLOB_DOCUMENTS_CONTAINER,
        settings.AZURE_BLOB_IMAGES_CONTAINER,
        settings.AZURE_BLOB_VIDEOS_CONTAINER,
        settings.AZURE_BLOB_RAW_CONTAINER,
    ]

    indexed_blobs = 0
    indexed_chunks = 0
    skipped = 0
    failed = 0

    for container in containers:
        container_client = blob_service_client.get_container_client(container)
        if not container_client.exists():
            continue

        for blob in container_client.list_blobs():
            blob_client = container_client.get_blob_client(blob.name)
            blob_url = blob_client.url

            if _is_indexed(blob_url):
                skipped += 1
                continue

            try:
                data = blob_client.download_blob().readall()
                out = ingest_file_into_search(
                    file_name=blob.name,
                    file_bytes=data,
                    blob_url=blob_url,
                )
                chunks = out.get("chunks_indexed", 0)
                indexed_blobs += 1
                indexed_chunks += chunks
                print(f"[INDEXED] {container}/{blob.name} -> {chunks} chunks")
            except Exception as exc:
                failed += 1
                print(f"[FAILED]  {container}/{blob.name} -> {exc}")

    print(
        f"\nDone. indexed_blobs={indexed_blobs}, indexed_chunks={indexed_chunks}, "
        f"skipped_existing={skipped}, failed={failed}"
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())