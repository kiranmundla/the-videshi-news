#!/usr/bin/env python3
"""News writer — 3 articles for 2026-06-02 evening batch."""

import json, os, re, sys, time, uuid, urllib.parse, subprocess

import requests

# ── env ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Check image URL returns HTTP 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD, try GET
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
    """Download image and upload to Supabase storage bucket article-images."""
    try:
        r = requests.get(image_url, timeout=20,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Failed to download image: status={r.status_code}, size={len(r.content)}")
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
            timeout=20,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def insert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=20,
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else data.get("id")
        print(f"  ✓ Inserted: {article['slug']}  id={art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ── ARTICLES ─────────────────────────────────────────────────────────

articles = []

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: India Inc Q4 Earnings Beat, Iran War Clouds Outlook
# ─────────────────────────────────────────────────────────────────────
a1_body = """India's listed companies delivered a surprise earnings beat for the quarter ended March 2026, buoyed by consumption tax cuts and an accommodative monetary policy cycle that kept domestic demand humming. But the three-month-old war in Iran and the near-total closure of the Strait of Hormuz are casting a long shadow over the quarters ahead.

## The Numbers

Net profit for Nifty 50 firms rose 6.6 per cent year-on-year in the January-March quarter, according to Kotak Institutional Equities — comfortably ahead of the consensus forecast of just 2 per cent growth. Banks, financial companies, metal producers and oil marketing companies drove the bulk of the improvement.

Beyond the blue-chip index, the picture was even brighter. Nomura's universe of 256 companies posted an 18 per cent rise in profit after tax, while Motilal Oswal's broader sample of 359 firms delivered 16 per cent growth. Mid-cap earnings surged roughly 35 per cent and small-caps advanced nearly 20 per cent, significantly outpacing their larger peers.

Automobile and telecom companies also showed improvement. But IT firms saw tepid revenue growth amid mounting concerns over AI-driven disruption to traditional outsourcing contracts, and pharmaceutical companies grappled with persistent weakness in the US generics market. Cement, consumer staples and durable goods makers flagged rising raw material and freight costs.

## The Iran War Overhang

The catch is that all of this happened before the full force of the energy shock was felt. The Strait of Hormuz, which carried more than 40 per cent of India's crude oil imports, has been effectively shut since March. Brent crude, though it has pulled back from an April peak of $122, still trades around $93 a barrel — roughly 44 per cent above pre-conflict levels.

India slipped to seventh place globally in terms of total market capitalisation on Tuesday, with South Korea's chip-heavy market overtaking it for the first time. Foreign portfolio investors have now pulled more money out of India in 2026 than they did in all of 2025, with net outflows exceeding $26 billion in five months.

Goldman Sachs has named India the most vulnerable major economy to the Hormuz disruption, estimating a potential 3.6 per cent hit to GDP if the strait remains closed through the year. Oil marketing companies, which absorbed fuel losses in the March quarter without corresponding retail price increases, face the steepest margin pressure ahead.

## What Comes Next

Analysts say the earnings beat was backward-looking. The real test arrives in the June and September quarters, when the full weight of elevated crude prices, supply chain rerouting and a potentially weak monsoon — now forecast to be the driest in 11 years — will show up in corporate results.

"Markets are still in the midst of uncertainties regarding the US-Iran war and a delayed monsoon and will need clarity on these two fronts for any further material gains," said Anita Gandhi, head of institutional business at Arihant Capital Markets.

For India's 200-million-strong diaspora, the macro picture carries direct implications. Remittance flows, which totalled $125 billion in FY26, are sensitive to both Indian asset valuations and the employment outlook in Gulf states that have been directly affected by the conflict. A sustained energy shock would also push up the cost of everything from air tickets to food prices — felt acutely by families straddling two economies.

The Q4 earnings beat is real. But it may be the last clean quarter India gets for a while.

*Sources: Reuters, Kotak Institutional Equities, Nomura, Motilal Oswal, Goldman Sachs*"""

articles.append({
    "headline": "India Inc Beat Q4 Estimates by a Wide Margin. The Iran War May Ensure It Was the Last Good Quarter.",
    "subheadline": "Nifty 50 profits rose 6.6% against a 2% forecast. Mid-caps surged 35%. But with Hormuz shut and oil at $93, analysts say the real test starts now.",
    "body": a1_body,
    "slug": "india-inc-q4-earnings-beat-iran-war-outlook-hormuz-oil-nifty-midcap-20260602",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "sources": json.dumps(["Reuters", "Kotak Institutional Equities", "Nomura", "Motilal Oswal", "Goldman Sachs"]),
    "image_search": {"type": "pexels", "query": "Mumbai stock exchange Bombay financial district", "fallback": "India stock market trading floor"},
    "image_attribution": "Pexels",
})

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: South Africa's Mashatile Wraps India Visit
# ─────────────────────────────────────────────────────────────────────
a2_body = """South Africa's Deputy President Paul Mashatile wrapped up the first leg of a six-day working visit to India on Tuesday, holding back-to-back meetings with President Droupadi Murmu, Vice President C.P. Radhakrishnan, and External Affairs Minister S. Jaishankar in New Delhi — a diplomatic schedule that signals both countries are serious about deepening a partnership rooted in the legacies of Mahatma Gandhi and Nelson Mandela.

## What Was Discussed

The talks covered a wide arc: trade and investment, defence cooperation, skills development, digital infrastructure, MSMEs, pharmaceuticals, energy, and people-to-people ties. Both sides also agreed to work more closely in multilateral forums, including BRICS, IBSA, the G20 and the United Nations.

India currently ranks among the top 10 investing countries in South Africa. Bilateral trade has been growing steadily, though both leaders acknowledged it could be significantly larger. President Murmu called for expanded engagement in technology and skilling — sectors where India's IT services and South Africa's mining and manufacturing economies could find natural synergies.

Mashatile, who arrived on May 29 with a high-level delegation of senior ministers and officials, told reporters that the visit was designed to "strengthen trade and investment relations" and to align cooperation with Africa's Agenda 2063 and India's Viksit Bharat 2047 vision.

## The Global South Angle

The visit underscored a broader geopolitical alignment. As the Iran war reshapes energy flows and the Global South pushes for a greater voice in international institutions, India and South Africa — both founding members of BRICS and champions of the Non-Aligned Movement's legacy — are positioning themselves as anchors of a multipolar order.

Jaishankar, in a post on X after his meeting with Mashatile, said the discussions focused on "opportunities in trade, investments, MSMEs, digital and infrastructure domains" and that both sides "agreed that India and South Africa must work closely in international forums."

Congress leader and former Union Minister Anand Sharma, who also met Mashatile, described the visit as a moment to "revisit the cherished memories of the heroic struggle against apartheid" and to discuss the role of both nations in shaping the future of the Global South.

## The Diaspora Connection

India's relationship with South Africa carries a unique emotional resonance for the diaspora. Mahatma Gandhi's formative years in South Africa, where he developed the concept of satyagraha, remain a cornerstone of the bilateral relationship. South Africa is home to one of the oldest Indian-origin communities in the world — an estimated 1.5 million people of Indian descent, concentrated largely in KwaZulu-Natal province.

For this community, the strengthening of India-South Africa ties has practical implications: easier visa processes, expanded business opportunities, educational exchanges, and a deeper institutional framework for protecting their rights and interests.

Mashatile is scheduled to visit Hyderabad before departing India on June 3, where his delegation will engage with the city's technology and pharmaceutical sectors.

*Sources: IANS, Devdiscourse, ANI, South African Government, Ministry of External Affairs*"""

articles.append({
    "headline": "South Africa's Deputy President Just Spent a Week in India. The Agenda Was Bigger Than Trade.",
    "subheadline": "Paul Mashatile met Murmu, Radhakrishnan, and Jaishankar in a diplomatic blitz covering defence, digital infrastructure, BRICS, and the future of the Global South.",
    "body": a2_body,
    "slug": "south-africa-mashatile-india-visit-brics-global-south-trade-defence-20260602",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "sources": json.dumps(["IANS", "Devdiscourse", "ANI", "South African Government", "Ministry of External Affairs"]),
    "image_search": {"type": "wikipedia", "person": "Paul Mashatile", "fallback_pexels": "India South Africa diplomacy flags"},
    "image_attribution": "Wikimedia Commons",
})

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 3: Zee Entertainment Secures FIFA World Cup 2026 Broadcast Rights
# ─────────────────────────────────────────────────────────────────────
a3_body = """Zee Entertainment has secured the broadcast rights to the 2026 FIFA World Cup and 38 other FIFA events through 2034, ending a months-long standoff that had left India — the world's most populous country — without a confirmed broadcaster just 10 days before the tournament kicks off on June 11.

## The Deal

Financial terms were not officially disclosed, but Reuters reported that FIFA had initially sought roughly $100 million for the India package covering the 2026 and 2030 World Cups before slashing its asking price to $60 million. Industry sources cited by The Hindu BusinessLine suggest the deal was closed somewhere between $25 million and $80 million.

The agreement covers an eight-year window from 2026 to 2034 and includes the FIFA World Cup 2030, the FIFA Women's World Cup 2027, youth tournaments at U-17 and U-20 levels for both men and women, the Futsal World Cup, and the FIFA Intercontinental Cup. Zee also secured rights to FIFA docu-series content.

JioStar, the Reliance-Disney joint venture that dominates Indian sports broadcasting with exclusive rights to the Indian Premier League and English Premier League, had offered about $20 million for the World Cup rights but was rejected by FIFA. Sony, which held rights for the 2014 and 2018 tournaments, held discussions but did not submit a formal bid.

## Unite8 Sports: Zee's New Play

Zee is launching a new sports network — Unite8 Sports — with four dedicated channels: Unite8 Sports 1 and Unite8 Sports 1 HD in Hindi, and Unite8 Sports 2 and Unite8 Sports 2 HD in English. The World Cup and subsequent FIFA events will also stream on ZEE5, the company's OTT platform.

The channels will carry a range of sports beyond football, including kabaddi, cricket, badminton, wrestling, boxing, and combat sports. Zee's stock surged roughly 7 per cent on the announcement, reflecting investor confidence that the FIFA deal could anchor a credible sports portfolio to challenge JioStar's dominance.

## Why It Matters for the Diaspora

The 2026 FIFA World Cup is the first to feature 48 teams, up from 32, and will be held across the United States, Canada and Mexico — three countries with massive Indian diaspora populations. For NRIs in these host nations, the tournament is not just a television event but a live, in-person experience.

India's football following, while historically smaller than cricket, has been growing steadily. The Indian Super League has expanded its fan base, and the FIFA World Cup has traditionally drawn strong viewership in India even without the national team qualifying. The 2022 World Cup final between Argentina and France was one of the most-watched non-cricket sporting events in Indian television history.

Zee's acquisition ensures that the roughly 1.4 billion people in India — and the diaspora audience on ZEE5 — will have legal access to every match of the tournament. Given that the group stage alone features 104 matches over 39 days, the volume of content is enormous.

The first match kicks off on June 11 when Mexico hosts the opening game at the Estadio Azteca in Mexico City.

*Sources: Reuters, Livemint, The Hindu BusinessLine, BestMediaInfo, Devdiscourse*"""

articles.append({
    "headline": "Zee Just Landed the FIFA World Cup. India's Biggest Broadcaster Didn't Even Come Close.",
    "subheadline": "With 10 days to kickoff, Zee Entertainment secured the 2026 World Cup and 38 FIFA events through 2034. JioStar's $20 million bid was rejected. Zee's stock surged 7%.",
    "body": a3_body,
    "slug": "zee-entertainment-fifa-world-cup-2026-broadcast-india-jiostar-unite8-20260602",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "sources": json.dumps(["Reuters", "Livemint", "The Hindu BusinessLine", "BestMediaInfo", "Devdiscourse"]),
    "image_search": {"type": "pexels", "query": "FIFA World Cup football stadium crowd", "fallback": "soccer football match stadium"},
    "image_attribution": "Pexels",
})

# ── MAIN ─────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"  News Writer — {len(articles)} articles")
    print(f"{'='*60}\n")

    published_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for i, art in enumerate(articles, 1):
        print(f"\n── Article {i}/{len(articles)}: {art['slug']}")

        # Image sourcing
        img_meta = art.pop("image_search")
        img_url = None
        attribution = art.get("image_attribution", "The Videshi")

        if img_meta.get("type") == "wikipedia" and img_meta.get("person"):
            print(f"  → Trying Wikipedia for '{img_meta['person']}'...")
            img_url = fetch_wikipedia_person_image(img_meta["person"])
            if img_url:
                attribution = "Wikimedia Commons"

        if not img_url and img_meta.get("type") == "pexels":
            print(f"  → Trying Pexels for '{img_meta.get('query')}'...")
            img_url = fetch_pexels_image(img_meta.get("query"), img_meta.get("fallback"))
            if img_url:
                attribution = "Pexels"

        if not img_url and img_meta.get("fallback_pexels"):
            print(f"  → Trying Pexels fallback for '{img_meta['fallback_pexels']}'...")
            img_url = fetch_pexels_image(img_meta["fallback_pexels"])
            if img_url:
                attribution = "Pexels"

        # Upload to Supabase storage for permanence
        final_image_url = None
        if img_url:
            if validate_image(img_url):
                art_id_for_img = art["slug"]
                filename = f"{art_id_for_img}.jpg"
                final_image_url = upload_to_supabase_storage(img_url, filename)
                if not final_image_url:
                    # If upload fails, use direct URL only if it's from a permanent source
                    if "upload.wikimedia.org" in img_url or "images.pexels.com" in img_url:
                        final_image_url = img_url
            else:
                print(f"  ⚠ Image validation failed for: {img_url[:80]}")

        # Prepare article payload
        art["published_at"] = published_at
        art["image_url"] = final_image_url
        art["image_attribution"] = attribution if final_image_url else None

        # Remove None image fields
        if not art["image_url"]:
            art.pop("image_url", None)
            art.pop("image_attribution", None)

        # Insert
        art_id = insert_article(art)
        if art_id and final_image_url and final_image_url.startswith(SB_URL):
            pass  # image already has slug-based name

        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"  Done. {len(articles)} articles processed.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
