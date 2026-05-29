#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-05-29 batch."""

import json, os, sys, time, uuid, re
from datetime import datetime, timezone
import requests, urllib.parse

# ── Supabase config ──────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip('"').strip("'")
if not PEXELS_KEY:
    pexels_env2 = os.path.expanduser("~/.env.pexels")
    if os.path.exists(pexels_env2):
        for line in open(pexels_env2):
            if line.startswith("PEXELS_API_KEY="):
                PEXELS_KEY = line.strip().split("=", 1)[1].strip('"').strip("'")
print(f"Pexels key loaded: {'yes' if PEXELS_KEY else 'no'}")

# ── Image helpers ────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            cmd = [
                "curl", "-sS",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                "-H", f"Authorization: {PEXELS_KEY}",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Check that image URL returns HTTP 200 and is > 5KB."""
    if not url:
        return False
    try:
        # Use GET with stream to get actual headers; Wikimedia sometimes 429s on HEAD
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        r.close()
        if r.status_code == 200 and "image" in ct:
            return True
        print(f"  ⚠ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase article-images bucket. Returns public URL or None."""
    try:
        r = requests.get(image_url, timeout=15,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed: status={r.status_code}, size={len(r.content)}")
            return None

        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": ct,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


# ── Supabase insert ──────────────────────────────────────────────
def publish_article(article):
    """Insert article into p2_articles."""
    article["id"] = str(uuid.uuid4())
    article["status"] = "published"
    article["published_at"] = datetime.now(timezone.utc).isoformat()
    article["category"] = "sports"
    article["vertical"] = "sports"
    article["urgency"] = "medium"
    # source_pipeline column doesn't exist, skip it

    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=20,
    )
    if resp.status_code in (200, 201):
        result = resp.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id", article["id"])
        print(f"  ✓ Published: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Publish failed ({resp.status_code}): {resp.text[:300]}")
        return None


# ── Articles ─────────────────────────────────────────────────────

articles = []

# ─── ARTICLE 1: Sumit Antil World Record ──────────────────────────
print("\n=== Article 1: Sumit Antil World Record ===")

antil_body = """Sumit Antil threw the javelin 74.82 metres at the Indian Open International Para Athletics Championships in Bengaluru this week, breaking his own world record in the F64 category by more than a metre and a half.

## The Throw That Rewrote the Record Books

The distance itself tells only part of the story. Antil's previous world record of 73.29 metres, set at the 2022 Asian Para Games in Hangzhou, had seemed like a ceiling for the F64 classification. Athletes in this category compete with below-knee amputations or equivalent impairments. For an athlete who lost his left leg below the knee in a motorcycle accident at seventeen, every centimetre of improvement requires recalibrating mechanics that able-bodied throwers take for granted.

At the Kanteerava Stadium, Antil's winning margin was staggering. The silver medallist, Maharashtra's Sandip Sargar, finished at 61.88 metres — nearly thirteen metres behind. Rajasthan's Sandeep took bronze. It was not a competition so much as a demonstration.

## A Career Built on Defying Limits

Antil's trajectory since his accident in 2015 reads like a masterclass in reinvention. Within three years of taking up para-javelin, he was competing internationally. By 2021, he had won Paralympic gold at Tokyo with a then-world-record 68.55 metres, breaking his own record three times during the competition itself. At the 2024 Paris Paralympics, he defended his title. He now holds two Paralympic gold medals, three World Para Athletics Championship golds, and the Asian Para Games record.

What makes his latest throw remarkable is timing. At twenty-eight, Antil is in his physical prime but also at the stage where incremental gains become harder. To add 1.53 metres to a world record at this level is the equivalent of a sprinter dropping half a second from a world-record hundred metres. It does not happen through minor adjustments.

## What It Means for Indian Para-Athletics

India's para-athletics programme has quietly become one of the country's most consistent medal factories. At the Paris 2024 Paralympics, India won seven athletics medals. Avani Lekhara, Mariyappan Thangavelu, and Antil himself have become household names in a country where the word "para" was once an afterthought appended to sports coverage.

The Indian Open International Para Athletics Championships, now in its eighth edition, has grown from a domestic meet into a genuinely competitive international event. Athletes from several countries participated in Bengaluru this week, though Antil's dominance made the F64 javelin feel like a solo exhibition.

## The Diaspora Angle

For NRIs who grew up watching Neeraj Chopra transform India's relationship with javelin, Antil's story offers a parallel that is in some ways more profound. Chopra made India believe an Indian could be the best javelin thrower in the world. Antil has been the best in his classification for half a decade, with less fanfare and fewer endorsement deals.

The gap between para-sport and mainstream sport in Indian media remains wide. Antil does not trend on social media after every competition. He does not feature in IPL ads. But his record — two Paralympic golds, three World golds, and now a world record that may stand for years — places him among the most decorated Indian athletes of any generation.

## What Comes Next

The 2028 Los Angeles Paralympics is the obvious target. Antil would be thirty and likely still improving. More immediately, the Asian Para Games and World Para Athletics Championships in the coming cycle will give him chances to compete against whatever field the world assembles.

At 74.82 metres, the question is no longer whether anyone in F64 can challenge Sumit Antil. It is whether Sumit Antil has found his ceiling, or whether Bengaluru was just another checkpoint on the way to something even more extraordinary.

*Sources: Livemint, The Bridge, DevDiscourse, LatestLY*"""

