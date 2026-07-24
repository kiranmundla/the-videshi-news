#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-26 22:00 UTC batch.
Topics (checked against ~30 recent articles to avoid dupes):
  1. Exercise — not the weight-loss drug alone — drove vascular gains after major
     weight loss. Nature Metabolism, prespecified secondary analysis of the S-LiTE
     trial (Sandsdal et al., 2026; DOI 10.1038/s42255-026-01554-4). 130 per-protocol
     adults with obesity (no diabetes) who had lost ~13.7 kg (~12.7%) on an 8-wk LCD,
     then randomized to placebo / exercise+placebo / liraglutide 3.0mg / exercise+
     liraglutide for 52 wks. Exercise (alone or w/ drug) cut carotid intima-media
     thickness (cIMT -7% / -6%), IL-6 (-26% / -22%), IFN-gamma (-45% exercise-only),
     and adhesion molecules; liraglutide ALONE showed no significant vascular/
     inflammatory benefit. — lifestyle-health
     (DISTINCT: prior pieces covered weight-regain/maintenance exercise generally,
      and an oral GLP-1 pill trial; NONE cover the GLP-1-vs-exercise *vascular/
      arterial-health* contrast. New angle in the GLP-1 era.)
  2. Glucosamine — the joint-pain supplement ~40M Americans take — linked to faster
     dementia progression and higher death risk in those with established disease.
     Nature Metabolism (Sun lab, Univ. of Florida; Gentry, Guo, Bian), published
     June 9 2026. AI-mined deidentified UF Health records 2012-2024: ~24,000 ADRD
     and ~42,000 MCI patients, ~8% glucosamine users. 25% higher likelihood of
     MCI-to-dementia progression over 5 yrs (P<.001); 25% higher mortality at 10 yrs
     in ADRD patients (P=.0023); no effect in MCI-only. Mechanism = hyperglycosylation
     (glucosamine crosses blood-brain barrier; sugar-tagging of brain proteins).
     Observational — association, not causation. — lifestyle-health
     (DISTINCT: no recent supplement/dementia piece; prior brain pieces were sleep/
      gene, sleep habits, anti-inflammatory diet, air pollution — none on supplements.)
  3. Amazon's fresh $13bn India pledge — Jassy meets Modi, total India outlay to
     $48bn (2026-30); >$21bn now earmarked for AI + cloud, expanding AWS data-centre
     capacity in Mumbai & Hyderabad. Builds on Dec-2025 $35bn pledge; cumulative
     2010-30 >$88bn. Targets 3.8M jobs, $80bn cumulative ecommerce exports, AI for
     15M small businesses, AI education for 4M govt-school students. Part of a
     hyperscaler wave: Google $15bn (Oct), Microsoft $17.5bn (Dec); India's data-
     centre tax breaks. — markets-finance
     (DISTINCT: prior finance pieces were monsoon macro-risk, NSE IPO, IRFC OFS,
      rupee/FCNR-B, gold, SIP flows, GIFT City, Meta-CRED, US-India trade — NONE
      cover the hyperscaler/AI-capex India build-out.)
