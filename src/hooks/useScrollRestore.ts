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
 * - Cancels restore immediately when user manually scrolls (wheel/touch/keyboard),
 *   so the restore never fights new user scroll input.
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
    const keys = Object.keys(map);
    if (keys.length > MAX_ENTRIES) {
      for (const k of keys.slice(0, keys.length - MAX_ENTRIES)) delete map[k];
    }
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(map));
  } catch {}
}

export default function useScrollRestore() {
  const location = useLocation();
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
    };
  }, [location.key, location.pathname]);

  // 4. On route change: detect back/forward via visited keys, then restore or scroll to top
  useEffect(() => {
    restoreCleanupRef.current?.();
    restoreCleanupRef.current = null;

    const key = location.key || location.pathname;
    const isRevisit = visitedKeys.current.has(key);
    visitedKeys.current.add(key);

    if (isRevisit) {
      const map = getScrollMap();
      const savedY = map[key];

      if (savedY != null && savedY > 0) {
        let cancelled = false;
        const timers: ReturnType<typeof setTimeout>[] = [];
        let observer: MutationObserver | null = null;

        // ── Central cleanup: stop all restore activity ──
        const cancelRestore = () => {
          if (cancelled) return;
          cancelled = true;
          timers.forEach(clearTimeout);
          observer?.disconnect();
          window.removeEventListener("wheel", onUserScroll);
          window.removeEventListener("touchmove", onUserScroll);
          window.removeEventListener("keydown", onUserKey);
        };

        // ── Cancel restore if user manually scrolls ──
        // This prevents the observer from fighting new user scroll input.
        const onUserScroll = () => { cancelRestore(); };
        const onUserKey = (e: KeyboardEvent) => {
          if (["ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End", " "].includes(e.key)) {
            cancelRestore();
          }
        };

        const tryScroll = () => {
          if (cancelled) return;
          window.scrollTo(0, savedY);
        };

        // Staggered retries over 5s to wait for async content
        const delays = [0, 50, 100, 200, 300, 500, 800, 1200, 1800, 2500, 3500, 5000];
        for (const d of delays) {
          timers.push(setTimeout(tryScroll, d));
        }

        // Start listening for user interaction after a brief delay
        // (300ms grace period so our own initial scrollTo doesn't trigger it)
        timers.push(setTimeout(() => {
          if (!cancelled) {
            window.addEventListener("wheel", onUserScroll, { passive: true });
            window.addEventListener("touchmove", onUserScroll, { passive: true });
            window.addEventListener("keydown", onUserKey);
          }
        }, 300));

        // MutationObserver: restore when page grows tall enough
        try {
          observer = new MutationObserver(() => {
            if (cancelled) return;
            if (document.documentElement.scrollHeight >= savedY + 100) {
              window.scrollTo(0, savedY);
            }
          });
          observer.observe(document.body, { childList: true, subtree: true });
          // Hard timeout: stop everything after 6s
          timers.push(setTimeout(cancelRestore, 6000));
        } catch {}

        restoreCleanupRef.current = cancelRestore;
      }
    } else {
      window.scrollTo(0, 0);
    }

    return () => {
      restoreCleanupRef.current?.();
      restoreCleanupRef.current = null;
    };
  }, [location.key, location.pathname]);
}
