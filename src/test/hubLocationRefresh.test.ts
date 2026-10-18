import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  FALLBACK_CLUSTERS,
  classifyHubRecord,
  dismissHubLocationSuggestion,
  getAnyBrowserGeoFix,
  getDismissedHubSuggestions,
  getFreshGeolocationFix,
  getFreshPreciseGeoFix,
  getGrantedGeolocationFix,
  hasPriorGeolocationGrantEvidence,
  isHubSuggestionDismissed,
  isMateriallyDifferentLocation,
  isSoftStaleHubRecord,
  isTripwireDifferentLocation,
  maybeRefreshHubLocation,
  maybeSuggestHubLocation,
  type HubLocation,
  type IpGeoFix,
} from "@/hooks/useHubLocation";

/* Regression suite for the sticky-Hub-location fix (2026-10-14):
 * Kiran was in Fremont earlier in the day (Hub auto-detected Fremont),
 * then in Dublin — Events/Directory followed him, but Your Hub and the
 * homepage banner kept saying Fremont because the stored Hub record
 * never refreshed its coords. The rule under test: an AUTO record
 * refreshes from a fresh precise fix (never a prompt, never an IP
 * estimate) when the device materially moved; a MANUAL pick never
 * moves. Clusters are the built-in fallback table (Fremont and Dublin
 * are standalone clusters there, exactly as in the real table).
 *
 * 2026-10-15 follow-up — the bug recurred on the HOMEPAGE banner:
 * Kiran's record predates provenance tagging (no `source` field) and
 * its coords are the Fremont cluster CENTER — byte-identical to a
 * legacy picker pick, so the classifier called it "manual" and the
 * refresh skipped it forever. But /api/geo returns IP-database city
 * CENTROIDS and the cluster centers are those same centroids, so a
 * legacy IP-written record wears the picker signature without the
 * reader ever picking anything. The rule now: only an EXPLICIT
 * source of "manual" is a hard lock; an INFERRED-manual legacy
 * record is correctable by a fresh precise fix under the same
 * materiality bar as an auto record.
 *
 * Both surfaces named in the reports — the homepage banner
 * (YourHubBanner) and /your-hub (YourHubPage) — mount the same
 * useHubLocation hook, whose refresh effect runs the shared
 * refreshHubLocationOnce -> maybeRefreshHubLocation. The cases below
 * exercise that one function, so they cover the homepage path and
 * the Hub-page path alike; there is no forked copy to test. */

const CLUSTERS = FALLBACK_CLUSTERS;

/** Kiran's Fremont record: MEASURED coords (a real device fix in
 * Fremont — deliberately NOT the cluster-table center), no provenance
 * field (written before provenance existed). */
const KIRAN_FREMONT: HubLocation = {
  city: "Fremont",
  state: "CA",
  lat: 37.5525,
  lon: -121.98,
  label: "Fremont, CA",
};

/** A measured precise fix in Dublin, ~0.6 mi from the Dublin center
 * and ~11 mi from the Fremont record above. */
const DUBLIN_FIX = { lat: 37.708, lon: -121.928 };

async function runRefresh(
  stored: HubLocation | null,
  fix: { lat: number; lon: number } | null,
  viaGranted = false,
) {
  const writes: HubLocation[] = [];
  const result = await maybeRefreshHubLocation({
    getStored: () => stored,
    getCacheFix: () => (viaGranted ? null : fix),
    getGrantedFix: async () => (viaGranted ? fix : null),
    loadClustersFn: async () => CLUSTERS,
    write: (loc) => writes.push(loc),
    now: () => 1_700_000_000_000,
  });
  return { result, writes };
}

beforeEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

