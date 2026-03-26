/**
 * Shapes returned by FastAPI (`app/main.py`, `app/models.py`).
 * Keep in sync when backend DTOs change.
 */

export interface HealthResponse {
  status: string;
  search_enabled: boolean;
  mode: string;
}

export interface UploadBlobInfo {
  blob_url?: string;
  [key: string]: unknown;
}

export interface IndexingInfo {
  file_name: string;
  chunks_indexed: number;
  message: string;
}

export interface UploadResponse {
  message: string;
  blob: UploadBlobInfo | null;
  indexing: IndexingInfo | null;
  search_enabled: boolean;
}

export interface SearchResultItem {
  id: string;
  file_name: string;
  source_url: string;
  content: string;
  chunk_number: number;
  score?: number | null;
}

export interface SearchResponseBody {
  query: string;
  results: SearchResultItem[];
}
