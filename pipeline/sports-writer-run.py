#!/usr/bin/env python3
"""Sports writer - June 6, 2026 run"""

import json, os, sys, time, re, uuid
import requests
import subprocess
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Load Pexels key
pexels_path = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = ""
if os.path.exists(pexels_path):
    with open(pexels_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                if 'PEXELS' in key.upper():
                    PEXELS_KEY = val.strip().strip('"').strip("'")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Use thumbnail.source AS-IS (330px) - do NOT modify
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    import urllib.parse
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a relevant image."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def validate_image_url(url):
    """Validate that URL returns a real image > 5KB."""
    if not url:
        return False
    try:
        r = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code} %{content_type} %{size_download}",
             "-L", "--max-time", "10", url],
            capture_output=True, text=True, timeout=15
        )
        parts = r.stdout.strip().split()
        if len(parts) >= 3:
            status = parts[0]
            content_type = parts[1]
            size = float(parts[2])
            if status == "200" and "image" in content_type and size > 5000:
                print(f"  ✓ Image validated: {status}, {content_type}, {size:.0f} bytes")
                return True
            else:
                print(f"  ✗ Image validation failed: {status}, {content_type}, {size:.0f} bytes")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Published: {data[0].get('headline', 'unknown')}")
            return True
        elif isinstance(data, dict):
            print(f"  ✓ Published: {data.get('headline', 'unknown')}")
            return True
    print(f"  ✗ Insert failed: {r.status_code} - {r.text[:200]}")
    return False


# ============================================================
# ARTICLE 1: Manav Suthar Test Debut Profile
# ============================================================

print("\n" + "="*60)
print("ARTICLE 1: Manav Suthar Test Debut")
print("="*60)

# Image sourcing: Try Wikipedia for Manav Suthar, then Commons, then Pexels
print("\nSourcing image...")
img1_url = None
img1_caption = ""
img1_attribution = ""

# Wikipedia
img1_url = fetch_wikipedia_person_image("Manav Suthar")
if img1_url and validate_image_url(img1_url):
    img1_caption = "Manav Suthar, India's Test cap No. 319"
    img1_attribution = "Wikimedia Commons"
else:
    img1_url = None

# Wikimedia Commons
if not img1_url:
    commons = fetch_wikimedia_commons_images("Manav Suthar cricketer India")
    for c in commons:
        if validate_image_url(c["url"]):
            img1_url = c["url"]
            img1_caption = "Manav Suthar, India's Test cap No. 319"
            img1_attribution = "Wikimedia Commons"
            break

# Try Kuldeep Yadav (since he gave the cap) as a related image
if not img1_url:
    img1_url = fetch_wikipedia_person_image("Kuldeep Yadav")
    if img1_url and validate_image_url(img1_url):
        img1_caption = "Kuldeep Yadav, who presented Manav Suthar his Test cap"
        img1_attribution = "Wikimedia Commons"
    else:
        img1_url = None

# Pexels fallback - cricket spin bowling
if not img1_url:
    img1_url = fetch_pexels_image("cricket spin bowling India")
    if img1_url and validate_image_url(img1_url):
        img1_caption = "A spinner in action during a cricket match"
        img1_attribution = "Pexels"
    else:
        img1_url = None

if not img1_url:
    print("  ⚠ No image found for Article 1")

