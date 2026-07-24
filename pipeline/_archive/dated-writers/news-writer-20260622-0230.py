#!/usr/bin/env python3
"""
Videshi News Writer — June 22, 2026 (02:30 UTC run)
2 NEW articles:
  1. India suspends UAE passport/visa/attestation services June 26-30 ahead of Al Hind takeover (nri-world / diaspora-services)
  2. India removes cough syrups from Schedule K — now prescription-only after contamination deaths (news / health-regulation)
"""

import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"


# ─── Image sourcing functions ────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
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
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
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
                if ii.get("width", 0) < 600:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  \u2713 Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  \u26a0 Download failed ({r.status_code}): {url[:80]}")
            try:
                tmp = f"/tmp/{slug}_src"
                subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
                with open(tmp, "rb") as f:
                    content = f.read()
                if len(content) < 5000:
                    return None
                r_content = content
            except Exception:
                return None
        else:
            r_content = r.content
        ct = r.headers.get("Content-Type", "") if r.status_code == 200 else "image/jpeg"
        if "image" not in ct and len(r_content) < 5000:
            print(f"  \u26a0 Not an image or too small: {ct}, {len(r_content)} bytes")
            return None

        from PIL import Image
        img = Image.open(io.BytesIO(r_content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()

        if len(compressed) < 5000:
            print(f"  \u26a0 Compressed image too small: {len(compressed)} bytes")
            return None

        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"

        requests.delete(upload_url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY
        })

        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=30)

        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ─── Article 1: UAE Indian consular services pause ───────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: UAE Indian consular services pause June 26-30")
    print("="*60)

    slug = "india-uae-passport-visa-attestation-services-pause-june-26-30-al-hind-takeover-20260622"
    headline = "India Is Switching Who Runs Its Visa Desks in the UAE. For Five Days at Month's End, the Lines Go Dark."
    subheadline = "From June 26 to 30, routine passport, visa and attestation appointments will stop across the Emirates as Al Hind Tours and Travel replaces BLS and SGIVS. The pause touches 3.5 million Indians — nearly 40 percent of the UAE's population."

    body = """For the largest Indian community anywhere outside India, a piece of bureaucratic housekeeping is about to become a five-day inconvenience with real consequences. The Embassy of India in Abu Dhabi has announced that routine passport, visa and attestation services across the United Arab Emirates will be suspended from June 26 to June 30, as the missions hand the work to a new outsourced provider.

The change is straightforward on paper. From July 1, Al Hind Tours and Travel LLC takes over as the outsourced partner handling Indian passport, visa and attestation services throughout the UAE, replacing the two incumbents: BLS International, which ran passport and visa work, and SGIVS Global, which handled attestation. Those existing providers will stop accepting new applications after the close of business on Thursday, June 25. In the gap between the old system shutting down and the new one switching on, no regular appointments will be available to the public.

The scale is what makes a routine handover matter. The Indian community in the UAE numbers roughly 3.5 million people — close to 40 percent of the country's entire population — and consular paperwork is a constant feature of expatriate life, from renewing a passport before it lapses to getting a degree or marriage certificate attested for a job or a school admission. Al Hind is preparing what has been described as a major operational overhaul to serve that community, with plans to open 16 dedicated centres across all seven emirates, including hubs in Abu Dhabi, Dubai and Fujairah.

For families whose documents are nearing expiry, the embassy's advice amounts to a deadline: submit before June 25, or wait until the new system opens on July 1. Applications filed before the transition date will continue to be processed through the existing centres, but anyone who misses that window and does not have an emergency will be left waiting out the five-day pause. For frequent travellers shuttling between Dubai, Abu Dhabi and Sharjah and Indian cities such as Mumbai, Delhi, Hyderabad, Chennai and Kochi, a passport that runs out during the blackout could mean a scramble.

Crucially, the missions have stressed that emergencies will not be left stranded. Emergency passport, visa and attestation services will continue throughout the suspension, handled directly by the Embassy of India in Abu Dhabi and the Consulate General of India in Dubai. Indian nationals needing urgent help during the transition can reach the missions through the toll-free number 800 46342 (800 INDIA), via WhatsApp on +971 54 309 0571, or by email at pbsk.dubai@mea.gov.in. On July 1, Al Hind will launch a new online appointment portal and formally assume responsibility for the services.

The embassy says Al Hind was chosen after a tendering and evaluation process, and that arrangements are being made to ensure a smooth handover while keeping essential services available across the UAE. The mission has urged the Indian community and other applicants to rely only on official channels for updates during the transition — a pointed reminder in a market where unofficial agents and middlemen have long preyed on expatriate workers needing paperwork done in a hurry.

For the diaspora, the episode is a small but telling reminder of how much daily life in the Gulf runs through the consular machinery of home. The UAE is the beating heart of the Indian expatriate experience — a place where remittances, family separations and the paperwork of belonging all converge on a handful of service windows. A change of contractor is, in one sense, invisible plumbing. But for a worker whose visa stamp must be renewed before a flight home, or a parent gathering attested documents for a child's overseas admission, the five days from June 26 are worth marking on the calendar.

The transition also signals the growing commercial stakes of serving the diaspora. Outsourced consular work for a community of millions is a substantial business, and the arrival of a new operator promising 16 centres across the Emirates underscores how the machinery of expatriate India keeps scaling to match its population abroad. Whether Al Hind's expanded footprint delivers shorter queues and smoother service will be the real test once July 1 arrives. For now, the message from the missions is simpler: get ahead of the pause, keep the emergency numbers handy, and trust only the official word."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    for q in ["Embassy of India Abu Dhabi", "Indian passport", "Consulate General of India Dubai", "Indian passport document"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "Indian consular services across the UAE will pause from June 26 to 30 during a change of outsourced provider"
            img_attribution = "Wikimedia Commons"
            break

    if not img_url:
        pex = fetch_pexels_image("passport documents office")
        if pex:
            img_url = pex
            img_caption = "Routine Indian passport and visa appointments in the UAE will be unavailable from June 26 to 30"
            img_attribution = "Pexels"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "diaspora-services",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "What's On (whatson.ae) — 'Indian passport and visa services in the UAE to pause for five days': Embassy of India in Abu Dhabi announced passport, visa and attestation services across the UAE will be suspended for five days at the end of June; from July 1, 2026, Al Hind Tours and Travel LLC becomes the new outsourced partner; current providers BLS International and SGIVS Global stop accepting new applications after business hours June 25; routine appointments unavailable June 26-30; emergency passport/visa/attestation support continues through Embassy Abu Dhabi and Consulate General Dubai; new online appointment platform goes live July 1",
            "News7tv / CurrentIndia — 'Indian Embassy in UAE to pause passport, visa services from June 26-30 ahead of Al Hind Tours takeover' (June 20, 2026): Al Hind selected after tendering and evaluation process; notice issued Friday; emergency contacts — toll-free 800 46342, WhatsApp +971 54 309 0571, email pbsk.dubai@mea.gov.in; applications submitted before transition processed through existing centres; from July 1 all new applications accepted through Al Hind centres",
            "The Gulf Gazette / Khaleej Times — 'Indian embassy in UAE to suspend regular consular appointments for 5 days': transition affects more than 3.5 million Indian expatriates in the UAE, nearly 40 percent of the UAE's population; Al Hind plans 16 dedicated centres across all seven emirates including Abu Dhabi, Dubai and Fujairah; BLS (passport/visa) and SGIVS Global (attestation) cease new applications from close of business June 25"
        ]),
        "diaspora_angle": "The UAE is home to roughly 3.5 million Indians — nearly 40 percent of the country's population — and the five-day consular blackout from June 26 directly affects anyone with a passport nearing expiry, a visa stamp pending, or documents to be attested for jobs and overseas admissions.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India cough syrup Schedule K amendment ───────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India cough syrup prescription-only Schedule K")
    print("="*60)

    slug = "india-cough-syrup-prescription-only-schedule-k-amendment-contamination-deaths-pharmacy-of-world-20260622"
    headline = "India Just Made Cough Syrup a Prescription Drug. The Backstory Is the Deaths of More Than 140 Children."
    subheadline = "A quiet amendment to a 1945 rulebook strips the word 'syrup' from the list of medicines that can be sold over the counter. Behind it lies a contamination scandal that battered India's standing as the 'pharmacy of the world'."

    body = """India has ended the over-the-counter sale of cough syrups, a regulatory shift that on its surface reads as dry administrative housekeeping but in fact closes a chapter on one of the most damaging public-health scandals to touch the country's pharmaceutical industry in years. Under a government notification, cough syrups have been removed from the exemption list that long allowed them to be sold as household remedies — meaning they can now be dispensed only through licensed pharmacies, increasingly against a doctor's prescription.

