import { describe, it, expect } from "vitest";
import {
  airlineBookingUrl,
  festivalAdvice,
  googleFlightsUrl,
  type CalendarEntry,
  type FestivalSeason,
} from "@/lib/flightDeals";

/* Airline direct-booking links (Kiran's strategy, locked 2026-10-15):
 * airline-direct is PRIMARY only where a prefilled format is VERIFIED;
 * Google Flights is the permanent compare/fallback; a carrier without
 * a verified template must return null — never a dressed-up homepage.
 *
 * Delta — verified 2026-10-15 (research §D): constructed URL returned
 * 200 with route/dates in delta.com's own search payload.
 * JetBlue — verified 2026-10-15, link-check pass #1
 * (research/airline-link-check-2026-10-15.md): the constructed URL was
 * rendered and landed on JetBlue's "Select Flights" results carrying
 * the requested route, dates and "1 Traveler" — for the live fare
 * cell JFK→DEL 2026-11-24→2026-12-16 and for JFK→LHR. */

describe("airlineBookingUrl — verified templates", () => {
  it("builds the verified Delta deep link (MM/DD/YYYY dates)", () => {
    const url = airlineBookingUrl("Delta", "SFO", "DEL", "2027-03-09", "2027-03-30");
    expect(url).toBe(
      "https://www.delta.com/flightsearch/search?action=findFlights" +
        "&tripType=ROUND_TRIP&priceSchedule=price" +
        "&originCity=SFO&destinationCity=DEL" +
        "&departureDate=03/09/2027&returnDate=03/30/2027" +
        "&paxCount=1&searchByCabin=true&cabinFareClass=MAIN&deltaOnlySearch=false",
    );
  });

  it("matches Delta by substring of the display name", () => {
    expect(
      airlineBookingUrl("Delta Air Lines", "JFK", "DEL", "2026-11-24", "2026-12-16"),
    ).toContain("delta.com/flightsearch/search");
  });

  it("builds the verified JetBlue deep link (ISO dates, adults contract)", () => {
    const url = airlineBookingUrl(
      "JetBlue Airways",
      "JFK",
      "DEL",
      "2026-11-24",
      "2026-12-16",
    );
    expect(url).toBe(
      "https://www.jetblue.com/booking/flights" +
        "?from=JFK&to=DEL&depart=2026-11-24&return=2026-12-16" +
        "&isMultiCity=false&noOfRoute=1&adults=1&children=0&infants=0" +
        "&roundTripFaresFlag=false&sharedMarket=false&usePoints=false",
    );
  });

  it("JetBlue link searches for 1 adult — never the 0-traveler variant", () => {
    const url = airlineBookingUrl("JetBlue", "JFK", "LHR", "2026-11-12", "2026-11-19");
    expect(url).toContain("adults=1");
    // The passengers=/fareType= variant parses the route but searches
    // with 0 travelers and lands on an empty results page (pass #1).
    expect(url).not.toContain("passengers=");
    expect(url).not.toContain("fareType=");
  });
});

describe("airlineBookingUrl — unverified carriers get no link", () => {
  it.each([
    "Emirates",
    "Qatar Airways",
    "Etihad Airways",
    "Singapore Airlines",
    "Air India", // session/app-state booking SPA — pass #1: no GET prefill format
    "KLM", // dated format is the partner metasearch landing (needs flight numbers)
    "Air France",
    "EVA Air",
    "Cathay Pacific",
    "Virgin Atlantic",
  ])("returns null for %s", (airline) => {
    expect(airlineBookingUrl(airline, "SFO", "DEL", "2026-11-19", "2026-12-10")).toBeNull();
  });

  it("returns null for missing airline names", () => {
    expect(airlineBookingUrl(null, "SFO", "DEL", "2026-11-19", "2026-12-10")).toBeNull();
    expect(airlineBookingUrl(undefined, "SFO", "DEL", "2026-11-19", "2026-12-10")).toBeNull();
    expect(airlineBookingUrl("", "SFO", "DEL", "2026-11-19", "2026-12-10")).toBeNull();
  });
});

describe("googleFlightsUrl — the permanent compare link", () => {
  it("builds a Google Flights search for the cell's route and dates", () => {
    const url = googleFlightsUrl("JFK", "DEL", "2026-11-24", "2026-12-16");
    expect(url).toContain("https://www.google.com/travel/flights?q=");
    expect(url).toContain(encodeURIComponent("Flights to DEL from JFK on 2026-11-24 through 2026-12-16"));
    expect(url).toContain("curr=USD");
  });
});

/* Festival advice template (holistic audit item 16, 2026-10-15): the
 * "Book N months ahead" clause rendered unconditionally, so every
 * live card carried book-by advice whose window had already passed.
 * The clause now survives only while it is still actionable. */
describe("festivalAdvice — book-ahead clause suppression", () => {
  const season = {
    note: "Long-weekend trips",
    book_by_months: 2,
  } as FestivalSeason;
  const entryOn = (dep: string) => ({ dep_date: dep }) as CalendarEntry;
  const TODAY = new Date(2026, 9, 15); // Oct 15, 2026

  it("keeps the clause while the book-by window is still open", () => {
    // Departs Mar 24, 2027; book-by deadline Jan 24, 2027 — ahead.
    expect(festivalAdvice(entryOn("2027-03-24"), season, TODAY)).toBe(
      "Long-weekend trips · Book 2 months ahead for best fares",
    );
  });

  it("suppresses the clause once the departure is inside the window", () => {
    // The audit's live Thanksgiving card: departs Nov 24, 2026,
    // book-by deadline Sep 24, 2026 — already passed on Oct 15.
    expect(festivalAdvice(entryOn("2026-11-24"), season, TODAY)).toBe(
      "Long-weekend trips",
    );
  });

  it("suppresses on the deadline day itself, keeps it the day before", () => {
    const onDeadline = new Date(2026, 8, 24); // Sep 24, 2026
    const dayBefore = new Date(2026, 8, 23);
    expect(festivalAdvice(entryOn("2026-11-24"), season, onDeadline)).toBe(
      "Long-weekend trips",
    );
    expect(festivalAdvice(entryOn("2026-11-24"), season, dayBefore)).toBe(
      "Long-weekend trips · Book 2 months ahead for best fares",
    );
  });
});
