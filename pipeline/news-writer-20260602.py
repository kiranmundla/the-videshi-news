#!/usr/bin/env python3
"""News writer for The Videshi — June 2, 2026 batch."""

import json, os, re, time, uuid, requests, urllib.parse
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────
for envfile in [os.path.expanduser("~/workspace/.env.supabase"),
                os.path.expanduser("~/workspace/.env.pexels")]:
    if os.path.exists(envfile):
        with open(envfile) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

SB_URL  = os.environ["SUPABASE_URL"]
SB_KEY  = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS  = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels with specific search terms."""
    if not PEXELS:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Verify image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Sometimes HEAD doesn't return Content-Length, try GET
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase article-images bucket."""
    try:
        r = requests.get(image_url, timeout=20,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed: {r.status_code}, size={len(r.content)}")
            return None
        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": ct,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ── articles ─────────────────────────────────────────────────────────

articles = []

# ── ARTICLE 1: Venezuela's Rodriguez visits India ────────────────────

articles.append({
    "headline": "Venezuela's Acting President Will Visit India This Week. The Oil Math Is the Reason.",
    "subheadline": "Delcy Rodriguez arrives Wednesday for five days of energy talks as India becomes the second-largest buyer of Venezuelan crude, importing 427,000 barrels a day.",
    "slug": "venezuela-rodriguez-india-visit-june-3-energy-oil-427000-bpd-modi-reliance-20260602",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Ministry of External Affairs", "url": "https://www.mea.gov.in"},
        {"name": "Press Trust of India", "url": "https://www.ptinews.com"}
    ]),
    "body": """Venezuela's Acting President Delcy Rodriguez will arrive in New Delhi on Wednesday for a five-day working visit that is, at bottom, about one thing: crude oil. India's Ministry of External Affairs confirmed the June 3–7 trip on Tuesday, saying Rodriguez will hold talks with Prime Minister Narendra Modi covering the "full spectrum" of bilateral relations — energy, trade, investment, pharmaceuticals, healthcare, transportation, and renewable energy.

The diplomatic language is wide. The commercial reality is narrow and urgent. India was the second-largest buyer of Venezuelan crude in May, importing 427,000 barrels per day — second only to the United States, according to Reuters shipping data. Reliance Industries has emerged as one of the three largest global buyers of Venezuelan oil in recent months, a position that would have been unthinkable a year ago.

## Why India Needs Venezuelan Oil Now

The arithmetic is brutal. Before the U.S.–Israeli strikes on Iran that began on February 28, more than 40 percent of India's crude imports transited the Strait of Hormuz. That chokepoint is now effectively shut. With Brent crude hovering near $95 a barrel and the Indian rupee under pressure from the largest foreign institutional outflows in modern history, every alternative barrel matters.

India had stopped buying Venezuelan crude last year after the Trump administration slapped a 25 percent discretionary tariff on countries purchasing oil from Caracas. It resumed purchases in February after sanctions were eased following a flagship supply pact between Washington and Caracas — a deal reached in the aftermath of the U.S. capture of President Nicolás Maduro in January. Under that agreement, proceeds from Venezuelan oil sales flow through bank accounts administered by the U.S. Treasury Department.

## The Numbers Behind the Visit

Venezuela's total oil exports rose to 1.25 million barrels per day in May — the third consecutive monthly increase. India's share of that flow has grown rapidly. Government trade data for April showed India's merchandise imports from Venezuela stood at $609.87 million, of which petroleum products accounted for $601.53 million. Exports in the other direction were a thin $20.33 million.

Rodriguez will be accompanied by Venezuela's ministers of foreign affairs, economy and finance, science and technology, communications, and transportation. It is the largest Venezuelan delegation to visit India in years, and the most senior since Rodriguez herself attended the India Energy Week conference in February 2025 as oil minister.

## Beyond Oil: Pharma and Renewables

While oil dominates the agenda, both sides are expected to discuss India's pharmaceutical exports to Venezuela, cooperation on renewable energy infrastructure, and technology partnerships. India's generic drug industry has long supplied Latin American markets, and Venezuela's healthcare system — battered by years of sanctions and mismanagement — needs affordable medicines.

## What This Means for the Diaspora

For NRIs in the energy sector and Indian businesses with Latin American exposure, the Rodriguez visit signals a broader shift in India's oil diplomacy. New Delhi is no longer waiting for the Hormuz crisis to resolve itself. It is building redundant supply chains from Latin America, Africa, and the Gulf's western flanks — and Venezuela, with its heavy crude grades that Indian refineries were built to process, is central to that strategy.

The visit also underscores how dramatically the global oil map has shifted since February. India's top five crude suppliers now include nations that barely registered a year ago, and Venezuela — a country India had deliberately avoided for geopolitical reasons — is now a cornerstone of its energy security.""",
    "image_search_person": "Delcy Rodriguez",
    "image_search_pexels": "oil refinery industrial",
    "image_search_pexels_fallback": "crude oil tanker ship",
})


# ── ARTICLE 2: CBSE OSM Row and new chairman ────────────────────────

