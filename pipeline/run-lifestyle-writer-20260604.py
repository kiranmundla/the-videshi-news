#!/usr/bin/env python3
"""Lifestyle & Markets writer — 2026-06-04 evening run."""

import json, os, sys, time, uuid, re, subprocess
from datetime import datetime, timezone

import requests, urllib.parse

# ── ENV ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):
                    line = line[7:]
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── IMAGE HELPERS ────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons, return list of image URLs."""
    results = []
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": "6",
                "gsrlimit": str(limit),
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": "1200",
                "format": "json",
            },
            headers={"User-Agent": UA}, timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            for pid, page in pages.items():
                for ii in page.get("imageinfo", []):
                    mime = ii.get("mime", "")
                    if mime.startswith("image/") and ii.get("width", 0) > 300:
                        url = ii.get("thumburl") or ii.get("url")
                        if url:
                            results.append(url)
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return results


def fetch_pexels(query, per_page=5):
    if not PEXELS_KEY:
        return []
    try:
        out = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page={per_page}"],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(out.stdout)
        return [p["src"]["large2x"] for p in data.get("photos", [])]
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return []


def validate_image(url):
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD
        if r.status_code == 200 and "image" in ct:
            return True
    except:
        pass
    return False


def best_image(wiki_person=None, commons_queries=None, pexels_query=None):
    """Multi-source compare, return (url, attribution) or (None, None)."""
    candidates = []

    if wiki_person:
        url = fetch_wikipedia_person_image(wiki_person)
        if url and validate_image(url):
            candidates.append((url, "Wikimedia Commons", 10))  # highest priority

    for q in (commons_queries or []):
        for url in fetch_wikimedia_commons(q, limit=3):
            if validate_image(url):
                candidates.append((url, "Wikimedia Commons", 7))
                break  # one per query is enough

    if pexels_query:
        for url in fetch_pexels(pexels_query, per_page=3):
            if validate_image(url):
                candidates.append((url, "Pexels", 4))
                break

    if not candidates:
        return None, None

    # Sort by priority desc
    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates[0][0], candidates[0][1]


# ── SUPABASE INSERT ─────────────────────────────────────────────────
def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {data[0].get('slug', '?')}")
            return True
        print(f"  ✓ Inserted (no body)")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


# ── ARTICLE DATA ─────────────────────────────────────────────────────
now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VERTICAL_MAP = {
    "lifestyle-health": "culture",
    "markets-finance": "economy",
}

ARTICLES = []

# ─── ARTICLE 1: Keto diet & anorexia nervosa ────────────────────────
ARTICLES.append({
    "headline": "A Keto Diet Just Put 72 Per Cent of Anorexia Patients Into Recovery. The Science Is Counterintuitive and Compelling.",
    "subheadline": "A UC San Diego pilot trial published in Nature's Communications Medicine found that 14 weeks of supervised ketogenic therapy reversed eating-disorder symptoms in nearly three out of four participants — without triggering weight loss.",
    "slug": "keto-diet-anorexia-nervosa-recovery-uc-san-diego-communications-medicine-20260604",
    "category": "lifestyle-health",
    "vertical": "culture",
    "status": "published",
    "is_editorial": False,
    "published_at": now_iso,
    "sources": json.dumps([
        {"name": "Communications Medicine (Nature)", "url": "https://www.nature.com/articles/s43856-026-00701-2"},
        {"name": "New Scientist", "url": "https://www.newscientist.com/article/2480550-keto-diet-shows-real-promise-for-anorexia-recovery/"},
        {"name": "News Medical", "url": "https://www.news-medical.net/news/20260603/Ketogenic-diet-shows-promise-in-treating-anorexia-nervosa.aspx"},
    ]),
    "image_search": {
        "wiki_person": "Guido Frank psychiatrist",
        "commons_queries": ["ketogenic diet food", "anorexia nervosa treatment"],
        "pexels_query": "ketogenic diet healthy fats avocado nuts",
    },
    "image_caption": "A spread of ketogenic-friendly foods including avocado, nuts and olive oil",
    "body": """Anorexia nervosa kills one person in the United States every 52 minutes. It carries the highest mortality rate of any psychiatric disorder, and for the patients who do survive and regain weight, the psychological torment — the relentless fear of food, the body dissatisfaction, the compulsive restriction — often persists for years. Standard therapies, primarily talk-based, have barely moved the needle on relapse rates.

