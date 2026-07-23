/**
 * App-wide scroll position save/restore for SPA back-button navigation.
 *
 * How it works:
 * - On every scroll (debounced), saves `window.scrollY` keyed by the current pathname
 *   into sessionStorage. This means every page's scroll position is remembered.
 * - When a page mounts, if the navigation was a POP (back/forward button),
 *   it restores the saved position. If it was a PUSH (new navigation), it scrolls to top.
 * - Uses popstate events to detect back/forward navigation.
 *
 * Usage: Call `useScrollRestore()` once in App.tsx or the root layout.
 */

import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";

const STORAGE_KEY = "videshi_scroll_positions";

function getScrollMap(): Record<string, number> {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveScrollMap(map: Record<string, number>) {
  try {
    // Cap entries to prevent unbounded growth
    const keys = Object.keys(map);
    if (keys.length > 50) {
      const toRemove = keys.slice(0, keys.length - 50);
      for (const k of toRemove) delete map[k];
    }
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(map));
  } catch {}
}

export default function useScrollRestore() {
  const location = useLocation();
  const prevPathRef = useRef(location.pathname);
  const isPopRef = useRef(false);
  const restoreCleanupRef = useRef<(() => void) | null>(null);

  // Disable browser's built-in scroll restoration — we handle it ourselves
  useEffect(() => {
    if ("scrollRestoration" in window.history) {
      window.history.scrollRestoration = "manual";
    }
  }, []);

  // Listen for popstate to detect back/forward
  useEffect(() => {
    const onPop = () => {
      isPopRef.current = true;
    };
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  // Save scroll position continuously (debounced)
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    const onScroll = () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const map = getScrollMap();
        map[location.pathname] = window.scrollY;
        saveScrollMap(map);
      }, 150);
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      clearTimeout(timer);
      window.removeEventListener("scroll", onScroll);
      // Final save on unmount
      const map = getScrollMap();
      map[location.pathname] = window.scrollY;
      saveScrollMap(map);
    };
  }, [location.pathname]);

  // On route change: restore or scroll to top
  useEffect(() => {
    // Cancel any pending restore from a previous navigation
    restoreCleanupRef.current?.();
    restoreCleanupRef.current = null;

    const wasPop = isPopRef.current;
    isPopRef.current = false;

    if (wasPop) {
      // Back/forward: restore saved position
      const map = getScrollMap();
      const savedY = map[location.pathname];
      if (savedY != null && savedY > 0) {
        // Pages load async content (articles, embeds, images, etc.) that
        // grows the page height over 1-3 seconds. The old rAF approach
        // gave up after ~320ms. Use staggered timeouts over 3s plus a
        // MutationObserver that fires whenever new DOM nodes render.
        let cancelled = false;
        const delays = [
          0, 50, 100, 150, 200, 300, 400, 500, 700, 900,
          1200, 1500, 2000, 2500, 3000,
        ];
        const timers: ReturnType<typeof setTimeout>[] = [];

        const tryScroll = () => {
          if (cancelled) return;
          window.scrollTo(0, savedY);
        };

        for (const delay of delays) {
          timers.push(setTimeout(tryScroll, delay));
        }

        // Also watch for DOM changes (new content rendering) and try to
        // restore when the page grows tall enough
        let observer: MutationObserver | null = null;
        try {
          observer = new MutationObserver(() => {
            if (cancelled) return;
            if (document.documentElement.scrollHeight >= savedY + 100) {
              window.scrollTo(0, savedY);
            }
          });
          observer.observe(document.body, {
            childList: true,
            subtree: true,
          });
          // Disconnect observer after 4 seconds
          timers.push(setTimeout(() => observer?.disconnect(), 4000));
        } catch {}

        restoreCleanupRef.current = () => {
          cancelled = true;
          timers.forEach(clearTimeout);
          observer?.disconnect();
        };
      }
    } else if (prevPathRef.current !== location.pathname) {
      // Forward navigation: scroll to top (unless it's the same page)
      window.scrollTo(0, 0);
    }

    prevPathRef.current = location.pathname;

    return () => {
      restoreCleanupRef.current?.();
      restoreCleanupRef.current = null;
    };
  }, [location.pathname]);
}
