#!/usr/bin/env python3
"""Markets & Finance writer — 2026-07-10 01:00 PDT run."""
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Silver Import Crackdown Sends Premiums to Six-Month High — What NRI Bullion Buyers Need to Know",
        "subheadline": "Imports have nearly halted after New Delhi hiked duties from 6% to 15% and restricted silver bars, grain, and powder. Domestic premiums have surged to $6.50 an ounce above global prices, and the squeeze is just getting started.",
        "slug": make_slug("india-silver-import-crackdown-premiums-six-month-high-nri-bullion"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "NRIs who buy silver bullion in India during visits, invest in Indian silver ETFs, or send money home for family jewellery purchases face a fundamentally different market. Premiums have flipped from discounts to double-digit surcharges, silver ETF outflows have released stored metal that is now drying up, and the import duty hike means any silver entering India costs 15% more at the border. For NRI investors holding Indian silver ETF units, the NAV may benefit from rising local premiums — but liquidity risk is growing as the physical market tightens.",
        "tags": ["silver", "commodities", "import-restrictions", "rupee", "nri-investing", "precious-metals", "india-trade-policy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/markets/commodities/india-silver-import-curbs-create-shortages-push-premiums-six-month-high-2026-07-09/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/commodities/silver-import-curbs-create-shortages-push-premiums-to-six-month-high/article69784532.ece"},
            {"name": "Mining.com", "url": "https://www.mining.com/web/india-restricts-most-silver-imports-to-cut-import-bill-support-rupee/"},
            {"name": "Reuters (June data)", "url": "https://www.reuters.com/markets/commodities/indias-silver-imports-hit-over-three-year-low-may-after-import-curbs-2026-06-16/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/df/Johnson_Matthey_500_grammes_silver_bullion.jpg",
        "image_caption": "Silver bullion bars — India's import restrictions have created acute domestic shortages",
        "image_attribution": "Wikimedia Commons",
        "body": """India has effectively shut down its silver import pipeline, and the consequences are rippling through global commodity markets and domestic investment channels alike.

Silver premiums over official domestic prices surged to $6.50 per ounce this week — more than 10% above benchmark global prices — compared with *discounts* of as much as $5.50 an ounce just two months ago in May, according to dealers tracked by Reuters. The swing from discount to premium represents a roughly $12 per ounce shift in market dynamics within weeks.

"Silver imports have nearly come to a halt, creating a shortage in the Indian market," said Chirag Thakkar, chief executive of Amrapali Group Gujarat, one of India's leading silver importers. "As a result, silver is trading at a significant premium to global prices."

## The Policy Cascade

New Delhi moved in three rapid stages. In mid-May, the government restricted imports of silver bars with 99.9% purity and all semi-manufactured forms with immediate effect. In June, it tightened further by adding silver grain and powder to the restricted category and requiring prior import authorisation from the Directorate General of Foreign Trade. And underpinning both moves: import duties on gold and silver were hiked from 6% to 15%.

The numbers tell the story. Silver imports collapsed to 46.8 metric tons in May, down from 534.3 metric tons a year earlier — a 91% plunge. In dollar terms, May imports fell to $75.57 million from $566.22 million, the lowest since February 2023. June imports fell even further from May's already cratered levels, Thakkar confirmed.

India spent a record $12 billion on silver imports in the fiscal year ended March 2026, more than double the $4.8 billion the previous year. That surge — driven by a boom in silver ETF inflows and industrial demand from solar panel manufacturing — is precisely what spooked policymakers already battling to defend the rupee and shore up forex reserves amid elevated oil prices from the Middle East conflict.

## The Domestic Supply Reality

The initial impact was cushioned by an unintended source. After duties were raised in May, many investors booked profits and exited silver ETFs, releasing physical metal into the domestic market. "That released metal, so there wasn't an immediate shortage despite the tighter import rules," a Mumbai-based bullion dealer told Reuters. "But now those supplies have dried up, and the market is feeling the pinch."

Today, the domestic market is "largely dependent on supplies from Hindustan Zinc, the country's biggest silver producer," according to a Kolkata-based dealer. That's a thin supply line for the world's largest silver consumer.

India meets more than 80% of its silver demand through overseas purchases. Silver is consumed across jewellery, coins and bars, and industrial applications including solar panels and electronics. Over the past year, investment demand — particularly through ETFs — has outpaced traditional consumption.

## What This Means for NRI Investors

For NRIs who buy silver during India trips, the math has changed dramatically. Physical silver in India now costs 10% or more above what the same metal trades for in London or New York. Anyone planning to purchase silver jewellery, coins, or bars for family in India should factor in a substantial domestic premium that didn't exist six months ago.

NRIs holding Indian silver ETF units face a more nuanced picture. Rising local premiums can boost the NAV of domestic silver ETFs, since these funds hold physical silver valued at Indian market prices. But the flip side is liquidity risk: if the ETF needs to sell physical silver in a market with restricted supply channels, execution becomes harder.

For those sending remittances to India for precious metal purchases, the timing calculus has shifted. The government's import restrictions are designed to be durable — they're part of a broader strategy to reduce pressure on foreign exchange reserves and support the rupee. Dealers expect premiums to climb higher as demand recovers from the current seasonal lull.

"As demand continues to recover, which has already begun, premiums are expected to move even higher," a Kolkata-based dealer told Reuters.

Lower Indian imports could also weigh on global silver prices, creating an unusual divergence: falling global prices but rising Indian domestic prices. NRI investors with exposure to both markets should watch this spread carefully.

The bottom line: India's silver market has entered a new regime. The days of importing silver freely at global prices plus modest duties are over. Whether you're an NRI investor, a bullion buyer, or someone sending money home for a wedding, the cost of silver in India is now structurally higher than what the world pays."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The India-US Trade Deal Is '99% Done' — So Why Can't They Close It?",
        "subheadline": "Commerce Minister Goyal says India won't sign until it secures a tariff edge over Pakistan and ASEAN rivals. Section 301 hearings in Washington could push Indian tariffs from 18% to 32%. For NRI exporters and IT workers, the stakes keep rising.",
        "slug": make_slug("india-us-trade-deal-99-percent-done-tariff-edge-goyal-nri"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "The India-US trade deal directly affects NRI professionals, business owners, and investors. Indian IT companies that employ tens of thousands of H-1B workers depend on favourable trade terms. NRI-owned export businesses face 18% tariffs that could jump to 28-32% under Section 301. And the deal's outcome will shape FDI flows, market sentiment, and the rupee — all of which touch NRI portfolios.",
        "tags": ["india-us-trade", "tariffs", "piyush-goyal", "trade-deal", "section-301", "nri-business", "bilateral-trade"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/india-bets-on-uk-trade-pact-as-us-negotiations-face-hurdles/"},
            {"name": "The Indian Eye (USISPF)", "url": "https://theindianeye.com/india-us-trade-deal-hinges-on-tariff-gap-with-pakistan-usispf-chief/"},
            {"name": "Outlook Business", "url": "https://business.outlookindia.com/economy/trumps-tariffs-again-what-washingtons-forced-labour-hearings-mean-for-new-delhi"},
            {"name": "The Indian Eye (Goyal)", "url": "https://theindianeye.com/india-aiming-for-competitive-advantage-before-implementing-us-fta-piyush-goyal/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/tariffs-shrink-indias-trade-surplus-with-us-fy26/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/63/Piyush_Goyal_crop.jpg",
        "image_caption": "Commerce Minister Piyush Goyal has said India will not implement the trade deal until it secures a competitive edge",
        "image_attribution": "Wikimedia Commons",
        "body": """US Ambassador to India Sergio Gor says the bilateral trade agreement is "99% there." Commerce Minister Piyush Goyal says the framework is finalised. Both sides describe recent talks in New Delhi as productive. And yet the deal remains unsigned, with no clear timeline for closure.

The gap between diplomatic optimism and commercial reality has become the defining feature of the India-US trade saga in 2026. And for the Indian diaspora in the United States — from IT professionals on H-1B visas to NRI business owners running export operations — the outcome of this negotiation will shape the economic ground beneath their feet.

## The 1% That Won't Budge

The sticking point is deceptively simple: tariff rates relative to competitors.

Under the proposed Bilateral Trade Agreement, Indian goods would face approximately 18% US tariffs. That rate was attractive to New Delhi when it represented a clear advantage over neighbouring exporters. "The whole deal was centred around that competitive advantage we got with that 18% over our neighbours and competing countries," Goyal explained at the India Global Forum's UK-India Week in London. "We were lower than all our neighbouring countries and all our ASEAN countries other than Singapore. That is why the deal was attractive for us."

But Washington has since restructured tariff rates for other countries, eroding India's relative advantage. Pakistan, in particular, now faces tariff treatment that is comparable to or below what India was offered. Until the US addresses this gap, New Delhi has made clear it will not sign.

"India very much wants a preferential tariff edge over its competitors, so it is in no hurry to conclude until there is further clarity on tariff rates and product exclusions," said Wendy Cutler, Senior Vice President at the Asia Society Policy Institute. "Moreover, it is seeking assurances from Washington on no further tariff hikes, which most likely is a bridge too far for the Trump team."

## The Section 301 Wildcard

Compounding the tariff dispute are ongoing Section 301 hearings in Washington focused on forced labour practices in global supply chains. The investigation, conducted by the US Trade Representative, could result in additional tariffs on Indian goods ranging from 10% to 14.5% on top of existing rates.

That would push effective tariffs on Indian exports from 18% to between 28% and 32.5% — a potentially devastating blow to competitiveness. Indian officials are negotiating the Section 301 implications alongside the broader trade deal, adding another layer of complexity to already difficult talks.

The legal framework for US tariffs is also shifting. After the Supreme Court ruled in February that the International Emergency Economic Powers Act does not authorise presidential tariffs, Washington introduced a temporary 10% tariff under Section 122, due to expire on July 24. Section 301 is emerging as the principal legal route for future country-specific tariffs.

## The Numbers Behind the Tension

India's trade surplus with the United States narrowed to $34.41 billion in FY2025-26, down from $40.88 billion the previous year. Indian exports to the US grew marginally to $87.31 billion, while US exports to India jumped to $52.90 billion from $45.63 billion.

The US remains India's top export destination, but the growth momentum has stalled. Meanwhile, India's exports to China surged 36.7% to $19.48 billion — reflecting a diversification that Washington watches warily.

Mukesh Aghi, president of the US-India Strategic Partnership Forum, frames the tariff issue as a political redline for New Delhi. Until Washington aligns India's tariff treatment at or below Pakistan's level, "New Delhi's negotiators will find it politically difficult to finalise any agreement."

## What NRIs Should Watch

The trade deal's trajectory matters for the diaspora across several dimensions.

**IT services and H-1B employers:** Indian IT giants — TCS, Infosys, Wipro, HCL — generate the bulk of their revenue from US clients. Unfavourable trade terms or retaliatory measures could complicate the operating environment for these companies, indirectly affecting the tens of thousands of Indian professionals they employ in the US on work visas.

**NRI-owned export businesses:** Small and mid-sized Indian exporters, many run by NRI families with operations spanning both countries, face direct tariff exposure. The difference between 18% and 32% tariffs can determine whether an export line is viable.

**Investment and market sentiment:** A signed trade deal would be a significant positive signal for Indian equities and the rupee. The continued uncertainty is already priced into market caution. Foreign portfolio investors have been net sellers for much of 2026, and trade deal clarity could reverse that trend.

**Bilateral investment flows:** US-India bilateral trade reached $149 billion in 2025, with $20 billion in new Indian investment into the US announced at SelectUSA. A deal would accelerate these flows; prolonged uncertainty could redirect them.

Despite the impasse, both governments appear committed to at least an interim arrangement. Farwa Aamer, Director of South Asia Initiatives at ASPI, notes that sustained engagement signals an agreement remains achievable. The question is whether achievable translates into imminent — and on that, nobody in either capital is making promises."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Inc. Hedged a Record $120 Billion in June as the Rupee Swings Between War and Central Bank Muscle",
        "subheadline": "Corporate FX hedging hit an all-time high as the rupee whipsawed between 94.96 and 95.60 this week. Goldman Sachs sees the dollar-rupee at 94 in three months. Here's what the hedging boom means for NRI remittances.",
        "slug": make_slug("india-record-120-billion-fx-hedging-rupee-war-rbi-nri-remittance"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "The rupee's trajectory directly affects every NRI sending money to India. With corporate hedging at record levels and Goldman Sachs forecasting USD/INR at 94 in three months (implying a stronger rupee), NRIs face a classic timing dilemma on remittances. The RBI's dollar-inflow measures could strengthen the rupee medium-term, meaning locking in today's 95+ rate for large transfers may be advantageous. NRE deposit rates, which are linked to rupee liquidity conditions, could also shift as RBI manages the inflow surge.",
        "tags": ["rupee", "forex", "hedging", "rbi", "goldman-sachs", "nri-remittance", "oil-prices", "corporate-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters (hedging)", "url": "https://www.reuters.com/markets/currencies/indias-dollar-inflow-salvo-sparks-record-120-bln-corporate-hedging-exporters-2026-07-09/"},
            {"name": "Reuters (rupee Friday outlook)", "url": "https://www.reuters.com/markets/currencies/rupee-finds-breathing-room-oil-pullback-soft-dollar-middle-east-risks-linger-2026-07-10/"},
            {"name": "Reuters (rupee Thursday)", "url": "https://www.reuters.com/markets/currencies/central-bank-intervention-oil-price-dip-help-rupee-edge-modestly-higher-2026-07-10/"},
            {"name": "Reuters (Goldman Sachs forecast)", "url": "https://www.reuters.com/markets/currencies/rupee-hits-three-week-low-firmer-dollar-ndf-maturities-pinch-2026-07-07/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Indian_currency-1.jpg/1280px-Indian_currency-1.jpg",
        "image_caption": "Indian rupee currency notes — the rupee traded between 94.96 and 95.60 this week amid geopolitical volatility",
        "image_attribution": "Wikimedia Commons",
        "body": """Indian corporates hedged a record $120 billion in foreign exchange exposure in June, according to clearing house data reported by Reuters — a staggering figure that reflects how fundamentally the rupee's risk profile has shifted in 2026.

The number is not just a record. It represents a 62% jump from the $74 billion monthly average during the same period last year. Between March and June, average monthly hedging stood at $102.4 billion, up from $74 billion in the comparable 2025 window. But June's $120 billion blew past even that elevated average, driven by a confluence of Middle East war risks, oil price volatility, and aggressive RBI policy action.

"There has been a noticeable increase in hedging, especially on the importer side, in recent months," said Ishan Nijhawan, assistant vice president at Mecklai Financial. "Corporates appear to be reassessing the volatility regime for the rupee, and that is leading to a more structural change in hedging behavior."

## A Week That Captured the New Normal

This week provided a textbook illustration of why Indian corporates are locking in rates at unprecedented volumes.

On Tuesday, July 8, the Sensex crashed 1,677 points — its steepest single-session fall in over three months — after President Trump declared the Iran ceasefire "over" and the US military launched fresh strikes. Brent crude surged toward $79 per barrel, and the rupee weakened to 95.50 against the dollar, a one-month low.

By Thursday, the picture had partially reversed. Oil pulled back to $77.50, the RBI was spotted selling dollars through state-run banks, and the rupee recovered to 95.39. On Friday morning, the currency was expected to open around 95.32-95.35 as Brent dipped further to $76.34.

The week's range — 94.96 to 95.60 — captures a currency caught between two powerful forces: geopolitical shock (pushing it weaker) and central bank muscle (pulling it stronger).

## The RBI's Dollar Magnet

The record hedging volumes are partly a response to the Reserve Bank of India's recent measures to attract dollar inflows into the economy. Analysts estimate these steps could draw between $40 billion and $80 billion, with most flowing into the RBI's reserves via a swap window.

The measures helped arrest a months-long rupee slide that had taken the currency to an all-time low near 97 per dollar earlier in 2026. The recovery to 94 was significant, but it has since lost momentum as recurring Middle East hostilities revive oil price fears.

Critically, the RBI's intervention has changed corporate behavior. Exporters who had been waiting for further rupee weakness sharply increased their hedging after the central bank's measures "tempered expectations of a sharp rupee depreciation," per Reuters. Long-tenor dollar buying jumped in June, suggesting importers and borrowers with foreign currency liabilities locked in longer-term protection while hedging costs were relatively low.

## Goldman's Forecast and What It Means

Goldman Sachs revised its rupee forecasts stronger this week, now projecting USD/INR at 94 in three months, 95 in six months, and 96 in twelve months — down from previous estimates of 96, 96, and 97 respectively.

The bank recommends staying short on Thai baht against the Indian rupee as a relative-value carry trade, and favours long positions on India's 30-year government bonds. Foreign investors have been active buyers, purchasing around ₹76 billion ($796 million) of the benchmark 2036 bond over the past two weeks, betting on potential inclusion in the Bloomberg Global Aggregate Index.

The 10-year benchmark yield has declined 34 basis points over the last six weeks to 6.71%, its sixth consecutive weekly drop — a bond rally that reflects confidence in India's fiscal and monetary trajectory despite the geopolitical noise.

## The NRI Remittance Calculus

For the roughly 18 million NRIs sending money to India, the hedging boom carries a direct signal: the smart money in India is locking in exchange rates now, not waiting.

If Goldman's forecast holds and the rupee strengthens to 94 within three months, an NRI sending $10,000 today at 95.39 gets ₹9,53,900. At 94, that same $10,000 yields ₹9,40,000 — a difference of ₹13,900, or roughly $146 lost to a stronger rupee. For large transfers — a property down payment, a wedding, or an NRE fixed deposit — the timing differential can run into thousands of dollars.

NRE fixed deposit rates, currently attractive at many banks, are linked to broader rupee liquidity conditions. If the RBI's inflow measures succeed in pulling $40-80 billion into reserves, domestic rupee liquidity could shift, potentially affecting deposit rates.

The counterargument: Middle East risks remain live. Iranian forces attacked US military infrastructure in Gulf states on Thursday in response to US strikes on Iran, and Brent crude could spike again if the conflict escalates. Oil at $80+ per barrel puts immediate pressure on the rupee, potentially pushing it back toward 96.

"While exporters may hedge opportunistically, importers are likely to be more aggressive and would look to hedge on any dips in USD/INR," said Abhishek Goenka, chief executive at FX advisory firm IFA Global.

The rupee's near-term path remains hostage to the Middle East. But the structural picture — record hedging, central bank support, foreign bond buying, and improving growth outlook — suggests the currency's floor is more robust than it was six months ago. For NRIs planning significant rupee transactions, the current 95+ level may be a window worth considering."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
