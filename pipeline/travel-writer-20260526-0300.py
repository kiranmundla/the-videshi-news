#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-26 03:00 PDT batch"""

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


# ── Article 1: Ladakh Year-Round Tourism ──────────────────────────────────

art1_body = """Ladakh's hotels have spent decades running a brutal business: six months of frantic tourism, six months of empty rooms and mounting bills. Starting June 1, that calculus changes. The Ladakh administration has granted industry status to every registered hotel and guest house in the union territory — a move that slashes electricity and water to industrial rates, opens the door to concessional bank loans, and exempts properties from property tax.

The numbers are not trivial. All 1,257 registered properties — 1,078 in Leh, 179 in Kargil — qualify immediately. For owners who have been paying residential utility rates while heating lobbies through Himalayan winters, the savings could be the difference between staying open year-round and shutting down in October.

## The Zoji La Tunnel Changes Everything

The real transformation, though, is underground. The Zoji La Tunnel — a 14-plus-kilometre, bi-directional bore through the mountain barrier between Srinagar and Leh — is under construction on the route that currently locks Ladakh off from the rest of India for months each winter. When complete, it will keep the corridor open in all weather, cutting travel times dramatically and making winter access reliable for the first time.

Ladakh's Lieutenant Governor Kavinder Gupta pitched this vision at SATTE 2026, South Asia's largest B2B travel exhibition, held in February at Delhi's Yashobhoomi convention centre. His message was blunt: Ladakh is no longer a summer-only destination.

## Dark Skies and New Circuits

Beyond the familiar icons — Pangong Lake, Nubra Valley, Khardung La — Ladakh is quietly building niche tourism corridors. Hanle, home to the Indian Astronomical Observatory, hosts one of the world's highest optical telescopes and the MACE gamma-ray telescope. The site offers some of the clearest night skies in India, and dark-sky tourism is growing fast: astrophotography workshops, stargazing camps, and monastery visits in a landscape that feels closer to the moon than to the rest of the subcontinent.

The administration is also pushing fixed calendars for local festivals, digital registration systems for hotels and tour operators, and sewage treatment infrastructure — the unsexy plumbing that determines whether sustainable tourism stays sustainable.

## What This Means for NRIs

For the Indian American diaspora, Ladakh has always been the trip you plan for years and execute in a narrow July-August window, competing with every other tourist for the same overpriced rooms and permits. The industry-status move signals a structural shift: better hotels, lower prices in shoulder seasons, and — once the Zoji La Tunnel opens — the possibility of a winter or spring trip that doesn't require a military-grade logistics plan.

Rigzin Wangmo Lachic, president of the All Ladakh Hotel and Guest House Association, called the decision "a major step towards strengthening the tourism and hospitality sector." For NRI families who have been putting off the Ladakh trip because of cost and logistics, the window is widening.

The smart move now: plan for autumn 2026 or spring 2027, when the policy benefits kick in but the crowds haven't caught up. Ladakh's skies aren't getting any darker elsewhere."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Ladakh's Hotels Just Got Industry Status — and the Zoji La Tunnel Will End the Winter Lockout",
    "subheadline": "Starting June 1, 1,257 hotels get industrial utility rates and tax breaks. A 14-km tunnel under construction will make year-round access real for the first time.",
    "slug": make_slug("ladakh-hotels-industry-status-zoji-la-tunnel-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs have always been forced into a narrow July-August window for Ladakh trips. Industry status means better hotels and lower shoulder-season prices; the Zoji La Tunnel means winter and spring trips become viable.",
    "tags": ["travel", "ladakh", "india-tourism", "infrastructure", "hotels"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/industry-status-gives-ladakh-hotels-long-sought-relief-from-high-costs/article71011119.ece"},
        {"name": "Tourism UAE News — SATTE 2026", "url": "https://www.tourismuae.com/news/ladakh-and-new-delhi-shine-at-satte-2026-as-india-pushes-experience--led-sustainable-tourism/50643"},
        {"name": "Tourism Cairns News — SATTE 2026", "url": "https://tourismcairns.com.au"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/29232390/pexels-photo-29232390.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art1_body.strip()
}

# ── Article 2: Bali Arts Festival 2026 ───────────────────────────────────

art2_body = """Every summer, NRI families face the same question: India (and the guilt-trip circuit of relatives), Europe (and the Schengen paperwork), or something easier. This June, Bali offers a third option — and it comes with 20,000 artists.

