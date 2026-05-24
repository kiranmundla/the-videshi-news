# The Videshi — Immigration Section Blueprint
## "The Go-To Source for Indian American Immigration"

---

## 1. SECTION ARCHITECTURE

### URL Structure
```
/immigration                              → Main dashboard (hero + all trackers + latest news)
/immigration/green-card                   → Green Card tracker deep-dive
/immigration/green-card/eb2               → EB-2 India dedicated page (highest search volume)
/immigration/green-card/eb3               → EB-3 India dedicated page
/immigration/green-card/eb1               → EB-1 India dedicated page
/immigration/green-card/family            → Family-based (F1-F4) tracker
/immigration/consulate-wait-times         → All 5 India consulates comparison
/immigration/consulate-wait-times/:city   → Individual city deep-dive (mumbai, delhi, chennai, hyderabad, kolkata)
/immigration/processing-times             → USCIS form processing tracker
/immigration/h1b                          → H-1B hub (lottery, transfer, extensions, cap)
/immigration/guides                       → All guides index
/immigration/guides/:slug                 → Individual guide page
/immigration/news                         → Immigration-specific news feed
/immigration/lawyers                      → Immigration lawyers from directory (filtered)
/immigration/tools/priority-date-tracker  → Personal priority date tracker (enter your date, get alerts)
/immigration/tools/wait-time-calculator   → Estimate your green card wait
```

---

## 2. DATABASE SCHEMA

### Table: `visa_bulletin` (Monthly Visa Bulletin data)
```sql
CREATE TABLE visa_bulletin (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  bulletin_month INT NOT NULL,          -- 1-12
  bulletin_year INT NOT NULL,           -- 2024, 2025, 2026...
  preference_type TEXT NOT NULL,        -- 'employment' or 'family'
  category TEXT NOT NULL,               -- 'EB-1', 'EB-2', 'EB-3', 'EB-3-Other', 'EB-4', 'EB-5-Unreserved', 'EB-5-Rural', 'EB-5-HUA', 'EB-5-Infra', 'F1', 'F2A', 'F2B', 'F3', 'F4'
  chart_type TEXT NOT NULL,             -- 'final_action' or 'dates_for_filing'
  country TEXT NOT NULL,                -- 'india', 'china', 'worldwide', 'mexico', 'philippines'
  priority_date DATE,                   -- NULL = 'C' (current) or 'U' (unavailable)
  status TEXT DEFAULT 'dated',          -- 'dated', 'current', 'unavailable'
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(bulletin_month, bulletin_year, category, chart_type, country)
);

-- Index for fast lookups
CREATE INDEX idx_visa_bulletin_india ON visa_bulletin(country, category, chart_type) WHERE country = 'india';
CREATE INDEX idx_visa_bulletin_month ON visa_bulletin(bulletin_year DESC, bulletin_month DESC);
```

### Table: `visa_bulletin_history` (Tracking movement over time)
```sql
-- This IS the visa_bulletin table — each row is one month's snapshot.
-- We query historically: SELECT * FROM visa_bulletin WHERE country='india' AND category='EB-2' ORDER BY bulletin_year DESC, bulletin_month DESC
-- Movement = diff between consecutive months
```

### Table: `consulate_wait_times` (US consulates in India)
```sql
CREATE TABLE consulate_wait_times (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  consulate TEXT NOT NULL,              -- 'mumbai', 'new_delhi', 'chennai', 'hyderabad', 'kolkata'
  consulate_display TEXT NOT NULL,      -- 'Mumbai (Bombay)', 'New Delhi', etc.
  visa_type TEXT NOT NULL,              -- 'B1B2', 'F_M_J', 'H_L_O_P_Q', 'C_D'
  visa_type_display TEXT NOT NULL,      -- 'Visitor (B1/B2)', 'Student (F/M/J)', 'Work (H/L/O/P/Q)', 'Crew (C/D)'
  avg_wait_months NUMERIC(4,1),        -- Average wait from last month (NULL if NA)
  next_available_months NUMERIC(4,1),  -- Next available appointment (NULL if NA)
  scraped_at TIMESTAMPTZ DEFAULT NOW(),
  source_updated TEXT,                  -- e.g. '18-MAY-2026'
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_consulate_wait ON consulate_wait_times(consulate, scraped_at DESC);
```

