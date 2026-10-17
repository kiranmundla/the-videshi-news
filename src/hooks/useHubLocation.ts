import { useState, useCallback, useEffect, useRef } from "react";
import { nearestZipPlace } from "@/lib/geo";

/** How a Hub record got its coordinates:
 *  - "manual": the reader deliberately chose the place (metro picker
 *    or ZIP entry). NEVER auto-overwritten — it is an explicit setting.
 *  - "geolocation": a precise device fix (browser geolocation, via the
 *    setup button, the Hub page-land detect, or the unified geo hook's
 *    write-through). Auto records may be refreshed when the device has
 *    clearly moved — see maybeRefreshHubLocation.
 *  - "ip": a coarse IP estimate stored by the page-land fallback.
 *    Also auto — a later precise fix should refine it.
 * Records written before 2026-10-14 carry no source; classifyHubRecord
 * reconstructs their class from the picker signature. */
export type HubLocationSource = "manual" | "geolocation" | "ip";

export interface HubLocation {
  city: string;
  state: string;
  lat: number;
  lon: number;
  /** Display label, e.g. "San Jose, CA" */
  label: string;
  /** Provenance — see HubLocationSource. Absent on legacy records. */
  source?: HubLocationSource;
  /** Epoch ms when this record was written. */
  setAt?: number;
}

const STORAGE_KEY = "videshi-user-location";

/** The Hub record is the site's ONE canonical location (2026-10-14
 * unification): useUserLocation resolves through it, so every surface
 * (Hub, homepage banner, Events strip, Events/Directory/Kids near-me)
 * agrees on a single place. This event is dispatched on every write
 * so other mounted hooks re-read the record immediately; the
 * `storage` event covers other tabs. */
export const HUB_LOCATION_CHANGED_EVENT = "videshi-hub-location-changed";

function notifyHubLocationChanged() {
  try {
    window.dispatchEvent(new Event(HUB_LOCATION_CHANGED_EVENT));
  } catch {
    /* non-browser context — ignore */
  }
}

/** Write the canonical record + notify listeners. The single write
 * path for this store: useHubLocation's setLocation and
 * useUserLocation's precise-fix write-through both go through here. */
export function setStoredHubLocation(loc: HubLocation) {
  try {
    const stamped: HubLocation =
      typeof loc.setAt === "number" ? loc : { ...loc, setAt: Date.now() };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(stamped));
  } catch {
    /* quota exceeded — ignore */
  }
  notifyHubLocationChanged();
}