describe("classifyHubRecord — provenance", () => {
  it("explicit source wins: manual stays manual even off-table", () => {
    expect(
      classifyHubRecord({ ...KIRAN_FREMONT, source: "manual" }, CLUSTERS),
    ).toBe("manual");
  });

  it("explicit ip / geolocation sources are auto", () => {
    expect(
      classifyHubRecord({ ...KIRAN_FREMONT, source: "ip" }, CLUSTERS),
    ).toBe("auto");
    expect(
      classifyHubRecord({ ...KIRAN_FREMONT, source: "geolocation" }, CLUSTERS),
    ).toBe("auto");
  });

  it("legacy picker signature (cluster-center coords + cluster label) is only INFERRED manual", () => {
    const pick: HubLocation = {
      city: "Fremont",
      state: "CA",
      lat: 37.5485, // fremont-ca center, verbatim from the table —
      // also the IP-geo centroid for Fremont, which is the ambiguity
      lon: -121.9886,
      label: "Fremont, CA",
    };
    expect(classifyHubRecord(pick, CLUSTERS)).toBe("inferred-manual");
  });

  it("legacy member signature (member coords + cluster label) is only INFERRED manual", () => {
    const pick: HubLocation = {
      city: "San Ramon",
      state: "CA",
      lat: 37.7799, // dublin-ca member coords, verbatim from the table
      lon: -121.978,
      label: "Dublin, CA",
    };
    expect(classifyHubRecord(pick, CLUSTERS)).toBe("inferred-manual");
  });

  it("legacy measured coords (Kiran's Fremont record) are auto", () => {
    expect(classifyHubRecord(KIRAN_FREMONT, CLUSTERS)).toBe("auto");
  });

  it("table coords under a mismatched label are not a picker signature", () => {
    const odd: HubLocation = {
      city: "San Jose",
      state: "CA",
      lat: 37.5485,
      lon: -121.9886,
      label: "San Jose, CA",
    };
    expect(classifyHubRecord(odd, CLUSTERS)).toBe("auto");
  });
});

describe("isMateriallyDifferentLocation", () => {
  it("Fremont -> Dublin is material (different cluster, >5 mi)", () => {
    expect(isMateriallyDifferentLocation(KIRAN_FREMONT, DUBLIN_FIX, CLUSTERS)).toBe(true);
  });

  it("~1 mi within the same cluster is not material", () => {
    const nearFix = { lat: 37.567, lon: -121.98 }; // ~1 mi north of the stored fix
    expect(isMateriallyDifferentLocation(KIRAN_FREMONT, nearFix, CLUSTERS)).toBe(false);
  });
});

