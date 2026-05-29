#!/usr/bin/env python3
"""
The Videshi — Lifestyle-Health & Markets-Finance Writer
Scheduled run: 2026-05-29
Produces 2 lifestyle-health articles + 1 markets-finance article
"""

import json, os, sys, uuid, re, time
import requests
from datetime import datetime, timezone

# Load environment
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = person_name.replace(' ', '_')
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
    """Fetch a relevant image from Pexels using curl. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    
    import subprocess, urllib.parse
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            encoded_q = urllib.parse.quote_plus(q)
            url = f"https://api.pexels.com/v1/search?query={encoded_q}&per_page=5&orientation=landscape"
            result = subprocess.run(
                ['curl', '-sS', url, '-H', f'Authorization: {PEXELS_KEY}'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                img_url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if img_url:
                    print(f"  ✓ Pexels image found for '{q}': {img_url[:80]}...")
                    return img_url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns HTTP 200 with proper content type and size."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {ct}, {cl} bytes")
            return True
        # Try GET for servers that don't support HEAD well
        r = requests.get(url, timeout=10, stream=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct:
            # Read a chunk to verify
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {ct}, {len(chunk)}+ bytes")
                return True
    except Exception as e:
        print(f"  ⚠ Image validation failed: {e}")
    return False

def upload_to_supabase_storage(image_url, filename):
    """Download an image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=15,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed: status={r.status_code}, size={len(r.content)}")
            return None
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            content_type = 'image/jpeg'
        
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }
        
        resp = requests.post(upload_url, data=r.content, headers=upload_headers, timeout=15)
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None

def publish_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Published: {data[0].get('id', 'unknown')}")
            return data[0].get('id')
        print(f"  ✓ Published (raw response)")
        return True
    else:
        print(f"  ✗ Publish failed: {r.status_code} — {r.text[:300]}")
        return None

def patch_article(article_id, updates):
    """Patch an existing article."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=HEADERS,
        json=updates
    )
    if r.status_code in (200, 204):
        print(f"  ✓ Patched article {article_id}")
        return True
    else:
        print(f"  ⚠ Patch failed: {r.status_code}")
        return False


# ============================================================
# ARTICLE 1: Yoga for Cancer Survivors (lifestyle-health)
# ============================================================
def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Yoga for Cancer Survivors (lifestyle-health)")
    print("="*60)
    
    slug = "yoga-cancer-survivors-asco-2026-yocas-insomnia-fatigue-indian-wellness"
    headline = "A Trial of 410 Cancer Survivors Found That Four Weeks of Gentle Yoga Reduced Insomnia, Fatigue, and Anxiety. No Medication Required."
    subheadline = "The YOCAS programme, presented at ASCO 2026, is built on hatha and restorative yoga — practices that Indian families have known for generations. Western oncology is finally catching up."
    
    body = """India gave the world yoga roughly five thousand years ago. For most of that time, Western medicine treated it as a curiosity — spiritual, perhaps, but not clinical. That changed on Thursday, when researchers presented the results of a major randomised trial at the American Society of Clinical Oncology's 2026 annual meeting. The data showed that a structured four-week yoga programme significantly reduced insomnia, fatigue, anxiety, and mood disturbance among cancer survivors. The effect sizes were moderate to large, and no pills were involved.

## The Trial

The study, led by Yuri Choi, PhD, RN, of the Wilmot Cancer Institute at the University of Rochester, evaluated a programme called YOCAS — Yoga for Cancer Survivors. It enrolled 410 survivors of non-metastatic cancer who were two to twenty-four months past treatment and had at least moderate sleep disruption. Their mean age was 54 years, and 75 per cent were breast cancer survivors.

Participants were randomly assigned to standard survivorship care alone or standard care plus YOCAS. Those in the yoga arm attended two 75-minute instructor-led sessions per week — gentle hatha poses, restorative poses done lying down with support cushions, breathing exercises, and mindfulness practices. They were also encouraged to practise at home for at least 30 minutes a week.

## What They Found

Compared with standard care alone, participants in the YOCAS group reported a 5.08-point lower score on the Profile of Mood States questionnaire — a moderate-to-large effect. Their anxiety scores dropped by 0.72 points (a small-to-medium effect), and fatigue dropped by 1.49 points (a medium-to-large effect).

