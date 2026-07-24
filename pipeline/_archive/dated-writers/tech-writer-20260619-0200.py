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

# ---------------------------------------------------------------------------
# ARTICLE 1 — EV two-wheeler shakeout (mobility beat)
# ---------------------------------------------------------------------------
body1 = """India's electric scooter market was supposed to be Ola Electric's to lose. For a stretch in 2024, the SoftBank-backed startup held nearly half of it, and its founder Bhavish Aggarwal sold a story the diaspora knew well: the scrappy Indian disruptor that would leapfrog legacy giants the way Reliance Jio once did in telecom. Two years on, that story has inverted. The disruptors are now the incumbents, and the incumbents are winning.

The numbers from May are blunt. India's total two-wheeler sales rose nearly 15% year-on-year to roughly 1.9 million units, with scooters the standout, up more than 27%. But the electric crown has changed heads. TVS Motor finished FY26 as the top electric two-wheeler retailer with over 341,000 units, up 43%. Bajaj Auto followed with 289,000, and Ather Energy — long the quiet, engineering-led brand — surged 82% to roughly 239,000. Ola, meanwhile, fell off a cliff: retail sales collapsed 52% to about 164,000 units, less than half of what it sold the year before.

## What broke

Ola's decline was not about technology or even price. It was about the unglamorous work of after-sales service. Customers who bought on hype found themselves stranded by slow repairs and patchy support, and word travelled fast on the same social platforms that once amplified the brand. Ola responded by shrinking its retail footprint from around 4,000 stores to roughly 700 and pouring $214 million into in-house battery cells and automation, betting that vertical integration will eventually deliver the profitability it has never posted.

Ather is running the opposite playbook. It plans to nearly double its store count to over 1,100 by March 2027 — opening more than one store a day — wagering that distribution depth and service reliability, not viral launches, are the real moat in a market where buyers are now replacing old scooters rather than experimenting.

## Why an NRI should care

For the diaspora, this is more than a spectator sport. Three of these companies — Ola Electric, Ather Energy and Bajaj — are publicly listed, and NRIs investing through GIFT City brokerages or family demat accounts back home have watched the volatility firsthand. Ola's stock has rallied nearly 60% in two months even as its sales cratered, a disconnect that should give any investor pause: in India's EV story, share price and market share have quietly decoupled.

There is a sharper lesson buried here for the Indian engineer in San Jose or London weighing a return-to-India bet, or an NRI angel writing cheques into Indian mobility startups. The market has shifted from disruption-led growth to execution-led competition. River Mobility, a Bengaluru startup, grew over 400% by quietly targeting a utility niche; Hero's Vida brand leapt 196%. The winners are not the loudest. They are the ones who fixed the scooter when it broke.

## What's next

The structural tailwind is real. Electric two-wheelers crossed 1.4 million units in FY26, and Delhi's draft policy would mandate that all new two-wheelers sold from April 2028 be electric — a regulatory cliff that will force the laggards either to scale or to exit. Prime Minister Modi's recent push to cut fuel imports sent EV stocks higher across the board. For diaspora investors, the trade is no longer "buy the disruptor." It is "buy the operator" — and in Indian EVs, those have turned out to be very different companies."""

