/**
 * App-wide scroll position save/restore for SPA back-button navigation.
 *
 * How it works:
 * - On every scroll (debounced), saves `window.scrollY` keyed by the current pathname
 *   into sessionStorage. This means every page's scroll position is remembered.
 * - When a page mounts, if the navigation was a POP (back/forward button),
 *   it restores the saved position. If it was a PUSH (new navigation), it scrolls to top.
 * - Uses `history.state` to detect navigation type since react-router's
 *   useNavigationType isn't always reliable with lazy routes.
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
    const wasPop = isPopRef.current;
    isPopRef.current = false;

    if (wasPop) {
      // Back/forward: restore saved position
      const map = getScrollMap();
      const savedY = map[location.pathname];
      if (savedY != null && savedY > 0) {
        // Need to wait for content to render before scrolling
        // Use a progressive retry approach for lazy-loaded content
        let attempts = 0;
        const tryRestore = () => {
          window.scrollTo(0, savedY);
          attempts++;
          // If document isn't tall enough yet, keep trying
          if (attempts < 20 && document.documentElement.scrollHeight < savedY + window.innerHeight) {
            requestAnimationFrame(tryRestore);
          } else if (Math.abs(window.scrollY - savedY) > 50 && attempts < 20) {
            requestAnimationFrame(tryRestore);
          }
        };
        requestAnimationFrame(tryRestore);
      }
    } else if (prevPathRef.current !== location.pathname) {
      // Forward navigation: scroll to top (unless it's the same page)
      window.scrollTo(0, 0);
    }

    prevPathRef.current = location.pathname;
  }, [location.pathname]);
}
