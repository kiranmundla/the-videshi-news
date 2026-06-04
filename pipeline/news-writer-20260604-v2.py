#!/usr/bin/env python3
"""
News writer for The Videshi - 2026-06-04 evening run (v2 - fixed)
"""

import json, os, sys, io, time, subprocess
from datetime import datetime, timezone

# Load env - IMPORTANT: load ~/.env.supabase LAST so JWT key wins
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/workspace/.env.pexels'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/.env.supabase'))  # LAST - has full JWT

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

print(f"SUPABASE_URL: {SUPABASE_URL[:40]}...")
print(f"SUPABASE_KEY starts with: {SUPABASE_KEY[:20]}...")
print(f"PEXELS_KEY starts with: {PEXELS_KEY[:10]}...")

import requests
from PIL import Image

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def fetch_wikipedia_person_image(person_name):
    import urllib.parse
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

def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
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
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0)
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(*queries):
    for query in queries:
        try:
            import urllib.parse
            encoded_q = urllib.parse.quote(query)
            result = subprocess.run([
                'curl', '-sS', '--max-time', '10',
                '-H', f'Authorization: {PEXELS_KEY}',
                f'https://api.pexels.com/v1/search?query={encoded_q}&per_page=3&size=large'
            ], capture_output=True, text=True, timeout=15)
            if result.stdout.strip():
                data = json.loads(result.stdout)
                photos = data.get('photos', [])
                if photos:
                    url = photos[0]['src']['large2x']
                    print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
                    return url, photos[0].get('alt', '')
        except Exception as e:
            print(f"  ⚠ Pexels error for '{query}': {e}")
    return None, None

def download_image(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 5000:
            print(f"  ✓ Downloaded {len(r.content)} bytes from {url[:60]}...")
            return r.content
        else:
            print(f"  ⚠ Download: status={r.status_code}, size={len(r.content)}")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None

def upload_to_supabase(img_bytes, filename):
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'image/jpeg',
        'x-upsert': 'true'
    }
    try:
        r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

