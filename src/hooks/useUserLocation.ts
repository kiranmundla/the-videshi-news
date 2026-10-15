import { useState, useEffect, useCallback, useRef } from "react";
import {
  getStoredHubLocation,
  setStoredHubLocation,
  resolvePlaceLabel,
  isGenericHubLabel,
  HUB_LOCATION_CHANGED_EVENT,
  type HubLocation,
} from "@/hooks/useHubLocation";

export interface UserLocation {
  latitude: number;
  longitude: number;
  city?: string;
  region?: string;
  /** "hub" = derived from the canonical Hub record (videshi-user-location) */
  source: "browser" | "ip" | "hub" | "none";
}

const STORAGE_KEY = "videshi_user_geo";
const STORAGE_TTL = 1000 * 60 * 60; // 1 hour

/* ------------------------------------------------------------------ */
/* Cached read / write (transient geo fixes only — IP + precise)       */
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
/* Canonical location: the Hub record wins (2026-10-14 unification)    */
/*                                                                     */
/* The site keeps ONE user location: the Hub record                    */
/* (videshi-user-location, written by useHubLocation). It is an        */
/* explicit, non-expiring user setting with real coords + label.       */
/* The geo cache below is only a transient fix store (IP estimate /    */
/* precise browser fix, 1 h TTL). Before this unification the two      */
/* stores were independent: on an origin where only the Hub record     */
/* existed, the homepage Events strip read an empty geo store and      */
/* silently fell back to national date order — Kiran was shown         */
/* Honolulu and Noblesville events while the banner on the same page   */
/* said Dublin, CA. Resolution is now: Hub record → fresh geo cache    */
/* → IP fetch. IP fixes deliberately never write the Hub record (a     */
/* coarse passive estimate must not create or clobber the user's       */
/* explicit setting); precise browser fixes DO write through to        */
/* both stores (see requestPrecise).                                   */
/* ------------------------------------------------------------------ */

/** Derive a UserLocation from the canonical Hub record. The record's
 * own city/state fields are authoritative; a non-generic label
 * ("City, ST") is parsed as a fallback for legacy records whose
 * city/state fields are empty. A generic label with empty fields
 * yields no city — never a fabricated one (the coords still flow, so
 * distance filtering works; the Hub surfaces heal such labels via
 * resolvePlaceLabel). */
export function hubToUserLocation(hub: HubLocation): UserLocation {
  let city = hub.city?.trim() || undefined;
  let region = hub.state?.trim() || undefined;
  if ((!city || !region) && hub.label && !isGenericHubLabel(hub.label)) {
    const parts = hub.label.split(",").map((p) => p.trim());
    if (!city && parts[0]) city = parts[0];
    if (!region && parts.length > 1) region = parts[parts.length - 1];
  }
  return {
    latitude: hub.lat,
    longitude: hub.lon,
    city,
    region,
    source: "hub",
  };
}

/** The one resolution rule every geo consumer shares: the Hub record
 * wins whenever it exists; otherwise the freshest transient fix. */
export function resolveEffectiveUserLocation(
  hub: HubLocation | null,
  cachedGeo: UserLocation | null,
): UserLocation | null {
  if (hub && typeof hub.lat === "number" && typeof hub.lon === "number") {
    return hubToUserLocation(hub);
  }
  return cachedGeo;
}

