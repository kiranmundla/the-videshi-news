#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-20 00:30 UTC run (scheduled videshi-writer-news)
3 fresh articles distinct from all 2026-06-18/19 published news topics
(monsoon, $100K H-1B fee, India-US trade deal, IT-stock crash, Jio/NSE IPO,
GIFT City dollars, foreigner registration rules, India-Canada CEPA, RBI NRI
deposits, AAPI physician fee, Hormuz reopening, UAE consular operator, fuel
losses, PM-VBRY, OCI overhaul, Mumbai water, defence production, rupee,
remittances, Yoga Day, US student collapse, anti-Hindu hate, Anil Menon,
men's World Cup PIO players, DHS duration-of-status, VivaTech, Iran war,
UK-India clean energy, Warsh Fed, Modi Paris, EU-India FTA):

  1. Carnegie's 2026 survey — 40% of Indian Americans have thought about
     leaving the US; "reverse brain drain" turns from theory to data
  2. India's women crush Netherlands by 95 runs to open the T20 World Cup —
     a diaspora-soil tournament playing out across England
  3. New York moves to proclaim Aug 15 as India Independence Day — a marker
     of Indian-American civic arrival, state by state
"""

import json, os, subprocess, re, time, datetime, urllib.parse, requests


def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                key = key.strip().replace('export ', '')
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val


load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/.env.pexels'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=8):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers=UA, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                width = ii.get("width", 0)
                if url and "image" in mime and width > 300 and not url.lower().endswith(".svg"):
                    results.append({"url": url, "title": page.get("title", ""),
                                    "width": width, "height": ii.get("height", 0)})
            print(f"  \u2713 Wikimedia Commons: {len(results)} results for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        print("  \u26a0 No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        for photo in data.get("photos", []):
            url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if url:
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def validate_image(url):
    try:
        r = requests.get(url, timeout=15, stream=True, allow_redirects=True, headers=UA)
        ct = r.headers.get("Content-Type", "")
        chunk = r.raw.read(12000)
        if r.status_code == 200 and "image" in ct and len(chunk) > 5000:
            print(f"  \u2713 Image validated: {r.status_code}, {ct}, {len(chunk)}+ bytes")
            return True
        print(f"  \u2717 Image validation failed: {r.status_code}, {ct}, {len(chunk)} bytes")
    except Exception as e:
        print(f"  \u2717 Image validation error: {e}")
    return False


def pick_commons_image(query, keywords, caption):
    for img in fetch_wikimedia_commons_images(query, 8):
        tl = img["title"].lower()
        if any(kw in tl for kw in keywords) and validate_image(img["url"]):
            return img["url"], caption, "Wikimedia Commons"
    return None, "", ""


def insert_article(article):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=20)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  \u2713 Inserted: {result[0].get('slug', 'unknown')}")
            return True
        print("  \u2713 Inserted (no body returned)")
        return True
    print(f"  \u2717 Insert failed: {r.status_code} \u2014 {r.text[:300]}")
    return False


def wc(body):
    return len(re.sub(r'[#*>\n]', ' ', body).split())


def finalize(article, image_url, image_caption, image_attribution):
    if image_url:
        article["image_url"] = image_url
        article["image_caption"] = image_caption
        article["image_attribution"] = image_attribution
    else:
        print("  \u26a0 No valid image found \u2014 inserting without image")
    article["word_count"] = wc(article["body"])
    print(f"  word_count={article['word_count']}")
    return insert_article(article)


# ========================================================================
# ARTICLE 1: Reverse brain drain — Carnegie 2026 survey
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: Reverse brain drain / Carnegie survey")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Silicon Valley technology campus office Indian engineers",
        ["silicon", "valley", "campus", "office", "tech", "building"],
        "A technology campus in the United States; a new survey finds 40% of Indian Americans have thought about leaving")
    if not image_url:
        image_url, image_attribution = fetch_pexels_image("airport departure suitcase travel"), "Pexels"
        if image_url and validate_image(image_url):
            image_caption = "A traveller at a departure gate; nearly 40% of Indian Americans have considered leaving the US"
        else:
            image_url = None

    slug = "carnegie-survey-40-percent-indian-americans-thought-leaving-us-reverse-brain-drain-20260620"

    body = """For half a century, the Indian-American story has been told as a single ascending line: arrive with two suitcases, earn the degree, build the company, run the boardroom. A new survey suggests that line has begun to wobble \u2014 and that a striking share of the community is, at least privately, contemplating the exit.

The 2026 Indian American Attitudes Survey, conducted by the Carnegie Endowment for International Peace with the polling firm YouGov, found that nearly 40 percent of Indian Americans have at some point thought about leaving the United States and moving to another country. The figure breaks down into 14 percent who say they have thought about it frequently and 26 percent who have considered it occasionally. The survey drew on a nationally representative sample of 1,000 Indian-American adults polled between late November 2025 and early January 2026, with a margin of error of plus or minus 3.6 percentage points.

