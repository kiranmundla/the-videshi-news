#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 06:30 PDT batch:
1. Diljit Dosanjh becomes first South Asian artist to sell out two consecutive
   nights at Madison Square Garden — AURA tour, Vikas Khanna Kada Prasad,
   Komagata Maru, bomb threat hoax
2. Zoya Akhtar confirms robbery at Tiger Baby office — 66 hard disks stolen
   containing Made in Heaven, Ghost Stories, unreleased footage; internal job,
   two arrests, drives sold for Rs 15-20K each
+ Score decay for older entertainment articles
"""

import json, os, uuid, requests, urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Supabase config ──
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

def sb_patch(table, filters, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, json=data, timeout=30)
    return r.status_code

def sb_get(table, filters, select="*"):
    r = requests.get(f"{SB_URL}/rest/v1/{table}?{filters}&select={select}", headers=HEADERS, timeout=15)
    return r.json() if r.status_code == 200 else []

def check_duplicate(slug):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS, timeout=15
    )
    return len(r.json()) > 0 if r.status_code == 200 else False


# ── Wikipedia person image (MANDATORY per IMAGE-SOURCING-RULES.md) ──
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


# ── Pexels fallback ──
PEXELS_KEY = None
pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() == "PEXELS_API_KEY":
                PEXELS_KEY = v.strip()

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": q, "per_page": 5, "orientation": "landscape"},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                return photos[0]["src"]["large2x"]
    return None


# ── Supabase image upload ──
def upload_image_to_supabase(img_url, filename):
    """Download image and upload to Supabase article-images bucket."""
    try:
        img_data = requests.get(img_url, timeout=15,
                                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}).content
        content_type = "image/jpeg"
        if img_url.lower().endswith(".png"):
            content_type = "image/png"
        elif img_url.lower().endswith(".svg"):
            content_type = "image/svg+xml"

        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        r = requests.post(upload_url, headers=upload_headers, data=img_data, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


now = datetime.now(timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")
articles = []


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Diljit Dosanjh Becomes First South Asian Artist
# to Sell Out Two Consecutive Nights at Madison Square Garden
# ══════════════════════════════════════════════════════════════
slug1 = "diljit-dosanjh-madison-square-garden-first-south-asian-artist-two-nights-aura-tour-20260526"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append({
        "id": art1_id,
        "headline": "Diljit Dosanjh Just Sold Out Madison Square Garden. Twice. In a Row. No Indian Artist Has Ever Done That.",
        "subheadline": "On May 24 and 25, 2026, Diljit Dosanjh performed two consecutive sold-out shows at MSG during his AURA World Tour — the first South Asian artist to headline the venue, let alone fill it for back-to-back nights. Outside, celebrity chef Vikas Khanna handed out Kada Prasad and jasmine bracelets to fans waiting in line. Inside, 20,000 people sang Punjabi songs in Manhattan. Back home in Ludhiana, someone sent a bomb threat to his house. It was a hoax. The concert was not.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "high",
        "status": "published",
        "published_at": now_iso,
        "score_total": 82,
        "tags": ["Diljit Dosanjh", "Madison Square Garden", "MSG", "AURA tour", "AURA World Tour 2026", "Punjabi music", "New York", "Vikas Khanna", "Kada Prasad", "Jimmy Fallon", "Komagata Maru", "Coachella", "BC Place", "Vancouver", "Rogers Centre", "Toronto", "South Asian", "bomb threat", "Ludhiana", "NRI", "diaspora"],
        "diaspora_angle": "This is the one that diaspora kids will tell their grandchildren about. For every Punjabi uncle who drove a taxi in Queens with Diljit playing on the stereo, for every Sikh kid who was asked 'what's on your head' in an American school, for every first-generation immigrant who watched Bollywood award shows and wondered when an Indian name would mean something at an American arena — this is the night. Madison Square Garden is not just a venue. It is the venue. Elvis played there. The Beatles played there. Led Zeppelin, Rolling Stones, Madonna, BTS. Now Diljit Dosanjh, from Dosanjh Kalan, a village in Jalandhar district with a population smaller than most apartment complexes in Queens. The fact that Vikas Khanna — another diaspora story, a Michelin-starred chef who came from Amritsar — was outside serving Kada Prasad to the crowd is not a footnote. It is the story. Two Punjabi men, both from modest origins, both now defining what Indian success looks like in New York City. One inside the Garden, the other outside it, feeding people. That is the most Punjabi sentence ever written about Madison Square Garden.",
        "sources": [
            {"url": "https://www.bollywoodhungama.com/news/features/diljit-dosanjh-creates-history-at-madison-square-garden-becomes-first-indian-musician-to-sell-out-two-consecutive-nights-at-the-iconic-venue/", "name": "Bollywood Hungama"},
            {"url": "https://www.cinemaexpress.com/hindi/news/2026/May/26/diljit-dosanjh-makes-history-on-the-same-stage-which-was-once-ruled-by-elton-john-and-madonna", "name": "Cinema Express"},
            {"url": "https://www.mirchi.in/bollywood/diljit-dosanjh-becomes-first-indian-artist-to-headline-a-concert-at-madison-square-garden", "name": "Radio Mirchi"},
            {"url": "https://www.bollywoodbubble.com/bollywood-news/diljit-dosanjh-becomes-first-indian-artist-to-headline-madison-square-garden-sells-2-night-shows-in-new-york/", "name": "Bollywood Bubble"},
            {"url": "https://www.mirchi.in/bollywood/diljit-dosanjhs-ludhiana-home-targeted-in-bomb-threat-scare", "name": "Radio Mirchi (bomb threat)"}
        ],
        "image_search_query": "Diljit Dosanjh singer",
        "image_entities": ["Diljit Dosanjh"],
        "image_must_show": "Diljit Dosanjh, Punjabi singer and actor",
        "word_count": 820,
        "body": """On May 24 and 25, 2026, **Diljit Dosanjh** walked onto the stage at **Madison Square Garden** in New York City and performed two consecutive sold-out concerts. No Indian artist had ever headlined the Garden before. No South Asian artist had ever sold it out for back-to-back nights.

