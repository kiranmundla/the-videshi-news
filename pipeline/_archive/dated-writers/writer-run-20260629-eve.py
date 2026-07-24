#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-29 evening run
Two articles:
  1. Amazon raises India bet to $48B
  2. US Ambassador Gor on H-1B visa changes
"""
import os, sys, json, requests, io, subprocess, re
from datetime import datetime, timezone
from urllib.parse import quote

# ── env ──────────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            k, _, v = line.partition('=')
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY   = os.environ.get('PEXELS_API_KEY', '')
UA = "TheVideshi/1.0 (thevideshi.com)"

# ── helpers ──────────────────────────────────────────────────────────────────
def sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

def sb_insert(table, payload):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}",
                      headers=sb_headers(), json=payload, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ⚠ INSERT {table} failed {r.status_code}: {r.text[:300]}")
        return None
    data = r.json()
    return data[0] if isinstance(data, list) else data

def fetch_wikipedia_person_image(person_name):
    encoded = quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
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
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use",
}

def commons_relevance_ok(commons_title, headline, topic=""):
    title_l = (commons_title or "").lower()
    if not title_l:
        return False
    kws = set()
    for t in re.findall(r"[A-Za-z][A-Za-z'-]+", (headline or "") + " " + (topic or "")):
        tl = t.lower()
        if len(tl) >= 4 and tl not in _COMMONS_STOP:
            kws.add(tl)
    if not kws:
        return True
    return any(kw in title_l for kw in kws)

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get("https://api.pexels.com/v1/search",
                         params={"query": query, "per_page": 3, "orientation": "landscape"},
                         headers={"Authorization": PEXELS_KEY}, timeout=10)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                return photos[0]["src"]["large2x"]
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def download_image(url):
    if "wikimedia.org" in url or "wikipedia.org" in url:
        result = subprocess.run(
            ["curl", "-sS", "-A", UA, "-L", "--max-time", "30", url],
            capture_output=True)
        if result.returncode == 0 and len(result.stdout) > 5000:
            return result.stdout
        print(f"  ⚠ curl download failed for {url[:80]}")
        return None
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
    except Exception as e:
        print(f"  ⚠ download error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_image_to_supabase(jpeg_bytes, filename):
    r = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        },
        data=jpeg_bytes, timeout=60)
    if r.status_code not in (200, 201):
        print(f"  ⚠ Upload failed {r.status_code}: {r.text[:200]}")
        return None
    return f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"

def source_and_upload_image(slug, person_name=None, topic_queries=None, headline=""):
    candidates = []
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "name": person_name})
    for q in (topic_queries or []):
        commons = fetch_wikimedia_commons_images(q)
        commons = [c for c in commons if commons_relevance_ok(c.get("title", ""), headline, q)]
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "title": c.get("title","")})
        if candidates:
            break
    if not candidates and topic_queries:
        for q in topic_queries:
            pex = fetch_pexels_image(q)
            if pex:
                candidates.append({"url": pex, "source": "pexels"})
                break
    if not candidates:
        print(f"  ✗ No image found for {slug}")
        return None, None, None
    best = candidates[0]
    print(f"  → Using {best['source']}: {best['url'][:80]}...")
    raw = download_image(best["url"])
    if not raw:
        for c in candidates[1:]:
            raw = download_image(c["url"])
            if raw:
                best = c
                break
    if not raw:
        print(f"  ✗ All downloads failed for {slug}")
        return None, None, None
    compressed = compress_image(raw)
    filename = f"{slug}.jpg"
    final_url = upload_image_to_supabase(compressed, filename)
    attribution = "Wikimedia Commons" if best["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
    return final_url, attribution, best.get("name") or best.get("title", "")


# ── Article 1: Amazon $48B India Investment ──────────────────────────────────
def write_amazon_article():
    slug = "amazon-48-billion-india-investment-jassy-modi-ai-quick-commerce-20260629"
    headline = "Amazon Just Raised Its India Bet to $48 Billion. The Quick Commerce War It Triggered Is Already Drawing Blood."
    subheadline = "Andy Jassy's visit to New Delhi came with $13 billion in fresh AI and cloud commitments — and a 300-city quick commerce expansion that has wiped $15 billion off Blinkit and Swiggy's market value."

    body = """Amazon CEO Andy Jassy flew to New Delhi last week and did what American tech chiefs have been doing with increasing frequency this year: he sat down with Prime Minister Narendra Modi, praised India's trajectory, and announced a number so large it was hard to process on the first read. Amazon will invest $48 billion in India between 2026 and 2030 — up from $35 billion pledged just six months ago.

