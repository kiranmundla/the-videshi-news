#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-19 22:00 UTC batch.
Topics:
  1. JAHA meta-analysis: fitness apps/wearables help heart-disease patients walk ~1,100 more steps/day — lifestyle-health
  2. Neurology (AAN), June 17: TBI and neurological disorders (stroke/dementia/epilepsy/Parkinson's) are a two-way risk — lifestyle-health
  3. Indian banks push to lend via GIFT City units to fuel RBI's diaspora dollar-deposit scheme; Nomura sees $55bn — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0619c.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0619c.bin"):
            with open("/tmp/_img_dl0619c.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0619c.bin")
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
# ARTICLE 1: Fitness apps/wearables help heart patients move (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Smartwatch on Your Wrist May Be Quietly Doing Your Heart a Favour, a Review of 14 Trials Finds",
    "subheadline": "Pooling 14 clinical trials, researchers found that heart-disease patients who used fitness apps or wearables walked nearly 1,100 more steps a day than those who did not \u2014 a small, low-cost nudge with outsized relevance for a community that develops heart disease early.",
    "slug": "fitness-apps-wearables-heart-disease-patients-extra-1100-steps-jaha-meta-analysis-diaspora-20260619-2200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "People of Indian origin suffer heart attacks up to a decade earlier than other populations and are among the most enthusiastic adopters of smartwatches and fitness rings \u2014 so the finding that a device many NRIs already wear can measurably push them to move more turns a gadget on the wrist into a genuine, low-cost cardiac-prevention tool for the diaspora.",
    "sources": json.dumps([
        {"name": "Journal of the American Heart Association \u2014 Digital tools and physical activity in cardiovascular disease: systematic review and meta-analysis (2026)", "url": "https://www.ahajournals.org/journal/jaha"},
        {"name": "Wyoming News / SWNS \u2014 Apps and trackers boost exercise for people with heart disease", "url": "https://www.wyomingnews.com/"}
    ]),
    "body": """The smartwatch that buzzes when you have been sitting too long may be doing more than nagging. A new pooled analysis of 14 clinical trials finds that people with established heart disease who used fitness apps or wearable devices walked substantially more than those who did not \u2014 and the effect was achieved with nothing more than gentle, automated prompts.

## What the Researchers Did

The analysis, published in the *Journal of the American Heart Association*, pulled together 14 separate clinical trials involving more than 1,000 participants. Almost all the studies enrolled adults aged 18 and over; one also included adolescents from age 12. Crucially, every participant already had diagnosed cardiovascular disease \u2014 coronary heart disease or heart failure, or a history of heart attack or stroke. This was not a study of the worried well; it was a study of people for whom movement is medicine.

Researchers compared those who used smartphone apps or wearable technology against peers who received usual care without the digital tools, and measured the difference in their daily activity.

## What They Found

The people using digital tools walked **nearly 1,100 more steps a day** than those who did not. They also logged about **four additional minutes** of moderate-to-vigorous physical activity daily. The gains held up even though the trials used very different devices and relied on simple behaviour-change techniques \u2014 self-monitoring, feedback and goal-setting.

"These devices are not just gadgets," said researcher Reza Zand. "When included in a treatment plan, they can support routine care and help patients take small yet important steps toward better cardiovascular health."

There was an honest limit to the findings. The tools did **not** significantly improve peak oxygen consumption or maximum walking distance \u2014 the harder measures of cardiovascular fitness. As Zand put it, digital programmes can clearly motivate patients to be more active, but longer studies are needed to confirm whether that extra movement translates into lasting gains in fitness and survival.

## Why a Thousand Extra Steps Matters

Eleven hundred steps may sound modest, but the dose-response evidence on walking is now strong: among people with heart disease and high blood pressure, every additional 1,000 steps a day has been linked to meaningfully lower risk of death, heart failure and heart attack. For a population that, by the researchers' own account, struggles to stay active \u2014 the American Heart Association notes that fewer than one in three people with cardiovascular disease are physically active \u2014 a tool that reliably adds a thousand steps is not trivial.

Damon Swift of the AHA's lifestyle physical activity committee welcomed the results, saying that combining mobile and wearable technology with standard prevention "provides a unique opportunity to potentially further reduce the risk" of a second or third cardiovascular event.

## Why It Resonates for the Diaspora

This is a story with the Indian diaspora's name on it for two reasons. First, the disease. South Asians develop coronary heart disease far earlier and more aggressively than most other groups \u2014 often a decade sooner \u2014 and at lower body weights, driven by a genetic tendency toward visceral fat, low HDL cholesterol and insulin resistance. A great many NRI families have watched a father or uncle have a heart attack in his forties or fifties. Secondary prevention \u2014 staying active after a cardiac event \u2014 is exactly where this evidence applies.

Second, the technology. Indian-origin professionals are among the most enthusiastic adopters of smartwatches, fitness bands and sleep-tracking rings. The device is already on the wrist or finger. This research suggests that turning on the step prompts and activity goals \u2014 features most people ignore \u2014 may quietly convert a status-symbol gadget into a cardiac-rehabilitation aid.

## What To Actually Do

The practical takeaway is refreshingly concrete. If you or a family member has heart disease, the fitness tracker you already own is worth using deliberately, not passively: set a daily step goal, switch on movement reminders, and review the weekly summary. For those in formal cardiac rehab, ask the cardiologist or physiotherapist whether app-based activity tracking can be folded into the plan. The goal is not a marathon. It is roughly a thousand more steps a day \u2014 a ten-minute walk after dinner \u2014 sustained over months. The science increasingly says the wrist-based nudge helps people actually do it, and for a community that pays an early and heavy price for heart disease, that small nudge is worth taking seriously."""
})

