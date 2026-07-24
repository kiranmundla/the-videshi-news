#!/usr/bin/env python3
"""Markets & Finance writer — 2026-07-14 09:00 PT run"""
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


# ─── ARTICLE 1: IDBI Bank Privatization Revival ───

art1_body = """India's longest-running bank privatization just lurched back to life. Canada's Fairfax Financial Holdings and Dubai's Emirates NBD have submitted revised bids for a controlling 60.7% stake in IDBI Bank, Reuters reported on Tuesday, reviving a deal that stalled in March when both bidders fell short of the government's valuation floor.

The Indian government owns 45.48% of IDBI Bank, and state-run Life Insurance Corporation of India holds another 49.24%. Together, they are looking to exit a lender that was once synonymous with India's development banking model but spent years weighed down by bad loans before a turnaround under LIC's stewardship.

## Fairfax Is the Frontrunner

Sources told Reuters that Fairfax is in active conversation with the government, while Emirates NBD — which acquired another Indian lender last year — is no longer actively pursuing the deal. A top panel of bureaucrats met Monday to evaluate the revised offers, and one source indicated the transaction could close within a month.

IDBI Bank's shares rose 2.87% on Tuesday to ₹86.54, giving the lender a market capitalisation of ₹930.5 billion (approximately $9.67 billion). The bank itself said in an exchange filing that it "cannot confirm or deny" reports about Fairfax's offer and has received no government communication on the disinvestment process.

## Prem Watsa's Indian Empire

For Hyderabad-born billionaire Prem Watsa, IDBI would be the crown jewel of an expanding Indian financial services portfolio. Fairfax already controls CSB Bank (formerly Catholic Syrian Bank), holds majority ownership of digital insurer GoDigit General Insurance, and recently raised its stake in IIFL Capital Services to 51% through a ₹2,000 crore equity infusion. Under the proposed structure, GoDigit and IIFL Capital would become subsidiaries of IDBI Bank, creating an integrated banking, insurance, and wealth management platform. Fairfax would divest its CSB Bank stake to comply with RBI's single-banking-licence rule.

With 1,884 branches and a government-bank pedigree, IDBI offers scale that CSB — a smaller, Kerala-based lender — never could. Earlier reports pegged Fairfax's revised all-cash bid at around ₹77 per share, implying a combined payout of approximately ₹50,000 crore ($5.2 billion) for the government and LIC.

## Why This Matters for NRI Investors

The IDBI privatization is a litmus test for India's willingness to cede control of a major public-sector bank to private — and foreign — hands. For NRIs who hold IDBI accounts, particularly NRE and NRO fixed deposits, a change in ownership could mean upgraded digital infrastructure, better service, and potentially higher deposit rates as a private operator competes more aggressively for funds.

For those invested in Indian banking stocks, the deal signals that the government is serious about its disinvestment agenda, even if progress has been glacial. A successful IDBI sale could unlock similar exits from other public-sector banks, reshaping a sector that still accounts for roughly 55% of India's banking assets.

The revised bids come at a moment of broader foreign interest in Indian financial services. RBI's recent proposal to simplify how mutual funds and insurers raise their bank stakes to 10% — with one-time approvals replacing repeated regulatory filings — adds another layer of deregulation that could accelerate institutional ownership changes across the sector.

For NRIs weighing Indian banking exposure through mutual funds or direct equity, the message is clear: the ownership structure of Indian banking is shifting, and IDBI may be the deal that finally proves it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Fairfax Submits Revised Bid for IDBI Bank — India's Biggest Bank Privatization Could Close Within a Month",
    "subheadline": "Canada's Fairfax Financial is the frontrunner to acquire a 60.7% stake in the $9.67 billion lender, reviving a deal that stalled over valuation in March.",
    "slug": make_slug("fairfax-revised-bid-idbi-bank-privatization-nri"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "is_editorial": False,
    "diaspora_angle": "NRIs holding IDBI accounts could see upgraded services under private ownership, while the deal signals India is finally serious about bank privatization — reshaping a sector where 55% of assets remain state-controlled.",
    "tags": ["markets", "finance", "banking", "privatization", "idbi-bank", "fairfax", "nri-investing", "disinvestment"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "Moneycontrol", "url": "https://www.moneycontrol.com/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Prem_Watsa.jpg",
    "image_caption": "Prem Watsa, Hyderabad-born billionaire and Fairfax Financial chairman, who is the frontrunner to acquire IDBI Bank",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}


# ─── ARTICLE 2: Indian Markets Sell-Off on Oil and Middle East ───

art2_body = """Indian equities slid sharply on Tuesday as escalating hostilities between the United States and Iran sent crude oil prices surging and revived fears of imported inflation for the world's third-largest oil importer.

