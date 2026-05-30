#!/usr/bin/env python3
"""
Lifestyle-Health & Markets-Finance writer for The Videshi
Run: 2026-05-30
Articles:
  1. Hepatitis B functional cure (bepirovirsen) — lifestyle-health
  2. Rupee's best day in two months / Week ahead — markets-finance
"""

import json, os, subprocess, sys, time, uuid, re, urllib.parse, datetime

# ── Load env ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS_SB = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def sb_post(table, data):
    """Insert into Supabase and return the created row."""
    import requests
    url = f"{SB_URL}/rest/v1/{table}"
    r = requests.post(url, json=data, headers=HEADERS_SB, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ✗ POST {table} failed: {r.status_code} {r.text[:300]}")
        return None
    rows = r.json()
    return rows[0] if isinstance(rows, list) and rows else rows


def sb_patch(table, match, data):
    """Update rows matching filter."""
    import requests
    params = "&".join(f"{k}={v}" for k, v in match.items())
    url = f"{SB_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, json=data, headers=HEADERS_SB, timeout=30)
    if r.status_code not in (200, 204):
        print(f"  ✗ PATCH {table} failed: {r.status_code} {r.text[:300]}")
        return None
    return r.json() if r.text else True


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import requests
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
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
    """Fetch an image from Pexels using curl (not Python urllib — gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket article-images."""
    import requests
    try:
        # Download
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=20)
        if r.status_code != 200:
            print(f"  ✗ Download failed: {r.status_code}")
            return None
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type:
            print(f"  ✗ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ✗ Image too small: {len(r.content)} bytes")
            return None

        # Upload to Supabase storage
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        r2 = requests.post(upload_url, data=r.content, headers=upload_headers, timeout=30)
        if r2.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed: {r2.status_code} {r2.text[:200]}")
            return None
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
        return None


def validate_image_url(url):
    """Verify URL returns HTTP 200 with image content > 5KB."""
    import requests
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # HEAD might not return Content-Length, try GET
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) >= 5000:
                return True
        print(f"  ⚠ Image validation failed: status={r.status_code} ct={ct} cl={cl}")
        return False
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False


# ── Articles ──────────────────────────────────────────────────────────────────

articles = []

# ═══════════════════════════════════════════════════════════════════════════════
# ARTICLE 1: Hepatitis B Functional Cure — lifestyle-health
# ═══════════════════════════════════════════════════════════════════════════════

