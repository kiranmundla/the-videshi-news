#!/usr/bin/env python3
"""
The Videshi — Lifestyle-Health & Markets-Finance Writer
Run: 2026-06-16 11:00 PDT (18:00 UTC)
Articles:
  1. Vitamin C blood levels tied to brain structure / dementia (lifestyle-health)
  2. Prediabetes lifestyle program beats metformin at preventing chronic disease (lifestyle-health)
  3. India bonds near Bloomberg Global Aggregate Index inclusion (markets-finance)
All inserted with status="review", is_editorial=False.
"""

import json, os, re
import requests
from datetime import datetime, timezone


def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.replace('export ', '').strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val


load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'


def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(' ', '_')
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ok Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  warn Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons(query, limit=6):
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "generator": "search", "gsrsearch": query,
                "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
                "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
            },
            headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                info = page.get("imageinfo", [{}])[0]
                url = info.get("thumburl") or info.get("url")
                mime = info.get("mime", "")
                width = info.get("width", 0)
                title = page.get("title", "").lower()
                # junk filter
                if any(j in title for j in ["satellite", "aerial", "topograph", "nasa", "map of",
                                            "coin", "banknote", "stamp", ".svg", "logo", "flag of",
                                            "diagram", "chart", "graph"]):
                    continue
                if url and "image" in mime and "svg" not in mime and width > 400:
                    results.append({"url": url, "title": page.get("title", ""), "width": width})
            if results:
                print(f"  ok Commons {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  warn Commons error for '{query}': {e}")
    return []


def fetch_pexels(query, per_page=6):
    if not PEXELS_KEY:
        print("  warn no Pexels key")
        return []
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY}, timeout=12)
        if r.status_code == 200:
            data = r.json()
            photos = data.get("photos", [])
            results = [{"url": p["src"]["large2x"], "alt": p.get("alt", "")}
                       for p in photos if p.get("src", {}).get("large2x")]
            if results:
                print(f"  ok Pexels {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  warn Pexels error for '{query}': {e}")
    return []


def validate_image(url):
    """GET-based validation (HEAD to wikimedia always 400s in this env)."""
    try:
        r = requests.get(url, timeout=15, stream=True, headers={"User-Agent": UA})
        ct = r.headers.get("Content-Type", "")
        if "image" not in ct:
            print(f"  x not an image: {ct} {url[:70]}")
            r.close()
            return False
        chunk = r.raw.read(20000)
        r.close()
        if len(chunk) > 5000:
            print(f"  ok image valid ({len(chunk)}+ bytes, {ct})")
            return True
        print(f"  x image too small ({len(chunk)} bytes)")
    except Exception as e:
        print(f"  x validation error: {e}")
    return False


def pick_image(commons_queries, pexels_queries, captions, wiki_person=None):
    """Try Wikipedia person -> Commons -> Pexels. Returns (url, caption, attribution)."""
    if wiki_person:
        img = fetch_wikipedia_person_image(wiki_person)
        if img and validate_image(img):
            return img, captions.get("wiki", captions["commons"]), "Wikimedia Commons"
    for q in commons_queries:
        for img in fetch_wikimedia_commons(q):
            if validate_image(img["url"]):
                return img["url"], captions["commons"], "Wikimedia Commons"
    for q in pexels_queries:
        for img in fetch_pexels(q):
            if validate_image(img["url"]):
                return img["url"], captions["pexels"], "Pexels"
    return None, None, None


def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles",
                      headers=HEADERS, json=article, timeout=20)
    if r.status_code in (200, 201):
        result = r.json()
        aid = result[0].get('id', 'unknown') if isinstance(result, list) else result.get('id', 'unknown')
        print(f"  ok INSERTED {aid} -- {article['headline'][:60]}...")
        return True
    print(f"  x insert failed ({r.status_code}): {r.text[:300]}")
    return False


# ─── ARTICLE 1: Vitamin C & brain structure ─────────────────────────────────

