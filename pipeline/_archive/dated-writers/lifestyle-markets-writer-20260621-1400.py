#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-21 14:00 UTC batch.
Topics:
  1. Food order / macronutrient sequencing — eating fibre and protein before
     carbohydrates blunts post-meal blood-sugar spikes (continuous glucose
     monitoring study, healthy adults + type 2 diabetics) — lifestyle-health
  2. Weakening muscles may fuel cancer growth — Duke-NUS study links sarcopenia
     to loss of a protective microRNA (miR-7a-5p) in muscle's extracellular
     vesicles; exercise can reactivate the anti-cancer signal — lifestyle-health
  3. India's tax tribunal rules NRE-account credits from overseas earnings
     cannot be taxed as "unexplained money" — a quiet but important win for
     the diaspora that banks abroad and remits home — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0621n.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0621n.bin"):
            with open("/tmp/_img_dl0621n.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0621n.bin")
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
# ARTICLE 1: Food order / macronutrient sequencing (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Order You Eat Your Food May Matter Almost as Much as What's On the Plate, a Glucose-Monitor Study Finds",
    "subheadline": "Tracking real meals with continuous glucose monitors, researchers found that eating fibre and protein before the carbohydrates flattened the post-meal blood-sugar spike \u2014 in healthy people and those with type 2 diabetes alike.",
    "slug": "food-order-fibre-protein-before-carbs-lowers-post-meal-blood-sugar-cgm-study-diaspora-20260621-1400",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The Indian plate is built around rice and roti, and South Asians carry an outsized, earlier-onset risk of type 2 diabetes \u2014 so a free, no-deprivation tweak like eating the dal, sabzi and salad before the rice offers diaspora families a way to keep their food and still blunt the blood-sugar spikes that drive that risk.",
    "sources": json.dumps([
        {"name": "Nutrients \u2014 Modulatory effects of ingesting dietary fiber and protein before carbohydrates on postprandial interstitial glucose responses", "url": "https://pubmed.ncbi.nlm.nih.gov/"},
        {"name": "Scientific Reports \u2014 Positive impact of a 10-min walk immediately after glucose intake on postprandial glucose levels", "url": "https://www.nature.com/srep/"},
        {"name": "Diabetes Care / Weill Cornell \u2014 food order and postprandial glucose research", "url": "https://diabetesjournals.org/care"}
    ]),
    "body": """For decades, dietary advice has fixated on a single question: what should be on the plate? Count the calories, watch the carbs, pick the right fats. A growing line of research suggests we have been ignoring something almost as powerful and far easier to change \u2014 not what we eat, but the order in which we eat it.

## What the Study Found

Researchers fitted healthy adults and people with type 2 diabetes with continuous glucose monitors, the same coin-sized sensors that diabetics increasingly wear to track blood sugar minute by minute. Instead of a controlled lab meal, participants ate normally and logged what they consumed and when, while the sensors captured how their glucose responded to ordinary daily food.

The pattern was clear. When people ate dietary fibre or protein before the carbohydrates \u2014 vegetables or a portion of protein first, the rice or bread after \u2014 their post-meal blood-sugar rise was significantly smaller than when they ate the same carbohydrates on their own. The effect was strongest in the first two hours after eating, the window when glucose normally spikes hardest, and it was most pronounced when fibre and protein were eaten together before the starch.

Crucially, the benefit showed up in both healthy participants and those with diabetes. Nothing was added to the meal and nothing was taken away. The only thing that changed was the sequence.

## Why Sequence Matters

The biology is surprisingly intuitive. Eating fibre and protein first slows down how quickly the stomach empties its contents into the small intestine, so the sugars from the carbohydrates trickle into the bloodstream rather than flooding in. Protein and fibre also prompt the gut to release hormones called incretins, which prime the body to handle the incoming glucose, and they sharpen the insulin response that clears sugar from the blood.

The result is the same meal, the same calories, the same carbohydrates \u2014 but a gentler, flatter glucose curve. Repeated meal after meal, day after day, those smaller spikes add up. Sharp, repeated surges in blood sugar are an independent driver of the blood-vessel damage behind heart disease and the slow slide toward type 2 diabetes, so smoothing them out is not a cosmetic win.

## A Companion Trick: The Post-Meal Walk

The food-order finding sits alongside a second, equally low-effort strategy that researchers keep confirming: moving after you eat. Separate work using glucose monitors has shown that even a short walk soon after a meal blunts the blood-sugar rise, with one study finding a 10-minute walk taken immediately after eating worked about as well as a much longer walk taken later. The evening meal, often the largest and the one most likely to be followed by sitting on the sofa, is where a brief stroll appears to pay off most.

Together, the two habits point in the same direction. The most accessible tools for steadying blood sugar may not be on the pharmacy shelf at all \u2014 they are the order of the plate and a few minutes of movement.

## The Honest Caveats

These were relatively small, real-world studies, and observational data cannot prove cause and effect on its own. The size of the benefit varied from person to person, and food order is no substitute for the basics \u2014 overall diet quality, weight, medication where it is needed, and a doctor's guidance for anyone managing diabetes. No one should read this as licence to pile on the rice as long as the salad goes first.

But as a free, side-effect-free tweak that asks for no special foods and no willpower around portions, eating fibre and protein before the starch is about as easy a habit as nutrition science offers.

## Why It Matters for the Diaspora

Few communities stand to gain more than the Indian diaspora. South Asians develop type 2 diabetes earlier, at lower body weights, and in greater numbers than most other populations \u2014 a genetic and metabolic vulnerability that does not disappear when families move to the United States, Britain or Canada. And the traditional plate is carbohydrate-heavy by design: rice, roti, idli, dosa, poha and parathas anchor most meals.

The beauty of the food-order finding is that it asks for no surrender of that food. A typical thali already contains the answer \u2014 dal, vegetables, paneer or curd, salad and rice. The only change is to start with the dal, sabzi and salad, eat the protein, and leave the rice and roti for the end, rather than mixing everything from the first bite. Add a 10-minute walk after dinner, and a diaspora family can hold on to the cuisine that anchors its identity while quietly defusing one of its biggest long-term health risks. For a community that often resists giving up its food in the name of health, that is a rare and welcome kind of advice."""
})

