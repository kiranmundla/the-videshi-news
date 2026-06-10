#!/usr/bin/env python3
"""
News writer for The Videshi — June 10, 2026
Two articles:
1. Modi becomes India's longest-serving elected PM (4,399 days)
2. US court strikes down $100,000 H-1B visa fee
"""

import json, os, sys, uuid, io, requests
from datetime import datetime, timezone
from PIL import Image

# Load env
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v

load_env('~/.env.supabase')
load_env('~/workspace/.env.pexels')

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

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

def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage bucket article-images"""
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
        print(f"  ✓ Uploaded {filename} ({len(img_bytes)} bytes) → {public_url[:80]}...")
        return public_url
    else:
        print(f"  ✗ Upload failed: {r.status_code} {r.text[:200]}")
        return None

def download_image(url):
    """Download image with proper User-Agent"""
    r = requests.get(url, headers=UA, timeout=15)
    if r.status_code == 200 and r.headers.get('Content-Type', '').startswith('image'):
        return r.content
    print(f"  ✗ Download failed: {r.status_code} for {url[:80]}")
    return None

def insert_article(article):
    """Insert article into Supabase"""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=20
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data['id']
        print(f"  ✓ Inserted article: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

# ═══════════════════════════════════════════════════
# ARTICLE 1: Modi becomes India's longest-serving elected PM
# ═══════════════════════════════════════════════════
print("\n" + "="*60)
print("ARTICLE 1: Modi — Longest-Serving Elected PM")
print("="*60)

slug1 = "modi-longest-serving-elected-prime-minister-surpasses-nehru-4399-days-20260610"

# Source image: Wikipedia official portrait
print("\nSourcing image...")
modi_img_url = "https://upload.wikimedia.org/wikipedia/commons/5/5f/The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg"
modi_img_bytes = download_image(modi_img_url)
modi_final_url = None
if modi_img_bytes:
    compressed = compress_image(modi_img_bytes)
    print(f"  Compressed: {len(modi_img_bytes)} → {len(compressed)} bytes")
    modi_final_url = upload_to_supabase(compressed, f"{slug1}.jpg")

body1 = """Narendra Modi has officially become India's longest-serving continuously elected Prime Minister, completing 4,399 consecutive days in office on June 10, 2026 — one more than the 4,398 days served by Jawaharlal Nehru after India's first general election in 1952.

The milestone lands one day after Modi marked the 12th anniversary of his first swearing-in, and two years into his unprecedented third consecutive term. No Indian prime minister has held the office through three unbroken democratic mandates.

## A Record Built on Three Consecutive Mandates

Modi first took office on May 26, 2014, after leading the BJP to a landslide 282-seat majority — the first single-party majority in three decades. He returned in 2019 with an even larger margin of 303 seats, and in 2024 secured a third term at the head of a coalition government.

Nehru, India's first elected Prime Minister, served 4,398 days from May 13, 1952 to May 27, 1964. His earlier stint from 1947 to 1952 is typically excluded from the comparison, as he led an interim government before elections were institutionalised. Indira Gandhi served longer in total — over 14 years — but her tenure was interrupted when she was voted out in 1977 after the Emergency.

Including his nearly 13-year stint as Chief Minister of Gujarat from October 2001 to May 2014, Modi has led an elected government for more than 8,900 days — the longest of any head of government in India's history.

## Congratulations Pour In From Delhi to Washington

Union Parliamentary Affairs Minister Kiren Rijiju said Modi's contributions would be "etched in golden letters" in history, crediting his leadership for steering the country toward the vision of a "Viksit Bharat."

US Senator John Cornyn, co-chair of the Senate India Caucus, called Modi's tenure "nothing short of transformational." In a post on X, Cornyn wrote: "From lifting 250 million out of poverty to making India the world's fastest-growing major economy, PM Modi's tenure has been nothing short of transformational. The US-India partnership has never been stronger."

The National Democratic Alliance convened a high-level meeting at Bharat Mandapam in New Delhi on Wednesday to mark the occasion. Chief ministers, deputy chief ministers, and senior leadership from all 22 NDA-ruled states and Union Territories attended, along with Defence Minister Rajnath Singh and Home Minister Amit Shah.

## What This Means for the Diaspora

For the roughly 5.4 million Indian Americans and the broader NRI community worldwide, Modi's long tenure has meant a fundamental shift in how India engages with its diaspora. Under his watch, India introduced dual citizenship provisions, expanded the Overseas Citizen of India framework, and made diaspora engagement a centrepiece of foreign policy — from the "Howdy, Modi!" rally in Houston to the "Bharat Ki Baat" global outreach.

