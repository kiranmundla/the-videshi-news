#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-04 batch"""

import json, os, re, sys, time, uuid, hashlib
from datetime import datetime, timezone

import requests
from PIL import Image
import io

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ─── Image helpers ───

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = person_name.replace(' ', '_')
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(encoded)}",
            headers={"User-Agent": UA},
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

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
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
            params=params,
            headers={"User-Agent": UA},
            timeout=15
        )
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
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for an image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
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
    return buf.getvalue()

def upload_to_supabase(img_bytes, filename):
    """Upload image bytes to Supabase storage article-images bucket."""
    compressed = compress_image(img_bytes)
    size_kb = len(compressed) / 1024
    if size_kb < 10:
        print(f"  ⚠ Compressed image too small ({size_kb:.0f} KB), skipping upload")
        return None
    print(f"  📦 Uploading {filename} ({size_kb:.0f} KB)...")
    
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    r = requests.post(url, data=compressed, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }, timeout=30)
    
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded: {public_url[:80]}...")
        return public_url
    else:
        print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
        return None

def download_image(url):
    """Download image bytes from URL."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and r.headers.get('Content-Type', '').startswith('image/'):
            if len(r.content) > 5000:
                return r.content
            else:
                print(f"  ⚠ Image too small ({len(r.content)} bytes)")
        else:
            print(f"  ⚠ Download failed: status={r.status_code}, type={r.headers.get('Content-Type')}")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None

def source_image(person_name=None, topic_queries=None, pexels_query=None, slug="article"):
    """Multi-source image search. Returns (url, attribution, caption_hint) or (None, None, None)."""
    candidates = []
    
    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "priority": 1})
    
    # Source 2: Wikimedia Commons
    if topic_queries:
        for q in topic_queries[:2]:
            results = fetch_wikimedia_commons_images(q)
            for r in results[:2]:
                candidates.append({"url": r["url"], "source": "wikimedia_commons", "priority": 2})
    
    # Source 3: Pexels
    if pexels_query:
        pexels_img = fetch_pexels_image(pexels_query)
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels", "priority": 3})
    
    # Pick best and upload to Supabase
    for cand in sorted(candidates, key=lambda c: c["priority"]):
        img_bytes = download_image(cand["url"])
        if img_bytes:
            filename = f"{slug}.jpg"
            final_url = upload_to_supabase(img_bytes, filename)
            if final_url:
                attr = "Wikimedia Commons" if cand["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return final_url, attr, cand["source"]
    
    print("  ⚠ No suitable image found from any source")
    return None, None, None

def insert_article(article):
    """Insert article into Supabase."""
    print(f"\n📝 Inserting: {article['headline'][:60]}...")
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        json=article,
        headers=HEADERS_SB,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            art_id = result[0].get('id', 'unknown')
            print(f"  ✓ Published: {art_id}")
            return art_id
        print(f"  ✓ Published (response: {str(r.text)[:100]})")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None

# ─── Articles ───

def write_aishwarya_jw_marriott():
    """Article 1: Aishwarya Rai named JW Marriott Global Brand Ambassador"""
    print("\n" + "="*60)
    print("ARTICLE 1: Aishwarya Rai × JW Marriott")
    print("="*60)
    
    slug = "aishwarya-rai-jw-marriott-global-brand-ambassador-stay-in-the-moment-nri-20260604"
    
    # Image sourcing
    img_url, img_attr, img_src = source_image(
        person_name="Aishwarya Rai",
        topic_queries=["Aishwarya Rai Bachchan actress", "Aishwarya Rai Cannes"],
        pexels_query="luxury hotel lobby elegant",
        slug=slug
    )
    
    headline = "Aishwarya Rai Just Became the Global Face of JW Marriott. For the Diaspora, the Appointment Says More Than the Press Release."
    
    subheadline = "The hotel chain's 'Stay in the Moment' campaign now has a face that NRIs have watched evolve from Miss World to Cannes regular to a Bollywood icon who chooses her battles. Here's why the partnership matters."
    
    body = """When JW Marriott announced Aishwarya Rai Bachchan as its Global Brand Ambassador on June 3, the press release did what press releases do — it talked about "mindful travel," "intentional luxury," and "meaningful connections." Strip away the corporate poetry, and what remains is a statement of reach that neither party could make alone.

## The Appointment

Aishwarya will front JW Marriott's global "Stay in the Moment" campaign across film, print, and digital platforms. She will also participate in curated brand experiences in India and select international markets. The partnership positions her not as a regional celebrity lending her face to a Western brand, but as a global figure extending a global brand's relevance into a market that is rewriting the rules of luxury travel.

"Travel has always been an important part of my life, both personally and professionally," Aishwarya said in the announcement. "The most meaningful experiences are often the quietest ones, when you are fully aware of where you are and who you are with."

