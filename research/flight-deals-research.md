# Flight Deals / Travel Price Section — Research Report

**Date:** 2026-10-10
**For:** The Videshi (thevideshi.com)
**Requested by:** Kiran

---

## Executive Summary

Building a flight deals section is **technically feasible and cheap** using the Duffel API (already integrated). Searches are free; the main cost is compute time. The key insight: don't compete with Google Flights on raw search — win on **diaspora-specific context** (festival timing, family pricing, WhatsApp alerts, India-corridor focus).

**Recommended approach:** Start with an India price calendar (highest value for the audience), then expand to leisure destinations.

---

## 1. Technical Feasibility

### 1.1 Data Source: Duffel API

**Status:** Already integrated via `duffel` CLI at `/opt/hatch/bin/duffel`.

**Verified working:** Tested SFO→DEL roundtrip search on 2026-10-10 — returned 5 offers successfully (~9 seconds per search).

**Pricing:**
- Flight **searches are free** (no per-search cost)
- Duffel charges **$3 per booking/order** — irrelevant for us since we're displaying prices, not booking
- **Effective data cost: $0**

**Rate limits:**
- No published hard limit
- Returns `429 Too Many Requests` with `ratelimit-limit`, `ratelimit-remaining`, `ratelimit-reset` headers
- Implement exponential backoff on 429 (standard practice)

**Coverage notes:**
- `search_coverage.complete` was `false` on test search — normal for Duffel (covers scanned inventory, not exhaustive)
- Results are real GDS (Global Distribution System) fares from 400+ airlines
- Roundtrip searches supported via `--return-date`
- Use `--limit 30` (not 300) for price-tracking — we only need the cheapest few offers

**Caveat:** Verify with the Duffel account dashboard whether there's a monthly search quota on the current plan. The skill documentation doesn't mention one, but it's worth confirming before scaling to thousands of searches/week.

### 1.2 Alternative Data Sources (Evaluated)

| Source | Status | Cost | Verdict |
|--------|--------|------|---------|
| **Duffel** | Active, tested | Free searches | ✅ **Use this** |
| Amadeus Self-Service | **Shut down July 17, 2026** | N/A | ❌ Dead |
| Skyscanner Travel API | Commercial only; not for startups <100K MAU | Unknown | ❌ Blocked |
| Kiwi.com Tequila | Invitation-only since May 2024 | Unknown | ❌ Blocked |
| SerpApi Google Flights | Works | 250 free/mo, then $0.025–$0.009/search | ⚠️ Backup option |
| Apify Flight Offers API | Works (Google Flights scraper) | $0.003/search + $0.0005/offer; $5 free credit ≈ 600 searches | ⚠️ Backup option |
| fast-flights (Python) | Scrapes Google Flights directly | Free but fragile | ❌ Breaks when Google changes layout |

**Conclusion:** Duffel is the clear winner — free, stable, already integrated, real GDS data.

### 1.3 Search Volume Math

**India corridor:**
- US metros: SFO, JFK, ORD, DFW, SEA, LAX, IAD, BOS, ATL, MIA = **10**
- Indian metros: DEL, BOM, HYD, BLR, MAA, CCU = **6**
- Routes: 10 × 6 = **60 routes**

**Price calendar strategy:**
- Per route-month: 2 sample roundtrip searches (e.g., depart 10th return 24th; depart 17th return 31st), take the minimum
- Full 12-month calendar: 60 routes × 12 months × 2 = **1,440 searches**

**Leisure destinations:**
- ~15 destinations (Hawaii, Cancun, Paris, London, Dubai, Bali, Maldives, etc.)
- × 5 US metros (SFO, JFK, ORD, DFW, LAX) = **75 routes**
- Per route: 2 searches (next 3 months, pick cheapest) = **150 searches**

**Total per full refresh cycle: ~1,590 searches**

**Timing:**
- ~9 seconds per search (measured)
- 1,590 × 9s = ~14,300 seconds ≈ **4 hours**
- Spread across a weekly cron: ~230 searches/day ≈ **35 minutes/day**
- Or batch in parallel (4 workers): ~1 hour for full refresh