A pilot trial from the University of California, San Diego, published this week in *Communications Medicine*, suggests that an unlikely intervention may offer a new path: the ketogenic diet.

## The Counterintuitive Premise

Prescribing a diet defined by extreme macronutrient restriction to patients who already restrict food sounds dangerous. Guido Frank, a professor of psychiatry at UC San Diego who has spent 25 years treating anorexia, argues the opposite. Growing evidence links anorexia to neurometabolic dysfunction — a malfunction in how brain cells release and use energy. The ketogenic state, which shifts the body from burning glucose to burning fat-derived ketones, may correct that underlying circuitry.

"People tell me clinically, it is like an addiction," Frank told New Scientist. "Perhaps if you create that state that they crave while giving them enough food, it can be beneficial."

## What the Trial Found

The study enrolled 22 women aged 18 to 45 with a history of anorexia whose body mass index had recovered to at least 17.5. For 14 weeks, participants followed a supervised ketogenic plan — 70 per cent fat, 20 per cent protein, 10 per cent carbohydrates — monitored by a dietician, a psychiatrist and a peer counsellor who had personally experienced anorexia.

Eighteen of the 22 completed the programme, an 82 per cent adherence rate that is notably high for an eating-disorder trial. The results were striking:

- **72 per cent** of completers scored in the recovered or normal range on the Eating Disorder Examination Questionnaire (EDE-Q), meaning they no longer met diagnostic criteria for anorexia.
- **All 18 completers** showed improvement in depression scores, with 72 per cent falling within the normal range on the Beck Depression Inventory.
- Body weight did not change significantly — no participant's BMI dropped below 17.5. The intervention was explicitly designed to maintain weight, not reduce it.
- Participants who continued ketogenic therapy three months after the study ended showed slightly better outcomes than those who stopped.

No serious adverse events were reported.

## Why This Matters for the Diaspora

Eating disorders are not a Western phenomenon, though they are often framed that way. Research published in the *International Journal of Eating Disorders* has documented rising rates of anorexia and bulimia among South Asian women, both in India and across the diaspora. Cultural pressures around body image, the stigma attached to mental illness in many South Asian households, and the scarcity of specialised treatment options create a particularly difficult landscape.

For NRI families, the challenge is compounded. Young South Asian women in the US, UK and Canada navigate dual beauty standards — one from their parents' culture, another from their peers — and often suffer in silence. A metabolic intervention that targets the brain's energy pathways rather than relying solely on psychotherapy could lower barriers to treatment, particularly for patients who have failed conventional approaches.

## The Caveats

The study was small, single-arm, and had no placebo control. Frank's team is already planning a larger randomised trial with brain imaging to map how ketosis changes neural glucose uptake in anorexia patients. Until that data arrives, the findings are best described as promising but preliminary.

The ketogenic diet also requires careful supervision. Unsupervised, it could be weaponised by patients as another form of restriction. The UC San Diego team embedded psychiatric and dietary monitoring at every stage — a model that would need to be replicated in any clinical rollout.

## What Comes Next

Frank's lab is now running a follow-up study using PET scans to measure how the ketogenic state affects regional brain glucose metabolism in recovered anorexia patients compared to healthy controls. The goal is to move from clinical observation to mechanistic proof — to show not just that the diet works, but precisely how it rewires the circuits that drive the disorder.

