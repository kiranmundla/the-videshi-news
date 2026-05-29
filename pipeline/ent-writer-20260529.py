#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-29 batch."""

import json, os, re, sys, time, uuid, urllib.parse, subprocess
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

PEXELS_KEY = None
pexels_env = os.path.expanduser("~/.env.pexels") if os.path.exists(os.path.expanduser("~/.env.pexels")) else os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Helpers ──────────────────────────────────────────────────────────────────
import requests

def sb_insert(table, row):
    """Insert a row into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=row,
        timeout=30,
    )
    if r.status_code not in (200, 201):
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None
    data = r.json()
    return data[0] if isinstance(data, list) and data else data


def sb_patch(table, filters, patch):
    """Patch rows matching filters."""
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=patch,
        timeout=30,
    )
    if r.status_code not in (200, 204):
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")


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
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                [
                    "curl", "-sS",
                    f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3",
                    "-H", f"Authorization: {PEXELS_KEY}",
                ],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate that an image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't support HEAD, try GET
        if r.status_code != 200:
            r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            ct = r2.headers.get("Content-Type", "")
            cl = int(r2.headers.get("Content-Length", 0))
            r2.close()
            if r2.status_code == 200 and "image" in ct:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


BANNED_DOMAINS = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
BANNED_PARAMS = ["_nc_ht=", "_nc_cat=", "ccb="]


def is_banned_url(url):
    if not url:
        return True
    for d in BANNED_DOMAINS:
        if d in url:
            return True
    for p in BANNED_PARAMS:
        if p in url:
            return True
    return False


# ── Articles ─────────────────────────────────────────────────────────────────

articles = []

# ─── ARTICLE 1: Maa Behen ───────────────────────────────────────────────────
articles.append({
    "headline": "Madhuri Dixit Finds a Dead Body in Her Kitchen. Netflix's Maa Behen Drops June 4.",
    "subheadline": "Suresh Triveni's dark comedy pairs Madhuri with Triptii Dimri and digital creator Dharna Durga in a mother-daughters crime cover-up that Netflix is positioning as its next Darlings.",
    "slug": "madhuri-dixit-maa-behen-netflix-triptii-dimri-dark-comedy-june-4-nri-20260529",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Netflix India", "url": "https://www.netflix.com"},
        {"name": "Hollywood Reporter India", "url": "https://hollywoodreporterindia.com"},
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Maa_Behen"}
    ]),
    "image_url": None,
    "image_attribution": None,
    "person_image": "Madhuri Dixit",
    "pexels_query": "Bollywood actress dark comedy",
    "body": """Rekha has a dead body in her kitchen, two bickering daughters standing over it, and an entire conservative neighbourhood that already thinks the worst of her family. Her plan? Figure it out together — a family that has never agreed on anything, not even what to eat for dinner.

That is the opening gambit of *Maa Behen*, Suresh Triveni's new Netflix India film dropping on June 4. The dark comedy stars Madhuri Dixit as Rekha, Triptii Dimri as older daughter Jaya, and digital creator Dharna Durga — making her feature debut — as the younger, wilder Sushma. Ravi Kishan rounds out the ensemble in a role the makers are keeping deliberately vague.

## A Director With Nerve

Triveni, best known for *Tumhari Sulu* and *Jalsa*, has been quietly building a filmography around women pushed to the edge by circumstances they didn't choose. *Maa Behen* fits that pattern but pushes it further into crime and satire. The screenplay, by Pooja Tolani (who also crafted the story with Triveni), forces a mother and her two daughters into an improbable alliance: dispose of a corpse, maintain the family's already-precarious reputation, and do it all before the neighbours start asking questions.

The trailer, which dropped on May 22 and has already racked up millions of views, shows a family that communicates almost entirely through arguments and eye-rolls — until the crisis forces them into something resembling teamwork. It is being compared to *Darlings* (2022), Alia Bhatt's Netflix hit that blended domestic tension with dark comedy, but the tone here is more satirical and deliberately chaotic.

## Why It Matters for the Diaspora