export function getStoredHubLocation(): HubLocation | null {
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

/** Labels that carry no place information. Records carrying one of
 * these alongside real coordinates are legacy artifacts: the Hub's
 * original auto-detect (pre-Oct-2026) stored "Near You" unconditionally
 * with the detected coords, and the LocationSetup "Use my location"
 * button stored "Current location". Because a stored record is sticky
 * (never re-prompted), those labels survived every later fix — Kiran
 * hit one on the vercel.app origin, whose localStorage is separate
 * from thevideshi.com (2026-10-14). They are healed on load by
 * useHubLocation via resolvePlaceLabel. */
const GENERIC_HUB_LABELS = new Set(["near you", "current location"]);

export function isGenericHubLabel(label: string | null | undefined): boolean {
  if (!label) return true;
  return GENERIC_HUB_LABELS.has(label.trim().toLowerCase());
}

export interface ResolvedPlace {
  label: string;
  city: string;
  state: string;
}

/** Resolve a human place label for raw coordinates. Fallback order —
 * a generic label is the LAST resort, never the default:
 *   1. Nearest cluster CENTER within 100 mi → the cluster's label.
 *      Center distance, NOT member distance (see the note in
 *      YourHubPage's resolveMetroNews: pooled buckets would steal
 *      labels from standalone clusters).
 *   2. Nearest cluster MEMBER city within 100 mi → "City, ST" of
 *      that member (covers places a pooled bucket reaches but no
 *      center is near).
 *   3. IP-derived city/region, when the caller has it.
 *   4. Reverse-resolve via the local zip database (nearestZipPlace).
 *   5. "Near You" — only when nothing above resolves. Callers only
 *      invoke this WITH coordinates, so a generic result means the
 *      coords are outside every dataset we carry (e.g. non-US).
 * Never throws. */
export async function resolvePlaceLabel(
  lat: number,
  lon: number,
  ip?: { city?: string; region?: string } | null,
): Promise<ResolvedPlace> {
  try {
    const clusters = await loadClusters().catch(() => getCachedClusters());
    let bestCenter: { cluster: Cluster; dist: number } | null = null;
    let bestMember: { member: ClusterMember; dist: number } | null = null;
    for (const cl of clusters) {
      const dc = haversineMiles(lat, lon, cl.center.lat, cl.center.lon);
      if (!bestCenter || dc < bestCenter.dist) {
        bestCenter = { cluster: cl, dist: dc };
      }
      for (const mb of cl.members) {
        const dm = haversineMiles(lat, lon, mb.lat, mb.lon);
        if (!bestMember || dm < bestMember.dist) {
          bestMember = { member: mb, dist: dm };
        }
      }
    }
    if (bestCenter && bestCenter.dist <= 100) {
      return {
        label: bestCenter.cluster.label,
        city: bestCenter.cluster.anchor,
        state: bestCenter.cluster.state,
      };
    }
    if (bestMember && bestMember.dist <= 100) {
      const mb = bestMember.member;
      return { label: `${mb.name}, ${mb.state}`, city: mb.name, state: mb.state };
    }
  } catch {
    /* clusters unavailable — fall through to IP / zip resolution */
  }
  if (ip?.city) {
    return {
      label: ip.region ? `${ip.city}, ${ip.region}` : ip.city,
      city: ip.city,
      state: ip.region ?? "",
    };
  }
  const place = await nearestZipPlace(lat, lon, 100).catch(() => null);
  if (place) {
    return { label: `${place.city}, ${place.state}`, city: place.city, state: place.state };
  }
  return { label: "Near You", city: "", state: "" };
}

/* ------------------------------------------------------------------ */
/* Sticky-record refresh (2026-10-14, Kiran's Fremont→Dublin report)   */
/*                                                                     */
/* The Hub record never expired, so a record that was itself AUTO-     */
/* detected kept pointing at the old city forever after the reader    */
/* travelled: Events/Directory re-detect per visit and showed Dublin,  */
/* while Your Hub and the homepage banner kept saying Fremont with     */
/* distances computed from Fremont. The fix: an auto record refreshes  */
/* when a PRECISE position is available without prompting and the      */
/* device has materially moved. A manual pick is an explicit user      */
/* setting and is never auto-overwritten.                              */
/* ------------------------------------------------------------------ */

/** How strongly a stored record's provenance is established:
 *  - "manual": an EXPLICIT source of "manual" — written since
 *    2026-10-14 by the metro picker or a ZIP submit, i.e. the reader
 *    demonstrably chose the place. Never auto-overwritten, no
 *    exceptions.
 *  - "inferred-manual": NO source field, but label + coordinates
 *    match the picker signature below. Only an INFERENCE — and a
 *    fallible one: the picker is not the only writer that can
 *    produce it. The IP fallback stores the coordinates /api/geo
 *    returns, which are the IP database's city CENTROID, and the
 *    cluster table's centers are those same centroids (Fremont's
 *    center, 37.5485/-121.9886, is the standard IP-geo centroid for
 *    Fremont); resolvePlaceLabel then labels such a record with the
 *    cluster's label. A legacy IP-written record is therefore
 *    byte-identical to a legacy picker pick. An inference must not
 *    lock a reader's location forever: the refresh may correct an
 *    inferred-manual record when a fresh PRECISE fix materially
 *    disagrees — and the correction stamps an explicit source, so
 *    the record's class is unambiguous from then on. (Kiran's stuck
 *    "Fremont, CA", 2026-10-15: a pre-provenance record matching
 *    this signature was treated as a deliberate pick and could
 *    never refresh.)
 *  - "auto": an explicit geolocation/ip source, or a legacy record
 *    without the picker signature — every auto writer (page-land
 *    detect, "Use my location", the geo hook's write-through)
 *    stores MEASURED coordinates, which essentially never coincide
 *    exactly with table values. Legacy ZIP entries also classify
 *    as auto: their centroid coords are indistinguishable from
 *    measured ones — ZIP submits are tagged "manual" at write
 *    time going forward. */
export type HubRecordClass = "manual" | "inferred-manual" | "auto";

export function classifyHubRecord(
  loc: HubLocation,
  clusters: Cluster[],
): HubRecordClass {
  if (loc.source) return loc.source === "manual" ? "manual" : "auto";
  for (const cl of clusters) {
    if (loc.label !== cl.label) continue;
    if (loc.lat === cl.center.lat && loc.lon === cl.center.lon) {
      return "inferred-manual";
    }
    for (const mb of cl.members) {
      if (loc.lat === mb.lat && loc.lon === mb.lon) return "inferred-manual";
    }
  }
  return "auto";
}

/* The transient geo cache (owned by useUserLocation). Read directly
 * here rather than imported — useUserLocation already imports this
 * module, and a back-import would create a cycle. Key + TTL mirror
 * useUserLocation's STORAGE_KEY / STORAGE_TTL. */
const GEO_CACHE_KEY = "videshi_user_geo";
const GEO_CACHE_TTL_MS = 1000 * 60 * 60; // 1 hour, same as useUserLocation

export interface PreciseFix {
  lat: number;
  lon: number;
}

/** A fresh PRECISE fix from the transient geo cache, or null. Only
 * browser-geolocation entries count: an IP estimate is too coarse to
 * override a stored precise fix, so it never triggers a rewrite. */
export function getFreshPreciseGeoFix(): PreciseFix | null {
  try {
    const raw = localStorage.getItem(GEO_CACHE_KEY);
    if (!raw) return null;
    const { ts, loc } = JSON.parse(raw);
    if (!loc || typeof ts !== "number" || Date.now() - ts > GEO_CACHE_TTL_MS) {
      return null;
    }
    if (loc.source !== "browser") return null;
    if (typeof loc.latitude !== "number" || typeof loc.longitude !== "number") {
      return null;
    }
    return { lat: loc.latitude, lon: loc.longitude };
  } catch {
    return null;
  }
}

/** A precise fix from the browser WITHOUT ever prompting: only asks
 * for a position when geolocation permission is already 'granted'.
 * When the Permissions API is unavailable the no-prompt guarantee
 * can't be verified, so it conservatively returns null. */
export async function getGrantedGeolocationFix(
  timeoutMs = 4000,
): Promise<PreciseFix | null> {
  try {
    if (typeof navigator === "undefined" || !navigator.geolocation) return null;
    if (!navigator.permissions?.query) return null;
    let state: PermissionState;
    try {
      const status = await navigator.permissions.query({
        name: "geolocation" as PermissionName,
      });
      state = status.state;
    } catch {
      return null;
    }
    if (state !== "granted") return null;
    return await new Promise<PreciseFix | null>((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (pos) =>
          resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
        () => resolve(null),
        { enableHighAccuracy: false, timeout: timeoutMs, maximumAge: 60000 },
      );
    });
  } catch {
    return null;
  }
}