# ---------------------------------------------------------------------------
# ARTICLE 2 — Bharat Innovates / DeepTech (ecosystem beat)
# ---------------------------------------------------------------------------
body2 = """For two decades, the story of Indian deep tech was a story of leaving. The brightest engineers from the IITs flew to Stanford and MIT, the breakthroughs were patented in California, and India supplied the talent while America captured the value. The three-day Bharat Innovates 2026 summit, which wrapped this week, was an attempt to rewrite that script — and it was held, pointedly, not in Bengaluru but in Nice, France.

The headline numbers were respectable. By the second day, the summit had facilitated roughly $254.5 million in funding commitments and advanced-stage investments into Indian deep-tech startups, with more than 80 companies pitching to over 50 global investors from more than ten countries. IIT Madras and its global arm signed seven commercial MoUs — mostly with French partners — expected to unlock close to $100 million in value, involving startups such as space-launch firm Agnikul Cosmos, industrial-AI company Detect Technologies, and TuTr Hyperloop.

## The pitch behind the pitch

What makes this different from the usual investment-summit theatre is where the money is being pointed: space, semiconductors, defence supply chains, and AI — the capital-intensive, patient-money sectors that India's consumer-app boom conspicuously skipped. IIT Madras director V. Kamakoti called it a "watershed moment," and for once the hyperbole has some grounding. Agnikul, which flew the world's first single-piece 3D-printed rocket engine, and Skyroot, which just became India's first space-tech unicorn ahead of a maiden orbital launch, are the kind of hard-tech names that did not exist in India's startup vocabulary five years ago.

## Why this matters to the diaspora

For NRIs, Bharat Innovates is a quiet invitation. The new institutional vehicles announced — the Bharat Innovates Fund, run with Agna Capital, and a tie-up to help Indian startups scale into German and French markets — are explicitly designed to channel cross-border capital into Indian deep tech. That is a structural opening for diaspora investors who have spent years watching India's tech wealth from the sidelines, able to buy Infosys shares but locked out of the early-stage frontier where the real returns sit.

It also reframes the return-to-India calculation for a generation of diaspora engineers. A semiconductor designer at Intel watching layoffs sweep through Santa Clara, or a propulsion engineer at a US space firm, now has something India could not offer a decade ago: domestic startups doing genuinely hard work, backed by patient capital and a government that has made deep tech a strategic priority. The pitch is no longer "come home and take a pay cut for patriotism." It is "come home and build the thing you would have built here anyway."

## The caveats

Summits are easy; execution is hard. India's deep-tech ecosystem still raises a fraction of what flows into a single mid-tier Silicon Valley AI startup, and MoUs have a long history of dissolving into press releases. The fact that the marquee event was held in France — a bid for European capital and credibility — is itself a tell that domestic funding remains thin. But the direction of travel is unmistakable. For the diaspora, the question is shifting from whether India can build deep tech to whether they want a stake in it before the rest of the world figures out the answer."""