For a condition that has resisted pharmacological innovation for decades, a dietary intervention grounded in neuroscience is a genuinely novel direction. Whether it scales beyond a pilot remains to be seen. But for the families who have watched someone they love cycle through relapse after relapse, even preliminary evidence of a new approach is hard to ignore.""",
})

# ─── ARTICLE 2: Revita procedure post-GLP-1 ─────────────────────────
ARTICLES.append({
    "headline": "A Single Gut Procedure Just Preserved 78 Per Cent of GLP-1 Weight Loss at One Year. South Asians Should Watch This Closely.",
    "subheadline": "Fractyl Health's REVEAL-1 data show that its endoscopic Revita procedure helps patients maintain weight after stopping Wegovy or Mounjaro — without lifelong medication. For a community with the world's highest metabolic disease burden, the implications are significant.",
    "slug": "fractyl-revita-procedure-glp1-weight-maintenance-one-year-south-asian-metabolic-20260604",
    "category": "lifestyle-health",
    "vertical": "culture",
    "status": "published",
    "is_editorial": False,
    "published_at": now_iso,
    "sources": json.dumps([
        {"name": "GlobeNewsWire / Fractyl Health", "url": "https://www.globenewswire.com/news-release/2026/06/04/3009012/0/en/Fractyl-Health-Reports-Positive-One-Year-REVEAL-1.html"},
        {"name": "Medscape", "url": "https://www.medscape.com/viewarticle/solutions-emerging-post-glp-1-weight-regain-2026a1000a7f"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/fractyl-health-says-experimental-procedure-helps-maintain-weight-loss-study-2025-10-01/"},
    ]),
    "image_search": {
        "wiki_person": None,
        "commons_queries": ["endoscopy procedure", "duodenum anatomy medical"],
        "pexels_query": "medical endoscopy procedure hospital",
    },
    "image_caption": "An endoscopic procedure being performed in a clinical setting",
    "body": """The central problem with GLP-1 weight-loss drugs is not getting the weight off. It is keeping it off.

Patients on semaglutide (Wegovy) or tirzepatide (Mounjaro, Zepbound) routinely lose 15 to 25 per cent of their body weight. But when they stop — because of cost, side effects, insurance changes, or personal choice — the weight comes roaring back. Published studies show an average regain of roughly 15 per cent of total body weight within a year of discontinuation. For many patients, that erases most of the progress.

New one-year data released today by Fractyl Health suggest there may be a way to break that cycle — with a single, minimally invasive gut procedure.

## The REVEAL-1 Results

The REVEAL-1 Cohort, an open-label study, enrolled patients with obesity who had lost at least 15 per cent of their total body weight on GLP-1 medications and then stopped treatment. Each patient underwent a single Revita procedure — a roughly 60-minute endoscopic treatment that remodels the lining of the duodenum, the first section of the small intestine.

At one year post-procedure and post-GLP-1 discontinuation, the results were striking:

- Participants retained approximately **78 per cent** of their GLP-1-induced weight loss.
- The mean total body weight change was just **5.3 per cent** — compared to the roughly 15 per cent regain observed in published GLP-1 withdrawal studies.
- **33 per cent** of patients continued to *lose* weight after stopping their GLP-1 and receiving the procedure.
- All patients maintained at least 5 per cent of their prior GLP-1-induced weight loss through the full year.
- HbA1c levels remained essentially stable, with a mean increase of just 0.08 per cent.
- No procedure-related serious adverse events were reported.

"This is the first data suggesting that drug-free, durable weight maintenance is possible after GLP-1 therapy," said Harith Rajagopalan, Fractyl's CEO. "It challenges the core assumption that obesity care must orbit around lifelong medical therapy."

## How Revita Works

Chronic diets high in processed sugar and fat damage the mucosal lining of the duodenum over time. That damage disrupts the gut's ability to sense nutrients and send the right hormonal signals to the brain — signals that regulate appetite, insulin release and fat storage. Revita uses controlled thermal energy delivered endoscopically to ablate the damaged lining, prompting the body to regenerate a healthier mucosal surface.

The procedure takes about an hour, requires no incisions, and patients typically go home the same day. It has received FDA Breakthrough Device designation for post-GLP-1 weight maintenance.

## Why This Matters for South Asians

South Asians carry a disproportionate burden of metabolic disease. Indians develop type 2 diabetes at lower BMIs and younger ages than virtually any other ethnic group. The diaspora in the US, UK and Canada inherits this risk — compounded by dietary shifts toward processed food and sedentary suburban lifestyles.

GLP-1 drugs have been transformative for many in this community. But the economics are brutal. Wegovy costs roughly $1,300 per month without insurance. Mounjaro is comparable. Indian health insurance plans, whether employer-sponsored in the US or private plans in India, often exclude weight-loss medications or impose severe restrictions. Cigna recently dropped GLP-1 weight-loss coverage for its own employees. UnitedHealthcare and others have tightened criteria.

A one-time procedure that could replace years or decades of monthly injections would fundamentally change the cost calculus. If Revita wins FDA approval — the company received favourable feedback on its De Novo classification request in March and expects to submit in late 2026 — it could offer a financially viable path for patients who cannot sustain lifelong GLP-1 therapy.

