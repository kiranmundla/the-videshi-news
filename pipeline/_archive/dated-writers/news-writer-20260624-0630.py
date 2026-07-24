#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (06:30 UTC run)
2 NEW articles, distinct from all prior runs (Jio IPO, sovereign-AI, monsoon,
seafarers, NSE IPO, Iran sanctions, RBI NRI deposits, FII flows, trade-deal, etc.):
  1. India opens its nuclear sector to private and foreign capital under the
     SHANTI Act (2025) — govt eyeing ~$26B private investment, up to 49% FDI,
     $214B market opportunity toward 100 GW by 2047. Energy/economy + diaspora
     investor & clean-energy angle.
  2. Indian Embassy in UAE pauses passport/visa/attestation services June 26-30
     as Al Hind Tours replaces BLS/SGIVS from July 1. Diaspora-safety/consular
     service story for ~3.5M Indians in the UAE.
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

UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error: {e}")
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


def pick_commons(queries, min_width=900):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            return pick["url"], pick.get("title", "")
    return None, ""


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


# ─── Article 1: India opens nuclear sector to private/foreign capital ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India opens nuclear sector to private capital")
    print("="*60)

    slug = "india-nuclear-sector-private-foreign-investment-shanti-act-100gw-diaspora-20260624"
    headline = "After Six Decades, India Is Letting Private Money Into Its Nuclear Plants"
    subheadline = "A landmark law has ended the state monopoly on atomic power, opening the sector to private operators and up to 49% foreign investment. New Delhi is chasing roughly $26 billion in private capital and a 100-gigawatt target — and a diaspora hungry for both clean-energy bets and a stake in India's rise is squarely in the frame."

    body = """For sixty years, building and running a nuclear power plant in India was a job reserved for the government and no one else. The Atomic Energy Act of 1962 drew a hard line around the sector, and a 2010 liability law made foreign partnerships nearly impossible by saddling equipment suppliers with open-ended risk. That era is now over. With the SHANTI Act — the Sustainable Harnessing and Advancement of Nuclear Energy for Transforming India Act, passed in December 2025 — private companies can, for the first time, be licensed to build, own and operate nuclear reactors, and foreign investors can take stakes of up to 49 percent.

This week the scale of the ambition came into focus. Industry estimates now put the opening at a market opportunity worth more than $214 billion as India races toward a target of 100 gigawatts of installed nuclear capacity by 2047, and the government is courting around $26 billion in private investment to help get there. For context, India's nuclear fleet today generates only about 8.8 gigawatts — so the country is talking about expanding more than tenfold within a generation.

## What the New Law Actually Changes

The SHANTI Act repeals both the 1962 Atomic Energy Act and the 2010 Civil Liability for Nuclear Damage Act, replacing six decades of state monopoly with a single modern statute. It grants statutory authority to the Atomic Energy Regulatory Board, sets up licensing and safety oversight, and — crucially for investors — restructures the liability rules that had scared off capital. Operator liability is now capped at up to 30 billion rupees for large reactors, with the central government covering damages beyond that through a Nuclear Liability Fund.

Private firms can now participate across the chain: fuel-cycle activities, equipment manufacturing, power generation, and even plant operations, all under license. The 49 percent foreign-investment ceiling is designed to bring in not just money but technology and research partnerships — the kind of know-how that the state-owned Nuclear Power Corporation of India (NPCIL), which has long been the sole builder and operator, cannot scale fast enough on its own.

## Why Now

The timing is deliberate. The 100-gigawatt target is simply too large for NPCIL to hit alone, and India needs vast quantities of reliable, low-carbon electricity to power its data centres, factories and cities without blowing past its climate commitments. Analysts say further rules and regulations still need to be written to operationalise the law, and the real test will be implementation — particularly whether the liability backstop holds up in practice. But the direction is unmistakable, and global players are circling. The United States has signalled interest in "joint innovation and R&D," and the sector's marquee gathering, the India Nuclear Business Platform, convened in Mumbai this month to connect investors and operators with policymakers.

## Why the Diaspora Should Care

For overseas Indians, this is a rare chance to participate in one of the country's biggest long-term infrastructure stories from the ground floor. Clean energy is exactly the kind of patient, decades-long bet that diaspora capital — through funds, foreign partners and direct investment routes — is well placed to make, and the sector has just been thrown open to it for the first time. Many NRIs work in the global nuclear, engineering and clean-tech industries, from reactor design to project finance, and the opening creates a natural bridge for that expertise to flow home.

There is a strategic dimension, too. A diaspora that worries about India's dependence on imported energy — and watched the recent Strait of Hormuz crisis send oil prices and anxiety spiking — has reason to welcome a homegrown push toward energy security. Nuclear power that is partly built with global capital and technology, but owned and regulated in India, fits the same instinct now driving the country's parallel drives into sovereign artificial intelligence and domestic manufacturing: build at home, but welcome the world's money and know-how to do it faster.

## What's Next

Expect a wave of detailed regulations, the first private licensing rounds, and a scramble among Indian conglomerates and foreign reactor-makers to form joint ventures. Whether India can turn a bold law into actual concrete-and-steel reactors — and hit even a fraction of its 100-gigawatt goal — will be one of the defining tests of its energy decade. For a diaspora looking to back India's future with more than remittances, the door to its atomic ambitions has, after sixty years, finally been opened."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing hero image (nuclear power plant / energy)...")
    img_url, ctitle = pick_commons([
        "nuclear power plant India Kudankulam",
        "Kudankulam Nuclear Power Plant",
        "nuclear power plant cooling towers",
        "nuclear reactor power station",
        "nuclear power plant"
    ])
    img_caption = "A nuclear power station; India's SHANTI Act has opened the sector to private operators and foreign investment for the first time"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("nuclear power plant cooling towers")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A nuclear power plant; India is opening atomic energy to private and foreign capital"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Law.asia (law.asia, June 2026) \u2014 'India sees the light on private participation in the nuclear energy sector': For six decades India's nuclear sector was the exclusive preserve of the state under the Atomic Energy Act of 1962, reinforced by the Civil Liability for Nuclear Damage Act of 2010 which saddled suppliers with open-ended liability; the SHANTI Act (Sustainable Harnessing and Advancement of Nuclear Energy for Transforming India Act, 2025), introduced mid-December 2025, repeals both predecessor laws, grants statutory authority to the Atomic Energy Regulatory Board, restructures liability on terms acceptable to private capital, and lets licensed private operators build, own and run nuclear power plants for the first time; India has committed to 100 GW of nuclear capacity by 2047, a target too large for state-owned NPCIL alone.",
            "The Indian Eye (theindianeye.com, June 2026) \u2014 'India's Nuclear Market Opens To Private And Global Investment: Industry Leaders To Convene At INBP 2026 In Mumbai': Following the SHANTI Act passed December 2025, which capped operator liability and opened nuclear projects to up to 49% private and foreign equity, industry estimates place the market opportunity at more than USD 214 billion as India works toward 100 GW of installed nuclear capacity by 2047; the 7th India Nuclear Business Platform convened 16-17 June 2026 in Mumbai; private industry is now authorised for the first time to fund, build and operate nuclear assets.",
            "Livemint (livemint.com, 2026) \u2014 'US eyes joint innovation and R&D with India as SHANTI Act paves way for private players, FDI in nuclear sector': the new law opens space for private players in fuel cycle activities, equipment manufacturing, power generation and plant operations subject to oversight, and allows up to 49% FDI in certain nuclear activities; India's nuclear capacity stands at 8.78 GW, expected to rise above 22 GW by 2031-32; the government says the act supports India's clean-energy transition and 100 GW by 2047 goal.",
            "Lexology / Devdiscourse (lexology.com, devdiscourse.com, 2026) \u2014 SHANTI Act analysis and 'India needs green bonds, blended finance and export credit support for future-ready nuclear energy ecosystem': operator liability capped at up to INR 30 billion for large reactors with the Central Government covering excess damages via a Nuclear Liability Fund under Section 14; Section 15(1) requires operators to maintain insurance or financial security; the SHANTI Act enables private-sector participation subject to regulatory and licensing requirements and repealed the 1962 Atomic Energy Act and 2010 CLND Act; report notes further legal and regulatory reforms needed to unlock the sector's full potential toward the 100 GW by 2047 target."
        ]),
        "diaspora_angle": "The opening of India's nuclear sector gives overseas Indians a first-ever, ground-floor route into one of the country's biggest long-term infrastructure bets \u2014 a patient clean-energy play suited to diaspora capital, foreign partners and the many NRIs working in global nuclear, engineering and clean-tech \u2014 while answering a diaspora desire for Indian energy security after the recent Hormuz oil scare.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: UAE Indian consular services pause June 26-30 ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Indian Embassy UAE pauses passport/visa services")
    print("="*60)

    slug = "indian-embassy-uae-passport-visa-services-pause-june-26-30-al-hind-takeover-diaspora-20260624"
    headline = "Indians in the UAE Have a Five-Day Window to Sort Their Passports. Then Services Go Dark."
    subheadline = "The Indian Embassy is pausing all routine passport, visa and attestation work from June 26 to 30 as a new contractor, Al Hind Tours, replaces BLS and SGIVS from July 1. For the roughly 3.5 million Indians in the UAE \u2014 the country's largest expatriate community \u2014 the message is simple: file now, or wait until July."

    body = """For the roughly 3.5 million Indians who live and work in the United Arab Emirates, a routine but consequential piece of housekeeping is about to interrupt their paperwork. The Indian Embassy in Abu Dhabi has announced that all regular passport, visa and attestation services will pause for five days, from June 26 to June 30, as the mission switches the private contractor that runs its consular service centres.

