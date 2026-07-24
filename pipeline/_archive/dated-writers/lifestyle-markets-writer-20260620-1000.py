#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-20 10:00 UTC batch.
Topics:
  1. ENDO 2026 (Dasman Diabetes Institute, Kuwait): a totally sugar-free diet may
     disrupt gut microbiome, raise inflammation & metabolic dysfunction (mouse study) — lifestyle-health
  2. UCLA AD-NP1 (Cell Stem Cell): first-in-class heart-repair drug blocking ENPP1
     may also heal injured kidney tissue — lifestyle-health
  3. NSE files DRHP for ~Rs 30,000 cr pure-OFS IPO — India's largest ever,
     ~Rs 5 lakh crore valuation — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0620c.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0620c.bin"):
            with open("/tmp/_img_dl0620c.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0620c.bin")
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
# ARTICLE 1: Zero-sugar diet may harm gut health (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Cutting Sugar Out Completely May Backfire on Your Gut, a New Study Warns",
    "subheadline": "Researchers who fed mice a diet with no table sugar at all found their gut bacteria fell out of balance and inflammation rose \u2014 a caution for anyone who treats 'zero sugar' as the holy grail of healthy eating.",
    "slug": "zero-sugar-sucrose-free-diet-gut-microbiome-inflammation-dasman-endo-2026-diaspora-20260620-1000",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Sugar has become the villain in many health-conscious NRI kitchens, where 'no sugar' is now a badge of discipline \u2014 but this research suggests that scrubbing sucrose out entirely, rather than simply eating less of it, may quietly unsettle the gut.",
    "sources": json.dumps([
        {"name": "Fox News \u2014 Zero sugar, more problems? Study reveals surprising gut health effects (ENDO 2026; Dasman Diabetes Institute, Kuwait City; Rasheed Ahmad)", "url": "https://www.foxnews.com/health/zero-sugar-more-problems-study-reveals-surprising-gut-health-effects"},
        {"name": "ENDO 2026 \u2014 Endocrine Society Annual Meeting, Chicago (June 2026)", "url": "https://www.endocrine.org/"}
    ]),
    "body": """For years, the message in health-conscious kitchens has been blunt: sugar is the enemy. Across the diaspora, cutting it out has become a kind of moral achievement \u2014 no sugar in the chai, no mithai, no "white poison." But new research presented at the Endocrine Society's annual meeting suggests that going to the other extreme, eliminating table sugar entirely, may carry its own hidden costs for the gut.

## What the Researchers Did

Scientists at the Dasman Diabetes Institute in Kuwait City set out to test what happens to the body when dietary sugar is removed altogether. Over 16 weeks, they fed two groups of mice a low-fat diet. The only difference between them was sucrose \u2014 ordinary table sugar. One group's food contained a standard amount of it; the other group's food had none at all.

Throughout the study, the researchers tracked a wide range of measures: body weight, glucose tolerance, insulin sensitivity, hormone levels, internal inflammation, and the specific mix of bacteria living in the animals' guts.

## The Surprising Result

The mice on the completely sugar-free diet did not gain extra weight. On the scale, they looked fine. But beneath the surface, their internal health markers told a different story.

"Completely removing sucrose from a low-fat diet may unexpectedly disrupt gut health and promote inflammation and metabolic dysfunction," said Rasheed Ahmad, principal scientist and head of the Immunology and Microbiology Department at the Dasman Diabetes Institute, in a statement accompanying the research.

The animals deprived of sugar developed an imbalance in their gut microbes and showed increased inflammation in both the intestines and the liver. In other words, the absence of sucrose appeared to nudge the body toward exactly the kind of low-grade inflammation that doctors associate with long-term metabolic trouble.

## Why This Is Counterintuitive

It runs against the grain of conventional wisdom. Excess sugar is firmly linked to obesity, type 2 diabetes, fatty liver disease and tooth decay, and cutting back genuinely helps most people. The finding here is narrower but important: total elimination is not the same as moderation, and the gut, it turns out, may rely on some sucrose to keep its ecosystem in balance.

A crucial caveat: this was a study in mice, not humans, and animal results do not translate directly to people. It also tested the complete removal of sugar, an extreme that very few real diets reach. The takeaway is not that anyone should eat more sweets \u2014 the dangers of overconsumption remain well established.

## What It Means for Diaspora Households

For Indian families, sugar sits in a complicated place. Diabetes is widespread in the community, so the instinct to banish it is understandable and often medically sound. But the wellness culture that has grown up around "zero sugar" and "sugar-free" labels can tip into an all-or-nothing mindset, where any sucrose is treated as toxic.

This research is a reminder that the body is rarely served by extremes. The healthier path is almost always moderation: less added sugar, fewer sweetened drinks and desserts, more whole foods and fibre that feed a diverse gut microbiome \u2014 not a fanatical zero. The dal, vegetables and whole grains at the heart of a traditional Indian plate already do much of that work, nourishing the very gut bacteria the study found could suffer when the diet swings too far.

The science of the microbiome is still young, and a single mouse study will not rewrite dietary guidelines. But it adds a useful note of humility for the home cook scanning labels for the word "sugar." The goal, as ever, is balance \u2014 not a war."""
})

