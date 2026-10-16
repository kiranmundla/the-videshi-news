import { useEffect, useRef, useState } from "react";

/* ------------------------------------------------------------------ */
/* useRailCounter — the ONE scroll-counter implementation for the     */
/* site's card rails (TrendingDestinations on /travel, MetroFareRail  */
/* on the India page + Your Hub). Returns the rail's scroll ref and   */
/* the index of the card nearest the rail's left edge, which drives   */
/* the "n / total" counter pill.                                      */
/*                                                                    */
/* FLUIDITY (Kiran, 2026-10-15: the two rails using the old copied    */
/* pattern felt "not as fluid" as the Hub trending strip / trailers  */
/* rail). The old pattern — duplicated verbatim in both components —  */
/* did two things the fluid rails never do:                           */
/*   1. `scroll-snap-type: x mandatory` on the container (+ snap-     */
/*      align on every card): the browser may only REST on card       */
/*      boundaries, so flings are truncated and the resting position  */
/*      is pulled onto a snap point (measured in the harness: a       */
/*      touch fling peaking at 245px was dragged back to 212px; a     */
/*      scripted momentum scroll was starved to 3–4 scroll events    */
/*      vs ~67 with snap off). The rails now carry NO scroll-snap —   */
/*      exactly like the baselines.                                   */
/*   2. A scroll listener that, on EVERY scroll event, read           */
/*      `children[0].offsetWidth` (a forced-layout read — measured    */
/*      at exactly 1 read per scroll event) and called setState,      */
/*      re-rendering the whole rail subtree mid-fling. The fluid      */
/*      rails run zero JS during a scroll.                            */
/* This hook keeps the counter but removes the cost from the scroll   */
/* path: the step is measured ONCE (on mount / item-count change /    */
/* resize) instead of per event; scroll events only schedule a        */
/* single requestAnimationFrame; and state updates fire ONLY when     */
/* the rounded index actually changes. The counter math itself is     */
/* unchanged (round(scrollLeft / step), clamped), so the pill reads   */
/* exactly as before — snap was never part of it.                     */
/*                                                                    */
/* PhotoScrollStrip still carries the old copied listener idiom       */
/* (plus arrow/nudge behaviour the rails don't have) — it was not     */
/* part of the 2026-10-15 complaint; migrating it here is a follow-   */
/* up if its strips ever feel grabby.                                 */
/* ------------------------------------------------------------------ */

const GAP = 12; // matches the rails' gap-3

export function useRailCounter(itemCount: number): {
  scrollRef: React.RefObject<HTMLDivElement | null>;
  currentIndex: number;
} {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const indexRef = useRef(0);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el || itemCount <= 0) return;

    /* Card step (card width + gap), measured once per mount /
       resize / item-count change — never on the scroll path.
       NB: children[0] is NOT the first card — both rails render a
       <style> element (scrollbar-hiding) as the container's first
       child, and it has offsetWidth 0. The previous copied pattern
       measured exactly that child, so its "step" was 0 + GAP = 12px
       and the counter saturated to the last card after ~100px of
       scrolling. Measure the first child with a real width instead:
       the counter now tracks card by card, as intended. */
    let step = 0;
    const measure = () => {
      step = 0;
      for (const child of Array.from(el.children)) {
        const w = (child as HTMLElement).offsetWidth;
        if (w > 0) {
          step = w + GAP;
          break;
        }
      }
    };
    measure();

    let raf = 0;
    const update = () => {
      raf = 0;
      if (step <= 0) measure(); // first child wasn't laid out yet
      if (step <= 0) return;
      /* Progress-pill convention: at max scroll the reader HAS
         reached the last card, so read the total — round() alone
         can't get there, because the rail physically stops a
         fraction of a step short of the last card's offset. */
      const max = el.scrollWidth - el.clientWidth;
      const idx =
        max > 0 && el.scrollLeft >= max - 1
          ? itemCount - 1
          : Math.min(
              itemCount - 1,
              Math.max(0, Math.round(el.scrollLeft / step)),
            );
      if (idx !== indexRef.current) {
        indexRef.current = idx;
        setCurrentIndex(idx);
      }
    };
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update);
    };
    const onResize = () => {
      measure();
      onScroll();
    };

    onScroll(); // settle the initial index
    el.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onResize);
    return () => {
      el.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onResize);
      if (raf) cancelAnimationFrame(raf);
    };
  }, [itemCount]);

  return { scrollRef, currentIndex };
}
