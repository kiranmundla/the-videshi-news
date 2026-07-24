#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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
        "headline": "Forty Per Cent More Indian Tech Workers Moved Home Last Year. Silicon Valley Is Starting to Notice.",
        "subheadline": "LinkedIn data confirms a dramatic reverse-migration surge as H-1B costs spike, GCCs multiply, and a generation of senior engineers decides that Bangalore's upside now outweighs the Bay Area's.",
        "slug": make_slug("india-reverse-migration-tech-talent-40-percent-rise-gcc-h1b"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The reverse-migration wave is rewriting the traditional NRI career script — for the first time in decades, experienced Indian-origin professionals are choosing to leave the US not because of failure but because India's opportunities now compete with Silicon Valley's. The shift raises existential questions for the diaspora: is the dream of an American career still the default, or has the calculus permanently changed?",
        "tags": ["nri", "diaspora", "reverse-migration", "tech", "h1b", "gcc", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TechGig", "url": "https://www.techgig.com/"},
            {"name": "Computerworld", "url": "https://www.computerworld.com/"},
            {"name": "Nearshore Americas / Bloomberg / LinkedIn", "url": "https://nearshoreamericas.com/"},
            {"name": "Observer Research Foundation", "url": "https://www.orfonline.org/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/ITPL_Bangalore_1.jpg/1280px-ITPL_Bangalore_1.jpg",
        "image_caption": "The International Tech Park in Bangalore, one of India's largest technology hubs absorbing returning diaspora talent",
        "image_attribution": "Wikimedia Commons",
        "body": """For most of the past three decades, the arrow pointed one way. Indian engineers graduated from an IIT, landed an H-1B, and climbed the ranks in Cupertino, Redmond, or Mountain View. The best might return to India one day — after the green card, after the kids' college funds were set, after enough frequent-flyer miles to fill a Boeing 787. It was a retirement plan, not a career move.

That script is being rewritten. According to LinkedIn data analysed by Bloomberg, the number of technology professionals changing their listed location from the United States to India surged by forty per cent in 2025. These are not junior developers returning after failed visa renewals. They are senior engineers, product leaders, and vice-presidents stepping into roles at India's rapidly expanding Global Capability Centres, AI startups, and deeptech ventures.

## The $100,000 Question

The catalyst has a precise dollar figure. In September 2025, the Trump administration imposed a $100,000 annual fee on employers sponsoring H-1B workers — ostensibly to curb fraud, but in practice a seismic repricing of foreign talent in the American labour market. The fee fundamentally altered the economics of hiring Indian engineers on US soil.

"This imposition has simply made it more difficult, whereas sourcing through offshore centres in India has long been a much more predictable path for US enterprises to gain access to technical talent at scale," Ashutosh Sharma, vice-president and research director at Forrester, told Computerworld.

The numbers bear this out. Meta, Apple, Google, Amazon, Microsoft, and Netflix collectively added more than 32,000 jobs in India during 2025 — an eighteen per cent year-over-year increase, according to staffing firm Xpheno. For the first time, the top four H-1B approvals for new employment went exclusively to American companies: Amazon with 4,644, Meta with 1,555, Microsoft with 1,394, and Google with 1,050. These firms are hiring to support a combined $380 billion in AI-related capital expenditure — but increasingly, they are hiring where the talent already lives.

## Not Just Push — Pull

The story is not simply about American doors closing. India has built a gravitational pull of its own. The country's GCC ecosystem — offices where multinational corporations run everything from engineering to strategy — now employs well over a million professionals and is growing at roughly fifteen per cent annually. Roles that once existed only in San Jose or Seattle — chief technology officer, head of AI research, vice-president of product — are materialising in Bangalore, Hyderabad, and Pune.

India's government has also sharpened its pitch. Programmes such as Bharat-Talent and Bharat-Return offer fast-track visas and tax incentives to non-resident professionals considering a move. The message is blunt: come build at home, and we will make it worth your while.

Shalu Bindlish, director at talent recruitment firm Advaita Bedanta Consultants, said the reversal became visible in recent months. "We have seen Indian tech talents looking for jobs in India rather than moving to the US," she said. "Now thirty to forty per cent of students are keen for Indian jobs after studying in the US, which was unprecedented."

## The Returnee Paradox

Yet the homecoming is not without friction. A detailed study by the Observer Research Foundation found that while returnees contribute disproportionately to knowledge-intensive sectors and bring global best practices, they sometimes struggle with India's business culture, its pace of institutional decision-making, and the sheer density of its domestic competition. Domestic founders — the "hometown heroes" who never left — still lead the majority of India's largest funding rounds and unicorn valuations.

The implication is nuanced. Returnees are not the saviours of Indian tech; they are a vital ingredient in a recipe that also requires local context, institutional patience, and networks that take years to build. The most successful transitions tend to happen when returnees join existing ecosystems rather than trying to transplant Silicon Valley wholesale.

## A Permanent Shift or a Cyclical Swing?

Previous reverse-migration waves — after the 2001 dot-com bust, after the 2008 financial crisis — proved temporary. When America's tech economy recovered, the talent flowed back. This time, several structural factors suggest the shift may be stickier.

The H-1B fee is unlikely to be reversed under any near-term political configuration. India's AI and semiconductor ambitions enjoy bipartisan government support and serious capital backing. And a generation of engineers who built careers remotely during the pandemic have already proved that geography is not destiny.

For the Indian diaspora, the calculus is no longer binary. The question is not whether to stay or go. It is where, within a genuinely global career, the next decade's best chapter will be written. For a growing number, the answer is Bangalore."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Americans Gave Up to Five Billion Dollars Last Year. The Community's Philanthropy Gap Is Finally Closing.",
        "subheadline": "A landmark survey shows Indian American giving has more than doubled as a share of income since 2018, shrinking a long-documented philanthropy deficit — and a new generation of donors is rewriting the playbook.",
        "slug": make_slug("indian-american-diaspora-philanthropy-5-billion-giving-gap"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For years, the Indian American community — despite being the highest-earning ethnic group in the US — was known for a stubborn philanthropy gap. This new data shows that gap is finally closing, driven by organised giving campaigns, generational shifts, and a growing sense that giving back is integral to diaspora identity. The trend matters to every NRI navigating the dual pull of contributing to both American and Indian causes.",
        "tags": ["nri", "diaspora", "philanthropy", "india-giving-day", "indiaspora", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The American Bazaar", "url": "https://www.americanbazaaronline.com/"},
            {"name": "Indiaspora", "url": "https://indiaspora.org/"},
            {"name": "India Philanthropy Alliance", "url": "https://indiaphilanthropyalliance.org/"},
            {"name": "Dalberg / IPA Survey 2025", "url": "https://indiaspora.org/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6646926/pexels-photo-6646926.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Community volunteers organising donations and supplies at a charity event",
        "image_attribution": "Pexels",
        "body": """The Indian American community has a reputation problem — the pleasant kind. It is the highest-earning ethnic group in the United States, with a median household income that eclipses every other demographic. Its members run some of the world's most valuable companies, hold senior positions across medicine, law, and technology, and send billions in remittances to India each year. By almost any economic measure, Indian Americans have arrived.

But for years, the community's philanthropy lagged behind its prosperity. Study after study documented a "giving gap" — the difference between what Indian Americans donated and what their income levels predicted they should give, benchmarked against comparable American communities. The gap was estimated at two to three billion dollars annually. The money was there; the giving culture, researchers argued, had not yet caught up.

That narrative is changing. A comprehensive survey released in late 2025 by Indiaspora, the India Philanthropy Alliance, and consulting firm Dalberg found that Indian American giving has risen sharply — from roughly one to two per cent of household income in 2018 to four to five per cent by 2024. In absolute terms, total Indian American diaspora giving now stands at an estimated four to five billion dollars annually. The giving gap has shrunk from two to three billion dollars to approximately one billion — a remarkable narrowing in just six years.

## The India Giving Day Effect

The shift did not happen by accident. A constellation of organisations has spent the better part of a decade building the infrastructure of Indian American philanthropy, and the results are now visible.

India Giving Day 2026, organised by the India Philanthropy Alliance, raised $5.6 million from 2,325 donors — more than a thousand of whom gave for the first time. Over sixty events were held nationwide, with a combined attendance exceeding 3,500. "This interest from the younger generation is heartening to see," Meenakshi Mahajan, deputy director of IPA, told The American Bazaar. "This is what evolution looks like, when future generations also engage and lead."

The campaign builds on the ChaloGive initiative launched by Indiaspora, which raised more than $15 million for COVID-19 relief in India and provided over eight million meals to people in both the US and India during the pandemic. What began as emergency generosity has evolved into a durable giving habit.

## Three Times the National Average

Perhaps the most striking finding in the survey is not about money at all. Indian Americans now volunteer their time at nearly triple the national American average. That figure challenges a persistent stereotype — that the community's relationship with giving is transactional, driven by tax optimisation or temple donations rather than deep civic engagement.

The data suggests something more fundamental is at play. As the Indian American population has grown — it now numbers over five million — community organisations have proliferated, and with them, a culture of local involvement that extends well beyond writing cheques to alma maters or building hospitals in ancestral villages.

The India Philanthropy Alliance itself reflects this evolution. Founded on the 150th birth anniversary of Mahatma Gandhi, the alliance has grown to twenty-one member organisations. Its annual giving day has scaled from modest beginnings to a nationally coordinated mobilisation, with young professionals and second-generation Indian Americans increasingly taking the lead.

## The $730 Billion Community

Context matters. A major report released by Indiaspora at its 2026 Forum in Bangalore — titled "India and its Diaspora: Partners in Progress" — quantified the global Indian diaspora's economic footprint: more than 35 million people across 200 countries, with an estimated combined annual income of $730 billion. The report argued that the diaspora's relationship with India has evolved beyond remittances — which themselves hit a record $145 billion in 2025, with the United States as the largest single source — into a more complex web of investment, knowledge transfer, technology partnerships, and yes, structured philanthropy.

"The giving gap fell by half — from an average of eight per cent in 2018 to four per cent in 2024," the survey noted. The "passion-giving gap" — the difference between what donors care about and where they actually direct their money — has also narrowed, suggesting that Indian Americans are increasingly able to align their donations with causes that genuinely move them, rather than defaulting to obligation-driven giving.

## What Remains

A billion-dollar gap still exists, and closing it will require more than goodwill. The survey highlighted the importance of donor education, institutional transparency from Indian nonprofits, and the active engagement of second- and third-generation diaspora members — many of whom feel a connection to India but channel their philanthropy toward American causes closer to their daily lives.

There is also a question of ambition. Sunil Wadhwani, the Pittsburgh-based tech entrepreneur who first challenged the community to close its giving gap nearly a decade ago, framed it as a test of collective identity: could the most economically successful immigrant community in American history also become one of its most generous?

The latest numbers suggest the answer is trending toward yes — not through grand gestures from billionaire philanthropists, but through the steady accumulation of five-figure donations, weekend volunteering shifts, and twenty-dollar contributions from first-time donors who clicked a link during India Giving Day. The revolution, it turns out, is being crowdsourced."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