# ============================================================
# ARTICLE 2: Heart-repair drug may also heal kidneys (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Drug Designed to Mend Broken Hearts May Also Heal Damaged Kidneys, Early Research Suggests",
    "subheadline": "An experimental UCLA compound built to help hearts recover after a heart attack appears to repair injured kidney tissue too \u2014 a tantalising prospect for the millions of South Asians living with both heart and kidney disease.",
    "slug": "experimental-heart-drug-ad-np1-enpp1-heals-kidney-tissue-ucla-cell-stem-cell-diaspora-20260620-1000",
    "category": "lifestyle-health",
    "vertical": "medical-research",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry a famously high burden of both heart disease and chronic kidney disease \u2014 conditions that often travel together with diabetes \u2014 so a single drug that might help repair both organs is exactly the kind of breakthrough that could one day matter in NRI households.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 Experimental first-in-class heart drug may also help heal kidneys (UCLA; Arjun Deb; AD-NP1; ENPP1)", "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/"},
        {"name": "Cell Stem Cell \u2014 UCLA research on ENPP1 blockade and tissue repair", "url": "https://www.cell.com/cell-stem-cell/home"}
    ]),
    "body": """Most drugs are designed to do one job in one organ. Every so often, scientists stumble on a molecule that may do more. New laboratory research from UCLA suggests that an experimental drug created to help the heart recover after a heart attack might also help heal damaged kidneys \u2014 two organs that, for millions of people of South Asian descent, tend to fail together.

## The Drug and the Discovery

The compound, called AD-NP1, is under development at UCLA and has recently been green-lighted for early human trials. Its purpose is to help the heart avoid failure after a heart attack. It works by blocking a protein called ENPP1, which interferes with the body's natural healing and prevents heart tissue from fully recovering after injury.

While studying that protein, the researchers noticed something. When they examined kidney biopsies from people with chronic kidney disease, they found the same ENPP1 protein present at much higher levels than in healthy tissue. The protein that sabotages heart repair appeared to be doing similar damage in the kidney.

## What the Experiments Showed

To test whether blocking ENPP1 could help, the team turned to mice. They induced kidney injuries in normal mice and in mice genetically engineered to lack ENPP1. At first, all the animals showed some damage. But weeks later, the mice without the protein had markedly better outcomes: enhanced kidney repair, reduced scarring, and improved kidney function. The findings were reported in the journal Cell Stem Cell.

The researchers then went a step further, inducing kidney damage in ordinary mice and treating them with the actual drug, AD-NP1. One week later, those mice showed improved kidney function and signs of healing.

"We found that the same mechanisms we observed in the heart were also applicable in the kidney," said study leader Arjun Deb of UCLA in a statement. He explained that the ENPP1 protein interferes with critical pathways cells need to derive energy \u2014 starving injured tissue of the fuel it needs to repair itself.

## An Important Note of Caution

This is early-stage science. The kidney results come from experiments in mice and laboratory tissue, not from patients, and the long road from a promising animal study to an approved treatment is littered with drugs that worked in mice but failed in humans. The heart programme has only just reached pilot human trials; a kidney indication would be further still.

Even so, the appeal of a single drug that targets a shared mechanism of tissue damage across two vital organs is obvious. Development of the first-in-class compound has been backed by the U.S. National Institutes of Health, the Department of Defense, and the California Institute for Regenerative Medicine.

## Why It Resonates for the Diaspora

For Indian and wider South Asian communities, this line of research lands close to home. The community faces an outsized burden of heart disease, often striking earlier and harder than in other populations. Chronic kidney disease frequently follows, driven by the same underlying culprits \u2014 diabetes and high blood pressure \u2014 that are also widespread among NRIs.

Today, treatment for failing kidneys often means a grinding routine of dialysis or the long wait for a transplant, both of which weigh heavily on patients and families alike. A therapy that could actually coax damaged kidney tissue to repair itself, rather than merely slowing the decline, would be transformative \u2014 potentially sparing people years of dialysis and easing the chronic shortage of donor organs. That future, if it arrives at all, is years away, and much can go wrong between a mouse study and a medicine on the shelf. But the discovery that one mechanism may underlie damage in both the heart and the kidney is the kind of insight that can open new doors \u2014 and for a community that bears more than its share of both diseases, it is worth watching closely."""
})

