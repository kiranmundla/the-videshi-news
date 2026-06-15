#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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
        "headline": "India Sent 44,000 Crypto Tax Notices and Found $104 Million Hidden. NRIs With Wallets Back Home Should Read the Fine Print.",
        "subheadline": "A data-matching crackdown is reconciling exchange records against tax filings — and dual-status investors are squarely in its path.",
        "slug": make_slug("india-crypto-tax-44000-notices-104-million-nri"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "NRIs who hold or trade crypto on Indian exchanges face a 30% flat tax, 1% TDS, and now algorithmic data-matching that flags undisclosed gains — making record-keeping a compliance necessity, not an afterthought.",
        "tags": ["crypto", "india-tax", "fintech", "nri-finance", "web3"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Traders Union", "url": "https://tradersunion.com/news/india-issues-44000-crypto-tax-notices/"},
            {"name": "AInvest", "url": "https://www.ainvest.com/news/india-tax-department-issued-44000-notices-detected-888-crore-104m-undisclosed-crypto-income-fy-2025-26/"},
            {"name": "Mint", "url": "https://www.livemint.com/money/personal-finance/itr-filing-2026-cryptocurrency-gains-tax-rules-explained.html"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5980213/pexels-photo-5980213.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A stack of gold-colored Bitcoin tokens, representing cryptocurrency holdings under scrutiny",
        "image_attribution": "Pexels",
        "body": """India's tax department has stopped politely asking. Over the past few weeks it has dispatched more than 44,000 notices to crypto investors and, in the process, surfaced upward of ₹888 crore — roughly $104 million — in income that was never declared. The figure covers the 2025-26 financial year, and it is less a one-off audit than a signal of how the machinery now works: exchange data goes in, filings come out, and the gaps light up automatically.

For the Indian diaspora, this is not abstract policy from a distant capital. A large share of NRIs in the Bay Area, New Jersey, and London keep at least one foot in India's financial system — a savings account, a demat account, and increasingly a crypto wallet on a domestic exchange like CoinDCX or WazirX. Those exchanges report transaction data directly to the authorities. When that data does not match what an investor put on a return, a notice follows.

## How the math actually works

India's crypto tax regime is unusually blunt. Profits from virtual digital assets are taxed at a flat 30%, plus a 4% cess, with no distinction between short- and long-term gains and no offsetting of losses against other income. On top of that sits a 1% tax deducted at source on transfers above modest thresholds — ₹10,000 for retail investors, ₹50,000 for some business filers. The TDS exists precisely so the government can trace who bought what and when.

That tracing is the heart of the current sweep. Officials are cross-referencing the transaction logs that exchanges submit against the Schedule VDA disclosures on individual returns. Where someone sold crypto but failed to report it, the system flags the discrepancy. Penalties are steep: up to double the tax evaded in severe cases, a ₹200-per-day charge for non-filing, and ₹50,000 for incorrect disclosure.

## Why dual-status investors are exposed

The diaspora angle is sharper than it first appears. An NRI who opened a wallet years ago while living in India, then moved abroad, may assume those holdings have slipped off the radar. They have not. The exchange still has the PAN on file, still reports the activity, and the data-matching engine does not care which time zone the account holder now lives in.

There is also the question of residency. India taxes residents on global income but non-residents only on income that arises or accrues in India. Crypto sold on an Indian exchange generally counts as Indian-sourced — so a Sunnyvale engineer liquidating an old wallet back home can owe the full 30% there, and then must work out how that interacts with U.S. reporting obligations like FBAR and Form 8938. Double-taxation relief under the India-U.S. treaty is rarely automatic for these assets.

## The practical takeaway

None of this makes crypto untouchable for NRIs. It makes carelessness expensive. The investors getting caught are overwhelmingly those who treated digital assets as off-books money rather than as a taxable asset class with a paper trail attached to their identity.

The fix is unglamorous: keep dated records of every transaction, the rupee value at the time, and the TDS already deducted; file Schedule VDA even when the gain is small; and for anyone with U.S. tax exposure, reconcile the Indian filing with the American one rather than treating them as separate worlds. Crypto bookkeeping tools that consolidate exchange data exist for exactly this reason.

India is not banning crypto — it tried that rhetoric years ago and quietly retreated. What it is building instead is a surveillance-grade compliance net that assumes every transaction is visible. For a diaspora that prizes legitimacy and clean cross-border finances, the message is simple: the wallet in Bengaluru is no longer a private matter.

The broader trend is worth watching. As India tightens enforcement and the U.S. sharpens its own crypto reporting rules, the era of treating digital assets as a regulatory grey zone is closing on both sides of the ocean. For NRIs straddling two tax systems, the cost of getting it wrong has rarely been higher — or easier for an algorithm to spot."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Uber and Lyft Are Suing New York Over a Law That Stops Them Firing Drivers Quickly. Indian Immigrant Drivers Are Watching Closely.",
        "subheadline": "Local Law 52 would bar 'wrongful deactivations' — and for the South Asian drivers who fill these fleets, a sudden app ban can mean losing a livelihood overnight.",
        "slug": make_slug("uber-lyft-sue-nyc-driver-deactivation-law-52"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Tens of thousands of South Asian immigrants drive for Uber and Lyft in U.S. cities; a law limiting arbitrary 'deactivations' directly affects their job security, while the platforms argue it forces them to keep unsafe drivers.",
        "tags": ["gig-economy", "uber", "lyft", "immigrant-workers", "labor"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/lyft-uber-sue-new-york-city-block-driver-retention-law/"},
            {"name": "Zacks", "url": "https://www.zacks.com/stock/news/uber-technologies-uber-june-2026.html"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/23319099/pexels-photo-23319099.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A rideshare driver uses a smartphone navigation app inside a car at night",
        "image_attribution": "Pexels",
        "body": """Uber and Lyft do not often agree on much, but they have just sued the same city within 24 hours of each other. Both have asked a Manhattan federal court to strike down New York City's Local Law 52 of 2026, a measure that prohibits the ride-hailing giants from swiftly dismissing drivers without a "bona fide economic reason" or "just cause." The law, which survived a City Council override of a mayoral veto, is set to take effect on July 28.

To the companies, it is an unacceptable constraint. Uber called the law "reckless"; Lyft called it "hazardous," arguing that it would force them to keep dangerous drivers on the road and violate their due-process and free-speech rights. To a large slice of the workforce that actually does the driving, however, the calculus looks very different — and that slice includes a substantial number of Indian and broader South Asian immigrants.

## The word that controls a livelihood: "deactivation"

In gig-economy parlance, being fired is called being "deactivated." There is no notice period, no HR meeting, often no clear explanation. A driver opens the app one morning and simply cannot log in. For someone driving to cover rent and remittances, that is not an inconvenience; it is the abrupt end of an income stream.

Local Law 52 targets exactly this. It would require ride-hailing firms to show just cause before deactivating a driver and to provide notice and a path to contest the decision. The companies object to the notice requirements, the privacy implications, and what they describe as a heightened burden of proof. City Council Speaker Julie Menin and Council Member Shekar Krishnan — himself of Indian origin — have said they will fight to ensure app-based drivers get "basic due process protections."

## Why this lands on the diaspora

Walk through any major U.S. airport rideshare lot and the accents tell the story. South Asian immigrants — Punjabi, Gujarati, Bengali, Tamil, and others — are heavily represented among Uber and Lyft drivers in New York, New Jersey, and the Bay Area. For many, gig driving is the first rung of the American economy: flexible enough to work around family or a second job, accessible without a corporate résumé, and available while immigration status or credential recognition is sorted out.

That accessibility comes with fragility. An algorithm can deactivate a driver over a disputed passenger complaint, a misread document, or a sudden policy change, and the driver has little recourse. For an immigrant with limited English, no union, and a thin financial cushion, the lack of due process is not a theoretical grievance — it is the difference between making this month's payments and not.

## The safety argument cuts both ways

The platforms are not inventing their concern. As of June 1, Uber faced more than 3,500 lawsuits and Lyft dozens more in nationwide litigation alleging driver misconduct, and the companies argue that any law slowing their ability to remove a driver puts passengers at risk. That is a real tension: due process for drivers versus rapid removal of bad actors.

But drivers' advocates counter that the current system already errs heavily toward removal, sweeping up the innocent alongside the guilty with no meaningful appeal. The point of Local Law 52, they say, is not to protect predators but to ensure that an honest driver wrongly flagged is not summarily cut off.

## What to watch

The financial stakes for the companies are modest relative to their scale — Uber is expected to post quarterly revenue near $14 billion — but the precedent is not. New York has repeatedly served as the template for gig-work regulation that other cities copy. If Local Law 52 survives the legal challenge, expect similar measures in other dense, immigrant-heavy markets where ride-hailing is a primary employer.

For the diaspora, the case is a reminder that the gig economy many newcomers rely on is being rewritten in real time, in courtrooms rather than apps. Whether a driver in Queens or Jersey City keeps the right to contest a deactivation may turn on how a federal judge weighs corporate free-speech claims against a worker's right to know why the app went dark."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Is Funding Its Own Eyes in the Sky. A Bengaluru Startup Just Won a Grant to Build AI That Sees the Subcontinent.",
        "subheadline": "SatSure's $2.6 million award is a small cheque with a big idea behind it: sovereign Earth-observation models trained on India's own land, not borrowed from the West.",
        "slug": make_slug("india-satsure-sovereign-ai-earth-observation-grant"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "India's push for sovereign space-AI infrastructure opens cross-border investment and engineering opportunities for NRIs in deep tech, while reducing the country's dependence on foreign satellite-data providers.",
        "tags": ["spacetech", "india-ai", "deeptech", "isro", "sovereign-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/space/indias-satsure-bags-26-million-grant-build-ai-powered-earth-observation-models/"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/weekly-funding-roundup-june-6-12-indian-startups"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/30596313/pexels-photo-30596313.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A satellite orbiting Earth, used to illustrate space-based Earth observation",
        "image_attribution": "Pexels",
        "body": """A $2.6 million grant rarely makes headlines in a world of billion-dollar AI rounds. But the 246-million-rupee award that India's space regulator just handed to SatSure Analytics is worth more than its size. It is a down payment on an idea that India has been circling for years: building artificial intelligence that understands the subcontinent on its own terms, rather than renting that understanding from foreign providers.

The Bengaluru-based firm will use the money to develop large Earth-observation models — AI systems trained on satellite and drone imagery — tuned specifically to Indian conditions. The pitch is that global models, built on data from temperate Western landscapes, routinely stumble over India's realities: erratic monsoons, fragmented farm plots, dense and chaotic urban sprawl. A model that has actually learned what an Indian floodplain or a Punjab wheat field looks like from orbit will simply be more accurate.

## The sovereign-AI logic

The grant fits a pattern visible from Washington to Beijing to New Delhi. Governments increasingly treat geospatial intelligence as critical infrastructure — too important for climate management, disaster response, and national security to outsource. India has opened its once state-monopolized space sector to private firms and stood up a 10-billion-rupee fund to help space startups scale. SatSure's award is one of the first concrete cheques to flow from that ambition into AI specifically.

"Earth observation is moving from project-specific analytics to reusable intelligence infrastructure," said Rashmit Singh Sukhmani, SatSure's co-founder and chief technology officer. Translated: instead of building a one-off model every time someone needs to assess flood risk or crop yield, the company wants a foundational layer that many sectors — agriculture, insurance, infrastructure, finance — can build on top of.

## Why an NRI should care

For the Indian diaspora, this is one of the more investable threads in India's tech story, and for several reasons.

First, deep tech is where India is trying to move up the value chain. For two decades the diaspora's professional identity was tied to IT services — the back office of global tech. Sovereign space-AI is a deliberate bet on owning intellectual property rather than billing hours, and it is the kind of frontier work that draws NRI engineers and researchers weighing a return or a cross-border role.

Second, the capital is increasingly cross-border. The same week SatSure won its grant, India's startup ecosystem absorbed a steady flow of venture money, and events like Bharat Innovates 2026 in Nice — co-launched by Prime Minister Modi and President Macron — were explicitly structured to connect 120 vetted Indian deep-tech firms with more than 500 global investors. NRIs with capital and networks are a natural bridge in that matchmaking.

Third, the use cases touch the diaspora's own concerns back home. Better monsoon and agricultural modeling affects family land, rural insurance, and food prices. Sharper urban-expansion data shapes the real-estate decisions many NRIs make remotely. Earth-observation infrastructure is not an abstraction when your parents' farm or your investment flat sits inside the area being mapped.

## The bigger picture

SatSure is also slated to take part in India's programme to build a commercial satellite constellation — meaning the AI models and the hardware feeding them are being developed in tandem. That vertical integration, from orbit to algorithm, is what "sovereign" actually means in practice: not just an Indian app on foreign data, but Indian satellites, Indian data, and Indian models stacked together.

There is a long road between a $2.6 million grant and a self-sufficient space-AI industry. India's private space sector is still young, and foreign providers remain far ahead on scale. But the direction is unmistakable. A country that once imported its satellite imagery is now funding the intelligence to interpret its own, and inviting its global citizens to help build it.

For a diaspora that has spent a generation as the engine of other companies' technology, the chance to own a piece of India's frontier — in space, in AI, in the infrastructure that ties them together — is exactly the kind of opportunity worth tracking from a desk in San Jose or London."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