article1_body = """His father is a school teacher in Sri Ganganagar, a city near the India-Pakistan border in northern Rajasthan. His mother, Sushila Devi, is a homemaker. Cricket was never the family business. But on Saturday, June 6, 2026, at the Maharaja Yadavindra Singh International Cricket Stadium in Mullanpur, their son Manav Suthar walked out as India's Test cap No. 319.

Kuldeep Yadav, his fellow left-arm spinner, handed him the cap before the toss. The BCCI posted a picture with a simple caption: *"The smile says it all."*

## The Road from Sri Ganganagar

Manav began playing cricket at ten or eleven. He wanted to be a batsman. His coach, Dheeraj Sharma, saw something else — a left arm that could turn the ball sharply and a patience that belied his age. Sharma steered him toward spin, and the move changed his trajectory entirely.

By the time he was captaining the Sriganganagar district team, he had already led them to Under-14 and Under-16 titles. He progressed through Rajasthan's age-group sides — Under-16, Under-19, Under-23 — and made his first-class debut for Rajasthan in the 2021-22 Ranji Trophy season against Andhra in February 2022.

What followed was a relentless accumulation of wickets. In the 2022-23 Ranji Trophy, Suthar finished as Rajasthan's top wicket-taker with 39 scalps from just six matches. Across 29 first-class matches, he has taken 129 wickets at an average of 25.76, with six five-wicket hauls and a best of 8/33. He has also scored 945 runs, including a century, confirming his credentials as a genuine bowling all-rounder.

## The India A Audition

Suthar's big breakthrough came during the unofficial Test series between India A and Australia A in 2025. He finished as joint-highest wicket-taker in the series with eight wickets, matching teammate Gurnoor Brar, and recorded best figures of 5/107 in an innings. That performance, against batters preparing for full international duty, put him firmly in the national selectors' conversation.

He had earlier caught attention at the 2023 ACC Emerging Teams Asia Cup, where he took 10 wickets in five matches and finished as the second-highest wicket-taker of the tournament. Senior players noticed. During India's preparation camp for the 2023 ODI World Cup, both Rohit Sharma and Virat Kohli were reportedly impressed with Suthar's consistency and control in the nets.

## Filling Large Shoes

The timing of Suthar's debut is significant. Ravichandran Ashwin retired from international cricket. Ravindra Jadeja was rested for the Afghanistan Test. For the first time in nearly 16 years and 69 consecutive home Tests, India fielded a home Test XI without either of those two spin giants.

That is the void Suthar is being asked to fill. Head coach Gautam Gambhir was direct about why he got the nod over fellow newcomer Harsh Dubey: *"This is perhaps the only Test match where we can have a look at someone who could be our fourth spinner. Because after this, we go to Sri Lanka, and we might have to carry four spinners. So this is an ideal opportunity to try someone who could be a long-term option as well."*

Suthar played four matches for Gujarat Titans in IPL 2026, picking up two wickets. His T20 numbers are modest — 25 wickets in 29 matches — but in red-ball cricket, where patience and guile outweigh pace and novelty, his record speaks for itself.

## What the NRI Community Should Know

For the Indian diaspora watching from abroad, Suthar's story carries a familiar resonance. A middle-class family in a small city. A son whose passion his parents supported without fully understanding where it could lead. A coach who saw talent that the boy himself did not recognise.

Jagdish Suthar, Manav's father, told Dainik Bhaskar after the call-up: *"My son has been working hard continuously for the last 12-13 years. Initially, he wanted to be a batsman, but coach Dheeraj Sharma recognised his bowling talent and made him a spinner, which later proved to be correct."*

India are building a new spin core. Washington Sundar, Kuldeep Yadav, and now Manav Suthar represent the next generation. At 23, Suthar has time, form, and the backing of a team management that is investing deliberately in youth. Cap 319 is just the beginning.

*Sources: BCCI, Reuters, Dainik Bhaskar, ESPNcricinfo, Sportskeeda*"""

article1 = {
    "headline": "His Father Is a School Teacher Near the Pakistan Border. On Saturday, He Became India's Cap No. 319.",
    "subheadline": "Manav Suthar's Test debut in Mullanpur caps a 13-year journey from Sri Ganganagar district cricket to filling the void left by Ashwin and Jadeja.",
    "body": article1_body,
    "slug": "manav-suthar-test-debut-cap-319-india-afghanistan-mullanpur-sri-ganganagar-nri",
    "category": "sports",
    "image_url": img1_url or "",
    "image_caption": img1_caption,
    "image_attribution": img1_attribution,
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "sources": json.dumps(["BCCI", "Reuters", "Dainik Bhaskar", "ESPNcricinfo", "Sportskeeda"])
}

