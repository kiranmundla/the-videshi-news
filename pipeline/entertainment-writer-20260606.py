#!/usr/bin/env python3
"""Entertainment writer for The Videshi - June 6, 2026 batch"""
import requests
import json
import os
import urllib.parse
import subprocess
import time
import uuid
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

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
            # Prefer thumbnail (330px, reliable), fall back to originalimage
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
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
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
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
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Fetch image from Pexels using curl (Python requests gets 403)."""
    try:
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def validate_image(url):
    """Validate that URL returns a real image >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD, try GET
        if "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                             headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except:
        pass
    return False

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('headline', '')[:60]}...")
            return True
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return False


# ============================================================
# ARTICLE 1: Hai Jawani Toh Ishq Hona Hai Day 1
# ============================================================
def write_article_1():
    print("\n=== Article 1: Hai Jawani Toh Ishq Hona Hai ===")
    
    # Image sourcing: Varun Dhawan
    img_url = None
    img_caption = ""
    img_attribution = ""
    
    # Try Wikipedia for Varun Dhawan
    wiki_img = fetch_wikipedia_person_image("Varun Dhawan")
    if wiki_img and validate_image(wiki_img):
        img_url = wiki_img
        img_caption = "Varun Dhawan at a promotional event"
        img_attribution = "Wikimedia Commons"
    
    # Try Wikimedia Commons
    if not img_url:
        commons = fetch_wikimedia_commons_images("Varun Dhawan actor Bollywood")
        for c in commons:
            if validate_image(c["url"]):
                img_url = c["url"]
                img_caption = "Varun Dhawan at a film event"
                img_attribution = "Wikimedia Commons"
                break
    
    # Try David Dhawan
    if not img_url:
        wiki_img2 = fetch_wikipedia_person_image("David Dhawan")
        if wiki_img2 and validate_image(wiki_img2):
            img_url = wiki_img2
            img_caption = "David Dhawan, veteran comedy director"
            img_attribution = "Wikimedia Commons"
    
    # Pexels fallback
    if not img_url:
        pexels = fetch_pexels_image("Bollywood comedy film theatre")
        if pexels and validate_image(pexels):
            img_url = pexels
            img_caption = "A cinema hall screening a Bollywood film"
            img_attribution = "Pexels"
    
    if not img_url:
        print("  ✗ No valid image found, skipping article")
        return False
    
    body = """David Dhawan has directed his last film. Whether or not *Hai Jawani Toh Ishq Hona Hai* becomes a box office success, it marks the end of a directorial career that gave Hindi cinema some of its most unapologetically entertaining comedies — from *Coolie No. 1* and *Hero No. 1* to *Biwi No. 1* and the original *Partner*.

The film, which opened in theatres on June 5, collected an estimated ₹7.5 to ₹8.5 crore on its first day, according to early trade estimates from Bollywood Hungama and Sacnilk. It managed around ₹4.25 crore from PVRInox and Cinepolis alone, with single screens and non-national chains contributing a higher-than-expected share. For a comedy without a massive pre-release campaign, those numbers represent a solid, if not spectacular, start.

Varun Dhawan, who stars alongside Mrunal Thakur and Pooja Hegde, is back in the territory his father made him for — loud, colourful, unabashedly mass entertainers. The supporting cast is stacked: Jimmy Shergill, Mouni Roy, Rakesh Bedi, Chunky Pandey, and Maniesh Paul. Trade analyst Taran Adarsh gave the film 3.5 stars, calling it a "fun-filled entertainer" driven by Varun's energy. Sumit Kadel called it a "paisa vasool entertainer" that "delivers exactly what it promises — laughter, romance, music, confusion and unlimited fun."

Not everyone agrees. India Today's review argued the film "mistakes loud volume for genuine humour" and described it as "a desperate attempt to recreate a very specific kind of 90s Bollywood hero: part Salman Khan, part Govinda, and entirely fabricated." The film also faced a pre-release legal tussle when producer Vashu Bhagnani challenged the use of songs 'Chunari Chunari' and 'Ishq Sona Hai' from *Biwi No. 1*, though Tips Films maintained they hold the rights.

The critical divide speaks to a larger question about what still works in Bollywood comedy. David Dhawan's formula — mistaken identities, romantic confusion, ensemble chaos — was the dominant mode of Hindi commercial cinema through the 1990s and early 2000s. It made household names of Govinda and Salman Khan in a register that was neither art-house nor action blockbuster. Whether that formula can still draw audiences in 2026, when the Hindi belt is increasingly saturated with thrillers and spectacle-driven tentpoles, is what this opening weekend will test.

For the Indian diaspora, the film carries a particular kind of nostalgia. David Dhawan comedies were a staple of weekend VHS and DVD rentals in NRI households across the US, UK, and Canada. Films like *Judwaa*, *Haseena Maan Jaayegi*, and *No. 1 Punjabi* were family-viewing defaults at a time when Indian content abroad was limited to whatever the local video store stocked. The announcement that this is his final directorial outing adds a bittersweet layer to the experience.

The film needs to hit approximately ₹70 crore in India to break even, a target that is achievable if the weekend delivers a meaningful jump. Advance bookings for Saturday and Sunday look healthy, and family audiences are expected to come in larger numbers over the weekend. The real test arrives on Monday, when weekday collections will determine whether word-of-mouth is strong enough to sustain a long theatrical run.

*Hai Jawani Toh Ishq Hona Hai* opened alongside Ram Charan's *Peddi*, which has already crossed ₹96 crore net in India after two days, and Bobby Deol's *Bandar*, which collected just ₹30 lakh on its opening day despite positive reviews. In a month where nine major releases are competing across four Fridays for screen space, the margins are thin and the stakes are real.

David Dhawan is not reinventing anything with this film. He is doing exactly what he has always done — delivering a two-and-a-half-hour escape built on comic timing, catchy music, and the belief that audiences will always show up for a good laugh. Whether they still do, in the numbers that matter, is the question this weekend will answer."""

    article = {
        "headline": "David Dhawan Has Directed His Last Film. Hai Jawani Toh Ishq Hona Hai Collected ₹8 Crore on Day One.",
        "subheadline": "Varun Dhawan's comedy opened solidly but not spectacularly in a week dominated by Peddi. The real test begins this weekend.",
        "body": body,
        "slug": "hai-jawani-toh-ishq-hona-hai-david-dhawan-last-film-day-1-box-office-nri-20260606",
        "category": "entertainment",
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Bollywood Hungama", "Sacnilk", "India Today", "Pinkvilla"]),
        "is_editorial": False,
        "vertical": "entertainment"
    }
    
    return insert_article(article)


