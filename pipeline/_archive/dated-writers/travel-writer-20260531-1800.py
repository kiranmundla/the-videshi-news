#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-31 18:00 UTC run. Two fresh travel articles."""

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

# ── Article 1: Sikkim Summer Tourism Surge ──────────────────────────────

sikkim_body = """Sixteen thousand tourists in five days. That is the number Sikkim's 3rd Mile check post recorded between May 24 and May 28 — and the state's summer season is barely warming up.

As a brutal heatwave sends temperatures above 45°C across the Indo-Gangetic plain, Sikkim has become the Himalayan escape of choice for families, trekkers, and — increasingly — NRI visitors timing their India trips around their children's summer break.

## The numbers are hard to argue with

Official data from the Sikkim tourism department paints a picture of sustained, accelerating demand. Over those five days in late May, 5,300 vehicles ferried visitors through the 3rd Mile checkpoint on the road to Nathula Pass and Tsomgo Lake. The daily breakdown: 6,591 tourists on May 24 alone, dipping to 2,772 on a quieter Sunday, then surging back to 4,399 by May 28.

The gender split — 7,836 men, 6,368 women, and 2,401 children — confirms this is not backpacker traffic. These are families. And international visitors from the US, UK, Canada, Australia, France, Germany, Japan, and Singapore are arriving alongside Indian domestic tourists from West Bengal, Bihar, and Uttar Pradesh.

For NRI families arriving in India during June or July, the implication is direct: Sikkim is no longer an afterthought tacked onto a Delhi-Agra itinerary. It is the itinerary.

## Why NRIs should pay attention

The appeal starts with temperature. While Delhi bakes at 46°C and even Shimla sees crowded, sweaty hillsides, Sikkim sits at 18–25°C — genuinely cool, not just less hot. Gangtok, the capital, is at 5,400 feet. Nathula Pass, the old Silk Road border crossing with China at 14,140 feet, offers snow-dusted scenery and cold mountain air that no air-conditioned mall in Gurgaon can replicate.

But the real draw for diaspora families is the combination of adventure and accessibility that Sikkim now offers. Tsomgo Lake, a glacial lake at 12,310 feet, has yak rides for children and jaw-dropping Himalayan panoramas for the Instagram-conscious. Buddhist monasteries like Rumtek and Pemayangtse provide cultural immersion that is distinctly different from the temple circuit of Rajasthan or Tamil Nadu. And Sikkim's status as India's first fully organic state means the food — momos, thukpa, local cheeses — actually tastes like something.

## Logistics that actually work

Getting to Sikkim has traditionally been the deterrent. The nearest airport is Bagdogra in West Bengal, followed by a four-hour drive through winding mountain roads. Pakyong Airport near Gangtok exists but operates limited flights.

The good news: Bagdogra is now well-connected with direct flights from Delhi, Mumbai, Kolkata, and Bengaluru — all cities NRIs are likely flying into internationally. From Bagdogra, the road to Gangtok has improved significantly, with new stretches of highway cutting travel time. Pre-booked SUVs are the standard transport and run about ₹3,000–4,000 one way.

The permit system is the part most NRI families do not know about until it is too late. Indian citizens need Inner Line Permits for North Sikkim (free, available online or at checkpoints). Foreign passport holders — including OCI cardholders in some cases — need Restricted Area Permits for Nathula and several North Sikkim destinations. These require advance application through a registered tour operator. Skip this step and you will be turned back at the checkpoint, no exceptions.

## What to book now

Sikkim's hotel supply is thin relative to demand. Gangtok has a handful of decent four-star properties — Mayfair Spa Resort and The Elgin Nor-Khill are the most reliable — but occupancy is running above 90% through June. Lachung and Lachen in North Sikkim have homestays and lodges, not luxury hotels. Book at least three weeks in advance during summer.

The best NRI itinerary runs five to seven days: two nights in Gangtok (monastery visits, MG Marg walking street, Himalayan Zoological Park), a day trip to Tsomgo Lake and Nathula Pass, two nights in Lachung or Lachen (Yumthang Valley, Zero Point), and a buffer day for weather-related delays — because in the Himalayas, weather always wins.

Carry cash. UPI works in Gangtok but coverage drops sharply once you leave the capital. ATMs exist but are unreliable in North Sikkim.

## The bigger picture

Sikkim's tourism surge is part of a broader shift in how Indians — and the diaspora — are traveling within India. The old circuit of Delhi-Agra-Jaipur is losing ground to experiential destinations that offer cool weather, adventure, and cultural depth. Meghalaya, Arunachal Pradesh, and Ladakh are seeing similar growth, but Sikkim's combination of accessibility, safety, and infrastructure puts it ahead of the pack for family travel.

For NRIs planning a summer trip home, the math is simple: fly into Bagdogra, spend a week in Sikkim, and return with photos that actually make your colleagues jealous — not another shot of the Taj Mahal shrouded in smog."""

