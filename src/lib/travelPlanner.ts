/* ------------------------------------------------------------------ */
/* Travel planner data — holiday windows, destinations by month,    */
/* in-India add-ons, per-destination seasonality facts.               */
/* Source: public/data/travel-by-month.json, generated from the       */
/* curated source in scripts/build-travel-data.mjs.                   */
/* ------------------------------------------------------------------ */

export type HolidayWindow = {
  id: string;
  name: string;
  emoji: string;
  start: string;
  end: string;
  peak: boolean;
  book_by: string;
  note: string;
};

export type DestinationFact = {
  cheapest_month: string;
  best_season: string;
};

export type MonthPick = {
  key: string;
  group: "india" | "usa" | "international";
  why: string;
};

export type MonthPicks = {
  month: string;
  label: string;
  picks: MonthPick[];
};

export type InIndiaPick = {
  key: string;
  blurb: string;
};

export type TravelPlannerData = {
  generated_at: string;
  holiday_windows: HolidayWindow[];
  destination_facts: Record<string, DestinationFact>;
  months: MonthPicks[];
  in_india: InIndiaPick[];
};

export const GROUP_LABELS: Record<MonthPick["group"], string> = {
  india: "In India",
  usa: "USA",
  international: "International",
};

let plannerCache: Promise<TravelPlannerData | null> | null = null;
export function loadTravelPlanner(): Promise<TravelPlannerData | null> {
  if (!plannerCache) {
    plannerCache = fetch("/data/travel-by-month.json")
      .then((r) => (r.ok ? r.json() : null))
      .catch(() => null);
  }
  return plannerCache;
}

/** Next holiday window that hasn't ended yet. */
export function nextHolidayWindow(
  data: TravelPlannerData,
  from: string,
): HolidayWindow | null {
  return data.holiday_windows.find((w) => w.end >= from) ?? null;
}