For NRI audiences, *Maa Behen* lands on the most accessible platform there is. Netflix availability means no geo-restrictions, no hunting for regional OTT apps. Madhuri Dixit, who remains one of the most recognizable faces in Indian cinema worldwide, continues her pivot toward character-driven streaming content after *The Fame Game*. Triptii Dimri, meanwhile, has become Netflix India's most reliable face — *Bulbbul*, *Qala*, and now this.

## The Music Plays a Quiet Hand

The film's full album dropped this week, and it is not what you would expect from a comedy about a kitchen corpse. Akashdeep Sengupta composed the score, with tracks like *Kaari Kaari* (sung by Neelkamal Singh) and *Yeh Kaisi Raat* (Shreya Jain) suggesting a film that leans into its noir instincts. The biggest surprise is *Dhak Dhak Reloaded*, a reimagining of Madhuri's iconic *Beta* track by Akshay & IP — a wink at her legacy that the film appears to use as commentary rather than mere nostalgia.

## What to Expect

Produced by Vikram Malhotra's Abundantia Entertainment and Triveni's Opening Image Films, *Maa Behen* is built for the same audience that turned *Darlings* into a word-of-mouth sensation. It premieres globally on Netflix on June 4. The question for Madhuri Dixit fans in the diaspora is not whether to watch it — it is whether the film can do justice to a cast this stacked and a premise this deliciously absurd.

Dharna Durga, who built a massive following creating digital content, is the wildcard. If her debut lands, *Maa Behen* could become the film that proves social media stars can hold their own alongside Bollywood royalty. If it doesn't, well — there is still a dead body in the kitchen, and Madhuri Dixit is in charge of the cover-up. That alone is worth pressing play."""
})

# ─── ARTICLE 2: Made in India: A Titan Story ────────────────────────────────
articles.append({
    "headline": "Naseeruddin Shah Plays JRD Tata in a Six-Part Series About How Titan Was Built. It Streams Free on June 3.",
    "subheadline": "Made in India: A Titan Story pairs Naseeruddin Shah and Jim Sarbh to tell the origin of India's most iconic watch brand — a pre-liberalisation startup story about bureaucratic hurdles, impossible deadlines, and a Parsi industrialist who refused to fail.",
    "slug": "made-in-india-titan-story-naseeruddin-shah-jrd-tata-jim-sarbh-amazon-mx-player-nri-20260529",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Amazon MX Player", "url": "https://www.amazonmxplayer.in"},
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "MensXP", "url": "https://mensxp.com"},
        {"name": "Brownstone Worldwide", "url": "https://brownstoneworldwide.com"}
    ]),
    "image_url": None,
    "image_attribution": None,
    "person_image": "Naseeruddin Shah",
    "pexels_query": "Indian watch Titan wristwatch",
    "body": """Every Indian household has a Titan story. The first watch your father wore to work. The Sonata your uncle gave you for passing your board exams. The Titan Edge that felt impossibly thin on your wrist. What most people do not know is the story behind the brand — a pre-liberalisation gamble that almost did not happen, driven by a man who was supposed to save a failing printing press and instead built India's most successful consumer brand.

*Made in India: A Titan Story* tells that story. The six-part biographical drama premieres on Amazon MX Player on June 3, streaming for free. Naseeruddin Shah plays JRD Tata, the legendary chairman of the Tata Group, and Jim Sarbh plays Xerxes Desai, the founding managing director who turned JRD's quiet confidence into a watchmaking revolution.

## The Real Story Is Stranger Than Fiction

The series is adapted from Vinay Kamath's acclaimed book *Titan: Inside India's Most Successful Consumer Brand*, and it is set in an India that most NRIs over 40 will recognize viscerally. Pre-liberalisation India meant that starting a business was an exercise in navigating a bureaucracy designed to say no. Import licenses, government approvals, and a domestic market dominated by state-owned HMT watches — Xerxes Desai walked into all of it with an eight-month deadline and a boss who believed in him more than he believed in himself.

Jim Sarbh, speaking about the role, described Desai as "quietly rebellious — someone unafraid to challenge convention and imagine what didn't yet exist." Naseeruddin Shah called JRD Tata's leadership style "an extraordinary ability to spot potential and nurture it with trust, something that feels increasingly rare."

## Why NRIs Should Pay Attention

For the Indian diaspora, the Titan story hits differently. Many NRIs left India precisely because of the bureaucratic suffocation that Xerxes Desai fought against. The series does not romanticize pre-liberalisation India — it shows the frustration, the impossible odds, and the personal sacrifices required to build something world-class in a system stacked against ambition.

The series also features Vaibhav Tatwawadi, Namita Dubey, Lakshvir Saran, and Kaveri Seth. Karan Vyas wrote the script, with direction by Robbie Grewal. Almighty Motion Pictures and T-Series Films produced the project.

## The Comparisons Are Inevitable

Early reactions to the trailer draw comparisons to *Scam 1992* and *Rocket Boys* — both biographical dramas that found massive audiences by telling distinctly Indian stories with global production values. If *Made in India* can deliver that same combination of nostalgia, ambition, and emotional depth, it could become Amazon MX Player's biggest original series.

The platform has positioned the series as available across mobile, connected TVs, the Amazon shopping app, Prime Video, Fire TV, JioTV, and Airtel Xstream — making it one of the most widely accessible Indian originals at launch.

## What Makes This Different

Unlike most biographical content that leans on hagiography, the Titan story is inherently dramatic because it nearly failed. The company was built by someone who was not supposed to be building watches at all — Desai was tasked with reviving Tata Press, a struggling printing business. The pivot to watches was his own idea, and the series traces how one man's instinct, backed by one chairman's trust, created something that outlasted both of them.

For anyone who has ever worn a Titan, given one as a gift, or seen one on their parent's wrist — this is the origin story you never knew you wanted. It arrives June 3, free to stream."""
})

