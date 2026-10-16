import type { VisaHolderStatus } from "@/lib/travel";

/* ------------------------------------------------------------------ */
/* "I'm traveling as" passport toggle — the control bar that drives   */
/* the visa badges on every destination card under it. Shared by      */
/* TravelPage (the All Destinations index) and TravelIndiaPage (the   */
/* India destinations section) — one control, one behaviour.          */
/* ------------------------------------------------------------------ */
const VISA_TABS: VisaHolderStatus[] = ["indian-passport", "us-citizen", "green-card"];
const VISA_TAB_SHORT: Record<VisaHolderStatus, string> = {
  "indian-passport": "US Visa Holder",
  "us-citizen": "US Citizen",
  "green-card": "Green Card",
};

export default function TravelerToggle({
  holderStatus,
  onChange,
}: {
  holderStatus: VisaHolderStatus;
  onChange: (status: VisaHolderStatus) => void;
}) {
  return (
    <div className="bg-foreground/[0.02] border border-border rounded-2xl px-4 py-3 mb-7">
      <div className="flex items-center gap-2 mb-2.5">
        <span className="text-lg">🧳</span>
        <p className="text-sm font-semibold">I'm traveling as</p>
      </div>
      <div className="flex gap-2 overflow-x-auto" style={{ WebkitOverflowScrolling: "touch" }}>
        {VISA_TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => onChange(tab)}
            className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-semibold border transition-colors ${
              holderStatus === tab
                ? "bg-primary text-primary-foreground border-primary"
                : "border-rule text-foreground/80 hover:text-primary hover:border-primary bg-card"
            }`}
          >
            {VISA_TAB_SHORT[tab]}
          </button>
        ))}
      </div>
    </div>
  );
}
