#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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
        "headline": "India Just Minted Its First Space Unicorn. The Money Came From Singapore, BlackRock — and the Founders of Swiggy.",
        "subheadline": "Skyroot's $60 million round crowns a Hyderabad rocket startup at a $1.1 billion valuation. For NRIs who grew up watching ISRO from the sidelines, private Indian space is now an asset class.",
        "slug": make_slug("skyroot-space-unicorn-funding-gic-blackrock-swiggy-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "India's first billion-dollar private space company gives NRI investors and engineers a credible on-ramp into a deep-tech sector that was, until five years ago, entirely closed to anyone outside the government.",
        "tags": ["space-tech", "indian-startups", "skyroot", "isro", "venture-capital", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indias-skyroot-becomes-first-1-bln-space-tech-startup-with-gic-sherpalo-blackrock-2026/"},
            {"name": "Bar & Bench", "url": "https://www.barandbench.com/news/skyroot-rockets-unicorn-status-60-million-fundraise"},
            {"name": "LodeHQ", "url": "https://news.lodehq.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/796206/pexels-photo-796206.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A rocket streaks through a night sky, leaving a luminous trail",
        "image_attribution": "Pexels",
        "body": """Skyroot Aerospace, the Hyderabad rocket company founded by two former ISRO engineers, has become India's first space-technology unicorn. A $60 million round co-led by Singapore's sovereign fund GIC and Silicon Valley's Sherpalo Ventures — with BlackRock among the backers — pushed the eight-year-old startup past a $1.1 billion valuation.

The investor list is the real story. GIC manages part of Singapore's reserves. BlackRock runs the world's largest pile of managed money. Sherpalo's founder, Ram Shriram, was one of Google's earliest backers and now joins Skyroot's board. When capital that conservative writes a cheque to an Indian rocket maker, it is making a statement about how seriously the world now takes India's private space sector.

## Why an Indian rocket startup matters now

For three decades, space in India meant one thing: ISRO, the national agency that put a probe in Mars orbit on a famously thin budget. Private companies were not allowed near launch vehicles. That changed in 2020, when the government opened the sector and created IN-SPACe, a regulator-cum-promoter to let startups use ISRO's facilities. Skyroot was the first company to sign such an agreement.

The timing is sharp. ISRO has stumbled through two consecutive orbital launch failures, and its credibility — long a point of national pride — is under quiet pressure. Skyroot is preparing the maiden flight of Vikram-1, India's first privately developed orbital rocket, and the fresh capital is meant to ramp up launch cadence, expand manufacturing, and fund Vikram-2, a heavier one-tonne-class vehicle with a cryogenic stage.

Co-founder Pawan Kumar Chandana frames the pitch in volume terms: small rockets can be built in weeks and launched 30 to 40 times a year, against the government's two or three over several months. The global market for small-satellite launches is precisely the gap he wants to fill.

## The diaspora angle

This is where the story turns personal for the Indian diaspora. Two details stand out. First, the round drew in not just institutional giants but Indian operator-investors: Swiggy co-founder Sriharsha Majety and former co-founder Nandan Reddy each put roughly ₹5 crore into Skyroot's pre-Series C2 tranche. The founders who built India's food-delivery empire are now backing its rockets — a sign that homegrown wealth is recycling into deep tech, not just into the next quick-commerce clone.

Second, the access question. For an NRI engineer in the Bay Area who grew up watching ISRO launches on a grainy stream, private Indian space was never something you could join or invest in. It was a government job in Bengaluru or nothing. A funded, billion-dollar launch company changes that math. It becomes a place to send capital, a potential employer for aerospace talent weighing a return home, and eventually — if Vikram-1 flies clean and the company heads toward an IPO — a public stock an NRI can actually own.

There is a cautionary note worth keeping. Skyroot is valued at over a billion dollars before its first orbital launch. Vikram-1 has not yet reached orbit. Aerospace is unforgiving, and a single failed maiden flight can reset both timelines and valuations. Diaspora investors tempted by the patriotic pull of "India's first space unicorn" should remember that the hardest engineering is still ahead, not behind.

## What's next

Watch the Vikram-1 maiden launch. A successful orbital insertion would validate the entire thesis and likely pull in a larger Series C at a higher mark. A failure would not kill the company, but it would cool the frenzy that just minted India's newest unicorn. Either way, the diaspora now has a front-row seat to a sector it was locked out of for fifty years — and, for the first time, a way in."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "TCS Just Opened India's First Oracle AI Lab. The Company That Sold Cheap Labor Is Trying to Sell Intelligence Instead.",
        "subheadline": "A new Kolkata center, with four more planned, signals how India's biggest IT firm wants to survive an AI shift that is gutting its old headcount-driven model — the one that put millions of Indians on H-1B visas.",
        "slug": make_slug("tcs-oracle-ai-data-platform-lab-kolkata-it-services-pivot-diaspora"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The pyramid model that staffed thousands of Indian engineers onto H-1B and L-1 visas is being hollowed out by AI; TCS's pivot to AI 'centers of excellence' shows what the diaspora's oldest career ladder is mutating into.",
        "tags": ["tcs", "oracle", "indian-it", "ai", "h1b", "it-services", "diaspora-jobs"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/tcs-launches-indias-first-oracle-ai-data-platform-lab-in-kolkata/article.ece"},
            {"name": "TCS Press Release", "url": "https://www.tcs.com/who-we-are/newsroom/press-release/tcs-oracle-ai-data-platform-lab-kolkata"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/global-firms-bring-more-work-in-house-india-hubs-ai-boost-2026/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3861951/pexels-photo-3861951.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An engineer works on code in a contemporary office",
        "image_attribution": "Pexels",
        "body": """Tata Consultancy Services has opened India's first Oracle AI Data Platform Lab in Kolkata, with four more centers planned across the country over the next three years. On its face it is a routine corporate announcement: a partnership, a ribbon-cutting, a press release full of phrases like "AI-ready data" and "agentic applications." Read it against what is happening to the Indian IT industry, and it looks more like a survival plan.

## The model that is breaking

For two decades, the business of TCS, Infosys, Wipro and their peers rested on a simple shape: a pyramid. A wide base of junior engineers, billed by the hour, doing maintenance, support and code that more expensive onshore consultants would have charged a fortune for. That pyramid is what powered the H-1B and L-1 pipelines, sending hundreds of thousands of Indian engineers to client sites in New Jersey, Texas and California.

AI is dissolving the base of that pyramid. Coding tools are eroding the pricing power of services firms faster than anyone expected. TCS's dollar revenue actually shrank in the year to March 2026 — its first decline since going public in 2004. Just this week, Accenture's stock cratered to a multi-year low on weak bookings, dragging down the US-listed shares of Infosys, Wipro and Cognizant with it. The signal from clients is unambiguous: they will pay for outcomes, not for warm bodies billed by the hour.

## What the Oracle lab really is

This is why a data-platform lab matters more than it sounds. TCS is trying to climb the value chain — from selling labor to selling intelligence. The Kolkata facility is pitched as a place to help enterprises fix fragmented data, build "agentic" AI applications, and deploy automation at scale. The company says it has 26,000 Oracle-skilled staff to throw at the effort.

The deeper shift is about what these centers are for. They are no longer expansion hubs measured by headcount. They are being recast as specialized centers of excellence, where a smaller number of highly skilled engineers build reusable AI assets rather than a large team grinding through bespoke client work. Quality of skill is replacing quantity of staff as the metric that matters.

## Why the diaspora should care

For an Indian engineer at a US client site, or one weighing the H-1B lottery, this is the most important structural story in tech right now — bigger than any single product launch. The onsite model is the part being squeezed hardest. AI-assisted delivery means fewer engineers need to sit next to the client, which means fewer visa-sponsored transfers and more cautious sponsorship even among firms that still hire.

At the same time, global companies are pulling work back in-house at their own India captive centers, or GCCs, because AI makes small internal teams productive enough to skip the outsourcer entirely. That is a double hit to the traditional Indian IT firm: clients buying less, and clients building more themselves.

The opportunity, for those who can reach it, is on the other side of the same trend. The engineers who thrive will be the ones who move from "I can write the code" to "I can design the AI system that writes and governs the code." TCS's lab, and the four to follow, are a bet that India can supply that higher tier of talent. For the diaspora, the lesson is blunt: the old ladder of a CS degree, OPT, the H-1B lottery and a services job is narrowing. The new one runs through AI architecture, data engineering and the ability to orchestrate systems rather than feed them.

## What's next

July brings first-quarter results from TCS, Infosys, HCLTech and Wipro. The numbers, and especially the deal-bookings and hiring commentary, will show whether the AI pivot is generating real revenue or just better slides. Watch the headcount line as closely as the topline — it is the truest measure of whether the pyramid is being rebuilt or quietly retired."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A US Cybersecurity Firm Just Opened in Bengaluru and Said the Quiet Part Out Loud: It Came for the Talent, Not the Discount.",
        "subheadline": "N-able's new India center, and a GCC workforce headed toward 2.36 million, mark a turning point — global firms now build core tech in India because of who is there, not because it is cheap.",
        "slug": make_slug("nable-india-gcc-bengaluru-talent-not-cost-diaspora-tech-jobs"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "As US firms move core engineering — not just support — into India captive centers for the talent, the calculus for NRIs weighing a return home shifts: the best jobs are no longer only in Silicon Valley.",
        "tags": ["gcc", "india-tech", "cybersecurity", "bengaluru", "talent", "return-to-india", "diaspora-jobs"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/us-cybersecurity-firm-n-able-opens-india-gcc-plans-50-local-workforce-expansion-2026/"},
            {"name": "Nasscom-Zinnov", "url": "https://nasscom.in/knowledge-center/publications"}
        ]),
        "score_total": 73,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Close-up of server racks in a data center",
        "image_attribution": "Pexels",
        "body": """When a US company opens an office in India, the assumption — for thirty years — was that it was chasing cheaper labor. N-able, an American cybersecurity firm that protects more than 500,000 organizations worldwide, just opened a Global Capability Center in Bengaluru and went out of its way to say the assumption is wrong.

"The reason we're in Bengaluru is capability," CEO John Pagliuca told Reuters. The move, he insisted, was "driven primarily by access to talent rather than cost reduction." The center already employs more than 100 people, and N-able plans to grow its India headcount by at least 50% by the end of 2026, building defensive AI capabilities — automated threat detection, monitoring, faster incident response — out of the Bengaluru team.

## The GCC inflection point

N-able is one data point in a wave. India's GCC workforce — the in-house centers that multinationals run rather than outsourcing — is projected to hit 2.36 million employees by the end of 2026, according to industry body Nasscom and consultancy Zinnov. AI and cybersecurity are driving much of that demand.

The important shift is in what these centers do. The first generation of India offices ran payroll, answered support tickets and tested software — the back office of the global economy. The new generation owns core functions: engineering, product development, performance-critical algorithms, security research. At Daimler Truck's Bengaluru hub, the company is bringing the development of safety-critical vehicle software in-house. Target says it already does the "vast majority" of its tech in India internally. The work being placed in India is now the work companies consider their competitive edge — exactly the opposite of the commodity tasks the country was once handed.

## Why this reframes the diaspora's choices

For decades, the implicit deal for an ambitious Indian engineer was clear: the interesting, high-stakes, well-paid work lived in Silicon Valley, Seattle and London. India was where you ran the support center or, at best, the offshore delivery arm. To work on the frontier, you left.

That deal is being rewritten. When a US security firm builds its AI defense systems in Bengaluru, and when a German automaker writes its safety-critical code there, the frontier work is no longer geographically exclusive. For an NRI in the Bay Area watching H-1B sponsorship tighten, layoffs mount, and the 60-day grace-period clock loom over every job change, the option of returning to a GCC role in Bengaluru or Hyderabad is no longer a step down. Increasingly it is a lateral move — sometimes onto more interesting work, with equity in the parent company and without the visa anxiety.

There is a catch the diaspora should weigh honestly. The GCC boom is contested ground: multinationals, Indian IT firms and local startups are all fishing in the same talent pool, and Pagliuca admitted that AI engineering, cloud security and threat research are among the hardest skills to source anywhere. Compensation in these roles is rising fast, but it still does not match Bay Area cash. The trade is lifestyle, family proximity and immigration certainty against raw dollars — and for a growing number of mid-career NRIs, that trade is finally tilting.

## What's next

Watch whether the GCC wave moves up the seniority ladder. So far it has absorbed engineers and managers; the open question is whether global firms will start placing senior leadership — VPs of engineering, product heads, business-line owners — in India rather than treating it as a cost-efficient extension of headquarters. The day a major US firm runs a global business line out of Bengaluru is the day the diaspora's geography of ambition truly flips."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")

print(f"\n{len(inserted)} article(s) inserted:")
for h in inserted:
    print(f" - {h}")
