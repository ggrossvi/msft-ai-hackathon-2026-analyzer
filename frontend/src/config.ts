/**
 * Central place for env-based toggles and API defaults.
 * Add new feature flags here as phases land (keeps rollout incremental).
 */
export const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8001";

/** When `VITE_ENABLE_AI_SEARCH_UI` is `"false"`, hide the search panel (opt-out). */
export const AI_SEARCH_UI_ENABLED =
  import.meta.env.VITE_ENABLE_AI_SEARCH_UI !== "false";

/** Default max length for chunk text shown in the search results list. */
export const SNIPPET_MAX_LEN = 280;
