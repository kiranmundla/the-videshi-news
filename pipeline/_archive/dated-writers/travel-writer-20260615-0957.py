#!/usr/bin/env python3
"""The Videshi — Travel writer run 2026-06-15 09:57 UTC.
Three fresh, distinct travel articles for the Indian diaspora:
  1. Europe airfares falling while the rest of the world surges
  2. US National Parks 2026 — reservation rollbacks + nonresident surcharge
  3. Mexico visa-free for US-visa holders — NRI side trips
Sources images via Wikipedia/Commons/Pexels, compresses, re-uploads to Supabase.
"""
import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
import urllib.parse

# ---------------- Env ----------------
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())
pexels_file = Path.home() / "workspace" / ".env.pexels"
for line in pexels_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

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

# ---------------- Image sourcing ----------------
def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def fetch_commons(search_query, limit=6):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers=UA, timeout=20)
        if r.status_code != 200:
            return []
        pages = r.json().get("query", {}).get("pages", {})
        out = []
        for _, page in pages.items():
            ii = page.get("imageinfo", [{}])[0]
            mime = ii.get("mime", "")
            if not mime.startswith("image/") or mime == "image/svg+xml":
                continue
            if ii.get("width", 0) < 600:
                continue
            url = ii.get("thumburl") or ii.get("url", "")
            if url:
                out.append({"url": url, "title": page.get("title", ""), "w": ii.get("width", 0)})
        return out
    except Exception as e:
        print(f"  ! Commons error: {e}")
        return []

def fetch_pexels(query, per_page=6):
    if not PEXELS_KEY:
        return []
    try:
        r = requests.get(f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page={per_page}&orientation=landscape",
                         headers={"Authorization": PEXELS_KEY}, timeout=20)
        if r.status_code != 200:
            print(f"  ! Pexels {r.status_code}")
            return []
        photos = r.json().get("photos", [])
        return [{"url": p["src"]["large2x"], "alt": p.get("alt", ""), "photographer": p.get("photographer", "")} for p in photos]
    except Exception as e:
        print(f"  ! Pexels error: {e}")
        return []

def download(url):
    try:
        r = requests.get(url, headers=UA, timeout=30)
        if r.status_code == 200 and len(r.content) > 5000:
            ct = r.headers.get("Content-Type", "")
            if ct.startswith("image/") or url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                return r.content
    except Exception as e:
        print(f"  ! download error: {e}")
    return None

def upload_supabase(img_bytes, filename):
    up_headers = {
        "apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg", "x-upsert": "true",
    }
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    r = requests.post(url, headers=up_headers, data=img_bytes, timeout=60)
    if r.status_code in (200, 201):
        return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  ! Supabase upload {r.status_code}: {r.text[:200]}")
    return None

def source_image(slug, commons_queries, pexels_queries):
    """Try Commons queries first, then Pexels. Returns (url, attribution)."""
    candidates = []
    for q in commons_queries:
        for c in fetch_commons(q):
            candidates.append((c["url"], "Wikimedia Commons"))
        if candidates:
            break
    if not candidates:
        for q in pexels_queries:
            for c in fetch_pexels(q):
                candidates.append((c["url"], "Pexels"))
            if candidates:
                break
    for url, attribution in candidates:
        raw = download(url)
        if not raw:
            continue
        try:
            comp = compress_image(raw)
        except Exception as e:
            print(f"  ! compress fail: {e}")
            continue
        if len(comp) < 10000:
            continue
        final = upload_supabase(comp, f"{slug}.jpg")
        if final:
            print(f"  ✓ image ({attribution}, {len(comp)//1024}KB): {final}")
            return final, attribution
    print(f"  ! No image sourced for {slug}")
    return None, None

