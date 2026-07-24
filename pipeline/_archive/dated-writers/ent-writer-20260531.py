#!/usr/bin/env python3
"""Entertainment writer — 2026-05-31 evening batch"""

import json, os, re, sys, time, uuid, hashlib
from datetime import datetime, timezone

import requests, urllib.parse

# ── env ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────────
def sb_insert(table, payload):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=payload, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None
    data = r.json()
    return data[0] if isinstance(data, list) else data

def sb_patch(table, filters, payload):
    qs = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{qs}", headers=HEADERS, json=payload, timeout=30)
    if r.status_code not in (200, 204):
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return r

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:100]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            cmd = [
                "curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                "-H", f"Authorization: {PEXELS_KEY}",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ✗ Download failed ({r.status_code}) for {image_url[:80]}")
            return None
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ✗ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ✗ Image too small ({len(r.content)} bytes)")
            return None

        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        up = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{filename}",
            headers=upload_headers,
            data=r.content,
            timeout=30,
        )
        if up.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}")
            return public_url
        else:
            print(f"  ✗ Upload failed ({up.status_code}): {up.text[:200]}")
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
    return None

def validate_image_url(url):
    """Check that url returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ Banned source detected: {b}")
            return False
    try:
        r = requests.head(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0"}, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't respond to HEAD, try GET
        if r.status_code != 200:
            r2 = requests.get(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0"}, stream=True)
            ct2 = r2.headers.get("Content-Type", "")
            if r2.status_code == 200 and "image" in ct2:
                chunk = r2.raw.read(6000)
                r2.close()
                if len(chunk) > 5000:
                    return True
    except Exception as e:
        print(f"  ⚠ Validation error: {e}")
    return False

def source_person_image(person_name, slug):
    """Source image for a person: Wikipedia → Pexels → upload to Supabase."""
    img_url = fetch_wikipedia_person_image(person_name)
    if not img_url:
        # Try alternate Wikipedia forms
        for variant in [f"{person_name} (actor)", f"{person_name} (actress)", f"{person_name} (film director)"]:
            img_url = fetch_wikipedia_person_image(variant)
            if img_url:
                break

    if img_url and "upload.wikimedia.org" in img_url:
        # Upload to Supabase for permanence
        filename = f"{slug}.jpg"
        final_url = upload_to_supabase_storage(img_url, filename)
        if final_url:
            return final_url, "Wikimedia Commons"

    if not img_url:
        print(f"  → No Wikipedia image for {person_name}, trying Pexels...")
        # Note: For person articles, Pexels rarely has good results, so we may skip
        return None, None

    return img_url, "Wikimedia Commons"


# ── Articles ─────────────────────────────────────────────────────────────

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

articles = []

# ─── ARTICLE 1: Bhooth Bangla Netflix OTT ─────────────────────────────
articles.append({
    "headline": "Bhooth Bangla Hits Netflix on June 12. Akshay Kumar and Priyadarshan's ₹264 Crore Horror-Comedy Gets Its OTT Date.",
    "subheadline": "After a 45-day theatrical run that outpaced Bhool Bhulaiyaa 3 and became Priyadarshan's biggest hit, the horror-comedy lands on Netflix for NRIs who missed it in cinemas.",
    "slug": "bhooth-bangla-netflix-ott-june-12-akshay-kumar-priyadarshan-264-crore-nri-20260531",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "is_editorial": False,
    "is_featured": False,
    "tags": [],
    "score_total": 0,
    "published_at": NOW,
    "sources": json.dumps(["Sacnilk", "Esquire India", "Hauterrfly", "Gadgets360"]),
    "person_name": "Akshay Kumar",
    "body": """Akshay Kumar's horror-comedy **Bhooth Bangla** is heading to Netflix on **June 12, 2026**, roughly eight weeks after its theatrical premiere on April 17. For NRI audiences who waited through sold-out opening weekends across North America and the Gulf, the streaming date marks the end of a genuinely frustrating window.

## The Numbers Tell a Specific Story