"""

import json, os, io, subprocess, urllib.parse, re
from datetime import datetime, timezone
import requests

# ---- env ----
for env_file in ("~/.env.supabase", "~/workspace/.env.supabase", "~/workspace/.env.pexels"):
    p = os.path.expanduser(env_file)
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY") or os.environ.get("PEXELS_KEY", "")
UA = "TheVideshi/1.0 (thevideshi.com)"

try:
    from PIL import Image
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

# ---------------- image helpers ----------------
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=12)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:70]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for _, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 600:
                    continue
                title = page.get("title", "").lower()
                if any(b in title for b in ("flag_of", "coat_of_arms", "emblem", "_map", "location_", "logo", "seal_of")):
                    continue
                results.append({"url": ii.get("thumburl") or ii.get("url", ""),
                                "title": page.get("title", ""), "width": ii.get("width", 0)})
            if results:
                print(f"  \u2713 Commons: {len(results)} imgs for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Commons error '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"
        out = subprocess.run(["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}", url],
                             capture_output=True, text=True, timeout=30)
        data = json.loads(out.stdout)
        photos = data.get("photos", [])
        if photos:
            src = photos[0]["src"]
            chosen = src.get("large2x") or src.get("large") or src.get("original")
            print(f"  \u2713 Pexels img for '{query}'")
            return chosen
    except Exception as e:
        print(f"  \u26a0 Pexels error '{query}': {e}")
    return None

def download_bytes(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
    except Exception:
        pass
    try:
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl2200.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl2200.bin"):
            with open("/tmp/_img_dl2200.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl2200.bin")
            if len(data) > 5000:
                return data
    except Exception as e:
        print(f"  \u26a0 download error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    if not HAVE_PIL:
        return img_bytes
    try:
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue()
    except Exception as e:
        print(f"  \u26a0 compress error: {e}")
        return img_bytes

def upload_to_supabase(img_bytes, filename):
    try:
        url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
                   "Content-Type": "image/jpeg", "x-upsert": "true"}
        r = requests.post(url, headers=headers, data=img_bytes, timeout=60)
        if r.status_code in (200, 201):
            public = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded {filename} ({len(img_bytes)//1024} KB)")
            return public
        else:
            print(f"  \u2717 Upload failed {filename}: {r.status_code} {r.text[:150]}")
    except Exception as e:
        print(f"  \u26a0 upload error: {e}")
    return None

def source_image(slug, commons_queries, pexels_queries, person=None):
    candidates = []
    if person:
        wiki = fetch_wikipedia_person_image(person)
        if wiki:
            candidates.append((wiki, "Wikimedia Commons"))
        for r in fetch_wikimedia_commons_images(person)[:3]:
            candidates.append((r["url"], "Wikimedia Commons"))
    for q in commons_queries:
        for r in fetch_wikimedia_commons_images(q)[:3]:
            candidates.append((r["url"], "Wikimedia Commons"))
        if candidates:
            break
    for q in pexels_queries:
        px = fetch_pexels_image(q)
        if px:
            candidates.append((px, "Pexels"))
            break
    for url, attribution in candidates:
        raw = download_bytes(url)
        if not raw:
            continue
        comp = compress_image(raw)
        if len(comp) < 10000:
            continue
        final = upload_to_supabase(comp, f"{slug}.jpg")
        if final:
            return final, attribution
    print(f"  \u26a0 No image sourced for {slug}")
    return None, None

# ---------------- DB insert ----------------
def insert_article(article):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
               "Content-Type": "application/json", "Prefer": "return=representation"}
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=headers,
                         json=article, timeout=30)
    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"  \u2713 Inserted: {article['slug']} (id: {data[0]['id'] if data else 'ok'})")
        return True
    print(f"  \u2717 FAILED: {article['slug']} \u2014 {resp.status_code}: {resp.text[:300]}")
    return False

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
articles = []

# ============================================================
# ARTICLE 1: Exercise vs GLP-1 alone for vascular health (lifestyle-health)
# ============================================================
articles.append({
    "headline": "After Major Weight Loss, the Drug Wasn\u2019t Enough \u2014 It Was Exercise That Healed the Arteries",
    "subheadline": "In a year-long trial of adults who had already shed a tenth of their body weight, regular exercise measurably thinned artery walls and cooled inflammation \u2014 while the popular weight-loss drug liraglutide, taken on its own, did neither.",
    "slug": "exercise-not-glp1-liraglutide-alone-vascular-health-s-lite-trial-nature-metabolism-carotid-inflammation-diaspora-20260626-2200",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "GLP-1 weight-loss drugs are spreading fast through affluent diaspora circles as a shortcut around a stubborn metabolic burden \u2014 South Asians face heart disease earlier and at lower body weights than almost any group \u2014 yet this trial warns that the needle and the scale are not the whole story: the arterial and inflammatory protection NRIs most need came from movement, not the medication, a crucial caveat for a community quick to adopt the drugs but slow to keep up the exercise.",
    "sources": json.dumps([
        {"name": "News-Medical \u2014 \u2018Exercise, not liraglutide alone, drives vascular gains after obesity-related weight loss\u2019", "url": "https://www.news-medical.net/news/20260625/Exercise-not-liraglutide-alone-drives-vascular-gains-after-obesity-related-weight-loss.aspx"},
        {"name": "Sandsdal, R. M., et al. (2026), \u2018Effects of exercise and liraglutide on vascular health and inflammation during weight loss maintenance: a prespecified secondary analysis of the S-LiTE trial\u2019, Nature Metabolism", "url": "https://www.nature.com/articles/s42255-026-01554-4"}
    ]),
    "body": """In the age of Ozempic and its cousins, it has become easy to imagine that a once-weekly injection can do the work that diet and exercise once demanded. A new analysis of a year-long trial complicates that hope in a specific and important way. After people with obesity had already lost a substantial amount of weight, it was exercise \u2014 not the weight-loss drug taken alone \u2014 that improved the health of their arteries and quieted the inflammation that drives heart disease.

