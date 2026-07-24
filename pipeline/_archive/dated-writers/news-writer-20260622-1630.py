#!/usr/bin/env python3
"""
Videshi News Writer — June 22, 2026 (16:30 UTC run)
2 NEW articles:
  1. Kunal Shah (CRED founder) named global head of WhatsApp; Meta puts $900M into CRED (news / tech)
  2. Lucknow coaching-centre fire kills 14, mostly students (news / public-safety)
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


# ─── Article 1: Kunal Shah named global head of WhatsApp ─────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Kunal Shah named global head of WhatsApp")
    print("="*60)

    slug = "kunal-shah-cred-founder-whatsapp-global-head-meta-900-million-investment-diaspora-20260622"
    headline = "An Indian Founder Now Runs the App 500 Million Indians Use Every Day"
    subheadline = "Meta has handed WhatsApp to CRED's Kunal Shah and poured $900 million into his fintech startup. The bet is that a man who built a consumer app in India can finally crack what WhatsApp has never managed there: payments at scale."

    body = """For the better part of a decade, the most-used app in India has been run from California. On Monday that changed. Meta named Kunal Shah, the founder of the Bengaluru fintech CRED, as the global head of WhatsApp, handing one of the company's three-billion-user platforms to an Indian entrepreneur for the first time. The appointment landed alongside a $900 million Meta-led investment into CRED, the startup Shah built, and it reads less like a routine executive reshuffle than a statement of where Meta thinks WhatsApp's future will be won.

Shah succeeds Will Cathcart, who has run WhatsApp since 2019 and oversaw its expansion from a private messaging tool into a sprawling platform with Communities, Channels, business messaging and, more recently, AI features. Cathcart is not leaving the company; he is moving to a new role building consumer products powered by artificial intelligence. But the symbolism of the handover is hard to miss. India is WhatsApp's single largest market, with more than 500 million users — a sixth of the app's entire global base — and it is precisely the market where WhatsApp's biggest ambition, payments, has fallen short.

That ambition is the subtext of the whole deal. WhatsApp Pay launched in India with enormous structural advantages: the app sits on nearly every smartphone in the country, and India's UPI rails make digital payments effectively free and instant. Yet WhatsApp Pay has been comprehensively out-competed by PhonePe and Google Pay, which together dominate a market that processes billions of transactions a month. Meta is betting that Shah — who spent the past seven years building CRED into a fintech "super app" spanning credit-card bill payments, lending, UPI, insurance and investments — understands how to win Indian consumers' financial trust in a way a Silicon Valley product team has not.

The money makes the alignment concrete. Meta's roughly $900 million (about ₹8,550 crore) financing is structured as a mix of primary and secondary share purchases and gives the company an approximately 20 percent stake in CRED, valuing the startup at around $4.5 billion on a post-money basis. That is a notable markdown from CRED's $6.4 billion peak in 2022, a reminder of how sharply late-stage startup valuations have reset. Shah will step down as CRED's chief executive — the company's Miten Sampat takes over as interim CEO — while keeping his personal shareholding. "I'll be joining Meta to lead WhatsApp globally. Meta comes in as a minority investor in CRED. No access to member data," Shah wrote in the post announcing the move, pre-empting the obvious question about whether a social-media giant would get its hands on the financial data of CRED's roughly 17 million creditworthy users.

For the Indian diaspora, the story carries a now-familiar charge. Shah joins a lengthening roster of Indian-origin leaders at the helm of the world's most powerful technology platforms — Sundar Pichai at Alphabet, Satya Nadella at Microsoft, Arvind Krishna at IBM, Shantanu Narayen at Adobe — except that Shah's path runs in the opposite direction to most of them. He did not climb a corporate ladder in the United States; he built two consumer companies in India, sold the first (FreeCharge, to Snapdeal in 2015) and scaled the second, and is now being brought into a global role on the strength of what he built at home. For a generation of Indian founders, that distinction matters: it suggests the Indian market is no longer just a place to acquire users, but a place that produces the operators who run global products.

There is a sharper edge to the timing, too. Meta is deepening its push into India's digital economy at a moment when New Delhi is increasingly assertive about data localisation, platform accountability and the treatment of Indian users' information. WhatsApp has spent years tangling with the Indian government over traceability and content rules. Putting an Indian founder in charge, while taking a minority stake in a beloved Indian brand, gives Meta both local credibility and a powerful commercial reason to keep investing in the market — even as it navigates a regulator that has grown far less deferential to American tech giants than it once was.