articles.append({
    "headline": "A 17-Year-Old Read CBSE's Tender Files. Now India Has a New Board Chairman.",
    "subheadline": "The government replaced the CBSE chief and secretary within hours after a student's analysis of the On-Screen Marking contract triggered a national firestorm.",
    "slug": "cbse-osm-controversy-new-chairman-lokhande-prashant-sitaram-sarthak-sidhant-20260602",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Bar and Bench", "url": "https://www.barandbench.com"},
        {"name": "Careers360", "url": "https://news.careers360.com"},
        {"name": "Inshorts", "url": "https://inshorts.com"},
        {"name": "Press Trust of India", "url": "https://www.ptinews.com"}
    ]),
    "body": """The Central Board of Secondary Education has a new chairman. The government announced on Tuesday that Lokhande Prashant Sitaram will take over as CBSE chairperson, while outgoing chairman Rahul Singh has been transferred to the Department of Agriculture and Farmers Welfare. CBSE Secretary Himanshu Gupta was also moved out. The twin transfers happened within hours of each other.

The trigger was not a parliamentary inquiry or a ministry audit. It was a 17-year-old student from Jharkhand named Sarthak Sidhant, whose forensic reading of CBSE's tender documents for its On-Screen Marking system turned into the biggest education controversy of 2026.

## What Went Wrong With OSM

The On-Screen Marking system was introduced by CBSE this year to digitise the evaluation of Class 12 answer books. The idea was straightforward: scan answer sheets, distribute them to evaluators digitally, reduce manual handling, and speed up results.

What followed was anything but straightforward. When the post-result re-evaluation portal opened, students began accessing scanned copies of their answer sheets — and immediately flagged blurred scans, missing pages, mismatched handwriting, and scoring discrepancies. The complaints went viral on social media. The re-evaluation portal then developed technical and payment failures, forcing CBSE to delay parts of the process and bring in public sector banks to shore up payment infrastructure.

## How a Student Broke the Story Open

Sarthak Sidhant, a Class 12 student, did not stop at complaining about his own paper. He obtained CBSE's tender documents through public channels and published a detailed analysis questioning how Hyderabad-based EduTeck Coempt won the contract to implement the OSM system. His findings — published on a blog and later amplified by opposition politicians on social media — raised questions about the procurement process, the technical qualifications of the vendor, and whether CBSE followed standard government procurement norms.

CBSE has strongly rejected allegations of irregularities, insisting the process followed all applicable guidelines. But the political damage was already done.

## Congress Demands Pradhan's Resignation

The opposition Congress party escalated the attack beyond CBSE's leadership. Rahul Gandhi accused the Centre of "shielding" Education Minister Dharmendra Pradhan, and Congress formally demanded his resignation, calling the episode "one of the biggest institutional failures in India's education history."

The party pointed to what it described as the government's denial of cybersecurity vulnerabilities in the OSM system for weeks before finally acting. Whether the political pressure was the proximate cause of the leadership change or whether the transfers were already in the pipeline is unclear, but the timing left little room for alternative interpretations.

## Over 16,000 Students Seek Re-evaluation

The scale of the fallout is measurable. More than 16,000 students have submitted re-evaluation requests through the CBSE portal — itself a system that had to withstand cyberattacks during the submission window. The sheer volume suggests the marking concerns are not isolated.

## What Changes Under New Leadership

Lokhande Prashant Sitaram, the new chairperson, takes charge with NEET-UG 2026 scheduled for June 21, a date that carries its own pressure after last year's paper-leak scandal that triggered Supreme Court intervention. The court told India's exam agency last week to learn from the UPSC, "the one body that has never had a paper leak."

For millions of Indian families — including those in the diaspora whose children sit CBSE exams at affiliated schools abroad — the OSM controversy is a reminder that India's examination infrastructure remains fragile even as the stakes it carries grow heavier each year.""",
    "image_search_person": None,
    "image_search_pexels": "Indian students examination hall",
    "image_search_pexels_fallback": "students exam answer sheet India",
})


# ── ARTICLE 3: 5 new SC judges, highest-ever strength ───────────────

