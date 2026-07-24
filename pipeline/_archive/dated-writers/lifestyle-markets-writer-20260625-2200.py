#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-25 22:00 UTC batch.
Topics (checked against recent articles to avoid dupes):
  1. USC / Valter Longo study (Cell Metabolism, 2026) — a low-methionine modified
     Mediterranean diet (LDMM) raised growth hormone, GLP-1 and FGF21, reduced
     frailty and let mice lose fat without losing lean mass; human data tied the
     highest animal-protein (methionine) intake to more obesity and double the
     diabetes rate. Suggests specific amino acids matter more than total protein.
     — lifestyle-health (Distinct from prior plant-based-Mediterranean CVD piece:
      this is the amino-acid / methionine mechanism, not the dietary-pattern epi.)
  2. University of Minnesota School of Nursing (Dereck Salisbury) — of 14 modifiable
     dementia risk factors, six can be addressed through exercise alone; a virtual
     telehealth exercise program for rural adults 45+ worried about memory improved
     fitness in 3 months. — lifestyle-health (Distinct: dementia-prevention framing
      via modifiable risk factors + telehealth access, not the strength/longevity
      mortality studies already covered.)
  3. US FDA SOS to Indian drugmakers for ifosfamide — the US FDA India office asked
     IDMA (June 19) to find Indian makers of the cancer drug ifosfamide amid a US
     shortage from a Baxter site disruption + West Asia supply snarls; Cipla, Zydus,
     Alkem, GLS Pharma named; pharma stocks rallied. — markets-finance (Distinct:
      pharma supply / trade story, none of the recent RBI/IPO/gold/bond pieces.)
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl2200z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl2200z.bin"):
            with open("/tmp/_img_dl2200z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl2200z.bin")
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
# ARTICLE 1: Methionine longevity diet (lifestyle-health)
# ============================================================
articles.append({
    "headline": "It May Not Be How Much Protein You Eat, but One Amino Acid Inside It, a Longevity Study Suggests",
    "subheadline": "A modified Mediterranean diet kept low in the amino acid methionine raised beneficial hormones, trimmed fat without sacrificing muscle and reduced frailty in mice \u2014 while in people, the highest animal-protein intake tracked with more obesity and double the diabetes rate.",
    "slug": "methionine-low-modified-mediterranean-diet-longevity-usc-longo-cell-metabolism-protein-amino-acid-diaspora-20260625-2200",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The protein craze has swept through diaspora kitchens and gyms alike \u2014 whey shakes, paneer-and-chicken meal preps, high-protein 'gym diets' \u2014 so evidence that the type of protein and a single amino acid may matter more than the gram count gives health-conscious Indian-origin families a sharper, more useful lens than 'eat more protein'.",
    "sources": json.dumps([
        {"name": "News-Medical \u2014 'USC study links modified Mediterranean diet to longer lifespan'", "url": "https://www.news-medical.net/news/20260624/USC-study-links-modified-Mediterranean-diet-to-longer-lifespan.aspx"},
        {"name": "Fanti, M., et al. \u2014 'Methionine-supplemented longevity diet increases growth hormone, GLP-1, and FGF21; reduces frailty; and promotes healthspan,' Cell Metabolism (2026)", "url": "https://www.sciencedirect.com/science/article/pii/S1550413126002251"}
    ]),
    "body": """For years the loudest advice in nutrition has been to eat more protein \u2014 for muscle, for satiety, for healthy aging. A new study from the University of Southern California suggests the picture is more subtle. It is not just how much protein you eat, the research argues, but the precise amino acids that protein delivers, and one in particular may hold the key.

## A Diet Built on the Long-Lived

The study, published in the journal *Cell Metabolism*, was led by the longevity researcher Valter Longo and his colleague Martina Fanti. They designed what they call a low-methionine modified Mediterranean diet \u2014 modelled on the eating patterns of famously long-lived populations such as those in traditional Italian and Okinawan communities, but deliberately kept low in methionine, an essential amino acid found in high amounts in animal protein.

Methionine has long interested aging scientists. Restricting it in animals has repeatedly been shown to extend lifespan, but cutting it too far causes problems of its own. The team wanted to find the window in which methionine is low but still sufficient, and to see what such a diet does to the body's metabolic machinery.

## What Happened in the Mice

The results in mice were striking. Animals on the diet showed higher levels of three beneficial signals \u2014 growth hormone, GLP-1 (the same gut hormone that the new generation of weight-loss drugs mimics) and FGF21, a hormone tied to better metabolism. They became less frail with age and lived in better health.

The most surprising finding concerned weight. Mice on the diet could eat as much food, and as many calories, as any other group \u2014 and still lose fat without losing lean muscle mass. But this only held in the narrow band where methionine was low yet adequate. "This challenges the dogma that calorie reduction is necessary to lose weight," Longo said, "but it also tells us that we need to have clear understanding of the mechanisms." Too little methionine caused frailty; too much abolished the benefits entirely.

## The Human Signal

Animal results rarely translate cleanly to people, and the authors are careful on this point. But the team also examined human data, and it pointed in the same direction. Participants who ate the highest levels of animal protein \u2014 and therefore the most methionine and other essential amino acids \u2014 had a higher prevalence of obesity and twice the rate of diabetes compared with those eating little or no animal protein. Strikingly, this held even though the high-animal-protein eaters consumed fewer total calories and otherwise had healthier diets.

"These results indicate that overall protein intake may be less important than specific amino acid intake," Longo said. In other words, the gram count on the back of a protein tub may be the wrong thing to obsess over. The composition of that protein \u2014 plant versus animal, and the amino acids it carries \u2014 may matter more.

A few cautions apply. The strongest results are from mice, and the human findings are observational, showing association rather than proof. The researchers stress that the next step is a controlled clinical trial of the diet in people, which they hope to pursue. This is a promising mechanism, not yet a prescription.

## Why It Matters for the Diaspora

For the Indian diaspora, the timing is pointed. High-protein eating has become something close to gospel in the community's fitness culture, from gym-goers chasing whey shakes to families piling on paneer, eggs and chicken in the belief that more protein is always better. This research complicates that instinct. It suggests that leaning heavily on animal protein \u2014 the richest source of methionine \u2014 may carry metabolic costs, especially for a community already prone to diabetes and central obesity at lower body weights than many other groups.

The encouraging part is how naturally it fits traditional Indian eating. A largely plant-forward diet built around lentils, beans, vegetables, whole grains and modest dairy \u2014 closer to how many households ate a generation ago \u2014 tends to be lower in methionine than a meat-heavy Western plate. The study does not call for cutting protein drastically, which can cause its own harm, but for rethinking its source. For diaspora families navigating between the protein-maximising advice of Western fitness culture and the vegetarian-leaning traditions of home, the message is reassuring: the old way of eating may have been quietly working in their favour all along."""
})

