#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-01 run.

Articles:
1. KASHISH Pride Film Festival 2026 — 153 films from 43 countries, June 3-7 Mumbai
2. Maa Behen — Madhuri Dixit + Triptii Dimri Netflix crime-comedy, June 4
3. Main Vaapas Aaunga — Imtiaz Ali + Diljit Dosanjh Partition love story, June 12
"""

import json, os, subprocess, sys, time, uuid, urllib.parse, re
from datetime import datetime, timezone

# --- env ---
env_file = os.path.expanduser("~/.env.supabase")
with open(env_file) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if "PEXELS" in k.upper():
                    PEXELS_KEY = v.strip().strip('"').strip("'")

import requests

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                [
                    "curl", "-sS",
                    f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                    "-H", f"Authorization: {PEXELS_KEY}",
                ],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Verify image URL returns HTTP 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {r.status_code}, {ct}, {cl} bytes")
            return True
        # Try GET for servers that don't support HEAD well
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get("Content-Type", "")
        cl2 = int(r2.headers.get("Content-Length", 0))
        if r2.status_code == 200 and "image" in ct2 and cl2 > 5000:
            print(f"  ✓ Image validated (GET): {r2.status_code}, {ct2}, {cl2} bytes")
            return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def insert_article(article):
    """Insert article into Supabase p2_articles table."""
    article_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "id": article_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": article["sources"],
        "vertical": "entertainment",
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution", ""),
        "is_editorial": False,
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
    )
    if r.status_code in (200, 201):
        result = r.json()
        print(f"  ✓ Published: {article['headline'][:60]}... (id={article_id})")
        return article_id
    else:
        print(f"  ✗ Failed to publish: {r.status_code} {r.text[:200]}")
        return None


# ============================================================
# ARTICLE 1: KASHISH Pride Film Festival 2026
# ============================================================
print("\n=== Article 1: KASHISH Pride Film Festival 2026 ===")

# Image: Try to get a Pride/rainbow flag or festival image from Pexels
img1 = fetch_pexels_image("pride month rainbow celebration", "LGBTQ pride festival colorful")
if img1 and not validate_image(img1):
    img1 = None

article1 = {
    "headline": "KASHISH Opens in Mumbai This Week With 153 Queer Films From 43 Countries. Here's What It Means for the Diaspora.",
    "subheadline": "South Asia's biggest LGBTQ+ film festival runs June 3-7 at Liberty Cinema. For NRI audiences who grew up without seeing themselves on screen, this is the conversation India is finally having.",
    "slug": "kashish-pride-film-festival-2026-mumbai-153-films-43-countries-nri-diaspora-20260601",
    "sources": [
        {"name": "KASHISH Pride Film Festival Official", "url": "https://mumbaiqueerfest.com"},
        {"name": "NewsPoint", "url": "https://newspointapp.com"},
        {"name": "Passionate in Marketing", "url": "https://passionateinmarketing.com"},
        {"name": "Festivals from India", "url": "https://festivalsfromindia.com"},
    ],
    "image_url": img1,
    "image_attribution": "Pexels" if img1 else "",
    "body": """It is June 1, Pride Month has officially begun, and in Mumbai, a 17-year-old institution is preparing to do what it does better than anyone else on the subcontinent: fill a cinema hall with queer stories and dare you not to feel something.

The **KASHISH Pride Film Festival** returns for its 17th edition from **June 3 to 7**, spreading across three South Mumbai venues — the iconic **Liberty Cinema**, the **Alliance Française de Bombay**, and for the first time, the **National Gallery of Modern Art**. This year's programme is the largest yet: **153 films from 43 countries**, curated under the theme *Reflect, Resonate, Rejoice!*

## Why This Matters Beyond Mumbai

For queer South Asians in the diaspora — in the Bay Area, London, Toronto, Sydney — the relationship with Indian cinema has always been complicated. Bollywood's idea of a queer character, for decades, was a punchline. A limp wrist. A predator. The representation wasn't just absent; it was hostile.

KASHISH exists to rewrite that. Founded in 2010, it was the first LGBTQ+ film festival in India to be held in a mainstream theatre, and the first to receive approval from the Information & Broadcasting Ministry. It has since been voted one of the **Top 5 LGBTQ+ film festivals in the world** by Movie Maker magazine, and named one of the **Top 15 International Film Festivals Worth Travelling For** by Travel & Leisure.

"This year there are 153 films from 43 countries that will be showcased," said festival director **Saagar Gupta**. "Our theme 'Reflect, Resonate, Rejoice!' is an invitation to embrace the full emotional spectrum of queer life."

## The Programme

The opening night on June 3 features **Jimpa**, a 113-minute feature, following the opening ceremony at 7 PM. The five-day schedule is dense and deliberate — student shorts competitions, documentary showcases, Spanish short film programmes, panel discussions, and country-focus features.