def source_image(slug, person_name=None, search_terms=None, pexels_queries=None):
    candidates = []
    
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "priority": 1})
    
    if search_terms:
        for term in search_terms:
            commons = fetch_wikimedia_commons_images(term)
            for r in commons[:2]:
                candidates.append({"url": r["url"], "source": "wikimedia_commons", "priority": 2})
            if candidates:
                break
    
    if pexels_queries:
        pexels_img, pexels_alt = fetch_pexels_image(*pexels_queries)
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels", "priority": 3})
    
    candidates.sort(key=lambda c: c["priority"])
    
    for candidate in candidates:
        img_bytes = download_image(candidate["url"])
        if img_bytes:
            compressed = compress_image(img_bytes)
            if len(compressed) < 5000:
                continue
            filename = f"{slug}.jpg"
            final_url = upload_to_supabase(compressed, filename)
            if final_url:
                attribution = "Wikimedia Commons" if candidate["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return final_url, attribution
    
    return None, None

def insert_article(article):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    try:
        r = requests.post(url, headers=HEADERS_SB, json=article, timeout=30)
        if r.status_code in (200, 201):
            result = r.json()
            art_id = result[0]['id'] if isinstance(result, list) and result else 'unknown'
            print(f"  ✓ Inserted: {art_id}")
            return art_id
        else:
            print(f"  ✗ Insert failed: {r.status_code} {r.text[:500]}")
            return None
    except Exception as e:
        print(f"  ✗ Insert error: {e}")
        return None


# ============================================================
# ARTICLE 1: Delhi Hotel Fire
# ============================================================
def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Delhi Hotel Fire Kills 21")
    print("="*60)
    
    slug = "delhi-malviya-nagar-hotel-fire-21-dead-foreign-nationals-medical-tourism-20260604"
    
    print("\n📸 Sourcing image...")
    img_url, img_attr = source_image(
        slug,
        search_terms=["Delhi fire 2026", "Delhi fire rescue operation"],
        pexels_queries=["building fire emergency rescue", "fire rescue apartment"]
    )
    
    body = """A fire that ripped through a six-storey building in south Delhi's Malviya Nagar on Wednesday morning killed 21 people, at least 17 of them foreign nationals who had come to India for medical treatment. It is the deadliest blaze the capital has witnessed since 2022, and it has forced an uncomfortable reckoning with the infrastructure that surrounds India's booming medical tourism industry.

The fire broke out at approximately 8:50 AM in the Lemon Green restaurant on the ground floor of the building, which housed the Flourish Stay bed-and-breakfast on its upper floors. Flames raced upward through the structure, smoke-locking several floors and trapping dozens of guests. Delhi Fire Services dispatched 10 to 12 fire tenders. Rescue crews pulled at least 40 people from the building, including three from the basement, but for many, the response came too late.

## The Victims Were Not Tourists

What makes this tragedy particularly devastating is who the victims were. Most of the foreign nationals killed — citizens of Bangladesh, Nigeria, Liberia, Kenya, Cameroon, and Mozambique — were not visiting Delhi for leisure. They were staying at the budget hotel because it sat within walking distance of Max Hospital and other major medical facilities in the area. They were patients' companions: husbands, mothers, and children who had travelled to India because their own countries' health systems could not treat their loved ones.

India's medical tourism industry, valued at an estimated $9 billion, draws hundreds of thousands of patients each year from Africa, South Asia, and the Middle East. Delhi, along with Chennai and Mumbai, is a primary hub. The hotels, guest houses, and bed-and-breakfasts that cluster around major hospitals are a critical part of this ecosystem, providing affordable accommodation for families who often spend weeks or months waiting through treatment cycles.

The fire has exposed the gap between the scale of this industry and the safety standards enforced at its margins. The Flourish Stay, according to initial reports, may have been operating beyond its licensed capacity. Whether it held a valid fire No Objection Certificate is now a central question in the criminal investigation.

## Political Fallout and a Promised Crackdown

Prime Minister Narendra Modi expressed his condolences on X, calling the loss of lives "tragic" and saying authorities were providing all possible assistance. External Affairs Minister S. Jaishankar confirmed that the Ministry of External Affairs was in direct contact with the embassies of Bangladesh, Nigeria, Liberia, and other affected nations, extending consular assistance.

The Delhi government moved quickly to announce a city-wide crackdown on guest houses and commercial establishments operating in violation of fire safety norms and building by-laws. The Chief Minister's office said non-compliant premises would be sealed and their operators prosecuted. Delhi Police have lodged a criminal case under culpable homicide provisions and arrested the building owner, identified as Lokesh Bajaj. Investigators are examining whether his group operates other properties with similar violations.

## A Recurring Pattern

Delhi's fire safety record is grim. The Anaj Mandi fire in 2019 killed 43 workers in an illegal factory. A fire in a children's hospital in 2017 killed six newborns. After each tragedy, authorities announce sweeping inspections and crackdowns. Compliance improves briefly, then fades. The structural problem — a city where millions of commercial establishments operate in buildings never designed for their current use — remains unaddressed.

For the Indian diaspora and the families across Africa and South Asia who rely on India's hospitals, the Malviya Nagar fire is a warning that the country's medical infrastructure extends beyond the gleaming hospital lobbies. It includes the buildings where patients' families sleep, eat, and wait. Those buildings, for now, remain largely unregulated.

Max Healthcare's Medical Director, Dr Sandeep Budhiraja, said eight survivors remained on ventilator support. Most suffered severe smoke inhalation rather than burns. Several patients had fractured bones after jumping from upper floors to escape the flames.

*Sources: Reuters, Livemint, Dainik Jagran, NDTV, India Today*"""

    caption = "Rescue operations underway after a fire at a hotel in Delhi's Malviya Nagar killed 21 people"
    
    article = {
        "headline": "A Fire in a Delhi Hotel Killed 21 People. Most Were Foreigners Who Came to India for Medical Care.",
        "subheadline": "The Malviya Nagar blaze has exposed the dangerous gap between India's booming medical tourism industry and the unregulated guest houses that surround its hospitals.",
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url or "",
        "image_caption": caption if img_url else "",
        "image_attribution": img_attr or "",
        "is_editorial": False,
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Livemint", "url": "https://www.livemint.com"},
            {"name": "Dainik Jagran", "url": "https://english.dainikjagranmpcg.com"},
            {"name": "NDTV", "url": "https://www.ndtv.com"},
            {"name": "India Today", "url": "https://www.indiatoday.in"}
        ]
    }
    
    print(f"\n📝 Inserting: {article['headline'][:60]}...")
    return insert_article(article)