### Table: `uscis_processing_times` (Form processing times by service center)
```sql
CREATE TABLE uscis_processing_times (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  form_number TEXT NOT NULL,            -- 'I-140', 'I-485', 'I-765', 'I-131', 'I-130', 'N-400', 'I-539', 'I-129'
  form_name TEXT NOT NULL,              -- 'Immigrant Petition for Alien Workers'
  form_category TEXT,                   -- Sub-category like 'EB-2', 'EB-3' (for I-140)
  office TEXT NOT NULL,                 -- Service center or field office name
  office_code TEXT NOT NULL,            -- 'NSC', 'TSC', 'CSC', 'VSC'
  processing_time_months NUMERIC(4,1), -- 80% of cases completed within
  estimated_range_low NUMERIC(4,1),    -- Lower range
  estimated_range_high NUMERIC(4,1),   -- Upper range
  scraped_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_processing_form ON uscis_processing_times(form_number, office_code, scraped_at DESC);
```

### Table: `immigration_guides` (Evergreen content)
```sql
CREATE TABLE immigration_guides (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  subtitle TEXT,
  category TEXT NOT NULL,               -- 'work-visas', 'green-card', 'citizenship', 'family', 'indian-services', 'student', 'practical'
  content TEXT NOT NULL,                -- Markdown
  meta_description TEXT,
  featured_image TEXT,
  reading_time_min INT,
  last_updated TIMESTAMPTZ DEFAULT NOW(),
  published BOOLEAN DEFAULT true,
  sort_order INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Table: `h1b_data` (H-1B lottery & statistics)
```sql
CREATE TABLE h1b_data (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  fiscal_year INT NOT NULL,             -- FY2026, FY2027
  metric TEXT NOT NULL,                 -- 'total_registrations', 'selected', 'selection_rate', 'india_pct', 'masters_pct', 'cap_regular', 'cap_masters'
  value TEXT NOT NULL,
  source_url TEXT,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(fiscal_year, metric)
);
```

---

## 3. LIVE DATA SOURCES & SCRAPING STRATEGY

### Source 1: Visa Bulletin (Monthly)
- **URL**: `https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2026/visa-bulletin-for-june-2026.html`
- **Format**: HTML tables, well-structured, parseable
- **Data**: Final Action Dates + Dates for Filing for Employment-Based (EB-1 through EB-5) and Family-Sponsored (F1-F4) for India, China, Worldwide, Mexico, Philippines
- **Frequency**: Published ~15th of each month for the following month
- **Scraping**: Parse HTML tables from travel.state.gov; date formats like "01SEP13", "C" (current), "U" (unavailable)
- **Cron**: Check weekly; parse and store when new bulletin detected

### Source 2: Consulate Wait Times (Monthly)
- **URL**: `https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html`
- **Format**: HTML table with all global posts
- **Indian consulates to extract**: Mumbai (Bombay), New Delhi, Chennai (Madras), Hyderabad, Kolkata
- **Data per consulate**: B1/B2 avg wait, B1/B2 next available, F/M/J next available, H/L/O/P/Q next available, C/D next available
- **Frequency**: Updated monthly (last: 18-MAY-2026)
- **Scraping**: Parse the global HTML table, filter to Indian cities
- **Cron**: Weekly check

### Source 3: USCIS Processing Times (Monthly)
- **URL**: `https://egov.uscis.gov/processing-times/`
- **Challenge**: Cloudflare-protected, requires browser-based scraping
- **Fallback**: Scrape from aggregator sites (manifestlaw.com, usvisastack.ai) or manually enter monthly
- **Forms to track for Indians**: I-140, I-485, I-765, I-131, I-130, N-400, I-539, I-129
- **Service centers**: Nebraska (NSC), Texas (TSC), California (CSC), Vermont (VSC), Potomac (PSC)
- **Cron**: Monthly manual update or browser-based scrape

