#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-23 10:00 UTC batch.
Topics (checked against last-3-day articles to avoid dupes):
  1. Hearing loss is one of the largest MODIFIABLE risk factors for dementia —
     a new All of Us analysis (16,270 adults) found severe hearing loss carried
     an odds ratio of 6.76 for dementia, and the randomized ACHIEVE-style
     hearing-aid trial (~1,000 adults 70-84) cut cognitive decline by nearly 50%
     in high-risk elders. — lifestyle-health
  2. Microplastics found inside the human eye — the first study to detect
     microplastics in the trabecular meshwork (20 glaucoma patients) tied the
     plastic burden tightly to higher intraocular pressure, hinting at a new,
     under-recognised pathway in glaucoma. — lifestyle-health
  3. Indian IT stocks slump after Accenture trims its FY26 revenue guidance to
     3-4%; brokerages warn FY27 for Indian IT could be weaker than the Street
     expects as AI and cautious client spending cloud the outlook. — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1000z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1000z.bin"):
            with open("/tmp/_img_dl1000z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1000z.bin")
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
# ARTICLE 1: Hearing loss as a leading modifiable dementia risk (lifestyle-health)
# ============================================================
articles.append({
    "headline": "One of the Biggest Risks for Dementia Is Also One of the Easiest to Treat \u2014 and It Sits in the Ears",
    "subheadline": "A new analysis of more than 16,000 American adults found severe hearing loss was associated with a sharply higher risk of dementia, while a major randomized trial showed that simply fitting at-risk elders with hearing aids slowed their cognitive decline by nearly half.",
    "slug": "hearing-loss-modifiable-dementia-risk-all-of-us-16270-achieve-hearing-aids-cognitive-decline-diaspora-20260623-1000",
    "category": "lifestyle-health",
    "vertical": "healthy-aging",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "In many Indian families, an elder's fading hearing is quietly accepted as a normal part of getting old and rarely treated \u2014 yet this research reframes an untreated hearing problem as a serious, fixable threat to the mind, making a hearing test and a pair of hearing aids one of the most worthwhile gifts an NRI child can arrange for a parent ageing in India or abroad.",
    "sources": json.dumps([
        {"name": "All of Us Research Program analysis (16,270 participants) \u2014 'Hearing Loss as a Modifiable Risk Factor for Dementia', medRxiv preprint", "url": "https://pubmed.ncbi.nlm.nih.gov/"},
        {"name": "NIH Research Matters \u2014 Hearing aids slow cognitive decline in people at high risk (ACHIEVE trial, ~1,000 adults aged 70-84)", "url": "https://www.nih.gov/news-events/nih-research-matters"},
        {"name": "Lancet Commission on dementia prevention, intervention and care \u2014 hearing loss as a leading modifiable risk factor", "url": "https://www.thelancet.com/commissions/dementia2024"}
    ]),
    "body": """It is one of the cruellest features of growing old, and one of the most quietly ignored: the slow fading of hearing. A conversation becomes a guessing game. The television creeps louder. Family gatherings turn into a blur of half-caught words. For decades this was waved away as a normal, harmless part of ageing. A growing body of research now argues it is anything but harmless \u2014 and that treating it may be one of the most powerful, and most overlooked, ways to protect the ageing brain.

## What the New Numbers Show

In one of the largest analyses of its kind, researchers drew on the United States' All of Us research database, examining 16,270 adults, of whom about 1,224 \u2014 roughly 7.5 percent \u2014 had been diagnosed with dementia. After matching participants by age and demographics, the pattern was stark. People with severe, self-reported hearing loss had an odds ratio of 6.76 for dementia \u2014 meaning the association was far stronger than for many risk factors people worry about far more.

To put that in context, the same analysis found smoking carried an odds ratio of 1.71 and high blood pressure 1.48. Sensorineural hearing loss \u2014 the common age-related kind caused by damage to the inner ear \u2014 carried an odds ratio of 3.90. In short, of all the things linked to dementia in this dataset, the loss of hearing stood out as one of the most strongly associated.

This is not a fringe finding. The influential Lancet Commission on dementia has for years ranked hearing loss among the single largest *modifiable* risk factors for dementia across a person's lifetime \u2014 the word "modifiable" being the crucial one. Unlike age or genetics, hearing loss can be treated.

## The Trial That Changes the Conversation

Association studies can only take you so far; they show a link, not proof that fixing the problem helps. That is what made a landmark randomized trial so important. Researchers, co-led by Dr. Frank Lin of Johns Hopkins University, enrolled nearly 1,000 adults aged 70 to 84 who had significant hearing loss. Half were fitted with hearing aids and taught how to use them. The other half received a health-education programme.

Across the whole group, the effect over three years was modest. But among the participants at higher risk of dementia \u2014 older people drawn from a long-running heart-health study, who were declining faster to begin with \u2014 those who got hearing aids saw their rate of cognitive decline cut by almost 50 percent compared with those who did not. For a vulnerable group, halving the speed of decline with a device that carries no drug side effects is a remarkable result.

## Why the Ears and the Mind Are Linked

Scientists offer several overlapping explanations. When hearing fades, the brain must strain to decode muffled sound, draining mental resources that might otherwise support memory and thinking. Poor hearing also pushes people toward isolation \u2014 they withdraw from conversation, social events and the mental stimulation that keeps the brain engaged. And there is evidence that the parts of the brain that process sound may shrink when starved of input. Restoring sound, the theory goes, keeps those circuits active and people connected.

## The Caveats

None of this means hearing aids are a cure for dementia, or that everyone who treats their hearing will be spared. The trial's strongest effect was confined to a high-risk subgroup, and the All of Us figures rest partly on self-reported hearing and cannot prove cause and effect on their own. Hearing loss is one piece of a complex puzzle that also includes blood pressure, diabetes, exercise, education and more.

But the direction of the evidence is consistent and the intervention is unusually safe and concrete. For a field that has spent billions chasing dementia drugs with disappointing results, the idea that a hearing test and a well-fitted device might meaningfully protect the brain is both humbling and hopeful.

## Why It Matters for the Diaspora

In Indian households, an elder cupping a hand to one ear is a familiar, almost affectionate image \u2014 and far too often, that is where it ends. Hearing loss is widely treated as an inevitable, untreatable quirk of old age rather than a medical condition worth acting on. Hearing aids carry stigma, get dismissed as vanity, or are written off as too expensive or too fiddly to bother with.

This research reframes that calculation. For NRIs managing a parent's health from afar \u2014 whether the parent is in Mumbai or has moved in across the world \u2014 arranging a proper hearing assessment and, if needed, hearing aids may rank among the most valuable things they can do for that parent's long-term independence and mind. It is concrete, it is increasingly affordable, and unlike so much health advice, it asks for a one-time action rather than a lifetime of willpower. Encouraging an elder past the embarrassment of wearing a device \u2014 and helping them actually use it \u2014 may protect not just what they hear, but how clearly they think for years to come."""
})

