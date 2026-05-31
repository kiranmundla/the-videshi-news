#!/usr/bin/env python3
"""
Videshi Lifestyle-Health & Markets-Finance Writer
Publishes 2 lifestyle-health + 1 markets-finance articles
"""

import json, os, sys, uuid, re, time
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, _, val = line.partition('=')
                val = val.strip().strip('"').strip("'")
                os.environ[key.strip()] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

import requests
import urllib.parse

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def sb_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        return r.json()
    print(f"  ✗ Insert error ({r.status_code}): {r.text[:200]}")
    return None

def sb_patch(table, match, data):
    params = "&".join(f"{k}={v}" for k, v in match.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch error ({r.status_code}): {r.text[:200]}")
    return False

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
    """Fetch an image from Pexels. Use curl-style headers."""
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
                timeout=15
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

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket article-images."""
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
        if r.status_code != 200:
            print(f"  ✗ Image download failed ({r.status_code})")
            return image_url  # fallback to direct URL if it's permanent
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if not content_type.startswith('image/'):
            print(f"  ✗ Not an image: {content_type}")
            return image_url
        if len(r.content) < 5000:
            print(f"  ✗ Image too small ({len(r.content)} bytes)")
            return None
        
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true"
        }
        up = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
            headers=upload_headers,
            data=r.content,
            timeout=30
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed ({up.status_code}): {up.text[:200]}")
            # If the source is permanent (wikimedia/pexels), use directly
            if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
                return image_url
            return None
    except Exception as e:
        print(f"  ✗ Upload exception: {e}")
        if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
            return image_url
        return None

def validate_image_url(url):
    """Check URL is not from banned sources."""
    if not url:
        return False
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', 'scontent-']
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ BANNED source detected: {b}")
            return False
    for p in banned_params:
        if p in url:
            print(f"  ✗ BANNED param detected: {p}")
            return False
    return True

# ============================================================
# ARTICLES
# ============================================================

articles = []

# ------ Article 1: Lifestyle-Health ------
# ARACOG Trial: Darolutamide preserves cognitive function vs enzalutamide

art1 = {
    "headline": "A Head-to-Head Trial Found That One Prostate Cancer Drug Causes Half the Cognitive Decline of Another. Every Patient Who Switched Was on the Worse Drug.",
    "subheadline": "The ARACOG trial, presented at ASCO 2026, is the first rigorous comparison of how two standard prostate cancer drugs affect memory, attention, and executive function. The results may change how doctors and families approach treatment decisions.",
    "slug": "darolutamide-nubeqa-cognitive-decline-prostate-cancer-asco-2026-south-asian-families",
    "category": "lifestyle-health",
    "sources": json.dumps(["ASCO 2026 Annual Meeting, Abstract #5005", "Urology Times", "AJMC", "Bayer / Alliance Foundation Trials"]),
    "person_for_image": "Alicia Morgans oncologist",
    "image_search": "prostate cancer treatment hospital",
    "image_fallback": "elderly man doctor consultation",
    "body": """When a man is diagnosed with advanced prostate cancer, the conversation with his oncologist almost always turns to androgen receptor pathway inhibitors — drugs that block testosterone from fuelling the tumour. Two of the most widely prescribed are darolutamide (sold as Nubeqa) and enzalutamide (sold as Xtandi). Both control the disease effectively. Until this week, no one had rigorously measured what they do to the brain.

The ARACOG trial, presented on May 30 at the American Society of Clinical Oncology annual meeting in Chicago, is the first head-to-head, randomised comparison of cognitive function between the two drugs. The results were striking enough to be highlighted in ASCO's press programme.

## What the Trial Found

Researchers at Dana-Farber Cancer Institute, led by Alicia Morgans, MD, enrolled 111 men with advanced prostate cancer and randomly assigned them to either darolutamide or enzalutamide. Over 24 weeks, they objectively measured cognitive performance across multiple domains — executive function, working memory, visual memory, and attention.

The primary endpoint was the maximally changed cognitive domain, essentially the area of thinking where a patient's brain took the biggest hit. Patients on darolutamide experienced a median decline of 15.8 per cent. Patients on enzalutamide declined by 36.1 per cent — more than double. The difference was statistically significant (p=0.009).

The largest gaps appeared in executive function and working memory. These are the cognitive abilities that let you follow a conversation, remember where you put your car keys, and manage the logistics of daily life. For a 65-year-old man whose family is already anxious about his cancer diagnosis, losing those abilities is not abstract — it shapes whether he can live independently.

## Every Patient Who Switched Was on Enzalutamide

Perhaps the most telling detail was the crossover data. The trial allowed patients to switch drugs at 12 or 24 weeks if they experienced significant cognitive decline. By 24 weeks, 23 patients had crossed over. Every single one of them had been randomised to enzalutamide and switched to darolutamide. Not a single darolutamide patient chose to switch the other way.

The reason, according to the researchers, is structural. Enzalutamide crosses the blood-brain barrier more readily than darolutamide. Higher central nervous system exposure means more cognitive side effects. Preclinical models had suggested this difference for years. The ARACOG trial is the first to prove it in patients.

## Why This Matters for South Asian Families

Prostate cancer is the second most common cancer in men worldwide, and its incidence among Indian men has risen sharply over the past two decades. In the diaspora, where men often delay screening and are diagnosed at more advanced stages, the choice of treatment drug carries outsized consequences.

For South Asian families, cognitive decline in a father or grandfather is not just a medical issue — it restructures the household. The generation of Indian men now reaching prostate cancer age (60 to 75) often serve as the family's decision-makers, financial planners, and emotional anchors. Losing executive function means losing that role, sometimes irreversibly.

The ARACOG data give families and doctors a concrete, evidence-based reason to prefer darolutamide when both drugs are equally effective against the cancer itself. The conversation is no longer just about tumour control. It is about preserving the person behind the diagnosis.

## What Comes Next

Researchers are continuing to monitor participants out to 48 weeks to assess whether the cognitive gap widens, stabilises, or narrows over time. They are also investigating genetic factors that may make some men more vulnerable to treatment-related cognitive decline.

The trial was funded by the Prostate Cancer Foundation and Bayer, which manufactures darolutamide. Longer-term survival comparisons between the two drugs in this specific context remain ongoing. For now, the message from Chicago is clear: when two drugs work equally well against the cancer, the one that spares the brain deserves serious consideration."""
}
articles.append(art1)

# ------ Article 2: Lifestyle-Health ------
# Lifyorli (relacorilant) — cortisol-blocking drug cuts ovarian cancer death risk 35%

art2 = {
    "headline": "A Drug That Blocks Cortisol Just Cut the Risk of Death From Ovarian Cancer by 35 Per Cent. No Biomarker Testing Was Required.",
    "subheadline": "The Phase 3 ROSELLA trial found that adding the cortisol-blocking drug relacorilant to chemotherapy extended survival in platinum-resistant ovarian cancer patients — regardless of prior treatment history. The results, presented at ASCO 2026, could establish a new standard of care.",
    "slug": "lifyorli-relacorilant-cortisol-ovarian-cancer-asco-2026-south-asian-women-health",
    "category": "lifestyle-health",
    "sources": json.dumps(["ASCO 2026 Annual Meeting, ROSELLA trial", "Corcept Therapeutics / BusinessWire", "StockTitan", "McGill University"]),
    "person_for_image": None,
    "image_search": "ovarian cancer research laboratory",
    "image_fallback": "medical research oncology treatment",
    "tags": ["health", "ovarian-cancer", "cortisol", "asco-2026", "relacorilant", "lifyorli", "south-asian-women", "cancer-treatment"],
    "body": """Platinum-resistant ovarian cancer is one of the most difficult diagnoses in oncology. By definition, it means the cancer has returned within six months of completing platinum-based chemotherapy — the frontline treatment. At that point, options narrow dramatically, and median survival on standard second-line therapy is typically less than a year.

A trial presented at the 2026 American Society of Clinical Oncology annual meeting in Chicago may have just changed that calculus. The Phase 3 ROSELLA trial showed that adding relacorilant, a cortisol-blocking drug now branded as Lifyorli, to standard nab-paclitaxel chemotherapy reduced the risk of death by 35 per cent compared to chemotherapy alone.

## The Numbers

The trial enrolled patients with platinum-resistant ovarian cancer and randomly assigned them to receive nab-paclitaxel plus either relacorilant or placebo. The results were unambiguous.

Patients who received the combination lived a median of 16.0 months, compared to 11.9 months for those on chemotherapy alone. The hazard ratio was 0.65, with a p-value of 0.0004 — a level of statistical significance that leaves very little room for chance.

What makes the data particularly compelling is their consistency. The survival benefit held across every prespecified subgroup, including patients who had received a taxane in their most recent prior treatment (hazard ratio: 0.67) and those with a taxane-free interval of six months or less (hazard ratio: 0.60). No biomarker testing was needed to identify who would benefit.

## How Cortisol Fuels Cancer

The mechanism behind relacorilant targets something most people associate with stress rather than cancer: cortisol. Cortisol is the body's primary stress hormone, and in normal amounts it regulates metabolism, immune function, and inflammation. But tumours can exploit cortisol signalling to suppress the immune response and resist chemotherapy.

Relacorilant is a selective cortisol modulator — it blocks the glucocorticoid receptor without affecting other steroid pathways. By removing cortisol's protective effect on tumour cells, the drug makes chemotherapy more effective. The cancer loses its shield.

This is a conceptually different approach from immunotherapy or targeted therapy. It does not require genetic testing or biomarker selection. It works by changing the hormonal environment in which the tumour operates.

## Why South Asian Women Should Pay Attention

Ovarian cancer is the third most common gynaecological cancer in Indian women, and it carries a high mortality rate in part because it is often diagnosed late. Symptoms — bloating, pelvic pain, changes in appetite — are vague and easily dismissed, especially in cultures where women's health complaints are sometimes deprioritised.

For South Asian women in the diaspora, the barriers are compounded. Language gaps with healthcare providers, cultural reluctance to discuss reproductive health, and delayed screening mean that many are diagnosed at advanced stages. By the time platinum resistance develops, treatment options have historically been limited.

The ROSELLA trial offers a new option that does not depend on biomarkers, complex genetic testing, or access to specialised immunotherapy centres. It is a pill added to a standard chemotherapy regimen. That simplicity matters for access and adoption.

Research has also suggested that South Asians may have elevated baseline cortisol levels compared to other ethnic groups, driven by a combination of genetic, dietary, and psychosocial factors. If cortisol does play a role in tumour resistance — as the ROSELLA data strongly suggest — then populations with higher cortisol exposure could theoretically benefit even more from cortisol-blocking strategies. This hypothesis has not been tested directly, but it underscores why the mechanism deserves attention from South Asian health researchers.

## What Happens Now

Corcept Therapeutics, which developed relacorilant, has positioned Lifyorli as a potential new standard of care for platinum-resistant ovarian cancer. Regulatory filings are expected to follow the ASCO presentation. The drug is already approved in the United States for Cushing's syndrome, so its safety profile is well-characterised.

Lucy Gilbert, MD, Director of Gynecologic Oncology at McGill University, said the consistent survival benefit across all patient subgroups, including those with poor prognostic features, makes relacorilant a candidate for broad adoption without the need for patient selection based on testing.

For the roughly 22,000 women diagnosed with ovarian cancer in the United States each year — and the estimated 60,000 in India — the ROSELLA trial represents one of the most significant survival improvements in platinum-resistant disease in over a decade."""
}
articles.append(art2)

# ------ Article 3: Markets-Finance ------
# Week ahead: RBI MPC + US Jobs + Rate hike expectations

art3 = {
    "headline": "The RBI Decides on Rates This Week. So Does the US Jobs Report. NRI Investors Are Caught Between Two Central Banks With Very Different Problems.",
    "subheadline": "India's Monetary Policy Committee meets June 3-5 with analysts split between a hold and a hike, while US nonfarm payrolls on Friday could cement the case for the Fed's first rate increase. Here is what NRI investors should watch across both economies.",
    "slug": "rbi-mpc-june-2026-us-jobs-nonfarm-payrolls-nri-investors-week-ahead",
    "category": "markets-finance",
    "sources": json.dumps(["Reuters poll of 56 economists", "Outlook Money", "Wall Street Journal", "Mizuho Securities / Vishnu Varathan", "FXStreet"]),
    "person_for_image": "Sanjay Malhotra RBI",
    "image_search": "Reserve Bank of India building",
    "image_fallback": "Indian central bank monetary policy",
    "tags": ["markets", "rbi", "monetary-policy", "us-jobs", "nonfarm-payrolls", "fed", "nri-investors", "rupee", "interest-rates"],
    "body": """The first week of June will force NRI investors to watch two central banks navigate two very different problems at the same time. In Mumbai, the Reserve Bank of India's Monetary Policy Committee meets from June 3 to 5, with Governor Sanjay Malhotra announcing the decision on the morning of June 5. In Washington, the May nonfarm payrolls report arrives on June 6, and it could seal the case for the Federal Reserve's first rate increase under new Chair Kevin Warsh.

For investors who hold assets in both countries — which describes a large share of the Indian diaspora — the outcomes of this week will shape portfolio decisions for the rest of the quarter.

## The RBI's Dilemma: Low Inflation, Rising Risks

On paper, the RBI has room to hold. India's retail inflation stood at 3.48 per cent in April, well below the central bank's 4 per cent target and the lowest reading in over a year. The repo rate sits at 5.25 per cent, where it has been since February 2026.

But the backdrop is more complicated than the headline number suggests. Crude oil prices remain roughly 30 per cent above pre-conflict levels. The rupee has fallen approximately 6 per cent this year, touching nearly 97 to the dollar. Wholesale inflation has accelerated sharply. And the monsoon forecast — which directly affects food prices and, by extension, the inflation trajectory for the second half of the year — has turned uncertain.

A Reuters poll of 56 economists found that 44 expect the RBI to hold rates at 5.25 per cent. But 11 forecast a 25-basis-point hike, and one predicted a 50-basis-point increase. In April's poll, only a single economist had predicted a June hike. The shift in sentiment is significant.

Vishnu Varathan, managing director at Mizuho Securities, has argued that a pre-emptive hike in June — even if out of consensus — would be strategically constructive for the rupee. Standard Chartered has projected a 50-basis-point increase over the current fiscal year, with the first move potentially coming this week.

The RBI's commentary on liquidity, the rupee, and food inflation will matter as much as the rate decision itself. If Governor Malhotra signals that the committee is leaning hawkish even while holding, markets will begin pricing a July or August hike.

## The US Side: Jobs Data Could Seal a Rate Hike

Across the Pacific, the picture is inverted. The Federal Reserve's problem is not a weak currency or imported inflation — it is domestic demand that refuses to slow down despite elevated prices.

US inflation stands at 3.8 per cent as measured by the PCE index, well above the Fed's 2 per cent target. The April nonfarm payrolls report showed 115,000 new jobs, stronger than expected. Markets are now pricing a 59 per cent probability of a rate hike by year-end, according to LSEG data. That is a sharp reversal from the rate-cut expectations that dominated just six months ago.

Friday's May payrolls report is expected to show jobs growth slowing to 96,000 with a 4.3 per cent unemployment rate. A number that beats those estimates could accelerate the timeline for a Fed hike — potentially as early as Warsh's first policy meeting in late June.

For NRI investors, a US rate hike means several things simultaneously. Dollar-denominated savings earn more, but the interest rate differential between the US and India narrows further (it is already at a decade low), increasing capital outflow pressure on the rupee. US bond yields rise, making equities relatively less attractive. And the cost of remitting dollars to India shifts subtly as exchange rates adjust.

## What Else to Watch

Monday opens with India's Manufacturing PMI for May and monthly auto sales data, both indicators of domestic demand strength. On Tuesday, US ISM manufacturing data will signal whether the factory sector is stabilising or deteriorating. Wednesday brings the ADP employment report, often seen as a preview of Friday's official jobs data.

Eurozone inflation data on Tuesday is also relevant. Analysts expect headline CPI to rise to 3.3 per cent from 3.0 per cent. If core inflation moves higher, the European Central Bank may hike rates in June as well, adding another front to the global tightening cycle. For NRI investors with European exposure, this is not background noise.

## How to Position

The base case is that the RBI holds and the Fed signals without acting. But the risk of a surprise on either side is higher than it has been in months. Indian banks and rate-sensitive stocks are particularly vulnerable to an unexpected RBI hike. Conversely, a weak US jobs report could trigger a relief rally in emerging-market currencies, including the rupee.

Diversification across currencies and asset classes remains the most sensible approach. But this is one of those weeks where the macro calendar is not just noise — it is the signal."""
}
articles.append(art3)


# ============================================================
# PUBLISH
# ============================================================

print("=" * 60)
print(f"Videshi Lifestyle-Health & Markets-Finance Writer")
print(f"Run: {datetime.now(timezone.utc).isoformat()}")
print("=" * 60)

results = []

for i, art in enumerate(articles):
    print(f"\n--- Article {i+1}/{len(articles)}: {art['category']} ---")
    print(f"  Headline: {art['headline'][:80]}...")
    
    # Validate headline length
    if len(art['headline']) > 200:
        print(f"  ⚠ Headline too long ({len(art['headline'])} chars), truncating")
        art['headline'] = art['headline'][:197] + "..."
    
    # Validate body length
    word_count = len(art['body'].split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ✗ REJECTED: Body too short ({word_count} words)")
        continue
    
    # Image sourcing
    print(f"  Sourcing image...")
    image_url = None
    image_attribution = None
    
    # Try Wikipedia for person articles
    if art.get('person_for_image'):
        image_url = fetch_wikipedia_person_image(art['person_for_image'])
        if image_url:
            image_attribution = "Wikimedia Commons"
    
    # Fallback to Pexels
    if not image_url:
        image_url = fetch_pexels_image(art['image_search'], art.get('image_fallback'))
        if image_url:
            image_attribution = "Pexels"
    
    # Validate and upload
    if image_url and validate_image_url(image_url):
        art_id = str(uuid.uuid4())
        filename = f"{art['slug'][:60]}.jpg"
        final_url = upload_image_to_supabase(image_url, filename)
        if final_url and validate_image_url(final_url):
            image_url = final_url
        elif not final_url:
            image_url = None
    else:
        image_url = None
    
    if not image_url:
        print(f"  ⚠ No valid image found — publishing without image")
    
    # Insert article
    article_data = {
        "headline": art['headline'],
        "subheadline": art['subheadline'],
        "slug": art['slug'],
        "body": art['body'],
        "category": art['category'],
        "vertical": art['category'],
        "tags": art.get('tags', []),
        "sources": art['sources'],
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    
    if image_url:
        article_data["image_url"] = image_url
    if image_attribution:
        article_data["image_attribution"] = image_attribution
    
    result = sb_insert("p2_articles", article_data)
    if result:
        art_id = result[0].get('id', 'unknown') if isinstance(result, list) else result.get('id', 'unknown')
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
        results.append({"slug": art['slug'], "id": art_id, "category": art['category']})
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")

print(f"\n{'=' * 60}")
print(f"DONE: {len(results)}/{len(articles)} articles published")
for r in results:
    print(f"  [{r['category']}] {r['slug']}")
print(f"{'=' * 60}")