The mechanism is a small edit with large reach. Schedule K of the Drugs Rules, 1945, lists medicines exempted from the usual prescription requirements — everyday items such as aspirin, paracetamol tablets and analgesic balms. For decades, Entry 7 of that schedule permitted the sale of syrups, lozenges, pills and tablets for the relief of coughs without the controls applied to prescription drugs. The new amendment deletes the word "syrup" from that entry. Pills, tablets and lozenges remain exempt; liquid cough preparations no longer do, according to a government notification dated June 15. A separate Health Ministry statement said the sale and dispensing of cough syrups in smaller villages would now take place only through duly licensed pharmacies, in line with the Drugs and Cosmetics Act.

The practical change falls hardest on rural India. In cities, existing rules already required cough syrups to be sold only through registered pharmacies. But in smaller towns and villages — places with populations of no more than 1,000 and often no pharmacy at all — restricted retail licences had allowed ordinary vendors and non-pharmaceutical shops to sell the syrups straight off the shelf, frequently without any prescription. It was precisely this loosely supervised village trade that the amendment is designed to shut down. "The measure is expected to promote responsible distribution and sale of cough syrups while ensuring greater compliance with regulatory standards across the country," the Health Ministry said.

The reason for the crackdown is grim. Since 2022, cough syrups manufactured in India have been linked to the deaths of more than 140 children, in countries across Africa and Central Asia, after toxic industrial solvents — diethylene glycol (DEG) and ethylene glycol (EG) — were found in liquid oral formulations. Those chemicals can cause acute kidney failure and death. The contamination triggered World Health Organization alerts and dealt a heavy blow to India's hard-won reputation as the "pharmacy of the world," the low-cost supplier of generic medicines to much of the developing globe.

