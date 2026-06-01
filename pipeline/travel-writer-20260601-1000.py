#!/usr/bin/env python3
"""Travel writer - 2026-06-01 10:00 UTC batch"""
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


# ─────────────────────────────────────────────
# ARTICLE 1: India's Luxury Hotel Domestic Boom
# ─────────────────────────────────────────────

article1_body = """India's luxury hotel industry is having a moment — and the catalyst is a war 3,000 kilometres away.

As the conflict in West Asia continues to disrupt Gulf-routed international travel, affluent Indian travellers are redirecting their summer budgets toward domestic luxury destinations. The result: a measurable, industry-wide surge in premium hotel bookings that NRIs flying home this summer will feel at the front desk.

## The numbers are hard to ignore

Radisson Hotel Group reports that occupancy across its India portfolio has jumped 5 per cent year-on-year, with average occupancy levels now approaching 75 per cent. Weekends are even tighter. Within the chain's network, hill stations posted a 69 per cent increase over the same period last year, while spiritual destinations — Ayodhya, Katra, Prayagraj — registered 41 per cent growth.

Jaypee Palace Hotel & Convention Centre in Agra says occupancy is up 8 per cent year-on-year. The Leela Palaces, Hotels and Resorts confirms that geopolitical uncertainty has pushed many affluent consumers to reconsider foreign holidays and explore luxury domestic alternatives instead. ITC Hotels reports that booking trends across its leisure properties are running ahead of last summer.

This is not a temporary blip. India's luxury travel market was valued at $72.9 billion in 2024 and is projected to reach $102.8 billion by 2033, according to recent industry estimates. Nearly 89 per cent of Indian high-net-worth individuals plan to increase their travel spending — not by flying more often, but by flying better.

## Where the demand is landing

The winners are not just Goa and Rajasthan anymore. Radisson's standout performers include Jammu & Kashmir, Manali, Mussoorie, and Udaipur. ITC Hotels is seeing rising demand in Prayagraj, Amritsar, and Bhubaneswar — cities that were firmly in the budget travel category five years ago.

The shift toward Tier-2 and Tier-3 cities reflects something deeper: travellers are now choosing destinations based on wellness, gastronomy, and immersive local culture rather than legacy brand recognition. Heritage stays, wellness retreats, nature lodges, and spiritual circuits are the fastest-growing segments across every major chain's portfolio.

Aahana Resort & Spa reports increasing interest in wildlife destinations and experiential luxury. The Leela says heritage-inspired stays and nature-led escapes are seeing their strongest traction in years. ITC Hotels highlights demand for experiences that combine food, wellness, and local storytelling — think Lucknow's kebab trails paired with Nawabi architecture, or Bhubaneswar's temple circuit followed by a coastal wellness retreat.

## What this means for NRIs

For the Indian American diaspora, the practical takeaway is simple: if you are flying to India this summer, book your hotels early.

The domestic travel boom means that premium rooms in places like Udaipur, Mussoorie, and the Kerala backwaters are filling faster than usual. Weekends at top-tier properties are already approaching sellout levels. The old assumption that you could walk into a Taj or Leela during monsoon season and find availability is no longer reliable.

The upside is equally real. India's luxury hospitality infrastructure has improved dramatically in the past three years. Properties that NRIs might remember as decent but dated have undergone serious renovations. New entrants — boutique wellness resorts in Rishikesh, heritage havelis converted into luxury stays in Rajasthan, premium wildlife lodges in Madhya Pradesh — have raised the floor across the board.

For NRIs accustomed to Four Seasons and Aman standards abroad, India's luxury tier is now competitive. The pricing remains a fraction of Western equivalents, but the gap in service quality has narrowed considerably.

## The West Asia factor is not going away

The Iran conflict shows no signs of quick resolution, and Gulf carriers continue to operate at reduced capacity. That means the domestic demand shift is likely to persist through at least the end of monsoon season. Airlines have already cut 250 daily domestic flights from June due to elevated fuel costs and softer connecting traffic from disrupted international routes — fewer flights mean fewer last-minute options for NRIs trying to reach their next Indian destination once they land.

The smartest move for diaspora travellers this summer: book the India hotel before the India flight. The plane will get you there. The room might not wait."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Luxury Hotels Are Riding a Domestic Travel Boom — and NRIs Should Book Before the Rooms Run Out",
    "subheadline": "As the West Asia conflict keeps Gulf carriers grounded and affluent Indians home, Radisson reports 69% growth at hill stations, Leela and ITC Hotels are running ahead of last summer, and Tier-2 cities are the new luxury frontier.",
    "slug": make_slug("india-luxury-hotel-boom-domestic-demand-nri-summer"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs flying to India this summer face a new reality: domestic travellers are filling luxury rooms faster than ever. Weekend availability at top-tier properties is already tight, and the old monsoon-season walkup strategy no longer works. Book early — the pricing is still a fraction of Western equivalents, but the gap is closing.",
    "tags": ["travel", "hotels", "luxury", "India", "NRI", "West Asia"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/leela-itc-hotels-radisson-ride-domestic-travel-demand-heres-whats-driving-it-99797.htm"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/business/3369081-luxury-hotels-in-india-see-surge-in-domestic-demand-amid-global-uncertainty"},
        {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/experiences/hyper-personalisation-is-redefining-luxury-travel-for-modern-travellers"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/32/Udaipur_Lake_Palace.jpg",
    "body": article1_body,
}


# ─────────────────────────────────────────────────
# ARTICLE 2: June Festival Calendar for NRIs
# ─────────────────────────────────────────────────

article2_body = """Every June, while NRIs negotiate monsoon flight delays and debate whether to visit India in the "off season," some of the country's most singular cultural events unfold in near-obscurity — at least to the diaspora.

