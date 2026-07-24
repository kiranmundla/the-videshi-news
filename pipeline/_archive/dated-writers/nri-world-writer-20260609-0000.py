#!/usr/bin/env python3
"""Videshi NRI World Writer — 2026-06-09 00:00 UTC batch"""

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


# ── ARTICLE 1: Paul & Daisy Soros Fellowships ───────────────────────────

article1_body = """Eight Indian Americans are among the 30 winners of this year's Paul & Daisy Soros Fellowships for New Americans, a programme that has quietly become one of the most reliable barometers of immigrant talent flowing through America's graduate schools.

Dhruv Gaur, Jaspreet Kaur, Omair M. Khan, Nathan Mallipeddi, Arjun Menta, Vaibhav Mohanty, Shyamala Ramakrishna, and Shomik Verma will each receive up to $90,000 in funding to pursue graduate studies at institutions including Harvard, MIT, Stanford, and Yale. That eight of thirty slots — more than a quarter — went to candidates of Indian origin is not an anomaly. It is a pattern the fellowship has traced for years, one that maps neatly onto the community's outsized presence in American research and professional life.

## From DACA to the Director's Chair

The cohort's range is striking. Dhruv Gaur is pursuing a PhD in economics at MIT, studying how severe marginalisation affects health outcomes — work that sits at the intersection of development economics and public health. Jaspreet Kaur, a DACA recipient from India and Harvard graduate, is enrolled in USC's MFA programme for writing for screen and television. Her ambition is to create films that centre the stories of communities rarely seen on American screens. Hers is the kind of trajectory the Soros Fellowship was designed to spotlight: an immigrant navigating legal precarity while building a creative career that talks back to the culture that both welcomed and constrained her.

Omair M. Khan is at Stanford, juggling an MD and a PhD in stem cell biology and regenerative medicine while dabbling in policy and venture capital. Nathan Mallipeddi, Arjun Menta, Vaibhav Mohanty, Shyamala Ramakrishna, and Shomik Verma round out the Indian American contingent across fields spanning medicine, engineering, and the sciences.

## A Fellowship Built on the Immigrant Bet

The Paul & Daisy Soros Fellowships were established by the Hungarian-born financier and philanthropist Paul Soros and his wife Daisy to honour the contributions immigrants and their children make to American society. Now in its twenty-eighth year, the programme has awarded more than $100 million in graduate funding. Its alumni include MacArthur Fellows, Pulitzer finalists, tech founders, and federal judges — a roster that doubles as a running argument for the economic returns of immigration.

For the Indian diaspora, the fellowship's annual announcement functions as something between a community report card and a quiet source of pride. Indian Americans make up roughly 1.5 per cent of the US population but regularly claim 20 to 30 per cent of the Soros class. The consistency suggests something structural: a community that channels an unusual share of its resources into education and research, and a fellowship that rewards exactly those investments.

## What It Signals

The 2026 class arrives at a moment when immigration policy is under intense scrutiny and anti-immigrant rhetoric has sharpened. Jaspreet Kaur's selection — a DACA recipient whose legal status remains tethered to executive discretion — is a pointed reminder that talent does not arrive with papers in order. Several of the Indian American fellows are children of immigrants who came on H-1B or student visas, the same visa categories now facing tighter caps and longer backlogs.

For NRIs watching from abroad, the Soros cohort offers a different data point than the usual headlines about visa uncertainty. It says that the pipeline of Indian intellectual capital into American institutions remains robust, even as the political ground shifts beneath it. Whether that pipeline stays open is another question entirely."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Eight Indian Americans Just Won a Fellowship That Pays $90,000 for Being an Immigrant. Here's What They Study.",
    "subheadline": "The Paul & Daisy Soros Fellowships picked 30 scholars from 1,800 applicants. More than a quarter are of Indian origin — a pattern that says something about the community's bet on education.",
    "slug": make_slug("soros-fellowship-eight-indian-americans-graduate-scholars"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian Americans dominate a top immigrant fellowship, reflecting the diaspora's deep investment in education and research — even as the visa system they depend on faces political headwinds.",
    "tags": ["nri", "diaspora", "education", "fellowship", "indian-american", "soros"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/8-indian-americans-win-paul-and-daisy-soros-fellowships/"},
        {"name": "MIT News", "url": "https://news.mit.edu/2026/six-mit-awarded-2026-paul-daisy-soros-fellowships-new-americans"},
        {"name": "Paul & Daisy Soros Fellowships", "url": "https://pdsoros.org/"}
    ]),
    "score_total": 74,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/29229903/pexels-photo-29229903.jpeg",
    "image_caption": "Graduates celebrating at a university commencement ceremony",
    "image_attribution": "Pexels",
    "body": article1_body
}


# ── ARTICLE 2: Chandrayaan-3 Goddard Award ──────────────────────────────

article2_body = """America's premier aerospace body has handed its highest astronautics honour to India's moon mission, and it was the Indian ambassador in Washington who walked to the podium to collect it. The symbolism was hard to miss.

