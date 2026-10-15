# Price-Comparison Feasibility: "Which Channel Is Cheapest?" per Route/Itinerary

**Date:** 2026-10-14 · **Question from Kiran:** show, per route/itinerary, which booking
channel is cheapest — live prices + booking links across airline-direct, Google Flights
results, OTAs and consolidators. **Scope:** evidence only, no build, no signups.

## Bottom line

- **Exactly one self-serve API available today returns true per-channel prices with
  booking links: SerpApi's Google Flights API.** Its `booking_options` call returns, for
  one selected itinerary, each seller Google Flights lists (airline-direct, Expedia,
  other OTAs) with that seller's price and a click-out booking link. Cost is per search,
  and a round-trip channel comparison costs up to **3 searches per itinerary**, which
  makes a full-matrix daily refresh expensive (see cost model).
- **Material risk:** Google is actively suing SerpApi (filed Dec 2025) over scraping
  search results and circumventing its SearchGuard anti-bot system. SerpApi counters
  with a First Amendment position and bundles a "U.S. Legal Shield" into Production
  plans and up. Building the channel-comparison feature on SerpApi means building on a
  supplier whose core data source is under litigation — viable, but it should be an
  informed decision, and the architecture should keep the Duffel calendar as the
  fallback that doesn't depend on it.
- **Duffel (already integrated) cannot do channel comparison.** Duffel is itself a
  single seller (merchant of record via its own accreditation) — one price per offer,
  no "airline vs OTA" spread. It stays the right engine for the fare calendar/ranges.
- **Amadeus Self-Service no longer exists** (decommissioned 17 Jul 2026). Amadeus
  Enterprise is contract-gated and, even with a contract, returns GDS offers with no
  per-channel comparison or outbound booking links. Dead end for this feature.
- **Kiwi Tequila is invitation-only** (since May 2024) and is single-channel anyway
  (Kiwi is the seller). **Skyscanner's Live Search API does return per-seller prices +
  deep links**, but access is by partnership application on revenue-share/affiliate
  terms — a later option, not a quick win.
- **Costco Travel, airline-direct sites, Indian Eagle / TripBeam-type consolidators,
  and Google Flights itself can never be live-priced by us** (no APIs; scraping is
  ToS-barred and bot-defended). They remain editorial content — which is what the
  "Best place to book" guide already covers.
- **Recommendation:** Architecture A (SerpApi channel comparison layered on the
  existing Duffel calendar, weekly cadence to start, ~$75/mo) — detailed below, with a
  $0 pilot that fits SerpApi's free tier.

## What "channel comparison" actually requires

For one itinerary (specific flights, dates), we need: (1) the list of sellers offering
that exact itinerary, (2) each seller's total price for it, (3) a working click-out
link per seller. Only metasearch-style sources have this data, because the sellers bid
into the metasearch index — no GDS/aggregator API (Duffel, Amadeus) sees rival
channels' prices for the same seat.