def write_article_1():
    print("\n=== ARTICLE 1: Vitamin C & Brain Aging ===")
    slug = "vitamin-c-blood-levels-brain-structure-gray-matter-hirosaki-plos-one-south-asian-diaspora-20260616"
    headline = "Higher Vitamin C in Your Blood May Mean a Better-Preserved Brain. A 2,044-Person Study Found the Link."
    subheadline = "New research from Japan, published in PLOS ONE, is the first to tie actual blood vitamin C levels — not just diet surveys — to the structure of the ageing brain. For a diaspora facing a rising dementia burden, the signal is worth heeding."

    img_url, caption, attrib = pick_image(
        commons_queries=["human brain MRI scan", "fresh oranges citrus fruit", "amla Indian gooseberry"],
        pexels_queries=["oranges citrus vitamin c", "fresh fruit vegetables healthy", "brain mri scan"],
        captions={
            "commons": "Citrus fruit, a rich dietary source of vitamin C linked to brain health",
            "pexels": "Vitamin C-rich fruit, the focus of new research on brain ageing",
        })
    if not img_url:
        print("  ! no image, skipping")
        return False

    body = """For years, the advice to "eat your fruits and vegetables" has rested on broad nutritional reasoning rather than direct evidence about the brain. A new study from Japan changes that. Published in the journal *PLOS ONE*, it is the first to demonstrate a direct association between the actual concentration of vitamin C in a person's blood and the physical structure of their ageing brain.

The research, led by Dr. Tomohiro Shintaku, an assistant professor in the Department of Radiology at Hirosaki University, examined 2,044 older adults living in Hirosaki City. The participants had an average age of 69, and 61 per cent were women. Crucially, the researchers did not rely on food questionnaires, which are notoriously unreliable. Instead, they measured vitamin C levels directly in the blood — a far more accurate window into what the body is actually absorbing.

## What the Scans Showed

Each participant underwent MRI scans that allowed researchers to calculate the volume of grey matter and white matter in the brain, along with the strength of structural connections between regions. Even after accounting for confounding factors like age, smoking, diabetes, and other lifestyle behaviours, a clear pattern emerged.

Older adults with lower vitamin C levels tended to have lower brain tissue volumes and weaker structural network patterns. Those with higher levels showed better-preserved grey matter and stronger connectivity within the default mode network — a critical brain system involved in memory and cognitive function that is among the first to deteriorate in conditions like Alzheimer's disease and depression.

"Our study demonstrates that older adults with higher blood levels of vitamin C tend to have better-preserved brain structure and stronger connections within the default mode network," Dr. Shintaku said. "While diets rich in vitamin C are known to lower the risk of cognitive decline, our study is the very first to demonstrate a direct association between actual blood plasma vitamin C levels and the structural connectivity of the brain."

## Why This Matters for the Diaspora

The findings carry particular weight for the South Asian diaspora, a community confronting a quietly growing dementia burden as its first-generation immigrants enter their seventies and eighties. Research has repeatedly shown that South Asians face elevated risks of vascular dementia, driven in part by the same metabolic conditions — diabetes, hypertension, and heart disease — that already disproportionately affect the community.

There is a cultural irony here worth naming. The traditional South Asian diet is, in principle, rich in vitamin C. Amla, the Indian gooseberry, is one of the most concentrated natural sources of the vitamin on earth. Guava, citrus, green chillies, and a wide range of vegetables central to Indian cooking all deliver substantial amounts. Yet as diaspora families shift toward Western convenience foods, processed meals, and diets heavier in refined carbohydrates, that natural advantage can erode.

The study does not prove that taking vitamin C supplements will protect the brain — this was an observational study, and the relationship may run in more than one direction. But it does suggest that maintaining adequate vitamin C status, ideally through a diet rich in fresh produce, is a sensible and low-cost investment in long-term brain health.

## A Caution Against the Supplement Shortcut

It would be a mistake to read this research as an endorsement of megadose supplements. Vitamin C is water-soluble, and the body excretes what it cannot use. The participants with healthier brains were not necessarily those swallowing the most pills; they were the ones whose blood reflected consistent, adequate intake over time.

For diaspora families, the practical takeaway is to return to the plate rather than the pharmacy. A bowl of fresh fruit, a squeeze of lemon, the inclusion of amla or guava when available, and a steady supply of vegetables do more reliable work than any capsule. For the parents and grandparents of the community — the generation now most at risk — these are small, familiar changes that the evidence increasingly suggests are worth making.

## What Comes Next

The researchers note that their findings open a path toward larger, longitudinal studies that could establish whether raising vitamin C levels actively slows brain ageing, rather than merely correlating with it. For now, the study adds a precise, biologically grounded data point to a body of nutritional advice that has long been heavy on intuition and light on hard measurement. The brain, it turns out, may keep a record of what we eat — and vitamin C appears to be one of the entries that counts."""

    article = {
        "headline": headline, "subheadline": subheadline, "slug": slug, "body": body,
        "category": "lifestyle-health", "status": "review",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url, "image_caption": caption, "image_attribution": attrib,
        "vertical": "health", "is_editorial": False,
        "diaspora_angle": "South Asian elders face a rising dementia burden, and the traditional diet's natural vitamin C advantage — from amla, guava, and citrus — can erode as families shift to Western processed foods.",
        "sources": json.dumps([
            {"name": "PLOS ONE (Hirosaki University study)", "url": "https://journals.plos.org/plosone/"},
            {"name": "New York Post — health coverage", "url": "https://nypost.com"}
        ])
    }
    return insert_article(article)


