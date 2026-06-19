#!/usr/bin/env python3
"""
Videshi News Writer — June 19, 2026 (16:30 UTC run)
2 NEW articles:
  1. RBI scraps rate caps on NRI deposits to pull in diaspora dollars (economy)
  2. AAPI physicians cheer court blocking the $100K H-1B physician fee (immigration/healthcare)
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


# ─── Article 1: RBI scraps NRI deposit rate caps ────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: RBI scraps NRI deposit rate caps")
    print("="*60)

    slug = "rbi-removes-nri-deposit-rate-caps-fcnr-nre-diaspora-dollars-20260619"
    headline = "The RBI Just Told Banks to Pay NRIs Whatever It Takes. Deposit Rates Have Already Jumped to 7%."
    subheadline = "In a move last used during the 2013 Taper Tantrum, the Reserve Bank has scrapped interest-rate ceilings on FCNR(B) and long-term NRE deposits until September 30 and is absorbing banks' hedging costs \u2014 a direct bid for the diaspora's dollars that has pushed rates from around 3% to as high as 7.1%."

    body = """For more than a decade, the interest the Reserve Bank of India allowed banks to pay on non-resident deposits sat under a firm ceiling. This week, that ceiling came off \u2014 and the timing tells the whole story. With the rupee bruised by months of war-driven oil prices and the country hungry for hard currency, the central bank has thrown open the door to the one pool of capital it can always count on: the savings of Indians living abroad.

In notifications issued on June 17, the RBI temporarily withdrew the interest-rate cap on fresh Foreign Currency Non-Resident (Bank), or FCNR(B), deposits of three-to-five-year tenors, and lifted the restriction on rates for non-resident external (NRE) rupee deposits of three years and above. Both relaxations apply to fresh deposits and to those renewed on maturity, and both run until September 30, 2026. The intent is blunt: give banks the freedom to pay whatever it takes to bring overseas money home.

## Rates Have Already Doubled

Banks did not wait. Interest rates on FCNR(B) dollar deposits in the three-to-five-year bucket have been pushed up to roughly 6 to 7.1 percent, from the 3 to 4 percent levels that prevailed earlier. For an NRI who has parked dollars in an Indian bank at the old rate, the gap is dramatic enough that many are scrambling to act. According to reports, several large depositors have already instructed banks to prematurely close existing deposits and redeploy the funds into the new, higher-paying schemes, while others are shifting money across banks chasing the best rate.

That rush has created a wrinkle. Because the RBI's sweetened terms apply only to fresh deposits and to those that have actually matured, existing FCNR(B) holders are stuck earning their lower contracted rates unless their bank lets them break and rebook. Commercial banks have now approached the RBI seeking permission to allow existing customers to prematurely withdraw and re-lodge their deposits under the new framework \u2014 a question of regulatory clarity that thousands of NRI savers are watching closely.

## A Playbook From 2013

This is not improvisation. The FCNR(B) mechanism is the same tool the RBI deployed in 2013 during the Taper Tantrum, when it raised some $26 billion from the diaspora to steady a sinking rupee. The current package goes further: alongside lifting the caps, the central bank introduced a concessional foreign-currency swap window that effectively shifts the cost of hedging dollar deposits from the banks to the RBI itself, letting lenders offer far richer returns without eating the currency risk. The government, for its part, has removed capital-gains tax on certain government bonds to court overseas capital.

The market expects the haul to be large. Brokerage Nomura estimates the scheme could draw in around $55 billion, with the bulk arriving in August and September; other industry estimates run as high as $60 to $70 billion. "Compared to 2013, while U.S. dollar rates are much higher, the scheme will also provide leverage to investors, which will boost returns," Nomura said in a note. Indian banks are even pressing to route some of this lending through their GIFT City units, the country's offshore finance hub, to widen the funnel.

## The Catch Beneath the Headline Rate

Not everyone is convinced the dollars will flood in. A sobering analysis in The Hindu BusinessLine argued the euphoria may be "misplaced," noting that the Trump-era squeeze on the US diaspora \u2014 higher tariffs feeding inflation at Indian grocery stores, the $100,000 H-1B fee, AI-driven job anxiety and strained credit \u2014 has left many NRIs wanting cash close to hand rather than locked into three-to-five-year deposits abroad. The numbers bear out the caution: outstanding FCNR(B) deposits grew just 2.9 percent in 2025-26, against 27.5 percent the year before and 32.9 percent the year before that. Whether the lure of a 7 percent rate can overpower that defensiveness is the open question.

