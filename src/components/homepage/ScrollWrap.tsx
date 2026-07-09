import { useRef, useState, useEffect, useCallback, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  className?: string;
  scrollAmount?: number; // px to scroll per click, default 320
  arrowVariant?: "light" | "dark"; // dark = white arrows (for navy bg)
}

export default function ScrollWrap({
  children,
  className = "",
  scrollAmount = 320,
  arrowVariant = "light",
}: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [canLeft, setCanLeft] = useState(false);
  const [canRight, setCanRight] = useState(false);

  const check = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    setCanLeft(el.scrollLeft > 2);
    setCanRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 2);
  }, []);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    check();
    el.addEventListener("scroll", check, { passive: true });
    const ro = new ResizeObserver(check);
    ro.observe(el);
    return () => {
      el.removeEventListener("scroll", check);
      ro.disconnect();
    };
  }, [check]);

  const scroll = (dir: -1 | 1) => {
    ref.current?.scrollBy({ left: dir * scrollAmount, behavior: "smooth" });
  };

  const isDark = arrowVariant === "dark";

  return (
    <div className="v2-scroll-wrap">
      {canLeft && (
        <button
          onClick={() => scroll(-1)}
          className={`v2-scroll-arrow v2-scroll-arrow-left ${isDark ? "v2-scroll-arrow-dark" : ""}`}
          aria-label="Scroll left"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>
      )}
      <div ref={ref} className={`v2-scroll-strip ${className}`}>
        {children}
      </div>
      {canRight && (
        <button
          onClick={() => scroll(1)}
          className={`v2-scroll-arrow v2-scroll-arrow-right ${isDark ? "v2-scroll-arrow-dark" : ""}`}
          aria-label="Scroll right"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="9 6 15 12 9 18" />
          </svg>
        </button>
      )}
    </div>
  );
}
