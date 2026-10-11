# Flight Deals — Edge Cases & UX Issues

Deep research on problems to solve BEFORE building. Kiran's directive: find these proactively, don't wait for him to catch them.

---

## 1. DATE / DURATION EDGE CASES

### 1.1 Cross-month trips (Kiran caught: Christmas/New Year)
**Problem:** A month-grid UI breaks when trips span two months. "Cheapest in December" for Dec 20 → Jan 5 is misleading — it's not a December trip.

**This affects more than Christmas:**
- Diwali trips: Nov 1 → Nov 20 (spans Nov only, OK)
- Summer trips: Jun 25 → Jul 15 (spans Jun/Jul)
- Any 3-4 week trip starting mid-month crosses the boundary

**Solution:** Don't use months as the primary unit. Use **seasons + date ranges**:
- Show "Dec 20 → Jan 5: $1,400" as a "Christmas & New Year" season card
- For regular months, show the actual best date range found, not just "$890 in November"
- The calendar becomes: [Seasons] + [Months with date ranges], not a 12-month grid

### 1.2 Non-standard durations (10 days, 12 days, etc.)
**Problem:** If we offer 1/2/3/4 week options, what about someone who wants 10 days? They get no useful data.

**Solution:** Don't overthink this. The duration selector (2/3/4 weeks for India) covers 90% of real trips. Someone wanting exactly 10 days can use the 2-week price as a close proxy — the fare difference between 10 and 14 days on the same route is usually <$50. Add a note: "Prices shown for 14-day trips; 10-12 day trips are typically within $50."

### 1.3 One-way trips
**Problem:** Some diaspora members fly one-way (relocating, extended stays, uncertain return). One-way international fares on legacy carriers are brutal — often 20%+ more than half a round-trip, sometimes dramatically worse (e.g., $3,000 one-way vs $1,700 round-trip on the same route).

**Solution:** Don't offer one-way pricing in v1. The price calendar is round-trip only. Add a disclaimer: "One-way fares are typically 20-50% more than half a round-trip on these routes. We show round-trip only." If demand emerges, add one-way as a Phase 3 feature with clear warnings.

### 1.4 Multi-city / open-jaw (fly into DEL, out of BOM)
**Problem:** Many diaspora travelers visit family in one city and fly out of another. E.g., SFO → DEL → (domestic) → BOM → SFO. Our simple round-trip calendar doesn't handle this.

**Solution:** Out of scope for v1. The price calendar assumes same-airport round-trip. Note this limitation. Multi-city is a Phase 3+ feature — it requires 2x the API searches and complex UX.

### 1.5 Stopover preferences (Dubai, Doha, London)
**Problem:** Some travelers PREFER a stop in Dubai/Doha to visit friends, shop, or break up the journey. Our "max 1 stop" filter treats all stops as undesirable.

**But there's a flip side:** Emirates (Dubai Connect), Qatar Airways, and Etihad offer FREE hotel + meals for long layovers (8-26 hours). This is a feature, not a bug, for some travelers.

**Solution:** Add a "stopover-friendly" toggle in Phase 2. When enabled, highlight itineraries with 8+ hour layovers in Dubai/Doha/Abu Dhabi and note the free hotel benefit. This is a genuine diaspora-specific differentiator — Google Flights doesn't surface this.

---

## 2. PRICE DISPLAY ISSUES

### 2.1 Price staleness — how fresh is fresh enough?
**Problem:** Airlines update fares up to 3x daily. A price we fetched Monday morning could be wrong by Monday evening, especially close to departure.

**Data:**
- Fares are most volatile in the final 2 weeks before departure and during peak seasons
- In the 2-4 month booking window, prices are relatively stable
- Our calendar shows prices for trips 1-12 months out — most are in the stable zone

**Solution:**
- Label every price with "as of [date]": "SFO → DEL, Dec 10-31: $890 (checked Oct 10)"
- Refresh cycle: weekly for 3+ months out, daily for <3 months out
- For peak seasons (Diwali, Christmas), refresh daily regardless
- Never show a price older than 7 days without a "stale" warning

