#!/usr/bin/env python3
"""Lifestyle & Markets writer — 2026-06-02 run"""

import json, os, sys, uuid, re, time
from datetime import datetime, timezone

import requests
import urllib.parse

# ── Supabase config ──
SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
SB_HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
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
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            cmd = [
                "curl", "-sS",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                "-H", f"Authorization: {PEXELS_KEY}",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                alt = (p.get("alt") or "").lower()
                # skip bad images
                bad_patterns = ["aerial", "satellite", "map", "flag", "icon", "logo"]
                if any(bp in alt for bp in bad_patterns):
                    continue
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(img_url, filename):
    """Download an image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(img_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0"})
        if r.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
            return img_url  # fall back to original
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return img_url
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return img_url

        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if up.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up.status_code} {up.text[:200]}")
            return img_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return img_url


def validate_image_url(url):
    """Verify an image URL returns 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0"}, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # HEAD may not return Content-Length, try GET
        if r.status_code == 200 and "image" in ct:
            return True
    except:
        pass
    return False


def insert_article(article):
    """Insert an article into Supabase."""
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=SB_HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ═══════════════════════════════════════════════════════════════
# ARTICLE 1 — Lifestyle-Health
# FDA Approves First Needle-Free Insulin for Children
# ═══════════════════════════════════════════════════════════════

art1_slug = "fda-approves-inhaled-insulin-afrezza-children-diabetes-south-asian-families-20260602"
art1_headline = "The FDA Just Approved the First Needle-Free Insulin for Children. For South Asian Families Managing Diabetes, It Changes Everything."
art1_subheadline = "MannKind's Afrezza, an inhaled rapid-acting insulin, is now cleared for kids aged six and older. With 350,000 American children living with diabetes and South Asians facing some of the highest rates in the world, this is not a niche approval."

art1_body = """The U.S. Food and Drug Administration has approved MannKind Corporation's Afrezza — an inhaled rapid-acting insulin delivered through a small, portable device — for children and adolescents aged six and older with Type 1 or Type 2 diabetes. It is the first and only needle-free mealtime insulin ever approved for the paediatric population.

The approval, announced on May 30, marks a significant expansion from Afrezza's original 2014 clearance for adults. For the estimated 350,000 children and adolescents in the United States living with diabetes, the majority of whom have Type 1 and require multiple daily insulin injections, this represents the first real alternative to needles at mealtimes.

## How It Works

Afrezza uses MannKind's Technosphere platform to deliver insulin powder through a pocket-sized inhaler. The insulin is absorbed rapidly through the lungs into the bloodstream, closely mimicking the body's natural insulin response to food. Patients inhale a dose at the start of each meal. The drug does not replace basal (long-acting) insulin for Type 1 patients — it supplements it.

The key advantage over injected rapid-acting insulins is speed and convenience. For children whose eating patterns, activity levels, and school schedules vary daily, a quick inhalation before a meal is substantially less disruptive than preparing and administering an injection.

"Mealtime insulin can be especially challenging for children because eating and snacking patterns, activity levels, and daily settings like school and sports often vary," said Dr Desmond Schatz, professor of paediatrics at the University of Florida College of Medicine. "With its rapid onset and dosing at the start of a meal, Afrezza may help clinicians better match insulin therapy to how children and families live day to day."

## The Clinical Evidence

The approval was supported by data from the Phase 3 INHALE-1 trial, which enrolled 230 children aged 4 to 17 with Type 1 (98 per cent) or Type 2 (2 per cent) diabetes. Participants were randomised to inhaled insulin or injected pre-meal insulin, all while continuing basal insulin, for 26 weeks.

The results showed mean HbA1c was 8.22 per cent at baseline and 8.41 per cent at 26 weeks with inhaled insulin, compared with 8.21 per cent at both time points for injected insulin. The difference did not meet the pre-specified non-inferiority margin of 0.4 per cent.

However, inhaled insulin showed no major safety concerns, no changes in pulmonary function, greater treatment satisfaction among patients and families, and less weight gain than injected alternatives. For many paediatric endocrinologists, the trade-off between marginally higher HbA1c and substantially improved quality of life and adherence is worth considering on a case-by-case basis.

Jennifer Segrist, whose 15-year-old daughter Taisie participated in MannKind's study, told Reuters that switching to inhaled insulin had been "life changing." Taisie, a track and cross-country athlete in Oklahoma, had previously needed several injections a day. "Diabetes is not such a huge weight on her shoulders anymore," Segrist said.

## Why This Matters for South Asian Families

South Asians are disproportionately affected by diabetes. Studies consistently show that Indian-origin populations develop insulin resistance and Type 2 diabetes at younger ages, lower body weights, and higher rates than most other ethnic groups. The MASALA study at Northwestern University found that 30 per cent of South Asian adults in the U.S. have prediabetes by age 45.

While Type 1 diabetes in South Asian children occurs at rates comparable to the general population, the growing incidence of Type 2 diabetes in South Asian adolescents — driven by genetic predisposition, dietary patterns, and sedentary lifestyles — means more young people in diaspora families may need insulin earlier than expected.

For parents managing a child's diabetes across school days, sports practices, sleepovers, and family gatherings, an inhaler is meaningfully different from a syringe. The stigma and self-consciousness that adolescents feel around injections is well documented, and adherence drops sharply in teenage years. A device that looks like an asthma inhaler and takes seconds to use removes a significant psychological barrier.

## Access and Cost

MannKind says eligible patients can access Afrezza for $35 or less per month through its MannKind Cares programme. Afrezza should not be used in children with chronic lung conditions such as asthma or COPD, and the FDA notes a risk of bronchospasm.

The approval does not change the fundamental management of Type 1 diabetes — basal insulin remains essential — but it adds a tool that prioritises how children and families actually live over how clinical protocols assume they should.

*Sources: FDA, Reuters, MedPage Today, MannKind Corporation, INHALE-1 trial data (ASCO 2026)*"""

# ═══════════════════════════════════════════════════════════════
# ARTICLE 2 — Lifestyle-Health
# Medicare's $50 GLP-1 Weight-Loss Drug Program
# ═══════════════════════════════════════════════════════════════

art2_slug = "medicare-glp1-bridge-50-dollar-wegovy-zepbound-weight-loss-nri-elderly-parents-20260602"
art2_headline = "Medicare Will Cover Wegovy and Zepbound for $50 a Month Starting July 1. If Your Parents Are on Medicare, Read This."
art2_subheadline = "The new GLP-1 Bridge program opens weight-loss drug access to 14 million Medicare beneficiaries. For NRI families managing ageing parents' health from abroad, the financial and logistical implications are substantial."

art2_body = """Starting July 1, millions of Americans on Medicare will be able to access GLP-1 weight-loss medications — including Wegovy, Zepbound, and the oral drug Foundayo — for just $50 a month. The programme, known as the Medicare GLP-1 Bridge, is the federal government's first direct coverage of obesity medications under Medicare, bypassing longstanding legal restrictions that limited these drugs to patients with diabetes or cardiovascular disease.

The shift is enormous. Previously, Medicare beneficiaries who wanted GLP-1s for weight loss had to pay out of pocket — often $1,000 or more per month. Under the new pilot, the $50 co-payment stays flat regardless of dose, and coverage runs for 18 months through December 2027.

## Who Qualifies

More than 14 million people enrolled in Medicare who have been diagnosed as obese or overweight could qualify. The programme covers three medications: injectable and oral Wegovy (Novo Nordisk), Zepbound KwikPen (Eli Lilly), and oral Foundayo.

The eligibility criteria focus on BMI thresholds and physician diagnosis, not prior conditions. This is a meaningful departure — until now, Medicare only covered these drugs when prescribed for Type 2 diabetes, prediabetes, or sleep apnoea. Covering obesity as a standalone indication is, as one physician put it, "a big deal."

"When these GLP-1s launched, because of the pricing, a lot of people got left behind," said Dr Sohaib Imtiaz, chief medical officer at People Inc. "This starts to equalize that."

## The Cost Question Nobody Is Answering

Medicare has not disclosed how much the programme will cost taxpayers. STAT News reported that the programme sidesteps federal law — which has historically excluded obesity drugs from Medicare Part D — by routing coverage directly through the government rather than through the private insurers and pharmacy benefit managers that administer Medicare Advantage and Part D plans.

Those private insurers balked at the potential costs and declined to participate. The result is that taxpayers and beneficiaries who fill prescriptions will foot the bill, with no published estimate of the total outlay. Analysts expect the cost to run into billions, given that even modest uptake among 14 million eligible beneficiaries would generate enormous pharmaceutical revenue for Eli Lilly and Novo Nordisk.

Meanwhile, the insurance landscape is shifting in parallel. CVS Caremark, one of the largest pharmacy benefit managers, announced it will drop coverage of Zepbound effective July 1, pushing patients toward Wegovy as its preferred GLP-1 for weight management. Patients switching medications may need to restart at lower doses and re-titrate, creating a disruptive transition.

## What This Means for NRI Families

For the Indian diaspora in the United States, this programme has particular relevance. Many NRI families have elderly parents on Medicare — either living with them in multigenerational households or aging in place with support from adult children managing care logistics from across the country or across the world.

Obesity and metabolic syndrome in older South Asian adults are well-documented challenges. South Asians accumulate visceral fat at lower BMIs than other populations, and the metabolic consequences — insulin resistance, cardiovascular disease, fatty liver — accelerate with age. GLP-1 medications have shown significant benefits beyond weight loss, including reductions in cardiovascular events and improvements in fatty liver markers.

At $50 a month, the financial barrier drops dramatically. But navigating the programme still requires active management: ensuring the physician documents an obesity diagnosis, selecting among the three covered medications, and monitoring for side effects that are more common in older patients (nausea, gastroparesis, muscle loss).

For families coordinating elder care remotely — a reality for many NRIs with parents in suburbs with limited public transit or specialist access — telehealth providers are increasingly offering GLP-1 prescribing and monitoring, though questions about safety oversight remain.

## The Bigger Picture

The GLP-1 Bridge programme is temporary, running through December 2027. A follow-up programme is expected but not guaranteed. For beneficiaries who start on these medications and experience significant weight loss, the prospect of losing coverage in 18 months raises questions about long-term sustainability — GLP-1 medications typically require ongoing use to maintain results.

The programme also raises a precedent question. If Medicare can cover obesity drugs through a pilot that bypasses existing law, the door opens for broader pharmaceutical coverage initiatives. Whether that is a positive development for healthcare costs or a windfall for drugmakers depends on who you ask.

For now, if you have a parent or grandparent on Medicare who has struggled with weight-related health issues, July 1 is a date worth marking.

*Sources: STAT News, People, Reuters, CMS, CVS Caremark, KFF Health News*"""

# ═══════════════════════════════════════════════════════════════
# ARTICLE 3 — Markets-Finance
# SpaceX IPO: The Largest Listing in History
# ═══════════════════════════════════════════════════════════════

art3_slug = "spacex-ipo-june-12-largest-listing-history-2-trillion-nri-investors-20260602"
art3_headline = "SpaceX Will Go Public on June 12. At Up to $2 Trillion, It Will Be the Largest IPO in History. Here Is What NRI Investors Need to Know."
art3_subheadline = "Elon Musk's rocket and satellite company plans to raise up to $86.5 billion in a single offering. Morningstar says it is overvalued by nearly half. The listing will test whether the current rally can absorb the largest capital extraction U.S. equity markets have ever seen."

art3_body = """SpaceX, the rocket, satellite, and AI conglomerate controlled by Elon Musk, is set to begin trading on the Nasdaq under the ticker SPCX on June 12, in what will be the largest initial public offering in the history of global capital markets.

The company is targeting a valuation of $1.8 trillion to $2 trillion and plans to raise approximately $75 billion to $86.5 billion from the offering. For context, Alibaba's 2014 IPO raised $21.8 billion. Facebook's 2012 listing raised $16 billion. SpaceX plans to raise more than four times the previous record in a single transaction.

## What SpaceX Actually Is Now

SpaceX's S-1 registration statement, filed with the SEC on May 20, reveals a company that has expanded far beyond rocket launches. The revenue breakdown shows three distinct businesses:

**Starlink** — the satellite internet service — generated $11.4 billion in revenue in 2025 and is the company's largest segment. With over 200 million subscribers globally and growing, Starlink provides broadband to underserved areas, maritime vessels, and airlines.

**Launch services** — SpaceX's core business of putting payloads into orbit — brought in $4.1 billion. This includes commercial satellite launches, NASA missions, and a growing roster of Department of Defence contracts, including a $4 billion agreement announced on May 29.

**xAI** — the artificial intelligence division that SpaceX absorbed after acquiring Musk's AI company in February — added $3.2 billion, largely from data centre operations. Anthropic, the AI lab, recently signed a $1.25 billion-per-month deal to access compute capacity at SpaceX's Colossus data centres through May 2029.

## Why the Market Is Nervous

The sheer size of the offering has Wall Street divided. The IPO will extract more new cash from U.S. equity markets in a single event than any prior listing, and some investors worry about the impact on a market that has already rallied sharply.

"There is no (even vaguely close) historical precedent to such a capital raise," wrote Rupert Mitchell of Blind Squirrel Macro, a former Salomon Brothers and Goldman Sachs executive. "I think it will place a huge test on the stability of the U.S. equity market."

Mitchell estimates that investors will need to deploy roughly half a trillion dollars — covering the $75 billion base offering plus a 15 per cent greenshoe option — for the listing to be considered a success.

The S&P 500 has closed higher for nine consecutive weeks, its longest streak since late 2023. The Nasdaq is approaching 30,000 points. The concern is that SpaceX's IPO could be the event that breaks the momentum, pulling capital away from existing positions to chase the new listing.

Barron's argued that the SpaceX IPO "could signal the end of the stock market rally," noting that the listing arrives just as earnings season momentum fades, inflation pressures persist, and the U.S.–Iran ceasefire remains fragile.

## Morningstar Says It Is Overvalued

Morningstar initiated coverage of SpaceX on Monday with a valuation of $780 billion — roughly 48 per cent below the expected listing price. Analysts Nicolas Owens and Suryansh Sharma assigned a "narrow moat" rating, citing uncertainty around the AI segment.

"Our discounted cash flow valuation of SpaceX is $780 billion, about 48 per cent below its private market valuation, including a wide range of probability-weighted scenarios for the AI business," they wrote. "In short, the outlook is very uncertain."

Morningstar expects heavy initial demand driven by investor appetite for AI infrastructure and a fast-track path to the Nasdaq-100 index — SpaceX could enter the index as early as July 7, just 15 trading days after listing. But selling pressure may emerge in the months after, as lockup windows for private investors and employees open.

## What NRI Tech Investors Should Consider

For the Indian diaspora's substantial community of tech-sector professionals and retail investors, SpaceX's IPO is the defining market event of 2026. Several considerations:

**Index fund exposure.** If SpaceX enters the Nasdaq-100 in July, every index fund and ETF tracking the QQQ will automatically become a buyer. If you hold Nasdaq-100 index funds in your 401(k) or brokerage account, you will own SpaceX whether you choose to or not.

**Valuation risk.** Morningstar's $780 billion estimate versus the $2 trillion target means a potential 48 per cent downside if fundamentals reassert themselves. The AI division — inherited from the xAI acquisition — is the least proven segment and the one driving the most aggressive valuation assumptions.

**Lockup dynamics.** Musk's 40 per cent economic stake is locked for one year. But other insiders can begin selling in tranches as early as 180 days after the offering, with additional windows opening every 15-20 days between earnings reports. This creates a persistent supply overhang.

**SpaceX is not a pure-play space company.** With xAI and Starlink in the mix, SpaceX is a conglomerate. Investors buying for the rocket business are also buying an AI data centre operation and a satellite internet provider. Each segment carries different risks and growth trajectories.

The Renaissance IPO ETF (ticker: IPO) gained 2.7 per cent on Monday, reflecting broad enthusiasm for the upcoming listing. Whether that enthusiasm survives contact with a $2 trillion valuation and a nervous June market remains to be seen.

*Sources: SpaceX S-1 Filing, Morningstar, Barron's, MarketWatch, The Motley Fool, Ameriprise Research, The Street*"""


# ═══════════════════════════════════════════════════════════════
# IMAGE SOURCING
# ═══════════════════════════════════════════════════════════════

print("\n=== Image Sourcing ===\n")

# Article 1: Inhaled insulin for kids - no specific person, use Pexels
print("Article 1: Inhaled insulin / diabetes in children")
art1_img = fetch_pexels_image("child using inhaler medical device", "diabetes insulin treatment child")
art1_attribution = "Pexels"

# Article 2: Medicare GLP-1 - no specific person, use Pexels
print("\nArticle 2: Medicare GLP-1 weight loss drugs")
art2_img = fetch_pexels_image("senior citizen pharmacy medication", "elderly patient prescription drugs")
art2_attribution = "Pexels"

# Article 3: SpaceX IPO - try Wikipedia for Elon Musk or SpaceX, or Pexels
print("\nArticle 3: SpaceX IPO")
art3_img = fetch_wikipedia_person_image("SpaceX")
if not art3_img:
    art3_img = fetch_wikipedia_person_image("Elon Musk")
art3_attribution = "Wikimedia Commons"
if not art3_img:
    art3_img = fetch_pexels_image("rocket launch space", "spacecraft launch pad")
    art3_attribution = "Pexels"


# ═══════════════════════════════════════════════════════════════
# UPLOAD & INSERT
# ═══════════════════════════════════════════════════════════════

print("\n=== Uploading Images ===\n")

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = [
    {
        "slug": art1_slug,
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "body": art1_body,
        "category": "lifestyle-health",
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "FDA", "url": "https://www.fda.gov"},
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "MedPage Today", "url": "https://www.medpagetoday.com"},
            {"name": "MannKind Corporation", "url": "https://www.mannkindcorp.com"},
        ]),
        "image_url": None,
        "image_attribution": art1_attribution,
    },
    {
        "slug": art2_slug,
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "body": art2_body,
        "category": "lifestyle-health",
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "STAT News", "url": "https://www.statnews.com"},
            {"name": "People", "url": "https://people.com"},
            {"name": "CMS", "url": "https://www.cms.gov"},
            {"name": "KFF Health News", "url": "https://kffhealthnews.org"},
        ]),
        "image_url": None,
        "image_attribution": art2_attribution,
    },
    {
        "slug": art3_slug,
        "headline": art3_headline,
        "subheadline": art3_subheadline,
        "body": art3_body,
        "category": "markets-finance",
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "SpaceX S-1 Filing", "url": "https://www.sec.gov"},
            {"name": "Morningstar", "url": "https://www.morningstar.com"},
            {"name": "Barron's", "url": "https://www.barrons.com"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com"},
            {"name": "The Motley Fool", "url": "https://www.fool.com"},
        ]),
        "image_url": None,
        "image_attribution": art3_attribution,
    },
]

