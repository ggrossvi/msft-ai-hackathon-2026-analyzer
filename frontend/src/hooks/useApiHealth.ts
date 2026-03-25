import { useCallback, useEffect, useState } from "react";
import { API_BASE_URL } from "../config";
import type { HealthResponse } from "../api/types";

/**
 * Polls GET /health on mount; exposes `refresh` so upload success can re-check mode
 * (e.g. after enabling Search env server-side without reloading the page).
 */
export function useApiHealth() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState("");

  const refresh = useCallback(async () => {
    setHealthError("");
    try {
      const res = await fetch(`${API_BASE_URL}/health`);
      const data = (await res.json()) as HealthResponse;
      if (!res.ok) {
        setHealthError(`Health check failed (${res.status}).`);
        return;
      }
      setHealth(data);
    } catch (e) {
      setHealthError(
        e instanceof Error ? e.message : "Could not reach the API.",
      );
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { health, healthError, refresh };
}