His three terms have also coincided with a deepening US-India strategic partnership, expanded defence cooperation, and tech-sector linkages that have directly benefited Indian professionals abroad. The proposed semiconductor fabs, the iCET technology initiative, and the growing defence trade pipeline all accelerated during this period.

## The Road Ahead

Modi's record will continue to grow with each passing day. His current term runs until 2029, and he has shown no signs of slowing. The NDA meeting at Bharat Mandapam on Wednesday was expected to outline the government's roadmap for the remaining three years of its third term.

The milestone also reignites questions about succession within the BJP, a party that has been defined by Modi's dominance for over a decade. For now, the focus remains on governing through an economic environment shaped by the Iran conflict, rising oil prices, and the challenge of an El Niño-weakened monsoon.

Whether history judges the 4,399 days kindly will depend on what comes next. The record has been set. The question is what Modi does with the mandate that made it possible."""

article1 = {
    "headline": "Modi Has Now Served Longer Than Nehru. No Elected Indian PM Has Lasted This Long.",
    "subheadline": "With 4,399 consecutive days in office, Narendra Modi surpasses Jawaharlal Nehru's post-independence record — the first PM to hold power through three unbroken democratic mandates.",
    "body": body1,
    "slug": slug1,
    "category": "news",
    "status": "review",
    "is_editorial": False,
    "image_url": modi_final_url or "",
    "image_caption": "Official portrait of Prime Minister Narendra Modi, now India's longest-serving continuously elected PM",
    "image_attribution": "Wikimedia Commons",
    "vertical": "news",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com"},
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "PTI via Swadesi", "url": "https://www.swadesi.com"},
        {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com"}
    ]),
    "published_at": datetime.now(timezone.utc).isoformat()
}

print("\nInserting article 1...")
art1_id = insert_article(article1)

# ═══════════════════════════════════════════════════
# ARTICLE 2: US court strikes down $100K H-1B fee
# ═══════════════════════════════════════════════════
print("\n" + "="*60)
print("ARTICLE 2: US Court Strikes Down $100K H-1B Fee")
print("="*60)

slug2 = "us-court-strikes-down-100000-h1b-visa-fee-trump-indian-tech-workers-20260610"

# Source image: Wikimedia Commons H-1B visa image
print("\nSourcing image...")
# Use the H-1B Visa Updates image from Wikimedia Commons
h1b_img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/H-1B_Visa_Updates.jpg/1200px-H-1B_Visa_Updates.jpg"
h1b_img_bytes = download_image(h1b_img_url)
h1b_final_url = None
if h1b_img_bytes:
    compressed = compress_image(h1b_img_bytes)
    print(f"  Compressed: {len(h1b_img_bytes)} → {len(compressed)} bytes")
    h1b_final_url = upload_to_supabase(compressed, f"{slug2}.jpg")

# If Wikimedia image failed, try Pexels for "US visa passport"
if not h1b_final_url:
    print("  Trying Pexels fallback...")
    pexels_key = os.environ.get('PEXELS_API_KEY', '')
    if pexels_key:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": pexels_key},
            params={"query": "US visa stamp passport immigration", "per_page": 3},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get('photos', [])
            if photos:
                pexels_url = photos[0]['src']['large2x']
                pexels_bytes = download_image(pexels_url)
                if pexels_bytes:
                    compressed = compress_image(pexels_bytes)
                    h1b_final_url = upload_to_supabase(compressed, f"{slug2}.jpg")

body2 = """A US federal judge has struck down the $100,000 fee that the Trump administration imposed on new H-1B visa applications, ruling it an unlawful tax that Congress never authorised. The decision, handed down on Monday by US District Judge Leo Sorokin in Massachusetts, is the most significant legal setback yet for the administration's campaign to restrict skilled immigration through executive action.

For Indian professionals — who account for more than 70 per cent of all H-1B visas issued — the ruling removes what had become the single largest financial barrier to working in the United States.

## What the Court Actually Said

Judge Sorokin was unsparing. He found that the $100,000 fee, introduced through a presidential proclamation in September 2025, functioned as a tax regardless of how the administration described it. Since only Congress has the power to impose taxes, the fee was struck down as unconstitutional.