if img1_url:
    insert_article(article1)
else:
    print("  ⚠ Skipping article 1 - no valid image found")
    # Try one more time with a generic cricket-related image
    img1_url = fetch_pexels_image("cricket stadium India")
    if img1_url and validate_image_url(img1_url):
        article1["image_url"] = img1_url
        article1["image_caption"] = "The Maharaja Yadavindra Singh International Cricket Stadium in Mullanpur hosted its first Test match"
        article1["image_attribution"] = "Pexels"
        insert_article(article1)
    else:
        print("  ✗ Cannot publish article 1 without image")


# ============================================================
# ARTICLE 2: India Without Ashwin and Jadeja - Historic Transition
# ============================================================

print("\n" + "="*60)
print("ARTICLE 2: India Without Ashwin and Jadeja")
print("="*60)

# Image sourcing for transition article
print("\nSourcing image...")
img2_url = None
img2_caption = ""
img2_attribution = ""

# Try Ashwin from Wikipedia
img2_url = fetch_wikipedia_person_image("Ravichandran Ashwin")
if img2_url and validate_image_url(img2_url):
    img2_caption = "Ravichandran Ashwin, who retired from international cricket after 106 Tests and 537 wickets"
    img2_attribution = "Wikimedia Commons"
else:
    img2_url = None

# Try Jadeja
if not img2_url:
    img2_url = fetch_wikipedia_person_image("Ravindra Jadeja")
    if img2_url and validate_image_url(img2_url):
        img2_caption = "Ravindra Jadeja was rested for the one-off Test against Afghanistan"
        img2_attribution = "Wikimedia Commons"
    else:
        img2_url = None

# Commons fallback
if not img2_url:
    commons = fetch_wikimedia_commons_images("Indian cricket test match spin bowling")
    for c in commons:
        if validate_image_url(c["url"]):
            img2_url = c["url"]
            img2_caption = "India's spin department faces a generational shift"
            img2_attribution = "Wikimedia Commons"
            break

# Pexels fallback
if not img2_url:
    img2_url = fetch_pexels_image("cricket test match India")
    if img2_url and validate_image_url(img2_url):
        img2_caption = "India's spin department faces a generational shift"
        img2_attribution = "Pexels"
    else:
        img2_url = None

if not img2_url:
    print("  ⚠ No image found for Article 2")


