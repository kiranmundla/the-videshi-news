#!/usr/bin/env python3
"""
Videshi Sports Writer — July 11, 2026 4:00 PM PT
2 articles:
1. England whitewash India in T20Is — Buttler's 131 caps off nightmare tour
2. India Women dominate at Lord's in historic first Women's Test
"""

import os, json, requests, urllib.parse, datetime, re, subprocess

# ── Supabase setup ──────────────────────────────────────────────────────
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env("~/.env.supabase")
SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── Image sourcing helpers ──────────────────────────────────────────────
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

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for images. Returns list of image URLs."""
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
            "format": "json"
        }
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
            for page in pages.values():
                ii = page.get("imageinfo", [{}])[0]
                thumb = ii.get("thumburl") or ii.get("url")
                if thumb and ii.get("mime", "").startswith("image/"):
                    results.append({
                        "url": thumb,
                        "title": page.get("title", ""),
                        "width": ii.get("thumbwidth", ii.get("width", 0)),
                        "height": ii.get("thumbheight", ii.get("height", 0)),
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Commons search error: {e}")
    return []

def verify_image_url(url):
    """Verify an image URL returns 200 with image content type and >5KB."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # If Content-Length is missing, read a chunk
        if r.status_code == 200 and "image" in ct:
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception:
        pass
    return False


# ── Insert article ──────────────────────────────────────────────────────
def insert_article(article):
    """Insert article into Supabase p2_articles table."""
    resp = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        if isinstance(data, list) and data:
            print(f"  ✅ Inserted: {data[0].get('headline', '?')}")
            return True
        elif isinstance(data, dict):
            print(f"  ✅ Inserted: {data.get('headline', '?')}")
            return True
    print(f"  ❌ Insert failed ({resp.status_code}): {resp.text[:300]}")
    return False


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: England Whitewash India in T20Is
# ═══════════════════════════════════════════════════════════════════════

