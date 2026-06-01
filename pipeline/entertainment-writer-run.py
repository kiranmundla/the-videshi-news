#!/usr/bin/env python3
"""Entertainment writer — June 1, 2026 15:00 UTC run"""

import json, os, sys, time, uuid, re, urllib.parse
from datetime import datetime, timezone

import requests

# --- env ---
ENV_FILE = os.path.expanduser("~/.env.supabase")
PEXELS_ENV = os.path.expanduser("~/workspace/.env.pexels")

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.replace("export ", "").strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(ENV_FILE)
load_env(PEXELS_ENV)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# --- helpers ---

def sb_insert(table, payload):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=payload, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ✗ INSERT {table} failed ({r.status_code}): {r.text[:300]}")
        return None
    data = r.json()
    return data[0] if isinstance(data, list) and data else data

def sb_patch(table, match, payload):
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=payload, timeout=30)
    if r.status_code not in (200, 204):
        print(f"  ✗ PATCH {table} failed ({r.status_code}): {r.text[:300]}")
    return r

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
    """Fetch an image from Pexels API using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            cmd = [
                "curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
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


def upload_to_supabase_storage(image_url, filename, bucket="article-images"):
    """Download image and upload to Supabase storage. Returns public URL or None."""
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200:
            print(f"  ✗ Download failed ({r.status_code}): {image_url[:80]}")
            return None
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type:
            print(f"  ✗ Not an image ({content_type}): {image_url[:80]}")
            return None
        if len(r.content) < 5000:
            print(f"  ✗ Image too small ({len(r.content)} bytes): {image_url[:80]}")
            return None

        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        upload_url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
        up = requests.post(upload_url, headers=upload_headers, data=r.content, timeout=30)
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed ({up.status_code}): {up.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def validate_image_url(url):
    """Validate image URL returns 200 with image content-type and decent size."""
    if not url:
        return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't support HEAD, try GET with range
        if r.status_code in (200, 405, 403):
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)", "Range": "bytes=0-1000"}, timeout=10)
            if r2.status_code in (200, 206):
                return True
    except:
        pass
    return False


# --- Articles ---

ARTICLES = []

# ============================================================
# Article 1: Zee Entertainment bags FIFA World Cup 2026 rights
# ============================================================
ARTICLES.append({
    "headline": "Zee Just Grabbed the FIFA World Cup. Indian Fans Had 10 Days to Spare.",
    "subheadline": "After months of standoff and a slashed asking price, Zee Entertainment secured broadcast and streaming rights for the 2026 World Cup and 38 other FIFA events through 2034. NRI fans across the US, Canada, and Mexico can breathe.",
    "slug": "zee-entertainment-fifa-world-cup-2026-broadcast-india-nri-20260601",
    "category": "entertainment",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Inc42", "url": "https://inc42.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
        {"name": "afaqs!", "url": "https://www.afaqs.com"}
    ]),
    "image_search_person": None,
    "image_search_pexels": "FIFA World Cup football stadium",
    "image_search_pexels_fallback": "football soccer world cup fans",
    "body": """The months-long stalemate is over. Zee Entertainment announced on Monday that it has secured the broadcast and digital streaming rights for the 2026 FIFA World Cup, along with 38 other FIFA events spanning eight years through 2034. The deal includes the 2030 World Cup and the 2027 FIFA Women's World Cup — and it was closed with just 10 days to spare before the tournament kicks off on June 11.

## A Standoff That Went Down to the Wire

FIFA had initially sought roughly $100 million from the Indian market for a package covering the 2026 and 2030 World Cups. When that price tag found no takers, it was slashed to $60 million, according to Reuters. India's dominant sports broadcaster JioStar — the Reliance-Disney joint venture that aired the 2022 World Cup through its predecessor Viacom18 — offered about $20 million and was turned away. Sony, which held rights for the 2014 and 2018 tournaments, discussed terms but never formally bid.

The final deal landed somewhere between $25 million and $80 million, per The Hindu BusinessLine, though exact financial terms remain undisclosed. For context, this was one of the last major global markets without a confirmed broadcaster for the biggest sporting event on the planet.

## Where NRI Fans Will Watch

Zee will broadcast the World Cup through its newly launched Unite8 Sports network — a four-channel lineup comprising Unite8 Sports 1, Unite8 Sports 1 HD, Unite8 Sports 2, and Unite8 Sports 2 HD. Streaming will be available on ZEE5 with multilingual viewing options.

