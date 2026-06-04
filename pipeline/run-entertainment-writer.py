#!/usr/bin/env python3
"""
The Videshi — Entertainment Writer (scheduled run)
Writes 3 articles on fresh entertainment topics with proper image sourcing.
"""

import json
import os
import sys
import uuid
import time
import io
import subprocess
from datetime import datetime, timezone

import requests
from PIL import Image

# ─── env ───────────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[7:]
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            os.environ[k] = v

# Load workspace env first (has GOOGLE_PLACES_API_KEY etc.)
# Then home env last so JWT-format keys override the shorter workspace keys
load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}


# ─── image helpers ─────────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
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
    """Search Wikimedia Commons. Returns list of dicts."""
    import urllib.parse
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
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers=UA, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(*queries):
    """Search Pexels with multiple fallback queries. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in queries:
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=3&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{q}': {url[:70]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    result = buf.getvalue()
    print(f"  → Compressed: {len(img_bytes)//1024}KB → {len(result)//1024}KB ({img.width}x{img.height})")
    return result


def upload_image_to_supabase(image_url, filename):
    """Download image, compress, upload to Supabase article-images bucket. Returns public URL."""
    try:
        r = requests.get(image_url, headers=UA, timeout=20)
        if r.status_code != 200:
            print(f"  ✗ Failed to download image: HTTP {r.status_code}")
            return None
        raw = r.content
        if len(raw) < 5000:
            print(f"  ✗ Image too small ({len(raw)} bytes), skipping")
            return None

        compressed = compress_image(raw)

        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=compressed,
            timeout=20,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ✗ Image upload error: {e}")
    return None


def source_image(person_names, topic_queries, pexels_queries, slug):
    """Multi-source image sourcing. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Source 1: Wikipedia (for person articles)
    for name in person_names:
        wiki_img = fetch_wikipedia_person_image(name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "priority": 1})
            break

    # Source 2: Wikimedia Commons
    for query in topic_queries:
        commons = fetch_wikimedia_commons_images(query, limit=3)
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "priority": 2})
        if commons:
            break

    # Source 3: Pexels
    pexels_img = fetch_pexels_image(*pexels_queries)
    if pexels_img:
        candidates.append({"url": pexels_img, "source": "pexels", "priority": 3})

    if not candidates:
        print(f"  ✗ No image candidates found for {slug}")
        return None, None

    # Pick best: prefer wikipedia > commons > pexels
    candidates.sort(key=lambda x: x["priority"])
    best = candidates[0]

    filename = f"{slug}.jpg"
    final_url = upload_image_to_supabase(best["url"], filename)
    if final_url:
        attr = "Wikimedia Commons" if best["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
        return final_url, attr

    # Try next candidates
    for c in candidates[1:]:
        final_url = upload_image_to_supabase(c["url"], filename)
        if final_url:
            attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
            return final_url, attr

    return None, None


# ─── article insertion ─────────────────────────────────────────────────────────

def insert_article(article):
    """Insert article to Supabase p2_articles."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": [{"name": s, "url": ""} for s in article.get("sources", [])],
        "image_url": article.get("image_url", ""),
        "image_attribution": article.get("image_attribution", ""),
        "is_editorial": False,
    }

    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=15,
    )
    if r.status_code in (200, 201):
        print(f"✅ Published: {article['headline'][:60]}... (slug: {article['slug']})")
        return art_id
    else:
        print(f"❌ Insert failed [{r.status_code}]: {r.text[:300]}")
        return None


# ─── articles ──────────────────────────────────────────────────────────────────

ARTICLES = [
    {
        "headline": "Cocktail 2 Trailer Is Here. Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna Are Doing What Bollywood Does Best When It Stops Trying So Hard.",
        "subheadline": "The spiritual sequel to the 2012 sleeper hit arrives June 19, and for the diaspora, it's the kind of summer escapism that plays just as well in Edison as it does in Bandra.",
        "slug": "cocktail-2-trailer-shahid-kapoor-kriti-sanon-rashmika-mandanna-june-19-nri-20260604",
        "body": """The trailer for *Cocktail 2* dropped on June 2, and within hours it had done exactly what a Bollywood romantic comedy trailer is supposed to do: it made people argue about which character they identified with most.

Shahid Kapoor plays Kunal, Kriti Sanon is Ally, and Rashmika Mandanna is Diya. Three people. One friendship. The kind of romantic geometry that the original *Cocktail* made unexpectedly resonant back in 2012, when Deepika Padukone walked away with the film and a career-defining turn as Veronica.

This time, the equation is different. Director Homi Adajania returns, but the writing credits now include Luv Ranjan and Tarun Jain, which signals a film that wants to be both commercially accessible and emotionally grounded. The trailer gives glimpses of Sicily (shot with Italian line producers, no less), Delhi, and Chandigarh, hopping between locations with the kind of casual affluence that Bollywood rom-coms have turned into an art form.

## What the Trailer Tells Us

The three-minute preview lays out a familiar but well-executed premise: two people who are clearly meant for each other, one person who complicates things, and a city that provides the backdrop for all the confusion. What separates this from the assembly-line rom-com is tone. There are moments of genuine humor — Shahid's delivery has always been underrated in comedy — and the editing suggests a film that knows when to linger and when to cut.

Kriti Sanon gets the showier moments in the trailer, playing a character who seems to carry the story's emotional center. Rashmika Mandanna, in what the producers are calling a role of "beautiful flaws," appears to bring a vulnerability that her Telugu and Kannada fans already know well but Hindi audiences are only beginning to see.

Pritam handles the music, which in a *Cocktail* film is half the marketing. Two tracks have already been previewed to media — *Mashooka*, described as an energetic romantic number shot in Sicily, and *Tujhko*, an Arijit Singh ballad that reportedly moved journalists at a recent preview event. If Pritam delivers even half the impact of *Tumhi Ho Bandhu* or *Daaru Desi* from the original, the soundtrack alone will carry the film through its promotional cycle.

## The Diaspora Calculation

For the Indian diaspora, *Cocktail 2* lands in a June window that is already stacked with heavier fare. *Peddi* opened this week, *Governor* arrives June 12, and *Welcome To The Jungle* closes out the month on June 26. In that landscape, a breezy, music-driven romance with three bankable stars is not just counterprogramming — it is exactly the kind of film that NRI families default to when they want an evening out without the emotional weight of a period drama or the volume of an action spectacle.

The original *Cocktail* did ₹120 crore worldwide, a substantial portion from overseas markets where its London setting and modern relationship dynamics played exceptionally well. This sequel, produced by Maddock Films, seems designed to replicate that audience — young professionals in the US, UK, Canada, and the Gulf who want Indian cinema to meet them where they actually are: dating apps, complicated friendships, commitment anxiety, and the quiet terror of being in your thirties without a plan.

## Why It Matters

In a year where Bollywood's calendar is dominated by franchise actioners, biographical dramas, and high-concept thrillers, *Cocktail 2* is a bet on something simpler: that people still want to watch attractive people fall in love to good music. It is not reinventing anything. It is just doing the old thing with enough craft and star power to make it feel worthwhile.

The film hits theaters on June 19. In the meantime, the trailer is doing its job — it has people talking about Shahid's comic timing, Kriti's wardrobe, Rashmika's eyes, and whether a film about messy modern love can hold its own against superheroes and sports dramas. The early signs suggest it can.""",
        "sources": [
            "Filmfare – Cocktail 2 Trailer: Shahid Kapoor, Kriti Sanon & Rashmika Mandanna Navigate Love & Friendship (Jun 2, 2026)",
            "The Hollywood Reporter India – Cocktail 2 Trailer: Shahid, Kriti & Rashmika Return With Messy Modern Romance (Jun 2, 2026)",
            "Bollywood Hungama – Cocktail 2 Official Trailer details (Jun 2, 2026)"
        ],
        "person_names": ["Shahid Kapoor", "Kriti Sanon"],
        "topic_queries": ["Cocktail 2 Bollywood film", "Shahid Kapoor actor Bollywood"],
        "pexels_queries": ["Bollywood film romance couple", "modern love couple city"],
    },
    {
        "headline": "Manoj Bajpayee Is Playing the Man Who Stopped India From Going Bankrupt. Most Indians Have Never Heard of Him.",
        "subheadline": "Governor, releasing June 12, dramatizes the 1991 economic crisis through the story of RBI Governor S. Venkitaramanan — the bureaucrat who shipped India's gold overseas to save the nation.",
        "slug": "governor-manoj-bajpayee-rbi-venkitaramanan-1991-economic-crisis-nri-20260604",
        "body": """There is an irony at the heart of *Governor* that the film's makers are counting on audiences to notice: the very economic liberalization that created the Indian diaspora — the IT boom, the H-1B pipeline, the NRI property market, the remittance economy — was enabled by a man most Indians could not name if asked.

S. Venkitaramanan became the 18th Governor of the Reserve Bank of India in December 1990, inheriting a nation that was weeks away from defaulting on its sovereign debt. Foreign exchange reserves had dwindled to roughly two weeks of import cover. The country's credit rating was in freefall. And the solution Venkitaramanan authorized — airlifting 47 tonnes of gold from the RBI's vaults to the Bank of England and the Union Bank of Switzerland as collateral for emergency loans — remains one of the most dramatic economic maneuvers in Indian history.

Manoj Bajpayee plays the fictional counterpart of this man, and if the trailer is any indication, he has found the role's center: a quiet, methodical civil servant who understood that the country's survival required decisions that no politician would publicly endorse.

## The Film's Architecture

Directed by Chinmay Mandlekar — best known for his Marathi-language work and making his Hindi directorial debut here — *Governor* is structured as a political thriller set entirely during the crisis months of 1990-91. The screenplay, written by Suvendu Bhattacharyjee, Saurabh Bharat, Ravi Asrani, and producer Vipul Amrutlal Shah, draws from documented accounts of what happened inside the RBI and the Finance Ministry during those weeks.

Bajpayee has spoken publicly about the challenges. He could not visit the RBI's offices — they remain restricted zones. He did not meet any serving or former governors. Instead, he worked from whatever documentation and published accounts were available, carrying reference pages with him on set to ensure factual accuracy.

Adah Sharma appears in a supporting role, and the technical crew includes Javed Akhtar (lyrics) and Amit Trivedi (music). Trivedi's involvement is noteworthy — he has consistently delivered atmospheric, era-appropriate scores, and a film set in the bureaucratic corridors of early-1990s India needs precisely that register: tense, institutional, and human.

## Why the Diaspora Should Pay Attention

For NRIs in the US, UK, and Canada, the 1991 crisis is not ancient history. It is origin story. The liberalization policies that followed Venkitaramanan's emergency measures — implemented by Manmohan Singh as Finance Minister — are directly responsible for the economic conditions that made mass Indian emigration to the West possible. The IT outsourcing boom, the opening of Indian markets to foreign investment, the creation of a new professional middle class that could afford US university tuition — all of it traces back to those months.

A film that dramatizes this moment is, for the diaspora, something closer to autobiography than political thriller. Every NRI software engineer in the Bay Area, every doctor in the NHS, every accountant in Toronto owes something to the decisions made inside the RBI in 1991. *Governor* is asking them to understand the cost.

## The Production Challenge

Recreating 1990s India on film is harder than it sounds. A source close to the production told Bollywood Hungama that the team spent significant resources eliminating modern anachronisms from real outdoor locations — mobile towers, LED billboards, contemporary cars, even hairstyles in crowd scenes had to be period-accurate. The attention to detail suggests a production that takes its historical material seriously, which is not always a given in Hindi cinema's treatment of recent history.

The film releases on June 12, sharing the week with *Main Vaapas Aaunga* (Imtiaz Ali's Partition drama) and *Hai Jawani Toh Ishq Hona Hai* (David Dhawan's comedy). In that company, *Governor* is the most unusual proposition — a political drama about monetary policy and institutional courage. It is the kind of film that Manoj Bajpayee has spent his career making possible: the one that should not work commercially but might, because the actor at its center refuses to let it be anything less than compelling.""",
        "sources": [
            "Bollywood Hungama – Makers of Governor had a major challenge of recreating a bygone era (Jun 3, 2026)",
            "Cinema Express – Who is S Venkitaramanan, the real-life inspiration for Manoj Bajpayee's protagonist in Governor? (Jun 1, 2026)",
            "Bollywood Hungama – Manoj Bajpayee on finally working with Vipul Amrutlal Shah in Governor (May 28, 2026)"
        ],
        "person_names": ["Manoj Bajpayee"],
        "topic_queries": ["Manoj Bajpayee Governor film", "Reserve Bank India 1991 gold crisis"],
        "pexels_queries": ["Reserve Bank India building", "India financial crisis economics"],
    },
    {
        "headline": "Welcome To The Jungle Has Fifteen Stars, One Jungle, and the Weight of Akshay Kumar's Entire Comeback Riding on a Punch Line.",
        "subheadline": "The third Welcome film arrives June 26 with the biggest Bollywood ensemble cast in years. After Bhooth Bangla crossed ₹267 crore, Akshay Kumar is betting that slapstick is the genre the audience actually wants.",
        "slug": "welcome-to-the-jungle-akshay-kumar-suniel-shetty-franchise-june-26-nri-20260604",
        "body": """Count them: Akshay Kumar, Suniel Shetty, Paresh Rawal, Sanjay Dutt, Arshad Warsi, Raveena Tandon, Lara Dutta, Jacqueline Fernandez, Disha Patani, Johnny Lever, Rajpal Yadav, Tusshar Kapoor, Shreyas Talpade, Krushna Abhishek, Kiku Sharda, Daler Mehndi, Mika Singh, Rahul Dev, and Mukesh Tiwari. That is not a film. That is a census.

*Welcome To The Jungle*, the third installment of the *Welcome* franchise, arrives in cinemas on June 26. Directed by Ahmed Khan and produced by Firoz Nadiadwala, it is positioned as the summer's biggest family entertainer — a phrase that in Bollywood means loud, broad, and engineered to make a family of four in a multiplex forget that the world outside is complicated.

The teaser dropped on May 15 and did exactly what it needed to do: it showed Akshay Kumar in a dark suit walking down a red carpet laid in the middle of a jungle, surrounded by chaos. That single image — the absurd juxtaposition of formality and wilderness — is the franchise's entire thesis statement.

## The Franchise Equation

The original *Welcome* (2007) was a gangster comedy that nobody expected to become a cultural touchstone. Directed by Anees Bazmee, it made ₹108 crore worldwide — enormous for its time — and embedded itself into the Indian diaspora's reference vocabulary. Lines from that film still circulate on WhatsApp forwards. *Welcome Back* (2015) made ₹137 crore despite mixed reviews, proving that the franchise was less about quality and more about occasion.

*Welcome To The Jungle* changes the director (Ahmed Khan replaces Bazmee), the setting (a jungle backdrop instead of Dubai penthouses), and the tone (more physical comedy, if the teaser is any indication). What it keeps is the franchise's central promise: you will not have to think, and you will laugh anyway.

## Akshay Kumar's Year

The timing matters. Akshay Kumar enters *Welcome To The Jungle* on the back of *Bhooth Bangla*, which has crossed ₹267 crore worldwide in its seventh week — a number that seemed impossible a year ago, when his box office track record was a running industry joke. Priyadarshan's horror comedy proved that Akshay's audience had not disappeared; it had simply been waiting for him to return to the genre where his instincts are sharpest.

Comedy has always been Akshay Kumar's superpower. Before action franchises and patriotic dramas became his brand, he was the man behind *Hera Pheri*, *Garam Masala*, *Bhagam Bhag*, and *Housefull*. His ability to play straight while everything around him descends into chaos is a specific skill — not all actors have it, and the ones who do rarely get credit for it. *Welcome To The Jungle* is designed to showcase precisely that register.

## The NRI Appeal

For the Indian diaspora, the *Welcome* franchise occupies a particular cultural niche: it is the film you watch when you want to feel Indian without the emotional labor of engaging with India's complexities. There are no partition stories, no caste narratives, no political statements. There is only Paresh Rawal doing Paresh Rawal things, Johnny Lever finding comedy in physical impossibilities, and Akshay Kumar navigating absurd situations with a deadpan that would make Buster Keaton nod in recognition.

JioStar has reportedly acquired the domestic theatrical rights along with satellite and OTT rights, meaning the film will eventually stream on JioHotstar — a platform that has become the default for diaspora families who want Hindi content without navigating multiple subscription tiers. That distribution strategy ensures *Welcome To The Jungle* will have a long tail well beyond its theatrical run.

## What to Expect

Do not expect a good film. Expect a *fun* film. The *Welcome* franchise has never trafficked in craft; it traffics in volume. The humor is broad, the plot is incidental, the performances are pitched at a register that prioritizes energy over subtlety. And for an audience that has spent the first half of 2026 processing spy thrillers, biographical dramas, and epic period films, that might be exactly the right prescription.

June 26. Fifteen stars. One jungle. Zero pretense. The math works.""",
        "sources": [
            "Bollywood Hungama – Welcome To The Jungle is not just a comedy; it's Bollywood's biggest stressbuster of 2026 (Jun 2, 2026)",
            "Sacnilk – Welcome To The Jungle Teaser: Akshay Kumar and Gang Promise A Laugh Riot (May 15, 2026)",
            "Filmfare – Upcoming Bollywood Movies To Watch In June 2026 (Jun 1, 2026)"
        ],
        "person_names": ["Akshay Kumar"],
        "topic_queries": ["Akshay Kumar Welcome To The Jungle film", "Welcome Bollywood comedy franchise"],
        "pexels_queries": ["Bollywood comedy film set", "jungle adventure movie set"],
    },
]


# ─── main ──────────────────────────────────────────────────────────────────────

def main():
    if not SB_URL or not SB_KEY:
        print("❌ Missing Supabase env vars")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"The Videshi — Entertainment Writer")
    print(f"Run: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}\n")

    published = 0

    for i, article in enumerate(ARTICLES, 1):
        print(f"\n── Article {i}/{len(ARTICLES)}: {article['headline'][:55]}... ──\n")

        # Source image
        print("  Sourcing image...")
        img_url, img_attr = source_image(
            article["person_names"],
            article["topic_queries"],
            article["pexels_queries"],
            article["slug"],
        )

        article["image_url"] = img_url or ""
        article["image_attribution"] = img_attr or ""

        # Insert
        art_id = insert_article(article)
        if art_id:
            published += 1

        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Done. Published {published}/{len(ARTICLES)} articles.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
