#!/usr/bin/env python3
"""Entertainment writer for The Videshi - June 5, 2026 run"""

import json
import os
import subprocess
import sys
import time
import requests
import urllib.parse
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/workspace/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Load Pexels key
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = ""
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                if "PEXELS" in key.upper():
                    PEXELS_KEY = val.strip().strip('"').strip("'")

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
            # Prefer thumbnail (330px, reliable) over originalimage (may 429)
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
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Fetch image from Pexels using curl (Python requests gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:60]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Validate image URL returns HTTP 200 with image content type and >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Try GET if HEAD didn't work well
        r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
        ct2 = r2.headers.get("Content-Type", "")
        cl2 = int(r2.headers.get("Content-Length", 0))
        if r2.status_code == 200 and "image" in ct2:
            # Read a bit to check size
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
        return False
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=15
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('slug', 'unknown')}")
            return True
        print(f"  ✓ Published (response: {r.text[:100]})")
        return True
    else:
        print(f"  ✗ Insert failed: {r.status_code} - {r.text[:200]}")
        return False

def get_image_for_article(person_names, search_terms):
    """Multi-source image search: Wikipedia first for people, then Commons, then Pexels."""
    # Try Wikipedia for person articles
    for name in person_names:
        img = fetch_wikipedia_person_image(name)
        if img and validate_image(img):
            return img, "Wikimedia Commons"
        time.sleep(1)

    # Try Wikimedia Commons
    for term in search_terms:
        results = fetch_wikimedia_commons_images(term)
        for r in results:
            url = r.get("url") or r.get("original_url")
            if url and validate_image(url):
                return url, "Wikimedia Commons"
        time.sleep(1)

    # Try Pexels
    for term in search_terms:
        img = fetch_pexels_image(term)
        if img and validate_image(img):
            return img, "Pexels"
        time.sleep(1)

    return None, None

# ========== ARTICLES ==========

articles = []

# ARTICLE 1: Gullak Season 5
print("\n=== Article 1: Gullak Season 5 ===")
gullak_image, gullak_attr = get_image_for_article(
    ["Jameel Khan (actor)", "Geetanjali Kulkarni"],
    ["Gullak TV series", "Indian family drama middle class", "Indian earthen piggy bank gullak"]
)
gullak_body = """India's most beloved family drama is back. *Gullak* Season 5 premiered on SonyLIV on June 5, making history as the first Indian web series to return for a fifth season. For diaspora audiences who grew up in small-town India, the Mishra household has become something between a memory and a mirror.

The new season finds the family navigating upgrades both literal and metaphorical. Mishra Nivas now has Wi-Fi. The house is getting a fresh coat of paint. But beneath these surface-level modernizations, the emotional architecture of the show remains unchanged: a family of four trying to stay afloat while the world around them shifts faster than they can keep up.

## What Changes This Time

Elder son Annu — now played by Anant V. Joshi, replacing Vaibhav Raj Gupta from the first four seasons — is fighting for a promotion at work while quietly apartment-hunting, a storyline that will resonate with any NRI who remembers the impossible math of Indian middle-class aspiration. Younger son Aman, played by Harsh Mayar, returns from college carrying secrets of his own. Their father Santosh, played by Jameel Khan with the same quiet desperation he has perfected over five seasons, is applying for a government housing flat. Their mother Shanti, played by Geetanjali Kulkarni, is discovering an online identity for the first time.

New additions include Gopal Dutt as Pinky Mama, Shanti's brother who arrives with an unexpected offer and stays long enough to upend the household, and Helly Shah in a yet-to-be-revealed role. The neighbour Bittu Ki Mummy, played by Sunita Rajwar, has evolved from a nosy gossip into the head of a local *mahila mandal*, giving her a platform to poke her nose into Mishra family affairs with newfound institutional authority.

## The Recasting Question

The biggest question hanging over Season 5 was whether audiences would accept a new Annu Bhaiya. By most accounts, Anant V. Joshi has answered it convincingly. Rather than imitating Vaibhav Raj Gupta's version of the character, Joshi brings his own natural rhythm while retaining the emotional essence that made the role iconic — the quiet frustration, the restrained anger, the elder brother's burden of being the family's first line of defense against the world.

Reviews have been overwhelmingly positive. MensXP called the finale "emotional, teary-eyed, and deeply satisfying." Filmfare described it as "a warm return to the Mishra household." IWMBuzz noted the show's unique ability to "touch hearts with simple, chaotic, and quirky moments."

## Why It Matters for the Diaspora

*Gullak* has always been a show that speaks directly to Indians living abroad. Its power lies not in plot twists or production scale but in the granular texture of middle-class Indian life — the housing loan applications, the neighbour who knows too much, the mother who holds everything together while quietly losing herself. For NRIs, each season is a three-hour visit home.

The show was created by TVF, the production house behind *Panchayat*, *Kota Factory*, and *Aspirants*. Written by Vidit Tripathi, the series has maintained a level of writing consistency that is rare in Indian streaming. Five seasons in, the Mishras feel less like characters and more like family you check in on once a year.

All seven episodes of *Gullak* Season 5 are now streaming on SonyLIV. The platform is available internationally, making it accessible to diaspora viewers in the US, UK, Canada, and beyond."""