## What's Driving the Restlessness

The reasons cited are less about India's pull than about America's friction. Asked why they had thought about leaving, the largest group \u2014 about 58 percent \u2014 named frustration with US politics. Concern over the cost of living followed at 54 percent, and personal safety at 41 percent. The portrait the researchers paint is of a community in "turbulence": unsettled by political polarization, an immigration system that leaves even successful professionals in years-long limbo, and a creeping sense that the national story no longer fully includes them.

That anxiety is reshaping everyday behavior. Nearly a third of respondents (31 percent) said they avoid discussing or engaging with politics on social media for fear of discrimination. Roughly a fifth reported avoiding leaving and re-entering the country, refraining from displaying political signs, or declining to wear Indian dress in public. Eighteen percent said they steer clear of political rallies.

## Theory Becomes Data

The "reverse brain drain" has been predicted for years \u2014 usually by op-ed writers, occasionally by venture capitalists, rarely with hard numbers behind it. The Carnegie findings, paired with separate reports of Indian tech workers returning home as H-1B rules tighten and fees climb, have moved the conversation from speculation to statistics. One widely shared analysis on LinkedIn pointed to a roughly 40 percent rise in Indian tech professionals returning from the US to India, citing stricter visa rules, rising costs and booming opportunities in Bengaluru, Hyderabad and Pune.

The mechanism is a textbook case of push and pull forces converging. On the American side: visa uncertainty, the high cost of metros, and what researchers call "identity friction." On the Indian side: a fast-growing economy, a maturing startup ecosystem, and the simple gravity of family and familiarity. Migration, in this framing, has shifted from "settle permanently" to "optimize globally" \u2014 talent treating borders as options rather than destinies.

## A Note of Caution

The numbers deserve careful reading. Carnegie's own authors are explicit that discrimination is reshaping behavior but is not, so far, prompting a mass exodus. A clear majority of respondents \u2014 37 percent said they had never considered leaving, another 22 percent only rarely \u2014 are not in departure mode, and most still recommend the United States as a place to build a career. Skeptics add a practical point: H-1B holders who have spent fifteen years buying homes, enrolling children in schools and putting down roots do not uproot easily, and most are not chasing "better opportunities" so much as protecting the stable lives they have built. "Thinking about leaving" and booking a one-way ticket are very different acts.

## Why It Matters to the Diaspora

For the diaspora, the survey is less a forecast than a mirror. It puts data to a feeling many Indian Americans have described privately \u2014 that the welcome has grown more conditional, the paperwork more punishing, and the public mood more wary. For the roughly 5.2 million people of Indian origin in the United States, it raises uncomfortable questions about belonging that cut across generations, from the engineers who arrived in the 1990s to their American-born children.

It also lands as a strategic signal for both countries. If even a fraction of the most highly educated immigrant group in America begins to drift toward the exits, the US risks losing the very talent that has powered its innovation economy \u2014 while India, courting returnees with incentives and a swelling private sector, stands to gain. For families straddling both shores, the takeaway is more intimate still: the question of where home truly is has rarely felt so open.

**Sources:** Carnegie Endowment for International Peace, American Kahani, Business Standard, LinkedIn"""

    article = {
        "headline": "40% of Indian Americans Have Thought About Leaving the US. The 'Reverse Brain Drain' Just Got Its Numbers.",
        "subheadline": "A Carnegie Endowment survey of 1,000 Indian Americans finds a community in 'turbulence' \u2014 with frustration over politics, cost of living and safety driving even successful professionals to weigh the exit.",
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "For 5.2 million people of Indian origin in the US, a survey showing 40% have considered leaving puts hard data to a private unease about belonging \u2014 and signals a possible realignment of talent between the country that drew them and the India now courting them back.",
        "sources": ["Carnegie Endowment for International Peace", "American Kahani", "Business Standard", "LinkedIn"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: Women's T20 World Cup — India's dominant start
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: Women's T20 World Cup, India start")
    print("=" * 60)

    image_url = fetch_wikipedia_person_image("Smriti Mandhana")
    if image_url and validate_image(image_url):
        image_caption = "India opener Smriti Mandhana, whose batting anchors the side at the 2026 Women's T20 World Cup"
        image_attribution = "Wikimedia Commons"
    else:
        image_url = fetch_wikipedia_person_image("Harmanpreet Kaur")
        if image_url and validate_image(image_url):
            image_caption = "India captain Harmanpreet Kaur, leading the side at the 2026 Women's T20 World Cup in England"
            image_attribution = "Wikimedia Commons"
        else:
            image_url, image_caption, image_attribution = pick_commons_image(
                "women cricket India bat stadium",
                ["cricket", "women", "india", "bat"],
                "India in action at the 2026 Women's T20 World Cup")

    slug = "india-women-t20-world-cup-2026-england-mandhana-netherlands-diaspora-20260620"

    body = """India's women have opened their T20 World Cup campaign in England the way the favourites are supposed to \u2014 with a statement. Harmanpreet Kaur's side posted 209 for 5 against the Netherlands at Headingley in Leeds and then bowled the Dutch out for 114, a crushing 95-run win that announced India as one of the teams to beat in a tournament being played, conveniently, in the diaspora's own backyard.

