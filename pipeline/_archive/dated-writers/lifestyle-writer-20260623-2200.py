#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-23 22:00 UTC batch.
Topics:
  1. Nature Metabolism: glucosamine supplements drive hyper-glycosylation, linked to faster Alzheimer's decline + 25% higher 5-yr mortality — lifestyle-health
  2. PLOS One / Penn State: 4-minute daily FAST-2 strength routine improves balance & leg strength in older adults — lifestyle-health
  3. RBI FCNR dollar-deposit scheme + new loan-against-FX-deposit rule pulls in diaspora dollars to shore up the rupee — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0623b.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0623b.bin"):
            with open("/tmp/_img_dl0623b.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0623b.bin")
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
# ARTICLE 1: Glucosamine & Alzheimer's (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Joint-Pain Supplement Millions Take May Quietly Speed Up Alzheimer\u2019s, a New Study Warns",
    "subheadline": "A study in Nature Metabolism finds that glucosamine \u2014 one of the world\u2019s most popular supplements for aching knees \u2014 fuels a sugar build-up in the brain that worsened memory in mice and was tied to faster decline and higher death rates in people with dementia.",
    "slug": "glucosamine-supplement-hyperglycosylation-alzheimers-faster-decline-mortality-nature-metabolism-diaspora-20260623-2200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Glucosamine is a staple in the supplement cabinets of older Indian-origin adults managing arthritis and knee pain, often taken for years without a doctor\u2019s oversight; this study is an early but sobering signal that anyone in a diaspora family already living with memory loss should review the habit with a physician rather than assume a 'natural' joint pill is harmless.",
    "sources": json.dumps([
        {"name": "Nature Metabolism / bioRxiv \u2014 Hyper-Glycosylation as a Central Metabolic Driver of Alzheimer's Disease", "url": "https://pubmed.ncbi.nlm.nih.gov/?term=Hyper-Glycosylation+Central+Metabolic+Driver+Alzheimer"},
        {"name": "New York Post \u2014 Popular pain supplement linked to faster Alzheimer's decline \u2014 and death", "url": "https://nypost.com/2026/06/23/health/widely-used-supplement-can-speed-up-alzheimers-decline-death/"}
    ]),
    "body": """One of the most widely used dietary supplements on the planet \u2014 a pill millions reach for to ease creaky, arthritic joints \u2014 may carry an unexpected cost for the aging brain. A new study suggests that glucosamine can accelerate the very processes that drive Alzheimer's disease, and that people already living with dementia who took it fared worse than those who did not.

## What the Study Found

The research, published in *Nature Metabolism*, set out to understand a little-discussed feature of Alzheimer's: a build-up of sugar molecules coating the brain's cells and proteins. Using a battery of techniques \u2014 spatial metabolomics, lipidomics and glycomics \u2014 across both mouse models and human post-mortem brain tissue, the team identified what they call a "hyper-glycosylation" phenotype as a hallmark of the disease.

In a healthy brain, cells carry short sugar chains called N-glycans that help proteins attach to one another and function normally. In Alzheimer's, those chains pile up where they should not, gumming up proteins, impairing memory and contributing to cell death.

To test whether this sugar overload was a cause rather than merely a symptom, the scientists intervened in two directions. Genetically dialing down the enzymes that build these glycans **eased the hyper-glycosylation and improved memory and behaviour** in Alzheimer's-model mice. Going the other way \u2014 feeding the mice **oral glucosamine** \u2014 drove the sugar build-up higher and **worsened their cognitive and behavioural deficits**.

## The Human Signal

The most attention-grabbing findings came from a retrospective look at real patients. Drawing on electronic health records, the researchers compared people with mild cognitive impairment (MCI) and Alzheimer's who used glucosamine against those who did not.

Glucosamine use was associated with a roughly **25 percent higher likelihood of death within five years** among those with Alzheimer's and related dementias. Among people with MCI \u2014 the early, in-between stage that sometimes progresses to full dementia \u2014 glucosamine users were **more likely to make that progression**.

Taken together, the authors argue that hyper-glycosylation is not a passive byproduct of Alzheimer's but a genuine driver of it, and that glucose-derived sugars like glucosamine can feed the fire.

## A Genuine Scientific Tension

Here is where readers should slow down, because the evidence is not one-directional. Several large earlier studies pointed the opposite way. A cohort of nearly half a million UK Biobank participants found regular glucosamine users had a **lower** risk of all-cause dementia, Alzheimer's and vascular dementia, and a Mendelian randomization analysis even suggested the link might be causal in the protective direction. Other work found no association at all.

So the field is genuinely unsettled. The crucial distinction in the new study may be **timing and context**: the harm showed up in brains that were already diseased or on the cusp, where the sugar-handling machinery is already malfunctioning. A supplement that is neutral \u2014 or even mildly helpful \u2014 in a healthy midlife brain could behave very differently once Alzheimer's pathology has taken hold. This is a mechanistic and observational study, not a randomized controlled trial, and it cannot by itself prove that stopping glucosamine changes anyone's fate.

## Why It Matters for Diaspora Families

Glucosamine, often paired with chondroitin, is a fixture in the medicine cabinets of older South Asian adults, who carry high rates of knee osteoarthritis and frequently self-prescribe joint supplements for years without medical supervision. In many diaspora households, an elderly parent's daily pill organiser quietly accumulates such over-the-counter remedies alongside prescription drugs, and no one tracks the interactions.

This study is a reminder that "natural" and "harmless" are not synonyms, especially in the presence of early memory problems. With an estimated 42 percent of Americans expected to develop dementia after the age of 55 \u2014 and South Asians facing their own rising dementia burden \u2014 the overlap between the arthritis crowd and the dementia-risk crowd is large.

## What To Actually Do

The responsible takeaway is not panic, and certainly not for a healthy 50-year-old whose knees feel better on glucosamine. It is this: if someone in the family has been **diagnosed with mild cognitive impairment or Alzheimer's** and is taking glucosamine, that is now a conversation worth having with their doctor rather than a decision to make unilaterally. Bring the full supplement list to the next appointment. For joint pain itself, evidence-backed alternatives \u2014 weight management, targeted strengthening exercise, physiotherapy and, where appropriate, prescribed medication \u2014 carry no such question mark over the brain. The science here will keep evolving; the prudent move in the meantime is informed, not reflexive."""
})