## A Closer Look at What Survives Weight Loss

The findings come from a prespecified secondary analysis of the S-LiTE trial, published in the journal *Nature Metabolism*. The original trial enrolled adults with obesity but without diabetes, who first lost an average of 13.7 kilograms \u2014 roughly 12.7 percent of their body weight \u2014 on an eight-week low-calorie diet. The 130 participants in this analysis were then randomly assigned, for a full year, to one of four groups: a placebo, supervised exercise plus placebo, the GLP-1 drug liraglutide (3.0 mg daily) on its own, or exercise combined with liraglutide.

The question was not whether the interventions kept weight off, but something subtler: what happens inside the blood vessels during the long, difficult phase of keeping weight off. Researchers tracked the thickness of the participants' carotid artery walls using high-resolution ultrasound, alongside a panel of inflammatory and endothelial biomarkers \u2014 the molecular signals of how healthy the lining of the blood vessels is.

## Movement Did What Medication Alone Did Not

The pattern was striking. Compared with placebo, the exercise groups saw the thickness of their carotid artery walls fall by 6 to 7 percent \u2014 a change the authors note sits within a range linked, in other studies, to lower cardiovascular risk. Markers of inflammation followed suit: interleukin-6, a key inflammatory signal, dropped by 26 percent in the exercise-plus-placebo group and 22 percent in the exercise-plus-drug group, while interferon-gamma fell by 45 percent in those who exercised without the drug. The combination of exercise and liraglutide also significantly reduced two adhesion molecules that mark a damaged vessel lining.

Liraglutide on its own, by contrast, produced no statistically significant improvement in any of these vascular or inflammatory measures. The drug is highly effective at promoting and maintaining weight loss \u2014 that is not in dispute. But in this trial, its metabolic benefits did not translate into the arterial and anti-inflammatory gains that exercise delivered.

The researchers were careful about the limits of their work. This was a secondary analysis, not the trial's main endpoint. Carotid wall thickness is a surrogate marker, a proxy for cardiovascular risk rather than a count of heart attacks avoided. The exercise was partly supervised, which may flatter results compared with what people manage on their own, and the statistics were not adjusted for multiple comparisons. The takeaway is therefore a signal, not a verdict: during weight-loss maintenance, the body's blood vessels appear more responsive to the physical act of exercise than to the drug's metabolic effects alone.

## Why It Matters for the Diaspora

For the Indian diaspora, the message lands on a fault line. South Asians develop cardiovascular disease earlier and at lower body weights than most populations, a vulnerability written into how their bodies store fat and handle insulin. As GLP-1 drugs have moved from clinics into dinner-table conversation across affluent NRI circles, many have understandably seized on them as a clean shortcut around a problem that has stalked their families for generations.

