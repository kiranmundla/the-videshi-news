import { Link } from "react-router-dom";
import { useHubLocation } from "@/hooks/useHubLocation";

/**
 * "Your Hub" entry on the homepage — a distinct personalized banner
 * below the hub icon strip, not another tile.
 */
export default function YourHubBanner() {
  const { location, isSet } = useHubLocation();

  return (
    <div className="container">
      <Link
        to="/your-hub"
        className="block rounded-xl overflow-hidden mt-1 mb-2 transition-transform active:scale-[0.99]"
        style={{
          background: "linear-gradient(120deg, #0B1D3A 0%, #16294a 70%, #1d3461 100%)",
        }}
        aria-label="Open Your Hub — your personalized diaspora dashboard"
      >
        <div className="flex items-center gap-3 px-4 py-3.5 md:px-5 md:py-4">
          {/* Person icon in gold circle */}
          <div
            className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center"
            style={{ backgroundColor: "#D4A843" }}
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="#0B1D3A"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="w-5 h-5"
            >
              <circle cx="12" cy="8" r="3.5" />
              <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-[15px] font-bold text-white">Your Hub</span>
              {isSet && location ? (
                <span className="flex items-center gap-1 text-[11px] font-semibold text-white/80 truncate">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    className="w-3 h-3 flex-shrink-0"
                  >
                    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />
                    <circle cx="12" cy="9" r="2.5" />
                  </svg>
                  <span className="truncate">{location.label}</span>
                </span>
              ) : (
                <span className="text-[11px] font-semibold text-[#D4A843]">
                  Set your location
                </span>
              )}
            </div>
            <p className="text-[12px] text-white/70 leading-snug mt-0.5">
              Your weekend, deadlines &amp; festivals — personalized for you.
            </p>
          </div>
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="#D4A843"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="w-5 h-5 flex-shrink-0"
          >
            <path d="M9 6l6 6-6 6" />
          </svg>
        </div>
      </Link>
    </div>
  );
}