**Refresh cadence recommendation:**
- **Rolling 3 months:** Daily refresh (180 searches/day for India routes — high value, near-term bookings)
- **Months 4–12:** Weekly refresh (far-term prices are less volatile)
- **Leisure destinations:** Weekly refresh (150 searches/week)

**Daily search budget: ~200–250 searches/day** — well within Duffel's tolerance.

### 1.4 What's Hard / Might Not Work

1. **Price accuracy:** Duffel returns live GDS fares, but prices change constantly. A price shown yesterday may not be bookable today. **Mitigation:** Label all prices "as of [date]" and link to Google Flights for live booking.

2. **No booking:** We're a price discovery tool, not a booking platform. Users click through to airline/Google Flights to book. This is fine — Google Flights does the same thing.

3. **Festival date alignment:** Mapping "Diwali 2026" to specific travel dates requires maintaining a festival calendar. We already have 339 temple festivals in the DB — extendable.

4. **Family pricing:** Default searches use 1 adult. Diaspora families travel in groups of 2–4. **Mitigation:** Default to 2 adults in searches, note "per person" clearly.

5. **Duffel coverage gaps:** Some budget carriers (Southwest, etc.) aren't in GDS. For US-India routes this matters less (all major carriers are GDS).

---

## 2. Competitive Analysis

### 2.1 Google Flights
- **Strengths:** 300+ partners, price tracking with email alerts, date grid, price graph, "cheapest time to book" insights from 2B+ daily data points, 95% prediction accuracy claims
- **Weaknesses:** Generic (not diaspora-aware), email-only alerts, no festival context, defaults to solo traveler
- **Our edge:** We don't compete on search breadth. We compete on **context**.

### 2.2 Hopper
- **Strengths:** Color-coded calendar (green/yellow/red), "buy now or wait" predictions, push notification alerts, claims 40% average savings
- **Weaknesses:** App-only (no web), generic audience, no India-specific features
- **Our edge:** Web-accessible, India-corridor specialized, integrated with Videshi content

### 2.3 Kayak / Skyscanner
- **Strengths:** Broad search, fare alerts
- **Weaknesses:** Commodity; no differentiation for diaspora
- **Our edge:** Same as above

### 2.4 Our Differentiators

1. **Festival-aware:** "Diwali is Nov 8 — fares from SFO are $1,200 now vs $900 last month." Nobody else connects festival dates to fare data.

2. **Family-default pricing:** Default to 2 adults + checked bags (diaspora reality), not 1 adult carry-on only.

3. **WhatsApp alerts:** The diaspora lives on WhatsApp. Price-drop alerts via WhatsApp (we have the channel) beat email.

4. **Trip context:** "Landing in Delhi Nov 5? Here are Diwali events near you." Flights + events + festivals in one place. Nobody else does this.

5. **India-corridor depth:** 60 routes with monthly granularity is deeper than any generalist tool goes for this specific corridor.

**Positioning:** Not "a better Google Flights." Instead: **"The diaspora's trip planner — know when to fly home."**

---

## 3. Data Architecture

### 3.1 Supabase Schema

