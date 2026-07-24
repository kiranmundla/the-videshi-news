#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-26 10:00 UTC batch.
Topics (checked against recent articles to avoid dupes):
  1. USC "longevity diet" / methionine study — Valter Longo (USC Leonard Davis),
     w/ Toronto + Harvard. Plant-and-fish, low-protein diet + a small but
     sufficient amount of the amino acid methionine extended healthspan, cut
     frailty and fat mass in mice; human data on 200,000+ people showed less
     obesity/T2D on more plant-focused diets. Published in Cell Metabolism.
     Angle: it's the amino-acid COMPOSITION (methionine), not protein quantity
     or calorie cutting. — lifestyle-health
     (DISTINCT from prior plant-based-Mediterranean-CVD and flavanol pieces:
      this is the methionine/protein-quality + frailty/longevity angle.)
  2. Five-minute movement breaks every hour — Keith Diaz (Columbia), ~11,500
     adults in NPR 21-day challenge; 5-min walking breaks at 30/60/120-min
     intervals all cut fatigue and lifted mood, hourly was the sweet spot, and
     work performance ticked UP, not down. Published in British Journal of
     Sports Medicine. — lifestyle-health
     (DISTINCT: a workplace-sitting/micro-movement & mood study, none of the
      recent diet/sleep/strength-training epi pieces cover movement snacks.)
  3. Meta's $900m CRED investment + Kunal Shah named global head of WhatsApp.
     ~20% stake, $4.5bn post-money valuation (Rs ~43,239 cr), ~$500m primary +
     ~$400m secondary; Meta gets no CRED customer data; Shah keeps ~20% stake,
     leaves exec role; Miten Sampat interim CEO; CRED eyes eventual IPO. The
     real story = WhatsApp's India-first payments/superapp push. — markets-finance
     (DISTINCT: prior finance pieces were NSE IPO, IRFC OFS, rupee/FCNR-B, gold,
      SIP flows, bonds, GIFT City — none cover the Meta-CRED deal.)
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1000.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1000.bin"):
            with open("/tmp/_img_dl1000.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1000.bin")
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
# ARTICLE 1: USC longevity diet / methionine (lifestyle-health)
# ============================================================
articles.append({
    "headline": "It May Not Be How Much Protein You Eat, but One Amino Acid \u2014 a New Longevity-Diet Study Finds",
    "subheadline": "A mostly plant-and-fish diet, kept low in protein but topped up with a small, sufficient amount of methionine \u2014 the amino acid in eggs, meat and dairy \u2014 extended healthy lifespan and cut frailty and fat in a USC study, challenging the idea that cutting calories is the key to staying lean.",
    "slug": "usc-longevity-diet-methionine-low-protein-plant-fish-valter-longo-cell-metabolism-frailty-healthspan-diaspora-20260626-1000",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Many Indian-origin households already eat a largely vegetarian, plant-forward diet \u2014 exactly the base this 'longevity diet' is built on \u2014 yet the same group faces high rates of frailty, sarcopenia and early diabetes, so a study showing that a touch of the right protein (a little fish, egg or dairy for methionine) rather than more protein or fewer calories is what protects muscle and lifespan speaks directly to how NRI families can fine-tune a diet they mostly follow already.",
    "sources": json.dumps([
        {"name": "News-Medical \u2014 'USC study links modified Mediterranean diet to longer lifespan'", "url": "https://www.news-medical.net/news/20260623/USC-study-links-modified-Mediterranean-diet-to-longer-lifespan.aspx"},
        {"name": "Fanti, M., et al. (2026), 'Methionine-supplemented longevity diet increases growth hormone, GLP-1, and FGF21; reduces frailty; and promotes healthspan', Cell Metabolism", "url": "https://www.sciencedirect.com/science/article/pii/S1550413126002251"}
    ]),
    "body": """For years the loudest debates in nutrition have been about quantity \u2014 how many calories, how many grams of protein, how big the plate. A new study from the University of Southern California suggests the more important question may be one of quality: not how much protein you eat, but which building blocks it contains, and in particular a single amino acid.

## A "Longevity Diet," With One Crucial Tweak

The research, published in the journal *Cell Metabolism*, was led by Valter Longo of the USC Leonard Davis School of Gerontology, working with colleagues at the University of Toronto and Harvard University. Longo has spent much of his career studying the low-protein, plant-focused Mediterranean diet that anchors some of the world's longest-lived populations.

But those populations carry a paradox. They live long lives, yet they also show high rates of frailty \u2014 the loss of muscle and resilience that makes old age fragile. Plant foods contain lower amounts of essential amino acids than animal products, and Longo suspected that shortfall was part of the problem. So his team designed a "longevity diet" that was largely vegan or vegetarian, with some fish added, and supplemented with a small but sufficient amount of one essential amino acid: methionine, found in eggs, meat and dairy.

## What the Mice Showed

To test it, the researchers fed groups of 20-month-old mice one of four diets: a standard diet; a Western diet high in fat and sugar; a low-carbohydrate ketogenic diet; or the low-protein, methionine-supplemented longevity diet, which the team labelled LDMM.

The mice on the longevity diet fared markedly better. They lived a longer *healthspan* \u2014 the portion of life spent in good health \u2014 and showed reduced fat mass and less frailty than the others. Tests also revealed several markers of better heart-and-metabolic health, including higher levels of signalling molecules such as GLP-1, the same gut hormone that the new generation of weight-loss drugs mimics.

One finding stood out. Mice on the longevity diet could eat as much food and as many calories as any other group and still lose fat without losing lean muscle \u2014 but only when methionine was kept low yet sufficient. "This challenges the dogma that calorie reduction is necessary to lose weight," Longo said. Too little methionine, though, caused frailty, while too much erased the benefits entirely. The sweet spot was narrow.

"What really impressed us was how modulating just a single amino acid, methionine, in the longevity diet could produce such dramatic metabolic changes," said Maura Fanti, the study's first author. "It points to the idea that amino acid composition, not just overall protein quantity, may be the target."

## The Human Signal

The mouse work was paired with an analysis of existing diet-and-health data on more than 200,000 people. There, the team found echoes of the same pattern: people on more plant-focused diets had less obesity and Type 2 diabetes. Strikingly, those who ate the most animal protein \u2014 and therefore the most methionine and other essential amino acids \u2014 had a higher prevalence of obesity and twice the rate of diabetes as those eating little to no animal protein, even though the heavy meat-eaters consumed fewer calories overall.

A note of caution is essential. The core experiment was in mice, and the metabolic pathways involved are regulated differently in humans. The human data are observational, showing associations rather than proof of cause. Longo and Fanti say the next step is a controlled clinical trial of the diet in people; until then, this is a promising signal, not a prescription.

## Why It Matters for the Diaspora

For Indian-origin families, the study lands on familiar ground. A largely vegetarian, plant-forward table is already the norm in many diaspora homes \u2014 the very foundation this longevity diet is built upon. Yet South Asians also carry an outsized burden of early diabetes, central fat and, in older age, frailty and muscle loss.

The takeaway is one of calibration rather than overhaul. The research suggests the goal is not to pile on protein powders or chase high-protein fads to fight frailty, nor to slash calories to stay lean, but to keep protein modest and plant-based while ensuring a small, steady source of the right amino acids \u2014 a little fish, egg, dahi or paneer woven into an otherwise plant-heavy diet. For a community that already eats close to the blueprint, the message is encouraging: the longevity diet may be less a foreign import than a familiar plate, seasoned with a touch more precision."""
})

