/**
 * Trust Lens shell: composes feature slices (health, upload, search) so each
 * can evolve independently — matches incremental phases in AI_Search_Feature.md.
 */
import "./App.css";
import {
  AI_SEARCH_UI_ENABLED,
  API_BASE_URL,
} from "./config";
import { useApiHealth } from "./hooks/useApiHealth";
import { HealthBadge } from "./features/health/HealthBadge";
import { UploadSection } from "./features/upload/UploadSection";
import { SearchPanel } from "./features/search/SearchPanel";

export default function App() {
  const { health, healthError, refresh } = useApiHealth();
  const serverSearchReady = health?.search_enabled === true;

  return (
    <div className="trust-lens">
      <header>
        <h1>Trust Lens AI</h1>
        <p>
          A governed RAG system that delivers source-backed, low-hallucination
          answers for compliance-critical industries.
        </p>
      </header>

      <HealthBadge
        health={health}
        healthError={healthError}
        apiBase={API_BASE_URL}
      />

      <UploadSection onUploadComplete={refresh} />

      {AI_SEARCH_UI_ENABLED ? (
        <SearchPanel serverSearchReady={serverSearchReady} />
      ) : (
        <p className="feature-off-note">
          AI Search UI is hidden (set{" "}
          <code>VITE_ENABLE_AI_SEARCH_UI</code> to enable).
        </p>
      )}
    </div>
  );
}
