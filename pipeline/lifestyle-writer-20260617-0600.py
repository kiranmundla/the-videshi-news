#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-17 06:00 UTC batch (retry).
Topics:
  1. Turmeric/curcumin cuts inflammation in prediabetes & Type 2 diabetes (SLU, Inflammopharmacology) — lifestyle-health
  2. Treating hearing loss before 70 cuts dementia risk sharply (Johns Hopkins / ACHIEVE) — lifestyle-health
  3. Reliance Jio's ~$4bn IPO draft filing imminent before Ambani's AGM — India's biggest-ever listing — markets-finance
"""

import json, os, io, subprocess, urllib.parse, re
from datetime import datetime, timezone
import requests

# ---- env ----
for env_file in ("~/.env.supabase", "~/workspace/.env.pexels"):
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0617.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0617.bin"):
            with open("/tmp/_img_dl0617.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0617.bin")
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
# ARTICLE 1: Turmeric / curcumin & metabolic inflammation (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Spice in Every Indian Kitchen Just Got a Diabetes Study. Curcumin Cut Inflammation in 28 Trials.",
    "subheadline": "A Saint Louis University analysis pooling 28 randomized clinical trials found that curcumin, the active compound in turmeric, measurably lowered inflammation and oxidative stress in people with prediabetes and Type 2 diabetes \u2014 conditions that strike South Asians earlier and harder than almost any other group.",
    "slug": "turmeric-curcumin-inflammation-prediabetes-type-2-diabetes-slu-meta-analysis-south-asian-20260617",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Turmeric is the one ingredient in nearly every Indian household, and a community with one of the world's highest rates of early diabetes now has peer-reviewed evidence that its kitchen staple may double as a low-cost ally against the inflammation that drives the disease \u2014 though as a complement to medicine, never a replacement for it.",
    "sources": json.dumps([
        {"name": "Saint Louis University \u2014 SLU Research: Turmeric May Reduce Inflammation for Diabetic Patients (Rafiei et al., Inflammopharmacology, March 2026)", "url": "https://www.slu.edu/news/2026/march/turmeric-inflammation-research.php"},
        {"name": "Frontiers in Nutrition \u2014 Curcumin\u2013piperine supplementation modulates inflammation, oxidative stress, and cardiometabolic risk: a systematic review of RCTs", "url": "https://www.frontiersin.org/journals/nutrition"},
        {"name": "MDPI \u2014 The Effects of Curcumin on Vascular Endothelial Function, Lipid Metabolism, Inflammation and Neuroprotection (review)", "url": "https://www.mdpi.com/search?q=curcumin+endothelial+inflammation"}
    ]),
    "body": """For generations, the deep-yellow turmeric in the masala dabba has been folded into dal, simmered into curries, stirred into warm milk for a cough, and dabbed on cuts. The diaspora carried that habit across oceans, even as the science treated it as folklore. A new analysis from Saint Louis University suggests the folklore was onto something \u2014 at least where diabetes is concerned.

## What the Researchers Did

Hossein Rafiei, an assistant professor of nutrition and dietetics at Saint Louis University, and his colleagues did not run a single small trial. They pooled the results of **28 randomized clinical trials** and asked a focused question: does curcumin, the main bioactive compound in turmeric, change the markers of inflammation and oxidative stress in people with prediabetes and Type 2 diabetes?

Their answer, published in the peer-reviewed journal *Inflammopharmacology* in March 2026, was yes. Curcumin supplementation was consistently associated with improvements in inflammatory and oxidative-stress markers \u2014 the very biological processes that, left unchecked, push prediabetes toward full diabetes and diabetes toward its complications.

## Why Inflammation Is the Right Target

"These biological processes play an important role in the development and progression of metabolic diseases, so reducing them may help support better metabolic health and potentially reduce insulin resistance," Rafiei said.

That sentence matters more than it looks. Type 2 diabetes is not simply about sugar; it is increasingly understood as a slow-burning inflammatory disease. Chronic, low-grade inflammation corrodes the body's response to insulin and accelerates the damage to blood vessels, kidneys and nerves that makes diabetes dangerous. A cheap, food-derived compound that nudges those markers in the right direction is exactly the kind of complementary tool clinicians have been hunting for.

The SLU finding does not stand alone. A separate systematic review in *Frontiers in Nutrition* examined 20 randomized trials of curcumin paired with piperine \u2014 the compound in black pepper that sharply improves curcumin's notoriously poor absorption. Fifteen of those 20 trials showed significant drops in inflammatory biomarkers such as C-reactive protein and interleukin-6, and most reported improvements in fasting blood glucose, HbA1c and insulin resistance in people with metabolic syndrome and Type 2 diabetes.

