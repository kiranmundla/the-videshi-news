#!/usr/bin/env python3
"""Sports Writer — July 11, 2026 midnight run
Two articles:
1. World Cup Super Saturday preview — England-Norway + Argentina-Switzerland
2. MLC — LA Knight Riders hand SF Unicorns first loss
"""

import json, os, sys, datetime, uuid, re, subprocess, urllib.parse, requests

# ── Supabase setup ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def supabase_insert(article):
    """Insert an article into p2_articles."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        title = data[0]["headline"] if data else article["headline"]
        print(f"  ✅ Inserted: {title}")
        return True
    else:
        print(f"  ❌ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


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


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for images."""
    try:
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": search_query,
            "gsrnamespace": "6",
            "gsrlimit": str(limit),
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
            "iiurlwidth": "1200",
            "format": "json",
        }
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page in pages.values():
                ii = page.get("imageinfo", [{}])[0]
                thumb = ii.get("thumburl") or ii.get("url")
                if thumb and ii.get("mime", "").startswith("image/"):
                    results.append({
                        "title": page.get("title", ""),
                        "url": thumb,
                        "width": ii.get("thumbwidth", ii.get("width", 0)),
                        "height": ii.get("thumbheight", ii.get("height", 0)),
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Commons search error: {e}")
    return []


def commons_relevance_ok(title, headline, topic):
    """Check if a Commons file title is relevant to the article headline/topic."""
    title_lower = title.lower()
    headline_lower = headline.lower()
    topic_lower = (topic or "").lower()

    _COMMONS_STOP = {
        "file", "jpg", "png", "svg", "jpeg", "gif", "webp", "commons",
        "wikimedia", "image", "photo", "picture", "logo", "icon",
        "the", "and", "for", "with", "from", "this", "that", "have",
        "was", "are", "been", "being", "will", "would", "could", "should",
        "their", "there", "about", "which", "when", "where", "what", "how",
        "not", "but", "all", "had", "has", "her", "his", "him", "its",
        "may", "new", "now", "old", "one", "our", "out", "own", "two",
        "who", "why", "also", "back", "can", "day", "did", "get", "got",
        "just", "make", "many", "more", "most", "much", "must", "name",
        "over", "such", "take", "than", "them", "then", "very", "well",
        "year", "years", "social", "media", "people", "world", "first",
        "time", "long", "great", "high", "some", "only", "good", "after",
        "before", "other", "between", "during", "under", "last", "each",
        "same", "both", "few", "any", "part", "game", "match", "team",
        "play", "player", "season", "league",
    }

    # Extract distinctive keywords from headline + topic
    combined = f"{headline_lower} {topic_lower}"
    words = re.findall(r'[a-z]{4,}', combined)
    distinctive = [w for w in words if w not in _COMMONS_STOP]

    if not distinctive:
        return True  # Can't filter, allow

    # Check if at least one distinctive keyword appears in the file title
    for kw in distinctive:
        if kw in title_lower:
            return True
    return False


def verify_image_url(url):
    """Verify an image URL returns 200 with image content type and >5KB."""
    try:
        r = requests.get(url, timeout=10, stream=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            print(f"  ✓ Image verified: {url[:80]}... ({content_length} bytes)")
            return True
        else:
            print(f"  ⚠ Image check failed: status={r.status_code}, type={content_type}, size={content_length}")
    except Exception as e:
        print(f"  ⚠ Image verify error: {e}")
    return False


# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 1: World Cup Super Saturday Preview
# ═══════════════════════════════════════════════════════════════════════════

print("\n══════ ARTICLE 1: World Cup Super Saturday ══════")

art1_headline = "Super Saturday Is Here: Haaland Takes On Kane in Miami, Messi Faces Switzerland in Kansas City"
art1_subheadline = "Two World Cup quarterfinals on American soil, four Golden Boot contenders, and a semifinal blockbuster already locked in. Here's what NRIs need to know about the biggest day of the tournament."
art1_slug = "world-cup-2026-super-saturday-haaland-kane-norway-england-messi-argentina-switzerland-nri-july-2026"

art1_body = """The 2026 FIFA World Cup has saved its best day for Saturday. Two quarterfinals, both on American soil, both featuring generational strikers at the peak of their powers. For the Indian diaspora scattered across the United States, this is the kind of day where you cancel everything and find the nearest screen — or, better yet, the nearest stadium.

## The Afternoon Showdown: Norway vs. England in Miami

The first quarterfinal kicks off at 5 PM ET (2 PM PT) at Hard Rock Stadium in Miami Gardens, Florida. On paper, it's a contest between England, serial underachievers finally looking like a cohesive tournament side under Thomas Tuchel, and Norway, a fairytale team making its first World Cup appearance since 1998.

In reality, it's Erling Haaland vs. Harry Kane. Both know it. Everyone knows it.

Haaland has been ridiculous at this tournament — seven goals in four matches, including the emphatic double against Brazil in the round of 16 that sent the five-time champions packing at MetLife Stadium. The Manchester City striker has 62 goals in 54 appearances in a Norwegian shirt, a ratio that defies logic. He's been characteristically blunt about Norway's chances, telling reporters their odds of winning the whole thing are "really low" — then cracking up and adding, "I think all of you should put every single pressure on the English lads."

Kane isn't exactly struggling. England's all-time leading World Cup scorer now has 14 tournament goals across three World Cups. His penalty against Mexico and his clinical finish against DR Congo — three seconds from Gordon's pass to the ball hitting the net — have been hallmarks of an England side that has won its knockout matches without ever looking comfortable.

Norway's supporting cast deserves credit, too. Martin Ødegaard has been pulling strings in midfield, and Jørgen Strand Larsen has provided the foil that lets Haaland operate as a pure finisher. "Everybody knows Erling is the biggest one, but they're really a good group together," said former Norwegian international Morten Gamst Pedersen.

## The Night Game: Argentina vs. Switzerland in Kansas City

The second quarterfinal arrives at 9 PM ET (6 PM PT) at Arrowhead Stadium in Kansas City, and it features the defending champions.

Lionel Messi, playing in what is almost certainly his final World Cup, has been doing Messi things. Eight goals — tied with Kylian Mbappé at the top of the Golden Boot race. His three-goal comeback against Egypt in the round of 16, rallying Argentina from 2-0 down, was the kind of performance that reminds you this sport will never produce another like him.

Switzerland are nobody's idea of an easy out. They edged Colombia on penalties to reach the quarterfinals and have built their tournament on defensive discipline and counter-attacking precision. But Argentina carry the weight of a nation — and the aura of a squad seeking back-to-back titles.

## The Semifinal Is Already Set on One Side

France and Spain have already punched their tickets to the semifinals after their respective quarterfinal wins. Kylian Mbappé's eighth goal of the tournament — a curled beauty from just inside the box — powered France past Morocco 2-0 on Thursday. Spain followed with a 2-1 victory over Belgium on Friday, Dani Olmo's late winner sending the European champions through.

France vs. Spain in Arlington on Tuesday will be a blockbuster. The winners from Saturday's two matches will meet Wednesday in Atlanta.

## Where NRIs Are Watching

Both quarterfinals air on FOX, with Spanish-language coverage on Telemundo and streaming options on Peacock Premium and Fubo. For the diaspora in South Florida — one of the largest NRI communities on the East Coast — the England-Norway game at Hard Rock Stadium offers a rare chance to attend a World Cup quarterfinal in their backyard. Kansas City's growing Indian-American community, bolstered by the tech corridor around Overland Park, will be buzzing for the evening game.

Watch parties have become the social event of the summer across diaspora hubs. From Edison, New Jersey to Fremont, California, Indian restaurants and community centers have been screening matches to packed houses since the group stage. Saturday's doubleheader will be the biggest test yet.

## The Golden Boot Race

The scoring race adds another layer. Here's where things stand heading into Saturday:

- Kylian Mbappé (France): 8 goals — done until the semifinals
- Lionel Messi (Argentina): 8 goals — plays Saturday night
- Erling Haaland (Norway): 7 goals — plays Saturday afternoon
- Harry Kane (England): 6 goals — plays Saturday afternoon

If Haaland and Kane both score, the Golden Boot could have four contenders within touching distance heading into the final week. If Messi adds to his tally against Switzerland, he could run away with it.

## What's at Stake

Saturday's winners get a semifinal and the promise of a final at MetLife Stadium on July 19. For Norway, even reaching this stage is historic — their best previous World Cup run ended in the round of 16 in 1998. For England, it's about delivering on decades of promise. For Argentina, it's about Messi's legacy. For Switzerland, it's about proving the penalty shootout against Colombia wasn't their ceiling.

Four teams. Two games. One Saturday. This is what the World Cup is for."""

# Image: Use the NY Times Haaland photo from WC library
art1_image_url = "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/wc-social/ig-nytimes-27c0210c7207.jpg"
art1_image_caption = "Erling Haaland celebrates after scoring against Brazil in the World Cup round of 16"
art1_image_attribution = "@nytimes / Instagram"
print(f"  Using WC library image: {art1_image_url[:60]}...")

art1_sources = json.dumps([
    {"name": "NBC Sports", "url": "https://www.nbcsports.com"},
    {"name": "Fox Sports", "url": "https://www.foxsports.com"},
    {"name": "Reuters", "url": "https://www.reuters.com"},
    {"name": "USA Today", "url": "https://www.usatoday.com"},
    {"name": "Sky Sports", "url": "https://www.skysports.com"},
])

art1_article = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "slug": art1_slug,
    "body": art1_body,
    "category": "sports",
    "vertical": "world-cup",
    "status": "review",
    "is_editorial": False,
    "image_url": art1_image_url,
    "image_caption": art1_image_caption,
    "image_attribution": art1_image_attribution,
    "sources": art1_sources,
    "published_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "score_total": 8,
    "diaspora_angle": "Both World Cup quarterfinals are on US soil — Miami and Kansas City — giving NRIs a chance to attend or watch at community gatherings across diaspora hubs from Edison to Fremont.",
}


# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 2: MLC — LA Knight Riders Hand SF Unicorns First Loss
# ═══════════════════════════════════════════════════════════════════════════

print("\n══════ ARTICLE 2: MLC — LA Knight Riders Beat SF Unicorns ══════")

art2_headline = "Knight Riders Finally Crack the Code: LA Hands League-Leading SF Unicorns Their First MLC Defeat"
art2_subheadline = "A back-to-back surge from the LA Knight Riders — wins over Washington Freedom and the previously unbeaten San Francisco Unicorns — has injected life into the MLC Season 4 race."
art2_slug = "la-knight-riders-beat-sf-unicorns-mlc-2026-first-loss-back-to-back-wins-standings-nri-july-2026"

art2_body = """For nine matches, the San Francisco Unicorns looked untouchable. Five wins, no defeats, and a four-point cushion at the top of the Major League Cricket standings. The franchise that has come to embody NRI cricket culture in America — playing out of AirHogs Stadium in Grand Prairie, Texas, but carrying the Bay Area's tech-powered fandom — seemed destined for a wire-to-wire title defense.

Then the LA Knight Riders showed up.

## The Result That Shook the Table

In a Thursday night clash at AirHogs Stadium, the Knight Riders chased down the Unicorns' total of 173 with room to spare, posting 184 to inflict San Francisco's first loss of Season 4. It was the exclamation point on a remarkable 48-hour stretch for LA, who had beaten Washington Freedom 192-174 just the day before.

The Knight Riders, owned by the same Shah Rukh Khan-led KKR franchise group that runs the Kolkata Knight Riders in the IPL, have been slow starters this season. Five of their nine matches ended without a result — the kind of frustrating rain-affected record that threatened to derail their campaign entirely. But consecutive victories have pushed them to six points, level with MI New York and suddenly within striking distance of the Unicorns.

## Where Things Stand

The MLC Season 4 standings after Thursday's results tell a story of one clear leader and a compressed middle:

- **San Francisco Unicorns**: 9 matches, 5 wins, 1 loss, 3 NR — 10 points
- **LA Knight Riders**: 9 matches, 3 wins, 1 loss, 5 NR — 6 points
- **MI New York**: 9 matches, 3 wins, 3 losses, 3 NR — 6 points
- **Seattle Orcas**: 9 matches, 2 wins, 4 losses, 3 NR — 4 points
- **Texas Super Kings**: 8 matches, 2 wins, 4 losses, 2 NR — 4 points
- **Washington Freedom**: 8 matches, 2 wins, 4 losses, 2 NR — 4 points

San Francisco's four-point lead remains healthy, but the psychology of the race has shifted. The Unicorns are beatable. Their earlier dominance — anchored by the explosive opening combination of Finn Allen and Matthew Short, who hammered opposing attacks during a run that included a ten-six 116-run partnership against the Knight Riders in their first meeting — has been decoded.

## The Knight Riders' IPL DNA

What makes the LA Knight Riders dangerous is their IPL pedigree. The KKR ecosystem has produced some of T20 cricket's most reliable performers, and the MLC roster reflects that pipeline. Andre Russell remains one of the most destructive finishers in franchise cricket history. Sunil Narine's mystery spin has tormented batters across every T20 league on the planet. Shakib Al Hasan adds experience and guile.

The franchise model that Shah Rukh Khan pioneered in Kolkata — invest in entertainment value as much as on-field results — translates naturally to America, where MLC is still building its audience. The Knight Riders' brand recognition gives them an advantage that goes beyond the boundary.

## The MI New York Factor

Don't overlook MI New York, who sit level on points with the Knight Riders. Backed by the Mumbai Indians ownership group, MI New York have been inconsistent but capable of match-winning performances. Their latest result — a comfortable win over the Seattle Orcas at Marine Park in New York — suggests they're finding form at the right time.

The three-team battle for the remaining playoff spots behind San Francisco could make the final weeks of the MLC regular season the most compelling yet.

## Why the Diaspora Should Care

Major League Cricket remains the only professional cricket league where NRIs in America can actually show up, sit in a stadium, and watch world-class T20 cricket on home soil. The league plays in Dallas, New York, Seattle, Virginia, and California — cities with massive Indian-American populations.

Season 4's attendance numbers have been encouraging, and the addition of more IPL-affiliated franchises has raised the standard of play. For the generation of Indian-American kids growing up with both baseball and cricket, MLC is building something that didn't exist five years ago: a professional pathway.

The Unicorns may still be the team to beat. But after Thursday night in Grand Prairie, the Knight Riders have served notice: the race is far from over."""

# Image for MLC article — try Wikipedia for Andre Russell
print("  Sourcing MLC image...")
art2_image_url = None
art2_image_caption = None
art2_image_attribution = None

# Try Andre Russell from Wikipedia
img = fetch_wikipedia_person_image("Andre Russell")
if img and verify_image_url(img):
    art2_image_url = img
    art2_image_caption = "Andre Russell, one of the LA Knight Riders' star all-rounders in MLC Season 4"
    art2_image_attribution = "Wikimedia Commons"

# Fallback: try Sunil Narine
if not art2_image_url:
    img = fetch_wikipedia_person_image("Sunil Narine")
    if img and verify_image_url(img):
        art2_image_url = img
        art2_image_caption = "Sunil Narine, mystery spinner and key performer for the LA Knight Riders in MLC"
        art2_image_attribution = "Wikimedia Commons"

# Fallback: try Major League Cricket commons
if not art2_image_url:
    commons = fetch_wikimedia_commons_images("Major League Cricket", limit=5)
    for c in commons:
        if commons_relevance_ok(c["title"], art2_headline, "cricket league"):
            if verify_image_url(c["url"]):
                art2_image_url = c["url"]
                art2_image_caption = "Major League Cricket action in the United States"
                art2_image_attribution = "Wikimedia Commons"
                break

# Fallback: Shah Rukh Khan (KKR owner)
if not art2_image_url:
    img = fetch_wikipedia_person_image("Shah Rukh Khan")
    if img and verify_image_url(img):
        art2_image_url = img
        art2_image_caption = "Shah Rukh Khan, whose KKR ownership group runs the LA Knight Riders in MLC"
        art2_image_attribution = "Wikimedia Commons"

if not art2_image_url:
    print("  ⚠ No image found — skipping article 2 image")

art2_sources = json.dumps([
    {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
    {"name": "SportsCafe", "url": "https://www.sportscafe.in"},
    {"name": "Major League Cricket", "url": "https://www.majorleaguecricket.com"},
])

art2_article = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "slug": art2_slug,
    "body": art2_body,
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": art2_image_url,
    "image_caption": art2_image_caption,
    "image_attribution": art2_image_attribution,
    "sources": art2_sources,
    "published_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "score_total": 8,
    "diaspora_angle": "MLC is the only professional cricket league where NRIs can attend live T20 matches in American cities — the standings race directly shapes the diaspora's summer sports calendar.",
}


# ═══════════════════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ═══════════════════════════════════════════════════════════════════════════

print("\n══════ INSERTING ARTICLES ══════")
ok1 = supabase_insert(art1_article)
ok2 = supabase_insert(art2_article)

total = sum([ok1, ok2])
print(f"\n✅ Done: {total}/2 articles inserted successfully.")
if total < 2:
    print("⚠ Some articles failed — check errors above.")
    sys.exit(1)
