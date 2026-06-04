#!/usr/bin/env python3
"""Entertainment Writer - June 4, 2026"""

import json, os, re, sys, uuid, requests, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    key, _, val = line.partition('=')
                    val = val.strip('"').strip("'")
                    os.environ[key.strip()] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
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

UA = "TheVideshi/1.0 (thevideshi.com)"

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
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
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and "image" in mime:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": ii.get("width", 0),
                        "height": ii.get("height", 0)
                    })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for an image."""
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
                print(f"  ✓ Pexels image found for '{query}'")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Validate that URL returns a real image > 5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if "image" in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD properly
        if "image" in ct or cl == 0:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            ct2 = r2.headers.get("Content-Type", "")
            if "image" in ct2:
                chunk = r2.raw.read(6000)
                if len(chunk) > 5000:
                    return True
    except:
        pass
    return False

def get_best_image(person_name=None, wiki_search=None, pexels_query=None):
    """Multi-source image search. Returns (url, attribution) or (None, None)."""
    candidates = []
    
    # Source 1: Wikipedia person image
    if person_name:
        img = fetch_wikipedia_person_image(person_name)
        if img and validate_image(img):
            candidates.append(("wikipedia", img, "Wikimedia Commons"))
    
    # Source 2: Wikimedia Commons
    if wiki_search:
        commons = fetch_wikimedia_commons_images(wiki_search)
        for c in commons[:3]:
            if validate_image(c["url"]):
                candidates.append(("commons", c["url"], "Wikimedia Commons"))
                break
    
    # Source 3: Pexels
    if pexels_query:
        img = fetch_pexels_image(pexels_query)
        if img and validate_image(img):
            candidates.append(("pexels", img, "Pexels"))
    
    # Prefer Wikipedia for person articles, then Commons, then Pexels
    for source_type in ["wikipedia", "commons", "pexels"]:
        for s, url, attr in candidates:
            if s == source_type:
                print(f"  → Selected {source_type} image: {url[:80]}...")
                return url, attr
    
    return None, None

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in [200, 201]:
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('headline', '')[:60]}...")
            return True
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return False

# ============================================================
# ARTICLE 1: Pahlaj Nihalani obituary
# ============================================================
def write_pahlaj_nihalani():
    print("\n📝 Article 1: Pahlaj Nihalani obituary")
    
    # Image sourcing
    img_url, img_attr = get_best_image(
        person_name="Pahlaj Nihalani",
        wiki_search="Pahlaj Nihalani film producer CBFC",
        pexels_query="Indian film industry Bollywood producer"
    )
    
    body = """Pahlaj Nihalani, the veteran film producer who introduced Govinda to Hindi cinema and later became one of India's most polarising censorship chiefs, died on Thursday morning at Mumbai's Nanavati Hospital. He was 76. His family confirmed that he had been battling liver cirrhosis for the past four months and had been moved between hospitals over the last thirty days as doctors worked to stabilise his condition.

## The Producer Who Built Careers

Nihalani entered film production in 1982 with Haathkadi and spent the next two decades backing commercially successful Hindi films. His 1986 production Ilzaam launched Govinda, then a complete unknown, into mainstream Bollywood. The following year, he introduced Chunky Pandey with Aag Hi Aag. His most significant commercial hit came with Aankhen in 1993, a film that cemented his reputation as a producer who could deliver mass entertainment.

His partnership with director David Dhawan produced a string of comedies that defined 1990s Bollywood — films that played on loop in NRI households from New Jersey to London, becoming cultural shorthand for a particular era of Hindi cinema.

## The Censor Board Years

Nihalani's appointment as chairman of the Central Board of Film Certification in January 2015 marked the beginning of a turbulent chapter. His tenure, which lasted until August 2017, was defined by an approach to censorship that drew fierce criticism from filmmakers and free-speech advocates alike.

Under his watch, the CBFC ordered cuts to films like Udta Punjab and refused certification to others. He mandated the replacement of the word "Bombay" with "Mumbai" in a Marathi film's title and demanded over 90 cuts to the adult drama Lipstick Under My Burkha, a decision that was later overturned by the Film Certification Appellate Tribunal. Directors accused him of imposing personal moral standards on Indian cinema. Nihalani defended his decisions as being in line with Indian cultural values.