The $13 billion increase will go almost entirely toward expanding Amazon Web Services data center capacity in Mumbai and Hyderabad, giving Indian startups, enterprises, and government agencies access to custom AI chips, managed AI services, and cloud developer tools. Combined with Microsoft's $17.5 billion and Google's $15 billion, the three American hyperscalers have now committed over $80 billion to build India's AI infrastructure in the span of a single year.

"India is becoming such a significant cloud and AI hub around the world, and we have so much demand here that we're continuing to invest in the country on the cloud side and the AI side as well," Jassy said.

## The Numbers Behind the Headline

Amazon's pledge isn't just about servers. By 2030, the company says it will support 3.8 million direct and indirect jobs in India, up from 2.8 million in 2024. It has also committed to enabling $80 billion in cumulative e-commerce exports, extending AI tools to 15 million small businesses, and bringing AI education to four million government school students.

Modi called the investment a reflection of "growing interest across the world to invest in India." Amazon's cumulative India spend from 2010 to 2030 will exceed $88 billion — the largest single-company investment commitment the country has ever received from a foreign firm.

The announcement lands at a moment when India's policy environment is actively courting hyperscaler capital. Earlier this year, New Delhi introduced long-term tax breaks for global cloud providers that use India-based data centers for worldwide operations — a direct play to ensure the data center buildout benefits Indian infrastructure, not just Indian customers.

## The Quick Commerce Front

But Jassy didn't come to India just to talk about cloud. He visited one of Amazon's quick commerce warehouses — the so-called "dark stores" that power 10-minute grocery deliveries — and announced that Amazon Now, the company's ultra-fast delivery arm, would expand from roughly 15 cities to more than 300.

The move sent shockwaves through India's booming $11-billion quick commerce sector. Blinkit-parent Eternal Ltd. has slipped 28 percent from its October all-time high, while Swiggy has plunged about 47 percent from its September peak — a combined selloff of more than $15 billion. Walmart-backed Flipkart, preparing for what bankers expect will be a $60-billion IPO, has simultaneously scaled its Flipkart Minutes service to 1,000 dark stores across 130 cities, with plans to reach 1,500 soon.

"The challenge right now is that the competition is really high, so near-term profitability is depressed," said Franklin Templeton fund manager Yi Ping Liao, who holds shares in Eternal. "The risk is the duration of the competitive intensity."

Amazon is making up for a late start. While Blinkit operates over 2,200 stores and Swiggy Instamart has more than 1,100, Amazon Now has roughly 500. But Amazon's global logistics machine and its willingness to absorb losses for years give it staying power that purely Indian competitors find hard to match. The company plans to launch more than 20 new fulfillment centers and over 100 delivery stations across India this year alone.

## What This Means for the Diaspora

For NRIs invested in Indian markets, the quick commerce war is a double-edged sword. Eternal (formerly Zomato) and Swiggy were darlings of the new-economy portfolio — high-growth, India-first stories that rewarded early believers. Amazon and Flipkart's entry doesn't kill those companies, but it compresses their margins and extends the timeline to profitability that investors had priced in.

On the other side of the ledger, the hyperscaler buildout is creating a new generation of high-paying AI and cloud jobs in India's tier-one cities. AWS alone plans to expand its India engineering teams significantly, and the downstream effect on the Indian startup ecosystem — where access to cheap, local compute power can determine whether a product scales — is potentially transformative.