### Source 4: H-1B Cap Data (Annual/Seasonal)
- **URL**: USCIS announcements (uscis.gov)
- **Data**: Registration counts, selection rates, Indian percentage, advanced degree stats
- **Frequency**: Annual (March lottery season), with periodic updates
- **Approach**: Web search + manual curation after each USCIS announcement

### Source 5: Immigration News (Ongoing)
- **Approach**: Add immigration-specific RSS feeds to existing article pipeline
- **Sources**: USCIS news releases, law firm blogs (Fragomen, Ogletree, Wolfsdorf), India media (Hindu Business Line, LiveMint)
- **Tags**: Add "Immigration" as article category in existing pipeline

---

## 4. EVERGREEN GUIDES — FULL CONTENT PLAN

### Category: Work Visas (6 guides)
1. **h1b-visa-complete-guide** — "H-1B Visa: The Complete Guide for Indian Workers"
   - What is H-1B, eligibility, cap/lottery system, FY2027 changes
   - Wage-weighted selection (new 2026 rule), $100K consular fee
   - Timeline: registration → selection → filing → approval → stamping
   - India-specific: 71% of H-1B holders are Indian, consulate stamping in India tips
   - Transfer, extension, amendment processes
   - 60-day grace period after layoff, portability under AC21

2. **h4-ead-work-authorization** — "H-4 EAD: Work Authorization for Dependent Spouses"
   - Who qualifies (I-140 approved or in backlog)
   - Application process (I-765), processing time
   - Current policy under Trump administration (status uncertain)
   - Alternatives if H-4 EAD revoked

3. **l1-visa-intracompany-transfers** — "L-1 Visa: Intracompany Transfers for Indian Professionals"
   - L-1A (managers) vs L-1B (specialized knowledge)
   - Blanket vs individual petition
   - Indian IT companies and L-1 usage
   - Path to green card from L-1

4. **f1-to-h1b-transition** — "F-1 to H-1B: Student to Worker Transition Guide"
   - OPT, STEM OPT extension
   - Cap-gap, day-1 CPT controversies
   - Timeline planning for Indian students

5. **o1-visa-extraordinary-ability** — "O-1 Visa: The Fast Track for Exceptional Indians"
   - Why O-1 is underused by Indians
   - Criteria and evidence strategies
   - No cap, no lottery, faster green card path

6. **eb5-investor-visa** — "EB-5 Investor Visa: A Backdoor for Indians Stuck in EB-2 Backlog"
   - $800K (TEA) or $1.05M investment
   - Set-aside categories still current for India
   - Processing times, regional centers vs direct
   - Compared to 10-15 year EB-2 wait

### Category: Green Card (5 guides)
7. **green-card-employment-based** — "Green Card Through Employment: EB Categories Explained"
   - EB-1A, EB-1B, EB-1C, EB-2 (PERM + NIW), EB-3
   - Per-country caps and why India is screwed
   - I-140 → I-485 process, concurrent filing
   - Consular processing vs adjustment of status (NEW Trump policy: AOS restricted)

8. **eb2-vs-eb3-downgrade** — "EB-2 vs EB-3: Should You Downgrade? The Indian Dilemma"
   - When EB-3 dates are moving faster than EB-2
   - Interfiling/porting priority dates
   - Current June 2026: EB-2 India Sept 2013, EB-3 India Dec 2013
   - Strategy analysis

9. **perm-labor-certification** — "PERM Labor Certification: The First Step to Your Green Card"
   - Employer requirements, recruitment process
   - Processing times (currently 6-12 months)
   - Common pitfalls and audit triggers
   - Prevailing wage and PWD processing

10. **green-card-backlog-survival** — "Surviving the 10-Year Wait: Life in Green Card Limbo"
    - EAD/AP combo card (I-765/I-131)
    - Job changes under AC21 (I-140 180+ days)
    - Aging out of children (CSPA)
    - Mental health and community resources
    - Legislative efforts: Eagle Act, country cap removal

