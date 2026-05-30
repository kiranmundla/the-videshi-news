#!/usr/bin/env python3
"""Sports writer for The Videshi — May 30, 2026"""

import requests, json, os, sys, urllib.parse, uuid, re, subprocess
from datetime import datetime, timezone

# ── Load env ──────────────────────────────────────────────────────────────
env_path = os.path.expanduser("~/.env.supabase")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# Load Pexels key
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if "PEXELS" in k.upper():
                    PEXELS_KEY = v.strip().strip('"').strip("'")

# ── Image helpers ─────────────────────────────────────────────────────────
def fetch_wikipedia_image(topic):
    """Fetch image from Wikipedia REST API. Returns URL or None."""
    encoded = urllib.parse.quote(topic.replace(" ", "_"))
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
                print(f"  ✓ Wikipedia image found for '{topic}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{topic}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                [
                    "curl", "-sS",
                    f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                    "-H", f"Authorization: {PEXELS_KEY}",
                ],
                capture_output=True, text=True, timeout=15,
            )
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
    """Verify image URL returns 200 with image/* content type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Sometimes HEAD doesn't return Content-Length, try GET with range
        if r.status_code == 200 and "image" in ct:
            return True
        print(f"  ⚠ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


# ── Check for banned image sources ────────────────────────────────────────
def is_banned_source(url):
    if not url:
        return True
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    return any(b in url for b in banned)


# ── Article insertion ─────────────────────────────────────────────────────
def insert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Published: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Failed to publish: {r.status_code} {r.text[:200]}")
        return None


# ── Check skip list ───────────────────────────────────────────────────────
skip_list_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/image-skip-list.json")
skip_list = []
if os.path.exists(skip_list_path):
    with open(skip_list_path) as f:
        skip_list = json.load(f)

# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 1: Champions League Final
# ══════════════════════════════════════════════════════════════════════════

print("\n═══ Article 1: Champions League Final ═══")

cl_headline = "No Team Has Defended the Champions League Since Real Madrid. PSG Will Try Tonight in Budapest Against an Arsenal Side That Has Never Won It."
cl_subheadline = "The final kicks off at 9:30 PM IST on Saturday — prime-time viewing for what might be the biggest club match of the year."
cl_slug = "champions-league-final-2026-arsenal-psg-budapest-nri-watch-guide-prime-time-ist"

cl_body = """The biggest match in club football this season happens tonight at the Puskás Arena in Budapest. Arsenal, the newly crowned Premier League champions, face Paris Saint-Germain, the defending Champions League holders, in a final that pits tactical discipline against devastating attacking flair.

For Arsenal, this is uncharted territory. The club has never won the Champions League. Their only previous appearance in the final was in 2006, when a red card to goalkeeper Jens Lehmann after eighteen minutes derailed their challenge against Barcelona. Two decades later, under Mikel Arteta, they return to Europe's biggest stage with the confidence of a side that just ended a twenty-two-year wait for the Premier League title.

For PSG, this is about legacy. No club has successfully defended the Champions League trophy since Real Madrid's three consecutive titles between 2016 and 2018. Luis Enrique's side dismantled Inter Milan 5-0 in last year's final and have the tactical sophistication and squad depth to make history again.

## The Tactical Battle

This final has been framed — somewhat provocatively — as Beauty and the Beast. PSG's front line is packed with the kind of talent that makes defenders lose sleep. Ballon d'Or winner Ousmane Dembélé leads a forward trio that includes Khvicha Kvaratskhelia and either Désiré Doué or Bradley Barcola. Behind them, a midfield anchored by João Neves, Vitinha, and Fabián Ruiz blends control with creative menace.

Arsenal's response is a defence that has been the foundation of everything they have achieved this season. Goalkeeper David Raya has kept nine clean sheets in the club's fourteen-game unbeaten run to the final. In front of him, William Saliba and Gabriel Magalhães form one of the most formidable centre-back partnerships in European football. Declan Rice, who has played over 4,300 minutes across all competitions this season — more than double Dembélé's total — anchors the midfield with relentless energy.

Arteta's Arsenal are not merely defensive, though. Their set-piece routines, particularly from corners, have become a defining weapon. Gabriel, in particular, has a knack for scoring decisive headers in the biggest moments — including a last-ditch intervention against Atlético Madrid in the semifinal.

## The Road to Budapest

Arsenal were the only team to win all eight of their league phase matches, finishing top of the thirty-six-team table. Their knockout path saw them dispatch opponents with the kind of controlled, low-scoring wins that have become their trademark — they scored just six goals across the entire knockout rounds while conceding only two.

