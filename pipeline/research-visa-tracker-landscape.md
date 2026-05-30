# Visa Consulate Appointment Tracker — Landscape Research

*Research date: May 30, 2026*

---

## 1. Current Landscape: Existing Tools & Services

### A. CheckVisaSlots (checkvisaslots.com)
- **What it is**: Community-driven, crowdsourced screenshot-sharing platform. Users voluntarily share screenshots of appointment availability they see on the official booking site.
- **Data source**: NOT scraped from the booking system. Users manually contribute screenshots from their own logged-in sessions on ustraveldocs.com / usvisascheduling.com. The platform aggregates these community contributions.
- **Pricing**: 
  - Free tier: See slot availability data, both OFC (biometrics) and consular appointments
  - Paid alerts: Email/push alerts when slots open in your preferred window. Price not publicly listed — likely ₹500–₹2,000 range based on app store reviews
  - "Book My Visa Slot" concierge service: They also offer to book slots on your behalf (higher-risk service)
- **App**: Google Play — 50K+ downloads, 3.4 rating, 148 reviews. Run by Twippy Tech Pvt. Ltd.
- **API**: Provides API keys to developers (used by USVisaSlotsChecker GitHub project)
- **Limitations**: 
  - Data quality depends entirely on community participation — gaps when nobody contributes
  - Alerts are based on crowdsourced data, not real-time system monitoring
  - "Book My Visa Slot" service is high-risk (credential sharing, ToS violation territory)
  - India-only alerts currently; other countries not yet supported

### B. WaitDelta (waitdelta.com)
- **What it is**: Wait time intelligence dashboard. Tracks official State Department wait times, provides comparisons across India's 5 consulates, historical trends, and strategy guides.
- **Data source**: U.S. Department of State's Global Visa Wait Times page (travel.state.gov). Scraped/tracked daily via automated pipeline.
- **Pricing**: Appears to be **free**. No visible subscription or paywall. Content-driven (strategy guides, blog posts).
- **Features**:
  - Side-by-side consulate comparison (Delhi vs Mumbai vs Chennai vs Hyderabad vs Kolkata)
  - Wait times by visa type (F-1, B1/B2, H-1B, L-1)
  - Average wait time calculations
  - Strategy guides (e.g., "US Visa Appointment Slot Strategy India 2026")
  - "Updated monthly" from official source
- **Limitations**:
  - Only shows official wait times — not real-time slot availability
  - Monthly updates mean data can be 2-4 weeks stale
  - No alerts, no community data
  - Purely informational, no actionable slot notifications

### C. Open-Source Bots (GitHub)
Multiple GitHub projects automate slot checking. Key ones:

| Project | Stars | Method | Risk Level |
|---------|-------|--------|------------|
| USVisaSlotsChecker (Abhishekkataria16) | Active | Uses CheckVisaSlots API, checks every 3 min | Medium (relies on CVS API) |
| us-visa-bot (jeangnc) | Active | Logs into ais.usvisa-info.com, auto-reschedules | **High** (credential sharing, auto-booking) |
| visa_checker (Niteshd7) | Apr 2026 | Uses Patchright to bypass Cloudflare, Telegram alerts | **High** (bot detection bypass) |
| usvisa-ca (kcajc) | Mar 2026 | Python script for Canada, uses ais.usvisa-info.com | **High** (credential sharing) |
| usa-visa-appointment-checker | Active | PowerShell, logs into ais.usvisa-info.com | **High** (credential sharing) |

**Key insight from the Niteshd7 Medium post**: Cloudflare bot detection on the visa scheduling site is aggressive. Standard headless browsers (Playwright, Puppeteer) are detected. The developer had to use **Patchright** (a patched Chromium binary) to bypass fingerprinting. This means scraping the booking site directly is a cat-and-mouse game with increasingly sophisticated anti-bot measures.

### D. Telegram / WhatsApp Groups
- Dozens of community Telegram groups exist for visa slot alerts (e.g., F1 visa groups, H-1B groups)
- Members manually report slot sightings in real-time
- Some Telegram bots auto-forward filtered messages (e.g., hppanpaliya/telegram-f1-visa-tracker)
- **Pros**: Real-time, human-verified, low-risk (no scraping)
- **Cons**: Noisy, unstructured, no historical data, hard to search/filter, fragmented across many groups