## The Crucial Caveat

Rafiei is emphatic on one point, and so is the evidence: curcumin is **not a replacement for standard medical treatment**. No one should swap metformin for a turmeric capsule.

"By helping reduce these biological processes that contribute to disease progression, curcumin may help improve the metabolic environment and potentially lower the risk of complications when combined with appropriate medical care and healthy lifestyle strategies," he said. The operative word is *combined*.

There are practical limits, too. Curcumin on its own is poorly absorbed by the gut \u2014 which is why the most promising trials pair it with piperine, and why a pinch of black pepper in the cooking pot is not an accident of tradition but a quiet act of pharmacology. The trial doses (often 500 to 1,500 mg of curcumin extract daily) are far higher than what a few teaspoons of household turmeric deliver. And anyone on blood thinners or diabetes medication should talk to a doctor before adding a concentrated supplement, because curcumin can interact with both.

## Why the Diaspora Should Pay Attention

South Asians develop Type 2 diabetes younger, at lower body weights, and with more aggressive cardiovascular complications than almost any other population. For the NRI parent watching their HbA1c creep up, or the second-generation professional just told they are prediabetic, the SLU analysis offers something rare: a piece of their own heritage that the evidence now partly vindicates.

The honest takeaway is not "eat more curry and cancel the doctor." It is that the anti-inflammatory diet many diabetes specialists recommend \u2014 rich in spices, vegetables, legumes and whole grains \u2014 already overlaps heavily with the traditional Indian plate. Turmeric, used generously and with a little pepper, is a reasonable, low-risk addition to a medically supervised plan.

## What To Actually Do

Keep cooking with turmeric, and add black pepper to help it absorb. Treat concentrated curcumin supplements as a medical decision, not a grocery one \u2014 raise them with your physician, especially if you take diabetes drugs or blood thinners. And remember the unglamorous truth buried in every one of these trials: curcumin moved the markers, but diet, movement and prescribed medicine moved them more. The spice is an ally, not a cure.
"""
})

# ============================================================
# ARTICLE 2: Treating hearing loss before 70 cuts dementia risk (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Treat Your Hearing Before 70 and Cut Dementia Risk by 60%. The Evidence Is Now Hard to Ignore.",
    "subheadline": "Newly highlighted research from Johns Hopkins finds that addressing hearing loss before age 70 can lower the risk of developing dementia by roughly 60 percent \u2014 making it the single most modifiable risk factor for a disease the diaspora's ageing parents fear most.",
    "slug": "hearing-loss-treatment-before-70-dementia-risk-johns-hopkins-achieve-diaspora-elders-20260617",
    "category": "lifestyle-health",
    "vertical": "healthy-aging",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "For NRIs caring for ageing parents across continents \u2014 often noticing a father's 'huh?' on a grainy video call long before anyone says the word dementia \u2014 the research reframes a hearing aid not as a vanity or an admission of age, but as one of the cheapest, most powerful brain-protective interventions available.",
    "sources": json.dumps([
        {"name": "Johns Hopkins University / ACHIEVE trial \u2014 hearing intervention and cognitive decline (Frank Lin et al.)", "url": "https://www.nia.nih.gov/news/hearing-aids-slow-cognitive-decline-people-high-risk"},
        {"name": "National Institute on Aging \u2014 Hearing aids slow cognitive decline in people at high risk", "url": "https://www.nia.nih.gov/news/hearing-aids-slow-cognitive-decline-people-high-risk"},
        {"name": "The Journals of Gerontology: Series A (Oxford Academic) \u2014 impact of hearing loss on incident dementia and quality of life in the US", "url": "https://academic.oup.com/biomedgerontology"}
    ]),
    "body": """It usually starts small. A parent turns the television up a notch too high. They smile and nod at the dinner table but answer a question no one asked. On the weekly video call, a father leans in and says "huh?" once too often. Families file it away as the ordinary arithmetic of age. New research says it may be one of the loudest warning signs a brain can give \u2014 and one of the most fixable.

## The 60 Percent Number

Research from Johns Hopkins University, recently spotlighted by clinicians and public-health groups, lands on a striking figure: treating hearing loss before the age of 70 can cut the risk of developing dementia by about 60 percent. Hearing loss has, in fact, been identified in major reviews as the single most modifiable risk factor for dementia \u2014 ahead of factors the public worries about far more.

