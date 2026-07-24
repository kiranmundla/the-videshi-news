#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-26 18:00 UTC batch.
Topics (checked against ~30 recent articles to avoid dupes):
  1. AQP4 gene x sleep interaction shapes Alzheimer's risk — Edith Cowan
     University study in Alzheimer's & Dementia (Porter et al.); 351 AIBL adults
     in their mid-70s, no cognitive impairment but amyloid-positive; 13 AQP4
     variants tracked against self-reported sleep + repeated brain scans +
     6-domain cognitive testing. Same variant protective or detrimental
     depending on sleep; glymphatic waste-clearance (active in sleep) effect
     depends on AQP4 variant. Quotes: Ayeisha Milligan Armstrong, Tenielle
     Porter, Simon Laws. — lifestyle-health
     (DISTINCT: prior sleep pieces covered white-matter lesions and sleep
      habits/brain-aging broadly; this is gene-sleep interaction +
      personalized risk, a new angle.)
  2. Long-term resistance training + aerobic activity + less TV = sharply lower
     type 2 diabetes risk — JAMA Network Open (Zhang T, Zhang Y, Lee DH et al.,
     2026; e2619420). 143,715 US health professionals across HPFS/NHS/NHS II,
     ~19yr follow-up, 10,038 T2D cases. 2+ hrs/wk resistance training HR 0.73;
     consistent high-level >=30 min/wk in midlife 42% lower (HR 0.58); the
     trifecta (>=1 hr/wk RT + >=15 MET-hr/wk aerobic + <2 hr/day TV) HR 0.38.
     — lifestyle-health
     (DISTINCT: no recent T2D-prevention or resistance-training-specific
      piece; prior coverage was diet/sleep/movement-snack and longevity epi.)
  3. India's sub-par monsoon as the biggest near-term macro risk — S&P Global
     cut FY27 growth to 6.6% (from 7.7% in FY26) citing sub-par monsoon, energy
     stress and slowing global growth; rainfall deficit 43% by June 22 amid El
     Nino; state-wise crop contingency plans; inflation seen rising to 5.1%,
     a rate hike flagged for H2 FY27; agriculture ~16% of GDP, 45% of workforce.
     — markets-finance
     (DISTINCT: prior finance pieces were NSE IPO, IRFC OFS, rupee/FCNR-B,
      gold, SIP flows, GIFT City NRI investing, Meta-CRED — none cover the
      monsoon/food-inflation/rural macro-risk angle.)
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1800.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1800.bin"):
            with open("/tmp/_img_dl1800.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1800.bin")
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
# ARTICLE 1: AQP4 gene x sleep -> Alzheimer's (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Your Genes May Decide Whether Your Sleep Protects Your Brain \u2014 or Harms It",
    "subheadline": "A study of older Australians found that variants of a single gene governing the brain\u2019s overnight waste-clearance system interact with sleep habits to shape brain structure and memory long before Alzheimer\u2019s appears \u2014 meaning the same night\u2019s sleep can help one person and hurt another.",
    "slug": "aqp4-gene-sleep-interaction-alzheimers-risk-edith-cowan-university-glymphatic-personalized-prevention-diaspora-20260626-1800",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry a heavy, often early-onset burden of dementia risk, and the diaspora\u2019s sandwich generation \u2014 caring for aging parents while raising children \u2014 is hungry for concrete prevention advice; this study\u2019s message that there is no universal \u2018right\u2019 amount of sleep, and that the benefit depends on your genes, argues for personalized, genetically informed brain care rather than one-size-fits-all rules NRI families often pass around.",
    "sources": json.dumps([
        {"name": "Inc. \u2014 \u2018Think 8 Hours of Sleep Is the Best for Your Cognitive Health? A New Study Suggests Otherwise\u2019", "url": "https://www.inc.com/lucia-auerbach/think-eight-hours-of-sleep-is-the-best-for-cognitive-health-new-study-suggests-otherwise/91364034"},
        {"name": "Porter, T., et al. (2026), \u2018Evidence for direct and sleep-moderated relationships between aquaporin-4 genetic variants and Alzheimer\u2019s disease phenotypes\u2019, Alzheimer\u2019s & Dementia", "url": "https://alz-journals.onlinelibrary.wiley.com/doi/10.1002/alz.70476"}
    ]),
    "body": """For years the advice on sleep and brain health has been comfortingly simple: get your eight hours, keep a steady schedule, and you lower your risk of dementia down the line. A new study complicates that tidy picture in a way that may ultimately make the advice more useful. It found that whether a given pattern of sleep helps or harms the aging brain depends, in part, on a gene you were born with.

## A Gene for the Brain's Night Shift

The research, published in the peer-reviewed journal *Alzheimer's & Dementia* and led by scientists at Edith Cowan University in Australia, centres on a gene called aquaporin-4, or AQP4. The gene governs a water channel that helps move fluid through the brain \u2014 the plumbing behind the glymphatic system, the brain's waste-clearance network that is most active during sleep and helps flush out amyloid and tau, the proteins that build up in Alzheimer's disease.

That clearance system, it turns out, does not work the same in everyone. How efficiently it operates depends partly on which version of the AQP4 gene a person carries, and partly on how they sleep. The interaction between the two, the researchers found, can tip the brain toward resilience or toward decline.

"Our study shows that individuals carrying certain AQP4 variants showed faster grey matter loss when they reported shorter sleep," said Ayeisha Milligan Armstrong, a postdoctoral research fellow in ECU's Centre for Precision Health. "It's not just which genes you carry \u2014 it's how those genes interact with the world around you. The same variant can look protective or detrimental depending on how someone is sleeping."

## What the Study Looked At

The team drew on 351 older adults enrolled in the Australian Imaging, Biomarkers and Lifestyle study, a long-running project that has followed thousands of participants since 2006, collecting data every 18 months. The people in this analysis were in their mid-70s and had no diagnosed cognitive impairment \u2014 but they were showing early signs of amyloid buildup in the brain, placing them on a biological path toward Alzheimer's even as they appeared healthy.

The scientists tracked 13 common variants of the AQP4 gene against each participant's self-reported sleep, then layered on repeated brain scans and cognitive testing across six domains, including memory, language and attention. The results refused to line up behind a single rule. For some participants, shorter sleep tracked with faster loss of grey matter over time; for others, what mattered most was how long it took them to fall asleep. Strikingly, longer sleep was not always better: for at least one variant, people who logged more hours actually showed a steeper cognitive decline than those who slept less. Cognitive trajectories diverged in the same way \u2014 the direction of the effect, better or worse, depended on which variant a person carried.

## No Single Magic Number

The practical upshot is humbling for anyone seeking a neat sleep target. "What this shows is that rather than assuming everyone at risk follows the same pathway, a more targeted and personalized approach to Alzheimer's prevention may be needed," said Tenielle Porter, a researcher on the study.

Professor Simon Laws, the centre's director, was blunt about why there is no universal number. "The effect shows up as an interaction between a person's genetic background and their sleep," he told Inc. "It's the interaction that matters, not sleep by itself." Well-established habits \u2014 keeping a consistent schedule, treating disorders like sleep apnea \u2014 still hold, he said, but their impact varies from person to person. He cautioned against treating sleep as a bigger or smaller lever than diet or exercise, since those, too, may be shaped by individual genetics.

The findings come with real limits. The sample was modest at 351 people, sleep was self-reported rather than measured in a lab, and an observational study cannot prove that sleep changes brain outcomes rather than merely tracking alongside them. The next step, Laws said, is genetically informed clinical trials that test whether sleep interventions tailored to a person's AQP4 profile actually improve long-term brain health. Crucially, the researchers stress that no single gene seals anyone's fate \u2014 and that sleep, unlike genetics, is something people can change.

## Why It Matters for the Diaspora

For the Indian diaspora, the study lands on sensitive ground. South Asians carry a disproportionate, often earlier-onset risk of dementia, and many NRI households are squarely in the sandwich generation \u2014 watching over aging parents while raising their own children, and trading prevention tips across continents in family WhatsApp groups.

The temptation in those conversations is to seize on a universal rule: everyone should sleep exactly eight hours, or nap less, or go to bed by ten. This research argues against that reflex. It suggests brain health is personal at the level of one's genes, and that the most defensible advice is the unglamorous, individualized kind \u2014 protect your sleep, treat the disorders that fragment it, and recognize that the same routine that suits one relative may not suit another. As genetic testing becomes cheaper and dementia rates climb among aging Indians at home and abroad, that shift from blanket rules to tailored care may prove one of the more important changes in how diaspora families think about protecting the minds of the people they love."""
})

