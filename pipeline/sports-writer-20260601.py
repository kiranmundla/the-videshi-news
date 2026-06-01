#!/usr/bin/env python3
"""
The Videshi Sports Writer — 2026-06-01
Two articles:
1. French Open Day 8 quarterfinal roundup
2. Jadeja dropped / India's post-IPL squad reset
"""
import os, sys, json, uuid, re, time, subprocess, urllib.parse
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────────
env_path = os.path.expanduser("~/.env.supabase")
if os.path.exists(env_path):
    for line in open(env_path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v.strip().strip('"').strip("'")

pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

import requests

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── helpers ──────────────────────────────────────────────────────────────
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


def fetch_pexels_image(query, fallback_query=None):
    """Search Pexels for an image using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate image URL returns 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # try GET if HEAD fails
        r = requests.get(url, timeout=10, stream=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct:
            return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=15,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            return None
        content_type = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_r = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true"
            },
            data=r.content,
            timeout=30
        )
        if upload_r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase storage: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {upload_r.status_code} {upload_r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data["id"]
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


def check_skip_list(slug):
    """Check if slug is in the image skip list."""
    skip_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/image-skip-list.json")
    if os.path.exists(skip_path):
        with open(skip_path) as f:
            skip_list = json.load(f)
            return slug in skip_list
    return False


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: French Open Day 8 Quarterfinals
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ARTICLE 1: French Open Quarterfinals")
print("="*60)

article1_slug = "french-open-2026-day-8-fonseca-jodar-mensik-quarterfinals-youngest-qf-lineup-nri"
article1_headline = "Fonseca Is Twenty. Jodar Is Nineteen. Mensik Is Twenty. The French Open Has Never Looked Like This."
article1_subheadline = "Three under-21 players have reached the Roland Garros quarterfinals in the same year for the first time this century. Every top seed but Zverev is gone."

article1_body = """The 2026 French Open lost its way early. Jannik Sinner, the world number one, fell in the second round. Novak Djokovic, the 24-time Grand Slam champion, followed him out the same day. Carlos Alcaraz, the defending champion, had already withdrawn before the tournament began. Coco Gauff, the women's defending champion, went out to Anastasia Potapova. And on Sunday, four-time champion Iga Swiatek lost on her 25th birthday to Marta Kostyuk, 7-5, 6-1.

What is left at Roland Garros is not a diminished field. It is a different tournament — one that belongs to a generation that was playing junior Grand Slams three years ago.

## The Day That Changed the Draw

Sunday's results were not upsets in the traditional sense. They were arrivals.

**João Fonseca**, the 20-year-old Brazilian seeded 28th, beat Casper Ruud — a three-time Roland Garros finalist — 7-5, 7-6(8), 5-7, 6-2. Ruud had the pedigree, the clay-court record, and the experience. Fonseca had the forehand and the nerve. After Ruud clawed back the third set, the Brazilian responded with a dominant fourth, committing fewer unforced errors in the final set than Ruud managed in the third.

**Rafael Jodar**, a 19-year-old Spaniard who was playing college tennis at the University of Virginia a year ago, produced the performance of the day. Down two sets to love against his compatriot Pablo Carreño Busta, Jodar staged a five-set comeback — 4-6, 4-6, 6-1, 6-2, 6-2. He committed only 19 unforced errors across the final three sets. It was a masterclass in mental recalibration.

**Jakub Menšík**, the 20-year-old Czech seeded 26th, outlasted Andrey Rublev in five sets, 6-3, 7-6(6), 4-6, 2-6, 6-3. Rublev, seeded 11th, launched a furious comeback from two sets down before Menšík steadied himself in the decider with precise serving.

Alexander Zverev, the second seed and now the highest-ranked player left in the men's draw by a country mile, handled Jesper De Jong in straight sets, 7-6(3), 6-4, 6-1. His quarterfinal opponent? The 19-year-old Jodar.

## The Quarterfinal Lineup

The men's draw now reads: Zverev (27) vs Jodar (19), Fonseca (20) vs Menšík (20). Three of the four quarterfinalists in the top half are 20 or younger. This has not happened at a Grand Slam in the 21st century.

In the bottom half, Felix Auger-Aliassime and Frances Tiafoe are in action on Monday, joined by the remaining fourth-round matches that will complete the quarterfinal picture.

## An Indian-American Started the Narrative

The generational shift at this French Open began on Day 1, when **Nishesh Basavareddy**, the 20-year-old Indian-American from Carmel, Indiana, stunned seventh seed Taylor Fritz in four sets on Court Suzanne Lenglen. Basavareddy, playing on a wildcard with just one main-draw singles win to his name, served Fritz off the court in the tiebreaks and closed the match with authority in the fourth set.

Basavareddy's run ended in the later rounds, but the tone he set was unmistakable: the French Open belongs to the next generation this year. For the Indian diaspora's tennis community — which has watched the sport grow from Leander Paes and Mahesh Bhupathi's doubles era to Sumit Nagal's singles breakthroughs — Basavareddy represents a new frontier: an Indian-American competing at the highest level on the biggest stage.

## Women's Draw: Sabalenka vs Osaka Under the Lights

On the women's side, Monday night's feature match is one for the ages. World number one **Aryna Sabalenka** faces four-time Grand Slam champion **Naomi Osaka** in the first women's night session match at Roland Garros in three years — ending a streak of 33 consecutive men's matches in the prime-time slot.

The scheduling is significant. French Open organisers have faced persistent criticism for excluding women from the lucrative night session. With Sinner and Djokovic eliminated, the women's match between two of the biggest names in the sport finally gets the spotlight.

Osaka, who has never reached a WTA final on clay, has looked transformed on the surface this year. She reached the fourth round in Paris for the first time in nine attempts.

"YOLO," Osaka said when asked about the night session.

Meanwhile, Kostyuk's 15-match clay-court winning streak — which includes the Madrid Open title and the scalps of both Gauff and Swiatek in Paris — makes the Ukrainian the most dangerous floater in the draw. She faces seventh seed Elina Svitolina, her compatriot, in an all-Ukrainian quarterfinal.

## Where NRI Fans Can Watch

For Indian fans abroad, the French Open streams live on Sony LIV in India and through local broadcast partners — TNT and HBO Max in the US, Eurosport in Europe. Monday's action begins at 3 PM CEST (6:30 PM IST / 6 AM PDT). The Sabalenka-Osaka night session starts at 8:15 PM CEST (11:45 PM IST / 11:15 AM PDT).

This is not the French Open anyone expected. It is the one the sport needed.

---

*Sources: Reuters, Bleacher Report, Associated Press, Sky Sports, Fox Sports*"""

# Image sourcing for Article 1
print("  Sourcing image for Article 1...")
img1_url = fetch_pexels_image("Roland Garros tennis clay court Paris", "French Open red clay tennis")
img1_final = None
img1_attribution = "The Videshi"

if img1_url:
    if validate_image_url(img1_url):
        art1_id_temp = str(uuid.uuid4())
        img1_final = upload_to_supabase_storage(img1_url, f"{art1_id_temp}.jpg")
    else:
        print("  ⚠ Image validation failed")

if not img1_final:
    # Try Wikipedia for Roland Garros
    img1_url = fetch_wikipedia_person_image("Roland Garros (venue)")
    if img1_url and validate_image_url(img1_url):
        art1_id_temp = str(uuid.uuid4())
        img1_final = upload_to_supabase_storage(img1_url, f"{art1_id_temp}.jpg")
        img1_attribution = "Wikimedia Commons"

article1 = {
    "headline": article1_headline,
    "subheadline": article1_subheadline,
    "slug": article1_slug,
    "body": article1_body,
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img1_final,
    "image_attribution": img1_attribution if img1_final else None,
    "sources": json.dumps(["Reuters", "Bleacher Report", "Associated Press", "Sky Sports", "Fox Sports"]),
    "tags": [],
    "is_featured": False,
    "is_editorial": False,
    "score_total": 0
}

art1_id = insert_article(article1)


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Jadeja Dropped / India's Post-IPL Squad Reset
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ARTICLE 2: India's Post-IPL Squad Reset")
print("="*60)

article2_slug = "jadeja-dropped-dubey-brar-maiden-call-up-india-afghanistan-post-ipl-squad-reset-nri"
article2_headline = "Jadeja Has Been Dropped. Axar Too. India's Post-IPL Squad Reset Has Begun."
article2_subheadline = "Harsh Dubey and Gurnoor Brar receive maiden India call-ups. Pant loses the vice-captaincy. KL Rahul is back in the leadership group. The Gill era is being built one selection at a time."

article2_body = """The IPL final was on Sunday night. By Monday morning, the conversation had already shifted. The BCCI announced India's squads for the Afghanistan series — one Test in Mohali starting June 6, three ODIs in Dharamshala, Lucknow, and Chennai — and the selection committee's choices said more about India's future than the series itself.

**Ravindra Jadeja** is not in either squad. Neither is **Axar Patel**. Chief selector Ajit Agarkar was careful with his language. Jadeja has been "rested," he said. The fresh faces of Harsh Dubey and Manav Suthar are "likely to be tested." But the message is clear: India's selectors are looking beyond the veterans who have held the all-rounder slots for the better part of a decade.

## The New Names

**Harsh Dubey**, a left-arm spinner from Vidarbha, and **Gurnoor Brar**, a seam-bowling all-rounder from Punjab, have received their maiden India call-ups. Both will be available across the Test and ODI squads.

Dubey, 24, was the highest wicket-taker in the Ranji Trophy's knockout stages last season. His left-arm orthodox spin and lower-order batting made him Vidarbha's most important player as they reached the semifinal. For selectors looking to build beyond Jadeja and Axar, Dubey is the most natural fit — a like-for-like replacement who is a decade younger.

Brar, 25, has been one of the standout performers in List A cricket for Punjab. A genuine seam-bowling all-rounder in the Hardik Pandya mould, his selection signals the BCCI's desire to find more multi-dimensional cricketers who can contribute with both bat and ball in the middle overs.

**Manav Suthar**, the Rajasthan left-arm spinner who impressed in India A tours, has been added to the Test squad. His ability to turn the ball sharply on Indian surfaces makes him a strong option for Mohali.

## Pant Demoted, Rahul Promoted

The leadership reshuffle is equally telling. **Rishabh Pant** has been stripped of the vice-captaincy and returned to the squad as a specialist wicketkeeper. The BCCI's displeasure with Pant's captaincy decisions during the South Africa Tests — when Gill was injured — has been an open secret. Now it is policy.

**KL Rahul** steps into the vice-captain role. At 34, Rahul's appointment is not about building the future — it is about steadying the present. His calm temperament and experience in pressure situations make him an ideal deputy for Gill, who is still finding his feet as a leader at the highest level.

## Bumrah Rested, Rohit and Pandya Fitness-Dependent

**Jasprit Bumrah** has been rested entirely from both squads. Given the relentless schedule — IPL followed by Afghanistan followed by England in July — the decision is pragmatic. Bumrah's workload management has become a standing item on the selection committee's agenda.

**Rohit Sharma** and **Hardik Pandya** are named in the ODI squad but their availability is subject to fitness clearance from the Centre of Excellence. Neither player was fully fit during the latter stages of the IPL. If Rohit passes the fitness test, the Dharamshala ODI on June 14 would mark his return to ODI cricket alongside **Virat Kohli**, who is confirmed for all three matches.

## What It Means for the Gill Era

Agarkar said something revealing at the press conference: the team, under Gill's captaincy, "wants to give opportunities to youngsters" because there are "still 15-16 months left for the 2027 ODI World Cup."

This is the template. Gill captains the Test. Rohit leads the ODIs if fit, with Gill as his deputy and likely successor. The spin department is being rebuilt around younger players. The pace attack is being managed for the long haul. And the all-rounder slots — which Jadeja and Axar have owned since the 2019 World Cup cycle — are officially up for competition.

For NRI fans who have followed Indian cricket through the Kohli-Rohit axis, this is the moment the axis begins to tilt. The Afghanistan series is not about Afghanistan. It is a casting call for the next era.

## The Schedule

**Test:** India vs Afghanistan, Maharaja Yadavindra Singh International Stadium, New Chandigarh — June 6-10

**1st ODI:** India vs Afghanistan, HPCA Stadium, Dharamshala — June 14, 1:30 PM IST

**2nd ODI:** India vs Afghanistan, Ekana Stadium, Lucknow — June 17, 1:30 PM IST

**3rd ODI:** India vs Afghanistan, MA Chidambaram Stadium, Chennai — June 20, 1:30 PM IST

---

*Sources: CricTracker, The Indian Eye, BCCI, ESPNcricinfo*"""

# Image sourcing for Article 2
print("  Sourcing image for Article 2...")
img2_url = fetch_wikipedia_person_image("Ravindra Jadeja")
img2_final = None
img2_attribution = "Wikimedia Commons"

if img2_url and validate_image_url(img2_url):
    art2_id_temp = str(uuid.uuid4())
    img2_final = upload_to_supabase_storage(img2_url, f"{art2_id_temp}.jpg")

if not img2_final:
    img2_url = fetch_wikipedia_person_image("Shubman Gill")
    if img2_url and validate_image_url(img2_url):
        art2_id_temp = str(uuid.uuid4())
        img2_final = upload_to_supabase_storage(img2_url, f"{art2_id_temp}.jpg")

if not img2_final:
    img2_url = fetch_pexels_image("India cricket team national", "cricket stadium India")
    img2_attribution = "The Videshi"
    if img2_url and validate_image_url(img2_url):
        art2_id_temp = str(uuid.uuid4())
        img2_final = upload_to_supabase_storage(img2_url, f"{art2_id_temp}.jpg")

article2 = {
    "headline": article2_headline,
    "subheadline": article2_subheadline,
    "slug": article2_slug,
    "body": article2_body,
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img2_final,
    "image_attribution": img2_attribution if img2_final else None,
    "sources": json.dumps(["CricTracker", "The Indian Eye", "BCCI", "ESPNcricinfo"]),
    "tags": [],
    "is_featured": False,
    "is_editorial": False,
    "score_total": 0
}

art2_id = insert_article(article2)


# ── Update image URLs with actual article IDs ─────────────────────────
def update_image_for_article(art_id, current_url, attribution):
    """Re-upload image with the article ID as filename for consistency."""
    if not art_id or not current_url:
        return
    try:
        # Download from current URL
        r = requests.get(current_url, timeout=15,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            return
        content_type = r.headers.get("Content-Type", "image/jpeg")
        filename = f"{art_id}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_r = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true"
            },
            data=r.content,
            timeout=30
        )
        if upload_r.status_code in (200, 201):
            final_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            # Update the article
            patch_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art_id}",
                headers=HEADERS,
                json={"image_url": final_url, "image_attribution": attribution},
                timeout=15
            )
            if patch_r.status_code in (200, 204):
                print(f"  ✓ Image updated for article {art_id}")
            else:
                print(f"  ⚠ Patch failed: {patch_r.status_code}")
    except Exception as e:
        print(f"  ⚠ Image update error: {e}")

if art1_id and img1_final:
    update_image_for_article(art1_id, img1_final, img1_attribution)
if art2_id and img2_final:
    update_image_for_article(art2_id, img2_final, img2_attribution)


# ── Summary ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SPORTS WRITER SUMMARY")
print("="*60)
results = []
if art1_id:
    results.append(f"✓ Article 1: {article1_headline[:70]}... → {art1_id}")
else:
    results.append(f"✗ Article 1: FAILED")
if art2_id:
    results.append(f"✓ Article 2: {article2_headline[:70]}... → {art2_id}")
else:
    results.append(f"✗ Article 2: FAILED")

for r in results:
    print(r)

print(f"\nTotal published: {sum(1 for r in results if r.startswith('✓'))}/2")
