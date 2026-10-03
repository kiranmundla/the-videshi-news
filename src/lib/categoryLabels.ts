// Canonical category slug → display label mapping for The Videshi.
// Single source of truth — import this instead of defining local copies.
// (2026-10-02: raw slugs like "lifestyle-health" were leaking into the UI
// because five components each kept their own incomplete copy of this map.)

export const CATEGORY_LABELS: Record<string, string> = {
  news: "India News",
  "nri-world": "World News",
  "markets-finance": "Markets & Finance",
  immigration: "Immigration",
  technology: "Technology",
  entertainment: "Entertainment",
  sports: "Sports",
  food: "Food",
  travel: "Travel",
  "lifestyle-health": "Lifestyle & Health",
};

/** Display label for a category slug. Never returns a raw slug — unknown
 *  slugs fall back to Title Case ("some-thing" → "Some Thing"). */
export function categoryLabel(slug?: string | null): string {
  if (!slug) return "";
  const hit = CATEGORY_LABELS[slug];
  if (hit) return hit;
  return slug
    .split("-")
    .map((w) => (w ? w.charAt(0).toUpperCase() + w.slice(1) : w))
    .join(" ");
}
