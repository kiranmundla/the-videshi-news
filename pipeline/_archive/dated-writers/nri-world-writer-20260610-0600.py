#!/usr/bin/env python3
"""NRI World Writer — 2026-06-10 06:00 UTC run"""

import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path

# ── Env ──────────────────────────────────────────────────────────────────────
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

pexels_env = Path.home() / "workspace/.env.pexels"
for line in pexels_env.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
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

def upload_to_supabase(img_bytes, filename, bucket="article-images"):
    """Upload image bytes to Supabase storage, return public URL."""
    up_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(
        f"{SB_URL}/storage/v1/object/{bucket}/{filename}",
        headers=up_headers,
        data=img_bytes,
        timeout=30,
    )
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/{bucket}/{filename}"

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image to JPEG."""
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

def download_image(url):
    """Download image bytes from URL."""
    r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
    r.raise_for_status()
    return r.content

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Image Sourcing ──────────────────────────────────────────────────────────

# Article 1: Indian food going mainstream — use Pexels food spread
print("Sourcing images...")

img1_url_pexels = "https://images.pexels.com/photos/17050759/pexels-photo-17050759.jpeg?auto=compress&cs=tinysrgb&w=1200"
img1_bytes = download_image(img1_url_pexels)
img1_compressed = compress_image(img1_bytes)
slug1 = "indian-food-mainstream-america-farzi-dabba-rasa-20260610"
img1_final = upload_to_supabase(img1_compressed, f"{slug1}.jpg")
print(f"  ✅ Article 1 image: {len(img1_compressed)} bytes → {img1_final[:60]}...")

# Article 2: India Census 2027 — use Wikimedia Commons (Modi self-enumeration)
# Original URL (thumbnail endpoint can rate-limit; fall back to full image + local compress)
img2_path = Path("/tmp/census2027_full.jpg")
if img2_path.exists() and img2_path.stat().st_size > 10000:
    img2_bytes = img2_path.read_bytes()
else:
    img2_url_commons = "https://upload.wikimedia.org/wikipedia/commons/c/c0/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_fills_out_the_self-enumeration_for_Census_2027.jpg"
    img2_bytes = download_image(img2_url_commons)
img2_compressed = compress_image(img2_bytes)
slug2 = "india-census-2027-caste-enumeration-delimitation-nri-20260610"
img2_final = upload_to_supabase(img2_compressed, f"{slug2}.jpg")
print(f"  ✅ Article 2 image: {len(img2_compressed)} bytes → {img2_final[:60]}...")


# ── Articles ─────────────────────────────────────────────────────────────────

articles = [
    # ── ARTICLE 1: Indian Food Going Mainstream in America ──────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "From Bellevue to Brooklyn, Indian Restaurants Are Opening at a Pace America Has Never Seen",
        "subheadline": "A Michelin-recognised bistro chain, a $2-billion food-hall empire, and a trio of childhood friends with a DC fast-casual — the race to make Indian food mainstream in America is suddenly very crowded.",
        "slug": slug1,
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Indian diaspora built the customer base, the talent pipeline, and the cultural familiarity that now allows Indian cuisine to scale in mainstream American food culture — from fine dining to fast-casual to ghost kitchens.",
        "tags": ["nri", "diaspora", "indian-food", "restaurants", "farzi-cafe", "wonder", "rasa", "dishoom"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com"},
            {"name": "Restaurant Business Online", "url": "https://restaurantbusinessonline.com"},
            {"name": "WPST / Townsquare Media", "url": "https://wpst.com"},
            {"name": "Dining and Cooking", "url": "https://diningandcooking.com"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img1_final,
        "image_caption": "An assortment of Indian dishes including curries, naan, and biryani — the kind of spread Americans are increasingly seeking out",
        "image_attribution": "Pexels",
        "body": """Something is happening to Indian food in America, and it is happening fast.

In Bellevue, Washington, Farzi Café has just opened its first US outlet inside the city's upscale shopping square — a gleaming, cocktail-forward bistro where molecular gastronomy meets grandmother's recipes. The man behind it, Zorawar Kalra, runs more than two dozen restaurants across 11 countries. His London outpost sits in the Michelin Guide. His late father, Jiggs Kalra, was known in India as the "czar of Indian cuisine." Now the younger Kalra wants to take Indian food coast to coast across the United States — and he has brought his core team from New Delhi and London to make it happen.

"My goal is to make Indian cuisine a mainstream cuisine across the US," Kalra told The Indian EYE at the Bellevue opening. His menu features paneer lasagna, karela calamari, and astrology-themed cocktails — the sort of food designed to convert the curry-cautious.

## Samosas in a food hall, vindaloo by algorithm

