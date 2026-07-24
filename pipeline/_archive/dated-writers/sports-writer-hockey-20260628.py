#!/usr/bin/env python3
"""Sports writer: India beat England 3-2 in FIH Pro League shootout (June 28, 2026)"""

import os, json, subprocess, requests, urllib.parse, sys, re
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── image sourcing ───────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
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


def fetch_wikimedia_commons_images(search_query, limit=5):
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
            for page_id, page in sorted(pages.items(), key=lambda x: x[1].get("index", 999)):
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                title = page.get("title", "")
                if url and ii.get("width", 0) > 200:
                    results.append({
                        "url": url,
                        "title": title,
                        "width": ii.get("width", 0),
                        "height": ii.get("height", 0)
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []


def verify_image(url):
    """Verify image returns 200 and is >5KB."""
    try:
        cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}|%{size_download}|%{content_type}",
               "-A", "TheVideshi/1.0 (thevideshi.com)", url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        parts = result.stdout.strip().split("|")
        status = parts[0]
        size = float(parts[1]) if len(parts) > 1 else 0
        ctype = parts[2] if len(parts) > 2 else ""
        return status == "200" and size > 5000 and "image" in ctype
    except:
        return False


def find_best_image():
    """Search multiple sources for the best image for this hockey article."""
    print("\n=== Image Sourcing ===")

    # 1. Try Wikipedia for key people in the article
    for person in ["India national field hockey team", "Harmanpreet Singh (field hockey)"]:
        print(f"\n  Trying Wikipedia: {person}")
        url = fetch_wikipedia_person_image(person)
        if url and verify_image(url):
            return url, f"Wikimedia Commons", "India hockey team"

    # 2. Wikimedia Commons search
    for query in ["India field hockey team 2024", "FIH Pro League India hockey", "India hockey team penalty", "Lee Valley Hockey Centre"]:
        print(f"\n  Trying Commons: {query}")
        results = fetch_wikimedia_commons_images(query)
        for r in results:
            title_lower = r["title"].lower()
            # Skip logos, flags, icons
            if any(skip in title_lower for skip in ["logo", "flag", "icon", "emblem", "badge", "coat of arms"]):
                continue
            if r["width"] >= 600 and verify_image(r["url"]):
                # Create a sensible caption from the title
                caption_raw = r["title"].replace("File:", "").rsplit(".", 1)[0].replace("_", " ")
                print(f"  ✓ Found Commons image: {r['url'][:80]}...")
                return r["url"], "Wikimedia Commons", caption_raw
    
    # 3. Try Pexels as last resort (generic hockey imagery)
    if PEXELS_KEY:
        for pexels_query in ["field hockey game", "hockey stadium"]:
            print(f"\n  Trying Pexels: {pexels_query}")
            try:
                pr = requests.get(
                    "https://api.pexels.com/v1/search",
                    params={"query": pexels_query, "per_page": 5, "orientation": "landscape"},
                    headers={"Authorization": PEXELS_KEY},
                    timeout=10
                )
                if pr.status_code == 200:
                    photos = pr.json().get("photos", [])
                    for photo in photos:
                        purl = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                        if purl and verify_image(purl):
                            return purl, "Pexels", photo.get("alt", "Field hockey match in action")
            except Exception as e:
                print(f"  ⚠ Pexels error: {e}")

    return None, None, None


# ── dedup check ──────────────────────────────────────────────────────
def check_duplicate():
    """Check if we've already written a similar article."""
    from datetime import timedelta
    three_days_ago = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT00:00:00Z")
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={
            "select": "headline,slug",
            "status": "in.(published,review)",
            "published_at": f"gte.{three_days_ago}",
            "category": "eq.sports",
            "order": "published_at.desc",
            "limit": "50"
        },
        headers=HEADERS
    )
    if r.status_code == 200:
        articles = r.json()
        for a in articles:
            slug = a.get("slug", "").lower()
            headline = a.get("headline", "").lower()
            # Check for duplicate hockey India vs England articles
            if ("england" in slug and "hockey" in slug and "shoot" in slug) or \
               ("england" in headline and "hockey" in headline and "shoot" in headline) or \
               ("england" in slug and "hockey" in slug and "pro-league" in slug and "3-2" in slug):
                print(f"  ⚠ Possible duplicate found: {a['headline']}")
                return True
    return False


