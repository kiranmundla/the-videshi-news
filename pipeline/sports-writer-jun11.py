#!/usr/bin/env python3
"""Sports writer for The Videshi — June 11, 2026 run.
2 articles:
1. Indian-origin footballers at FIFA World Cup 2026
2. Nitish Kumar Reddy's ODI opportunity with Hardik Pandya out
"""
import os, json, requests, urllib.parse, datetime, subprocess

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = 'TheVideshi/1.0 (thevideshi.com)'

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query", "generator": "search", "gsrsearch": query,
        "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for page in pages.values():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                w = ii.get("width", 0)
                if url and "image" in mime and w >= 300:
                    results.append(url)
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels(query):
    if not PEXELS_KEY:
        return None
    try:
        result = subprocess.run([
            'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
            f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape'
        ], capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"].get("large2x") or photos[0]["src"].get("large")
            print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct:
            if cl > 5000:
                return True
            # HEAD might not return Content-Length
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            first = next(r2.iter_content(8192), b"")
            if len(first) > 5000:
                return True
    except:
        pass
    return False

def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS_SB, json=article)
    if r.status_code in (200, 201):
        res = r.json()
        if isinstance(res, list) and res:
            print(f"  ✓ INSERTED: {res[0].get('headline','?')[:60]}... (id: {res[0].get('id','?')[:12]})")
        else:
            print(f"  ✓ INSERTED (raw response)")
        return True
    else:
        print(f"  ✗ FAILED ({r.status_code}): {r.text[:300]}")
        return False

def source_image(person_names, commons_queries, pexels_query):
    """Try Wikipedia persons, then Commons, then Pexels. Returns (url, caption, attribution) or None."""
    for name in person_names:
        url = fetch_wikipedia_person_image(name)
        if url and validate_image(url):
            return url, f"{name}", "Wikimedia Commons"
    for q in commons_queries:
        urls = fetch_wikimedia_commons(q)
        for u in urls:
            if validate_image(u):
                return u, q, "Wikimedia Commons"
    if pexels_query:
        url = fetch_pexels(pexels_query)
        if url and validate_image(url):
            return url, pexels_query, "Pexels"
    return None