For the Indian diaspora in the US, Canada, and Mexico — the three host countries for this year's tournament — the timing couldn't be more relevant. Many NRI football fans had been scrambling for clarity on how to watch the tournament from India-facing platforms, especially those who prefer Hindi or regional-language commentary alongside the action.

## More Than Just One Summer

The deal isn't a one-off. Beyond the 2026 and 2030 men's World Cups, Zee's package includes FIFA Men's and Women's U-17 World Cups (2026-2034), U-20 World Cups for both genders, FIFA Futsal World Cups, the FIFA Intercontinental Cup (2026-2030), and exclusive docu-series content tied to these tournaments.

"Football cuts across regions and demographics," said Zee CEO Punit Goenka. "Our partnership with FIFA will enable us to unlock the true value of the sport."

## What This Means for the Indian Media Landscape

Zee's move marks a strategic pivot. The company has been rebuilding after the collapsed merger with Sony, and securing a prestige global sporting property signals ambition. The Unite8 Sports brand is entirely new — a dedicated sports vertical that didn't exist until this deal was announced.

For JioStar, the dominant force in Indian sports broadcasting with IPL, Olympics, and cricket rights, this is a rare miss. It also reshapes the competitive dynamics: Zee now has a year-round football content pipeline that could pull younger, urban, sports-hungry viewers toward its ecosystem.

For the millions of Indian football fans — and the growing diaspora community that follows the sport passionately — the uncertainty is finally over. The World Cup will be on Indian screens. And this time, Zee is the one holding the remote."""
})


# ============================================================
# Article 2: Maa Behen — Netflix June 4
# ============================================================
ARTICLES.append({
    "headline": "Madhuri Dixit Hides a Dead Body in Her Kitchen in Maa Behen. Netflix Drops It Wednesday.",
    "subheadline": "Suresh Triveni's crime-comedy pairs Madhuri with Gen-Z star Triptii Dimri as a dysfunctional mother-daughter trio navigating chaos, nosy neighbours, and a very inconvenient corpse. It streams globally on June 4.",
    "slug": "maa-behen-madhuri-dixit-triptii-dimri-netflix-june-4-nri-20260601",
    "category": "entertainment",
    "sources": json.dumps([
        {"name": "Filmfare", "url": "https://www.filmfare.com"},
        {"name": "Bollywood Life", "url": "https://www.bollywoodlife.com"},
        {"name": "IANS", "url": "https://ianslive.in"},
        {"name": "Bollywood Bubble", "url": "https://www.bollywoodbubble.com"}
    ]),
    "image_search_person": "Madhuri Dixit",
    "image_search_pexels": None,
    "image_search_pexels_fallback": None,
    "body": """There's a dead body in the kitchen, nosy neighbours circling, and a mother-daughter trio that can barely agree on what to have for dinner. That's the setup for Maa Behen, the Netflix crime-comedy dropping globally on June 4, and it might be the most unexpectedly fun Hindi film to land on OTT this month.

## The Setup

Directed by Suresh Triveni — who earned critical praise for Tumhari Sulu and Jalsa — Maa Behen follows Rekha (Madhuri Dixit), a mother already juggling more than enough when life throws her the ultimate curveball: a corpse in her kitchen. Her two daughters couldn't be more different — Jaya (Triptii Dimri), the responsible one, and Sushma (Dharna Durga), the wild card. Together, this dysfunctional trio must think fast, lie faster, and somehow keep the truth from spilling out.

It's black comedy meets family drama, set in a neighbourhood that feels like every middle-class colony in India — where everyone knows everyone's business, and secrets have a shelf life of approximately thirty minutes.

## Why It Matters

The casting alone makes this worth watching. Madhuri Dixit, who last appeared alongside Triptii Dimri in Bhool Bhulaiyaa 3, is fully leaning into her post-comeback phase with projects that feel more adventurous than safe. Playing a harried mother navigating moral grey areas is a far cry from the song-and-dance routines that defined her '90s peak — and that's exactly what makes it interesting.

Then there's Triptii Dimri, who has quietly become one of the most bankable names in Hindi cinema. After Animal's breakout success, she's been selective about her choices, and a Suresh Triveni film feels like a smart bet for maintaining critical credibility alongside commercial appeal.