# ── article data ─────────────────────────────────────────────────────
ARTICLE = {
    "headline": "Shootout Revenge at Lee Valley. India Edge England 3-2 to End Their Pro League Tour on a High.",
    "subheadline": "Mohith Shashikumar's heroics in goal, a crucial overturned penalty stroke, and clinical shootout finishing helped India avenge their earlier loss to the hosts and head into the Hockey World Cup with momentum.",
    "slug": "india-beat-england-3-2-shootout-fih-pro-league-london-lee-valley-hardik-abhishek-mohith-hockey-world-cup-2026-diaspora-nri",
    "category": "sports",
    "vertical": "hockey",
    "status": "review",
    "is_editorial": False,
    "diaspora_angle": "India's hockey resurgence under Craig Fulton continues to build the sport's profile among NRIs in the UK, US, and Canada, with the team's fearless overseas performances echoing the spirit of a new generation of Indian sport.",
    "sources": json.dumps([
        {"name": "Hockey India", "url": "https://hockeyindia.org/news/indian-mens-hockey-team-prevails-3-2-over-england-in-shoot-out-after-goalless-draw-in-fih-pro-league-reverse-fixture"},
        {"name": "FIH Pro League Wikipedia", "url": "https://en.wikipedia.org/wiki/2025%E2%80%9326_Men%27s_FIH_Pro_League"},
        {"name": "Khel Now", "url": "https://khelnow.com/hockey/fih-pro-league-2025-26-india-pakistan-7-1-london"},
        {"name": "The Sports Tak", "url": "https://thesportstak.com/hockey/fih-pro-league-india-england-penalty-shootout"}
    ]),
}

BODY = """It was not pretty. It was not the seven-goal demolition India served up against Pakistan two days earlier. It was tighter, harder, and meaner — a match that needed its goalkeepers far more than its strikers. And in the end, under the grey London sky at Lee Valley, India found a way.

The Indian men's hockey team beat England 3-2 in a penalty shootout on Sunday after a fiercely contested 0-0 draw in their final FIH Hockey Pro League fixture of the season. Abhishek, Shilanand Lakra, and Hardik Singh converted their one-on-one attempts to clinch the bonus point and — more importantly — avenge the 1-4 shootout loss to the same opponents just 48 hours earlier.

Defender Sanjay was named Player of the Match. But the evening belonged to India's goalkeeping unit — first Mohith Shashikumar, then Sanjay Karkera — who together made save after save to keep England's swarming attack scoreless across 60 minutes.

## The Goalkeeper's Night

England came out with intent from the first whistle. Sam Ward won an early penalty corner, and Mohith responded with a sensational double save. He denied Ward again moments later, then stopped Sanford, establishing himself as the dominant presence in the circle before the first quarter was even done.

India's best chance of the opening period came late through Abhishek, but England had the better of the exchanges. The visitors were content to absorb and counter — a tactical shift from the all-out attacking style that had produced 11 goals in two matches against Pakistan.

The pattern held through the second quarter: England pressing, India holding firm. Jarmanpreet Singh fired a shot that drew a strong save from the England goalkeeper. Nicholas Bandurak came close at the other end. Neither side blinked.

## The Stroke That Wasn't

India returned after halftime with sharper attacking intent. Hardik Singh produced a driving run from midfield that tore open the English defence, feeding Mandeep Singh, whose effort was well saved. Hardik then won a penalty corner in the 37th minute, but Amandeep Lakra couldn't convert.

The match's pivotal moment came late in the third quarter. England were awarded a penalty stroke after Yashdeep Singh was adjudged to have fouled Henry Croft — a decision that would have almost certainly handed England the lead. India immediately referred the call to video. The replays confirmed a clean challenge, the stroke was overturned, and England's Nicholas Park picked up a green card in the aftermath.

The reversal shifted momentum. India won another penalty corner, though the English goalkeeper denied them. Tempers rose between the benches. Dilpreet Singh received a green card. But the score stayed locked at zero.

## Shootout Nerves, Indian Steel

The final quarter was a continuation of the arm-wrestle. Sanjay Karkera — replacing Mohith in goal — made a crucial save to preserve the clean sheet. Sukhjeet Singh won India a string of penalty corners with a brilliant piece of play, but England's defence held.

In the dying seconds, England won a penalty corner. India reviewed the decision. Once again, it was overturned. The whistle blew: 0-0 after regulation.

In the shootout, India's composure was clinical. Abhishek went first and converted. Shilanand Lakra followed with a calm finish. Hardik Singh sealed it, his trademark confidence from the spot carrying India to a 3-2 win over the hosts.

## London Leg: The Bigger Picture

India's London campaign ended with a record worth celebrating: three wins from four matches. They hammered Pakistan 4-3 and 7-1 in the two reverse fixtures, lost the first England shootout 1-4 after a 2-2 draw, then recovered to win the return fixture on penalties.

More critically, this was India's final Pro League game before the Hockey World Cup. After a difficult European leg that began with losses to Belgium and Argentina in Rourkela and continued with mixed results in Hobart and Rotterdam, the London chapter felt like a turning point — the performance of a team that has found its defensive identity under coach Craig Fulton.

For NRIs who watched the India-Pakistan thrashing on Friday and tuned in again on Sunday, the takeaway is unmistakable: this Indian hockey team does not fold away from home. The World Cup is next. And India head into it with something they've lacked in tournaments past — genuine belief that they can win the hard, ugly, 0-0 matches, not just the ones where the goals flow freely.
"""