# ─── ARTICLE 2: Prediabetes lifestyle beats metformin ───────────────────────

def write_article_2():
    print("\n=== ARTICLE 2: Prediabetes Lifestyle vs Metformin ===")
    slug = "prediabetes-lifestyle-intervention-beats-metformin-multimorbidity-nih-niddk-dpp-south-asian-20260616"
    headline = "Diet and Exercise Beat a Popular Diabetes Pill at Preventing Chronic Disease, a Landmark NIH Study Found."
    subheadline = "In a long-running US trial, a lifestyle program cut the risk of developing multiple chronic conditions by up to 25 per cent — while metformin showed no significant benefit. For South Asians, who slide into prediabetes early, the result reframes prevention."

    img_url, caption, attrib = pick_image(
        commons_queries=["vegetables healthy diet plate", "people walking exercise park", "fresh produce market vegetables"],
        pexels_queries=["healthy vegetables meal plate", "person walking exercise outdoors", "fresh vegetables market"],
        captions={
            "commons": "Fresh vegetables and produce central to lifestyle-based diabetes prevention",
            "pexels": "A diet rich in vegetables, a pillar of lifestyle intervention for prediabetes",
        })
    if not img_url:
        print("  ! no image, skipping")
        return False

    body = """For decades, the prevention of type 2 diabetes has rested on two pillars: lifestyle change and the drug metformin. Both have been shown to reduce the risk of progressing from prediabetes to full diabetes. But a new analysis from one of America's longest-running prevention trials has delivered a result that should reshape how doctors — and patients — think about the choice. When it comes to preventing the accumulation of multiple chronic diseases, lifestyle change worked. The pill did not.

The findings, released by the National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK), part of the National Institutes of Health, draw on the Diabetes Prevention Program and its long-term follow-up — a study that has tracked thousands of adults with prediabetes for more than two decades.

## What the Study Found

Researchers examined how many participants went on to develop "multimorbidity," defined as two or more chronic conditions, across 15 illnesses commonly tracked in Medicare data — including hypertension, heart disease, stroke, arthritis, chronic kidney disease, COPD, cancer, depression, dementia, and osteoporosis.

By the end of the follow-up, multimorbidity was widespread: it affected 82 per cent of the lifestyle group, 85 per cent of the metformin group, and 87 per cent of the placebo group. But the differences underneath those headline numbers were decisive. Compared with placebo, participants in the lifestyle intervention had a 21 per cent lower risk of developing two chronic conditions and a 25 per cent lower risk of developing three. Participants assigned to metformin showed no statistically significant reduction in multimorbidity at all.

Critically, these benefits held even when diabetes itself was removed from the definition — meaning the lifestyle program protected against a broad sweep of disease, not just the condition it was originally designed to prevent.

"These findings are highly encouraging, reinforcing that lifestyle programs focused on diet and exercise may persistently lower the risk of developing multiple chronic conditions, beyond diabetes," said Dr. Griffin P. Rodgers, Director of NIDDK. He added that because such changes are "safe and cost-effective," they may reduce both individual health burden and broader healthcare spending.

## The South Asian Stakes

Few communities have more riding on this result than the South Asian diaspora. South Asians develop prediabetes and type 2 diabetes at lower body weights and younger ages than most other populations — a phenomenon clinicians sometimes call the "thin-outside, fat-inside" profile, marked by visceral fat and insulin resistance that standard screening can miss. By the time many in the community reach their mid-forties, the metabolic clock is already ticking.

For decades, the default response has often been pharmaceutical. Metformin is cheap, familiar, and widely prescribed across India and the diaspora. This study does not suggest the drug is useless — it remains effective at delaying diabetes onset and has its own cardiovascular and longevity literature. But it does puncture the assumption that a pill is an adequate substitute for the harder work of changing how one eats and moves.

The lifestyle intervention in the trial was not exotic. It centred on modest weight loss, roughly 150 minutes of physical activity a week, and a shift toward a healthier diet — goals that map cleanly onto a community whose traditional cuisine, when built around vegetables, legumes, and whole grains rather than refined flour and fried snacks, is already well-positioned to deliver them.

## Why the Distinction Matters

The deeper significance of the study lies in what it measured. Most diabetes-prevention research asks a narrow question: did the person develop diabetes or not? This analysis asked a broader one: did the person stay healthier across their whole body, across many years? That framing matters enormously for a diaspora that does not simply face diabetes in isolation but a clustered burden of heart disease, kidney disease, and more, often arriving together and feeding one another.

A 21 to 25 per cent reduction in the risk of stacking up chronic illnesses, achieved without a prescription, is the kind of result that endocrinologists describe as "powerful." As Dr. Shirin Jaggi, an endocrinologist not involved in the study, put it, the findings let doctors tell patients "it's not just a pill that I need to give you."

## The Practical Path

The researchers and clinicians are careful to stress that lifestyle change is not one-size-fits-all and should be built gradually — ten or fifteen minutes of activity once or twice a day for someone sedentary, scaling up over time, with regular check-ins. For diaspora families, the message is both old and newly validated: the kitchen and the walking path are not soft alternatives to medicine. On the measure that arguably matters most — staying broadly healthy for the long haul — they outperformed the pill."""

    article = {
        "headline": headline, "subheadline": subheadline, "slug": slug, "body": body,
        "category": "lifestyle-health", "status": "review",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url, "image_caption": caption, "image_attribution": attrib,
        "vertical": "health", "is_editorial": False,
        "diaspora_angle": "South Asians slide into prediabetes earlier and at lower body weights than other groups, and often default to metformin — but this study shows lifestyle change does far more to prevent the clustered chronic diseases the community faces.",
        "sources": json.dumps([
            {"name": "NIH / NIDDK", "url": "https://www.niddk.nih.gov"},
            {"name": "New York Post — health coverage", "url": "https://nypost.com"}
        ])
    }
    return insert_article(article)


