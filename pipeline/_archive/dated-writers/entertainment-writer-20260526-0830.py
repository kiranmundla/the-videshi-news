#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 15:30 UTC batch (08:30 PDT):
1. Karisma Kapoor's Brown teaser — ZEE5 neo-noir thriller where she plays
   Rita Brown, a troubled, pill-popping Kolkata cop. Directed by Abhinay Deo.
   Her most transformative OTT role after decades of 90s glamour.
2. Karan Johar turns 54 — birthday celebrated with Kareena Kapoor's monochrome
   photos, Farah Khan's reel, Manish Malhotra's behind-the-scenes Met Gala
   video. First Indian filmmaker at the Met Gala, Raja Ravi Varma-inspired
   ensemble by Manish Malhotra. The man who defined NRI cinema reflects.
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

# ── Image sourcing: Wikipedia first (per IMAGE-SOURCING-RULES.md) ──
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
        print(f"  Pexels HTTP {r.status_code} for '{q}'")
    return None

# ── Supabase image upload ──
def upload_image_to_supabase(img_url, filename):
    """Download image and upload to Supabase article-images bucket. Returns public URL."""
    try:
        img_data = requests.get(img_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0"}).content
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        r = requests.post(
            upload_url,
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=img_data,
            timeout=30,
        )
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return img_url  # Fall back to original URL

now = datetime.now(timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")
articles = []


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Karisma Kapoor's "Brown" — ZEE5 Neo-Noir
# ══════════════════════════════════════════════════════════════
slug1 = "karisma-kapoor-brown-zee5-kolkata-cop-neo-noir-abhinay-deo-teaser-20260526"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append({
        "id": art1_id,
        "headline": "Karisma Kapoor Just Dropped a Teaser for a ZEE5 Show Where She Plays an Alcoholic, Pill-Popping Kolkata Cop. If You Grew Up Watching Her Dance in 'Dil To Pagal Hai,' This Will Require an Adjustment Period.",
        "subheadline": "ZEE5's 'Brown' is a neo-noir psychological thriller directed by Abhinay Deo (Delhi Belly, 24). Karisma plays Rita Brown — a disgraced officer battling personal demons while investigating a serial killer targeting women in Kolkata. The teaser has already gone viral, with netizens calling it her most fearless role in 30 years.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 76,
        "tags": ["Karisma Kapoor", "Brown", "ZEE5", "OTT", "neo-noir", "Abhinay Deo", "Kolkata", "web series", "Rita Brown", "streaming", "Bollywood comeback", "NRI", "diaspora"],
        "diaspora_angle": "For NRIs of a certain age, Karisma Kapoor is frozen in a specific cultural amber: the dancing queen of the 90s, the girl in the yellow outfit from Dil To Pagal Hai, the actress who won a National Award before anyone expected her to and then quietly stepped away from the spotlight. She is the Bollywood star your parents reference when they want to make a point about 'class' versus 'item numbers.' Seeing her play an alcoholic, pill-popping cop in a neo-noir thriller set in Kolkata is the kind of cognitive dissonance that only OTT can create — and it is exactly the reason diaspora audiences have become the biggest consumers of Indian streaming content.",
        "sources": [
            {"url": "https://www.bollywoodhungama.com/news/bollywood/brown-teaser-out-karisma-kapoor-plays-a-troubled-kolkata-cop-in-abhinay-deos-neo-noir-thriller-watch/", "name": "Bollywood Hungama"},
            {"url": "https://www.newkerala.com/entertainment/karisma-kapoors-fierce-cop-avatar-in-brown-teaser/", "name": "NewKerala"},
            {"url": "https://www.zoomtventertainment.com/entertainment/brown-teaser-released-karisma-kapoor-portrays-a-tough-police-officer/", "name": "Zoom TV"},
            {"url": "https://www.filmibeat.com/bollywood/karisma-kapoor-brown-zee5-teaser/", "name": "FilmiBeat"}
        ],
        "image_search_query": "Karisma Kapoor",
        "image_entities": ["Karisma Kapoor"],
        "image_must_show": "Karisma Kapoor, Indian actress",
        "word_count": 720,
        "body": """The teaser opens in darkness. A woman sits at a desk in what appears to be a police station. Her hair is unwashed. Her eyes are hollow. She picks up a phone. The camera holds on her face for three seconds longer than any Bollywood trailer would dare.

This is **Karisma Kapoor**. And she looks nothing like Karisma Kapoor.

## The Transformation

**Brown**, a new **ZEE5** original series directed by **Abhinay Deo** — the filmmaker behind *Delhi Belly* and the Indian adaptation of *24* — is a **neo-noir psychological crime thriller** set in **Kolkata**. Karisma plays **Rita Brown**, a disgraced officer in the Kolkata Police Force who is battling alcoholism, prescription drug dependency, and the ghosts of a career that went sideways while investigating a serial killer targeting women across the city.

The teaser dropped quietly online and immediately went viral. Not for a dance step. Not for a fashion moment. For the sheer shock of seeing one of the 1990s' most polished, glamorous leading ladies looking like she had slept in a jail cell and woken up to solve a murder.

Netizens called it her "most fearless role in 30 years." They are probably right.

## Why Karisma Kapoor in 2026 Is a Bigger Deal Than You Think

If you are a millennial NRI, Karisma Kapoor is not a name you file under "90s nostalgia." She is a name you file under "the first Bollywood actress I ever had an opinion about."

She was the girl in the yellow outfit in **Dil To Pagal Hai** (1997) — the film your parents watched on a rented VCD from the Indian grocery store, the film you watched because there was nothing else to do on a Sunday afternoon, the film where you realized that Bollywood musicals could make you feel things you didn't have vocabulary for.

She was the lead of **Raja Hindustani** (1996) — one of the highest-grossing Hindi films of its decade, a movie that played in NRI community halls from Edison to Southall. She won the **Filmfare Award for Best Actress** for it — and then won it again for **Dil To Pagal Hai**. Back-to-back. In an era when awards were not gifted at brand events.

She was one half of the Kapoor sisters — the other being Kareena — and for a brief, incandescent window in the mid-to-late 90s, she was the bigger star. She was the one who proved that a woman from the Kapoor family could be more than a wife. She was the one who won the **National Film Award for Best Supporting Actress** for **Dil To Pagal Hai** — the kind of recognition that arrives when an industry grudgingly admits that the person they dismissed as a commercial star is, in fact, an actress.

And then she stepped back. Marriage. Family. A quiet withdrawal from the spotlight that lasted the better part of fifteen years.

## The OTT Reinvention

Brown is not Karisma Kapoor's first OTT project. She appeared in **Mentalhood** (2020), a ALTBalaji series about urban motherhood that was pleasant and forgettable. But *Brown* is something else entirely.

The source material is Abheek Barua's novel, adapted into a dark, morally complex narrative that Abhinay Deo has set against the crumbling architecture and monsoon-soaked streets of Kolkata. Rita Brown is not a clean protagonist. She is messy, compromised, chemically dependent, and possibly unreliable as a narrator of her own investigation.

This is the kind of role that Indian OTT has made possible — the kind that would never have existed in the theatrical ecosystem of the 90s, where leading ladies were expected to be aspirational, not damaged. It is the kind of role that has turned streaming platforms into the single most important pipeline for serious Indian acting.

For the diaspora, the significance is double-edged. On one hand, seeing Karisma Kapoor in this avatar disrupts a very specific emotional relationship — she was the Bollywood of your childhood, preserved in amber, permanently 25 years old and dancing in slow motion. On the other hand, this is exactly what makes OTT compelling for NRI audiences: the promise that Indian entertainment has grown up alongside them.

## What We Know About the Show

The series is produced by **ZEE5** and directed by **Abhinay Deo**, whose *Delhi Belly* (2011) remains one of the sharpest, most tonally daring Hindi films of the last twenty years. The neo-noir framing is intentional — *Brown* is shot in muted tones, with Kolkata functioning not just as a backdrop but as a character, a city whose colonial architecture and contemporary chaos mirror Rita Brown's own internal fractures.

No release date has been confirmed yet, but the teaser's reception suggests ZEE5 will not sit on it for long. The streaming wars are intense, and a Karisma Kapoor-led neo-noir is the kind of project that makes headlines simply by existing.

For the actress who once defined what it meant to be a Bollywood heroine, the definition is changing. She is not the dancing queen anymore. She is a cop in Kolkata who drinks too much and takes too many pills and might be the only person who can catch a killer.

It is, in every way, a role she could not have played at 25. And it is, in every way, better for it.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Karan Johar Turns 54 — Met Gala, Birthday, Legacy
# ══════════════════════════════════════════════════════════════
slug2 = "karan-johar-54-birthday-met-gala-debut-manish-malhotra-raja-ravi-varma-first-indian-filmmaker-20260526"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append({
        "id": art2_id,
        "headline": "Karan Johar Just Turned 54. Two Weeks Ago He Was the First Indian Filmmaker at the Met Gala. Manish Malhotra Dressed Him Like a Raja Ravi Varma Painting. The Boy Who Was Bullied for Being 'Like a Girl' Walked Into the Most Exclusive Room in Fashion and Didn't Flinch.",
        "subheadline": "On May 25, Karan Johar turned 54. Kareena Kapoor wished him with rare monochrome photos. Farah Khan made a reel calling herself 'Khaala.' Manish Malhotra released a behind-the-scenes video of the Met Gala debut that made Malaika Arora cry. The man who invented the NRI love story — and became NRI culture's most consistent mirror — is having a year.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 75,
        "tags": ["Karan Johar", "Met Gala 2026", "Manish Malhotra", "Raja Ravi Varma", "birthday", "Indian filmmaker", "Kareena Kapoor", "Farah Khan", "Bollywood", "fashion", "NRI", "diaspora", "LGBTQ"],
        "diaspora_angle": "No one in Indian cinema has built a career more directly around the emotional architecture of NRI life than Karan Johar. Kabhi Khushi Kabhie Gham was the film that played in every Indian household in North America and the UK during the early 2000s. It was the film where Amitabh Bachchan said 'It's all about loving your parents' and every NRI parent printed it on a motivational poster. Kuch Kuch Hota Hai was the film that taught a generation of Indian kids in Brampton and Fremont and Hounslow that love stories could have an Indian soundtrack. SOTY was the guilty pleasure. My Name Is Khan was the post-9/11 film that NRIs needed but didn't know they needed. Karan Johar has been, for three decades, the filmmaker who makes the diaspora feel seen — sometimes flatteringly, sometimes uncomfortably, always accurately. His presence at the Met Gala was not just fashion news. It was the diaspora's filmmaker arriving at the diaspora's red carpet.",
        "sources": [
            {"url": "https://www.latestly.com/entertainment/bollywood/manish-malhotra-wishes-karan-johar-birthday-met-gala-debut-7445464.html", "name": "LatestLY"},
            {"url": "https://www.dailyheadlinez.com/kareena-kapoor-khan-wishes-karan-johar-kunal-kemmu-birthday/", "name": "Daily Headlinez"},
            {"url": "https://harpersbazaar.in/karan-johar-met-gala-2026-manish-malhotra/", "name": "Harper's Bazaar India"},
            {"url": "https://www.zoomtventertainment.com/karan-johar-farah-khan-khaala-birthday-reel/", "name": "Zoom TV"},
            {"url": "https://prestigeonline.com/sg/lifestyle/entertainment/best-met-gala-asian-looks-2026/", "name": "Prestige Online"}
        ],
        "image_search_query": "Karan Johar",
        "image_entities": ["Karan Johar"],
        "image_must_show": "Karan Johar, Indian filmmaker",
        "word_count": 750,
        "body": """On **May 25, 2026**, **Karan Johar** turned 54. The birthday celebrations were characteristically Bollywood: **Kareena Kapoor Khan** posted rare monochrome candid photos with a note about their decades-long friendship. **Farah Khan** made a playful Instagram reel at his party, with KJo calling her "Khaala" — the affectionate term that immediately went viral. **Manish Malhotra** released a behind-the-scenes video of the outfit he designed for Karan's **Met Gala debut** three weeks earlier, with footage that made **Malaika Arora** leave a tearful comment.

It was a birthday that doubled as a career retrospective — because Karan Johar at 54 is not the same Karan Johar who turned 50, and the difference is measured in a single room.

## The Room

On **May 5, 2026**, Karan Johar walked into the **Metropolitan Museum of Art** in New York City for the **Met Gala** — fashion's most exclusive annual event, where the guest list is curated by Anna Wintour and the dress code is treated as a creative mandate.

He was the **first Indian filmmaker** ever invited.

He wore a custom **Manish Malhotra** couture ensemble inspired by the paintings of **Raja Ravi Varma** — the 19th-century Indian artist who painted goddesses and queens with a European oil technique, creating the visual vocabulary that would become the foundation of Indian calendar art, Bollywood iconography, and an entire nation's idea of beauty. The outfit featured **hand-painted gold detailing**, classical Indian drapery reimagined as contemporary red-carpet drama, and the kind of maximalism that only Karan Johar can carry without tipping into costume.

Manish Malhotra, who also attended the Met Gala this year, called the creation the culmination of their **30-year collaboration** — a friendship and professional partnership that has defined the aesthetic of modern Bollywood fashion. In the birthday video he released, Malhotra showed the fitting process, the last-minute adjustments, the moment Karan saw the final look. Karan's reaction: "This is a masterpiece."

It was.

## The Boy Who Was Bullied

Here is the thing about Karan Johar at the Met Gala that most fashion coverage missed:

He has spoken publicly, repeatedly, about being bullied as a child for being effeminate. For being overweight. For not fitting the template of what an Indian boy was supposed to be. He has described, in interviews and in his autobiography *An Unsuitable Boy*, the experience of growing up knowing that something about him was "different" in a way that his culture had no language for — and then spending decades in an industry that celebrated him for his talent while constantly speculating about his personal life.

Karan Johar has never publicly come out. He has also never pretended to be straight. He exists in a space that is uniquely Indian — a space where everyone knows, no one says, and the work speaks for itself.

Walking into the Met Gala dressed like a Raja Ravi Varma painting — a painter who reimagined Indian femininity through a Western lens — was not subtle. It was a statement about beauty, about queerness, about Indian maximalism, and about the right to take up space in rooms that were never designed for you.

## The Filmmaker the Diaspora Built

No Indian filmmaker has a more direct relationship with NRI audiences than Karan Johar.

**Kuch Kuch Hota Hai** (1998) was the film that NRI kids watched on rented VCDs at sleepovers. **Kabhi Khushi Kabhie Gham** (2001) — K3G — was the NRI origin film: a wealthy Indian family, a London setting, Amitabh Bachchan's "It's all about loving your parents" line that became the most quoted sentence in Indian diaspora history. **My Name Is Khan** (2010) was the post-9/11 film that addressed what it meant to be Muslim and Indian in America. **Student of the Year** (2012) was the guilty pleasure that launched a generation of abs.

Each film was built around the same insight: that the Indian diaspora exists in a permanent state of emotional transit — between cultures, between generations, between the India they left and the India that exists now. Karan Johar understood this not because he conducted research, but because he *felt* it. His films are sentimental because the diaspora experience is sentimental. His characters overdress because NRIs overdress. His families fight loudly and love louder because that is what Indian families do when geography has stretched them across continents.

## The Birthday Reel

Farah Khan's reel from the party was the kind of content that only old Bollywood friendships produce. In it, she and Karan engage in affectionate roasting — she calls herself "Khaala" (the cool aunt/elder), he plays along. The video has the energy of a WhatsApp group chat between people who have known each other for 30 years and have stopped performing for the camera.

Kareena's monochrome photos — shared alongside a birthday wish for both Karan and her brother-in-law **Kunal Kemmu**, who shares the May 25 birthday — showed the private side of a public man. No red carpets. No couture. Just two people who have been in each other's lives long enough that the photos don't need to be flattering to be meaningful.

## 54 and Counting

Karan Johar is producing **Chand Mera Dil** (in theaters now), nurturing the next generation of Bollywood talent through Dharma Productions, and — if the Met Gala is any indication — operating at a level of cultural confidence that he has never had before.

He was bullied for being like a girl. He walked into the Met Gala dressed like a painting of a goddess.

He made the films that taught a generation of NRIs how to cry about India. And on his 54th birthday, the people who grew up watching those films sent him pictures and reels and told him that the films still work.

They still work because the feelings haven't changed. The distance between India and everywhere else is still measured in the same unit: the ache of a family that loves too much and says too little. Karan Johar has been soundtracking that ache for 28 years.

Happy birthday, KJo. The diaspora raises its chai.""",
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
# IMAGE SOURCING — Wikipedia first for person articles
# ══════════════════════════════════════════════════════════════
print("\n── Image Sourcing ──")

# Check image skip list
skip_list = set()
skip_file = Path.home() / "workspace/the-videshi-news/pipeline/image-skip-list.json"
if skip_file.exists():
    try:
        skip_list = set(json.loads(skip_file.read_text()))
    except:
        pass

image_tasks = [
    {
        "slug": slug1,
        "person": "Karisma Kapoor",
        "alt_persons": [],
        "pexels_fallback": None,  # Wikipedia should have Karisma Kapoor
        "attribution": "Wikimedia Commons",
    },
    {
        "slug": slug2,
        "person": "Karan Johar",
        "alt_persons": [],
        "pexels_fallback": None,  # Wikipedia should have Karan Johar
        "attribution": "Wikimedia Commons",
    },
]

for task in image_tasks:
    slug = task["slug"]
    if slug in skip_list:
        print(f"  ⏭ Skipped (in skip list): {slug[:50]}")
        continue

    # Find the article ID
    art_match = [a for a in articles if a["slug"] == slug]
    if not art_match:
        print(f"  ⚠ No article found for {slug[:50]}")
        continue
    art_id = art_match[0]["id"]

    # Step 1: Wikipedia — try primary name, then alternates
    img_url = fetch_wikipedia_person_image(task["person"])
    attribution = task["attribution"]

    if not img_url and task.get("alt_persons"):
        for alt in task["alt_persons"]:
            img_url = fetch_wikipedia_person_image(alt)
            if img_url:
                break

    # Step 2: Pexels fallback (only if specified)
    if not img_url and task.get("pexels_fallback"):
        print(f"  Wikipedia returned nothing for '{task['person']}', trying Pexels...")
        img_url = fetch_pexels_image(task["pexels_fallback"])
        attribution = "The Videshi"

    if img_url:
        # Upload to Supabase
        filename = f"{art_id}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        status = sb_patch(
            "p2_articles",
            f"id=eq.{art_id}",
            {"image_url": final_url, "image_attribution": attribution}
        )
        print(f"  PATCH image → HTTP {status} for {slug[:50]}")
    else:
        print(f"  ⚠ No image found for: {slug[:50]} — leaving blank (no image > wrong image)")


# ══════════════════════════════════════════════════════════════
# SCORE DECAY — entertainment articles
# ══════════════════════════════════════════════════════════════
print("\n── Score Decay ──")

# 7+ days old → score 35
cutoff_7d = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
status_7d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_7d}&score_total=gt.35",
    {"score_total": 35}
)
print(f"7d+ decay → HTTP {status_7d}")

# 3-7 days old → score 50
cutoff_3d = (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
status_3d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_3d}&published_at=gte.{cutoff_7d}&score_total=gt.50",
    {"score_total": 50}
)
print(f"3-7d decay → HTTP {status_3d}")


print("\n✅ Entertainment writer batch complete.")