The reason is a changing of the guard. The current outsourced providers — BLS International and SGIVS Global — will stop accepting new applications after June 25. From July 1, a new operator, Al Hind Tours and Travel LLC, takes over the processing of all passport, visa and consular applications across the country. The five-day gap in between is meant to let the embassy migrate consular data, move logistics and relocate service centres without creating errors or backlogs.

## What This Means If You Need a Document

The practical upshot is a hard deadline. Anyone who needs to renew a passport, apply for a visa, or get a document attested in the near term should submit their application before the close of business on June 25, while BLS and SGIVS are still accepting them. Applications filed before the cut-off will continue to be processed through the existing centres. Miss that window, and routine appointments will simply not be available until the new system goes live in July.

The embassy has stressed one point repeatedly: rely only on official channels for updates, and beware of misinformation during the transition. Details on the new service centre locations, operating hours, appointment procedures, fees and contact information are expected to be released before July 1.

## Emergencies Are Still Covered

Crucially, the pause applies to routine work, not genuine emergencies. During the five-day window, emergency consular services will be handled directly by the Embassy of India in Abu Dhabi and the Consulate General of India in Dubai. The embassy has published contact details for anyone who needs urgent help:

- Toll-free number: 800 46342
- WhatsApp: +971 54 309 0571
- Email: pbsk.dubai@mea.gov.in

