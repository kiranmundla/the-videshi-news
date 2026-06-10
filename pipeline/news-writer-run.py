#!/usr/bin/env python3
"""News writer run - June 10, 2026 evening cycle"""

import json
import os
import requests
from datetime import datetime, timezone

# Load Supabase credentials
env_lines = open(os.path.expanduser("~/.env.supabase")).readlines()
env = {}
for line in env_lines:
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

SUPABASE_URL = env.get("SUPABASE_URL", "")
SUPABASE_KEY = env.get("SUPABASE_SERVICE_ROLE_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ============================================================
# ARTICLE 1: H-1B $100,000 Fee Struck Down
# ============================================================
articles.append({
    "headline": "A Federal Judge Just Killed Trump's $100,000 H-1B Fee. The Administration Says It Will Appeal.",
    "subheadline": "The ruling by US District Judge Leo Sorokin in Massachusetts is the most significant legal setback yet for the administration's campaign to restrict skilled immigration. Indian professionals, who hold roughly 72% of all H-1B visas, stand to benefit the most.",
    "slug": "federal-judge-strikes-down-trump-100000-h1b-visa-fee-sorokin-massachusetts-indian-workers-20260610",
    "category": "news",
    "status": "review",
    "is_editorial": False,
    "published_at": now_utc,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/aa/Leo_Sorokin_%28cropped%29.jpg",
    "image_caption": "US District Judge Leo Sorokin, who ruled the $100,000 H-1B fee was an unlawful tax",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com"},
        {"name": "People Matters", "url": "https://www.peoplematters.in"},
        {"name": "Connected to India", "url": "https://www.connectedtoindia.com"}
    ]),
    "body": """The most expensive barrier to hiring foreign tech workers in the United States lasted nine months. On Monday, a federal judge in Massachusetts struck it down.

US District Judge Leo Sorokin ruled that the **$100,000 fee** President Donald Trump imposed on new H-1B visa applications last September was an unlawful tax that exceeded the executive branch's authority. The government said it would appeal.

The decision lands like a thunderclap across the American technology sector — and nowhere louder than in Indian households that depend on the H-1B programme for their livelihoods. Indian nationals account for roughly **72% of all H-1B visas issued**, and tens of thousands of engineers, researchers, doctors, and data scientists from India enter the US workforce through the programme every year.

## What the Fee Was Designed to Do

The Trump administration introduced the one-time $100,000 charge through a presidential proclamation in September 2025. Before the policy, employers generally paid between $2,000 and $5,000 in government filing fees depending on the petition category.

The administration argued that the fee would discourage abuse of the H-1B programme and protect American workers from foreign competition. In his proclamation, Trump contended that "abuses of the H-1B program present a national security threat by discouraging Americans from pursuing careers in science and technology."

Critics in the technology industry called it a de facto ban. At $100,000 per petition, sponsoring a mid-level software engineer from Hyderabad or Pune would cost more than many of those engineers would earn in their first year.

## Why the Court Said No

A coalition of **20 Democratic state attorneys general**, led by California, challenged the measure. They argued that the president had effectively created a new tax without congressional approval.

Judge Sorokin agreed. In his ruling, he wrote that the "substance and application" of the payment demonstrated that it functioned as a tax — regardless of how the administration labelled it. Under US law, only Congress has the power to impose taxes.

The court also found that neither the State Department nor US Citizenship and Immigration Services had the legal authority to implement such a charge unilaterally.

## The Diaspora Reacts

Indian diaspora organisations in the US welcomed the decision, though with a note of caution.

"All stakeholders connected with H-1B visas will heave a sigh of relief after the court order, but one wonders if this is truly the end of the matter," said **Sanjeev Joshipura**, Executive Director of Indiaspora. He warned that the administration could still create procedural hurdles for H-1B holders that would not run afoul of the law.

**Khanderao Kand**, Chief of Policy and Strategy at the Foundation for India and Indian Diaspora Studies, called the ruling essential for preserving American competitiveness. "Access to highly skilled global talent remains essential for the continued growth of the US's technology, healthcare, and advanced manufacturing sectors," he said.

## The Landscape Has Already Changed

Even with the $100,000 fee gone, the H-1B system is not what it was. The Department of Homeland Security has already scrapped the old random lottery in favour of a **salary-based selection model** that prioritises higher-paid applicants. Companies that file multiple petitions for the same person now face fraud charges.

The fee reversal removes a financial sledgehammer, but the broader direction of US immigration policy — making it harder, slower, and more expensive for skilled workers to enter the country — remains firmly in place. For the roughly 700,000 Indian nationals in the decades-long green card backlog, Monday's ruling changes little about the wait ahead.

What it does change is the immediate math for employers deciding whether to hire abroad at all. And for Indian professionals waiting on their next petition, the $100,000 question just got a $100,000 answer."""
})