# ============================================================
# ARTICLE 2: Microplastics found inside the human eye (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Scientists Have Found Microplastics Inside the Human Eye \u2014 and the More There Were, the Higher the Pressure",
    "subheadline": "In the first study to look, researchers detected microplastic particles in every sample of a delicate drainage tissue taken from glaucoma patients, and the plastic burden tracked closely with the dangerously high eye pressure that drives the disease.",
    "slug": "microplastics-human-eye-trabecular-meshwork-glaucoma-intraocular-pressure-first-evidence-diaspora-20260623-1000",
    "category": "lifestyle-health",
    "vertical": "environmental-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Glaucoma is a leading cause of irreversible blindness in India, and the diaspora hails from some of the most plastic-saturated, air-polluted cities on earth \u2014 so early evidence that plastic particles may lodge in the eye and push up the pressure that steals sight is a story that lands close to home for millions of NRI families.",
    "sources": json.dumps([
        {"name": "Environmental Pollution \u2014 'First evidence of microplastic pollution in human trabecular meshwork and its association with intraocular pressure in glaucoma' (20 POAG patients)", "url": "https://pubmed.ncbi.nlm.nih.gov/"},
        {"name": "Scientific Reports (Nature) \u2014 Microplastics exposures in cataract surgery and potential clinical concerns", "url": "https://www.nature.com/srep/"},
        {"name": "Current Research in Toxicology \u2014 Micro/nanoplastics in the ocular environment: pathways, toxic effects and future challenges", "url": "https://pmc.ncbi.nlm.nih.gov/"}
    ]),
    "body": """Microplastics have already been found in human blood, the lungs, the placenta, even the brain. Now scientists have detected them somewhere unsettlingly intimate: deep inside the human eye. And in the first study to look, the amount of plastic lurking in a tiny, crucial drainage tissue was tightly linked to the very pressure that drives one of the world's leading causes of blindness.

## What the Researchers Did

A team examined surgical samples of the trabecular meshwork \u2014 a sponge-like ring of tissue at the front of the eye that drains fluid and keeps internal pressure in check \u2014 taken from 20 patients with primary open-angle glaucoma, the most common form of the disease. Using three separate analytical techniques to rule out contamination, they searched each sample for plastic particles.

They found them in every single one. The dominant polymers were polyamide 66 (a nylon used in textiles and many consumer goods), polyvinyl chloride (PVC) and polypropylene. Across the samples, the analysis identified 14 different polymer types in all, and nearly 77 percent of the detected particles were smaller than 50 micrometres \u2014 small enough to matter for the eye's microscopic drainage channels.

## The Worrying Correlation

The most striking result was not merely that the plastics were there, but how closely their abundance tracked the disease. After adjusting for factors such as age and medication, the total microplastic burden in the tissue showed a strong, statistically significant correlation with the patients' peak intraocular pressure before any treatment, and with their pressure just before surgery.

Intraocular pressure is the central villain in glaucoma. When fluid cannot drain properly and pressure builds, it gradually damages the optic nerve, stealing peripheral vision so slowly that many people do not notice until sight is permanently lost. The new study raises the possibility \u2014 and the authors are careful to call it a possibility \u2014 that accumulating plastic particles may clog or irritate that drainage system, nudging pressure upward through a pathway nobody had mapped before.

## Part of a Bigger Picture

This work does not stand alone. A separate study detected microplastics in the intraocular fluid and clouded lenses of patients undergoing cataract surgery, with higher concentrations in those who had diabetes or recent eye disease \u2014 conditions that weaken the barriers meant to keep such particles out. Reviews of the emerging field describe how plastics may reach the eye through direct contact, through the air, or by travelling through the bloodstream after we eat and breathe them, and how, once there, they can trigger oxidative stress and inflammation, with smaller particles tending to do more damage.

## The Caveats Are Significant

It is essential to be clear about what this study does and does not show. Twenty patients is a small sample. A correlation between plastic levels and eye pressure is not proof that the plastic caused the pressure \u2014 it is plausible that diseased, higher-pressure eyes simply trap more particles, rather than the particles driving the disease. No one has yet shown that reducing plastic exposure lowers eye pressure or prevents glaucoma. This is the opening chapter of a research story, not its conclusion.

What it does do is open a genuinely new line of inquiry into a disease that blinds millions, and add the eye to the lengthening list of human organs in which our plastic-soaked environment leaves a measurable trace.

## Why It Matters for the Diaspora

Glaucoma is often called the "silent thief of sight," and it weighs heavily on Indian families: India is home to a vast share of the world's glaucoma cases, and the condition runs in families, so a diagnosis in one relative is a warning to the rest. Much of the diaspora, meanwhile, traces its roots to cities choked with plastic waste and fine particulate pollution, and carries those exposures into urban lives abroad.

The practical takeaways are not panic but prudence. The single most important defence against glaucoma remains unchanged and is well within reach: regular eye-pressure checks, especially for anyone over 40 or with a family history, because early-caught glaucoma can be controlled while lost vision cannot be restored. Sensible steps to cut everyday plastic exposure \u2014 less single-use plastic, filtered water, fewer plastic food containers heated in the microwave \u2014 are reasonable on their own merits while science works out whether they protect the eye. For a community that prizes both its elders' independence and its children's future, keeping an eye on the eyes has rarely looked more worthwhile."""
})