The irony was not lost on the industry when Nihalani himself produced the erotic thriller Julie 2 shortly after leaving the CBFC, a film whose content sat uncomfortably next to his censorship record.

## What It Means for the Diaspora

For NRIs who grew up watching the films Nihalani produced, his death closes a chapter of Bollywood history. The Govinda comedies, the Aankhen-era popcorn films — these were the DVDs that circulated through Indian grocery stores in the United States and the UK in the 1990s and early 2000s, the films that kept a generation connected to Hindi cinema before streaming made everything accessible.

His censorship legacy is more complicated. Many diaspora viewers experienced his CBFC tenure primarily through the controversies that made international headlines — the Udta Punjab battle, the Lipstick Under My Burkha refusal — episodes that raised questions about artistic freedom in the world's largest film industry.

## Industry Reactions

IMPPA President Abhay Sinha confirmed the news, calling Nihalani an industry leader. Filmmaker Ashoke Pandit posted on Instagram, writing that Nihalani was "a man who stood by the Industry causes and somebody who is responsible for making many hit films." Current CBFC Chairperson Shashi Shekhar Vempati offered condolences on behalf of the CBFC family.

Nihalani also served as president of the Association of Motion Pictures and TV Programme Producers for 29 years before stepping down in 2009. His last rites were scheduled for Thursday afternoon at the Santacruz Hindu Crematorium in Mumbai.

He is survived by his wife Nita, who was his childhood sweetheart. The couple celebrated their 50th wedding anniversary in 2023."""

    article = {
        "headline": "Pahlaj Nihalani, the Producer Who Launched Govinda and Then Tried to Censor Bollywood, Has Died at 76",
        "subheadline": "The former CBFC chairman spent four decades shaping Hindi cinema from both sides — making the films and then deciding what audiences could see.",
        "body": body,
        "slug": "pahlaj-nihalani-death-producer-cbfc-chairman-govinda-bollywood-nri-20260604",
        "category": "entertainment",
        "vertical": "entertainment",
        "image_url": img_url or "",
        "image_caption": "Pahlaj Nihalani, veteran Bollywood producer and former CBFC chairman" if img_url else "",
        "image_attribution": img_attr or "",
        "sources": json.dumps(["Bollywood Hungama", "Exchange4Media", "IANS", "Filmibeat"]),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False
    }
    
    if not img_url:
        print("  ⚠ No image found, publishing without image")
        article.pop("image_url")
        article.pop("image_caption")
        article.pop("image_attribution")
    
    return insert_article(article)

# ============================================================
# ARTICLE 2: Dhurandhar 2 arrives on JioHotstar
# ============================================================
def write_dhurandhar_2_ott():
    print("\n📝 Article 2: Dhurandhar 2 arrives on JioHotstar")
    
    # Image sourcing
    img_url, img_attr = get_best_image(
        person_name="Ranveer Singh",
        wiki_search="Dhurandhar film Ranveer Singh",
        pexels_query="Indian spy thriller action"
    )
    
    body = """The wait is over. Dhurandhar 2: The Revenge, the spy action blockbuster that grossed ₹1,800 crore worldwide and became the second-highest-grossing Indian film of all time, started streaming on JioHotstar in India today. For NRIs in North America, the UK, and Canada who missed the theatrical run or want to watch it again, this is the one to queue up this weekend.

## The Numbers That Got Us Here

Directed by Aditya Dhar, Dhurandhar 2 opened on March 19 and spent eleven weeks in theatres, still earning over ₹30 lakh daily in its ninth week when the OTT date was finally confirmed. The film's extended theatrical window — well beyond the standard eight-week digital holdback — reflected just how much money it was still making on the big screen.

Ranveer Singh reprises his role as Jaskirat Singh Rangi, an undercover operative now known as Hamza Ali Mazari, navigating organised crime networks in Karachi while targeting terror cells linked to the 26/11 attacks. The sequel scales up the original's intimate spy thriller framework into a large-scale action spectacle, with set pieces that drew comparisons to Hollywood franchise filmmaking.