### 2.2 "Only 1 seat left at this price"
**Problem:** Duffel returns the cheapest available fare. If only 1 seat remains at $890 and the next fare bucket is $1,100, our calendar shows $890 — but the user likely can't book it.

**Solution:** This is a known limitation of all fare displays (Google Flights has the same issue). Mitigate by:
- Showing a price RANGE for each month, not just the cheapest: "$890 - $1,050"
- The range captures fare bucket volatility
- Add note: "Prices are for the cheapest available fare and may change"

### 2.3 Baggage — the hidden cost
**Problem:** US-India economy typically includes 2 checked bags (23kg each). BUT:
- Basic Economy on United/American/Delta: **ZERO free checked bags** internationally
- First checked bag on basic economy transatlantic: $75 each way
- Emirates "Special" fares: no checked baggage included
- A "$750" basic economy fare + $150 in bag fees = $900 effective

For diaspora travelers who ALWAYS check 2 bags (gifts, food, clothes), a basic economy "deal" is a trap.

**Solution:**
- **Exclude basic economy fares entirely.** Filter to standard economy+ only.
- Label clearly: "Prices include 2 checked bags (standard for US-India routes)"
- This is a trust issue — showing a misleadingly low basic economy fare destroys credibility

### 2.4 Fare class confusion
**Problem:** Duffel returns multiple fare brands for the same flight. The cheapest might be non-refundable, no-changes, no seat selection.

**Solution:** Default to the cheapest **standard** economy fare (not basic). In the detail view, show fare conditions: refundable/changeable status. Keep the calendar simple — just the price — but ensure it's for a usable fare.

---

## 3. ROUTE ISSUES

### 3.1 "SFO → Delhi" vs. creative routings
**Problem:** What if SFO → BOM → DEL (domestic connection) is cheaper than SFO → DEL direct? Do we show it?

**Solution:** No. Keep it simple: SFO → DEL means arriving in Delhi. If the cheapest option routes through Mumbai, that's fine — Duffel handles it as a connection. We display the final destination price. Don't try to be clever with split tickets.

### 3.2 Nearby airports — Bay Area problem
**Problem:** SFO vs SJC vs OAK. Should we combine them?

**Data:** SFO has 60+ international destinations. OAK has ~15 (mostly domestic/Caribbean). SJC has ~8. For US-India specifically, **SFO is essentially the only Bay Area option.** OAK and SJC don't have meaningful India service.

**Solution:** Don't combine. Use the primary international airport per metro:
- Bay Area → SFO
- NYC → JFK (not EWR — though EWR has some India service via United)
- Chicago → ORD
- Dallas → DFW

For NYC, consider showing both JFK and EWR as separate options in Phase 2 since both have India flights. For other metros, single airport is fine.

### 3.3 Indian domestic connections
**Problem:** Someone flying SFO → HYD might connect through DEL or BOM. That's handled by the airline. But what about showing DEL → HYD as a separate searchable route?

**Solution:** Out of scope for v1. Focus on US → India international routes. Indian domestic connections are the traveler's problem to solve (and they're cheap — $50-100 on IndiGo). Don't complicate the UI.

---

## 4. USER EXPECTATION ISSUES

### 4.1 "I clicked through and the price is different"
**Problem:** This is the #1 trust killer. User sees "$890" on our site, clicks to book, finds $1,050.

**Why it happens:**
- Price changed since our last refresh
- Fare bucket sold out
- Duffel's price was for a specific flight combo that's no longer available
- User's dates are slightly different

**Solution:**
- Always show "as of" date prominently
- Show price ranges, not single prices
- Set expectations: "Prices are indicative and change frequently. Use this to plan WHEN to fly, not as a booking quote."
- Position as a **planning tool**, not a booking engine. This is key to the value prop.

### 4.2 No data available
**Problem:** What if Duffel returns no results for a route/date? (API error, no flights, route not served)

**Solution:**
- Show "No data" gracefully, not a $0 or error
- Distinguish: "No flights on this route" vs "Data temporarily unavailable, check back tomorrow"
- Don't let one failed route break the entire calendar

### 4.3 What counts as a "deal"?
**Problem:** If everything is labeled a "deal," nothing is. What's the baseline?