# ─── ARTICLE 3: India bonds near Bloomberg index inclusion ──────────────────

def write_article_3():
    print("\n=== ARTICLE 3: India Bonds & Bloomberg Index ===")
    slug = "india-government-bonds-bloomberg-global-aggregate-index-inclusion-review-fpi-inflows-nri-20260616"
    headline = "India's Bonds Are on the Cusp of Joining a Global Index That Moves Billions. The Review Lands This Month."
    subheadline = "After scrapping bond taxes and reopening the debt door, India is making its strongest bid yet for inclusion in the Bloomberg Global Aggregate Index — a move that could pull $20-25 billion into the country. For NRIs, it is a quiet but consequential signal."

    img_url, caption, attrib = pick_image(
        commons_queries=["Reserve Bank of India building Mumbai", "Bombay Stock Exchange building", "Mumbai financial district skyline"],
        pexels_queries=["Mumbai financial district buildings", "stock exchange trading screens", "indian currency rupee notes"],
        captions={
            "commons": "The Reserve Bank of India headquarters in Mumbai, at the centre of the bond-market reforms",
            "pexels": "Mumbai's financial district, home to India's bond and equity markets",
        })
    if not img_url:
        print("  ! no image, skipping")
        return False

    body = """While India's stock market has spent June bleeding foreign money, a quieter and potentially more durable story has been unfolding in the bond market. Foreign investors have poured more than $1.6 billion into Indian government bonds over just six trading sessions, the country's 10-year benchmark yield has fallen to a 12-week low, and global asset managers are watching for a decision that could reshape India's place in the world's fixed-income landscape: inclusion in the Bloomberg Global Aggregate Index.

Bloomberg Index Services is expected to seek investor feedback this month on whether Indian government bonds should be added to its flagship global bond benchmark. It would be the second major index milestone for India after the country's entry into JPMorgan's emerging-market debt index — and, by most accounts, a far bigger one.

## Why the Bloomberg Index Is Different

The JPMorgan index draws money from funds that specifically target emerging markets. The Bloomberg Global Aggregate is a different animal: it is one of the broadest and most widely tracked bond benchmarks on earth, followed by enormous pools of global capital that are not emerging-market specialists at all. Inclusion would force a vast universe of passive and benchmark-following funds to buy Indian government securities simply to match the index.

Analysts estimate the recent reforms and a potential inclusion could draw $20 to $25 billion in incremental debt inflows over the next 12 to 24 months. BNP Paribas Asset Management, which oversees more than €1.6 trillion, said the steps would "redirect flows to the onshore market" and provide "a constructive boost" to India's inclusion bid. M&G Investments called Bloomberg inclusion "a bigger driver of inflows" than the recent tax changes themselves.

## What India Did to Get Here

The breakthrough followed a deliberate policy push. In early June, the government scrapped taxes on certain foreign bond investments, and the Reserve Bank of India removed short-term investment limits and concentration limits for foreign portfolio investors in the corporate debt market — measures designed to align India's framework with global best practices and remove the friction that had kept big institutional money on the sidelines.

The timing was not accidental. With the rupee under severe pressure earlier this year — touching a record low near 97 per dollar — and foreign investors having pulled roughly $30 billion out of Indian equities during the US-Iran conflict, New Delhi needed a counterweight. The bond reforms, paired with a revived window to mobilise non-resident deposits, were engineered to bring dollars back in. India's finance minister reportedly met central bank officials to press the case for Bloomberg entry directly.

The early returns are visible. Foreign investors net bought bonds worth 155.5 billion rupees in the six sessions from June 5 — more than they had bought in the entire year up to that point. Kotak Mahindra Bank estimates the broader package of measures could draw about $75 billion in cumulative inflows and bring India's balance of payments close to neutral.

## Why NRIs Should Care

For non-resident Indians, the implications run along several channels at once.

The most immediate is the rupee. A wave of index-driven inflows provides structural support for the currency, which has already climbed to a five-week high near 94.5 per dollar as oil prices tumbled on the Iran peace deal. A stronger, more stable rupee changes the calculus for everything from remittances to property purchases back home — though NRIs sending money to India benefit more from a weaker rupee at the moment of transfer, the stability that index inclusion brings reduces the gut-wrenching volatility that has defined the currency this year.

The second channel is investment opportunity. Index inclusion typically compresses bond yields over time as demand rises, which can lift the price of bonds NRIs already hold and lower the government's borrowing costs across the economy. For NRIs invested in Indian debt funds, gilt funds, or the growing menu of GIFT City fixed-income products, a structural inflow story is a tailwind.

The third is confidence. Inclusion in a benchmark of this stature is, in effect, a global stamp of approval on the credibility of India's fiscal and monetary management. For diaspora investors weighing how much of their portfolio to anchor to India, that signal carries weight beyond the immediate flows.

## The Caveats

None of this is guaranteed. A review is not an inclusion, and index providers move on their own timelines. The durability of the recent rally depends heavily on whether the Iran peace deal holds and oil stays anchored near $80 a barrel. The RBI has also signalled it may not allow the rupee to appreciate too far, preferring to use any strength to rebuild its depleted forward book. And the broader backdrop — a US Federal Reserve decision, the Bank of Japan's trajectory, and the OECD's warning of the weakest global growth since 2008 — could swamp the India-specific story at any moment.

But the direction of travel is clear. After years of hesitation, India has opened its bond market to the world on terms the world has been asking for. The Bloomberg review this month will reveal how willing global capital is to walk through the door."""

    article = {
        "headline": headline, "subheadline": subheadline, "slug": slug, "body": body,
        "category": "markets-finance", "status": "review",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url, "image_caption": caption, "image_attribution": attrib,
        "vertical": "economy", "is_editorial": False,
        "diaspora_angle": "Index inclusion would steady the rupee, lift Indian bond holdings, and stamp global approval on India's fiscal management — all of which shape how NRIs remit, invest, and anchor portfolios to India.",
        "sources": json.dumps([
            {"name": "Reuters — India bond-tax moves and index inclusion", "url": "https://www.reuters.com"},
            {"name": "The Hindu BusinessLine — bond yield 12-week low", "url": "https://www.thehindubusinessline.com"},
            {"name": "AInvest — RBI FPI reforms and index inclusion", "url": "https://www.ainvest.com"}
        ])
    }
    return insert_article(article)


def main():
    print("The Videshi — Lifestyle/Markets Writer")
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    results = []
    results.append(("Vitamin C & Brain Aging", write_article_1()))
    results.append(("Prediabetes Lifestyle vs Metformin", write_article_2()))
    results.append(("India Bonds & Bloomberg Index", write_article_3()))
    print("\n" + "=" * 60)
    print("SUMMARY:")
    for name, ok in results:
        print(f"  {'ok PUBLISHED(review)' if ok else 'x FAILED'}: {name}")
    print(f"\n{sum(1 for _, s in results if s)}/{len(results)} articles inserted")


if __name__ == "__main__":
    main()