# ---------------------------------------------------------------------------
# ARTICLE 3 — NVIDIA agentic compute / Computex (AI infra beat)
# ---------------------------------------------------------------------------
body3 = """At Computex in Taipei, Jensen Huang spent two hours making an argument that should unsettle anyone whose career rests on writing code. The most demanding customer for computing, the NVIDIA chief executive said, is no longer a human. It is software — AI agents running thousands of tool calls in sequence, machines that "never sleep, never wait, and exist in numbers that will dwarf the human population." For the millions of Indian engineers who built their livelihoods serving human users, that is not a product update. It is a warning about the shape of the work to come.

The technical news was that NVIDIA's new Vera CPU — not another GPU — was the star. Huang framed it as a chip designed for agents rather than people: low-latency, high-throughput, engineered for the orchestration layer beneath autonomous software. NVIDIA claims roughly 1.8 times the agentic performance of incumbent x86 chips and around three times faster data processing. The company also confirmed its Vera Rubin platform is in full production, with rack assembly compressed to minutes, and launched a cheaper open model, Nemotron 3 Ultra. The mantra repeated through the keynote: "Compute is revenue, compute is profit."

## The Indian fingerprints

Strip away the showmanship and the diaspora is everywhere in this story. Indian engineers are disproportionately represented in NVIDIA's software stack, in the hyperscaler teams at Microsoft, Google and AWS racing to deploy these agents, and in the IT-services giants — TCS, Infosys, Wipro, Cognizant — whose entire business model is built on supplying human developers by the tens of thousands. When Huang says the customer is now an agent, he is describing a future where the unit India has exported for thirty years — billable human hours of coding — becomes the thing the technology is built to replace.

## Why this lands hard for NRIs

For the Indian engineer on an H-1B at a Bay Area firm, the agentic shift cuts two ways. The optimistic read is that someone has to build, govern and orchestrate these agents, and that work is harder and better paid than the code it displaces — a move up the value chain that India's best engineers are well positioned to make. The pessimistic read is that the "conveyor belt" of entry-level coding jobs, the rung that brought generations of Indian engineers to America in the first place, is precisely what agents eat first. India's tech hiring already hit a 28-month low this year. Companies like eBay are cutting American jobs while filing H-1B petitions, fueling a political backlash that lands on Indian workers regardless of the cause.

## The bottom line

Huang's other message in Taipei was geopolitical: AI infrastructure, he insisted, would increasingly be "made in America," with chipmaking centred in Arizona and assembly in Texas. That domestic-supply-chain push, blessed by both the Biden and Trump administrations, is good for US resilience but complicates the offshore model that built India's IT industry. The diaspora's edge was always being the people who did the work. The uncomfortable question Computex posed is what happens when the most valuable work is teaching machines to do it instead — and whether Indian engineers end up writing that future or being written out of it."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Ola Electric Was Supposed to Win India's EV Race. It Just Lost Half Its Market in a Year.",
        "subheadline": "TVS, Bajaj and a quietly relentless Ather have overtaken the one-time disruptor — and diaspora investors are learning that share price and market share have decoupled.",
        "slug": make_slug("ola-electric-india-ev-two-wheeler-shakeout-tvs-ather-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Three of India's top EV two-wheeler makers are publicly listed, and NRIs investing through GIFT City and family demat accounts are watching a market where execution, not hype, now decides the winners.",
        "tags": ["india-ev", "ola-electric", "ather-energy", "tvs-motor", "nri-investors", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "BikeWale — Electric Two-Wheelers FY26 Retail Growth", "url": "https://www.bikewale.com/news/"},
            {"name": "Rushlane — Top 10 Two Wheelers May 2026", "url": "https://www.rushlane.com/"},
            {"name": "Livemint — Ather distribution push vs Ola", "url": "https://www.livemint.com/"},
            {"name": "Reuters — Ola Electric to invest $208.5 million", "url": "https://www.reuters.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37807346/pexels-photo-37807346.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An electric scooter plugged into a city charging station as India's EV two-wheeler market accelerates",
        "image_attribution": "Pexels",
        "body": body1,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Deep-Tech Pitch Just Raised $254 Million — in France. For the Diaspora, It's an Invitation.",
        "subheadline": "Bharat Innovates 2026 channelled capital into space, chips and AI, and launched cross-border funds aimed squarely at NRIs who have watched India's tech wealth from the sidelines.",
        "slug": make_slug("bharat-innovates-2026-deep-tech-funding-nice-nri-investors-space-semiconductors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "New cross-border funds unveiled at the summit are designed to let diaspora investors and returning engineers buy into India's hard-tech frontier — space, semiconductors, AI — for the first time at the early stage.",
        "tags": ["india-deep-tech", "startups", "agnikul", "skyroot", "nri-investors", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "IANS — Bharat Innovates 2026 secures $254.5M", "url": "https://www.ianslive.in/"},
            {"name": "The Hindu BusinessLine — IIT Madras startups sign $100M MoUs", "url": "https://www.thehindubusinessline.com/"},
            {"name": "TechCrunch — Skyroot becomes India's first space-tech unicorn", "url": "https://techcrunch.com/"}
        ]),
        "score_total": 71,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18999276/pexels-photo-18999276.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A presenter pitches before an audience, evoking the startup-investor sessions at Bharat Innovates 2026",
        "image_attribution": "Pexels",
        "body": body2,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Jensen Huang Says the AI Era's Top Customer Isn't Human. India's Coders Should Listen Closely.",
        "subheadline": "At Computex, NVIDIA pitched a future built for software agents, not people — and the work India has exported for thirty years is exactly what those agents replace first.",
        "slug": make_slug("nvidia-jensen-huang-computex-agentic-ai-vera-cpu-indian-engineers-it-jobs"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian engineers fill NVIDIA's software stack, the hyperscaler AI teams, and the IT-services giants whose billable-human-hours model is precisely what agentic computing threatens to automate away.",
        "tags": ["nvidia", "agentic-ai", "jensen-huang", "it-services", "h1b", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "BusinessWire — HPE and NVIDIA agentic AI", "url": "https://www.businesswire.com/"},
            {"name": "Barchart — Nvidia's Huang pledges AI manufacturing jobs", "url": "https://www.barchart.com/"},
            {"name": "Daily Caller — Nvidia CEO warns way of life will change", "url": "https://dailycaller.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Jen-Hsun_Huang_2025.jpg/330px-Jen-Hsun_Huang_2025.jpg",
        "image_caption": "NVIDIA founder and CEO Jensen Huang, who used Computex 2026 to argue AI agents are computing's new primary customer",
        "image_attribution": "Wikimedia Commons",
        "body": body3,
    },
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  [{art['slug']}] words={wc}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