The strongest evidence comes from a landmark randomized trial led by Dr. Frank Lin at Johns Hopkins, which enrolled nearly 1,000 adults aged 70 to 84 with substantial hearing loss. Participants were randomly assigned either to receive hearing aids and training, or to a health-education program focused on healthy ageing. Crucially, some participants were recruited from a long-running heart-health study and carried more dementia risk factors than the general population.

Among that higher-risk group, the result was clear: those who received hearing aids experienced meaningfully slower cognitive decline over three years than those who did not. In a field where most "breakthroughs" involve expensive drugs with modest effects, a device you can wear in your ear stood out.

## Why Hearing and the Brain Are Linked

The mechanism makes intuitive sense once you stop thinking of hearing as a passive sense. When sound fades, the brain works harder to decode every conversation, draining cognitive resources that would otherwise go to memory and thinking \u2014 the so-called "cognitive load" theory. Untreated hearing loss also pushes people to withdraw from conversation, dinners and gatherings, and that social isolation is itself a powerful, independent driver of cognitive decline.

A separate analysis in *The Journals of Gerontology* underscored the stakes at population scale, tying hearing loss and its associated dementia to substantial losses in quality-adjusted life expectancy \u2014 years of independent living quietly erased. The encouraging flip side: effective treatments already exist, from over-the-counter and prescription hearing aids to cochlear implants and aural rehabilitation.

## The Caveats Worth Keeping

The science is not uniformly settled. The Johns Hopkins trial's headline benefit was strongest in the higher-risk subgroup; in the healthier community-recruited participants, the effect was smaller. Some reviews still describe the evidence that hearing aids *prevent* dementia as mixed. What is not mixed is the evidence that treating hearing loss improves quality of life, mood and social connection \u2014 benefits that matter on their own and plausibly protect the brain along the way.

## Why This Hits Home for the Diaspora

For the Indian diaspora, this research sits at a painful intersection. Many NRIs parent from a distance, managing an ageing mother or father's health across ten or twelve time zones. The first sign of trouble often arrives through exactly the medium where hearing loss is most exposed: the phone call, the patchy video link, the parent who stops calling because following the conversation has become exhausting.

There is a cultural barrier, too. In many South Asian households, a hearing aid is treated as a humiliating marker of decline, hidden or refused. This evidence reframes the device entirely \u2014 not as surrender to old age, but as one of the cheapest, most effective things a family can do to protect a parent's mind.

## What To Actually Do

Push for a hearing test before age 70, not after symptoms become severe \u2014 earlier treatment is where the benefit concentrates. Treat a parent's "huh?" and rising TV volume as a medical cue, not a quirk. Over-the-counter hearing aids have made the first step far cheaper and less clinical than it used to be. And frame the conversation gently with ageing relatives: this is about staying in the conversation, at the dinner table and on the call, for as many years as possible.
"""
})

# ============================================================
# ARTICLE 3: Reliance Jio IPO imminent (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Biggest IPO Ever Is About to Land. Reliance Jio May File Draft Papers Within Days.",
    "subheadline": "Reliance Jio Infocomm could file draft papers for its expected $4 billion IPO within days \u2014 just before Mukesh Ambani's closely watched annual address on Friday \u2014 in what would be the first listing from his conglomerate in over two decades and potentially the largest public offering in Indian history.",
    "slug": "reliance-jio-ipo-draft-filing-4-billion-ambani-agm-largest-india-listing-nri-investor-20260617",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Jio is the network most NRIs hand their relatives in India and the app bundle that powers their parents' digital lives; now the diaspora can weigh whether to own a slice of it \u2014 a decision sharpened by a record-breaking float that some veteran analysts warn has historically marked market tops.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 Ambani's Jio set to file for India IPO within days, FT reports", "url": "https://www.reuters.com/business/ambanis-jio-set-file-india-ipo-within-days-ft-reports-2026-06-17/"},
        {"name": "Reuters \u2014 Ambani's Reliance Jio considers 2.5% public offering in 2026 India IPO, sources say", "url": "https://www.reuters.com/markets/deals/ambanis-reliance-jio-considers-25-public-offering-2026-india-ipo-sources-say-2026-01-10/"},
        {"name": "Mint \u2014 Andy Mukherjee: the success of SpaceX's IPO may have eased the path for Jio Platforms to go public", "url": "https://www.livemint.com/opinion"}
    ]),
    "body": """The most anticipated stock-market debut in India is finally moving from rumour to paperwork. Reliance Jio Infocomm, the telecom crown jewel of Mukesh Ambani's empire, could file draft papers for its long-awaited initial public offering within days, the *Financial Times* reported on Wednesday, citing people familiar with the plan. The timing is no accident: it would land just before Ambani's closely watched annual address to Reliance Industries shareholders on Friday.

