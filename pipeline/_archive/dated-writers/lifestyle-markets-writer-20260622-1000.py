#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-22 10:00 UTC batch.
Topics:
  1. DPP/DPPOS JAMA study: among adults with prediabetes followed 21 yrs,
     intensive lifestyle (not metformin) tied to lower long-term multimorbidity
     (HR 0.79 vs placebo; HR 0.57 for the costliest disease dyads). Metformin
     no better than placebo. — lifestyle-health
  2. ENDO 2026 / Frontiers in Immunology mouse study (Dasman Diabetes Institute,
     Kuwait): COMPLETE sucrose elimination from a low-fat diet disrupted the gut
     microbiome, worsened glucose control/insulin resistance and drove gut+liver
     inflammation and fatty-liver signs — despite no weight gain. Nuance: reduce
     excess sugar, don't necessarily eliminate it entirely. — lifestyle-health
  3. Jio Platforms files DRHP with SEBI (June 19): fresh-issue-only IPO of up to
     27 crore equity shares (FV Rs 10), est. ~Rs 36,000 cr raise, ~Rs 12.5 lakh
     cr ($130-180bn) valuation — potentially India's largest IPO ever; proceeds
     mainly to repay ~Rs 27,500 cr of RJIL debt. Led by Akash, Isha, Anant
     Ambani. — markets-finance
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
# ARTICLE 1: Lifestyle beats metformin for multimorbidity (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Diet and Exercise Beat a Popular Diabetes Pill at Holding Off Multiple Diseases, a 21-Year Trial Finds",
    "subheadline": "Following adults with prediabetes for more than two decades, researchers found that an intensive diet-and-exercise program \u2014 not the widely prescribed drug metformin \u2014 was tied to a meaningfully lower risk of piling up multiple chronic illnesses, with the sharpest protection against the costliest disease combinations.",
    "slug": "lifestyle-intervention-beats-metformin-multimorbidity-dpp-dppos-jama-21-year-trial-diaspora-20260622-1000",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Metformin is one of the most commonly prescribed drugs across Indian households at home and abroad, and many NRIs reach for the pill while treating diet and exercise as optional \u2014 so a 21-year trial showing that the lifestyle program, not the drug, blunted the long-term accumulation of chronic disease reframes what genuine prevention looks like for a diaspora at high metabolic risk.",
    "sources": json.dumps([
        {"name": "JAMA \u2014 Lifestyle and Metformin Interventions and Risk of Multimorbidity in Adults With Prediabetes", "url": "https://jamanetwork.com/journals/jama/fullarticle/2850450"},
        {"name": "New York Post \u2014 Two simple habits may outperform a popular longevity wonder drug: study", "url": "https://nypost.com/2026/06/16/health/two-habits-beat-out-diabetes-wonder-drug-metaformin-study/"},
        {"name": "American Diabetes Association \u2014 New Data from the Diabetes Prevention Program Outcomes Study", "url": "https://diabetes.org/"}
    ]),
    "body": """Metformin has become something close to a household word, a cheap, decades-old diabetes pill that has lately been talked up as a possible longevity drug. A long-running American trial has now put it to a stern test against an old-fashioned rival \u2014 diet and exercise \u2014 and the rival won.

## What the Study Found

The findings, published in JAMA, draw on one of the most influential prevention trials ever run: the Diabetes Prevention Program (DPP) and its decades-long follow-up, the DPP Outcomes Study. Beginning in the late 1990s, 3,234 adults at high risk of diabetes were randomly assigned to one of three groups \u2014 an intensive lifestyle program built around a low-fat, low-calorie diet and at least 150 minutes of physical activity a week; the drug metformin; or a placebo.

Researchers then tracked what happened over the very long term. For 1,173 of those participants who could be followed through Medicare records for 21 years, the team measured not a single disease but multimorbidity \u2014 the accumulation of two or more chronic conditions from a list of 15, including high blood pressure, cancer, dementia, chronic kidney disease, heart failure, osteoporosis and stroke.

By the end of follow-up, multimorbidity was nearly universal in this aging group, but the gaps between the arms were telling. Among the lifestyle group, 82 percent developed multiple chronic conditions, compared with 85 percent on metformin and 87 percent on placebo. After adjusting for other factors, the lifestyle group's risk of multimorbidity was 21 percent lower than the placebo group's. Metformin, by contrast, showed no significant advantage over placebo.

## The Standout Number

The most striking result lay in the most expensive, most debilitating disease combinations. When researchers narrowed the lens to "dyads" of the costliest conditions \u2014 pairings such as heart failure with kidney disease, or cancer with a mental-health condition \u2014 the lifestyle group's risk was 43 percent lower than placebo. These are precisely the clusters that overwhelm patients and health systems alike, and the kind that medicine has struggled to prevent once they begin to snowball.

That distinction matters because, as the authors note, efforts to stop multimorbidity have largely fallen short in everyday practice. Once a person starts collecting illnesses, the conditions tend to feed one another, and reversing the cascade is hard. A program that measurably slows it, decades out, is unusual.

## How to Read It Honestly

A few caveats keep the result in proportion. The long-term comparison is observational, so it shows a strong association rather than airtight proof. The lifestyle "dose" also faded over time \u2014 the booster classes that kept participants on track were offered only through 2014 \u2014 and many people in all groups ended up taking metformin for diabetes as the years passed, which may have blurred the drug's standalone effect. The participants were also older, with a median age of 74 by the end, and most were women.

None of that erases the headline. This is not a study saying metformin is useless; the drug remains a frontline diabetes treatment with real benefits. It is a study saying that, for warding off the long, slow pileup of chronic disease, a sustained change in how a person eats and moves did something a pill did not.

## Why It Matters for the Diaspora

For Indians at home and abroad, the message lands on familiar ground. South Asians carry an elevated, well-documented risk of type 2 diabetes and heart disease, often striking earlier and at lower body weights than in other populations. Metformin is among the most commonly prescribed medicines in Indian families, and for many it has become a substitute for harder lifestyle change rather than a complement to it.

This trial reframes that bargain. The intensive program it tested was not exotic \u2014 a balanced, calorie-aware diet and about 150 minutes of weekly activity, roughly half an hour most days. That is squarely within reach for a community that already prizes home cooking and can fold movement into daily routine. The endocrinologists who reviewed the findings stressed starting small and building gradually: 10 to 15 minutes of activity once or twice a day for someone sedentary, then more.

The deeper takeaway is one of agency. For a diaspora that often feels its metabolic risk is fixed by genetics, the study offers evidence that the long arc of chronic disease can be bent \u2014 not by a prescription alone, but by the unglamorous, daily habits that remain, decades on, the most powerful prevention available."""
})

