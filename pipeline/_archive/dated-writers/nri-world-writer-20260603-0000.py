#!/usr/bin/env python3
"""NRI World Writer — 3 June 2026 00:00 UTC batch"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load Supabase env
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


# ── ARTICLE 1: India Heritage Center Museum in Washington DC ──

art1_body = """After eight years of research, fundraising plans, and content curation, the team behind the proposed India Heritage Center is moving from blueprints to bricks. The project, led by Atlanta-based educationist Dr Amitabh Sharma, aims to establish the first permanent museum in the United States dedicated exclusively to India's civilisational, cultural, and historical journey — spanning more than 11,000 years.

The proposed site is Washington DC, deliberately chosen for its foot traffic and symbolic weight. The US capital houses some of the world's most visited museums — the Smithsonian, the Holocaust Memorial Museum, the National Museum of African American History — each one a statement that a community's story matters enough to be told in stone. The India Heritage Center would add a 20,000-square-foot complex to that landscape: ten themed galleries, a 350-seat auditorium, a library, reception facilities, and a gift centre.

## What the Galleries Would Cover

According to project documents, exhibits would trace India's arc from the Indus Valley civilisation through Vedic traditions, scientific discovery, yoga and Ayurveda, cultural heritage, independence movements, and modern India's economic and technological rise. The organisers plan to deploy virtual reality, augmented reality, interactive audio-video installations, murals, and physical artefacts.

"Indian history and Indian civilisation has never been portrayed in the strength that it deserves," Sharma told IANS. "It is important in today's perspective, more importantly, to be able to tell the world that this is the rich civilisation, rich heritage that we have."

The museum is registered as a 501(c)(3) non-profit and estimates total project costs between $12 million and $14 million. Funding is expected to come from high-net-worth individuals, corporate sponsorships, grants, crowdfunding, and naming opportunities for galleries and facilities.

## Why It Matters to the Diaspora

The timing is deliberate. The Indian-American community — now numbering well over 4.4 million according to recent Census data — has become one of the most influential immigrant groups in the United States, with growing representation in technology, medicine, business, academia, and public service. Yet there is no permanent cultural institution in the country that tells India's full story.

Weekend language schools and temple events keep culture alive in living rooms and community halls. But a museum on the National Mall corridor would do something different: it would make India's civilisational narrative part of the permanent American cultural record, accessible to anyone who walks through the door.

Sharma framed it bluntly: "This is not my project. It is not your project. It is the entire Indian community's project."

## The Validation Question

The team spent years gathering and cross-referencing historical material before moving to fundraising. "It took us a long time to amalgamate humongous amounts of data over 11,000 years and then to get that data validated so that tomorrow nobody can raise a finger or raise an objection," Sharma said.

That kind of scholarly caution is unusual in diaspora institution-building, where enthusiasm sometimes outpaces rigour. Whether the India Heritage Center can hold to that standard through the messier phases of construction, exhibit design, and community politics will be the real test.

Community response, Sharma said, has been encouraging. "When I reach out to people, people say, yeah, why wasn't it done earlier? People are joining in."