Before the proclamation, employers typically paid between $2,000 and $5,000 in government filing fees to sponsor an H-1B worker. The hundred-fold increase had effectively priced out smaller companies, universities, hospitals, and research institutions from sponsoring foreign talent.

The lawsuit was brought by a coalition of 20 Democratic state attorneys general, who argued that the fee exceeded presidential authority under the Immigration and Nationality Act. Sorokin agreed, writing that the "substance and application" of the payment left no room for interpretation.

## The Backstory: Jaishankar, Rubio, and Quiet Diplomacy

The fee had triggered alarm bells far beyond American courtrooms. In May, India's External Affairs Minister S. Jaishankar raised the issue directly with US Secretary of State Marco Rubio during what was described as a sensitive bilateral discussion. Rubio acknowledged that the administration's immigration overhaul was creating "some difficulties" but insisted it was not designed to target India specifically.

Behind the scenes, India's IT industry — whose top firms collectively hold thousands of H-1B petitions annually — had been lobbying aggressively. The fee threatened to upend a business model built on deploying Indian engineers to American clients, and companies like TCS, Infosys, and Wipro had begun modelling scenarios where they would absorb or pass through the cost.

## Relief, but Not the End of the Story

Indian diaspora groups welcomed the ruling with cautious optimism. Khanderao Kand of the Foundation for India and Indian Diaspora Studies said the decision "restores predictability and fairness to the employment-based immigration system" and preserves America's competitive advantage in technology, healthcare, and advanced manufacturing.

But Sanjeev Joshipura of Indiaspora struck a more measured tone. "All stakeholders connected with H-1B visas will heave a sigh of relief after the court order, but one wonders if this is truly the end of the matter," he told PTI. He warned that the administration could still impose procedural hurdles that do not technically violate the law.

That caution is well-placed. The $100,000 fee was only one piece of a broader immigration overhaul. The Department of Homeland Security has already scrapped the old random lottery system for H-1B selection, replacing it with a salary-based merit model that took effect in February 2026. Duplicate petition filing — where companies submit multiple applications for the same worker to game the odds — is now classified as fraud.

## What Indian Workers Should Know Right Now

The ruling is effective immediately, meaning the $100,000 fee is no longer in force. However, the administration is expected to appeal. In the interim, here is what matters:

Employers who were holding back on H-1B sponsorship due to cost can resume filing without the surcharge. The standard filing fees of $2,000 to $5,000 remain in place. The merit-based selection system is unaffected by this ruling — salary and qualifications still determine selection priority.

For the roughly 300,000 Indian H-1B holders currently in the United States, the immediate impact is on renewals and employer changes rather than existing status. For the hundreds of thousands waiting in India for their chance, the path just got a little less expensive — though not necessarily shorter.

The broader fight over skilled immigration is far from settled. Trump told reporters on Tuesday that "these federal judges are really giving us a hard time," signalling that the administration sees this as a battle, not a concession. The next move will likely come from the appeals court."""

article2 = {
    "headline": "A Federal Judge Just Killed the $100,000 H-1B Fee. Every Indian Worker in America Should Read the Fine Print.",
    "subheadline": "The Trump administration's most aggressive move against skilled immigration has been struck down as an unlawful tax — but the administration is expected to appeal, and the broader overhaul is far from over.",
    "body": body2,
    "slug": slug2,
    "category": "news",
    "status": "review",
    "is_editorial": False,
    "image_url": h1b_final_url or "",
    "image_caption": "H-1B visa programme updates — the court ruled the $100,000 fee exceeded presidential authority",
    "image_attribution": "Wikimedia Commons",
    "vertical": "immigration",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "PeopleMatters", "url": "https://www.peoplematters.in"},
        {"name": "Livemint", "url": "https://www.livemint.com"},
        {"name": "Connected to India", "url": "https://www.connectedtoindia.com"},
        {"name": "ainvest.com", "url": "https://www.ainvest.com"}
    ]),
    "published_at": datetime.now(timezone.utc).isoformat()
}

print("\nInserting article 2...")
art2_id = insert_article(article2)

# ═══════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Article 1: {'✓' if art1_id else '✗'} Modi longest-serving PM")
print(f"  Slug: {slug1}")
print(f"  Image: {'✓' if modi_final_url else '✗'}")
print(f"Article 2: {'✓' if art2_id else '✗'} H-1B $100K fee struck down")
print(f"  Slug: {slug2}")
print(f"  Image: {'✓' if h1b_final_url else '✗'}")
print(f"\nBoth articles inserted with status='review' and is_editorial=False")