The crisis came home in October last year, when Coldrif syrup, made by Sresan Pharmaceutical, was linked to the deaths of 24 children in India itself, in cases concentrated in Rajasthan and Madhya Pradesh. State authorities cancelled the manufacturer's licences, halted production and arrested the company's owner. The episode forced a reckoning: a country that exports vast quantities of affordable medicine had to confront how lightly some of that medicine was regulated at home, particularly the small manufacturers who dominate the sector.

The prescription rule is one piece of a broader tightening. The Indian Pharmacopoeia Commission has updated standards for high-risk excipients — glycerin, propylene glycol, sorbitol and liquid maltitol — that can carry DEG impurities, and a draft National Formulary has moved to bar cough and cold medications for children under two and discourage them for those under five. Risk-based inspections have been launched across manufacturing units in multiple states. Critics, though, note that restricting who can buy a syrup does not by itself fix the deeper problem the scandal exposed: how the medicine is manufactured, tested and policed before it ever reaches a shelf.

For the diaspora, the story carries a particular resonance. India's pharmaceutical exports are a source of national pride and a lifeline for patients worldwide, and many NRIs stock up on familiar Indian-made medicines on trips home or have them sent by relatives. The contamination deaths abroad — and the slow, scandal-driven tightening of rules at home — speak directly to the question of whether "made in India" medicine can be trusted, a question that matters to Indian families on every continent. A prescription requirement on cough syrup will not, on its own, restore that trust. But it is a visible signal that the regulator has, however belatedly, decided that the era of buying these products like sweets off a village counter is over."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    for q in ["cough syrup bottle", "medicine syrup bottle", "pharmacy India medicines", "medicine bottles pharmacy"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "India has removed cough syrups from the over-the-counter exemption list, requiring sale through licensed pharmacies"
            img_attribution = "Wikimedia Commons"
            break

    if not img_url:
        pex = fetch_pexels_image("medicine syrup bottle pharmacy")
        if pex:
            img_url = pex
            img_caption = "Cough syrups in India must now be sold through licensed pharmacies after a rule change"
            img_attribution = "Pexels"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "health-regulation",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters — 'India limits cough syrup sales to pharmacies after contamination cases' (June 2026): India removed cough syrups from the Schedule K exemption list per a government notification dated June 15, while keeping pills, tablets and lozenges exempt; sale in smaller villages now only through duly licensed pharmacies under the Drugs and Cosmetics Act; restricted retail licences previously let vendors in towns/villages of up to 1,000 people sell syrups without prescription; since 2022 India-made cough syrups linked to deaths of more than 140 children in Africa and Central Asia; in October 2025 Sresan Pharmaceutical's Coldrif syrup linked to 24 child deaths; India's pharma industry aims for $130 billion value by 2030",
            "The Health Master — 'India Bans Over-the-Counter Cough Syrups Sales: Schedule K' (June 19, 2026): notification No. GSR 477(E) dated 09-06-2026 amends the Drugs Rules of 1945; Schedule K Entry 7 long permitted sale of syrups, lozenges, pills and tablets for cough relief without prescription; the amendment deletes the word 'syrup' from that entry, requiring a doctor's prescription for cough syrups",
            "PocketIAS / UPSC analysis — 'Syrup-Based Medicines and Doctor's Prescription' (June 19, 2026): government removed 'syrup' from Schedule K of the Drugs Rules, 1945; syrup-based medicines now prescription-only and sold only through licensed pharmacies; change follows a December 2025 draft notification; contamination since 2022 involved ethylene glycol and diethylene glycol, more than 300 child deaths reported across countries, WHO safety alerts in 2022 and 2023; Indian Pharmacopoeia Commission updated standards for high-risk excipients (glycerin, propylene glycol, sorbitol, liquid maltitol)"
        ]),
        "diaspora_angle": "India's role as the 'pharmacy of the world' is a point of national pride and a lifeline for patients globally; with many NRIs relying on familiar Indian-made medicines, the contamination deaths abroad and the scandal-driven tightening of rules at home speak directly to whether 'made in India' medicine can be trusted.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    print("\n" + "="*60)
    print(f"DONE. Inserted IDs: {[i for i in ids if i]}")
    print("="*60)
