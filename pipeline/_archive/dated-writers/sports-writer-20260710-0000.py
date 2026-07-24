#!/usr/bin/env python3
"""Sports writer — 2026-07-10 00:00 PDT run.
Articles:
  1. England seal first-ever T20 series win over India (4th T20I Bristol result)
  2. Sourav Ganguly inducted into ICC Hall of Fame
  3. France 2-0 Morocco — Mbappe's 8th World Cup goal sends Les Bleus to semis
"""

import json, os, re, subprocess, sys, urllib.parse
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def supabase_post(table, payload):
    """Insert a row into Supabase via curl (proxy-safe)."""
    data = json.dumps(payload)
    result = subprocess.run(
        ["curl", "-sS", "-X", "POST",
         f"{SUPABASE_URL}/rest/v1/{table}",
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=representation",
         "-d", data],
        capture_output=True, text=True, timeout=30
    )
    resp = result.stdout.strip()
    if result.returncode != 0 or '"code"' in resp:
        print(f"  ❌ Insert failed: {resp[:300]}")
        return None
    print(f"  ✅ Inserted into {table}")
    return resp


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        result = subprocess.run(
            ["curl", "-sS", "-A", "TheVideshi/1.0 (thevideshi.com)",
             f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            img = (data.get("originalimage") or {}).get("source") or \
                  (data.get("thumbnail") or {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons for images. Returns list of (title, url) tuples."""
    params = urllib.parse.urlencode({
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    try:
        result = subprocess.run(
            ["curl", "-sS", "-A", "TheVideshi/1.0 (thevideshi.com)", url],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                title = page.get("title", "")
                ii = page.get("imageinfo", [{}])[0]
                thumb = ii.get("thumburl") or ii.get("url")
                if thumb and ii.get("mime", "").startswith("image/"):
                    results.append((title, thumb))
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return []


def verify_image(url):
    """Check image URL returns 200 and >5KB."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}|%{size_download}",
             "-A", "TheVideshi/1.0 (thevideshi.com)", url],
            capture_output=True, text=True, timeout=15
        )
        parts = result.stdout.strip().split("|")
        code = int(parts[0])
        size = int(float(parts[1]))
        return code == 200 and size > 5000
    except:
        return False


# ── ARTICLE 1: England seal first-ever T20 series win over India ─────────────
def article_1():
    print("\n=== Article 1: England seal T20 series win over India ===")
    slug = "england-first-ever-t20-series-win-india-bristol-brook-salt-iyer-80-fifth-loss-nri-2026"
    
    # Image: try Harry Brook (MOTM performer), then Phil Salt, then Jofra Archer
    image_url = None
    image_caption = ""
    image_attribution = "Wikimedia Commons"
    
    for person in ["Harry Brook (cricketer)", "Harry Brook", "Phil Salt", "Jofra Archer"]:
        img = fetch_wikipedia_person_image(person)
        if img and verify_image(img):
            image_url = img
            clean_name = person.split("(")[0].strip()
            image_caption = f"{clean_name} in action for England"
            break
    
    if not image_url:
        # Fallback: Wikimedia Commons
        commons = fetch_wikimedia_commons("England cricket T20 2026")
        for title, url in commons:
            if verify_image(url):
                image_url = url
                image_caption = "England cricket team in T20 International action"
                break
    
    if not image_url:
        print("  ⚠ No image found, skipping article")
        return None
    
    body = """Harry Brook hammered 79 off 35 balls and Phil Salt struck an unbeaten 59 as England sealed their first-ever T20 series victory over India with a comprehensive nine-wicket win at Bristol on Thursday. The result gives England an unassailable 3-0 lead in the five-match series — and extends India's record run of five consecutive T20 defeats in completed matches.

It was supposed to be India's last stand. After the 76-all-out humiliation at Trent Bridge and a four-wicket loss at Old Trafford, the tourists arrived in Bristol needing to start winning or face uncomfortable questions about the direction of their white-ball cricket under new T20 captain Shreyas Iyer.

## One Man Against an Army

Iyer, to his credit, delivered. The 31-year-old chose to bat first and anchored India's innings with an unbeaten 80 off 49 balls — a lone hand of resistance in an otherwise limp batting card. But the captain's defiance only highlighted how completely the rest of the order has collapsed.

Fifteen-year-old Vaibhav Sooryavanshi, playing his fourth T20I, hit Jofra Archer for a six before the Rajasthan Royals connection came back to bite him — Archer had him caught by Sam Curran for 15. It was the second time in as many matches that Archer dismissed the teenager, raising fresh questions about whether the prodigy is being exposed too early at the highest level.

Shivam Dube managed 22 off 23 balls in a 53-run stand with Iyer, but no other Indian batter crossed 15. India finished on 158-7 — a total that looked competitive on paper but proved laughably inadequate against England's firepower.

## Brook and Salt Tear India Apart

The chase was a masterclass in controlled aggression. After Jos Buttler fell early, Brook and Salt shared an unbroken 146-run partnership off just 70 balls. Brook ramped, swept, and drove with the assurance of a man playing a different sport, reaching his fifty in 21 balls and finishing on 79 with eight fours and four sixes.

Salt, who took 10 balls to get off the mark, accelerated steadily and hit the winning runs with 37 balls to spare. Archer's figures of 2-20 rounded off another dominant England performance.

## The Transition Defence Wears Thin

"This is the transition phase and we will be making a lot of mistakes," Iyer said afterward — the same line he offered after the Trent Bridge debacle. For Indian fans watching from living rooms in New Jersey and Sunnyvale, the transition argument is wearing dangerously thin.

The core problem is not a lack of talent. It is a lack of intent from everyone not named Iyer. India's celebrated batting depth — the very quality that powered their T20 World Cup triumph under Suryakumar Yadav in March — has evaporated. The omission of Sanju Samson, the World Cup hero, continues to baffle selectors and social media alike. Reports suggest he is likely to return for the dead-rubber fifth T20I at Southampton on Saturday.

## What NRIs Are Saying

The diaspora reaction has been swift and unsparing. On X and cricket forums, NRI fans are debating whether the BCCI's rotation policy has gone too far, whether Iyer is the right man for the T20 captaincy, and whether the Sooryavanshi experiment should pause until the teenager has more domestic cricket under his belt.

For the millions of Indian Americans who stayed up to watch the Bristol match, the scoreline tells a painful story: five losses in a row, a 15-year-old looking out of his depth against world-class pace, and a captain carrying an entire batting lineup on his back. The final T20I at Southampton on Saturday is now a dead rubber — but for India's pride and Iyer's captaincy, it may be the most important match of the tour."""

    payload = {
        "headline": "Five Losses in a Row. England Seal Their First-Ever T20 Series Win Over India.",
        "subheadline": "Harry Brook's 79 off 35 balls and Phil Salt's unbeaten 59 power England to a nine-wicket win at Bristol. Shreyas Iyer's lone 80 not out cannot save India from a record-extending collapse.",
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "BBC Sport", "url": "https://www.bbc.com/sport/cricket"},
            {"name": "SportsCafe", "url": "https://www.sportscafe.in"},
            {"name": "The Times", "url": "https://www.thetimes.com"}
        ]),
        "diaspora_angle": "India's record five-match T20 losing streak and the omission of World Cup hero Sanju Samson are dominating NRI cricket debates from the Bay Area to the Tri-State area.",
        "score_total": 8,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    return supabase_post("p2_articles", payload)


