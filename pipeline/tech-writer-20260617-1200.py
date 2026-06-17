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
        "headline": "Adani Just Recruited an Apple Supplier to Build India's AI Hardware. The Bet Is That Compute Follows Cheap Power.",
        "subheadline": "A new alliance between the Adani Group and Florida's Jabil aims to manufacture multi-gigawatt AI data-center racks inside India — the clearest sign yet that the country wants to build the machines the world's models run on, not just write the code.",
        "slug": make_slug("adani-jabil-ai-data-center-hardware-manufacturing-india-alliance"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs who have spent careers inside American data centers and chip supply chains, India's push to manufacture AI hardware at home opens a homecoming option that did not exist a year ago — and a fresh thesis for diaspora investors tracking Adani's stocks.",
        "tags": ["adani", "jabil", "ai-infrastructure", "data-centers", "indian-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/apple-supplier-jabil-adani-partner-build-ai-data-center-infra-platform-india-2026-06-15/"},
            {"name": "BusinessWire", "url": "https://www.businesswire.com/news/home/20260615/en/"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/adani-group-partners-with-jabil-to-build-ai-data-infrastructure/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/companies/"}
        ]),
        "score_total": 83,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/ff/Gautam_Adani.jpg",
        "image_caption": "Adani Group chairman Gautam Adani, whose conglomerate has partnered with U.S. manufacturer Jabil to build AI data-center hardware in India.",
        "image_attribution": "Wikimedia Commons",
        "body": """For a decade, India's role in the global technology stack has been defined by one word: software. The country writes the code, staffs the back offices, and runs the support desks. The machines that actually do the computing have always been built somewhere else — Taiwan, China, the American Southwest. On June 15, the Adani Group and Jabil Inc. announced a plan to change that, and the ambition is large enough that NRIs in the chip and data-center business should read it twice.

The two companies said they intend to form a strategic alliance to build a "vertically integrated" AI and data-center infrastructure manufacturing platform inside India. In plain terms: factories that produce the physical guts of an AI data center — liquid-cooled server racks, storage, networking gear — at "multi-gigawatt" scale, alongside the unglamorous but essential supporting hardware: power distribution units, coolant distribution units, transformers, switchgears, bus bars, thermal-management systems. The pitch is a single-source, design-to-deployment hardware ecosystem, aimed at global hyperscalers and Indian enterprises alike.

Jabil is not a random partner. The St. Petersburg, Florida company (NYSE: JBL) counts Apple among its customers and has six decades of contract-manufacturing pedigree. In February it raised its annual forecast on the strength of AI data-center demand. Pairing that manufacturing muscle with Adani's land, logistics, and — crucially — green energy is the whole logic of the deal.

## The energy-compute symmetry

Gautam Adani framed the announcement in characteristically grand terms. "The world is entering an Intelligence Revolution more profound than any previous Industrial Revolution," he said. "Nations that master the symmetry between energy and compute will shape the next decade."

Strip away the rhetoric and there is a real insight underneath. AI data centers are, fundamentally, devices for converting electricity into computation. Whoever supplies the cheapest, most reliable power has a structural edge in hosting them. Adani's bet — backed by a $100 billion commitment announced in February to build renewable-powered, hyperscale AI-ready data centers by 2035 — is that India's solar-heavy energy buildout can make the country a natural home for compute, and that it might as well manufacture the hardware on the same soil.

The market opportunity is concrete. India's data-center capacity is projected to reach 5-8 GW by 2030, propelled by data-localization laws that require Indian user data to stay in-country and by tax incentives for domestic manufacturing. Over $50 billion in spending is planned across data center, cloud, and AI ecosystems. Adani has already tied up with Uber for its first Indian data center, due to go live later this year, and has reportedly explored partnerships with Meta and Google.

## Why this matters to the diaspora

There are two NRI audiences with a stake here, and they are watching different things.

The first is the engineer and operations professional. A generation of Indian-origin talent has built careers inside American hyperscale data centers, semiconductor fabs, and hardware supply chains — the people who know how to stand up a liquid-cooled rack farm and keep it running. For years, the only way to do that work at the frontier was to do it in Phoenix or Virginia. An Indian manufacturing platform at gigawatt scale, if it materializes, creates senior roles at home that simply did not exist before. For anyone weighing a return, that changes the math.

The second is the investor. For the diaspora that tracks Adani Enterprises and the group's listed entities, this is a new growth narrative layered on top of ports, power, and airports. Hardware manufacturing is capital-intensive and margin-thin, and the companies were careful to note that operational frameworks and formal documentation are still being finalized, with no firm timeline. That caution is the tell: this is an intent, not a ribbon-cutting.

## The catch

India has announced manufacturing revolutions before — in solar, in phones, in semiconductors — with mixed results. The hard parts here are the same as always: building a domestic component supply chain so the "vertical integration" is not just final assembly of imported parts, securing the skilled workforce, and competing on cost with entrenched Asian manufacturers. A press release describing "intent" is the easy part.

But the direction of travel is unmistakable. India spent the software era renting out its brains. The Adani-Jabil alliance is a bet that the AI era is a chance to build the body too — and to do it powered by the country's own sun."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Wall Street Just Downgraded the Companies That Employ the Indian Diaspora. The Reason Should Worry Every IT Worker.",
        "subheadline": "Morgan Stanley cut Accenture and turned cautious on the entire US IT-services industry, warning that AI spending is crowding out the consulting budgets that pay hundreds of thousands of Indian-origin professionals.",
        "slug": make_slug("morgan-stanley-downgrades-accenture-it-services-diaspora-jobs"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Accenture, Cognizant, Capgemini and the Indian IT majors employ vast numbers of Indian and Indian-American workers. A Wall Street downgrade of the whole industry is an early-warning signal about the career ground beneath the diaspora's feet.",
        "tags": ["accenture", "it-services", "morgan-stanley", "indian-tech", "ai-disruption"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "AInvest", "url": "https://www.ainvest.com/news/accenture-fell-morgan-stanley-ai-budget-rationalization-happened/"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NYSE/ACN/price-target/"},
            {"name": "Investopedia", "url": "https://www.investopedia.com/accenture-stock-earnings-preview"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35118208/pexels-photo-35118208.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A candlestick chart showing a downward trend; Morgan Stanley downgraded Accenture and the broader US IT-services industry.",
        "image_attribution": "Pexels",
        "body": """When a Wall Street bank downgrades a single stock, it is a trade. When it downgrades an entire industry, it is a warning. On June 15, Morgan Stanley did both — and the industry in question is the one that pays a large share of the Indian diaspora's salaries.