# ============================================================
# ARTICLE 2: TBI <-> neurological disorders two-way risk (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Head Injury Can Raise the Risk of Brain Disease. New Research Says the Danger May Run Both Ways.",
    "subheadline": "A study of more than 55,000 older veterans finds that those recently diagnosed with stroke, dementia, epilepsy or Parkinson's were far more likely to have suffered a traumatic brain injury \u2014 a finding that reframes fall prevention as brain protection for ageing parents.",
    "slug": "traumatic-brain-injury-neurological-disorders-two-way-risk-falls-older-adults-neurology-aan-diaspora-20260619-2200",
    "category": "lifestyle-health",
    "vertical": "elder-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Millions of NRIs are caring for ageing parents \u2014 some living abroad with them, many supporting elders back in India from a distance \u2014 and this research delivers a sharp, actionable warning: a parent newly diagnosed with dementia, stroke, epilepsy or Parkinson's is in a high-risk window for a fall-related head injury, making home fall-proofing one of the most concrete things a diaspora family can do.",
    "sources": json.dumps([
        {"name": "Neurology (American Academy of Neurology) \u2014 Bidirectional association between TBI and neurological disorders in older adults (published June 17, 2026)", "url": "https://www.neurology.org/"},
        {"name": "News-Medical \u2014 Neurological disorders may raise traumatic brain injury risk in older adults", "url": "https://www.news-medical.net/"}
    ]),
    "body": """For years, the link between a serious blow to the head and later brain disease ran one way in the public imagination: a traumatic brain injury (TBI) could raise the risk of stroke, dementia, epilepsy or Parkinson's down the line. New research suggests the arrow may also point the other way \u2014 that having one of those brain conditions can itself make a head injury more likely. For families caring for ageing parents, it is a finding with immediate, practical force.

## What the Researchers Found

The study, published on June 17, 2026, in *Neurology*, the medical journal of the American Academy of Neurology, examined older military veterans. Researchers compared **13,801 veterans** with an average age of 78 who had recently suffered a traumatic brain injury against **41,403 veterans** of similar age who had not. They then combed through health records for the year before and after the injury.

The result was striking. Older veterans with a recent TBI were **three to four times more likely** to have been diagnosed with stroke, dementia, epilepsy or Parkinson's disease in the preceding year than those without a head injury. People who already had any of those four conditions before the study window were excluded, so the diagnoses being counted were genuinely recent.

## Reading the Finding Carefully

The study does not prove that brain diseases cause head injuries. It shows an association, and the direction of cause is not settled by data like this. But the authors offer a compelling and intuitive explanation for why the link is real.

"These findings suggest that the period after being diagnosed with a neurological condition is an important time period for preventing TBI," said study author Carrie Peltz of the San Francisco Veterans Affairs Health Care System. "Our findings raise the possibility that dementia, stroke, epilepsy and Parkinson's disease are themselves risk factors for TBI in older people. Neurological diseases often impair motor control, balance, gait, coordination and thinking skills \u2014 all of which make people more likely to fall, which is the main cause of TBI in older adults."

In other words, the newly diagnosed brain condition does not magically summon a head injury. It quietly erodes the very systems \u2014 balance, coordination, judgement \u2014 that keep a person upright. A fall follows. And a fall in an older adult is the leading route to a traumatic brain injury.

## Why This Lands Hard in Diaspora Homes

The Indian diaspora is, increasingly, a sandwich generation. NRIs in their forties and fifties are raising children abroad while caring for ageing parents \u2014 some who have moved overseas to live with them, many more who remain in India and are supported from a distance through phone calls, money and worry. The fear of "something happening" to a parent back home, with the family an ocean away, is one of the most universal diaspora anxieties.

This study turns that diffuse anxiety into a specific, addressable risk. If a parent has just been diagnosed with dementia, has had a stroke, or is living with Parkinson's or epilepsy, they have entered a window of heightened danger for a fall and a resulting head injury. That is precisely the moment to act.

## What To Actually Do

The good news is that fall prevention is among the most concrete, low-tech interventions in all of medicine. For a parent recently diagnosed with a neurological condition \u2014 whether they live down the hall or in another country \u2014 the checklist is clear and worth treating as urgent:

- **Fall-proof the home.** Remove loose rugs and clutter, fix loose stair railings, add grab bars in the bathroom and near the toilet, and ensure hallways and staircases are brightly lit, including at night.
- **Review medications.** Many drugs prescribed for these very conditions, along with sedatives and some blood-pressure medicines, can cause dizziness or low blood pressure on standing. Ask the doctor for a medication review focused on fall risk.
- **Check vision and footwear.** Updated glasses and well-fitting, non-slip shoes (not loose chappals on smooth floors) cut fall risk meaningfully.
- **Build strength and balance.** Gentle, supervised exercise \u2014 even chair-based or simple balance work, and for the able, yoga and tai-chi-style movement \u2014 measurably reduces falls.
- **Arrange support.** For a parent in India, this may mean a daytime attendant, a relative checking in, or a medical-alert system within reach.

The headline is not that a diagnosis dooms a parent to a head injury. It is that the months after such a diagnosis are a recognisable high-risk window \u2014 and that a weekend spent fall-proofing a home is one of the most protective things a diaspora family can do from anywhere in the world."""
})

