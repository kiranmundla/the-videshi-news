#!/usr/bin/env python3
"""Markets & Finance writer — 2026-07-10 17:00 PDT run."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ── Article 1: Dr. Reddy's Semaglutide Crisis ──

art1_body = """Dr. Reddy's Laboratories, the Hyderabad-based pharma giant, is closing out what may be its worst week in three years — and the culprit is a drug that was supposed to be its ticket to the next phase of growth.

Shares of Dr. Reddy's (NSE: DRREDDY) fell as much as 9.3% over the five trading sessions ending July 10, after the company disclosed that an impurity in the active pharmaceutical ingredient (API) of its generic semaglutide had forced it to halt production of new batches. Commercial supplies of the drug — marketed in India under the brand name Obeda — will remain unavailable domestically and disrupted in Canada until at least late October.

The timing could not be worse. Semaglutide, the compound behind Novo Nordisk's blockbuster Ozempic and Wegovy brands, went off-patent in India in March, triggering a race among domestic drugmakers to capture a piece of what analysts project as a multi-billion-dollar opportunity globally. Dr. Reddy's had positioned itself as the first mover, launching Obeda ahead of competitors. That advantage is now evaporating.

## The damage in numbers

At least five brokerages have slashed their price targets on Dr. Reddy's since the announcement, according to LSEG data. Three have cut earnings estimates outright. The stock closed Friday at ₹1,246.50 — its weakest in months — making it the Nifty 50's second-worst performer of the week.

Bank of America analysts warned that the timing of supply resumption would be critical, noting the setback could prevent Dr. Reddy's from capturing high-value volumes during a limited-competition window in Canada, where the company had fought through regulatory hurdles to secure early market access.

"The first-mover advantage looks like it is no more," said Shrikant Akolkar, pharma analyst at Nuvama Institutional Equities.

## Competitors smell blood

The supply vacuum is a gift to rivals. Zydus Lifesciences and Sun Pharmaceutical Industries, both of which have launched competing generic semaglutide versions in India, stand to gain market share during Obeda's absence. On Friday, Torrent Pharmaceuticals announced it was voluntarily recalling select batches of its Semalix semaglutide pens — manufactured by Dr. Reddy's — after the same API quality issue surfaced downstream.

India has the world's second-largest diabetic population, making the domestic semaglutide market alone a substantial prize. But the real revenue play was always international. Dr. Reddy's had been eyeing launches in Canada, Brazil, and Turkey as semaglutide patents expire market by market. The impurity issue now jeopardizes that entire rollout timeline.

Systematix analysts noted that competition is intensifying across every target market, and Dr. Reddy's window to establish dominance may be closing.

## What this means for NRI investors

For NRI investors with exposure to Indian pharma — either through direct holdings or mutual funds with significant healthcare allocations — the Dr. Reddy's stumble is a reminder that the GLP-1 opportunity, while enormous, carries real execution risk.

The broader Indian pharma sector remains structurally attractive. India's generic manufacturing base gives it a natural advantage as GLP-1 patents expire globally, and multiple Indian companies are pursuing approvals across dozens of markets. But the Dr. Reddy's episode shows that API quality, regulatory approvals, and supply chain reliability matter as much as being first to file.

Investors watching this space should monitor three developments: whether Dr. Reddy's can resume production by October as promised, how aggressively Zydus and Sun expand in the interim, and whether Brazil's regulator — which previously denied Dr. Reddy's semaglutide registration on technical grounds — reopens the door.

