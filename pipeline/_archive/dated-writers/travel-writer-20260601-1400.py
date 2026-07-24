#!/usr/bin/env python3
"""Travel writer: 2 fresh articles for The Videshi — 2026-06-01 14:00 UTC run."""

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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


def validate_image(url):
    """Verify an image URL returns 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {url[:80]}... ({cl} bytes)")
            return True
        # Some servers don't return Content-Length on HEAD; try GET with stream
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get("Content-Type", "")
        chunk = r2.raw.read(6000)
        r2.close()
        if r2.status_code == 200 and "image" in ct2 and len(chunk) > 5000:
            print(f"  ✓ Image validated (GET): {url[:80]}... ({len(chunk)}+ bytes)")
            return True
        print(f"  ✗ Image failed: status={r2.status_code}, ct={ct2}, size={len(chunk)}")
        return False
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
        return False


# ── Article 1 ─────────────────────────────────────────────────────────
# Air India's 2026 route expansion

art1_body = """Air India's route map for 2026 reads less like a schedule update and more like a strategic manifesto. The Tata-owned carrier has announced a wave of new international services that, taken together, represent its most ambitious expansion since privatisation — and for the Indian American diaspora, the implications are immediate and practical.

## London to Bengaluru: The Route South India Has Been Waiting For

The headline addition lands on 1 August. Air India will operate nonstop service from London Heathrow to Bengaluru using the widebody Airbus A350-900, the same aircraft that has won praise for its business-class lie-flat seats and quieter cabin. Until now, NRIs in the UK heading to Karnataka, Kerala, or Tamil Nadu have overwhelmingly routed through Mumbai or Delhi — adding a domestic connection, a second boarding pass, and often an overnight layover. The direct link eliminates that detour entirely.

For the estimated 400,000-plus people of South Indian origin in Britain — concentrated in London, Birmingham, and the West Midlands — this is not a marginal improvement. It is a structural change in how they get home.

## Tokyo, Shanghai, and the Asia Pivot

Air India's Delhi–Tokyo Haneda service, which shifted from Narita in March 2025, has been upgraded to daily frequency. Through an expanded codeshare with Star Alliance partner All Nippon Airways, passengers can now connect onward to Fukuoka, Hiroshima, Nagoya, Okinawa, Osaka, and Sapporo on a single ticket with checked baggage flowing through. For NRIs working in Japan's tech and automotive sectors — or planning a family holiday — the one-ticket convenience is a genuine unlock.

Meanwhile, Delhi–Shanghai has resumed with four weekly flights after a nearly six-year hiatus, reconnecting two of Asia's largest economies. India–Singapore capacity has been ramped to 52 weekly flights, giving travellers near-hourly flexibility on what is already one of the busiest diaspora corridors.

## Europe Gets Deeper Coverage

Four weekly nonstop flights between Delhi and Rome launched in late March, and five weekly services to Hanoi started in May, complementing existing daily flights to Ho Chi Minh City. Neither city had direct Air India service before, and both open visa-friendly leisure routes that previously required Gulf carrier connections.

## What NRIs Should Actually Do With This Information

The practical takeaway is simple: Air India's network now covers enough of the map that routing through Dubai, Doha, or Abu Dhabi is no longer the default for most India-bound journeys from the US, UK, or Asia. With IndiGo simultaneously holding 17.6 percent of India's international market share — surpassing Emirates at 8.3 percent — the era of Gulf carrier dominance on India routes is measurably ending.

For NRIs booking summer and autumn travel, Air India's A350 product is competitive with anything in the market on comfort, and the direct-routing advantage on connections like Heathrow–Bengaluru and Haneda–Delhi saves real hours. The airline has also won the APEX Award for Best Entertainment in Central and Southern Asia, a signal that the inflight experience has caught up with the fleet investment.

Book early. These new routes will fill fast as word spreads."""

art1_image = "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png"

# ── Article 2 ─────────────────────────────────────────────────────────
# Royal Enfield Himalayan Odyssey & Base Camp Ladakh 2026

art2_body = """If you grew up watching Royal Enfield Bullets thud through Indian hill stations, the Himalayan Odyssey needs no introduction. For NRIs who have spent years promising themselves they would "do Ladakh one summer," 2026 might be the year to stop promising and start registering.

## The Odyssey: 2,400 Kilometres, 16 Days, One Legacy

Royal Enfield has opened registrations for Himalayan Odyssey 2026, running from 25 June to 10 July. The route threads through Leh, Hanle, Zanskar, and Manali, culminating at Umling La — the world's highest motorable road at 19,024 feet. Riders choose between Team Baralacha La and Team Shinku La, each path offering distinct high-altitude cultures and terrain.

This year's edition is unusually significant: it marks Royal Enfield's 125th anniversary. The company, founded in 1901, has turned what began as a niche British motorcycle brand into a global adventure icon — and nowhere is that identity more concentrated than on the roads of Ladakh.

The Odyssey is not a guided tour. It is a rider-led expedition through water crossings, dirt trails, and technical passes where oxygen runs thin and mechanical skill matters as much as nerve. Participants ride their own or rented Royal Enfield motorcycles. Meals, accommodation (mostly camps), and mechanical support are included, but the Himalayas supply the difficulty.

## Base Camp Ladakh: A Newer, Broader Format

For those who want the Ladakh experience without committing to two weeks in the saddle, Royal Enfield is launching a second event: Himalayan Base Camp — Ladakh Edition, a three-day experiential gathering in Leh from 4 to 6 September 2026. Set at 11,480 feet, the format goes beyond motorcycling to include overlanding, cycling, kayaking, bouldering, and mountaineering, all led by expert practitioners.