# ---------------- Article bodies ----------------
BODY_EUROPE = """For the legions of Indian Americans who spend each summer agonizing over the cost of a trip home, this year's airfare math has been brutal. A round-trip economy seat from the West Coast to Delhi or Bengaluru is routinely clearing $1,500, and premium cabins have crossed $8,000. But amid the gloom, one corner of the map has quietly gone the other way: Europe is getting cheaper, and it is reshaping how savvy diaspora families are planning their travel.

## The numbers behind the dip

Trans-Atlantic advance-purchase fares were down roughly 15% year over year for mid-June departures, according to Deutsche Bank's pricing analysis of the 500 busiest routes. Across the second quarter, U.S.–Europe fares are down about 17% on the previous year, per Raymond James, with the steepest declines on flights to London Heathrow and Paris from Dallas, New York, and Atlanta. Mexico was the only other region to see fares fall.

The contrast with domestic travel is stark. United Airlines' average domestic fares more than doubled year over year, American's rose 41%, and JetBlue's climbed 30%. The culprits are a familiar trio: jet-fuel prices pushed up by the Iran conflict, capacity discipline from carriers wary of overbuilding, and a summer of marquee events — the FIFA World Cup and the America 250 celebrations — soaking up domestic demand.

## Why Europe, and why now

Europe's softness is partly a supply story. Carriers added significant trans-Atlantic capacity for 2026, and with the dollar holding reasonably firm against the euro and pound, the discounting has flowed straight to leisure travelers booking three weeks out. Premium demand on long-haul international routes "continues to be the driving force," analysts note, which means the deepest discounts are concentrated in economy — exactly where most family travelers sit.

## The NRI angle: Europe as a layover, not just a destination

For Indian Americans, the cheaper-Europe story is more than a vacation tip. It changes the calculus of the trip home. A growing number of diaspora travelers route through Europe deliberately — flying a U.S.–Europe leg on a cheap trans-Atlantic fare, spending a few days in London, Frankfurt, or Rome, then continuing to India on a separate ticket. With the U.S.–Europe segment down 15-17%, that split-ticket strategy is suddenly competitive with a straight one-stop fare through the Gulf.

It helps that Indian passport holders now enjoy easier access to the Schengen zone. Under the EU's 2024 "cascade" rules for Indian nationals, travelers who have lawfully used two Schengen visas in the prior three years can be issued a two-year multiple-entry visa, typically followed by a five-year one. That makes a European stopover far less of a paperwork ordeal than it once was — though travelers should budget extra time for the new Entry/Exit System biometric checks now rolling out at EU borders.

## How to play it

A few practical moves for diaspora families eyeing the window:

- **Book the trans-Atlantic leg early.** The discounts are concentrated in 21-day advance fares; last-minute Europe seats are not cheap.
- **Consider an open-jaw home trip.** Fly into one European hub, out of another, and stitch the India segment separately — the fare savings can fund the stopover.
- **Mind the passport rules.** EU border officers are enforcing the requirement that passports be no more than 10 years old and valid for at least three months beyond departure. A perfectly unexpired passport can still trigger a denied boarding.
- **Watch the hurricane caveat on Mexico.** The other region with falling fares overlaps with Atlantic hurricane season, so flexible tickets are worth the premium.

The broader lesson is that 2026 is a year of dislocation in air travel, and dislocation creates openings. For a community that flies internationally more than almost any other in America, the families paying attention to where fares are falling — not just where they are rising — will be the ones who still get their summer abroad without emptying the savings account.

## What's next

Analysts expect the trans-Atlantic softness to persist through at least early summer, with two consecutive weeks of falling advance fares already on the board. Whether it survives into the autumn shoulder season depends on fuel prices and whether carriers blink on the capacity they added. For now, the message to diaspora travelers is simple: if Europe was ever on the itinerary, this is the cheapest it has looked in years."""