# ============================================================
# ARTICLE 2: Five-minute movement breaks (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Five Minutes Every Hour: A Simple Movement Habit Lifted Mood and Cut Fatigue, a Study Finds",
    "subheadline": "Short walking breaks scattered through the workday eased fatigue and brightened mood in nearly 11,500 adults \u2014 and, contrary to the fear that stepping away hurts output, work performance edged up rather than down, researchers report.",
    "slug": "five-minute-movement-breaks-hourly-mood-fatigue-columbia-keith-diaz-bjsm-11500-adults-sitting-diaspora-20260626-1000",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "A large share of the Indian diaspora works in desk-bound technology, finance and professional jobs where ten-hour sitting days are routine, layered on a genetic predisposition to early heart disease and diabetes \u2014 so a study showing that five-minute walking breaks an hour, with no gym and no lost productivity, can lift mood and break up dangerous sitting offers NRI knowledge workers a free, frictionless lever for both mind and metabolism.",
    "sources": json.dumps([
        {"name": "Drugs.com / HealthDay \u2014 'Even 5-Minute Movement Breaks Can Boost Your Mood And Fight Fatigue'", "url": "https://www.drugs.com/news/even-5-minute-movement-breaks-boost-mood-fight-fatigue-125000.html"},
        {"name": "Diaz, K., et al. (2026), movement-break study of an NPR 21-day challenge, British Journal of Sports Medicine", "url": "https://bjsm.bmj.com/"}
    ]),
    "body": """Most advice about exercise asks for a commitment many people feel they cannot make: a gym membership, a 30-minute block, a change of clothes. A new study offers a far gentler bargain. Five minutes of walking, once an hour, may be enough to lift your mood, ease fatigue and break up the long stretches of sitting that quietly undermine health \u2014 without denting your work.

## A Real-World Test

The study, published in the *British Journal of Sports Medicine*, was led by Keith Diaz of the Columbia University Medical Center in New York. His team analysed data from nearly 11,500 adults who took part in a 21-day movement challenge organised by National Public Radio in the United States.

Participants were asked to take five-minute walking breaks at one of three cadences \u2014 every 30, 60 or 120 minutes \u2014 throughout their day. Each night, they completed surveys rating their mood, fatigue, and how their workday had gone.

The pattern was consistent across the board. Fatigue fell, low mood eased, and good mood rose, no matter which schedule people followed. All three rhythms also proved practical and easy to slot into a normal day, which matters: the best health habit is the one people actually keep.

## The Hourly Sweet Spot

When the researchers compared the schedules, hourly breaks stood out. Taking five minutes to move every 60 minutes struck the best balance between being effective and being realistic to sustain \u2014 frequent enough to deliver benefits, not so frequent as to feel disruptive.

The most reassuring finding addressed a fear that keeps many desk workers glued to their chairs: that stepping away will hurt their output. The data pointed the other way. Short movement breaks did not undermine work performance and, on average, produced small but favourable gains \u2014 improvements of roughly 4 to 7 percent in engagement and 1 to 3 percent in performance.

"Our findings counter this perception," the researchers wrote, referring to the worry that breaks cost productivity. They concluded that movement breaks are "implementable and effective," and argued they deserve a place as a public-health strategy, not just personal wellness advice.

## Why Sitting Is the Quiet Risk

The backdrop to the study is the growing body of evidence that prolonged sitting is independently harmful, even for people who exercise. Long, unbroken hours in a chair are linked to higher risks of heart disease, Type 2 diabetes and early death, and a brisk evening workout does not fully cancel out a ten-hour sedentary day. The appeal of "movement snacks" \u2014 tiny, repeated bursts of activity \u2014 is that they interrupt that sitting throughout the day rather than trying to make up for it all at once.

A few caveats apply. The participants volunteered for a movement challenge, so they may have been more motivated than the average worker, and the mood and performance measures were self-reported. The study tracked short-term effects over three weeks rather than long-term health outcomes. Still, the simplicity and the scale of the benefit are hard to dismiss.

## Why It Matters for the Diaspora

For the Indian diaspora, the finding is unusually well-targeted. A large proportion of NRIs work in the desk-bound professions \u2014 software, finance, consulting, medicine, academia \u2014 where the workday is measured in hours of screen time and the chair barely moves. That sedentary load sits atop a well-documented South Asian vulnerability to heart disease and diabetes that strikes earlier and at lower body weights than in many other groups.

What this study offers that community is a habit with almost no barrier to entry. It costs nothing, needs no equipment or gym, fits inside a packed workday, and \u2014 crucially for the ambitious \u2014 appears to help rather than hurt productivity. A five-minute walk to refill a water bottle, a lap of the floor between meetings, a few minutes of stairs each hour: for diaspora knowledge workers weighing how to protect both their hearts and their focus, the prescription may be as small as setting an hourly reminder to stand up and move."""
})