# ============================================================
# ARTICLE 2: Resistance training + aerobic -> lower T2D risk (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Lifting Weights Through Midlife Sharply Cut the Risk of Type 2 Diabetes \u2014 Especially Paired With Walking",
    "subheadline": "Following nearly 144,000 health professionals for almost two decades, researchers found that those who kept up resistance training had a markedly lower risk of type 2 diabetes \u2014 and the benefit was greatest when strength work was combined with aerobic exercise and less time in front of the television.",
    "slug": "resistance-training-aerobic-exercise-lower-type-2-diabetes-risk-jama-network-open-143715-adults-diaspora-20260626-1800",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians develop type 2 diabetes earlier, at lower body weights, and at far higher rates than most other groups \u2014 a defining health threat for the Indian diaspora \u2014 yet the community\u2019s exercise culture still leans heavily on walking and cardio while neglecting strength work; this study makes a data-backed case that adding resistance training, not just doing more cardio, is one of the most powerful levers NRIs and their families have against a disease that stalks them disproportionately.",
    "sources": json.dumps([
        {"name": "News-Medical \u2014 \u2018Strength training plus cardio cuts type 2 diabetes risk the most\u2019", "url": "https://www.news-medical.net/news/20260623/Strength-training-plus-cardio-cuts-type-2-diabetes-risk-the-most.aspx"},
        {"name": "Zhang T, Zhang Y, Lee DH, et al. (2026), \u2018Long-Term Resistance Training and Risk of Type 2 Diabetes\u2019, JAMA Network Open, 9(6):e2619420", "url": "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2850563"}
    ]),
    "body": """The standard mental image of exercise for diabetes prevention is a brisk walk or a jog \u2014 something that gets the heart pumping. A large new study suggests that picture is incomplete in an important way. Among nearly 144,000 American health professionals followed for almost two decades, those who consistently did resistance training \u2014 lifting weights, using machines or bands \u2014 had a substantially lower risk of developing type 2 diabetes, and the effect was strongest when strength work was combined with regular aerobic activity and less sedentary time.

## A Two-Decade View

The study, published in *JAMA Network Open*, pooled data from three of the largest and longest-running health cohorts in the United States: the Health Professionals Follow-up Study, the Nurses' Health Study and its successor, NHS II. Together they followed 143,715 adults who were free of diabetes, major heart disease and cancer at the outset, tracking their health and habits through biennial questionnaires. Participants were a mean age of 56, mostly women, and were followed for roughly 19 years \u2014 a span over which 10,038 of them went on to develop type 2 diabetes.

Rather than capturing exercise at a single point, the researchers measured resistance training repeatedly, every two to four years, with up to 14 assessments per person. That let them study not just whether people lifted weights but whether they kept it up, expanded it, or let it slide across middle age \u2014 a far richer picture than a one-time snapshot.

## Consistency Was the Key

The pattern that emerged rewarded persistence. Compared with people who did no resistance training, those doing at least two hours a week had a 27 percent lower risk of type 2 diabetes. Middle-aged adults who consistently kept up a higher level of strength training \u2014 even as little as 30 minutes a week done reliably \u2014 had a 42 percent lower risk. Those who built up their training over time fared better than people whose levels stayed consistently low, while an on-again, off-again pattern showed no significant benefit. In short, doing it steadily mattered more than doing a lot in bursts.

The most striking result came from combining habits. People who met recommendations for resistance training and aerobic activity while also limiting television to under two hours a day \u2014 specifically, at least an hour a week of strength work, at least 15 metabolic-equivalent hours a week of aerobic exercise, and curtailed screen time \u2014 had the lowest risk of all, roughly 62 percent below those who did none of these things. Strength and cardio, the data suggest, are not interchangeable; they add up.

The findings held after the researchers adjusted for age, family history of diabetes, smoking, alcohol, diet quality and aerobic activity, and barely budged when they additionally accounted for body weight, waist size or intentional weight loss \u2014 hinting that the benefit is not merely a matter of staying slim. The authors are appropriately cautious. This was an observational study, so it cannot prove cause and effect, and people who train consistently tend to have healthier lifestyles overall, which could flatter the results. The cohort was also overwhelmingly White and female, limiting how far the numbers travel. They call for more diverse populations and objective measures of training in future work.

## Why It Matters for the Diaspora

For the Indian diaspora, few health findings cut closer to home. South Asians are strikingly prone to type 2 diabetes \u2014 developing it earlier in life, at lower body weights, and at rates well above most other populations, a vulnerability rooted in how the body stores fat and handles insulin. For many NRI families, diabetes is not an abstract risk but a near-certain presence across the generations, from grandparents in India to cousins abroad.

Yet the community's exercise habits often lean heavily on walking and cardio, with strength training treated as optional or unfamiliar \u2014 something for bodybuilders, not for managing a chronic-disease risk. This study reframes that. It suggests resistance training is not a luxury add-on but a distinct and powerful tool, one that works best alongside the cardio many already do. The practical takeaway is both simple and demanding: a couple of strength sessions a week, kept up steadily through midlife rather than abandoned after a New Year's burst, paired with regular walking and less time on the sofa. For a community carrying an outsized diabetes burden, that combination may be among the highest-value health investments available \u2014 and one that costs little more than a resistance band and the discipline to keep going."""
})