# ============================================================
# ARTICLE 2: OECD Warns on Hormuz
# ============================================================
def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: OECD Warns on Hormuz Closure")
    print("="*60)
    
    slug = "oecd-warns-hormuz-closure-global-recession-india-asia-hardest-hit-20260604"
    
    print("\n📸 Sourcing image...")
    img_url, img_attr = source_image(
        slug,
        person_name="Mathias Cormann",
        search_terms=["OECD headquarters Paris 2026", "Strait of Hormuz oil tanker"],
        pexels_queries=["oil tanker ocean shipping", "global economy stock market"]
    )
    
    body = """The Organisation for Economic Co-operation and Development has issued its starkest warning yet on the Iran war's economic fallout: if the Strait of Hormuz is not reopened within a month, the world faces a prolonged slowdown that could push multiple economies into recession by 2027. For India, the third-largest oil importer on the planet, the forecast is a direct threat to the growth story its government has spent a decade building.

The OECD's Economic Outlook, released on Wednesday, models two scenarios. Under the first — a time-limited disruption where Gulf energy production begins recovering by the third quarter of this year — global growth slows from 3.4 percent in 2025 to 2.8 percent in 2026 before rebounding to 3.1 percent next year. Under the second scenario, where the strait remains effectively closed, growth drops to 2.1 percent this year and plunges to 1.8 percent in 2027. That would be the weakest global expansion outside of the COVID-19 pandemic and the 2008 financial crisis.

## Asia Bears the Heaviest Burden

The OECD's report makes clear that the damage is not evenly distributed. Asian economies that depend on crude oil and liquefied natural gas from the Persian Gulf are the hardest hit. India, which sourced more than 40 percent of its crude imports through the Strait of Hormuz before the war, has seen its energy costs surge since the strait's closure in late February. Brent crude remains near $96 a barrel, a level that erodes corporate margins, pressures the rupee, and feeds directly into consumer prices.

"The global economy entered 2026 with robust momentum, but the outlook has weakened significantly since the start of the conflict in the Middle East, with effects likely to be felt for some time," said OECD Secretary-General Mathias Cormann. "The longer the disruptions last, the larger the economic and social costs become."

The warning comes one day before the Reserve Bank of India announces its rate decision. A Reuters poll shows most economists expect the RBI to hold its key rate at 5.25 percent on Friday, but the consensus is shifting toward a hike later this year. Standard Chartered has already called for a 25 basis-point increase at this meeting itself. The central bank is caught between supporting growth in a slowing economy and containing inflation that is now driven by forces entirely outside its control.

## India's Scramble for Alternatives

New Delhi has not been passive. Prime Minister Modi's five-nation European tour, which concluded this week, was widely understood as an energy diversification mission wrapped in diplomatic protocol. India has deepened ties with Venezuela — now its fourth-largest oil supplier — and signed a new trade pact with Oman that offers a partial bypass of the Hormuz chokepoint. The government scrapped capital gains tax on foreign investment in government bonds this week, a move designed to stem the rupee's decline and attract capital inflows.

But these are tactical responses to a structural crisis. The OECD's numbers make clear that no amount of bilateral deal-making can fully compensate for the loss of 13.5 percent of global oil supply. The Persian Gulf's production has fallen by 45 percent since the strait's closure, and Iran's Revolutionary Guard continues to assert control over passage through the waterway.

## The Clock Is Ticking

The OECD effectively set a June deadline for meaningful progress. If energy production and shipping from the Gulf begin normalising this month, the economic damage remains manageable. If they do not, the organisation warned, the consequences cascade: higher energy costs feed into food prices, manufacturing slows, and poorer nations where households spend larger shares of income on fuel and food face the steepest decline in living standards.

For India's 1.8 million NRIs in the Gulf states — many of whom have already been affected by the regional economic contraction — the OECD report adds urgency to an already precarious situation. Remittances from the Gulf, which account for a significant share of India's $125 billion annual remittance inflows, are under pressure as construction, hospitality, and logistics sectors in the region contract.

The negotiations between the United States and Iran over the war's terms remain stalled. Iran suspended talks on June 1, ostensibly over Israeli operations in Lebanon. The IRGC continues to enforce its claim over the strait. The OECD's one-month window is not a diplomatic guideline. It is an economic warning with a hard deadline.

*Sources: OECD Economic Outlook, Reuters, AP, New York Post, Wall Street Next*"""

    caption = "OECD Secretary-General Mathias Cormann at a press conference"
    
    article = {
        "headline": "The OECD Just Gave the World One Month to Reopen the Strait of Hormuz. India Cannot Afford to Wait.",
        "subheadline": "Global growth could fall to levels not seen since the 2008 crisis if Gulf energy supplies remain cut off. Asian economies, including India, are in the direct line of fire.",
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url or "",
        "image_caption": caption if img_url else "",
        "image_attribution": img_attr or "",
        "is_editorial": False,
        "sources": [
            {"name": "OECD Economic Outlook", "url": "https://www.oecd.org/economic-outlook/"},
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "AP", "url": "https://apnews.com"},
            {"name": "New York Post", "url": "https://nypost.com"},
            {"name": "Wall Street Next", "url": "https://wsnext.com"}
        ]
    }
    
    print(f"\n📝 Inserting: {article['headline'][:60]}...")
    return insert_article(article)