What Shah inherits is a paradox: the most ubiquitous app in India that has never quite figured out how to make money from Indian commerce. The diaspora, scattered across the Gulf, North America, Britain and Australia, runs much of its family and business life through the same green-and-white interface — group chats with parents in Pune, voice notes to cousins in Toronto, small businesses taking orders in Dubai. If Shah can turn that ubiquity into a payments and commerce engine, the change will be felt not just in India but in every WhatsApp group where the diaspora lives. If he cannot, he will have learned what Cathcart already knows: that being on every phone in India is not the same as owning a rupee of what flows through it."""

    img_url = fetch_wikipedia_person_image("Kunal Shah")
    img_caption = ""
    img_attribution = ""
    if img_url:
        img_caption = "Kunal Shah, founder of CRED, who has been named global head of WhatsApp"
        img_attribution = "Wikimedia Commons"
    else:
        for q in ["WhatsApp logo", "Meta Platforms headquarters", "smartphone messaging app India"]:
            commons = fetch_wikimedia_commons_images(q)
            if commons:
                img_url = commons[0]["url"]
                img_caption = "Meta has named CRED founder Kunal Shah as the new global head of WhatsApp"
                img_attribution = "Wikimedia Commons"
                break

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters — 'Meta's WhatsApp to be led by Indian startup founder Kunal Shah' (June 22, 2026): CRED founder Kunal Shah will become Meta-owned WhatsApp's new leader; current head Will Cathcart announced the move on X; announcement comes after CRED said it will raise about $900 million from Meta",
            "TechCrunch — 'WhatsApp gets new chief as Meta taps India's CRED founder Kunal Shah, and invests $900M in startup' (June 22, 2026): Shah to succeed Will Cathcart, who is stepping down after nearly seven years to take a new AI product-building role at Meta; $900M financing via primary and secondary share purchases makes Meta a minority investor; Shah steps down as CEO while retaining his shareholding; India is WhatsApp's largest market with more than 500 million users; WhatsApp Pay gained traction but trailed PhonePe and Google Pay",
            "Livemint — 'Meta appoints Kunal Shah as new WhatsApp boss as part of ₹8,550 crore investment in Cred': investment gives Meta ~20% stake in CRED; deal values the company at roughly ₹42,600 crore ($4.5 billion) post-money; Shah replaces Cathcart, who will transition to a new role developing AI-powered consumer apps (per Bloomberg)",
            "Inc42 — 'Kunal Shah Leaves CRED For Top Role At WhatsApp': Shah stepping down from day-to-day operations to take over as global head of WhatsApp; Miten Sampat to be interim CEO; CRED raising ₹8,550 Cr ($900M) Series H led by Meta at ₹43,239 crore post-money valuation; Shah said 'Meta comes in as a minority investor in CRED. No access to member data'; CRED reported revenue of ₹3,200 Cr and announced its fifth ESOP buyback; ~1.7 crore users"
        ]),
        "diaspora_angle": "WhatsApp is the connective tissue of diaspora family and business life from the Gulf to North America, and an Indian-built fintech founder now runs it globally — a marker of Indian operators, not just Indian users, reaching the top of the world's biggest platforms.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    art_id = insert_article(article)
    return art_id


# ─── Article 2: Lucknow coaching-centre fire ─────────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Lucknow coaching-centre fire kills 14")
    print("="*60)

    slug = "lucknow-coaching-centre-fire-14-students-killed-aliganj-fire-safety-india-diaspora-20260622"
    headline = "Fourteen Students Walked Into a Coaching Centre in Lucknow. They Never Walked Out."
    subheadline = "A fire tore through a crowded building in Lucknow's Aliganj on Monday, killing 14 — most of them young people — as some jumped from windows to escape. The cause is still unknown. The pattern, in India's tightly packed coaching towns, is not."

    body = """The fire was first reported at around 3 p.m. By the time it was brought under control more than an hour later, 14 people were dead, most of them students, and the burnt shell of a commercial building in Lucknow's Aliganj neighbourhood had become the latest entry in a grimly repetitive Indian story. Uttar Pradesh's Deputy Chief Minister, Brajesh Pathak, who rushed to the site, was unsparing in his account. "Fourteen children have lost their lives," he told reporters, visibly shaken. "I have seen 14 bodies with my own eyes."

The building was a mixed-use commercial block — a coaching and computer-training institute that also functioned as an animation centre, sharing the premises with a pet shop and other small stores. Witnesses described thick black smoke pouring from the structure and a scene of panic as people trapped on the upper floors searched for a way out. Five to seven students jumped from the first floor to escape, according to witnesses who spoke to local broadcasters; one suffered broken bones, and a man was filmed falling as he tried to climb down. Rescuers from the fire brigade, the State Disaster Response Force and the National Disaster Response Force eventually drilled a hole in the side of the building to reach those inside.

Doctors at King George's Medical University offered an early, telling detail. The bodies brought in showed limited external burn injuries, the hospital's spokesman said; the likely cause of death was suffocation from inhaling dense smoke. The building, Pathak noted, was packed with wooden furniture that fed the smoke and obscured visibility so badly that fire crews could barely see inside. Prime Minister Narendra Modi said he was "anguished by the loss of lives" and offered condolences to the families. The state has ordered a high-level inquiry, and the cause of the blaze — electrical fault, short circuit, something else — remains, for now, unestablished.

