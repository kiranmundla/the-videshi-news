import { describe, it, expect } from "vitest";
import {
  cheapestOrigin,
  destinationFareClass,
  representativeWindow,
  resolveIndiaFares,
  resolveIntlFares,
  resolveModuleOrigin,
} from "@/lib/destinationFares";
import {
  FARES_ORIGIN_STORAGE_KEY,
  type CalendarEntry,
  type FlightDealsData,
  type IntlDealsData,
  type MetrosDealsData,
  type RouteData,
} from "@/lib/flightDeals";

/* Destination fare module class resolution (Phase 2, 2026-10-15).
 * The rules under test:
 *  - the class is a property of the slug: karnataka → A (own metro
 *    BLR), the intl-matrix slugs → B, everything else → fallback;
 *  - class A reads ONLY the destination's own metro — a cheap Delhi
 *    fare in the same file must never surface on Karnataka's page,
 *    and Rajasthan/Goa resolve to zero fares (own-metro rule);
 *  - daily data wins over the weekly grid for the same route, and
 *    each route carries its own honest stamp ("Checked …" daily,
 *    "Checked weekly · …" weekly) from the winning cell's date;
 *  - class B matches on the destination airport (and slug when the
 *    route carries one);
 *  - the default origin is stored-pref → Hub-detected → cheapest. */

function entry(
  price: number,
  dep = "2026-11-10",
  ret = "2026-12-01",
  fetched = "2026-10-15",
): CalendarEntry {
  return {
    date_range: `${dep} → ${ret}`,
    dep_date: dep,
    ret_date: ret,
    price_min: price,
    price_max: price + 300,
    cheapest_airline: "Test Air",
    num_samples: 4,
    year: 2026,
    month: 11,
    duration_days: 21,
    band: "in-3wk",
    fetched_as_of: fetched,
  };
}

function route(
  origin: string,
  dest: string,
  entries: CalendarEntry[],
  slug?: string,
): RouteData {
  return {
    origin,
    destination: dest,
    origin_metro: "",
    dest_metro: "",
    calendar: entries,
    ...(slug ? { destination_slug: slug } : {}),
  };
}

const SPEC = {
  max_stops: 1,
  trip_type: "round_trip",
  pricing: "per_person",
  cabin: "economy",
  min_checked_bags: 2,
  note: "",
};

function dailyData(routes: Record<string, RouteData>): FlightDealsData {
  return {
    generated_at: "2026-10-15T00:00:00Z",
    as_of: "2026-10-15",
    routes,
    festival_seasons: [],
    spec: SPEC,
  };
}

function metrosData(routes: Record<string, RouteData>): MetrosDealsData {
  return { generated_at: "2026-10-15T00:00:00Z", as_of: "2026-10-15", routes };
}

function intlData(routes: Record<string, RouteData>): IntlDealsData {
  return { generated_at: "2026-10-15T00:00:00Z", as_of: "2026-10-15", routes };
}

describe("destinationFareClass", () => {
  it("classifies by slug alone", () => {
    expect(destinationFareClass("karnataka")).toBe("A");
    expect(destinationFareClass("australia")).toBe("B");
    expect(destinationFareClass("bali")).toBe("B");
    expect(destinationFareClass("hawaii")).toBe("B");
    expect(destinationFareClass("goa")).toBe("fallback");
    expect(destinationFareClass("kerala")).toBe("fallback");
    expect(destinationFareClass("rajasthan")).toBe("fallback");
    expect(destinationFareClass("japan")).toBe("fallback");
  });
});

describe("resolveIndiaFares (class A, own-metro rule)", () => {
  const daily = dailyData({
    "SFO-BLR": route("SFO", "BLR", [entry(1243, "2026-10-21", "2026-11-12")]),
    "SFO-DEL": route("SFO", "DEL", [entry(999, "2026-10-21", "2026-11-12")]),
  });
  const metros = metrosData({
    "SFO-BLR": route("SFO", "BLR", [entry(1500)]),
    "LAX-BLR": route("LAX", "BLR", [entry(1339, "2026-10-21", "2026-11-12")]),
  });

  it("returns only the destination's own metro, daily winning", () => {
    const fares = resolveIndiaFares("karnataka", daily, metros);
    expect(fares.map((f) => f.routeKey)).toEqual(["LAX-BLR", "SFO-BLR"]);
    const sfo = fares.find((f) => f.origin === "SFO")!;
    expect(sfo.cheapest.price_min).toBe(1243);
    expect(sfo.source).toBe("daily");
    expect(sfo.checkedLabel).toBe("Checked Oct 15, 2026");
    const lax = fares.find((f) => f.origin === "LAX")!;
    expect(lax.cheapest.price_min).toBe(1339);
    expect(lax.source).toBe("weekly");
    expect(lax.checkedLabel).toBe("Checked weekly · Oct 15, 2026");
  });

  it("never borrows another metro's fare for other India guides", () => {
    expect(resolveIndiaFares("rajasthan", daily, metros)).toEqual([]);
    expect(resolveIndiaFares("goa", daily, metros)).toEqual([]);
    expect(resolveIndiaFares("kerala", daily, metros)).toEqual([]);
  });

  it("degrades to zero fares on missing data", () => {
    expect(resolveIndiaFares("karnataka", null, null)).toEqual([]);
  });
});