The 48th Bali Arts Festival runs from June 13 through July 11, turning Denpasar's Bali Art Centre into one of Southeast Asia's largest month-long cultural gatherings. More than 673 artistic groups from across the island will perform traditional dance, music, theatre, and ritual-inspired art, alongside international participants from India, Japan, South Korea, and the United States.

## Not Your Instagram Bali

This is not the Bali of influencer reels and overpriced smoothie bowls. The festival — *Pesta Kesenian Bali*, or PKB — has run annually since 1979 and remains the island's most serious cultural event. Each regency presents distinct dance styles, costumes, and ceremonial interpretations that reveal a Bali most tourists never see.

Former journalist and academic Agus Dei, who spent 14 years documenting the island's tourism and environmental challenges, put it plainly: "Cultural events like this remind people that Bali is not only a tourism destination, but also a living cultural and environmental ecosystem."

That tension — between tourism's economic engine and the cultural identity it risks flattening — is now central to Bali's public conversation. The festival is where the island makes its case that the two can coexist.

## The Visa Situation for NRIs

Here's where it gets practical. NRIs holding US passports can enter Indonesia visa-free for up to 30 days — no paperwork, no consulate visits, just land and go. Indian passport holders qualify for a Visa on Arrival (VOA) at Ngurah Rai International Airport in Bali, valid for 30 days at a cost of IDR 500,000 (roughly $30). Both categories need a passport valid for at least six months and proof of onward travel.

New this year: Indonesia now requires all visitors to complete an electronic Arrival Card before landing — a digital form similar to India's own new e-Arrival Card requirement. Fill it out before you board. The tourist levy of IDR 150,000 (~$9) also applies.

## Why NRIs Should Care

Bali sits roughly 5-6 hours from most major Indian cities by air, with excellent connections through Singapore, Kuala Lumpur, and Bangkok. Return flights from the US West Coast run 16-20 hours through Asian hubs. Compared to a European cultural trip, costs are dramatically lower: a quality Ubud resort runs $80-150 a night, and a full day of temple visits, rice-terrace walks, and a traditional cooking class costs less than a single museum ticket in Paris.

For NRI families, the festival timing — mid-June through mid-July — lines up perfectly with school summer breaks. The island is also squarely in dry season, meaning clear skies and comfortable temperatures.

Beyond the festival, Bali's wellness scene has exploded: yoga retreats in Ubud, sound healing in Canggu, and Ayurveda-influenced spa treatments that will feel familiar to anyone who grew up with an Indian grandmother's home remedies. Indonesia's broader wellness expansion now stretches to Lombok, Flores, and the Gili Islands.