# ============================================================
# ARTICLE 2: 4-minute FAST-2 strength routine (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Four Minutes a Day Was Enough to Make Frail Older Adults Steadier on Their Feet, a Trial Finds",
    "subheadline": "A home-based program of just four simple exercises \u2014 done daily for half a minute each \u2014 measurably improved leg strength, balance and the ability to rise from a chair in inactive adults over 65, with most participants sticking to it 81 percent of the time.",
    "slug": "four-minute-daily-strength-routine-fast2-older-adults-balance-leg-strength-falls-plos-one-penn-state-diaspora-20260623-2200",
    "category": "lifestyle-health",
    "vertical": "healthy-aging",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Aging Indian-origin parents \u2014 many living with their children abroad, often sedentary through long winters and culturally hesitant about gyms \u2014 are precisely the group this study targets: a four-minute, no-equipment-heavy routine doable in a living room is a realistic way for diaspora families to help elders stay independent and avoid the falls that so often trigger a cascade of decline.",
    "sources": json.dumps([
        {"name": "PLOS One \u2014 Brief daily functional strength training to improve functional performance in older adults with mobility disability: A randomized trial", "url": "https://pubmed.ncbi.nlm.nih.gov/?term=Brief+daily+functional+strength+training+older+adults+mobility+disability"},
        {"name": "Fox News \u2014 Researchers say 4-minute routine may help prevent dangerous falls (Penn State College of Medicine)", "url": "https://www.foxnews.com/health/want-age-better-researchers-say-4-minute-routine-may-help-prevent-dangerous-falls"}
    ]),
    "body": """The standard advice for staying strong in old age \u2014 150 minutes of moderate exercise a week, plus dedicated muscle-strengthening sessions \u2014 is well-founded but, for many older adults, wholly unrealistic. Fewer than one in five seniors actually meet the muscle-strengthening guidelines. A new randomized trial offers a far lower bar that still seems to work: **four minutes a day**.

## What the Researchers Did

Scientists at the Penn State College of Medicine designed a home-based regimen called **Functional Activity Strength Training, or FAST-2**, and tested it on 97 sedentary adults aged 65 and older, with an average age of 74. Many had pre-existing walking difficulty, and before the study they were averaging a mere **18 minutes of total physical activity per week**.

Participants were randomly split into two groups: one followed the daily routine, the other served as a delayed-treatment control. The workout itself could hardly be simpler. Four movements, **30 seconds each, separated by 30-second rests** \u2014 four minutes start to finish. The circuit: push-ups, chair stands, two-arm resistance-band rows, and stair stepping.

Crucially, the program was built for real bodies. Push-ups could be done against a kitchen counter or wall. Chair stands allowed hands on the knees for support. Each participant received elastic resistance bands and an adjustable step platform, plus video coaching at the start and at weeks two, four and eight, along with daily email reminders. The program ran for **12 weeks**.

## What Changed

The results were measured with standard geriatric tests, and the gains were real. Compared with the control group, the exercise group:

- Cut **2.3 seconds** off their Five-Times Sit-to-Stand time, a marker of leg power and fall risk.
- Added **3.6 seconds** to their One-Legged Stance time, a direct measure of balance.
- Managed **4.2 more repetitions** in the 30-second chair-stand test, reflecting lower-body endurance.

Just as important as the numbers was the adherence: participants completed the workout on **81 percent of days**, and there were no significant adverse events. For a population that struggles to start and stick with exercise, that compliance rate is arguably the headline finding. A program no one follows helps no one; a four-minute habit that eight in ten days get done can genuinely move the needle.

## Why Balance and Leg Strength Are Life-or-Death

This is not about aesthetics or even general fitness. For older adults, the ability to rise from a chair unaided and to stand steady on one leg are the difference between independence and a downward spiral. Falls are the leading cause of injury-related death in seniors, and a single fall \u2014 a fractured hip, a head injury \u2014 frequently triggers a cascade of hospitalisation, lost mobility and decline. Strengthening the legs and improving balance is the single most evidence-backed way to prevent that first fall.

## Why It Lands Hard in Diaspora Homes

Across the Indian diaspora, a familiar arrangement plays out: aging parents move in with their adult children abroad, or visit for months at a stretch. Many become far more sedentary than they were back home \u2014 no morning temple walk, no neighbourhood market run, long indoor winters in colder climates. Gym culture often feels alien or intimidating, and there is sometimes a cultural reluctance to "exercise" as a formal activity.

A four-minute routine that needs little more than a sturdy chair, a wall, a stair and a couple of resistance bands sidesteps almost all of those barriers. It can be done in a living room, in regular clothes, with a grandchild counting reps alongside. For families anxious about an elderly parent's steadiness on the stairs, it is a concrete, low-cost intervention rather than a vague worry.

## What To Actually Do

Anyone considering this for an older relative should start with a quick medical check, especially if there is heart disease, severe arthritis or a history of falls. From there, the formula is forgiving: four basic movements, 30 seconds each, daily, with modifications that fit the person's ability \u2014 counter push-ups, supported chair stands, gentle band rows, careful step-ups with a handrail nearby. The study's lesson is liberating: the perfect, hour-long gym session that never happens is worth far less than the modest four-minute routine that actually gets done, day after day."""
})