From a masked Buddhist dance ritual in Ladakh to a fertility festival at one of Hinduism's most powerful Shakti Peethas, June's festival calendar offers experiences that no amount of Diwali nostalgia can replicate. Here are the events worth rerouting your trip for.

## Hemis Festival, Ladakh — June 24-25

The largest and most spectacular religious festival in Ladakh takes place at Hemis Monastery, about 45 kilometres southeast of Leh. The two-day celebration honours the birth anniversary of Guru Padmasambhava — the eighth-century Buddhist master credited with bringing Tantric Buddhism to Tibet.

The centrepiece is the Cham dance: monks in elaborate brocade costumes and oversized painted masks perform choreographed sequences that depict the triumph of good over evil. The dances are accompanied by long horns, cymbals, and drums that echo off the monastery's courtyard walls. Between performances, thangka paintings are unveiled, and locals set up food stalls selling butter tea and thukpa.

For NRIs: Ladakh in late June is accessible (Leh airport operates year-round, and the Manali-Leh highway is typically open by mid-June), the weather is warm by Ladakh standards (15-25°C), and tourist crowds have not yet peaked. Entry to the festival is approximately ₹50 for Indians, ₹200 for foreigners. The real cost is the planning — Leh hotels fill fast during festival week.

## Ambubachi Mela, Guwahati — June 22-26

Kamakhya Temple, perched on Nilachal Hill overlooking the Brahmaputra, hosts one of India's most distinctive and least understood festivals. Ambubachi marks the annual menstruation of Goddess Kamakhya — the temple closes for three days, then reopens with celebrations that draw lakhs of devotees, sadhus, and tantric practitioners from across the subcontinent.

The festival is both a major pilgrimage and a living exhibition of tantric Hinduism. Devotees receive pieces of the angavastha (red cloth) that drapes the deity during the closure period, considered deeply auspicious. The surrounding fair features folk music, traditional Assamese food, and a palpable energy that has no equivalent elsewhere in India.