A few hundred miles south, an even bigger bet is being placed. Wonder, the $2-billion food-hall-and-delivery company founded by serial entrepreneur Marc Lore, launched a new Indian concept called Dabba this month. Named after Mumbai's legendary dabbawallas — the lunch-box delivery workers who have been crisscrossing the city's train network for over 130 years — the concept is testing in four Philadelphia-area stores, with plans to go systemwide across Wonder's 100-plus East Coast locations later this year.

The menu is familiar but calibrated for mass appeal: samosas at $8.95, chicken tikka masala at $18.95, butter chicken, lamb vindaloo. All of it is prepared in Wonder's vertically integrated kitchens, where recipes are developed centrally and finished to order using specialised ovens. If Dabba scales, Wonder — which also owns Grubhub and Blue Apron — would become one of the few companies offering Indian food at truly national scale.

"We've built a vertically integrated model that allows us to control the full process — from recipe development through production and final preparation in our kitchens," a Wonder spokesperson said. "For Dabba, that includes developing our curries and sauces in-house and focusing on the techniques required to build depth and consistency in flavour."

## The childhood friends and the cult favourite

In Washington, DC, two childhood friends who grew up around their immigrant fathers' Indian restaurants are expanding on a different wavelength. Sahil Rahman and Rahul Vinod's three-unit fast-casual chain Rasa — a portmanteau of their names, and the Sanskrit word for "the essence of" — has just secured growth funding from Rellevant Partners to add locations along the East Coast.

"We grew up in and around Indian restaurants," Vinod told Restaurant Business. "People were unfamiliar with that food. We would bring our friends and colleagues to our fathers' restaurants. Time and time again they would leave almost evangelised by the experience. We always wondered why more people haven't had the same experience with Indian food we do."

Their answer is dishes with names like Tikka Chance on Me and Goa Your Own Way — cheeky, but backed by serious spice work.

Meanwhile, Dishoom, the cult-favourite Bombay café chain that has turned weekend queues into a national pastime in Britain, is preparing to open its first US restaurant in New York City. The expansion is backed by L Catterton, the private-equity firm behind LVMH's luxury brands. If Dishoom can replicate its London magic — all-day Irani café fare, immaculate design, and a pay-it-forward meal programme — it could become the Indian equivalent of Nobu or Nando's in the American market.

## The diner that became a Bombay

And then there is the story of the Menlo Park Diner in Edison, New Jersey — a 24-hour institution that first opened in 1960 and never fully recovered after the pandemic. It closed for good after a fire. Now, in a transformation that captures something essential about the changing American suburb, the old diner is becoming House of Bombay, a new Indian restaurant. A soft opening is expected this month.

Edison's population is roughly 40 per cent South Asian. The diner-to-Indian-restaurant pipeline is not a cultural footnote; it is demography in real time.

## The numbers behind the boom

The scale of the opportunity explains the frenzy. Indian cuisine is one of the fastest-growing segments in American dining. Some 34 per cent of US consumers say they have tried Indian food and consider it "unique and exciting," according to Technomic consumer data. The country already has 50-unit Bawarchi Indian Cuisine, 42-unit Honest Restaurants, and 19-unit Curry Up Now — chains that barely existed a decade ago.

What changed is not just American taste buds. It is the 5.1 million–strong Indian-American population — the wealthiest and most educated ethnic group in the country — which built the customer base, trained the chefs, and normalised the flavours long before Michelin or Marc Lore got involved. Every weekend samosa at a temple fundraiser, every dosa at a Diwali potluck, every biryani passed across a cubicle wall at a tech company — all of it was infrastructure, laid one plate at a time.

The question is no longer whether Indian food can go mainstream in America. It already has. The question is who will own the franchise."""
    },

    # ── ARTICLE 2: India Census 2027 & Caste Enumeration ────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India Is Counting Its People — and Their Caste — for the First Time in 95 Years. Every NRI Should Be Paying Attention.",
        "subheadline": "The 2027 Census will reshape parliamentary seats, reservation quotas, and welfare targeting. For a diaspora rooted in the south, the numbers could rearrange everything they thought was settled.",
        "slug": slug2,
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Most NRIs originate from southern states that fear losing Lok Sabha seats in delimitation. The census will also shape reservation policy, property rights, and welfare — all areas where NRIs maintain deep personal and financial stakes.",
        "tags": ["nri", "diaspora", "india-census-2027", "caste-enumeration", "delimitation", "lok-sabha", "southern-states"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/2027_census_of_India"},
            {"name": "ORF Online", "url": "https://orfonline.org"},
            {"name": "Dainik Jagran English", "url": "https://english.dainikjagranmpcg.com"},
            {"name": "The Squirrels", "url": "https://thesquirrels.in"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img2_final,
        "image_caption": "Prime Minister Narendra Modi fills out the self-enumeration form for Census 2027, the first census to go fully digital",
        "image_attribution": "Wikimedia Commons",
        "body": """On the first of April this year, hundreds of thousands of enumerators fanned out across India carrying not clipboards but smartphones. For the first time in the country's history, Census 2027 — India's 16th — is being conducted entirely digitally, with a dedicated mobile application in 16 languages and a self-enumeration portal that lets citizens submit their own details online. Prime Minister Narendra Modi himself sat down to fill out the digital form, making it the most visible census launch in living memory.

