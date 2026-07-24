#!/usr/bin/env python3
"""
Videshi News Writer — June 25, 2026 (12:30 UTC / 05:30 PDT run)
2 NEW articles, dedup-checked against last ~40 news articles:
  1. Fire at the STT/Tata Communications data centre in New Delhi (Greater
     Kailash, June 5) caused "extensive damage"; Matrix Cellular fears losing
     20+ years of data, ISP R2 Net ~$2M losses, and Google Cloud India hit by
     network disruptions/latency still unresolved as of June 23. Tech-infra /
     data-sovereignty story. Distinct from any prior coverage (none on this).
  2. ED searches Rajesh Exports (world's largest gold processor) at 9
     Bengaluru/Mumbai sites under FEMA, after SEBI's Rs 15.15 lakh crore
     revenue-inflation order (Valcambi, Switzerland). 40% physical-gold
     shortfall, ~Rs 3,000cr suspicious trade adjustments, UAE shell entities,
     unverified Rs 1,000cr African-mine ODI, ~$20M siphoned via benamidars.
     Economy/corporate-governance story. Distinct from the bullion-price
     pieces (those are gold *prices*; this is gold-*company* fraud).
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


# \u2500\u2500\u2500 Article 1: Delhi data centre fire \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: STT/Tata Delhi data centre fire")
    print("="*60)

    slug = "stt-tata-delhi-data-centre-fire-extensive-damage-matrix-cellular-google-cloud-data-loss-20260625"
    headline = "A Fire at a Tata Data Centre in Delhi May Have Erased 20 Years of One Company's Data. Google Cloud Was Hit Too."
    subheadline = "A June 5 blaze at the STT-Tata facility in Greater Kailash caused 'extensive damage,' and three weeks on the recovery is still failing \u2014 a warning about how much of digital India sits in a handful of buildings."

    body = """A single fire in a south Delhi building has done what hackers spend years trying to achieve: it has wiped out, possibly forever, more than two decades of one company's records. A blaze that broke out in the early hours of June 5 at the STT Global Data Centres India facility in Greater Kailash \u2014 jointly owned by Singapore's ST Telemedia and India's Tata Communications \u2014 caused damage so severe that, three weeks later, clients are being told their data may never come back.

The most striking casualty is Matrix Cellular, an Indian firm that sells international SIM cards to travellers. "Matrix has potentially lost access to over 20 years of accumulated operational and business data stored in the affected Tata data centre," its chief executive, Gaurav Khanna, told Reuters. In a June 15 letter to Matrix that had not previously been reported, a Tata Communications unit, Novamesh, wrote that the fire was "so severe that it caused extensive damage" and conceded the obvious: "Despite our ongoing best efforts to recover the data, the severity of the damage ... presents significant challenges to the recovery of the affected data and systems."

## Not Just One Client

The damage radiates outward. The internet service provider R2 Net estimated losses of around $2 million from the outage. And in a sign of how deeply foreign tech giants rely on Indian infrastructure, some of Google Cloud's intermittent network disruptions in India were also linked to the same fire, according to a source with direct knowledge of the matter. Google said a fire at a third-party data centre had forced an emergency shutdown of networking equipment, and in an update on June 23 warned that some users could keep experiencing latency until the facility is fully restored \u2014 nearly three weeks after the flames were put out.

Television footage from inside the building on the day of the fire showed the scale of it: server racks and electrical infrastructure burnt through, ceiling panels collapsed, debris strewn across the floor. Delhi fire authorities said the blaze originated in lithium battery units \u2014 the same battery chemistry that powers the backup systems data centres depend on \u2014 though the exact cause is still under investigation. Ten fire tenders were deployed, the operation lasted several hours, two firefighters were injured, and the damage was eventually confined to the third floor.

## "Business Continuity," Tested

Tata Communications told Indian stock exchanges on the very day of the fire that it had activated business continuity protocols to minimise disruption. STT Global Data Centres India later said it was supporting affected customers, including by shifting them to alternate capacity where possible, and that an "independent technical root cause analysis is underway." Neither Tata Communications nor ST Telemedia responded to Reuters queries about the incident.

But the episode has exposed an uncomfortable truth about modern infrastructure: business continuity is only as good as a client's own backups. Companies that mirrored their data elsewhere can recover; those that trusted a single facility to hold their only copy \u2014 as Matrix appears to have done \u2014 are left with letters of apology and lawyers. Data centres market themselves on redundancy, fire suppression and tier-rated reliability, which is exactly why a fire that destroys decades of records is so jarring.

## Why It Matters for the Diaspora