BODY_PARKS = """Every summer, Indian American families pack the minivan for the great American road trip — and increasingly, the destination is a national park. Yosemite's granite walls, the red rock of Utah, the geysers of Yellowstone: for first-generation families showing relatives visiting from India the scale of the country, the parks are the headline act. This year, the rules for getting in have changed in ways that cut both ways.

## The reservation whiplash

For three summers, the most-visited parks fought overcrowding with timed-entry reservation systems — book a two-hour entry window online or be turned away at the gate. For 2026, several of the biggest names have reversed course. Yosemite has dropped entrance reservations entirely. Glacier ended its park-wide vehicle reservations (though it kept controls on the popular Logan Pass corridor). Arches in Utah scrapped timed entry, and Mount Rainier in Washington followed suit.

That is good news for spontaneity — you can now drive into Yosemite Valley without a months-ahead booking. But it is not universal. Rocky Mountain National Park, which drew over 4 million visitors last year, reinstated its timed-entry system beginning May 22, running through mid-October. Two permit types are sold through Recreation.gov for a $2 processing fee: one covering the Bear Lake Road corridor, one for the rest of the park. Families heading to Colorado still need to plan around the calendar, not the gate.

## The cost shock for international visitors

The more consequential change for the diaspora is about money — and who counts as a local. As part of an "America-first pricing" overhaul introduced by the Department of the Interior, nonresidents now face an additional **$100 surcharge** at some of the most heavily trafficked parks, and a nonresident annual parks pass now costs **$250**. U.S. residents pay the same as before.

For Indian American families, the dividing line is residency, not citizenship or ancestry. A green-card holder or U.S. citizen pays the resident rate. But the parents or in-laws visiting from Hyderabad on a B-2 tourist visa — the relatives these trips are often built around — may be charged the nonresident surcharge. A family of four that includes two visiting grandparents could see the entrance bill climb by $200 at a flagship park.

## The free-day calendar also shifted

The Interior Department reshuffled which days the parks waive entrance fees. Martin Luther King Jr. Day and Juneteenth were removed from the fee-free list. Added in their place: the National Park Service's 110th anniversary, Constitution Day, and Theodore Roosevelt's birthday. The department also designated Flag Day as a fee-free day this year. The upshot: families who used to anchor a long-weekend trip to Juneteenth will now pay full price on June 19, while a handful of new dates open up later in the year.

## The NRI angle

Indian Americans are among the most enthusiastic national-park visitors in the country, and the parks have become a fixture of the visiting-relatives itinerary — a way to show India-based family the country's natural grandeur. The 2026 changes mean two things for that ritual. First, the marquee parks are easier to enter on short notice than they have been in years, which suits families coordinating around a relative's visa-limited visit. Second, the trip is now meaningfully more expensive when those relatives are nonresidents, and the surcharge is steep enough to factor into the budget.

## How to plan around it

- **Check each park individually.** There is no single 2026 rulebook. Rocky Mountain requires reservations; Yosemite, Glacier, Arches, and Mount Rainier largely do not.
- **Budget the surcharge for visiting family.** If grandparents are on tourist visas, assume the $100 nonresident fee at flagship parks and price it in.
- **Time it to a fee-free day where you can.** The new patriotic free days — including Constitution Day in September — can save a family the entrance fee entirely.
- **Book lodging early regardless.** Dropping entry reservations does not add hotel rooms or campsites; in-park lodging still sells out months ahead.

## What's next

The Park Service says it will use "targeted tools only where necessary," leaving the door open to reinstating reservations mid-season if a park hits capacity. And the nonresident pricing — framed by the Interior Department as making international visitors "contribute their fair share" — is likely to expand to more parks in coming years. For diaspora families who treat the parks as a summer institution, 2026 is the year to read the fine print before loading the car."""