Among the highlights:

- **Sabar Bonda**, directed by **Rohan Kanawade** — a tender romance between two men set during a 10-day mourning period in a village, which won acclaim at Sundance
- **Na Aavadti Goshta**, the debut feature from **Sai Deodhar**, which she described as a film "that families could watch together and have a conversation around the topic"
- **Queering India**, an Indian documentary centrepiece screening on Friday
- **LSD 2: Love, Sex and Betrayal 2**, a special presentation
- **A (Dis)Liked Story** and **Astronaut Lovers**, both screening on Friday night

The festival's advisory board includes figures like **Ashwiny Iyer Tiwari** and **Nikkhil Advani** as jury members, alongside board members **Arunaraje Patil**, **Dolly Thakore**, and **Meghna Ghai Puri** — names that signal the mainstream is no longer looking away.

## The Diaspora Connection

For NRI families, KASHISH represents something that wasn't available when most first-generation immigrants left India: an institutional, government-approved space for queer Indian stories. The festival has steadily become a reference point for queer South Asians abroad who want to see their experiences reflected in their own cultural language, not just through Western narratives.

As filmmaker Sai Deodhar put it: "Maharashtrians are a very progressive community, but there is no conversation on LGBTQ. So I wanted to create a film that families could watch together. Love is the purest emotion — how does gender matter?"

That sentence carries different weight when you hear it in a family WhatsApp group than when you read it in an American think piece about representation. It's the kind of shift that KASHISH has been engineering, one screening at a time, for nearly two decades.

## The Numbers

The festival draws an average footfall of **9,500 attendees** per year. Past guests have included **Ian McKellen**, **Nandita Das**, **Sonam Kapoor**, and filmmakers like **Shyam Benegal** and **Onir**. For the first time this year, KASHISH has launched a dedicated app for scheduling and access — a small detail that signals growth.

## What's Next

If you're in Mumbai between June 3 and 7, registrations are open with discounts for students, senior citizens, and transgender persons. If you're in the diaspora, the festival's digital footprint continues to expand, and several films from previous editions are available on streaming platforms.

The real story here isn't the film count or the venue additions. It's that in 2026, the largest queer film festival in South Asia can fill three venues across five days in the heart of Mumbai — and the government's response isn't a raid but an approval stamp. For a community that has spent decades watching itself be caricatured on screen, that's not just progress. It's a reckoning.""",
}

# ============================================================
# ARTICLE 2: Maa Behen — Madhuri + Triptii on Netflix
# ============================================================
print("\n=== Article 2: Maa Behen ===")

img2 = fetch_wikipedia_person_image("Madhuri Dixit")
if img2 and not validate_image(img2):
    img2 = None
if not img2:
    img2 = fetch_wikipedia_person_image("Triptii Dimri")
    if img2 and not validate_image(img2):
        img2 = None

article2 = {
    "headline": "Madhuri Dixit and Triptii Dimri Hide a Dead Body in Maa Behen. Netflix Drops It Wednesday.",
    "subheadline": "Suresh Triveni's crime-comedy pairs Bollywood's most beloved dancer with Gen Z's breakout star. For diaspora audiences who grew up on Madhuri, this is the Netflix homecoming you didn't know you needed.",
    "slug": "maa-behen-madhuri-dixit-triptii-dimri-netflix-june-4-crime-comedy-nri-20260601",
    "sources": [
        {"name": "Filmfare", "url": "https://filmfare.com"},
        {"name": "Zoom TV Entertainment", "url": "https://zoomtventertainment.com"},
        {"name": "Bollywood Life", "url": "https://bollywoodlife.com"},
        {"name": "IANS", "url": "https://ianslive.in"},
    ],
    "image_url": img2,
    "image_attribution": "Wikimedia Commons" if img2 else "",
    "body": """There's a dead body in the kitchen, the neighbours are nosy, and the only people who can fix this are a mother and her two daughters who can barely stand each other. That's the premise of **Maa Behen**, and if you think it sounds like a family gathering during Diwali gone sideways, you're not far off.

Directed by **Suresh Triveni** (*Tumhari Sulu*, *Jalsa*), the Netflix crime-comedy stars **Madhuri Dixit**, **Triptii Dimri**, and newcomer **Dharna Durga** as Rekha, Jaya, and Sushma — a dysfunctional mother-daughter trio in Bhopal who must hide a corpse while keeping their neighbourhood from finding out. It drops on **Netflix on June 4**.

## The Cast

Let's start with the obvious: **Madhuri Dixit** on Netflix. For an entire generation of NRI families, Madhuri wasn't just an actress — she was the reason the VCR existed. Hum Aapke Hain Koun, Dil To Pagal Hai, Devdas — her filmography is essentially the soundtrack of every Indian household in the 1990s. She lived in Denver for over a decade before returning to Mumbai, making her as much a diaspora figure as a Bollywood one.

