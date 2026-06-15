#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-15 18:00 UTC batch.
Topics: OurHealth South Asian genomic biobank, Vitamin D + genes + diabetes, NSE mega-IPO.
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
                results.append({"url": ii.get("thumburl") or ii.get("url", ""),
                                "title": page.get("title", ""), "width": ii.get("width", 0)})
            if results:
                print(f"  ✓ Commons: {len(results)} imgs for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error '{search_query}': {e}")
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
            print(f"  ✓ Pexels img for '{query}'")
            return chosen
    except Exception as e:
        print(f"  ⚠ Pexels error '{query}': {e}")
    return None

def download_bytes(url):
    # try requests first, then curl (Wikimedia 429 / Pexels 403 workaround)
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
    except Exception:
        pass
    try:
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl.bin"):
            with open("/tmp/_img_dl.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl.bin")
            if len(data) > 5000:
                return data
    except Exception as e:
        print(f"  ⚠ download error: {e}")
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
        print(f"  ⚠ compress error: {e}")
        return img_bytes

def upload_to_supabase(img_bytes, filename):
    try:
        url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
                   "Content-Type": "image/jpeg", "x-upsert": "true"}
        r = requests.post(url, headers=headers, data=img_bytes, timeout=60)
        if r.status_code in (200, 201):
            public = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded {filename} ({len(img_bytes)//1024} KB)")
            return public
        else:
            print(f"  ✗ Upload failed {filename}: {r.status_code} {r.text[:150]}")
    except Exception as e:
        print(f"  ⚠ upload error: {e}")
    return None

def source_image(slug, commons_queries, pexels_queries):
    """Try Commons queries, then Pexels queries. Download, compress, upload. Returns (url, attribution)."""
    candidates = []  # (url, attribution)
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
    print(f"  ⚠ No image sourced for {slug}")
    return None, None

# ---------------- DB insert ----------------
def insert_article(article):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
               "Content-Type": "application/json", "Prefer": "return=representation"}
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=headers,
                         json=article, timeout=30)
    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"  ✓ Inserted: {article['slug']} (id: {data[0]['id'] if data else 'ok'})")
        return True
    print(f"  ✗ FAILED: {article['slug']} — {resp.status_code}: {resp.text[:300]}")
    return False

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
articles = []