## The Numbers Behind the Hype

The expected float is roughly **$4 billion**, a figure that would make it the largest IPO in Indian history \u2014 eclipsing Hyundai Motor India's $3.3 billion listing in 2024. Yet that headline number tells only part of the story, because of how little of the company Reliance intends to sell.

The plan, according to earlier Reuters reporting, is to list around **2.5 percent** of Jio Platforms. Reliance prefers a smaller float precisely because the company is so vast: investment bank Jefferies pegged Jio's valuation at about $180 billion in November, with some bankers pitching figures as high as $200 billion to $240 billion. A 2.5 percent slice of a $180 billion company still raises roughly $4.5 billion \u2014 and a smaller float, one source noted, "creates more pricing tension," industry shorthand for a debut engineered to pop.

Jio is not a small or speculative business. Its parent, Jio Platforms, posted operating revenue of $13.65 billion in the year ending March 2025 and a profit after tax of $2.8 billion. Around 75 to 80 percent of that revenue still comes from the core telecom operation \u2014 India's largest, with more than 500 million subscribers.

## A Long Road to the Bourse

This listing has been promised, and delayed, for years. Back in 2019 Ambani said Jio would "move towards" a listing within five years; the plans slipped in 2025, and the targeted filing was pushed back again this year as the conflict in West Asia chilled investor appetite for new issues. The company has hired 17 banks to manage the offering \u2014 a syndicate that itself signals the scale of ambition.

Jio's marquee backers read like a who's who of global capital. In 2020, the company raised more than $20.5 billion from 13 investors, including Meta Platforms (which holds about 9.9 percent), Google parent Alphabet (7.7 percent), KKR, General Atlantic, Silver Lake and the Abu Dhabi Investment Authority. How much of the IPO is a fresh fundraising versus existing investors selling down remains one of the open questions in the draft papers.

## The RBI's Quiet Hand

There is a macro subplot that NRIs in particular should notice. As columnist Andy Mukherjee argued in *Mint*, Jio's float is arriving just as the Reserve Bank of India has moved to absorb the hedging costs for banks raising deposits from the Indian diaspora \u2014 a bid to shore up a weak rupee. If tens of billions of dollars rush into India through that NRI-deposit channel, much of the residual liquidity is likely to gravitate toward the stock market, helping local savers and institutions absorb a mega-float that foreign "hot money," now fixated on AI, may sit out.

## The Caution Flag

Not everyone is cheering. Mukherjee relayed a pointed warning from former Credit Suisse analyst Ashish Gupta, whose 2012 *House of Debt* report presciently flagged the leverage crisis that later hit India Inc. Gupta's caution this time is blunt: massive, record-breaking IPOs have historically preceded market tops. A debut designed for maximum pricing tension can reward the patient and punish the late.

## What It Means for the Diaspora

For NRIs, Jio is not an abstraction. It is the SIM card they buy for visiting relatives, the data plan that keeps their parents on WhatsApp, the bundle of apps \u2014 payments, streaming, commerce \u2014 woven into daily Indian life. Owning a piece of it will be tempting precisely because the product is so familiar.

The sober counsel is the same one that applies to every blockbuster listing. A great company and a great investment are not always the same thing at the same price, and a 2.5 percent float engineered for tension can debut rich. NRIs should watch the draft red herring prospectus for the real numbers \u2014 valuation, use of proceeds, and how much is fresh capital versus insiders cashing out \u2014 rather than buying the hype around Ambani's Friday speech. The biggest IPO in Indian history deserves the most careful reading.
"""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["turmeric powder spice", "turmeric root rhizome", "haldi turmeric bowl"],
                          ["turmeric powder spice bowl", "turmeric root spice"], None),
    articles[1]["slug"]: (["hearing aid device", "elderly person hearing aid", "audiologist hearing test"],
                          ["senior man hearing aid", "elderly hearing aid ear"], None),
    articles[2]["slug"]: (["Reliance Jio store", "Jio logo storefront India", "Mukesh Ambani"],
                          ["mobile phone store india", "indian telecom shop"], "Mukesh Ambani"),
}
img_captions = {
    articles[0]["slug"]: "Turmeric, whose active compound curcumin lowered inflammation markers across 28 diabetes trials",
    articles[1]["slug"]: "A hearing aid; new research finds treating hearing loss before 70 can cut dementia risk sharply",
    articles[2]["slug"]: "Mukesh Ambani, whose Reliance Jio may file for India's largest-ever IPO within days",
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