# ============================================================
# ARTICLE 2: Going completely sugar-free can backfire (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Cutting Out Sugar Entirely May Backfire on the Gut, a New Study Suggests \u2014 the Lesson Is Moderation, Not Zero",
    "subheadline": "Mice fed a low-fat diet with no sugar at all developed a disrupted gut microbiome, worse blood-sugar control and signs of fatty liver \u2014 even though they did not gain weight \u2014 hinting that total elimination, rather than simply trimming excess, can undo the very benefits people are chasing.",
    "slug": "complete-sugar-elimination-sucrose-free-low-fat-diet-gut-microbiome-liver-inflammation-endo-2026-dasman-diaspora-20260622-1000",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "\"Sugar-free\" and \"no sugar\" have become aspirational badges in diaspora kitchens and on diabetes-conscious Indian menus, where cutting out mithai and refined carbs is treated as an unalloyed good \u2014 so a study warning that total elimination may disrupt gut and metabolic health adds a needed note of nuance for a community both highly sugar-aware and highly diabetes-prone.",
    "sources": json.dumps([
        {"name": "ScienceAlert \u2014 Sugar-Free Diets May Have a Hidden Side Effect, Study in Mice Suggests", "url": "https://www.sciencealert.com/sugar-free-diets-may-have-a-hidden-side-effect-study-in-mice-suggests"},
        {"name": "Medical Daily \u2014 Going Completely Sugar-Free May Actually Be Making You Less Healthy", "url": "https://www.medicaldaily.com/"},
        {"name": "Endocrine Society \u2014 ENDO 2026 / Frontiers in Immunology: Nutritional Immunology", "url": "https://www.endocrine.org/"}
    ]),
    "body": """For anyone trying to eat well, "no sugar" has the ring of a virtue. Cut it out completely, the thinking goes, and the body can only benefit. A new study complicates that clean story, suggesting that going all the way to zero \u2014 rather than simply easing off excess \u2014 may quietly work against you.

## What the Study Found

Researchers at the Dasman Diabetes Institute in Kuwait City ran a 16-week experiment on two groups of mice, presented at ENDO 2026, the Endocrine Society's annual meeting, and accepted for publication in Frontiers in Immunology. Both groups ate a low-fat diet. The only difference was sugar: one group's food contained a standard, moderate amount of sucrose \u2014 ordinary table sugar \u2014 while the other's was completely sugar-free.

Over the four months, the scientists tracked weight, glucose tolerance, insulin sensitivity, hormone levels, internal inflammation and the makeup of the animals' gut bacteria. The sugar-free group did not gain extra weight \u2014 the usual headline measure of a "successful" diet. But beneath that reassuring surface, their internal health markers deteriorated.

The mice on the totally sugar-free diet developed an imbalance in their gut microbes, along with increased inflammation in both the intestines and the liver. They also showed poorer blood-sugar control, signs of insulin resistance, and cellular changes associated with fatty liver disease. In other words, removing sugar entirely appeared to trigger the very kind of metabolic dysfunction that healthy eating is meant to prevent.

"Completely removing sucrose from a low-fat diet may unexpectedly disrupt gut health and promote inflammation and metabolic dysfunction," said Rasheed Ahmad, the principal scientist who led the work. The researchers concluded that the finding "reveals an unrecognized dietary trigger of metabolic dysfunction" \u2014 one hiding in plain sight inside a diet most people would call exemplary.

## What It Does Not Say

The caveats here are unusually important, because the headline is so easy to misread. This was a study in mice, not people, over a relatively short window, and rodent gut bacteria and carbohydrate metabolism differ from ours in meaningful ways. The findings cannot be transplanted directly onto a human dinner plate without further clinical research.

Crucially, the study does not give sugar a clean bill of health, nor does it license a return to sweets. The well-established advice to cut down on excess added sugar \u2014 especially from sugary drinks, ultra-processed foods and discretionary treats \u2014 still stands, backed by a deep body of evidence. What the researchers tested was something narrower and more extreme: the complete elimination of sucrose from an otherwise balanced, low-fat diet. Trimming excess and abolishing sugar entirely, the study suggests, are different interventions that may lead to very different places.

The likely mechanism is the gut. Dietary carbohydrates, including some sugar, appear to help feed and balance the community of microbes that regulate metabolism and inflammation. Starve that ecosystem too aggressively, and the balance can tip the wrong way. As one of the researchers put it, healthy eating may be less about banishing a single ingredient and more about sustaining a diverse, well-fed population of gut bacteria.

## Why It Matters for the Diaspora

Few communities are as sugar-conscious \u2014 and as sugar-anxious \u2014 as the Indian diaspora. With type 2 diabetes running high among South Asians, "sugar-free" has become an aspirational label in NRI kitchens, on restaurant menus and at family gatherings, where forgoing mithai, sweetened chai and white rice is treated as an unambiguous good. Many diaspora households swing hard toward total elimination, equating zero sugar with maximum health.

This study is a gentle corrective to that instinct. It does not say indulge; it says that the leap from moderation to absolute restriction may not deliver the payoff people expect, and could even undercut gut and metabolic health. For a community that often frames food in terms of strict permission and prohibition, the more useful frame may be balance: cut the genuine excess \u2014 the sodas, the syrupy sweets, the refined-carb overload \u2014 while keeping a varied, fiber-rich diet that keeps the gut's microbial tenants fed.

Until human trials confirm whether the effect holds in people, the practical takeaway is modest but freeing. The goal of healthy eating is not a number as low as zero. It is a pattern the body, and the trillions of microbes living in it, can actually thrive on."""
})

