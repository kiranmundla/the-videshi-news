#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-17 14:00 UTC batch.
Topics:
  1. GLP-1 weight-loss drugs quietly cut physical activity (ENDO 2026) — lifestyle-health
  2. US POINTER trial: structured lifestyle plan slows brain ageing — lifestyle-health
  3. India's IT index, gutted 27% by AI fears, becomes the contrarian trade — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl2200.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl2200.bin"):
            with open("/tmp/_img_dl2200.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl2200.bin")
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
# ARTICLE 1: Akkermansia muciniphila weight-loss maintenance (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Single Gut Microbe Helped People Keep the Weight Off. A New Trial Puts a Number on It.",
    "subheadline": "In a randomized trial published in Nature Medicine, adults who took a daily dose of a pasteurized gut bacterium after dieting regained far less weight than those on a placebo \u2014 2.6 pounds versus 7.1 \u2014 over six months. It is the clearest human evidence yet that the bug in your gut may decide whether the kilos stay off.",
    "slug": "akkermansia-muciniphila-mucT-weight-loss-maintenance-nature-medicine-maastricht-diaspora-20260617",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians are uniquely prone to regaining weight as dangerous visceral fat after dieting, and to the early diabetes that follows \u2014 a microbiome-based tool that helps the weight stay off could matter more for the diaspora than for almost any other group.",
    "sources": json.dumps([
        {"name": "Nature Medicine \u2014 Mount et al., Pasteurized Akkermansia muciniphila MucT for weight loss maintenance in people with overweight and obesity: a controlled randomized trial", "url": "https://www.nature.com/articles/s41591-026-04394-7"},
        {"name": "Nature Reviews Microbiology \u2014 Keeping off the weight with Akkermansia", "url": "https://www.nature.com/articles/s41579-026-01200-x"},
        {"name": "Fox News Health \u2014 Secret to weight loss may be hiding in your gut, new study suggests", "url": "https://www.foxnews.com/health"}
    ]),
    "body": """Anyone who has lost weight knows the cruelest part comes after. The diet works, the scale moves \u2014 and then, slowly, the pounds creep back. A new clinical trial suggests that one reason may be living inside the gut, and that a single bacterium could help tip the odds in the dieter's favour.

## What the Researchers Tested

The study, published in the journal Nature Medicine, was run by a team led by researchers at Maastricht University in the Netherlands. It enrolled 90 adults who were overweight or obese and put them through two phases.

First came the weight-loss phase: eight weeks on a low-energy diet, with participants asked to shed about 8 percent of their body weight. Then came the hard part \u2014 a 24-week maintenance phase on an unrestricted, healthy diet. During those six months, participants were randomly assigned to take either a daily supplement of pasteurized Akkermansia muciniphila MucT, a bacterium that naturally lines the healthy human gut, or a placebo.

Neither group was told to follow a strict diet during maintenance. They simply ate as they normally would, which is exactly the real-world test that most weight studies avoid.

## The Number That Matters

The result was clear. People taking the Akkermansia supplement regained an average of 2.6 pounds, while those on placebo regained 7.1 pounds \u2014 a statistically significant difference. Put another way, the bacterium roughly cut weight regain by more than half over six months.

Participants on the supplement also showed greater net weight loss from the very start of the study to the end of the maintenance period, meaning they held on to more of what they had worked to lose. No serious treatment-related side effects were reported.

The researchers pointed to several possible mechanisms: people taking the microbe appeared to lose more energy through their stool, showed reduced inflammation, and had more metabolically active subcutaneous fat tissue. In other words, the bug seems to nudge the body's whole energy economy in a favourable direction.

## A Twist: Who Benefits Most

One of the most intriguing findings was that the benefit was not uniform. Participants who started the trial with low levels of Akkermansia already in their own gut showed the greatest cardiometabolic gains from the supplement. The effect, the team noted, depends on a person's existing microbiome \u2014 a sign that future treatments may need to be matched to the gut a person already has.

It is also worth noting what the supplement is not. This is a pasteurized \u2014 that is, heat-killed \u2014 bacterium, not a live probiotic. Experts believe it works through components of the dead bacterium, particularly a protein called Amuc_1100, rather than by colonising the gut. That makes it more stable and predictable than a typical live probiotic.

## The Caveats

The trial was small \u2014 90 people \u2014 and relatively short, at six months of maintenance. The researchers themselves caution that the duration and sample size are not enough to prove long-term benefits, and that larger, longer trials are needed before anyone calls this a treatment. Several of the study's authors are affiliated with the company developing the supplement, which is a flag worth noting even though the trial was randomized and placebo-controlled. And it is not a substitute for diet and exercise; it was tested as an add-on to a healthy lifestyle, not a replacement for one.

## Why It Lands for the Diaspora

For Indian and wider South Asian communities, weight regain is not a vanity problem \u2014 it is a metabolic landmine. South Asians tend to store regained weight as visceral fat, the deep abdominal fat wrapped around the organs that drives insulin resistance, type 2 diabetes and early heart disease. The community develops these conditions at lower body weights and younger ages than most populations, which means the yo-yo cycle of losing and regaining weight is especially costly.

The gut microbiome angle is also culturally resonant. Traditional South Asian diets, rich in fibre, fermented foods like dahi and idli batter, and plant diversity, have long been understood to feed a healthy gut. This research adds a precise, mechanistic layer to that intuition: the specific microbes a person carries may help determine whether a hard-won weight loss survives the festival seasons, the wedding feasts and the everyday temptations.

## What To Actually Do

This is early science, and no one should rush to buy supplements off the back of a single 90-person trial. The practical takeaway is upstream of any pill. Eat in a way that feeds a diverse gut \u2014 more fibre, more plants, fermented foods, fewer ultra-processed items \u2014 because a healthier baseline microbiome is exactly what the study suggests amplifies benefits. Treat weight maintenance, not just weight loss, as the real goal, and expect it to require ongoing effort. And watch this space: if larger trials confirm the result, microbiome-matched support for keeping weight off could become a genuine tool, particularly for a community where the stakes are so high.
"""
})