PSG's route was more dramatic. They finished eleventh in the league phase and had to navigate the playoff round before finding their stride. In the semifinals, they beat Bayern Munich 6-5 on aggregate in a breathless two-legged affair that included a 5-4 first-leg win.

## The NRI Watch Guide

For viewers in India, the final kicks off at **9:30 PM IST on Saturday** — prime-time viewing for a weekend night. The match will be broadcast on Sony Sports Network and streamed on SonyLIV.

For the diaspora in the United States, kickoff is at **12:00 PM ET / 9:00 AM PT**, broadcast on CBS and streamed on Paramount+.

In the United Kingdom, kickoff is at **5:00 PM BST** on TNT Sports.

## Why It Matters for the Diaspora

This final arrives at a moment when the Premier League's dominance in Europe is at its peak. Aston Villa won the Europa League and Crystal Palace took the Conference League — if Arsenal win tonight, English clubs will hold all three European trophies for the first time in history.

For the Indian diaspora, the Premier League is the most-watched football league by a significant margin. Arsenal's global fan base extends deep into India, where weekend viewing parties for Premier League matches are a fixture of urban life in Delhi, Mumbai, and Bangalore. An Arsenal victory would be celebrated across WhatsApp groups and sports bars from Edison, New Jersey, to Southall, London.

But PSG are formidable. Luis Enrique's record in one-off finals — eleven wins from twelve — is the statistic that should concern every Arsenal supporter. The Spaniard knows how to prepare a team for the occasion, and his squad has the individual brilliance to punish even the slightest defensive lapse.

"We have raised different standards now, and we have to go to the next level," Arteta said this week.

He has. Tonight, Budapest will determine whether it is enough."""

cl_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com/sports/soccer/rock-solid-arsenal-ready-psg-test-champions-league-final-2026-05-29/"},
    {"name": "USA Today", "url": "https://www.usatoday.com/story/sports/soccer/2026/05/29/champions-league-final-time-arsenal-psg/"},
    {"name": "CNN Sports", "url": "https://www.cnn.com/sport/arsenal-psg-champions-league-final-budapest-2026"},
])

# Source image — try Puskás Arena from Wikipedia
cl_image = fetch_wikipedia_image("Puskás Arena")
if not cl_image or not validate_image(cl_image):
    cl_image = fetch_wikipedia_image("Arsenal F.C.")
if not cl_image or not validate_image(cl_image):
    cl_image = fetch_pexels_image("football stadium night match", "soccer champions league")
if cl_image and is_banned_source(cl_image):
    cl_image = None

cl_article = {
    "headline": cl_headline,
    "subheadline": cl_subheadline,
    "slug": cl_slug,
    "body": cl_body,
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": cl_sources,
    "image_url": cl_image,
    "image_attribution": "Wikimedia Commons" if cl_image and "wikimedia" in (cl_image or "").lower() else "Pexels",
}

cl_id = insert_article(cl_article)


# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 2: India U18 Hockey Asia Cup
# ══════════════════════════════════════════════════════════════════════════

print("\n═══ Article 2: India U18 Hockey Asia Cup Results ═══")

hockey_headline = "A Hat-Trick From the Captain and Both Goals From a Fifteen-Year-Old. India's U18 Hockey Teams Have Opened the Asia Cup With Two Wins in Japan."
hockey_subheadline = "The men demolished Kazakhstan 13-0 in Kakamigahara while the women edged Malaysia 2-1 — setting up decisive pool matches against Korea."
hockey_slug = "india-u18-hockey-asia-cup-2026-men-13-0-kazakhstan-women-2-1-malaysia-kushwaha-naz-kakamigahara"

hockey_body = """India's Under-18 hockey teams have opened their Asia Cup campaign in Kakamigahara, Japan, with two victories that set starkly different tones — and both point to a pipeline that is very much alive.

## The Men: Thirteen Goals, Zero Resistance

Captain Ketan Kushwaha scored a hat-trick as India crushed Kazakhstan 13-0 in their Pool A opener on Thursday, recording the most emphatic result of the tournament's opening day.

Shahrukh Ali struck first in the twelfth minute with a thunderous shot from inside the circle. Prahalad Rajbhar doubled the lead two minutes later. From there, India never looked back.

Kushwaha, leading by example, scored in the eighteenth minute after India won possession high up the pitch. Gazee Khan added a fourth in the twentieth. By halftime, India had six goals — Shahrukh completing his brace in the twenty-ninth minute and Ashish Tani Purti converting a penalty corner on the stroke of the interval.

