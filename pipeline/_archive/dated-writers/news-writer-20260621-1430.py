#!/usr/bin/env python3
"""
Videshi News Writer — June 21, 2026 (14:30 UTC run)
2 NEW articles:
  1. India's cash-transfer-to-women boom; 16th Finance Commission fiscal warning (news / economy)
  2. India's census resumes after 15 years — first digital, first with caste enumeration (news / governance)
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


# ─── Article 1: Cash transfers to women / Finance Commission warning ─

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Cash transfers to women — fiscal warning")
    print("="*60)

    slug = "india-states-cash-transfer-schemes-women-fiscal-warning-finance-commission-ladki-bahin-20260621"
    headline = "India's States Are Sending Cash Straight to Women. The Bill Is Now Big Enough to Worry the Economists."
    subheadline = "Sixteen states now deposit money directly into women's bank accounts every month \u2014 a political juggernaut that has reshaped Indian elections. With the combined cost approaching \u20b92 lakh crore, the body that decides how India's money is split is sounding a careful alarm."

    body = """In the space of three years, one idea has rewired Indian state politics: pay women directly, every month, no strings attached. What began as a scattered experiment in two states in 2022-23 has become a near-universal feature of governance, with sixteen states now running unconditional cash-transfer schemes that put money straight into the bank accounts of crores of women. The schemes have decided elections, lifted incumbents who looked finished, and changed what Indian voters expect from their governments. They have also grown large enough that the country's fiscal referees are beginning to flag the cost out loud.

For the diaspora, this is not a distant policy curiosity. The women receiving these transfers are the mothers, sisters and grandmothers whom NRIs support from abroad. The schemes interact directly with the remittance economy \u2014 easing, in some households, the pressure on money sent home, while in others reshaping how families budget. And the fiscal questions they raise bear on the broader health of the Indian states where so many diaspora families still own property, run businesses and plan to retire.

## How Big the Wave Has Become

The numbers tell the story of an idea that went from fringe to mainstream at remarkable speed. According to an analysis drawing on legislative research, the combined annual outlay of these schemes is projected to approach \u20b91.96 lakh crore \u2014 more than half a per cent of India's GDP and, by some estimates, close to a fifth of all subsidies handed out by states. That is a structural commitment, not a one-off giveaway, and it is locked into state budgets that were already stretched.

The flagship is Maharashtra's Mukhyamantri Majhi Ladki Bahin Yojana, which transfers \u20b91,500 a month to roughly 2.3 crore women and is widely credited with rescuing the ruling coalition in the 2024 assembly election. Karnataka's Gruha Lakshmi sends \u20b92,000 a month to women heads of household. West Bengal's Lakshmir Bhandar, an early mover, helped cement Mamata Banerjee's dominance. Madhya Pradesh's Ladli Behna scheme is credited with the BJP's surprise 2023 win there. Delhi's Mahila Samriddhi Yojana promises \u20b92,500 a month. Tamil Nadu, Jharkhand, Telangana, Himachal Pradesh and others have joined, each tailoring the amount but keeping the core promise the same: cash, monthly, directly to women.

## Why the Finance Commission Is Watching

The caution is now coming from the top of India's fiscal architecture. The 16th Finance Commission, chaired by economist Arvind Panagariya and tasked with recommending how tax revenue is divided between the centre and the states for the 2026-31 period, has flagged the rising burden of these welfare commitments. The concern is not the principle of helping women \u2014 it is the math. When a recurring expense of this size is baked into budgets, it crowds out spending on the things that build long-term growth: roads, schools, hospitals, power.

The warning signs are already visible. Maharashtra, the scheme's poster child, has had to trim benefits and tighten eligibility under fiscal strain, removing lakhs of women found ineligible. Ratings agency Crisil has noted that aggregate state borrowing rose sharply year-on-year, with welfare transfers among the drivers. The Reserve Bank of India has repeatedly cautioned states that competitive freebies, however popular, narrow the room for productive capital spending. Several states now spend more on these transfers than on their entire health or higher-education budgets.

## The Politics That Make Them Untouchable

What makes the schemes so hard to rein in is precisely what makes them effective: they work, electorally. Direct transfers to women have proved one of the most reliable vote-winners in modern Indian politics, cutting across caste and region in a way few other promises do. The money reaches a constituency that turns out to vote, lands visibly in bank accounts, and is felt immediately in household budgets. No party that has launched such a scheme has been able to withdraw it, and rivals racing to match or outbid one another has become a feature of nearly every recent state campaign.

That dynamic is the heart of the fiscal worry. Economists broadly accept that putting cash in women's hands can improve nutrition, schooling and household bargaining power \u2014 the gains are real. The question the Finance Commission and the RBI keep returning to is one of balance and design: whether transfers this large, growing this fast, and politically impossible to reverse, leave states enough fiscal space to invest in the future even as they ease the present.