# ============================================================
# ARTICLE 2: Gullak Season 5
# ============================================================
def write_article_2():
    print("\n=== Article 2: Gullak Season 5 ===")
    
    img_url = None
    img_caption = ""
    img_attribution = ""
    
    # Try Wikimedia Commons for Gullak or TVF
    commons = fetch_wikimedia_commons_images("Gullak TV series India")
    for c in commons:
        if validate_image(c["url"]):
            img_url = c["url"]
            img_caption = "A scene from Gullak, TVF's beloved family drama"
            img_attribution = "Wikimedia Commons"
            break
    
    # Try Jameel Khan (lead actor)
    if not img_url:
        wiki_img = fetch_wikipedia_person_image("Jameel Khan (actor)")
        if wiki_img and validate_image(wiki_img):
            img_url = wiki_img
            img_caption = "Jameel Khan, who plays Santosh Mishra in Gullak"
            img_attribution = "Wikimedia Commons"
    
    if not img_url:
        commons2 = fetch_wikimedia_commons_images("Indian middle class family home")
        for c in commons2:
            if validate_image(c["url"]):
                img_url = c["url"]
                img_caption = "A middle-class Indian household, the world Gullak inhabits"
                img_attribution = "Wikimedia Commons"
                break
    
    if not img_url:
        pexels = fetch_pexels_image("Indian family watching television home")
        if pexels and validate_image(pexels):
            img_url = pexels
            img_caption = "An Indian family at home, the kind of world Gullak brings to screen"
            img_attribution = "Pexels"
    
    if not img_url:
        print("  ✗ No valid image found, skipping article")
        return False
    
    body = """Five seasons in, Gullak still feels like walking into a house you grew up in. The furniture is rearranged — literally, this time, as Santosh Mishra applies for a housing loan to renovate the family home — but the warmth is exactly where you left it.

The fifth season of TVF's quiet masterpiece premiered on SonyLIV on June 5, and the reviews are in. Filmfare called it "a warm return to the Mishra household." India Forums gave it 3 out of 5 stars, noting that "the familiarity remains one of the show's biggest strengths — ironically, it is also becoming one of its biggest challenges." MensXP's reviewer admitted to being left "emotional, teary-eyed, and deeply satisfied" by the finale. The consensus is clear: Gullak has not lost its soul, even as it navigates the inevitable growing pains of a long-running series.

The biggest question hanging over this season was the recasting of Annu Bhaiya. Vaibhav Raj Gupta, who played the elder Mishra son across four seasons, has been replaced by Anant V. Joshi, known for *12th Fail* and *Maamla Legal Hai*. The decision sparked genuine anxiety among the show's devoted fanbase. But the reviews are unanimous: Joshi earns his place. Rather than imitating Gupta, he brings a fresh interpretation while retaining the character's defining traits — the quiet frustration, the restrained anger, the weight of being the responsible elder sibling. His chemistry with Harsh Mayar's Aman feels organic, and by the second episode, the recasting stops being a distraction.

Jameel Khan and Geetanjali Kulkarni remain the show's emotional anchors. Khan's Santosh Mishra — the government employee navigating financial anxieties with quiet dignity — is one of Indian streaming's most achingly real characters. Kulkarni's Shanti is sharper than ever this season, exploring what happens when a woman who has spent decades as the family's emotional anchor starts questioning her own identity. Sunita Rajwar's Bittu Ki Mummy gets a notable upgrade too: the nosy neighbour has discovered social media and reinvented herself as a content creator, a subplot that lands its comedy without sacrificing the character's depth.

New additions include Gopal Dutt as Pinky Mama, Shanti's visiting brother who brings chaos to the Mishra household, and Helly Shah as Dr. Preeti, whose romantic track with Annu hints at possibilities for future seasons. The writing, by Vidit Tripathi, remains the show's backbone — rooted in specificity, unafraid of silence, and trusting the audience to find meaning in the smallest domestic exchanges.

What makes Gullak essential viewing for the Indian diaspora is precisely what makes it difficult to describe to anyone who hasn't watched it. It is not plot-driven. There are no twists, no cliffhangers, no manufactured drama. It is a show about a lower-middle-class family in a small Indian town living their lives — worrying about money, arguing about dinner, navigating the gap between what they can afford and what they aspire to. For NRIs who grew up in similar households before moving to the US, UK, or Canada, each episode is a minor act of time travel. The dialogue rhythms, the family dynamics, the specific texture of an Indian home where nothing dramatic happens but everything matters — it is all there, rendered with a precision that big-budget productions rarely achieve.

Season 5 grapples with contemporary concerns — hustle culture, social media validation, the anxieties of ageing parents watching their children face a world more uncertain than the one they navigated — without ever losing its grounding. The ending, some reviewers note, wraps up a little too neatly. But in a streaming landscape dominated by darkness and spectacle, Gullak's insistence on gentleness is itself a kind of defiance.

All eight episodes are streaming now on SonyLIV, which is available internationally."""

    article = {
        "headline": "Gullak Season 5 Is Now Streaming. The Mishra Family Still Feels Like Home.",
        "subheadline": "TVF's beloved slice-of-life drama returns on SonyLIV with a new Annu Bhaiya, a housing loan, and the same quiet emotional precision that made it a modern classic.",
        "body": body,
        "slug": "gullak-season-5-sonyliv-review-tvf-mishra-family-anant-joshi-nri-20260606",
        "category": "entertainment",
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Filmfare", "India Forums", "MensXP", "Bollywood Shaadis", "Indian Community"]),
        "is_editorial": False,
        "vertical": "entertainment"
    }
    
    return insert_article(article)