# ============================================================
# ARTICLE 2: Cohabitation shapes the microbiome (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The People You Live With Are Quietly Rewiring Your Gut. A New Study Maps How Microbes Spread Under One Roof.",
    "subheadline": "Researchers found that people who share a home share a quarter of their oral microbes \u2014 and romantic partners share far more \u2014 regardless of whether they eat the same food. The finding reframes health as something families pass between one another, microbe by microbe.",
    "slug": "cohabitation-shared-microbiome-family-household-trento-study-diaspora-multigenerational-20260617",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Multigenerational living \u2014 grandparents, parents and children under one roof \u2014 is a hallmark of diaspora households, which means the microbes, and the health risks and benefits they carry, are shared more intensely in Indian families than in the nuclear homes this kind of research usually studies.",
    "sources": json.dumps([
        {"name": "The New York Post \u2014 Who you live with has a major impact on your gut health \u2014 even if you have different diets", "url": "https://nypost.com/"},
        {"name": "University of Trento / Vitor Heidrich et al. \u2014 microbiome sharing among cohabiting individuals", "url": "https://www.unitn.it/en"}
    ]),
    "body": """We tend to think of our microbiome \u2014 the trillions of bacteria and other microbes that live in and on us \u2014 as deeply personal, as individual as a fingerprint. New research suggests it is closer to a shared inheritance, passed quietly between the people who live under the same roof.

## What the Researchers Found

A team including researchers at the University of Trento in Italy examined the microbes carried by people who live together, and the numbers were striking. People sharing a household shared about 26 percent of the same oral microbes \u2014 and the relationship type barely mattered. Siblings, parents and children all showed the same broad pattern of overlap.

Romantic partners shared even more: roughly 44 percent of their oral microbes, a figure the researchers attributed in large part to kissing. But the headline finding was that intimacy of that kind was not required. Simply sharing space \u2014 the same kitchen, the same bathroom, the same air \u2014 was enough to make housemates microbially alike.

"Your microbiome is not just yours as an isolated entity," lead author Vitor Heidrich told The New York Post. "It is partly a reflection of the people you live with, and theirs is partly a reflection of you."

## Why It Is Not Just About Food

The most counterintuitive part of the study was what did not explain the sharing. You might assume that families who eat the same meals develop the same gut and mouth microbes through their diet. The research found that diet, on its own, was less significant than the simple fact of living together.

"Unless my strains physically travel from me to you, the same diet alone will not necessarily make us share more of our strains," Heidrich explained. The key, he said, is transmission followed by a hospitable environment: "It's more that if I pass one of my strains to you and we eat the same diet, that strain will find a similar nutritional environment in your gut to the one it was thriving in before, making it more likely to successfully colonize your gut."

In other words, the food does not create the shared microbe \u2014 it helps a shared microbe, once passed along, take hold.

## Why Microbial Diversity Matters

The microbiome is a sprawling community of bacteria and other organisms, both helpful and harmful, too small to see. As a general rule, the more diverse this community, the more resilient it is to disturbance and the better it tends to be for health. A diverse gut is linked to better digestion, stronger immunity and lower inflammation; a depleted one is associated with a range of metabolic and immune problems.

That makes the sharing cut both ways. Living closely with others can broaden a person's microbial diversity \u2014 a potential benefit. But it also means that the microbes linked to certain conditions may be transferable too. As Heidrich put it, "the health benefits and disease risks linked to specific microbiome members may themselves be transferable between people, which is something we are only beginning to understand."

## The Caveats

This is an emerging field, and the study describes associations and sharing patterns rather than firm health outcomes. The researchers are clear that the science of which transferable microbes help and which harm is still in its infancy. Sharing 26 percent of oral microbes does not mean sharing 26 percent of any given disease risk. The work is best read as a map of how microbes move between people, not yet a prescription for what to do about it.

## Why It Lands for the Diaspora

For the Indian diaspora, this research has an unusually direct resonance, because the multigenerational household is so common. In countless Indian-American, British-Indian and Canadian-Indian homes, grandparents, parents and children share not just meals but kitchens, utensils, and the everyday closeness of joint family life. If microbes travel by cohabitation, they travel especially freely in these homes.

There is a hopeful reading and a cautious one. The hopeful one: elders steeped in traditional, fibre-rich, fermented-food diets may carry beneficial microbes that get shared with younger, more Westernised family members \u2014 a quiet transmission of gut health across generations. The cautious one: the metabolic risks that run in South Asian families may have a microbial dimension that close living amplifies. Either way, the study suggests family health is, in a literal biological sense, collective.

## What To Actually Do

There is no need to disinfect the family home \u2014 shared microbes are largely a normal, even beneficial, feature of close living. The practical lessons are gentler. Feed the household's microbiome as a unit: cook with plenty of fibre, vegetables, and traditional fermented foods like dahi, kanji and idli, so that the strains being shared are good ones landing in fertile ground. Maintain basic hygiene around illness, since the same closeness that shares helpful microbes can share pathogens too. And think of health choices as family choices \u2014 because, microbe by microbe, that is increasingly what the science says they are.
"""
})

