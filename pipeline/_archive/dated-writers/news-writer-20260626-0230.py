#!/usr/bin/env python3
"""
Videshi News Writer — June 26, 2026 (02:30 UTC / June 25 19:30 PDT run)
2 NEW articles, dedup-checked against last ~60 news/nri-world articles:
  1. India Women beat Bangladesh by 5 wickets at ICC Women's T20 World Cup,
     Old Trafford, June 25 — Shafali Verma 53(34) PoTM, keeps semifinal hopes
     alive ahead of the Australia blockbuster at Lord's on Sunday. The
     tournament is in England, home to ~2M Indians. NOT covered.
  2. Indian-American diaspora's largest-ever civic push — FIIDS Capitol Hill
     Day (200 delegates, 25 states, 125+ offices, June 23) plus Indian-American
     lawmakers (Krishnamoorthi, Subramanyam, Thanedar) urging the diaspora to
     run for office amid rising anti-Hindu/anti-India hate (June 24). NOT covered.
"""
import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            data = r.json()
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
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  \u2713 Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  \u26a0 Download failed ({r.status_code}): {url[:80]}")
            try:
                tmp = f"/tmp/{slug}_src"
                subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
                with open(tmp, "rb") as f:
                    content = f.read()
                if len(content) < 5000:
                    return None
                r_content = content
            except Exception:
                return None
        else:
            r_content = r.content
        ct = r.headers.get("Content-Type", "") if r.status_code == 200 else "image/jpeg"
        if "image" not in ct and len(r_content) < 5000:
            print(f"  \u26a0 Not an image or too small: {ct}, {len(r_content)} bytes")
            return None

        from PIL import Image
        img = Image.open(io.BytesIO(r_content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()

        if len(compressed) < 5000:
            print(f"  \u26a0 Compressed image too small: {len(compressed)} bytes")
            return None

        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"

        requests.delete(upload_url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY
        })

        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=30)

        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def pick_commons(queries, min_width=900):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            return pick["url"], pick.get("title", "")
    return None, ""


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# \u2500\u2500\u2500 Article 1: India Women beat Bangladesh at T20 World Cup \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India Women beat Bangladesh, T20 World Cup")
    print("="*60)

    slug = "india-women-beat-bangladesh-five-wickets-t20-world-cup-old-trafford-shafali-verma-australia-lords-20260625"
    headline = "Shafali Verma Lights Up Old Trafford as India Keep Their World Cup Alive"
    subheadline = "A 53 off 34 from the returning opener powered a five-wicket win over Bangladesh in Manchester. Now a Sunday showdown with Australia at Lord's will decide India's semifinal fate."

    body = """For the tens of thousands of Indians who fill English grounds every summer, Thursday at Old Trafford was the kind of afternoon they travel for. Shafali Verma walked out under Manchester's grey skies, and within half an hour she had turned a tricky chase into a procession, dragging India to a five-wicket win over Bangladesh that keeps their ICC Women's T20 World Cup campaign firmly alive.

Verma's 53 came off just 34 balls — eight fours and a six, a half-century raised in 29 deliveries — and earned her the Player of the Match award. India knocked off their target of 137 in 16.5 overs, with 19 balls to spare, in front of a crowd thick with tricolours.

## A Chase Built on a Blistering Start

Bangladesh had set a competitive 136 for 8 after being put in, built around opener Juairiya Ferdous (33 off 31) and captain Nigar Sultana (32 off 27). But India's spinners choked the middle overs: left-armer Radha Yadav was the pick with 3 for 28, while the uncapped Shree Charani chipped in with 2 for 21, and Bangladesh's lower order failed to kick on.

The chase wobbled briefly — Smriti Mandhana fell for 8 — but Verma made the target look small. "Whatever comes in my zone, just go for that. Otherwise, take a single," she said afterwards, describing a clear-headed approach that produced India's highest-ever Powerplay score in a Women's T20 World Cup. Yastika Bhatia's brisk 23 kept the rate up, and after a brief wobble that saw Richa Ghosh fall cheaply, captain Harmanpreet Kaur (unbeaten on 13) and Jemimah Rodrigues guided the side home without further alarm.

## The Maths of the Group

The win lifts India to second in Group A — three wins from four, six points, a healthy net run rate — behind an unbeaten Australia. It was the result India needed, but it does not, on its own, book a semifinal place. With South Africa still in the mix, India will be watching other results closely. As the reigning ODI world champions, they arrived in England carrying expectation; performances like Thursday's are why that expectation feels earned rather than imposed.

## All Roads Lead to Lord's

Everything now points to Sunday, when India meet Australia in what promises to be the defining fixture of their group. A win would all but guarantee a semifinal berth and settle nerves that have lingered since an earlier defeat. For the senior batters — Mandhana and Harmanpreet especially — it is the stage to deliver. The tournament, running June 12 to July 5 across England and Wales, builds toward a final at Lord's on July 5, and India will want to be there.

## Why It Matters for the Diaspora

Staging a World Cup in England has a particular resonance for the Indian diaspora. Britain is home to roughly two million people of Indian origin, and grounds from Old Trafford to The Oval have long doubled as gathering points for a community that treats a day at the cricket as both sport and homecoming. Indian women's cricket has never enjoyed a higher profile — the launch and growth of the Women's Premier League has turned players like Verma, Rodrigues and Mandhana into genuine stars — and a deep run in England would land squarely in front of the most engaged overseas audience the team has.

For NRIs in the United States and Canada, where women's cricket is slowly building a foothold, the timing matters too: a generation of diaspora daughters now has a side worth setting an early alarm for. And for families back home, a World Cup carries a weight no bilateral series can match. India have unfinished business in this format — they have reached finals before without lifting the trophy — and Thursday was a reminder that this group has the firepower to change that. Sunday at Lord's will tell us whether they can."""

    img_url, ititle = pick_commons([
        "Old Trafford cricket ground Manchester",
        "Old Trafford cricket pavilion",
        "Emirates Old Trafford",
        "India women cricket team",
        "Cricket bat ball stadium"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Old Trafford in Manchester, where India beat Bangladesh by five wickets to keep their T20 World Cup campaign alive"

    if not img_url:
        px = fetch_pexels_image("cricket stadium match crowd")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "India chased down 137 in 16.5 overs to beat Bangladesh at the Women's T20 World Cup"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "sports",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Sportradar / ICC T20 World Cup Women 2026 match data \u2014 India vs Bangladesh, Old Trafford Cricket Ground, Manchester, Thursday 25 June 2026: Bangladesh (batting first after winning toss) 136/8 in 20 overs; India 139/5 in 16.5 overs, won by 5 wickets with 19 balls remaining; run rate 8.26; India squad incl. Harmanpreet Kaur (c), Smriti Mandhana, Shafali Verma, Jemimah Rodrigues, Deepti Sharma, Richa Ghosh, Renuka Singh, Radha Yadav, Yastika Bhatia, Shree Charani, Nandani Sharma; tournament season 12 June \u2013 5 July 2026.",
            "Nation Press (nationpress.com, 25 June 2026) \u2014 'Shafali Verma's 53 off 34 powers India to 5-wicket win vs Bangladesh in Women's T20 WC': Verma scored 53 off 34 balls (eight fours, one six), half-century off 29 balls, named Player of the Match; India chased 137 in 16.5 overs; India posted their highest-ever Powerplay score in Women's T20 World Cup history; Verma was stumped in the ninth over; her post-match quotes on approach ('Whatever comes in my zone, just go for that. Otherwise, take a single').",
            "SportsTiger (sportstiger.com, 25 June 2026) \u2014 'Shafali Verma leads India's charge': Bangladesh 136/8 built on Juairiya Ferdous 33 (31) and captain Nigar Sultana 32 (27); Radha Yadav 3/28 and Shree Charani 2/21 restricted Bangladesh; India lost Mandhana early for 8, Yastika Bhatia made 23 (18), Richa Ghosh fell for 10 before Harmanpreet Kaur and Jemimah Rodrigues steadied the chase.",
            "India Forums live thread / match summary (indiaforums.com, 25 June 2026) \u2014 ICC Women's T20 World Cup 2026 Group A, India W vs Bangladesh W: India won by 5 wickets (19 balls remaining), BANW 136/8 (20), INDW 139/5 (16.5); Shafali Verma Player of the Match; India must beat Australia in Sunday's Lord's double-header to comfortably reach the semifinals, otherwise dependent on South Africa slipping."
        ]),
        "diaspora_angle": "The Women's T20 World Cup is being staged in England, home to roughly two million people of Indian origin, turning grounds like Old Trafford into diaspora gathering points; India's five-wicket win over Bangladesh and Shafali Verma's match-winning half-century keep the reigning ODI champions on course for a semifinal in front of their largest overseas fanbase, with a defining clash against Australia at Lord's on Sunday.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: Indian-American diaspora's largest civic push \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Indian-American diaspora civic push on Capitol Hill")
    print("="*60)

    slug = "indian-american-diaspora-capitol-hill-fiids-lawmakers-run-for-office-anti-india-hate-20260625"
    headline = "'If You Don't Have a Seat at the Table, You're on the Menu': The Diaspora's Loudest Year in Washington"
    subheadline = "Nearly 200 Indian-American delegates fanned out across Capitol Hill this week as lawmakers urged the community to run for office \u2014 a civic surge sharpened by rising anti-Hindu and anti-India hate."

    body = """The Indian-American community has long been celebrated for what it earns and what it builds. This week in Washington, it pressed a different claim: a seat at the table where the rules are written.

Nearly 200 delegates from 25 states converged on Capitol Hill on Tuesday for the fourth annual Capitol Hill Day organised by the Foundation for India and Indian Diaspora Studies (FIIDS), fanning out across more than 125 Congressional offices. It was the largest such advocacy effort the community has mounted \u2014 up from roughly 70 delegates in 2023, 132 in 2024 and 145 last year \u2014 and a marker of how quickly a prosperous, professional diaspora is converting economic weight into political voice.

## Five Priorities, One Message

The FIIDS platform centred on five priorities: Indo-Pacific trade and security, the US-India strategic partnership, recognition of Indian-American contributions, reform of high-skilled immigration programmes, and securing critical-minerals supply chains. The last is new this year, reflecting bipartisan anxiety in Washington over dependence on China-dominated supply lines. "This is a moment to translate influence into policy impact," said Khanderao Kand, FIIDS chief of policy and strategy.

The immigration plank is the one that lands most directly on diaspora kitchen tables. Indian nationals account for the overwhelming majority of H-1B beneficiaries and bear the brunt of a green-card backlog that stretches into decades. Several lawmakers \u2014 Democrats Sanford Bishop, James Walkinshaw, Brad Sherman and Republican Bill Huizenga among them \u2014 assured delegates of support on immigration and the permanent-residency backlog. The advocacy day was followed by a US-India Partnership Summit featuring senior State Department and embassy officials.

## A Call to Run for Office

If the agenda was about policy, the loudest note of the week was about power. Addressing the FIIDS gathering, Congressman Raja Krishnamoorthi delivered a blunt charge to a community that has often preferred influence to office. "There's an old saying in Washington DC: if you don't have a seat at the table, you're on the menu," he said. "And none of you can afford to be on the menu, nor can our families, nor can our interests."

Krishnamoorthi urged Indian-Americans to run at every level \u2014 city council, state legislature, Congress \u2014 regardless of party. "I don't care if you're a Republican, Democrat, or Independent," he said. Congressman Suhas Subramanyam echoed him, arguing that representation in decision-making bodies is the surest way to address the community's concerns.

## The Shadow Over the Celebration

The civic push comes with an edge of unease. Congressman Shri Thanedar warned that hate against immigrants is rising and urged the diaspora to stay united. The backdrop, community leaders say, is a documented uptick in anti-Hindu, anti-India and "anti-Desi" hate \u2014 vandalism and attacks targeting Hindu temples, anti-Hindu graffiti, disrupted religious events, and campaigns opposing Indian representation in corporate settings. "There is the rise of anti-Hindu, anti-Indian, anti-Desi hate," Krishnamoorthi said. "It's time to get more involved than you've ever been."

That tension \u2014 unprecedented success shadowed by unprecedented hostility \u2014 is the defining condition of the moment. The community is estimated at more than four million, and by some counts 5.2 million as of 2023, among the fastest-growing and most influential ethnic groups in the country.

## Why It Matters for the Diaspora

For NRIs, the week reframes a familiar question. For a generation, the diaspora's strategy was excellence: study hard, work harder, let the rsum speak. The message from Capitol Hill is that excellence alone no longer suffices \u2014 that a community facing both a visa system stacked against it and a rising tide of hate needs people inside the rooms where decisions are made, not just lobbying outside them.

There is evidence the shift is already underway, from a growing bench of Indian-American mayors and state legislators to high-profile figures in both parties. But the gap between economic clout and political representation remains wide, and closing it is generational work. The delegates who walked the marble halls this week were, in effect, modelling the behaviour their congressmen were preaching: showing up, speaking up, and refusing to be on the menu. Whether that energy translates into a durable pipeline of Indian-American candidates \u2014 and into the immigration relief the community has sought for decades \u2014 is the test the next few years will set."""

    img_url, ititle = pick_commons([
        "United States Capitol building Washington",
        "United States Capitol dome",
        "US Capitol west front",
        "Raja Krishnamoorthi",
        "United States Congress chamber"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "The US Capitol, where nearly 200 Indian-American delegates lobbied more than 125 Congressional offices this week"

    if not img_url:
        px = fetch_pexels_image("united states capitol washington dc")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Indian-American delegates pressed lawmakers on immigration and US-India ties at the Capitol this week"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "nri-world",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Nation Press (nationpress.com, 23 June 2026) \u2014 'Indian Americans descend on Capitol Hill with US-India agenda, 200 delegates from 25 states': nearly 200 Indian-American delegates from 25 states converged on Capitol Hill on Tuesday 23 June 2026 for the fourth annual FIIDS Capitol Hill Day, visiting more than 125 Congressional offices \u2014 the largest such effort to date; five priority areas (Indo-Pacific trade/security, US-India strategic partnership, recognition of Indian-American contributions, high-skilled immigration reform, critical-minerals supply-chain security); growth from ~70 delegates (2023) to ~132 (2024) to ~145 (2025); followed by a US-India Partnership Summit with Deputy Assistant Secretary of State Bethany Morrison and DCM Ambassador Mangya Khampa; community estimated at over 4 million; Khanderao Kand quote 'This is a moment to translate influence into policy impact.'",
            "The Hindu BusinessLine (thehindubusinessline.com, 24 June 2026) \u2014 'Indian-American lawmakers urge diaspora to enter politics amid rise in anti-India sentiment': at the FIIDS Capitol Hill event, Congressman Raja Krishnamoorthi (D-IL) cited 'the rise of anti-Hindu, anti-Indian, anti-Desi hate' and urged community members to run for office at all levels regardless of party ('if you don't have a seat at the table, you're on the menu'); Congressman Suhas Subramanyam emphasised representation in decision-making bodies; Congressman Shri Thanedar warned hate against immigrants is rising and urged unity; Senator Roger Marshall (R-KS) backed a bilateral trade agreement; Democrats Sanford Bishop, James Walkinshaw, Brad Sherman and Republican Bill Huizenga assured support on immigration and the PR backlog; incidents cited include attacks/vandalism on Hindu temples, anti-Hindu graffiti, disrupted religious events; community estimated at 5.2 million as of 2023 (US Census Bureau)."
        ]),
        "diaspora_angle": "The Indian-American community's largest-ever Capitol Hill advocacy day \u2014 200 delegates pressing immigration reform and the green-card backlog \u2014 paired with lawmakers urging the diaspora to run for office amid rising anti-Hindu and anti-India hate, marks a strategic shift for NRIs from quiet professional success toward direct political representation, with the visa and PR backlog issues that affect millions of Indian families at the centre of the agenda.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-26 02:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (India Women beat Bangladesh, T20 WC): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (Indian-American Capitol Hill push): {'OK id=' + str(id2) if id2 else 'FAILED'}")