```sql
-- Raw price observations
CREATE TABLE flight_prices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  origin TEXT NOT NULL,           -- e.g., 'SFO'
  destination TEXT NOT NULL,      -- e.g., 'DEL'
  departure_date DATE NOT NULL,
  return_date DATE NOT NULL,
  price_usd DECIMAL NOT NULL,
  airline TEXT,                   -- e.g., 'Air India'
  stops INT,                      -- 0, 1, 2
  duration_min INT,
  cabin TEXT DEFAULT 'economy',
  passengers INT DEFAULT 2,
  searched_at TIMESTAMPTZ DEFAULT NOW(),
  source TEXT DEFAULT 'duffel'
);
CREATE INDEX ON flight_prices (origin, destination, departure_date);
CREATE INDEX ON flight_prices (searched_at);

-- Aggregated monthly stats (for calendar view)
CREATE TABLE flight_price_monthly (
  origin TEXT NOT NULL,
  destination TEXT NOT NULL,
  year INT NOT NULL,
  month INT NOT NULL,
  min_price DECIMAL,
  avg_price DECIMAL,
  median_price DECIMAL,
  sample_count INT,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (origin, destination, year, month)
);

-- User price alerts
CREATE TABLE flight_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,                    -- nullable for anonymous
  phone TEXT,                      -- for WhatsApp alerts
  email TEXT,
  origin TEXT NOT NULL,
  destination TEXT NOT NULL,
  target_price DECIMAL,
  travel_month INT,                -- nullable (any month)
  travel_year INT,                 -- nullable
  is_active BOOLEAN DEFAULT TRUE,
  last_notified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.2 Refresh Strategy

| Data | Cadence | Searches/day | Method |
|------|---------|-------------|--------|
| India routes, months 1–3 | Daily | ~180 | Cron at 2 AM PDT |
| India routes, months 4–12 | Weekly (Sunday) | ~170 avg | Cron Sunday 3 AM PDT |
| Leisure routes | Weekly (Sunday) | ~150 | Same Sunday cron |
| **Total** | | **~200–250/day avg** | |

### 3.3 Deal Detection Algorithm

Simple and explainable (no ML needed for v1):

```
For each route:
  median_90d = median(price) WHERE searched_at > NOW() - 90 days
  current = latest min_price for route

  if current < median_90d * 0.75:  → "Great deal" 🟢
  elif current < median_90d * 0.85: → "Good deal" 🟢
  elif current < median_90d * 1.15: → "Typical" 🟡
  else:                             → "High" 🔴
```

**Why this works:** It's the same approach Google Flights uses (comparing to historical median). Simple, explainable, no training data needed. Gets smarter as we accumulate history.

**Phase 2 enhancement:** Add "buy now or wait" by tracking price velocity (is the 7-day trend going up or down?).

### 3.4 Pipeline Script

New file: `pipeline/flight-prices.py`
- Reads route list from `pipeline/flight-routes.json`
- Runs Duffel searches via subprocess (following existing curl/subprocess patterns)
- Inserts into `flight_prices` via Supabase REST (curl, per AGENTS.md)
- Updates `flight_price_monthly` aggregations
- Logs to `~/memory/YYYY-MM-DD.md`

---

## 4. UX Proposal

### 4.1 India Price Calendar

**Layout (mobile-first):**
```
┌─────────────────────────────────┐
│ ✈️ India Flight Prices          │
│                                 │
│ From: [SFO ▾]  To: [DEL ▾]     │
│                                 │
│ ┌───┬───┬───┬───┬───┬───┐      │
│ │Nov│Dec│Jan│Feb│Mar│Apr│ ...  │
│ │$98│$14│$11│$89│$95│$10│      │
│ │ 0 │20 │50 │ 0 │ 0 │20 │      │
│ └───┴───┴───┴───┴───┴───┘      │
│ 🟢 Nov: Great deal              │
│ 🟡 Dec: Typical for Diwali      │
│ 🔴 Jan: High — wait if flexible │
│                                 │
│ 🎉 Diwali 2026: Nov 8           │
│ ✈️ Cheapest Diwali week: Nov 1-8│
│    from $980                     │
└─────────────────────────────────┘
```

**Key features:**
- Color-coded months (green/yellow/red) like Hopper
- Festival markers on relevant months (Diwali, Christmas, Holi, summer)
- Tap a month → see sample dates and prices
- "Set alert" button per route

### 4.2 Leisure Destination Cards

**Layout:**
```
┌─────────────────────────────────┐
│ 🌴 Top Destinations             │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ [Photo: Bali]               │ │
│ │ Bali, Indonesia             │ │
│ │ From $650 · Best: Sep-Nov   │ │
│ │ 🟢 $120 below average       │ │
│ │ [Set Alert]                 │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ [Photo: Paris]              │ │
│ │ Paris, France               │ │
│ │ From $480 · Best: Jan-Mar   │ │
│ │ 🟡 Typical for season       │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