describe("maybeRefreshHubLocation", () => {
  it("(a) Kiran's case: stored auto Fremont + fresh Dublin fix -> Hub becomes Dublin", async () => {
    const { result, writes } = await runRefresh(KIRAN_FREMONT, DUBLIN_FIX);
    expect(writes).toHaveLength(1);
    expect(result).not.toBeNull();
    expect(result!.label).toBe("Dublin, CA");
    expect(result!.city).toBe("Dublin");
    expect(result!.state).toBe("CA");
    expect(result!.lat).toBe(DUBLIN_FIX.lat);
    expect(result!.lon).toBe(DUBLIN_FIX.lon);
    expect(result!.source).toBe("geolocation");
    expect(result!.setAt).toBe(1_700_000_000_000);
  });

  it("(a2) same refresh when the fix arrives via the permission-granted path", async () => {
    const { result, writes } = await runRefresh(KIRAN_FREMONT, DUBLIN_FIX, true);
    expect(writes).toHaveLength(1);
    expect(result!.label).toBe("Dublin, CA");
  });

  it("(b) manual pick (Edison, NJ) + Dublin fix -> unchanged", async () => {
    const manual: HubLocation = {
      city: "Edison",
      state: "NJ",
      lat: 40.5187,
      lon: -74.4121,
      label: "Edison, NJ",
      source: "manual",
    };
    const { result, writes } = await runRefresh(manual, DUBLIN_FIX);
    expect(result).toBeNull();
    expect(writes).toHaveLength(0);
  });

  it("(b2) legacy inferred-manual Fremont + Dublin fix -> corrected to Dublin (the 2026-10-15 recurrence)", async () => {
    // Kiran's stuck record: no source field, Fremont cluster-center
    // coords + cluster label — the exact shape a legacy IP-written
    // record takes, misread as a deliberate pick until 2026-10-15.
    const stuck: HubLocation = {
      city: "Fremont",
      state: "CA",
      lat: 37.5485,
      lon: -121.9886,
      label: "Fremont, CA",
    };
    const { result, writes } = await runRefresh(stuck, DUBLIN_FIX);
    expect(writes).toHaveLength(1);
    expect(result).not.toBeNull();
    expect(result!.label).toBe("Dublin, CA");
    expect(result!.city).toBe("Dublin");
    expect(result!.lat).toBe(DUBLIN_FIX.lat);
    expect(result!.lon).toBe(DUBLIN_FIX.lon);
    // The correction stamps an explicit provenance, so the record's
    // class is unambiguous from now on.
    expect(result!.source).toBe("geolocation");
  });

  it("(b3) EXPLICIT manual Fremont (picker-written, source tagged) + Dublin fix -> stays Fremont", async () => {
    const manual: HubLocation = {
      city: "Fremont",
      state: "CA",
      lat: 37.5485, // same coords as (b2) — the explicit source is the difference
      lon: -121.9886,
      label: "Fremont, CA",
      source: "manual",
    };
    const { result, writes } = await runRefresh(manual, DUBLIN_FIX);
    expect(result).toBeNull();
    expect(writes).toHaveLength(0);
  });

  it("(b4) inferred-manual Fremont + NO precise fix -> unchanged (an inference alone never moves a record)", async () => {
    const stuck: HubLocation = {
      city: "Fremont",
      state: "CA",
      lat: 37.5485,
      lon: -121.9886,
      label: "Fremont, CA",
    };
    const { result, writes } = await runRefresh(stuck, null);
    expect(result).toBeNull();
    expect(writes).toHaveLength(0);
  });

  it("(b5) inferred-manual Fremont + fix ~1 mi away, same cluster -> no churn", async () => {
    const stuck: HubLocation = {
      city: "Fremont",
      state: "CA",
      lat: 37.5485,
      lon: -121.9886,
      label: "Fremont, CA",
    };
    const nearFix = { lat: 37.562, lon: -121.9886 }; // ~0.9 mi north, still Fremont
    const { result, writes } = await runRefresh(stuck, nearFix);
    expect(result).toBeNull();
    expect(writes).toHaveLength(0);
  });

  it("(c) no fresh fix available -> unchanged", async () => {
    const { result, writes } = await runRefresh(KIRAN_FREMONT, null);
    expect(result).toBeNull();
    expect(writes).toHaveLength(0);
  });

  it("(d) fresh fix ~1 mi away, same cluster -> no churn", async () => {
    const nearFix = { lat: 37.567, lon: -121.98 };
    const { result, writes } = await runRefresh(KIRAN_FREMONT, nearFix);
    expect(result).toBeNull();
    expect(writes).toHaveLength(0);
  });

  it("no stored record -> nothing (setup flows own creation)", async () => {
    const { result, writes } = await runRefresh(null, DUBLIN_FIX);
    expect(result).toBeNull();
    expect(writes).toHaveLength(0);
  });
});

describe("getFreshPreciseGeoFix — only precise browser fixes count", () => {
  const seedCache = (loc: unknown, ageMs = 0) =>
    localStorage.setItem(
      "videshi_user_geo",
      JSON.stringify({ ts: Date.now() - ageMs, loc }),
    );

  it("returns a fresh browser fix", () => {
    seedCache({ latitude: 37.708, longitude: -121.928, source: "browser" });
    expect(getFreshPreciseGeoFix()).toEqual({ lat: 37.708, lon: -121.928 });
  });

  it("an IP estimate never counts, however fresh", () => {
    seedCache({ latitude: 37.708, longitude: -121.928, source: "ip" });
    expect(getFreshPreciseGeoFix()).toBeNull();
  });

  it("a stale browser fix (>1 h) does not count", () => {
    seedCache(
      { latitude: 37.708, longitude: -121.928, source: "browser" },
      2 * 60 * 60 * 1000,
    );
    expect(getFreshPreciseGeoFix()).toBeNull();
  });

  it("empty cache -> null", () => {
    expect(getFreshPreciseGeoFix()).toBeNull();
  });
});