## Why It Matters for the Diaspora

For NRIs, this is one of the rare moments when New Delhi's macro anxiety becomes a personal opportunity. A dollar deposit in an Indian bank at 7 percent \u2014 with no rupee-conversion risk on FCNR(B) accounts \u2014 is a genuinely attractive, low-risk return at a time when keeping money in a US savings account earns far less. NRE deposits, which are rupee-denominated and fully repatriable with tax-free interest in India, become similarly compelling for those comfortable with currency exposure.

But the window is narrow and the fine print matters. The relaxation expires September 30, so the best rates are a limited-time offer. Transfers from NRO accounts into NRE accounts do not qualify for the exemption. And anyone holding an older deposit should ask their bank directly whether \u2014 and when \u2014 they can break and rebook, because the rules on that are still being settled. For a diaspora that sent home a record $135 billion last year, the RBI has essentially put out a sign: bring it here, and we will pay you well for it \u2014 at least until the leaves turn."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "The Reserve Bank of India headquarters in Mumbai; the central bank scrapped rate caps on NRI deposits on June 17"
    img_attribution = "Wikimedia Commons"

    for q in ["Reserve Bank of India building Mumbai", "Reserve Bank of India headquarters", "Reserve Bank of India"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            break

    if not img_url:
        px = fetch_pexels_image("bank building finance")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A bank building"

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
            "Reserve Bank of India \u2014 Notifications on FCNR(B) and NRE deposit interest-rate ceilings (June 17, 2026)",
            "The Hindu BusinessLine \u2014 Attracting NRI inflows: RBI temporarily withdraws interest rate ceiling on fresh FCNR(B) deposits of 3-5 yr tenor",
            "Outlook Business \u2014 RBI Wants More Dollars; Here's Why It Has Relaxed NRI Deposit Rules",
            "Outlook Business \u2014 Why NRIs Are Rushing to Break Old Deposits and Reinvest at Higher Rates",
            "Reuters \u2014 Indian banks push for lending via GIFT City units in dollar deposit scheme; Nomura estimates $55 billion in inflows"
        ]),
        "diaspora_angle": "The RBI has temporarily lifted rate caps on FCNR(B) and long-term NRE deposits, pushing returns from ~3% to as high as 7.1% \u2014 a rare, time-limited chance for NRIs to earn high, low-risk returns on dollars or rupees parked in Indian banks, but only until September 30 and with tricky rules on breaking older deposits.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: AAPI physicians / $100K H-1B physician fee blocked ─

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: AAPI cheers court blocking $100K H-1B physician fee")
    print("="*60)

    slug = "aapi-physicians-court-blocks-100k-h1b-fee-imgs-underserved-care-20260619"
    headline = "A Court Just Lifted a $100,000 Wall in Front of Immigrant Doctors. Indian-American Physicians Are Calling It a Win for Patients."
    subheadline = "The American Association of Physicians of Indian Origin has welcomed a federal ruling striking down the Trump administration's $100,000 H-1B fee, warning the charge would have gutted rural and safety-net hospitals where international medical graduates \u2014 a large share of them Indian-trained \u2014 keep the lights on."

    body = """When a federal judge struck down the Trump administration's $100,000 H-1B fee this week, the loudest cheers did not come from Silicon Valley. They came from the medical community \u2014 and, specifically, from the doctors of Indian origin who fill some of the hardest-to-staff jobs in American healthcare.

The American Association of Physicians of Indian Origin (AAPI), one of the largest ethnic medical organisations in the United States, formally welcomed the decision, framing it not as a political outcome but as a clinical one. "This ruling restores fairness and stability to a system that thousands of international physicians depend upon," said AAPI President Dr. Amit Chakrabarty. "This is not a political victory \u2014 it is a healthcare victory. It ensures that patients are not placed at risk due to policy barriers unrelated to clinical need."

## What the Court Decided

The ruling, handed down by a federal judge earlier this week, held that the Trump administration lacked the authority to impose a $100,000 charge on H-1B visa applications. The judge found that only Congress has the power to create a tax of that magnitude, and that lawmakers never granted the executive branch that authority. The fee had been introduced by presidential proclamation in September 2025, applying to new petitions filed after September 21, and represented an extraordinary jump from the roughly $780 application fee plus a $215 lottery cost that preceded it.

The lawsuit was brought by a coalition of Democratic attorneys general, who argued the charge amounted to an unauthorised tax on employers trying to fill specialised roles. President Trump has criticised the decision, and the administration is widely expected to appeal \u2014 meaning the relief, while real, may not be the final word.

## Why Doctors Felt It Most

For the technology sector, the fee was a costly nuisance. For medicine, AAPI leaders argued, it threatened to be catastrophic in exactly the places that can least afford it. The group stressed that the charge would have fallen hardest on rural hospitals, safety-net institutions and underserved communities, where international medical graduates (IMGs) are not a convenience but a lifeline.

"Many hospitals would have struggled to absorb such a financial burden," Dr. Chakrabarty explained. "The consequences would have been immediate \u2014 fewer physicians, longer wait times, and reduced access to care for communities that already face healthcare disparities." Independent physician practices, many operating on razor-thin margins, simply could not stack a six-figure fee on top of existing onboarding costs.

The scale of the dependence is striking. According to U.S. Citizenship and Immigration Services data, more than 8,200 H-1B approvals in 2023 were for general medicine and surgical hospitals. The Migration Policy Institute reports that roughly 21 percent of immigrant physicians practising in the United States were trained in India \u2014 and India accounted for more than 70 percent of all H-1B visas issued last year. In primary care, where shortages are already acute and recruitment in rural areas is hardest, IMGs often represent the difference between an open clinic and a shuttered one.

## A Broader Diaspora Push

The AAPI statement is part of a wider mobilisation across the Indian-American community against the H-1B restrictions. Diaspora organisations such as GOPIO have taken the issue to lawmakers, and figures including Connecticut Congressman Jim Himes have voiced support for protecting the visa channel that brought many of America's best-known executives \u2014 from Sundar Pichai to Satya Nadella \u2014 into the country. Forty-seven medical groups, including the American Academy of Pediatrics, have signed onto a letter backing bipartisan legislation that would explicitly exempt physicians and other healthcare professionals from the $100,000 fee, arguing that "each month of delay translates directly into longer patient wait times, deferred care, and risks straining already overburdened emergency departments."

## Why It Matters for the Diaspora

For Indian-American families, this fight sits at the intersection of identity and livelihood. The community's success in American medicine is one of its proudest stories \u2014 Indian-origin doctors run hospital departments, teach in medical schools and, disproportionately, serve the rural and inner-city patients other physicians avoid. A policy that priced new immigrant doctors out of the system would not only have shut the door on the next generation of IMGs; it would have weakened the very institutions the community has spent decades building inside.

But the celebration comes with an asterisk. The fee has been blocked, not buried, and an appeal could revive it. Meanwhile, separate legislative efforts in Congress aim to shrink H-1B duration, end its use as a green-card pathway and scrap the OPT programme that funnels foreign graduates into the workforce \u2014 threats that no single court ruling resolves. For now, immigrant physicians can breathe; for the diaspora that depends on them, the larger battle over who gets to practise medicine in America is far from settled."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "A United States federal courthouse; a federal judge struck down the $100,000 H-1B fee this week"
    img_attribution = "Wikimedia Commons"

    for q in ["United States federal courthouse building", "United States courthouse exterior", "hospital corridor doctors"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "hospital" in t or "corridor" in t:
                img_caption = "A hospital interior; international medical graduates fill critical roles in US rural and safety-net hospitals"
            break

    if not img_url:
        px = fetch_pexels_image("hospital corridor doctor")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A hospital corridor"

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
            "The Indian EYE \u2014 AAPI Applauds Court Ruling Blocking $100,000 H-1B Physician Visa Requirement (Dr. Amit Chakrabarty statement)",
            "NBC Palm Springs / Associated Press \u2014 Federal Judge Blocks $100,000 Fee on H-1B Visa Applications",
            "Medical Economics \u2014 Trump's $100,000 H-1B fee rattles businesses and alarms physician advocates (USCIS and Migration Policy Institute data)",
            "American Academy of Pediatrics \u2014 AAP urges federal officials to remove immigration barriers for international medical graduates",
            "The Indian EYE \u2014 Connecticut Congressman Jim Himes supports GOPIO's stand on H-1B visa issue"
        ]),
        "diaspora_angle": "A federal court struck down the $100,000 H-1B fee that Indian-American physician group AAPI says would have crippled rural and safety-net hospitals \u2014 where Indian-trained doctors (21% of US immigrant physicians) are essential \u2014 but with an appeal likely and other anti-H-1B bills moving, the relief for the diaspora's medical community may be temporary.",
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
