#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-10 batch
3 articles: Modi-Trump G7, DOJ Denaturalization, ISRO LVM3 Tech Transfer
"""

import os, json, uuid, time, re, io, sys
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── Image helpers ──

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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
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
                })
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for a specific image. Uses curl internally."""
    import subprocess
    try:
        result = subprocess.run([
            'curl', '-sS', '-H', f'Authorization: {PEXELS_API_KEY}',
            f'https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3'
        ], capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            url = photos[0]['src']['large2x']
            print(f"  ✓ Pexels: found for '{query}'")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
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

def download_image(url):
    """Download image bytes from URL with retry on 429."""
    for attempt in range(3):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
            if r.status_code == 200 and len(r.content) > 5000:
                ct = r.headers.get('Content-Type', '')
                if 'image' in ct or len(r.content) > 10000:
                    return r.content
            if r.status_code == 429:
                wait = (attempt + 1) * 3
                print(f"  ⚠ Rate limited (429), waiting {wait}s...")
                time.sleep(wait)
                continue
            print(f"  ⚠ Image download failed: status={r.status_code}, size={len(r.content)}")
            return None
        except Exception as e:
            print(f"  ⚠ Image download error: {e}")
            return None
    return None

def upload_to_supabase(img_bytes, filename):
    """Upload compressed image to Supabase storage bucket 'article-images'."""
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {filename} ({len(img_bytes)} bytes)")
        return public_url
    else:
        print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
        return None

def source_image(person_name=None, topic_queries=None, pexels_query=None, slug="article"):
    """Multi-source image sourcing. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "priority": 1})

    # Source 2: Wikimedia Commons
    if topic_queries:
        for q in (topic_queries if isinstance(topic_queries, list) else [topic_queries]):
            commons = fetch_wikimedia_commons_images(q)
            for c in commons[:2]:
                candidates.append({"url": c["url"], "source": "wikimedia_commons", "priority": 2})

    # Source 3: Pexels (only for non-person topics)
    if pexels_query and not person_name:
        pexels_img = fetch_pexels_image(pexels_query)
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels", "priority": 3})

    # Pick best and upload
    candidates.sort(key=lambda x: x["priority"])
    for cand in candidates:
        print(f"  Trying {cand['source']}: {cand['url'][:80]}...")
        raw = download_image(cand["url"])
        if raw:
            compressed = compress_image(raw)
            if len(compressed) > 5000:
                filename = f"{slug}.jpg"
                final_url = upload_to_supabase(compressed, filename)
                if final_url:
                    attr = "Wikimedia Commons" if cand["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                    return final_url, attr
    print("  ⚠ No valid image found for this article")
    return None, None

def insert_article(article):
    """Insert article into Supabase p2_articles."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS_SB, json=article, timeout=15)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Article inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ── ARTICLE 1: Modi-Trump Bilateral at G7 ──

def write_article_1():
    print("\n═══ ARTICLE 1: Modi-Trump G7 Bilateral ═══")

    slug = "modi-trump-bilateral-g7-france-trade-visas-h1b-energy-20260610"
    headline = "Modi and Trump Will Sit Down at the G7 Next Week. Here Is What Every NRI Should Watch For."
    subheadline = "Trade, H-1B visas and energy cooperation top the agenda as the two leaders prepare for their first face-to-face meeting in over a year"

    body = """Prime Minister Narendra Modi and U.S. President Donald Trump are expected to hold bilateral talks on the sidelines of the G7 summit in Évian-les-Bains, France, next week — their first in-person meeting since February 2025. For the millions of Indians living and working in the United States, this is not just another diplomatic photo-op. The conversation will shape policy on trade, visas and energy for months to come.

An Indian government source confirmed that H-1B visas, bilateral trade and energy cooperation will be at the top of the agenda. The timing is significant: a federal judge in Massachusetts struck down Trump's $100,000 H-1B fee just this week, and Congress is already moving to codify it through legislation. Modi is expected to raise the visa issue directly, pushing back against measures that disproportionately affect Indian technology workers who account for over 70 percent of all H-1B approvals.

## A Relationship Under Strain

The Modi-Trump dynamic has navigated turbulence over the past year. Washington imposed tariffs on Indian goods and launched Section 301 investigations alleging overcapacity in Indian textiles and steel — charges New Delhi flatly rejects. Trump has also repeatedly claimed credit for intervening in India's brief 2025 conflict with Pakistan, a narrative that New Delhi has publicly denied.

U.S. Secretary of State Marco Rubio's visit to India last month helped ease some of the tension. The two sides discussed maritime security, Middle East energy supplies and the contours of a potential trade deal. India's Trade Minister Piyush Goyal said last week that the first tranche of a bilateral trade agreement could be concluded by mid-July.

## What NRIs Should Watch

The stakes for the Indian diaspora are concrete. Washington has proposed an additional 12.5 percent tariff on imports from India, alleging forced labour — which India has rejected. If these tariffs materialise, they would hit Indian exporters and the supply chains that connect Indian-American businesses on both sides of the Pacific.

On visas, the conversation extends beyond H-1B fees. The EB-2 green card queue for Indians slammed shut this month and will not reopen until October. A direct Modi-Trump engagement on immigration could signal whether the administration is willing to consider relief for the nearly one million Indians stuck in the green card backlog.

Energy cooperation is the third pillar. With the Iran war pushing oil prices above $90 a barrel and India's balance of payments deficit ballooning, New Delhi is looking to lock in energy supplies from the United States. India's oil-and-gas import bill jumped 53 percent in April alone, and any deal to increase U.S. energy exports to India would offer relief on both sides.

## The Broader Agenda

Modi's five-day trip begins on June 13 with a stop in Nice for a bilateral meeting with French President Emmanuel Macron. He will then visit Slovakia before returning to France for the G7 sessions on June 16-17. Meetings with leaders from the UK, Germany and possibly Ukrainian President Volodymyr Zelenskyy are also on the schedule.

The G7 agenda itself will cover global partnerships, economic growth, and the governance of artificial intelligence — areas where India's technology workforce and digital infrastructure give it a distinctive voice.

For the Indian diaspora, the Modi-Trump bilateral is the headline. A productive meeting could unlock movement on trade, visas and energy. A contentious one could freeze progress for months. Either way, the outcome will be felt from Hyderabad to Houston."""

    sources = json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com"},
        {"name": "Livemint", "url": "https://www.livemint.com"},
        {"name": "Ministry of External Affairs", "url": "https://mea.gov.in"}
    ])

    # Image sourcing
    print("  Sourcing image...")
    img_url, img_attr = source_image(
        person_name="Narendra Modi",
        topic_queries=["Modi Trump bilateral summit", "G7 summit India"],
        slug=slug
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "politics",
        "status": "review",
        "is_editorial": False,
        "sources": sources,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": "Prime Minister Narendra Modi at an international summit",
        "image_attribution": img_attr or "Wikimedia Commons"
    }

    return insert_article(article)