Bruce Rohr, Vice President and Global Brand Leader of JW Marriott, called her "a natural embodiment of JW Marriott and an ideal partner for the brand."

## Why This Matters for Indian Travellers

The numbers behind the appointment tell their own story. Indian travellers are now the fastest-growing outbound luxury segment globally. JW Marriott operates more than 130 properties worldwide, and India is one of its most dynamic portfolios. The demand is being driven by rising affluence, multigenerational journeys, and a generational shift toward experience-led stays over transactional ones.

For decades, luxury hospitality marketed to Indians followed a familiar formula: show marble lobbies, mention thread counts, and assume aspiration would do the rest. That playbook is aging. Today's Indian luxury traveller — particularly the NRI who splits time between continents — wants what Marriott's campaign language actually describes: presence, purpose, and connection. They have already stayed at the marble lobbies. Now they want to feel something.

## The Diaspora Angle

For NRIs, Aishwarya Rai occupies a peculiar and specific space. She is not the Bollywood star you discovered last year. She is the one your parents watched win Miss World in 1994, the one your aunties debated over at every family gathering for two decades, the one who showed up at Cannes year after year until the West stopped treating her presence as a novelty and started treating it as a fixture.

That kind of longevity is exactly what a hotel brand trading on permanence needs. JW Marriott is not selling flash. It is selling the idea that luxury is a posture, not a purchase. In Aishwarya, they have found someone whose public life has been an exercise in exactly that discipline.

## The Business Context

The appointment arrives at a moment when India's luxury travel market is undergoing structural change. Domestic premium travel is rising as fast as outbound, driven by wellness retreats, heritage properties, and experience-first booking behaviour. The Indian luxury traveller no longer fits a single profile. They could be a tech founder from Bengaluru booking a weekend at a JW in Mussoorie, or a second-generation NRI in New Jersey choosing between a Maldives villa and a Rajasthan palace.

Marriott's bet is that Aishwarya bridges both segments. She is familiar enough to resonate with the domestic market and global enough to anchor a campaign that runs from New York to Dubai to Tokyo.

## What Comes Next

The campaign will roll out across international markets in the coming months. For NRIs who have watched Aishwarya Rai evolve through every possible phase of Indian public life, the JW Marriott partnership is less a surprise than a confirmation. She has always been the one who understood that the most powerful move in a noisy room is stillness.

JW Marriott is hoping that philosophy sells suites. Based on the trajectory of Indian luxury travel, they are probably right."""
    
    image_caption = "Aishwarya Rai Bachchan, newly appointed Global Brand Ambassador for JW Marriott"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr or "Wikimedia Commons",
        "sources": json.dumps([
            "https://hollywoodreporterindia.com",
            "https://bollywoodhungama.com",
            "https://restaurantindia.in"
        ]),
        "is_editorial": False
    }
    
    return insert_article(article)


def write_made_in_india_titan():
    """Article 2: Made in India: A Titan Story — Jim Sarbh, Naseeruddin Shah"""
    print("\n" + "="*60)
    print("ARTICLE 2: Made in India: A Titan Story")
    print("="*60)
    
    slug = "made-in-india-titan-story-jim-sarbh-naseeruddin-shah-amazon-mx-player-nri-20260604"
    
    # Image sourcing — Jim Sarbh is the lead
    img_url, img_attr, img_src = source_image(
        person_name="Jim Sarbh",
        topic_queries=["Jim Sarbh actor", "Titan watches India", "Naseeruddin Shah actor"],
        pexels_query="vintage wristwatch elegant",
        slug=slug
    )
    
    headline = "Made in India: A Titan Story Is the Show Nobody Expected to Be This Good. Jim Sarbh and Naseeruddin Shah Make Watchmaking Feel Like War."
    
    subheadline = "A six-episode series about how Xerxes Desai built India's first world-class watch brand just dropped on Amazon MX Player. For NRIs who grew up with a Titan on their wrist, this one hits different."
    
    body = """The pitch sounds like a corporate PowerPoint brought to life: a series about the founding of Titan, India's iconic watch brand, produced in partnership with the Tata legacy, streaming on Amazon MX Player. Every instinct says it should be branded content dressed up as drama. Every instinct is wrong.

*Made in India: A Titan Story*, directed by Robbie Grewal and adapted from Vinay Kamath's book *Titan: India's Most Successful Consumer Brand*, is drawing 3.5 to 4-star reviews across the board. The consensus is unanimous and slightly bewildered: a series about making watches in pre-liberalisation India has no business being this compelling.

## The Story