R. Madhavan, Sanjay Dutt, and Arjun Rampal round out a cast that leans into the film's ambition. A.R. Rahman's score carries the emotional weight between the action sequences.

## The Streaming Strategy

JioHotstar secured the Indian digital rights in what industry insiders describe as a premium deal, marking a platform shift from the first film, which premiered on Netflix. But the streaming strategy does not end with JioHotstar alone. Netflix India will receive the film on June 19, two weeks after the JioHotstar premiere, giving both platforms a window to capitalise on different subscriber bases.

Internationally, the film has already been available on Netflix in several markets, making it accessible to diaspora audiences who could not catch it in theatres. The staggered domestic rollout is an attempt to replicate the theatrical strategy of building sustained momentum across weeks.

## Why NRIs Should Care

Dhurandhar 2 is not just a box office story. It is a cultural event that shifted conversations about what Indian cinema can achieve at scale. The film's ₹1,800-crore worldwide haul places it in territory previously occupied only by Baahubali 2, and it did so with a Hindi-language spy franchise rather than a Telugu-origin epic.

For diaspora viewers, the film's themes — intelligence operations, cross-border conflict, national security — resonate differently when watched from abroad. The franchise has become a reference point in conversations about Indian soft power and the globalisation of Bollywood beyond the song-and-dance formula.

The JioHotstar release also means the film is now available with subtitles in multiple Indian languages — Telugu, Tamil, Kannada, and Malayalam — making it accessible to South Indian diaspora communities who may not have watched it theatrically in Hindi.

## What to Expect

The theatrical cut runs just under four hours. Reports suggest Netflix will eventually release an extended version internationally, though JioHotstar is streaming the theatrical cut for now. If you are planning a watch party, clear the evening."""

    article = {
        "headline": "Dhurandhar 2 Is Finally Streaming. India's ₹1,800-Crore Spy Blockbuster Just Landed on JioHotstar.",
        "subheadline": "The second-highest-grossing Indian film of all time arrives on OTT after eleven weeks in theatres. Netflix India gets it on June 19.",
        "body": body,
        "slug": "dhurandhar-2-the-revenge-jiohotstar-ott-release-ranveer-singh-streaming-nri-20260604",
        "category": "entertainment",
        "vertical": "entertainment",
        "image_url": img_url or "",
        "image_caption": "Ranveer Singh stars as undercover operative Jaskirat Singh Rangi in the Dhurandhar franchise" if img_url else "",
        "image_attribution": img_attr or "",
        "sources": json.dumps(["SacNilk", "Filmibeat", "JioHotstar"]),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False
    }
    
    if not img_url:
        print("  ⚠ No image found, publishing without image")
        article.pop("image_url")
        article.pop("image_caption")
        article.pop("image_attribution")
    
    return insert_article(article)

# ============================================================
# ARTICLE 3: Patriot arrives on ZEE5 — Mammootty + Mohanlal
# ============================================================
def write_patriot_zee5():
    print("\n📝 Article 3: Patriot arrives on ZEE5")
    
    # Image sourcing - try Mammootty first
    img_url, img_attr = get_best_image(
        person_name="Mammootty",
        wiki_search="Patriot Malayalam film Mammootty Mohanlal 2026",
        pexels_query=None
    )
    
    body = """Mammootty and Mohanlal sharing the screen is the kind of event that stops Malayalam cinema in its tracks. It has happened exactly once in seventeen years. Tomorrow, that film — Patriot — arrives on ZEE5, and for the millions of Malayali diaspora scattered across the Gulf, North America, and Europe, it removes the last barrier between them and the most anticipated Malayalam film of the decade.

## The Reunion That Took Seventeen Years

The last time Mammootty and Mohanlal appeared together in substantial roles was Twenty:20 in 2008, a charity film that brought together virtually every name in Malayalam cinema. Before that, their collaborations were the stuff of 1990s legend — films that defined an era when Kerala's two superstars were rivals and collaborators in equal measure.

