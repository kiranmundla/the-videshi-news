#!/usr/bin/env python3
"""
Entertainment Writer — 2026-05-30
Publishes 4 articles to The Videshi:
1. Gullak Season 5 returns on SonyLIV June 5
2. Ramayana eyeing San Diego Comic-Con trailer debut + October 30 release
3. Patriot (Mammootty-Mohanlal) hits ZEE5 June 5 after theatrical disappointment
4. Ranbir Kapoor says playing Lord Ram changed him as a father
"""

import json, os, sys, time, uuid, re
import requests, urllib.parse
from datetime import datetime, timezone

# ── Load env ──
env_file = os.path.expanduser("~/.env.supabase")
if os.path.exists(env_file):
    for line in open(env_file):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"')

# ── Image helpers ──
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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels. Use curl underneath (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            cmd = [
                "curl", "-sS",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3",
                "-H", f"Authorization: {PEXELS_KEY}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Verify image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET for servers that don't return Content-Length on HEAD
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def sb_insert(table, row):
    """Insert a row into Supabase and return the inserted data."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=row,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) else data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


def sb_patch(table, filters, updates):
    """Patch rows in Supabase."""
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=updates,
        timeout=30
    )
    if r.status_code in (200, 204):
        print(f"  ✓ Patched {table}")
    else:
        print(f"  ⚠ Patch warning ({r.status_code}): {r.text[:200]}")


# ── Articles ──
articles = [
    {
        "headline": "Gullak Season 5 Drops on SonyLIV June 5. India's Most Relatable Family Is Back.",
        "subheadline": "TVF's beloved Mishra family returns with new struggles, small upgrades, and Shanti Mishra's unexpected turn as a social media personality.",
        "slug": "gullak-season-5-sonyliv-june-5-mishra-family-tvf-nri-20260530",
        "category": "entertainment",
        "vertical": "entertainment",
        "image_person": "Jameel Khan actor",
        "image_pexels_query": "Indian family living room",
        "image_pexels_fallback": "Indian household warm",
        "sources": [
            {"name": "Bombay Times", "url": "https://www.bombaytimes.com"},
            {"name": "SonyLIV", "url": "https://www.sonyliv.com"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Gullak"}
        ],
        "body": """The Mishra family is coming home again. Gullak Season 5, the TVF-produced web series that has quietly become one of the most cherished shows in Indian streaming, will premiere on SonyLIV on June 5, 2026.

For a show that has never relied on big-budget spectacle or celebrity star power, Gullak's longevity is remarkable. Five seasons in, the series continues to draw viewers who see their own families reflected in the small-town household of Santosh and Shanti Mishra — played once again by Jameel Khan and Geetanjali Kulkarni — and their two sons, Annu and Aman.

## What's Changed This Time

Season 5 picks up with the Mishra household in quiet flux. There are small upgrades at home — the kind that middle-class Indian families celebrate as milestones. But beneath the surface, the emotional landscape has shifted.

Annu, the elder son played by Vaibhav Raj Gupta, is navigating the weight of expectations and self-doubt that comes with early adulthood in a family where resources are limited but aspirations are not. Aman, the younger son played by Harsh Mayar, appears more withdrawn this season, carrying struggles he hasn't yet articulated to his parents.

The most intriguing new thread involves Shanti Mishra herself. In a development that mirrors millions of real Indian households, she's found an unexpected audience through some kind of online presence — a subplot that speaks directly to how social media has reshaped even the most traditional family dynamics.

"With each season, Gullak has come closer to viewers because the Mishras feel like people we all recognise," the makers said in a statement. "This chapter reflects how middle-class India is changing, while still holding on to its warmth and simplicity."

## Why the Diaspora Keeps Coming Back

For NRIs, Gullak has always been more than entertainment. It's a window into the India they left behind — the chai-and-conversation rhythms of a household where the biggest drama is a phone bill or a neighbor's gossip. The show's genius has always been its refusal to manufacture conflict. Life provides enough.

The series debuted in 2019 on TVF Play and SonyLIV, and each subsequent season has deepened the emotional vocabulary of its characters without betraying the show's fundamental simplicity. Season 4 arrived in June 2024 and delivered five episodes that leaned into the father-son dynamic with characteristic understatement.

What makes Gullak rare in the Indian OTT landscape is its economy. Episodes run 20 to 30 minutes. There are no musical interludes, no item numbers, no celebrity cameos. The narrator is a clay piggy bank — the gullak itself — voiced by Shivankit Singh Parihar, offering a sardonic running commentary on the family's life.

## The Cast Returns

Sunita Rajwar returns as Bittu ki Mummy, the neighbor whose presence is as reliable as the Mishras' morning newspaper. The core cast has remained unchanged across all five seasons, which is itself a statement in an industry where ensemble shows routinely swap actors between seasons.

Gullak Season 5 will stream exclusively on SonyLIV starting June 5. For the millions of Indians — at home and abroad — who've adopted the Mishras as their own fictional family, the date is already circled."""
    },
    {
        "headline": "Ramayana Is Eyeing San Diego Comic-Con for Its Trailer Launch. The Film May Release a Week Before Diwali.",
        "subheadline": "Nitesh Tiwari's ₹4,000-crore epic is planning a global rollout strategy that includes a SDCC debut, a Hans Zimmer-A.R. Rahman concert, and an October 30 release to grab the festive window early.",
        "slug": "ramayana-san-diego-comic-con-trailer-october-30-release-ranbir-kapoor-nri-20260530",
        "category": "entertainment",
        "vertical": "entertainment",
        "image_person": "Ranbir Kapoor",
        "image_pexels_query": None,
        "image_pexels_fallback": None,
        "sources": [
            {"name": "Sacnilk", "url": "https://sacnilk.com"},
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Mid-day", "url": "https://www.mid-day.com"},
            {"name": "Filmfare", "url": "https://www.filmfare.com"}
        ],
        "body": """The most ambitious Indian film ever made is building toward a global launch strategy that has no real precedent in Bollywood. Nitesh Tiwari's Ramayana — starring Ranbir Kapoor as Lord Ram, Sai Pallavi as Sita, and Yash as Ravana — is reportedly planning to debut its trailer at San Diego Comic-Con this July.

If the deal goes through, Ramayana would become the first Indian film to use SDCC as its primary launchpad, a move that signals how aggressively the makers are positioning this as a crossover event rather than a domestic release with international markets tacked on.

## The Comic-Con Play

According to industry reports, producer Namit Malhotra and director Nitesh Tiwari are in advanced talks with SDCC organizers. The decision follows a focus group screening held recently in Los Angeles, where an early cut reportedly received highly positive feedback from a diverse audience.

"The feedback has strengthened the belief that the film can travel across cultures," industry insiders told Mid-day, explaining why the team is pursuing a platform typically reserved for Marvel, DC, and major Hollywood franchises.

The strategy extends well beyond a trailer drop. The makers are also planning a large-scale musical event in October — a live concert featuring a historic collaboration between Academy Award winners Hans Zimmer and A.R. Rahman, who jointly composed the film's score. There are also whispers about international film festival screenings before the wide release.

## The October 30 Question

While Ramayana was originally slated for Diwali 2026, Bollywood Hungama reported that the makers are now considering preponing to October 30 — a week before the festivities begin. The logic: arriving early gives the film time to build word-of-mouth before the holiday surge, without any competing major release in that window.

Internal discussions are reportedly underway, with a final decision expected once distribution negotiations are locked. Those negotiations are themselves historic — the makers are reportedly pursuing a theatrical distribution deal worth ₹450 crore.

## The Numbers Behind the Ambition

Ramayana Part 1 has a reported production budget of ₹4,000 crore across both parts, making it the most expensive Indian film ever produced. The makers reportedly rejected a ₹700 crore OTT deal for both parts — the highest ever offered for an Indian film — because they believe Ramayana deserves more.

Ranbir Kapoor is playing a dual role: Lord Ram and Lord Parashuram. He has confirmed that Part 2 shooting is already 50 percent complete. The film also features Sunny Deol as Hanuman and Ravi Dubey as Lakshman, with visual effects handled by Oscar-winning studio DNEG.

## What This Means for Diaspora Audiences

For NRIs, the SDCC trailer launch and the aggressive global positioning mean Ramayana won't be an afterthought in international markets. If the makers follow through on their strategy, US, UK, and Canadian audiences could see the film on the same scale as a major Hollywood tentpole — wide release, premium formats, IMAX.

Part 1 is targeting late October or early November 2026. Part 2 is planned for Diwali 2027. The film that was once dismissed as too expensive, too risky, and too sacred to adapt may end up being the project that permanently changes how Indian cinema markets itself to the world."""
    },
    {
        "headline": "Mammootty and Mohanlal's Patriot Heads to ZEE5 on June 5. The ₹140-Crore Spy Thriller Couldn't Break Even in Theaters.",
        "subheadline": "The film grossed around ₹80 crore worldwide against a budget of ₹140 crore. Its OTT premiere gives it a second life — and NRIs a first chance to watch Malayalam cinema's most expensive bet.",
        "slug": "patriot-mammootty-mohanlal-zee5-ott-june-5-box-office-loss-nri-20260530",
        "category": "entertainment",
        "vertical": "entertainment",
        "image_person": "Mammootty",
        "image_pexels_query": None,
        "image_pexels_fallback": None,
        "sources": [
            {"name": "Sacnilk", "url": "https://sacnilk.com"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Patriot_(film)"},
            {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"}
        ],
        "body": """When Mammootty and Mohanlal agreed to star in the same film for the first time in nearly two decades, the expectation was simple: a landmark moment for Malayalam cinema that would translate into landmark box office numbers. Patriot was supposed to be that film. It wasn't — at least not commercially.

Directed by Mahesh Narayanan, the spy action thriller opened on May 1 with an impressive ₹28 crore worldwide on its first day. The opening weekend pushed past ₹60 crore globally. Then the weekday collapse began. By the end of its theatrical run, Patriot had grossed roughly ₹80 crore worldwide — ₹37 crore domestically and ₹43 crore from overseas — against a reported budget of ₹125 to ₹140 crore.

The film will now premiere on ZEE5 on June 5, 2026, in Malayalam, Tamil, Telugu, Kannada, and Hindi. For the NRI audiences who never got a chance to see it on the big screen — and for the many who heard the mixed word-of-mouth and decided to wait — this is the film's real second act.

## What Went Wrong at the Box Office

Patriot's commercial failure is not a story about a bad film. The critical response was mixed but acknowledged the film's technical brilliance and the sheer novelty of watching Mammootty and Mohanlal share the screen in a modern political thriller.

The problem was the gap between the budget and the audience the film could realistically reach. A ₹140 crore Malayalam-language production needs to perform like a pan-India blockbuster to break even, and Patriot — despite its Hindi and other language dubs — never generated the national conversation that films like Drishyam 3 (which just crossed ₹200 crore in eight days) or KGF managed.

The 180-minute runtime didn't help. Neither did the film's niche subject matter — a sophisticated espionage narrative involving a RAW agent gone underground, cyber-attacks targeting the Indian government, and a mole inside a Chief Minister's cabinet. It's the kind of story that plays well in reviews but faces headwinds at the ticket counter.

## The Cast Nobody Could Ignore

Whatever Patriot's commercial fate, the cast assembled for this film is staggering. Mohanlal plays Vikramadithyan, a seasoned RAW agent who has gone off the grid after a failed mission in Europe. Mammootty is Chief Minister Raghavan, whose own cabinet may be compromised.

The ensemble extends to Fahadh Faasil, Kunchacko Boban, Nayanthara, Revathi, Darshana Rajendran, and Rajiv Menon. The music is by Sushin Shyam. The cinematography is by Manush Nandan. On paper and on screen, this is a prestige production.

## The OTT Opportunity

For the Indian diaspora, ZEE5's June 5 premiere may be Patriot's real opening day. The overseas theatrical footprint for Malayalam films, while growing, is still limited compared to Hindi or Telugu releases. Many NRIs who wanted to watch the Mammootty-Mohanlal reunion simply didn't have access to a theater showing it.

ZEE5 will stream Patriot in five languages, giving it the pan-India reach that eluded its theatrical run. Whether the film finds its audience on the small screen — the way so many high-budget Indian films have been salvaged by OTT deals — will determine whether Patriot becomes a cautionary tale or a slow-burn success story.

The film streams on ZEE5 starting June 5, 2026."""
    },
    {
        "headline": "Ranbir Kapoor Says Playing Lord Ram Changed How He Approaches Fatherhood. 'I Really Needed That in My Life.'",
        "subheadline": "The actor, who initially refused the role, says becoming a father to Raha was what convinced him to take on the most ambitious part of his career.",
        "slug": "ranbir-kapoor-lord-ram-fatherhood-raha-ramayana-interview-nri-20260530",
        "category": "entertainment",
        "vertical": "entertainment",
        "image_person": "Ranbir Kapoor",
        "image_pexels_query": None,
        "image_pexels_fallback": None,
        "sources": [
            {"name": "News Ei Samay", "url": "https://www.newseisamay.com"},
            {"name": "Sacnilk", "url": "https://sacnilk.com"},
            {"name": "Filmfare", "url": "https://www.filmfare.com"}
        ],
        "body": """Ranbir Kapoor had turned down the role of Lord Ram. He's said so publicly, and the reason was honest: it felt like too massive a responsibility. Then his daughter Raha was born, and everything shifted.

In a recent interview with international media following the release of the Ramayana teaser, Kapoor opened up about how preparing for Nitesh Tiwari's epic adaptation has changed him — not just as an actor, but as a father and a person.

"I think I really needed that in my life," Kapoor said, speaking about the values he absorbed while studying Lord Ram's journey for the role.

## The Father Who Found the Character

The actor, who is married to Alia Bhatt, explained that becoming a parent fundamentally altered his perspective on the Ramayana. What once seemed like an overwhelming cultural responsibility began to feel like something personal and necessary.

"When I became a father, my perspective changed," Kapoor said. The values associated with Lord Ram's journey — duty, sacrifice, the tension between personal desire and larger responsibility — began to resonate with him in ways they hadn't before.

He shared that the lessons from the preparation "positively influenced his personal life and helped him become more grounded." Understanding Ram's approach to relationships, responsibilities, and family brought about meaningful changes in the way he approached parenthood.

It's a striking admission from an actor known for his brooding, complicated screen presence — the troubled heir in Rockstar, the calculating Don in Animal. Lord Ram requires something entirely different: stillness, moral clarity, a quiet authority that doesn't rely on menace or ambiguity.

## A Dual Role Nobody Expected

During the same interview, Kapoor confirmed something the teaser had hinted at: he's playing a dual role in the film. In addition to Lord Ram, he will portray Lord Parashuram — an avatar of Vishnu known for his fierce warrior nature. The contrast between the two characters represents a significant acting challenge, and the recently released teaser offered brief glimpses of both incarnations.

Kapoor also revealed that shooting for Ramayana Part 2 is already 50 percent complete — a timeline that suggests the production is running with remarkable efficiency given the film's ₹4,000-crore combined budget. Both parts together will run over six hours, making this the longest mainstream Indian film project in recent memory.

## What the Diaspora Will See

For Indian audiences abroad, Kapoor's personal transformation adds an emotional layer to a film that's already carrying enormous cultural weight. Ramayana isn't just a movie — for millions in the diaspora, it's an adaptation of a text that shaped their childhoods, their moral frameworks, their understanding of what it means to be Indian.

The fact that the lead actor struggled with the role, refused it, and ultimately accepted it because fatherhood gave him a new lens through which to understand Ram's story — that's the kind of narrative that transcends box office numbers.

Ramayana Part 1, directed by Nitesh Tiwari, also stars Sai Pallavi as Sita, Yash as Ravana, Sunny Deol as Hanuman, and Ravi Dubey as Lakshman. The film is produced by Namit Malhotra's Prime Focus Studios and backed by Monster Mind Creations. The music features a collaboration between Oscar winners A.R. Rahman and Hans Zimmer.

Part 1 is targeting a release around Diwali 2026. Part 2 is set for Diwali 2027."""
    }
]

# ── Main loop ──
published = 0
now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {art['headline'][:70]}...")

    # Image sourcing
    img_url = None

    # Try Wikipedia first for person articles
    if art.get("image_person"):
        img_url = fetch_wikipedia_person_image(art["image_person"])
        if img_url and not validate_image(img_url):
            print(f"  ⚠ Wikipedia image failed validation, trying alternate names")
            img_url = None

    # Fall back to Pexels
    if not img_url and art.get("image_pexels_query"):
        img_url = fetch_pexels_image(art["image_pexels_query"], art.get("image_pexels_fallback"))
        if img_url and not validate_image(img_url):
            print(f"  ⚠ Pexels image failed validation")
            img_url = None

    if not img_url:
        print(f"  ⚠ No valid image found — publishing without image (no image > wrong image)")

    # Check for banned image sources
    if img_url:
        banned_patterns = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat="]
        for bp in banned_patterns:
            if bp in img_url:
                print(f"  ✗ BANNED image source detected ({bp}), dropping image")
                img_url = None
                break

    # Build article row
    row = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"].strip(),
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now_utc,
        "sources": json.dumps(art["sources"]),
        "image_url": img_url,
    }

    result = sb_insert("p2_articles", row)
    if result:
        art_id = result.get("id")
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
        published += 1
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