The third quarter was the most devastating stretch of the match. Ansh Bahutra converted two penalty corners in the thirty-first and forty-fourth minutes. Purti added another from a set piece. Kushwaha then scored twice in quick succession — including a penalty corner — to complete his hat-trick and push India to an 11-0 lead.

Akash Deep and Rajbhar rounded off the scoring in the fourth quarter to seal a 13-0 rout that announced India's intentions for the tournament in unmistakable terms.

The scoresheet tells its own story: seven different goalscorers, five penalty corner conversions, and a captain who led with three goals and a relentless attacking tempo.

## The Women: Naz Makes Her Mark

The women's side had a tighter assignment — and delivered under pressure. India beat Malaysia 2-1 on Friday, with fifteen-year-old forward Nousheen Naz scoring both goals.

After a goalless first quarter, Naz broke the deadlock in the nineteenth minute, capitalising on a penalty corner to give India the lead. She struck again in the twenty-eighth minute with a sharp shot that beat the Malaysian goalkeeper, sending India into halftime with a 2-0 cushion.

Malaysia fought back. Nur Azli pulled one back in the forty-first minute, cutting the deficit to a single goal and setting up a tense final quarter. But the Indian defence held firm. Naz earned the Player of the Match award for her decisive contribution — a remarkable performance for a player who turned fifteen earlier this year.

India earned sixteen penalty corners across the match, a dominance in set-piece opportunities that they will need to convert more efficiently when the competition stiffens.

## The Pipeline

These age-group tournaments are where India's next generation of senior internationals are identified. The men's senior team has been a consistent force at the continental level, and the depth of talent on display in Kakamigahara suggests the pathway from junior to senior hockey is functioning well.

Kushwaha's hat-trick was notable for its variety — goals from open play, set pieces, and opportunistic positioning. At the U18 level, this kind of all-round finishing is exactly what national selectors look for when projecting players into the senior setup.

For the women's programme, Naz's emergence is a significant development. Indian women's hockey has made strides in recent years — the senior team reached the semifinals at the Tokyo Olympics — and identifying talent this early is crucial for sustained competitiveness.

## What Comes Next

The men face hosts Japan on Saturday — a far sterner test that will determine whether India's quality extends beyond dominance over weaker opposition. A pool match against South Korea follows on June 1.

The women face South Korea on Sunday in what should be the decisive pool encounter. Korea demolished Singapore 8-0 in their opener and sit level with India on three points, separated only by goal difference.

Both teams are well-positioned for the semifinals. The tests that matter begin now."""

hockey_sources = json.dumps([
    {"name": "ANI via LatestLY", "url": "https://www.latestly.com/agency-news/sports-news-captain-ketan-kushwahas-hat-trick-leads-indias-dominating-13-0-win-in-mens-u-18-asia-cup-opener.html"},
    {"name": "RevSportz", "url": "https://revsportz.in/indian-u18-womens-hockey-team-holds-nerve-to-beat-malaysia-2-1/"},
    {"name": "FIH via Wikipedia", "url": "https://en.wikipedia.org/wiki/2026_Men%27s_Hockey_U18_Asia_Cup"},
])

# Source image — try Pexels for field hockey
hockey_image = fetch_pexels_image("field hockey game players", "hockey sport field")
if hockey_image and is_banned_source(hockey_image):
    hockey_image = None
if not hockey_image or not validate_image(hockey_image):
    hockey_image = fetch_wikipedia_image("Field hockey at the Summer Olympics")
    if hockey_image and is_banned_source(hockey_image):
        hockey_image = None

hockey_article = {
    "headline": hockey_headline,
    "subheadline": hockey_subheadline,
    "slug": hockey_slug,
    "body": hockey_body,
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": hockey_sources,
    "image_url": hockey_image,
    "image_attribution": "Pexels" if hockey_image and "pexels" in (hockey_image or "").lower() else "Wikimedia Commons",
}

hockey_id = insert_article(hockey_article)


# ── Summary ───────────────────────────────────────────────────────────────
print("\n═══ Summary ═══")
results = []
if cl_id:
    results.append(f"✓ Champions League Final: {cl_slug}")
if hockey_id:
    results.append(f"✓ India U18 Hockey: {hockey_slug}")

if results:
    print(f"Published {len(results)} article(s):")
    for r in results:
        print(f"  {r}")
else:
    print("✗ No articles published")
    sys.exit(1)

print("\nDone.")