# ============================================================
# ARTICLE 3: NSE files for India's largest-ever IPO (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Biggest Stock Exchange Is Finally Going Public \u2014 in What Could Be the Country's Largest IPO Ever",
    "subheadline": "After a decade of delays and a co-location scandal, the National Stock Exchange has filed for a roughly Rs 30,000 crore listing that values the bourse near Rs 5 lakh crore \u2014 a pure offer-for-sale that hands existing investors a giant payday.",
    "slug": "nse-files-drhp-largest-ipo-india-30000-crore-offer-for-sale-5-lakh-crore-valuation-nri-investor-20260620-1000",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "For NRIs who already invest in Indian equities \u2014 and increasingly can, after recent RBI moves to open repatriable rupee accounts \u2014 the listing of the exchange that powers India's markets is both a landmark and a potential portfolio addition worth understanding before the hype builds.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India's long-delayed NSE IPO sets up $2.6 billion windfall for top investors", "url": "https://www.reuters.com/world/india/"},
        {"name": "Outlook Business \u2014 NSE IPO: The 10-Year Wait, Rs 5-Lakh-Cr Valuation And Big Questions Ahead", "url": "https://www.outlookbusiness.com/"}
    ]),
    "body": """The institution that sits at the very centre of India's stock market is, at last, preparing to join it. The National Stock Exchange \u2014 the country's largest bourse and the world's busiest derivatives exchange \u2014 has filed its draft prospectus for an initial public offering that could become the biggest in India's history.

## The Numbers

NSE filed its Draft Red Herring Prospectus with the market regulator SEBI and with rival exchange BSE, where its shares will list. The offering is structured as a pure offer for sale: existing shareholders will collectively sell up to roughly 148.9 million shares, equal to about 6 percent of the exchange's equity. NSE itself will raise no fresh capital.

Based on the exchange's unlisted-market valuation of around Rs 5 lakh crore, market participants estimate the issue size at close to Rs 30,000 crore. That would surpass Hyundai Motor India's Rs 27,870 crore listing in 2024 to become the largest IPO India has ever seen. In the grey market, NSE shares already change hands near Rs 2,000 apiece, with the offer expected to come at a modest discount to that level.

The exchange is enormously profitable. For the financial year ended March 2026, NSE reported total income of around Rs 18,700 crore and a net profit of about Rs 10,302 crore \u2014 a reminder that the company running India's markets is itself one of the country's great cash machines.

## A Decade in the Making

The road here has been long and bruising. NSE first filed to go public back in December 2016, aiming to list within a year at a valuation of Rs 40,000 to 45,000 crore. Then the co-location scandal broke. SEBI found that certain high-frequency trading firms had been granted preferential, faster access to NSE's servers, handing them a split-second edge over ordinary traders.

The fallout was severe: in 2019 SEBI barred the exchange from accessing capital markets for six months and ordered it to disgorge hundreds of crores. The IPO was shelved indefinitely, and years of appeals and governance overhauls followed. Only in January 2026 did SEBI grant an in-principle settlement, clearing the final regulatory hurdle. The board approved the listing in February, and the prospectus landed in June.

The exchange that was valued at about Rs 18,200 crore in 2016 is now filing at roughly 27 times that \u2014 the steep price, in a sense, of arriving a decade late to its own party.

## Who Cashes In

Because this is an offer for sale, the proceeds flow to selling shareholders rather than the company. State Bank of India is the largest seller, offering up to 24.75 million shares. Other major sellers include the Canada Pension Plan Investment Board and two Mauritius-based investors, MS Strategic and Aranda Investments. Public-sector institutions such as Bank of Baroda and several state insurers are also paring stakes. Notably, Life Insurance Corporation of India \u2014 a key shareholder \u2014 is sitting this round out. NSE has more than 180,000 shareholders today, and the listing finally gives them a transparent exit.

## What NRIs Should Keep in Mind

For the diaspora, the timing is intriguing. The Reserve Bank of India has recently been opening new doors for non-resident investors, including a repatriable rupee account that makes it easier for individual NRIs to buy Indian stocks. A marquee listing like NSE's is exactly the sort of name that draws first-time and overseas investors in.

A few cautions are worth holding onto. This is a pure offer for sale, so no new money goes into growing the business \u2014 buyers are simply taking over existing investors' shares. The valuation is rich, and final pricing will only be set after roadshows, closer to the listing date that SEBI's review will determine. And a mega-IPO of this size arrives just as India's markets have wobbled, testing how much appetite really exists.

Still, the symbolism is hard to miss. The exchange that has quietly powered India's wealth creation for three decades is finally about to let investors own a piece of it \u2014 and for NRIs watching from abroad, it may soon be more than a place where their trades are settled. It could be a line on their own statements."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["sugar cubes white", "sugar crystals food", "gut bacteria microbiome illustration"],
                          ["sugar cubes white background", "white sugar bowl"], None),
    articles[1]["slug"]: (["human kidney anatomy model", "kidney medical illustration", "human heart anatomy model"],
                          ["kidney anatomy medical", "laboratory medical research"], None),
    articles[2]["slug"]: (["National Stock Exchange India building Mumbai", "Bombay Stock Exchange building", "stock market trading screen India"],
                          ["stock market trading screen", "indian rupee finance"], None),
}
img_captions = {
    articles[0]["slug"]: "A 16-week mouse study found that a totally sucrose-free diet disrupted gut bacteria and raised inflammation",
    articles[1]["slug"]: "UCLA's experimental drug AD-NP1, designed to repair heart tissue, also healed injured kidneys in mice",
    articles[2]["slug"]: "The National Stock Exchange has filed for what could be India's largest-ever IPO, worth around Rs 30,000 crore",
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
