import { useState, useCallback } from "react";

export interface HubLocation {
  city: string;
  state: string;
  lat: number;
  lon: number;
  /** Display label, e.g. "San Jose, CA" */
  label: string;
}

const STORAGE_KEY = "videshi-user-location";

function readStored(): HubLocation | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const loc = JSON.parse(raw);
    if (typeof loc.lat !== "number" || typeof loc.lon !== "number") return null;
    return loc as HubLocation;
  } catch {
    return null;
  }
}

/* ------------------------------------------------------------------ */
/* Diaspora clusters — the picker and local-news resolution read the  */
/* SAME canonical table the local-news builder consumes:              */
/* /data/clusters.json (ACS 2024 suburb clusters, Phase 1). The       */
/* built-in fallback below covers the top clusters if the fetch       */
/* fails, so the hub never breaks.                                    */
/* ------------------------------------------------------------------ */

export interface ClusterMember {
  name: string;
  state: string;
  lat: number;
  lon: number;
}

export interface Cluster {
  id: string;
  label: string;
  state: string;
  center: { lat: number; lon: number };
  anchor: string;
  query_cities: string[];
  aliases: string[];
  members: ClusterMember[];
  block: string[];
  context_guard: string | null;
}

const m = (name: string, state: string, lat: number, lon: number): ClusterMember => ({ name, state, lat, lon });
const c = (
  id: string,
  label: string,
  state: string,
  lat: number,
  lon: number,
  anchor: string,
  members: ClusterMember[],
): Cluster => ({
  id, label, state, center: { lat, lon }, anchor, members,
  query_cities: [], aliases: [], block: [], context_guard: null,
});

export const FALLBACK_CLUSTERS: Cluster[] = [
  c("new-york-ny", "New York, NY", "NY", 40.7128, -74.006, "New York", [
    m("New York", "NY", 40.7128, -74.006), m("Jersey City", "NJ", 40.7178, -74.0431),
    m("Edison", "NJ", 40.5187, -74.4121),
  ]),
  c("san-jose-ca", "San Jose, CA", "CA", 37.3382, -121.8863, "San Jose", [
    m("San Jose", "CA", 37.3382, -121.8863), m("Sunnyvale", "CA", 37.3688, -122.0363),
    m("Santa Clara", "CA", 37.3541, -121.9552), m("Milpitas", "CA", 37.4323, -121.8996),
  ]),
  c("fremont-ca", "Fremont, CA", "CA", 37.5485, -121.9886, "Fremont", [
    m("Fremont", "CA", 37.5485, -121.9886),
  ]),
  c("frisco-plano-tx", "Frisco / Plano, TX", "TX", 33.1507, -96.8236, "Frisco", [
    m("Frisco", "TX", 33.1507, -96.8236), m("Plano", "TX", 33.0198, -96.6989),
  ]),
  c("seattle-wa", "Seattle, WA", "WA", 47.6062, -122.3321, "Seattle", [
    m("Seattle", "WA", 47.6062, -122.3321), m("Bellevue", "WA", 47.6101, -122.2015),
    m("Redmond", "WA", 47.674, -122.1215),
  ]),
  c("dublin-ca", "Dublin, CA", "CA", 37.7022, -121.9358, "Dublin", [
    m("Dublin", "CA", 37.7022, -121.9358), m("San Ramon", "CA", 37.7799, -121.978),
    m("Pleasanton", "CA", 37.6624, -121.8747), m("Livermore", "CA", 37.6819, -121.768),
  ]),
  c("chicago-il", "Chicago, IL", "IL", 41.8781, -87.6298, "Chicago", [
    m("Chicago", "IL", 41.8781, -87.6298), m("Naperville", "IL", 41.7508, -88.1535),
    m("Schaumburg", "IL", 42.0334, -88.0834),
  ]),
  c("irving-tx", "Irving, TX", "TX", 32.8141, -96.9489, "Irving", [
    m("Irving", "TX", 32.8141, -96.9489), m("Dallas", "TX", 32.7767, -96.797),
    m("Arlington", "TX", 32.7357, -97.1081),
  ]),
  c("edison-nj", "Edison, NJ", "NJ", 40.5187, -74.4121, "Edison", [
    m("Edison", "NJ", 40.5187, -74.4121), m("Iselin", "NJ", 40.5751, -74.3224),
  ]),
  c("washington-dc", "Washington, DC", "DC", 38.9072, -77.0369, "Washington", [
    m("Washington", "DC", 38.9072, -77.0369), m("Arlington", "VA", 38.8816, -77.091),
    m("Bethesda", "MD", 38.9847, -77.0947),
  ]),
  c("los-angeles-ca", "Los Angeles, CA", "CA", 34.0522, -118.2437, "Los Angeles", [
    m("Los Angeles", "CA", 34.0522, -118.2437), m("Irvine", "CA", 33.6846, -117.8265),
    m("Cerritos", "CA", 33.8583, -118.0648),
  ]),
  c("houston-tx", "Houston, TX", "TX", 29.7604, -95.3698, "Houston", [
    m("Houston", "TX", 29.7604, -95.3698), m("Sugar Land", "TX", 29.6197, -95.6349),
    m("Katy", "TX", 29.7858, -95.8245),
  ]),
];

let clustersCache: Cluster[] | null = null;
let clustersPromise: Promise<Cluster[]> | null = null;

/** Load the canonical cluster table (module-cached; falls back to the
 * built-in top-clusters list so the hub never breaks). */
export async function loadClusters(): Promise<Cluster[]> {
  if (clustersCache) return clustersCache;
  if (clustersPromise) return clustersPromise;
  clustersPromise = fetch("/data/clusters.json")
    .then((r) => {
      if (!r.ok) throw new Error(`clusters fetch ${r.status}`);
      return r.json();
    })
    .then((data: { clusters: Cluster[] }) => {
      clustersCache =
        Array.isArray(data?.clusters) && data.clusters.length
          ? data.clusters
          : FALLBACK_CLUSTERS;
      return clustersCache;
    })
    .catch(() => {
      clustersCache = FALLBACK_CLUSTERS;
      return clustersCache;
    });
  return clustersPromise;
}

/** Synchronous view: loaded clusters, or the built-in fallback until the
 * fetch lands. */
export function getCachedClusters(): Cluster[] {
  return clustersCache ?? FALLBACK_CLUSTERS;
}

/**
 * User-chosen hub location, persisted in localStorage.
 * Unlike the transient IP-geo hook, this is an explicit user setting —
 * it never expires and is only changed by the user.
 */
export function useHubLocation() {
  const [location, setLocationState] = useState<HubLocation | null>(readStored);

  const setLocation = useCallback((loc: HubLocation) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(loc));
    } catch {
      /* quota exceeded — ignore */
    }
    setLocationState(loc);
  }, []);

  const clearLocation = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    setLocationState(null);
  }, []);

  return { location, setLocation, clearLocation, isSet: location !== null };
}

/** Great-circle distance in miles. */
export function haversineMiles(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number,
): number {
  const R = 3958.8; // Earth radius in miles
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}