The total was built on the familiar engine room at the top of the order. Smriti Mandhana and the explosive Shafali Verma gave India the platform, with Verma later describing the partnership in plain terms: "I feel like hitting 18 runs off six balls, but she's the one to keep me calm." Richa Ghosh and Jemimah Rodrigues supplied the acceleration, and the bowlers \u2014 led by Deepti Sharma's spin \u2014 made short work of a Netherlands chase that never threatened the required rate.

## A Tournament on Diaspora Soil

The 2026 ICC Women's T20 World Cup, running from June 12 to July 5, is being staged across England, putting it within reach of one of the largest concentrations of the Indian diaspora anywhere in the world. Grounds in Leeds, Birmingham, Manchester and London sit in cities where British-Indian communities have followed the women's game for years, and the tournament has the feel of a home fixture for the travelling support that has long turned England's Test summers blue.

For the women's team, the timing matters. India arrived in England fresh off a dominant run at home \u2014 the men beat Afghanistan by 170 runs in Lucknow and the women had been in ruthless touch \u2014 and carrying the weight of a near-miss in the last global final. A World Cup on English soil, with the diaspora packing the stands, is exactly the stage on which this group has said it wants to convert promise into silverware.

## The Engine and the Question Marks

If there is a worry threading through the celebration, it is fitness. Captain Harmanpreet Kaur was guarded on the status of all-rounder Shreyanka Patil, telling reporters the medical team would assess her before any clear update \u2014 a reminder that the margins in a four-week tournament are as much about the physio's room as the middle. India's depth, with Mandhana and Verma at the top and Sharma and Rodrigues through the middle, gives them cover that few sides can match, but a tournament is long and the schedule unforgiving.

The opening result also sharpens a broader story the women's game has been telling for several years. The success of the Women's Premier League back home, the rise of bankable stars like Mandhana, and the growing crowds for women's internationals have pushed the team from afterthought to genuine box office. A deep run in England would accelerate that shift, and the diaspora \u2014 buying the tickets, filling the stands, streaming the games at odd hours from California to Toronto \u2014 is a central part of the commercial story.

## What's Next

India move on through the group stage with the comfort of a healthy net run rate already banked, but the real tests lie ahead in the form of the traditional powers and a resurgent host nation. The path to the final, should they reach it, runs through some of the most storied grounds in the sport.

## Why It Matters to the Diaspora

For Indian families abroad, the women's World Cup is more than a sporting event \u2014 it is a shared ritual that crosses oceans and time zones. In Britain it is a rare home tournament: a chance for British-Indian fans to watch Mandhana and Kaur in person rather than at 5 a.m. on a phone screen. For the wider diaspora in the US, Canada, Australia and the Gulf, the team's rise offers role models for a generation of daughters now picking up bats in suburban leagues, and a reminder that the cricket that binds the diaspora is no longer only the men's game. A trophy in England would be celebrated from Southall to Sunnyvale.

**Sources:** Cricbuzz, CricToday, Sportradar, The Indian Eye"""

    article = {
        "headline": "India's Women Open Their World Cup With a 95-Run Demolition \u2014 and the Diaspora Has a Home Tournament in England",
        "subheadline": "Smriti Mandhana and Shafali Verma powered India to 209 against the Netherlands at Headingley before the bowlers sealed a crushing win, as the 2026 Women's T20 World Cup unfolds across British-Indian heartlands.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "sports",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "A Women's T20 World Cup staged across England puts India's rising women's side within reach of one of the world's largest Indian diasporas \u2014 a rare home tournament for British-Indian fans and a source of role models for diaspora daughters taking up the game from Southall to Sunnyvale.",
        "sources": ["Cricbuzz", "CricToday", "Sportradar", "The Indian Eye"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: New York's India Independence Day resolution
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: NY India Independence Day resolution")
    print("=" * 60)

    image_url = fetch_wikipedia_person_image("Kathy Hochul")
    if image_url and validate_image(image_url):
        image_caption = "New York Governor Kathy Hochul, whom the State Senate has urged to proclaim August 15 as India Independence Day"
        image_attribution = "Wikimedia Commons"
    else:
        image_url, image_caption, image_attribution = pick_commons_image(
            "New York State Capitol Albany building",
            ["capitol", "albany", "state", "new york"],
            "The New York State Capitol in Albany, where the Senate adopted a resolution honouring India's independence")

    slug = "new-york-senate-india-independence-day-resolution-august-15-indian-american-recognition-20260620"

    body = """A resolution moving through Albany is, on its face, a modest piece of ceremony: a request that the governor mark a date on a calendar. But for the Indian-American community in New York, the State Senate's call to proclaim August 15 as India Independence Day is being read as something larger \u2014 a marker of civic arrival, state by state, for a diaspora that has spent decades moving from the margins of American public life toward its centre.