# ─── ARTICLE 3: Drishyam 3 crosses ₹200 crore ──────────────────────────────
articles.append({
    "headline": "Drishyam 3 Just Crossed ₹200 Crore Worldwide in Its First Week. The Hindi Version Arrives in October.",
    "subheadline": "Mohanlal's final chapter as Georgekutty is the fastest Malayalam film to ₹200 crore. Ajay Devgn's Hindi remake is already confirmed for October 2 — and the ending may be different.",
    "slug": "drishyam-3-200-crore-first-week-mohanlal-hindi-remake-ajay-devgn-october-nri-20260529",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Latestly / ANI", "url": "https://latestly.com"},
        {"name": "Pinkvilla", "url": "https://pinkvilla.com"},
        {"name": "Bombay Times", "url": "https://bombaytimes.com"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Drishyam_3"}
    ]),
    "image_url": None,
    "image_attribution": None,
    "person_image": "Mohanlal",
    "pexels_query": "Indian cinema thriller suspense",
    "body": """Georgekutty is back. And this time, the box office numbers suggest that the audience has been waiting with the same patience his character applies to covering his tracks.

*Drishyam 3*, the final chapter of Jeethu Joseph's iconic Malayalam thriller franchise, crossed ₹200 crore worldwide in its first week of release — making it the fastest Malayalam film to reach that milestone. Mohanlal, reprising his career-defining role as the resourceful everyman, thanked fans for turning his 66th birthday release into a box office event. The film opened on May 21 to packed theatres across India and the Middle East, and the momentum has not slowed.

## The Story Picks Up Where You Hoped It Wouldn't

Set roughly four-and-a-half years after the events of *Drishyam 2*, the third instalment finds Georgekutty living a life that looks suspiciously successful. He has become a film producer. The movie inspired by his own hidden past has become a hit. His family has a bigger house, more money, and by all appearances, a comfortable life. But Jeethu Joseph is not interested in comfort.

The film's central tension revolves around Georgekutty's attempt to arrange his elder daughter Anju's marriage — a process repeatedly sabotaged by lingering rumours connected to the Varun case. Meanwhile, Geetha Prabhakar and her husband (Asha Sharath and Siddique) are still seeking revenge, this time allied with former police officer Sahadevan (Kalabhavan Shajohn) and IG Thomas Bastin (Murali Gopy). Their plan is not to arrest Georgekutty — it is to psychologically destroy him by framing Anju.

## The Ending Changes Everything

Without spoilers, the ending of *Drishyam 3* takes the franchise in a direction that neither the original nor its sequel prepared audiences for. Early reports suggest the conclusion is more psychological than procedural — a shift that director Jeethu Joseph had hinted at in pre-release interviews. He described this instalment as moving away from legal complexities toward examining "the internal cracks within the George family as they buckle under the decade-long weight of their secret."

## What the Hindi Version Means for NRIs

Here is where it gets interesting for the diaspora. Ajay Devgn's Hindi remake of *Drishyam 3* is already confirmed with a theatrical release date of October 2, 2026. The Hindi versions have historically followed the Malayalam originals closely — but early reports suggest the Hindi *Drishyam 3* may alter the ending. That means NRIs who watch the Malayalam original now and the Hindi version in October could get two genuinely different conclusions to the same story.

The original Malayalam version features Shriya Saran, Ishita Dutta, and Mrunal Jadhav reprising their roles. Akshaye Khanna, who was initially attached, has exited the project — a casting change that has fuelled speculation about how the Hindi version will handle its antagonists.

## The Streaming Battle

Amazon Prime Video has already claimed post-theatrical streaming rights for the Malayalam version, filing a Delhi High Court petition to prevent the makers from negotiating with other platforms. The court granted interim relief restraining any third-party streaming deals. This legal tussle means the film's OTT premiere could be delayed or complicated — another reason to catch it in theatres if you can.

## The Numbers in Context

At ₹200 crore in week one, *Drishyam 3* has already surpassed the lifetime collections of many Hindi films released in 2026. The franchise, which started as a modest Malayalam thriller in 2013, has now been remade in Hindi, Tamil, Telugu, Kannada, and Chinese — making Georgekutty arguably the most widely adapted character in Indian cinema history. Pre-release distribution sales reportedly closed at ₹350 crore, suggesting the makers expect a total run well beyond that.

For the Indian diaspora, the message is clear: if you have been following Georgekutty's story, this is the ending — and it is not what you think. The Malayalam original is in theatres now. The Hindi version arrives October 2. The streaming rights are in court. And somewhere in a fictional Kerala town, Georgekutty is still three steps ahead of everyone."""
})