# ============================================================
# ARTICLE 3: Indian IT stocks slump after Accenture guidance cut (markets-finance)
# ============================================================
articles.append({
    "headline": "An Accenture Warning Knocks Indian IT \u2014 and the Bigger Fear Is What It Signals for Next Year",
    "subheadline": "After the world's largest IT services firm trimmed its revenue outlook, Indian software giants like Infosys, TCS and Wipro slid as much as 7 percent, and brokerages warned that the coming financial year could prove tougher than the market has been pricing in.",
    "slug": "indian-it-stocks-slump-accenture-guidance-cut-infosys-tcs-wipro-fy27-ai-weak-demand-nri-investor-20260623-1000",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Indian IT is the diaspora's bellwether industry \u2014 it employs many NRIs' relatives, anchors the portfolios of those who invest back home, and underpins the H-1B pipeline that brought a generation to America \u2014 so a warning that demand and AI are squeezing the sector touches NRI jobs, savings and family fortunes at once.",
    "sources": json.dumps([
        {"name": "Outlook Business \u2014 'Infosys, TCS, Coforge Recover As Investors Buy The Dip After Accenture Shock'", "url": "https://www.outlookbusiness.com/"},
        {"name": "Mint \u2014 'AI, weak demand cloud FY27 outlook for Indian IT'", "url": "https://www.livemint.com/industry/infotech"},
        {"name": "Reuters / Asia Insider \u2014 'Indian IT stocks slump up to 7% as Accenture cuts revenue outlook'", "url": "https://www.reuters.com/"}
    ]),
    "body": """When Accenture sneezes, Indian IT catches a cold. That old market adage proved true again last week. After the Dublin-based services giant \u2014 the world's largest \u2014 trimmed its full-year revenue forecast, shares of India's software majors tumbled, with some falling as much as 7 percent in a single session. The deeper worry on Dalal Street is not the one bad day, but what the warning hints at for the year ahead.

## What Accenture Said

On June 18, Accenture narrowed its guidance for the financial year ending in August, cutting the upper end of its expected revenue growth to 4 percent from 5 percent, leaving a range of just 3 to 4 percent. It also flagged that new order bookings in its traditional IT services business had weakened, reporting $19.3 billion in fresh orders \u2014 its lowest in six quarters. Chief executive Julie Sweet told analysts that client budgets "haven't been increasing," even with the buzz around artificial intelligence: companies are spending differently, not spending more.

For markets, the read-across to India was immediate. Indian IT firms earn a large share of their revenue from the United States and have long taken cues from Accenture as a barometer of global technology demand.

## The Hit to Indian Names

The selling was broad. Tata Consultancy Services, India's largest IT company, fell more than 5 percent. Infosys dropped over 7 percent, and Tech Mahindra slid more than 4 percent. The benchmark Nifty IT index shed more than 5 percent, and over a tougher stretch had given up more than 7 percent in six trading days. By Friday the index had touched its lowest level since April 2023.

The bleeding was not permanent. By the following session, bargain hunters stepped in and names like Infosys, TCS and Coforge clawed back some ground as investors "bought the dip." But the rebound did little to settle the underlying anxiety.

## The Real Fear: FY27

What rattled analysts was less the current year than the next one. Bank of Baroda analysts noted that combining Accenture's signalled weakness in the second half of its fiscal year with cautious commentary from peers like Cognizant points to one conclusion: that the next financial year for the Indian IT services industry could be weaker than the Street had assumed. Morgan Stanley called the backdrop a "tough macro climate" and warned the uncertainty could spill into guidance from Indian firms. Jefferies said consensus earnings estimates across the sector may need to come down.

Two forces are squeezing the industry at once. The first is cautious client spending, aggravated by geopolitical tension in West Asia that has prompted some companies to hold off on technology projects. The second, more structural, is artificial intelligence. AI tools are no longer confined to automating coding or call-centre work; they are increasingly used to build software and even craft sales pitches, prompting clients to rethink how much they need to hand to traditional IT vendors at all.

## Cheap, But Not Yet a Bargain

There is a more constructive reading. Several brokerages pointed out that valuations have fallen to historically attractive levels, with top IT stocks trading near their ten-year average price-to-earnings multiples. Citi, however, noted that the Nifty IT index still trades around 16 times forward earnings against Accenture's 10 times \u2014 a gap that leaves room for further de-rating. HSBC argued recent weakness owes more to geopolitical uncertainty than to fears about AI, but conceded the sector "lacks significant near-term catalysts." In other words: cheaper, yes; an obvious bargain, not yet. A genuine re-rating, most agree, will require a new technology spending cycle and real earnings upgrades \u2014 neither of which is visible today.

## Why It Matters for the Diaspora

No industry is woven into the Indian diaspora's story quite like IT. It is the sector that employs millions back home, including the relatives of countless NRIs; it dominates the India-focused portfolios many in the diaspora hold; and it built the H-1B pipeline that carried a generation of Indian engineers to Silicon Valley and beyond. A warning about its growth is therefore not abstract \u2014 it touches NRI savings, family livelihoods and the career prospects of the next wave hoping to follow.

For diaspora investors, the lesson is to separate the noise of a single down day from the signal of a structural shift. The near-term demand wobble may pass; the AI-driven rethinking of what clients buy from IT services firms is likely to be more lasting. That argues for patience over panic, for watching the first-quarter results and FY27 guidance from Infosys and TCS closely, and for treating today's lower valuations as a reason to study the sector carefully rather than a guarantee of easy gains. The companies that adapt fastest to selling AI-era outcomes, rather than billable hours, will be the ones worth owning through the transition."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["hearing aid older adult", "audiology hearing test senior", "elderly person hearing aid ear"],
                          ["senior hearing aid older adult", "audiology hearing test"], None),
    articles[1]["slug"]: (["human eye close up macro", "ophthalmology eye examination patient", "eye iris close up"],
                          ["human eye close up macro", "eye examination ophthalmology"], None),
    articles[2]["slug"]: (["Bombay Stock Exchange building Mumbai", "Infosys campus Bangalore building", "BSE Mumbai trading floor"],
                          ["stock market trading screen india", "office technology workers india"], None),
}
img_captions = {
    articles[0]["slug"]: "Researchers found fitting at-risk older adults with hearing aids cut their rate of cognitive decline by nearly half",
    articles[1]["slug"]: "Scientists detected microplastic particles in the eye's fluid-draining tissue, linked to higher intraocular pressure in glaucoma patients",
    articles[2]["slug"]: "Indian IT majors slid sharply after Accenture trimmed its revenue guidance, dragging the Nifty IT index lower",
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