If realised, the museum would offer younger generations of Indian Americans — many of whom have never visited India — a permanent, immersive encounter with the civilisation their grandparents left behind. For the broader American public, it would provide what Sharma called "a very compelling narrative" of one of the world's oldest continuous civilisations. Washington already has the real estate, the tourists, and the institutional culture to make that narrative stick. What remains is whether the diaspora can raise the $12 million to build it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Indian Diaspora Wants a Permanent Museum in Washington. After Eight Years, It Might Actually Happen.",
    "subheadline": "Dr Amitabh Sharma's India Heritage Center would be the first US institution dedicated to India's 11,000-year civilisational story. The price tag is $12 million. The ambition is larger.",
    "slug": make_slug("india-heritage-center-museum-washington-dc-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "There is no permanent museum in the United States that tells India's full civilisational story. The India Heritage Center aims to fill that gap, giving 4.4 million Indian Americans a cultural anchor in Washington DC and making India's narrative part of America's institutional memory.",
    "tags": ["nri", "diaspora", "museum", "washington-dc", "culture", "heritage"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "IndiaPost", "url": "https://indiapost.com/indian-diaspora-pushes-for-landmark-museum-in-washington/"},
        {"name": "IANS", "url": "https://ianslive.in/news/indian-diaspora-pushes-for-landmark-museum-in-washington-20250530"},
        {"name": "IndiaWest", "url": "https://www.indiawest.com/news/india-heritage-museum-planned-for-washington-d-c/"},
        {"name": "Global Indian News Network", "url": "https://globalindiannewsnetwork.com/india-heritage-museum-planned-for-washington-dc/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/29704413/pexels-photo-29704413.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "is_editorial": False,
    "body": art1_body,
}


# ── ARTICLE 2: Japan Suspends Indian Mango Imports ──

art2_body = """Japan has suspended all fresh Indian mango imports for the 2026 season after inspectors found deficiencies in fumigation and disinfection practices at Indian treatment facilities. The decision, confirmed in late May, covers six approved varieties — Alphonso, Kesar, Banganapalli, Langra, Chausa, and Malika — and shuts down a trade corridor that took nearly two decades of negotiation to open.

For India's mango export industry, the immediate financial hit is modest. Japan was never a volume buyer. But the reputational damage runs deeper, and for millions of NRIs who treat the arrival of Indian mangoes each summer with something closer to religious observance, the story touches a nerve that trade statistics cannot capture.

## The Fumigation Failure

Japan maintains one of the world's strictest agricultural quarantine systems. Indian mangoes were banned from the Japanese market for two decades — from 1986 to 2006 — over fruit fly concerns. Regaining access required India to build Vapour Heat Treatment facilities meeting Japanese standards and submit to periodic inspections.

The March 2026 inspections found those standards had slipped. Japanese plant quarantine officials identified "significant deficiencies" in pest-control procedures, according to reports in the Times of India. Rather than negotiate exceptions, Japan suspended the entire category.

"That is how fragile agricultural trade can be: one fruit, one rulebook, one missed standard," noted the Indulge Express in its analysis of the ban.

## The Mango as Cultural Currency

To anyone outside the Indian diaspora, this is a phytosanitary compliance story. Inside it, the emotional register is entirely different.

The mango is not merely a fruit for Indians abroad. It is a seasonal clock, a nostalgia delivery system, a marker of home. NRI families across the United States, United Kingdom, and Gulf states build summer rituals around the arrival of Alphonso shipments. Indian consulates host mango festivals — Seattle's Consulate General is holding its "King of Fruits" promotion event on 4 June. Grocery stores in Edison, Southall, and Dubai stack crates of Hapus with the reverence other cultures reserve for wine vintages.

India exported 29,938 tonnes of mangoes worth $56.5 million in FY25, primarily to the UAE, the US, Kuwait, and Qatar. The US market, which opened to Indian mangoes in 2007 after its own lengthy phytosanitary negotiations, processes about 1,000 tonnes each season. Prime Minister Narendra Modi highlighted the fruit's economic significance in his most recent Mann Ki Baat address, listing regional varieties and urging export diversification.

## What Exporters Are Doing

The Japan setback comes as India's mango export sector faces pressure on multiple fronts. Gulf demand has softened, with traders from Vasai and Surat reportedly delaying or cancelling advance bookings for Karnataka's Alphonso crop this season. India's Mango Growers' Association has been exploring alternatives, including expanded shipments to the US, UK, and Singapore.

Dr Rajendra Poddar, honorary president of the association, told media that the situation may create opportunities to diversify. "The association has been exploring alternative international markets," he said.

But diversification requires the same compliance infrastructure that Japan just found wanting. The US market, while currently open, requires its own irradiation treatments. The EU has its own Maximum Residue Limits. Each corridor is a new set of rules, a new set of inspections, and a new set of ways to fail.

## The Diaspora's Unspoken Role

What rarely gets acknowledged is the role the diaspora plays in driving mango demand abroad. It is not Japanese consumers clamouring for Alphonso. It is Indian-origin families in Tokyo, London, and New York whose spending creates the market signal that Indian exporters and trade diplomats respond to. The fumigation failures that cost India the Japanese market are, in a sense, a failure to protect the supply chain that the diaspora built.

For now, NRIs in Japan will go without Alphonso this summer. The India-Japan mango corridor will presumably reopen once India's treatment facilities pass reinspection. But the episode is a reminder that the King of Fruits does not travel on sentiment alone. It travels on compliance, cold chains, and the unglamorous machinery of international phytosanitary standards. When that machinery breaks down, even the most beloved fruit in the world gets stopped at the border."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Japan Just Banned Indian Mangoes for the Season. The Diaspora Felt It Before the Exporters Did.",
    "subheadline": "Fumigation failures at Indian treatment facilities shut down a trade corridor that took 20 years to open. For NRIs who build their summers around Alphonso arrivals, the loss is more than commercial.",
    "slug": make_slug("japan-bans-indian-mangoes-2026-diaspora-alphonso"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The Indian mango is cultural currency for NRIs — a nostalgia delivery system, a seasonal ritual, a marker of home. Japan's 2026 ban on Indian mangoes is a phytosanitary story on paper, but for the diaspora it is a reminder that the supply chains they built on sentiment run on compliance.",
    "tags": ["nri", "diaspora", "mango", "japan", "trade", "food", "alphonso"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Indulge Express", "url": "https://www.indulgexpress.com/food/2026/May/31/what-is-the-real-reason-japan-suspended-indian-mango-imports"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/mango-cultivation-a-very-special-part-of-indias-farm-economy-pm"},
        {"name": "LinkedIn / Dr. Analysis", "url": "https://www.linkedin.com/pulse/japans-suspension-indian-mango-imports-2026/"},
        {"name": "FreshPlaza", "url": "https://www.freshplaza.com/article/indias-alphonso-mango-exports-face-uncertainty/"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/30893290/pexels-photo-30893290.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "is_editorial": False,
    "body": art2_body,
}


# ── ARTICLE 3: International Day of Yoga 2026 – Diaspora Preparations ──

art3_body = """The 12th International Day of Yoga falls on 21 June 2026, and the preparations reveal something more interesting than the event itself: the machinery of cultural diplomacy that the Indian diaspora now operates, almost on autopilot, in cities from Seattle to Muscat.

India's Ministry of Ayush unveiled this year's theme — "Yoga for Healthy Ageing" — at the Yoga Mahotsav in Khajuraho, where Minister Prataprao Jadhav framed it as both a wellness philosophy and a policy response to the world's ageing demographics. The ministry is targeting 100 million online participants globally, a structured 21-day programme culminating on 21 June, and embassy-led mass yoga demonstrations in more than 100 countries.

## The Consulate Circuit

The diaspora dimension is where the real logistics play out. Indian missions abroad are the organising spine of International Day of Yoga celebrations worldwide, and the scale has grown quietly formidable.

The Consulate General of India in Seattle has two events on its calendar: a yoga session in Seattle on 21 June and a parallel one in Portland. Last year, the Indian Embassy in Washington DC held its celebration at the Wharf overlooking the Potomac River, combining yoga with Indian classical dance and millet promotion. In London, New York, San Francisco, Sydney, Dubai, and Singapore, consulates partner with local yoga studios, community organisations, and municipal governments to fill parks and public spaces with mat-to-mat practitioners.

What began as a government initiative — India proposed the UN resolution establishing IDY in 2014, endorsed by a record 175 member states — has become a diaspora fixture. Community organisations now run the local production: booking venues, coordinating instructors, handling permits, printing banners, and managing the social media documentation that feeds back to the Ministry of External Affairs as evidence of soft power at work.

## "Yoga for Healthy Ageing" — Why This Theme

The choice of theme is not accidental. Global life expectancy has been rising steadily, and India's own elderly population is projected to reach 194 million by 2031. The "silver economy" around elder care and wellness is already a significant market in India, and the ministry clearly sees yoga as India's competitive advantage in that space.

For the diaspora, the theme resonates differently. Many NRI families are navigating the challenge of ageing parents in India from thousands of miles away, or watching their own parents grow older in countries with limited intergenerational support systems. Yoga as a framework for healthy ageing speaks directly to that anxiety — not as a cure, but as a practice that bridges the cultural gap between an Indian wellness tradition and Western healthcare systems that often treat ageing as a problem to be medicated rather than a process to be managed.

Research has increasingly supported the case. Studies published in the Journal of the American Geriatrics Society and Age and Ageing have documented yoga's benefits for balance, cognitive function, chronic pain management, and fall prevention in older adults. The Ministry of Ayush's "Yoga 365" programme, launched alongside this year's IDY preparations, aims to make daily practice a sustained habit rather than a once-a-year photo opportunity.

## The 75-Day Countdown

The ministry kicked off a 75-day countdown on 7 April with a mass event at the Lonar crater lake in Maharashtra, where 5,000 participants performed Trikonasana simultaneously, earning an Asia Book of Records certification. The countdown has since included curtain-raiser events at Indian missions worldwide, corporate yoga sessions, and partnerships with international airlines to develop in-flight yoga protocols.

New this year: disease-specific yoga sequences developed in collaboration with hospitals, and an expanded digital platform for global participation. The ministry's ambition to hit 100 million concurrent online participants would, if achieved, make IDY 2026 one of the largest coordinated wellness events in history.

## What the Diaspora Actually Does

The official narrative is about government programmes and UN resolutions. The ground reality in diaspora communities is more organic. In suburbs across North America, weekend yoga classes taught by Indian aunties have been happening for decades — long before IDY gave the practice an official calendar date. Temple yoga sessions, community centre workshops, and informal neighbourhood groups form the base layer of yoga practice in the diaspora.

IDY's contribution was to give these scattered efforts a focal point and a sense of collective participation. When a family in Fremont, California rolls out their mats on 21 June alongside millions in Mumbai, Delhi, and Rishikesh, the practice becomes something more than exercise. It becomes a quiet act of cultural continuity — proof that a tradition older than most nations can still find new ground in the places Indians have made home.

The mats will be unrolled in 19 days. The real question, as the Yoga 365 initiative acknowledges, is whether they will stay unrolled on 22 June."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "International Day of Yoga Turns 12. The Diaspora's Role Has Quietly Become the Whole Point.",
    "subheadline": "India wants 100 million online participants for IDY 2026. The consulates, community centres, and temple yoga aunties who will actually deliver that number were never part of the original plan.",
    "slug": make_slug("international-day-yoga-2026-diaspora-healthy-ageing"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "International Day of Yoga has evolved from a government initiative into a diaspora fixture. Indian consulates worldwide organise mass events, but the real infrastructure is the community yoga classes, temple sessions, and neighbourhood groups that have been running for decades. IDY 2026's theme — Yoga for Healthy Ageing — speaks directly to NRI families navigating the challenge of ageing parents across continents.",
    "tags": ["nri", "diaspora", "yoga", "international-day-of-yoga", "wellness", "community"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/law-order/yoga-day-2026-aims-to-promote-healthy-ageing"},
        {"name": "Yogajala", "url": "https://yogajala.com/india-kicks-off-75-day-countdown-to-international-day-of-yoga-2026/"},
        {"name": "Ministry of Ayush / IDY 2026 Guidelines", "url": "https://ddhekangra.edu.in/assets/pdf/IDY_2026_guidelines.pdf"},
        {"name": "Consulate General of India, Seattle", "url": "https://indiainseattle.gov.in/"}
    ]),
    "score_total": 70,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8172947/pexels-photo-8172947.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "is_editorial": False,
    "body": art3_body,
}


# ── Publish ──

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