antil_img = fetch_wikipedia_person_image("Sumit Antil")
if not antil_img:
    antil_img = fetch_wikipedia_person_image("Sumit Antil (athlete)")
# If Wikipedia is rate-limiting, use the known image URL directly
if antil_img and not validate_image(antil_img):
    print("  Retrying Sumit Antil image after delay...")
    time.sleep(3)
    if not validate_image(antil_img):
        # Use a specific Pexels image for javelin
        antil_img = fetch_pexels_image("javelin throw athletics stadium", "para athletics javelin")
if not antil_img:
    antil_img = fetch_pexels_image("javelin throw athletics stadium", "para athletics javelin")

antil_slug = "sumit-antil-74-82m-javelin-world-record-f64-bengaluru-indian-open-para-athletics-20260529"
antil_final_img = None
if antil_img and validate_image(antil_img):
    antil_final_img = upload_to_supabase_storage(antil_img, f"{antil_slug}.jpg")

articles.append({
    "headline": "Sumit Antil Threw 74.82 Metres in Bengaluru. That Is a World Record by a Metre and a Half.",
    "subheadline": "The two-time Paralympic champion broke his own F64 javelin mark at the Indian Open Para Athletics Championships. The silver medallist finished nearly thirteen metres behind.",
    "body": antil_body,
    "slug": antil_slug,
    "image_url": antil_final_img,
    "image_attribution": "Wikimedia Commons" if antil_img and "wiki" in (antil_img or "").lower() else "The Videshi",
    "sources": json.dumps(["Livemint", "The Bridge", "DevDiscourse", "LatestLY"]),
})


# ─── ARTICLE 2: Randhir Singh Obituary ──────────────────────────
print("\n=== Article 2: Randhir Singh Tribute ===")

randhir_body = """Raja Randhir Singh, the five-time Olympian, Asian Games gold medallist, and one of the most influential figures in Indian and Asian sports administration, has died at seventy-nine. The International Olympic Committee ordered its flag lowered to half-mast at its Lausanne headquarters for three days.

## The Shooter Who Became the Architect

Randhir Singh's biography spans two distinct careers, both exceptional. As a competitive shooter, he represented India at five consecutive Olympic Games — a feat that remains nearly unmatched in Indian sport. At the 1978 Asian Games in Bangkok, he won India's first-ever shooting gold medal, a breakthrough that helped establish the discipline as a legitimate pathway to medals for Indian athletes.

But it was his second career, in sports administration, that would define his lasting legacy. Singh served as Secretary General of the Indian Olympic Association for over three decades. He was India's representative on the International Olympic Committee. And in 2024, he became the first Indian to be elected President of the Olympic Council of Asia, the continental body that oversees the Asian Games.

## Building the Machine

The Indian sports system that exists today — imperfect, occasionally dysfunctional, but vastly more professional than what existed forty years ago — owes a significant debt to administrators like Randhir Singh. He was instrumental in India's bid to host the 2010 Commonwealth Games in Delhi, a project that was marred by corruption scandals and construction delays but ultimately delivered an event that India hosted on the world stage.

His defenders argue that Singh understood a truth about Indian sport that idealists often missed: infrastructure precedes performance. Without stadiums, training centres, and institutional credibility, talent alone cannot produce sustained medal counts. His critics counter that decades of administrative continuity without reform enabled the very governance problems that have plagued Indian sport.

The truth, as with most institution-builders, is probably both.

## The Royal and the Republican

Singh was born into the Patiala royal family, descendants of the Maharajas who were among India's earliest patrons of sport. His grandfather, Maharaja Bhupinder Singh, captained India's cricket team and built what was then one of Asia's finest cricket grounds. The family's relationship with sport was not casual — it was constitutional.

That lineage gave Randhir Singh access and influence from the start. It also exposed him to criticism that his administrative career was a product of privilege rather than merit. But five Olympic appearances suggest the privilege came with genuine competence, at least on the shooting range.

## What NRIs Should Know

For the Indian diaspora, Randhir Singh represents a generation of sports administrators who operated in a world that no longer exists — one where Olympic committee elections were decided in smoke-filled rooms and continental sports politics ran on personal relationships rather than broadcast deals.

That world produced some of India's most important sporting infrastructure. It also produced some of its most persistent governance failures. Singh navigated both with a skill that earned him IOC Honorary Member status and the respect of administrators across Asia.

His death comes at a moment when Indian sport is undergoing its most significant generational transition. The IPL has professionalised cricket economics. Olympic sports have produced genuine world champions in javelin, wrestling, and shooting — the very discipline Singh once dominated. The question for the next generation of administrators is whether they can build on what Singh's generation created without inheriting its limitations.

## The IOC's Tribute

In its statement, the IOC described Singh as a man who "dedicated his life to the Olympic Movement and the advancement of sport in Asia." The three-day half-mast protocol is reserved for members who made sustained contributions to the Olympic system. Singh's inclusion in that category is not a courtesy — it reflects decades of institutional engagement that few Indian administrators have matched.

He is survived by his family, including members who continue to be involved in Indian shooting and sports governance. The dynasty continues, even as the founder exits.

*Sources: International Olympic Committee, LatestLY, The Daily Jagran, Swadesi, ChessBase India (via EIN Presswire)*"""