## The Caveats

The REVEAL-1 Cohort was small (15 evaluable patients) and open-label, meaning there was no sham-procedure control group. The more rigorous data will come from REMAIN-1: randomised, blinded results from the Midpoint Cohort are expected in Q3 2026, with pivotal six-month data in early Q4.

Earlier randomised data from REMAIN-1 were encouraging — at three months, Revita patients lost an additional 2.5 per cent of body weight while sham patients regained 10 per cent — but one-year randomised data will be the true test.

## What Comes Next

Fractyl is a tiny company. Its stock (ticker: GUTS) trades under a dollar. But the science behind duodenal mucosal resurfacing is grounded in two decades of metabolic surgery research, and the unmet need it addresses — durable weight maintenance without chronic medication — is arguably the biggest open problem in obesity medicine.

For NRI families navigating the intersection of genetic metabolic risk, high drug costs and limited insurance coverage, the Revita data are worth following. A single procedure that preserves most of the weight loss achieved on GLP-1 therapy is not a cure. But it may be the bridge between starting treatment and sustaining the results for life.""",
})

# ─── ARTICLE 3: Alphabet $85B offering ───────────────────────────────
ARTICLES.append({
    "headline": "Alphabet Just Raised $85 Billion by Selling Its Own Stock. If You Own GOOGL, Here Is What That Means.",
    "subheadline": "Google's parent company upsized its equity offering to $84.75 billion — the largest stock sale in corporate history — to fund AI data centres. The move cancels buybacks, dilutes shareholders, and signals that the AI spending race has outgrown even Big Tech's enormous cash flows.",
    "slug": "alphabet-google-85-billion-stock-offering-ai-infrastructure-nri-investors-20260604",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "published",
    "is_editorial": False,
    "published_at": now_iso,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/alphabet-raise-8475-billion-upsized-equity-offering-fund-ai-ambitions-2026-06-03/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/alphabet-google-stock-offering-ai-spending-f51c5b7e"},
        {"name": "Investopedia", "url": "https://www.investopedia.com/ai-spending-rational-phase-markets-12286553"},
    ]),
    "image_search": {
        "wiki_person": "Sundar Pichai",
        "commons_queries": ["Google data center", "Alphabet Inc headquarters"],
        "pexels_query": "data center server room technology",
    },
    "image_caption": "Sundar Pichai, CEO of Alphabet, has called demand for AI computing power 'unprecedented'",
    "body": """Alphabet does not need to sell stock. It is one of the most profitable companies in history, generating roughly $214 billion in operating cash flow this year. It sits on a fortress balance sheet. It has not needed to tap equity markets for capital in its two decades as a public company.

Until now.

On Monday, Google's parent announced plans to raise $80 billion through a combination of public stock offerings, a private placement with Berkshire Hathaway and an at-the-market programme. By Wednesday, it had upsized the deal to $84.75 billion — the largest equity offering in corporate history — after the first tranche was "well over-subscribed," according to CEO Sundar Pichai.

The stock dropped nearly 4 per cent on the announcement. It has since recovered some ground, trading around $372 on Thursday, but remains roughly 10 per cent below its all-time high of $408.61 from mid-May.

For NRI investors — many of whom hold GOOGL directly, through index funds, or through employer stock at Google — the offering raises important questions about dilution, capital allocation and the sustainability of the AI spending race.

## The Structure

The $84.75 billion raise breaks down into four components:

- **$18 billion** from a public offering of Class A and C shares
- **$16.75 billion** from depositary shares (a stock-linked security)
- **$10 billion** from a private placement with Warren Buffett's Berkshire Hathaway
- **$40 billion** from an at-the-market offering programme planned for Q3 2026

About $30 billion of the total is earmarked for taxes. The remainder funds AI infrastructure — data centres, chips, power systems and the vast physical plant required to run AI models at global scale.

## Why Alphabet Needs Outside Money

The AI capital expenditure cycle has grown faster than even Big Tech's extraordinary profits can support.

Alphabet expects to spend between $180 billion and $190 billion on capital expenditure in 2026 alone, up from its prior forecast of $175 billion. It has warned that spending will "significantly increase" in 2027. Together with Microsoft, Amazon, Meta and Oracle, the five hyperscalers are now on track to spend more than $700 billion on AI infrastructure this year — up from an earlier consensus of roughly $600 billion.