# ============================================================
# ARTICLE 3: India's weak monsoon as macro risk (markets-finance)
# ============================================================
articles.append({
    "headline": "A Failing Monsoon Becomes India\u2019s Biggest Economic Wildcard as S&P Trims Growth Forecast",
    "subheadline": "S&P Global has cut India\u2019s growth projection for the year to 6.6 percent, citing a sub-par monsoon, energy stress and a softer global economy \u2014 a reminder that for all its tech and services heft, the country\u2019s fortunes still ride on the rains.",
    "slug": "india-weak-monsoon-macro-risk-sp-global-cuts-fy27-growth-6-6-percent-food-inflation-rural-diaspora-portfolios-20260626-1800",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "For NRIs the monsoon is not weather trivia but a direct line to the things they track from afar \u2014 the rupee they remit in, the food prices their parents pay, the rural incomes that underpin family finances back home, and the inflation-and-rates path that moves their India-linked investments; a deficient monsoon touches diaspora wallets through every one of those channels at once.",
    "sources": json.dumps([
        {"name": "Outlook Business \u2014 \u2018India\u2019s FY27 Growth Likely to Slow Down to 6.6% on Energy Stress, Sub-Par Monsoon: S&P\u2019", "url": "https://www.outlookbusiness.com/economy-and-policy/indias-fy27-growth-likely-to-slow-down-to-66-on-energy-stress-sub-par-monsoon-sp"},
        {"name": "The Hindu BusinessLine \u2014 \u2018India\u2019s growth expected be in 6.4-6.7% range\u2019", "url": "https://www.thehindubusinessline.com/economy/indias-growth-expected-be-in-64-67-range/article71140000.ece"}
    ]),
    "body": """India likes to tell a story about itself as a modern, services-driven economy \u2014 a software and start-up powerhouse insulated from the old rhythms of the field. A run of worrying forecasts this week is a reminder that the rains still write a large part of the plot. S&P Global Ratings has cut its projection for India's economic growth in the fiscal year ending March 2027 to 6.6 percent, down from the 7.7 percent the economy delivered the year before, citing a sub-par monsoon, energy stress and slowing global growth.

## The Numbers and the Rains

S&P's downgrade, contained in its quarterly Asia-Pacific economic commentary, lands in the middle of a clutch of similar revisions: HDFC Bank pegs FY27 growth at 6.7 percent, Bank of Baroda at 6.4 to 6.6 percent, and the figures sit close to the Reserve Bank of India's own revised estimate of 6.6 percent, trimmed from 6.9 percent. The common thread is the weather. By June 22, the cumulative monsoon rainfall deficit had widened to 43 percent, with a weak El Nino sapping the rains that irrigate much of the country's farmland. In response, the government has drawn up state-by-state contingency plans, recommending alternative crops better suited to dry conditions.

The reason a poor monsoon still rattles the whole economy is structural. Agriculture accounts for only about 16 percent of India's output but supports roughly 45 percent of its workforce. A weak season hits rural incomes directly, which saps demand for everything from motorcycles to soap, while pushing up the price of food \u2014 the largest single component of the consumer price basket. S&P expects consumer inflation to climb to 5.1 percent this fiscal year, with food and fertiliser costs compounded by energy stress from conflict in West Asia. India imports nearly 89 percent of its crude oil, so higher global prices inflate its import bill, widen the current account deficit and weigh on the rupee.

## A Squeeze From Two Sides

That combination \u2014 dearer food at home and dearer oil from abroad \u2014 leaves policymakers with an uncomfortable trade-off. Rising prices erode purchasing power and dampen the consumer spending that drives much of India's growth, yet the usual remedy, cutting interest rates to spur activity, becomes harder when inflation is climbing. S&P expects the central bank to actually raise its policy rate in the second half of the fiscal year, a tightening that would lift borrowing costs for businesses and households alike. The agency reckons consumer inflation could run half a percentage point higher in the third quarter as manufacturers pass on higher energy costs, alongside recent increases in petrol, diesel and cooking-gas prices.

Some caution is warranted before treating any of this as fate. Monsoon forecasts are notoriously volatile, and a deficit in late June can narrow sharply if the rains revive in July and August, the heart of the season. India's deep foreign-exchange reserves, robust domestic demand and diversified services sector \u2014 IT and business-process outsourcing still hum along, buoyed by an AI-driven export boom \u2014 give it real buffers that many emerging economies lack. A 6.6 percent expansion would still rank among the fastest of any major economy. The downgrade is a trimming of expectations, not a forecast of crisis.

## Why It Matters for the Diaspora

For the Indian diaspora, the monsoon is not distant weather news but a thread tied to several things NRIs watch closely from abroad. The most immediate is the rupee: a weaker currency, pressured by a rising oil bill, changes the math on every remittance sent home and on the value of India-held savings. Then there is the household reality for family back home \u2014 a poor harvest means higher prices at the market for the very parents and relatives many NRIs support, and softer incomes in the rural communities where extended families often still have roots and land.

For those who invest in India, the implications run deeper still. A path of higher inflation and higher interest rates reshapes the outlook for Indian equities and bonds, weighs on rate-sensitive sectors, and clouds the consumption-led growth story that draws diaspora capital in the first place. Agriculture-exposed stocks, consumer companies and the banks all feel the monsoon's pull. None of this argues for alarm \u2014 the rains may yet come good, and India's long-run trajectory remains among the world's most compelling. But it is a useful corrective to the idea that the country has outgrown the sky. For NRIs weighing how much of their portfolio, and their hearts, to anchor in India, the season's progress is worth watching as closely as any earnings report."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["older adult sleeping bed", "senior person sleeping rest", "brain MRI scan medical"],
                          ["older person sleeping peacefully", "senior adult sleep rest bed"], None),
    articles[1]["slug"]: (["person resistance training dumbbell gym", "weight training strength exercise", "older adult lifting weights fitness"],
                          ["person lifting weights gym strength", "resistance training dumbbell workout"], None),
    articles[2]["slug"]: (["monsoon rain India agriculture field", "Indian farmer paddy field rain", "India rice farming monsoon"],
                          ["monsoon rain farm field india", "indian agriculture farmer field"], None),
}
img_captions = {
    articles[0]["slug"]: "Whether a given sleep pattern protects the aging brain may depend on a gene that governs its overnight waste-clearance system, researchers found",
    articles[1]["slug"]: "Consistent resistance training through midlife was linked to a sharply lower risk of type 2 diabetes, a 144,000-person study found",
    articles[2]["slug"]: "A 43% monsoon rainfall deficit has emerged as a leading risk to India's growth and food prices this year",
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