"The Himalayan Base Camp is a rendezvous point for all adventurers, regardless of whether they are driven by horsepower, willpower, or their own two feet," said Mohit Dhar Jayal, Royal Enfield's Chief Brand Officer. Registrations opened on 1 May.

## Why NRIs Should Pay Attention

Adventure tourism in India is no longer a fringe pursuit. Ladakh permit data from May 2026 shows over 16,700 tourists — including significant numbers from the US, UK, and Canada — passing through checkpoints in just five days. Nathula Pass issued 618 permits in two days; Tsomgo Lake exceeded 2,500 daily online permits. The infrastructure is real, the demand is documented, and the window is finite.

For Indian Americans in particular, the calculus is straightforward. A Himalayan Odyssey slot gives you a structured, supported framework to ride roads that require no prior expedition experience but deliver the kind of raw physical engagement that a beach resort cannot. The September Base Camp offers a shorter, more accessible version — fly into Leh on a Thursday, kayak and boulder for three days, fly out Sunday.

## Practical Details

**Himalayan Odyssey 2026**: 25 June–10 July. 2,400+ km. Register at royalenfield.com. Requirements include passport, valid licence, medical fitness certificate, and high-risk mediclaim insurance with personal accident cover. Royal Enfield motorcycles available for rent.

**Himalayan Base Camp — Ladakh Edition**: 4–6 September 2026, Leh. Registrations open now at royalenfield.com. Multi-discipline: motorcycling, overlanding, cycling, kayaking, bouldering, mountaineering.

**Getting there**: Air India, IndiGo, and Vistara operate daily flights to Leh's Kushok Bakula Rimpochee Airport from Delhi. Book at least two weeks ahead during summer — seats fill quickly. Acclimatisation matters: plan to arrive a day early and stay below 12,000 feet for the first 24 hours.

The Himalayas are not going anywhere. But your window to ride them this summer is already closing."""

art2_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Pangong_Tso_2.jpg/3840px-Pangong_Tso_2.jpg"

# ── Validate images ───────────────────────────────────────────────────
print("Validating images...")
art1_img_valid = validate_image(art1_image)
art2_img_valid = validate_image(art2_image)

# ── Build article payloads ────────────────────────────────────────────
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Is Adding London–Bengaluru, Daily Tokyo, and a Dozen Other Routes — Here's What NRIs Need to Know",
        "subheadline": "The Tata-owned carrier's 2026 expansion covers four continents and finally gives South Indian diaspora in Britain a nonstop option home.",
        "slug": make_slug("air-india-2026-route-expansion-london-bengaluru-tokyo-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Direct London-Bengaluru A350 service starting August eliminates the Mumbai/Delhi layover for 400K+ South Indians in the UK; daily Tokyo and resumed Shanghai flights serve NRIs in East Asian tech and business roles; 52 weekly Singapore flights give US-based NRIs better one-stop options to South India.",
        "tags": ["travel", "airlines", "air-india", "routes", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "BrightSun Travel", "url": "https://brightsun.co.in/blog/air-india-new-routes-2026/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/indigo-and-air-india-surges-ahead/"},
            {"name": "Travel Daily Media", "url": "https://www.traveldailymedia.com/air-india-daily-flights-tokyo-haneda/"},
            {"name": "India Outbound", "url": "https://indiaoutbound.info/air-india-shifts-tokyo-flights-to-haneda/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": art1_image if art1_img_valid else None,
        "image_attribution": "Wikimedia Commons" if art1_img_valid else None,
        "is_editorial": False,
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Royal Enfield's Himalayan Odyssey 2026 Is Open for Registration — and NRIs Should Stop Dreaming and Sign Up",
        "subheadline": "The iconic 2,400-km Ladakh expedition marks Royal Enfield's 125th anniversary, and a new three-day Base Camp in September lowers the barrier for first-timers.",
        "slug": make_slug("royal-enfield-himalayan-odyssey-base-camp-ladakh-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Ladakh is the most-deferred bucket-list trip for Indian Americans; the Odyssey provides mechanical support and structure that removes the planning barrier; the shorter September Base Camp suits NRIs with limited vacation days; permit data shows growing US/UK/Canada participation.",
        "tags": ["travel", "adventure", "ladakh", "royal-enfield", "motorcycling"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Royal Enfield UK", "url": "https://www.royalenfield.com/uk/en/himalayan-odyssey-2026/"},
            {"name": "ET TravelWorld / Saartaj", "url": "https://saartaj.com/royal-enfield-himalayan-base-camp-ladakh/"},
            {"name": "LinkedIn / Sanjay Sharma", "url": "https://www.linkedin.com/pulse/ultimate-himalayan-motorcycle-adventure-returns/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/sikkim-tourism-surge-2026/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": art2_image if art2_img_valid else None,
        "image_attribution": "Wikimedia Commons" if art2_img_valid else None,
        "is_editorial": False,
        "body": art2_body,
    },
]

# Remove None values
for art in articles:
    art = {k: v for k, v in art.items() if v is not None}

print("\nPublishing articles...")
for art in articles:
    # Strip None keys before posting
    clean = {k: v for k, v in art.items() if v is not None}
    try:
        sb_post("p2_articles", clean)
        print(f"✅ {clean['slug']}")
    except Exception as e:
        print(f"❌ {clean['slug']}: {e}")