The American Institute of Aeronautics and Astronautics (AIAA) awarded its 2026 Goddard Astronautics Award to ISRO's Chandrayaan-3 at the ASCEND 2026 Conference in Washington DC on May 21. Ambassador Vinay Kwatra accepted the award on behalf of the Indian Space Research Organisation, delivering remarks that leaned into Prime Minister Narendra Modi's Space Vision 2047 — a roadmap for deep space exploration, human spaceflight, and the commercial space sector India is racing to build.

## The Mission That Changed India's Coordinates

On August 23, 2023, Chandrayaan-3's Vikram lander touched down near the Moon's south pole, making India the first country to reach this scientifically prized and operationally treacherous region. The mission confirmed the presence of sulphur, aluminium, calcium, iron, chromium, and titanium in the lunar south polar soil — data points that matter because they hint at resources that could sustain future manufacturing on the Moon's surface.

The Goddard Award, named after rocket pioneer Robert H. Goddard, is the most prestigious recognition AIAA bestows in astronautics. Past recipients include teams behind the Mars rovers, the Hubble Space Telescope, and the James Webb Space Telescope. ISRO is the first Indian organisation to receive it. The citation praised the mission "for the groundbreaking landing of ISRO's Chandrayaan-3 near the lunar south pole region, to deepen our understanding of the moon and beyond."

## Why the Diaspora Cares

For the estimated 700,000 Indian Americans working in STEM fields — many of them in aerospace, at NASA, SpaceX, Boeing, and a constellation of defence contractors — the award carries a specific charge. It validates the technical ecosystem they emerged from before they joined America's own space enterprise.

Indian-origin engineers and scientists occupy senior positions across the US aerospace industry. Swati Mohan narrated Perseverance's Mars landing for NASA. Sunita Williams has logged over 300 days in space aboard the International Space Station. The Goddard Award for Chandrayaan-3 adds an institutional line under the informal argument the diaspora has been making for decades: that India's engineering bench is world-class, and the people it produces tend to prove it wherever they land.

Ambassador Kwatra used the moment to call for deeper collaboration between Indian and American governments, industries, and research institutions in space exploration. It is a pitch that resonates with a diaspora that already lives and works in the overlap between the two countries' technical establishments. India's space programme runs on a fraction of NASA's budget — Chandrayaan-3 cost roughly $75 million, less than the budget of most Hollywood films about space — and the award is a public acknowledgement that cost efficiency and scientific ambition are not mutually exclusive.

## The Road to 2047

Modi's Space Vision 2047 envisions India as a leading spacefaring nation by the centenary of its independence. The plan includes the Gaganyaan human spaceflight programme, a Venus orbiter mission, and an ambitious push to open India's space sector to private enterprise. For NRIs in aerospace, the question is whether this roadmap creates opportunities to contribute directly — through joint ventures, technology transfers, or the kind of brain circulation that has already transformed India's IT and pharmaceutical sectors.