But the technology is not the headline. The headline is that India will, for the first time since 1931, count its people by caste.

## Ninety-five years of silence

The last time India attempted a comprehensive caste census was under the British Raj, when the colonial administration recorded caste as part of the 1931 enumeration. Independent India has conducted a census every decade since 1951, but successive governments deliberately avoided the caste question — fearing, not unreasonably, that hard numbers would ignite demands for larger reservation quotas and rearrange the country's political arithmetic.

That era of deliberate ambiguity is ending. A June 2025 Gazette notification under Section 3 of the Census Act, 1948, legally mandated the collection of socio-economic and caste data during the second phase of the census, scheduled for February 2027. The digital infrastructure — mobile apps, backend portals, cybersecurity protocols — has been explicitly updated to capture this new demographic layer.

The implications are seismic. India's affirmative action system currently reserves seats in education, government jobs, and legislatures for Scheduled Castes, Scheduled Tribes, and Other Backward Classes. But no one knows, with any precision, how large these groups actually are. Policymakers have been working with extrapolations from the 1931 data and periodic sample surveys. A fresh count could trigger demands for sub-categorisation within OBC quotas, adjustments to creamy-layer thresholds, and a wholesale renegotiation of who benefits from the world's largest affirmative action programme.

## The delimitation question

The census carries a second charge that is, if anything, even more politically explosive: it will determine the redistribution of seats in the Lok Sabha, India's lower house of parliament.

India's parliamentary constituencies were last redrawn using 1971 population data. A constitutional freeze, extended multiple times, prevented redistribution to avoid penalising states that had successfully controlled population growth. But the freeze is expiring, and the 2027 Census will serve as the basis for a fresh delimitation exercise.

The maths is stark. States in the south and west — Kerala, Tamil Nadu, Karnataka, Andhra Pradesh, Telangana — slowed their population growth decades ago, in line with national policy. States in the north — Uttar Pradesh, Bihar, Madhya Pradesh, Rajasthan — did not. A straight population-proportional redistribution could see southern states lose dozens of seats while northern states gain them.

Pinarayi Vijayan, the Chief Minister of Kerala, has called the exercise "a demographic coup that undermines the fundamental principles of federalism." K.T. Rama Rao of the BRS described the contradiction bluntly: "Southern states, which are moving forward with progressive policies, get fewer seats."

The Women's Reservation Bill — introduced as the Constitution (131st Amendment) on April 16, 2026 — would have tied reserved seats for women to this same delimitation data. It fell short of the required two-thirds majority by 56 votes.

## Why the diaspora cannot look away

This might seem like domestic Indian politics. It is not — or at least, not only.

The Indian diaspora is disproportionately southern. The states that stand to lose the most political representation — Kerala, Tamil Nadu, Andhra Pradesh, Telangana, Karnataka — are the same states that have sent the most engineers, doctors, and entrepreneurs to the United States, the United Kingdom, Canada, and the Gulf. Tamil Nadu and Kerala alone account for a vast share of the 35 million–strong global Indian diaspora.

A loss of parliamentary seats for these states means a loss of voice on policies that directly affect NRIs: property law enforcement, infrastructure investment, airport connectivity, educational institutions, and the very reservation system that shaped many NRIs' own trajectories. OCI holders cannot vote, but they own land, fund family businesses, endow institutions, and pay taxes on Indian income. They have more at stake than most voters.

Caste enumeration adds another layer. In diaspora communities from Silicon Valley to Slough, caste has become an increasingly visible — and contested — social fault line. California's failed caste discrimination bill, the now-dead New York caste legislation, and the ongoing debate at American universities all draw energy from the same question: does caste travel? India's first hard data on caste in nearly a century will not settle that argument, but it will certainly reshape it.

## 33 questions, one country

The census questionnaire covers 33 structured items — demographics, housing conditions, asset ownership, social classification. In a nod to modern realities, live-in couples who have cohabited for an extended period will be recorded as married. A mobile phone with FM will count as a radio. Watching YouTube will not count as owning a television.

The data has been classified as Critical Information Infrastructure, subject to biometric access controls and oversight by the National Critical Information Infrastructure Protection Centre. Census officials have clarified that citizens are not required to disclose income, bank details, or identification documents like Aadhaar or PAN — a safeguard against the kind of coercion that marked earlier exercises.

The house-listing phase will run until September 2026. The population enumeration phase, which includes the caste question, begins in February 2027. The first results are unlikely before late 2027 at the earliest.

For a diaspora that has spent decades navigating identity between two countries, the wait will feel both very long and very personal."""
    },
]

# ── Insert ───────────────────────────────────────────────────────────────────
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