describe("getGrantedGeolocationFix — never prompts", () => {
  it("permission 'prompt' -> null, and getCurrentPosition is never called", async () => {
    const getCurrentPosition = vi.fn();
    Object.defineProperty(window.navigator, "permissions", {
      configurable: true,
      value: {
        query: async () => ({ state: "prompt" }) as PermissionStatus,
      },
    });
    Object.defineProperty(window.navigator, "geolocation", {
      configurable: true,
      value: { getCurrentPosition },
    });
    await expect(getGrantedGeolocationFix()).resolves.toBeNull();
    expect(getCurrentPosition).not.toHaveBeenCalled();
  });

  it("permission 'granted' -> returns the position", async () => {
    Object.defineProperty(window.navigator, "permissions", {
      configurable: true,
      value: {
        query: async () => ({ state: "granted" }) as PermissionStatus,
      },
    });
    Object.defineProperty(window.navigator, "geolocation", {
      configurable: true,
      value: {
        getCurrentPosition: (ok: PositionCallback) =>
          ok({
            coords: { latitude: 37.708, longitude: -121.928 },
          } as GeolocationPosition),
      },
    });
    await expect(getGrantedGeolocationFix()).resolves.toEqual({
      lat: 37.708,
      lon: -121.928,
    });
  });
});

describe("getFreshGeolocationFix — never a stale cached position", () => {
  it("requests maximumAge 0 and resolves the fresh position", async () => {
    let seenOptions: PositionOptions | undefined;
    Object.defineProperty(window.navigator, "geolocation", {
      configurable: true,
      value: {
        getCurrentPosition: (
          ok: PositionCallback,
          _err: PositionErrorCallback,
          options?: PositionOptions,
        ) => {
          seenOptions = options;
          ok({
            coords: { latitude: 37.702, longitude: -121.935 },
          } as GeolocationPosition);
        },
      },
    });
    await expect(getFreshGeolocationFix()).resolves.toEqual({
      lat: 37.702,
      lon: -121.935,
    });
    /* The regression guard for the 2026-10-16 Fremont latch: an
       auto-detect that accepts a cached position (maximumAge
       300000) can pin "near you" to a city the reader has left. */
    expect(seenOptions?.maximumAge).toBe(0);
  });

  it("resolves null when the browser errors (denied / timeout)", async () => {
    Object.defineProperty(window.navigator, "geolocation", {
      configurable: true,
      value: {
        getCurrentPosition: (
          _ok: PositionCallback,
          err: PositionErrorCallback,
        ) => err({ code: 3 } as GeolocationPositionError),
      },
    });
    await expect(getFreshGeolocationFix()).resolves.toBeNull();
  });
});

/* ================================================================== */
/* 2026-10-18 — the smart refresh. Kiran, on his phone: the site      */
/* still showed the previous location. Three gaps closed:             */
/*  1. iOS Safari has no reliable Permissions API for geolocation,    */
/*     so the granted-fix path could never fire on iPhone — it now    */
/*     falls back to prior-grant EVIDENCE (a browser fix in the geo   */
/*     cache, however old) and stays silent without it.               */
/*  2. An IP tripwire SUGGESTS (never writes) a switch when the       */
/*     stored place looks materially wrong and the record is not a    */
/*     manual pick; dismissed cities never nag twice.                 */
/*  3. Auto records older than 7 days are soft-stale and revalidate   */
/*     on the next landing; a same-metro confirmation restarts their  */
/*     clock by refreshing setAt only.                                */
/* ================================================================== */

const DAY_MS = 24 * 60 * 60 * 1000;
const NOW = 1_700_000_000_000;

describe("prior-grant evidence — a browser fix in the geo cache, any age", () => {
  const seedGeoCache = (loc: unknown, ageMs = 0) =>
    localStorage.setItem(
      "videshi_user_geo",
      JSON.stringify({ ts: Date.now() - ageMs, loc }),
    );

  it("a fresh browser fix is evidence", () => {
    seedGeoCache({ latitude: 37.708, longitude: -121.928, source: "browser" });
    expect(hasPriorGeolocationGrantEvidence()).toBe(true);
    expect(getAnyBrowserGeoFix()).toEqual({ lat: 37.708, lon: -121.928 });
  });

  it("an EXPIRED browser fix is still evidence (provenance, not position)", () => {
    seedGeoCache(
      { latitude: 37.708, longitude: -121.928, source: "browser" },
      30 * DAY_MS,
    );
    expect(hasPriorGeolocationGrantEvidence()).toBe(true);
  });

  it("an IP fix is NOT evidence — it never involved a grant", () => {
    seedGeoCache({ latitude: 37.708, longitude: -121.928, source: "ip" });
    expect(hasPriorGeolocationGrantEvidence()).toBe(false);
    expect(getAnyBrowserGeoFix()).toBeNull();
  });

  it("empty / corrupt cache -> no evidence", () => {
    expect(hasPriorGeolocationGrantEvidence()).toBe(false);
    localStorage.setItem("videshi_user_geo", "{not json");
    expect(hasPriorGeolocationGrantEvidence()).toBe(false);
  });
});