The New York State Senate adopted the resolution, sponsored by Senator Jeremy Cooney, urging Governor Kathy Hochul to proclaim August 15, 2026 as India Independence Day across the state. Lawmakers framed it as part of the legislature's custom of recognising days important to the cultural heritage of New York's residents, invoking Mahatma Gandhi's legacy and the contributions of the Indian-American community.

## "Woven Into the Fabric"

The floor debate was, by the standards of state resolutions, unusually warm. Senators rose one after another to praise not just India's independence but the community that now calls New York home. "India's independence is enormously important to people around the world," the resolution noted, describing it as the end of "a 90-year struggle to achieve stronger civil, political, and economic rights along with self-determination."

Senator John Liu offered a civilisational frame, observing that India "has been a model of democracy for actually a lot longer than our country." Senator Jeremy Zellner put it in local terms, calling the Indian-American community "woven into the fabric of our everyday life" \u2014 "our neighbours raising families here, working in critical professions, and helping shape the character of our region." Senator Joseph Addabbo Jr. reached for Gandhi's words that the future depends on what one does in the present, saying the message continues to inspire Indian Americans and the generations following them.

## A Pattern, Not a One-Off

New York's gesture is part of a broader pattern of official recognition that has accelerated in recent years, as the Indian-American population \u2014 now the second-largest immigrant group in the United States and among its most economically successful \u2014 has translated demographic weight into political visibility. Independence Day flag-hoistings at city halls, Diwali celebrations in statehouses, and proclamations marking Indian cultural milestones have become routine fixtures of the civic calendar in states with significant diaspora communities.

What gives the New York move particular resonance is its timing and its tone. It arrives in a year when a Carnegie Endowment survey found a community feeling unusually unsettled \u2014 weighing questions of belonging amid political polarization and reports of rising discrimination. Against that backdrop, a chamber of elected officials standing to affirm that Indian Americans are "woven into the fabric" of the state reads as a deliberate counter-signal: recognition offered precisely when parts of the community have wondered whether the welcome was fraying.

## Symbol and Substance

Resolutions of this kind carry no force of law and allocate no money. A proclamation is, in the end, a statement of values rather than policy. But symbols matter to communities that have spent generations seeking acknowledgement, and the steady accumulation of them \u2014 a day named here, a heritage month declared there \u2014 maps the diaspora's growing political self-confidence and the willingness of mainstream politicians to court its support.

## Why It Matters to the Diaspora

For Indian Americans in New York and beyond, the resolution is a small but meaningful piece of belonging. August 15 is already marked privately in homes and at community flag-hoistings across the diaspora; having a state officially recognise it folds that private observance into the public American calendar, the way St. Patrick's Day or Lunar New Year long ago became civic events rather than community ones.

It also signals something to the next generation. For the American-born children of immigrants \u2014 the cohort most likely to feel caught between identities \u2014 seeing their heritage honoured in the chamber where their state's laws are made is a quiet form of validation. And for a community navigating a year of mixed signals about its place in America, the message from Albany was unambiguous: you are seen, and you belong.

**Sources:** Press Trust of India, Swadesi, Carnegie Endowment for International Peace, The Indian Eye"""

    article = {
        "headline": "New York Moves to Make August 15 India Independence Day. For the Diaspora, It's a Marker of Arrival.",
        "subheadline": "The State Senate has urged Governor Kathy Hochul to proclaim the date statewide, with lawmakers calling the Indian-American community 'woven into the fabric' of New York \u2014 a recognition that lands in a year of unease about belonging.",
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "A state officially recognising August 15 folds a private diaspora observance into America's public civic calendar \u2014 a marker of arrival for the second-largest US immigrant group, and a counter-signal of belonging in a year when surveys show parts of the community feeling unsettled.",
        "sources": ["Press Trust of India", "Swadesi", "Carnegie Endowment for International Peace", "The Indian Eye"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"VIDESHI NEWS WRITER \u2014 {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = []
    results.append(("Reverse brain drain / Carnegie survey", write_article_1()))
    results.append(("Women's T20 World Cup India start", write_article_2()))
    results.append(("NY India Independence Day resolution", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