# ============================================================
# ARTICLE 3: Anushka Sharma Homeopathy Controversy
# ============================================================
def write_article_3():
    print("\n=== Article 3: Anushka Sharma Homeopathy Controversy ===")
    
    img_url = None
    img_caption = ""
    img_attribution = ""
    
    # Try Wikipedia for Anushka Sharma
    wiki_img = fetch_wikipedia_person_image("Anushka Sharma")
    if wiki_img and validate_image(wiki_img):
        img_url = wiki_img
        img_caption = "Anushka Sharma at a public event"
        img_attribution = "Wikimedia Commons"
    
    if not img_url:
        commons = fetch_wikimedia_commons_images("Anushka Sharma actress")
        for c in commons:
            if validate_image(c["url"]):
                img_url = c["url"]
                img_caption = "Anushka Sharma at an industry event"
                img_attribution = "Wikimedia Commons"
                break
    
    if not img_url:
        print("  ✗ No valid image found, skipping article")
        return False
    
    body = """Anushka Sharma shared a video about homeopathy on her Instagram Story. Within hours, a hepatologist had called her an "illiterate celeb," a doctor had labeled the entire exchange a "triangle of shame," and the internet had split into camps with the ferocity usually reserved for cricket rivalries.

The sequence of events is straightforward. On June 3, Sharma reposted a video featuring homeopathic physician Rajan Sankaran in conversation with Shark Tank India judge Namita Thapar. She wrote: "Homeopathy has played an important role in my life, and Dr. Rajan Sankaran has been a key part of that journey. I deeply value his insights on health and mindful living." In the video, Sankaran argued for integrated medicine, stating that "homeopathy doesn't treat conditions, it treats people" and that modern medical practitioners sometimes refer patients for homeopathic treatment for conditions like multiple sclerosis and eczema.

Cyriac Abby Philips — the hepatologist known online as The Liver Doc and a persistent critic of alternative medicine — responded with a post calling Sharma, Sankaran, and Thapar a "triangle of shame" and describing them as "Supplement Seller – Legalized Quack – Illiterate Celeb." He wrote: "Homeopathy is 'medicine' made of water, alcohol, and sugar. So you're paying premium prices for fancy sugar pills containing precisely no medicine at all." The response was blunt, medically pointed, and — in several places — personally insulting.

The backlash against Sharma was swift but not one-sided. Many social media users echoed Philips's concerns, arguing that a celebrity with over 60 million followers endorsing a system whose core claims remain scientifically unverified is irresponsible, particularly when her audience includes people who may lack access to evidence-based healthcare. "She is getting the best medical treatment available while promoting sugar pills to millions," one widely shared post read. Others pointed out that Sharma's post came a day after she visited the ashram of Vrindavan-based Sant Premanand Maharaj with Virat Kohli, framing it as part of a broader pattern of wellness endorsements.

But a significant portion of the Indian internet pushed back against the criticism. Homeopathy occupies a unique position in Indian healthcare — it is a legally recognized system of medicine in the country, taught in accredited colleges, and practiced by hundreds of thousands of registered practitioners. For many Indian families, homeopathy is not an alternative; it is the default first response for chronic conditions, childhood ailments, and allergies. Multiple users shared their own positive experiences and questioned why Philips's critique relied on personal attacks rather than measured scientific disagreement.

For the diaspora, this debate touches something more layered than a simple science-versus-pseudoscience binary. Many NRIs in the US, UK, and Canada grew up in households where homeopathic remedies sat alongside allopathic prescriptions. Moving to countries where homeopathy is either unavailable, unregulated, or actively dismissed by the medical establishment creates a specific kind of dissonance. The attachment to these practices is often less about rejecting modern medicine and more about maintaining a connection to familial healthcare traditions — the small white pills from a neighbourhood practitioner who knew your family's medical history across generations.

None of which excuses the responsibility that comes with Sharma's platform. The central criticism — that a public figure with her reach should exercise caution when endorsing a medical system whose foundational claims are not supported by robust clinical evidence — is legitimate and important, regardless of how intemperately it was made.

The episode also raises questions about India's regulatory framework. Homeopathy is governed by the Central Council of Homoeopathy and the Ministry of AYUSH, which gives it institutional legitimacy even as the global scientific consensus remains skeptical. This regulatory position means that Indian celebrities endorsing homeopathy are not, strictly speaking, promoting an unregulated practice — even if the evidence base remains contested.

Sharma has not responded to the backlash. The original Instagram Story has since expired. The debate, as always with these cycles, will move on. But the underlying tension — between evidence-based medicine and traditional practice, between celebrity influence and personal choice, between the healthcare systems people grew up with and the ones they now live under — is not going anywhere."""

    article = {
        "headline": "Anushka Sharma Endorsed Homeopathy. A Doctor Called Her an 'Illiterate Celeb.' The Internet Did the Rest.",
        "subheadline": "A routine Instagram Story about a homeopathic physician turned into a full-blown debate about celebrity influence, medical evidence, and the healthcare traditions NRI families carry across borders.",
        "body": body,
        "slug": "anushka-sharma-homeopathy-controversy-liver-doc-cyriac-philips-celebrity-health-nri-20260606",
        "category": "entertainment",
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Livemint", "Zoom TV", "Bollywood Hungama", "NewsPoint", "Indian Witness"]),
        "is_editorial": False,
        "vertical": "entertainment"
    }
    
    return insert_article(article)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print(f"Entertainment writer starting at {datetime.now(timezone.utc).isoformat()}")
    print(f"Supabase URL: {SUPABASE_URL[:30]}..." if SUPABASE_URL else "ERROR: No SUPABASE_URL")
    
    results = []
    results.append(("Hai Jawani Toh Ishq Hona Hai", write_article_1()))
    results.append(("Gullak Season 5", write_article_2()))
    results.append(("Anushka Sharma Homeopathy", write_article_3()))
    
    print("\n=== Summary ===")
    for title, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {title}")
    
    published = sum(1 for _, s in results if s)
    print(f"\nPublished: {published}/{len(results)} articles")