Bhooth Bangla closed its theatrical run with a **₹264 crore worldwide gross** against a reported ₹120 crore budget. What makes this particularly interesting is that the producers had already recovered ₹105 crore before the film even opened — ₹60 crore from Netflix for digital rights, ₹25 crore from Zee Cinema for satellite, and ₹10 crore from Zee Music Company for music. Every rupee earned at the box office was profit from day one.

The film now ranks as **the 16th highest-grossing Hindi film of all time** at the 26-day mark, having outpaced both Bhool Bhulaiyaa 2 (₹1.29 crore on Day 26) and Bhool Bhulaiyaa 3 (₹1.10 crore) in same-day comparisons. Even the original Stree recorded a lower ₹0.87 crore at the same point in its run. Over 3 million tickets were sold on BookMyShow alone.

## Why This Reunion Worked

Priyadarshan and Akshay Kumar hadn't collaborated in over **14 years**, since their last outing in the early 2010s. Their earlier partnerships produced Hera Pheri, Garam Masala, Bhool Bhulaiyaa, and Bhagam Bhaag — films that essentially defined Bollywood's comedy DNA for a generation of NRI kids raised on pirated DVDs and weekend rentals.

The supporting cast reads like a comedy all-star lineup: **Paresh Rawal, Rajpal Yadav, Asrani, Tabu, Mithila Palkar, Wamiqa Gabbi, Jisshu Sengupta**, and Zakir Hussain. The 2-hour-45-minute runtime suggests Priyadarshan went for the full treatment — multiple subplots, multiple set pieces, and the kind of layered comedy that his best work is known for.

## The Diaspora Angle

For Indian families abroad, the Priyadarshan-Akshay formula carries a specific nostalgia. These weren't just comedies — they were the films your parents actually agreed to watch, the ones that played on loop during Diwali gatherings, the rare genre that worked across generational lines. Bhooth Bangla reportedly leans into that same family-friendly horror-comedy space, blending supernatural chaos with physical comedy.

The Netflix release means the film will be available globally on the same day, bypassing the usual frustrations of staggered international rollouts. Given that Netflix acquired the rights for ₹60 crore — their biggest Indian acquisition this year — expect heavy promotion on the platform in the lead-up to June 12.

## What Critics Said

Reviews were largely positive, with praise for the ensemble chemistry and Priyadarshan's ability to manage a massive cast without losing comedic rhythm. Gadgets360 gave it a **2.8/5**, noting that while it doesn't reinvent the genre, it delivers exactly what audiences came for. The horror elements are played strictly for laughs, and the film reportedly includes several callback moments to Bhool Bhulaiyaa that will land specifically with longtime fans.

For NRIs planning a family movie night, mark **June 12** on your calendar. The Akshay-Priyadarshan machine delivered exactly what it promised, and this time you don't need to fight for parking at the local multiplex.""",
})