articles.append({
    "headline": "India's Supreme Court Just Hit Its Highest-Ever Strength. One of the New Judges Was Never a Judge Before.",
    "subheadline": "Five judges took oath on Tuesday, bringing the court to 37 — including V. Mohana, only the second woman in India's history to be elevated directly from the Bar to the apex court.",
    "slug": "supreme-court-5-new-judges-37-highest-strength-v-mohana-bar-elevation-20260602",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Bar and Bench", "url": "https://www.barandbench.com"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"},
        {"name": "SCC Online", "url": "https://www.scconline.com"},
        {"name": "Press Trust of India", "url": "https://www.ptinews.com"}
    ]),
    "body": """Chief Justice of India Surya Kant administered the oath of office to five new judges of the Supreme Court on Tuesday morning, raising the working strength of the court to 37 — the highest it has ever been.

The five are Justices Sheel Nagu, Shree Chandrashekhar, Sanjeev Sachdeva, Arun Palli, and V. Mohana. The first four were serving as chief justices of high courts before their elevation. Mohana was not.

## The Significance of V. Mohana

Venkita Subramani Mohana is only the second woman in Indian judicial history to be elevated directly from the Bar to the Supreme Court bench, after Justice Indu Malhotra in 2018. Unlike her four colleagues, she has never served as a judge at any level — she comes to the court as a senior advocate, a rare and constitutionally significant appointment.

With her oath, the Supreme Court now has two serving women judges. The other is Justice B.V. Nagarathna, who has been on the bench since August 2021 and is next in line to become Chief Justice of India — a milestone expected in 2027, when she will serve as CJI for slightly more than a month.

## Why the Court Was Expanded

The appointments came days after the government issued an ordinance amending the law to increase the sanctioned strength of the Supreme Court from 34 to 38, including the Chief Justice. The move was driven by India's staggering case backlog, which has grown even as the court has steadily added judges over the past decade.

Before Tuesday's oath ceremony, the court was operating with just 32 judges against what was then a 34-seat bench — two vacancies that the government had been slow to fill. With the ordinance expanding the court and the Collegium acting within days, five slots were filled in a single appointment cycle.

The court still has one vacancy.

## Who the New Judges Are

**Justice Sheel Nagu** served as Chief Justice of the Punjab and Haryana High Court. His parent high court was Madhya Pradesh, and he was enrolled as an advocate in October 1987.

**Justice Shree Chandrashekhar** was Chief Justice of the Bombay High Court, elevated from the Jharkhand High Court where he began his judicial career.

**Justice Sanjeev Sachdeva** headed the Madhya Pradesh High Court and came from the Delhi High Court, where he was known for handling significant constitutional and commercial matters.

**Justice Arun Palli** served as Chief Justice of the Jammu and Kashmir and Ladakh High Court, with the Punjab and Haryana High Court as his parent court.

**V. Mohana**, a senior advocate practising before the Supreme Court, was recommended by the Collegium on May 27. The President's approval came on June 1 — a turnaround of just four days, unusually fast by the standards of judicial appointments in India.

## Four Days From Recommendation to Oath

The speed of the appointment cycle is notable. The Supreme Court Collegium, headed by CJI Kant, recommended all five names on May 27. The Centre cleared them on June 1. The oath ceremony was held on June 2. In a system where judicial appointments have historically been delayed for months — sometimes years — by friction between the Collegium and the government, a four-day clearance signals alignment between the judiciary and the executive on the urgency of filling the bench.

## What Comes Next

Two sitting judges — Justice Pankaj Mithal and Justice J.K. Maheshwari — are set to retire on June 16 and June 28 respectively. Their departures will bring the strength back down to 35, creating three vacancies against the new 38-seat bench. The Collegium will need to move again before the summer recess to prevent the bench from thinning out.

For ordinary litigants and for the Indian diaspora navigating cross-border disputes, property matters, and constitutional questions from abroad, a fuller bench means shorter wait times and a better chance that cases are heard by constitution benches rather than routed into an indefinite queue.""",
    "image_search_person": "Surya Kant Chief Justice India",
    "image_search_pexels": "Supreme Court India building",
    "image_search_pexels_fallback": "Indian court judiciary gavel",
})


# ── process articles ─────────────────────────────────────────────────

for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"ARTICLE {i+1}: {art['headline'][:70]}...")
    print(f"{'='*60}")

    # Image sourcing
    image_url = None
    image_attribution = None

    # Try Wikipedia for person articles
    person = art.pop("image_search_person", None)
    pexels_q = art.pop("image_search_pexels", None)
    pexels_fb = art.pop("image_search_pexels_fallback", None)

    if person:
        image_url = fetch_wikipedia_person_image(person)
        if image_url:
            image_attribution = "Wikimedia Commons"

    # Fallback to Pexels
    if not image_url and pexels_q:
        image_url = fetch_pexels_image(pexels_q, pexels_fb)
        if image_url:
            image_attribution = "Pexels"

    # Validate
    if image_url and not validate_image(image_url):
        print(f"  ⚠ Image validation failed, trying upload anyway...")

    # Upload to Supabase if from Wikipedia (permanent but let's be safe)
    slug = art["slug"]
    if image_url and "upload.wikimedia.org" in image_url:
        uploaded = upload_to_supabase_storage(image_url, f"{slug}.jpg")
        if uploaded:
            image_url = uploaded
            image_attribution = "Wikimedia Commons"
    elif image_url and "pexels.com" not in image_url:
        uploaded = upload_to_supabase_storage(image_url, f"{slug}.jpg")
        if uploaded:
            image_url = uploaded

    if image_url:
        art["image_url"] = image_url
        art["image_attribution"] = image_attribution
        print(f"  ✓ Final image: {image_url[:80]}...")
    else:
        print(f"  ⚠ No image found — publishing without image")

    # Insert
    art_id = insert_article(art)
    if art_id:
        print(f"  ✓ Published: {slug}")
    else:
        print(f"  ✗ FAILED: {slug}")

    time.sleep(1)

print("\n\nDone! All articles processed.")
