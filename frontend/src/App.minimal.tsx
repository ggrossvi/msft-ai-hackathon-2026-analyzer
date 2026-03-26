import { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8001";

type SearchResult = {
  id: string;
  file_name: string;
  source_url: string;
  content: string;
  chunk_number: number;
  score?: number | null;
};

type ChatCitation = {
  file_name?: string;
  source_url?: string;
  chunk_number?: number;
  snippet?: string;
};

type ChatResponse = {
  answer: string;
  citations?: ChatCitation[];
};

export default function App() {
  // Upload
  const [file, setFile] = useState<File | null>(null);
  const [uploadMsg, setUploadMsg] = useState("");

  // Search
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searchMsg, setSearchMsg] = useState("");

  // Chat
  const [chatInput, setChatInput] = useState("");
  const [chatAnswer, setChatAnswer] = useState("");
  const [chatCitations, setChatCitations] = useState<ChatCitation[]>([]);
  const [chatMsg, setChatMsg] = useState("");

  const [loadingUpload, setLoadingUpload] = useState(false);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [loadingChat, setLoadingChat] = useState(false);

  async function uploadFile() {
    if (!file) return setUploadMsg("Pick a file first.");
    setLoadingUpload(true);
    setUploadMsg("");
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE_URL}/upload`, { method: "POST", body: form });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) return setUploadMsg(`Upload failed (${res.status}): ${String(data?.detail ?? "Unknown error")}`);
      setUploadMsg("Upload complete. If search is configured, it should be indexed.");
    } catch (e) {
      setUploadMsg(`Network error: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setLoadingUpload(false);
    }
  }

  async function runSearch() {
    const q = query.trim();
    if (!q) return setSearchMsg("Enter a query.");
    setLoadingSearch(true);
    setSearchMsg("");
    setResults([]);
    try {
      const res = await fetch(`${API_BASE_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, top_k: 5 }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) return setSearchMsg(`Search failed (${res.status}): ${String(data?.detail ?? "Unknown error")}`);
      setResults(data.results ?? []);
      setSearchMsg(`Found ${(data.results ?? []).length} result(s).`);
    } catch (e) {
      setSearchMsg(`Network error: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setLoadingSearch(false);
    }
  }

  async function runChat() {
    const message = chatInput.trim();
    if (!message) return setChatMsg("Enter a chat question.");
    setLoadingChat(true);
    setChatMsg("");
    setChatAnswer("");
    setChatCitations([]);

    try {
      const res = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, top_k: 5 }),
      });

      // If /chat doesn't exist yet, guide clearly.
      if (res.status === 404 || res.status === 405) {
        setChatMsg("`/chat` endpoint is not implemented yet. Add backend /chat to enable real RAG chat.");
        return;
      }

      const data = (await res.json().catch(() => ({}))) as ChatResponse & { detail?: string };
      if (!res.ok) return setChatMsg(`Chat failed (${res.status}): ${String(data?.detail ?? "Unknown error")}`);

      setChatAnswer(data.answer ?? "");
      setChatCitations(data.citations ?? []);
    } catch (e) {
      setChatMsg(`Network error: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setLoadingChat(false);
    }
  }

  return (
    <main style={{ maxWidth: 900, margin: "2rem auto", padding: "0 1rem", fontFamily: "sans-serif" }}>
      <h1>Trust Lens - Minimal UI</h1>
      <p>Basic functional frontend for Upload, Search, and Chat.</p>

      <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, marginBottom: 16 }}>
        <h2>1) Upload</h2>
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <button onClick={() => void uploadFile()} disabled={loadingUpload} style={{ marginLeft: 8 }}>
          {loadingUpload ? "Uploading..." : "Upload"}
        </button>
        {uploadMsg && <p>{uploadMsg}</p>}
      </section>

      <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, marginBottom: 16 }}>
        <h2>2) Search</h2>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask for document content"
          style={{ width: "70%", marginRight: 8 }}
        />
        <button onClick={() => void runSearch()} disabled={loadingSearch}>
          {loadingSearch ? "Searching..." : "Search"}
        </button>
        {searchMsg && <p>{searchMsg}</p>}
        <ul>
          {results.map((r) => (
            <li key={r.id} style={{ marginBottom: 10 }}>
              <strong>{r.file_name}</strong> {r.score != null ? `(${r.score.toFixed(3)})` : ""}
              <div>{r.content?.slice(0, 220)}...</div>
              {r.source_url && (
                <a href={r.source_url} target="_blank" rel="noreferrer">
                  Source
                </a>
              )}
            </li>
          ))}
        </ul>
      </section>

      <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16 }}>
        <h2>3) Chat (RAG answer + citations)</h2>
        <textarea
          rows={3}
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          placeholder="Ask a question about your uploaded docs"
          style={{ width: "100%", marginBottom: 8 }}
        />
        <button onClick={() => void runChat()} disabled={loadingChat}>
          {loadingChat ? "Thinking..." : "Send"}
        </button>

        {chatMsg && <p>{chatMsg}</p>}
        {chatAnswer && (
          <>
            <h3>Answer</h3>
            <p>{chatAnswer}</p>
          </>
        )}

        {chatCitations.length > 0 && (
          <>
            <h3>Citations</h3>
            <ul>
              {chatCitations.map((c, i) => (
                <li key={i}>
                  {c.file_name ?? "unknown file"}
                  {c.chunk_number != null ? ` (chunk ${c.chunk_number})` : ""}
                  {c.source_url ? (
                    <>
                      {" "}
                      -{" "}
                      <a href={c.source_url} target="_blank" rel="noreferrer">
                        link
                      </a>
                    </>
                  ) : null}
                </li>
              ))}
            </ul>
          </>
        )}
      </section>
    </main>
  );
}