# ============================================================
# ARTICLE 2: India Rejects US Section 301 Overcapacity Charges
# ============================================================
articles.append({
    "headline": "India Fires Back at Washington: 'We Don't Have Overcapacity in Anything.'",
    "subheadline": "India's top trade official rejected US allegations of surplus manufacturing capacity in textiles and steel, calling them a new narrative outside WTO rules. The pushback comes as both sides race toward a trade deal before Section 301 tariffs kick in.",
    "slug": "india-rejects-us-section-301-overcapacity-textiles-steel-trade-deal-20260610",
    "category": "news",
    "status": "review",
    "is_editorial": False,
    "published_at": now_utc,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Textile_manufacturing_in_Meerut%2C_India.jpg/1280px-Textile_manufacturing_in_Meerut%2C_India.jpg",
    "image_caption": "Textile manufacturing in Meerut, India — the sector at the centre of the US-India trade dispute",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"}
    ]),
    "body": """India does not have surplus manufacturing capacity in textiles or steel, no matter what Washington says. That was the message from **Amitabh Kumar**, India's additional trade secretary and Director General of Trade Remedies, who pushed back on Wednesday against allegations at the heart of a US trade investigation that could trigger punishing new tariffs.

"Overcapacity is a country's perspective," Kumar told reporters. "We don't think we have overcapacity in anything."

The rebuttal is India's most pointed public response yet to a **Section 301 investigation** launched by the Office of the US Trade Representative in March. The probe targets India alongside 15 other countries over policies Washington says allow factories to keep producing beyond what market conditions support — from solar modules and petrochemicals to steel and textiles.

## The Core Argument

Washington points to India's $42 billion goods trade surplus with the United States in 2025 as evidence of structural overcapacity. India says that number ignores a basic fact: its 1.4 billion people consume far less per capita than almost any major economy.

Kumar's argument was blunt and specific. India's per capita consumption of textile products, particularly man-made fibre and technical textiles, is "abysmal." The country is a net importer of man-made fibres, not a dumper.

"This country has a hot climate, tropical climate. We wear cotton," Kumar said. "How do we have overcapacity?"

On steel, the logic was the same. India may be the world's second-largest producer, but its per capita steel consumption is among the lowest globally. The country's output reflects its development needs — roads, bridges, railways, housing — not excess production aimed at flooding foreign markets.

## What Washington Really Wants

Trade analysts say the overcapacity allegations are leverage, not the endgame. Washington is using the threat of Section 301 tariffs to press India on three fronts: opening its agricultural markets, purchasing more American energy and defence products, and reducing barriers to US goods.

The United States has also proposed an additional 12.5% tariff on imports from India and several other countries over allegations of forced labour — charges India has flatly rejected.

Meanwhile, India is pushing for a bilateral trade deal that would include preferential tariffs compared to competitors like China and Vietnam. Trade Minister **Piyush Goyal** said last week that the first tranche of an agreement could be concluded by mid-July.

## Why NRIs Should Care

For the Indian diaspora in the United States, the trade friction hits multiple pressure points at once. A trade war would raise prices on Indian-made goods Americans buy — from generic pharmaceuticals and cotton garments to auto parts and IT services. It could also complicate the broader diplomatic relationship at a moment when Modi and Trump are expected to meet at the G7 summit in France next week, with H-1B visas and energy cooperation on the agenda.

India's formal submission to the USTR has already rejected the allegations, stating that Washington provided no "cogent rationale or prima facie evidence" to support its claims. Kumar added that overcapacity is a concept that does not exist in any trade remedial law under the WTO framework.

"It is a new narrative," he said.

New narrative or not, the tariff clock is ticking. And the gap between what Washington demands and what New Delhi is willing to concede will define the most consequential trade negotiation either country has entered in years."""
})