describe("resolveIntlFares (class B)", () => {
  const intl = intlData({
    "SFO-SYD": route("SFO", "SYD", [entry(1132, "2026-10-21", "2026-10-27")], "australia"),
    "JFK-SYD": route("JFK", "SYD", [entry(1500, "2026-11-24", "2026-12-02")], "australia"),
    "SFO-HNL": route("SFO", "HNL", [entry(400, "2026-11-10", "2026-11-17")], "hawaii"),
    "LAX-AKL": route("LAX", "AKL", [entry(900, "2026-11-10", "2026-11-17")], "australia"),
  });

  it("matches the destination's airport only, weekly stamps", () => {
    const fares = resolveIntlFares("australia", intl);
    expect(fares.map((f) => f.routeKey)).toEqual(["JFK-SYD", "SFO-SYD"]);
    expect(fares[0].source).toBe("weekly");
    expect(fares[0].checkedLabel).toBe("Checked weekly · Oct 15, 2026");
  });

  it("resolves zero fares before the destination's routes land", () => {
    expect(resolveIntlFares("bali", intl)).toEqual([]);
    expect(resolveIntlFares("australia", null)).toEqual([]);
  });
});

describe("cheapestOrigin", () => {
  it("picks the lowest cheapest-fare, ties broken A–Z", () => {
    const fares = resolveIndiaFares(
      "karnataka",
      dailyData({
        "SFO-BLR": route("SFO", "BLR", [entry(1243)]),
        "LAX-BLR": route("LAX", "BLR", [entry(1100)]),
        "JFK-BLR": route("JFK", "BLR", [entry(1100)]),
      }),
      null,
    );
    expect(cheapestOrigin(fares)).toBe("JFK");
    expect(cheapestOrigin([])).toBeNull();
  });
});

describe("resolveModuleOrigin", () => {
  const clear = () => {
    localStorage.removeItem(FARES_ORIGIN_STORAGE_KEY);
    localStorage.removeItem("videshi-user-location");
  };

  it("stored preference wins when it has fares here", () => {
    clear();
    localStorage.setItem(FARES_ORIGIN_STORAGE_KEY, "LAX");
    expect(resolveModuleOrigin(["SFO", "LAX"], "SFO")).toEqual({
      origin: "LAX",
      reason: "stored",
    });
  });

  it("falls through when the stored origin has no route here", () => {
    clear();
    localStorage.setItem(FARES_ORIGIN_STORAGE_KEY, "BOS");
    expect(resolveModuleOrigin(["SFO", "LAX"], "LAX")).toEqual({
      origin: "LAX",
      reason: "cheapest",
    });
  });

  it("uses the Hub-location origin when detected", () => {
    clear();
    localStorage.setItem(
      "videshi-user-location",
      JSON.stringify({
        city: "Dublin",
        state: "CA",
        label: "Dublin, CA",
        lat: 37.7022,
        lon: -121.9358,
        source: "manual",
        setAt: Date.now(),
      }),
    );
    expect(resolveModuleOrigin(["SFO", "JFK"], "JFK")).toEqual({
      origin: "SFO",
      reason: "hub",
    });
  });

  it("defaults to the cheapest origin and handles the empty case", () => {
    clear();
    expect(resolveModuleOrigin(["JFK", "LAX"], "LAX")).toEqual({
      origin: "LAX",
      reason: "cheapest",
    });
    expect(resolveModuleOrigin([], null)).toBeNull();
    clear();
  });
});

describe("representativeWindow (fallback search link)", () => {
  it("anchors on the cheapest range's first month, next occurrence", () => {
    expect(representativeWindow("Jun – Sep (monsoon)", true, "2026-10-15")).toEqual({
      dep: "2027-06-10",
      ret: "2027-06-30",
    });
    expect(representativeWindow("Nov – Mar (rainy season)", false, "2026-10-15")).toEqual({
      dep: "2026-11-10",
      ret: "2026-11-17",
    });
  });

  it("uses India trip length for India destinations, a week elsewhere", () => {
    expect(representativeWindow("Jan – Feb (cold)", true, "2026-10-15").ret).toBe("2027-01-30");
    expect(representativeWindow("Jan – Feb (cold)", false, "2026-10-15").ret).toBe("2027-01-17");
  });

  it("degrades to ~2 months out on an unparseable label", () => {
    expect(representativeWindow(null, false, "2026-10-15")).toEqual({
      dep: "2026-12-14",
      ret: "2026-12-21",
    });
  });
});