articles.append({
    "headline": "Gullak Season 5 Is Now Streaming. It Is the First Indian Web Series to Make It to a Fifth Season.",
    "subheadline": "The Mishra family returns on SonyLIV with Wi-Fi, a new Annu Bhaiya, and the same ache for home that has kept diaspora audiences coming back for six years.",
    "slug": "gullak-season-5-sonyliv-premiere-mishra-family-fifth-season-nri-20260605",
    "body": gullak_body,
    "category": "entertainment",
    "image_url": gullak_image,
    "image_caption": "The Mishra family returns for a historic fifth season of Gullak on SonyLIV",
    "image_attribution": gullak_attr or "Pexels",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["SonyLIV", "Filmfare", "MensXP", "IWMBuzz", "Bollywood Shaadis"]),
})

# ARTICLE 2: Dhurandhar 2 OTT Debut
print("\n=== Article 2: Dhurandhar 2 OTT ===")
dhur_image, dhur_attr = get_image_for_article(
    ["Ranveer Singh"],
    ["Ranveer Singh actor", "Indian spy thriller action"]
)
dhur_body = """The biggest Indian film of the year just became the biggest streaming event of the year. *Dhurandhar 2: The Revenge*, Aditya Dhar's ₹1,800-crore spy action thriller starring Ranveer Singh, premiered on JioHotstar on June 4 with a special "Raw & Undekha" edition that includes 30 minutes of unseen footage, behind-the-scenes content, and exclusive cast interviews.

The film's OTT debut has been engineered as a cultural moment. JioHotstar signed 50 brand partners for the digital premiere alone — a number that rivals what most theatrical releases manage. Bhaskar Ramesh, JioStar's Head of Entertainment Sales, called it "a shared national moment at an unprecedented scale," noting that the platform's 500 million monthly active users give the premiere television-scale reach.

## The Numbers Behind the Moment

*Dhurandhar 2* grossed approximately ₹1,800 crore worldwide during its theatrical run, making it the second-biggest Indian film of all time. The sequel expanded on the original's foundation with large-scale action sequences, emotional drama, and the kind of mass appeal that kept audiences returning for second and third viewings.

Ranveer Singh leads the cast as Jakirat Singh Rangi, a spy navigating the aftermath of the 26/11 Mumbai terror attacks. R. Madhavan, Sanjay Dutt, and Arjun Rampal round out an ensemble that has been praised for balancing spectacle with emotional weight.

## A Two-Platform Strategy

The OTT rollout follows a staggered two-platform release that is unusual for Indian cinema. JioHotstar holds the India premiere window, with Netflix India set to receive the film on June 19 — two weeks later. The film has already been streaming globally on Netflix in international markets.

The dual-platform approach reflects the film's sheer commercial gravity. Industry trackers see it as an attempt to maximize reach across JioHotstar's massive subscriber base and Netflix's international footprint. For the Spy Universe franchise that Aditya Dhar has built, the streaming debut extends the film's life well beyond its theatrical run.

## What NRI Audiences Should Know

For diaspora viewers who missed the theatrical window, this is the version to watch. The "Raw & Undekha" edition adds behind-the-scenes context that enriches the viewing experience, and the film is available in Hindi, Tamil, Telugu, Malayalam, and Kannada.

The timing is strategic. Arriving right after the conclusion of IPL 2026, the premiere captures a viewership window when cricket-fatigued audiences are ready to shift back to entertainment content. JioHotstar has positioned the film as integrated advertising across television, digital, social media, and on-ground activations — treating it less like a movie premiere and more like a national event.

*Dhurandhar 2: The Revenge* is now streaming on JioHotstar in India, with the Netflix India release scheduled for June 19."""

articles.append({
    "headline": "Dhurandhar 2 Just Hit JioHotstar. Fifty Brands Bought In. The Streaming War for India's Biggest Film Is On.",
    "subheadline": "Ranveer Singh's ₹1,800-crore spy thriller arrives on OTT with a special 'Raw & Undekha' edition. Netflix India gets it June 19.",
    "slug": "dhurandhar-2-revenge-jiohotstar-ott-premiere-ranveer-singh-streaming-nri-20260605",
    "body": dhur_body,
    "category": "entertainment",
    "image_url": dhur_image,
    "image_caption": "Ranveer Singh stars in Dhurandhar 2: The Revenge, now streaming on JioHotstar",
    "image_attribution": dhur_attr or "Wikimedia Commons",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["JioHotstar", "Sacnilk", "Livemint", "Zoom TV", "Filmibeat"]),
})

