#!/usr/bin/env python3
"""Entertainment writer — 2026-05-29 batch"""

import json, os, re, sys, time, uuid, urllib.parse
import requests
from datetime import datetime, timezone

# ── Load .env.supabase ───────────────────────────────────────────────
def load_env(path):
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass

load_env("~/.env.supabase")
load_env("~/.env.pexels")

# ── Supabase config ──────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
PEXELS_KEY = None
try:
    with open(os.path.expanduser("~/.env.pexels")) as f:
        for line in f:
            if line.startswith("PEXELS_API_KEY="):
                PEXELS_KEY = line.strip().split("=", 1)[1].strip('"').strip("'")
except Exception:
    pass

# ── Image helpers ────────────────────────────────────────────────────
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
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Check image URL is valid (HTTP 200, image/*, >5KB)."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {ct}, {cl} bytes")
            return True
        # Try GET if HEAD didn't provide content-length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {ct}, >{len(chunk)} bytes")
                return True
        print(f"  ✗ Image failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def sb_insert(table, data):
    """Insert a row into Supabase and return the response data."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        return result[0] if isinstance(result, list) and result else result
    print(f"  ✗ Insert into {table} failed: {r.status_code} — {r.text[:300]}")
    return None


def sb_patch(table, match, data):
    """Patch a row in Supabase."""
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=data,
        timeout=30,
    )
    if r.status_code in (200, 204):
        print(f"  ✓ Patched {table} where {match}")
        return True
    print(f"  ✗ Patch {table} failed: {r.status_code} — {r.text[:300]}")
    return False


# ── Articles ─────────────────────────────────────────────────────────
now_iso = datetime.now(timezone.utc).isoformat()

articles = [
    # ── Article 1: Akshay Kumar's Samuk ──
    {
        "headline": "Akshay Kumar Is Making India's First Alien Survival Thriller. The Predator's Creature Designer Is Building the Monster.",
        "subheadline": "Samuk brings together Hollywood's top practical-effects talent with Bollywood's biggest action star for a 2027 sci-fi spectacle that could redefine the genre in Indian cinema.",
        "slug": "akshay-kumar-samuk-alien-thriller-alec-gillis-predator-hollywood-nri-20260529",
        "category": "entertainment",
        "status": "published",
        "published_at": now_iso,
        "person": "Akshay Kumar",
        "sources_json": json.dumps([
            {"name": "Variety India", "url": "https://variety.com"},
            {"name": "Sacnilk", "url": "https://sacnilk.com"},
            {"name": "Filmy Khabri", "url": "https://filmykhabri.com"},
            {"name": "Asian Reels", "url": "https://asianreels.com"}
        ]),
        "body": """Bollywood has flirted with science fiction before — from *Koi… Mil Gaya*'s friendly alien to *Brahmastra*'s mythological VFX — but never quite attempted what Akshay Kumar and producer Vipul Amrutlal Shah are planning with **Samuk**. The film, announced this week through a wide-ranging Variety India interview, is being positioned as India's first large-scale alien survival thriller, and it's bringing Hollywood's most decorated creature designers along for the ride.

## The Predator's Guy Is Building the Monster

The headline hire is **Alec Gillis**, the Academy Award-nominated creature effects designer whose resume includes the *Alien*, *Predator*, and *Tremors* franchises. Gillis will design and physically construct the extraterrestrial creature for *Samuk* — and the emphasis on "physically" is deliberate. The filmmakers have committed to practical creature effects over CGI, an approach that's rare even in Hollywood blockbusters these days and virtually unheard of in Indian cinema.

Joining the production is **Luke Tumber**, the British stunt coordinator whose credits span *Mission: Impossible — The Final Reckoning*, the *Venom* films, *Star Wars*, *No Time To Die*, and Marvel's *Vision Quest*. Tumber will oversee the action choreography, blending military realism with high-intensity survival sequences.

## Why This Matters for Indian Cinema

Indian filmmakers have historically outsourced VFX to post-production studios, often with mixed results. *Samuk*'s decision to invest in on-set practical effects represents a philosophical shift — the creature will physically exist on set, interacting with actors in real time, making the horror and suspense feel grounded rather than synthetic.

Director **Kanishk Varma**, who reportedly spent over two years developing the film's concept and visual world, drew inspiration from iconic alien survival films but wanted *Samuk* to have its own identity rooted in Indian storytelling sensibilities. The producers describe it as blending survival horror, intense action, and extraterrestrial suspense in a "grounded yet cinematic manner."

## The Akshay-Vipul Reunion

The project marks a reunion between Akshay Kumar and Vipul Shah, a partnership that has delivered multiple commercial entertainers over the years. But *Samuk* is a departure from their comedy-action formula. Speaking to Variety India, Akshay called it "never-seen-before cinema" — a description he doesn't deploy lightly, given his prolific output of 3-4 films annually.

## The Diaspora Angle

For NRIs who grew up watching Bollywood but switched to Hollywood for their sci-fi fix, *Samuk* represents a tantalizing proposition: a big-budget Indian film that doesn't just compete with Hollywood on spectacle but actively imports Hollywood's best technical minds to achieve it. If the practical creature effects land, this could open an entirely new genre lane for Indian cinema.

**Samuk** begins shooting in August 2026 for a grand theatrical release in 2027. Co-produced by Aashin A Shah, it's being planned as a pan-Indian theatrical event.""",
    },
    # ── Article 2: Anupam Kher ──
    {
        "headline": "Anupam Kher Just Started Filming His 552nd Movie. He Has Two More Lined Up. At 71, He's Never Been Busier.",
        "subheadline": "Between Shri Ram Bhoomi, Khosla Ka Ghosla 2, and a mystery project with Sooraj Barjatya, the veteran actor's 2026 is shaping up to be the most prolific year of a 42-year career.",
        "slug": "anupam-kher-552-films-shri-ram-bhoomi-khosla-ka-ghosla-2-barjatya-nri-20260529",
        "category": "entertainment",
        "status": "published",
        "published_at": now_iso,
        "person": "Anupam Kher",
        "sources_json": json.dumps([
            {"name": "IANS", "url": "https://ianslive.in"},
            {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
            {"name": "Blaze Trends", "url": "https://blazetrends.com"},
            {"name": "CineTalkers", "url": "https://cinetalkers.com"}
        ]),
        "body": """Most actors slow down in their seventies. Anupam Kher appears to be speeding up.

On Thursday, the 71-year-old began filming **Shri Ram Bhoomi** — his 552nd film — in a *mahurat* ceremony attended by co-stars Ritwik Bhowmik and Amruta Khanvilkar. The project, directed by National Award-winning filmmaker **Kamakhaya Narayan Singh** (who just completed *The Kerala Story 2*), is backed by Zee Studios, Dancing Shiva Films, and Cinekorn Entertainment. And it's just one of three major projects on Kher's 2026 slate.

## Shri Ram Bhoomi: Faith, Sacrifice, and Ayodhya

The makers are keeping specific plot details tightly under wraps, but the title alone has set social media buzzing. Kher described the script as "a story rooted in truth, faith, and the concept of returning home" — language that strongly suggests an Ayodhya-centric narrative exploring one of the most consequential chapters in modern Indian history.

The timing isn't accidental. Indian cinema is experiencing a wave of culturally rooted storytelling, with Nitesh Tiwari's ₹4,000-crore *Ramayana* adaptation generating massive anticipation. Zee Studios appears to be positioning *Shri Ram Bhoomi* to ride that cultural momentum, pairing a veteran actor with deep emotional credibility with a director known for handling politically charged material.

Ritwik Bhowmik, who rose to prominence through the OTT series *Bandish Bandits*, represents the cross-generational appeal the project is targeting — heritage audiences through Kher, younger digital-native viewers through Bhowmik.

## Khosla Ka Ghosla 2: The Sequel Every NRI Has Been Waiting For

If there's one Bollywood film that resonated universally with the Indian middle class — and particularly with NRIs who watched their parents navigate property disputes from 10,000 miles away — it's *Khosla Ka Ghosla*. The 2006 cult classic about a retired Delhi man fighting to reclaim his land from a smooth-talking builder became a touchstone for anyone who's ever dealt with Indian real estate.

The sequel, releasing **August 28, 2026** (Raksha Bandhan weekend), brings back Kher as Kamal Kishore Khosla alongside **Boman Irani**, **Parvin Dabas**, **Ranvir Shorey**, **Kiran Juneja**, and **Tara Sharma**. New addition **Ravi Kishan** joins the ensemble. The film is directed by **Umesh Bisht** (*Pagglait*, *Gyaarah Gyaarah*), taking over from original director Dibakar Banerjee.

Kher wrapped 90% of his work on the sequel earlier this year, calling it "an EPIC sequel to an OG cult classic" and promising that "this time the con is bigger than the biggest."

## The Sooraj Barjatya Mystery

As if two major productions weren't enough, Kher has also confirmed an untitled project with **Sooraj Barjatya** — the filmmaker behind *Maine Pyar Kiya*, *Hum Aapke Hain Koun*, and *Hum Saath-Saath Hain*. The pair share a 42-year history: Barjatya was the fifth assistant director on Kher's debut film *Saaransh* (1984). Every detail about this collaboration is under wraps, but a Kher-Barjatya reunion after four decades carries significant emotional weight for audiences who grew up on Rajshri Productions' family dramas.

## 552 Films and Counting

The sheer number is staggering. Kher has now appeared in more films than almost any other working actor in world cinema. That he's delivering this volume while maintaining quality — *The Kashmir Files* and *Uunchai* both landed in the last few years — makes his late-career productivity all the more remarkable.

For the diaspora, Kher has always occupied a unique position: equally at home in a Marvel series (*New Amsterdam*), a Robert De Niro film (*Silver Linings Playbook*), or a Dharma family drama. His 2026 slate, spanning a spiritual epic, a beloved comedy franchise, and a Barjatya reunion, is essentially a cross-section of everything Indian cinema does best.""",
    },
    # ── Article 3: Jio ₹200 OTT Pass ──
    {
        "headline": "Jio Just Bundled 15 Streaming Platforms Into One ₹200 Pass. Here's What That Means for How India Watches Content.",
        "subheadline": "YouTube Premium, JioHotstar, Prime Video, and 12 more OTT apps — all for roughly $2.40 a month. India's streaming wars just entered a new phase.",
        "slug": "jio-200-ott-pass-15-platforms-youtube-premium-streaming-india-nri-20260529",
        "category": "entertainment",
        "status": "published",
        "published_at": now_iso,
        "person": None,
        "sources_json": json.dumps([
            {"name": "Gadgets 360", "url": "https://gadgets360.com"},
            {"name": "LatestLY", "url": "https://latestly.com"},
            {"name": "Digit.in", "url": "https://digit.in"},
            {"name": "Gizbot", "url": "https://gizbot.com"}
        ]),
        "body": """Reliance Jio launched a new ₹200 OTT Pass on May 27 that bundles access to 15 premium streaming platforms, over 1,000 live TV channels, 30 GB of high-speed data, and unlimited 5G connectivity into a single 28-day pack. The company claims the bundled services are worth approximately ₹1,500 per month.

For ₹200 — roughly $2.40 — Indian consumers now get what most Americans pay $50+ to assemble across separate subscriptions. That price gap tells you everything about where India's streaming wars are headed.

## What's in the Box

The headline inclusions are **YouTube Premium** (ad-free viewing, background play, offline downloads), **JioHotstar Mobile + Hollywood** (live sports, Hotstar Originals, Hollywood content), and **Prime Video Mobile Edition**. Beyond the big three, the pack adds 12 more platforms accessible through the JioTV app: **SonyLiv**, **ZEE5**, **Lionsgate Play**, **Discovery+**, **Sun NXT**, **FanCode**, **Kanccha Lannka**, **Planet Marathi**, **Chaupal**, **Hoichoi**, **TimesPlay**, and **Tarang Plus**.

On the live TV side, JioTV provides access to over 1,000 channels including 150+ paid channels from broadcasters like JioStar (Star Plus HD, Colors HD), Sony Entertainment (SET HD, Sony SAB HD), Sun TV Network (Sun TV HD, KTV HD), Warner Bros. Discovery (Discovery Channel, Animal Planet), and ETV regional channels.

## The YouTube Premium Play

The real headline isn't the OTT platforms — most Indian users with any streaming subscription already have access to some combination of these. It's **YouTube Premium**. For a generation of Indian consumers — particularly the under-30 demographic — YouTube is the primary entertainment platform. They watch more YouTube than Netflix, Prime, and Hotstar combined.

By making YouTube Premium the anchor of a ₹200 bundle, Jio is effectively saying: we'll give you the platform you actually use every day, and throw in everything else as a bonus. The psychology is inverted from how American bundling works, where the premium service (say, Max or Disney+) leads and lesser-known platforms ride along.

## What This Means for NRIs

If you're in the diaspora and your parents, siblings, or extended family back home are on Jio — which, given Jio's 470+ million subscribers, they probably are — this changes how your family consumes content. For the cost of a single Starbucks latte, your parents now have ad-free YouTube, live cricket on Hotstar, Bollywood on Prime, regional content across a dozen platforms, and 30 GB of data to watch it all.

The practical impact: fewer "can you share your Netflix password?" conversations during family WhatsApp calls. The strategic impact: Jio is training an entire generation of Indian consumers to expect everything for almost nothing, which makes life extremely difficult for standalone streaming platforms trying to charge ₹499 or ₹999 per month.

## The Bundling Endgame

India's streaming market has been moving toward this consolidation for years. JioHotstar's merger, Amazon's mobile-first pricing, and now this 15-in-1 bundle all point toward the same conclusion: in a price-sensitive market of 1.4 billion people, the winner isn't the platform with the best content library — it's the one that can bundle the most value at a price point that feels like rounding error.

At ₹200 for 15 platforms, Jio isn't just competing with other telecom providers. It's making the case that streaming, like mobile data before it, should be essentially free — just a value-add that keeps you loyal to the Jio ecosystem.

The ₹200 Jio OTT Pass is available now across MyJio, Jio.com, retail stores, and third-party recharge apps for all Jio users with an active base plan.""",
    },
]

# ── Publish each article ─────────────────────────────────────────────
published_count = 0
for art in articles:
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:70]}...")

    # Source image
    img_url = None
    img_attribution = None
    person = art.pop("person", None)

    if person:
        print(f"  Sourcing Wikipedia image for '{person}'...")
        img_url = fetch_wikipedia_person_image(person)
        if img_url:
            img_attribution = "Wikimedia Commons"

    if not img_url and not person:
        # For non-person articles, try Pexels with specific terms
        if "jio" in art["slug"] or "streaming" in art["slug"]:
            print("  Sourcing Pexels image for streaming/OTT...")
            img_url = fetch_pexels_image("smartphone streaming video app", "mobile entertainment India")
            if img_url:
                img_attribution = "Pexels"

    if not img_url and person:
        # Fallback to Pexels for person articles with specific terms
        print(f"  Wikipedia failed, trying Pexels for '{person}'...")
        if "akshay" in person.lower():
            img_url = fetch_pexels_image("Bollywood sci-fi film set", "movie production set")
        elif "anupam" in person.lower():
            img_url = fetch_pexels_image("Bollywood veteran actor filming", "Indian cinema production")
        if img_url:
            img_attribution = "Pexels"

    # Validate image
    if img_url:
        if not validate_image(img_url):
            print("  ✗ Image validation failed, proceeding without image")
            img_url = None
            img_attribution = None

    # Build insert payload
    sources = art.pop("sources_json")
    body_text = art["body"]
    word_count = len(body_text.split())
    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "vertical": art["category"],
        "status": art["status"],
        "published_at": art["published_at"],
        "body": body_text,
        "sources": sources,
        "image_url": img_url,
        "image_attribution": img_attribution,
        "urgency": "medium",
        "tags": [],
        "is_featured": False,
        "score_total": 55,
        "word_count": word_count,
    }

    result = sb_insert("p2_articles", payload)
    if result:
        art_id = result.get("id")
        print(f"  ✓ Published! ID: {art_id}")
        published_count += 1
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {published_count}/{len(articles)} articles.")