This study is a reminder that the shortcut has a blind spot. The drugs can shrink the number on the scale, but the protection that matters most for South Asian hearts \u2014 thinner artery walls, lower inflammation, a healthier vessel lining \u2014 came, in this trial, from exercise. The practical implication is not to abandon the medication, which has real and proven uses, but to refuse to treat it as a substitute for movement. For a community carrying an outsized cardiovascular burden and increasingly drawn to pharmaceutical fixes, the most defensible course is the unglamorous combination: use the tools that help, but keep walking, keep lifting, keep moving. The needle may change the weight; the workout, this research suggests, is what still changes the arteries."""
})

# ============================================================
# ARTICLE 2: Glucosamine linked to faster dementia + death (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Joint-Pain Supplement Millions Take Daily Is Now Linked to Faster Dementia and Higher Death Risk",
    "subheadline": "A large analysis of health records found that people with cognitive decline who took glucosamine were 25 percent more likely to progress to dementia \u2014 and those who already had it faced a 25 percent higher risk of dying \u2014 raising a clinical question researchers say now deserves far more attention.",
    "slug": "glucosamine-joint-supplement-faster-dementia-progression-higher-death-risk-nature-metabolism-university-florida-hyperglycosylation-diaspora-20260626-2200",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Glucosamine is a fixture in the daily supplement routines of aging Indians at home and abroad \u2014 taken on faith for creaky knees and passed between relatives like sound advice \u2014 even as South Asians carry a heavy, often early-onset dementia burden; this finding gives NRI families a concrete, time-sensitive reason to revisit what their parents are swallowing every morning, and to raise it with a doctor rather than the family WhatsApp group.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 \u2018Glucosamine used for joint pain linked to dementia progression\u2019", "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/glucosamine-used-joint-pain-linked-dementia-progression-2026-06-11/"},
        {"name": "Drugs.com / HealthDay \u2014 \u2018Popular Joint Pain Supplement, Glucosamine, Might Increase Alzheimer\u2019s Risk, Study Says\u2019", "url": "https://www.drugs.com/news/popular-joint-pain-supplement-glucosamine-might-increase-alzheimer-s-risk-study-says.html"},
        {"name": "Nature Metabolism \u2014 \u2018Hyperglycosylation is a metabolic driver of Alzheimer\u2019s disease\u2019 (Univ. of Florida; Sun, Gentry, Guo, Bian)", "url": "https://www.nature.com/articles/s42255-026-01549-1"}
    ]),
    "body": """It is one of the most widely taken supplements in the world, swallowed each morning by tens of millions of people hoping to ease the ache of stiff joints. Now a large new study suggests that glucosamine, long treated as harmlessly helpful, may carry a hidden cost for the aging brain \u2014 accelerating the slide toward dementia in those already at risk, and raising the risk of death in those who have it.

## What the Records Showed

The research, published in the journal *Nature Metabolism*, came out of the University of Florida, where scientists used artificial intelligence to comb through deidentified health records collected between 2012 and 2024. They identified more than 24,000 patients with Alzheimer's disease and related dementias, and nearly 42,000 with mild cognitive impairment \u2014 the often-reversible early stage that sometimes, but not always, progresses to dementia. About 8 percent of patients in both groups were recorded as glucosamine users.

After adjusting for age, sex and demographic factors, the pattern was consistent and unsettling. People with mild cognitive impairment who took glucosamine were 25 percent more likely to progress to full dementia over five years. And among those who already had dementia, glucosamine use was tied to a 25 percent higher risk of death over the study's span. Notably, there was no such mortality effect in the milder group, suggesting the supplement's danger may be concentrated in people whose brains are already under siege \u2014 not the general aging population.

## A Question of Sugar in the Brain

Why would a joint supplement touch the brain at all? Glucosamine is a sugar-related molecule, and crucially, it can cross the blood-brain barrier \u2014 the protective wall that keeps most substances out of brain tissue. Once inside, the researchers propose, it may feed a damaging process called hyperglycosylation, in which sugar molecules attach abnormally to proteins in the brain, disrupting their ability to fold and function. In animal experiments, mice with Alzheimer's-like symptoms given glucosamine developed worse memory, while blocking the enzyme that produces such sugars actually improved their symptoms \u2014 hinting that this metabolic pathway could itself become a treatment target.

The scientists were emphatic about what the study does not prove. It is observational, built from medical records rather than a controlled trial, so it cannot establish that glucosamine causes the worse outcomes rather than merely traveling alongside other factors. People who take supplements may differ in countless ways from those who do not. "While it's an association and not proof of causality, it does raise an important clinical question that now deserves much more attention," said Matt Gentry, chair of biochemistry and molecular biology at the University of Florida and a co-author. A commentary published alongside the study struck a more hopeful note, suggesting the sugar-tagging pathway "is a targetable pathway for combating this disease."

## Why It Matters for the Diaspora

For the Indian diaspora, the finding cuts uncomfortably close to a familiar ritual. Glucosamine is a staple of the daily pill organizers of aging Indians, in Bengaluru and in New Jersey alike \u2014 recommended for sore knees, bought without a prescription, and shared as trusted advice across the generations. It sits beside the turmeric and the multivitamins as something assumed to be, at worst, useless and at best gently beneficial.