For the Indian diaspora, this is not an abstract infrastructure story \u2014 it is a reminder of where their digital lives actually live. NRIs lean on Indian cloud and telecom services constantly: international SIMs bought from firms like Matrix for trips home, fintech and remittance apps that route through Indian data centres, the e-governance portals used to renew an OCI card, file taxes, manage NRI bank accounts or pay for property back home. When a building in Delhi burns and Google Cloud wobbles across the country, the outage can reach an app opened in New Jersey or Dubai.

It also lands at a sensitive moment for India's ambitions. The country is racing to become a global data-centre hub, with Amazon, Google and domestic players pouring billions into capacity on the promise that India can host the world's data safely. A fire that may have destroyed 20 years of one client's records, knocked a global cloud provider offline regionally, and resisted recovery for three weeks is a hard advertisement to counter. For diaspora investors weighing India's digital-infrastructure boom, and for families who quietly trust these systems with their documents and money, the lesson is old but newly urgent: keep your own copy, because even the cloud can catch fire.
"""

    img_url, ititle = pick_commons([
        "data center server room",
        "server racks data centre",
        "data center servers India"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Server racks inside a data centre; a June 5 fire at the STT-Tata facility in Delhi caused extensive damage"

    if not img_url:
        px = fetch_pexels_image("data center server room")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A data-centre server room; a fire at the STT-Tata Delhi facility left clients fearing decades of lost data"

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
            "Reuters (reuters.com, June 24, 2026) \u2014 'Exclusive: STT, Tata Delhi data centre fire leaves clients fearing decades of data lost; Google hit' by Aditya Kalra and Munsif Vengattil: a fire at the STT Global Data Centres India facility owned by Singapore's ST Telemedia and India's Tata Communications caused 'extensive damage'; Tata told exchanges June 5 it activated business continuity plans after an early-morning fire; Matrix Cellular said it is struggling to recover more than two decades of data; some Google Cloud intermittent network disruptions in India are linked to the fire; Novamesh's June 15 letter said the fire was 'so severe that it caused extensive damage'; STT said an independent technical root cause analysis is underway; CEO Gaurav Khanna: 'Matrix has potentially lost access to over 20 years of accumulated operational and business data.'",
            "The Hindu BusinessLine (thehindubusinessline.com, June 24, 2026) \u2014 'STT, Tata Delhi data centre fire leaves clients fearing decades of data lost; Google hit': Delhi fire authorities said the fire occurred in lithium battery units; Tata Communications unit Novamesh told a client in the June 15 letter the fire was 'so severe that it caused extensive damage' and hindered services; Tata Communications and ST Telemedia did not respond to Reuters queries.",
            "Outlook Business (outlookbusiness.com, June 24, 2026) \u2014 'Fire at Tata-STT Data Centre Threatens 20 Yrs of Matrix Cellular Data, Disrupts Google Cloud': the June 5 fire at the data centre in New Delhi's Greater Kailash caused extensive damage; Matrix Cellular faces loss of over 20 years of data while R2 Net estimates $2 million in losses; Google Cloud flagged network disruptions in India linked to the facility, with no workaround as of June 23; ten fire tenders were deployed, the operation lasted several hours, two firefighters were injured, and damage was confined to the third floor.",
            "Madhyamam (madhyamamonline.com, June 24, 2026) \u2014 'Tata says Delhi data centre fire caused extensive damage': the fire broke out June 5 at the STT facility; Tata activated business continuity measures and later told clients the severity of the damage was delaying restoration; Google said a fire at a third-party data centre forced an emergency shutdown of networking equipment and, in a June 23 update, warned some users could continue to experience latency until the facility is fully restored.",
            "Devdiscourse (devdiscourse.com, June 24, 2026) \u2014 'Blaze at New Delhi Data Center Sparks Data Recovery Crisis': a fire at a New Delhi data center owned by Singapore's ST Telemedia and India's Tata Communications resulted in significant damage; the facility activated emergency business continuity protocols; affected clients include Matrix Cellular (potential loss of two decades of operational data), Google Cloud (sporadic network disruptions) and R2 Net; authorities suggest the fire began in lithium battery units."
        ]),
        "diaspora_angle": "NRIs depend on Indian cloud and telecom infrastructure daily \u2014 from international SIMs and remittance apps to the e-governance portals used to renew OCI cards, file taxes and manage NRI accounts \u2014 so a Delhi data-centre fire that may have destroyed 20 years of one firm's records and disrupted Google Cloud across India is a direct warning about how concentrated, and how fragile, the digital systems holding diaspora documents and money can be.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: ED searches Rajesh Exports \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: ED searches Rajesh Exports (FEMA / gold)")
    print("="*60)

    slug = "ed-searches-rajesh-exports-fema-gold-mismatch-sebi-15-lakh-crore-valcambi-revenue-inflation-20260625"
    headline = "India's Financial-Crime Agency Raided the World's Biggest Gold Processor. The Books Allegedly Didn't Match the Vault."
    subheadline = "After SEBI accused Rajesh Exports of inflating revenue by an almost unimaginable Rs 15.15 lakh crore, investigators found the physical gold was 40% short of what the ledgers claimed \u2014 and money trails running to the UAE and African mines that no one can fully account for."

    body = """The numbers in this case are so large they strain belief, which is part of why it matters. On Tuesday, India's Enforcement Directorate raided nine premises in Bengaluru and Mumbai linked to Rajesh Exports, a company that calls itself the world's largest gold processor, and the agency emerged with a set of findings that read less like an accounting dispute than a hollowed-out shell. Among them: when investigators physically counted the gold, the stock on hand was roughly 40% lower than what the company's own books recorded.

