#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (14:30 UTC run)
2 NEW articles, distinct from all prior runs:
  1. India-UK CETA free-trade agreement comes into force July 15, with the
     Double Contribution Convention exempting Indian professionals on temporary
     UK assignments from paying social security in both countries; Goyal heads
     to London June 25-27 on implementation. A direct money story for the UK
     diaspora and the firms that post Indians there.
  2. India presses the Gulf states to raise minimum salaries for its 5M+
     workers there — diplomats in all six GCC nations have quietly hiked the
     recommended minimum wages, a billions-in-remittances gambit that could
     also price some Indians out. A core diaspora-labour story.
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


# ─── Article 1: India-UK CETA comes into force July 15 ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India-UK CETA / Double Contribution Convention")
    print("="*60)

    slug = "india-uk-fta-ceta-july-15-double-contribution-convention-diaspora-professionals-20260624"
    headline = "On July 15, an Indian Professional Posted to Britain Stops Paying Twice for the Same Pension"
    subheadline = "The India-UK free-trade pact, signed last year, finally goes live next month \u2014 and tucked inside it is a social-security carve-out that puts real money back in the pockets of Indians sent to work in Britain. Trade Minister Piyush Goyal flies to London this week to nail down the rollout."

    body = """For a year the India-UK trade deal has been a headline without a date. Now it has one. The Comprehensive Economic and Trade Agreement \u2014 CETA, the formal name for the free-trade agreement the two countries signed in July 2025 \u2014 comes into force on Wednesday, July 15, both governments have confirmed. And ahead of the switch-on, India's Commerce and Industry Minister Piyush Goyal will travel to the United Kingdom from June 25 to 27 to meet his counterpart, Business and Trade Secretary Peter Kyle, and settle the practical details of implementation: tariff cuts, regulatory coordination and, crucially for the diaspora, the mechanics of moving professionals between the two countries.

Most of the coverage of CETA has fixated, understandably, on what gets cheaper. Britain will scrap tariffs on roughly 99% of Indian tariff lines, a windfall for textiles, leather, footwear, gems and jewellery, seafood and engineering goods. In the other direction, India will cut its punishing 150% duty on Scotch whisky to 40% over time, and tariffs on a quota of British cars from 100% to 10%. But for the millions of people of Indian origin who actually live and work in Britain, the most consequential clause is not about whisky or cars. It is about paychecks.

## The Double-Contribution Problem, Solved

Alongside the trade pact, a Double Contribution Convention (DCC) takes effect. Today, when an Indian company posts an employee to the UK on a temporary assignment, that worker typically has to pay into Britain's National Insurance system \u2014 the UK's social-security scheme \u2014 even though they are also still contributing to India's social-security net and will draw their pension back home. They pay twice and, because such contributions usually require years of residency to ever pay out, often see nothing for the British half.

The DCC ends that for assignments of up to three years. Indian professionals on temporary postings, and their employers, will be exempt from UK social-security contributions during that window, continuing to pay only into the Indian system. For an Indian IT engineer, consultant or manager sent to London or Manchester, that is a direct, immediate boost to take-home pay \u2014 and for the Indian firms that staff Britain's technology and services sector, a meaningful cut in the cost of every posting. India has long argued the arrangement could save its companies and workers thousands of crores of rupees a year.

## Who Can Move, and How

CETA also locks in and modestly widens the routes for Indians to work in Britain temporarily. Business visitors keep guaranteed access for short trips to attend meetings, negotiate contracts and the like. Intra-corporate transferees \u2014 staff moved within a multinational \u2014 and contractual service suppliers sent to deliver services for up to a year retain their pathways, with the contractual route extended to additional sectors. There is even a small, much-discussed quota: up to 1,800 Indian chefs, yoga instructors and classical musicians a year can be sent to the UK on contract. Independent, self-employed professionals in listed fields such as architecture and engineering get access too.

What CETA is not is a new immigration highway. It does not change Britain's points-based visa system or create open-ended work rights; the mobility it offers is temporary, sector-bound and tied to specific business purposes. For a diaspora weary of shifting visa goalposts in the US, that distinction matters \u2014 this is about smoothing temporary work, not settlement.

## A Deal That Nearly Wobbled

The July 15 start date was not a foregone conclusion. Indian officials had floated reopening or delaying the agreement over a dispute about Britain's incoming steel-tariff regime, due to take effect July 1. The impasse broke only after Prime Ministers Narendra Modi and Keir Starmer met on the sidelines of the G7 leaders' summit in France and agreed to push ahead regardless. The deal is worth an estimated \u00a34.8 billion ($6.5 billion) a year in additional bilateral trade, and the British government has urged its exporters to register \u2014 they have a 28-day window \u2014 to claim the new tariff benefits from day one.

## Why It Matters for the Diaspora

Britain is home to roughly 1.9 million people of Indian origin, and Indians are the single largest group of skilled migrants and international students flowing into the country. CETA touches them on several fronts at once: cheaper Indian goods on British shelves, new export openings for diaspora-run businesses, and \u2014 most tangibly \u2014 a social-security exemption that quietly raises the real wages of every Indian professional posted to the UK on a temporary contract. For the firms that send them, it lowers the cost of competing for British work. Goyal's three days in London this week are about turning all of that from treaty text into something a worker can see on a payslip from July 15. The diaspora will find out soon enough whether the implementation is as smooth as the signing ceremony.
"""

    # Hero: Wikimedia Commons photo (place/scene, not a named person)
    img_url, _ = pick_commons([
        "City of London financial district",
        "London skyline Thames",
        "Houses of Parliament London",
        "London cityscape"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "The City of London; the India-UK CETA free-trade pact comes into force on July 15, easing trade and professional mobility"

    if not img_url:
        px = fetch_pexels_image("London city skyline business")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "London's financial district, as the India-UK trade pact prepares to take effect on July 15"

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
            "Reuters (reuters.com, June 24 2026) \u2014 'India\u2019s Goyal to visit UK ahead of trade deal implementation': India's Trade Minister Piyush Goyal will visit the UK between June 25 and 27 for talks ahead of the rollout of the India-UK trade agreement on July 15; he is scheduled to meet UK Business and Trade Secretary Peter Kyle to discuss implementation issues including tariff cuts, regulatory coordination and mechanisms to ease trade and mobility of professionals.",
            "Reuters (reuters.com, June 18 2026) \u2014 'UK-India trade deal worth over $6 billion to start July 15': Britain's FTA with India comes into force July 15; deal worth \u00a34.8 billion ($6.5 billion), signed last year; implementation agreed despite a dispute over the UK's forthcoming steel-tariff regime due July 1, after PM Starmer and PM Modi met at the G7 summit in France; India to cut whisky tariffs to 40% from 150% and autos under a quota; UK cutting tariffs on clothes, footwear and some food; businesses have 28 days to register for tariff reductions.",
            "Outlook Business (outlookbusiness.com, June 23 2026) \u2014 'India UK FTA From July 15, Here's What Will Become Cheaper & Which Sectors Gain The Most': CETA effective July 15, 2026; covers goods, services, digital trade, investments, IP, government procurement and professional mobility; the Double Contribution Convention takes effect alongside it, removing the requirement for Indian professionals working temporarily in the UK to pay social-security contributions in both countries; Scotch whisky duty falls in phases from 150% to 40%; British auto tariffs from 100% to 10% under a quota.",
            "GOV.UK (gov.uk) \u2014 'UK-India Free Trade Agreement: Business Mobility explainer': details the mobility provisions \u2014 business visitors, intra-corporate transferees, contractual service suppliers (route extended to additional sectors, with a quota of 1,800 Indian chefs de cuisine, yoga teachers and classical musicians a year), and independent self-employed professionals in listed sectors such as architecture and engineering able to deliver contracted services in the UK for up to a year; the agreement does not change the UK's points-based visa system."
        ]),
        "diaspora_angle": "Britain's 1.9-million-strong Indian community \u2014 and especially the IT engineers, consultants and managers posted there temporarily by Indian firms \u2014 gain real take-home pay from July 15, when the India-UK CETA's Double Contribution Convention stops them paying social security in both countries, while diaspora-run exporters get new openings into the British market.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India presses Gulf to raise pay for its workers ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India presses Gulf to raise minimum pay for workers")
    print("="*60)

    slug = "india-pushes-gulf-states-higher-minimum-wages-indian-workers-gcc-remittances-20260624"
    headline = "India Is Quietly Telling the Gulf to Pay Its 5 Million Workers More. It's a Billion-Dollar Bet With a Catch."
    subheadline = "Over the past several months, Indian diplomats across all six Gulf states have sharply raised the minimum salaries they recommend for Indian workers \u2014 a drive that could pull in billions more in remittances, but also risks pricing some of India's own citizens out of the market."

    body = """The Indian government has opened a quiet but consequential front in the Gulf, and it is being waged not over oil or trade but over wages. Over the past several months, Indian diplomatic missions across all six member states of the Gulf Cooperation Council \u2014 Bahrain, Kuwait, Qatar, Oman, Saudi Arabia and the United Arab Emirates \u2014 have sharply increased the minimum salaries they recommend for Indian nationals working at private and public firms in those countries. It is a campaign aimed squarely at lifting the pay of one of the most important and least visible engines of India's economy: its Gulf workforce.

The numbers explain why New Delhi cares so much. More than five million Indian nationals are believed to be employed across the oil-exporting Gulf, the single largest group within a migrant workforce of over 20 million. These migrants do much of the region's hardest and most dangerous work \u2014 construction, oil-field labour, transport, domestic and service jobs \u2014 and together with other foreign workers they make up nearly half of the GCC's roughly 50 million people. The money they send home is a lifeline, not just for their families but for India's balance of payments.

## What India Is Doing

The lever India is pulling is the minimum referral wage \u2014 the salary floor its embassies recommend, and in practice often require, for contracts they will attest for Indian workers. By raising those floors, Indian diplomats are trying to push up the baseline pay across the Gulf labour market for their citizens.

"We want the Indian workforce to be paid higher salaries. Inflation, the value of the Indian currency and a rise in the cost of living in the Gulf were the factors that led to the decision," said Y.S. Kataria, a spokesman for the Ministry of Overseas Indian Affairs in New Delhi. The logic is straightforward: a weaker rupee means each Gulf dollar buys more back home, but rising prices in the Gulf erode what workers can save, and the old salary floors had simply fallen out of step with reality.

## The Catch

The strategy carries a real risk, and Indian officials know it. If Indian workers become more expensive than the alternatives, Gulf employers can simply hire elsewhere \u2014 from Pakistan, Bangladesh, Nepal or the Philippines, all of which supply large numbers of migrant workers and may not impose the same wage floors. India would then be trading higher pay for some workers against fewer jobs for others.

"Of course it will encourage companies to look at Bangladesh and Pakistan as more viable options to get migrant workers," warned Mohammed Jindran, managing director of the UAE-based recruitment agency Overseas Labour Supply. Some GCC governments have themselves expressed displeasure at India's push, wary of any move that raises their labour costs or looks like an outside government dictating terms inside their economies. The success of the campaign, by India's own admission, is not yet clear.

## A Policy With History

This is not New Delhi's first turn on Gulf wages, and the recent history shows how politically charged the issue is. In September a few years ago, the government had actually cut minimum referral wages by 30 to 50 percent for the six Gulf states \u2014 a move migrant-welfare groups said left workers exploited and underpaid. After a sustained civil-society campaign, the government reversed course and withdrew those circulars, a decision welfare advocates said would help millions of Indian workers in the Gulf. The current drive to raise wages is, in effect, the pendulum swinging hard the other way.

## Why It Matters for the Diaspora

For the millions of Indian families with a breadwinner in the Gulf, this is among the most directly material policy stories going. A higher salary floor can mean meaningfully more money wired home each month \u2014 for school fees, home loans, medical bills \u2014 from the segment of the diaspora that can least afford to be shortchanged and is most exposed to exploitation. Remittances from the Gulf are a quiet pillar of countless household budgets across Kerala, Uttar Pradesh, Bihar, Tamil Nadu and beyond, and a key source of the foreign exchange that helps steady the rupee.

But the same workers are the ones most vulnerable to the downside. If the floor is set too high and employers pivot to cheaper labour from rival countries, it is blue-collar Indians \u2014 not the white-collar professionals in Dubai's towers \u2014 who lose the jobs. The coming months will reveal whether New Delhi has calibrated its push well enough to lift pay without pricing its own people out of the market that millions of Indian families depend on.
"""

    # Hero: Wikimedia Commons photo (scene/place, not a named person)
    img_url, _ = pick_commons([
        "construction workers Dubai UAE",
        "Dubai construction site labour",
        "migrant workers Gulf construction",
        "Dubai skyline construction"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Construction in the Gulf, where more than five million Indians work \u2014 the single largest migrant group in the region"

    if not img_url:
        px = fetch_pexels_image("construction workers Dubai labour")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Migrant labour in the Gulf, where India is pressing for higher minimum wages for its workers"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-labour",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Asian Voice / Reuters (asian-voice.com, June 2026) \u2014 'India seeks higher pay for millions of Gulf workers': India is pressing Gulf states to raise wages for millions of Indians working there; over 5 million Indian nationals employed in the oil-exporting Gulf, the single largest group in a migrant workforce of more than 20 million, accounting for nearly half of the GCC's ~50 million population; over the past seven months Indian diplomats in Bahrain, Kuwait, Qatar, Oman, Saudi Arabia and the UAE sharply increased recommended minimum salaries; MOIA spokesman Y.S. Kataria cited inflation, the rupee's value and rising Gulf cost of living; recruitment-agency MD Mohammed Jindran warned firms may turn to Bangladesh and Pakistan; some GCC officials expressed displeasure.",
            "CESLAM (ceslam.org, June 2026) \u2014 'India urges higher pay for Gulf workers': corroborates that India's campaign for higher pay could ripple across the region and affect workers from other labour-supplying countries such as Pakistan and Bangladesh; reiterates the MOIA's stated rationale and the risk of pricing Indian workers out of the market.",
            "Business & Human Rights Resource Centre (business-humanrights.org) \u2014 'Indian Govt. revokes directive mandating lower minimum salary for migrant workers to the Gulf, following civil society campaign': documents the earlier September directive that cut minimum referral wages by 30\u201350% for the six Arab Gulf countries, the civil-society campaign by the Gulf JAC and Emigrants' Welfare Forum (Bheem Reddy Mandha) that called it exploitative, and the government's subsequent withdrawal of those circulars, a move said to help roughly 88 lakh Indian workers in the Gulf."
        ]),
        "diaspora_angle": "More than five million Indians \u2014 the largest migrant group in the Gulf and the source of remittances that sustain countless households across Kerala, UP, Bihar and Tamil Nadu \u2014 stand to earn meaningfully more if India's push to raise minimum wages succeeds, but blue-collar workers are also the ones who could lose jobs if Gulf employers pivot to cheaper labour from rival nations.",
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