# ============================================================
# ARTICLE 1: OurHealth South Asian genomic biobank (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Why South Asians Get Heart Disease Younger Has Never Been Answered. A New Genomic Biobank Is Built to Find Out.",
    "subheadline": "The OurHealth Study, a decentralised digital biobank run by the Broad Institute, Harvard, Stanford and Yale, is sequencing the DNA of South Asian Americans from their kitchen tables — and handing them back personalised heart-risk scores. It is one of the first serious attempts to close a genomic blind spot that has left the diaspora flying blind.",
    "slug": "ourhealth-study-south-asian-genomic-biobank-cardiometabolic-risk-polygenic-scores-20260615",
    "category": "lifestyle-health",
    "vertical": "health-science",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry more than double the cardiometabolic disease risk of other groups yet are almost absent from the genomic datasets that drive modern risk prediction and drug development — a gap the OurHealth biobank is specifically designed to close for the US diaspora.",
    "sources": json.dumps([
        {"name": "npj Digital Medicine (Nature)", "url": "https://www.nature.com/articles/s41746-026"},
        {"name": "Broad Institute", "url": "https://www.broadinstitute.org/news/our-health-study"},
        {"name": "OurHealth Study", "url": "https://ourhealthstudy.org"},
        {"name": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov/"}
    ]),
    "body": """For as long as cardiologists have studied the South Asian diaspora, one fact has hovered without an explanation. People of South Asian ancestry develop heart disease, diabetes, and stroke at more than double the rate of other populations, and they do it younger and at lower body weights. Doctors have known this for decades. What they have never had is the data to say precisely why. A new research effort is now built to change that, and its design is as notable as its goal.

The OurHealth Study, described this year in the journal npj Digital Medicine, is a nationwide digital biobank assembling genetic, medical, and lifestyle data from South Asian adults living in the United States. It is run by a heavyweight consortium — the Broad Institute of MIT and Harvard, Massachusetts General Hospital, Harvard Medical School, Stanford School of Medicine, and Yale School of Medicine — and its premise is blunt: you cannot fix a health disparity you have never properly measured.

## The Blind Spot at the Heart of Modern Medicine

Genomic medicine has a representation problem, and South Asians sit squarely inside it. The vast genetic databases that power today's risk prediction tools and drug discovery were built overwhelmingly from people of European descent. That means polygenic risk scores — the statistical tools that estimate a person's inherited risk for a disease — are far less accurate for everyone else.

For a community that already carries the highest cardiometabolic burden of any major group, that is not an abstract inequity. It means a South Asian patient's genetic risk may be systematically mis-estimated, and that treatments and prevention strategies have rarely been tested on the population that needs them most. "A previous study of ours showed that South Asians living in the United Kingdom had double the risk of developing heart disease despite their clinical predicted risk being the same as others around them," said Amit Khera, a co-principal investigator of OurHealth. "This result was striking and it inspired us to build a resource to understand the drivers of this risk."

## A Biobank Run From the Kitchen Table

What makes OurHealth unusual is how it collects its data. There are no clinic queues or hospital visits required. The entire study runs through a digital platform at ourhealthstudy.org, open to adults of South Asian ancestry living in the US. Participants consent online, fill out detailed surveys about medical history, diet, family background, and cultural heritage, and then mail in a saliva sample using a self-collection kit that arrives in the post.

Those saliva samples are sequenced using an advanced method known as blended genome exome sequencing, which combines a broad low-coverage read of the whole genome with a deep, detailed read of the protein-coding regions where many disease-causing variants hide. This approach captures both common and rare variants more effectively across non-European populations than the older gene-chip arrays most studies relied on.

The decentralised, mail-in design is the point. It removes the logistical barriers — time off work, travel, distrust of medical institutions — that have historically kept South Asians out of research, and it lets the study scale across the entire country rather than a single city's hospital catchment.

## Handing the Results Back

Most biobanks are a one-way street: you give your data, and it disappears into a research pipeline you never hear about again. OurHealth is trying something different through a sub-study called OurHealth-PRS, which returns polygenic risk scores for coronary artery disease directly to participants.

That is a meaningful shift. Rather than treating the diaspora purely as research subjects, the study gives participants something actionable about their own inherited heart risk, and then studies how people understand and respond to that information. For a population where heart disease strikes early, knowing your genetic risk in your thirties or forties — while prevention is still possible — could be the difference that clinical guidelines, built on other populations, have failed to provide.

## Why This Matters for Diaspora Families

For NRI families, the value here is twofold. The immediate one is participation: this is a rare chance to be counted in the very dataset that will shape how South Asian heart and metabolic disease is understood and treated for the next generation. Every additional participant sharpens the genetic picture for the whole community, including children growing up in the diaspora who will inherit both the risk and, eventually, the science built to manage it.

The longer-term promise is precision. If OurHealth succeeds in identifying South Asian-specific genetic and lifestyle drivers of cardiometabolic disease, it opens the door to risk scores that actually work for the diaspora, prevention advice tailored to real biology rather than borrowed assumptions, and potentially new drugs developed with this population in mind.

It is, of course, early. A biobank is infrastructure, not a cure, and the discoveries it enables will take years to arrive. But after decades in which the central question — why do we get sick younger? — went unanswered for lack of data, the diaspora finally has a study built specifically to ask it. The first step toward an answer is simply being counted, and for once, the data is being gathered from the community itself."""
})