BODY_MEXICO = """As the FIFA World Cup draws millions of fans to North America this summer, a quieter travel perk is catching on among Indian Americans: the ease of slipping down to Mexico. For NRIs who already hold a U.S. visa or green card, Mexico is effectively visa-free — and that single fact is turning Cancún, Los Cabos, and Mexico City into the diaspora's favorite long-weekend escape.

## The rule that makes it work

Mexico's immigration policy is unusually generous to anyone holding strong travel documents. Citizens of more than 65 countries can enter visa-free for up to 180 days. Crucially for Indian passport holders — who normally need a visa for Mexico — there is a separate exemption: travelers holding a valid visa or permanent residency from the **United States, Canada, Japan, the United Kingdom, or the Schengen Area** may enter Mexico without applying for a separate Mexican tourist visa.

For the roughly 5 million people of Indian origin in the United States, most of whom hold either a U.S. visa or a green card, that means Mexico is open with nothing more than the documents already in their wallet. No consulate appointment, no separate application fee, no weeks of waiting. An Indian citizen on an H-1B, an F-1 student, or an L-1 transfer can book a Cancún flight and go.

## Why it matters more this year

The World Cup has put a spotlight on cross-border travel between the three host nations, and Mexico has leaned into it. The country's Viajero Confiable program offers automated kiosks and expedited immigration lanes at major airports, smoothing arrivals during what is expected to be a crushingly busy summer. For fans planning multi-country itineraries — a match in the U.S., another in Mexico — the visa exemption removes the single biggest friction point.

But the appeal extends well beyond football. Mexico is one of the few destinations where airfares are actually falling this year; it was the only region besides Europe to see trans-Atlantic-style fare declines, down about 1.9% year over year, even as domestic U.S. fares surged. A beach break in Tulum or Los Cabos has rarely been a more rational alternative to an expensive domestic trip.

## The practical fine print

The exemption is real but not automatic, and a few details trip people up:

- **The visa must be valid.** An expired U.S. visa does not qualify, even if you remain in lawful status on an unexpired I-797 approval. Carry the physical visa stamp or your green card.
- **Carry your documents.** Mexican airlines verify the U.S. or Schengen visa at check-in before boarding. Travelers without proof have been denied boarding even when technically eligible.
- **Mind the FMM.** Travelers outside the exemption need a Forma Migratoria Múltiple tourist permit, available on arrival or online — but exempt travelers generally do not.
- **Watch the hurricane calendar.** Mexico's cheaper summer fares coincide with the active Atlantic hurricane season, so flexible or refundable bookings are worth the small premium, especially for the Caribbean coast.
- **Plan the U.S. re-entry.** The bigger logistical question for many NRIs is not getting into Mexico but getting back into the United States. Make sure your U.S. visa permits re-entry and, if on a status like H-1B with an expired stamp, understand the risks before leaving.

## The NRI angle

For the diaspora, Mexico fills a specific niche: an international getaway that feels genuinely abroad — different language, food, culture — without the visa paperwork that shadows so much of an Indian passport holder's travel life. Families use it for spring-break beach trips, couples for quick anniversary escapes, and increasingly, groups of friends for World Cup side trips. In a year when the cost and hassle of travel have climbed almost everywhere, Mexico's open door to U.S.-visa holders is one of the few things that got easier.

## What's next

Mexico has shown no sign of tightening the exemption, and the World Cup is likely to cement its status as the diaspora's default warm-weather escape. The smart move for NRIs is to treat Mexico the way they would a domestic trip — bookable on short notice, with the only real homework being a careful check that their U.S. documents are current and permit a smooth return."""