# ── ARTICLE 1 ──
def write_article_1():
    print("\n═══ ARTICLE 1: Indian-Origin Footballers at FIFA World Cup 2026 ═══")

    headline = "Two Players of Indian Heritage Will Take the Pitch at This World Cup. Neither Plays for India."
    subheadline = "Sarpreet Singh of New Zealand and Nishan Velupillay of Australia carry desi roots onto the biggest stage in football — a bittersweet milestone for 745 million Indian fans."
    slug = "sarpreet-singh-nishan-velupillay-indian-origin-players-fifa-world-cup-2026-nri"

    body = """As the 2026 FIFA World Cup kicked off on Wednesday with Mexico hosting South Africa at the Estadio Azteca in Mexico City, Indian football fans found themselves in a familiar position — watching from the sidelines, cheering for a national team that is nowhere near the tournament. India, home to an estimated 745 million football fans, did not come close to qualifying.

But tucked inside the squad lists of two participating nations are names that carry unmistakably Indian roots. Sarpreet Singh, a midfielder with New Zealand, and Nishan Velupillay, a forward with Australia, are the two players of Indian heritage who will feature in the expanded 48-team tournament. Their stories, separated by thousands of kilometres but connected by a shared thread of diaspora identity, offer NRI fans something rare: a personal stake in the beautiful game's grandest event.

## The Punjabi Who Played for Bayern Munich

Sarpreet Singh was born in Auckland to Punjabi parents whose family traces its origins to Jalandhar. His mother, Sarabjit, enrolled him at the Wynton Rufer Soccer Academy when he was seven years old — a decision that would eventually take him to one of the most storied clubs in world football.

In 2019, Singh signed with FC Bayern Munich, becoming the first player of Indian heritage to represent the German giants. The move made global headlines, particularly across the Indian diaspora, where it was seen as a breakthrough moment for South Asian representation in European football.

His time at Bayern was marked more by promise than playing time. Injuries and loan spells across Germany, Portugal, and Serbia followed. Singh returned to Wellington Phoenix in the A-League ahead of the 2026 World Cup, determined to rebuild his career on home soil.

Now 27 and wearing the number 10 jersey for New Zealand, Singh has been candid about the weight of his heritage on this stage. "I don't say it's added pressure. I just want to do my best to lift the names of Indian people, and there is no better stage to do it than the World Cup," he told *The Mint* in a recent interview. "I see it as a responsibility to do my best and even inspire the next generation."

New Zealand's first World Cup match is against Iran on June 15 in Los Angeles — prime time for the large Indian diaspora on the US West Coast.

## A Tamil Kid from Melbourne's Suburbs

Nishan Velupillay's path to the World Cup began in the Melbourne suburb of Mulgrave. His father, Sasinath, is of Sri Lankan Tamil descent with Malaysian roots; his mother, Gillian, is Anglo-Indian. He attended Mazenod College and began playing at Glen Eira FC before working his way through the Melbourne Victory academy.

Velupillay announced himself to Australian football in dramatic fashion, scoring on his international debut when he came off the bench against China and netted within minutes to seal a 3-1 win in a World Cup qualifier. He has since earned seven senior caps and scored three goals for the Socceroos.

At 23, Velupillay represents a new generation of Australian players with South Asian heritage — a demographic that has historically been underrepresented in the country's football culture. His inclusion in Australia's World Cup squad has resonated across Tamil and Indian communities in Melbourne and beyond.

## Why This Matters for the Diaspora

For the estimated 5.4 million people of Indian origin living in the United States, the 2026 World Cup is uniquely accessible. With matches spread across 16 cities in the US, Canada, and Mexico, attending a game has never been easier for NRI families. And while there is no Indian flag to wave, Singh and Velupillay offer the next best thing — visible representation of desi heritage on the sport's ultimate stage.

Their presence also underscores a painful truth: India, ranked 124th by FIFA, remains decades away from World Cup contention. The All India Football Federation has spoken of long-term development plans, but for now, the country's football ambitions are carried by its children abroad.

The World Cup runs through July 19, with the final at MetLife Stadium in New Jersey. For fans of Indian origin, the tournament has at least two reasons to tune in — both wearing jerseys that are not India's, but carrying names that are undeniably Indian.

*Sources: Sporting News, The Mint, FIFA, Wellington Phoenix FC*"""

    print("  Sourcing images...")
    result = source_image(
        ["Sarpreet Singh (footballer)", "Sarpreet Singh", "Nishan Velupillay"],
        ["Sarpreet Singh footballer New Zealand", "FIFA World Cup 2026 opening ceremony"],
        "FIFA World Cup football stadium crowd"
    )
    if not result:
        print("  ✗ No valid image found, skipping")
        return False

    img_url, img_subj, img_attr = result
    if "Sarpreet" in img_subj or "sarpreet" in img_url.lower():
        img_caption = "Sarpreet Singh, New Zealand's Punjabi-origin midfielder heading to the 2026 FIFA World Cup"
    elif "Nishan" in img_subj or "Velupillay" in img_subj:
        img_caption = "Nishan Velupillay, Australia's forward of Sri Lankan Tamil descent, in the World Cup squad"
    else:
        img_caption = "The 2026 FIFA World Cup brings football's biggest stage to North America"

    print(f"  Using: {img_url[:80]}... ({img_attr})")

    return insert_article({
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "diaspora-sports",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "sources": json.dumps(["Sporting News", "The Mint", "FIFA", "Wellington Phoenix FC"]),
        "diaspora_angle": "Two players of Indian heritage — one Punjabi, one Tamil — represent New Zealand and Australia at the World Cup, giving NRI fans a personal connection to the tournament in their backyard.",
        "published_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    })


# ── ARTICLE 2 ──
def write_article_2():
    print("\n═══ ARTICLE 2: Nitish Kumar Reddy's ODI Opportunity ═══")

    headline = "Hardik Is Out. Nitish Kumar Reddy Has Three Matches to Prove He Belongs."
    subheadline = "With Pandya sidelined by a last-minute leg sprain and Kohli nursing a hamstring injury, India's ODI series against Afghanistan gives the young all-rounder a rare opening."
    slug = "nitish-kumar-reddy-odi-opportunity-hardik-pandya-injury-afghanistan-dharamsala-nri"

    body = """When Hardik Pandya was cleared fit for the Afghanistan ODI series on Tuesday, it looked like business as usual for India's pace-bowling all-rounder. By Wednesday, a last-minute leg sprain had ruled him out entirely. One day later, the opening that every young all-rounder in Indian cricket has been waiting for was wide open.

Nitish Kumar Reddy, the 21-year-old from Visakhapatnam who burst onto the scene during the Australia Test tour in 2024-25, is now the frontrunner to fill Pandya's role in the three-match ODI series against Afghanistan. The first ODI is on June 13 at Dharamsala, followed by matches in Lucknow on June 17 and Chennai on June 20.

## The All-Rounder India Has Been Looking For

India's search for a reliable backup to Hardik Pandya in white-ball cricket has been one of the most persistent selection puzzles of the post-2023 World Cup cycle. Pandya's body has been a constant concern — his workload is managed meticulously, and every series carries the risk of a last-minute withdrawal.

Reddy, who was initially picked as a batting all-rounder for the Test squad to Australia, showed his mettle with a courageous century at the MCG that turned public perception from promising youngster to genuine prospect. In IPL 2026, he reinforced that impression with consistent performances for Sunrisers Hyderabad, scoring over 400 runs while providing useful medium-pace overs.

What makes Reddy's case compelling is his versatility. He can bat in the middle order — anywhere from five to seven — and bowl tight, disciplined medium-pace spells that extract movement when conditions allow. For India's ODI setup, where the balance between five bowlers and a deep batting lineup is always a tightrope, that dual capability is invaluable.

## The Broader Selection Picture

Pandya's absence is not the only gap head coach Gautam Gambhir and captain Shubman Gill need to manage. Virat Kohli is also missing, ruled out with a hamstring injury sustained during the IPL. Yashasvi Jaiswal has been named as his replacement at number three, while KL Rahul and Shreyas Iyer anchor the middle order.

Washington Sundar, fresh from a superb all-round performance in the one-off Test — where he scored an unbeaten 52 and took four wickets in the second innings as India won by an innings and 300 runs — is likely to be the primary spin-bowling all-rounder. But India's template in ODIs increasingly requires a pace option at seven or eight who can bat, exactly the role Pandya has owned for five years.

If Reddy gets the nod, he will be measured against that benchmark. Three matches may not definitively answer whether he can be India's second-choice pace all-rounder, but they are enough to show whether he belongs in the conversation.

## Two Uncapped Bowlers Add Intrigue

The series also offers potential debuts for Harsh Dubey, the Vidarbha leg-spinner who claimed 69 wickets in the Ranji Trophy 2024-25 to become the tournament's leading wicket-taker, and Gurnoor Brar, the towering Punjab pacer who stands six feet five inches tall and impressed during the Vijay Hazare Trophy.

Both represent India's deepening domestic talent pool — a pipeline that has already produced Manav Suthar, whose seven-wicket debut in the one-off Test last week earned him a county contract with Warwickshire within 48 hours.

## What NRI Fans Should Watch For

For diaspora fans tracking India's 2027 World Cup preparations, this series is the first meaningful data point. India play 20 ODIs before the World Cup in South Africa, and the Afghanistan series is where the rebuild begins.

Gill's captaincy in the 50-over format will be scrutinised — he has won every Test he has captained but lost every ODI series. Rohit Sharma's form will be under the microscope after he was cleared fit. And Jaiswal at number three, replacing the irreplaceable Kohli, will face a challenge that is as much psychological as it is technical.

But the most consequential storyline may belong to Nitish Kumar Reddy. In a team defined by its specialist superstars, the all-rounder's role has always been the hardest to fill. If Reddy can bowl ten tight overs and score 30-40 crucial runs in the death overs across three games, he will have done more than enough to keep his name in the selectors' minds when the World Cup squad is finalised.

The first ODI begins at 1:30 PM IST on Friday at the HPCA Stadium in Dharamsala — 4:00 AM Eastern, 1:00 AM Pacific for NRI fans willing to set an early alarm.

*Sources: RevSportz, Bhaskar English, Sportskeeda, BCCI*"""

    print("  Sourcing images...")
    result = source_image(
        ["Nitish Kumar Reddy", "Nitish Kumar Reddy (cricketer)", "Hardik Pandya"],
        ["Nitish Kumar Reddy cricket India", "HPCA Stadium Dharamsala cricket"],
        "cricket stadium India mountains"
    )
    if not result:
        print("  ✗ No valid image found, skipping")
        return False

    img_url, img_subj, img_attr = result
    if "Nitish" in img_subj:
        img_caption = "Nitish Kumar Reddy, India's young pace-bowling all-rounder, gets his chance in ODIs"
    elif "Hardik" in img_subj or "Pandya" in img_subj:
        img_caption = "Hardik Pandya's leg sprain has opened the door for Nitish Kumar Reddy in the Afghanistan ODI series"
    elif "HPCA" in img_subj or "Dharamsala" in img_subj:
        img_caption = "The HPCA Stadium in Dharamsala, venue for the first India-Afghanistan ODI on June 13"
    else:
        img_caption = "India's ODI series against Afghanistan begins at Dharamsala on June 13"

    print(f"  Using: {img_url[:80]}... ({img_attr})")

    return insert_article({
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "sources": json.dumps(["RevSportz", "Bhaskar English", "Sportskeeda", "BCCI"]),
        "diaspora_angle": "The Afghanistan ODI series is the first step in India's 2027 World Cup rebuild — NRI fans can watch the emergence of the next generation including Nitish Kumar Reddy.",
        "published_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    })


if __name__ == "__main__":
    print(f"Sports writer run: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    r1 = write_article_1()
    r2 = write_article_2()
    print(f"\n═══ SUMMARY ═══")
    print(f"  {'✓' if r1 else '✗'} Article 1 (Indian-origin WC footballers)")
    print(f"  {'✓' if r2 else '✗'} Article 2 (Nitish Kumar Reddy ODI)")
    total = sum([r1, r2])
    print(f"  {total}/2 articles inserted")