describe("getGrantedGeolocationFix — the iOS path (no Permissions API)", () => {
  const seedBrowserCache = () =>
    localStorage.setItem(
      "videshi_user_geo",
      JSON.stringify({
        ts: Date.now() - 30 * DAY_MS, // long expired — evidence only
        loc: { latitude: 37.5525, longitude: -121.98, source: "browser" },
      }),
    );
  const noPermissionsApi = () =>
    Object.defineProperty(window.navigator, "permissions", {
      configurable: true,
      value: undefined,
    });
  const mockPosition = (lat: number, lon: number) => {
    const getCurrentPosition = vi.fn((ok: PositionCallback) =>
      ok({ coords: { latitude: lat, longitude: lon } } as GeolocationPosition),
    );
    Object.defineProperty(window.navigator, "geolocation", {
      configurable: true,
      value: { getCurrentPosition },
    });
    return getCurrentPosition;
  };

  it("prior-grant evidence -> silent GPS attempt WITHOUT the Permissions API", async () => {
    seedBrowserCache();
    noPermissionsApi();
    const getCurrentPosition = mockPosition(37.708, -121.928);
    await expect(getGrantedGeolocationFix()).resolves.toEqual({
      lat: 37.708,
      lon: -121.928,
    });
    expect(getCurrentPosition).toHaveBeenCalledTimes(1);
  });

  it("no evidence -> null, and getCurrentPosition is NEVER called (it could prompt)", async () => {
    noPermissionsApi();
    const getCurrentPosition = mockPosition(37.708, -121.928);
    await expect(getGrantedGeolocationFix()).resolves.toBeNull();
    expect(getCurrentPosition).not.toHaveBeenCalled();
  });

  it("an IP-only cache is not evidence -> silent, no GPS attempt", async () => {
    localStorage.setItem(
      "videshi_user_geo",
      JSON.stringify({
        ts: Date.now(),
        loc: { latitude: 37.5525, longitude: -121.98, source: "ip" },
      }),
    );
    noPermissionsApi();
    const getCurrentPosition = mockPosition(37.708, -121.928);
    await expect(getGrantedGeolocationFix()).resolves.toBeNull();
    expect(getCurrentPosition).not.toHaveBeenCalled();
  });

  it("an explicit 'denied' beats cache evidence — a revoked grant is not retried", async () => {
    seedBrowserCache();
    Object.defineProperty(window.navigator, "permissions", {
      configurable: true,
      value: {
        query: async () => ({ state: "denied" }) as PermissionStatus,
      },
    });
    const getCurrentPosition = mockPosition(37.708, -121.928);
    await expect(getGrantedGeolocationFix()).resolves.toBeNull();
    expect(getCurrentPosition).not.toHaveBeenCalled();
  });
});

