#!/usr/bin/env python3
"""
Videshi News Writer — June 23, 2026 (06:30 UTC run)
2 NEW articles (both fresh, distinct from prior runs which covered SpaceX,
NEET re-exam, Iran sanctions/oil, foreign-investor return, USTR Delhi trade):
  1. India says ties with China are 'normalising' after NSA Ajit Doval and
     Chinese FM Wang Yi meet on the sidelines of the BRICS NSA meet in Delhi —
     Wang's first India visit since Aug 2025; a push to restart dialogue,
     trade, flights and visas frozen since the 2020 border clash. (geopolitics
     — diaspora travel/business/student angle)
  2. India's private-sector growth slips to a three-month low and business
     confidence falls near a four-year low (HSBC flash PMI), even as the
     Iran-driven oil relief lifts equities. (economy — NRI investor/jobs/
     remittances angle)
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


# ─── Article 1: India–China normalisation, Doval–Wang Yi in Delhi ──────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India-China ties normalising, Doval-Wang Yi")
    print("="*60)

    slug = "india-china-ties-normalising-doval-wang-yi-meet-brics-nsa-delhi-diaspora-flights-visas-20260623"
    headline = "India and China Say Their Ties Are 'Normalising' Again. The Diaspora Has Heard This Before."
    subheadline = "National Security Adviser Ajit Doval met Chinese Foreign Minister Wang Yi in Delhi on Monday \u2014 Wang's first India visit since August 2025 \u2014 and both sides called the talks 'constructive and forward-looking.' Behind the diplomatic language sit the flights, visas and business links the 2020 border clash froze, and that the diaspora still navigates around."

    body = """India and China inched another step away from their deepest freeze in decades on Monday, with National Security Adviser Ajit Doval meeting Chinese Foreign Minister Wang Yi in New Delhi and both governments describing the conversation as a move toward "gradual normalisation." It was Wang's first visit to India since August 2025, and it took place on the sidelines of a meeting India is chairing this week \u2014 a gathering of the national security advisers of the BRICS group, which India leads in 2026 for the fourth time.

India's foreign ministry called the Doval\u2013Wang talks "constructive and forward-looking," saying the two discussed "recent developments in their relationship" and "noted progress towards gradual normalisation." China's readout struck a similar register but added a familiar caution: "We must respect each other's core interests, properly handle sensitive issues," Wang said, while urging both countries to resume the bilateral dialogue mechanisms that lapsed after the 2020 clash and to revive exchanges across trade, finance, law enforcement and media.

## Why This Keeps Happening

Relations between Asia's two giants cratered in 2020, when a deadly skirmish in the Galwan Valley along the disputed Himalayan frontier killed soldiers on both sides and sent ties into a years-long deep chill. New Delhi tightened scrutiny of Chinese investment, banned scores of Chinese apps, suspended most direct passenger flights and all but stopped issuing tourist visas to Chinese nationals; Beijing reciprocated in kind. A cautious thaw began in 2024, helped by leader-level meetings between Prime Minister Narendra Modi and President Xi Jinping, and the appointment this year of a new Indian ambassador in Beijing. Monday's meeting is the latest brick in that slow rebuild \u2014 and, crucially, a step toward preparing the BRICS summit India will host in September.

The hosting role matters. As BRICS chair, India set the meeting's theme as "non-traditional security challenges" \u2014 cybersecurity, AI-driven threats, terrorism, the security of digital infrastructure \u2014 and brought together security chiefs including Russia's Sergei Shoigu alongside Wang. For Indian diplomacy, it is a chance to show it can convene rivals and partners at the same table even as it manages an unresolved border with one of them.

## What It Means for the Diaspora

For the Indian diaspora, the headline is less about the border than about the plumbing of everyday connection. The 2020 rupture quietly reshaped how millions move and do business. Direct India\u2013China flights vanished, forcing travellers \u2014 including students, traders and families with members on both sides \u2014 to route through Hong Kong, Singapore or the Gulf. Visa channels narrowed to a trickle. Indian firms with Chinese suppliers, and the large community of Indian-origin professionals working across Chinese-linked supply chains in Southeast Asia and the Gulf, have spent five years building workarounds.

A genuine normalisation would touch all of that: the resumption of direct flights under discussion for months, smoother business and tourist visas, and a steadier climate for the Indian students and academics who once studied in China and the Chinese students who came to India. It would also ease one of the diaspora's quieter anxieties \u2014 that a fresh border flare-up could once again sweep ordinary people into a geopolitical quarrel, stranding travellers and freezing remittance-linked trade overnight.

## What's Next

The diaspora's caution is earned. "Normalisation" has been declared, walked back, and declared again repeatedly since 2024, and the border itself \u2014 the thing that broke the relationship \u2014 remains unsettled, with troops still arrayed along long stretches of the Line of Actual Control. Wang's call to "respect each other's core interests" is the same coded language that has accompanied every previous round, and India has been careful to keep deepening ties with the United States, Japan and its Quad partners even as it talks to Beijing.