The venue holds approximately **20,000 people**. Both nights were at capacity. Videos from inside the arena show the entire floor and upper decks lit with phone flashlights, thousands of voices singing Punjabi lyrics in unison in a building that has previously hosted **Elvis Presley**, **The Beatles**, **Led Zeppelin**, **Madonna**, **Elton John**, and **BTS**.

Diljit posted on Instagram after the first night: **"HISTORY HAS BEEN MADE. MADISON SQUARE GARDEN. WE DID IT FOLKS. KAL FER MILDE AN SAME PLACE SAME TIME. TWO NIGHTS AT THE GARDEN 🇺🇸 PANJABI AA GAYE OYE."**

He was not exaggerating.

## The AURA Tour

The Madison Square Garden dates are part of Diljit's **AURA World Tour 2026**, which has already produced record-breaking numbers across multiple continents. Earlier this year, the tour stopped at **BC Place** in **Vancouver**, where **55,000 fans** attended — making it one of the largest audiences for an Indian artist at a single concert in North America.

Before the Vancouver show, Diljit gave an interview on **The Tonight Show Starring Jimmy Fallon** — his second appearance on the programme. During the conversation, he told Fallon about the **Komagata Maru incident of 1914**, when a ship carrying 376 passengers — mostly Sikh men from Punjab — was denied entry into Vancouver harbour and forced to return to India, where British colonial police opened fire on the passengers upon arrival.

"I told Jimmy," Diljit later recounted, "that in 1914, Sikhs were not allowed into Vancouver. And in 2026, 55,000 people are singing Punjabi songs in Vancouver." Fallon, according to multiple reports, had no prior knowledge of the incident. The clip went viral.

The next stop after New York is **Rogers Centre** in **Toronto** on **May 31**, where another capacity crowd is expected.

