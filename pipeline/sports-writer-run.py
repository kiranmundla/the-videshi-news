#!/usr/bin/env python3
"""Sports writer for The Videshi — June 5, 2026 run."""

import json, os, sys, time, uuid, re, urllib.parse
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

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
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
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
    """Search Wikimedia Commons for CC-licensed images."""
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
            params=params, headers=UA, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                thumb = ii.get("thumburl") or ii.get("url")
                if thumb and ii.get("mime", "").startswith("image/"):
                    results.append({
                        "url": thumb,
                        "title": page.get("title", ""),
                        "width": ii.get("thumbwidth", ii.get("width", 0)),
                        "height": ii.get("thumbheight", ii.get("height", 0))
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Commons search error: {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for an image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY, **UA},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image: {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def validate_image(url):
    """Verify image URL returns 200 with image content-type and reasonable size."""
    try:
        r = requests.head(url, headers=UA, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't return Content-Length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, headers=UA, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def find_best_image(person_name=None, commons_query=None, pexels_query=None):
    """Multi-source image search. Returns (url, attribution, caption) or (None, None, None)."""
    # 1. Wikipedia person image
    if person_name:
        wp_img = fetch_wikipedia_person_image(person_name)
        if wp_img and validate_image(wp_img):
            return wp_img, "Wikimedia Commons", f"{person_name}"
    
    # 2. Wikimedia Commons
    if commons_query:
        commons_results = fetch_wikimedia_commons_images(commons_query)
        for r in commons_results:
            if r["width"] >= 400 and validate_image(r["url"]):
                title = r["title"].replace("File:", "").rsplit(".", 1)[0].replace("_", " ")
                return r["url"], "Wikimedia Commons", title[:80]
    
    # 3. Pexels
    if pexels_query:
        px_img = fetch_pexels_image(pexels_query)
        if px_img and validate_image(px_img):
            return px_img, "Pexels", pexels_query.title()
    
    return None, None, None


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
        if isinstance(data, list) and data:
            return data[0].get("id")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None


# ============================================================
# ARTICLE 1: Norway Chess Final Round Preview
# ============================================================
def write_norway_chess_article():
    print("\n=== Article 1: Norway Chess Final Round ===")
    
    # Image: Try Wesley So (tournament leader), then Praggnanandhaa
    img_url, img_attr, img_cap = find_best_image(
        person_name="Wesley So",
        commons_query="Wesley So chess 2024",
        pexels_query="chess grandmaster tournament"
    )
    
    # If Wesley So image fails, try Praggnanandhaa
    if not img_url:
        img_url, img_attr, img_cap = find_best_image(
            person_name="Rameshbabu Praggnanandhaa",
            commons_query="Praggnanandhaa chess",
            pexels_query="chess tournament pieces"
        )
    
    if img_url:
        print(f"  Using image: {img_url[:80]}...")
    else:
        print("  ⚠ No suitable image found")
    
    slug = "norway-chess-2026-final-round-so-praggnanandhaa-firouzja-title-race-nri"
    headline = "Half a Point Separates First and Second. Norway Chess Will Be Decided in the Final Round Today."
    subheadline = "Wesley So leads Praggnanandhaa by the thinnest margin. Firouzja is a point behind. Three pairings on Friday will determine who takes home the title and the $100,000 prize."
    
    body = """The 14th edition of Norway Chess will come down to its final three games on Friday in Oslo. Wesley So leads with 15.5 points, Praggnanandhaa Rameshbabu is half a point behind at 15, and Alireza Firouzja sits at 14.5. All three can still win the tournament. Magnus Carlsen and Gukesh Dommaraju cannot.

## The Title Permutations

The math is simple but the chess will not be. So faces Firouzja in the round that could make or break both their campaigns. A classical win for So would seal the title regardless of other results. A classical win for Firouzja, combined with a Praggnanandhaa draw or loss, would give the French grandmaster the crown. If So and Firouzja draw and head to Armageddon, the door stays open for Praggnanandhaa.

Praggnanandhaa plays Vincent Keymer, the German who has gone unbeaten in classical games throughout the tournament. The 19-year-old Indian has been the form player of the last three rounds, winning three consecutive classical games against Carlsen, Keymer's compatriot, and Gukesh. A fourth straight classical win would guarantee at least a share of first place if So falters.

The third pairing pits Carlsen against Gukesh in what amounts to a pride match for both. Carlsen sits fifth with 10 points, his worst showing at his home tournament. Gukesh is last with 8 points, a dismal result for the reigning World Champion. The two have not met since their World Championship match in December.

## Praggnanandhaa's Extraordinary Run

The story of this tournament's second half belongs to Praggnanandhaa. After losing to So in the opening round and to Firouzja in round three, the Chennai-born teenager has been near-flawless. He beat Carlsen with the white pieces. Then he beat Carlsen with the black pieces. In round nine, he completed a hat trick against Gukesh, outplaying the World Champion in a sharp tactical battle where Gukesh sacrificed material for initiative but found no breakthrough.

Three consecutive classical wins at a Category XXI event is a feat that few players in history have managed. Praggnanandhaa's ability to thrive under tournament pressure, shifting gears between classical and Armageddon play, has been the defining narrative of this event. He has scored 9 out of a possible 12 points over the last four rounds.

## So's Steady Hand

Wesley So has led this tournament since round two and has not relinquished the top spot. His strategy has been disciplined: he has avoided classical losses, and when games have gone to Armageddon, he has consistently converted. In round nine, he drew Carlsen in classical and then won the tiebreaker, extending his lead at a moment when Praggnanandhaa was closing in.

The Filipino-American grandmaster's last classical win came in round five against Gukesh. Since then, he has relied on the Armageddon format to accumulate the half-points that have kept him ahead. Against Firouzja on Friday, he faces the one opponent who has beaten him in classical at this event.

## The Indian Contingent's Mixed Tournament

For the Indian diaspora, this tournament has been a study in contrasts. Praggnanandhaa has been spectacular, but Gukesh has endured his worst elite tournament since becoming World Champion. The 19-year-old has lost three classical games, including back-to-back defeats to Carlsen and Praggnanandhaa, and sits at the bottom of the standings.

In the Women's section, Bibisara Assaubayeva of Kazakhstan clinched the title with a round to spare. India's Divya Deshmukh and Koneru Humpy finish in the bottom half of the standings, with Humpy losing seven consecutive Armageddon games at one point during the event.

## What NRI Fans Should Watch For

The final round begins at 5:00 PM CEST on Friday, which translates to 8:30 AM on the West Coast and 11:30 AM on the East Coast. The So-Firouzja and Praggnanandhaa-Keymer games will run simultaneously, and the title could be decided by a single Armageddon game. NRI chess fans who have followed Praggnanandhaa's journey from prodigy to elite contender have rarely had a more dramatic stage to watch.

The tournament uses a scoring system where a classical win earns 3 points, an Armageddon win earns 1.5 points, and an Armageddon loss earns 1 point. A classical loss earns nothing. This means Praggnanandhaa needs either a classical win combined with a So draw or loss, or any win combined with a So classical loss, to overtake the leader.

For a nation that produced the current World Champion and now watches two of its teenagers fight for a super-tournament title, Friday in Oslo is appointment viewing."""

    sources = [
        "chess.com — Norway Chess 2026 Round 9 coverage",
        "ChessBase India — Pragg defeats Gukesh, Assaubayeva wins title",
        "Wikipedia — Norway Chess 2026 standings",
        "Rook Review — Norway Chess Day 9 analysis"
    ]
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(sources),
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_cap if img_cap else "Wesley So at a chess tournament",
        "image_attribution": img_attr if img_attr else "Wikimedia Commons"
    }
    
    result = insert_article(article)
    if result:
        print(f"  ✓ Published: {headline}")
        print(f"    Slug: {slug}")
    return result


# ============================================================
# ARTICLE 2: India U-18 Hockey Asia Cup Semifinals
# ============================================================
def write_hockey_article():
    print("\n=== Article 2: India U-18 Hockey Asia Cup Semifinals ===")
    
    # Image: Try Sardar Singh (coach), then hockey commons
    img_url, img_attr, img_cap = find_best_image(
        person_name="Sardar Singh (field hockey)",
        commons_query="India hockey team 2024",
        pexels_query="field hockey India"
    )
    
    if not img_url:
        # Try broader commons search
        img_url, img_attr, img_cap = find_best_image(
            commons_query="India field hockey national team",
            pexels_query="field hockey match"
        )
    
    if img_url:
        print(f"  Using image: {img_url[:80]}...")
    else:
        print("  ⚠ No suitable image found")
    
    slug = "india-u18-hockey-asia-cup-2026-semifinals-pakistan-china-kakamigahara-nri"
    headline = "India Face Pakistan and China in the U-18 Asia Cup Semifinals Today. Sardar Singh Says His Team Is Ready."
    subheadline = "The U-18 men take on Pakistan at 3:30 PM IST in Kakamigahara. The women, unbeaten with a 25-0 rout in the group stage, face China at 9:30 AM. Both squads have outscored opponents by a combined 57-7."
    
    body = """India's U-18 hockey teams will play the most consequential matches of their young careers on Thursday in Kakamigahara, Japan. The women face China in the first semifinal at 9:30 AM IST. The men face Pakistan at 3:30 PM IST. Both teams have been dominant through the group stage, and both now face opponents who can genuinely trouble them.

## The Women's Side: 55 Goals in Three Games

The Indian U-18 women's team has not simply won their group — they have dismantled it. In three Pool A matches, they beat Malaysia, Korea, and Singapore while scoring a combined total that is difficult to contextualize at any level of hockey. Their 25-0 demolition of Singapore in the final group game saw ten different players score, with striker Nousheen Naz netting seven goals in a single match.

Captain Sweety Kujur has led from the front with consistent scoring, while Geethasri Nammi earned the Player of the Match award against Singapore for her five-goal performance. The depth of India's attacking options has been remarkable: Priyanka Minz contributed a hat trick, and players from every line of the team have found the net.

China, their semifinal opponents, topped Pool B and present a fundamentally different challenge from anyone India have faced so far. Where Singapore, Malaysia, and Korea were overwhelmed by India's pace and technical superiority, China will match them physically and bring structured defensive discipline. This is where India's tournament truly begins.

## The Men's Side: Sardar Singh's Blueprint

The U-18 men's team finished second in Pool A, behind hosts Japan, with three wins and one loss. Their 4-2 defeat to Japan in the second group match remains the only blemish on an otherwise commanding campaign. India scored 32 goals in the group stage, with captain Ketan Kushwaha contributing seven and Ashish Tani Purti adding six.

The 13-1 win over Chinese Taipei and the 13-0 opening victory against Kazakhstan demonstrated the team's attacking firepower. But it is the Japan loss that has defined their preparation for the semifinal. Coach Sardar Singh, the former India captain who represented the country in over 300 international matches, said his staff reviewed all four games and identified penalty corner attack and defence as the areas needing improvement.

"The aim is to be fully ready for the semifinal," Sardar Singh said, adding that training has been split into separate groups of defenders, midfielders, and forwards. He emphasized disciplined hockey and trust in passing, while also urging skillful players to express themselves when the situation demands it.

## India vs Pakistan: History and Context

The men's semifinal carries weight that extends beyond age-group hockey. India-Pakistan hockey rivalries have shaped the sport's identity in South Asia for decades. At the senior level, India's dominance has fluctuated, but at U-18 level, both teams bring raw talent and emotional intensity that can make these encounters unpredictable.

Pakistan topped Pool B in the men's event with two wins and one defeat. They are a physical side with strong counter-attacking instincts. For India, the key will be converting the penalty corners that Sardar Singh has been drilling into his players. Gazee Khan and Shahrukh Ali, who scored three goals each in the group stage, provide India with options from set pieces and open play.

## What It Means for Indian Hockey's Pipeline

These U-18 tournaments are where Indian hockey identifies the players who will eventually represent the senior team at the Asian Games and the Olympics. The current senior women's squad, which reached the Olympic quarterfinals, was built on players who came through exactly this pathway. The men's senior team, which won Asian Games gold, relies on talent spotted and developed at this level.

For NRI fans, the significance is dual. These young athletes represent the depth of India's investment in hockey infrastructure, particularly the academies in Odisha, Punjab, and Jharkhand that have become production lines for international talent. The results in Kakamigahara will signal whether the next generation is ready to sustain what the current senior teams have built.

Both semifinals will be streamed live on the Asian Hockey Federation's official YouTube channel. The women's semifinal begins at 9:30 AM IST on Thursday, with the men's match following at 3:30 PM IST. The finals are scheduled for Saturday."""

    sources = [
        "Mykhel.com — India U-18 teams advance to Asia Cup semifinals",
        "India Sports Hub — India 25-0 Singapore match report",
        "Sports Digest India — India 13-1 Chinese Taipei report",
        "Nagaland Post — U18 Asia Cup group stage coverage"
    ]
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(sources),
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_cap if img_cap else "India U-18 hockey team at the Asia Cup 2026 in Kakamigahara, Japan",
        "image_attribution": img_attr if img_attr else "Wikimedia Commons"
    }
    
    result = insert_article(article)
    if result:
        print(f"  ✓ Published: {headline}")
        print(f"    Slug: {slug}")
    return result


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print(f"Sports writer run — {datetime.now(timezone.utc).isoformat()}")
    
    results = []
    results.append(write_norway_chess_article())
    results.append(write_hockey_article())
    
    published = sum(1 for r in results if r)
    print(f"\n=== Done: {published}/{len(results)} articles published ===")
    sys.exit(0 if published > 0 else 1)
