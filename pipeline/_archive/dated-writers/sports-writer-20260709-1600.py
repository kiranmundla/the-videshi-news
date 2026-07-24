#!/usr/bin/env python3
"""Sports Writer — 2026-07-09 16:00 PDT
Three articles:
1. Suryakumar Yadav named MLB Ambassador (diaspora crossover)
2. Historic first women's Test at Lord's — England vs India (starts Fri July 11)
3. MLC 2026 mid-season: San Francisco Unicorns dominating Season 4
"""

import json, os, re, subprocess, sys, urllib.parse, uuid
from datetime import datetime, timezone

# ─── Supabase ──────────────────────────────────────────────────────────────
def load_env():
    env_path = os.path.expanduser("~/workspace/.env.supabase")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

load_env()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ─── Image Helpers ─────────────────────────────────────────────────────────
UA = "TheVideshi/1.0 (thevideshi.com)"

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        result = subprocess.run(
            ["curl", "-sS", "-A", UA, "-L",
             f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            img = (data.get("originalimage") or {}).get("source") or \
                  (data.get("thumbnail") or {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = urllib.parse.urlencode({
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    try:
        result = subprocess.run(
            ["curl", "-sS", "-A", UA, "-L", url],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{search_query}': {e}")
    return []

# Relevance gate for Commons images
_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use",
}

def _keywords(text):
    toks = re.findall(r"[A-Za-z][A-Za-z'-]+", text or "")
    return [t.lower() for t in toks if len(t) >= 4 and t.lower() not in _COMMONS_STOP]

def commons_relevance_ok(commons_title, headline, topic=""):
    title_l = (commons_title or "").lower()
    if not title_l:
        return False
    kws = _keywords(headline) + _keywords(topic)
    if not kws:
        return True
    return any(kw in title_l for kw in kws)

def verify_image_url(url):
    """Verify image URL returns 200 with image content-type and >5KB."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w",
             "%{http_code} %{content_type} %{size_download}",
             "-A", UA, "-L", url],
            capture_output=True, text=True, timeout=15
        )
        parts = result.stdout.strip().split()
        if len(parts) >= 3:
            code = parts[0]
            ctype = parts[1]
            size = float(parts[2])
            if code == "200" and "image" in ctype and size > 5000:
                return True
    except Exception:
        pass
    return False

def insert_article(article):
    """Insert article into Supabase p2_articles."""
    payload = json.dumps(article)
    result = subprocess.run(
        ["curl", "-sS", "-X", "POST",
         f"{SUPABASE_URL}/rest/v1/p2_articles",
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=representation",
         "-d", payload],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout

# ─── Article 1: Suryakumar Yadav as MLB Ambassador ────────────────────────
def build_article_sky_mlb():
    print("\n📰 Article 1: Suryakumar Yadav — MLB Ambassador")

    headline = "Cricket's Mr. 360 Goes to Baseball. Suryakumar Yadav Named MLB's First Indian Ambassador."
    subheadline = "India's T20 World Cup-winning captain will attend All-Star Week in Philadelphia, as Major League Baseball bets big on the world's largest cricket-loving market."

    body = """When Major League Baseball announced Suryakumar Yadav as its newest global ambassador on Wednesday, it wasn't just a branding play. It was an acknowledgment that the fastest route to America's next generation of baseball fans may run through Mumbai, not Miami.

Suryakumar — universally known as SKY — captained India to a record third T20 World Cup title in March with a ruthless demolition of New Zealand. Now, just four months later, the man whose 360-degree shot-making redefined T20 batting is being asked to do something even more audacious: sell baseball to a country where cricket is a religion.

## The Philly Pitch

SKY will make his first public appearance as ambassador during MLB All-Star Week in Philadelphia from July 10-14, baseball's annual mid-season festival of its best talent. He'll attend events, create content for Indian audiences, and serve as a living bridge between two bat-and-ball sports that share more DNA than either side usually admits.

"I'm excited to partner with Major League Baseball and be part of its journey in India," Suryakumar said. "I look forward to learning more about the game myself and helping more fans discover the energy, excitement and culture that make baseball something else."

Jeremiah Yolkut, MLB's senior vice president of global operations, called India "home to one of the most vibrant sports cultures in the world." The league also renewed its broadcast deal with JioStar, India's dominant sports media platform, ensuring live MLB games continue to reach Indian screens.

## Why This Matters for NRIs

For the estimated 4.4 million Indian Americans, the partnership is more than marketing. It's validation.

South Asians in the US have long occupied an awkward middle ground in American sports culture — passionate cricket fans who learned to love (or at least tolerate) baseball's slower rhythms. The typical NRI household in Edison, Fremont, or Plano might toggle between an IPL stream on one screen and an MLB game on another. Suryakumar's appointment gives that dual identity an official face.

The timing also intersects with Major League Cricket's Season 4, now in full swing across Grand Prairie, Oakland, and Pomona. Cricket in the US is no longer a backyard affair — it's televised, franchised, and attended by thousands. Having an Indian cricket icon validate baseball at the same moment creates an unusual two-way corridor between the sports.

## The Bigger Play

MLB's India push isn't new. The league opened an office in Mumbai in 2019 and has steadily invested in youth development programs. But the Suryakumar deal escalates the ambition. By pairing a cricketing superstar with JioStar's broadcast muscle, MLB is betting it can convert India's 1.4 billion cricket fans — or at least a fraction of them — into baseball-curious viewers.

Whether Indian fans will embrace nine-inning games with the same fervor they reserve for T20 finishes remains an open question. But for the diaspora, the message is clear: the sports you love aren't rivals. They're cousins. And SKY is here to prove it."""

    # Image: Wikipedia photo of Suryakumar Yadav
    image_url = fetch_wikipedia_person_image("Suryakumar Yadav")
    image_caption = "Suryakumar Yadav, India's T20 World Cup-winning captain, named MLB's newest global ambassador"
    image_attribution = "Wikimedia Commons"

    if not image_url:
        # Fallback to Commons
        commons = fetch_wikimedia_commons_images("Suryakumar Yadav cricket India", limit=3)
        for c in commons:
            if commons_relevance_ok(c["title"], headline, "Suryakumar Yadav cricket"):
                image_url = c["url"]
                break

    if image_url and not verify_image_url(image_url):
        print(f"  ⚠ Image verification failed, trying Commons fallback")
        image_url = None

    if not image_url:
        print("  ⚠ No image found for SKY — skipping article")
        return None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": "suryakumar-yadav-mlb-ambassador-india-cricket-baseball-all-star-philadelphia-nri-2026",
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "vertical": "cricket-crossover",
        "diaspora_angle": "India's cricket captain bridging the gap between cricket and baseball gives NRIs in America official representation at the highest level of both bat-and-ball sports.",
        "sources": json.dumps(["Reuters", "RevSportz", "SportsCafe", "DevDiscourse"]),
        "score_total": 8,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


# ─── Article 2: First Women's Test at Lord's ──────────────────────────────
def build_article_womens_test_lords():
    print("\n📰 Article 2: First Women's Test at Lord's — England vs India")

    headline = "212 Years of Lord's. Zero Women's Tests. Until Friday."
    subheadline = "England and India will play the first-ever women's Test at the Home of Cricket, 50 years after Rachael Heyhoe-Flint led the first women's match at the ground."

    body = """Lord's Cricket Ground, the self-styled Home of Cricket since 1814, has hosted 150 men's Test matches. Kings have watched from the pavilion. Knighthoods have been earned on its outfield. But in 212 years of existence, the ground has never hosted a women's Test match.

That changes on Friday when England and India walk out for a four-day Test that is as much about righting a historical wrong as it is about cricket.

## Breaking Through the Long Room

The symbolism is hard to overstate. Women were not permitted to join the Marylebone Cricket Club — which owns Lord's and has governed cricket's laws since 1788 — until 1999. They could not enter the Long Room, cricket's most hallowed corridor, until the club voted to admit female members after a bitter internal battle.

Now, more than 30,000 tickets have been sold for a women's Test at the same ground. A special opening ceremony will feature 50 past and present England women's players, including Enid Bakewell, who played in the 1976 international that was the first women's match of any kind at Lord's — led by the pioneering Rachael Heyhoe-Flint, who has a gate named in her honour at the ground.

"It's a huge honour and a privilege to be walking out there tomorrow," said England captain Nat Sciver-Brunt. "We are looking forward to such a special week here at Lord's, doing something that we dreamt of as kids growing up playing cricket."

## Beaumont's Farewell

The match also serves as the final international appearance of Tammy Beaumont, who announced her retirement from international cricket at 35 after being left out of England's T20 World Cup squad.

Beaumont's 17-year career includes 260 caps, 14 international centuries, and a record-setting double century of 208 against Australia in the 2023 Ashes — the highest score ever by an Englishwoman in Tests. She was Player of the Tournament in England's 2017 World Cup triumph and became one of the first women awarded professional central contracts by the ECB.

"This Test match at Lord's — our first ever women's Test at Lord's — feels like the perfect occasion to sign off," Beaumont said.

## India's Challenge

India arrive at Lord's after a turbulent summer. The men's side is reeling from a record 125-run T20 defeat to England at Trent Bridge, trailing the series 2-0. The women's team has a chance to provide a different narrative.

England and India have played 15 women's Tests, with 11 ending in draws and England winning just once. The visitors will be keen to spoil the party on what promises to be an emotionally charged occasion.

For NRIs in the UK, Friday represents something rare — a chance to watch India's women compete at the most iconic venue in cricket, in a match that makes history simply by existing. With the Indian diaspora comprising one of the largest groups of cricket fans in Britain, the demand for tickets has been significant.

## More Than a Cricket Match

The first women's Test at Lord's is ultimately about legitimacy. Every major men's cricketing moment — from Douglas Jardine's Bodyline series to Ben Stokes's Ashes miracle — has Lord's as part of its mythology. Women's cricket has been excluded from that mythology for over two centuries.

Friday begins correcting that. The scorecard will matter. But the dateline will matter more."""

    # Image: Wikimedia Commons for Lord's Cricket Ground
    image_url = None
    image_caption = "Lord's Cricket Ground in London, set to host its first women's Test match on Friday"
    image_attribution = "Wikimedia Commons"

    commons = fetch_wikimedia_commons_images("Lord's Cricket Ground London pavilion", limit=5)
    for c in commons:
        if commons_relevance_ok(c["title"], "Lord's Cricket Ground", "Lord's cricket pavilion"):
            if verify_image_url(c["url"]):
                image_url = c["url"]
                print(f"  ✓ Using Commons image: {c['title']}")
                break
            else:
                print(f"  ⚠ Commons image failed verification: {c['title']}")

    if not image_url:
        # Try alternate search
        commons2 = fetch_wikimedia_commons_images("Lords cricket ground England", limit=5)
        for c in commons2:
            if verify_image_url(c["url"]):
                image_url = c["url"]
                print(f"  ✓ Using Commons fallback: {c['title']}")
                break

    if not image_url:
        print("  ⚠ No Lord's image found — skipping article")
        return None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": "first-womens-test-lords-england-india-beaumont-retirement-sciver-brunt-nri-2026",
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "vertical": "women-cricket",
        "diaspora_angle": "The first women's Test at Lord's gives NRIs in the UK a historic chance to watch India's women at cricket's most iconic venue, correcting a 212-year exclusion.",
        "sources": json.dumps(["Reuters", "ICC Cricket", "Wisden", "FemaleCricket.com"]),
        "score_total": 8,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


# ─── Article 3: MLC 2026 Season 4 ─────────────────────────────────────────
def build_article_mlc_season():
    print("\n📰 Article 3: MLC 2026 — San Francisco Unicorns Dominating Season 4")

    headline = "America's Cricket League Has a Runaway Leader. San Francisco's Unicorns Are the Team to Beat."
    subheadline = "With five wins from eight matches and a four-point cushion at the top, the Unicorns are turning Major League Cricket's fourth season into a one-horse race."

    body = """Major League Cricket is barely a month old and already has a problem most sports leagues would kill for: a team so dominant it's making the competition look one-sided. The San Francisco Unicorns sit atop the Season 4 standings with 10 points from eight matches — five wins, just one loss, and two no-results — a four-point gap over every other franchise.

## The Standings Tell the Story

The Unicorns' latest statement came on Wednesday night, chasing down MI New York's 143 at Marine Park with three balls to spare. It was their sixth straight match without defeat, a streak that has effectively separated the league into two tiers.

Behind them, MI New York sit second on six points, with the defending champions struggling to find the consistency of their title-winning 2025 campaign. They've lost three of eight matches, including two consecutive defeats that dented their playoff positioning.

The Los Angeles Knight Riders, Seattle Orcas, Texas Super Kings, and Washington Freedom are all bunched on four points, separated only by net run rate. With LA still having a game in hand, the race for the remaining playoff spots remains wide open — even as the top appears settled.

| Team | M | W | L | NR | Pts |
|------|---|---|---|----|-----|
| San Francisco Unicorns | 8 | 5 | 1 | 2 | 10 |
| MI New York | 8 | 3 | 3 | 2 | 6 |
| Los Angeles Knight Riders | 7 | 2 | 1 | 4 | 4 |
| Seattle Orcas | 8 | 2 | 4 | 2 | 4 |
| Texas Super Kings | 8 | 2 | 4 | 2 | 4 |
| Washington Freedom | 7 | 2 | 3 | 2 | 4 |

## The League NRIs Can Actually Attend

What makes MLC unique in the Indian cricketing calendar is access. IPL matches happen at 5 AM Pacific. Champions Trophy games require a cable package and an alarm clock. But MLC plays in Grand Prairie, Oakland, and Pomona — venues that NRIs in Texas, the Bay Area, and Southern California can drive to after work.

The league has leaned into this. South African, Caribbean, and English imports mix with Indian stars, and the broadcast deal with JioStar ensures that fans who can't make it to the ground can still watch on the same platform they use for IPL. Season 4 features 34 matches across six franchises, with plans to expand to eight teams by 2027 — and a potential extension into Canada under active consideration.

For diaspora cricket fans who spent decades playing tennis-ball matches in apartment parking lots, watching a professional franchise league in their own time zone is still slightly surreal.

## What's Coming

The business end of the tournament looms. The Unicorns face the Knight Riders on July 11 and Seattle on July 12 — two matches that could either clinch their playoff spot or give the chasing pack a lifeline. MI New York, who own the competition's most expensive roster, need to find their 2025 form fast.

Ownership ambitions continue to scale. MLC's investors have committed over $150 million toward building ten international-standard cricket venues across the US by 2030. The Knight Riders' ownership group — which also runs Kolkata Knight Riders and Trinbago Knight Riders — recently pledged $15-20 million in equity and vowed to bring marquee international players through their global network.

The league itself operates on an NFL-style model where franchises collectively hold roughly 75% ownership — a structure designed to align incentives in ways the IPL's centralized BCCI model does not.

## The Bottom Line

MLC Season 4 is proof that professional cricket in the United States isn't a novelty anymore. It's a functioning league with genuine competition, international talent, and a growing fanbase that skews heavily South Asian. The Unicorns' dominance might be a concern for competitive balance, but it's exactly the kind of storyline that builds narratives — and narratives sell tickets."""

    # Image: Wikimedia Commons for MLC or cricket in USA
    image_url = None
    image_caption = "Major League Cricket action during Season 4 in the United States"
    image_attribution = "Wikimedia Commons"

    # Try cricket-related Commons images
    searches = [
        "Major League Cricket USA",
        "Grand Prairie Stadium cricket",
        "cricket match stadium USA",
        "T20 cricket match"
    ]
    for q in searches:
        commons = fetch_wikimedia_commons_images(q, limit=3)
        for c in commons:
            if commons_relevance_ok(c["title"], "Major League Cricket", "cricket stadium"):
                if verify_image_url(c["url"]):
                    image_url = c["url"]
                    image_caption = f"Cricket action at a Major League Cricket venue in the United States"
                    print(f"  ✓ Using Commons image: {c['title']}")
                    break
        if image_url:
            break

    if not image_url:
        # Try Wikipedia page for MLC
        img = fetch_wikipedia_person_image("Major League Cricket")
        if img and verify_image_url(img):
            image_url = img

    if not image_url:
        # Fallback: generic cricket bat and ball
        commons = fetch_wikimedia_commons_images("cricket bat ball pitch", limit=5)
        for c in commons:
            if verify_image_url(c["url"]):
                image_url = c["url"]
                image_caption = "Cricket equipment on the pitch as MLC Season 4 heats up in the US"
                print(f"  ✓ Using generic cricket Commons image: {c['title']}")
                break

    if not image_url:
        print("  ⚠ No MLC image found — skipping article")
        return None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": "mlc-2026-season-4-san-francisco-unicorns-standings-mi-new-york-nri-cricket-usa",
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "vertical": "cricket-franchise",
        "diaspora_angle": "MLC is the only major cricket league NRIs in the US can attend in person and watch in their own time zone, making it uniquely accessible for diaspora fans.",
        "sources": json.dumps(["SportsCafe", "CricTracker", "ESPN", "CricBuzz", "Wikipedia"]),
        "score_total": 8,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }


# ─── Main ──────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("🏏 The Videshi Sports Writer — 2026-07-09 16:00 PDT")
    print("=" * 60)

    builders = [
        build_article_sky_mlb,
        build_article_womens_test_lords,
        build_article_mlc_season,
    ]

    results = []
    for builder in builders:
        article = builder()
        if article:
            print(f"\n  📝 Inserting: {article['headline'][:60]}...")
            resp = insert_article(article)
            try:
                data = json.loads(resp)
                if isinstance(data, list) and data:
                    print(f"  ✅ Inserted: {data[0].get('slug', 'unknown')}")
                    results.append(data[0].get("slug"))
                elif isinstance(data, dict) and data.get("message"):
                    print(f"  ❌ Error: {data.get('message')}")
                else:
                    print(f"  ⚠ Unexpected response: {resp[:200]}")
            except json.JSONDecodeError:
                print(f"  ❌ Bad response: {resp[:200]}")
        else:
            print("  ⏭ Skipped (no image)")

    print(f"\n{'=' * 60}")
    print(f"✅ Done. {len(results)} article(s) inserted into 'review' status.")
    for slug in results:
        print(f"   • {slug}")
    print("=" * 60)

if __name__ == "__main__":
    main()
