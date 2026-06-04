#!/usr/bin/env python3
"""News writer for The Videshi — generates 3 articles with multi-source image sourcing."""

import json, os, sys, time, uuid, subprocess, urllib.parse, io, re
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
                    key, val = line.split('=', 1)
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import requests
from PIL import Image

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ─── Image sourcing functions ───

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
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


def fetch_wikimedia_commons(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
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
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []


def fetch_pexels_image(*queries):
    """Search Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in queries:
        try:
            result = subprocess.run([
                "curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape"
            ], capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels: found for '{q}'")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image to JPEG."""
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P', 'LA'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    compressed = buf.getvalue()
    print(f"  📦 Compressed: {len(img_bytes)//1024}KB → {len(compressed)//1024}KB ({img.width}x{img.height})")
    return compressed


def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage bucket article-images."""
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {filename}")
        return public_url
    else:
        print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
        return None


def download_image(url):
    """Download image bytes."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            ct = r.headers.get("Content-Type", "")
            if "image" in ct or len(r.content) > 10000:
                print(f"  ✓ Downloaded {len(r.content)//1024}KB from {url[:60]}...")
                return r.content
        else:
            print(f"  ⚠ Download issue: status={r.status_code}, size={len(r.content)}")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None


def source_image(slug, person_name=None, topic_queries=None, pexels_queries=None):
    """Multi-source image search: Wikipedia → Wikimedia Commons → Pexels. Returns (public_url, attribution)."""
    candidates = []

    # Source 1: Wikipedia (person articles)
    if person_name:
        wiki_url = fetch_wikipedia_person_image(person_name)
        if wiki_url:
            candidates.append({"url": wiki_url, "source": "Wikimedia Commons", "priority": 1})

    # Source 2: Wikimedia Commons
    if topic_queries:
        for tq in topic_queries:
            results = fetch_wikimedia_commons(tq)
            for r in results[:2]:
                candidates.append({"url": r["url"], "source": "Wikimedia Commons", "priority": 2})
            if results:
                break

    # Source 3: Pexels
    if pexels_queries:
        pexels_url = fetch_pexels_image(*pexels_queries)
        if pexels_url:
            candidates.append({"url": pexels_url, "source": "Pexels", "priority": 3})

    # Pick best and upload
    candidates.sort(key=lambda c: c["priority"])
    for cand in candidates:
        print(f"  🎯 Trying {cand['source']}: {cand['url'][:70]}...")
        img_bytes = download_image(cand["url"])
        if img_bytes:
            compressed = compress_image(img_bytes)
            if len(compressed) > 5000:
                filename = f"{slug}.jpg"
                public_url = upload_to_supabase(compressed, filename)
                if public_url:
                    return public_url, cand["source"]

    print("  ❌ No suitable image found")
    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS_SB, json=article, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  ✓ Inserted article: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ❌ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ─── Articles ───

now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ── ARTICLE 1: H-1B $100K fee ──
print("\n" + "="*60)
print("ARTICLE 1: H-1B $100,000 fee — 200,000+ applicants")
print("="*60)

slug1 = "h1b-100000-fee-200000-applicants-dhs-mullin-senate-fy2026"

img1_url, img1_attr = source_image(
    slug1,
    person_name="Markwayne Mullin",
    topic_queries=["H-1B visa United States", "US Capitol Senate hearing"],
    pexels_queries=["US Capitol building Washington", "immigration visa passport"]
)

body1 = """More than 200,000 applicants paid $100,000 each to fast-track their H-1B visa applications in fiscal year 2026, the US Department of Homeland Security has confirmed — a figure that reveals just how far employers and skilled workers are willing to go to navigate an immigration system that now charges a premium for basic functionality.

DHS Secretary Markwayne Mullin disclosed the numbers during testimony before the Senate Appropriations Subcommittee on Homeland Security on Tuesday, telling lawmakers that the department received approximately 286,000 H-1B applications in the current fiscal year. Of those, over 200,000 — more than 70 percent — opted to pay the $100,000 expedited processing fee introduced by President Trump's September 2025 executive proclamation.

## Fifteen Days Versus Seven and a Half Months

The arithmetic behind the surge is straightforward. Applicants who pay the fee have their cases processed in roughly 15 days. Everyone else waits an average of seven and a half months — a timeline that can derail hiring schedules, disrupt project timelines and leave foreign workers in legal limbo while their paperwork sits in a queue.

For Indian professionals, who constitute the largest single nationality among H-1B holders, the stakes are particularly acute. Many are already caught in a green card backlog that stretches back over a decade, and delays in H-1B processing compound an already precarious immigration status. The $100,000 fee, typically borne by sponsoring employers, effectively creates a two-tier system in which speed is a luxury reserved for those who can afford it.

## Rural Hospitals and Schools Left Behind

The hearing exposed a sharp divide between the programme's largest beneficiaries — technology companies recruiting skilled engineers in Silicon Valley and other tech hubs — and institutions serving communities that cannot absorb the cost.

Senator Susan Collins of Maine told the subcommittee that a hospital in Presque Isle, a rural community in the state's north, recently had to pay the full $100,000 to secure a surgeon from overseas. She argued that medical providers serving remote areas should be treated differently from employers recruiting in sectors with larger domestic labour pools.

"I would suggest that there's a huge difference between bringing in a computer expert from another country to work in wealthy California and Silicon Valley versus a much-needed surgeon to work at a rural hospital in northern Maine," Collins said.

Mullin told Collins he would explore whether such applications could receive flexibility on a case-by-case basis, though he stopped short of committing to a formal exemption. Senator Lisa Murkowski of Alaska raised similar concerns about the shortage of teachers in rural school districts, signalling that the pressure for carve-outs extends beyond healthcare.

## What It Means for Indian Tech Workers

The $100,000 fee has reshaped the economics of H-1B sponsorship. For large technology firms and well-funded startups, the cost is a manageable line item that buys certainty in hiring timelines. For smaller companies, universities, research institutions and non-profits — many of which employ Indian workers — the fee is prohibitive.

Immigration attorneys have noted that the fee is triggering a shift in sponsorship patterns, with some employers reconsidering or delaying H-1B filings altogether. The Murthy Law Firm, a prominent immigration practice, observed in April that the practical application of the fee has diverged from published guidance, creating additional uncertainty for applicants and their employers.

The broader picture for Indian nationals is one of compounding costs. Beyond the $100,000 expedited fee, H-1B applicants face standard filing fees, premium processing charges, legal costs and, for many, the indefinite expense of maintaining status while waiting for an employment-based green card. The EB-2 visa category for Indians was effectively frozen earlier this year, with the backlog now stretching to 2014.

## A System That Works for Those Who Can Pay

The DHS testimony laid bare a system operating under enormous demand. The 286,000 applications received in FY2026 represent a modest decline from previous years' initial registration totals, reflecting the chilling effect of higher costs. But the overwhelming willingness of applicants to pay $100,000 suggests that demand for US work visas remains structurally robust, driven by wage differentials, career opportunities and the sheer depth of the American technology economy.

For the Indian diaspora, the H-1B programme remains the primary legal pathway into the American workforce. Whether the current fee structure survives legal challenges or congressional scrutiny is an open question. What is clear is that 200,000 applicants — and the companies behind them — decided that $100,000 was a price worth paying to avoid a seven-month wait. That calculation, more than any policy statement, tells you what the system has become."""

articles.append({
    "headline": "Over 200,000 H-1B Applicants Paid $100,000 Each to Skip the Queue. The System Now Has a Price Tag.",
    "subheadline": "DHS Secretary Mullin told Congress that 70 percent of this year's H-1B applicants chose the expedited route, while rural hospitals and schools struggle to compete.",
    "slug": slug1,
    "body": body1,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now_iso,
    "sources": json.dumps(["The Hindu BusinessLine / PTI", "Reuters", "DHS Senate Appropriations Testimony (June 2, 2026)", "Murthy Law Firm"]),
    "image_url": img1_url,
    "image_caption": "DHS Secretary Markwayne Mullin testifies before the Senate Appropriations Subcommittee in Washington",
    "image_attribution": img1_attr or "Wikimedia Commons",
    "is_editorial": False
})


# ── ARTICLE 2: India-Africa Summit Postponed / Ebola ──
print("\n" + "="*60)
print("ARTICLE 2: India-Africa Summit Postponed Amid Ebola")
print("="*60)

slug2 = "india-africa-forum-summit-postponed-ebola-congo-outbreak-bundibugyo-20260604"

img2_url, img2_attr = source_image(
    slug2,
    person_name=None,
    topic_queries=["India Africa Forum Summit", "Ebola outbreak Congo 2026", "World Health Organization Ebola response"],
    pexels_queries=["Africa summit diplomacy", "medical health workers protective equipment"]
)

body2 = """India and the African Union have quietly postponed one of the most significant diplomatic gatherings on their shared calendar — the Fourth India-Africa Forum Summit — after concluding that an Ebola outbreak spreading across eastern Congo made it inadvisable to bring dozens of heads of state and hundreds of delegates to New Delhi. No new dates have been set.

The summit, originally scheduled for May 28 to 31 in the Indian capital, was expected to convene leaders from across the African continent alongside Indian officials for discussions on trade, development finance, health cooperation and strategic alignment. Its postponement, announced jointly by the Government of India and the African Union Commission, was framed as a precautionary public health measure rather than a diplomatic setback.

## The Outbreak India Is Watching

The Ebola outbreak that forced the postponement is not an ordinary one. It is caused by the Bundibugyo strain of the virus, for which there is no approved vaccine and no specific treatment — a complication that has alarmed epidemiologists and slowed the containment response.

As of this week, the Democratic Republic of Congo has recorded 363 confirmed cases and 62 deaths since the outbreak was officially declared on May 15, according to the country's health ministry. The virus has spread across 17 health zones in Ituri province, seven in North Kivu and one in South Kivu. It has also crossed into Uganda, where 15 cases have been confirmed.

The World Health Organization has acknowledged progress in testing and surveillance but conceded that the response is still playing catch-up. "The outbreak had a big head start, and we're still behind," WHO Director-General Tedros Adhanom Ghebreyesus said this week, "but under the leadership of the government of DRC, we're catching up."

Complicating matters further, the outbreak has reached territory controlled by the Allied Democratic Forces, an Islamic State affiliate operating in eastern Congo. Health workers cannot safely enter the area, and volunteers have reportedly had to smuggle blood samples out of militant-held zones for laboratory testing.

## India's Ebola Calculus

India's decision to defer the summit reflects a calculation that extends beyond protocol. The country has a significant diaspora in Africa — an estimated three million Indians live and work across the continent — and maintains commercial interests in mining, pharmaceuticals, infrastructure and energy across several African nations. An outbreak that spills beyond Congo and Uganda would directly affect Indian communities and trade routes.

The Ministry of External Affairs has issued health advisories and maintained contact with African health authorities as the situation develops. Diplomats involved in the planning noted that postponement also creates space for India and the African Union to coordinate on outbreak response, including vaccine research and treatment supply chains, before resuming summit-level engagement.

India's pharmaceutical industry is a critical supplier of generic medicines to the African continent. Indian vaccine manufacturers, including the Serum Institute of India, played a central role in supplying COVID-19 doses to African nations through the COVAX facility and bilateral agreements. Whether India will step into a similar role for Ebola therapeutics or future vaccines remains an open question, but the institutional infrastructure exists.

## What the Summit Was Supposed to Deliver

The India-Africa Forum Summit is the flagship platform for India's engagement with the continent. The last edition was held in 2015, when Prime Minister Narendra Modi hosted leaders from 54 African nations in New Delhi — the largest gathering of its kind at the time. Since then, India has expanded its development finance commitments, opened new diplomatic missions and increased trade volumes, though the relationship has been overshadowed by China's far larger financial footprint in Africa.

The fourth summit was expected to focus on digital infrastructure, healthcare partnerships, critical mineral supply chains and climate finance — areas where India is positioning itself as an alternative to both Chinese lending and Western conditionality. Its indefinite postponement leaves a gap in India's continental strategy at a time when several African nations are actively renegotiating their external partnerships.

## No Vaccine, No Timeline

The absence of a vaccine for the Bundibugyo strain is the single factor that makes this outbreak different from Congo's previous Ebola emergencies, several of which were contained with the help of the rVSV-ZEBOV vaccine developed during the 2014-2016 West Africa crisis. That vaccine targets the Zaire strain and is ineffective against Bundibugyo.

Researchers are working to adapt existing vaccine candidates and test experimental treatments, but no clinical trials have begun at scale. Until a medical countermeasure is available, containment depends entirely on surveillance, contact tracing, isolation and community engagement — precisely the measures that armed conflict in eastern Congo continues to undermine.

For India, the postponement is a setback measured in months, not years. For the communities in eastern Congo living alongside both the virus and armed insurgents, the timeline is far less forgiving."""

articles.append({
    "headline": "India Postpones Its Flagship Africa Summit Indefinitely. The Reason Is an Ebola Strain No Vaccine Can Stop.",
    "subheadline": "The Fourth India-Africa Forum Summit, planned for New Delhi, was shelved after a Bundibugyo Ebola outbreak in Congo reached 363 cases with no approved vaccine or treatment in sight.",
    "slug": slug2,
    "body": body2,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now_iso,
    "sources": json.dumps(["The Indian EYE", "Reuters", "World Health Organization", "Wall Street Journal", "US State Department"]),
    "image_url": img2_url,
    "image_caption": "Health workers during an Ebola response operation in the Democratic Republic of Congo",
    "image_attribution": img2_attr or "Wikimedia Commons",
    "is_editorial": False
})


# ── ARTICLE 3: Iran oil exports crash ──
print("\n" + "="*60)
print("ARTICLE 3: Iran Oil Exports Crash to Six-Year Low")
print("="*60)

slug3 = "iran-oil-exports-six-year-low-us-blockade-hormuz-india-energy-crisis-20260604"

img3_url, img3_attr = source_image(
    slug3,
    person_name=None,
    topic_queries=["Strait of Hormuz oil tanker", "Iran oil tanker Persian Gulf", "oil tanker shipping"],
    pexels_queries=["oil tanker ship ocean", "crude oil refinery industrial"]
)

body3 = """Iran's crude oil and condensate exports collapsed to their lowest level in at least six years in May, averaging just 209,000 barrels per day — down from 1.9 million barrels per day in March — as the US naval blockade and the effective closure of the Strait of Hormuz strangled what remains of Tehran's petroleum lifeline.

The figures, published by shipping analytics firm Vortexa and confirmed by separate data from Kpler, represent a steeper decline than most market analysts anticipated. Iran's exports are now below the levels reached during the first Trump administration's "maximum pressure" campaign in late 2019, when sanctions alone — without a shooting war — had squeezed shipments to roughly 300,000 barrels per day.

## The Blockade Is Working. The Strait Is Not.

The US began enforcing a naval blockade of Iranian ports on April 13, targeting vessels entering or departing Iranian waters. The result has been a near-total shutdown of Iran's ability to move oil by sea. But the blockade is only part of the story.

The Strait of Hormuz, through which roughly a fifth of the world's oil and liquefied natural gas supplies normally flow, remains largely closed more than three months after the US and Israel launched strikes on Iran at the end of February. The closure has cut off not just Iranian exports but shipments from Saudi Arabia, Kuwait, Iraq and the UAE — producers that collectively account for a far larger share of global supply than Iran alone.

"The key drivers appear to be the disruption around the Strait of Hormuz, the US naval blockade targeting vessels entering or departing Iranian ports, and the broader unwillingness of owners, operators, insurers and counterparties to expose vessels and crews to the current security environment," said Vortexa analyst Claire Jungman.

## India's Energy Bind Tightens

For India, which imports over 80 percent of its crude oil, the compounding effects of the Hormuz closure and the Iranian blockade have created what policymakers in New Delhi are treating as a slow-moving energy emergency.

India had largely stopped buying Iranian crude after previous rounds of US sanctions, but the broader disruption to Gulf shipping has constrained supplies from Iraq, Saudi Arabia and the UAE — countries that collectively account for roughly 60 percent of India's oil imports. With Brent crude hovering near $96 a barrel and the rupee under sustained pressure, the cost of India's import bill has ballooned.

The Reserve Bank of India's monetary policy decision on Friday will be shaped in part by the energy shock. Inflation driven by higher fuel and transport costs has complicated the central bank's calculus, with most economists expecting the RBI to hold rates steady while signalling readiness to tighten if price pressures intensify. The rupee has weakened more than 5 percent since the war began.

Prime Minister Narendra Modi's ongoing five-nation diplomatic tour — which has already taken him to the UAE and will include Saudi Arabia — is explicitly designed to secure alternative energy supply arrangements. The strategic petroleum reserves agreement signed with Abu Dhabi's ADNOC during Modi's stopover, and the framework for long-term LNG supply to Hindustan Petroleum, are direct responses to the Hormuz disruption.

## Floating Storage and Stranded Barrels

Of the roughly 147 million barrels of Iranian crude and condensate currently sitting in floating storage on tankers, approximately 67 million barrels are stranded inside the Gulf and the Gulf of Oman, unable to move through the blocked strait. The total volume of floating storage has fallen from a peak of 190 million barrels in late April as some tankers have discharged cargo in China, but the pace of drawdown is slow.

China remains Iran's primary customer, though even Chinese imports of Iranian crude fell to 1.1 million barrels per day in May — the lowest since January 2025 — as independent refiners in Shandong province cut processing rates in response to weak domestic fuel demand and elevated costs.

The pricing has shifted accordingly. Iranian Light crude is now being offered at a discount of 50 cents to $1 per barrel to ICE Brent for delivery to Shandong, down from premiums of $1 to $2 in recent months. When the only buyer left is offering less, the economics of sanctions enforcement start to bite in ways that export statistics alone do not capture.

## No Clear Path to Recovery

The prospect of reopening the Strait of Hormuz remains the central variable in global energy markets. Iran has made a ceasefire in Lebanon and the lifting of the US blockade preconditions for any deal to restore normal shipping. Hezbollah's rejection on Thursday of a US-brokered Lebanon ceasefire — and Israel's declaration that it would not withdraw troops — pushed that prospect further away.

Even if a political breakthrough were to materialise, the recovery of normal shipping through Hormuz would take months. Producers have shut in roughly 11 million barrels per day of capacity during the conflict and will not restart without confidence that exports can flow reliably. Shipowners remain reluctant to send empty tankers into the Gulf, and insurance premiums continue to reflect wartime risk.

For India, the arithmetic is unforgiving. Every week the strait remains closed costs the economy billions in higher energy imports, feeds inflation and weakens the rupee. The diplomatic scramble for alternative supplies is rational but insufficient to replace the volumes that normally transit Hormuz. India's energy security, for all the strategic petroleum reserve agreements and LNG contracts being signed on Modi's tour, ultimately depends on a resolution that no one in New Delhi can control."""

articles.append({
    "headline": "Iran's Oil Exports Have Collapsed to a Six-Year Low. India Cannot Afford to Wait for a Recovery.",
    "subheadline": "Shipping data shows Iranian crude shipments fell to 209,000 barrels per day in May, down 89 percent from March, as the US blockade and Hormuz closure strangle Gulf energy flows.",
    "slug": slug3,
    "body": body3,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now_iso,
    "sources": json.dumps(["Reuters", "Vortexa", "Kpler", "The Hindu BusinessLine"]),
    "image_url": img3_url,
    "image_caption": "An oil tanker near the Strait of Hormuz, where shipping remains severely disrupted by the US-Iran conflict",
    "image_attribution": img3_attr or "Wikimedia Commons",
    "is_editorial": False
})


# ─── Publish all articles ───
print("\n" + "="*60)
print("PUBLISHING ARTICLES")
print("="*60)

success_count = 0
for i, art in enumerate(articles):
    print(f"\n--- Article {i+1}: {art['slug']} ---")
    if not art.get("image_url"):
        print("  ⚠ No image — publishing without hero image")
        art.pop("image_url", None)
        art.pop("image_caption", None)
        art.pop("image_attribution", None)

    art_id = insert_article(art)
    if art_id:
        success_count += 1

print(f"\n{'='*60}")
print(f"DONE: {success_count}/{len(articles)} articles published")
print(f"{'='*60}")