# ── Publish & image sourcing ─────────────────────────────────────────────────
published = 0
for art in articles:
    # Extract image fields
    person_name = art.pop("person_image", None)
    pexels_q = art.pop("pexels_query", None)

    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:70]}...")

    # Insert article first
    result = sb_insert("p2_articles", art)
    if not result:
        print("  ✗ Failed to insert article, skipping")
        continue

    art_id = result.get("id")
    print(f"  ✓ Article inserted: {art_id}")
    published += 1

    # Image sourcing
    img_url = None
    img_attr = None

    # 1. Try Wikipedia for person articles
    if person_name:
        print(f"  → Trying Wikipedia for '{person_name}'...")
        img_url = fetch_wikipedia_person_image(person_name)
        if img_url:
            img_attr = "Wikimedia Commons"

    # 2. Fallback to Pexels
    if not img_url and pexels_q:
        print(f"  → Trying Pexels for '{pexels_q}'...")
        img_url = fetch_pexels_image(pexels_q)
        if img_url:
            img_attr = "Pexels"

    # 3. Validate & apply
    if img_url and not is_banned_url(img_url):
        if validate_image_url(img_url):
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {
                "image_url": img_url,
                "image_attribution": img_attr,
            })
            print(f"  ✓ Image applied: {img_url[:80]}...")
        else:
            print(f"  ✗ Image validation failed, publishing without image")
    elif img_url:
        print(f"  ✗ Image URL is banned, publishing without image")
    else:
        print(f"  ⚠ No image found, article published without hero image")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} entertainment articles.")