### E. Trackitt (trackitt.com)
- Long-standing immigration forum/community
- Users self-report visa processing timelines, interview experiences, appointment dates
- Discussion forums organized by visa type and consulate
- **Pros**: Deep historical data, community trust
- **Cons**: Forum format is antiquated, hard to extract structured data, no real-time alerts

### F. Visard Bot (visard.io) — Schengen, not US, but instructive model
- Telegram bot for Schengen visa appointments (VFS/TLScontact)
- **Pricing model**: 
  - Notifications only: one-time payment for 31 days of monitoring
  - Auto-booking: £100 for first applicant + £50 per additional, paid ONLY after successful booking
- UK-registered company, Stripe payments, GDPR compliant
- Relevant as a monetization template

### G. Visa Slot Scalpers / Agents
- Companies (often on social media/Facebook) offer to book slots for $100–$1,000
- They monitor 24/7 and bulk-book when slots appear
- "Payment after slot confirmation only" — success-based pricing
- This is explicitly against ToS and creates artificial scarcity
- US State Department and immigration lawyers have flagged this as a problem

---

## 2. Data Sources We Can Legally Use

### A. State Department Global Visa Wait Times ✅ FULLY LEGAL
- **URL**: `https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html`
- **Format**: Single HTML page with one large table, ~250+ rows (one per consulate worldwide)
- **Update frequency**: Monthly (last updated 18-MAY-2026 as of research date)
- **Data columns**:
  - City/Post
  - B1/B2: Average wait times (months)
  - B1/B2: Next available appointment (months)
  - F,M,J: Next available appointment (months)
  - Petition-Based (H,L,O,P,Q): Next available appointment (months)
  - Crew & Transit (C,D,C1/D): Next available appointment (months)
- **India-specific data (as of May 18, 2026)**:
  - Chennai: B1/B2 avg 5.5mo, next appt NA for most categories
  - Hyderabad: B1/B2 avg 6.5mo, next 7mo; H/L 3mo
  - Kolkata: B1/B2 avg 4.5mo, next 7mo; F/M/J 3.5mo
  - Mumbai: B1/B2 avg 7.5mo, next 7.5mo; H/L 1.5mo
  - New Delhi: B1/B2 avg 5.5mo, next 8mo; H/L 2mo
- **Scraping feasibility**: Simple HTML table, easily parseable. Public government data, no ToS restrictions on reading public web pages. No API, but straightforward to scrape.
- **April 2025 redesign note**: State Dept redesigned the page in April 2025. Now shows "average wait time" (for B1/B2 only when > 3 months) AND "next available appointment". Data is more granular than before.
- **Calculation method**: Months = 30-day increments, half-months = 15-day increments, includes weekends/holidays.

### B. Embassy/Consulate X/Twitter Accounts ⚠️ LEGAL BUT IRREGULAR
- **@USAndIndia** — main US Embassy India account
- Individual consulate accounts exist but are less active
- **What they announce**: 
  - Policy changes (social media screening, rescheduling notices)
  - Batch appointment release announcements (irregular)
  - Emergency notices (government shutdown impacts, holiday closures)
  - General advisories
- **Frequency**: Not systematic. They do NOT announce every batch release. Announcements are event-driven (policy changes, crises).
- **Example tweets**: 
  - Dec 2025: "ATTENTION VISA APPLICANTS – If you have received an email advising that your visa appointment has been rescheduled..."
  - Apr 2026: Resumed releasing H-1B, H-4, F-1 slots in small batches after months of delays
- **Monitoring approach**: Can set up a cron to monitor these accounts for keyword-matched tweets. Low volume, high signal.

### C. NVC Timeframes (travel.state.gov) ✅ FULLY LEGAL
- `https://travel.state.gov/content/travel/en/us-visas/immigrate/nvc-timeframes.html`
- Updated weekly
- Covers immigrant visa processing timelines
- Relevant for EB-2/EB-3 green card backlog tracking (huge NRI concern)

### D. Visa Bulletin (travel.state.gov) ✅ FULLY LEGAL
- Monthly visa bulletin with priority date cutoffs
- Critical for EB-2/EB-3 India tracking
- Available as structured data