India's tech sector absorbed about $7.7 billion in net foreign direct investment in the year ended March 2026, well behind Vietnam and Indonesia. The hyperscaler wave could change that equation dramatically — if the jobs, the data, and the intellectual property stay in India rather than passing through it."""

    image_caption = "Amazon CEO Andy Jassy meets Prime Minister Narendra Modi in New Delhi to discuss the company's expanded India investment"
    diaspora_angle = "NRIs invested in Indian quick commerce stocks face margin compression, while the $80B+ hyperscaler buildout creates high-paying AI jobs and transforms the Indian startup ecosystem"

    sources = json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Barron's", "url": "https://www.barrons.com"},
        {"name": "The Wall Street Journal", "url": "https://www.wsj.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
        {"name": "CNBC TV18", "url": "https://www.cnbctv18.com"}
    ])

    print("\n=== Article 1: Amazon $48B India Investment ===")
    img_url, img_attr, _ = source_and_upload_image(
        slug,
        person_name="Andy Jassy",
        topic_queries=["Andy Jassy Amazon CEO", "Amazon India data center", "Amazon Web Services cloud"],
        headline=headline
    )

    payload = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "sources": sources,
        "diaspora_angle": diaspora_angle,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    if img_url:
        payload["image_url"] = img_url
        payload["image_caption"] = image_caption
        payload["image_attribution"] = img_attr

    result = sb_insert("p2_articles", payload)
    if result:
        print(f"  ✓ Article 1 inserted: {result.get('id', '?')}")
    return result


