/**
 * App-wide scroll position save/restore for SPA back-button navigation.
 *
 * How it works:
 * - Continuously tracks scrollY in a ref and saves to sessionStorage on scroll (debounced).
 * - On link clicks, eagerly saves the current scroll position BEFORE React Router navigates.
 * - On back/forward (popstate), restores saved position with staggered retries + MutationObserver.
 * - On forward navigation, scrolls to top.
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
  // Keep a live reference to the current scroll position + pathname
  const lastScrollRef = useRef({ pathname: location.pathname, y: 0 });

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

  // Eagerly save scroll position on link clicks BEFORE navigation
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const target = (e.target as HTMLElement)?.closest?.("a");
      if (!target) return;
      const href = target.getAttribute("href");
      // Only save for internal navigation links (not external, not anchors)
      if (href && href.startsWith("/") && !href.startsWith("//")) {
        const map = getScrollMap();
        map[lastScrollRef.current.pathname] = window.scrollY;
        saveScrollMap(map);
      }
    };
    document.addEventListener("click", onClick, { capture: true });
    return () => document.removeEventListener("click", onClick, { capture: true });
  }, []);

  // Track scroll position continuously in ref + save debounced to sessionStorage
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    const onScroll = () => {
      // Always update ref immediately (no debounce)
      lastScrollRef.current = { pathname: location.pathname, y: window.scrollY };
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
      // Final save on unmount — use the ref value which was captured BEFORE navigation
      const { pathname, y } = lastScrollRef.current;
      if (pathname === location.pathname) {
        const map = getScrollMap();
        map[pathname] = y;
        saveScrollMap(map);
      }
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
        // grows the page height over 1-3 seconds. Use staggered timeouts
        // over 5s plus a MutationObserver that fires whenever new DOM nodes render.
        let cancelled = false;
        const delays = [
          0, 50, 100, 150, 200, 300, 400, 500, 700, 900,
          1200, 1500, 2000, 2500, 3000, 4000, 5000,
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
          // Disconnect observer after 6 seconds
          timers.push(setTimeout(() => observer?.disconnect(), 6000));
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
    // Update ref for the new page
    lastScrollRef.current = { pathname: location.pathname, y: 0 };

    return () => {
      restoreCleanupRef.current?.();
      restoreCleanupRef.current = null;
    };
  }, [location.pathname]);
}
