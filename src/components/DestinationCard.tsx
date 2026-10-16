import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import {
  REGIONS,
  visaBadgeColor,
  visaBadgeLabel,
  visaNoteAddsInfo,
} from "@/lib/travel";
import type { Destination, VisaHolderStatus } from "@/lib/travel";

/* ------------------------------------------------------------------ */
/* Destination Card — one guide card in the destinations index.       */
/* Shared by TravelPage (all groups) and TravelIndiaPage (the India   */
/* group) so the two can never drift apart.                           */
/* ------------------------------------------------------------------ */
export default function DestinationCard({ dest, holderStatus }: { dest: Destination; holderStatus: VisaHolderStatus }) {
  const region = REGIONS.find((r) => r.key === dest.region);
  const visaInfo = dest.visa[holderStatus];
  return (
    <Link
      to={dest.hasGuide ? `/travel/${dest.key}` : "#"}
      className={`block group ${!dest.hasGuide ? "cursor-default" : ""}`}
      onClick={dest.hasGuide ? undefined : (e) => e.preventDefault()}
    >
      <div className="bg-card border border-border rounded-xl p-4 h-full hover:border-primary/40 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5 flex flex-col gap-2">
        {/* Top row: name + region emoji */}
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <h3 className="font-semibold text-sm group-hover:text-primary transition-colors leading-tight">
              {region?.emoji} {dest.label}
            </h3>
            <p className="text-[11px] text-foreground/50 leading-tight mt-0.5">{dest.description}</p>
          </div>
          {dest.hasGuide && (
            <ChevronRight className="h-4 w-4 text-foreground/20 group-hover:text-primary transition-colors flex-shrink-0 mt-0.5" />
          )}
        </div>

        {/* Visa badge + note — the note prints ONLY when it adds a
            condition/duration/mechanism beyond the badge (audit
            item 10); survivors get the legible 10px/50% treatment. */}
        <div className="flex flex-col gap-0.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${visaBadgeColor(visaInfo.status)}`}>
              {visaBadgeLabel(visaInfo.status)}
            </span>
            <span className="text-[10px] text-foreground/40">📅 {dest.bestMonths}</span>
          </div>
          {visaNoteAddsInfo(visaInfo) && (
            <span className="text-[10px] text-foreground/50 leading-tight pl-0.5">{visaInfo.note}</span>
          )}
        </div>

        <div className="flex items-center gap-3 text-[10px] text-foreground/40 mt-auto">
          <span>💰 {dest.budget}</span>
          {!dest.hasGuide && (
            <span className="text-[10px] text-foreground/30 italic">Guide coming soon</span>
          )}
        </div>
      </div>
    </Link>
  );
}