That assumption now warrants a second look, particularly because South Asians carry a disproportionate and often earlier-onset burden of dementia. For the many NRI households in the sandwich generation \u2014 caring for elderly parents while raising children \u2014 the practical takeaway is not panic but a conversation. If an aging relative with memory concerns or early cognitive decline is taking glucosamine, this is a question for their doctor, not a verdict to act on alone. The supplement aisle has long enjoyed a halo of safety simply because its products are sold without a prescription. This study is a reminder that "natural" and "over-the-counter" are not the same as "proven harmless" \u2014 and that for a community that prizes both its elders and its home remedies, the safest path runs through a physician, not the family group chat."""
})

# ============================================================
# ARTICLE 3: Amazon's $13bn India AI/cloud pledge (markets-finance)
# ============================================================
articles.append({
    "headline": "Amazon Pledges Another $13 Billion to India, Betting the Country Becomes a Global AI Hub",
    "subheadline": "Andy Jassy\u2019s meeting with Narendra Modi capped a fresh commitment that lifts Amazon\u2019s planned 2026\u201330 India spend to $48 billion \u2014 the latest and largest move in a hyperscaler land grab that is quietly turning India into critical infrastructure for the AI age.",
    "slug": "amazon-13-billion-india-ai-cloud-investment-jassy-modi-aws-mumbai-hyderabad-48-billion-hyperscaler-nri-investor-20260626-2200",
    "category": "markets-finance",
    "vertical": "tech",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "For NRIs \u2014 many of them the engineers, founders and investors of the global tech economy \u2014 a wave of hyperscaler capital landing in Mumbai and Hyderabad reshapes the calculus of where careers, startups and portfolios should be anchored: the AI infrastructure they have helped build in Seattle and the Bay Area is now being poured into the country many of them came from, narrowing the distance between the diaspora\u2019s two homes.",
    "sources": json.dumps([
        {"name": "The Wall Street Journal \u2014 \u2018Amazon to Invest Additional $13 Billion in India by 2030\u2019", "url": "https://www.wsj.com/business/amazon-to-invest-additional-13-billion-in-india-by-2030"},
        {"name": "Barron\u2019s \u2014 \u2018Why Amazon Is Investing Another $13 Billion in India\u2019s AI Data Centers\u2019", "url": "https://www.barrons.com/articles/amazon-india-ai-data-center-investment"},
        {"name": "Inc42 \u2014 \u2018Amazon Announces Additional $13 Bn Investment In India\u2019", "url": "https://inc42.com/buzz/amazon-announces-additional-13-bn-investment-in-india/"}
    ]),
    "body": """Amazon has committed an additional $13 billion to India, a pledge that pushes its planned investment in the country to $48 billion between 2026 and 2030 and underscores a broader truth taking shape this year: the world's largest technology companies have decided that India is where the next phase of the artificial-intelligence build-out will happen. Chief Executive Andy Jassy announced the figure during a visit to New Delhi, where he met Prime Minister Narendra Modi.

## Where the Money Goes

The fresh capital is pointed squarely at the plumbing of the AI economy. It will expand the data-centre capacity of Amazon Web Services in Mumbai and Hyderabad, giving startups, enterprises and government bodies access to custom AI chips, managed AI services, secure cloud technology and developer tools. With this addition, Amazon's planned AI and cloud infrastructure spending in India now exceeds $21 billion over the five-year window \u2014 establishing it, the company says, as one of the largest such investors in the country.

The $13 billion builds on a $35 billion India commitment Amazon unveiled in December 2025, and it sits within a far longer arc. Counting everything since the company entered India over a decade ago \u2014 first with a price-comparison site in 2012, then a marketplace in 2013 \u2014 Amazon's cumulative investment from 2010 to 2030 now tops $88 billion. Beyond data centres, the company plans to open more than 20 new fulfilment centres and over 100 last-mile delivery stations within the year, much of it aimed at deepening its reach into smaller Tier III and IV towns.

## A Hyperscaler Land Grab

Amazon is not moving alone, and that is the larger story. India has become the new frontier for the so-called hyperscalers \u2014 the handful of giants building the colossal data centres that house the world's cloud and AI computing. In October, Alphabet-owned Google announced a $15 billion plan to expand data-centre capacity in southern India, including undersea-cable links. In December, Microsoft unveiled its largest-ever investment in Asia, a $17.5 billion pledge to develop India's cloud and AI infrastructure. Taken together, the commitments amount to tens of billions of dollars converging on a single country in the span of a year.