## Outside the Garden: Vikas Khanna and Kada Prasad

While fans queued outside MSG on both nights, celebrity chef **Vikas Khanna** — the Michelin-starred Indian-American chef who runs **Bungalow** in New York — set up an impromptu station near the venue. He served **Kada Prasad**, the sweet wheat-flour offering distributed in Sikh gurdwaras, along with **jasmine floral bracelets** to fans waiting in line.

Videos posted on social media show Khanna personally serving fans, many of whom recognised him from his Netflix appearances and his restaurant. The gesture transformed the concert queue into something closer to a langar line than a ticket checkpoint — a communal Punjabi moment on Seventh Avenue.

Khanna did not make a formal announcement about the initiative. He simply showed up with food.

## Back in Ludhiana: The Bomb Threat

On **May 25** — the same day as the second MSG concert — an email threatening bomb blasts was sent to the **Ludhiana Municipal Corporation** and to an address associated with **Diljit Dosanjh's family home** in Ludhiana. The email, written in the name of the **"Khalistan National Army"**, referenced the **1984 anti-Sikh riots** and warned of explosions before **June 6** — the anniversary of **Operation Blue Star**.

Punjab Police and cybercrime units initiated an investigation. Security at multiple locations in Ludhiana was heightened. A search of the areas mentioned in the email found **no explosives or suspicious materials**. Police confirmed the threat was a **hoax**.

The email also targeted **Principal Inderjit Kaur**, the Mayor of Ludhiana. The Ludhiana Police registered a case and are tracing the email's origin. The threat follows a pattern of similar hoax emails sent to public figures and institutions in Punjab in recent weeks.

Diljit did not publicly acknowledge the threat. He performed the second MSG show as scheduled.

## The Numbers Behind the Name

Diljit Dosanjh's trajectory from Punjabi-language regional star to global arena headliner has no real precedent in Indian music.

He performed at **Coachella** in 2023, becoming the first Punjabi artist to appear at the festival. His Dil-Luminati Tour in 2024-25 sold out venues across **North America, Europe, Australia, and India**. His 2023 film **Crew** (with Kareena Kapoor Khan and Tabu) and 2024 film **Jatt & Juliet 3** were both commercial hits. His role as **Amar Singh Chamkila** in Imtiaz Ali's biographical film on Netflix brought critical acclaim.

But the music has always been the engine. Songs like **"Lover"**, **"Born to Shine"**, **"GOAT"**, and **"Kinni Kinni"** have accumulated billions of streams across Spotify, YouTube, and Apple Music. His Instagram following exceeds **75 million**. His concert revenue in 2025 alone reportedly crossed **$100 million**, making him one of the highest-earning touring artists of South Asian origin in history.

## What MSG Means

Madison Square Garden is often called "The World's Most Famous Arena." It has hosted **4,600 events per year** since it opened in its current form in 1968. Its concert legacy includes some of the most iconic performances in music history — from George Harrison's Concert for Bangladesh (1971) to Jay-Z's farewell residency (2003) to BTS's sold-out run (2022).

For Indian music, MSG has been a milestone that seemed permanently out of reach. Bollywood playback singers have performed in smaller venues across New York — the **Barclays Center**, the **Prudential Center**, the **Nassau Coliseum** — but never at the Garden. AR Rahman performed at the **United Nations General Assembly Hall** in 2016 but not at MSG. Arijit Singh has sold out the **O2 Arena** in London but not MSG.

Diljit didn't just play MSG. He played it twice. Consecutively. In Punjabi.

## The Next Stop

The AURA tour continues to **Rogers Centre** in **Toronto** on May 31, followed by dates across Europe and a return to India later in the year. Toronto is expected to draw one of the tour's largest North American crowds, given the size of the Punjabi diaspora in the Greater Toronto Area.

