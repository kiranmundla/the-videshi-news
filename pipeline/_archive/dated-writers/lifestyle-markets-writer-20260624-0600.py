#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-24 06:00 UTC batch.
Topics (checked against last-3-day articles to avoid dupes):
  1. Supervised Nordic walking cut depression symptoms within five weeks in a
     randomized trial of 64 adults with moderate-to-severe depression — the
     fastest gains came in the first half and among the most severely depressed.
     (Journal of Affective Disorders) — lifestyle-health
  2. Ultra-processed foods linked to declining male fertility — a Cell Metabolism
     controlled-feeding study (43 men) found a UPF diet worsened body fat, lipids
     and sperm-related hormones in just three weeks, independent of calories,
     pointing to industrial processing itself. — lifestyle-health
  3. Tata Motors' investor day: a five-year roadmap to ₹6 lakh crore revenue and
     a 10% EBIT margin by FY31, net debt-free by FY29, with JLR guided to ~4%
     margin and breakeven cash flow in FY27 — brokerages remain divided. — markets-finance
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
# ARTICLE 1: Nordic walking eases depression within 5 weeks (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Simple Walk With Poles Eased Depression in Five Weeks, a New Trial Finds",
    "subheadline": "In a randomized study of 64 adults with moderate-to-severe depression, a supervised Nordic-walking program brought large, rapid drops in symptoms within the first five weeks \u2014 and the most severely depressed improved the fastest.",
    "slug": "nordic-walking-rapid-antidepressant-effect-five-weeks-randomized-trial-journal-affective-disorders-diaspora-20260624-0600",
    "category": "lifestyle-health",
    "vertical": "mental-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Depression is heavily stigmatised and under-treated across many Indian families, where therapy and antidepressants are still met with shame or silence; a low-cost, group-friendly walk that shows benefit in weeks is the kind of accessible, face-saving first step that can reach diaspora elders and stressed newcomers who would never walk into a psychiatrist's office.",
    "sources": json.dumps([
        {"name": "Journal of Affective Disorders \u2014 'Early antidepressant effects of supervised Nordic walking in adults with moderate to severe depression: A randomized controlled trial' (DOI: 10.1016/j.jad.2026.121618)", "url": "https://pubmed.ncbi.nlm.nih.gov/41850606/"},
        {"name": "Knowridge Science Report \u2014 'This Walking Style May Reduce Depression in 5 Weeks'", "url": "https://knowridge.com/2026/06/this-walking-style-may-reduce-depression-in-5-weeks/"}
    ]),
    "body": """We are used to thinking of antidepressants as something that comes in a pill bottle or a therapist's office. A new clinical trial adds weight to a humbler idea: that for many people, a brisk walk \u2014 done regularly, in company, with a pair of poles in hand \u2014 can move the needle on depression, and do it surprisingly fast.

## A Full-Body Walk, Borrowed From Skiers

The activity at the centre of the study is Nordic walking, which looks much like ordinary walking but uses two specially designed poles. It was invented in Finland as a way for cross-country skiers to keep training through the summer, and it has since spread worldwide because it turns a stroll into a full-body workout. The poles draw the arms, shoulders, chest and back into the motion; researchers estimate that up to 90 percent of the body's muscles can be engaged. The pay-off is a more demanding session that still feels natural and is easy for almost anyone to learn.

## What the Trial Did

The study, published in the Journal of Affective Disorders, was a randomized controlled trial \u2014 the most rigorous everyday design in clinical research. Sixty-four adults with moderate to severe depression, none of whom exercised regularly, were divided into two groups. Forty-eight took part in a supervised Nordic-walking program; sixteen did no exercise and served as a comparison group.

The walkers met twice a week for ten weeks. Each one-hour session was led by a trained instructor, and the researchers strapped on heart-rate monitors to keep everyone working at a genuine moderate intensity \u2014 about 65 to 75 percent of maximum heart rate, hard enough to count but not punishing. Symptoms were measured three times, using the widely used Beck Depression Inventory-II: at the start, at the halfway point in week five, and at the end in week ten.

## Rapid Relief, Strongest Early

The results were striking on two fronts. First, the Nordic walkers improved far more than the people who did not exercise. Second, and more unexpectedly, most of that improvement arrived early. The biggest gains came in the first five weeks, with a large effect size by clinical standards, and the change then slowed in the back half of the program. In plain terms, people did not have to grind through months of exercise before feeling different \u2014 the lift came quickly.

The pattern was most dramatic for those who were worst off at the outset. Participants with severe baseline depression improved larger and faster than those with moderate symptoms. By the end of the ten weeks, somewhere between 35 percent and 53.6 percent of the walkers had improved enough that their symptoms no longer met the threshold for clinical depression. And no one was hurt: there were no injuries or significant health problems during the program, a reminder that this is a gentle, low-risk intervention.

## What It Does and Doesn't Prove

The authors are careful about the limits. The trial was small, with only 64 people, and ran for just ten weeks, so the long-term picture is unknown and larger studies are needed to confirm the effect. The comparison group was inactive rather than doing a different exercise, so the study shows that structured Nordic walking beats doing nothing \u2014 not necessarily that the poles themselves are essential. And crucially, the researchers frame this as a support for treatment, not a replacement: Nordic walking is not a substitute for therapy or medication, but it may be a powerful and affordable addition to comprehensive care, and a way to start feeling better sooner than many patients expect.

What makes the finding genuinely useful is its sheer practicality. This is a cheap activity that can be done outdoors, in a group, with minimal equipment and no gym membership. That combination of physical exercise, fresh air and social contact may be doing more work together than any one of them alone.

## Why It Matters for the Diaspora

Mental health remains one of the hardest subjects to broach in many Indian and South Asian families. Depression is too often dismissed as weakness, a private failing, or something to be hidden from relatives and the community; therapy carries stigma, and antidepressants more so. For elders who would never accept a referral to a psychiatrist, and for younger migrants buckling under the isolation of a new country, a long-distance family and relentless work, a structured walking group is a rare intervention that sidesteps almost all of that resistance.

It can be framed simply as exercise. It happens in daylight, alongside others, in a park rather than a clinic. It costs little and asks for no diagnosis. For diaspora communities that already build life around temples, gurdwaras, mosques and cultural associations, the model is easy to imagine: a weekly walking group organised through a community centre could deliver real mental-health benefit while looking, to a reluctant participant, like nothing more than a healthy habit and good company. The science is still early, but the message is encouraging \u2014 movement, especially shared movement, is medicine the whole family can take."""
})

