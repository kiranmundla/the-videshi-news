#!/usr/bin/env python3
"""Travel writer — 2026-06-11 14:00 UTC run. Two articles."""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# ── env ──────────────────────────────────────────────────────────────────
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
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


def compress_image(img_bytes, max_width=1200, quality=80):
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase storage. Return public URL."""
    print(f"  ↓ Downloading {img_url[:80]}...")
    r = requests.get(img_url, headers=UA, timeout=30)
    r.raise_for_status()
    raw = r.content
    print(f"  ↓ Downloaded {len(raw)} bytes, compressing...")
    compressed = compress_image(raw)
    print(f"  ↓ Compressed to {len(compressed)} bytes")

    # Upload
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    up_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    r2 = requests.post(up_url, headers=upload_headers, data=compressed, timeout=30)
    if r2.status_code not in (200, 201):
        # Try PUT instead
        r2 = requests.put(up_url, headers=upload_headers, data=compressed, timeout=30)
    r2.raise_for_status()

    public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  ✓ Uploaded → {public_url}")
    return public_url


# ═════════════════════════════════════════════════════════════════════════
#  ARTICLE 1: Europe Is the Smart NRI Summer Escape
# ═════════════════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_slug = make_slug("europe-summer-escape-nri-cheap-fares-world-cup")

art1_body = """While American highways clog with World Cup traffic and domestic airfares hit levels not seen since the post-pandemic revenge-travel surge, a quiet inversion is playing out across the Atlantic. For Indian Americans planning a summer getaway, Europe has become the unlikely bargain destination of 2026 — and the numbers are hard to argue with.

## The fare gap is staggering

Trans-Atlantic advance-purchase fares are down 15% year over year for mid-June departures, according to Deutsche Bank's analysis of the 500 busiest domestic and international routes. Raymond James analyst Savanthi Syth pegs the second-quarter decline even steeper — 17% below last year's levels on the lowest published fares.

Go the other direction and it's a different story entirely. United Airlines domestic fares have more than doubled. American Airlines prices are up 41%. JetBlue fares have climbed 30%. The culprits are familiar: jet fuel driven sky-high by the Iran conflict, the FIFA World Cup inflating prices across 16 host cities, and an airline industry trimming capacity to protect margins.

The math is simple. A round-trip from New York to London can now cost less than New York to Miami. Dallas to Paris has seen double-digit price drops. Atlanta to London Heathrow is following the same trend.

## Hotels are joining the party

It's not just flights. Trivago CEO Johannes Thomas told Barron's that room rates in several major European cities have dropped meaningfully — even as American demand surges. Madrid is down 15% to about €178 per night, with US demand up 24%. Florence has dropped 10% while demand has risen 39%. Venice rooms are 7% cheaper, Rome 5% lower. Americans are noticing the value and booking in volume.

Ryanair, Europe's dominant low-cost carrier, is keeping intra-Europe fares almost absurdly low. A London-to-Madrid flight in peak August currently costs $28. The airline is 80% hedged on fuel at just $67 per barrel through April 2027, insulating it from the same cost pressures that are crushing American carriers.

## Why NRIs should pay attention

For the 4.4 million Indian Americans in the US, Europe represents something US domestic travel cannot match right now: affordability paired with novelty. Many NRIs already hold valid Schengen visas from prior trips. Those who don't can apply — the savings on flights and hotels alone may justify the $80 application fee and the three-week processing time.

The practical advantages go further. A family of four flying JFK to Rome and spending a week in Florence and Venice could save $3,000–$4,000 compared to the same family driving to a World Cup host city, staying in inflated hotels, and paying $200-a-day rental car rates. Europe's rail networks — from Italy's Frecciarossa to France's TGV — eliminate the need for a car entirely.

There's also the cultural draw. NRI families seeking summer travel beyond the beach-resort circuit can explore London's thriving South Asian food scene, the centuries-old spice trading routes in Lisbon and Amsterdam, or the increasingly visible Indian diaspora communities in cities like Frankfurt and Milan.

## The window is narrow

The Europe fare advantage won't last indefinitely. If the Iran conflict de-escalates and oil prices drop, the trans-Atlantic capacity equation shifts. Airlines that hedged aggressively — like Ryanair — would maintain low fares, but the overall pricing gap between US domestic and trans-Atlantic travel would narrow.

