#!/usr/bin/env python3
"""NRI World Writer — 2026-06-09 12:00 UTC run
Publishes 2 articles to p2_articles with status='review'.
"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Supabase credentials ─────────────────────────────────────────────
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


# ── Image helpers ─────────────────────────────────────────────────────

def download_and_compress(url, max_width=1200, quality=80):
    """Download image, compress to JPEG, return bytes."""
    from PIL import Image
    r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_bytes, filename):
    """Upload compressed JPEG to Supabase article-images bucket."""
    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(upload_url, headers=upload_headers, data=img_bytes, timeout=30)
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"


# ── ARTICLE 1 ─────────────────────────────────────────────────────────
# Indian Restaurant Congress & Awards Debuts in London

art1_id = str(uuid.uuid4())
art1_slug = make_slug("indian-restaurant-congress-london-sanjeev-kapoor-global-awards")

art1_body = """Indian cuisine has long punched above its weight in Britain's dining scene. Now, for the first time, the industry has a global platform to match its ambitions.

On 28 May, more than 250 restaurateurs, Michelin-starred chefs, and hospitality executives gathered at the Royal Lancaster London for the inaugural global edition of the Indian Restaurant Congress & Awards — an event that, after fifteen years as an India-only affair, chose London as the launchpad for its international expansion.

The choice of city was deliberate. Britain is home to an estimated 12,000 Indian restaurants — the highest concentration outside the subcontinent — and has produced some of the world's most celebrated Indian chefs. The congress sought to bring those chefs, and their counterparts from India and the Gulf, into the same room.

## From Curry Houses to Culinary Empire

The conference sessions tackled subjects that would have been unthinkable a generation ago, when "Indian restaurant" was shorthand for a high-street curry house. Panels addressed scaling culinary brands across borders, adapting menus to local palates without sacrificing authenticity, integrating technology into restaurant operations, and attracting investment capital for cross-border expansion.

The speakers read like a who's-who of Indian gastronomy in Britain: two-time Michelin-starred chef Atul Kochhar, Cinnamon Collection's Vivek Singh, Café Spice Namasté's Cyrus Todiwala OBE, Benares' Sameer Taneja, and the MBE-holding author-chef Romy Gill. Alongside them sat Dipna Anand of Brilliant Gastro in Southall and Peter Joseph of Kahani London — chefs whose work bridges haute cuisine and community roots.

## The Winners

The evening's awards ceremony, judged by a panel that included former BBC journalist George Shaw, food critic Andy Hayler, and TV host Rashmi Uday Singh, crowned the following:

- **Global Indian Chef of the Year**: Sanjeev Kapoor
- **Culinary Excellence Award**: Atul Kochhar
- **Global Ambassador of Indian Cuisine**: Shipra Khanna
- **Global Indian Restaurant of the Year**: The Cinnamon Club / Cinnamon Collection
- **Best Fine Dining Indian Restaurant**: Kahani
- **Best Chef-Led Restaurant**: Benares Restaurant & Bar
- **Best Indian Restaurant Brand**: Jamavar
- **Best Indian Restaurant — UK**: Colonel Saab
- **Restaurant Group of the Year**: Tresind
- **Regional Cuisine Champion**: Dev Biswal, The Cook's Tale (Canterbury), for Odisha cooking

Biswal's award was particularly telling. "Odisha has one of the oldest and richest culinary traditions in the world, yet very few people in the UK have had the opportunity to experience it," he said. "To receive national recognition for championing regional Indian cuisine is both humbling and deeply rewarding."

## Two Industry Launches

The congress also unveiled two new trade initiatives. *Entrepreneur's Restaurateur Global Issue*, a print and digital magazine profiling hospitality leaders and growth strategies, made its debut alongside **RestaurantIndia.uk**, a business-to-business platform designed to serve the UK's Indian restaurant sector with market intelligence, supplier networks, and industry analysis.

"The global edition of the Indian Restaurant Congress & Awards marked an important milestone," said Sachin Marya, managing director of Franchise India, the organiser. "The response from restaurateurs, chefs, entrepreneurs, partners and industry stakeholders has been truly overwhelming."