# ── Article 2: US Ambassador Gor on H-1B ─────────────────────────────────────
def write_gor_article():
    slug = "us-ambassador-sergio-gor-h1b-visa-not-targeted-india-rubio-trade-deal-20260629"
    headline = "America's New Ambassador to India Says the Visa Crackdown Isn't About India. Here's What He's Not Saying."
    subheadline = "Sergio Gor insists H-1B reforms are part of a 'broader overhaul,' not targeted at Indians. But a new wage-based selection system could shut out the entry-level workers who built Silicon Valley's outsourcing pipeline."

    body = """Sergio Gor had been America's ambassador to India for barely a month when he sat down for his first major interview and said the thing every Indian professional in the United States needed to hear — and the thing many of them no longer believe.

"I don't think the big item to remember on that is this is not targeted at India," Gor told IANS at the White House on Friday, addressing the wave of anxiety that has gripped Indians in the U.S. since the Trump administration began overhauling the country's immigration system earlier this year. "The United States, we had to take stock of the whole immigration system, every kind of visa. Unfortunately, under previous administrations, our borders were wide open. That's something the President wanted to fix on day one."

## The Official Line

Gor, a longtime Trump loyalist who was sworn in as ambassador after being confirmed by the Senate, struck a reassuring tone throughout the interview. He pointed to the scale of U.S. visa operations in India — "our embassy is one of the busiest embassies in the world as it relates to visas" — as proof that people-to-people ties remain strong.

He drew a parallel between Trump's immigration stance and Modi's own rhetoric. "It's actually something the Prime Minister relates to," Gor said. "When I listen to the Prime Minister speaking in India, he talks about no illegal migrants. We hundred per cent agree with that."

Secretary of State Marco Rubio, in a separate interview the same day, was even more effusive. "We're enormous fans of Prime Minister Modi and what he's done," Rubio said. "He leads a country that's making incredible gains economically. And it's really coming into its own, as sort of a global power."

Rubio also confirmed that Washington is planning a Trump visit to India "in the early parts of next year" and that a trade deal is in its final stages. "We're on the last inches of getting it done," he said.

## What the Reassurance Doesn't Cover

The ambassador's framing — that visa changes are systemic, not country-specific — is technically accurate. But it glosses over the fact that Indians are, by an enormous margin, the single largest group affected by every H-1B policy change.

Indian nationals received roughly 72 percent of all H-1B visas approved in the most recent fiscal year. They account for the vast majority of the 1.8 million people stuck in the employment-based green card backlog, with some facing estimated wait times of over 100 years.

The most consequential change Gor did not address in detail is the shift from a random lottery to a wage-based selection system for cap-subject H-1B visas beginning in fiscal year 2027. Under the new rules, applications tied to higher-paying positions will be prioritized. Entry-level jobs — the kind that Indian IT services companies use to place hundreds of thousands of workers at client sites across America — will be deprioritized.

For companies like Infosys, TCS, and Wipro, which built their business models on placing mid-level Indian engineers at competitive (but not top-tier) salaries, the wage-based system is an existential threat to their U.S. staffing pipeline. For the individual workers, it means the path from campus hire in Bangalore to H-1B holder in California just got steeper.

## The Trade Deal Backdrop

The diplomatic warmth around Gor's appointment and Rubio's praise for Modi are inseparable from the trade negotiations that both sides describe as imminent. India and the U.S. agreed in February to an 18 percent tariff framework on Indian goods — lower than what was imposed on Vietnam or Bangladesh — in exchange for India lowering trade barriers and buying more American products.

Commerce Minister Piyush Goyal said last week that the two countries are "very close" to finalizing the deal, though the U.S. Section 301 investigation into alleged overcapacity and forced labor continues to hang over the talks.

For the Indian diaspora, the trade deal and the immigration overhaul are two sides of the same coin. A deal that opens markets but restricts the movement of the people who run those markets will feel hollow. The four million Indian Americans who vote, pay taxes, and start businesses in the United States are not a trade commodity to be negotiated over — they are the relationship.

## The View From India

Gor's reassurance will play well in New Delhi's diplomatic corridors, where the priority is maintaining the broader strategic partnership. But in the waiting rooms of U.S. consulates across India — where visa interviews are being delayed, denied, or subjected to administrative processing at higher rates than in recent memory — the ambassador's words will be measured against experience.

The trade deal may come. The Trump visit may happen. But for the Indian engineer in Hyderabad waiting six months for a visa appointment, or the Indian-American family watching their green card priority date crawl forward by weeks over a span of years, the question isn't whether the crackdown is "targeted" at India. The question is whether it matters that it isn't."""

    image_caption = "U.S. Ambassador to India Sergio Gor at the White House"
    diaspora_angle = "Indians are 72% of H-1B recipients and dominate the green card backlog — the shift to wage-based selection could reshape the pathway that brought millions of Indian professionals to America"

    sources = json.dumps([
        {"name": "IANS", "url": "https://ianslive.in"},
        {"name": "Outlook Business", "url": "https://outlookbusiness.com"},
        {"name": "Times Now", "url": "https://www.timesnow.com"},
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "India Today", "url": "https://www.indiatoday.in"}
    ])

    print("\n=== Article 2: US Ambassador Gor on H-1B ===")
    img_url, img_attr, _ = source_and_upload_image(
        slug,
        person_name="Sergio Gor",
        topic_queries=["Sergio Gor US ambassador", "US Embassy New Delhi India", "H-1B visa United States passport"],
        headline=headline
    )

    payload = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "sources": sources,
        "diaspora_angle": diaspora_angle,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    if img_url:
        payload["image_url"] = img_url
        payload["image_caption"] = image_caption
        payload["image_attribution"] = img_attr

    result = sb_insert("p2_articles", payload)
    if result:
        print(f"  ✓ Article 2 inserted: {result.get('id', '?')}")
    return result


# ── main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Videshi Writer Run — {datetime.now(timezone.utc).isoformat()}")
    a1 = write_amazon_article()
    a2 = write_gor_article()
    print("\n=== Summary ===")
    print(f"  Article 1 (Amazon $48B): {'OK ' + str(a1.get('id','?')) if a1 else 'FAILED'}")
    print(f"  Article 2 (Gor H-1B):    {'OK ' + str(a2.get('id','?')) if a2 else 'FAILED'}")