article2_body = """For 69 consecutive home Tests — a span covering more than 15 years — at least one of Ravichandran Ashwin or Ravindra Jadeja walked out in India whites whenever India played at home. That streak ended on Saturday, June 6, 2026, at the Maharaja Yadavindra Singh International Cricket Stadium in Mullanpur.

The one-off Test against Afghanistan is India's first home Test without either spinner since late 2010. Ashwin has retired. Jadeja was rested. In their place: Washington Sundar, Kuldeep Yadav, and debutant Manav Suthar — a 23-year-old left-arm orthodox spinner from Rajasthan who received his cap from Kuldeep before the match.

The numbers those two compiled together are staggering.

## What India Loses — By the Numbers

During those 69 home Tests featuring at least one of Ashwin or Jadeja, India won 49 and lost only 11. That is a win rate of 71 per cent. Ashwin alone played 65 home Tests, taking 383 wickets at home — the bedrock of India's fortress reputation. He registered 29 five-wicket hauls at home, six ten-wicket matches, seven Player of the Match awards and 11 Player of the Series honours. No Indian spinner in the modern era dominated home conditions as thoroughly.

Jadeja, meanwhile, evolved from a containing left-arm spinner into one of Test cricket's most valuable all-rounders. His batting, particularly from No. 7 and No. 8, regularly rescued India from precarious positions, and his fielding was among the best in the world.

"His consistency and accuracy were remarkable," former India bowling coach Bharat Arun told Cricbuzz of Ashwin. "He had this uncanny knack for bowling straighter deliveries even on turning tracks, which is never easy. The batsman would be playing for the turn and the ball goes straight."

## The New Spin Core

India's selection for the Afghanistan Test signals the direction of travel. Three spinners were named in the XI — Washington Sundar, who offers batting depth and off-spin at a tight economy; Kuldeep Yadav, whose wrist spin and left-arm variations make him India's primary attacking option; and Manav Suthar, a bowling all-rounder with 129 first-class wickets at 25.76 from 29 matches.

Gambhir was explicit about the reasoning. "This is perhaps the only Test match where we can have a look at someone who could be our fourth spinner," he said. "Because after this, we go to Sri Lanka, and we might have to carry four spinners."

India's next red-ball assignment after this Test is a series in Sri Lanka, where pitches historically assist slow bowlers from the first session. Building a deep spin roster is not a luxury — it is a strategic necessity. The management wants to know whether Suthar can complement Kuldeep and Sundar, or whether Harsh Dubey, who missed out this time, should be the preferred option.

## Why It Matters Beyond Cricket

The Ashwin-Jadeja era represented something broader than wickets and averages. It represented an era in which India's home dominance was taken as a given. Visiting teams arrived expecting to lose. The pitch, the crowd, and the two spinners formed a combination that broke batting lineups season after season.

That certainty is gone. India's recent home record has been turbulent — a 0-3 whitewash by New Zealand, a 2-0 defeat to South Africa, and a Test championship position that has slid to sixth. The team that once made home soil feel like an impregnable fortress has been breached repeatedly.

"A Test match is a Test match," Gambhir said when asked about the importance of the Afghanistan game, which does not carry World Test Championship points. "I know people say this isn't part of the World Test Championship, but for me, it is a Test match. We need to win for the country."

## For the Diaspora

For NRIs who grew up watching Ashwin orchestrate home victories, this transition is both uncomfortable and overdue. India's cricket team is doing what every great institution must eventually do: trusting the next generation before it feels safe.

Ashwin, characteristically thoughtful about his own exit, offered his blessing. "I enjoyed every moment under the sun playing at home. It's like you are defending your territory," he told Cricbuzz. "Good luck to all the boys who will play to defend their territory."

The territory is unchanged. The defenders have not yet proven themselves. That is what makes this Test, against a modest Afghanistan side on a hot afternoon in Mullanpur, more significant than its billing suggests. Nine more Tests are scheduled for India this year, including the Sri Lanka and New Zealand series and a tour to England. The spin department that takes the field in those series is being shaped right now.

*Sources: CricketAddictor, Cricbuzz, Reuters, ESPNcricinfo, BCCI*"""

article2 = {
    "headline": "Sixty-Nine Home Tests. At Least One of Them Always Played. On Saturday in Mullanpur, Neither Did.",
    "subheadline": "Ashwin has retired. Jadeja was rested. India's first home Test without either in 16 years marks the end of a spin era and the start of an uncertain transition.",
    "body": article2_body,
    "slug": "india-without-ashwin-jadeja-69-home-tests-spin-transition-afghanistan-mullanpur-nri",
    "category": "sports",
    "image_url": img2_url or "",
    "image_caption": img2_caption,
    "image_attribution": img2_attribution,
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "sources": json.dumps(["CricketAddictor", "Cricbuzz", "Reuters", "ESPNcricinfo", "BCCI"])
}

if img2_url:
    insert_article(article2)
else:
    print("  ⚠ Skipping article 2 - no valid image found")
    img2_url = fetch_pexels_image("cricket spin bowler")
    if img2_url and validate_image_url(img2_url):
        article2["image_url"] = img2_url
        article2["image_caption"] = "India's spin department enters a new era without Ashwin and Jadeja"
        article2["image_attribution"] = "Pexels"
        insert_article(article2)
    else:
        print("  ✗ Cannot publish article 2 without image")

print("\n✓ Sports writer run complete")
