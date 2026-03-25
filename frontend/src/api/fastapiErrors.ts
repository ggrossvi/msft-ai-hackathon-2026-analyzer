/**
 * FastAPI HTTPException responses use `{ "detail": string | object }`.
 * Use this when mapping non-OK responses to UI strings.
 */
export function fastApiErrorDetail(data: unknown): string {
  if (typeof data === "object" && data !== null && "detail" in data) {
    return String((data as { detail: unknown }).detail);
  }
  return JSON.stringify(data);
}
