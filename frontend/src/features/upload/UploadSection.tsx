import { useState } from "react";
import { API_BASE_URL } from "../../config";
import type { UploadResponse } from "../../api/types";
import { fastApiErrorDetail } from "../../api/fastapiErrors";

type Props = {
  /** Called after a successful upload so parent can refresh GET /health. */
  onUploadComplete?: () => void | Promise<void>;
};

/**
 * POST /upload — file picker, blob + indexing feedback (Phase 3/5 contract).
 * Isolated so upload UX can evolve without touching search UI.
 */
export function UploadSection({ onUploadComplete }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [uploadDetails, setUploadDetails] = useState<UploadResponse | null>(
    null,
  );
  const [loading, setLoading] = useState(false);

  async function upload() {
    if (!file) {
      setUploadStatus("Choose a file first.");
      setUploadDetails(null);
      return;
    }
    setLoading(true);
    setUploadStatus("");
    setUploadDetails(null);

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: form,
      });
      const data = (await res.json().catch(() => ({}))) as
        | UploadResponse
        | Record<string, unknown>;

      if (!res.ok) {
        setUploadStatus(`Error ${res.status}: ${fastApiErrorDetail(data)}`);
        return;
      }

      setUploadStatus("Upload completed.");
      setUploadDetails(data as UploadResponse);
      await onUploadComplete?.();
    } catch (e) {
      setUploadStatus(
        `Network error: ${e instanceof Error ? e.message : String(e)}`,
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section aria-labelledby="upload-heading">
      <h2 id="upload-heading">Upload file</h2>
      <input
        type="file"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <div style={{ marginTop: 12 }}>
        <button type="button" className="btn" onClick={upload} disabled={loading}>
          {loading ? "Uploading…" : "Upload"}
        </button>
      </div>
      {uploadStatus && <p className="muted">{uploadStatus}</p>}

      {uploadDetails && (
        <div className="feedback" role="region" aria-label="Upload result">
          <div>
            <span className="ok">Blob upload:</span> succeeded
            {uploadDetails.blob?.blob_url && (
              <>
                {" "}
                (
                <a
                  href={String(uploadDetails.blob.blob_url)}
                  target="_blank"
                  rel="noreferrer"
                >
                  open blob URL
                </a>
                )
              </>
            )}
          </div>

          {!uploadDetails.search_enabled && (
            <div className="muted" style={{ marginTop: "0.5rem" }}>
              Server reports search is not configured — file was not indexed.
            </div>
          )}

          {uploadDetails.search_enabled && uploadDetails.indexing && (
            <ul>
              <li>
                <strong>Indexing:</strong>{" "}
                {uploadDetails.indexing.chunks_indexed > 0 ? (
                  <span className="ok">
                    {uploadDetails.indexing.chunks_indexed} chunk(s) indexed
                  </span>
                ) : (
                  <span className="warn">0 chunks — not searchable</span>
                )}
              </li>
              <li>
                <strong>Message:</strong> {uploadDetails.indexing.message}
              </li>
              <li>
                <strong>Searchable:</strong>{" "}
                {uploadDetails.indexing.chunks_indexed > 0 ? (
                  <span className="ok">
                    Yes — try a query in the search panel below.
                  </span>
                ) : (
                  <span className="warn">
                    Not yet — extraction produced no chunks (try another format
                    or content).
                  </span>
                )}
              </li>
            </ul>
          )}
        </div>
      )}
    </section>
  );
}