# ── ARTICLE 2: DOJ Denaturalization / H-1B Fraud ──

def write_article_2():
    print("\n═══ ARTICLE 2: DOJ Denaturalization — H-1B Fraud ═══")

    slug = "doj-denaturalization-h1b-fraud-neeraj-sharma-magnavision-indian-citizenship-20260610"
    headline = "An Indian-Born CEO Filed Fake H-1B Petitions. Now the DOJ Wants His Citizenship Back."
    subheadline = "Neeraj Sharma is among 17 naturalized citizens targeted in the Trump administration's expanding denaturalization campaign — a warning shot for the Indian tech community"

    body = """The Department of Justice has moved to revoke the U.S. citizenship of Neeraj Sharma, an India-born businessman who ran Magnavision LLC, a New Jersey-based staffing company. The allegation: he signed and filed eleven fraudulent H-1B visa petitions, forged letters on a global financial institution's letterhead, and then lied about all of it on his citizenship application.

Sharma is one of 17 naturalized citizens targeted in the latest round of the Trump administration's denaturalization push — a legal process that was used an average of just 11 times per year between 1990 and 2017 but has accelerated sharply under the current administration.

## What the Government Alleges

According to the DOJ complaint, Sharma filed H-1B petitions claiming that foreign workers would be employed at a specific global financial institution. The petitions included letters on the institution's official letterhead bearing forged signatures of its executives. None of the represented employment arrangements were real.

When Sharma applied for naturalization in 2017, he falsely swore under penalty of perjury that he had never committed a crime for which he was not arrested, never provided false information to government officials, and never lied to gain immigration benefits. His citizenship was granted in December 2017.

Under the Immigration and Nationality Act, naturalized citizenship can be revoked if it was obtained through concealment of a material fact or willful misrepresentation. The DOJ must prove its case before a federal judge — denaturalization is a civil proceeding, not an automatic administrative action.

## The Broader Campaign

Sharma's case is part of a pattern. Homeland Security Secretary Markwayne Mullin said in a statement that "American citizenship is a privilege, and it must be earned honestly." Last year, the DOJ directed its civil rights division to "prioritize and maximally pursue denaturalization proceedings."

The 17 individuals targeted in this latest batch include people accused of offenses ranging from child sex abuse to wire fraud to drug trafficking. Sharma's case stands out because it involves H-1B fraud — a category that directly concerns the Indian tech workforce.

Between 1990 and 2017, the government averaged about 11 denaturalization cases annually. Under the current administration, that pace has accelerated dramatically. In May alone, the DOJ moved to strip citizenship from a dozen people.

## Why This Matters for Indian Americans

The Indian community is the largest beneficiary of the H-1B programme, accounting for over 70 percent of approved petitions. The overwhelming majority of Indian H-1B holders and staffing companies operate legitimately. But cases like Sharma's create a narrative that the administration can use to justify broader restrictions.

Immigration attorneys say the denaturalization push sends a clear message: fraud in visa petitions can follow you for years, even after you become a citizen. Statements made in H-1B applications, green card filings and citizenship forms can be revisited long after they were submitted.

For the estimated 2.7 million Indian Americans — many of whom navigated the H-1B-to-green-card-to-citizenship pipeline — the Sharma case is a reminder that the system demands transparency at every stage. A single misrepresentation, even one that occurred years before naturalization, can unravel the entire process.

The case is pending in federal court. Sharma has not yet been stripped of citizenship, and the government must prove its allegations before a judge. But in the current enforcement climate, the direction of travel is unmistakable."""

    sources = json.dumps([
        {"name": "Department of Justice", "url": "https://www.justice.gov"},
        {"name": "USA Today", "url": "https://www.usatoday.com"},
        {"name": "The Indian Eye", "url": "https://www.theindianeye.com"},
        {"name": "VisaVerge", "url": "https://www.visaverge.com"}
    ])

    # Image sourcing — topic-based (no person image for fraud/legal story)
    print("  Sourcing image...")
    img_url, img_attr = source_image(
        topic_queries=["United States citizenship naturalization ceremony", "US immigration visa"],
        pexels_query="US citizenship naturalization ceremony American flag",
        slug=slug
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "sources": sources,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": "A U.S. naturalization ceremony — citizenship can be revoked if obtained through fraud",
        "image_attribution": img_attr or "Pexels"
    }

    return insert_article(article)