The benchmark Nifty 50 fell 0.66% to 24,052.05, while the BSE Sensex dropped 0.72% to 77,054.94. Twelve of the 16 major sectoral indices closed in the red, with autos, financials, and banks bearing the brunt.

## The Oil Shock Returns

Brent crude jumped 4.1% to approximately $87 per barrel — its highest level in a month — after Iran attacked two Emirati oil tankers and the U.S. military carried out a third consecutive night of strikes against Iranian targets. President Trump reinstated a blockade of Iranian shipping and floated a 20% fee for guarding the Strait of Hormuz, the narrow waterway through which roughly a fifth of the world's oil supply passes.

For India, which imports over 85% of its crude requirements, the price spike is a direct threat to the macro outlook. The auto index fell 1.6% as investors priced in higher fuel costs and crude-linked input pressures. High-weightage financials and banks each shed 1.1%, while mid-caps and small-caps dropped 0.4% and 1% respectively.

"Brent crude's sharp jump to around $87 per barrel remains the key monitor for Indian markets," said Rajesh Palviya, head of research at Axis Direct. "Sustained higher oil prices could fuel imported inflation, widen the current account deficit, and reduce the scope for monetary easing."

## Rupee Breaches 96 per Dollar

The Indian rupee slumped to 96.2375 per U.S. dollar — its weakest in over a month — before settling at 96.20, down 0.6% on the day. The 10-year benchmark bond yield rose 6 basis points as traders recalibrated inflation expectations.

The RBI was spotted selling dollars in both the spot and non-deliverable forward markets to contain the slide, according to traders. But with Brent now more than 20% above its recent lows, the central bank's reserves buffer is under pressure.

The rupee is now less than 1% from its all-time low of 96.96 per dollar, a level that would carry psychological weight for a market already rattled by geopolitical risk.

## The Bright Spot: IT Stocks

Not everything bled red. The IT index bucked the trend, rising modestly on the back of sector-specific catalysts. HCLTech fell 4.5% after brokerages flagged its unchanged growth outlook as a sign of lingering demand uncertainty. But Biocon surged 6.4%, leading the pharma index 1% higher, as roughly 46 million shares changed hands in a large block deal.

J.P. Morgan analysts, led by Rajiv Batra, reiterated their year-end Nifty target of 27,000, implying 11.5% upside from current levels. They see revenue growth — supported by healthy demand, strong credit expansion, and rising GST collections — as the biggest upside catalyst during earnings season.

## What NRI Investors Should Do

For NRIs with dual-economy exposure, Tuesday's sell-off is a stress test on multiple fronts. The rupee's slide directly erodes the dollar value of Indian equity holdings and the yield on NRE deposits. Those planning remittances to India may find the current exchange rate — near 96.20 per dollar — one of the most favourable windows in months to send money home.

On the equity side, the Nifty's support near 24,000 and resistance at 24,300-24,400 define a narrow trading range that suggests caution. Analysts at Axis Securities and Choice Broking recommend waiting for clarity on Middle East developments before adding positions. Defensive sectors like pharma and IT, which have historically outperformed during oil shocks, remain the safer bets for risk-averse NRI portfolios."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Sensex Drops 560 Points as Brent Crude Hits $87 and Rupee Slides Past 96 — What NRIs Need to Know About the Oil Shock",
    "subheadline": "India's markets buckle under renewed U.S.-Iran hostilities, with 12 of 16 sectors in the red and the rupee at its weakest in over a month.",
    "slug": make_slug("sensex-drops-brent-87-rupee-96-oil-shock-nri"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "is_editorial": False,
    "diaspora_angle": "The rupee near 96.20/USD creates a favourable remittance window, but erodes dollar-denominated returns on Indian equity and NRE deposits. NRIs with dual-economy portfolios face a stress test across currencies, oil, and equities.",
    "tags": ["markets", "finance", "sensex", "nifty", "crude-oil", "rupee", "middle-east", "nri-investing", "remittance"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Axis Securities", "url": "https://simplehai.axisdirect.in/"}
    ]),
    "score_total": 85,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
    "image_caption": "The Bombay Stock Exchange building in Mumbai, where the Sensex dropped 0.72% on Tuesday amid oil shock fears",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}


# ─── ARTICLE 3: RBI's NRI Deposit Drive Hits $10 Billion ───