One thing to note: Indonesia has recently tightened visa rules for digital nomads and influencers creating commercial content on tourist visas. If you're planning to work remotely from a Bali co-working space, check the current rules carefully. For genuine vacation travel, the door is wide open."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Bali's Month-Long Arts Festival Starts June 13 — Here's the NRI's Complete Guide",
    "subheadline": "20,000 artists, 673 groups, a month of performances — and US passport holders don't even need a visa. The practical case for swapping the annual India trip for Indonesia this summer.",
    "slug": make_slug("bali-arts-festival-2026-nri-summer-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Summer travel alternative for NRI families tired of the annual India relative circuit. US passport holders enter visa-free; Indian passport holders get VOA for $30. Festival timing aligns with school breaks, costs a fraction of Europe.",
    "tags": ["travel", "bali", "indonesia", "arts-festival", "summer-travel", "visa"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "London Daily News", "url": "https://www.londondaily.news/balis-cultural-soul-faces-a-modern-test-as-2026-arts-festival-returns/"},
        {"name": "The Honeycombers — Bali Visa Guide 2026", "url": "https://thehoneycombers.com/bali/bali-visa/"},
        {"name": "Alike.io — Summer 2026 Travel Trends", "url": "https://alike.io"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/32877859/pexels-photo-32877859.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art2_body.strip()
}

# ── Article 3: India #1 in Wellness Tourism ──────────────────────────────

art3_body = """Your grandmother's turmeric milk has gone global — and the numbers prove it. India has overtaken Thailand, Indonesia, Japan, Switzerland, and Australia to claim the top spot in the 2026 Top 50 Wellness Travel Destinations rankings, published by Travel and Tour World. The country's wellness tourism economy generated an estimated $35 billion in 2025 and is projected to surpass $116 billion by 2035.

For NRIs who grew up watching their parents dismiss Western medicine in favour of haldi doodh and yoga at dawn, the irony is rich: the world is now paying premium prices for what was once just Tuesday morning in an Indian household.

## What Changed

The global wellness travel market is now valued at nearly $1 trillion, and the shift is structural, not trendy. Modern wellness travellers are no longer content with spa weekends and cucumber water. They want Panchakarma detox treatments that last weeks, silent meditation retreats in the Himalayas, and yoga teacher training programmes that require commitment, not just Instagram content.

India's advantage is authenticity. Unlike wellness destinations built around commercial luxury packaging, India's healing traditions are rooted in millennia of Ayurvedic science, Vedantic philosophy, and yogic practice. Kerala leads Ayurveda tourism through herbal detox therapies and rejuvenation programmes across its backwater resorts. Rishikesh remains the global capital of yoga, drawing practitioners to ashrams along the Ganges. Dharamshala offers Tibetan meditation and Buddhist wellness. Goa delivers beachfront mindfulness for those who need their inner peace with a sea view.

## The New Wellness Corridors

The growth extends well beyond the established hubs. The Himalayan towns of Manali and Dharamshala are developing forest meditation and mindful trekking circuits. Mysore continues to dominate classical yoga education. And a new generation of luxury wellness resorts — think Ananda in the Himalayas, Vana in Dehradun, SwaSwara in Gokarna — is integrating traditional therapies with modern wellness science: longevity programmes, biohacking, sleep therapy, and evidence-based nutrition.

India's government-backed AYUSH sector is also investing in international promotion of traditional medicine and herbal wellness products, turning what was once a niche into a national export strategy.

## The NRI Opportunity

Here's the practical case for diaspora families. A two-week Panchakarma programme at a reputable Kerala resort runs $2,000-4,000, including accommodation, all meals, daily treatments, and physician consultations. The equivalent programme at a wellness resort in Switzerland or California would cost $8,000-15,000 — and would likely borrow its protocols from Indian traditions anyway.

For NRIs planning their next India trip, the wellness angle solves two problems at once: you get the family visit, and you get a genuine health reset instead of two weeks of overeating at relatives' houses. Kerala's wellness resorts are within easy reach of Kochi airport (COK), which now connects through multiple Gulf and Southeast Asian hubs. Rishikesh is a five-hour drive from Delhi, or a short flight to Dehradun's Jolly Grant Airport.

The timing is also right. Monsoon season — June through September — is traditionally considered the best period for Ayurvedic treatments, when humidity opens the body's channels and makes therapies more effective. It's also when prices are lowest and crowds thinnest.

The country that invented wellness is now, finally, the world's top destination for it. For NRIs, the question isn't whether to go — it's why you haven't gone already."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Topped the World's Wellness Tourism Rankings — and Your Grandmother Isn't Surprised",
    "subheadline": "A $35 billion industry built on Ayurveda, yoga, and traditions NRIs grew up with. Kerala, Rishikesh, and a new generation of luxury retreats are drawing global wellness travellers — and diaspora families should be next.",
    "slug": make_slug("india-tops-wellness-tourism-rankings-ayurveda-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs grew up with Ayurveda and yoga as household staples. India now leads global wellness rankings, and a 2-week Panchakarma in Kerala costs a fraction of equivalent Western programmes. Monsoon season is ideal timing for treatment and coincides with lower prices.",
    "tags": ["travel", "wellness", "ayurveda", "yoga", "india-tourism", "kerala"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel and Tour World — Top 50 Wellness Destinations 2026", "url": "https://www.travelandtourworld.com/news/article/india-overtakes-thailand-indonesia-japan-switzerland-australia-and-other-countries-around-the-world-to-claim-top-most-position-in-the-top-50-wellness-travel-destinations-rankings-complete-guide-t/"},
        {"name": "AP News — TTW Rankings Release", "url": "https://apnews.com"},
        {"name": "Glance Trends — Wellness Tourism", "url": "https://trends.glance.com"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36993247/pexels-photo-36993247.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art3_body.strip()
}

# ── Publish ───────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles queued at {now}")
