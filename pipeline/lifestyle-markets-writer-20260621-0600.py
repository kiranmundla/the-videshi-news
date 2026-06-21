#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-21 06:00 UTC batch.
Topics:
  1. Everyday painkillers (NSAIDs — ibuprofen, naproxen, diclofenac; plus
     gabapentinoids/opioids) carry under-appreciated risks to the heart, kidneys,
     weight and sleep — UAB (Life Sciences), Denmark 6M-adult study (BMJ),
     Newcastle/UK Biobank 133,000 (PLOS ONE) — lifestyle-health
  2. Microplastics may worsen fatty liver disease on a high-fat diet — University of
     Oklahoma, Science Advances, mouse MASH model, spatial transcriptomics, PPAR-alpha — lifestyle-health
  3. NSE files for India's biggest-ever IPO (~Rs 30,000 cr / $3.3B), a pure offer-for-sale
     of ~6% / 14.89 cr shares, valuing the bourse near Rs 5 lakh cr ($57B) after a
     decade-long wait — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0621f.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0621f.bin"):
            with open("/tmp/_img_dl0621f.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0621f.bin")
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
# ARTICLE 1: Everyday painkillers carry hidden risks (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Painkiller in Your Medicine Cabinet May Be Quietly Taxing Your Heart and Kidneys, New Research Warns",
    "subheadline": "A run of new studies \u2014 including a Danish analysis of more than six million adults \u2014 finds that everyday pain relievers such as diclofenac, ibuprofen and naproxen can raise the risk of heart attacks, strokes and kidney strain, especially in people who already have heart trouble or diabetes.",
    "slug": "everyday-painkillers-nsaids-diclofenac-heart-kidney-risk-denmark-bmj-newcastle-biobank-diaspora-20260621-0600",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry an unusually high burden of early heart disease and diabetes, and over-the-counter painkillers are a fixture of NRI medicine cabinets \u2014 reached for at the first headache, body ache or fever \u2014 so a body of research showing these common drugs can quietly strain the very organs the community is most vulnerable in is a direct, practical caution for diaspora households.",
    "sources": json.dumps([
        {"name": "Knowridge \u2014 Everyday Painkillers May Have Unexpected Health Risks", "url": "https://knowridge.com/2026/06/everyday-painkillers-may-have-unexpected-health-risks/"},
        {"name": "The BMJ \u2014 Danish cohort study of diclofenac and cardiovascular risk (6 million+ adults)", "url": "https://www.bmj.com/"},
        {"name": "PLOS ONE \u2014 Newcastle University / UK Biobank analysis of gabapentinoids, weight and sleep (133,000+ participants)", "url": "https://journals.plos.org/plosone/"}
    ]),
    "body": """Few things feel as harmless as reaching for a painkiller. A headache, a sore back, a fever, the ache of arthritis \u2014 millions of people around the world swallow a pill and get on with their day. Many of these medicines sit on supermarket shelves without a prescription, which makes them feel as routine as a cup of tea. A run of new research is a reminder that routine is not the same as risk-free.

## The Drugs in Question

The biggest group of everyday pain relievers is the non-steroidal anti-inflammatory drugs, or NSAIDs. They cut both pain and swelling, which is why they are reached for so often \u2014 for headaches, muscle injuries, joint pain and arthritis. The familiar names are ibuprofen, naproxen and diclofenac.

Researchers at the University of Alabama at Birmingham recently studied an NSAID called carprofen in animals that already had heart disease. They found the drug caused mild inflammation in both the heart and the kidneys. When the animals then suffered a heart attack, that inflammation worsened \u2014 a signal that certain NSAIDs could deepen the danger for people whose hearts are already compromised. The work was published in the journal Life Sciences.

## A Study of Six Million Adults

The most striking warning came out of Denmark, where scientists examined health records from more than six million adults. People who started taking diclofenac had a higher chance of developing serious heart problems \u2014 heart attacks, strokes and irregular heartbeats \u2014 within just one month of beginning the drug.

The risk was greater than for people taking other NSAIDs such as ibuprofen and naproxen, and higher than for those using paracetamol, known as acetaminophen in some countries. The researchers, writing in The BMJ, concluded that diclofenac may be particularly hazardous for people who already have heart concerns. That matters because diclofenac is widely available across South Asia and in diaspora pharmacies, often bought without a second thought.

## It Is Not Only the Heart

Pain management reaches beyond NSAIDs. People with long-term or nerve-related pain are sometimes prescribed opioids or a class of drugs called gabapentinoids, which includes gabapentin and pregabalin. These can be genuinely helpful for severe pain \u2014 but they carry their own quiet costs.

Researchers at Newcastle University in the United Kingdom examined data from more than 133,000 participants in the UK Biobank. People taking these medications were more likely to be overweight and to sleep poorly. The likely reasons are intertwined: some of the drugs are sedating, leaving people drowsy and less active during the day; some appear to stoke cravings for sweet foods or change how food tastes. Less movement and more sugar, over time, add up. That study appeared in PLOS ONE.

## What the Findings Do \u2014 and Don't \u2014 Say

None of this means pain relief is the enemy. These medicines let people work, sleep and move when pain would otherwise stop them, and for short-term use at the lowest effective dose they remain reasonable for many. The point the researchers press is more measured: these are not sweets, and they are not free of consequence \u2014 particularly for people who already carry heart disease, kidney trouble or diabetes.

The practical guidance is sensible and undramatic. Use the smallest dose that works, for the shortest time that works. For ongoing pain, weigh non-drug options \u2014 physical therapy, gentle exercise, stretching, relaxation techniques \u2014 alongside or instead of a daily pill. And anyone who relies on pain medicine long-term should be checking in with a doctor and watching for side effects rather than quietly topping up from the cabinet.

## Why It Matters for the Diaspora

For Indian-origin families, the caution lands close to home. South Asians develop heart disease and type 2 diabetes earlier and at lower body weights than many other groups \u2014 the very conditions that make these painkillers riskiest. Yet the over-the-counter pill is a diaspora staple, a reflex for every body ache, fever or hangover-grade headache, and often shared across a household without much thought to dose or duration.

The takeaway is not fear, but attention. A painkiller now and then for a genuine ache is not what these studies are warning about. Daily, casual, indefinite use \u2014 especially by parents and elders already managing blood pressure, blood sugar or a weak heart \u2014 is. For a community that loses too many of its own to heart disease too young, knowing that the humble tablet in the kitchen drawer has a cost worth respecting is its own kind of preventive medicine."""
})