# ============================================================
# ARTICLE 2: Weakening muscles may fuel cancer growth (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Weakening Muscles May Quietly Make It Easier for Cancer to Grow, New Research Suggests \u2014 and Exercise May Reverse It",
    "subheadline": "A Duke-NUS study finds that as muscles lose strength with age, they stop sending out a protective molecular signal that helps hold tumours in check \u2014 and that exercise can switch that signal back on.",
    "slug": "weakening-muscles-sarcopenia-cancer-growth-mir-7a-5p-exercise-duke-nus-study-diaspora-20260621-1400",
    "category": "lifestyle-health",
    "vertical": "cancer-prevention",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians tend to carry less muscle and more fat at any given weight \u2014 the so-called 'thin-fat' body type \u2014 which leaves many in the diaspora vulnerable to age-related muscle loss even when the scale looks fine, making the study's message that strength training protects against more than just frailty especially relevant.",
    "sources": json.dumps([
        {"name": "Knowridge \u2014 Weakening Muscles May Encourage Cancer Growth", "url": "https://knowridge.com/2026/06/weakening-muscles-may-encourage-cancer-growth/"},
        {"name": "Duke-NUS Medical School \u2014 research on muscle extracellular vesicles and tumour growth", "url": "https://www.duke-nus.edu.sg/"},
        {"name": "World Health Organization \u2014 Physical activity fact sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/physical-activity"}
    ]),
    "body": """Doctors have long noticed that patients with advanced cancer often have wasted, weakened muscles, and assumed the disease was simply eating away at the body. New research turns that assumption on its head, suggesting the relationship may run the other way too: weakening muscle may itself help create the conditions in which cancer grows.

## Muscle as a Messenger

The study, led by scientists at Duke-NUS Medical School in Singapore, focused on a surprising idea \u2014 that muscle is not just an engine for movement but an organ that talks to the rest of the body. It does so partly through tiny packages called extracellular vesicles, microscopic bubbles that muscle cells release into the bloodstream carrying molecular messages to distant tissues.

Healthy muscles, the researchers found, release large numbers of these vesicles. Muscles affected by sarcopenia \u2014 the gradual loss of muscle mass and strength that comes with age \u2014 release far fewer. And the contents of the vesicles change with age too. In particular, ageing muscle carries lower levels of a molecule called miR-7a-5p, one of a family of genetic regulators known as microRNAs that fine-tune which proteins cells make.

That detail matters because earlier work has suggested miR-7a-5p plays a role in restraining tumour growth. As muscles age and pump out fewer vesicles carrying this protective molecule, the body's anti-cancer signalling appears to weaken \u2014 quietly tilting the environment in a tumour's favour.

## The Encouraging Part

If the story stopped there, it would be a bleak one: muscles fade with age, and there is nothing to do about it. But the researchers found the signalling pathway that drives vesicle release, which becomes sluggish with age, can be switched back on \u2014 through exercise.

That gives the findings a hopeful, practical edge. Exercise has long been linked to a lower risk of several cancers, but the reasons have been fuzzy. This study offers one concrete mechanism: physical activity may help muscles keep producing the protective molecular messages that hold tumour growth in check. It is not just that strong muscles let you climb stairs and carry groceries; they may be actively sending out anti-cancer signals, and movement keeps that signal alive.

## Why It Fits a Bigger Picture

The work dovetails with a wave of recent research repositioning muscle as central to healthy ageing. Strength has been tied to longer life, better brain health, and lower risk of falls and metabolic disease. Doctors involved in the study stressed that maintaining healthy muscle through both aerobic and resistance exercise matters not only for independence and mobility but for overall health \u2014 and now, potentially, for cancer resistance.

It also reframes a common clinical sight. The muscle wasting seen in cancer patients has usually been treated as a consequence of the disease. This research suggests low muscle mass may be part of a vicious cycle, both a result of illness and a factor that makes the body more hospitable to it.

## The Caveats

This is early-stage science, much of it worked out in laboratory and animal models, and a single molecule is never the whole story of something as complex as cancer. The findings do not mean exercise prevents cancer, or that lifting weights can treat it. They illuminate one biological pathway among many, and a great deal more work is needed before anyone can translate miR-7a-5p into a therapy.

What the study does reinforce is a message that is already well supported and costs nothing: keeping muscle on the body, and keeping it active, is one of the most powerful things a person can do for long-term health.

## Why It Matters for the Diaspora

For people of South Asian origin, the finding lands on a known vulnerability. Research has repeatedly shown that South Asians tend to carry less muscle and more body fat at any given weight than many other groups \u2014 the so-called 'thin-fat' phenotype \u2014 and often store that fat around the organs, where it does the most metabolic harm. A person of Indian origin can look slim, register a normal weight, and still be carrying relatively little muscle.

That makes age-related muscle loss a quiet risk for many in the diaspora, one the bathroom scale will not reveal. The cultural emphasis on cardio, yoga and walking, while valuable, often leaves resistance training out entirely, especially for women and older adults. This study adds another reason to pick up the weights, the resistance bands, or even bodyweight exercises at home: building and keeping muscle may be protecting far more than strength. For a community already primed for metabolic disease, treating muscle as something to actively maintain \u2014 not just a youthful luxury \u2014 may be one of the smarter long-term investments in health."""
})