The improvements in mood and fatigue appeared to drive better sleep: each accounted for roughly 25 per cent of the improvement in participants' insomnia ratings. In other words, yoga was not just a sleep aid. It was working on the full cluster of survivorship symptoms simultaneously.

"Clinicians should consider recommending gentle hatha and restorative yoga for survivors experiencing these side effects," Choi said at the ASCO press briefing.

## Why This Matters for the Diaspora

Up to 95 per cent of cancer survivors experience sleep disturbances during or after treatment. More than half report mood disturbances, anxiety, or fatigue. The standard response in American medicine has been to add medications — sleep aids, anti-anxiety drugs, antidepressants — to a patient already managing a complicated drug regimen.

Fumiko Chino, MD, an ASCO expert in survivorship care, noted that many survivors are already taking multiple medications. Yoga, she said, offers a non-drug option for "reducing four different side effects at once."

For Indian-Americans, the irony is hard to miss. Yoga — pranayama, asanas, dhyana — has been a part of the cultural inheritance for millennia. Yet it often takes a randomised controlled trial at a Western oncology conference for it to be taken seriously in an American hospital.

South Asians in the United States have elevated risks for several cancers, including breast, liver, and thyroid. The number of cancer survivors in the US is projected to reach 22 million by 2035. As that number grows, so does the need for non-pharmaceutical interventions that work.

## What Comes Next

ASCO guidelines already support gentle yoga as an option for managing fatigue in cancer survivors. This trial strengthens the evidence base considerably. The next phase of the YOCAS programme will focus on adapting the intervention for young cancer survivors and developing digital delivery platforms, including an online version and a mobile app.

Julie Gralow, MD, a breast medical oncologist at the University of Washington who moderated the ASCO briefing, put it plainly: "Gentle, evidence-based practices, such as the restorative or therapeutic yoga studied here, are safe and highly effective tools for managing symptoms like fatigue, anxiety, and sleep disturbances during and after treatment."

Your grandmother did not need a clinical trial to know that yoga helps you sleep. But the clinical trial helps ensure your oncologist recommends it."""
    
    # Image sourcing: Pexels for yoga/meditation (not a specific person article)
    print("  Sourcing image...")
    img_url = fetch_pexels_image("gentle yoga meditation health wellness", "yoga class breathing exercises")
    img_attribution = "The Videshi"
    
    final_image_url = None
    if img_url:
        filename = f"{slug}.jpg"
        final_image_url = upload_to_supabase_storage(img_url, filename)
    
    word_count = len(body.split())
    print(f"  Word count: {word_count}")
    assert word_count >= 600, f"Body too short: {word_count} words"
    assert len(headline) <= 200, f"Headline too long: {len(headline)} chars"
    assert len(subheadline) >= 15, f"Subheadline too short"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "lifestyle-health",
        "vertical": "lifestyle-health",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "Medscape — Yoga Eases Insomnia, Fatigue, Anxiety in Cancer Survivors (ASCO 2026)",
            "American Society of Clinical Oncology (ASCO) 2026 Annual Meeting",
            "American Cancer Society — cancer survivor projections"
        ]),
        "image_url": final_image_url,
        "image_attribution": img_attribution if final_image_url else None,
        "image_caption": "A gentle yoga session — the kind of hatha and restorative practice now shown to significantly reduce insomnia and fatigue in cancer survivors."
    }
    
    art_id = publish_article(article)
    return art_id


# ============================================================
# ARTICLE 2: Wildfire Smoke and Brain Health (lifestyle-health)
# ============================================================
def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Wildfire Smoke and Brain Health (lifestyle-health)")
    print("="*60)
    
    slug = "wildfire-smoke-brain-health-dementia-risk-indian-american-california-2026"
    headline = "Wildfire Smoke Does Not Just Burn Your Lungs. A Growing Body of Research Says It Is Rewiring Your Brain."
    subheadline = "Dementia risk, cognitive decline, and mental illness in children — the neuroscience of wildfire smoke is catching up to what California residents already sense. Indian-Americans in the Bay Area and LA are disproportionately exposed."
    
    body = """Every summer, the haze returns. Across California's Bay Area and Los Angeles Basin — home to roughly 700,000 Indian-Americans — wildfire smoke has become an annual fixture. Most people know it is bad for their lungs. Fewer realise it may be changing their brains.

## The Evidence Is Accumulating Fast