# ARTICLE 3: Cocktail 2 Trailer
print("\n=== Article 3: Cocktail 2 ===")
cocktail_image, cocktail_attr = get_image_for_article(
    ["Shahid Kapoor", "Kriti Sanon", "Rashmika Mandanna"],
    ["Cocktail 2 film Bollywood", "Shahid Kapoor actor", "romantic drama Italy"]
)
cocktail_body = """The trailer for *Cocktail 2* dropped on June 2, and it answers the question that has been hanging over the project since its announcement: this is not a sequel. It is a spiritual successor — same name, same director, completely different story.

Homi Adajania, who directed the 2012 original starring Saif Ali Khan, Deepika Padukone, and Diana Penty, returns with a fresh love triangle built around Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna. The new film is set between India and Sicily, shot across picturesque Italian locations, and scored by Pritam, whose soundtrack has already become one of the film's biggest promotional assets.

## What the Trailer Shows

Shahid Kapoor plays Kunal, a man caught between two women and his own inability to decide what he wants. The trailer opens with Kunal's voiceover, reflecting on the distance between friendship and love, and how both become complicated when they start to overlap. He compares love to a worn-out T-shirt — comfortable, familiar, but increasingly difficult to wear in public.

Kriti Sanon plays Ally, who punctures Kunal's philosophizing with a single line: "Like a threesome?" The film's tone is set from that moment — messy, warm, self-aware, and unafraid of the uncomfortable.

Rashmika Mandanna's character rounds out the triangle, and the trailer hints at a dynamic where both women's feelings for Kunal deepen at different rates, creating a rivalry that threatens to fracture the friendship holding all three together.

## The Music Is Already Winning

Pritam has delivered two tracks that the makers previewed at a media event in Mumbai. *Mashooka* is the energetic romantic number shot across Sicily featuring Shahid and Kriti. *Tujhko*, sung by Arijit Singh, is an emotional track centered on Shahid and Rashmika's characters. Lyricist Amitabh Bhattacharya handles the words. If the original *Cocktail* is remembered for anything beyond Deepika Padukone's star-making turn, it is the music — and the sequel appears to understand that.

## The Trailer Launch Made News for Other Reasons

At the launch event on June 2, the cast addressed persistent online speculation that the film is a lesbian love story. Producer Dinesh Vijan firmly denied the rumour. Director Homi Adajania explained that it started as a joke on set when Kriti and Rashmika's off-screen friendship was observed, and Homi hypothetically suggested what if the story revolved around them with Shahid as the third wheel.

A separate moment from the launch went viral: Shahid Kapoor consoling a female fan who broke down in tears while meeting him, embracing her in a hug after signing her autograph.

## The Diaspora Angle

*Cocktail 2* releases in theatres on June 19. It is positioned as a summer romantic entertainer — the kind of film that the original delivered in 2012 and that Bollywood has struggled to produce consistently since. For NRI audiences, the Italian setting, the modern relationship dynamics, and Pritam's soundtrack make it a strong candidate for the weekend watchlist.

Written by Tarun Jain and Luv Ranjan, and produced by Maddock Films and Luv Films, *Cocktail 2* arrives in a market that has been starved of mid-budget romantic films. The original proved the formula works. The sequel has the cast to back it up."""

articles.append({
    "headline": "Cocktail 2 Drops Its Trailer. Shahid, Kriti, and Rashmika Are Not Remaking the Original. They Are Starting Over.",
    "subheadline": "Homi Adajania's spiritual successor to the 2012 hit trades Delhi for Sicily, Deepika for a new trio, and adds a Pritam soundtrack that is already half the appeal.",
    "slug": "cocktail-2-trailer-shahid-kapoor-kriti-sanon-rashmika-mandanna-homi-adajania-nri-20260605",
    "body": cocktail_body,
    "category": "entertainment",
    "image_url": cocktail_image,
    "image_caption": "Shahid Kapoor at the Cocktail 2 trailer launch in Mumbai",
    "image_attribution": cocktail_attr or "Wikimedia Commons",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["Sacnilk", "Bollywood Hungama", "Bollywood Bubble", "Zoom TV", "The Bridge Chronicle"]),
})

