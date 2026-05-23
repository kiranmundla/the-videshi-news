import { useState, useCallback } from "react";
import { lookupZip, type ZipInfo } from "@/lib/geo";

export type LocationResult = {
  lat: number;
  lng: number;
  city: string;
  state: string;
  label: string; // e.g. "90210 — Beverly Hills, CA" or "📍 Near You"
  source: "zip" | "geolocation";
};

type Props = {
  onLocation: (result: LocationResult | null) => void;
  /** Currently active? Controls highlight state */
  active: boolean;
  /** Compact mode for tight filter bars */
  compact?: boolean;
  className?: string;
};

export default function ZipCodeSearch({ onLocation, active, compact, className }: Props) {
  const [zip, setZip] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [geoLoading, setGeoLoading] = useState(false);

  const handleZipSubmit = useCallback(async () => {
    const cleaned = zip.trim();
    if (!/^\d{5}$/.test(cleaned)) {
      setError("Enter a 5-digit zip code");
      return;
    }
    setError(null);
    const info: ZipInfo | null = await lookupZip(cleaned);
    if (!info) {
      setError("Zip code not found");
      return;
    }
    onLocation({
      lat: info.lat,
      lng: info.lng,
      city: info.city,
      state: info.state,
      label: `${cleaned} — ${info.city}, ${info.state}`,
      source: "zip",
    });
  }, [zip, onLocation]);

  const handleNearMe = useCallback(() => {
    if (active) {
      // Toggle off
      onLocation(null);
      return;
    }
    if (!navigator.geolocation) {
      setError("Geolocation not supported");
      return;
    }
    setGeoLoading(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGeoLoading(false);
        setZip("");
        onLocation({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          city: "",
          state: "",
          label: "📍 Near You",
          source: "geolocation",
        });
      },
      () => {
        setGeoLoading(false);
        setError("Location access denied");
      },
      { enableHighAccuracy: false, timeout: 8000 }
    );
  }, [active, onLocation]);

  const handleClear = useCallback(() => {
    setZip("");
    setError(null);
    onLocation(null);
  }, [onLocation]);

  const py = compact ? "py-1.5" : "py-2.5";

  return (
    <div className={`flex flex-col gap-1 ${className || ""}`}>
      <div className="flex items-center gap-2">
        {/* Near Me button */}
        <button
          onClick={handleNearMe}
          disabled={geoLoading}
          className={`shrink-0 flex items-center gap-1.5 px-3.5 ${py} rounded-lg border text-sm font-medium transition-colors ${
            active
              ? "bg-primary/15 border-primary/40 text-primary"
              : "border-border text-foreground/70 hover:border-primary hover:text-primary"
          } ${geoLoading ? "opacity-60 cursor-wait" : "cursor-pointer"}`}
        >
          {geoLoading ? (
            <span className="inline-block w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
          ) : (
            <span>📍</span>
          )}
          <span className="hidden sm:inline">{active ? "Near You" : "Near Me"}</span>
        </button>

        {/* Zip code input */}
        <div className="flex items-center gap-0">
          <input
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={5}
            placeholder="Zip code"
            value={zip}
            onChange={(e) => {
              const v = e.target.value.replace(/\D/g, "").slice(0, 5);
              setZip(v);
              setError(null);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleZipSubmit();
            }}
            className={`w-24 sm:w-28 px-3 ${py} rounded-l-lg border border-r-0 text-sm bg-card border-border text-foreground placeholder:text-foreground/40 focus:outline-none focus:ring-2 focus:ring-primary/40 focus:z-10`}
          />
          <button
            onClick={handleZipSubmit}
            className={`px-3 ${py} rounded-r-lg border border-border bg-muted/40 text-sm font-medium text-foreground/70 hover:bg-muted/60 hover:text-foreground transition-colors`}
          >
            Go
          </button>
        </div>

        {/* Clear button when active */}
        {active && (
          <button
            onClick={handleClear}
            className="shrink-0 p-1.5 rounded text-foreground/40 hover:text-foreground transition-colors"
            title="Clear location filter"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Error / active label */}
      {error && (
        <span className="text-xs text-red-400 pl-1">{error}</span>
      )}
    </div>
  );
}