/** A FRESH precise fix for page-load auto-detection: maximumAge 0,
 * so the browser must produce a current position or error — never
 * a cached one. (The 2026-10-16 Directory bug, Kiran's catch: the
 * page's own auto-detect accepted maximumAge 300000 and latched a
 * stale Fremont fix on a device sitting in Dublin; the manual pin,
 * which leaves maximumAge at its 0 default, got Dublin instantly.
 * Every auto-detect-on-load call site uses this helper so the
 * stale latch cannot come back.) Resolves null on any failure —
 * callers fall back to IP geo as before. NOTE: unlike
 * getGrantedGeolocationFix this CAN surface a permission prompt;
 * it is only for surfaces that already request geolocation on
 * load. */
export function getFreshGeolocationFix(
  timeoutMs = 8000,
): Promise<PreciseFix | null> {
  return new Promise((resolve) => {
    if (typeof navigator === "undefined" || !navigator.geolocation) {
      return resolve(null);
    }
    navigator.geolocation.getCurrentPosition(
      (pos) =>
        resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
      () => resolve(null),
      { enableHighAccuracy: false, timeout: timeoutMs, maximumAge: 0 },
    );
  });
}

/** Nearest cluster by CENTER within maxMiles (same center rule as
 * resolvePlaceLabel), or null when no center is close enough. */