describe("soft-stale auto records — 7-day revalidation", () => {
  const STALE_AUTO: HubLocation = {
    ...KIRAN_FREMONT,
    source: "geolocation",
    setAt: NOW - 8 * DAY_MS,
  };
  const NEAR_FIX = { lat: 37.567, lon: -121.98 }; // ~1 mi, same cluster

  it("isSoftStaleHubRecord: >7 days true; fresh false; no setAt false (age unprovable)", () => {
    expect(isSoftStaleHubRecord(STALE_AUTO, NOW)).toBe(true);
    expect(
      isSoftStaleHubRecord({ ...STALE_AUTO, setAt: NOW - DAY_MS }, NOW),
    ).toBe(false);
    expect(
      isSoftStaleHubRecord({ ...STALE_AUTO, setAt: NOW - 7 * DAY_MS }, NOW),
    ).toBe(false);
    expect(isSoftStaleHubRecord(KIRAN_FREMONT, NOW)).toBe(false);
  });

  it("same-metro revalidation quietly refreshes setAt — place, coords, source untouched", async () => {
    const writes: HubLocation[] = [];
    const result = await maybeRefreshHubLocation({
      getStored: () => STALE_AUTO,
      getCacheFix: () => NEAR_FIX,
      getGrantedFix: async () => NEAR_FIX,
      loadClustersFn: async () => CLUSTERS,
      write: (loc) => writes.push(loc),
      now: () => NOW,
    });
    expect(writes).toHaveLength(1);
    expect(result).not.toBeNull();
    expect(result!.setAt).toBe(NOW);
    expect(result!.label).toBe("Fremont, CA");
    expect(result!.lat).toBe(KIRAN_FREMONT.lat);
    expect(result!.lon).toBe(KIRAN_FREMONT.lon);
    expect(result!.source).toBe("geolocation");
  });

  it("soft-stale revalidation runs the granted path EVEN WITH a fresh cache fix, and prefers it", async () => {
    const writes: HubLocation[] = [];
    const result = await maybeRefreshHubLocation({
      getStored: () => STALE_AUTO,
      getCacheFix: () => NEAR_FIX, // cache says "still Fremont"
      getGrantedFix: async () => DUBLIN_FIX, // fresh granted fix says Dublin
      loadClustersFn: async () => CLUSTERS,
      write: (loc) => writes.push(loc),
      now: () => NOW,
    });
    expect(writes).toHaveLength(1);
    expect(result!.label).toBe("Dublin, CA");
    expect(result!.setAt).toBe(NOW);
  });

  it("fresh auto record: the cache fix short-circuits — granted path never consulted, no touch", async () => {
    const freshAuto: HubLocation = {
      ...KIRAN_FREMONT,
      source: "geolocation",
      setAt: NOW - DAY_MS,
    };
    const granted = vi.fn(async () => DUBLIN_FIX);
    const writes: HubLocation[] = [];
    const result = await maybeRefreshHubLocation({
      getStored: () => freshAuto,
      getCacheFix: () => NEAR_FIX,
      getGrantedFix: granted,
      loadClustersFn: async () => CLUSTERS,
      write: (loc) => writes.push(loc),
      now: () => NOW,
    });
    expect(result).toBeNull();
    expect(writes).toHaveLength(0);
    expect(granted).not.toHaveBeenCalled();
  });

  it("soft-stale but NO fix obtainable -> nothing (the clock never restarts on faith)", async () => {
    const { result, writes } = await runRefresh(
      { ...STALE_AUTO },
      null,
    );
    expect(result).toBeNull();
    expect(writes).toHaveLength(0);
  });

  it("manual records never revalidate, however old", async () => {
    const oldManual: HubLocation = {
      ...KIRAN_FREMONT,
      source: "manual",
      setAt: NOW - 30 * DAY_MS,
    };
    const { result, writes } = await runRefresh(oldManual, NEAR_FIX);
    expect(result).toBeNull();
    expect(writes).toHaveLength(0);
  });
});

/** IP-geo fixes, shaped like /api/geo responses for those networks. */
const IP_CHICAGO: IpGeoFix = {
  lat: 41.8781,
  lon: -87.6298,
  city: "Chicago",
  region: "IL",
};
const IP_LOS_ANGELES: IpGeoFix = {
  lat: 34.0522,
  lon: -118.2437,
  city: "Los Angeles",
  region: "CA",
};
const IP_DUBLIN_CA: IpGeoFix = {
  lat: 37.7022,
  lon: -121.9358,
  city: "Dublin",
  region: "CA",
};

describe("isTripwireDifferentLocation — the suggestion bar", () => {
  it("a different state fires (Fremont, CA vs Chicago, IL)", () => {
    expect(isTripwireDifferentLocation(KIRAN_FREMONT, IP_CHICAGO)).toBe(true);
  });

  it("same state but >100 miles fires (Fremont vs Los Angeles)", () => {
    expect(isTripwireDifferentLocation(KIRAN_FREMONT, IP_LOS_ANGELES)).toBe(
      true,
    );
  });

  it("same-metro IP wobble does NOT fire (Fremont vs Dublin, ~11 mi, same state)", () => {
    expect(isTripwireDifferentLocation(KIRAN_FREMONT, IP_DUBLIN_CA)).toBe(
      false,
    );
  });

  it("a full region NAME never false-fires the state test against a stored code", () => {
    expect(
      isTripwireDifferentLocation(KIRAN_FREMONT, {
        ...IP_DUBLIN_CA,
        region: "California",
      }),
    ).toBe(false);
  });
});