# ============================================================
# ARTICLE 2: Exercise & dementia prevention (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Single Habit \u2014 Regular Exercise \u2014 May Head Off Nearly Half of Dementia Cases, Researchers Say",
    "subheadline": "Of the fourteen lifestyle and environmental factors that shape dementia risk, six can be tackled through exercise alone, University of Minnesota researchers report \u2014 and a virtual program shows even rural adults far from gyms can do it from home.",
    "slug": "exercise-prevent-delay-dementia-six-of-fourteen-risk-factors-university-minnesota-telehealth-rural-diaspora-20260625-2200",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry an elevated, earlier risk of both diabetes and dementia, and aging diaspora parents are often scattered far from family and specialist care \u2014 so a finding that one accessible, no-cost habit, deliverable even by telehealth at home, can address six of dementia's biggest risk factors is unusually relevant to Indian-origin households.",
    "sources": json.dumps([
        {"name": "NBC Palm Springs \u2014 'University of Minnesota Study Shows Exercise Can Prevent or Delay Half of All Dementia Cases'", "url": "https://www.nbcpalmsprings.com/2026/06/24/university-of-minnesota-study-shows-exercise-can-prevent-or-delay-half-of-all-dementia-cases"},
        {"name": "University of Minnesota School of Nursing \u2014 research led by Dereck Salisbury on modifiable dementia risk and telehealth exercise", "url": "https://nursing.umn.edu/"}
    ]),
    "body": """Dementia can feel like a fate written in the genes \u2014 something to dread and little to be done. A growing body of research, and a new effort from the University of Minnesota, pushes back hard on that fatalism. A large share of dementia cases, the researchers argue, are preventable or can be delayed, and one ordinary habit does more of the work than any other: regular physical exercise.

## The Scale of the Problem

The stakes are large. Public-health experts estimate that roughly 42 percent of Americans over the age of 55 will eventually develop some form of dementia, and the number of new cases each year is projected to double between 2020 and 2060. That trajectory has made prevention a national priority, because the health system cannot simply treat its way out of a doubling.

Genetics and age cannot be changed. But according to Dereck Salisbury, an associate professor at the University of Minnesota School of Nursing, an individual's overall risk is heavily shaped by fourteen specific lifestyle and environmental factors that *can* be modified. The crucial insight is how many of them respond to a single intervention. Six of those fourteen risk factors, Salisbury says, can be directly addressed through consistent physical exercise.

## How Movement Protects the Brain

The brain does not exist in isolation from the body, and that is the heart of the explanation. Exercise, Salisbury notes, helps mitigate obesity, high blood pressure, high blood sugar, depression, high cholesterol and physical inactivity itself \u2014 a cluster of conditions that quietly damage the brain's blood supply over the years.

By keeping those conditions in check, regular movement protects vascular health, reduces the chronic, low-grade inflammation linked to cognitive decline, and lowers the odds of the brain aging prematurely. The payoff, researchers emphasise, is not only more years but better ones: more of life lived with a sharp, functioning mind.

## Bringing It Within Reach

A frequent objection to exercise advice is access \u2014 not everyone lives near a gym or a fitness class. Salisbury's team set out to test whether the benefits could be delivered remotely. They focused on adults aged 45 and older who were already worried about their memory, and specifically on people living in rural communities, where distance often makes specialist facilities hard to reach.

Participants were enrolled in a virtual telehealth exercise program and sent the equipment they needed at home \u2014 stationary cycles, heart-rate monitors and blood-pressure cuffs \u2014 so researchers could track their progress through virtual screenings. After three months of structured training, participants showed significant improvements in aerobic fitness. The takeaway was twofold: that a serious exercise intervention can be run entirely from home, and that aerobic work, strength training and mind-body activities each help enhance cognition, executive function and short-term memory.

Two caveats are worth keeping in view. This is prevention and delay, not a cure, and exercise reduces risk rather than eliminating it. And researchers stress that the benefit only materialises if the routine is sustained \u2014 which, they say, means choosing an activity a person genuinely enjoys rather than one they dread. It is never too late to start, they add, but it has to be something you will keep doing.

## Why It Matters for the Diaspora

For Indian-origin families, the message lands on fertile ground. South Asians face an elevated burden of exactly the conditions exercise targets \u2014 diabetes, high blood pressure and heart disease \u2014 often at younger ages and lower body weights than other groups, and these same conditions feed the vascular risk behind much dementia. The community also carries a documented vulnerability to cognitive decline as it ages.

There is a practical dimension too. Many diaspora households are caring, often from a distance, for aging parents who may live far from specialist memory clinics. The telehealth angle of this research is therefore quietly powerful: a structured, monitored exercise routine can be delivered to a parent at home, whether across town or across an ocean, without a single trip to a clinic. None of this requires medication or money \u2014 just consistent movement of a kind the person will actually keep up. In a community that prizes both academic sharpness and family duty, the study reframes a daily walk, a cycle or a strength session as one of the most accessible investments available in a longer, clearer-minded life."""
})