randhir_img = fetch_wikipedia_person_image("Randhir Singh (sports administrator)")
if not randhir_img:
    randhir_img = fetch_wikipedia_person_image("Raja Randhir Singh")

randhir_slug = "randhir-singh-dies-79-five-time-olympian-ioc-oca-president-shooting-gold-india-20260529"
randhir_final_img = None
if randhir_img and validate_image(randhir_img):
    randhir_final_img = upload_to_supabase_storage(randhir_img, f"{randhir_slug}.jpg")

articles.append({
    "headline": "Randhir Singh Is Dead at Seventy-Nine. The IOC Flag Flew at Half-Mast for Three Days.",
    "subheadline": "India's first Asian Games shooting gold medallist, five-time Olympian, and longtime Olympic Council of Asia president shaped Indian sport for four decades. The institution he built will outlast the man.",
    "body": randhir_body,
    "slug": randhir_slug,
    "image_url": randhir_final_img,
    "image_attribution": "Wikimedia Commons" if randhir_img and "wiki" in (randhir_img or "").lower() else "The Videshi",
    "sources": json.dumps(["International Olympic Committee", "LatestLY", "The Daily Jagran", "Swadesi"]),
})


# ─── ARTICLE 3: IPL to India — UK Summer Tour Selection ──────────
print("\n=== Article 3: IPL to India T20I UK Tour ===")