# ============================================================
# ARTICLE 2: Ultra-processed foods and male fertility (lifestyle-health)
# ============================================================
articles.append({
    "headline": "It Isn't Just the Calories: Ultra-Processed Diets Are Now Linked to Falling Male Fertility",
    "subheadline": "A tightly controlled feeding study found that just three weeks on an ultra-processed diet worsened body fat, blood lipids and hormones tied to sperm production \u2014 even when calories and nutrients were matched \u2014 pointing the finger at industrial processing itself.",
    "slug": "ultra-processed-food-male-fertility-sperm-quality-cell-metabolism-controlled-feeding-study-diaspora-20260624-0600",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Falling fertility and rising reliance on packaged convenience food are both acute in diaspora life \u2014 long work hours, ready meals and Western supermarket aisles displacing home-cooked dals and vegetables \u2014 making this a quietly personal warning for younger NRI couples already navigating the cost and stress of fertility treatment abroad.",
    "sources": json.dumps([
        {"name": "Medscape \u2014 'Ultraprocessed Foods: A Factor in Male Fertility Decline?'", "url": "https://www.medscape.com/viewarticle/ultraprocessed-foods-factor-male-fertility-decline-2026a1000kwy"},
        {"name": "Cell Metabolism (2025) \u2014 controlled crossover trial of ultra-processed vs minimally processed diets and cardiometabolic and reproductive outcomes in 43 men", "url": "https://www.cell.com/cell-metabolism/home"}
    ]),
    "body": """For years the warning about ultra-processed food focused on the waistline: these products are easy to overeat, so people gain weight. A growing body of research is now making a more unsettling case \u2014 that the harm may come from the processing itself, not just the extra calories \u2014 and one of the newest concerns is an intimate one: male fertility.

## What Counts as Ultra-Processed

The term comes from the NOVA classification system devised by the Brazilian epidemiologist Carlos Monteiro. Ultra-processed foods, or UPFs, are industrial formulations built largely from refined ingredients and additives rather than whole foods. The familiar examples are sugar-sweetened drinks, packaged snacks, processed meats, instant noodles and ready meals, and refined-grain products laced with added sugar. They are engineered for long shelf life, safety, appearance and, above all, palatability \u2014 the qualities that make them so convenient and so easy to keep eating.

The concern, researchers stress, goes beyond poor nutrition. The heavy processing changes the food in ways that ordinary nutrient labels do not capture, and that is exactly what recent fertility research has tried to isolate.

## A Study Built to Separate Processing From Calories

The most striking evidence comes from a controlled-feeding trial published in the journal Cell Metabolism. Rather than rely on people's unreliable memories of what they ate, the researchers fed participants directly and controlled the contents. Forty-three men aged 20 to 35 followed two different diets \u2014 one built around ultra-processed foods, the other around minimally processed foods \u2014 for three weeks each, separated by a three-month washout period so the first diet's effects could clear before the second began.

The clever part was the matching. Both diets contained similar amounts of calories, protein, carbohydrate and fat. The principal difference between them was the degree of processing. That design lets the study ask a sharp question: if everything nutritional is held roughly equal, does processing alone do damage?

## Changes in Just Three Weeks

The answer was yes, and quickly. After only three weeks on the ultra-processed diet, the men showed increased body fat and a less favourable lipid profile, including unhelpful shifts in HDL and LDL cholesterol. More pointedly for fertility, the study reported hormonal alterations associated with spermatogenesis \u2014 the body's process of making sperm. In other words, a short stint of eating heavily processed food, with calories matched to a whole-food diet, was enough to nudge the very hormones that govern male reproductive function in the wrong direction.

The finding lands amid a wider, decades-long debate about declining sperm counts in many countries, and a turn of scientific attention toward diet as one possible driver. It does not stand alone: a broader literature has tied higher UPF intake to obesity, cardiovascular disease, type 2 diabetes and higher all-cause mortality, and controlled trials have repeatedly shown that UPF-rich diets push people to eat more and gain weight. The fertility angle extends that pattern into reproductive health.

## The Caveats Worth Keeping

This is one small, short study, and it measured hormonal and metabolic markers over three weeks rather than tracking whether men actually had more trouble conceiving. The sample was young and limited in size, and the mechanisms \u2014 whether the culprit is additives, the disrupted physical structure of the food, faster eating, or something else \u2014 are still being worked out. No one is claiming a single packet of chips causes infertility. What the work does suggest is that habitually building a diet around ultra-processed products may carry costs that go well beyond weight, and that the processing itself deserves scrutiny.

The practical takeaway is reassuringly old-fashioned: lean toward whole and minimally processed foods \u2014 vegetables, fruit, whole grains, pulses, fresh proteins \u2014 and treat packaged convenience food as an occasional shortcut rather than a daily foundation.

## Why It Matters for the Diaspora

For the Indian diaspora, this research touches a nerve in two ways at once. Fertility is already a fraught, expensive and emotionally charged subject for many young NRI couples, who often pursue treatment far from family support and under the weight of community expectation. And diaspora diets are precisely the kind most vulnerable to processing creep: demanding jobs, long commutes and unfamiliar supermarket aisles steadily crowd out the home-cooked dals, sabzis and freshly made rotis of a traditional Indian kitchen in favour of frozen meals, restaurant takeout and packaged snacks.

The encouraging flip side is that a traditional Indian diet, when actually cooked at home, is largely the minimally processed pattern this research favours \u2014 lentils, vegetables, whole grains and spices prepared from scratch. The study is a quiet argument for protecting that kitchen culture against the convenience economy, not only for heart and waistline but, this evidence suggests, for reproductive health too. For couples planning a family, it reframes a humble choice \u2014 what goes on the plate, and how processed it is \u2014 as something that may matter more than its calorie count alone."""
})