**Each card shows:**
- Destination photo (already have 50 travel guides with Pexels photos)
- Name
- Best fare from user's nearest metro (or SFO default)
- Best months to visit
- Deal indicator (vs historical average)
- Alert signup

### 4.3 Integration Points

- **Travel page** (`/travel`): Add "Flight Deals" tab alongside existing destination guides
- **Festival pages:** "Flying for Diwali? Cheapest fares from your city" widget
- **Your Hub:** Personalized — "Based on your location (SFO), here are Diwali fares to DEL"
- **WhatsApp:** Price-drop alerts via existing channel

### 4.4 Mobile Considerations

- Calendar must work with horizontal scroll on mobile (12 months don't fit)
- Default to showing next 6 months, "see more" for full year
- Destination cards: single column, large tap targets
- All prices labeled "per person" and "as of [date]"

---

## 5. Build Plan

### Phase 1: MVP — India Price Calendar (1 week)

**Scope:**
- 10 routes (top 5 US metros × top 2 Indian metros: SFO/JFK/ORD/DFW/LAX × DEL/BOM)
- 6-month forward calendar (not 12)
- Daily refresh cron
- Basic grid UI on `/travel/deals`
- Manual "as of" timestamps, no alerts yet

**Files to create:**
- `pipeline/flight-prices.py` — search + insert script
- `pipeline/flight-routes.json` — route configuration
- `src/pages/FlightDealsPage.tsx` — calendar UI
- Supabase migration for `flight_prices` + `flight_price_monthly`

**Deliverable:** Working price calendar for 10 routes, updated daily.

### Phase 2: Full Coverage + Alerts (2 weeks)

**Scope:**
- Expand to all 60 India routes × 12 months
- Deal detection (green/yellow/red indicators)
- Festival markers (Diwali, Christmas, Holi, summer)
- Price alert signup (email first, WhatsApp second)
- "Best time to book" insights per route

**Deliverable:** Full India corridor coverage with deal indicators and alerts.

### Phase 3: Leisure Destinations (2 weeks)

**Scope:**
- 15 leisure destinations × 5 US metros
- Destination deal cards with photos
- Integration with existing 50 travel guides
- "Best months to visit" per destination
- WhatsApp price-drop alerts

**Deliverable:** Complete travel deals section covering both India and leisure.

### Total Timeline: ~5 weeks for full build

---

## 6. Costs

| Item | Cost |
|------|------|
| Duffel API searches | **$0** (free) |
| Supabase storage (price history) | Negligible (~$0, within existing plan) |
| Compute (cron searches) | $0 (existing VM) |
| WhatsApp alerts | $0 (existing channel, manual for MVP) |
| **Total monthly** | **~$0** |

This is essentially free to operate. The main investment is build time.

---

## 7. Risks and Honest Caveats

1. **Duffel quota:** Confirm no hidden search limits on the current plan before scaling.

2. **Price staleness:** Displayed prices are snapshots. Always label "as of [date]" and link out for live booking. Don't promise the displayed price is bookable.

3. **Google competition:** We're not beating Google Flights at search. Our win is context (festivals, family, WhatsApp, curation). If Kiran expects feature parity with Google Flights, reset that expectation.

4. **Maintenance burden:** 250 searches/day is a new daily cron to monitor. Price data pipelines can break silently (API changes, rate limits). Build alerting for pipeline failures.

5. **Alert fatigue:** If we send too many WhatsApp alerts, users will mute. Be conservative: only alert on >15% drops, max 1 alert per route per week.

6. **Seasonal accuracy:** The "best months" data will be thin for the first 3 months until we accumulate history. Label early data as "limited history."

---

## 8. Recommendation

**Build Phase 1 (MVP) first.** It's 1 week of work, essentially free to operate, and will validate whether users actually engage with fare data. If the price calendar gets traction, invest in Phases 2 and 3.

**Don't build:** A full flight search/booking flow. That's Google Flights' game. Stay in the discovery/alerts lane.

**Do build:** The festival-aware, family-default, WhatsApp-alert layer that nobody else offers for the India corridor.

---

*Report saved to `~/workspace/the-videshi-news/research/flight-deals-research.md`*