def build_article_1():
    print("\n📝 Article 1: England whitewash India in T20Is")

    # Source image — Jos Buttler from Wikipedia
    image_url = fetch_wikipedia_person_image("Jos Buttler")
    image_caption = "Jos Buttler smashed 131 off 64 balls in the 5th T20I at Southampton"
    image_attribution = "Wikimedia Commons"

    # Fallback: try Wikimedia Commons
    if not image_url:
        commons = fetch_wikimedia_commons_images("Jos Buttler cricket England", limit=3)
        for c in commons:
            if verify_image_url(c["url"]):
                image_url = c["url"]
                break

    if image_url and not verify_image_url(image_url):
        print(f"  ⚠ Primary image failed verification, trying Commons fallback")
        commons = fetch_wikimedia_commons_images("England cricket T20 2026", limit=3)
        for c in commons:
            if verify_image_url(c["url"]):
                image_url = c["url"]
                image_caption = "England completed a dominant T20I series whitewash against India"
                break

    headline = "Buttler's Brutal 131 Seals the Humiliation. England Whitewash India 4-0 in T20Is."
    subheadline = "The T20 World Champions failed to win a single completed match on tour. England become the world's number-one ranked T20I side."

    body = """It was supposed to be a fresh start under Shreyas Iyer. Instead, India's tour of England became the longest nightmare in the country's T20I history.

Jos Buttler's savage 131 off just 64 balls — his highest T20I score — powered England to 257 for 3 in the fifth and final match at the Rose Bowl in Southampton on Saturday. India, chasing the improbable, managed 201 for 8 in reply, falling short by 56 runs and completing a comprehensive 4-0 whitewash. The first match was washed out by rain — the only mercy India received in ten days on English soil.

## A Masterclass From Buttler

At 35, Buttler played the innings of a man half his age. He struck 11 fours and nine sixes in a display that mixed vintage power with cold precision. Harry Brook, England's captain and the architect of this series dominance, was unbeaten on 95 off 45 balls at the other end, the pair feasting on an Indian attack that looked spent before the powerplay ended.

Sam Curran, England's utility man, collected three wickets for 36 runs to cap a superb all-round series. Adil Rashid chipped in with two as India's middle order buckled again.

## India's Batting: Bright Spots, Same Outcome

Tilak Varma's explosive 53 off 25 balls — including four sixes — was the kind of counter-attacking innings that will keep selectors interested. Ishan Kishan made 56 off 35, his best knock of the tour, while Sanju Samson hit a brisk 27 off 14 at the top. But wickets fell in clusters. Captain Shreyas Iyer made 28 before holing out, and when Shivam Dube and Suryansh Shedge departed in quick succession, the chase was effectively over.

The pattern has been relentless: India's top order fires in bursts, the middle order caves under pressure, and the bowling lacks the bite to contain modern English batting.

## The Bigger Picture

This isn't just about one bad series. India arrived in England after suffering their first-ever T20I defeat and first-ever T20I series loss to Ireland in a 2-0 sweep in Belfast. That's six consecutive T20I losses for the reigning World Champions — a sequence without precedent in Indian cricket history.

The BCCI has already ordered a performance review of head coach Gautam Gambhir's tenure, focusing on India's alarming white-ball decline since their triumphant 2026 T20 World Cup campaign earlier this year. The Sanju Samson selection controversy — the World Cup hero was dropped for the first three matches — has dominated headlines, while questions about Iyer's captaincy credentials grow louder with each defeat.

England, by contrast, have been clinical. Harry Brook's side has now won 19 of 22 completed T20Is since he took the captaincy. This series win gives them the number-one T20I ranking — a just reward for a squad that has been ruthlessly consistent.

## The Traffic-Jam Finale

As if to summarize India's tour, the team bus got stuck in a traffic jam en route to Southampton for the final match, arriving five minutes after the scheduled toss time and delaying the start by 30 minutes. "I personally feel that we've seen almost everything in this series," Iyer said afterward, mustering a weary smile.

He's not wrong. India's tour of the British Isles has delivered record defeats, selection controversies, a performance review, and now a traffic jam. The only thing missing was a win.

## What NRIs Are Watching Next

For Indian fans in the US and UK who tuned in to this wreckage, the ODI series starting Tuesday at Edgbaston offers a different format — and, hopefully, a different outcome. India's ODI squad includes several senior players rested from the T20Is. But the scars from this whitewash will take longer to heal than a three-day break."""

    sources = json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "KhelNow", "url": "https://www.khelnow.com"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "SportsCafe", "url": "https://www.sportscafe.in"}
    ])

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": "buttler-131-england-whitewash-india-4-0-t20i-series-southampton-number-one-nri-july-2026",
        "body": body,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": sources,
        "score_total": 8,
        "published_at": datetime.datetime.utcnow().isoformat() + "Z",
        "diaspora_angle": "NRI cricket fans are grappling with their World Champions' worst-ever overseas T20I tour — six straight losses across Ireland and England — while England's number-one ranking means the power balance in white-ball cricket has shifted decisively."
    }

    return article


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: India Women Dominate Lord's Historic Test
# ═══════════════════════════════════════════════════════════════════════