# ============================================================
# ARTICLE 3: Meta's $900m CRED deal + Kunal Shah to WhatsApp (markets-finance)
# ============================================================
articles.append({
    "headline": "Meta Bets $900 Million on an Indian Fintech \u2014 and Hands an Indian Founder the Keys to WhatsApp",
    "subheadline": "Meta is investing about $900 million in Bengaluru-based CRED at a $4.5 billion valuation and has named its founder, Kunal Shah, the global head of WhatsApp \u2014 a twin move that signals how central India has become to the messaging giant's push into payments.",
    "slug": "meta-900-million-cred-investment-kunal-shah-whatsapp-head-4-5-billion-valuation-india-payments-superapp-nri-investor-20260626-1000",
    "category": "markets-finance",
    "vertical": "tech",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "WhatsApp is the default communication tool binding the Indian diaspora to family back home, and the elevation of an Indian fintech founder with no Silicon Valley pedigree to run it \u2014 alongside a near-billion-dollar bet on an Indian startup \u2014 is both a marker of diaspora ascent in Big Tech leadership and a sign that the payments and commerce features NRIs use to send money and shop across borders are about to be reimagined from an Indian playbook.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 'Indian fintech firm CRED to raise $900 million from Meta at $4.5 billion valuation'", "url": "https://www.reuters.com/world/india/indian-fintech-firm-cred-raise-900-million-meta-45-billion-valuation-2026-06-22/"},
        {"name": "Reuters \u2014 \"WhatsApp's pick of Indian fintech founder signals scale of payment ambitions\"", "url": "https://www.reuters.com/technology/whatsapp-pick-indian-fintech-founder-kunal-shah-2026-06-23/"},
        {"name": "The Hindu BusinessLine \u2014 'Kunal Shah to lead WhatsApp as Meta pumps $900 mn into CRED'", "url": "https://www.thehindubusinessline.com/info-tech/kunal-shah-to-lead-whatsapp-as-meta-pumps-900-mn-into-cred/article69720000.ece"}
    ]),
    "body": """Meta has made two moves at once, and together they say a great deal about where it sees its future. The company is investing roughly $900 million in CRED, the Bengaluru-based credit-card and fintech startup, and it has named CRED's founder, Kunal Shah, the new global head of WhatsApp. One deal puts Meta's money into India; the other puts an Indian at the controls of the world's most widely used messaging app.

## The Structure of the Deal

Meta's investment values CRED at about $4.5 billion on a post-money basis \u2014 roughly Rs 43,239 crore \u2014 in exchange for a stake of around 20 percent. The financing is a mix: by most accounts about $500 million is fresh primary capital injected into CRED to fund growth, while roughly $400 million is a secondary purchase of shares from existing investors such as Peak XV and Tiger Global, letting early backers book returns.

Two details stand out. Meta said it will not receive access to CRED's customer data despite becoming a strategic investor \u2014 an effort to pre-empt the privacy and competition concerns that shadow any Big Tech move into Indian finance. And the $4.5 billion price tag, while a strong number, sits below CRED's 2022 peak of around $6.4 billion, marking a recovery from a funding-winter low near $3.5 billion rather than a fresh all-time high.

Shah, 47, will keep his roughly 20 percent stake in CRED but step away from running it. Miten Sampat, who has overseen strategy and finance at the company since 2020, takes over as interim chief executive, and CRED is reported to be preparing a longer-term management structure ahead of an eventual public listing.

## Why WhatsApp Wanted Him

The leadership choice is the more telling half of the story. Kunal Shah built CRED \u2014 a platform that rewards users for paying credit-card bills on time and now processes a large share of India's card payments \u2014 into one of the country's most prominent fintech names, without an engineering degree or a Silicon Valley resume. Meta's chief product officer, Chris Cox, said the company wanted a leader with "an intuitive grasp of the immense, global product potential for WhatsApp," and praised Shah's "entrepreneurial energy."

The subtext is monetisation. WhatsApp has more than 500 million users in India, its largest market, yet it has long struggled to turn that vast reach into revenue. WhatsApp Payments launched in India but never achieved the scale of rivals PhonePe and Google Pay. Industry watchers expect India to become the testing ground for new payments, advertising and business services under Shah, with the lessons exported to other emerging markets such as Brazil and Indonesia. The ambition, in short, is to turn a messaging app into a "superapp" \u2014 the model that has reshaped digital life across much of Asia.

## A Word of Caution

For all the fanfare, the bet carries real risk. WhatsApp's payments efforts have stumbled before, and India's regulators are wary of Big Tech extending its grip over the payments rails; there have already been calls to scrutinise the deal. The structure \u2014 part of the money going to existing investors rather than the business \u2014 and the valuation still below its peak are reminders that this is a maturing startup finding a strategic anchor, not a company at the start of an explosive run. The promise of monetising WhatsApp is enormous; so is the difficulty, which is precisely why it has stayed unrealised for so long.

## Why It Matters for the Diaspora

Few products are woven as tightly into diaspora life as WhatsApp. It is the thread connecting NRIs to parents, siblings and friends across continents, the channel for video calls home and the quiet logistics of cross-border family life. The prospect of an Indian founder shaping its next decade carries genuine symbolism \u2014 another marker of how far the diaspora has climbed in the leadership ranks of global technology, joining the Indian-origin chiefs already running Google, Microsoft and others.

The practical stakes matter too. If Shah succeeds in building payments and commerce into WhatsApp, the app that diaspora families already live in could become the place they also send money, shop and transact across borders \u2014 functions NRIs juggle today across a patchwork of services. For diaspora investors, the deal is also a signal worth reading: India is no longer merely a market for Western tech to sell into, but a source of the leadership and the playbook those companies now want to follow."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["Mediterranean diet vegetables fish healthy food", "fresh vegetables fish plate healthy", "salmon vegetables plate meal"],
                          ["mediterranean diet healthy food fish vegetables", "healthy plant based meal fish"], None),
    articles[1]["slug"]: (["person walking office workplace", "office worker walking break", "people walking outdoors exercise"],
                          ["person walking break office", "walking outdoors fitness"], None),
    articles[2]["slug"]: (["WhatsApp smartphone screen app", "smartphone messaging app screen", "mobile phone apps screen"],
                          ["whatsapp smartphone screen", "mobile payment app phone"], "Kunal Shah"),
}
img_captions = {
    articles[0]["slug"]: "A plant-and-fish Mediterranean-style diet, kept low in protein, was at the heart of the USC longevity study",
    articles[1]["slug"]: "Five-minute walking breaks scattered through the day eased fatigue and lifted mood, researchers found",
    articles[2]["slug"]: "Meta is investing about $900 million in Indian fintech CRED and has named its founder to lead WhatsApp",
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