The pull is twofold. India's 1.4 billion people are among the most enthusiastic users of data and AI tools anywhere, generating raw demand that the hyperscalers are racing to serve locally rather than from distant servers \u2014 a structure that also lets customers keep data within India's borders. And policy has sweetened the case: earlier this year the government introduced measures granting long-term tax breaks to global hyperscalers that route worldwide operations through India-based data centres, an explicit bid to turn the country into an export hub for compute rather than merely a consumer of it.

Amazon framed its spending around India's own stated ambitions. Jassy said the company aims to support 3.8 million jobs in India by 2030, enable $80 billion in cumulative e-commerce exports, extend AI tools to 15 million small businesses and provide AI education to 4 million government-school students \u2014 invoking Modi's vision of a "Viksit and Atmanirbhar Bharat," a developed and self-reliant India. The rhetoric aside, the commercial logic is straightforward: demand is exploding, and whoever owns the infrastructure owns the toll road.

## Why It Matters for the Diaspora

For the Indian diaspora, this wave of capital is more than a business-page headline \u2014 it reshapes a long-running personal calculation. Many NRIs are themselves the engineers, founders and investors who built the AI and cloud systems now being replicated in Mumbai and Hyderabad. Indeed, AWS, Microsoft and Google are all led at the top or in key divisions by leaders of Indian origin, a quiet symmetry in this story of American capital flowing back to the homeland.

The practical effects ripple outward. A denser AI infrastructure at home strengthens the case for diaspora founders to build in India, or to split operations across both countries, and it deepens the talent magnet that may keep more graduates from emigrating in the first place. For NRI investors, the build-out lifts the long-term prospects of Indian technology, real estate around data-centre clusters, and the power and cooling industries that feed them. None of this is without risk \u2014 questions of energy supply, water use and whether the promised jobs materialise remain open. But for a community whose identity has always been stretched between two countries, the spectacle of the world's tech titans pouring their most strategic capital into India narrows that distance. The infrastructure of the future is being laid, increasingly, in the place many of them still call home."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["person exercise treadmill cardio fitness", "adult walking exercise outdoor", "people running jogging fitness"],
                          ["person exercising treadmill gym cardio", "adult jogging running outdoor fitness"], None),
    articles[1]["slug"]: (["dietary supplement capsules pills bottle", "glucosamine supplement capsules", "supplement pills tablets hand"],
                          ["dietary supplement capsules pills", "supplement pills tablets bottle"], None),
    articles[2]["slug"]: (["data center servers cloud computing", "server room data center technology", "Amazon Web Services data center"],
                          ["data center server room cloud", "server racks data center technology"], None),
}
img_captions = {
    articles[0]["slug"]: "In a year-long trial, regular exercise \u2014 not the weight-loss drug liraglutide alone \u2014 improved artery health and lowered inflammation after major weight loss",
    articles[1]["slug"]: "Glucosamine, taken by tens of millions for joint pain, was linked to faster dementia progression and higher death risk in a large records analysis",
    articles[2]["slug"]: "Amazon's fresh $13 billion pledge will expand AWS data-centre capacity in Mumbai and Hyderabad, part of a hyperscaler push into India's AI economy",
}
for art in articles:
    cq, pq, person = img_specs[art["slug"]]
    url, attribution = source_image(art["slug"], cq, pq, person=person)
    if url:
        art["image_url"] = url
        art["image_caption"] = img_captions[art["slug"]]
        art["image_attribution"] = attribution
    else:
        print(f"  \u26a0 {art['slug']} will publish without hero image")

# ============================================================
# INSERT
# ============================================================
print(f"\n{'='*60}\nInserting {len(articles)} articles at {now}\n{'='*60}\n")
success = 0
for a in articles:
    wc = len(a['body'].split())
    has_img = "img\u2713" if a.get("image_url") else "NO-IMG"
    print(f"  [{a['category']}] {a['slug']} \u2014 {wc} words \u2014 {has_img}")
    if insert_article(a):
        success += 1
print(f"\n{'='*60}\nDone: {success}/{len(articles)} articles inserted\n{'='*60}")