That spending exceeds their combined operating cash flows for the first time. Since May 2025, Alphabet has borrowed over $85 billion across six currencies. Its total debt now exceeds $100 billion, up from $28 billion at the end of March 2025. It also carries $18 billion in lease liabilities.

The equity offering signals that even debt markets are insufficient. "Equity funding suggests the AI capex cycle is entering an increasingly mature and capital-intensive phase, where even cash-rich hyperscalers are increasingly tapping external capital," analysts at BCA Research wrote this week.

## The Dilution Problem

For shareholders, the most immediate concern is dilution. Alphabet did not buy back a single share last quarter — the first time since 2017. The offering effectively cancels the company's buyback programme for the foreseeable future.

Barron's estimates that the $84.75 billion in new equity, at current prices, represents roughly 2 per cent dilution — manageable in isolation, but symbolically significant for a company whose buybacks have been a key driver of per-share earnings growth.

The deeper worry is precedent. If Alphabet needs $85 billion in equity now, and capex is only going up, will there be another offering in 2027? The at-the-market programme already builds in a mechanism for ongoing share sales through the third quarter.

## What It Means for NRI Portfolios

GOOGL is a staple of Indian diaspora investment portfolios. Many tech professionals in the US hold it through RSUs or ESPPs. It sits in every major index fund — the S&P 500, the Nasdaq-100, most target-date retirement funds.

The key question is whether the AI spending will generate returns that justify the dilution. Pichai has pointed to "unprecedented customer demand" for Google's AI products. Cloud revenue, powered by AI workloads, grew 28 per cent last quarter. Google's Gemini models are being embedded across Search, YouTube, Workspace and Android.

But the market is not fully convinced. The stock's 10 per cent pullback from its peak reflects a repricing of the risk that AI capex may be a treadmill — each generation of models requiring more compute, more power, more capital — rather than a one-time investment that generates durable competitive advantage.

For NRI investors holding concentrated GOOGL positions, especially through employer stock, the offering is a reminder to review allocation. A company raising this much equity is signalling that it expects to consume capital at a pace that exceeds its own prodigious cash generation for years to come. That is not inherently bearish — Amazon burned capital for a decade before its margins expanded — but it does change the return profile.

## The Bigger Picture

Alphabet's offering is not an isolated event. SpaceX is preparing a $75 billion IPO that would value it at $1.75 trillion. OpenAI and Anthropic are each expected to list at around $1 trillion. The capital markets are being asked to absorb an extraordinary volume of new equity in a short window.

The risk for markets is not that any single offering fails. It is that the collective demand for capital from the AI sector crowds out other investments, pushes up interest rates and creates a feedback loop where the cost of building AI infrastructure rises faster than the revenue it generates.

For now, demand for Alphabet's shares was strong enough to upsize the deal. Berkshire Hathaway's $10 billion private placement is a significant vote of confidence. But the fact that Alphabet — a company that mints cash — felt it had no choice but to sell equity tells you everything about where the AI arms race stands. The spending has outgrown the profits. And the race is still accelerating.""",
})

# ── MAIN ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    success = 0
    for i, art in enumerate(ARTICLES):
        print(f"\n{'='*60}")
        print(f"Article {i+1}: {art['headline'][:70]}...")

        # Image sourcing
        img_cfg = art.pop("image_search")
        img_url, img_attr = best_image(
            wiki_person=img_cfg.get("wiki_person"),
            commons_queries=img_cfg.get("commons_queries"),
            pexels_query=img_cfg.get("pexels_query"),
        )

        if img_url:
            art["image_url"] = img_url
            art["image_attribution"] = img_attr
            print(f"  Image: {img_attr} — {img_url[:80]}...")
        else:
            print("  ⚠ No image found — inserting without image")
            art["image_url"] = None
            art["image_attribution"] = None

        # Validate body length
        words = len(art["body"].split())
        print(f"  Body: {words} words")
        if words < 400:
            print(f"  ✗ SKIPPING — body too short ({words} < 400)")
            continue

        # Insert
        ok = insert_article(art)
        if ok:
            success += 1
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Done. {success}/{len(ARTICLES)} articles published.")
