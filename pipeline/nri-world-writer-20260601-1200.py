#!/usr/bin/env python3
"""NRI World Writer — 2026-06-01 12:00 UTC run"""
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
        "headline": "The 'Return to India' Trap: Why NRIs Keep Moving the Goalposts on Going Home",
        "subheadline": "A viral video by a US-based Indian reignites the diaspora's oldest internal debate — the savings target that never stays still, the lifestyle that quietly becomes permanent, and the parents who keep getting older.",
        "slug": make_slug("return-to-india-trap-nri-goalposts-savings-viral"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Speaks directly to every NRI who has told themselves 'just two more years' — the financial, emotional, and generational tensions that make the return question the defining dilemma of diaspora life.",
        "tags": ["nri", "diaspora", "return-to-india", "personal-finance", "identity"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/news/trends/nri-explains-why-indians-abroad-keep-delaying-their-return-ill-earn-5-8-crores-11780236175315.html"},
            {"name": "SBI Research / Finnovate", "url": "https://www.finnovate.in/learn/blog/india-remittances-fy26-record-economy-impact"},
            {"name": "IBEF — Diaspora Remittances", "url": "https://www.ibef.org/blogs/the-diaspora-effect-remittances-to-india-rising"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/36183004/pexels-photo-36183004.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Every NRI has a number. A savings target, denominated in crores, that marks the point at which they will finally book the one-way ticket home. The number is always specific — ₹5 crore, ₹8 crore, sometimes ₹10 crore — and it is almost never reached in the way it was originally imagined.

A video posted this week by Nitin, a US-based Indian who has lived abroad for 15 years, cut through the usual platitudes. "I'll earn 5–8 crores, and after that, I'll go back to India," he said. "Brother, this is next to impossible." The video went viral across Indian social media, not because it said anything new, but because it said out loud what millions of NRIs already know and rarely admit: the return plan is, for most, a comforting fiction.

## The moving target

The psychology is straightforward, even if the lived experience is not. An Indian professional arrives in the US, UK, or Gulf on a work visa. The plan is temporary: earn well, save aggressively, build a corpus, go home. The timeline is two years, maybe five, certainly not fifteen.

But the target moves. A salary hike arrives. A promotion follows. The dollar-to-rupee conversion becomes more favourable — the rupee has weakened to roughly ₹95.5 against the dollar in 2026, down from the mid-80s just a year ago. Each year abroad, the gap between what one earns overseas and what one could earn in India widens rather than narrows.

Nitin described this with blunt arithmetic. Even entry-level gig workers in the US can save several thousand dollars a month after expenses. Comparable positions in India pay a fraction of that. The professional class faces the same calculus at a higher order of magnitude: a senior software engineer in the Bay Area earning $250,000 would need to find a ₹50-lakh-plus role in Bengaluru or Hyderabad — a number that exists in India but is not easily replicated, especially with stock compensation factored in.

## The lifestyle lock-in

Money is only half the equation. The other half is the invisible infrastructure of daily life that builds up over a decade abroad.

Children enter American or British schools and develop friendships, speech patterns, and cultural reference points that do not translate easily to a CBSE classroom. A spouse builds a career of their own. Health insurance, retirement accounts, and mortgage payments create financial gravity. The house that was supposed to be temporary becomes permanent because selling it means crystalising a loss or walking away from a neighbourhood that feels, by now, like home.

This is the part of the "Return to India" conversation that viral videos rarely capture. The decision is not purely financial. It is structural. An NRI who has been abroad for 15 years has not just saved money in a foreign currency — they have built a life in a foreign country. Unwinding that life has costs that no savings target accounts for.

## The generational pull

Against all of this sits the one force that no spreadsheet can quantify: ageing parents.

Indian diaspora conversations about returning home almost always circle back to family. Parents who were in their 50s when the child left are now in their 70s. Health crises that once felt abstract become urgent. The guilt of missing a parent's hospitalisation from 8,000 miles away is a specific kind of pain that the diaspora knows intimately.

The social media response to Nitin's video split predictably along this fault line. One camp argued that ₹5-8 crore is no longer enough to retire comfortably in urban India, citing rising property prices, private school fees that rival American tuition, and healthcare costs that have ballooned since the pandemic. The other camp said that money was never really the point — that the NRIs who keep raising their target number are simply rationalising a decision they have already made but cannot bring themselves to articulate.

## The numbers underneath

The data supports both interpretations. India received an estimated $137-140 billion in remittances in FY26, a new record, according to SBI Research. The United States alone now accounts for 27.7% of those flows, up from 23.4% in FY21. The structural shift from Gulf-sourced remittances to flows from the US, UK, and Canada reflects a diaspora that is wealthier, more professionally embedded, and — by extension — harder to dislodge.

The RBI's sixth remittances survey, published in its March 2025 Bulletin, confirmed what anecdotal evidence had long suggested: Indian migrants in advanced economies send larger individual transfers than their Gulf counterparts, and a growing share of those transfers flows into investment and savings rather than pure family maintenance. NRE and NRO deposit growth has tracked remittance growth in recent years. The diaspora is not just sending money home — it is parking money in India while staying put abroad.

## The honest answer

The most truthful response to "When are you coming back?" may be the one that most NRIs find hardest to say: probably never, or at least not in the way the question implies. The return, when it happens, is increasingly a retirement move — a decision made in one's 50s or 60s, after careers have wound down and children have left home. It is not the triumphant homecoming imagined at 28.

Nitin's video resonated because it named the gap between the narrative and the reality. The narrative says: save a target amount, go home, live well. The reality says: the target amount keeps changing because you keep changing. And at some point, the question is no longer about money at all. It is about which version of your life you are willing to give up.

For the Indian diaspora, that question has no clean answer. It never did."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Crossed $140 Billion in Remittances. The Diaspora Is Now Its Biggest Financial Safety Net.",
        "subheadline": "The RBI's latest data confirms what migration economists have argued for years: NRI money transfers are no longer a welfare flow — they are a macroeconomic anchor propping up the rupee, covering half the trade deficit, and quietly underwriting India's global ambitions.",
        "slug": make_slug("india-140-billion-remittance-record-nri-diaspora-safety-net"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Every NRI who sends money home is part of a $140 billion flow that now functions as India's single most reliable source of foreign exchange — bigger than FDI, more stable than portfolio investment, and increasingly driven by high-income professionals in the US and UK rather than construction workers in the Gulf.",
        "tags": ["nri", "diaspora", "remittances", "india-economy", "rbi", "rupee"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Finnovate / SBI Research", "url": "https://www.finnovate.in/learn/blog/india-remittances-fy26-record-economy-impact"},
            {"name": "IBEF — Diaspora Remittances", "url": "https://www.ibef.org/blogs/the-diaspora-effect-remittances-to-india-rising"},
            {"name": "RBI Annual Report / The Hindu Business Line", "url": "https://www.thehindubusinessline.com/money-and-banking/net-fdi-rebounds-to-77-bn-in-fy26-but-portfolio-flows-short-for-financing-cad-rbi/article69643123.ece"},
            {"name": "Dainik Bhaskar English / FPI Outflows", "url": "https://www.bhaskarenglish.in/national/weak-rupee-sluggish-earnings-drive-fpi-outflows-india-markets-137434399.html"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6289170/pexels-photo-6289170.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The number is so large it is easy to gloss over. India is on course to receive between $137 billion and $140 billion in remittances in FY26, according to SBI Research — a new record, and more than the GDP of many sovereign nations. It is more than double what Mexico, the second-largest recipient, collects. It is four times India's net foreign direct investment. And unlike portfolio flows, which reversed sharply in FY26 with $16.5 billion in net outflows, remittances do not panic and leave.

The Reserve Bank of India's annual report and its sixth remittances survey have confirmed what migration economists have argued for a decade: remittances are no longer a side story in India's balance of payments. They are the main story.

## The structural shift

For decades, India's remittance map was dominated by a single colour: Gulf blue. Millions of Indian workers in Saudi Arabia, the UAE, Qatar, Kuwait, and Oman sent home modest sums each month — enough to build a house in Kerala, fund a sister's wedding in Bihar, or pay school fees in Uttar Pradesh. The Gulf corridor still matters. But it is no longer the dominant one.

Advanced economies now account for more than half of India's inward remittances. The United States leads at 27.7% of total flows, up from 23.4% in FY21. The United Kingdom contributes 10.8%, up from 6.8% in the same period. Singapore, Canada, and Australia add another 13.5% combined. The GCC's share has fallen from 46.7% in FY17 to 37.9% in FY24.

The reason is compositional. India's migrant stock has tripled from 6.6 million in 1990 to 18.5 million in 2024, with a growing share concentrated in white-collar technology, finance, and healthcare roles in high-income countries. A software engineer in Seattle sending $3,000 a month generates more remittance volume than three construction workers in Dubai sending $500 each. The per-migrant yield has gone up, even as total migrant numbers from the Gulf have plateaued.

## The macro anchor

The practical consequence of $140 billion flowing into India each year is that remittances now finance close to half of India's merchandise trade deficit in a typical year. India imports more than it exports — that is structural and unlikely to change soon. The gap is closed by services exports (mainly IT), capital flows (FDI and portfolio investment), and private transfers (mainly remittances).

In the first half of FY26, India's current account deficit narrowed to $15 billion, or 0.8% of GDP, down from $25.3 billion in the same period a year earlier. Remittances were a significant part of that improvement. When foreign portfolio investors pulled $16.5 billion out of Indian equities during the year — spooked by the West Asia conflict that erupted in late February 2026, the weakening rupee, and sluggish corporate earnings — remittances kept flowing in the opposite direction.

This counter-cyclical quality is what makes remittances different from every other capital flow India receives. FDI is lumpy and project-dependent. Portfolio investment is sentiment-driven and can reverse in a week. Remittances are steady, month after month, driven by individual households making the same transfer they have made every month for years. It is the most boring and most reliable source of foreign exchange India has.

## The West Asia surge

SBI Research flagged an unusual pattern in March 2026: a 30-35% spike in remittances from the Gulf. The cause was not prosperity. It was fear. As the Iran conflict escalated and Strait of Hormuz disruptions pushed Brent crude to $95-105 per barrel, Indian expatriates in the Gulf began moving money home as a precaution — a hedge against potential evacuation or job loss.

The pattern has precedent. During COVID-19, a similar precautionary wave hit as workers feared repatriation. In both cases, flows normalised within months as the immediate threat subsided. SBI's assessment for FY27 is relatively sanguine: $135-137 billion, a slight dip from the FY26 spike but still comfortably above the long-term trend line.

For the four million Indian expatriates in the Gulf, though, the precautionary transfers are a reminder that their position is structurally more fragile than their counterparts in the US or UK. Saudisation and Emiratisation policies are steadily reducing openings for low-skilled foreign labour. States like Kerala, which built an entire economic model on Gulf remittances, face a slow-motion corridor compression that national aggregate numbers obscure.

## The rupee connection

Every dollar remitted into India creates demand for rupees. In a year when the rupee has weakened roughly 6% against the dollar — falling from the mid-80s to approximately 95.5 — that demand matters more than usual.

The weaker rupee actually incentivises higher remittances: each dollar buys more rupees, so NRIs get better conversion value when they send money home. This creates a natural counter-cyclical buffer. When the rupee is under pressure from FPI outflows and rising oil imports, remittances increase because the exchange rate makes transfers more attractive. It is not a perfect offset, but it is a meaningful one.

India's forex reserves stood at $701.4 billion as of January 2026, covering approximately 11 months of imports. Consistent remittance inflows are one of the structural inputs that have helped build and sustain that buffer over the past decade.

## What it means for NRIs

The macro story is about India. The micro story is about the 18.5 million Indians abroad who collectively constitute this flow.

The shift from Gulf to advanced-economy sourcing has a household-level implication. Gulf remittances have historically been consumption-oriented: money sent home for daily expenses, housing, and family events. Remittances from the US and UK increasingly flow toward savings and investment as well — NRE and NRO deposit growth has tracked remittance growth in recent years, and NRI interest in Indian mutual funds and real estate has expanded alongside the macro flows.

This means the diaspora's financial relationship with India is deepening, not just in volume but in complexity. It is no longer simply about sending money home to support parents. It is about maintaining investment portfolios, managing property, navigating dual-taxation regimes, and — for a growing number of professionals — keeping one financial foot in India as a hedge against an uncertain future abroad.

India's $140 billion remittance record is, in one reading, a measure of national economic strength. In another, it is a measure of how many Indians felt they needed to leave in order to earn enough to send that money back. Both readings are true. The diaspora did not set out to become India's financial safety net. It became one anyway."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}... -> {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
