#!/usr/bin/env python3
"""
Sports writer — 2026-06-05 batch
Articles:
1. Indian Boxing World Rankings — Minakshi Hooda & Jaismine Lamboria at World No. 1
2. World Yogasana Championship 2026 — Modi inaugurates first-ever event in Ahmedabad
"""

import os, sys, json, uuid, requests, io, subprocess, time
from datetime import datetime, timezone
from PIL import Image

# ── env ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            line = line.replace("export ", "")
            k, v = line.split("=", 1)
            v = v.strip('"').strip("'")
            os.environ[k] = v

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS_SB = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── image helpers ────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
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
    try:
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": search_query,
            "gsrnamespace": "6",
            "gsrlimit": str(limit),
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
            "iiurlwidth": "1200",
            "format": "json"
        }
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
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        import urllib.parse
        url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3"
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}", url],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            src = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image found for '{query}': {src[:80]}...")
            return src
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P', 'LA'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def download_image(url):
    """Download image bytes from URL."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image"):
            return r.content
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None


def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage bucket 'article-images'. Returns public URL."""
    bucket = "article-images"
    upload_url = f"{SB_URL}/storage/v1/object/{bucket}/{filename}"
    headers = {
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(upload_url, data=img_bytes, headers=headers, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/{bucket}/{filename}"
        print(f"  ✓ Uploaded to Supabase: {filename} ({len(img_bytes)} bytes)")
        return public_url
    else:
        print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
        return None


def source_image(slug, person_name=None, wiki_search=None, pexels_query=None):
    """Multi-source image pipeline. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": "high"})

    # Source 2: Wikimedia Commons
    if wiki_search:
        searches = wiki_search if isinstance(wiki_search, list) else [wiki_search]
        for q in searches:
            commons = fetch_wikimedia_commons_images(q)
            for r in commons[:2]:
                candidates.append({"url": r["url"], "source": "wikimedia_commons", "relevance": "medium"})
            if candidates:
                break

    # Source 3: Pexels
    if pexels_query:
        pex = fetch_pexels_image(pexels_query)
        if pex:
            candidates.append({"url": pex, "source": "pexels", "relevance": "low"})

    # Pick best and upload
    for c in candidates:
        raw = download_image(c["url"])
        if raw and len(raw) > 5000:
            compressed = compress_image(raw)
            if len(compressed) > 10000:
                filename = f"{slug}.jpg"
                pub_url = upload_to_supabase(compressed, filename)
                if pub_url:
                    attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                    return pub_url, attr

    print(f"  ⚠ No suitable image found for {slug}")
    return None, None


# ── topic + article insertion ─────────────────────────────────────────
def create_topic(title, category):
    """Create a topic in p2_topics. Returns topic UUID."""
    cat_to_vertical = {
        "sports": "sports", "news": "politics", "entertainment": "entertainment",
        "technology": "tech", "markets-finance": "economy", "travel": "travel",
        "food": "food", "nri-world": "immigration"
    }
    topic = {
        "canonical_title": title,
        "vertical": cat_to_vertical.get(category, "sports"),
        "urgency": "daily",
        "score_total": 70,
        "score_diaspora": 70,
        "score_significance": 70,
        "score_recency": 80,
        "score_source_avail": 80,
        "signal_count": 1,
        "status": "published",
        "keywords": [],
        "category": category
    }
    url = f"{SB_URL}/rest/v1/p2_topics"
    r = requests.post(url, json=topic, headers=HEADERS_SB, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        tid = data[0]["id"] if isinstance(data, list) else data.get("id", "")
        print(f"  ✓ Topic created: {tid}")
        return tid
    else:
        print(f"  ⚠ Topic creation failed ({r.status_code}): {r.text[:200]}")
        return None


def insert_article(article):
    """Insert article into p2_articles."""
    url = f"{SB_URL}/rest/v1/p2_articles"
    r = requests.post(url, json=article, headers=HEADERS_SB, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id", "?")
        print(f"  ✓ Inserted: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ──────────────────────────────────────────────────────────────────────
# ARTICLE 1: Indian Boxing World Rankings
# ──────────────────────────────────────────────────────────────────────
def write_boxing_article():
    print("\n═══ Article 1: Indian Boxing World Rankings ═══")

    slug = "india-boxing-world-rankings-minakshi-jaismine-world-no-1-asian-games-2026-nri"

    # Image sourcing
    print("  Sourcing image...")
    img_url, img_attr = source_image(
        slug,
        person_name="Jaismine Lamboria",
        wiki_search=["Indian women boxing championship", "India boxing Asian Games", "boxing ring India women"],
        pexels_query="boxing ring women athlete competition"
    )

    headline = "Two World No. 1 Rankings. Seventeen Top-10 Finishes Across Twenty Weight Classes. Indian Boxing Has Never Been This Deep."

    subheadline = "Minakshi Hooda and Jaismine Lamboria both hold the top spot in their divisions. India now features in the top 10 of nine of ten women's and eight of ten men's weight categories."

    body = """For years, Indian boxing lived and died by the fortune of one or two individuals at a time. Mary Kom carried the sport alone for the better part of a decade. Vijender Singh's bronze in Beijing opened a door. Lovlina Borgohain's medal in Tokyo confirmed the trend was real.

But the latest World Boxing Rankings, released on Thursday, tell a different story entirely. This is no longer a one-name sport. India now has two women ranked World No. 1, top-10 boxers in nine of ten women's weight categories, and men in eight of ten divisions. The depth is unprecedented.

## The Two at the Top

Minakshi Hooda retained her World No. 1 ranking in the women's 48kg category, a position she has held since winning gold at the Asian Boxing Championships in Mongolia in March. At 48kg, the lightest Olympic weight class, she has become a fixture at the top of the rankings through consistent performances across World Boxing Cup events over the past two years.

Jaismine Lamboria climbed to No. 1 in the women's 57kg division, overtaking Poland's Julia Szeremeta following her silver medal at the Asian Championships. Jaismine, who made her mark at the 2022 Commonwealth Games in Birmingham, has steadily risen through the rankings and now leads a weight class that has historically been dominated by boxers from Kazakhstan, China, and Eastern Europe.

The rankings are based on results from major international competitions held between July 2024 and May 2026, and they will play a significant role in determining seedings for the 2026 Asian Games in Aichi-Nagoya and the upcoming Commonwealth Games.

## Depth, Not Just Headlines

What makes these rankings remarkable is not the two No. 1 spots alone but the breadth behind them.

Preeti Pawar climbed to No. 3 in the 54kg category. Priya Ghanghas, the Asian champion, achieved the same ranking at 60kg. Three Indian women — Arundhati Choudhary (70kg), Pooja Rani (80kg), and Nupur (+80kg) — are all ranked World No. 2 in their respective divisions, a sweep across the heavier weight classes that would have been unthinkable five years ago.

Established stars Nikhat Zareen (51kg) and Lovlina Borgohain (75kg) retained their places among the world's elite. Together with the newer names, they form a roster where virtually every weight class has a contender.

The men's contingent mirrors that consistency. Sachin Siwach and Narender broke into the top five following a sustained run of international success. Vishvanath Suresh, the Asian champion at 50kg, surged into the top three. Hitesh Gulia retained his No. 6 ranking at 70kg. Abhinash Jamwal sits eighth at 65kg. Akash (75kg) and Lokesh (85kg) also entered the top 10.

## What It Means for the Diaspora

For NRI fans, the implications extend beyond rankings. The 2026 Asian Games in Aichi-Nagoya, Japan, will use these standings to determine seedings. India entering with two No. 1 seeds, multiple top-three placements, and at least one contender in almost every division means a medal haul that could rival or exceed the Tokyo Olympics cycle.

Ajay Singh, the president of the Boxing Federation of India, said the rankings reflected the investments made across grassroots development, high-performance training, and talent identification systems. "It is encouraging to see that today, almost every weight category features a strong Indian presence at the global level, firmly establishing India as one of the leading boxing nations in the world," he said.

## The Pipeline Is the Point

The real shift is structural. India's boxing infrastructure now produces contenders across weight classes, genders, and age groups rather than relying on the occasional prodigy to carry the sport. The BFI's systematic development of training academies across Haryana, Assam, Manipur, and other states has created a pipeline that feeds directly into international competition.

For a sport that once celebrated a single medal as a generational achievement, having seventeen top-10 boxers across twenty weight classes is a statement of arrival. The next test comes at the Asian Games in September. The rankings suggest India will arrive not hoping for medals, but expecting them.

*Sources: Boxing Federation of India, Olympics.com, IANS*"""

    image_caption = "Jaismine Lamboria during an international boxing competition" if img_url else None

    # Create topic first
    topic_id = create_topic("Indian Boxing World Rankings: Minakshi and Jaismine at No. 1", "sports")
    if not topic_id:
        print("  ✗ Failed to create topic, skipping article")
        return None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "topic_id": topic_id,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False,
        "diaspora_angle": "For NRI fans tracking India's Olympic medal prospects, the rankings signal unprecedented depth across weight classes. With Asian Games seedings in Aichi-Nagoya determined by these standings, Indian boxers enter with two No. 1 seeds and multiple top-three placements.",
        "tags": ["boxing", "world rankings", "Minakshi Hooda", "Jaismine Lamboria", "Asian Games 2026", "Indian boxing", "Olympics"],
        "urgency": "daily",
        "sources": [
            {"name": "Boxing Federation of India", "url": "https://bfi.org.in"},
            {"name": "Olympics.com", "url": "https://olympics.com/en/sports/boxing"},
            {"name": "IANS", "url": "https://ianslive.in"}
        ],
        "word_count": len(body.split()),
        "score_total": 75,
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr,
    }

    # Remove None values
    article = {k: v for k, v in article.items() if v is not None}

    return insert_article(article)


# ──────────────────────────────────────────────────────────────────────
# ARTICLE 2: World Yogasana Championship 2026
# ──────────────────────────────────────────────────────────────────────
def write_yogasana_article():
    print("\n═══ Article 2: World Yogasana Championship 2026 ═══")

    slug = "world-yogasana-championship-2026-ahmedabad-modi-60-countries-olympic-pathway-nri"

    # Image sourcing
    print("  Sourcing image...")
    img_url, img_attr = source_image(
        slug,
        person_name=None,
        wiki_search=["Yogasana competition India", "yoga championship India international", "yoga sport competition"],
        pexels_query="yoga competition athletes stretching performance"
    )

    headline = "Sixty Countries. Four Hundred Athletes. India Just Turned Yoga Into a Competitive Sport With an Olympic Ambition."

    subheadline = "The first World Yogasana Championship opened in Ahmedabad on Thursday, with electronic scoring, six age categories, and a clear pitch for Olympic recognition."

    body = """The mat is not typically a place where medals are contested. For millennia, yoga has been understood as a private discipline — breath, posture, stillness. On Thursday, in Ahmedabad, it became something else entirely: a scored, judged, internationally contested competitive sport with more than 400 athletes from over 60 countries, electronic scoring systems, and the explicit backing of the Indian government.

Prime Minister Narendra Modi virtually inaugurated the first World Yogasana Championship at the Eka Arena, calling it "the beginning of a new phase" for yoga. "Through this championship, yogasana will gain recognition as a competitive sport," he said. "I am confident that in the future, yogasana will secure its place in international sporting events, whether in the Olympics or other multi-sport competitions."

## How It Works

The championship, running from June 4 to 8, is organised by the International Yogasana Sports Federation under the aegis of the Ministry of Youth Affairs and Sports, the Ministry of Ayush, and the Sports Authority of India. Competitors will perform across two formats — individual events and artistic events — in six age categories ranging from sub-junior (10–14 years) to senior C (45–55 years).

For the first time at the global level, an electronic scoring system is being used, a deliberate move to bring transparency and consistency to judging. "This is meant to improve transparency in marking and bring greater consistency and stronger judging standards," officials said. The framework mirrors what other non-traditional sports — rhythmic gymnastics, artistic swimming, breaking — have done to build credibility with the International Olympic Committee.

## India's 122-Member Contingent

As the host nation, India has fielded its largest yogasana contingent ever: 122 athletes across all six age categories. The size of the squad reflects years of domestic competition infrastructure that most outsiders are unaware of. National-level yogasana championships have been held in India for over a decade, with state-level qualifiers feeding into national events. The World Championship adds an international tier to a system that already has depth.

Athletes from the United States, Ghana, Kenya, Malaysia, Sri Lanka, Uzbekistan, and dozens of other nations are participating, a signal of how far the practice has spread beyond its South Asian roots. For Indian diaspora communities in the US, UK, and Canada, where yoga studios outnumber cricket clubs, the championship reframes a cultural practice they have long practiced recreationally as something competitive and internationally legitimate.

## The Olympic Question

Modi's reference to the Olympics was not casual. The International Yogasana Sports Federation has been steadily building the case for yogasana's inclusion in the Olympic program, following the pathway that sports like skateboarding, surfing, and breaking used to gain entry in recent Games.

The requirements are well-defined: an international governing body, standardised rules, anti-doping compliance, a minimum number of participating countries across multiple continents, and competitive events that can be objectively scored. Thursday's championship checked several of those boxes simultaneously — 60-plus countries, electronic scoring, official government support, and a format that can be broadcast and understood by non-practitioners.

Dr Jaideep Arya, general secretary of World Yogasana, called the championship "a defining moment in the evolution of yogasana as a global sport." Whether it reaches the Olympics within one cycle or two, the infrastructure being laid in Ahmedabad this week is designed to make the question "when," not "if."

## Why It Matters Beyond the Mat

For India, the championship serves a dual purpose. Domestically, it validates yogasana as a sporting discipline, opening doors for government funding, institutional recognition, and athlete development pathways that parallel those for cricket, badminton, and athletics.

Internationally, it positions India as the undisputed home of a sport that carries enormous cultural soft power. In a world where countries compete fiercely to own sporting narratives — South Korea with taekwondo, Japan with judo and karate, Brazil with capoeira — India has a plausible claim to do the same with yogasana.

The championship runs through June 8. By the time it ends, the medals will be the least important outcome. The real achievement will be whether 60 countries competing under standardised rules, with electronic scores and international judges, is enough to move the Olympic needle. Modi seems to think so. The athletes on the mat in Ahmedabad are betting their practice on it.

*Sources: Press Trust of India, Ministry of Youth Affairs & Sports, DevDiscourse*"""

    image_caption = "Athletes performing yogasana during a competitive event" if img_url else None

    # Create topic first
    topic_id = create_topic("World Yogasana Championship 2026 in Ahmedabad", "sports")
    if not topic_id:
        print("  ✗ Failed to create topic, skipping article")
        return None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "topic_id": topic_id,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False,
        "diaspora_angle": "For the Indian diaspora in the US, UK, and Canada — where yoga studios outnumber cricket clubs — the World Yogasana Championship reframes a cultural practice they have long practiced recreationally as an internationally competitive sport with Olympic aspirations.",
        "tags": ["yogasana", "World Yogasana Championship", "Modi", "Ahmedabad", "Olympics", "competitive yoga", "India sports"],
        "urgency": "daily",
        "sources": [
            {"name": "Press Trust of India", "url": "https://ptinews.com"},
            {"name": "Ministry of Youth Affairs & Sports", "url": "https://yas.nic.in"},
            {"name": "DevDiscourse", "url": "https://devdiscourse.com"}
        ],
        "word_count": len(body.split()),
        "score_total": 72,
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr,
    }

    article = {k: v for k, v in article.items() if v is not None}

    return insert_article(article)


# ──────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("═══ Videshi Sports Writer — 2026-06-05 ═══")
    print(f"  Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    results = []

    art1 = write_boxing_article()
    results.append(("Boxing Rankings", art1))

    art2 = write_yogasana_article()
    results.append(("Yogasana Championship", art2))

    print("\n═══ Summary ═══")
    for name, art_id in results:
        status = f"✓ {art_id}" if art_id else "✗ FAILED"
        print(f"  {name}: {status}")

    failed = sum(1 for _, r in results if r is None)
    if failed:
        print(f"\n  ⚠ {failed} article(s) failed!")
        sys.exit(1)
    else:
        print(f"\n  ✓ All {len(results)} articles published successfully!")