# ============================================================
# ARTICLE 3: Banks push to lend via GIFT City for diaspora dollar deposits (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Banks Want to Lend You the Dollars to Deposit With Them \u2014 and GIFT City Is the Catch",
    "subheadline": "Lenders are pressing the RBI to let their GIFT City branches finance the diaspora dollar-deposit scheme designed to shore up the rupee. Nomura reckons the plan could pull in $55 billion \u2014 most of it from NRIs \u2014 with the bulk arriving by September.",
    "slug": "india-banks-gift-city-lending-fcnr-dollar-deposit-scheme-nomura-55-billion-rupee-nri-investor-20260619-2200",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "This entire scheme is built around the diaspora's dollars \u2014 it is NRIs the RBI is trying to coax into Indian banks to defend the rupee \u2014 so the mechanics of how banks fund it, and the leverage being negotiated behind the scenes, directly shape the returns and risks facing any overseas Indian weighing an FCNR deposit this summer.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 Indian banks push for lending via GIFT City units in dollar deposit scheme, sources say", "url": "https://www.reuters.com/"},
        {"name": "Finshots \u2014 RBI may have found a way to bring $50 billion into India", "url": "https://finshots.in/"},
        {"name": "CAclubindia \u2014 RBI temporarily removes interest rate caps on NRE and FCNR(B) deposits till 30th Sept 2026", "url": "https://www.caclubindia.com/"}
    ]),
    "body": """India's effort to defend the rupee has produced one of the more intricate financial-engineering schemes in recent memory \u2014 and it hinges on the diaspora's dollars. Now the country's banks are quietly pressing the Reserve Bank of India over a crucial piece of plumbing: whether they can use their branches in the tax-neutral hub of GIFT City to finance the whole thing. The answer will help decide how much overseas money actually flows in.

## The Backstory

The rupee has had a punishing run. Foreign institutional investors have sold roughly $45 billion of Indian assets since 2024, foreign portfolio investors dumped a record $18.9 billion of stocks in 2025, and in just the first four months of 2026 they offloaded over $20 billion \u2014 already surpassing all of last year. With dollars flooding out, the rupee slid to a record low near 97 to the dollar last month before recovering to around 94.

To stem the bleeding, the RBI reached for a tool it last used in 2013. Earlier this month it offered to **subsidise the hedging cost** on foreign-currency non-resident, or FCNR(B), deposits of three to five years, and on external commercial borrowings. In plain terms, the central bank is absorbing the currency risk so banks can offer NRIs a deal that is hard to refuse: park your dollars with an Indian bank for three years, earn around 7 percent in dollars, and get every dollar back at maturity regardless of where the rupee goes. Separately, the RBI on June 17 temporarily lifted interest-rate caps on NRE and FCNR(B) deposits until September 30, letting banks compete harder for overseas money.

## The New Wrinkle: GIFT City

Here is where the latest development comes in. The 2013-style scheme typically works through leverage: a bank lends a customer the dollars, the customer parks that money in a dollar deposit with an Indian lender, and the leverage juices the effective return. The question now being negotiated is *which* arm of the bank gets to do the lending.

Indian lenders are asking the RBI to let their branches in the Gujarat International Finance Tec-City \u2014 GIFT City \u2014 provide this funding. These branches operate under offshore banking rules and, the banks argue, function much like foreign banks, so they should be allowed to extend such loans. As one treasury head, VRC Reddy of Karur Vysya Bank, put it: "Most banks have branches in GIFT City, but many of them do not have a presence in foreign countries. If the leverage is not allowed through GIFT, these banks will have to depend on foreign lenders." The RBI has not yet responded publicly, and it is unclear whether existing rules on leverage extend to GIFT City branches.

## Why the Plumbing Matters

This is not a technicality. If GIFT City branches can do the lending, a far wider set of Indian banks \u2014 not just the handful with overseas operations \u2014 can participate, and the leverage that makes the deposits attractive can be offered at home rather than farmed out to foreign banks. That widens the funnel for dollars and keeps more of the economics within India.

The numbers at stake are large. Brokerage **Nomura estimates the scheme could attract $55 billion**, with the bulk arriving in August and September. Nomura notes that, compared with 2013, US dollar rates are far higher now \u2014 and the leverage on offer "will boost returns." Finshots and other analysts have put the figure near $50 billion. Either way, it is the kind of inflow that could meaningfully steady the rupee and rebuild the RBI's foreign-exchange buffers, which have fallen from a March peak of $728.5 billion to about $681.6 billion.

## Why NRIs Should Pay Attention

For the diaspora, this is not a spectator sport \u2014 it is a scheme designed expressly to attract their money. Several things follow for any NRI weighing an FCNR(B) deposit this summer.

First, the **deal is genuinely better than usual**. With rate caps lifted and the RBI eating the hedging cost, FCNR(B) dollar-deposit rates over the coming months are likely to be more competitive than they have been in years \u2014 and crucially, they carry no rupee risk, since dollars go in and dollars come out.

Second, **timing is built in**. The interest-rate-cap relaxation expires on September 30, and analysts expect the bulk of inflows in August and September. The window is deliberately short.

Third, **understand the leverage**. The headline returns some promoters tout rely on borrowed dollars layered on top of the deposit. Leverage amplifies returns but also costs \u2014 and introduces a lender into the equation. An NRI should be clear about whether they are simply making a plain dollar deposit or entering a leveraged structure, and read the terms accordingly.

## The Bottom Line

The rupee's defence has quietly become a courtship of the diaspora. The RBI has sweetened the terms; the banks are now haggling over the pipes that carry the money in. For overseas Indians, the result is a rare moment when parking dollars back home pays unusually well \u2014 provided they move before the September deadline and understand exactly what they are signing."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["smartwatch fitness tracker wrist", "person walking exercise outdoors", "fitness wearable activity tracker"],
                          ["smartwatch fitness tracker", "person walking exercise"], None),
    articles[1]["slug"]: (["elderly person walking cane", "senior citizen India elderly", "older adult walking support"],
                          ["elderly person walking", "senior citizen care"], None),
    articles[2]["slug"]: (["GIFT City Gandhinagar Gujarat", "Indian rupee dollar currency notes", "Mumbai financial district bank building"],
                          ["indian rupee dollar notes", "bank building finance"], None),
}
img_captions = {
    articles[0]["slug"]: "A fitness tracker; a review of 14 trials found heart patients using such tools walked about 1,100 more steps daily",
    articles[1]["slug"]: "An older adult walking with support; falls are the main cause of traumatic brain injury in the elderly",
    articles[2]["slug"]: "Indian and US currency; banks want to fund the RBI's diaspora dollar-deposit scheme via GIFT City branches",
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