In the meantime, Vikas Khanna has returned to running his restaurant. The bomb threat investigation continues in Ludhiana. And somewhere in Manhattan, a venue that has hosted every genre of music that has ever mattered now has Punjabi on the list.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Zoya Akhtar Confirms Robbery at Tiger Baby —
# 66 Hard Disks Stolen, Sold for ₹15-20K Each
# ══════════════════════════════════════════════════════════════
slug2 = "zoya-akhtar-tiger-baby-office-robbery-66-hard-disks-stolen-made-in-heaven-ghost-stories-20260526"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append({
        "id": art2_id,
        "headline": "Someone Stole 66 Hard Disks from Zoya Akhtar's Office. They Contained Made in Heaven, Ghost Stories, and Unreleased Footage. Each Drive Was Sold for ₹15,000.",
        "subheadline": "Tiger Baby Digital LLP — the production company founded by Zoya Akhtar and Reema Kagti behind Made in Heaven, Luck by Chance, and Gully Boy — discovered on May 21 that 66 of its 119 hard disks were missing. The drives, ranging from 16TB to 72TB, contained raw footage, edited scenes, post-production backups, advertisement campaign material, and unreleased OTT content. An office boy admitted to stealing 24 of them over five months and selling them in Mumbai's grey market. The entire haul was worth crores. Each disk fetched roughly ₹15,000 to ₹20,000.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 74,
        "tags": ["Zoya Akhtar", "Reema Kagti", "Tiger Baby", "Tiger Baby Digital", "Made in Heaven", "Ghost Stories", "hard disk theft", "Mumbai Police", "Bandra", "data theft", "Bollywood", "OTT", "cybersecurity", "intellectual property", "production house", "NRI", "diaspora"],
        "diaspora_angle": "For NRIs who binged Made in Heaven on late-night Amazon Prime sessions — the show that explained modern Indian marriages to people who had left India before their own weddings happened — the idea that its raw footage was sitting on hard disks sold for the price of a dinner in Manhattan is both absurd and familiar. India's entertainment industry produces content consumed by hundreds of millions of people globally, but its physical infrastructure — the offices, the storage, the security — often operates at a scale that would horrify a Silicon Valley intern. The gap between the creative ambition of a Zoya Akhtar production and the reality of an office boy walking out with 72-terabyte drives in a backpack is the gap that defines India's creative economy. For diaspora professionals who work in tech, media, or entertainment in the US and UK, this story is a reminder that the Bollywood they consume on streaming platforms is still, in many ways, stored in cardboard boxes in Bandra offices.",
        "sources": [
            {"url": "https://www.bollywoodhungama.com/news/bollywood/exclusive-zoya-akhtar-confirms-robbery-at-office-after-66-hard-disks-go-missing-says-luckily-we-have-backup-files-of-everything/", "name": "Bollywood Hungama"},
            {"url": "https://www.bollywoodhungama.com/news/bollywood/shocking-66-hard-disks-containing-made-in-heaven-ghost-stories-and-unreleased-footage-go-missing-from-zoya-akhtar-reema-kagtis-tiger-baby-office/", "name": "Bollywood Hungama (initial report)"},
            {"url": "https://www.hollywoodreporterindia.com/film-industry/tiger-baby-data-theft-66-hard-disks-stolen", "name": "Hollywood Reporter India"},
            {"url": "https://www.latestly.com/entertainment/zoya-akhtar-reema-kagti-tiger-baby-hard-disks-stolen", "name": "LatestLY"},
            {"url": "https://www.indulgexpress.com/entertainment/valuable-footages-go-missing-from-rima-kagtis-tiger-baby-office", "name": "Indulge Express"}
        ],
        "image_search_query": "Zoya Akhtar filmmaker",
        "image_entities": ["Zoya Akhtar"],
        "image_must_show": "Zoya Akhtar, Indian filmmaker and director",
        "word_count": 780,
        "body": """On **May 21, 2026**, staff at **Tiger Baby Digital LLP** — the production company co-founded by filmmaker **Zoya Akhtar** and her creative partner **Reema Kagti** — attempted to locate several hard disks required for ongoing projects. The disks were not where they were supposed to be.

An internal audit followed. Of the **119 hard disks** on the company's inventory, **66 were missing**.

The drives ranged in capacity from **16TB to 72TB**. Investigators believe they contained **raw footage, edited scenes, post-production files, archival backups, advertisement campaign material, and unreleased content** linked to some of Bollywood's most prominent OTT and film projects — including **Made in Heaven**, **Ghost Stories**, and a project reportedly titled **Gandhi Money**.

## The Complaint and the Arrests

**Mehjabeen Mushtaq Shaikh**, the executive assistant and HR administrator at Tiger Baby Digital, filed a complaint with the **Bandra Police** in Mumbai. An FIR was registered against **Mohammad Shahid Azim Khan**, described in reports as an office boy at the company, and **Ritesh Suresh Shah**, identified as a buyer.

Both were arrested. Police remanded them to custody until **May 29**.

According to investigators, Khan admitted to stealing **24 hard disks** over a period of approximately **five months**. He allegedly sold each drive for between **₹15,000 and ₹20,000** in Mumbai's grey market. The total inventory value of the missing 66 drives was estimated at **₹12-13 lakh** for the hardware alone — but the intellectual property stored on them, if leaked or distributed, could result in losses running into **crores**.

Police are now investigating whether any of the stolen data was **copied, leaked, or circulated online** before the drives were physically sold. The involvement of a larger network has not been ruled out.

## Zoya Akhtar Responds

Speaking exclusively to **Bollywood Hungama**, Zoya Akhtar confirmed the incident.

"Yes there has been a robbery in my office, hard disks have been stolen," she said. "We filed a complaint and police has made some arrests as well. It's an internal job, it's sad to what extent people go to make money."

She added one piece of reassurance: **"Luckily we have backup files of everything."**

The statement suggests that while the physical drives are gone, the production data has not been permanently lost. However, the question of whether any content was duplicated before the drives were sold remains open.

## What Was on the Drives

Tiger Baby Digital is the production arm behind some of the most critically acclaimed Indian content of the past decade.

**Made in Heaven** — the Amazon Prime Video series about Delhi's wedding industry, its class structures, its sexual politics, and its moral compromises — ran for two seasons (2019 and 2023) and was one of the most-watched Indian original series on the platform. **Ghost Stories** (2020) was an anthology horror film directed by Akhtar alongside Anurag Kashyap, Dibakar Banerjee, and Karan Johar. Tiger Baby has also produced **Luck by Chance** (2009), contributed to **Gully Boy** (2019), and is developing multiple new projects for streaming platforms.

Reports indicate that the stolen drives contained not just completed project files but **raw footage** — the unedited, ungraded, unprocessed recordings from set — as well as **advertisement campaign material** for brand partnerships. Raw footage is particularly sensitive because it includes outtakes, alternate takes, behind-the-scenes material, and content that was never intended for public release.

## The ₹15,000 Hard Disk Problem

The economics of the theft illuminate a broader vulnerability in India's entertainment production infrastructure.

A 72-terabyte hard disk retails for approximately **₹25,000 to ₹40,000** depending on the brand and specification. The content on such a drive — if it contains unreleased footage from a major OTT series — could be worth orders of magnitude more. That the drives were allegedly sold for **₹15,000 to ₹20,000 each** — roughly the price of a dinner for two at a mid-range restaurant in Bandra — suggests the buyer was purchasing them for the hardware resale value, not for the data.

But investigators cannot yet confirm this. The possibility that someone recognised the value of the data and either copied or distributed it before the physical drives changed hands is the central concern driving the ongoing investigation.

## An Industry Problem

The Tiger Baby theft is not an isolated incident. Indian production houses, despite producing content that streams globally on platforms with billions of dollars in market capitalisation, frequently store critical production data on **local hard drives** rather than enterprise-grade cloud infrastructure. The reasons are partly cultural — many filmmakers and editors prefer physical drives for speed and familiarity — and partly economic. Cloud storage at the scale required for film production (where a single day of shooting can generate **multiple terabytes** of data) remains expensive and bandwidth-constrained in parts of India.

**Siddharth Roy Kapur**, the president of the **Producers Guild of India**, has previously flagged digital security as an industry-wide concern, noting that production houses of all sizes remain vulnerable to both internal theft and external cyberattacks.

Zoya Akhtar's Tiger Baby had backups. Not every production house does.

## What Happens Next

The Bandra Police investigation continues. The remand hearing for Khan and Shah is scheduled for **May 29**. Investigators are attempting to trace the full chain of custody for all 66 missing drives — including the **42 drives** that Khan did not account for in his confession.

Tiger Baby Digital has not announced any changes to its data security protocols. Zoya Akhtar, characteristically, said what needed to be said and no more. The backups exist. The police have made arrests. The work continues.

The hard disks are still out there.""",
    })
    print(f"✅ Article 2 prepared: {slug2}")
