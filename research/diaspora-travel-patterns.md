# Indian Diaspora Travel Patterns — Research for Flight Deals UI

**Date:** 2026-10-10
**Purpose:** Inform the flight deals price calendar UI for The Videshi with real diaspora travel behavior data.

---

## 1. When Diaspora Flies to India — Peak Seasons

### Peak (expensive, book 4-5 months ahead)

| Period | Dates | Why |
|--------|-------|-----|
| **Diwali** | Oct-Nov (varies yearly) | Biggest festival; family reunions |
| **Christmas / New Year** | Dec 20 – Jan 5 | Winter break; school holidays |
| **Summer** | June – July | School summer break; wedding season |
| **Thanksgiving week** | Late November | Long weekend trips |

### Shoulder (moderate prices)

| Period | Dates | Why |
|--------|-------|-----|
| **Navratri / Dussehra** | Oct (varies) | Festival travel, less than Diwali |
| **Spring break** | March – April | School breaks |

### Off-peak (cheapest, 30-40% below peak)

| Months | Notes |
|--------|-------|
| **February** | Post-holiday lull; good weather in India |
| **March** | Pre-summer; Holi is early March but doesn't spike fares like Diwali |
| **August** | Monsoon; lowest demand |
| **September** | Post-monsoon, pre-festival; sweet spot for deals |

**Key insight:** The cheapest months (Feb, Aug, Sep) are 30-40% cheaper than December. This is the single most useful fact for the UI — a user who can shift from December to February saves hundreds.

---

## 2. Festival Dates — Exact (for UI markers)

### 2026

| Festival | Date | Day | Travel window (fly out → return) |
|----------|------|-----|----------------------------------|
| Holi | Mar 4 | Wed | Feb 28 – Mar 8 |
| Ganesh Chaturthi | Sep 14 | Mon | Sep 10 – Sep 18 |
| Navratri | Oct 11–19 | Sun–Mon | Oct 8 – Oct 22 |
| Dussehra | Oct 20 | Tue | Oct 17 – Oct 23 |
| **Diwali (main day)** | **Nov 8** | **Sun** | **Nov 1 – Nov 15** |
| Diwali 5-day festival | Nov 6–10 | Fri–Tue | — |
| Christmas | Dec 25 | Fri | Dec 20 – Jan 3 |

### 2027

| Festival | Date | Day |
|----------|------|-----|
| Holi | Mar 22 | Mon |
| Dussehra | Oct 9 | Sat |
| **Diwali (main day)** | **Oct 29** | **Fri** |

### Wedding Season (drives additional demand)

- **Peak wedding months:** November–December, January–February, April–May
- **No weddings:** August–October (Chaturmas — religious pause)
- 2026 auspicious dates cluster: Nov 21–26, Dec 2–6, Feb 5–26
- Wedding travelers often fly for 1-2 weeks around specific dates

**UI implication:** Mark Diwali, Christmas, and wedding-season peaks on the calendar. These aren't just "expensive months" — they're the *reason* people are flying, so the UI should acknowledge the context ("Diwali week — fares 60% above average").

---

## 3. Trip Durations — What's Realistic

### India family visits

| Trip type | Duration | Frequency | Notes |
|-----------|----------|-----------|-------|
| **Annual long trip** | 3–4 weeks | Once/year | Summer or Diwali/Christmas; uses most PTO |
| **Short trip** | 2 weeks | Once/year | Second visit; often around a festival or wedding |
| **Wedding trip** | 1–2 weeks | As needed | Tied to specific dates |

**Most common pattern:** 2 trips/year — one ~1 month, one ~2 weeks. (Source: diaspora community forums.)

**Recommended UI duration options:**
- **2 weeks** (most common single selection)
- **3 weeks** (sweet spot for "going home" trips)
- **4 weeks** (annual long trip)

**NOT recommended:** 1 week is too short for India (jet lag alone eats 3-4 days). Don't offer it for India routes — it's a useless option that produces misleading "cheap" prices.

### Leisure destinations

| Destination | Typical duration |
|-------------|-----------------|
| Hawaii | 5–7 days |
| Cancun / Caribbean | 5–7 days |
| Europe (Paris, London) | 7–10 days |
| Dubai | 4–5 days |
| Bali / Southeast Asia | 7–10 days |

**Recommended UI duration options for leisure:** 1 week, 2 weeks.

---

## 4. Day-of-Week Patterns

### Cheapest days to FLY (departure)