# ============================================================
# ARTICLE 2: Microplastics and fatty liver (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Microplastics May Hit the Liver Hardest When the Diet Is Already Rich, a New Study Finds",
    "subheadline": "University of Oklahoma researchers report that a common plastic doubled markers of liver injury in mice on a high-fat diet compared with the same particles on a standard diet \u2014 the clearest sign yet that microplastics and a rich diet may compound each other's harm.",
    "slug": "microplastics-fatty-liver-disease-high-fat-diet-oklahoma-science-advances-ppar-alpha-mash-diaspora-20260621-0600",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Fatty liver disease is quietly common in Indian-origin populations, who develop it at lower body weights than other groups, and diaspora kitchens lean heavily on plastic \u2014 takeaway containers, cling film, bottled water and reheated leftovers \u2014 so a finding that microplastics may bite hardest precisely when the diet is rich speaks directly to a community already at elevated metabolic risk.",
    "sources": json.dumps([
        {"name": "Medical Xpress \u2014 Microplastics may worsen fatty liver disease, new study suggests (University of Oklahoma)", "url": "https://medicalxpress.com/news/2026-06-microplastics-worsen-fatty-liver-disease.html"},
        {"name": "Science Advances \u2014 Jung et al, 'Spatial transcriptome mapping identifies Ppara-Anxa2 cross-talk in microplastic-induced hepatotoxicity'", "url": "https://www.science.org/doi/10.1126/sciadv.aec8681"}
    ]),
    "body": """Microplastics \u2014 the tiny fragments that break off from larger plastic waste \u2014 have turned up in human blood, lungs and even placentas. We inhale them, swallow them and wear them on our skin. A new study suggests they may be most damaging to the liver precisely when the diet is already working that organ hard.

## What the Researchers Did

The work, from the University of Oklahoma and published in the journal Science Advances, was carried out in mice. Researchers gave the animals equal amounts of microplastics over eight weeks. The key difference was the food: some mice ate a standard diet, while others were fed a diet designed to model metabolic dysfunction-associated steatohepatitis, or MASH \u2014 a serious form of fatty liver disease.

The contrast was stark. Blood markers of liver injury were more than twice as high in the mice exposed to microplastics while eating the high-fat diet, compared with mice given the same particles on a normal diet. The plastic in question was polyethylene, the most common type, found in everyday objects such as plastic bags and milk jugs.

"We expected to see a synergistic effect between the diet and microplastics, and we did," said Tae Gyu Oh, the assistant professor of oncology science who led the study. In other words, the diet and the plastic did not simply add up \u2014 together they appeared to multiply the harm.

## A First Look Inside the Cells

To understand what was happening, the team used a technique called spatial transcriptomics, which maps gene activity in exact locations within tissue rather than averaging it across millions of cells. The researchers believe this is the first time the technology has been used in this context.

The high-resolution view let them pinpoint "hot spots" of liver damage at the single-cell level \u2014 regions of inflammation and disrupted biology that older methods would have blurred over. They also identified a gene regulator called PPAR-alpha, a protein that governs how the body breaks down and uses fat for energy. It influences another gene, Anxa2, involved in tissue repair. The findings suggest microplastics may interfere with the liver's own defence and repair machinery.

## The Caveats Matter

This is a mouse study, and an important one to keep in proportion. It does not prove that microplastics cause fatty liver disease in people, nor does it quantify how much exposure a human would need before harm follows. What it does is establish a framework \u2014 a plausible mechanism and a clear signal that a rich diet and plastic exposure may compound each other. Human research will have to test whether the same cross-talk plays out in people.

"Microplastics are now part of our everyday environment, but we are still learning how they affect the body," Oh said. The study, he added, points to "areas for future investigation" rather than firm conclusions.

## Why It Matters for the Diaspora

For the Indian diaspora, the study touches two sensitive nerves at once. Fatty liver disease is quietly widespread among South Asians, who tend to accumulate visceral fat and develop metabolic trouble at lower body weights than other populations \u2014 the very profile the study modelled. And plastic is woven through the modern diaspora kitchen: takeaway containers, cling-filmed leftovers, bottled water, and food reheated in plastic tubs.

The sensible response is not panic but a few low-effort habits that reduce exposure while the science matures. Avoid microwaving food in plastic, which can shed particles into hot food; lean on glass or steel for storage and reheating; cut down on single-use bottled water where tap or filtered water will do. None of that replaces the fundamentals of liver health \u2014 a diet that is not relentlessly high in fat and refined carbohydrate, regular movement, and limited alcohol. But for a community already carrying more than its share of metabolic risk, the message is worth hearing: the plastic and the plate may be working on the liver together, and both are within reach to change."""
})

