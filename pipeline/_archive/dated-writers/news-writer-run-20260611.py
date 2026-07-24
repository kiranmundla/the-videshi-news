#!/usr/bin/env python3
"""
Videshi News Writer — June 11 2026 run
Produces 3 articles: Hormuz closure, Dubai crash, Indian unicorn founders
"""

import os, json, sys, uuid, subprocess, time, re, io
from datetime import datetime, timezone

import requests
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
            key, _, val = line.partition("=")
            key = key.replace("export ", "").strip()
            val = val.strip().strip('"').strip("'")
            os.environ[key] = val

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── image helpers ────────────────────────────────────────────────────

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def download_image(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image"):
            if len(r.content) > 5000:
                return r.content
            print(f"  ⚠ Image too small ({len(r.content)} bytes): {url[:80]}")
    except Exception as e:
        print(f"  ⚠ Download failed: {e}")
    return None


def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage article-images bucket, return public URL."""
    compressed = compress_image(img_bytes)
    size_kb = len(compressed) / 1024
    print(f"  Compressed to {size_kb:.0f} KB")
    
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(url, headers=headers, data=compressed, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded: {public_url[:80]}...")
        return public_url
    else:
        print(f"  ✗ Upload failed ({r.status_code}): {r.text[:200]}")
        return None


def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA},
            timeout=15,
        )
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
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                })
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []


def fetch_pexels(query):
    if not PEXELS_KEY:
        return None
    try:
        r = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3&orientation=landscape"],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(r.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels: {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def source_image(slug, person_name=None, wiki_queries=None, pexels_query=None):
    """Multi-source image pipeline. Returns (public_url, attribution) or (None, None)."""
    candidates = []
    
    # 1. Wikipedia person image
    if person_name:
        img = fetch_wikipedia_person_image(person_name)
        if img:
            candidates.append({"url": img, "source": "wikipedia", "priority": 1})
    
    # 2. Wikimedia Commons
    for q in (wiki_queries or []):
        results = fetch_wikimedia_commons(q)
        for r in results[:2]:
            candidates.append({"url": r["url"], "source": "wikimedia_commons", "priority": 2})
    
    # 3. Pexels fallback
    if pexels_query:
        purl = fetch_pexels(pexels_query)
        if purl:
            candidates.append({"url": purl, "source": "pexels", "priority": 3})
    
    # Try candidates in priority order
    candidates.sort(key=lambda c: c["priority"])
    for c in candidates:
        print(f"  Trying {c['source']}: {c['url'][:80]}...")
        raw = download_image(c["url"])
        if raw:
            public_url = upload_to_supabase(raw, f"{slug}.jpg")
            if public_url:
                attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return public_url, attr
    
    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=15,
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: Iran Declares Strait of Hormuz Closed
# ═══════════════════════════════════════════════════════════════════════

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Iran Declares Strait of Hormuz Closed")
    print("="*60)
    
    slug = "iran-declares-strait-of-hormuz-closed-india-oil-crisis-gulf-diaspora-20260611"
    
    headline = "Iran Has Declared the Strait of Hormuz Closed. India Just Lost Its Most Important Oil Route."
    
    subheadline = "The first full closure of the world's most critical energy chokepoint since the 1980s threatens to push Brent crude past $100, hammers Indian markets, and puts 8 million Gulf-based Indians in an increasingly volatile region."
    
    body = """India woke up Thursday to its worst energy nightmare since the Iran war began on February 28. Iran's top joint military command declared the Strait of Hormuz closed to all vessels — oil tankers and commercial ships alike — warning that any craft attempting passage would be fired upon.

It is the first time the strait has been fully closed since the Iran–Iraq tanker wars of the 1980s.

## What Just Happened

The closure came hours after the United States launched a fresh wave of strikes against multiple Iranian targets on Wednesday evening, hitting air defences and radar installations near the strait itself. President Donald Trump had warned earlier in the day that Washington would hit Iran "very hard" if no peace deal was finalised, and Defence Secretary Pete Hegseth said strikes would continue nightly until Tehran complied.

Iran's Revolutionary Guard responded by announcing the total closure. "From this moment on, due to insecurity in the region, the Strait of Hormuz is declared closed to the traffic of any type of vessel, including oil tankers and commercial vessels, and any traffic will be affected," the Iranian military said in a statement.

The U.S. military's Central Command disputed the claim, posting on X that "commercial ships are continuing to transit in and out" of the strait. That contradiction — between Iran's declaration and America's insistence that ships are still moving — leaves the actual navigability of the waterway uncertain and dangerous.

## Why India Should Be Terrified

The Strait of Hormuz normally carries roughly one-fifth of all global oil and gas shipments. India, the world's third-largest oil importer and consumer, is acutely exposed. The country imports over 85 per cent of its crude oil, and a significant share of that supply either transits through or originates near the Persian Gulf.

Oil prices surged immediately. Brent crude climbed to $95.40 a barrel on Thursday morning, up 2.5 per cent, after already rising nearly $3 on Wednesday. Analysts at Rystad Energy warned that if full-scale hostilities resume, prices could reach $150 per barrel — a level that would devastate India's current account, force painful fuel price hikes, and accelerate the inflationary spiral that has already breached the Reserve Bank of India's 4 per cent comfort zone.

Indian equity markets opened sharply lower. The Nifty 50 fell 0.48 per cent to 23,104, while the Sensex shed 0.5 per cent. All 16 major sectors logged losses. The benchmarks have already dropped between 8 and 13 per cent since the war began, with $29 billion in foreign outflows.

## The Diaspora Dimension

Beyond oil, the closure raises acute concerns for the estimated 8 million Indians living and working in Gulf states — the largest concentration of overseas Indians anywhere in the world. The UAE alone hosts over 3.4 million Indian nationals, Saudi Arabia 2.6 million, and smaller but significant communities in Oman, Kuwait, Qatar, and Bahrain.

The escalation comes just days after seven Indian workers were killed in a road accident in Dubai and after India summoned the U.S. deputy chief of mission to lodge a "strong protest" over a U.S. military strike on an oil tanker in the Gulf of Oman that left three Indian seafarers missing. India's foreign ministry condemned the strike, saying "the targeting of commercial shipping and civilian infrastructure in the region must end."

## The Secret Oil Lifeline

In a remarkable disclosure on Wednesday, Trump revealed that the United States has been covertly extracting "millions of barrels" of Iranian oil — operations he said explain why crude has stayed near $90 rather than surging to $250. JPMorgan estimates that approximately 2.1 million barrels per day were still flowing through the strait in late May, despite the blockade, with some vessels paying tolls to Iran's newly created Persian Gulf Strait Authority and others going "dark" — switching off transponders to evade detection.

Whether those covert flows can continue after Iran's formal closure announcement remains the key question for global energy markets.

## What's Next

India's government has already been scrambling to cushion the blow. Last week, policymakers scrapped withholding and capital gains taxes on foreign government bond investments, introduced subsidised foreign currency deposit schemes for NRIs, and cut excise duty on ethanol-blended petrol. The RBI has intervened repeatedly to support the rupee, which has fallen 6 per cent this year and hit record lows.

But those are defensive measures against a crisis that keeps escalating. If the Hormuz closure holds, India faces the prospect of rationed fuel supplies, a widening current account deficit, and difficult conversations about whether to join or resist America's blockade of Iranian shipping — all while millions of its citizens live in the blast radius.

Prime Minister Modi is expected to raise the Hormuz crisis directly with Trump at the G7 summit in Evian-les-Bains, France, starting June 15. For India, the stakes could not be higher."""
    
    sources = json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com"},
        {"name": "Barron's", "url": "https://www.barrons.com"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com"},
    ])
    
    # Image sourcing
    print("  Sourcing image...")
    img_url, img_attr = source_image(
        slug,
        wiki_queries=["Strait of Hormuz", "Persian Gulf oil tanker"],
        pexels_query="oil tanker strait ocean shipping",
    )
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "status": "review",
        "is_editorial": False,
        "sources": sources,
        "image_url": img_url or "",
        "image_caption": "Commercial vessels transit the Strait of Hormuz, the narrow waterway through which one-fifth of global oil shipments normally pass",
        "image_attribution": img_attr or "",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    
    return insert_article(article)


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Seven Indian Workers Killed in Dubai Crash
# ═══════════════════════════════════════════════════════════════════════

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Seven Indian Workers Killed in Dubai")
    print("="*60)
    
    slug = "seven-indian-workers-killed-dubai-minibus-crash-emirates-road-20260611"
    
    headline = "Seven Indian Workers Killed in Dubai After Minibus Rams Into Stalled Truck on Emirates Road."
    
    subheadline = "The Indian Consulate is assisting families of the dead and nine others injured in the crash, one of the deadliest road accidents involving Indian nationals in the Gulf this year."
    
    body = """Seven people, including several Indian workers, were killed on Monday when a minibus crashed into a truck that had stopped on Emirates Road in Dubai due to a mechanical fault. Nine others were injured — five seriously.

The crash is one of the deadliest road accidents involving Indian nationals in the Gulf in recent memory, and has prompted the Indian Consulate in Dubai to deploy officials to hospitals and coordinate directly with Emirati authorities.

## How It Happened

According to Brigadier Juma Salem bin Suwaidan, Director of the General Department of Traffic at Dubai Police, the truck had come to a sudden stop in the middle of Emirates Road after suffering a technical fault. The minibus driver, who was allegedly not paying sufficient attention and failed to maintain a safe braking distance, rammed into the rear of the truck at speed.

The force of the collision killed seven people on impact or shortly after. Of the nine survivors, five sustained serious injuries while four suffered moderate injuries. All were immediately transported to nearby hospitals by emergency services.

Dubai Police dispatched specialists from the Traffic Accident Investigation Section to the scene. Traffic patrols were deployed to manage flow, and both the damaged truck and minibus were cleared to restore normal movement on the road. The investigation remains ongoing, and the identities of the victims have not been publicly released pending notification of families.

## Consulate Response

The Indian Consulate in Dubai moved quickly. In a statement posted on X, the mission said it was "deeply saddened by the tragic road accident in Dubai that claimed the lives of several Indian workers."

Consular officials visited the hospital, met with the injured Indian nationals, and began coordinating with local authorities to provide assistance and support. The Consulate said it is also working to facilitate the repatriation of the remains of those who died and to help families navigate the procedural and financial challenges that follow a death abroad.

"Our heartfelt condolences and prayers are with the grieving families during this difficult time," the Consulate said.

## A Recurring Pattern

The tragedy underscores the everyday dangers faced by millions of Indian blue-collar workers in the Gulf states. India's Ministry of External Affairs has recorded hundreds of accidental deaths among Indian nationals in the Gulf over the past decade, with road accidents, workplace injuries, and heat-related fatalities among the leading causes.

The UAE alone hosts more than 3.4 million Indian nationals — the largest Indian expatriate community in any single country. The majority work in construction, transport, logistics, and service industries, often commuting in buses or company-provided vehicles on high-speed Gulf highways where traffic fatalities remain a persistent problem despite years of enforcement campaigns.

According to Dubai Police, Emirates Road — a major highway connecting Dubai to its northern suburbs and neighbouring emirates — has been the site of numerous fatal collisions, with rear-end crashes involving heavy vehicles identified as a recurring hazard.

## What Families Should Know

Indian workers' families in India often face an agonising wait for information after incidents like this. The Indian embassy and consulates in the Gulf typically assist with death certificates and attestation, coordination with employers on unpaid wages and end-of-service benefits, repatriation of mortal remains — which can cost between $3,000 and $5,000 and often depends on the employer's insurance — and emergency travel documents for family members who need to travel to the Gulf.

The Indian Community Welfare Fund, maintained by Indian missions abroad, can cover repatriation costs and emergency medical bills in cases where the employer or insurer fails to pay. Families should contact the Indian Consulate in Dubai at +971-4-397-1222 or the 24-hour helpline of the Ministry of External Affairs at +91-11-2338-4747 for assistance.

## A Dangerous Moment in the Gulf

The crash comes at a particularly tense time for the Indian diaspora in the Gulf. The Iran–U.S. conflict has already resulted in missile attacks on the region, a declared closure of the Strait of Hormuz, and the arrest of 19 Indian nationals in the UAE for spreading alleged misinformation about the conflict on social media. For families back in India, every news alert from the Gulf now carries an extra layer of dread."""
    
    sources = json.dumps([
        {"name": "Madhyamam Online", "url": "https://www.madhyamamonline.com"},
        {"name": "The Indian Witness", "url": "https://www.indianwitness.com"},
        {"name": "PTI via Inshorts", "url": "https://www.inshorts.com"},
        {"name": "TeluguNow", "url": "https://www.telugunow.com"},
    ])
    
    # Image sourcing
    print("  Sourcing image...")
    img_url, img_attr = source_image(
        slug,
        wiki_queries=["Emirates Road Dubai", "Dubai road highway"],
        pexels_query="Dubai highway road traffic emergency",
    )
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "status": "review",
        "is_editorial": False,
        "sources": sources,
        "image_url": img_url or "",
        "image_caption": "Emirates Road in Dubai, where a minibus collided with a stalled truck on Monday killing seven Indian workers",
        "image_attribution": img_attr or "",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    
    return insert_article(article)


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 3: Indians Founded 96 US Unicorn Startups
# ═══════════════════════════════════════════════════════════════════════

def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: Indians Lead US Unicorn Startups")
    print("="*60)
    
    slug = "indians-founded-96-unicorn-startups-us-nfap-study-immigrant-entrepreneurs-20260611"
    
    headline = "Indians Have Founded 96 of America's Billion-Dollar Startups. No Other Immigrant Group Comes Close."
    
    subheadline = "A new study from the National Foundation for American Policy finds immigrants built 59 per cent of all US unicorns — with Indian-origin founders leading the pack by a massive margin, even as the MAGA movement targets them."
    
    body = """At a time when the political debate in the United States has curdled around whether immigrants are stealing American jobs, a new study offers a sharply different picture: immigrants are building the companies that define America's economic future — and Indians are leading the charge by an extraordinary margin.

According to a policy brief from the National Foundation for American Policy (NFAP), immigrants founded or co-founded 455 of America's 775 unicorn startups — private companies valued at over $1 billion — representing 59 per cent of all billion-dollar ventures in the country. Nearly 80 per cent of US unicorns have either an immigrant founder or an immigrant in a key leadership role.

Among all immigrant groups, Indian-origin entrepreneurs dominate the table. People of Indian origin account for 96 unicorn startups — far ahead of Israel (60), Britain (47), and China (41).

## The Numbers in Context

The scale of Indian entrepreneurial success in America is worth pausing over. Indian-origin households in the United States now earn a median income exceeding $150,000 — roughly 80 per cent more than the typical American household income of $83,730. This is not a story about cheap labour undercutting domestic workers, the narrative that has gained traction in certain MAGA-aligned political circles. It is a story about immigrants creating the companies, jobs, and tax revenue that sustain the American innovation economy.

The NFAP study arrives at a particularly charged moment. The Trump administration has proposed a $100,000 H-1B visa fee — recently struck down by a federal court — and a new bill, the PROTECT American Workers Act, aims to codify even steeper fees. Visa wait times for Indians remain the longest in the world, with EB-2 green card queues recently slamming shut until October. Anti-Indian sentiment has been amplified on social media, with viral posts and organised campaigns targeting Indian workers in Silicon Valley and beyond.

Against that backdrop, the unicorn data is a direct rebuttal.

## Who Are These Founders?

The study does not name all 96 Indian-origin unicorn founders, but the broader ecosystem is well known. Indian immigrants or their children have founded or led companies spanning enterprise software, fintech, AI, health tech, logistics, and cybersecurity. Some of the most prominent Indian-origin-founded unicorns include companies in cloud infrastructure, payments processing, and artificial intelligence.

The pattern extends beyond founders to the C-suite. Indian-born CEOs run three of the five largest technology companies in the world — Alphabet's Sundar Pichai, Microsoft's Satya Nadella, and IBM's Arvind Krishna. Adobe's Shantanu Narayen and Palo Alto Networks' Nikesh Arora are among the most prominent Indian-origin leaders in the tech sector.

The pipeline shows no sign of slowing. Indian students remain the second-largest group of international students in the United States, and Optional Practical Training (OPT) extensions for STEM graduates continue to funnel Indian talent directly into the startup ecosystem. Nearly half of all H-1B visa holders are Indian-born.

## The Contradiction at the Heart of US Immigration Policy

The NFAP study exposes a fundamental contradiction in American politics. The same workforce that MAGA rhetoric portrays as a threat to American jobs is, by the numbers, the most prolific creator of billion-dollar American companies among any immigrant group. Every unicorn generates hundreds of jobs — in engineering, sales, marketing, operations, legal, and support. The multiplier effect extends far beyond the founders themselves.

Stuart Anderson, executive director of NFAP and a former head of policy at the Immigration and Naturalization Service, has argued that restricting skilled immigration does not protect American workers — it pushes entrepreneurial talent to Canada, the UK, and Singapore, countries that have explicitly redesigned their immigration systems to attract the kind of founders the US is making it harder to retain.

## What NRIs Should Take Away

For the Indian diaspora, the study is a source of pride — but also a reminder that the policy environment remains hostile. The $100K H-1B fee may have been struck down in court, but the legislative effort to codify it continues. EB-2 retrogression means tens of thousands of Indian professionals are stuck in a green card queue that stretches over a decade. And the cultural climate, shaped by social media disinformation and political opportunism, has made many Indian-Americans feel less welcome than their economic contributions suggest they should be.

The 96 unicorns are proof of what Indian immigrants have built. Whether America continues to be the place where they build remains an open question."""
    
    sources = json.dumps([
        {"name": "National Foundation for American Policy (NFAP)", "url": "https://nfap.com"},
        {"name": "Times of India / GIBN", "url": "https://www.globalindiabroadcastnews.com"},
        {"name": "NDTV", "url": "https://www.ndtv.com"},
    ])
    
    # Image sourcing
    print("  Sourcing image...")
    img_url, img_attr = source_image(
        slug,
        wiki_queries=["Silicon Valley startup technology", "Indian Americans technology"],
        pexels_query="Silicon Valley startup office technology innovation",
    )
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "status": "review",
        "is_editorial": False,
        "sources": sources,
        "image_url": img_url or "",
        "image_caption": "Silicon Valley, where Indian-origin entrepreneurs have founded more billion-dollar startups than any other immigrant group",
        "image_attribution": img_attr or "",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    
    return insert_article(article)


# ── main ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Videshi News Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Writing 3 articles...")
    
    results = []
    
    art1_id = write_article_1()
    results.append(("Hormuz closure", art1_id))
    
    art2_id = write_article_2()
    results.append(("Dubai crash", art2_id))
    
    art3_id = write_article_3()
    results.append(("Indian unicorns", art3_id))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, aid in results:
        status = "✓" if aid else "✗"
        print(f"  {status} {name}: {aid or 'FAILED'}")
    
    failures = sum(1 for _, aid in results if not aid)
    if failures:
        print(f"\n⚠ {failures} article(s) failed!")
        sys.exit(1)
    else:
        print(f"\n✓ All 3 articles inserted with status=review")