# ============================================================
# ARTICLE 3: Calcutta HC ChatGPT
# ============================================================
def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: Calcutta HC ChatGPT Ruling")
    print("="*60)
    
    slug = "calcutta-high-court-chatgpt-originator-not-intermediary-indiamart-openai-20260604"
    
    print("\n📸 Sourcing image...")
    img_url, img_attr = source_image(
        slug,
        search_terms=["Calcutta High Court building", "Kolkata High Court"],
        pexels_queries=["artificial intelligence technology law", "AI robot judge gavel"]
    )
    
    body = """The Calcutta High Court has ruled, in what may become one of the most consequential technology decisions in Indian jurisprudence, that ChatGPT is not an intermediary under the Information Technology Act. It is an originator — a generator of content, not a conduit for it. The distinction sounds technical. Its implications are enormous.

The ruling came in a case filed by IndiaMart InterMesh Limited, the B2B e-commerce platform, against OpenAI. IndiaMart alleged that ChatGPT was systematically excluding its listings from AI-generated responses while continuing to surface its competitors. The company argued that OpenAI's tool qualified as an intermediary under Section 2(1)(w) of the IT Act, which would subject it to the obligations and safeguards of the Information Technology (Intermediaries Guidelines) Rules, 2021.

Justice Ravi Krishan Kapur disagreed. In a judgment that acknowledged the legal framework's limitations, he noted that the IT Act "was drafted long before the advent of generative AI and its definition reflects a world where only humans or legal entities could originate messages." ChatGPT, the court held, does not merely relay or store information in the way a search engine, a social media platform, or a web hosting service does. It synthesises, generates, and creates responses. That makes it an originator, not an intermediary.

## Why the Classification Matters

Under the IT Act, intermediaries — platforms like Google Search, Facebook, or Amazon — enjoy a "safe harbour" protection. They are generally not liable for the content that flows through them, provided they follow prescribed guidelines. This safe harbour has been the legal bedrock on which India's digital economy operates.

If ChatGPT is not an intermediary, it does not get that protection. Every response it generates could, in principle, be treated as content it authored. Every factual error, every omission, every instance of bias in its outputs could create direct liability for OpenAI. For a tool that processes millions of queries daily, this is a fundamentally different legal exposure than what traditional tech platforms face.

The ruling also means that the IT Intermediaries Guidelines — which impose obligations around content moderation, grievance redressal, and transparency — do not automatically apply to generative AI platforms. This creates a regulatory gap. India does not yet have a dedicated AI governance framework, and the IT Act, written in 2000, was never designed to address technology that creates content rather than hosting or transmitting it.

## IndiaMart's Commercial Grievance Remains Unresolved

While the court's classification of ChatGPT grabbed the legal world's attention, IndiaMart's core complaint — that it was being unfairly excluded from AI-generated responses — received a more measured treatment. In an earlier hearing in December 2025, Justice Kapur had noted a "strong prima facie case" of selective discrimination, observing that IndiaMart appeared to have been excluded "without any logic" while rival platforms continued to appear in ChatGPT's outputs.

The court found that OpenAI had relied on reports from the United States Trade Representative that named IndiaMart, without conducting an independent assessment. India's own Ministry of Consumer Affairs has clarified that such USTR reports are not binding.

However, the court declined to grant interim relief, reasoning that such an order would effectively amount to a final decree without hearing OpenAI fully. The case proceeds to a full trial, where technical evidence and expert testimony will determine the final classification.

## What This Means for the Indian Tech Ecosystem

The IndiaMart case is a preview of conflicts that will multiply as AI tools increasingly mediate how businesses are discovered, ranked, and recommended. When a search engine omits a listing, the business can at least point to published ranking factors and appeal through established channels. When an AI tool does it, the process is opaque, the reasoning is unknown, and the business may never know it has been excluded.

For India's millions of small and medium enterprises that increasingly rely on digital discovery — and for the diaspora entrepreneurs who use these platforms to source suppliers and partners — the stakes are high. The Calcutta High Court has opened a door. Whether India's Parliament walks through it with a comprehensive AI governance framework remains to be seen.

*Sources: SCC Times, LiveLaw, Inc42, Tax Concept*"""

    caption = "The Calcutta High Court, where Justice Ravi Krishan Kapur issued the landmark AI classification ruling"
    
    article = {
        "headline": "An Indian Court Just Ruled That ChatGPT Is Not an Intermediary. It Is a Creator.",
        "subheadline": "The Calcutta High Court's classification of generative AI as an 'originator' under the IT Act strips it of safe-harbour protection and opens a legal frontier India has no framework to govern.",
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url or "",
        "image_caption": caption if img_url else "",
        "image_attribution": img_attr or "",
        "is_editorial": False,
        "sources": [
            {"name": "SCC Times", "url": "https://scconline.com"},
            {"name": "LiveLaw", "url": "https://www.livelaw.in"},
            {"name": "Inc42", "url": "https://inc42.com"},
            {"name": "Tax Concept", "url": "https://taxconcept.net"}
        ]
    }
    
    print(f"\n📝 Inserting: {article['headline'][:60]}...")
    return insert_article(article)


if __name__ == '__main__':
    print("="*60)
    print("THE VIDESHI — News Writer Run v2")
    print(f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("="*60)
    
    results = []
    
    a1 = write_article_1()
    results.append(("Delhi Hotel Fire", a1))
    time.sleep(1)
    
    a2 = write_article_2()
    results.append(("OECD Hormuz Warning", a2))
    time.sleep(1)
    
    a3 = write_article_3()
    results.append(("ChatGPT Calcutta HC", a3))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for title, art_id in results:
        status = "✓ Published" if art_id else "✗ Failed"
        print(f"  {status}: {title} ({art_id or 'N/A'})")
    
    success = sum(1 for _, a in results if a)
    failed = sum(1 for _, a in results if not a)
    print(f"\nTotal: {success} published, {failed} failed")