For NRIs: Guwahati is a direct flight from Delhi, Mumbai, Kolkata, and Bengaluru. The festival coincides with early monsoon, so rain is guaranteed — pack accordingly. The temple crowd during Ambubachi is enormous; plan to arrive a day early and stay near the temple complex. This is not a sanitised heritage experience. It is raw, devotional, and unforgettable.

## Shimla Summer Festival — June 8-12

The Ridge — Shimla's grand colonial-era promenade — transforms into an open-air stage for five days of cultural performances, folk dances, music evenings, and community competitions. The Himachal Pradesh Tourism Department organises the event annually, and this year's edition includes a Himachali food festival, a flower show, painting contests, and the release of a coffee table book featuring rare archival photographs of Shimla.

For NRIs: Shimla in early June is pleasant (20-28°C), the monsoon has not yet arrived in the western Himalayas, and the festival is free. It is an easy weekend trip from Delhi (Kalka-Shimla toy train or a 7-hour drive). If your India trip happens to overlap with these dates, it is worth the detour — think of it as India's version of a small-town arts festival, set against Himalayan ridgelines.

## Shabd, NMACC Mumbai — June 5

For NRIs passing through Mumbai, this single-evening event at the Jio World Centre's Grand Theatre is worth marking. Shabd brings together Urdu poet Waseem Barelvi, actor Ratna Pathak Shah, storyteller Nayab Midha, and sitar player Mehtab Ali Niazi in a live exploration of Hindustani language through spoken word, poetry, and music.

Curated by Kommune, the event sits at the intersection of literary tradition and live performance — a format that barely exists outside India. Tickets start at ₹750.

## Tabla & Taalis: A Sufi Jam Night, Delhi — June 20

A gathering of over 2,000 voices singing Sufi music under the open sky at Talkatora Stadium. Performed by the group Jogi, it is part concert, part communal meditation — the kind of event that makes you understand why qawwali survived centuries of political upheaval. Tickets from ₹1,899.

## The NRI calculation

June is India's least popular month for diaspora travel. Flights are cheaper (one-way fares from the US start around $500 this month). Hotels have availability. And the cultural calendar is, counterintuitively, richer than the peak winter season that most NRIs default to.

The monsoon is real — you will get wet, flights will sometimes be delayed, and hill stations will be clouded in. But the trade-off is access to experiences that the December-January crowd never sees: masked dances in Ladakh, tantric rituals in Assam, Sufi devotion in Delhi, and the quiet luxury of an India that is not performing for tourists.

The festivals listed here require no special tickets, no tour operators, and no advance registration beyond a plane ticket and a hotel room. They require only the willingness to show up in a month when most of the diaspora stays home."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "From Hemis to Kamakhya — India's June Festival Calendar That NRIs Keep Missing",
    "subheadline": "Masked Buddhist dances in Ladakh, a tantric fertility festival in Assam, Sufi devotion in Delhi, and a colonial-era arts festival in Shimla — June's cultural calendar is richer than any Diwali trip, and almost no one in the diaspora knows about it.",
    "slug": make_slug("hemis-kamakhya-june-festivals-nri-calendar"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "June is the diaspora's blind spot. Flights are cheapest, hotels have availability, and India's cultural calendar — from Ladakh's Hemis Festival to Assam's Ambubachi Mela — is richer than the December-January peak most NRIs default to. These are experiences that require no tour operator, just the willingness to show up.",
    "tags": ["travel", "festivals", "India", "NRI", "Hemis", "Ladakh", "Assam", "Shimla", "culture"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel+Leisure Asia", "url": "https://www.travelandleisureasia.com/in/destinations/india/the-most-exciting-festivals-and-events-happening-in-india-in-june-2026/"},
        {"name": "InsideAsia Tours", "url": "https://www.insideasiatours.com/india/when-to-go/"},
        {"name": "Wikipedia - Hemis Festival", "url": "https://en.wikipedia.org/wiki/Hemis_Festival"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Hemis_Monastery_02.jpg/3840px-Hemis_Monastery_02.jpg",
    "body": article2_body,
}


# ─────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