The real test will be whether Monday's warm words translate into concrete restorations before the September summit: flights back in the air, visas flowing, dialogue mechanisms formally restarted. Until then, the diaspora will do what it has done since 2020 \u2014 welcome the thaw, book the connecting flight through Singapore anyway, and wait to see whether this time the normalisation sticks."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Named people involved -> Wikipedia first per rules
    img_url = fetch_wikipedia_person_image("Ajit Doval")
    img_caption = "India's National Security Adviser Ajit Doval, who met Chinese Foreign Minister Wang Yi in Delhi as both sides cited 'gradual normalisation'"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        img_url = fetch_wikipedia_person_image("Wang Yi (politician)")
        img_caption = "Chinese Foreign Minister Wang Yi, who met India's NSA Ajit Doval in Delhi on his first India visit since August 2025"

    if not img_url:
        img_url, ctitle = pick_commons([
            "Ajit Doval", "Wang Yi politician",
            "India China flags", "Ministry of External Affairs India building"
        ])

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters \u2014 India says ties with China normalising as top officials meet in Delhi (June 22, 2026): Indian NSA Ajit Doval spoke with Chinese FM Wang Yi on Monday on the sidelines of a BRICS National Security Advisers' meeting in New Delhi; India's foreign ministry described the talks as 'constructive and forward-looking' and said the two 'noted progress towards gradual normalisation'; relations improved in 2024 after years of friction that began with the 2020 border clash; Wang said 'We must respect each other's core interests, properly handle sensitive issues' and urged resumption of bilateral dialogue mechanisms and exchanges in trade, finance, law enforcement and media; India is BRICS chair and hosting the NSA meeting June 22-23",
            "The Hindu BusinessLine / MEA \u2014 India to host BRICS National Security Advisers' Meet from June 22-23 (June 20, 2026): the meeting is chaired by NSA Ajit Doval; NSAs/heads of delegation exchange views on 'Non-traditional security challenges confronting the world today', including new technologies and emerging threats; they review outcomes of BRICS Joint Working Groups on Counter-Terrorism and on security in the use of ICTs; India holds the BRICS chairship for the fourth time in 2026 (after 2012, 2016, 2021) under the theme 'Building for Resilience, Innovation, Cooperation and Sustainability'",
            "Madhyamam / newkerala \u2014 India to host BRICS security advisers' meeting chaired by Ajit Doval (June 20-22, 2026): participants include Chinese FM Wang Yi and Russian Security Council Secretary Sergei Shoigu; Wang Yi's attendance marks his first visit to India since August 2025; the meeting is an important step toward the BRICS Summit India will host in September; Chinese Ambassador to India Xu Feihong said the Chinese delegation would exchange views on the international security situation and regional and global issues"
        ]),
        "diaspora_angle": "A genuine India\u2013China thaw would restore the direct flights, business and tourist visas and student exchanges that the 2020 border clash froze \u2014 the everyday plumbing millions in the diaspora have routed around for five years \u2014 and ease the fear that a fresh flare-up could again strand travellers and freeze trade overnight.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India private-sector growth slips, confidence near 4-yr low ─

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India private-sector PMI slips, confidence cools")
    print("="*60)

    slug = "india-private-sector-growth-three-month-low-business-confidence-pmi-june-2026-diaspora-investors-20260623"
    headline = "India's Economy Is Still Growing Fast. The Mood of the People Running It Just Hit a Four-Year Low."
    subheadline = "A closely watched survey shows India's private sector expanded at its slowest pace in three months in June, hiring at its weakest in half a year, and business confidence at goods producers sinking to its gloomiest in nearly four years \u2014 a cooling that lands just as the diaspora's portfolios and remittances flow back into the country."

    body = """India remains the fastest-growing major economy on the planet, but the people who actually run its companies are feeling distinctly less sure of themselves. A closely watched survey released Tuesday showed India's private sector expanded in June at its slowest pace in three months, with weaker demand dragging on both factories and services, and overall business confidence slipping to its lowest level since January.

HSBC's flash India Composite Purchasing Managers' Index, compiled by S&P Global, fell to 57.4 in June from 59.3 in May. Any reading above 50 still signals expansion \u2014 so this is a story of growth that is decelerating, not reversing. But the details are softer than the headline. The services PMI dropped to a 17-month low of 57.3 from 59.8, and manufacturing eased to a three-month low of 54.5 from 55.0. New orders, the clearest gauge of demand, rose at their slowest pace since March, with firms blaming competitive pressure and gas shortages for the squeeze.

## The Mood Is the Real Signal

The most striking number is not about output but about sentiment. Business confidence slipped below its long-run average in June, and among goods producers it sank to its weakest in nearly four years. Confidence is a leading indicator: it shapes whether firms hire, build and invest in the months ahead. And the survey already shows that caution biting \u2014 private-sector employment rose only marginally in June, the weakest gain in the current six-month run of expansion, with hiring at both factories and service providers at its lowest since December.

There is a sliver of relief in the data for households: cost pressures eased for a third straight month to their lowest since January, and selling-price inflation cooled as some firms held back from passing on increases in a tough demand climate. Lower input costs are good news for India's inflation fight, but they also reflect the same slackening demand that is denting confidence.

## Why the Diaspora Should Pay Attention

For the diaspora, the timing is pointed. This cooling lands in the very week that foreign money has started flowing back into Indian markets. After offloading a record $30.6 billion of Indian stocks so far this year, foreign portfolio investors bought $515 million of equities on Friday \u2014 their biggest daily purchase since February \u2014 and the Nifty and Sensex have risen in six of the last seven sessions, lifted by falling oil prices and the U.S.\u2013Iran de-escalation. Many NRIs invest in India precisely through these flows, via India-focused funds, GIFT City vehicles and direct equity, and a market rallying on cheaper oil while the real economy quietly cools is exactly the kind of divergence that catches retail investors offside.

The labour signal matters too. A large share of the diaspora's families still have working-age relatives in India, and a chunk of NRI savings rides on the assumption that India's hiring engine keeps humming \u2014 it underpins everything from property bets to the remittances that flow the other way, into Indian households. Weakening job creation, even from a high base, is a quieter warning than a market crash, but it is the kind that shows up six months later in pay packets and consumer spending.

## What's Next

None of this dents the bigger picture: at a composite reading of 57.4, India is still expanding far faster than most of the world, and a fresh tailwind \u2014 sub-$80 oil, a steadier rupee after central-bank support, and the prospect of an India\u2013U.S. trade deal that could hand Indian exporters a tariff edge \u2014 could revive both demand and confidence quickly. The Reserve Bank of India has already trimmed its growth forecast for the year, pointing at exactly the external uncertainty the PMI respondents are flagging.

For diaspora investors, the lesson is to read past the index headline. India's growth story is intact, but June's survey is a reminder that the gap between a roaring stock market and the cautious mood inside the country's boardrooms can widen \u2014 and that the people closest to the ground are, for now, bracing rather than betting."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "Bombay Stock Exchange building Mumbai",
        "Bombay Stock Exchange",
        "Mumbai financial district skyline",
        "Nariman Point Mumbai",
        "factory manufacturing India"
    ])
    img_caption = "Mumbai's financial district; India's private-sector growth slowed to a three-month low in June as business confidence fell near a four-year low"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("Mumbai skyline business district")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A city financial district; India's June PMI showed growth cooling to a three-month low with confidence near a four-year low"

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
            "Reuters \u2014 India's June private sector growth slips to three-month low as demand, confidence cool, PMI shows (June 23, 2026): HSBC flash India Composite PMI (S&P Global) fell to 57.4 in June from 59.3 in May; new orders rose at their slowest pace since March amid competitive pressure and gas shortages; services PMI fell to a 17-month low of 57.3 from 59.8 and manufacturing PMI eased to a three-month low of 54.5 from 55.0; employment rose only marginally \u2014 weakest gain in the six-month expansion, hiring at factories and services lowest since December; cost pressures eased for a third straight month to lowest since January and selling-price inflation cooled; business confidence slipped below its long-run average, with sentiment at goods producers weakest in nearly four years",
            "Reuters \u2014 Indian shares rise on Reliance, IT rebound; Mideast hopes lift sentiment (June 22, 2026): Nifty 50 rose 0.37% to 24,102.90 and Sensex added 0.38% to 77,094.07, a sixth gain in seven sessions; foreign portfolio investors who offloaded a record $30.6 billion of Indian stocks year-to-date bought $515.2 million of equities on Friday, their biggest daily purchase since early February; Brent crude fell 1.9% below $80; IT index rose ~0.75% after tumbling 3.7% on Friday on Accenture's weak demand forecast",
            "Reuters \u2014 Indian shares open flat after oil-led rally (June 23, 2026): Nifty 50 and Sensex roughly flat at open after gaining 4.1% and 4.4% over seven sessions on lower oil and moderating foreign outflows following measures to support the rupee; Brent traded around $78; analysts expect a phase of consolidation absent fresh triggers"
        ]),
        "diaspora_angle": "The cooling lands just as foreign money \u2014 including the India-focused funds and GIFT City vehicles many NRIs invest through \u2014 flows back into a market rallying on cheaper oil, even as hiring weakens; that gap between a roaring index and cautious boardrooms is exactly what catches diaspora retail investors offside and eventually shows up in the jobs and remittances their families depend on.",
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