# ============================================================
# ARTICLE 3: ITAT rules NRE credits from overseas earnings not taxable (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Tax Tribunal Says Money NRIs Send Into Their NRE Accounts From Foreign Salaries Cannot Be Taxed as 'Unexplained' Income",
    "subheadline": "An income-tax appellate ruling has deleted a tax demand against a non-resident Indian, holding that once funds in an NRE account are shown to come from foreign earnings, the tax department cannot treat them as unexplained money \u2014 a quiet but meaningful protection for the diaspora.",
    "slug": "itat-nre-account-foreign-salary-credits-not-unexplained-income-tax-ruling-nri-investor-20260621-1400",
    "category": "markets-finance",
    "vertical": "tax",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Millions of NRIs route their overseas salaries into NRE accounts in India to support family, buy property or invest \u2014 and the fear of a tax notice questioning those inflows is real, so a tribunal confirming that genuinely foreign-earned money parked in an NRE account is not taxable removes a recurring anxiety for the diaspora.",
    "sources": json.dumps([
        {"name": "Taxscan \u2014 NRI's NRE Account Credits Linked to Overseas Earnings Cannot Be Taxed as Unexplained Money: ITAT Deletes Addition", "url": "https://www.taxscan.in/"},
        {"name": "Income Tax Appellate Tribunal \u2014 Rahulkumar Narshibhai Patel vs Income Tax Officer (ITAT Ahmedabad)", "url": "https://itat.gov.in/"},
        {"name": "Reserve Bank of India \u2014 NRE / FCNR(B) account rules for non-residents", "url": "https://www.rbi.org.in/"}
    ]),
    "body": """For the millions of Indians who work abroad and send money home, one anxiety recurs every time the tax season comes around: could the Indian tax department question the money flowing into their accounts back home? A recent ruling from India's income-tax tribunal offers a reassuring answer \u2014 if the money is genuinely earned overseas, it cannot simply be taxed as unexplained income.

## What the Tribunal Decided

The case, heard by the Income Tax Appellate Tribunal (ITAT), involved a non-resident Indian whose accounts in India had received credits the tax officer treated as suspicious. The department invoked Section 69A of the Income Tax Act \u2014 the provision used to tax money a person cannot satisfactorily explain \u2014 and added the sums to his taxable income, including an amount of ₹5.52 lakh tied to one of his bank accounts.

The taxpayer argued that the credits in his Non-Resident External (NRE) accounts were simply his foreign salary, remitted from his earnings abroad and routed through an overseas bank. The tribunal agreed. It noted that the assessing officer had already accepted that a substantial portion of the funds originated from foreign salary remittances. Once the source of money in an NRE account is established as foreign earnings, the bench held, no addition under Section 69A is warranted, and it deleted the ₹5.52 lakh demand.

The ruling did not give a blanket pass to every inflow \u2014 a separate, larger balance was sent back to the assessing officer for fresh examination with complete bank details \u2014 but the principle it affirmed is what matters for the wider diaspora.

## Why an NRE Account Is Special

The decision rests on the basic logic of how India taxes non-residents. India broadly taxes residents on their global income, but non-residents are taxed only on income earned or received in India. Salary earned abroad for work done abroad is foreign income, outside India's tax net for an NRI.

The NRE account exists precisely to hold such money. It is designed for non-residents to park their foreign earnings in India in rupees, is freely repatriable, and the interest it earns is exempt from Indian tax for as long as the holder remains a non-resident. Money flowing into an NRE account from overseas earnings is, by its nature, already-taxed-or-exempt foreign income \u2014 not fresh Indian income to be taxed again.

The tribunal's contribution was to push back against a tendency to treat unexplained reconciliation gaps as taxable income. A mismatch in paperwork, it held, is not the same as undisclosed income when the underlying source is clearly foreign salary.

## The Practical Lesson: Keep the Paper Trail

If there is a single takeaway for NRIs, it is the importance of documentation. The taxpayer won because he could trace the money back to foreign salary routed through an identifiable overseas bank. The tribunal's reasoning turned on that traceability.

Tax advisers have long urged the diaspora to keep clean records \u2014 foreign salary slips, overseas bank statements, and a clear remittance trail showing money moving from an overseas account into the NRE account. Mixing foreign earnings with domestic income, or routing money through informal channels, is what invites scrutiny and turns a legitimate inflow into an argument with the tax department.

## Why NRIs Should Care

This is not an abstract legal nicety. NRE accounts are the financial backbone of diaspora life. Indians working in the Gulf, the United States, Britain, Canada, Singapore and beyond use them to send money to ageing parents, pay for property, fund children's education in India, and invest in everything from fixed deposits to mutual funds. The sums are enormous \u2014 India consistently ranks as the world's largest recipient of remittances, taking in well over $100 billion a year, much of it through exactly these accounts.

For many of those senders, a notice from the Indian tax department questioning their inflows is a genuine fear, especially for first-generation migrants unfamiliar with the fine print of cross-border taxation. The ITAT ruling confirms what the law already intends: money you earned abroad and brought into your NRE account is yours, not taxable Indian income, provided you can show where it came from.

The decision also lands at a moment when India is actively courting diaspora money \u2014 the central bank has just rolled out incentives to pull more foreign-currency deposits into the banking system. A tax regime that treats legitimate NRI inflows fairly is part of that same bargain. The practical homework for the diaspora is unglamorous but vital: bank abroad cleanly, document the remittance, and keep the trail. Do that, and the law is on your side."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["Indian thali meal vegetables rice", "healthy salad plate vegetables", "fresh vegetables lentils healthy food"],
                          ["healthy meal vegetables plate", "salad bowl vegetables"], None),
    articles[1]["slug"]: (["man strength training dumbbells gym", "older adult resistance exercise weights", "person lifting weights fitness"],
                          ["strength training weights", "senior exercise fitness gym"], None),
    articles[2]["slug"]: (["Income Tax Department India building", "Reserve Bank of India building Mumbai", "Indian rupee currency notes money"],
                          ["tax documents calculator finance", "money currency financial documents"], None),
}
img_captions = {
    articles[0]["slug"]: "Eating fibre and protein such as dal, vegetables and salad before the rice and roti blunted post-meal blood-sugar spikes in a glucose-monitor study",
    articles[1]["slug"]: "A Duke-NUS study suggests maintaining muscle through resistance exercise may help keep the body's anti-cancer signalling active with age",
    articles[2]["slug"]: "India's tax tribunal ruled that foreign-salary credits in an NRI's NRE account cannot be taxed as unexplained income",
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