The GLP-1 wave is real. But riding it requires more than ambition — it demands flawless manufacturing execution in a segment where the active ingredient itself costs more per gram than gold."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Dr. Reddy's Posts Worst Week in Three Years as Semaglutide Supply Crisis Hands Rivals the GLP-1 Prize",
    "subheadline": "An impurity in the active ingredient has halted production of Obeda until at least late October, eroding the first-mover advantage that was central to Dr. Reddy's growth thesis — and opening the door for Zydus and Sun Pharma.",
    "slug": make_slug("dr-reddys-semaglutide-supply-crisis-worst-week-nri-pharma"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRI investors with Indian pharma exposure face a strategic question: is the Dr. Reddy's dip a buying opportunity or a signal that GLP-1 execution risk is underpriced across the sector?",
    "tags": ["markets", "finance", "pharma", "dr-reddys", "semaglutide", "glp-1", "nri-investing", "indian-pharma"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-dr-reddys-set-worst-week-3-years-semaglutide-setback-fuels-growth-concerns-2026-07-10/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/companies/dr-reddys-delays-semaglutide-supplies-after-api-related-quality-issue/article69780742.ece"},
        {"name": "Reuters - Supply Disruption", "url": "https://www.reuters.com/world/india/indias-dr-reddys-sees-semaglutide-supply-disruption-lasting-until-least-late-2026-07-09/"},
        {"name": "Reuters - Torrent Recall", "url": "https://www.reuters.com/world/india/indias-torrent-pharma-recalls-select-semaglutide-pens-after-dr-reddys-notice-2026-07-10/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Ozempic%C2%AE_3ml.jpg/1280px-Ozempic%C2%AE_3ml.jpg",
    "image_caption": "A semaglutide injection pen — the drug at the center of Dr. Reddy's supply crisis",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}

# ── Article 2: Rupee and Goldman Sachs Forecast ──

art2_body = """Goldman Sachs just upgraded its rupee outlook for the second time in three months — and for once, the revision is in NRIs' favor.

The Wall Street bank now expects the dollar-rupee pair to settle at 94, 95, and 96 at the three-, six-, and twelve-month horizons, respectively. That is a notable improvement from its previous forecast of 96, 96, and 97, and a world away from the panic-driven predictions of a rupee at 100 that dominated markets when the currency hit its record low of 96.97 per dollar on May 20.

The revision comes at a pivotal moment. The rupee just endured another week of geopolitical whiplash — sliding to 95.86 per dollar on July 8 after U.S. President Donald Trump declared the ceasefire with Iran "over," then clawing back to 95.39 by Thursday as RBI intervention and a dip in Brent crude prices restored calm. One-month implied volatility has ticked up to 5.3% from 4.9% a week earlier, but traders say the rupee's worst days may be behind it.

## What changed

Three structural shifts underpin Goldman's upgraded outlook.

First, the Reserve Bank of India's June policy blitz. The central bank and government rolled out a suite of measures to attract foreign capital: tax exemptions on foreign investments in government securities, expanded access to Indian bonds through the Fully Accessible Route, and exemptions for banks raising foreign-currency deposits. Analysts estimate these steps could attract $40 billion to $80 billion in fresh inflows over the coming quarters.

Second, the unwinding of rate-hike bets. Investors who had accumulated sizeable positions expecting a series of front-loaded RBI rate hikes — driven by inflation fears and rupee weakness — are now aggressively reversing course. Turnover in the five-year overnight index swap market hit a record 253 billion rupees ($2.65 billion) on July 8, nearly three times the daily average, as traders scrambled to close bearish positions.

Third, foreign bond buying. Global investors have plowed 76 billion rupees ($796 million) into the benchmark 2036 Indian government bond over the past two weeks alone, betting on potential inclusion in the Bloomberg Global Aggregate Index. That structural demand provides a floor for the rupee that did not exist six months ago.

## The RBI's invisible hand

State-run banks were spotted offering dollars early in Thursday's session — the telltale sign of coordinated RBI intervention — and broader dollar selling picked up once the rupee held above the psychologically important 95.50 mark.

The central bank's strategy has shifted from defending an absolute level to engineering a plateau. As Goldman analyst Kamakshya Trivedi put it: "We envisage a plateau in the USD/INR cross rate." The RBI is not trying to push the rupee stronger. It is absorbing incoming dollars to rebuild its reserve buffer — which had been depleted during the rupee's slide from 85 to nearly 97 — while keeping the currency stable enough to prevent a new wave of speculation.

Corporate India is reading the same signals. Foreign exchange hedging hit a record $120 billion in June, with exporters sharply increasing protection after the RBI's measures tempered expectations of a continued rupee slide.

## What this means for NRIs sending money home

For NRIs remitting money to India, the math has shifted. At the current rate of roughly 95.4 per dollar, remitters are still getting significantly more rupees per dollar than a year ago, when the rate hovered around 85. But if Goldman's three-month forecast of 94 materializes, the window for favorable remittance rates is narrowing.

The practical calculus depends on individual timelines. NRIs planning large transfers for property purchases, family support, or NRE fixed deposits may find the current 95+ rate more attractive than what could be available later this year if inflows accelerate and the RBI allows modest appreciation.

NRE fixed deposit rates remain compelling — several banks offer 7%+ on one-year deposits denominated in rupees, and the interest is tax-free for NRIs. Locking in at the current exchange rate and high deposit rates offers a dual tailwind that may not last.

For those with longer horizons, Goldman's 12-month forecast of 96 suggests the depreciation trade is not dead — just capped. Geopolitical risk from the Middle East, oil prices, and Fed policy remain wildcards that could push the rupee back toward 96-97 temporarily.

The bottom line: the rupee's floor is rising, the structural supports are real, and the panic premium has evaporated. For NRI investors and remitters, the question is no longer whether the rupee will crash to 100 — it almost certainly will not. The question is how long the current 95+ window stays open."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Goldman Sachs Upgrades Rupee Forecast to 94 — What NRIs Should Know Before the Remittance Window Closes",
    "subheadline": "The Wall Street bank sees the dollar-rupee pair plateauing as RBI measures, record bond inflows, and an unwind of rate-hike bets reshape the currency outlook. For NRIs, the 95+ remittance rate may not last.",
    "slug": make_slug("goldman-sachs-rupee-forecast-94-nri-remittance-window"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRIs sending money home face a narrowing window: the rupee's current 95+ rate may tighten toward 94 if Goldman's forecast plays out. NRE deposit rates at 7%+ tax-free amplify the urgency.",
    "tags": ["markets", "finance", "rupee", "dollar", "goldman-sachs", "nri-remittance", "rbi", "exchange-rate", "nre-deposits"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/currencies/rupee-hits-three-week-low-firmer-dollar-ndf-maturities-pinch-2026-07-07/"},
        {"name": "Reuters - RBI Intervention", "url": "https://www.reuters.com/markets/currencies/central-bank-intervention-oil-price-dip-help-rupee-edge-modestly-higher-2026-07-09/"},
        {"name": "Reuters - Record Swaps", "url": "https://www.reuters.com/markets/rates-bonds/foreign-investors-pare-india-rate-hike-bets-fuel-record-5-year-swaps-trading-2026-07-08/"},
        {"name": "The Hindu BusinessLine - Goldman Sachs", "url": "https://www.thehindubusinessline.com/markets/forex/goldman-sees-rupee-weakness-capped-after-steps-to-boost-inflows/article69656543.ece"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Indian_currency-1.jpg/1280px-Indian_currency-1.jpg",
    "image_caption": "Indian rupee currency notes — NRIs face a narrowing window for favorable remittance rates",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}

# ── Article 3: India's Q1 Earnings Season and JP Morgan 27,000 Target ──

art3_body = """India's earnings season just fired its opening salvo — and if TCS is any indication, the bears may need to revise their thesis.

Tata Consultancy Services, India's largest IT services company by market capitalization, reported Q1 FY27 revenue of ₹722.75 billion ($7.58 billion), beating analyst estimates and adding 9,300 employees in its largest quarterly hiring spree in over three years. The results helped lift the Nifty IT index 2% on Friday, led the broader market to close the week on a high note, and gave J.P. Morgan's equity strategists confidence to reiterate their year-end Nifty 50 target of 27,000 — implying 11.5% upside from Friday's close.

But the real story is not TCS. It is whether India's corporate sector can collectively deliver the revenue growth that justifies keeping the market's premium valuation intact after a week that tested every nerve.

## The week the market survived

By any measure, this was a bruising week for Indian equities. On Tuesday, markets were flirting with 10-week highs after a four-session rally. By Wednesday, the Sensex had cratered 1,677 points — its steepest single-day fall in three months — after Trump declared the Iran ceasefire "over," triggering fresh U.S. military strikes that sent Brent crude surging to $78-79 per barrel.

By Friday, the Nifty had clawed back to 24,206.90, up 1.02% on the day, trimming the weekly loss to just 0.3%. The Sensex closed at 77,569.39, recovering virtually all the ground lost in Wednesday's rout.

Foreign institutional investors, who had been net sellers for much of the year, turned buyers for four of the last five sessions, investing ₹1,963 crore on Wednesday alone — even as markets were falling. That willingness to buy the dip, rather than amplify the sell-off, is a structural shift that analysts say reflects growing confidence in India's earnings trajectory.

## What the bulls are banking on

J.P. Morgan's Nifty target of 27,000 rests on four pillars: healthy demand, strong credit expansion, rising GST collections, and resilient nominal GDP growth. Lead analyst Rajiv Batra's team flagged revenue growth as the "biggest upside risk" this earnings season — a notable framing given how rarely analysts position revenue surprises as the base case.

The logic is straightforward. India's nominal GDP growth is running above 9%, consumer credit is expanding at double digits, and GST collections have averaged over ₹1.8 lakh crore monthly. Companies operating in India's domestic economy — banks, consumer goods, infrastructure — should see that demand reflected in top-line numbers.

TCS's results already hint at the dynamic. Revenue rose 14% year-over-year, driven by two mega-deal wins in banking and financial services. CEO K. Krithivasan struck an optimistic tone on the post-earnings call, predicting a turnaround in tech spending among manufacturing and life sciences clients in Q2.

## Sectors to watch

The earnings calendar for the coming weeks is dense. Key reports that will shape the market's direction include:

**Banking:** HDFC Bank, ICICI Bank, and Kotak Mahindra Bank report in the next two weeks. Analysts expect strong loan growth and stable asset quality, with net interest margins potentially expanding as rate-hike fears recede. Foreign investors have already poured $1.5 billion into Indian banks in recent sessions — a bet on exactly this outcome.

**IT Services:** After TCS, Infosys reports next week. The $100 billion market-cap wipeout in the Nifty IT index since February has created a low bar for surprises. AI-linked revenue — which crossed $2.6 billion at TCS — is emerging as a new growth driver that could re-rate the entire sector.

**Pharmaceuticals:** The Dr. Reddy's semaglutide debacle will hang over the sector, but Sun Pharma and Zydus could benefit from competitor missteps. Investors will parse commentary on GLP-1 pipeline progress closely.

**Energy and Commodities:** With Brent crude oscillating between $76 and $79, oil marketing companies and upstream producers face divergent fortunes. ONGC and Oil India rallied this week on elevated crude prices, but sustained $80+ oil would pressure India's current account.

## The NRI investor's playbook

For NRI investors, the setup heading into earnings season is nuanced. Valuations are not cheap — the Nifty trades at roughly 20x forward earnings — but neither are they stretched relative to India's growth premium. J.P. Morgan's 27,000 target implies the market can absorb moderate earnings beats and geopolitical noise while still delivering double-digit returns by year-end.

The risk-reward favors two strategies. First, sectoral bets on banking and IT — both are underowned by foreign investors relative to recent history, and both have catalysts (loan growth, AI revenue) that could drive upward revisions. Second, systematic exposure through SIPs in diversified Indian equity funds, which smooth out the kind of single-day volatility seen this week.

The one clear message from this week: India's market infrastructure — RBI intervention, domestic institutional buying, corporate hedging — has matured to the point where even a 1,677-point crash is absorbed and reversed within 48 hours. For long-term NRI investors, that resilience is itself the thesis."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Earnings Season Opens With a Bang — J.P. Morgan Sees Nifty at 27,000 as TCS Delivers and Markets Shake Off Iran Fears",
    "subheadline": "After surviving a 1,677-point Sensex crash mid-week, Indian markets closed just 0.3% lower as TCS beat estimates and foreign investors bought the dip. Here's what NRI investors should watch as Q1 results pour in.",
    "slug": make_slug("india-q1-earnings-season-jp-morgan-nifty-27000-tcs-nri"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRI investors face a rare setup: Indian markets absorbed a brutal crash in 48 hours, earnings season has started strong, and J.P. Morgan sees 11.5% upside. The playbook favors banking and IT sector bets.",
    "tags": ["markets", "finance", "earnings-season", "jp-morgan", "nifty", "sensex", "tcs", "nri-investing", "india-markets"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters - Market Wrap", "url": "https://www.reuters.com/world/india/indian-shares-rise-tcs-boost-snap-weekly-winning-run-mideast-worries-2026-07-10/"},
        {"name": "Reuters - TCS Results", "url": "https://www.reuters.com/technology/indias-tcs-tops-revenue-estimates-weak-rupee-banking-boost-2026-07-10/"},
        {"name": "The Hindu BusinessLine - Market Live", "url": "https://www.thehindubusinessline.com/markets/stock-markets/stock-market-today-live-july-9-2026/article69777625.ece"},
        {"name": "Reuters - Weekly Wrap", "url": "https://www.reuters.com/world/india/indian-shares-snap-winning-run-investors-book-profits-earnings-focus-2026-07-08/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
    "image_caption": "The Bombay Stock Exchange in Mumbai — India's markets showed resilience this week despite geopolitical shocks",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip(),
}

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