def build_article_2():
    print("\n📝 Article 2: India Women dominate Lord's historic Test")

    # Source image — Smriti Mandhana from Wikipedia
    image_url = fetch_wikipedia_person_image("Smriti Mandhana")
    image_caption = "Smriti Mandhana scored 83 in India's first innings at Lord's"
    image_attribution = "Wikimedia Commons"

    # Fallback: Lord's Cricket Ground
    if not image_url:
        image_url = fetch_wikipedia_person_image("Lord's Cricket Ground")
        image_caption = "Lord's Cricket Ground, hosting its first-ever women's Test match"

    if image_url and not verify_image_url(image_url):
        print(f"  ⚠ Primary image failed verification, trying Commons")
        commons = fetch_wikimedia_commons_images("Lord's Cricket Ground London", limit=3)
        for c in commons:
            if verify_image_url(c["url"]):
                image_url = c["url"]
                image_caption = "Lord's Cricket Ground hosted its first-ever women's Test match"
                break

    headline = "Making History, Then Making a Statement. India's Women Take Lord's Apart on Day Two."
    subheadline = "Smriti Mandhana's 83, Deepti Sharma's 57, and a commanding second-innings lead of 269 have turned Lord's first-ever women's Test into India's coronation."

    body = """Lord's has stood for 212 years. It has hosted 150 men's Tests, seen Bradman and Tendulkar and Anderson at their best, and witnessed moments that rewrote the sport. But until Friday, it had never hosted a women's Test match. India made sure the first one would be remembered for more than just the milestone.

## India's First Innings: Setting the Tone

Batting first after England won the toss and chose to bowl, India posted 285 — a total built on elegance and grit in equal measure. Smriti Mandhana was the centrepiece, scoring 83 off 108 balls with 11 fours and a six, batting with the fluency that makes her one of the most watchable players in world cricket. Captain Harmanpreet Kaur contributed a determined 58 off 121 balls, anchoring the middle order through a tricky period, while Deepti Sharma's 57 off 87 gave India's total genuine heft.

Jemimah Rodrigues added a breezy 35, and Richa Ghosh's cameo of 13 off 12 balls showed India's depth with the bat. Sophie Ecclestone, England's star spinner, was the pick of the home bowlers with 3 for 68, but she had to toil through nearly 22 overs to earn those wickets.

## England Crumble

England's reply was a collapse. Bowled out for 170, the hosts trailed by 115 runs on first innings — a deficit that speaks to the gulf in preparation and composure. India's bowlers were relentless on a surface offering just enough for the seamers and spinners alike.

The St John's Wood crowd, which had arrived to celebrate a historic occasion, watched their team unravel. Only a few batters showed sustained resistance as India's bowling attack, led by steady spells across the seam and spin departments, took control.

## Day Two: India Twist the Knife

Rather than rest on their advantage, India came out on Day Two with intent. At stumps, they were 154 for 1 in their second innings — a lead of 269 with nine wickets in hand. Mandhana, batting again with authority, and Yastika Bhatia were at the crease, building an unbroken partnership that has all but ended England's hopes of a competitive finish.

The math is stark. Even if India declare soon, England would need to chase somewhere north of 300 on a pitch that is only going to deteriorate. In women's Test cricket, where draws are common, that kind of fourth-innings target is virtually insurmountable.

## More Than a Match

This Test matters beyond the scorecard. Lord's has been the spiritual home of cricket for over two centuries, and the fact that women hadn't played a Test there until 2026 was a glaring omission. India's women haven't just shown up — they've dominated.

For the Indian diaspora in the UK, this match is a point of deep pride. The India India coach urged her players to "embrace the occasion," and they've done exactly that. NRI families who made the pilgrimage to St John's Wood this weekend have watched their team produce arguably the most significant result in Indian women's cricket history.

## What's at Stake on Day Three

India will look to bat England out of the game entirely before setting a declaration target that makes the result a formality. With two days remaining in the four-day Test, time is on India's side. The question isn't whether India will win — it's whether England can avoid an innings defeat.

The first women's Test at Lord's deserved a spectacle. India has provided one — just not the kind England had hoped for."""

    sources = json.dumps([
        {"name": "Sportradar Live Data", "url": "https://www.sportradar.com"},
        {"name": "CricketNMore", "url": "https://www.cricketnmore.com"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"}
    ])

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": "india-women-dominate-lords-day-2-mandhana-83-deepti-57-lead-269-historic-test-nri-july-2026",
        "body": body,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": sources,
        "score_total": 8,
        "published_at": datetime.datetime.utcnow().isoformat() + "Z",
        "diaspora_angle": "NRI families in the UK packed Lord's for the venue's first-ever women's Test — and watched India's women dismantle the hosts, turning a historic occasion into a statement of cricketing dominance that resonates across the diaspora."
    }

    return article


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("THE VIDESHI — Sports Writer (July 11, 2026)")
    print("=" * 60)

    articles = []

    a1 = build_article_1()
    if a1.get("image_url"):
        articles.append(a1)
    else:
        print("  ⚠ Article 1 has no image, inserting anyway (image may be null)")
        articles.append(a1)

    a2 = build_article_2()
    if a2.get("image_url"):
        articles.append(a2)
    else:
        print("  ⚠ Article 2 has no image, inserting anyway")
        articles.append(a2)

    print(f"\n📰 Inserting {len(articles)} articles...")
    success = 0
    for article in articles:
        if insert_article(article):
            success += 1

    print(f"\n{'=' * 60}")
    print(f"✅ Done: {success}/{len(articles)} articles inserted")
    print(f"{'=' * 60}")