The searches, conducted under the Foreign Exchange Management Act (FEMA), follow a 109-page interim order this month from the markets regulator SEBI that contained an even more staggering figure. SEBI alleged that between April 2020 and September 2025, Rajesh Exports overstated its consolidated revenue by about Rs 15.15 lakh crore \u2014 roughly $159 billion \u2014 largely by attributing enormous sales to overseas subsidiaries, particularly its Switzerland-based refining unit Valcambi, even though that subsidiary's audited standalone accounts showed only a fraction of the amounts. SEBI was careful to clarify that the figure is the cumulative value of allegedly misstated entries from circular transactions routed repeatedly through multiple entities, not money that physically changed hands. It is, by SEBI's account, unprecedented in India's accounting probes.

## What the Raids Turned Up

The ED's preliminary findings sketch a web of suspicious cross-border flows. The agency said it found set-offs of trade payables and receivables of about Rs 3,000 crore ($317 million) involving "suspicious foreign parties" based in the UAE and other jurisdictions, described by officials as entities of "dubious credentials." Records for those foreign transactions were, in many cases, simply missing. The agency also flagged that "contemporaneous records and documentation of claimed investment of 10.35 billion rupees" \u2014 over Rs 1,000 crore \u2014 "into African Mines were neither found nor provided by the company as yet."

Investigators said multiple trades in Rajesh Exports shares were routed through "benamidars," or proxy holders used to disguise true ownership, and that over $20 million may have been siphoned out of the country through such transactions. The ED is also examining roughly Rs 3,000 crore of trade receivables that were adjusted against gold imports whose delivery it called "suspicious" \u2014 suggesting the paperwork may not reflect real movements of metal. SEBI separately found that the company transferred Rs 338.90 crore to chairman Rajesh Mehta's personal bank account and received Rs 232.44 crore back, without producing loan agreements or board approvals to justify it.

## A Company That Doesn't Add Up

Some of the smaller details are the most telling. The ED alleged that despite a consolidated revenue of Rs 7.7 lakh crore, the company's chief financial officer had not been paid since 2020 and its managing director drew just Rs 17,000 a month \u2014 the kind of figures that do not fit a genuine global gold giant. SEBI has restrained Mehta from dealing in the company's securities until further orders. Rajesh Exports has denied any wrongdoing, saying its reported revenues were correct and blaming a "communication gap" with the regulator. Curiously, its shares hit the 5% upper circuit after the raids, closing at Rs 108.25 on the BSE \u2014 a sharp recovery from a 52-week low of Rs 73.20 hit after SEBI's order.

## Why It Matters for the Diaspora

Gold is the diaspora's emotional and financial anchor, and Rajesh Exports sits close to the heart of the trade that serves it. Through its Shubh Jewellers retail chain and its Valcambi refinery \u2014 one of the world's most trusted sources of minted gold bars and coins \u2014 the company touches the supply chain that NRIs buy from for weddings, festivals and savings. An allegation that a marquee Indian gold name fabricated revenue on this scale, ran metal through suspicious UAE channels and came up 40% short on physical stock is a jolt to confidence in the integrity of that chain.