uk_tour_body = """The IPL 2026 final is on Sunday. India's next assignment is a fortnight away: two T20Is in Ireland on June 26 and 28, followed by five T20Is in England from July 1 to 11. The selectors will meet within days of the final, and for the first time in years, the IPL has produced a cluster of uncapped players who are genuinely difficult to ignore.

## The Names That Changed

Every IPL season produces highlights. Not every season produces selection-grade evidence. The difference this year is that several breakout performers have done it consistently, across enough matches, against enough quality bowling, to shift the conversation from "impressive cameo" to "serious India contender."

**Kartik Tyagi** is the most compelling comeback story. The fast bowler went unsold in the 2025 auction. Kolkata Knight Riders picked him up for thirty lakh rupees — a base-price afterthought. He has repaid them with eighteen wickets in thirteen matches, including best figures of three for twenty-two against Rajasthan Royals. His average of 24.61 and strike rate of 15.67 would be respectable in any season. In a campaign where batting totals have routinely crossed two hundred, they represent genuine wicket-taking impact.

What changed was not Tyagi's pace — he still touches the high 140s — but his control. He has hit better lengths this season, attacked the pitch harder, and looked physically sharper than at any point since his early promise with Rajasthan Royals in 2020-21. England's responsive surfaces would suit his skillset.

**Ayush Mhatre** batted like a player who did not know he was supposed to be nervous. The eighteen-year-old Chennai Super Kings opener scored 201 runs in six innings at a strike rate of 177.87 before a hamstring injury ended his season. For context, his powerplay scoring rate was higher than any CSK opener since the franchise's inception. If he is fit, the selectors will find it hard to leave him out of the touring party. If he is not, the England series gives him a clear next target.

**Kartik Sharma** filled a profile India's selectors have been hunting for years: a left-handed wicketkeeper-batter who can play in the middle order and attack spin. His 295 runs for CSK included a composed fifty-four not out against Mumbai Indians and a valuable seventy-one against Lucknow. He is not a finished international product, but the Ireland leg — where India traditionally tests unproven names — is exactly where such players earn their chance.

**Prince Yadav** had the misfortune of bowling for a poor Lucknow Super Giants side. He had the talent to look like the one bowler with rhythm and clarity regardless. Sixteen wickets in thirteen matches, hitting hard lengths, operating effectively in the middle and death overs. India's pace stocks are deep, but discipline like Yadav's has a way of finding its level.

## The Sooryavanshi Question

And then there is Vaibhav Sooryavanshi, who is simultaneously the most talented and the most complicated selection case of the lot. The fifteen-year-old Rajasthan Royals opener has 680 runs and sixty-five sixes in IPL 2026, both numbers that exist in territory no Indian has previously occupied.

He has already been named in the India A squad for the Sri Lanka tri-series in June, which suggests the selectors are channeling him through the development pathway. That is probably correct. But the England series in July is a different question. If Sooryavanshi finishes the IPL final — should Rajasthan get there — with numbers that would embarrass most international careers, the selectors will face an uncomfortable choice between protocol and evidence.

## The Diaspora Calendar

For NRIs in the UK, the timing is perfect. India will be in Dublin on June 26 and 28, then in England for five T20Is from July 1 to 11, with matches likely at venues including The Oval, Edgbaston, and Old Trafford. This is the summer India tour that British-Indians mark on their calendars months in advance.

The added intrigue this year is that several of the players who could make the squad are completely new names. NRIs who have been watching the IPL will know Sooryavanshi and Mhatre. Those who have not will be introduced to a generation of Indian cricketers who play T20 cricket with an aggression and clarity that previous generations did not possess.

## What the Selectors Will Weigh

India's selection committee, chaired by Ajit Agarkar, faces the perennial IPL problem: distinguishing tournament form from international readiness. Tyagi's case is strongest because pace bowlers with his trajectory tend to translate directly. Mhatre's is strongest in terms of pure ceiling. Sooryavanshi's is strongest in terms of public excitement, which the selectors will try to resist but cannot entirely ignore.

The squad announcement is expected within a week of the IPL final. For at least three of these five players, the summer of 2026 will mark the beginning of their India careers. For NRIs planning their summer viewing, that makes the Ireland and England series appointment television.

*Sources: Sports Yaari, CricTracker, Reuters, Cricbuzz*"""

# For this article, use a cricket-specific Pexels image since it's about multiple players
uk_tour_img = fetch_pexels_image("cricket batsman T20 stadium India", "cricket fast bowler stadium")

uk_tour_slug = "ipl-2026-breakout-stars-india-t20i-squad-uk-tour-ireland-england-tyagi-mhatre-sooryavanshi-20260529"
uk_tour_final_img = None
if uk_tour_img and validate_image(uk_tour_img):
    uk_tour_final_img = upload_to_supabase_storage(uk_tour_img, f"{uk_tour_slug}.jpg")

articles.append({
    "headline": "Five IPL Performers Are Knocking on India's Door. The UK Summer Tour Starts in Four Weeks.",
    "subheadline": "Kartik Tyagi went unsold last year. Ayush Mhatre is eighteen. Sooryavanshi is fifteen. The selectors meet after the final, and this time the evidence is hard to argue with.",
    "body": uk_tour_body,
    "slug": uk_tour_slug,
    "image_url": uk_tour_final_img,
    "image_attribution": "The Videshi",
    "sources": json.dumps(["Sports Yaari", "CricTracker", "Reuters", "Cricbuzz"]),
})


# ── Publish all ──────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Publishing {len(articles)} articles...")
print(f"{'='*60}")

published = 0
for i, art in enumerate(articles, 1):
    print(f"\n--- Article {i}/{len(articles)} ---")
    art_id = publish_article(art)
    if art_id:
        published += 1
        # If we uploaded an image, patch the article
        if art.get("image_url"):
            print(f"  Image: {art['image_url'][:60]}...")
    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
print(f"{'='*60}")