# ---------------- Articles ----------------
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Europe Is the One Place Getting Cheaper to Fly This Summer — and NRIs Should Take Note",
        "subheadline": "Trans-Atlantic fares are down 15-17% as domestic and India routes surge, opening a savvy split-ticket route home for diaspora families.",
        "slug": make_slug("europe-cheaper-airfares-summer-nri-split-ticket-india"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "With U.S.–Europe fares down 15-17% while India and domestic routes surge, Indian American families can route home through a cheap European stopover — made easier by the EU's multi-year Schengen visa for Indians.",
        "tags": ["travel", "airlines", "airfares", "europe", "schengen"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Barron's — The One Summer Vacation Destination Getting Cheaper", "url": "https://www.barrons.com/articles/cheap-summer-vacation-europe-airfare"},
            {"name": "EEAS — EU adopts more favourable Schengen visa rules for Indians", "url": "https://www.eeas.europa.eu/delegations/india/european-union-adopts-more-favourable-schengen-visa-rules-indians_en"},
            {"name": "Travel And Tour World — Global airfare shockwave summer 2026", "url": "https://www.travelandtourworld.com/news/article/global-airfare-shockwave-summer-2026/"},
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_caption": "A wide-body jet on approach against a clear summer sky.",
        "body": BODY_EUROPE,
        "_commons": ["airliner approach landing", "wide body aircraft airport"],
        "_pexels": ["airplane landing runway sky", "airplane wing sky travel"],
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America's National Parks Just Rewrote the Rules for Summer 2026 — Here's What NRI Families Need to Know",
        "subheadline": "Yosemite and Glacier drop entry reservations while a new $100 nonresident surcharge hits visiting relatives at flagship parks.",
        "slug": make_slug("us-national-parks-2026-rules-nonresident-surcharge-nri"),
        "category": "travel",
        "vertical": "diaspora-travel",
        "diaspora_angle": "Flagship parks are easier to enter on short notice this year, suiting families coordinating around a relative's visa-limited visit — but visiting parents on tourist visas now face a $100 nonresident surcharge that can add $200 to a family trip.",
        "tags": ["travel", "national parks", "usa", "road trip", "fees"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NPS — Park Service Expands Access for Summer 2026", "url": "https://www.nps.gov/orgs/1207/summer-2026-access.htm"},
            {"name": "The Points Guy — National park reservation requirements changing in 2026", "url": "https://thepointsguy.com/news/national-park-reservations-2026/"},
            {"name": "The Sun — National parks holiday calendar and fee change", "url": "https://www.the-sun.com/travel/national-parks-fee-free-days-2026/"},
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_caption": "A scenic vista in a U.S. national park during peak summer season.",
        "body": BODY_PARKS,
        "_commons": ["Yosemite Valley tunnel view", "Glacier National Park landscape"],
        "_pexels": ["yosemite national park valley", "national park mountain landscape usa"],
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Mexico Is Open to NRIs Without a Visa — and It's Becoming the Diaspora's Favorite Escape",
        "subheadline": "Indian passport holders with a valid U.S. visa or green card can skip Mexico's tourist visa entirely, just as World Cup fever and falling fares converge.",
        "slug": make_slug("mexico-visa-free-us-visa-holders-nri-cancun-world-cup"),
        "category": "travel",
        "vertical": "diaspora-travel",
        "diaspora_angle": "Indian citizens holding a valid U.S. visa or green card can enter Mexico without a separate tourist visa, turning Cancún and Los Cabos into a paperwork-free getaway for the 5 million-strong U.S. diaspora.",
        "tags": ["travel", "mexico", "visa", "world cup", "beach"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World — World Cup 2026 entry requirements and Mexico visa flexibility", "url": "https://www.travelandtourworld.com/news/article/expert-guide-official-entry-requirements-2026-world-cup/"},
            {"name": "Barron's — Mexico among regions where fares are falling", "url": "https://www.barrons.com/articles/cheap-summer-vacation-europe-airfare"},
            {"name": "Travel And Tour World — Mexico broad visa flexibility for international travelers", "url": "https://www.travelandtourworld.com/news/article/usa-canada-mexico-world-cup-2026-entry-rules/"},
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_caption": "The turquoise Caribbean coastline at a beach resort in Mexico.",
        "body": BODY_MEXICO,
        "_commons": ["Cancun beach Mexico", "Tulum beach Caribbean Mexico"],
        "_pexels": ["cancun mexico beach resort turquoise", "mexico caribbean beach palm"],
    },
]

# ---------------- Run ----------------
inserted = []
for art in articles:
    commons_q = art.pop("_commons")
    pexels_q = art.pop("_pexels")
    print(f"\n=== {art['slug']} ===")
    img_url, attribution = source_image(art["slug"], commons_q, pexels_q)
    if img_url:
        art["image_url"] = img_url
        art["image_attribution"] = attribution
    else:
        # No image > wrong image — leave image fields unset
        art["image_caption"] = None
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  (image={'yes' if img_url else 'NONE'})")
        inserted.append(art["headline"])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\n========== SUMMARY ==========")
print(f"Inserted {len(inserted)} / {len(articles)} articles:")
for h in inserted:
    print(f"  - {h}")