### E. ustraveldocs.com / usvisascheduling.com ❌ HIGH RISK
- This is the actual appointment booking portal, operated by CGI Federal under contract with DOS
- **ToS restrictions**: 
  - Requires authenticated login (you need a paid MRV receipt to see appointment dates)
  - No public API
  - Anti-bot measures: Cloudflare protection, CAPTCHA, rate limiting
  - Multiple GitHub projects have been built to scrape it — requires Patchright or similar anti-detection tools
  - Accounts can be **permanently suspended** if automation is detected
- **Legal risk**: Not just ToS violation — CFAA (Computer Fraud and Abuse Act) implications for unauthorized automated access
- **Our approach**: DO NOT scrape or interact with this system. Period.

### F. Public State Department APIs ❌ NONE EXIST
- The State Department does not offer a public API for visa wait times or appointment availability
- All data is published as HTML on travel.state.gov
- The CEAC status check system has some query capabilities but is for individual case tracking, not bulk data

---

## 3. User Pain Points (from Reddit, forums, news)

### Top complaints:

1. **"No visibility into when slots will open"** — The booking system shows "no appointments available" with zero indication of when new slots might appear. Users refresh obsessively.

2. **"Abrupt cancellations with months-long delays"** — Dec 2025/Jan 2026 crisis: hundreds of H-1B holders had appointments cancelled due to new social media screening policy. Rescheduled to March-July 2026. People stranded in India, unable to return to US jobs.

3. **"No way to compare consulates easily"** — Users don't know which consulate is fastest. They have to manually check each one. WaitDelta helps but only shows monthly snapshots, not real-time.

4. **"Wednesday midnight ritual"** — Community wisdom says slots release Wednesday 11 PM – 1 AM IST. Users stay up all night refreshing. No official confirmation this is real.

5. **"Scalpers are taking all the slots"** — Agents and bots bulk-book slots, creating artificial scarcity. Regular applicants can't compete with automated systems. Slots that appear are gone in seconds.

6. **"F-1 free reschedule limit"** — Since Jan 2026, F-1 applicants only get 1 free reschedule (2nd costs full $185 again). Creates pressure to book the "right" slot the first time.

7. **"Social media vetting anxiety"** — Dec 2025 policy: all H-1B/H-4 applicants must make social media public. People scrubbing old posts, worried about years-old tweets. Adds weeks to processing time.

8. **"No historical data to plan around"** — Users want to know: "Is June usually better than August for Chennai H-1B slots?" Nobody tracks this systematically at a granular level.

9. **"Third-country processing confusion"** — Some users consider getting stamped at a different country's consulate. But rules vary, some consulates restrict TCN processing seasonally. No central resource.

10. **"Admin processing black hole"** — After interview, some cases go into "administrative processing" (221(g)) with zero visibility into timeline. Can be weeks or months.

---

## 4. Monetization Models

### What competitors charge:

| Service | Model | Price |
|---------|-------|-------|
| CheckVisaSlots (alerts) | Subscription | Estimated ₹500–₹2,000 ($6–$24) |
| CheckVisaSlots (booking assist) | Per-booking | Not publicly disclosed; likely ₹5,000–₹15,000 ($60–$180) |
| Visa scalpers/agents | Per-slot | $100–$1,000 (illegal/gray market) |
| Visard (Schengen model) | Per-booking, success-based | £100/$100 first applicant + £50/$50 additional |

### What The Videshi could offer:

**Free tier (traffic + audience building):**
- Wait time dashboard with historical trends (public State Dept data)
- Strategy guides and editorial content
- Community sighting feed (read-only)
- Embassy Twitter/X announcement monitoring

**Freemium tier ($5–$10/month):**
- Email/WhatsApp alerts when community reports slots opening at your consulate + visa type
- Weekly digest of wait time changes and trends
- Personalized "best consulate for you" recommendation based on visa type and urgency
- 221(g) processing time community data

**Premium tier ($15–$25/month):**
- Real-time push notifications (sub-minute delivery) for slot sightings
- Historical trend analytics (seasonal patterns: "when is the best month to apply")
- Multi-consulate monitoring (all 5 India + popular TCN consulates like Singapore, Bangkok)
- Priority access to strategy guides and immigration lawyer Q&A sessions

