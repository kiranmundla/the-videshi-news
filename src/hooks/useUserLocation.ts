import { useState, useEffect, useCallback } from "react";

export interface UserLocation {
  latitude: number;
  longitude: number;
  city?: string;
  region?: string;
  source: "browser" | "ip" | "none";
}

const STORAGE_KEY = "videshi_user_geo";
const STORAGE_TTL = 1000 * 60 * 60; // 1 hour

/* ------------------------------------------------------------------ */
/* Cached read / write                                                 */
/* ------------------------------------------------------------------ */

function getCached(): UserLocation | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const { ts, loc } = JSON.parse(raw);
    if (Date.now() - ts > STORAGE_TTL) return null;
    return loc as UserLocation;
  } catch {
    return null;
  }
}

function setCache(loc: UserLocation) {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ ts: Date.now(), loc }),
    );
  } catch {
    /* quota exceeded — ignore */
  }
}

/* ------------------------------------------------------------------ */
/* IP-based geo (Vercel headers, free, instant, no prompt)             */
/* ------------------------------------------------------------------ */

async function fetchIpGeo(): Promise<UserLocation | null> {
  try {
    const r = await fetch("/api/geo");
    if (!r.ok) return null;
    const d = await r.json();
    if (d.latitude && d.longitude) {
      return {
        latitude: d.latitude,
        longitude: d.longitude,
        city: d.city || undefined,
        region: d.region || undefined,
        source: "ip",
      };
    }
  } catch {
    /* network error */
  }
  return null;
}

/* ------------------------------------------------------------------ */
/* Browser geolocation (precise, requires user permission)             */
/* ------------------------------------------------------------------ */

function getBrowserGeo(): Promise<UserLocation | null> {
  return new Promise((resolve) => {
    if (!navigator.geolocation) return resolve(null);
    navigator.geolocation.getCurrentPosition(
      (pos) =>
        resolve({
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          source: "browser",
        }),
      () => resolve(null),
      { enableHighAccuracy: false, timeout: 5000 },
    );
  });
}

/* ------------------------------------------------------------------ */
/* Hook                                                                */
/* ------------------------------------------------------------------ */

/**
 * Returns user location, resolving in priority:
 *   1. localStorage cache (1-hr TTL)
 *   2. Vercel IP geo (/api/geo, free, no prompt)
 *
 * Call `requestPrecise()` to upgrade to browser geolocation (shows
 * the browser permission prompt). Precise location is cached and
 * replaces the IP-based one.
 */
export function useUserLocation() {
  const [location, setLocation] = useState<UserLocation | null>(getCached);
  const [loading, setLoading] = useState(!getCached());

  // On mount: if no cache, fetch IP geo
  useEffect(() => {
    if (location) return;
    let cancelled = false;
    fetchIpGeo().then((loc) => {
      if (cancelled) return;
      if (loc) {
        setCache(loc);
        setLocation(loc);
      }
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Upgrade to browser geolocation on demand (call on Events/Directory pages)
  const requestPrecise = useCallback(async () => {
    setLoading(true);
    const loc = await getBrowserGeo();
    if (loc) {
      // Keep city/region from IP if browser doesn't provide them
      const merged: UserLocation = {
        ...loc,
        city: loc.city || location?.city,
        region: loc.region || location?.region,
      };
      setCache(merged);
      setLocation(merged);
      setLoading(false);
      return merged;
    }
    setLoading(false);
    return null;
  }, [location]);

  return { location, loading, requestPrecise };
}