## What It Means for the Diaspora

For the 1.8 million people of Indian origin living in Britain, the congress represents something broader than business networking. Indian restaurants in the UK employ an estimated 100,000 people and contribute billions to the economy. The sector's professionalisation — from Michelin stars to global trade platforms — reflects the community's transition from survival-mode immigrant enterprise to confident cultural export.

The event was attended by prominent community figures including Lord Rami Ranger, Lord Kulveer Ranger, and Councillor Aarien Areti, the Deputy Mayor of the Royal Borough of Kensington and Chelsea — a sign that the political establishment, too, recognises where the industry is heading.

Whether the congress returns annually to London or rotates to other diaspora capitals remains to be seen. What is already clear is that Indian cuisine's global story has outgrown the curry-house narrative. It now has a congress to prove it."""

# Image: Sanjeev Kapoor from Wikipedia
# Image: Sanjeev Kapoor from Wikipedia (already uploaded in prior run)
art1_img_url = upload_to_supabase(
    download_and_compress("https://upload.wikimedia.org/wikipedia/commons/e/ea/Sanjeev_kapoor_at_the_Launch_of_new_restaurant_%27Arola%27_at_J_W_Marriott.jpg"),
    f"{art1_id}.jpg"
) if True else None  # always re-upload since new UUID
print(f"  ✅ Art1 image ready")