# ============================================================
# ARTICLE 3: NSE files for India's biggest-ever IPO (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Biggest Stock Exchange Is Finally Going Public \u2014 in What Could Be the Country's Largest IPO Ever",
    "subheadline": "After a decade of delays, the National Stock Exchange has filed papers for a roughly Rs 30,000 crore ($3.3 billion) listing \u2014 a pure sale of existing shares that could value the bourse near Rs 5 lakh crore and hand its long-locked-in investors a multi-billion-dollar windfall.",
    "slug": "nse-files-record-ipo-30000-crore-offer-for-sale-5-lakh-crore-valuation-decade-wait-nri-investor-20260621-0600",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "The NSE is the exchange on which most of the Indian shares and funds that NRIs own actually trade, so its own market debut \u2014 potentially India's largest ever \u2014 is both a marquee investment opportunity for diaspora portfolios and a barometer of how much appetite global money still has for Indian equities after a bruising year of outflows.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India's long-delayed NSE IPO sets up $2.6 billion windfall for top investors", "url": "https://www.reuters.com/world/india/"},
        {"name": "Outlook Business \u2014 NSE IPO Takes Off: Exchange Files Draft Papers For Rs 30,000 Crore Offer", "url": "https://www.outlookbusiness.com/"}
    ]),
    "body": """India's largest stock exchange has spent a decade trying to do something millions of its listed companies do as a matter of course: sell shares to the public. This week the National Stock Exchange finally took the decisive step, filing its draft red herring prospectus with the market regulator and the rival Bombay Stock Exchange. The offering could become the biggest initial public offering in India's history.

## The Shape of the Deal

The NSE is the country's largest bourse and the world's most active derivatives exchange \u2014 the venue on which the overwhelming majority of Indian shares and equity funds actually change hands. Its IPO is structured entirely as an offer for sale, meaning existing shareholders will sell roughly 6 percent of the exchange's equity \u2014 about 14.89 crore shares \u2014 and the exchange itself will raise no fresh capital.

Based on the NSE's estimated unlisted-market valuation of around Rs 5 lakh crore, market participants expect the issue to be worth roughly Rs 30,000 crore, or about $3.3 billion. That would edge past Hyundai Motor India's Rs 27,870 crore offering from 2024 to become the largest IPO India has ever seen. The exchange reported a net profit of Rs 10,302 crore on revenue of Rs 16,601 crore in the last financial year \u2014 a reminder that, as a near-monopoly toll-collector on India's trading boom, it is extraordinarily profitable.

In a neat twist, the NSE's shares will be listed on the BSE, mirroring the arrangement under which BSE's own shares trade on the NSE.

## A Windfall a Decade in the Making

For the exchange's long-locked-in shareholders, the listing is a payday years overdue. Investors ranging from Indian state-owned lenders to Singapore's sovereign wealth fund and Canada's national pension manager stand to share a windfall estimated at around $2.6 billion.

The State Bank of India is the largest seller, offering up to 24.75 million shares. Canada Pension Plan Investment Board is parting with up to 11.87 million, alongside Mauritius-based investors MS Strategic and Aranda Investments and a clutch of public-sector insurers including GIC Re, New India Assurance and United India Insurance. Notably, Life Insurance Corporation of India \u2014 one of the NSE's key shareholders \u2014 is sitting this round out and not selling.

The exchange's shares change hands at close to Rs 2,000 in the unlisted market, implying a valuation of some $57 billion. That would make the NSE the world's fifth most valuable exchange operator, behind only the likes of the London Stock Exchange Group. Bankers say the IPO may be priced at a 5 to 10 percent discount to that private-market level \u2014 around Rs 1,900 a share \u2014 to leave something on the table for new investors without short-changing those getting out.

## Why the Long Wait

The NSE first tried to list back in 2016, only to be derailed by regulatory scrutiny and the long-running "co-location" controversy, which raised questions about whether some traders had gained unfair, faster access to its systems. Years of investigations and settlements followed. A recent settlement in the co-location case and a No Objection Certificate from the market regulator earlier this year finally cleared the path. With more than 200,000 shareholders already on its register, the exchange comes to market with unusually broad ownership.

## Why NRIs Should Care

For the Indian diaspora, the NSE listing is more than another marquee IPO. This is the plumbing of the market itself \u2014 the exchange on which the Indian stocks, index funds and ETFs in NRI portfolios are bought and sold. Owning a slice of it is, in effect, a bet on the long-term growth of Indian capital markets rather than on any single company's fortunes.

The timing is pointed. The IPO lands after a punishing stretch in which foreign investors pulled a record amount out of Indian equities and the benchmark Sensex shed close to a tenth of its value for the year, buffeted by the Middle East conflict and a weak rupee. A successful, heavily subscribed NSE debut would be read as a vote of confidence that global and domestic money still believe in the India story; a tepid one would say the opposite. Either way, diaspora investors weighing whether to apply should remember the basics that apply to any IPO \u2014 the offer is existing investors cashing out rather than fresh money funding growth, the valuation is rich, and the eventual listing price, not the hype, is what determines the return. The plumbing is finally going public; whether it is a bargain is a separate question."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["ibuprofen tablets pills medication", "painkiller pills blister pack", "medicine tablets pills"],
                          ["pills medication tablets", "painkiller medicine pills"], None),
    articles[1]["slug"]: (["microplastics plastic pollution water", "plastic bottles waste pollution", "plastic food containers"],
                          ["plastic bottles pollution", "microplastics water"], None),
    articles[2]["slug"]: (["National Stock Exchange India building Mumbai", "Bombay Stock Exchange building", "stock exchange trading screen India"],
                          ["stock exchange building", "stock market trading floor"], None),
}
img_captions = {
    articles[0]["slug"]: "New research links common painkillers such as ibuprofen, naproxen and diclofenac to raised heart and kidney risk",
    articles[1]["slug"]: "A University of Oklahoma study found microplastics doubled liver-injury markers in mice on a high-fat diet",
    articles[2]["slug"]: "The National Stock Exchange has filed for what could be India's largest-ever IPO, a roughly Rs 30,000 crore offer for sale",
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