# ── ARTICLE 2: Sourav Ganguly inducted into ICC Hall of Fame ─────────────────
def article_2():
    print("\n=== Article 2: Sourav Ganguly ICC Hall of Fame ===")
    slug = "sourav-ganguly-icc-hall-of-fame-10th-indian-sachin-tribute-dada-biopic-rajkummar-rao-nri-2026"
    
    # Image: Wikipedia for Sourav Ganguly
    image_url = None
    image_caption = ""
    image_attribution = "Wikimedia Commons"
    
    for name in ["Sourav Ganguly", "Sourav_Ganguly"]:
        img = fetch_wikipedia_person_image(name)
        if img and verify_image(img):
            image_url = img
            image_caption = "Sourav Ganguly, former India captain and newly inducted ICC Hall of Fame member"
            break
    
    if not image_url:
        commons = fetch_wikimedia_commons("Sourav Ganguly cricket")
        for title, url in commons:
            if verify_image(url):
                image_url = url
                image_caption = "Sourav Ganguly at a cricket event"
                break

    if not image_url:
        print("  ⚠ No image found, skipping article")
        return None
    
    body = """On the day he turned 54, Sourav Ganguly received the honour that was decades overdue. The former India captain was inducted into the ICC Hall of Fame on Tuesday, becoming only the 10th Indian men's cricketer — and the 12th Indian overall — to join cricket's most exclusive club.

"Thank you ICC and Chairman Jay Shah for inducting me in the Hall of Fame. It's a huge honour. One of the 10 Indians to be inducted in the Hall of Fame ever. Amazing to be a part of some great names," Ganguly wrote on X, the gratitude unmistakable in a man not known for understatement.

## The Prince of Calcutta

The numbers tell part of the story: 18,575 international runs across 424 matches, 38 centuries, and 107 half-centuries. Seven thousand two hundred and twelve runs in 113 Tests. Eleven thousand three hundred and sixty-three in 311 ODIs. A debut century at Lord's in 1996 — followed by another ton in his very next Test, making him only the third batsman in history to score hundreds in each of his first two Test innings.

But Ganguly's legacy was never really about the numbers. It was about what he did to Indian cricket's spine.

## The Captain Who Changed Everything

When Ganguly took over as captain in 2000, Indian cricket was reeling from the match-fixing scandal. The team was demoralised, the public's trust shattered. What followed was one of the most remarkable rebuilding jobs in sporting history.

He backed young talent — Harbhajan Singh, Yuvraj Singh, Zaheer Khan, Virender Sehwag — when the establishment wanted safe picks. He turned India into a team that fought abroad, not just survived. The 2001 series against Australia, where India came from behind to win 2-1 after following on at Kolkata, remains the gold standard of Test cricket comebacks. Ganguly was the captain who made it happen.

The 2003 World Cup final in Johannesburg. The 2002 NatWest Trophy final, where his shirtless celebration on the Lord's balcony became the defining image of a new, aggressive India. The historic Test series win in Pakistan in 2004. Every milestone was stamped with Ganguly's defiance.

## Sachin's Tribute

His longest-running opening partner, Sachin Tendulkar, was among the first to congratulate him. "There aren't too many surprises left after knowing each other since we were 14. This wasn't one either," Tendulkar wrote. "So happy to see you in the ICC Hall of Fame."

The Tendulkar-Ganguly opening partnership in ODIs was not just a batting combination — it was a cultural event. For Indian fans in the late 1990s and early 2000s, watching them walk out together was appointment television. Their contrasting styles — Tendulkar's precision, Ganguly's audacity — made them the most complete opening pair of their generation.

## Dada Goes to Bollywood

Ganguly's birthday brought a second announcement: the first-look poster for *Dada: The Sourav Ganguly Story*, starring Rajkummar Rao. The biopic, scheduled for May 2027, will cover the arc of Ganguly's career from prodigy to outcast to captain to administrator. For the diaspora, it promises to be a nostalgic trip through two decades of Indian cricket's most turbulent and triumphant years.

## The Hall of Fame Roll Call

Ganguly joins Sunil Gavaskar, Kapil Dev, Sachin Tendulkar, Rahul Dravid, Anil Kumble, Bishan Singh Bedi, Vinoo Mankad, Virender Sehwag, and MS Dhoni in the Indian men's contingent. Diana Edulji and Neetu David represent Indian women's cricket in the Hall. That Ganguly was not already in this company is itself a statement about how long the honour took to arrive.

## Why NRIs Care

For the Indian diaspora, Ganguly represents something specific: the moment Indian cricket stopped being polite. Every NRI who grew up watching him remembers the shirt-waving at Lord's, the refusal to back down against Steve Waugh, the swagger that said India would no longer be grateful just to compete. He made it acceptable to expect victory — and that shift in mentality spread far beyond cricket, into how a generation of Indians abroad carried themselves.

His induction is not a surprise. It is a correction."""

    payload = {
        "headline": "Dada Enters the Pantheon. Sourav Ganguly Inducted Into ICC Hall of Fame.",
        "subheadline": "The former India captain becomes the 10th Indian men's cricketer in cricket's most exclusive club. Sachin Tendulkar's tribute: 'This wasn't a surprise.' A Rajkummar Rao biopic was unveiled the same day.",
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            {"name": "CricTracker", "url": "https://www.crictracker.com"},
            {"name": "CricketAddictor", "url": "https://www.cricketaddictor.com"},
            {"name": "RevSportz", "url": "https://www.revsportz.in"},
            {"name": "Khel Now", "url": "https://www.khelnow.com"}
        ]),
        "diaspora_angle": "Ganguly's fearless captaincy defined how a generation of NRIs see Indian cricket — his Lord's celebration and refusal to back down became symbols of a new Indian confidence that resonated far beyond the boundary.",
        "score_total": 8,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    return supabase_post("p2_articles", payload)