# ============================================================
# ARTICLE 3: Jio Platforms files DRHP for India's biggest IPO (markets-finance)
# ============================================================
articles.append({
    "headline": "Ambani's Jio Files for What Could Be India's Biggest IPO Ever \u2014 and This Time, No One Is Cashing Out",
    "subheadline": "Jio Platforms has filed draft papers with India's markets regulator for a fresh-issue-only listing of up to 27 crore shares, a deal market estimates put near \u20b936,000 crore at a valuation of roughly \u20b912.5 lakh crore \u2014 with the proceeds aimed squarely at paying down debt rather than handing existing investors an exit.",
    "slug": "jio-platforms-drhp-sebi-fresh-issue-ipo-27-crore-shares-india-largest-listing-ambani-nri-investor-20260622-1000",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Jio touches nearly every Indian family with a phone, and its listing is the marquee event NRI investors have waited years for \u2014 a chance to own a slice of the diaspora's most-used digital utility, even as the fresh-issue-only structure and a cooled, war-rattled market raise real questions about price and timing.",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine \u2014 Reliance Jio Board approves DRHP for IPO before SEBI on June 19", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Reuters \u2014 Ambani's Jio Platforms IPO pivots to pure fundraising, no investor exits", "url": "https://www.reuters.com/"},
        {"name": "Inc42 \u2014 Jio Files For DRHP For A Fresh Issue-Only IPO", "url": "https://inc42.com/"}
    ]),
    "body": """It has been promised, deferred and dissected for years. On Friday, Mukesh Ambani finally set the clock ticking: Jio Platforms, the telecom-and-technology arm of Reliance Industries, filed its draft papers for a stock-market listing that could be the largest in India's history.

## The Deal on Paper

The board of Jio Platforms approved its Draft Red Herring Prospectus \u2014 the formal disclosure document that opens an IPO process \u2014 on June 19 and lodged it with the Securities and Exchange Board of India, the BSE and the NSE the same day. The offering is structured as a fresh issue of up to 27 crore equity shares, each with a face value of \u20b910, at a price to be set through book-building.

The numbers, even in draft form, are staggering. Market estimates peg the raise at up to roughly \u20b936,000 crore, valuing Jio Platforms at about \u20b912.5 lakh crore. Brokerages put the company's worth at somewhere between $130 billion and $180 billion \u2014 a range that, at the top end, would make this one of the largest public offerings ever attempted in the country. Reliance has not yet disclosed a final issue size; the public portion is widely speculated to be around $4 billion.

Calling it "a deeply emotional moment," Ambani told shareholders at Reliance's annual general meeting that his children \u2014 Akash, Isha and Anant Ambani \u2014 are leading the IPO process. The listing, he said, would "demonstrate to the world that India can build technology companies of global scale, global capability and global value."

## Why "Fresh Issue Only" Matters

The most consequential detail is structural. Earlier plans had cast the IPO as an "offer for sale," in which existing shareholders \u2014 including marquee backers Meta, with a 9.99 percent stake, and Google, with 7.73 percent, alongside Gulf sovereign funds and private-equity giants such as KKR and Vista \u2014 would sell down part of their holdings and cash out. That has been scrapped.

Instead, every rupee raised will come from new shares, with none of the early investors heading for the door. "Investors were not keen to sell and wanted to stay invested for the long term," one source involved told Reuters. The signal to the market is pointed: the people who know Jio best want to keep their chips on the table.

The money has a clear destination. According to the prospectus, the bulk of the net proceeds \u2014 about \u20b927,500 crore \u2014 will go to prepay or repay borrowings of Reliance Jio Infocomm, including external commercial loans taken on in 2024, with the remainder reserved for general corporate purposes. This is a deleveraging story as much as a growth story: a listing designed to clean up the balance sheet of a business that already serves more than 500 million subscribers, the world's second-largest telecom operator by users after China Mobile.

## A Tricky Moment to List

The timing is anything but serene. India's equity markets have cooled in recent months, rattled by the West Asia conflict, volatile oil and a record exodus of foreign portfolio money \u2014 more than $30 billion pulled from Indian stocks so far in 2026. The benchmark indices have whipsawed, and the IT sector just touched a three-year low. Jio is stepping into that crosswind, and it is not alone: the NSE, India's largest stock exchange, filed its own draft papers a day earlier, setting up a crowded second half of the year for Indian listings.

A draft filing is also only the starting gun. SEBI approval, final pricing and the eventual listing date all lie ahead, and the headline valuation could shift before shares ever trade.

## Why It Matters for NRIs

For the diaspora, this is the listing many have waited the better part of a decade to see. Jio is woven into the daily life of nearly every Indian family with a smartphone \u2014 the data plan, the digital payments, the streaming, increasingly the AI services Ambani keeps promising. Owning a piece of it carries an emotional pull that few other Indian stocks can match, a chance to hold equity in the diaspora's most-used digital utility.

But sentiment is not a strategy. The fresh-issue-only design means NRIs would be buying new shares to fund debt repayment and expansion, not stepping in as insiders step out \u2014 a structure that can be read as confidence, or as a company raising capital on its own terms. The valuation is rich, the market is jittery, and the final price is unknown. For NRIs weighing whether to participate through permitted routes, the prudent posture is the same as for any blockbuster IPO: separate the pride of ownership from the arithmetic of price, and wait for the numbers the draft does not yet reveal."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["healthy vegetables fruits diet plate", "person exercising walking outdoors fitness", "fresh vegetables healthy food"],
                          ["healthy diet vegetables exercise", "fresh vegetables fruit plate"], None),
    articles[1]["slug"]: (["sugar cubes white sugar", "table sugar bowl spoon", "refined sugar food"],
                          ["sugar cubes bowl", "white sugar spoon"], None),
    articles[2]["slug"]: (["Reliance Jio store India", "Mukesh Ambani", "Bombay Stock Exchange building Mumbai"],
                          ["mumbai stock exchange building", "indian smartphone telecom"], None),
}
img_captions = {
    articles[0]["slug"]: "A 21-year trial found an intensive diet-and-exercise program, not metformin, lowered the long-term risk of multiple chronic diseases",
    articles[1]["slug"]: "A new study suggests removing sugar entirely from a low-fat diet may disrupt the gut microbiome and metabolic health",
    articles[2]["slug"]: "Jio Platforms has filed draft papers for what could become India's largest-ever initial public offering",
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