# ============================================================
# ARTICLE 3: India Bond Tax Exemption Draws Foreign Inflows
# ============================================================
articles.append({
    "headline": "India Scrapped Taxes on Foreign Bond Investments. A Billion Dollars Showed Up in Three Days.",
    "subheadline": "The government eliminated withholding and capital gains taxes on foreign holdings of government bonds, broadened market access, and incentivised NRI deposits — all in a single emergency package designed to stabilise the rupee and counter the oil shock.",
    "slug": "india-scraps-bond-tax-foreign-investors-billion-dollar-inflows-rbi-rupee-oil-20260610",
    "category": "news",
    "status": "review",
    "is_editorial": False,
    "published_at": now_utc,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_02.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_02.jpg",
    "image_caption": "The Reserve Bank of India headquarters in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "State Street Investment Management", "url": "https://www.statestreet.com"}
    ]),
    "body": """For years, India's government bond market was one of the hardest places in Asia for foreign investors to put money. The taxes were steep, the access was limited, and the paperwork was relentless.

Last Friday, policymakers tore most of those barriers down in a single afternoon. And the money started moving immediately.

More than **$1 billion** worth of Indian government debt was bought by foreign investors in just three trading sessions after the announcement — matching the total foreign inflows into the market for the entire year before it. Yields on government bonds have already fallen 10 to 30 basis points across the curve, with shorter maturities seeing the biggest drops.

## What Changed

The package, rolled out by the government and the Reserve Bank of India in a coordinated response to the oil shock battering Indian assets, had three major components.

First, the government **scrapped withholding and capital gains taxes** on foreign investments in government bonds. This was the single biggest deterrent for institutional investors, who had long complained that India's tax treatment made its bonds uncompetitive against peers like Indonesia and South Korea.

Second, policymakers **broadened the pool of government securities** available to foreigners without investment limits. Previously, foreign participation was tightly capped, and many bonds were off-limits entirely.

Third, the RBI introduced **concessional forex swap facilities** to encourage banks to raise foreign currency deposits from non-resident Indians and for companies to tap overseas borrowings. The move effectively eliminates forex hedging costs for lenders, lowering the cost of mobilising dollar liquidity.

## Why Now

The timing is not subtle. India's external balance sheet has been under siege since the Iran war began in February. Brent crude has been trading near $90 a barrel, with spikes above $98 during escalation cycles. The rupee has weakened to 95.26 per dollar. Foreign investors have pulled $29 billion out of Indian equities in 2026 alone.

The government needed to find new sources of dollar inflows — fast. Bond markets, which were barely registering foreign interest, became the obvious target.

"We believe that these changes are a game-changer for debt flows," said **Jennifer Taylor**, head of emerging market debt at State Street Investment Management, which manages about $5.6 trillion in assets. She said the tax removal makes Indian government bonds more attractive on a relative basis and should boost foreign participation across the yield curve.

## The NRI Connection

The package includes specific sweeteners for the Indian diaspora. The concessional swap facility means banks can now offer higher rates on NRI dollar deposits without bearing the forex risk themselves. Several Indian banks are already offering NRI depositors up to 7% on dollar-denominated accounts, a rate competitive with US high-yield savings accounts but backed by state-owned lenders.

For NRIs who have been watching the rupee slide and wondering whether to park money in India, the calculus just shifted. Higher deposit rates, reduced tax friction on bond investments, and an RBI clearly willing to defend the currency all tilt the equation toward sending more remittances home.

## The Bigger Picture

The bond-tax overhaul also strengthens India's case for inclusion in global bond indexes — a long-running ambition that could unlock tens of billions in passive inflows. India was added to the JPMorgan Government Bond Index-Emerging Markets last year, but full inclusion in other major indexes has been held back by exactly the kind of access and tax barriers that were just removed.

BlackRock, the world's largest asset manager, said on Wednesday that India's market has been "over-punished" for lacking a direct AI play and for its oil import dependence. The firm called the country one of its "highest-conviction" medium- to long-term emerging market trades.

Whether the bond inflows sustain depends largely on one variable no policymaker in Mumbai can control: the price of oil. If the Iran war escalates further and Brent pushes past $100, no tax incentive will be enough to offset the structural drag on India's current account. But for now, the money is moving in the right direction — and faster than anyone expected."""
})

# ============================================================
# INSERT INTO SUPABASE
# ============================================================
inserted = 0
for article in articles:
    print(f"\nInserting: {article['headline'][:70]}...")
    
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    
    if resp.status_code in (200, 201):
        data = resp.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: id={data[0].get('id','?')}, slug={data[0].get('slug','?')}")
            inserted += 1
        else:
            print(f"  ✓ Inserted (response: {str(data)[:100]})")
            inserted += 1
    else:
        print(f"  ✗ FAILED ({resp.status_code}): {resp.text[:200]}")

print(f"\n{'='*50}")
print(f"Done. {inserted}/{len(articles)} articles inserted with status='review'.")