# ============================================================
# ARTICLE 3: RBI FCNR / diaspora dollar deposit scheme (markets-finance)
# ============================================================
articles.append({
    "headline": "India Is Courting the Diaspora\u2019s Dollars to Rescue the Rupee \u2014 and Banks Are Racing to Cash In",
    "subheadline": "The RBI is subsidising hedging costs on foreign-currency deposits and now letting domestic banks lend against them, in a 2013-style push to pull tens of billions of NRI dollars into the country. Analysts estimate the scheme could draw anywhere from $55 billion to $100 billion.",
    "slug": "rbi-fcnr-diaspora-dollar-deposit-scheme-loans-against-fx-deposits-rupee-defence-gift-city-nri-investor-20260623-2200",
    "category": "markets-finance",
    "vertical": "personal-finance",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "This scheme is aimed squarely at NRIs: with banks now offering 6\u20137 percent on dollar deposits \u2014 and leveraged structures that could push returns toward 12\u201315 percent \u2014 overseas Indians can earn high rupee-equivalent yields without taking on currency risk, while helping defend the very rupee their families back home depend on.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India File: Rupee gets diaspora lifeline, banks cash in", "url": "https://www.reuters.com/world/india/"},
        {"name": "Reuters \u2014 India's RBI to allow domestic banks to extend loans against overseas FX deposits", "url": "https://www.reuters.com/world/india/"},
        {"name": "Reuters \u2014 India's central bank sold net $8.9 billion in April defending the rupee", "url": "https://www.reuters.com/markets/currencies/"}
    ]),
    "body": """When the rupee plunged to a record low near 97 to the dollar during the U.S.-Iran war, the Reserve Bank of India burned through nearly $9 billion in a single month defending it, pushing foreign-exchange reserves to a more than one-year low. Now the central bank is reaching for a different, more durable tool to shore up the currency: the wallets of the Indian diaspora.

## The Scheme

Earlier this month the RBI revived a playbook last used during the 2013 "taper tantrum" crisis. It offered to **subsidise the hedging costs** banks incur when they raise foreign-currency non-resident (FCNR) deposits \u2014 dollars placed by overseas Indians with Indian banks for three to five years. Because the RBI absorbs the currency-hedging expense, banks can offer NRIs unusually attractive rates while converting those dollars into rupees, injecting hard currency into the system.

This week the central bank went further. In a notice on Tuesday, it said domestic lenders may now **extend loans to non-residents against those foreign-currency deposits**, including through their overseas branches and units in India's tax-neutral hub, **GIFT City** in Gujarat. Banks can also issue standby letters of credit against such deposits and place a lien on the accounts. The RBI's swap will cover only the principal, not the interest, and applies to deposits mobilised for a minimum of three years.

In plain terms: an NRI can park dollars in a high-yielding Indian deposit, then borrow against it to deposit even more \u2014 a leveraged structure that magnifies returns.

## The Numbers Banks Are Chasing

The appetite is enormous. Banks have raised rates on these deposits to around **6 to 7 percent**, well above what comparable dollar deposits earn in the West. With leverage layered on, the math gets striking. Macquarie analysts estimate returns could approach **12 percent**; Axis Bank suggests they could climb to **15 percent** at higher leverage levels.

Estimates for the total inflow vary widely but are large in every case. Nomura puts the potential at about **$55 billion**, with the bulk expected in August and September. Axis Bank sees scope for as much as **$100 billion**. Macquarie pencils in $30 billion to $50 billion. Any of these would meaningfully ease the pressure on the rupee.

## Why Banks Win Too

Lenders stand to be major beneficiaries, which is why they are marketing the scheme aggressively. The inflows could **revive sluggish deposit growth**, improve liquidity in the financial system, and push down market interest rates \u2014 lower borrowing costs that have already nudged companies toward the bond market. Because these deposits are exempt from reserve requirements, they are an especially cheap and efficient source of funding, and they help ease banks' stretched loan-to-deposit ratios.

Investors have noticed. The Nifty Bank index has climbed nearly 7.2 percent over the past month, sharply outperforming the broader Nifty 50's 1.6 percent advance. Large lenders with strong overseas footprints \u2014 State Bank of India and HDFC Bank among them \u2014 are seen as the biggest winners. One sticking point remains: many banks have GIFT City branches but no presence in foreign countries, and it is not yet fully settled whether GIFT City units can offer the leveraged loans, or whether those banks will have to lean on foreign lenders.

## Why NRIs Should Pay Close Attention

For the diaspora, this is a rare alignment of self-interest and sentiment. An NRI can earn a **high yield in dollars without taking on rupee-depreciation risk** \u2014 the FCNR structure keeps the deposit denominated in foreign currency, so a falling rupee does not erode the principal. That removes the single biggest fear that has historically kept overseas Indians wary of sending money home: watching their savings shrink in dollar terms as the rupee slides.

At the same time, every dollar deposited helps defend the rupee that their relatives in India live on, that their property back home is valued in, and that their future remittances will convert into. It is, unusually, a financial decision that doubles as a vote of confidence in the home economy.

## The Caveats

None of this is free money. Leveraged returns of 12 to 15 percent come with leveraged risk; borrowing against a deposit amplifies losses as well as gains if rates or terms move unfavourably. The schemes can be complex, with hedging, lien and letter-of-credit mechanics that the average saver will not fully grasp. And the 2013 precedent is a reminder that India turns to this tool precisely when its currency is under strain \u2014 a signal of stress as much as opportunity.

## The Bottom Line

India is making an explicit pitch to its global family: bring your dollars home, earn a premium, and help steady the rupee in the bargain. For NRIs weighing where to park savings, the offer is genuinely attractive \u2014 but it rewards those who read the fine print, understand the leverage, and treat it as one considered piece of a portfolio rather than a guaranteed windfall."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["dietary supplement capsules pills", "glucosamine supplement tablets", "medication pills capsules bottle"],
                          ["dietary supplement capsules", "pills medication"], None),
    articles[1]["slug"]: (["senior exercise resistance band", "older adults exercise fitness", "elderly woman exercise home"],
                          ["senior exercise", "older adult fitness"], None),
    articles[2]["slug"]: (["Reserve Bank of India building Mumbai", "Indian rupee US dollar currency notes", "GIFT City Gujarat building"],
                          ["indian rupee dollar money", "currency exchange dollar"], None),
}
img_captions = {
    articles[0]["slug"]: "Dietary supplement capsules; a new study links glucosamine to a sugar build-up that worsened Alzheimer\u2019s in mice and people",
    articles[1]["slug"]: "An older adult exercising at home; a four-minute daily routine improved balance and leg strength in adults over 65",
    articles[2]["slug"]: "The Reserve Bank of India is courting diaspora dollars through high-yield foreign-currency deposits to defend the rupee",
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