# ── ARTICLE 3: France 2-0 Morocco — Mbappe's WC dominance ───────────────────
def article_3():
    print("\n=== Article 3: France 2-0 Morocco, World Cup QF ===")
    slug = "france-2-0-morocco-world-cup-quarterfinal-mbappe-8th-goal-dembele-semifinal-spain-belgium-nri-2026"
    
    # Image: World Cup social image library (already found)
    image_url = "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/wc-social/ig-fifaworldcup-4e07cb880e65.jpg"
    image_caption = "France celebrate their quarterfinal victory at the 2026 FIFA World Cup"
    image_attribution = "@fifaworldcup / Instagram"
    
    body = """Kylian Mbappe scored his eighth goal of the 2026 World Cup as France dispatched Morocco 2-0 in Thursday's quarterfinal at Gillette Stadium in Foxborough, advancing to a semifinal against the winner of Friday's Spain-Belgium clash. Ousmane Dembele added a second to put the result beyond doubt.

For Morocco, it was a heartbreaking repeat of 2022. For the second consecutive World Cup, Les Bleus ended the Atlas Lions' run — four years ago in the semifinal, now a round earlier.

## Mbappe's Relentless March

France's captain had a penalty saved by Yassine Bounou in the 28th minute — a rare setback that would have deflated lesser players. But Mbappe, operating at a level that defies superlatives, made amends on the hour mark with a curled strike from just inside the box that gave Bounou no chance.

Eight goals in 20 career World Cup appearances. The 27-year-old is now level with Lionel Messi in this tournament's scoring charts and trails the Argentine by just one goal on the all-time World Cup list. At this rate, the record feels less like a question of if than of when.

## Dembele Seals It

Six minutes after Mbappe's opener, Dembele collected a loose clearance and fired a low drive past Bounou to make it 2-0. The Barcelona winger's goal was the insurance France barely needed — Morocco had struggled to create anything meaningful all evening.

"We have to recognise that they're a great team," Morocco coach Mohamed Ouahbi told reporters. "They had better goal-scoring opportunities. We lacked ideas and freshness. It is hard to talk so soon after the match, but it's also difficult to talk about regrets when we got to the quarterfinal."

## A Tournament Taking Shape

The World Cup bracket is narrowing toward its climax, and the four remaining quarterfinal spots tell a story of European dominance and Argentine resilience:

- **France vs. Spain/Belgium** — The first semifinal will pit Mbappe's scoring machine against either Spain's tiki-taka descendants or Belgium's tactical masterclass. Spain face Belgium at SoFi Stadium in Los Angeles on Friday.
- **Norway/England vs. Argentina/Switzerland** — Saturday's doubleheader in Miami and Kansas City will complete the last four. Erling Haaland's Norway, who shocked Brazil 2-1, face a wounded England. Argentina, buoyed by their dramatic 3-2 comeback against Egypt, face penalty-shootout specialists Switzerland.

## The NRI Viewing Experience

For Indian Americans, the World Cup quarterfinals have become a social event that rivals Diwali parties in scale. Watch parties in Edison, Fremont, and Sugar Land drew thousands for the Round of 16 matches, and the quarterfinals — all played in American time zones, at American venues — have made this the most accessible World Cup in NRI history.

France's clinical dispatching of Morocco particularly resonated in diaspora communities with North African connections, but the real draw for most Indian viewers remains Friday's Spain-Belgium match at SoFi and Saturday's Argentina showdown. Messi's potential farewell tournament continues to be the storyline that cuts across every community.

The semifinal schedule — July 14 and July 15 — means NRIs planning Fourth of July weekend leftovers and World Cup semifinal viewing parties are in for a packed few days. For a diaspora that has watched cricket dominate their sporting identity for decades, this World Cup on American soil is writing a new chapter in how Indian Americans engage with global football."""

    payload = {
        "headline": "Mbappe's Eighth Goal Sends France Past Morocco and Into the World Cup Semifinals.",
        "subheadline": "Kylian Mbappe and Ousmane Dembele score in the second half as France eliminate Morocco 2-0 in Foxborough. Les Bleus await the winner of Spain vs. Belgium in the last four.",
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "world-cup",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "NBC Sports", "url": "https://www.nbcsports.com"},
            {"name": "Sporting News", "url": "https://www.sportingnews.com"},
            {"name": "FOX Sports", "url": "https://www.foxsports.com"}
        ]),
        "diaspora_angle": "With all quarterfinals and semifinals on American soil and in American time zones, NRI watch parties from Edison to Fremont are turning this World Cup into the most accessible global football event in diaspora history.",
        "score_total": 8,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    return supabase_post("p2_articles", payload)


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi Sports Writer — 2026-07-10 00:00 PDT")
    print("=" * 60)
    
    results = []
    for fn in [article_1, article_2, article_3]:
        r = fn()
        results.append(r)
    
    ok = sum(1 for r in results if r)
    print(f"\n{'=' * 60}")
    print(f"Done. {ok}/3 articles inserted.")
    print("=" * 60)