So a traveller facing a real emergency — a lost passport before an urgent flight, a medical or family crisis back home — is not left stranded. But the ordinary business of renewals and fresh applications goes on hold.

## A Bigger Operation Than It Sounds

The handover is larger than a simple vendor swap. Al Hind Tours and Travel was selected after a formal tender and evaluation process by India's diplomatic missions in the UAE, and the company has indicated it plans to operate around 16 centres across the seven emirates. From July, it will offer the full range of services Indians abroad rely on: passport renewals, visas, Overseas Citizen of India (OCI) cards, Police Clearance Certificates, surrender certificates, Global Entry Program verification and document attestation. Applicants will use a dedicated online platform to book appointments and file applications, while the underlying procedures are expected to stay largely the same.

## Why the Diaspora Should Care

The UAE is home to India's single largest overseas community, and consular paperwork is the connective tissue of expatriate life. A passport renewal can determine whether a worker can keep a job or sign a tenancy; an attested certificate can decide a child's school admission or a spouse's visa; an OCI card governs how freely a person can travel back to India. A five-day blackout, even a planned one, ripples through thousands of households, and the families most exposed are often blue-collar workers with the least slack in their schedules and the most to lose from a delayed document.

For the wider diaspora, the switch is also a reminder of how much daily life abroad runs through a handful of outsourced service centres — and how a smooth handover, or a botched one, lands first on the people furthest from the embassy's front desk.

## What's Next

Expect the embassy and Al Hind to publish centre locations, hours and the new appointment portal ahead of the July 1 launch. Until then, the advice from the mission is unambiguous: if you have consular business in the UAE, get it filed before June 25 — or be ready to wait."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing hero image (passport / consular / UAE)...")
    img_url, ctitle = pick_commons([
        "Indian passport document",
        "passport application office counter",
        "Embassy of India Abu Dhabi",
        "passport stamp visa",
        "passport travel document"
    ])
    img_caption = "An Indian passport; consular services in the UAE pause June 26-30 during a contractor handover"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("passport application documents desk")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Passport and travel documents; Indian consular services in the UAE pause June 26-30"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "CurrentIndia.com / ThisDay (currentindia.com, thisday.com.ng, June 2026) \u2014 'Indian embassy in UAE to pause passport, visa services from June 26-30 ahead of Al Hind Tours takeover': The Indian Embassy in Abu Dhabi announced Al Hind Tours and Travel LLC will take over passport, visa and attestation services from July 1, 2026; current providers BLS International and SGIVS Global stop accepting new applications after June 25; no regular appointments June 26-30; emergency consular services during the window handled directly by the Embassy in Abu Dhabi and Consulate General in Dubai \u2014 toll-free 800 46342, WhatsApp +971 54 309 0571, email pbsk.dubai@mea.gov.in; applications submitted before the transition continue through existing centres.",
            "Madhyamam (madhyamamonline.com, June 2026) \u2014 'UAE: Al Hind to handle Indian passport, visa services from July 1': Al Hind Tours and Travels LLC takes over from July 1 through service centres across the country; BLS International and SGIVS Global continue until June 30; from July Al Hind will offer passport renewals, visas, OCI cards, Police Clearance Certificates, surrender certificates, Global Entry Program verification and document attestation; company plans to operate 16 centres across the UAE with a dedicated online appointment platform; procedures expected to remain largely unchanged; transition follows a tender by Indian missions in the UAE.",
            "Times Now World / Travel And Tour World (timesnowworld.com, travelandtourworld.com, June 22, 2026) \u2014 'India substitutes BLS and SGIVS with Al Hind for passport and visa services in the UAE, effective July 1': Embassy of India in Abu Dhabi announced the change after a tendering and evaluation process; applicants advised to use BLS/SGIVS until end of June and rely only on official websites and verified social media channels to avoid misinformation; the transition involves migrating consular databases, logistics and relocating service centres across the seven emirates."
        ]),
        "diaspora_angle": "The UAE hosts India's single largest overseas community of roughly 3.5 million people, so a planned five-day pause in passport, visa and attestation services \u2014 with a hard June 25 filing deadline before Al Hind Tours replaces BLS and SGIVS on July 1 \u2014 directly affects thousands of NRI households, especially blue-collar workers whose jobs, tenancies and family visas hinge on timely consular paperwork.",
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
