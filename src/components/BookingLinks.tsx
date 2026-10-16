import { ExternalLink } from "lucide-react";
import {
  airlineBookingUrl,
  googleFlightsUrl,
  type CalendarEntry,
} from "@/lib/flightDeals";

/* ------------------------------------------------------------------ */
/* Booking links for a fare (Kiran's decision, 2026-10-15): the       */
/* airline's own deep link is primary ONLY when the carrier has a     */
/* verified template in AIRLINE_LINK_TEMPLATES; "Compare on Google    */
/* Flights" is always present. No template → Google Flights only.     */
/* Never a bare homepage.                                             */
/*                                                                    */
/* Extracted from FlightDeals.tsx (Phase 2, 2026-10-15) so the        */
/* /travel fares hub and the destination-page fare module render      */
/* the exact same links — one component, no drift.                    */
/* ------------------------------------------------------------------ */

export default function BookingLinks({
  entry,
  origin,
  dest,
}: {
  entry: CalendarEntry;
  origin: string;
  dest: string;
}) {
  const gfUrl = googleFlightsUrl(origin, dest, entry.dep_date, entry.ret_date);
  const airlineUrl = airlineBookingUrl(
    entry.cheapest_airline,
    origin,
    dest,
    entry.dep_date,
    entry.ret_date,
  );
  return (
    <div className="flex flex-col gap-1.5 mt-1">
      {airlineUrl && (
        <a
          href={airlineUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 text-[13px] font-semibold text-primary hover:underline"
        >
          Book on {entry.cheapest_airline} <ExternalLink className="h-3.5 w-3.5" />
        </a>
      )}
      <a
        href={gfUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1.5 text-[13px] font-semibold text-primary hover:underline"
      >
        Compare on Google Flights <ExternalLink className="h-3.5 w-3.5" />
      </a>
    </div>
  );
}
