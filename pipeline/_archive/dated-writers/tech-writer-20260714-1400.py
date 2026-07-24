#!/usr/bin/env python3
"""Tech writer run: 2026-07-14 14:00 PT — 3 articles."""
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
    # ─── Article 1: TYLSemi $43M AI Chiplets ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Two Ex-Qualcomm Engineers Just Raised $43 Million to Break Broadcom's Grip on Custom AI Chips",
        "subheadline": "TYLSemi's Indian-origin co-founders are betting that open-standard chiplets, not proprietary lock-in, will define the next era of AI silicon.",
        "slug": make_slug("tylsemi-43-million-chiplets-ai-broadcom-qualcomm"),
        "category": "technology",
        "vertical": "semiconductors",
        "diaspora_angle": "Indian-origin semiconductor founders are now building the fundamental building blocks of AI hardware, challenging Broadcom and Marvell's dominance in the custom chip market that powers Meta, Google, and Amazon's AI infrastructure.",
        "tags": ["semiconductors", "ai-chips", "indian-founders", "chiplets", "startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/tylsemi-raises-43-million-create-building-blocks-custom-ai-chips-2026-07-14/"},
            {"name": "Qualcomm AlphaWave Acquisition", "url": "https://www.qualcomm.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Close-up of a semiconductor circuit board with microchips and electronic pathways",
        "image_attribution": "Pexels",
        "body": """When Qualcomm acquired the Canadian chip interconnect firm AlphaWave Semi, two of its senior leaders saw an opening — not inside the acquirer, but outside it.

Mohit Gupta and Sunil Bhardwaj, both veterans of the high-speed semiconductor interconnect world, left less than a year after the deal closed and founded TYLSemi. On Tuesday, the startup announced a $43 million early-stage funding round — a substantial war chest for a company that wants to fundamentally reshape how AI chips are designed and assembled.

## The Problem: A Duopoly Controls the Plumbing

The custom AI chip market is booming. Meta, Amazon, Google, and Microsoft are all racing to design their own silicon rather than depend entirely on Nvidia. But there is a bottleneck: to make these custom chips talk to each other at the speeds AI workloads demand, companies must work with either Broadcom or Marvell Technology — the two firms that control the proprietary interconnect technology that stitches chip components together.

That means you cannot build a custom AI chip without effectively hiring one of two gatekeepers.

TYLSemi wants to change the equation by offering "chiplets" — standardised, interchangeable pieces of AI chips built on open industry standards. Instead of being locked into a single vendor's technology stack, TYLSemi's customers can mix and match chiplets from multiple providers, assembling them into a final chip the way a builder sources standardised components.

"I feel progress happens with standardisation," Gupta told Reuters. "Whenever you do proprietary lock-in, it's a short-term game. Yes, you can squeeze customers given your position and whatnot, but it's not healthy for the market."

## Why This Matters for Indian Tech Professionals

The semiconductor industry's centre of gravity is shifting, and Indian-origin engineers are increasingly at the helm. Gupta and Bhardwaj join a growing roster of diaspora founders tackling hardware's hardest problems — from Sanjay Mehrotra running Micron's $250 billion U.S. expansion to Raghib Hussain turning Intel's Altera spinoff into an AI contender.

For the thousands of Indian engineers working at Broadcom, Marvell, Qualcomm, and the hyperscalers' custom silicon teams, TYLSemi's open-standard bet could create an entirely new ecosystem of roles. If chiplets become the norm, the demand shifts from monolithic chip design to modular architecture — a discipline where Indian engineering talent, already dominant in VLSI and chip verification, would be exceptionally well-positioned.

## The Funding and What Comes Next

Matter Venture Partners led the round, with participation from Viola Ventures, GHOVC, and Egis Technology. TYLSemi also disclosed unnamed strategic investments from companies in the "global semiconductor and AI infrastructure ecosystem," hinting at potential customers or partners already bought into the open-chiplet thesis.

The timing is not accidental. The chiplet market is projected to grow to over $50 billion by 2030, driven by the economics of AI: building a single monolithic chip at cutting-edge process nodes is prohibitively expensive for all but the largest players. Chiplets offer a way to combine older, cheaper manufacturing processes with cutting-edge components — getting AI performance without the full cost of a ground-up custom design.

For NRI investors watching the semiconductor space, TYLSemi represents a different kind of bet than the megacap chip stocks. It is early-stage, pre-revenue, and competing against entrenched incumbents. But if the open-chiplet thesis plays out, the founders who spent years inside AlphaWave understanding exactly how chips interconnect may have a structural advantage that money alone cannot buy.

The custom AI chip market needs more than two gatekeepers. Two Indian-origin engineers are betting $43 million that the industry agrees."""
    },

    # ─── Article 2: Asha Sharma Xbox / Fed / H-1B Backlash ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Xbox CEO Asha Sharma Joins the Federal Reserve's New Task Force. The Backlash Says More About America Than About Her.",
        "subheadline": "The Indian-American executive is restructuring Microsoft's $20 billion gaming business while facing racially charged attacks over H-1B visas — a controversy she has nothing to do with.",
        "slug": make_slug("asha-sharma-xbox-fed-task-force-h1b-backlash"),
        "category": "technology",
        "vertical": "tech-leadership",
        "diaspora_angle": "An Indian-American tech executive born in Wisconsin is being scapegoated for the H-1B system she did not design, highlighting how even American-born professionals of Indian heritage face racialised scrutiny in tech leadership roles.",
        "tags": ["xbox", "microsoft", "h-1b", "indian-american", "federal-reserve", "tech-leadership"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fox News", "url": "https://foxnews.com/politics/ceo-under-fire-mass-layoffs-amid-foreign-worker-hiring-spree-now-appointed-feds-task-force-jobs"},
            {"name": "New York Post", "url": "https://nypost.com/2026/07/10/us-news/fury-erupts-as-us-brand-fires-1600-employees-after-securing-thousands-of-foreign-worker-visas/"},
            {"name": "GeekWire", "url": "https://www.geekwire.com/2026/this-cannot-continue-microsoft-xbox-ceo-calls-for-reset-amid-reports-of-looming-job-cuts/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/62/Asha_Sharma_CEO_of_XBOX_at_2026_XBOX_Showcase.jpg",
        "image_caption": "Asha Sharma, CEO of Xbox, at the 2026 Xbox Showcase",
        "image_attribution": "Wikimedia Commons",
        "body": """Asha Sharma has had a turbulent week, even by the standards of someone running one of the most challenging jobs in the technology industry.

On one hand, the Federal Reserve appointed her to its newly created "Productivity and Jobs" task force, alongside venture capital titan Marc Andreessen and Stanford economist Charles I. Jones. On the other, she has become the target of a racially charged online campaign that conflates her Indian heritage with the H-1B visa programme — despite the fact that she was born in Wisconsin.

The proximate cause of the fury: Microsoft announced 4,800 layoffs across the company, with 1,600 coming from Sharma's Xbox division. The same week, data showed Microsoft had been approved to hire 2,273 H-1B workers this year. Critics, primarily on conservative media and social platforms, drew a straight line between the two figures. Representative Riley Moore of West Virginia called the H-1B programme "a scam" and demanded it be abolished outright.

## The Business Reality

What the outrage machine omits is the business context that made the layoffs inevitable. Sharma inherited an Xbox division bleeding money. In her own words, the business operates at margins "3 to 10 times lower than comparable platform and publishing businesses." Excluding the Activision Blizzard King acquisition, Xbox spent more than $20 billion over five years on content, platform, and hardware subsidies — while annual revenue actually declined by nearly half a billion dollars.

"Going forward, this cannot continue," Sharma and Xbox content chief Matt Booty wrote in an internal memo that Sharma made public, a transparency move unusual for a division head at Microsoft.

She has moved fast since taking over as CEO in February: slashing Game Pass prices to stem subscriber losses, killing Microsoft's Gaming Copilot service, and announcing the return of console exclusives. The layoffs, painful as they are, fit the pattern of a new leader cleaning up years of strategic drift.

## The Racial Dimension

But the reaction to Sharma has been different from the reaction to, say, a white male CEO announcing identical layoffs. Online critics have called her appointment to the Fed task force "like asking El Chapo to lead the DEA." Others have attacked her competence in explicitly racial terms, claiming her "one function is to purge white Americans and replace them with Indian cheap foreign labour."

Sharma is not an immigrant. She is not on a visa. She is an American-born tech executive who was previously Instacart's COO before joining Microsoft. The conflation of her heritage with the H-1B programme is a case study in how anti-immigration sentiment bleeds into anti-Indian sentiment, regardless of citizenship.

An Indian-origin tech investor pushed back directly, noting on X that the H-1B approvals largely represent visa renewals for long-tenured employees stuck in green card backlogs, not new hires replacing laid-off Americans. "Saying that's 'replacing Americans' is like saying letting a loyal employee stay and renew his visa in the building is the same as hiring someone new off the street," the investor wrote.

## The Bigger Picture for Indian Americans in Tech

The episode arrives against an intensifying political backdrop. Vice President JD Vance announced this week that the Department of Labour has launched "dozens of subpoenas and investigations into foreign fraudsters who are trying to take advantage of the H-1B visa program." President Trump's attempt to impose a $100,000 fee on H-1B applications was struck down by a federal judge, but the signal is clear: the programme is under sustained political pressure.

For Indian Americans in tech — whether on H-1B visas, green cards, or as natural-born citizens like Sharma — the message is unsettling. The political environment does not distinguish between immigrants and Americans with immigrant heritage. The same week that Microsoft clarified its layoffs were "based on business need, not visa status" and that H-1B employees were also affected, the narrative had already hardened.

Meanwhile, Sharma will be advising the Federal Reserve on productivity and employment. If there is irony in the appointment, it is not the kind her critics intend: an executive actively restructuring a bloated business to make it productive is precisely the kind of person a task force on productivity should want."""
    },

    # ─── Article 3: Nadella "Reverse Information Paradox" ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Satya Nadella Says You're Paying for AI Twice — Once With Money, Once With Your Secrets",
        "subheadline": "The Microsoft CEO's 'Reverse Information Paradox' should worry every Indian IT services firm betting its future on deploying other people's AI models.",
        "slug": make_slug("satya-nadella-reverse-information-paradox-ai-enterprise"),
        "category": "technology",
        "vertical": "enterprise-ai",
        "diaspora_angle": "Nadella's warning directly threatens the business model of Indian IT giants like TCS, Infosys, and Wipro, who are rushing to deploy OpenAI and Anthropic models for enterprise clients — if those clients' proprietary knowledge leaks to model providers, the entire value proposition collapses.",
        "tags": ["satya-nadella", "microsoft", "ai", "enterprise", "indian-it", "data-privacy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/microsoft-ceo-satya-nadella-warns-of-reverse-information-paradox-facing-businesses-in-ai-age/article71215870.ece"},
            {"name": "Satya Nadella on X", "url": "https://x.com/sataborasu"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Satya Nadella, Chairman and CEO of Microsoft",
        "image_attribution": "Wikimedia Commons",
        "body": """Satya Nadella has a gift for naming problems that everyone senses but nobody has articulated. His latest: the "Reverse Information Paradox."

In a detailed post on X, the Microsoft CEO drew on Nobel laureate Kenneth Arrow's classic information paradox — where a seller risks giving away knowledge just by trying to sell it — and flipped it. In the age of artificial intelligence, Nadella argued, the buyer is the one at risk.

"You essentially pay for intelligence twice," he wrote. "Once with money, and again with something even more valuable: the proprietary knowledge you must reveal to make that intelligence useful."

## The Paradox, Unpacked

The logic is deceptively simple. To get an AI model to perform well on your company's specific tasks, you need to feed it your data — your customer records, your internal processes, your strategic documents, your corrections when the model gets things wrong. Every prompt, every fine-tuning dataset, every error correction becomes a form of institutional knowledge that flows to the model provider.

"Every correction is distilled into institutional know-how," Nadella wrote. "It's the kind of knowledge a competitor could never buy, and the kind that leaks almost imperceptibly: trace by trace, correction by correction, eval by eval."

Over time, the information asymmetry worsens. The model provider learns more about the buyer. The buyer learns almost nothing about what the provider has absorbed. If learning flows in only one direction, Nadella argued, economic value converges toward the infrastructure owners — not the companies creating the knowledge.

He quoted Palantir CEO Alex Karp to underscore the point: "What the technical customers want is control over their compute, their models, their data stack, and their alpha. They want to know they own the means of production."

## What This Means for Indian IT

The implications for India's $250 billion IT services industry are enormous — and awkward.

Companies like TCS, Infosys, HCLTech, and LTIMindtree are sprinting to position themselves as the deployment layer for enterprise AI. LTIMindtree just signed a partnership with Anthropic and disclosed $150 million in quarterly AI revenue. HCLTech reported $171 million. TCS is restructuring its entire U.S. operation around AI delivery. The business model is straightforward: take a powerful foundation model from OpenAI, Anthropic, or Google, and deploy it inside an enterprise client's workflow.

But Nadella's paradox suggests that model may be structurally compromised. If every deployment feeds proprietary client knowledge back to the model provider — even indirectly, through usage patterns and corrections — then the Indian IT firm is not just a deployer but an unwitting conduit for its clients' intellectual property to leak upstream.

The risk is not theoretical. Model providers explicitly reserve the right to learn from usage data in their terms of service. The better the AI performs for a client, the more that client has revealed. And the Indian IT company in the middle has limited visibility into, or control over, what the model provider retains.

## Nadella's Five-Point Solution

Nadella outlined five principles for enterprises seeking to protect themselves: control, capability, choice, cost, and compounding. In practice, this means building private evaluation environments, retaining ownership of organisational memory, creating proprietary learning loops within a secured boundary, and avoiding lock-in to any single model.

It is also, conveniently, a pitch for Microsoft's own enterprise AI stack — Azure, Copilot, and the company's growing portfolio of proprietary foundation models. If the fear is that using someone else's AI leaks your secrets, the answer Nadella is selling is: use ours, inside a boundary you control.

## The Diaspora Angle

For the hundreds of thousands of Indian-origin professionals working in enterprise AI — whether at the hyperscalers, at IT services firms, or at startups building on foundation models — Nadella's framework redraws the map. The highest-value roles will not be in deployment alone. They will be in building the trust architectures, the private learning environments, and the orchestration layers that let enterprises use AI without surrendering the knowledge that makes them competitive.

The paradox is real. The question is whether Indian IT can solve it before their clients decide to solve it without them."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