A study published in the journal *Environmental Health Perspectives* found that long-term exposure to fine particulate matter from wildfire smoke is associated with a tenfold increase in dementia diagnoses. A separate analysis found that each 1 microgram-per-cubic-metre increase in PM2.5 from wildfire smoke was linked to an 18 per cent rise in dementia cases.

These are not marginal numbers. And the mechanism is disturbingly plausible. PM2.5 — particulate matter smaller than 2.5 micrometres — is small enough to cross the blood-brain barrier. Once inside the brain, these particles trigger neuroinflammation, oxidative stress, and the accumulation of amyloid and tau proteins, the hallmarks of Alzheimer's disease.

A study at the University of California, Davis, exposed mice to wildfire smoke and found that 30 per cent of hippocampal proteins — the region critical for memory — were altered. Older animals were hit hardest, and the changes mirrored early markers of neurodegenerative disease.

## It Is Not Just the Elderly

Research from the University of Colorado Boulder tracked 10,000 children aged nine to eleven and found that each additional day of wildfire smoke exposure increased the risk of depression and anxiety symptoms — with effects persisting up to a year after exposure. The study controlled for other pollutants and socioeconomic factors. The wildfire smoke effect held.

For Indian-American families raising children in California — the state that accounts for roughly a third of all US wildfire acreage burned annually — this is not an abstract concern. Wildfire season increasingly overlaps with the school year. Children are outside during recess, at soccer practice, walking to school. The smoke they breathe today may shape their mental health for years.

## Air Pollution and Cognition in Midlife

A study published in the journal *Stroke* examined the link between air pollution and cognitive function in midlife adults. It found that each 5 parts-per-billion increase in nitrogen dioxide — a common air pollutant that spikes during wildfire events — was associated with reduced cognitive performance and 8 per cent higher odds of covert vascular brain injury detected by MRI.

The researchers examined multiple confounders — diabetes, hypertension, central obesity — and found that none of them explained away the association. Air pollution appeared to damage the brain independently of the conditions we already know are bad for it.

## The Diaspora Dimension

Indian-Americans are concentrated in exactly the metros most affected. The Bay Area — San Jose, Sunnyvale, Fremont, Cupertino — regularly records hazardous air quality during fire season. Los Angeles and its eastern suburbs are no better. Houston and the Texas Gulf Coast face a different pollution profile but similar particulate risks.

The cultural pattern compounds the exposure. Extended family visits to India during winter coincide with Delhi's notorious pollution season, where PM2.5 levels routinely exceed WHO guidelines by ten to twenty times. A Bay Area Indian-American who visits Delhi in December and returns to California in August is facing a double exposure window that few other demographic groups experience.

Meanwhile, indoor air quality assumptions are often wrong. Many Indian-American households cook with high-heat methods — tadka, deep frying, tandoor-style grilling — that generate significant indoor particulate matter. When wildfire smoke pushes outdoor air quality into the red zone and families seal their homes, indoor cooking emissions have nowhere to go.

## What You Can Do

The practical advice is straightforward, even if imperfect. HEPA air purifiers rated for the square footage of your home are the single most effective intervention. N95 or KN95 masks work outdoors — cloth masks do not filter PM2.5. Air quality apps like PurpleAir and AirNow provide hyperlocal readings that are more accurate than citywide averages.

For children, limit outdoor activity when AQI exceeds 100. For elderly family members — particularly those with existing cognitive concerns — the threshold should be lower. The Alzheimer's Association now explicitly recommends limiting outdoor time during smoke events and using high-efficiency air filters indoors.

The harder truth is structural. Indian-Americans in California are not going to relocate en masse. But they can advocate — for better air filtration in schools, for workplace air quality standards that account for wildfire smoke, and for health screening protocols that take cumulative pollution exposure seriously.