# ============================================================
# ARTICLE 3: Tata Motors five-year roadmap / JLR FY27 (markets-finance)
# ============================================================
articles.append({
    "headline": "Tata Motors Bets on a Five-Year Turnaround \u2014 \u20b96 Lakh Crore in Revenue, and a Promise to Clear Its Debt",
    "subheadline": "At its investor day, Tata Motors' passenger-vehicle group set out targets to lift consolidated revenue past \u20b96 lakh crore and reach a 10% margin by FY31, and to be net debt-free by FY29 \u2014 even as a cautious JLR outlook for FY27 left brokerages split.",
    "slug": "tata-motors-pv-five-year-roadmap-six-lakh-crore-revenue-net-debt-free-fy29-jlr-fy27-guidance-nri-investor-20260624-0600",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Tata Motors is both a heavyweight in the Nifty and Sensex that anchor most NRI India portfolios and the owner of Jaguar Land Rover, whose Range Rovers and Defenders the diaspora actually buys on the streets of London, New Jersey and Toronto \u2014 making its five-year bet a rare stock where the diaspora is invested in the shares and the showroom at once.",
    "sources": json.dumps([
        {"name": "Autocar Professional \u2014 'Tata Motors PV Targets \u20b96 Lakh Crore Revenue, 10% EBIT Margin by FY31'", "url": "https://www.autocarpro.in/news/tata-motors-pv-targets-rs-6-lakh-crore-revenue-10-percent-ebit-margin-by-fy31-133205"},
        {"name": "Autocar Professional \u2014 'Tata Motors PV Targets \u20b91.4 Lakh Crore Revenue From Indian Business by FY31'", "url": "https://www.autocarpro.in/news/tata-motors-pv-targets-rs-14-lakh-crore-revenue-from-indian-business-by-fy31-133198"},
        {"name": "Reuters \u2014 'JLR's profit recovery plan disappoints investors despite US growth push'", "url": "https://www.reuters.com/business/autos-transportation/british-luxury-carmaker-jlr-targets-double-digit-revenue-growth-2026-06-17/"},
        {"name": "The Hindu BusinessLine \u2014 'TMPV shares in spotlight after JLR's FY27 outlook, brokerages divided'", "url": "https://www.thehindubusinessline.com/markets/tmpv-shares-in-spotlight-after-jlrs-fy27-outlook-brokerages-divided/article71117059.ece"}
    ]),
    "body": """After a bruising year, Tata Motors has tried to give investors something to hold on to: a number, a deadline and a plan. At an investor day laying out its strategy for the rest of the decade, the company's passenger-vehicle group \u2014 which spans its India car business and the British luxury marque Jaguar Land Rover \u2014 set out a five-year roadmap built around scale, margins and, perhaps most importantly for a debt-watching market, a pledge to wipe out its net debt.

## The Headline Targets

The centrepiece is a goal to lift consolidated revenue past \u20b96 lakh crore by FY31, alongside an earnings-before-interest-and-tax (EBIT) margin of 10 percent and profit before tax and exceptional items of more than \u20b950,000 crore by the same year. The group also said it expects to generate significant free cash flow by then.

There is an intermediate checkpoint to judge progress against. By FY29, the company wants consolidated revenue to cross \u20b95 lakh crore, an EBIT margin of 7 percent, and profit before tax and exceptional items above \u20b930,000 crore. Most notably, it aims to be net debt-free by FY29 \u2014 a milestone that, for a capital-hungry carmaker, would mark a genuine change in financial character.

To set those targets in context, the group used FY25 as its base year, deliberately stepping over a damaged FY26. In FY25 it reported consolidated revenue of about \u20b93.66 lakh crore, an EBIT margin of 7.7 percent and profit before tax and exceptional items of \u20b928,700 crore. The India passenger-vehicle business alone is being steered toward roughly \u20b91.4 lakh crore in revenue by FY31, with its mainstream brands staying centred on India while expanding selectively abroad.

## Why FY26 Was a Year to Forget

The choice of FY25 as the baseline is not cosmetic; FY26 was genuinely ugly. Consolidated revenue slipped to \u20b93.36 lakh crore, and profit before tax and exceptional items collapsed to just \u20b92,519 crore. The damage was concentrated at JLR, which contributes the lion's share of the group's revenue, and which ran into a wall of trouble at once: higher US tariffs, weak luxury demand in China, the wind-down of older Jaguar models, and a cyberattack that forced the company to halt manufacturing for roughly five weeks.

That backdrop explains why the market has been so jittery, and why management felt the need to spell out a recovery path in such concrete numbers.

## The JLR Question

JLR remains both the engine and the risk. For FY27, the luxury business has guided to revenue of about \u00a326 billion, an EBIT margin of around 4 percent, and breakeven operating cash flow \u2014 an improvement on a dismal recent stretch, but well short of the near double-digit margins JLR earned in better years and the 10 percent it still holds up as a long-term ambition. The company is leaning on a \u00a31.7-billion profitability programme and a product blitz: five launches over two years, led by the Range Rover Electric and the first vehicle from a reinvented Jaguar range, with a sharpened "hyper-focus" on wealthy American buyers to offset Chinese weakness.

Investors were not uniformly convinced. When JLR first laid out the FY27 plan, Tata Motors shares fell by as much as 10 percent before recovering some ground, and brokerages split on what it means. Jefferies kept an underperform rating with a \u20b9300 target, citing rising competition, heavier discounts, higher warranty costs and an ageing model line-up; Bank of America also stayed at underperform; and Citi retained a sell rating, trimming its target to \u20b9320 and calling the guidance cautious. The bulls counter that the worst \u2014 tariffs, the cyberattack, the Jaguar transition \u2014 is now in the base, leaving room to recover.

## Synergies and the Long Game

Strategically, the plan leans on pulling the India and JLR businesses closer together. The two will share more in batteries, suppliers, software, digital technology and international sales, and have already begun sharing manufacturing infrastructure at the Panapakkam plant in Tamil Nadu. Management argues that closer collaboration will improve scale, speed up learning and support capital discipline \u2014 the financial restraint that underpins the net-debt-free promise. The group also intends to draw on the wider Tata ecosystem for batteries, digital capability and other parts of the automotive value chain.

The throughline is a shift in how Tata Motors wants to be judged: less on grand vision, more on hard, dated targets it can be held to. Promises, as ever in this sector, are not profits \u2014 and execution against a tough auto cycle will decide whether the roadmap survives contact with reality.

## Why It Matters for the Diaspora

Few Indian companies sit as squarely in diaspora life as Tata Motors. As a heavyweight constituent of the Nifty and Sensex, it is a meaningful holding in the India-focused mutual funds, ETFs and SIPs that NRIs use to stay invested back home, so its turnaround feeds directly into portfolio returns. But it is also unusual in that the diaspora encounters the product, not just the ticker: through JLR, Tata owns the Range Rovers, Defenders and Jaguars that are status symbols on the roads of London, New Jersey and Toronto, and the "hyper-focus" on affluent American buyers is, in part, a bet on diaspora and aspirational customers in those very markets.

That gives NRI investors a rare double lens. The five-year roadmap is a window into whether an Indian-owned global carmaker can fix a luxury brand under real pressure, clear its debt, and grow at home at the same time. The sensible posture mirrors the brokerages' caution: treat the ambition seriously, watch the FY29 debt and margin checkpoints as the real test, and remember that for once the company has handed the market specific numbers against which its promises can be measured."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["Nordic walking poles outdoor exercise", "people Nordic walking park", "senior adults walking outdoors exercise"],
                          ["nordic walking poles people outdoors", "group walking exercise park"], None),
    articles[1]["slug"]: (["packaged processed food supermarket snacks", "ultra processed food junk food", "fast food packaged snacks unhealthy"],
                          ["processed packaged junk food snacks", "supermarket packaged food aisle"], None),
    articles[2]["slug"]: (["Range Rover car", "Jaguar Land Rover vehicle", "Tata Motors car factory India"],
                          ["luxury SUV car showroom", "modern car automobile"], None),
}
img_captions = {
    articles[0]["slug"]: "A new randomized trial found supervised Nordic walking eased moderate-to-severe depression within five weeks",
    articles[1]["slug"]: "A controlled study links ultra-processed diets to hormonal changes affecting sperm production in young men",
    articles[2]["slug"]: "Tata Motors' Jaguar Land Rover unit, maker of the Range Rover, anchors the group's five-year turnaround plan",
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
