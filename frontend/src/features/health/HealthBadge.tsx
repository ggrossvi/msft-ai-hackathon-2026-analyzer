import type { HealthResponse } from "../../api/types";

type Props = {
  health: HealthResponse | null;
  healthError: string;
  apiBase: string;
};

/** GET /health — blob-only vs search-enabled badge for the shell. */
export function HealthBadge({ health, healthError, apiBase }: Props) {
  if (healthError) {
    return (
      <p className="mode-badge blob-only" role="status">
        <span className="dot" aria-hidden />
        API: {healthError} ({apiBase})
      </p>
    );
  }
  if (health) {
    return (
      <p
        className={`mode-badge ${health.search_enabled ? "" : "blob-only"}`}
        role="status"
      >
        <span className="dot" aria-hidden />
        API mode: <strong>{health.mode}</strong>
        {health.search_enabled
          ? " — upload can index into AI Search."
          : " — uploads go to Blob only (search env not set)."}
      </p>
    );
  }
  return (
    <p className="mode-badge" role="status">
      <span className="dot" aria-hidden />
      Checking API…
    </p>
  );
}