For now, the arbitrage is real. CoStar has already downgraded its 2026 US outbound travel forecast, noting that more Americans are staying home — which means European destinations are absorbing demand without the overcrowding that plagued post-pandemic summers.

The smart money, and the smart NRI family, is booking across the Atlantic while the numbers still make sense."""

print(f"\n{'='*60}")
print(f"ARTICLE 1: Europe Summer Escape")
print(f"{'='*60}")

# Image: Venice Grand Canal at summer evening (Wikimedia Commons)
img1_url = "https://upload.wikimedia.org/wikipedia/commons/4/4d/The_Grand_Canal_at_summer_evening.jpg"
try:
    art1_img = upload_to_supabase(img1_url, f"{art1_id}.jpg")
except Exception as e:
    print(f"  ⚠ Image upload failed: {e}, using original URL")
    art1_img = img1_url

article1 = {
    "id": art1_id,
    "headline": "Europe Is the Smartest Summer Escape for NRIs — and the Fare Gap Proves It",
    "subheadline": "Trans-Atlantic fares are down 17% while US domestic prices have doubled. For Indian Americans squeezed by World Cup inflation, the continent across the pond has never looked cheaper.",
    "slug": art1_slug,
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Indian Americans with Schengen visas can save thousands compared to domestic US travel this summer. European cities offer lower hotel rates, cheap intra-Europe flights, and no World Cup price surges.",
    "tags": ["travel", "europe", "flights", "world-cup", "fares", "summer-travel"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Barron's", "url": "https://www.barrons.com/articles/summer-travel-airfares-delta-united-world-cup-a50bb050"},
        {"name": "Deutsche Bank Pricing Analysis", "url": "https://www.barrons.com/articles/summer-travel-airfares-delta-united-world-cup-a50bb050"},
        {"name": "Raymond James (Savanthi Syth)", "url": "https://www.barrons.com/articles/summer-travel-airfares-delta-united-world-cup-a50bb050"},
        {"name": "CNN Travel", "url": "https://www.cnn.com/2026/06/11/business/summer-travel-creative-saving/index.html"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art1_img,
    "image_caption": "Venice's Grand Canal at sunset — hotel rates in the city are down 7% this summer",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ═════════════════════════════════════════════════════════════════════════
#  ARTICLE 2: World Cup Hotel Bust — NRIs Should Look to Mexico and Canada
# ═════════════════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_slug = make_slug("world-cup-hotel-bust-nri-mexico-canada-cheaper")

art2_body = """The FIFA World Cup kicks off Thursday in North America, and the travel bonanza that US cities spent years preparing for is arriving with a whimper. Hotel bookings in American host cities are trailing their Canadian and Mexican counterparts, flight bookings from Europe are down, and industry executives are scrambling to explain why the world's biggest sporting event isn't filling rooms.

For NRIs who want to experience the tournament without emptying their savings, the data points to a clear playbook: cross the border.

## US hotels are in last place

According to CoStar, Vancouver and Guadalajara lead all World Cup host cities with 48% hotel occupancy rates ahead of the tournament. Toronto, Mexico City, and Monterrey are all above 40%. The only US city to crack that threshold is San Francisco, at 44%.

The Hotel Association of New York City has slashed its World Cup revenue forecast by 60%, from roughly $150 million to $60 million. CEO Vijay Dandapani called the outcome "overall a disappointment." FIFA had projected 1.2 million fans descending on the city for the July 19 final at MetLife Stadium. The hotel association now expects half that.

Flight bookings tell the same story. European arrivals into most US host cities are down 3.8% year over year, according to Cirium. Bookings from Europe into New York have plunged 15.8%. Visa concerns, the political climate, and stratospheric ticket prices — with resale seats for the final already topping $20,000 — have created what luxury travel executive Dave Guenther calls a market where "aspirational travelers were probably shut out."

## The Mexico and Canada advantage

The contrast is striking. Mexico's host cities — Guadalajara, Mexico City, and Monterrey — are pulling fans that the US is losing. The reasons are straightforward: lower hotel rates, cheaper food and transport, and a soccer culture that makes the atmosphere electric even outside the stadium.

For Indian Americans, Mexico holds an additional advantage that many don't realize. Indian passport holders with a valid US visa, green card, or permanent residency can enter Mexico without a separate Mexican visa. That means NRIs living anywhere in the US can fly to Guadalajara or Mexico City for a group-stage match, pay half what they'd spend in a US host city, and still catch the action.