art1 = {
    "id": art1_id,
    "headline": "Indian Cuisine Got Its Own Davos in London. Sanjeev Kapoor Walked Away With the Top Prize.",
    "subheadline": "The inaugural global Indian Restaurant Congress & Awards brought 250 chefs, restaurateurs, and hospitality executives to the Royal Lancaster London — and launched a new industry platform for the UK's 12,000 Indian restaurants.",
    "slug": art1_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Britain's Indian restaurant sector employs 100,000 people and represents the diaspora's transition from immigrant enterprise to global culinary export. The congress, backed by Lords and MPs, formalises what NRI chefs have built over decades.",
    "tags": ["nri", "diaspora", "uk", "food", "restaurants", "awards", "london"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Restaurant India", "url": "https://restaurantindia.in/news/indian-restaurant-congress-awards-debuts-in-london.html"},
        {"name": "Mosaic Digest", "url": "https://mosaicdigest.com/indian-restaurant-industry-takes-global-stage-at-london-congress/"},
        {"name": "Taste Asia UK", "url": "https://tasteasia.co.uk/indian-cuisine-london-global-restaurant-leaders/"},
        {"name": "World News TV", "url": "https://wntv.co.uk/dev-biswal-regional-indian-cuisine-champion-chef-award-odisha/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art1_img_url,
    "image_caption": "Sanjeev Kapoor, named Global Indian Chef of the Year at the inaugural London congress",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ── ARTICLE 2 ─────────────────────────────────────────────────────────
# Seven Indian Workers Killed in Dubai Bus Crash

art2_id = str(uuid.uuid4())
art2_slug = make_slug("seven-indian-workers-killed-dubai-emirates-road-bus-crash")

art2_body = """Seven Indian workers were killed and nine others injured on Monday when a minibus carrying labourers slammed into the back of a stationary truck on Emirates Road in Dubai — the latest in a grim pattern of road fatalities among blue-collar Indian migrants in the Gulf.

The Indian Consulate in Dubai confirmed the deaths within hours. "Deeply saddened by the tragic road accident in Dubai that claimed the lives of several Indian workers," it wrote on X. "Our officials visited the hospital, met the injured Indians, and are working closely with local authorities to provide all possible assistance and support."

## What Happened

According to Brigadier Juma Salem bin Suwaidan, Director of the General Department of Traffic at Dubai Police, the truck had come to a sudden halt in the middle of Emirates Road — one of the emirate's busiest arteries — after suffering a technical malfunction. The minibus driver, allegedly failing to maintain a safe following distance, rear-ended the truck at speed.

Of the nine injured, five were in serious condition and four sustained moderate injuries. All were rushed to hospital. Authorities have not released the victims' identities pending notification of families in India.

Traffic accident investigators were dispatched to the scene to gather evidence. Police work crews cleared the wreckage and restored traffic flow, but the force also issued a pointed warning to drivers about the dangers of stopping in the middle of a highway — and about the obligation to ensure vehicles are mechanically sound before taking to the road.

## A Recurring Tragedy

The accident underscores an uncomfortable reality for the estimated 3.5 million Indian nationals living in the UAE, most of them workers in construction, logistics, and services. Road accidents remain one of the leading causes of accidental death among Indian migrants in the Gulf. Worker transport — typically by minibus or company van — is a recurring factor: vehicles are often crowded, routes traverse high-speed highways, and drivers face punishing schedules.

India's Ministry of External Affairs has not yet issued a statement on the latest crash. The Consulate in Dubai, which serves as the first point of contact for grieving families, said it was coordinating repatriation of remains and providing hospital liaison.

## The Broader Picture

India receives more remittances from the UAE than from any country except the United States — roughly $15 billion annually, according to Reserve Bank of India data. The workers who generate those flows occupy some of the most physically demanding and dangerous jobs in the Gulf economy. When they die abroad, their families in Kerala, Uttar Pradesh, Rajasthan, and Bihar are often left navigating an opaque process of death certificates, embassy paperwork, and airline policies to bring their loved ones home.

Diaspora advocacy groups have repeatedly called for stronger worker protection frameworks in bilateral agreements between India and Gulf states. The crash on Emirates Road will likely renew those demands — though past incidents suggest the policy response tends to be slow, incremental, and overshadowed by the next news cycle.

For the families of the seven who did not come home on Monday, that cycle offers no comfort."""

# Image: Dubai highway from Pexels (Wikimedia 429'd)
art2_source_img = "https://images.pexels.com/photos/5075798/pexels-photo-5075798.jpeg?auto=compress&cs=tinysrgb&w=1200"
print("⏳ Downloading & compressing Article 2 image (Dubai highway)...")
import time
time.sleep(2)  # brief pause after prior request
art2_img_bytes = download_and_compress(art2_source_img)
art2_img_url = upload_to_supabase(art2_img_bytes, f"{art2_id}.jpg")
print(f"  ✅ Uploaded: {len(art2_img_bytes)//1024} KB → {art2_img_url[:80]}...")

art2 = {
    "id": art2_id,
    "headline": "Seven Indian Workers Died on a Dubai Highway on Monday. Their Families Are Now Navigating the Hardest Part.",
    "subheadline": "A minibus carrying labourers rear-ended a broken-down truck on Emirates Road, killing seven and injuring nine. The Indian Consulate confirmed it is coordinating hospital visits and repatriation.",
    "slug": art2_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "India receives roughly $15 billion in remittances from the UAE annually, generated overwhelmingly by blue-collar workers in dangerous transport and construction jobs. When they die abroad, families face a labyrinth of embassy paperwork, airline policies, and grief — a burden that falls disproportionately on India's poorest states.",
    "tags": ["nri", "diaspora", "dubai", "uae", "gulf", "workers", "road-accident", "safety"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "IANS", "url": "https://ianslive.in/news/7-indians-killed-9-injured-in-dubai-road-accident-20260608200024/"},
        {"name": "Madhyamam Online", "url": "https://madhyamamonline.com/en/world/middle-east/several-indian-workers-among-7-killed-in-dubai-road-accident-1230932"},
        {"name": "Indian News Network", "url": "https://indianewsnetwork.com/seven-indian-workers-die-in-dubai-road-accident/"},
        {"name": "Indian Witness", "url": "https://indianwitness.com/seven-killed-nine-injured-in-dubai-bus-crash-involving-indian-workers/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art2_img_url,
    "image_caption": "Dubai's highway skyline — Emirates Road, where the collision occurred, is one of the emirate's busiest arterial routes",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ── Insert articles ───────────────────────────────────────────────────

articles = [art1, art2]
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
