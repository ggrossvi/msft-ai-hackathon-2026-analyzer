import { SNIPPET_MAX_LEN } from "../config";

/**
 * Shortens long chunk text for list previews in search results.
 */
export function truncateSnippet(
  value: unknown,
  maxLen: number = SNIPPET_MAX_LEN,
): string {
  const text = typeof value === "string" ? value.trim() : "";
  if (!text) return "";
  if (text.length <= maxLen) return text;
  return `${text.slice(0, maxLen)}...`;
}
