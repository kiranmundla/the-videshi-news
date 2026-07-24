#!/usr/bin/env python3
"""NRI World writer — July 7, 2026 run."""
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


# ──────────────────────────────────────────────────────────
# Article 1: Carnegie Hall Indian Dance Festival
# ──────────────────────────────────────────────────────────

art1_body = """On a Sunday afternoon in early July, a dozen Indian classical dance schools from across the United States took the stage at Carnegie Hall's Stern Auditorium — the same 2,800-seat room where Tchaikovsky once conducted and where Ravi Shankar introduced the sitar to American concertgoers in the 1960s. The performers at the All-Indian Dance Festival 2026 were not visiting artists flown in from Chennai or Hyderabad. Most of them were born and raised in American suburbs, and their art was learned not in temple courtyards but in strip-mall studios and community centres from Texas to New Jersey.

The festival, held on July 5, was produced by Three Aksha and curated by Viji Rao in collaboration with the Consulate General of India in New York. It featured classical and folk dance forms — Kuchipudi, Bharatanatyam, Odissi, and several regional traditions — performed by troupes drawn from schools that have quietly built a parallel cultural infrastructure across North America.

## A Network Nobody Talks About

The list of performers reads like a census of Indian classical arts education in the United States. Abhinaya Tharangini, an academy of Kuchipudi dance; Bharathakala Naatya Academy; Bairava School of Dance; Nupoor Dance School; Samskruthi School of Dance; Nrithya Samarpanam; The Odisha Society of the Americas. These are not institutions that make headlines, but they are the institutions that keep Odissi mudras and Bharatanatyam adavus alive 8,000 miles from their place of origin.

One of them, Natyalaya School of Dance in Austin, Texas — the oldest Indian classical dance school in central Texas — launched a GoFundMe campaign to send roughly 20 dancers to New York for the performance. The out-of-pocket costs for travel, lodging, choreographer fees, and studio rental were steep enough to require community fundraising. This is the unglamorous reality of how classical Indian culture survives in America: one recital, one car wash, one donation jar at a time.

## Carnegie Hall's Indian Pivot

The festival did not happen in a vacuum. In February, Carnegie Hall announced a new annual Indian Music Festival, set to launch in May 2027, backed by a $10 million gift from Ila and Dinesh Paliwal. Ila Paliwal — a trained classical musician — simultaneously joined Carnegie Hall's Board of Trustees, becoming one of the first Indian voices in the institution's governance.

The inaugural music festival will feature performances in the Stern Auditorium and two evenings in Zankel Hall, spotlighting instrumental and vocal recitals, cross-generational collaborations, and contemporary compositions. Educational programming and community initiatives will accompany the concerts.

Clive Gillinson, Carnegie Hall's Executive and Artistic Director, called the initiative "a major step forward in Carnegie Hall's commitment to celebrate treasured musical traditions from around the world."

## The Diaspora Angle

For the roughly five million Indian Americans in the United States, these events represent something more than cultural programming. They are a test of whether traditions that took centuries to develop in the subcontinent can genuinely survive transplantation — not as museum pieces, but as living art forms practised by children who may never have visited the temples where these dances originated.

The answer, at least on the evidence of a Sunday afternoon at Carnegie Hall, appears to be yes. But the sustainability question remains. Dance gurus who emigrated in the 1980s and 1990s are ageing. The generation of American-born students they trained is now teaching a further generation, each step adding distance from the source tradition even as it roots the art deeper in American soil.

The Indian government, through its consulates, has been an active partner — co-presenting events, supporting cultural exchanges, and using occasions like International Yoga Day and Pravasi Bharatiya Divas to keep the diaspora tethered to Indian cultural identity. Whether the next generation, fluent in TikTok but learning Kuchipudi on weekends, will carry these traditions forward with the same devotion is the open question no festival can answer.

What Carnegie Hall's stage does offer is legitimacy. When Bharatanatyam is performed in the same auditorium where the New York Philharmonic plays, it sends a signal — to the dancers, to their families, and to the broader American public — that these are not niche ethnic activities. They are world-class art forms, and the kids from Austin and New Jersey performing them are their custodians now.

*Sources: Carnegie Hall event listing; BroadwayWorld; GoFundMe/Natyalaya Austin; South Asian Herald*"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Twelve Dance Schools Took Carnegie Hall's Biggest Stage. Every Performer Was Born in America.",
    "subheadline": "The All-Indian Dance Festival 2026 brought Kuchipudi, Bharatanatyam, and Odissi to the Stern Auditorium — performed by suburban kids trained in strip-mall studios, and backed by a $10 million bet that Indian classical arts belong in America's most storied concert hall.",
    "slug": make_slug("carnegie-hall-indian-dance-festival-american-born-youth-classical"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "American-born Indian youth performing ancestral classical dance forms at Carnegie Hall represents the ultimate test of whether these traditions can survive transplantation — and thrive — far from their origins.",
    "tags": ["nri", "diaspora", "indian-classical-dance", "carnegie-hall", "bharatanatyam", "cultural-preservation", "indian-american"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Carnegie Hall", "url": "https://www.carnegiehall.org/Calendar/2026/07/05/All-Indian-Dance-Festival-2026-0200PM"},
        {"name": "BroadwayWorld", "url": "https://www.broadwayworld.com/article/Carnegie-Hall-Unveils-New-Annual-Indian-Music-Festival-20260206"},
        {"name": "South Asian Herald", "url": "https://southasianherald.com/carnegie-hall-announces-annual-indian-music-festival-10-million-gift/"},
        {"name": "GoFundMe / Natyalaya Austin", "url": "https://www.gofundme.com/f/natyalaya-austin-all-india-dance-festival-carnegie-hall"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Bharatanatyam_dance_performance_at_the_Khajuraho_Dance_Festival_2026_009.jpg/1280px-Bharatanatyam_dance_performance_at_the_Khajuraho_Dance_Festival_2026_009.jpg",
    "image_caption": "Bharatanatyam performer at the Khajuraho Dance Festival 2026",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ──────────────────────────────────────────────────────────
# Article 2: India Real Estate Boom and NRI Investment
# ──────────────────────────────────────────────────────────

art2_body = """India's real estate sector absorbed $4.5 billion in institutional investment during the first half of 2026, a 50 per cent jump from the same period last year and the highest capital inflow in six years. A Colliers India report released on July 5 showed the surge powered through headwinds from the West Asian crisis, rising global uncertainty, and what the International Monetary Fund recently upgraded as India's 6.5 per cent GDP growth projection for FY2027.

