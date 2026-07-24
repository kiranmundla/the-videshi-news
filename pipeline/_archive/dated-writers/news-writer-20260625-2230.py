#!/usr/bin/env python3
"""
Videshi News Writer — June 25, 2026 (22:30 UTC / 15:30 PDT run)
2 NEW articles, dedup-checked against last ~40 news articles:
  1. US FDA sends SOS to Indian drugmakers for ifosfamide — critical cancer
     drug in short supply in the US after a Baxter contract-manufacturing
     disruption; FDA India office asked IDMA/IPA to identify Indian suppliers
     (Cipla, Zydus, Alkem, Aurobindo, GLS Pharma). Diaspora/pharma angle. NOT covered.
  2. The struck-down $100,000 H-1B fee is quietly BACK — a Boston judge
     vacated it June 8, but the district court paused that ruling June 12 and
     the govt filed an emergency stay motion with the First Circuit June 18,
     so USCIS may keep collecting the fee while the appeal proceeds. Indian
     workers are the largest H-1B cohort. NOT covered (only the strike-down was).
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
load_env(os.path.expanduser('~/workspace/.env.supabase'))
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


# \u2500\u2500\u2500 Article 1: US FDA SOS to Indian drugmakers for ifosfamide \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: US FDA SOS to Indian drugmakers for cancer drug")
    print("="*60)

    slug = "us-fda-sos-indian-drugmakers-ifosfamide-cancer-drug-shortage-cipla-zydus-alkem-2026-20260625"
    headline = "America Has Run Short of a Cancer Drug. It Just Sent an SOS to India's Drugmakers."
    subheadline = "The US FDA has quietly asked Indian manufacturers to supply ifosfamide \u2014 a chemotherapy in short supply after a US plant disruption \u2014 a reminder of how much the world's medicine cabinet leans on India."

    body = """When the United States runs low on a life-saving drug, it does not always turn inward. This month it turned to India.

The US Food and Drug Administration has sent what one industry leader bluntly called an "SOS" to Indian pharmaceutical manufacturers, seeking emergency supplies of ifosfamide, a chemotherapy used to treat testicular, bladder and lung cancers. The drug has fallen into short supply in the United States after a manufacturing disruption at the primary supplier, and American regulators are now scouring the world's largest generic-drug industry for help.

## An SOS, in Writing

The request was concrete. According to a communication dated June 19, 2026, the FDA's India office wrote to the Indian Drug Manufacturers' Association (IDMA) seeking assistance in identifying companies "currently producing or have the capability to produce" ifosfamide injection in 1-gram and 3-gram vials "to help address an ongoing drug shortage in the US." A parallel message went through the Indian Pharmaceutical Alliance (IPA), which represents the country's largest drugmakers; its secretary general, Sudarshan Jain, confirmed the US embassy had reached out and that the request had been passed to members.

Viranchi Shah, a national spokesperson for the IDMA, did not understate the moment. The disruption at the primary site, he said, made the appeal "like an SOS," precisely because it concerned a cancer drug with few alternative producers. Indian manufacturers of ifosfamide include Cipla, Zydus Lifesciences, Alkem Laboratories, Aurobindo Pharma and GLS Pharma \u2014 the last of which markets the drug in India under the brand Ipoget.

## How the Shortage Happened

The root cause lies not in India but in Illinois. A technical disruption at a contract-manufacturing site tied to Baxter International, the Deerfield-based company that is the main US supplier of ifosfamide, choked off output. Supply-chain dislocations linked to the conflict in West Asia compounded the squeeze. Officials expect the limited supply of ifosfamide injection to persist through 2026 \u2014 a long gap for a medicine on which cancer patients depend.

It is a familiar pattern. American and European shortages of specialised drugs tend to erupt when a single dominant producer stumbles, because so few plants make these complex injectables and both regions impose stringent regulatory benchmarks that are hard to scale quickly. In moments like these, the surge capacity tends to sit in India.

## The Pharmacy of the World

There is a reason Washington's first call was to New Delhi. India supplies a large share of the generic medicines Americans take every day, and its drugmakers have repeatedly been the relief valve in a crisis. During the Covid-19 pandemic, the Trump administration secured supplies of hydroxychloroquine from Indian firms. Years earlier, the FDA leaned on Indian-made alternatives to ease shortages of cancer drugs such as Doxil. The latest appeal, industry-watchers note, reinforces the same point: when the rich world's supply chain breaks, India's affordable-medicine machine is often what keeps treatment going.