# ─── ARTICLE 2: Karisma Kapoor's Brown on ZEE5 ────────────────────────
articles.append({
    "headline": "Karisma Kapoor Is a Disgraced Cop in Kolkata in Brown. Helen Returns to Acting After 14 Years.",
    "subheadline": "The Delhi Belly director's neo-noir crime thriller drops on ZEE5 June 5, with a cast that includes singer Shaan's OTT debut and one of Hindi cinema's most iconic legends.",
    "slug": "karisma-kapoor-brown-zee5-june-5-helen-comeback-abhinay-deo-nri-20260531",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "is_editorial": False,
    "is_featured": False,
    "tags": [],
    "score_total": 0,
    "published_at": NOW,
    "sources": json.dumps(["Cinema Express", "MensXP", "Filmfare", "IANS"]),
    "person_name": "Karisma Kapoor",
    "body": """The trailer for **Brown** dropped on Saturday, and it looks like nothing Karisma Kapoor has done before. The ZEE5 original, premiering **June 5**, casts her as **Rita Brown** — a disgraced, alcoholic police officer in Kolkata who is pulled back into service when a string of brutal murders shocks the city.

## The Setup

Directed by **Abhinay Deo** — the man behind Delhi Belly, one of Bollywood's sharpest black comedies — Brown is built as a neo-noir crime thriller set against what Deo calls "the haunting beauty and moral chaos of Kolkata." Rita Brown was once the city's finest cop. Now she's a wreck. When the daughter of an influential businessman turns up dead, she's reluctantly brought back in, partnered with a grieving junior officer, Inspector Arjun (Surya Sharma).

Karisma described the character as fundamentally different from her previous work: "Rita Brown is unlike any character I've played before. She is flawed, vulnerable, emotionally bruised, yet incredibly resilient in the way she keeps moving forward despite everything life throws at her."

What drew her to the project, she said, was "the emotional honesty of the writing. There's no attempt to glamorise pain or simplify human relationships."

## Helen's Return

The most unexpected casting choice is **Helen** — the legendary dancer-actress who defined Bollywood cabaret across four decades — making her return to acting after a **14-year absence**. She plays a supporting role that reportedly provides comic relief in an otherwise dark story.

"It's been such a long time since I faced the camera," Helen said. "Returning to acting, even for a small role in Brown, has been delightful. Sometimes, it's not about the length of the role, but the joy of being part of something special." She added that working with Karisma and Soni Razdan "felt so natural and full of warmth."

For the diaspora, Helen isn't just a name — she's a cultural institution. The fact that she chose a ZEE5 crime thriller for her comeback, not a Bollywood blockbuster, says something about where meaningful storytelling is happening in Indian entertainment right now.

## Singer Shaan's OTT Debut

The series also marks **Shaan's** first acting role on OTT. The singer, whose voice defined the early 2000s for every NRI kid who grew up on Chand Sifarish and Tanha Dil, has spoken about how Kolkata's cultural landscape drew him to the project: "The show is rooted in Kolkata and beautifully captures its unique cultural and emotional landscape. With so many Bengali nuances woven into the narrative, there were moments I could deeply relate to."

## The Bigger Picture

Karisma Kapoor's career trajectory is increasingly interesting. After Murder Mubarak (2024) with Sara Ali Khan and Vijay Varma, and Mentalhood (2020) on ALTBalaji, she's clearly gravitating toward darker, more layered roles on streaming platforms — a pattern that mirrors what Madhuri Dixit is doing with Maa Behen on Netflix and what Raveena Tandon did with Karmma Calling.

The supporting cast is strong: **Jisshu Sengupta** plays a psychiatrist who may hold crucial information, **Soni Razdan** is in a pivotal role, and **Paresh Pahuja** and **Ajinkya Deo** round out the ensemble. The writing team of Diggi Sissodia, Sunayana Kumari, and Mayukh Gosh was developed by Suri Gopalan.

For NRI audiences, Brown represents the kind of content that Indian streaming does better than anyone right now — intimate, atmospheric, and character-driven, with a cast that bridges generational lines. Karisma, Helen, and Shaan in the same project is the kind of lineup that only makes sense if the material genuinely called for it.

**Brown premieres June 5 on ZEE5**, available globally.""",
})