For the roughly five million NRIs scattered across the United States, United Kingdom, Canada, the Gulf, and beyond, the numbers carry a specific invitation: Indian property is booming, foreign capital is welcome, and the government is making it easier than ever to invest from abroad.

## The Numbers

The second quarter alone attracted $2.9 billion in investment — up 70 per cent year-on-year. Domestic investors accounted for 57 per cent of the total, deploying $2.6 billion (an 80 per cent annual increase). Foreign investors, while more selective, contributed $1.9 billion in H1 2026, a 24 per cent rise driven by strategic equity stake acquisitions and capital allocation across mixed-use and alternative assets.

Mumbai confirmed its status as the country's property capital. Knight Frank India reported 80,221 property registrations in the first half of 2026 — the highest for any January-to-June period since 2013 and a 6 per cent increase over last year. June alone saw 13,302 registrations, the highest for that month in 14 years. Stamp duty collections reached ₹6,968 crore, up 4 per cent year-on-year.

Meanwhile, India's office market set an all-time record. CBRE reported 45.5 million square feet of office leasing in H1 2026 — equivalent to roughly 400 football pitches — up 9.6 per cent from a year earlier and the highest ever for any six-month period. Global Capability Centres (GCCs) drove 43 per cent of all leasing, with Fortune 500 companies leasing 6.8 million square feet in Q2 alone.

## Why NRIs Are Paying Attention

Several factors have aligned to make 2026 a particularly compelling window for diaspora property investment. The rupee, trading above ₹90 to the dollar, means dollar-denominated savings stretch further in Indian property markets. The RBI's repo rate, at 5.25 per cent as of June, keeps mortgage costs manageable. And the government's recent move to eliminate the physical OCI booklet in favour of a digital-only eOCI card — reported last week — removes one more layer of bureaucratic friction for overseas Indians transacting in India.