## What It Means for Families Abroad

For NRI families, the schemes are a quiet new variable in the household economy back home. A monthly state transfer to a mother or widowed relative can reduce the regularity or size of remittances some families send, or simply add a cushion that did not exist before. At the macro level, the fiscal health of states such as Maharashtra, Karnataka and West Bengal \u2014 where diaspora investment and property ownership are concentrated \u2014 depends on getting this balance right. The cash-transfer revolution has already changed how Indian governments win power. The coming years will test whether they can afford to keep the promise."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "A woman uses a bank passbook in India; sixteen states now run monthly cash-transfer schemes that deposit money directly into women's accounts"
    img_attribution = "Wikimedia Commons"

    # Prefer Panagariya's own photo (the named protagonist of the warning)
    person_img = fetch_wikipedia_person_image("Arvind Panagariya")
    if person_img:
        img_url = person_img
        img_caption = "Economist Arvind Panagariya, chairman of the 16th Finance Commission, which has flagged the rising fiscal burden of states' cash-transfer schemes for women"
        img_attribution = "Wikimedia Commons"

    if not img_url:
        for q in ["Indian women rural", "woman bank India", "Indian rupee currency notes", "women self help group India"]:
            commons = fetch_wikimedia_commons_images(q)
            if commons:
                img_url = commons[0]["url"]
                img_caption = "Women in India; sixteen states now run monthly cash-transfer schemes depositing money directly into women's bank accounts, at a combined cost approaching \u20b92 lakh crore"
                break

    if not img_url:
        px = fetch_pexels_image("indian woman rural village")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Women in India; states' direct cash-transfer schemes for women have reshaped politics and are now drawing fiscal caution from the 16th Finance Commission"

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
            "The Hindu BusinessLine / PRS Legislative Research \u2014 analysis of state cash-transfer schemes for women: 16 states now run such schemes (up from 2 in 2022-23); combined outlay projected near \u20b91.96 lakh crore (~0.5%+ of GDP; ~20% of state subsidies)",
            "16th Finance Commission (chaired by Arvind Panagariya) \u2014 mandate to recommend centre-state tax devolution for 2026-31; flagged rising burden of state welfare/cash-transfer commitments on fiscal space",
            "Government of Maharashtra \u2014 Mukhyamantri Majhi Ladki Bahin Yojana: \u20b91,500/month to ~2.3 crore women; benefits trimmed and ineligible beneficiaries removed under fiscal strain",
            "Crisil report (May 2026) \u2014 aggregate state market borrowing rose ~15% year-on-year, with welfare transfers among the drivers; RBI cautions on competitive freebies narrowing capital-expenditure space",
            "Scheme records \u2014 Karnataka Gruha Lakshmi (\u20b92,000/mo), West Bengal Lakshmir Bhandar, Madhya Pradesh Ladli Behna, Delhi Mahila Samriddhi Yojana (\u20b92,500/mo); credited with election outcomes in Maharashtra, MP and West Bengal"
        ]),
        "diaspora_angle": "The women receiving these monthly state transfers are the mothers, sisters and grandmothers NRIs support from abroad; the schemes ease remittance pressure in some households while reshaping budgets in others, and the fiscal health of states like Maharashtra, Karnataka and West Bengal \u2014 where diaspora property and investment are concentrated \u2014 hinges on getting the balance right.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India's census resumes — first digital, first caste count ─

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India's census resumes after 15 years")
    print("="*60)

    slug = "india-census-2027-resumes-first-digital-caste-enumeration-houselisting-begins-diaspora-20260621"
    headline = "After 15 Years, India Is Counting Itself Again \u2014 On a Phone, and Asking About Caste for the First Time Since 1931"
    subheadline = "Houselisting for India's long-delayed census has quietly begun across the states, the first stage of a count that will be conducted on mobile apps, allow households to enumerate themselves, and record caste for the first time in independent India's history."

    body = """India has begun the largest act of self-measurement on earth. After a delay of more than five years \u2014 the original 2021 census was postponed by the pandemic and then held back year after year \u2014 the machinery of the decennial count has finally started to move. The first phase, houselisting and the housing census, is now underway, rolling across states through the second half of 2026, ahead of the main population enumeration scheduled for February 1, 2027. It will be unlike any census India has ever conducted: the first done digitally, the first to let citizens count themselves, and the first since 1931 to ask every Indian their caste.

For the global Indian diaspora, a census is more than a headcount. It is the dataset that underpins constituency boundaries, the allocation of central funds, reservation policy, and the planning of everything from schools to highways. It shapes the India that NRIs invest in, send money to, and often intend to return to. And for the millions of overseas Indians with property, ancestral homes and dependent relatives back home, the questions of who gets counted, where, and how, carry real weight.

## A Count That Kept Slipping

The scale of the delay is hard to overstate. India has counted its people every ten years without fail since 1881 \u2014 through famine, partition and war. The 2021 census broke that streak. First the COVID-19 pandemic made field operations impossible; then, year after year, the exercise was deferred amid administrative and political wrangling. By the time it resumes, India will have gone fifteen years without fresh, comprehensive population data, forcing policymakers to lean on increasingly stale 2011 figures and projections to run welfare schemes, draw budgets and target subsidies.

That data gap has had real consequences. Beneficiary lists for major welfare programmes have run on 2011 population numbers, meaning crores of people may have been excluded simply because the denominator was out of date. The freeze on delimitation \u2014 the redrawing of parliamentary and assembly seats \u2014 is tied to census data, making this count a prerequisite for one of the most consequential political exercises of the coming decade.

## How the New Census Works

The Ministry of Home Affairs has confirmed that field operations are now beginning in earnest. A press release in mid-June noted that houselisting work had commenced in Himachal Pradesh, with self-enumeration options being rolled out in states including Kerala and Nagaland. The reference date for most of the country is set, with hill and snow-bound regions following a separate calendar.

The mechanics mark a generational leap. Some 34 lakh enumerators and roughly 1.3 lakh supervisory functionaries will fan out across the country, but this time armed with mobile applications rather than paper schedules. Households will, for the first time, be able to count themselves through a self-enumeration portal, entering their own details before the population enumeration. The questionnaire has been restructured \u2014 a 31-question housing schedule in the first phase, followed by a detailed population schedule \u2014 and the entire operation is designed to feed data digitally into a central system, sharply cutting the years it once took to publish results.

## The Caste Question

The single most consequential change is the decision to enumerate caste. India has not collected comprehensive caste data in its census since 1931, under British rule. Every count since independence has recorded only Scheduled Castes and Scheduled Tribes, leaving the country to govern reservation policy, affirmative action and social welfare using nearly century-old caste figures and contested estimates. The decision to count caste again \u2014 long demanded by opposition parties and several state governments, and eventually embraced by the central government \u2014 will produce the first authoritative picture in over ninety years of how India's population breaks down across caste lines.

The political stakes are enormous. Caste numbers feed directly into debates over the size of reservation quotas, the sub-categorisation of backward classes, and the distribution of political power. Whatever the count reveals will reverberate through Indian politics for a decade, and the design of the caste question \u2014 how categories are defined and recorded \u2014 is already being scrutinised closely by every side.

## Why the Diaspora Should Care

For overseas Indians, the census touches several nerves at once. OCI and PIO households with property in India, NRIs whose extended families will be enumerated, and diaspora investors who track India's demographic trajectory all have a stake in accurate data. The count will reset the population baseline that drives everything from infrastructure planning in the cities where the diaspora invests, to the welfare entitlements of relatives left behind. It will inform the delimitation that reshapes India's political map, with consequences for how the country is governed for years to come.

After a decade and a half of governing in the dark, India is about to switch the lights back on. The picture that emerges in 2027 \u2014 of how many Indians there are, where they live, and who they are \u2014 will set the terms of the national conversation, at home and across the diaspora, well into the 2030s."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "A crowded street in India; the country's first census in 15 years has begun, conducted digitally and recording caste for the first time since 1931"
    img_attribution = "Wikimedia Commons"

    for q in ["India crowd street people", "Indian census", "crowded market India", "India population city street"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "A crowded street in India; houselisting for the country's first census in 15 years has begun, with population enumeration set for February 1, 2027"
            break

    if not img_url:
        px = fetch_pexels_image("india crowd street people")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A crowded street in India; the long-delayed census has resumed, conducted digitally and recording caste for the first time since 1931"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "governance",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Press Information Bureau / Ministry of Home Affairs (June 16, 2026) \u2014 census houselisting field operations commenced (Himachal Pradesh noted); self-enumeration rolled out in states including Kerala and Nagaland; reference dates set",
            "The Hindu BusinessLine / LiveMint \u2014 India's census resumes after delay from 2021; houselisting phase through 2026; population enumeration scheduled February 1, 2027; ~34 lakh enumerators and ~1.3 lakh functionaries",
            "Census of India / official notifications \u2014 first fully digital census via mobile apps; self-enumeration portal; restructured questionnaire (housing schedule then population schedule)",
            "Government announcements \u2014 caste to be enumerated for the first time since 1931; previous post-independence censuses recorded only Scheduled Castes and Scheduled Tribes; data tied to delimitation freeze and welfare beneficiary lists still based on 2011 figures"
        ]),
        "diaspora_angle": "A census underpins constituency boundaries, central fund allocation, reservation policy and infrastructure planning \u2014 the India that NRIs invest in, send money to and often plan to return to; OCI/PIO households with property, NRIs whose families will be enumerated, and diaspora investors tracking India's demographics all have a direct stake in an accurate count after 15 years of stale data.",
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