**How Google does it:** 60-day price history, color-coded low (green) / typical (yellow) / high (red) vs. recent prices on that route.

**Solution for us:**
- Build 90-day rolling price history per route
- "Deal" = >15% below the 90-day median for that route
- "Typical" = within 15% of median
- "High" = >15% above median
- Don't label everything — only highlight true deals (green) and warnings (red for peak pricing)
- Early on (first 3 months), we won't have enough history. Use a "New — building price history" label instead of fake deal indicators.

---

## 5. MOBILE UX

### 5.1 12-month grid doesn't work on mobile
**Problem:** A 12-column grid is unreadable on a phone.

**Solution:**
- Mobile: vertical list, not grid. Each row = one month/season with price, date range, and deal indicator.
- Show 3 months by default, "show more" to expand
- The mockup already does this correctly — keep it

### 5.2 Too many routes = overwhelming
**Problem:** 10 US metros × 6 Indian metros = 60 routes. A dropdown with 60 options is unusable.

**Solution:**
- Default to the user's nearest metro (geolocation or manual selection, like Your Hub does)
- Show 4-6 most popular routes from that metro
- "Compare all routes" as a secondary view, not the default
- Tier 1 routes first: SFO→DEL/BLR, JFK→DEL/BOM, ORD→DEL, DFW→HYD

---

## 6. DATA FRESHNESS & API

### 6.1 How often do US-India fares actually change?
**Data:**
- Airlines update fares up to 3x daily
- Most volatile: <2 weeks to departure, peak seasons
- Most stable: 2-4 months out (our primary planning window)
- Realistically: prices for 3+ months out change weekly, not daily

**Solution:**
- Weekly refresh is sufficient for 3+ months out
- Daily refresh for <3 months out and peak seasons
- This keeps API load manageable (~200 searches/day)

### 6.2 Duffel API limits
**Data:** Duffel charges $3/order (booking). Searches appear to be free/unmetered based on available documentation. No explicit search quota found.

**Risk:** If we scale to 1,590 searches/week and Duffel imposes limits, we're stuck.

**Solution:**
- Start with Phase 1 (10 routes × 6 months = manageable volume)
- Monitor for rate limiting
- Have a fallback: if Duffel throttles, reduce to bi-weekly refresh for far-out dates
- Don't build the entire product on an undocumented assumption — verify with Duffel before Phase 2 scale-up

### 6.3 Search result volume
**Problem:** Each Duffel search returns up to 300 offers. For 1,590 searches/week, that's potentially 477,000 offers to process.

**Solution:**
- We only need the cheapest standard-economy fare per date — not all 300 offers
- Parse and discard: extract min price + date range, store aggregate, drop the rest
- Don't store raw API responses long-term

---

## 7. THINGS THAT WON'T WORK (be honest)

### 7.1 Real-time prices
We cannot show real-time prices. We're a planning tool with weekly/daily refreshes, not a live booking engine. Be upfront about this.

### 7.2 Predicting future prices
We cannot predict whether Diwali 2027 fares will go up or down. We can show historical trends ("Diwali fares rose 40% from Aug to Oct last year") but not forecasts. Don't try — Hopper tried and it's unreliable.

### 7.3 Covering every route
We cannot cover every US-India city pair. Start with Tier 1 (8-10 routes), expand based on usage data.

### 7.4 Competing with Google Flights on search
We will not build a better flight search than Google. Our value is curation, context, and diaspora-specific intelligence — not search completeness.

---

## SUMMARY: Design Principles

1. **Planning tool, not booking engine** — help users decide WHEN to fly, not WHERE to book
2. **Seasons over months** — show "Christmas & New Year: Dec 20 → Jan 5" not just "December"
3. **Date ranges always** — never show a month price without the actual dates
4. **Exclude basic economy** — only show fares with 2 checked bags included
5. **Price ranges, not single prices** — "$890 - $1,050" captures reality better than "$890"
6. **"As of" on everything** — every price labeled with its check date
7. **Mobile-first vertical list** — no grids on mobile
8. **Start small** — 10 routes, expand based on real usage
9. **Build price history before claiming "deals"** — 90 days minimum
10. **Be honest about limitations** — "indicative prices for planning" not "book now at this price"