The outreach is notable for another reason. The FDA is reportedly willing to consider not only its own registered facilities but also non-registered Indian plants with strong compliance records and proven quality standards \u2014 a sign of how urgently the agency wants to broaden its sourcing options. And it lands against a delicate backdrop: even as Washington and New Delhi negotiate trade terms, generic drugs have so far been kept outside the scope of US tariffs, a carve-out this episode quietly vindicates.

## Why It Matters for the Diaspora

For the millions of Indians abroad, the story cuts close in two ways. The most immediate is personal: an NRI family with a relative undergoing cancer treatment in a US hospital has a direct stake in whether ifosfamide stays on the shelf, and it may well be an Indian-made vial that fills the gap. The reassurance that the world's generic-drug powerhouse is being asked to step in is not abstract \u2014 it is the difference between a treatment delayed and a treatment delivered.

The second is a matter of pride and perception. The Indian pharmaceutical industry has spent years dogged by headlines about quality lapses and FDA inspection failures at individual plants. An explicit request from the same regulator \u2014 asking India to rescue American patients \u2014 is a counter-narrative the diaspora will recognise. It is also a reminder of the leverage India quietly holds in global health, the kind of soft power that travels with every NRI who explains to a sceptical neighbour where their affordable medicines actually come from.

For investors among the diaspora, there is a sharper edge too. Listed names such as Cipla, Alkem and Zydus drew immediate market attention on the news, a reminder that India's role as the pharmacy of the world is not just a point of pride but a recurring business opportunity \u2014 one that surfaces every time a shortage erupts an ocean away."""

    img_url, ititle = pick_commons([
        "Chemotherapy vials",
        "Cipla inhaler",
        "pharmaceutical manufacturing India",
        "intravenous medication vial"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Vials of chemotherapy drugs; the US FDA has asked Indian manufacturers to help supply the cancer drug ifosfamide"

    if not img_url:
        px = fetch_pexels_image("pharmaceutical vials medicine")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The US FDA has sought Indian-made supplies of a cancer drug now in short supply"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "pharma",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Livemint (livemint.com, June 2026) \u2014 'US FDA sends SOS to Indian drugmakers for critical cancer medicine amid US shortage': the US FDA reached out to Indian manufacturers for ifosfamide, used to treat testicular, bladder and lung cancers, currently in short supply; per two Indian government officials and a document reviewed by Mint, the FDA India Office wrote to the IDMA on June 19, 2026 seeking manufacturers capable of supplying ifosfamide Injection 1 g and/or 3 g; Indian makers include Cipla, Zydus Lifesciences, Alkem Laboratories and GLS Pharma (which markets Ipoget); the shortage stems from a technical disruption at a contract manufacturing site of Baxter International (Deerfield, Illinois), the primary US supplier, plus supply-chain disruptions from the war in West Asia; limited supply expected to continue through 2026; India's oncology/cancer-treatment market valued at $947.84 million.",
            "The Hindu BusinessLine (thehindubusinessline.com, June 24, 2026) \u2014 'US cancer drug supply reinforces role of Indian drugmakers, say industry insiders': IDMA national spokesperson Viranchi Shah said the USFDA's India office contacted the government and IDMA for the supply of the cancer drug following a short supply from a manufacturing-site disruption, describing it as 'like an SOS'; the Baxter site was a major player; companies like Zydus, Aurobindo and Alkem make the drug; IPA secretary general Sudarshan Jain confirmed the US embassy in India had contacted them and the request was communicated to members; during Covid the Trump administration secured hydroxychloroquine from Indian companies; generic drugs have so far been kept out of the ambit of US tariffs.",
            "Trade Brains (tradebrains.in, June 2026) \u2014 '3 Pharma Stocks Likely to Benefit From the Shortage of Cancer Drugs in the US': the USFDA reached out to Indian drug manufacturers through the IDMA seeking additional sources of ifosfamide; preference given to FDA-registered facilities but the regulator is also considering non-registered Indian plants with strong compliance history and proven quality standards; listed firms Cipla, Alkem Laboratories and Zydus Lifesciences expected to attract investor attention; Cipla shares rose about 2.4% in the day's trade."
        ]),
        "diaspora_angle": "An NRI family with a relative in cancer treatment in the US has a direct stake in whether ifosfamide stays on the shelf \u2014 and an Indian-made vial may be what fills the gap; the FDA's explicit appeal to Indian drugmakers underscores India's standing as the pharmacy of the world and offers the diaspora both reassurance and a recurring investment angle in names like Cipla, Alkem and Zydus.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: $100,000 H-1B fee quietly back in effect pending appeal \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: $100K H-1B fee quietly back pending appeal")
    print("="*60)

    slug = "h1b-100000-dollar-fee-back-in-effect-stay-first-circuit-appeal-indian-workers-2026-20260625"
    headline = "A Judge Killed Trump's $100,000 H-1B Fee. Two Weeks Later, It's Quietly Back."
    subheadline = "A Boston court struck down the fee on June 8 as an unlawful tax \u2014 then paused its own ruling. USCIS may keep collecting the six-figure charge while the appeal proceeds, and Indians, the largest H-1B group, are again left guessing."

    body = """For a few days this month, it looked like the most punishing immigration cost of the Trump era had been erased. It hadn't. The $100,000 fee on new H-1B visas is, for now, back in force \u2014 and the whiplash is its own kind of penalty.

On June 8, 2026, US District Judge Leo Sorokin in Boston struck down the fee, ruling that it amounted to an unlawful tax that Congress never authorised the president to impose. The decision, in a lawsuit led by 20 Democratic state attorneys general, was sweeping: the court declared the policy in excess of statutory authority, procedurally deficient, "arbitrary and capricious," and vacated it in its entirety. For the hundreds of thousands of Indians who form the backbone of the H-1B programme, it read like a reprieve.

## The Reprieve That Wasn't

The relief lasted barely four days. On June 12, the government appealed to the US Court of Appeals for the First Circuit and asked the district court to pause the effect of its own ruling. Judge Sorokin declined a full stay but temporarily delayed his decision \u2014 keeping the fee in place \u2014 to give the appeals court time to weigh in, on the condition that the government file its stay request with the First Circuit by June 18. The government met that deadline, filing an emergency motion on June 18 asking the appellate court to keep the fee alive while the appeal is heard.

The practical upshot, immigration lawyers say, is unambiguous. USCIS is currently permitted to keep requiring the $100,000 payment for H-1B petitions filed for, or only approvable through, consular notification. Employers planning affected filings should assume the fee still applies "unless and until a court orders otherwise." The case now sits before the First Circuit as State of California v. Mullin.

## What the Fee Actually Is

The charge traces to a presidential proclamation of September 19, 2025, which imposed a $100,000 payment on certain new H-1B petitions \u2014 a staggering jump from the $2,000 to $5,000 in fees that had typically applied. The administration cast the H-1B programme as a vehicle "to replace, rather than supplement, American workers with lower-paid, lower-skilled labor," and argued the fee was a lawful penalty within the president's broad power to restrict the entry of foreign nationals deemed detrimental to US interests.

Judge Sorokin disagreed on the law, not the politics. Citing the Supreme Court's February ruling that struck down Trump's emergency-powers tariffs, he reasoned that the president had no more authority to levy this tax than he did those duties. The White House has said it is confident the ruling will be reversed on appeal. The fee, as written, is set to expire in September 2026, though it can be extended \u2014 making the appeal's timing all the more consequential.

## Why Indians Bear the Brunt

No nationality has more riding on the outcome than Indians, who for years have received the lion's share of H-1B visas. The fee, if upheld, would reshape who even gets to apply. A six-figure charge is one many startups, smaller firms, hospitals and universities simply cannot absorb \u2014 precisely the employers that have long sponsored Indian engineers, researchers and doctors. India's largest IT services firms have already seen H-1B approvals slump about 40% this year, pushing work offshore and toward local US hiring.

There is a human cost to the legal ping-pong itself. When the fee was first announced last September, Indian workers and their employers scrambled over a frantic weekend to get people back into the country before it bit. The on-again, off-again litigation since has made it nearly impossible to plan a career, a family move, or a return trip home with any confidence. For a community whose lives are stitched across two continents, uncertainty is not a footnote \u2014 it is the condition.

## What the Diaspora Should Watch

The near-term signal to watch is the First Circuit's response to the government's stay motion: if the appeals court keeps the fee in place, the six-figure cost remains a live reality for the upcoming filing season; if it lifts the pause, the fee falls away again pending the full appeal. Either way, the underlying question \u2014 whether a president can attach a $100,000 price tag to a work visa by proclamation \u2014 is now headed for a definitive answer.

For Indian professionals weighing the American route, the lesson of June is sobering. A favourable ruling is not the same as a settled rule. Until the appeals run their course, the prudent assumption is that the fee applies \u2014 and that the gap between what a court says and what an applicant must pay can stay open for a long time. It is also why a growing number of Indian H-1B holders are quietly studying Plan B, from Canada's employer-independent PR routes to a return to India's expanding job market."""

    img_url, ititle = pick_commons([
        "United States Passport Visa Pages",
        "Passport stamps of the United States Visum",
        "US passport visa",
        "United States visa"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "A US visa in a passport; a $100,000 fee on new H-1B petitions is back in effect while a federal appeal proceeds"

    if not img_url:
        px = fetch_pexels_image("passport visa immigration document")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The $100,000 H-1B fee remains in effect while the government's appeal proceeds"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "WR Immigration / Wolfsdorf (wolfsdorf.com, ~June 15, 2026) \u2014 'Court Temporarily Reinstates USCIS Authority to Collect $100,000 H-1B Consular Processing Fee Pending Appeal': a Massachusetts federal district court on June 12, 2026 temporarily stayed its June 8, 2026 decision vacating USCIS's policy implementing the $100,000 H-1B fee from Trump's September 19 proclamation; as a result USCIS is currently permitted to continue requiring the fee for H-1B petitions filed for, or only approvable through, consular notification while appellate review proceeds; the government appealed on June 12 to the First Circuit and the district court paused its ruling to let the First Circuit consider a stay, requiring the government to file its stay request by June 18 for the pause to remain in effect; appeal pending in State of California, et al. v. Mullin, et al., No. 26-1699 (1st Cir.).",
            "Musillo Unkenholt Immigration Law (muimmigration.com, ~June 23, 2026) \u2014 'Government Asks Appeals Court to Keep H-1B Fee in Place While Lawsuit Continues': timeline \u2014 Sept 19, 2025 proclamation requiring $100,000 for certain new H-1B petitions; Dec 12, 2025 California-led states sued; June 8, 2026 Massachusetts judge ruled the government lacked authority and set aside the implementing guidance; the government appealed to the First Circuit and asked the district court to pause the ruling; June 12, 2026 the district court declined a full stay but temporarily delayed the effect of its decision, keeping the fee in place; June 18, 2026 the government filed an emergency motion with the First Circuit to keep the fee in place while the appeal is pending.",
            "Reuters (reuters.com, June 8, 2026) \u2014 'Trump's $100,000 H-1B visa fee is unlawful, US judge rules': US District Judge Leo Sorokin in Boston struck down the fee in a suit by 20 Democratic state attorneys general, concluding it was an unlawful tax Congress never authorized; he cited the Supreme Court's February ruling against Trump's emergency-powers tariffs; the White House (spokeswoman Taylor Rogers) said it is confident the order will be reversed on appeal.",
            "SHRM (shrm.org, June 2026) \u2014 'Federal Court Strikes Down $100K H-1B Fee' (editor's note): the order has been stayed pending a decision from the First Circuit after the Trump administration appealed; Judge Sorokin ruled June 8 that Congress never authorized the fee, vacating it in its entirety and finding it in excess of statutory authority, procedurally deficient, and arbitrary and capricious under the APA; the proclamation characterized the H-1B program as designed to replace rather than supplement American workers; the fee is set to expire September 2026 but can be extended."
        ]),
        "diaspora_angle": "Indians receive the largest share of H-1B visas, so the on-again, off-again fate of Trump's $100,000 fee \u2014 struck down on June 8 but back in force days later while the First Circuit weighs the government's appeal \u2014 directly governs whether Indian engineers, doctors and researchers can still realistically be sponsored, and the resulting uncertainty is pushing many toward Canada or a return to India.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-25 22:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (FDA SOS ifosfamide): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (H-1B fee back): {'OK id=' + str(id2) if id2 else 'FAILED'}")