sikkim_article = {
    "id": str(uuid.uuid4()),
    "headline": "Sikkim Just Logged 16,700 Tourists in Five Days — Why NRI Families Should Book Before It Sells Out",
    "subheadline": "As India's heatwave sends temperatures past 45°C, Sikkim's glacial lakes, Buddhist monasteries, and 18°C summers are drawing record crowds — including a growing wave of diaspora families.",
    "slug": make_slug("sikkim-summer-tourism-surge-nri-family-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRI families visiting India during summer school breaks are increasingly choosing Sikkim over overcrowded hill stations. Permits, logistics, and booking timelines that diaspora visitors need to know.",
    "tags": ["travel", "sikkim", "summer", "family-travel", "hill-stations", "nri-guide"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/7q2zef5dpm3z/"},
        {"name": "Curly Tales", "url": "https://curlytales.com/not-mussoorie-or-shimla-this-state-tops-new-year-2026-travel-hotels-fully-booked/"},
        {"name": "Sikkim Tourism Department", "url": "https://www.sikkimtourism.gov.in/"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Tsongmo_Lake_or_Changu_Lake_-_East_Sikkim.jpg/3840px-Tsongmo_Lake_or_Changu_Lake_-_East_Sikkim.jpg",
    "body": sikkim_body
}

# ── Article 2: India's Industrial Hospitality Boom ──────────────────────

hospitality_body = """Forget Goa and Jaipur. India's next hotel boom is happening in places most NRI business travelers have never voluntarily visited — Aurangabad, Nashik, Sriperumbudur, Dholera, and the factory belts ringing Chennai.

New research from Noesis Capital Advisors quantifies the gap: India has roughly 375,000 branded hotel rooms today. Projected demand by 2030 requires about 630,000. That shortfall — one of the largest among major economies — is not concentrated in tourist destinations or metro downtowns. It is widest in the industrial corridors and Tier II cities now absorbing billions of dollars in manufacturing investment.

For the 200,000-odd NRI professionals who fly to India each year on business — consulting, vendor management, factory audits, family-owned plant visits — this is not abstract industry analysis. It is the reason your last trip to a manufacturing site outside Chennai involved a three-star hotel with intermittent hot water and a conference room that smelled like last night's biryani.

## The China Plus One effect is filling hotel rooms

The global supply chain reset — companies diversifying manufacturing away from China into India — is the engine driving this shift. Tamil Nadu's Sriperumbudur corridor near Chennai is now home to automotive and electronics plants from Samsung, Hyundai, BMW, and Foxconn. Gujarat's Dholera Special Investment Region is building an entire greenfield smart city around semiconductor and solar manufacturing. Maharashtra's Nashik-Aurangabad belt is attracting aerospace, defence, and specialty chemicals facilities.

Each of these corridors generates a specific type of hotel demand that is structurally different from tourism. Engineers stay for months during plant commissioning. EPC contractors rotate through on weekly cycles. Foreign delegations arrive for quality audits. Government compliance teams make scheduled inspections. This demand shows up on a Tuesday in February as reliably as in peak season — it is tied to production schedules and export orders, not monsoon patterns or festival calendars.

Global hotel brands have noticed. Courtyard by Marriott, Hyatt Place, and Fern Hotels are already opening or expanding in manufacturing hubs like Vithalapur in Gujarat and Talegaon near Pune. Industry analysts say feasibility studies are underway in Ranjangaon, Manesar, Hosur, and Pithampur — towns that did not appear in any hotel investment conversation five years ago.

## Why NRI business travelers should care

If you work in consulting, supply chain, or technology and your company has India operations, your travel map is shifting whether you like it or not. The familiar loop of Mumbai-Bengaluru-Hyderabad is being supplemented — and in some sectors replaced — by trips to manufacturing corridors that lack the hospitality infrastructure you take for granted in metro cities.

The practical impact is real. Branded hotel supply near India's defence manufacturing corridors, where sensitive work often requires extended stays, is almost nonexistent. The same is true for renewable energy project sites in Gujarat and Rajasthan, where green hydrogen, solar, and battery plants are creating entirely new industrial townships in areas that previously had no organized hospitality.

For NRI professionals visiting family-owned businesses in Tier II cities — a common pattern in the Gujarati, Marwari, and South Indian diaspora — the hotel situation is particularly relevant. A Courtyard by Marriott in Aurangabad or a Hyatt Place in Nashik changes the calculus of how long you are willing to stay, how often you visit, and whether you bring your family along.

## The investment angle

For NRIs with capital to deploy, India's industrial hospitality gap represents something more than a business travel inconvenience — it is an investment thesis.

The math is straightforward. Hotel development is a five-to-six-year cycle from land acquisition to stabilized operations. By the time an industrial corridor becomes obvious to every investor, land prices have surged, competition has intensified, and returns have compressed. The window where structural demand exists but supply has not caught up is narrow — and it is open now in about fifteen Indian cities that most hospitality investors are still ignoring.

The global playbook supports this pattern. Huntsville, Alabama became a serious hotel market because of aerospace and defence. Jubail, Saudi Arabia's hotel demand was built entirely on petrochemicals. Suzhou, China evolved from an industrial park into a full urban ecosystem with layered hospitality demand. India is entering the same phase at far greater scale.

The cities to watch — Aurangabad, Nashik, Vizag, Coimbatore, Hosur, Vadodara, Surat, Lucknow, Bhubaneswar — share a common profile: strong manufacturing pipeline, affordable land, thin branded competition, and undersupplied mid-scale hotel inventory. For NRI investors comfortable with long-cycle assets, these markets offer both rising room demand and rising land values.

## What this means for India's travel infrastructure

The broader implication extends beyond hotel rooms. As industrial corridors mature, they evolve into full ecosystems requiring branded residences, co-living spaces, retail, wellness centers, hospitals, and convention venues alongside traditional lodging. The manufacturing town of today becomes the business city of tomorrow — and that transformation creates compounding demand for hospitality at every price point.

India's logistics sector alone is projected to grow from roughly $244 billion in 2025 to more than $429 billion by 2034. Defence production has crossed ₹1.5 lakh crore. The semiconductor, EV, and data centre buildouts are still in early stages. Each of these programs puts people in motion — and people in motion need places to stay.

For NRI business travelers, the short-term message is practical: expect improving hotel options in India's industrial corridors over the next three to five years, but do not expect them yet. For NRI investors, the message is strategic: the map of Indian hospitality is being redrawn by manufacturing, not tourism — and the early movers will capture the value."""

hospitality_article = {
    "id": str(uuid.uuid4()),
    "headline": "India's Next Hotel Boom Is Not in Goa — It Is in the Factory Towns NRI Business Travelers Already Dread",
    "subheadline": "Aurangabad, Nashik, Sriperumbudur, and Dholera are the unlikely epicentres of a hospitality supply gap that matters to every NRI who has ever endured a bad hotel near a manufacturing site.",
    "slug": make_slug("india-industrial-hospitality-boom-nri-business"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRI business travelers visiting India's expanding manufacturing corridors face thin hotel supply in Tier II cities. Industrial hospitality is also an emerging investment thesis for diaspora capital.",
    "tags": ["travel", "hospitality", "business-travel", "manufacturing", "investment", "tier-2-cities"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/0rmo4rccbxbz/"},
        {"name": "Hotelier India", "url": "https://www.hotelierindia.com/operations/why-indias-next-great-hospitality-frontier-is-opening-up-inside-its-industrial-corridors"},
        {"name": "Noesis Capital Advisors", "url": "https://www.noesis.co.in/"}
    ]),
    "score_total": 70,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/12522753/pexels-photo-12522753.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": hospitality_body
}

# ── Publish ─────────────────────────────────────────────────────────────

articles = [sikkim_article, hospitality_article]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