function sameLocation(a: UserLocation | null, b: UserLocation | null): boolean {
  if (a === b) return true;
  if (!a || !b) return false;
  return (
    a.latitude === b.latitude &&
    a.longitude === b.longitude &&
    a.city === b.city &&
    a.region === b.region &&
    a.source === b.source
  );
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
 * Returns the user's location from the ONE canonical store.
 *
 * Resolution priority:
 *   1. The Hub record (videshi-user-location) — explicit user setting,
 *      never expires; wins whenever it exists.
 *   2. Transient geo cache (1-hr TTL: last IP estimate / precise fix).
 *   3. Vercel IP geo (/api/geo, free, no prompt) — fills the cache
 *      only; never creates or overwrites the Hub record.
 *
 * Call `requestPrecise()` to upgrade to browser geolocation (shows
 * the browser permission prompt). A precise fix is written through to
 * BOTH stores — geo cache and the Hub record (label resolved by the
 * Hub's own resolvePlaceLabel rules) — so every surface agrees.
 */
export function useUserLocation() {
  const [location, setLocation] = useState<UserLocation | null>(() =>
    resolveEffectiveUserLocation(getStoredHubLocation(), getCached()),
  );
  const [loading, setLoading] = useState(
    () => resolveEffectiveUserLocation(getStoredHubLocation(), getCached()) === null,
  );
  const locationRef = useRef(location);
  locationRef.current = location;
  const ipFetchInFlight = useRef(false);

  const applyLocation = useCallback((next: UserLocation | null) => {
    if (!sameLocation(locationRef.current, next)) {
      locationRef.current = next;
      setLocation(next);
    }
  }, []);

  const ensureIpFetch = useCallback(() => {
    if (ipFetchInFlight.current) return;
    ipFetchInFlight.current = true;
    fetchIpGeo()
      .then((loc) => {
        ipFetchInFlight.current = false;
        if (loc) {
          setCache(loc);
          // A Hub record may have appeared while the fetch was in
          // flight — it still wins over this passive estimate.
          applyLocation(
            resolveEffectiveUserLocation(getStoredHubLocation(), loc),
          );
        }
        setLoading(false);
      })
      .catch(() => {
        ipFetchInFlight.current = false;
        setLoading(false);
      });
  }, [applyLocation]);

  // On mount: if nothing resolved synchronously, fetch IP geo.
  useEffect(() => {
    if (locationRef.current) {
      setLoading(false);
      return;
    }
    ensureIpFetch();
  }, [ensureIpFetch]);

  // Stay in sync with the canonical record: Hub writes (this tab via
  // the change event, other tabs via `storage`) re-resolve instantly,
  // so e.g. picking a Hub city updates the homepage strip without a
  // reload, and clearing it falls back to the transient geo fix / IP.
  useEffect(() => {
    const onStoreChanged = () => {
      const eff = resolveEffectiveUserLocation(
        getStoredHubLocation(),
        getCached(),
      );
      if (eff) {
        applyLocation(eff);
        setLoading(false);
      } else if (!locationRef.current) {
        ensureIpFetch();
      } else {
        // Hub cleared and no fresh geo fix: keep showing the last
        // known fix for this session rather than blanking surfaces,
        // and refresh the cache in the background.
        ensureIpFetch();
      }
    };
    window.addEventListener(HUB_LOCATION_CHANGED_EVENT, onStoreChanged);
    window.addEventListener("storage", onStoreChanged);
    return () => {
      window.removeEventListener(HUB_LOCATION_CHANGED_EVENT, onStoreChanged);
      window.removeEventListener("storage", onStoreChanged);
    };
  }, [applyLocation, ensureIpFetch]);

  // Upgrade to browser geolocation on demand (call on Events/Directory pages)
  const requestPrecise = useCallback(async () => {
    setLoading(true);
    const loc = await getBrowserGeo();
    if (loc) {
      // Keep city/region from IP if browser doesn't provide them
      const merged: UserLocation = {
        ...loc,
        city: loc.city || locationRef.current?.city,
        region: loc.region || locationRef.current?.region,
      };
      setCache(merged);
      // Write through to the canonical Hub record so the Hub, the
      // banner and every geo consumer agree on the precise fix. The
      // label is produced by the Hub's own resolver — the label rules
      // themselves are unchanged.
      try {
        const place = await resolvePlaceLabel(merged.latitude, merged.longitude, {
          city: merged.city,
          region: merged.region,
        });
        const hubRecord: HubLocation = {
          city: place.city || merged.city || "",
          state: place.state || merged.region || "",
          lat: merged.latitude,
          lon: merged.longitude,
          label: place.label,
        };
        setStoredHubLocation(hubRecord);
      } catch {
        /* Hub write-through is best-effort; the geo cache still holds the fix */
      }
      applyLocation(
        resolveEffectiveUserLocation(getStoredHubLocation(), merged),
      );
      setLoading(false);
      return merged;
    }
    setLoading(false);
    return null;
  }, [applyLocation]);

  return { location, loading, requestPrecise };
}