Patriot is different. Director Mahesh Narayanan has built a spy action drama around both actors, not as cameo appearances or extended guest spots, but as full-fledged characters central to the narrative. Mammootty plays Dr. Daniel James, a scientist who stumbles onto a massive surveillance conspiracy involving a spyware programme called Periscope and a tech conglomerate named Shakthi Solutions. After leaking classified data and fleeing to London, he builds an online platform to continue exposing the network.

Mohanlal enters as Colonel Rahim Naik, a retired military officer who becomes an unlikely ally. The film's supporting cast reads like a who's who of Malayalam cinema: Fahadh Faasil, Kunchacko Boban, Nayanthara, Revathi, and Rajiv Menon.

## Why the Diaspora Angle Matters

Patriot's surveillance themes — spyware, tech companies weaponising user data, whistleblowers fleeing across borders — hit differently for NRIs working in Silicon Valley, London's tech corridor, and the Gulf's growing tech hubs. The film's premise borrows from real-world controversies around programmes like Pegasus, and its London-set narrative places Indian intelligence operations in the global context that diaspora audiences navigate daily.

The film opened theatrically on May 1 and performed strongly in Kerala and in the Middle East, where Mammootty and Mohanlal command fanatical followings. The ZEE5 release makes it available across all five South Indian languages — Malayalam, Hindi, Tamil, Telugu, and Kannada — as well as in India and international markets.

## The Verdict From Theatres

Critics praised the ambition. A three-hour spy drama that tackles surveillance, civil liberties, and state power is not typical Malayalam commercial fare, even by the standards of an industry that has spent the last five years producing some of the most adventurous cinema in India. Mammootty's performance as a man torn between patriotism and principle was singled out. Mohanlal brings gravitas to a role that is smaller in screen time but pivotal in the narrative's architecture.

Sushin Shyam's score — the composer behind the music of Bougainvillea and other recent Malayalam hits — anchors the film's emotional register. The soundtrack, including the singles Kaattu Thottappol and Manushyan, has already found a life of its own on streaming platforms.

## What to Know Before Watching

Clear three hours. Patriot is not a lean thriller. It is a dense, layered narrative that rewards patience. The film's structure moves between timelines and continents. If you are a Malayali in the diaspora, this is appointment viewing. If you are not, and you have been curious about why Malayalam cinema keeps producing the most talked-about films in India, this is as good a starting point as any.

ZEE5 begins streaming Patriot on June 5."""

    article = {
        "headline": "Patriot Arrives on ZEE5 Tomorrow. Mammootty and Mohanlal Together After Seventeen Years Is Exactly as Big as It Sounds.",
        "subheadline": "The spy drama that reunites Malayalam cinema's two greatest stars tackles surveillance, whistleblowing, and state power. The diaspora has been waiting.",
        "body": body,
        "slug": "patriot-zee5-ott-mammootty-mohanlal-fahadh-faasil-spy-drama-malayalam-nri-20260604",
        "category": "entertainment",
        "vertical": "entertainment",
        "image_url": img_url or "",
        "image_caption": "Mammootty stars as Dr. Daniel James in the spy drama Patriot" if img_url else "",
        "image_attribution": img_attr or "",
        "sources": json.dumps(["Pinkvilla", "Wikipedia", "Hollywood Reporter India", "ZEE5"]),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False
    }
    
    if not img_url:
        print("  ⚠ No image found, publishing without image")
        article.pop("image_url")
        article.pop("image_caption")
        article.pop("image_attribution")
    
    return insert_article(article)

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("🎬 Entertainment Writer — June 4, 2026")
    print("=" * 50)
    
    results = []
    results.append(("Pahlaj Nihalani obituary", write_pahlaj_nihalani()))
    results.append(("Dhurandhar 2 OTT", write_dhurandhar_2_ott()))
    results.append(("Patriot ZEE5", write_patriot_zee5()))
    
    print("\n" + "=" * 50)
    print("📊 Results:")
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {name}")
    
    succeeded = sum(1 for _, s in results if s)
    print(f"\n  {succeeded}/{len(results)} articles published")