NRIs are estimated to account for roughly 19 per cent of property purchases in India, according to industry data. Tier II and III cities — Coorg, Hosur, Coimbatore, Kochi, Ujjain — are seeing significant capital deployment, particularly in hospitality, industrial and warehousing, and residential segments, per the Colliers report. For NRIs who cannot afford Mumbai prices but want a foothold back home, these emerging markets offer entry points that the metros priced out years ago.

## The Catches

The picture is not uniformly rosy. Housing sales across India's top seven cities dipped 6 per cent in Q2 2026, according to ANAROCK, with Pune falling 15 per cent and Delhi-NCR and Chennai both slipping. The affordable housing segment continues to shrink — now just 6 per cent of new supply — as developers chase premium and luxury buyers. For NRIs thinking about residential investment, the market increasingly rewards those who can put in ₹1 crore or more.

Repatriation remains the perennial sticking point. FEMA regulations allow NRIs to repatriate proceeds from up to two residential properties purchased with foreign currency. Sale proceeds from a third property onward fall under the $1 million per financial year NRO account limit, requiring Forms 15CA and 15CB and a CA certification. The flat 12.5 per cent long-term capital gains rate introduced in the latest budget simplifies tax liability, but the paperwork remains considerable.

"Institutional investment growth was led by equally strong participation from domestic as well as foreign investors," said Badal Yagnik, CEO and Managing Director of Colliers India. "This balanced interplay of foreign and domestic investors will be crucial in charting the next growth phase of Indian real estate, especially during the times of uncertainty in capital deployment."

## What to Watch

The second half of 2026 will test whether the momentum holds. The Middle East conflict's impact on crude prices and capital flows, AI-driven uncertainty in the IT sector that powers many GCC leasing decisions, and the usual monsoon-season slowdown in registrations will all weigh on the numbers. For NRIs, the window is open. Whether it stays that way depends on forces well beyond any property brochure.

*Sources: Colliers India H1 2026 report; Knight Frank India; CBRE India / Reuters; ANAROCK Group; Outlook Money*"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Real Estate Just Had Its Best Half-Year in Six Years. Here Is What NRIs Need to Know.",
    "subheadline": "Institutional investment hit $4.5 billion, Mumbai registrations reached a 14-year high, and office leasing broke all records. For the diaspora eyeing property back home, the numbers are loud — but the fine print matters.",
    "slug": make_slug("india-real-estate-investment-h1-2026-nri-property-boom"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "NRIs account for roughly 19% of Indian property purchases. With the rupee above 90/USD, repo rates at 5.25%, and the new digital-only eOCI card reducing bureaucratic friction, 2026 is a particularly compelling window for diaspora real estate investment — but FEMA repatriation rules and market shifts demand careful planning.",
    "tags": ["nri", "diaspora", "real-estate", "investment", "mumbai", "property", "fema", "repatriation"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Outlook Money / Colliers India", "url": "https://www.outlookmoney.com/invest/indias-real-estate-investments-surge-50-per-cent-to-450-billion-in-h1-2026-says-report"},
        {"name": "Reuters / CBRE India", "url": "https://www.reuters.com/world/india/indias-office-leasing-hits-record-multinationals-expand-despite-global-uncertainty-2026-07-07/"},
        {"name": "Outlook Money / Knight Frank India", "url": "https://www.outlookmoney.com/invest/mumbai-records-over-80000-property-registrations-in-h1-2026-knight-frank"},
        {"name": "Outlook Money / ANAROCK", "url": "https://www.outlookmoney.com/invest/housing-sales-dip-6-across-top-7-cities-in-q2-2026-anarock"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Mumbai_03-2016_27_skyline_at_Marine_Drive.jpg/1280px-Mumbai_03-2016_27_skyline_at_Marine_Drive.jpg",
    "image_caption": "Mumbai skyline along Marine Drive, the financial capital driving India's property boom",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}


articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