export function nearestClusterId(
  lat: number,
  lon: number,
  clusters: Cluster[],
  maxMiles = 100,
): string | null {
  let best: { id: string; dist: number } | null = null;
  for (const cl of clusters) {
    const d = haversineMiles(lat, lon, cl.center.lat, cl.center.lon);
    if (!best || d < best.dist) best = { id: cl.id, dist: d };
  }
  return best && best.dist <= maxMiles ? best.id : null;
}

/** Minimum move (miles) that counts as "the device travelled", when
 * the resolved cluster doesn't already say so. */
export const HUB_REFRESH_MIN_DISTANCE_MILES = 5;

/** Materially different = the resolved cluster changed, or the fix is
 * more than HUB_REFRESH_MIN_DISTANCE_MILES from the stored coords.
 * A ~1 mi move inside the same cluster is not material — no churn. */
export function isMateriallyDifferentLocation(
  stored: HubLocation,
  fix: PreciseFix,
  clusters: Cluster[],
): boolean {
  if (haversineMiles(stored.lat, stored.lon, fix.lat, fix.lon) >
    HUB_REFRESH_MIN_DISTANCE_MILES) {
    return true;
  }
  const a = nearestClusterId(stored.lat, stored.lon, clusters);
  const b = nearestClusterId(fix.lat, fix.lon, clusters);
  return a !== null && b !== null && a !== b;
}

export interface HubRefreshDeps {
  getStored?: () => HubLocation | null;
  getCacheFix?: () => PreciseFix | null;
  getGrantedFix?: () => Promise<PreciseFix | null>;
  loadClustersFn?: () => Promise<Cluster[]>;
  write?: (loc: HubLocation) => void;
  resolveLabel?: typeof resolvePlaceLabel;
  now?: () => number;
}

/** One refresh attempt against the stored record. Returns the new
 * record when a rewrite happened, else null. Rules:
 *  - no stored record → nothing (the setup flows own creation);
 *  - explicit-manual record → never touched;
 *  - inferred-manual record (legacy picker signature, no explicit
 *    source) → correctable, but held to the SAME bar as an auto
 *    record: only a fresh precise fix that materially disagrees —
 *    never an IP estimate, never a prompt;
 *  - no fresh precise fix available without prompting → nothing;
 *  - fix not materially different → nothing (no churn);
 *  - otherwise rewrite coords + label via resolvePlaceLabel and the
 *    canonical write path (which also fires the live-sync events, so
 *    every mounted surface updates at once). The rewritten record is
 *    itself 'geolocation'-sourced, so a later genuine move refreshes
 *    again. */