def main():
    print("=" * 60)
    print("SPORTS WRITER: India beat England in FIH Pro League shootout")
    print("=" * 60)

    # Dedup check
    print("\n--- Dedup Check ---")
    if check_duplicate():
        print("  ✗ Duplicate detected, skipping this article.")
        sys.exit(0)
    print("  ✓ No duplicate found.")

    # Image sourcing
    image_url, image_attribution, image_caption_raw = find_best_image()

    if image_url:
        ARTICLE["image_url"] = image_url
        ARTICLE["image_attribution"] = image_attribution
        ARTICLE["image_caption"] = image_caption_raw[:200] if image_caption_raw else "India men's hockey team in action during a FIH Pro League match"
    else:
        print("\n  ⚠ No suitable image found. Setting fallback.")
        ARTICLE["image_url"] = ""
        ARTICLE["image_attribution"] = ""
        ARTICLE["image_caption"] = ""

    # Set body and published_at
    ARTICLE["body"] = BODY.strip()
    ARTICLE["published_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    # Validate
    print("\n--- Validation ---")
    assert len(ARTICLE["headline"]) >= 20, f"Headline too short: {len(ARTICLE['headline'])}"
    assert len(ARTICLE["headline"]) <= 200, f"Headline too long: {len(ARTICLE['headline'])}"
    assert len(ARTICLE["subheadline"]) >= 15, f"Subheadline too short"
    word_count = len(ARTICLE["body"].split())
    assert word_count >= 400, f"Body too short: {word_count} words (need 400+)"
    assert ARTICLE["category"] == "sports", "Category must be lowercase 'sports'"
    assert ARTICLE["status"] == "review", "Status must be 'review'"
    assert ARTICLE["is_editorial"] == False, "is_editorial must be False"
    print(f"  ✓ Headline: {len(ARTICLE['headline'])} chars")
    print(f"  ✓ Subheadline: {len(ARTICLE['subheadline'])} chars")
    print(f"  ✓ Body: {word_count} words")
    print(f"  ✓ Slug: {ARTICLE['slug']}")
    print(f"  ✓ Category: {ARTICLE['category']}")
    print(f"  ✓ Status: {ARTICLE['status']}")
    print(f"  ✓ Image URL: {ARTICLE.get('image_url', 'NONE')[:80]}...")
    print(f"  ✓ Vertical: {ARTICLE['vertical']}")
    print(f"  ✓ Diaspora angle: {ARTICLE['diaspora_angle'][:60]}...")

    # Insert
    print("\n--- Inserting Article ---")
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=ARTICLE
    )
    if r.status_code in (200, 201):
        result = r.json()
        article_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  ✓ Article inserted! ID: {article_id}")
        print(f"  ✓ Headline: {ARTICLE['headline']}")
        return article_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} — {r.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()