# ── ARTICLE 3: ISRO LVM3 Tech Transfer to Private Sector ──

def write_article_3():
    print("\n═══ ARTICLE 3: ISRO LVM3 Tech Transfer ═══")

    slug = "isro-lvm3-rocket-technology-transfer-private-sector-in-space-20260610"
    headline = "ISRO Is Handing Its Biggest Rocket to the Private Sector. India's Space Economy Just Changed."
    subheadline = "IN-SPACe has invited private companies to manufacture and launch the LVM3 — the vehicle behind Chandrayaan-2 and Chandrayaan-3 — in a move that could transform India's launch capacity"

    body = """India's space programme just crossed a threshold that has been years in the making. IN-SPACe, the government body that regulates private participation in space activities, has formally invited Indian companies to acquire, manufacture and commercially operate the LVM3 — ISRO's heaviest and most capable rocket.

The LVM3, often called ISRO's "Baahubali," is the launch vehicle that carried Chandrayaan-2 and Chandrayaan-3 to the moon. It is the backbone of India's deep space ambitions. Until now, it has been exclusively built and operated by ISRO. That era is ending.

## What the Transfer Looks Like

The Expression of Interest released this week lays out a structured handover. The selected private entity — whether a single company or an industry consortium — will receive full technology transfer from ISRO, along with extensive support to absorb the manufacturing and launch processes.

ISRO will provide handholding and infrastructure support for a defined period of 42 months, or until the private entity successfully realises and launches two LVM3 vehicles, whichever comes first. After that, the company is expected to operate the rocket commercially and independently.

IN-SPACe framed the move in strategic terms: "Taking cognizance of the expanding global space economy and the strategic need to significantly scale up launch frequencies, IN-SPACe has taken the initiative for technology-transfer of LVM3 for end-to-end realisation, operation and commercialisation."

## Why It Matters

India's launch cadence has been declining. ISRO's annual launch count has lagged behind commercial demand, and several recent incidents involving the PSLV — India's workhorse rocket — have raised questions about reliability under the current model.

The global space economy, meanwhile, is accelerating. SpaceX has demonstrated that private-sector launch operations can dramatically increase frequency and lower costs. India's private space ecosystem — companies like Skyroot Aerospace, Agnikul Cosmos and the Tata-Airbus joint venture — has been growing rapidly but has been limited to smaller rockets. Handing over the LVM3 changes the scale of what Indian private companies can attempt.

Chaitanya Giri, Space Fellow at the Observer Research Foundation, called it a positive step. "We already have various private sector infrastructure and aerospace companies who play a role in making the rockets. Now with a technology transfer to such players, it will help improve the launch cadence which has been declining," he said.

## The Diaspora Connection

For the Indian diaspora in the United States, this development intersects with both professional interest and national pride. Thousands of Indian-origin engineers work at SpaceX, Blue Origin, NASA and other space organisations. India's move to commercialise its heavy-lift capability mirrors the trajectory that transformed the American space industry over the past two decades.

The transfer also has implications for India's position in the global satellite launch market. The LVM3 can place up to 4,000 kilograms into geostationary transfer orbit — a capability that, at competitive pricing, could attract commercial satellite operators who currently depend on SpaceX, Arianespace or China's Long March rockets.

Space industry executives noted that the speed of technology transfer, the frequency of subsequent launches and the cost structure will determine whether this gamble pays off. "The good part is that once the private sector kicks in, the number of launches may increase," one executive said.

The clock is ticking. With the global launch market projected to exceed $30 billion by 2030 and competitors scaling fast, India's window to capture a meaningful share depends on how quickly private players can turn ISRO's blueprints into operational rockets."""

    sources = json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
        {"name": "IN-SPACe", "url": "https://www.inspace.gov.in"},
        {"name": "Observer Research Foundation", "url": "https://www.orfonline.org"}
    ])

    # Image sourcing
    print("  Sourcing image...")
    img_url, img_attr = source_image(
        topic_queries=["ISRO LVM3 rocket launch", "GSLV Mark III India space launch vehicle"],
        pexels_query="rocket launch India space",
        slug=slug
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "sources": sources,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": "ISRO's LVM3 launch vehicle on the launchpad at Sriharikota",
        "image_attribution": img_attr or "Wikimedia Commons"
    }

    return insert_article(article)


# ── Main ──

if __name__ == "__main__":
    print("═══ Videshi News Writer — 2026-06-10 ═══")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")

    results = []
    for writer_fn in [write_article_1, write_article_2, write_article_3]:
        try:
            art_id = writer_fn()
            results.append(art_id)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append(None)

    print(f"\n═══ SUMMARY ═══")
    print(f"Articles attempted: 3")
    print(f"Articles inserted: {sum(1 for r in results if r)}")
    print(f"IDs: {results}")