art1 = {
    "headline": "A Drug Just Cured One in Five Chronic Hepatitis B Patients. India Has 40 Million Carriers. This Is the Biggest Breakthrough in Decades.",
    "subheadline": "GSK's bepirovirsen achieved a functional cure in 19 per cent of patients after just six months of weekly injections — in a disease where the current cure rate is less than 1 per cent. For South Asians, who carry a disproportionate burden of the virus, the implications are enormous.",
    "slug": "hepatitis-b-functional-cure-bepirovirsen-gsk-india-south-asian-diaspora-20260530",
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "published",
    "published_at": datetime.datetime.utcnow().isoformat() + "Z",
    "sources": json.dumps([
        {"name": "New England Journal of Medicine", "url": "https://www.nejm.org"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/gsks-chronic-hepatitis-b-drug-helps-one-five-achieve-functional-cure-key-studies-2026-05-29/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com"},
        {"name": "AJMC", "url": "https://www.ajmc.com"},
        {"name": "PMC / NIH", "url": "https://pmc.ncbi.nlm.nih.gov"}
    ]),
    "body": """For a disease that has quietly killed more people than HIV, the word "cure" has never really applied to hepatitis B. Until now.

Results from two global phase 3 trials, published simultaneously in the *New England Journal of Medicine* and presented at the European Association for the Study of the Liver Congress this week, show that GSK's experimental drug bepirovirsen achieved a **functional cure in 19 per cent of chronic hepatitis B patients** — meaning the virus became undetectable and stayed undetectable for at least six months after all treatment stopped.

In a disease where current standard-of-care therapies achieve functional cure rates of **less than 1 per cent per year**, and where patients typically take antiviral pills for the rest of their lives, this is not incremental. It is structural.

## What the Trials Found

The B-Well 1 and B-Well 2 trials enrolled **1,838 patients across 29 countries** in Asia, Europe, and the Americas. Participants received weekly injections of bepirovirsen for six months alongside their regular antiviral pills. If the virus was undetectable for six months after stopping injections, they could stop their daily pills too.

Among patients who started with lower levels of the hepatitis B surface antigen — the key viral protein that indicates active infection — the functional cure rate rose to **26 per cent**. No patients in the placebo group achieved a functional cure.

"To have six months of injections to achieve functional cure of this magnitude is a great advance in the management of my patients," said Dr. Seng Gee Lim, the lead investigator and director of hepatology at the National University Health System in Singapore.

Bepirovirsen works differently from existing treatments. While current antivirals suppress the virus without eliminating it, bepirovirsen is an antisense oligonucleotide — it binds directly to the virus's genetic material, blocks replication, suppresses the surface antigen protein, and helps the immune system mount an effective attack. GSK has tracked patients from earlier studies and found most remain virus-free up to three years later.

Side effects were mild: injection-site redness, occasional pain, and a temporary rise in liver enzymes. The trials did not include patients with cirrhosis or very high viral loads, a limitation that researchers acknowledge.

## Why This Matters Disproportionately for South Asians

Chronic hepatitis B is not evenly distributed around the world. And the numbers for South Asians are stark.

**India alone has an estimated 40 million chronic hepatitis B carriers**, with a national prevalence of 3 to 4 per cent — classifying it as an intermediate endemic zone. In certain tribal and rural communities, prevalence exceeds 10 per cent. Hepatitis B is responsible for roughly 70 per cent of chronic hepatitis cases and 80 per cent of cirrhosis cases in India, and about 60 per cent of hepatocellular carcinoma patients are HBV-positive.

For South Asians in the diaspora, the risk does not end at immigration. Studies in the UK found that hepatitis B incidence among South Asians was **3.1 times higher** than among non-South Asians. In the United States, first-generation Indian immigrants have HBsAg prevalence rates of 1 to 6 per cent — comparable to rates in India itself. South Asian children in the UK showed acute HBV infection rates **10 times higher** than non-South Asian children.

The problem is compounded by screening gaps. Hepatitis B testing is not required as part of the US immigration process, meaning many chronic carriers arrive in the country undiagnosed. The CDC has estimated that 2.2 million US residents have chronic hepatitis B, with 1.3 million being foreign-born — and those figures likely undercount undocumented immigrants and other underserved populations.

## What NRI Families Should Know

If you were born in India before hepatitis B vaccination became part of the national immunisation schedule — which was only added in 2002 and rolled out gradually — your vaccination status is worth checking.

Chronic hepatitis B is often silent for decades. Many carriers have no symptoms until the virus has caused serious liver damage. A simple blood test for HBsAg can confirm whether you carry the virus.

If you are a carrier currently on lifelong antiviral therapy, bepirovirsen represents the first realistic prospect of a finite treatment that could let you stop taking pills altogether. GSK has sought regulatory approval in the US, Japan, China, and Europe. **The US FDA decision is expected by October 2026.**

For parents: ensure your children's hepatitis B vaccination is up to date. The three-dose vaccine series is one of the most effective vaccines ever developed, with a protection rate above 95 per cent. If your child was born abroad and you are unsure of their vaccination status, a blood test can confirm immunity.

## The Bigger Picture

Hepatitis B kills approximately 1.1 million people every year, more than HIV and malaria combined. It is the world's leading cause of liver cancer. And yet it receives a fraction of the funding, public attention, and political urgency.

Bepirovirsen is not a universal cure — it worked for roughly one in five patients. But it is the first therapy in the history of the disease to complete global phase 3 trials with functional cure as the primary endpoint. GSK expects peak annual sales of more than £2 billion, and Jefferies analysts have called the commercial potential "blockbuster."

For the estimated 40 million carriers in India alone, and the millions more in the diaspora who carry the virus without knowing it, this is the closest thing to hope that hepatitis B has ever produced. The question now is whether screening, access, and awareness can keep pace with the science.""",
}
articles.append(art1)


# ═══════════════════════════════════════════════════════════════════════════════
# ARTICLE 2: Rupee's Best Day / Week Ahead — markets-finance
# ═══════════════════════════════════════════════════════════════════════════════

art2 = {
    "headline": "The Rupee Just Had Its Best Day in Two Months. Oil Dropped, the RBI Stepped In, and a US-Iran Truce Extension Is on the Table. Here Is What the Week Ahead Looks Like.",
    "subheadline": "The Indian currency surged 0.7 per cent to 95 per dollar on Friday after central bank intervention and a drop in crude prices. With the RBI meeting on June 5 and US jobs data on June 6, the next seven days will set the tone for Indian markets through the monsoon.",
    "slug": "rupee-best-day-two-months-rbi-intervention-oil-drop-week-ahead-nri-20260530",
    "category": "markets-finance",
    "vertical": "markets-finance",
    "status": "published",
    "published_at": datetime.datetime.utcnow().isoformat() + "Z",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/currencies/rupee-soars-best-day-nearly-two-months-central-bank-steps-oil-drops-2026-05-30/"},
        {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/rbi-hold-rates-june-majority-now-expect-hike-by-year-end-2026-05-30/"},
        {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/indian-equity-benchmarks-log-monthly-losses-iran-war-jitters-2026-05-30/"},
        {"name": "Capital Economics", "url": "https://www.capitaleconomics.com"}
    ]),
    "body": """After two months of grinding losses, the Indian rupee staged its sharpest single-day rally since April on Friday. The question for NRI investors is whether this is a turning point or a reprieve.

The rupee ended the session at **95 per US dollar**, up 0.7 per cent from the previous close — its best day since April 2. At one point, it briefly crossed the 95 mark. On a weekly basis, it gained about 0.7 per cent, though it was essentially flat for May as a whole.

Three forces converged to produce the move.

## What Happened

**The RBI stepped in aggressively.** State-run banks were spotted selling dollars before the local spot market opened — a classic marker of central bank intervention. Before the selling began, the rupee was quoting around 95.77-95.78. Within minutes, it had jumped sharply. Five traders confirmed to Reuters that the Reserve Bank of India was likely behind the move.

**Oil prices dropped.** Brent crude futures fell to around $91 per barrel, on track for their steepest weekly decline since early April. The trigger: reports of a plan to extend the US-Iran ceasefire for another 60 days and reopen traffic through the Strait of Hormuz — the narrow passage through which roughly one-fifth of the world's oil supply flows. India, the world's third-largest oil importer, is acutely sensitive to crude prices. The Iran conflict had pushed Brent above $100 in March, inflating India's import bill and widening the current account deficit.

**MSCI rebalancing passed.** The MSCI May index rejig, which went into effect at Friday's close, had been a source of anxiety. India's weight in the MSCI Emerging Markets Index is expected to fall from about 20 per cent to 11.2 per cent — a dramatic reduction that triggered passive fund selling. With that event now behind the market, one overhang has lifted.

## The Damage Report: May in Numbers

Despite Friday's rally, May was not kind to Indian markets. The Nifty 50 fell **1.9 per cent** for the month to close at 23,547.75. The Sensex shed **2.8 per cent** to 74,775.74. It was the worst May for Indian benchmarks in three years.

Foreign investors pulled over **$24 billion** from Indian debt and equities on a net basis between March and May. Ten of 16 major sectors logged monthly losses. The rupee itself is down more than 5 per cent year-to-date — the worst-performing Asian currency.

Not everything was bleak. Small-cap and mid-cap indices rose 0.7 per cent and 3.2 per cent respectively in May, buoyed by domestic earnings optimism. Adani Enterprises surged 22 per cent for the month after the US dropped fraud charges against Gautam Adani.

## The Week Ahead: Two Events That Matter

**June 5: RBI monetary policy decision.** This is the marquee event. A Reuters poll of economists found that most expect the RBI to hold its key repo rate unchanged at 5.25 per cent. But a growing minority — and a growing chorus of analysts — argue that a rate hike is becoming inevitable.

Bank Indonesia delivered a surprise 50-basis-point hike last week. The Philippines raised rates in April. India's Asian peers are already tightening to defend their currencies. Capital Economics expects the RBI to raise the repo rate to 6.00 per cent before year-end, though the timing depends on whether oil prices stay below $95.

A hawkish statement — even without a hike — could steady the rupee and signal to foreign investors that the RBI takes inflation seriously. A dovish hold could invite renewed selling pressure.

**June 6: US non-farm payrolls.** Markets expect 96,000 jobs added in May and a 4.3 per cent unemployment rate. Any hint of overheating — stronger job growth, rising wages — could push US bond yields higher and strengthen the dollar, which would put fresh pressure on the rupee and emerging market assets broadly.

The new Federal Reserve Chair Kevin Warsh has his first meeting later in June. Markets now see a greater chance of a US rate hike than a cut in 2026, despite President Trump's calls for easing.

## What NRI Investors Should Watch

**Remittances.** The rupee at 95 is still historically weak. If you are remitting dollars to India, the exchange rate remains favourable compared to any point before March 2026. But if the RBI hikes and oil stays below $95, the rupee could strengthen meaningfully in the second half of the year.

**NRI fixed deposits.** If the RBI signals a rate hike in June or August, Indian banks will likely raise deposit rates. Locking into an NRI FD at current rates may be less attractive than waiting for a post-hike repricing — unless you want the certainty of today's rate on a long-duration deposit.

**Indian equities.** Broad market direction will depend on three variables: oil prices, the Iran situation, and whether the RBI acts on rates. Until US-Iran uncertainty resolves, analysts expect rangebound trading. The small-cap and mid-cap rally suggests domestic investors are finding selective value, but foreign flows remain firmly negative.

**The insurance angle.** Indian life insurers have asked the government to double the tax-free investment limit for insurance policies from ₹500,000. If granted, it would boost inflows into long-duration debt instruments — a potential positive for bond investors and for insurers listed on Indian exchanges.

The bottom line: Friday was a good day for the rupee, but one day does not make a trend. The next seven days — RBI on Thursday, US jobs on Friday — will tell us whether it can be sustained.""",
}
articles.append(art2)


# ═══════════════════════════════════════════════════════════════════════════════
# Image sourcing & publishing
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("PUBLISHING ARTICLES")
print("="*60)

for i, art in enumerate(articles):
    print(f"\n--- Article {i+1}: {art['headline'][:80]}... ---")

    # Insert article
    row = sb_post("p2_articles", art)
    if not row:
        print(f"  ✗ Failed to insert article {i+1}")
        continue

    art_id = row.get("id")
    print(f"  ✓ Inserted: id={art_id}")

    # Image sourcing
    img_url = None

    if i == 0:  # Hepatitis B article — use Pexels for liver/medical
        img_url = fetch_pexels_image("hepatitis medical laboratory blood test", "medical research laboratory")

    elif i == 1:  # Rupee/markets article — use Pexels for Indian currency/markets
        img_url = fetch_pexels_image("Indian rupee currency notes", "stock market trading financial")

    if img_url:
        # Upload to Supabase storage for permanence
        filename = f"{art_id}.jpg"
        final_url = upload_to_supabase_storage(img_url, filename)
        if final_url:
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {
                "image_url": final_url,
                "image_attribution": "The Videshi"
            })
            print(f"  ✓ Image set: {final_url[:80]}...")
        else:
            # Try using Pexels URL directly (permanent)
            if "images.pexels.com" in img_url:
                sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {
                    "image_url": img_url,
                    "image_attribution": "The Videshi"
                })
                print(f"  ✓ Image set (Pexels direct): {img_url[:80]}...")
    else:
        print(f"  ⚠ No image found — article published without image")

    print(f"  ✓ Article {i+1} published successfully")

print("\n" + "="*60)
print("ALL DONE")
print("="*60)