The bank's analyst James Faucette cut Accenture to Equal Weight from Overweight and slashed his price target to $177 from $240. More striking was the second move: Morgan Stanley downgraded the US IT-services industry as a whole from neutral to cautious. The logic was not that artificial intelligence demand is fading. The bank still expects nearly $3 trillion of AI-related infrastructure investment by 2028. The problem is where that money is going — and it is not going to the consultants.

## The budget math that should unsettle the diaspora

Morgan Stanley's latest survey of chief information officers found that IT-services budgets are expected to grow just 2% in 2026. Total IT budgets, by contrast, are growing about 3.7%. That gap is the whole story. Companies are still spending on technology — they are just spending it on AI infrastructure, chips, and cloud, rather than on the armies of consultants and systems integrators that have long done the hands-on work.

The bank's blunt conclusion: AI investment "may crowd out IT-services budgets, increase pricing pressure, and dilute returns on invested capital." For an industry built on billing human hours, an efficiency technology that lets clients do more with fewer people is not a tailwind. It is the tide going out.

The market has already noticed. Accenture shares have lost nearly 40% of their value since the start of the year, and a string of banks — Susquehanna, Jefferies, Citigroup, Truist — have cut targets in recent weeks. The company reports earnings on June 18, and options pricing implies a swing of up to 7% in either direction.

## Why this is a diaspora story

Walk into Accenture, Cognizant, or Capgemini and you will find a workforce that is heavily Indian and Indian-American — from H-1B engineers in U.S. delivery centers to the hundreds of thousands of staff across Bengaluru, Hyderabad, Pune, and Chennai. The Indian IT majors — TCS, Infosys, Wipro — face the same structural squeeze and the same client CIOs holding the same flat budgets. When Wall Street turns cautious on this sector, it is turning cautious on the single largest employer category for the global Indian tech middle class.

The threat is not a single round of layoffs. It is a slow re-rating of the entire business model. The IT-services industry was built on a "labor arbitrage" foundation — selling skilled human effort at scale. The middle layer of that model, the project managers and mid-level engineers who translated client requirements into delivered code, is exactly the layer AI agents are now coming for. TCS chairman N. Chandrasekaran said as much at the company's recent annual meeting, conceding that AI will lead to a decrease in hiring and describing a future with as many AI agents as human staff.

## What an NRI in the industry should actually take away

Three things.

First, read the downgrade as a career signal, not just a stock note. If your role is the billable middle — coordinating, translating, managing delivery — that is the layer under the most pressure. The defensible roles are at the edges: deep technical specialization on one end, genuine client and domain expertise on the other.

Second, watch where the $3 trillion goes. Morgan Stanley is not bearish on technology; it is bearish on a particular way of selling it. The same forces hammering IT services are creating demand in AI infrastructure, data engineering, and the "responsible-AI" and governance roles that did not exist three years ago. The skills migrate; the paycheck follows.

Third, do not panic, but do not coast. The industry that brought a generation of Indian professionals to America and built the modern Indian middle class is not collapsing. But it is being repriced in real time, by the very technology its clients are racing to adopt. The smart move is to be the person building the new thing, not maintaining the old one."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art["body"].split())
        print(f"OK  {art['slug']}  ({wc} words)")
    except Exception as e:
        print(f"FAIL  {art['slug']}: {e}")