# ============================================================
# ARTICLE 2: Vitamin D, genes & diabetes (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Vitamin D Cuts Diabetes Risk — but Only If Your Genes Cooperate. A New Study Explains Who Actually Benefits.",
    "subheadline": "Tufts researchers analysing DNA from over 2,000 trial participants found that vitamin D meaningfully lowered the risk of type 2 diabetes in people with certain variations of the vitamin D receptor gene, and did nothing for the roughly one in three who carry a different variant. For a diaspora plagued by both vitamin D deficiency and diabetes, it is a clue worth understanding.",
    "slug": "vitamin-d-receptor-gene-variant-diabetes-prevention-tufts-study-south-asian-deficiency-20260615",
    "category": "lifestyle-health",
    "vertical": "nutrition",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians suffer from unusually high rates of both vitamin D deficiency and type 2 diabetes, making the question of who actually benefits from supplementation — and why the answer may be written in their genes — directly relevant to millions of diaspora families.",
    "sources": json.dumps([
        {"name": "Tufts University", "url": "https://now.tufts.edu/2026/04/vitamin-d-diabetes-genes"},
        {"name": "Medical Xpress", "url": "https://medicalxpress.com/news/2026-vitamin-d-diabetes-genes.html"},
        {"name": "American Journal of Clinical Nutrition", "url": "https://ajcn.nutrition.org/"}
    ]),
    "body": """Vitamin D supplements are among the most widely taken pills in the world, and for years the evidence on whether they actually prevent type 2 diabetes has been frustratingly muddy. Some large trials showed a modest benefit; others showed essentially none. A new analysis from Tufts University offers a compelling explanation for the contradiction, and it points to an answer hiding in our DNA: vitamin D may work, but only for people whose genes let it.

The findings, drawn from one of the largest diabetes-prevention trials ever run, matter unusually for the South Asian diaspora — a population caught in the crossfire of two epidemics at once. South Asians have some of the highest rates of vitamin D deficiency in the world, driven by darker skin, limited sun exposure, and dietary patterns. They also carry exceptionally high rates of type 2 diabetes. A study that clarifies when vitamin D helps blood sugar speaks directly to that double burden.

## The Gene That Decides

The Tufts team, led by senior author Dr. Anastassios Pittas, analysed genetic data from 2,098 participants who had taken part in a major vitamin D diabetes-prevention trial and consented to DNA testing. They focused on a specific gene: the vitamin D receptor, the protein that allows the body's cells to actually respond to the vitamin circulating in the blood.

The logic is elegant. Vitamin D does not do its work directly; it must bind to this receptor to have any effect. The insulin-producing cells of the pancreas carry these receptors, which is how the vitamin is thought to influence blood sugar control. So the researchers asked: do common variations in the receptor gene change whether supplementation works?

The answer was striking. Among adults carrying what is called the AA variation of the ApaI receptor gene — roughly 30 per cent of the study population — high-dose vitamin D made no difference at all to diabetes risk compared with a placebo. But among those with the AC or CC variations of the same gene, the identical treatment significantly reduced the risk of developing type 2 diabetes.

In other words, the same pill produced two completely different outcomes depending on a single inherited genetic trait. The "vitamin D doesn't prevent diabetes" trials and the "vitamin D does prevent diabetes" trials may both have been right — they were simply measuring different mixes of genetic responders and non-responders.

## A Step Toward Personalised Prevention

"The findings may represent an important step toward developing a personalised approach to lowering the risk of developing type 2 diabetes among high-risk adults," Pittas said. The appeal, he noted, is partly practical: "Part of what makes vitamin D appealing as a potential preventive tool is that it is inexpensive, widely available, and easy for people to take."

That is the genuinely exciting part. Most precision-medicine breakthroughs involve expensive drugs or complex therapies. Here, the intervention is a cheap, over-the-counter vitamin — and the only thing standing between guesswork and a targeted strategy is a simple genetic test that could one day tell a person whether supplementation is likely to help them at all.

## The Crucial Caveat

The researchers were emphatic on one point, and it bears repeating. The study does not mean people should rush to take high doses of vitamin D on their own to prevent diabetes. The doses used in the trial were high and medically supervised, and excessive vitamin D carries its own risks, including dangerously elevated calcium levels.

What the study supports is the future use of genetic information to guide who should consider supplementation and at what dose — not a free-for-all at the supplement aisle. It is a research finding pointing toward a clinical tool, not a prescription.

## What the Diaspora Should Take From It

For South Asian families, three practical threads emerge. First, vitamin D deficiency is genuinely widespread in the community and worth checking through a simple blood test, because deficiency has consequences well beyond diabetes — for bone health, immunity, and mood. Correcting a true deficiency is sound medicine regardless of genetics.

Second, the diabetes-prevention question is more nuanced than "take vitamin D and you're protected." For perhaps a third of people, the evidence now suggests the pancreatic benefit simply will not materialise, and relying on the supplement as a diabetes shield could give false reassurance.

Third, and most encouraging, the foundations of diabetes prevention remain unchanged and within everyone's control regardless of which gene variant they carry: maintaining a healthy weight, staying physically active, limiting refined carbohydrates and sugar, and getting screened early — especially given that South Asians develop diabetes at lower BMIs and younger ages than most populations.

Vitamin D, this study suggests, may eventually become one personalised tool among many. But until a genetic test routinely guides that choice, the diaspora's best defence against diabetes is still the unglamorous, gene-blind basics — done consistently, and started early."""
})