It also speaks to the corporate-governance risk that shadows diaspora money flowing back to India. Many NRIs invest in Indian equities, jewellery brands and gold instruments precisely because they trust the names they grew up with; cases like this are why regulators' clean-up matters to them directly. For now the allegations are interim and unproven, and Rajesh Exports is contesting them. But for a community that treats gold as both ornament and insurance, the message is sobering: even the biggest names in Indian gold are not beyond the reach \u2014 or the need \u2014 of scrutiny.
"""

    img_url, ititle = pick_commons([
        "gold bars Valcambi refinery",
        "gold bullion bars refinery",
        "gold ingots stacked"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Refined gold bars; the ED found Rajesh Exports' physical gold stock about 40% short of its books"

    if not img_url:
        px = fetch_pexels_image("gold bars refinery")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Refined gold bars; India's ED raided gold processor Rajesh Exports under FEMA after a SEBI fraud order"

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
            "Reuters (reuters.com, June 24, 2026) \u2014 'India financial crime agency flags forex breaches, missing records at Rajesh Exports': the ED said searches at nine locations in Mumbai and Bengaluru on Tuesday found set-offs of trade payables and receivables of about 30 billion rupees ($316.91 million) involving suspicious foreign parties based in the UAE and other jurisdictions; missing records of foreign transactions; 'contemporaneous records and documentation of claimed investment of 10.35 billion rupees ($109.33 million) into African Mines were neither found nor provided'; flagged suspicious block trades and share price manipulation; the probe follows a SEBI investigation alleging the firm overstated revenue at Swiss refining unit Valcambi by $159 billion. ($1 = 94.6650 rupees).",
            "The Hindu BusinessLine (thehindubusinessline.com, June 23, 2026) \u2014 'ED searches against Rajesh Exports after SEBI scrutiny': the ED conducted searches Tuesday under FEMA at the Bengaluru-headquartered company; SEBI's interim order alleges Rajesh Exports inflated consolidated revenues by more than Rs 15 lakh crore over five years by attributing massive revenues to overseas subsidiaries, particularly Switzerland-based Valcambi SA, despite the subsidiary's audited standalone statements showing a fraction of those amounts; SEBI restrained Chairman and MD Rajesh Mehta from dealing in the company's securities; the company denied irregularities, citing a 'communication gap.'",
            "LiveMint (livemint.com, June 24, 2026) \u2014 'ED searches Rajesh Exports premises over Rs 3,000-cr dubious deals, gold mismatch': searches at nine premises examining benami share transactions, gold-inventory discrepancies and questionable overseas transactions; an ED official said over $20 million may have been siphoned via benamidars; 'physical verification carried out during the searches has shown that the gold stock found was around 40% lower than the stock reflected in the books'; ~Rs 3,000 crore of trade receivables allegedly adjusted against gold imports of suspicious delivery; shares hit the 5% upper circuit, closing at Rs 108.25 on the BSE, recovering from a 52-week low of Rs 73.20; ODI in African gold mining assets also under examination.",
            "Outlook Business (outlookbusiness.com, June 24, 2026) \u2014 'ED Raids Rajesh Exports in Bengaluru Days after SEBI's Rs 15.15 Lakh Cr Fraud Findings': SEBI's 109-page interim ex-parte order alleged Rajesh Exports, chairman Rajesh Mehta and related entities created multiple layers of transactions obscuring fund movement; between April 2020 and September 2025 the company transferred Rs 338.90 crore to Mehta's personal account and received Rs 232.44 crore back without loan agreements or board approvals; the Rs 15.15 lakh crore figure represents the cumulative value of allegedly misstated entries from repeated circular transactions, not funds that actually changed hands; SEBI imposed interim restrictions.",
            "Inshorts / agencies (inshorts.com, June 24, 2026) \u2014 'Rajesh Exports CFO wasn't paid since 2020, MD got Rs 17,000/month: ED in Rs 15 lakh cr fraud case': the ED alleged the world's largest gold processor's CFO received no salary since 2020 and its MD drew only Rs 17,000/month despite consolidated revenue of Rs 7.7 lakh crore; follows SEBI's allegation the firm inflated revenue by Rs 15.15 lakh crore; raids were carried out at nine locations; suspicious block trades also found."
        ]),
        "diaspora_angle": "Through its Shubh Jewellers chain and the Valcambi refinery \u2014 a globally trusted source of minted gold bars and coins \u2014 Rajesh Exports sits close to the supply chain NRIs buy from for weddings, festivals and savings, so allegations that a marquee Indian gold name fabricated revenue on a record scale, routed metal through suspicious UAE channels and came up 40% short on physical stock strike directly at the diaspora's confidence in the integrity of Indian gold and in the Indian equities and jewellery brands many of them invest in.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-25 12:30 UTC run")
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    print("\n" + "="*60)
    print(f"DONE. Inserted IDs: {ids}")
    print("="*60)