One coverage caveat that applies to every metasearch source: the channel list is
whatever the metasearch carries. On Google Flights for US→India routes that typically
means the operating airline(s) plus large OTAs. **Diaspora consolidators (Indian
Eagle, TripBeam, ASAP Tickets) generally do not appear in Google Flights booking
options**, so even the best implementation cannot live-price the consolidator channel
— it stays editorial ("consolidators sometimes beat these prices; check before
booking"). Which sellers actually appear per India route is **unverified** — it can
only be confirmed with live API calls, and no sample call was possible (free tier
requires an account signup, which was out of scope).

## Per-provider findings

| Provider | Per-channel prices? | Booking links? | US→India coverage | Cost model | Access gate | Verdict |
|---|---|---|---|---|---|---|
| **SerpApi Google Flights** | **Yes** — `booking_options[]`: seller, price, baggage prices, separate-ticket flag | **Yes** — per-seller `booking_request` click-out link | Whatever Google Flights lists (airlines + major OTAs); consolidators generally absent (unverified per route) | Per search: free 250/mo; $25/1,000; $75/5,000; $150/15,000; $275/30,000 | Self-serve signup, immediate | **Only viable channel-comparison source today — with litigation risk (below)** |
| **Duffel** (integrated) | No — Duffel is the single seller | Duffel Links hosted checkout / Orders API (book *through* Duffel, not a channel link) | Good on US→India (Air India, partners, NDC+GDS content) | Per order (~$3, 3rd-party listings) + excess-search fee $0.005/search beyond 1,500 searches per order; test mode free | Already connected (managed connector) | Keep for calendar/fare ranges; not comparison |
| **Amadeus Self-Service** | — | — | — | Was free tier + per-call | **Decommissioned 17 Jul 2026** | Gone |
| **Amadeus Enterprise** | No — GDS offers only, no rival channels, no outbound links | No (booking via Amadeus itself) | Strong GDS coverage | Contract: monthly minimums + per-segment fees (3rd-party estimates vary widely — unverified) | Sales contract, certification | Not viable for this feature |
| **Kiwi Tequila** | No — Kiwi is the single seller (virtual interlining) | Yes, to Kiwi checkout | Decent, LCC-heavy | Commission share (affiliate) | **Invitation-only since May 2024** | Not obtainable; not comparison anyway |
| **Skyscanner Travel API** | **Yes** — Live Search returns offers per seller | **Yes** — deep links to airlines/OTAs | Strong global metasearch | Revenue share / affiliate (via impact.com) | Partnership application + review; reportedly expects established traffic (≥100K monthly users figure is unverified) | True comparison, but gated — revisit at scale |
| **Travelpayouts / Aviasales Data API** | No — one aggregated price per itinerary, not per seller | Link back to Aviasales search (affiliate marker); per-agency links generated only on user click, 15-min validity, bulk collection prohibited | Cached user-search data (2–7 days old), market skew unverified for US→India | Free; affiliate commission model | Self-serve affiliate signup | Optional free supplement for cached fare color; affiliate decision required; not live comparison |
| **Aviation Edge Flight Ticket Prices** | No — single price per result in docs examples | None shown in docs | Unverified | Monthly API subscription | Self-serve | Not a comparison API |
| **fast-flights (open-source scraper)** | No — one Google Flights price | Google Flights URL only | Same as Google Flights UI | Free (self-hosted) | None | Breaks when Google changes markup; self-scraping breaches Google ToS — not recommended |

### SerpApi Google Flights — detail

- **Flow (this drives the cost):** a round-trip comparison takes up to **3 paid
  searches** — (1) outbound search returning options with `departure_token`,
  (2) return-options call with that token, returning the chosen itinerary's
  `booking_token`, (3) booking-options call with the token, returning
  `booking_options[]` (seller name, price, baggage prices, separate-ticket warning,
  booking link) plus `price_insights` (lowest price, typical range, price history).
  One-way itineraries take 2 calls. Sources: SerpApi API docs
  (https://serpapi.com/google-flights-api) and integrator write-ups of the token flow
  (https://github.com/danilok77/take-off, https://github.com/haroldleo/google-flights-mcp).
- **Pricing** (SerpApi pricing page, corroborated by multiple Oct-2026 roundups):
  Free 250 searches/mo · Starter $25/1,000 · Developer $75/5,000 ·
  Production $150/15,000 · Big Data $275/30,000. Failed/empty searches still count;
  identical searches are cached free for 1 hour; "Ludicrous Speed" doubles cost
  (avoid). Throughput caps apply per plan (Starter 200 searches/hr) — batch jobs must
  pace themselves.
- **ToS/display:** the API is sold for commercial app use and returns booking links
  precisely so developers can present them; there is no separate "display license."
  The legal exposure sits upstream (SerpApi↔Google) — see risk note. SerpApi's
  "U.S. Legal Shield" (they assume scraping liability) is bundled from Production
  ($150/mo) up. Full legal terms were not re-read line-by-line; treat ToS detail as
  partially verified.
- **Litigation risk (flagged, facts):** Google sued SerpApi in Dec 2025 alleging
  DMCA/ToS violations for circumventing SearchGuard to harvest search results at
  scale; Reddit has a related suit naming SerpApi. SerpApi's public position is that
  accessing public data is First-Amendment-protected. If Google wins injunctive
  relief, this data source could degrade or stop. Coverage:
  https://www.archyde.com/google-sues-serp-scraper-serpapi-marking-a-fierce-new-push-to-guard-search-data-in-the-ai-era/
  and https://almcorp.com/blog/google-sues-serpapi-lawsuit-analysis/

### Duffel — detail

- Current integration (`pipeline/flight-deals.py`) calls the managed `duffel` CLI
  search and keeps, per offer: total price, operating airline, stops, fare brand,
  checked-bag count, currency. That is everything the calendar needs. It does not
  capture (and Duffel does not provide) rival-seller prices.
- **Booking path:** Duffel Links is a Duffel-hosted search-and-checkout page, or the
  Orders API for a self-built checkout. Either way the Duffel account holder is the
  seller of record — adopting it converts The Videshi from discovery into a ticket
  seller (payments, servicing, schedule-change handling). That is a business-model
  decision for Kiran, not a linking option, and it still wouldn't show competing
  channels.
- **Cost:** official pricing page confirms a per-order fee plus an **excess search
  fee**: searches are free up to 1,500 per order; beyond that, $0.005/search
  (https://duffel.com/pricing). Today's traffic runs through the managed connector,
  so no per-search billing is visible to the project. On a hypothetical own account
  with zero Duffel bookings, the current calendar workload (~432 searches/run;
  ~13,000/mo daily) would incur roughly **$65/mo** in excess-search fees; a weekly
  calendar (~1,900 searches/mo) roughly **$9/mo**. Third-party listings put the
  per-order fee at ~$3.

### The closed doors

- **Amadeus Self-Service:** decommissioned 17 Jul 2026; registrations paused, keys
  disabled, SDK repos archived; Enterprise continues for contracted customers
  (PhocusWire, 2026-02-09:
  https://www.Phocuswire.com/amadeus-shut-down-self-service-apis-portal-developers;
  corroborated by the Amadeus for Developers homepage notice as reported Oct 2026).
- **Kiwi Tequila:** new partnerships "on an invitation 
...[truncated 8798 chars]