# ============================================================
# ARTICLE 3: Fed holds, Warsh turns hawkish, dot plot flips to a hike (markets-finance)
# ============================================================
articles.append({
    "headline": "The Fed Just Stopped Promising Rate Cuts \u2014 and Started Hinting at a Hike. Warsh's First Meeting Spooked Wall Street.",
    "subheadline": "In Kevin Warsh's debut as Federal Reserve Chair, the central bank held rates at 3.50\u20133.75% but flipped its dot plot from an implied cut to an implied hike, sending US stocks sliding and the dollar firmer. For NRIs, a hawkish Fed reshapes everything from the rupee to mortgage rates to the calculus on sending money home.",
    "slug": "fed-holds-rates-warsh-first-meeting-dot-plot-hike-june-2026-nri-investor-rupee-dollar-20260617",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "A hawkish US Fed keeps the dollar strong and US mortgage and savings rates elevated \u2014 directly shaping how much NRIs earn on dollar deposits, what they pay on American home loans, and how many rupees their remittances buy back home.",
    "sources": json.dumps([
        {"name": "USA Today \u2014 Fed's Warsh era starts with rates unchanged, price stability promised", "url": "https://www.usatoday.com/money/"},
        {"name": "StockTitan \u2014 Fed Holds Rates June 2026; Dot Plot Flips to a Hike", "url": "https://www.stocktitan.net/"},
        {"name": "Detroit Free Press \u2014 Fed keeps rates unchanged as inflation remains elevated", "url": "https://www.freep.com/"}
    ]),
    "body": """The Federal Reserve did what almost everyone expected on Wednesday \u2014 it held interest rates steady. What it signalled about the future was the shock. In Kevin Warsh's first meeting as Fed Chair, the central bank abandoned its lingering bias toward cutting rates and tilted, for the first time in this cycle, toward raising them.

## What the Fed Decided

The Federal Open Market Committee voted unanimously, 12 to 0, to keep the federal funds target range at 3.50 to 3.75 percent \u2014 where it has sat since December 2025. It was the fourth consecutive hold of 2026, after meetings in January, March and April. No analyst had expected a move at this meeting.

The statement explaining the decision was unusually terse \u2014 roughly half the length of the previous one, a stylistic signal from the new chair. It cited a labour market where "job gains have kept pace with the workforce" and inflation that "remains elevated" relative to the Fed's 2 percent goal, driven in part by energy and supply shocks tied to the recent conflict in the Middle East.

## The Real News: The Dot Plot Flipped

The genuine surprise was buried in the Summary of Economic Projections \u2014 the "dot plot" that maps where each policymaker expects rates to go. The median projection for the end of 2026 rose to 3.8 percent, up from 3.4 percent in March. That shift is subtle on paper but seismic in meaning: it moved the Fed's own median forecast from implying a rate cut to implying a rate hike before year-end. The projections for 2027 and 2028 also moved higher.

In plain terms, the central bank that spent early 2026 debating when to ease is now, collectively, leaning toward tightening. "One thing is certain and that is the Federal Reserve will definitely not cut interest rates this year. Bet on it. The markets are," said Chris Rupkey, chief economist at FWDBONDS, in a note.

## A New Chair With a Hawkish Record

The shift carries Warsh's fingerprints. Sworn in on 22 May after a 54-45 Senate confirmation, the new chair brings a famously hawkish history \u2014 during his earlier Fed tenure from 2006 to 2011, he repeatedly favoured higher rates to suppress inflation, even as unemployment surged in the financial crisis. At his swearing-in he pledged a "reform-oriented Federal Reserve" focused on discipline, and has spoken of wanting "messier meetings" with more open debate.

His debut press conference struck a hawkish tone, and markets recoiled. The Nasdaq fell more than 350 points, or 1.3 percent; the S&P 500 slid 1.2 percent; the Dow gave back about 507 points. The VIX volatility index jumped 13 percent, and the 10-year Treasury yield sold off to about 4.50 percent. President Trump, who spent months attacking former Chair Jerome Powell to cut rates, was uncharacteristically muted, telling reporters in Paris, "It's all right. Whatever," and adding of a possible hike, "It could happen."

## Why It Matters Beyond Wall Street

A hawkish Fed ripples far beyond the stock ticker. It tends to keep the US dollar strong, since higher-for-longer rates draw global capital into dollar assets. It keeps borrowing costs elevated \u2014 the 30-year mortgage sits around 6.53 percent, and the Fed's signal suggests little relief ahead. And it keeps yields on dollar savings attractive, even as it squeezes the equity and bond markets that retirement portfolios depend on.

## What It Means for the Diaspora

For NRIs, a hawkish US Fed is a multi-front event. Start with the dollar: a stronger greenback against the rupee means remittances sent home stretch further, the inverse of what a falling oil price has lately been doing to the rupee. The two forces \u2014 cheaper oil firming the rupee, a hawkish Fed firming the dollar \u2014 are now pulling in opposite directions, and the net effect will set the exchange rate that governs every transfer.

On savings, the Fed's hold-or-hike stance keeps US dollar yields high, which is good news for NRIs parking money in American instruments and a key backdrop to the recent wave of high-rate FCNR dollar deposits Indian banks have rolled out to court diaspora cash. On borrowing, anyone in the diaspora carrying an American mortgage, car loan or credit-card balance should brace for elevated costs to persist through 2026 rather than ease.

And for those invested across both markets, the divergence is the story. US equities just took a hit on the hawkish turn, while Indian benchmarks have been rallying on falling oil. A diaspora investor with money on both sides of the ocean is, in effect, holding two economies moving to different drums \u2014 a reminder that diversification across geographies is doing real work right now.

## The Bottom Line

The Fed held, but the message was hawkish, and a new chair with a hard-money record now sets the tone. For NRIs, the practical posture is to watch the dollar-rupee cross closely \u2014 it is being pushed and pulled at once \u2014 to lock in elevated dollar deposit rates while they last, and to expect US borrowing costs to stay high. The era of waiting for the Fed to cut is, for now, over.
"""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["gut bacteria microbiome illustration", "probiotic supplement capsule", "human gut microbiota"],
                          ["gut health probiotics", "healthy food weight loss"], None),
    articles[1]["slug"]: (["Indian family eating meal together", "family dinner home", "multigenerational family kitchen"],
                          ["family eating together", "indian family dinner"], None),
    articles[2]["slug"]: (["Federal Reserve building Washington", "Marriner Eccles Federal Reserve", "Federal Reserve headquarters"],
                          ["federal reserve building", "us dollar money"], None),
}
img_captions = {
    articles[0]["slug"]: "An illustration of gut microbiota; a Nature Medicine trial found a pasteurized gut bacterium cut weight regain by more than half",
    articles[1]["slug"]: "A family sharing a meal; new research finds people who live together share about a quarter of their oral microbes",
    articles[2]["slug"]: "The Federal Reserve in Washington; the Fed held rates but flipped its projections toward a hike at Kevin Warsh's first meeting",
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