describe("maybeSuggestHubLocation — the IP tripwire", () => {
  const runSuggest = (
    stored: HubLocation | null,
    ip: IpGeoFix | null = IP_CHICAGO,
    extra: Partial<Parameters<typeof maybeSuggestHubLocation>[0]> = {},
  ) =>
    maybeSuggestHubLocation({
      getStored: () => stored,
      loadClustersFn: async () => CLUSTERS,
      fetchIpGeo: async () => ip,
      now: () => NOW,
      ...extra,
    });

  it("auto record + different-state IP -> a suggestion (never a write)", async () => {
    const s = await runSuggest(KIRAN_FREMONT);
    expect(s).not.toBeNull();
    expect(s!.key).toBe("Chicago, IL");
    expect(s!.storedLabel).toBe("Fremont, CA");
    // The record that "Use this" would write: resolved label/coords,
    // IP-sourced so the precise refresh can still refine it later.
    expect(s!.location.label).toBe("Chicago, IL");
    expect(s!.location.city).toBe("Chicago");
    expect(s!.location.state).toBe("IL");
    expect(s!.location.lat).toBe(IP_CHICAGO.lat);
    expect(s!.location.lon).toBe(IP_CHICAGO.lon);
    expect(s!.location.source).toBe("ip");
    expect(s!.location.setAt).toBe(NOW);
  });

  it("inferred-manual record (the legacy stuck shape) + different-state IP -> suggestion fires", async () => {
    const stuck: HubLocation = {
      city: "Fremont",
      state: "CA",
      lat: 37.5485,
      lon: -121.9886,
      label: "Fremont, CA",
    };
    const s = await runSuggest(stuck);
    expect(s).not.toBeNull();
    expect(s!.key).toBe("Chicago, IL");
  });

  it("manual record -> NEVER, and the IP lookup is not even made", async () => {
    const fetchIpGeo = vi.fn(async () => IP_CHICAGO);
    const s = await maybeSuggestHubLocation({
      getStored: () => ({ ...KIRAN_FREMONT, source: "manual" }),
      loadClustersFn: async () => CLUSTERS,
      fetchIpGeo,
      now: () => NOW,
    });
    expect(s).toBeNull();
    expect(fetchIpGeo).not.toHaveBeenCalled();
  });

  it("auto record + same-metro IP -> no suggestion (IP wobble is not travel)", async () => {
    const s = await runSuggest(KIRAN_FREMONT, IP_DUBLIN_CA);
    expect(s).toBeNull();
  });

  it("a city the reader already dismissed never nags again", async () => {
    const s = await runSuggest(KIRAN_FREMONT, IP_CHICAGO, {
      isDismissed: (key) => key === "Chicago, IL",
    });
    expect(s).toBeNull();
  });

  it("no stored record -> nothing (setup flows own creation)", async () => {
    expect(await runSuggest(null)).toBeNull();
  });

  it("no IP fix -> nothing", async () => {
    expect(await runSuggest(KIRAN_FREMONT, null)).toBeNull();
  });
});

describe("suggestion dismissals — persisted per city", () => {
  it("dismiss -> suppressed; other cities unaffected; no duplicates", () => {
    expect(isHubSuggestionDismissed("Chicago, IL")).toBe(false);
    dismissHubLocationSuggestion("Chicago, IL");
    expect(isHubSuggestionDismissed("Chicago, IL")).toBe(true);
    expect(isHubSuggestionDismissed("Austin, TX")).toBe(false);
    dismissHubLocationSuggestion("Chicago, IL");
    expect(getDismissedHubSuggestions()).toEqual(["Chicago, IL"]);
  });

  it("a persisted dismissal suppresses the suggestion through the default path", async () => {
    dismissHubLocationSuggestion("Chicago, IL");
    const s = await maybeSuggestHubLocation({
      getStored: () => KIRAN_FREMONT,
      loadClustersFn: async () => CLUSTERS,
      fetchIpGeo: async () => IP_CHICAGO,
      now: () => NOW,
    });
    expect(s).toBeNull();
  });
});