imgs = [art1_img, art2_img, art3_img]

for i, art in enumerate(articles):
    img = imgs[i]
    if img:
        art_id_temp = str(uuid.uuid4())
        filename = f"{art_id_temp}.jpg"
        final_url = upload_image_to_supabase(img, filename)
        if final_url:
            art["image_url"] = final_url
    else:
        print(f"  ⚠ No image for article {i+1}, inserting without image")

print("\n=== Inserting Articles ===\n")

for art in articles:
    # Remove None image_url
    if art["image_url"] is None:
        del art["image_url"]
        del art["image_attribution"]
    
    art_id = insert_article(art)
    if art_id:
        # If we uploaded with temp UUID, update the image filename to use real ID
        if art.get("image_url") and "article-images/" in art["image_url"]:
            old_filename = art["image_url"].split("article-images/")[-1]
            new_filename = f"{art_id}.jpg"
            if old_filename != new_filename:
                # Re-upload with correct filename
                print(f"  Renaming image to {new_filename}...")
                new_url = upload_image_to_supabase(art["image_url"], new_filename)
                if new_url and new_url != art["image_url"]:
                    # Update article with new URL
                    patch_r = requests.patch(
                        f"{SB_URL}/rest/v1/p2_articles?id=eq.{art_id}",
                        headers=SB_HEADERS,
                        json={"image_url": new_url},
                        timeout=15,
                    )
                    if patch_r.status_code in (200, 204):
                        print(f"  ✓ Updated image URL for {art['slug']}")

print("\n=== Done ===")