Opposite her is **Triptii Dimri**, who in the last two years has become Gen Z's definitive Bollywood star. From *Animal* to *Bhool Bhulaiyaa 3*, she's demonstrated range that most of her contemporaries can't touch. Pairing her with Madhuri isn't just casting — it's a generational handshake.

**Dharna Durga** rounds out the trio as Sushma, the wild card sister. **Ravi Kishan**, **Geetanjali Kulkarni**, **Arunoday Singh**, and **Shardul Bhardwaj** fill out the supporting cast.

## The Premise

The film is set in **Bhopal's Adarsh Colony** — the kind of neighbourhood where everyone knows everyone else's business, and a dead body in your kitchen is everyone's problem. Rekha (Madhuri) is a mother already dealing with enough family drama when the ultimate curveball arrives. Jaya (Triptii) is the responsible daughter, Sushma (Dharna) is the chaos agent, and together they must think fast, lie faster, and somehow keep their world from unravelling.

During a promotional event in Gurugram, Madhuri was asked who among the three would cause the most *kaands* (chaos) in real life. "I think they will have more kaands because they are from here," she laughed. "She has less to do."

Triptii disagreed. "All three of us are equally *kaandi*. Whether it's the mother, whether it's the sister, or the older sister. It's a very dysfunctional family."

## Why It Matters for NRI Audiences

Suresh Triveni has built a reputation for wrapping social commentary inside commercial packaging. *Tumhari Sulu* turned a housewife's radio career into a meditation on ambition. *Jalsa* used a hit-and-run to examine class privilege. With *Maa Behen*, the framework is dark comedy — but the subtext is about the bonds that hold Indian families together even when everything is falling apart.

For diaspora viewers, that's a familiar frequency. The mother-daughter dynamic at the film's centre — the expectations, the resentment, the inability to say what you mean, the willingness to bury a body together when it counts — translates across time zones.

Madhuri herself addressed the shifting landscape of audience criticism in the age of social media: "There were people like that even then, but they didn't have a way to express. Today everyone is a filmmaker, everyone is a fashionista, and everyone is moral police."

## The Streaming Landscape

*Maa Behen* arrives in a stacked week for Indian OTT. Also dropping: **Dhurandhar: The Revenge** (Ranveer Singh, JioHotstar, June 4), **Gullak Season 5** (SonyLIV, June 5), **Brown** starring Karisma Kapoor (ZEE5, June 5), and **Made In India: A Titan Story** (Amazon Prime Video, June 3).

But the Madhuri-Triptii pairing gives *Maa Behen* a demographic range that none of the others can match. It's simultaneously an event for parents who remember *Ek Do Teen* and for the college-age cousin who discovered Triptii through Instagram reels.

Produced by **Abundantia Entertainment** in association with **Opening Image Films**, *Maa Behen* streams on Netflix starting **June 4**. Mark it.""",
}

# ============================================================
# ARTICLE 3: Main Vaapas Aaunga — Imtiaz Ali + Diljit
# ============================================================
print("\n=== Article 3: Main Vaapas Aaunga ===")

img3 = fetch_wikipedia_person_image("Diljit Dosanjh")
if img3 and not validate_image(img3):
    img3 = None
if not img3:
    img3 = fetch_wikipedia_person_image("Imtiaz Ali (director)")
    if img3 and not validate_image(img3):
        img3 = None

article3 = {
    "headline": "Diljit Dosanjh Showed the Main Vaapas Aaunga Trailer to a Packed Toronto Stadium. The Film Is About Partition. The Crowd Roared.",
    "subheadline": "Imtiaz Ali's Partition-era love story reunites the Chamkila director with Diljit, adds A.R. Rahman's score and Naseeruddin Shah. It opens June 12 — and advance bookings in North America are already live.",
    "slug": "main-vaapas-aaunga-diljit-dosanjh-imtiaz-ali-toronto-trailer-partition-nri-20260601",
    "sources": [
        {"name": "Filmfare", "url": "https://filmfare.com"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Main_Vaapas_Aaunga"},
        {"name": "Hauterfly", "url": "https://hauterrfly.com"},
        {"name": "The Daily Jagran", "url": "https://thedailyjagran.com"},
        {"name": "Zoom TV Entertainment", "url": "https://zoomtventertainment.com"},
    ],
    "image_url": img3,
    "image_attribution": "Wikimedia Commons" if img3 else "",
    "body": """There's a video circulating from Diljit Dosanjh's **AURA Tour** stop in Toronto. He's on stage, tens of thousands of fans packed into a stadium, and instead of dropping a track, he plays the trailer for **Main Vaapas Aaunga**. The screen lights up with images of Partition — separation, longing, a love story fractured by history — and the crowd, largely diaspora, erupts.