else:
    print(f"⚠️ DUPLICATE: {slug2}")


# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
print(f"\n📝 Inserting {len(articles)} articles...")
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Inserted: {art['slug'][:60]} → {result[0]['id'][:8] if result else '?'}")
    except Exception as e:
        print(f"❌ Insert failed for {art['slug'][:40]}: {e}")


# ══════════════════════════════════════════════════════════════
# IMAGE SOURCING — Wikipedia first (mandatory), Pexels fallback
# ══════════════════════════════════════════════════════════════
print("\n── Image Sourcing ──")

# Check image skip list
skip_list = []
skip_file = Path.home() / "workspace/the-videshi-news/pipeline/image-skip-list.json"
if skip_file.exists():
    try:
        skip_list = json.loads(skip_file.read_text())
    except:
        pass

image_tasks = []
for art in articles:
    if art["slug"] in skip_list:
        print(f"  ⏭ Skipping (in skip list): {art['slug'][:50]}")
        continue
    image_tasks.append(art)

for art in image_tasks:
    slug = art["slug"]
    art_id = art["id"]
    img_url = None
    attribution = None

    # Step 1: Try Wikipedia for person images
    person_names = art.get("image_entities", [])
    for person in person_names:
        print(f"  🔍 Wikipedia lookup: '{person}'")
        img_url = fetch_wikipedia_person_image(person)
        if img_url:
            attribution = "Wikimedia Commons"
            break

    # Step 2: Pexels fallback only if Wikipedia failed
    if not img_url:
        query = art.get("image_search_query", "")
        if query:
            print(f"  🔍 Pexels fallback: '{query[:50]}'")
            img_url = fetch_pexels_image(query)
            if img_url:
                attribution = "The Videshi"

    # Step 3: Upload and patch
    if img_url:
        filename = f"{art_id}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        if final_url:
            patch_data = {"image_url": final_url}
            if attribution:
                patch_data["image_attribution"] = attribution
            status = sb_patch("p2_articles", f"id=eq.{art_id}", patch_data)
            print(f"  ✅ Image set for {slug[:50]} → HTTP {status}")
        else:
            print(f"  ⚠️ Upload failed for {slug[:50]}, setting direct URL")
            sb_patch("p2_articles", f"id=eq.{art_id}", {"image_url": img_url})
    else:
        print(f"  ⚠️ No image found for: {slug[:50]} (no image > wrong image)")


# ══════════════════════════════════════════════════════════════
# SCORE DECAY — entertainment articles
# ══════════════════════════════════════════════════════════════
print("\n── Score Decay ──")

cutoff_7d = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
status_7d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_7d}&score_total=gt.35",
    {"score_total": 35}
)
print(f"7d+ decay → HTTP {status_7d}")

cutoff_3d = (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
status_3d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_3d}&published_at=gte.{cutoff_7d}&score_total=gt.50",
    {"score_total": 50}
)
print(f"3-7d decay → HTTP {status_3d}")


print("\n✅ Entertainment writer batch complete.")