Canada offers a similar value proposition. Toronto and Vancouver have strong Indian diaspora communities, direct Air Canada flights from most US hubs, and the kind of walkable transit infrastructure that makes getting to a stadium straightforward. Vancouver's SkyTrain runs directly to BC Place, the tournament venue. Toronto's hotel rates, while rising, remain well below New York or Miami levels for comparable dates.

## What the pricing looks like

The numbers make the case on their own. A standard hotel room near MetLife Stadium in East Rutherford during match weeks is running $350–$500 per night on major booking platforms. In Guadalajara's Zona Centro, comparable rooms are available for $80–$120. Mexico City's Roma and Condesa neighborhoods — walkable, safe, full of restaurants — hover around $100–$150.

Transportation compounds the gap. Gas prices in the US are above $4 per gallon. Rental cars in host cities are hitting $200 per day. Mexico City's metro costs 5 pesos per ride — about 25 cents. Guadalajara's bus system covers the city for under a dollar.

Match tickets are a separate equation, but group-stage games in Mexico are consistently priced 30–40% below their US equivalents on the secondary market, according to TicketData tracking.

## The practical guide for NRIs

For Indian Americans near the southern border — in Texas, Arizona, or California — Guadalajara and Monterrey are within a short flight. Spirit, Volaris, and VivaAerobus operate frequent routes from US border cities at fares that often dip below $100 one-way.

For those on the East Coast, Toronto is a three-hour drive from Buffalo and a one-hour flight from most Northeast airports. Mexico City is accessible via direct flights from JFK, LAX, SFO, Houston, and Dallas, often at fares lower than cross-country US domestic routes this summer.

The one caveat: travel insurance. NRIs should confirm their US health insurance covers them in Mexico or Canada, or purchase supplemental coverage. Most major credit cards include basic travel protection for international trips.

## The bottom line

The World Cup was supposed to be a windfall for American travel. Instead, it's become a case study in pricing people out of their own backyard. For NRIs who want the tournament experience without the financial hangover, Mexico and Canada aren't consolation prizes — they're the smarter ticket."""

print(f"\n{'='*60}")
print(f"ARTICLE 2: World Cup Hotel Bust")
print(f"{'='*60}")

# Image: MetLife Stadium (Wikimedia Commons)
img2_url = "https://upload.wikimedia.org/wikipedia/commons/d/d1/MetLife_Stadium%2C_East_Rutherford_New_Jersey.jpg"
try:
    art2_img = upload_to_supabase(img2_url, f"{art2_id}.jpg")
except Exception as e:
    print(f"  ⚠ Image upload failed: {e}, using original URL")
    art2_img = img2_url

article2 = {
    "id": art2_id,
    "headline": "The World Cup Was Supposed to Fill American Hotels — NRIs Are Finding Better Deals Across the Border",
    "subheadline": "US host city hotel bookings trail Mexico and Canada by double digits. For Indian Americans with valid US visas, Guadalajara and Toronto offer the same tournament at half the price.",
    "slug": art2_slug,
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Indian passport holders with valid US visas can enter Mexico visa-free. With US World Cup hotels at $350-500/night and Mexican host cities at $80-150, NRIs have a clear arbitrage opportunity — and Canada's diaspora infrastructure makes Toronto an easy alternative.",
    "tags": ["travel", "world-cup", "fifa-2026", "mexico", "canada", "hotels", "nri-travel"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/sports/soccer/pricey-world-cup-keeps-fans-away-hits-us-hotels-airlines-2026-06-11/"},
        {"name": "The Wall Street Journal / The Times", "url": "https://www.thetimes.com/business-money/companies/article/america-is-already-losing-the-world-cup-for-hotel-bookings-hbz6hv0cq"},
        {"name": "Front Office Sports", "url": "https://frontofficesports.com/world-cup-fans-face-significant-sticker-shock-for-hotels/"},
        {"name": "CoStar Hotel Data", "url": "https://www.thetimes.com/business-money/companies/article/america-is-already-losing-the-world-cup-for-hotel-bookings-hbz6hv0cq"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art2_img,
    "image_caption": "MetLife Stadium in East Rutherford, New Jersey — host of the FIFA World Cup 2026 final on July 19",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}


# ═════════════════════════════════════════════════════════════════════════
#  INSERT ARTICLES
# ═════════════════════════════════════════════════════════════════════════

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone — {len(articles)} articles submitted for review.")
