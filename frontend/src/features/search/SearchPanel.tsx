import { useState } from "react";
import { API_BASE_URL } from "../../config";
import type { SearchResponseBody, SearchResultItem } from "../../api/types";
import { fastApiErrorDetail } from "../../api/fastapiErrors";
import { truncateSnippet } from "../../lib/snippet";

type Props = {
  /** Mirrors /health.search_enabled — helper copy only; does not block search. */
  serverSearchReady: boolean;
};

/**
 * POST /search — query, top_k, chunk results (Phase 5).
 * Split from upload so search can ship or iterate independently.
 */
export function SearchPanel({ serverSearchReady }: Props) {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([]);
  const [lastQuery, setLastQuery] = useState("");

  async function runSearch() {
    const q = query.trim();
    if (!q) {
      setSearchError("Enter a search query.");
      setSearchResults([]);
      return;
    }

    setSearchLoading(true);
    setSearchError("");
    setSearchResults([]);
    setLastQuery(q);

    try {
      const res = await fetch(`${API_BASE_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, top_k: topK }),
      });
      const data = (await res.json().catch(() => ({}))) as
        | SearchResponseBody
        | { detail?: string };

      if (res.status === 503) {
        setSearchError(
          typeof data === "object" && data && "detail" in data
            ? fastApiErrorDetail(data)
            : "Search is not configured on the server.",
        );
        return;
      }
      if (!res.ok) {
        setSearchError(
          `Search failed (${res.status}): ${fastApiErrorDetail(data)}`,
        );
        return;
      }

      setSearchResults((data as SearchResponseBody).results ?? []);
    } catch (e) {
      setSearchError(
        e instanceof Error ? e.message : "Network error while searching.",
      );
    } finally {
      setSearchLoading(false);
    }
  }

  return (
    <section aria-labelledby="search-heading">
      <h2 id="search-heading">Search indexed documents</h2>
      {!serverSearchReady && (
        <p className="muted">
          Search requests will fail until the API has Azure AI Search and OpenAI
          embedding settings (see <code>/health</code>).
        </p>
      )}
      <div className="row">
        <div className="grow">
          <label htmlFor="search-query">Query</label>
          <input
            id="search-query"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. policy clause about retention"
            autoComplete="off"
          />
        </div>
        <div>
          <label htmlFor="top-k">Top results</label>
          <select
            id="top-k"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
          >
            {/* API allows top_k 1–50; preset list keeps the demo UI simple */}
            {[3, 5, 10, 15, 20, 30].map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
        </div>
        <div>
          <button
            type="button"
            className="btn"
            onClick={() => void runSearch()}
            disabled={searchLoading || !query.trim()}
          >
            {searchLoading ? "Searching…" : "Search"}
          </button>
        </div>
      </div>

      {searchError && (
        <p className="feedback error" role="alert">
          {searchError}
        </p>
      )}

      {!searchError && lastQuery && !searchLoading && (
        <p className="muted">
          Showing results for &quot;{lastQuery}&quot; ({searchResults.length}{" "}
          hit{searchResults.length === 1 ? "" : "s"}).
        </p>
      )}

      {searchResults.length > 0 && (
        <ul className="search-results">
          {searchResults.map((r) => (
            <li key={r.id}>
              <div className="meta">
                <strong>{r.file_name || "(unnamed)"}</strong>
                {r.score != null && <> · score {Number(r.score).toFixed(4)}</>}
                {r.chunk_number != null && <> · chunk #{r.chunk_number}</>}
              </div>
              <div className="snippet">{truncateSnippet(r.content)}</div>
              {r.source_url ? (
                <div style={{ marginTop: "0.5rem" }}>
                  <a href={r.source_url} target="_blank" rel="noreferrer">
                    {r.source_url}
                  </a>
                </div>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
