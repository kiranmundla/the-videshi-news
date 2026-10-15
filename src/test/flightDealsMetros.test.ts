import { describe, it, expect } from "vitest";
import {
  INDIA_METROS,
  dealRouteSource,
  mergeDealRoutes,
  metroFaresForOrigin,
  type CalendarEntry,
  type FlightDealsData,
  type MetrosDealsData,
  type RouteData,
} from "@/lib/flightDeals";

/* India Metros Scroll merge logic (2026-10-15): the weekly grid
 * (flight-deals-metros.json) fills the 38 origin×metro pairs the
 * daily core doesn't cover. The rules under test:
 *  - daily data WINS over grid data for the same route;
 *  - a metro with no upcoming fare is omitted — never a placeholder;
 *  - grid fares are labelled "Checked weekly · <the cell's own date>",
 *    daily fares "Checked <the cell's own date>" (the two standard
 *    stamp formats, holistic audit item 22, 2026-10-15). */

function entry(price: number, dep = "2026-11-10", fetched = "2026-10-15"): CalendarEntry {
  return {
    date_range: `${dep} → 2026-12-01`,
    dep_date: dep,
    ret_date: "2026-12-01",
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

function route(origin: string, dest: string, entries: CalendarEntry[]): RouteData {
  return {
    origin,
    destination: dest,
    origin_metro: "Metro",
    dest_metro: "Dest",
    band: "in-3wk",
    calendar: entries,
  };
}

function dailyFile(routes: Record<string, RouteData>): FlightDealsData {
  return {
    generated_at: "2026-10-15T00:00:00Z",
    as_of: "2026-10-15",
    routes,
    festival_seasons: [],
    spec: {
      max_stops: 1,
      trip_type: "round-trip",
      pricing: "per-person",
      cabin: "economy",
      min_checked_bags: 2,
      note: "",
    },
  };
}

function metrosFile(routes: Record<string, RouteData>): MetrosDealsData {
  return {
    generated_at: "2026-10-15T00:00:00Z",
    as_of: "2026-10-14",
    cadence: "weekly",
    indicative: true,
    routes,
  };
}

describe("mergeDealRoutes", () => {
  it("daily wins over grid for the same route key", () => {
    const daily = dailyFile({ "SFO-BOM": route("SFO", "BOM", [entry(1500)]) });
    const metros = metrosFile({ "SFO-BOM": route("SFO", "BOM", [entry(1200)]) });
    const merged = mergeDealRoutes(daily, metros);
    expect(merged["SFO-BOM"].calendar[0].price_min).toBe(1500);
  });

  it("unions the key sets", () => {
    const daily = dailyFile({ "SFO-DEL": route("SFO", "DEL", [entry(1300)]) });
    const metros = metrosFile({ "SFO-CCU": route("SFO", "CCU", [entry(1400)]) });
    expect(Object.keys(mergeDealRoutes(daily, metros)).sort()).toEqual([
      "SFO-CCU",
      "SFO-DEL",
    ]);
  });

  it("tolerates a missing grid file (null)", () => {
    const daily = dailyFile({ "SFO-DEL": route("SFO", "DEL", [entry(1300)]) });
    expect(Object.keys(mergeDealRoutes(daily, null))).toEqual(["SFO-DEL"]);
    expect(mergeDealRoutes(null, null)).toEqual({});
  });
});

describe("dealRouteSource", () => {
  it("reports daily only when the daily file carries the route", () => {
    const daily = dailyFile({ "SFO-DEL": route("SFO", "DEL", [entry(1300)]) });
    expect(dealRouteSource("SFO-DEL", daily)).toBe("daily");
    expect(dealRouteSource("SFO-CCU", daily)).toBe("weekly");
  });
});

describe("metroFaresForOrigin", () => {
  it("returns canonical metro order regardless of data order", () => {
    const metros = metrosFile({
      "SFO-CCU": route("SFO", "CCU", [entry(1400)]),
      "SFO-DEL": route("SFO", "DEL", [entry(1300)]),
      "SFO-HYD": route("SFO", "HYD", [entry(1350)]),
    });
    const fares = metroFaresForOrigin(null, metros, "SFO");
    expect(fares.map((f) => f.metro)).toEqual(["DEL", "HYD", "CCU"]);
    expect(INDIA_METROS.map((m) => m.code)).toEqual([
      "DEL",
      "BOM",
      "BLR",
      "HYD",
      "CCU",
    ]);
  });

  it("omits metros with no route or no upcoming fare — no placeholders", () => {
    const metros = metrosFile({
      "SFO-BOM": route("SFO", "BOM", []),
      "SFO-BLR": route("SFO", "BLR", [entry(1200, "2020-01-10", "2020-01-01")]),
      "SFO-DEL": route("SFO", "DEL", [entry(1300)]),
    });
    const fares = metroFaresForOrigin(null, metros, "SFO");
    expect(fares.map((f) => f.metro)).toEqual(["DEL"]);
  });

  it("daily fare beats a cheaper grid fare for the same route", () => {
    const daily = dailyFile({ "SFO-BOM": route("SFO", "BOM", [entry(1500)]) });
    const metros = metrosFile({ "SFO-BOM": route("SFO", "BOM", [entry(1200)]) });
    const fares = metroFaresForOrigin(daily, metros, "SFO");
    expect(fares).toHaveLength(1);
    expect(fares[0].entry.price_min).toBe(1500);
    expect(fares[0].source).toBe("daily");
  });

  it("labels grid fares 'checked weekly' with the cell's own date", () => {
    const metros = metrosFile({
      "SFO-CCU": route("SFO", "CCU", [entry(1400, "2026-11-10", "2026-10-12")]),
    });
    const fares = metroFaresForOrigin(null, metros, "SFO");
    expect(fares[0].source).toBe("weekly");
    expect(fares[0].checkedLabel).toBe("Checked weekly · Oct 12, 2026");
  });

  it("labels daily fares with the cell's own fetch date", () => {
    const daily = dailyFile({
      "SFO-DEL": route("SFO", "DEL", [entry(1300, "2026-11-10", "2026-10-15")]),
    });
    const fares = metroFaresForOrigin(daily, null, "SFO");
    expect(fares[0].checkedLabel).toBe("Checked Oct 15, 2026");
  });

  it("picks the cheapest upcoming entry in the 3-month window", () => {
    const daily = dailyFile({
      "SFO-DEL": route("SFO", "DEL", [
        entry(1600, "2026-11-03"),
        entry(1300, "2026-12-08"),
        entry(1800, "2026-10-20"),
      ]),
    });
    const fares = metroFaresForOrigin(daily, null, "SFO");
    expect(fares[0].entry.price_min).toBe(1300);
  });

  it("returns nothing for an origin with no data", () => {
    const metros = metrosFile({ "SFO-DEL": route("SFO", "DEL", [entry(1300)]) });
    expect(metroFaresForOrigin(null, metros, "IAH")).toEqual([]);
    expect(metroFaresForOrigin(null, null, "SFO")).toEqual([]);
  });
});