11. **national-interest-waiver** — "EB-2 NIW: Skip PERM and Self-Petition for Your Green Card"
    - No employer needed, self-petition
    - Three-prong test (Dhanasar framework)
    - Popular among Indian researchers, doctors, entrepreneurs
    - Processing time: 6-12 months premium

### Category: Citizenship (2 guides)
12. **naturalization-guide** — "Becoming a US Citizen: Naturalization Guide for Indians"
    - Eligibility (5 years GC, 3 years if married to USC)
    - N-400 process, interview, civics test
    - Dual citizenship: India DOES NOT allow it
    - OCI card after naturalization
    - Impact on Indian property, bank accounts, inheritance

13. **oci-card-guide** — "OCI Card: Everything Indian Americans Need to Know"
    - Who needs it, how to apply
    - Renewal/re-issuance rules (after new passport, at 20 and 50)
    - VFS Global process in US
    - Processing times by consulate (SF, NY, Chicago, Houston, Atlanta)
    - e-Visa vs OCI for parents

### Category: Family Immigration (2 guides)
14. **parent-visitor-visa** — "Getting Your Parents to America: B1/B2 Visitor Visa Guide"
    - Invitation letter template
    - Documents needed
    - Interview tips for Indian consulates
    - 10-year multiple entry strategy
    - Health insurance for visiting parents
    - Super Visa (Canada comparison) mention

15. **family-green-card** — "Sponsoring Family Members for Green Card: What Indians Should Know"
    - F1-F4 categories and current wait times
    - IR (immediate relative) for parents of US citizens
    - Sibling category (F4): 15-20 year wait for India

### Category: Indian Consular Services (3 guides)
16. **indian-passport-renewal** — "Indian Passport Renewal in the US: Complete Guide"
    - VFS Global process
    - Documents, fees ($96-117)
    - Processing by city (SF 2-3 weeks, Chicago 4 weeks)
    - Tatkal (emergency) option

17. **surrender-certificate** — "Indian Passport Surrender Certificate: Do You Need One?"
    - Required for OCI application
    - Online vs in-person process
    - Common mistakes

18. **power-of-attorney-india** — "Managing Indian Property from the US: Power of Attorney Guide"
    - Executing POA in the US for India
    - Apostille requirements
    - Notarization at Indian consulate

### Category: Practical & Financial (4 guides)
19. **tax-implications-nri** — "NRI Tax Guide: Filing in Both US and India"
    - FBAR, FATCA reporting
    - NRE/NRO account rules
    - Tax treaty benefits
    - Common mistakes Indians make

20. **money-transfer-india** — "Sending Money to India: Best Methods Compared (2026)"
    - Wise, Remitly, Western Union, wire transfers
    - Fees, exchange rates, speed comparison
    - Tax implications both sides
    - LRS (Liberalized Remittance Scheme) limits

21. **social-security-india** — "Social Security for Indian Americans: Will You Get Benefits?"
    - 40 quarters requirement
    - Totalization agreement (US-India)
    - Impact if you return to India
    - Medicare eligibility

22. **health-insurance-immigration** — "Health Insurance During Immigration Limbo"
    - Marketplace options during pending AOS
    - H-1B employer coverage
    - Short-term gaps (between jobs, status changes)
    - Travel insurance for India trips

---

## 5. FRONTEND COMPONENTS & PAGES