The supporting cast adds weight: Ravi Kishan brings his small-town comic timing, Geetanjali Kulkarni (who was terrific in Gullak) handles the neighbour dynamics, and Arunoday Singh adds an edge that the trailer hints will be significant.

## The NRI Angle

For diaspora audiences, this is straightforward: it's on Netflix, it drops globally on June 4, and it's the kind of film you can watch with family without needing to explain the cultural context. The setting is distinctly Indian, the humour is rooted in recognizable middle-class anxieties — property disputes, social reputation, keeping up appearances — and the performances promise to carry the premise past its genre-film foundation.

During promotions in Gurugram last week, the cast arrived on a decorated rickshaw to a packed mall, complete with flash mobs and the now-viral "Roti Challenge" that's been circulating on Instagram. When asked who'd cause the most chaos if Maa Behen were set in Delhi instead of Bhopal, Madhuri immediately pointed to her co-stars: "They're from here. I don't know much about Delhi."

## What to Expect

Suresh Triveni has a track record of making films that are smarter than their trailers suggest. Tumhari Sulu looked like a simple feel-good comedy but was actually a sharp commentary on ambition and domesticity. Jalsa, also on Prime Video, dealt with class and privilege through a thriller framework. If Maa Behen follows this pattern, the dead-body premise is likely just the entry point for something more layered about family loyalty, moral compromise, and who gets to define right and wrong.

The film is produced by Abundantia Entertainment in association with Opening Image Films. Runtime details haven't been confirmed, but expect a tight sub-two-hour package — Triveni doesn't waste screen time."""
})


# ============================================================
# Article 3: Bandar — Bobby Deol + Anurag Kashyap
# ============================================================
ARTICLES.append({
    "headline": "Bobby Deol Plays a Fading Star Accused of Rape in Anurag Kashyap's Bandar. It Premiered at TIFF. It Releases Friday.",
    "subheadline": "Written by the Paatal Lok team, this crime drama explores false allegations, prison survival, and a broken justice system. Bobby Deol's transformation continues with his most demanding role yet.",
    "slug": "bandar-bobby-deol-anurag-kashyap-tiff-release-june-5-nri-20260601",
    "category": "entertainment",
    "sources": json.dumps([
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Bandar_(film)"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "Zoom TV", "url": "https://www.zoomtventertainment.com"},
        {"name": "Cinema Express", "url": "https://www.cinemaexpress.com"}
    ]),
    "image_search_person": "Bobby Deol",
    "image_search_pexels": None,
    "image_search_pexels_fallback": None,
    "body": """Bobby Deol plays a once-famous television star. His ex-girlfriend accuses him of rape. His career implodes. He lands in prison. And the system he trusted to deliver justice turns out to be as broken as his public image. That's Bandar — Anurag Kashyap's crime drama that premiered at the Toronto International Film Festival last September and finally hits Indian theatres on June 5.

## The Film

Bandar — subtitled "Monkey In A Cage" for international audiences — follows Samar Mehra, an aging TV star whose life collapses after serious allegations surface following a breakup. Proclaimed innocence doesn't count for much when the court of public opinion has already rendered its verdict. The film tracks what happens after the headlines: the prison system, the corruption inside it, the violence, and the question of whether truth can survive when everyone has already picked a side.

The script comes from Sudip Sharma and Abhishek Banerjee — the writers behind Paatal Lok, Kohra, and Udta Punjab. That pedigree matters. These are storytellers who don't simplify moral complexity for audience comfort, and Bandar apparently follows that tradition. The film is reportedly inspired by real events, though specific details about which case have been kept deliberately vague.

## Bobby Deol's Reinvention

Three years ago, if you'd told anyone that Bobby Deol would be headlining an Anurag Kashyap film that premiered at TIFF, you'd have been laughed out of the room. But that's exactly where we are. After Animal gave him a career-defining villain turn, Bobby has systematically dismantled the rom-com hero image that defined — and limited — his career for two decades.

For Bandar, he shot in actual prison conditions. Producer Nikhil Dwivedi revealed that during filming, Bobby "had someone's foot on his cheek, sometimes on his stomach." It's the kind of physical commitment that suggests this isn't just acting — it's transformation.

Bobby himself has spoken about how his sisters shaped his understanding of the film's themes. "I have grown up in an environment where I have seen this myself," he said recently. "I have sisters and I used to always worry. We have grown up in a very male chauvinist kind of a world." The honesty cuts through the standard promotional noise.