It is the predictability of the tragedy that should disturb most. India's private coaching industry, worth tens of billions of dollars, runs on cramming as many students as possible into rented floors of commercial buildings that were rarely designed for dense human occupancy. Fire exits are routinely blocked or absent, no-objection certificates from fire departments are missing or fraudulently obtained, and combustible material — furniture, paper, cabling — is everywhere. The result is a recurring cycle of disaster: a coaching-centre fire in Surat killed 22 students in 2019; a hospital fire, a hotel fire, a basement library flooding that drowned aspirants in Delhi in 2024. Each is followed by ministerial visits, an inquiry, a few arrests, and then the same conditions reassert themselves.

For the diaspora, the instinct to read this as distant news would be a mistake. The coaching ecosystem that funnels Indian teenagers toward engineering, medical and civil-service exams is the same machine that, a few years downstream, produces the students who fill universities in the United States, Britain, Canada and Australia, and the professionals the diaspora is largely built from. Many NRIs passed through exactly these buildings — the cramped tutorial floors of Kota, Hyderabad, Lucknow and Delhi — on their own way out. The families grieving in Lucknow are, in many cases, the same kind of aspirational middle-class households that send their next child abroad. The safety failures that killed 14 people on Monday are a tax levied on precisely the ambition the diaspora celebrates in itself.

There is also a governance dimension the diaspora watches closely. India markets itself abroad as a rising power with world-class cities and a booming knowledge economy, courting investment and returning talent with the promise of a modernising state. Events like the Aliganj fire puncture that pitch in the most basic way: a country that can run a space programme and a billion-person digital payments network still cannot reliably stop a tutorial building from becoming a death trap. For returning NRIs weighing where to raise children or set up businesses, the gap between India's ambitions and its enforcement of something as elementary as a fire code is not an abstraction — it is the difference between a brochure and a building.

The inquiry will run its course. There will be questions about the building's clearances, its single staircase, the wooden interiors, whether anyone warned of the risk before. The honest answer, residents of India's coaching hubs already know, is that the warnings are perennial and the enforcement is not. Fourteen families in Lucknow will spend the coming days collecting bodies and burying children who had gone to a building to study for a better future. The least the country owes them is that the inquiry this time produces something more durable than the last one did."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    for q in ["India fire brigade", "fire engine India", "fire truck Uttar Pradesh"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "Fire and emergency services in India; a coaching-centre fire in Lucknow's Aliganj killed 14 on June 22"
            img_attribution = "Wikimedia Commons"
            break

    if not img_url:
        pex = fetch_pexels_image("fire truck emergency")
        if pex:
            img_url = pex
            img_caption = "Emergency services responded to a deadly coaching-centre fire in Lucknow"
            img_attribution = "Pexels"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "public-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters / Devdiscourse — 'Fire at coaching centre in India's Lucknow kills at least eight, police say' (June 22, 2026): at least eight killed, mostly students, in a fire at a coaching centre in Lucknow; local media put the toll higher at 14; fire reported in the afternoon",
            "Devdiscourse / ANI — '14 children killed, four injured in Lucknow coaching institute fire; high-level probe ordered: UP Dy CM Brajesh Pathak': Deputy CM Brajesh Pathak confirmed 14 children dead and four injured admitted to KGMU Trauma Centre; search operation completed with no children remaining trapped; building functioned as a coaching/animation centre filled with wooden furniture; cause yet to be ascertained; high-level inquiry ordered",
            "Dainik Bhaskar (bhaskarenglish.in) live blog — 'Lucknow Coaching Centre Fire: Students Jump to Escape': fire in Lucknow's Aliganj; KGMU spokesperson Dr K.K. Singh said bodies showed limited external burn injuries and likely cause of death was suffocation from dense smoke; seven injured admitted with 12–15 more possibly incoming; building also housed a pet shop and other stores; UP Deputy CM Brajesh Pathak at the site",
            "The Sun / NDTV / ANI — 'At least 14 killed as huge fire engulfs training centre as terrified students jump from windows': fire reported around 3pm and brought under control after more than an hour; five to seven students jumped from the first floor, one suffering broken bones; rescuers drilled a hole in the building's side; PM Narendra Modi expressed condolences on X, calling himself 'anguished by the loss of lives'; comparison to 2019 Surat coaching-centre fire that killed 22 students"
        ]),
        "diaspora_angle": "India's coaching-centre ecosystem is the same machine that, years downstream, produces the students and professionals the diaspora is built from; the recurring fire-safety failures that killed 14 in Lucknow are a tax on exactly the middle-class ambition NRIs celebrate, and a marker of the gap between India's pitch to returning talent and its enforcement on the ground.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    art_id = insert_article(article)
    return art_id


if __name__ == "__main__":
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    print("\n" + "="*60)
    print(f"DONE. Inserted IDs: {[i for i in ids if i]}")
    print("="*60)
