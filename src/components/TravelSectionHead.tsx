/* ------------------------------------------------------------------ */
/* Section header system — the redesign's one treatment for every     */
/* /travel-family section (Kiran approved mockup, 2026-10-15): gold   */
/* kicker, serif navy title, hairline with a gold tick. Shared by     */
/* TravelPage and TravelIndiaPage. TrendingDestinations and           */
/* FlightDeals render the same treatment inline (the rail needs its   */
/* counter pill in the title row; the fares header sits inside the    */
/* cream panel, so its hairline is navy-tinted).                      */
/* ------------------------------------------------------------------ */
export default function SectionHead({
  kicker,
  title,
  sub,
}: {
  kicker: string;
  title: string;
  sub?: string;
}) {
  return (
    <div className="mb-5">
      <div className="relative border-b border-rule pb-3">
        <p className="text-[11px] font-bold uppercase tracking-[2px] text-[#7a5c14] dark:text-[#D4A843] mb-1">
          {kicker}
        </p>
        <h2
          className="font-serif text-xl font-bold leading-none"
          style={{ color: "#0B1D3A" }}
        >
          {title}
        </h2>
        <span className="absolute left-0 -bottom-px h-[2px] w-10 bg-[#D4A843]" />
      </div>
      {sub && (
        <p className="text-sm text-foreground/55 leading-relaxed mt-3">{sub}</p>
      )}
    </div>
  );
}