export async function maybeRefreshHubLocation(
  deps: HubRefreshDeps = {},
): Promise<HubLocation | null> {
  const stored = (deps.getStored ?? getStoredHubLocation)();
  if (!stored) return null;
  const clusters = await (deps.loadClustersFn ?? loadClusters)().catch(
    () => getCachedClusters(),
  );
  if (classifyHubRecord(stored, clusters) === "manual") return null;
  const fix =
    (deps.getCacheFix ?? getFreshPreciseGeoFix)() ??
    (await (deps.getGrantedFix ?? getGrantedGeolocationFix)());
  if (!fix) return null;
  if (!isMateriallyDifferentLocation(stored, fix, clusters)) return null;
  const place = await (deps.resolveLabel ?? resolvePlaceLabel)(
    fix.lat,
    fix.lon,
    null,
  );
  const next: HubLocation = {
    city: place.city || stored.city,
    state: place.state || stored.state,
    lat: fix.lat,
    lon: fix.lon,
    label: place.label,
    source: "geolocation",
    setAt: (deps.now ?? Date.now)(),
  };
  (deps.write ?? setStoredHubLocation)(next);
  return next;
}

/* At most one refresh attempt per page load, shared by every mounted
 * useHubLocation instance (Hub page, homepage banner, FlightDeals). */
let hubRefreshAttempt: Promise<HubLocation | null> | null = null;

export function refreshHubLocationOnce(): Promise<HubLocation | null> {
  if (!hubRefreshAttempt) {
    hubRefreshAttempt = maybeRefreshHubLocation().catch(() => null);
  }
  return hubRefreshAttempt;
}

/**
 * The canonical hub location, persisted in localStorage. It never
 * expires. A MANUAL pick is an explicit user setting and is only
 * changed by the user; an AUTO-detected record (browser/IP) refreshes
 * itself when the device materially moves — see the refresh block
 * above.
 */
export function useHubLocation() {
  const [location, setLocationState] = useState<HubLocation | null>(getStoredHubLocation);

  const setLocation = useCallback((loc: HubLocation) => {
    setStoredHubLocation(loc);
    setLocationState(loc);
  }, []);

  /* Stay in sync with writes that bypass this hook instance — the
   * unified useUserLocation writes precise fixes through to this
   * record, and other tabs can change it too. */
  useEffect(() => {
    const reread = () => setLocationState(getStoredHubLocation());
    window.addEventListener(HUB_LOCATION_CHANGED_EVENT, reread);
    window.addEventListener("storage", reread);
    return () => {
      window.removeEventListener(HUB_LOCATION_CHANGED_EVENT, reread);
      window.removeEventListener("storage", reread);
    };
  }, []);

  /* Sticky-record refresh: an AUTO-detected record follows the device
   * when it has materially moved and a precise fix is available
   * without prompting (see maybeRefreshHubLocation). Runs once per
   * page load via the shared module guard, so the Hub page and the
   * homepage banner both get it without double geolocation calls.
   * The write goes through the canonical path, whose change event
   * re-reads every mounted instance — state is set directly here too
   * so this instance updates even if the write raced its listener. */
  useEffect(() => {
    let cancelled = false;
    void refreshHubLocationOnce().then((next) => {
      if (!cancelled && next) setLocationState(next);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  /* Self-heal legacy generic labels: a stored record whose label is
   * "Near You" / "Current location" but which carries real coords gets
   * its label re-resolved from those coords, once, and the healed
   * record is written back — so every surface that renders the label
   * (Hub chip, weekend heading, homepage banner) shows the real city
   * without the reader re-picking their location. Coords, and the
   * reader's explicit setting itself, are never touched. The healed
   * fields merge onto the FRESHEST stored record, so a refresh write
   * that landed while the label was resolving is never clobbered. */
  const healTriedRef = useRef(false);
  useEffect(() => {
    if (healTriedRef.current || !location) return;
    if (!isGenericHubLabel(location.label)) return;
    if (typeof location.lat !== "number" || typeof location.lon !== "number") return;
    healTriedRef.current = true;
    let cancelled = false;
    void resolvePlaceLabel(location.lat, location.lon, null)
      .then((place) => {
        if (cancelled || isGenericHubLabel(place.label)) return;
        const base = getStoredHubLocation() ?? location;
        setLocation({
          ...base,
          label: place.label,
          city: place.city || base.city,
          state: place.state || base.state,
        });
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [location, setLocation]);

  const clearLocation = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    setLocationState(null);
    notifyHubLocationChanged();
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