### Main Dashboard `/immigration`
```
┌──────────────────────────────────────────────┐
│ 🗽 IMMIGRATION HUB                          │
│ "Your Indian American Immigration Dashboard" │
├──────────────────────────────────────────────┤
│                                              │
│ ┌─────── GREEN CARD TRACKER ──────────────┐  │
│ │ EB-1 India: Dec 15, 2022  ▼ -3 months  │  │
│ │ EB-2 India: Sep 1, 2013   ▼ -10 months │  │
│ │ EB-3 India: Dec 15, 2013  ▲ +1 month   │  │
│ │ [View Full Bulletin →]                  │  │
│ └─────────────────────────────────────────┘  │
│                                              │
│ ┌─────── CONSULATE WAIT TIMES ────────────┐  │
│ │ 🟢 Chennai    — B1/B2: 5.5mo  H/L: NA  │  │
│ │ 🟡 Kolkata    — B1/B2: 4.5mo  H/L: 1mo │  │
│ │ 🟠 New Delhi  — B1/B2: 5.5mo  H/L: 2mo │  │
│ │ 🔴 Hyderabad  — B1/B2: 6.5mo  H/L: 3mo │  │
│ │ 🔴 Mumbai     — B1/B2: 7.5mo  H/L:1.5mo│  │
│ │ [Compare All Consulates →]              │  │
│ └─────────────────────────────────────────┘  │
│                                              │
│ ┌─────── H-1B SEASON ────────────────────┐   │
│ │ FY2027: 211,600 registrations          │   │
│ │ Selection rate: ~40%  (↑ from 35% FY26)│   │
│ │ 71.5% hold US Master's or higher       │   │
│ │ [H-1B Hub →]                           │   │
│ └────────────────────────────────────────┘   │
│                                              │
│ ┌─────── PROCESSING TIMES ───────────────┐   │
│ │ I-140 (EB-2): 3-17 months              │   │
│ │ I-485 (AOS):  8-24 months              │   │
│ │ I-765 (EAD):  3-7 months               │   │
│ │ N-400 (Citizenship): 8-14 months       │   │
│ │ [All Processing Times →]               │   │
│ └────────────────────────────────────────┘   │
│                                              │
│ ┌─────── QUICK LINKS (Guides) ───────────┐   │
│ │ [H-1B Guide] [Green Card] [OCI Card]   │   │
│ │ [Parent Visa] [NRI Taxes] [EB-2 vs EB-3│   │
│ └────────────────────────────────────────┘   │
│                                              │
│ ┌─────── BREAKING: Immigration News ─────┐   │
│ │ • Trump ends AOS for temp visa holders  │   │
│ │ • EB-2 India retrogresses 10 months     │   │
│ │ • H-1B FY2027 lottery complete          │   │
│ │ [More Immigration News →]               │   │
│ └────────────────────────────────────────┘   │
│                                              │
│ ┌─────── FIND A LAWYER ──────────────────┐   │
│ │ 🔍 Immigration lawyers near you         │   │
│ │ [Browse 174 Attorneys →]                │   │
│ └────────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

### Green Card Deep Dive `/immigration/green-card`
- Historical priority date charts (12-24 month line chart per category)
- Movement analysis: "EB-2 India moved -10.5 months this bulletin"
- EB-2 vs EB-3 comparison chart (which is moving faster?)
- Prediction: "At current pace, EB-2 India reaching 2015 could take X months"
- Tabs: EB-1 | EB-2 | EB-3 | EB-5 | Family-Based
- Individual EB pages with dedicated analysis

### Consulate Wait Times `/immigration/consulate-wait-times`
- Side-by-side comparison card for all 5 cities
- Bar chart: wait times by visa type across cities
- Color-coded: green (<2mo), yellow (2-5mo), red (>5mo)
- Recommendation: "For H/L stamping, Kolkata is currently fastest at 1 month"
- Tips for each consulate (what to bring, parking, nearby hotels)
- Also include: Dubai, Singapore, Toronto (popular for Indians doing third-country stamping)

### H-1B Hub `/immigration/h1b`
- Current cap season status
- Historical lottery data (FY2024-FY2027)
- Wage-weighted changes explained
- Links to relevant guides

---

## 6. CRON/REFRESH STRATEGY

| What | Cron | Frequency | Notes |
|------|------|-----------|-------|
| Visa Bulletin scraper | `videshi-visa-bulletin` | Weekly (check for new bulletin ~15th of month) | Parse travel.state.gov HTML |
| Consulate wait times | `videshi-consulate-waits` | Weekly | Parse travel.state.gov global wait times page |
| USCIS processing times | Manual + cron attempt | Monthly | Cloudflare blocks; may need browser or manual |
| H-1B cap data | Manual | Seasonal (March-April) | From USCIS announcements |
| Immigration news | Add to existing `videshi-writer` | Every 3h (existing cadence) | Add immigration RSS feeds |

---

## 7. SEO STRATEGY — HIGH VALUE KEYWORDS

| Keyword | Monthly Volume (est.) | Our Page |
|---------|----------------------|----------|
| eb2 india priority date | 50,000+ | /immigration/green-card/eb2 |
| green card india wait time | 30,000+ | /immigration/green-card |
| h1b visa 2026 | 100,000+ | /immigration/h1b |
| us visa appointment wait time india | 20,000+ | /immigration/consulate-wait-times |
| uscis processing times | 50,000+ | /immigration/processing-times |
| h4 ead news | 15,000+ | /immigration/guides/h4-ead |
| oci card renewal | 15,000+ | /immigration/guides/oci-card |
| parent visa usa from india | 10,000+ | /immigration/guides/parent-visitor-visa |
| indian passport renewal usa | 8,000+ | /immigration/guides/indian-passport-renewal |
| eb2 vs eb3 india | 5,000+ | /immigration/guides/eb2-vs-eb3 |
| nri tax guide | 5,000+ | /immigration/guides/tax-implications-nri |
| send money to india | 20,000+ | /immigration/guides/money-transfer-india |

**Total addressable search volume: 300,000+ monthly searches**

---

## 8. BUILD ORDER

### Phase 1: Data Foundation (Day 1)
1. Create all Supabase tables
2. Build Visa Bulletin scraper → seed with June 2026 data + historical (last 12 months)
3. Build consulate wait times scraper → seed with current data
4. Seed USCIS processing times (manual from search results)
5. Seed H-1B data (FY2025, FY2026, FY2027)

### Phase 2: Main Dashboard + Green Card Tracker (Day 1-2)
6. Build ImmigrationPage.tsx (main dashboard)
7. Build GreenCardTracker component (the star of the show)
8. Build ConsulateWaitTimes component
9. Build ProcessingTimes component
10. Wire routes in App.tsx

### Phase 3: Deep Dive Pages (Day 2-3)
11. Green Card deep dive with historical charts
12. Individual EB category pages
13. Consulate comparison page
14. H-1B hub page
15. Processing times detailed page

### Phase 4: Guides (Day 3-5)
16. Write top 5 most-searched guides first:
    - H-1B Complete Guide
    - Green Card Employment-Based
    - OCI Card Guide
    - Parent Visitor Visa
    - EB-2 vs EB-3
17. Write remaining 17 guides in batches

### Phase 5: Automation (Day 5+)
18. Set up Visa Bulletin cron (weekly)
19. Set up consulate wait times cron (weekly)
20. Add immigration category to article pipeline
21. SEO: sitemap, JSON-LD, meta descriptions

---

## 9. MONETIZATION

- **Immigration lawyer ads**: $50-200 CPC (highest-value ad category)
- **Premium featured lawyer listings** in directory
- **Affiliate: VFS Global, Wise (money transfer)**
- **Consultation booking referrals**
- **Premium tool: priority date email alerts** (free → email capture)
- **Sponsored content from law firms**

---

## 10. COMPETITIVE MOAT

**Why The Videshi beats existing sources:**
- **Trackitt**: Community forums, ugly UI, no curated analysis
- **AM22Tech**: Decent but not comprehensive, no live dashboards
- **USCIS.gov**: Official but impossible to navigate
- **Law firm blogs**: Analysis but fragmented, each pushing their services
- **ImmiHelp**: Outdated UI, no live data

**The Videshi advantage:**
- Single dashboard with ALL live data (bulletin + waits + processing)
- Indian-diaspora lens on every guide (not generic immigration content)
- Beautiful, mobile-first UI (same quality as rest of the site)
- Integrated with directory (find a lawyer) and events (community)
- AI-generated news analysis with NRI angle
- Historical tracking and trend visualization
