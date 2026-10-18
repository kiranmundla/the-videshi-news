import { useHubLocationSuggestion } from "@/hooks/useHubLocation";

/**
 * "Looks like you're near <City, ST> — [Use this] [Keep <stored>]"
 *
 * The IP-tripwire suggestion (useHubLocation.ts): when the stored
 * location looks materially wrong against the visitor's IP-geo city,
 * ask ONCE — never on every landing, and never for a manual pick.
 * "Use this" writes the suggested place through the canonical setter
 * (all surfaces live-sync); "Keep" dismisses AND persists the city,
 * so it never nags twice. Renders nothing when there is no
 * suggestion, which is the overwhelmingly common case.
 */
export default function LocationSuggestionChip({
  className = "",
}: {
  className?: string;
}) {
  const { suggestion, accept, dismiss } = useHubLocationSuggestion();
  if (!suggestion) return null;
  return (
    <div
      role="status"
      className={`flex flex-wrap items-center gap-x-3 gap-y-2 rounded-lg border border-[#D4A843]/60 bg-[#D4A843]/10 px-4 py-3 ${className}`}
    >
      <span className="text-sm text-foreground">
        📍 Looks like you&rsquo;re near{" "}
        <strong className="font-semibold">{suggestion.location.label}</strong>
      </span>
      <span className="flex items-center gap-2">
        <button
          type="button"
          onClick={accept}
          className="px-3.5 py-1.5 rounded-full text-[13px] font-bold text-white transition-opacity hover:opacity-90"
          style={{ backgroundColor: "#0B1D3A" }}
        >
          Use this
        </button>
        <button
          type="button"
          onClick={dismiss}
          className="px-3.5 py-1.5 rounded-full text-[13px] font-medium border border-border bg-background/60 text-muted-foreground hover:text-foreground transition-colors"
        >
          Keep {suggestion.storedLabel}
        </button>
      </span>
    </div>
  );
}