The smoke is not going away. Understanding what it does to the brain is the first step toward protecting it."""
    
    # Image sourcing
    print("  Sourcing image...")
    img_url = fetch_pexels_image("wildfire smoke haze city skyline", "air pollution smog urban")
    img_attribution = "The Videshi"
    
    final_image_url = None
    if img_url:
        filename = f"{slug}.jpg"
        final_image_url = upload_to_supabase_storage(img_url, filename)
    
    word_count = len(body.split())
    print(f"  Word count: {word_count}")
    assert word_count >= 600, f"Body too short: {word_count} words"
    assert len(headline) <= 200, f"Headline too long: {len(headline)} chars"
    assert len(subheadline) >= 15, f"Subheadline too short"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "lifestyle-health",
        "vertical": "lifestyle-health",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "Environmental Health Perspectives — wildfire PM2.5 and dementia risk study",
            "University of Colorado Boulder — wildfire smoke exposure and youth mental health (10,000 children study)",
            "University of California Davis — hippocampal protein changes in wildfire-exposed mice",
            "Stroke journal — air pollution, cognitive function, and covert vascular brain injury",
            "Alzheimer's Association — wildfire smoke advisory guidelines"
        ]),
        "image_url": final_image_url,
        "image_attribution": img_attribution if final_image_url else None,
        "image_caption": "Wildfire smoke over a city skyline — fine particulate matter from these events can cross the blood-brain barrier and trigger neuroinflammation."
    }
    
    art_id = publish_article(article)
    return art_id


# ============================================================
# ARTICLE 3: Wipro AI + Markets Reopen (markets-finance)
# ============================================================
def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: Wipro-ServiceNow AI Deal + Markets Reopen (markets-finance)")
    print("="*60)
    
    slug = "wipro-servicenow-agentic-ai-partnership-nifty-markets-reopen-bakrid-20260529"
    headline = "Wipro's ADR Surged 18 Per Cent Overnight on an AI Deal With ServiceNow. Indian Markets Just Reopened. Here Is What NRI Investors Need to Know."
    subheadline = "The Nifty IT index jumped 2.3 per cent at open. Brent crude fell to $93 on Iran ceasefire hopes. And the biggest question facing Indian IT — whether AI destroys the outsourcing model or reinvents it — just got a data point."
    
    body = """Indian stock markets reopened on Friday after the Bakrid holiday to a wall of news. The benchmark Nifty 50 rose 0.21 per cent to 23,956.65 and the BSE Sensex added 0.31 per cent to 76,106.80 in early trade. But the real story was in IT.

## The Wipro-ServiceNow Deal

On Thursday, while Indian markets were closed, Wipro announced an expanded partnership with ServiceNow — the US-based enterprise software company — to deploy agentic AI workflows across IT, HR, procurement, and cybersecurity functions. The market response was immediate and extreme. Wipro's American Depositary Receipts on the New York Stock Exchange surged 18.54 per cent in a single session.

When Mumbai opened on Friday morning, Wipro's domestic shares jumped 4.35 per cent, leading the Nifty IT index to a 2.3 per cent gain. Eleven of the sixteen major sectors on the Nifty logged gains, but IT was the clear leader.

The partnership integrates Wipro Intelligence — the company's proprietary AI platform — with ServiceNow's AI infrastructure. The tools include SmartProcure for procurement automation, Cyber Transform for security operations, and a suite of agentic AI agents designed to handle tasks autonomously, without human intervention at every step.

## Why 'Agentic AI' Matters for Indian IT

The Indian IT services industry — TCS, Infosys, Wipro, HCL Tech — has spent the past two years under an existential question: does artificial intelligence eliminate the need for the armies of engineers that Indian outsourcers have built their businesses around?

The bear case is straightforward. If AI agents can write code, manage tickets, and automate HR processes, then the labour-arbitrage model that Indian IT was built on starts to erode. The industry's margins have historically depended on deploying large teams at lower cost.

The Wipro-ServiceNow deal offers a counter-narrative. Instead of AI replacing Indian IT, the partnership positions Wipro as the integrator — the company that helps enterprises adopt agentic AI at scale. The revenue model shifts from headcount to platform fees, implementation contracts, and managed AI services. Whether this transition works at scale remains an open question, but the market priced Thursday's announcement as a proof point.

For NRI investors holding Indian IT stocks — or US-listed ADRs — this is the pivot to watch. The companies that successfully move from body-shopping to AI-platform partnerships will outperform. The ones that do not will face margin compression.

## The Iran Ceasefire and Oil

The broader market mood was shaped by geopolitics. On Thursday, sources told Reuters that the US and Iran had reached an agreement to extend their ceasefire and lift restrictions on shipping through the Strait of Hormuz. President Trump has not yet approved the deal, and Iranian state media said it had not been finalised. But the signal alone moved markets.

Brent crude futures fell to $93 per barrel — a meaningful drop for India, which imports more than 85 per cent of its oil. Every dollar down on Brent eases pressure on the current account deficit, the rupee, and inflation expectations. The Reserve Bank of India, which meets on June 5, will be watching closely. Bond traders are already pricing in multiple rate moves this year.

