import { useEffect, useRef, useState, type ReactNode } from "react";

/* ── LazyMount ────────────────────────────────────────────────
   Mounts children only when the section is near the viewport
   (IntersectionObserver, 800px preload margin). Before that it
   renders an empty placeholder with a min-height to avoid
   layout shift. Once mounted it stays mounted.

   Use for below-the-fold homepage sections so the initial page
   load only pays for what's visible: no data fetches, no DOM,
   no images for sections the user hasn't scrolled to. */

export default function LazyMount({
  children,
  minHeight = 320,
}: {
  children: ReactNode;
  minHeight?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (typeof IntersectionObserver === "undefined") {
      setVisible(true);
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setVisible(true);
          io.disconnect();
        }
      },
      { rootMargin: "800px 0px" }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div ref={ref} style={visible ? undefined : { minHeight }}>
      {visible ? children : null}
    </div>
  );
}