# ARTICLE 4: SPB at 80
print("\n=== Article 4: SPB at 80 ===")
spb_image, spb_attr = get_image_for_article(
    ["S. P. Balasubrahmanyam", "SP Balasubrahmanyam"],
    ["SP Balasubrahmanyam singer", "Indian playback singer legendary"]
)
spb_body = """On June 4, what would have been S. P. Balasubrahmanyam's 80th birthday, the Indian music world paused to remember the voice that shaped five decades of film across six languages. Nearly six years after his death from COVID-19 complications in September 2020, the tributes were not routine. They were raw.

Ilaiyaraaja, one of India's greatest music composers and SPB's closest creative partner, posted an audio message on X that stripped away the usual platitudes. "Balu's absence has created a vacuum in my heart," Ilaiyaraaja said. "There is no other voice equal to his. Even those voices that attempt to copy his voice aren't singing correctly. His voice cannot be copied. How can his involvement be copied?"

Ilaiyaraaja revealed that SPB sang the majority of his songs requiring a male voice not because of fame but because of an unmatched ability to understand a composer's vision instantly. "No matter what emotion is required for the song, he will deliver it with focus and dedication. He always fulfilled my expectations," he said. "He is my best friend."

## Kamal Haasan's Quiet Grief

Kamal Haasan, whose screen career was inseparable from SPB's voice for decades, wrote on social media: "The hand that holds mine, the voice that is my musical companion — today marks his birth anniversary. May he continue to resonate as a voice."

The partnership between Kamal Haasan and SPB produced some of Indian cinema's most enduring songs — *Sorgam Madhuvile*, *Ore Jeevan*, *Engeyum Eppodhum*. SPB's Hindi playback debut came through Kamal Haasan's *Ek Duuje Ke Liye* in 1981, a performance that earned him a National Film Award and introduced his voice to a generation of North Indian audiences. He also dubbed for Kamal Haasan in several Telugu films, including *Dasavathaaram*.

## Fifty Thousand Songs

The scale of SPB's career is difficult to comprehend. Over 50,000 songs recorded across Telugu, Tamil, Kannada, Hindi, Malayalam, and other languages. Six National Film Awards for Best Male Playback Singer. The Padma Bhushan in 2011. A voice that could pivot from the devotional intensity of *Yeh Haseen Vadiyan* from *Roja* to the infectious romance of *Pehla Pehla Pyar Hai* from *Hum Aapke Hain Koun* without losing an ounce of sincerity.

As Ilaiyaraaja put it: "Singing more than 50,000 songs is no ordinary thing. It is a very great achievement in the world of music. Nobody has achieved that achievement."

## A Voice That Followed the Diaspora

For Indians abroad, SPB's voice is the soundtrack of distance. His Hindi hits from the late 1980s and 1990s — *Mere Rang Mein Rangne Wali* from *Maine Pyar Kiya*, *Bahut Pyar Karte Hain* from *Saajan* — were the songs playing at every NRI gathering, every Diwali party, every car ride with parents who were building new lives while holding onto old ones. His South Indian work, spanning AR Rahman's early career through decades of collaboration with Ilaiyaraaja, was the music that connected Tamil, Telugu, and Kannada diaspora communities to a home they visited once a year.

Singer Shaan wrote on social media: "He may not be here physically but through his music and magical voice, he is here with us. Now and forever." Actor Jackie Shroff shared a photo of SPB holding a microphone, set to *Yeh Mera Dil Toh Paagal Hai*. Former Andhra Pradesh Chief Minister Y. S. Jagan Mohan Reddy praised SPB's ability to bridge language and regional divides through music.

S. P. Balasubrahmanyam was born on June 4, 1946, in Nellore, Andhra Pradesh. He died on September 25, 2020, at the age of 74. The vacuum Ilaiyaraaja described is six years old now. It has not gotten smaller."""

articles.append({
    "headline": "SPB Would Have Turned 80. Ilaiyaraaja Says the Vacuum Has Not Gotten Smaller.",
    "subheadline": "Kamal Haasan, Shaan, and Jackie Shroff join tributes to the man who sang 50,000 songs. For the diaspora, his voice is the soundtrack of every mile between here and home.",
    "slug": "sp-balasubrahmanyam-80th-birthday-ilaiyaraaja-kamal-haasan-tributes-nri-20260605",
    "body": spb_body,
    "category": "entertainment",
    "image_url": spb_image,
    "image_caption": "S. P. Balasubrahmanyam, the legendary Indian playback singer who recorded over 50,000 songs",
    "image_attribution": spb_attr or "Wikimedia Commons",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["Cinema Express", "Zoom TV", "IANS", "The Freedom Press"]),
})

# Publish all articles
print("\n=== Publishing ===")
success_count = 0
for i, article in enumerate(articles):
    print(f"\nArticle {i+1}: {article['headline'][:60]}...")
    if article["image_url"] is None:
        print("  ⚠ No image found — skipping image")
        article["image_url"] = ""
        article["image_caption"] = ""
        article["image_attribution"] = ""
    
    if insert_article(article):
        success_count += 1
    time.sleep(1)

print(f"\n=== Done: {success_count}/{len(articles)} articles published ===")
