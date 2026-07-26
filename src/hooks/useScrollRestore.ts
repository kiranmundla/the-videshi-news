/**
 * App-wide scroll position save/restore for SPA back-button navigation.
 *
 * Strategy:
 * - Tracks visited history entries via React Router's `location.key`.
 *   First visit → scroll to top. Revisit (back/forward) → restore saved position.
 *   This avoids the fragile `popstate` event listener race with React Router.
 * - Saves scroll position eagerly on link clicks (capture phase, before navigation)
 *   and continuously via a debounced scroll listener.
 * - Restores with staggered retries + MutationObserver to handle async content loading.
 *
 * Usage: Call `useScrollRestore()` once in App.tsx inside BrowserRouter.
 */

import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";

const STORAGE_KEY = "videshi_scroll_positions";
const MAX_ENTRIES = 50;

function getScrollMap(): Record<string, number> {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function savePosition(key: string, y: number) {
  try {
    const map = getScrollMap();
    map[key] = y;
    // Cap entries to prevent unbounded growth
    const keys = Object.keys(map);
    if (keys.length > MAX_ENTRIES) {
      for (const k of keys.slice(0, keys.length - MAX_ENTRIES)) delete map[k];
    }
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(map));
  } catch {}
}

export default function useScrollRestore() {
  const location = useLocation();
  // Track which history entries we've seen (by location.key).
  // A key we've seen before means back/forward navigation.
  const visitedKeys = useRef<Set<string>>(new Set());
  const restoreCleanupRef = useRef<(() => void) | null>(null);

  // 1. Disable browser's built-in scroll restoration — we handle it
  useEffect(() => {
    if ("scrollRestoration" in window.history) {
      window.history.scrollRestoration = "manual";
    }
  }, []);

  // 2. Eagerly save scroll position on link clicks BEFORE React Router navigates
  useEffect(() => {
    const key = location.key || location.pathname;
    const onClick = (e: MouseEvent) => {
      const anchor = (e.target as HTMLElement)?.closest?.("a");
      if (!anchor) return;
      const href = anchor.getAttribute("href");
      if (href && href.startsWith("/") && !href.startsWith("//")) {
        savePosition(key, window.scrollY);
      }
    };
    document.addEventListener("click", onClick, { capture: true });
    return () => document.removeEventListener("click", onClick, { capture: true });
  }, [location.key, location.pathname]);

  // 3. Continuously save scroll position (debounced) as user scrolls
  useEffect(() => {
    const key = location.key || location.pathname;
    let timer: ReturnType<typeof setTimeout>;
    const onScroll = () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        savePosition(key, window.scrollY);
      }, 200);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      clearTimeout(timer);
      window.removeEventListener("scroll", onScroll);
      // Don't save in cleanup — by now the DOM has changed and scrollY
      // may be 0, which would overwrite the eagerly-saved correct value.
    };
  }, [location.key, location.pathname]);

  // 4. On route change: detect back/forward via visited keys, then restore or scroll to top
  useEffect(() => {
    // Cancel any pending restore from a previous navigation
    restoreCleanupRef.current?.();
    restoreCleanupRef.current = null;

    const key = location.key || location.pathname;
    const isRevisit = visitedKeys.current.has(key);
    visitedKeys.current.add(key);

    if (isRevisit) {
      // ── Back/forward navigation: restore saved position ──
      const map = getScrollMap();
      const savedY = map[key];

      if (savedY != null && savedY > 0) {
        let cancelled = false;

        // Staggered retries over 5 seconds to wait for async content to render
        const delays = [0, 50, 100, 200, 300, 500, 800, 1200, 1800, 2500, 3500, 5000];
        const timers: ReturnType<typeof setTimeout>[] = [];

        const tryScroll = () => {
          if (cancelled) return;
          window.scrollTo(0, savedY);
        };

        for (const d of delays) {
          timers.push(setTimeout(tryScroll, d));
        }

        // Also watch for DOM changes and scroll when page is tall enough
        let observer: MutationObserver | null = null;
        try {
          observer = new MutationObserver(() => {
            if (cancelled) return;
            if (document.documentElement.scrollHeight >= savedY + 100) {
              window.scrollTo(0, savedY);
            }
          });
          observer.observe(document.body, { childList: true, subtree: true });
          timers.push(setTimeout(() => observer?.disconnect(), 6000));
        } catch {}

        restoreCleanupRef.current = () => {
          cancelled = true;
          timers.forEach(clearTimeout);
          observer?.disconnect();
        };
      }
    } else {
      // ── First visit: scroll to top ──
      window.scrollTo(0, 0);
    }

    return () => {
      restoreCleanupRef.current?.();
      restoreCleanupRef.current = null;
    };
  }, [location.key, location.pathname]);
}