# ============================================================
# ARTICLE 3: NSE mega-IPO (markets-finance)
# ============================================================
articles.append({
    "headline": "India's Largest Stock Exchange Is About to Go Public. The NSE's Mega-IPO Could Be the Country's Biggest Ever.",
    "subheadline": "The National Stock Exchange is set to file its draft prospectus with SEBI this week for an offering structured entirely as a sale of existing shares, with its unlisted stock already valued above ₹5 lakh crore in the grey market. For NRIs who have long held NSE shares privately — and for those who want in — this is the moment a decade in the making.",
    "slug": "nse-ipo-drhp-sebi-filing-largest-india-offering-for-sale-nri-investor-guide-20260615",
    "category": "markets-finance",
    "vertical": "markets",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Many NRIs and OCIs have held National Stock Exchange shares for years in the unlisted market, and a public listing finally offers a transparent exit and price discovery — while the broader opening of India's markets to foreign individuals makes the IPO a live opportunity for the diaspora rather than a spectator event.",
    "sources": json.dumps([
        {"name": "Outlook Money", "url": "https://www.outlookmoney.com/invest/nse-ipo-drhp-filing"},
        {"name": "Press Trust of India", "url": "https://www.ptinews.com/"},
        {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/"}
    ]),
    "body": """After years of false starts, regulatory tangles, and investor impatience, the biggest listing in Indian market history may finally be moving. The National Stock Exchange — the platform on which the vast majority of India's equity trades are executed — is expected to file its Draft Red Herring Prospectus with the Securities and Exchange Board of India this week, according to people familiar with the matter cited by the Press Trust of India. The draft papers are likely to land with the regulator on June 15 or 16.

It would mark the formal start of an IPO that market participants have anticipated for the better part of a decade, and one that by sheer scale could dwarf anything India has seen before.

## The Numbers Behind the Hype

The headline figure is staggering. In the grey market, where shares of unlisted companies trade privately ahead of a listing, the NSE is already valued at more than ₹5 lakh crore — over $58 billion. That would place it among the most valuable companies in the country and make its public debut potentially the largest IPO in Indian history.

The structure is important and worth understanding. According to the reports, the offering is expected to be entirely an Offer for Sale, or OFS. That means existing shareholders — and the NSE has many, from financial institutions to long-time private investors — will sell their stakes to the public, while the exchange itself will not raise any fresh capital. For a company that is already highly profitable and cash-rich, that makes sense: it does not need the money. The IPO is about giving existing holders an exit and establishing a transparent public price, not about funding expansion.

## Why It Took So Long

The NSE's road to a listing has been anything but smooth. Plans to go public have been floated and shelved repeatedly over the years, derailed at various points by a long-running regulatory investigation into a co-location trading scandal and by the practical complexity of taking a stock exchange — itself the venue where IPOs happen — public. Resolving the outstanding regulatory matters with SEBI was the precondition everyone was waiting on, and the imminent DRHP filing signals that the path is now substantially clear.

That backstory matters for investors, because it explains both the pent-up demand and the caution. The shares have traded actively in the unlisted market precisely because a listing was always assumed to be coming eventually; now that it appears to be arriving, the question shifts from "if" to "at what price."

## The Diaspora Connection

For non-resident Indians, the NSE IPO is unusually relevant, and for a specific reason: a meaningful number of NRIs and OCIs already own NSE shares. The exchange's stock has been one of the most sought-after names in India's unlisted market for years, and diaspora investors with access to it have accumulated positions through private deals, often years ago and at far lower valuations.

For those holders, a public listing is the long-awaited payoff. It transforms an illiquid private holding — difficult to value, harder to sell — into a transparent, exchange-traded asset with a real market price and a clean exit. Anyone sitting on unlisted NSE shares will want to read the eventual prospectus closely for the offer price, lock-in terms, and how the OFS treats existing shareholders.

For NRIs who do not yet own a piece but want in, the timing dovetails with a broader shift. India has been steadily widening foreign access to its markets, including recent moves to allow a far broader set of foreign individuals to invest directly in Indian equities, alongside the RBI's push to draw diaspora capital through higher-yielding deposit schemes. The NSE listing arrives into a market that is, deliberately, becoming easier for the diaspora to participate in.

## What to Watch Next

A DRHP filing is the opening move, not the finish line. After the draft is submitted, SEBI reviews it, the company addresses any observations, and only then is a price band set and a subscription window opened — a process that typically takes months. The grey-market valuation, however enticing, is not the offer price, and history is full of hotly anticipated IPOs that listed below the froth of pre-listing speculation.

There are also broader currents to weigh. Foreign portfolio investors have been net sellers of Indian equities this year, and the benchmark indices have had a bruising run, though the recent oil-price crash and rupee recovery have brightened sentiment. A mega-IPO of this size will test the market's appetite to absorb a very large block of new tradable stock.

Still, the symbolism is hard to overstate. The exchange that hosts India's capital markets is preparing to become a public company traded on those very markets. For the diaspora — whether holding shares already or simply watching India's financial system mature — it is a milestone worth following closely as the prospectus, and the price, come into view."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
print(f"\n{'='*60}\nSourcing images\n{'='*60}")
img_specs = {
    articles[0]["slug"]: (["DNA sequencing laboratory", "genome research laboratory"],
                          ["DNA genetic research laboratory", "scientist laboratory DNA test"]),
    articles[1]["slug"]: (["vitamin D supplement", "dietary supplement capsules"],
                          ["vitamin d supplement capsules", "vitamin supplements pills sunlight"]),
    articles[2]["slug"]: (["National Stock Exchange of India building", "Bombay Stock Exchange building Mumbai"],
                          ["stock exchange trading floor", "stock market financial district India"]),
}
img_captions = {
    articles[0]["slug"]: "DNA sequencing in a genomics laboratory, the technology behind the OurHealth biobank",
    articles[1]["slug"]: "Vitamin D supplement capsules, whose diabetes-prevention benefit may depend on a person's genes",
    articles[2]["slug"]: "A stock exchange trading environment, as India's NSE prepares its landmark public listing",
}
for art in articles:
    cq, pq = img_specs[art["slug"]]
    url, attribution = source_image(art["slug"], cq, pq)
    if url:
        art["image_url"] = url
        art["image_caption"] = img_captions[art["slug"]]
        art["image_attribution"] = attribution
    else:
        # No image > wrong image. Leave fields unset.
        print(f"  ⚠ {art['slug']} will publish without hero image")

# ============================================================
# INSERT
# ============================================================
print(f"\n{'='*60}\nInserting {len(articles)} articles at {now}\n{'='*60}\n")
success = 0
for a in articles:
    wc = len(a['body'].split())
    has_img = "img✓" if a.get("image_url") else "NO-IMG"
    print(f"  [{a['category']}] {a['slug']} — {wc} words — {has_img}")
    if insert_article(a):
        success += 1
print(f"\n{'='*60}\nDone: {success}/{len(articles)} articles inserted\n{'='*60}")
