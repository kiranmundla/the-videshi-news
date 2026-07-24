#!/usr/bin/env python3
"""Travel writer — 2026-06-09 06:00 UTC run. Two fresh articles for The Videshi."""

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
    # ── ARTICLE 1: Air India + Riyadh Air MOU ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Just Teamed Up With Saudi Arabia's Brand-New Airline — and NRIs on Both Sides Should Pay Attention",
        "subheadline": "A new MOU with Riyadh Air promises codeshares, shared loyalty points, and smoother connections through Delhi, Mumbai, and Riyadh — exactly the corridors 2.6 million Indians in the Kingdom use most.",
        "slug": make_slug("air-india-riyadh-air-mou-codeshare-nri-saudi"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Over 2.6 million Indians live and work in Saudi Arabia, making the India-KSA air corridor one of the busiest diaspora routes in the world. A codeshare between Air India and Riyadh Air means single-ticket bookings across both networks, loyalty program reciprocity for frequent flyers, and seamless connections through Riyadh to Europe and beyond — directly benefiting NRIs who shuttle between the Gulf and home.",
        "tags": ["travel", "airlines", "air-india", "riyadh-air", "saudi-arabia", "codeshare", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TTR Weekly", "url": "https://ttrweekly.com/2026/06/09/air-india-and-riyadh-air-sign-mou/"},
            {"name": "Aviation Week", "url": "https://aviationweek.com/air-transport/airlines-lessors/riyadh-air-air-india-pursue-codeshare-interline-collaboration"},
            {"name": "Arabian Gulf Business Insight", "url": "https://www.agbi.com/articles/riyadh-airs-deal-with-air-india-takes-a-long-term-view/"},
            {"name": "Hospitality News India", "url": "https://hospitalitynews.in/air-india-riyadh-air-sign-connectivity-pact/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/HZ-RXX_Boeing_787-9_Dreamliner_Riyadh_Air_LHR_4.1.26_%2855027186633%29.jpg/3840px-HZ-RXX_Boeing_787-9_Dreamliner_Riyadh_Air_LHR_4.1.26_%2855027186633%29.jpg",
        "image_caption": "A Riyadh Air Boeing 787-9 Dreamliner at London Heathrow Airport",
        "image_attribution": "Wikimedia Commons",
        "body": """Air India and Riyadh Air, Saudi Arabia's brand-new national carrier, have signed a Memorandum of Understanding that lays the groundwork for codeshare flights, interline ticketing, reciprocal loyalty benefits, and joint cargo operations between India and the Kingdom. The agreement, announced on June 4, positions Delhi, Mumbai, and Riyadh as interconnected hubs — and for the Indian diaspora on both ends, the implications are immediate and practical.

## What the deal actually includes

The MOU covers five areas of collaboration. First, codeshare and interline arrangements: once regulatory approvals come through, passengers will be able to book a single ticket that spans both airlines' networks, with baggage checked through and connections handled seamlessly. Second, reciprocal loyalty benefits — meaning Air India's Flying Returns members could eventually earn and burn points on Riyadh Air metal, and vice versa. Third, cargo partnerships, which matter for the $43 billion bilateral trade corridor. Fourth, operational support. And fifth, digital and technology collaboration, though neither airline has specified what that looks like yet.

x-official:https://x.com/airindia/status/2062423722611634513

Campbell Wilson, Air India's CEO, called it "a natural partnership" between "two important growth markets in global aviation." Riyadh Air's CEO Tony Douglas — the former Etihad boss who knows Gulf-India traffic intimately — has been building a roster of airline partnerships ahead of Riyadh Air's commercial launch, expected later this year.

## Why NRIs should care

The numbers tell the story. Over 2.6 million Indians live and work in Saudi Arabia, making the Indian community the largest expatriate group in the Kingdom. They fly home for weddings, festivals, family emergencies, and the annual leave cycle that peaks around Diwali and summer. Until now, that traffic has been split between Air India, IndiGo, Saudia, and the Gulf Big Three — Emirates, Qatar, and Etihad — each routing through their own hubs.

A functioning Air India–Riyadh Air codeshare changes the math. An NRI engineer in Riyadh could book a single ticket from Riyadh to Thiruvananthapuram via Delhi, with luggage checked through and a single loyalty account accruing miles. A business traveler heading from Mumbai to Jeddah could connect onward to a European destination on Riyadh Air's growing long-haul network without re-ticketing.

## The bigger picture: Riyadh vs. Dubai

This partnership fits a larger geopolitical chess match. Saudi Arabia is spending heavily to turn Riyadh into a global aviation hub that can compete with Dubai, Doha, and Abu Dhabi. Riyadh Air — with an order book of 72 Boeing 787 Dreamliners — is the centrepiece of that ambition. But the airline needs feed traffic, and India's 1.4 billion people represent the single largest untapped source.

The catch, as aviation analysts point out, is that government-imposed bilateral caps still limit the number of flights between India and Saudi Arabia. Saudia already operates a codeshare with Air India that took effect in February. Adding Riyadh Air to the mix means more airline brands competing for the same capped slots — unless New Delhi and Riyadh negotiate expanded air service agreements.

John Grant, a partner at Midas Aviation, put it plainly: "Air India will hope to benefit from association with a new and prestigious brand, while Riyadh Air will be hoping to get connecting traffic and a better hearing in any future discussions around capacity growth."

## What to watch

The MOU is a framework, not a finished product. Codeshares require regulatory approval from both countries' aviation authorities. Loyalty integration takes months of technical work. And Riyadh Air hasn't even started scheduled commercial service yet — its first flights are expected in the second half of 2026.

But for the millions of Indians who move between the subcontinent and the Gulf every year, the direction is clear: more options, better connections, and the slow erosion of the hub monopoly that Emirates and Qatar Airways have held for two decades. If you're an NRI in the Kingdom, keep your Flying Returns account active — it may soon be worth more than you think."""
    },

    # ── ARTICLE 2: Marriott Luxury Push — Ritz-Carlton Kathmandu + JW Marriott Siliguri ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Nepal Is Getting a Ritz-Carlton — and NRIs Planning Himalayan Trips Just Got a Luxury Upgrade",
        "subheadline": "Marriott's landmark deal with CG Hospitality brings the Ritz-Carlton and Westin brands to Kathmandu for the first time, plus a JW Marriott in Siliguri — the gateway to Darjeeling, Sikkim, and the Northeast.",
        "slug": make_slug("ritz-carlton-kathmandu-jw-marriott-siliguri-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs who combine India trips with Nepal — whether for Pashupatinath, Everest base camp treks, or family visits across the border — the arrival of Ritz-Carlton and Westin in Kathmandu and JW Marriott in Siliguri means familiar luxury brands at two key gateways. Siliguri is the road and rail hub for Darjeeling, Kalimpong, Gangtok, and the entire Northeast corridor that diaspora families increasingly explore during extended home visits.",
        "tags": ["travel", "hotels", "marriott", "ritz-carlton", "kathmandu", "nepal", "siliguri", "luxury", "nri"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Tripura Star News", "url": "https://tripurastarnews.com/marriott-international-and-cg-hospitality-global-sign-multi-unit-agreement/"},
            {"name": "Hospitality Biz India", "url": "https://www.hospitalitybizindia.com/news/cg-hospitality-and-marriott-international-deepen-partnership/"},
            {"name": "Travel Mail India", "url": "https://www.travelmail.in/marriott-cg-hospitality-india-nepal/"},
            {"name": "Business News This Week", "url": "https://businessnewsthisweek.com/marriott-cg-hospitality-india-nepal/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36524167/pexels-photo-36524167.jpeg",
        "image_caption": "The Kathmandu Valley at sunset with the Himalayas in the background",
        "image_attribution": "Pexels",
        "body": """Marriott International and CG Hospitality Global signed a three-property deal on June 8 that will bring the Ritz-Carlton and Westin brands to Kathmandu and plant a JW Marriott in Siliguri, the eastern Indian city that serves as the gateway to Darjeeling, Sikkim, and the Northeast. The properties are expected to open by 2031, adding nearly 450 rooms to Marriott's South Asia portfolio — and giving diaspora travelers two new luxury anchors on a circuit that has long been underserved by international hotel brands.

## The properties

**The Ritz-Carlton Kathmandu** will be the first Ritz-Carlton in Nepal. No details on room count or exact location have been released, but the brand's positioning — ultra-premium, typically 200+ keys, heavy on F&B and spa — suggests a flagship property aimed at the growing wave of luxury travelers visiting Nepal for trekking, spiritual tourism, and destination weddings.

**The Westin Kathmandu** will complement the Ritz-Carlton with Marriott's wellness-focused premium brand. Together, the two Kathmandu properties will add roughly 300 keys. For context, Kathmandu's existing international hotel stock is thin: a Marriott-branded hotel already operates in the city, but options at the Ritz-Carlton tier have been essentially nonexistent.

**JW Marriott Hotel Siliguri** rounds out the deal with 150 rooms. Siliguri — population 700,000, located at the foot of the Himalayas in West Bengal — is the logistical hub for anyone heading to Darjeeling by road, Gangtok by highway, or the Northeast by rail. The hotel will sit just 10 kilometers from Bagdogra Airport, which handles direct flights from Delhi, Mumbai, Kolkata, and Bangalore. Plans include four restaurants, a signature JW spa, a pool, a fitness centre, and 1,500 square meters of event space.

## Why this matters for NRI travelers

The India-Nepal travel corridor is one of the busiest in South Asia, and NRIs are an increasingly important segment of it. Pashupatinath Temple in Kathmandu draws hundreds of thousands of Hindu pilgrims annually. Everest base camp treks and Annapurna Circuit hikes are bucket-list items for second-generation diaspora travelers. And the open border between India and Nepal means that families visiting relatives in Bihar, UP, or West Bengal routinely extend their trips across the frontier.

Until now, the gap has been at the top end. Kathmandu has plenty of mid-range hotels and a handful of boutique properties, but nothing that carries the recognition — or the loyalty program integration — that a Marriott Bonvoy member expects. An NRI family that accumulates points on business travel in the US can now burn them in Kathmandu, which changes the calculus for trip planning.

The JW Marriott Siliguri fills a different gap. The corridor from Bagdogra to Darjeeling has historically offered heritage tea estate bungalows and budget hotels, with very little in between. A JW Marriott at the base of the route means travelers can break the journey in comfort — arriving from a red-eye flight, recovering for a night, and heading up to the hills the next morning. For NRI families with elderly parents who can't handle the six-hour mountain drive in one shot, this is a practical upgrade, not just a luxury one.

## CG Hospitality: Nepal's biggest player

The partner behind all three properties is CG Hospitality Global, the hospitality arm of Nepal's Chaudhary Group. Founded by Binod Chaudhary — Nepal's only billionaire and a Rajya Sabha member — CG is the country's largest conglomerate, with interests spanning FMCG, finance, cement, telecom, and real estate. The group already operates the existing Kathmandu Marriott Hotel and has Marriott-branded properties across South Asia.

The signing ceremony was attended by David Marriott, the company's Chairman of the Board, signaling the strategic weight Marriott places on the South Asian expansion. Rajeev Menon, Marriott's President for Asia Pacific (excluding China), called the partnership "a reflection of the growing demand for world-class hospitality experiences in the region."

## The timeline and the fine print

All three properties are anticipated to open in 2031 — five years out. That's standard for luxury hotel development in South Asia, where land acquisition, permits, and construction timelines routinely stretch beyond initial estimates. The announcement is a signing, not a groundbreaking.

But for NRIs planning future trips, the direction matters more than the exact opening date. Nepal is positioning itself as a serious luxury tourism destination, and Marriott is betting nearly 450 rooms on that thesis. Siliguri, meanwhile, is finally getting the kind of infrastructure that matches its importance as a transit hub.

If your idea of a dream trip involves Darjeeling tea gardens in the morning and a proper hotel bed at night — or Everest views followed by a Ritz-Carlton spa — the pieces are starting to fall into place."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