The series opens with two pivotal moments. Xerxes Desai, a forward-thinking Tata Group executive played by Jim Sarbh, is returning to the company after a successful stint elsewhere. Meanwhile, JRD Tata — played by Naseeruddin Shah with a gravitas that makes you forget you are watching an actor — sits across from a Swiss watchmaker who tells him, more or less, that India cannot make a world-class watch.

Rather than accept the insult, JRD channels it into a mission. Desai becomes the man tasked with proving Switzerland wrong. What follows is six episodes of bureaucratic warfare, financial brinkmanship, technological setbacks, and the slow, grinding work of building something from nothing in a country that had not yet learned to believe in its own manufacturing ambitions.

## The Performances

Jim Sarbh, who nailed Homi J Bhabha in *Rocket Boys* and played a ruthless billionaire in *Kuberaa*, delivers another shape-shifting performance. His Xerxes Desai is not a shouting visionary. He is a quiet operator who understands that building a watch brand requires convincing everyone around you — the government, the financiers, the skeptics, your own team — to believe in an idea that sounds impossible until the day it isn't.

Naseeruddin Shah as JRD Tata is perfect casting. Every time Sarbh's Desai seems cornered, Shah appears on screen with the kind of calm authority that makes you feel things will work out. He does not dominate scenes. He steadies them.

Vaibhav Tatwawadi as Akash Dikshit, Desai's friend and collaborator, turns out to be the series' quiet surprise. The supporting cast — Kaveri Seth, Lakshvir Saran, Joy Sengupta, and Paresh Ganatra — fills out the world around the central mission without ever feeling like decoration.

## Why NRIs Will Feel This

There is a particular sensation that Indian diaspora audiences know well. You are standing in a store somewhere in America or London, you see a Titan watch in someone's collection or in an old photo, and you feel a flash of something that has nothing to do with horology. It is pride, and it is memory, and it is the knowledge that the object in front of you was built by people who were told it could not be done.

*Made in India* captures the origin of that feeling. It does not wave flags or manufacture patriotism. It shows the work — the late nights, the failed prototypes, the licence raj that treated ambition as a threat — and trusts the audience to understand what was at stake. For NRIs who grew up in households where a Titan Raga was the graduation gift and a Titan Edge was the promotion reward, this series is personal history presented as drama.

## The Verdict

The show is not perfect. Six episodes at 55 minutes each occasionally let the pacing drift, and some of the period detail feels more functional than immersive. But these are minor complaints against a show that takes a corporate origin story and makes it feel urgent, human, and emotionally earned.

