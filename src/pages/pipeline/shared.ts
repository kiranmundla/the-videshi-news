export const VERTICALS = [
  "politics",
  "economy",
  "tech",
  "immigration",
  "diaspora",
  "science",
  "culture",
] as const;

export const VERTICAL_COLORS: Record<string, string> = {
  politics: "bg-red-100 text-red-900 border-red-200",
  economy: "bg-emerald-100 text-emerald-900 border-emerald-200",
  tech: "bg-blue-100 text-blue-900 border-blue-200",
  immigration: "bg-purple-100 text-purple-900 border-purple-200",
  diaspora: "bg-amber-100 text-amber-900 border-amber-200",
  science: "bg-teal-100 text-teal-900 border-teal-200",
  culture: "bg-pink-100 text-pink-900 border-pink-200",
};

export const URGENCY_COLORS: Record<string, string> = {
  breaking: "bg-red-600 text-white",
  daily: "bg-yellow-400 text-black",
  evergreen: "bg-gray-300 text-gray-900",
};

export const STATUS_COLORS: Record<string, string> = {
  pending: "bg-gray-200 text-gray-800",
  hunting: "bg-blue-200 text-blue-900",
  synthesizing: "bg-purple-200 text-purple-900",
  review: "bg-yellow-200 text-yellow-900",
  published: "bg-emerald-200 text-emerald-900",
  rejected: "bg-red-200 text-red-900",
  draft: "bg-gray-200 text-gray-800",
  approved: "bg-emerald-200 text-emerald-900",
};

export function relTime(iso?: string | null): string {
  if (!iso) return "—";
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}

export function scoreColor(s?: number | null): string {
  if (s == null) return "text-muted-foreground";
  if (s >= 80) return "text-emerald-600 font-bold";
  if (s >= 60) return "text-yellow-600 font-bold";
  return "text-red-600 font-bold";
}