art3_body = """The Reserve Bank of India's special deposit programme for overseas Indians has attracted approximately $10 billion in inflows, Reuters reported on Tuesday, marking a significant early milestone in a scheme designed to shore up the country's foreign exchange reserves and defend the rupee.

The programme, announced at RBI's June 5 monetary policy meeting, offers banks a zero-cost foreign-exchange swap facility for deposits raised from non-resident Indians (NRIs). A subsequent clarification on June 23 allowed banks to lend against these deposits and place a lien on them, effectively letting them leverage the inflows — a sweetener that has accelerated participation.

## $30–60 Billion Is the Real Target

The $10 billion raised so far is a fraction of what economists and bankers expect. Estimates for total inflows by the programme's September 30 deadline range from $30 billion to $60 billion. Most of the money is expected to be "back-ended," according to one source familiar with the matter, meaning the bulk of NRI deposits will arrive in August and September as banks ramp up marketing and the deadline creates urgency.

The programme echoes India's playbook from previous currency crises. In 2013, when the rupee crashed past 68 per dollar during the "taper tantrum," the RBI launched a similar FCNR(B) deposit scheme that attracted $34 billion and stabilised the currency. That programme offered banks favourable swap rates on three-year deposits, and many of those deposits were eventually rolled over.

## Why the Timing Matters

The deposit drive arrives as the rupee faces renewed pressure from multiple directions. Brent crude's jump to $87 per barrel — driven by U.S.-Iran hostilities and Strait of Hormuz disruptions — threatens to widen India's current account deficit. The rupee slid past 96 per dollar on Tuesday, its weakest in over a month, and sits less than 1% from its all-time low of 96.96.

India's forex reserves, while substantial at over $640 billion, are being drawn down through intervention. The RBI was spotted selling dollars in both spot and NDF markets on Tuesday to contain the rupee's slide. The NRI deposit inflows provide a more sustainable source of dollar liquidity — one that doesn't deplete the reserves.

For the rupee, the arithmetic is straightforward. If the programme hits even the lower end of its $30 billion target, it would offset roughly three months of India's current trade deficit at recent levels.

## What NRIs Should Consider

For NRIs in the United States, the programme creates a rare confluence of favourable conditions. The rupee at 96.20 per dollar means every dollar converted buys more rupees than at any point in the past month. The FCNR deposits carry no currency risk for the depositor — they are denominated in the foreign currency (dollars, euros, pounds) and repaid in the same currency at maturity. The swap facility means Indian banks can offer rates competitive with, and in some cases above, U.S. Treasury yields for comparable tenors.

Several major Indian banks — including State Bank of India, Bank of Baroda, and Bank of India — have been actively marketing the scheme to their overseas branches and NRI desks. SBI recently secured global credit ratings that enhance its international credibility, making its FCNR deposits a more palatable option for NRIs accustomed to Western banking standards.

The key trade-off is liquidity. FCNR deposits typically carry minimum tenors of one to five years, meaning the funds are locked up. For NRIs who can afford to park capital for that duration, the combination of competitive yields, zero currency risk, and the current exchange rate window makes this one of the more attractive NRI deposit opportunities in recent memory.

But the window has an expiration date. The RBI's swap facility is available only for deposits raised by September 30, 2026. After that, the favourable terms disappear — and so does the incentive for banks to offer above-market rates. NRIs considering the programme should be talking to their banks now, not in September."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "RBI's NRI Deposit Drive Crosses $10 Billion — But the Real Flood Is Coming Before the September Deadline",
    "subheadline": "India's special FCNR scheme for overseas Indians has raised $10 billion so far, with economists expecting $30–60 billion by the September 30 cutoff as the rupee weakens past 96.",
    "slug": make_slug("rbi-nri-deposit-drive-10-billion-fcnr-september"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "is_editorial": False,
    "diaspora_angle": "FCNR deposits carry zero currency risk for NRIs, and with the rupee at 96.20/USD and banks offering competitive yields under the RBI swap facility, the programme represents one of the best NRI deposit windows in years — but the September 30 deadline is firm.",
    "tags": ["markets", "finance", "rbi", "fcnr", "nri-deposits", "rupee", "forex-reserves", "nri-investing"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "Reserve Bank of India", "url": "https://www.rbi.org.in/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
    ]),
    "score_total": 80,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Mumbai%2C_reserve_bank_of_india_01.jpg/1280px-Mumbai%2C_reserve_bank_of_india_01.jpg",
    "image_caption": "The Reserve Bank of India headquarters in Mumbai, where policymakers designed the NRI deposit programme to bolster forex reserves",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip(),
}


# ─── PUBLISH ───

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