# ============================================================
# ARTICLE 3: US FDA SOS to Indian pharma for ifosfamide (markets-finance)
# ============================================================
articles.append({
    "headline": "America Runs Short of a Cancer Drug \u2014 and Sends an SOS to India's Generic Makers",
    "subheadline": "With the chemotherapy drug ifosfamide in short supply, the US FDA has quietly asked Indian manufacturers to step in. The episode lifted pharma stocks and underscored, once again, the world's reliance on India's drug industry.",
    "slug": "us-fda-sos-indian-pharma-ifosfamide-cancer-drug-shortage-cipla-zydus-alkem-pharma-stocks-nri-investor-20260625-2200",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "It is a vivid reminder of how central India is to the medicines the diaspora and the wider world depend on \u2014 the same Indian generic makers being asked to rescue a US cancer-drug shortage are core holdings in many NRI portfolios, and the episode sits at the centre of the simmering India-US trade conversation.",
    "sources": json.dumps([
        {"name": "LiveMint \u2014 'US FDA sends SOS to Indian drugmakers for critical cancer medicine amid US shortage'", "url": "https://www.livemint.com/companies/news/us-fda-sends-sos-to-indian-drugmakers-for-critical-cancer-medicine-amid-us-shortage-ifosfamide-idma-cipla-zydus-alkem-11718900000000.html"},
        {"name": "The Hindu BusinessLine \u2014 'US cancer drug supply reinforces role of Indian drugmakers, say industry insiders'", "url": "https://www.thehindubusinessline.com/companies/us-cancer-drug-supply-reinforces-role-of-indian-drugmakers-say-industry-insiders/article69730000.ece"},
        {"name": "Trade Brains \u2014 '3 Pharma Stocks Likely to Benefit From the Shortage of Cancer Drugs in the US'", "url": "https://tradebrains.in/3-pharma-stocks-likely-to-benefit-from-the-shortage-of-cancer-drugs-in-the-us/"}
    ]),
    "body": """When the world's richest country runs short of a life-saving medicine, it increasingly turns to the same place: India's pharmaceutical factories. This week offered a textbook example. The US Food and Drug Administration has quietly asked Indian drugmakers to help fill a shortage of a critical cancer drug \u2014 a request that says as much about the global medicine supply chain as it does about any single shortfall.

## An SOS for Ifosfamide

According to two Indian government officials and a document reviewed by *Mint*, the US FDA's India office reached out to the Indian Drug Manufacturers' Association, or IDMA, seeking help identifying companies able to supply ifosfamide, a chemotherapy drug used to treat testicular, bladder and lung cancers. In a communication to its members dated June 19, the IDMA said the FDA was "seeking assistance in identifying potential manufacturers capable of supplying ifosfamide Injection 1 g and/or 3 g to help address an ongoing drug shortage in the US."

The cause is a familiar one for specialised generic drugs, where production is concentrated in just a few hands. A technical disruption at a contract manufacturing site of Baxter International \u2014 the Illinois-based company that is the primary US supplier of ifosfamide \u2014 combined with supply-chain knocks from the conflict in West Asia, left American hospitals short. Officials expect the limited supply to persist through 2026. "It is like an SOS," one industry figure said, given that the drug treats cancer.

## India's Place in the Chain

Indian manufacturers of ifosfamide include Cipla, Zydus Lifesciences, Alkem Laboratories and GLS Pharma, with industry names such as Aurobindo also in the mix; India's oncology and cancer-treatment market is valued at roughly $948 million. The FDA is said to prefer FDA-registered facilities but is also weighing non-registered Indian plants with strong compliance records and proven quality \u2014 a sign of how urgently the gap needs filling.

This is not new territory. During the Covid-19 pandemic, the Trump administration secured supplies of hydroxychloroquine from Indian companies. Years earlier, the FDA leaned on India's Sun Pharma to import a substitute when the cancer drug Doxil ran short. Each episode reinforces a point industry insiders make repeatedly: India is the pharmacy of the world, and when affordable medicines are needed at scale, its generic makers are the ones that step up.

## The Market Reaction

Investors read the request as opportunity. Pharmaceutical stocks rallied, with the Nifty Pharma index outperforming the broader market. Cipla shares rose about 2.4 percent, touching a high of around Rs 1,449. Analysts flagged Cipla, Alkem and Zydus as the names most likely to draw investor attention, even though no company has been formally named as a supplier \u2014 the market is betting on who could win the business.

The episode also fed a broader theme that has supported Indian pharma all week. India's benchmark indices logged their longest weekly winning streak in seven months, and the pharma index gained more than 2 percent over the period, helped both by the FDA outreach and by investor preference for sectors insulated from oil-price and weather risks. For a sector long dogged by US regulatory scrutiny over manufacturing quality, being courted by that same regulator is a notable turn.

## Why It Matters for the Diaspora

There are caveats worth keeping in mind. A single supply request, however symbolically powerful, is not by itself a major earnings driver; the volumes involved are modest against these companies' overall revenue, and the stock moves owe as much to sentiment as to confirmed contracts. The lasting significance is strategic rather than immediate.

For diaspora investors, the story matters on two levels. The companies at its centre \u2014 Cipla, Zydus, Alkem and their peers \u2014 are staples of many NRI portfolios and of India-focused funds, and the episode burnishes the long-term case for Indian pharma as a supplier the world cannot easily do without. It also lands squarely inside the delicate India-US trade conversation: generic drugs have so far been kept outside the scope of US tariffs, and moments like this, when American patients depend on Indian factories, are a quiet reminder of why that exemption exists. For the diaspora, it is a point of pride with a portfolio dimension attached \u2014 the medicines that keep families healthy on both sides of the ocean, and an industry whose strategic value the wider world keeps rediscovering."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["Mediterranean diet healthy food vegetables", "lentils beans legumes plant protein", "fresh vegetables whole grains diet"],
                          ["mediterranean diet healthy food", "lentils beans plant based food"], None),
    articles[1]["slug"]: (["older adults exercise senior fitness", "elderly person walking exercise outdoors", "senior cycling stationary bike fitness"],
                          ["senior exercise older adult fitness", "elderly walking exercise"], None),
    articles[2]["slug"]: (["pharmaceutical manufacturing factory India", "medicine vials injection pharmaceutical", "pharmacy medication tablets pills"],
                          ["pharmaceutical factory medicine production", "medicine vials injection"], None),
}
img_captions = {
    articles[0]["slug"]: "A modified Mediterranean diet kept low in the amino acid methionine was linked to longer healthspan in a new study",
    articles[1]["slug"]: "Researchers say regular exercise can address six of the fourteen modifiable risk factors for dementia",
    articles[2]["slug"]: "The US FDA has asked Indian generic drugmakers to help supply the cancer drug ifosfamide amid a US shortage",
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
