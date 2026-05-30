#!/usr/bin/env python3
"""Lifestyle-Health & Markets-Finance writer — 2026-05-30 run"""

import json, os, sys, time, uuid, urllib.parse, re
import requests
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels config ────────────────────────────────────────────────────
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Image helpers ────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
    """Fetch from Pexels using specific search terms."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Verify image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't return Content-Length
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
        print(f"  ⚠ Image validation failed: status={r.status_code} ct={ct} cl={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def sb_insert(table, data):
    """Insert a row into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    print(f"  ✗ Insert to {table} failed: {r.status_code} {r.text[:200]}")
    return None


def sb_patch(table, filters, data):
    """Patch a row in Supabase."""
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=data,
    )
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch {table} failed: {r.status_code} {r.text[:200]}")
    return False


# ── Article definitions ──────────────────────────────────────────────

articles = []

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1: Long COVID Autoantibodies Discovery
# ═══════════════════════════════════════════════════════════════════

articles.append({
    "headline": "Two Studies Just Proved That Long COVID Neurological Symptoms Are Caused by the Body Attacking Itself. Existing Drugs May Already Work.",
    "subheadline": "Autoantibodies from long COVID patients caused fatigue, pain, and nerve damage when transferred to healthy mice — even two years after infection. Researchers say millions could benefit from immunotherapy treatments already on the market.",
    "slug": "long-covid-autoantibodies-neurological-symptoms-autoimmunity-treatment-south-asian-diaspora-20260530",
    "category": "lifestyle-health",
    "sources": [
        {"name": "Cell Reports Medicine", "url": "https://www.cell.com/cell-reports-medicine"},
        {"name": "Cell", "url": "https://www.cell.com/cell"},
        {"name": "Reuters Health", "url": "https://www.reuters.com/"},
        {"name": "Icahn School of Medicine at Mount Sinai", "url": "https://icahn.mssm.edu/"}
    ],
    "vertical": "lifestyle-health",
    "urgency": "daily",
    "tags": ["long COVID", "autoimmunity", "autoantibodies", "neurological symptoms", "immunotherapy", "chronic illness"],
    "diaspora_angle": "India experienced one of the world's most severe COVID waves, with seroprevalence above 90 per cent by mid-2022. South Asians in the US, UK, and Canada report higher rates of post-COVID fatigue and cognitive complaints than the general population. The autoantibody finding offers a testable biomarker and a path to targeted treatment for millions.",
    "image_search": {"type": "pexels", "query": "immune system cells antibody medical", "fallback": "neurological brain scan research"},
    "body": """Long COVID has baffled clinicians for five years. More than 200 million people worldwide have struggled with persistent fatigue, brain fog, pain sensitivity, and balance problems long after their initial SARS-CoV-2 infection cleared. Now, two landmark studies published simultaneously — one in *Cell Reports Medicine*, the other in *Cell* — have identified a central mechanism behind the neurological devastation: the body's own immune system is attacking itself.

## The Discovery

Both research teams collected autoantibodies — rogue immune proteins that mistakenly target the body's own tissues rather than foreign invaders — from the blood of long COVID patients. When these human autoantibodies were infused into healthy mice, the animals developed neurological symptoms that closely mimicked those of the patients who donated the blood.

The mice exhibited fatigue, loss of balance, heightened pain sensitivity, and measurable nerve fibre damage. In one particularly striking experiment from the *Cell Reports Medicine* study, autoantibodies collected from patients **two full years** after their initial COVID-19 infection still produced the same debilitating effects when transferred to mice. The immune system's misdirected assault, it appears, does not fade on its own.

"This new awareness of the physiology of long COVID will enable us to identify a number of effective treatments for autoimmunity that could significantly improve the symptoms of millions of people with this chronic condition," said Dr David Putrino from the Icahn School of Medicine at Mount Sinai, a coauthor of the *Cell* study.

## Why This Matters for Treatment

The breakthrough is not just diagnostic — it is immediately actionable. Autoimmune conditions have been treated for decades with well-established immunotherapy drugs, including monoclonal antibodies, plasma exchange, and immunomodulators like baricitinib (already FDA-approved for rheumatoid arthritis and used during acute COVID-19). Until now, the challenge was that clinicians had no way of knowing which long COVID patients would respond to these therapies.

"Before we had no way of predicting who would benefit from these therapies," Putrino said. "Our study now shows that if you are in a subgroup of long COVID patients who have autoantibodies circulating in your body, you may be a good candidate for these drugs."

A commentary published alongside the studies in *Cell* described the evidence as "compelling" but cautioned that autoantibodies are likely one of several mechanisms driving long COVID, not the sole explanation for every patient's experience.

## The South Asian Dimension

The findings carry particular weight for the Indian diaspora. India experienced one of the world's most severe COVID waves, and population-level seroprevalence studies suggest that well over 90 per cent of Indians had been infected by mid-2022. Community health surveys across the US, UK, and Canada have consistently shown that South Asians report higher rates of post-COVID fatigue, cognitive complaints, and pain syndromes than the general population.

Access to specialist immunology care remains uneven. In India, long COVID clinics are concentrated in metro hospitals; in the diaspora, many patients have been told their symptoms are psychosomatic or stress-related. The new autoantibody evidence provides a concrete, testable biomarker that could change the clinical conversation entirely.

For NRI families with elderly relatives in India who have been struggling with unexplained fatigue or cognitive decline since a COVID infection, a simple blood test for circulating autoantibodies — available at most major pathology labs — could now be the first step toward targeted treatment rather than years of symptomatic management.

## What Comes Next

Several clinical trials targeting the autoimmune pathway in long COVID are already underway. The REVERSE-LC trial at Vanderbilt University Medical Center is testing baricitinib in a Phase 3, placebo-controlled study. AER002, a long-acting human immunoglobulin designed to neutralise persistent spike protein, is in Phase 2 testing. And existing IVIG (intravenous immunoglobulin) protocols used for other autoimmune conditions are being adapted for long COVID patients who test positive for pathogenic autoantibodies.

The timeline from bench to bedside may be unusually short. Unlike novel drug development, repurposing existing immunotherapy agents for a newly understood mechanism can move through regulatory channels in months rather than years."""
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2: Mounjaro SURPASS-EARLY — Best GLP-1 for Early Diabetes
# ═══════════════════════════════════════════════════════════════════

articles.append({
    "headline": "Mounjaro Outperformed Every Other GLP-1 Drug in a Two-Year Trial of Early Type 2 Diabetes Patients. 60 Per Cent Achieved Normal Blood Sugar.",
    "subheadline": "The SURPASS-EARLY trial found that tirzepatide helped recently diagnosed patients reach glycaemic targets 4 to 12 weeks faster than semaglutide and produced sustained normal HbA1c levels in more than double the patients on competing drugs.",
    "slug": "mounjaro-tirzepatide-surpass-early-type-2-diabetes-glp1-south-asian-20260530",
    "category": "lifestyle-health",
    "sources": [
        {"name": "Annals of Internal Medicine", "url": "https://www.acpjournals.org/journal/aim"},
        {"name": "Reuters Health", "url": "https://www.reuters.com/"},
        {"name": "Eli Lilly and Company", "url": "https://www.lilly.com/"},
        {"name": "Drug Topics / EASD", "url": "https://www.drugtopics.com/"}
    ],
    "vertical": "lifestyle-health",
    "urgency": "daily",
    "tags": ["Mounjaro", "tirzepatide", "type 2 diabetes", "GLP-1", "SURPASS-EARLY", "South Asian health", "insulin resistance"],
    "diaspora_angle": "South Asians have among the highest type 2 diabetes rates globally — 23 per cent prevalence among Indian Americans vs 11 per cent in the general US population. They develop diabetes a decade earlier and at lower BMI thresholds, making early aggressive treatment even more critical. The SURPASS-EARLY data directly supports earlier intervention with tirzepatide for this population.",
    "image_search": {"type": "pexels", "query": "blood sugar glucose monitor diabetes", "fallback": "diabetes insulin injection health"},
    "body": """A new two-year clinical trial has established Eli Lilly's Mounjaro as the most effective GLP-1 drug for recently diagnosed type 2 diabetes patients — a finding with outsized implications for the South Asian community, which faces among the highest diabetes rates of any ethnic group worldwide.

## The Trial

The SURPASS-EARLY trial, published in the *Annals of Internal Medicine* and presented at the American Society of Clinical Oncology meeting in Chicago, enrolled nearly 800 adults who had been diagnosed with type 2 diabetes within the previous four years and whose blood sugar remained poorly controlled despite treatment with metformin, the standard first-line medication, combined with diet and exercise.

Patients were randomly assigned to add either tirzepatide — the active ingredient in Mounjaro — or another medication to their existing metformin regimen. Most patients in the control group received other GLP-1 drugs, including Novo Nordisk's semaglutide (sold as Ozempic and Rybelsus for diabetes) or Lilly's older drug Trulicity (dulaglutide).

The results after two years were decisive.

## The Numbers

Roughly **60 per cent** of patients receiving tirzepatide achieved normal blood sugar levels (HbA1c below 5.7 per cent), compared to just **24 per cent** of patients on other GLP-1 drugs. Tirzepatide patients also showed significantly greater improvements in weight loss and waist circumference — both critical markers for the metabolic syndrome that disproportionately affects South Asians.

A separate analysis of pooled data from the broader SURPASS programme, presented at the European Association for the Study of Diabetes annual meeting, found that tirzepatide helped patients reach glycaemic targets **4 to 12 weeks sooner** than those receiving semaglutide or long-acting insulin degludec.

"Tirzepatide is unique because it mimics two natural insulin-releasing and appetite-suppressing hormones in one injection," said lead investigator Dr Adie Viljoen, a consultant metabolic physician at the East and North Hertfordshire NHS Trust. "The speed we are seeing in glucose-lowering and weight loss is beyond anything else we have available right now."

## Why Early Intervention Matters

The study's most significant implication may not be which drug won, but when treatment should begin. The researchers found that patients who started tirzepatide early — within four years of diagnosis, when metformin alone was insufficient — experienced "stronger and more sustained metabolic benefits" than patients who waited longer or used less potent add-on therapies.

This matters enormously because type 2 diabetes is a progressive disease. The longer blood sugar remains elevated, the more damage accumulates in blood vessels, nerves, kidneys, and the retina. South Asians develop diabetic complications at lower BMI and lower blood sugar thresholds than European-descent populations, making early aggressive treatment even more critical.

## The South Asian Crisis

The numbers are staggering. India has an estimated 101 million people living with diabetes — the highest absolute count of any country. The prevalence among Indian Americans in the US is roughly 23 per cent, compared to 11 per cent in the general US population. And South Asians tend to develop type 2 diabetes a decade earlier than white populations, often in their 30s and 40s, driven by a combination of genetic insulin resistance, visceral fat distribution, and dietary patterns high in refined carbohydrates.

For NRI families, the practical question is immediate: if a parent or sibling in India or a family member in the US has been on metformin for years without reaching target HbA1c, the SURPASS-EARLY data suggests that adding tirzepatide early — rather than waiting for the disease to progress — could be the difference between achieving normal blood sugar and spending decades managing complications.

## Cost and Access

Mounjaro's list price in the US is roughly $1,000 per month without insurance. Most commercial insurance plans now cover it for type 2 diabetes (its FDA-approved indication), though prior authorisation is often required. In India, tirzepatide was launched in late 2025 at approximately ₹15,000–18,000 per month — expensive by Indian standards but significantly cheaper than the US price.

Generic versions are not yet available, but Lilly has signed licensing agreements with several Indian pharmaceutical manufacturers. Biosimilar competition is expected to begin driving prices down by 2028.

## What to Ask Your Doctor

The SURPASS-EARLY results reinforce a shift already underway in diabetes care: treating early and treating aggressively, rather than starting with the mildest intervention and escalating only after years of inadequate control. For South Asian patients, who face higher baseline risk and faster disease progression, that message is especially urgent.

If you or a family member has been on metformin for more than a year without achieving an HbA1c below 7 per cent, the data now supports a conversation about adding a GLP-1 drug — and tirzepatide, based on this trial, appears to be the most effective option in the class."""
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3: Markets — US-Iran Deal, Hormuz, and the Week Ahead
# ═══════════════════════════════════════════════════════════════════

articles.append({
    "headline": "The US and Iran Have a Deal to Reopen the Strait of Hormuz. Markets Rallied. But a Reuters Analysis Says It May Change Nothing.",
    "subheadline": "A 60-day truce extension would lift shipping restrictions and require Iran to de-mine the strait within 30 days. But global oil reserves are running out, the PCE just hit 3.8 per cent, and Friday's US jobs report could push the Fed toward a rate hike. Here is what NRI investors should watch.",
    "slug": "us-iran-hormuz-deal-60-day-truce-oil-markets-nri-investors-week-ahead-june-2026",
    "category": "markets-finance",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "Axios", "url": "https://www.axios.com/"},
        {"name": "New York Post", "url": "https://nypost.com/"},
        {"name": "Brookings Institution", "url": "https://www.brookings.edu/"},
        {"name": "The Sun", "url": "https://www.thesun.co.uk/"}
    ],
    "vertical": "markets-finance",
    "urgency": "daily",
    "tags": ["US-Iran", "Strait of Hormuz", "oil prices", "Brent crude", "Fed rate hike", "PCE inflation", "NRI investments", "RBI"],
    "diaspora_angle": "India imports 85 per cent of its crude oil. Every $10 rise in Brent costs India roughly $15 billion annually. The Hormuz deal directly affects the rupee, RBI rate decisions, NRI deposit rates, and inflation-sensitive portfolios held by diaspora investors.",
    "image_search": {"type": "pexels", "query": "oil tanker ship strait ocean", "fallback": "crude oil barrel global trade"},
    "body": """The United States and Iran reached an agreement on May 28 to extend their ceasefire for 60 days and reopen the Strait of Hormuz to unrestricted commercial shipping, Reuters reported, citing sources familiar with the deal. Markets rallied on the news, with Brent crude dropping from $94.50 to about $91.30 per barrel within hours. But the agreement remains unsigned — President Trump has not yet approved it, Iran says it has not been finalised, and a sobering analysis from Reuters warns that even a successful deal may not prevent a global oil crunch that is already well underway.

## The Deal

The tentative agreement, first reported by Axios, would require Iran to remove all mines from the Strait of Hormuz within 30 days and guarantee unrestricted shipping through the waterway — meaning no tolls, no harassment, and no military interference. In return, the United States would lift its naval blockade of Iranian ports and ease some sanctions on Iranian oil sales.

The deal would also open formal negotiations on Iran's nuclear programme, with Tehran pledging to discuss destroying its highly enriched uranium and future enrichment activities. The US would commit to discussing the release of $12 billion in frozen Iranian assets.

Trump posted on Truth Social on Friday that Iran would remove its mines and end the strait closure "with no tolls," while the US would lift its "parallel blockade." But Iran's foreign ministry spokesman Esmaeil Baqaei told state media that "no final agreement has been reached yet" and that the republic "said goodbye to the language of 'must' 47 years ago."

## Why the Market Reaction May Be Premature

Reuters' Yawen Chen published a pointed analysis on Friday arguing that a ceasefire extension is "no solution to the Hormuz crisis" and could simply postpone a deeper reckoning.

The core problem: the Strait of Hormuz has been effectively closed to commercial shipping for three months. During that period, governments worldwide have released more than 400 million barrels from emergency petroleum reserves. The Brookings Institution estimates that once those reserves and other temporary buffers are exhausted — likely by July — the global market will face a shortfall equivalent to roughly **16 per cent of global crude trade**. That is a gap no 60-day truce can fill.

Even if the strait reopens and shipping resumes, crude prices are unlikely to return to pre-crisis levels. Physical infrastructure in the Gulf has been damaged, inventories need replenishing, and insurers are demanding war-risk premiums on tankers transiting the waterway.

Brent crude settled at $92.05 per barrel on Friday, down 1.77 per cent on the day but still well above the $70–75 range that prevailed before the conflict began.

## The Inflation Problem Is Already Here

Thursday's Personal Consumption Expenditures (PCE) price index — the Federal Reserve's preferred inflation gauge — showed annual inflation at **3.8 per cent** in April, nearly double the Fed's 2 per cent target. It is expected to top 4 per cent in May, driven almost entirely by energy costs.

The data has transformed the Fed outlook. Markets now see a greater probability of a rate **hike** than a cut in 2026. Fed Board member Lisa Cook said on Wednesday that if disinflation does not resume soon, she would be "prepared to raise rates." New Fed Chair Kevin Warsh, who took over this year, faces his first meeting in June with inflation running at levels that leave little room for the rate cuts President Trump has publicly demanded.

## The Week Ahead

Friday's May non-farm payrolls report is expected to show job growth slowing to 96,000 and an unemployment rate of 4.3 per cent, according to a Reuters poll. A stronger-than-expected number could signal overheating and rattle bonds further. Manufacturing and services data will offer additional clues on economic momentum.

The S&P 500 closed at 7,580.12 on Friday, the Dow at 51,032.65, and the Nasdaq at 26,972.62 — all modestly higher on the day. Remarkably, the S&P 500 has climbed more than 9 per cent since the start of the US-Iran conflict, with Goldman Sachs raising its year-end target from 7,600 to 8,000, citing strong corporate earnings.

But rising Treasury yields remain the market's biggest vulnerability. The 10-year yield settled at 4.441 per cent, and the 30-year at 4.98 per cent. The dollar index fell 0.1 per cent to 98.90, with the euro at $1.1663.

## What This Means for NRI Portfolios

**Oil and energy exposure:** India imports roughly 85 per cent of its crude. Every $10 rise in Brent costs India approximately $15 billion annually in additional import bills. If the Hormuz deal collapses or oil climbs past $100, the rupee will come under renewed pressure, the RBI's foreign exchange reserves (already at a one-year low of $681 billion) will deplete faster, and inflation-indexed bonds could outperform equities.

**Fixed income:** The RBI meets on June 5. Bond traders are pricing in up to 100 basis points of hikes. NRI deposits in Indian banks could see rising rates, making FCNR and NRE fixed deposits more attractive than they have been in years.

**US equities:** If payrolls come in hot and the Fed signals a hike, growth stocks and high-multiple tech names — which dominate many NRI portfolios — could face a sharp correction. Defensive sectors (utilities, healthcare, consumer staples) and inflation hedges (TIPS, commodity ETFs, energy stocks) deserve a closer look.

**The rupee:** The Indian currency had its best day in two months on Friday, aided by the oil price dip and RBI intervention. But the relief could be short-lived. If the Hormuz deal falls apart over the weekend, Monday's open in Mumbai could be volatile.

The bottom line: the deal is real but fragile. Its success depends not on whether Iran and the US sign a piece of paper, but on whether crude oil actually starts flowing again — and whether 400 million barrels of depleted reserves can be rebuilt before the next escalation."""
})

# ── Publish articles ─────────────────────────────────────────────────

now = datetime.now(timezone.utc).isoformat()

for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {article['headline'][:70]}...")
    print(f"Category: {article['category']}")
    
    # Generate article ID
    art_id = str(uuid.uuid4())
    
    # Image sourcing
    img_url = None
    img_attribution = None
    search_info = article.pop("image_search")
    
    if search_info["type"] == "pexels":
        img_url = fetch_pexels_image(search_info["query"], search_info.get("fallback"))
        img_attribution = "Pexels"
    
    if img_url and not validate_image(img_url):
        print(f"  ⚠ Image failed validation, trying fallback...")
        img_url = fetch_pexels_image(search_info.get("fallback"))
        if img_url and not validate_image(img_url):
            img_url = None
    
    if not img_url:
        print(f"  ⚠ No valid image found, publishing without image")
    
    # Build article record
    record = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article.get("vertical", article["category"]),
        "body": article["body"],
        "sources": article["sources"],
        "tags": article.get("tags", []),
        "urgency": article.get("urgency", "daily"),
        "diaspora_angle": article.get("diaspora_angle"),
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
    }
    
    if img_url:
        record["image_url"] = img_url
        record["image_attribution"] = img_attribution
    
    result = sb_insert("p2_articles", record)
    if result:
        print(f"  ✓ Published: {article['slug']}")
        print(f"    ID: {art_id}")
        if img_url:
            print(f"    Image: {img_url[:80]}...")
    else:
        print(f"  ✗ FAILED to publish: {article['slug']}")
    
    time.sleep(1)

print(f"\n{'='*60}")
print("Writer run complete.")