## The Controversy

Bandar has already sparked debate before anyone outside TIFF has seen it. The premise — a man accused of sexual assault who maintains his innocence — inevitably draws scrutiny in the post-MeToo landscape. Producer Nikhil Dwivedi has been direct: "This is not an anti-women film. It's a pro-justice film. Nobody is saying please don't believe women when they have been wronged. We want to believe in justice more than we want to believe a particular gender."

It's a tightrope statement, and the film will be judged on whether it walks it convincingly or falls into victimhood narratives. Given Kashyap's track record of uncomfortable, morally grey storytelling — Gangs of Wasseypur, Ugly, Raman Raghav 2.0 — the bet is that Bandar won't offer easy answers.

## The Cast

Beyond Bobby, the ensemble is stacked: Sanya Malhotra, Sapna Pabbi, and Saba Azad handle key roles. Indrajith Sukumaran (Malayalam cinema's quietly brilliant presence) and Raj B. Shetty (Karnataka's indie darling) add cross-industry heft. Jitendra Joshi rounds out the cast. First-time actor Agu Stanley Chiedozie — a Nigerian content creator who moved to India seven years ago and learned fluent Hindi — makes his Bollywood debut, calling it "a full-circle moment."

## The NRI Factor

Two things make Bandar relevant for diaspora audiences. First, it premiered at TIFF — a festival that NRI film communities in Toronto follow closely. The buzz from that screening has been circulating in diaspora film circles for months. Second, the themes are universal: power, accusation, justice, and what happens when a system designed to protect people fails them. These conversations don't respect borders.

Distributed by Zee Studios, Bandar releases worldwide on June 5. Runtime is 140 minutes. The film is in Hindi, Marathi, and English."""
})


# --- Main execution ---

def process_article(article):
    art_id = str(uuid.uuid4())
    slug = article["slug"]
    print(f"\n{'='*60}")
    print(f"Processing: {article['headline'][:60]}...")
    print(f"  Slug: {slug}")
    
    # Image sourcing
    image_url = None
    image_attribution = None
    
    # 1. Try Wikipedia for person articles
    if article.get("image_search_person"):
        person = article["image_search_person"]
        print(f"  Trying Wikipedia for: {person}")
        wiki_url = fetch_wikipedia_person_image(person)
        if wiki_url:
            # Upload to Supabase for permanence
            filename = f"{art_id}.jpg"
            uploaded = upload_to_supabase_storage(wiki_url, filename)
            if uploaded:
                image_url = uploaded
                image_attribution = "Wikimedia Commons"
    
    # 2. Fall back to Pexels
    if not image_url and article.get("image_search_pexels"):
        print(f"  Trying Pexels for: {article['image_search_pexels']}")
        pexels_url = fetch_pexels_image(
            article["image_search_pexels"],
            article.get("image_search_pexels_fallback")
        )
        if pexels_url:
            # Pexels URLs are permanent, but upload to Supabase for consistency
            filename = f"{art_id}.jpg"
            uploaded = upload_to_supabase_storage(pexels_url, filename)
            if uploaded:
                image_url = uploaded
                image_attribution = "Pexels"
            else:
                # Fall back to direct Pexels URL (permanent)
                image_url = pexels_url
                image_attribution = "Pexels"
    
    if image_url:
        print(f"  ✓ Final image: {image_url[:80]}...")
    else:
        print(f"  ⚠ No image found — publishing without image")
    
    # Build payload
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": slug,
        "category": article["category"],
        "vertical": article["category"],
        "body": article["body"].strip(),
        "sources": article["sources"],
        "status": "published",
        "published_at": now,
        "is_editorial": False,
    }
    
    if image_url:
        payload["image_url"] = image_url
    if image_attribution:
        payload["image_attribution"] = image_attribution
    
    result = sb_insert("p2_articles", payload)
    if result:
        print(f"  ✓ Published: {slug}")
        return True
    else:
        print(f"  ✗ Failed to publish: {slug}")
        return False


if __name__ == "__main__":
    print(f"Entertainment Writer Run — {datetime.now(timezone.utc).isoformat()}")
    print(f"Articles to write: {len(ARTICLES)}")
    
    success = 0
    for article in ARTICLES:
        if process_article(article):
            success += 1
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"Done. Published {success}/{len(ARTICLES)} articles.")