The Goddard Award will not, by itself, answer that question. But it puts ISRO in a room it has never been in before, alongside the agencies and teams that define what counts as frontier space science. For the diaspora, that matters."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "America's Top Aerospace Body Just Gave Its Highest Honour to India's Moon Mission. The Diaspora Noticed.",
    "subheadline": "AIAA's Goddard Astronautics Award — previously reserved for the Hubble and James Webb telescope teams — went to ISRO's Chandrayaan-3. Ambassador Kwatra accepted it in Washington.",
    "slug": make_slug("chandrayaan-3-goddard-astronautics-award-aiaa-isro-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The award validates the technical ecosystem that produced hundreds of thousands of Indian-origin aerospace professionals now working in America's own space enterprise.",
    "tags": ["nri", "diaspora", "isro", "chandrayaan-3", "space", "aiaa", "goddard-award"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/aiaa-honors-chandrayaan-3-with-goddard-astronautics-award/"},
        {"name": "AIAA Official", "url": "https://www.aiaa.org/news/news/2026/01/09/aiaa-announces-2026-premier-award-winners"},
        {"name": "Blitz India Media", "url": "https://blitzindiamedia.com/chandrayaan-3-wins-prestigious-2026-goddard-award/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/aa/Chandrayaan-3_%E2%80%93_Image_of_Vikram_lander_on_lunar_surface_taken_by_Pragyan_rover_navcam_at_1104_IST%2C_30_August_2023_from_15_meters_away_%28with_text%29.webp",
    "image_caption": "Chandrayaan-3 Vikram lander photographed on the lunar surface by the Pragyan rover",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body
}


# ── ARTICLE 3: HungerMitao / Indian Diaspora Philanthropy ───────────────

article3_body = """Raj and Aradhana Asava did not set out to build a national hunger-relief movement. They set out to answer a question that nags at many successful Indian Americans: what does it mean to give where you live?

The couple, who founded the volunteer-driven HungerMitao movement in 2017, have now pledged $1 million to Feeding America, the country's largest domestic hunger-relief network. The pledge was announced at a Hunger Free America gala in New York, where India's Consul General Randhir Jaiswal was in attendance — a detail that signals how seriously the Indian diplomatic establishment now takes diaspora philanthropy as soft power.

## Thirty Million Meals and Counting

HungerMitao — the name translates to "Wipe Out Hunger" — has enabled 30 million meals through the Feeding America network since its launch. The movement operates as a grassroots mobilisation engine, channelling Indian American community resources and volunteer hours toward local food banks. It is active in North Texas, Houston, New York City, Atlanta, and Seattle, with planned expansions into Central Texas, Connecticut, Alameda County, New Jersey, and the Tarrant area.

The model is deliberate. Rather than building parallel infrastructure, HungerMitao plugs into Feeding America's existing network of 200-plus food banks and 60,000 food pantries. Indian American volunteers pack boxes, organise drives, and fundraise within their own community networks — gurdwaras, temple associations, professional organisations, Diwali galas — then direct the money and labour toward food banks that serve everyone, regardless of background.

"HungerMitao is as much about eradicating hunger as it is about unifying the fragmented efforts of our community and focusing it on the humanitarian cause of hunger," Aradhana Asava has said. "In the spirit of 'give where you live' we invite the four-million-strong Indian diaspora in the US to join us."

## The Philanthropy Gap

The pledge arrives at an interesting moment in the evolution of Indian American giving. The community's median household income — roughly $150,000, the highest of any ethnic group in America — has long outstripped its visibility in domestic philanthropy. Indian Americans give generously, but much of that giving flows back to India: temple construction, school funding, medical camps in home villages, disaster relief. Organisations like HungerMitao represent a conscious effort to redirect some of that philanthropic energy toward American communities.

MR Rangaswami, founder of Indiaspora and himself a Feeding America donor, framed it in characteristically pragmatic terms: "When we come together with passion, we can accomplish anything." The subtext is that a community perceived as insular — one that builds temples and weekend Gujarati schools and cricket leagues — gains political and social capital when it is also seen feeding its neighbours.

## Why Diplomats Show Up

Consul General Jaiswal's presence at the gala is not incidental. The Indian government has, over the past decade, moved from vaguely acknowledging the diaspora to actively courting it as an instrument of bilateral influence. Philanthropy directed at American communities — as opposed to remittances sent home — complicates the narrative that Indian immigrants are extractive, taking American jobs and sending dollars east. Organisations like HungerMitao provide a counter-story: Indians feeding Americans.

For the diaspora itself, the calculation is simpler. Food insecurity in the United States affects roughly 47 million people, including 14 million children. Indian Americans live in the same neighbourhoods, send their children to the same schools, and shop at the same grocery stores. The hunger is not abstract. And for a community that prizes the concept of *anna daan* — the sacred act of feeding others — there is a cultural logic to the work that transcends strategic positioning.

The Asavas' $1 million pledge will not solve American hunger. But it signals that the largest, wealthiest diaspora in the country is beginning to think of itself as something more than a guest — and that the institutions watching, from Feeding America to the Indian consulate, have noticed."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "An Indian American Couple Pledged $1 Million to Feed America's Hungry. Their Movement Has Already Delivered 30 Million Meals.",
    "subheadline": "The HungerMitao movement channels Indian diaspora resources into America's food banks. India's consul general attended the latest gala — a sign of how seriously New Delhi takes diaspora philanthropy.",
    "slug": make_slug("hungermitao-asava-million-dollar-pledge-feeding-america-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian Americans are redirecting philanthropic energy from remittances to local American communities, building social capital and complicating the narrative that the diaspora only takes.",
    "tags": ["nri", "diaspora", "philanthropy", "hunger", "feeding-america", "hungermitao", "community"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/indian-diaspora-giving-back-to-society-hunger-free-america-gala-organized/"},
        {"name": "HungerMitao / Feeding America", "url": "https://www.feedingamerica.org/"},
        {"name": "Indiaspora", "url": "https://www.indiaspora.org/"}
    ]),
    "score_total": 76,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6591154/pexels-photo-6591154.jpeg",
    "image_caption": "Volunteers packing food donations at a community food bank",
    "image_attribution": "Pexels",
    "body": article3_body
}


# ── INSERT ───────────────────────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