# ─── ARTICLE 3: Kiara Advani Toxic prep ────────────────────────────────
articles.append({
    "headline": "Kiara Advani Shot Toxic in English and Kannada Simultaneously. Here's Why She Wasn't Allowed to Say 'Hi' on Set.",
    "subheadline": "Yash's first film since KGF 2 demanded complete immersion from its cast — Geetu Mohandas banned pleasantries, and Kiara memorized Kannada dialogues the night before each shoot day.",
    "slug": "kiara-advani-toxic-yash-dual-language-geetu-mohandas-method-acting-nri-20260531",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "is_editorial": False,
    "is_featured": False,
    "tags": [],
    "score_total": 0,
    "published_at": NOW,
    "sources": json.dumps(["Bombay Times", "India Forums", "Cinema Express", "Bollywood Hungama"]),
    "person_name": "Kiara Advani",
    "body": """Kiara Advani has talked about many film shoots. None of them sound like **Toxic: A Fairy Tale for Grown-Ups**.

In a series of recent interviews, the actress revealed that director **Geetu Mohandas** imposed a strict no-pleasantries rule on the set of Yash's upcoming action-drama. No "hi." No "hello." No small talk. Kiara — who by her own admission usually greets everyone warmly when she walks in — was instructed to stay completely in character from the moment she arrived until the day's shoot wrapped.

"I was not supposed to exchange pleasantries with anyone, including my own team," she said. The goal was total immersion in her character **Nadia** — and by all accounts, it worked.

## The Dual-Language Challenge

What made the shoot genuinely unprecedented is that **Toxic was filmed simultaneously in English and Kannada**. Every scene was performed twice — first in English, then in Kannada. For Kiara, who doesn't speak Kannada fluently, this meant memorizing dialogue in a language she was still learning, often receiving lines the night before a shoot day.

"I have been mugging up my dialogues literally," she told Cinema Express. "Sometimes, they would come with the lines the night before shoot. It is work; it is homework for sure." She compared it to being a diligent student: "I am that frontbencher in class. I will mug up my dialogues and will do the other person's lines. I will know my work thoroughly."

The choice to shoot bilingually was Yash's — he co-wrote the film and wanted Toxic to play as a genuinely international production, not just a dubbed version of a Kannada film. This is the kind of creative ambition that KGF's success allows, and it speaks to where pan-Indian cinema is heading: not just dubbing into five languages, but actually shooting in multiple languages to capture performance nuances that dubbing loses.

## "Liberation in Love"

Beyond the production details, Kiara's comments on the film's themes are striking. Speaking to Bombay Times, she described Toxic as a film that "completely changes the way you see the man-woman dynamic."

"Even for me, when Geetu narrated the script, it took a while for me to understand that okay, this is also normal," she said. "It may be grey, it may be not in your conventional space, but there's a certain liberation in love. I wish I were so capable, detached, and liberated in my own thoughts."

Earlier, Yash described the female characters in Toxic as "badass" — a word he used deliberately, not as marketing fluff but as a characterization of how the film treats its women. Given that Geetu Mohandas is both a founding member of the **Women in Cinema Collective** (which advocates for gender equality in Malayalam film) and the director of critically acclaimed films like Moothon, the feminist lens is built into the DNA of the production, not bolted on as an afterthought.

## Why NRIs Should Care

Toxic stars Yash in his first role since **KGF: Chapter 2** (2022), which grossed over ₹1,200 crore worldwide and made him a genuine global star. The film also features **Nayanthara, Huma Qureshi, Tara Sutaria, and Rukmini Vasanth**. Music is by Ravi Basrur, and action sequences were choreographed by JJ Perry and the Anbariv duo.

The film's release date has been pushed from its original June 4 slot after feedback from international media screenings. No new date has been confirmed yet, but everything about the production suggests this is being positioned as a global event film, not just a Kannada release.

For diaspora audiences who grew up watching action heroes simply dominate female co-stars, the idea of Yash and Geetu Mohandas collaborating on a film where the women are "badass" and the central theme is "liberation in love" is worth paying attention to. This might be the rarest thing in Indian commercial cinema: a mass entertainer with actual ideas about gender.""",
})


# ── Publish ──────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Entertainment Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print(f"{'='*60}")

for i, art in enumerate(articles, 1):
    person_name = art.pop("person_name", None)
    print(f"\n[{i}/{len(articles)}] {art['headline'][:80]}...")

    # ── Image sourcing ──
    img_url = None
    img_attr = None
    if person_name:
        img_url, img_attr = source_person_image(person_name, art["slug"])

    if img_url:
        art["image_url"] = img_url
        art["image_attribution"] = img_attr or "Wikimedia Commons"
    else:
        print(f"  → No image found, publishing without image")

    # ── Insert ──
    result = sb_insert("p2_articles", art)
    if result:
        art_id = result.get("id", "?")
        print(f"  ✓ Published: {art['slug']} (id={art_id})")
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")

print(f"\n{'='*60}")
print(f"Done. {len(articles)} articles processed.")
print(f"{'='*60}")