In a streaming landscape crowded with dark thrillers and franchise sequels, *Made in India: A Titan Story* is a reminder that the most gripping stories are sometimes the ones about people who simply refused to quit. It is streaming now on Amazon MX Player. If you have ever worn a Titan watch, you owe it to yourself to understand how it got to your wrist."""

    image_caption = "Jim Sarbh stars as Xerxes Desai in Made in India: A Titan Story"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr or "Wikimedia Commons",
        "sources": json.dumps([
            "https://indiaforums.com",
            "https://koimoi.com",
            "https://hollywoodreporterindia.com",
            "https://mensxp.com"
        ]),
        "is_editorial": False
    }
    
    return insert_article(article)


def write_hai_jawani():
    """Article 3: Hai Jawani Toh Ishq Hona Hai — David Dhawan's final film"""
    print("\n" + "="*60)
    print("ARTICLE 3: Hai Jawani Toh Ishq Hona Hai — David Dhawan's Last Film")
    print("="*60)
    
    slug = "hai-jawani-toh-ishq-hona-hai-david-dhawan-final-film-varun-dhawan-june-5-nri-20260604"
    
    # Image sourcing
    img_url, img_attr, img_src = source_image(
        person_name="David Dhawan",
        topic_queries=["David Dhawan director Bollywood", "Varun Dhawan actor"],
        pexels_query="cinema director movie set Bollywood",
        slug=slug
    )
    
    headline = "David Dhawan Is Retiring After This Film. For a Generation of NRIs, He Taught Them How to Laugh in Hindi."
    
    subheadline = "Hai Jawani Toh Ishq Hona Hai, starring Varun Dhawan, Mrunal Thakur, and Pooja Hegde, releases June 5. It is the last directorial venture of the man who made Govinda a god and made every Indian living room a comedy club."
    
    body = """There is a version of this story that is just a release-date article. Hai Jawani Toh Ishq Hona Hai, a romantic comedy directed by David Dhawan, starring his son Varun Dhawan alongside Mrunal Thakur and Pooja Hegde, releases in theatres on June 5. Budget is reasonable. CBFC rating is U/A. Runtime is a brisk two hours and sixteen minutes. Fifty percent off on first-day tickets. Move on.

But this is not just a release. This is the last time David Dhawan will sit in the director's chair. He has announced his retirement after this film. And for a generation of Indians who grew up on his work — particularly those who now live thousands of miles from the country where they first watched *Hero No. 1* on a pirated VHS — that carries weight.

## The Film

The plot follows Jass, played by Varun Dhawan, and Bani, played by Mrunal Thakur. They have been married for five years. The marriage crumbles over the usual fault lines — career versus family, ambition versus domesticity. After the split, Jass travels abroad and meets a new woman, played by Pooja Hegde. What follows is the David Dhawan formula in its final form: situational chaos, mistaken identities, romantic entanglements, and a resolution that believes love — however messy — eventually finds its way.

The cast also includes Mouni Roy, Jimmy Shergill, Chunky Panday, Maniesh Paul, Kubbra Sait, Rakesh Bedi, and Ali Asgar. It is the kind of ensemble that David Dhawan has always preferred — comedians who understand timing, actors who are willing to look ridiculous, and a leading man who can carry both the romance and the slapstick.

## The Legacy Being Retired

David Dhawan directed 45 films over four decades. He made Govinda into a comedy institution. He gave Bollywood *Coolie No. 1*, *Hero No. 1*, *Bade Miyan Chote Miyan*, *Haseena Maan Jaayegi*, and *Partner*. He did not invent the Hindi film comedy, but he industrialised it — built a machine that could reliably produce two hours of laughter without pretending to be anything other than entertainment.

His critics always said the same things: the films were formulaic, the jokes were broad, the plots were interchangeable. His audience never cared. They showed up because David Dhawan understood something most filmmakers do not — that making someone laugh is harder than making them cry, and that there is no shame in optimising for joy.

## The NRI Connection

For Indians in the diaspora, David Dhawan comedies occupied a very specific role. They were the films you watched when you were homesick. Not the Yash Chopra romances that made you ache for Switzerland standing in for India, not the Karan Johar dramas that turned family dysfunction into spectacle. David Dhawan films were simpler than that. They were the cinematic equivalent of dal chawal — unambitious, reliable, and exactly what you needed.

In rented apartments in New Jersey, in student housing in London, in tech corridors in the Bay Area, Indian families gathered around television sets and watched Govinda dance in colours that did not exist in nature, and they laughed. The laughter was not ironic. It was not guilty. It was the specific, uncomplicated laughter of people who needed two hours of not thinking about visas, mortgages, or the distance between who they were becoming and who they had been.

## The Father-Son Angle

This is Varun Dhawan's fourth film with his father, after *Main Tera Hero* (2014), *Judwaa 2* (2017), and *Coolie No. 1* (2020). The earlier collaborations were attempts to transplant the classic David Dhawan formula into a new generation. Some worked better than others. None had the stakes that this one carries.

Varun has spoken publicly about what it means to close this chapter. He has described the film as a gift — from son to father, from father to audience. Whether it works commercially or not, the emotional mathematics of the project are unmistakable: the son is starring in the last thing his father will ever make.

## What to Expect

Advance reports suggest the film has been positioned carefully. The 50% ticket discount on opening day is designed to fill theatres. The U/A rating ensures family audiences can attend without hesitation. The 2-hour-16-minute runtime is tight by Bollywood standards, suggesting the edit was disciplined.

Whether *Hai Jawani Toh Ishq Hona Hai* is a fitting final chapter or a standard David Dhawan outing that happens to be the last one, only Thursday will tell. But for the audience that grew up on his films, the verdict is almost beside the point. You show up because he showed up for you, for forty years, every single time you needed to laugh."""

    image_caption = "Director David Dhawan, whose final film Hai Jawani Toh Ishq Hona Hai releases June 5"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr or "Wikimedia Commons",
        "sources": json.dumps([
            "https://sacnilk.com",
            "https://bollywoodhungama.com",
            "https://koimoi.com"
        ]),
        "is_editorial": False
    }
    
    return insert_article(article)


# ─── Main ───

if __name__ == "__main__":
    print("="*60)
    print("The Videshi — Entertainment Writer")
    print(f"Run: {datetime.now(timezone.utc).isoformat()}")
    print("="*60)
    
    results = []
    
    r1 = write_aishwarya_jw_marriott()
    results.append(("Aishwarya Rai × JW Marriott", r1))
    time.sleep(1)
    
    r2 = write_made_in_india_titan()
    results.append(("Made in India: A Titan Story", r2))
    time.sleep(1)
    
    r3 = write_hai_jawani()
    results.append(("Hai Jawani Toh Ishq Hona Hai", r3))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, result in results:
        status = "✓ Published" if result else "✗ Failed"
        print(f"  {status}: {name}")
    
    failed = sum(1 for _, r in results if not r)
    if failed:
        print(f"\n⚠ {failed} article(s) failed")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} articles published successfully")