- **Tuesday, Wednesday, Thursday** — cheapest
- **Friday, Sunday** — most expensive
- **Monday, Saturday** — moderate

**Savings:** Midweek departures are $80–$220 cheaper than weekend departures on US-India routes. Google Flights data shows ~14% savings for Mon departure / Tue-Wed return vs weekend travel.

### Cheapest day to BOOK

**Doesn't matter.** Multiple 2026 studies confirm the "book on Tuesday" advice is a myth — only ~1.4% difference between cheapest and most expensive booking day. Algorithms reprice constantly.

**UI implication:** Don't show "book on Tuesday" tips — it's noise. DO default the calendar to show Tue-Thu departure options, since that's where the real savings are. If a user picks weekend dates, show a gentle nudge: "Flying Wed instead of Sat saves ~$150."

---

## 5. Booking Lead Time — The Sweet Spot

| Travel period | Book ahead | Notes |
|---------------|------------|-------|
| **Diwali / Christmas** | 120–150 days (4–5 months) | Waiting longer almost always costs more |
| **Summer** | 90–120 days (3–4 months) | — |
| **Off-peak** | 30–60 days | More flexibility; prices stay low longer |
| **Last-minute** | < 14 days | Premium pricing; avoid if possible |

**UI implication:** Show a "book by" date for peak seasons. E.g., for Diwali 2026 (Nov 8): "Book by July for best fares." This is actionable and time-sensitive — it creates urgency without being pushy.

---

## 6. What to Display — UI Recommendations

### Price calendar structure

For each route (e.g., SFO → DEL):

```
[Duration: 2 weeks ▾]  [From: SFO ▾]

  Nov 2026                    Dec 2026
  ┌─────────────────┐        ┌─────────────────┐
  │ 🪔 Diwali week  │        │ 🎄 Christmas    │
  │ Nov 1 → Nov 15  │        │ Dec 20 → Jan 3  │
  │ $1,450 (peak)   │        │ $1,680 (peak)   │
  │ Book by: July   │        │ Book by: Aug    │
  └─────────────────┘        └─────────────────┘
```

**Key design decisions:**

1. **Show date ranges, not just months.** "Nov 1 → Nov 15: $1,450" is useful. "November: $1,450" is not — it could mean Nov 1-3.

2. **Duration selector drives everything.** When user picks "3 weeks," the calendar recalculates the cheapest 21-day window in each month. Options: 2 weeks, 3 weeks, 4 weeks (India). 1 week, 2 weeks (leisure).

3. **Festival markers, not just prices.** A red "$1,450" in November means nothing without "🪔 Diwali week" context. The festival IS the reason for the price.

4. **"Book by" urgency dates.** For each peak period, calculate: peak date minus 120 days = book-by date. Display it. This turns a passive calendar into an active planning tool.

5. **Midweek default.** Default departure/return to Tue-Thu. Show weekend surcharge as a nudge, not a blocker.

6. **Don't show 1-week option for India.** It's a trap — produces artificially low prices for trips nobody takes.

### What NOT to display

- "Cheapest day to book" tips (myth, ~1.4% difference)
- 2+ stop itineraries (Kiran's rule: max 1 stop)
- One-way prices (meaningless for this audience)
- Per-person vs total toggle (Kiran decided: per person, always)

---

## 7. Route Priorities

### India routes (by diaspora population)

**Tier 1 — Build first:**
- SFO → DEL, SFO → BLR
- JFK → DEL, JFK → BOM
- ORD → DEL
- DFW → HYD

**Tier 2:**
- LAX → DEL, SEA → DEL
- EWR → BOM, IAD → DEL
- ATL → DEL, BOS → DEL

**Tier 3:**
- Any US metro → MAA, CCU, COK

### Leisure destinations (from major US metros)

- Hawaii (HNL) — from SFO, LAX, SEA
- Cancun (CUN) — from DFW, IAH, ORD
- London (LHR) — from JFK, BOS
- Paris (CDG) — from JFK, EWR
- Dubai (DXB) — from JFK, SFO
- Bali (DPS) — from SFO, LAX

---

## Sources

- TripBeam fare analysis (tripbeam.com)
- Indian Eagle fare data (indianeagle.com)
- Google Flights 2026 5-year data analysis
- EaseMyTrip 2026 festive travel calendar
- Drik Panchang / Diwali.info (festival dates)
- IndusLadies diaspora community (trip patterns)
- CAIT wedding season data