**NOT recommended:**
- Concierge booking service — ToS violation, legal risk, reputation risk
- Direct slot checking/scraping — CFAA risk, anti-bot arms race
- Any service that requires user credentials

---

## 5. Legal & ToS Risks

### Safe zone ✅
- Scraping travel.state.gov (public government website, updated monthly)
- Monitoring embassy Twitter/X accounts (public posts)
- Community-sourced reports (users voluntarily share what they see)
- Editorial content and strategy guides
- NVC timeframes and Visa Bulletin tracking

### Gray zone ⚠️
- Using CheckVisaSlots API to build on top of their crowdsourced data — depends on their API ToS
- Building tools that encourage users to share screenshots from the booking portal — we're not scraping, but we're systematizing access to data behind a login wall

### Red zone ❌
- Scraping ustraveldocs.com or usvisascheduling.com — authenticated access, Cloudflare-protected, explicitly ToS-violating, potential CFAA liability
- Offering to book slots on users' behalf — requires their credentials, ToS violation, account suspension risk
- Using bots to hold/release slots — creates artificial scarcity, potentially illegal
- Any automation that bypasses anti-bot measures (Patchright, undetected-chromedriver, etc.)

### Has anyone been shut down?
- No publicized legal cases specifically against visa slot scrapers
- BUT accounts have been permanently suspended on ustraveldocs.com for automated access
- CGI Federal (the portal operator) has progressively added anti-bot measures (Cloudflare, CAPTCHA, rate limiting)
- The State Department has publicly acknowledged the scalper problem but hasn't taken direct legal action against scrapers
- The WaitDelta/CheckVisaSlots model (using only public or crowdsourced data) has operated for years without legal issues

---

## 6. Recommended Approach for The Videshi

### Phase 1: Wait Time Dashboard + Community Feed (MVP)
Build a page/section that:
1. **Scrapes travel.state.gov monthly** — store historical wait times for India's 5 consulates across all visa types. Show trend charts (are wait times going up or down?).
2. **Community slot sighting feed** — simple structured form: "I just saw [visa type] slots at [consulate] for [date range]." No login required, email verification only. Display as a real-time feed.
3. **Embassy Twitter monitor** — cron watches @USAndIndia for appointment-related tweets, auto-posts to the feed.
4. **Strategy guides** — editorial content: which consulate to target, Wednesday midnight tips, free reschedule rules, third-country processing guide.

### Phase 2: Alerts (Monetization)
5. **Email/WhatsApp alerts** — users subscribe to consulate + visa type. When a community sighting matches, send alert. Free for daily digest, paid for instant alerts.

### Phase 3: Intelligence Layer
6. **Seasonal analysis** — "Based on 12 months of data, Chennai H-1B wait times peak in June and dip in September"
7. **TCN consulate comparison** — compare India wait times vs Singapore, Bangkok, Dubai for TCN processing
8. **EB-2/EB-3 backlog tracker** — monthly visa bulletin tracking with India-specific priority date movement charts

### Key principles:
- **Self-owned data only** — no scraping the booking portal
- **Community-powered** — users voluntarily report what they see
- **Editorial layer** — strategy guides and analysis that bots can't replicate
- **Trust** — don't sell booking services, don't touch credentials
- **Audience fit** — The Videshi already has the exact audience that needs this

---

## 7. Latest India Consulate Wait Times (as of May 18, 2026)

| Consulate | B1/B2 Avg | B1/B2 Next | F/M/J Next | H/L/O/P/Q Next | C/D Next |
|-----------|-----------|------------|------------|----------------|----------|
| Chennai | 5.5 mo | NA | NA | NA | NA |
| Hyderabad | 6.5 mo | 7 mo | 2.5 mo | 3 mo | < 0.5 mo |
| Kolkata | 4.5 mo | 7 mo | 3.5 mo | 1 mo | NA |
| Mumbai | 7.5 mo | 7.5 mo | 2 mo | 1.5 mo | 1 mo |
| New Delhi | 5.5 mo | 8 mo | 2 mo | 2 mo | 1 mo |

**Notable**: Chennai shows NA for "next available appointment" across most categories — meaning they're not currently releasing new appointment slots in those categories. This is likely related to the ongoing social media screening capacity constraints.