Asian markets jumped 1.6 per cent on the combined optimism of the Iran deal and a global AI rally. The S&P 500 and Nasdaq posted record closing highs on Thursday.

## The Rupee and Capital Flows

The Indian rupee found marginal breathing room on the ceasefire reports, but traders remained cautious. Multiple prior reports of US-Iran progress have led to nothing, and the recent pattern of foreign portfolio investors pulling money out of India has not reversed. FPIs have withdrawn roughly $23 billion from Indian equities in the current cycle.

The government's plan to boost capital inflows — floated this week but light on specifics — added a layer of policy uncertainty. For NRI investors, the question is whether the FPI outflow creates a buying opportunity or signals deeper structural concerns about Indian valuations relative to other emerging markets.

## What NRI Investors Should Watch

**Short term**: The RBI meeting on June 5 is the next major domestic catalyst. If the Iran ceasefire holds and oil stays below $95, the central bank has more room to manoeuvre. If the deal collapses, expect Brent back above $100 and renewed pressure on the rupee and rate expectations.

**Medium term**: Indian IT earnings season in July will reveal whether the agentic AI pivot is generating real revenue or just headlines. Watch Wipro's order book commentary closely — the ServiceNow deal needs to show pipeline growth, not just a press release.

**Portfolio positioning**: The domestic mutual fund industry continues to absorb FPI outflows — Indian SIP inflows hit record highs in April. For NRIs investing through mutual funds or direct equity, the large-cap IT names that are credibly positioning for AI integration (Wipro, Infosys, HCL Tech) deserve a closer look relative to the laggards.

The day India's markets were closed for a holiday, the most important trade of the week happened in New York. That is the new normal for Indian IT — and for the NRI portfolios that hold it."""
    
    # Image sourcing: Wikipedia for Wipro (corporate)
    print("  Sourcing image...")
    img_url = fetch_pexels_image("stock market trading India technology", "stock exchange digital screen AI")
    img_attribution = "The Videshi"
    
    final_image_url = None
    if img_url:
        filename = f"{slug}.jpg"
        final_image_url = upload_to_supabase_storage(img_url, filename)
    
    word_count = len(body.split())
    print(f"  Word count: {word_count}")
    assert word_count >= 600, f"Body too short: {word_count} words"
    assert len(headline) <= 200, f"Headline too long: {len(headline)} chars"
    assert len(subheadline) >= 15, f"Subheadline too short"
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "markets-finance",
        "vertical": "markets-finance",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "Reuters — Indian shares open higher as IT gains after Wipro's AI partnership with ServiceNow (May 29, 2026)",
            "Reuters — Wall Street ends higher, Brent crude eases on reports of US-Iran truce extension",
            "LiveMint — Wipro ADR jumps over 18% on NYSE after AI partnership with ServiceNow",
            "Reuters — Rupee likely to contend with outflows even as US-Iran ceasefire reports give oil relief"
        ]),
        "image_url": final_image_url,
        "image_attribution": img_attribution if final_image_url else None,
        "image_caption": "Indian markets reopened after the Bakrid holiday to a wall of AI-driven optimism — Wipro led the IT index with a 4.35 per cent jump."
    }
    
    art_id = publish_article(article)
    return art_id


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("="*60)
    print("The Videshi — Lifestyle & Markets Writer")
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}")
    print("="*60)
    
    results = []
    
    try:
        r1 = write_article_1()
        results.append(('yoga-cancer-survivors', r1))
    except Exception as e:
        print(f"  ✗ Article 1 failed: {e}")
        results.append(('yoga-cancer-survivors', None))
    
    try:
        r2 = write_article_2()
        results.append(('wildfire-smoke-brain', r2))
    except Exception as e:
        print(f"  ✗ Article 2 failed: {e}")
        results.append(('wildfire-smoke-brain', None))
    
    try:
        r3 = write_article_3()
        results.append(('wipro-servicenow-markets', r3))
    except Exception as e:
        print(f"  ✗ Article 3 failed: {e}")
        results.append(('wipro-servicenow-markets', None))
    
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    published = 0
    for name, result in results:
        status = "✓ PUBLISHED" if result else "✗ FAILED"
        print(f"  {status}: {name}")
        if result:
            published += 1
    
    print(f"\n  Total: {published}/{len(results)} articles published")
    
    if published == 0:
        sys.exit(1)