The moment crystallises something that's been building for months: this isn't just another Bollywood release. It's a film about leaving home, made by people who understand what that means, premiering its trailer to an audience that lives it.

## What We Know

**Main Vaapas Aaunga** (translation: *I Will Return*) is directed by **Imtiaz Ali** and stars **Diljit Dosanjh**, **Naseeruddin Shah**, **Vedang Raina**, and **Sharvari**. **Banita Sandhu** and **Danish Pandor** also appear. It's a Hindi-language period romantic drama set against the backdrop of **Partition**, structured across two timelines, exploring a love story that is interrupted by history and endures across decades.

The music is by **A.R. Rahman** with lyrics by **Irshad Kamil** — the same creative trio (Ali-Rahman-Kamil) that gave us *Rockstar*, *Highway*, and *Tamasha*. Two singles have already been released: "Kya Kamaal Hai" (sung by Diljit, dropped April 17) and "Maskara" (by Nilanjana Ghosh Dastidar and Vedang Raina, released May 5). "Maskara" has become a viral sensation on social media.

Principal photography ran from August to December 2025, with significant portions filmed in Punjab. It's produced by **Applause Entertainment**, **Birla Studios**, and **Window Seat Films**, with a worldwide release on **June 12, 2026**.

## The Diaspora Trailer Moment

The Toronto screening wasn't an accident. Diljit Dosanjh is, at this point, the single most important cultural bridge between Punjab and the global Punjabi diaspora. His AURA Tour is selling out stadiums across North America. He isn't promoting a film to a niche audience — he's premiering it to his core demographic, many of whom carry Partition stories in their family histories.

"From a story of belonging to a stadium full of emotions," one fan posted on social media after the Toronto reveal. "What a moment. What a beginning."

The makers have since announced that **advance bookings in North America** are open a full week before India — a recognition that diaspora demand is not secondary to domestic interest but is driving the conversation.

## Why This Film Hits Different

Partition films have been attempted before, with varying degrees of success. What sets Main Vaapas Aaunga apart is its creative pedigree and its timing.

**Imtiaz Ali** has spent his career making films about people searching for something they've lost — identity, love, a version of themselves they left behind. From *Jab We Met*'s Geet running away from an arranged marriage to *Tamasha*'s Ved trying to escape the life he built, Ali's protagonists are always, in some sense, displaced. A Partition love story is the most literal version of his recurring theme.

**Diljit Dosanjh** brings something no other lead could: authenticity. He's Punjabi, he's deeply rooted in the culture that Partition severed, and his collaboration with Ali on *Amar Singh Chamkila* (2024) proved they could handle heavy material with nuance.

**A.R. Rahman** scoring a Partition love story directed by Imtiaz Ali feels inevitable in the way the best creative pairings do. The "Maskara" single has already demonstrated that the soundtrack will be more than functional — it'll be the emotional spine of the film.

And then there's **Naseeruddin Shah**, whose presence in any cast signals that the material is serious. He's not doing rom-coms for the paycheck.

## The Box Office Setup

Main Vaapas Aaunga opens June 12 against **Kangana Ranaut's Bharat Bhagya Vidhata** (a 26/11 drama) and **Manoj Bajpayee's Governor** (a political thriller set during the 1990 economic crisis). It's a crowded corridor, but the film's positioning as a prestige romance with music-driven appeal gives it a lane.

After its theatrical run, the film will stream on **Netflix** — confirming a pattern from *Chamkila*, which went directly to the platform. This time, Ali and Diljit are doing theatres first, a bet that the material can sustain a big-screen experience.

The film topped **IMDb's Most Anticipated Indian Films and Shows of 2026** — a list that, for all its algorithmic quirks, reflects genuine search interest.

## What It Means

The title translates to "I Will Return." For a film about Partition, that's not just a romantic promise — it's a historical wound. Millions of families separated in 1947 carried that exact hope, and most never fulfilled it.

For the diaspora watching the trailer in a Toronto stadium, the title carries a third meaning: the promise every immigrant makes to the place they left. *Main vaapas aaunga.* I'll come back. The question the film seems to be asking is: what happens when you can't?

**Main Vaapas Aaunga** releases in theatres on **June 12, 2026**. Advance bookings are live in North America.""",
}

# ============================================================
# PUBLISH
# ============================================================
articles = [article1, article2, article3]
published = 0

for i, art in enumerate(articles, 1):
    print(f"\n--- Publishing Article {i} ---")
    aid = insert_article(art)
    if aid:
        published += 1
    time.sleep(1)

print(f"\n=== Done. Published {published}/{len(articles)} articles. ===")
