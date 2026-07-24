#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-25 19:00 PT batch.
Topics (checked against recent articles to avoid dupes):
  1. Vitamin D deficiency hidden year-round (Newcastle Univ / European Journal of
     Clinical Nutrition) — even in summer sun, 54.8% of older adults and 72.1% of
     ethnic-minority participants with darker skin were low; ties to the TARGET-D
     trial showing personalized dosing halved heart-attack risk. STRONG diaspora
     angle (darker skin pigmentation). — lifestyle-health (Distinct: micronutrient
     / supplement story, not the diet-pattern or exercise pieces already covered.)
  2. Anti-inflammatory diet uniquely protects the genetically predisposed
     (NY Post coverage of a Health & Retirement Study analysis of AMED, AHEI and
     rEDII diets) — among people at HIGH genetic risk for Alzheimer's, only the
     anti-inflammatory (rEDII) pattern significantly cut risk. — lifestyle-health
     (Distinct: genetic-risk personalization + anti-inflammatory mechanism, not the
     plant-based-Mediterranean-CVD epi or exercise-dementia pieces.)
  3. India-US trade deal "very close" — Goyal says framework finalised but won't
     take effect until India locks a tariff edge over Vietnam/Bangladesh etc.;
     July 24 deadline; 18% interim tariff; Section 301 probe. — markets-finance
     (Distinct: trade/geopolitics-markets, none of the recent RBI/IPO/gold/bond/
     pharma/FDI pieces touched the BTA itself.)
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl1900z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl1900z.bin"):
            with open("/tmp/_img_dl1900z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl1900z.bin")
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
# ARTICLE 1: Hidden vitamin D deficiency (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The 'Sunshine Vitamin' Many Are Missing \u2014 Even in Summer, and Most of All Those With Darker Skin",
    "subheadline": "New research finds large numbers of people run low on vitamin D year-round without knowing it \u2014 nearly three in four with darker skin pigmentation in one study \u2014 just as a separate trial suggests that getting levels right can sharply cut heart-attack risk.",
    "slug": "vitamin-d-deficiency-hidden-year-round-darker-skin-newcastle-ejcn-target-d-heart-attack-diaspora-20260625-1900",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Vitamin D is made in the skin from sunlight, and darker skin makes far less of it \u2014 so Indian-origin families living in the cloudier, higher-latitude cities of the US, UK and Canada are among the most likely in the world to be quietly deficient, a risk that compounds the community's existing vulnerability to diabetes and heart disease.",
    "sources": json.dumps([
        {"name": "The Sun \u2014 'Are you tired all the time or suffering back pain? You could be among the 1 in 5 deficient in summer vitamin' (Newcastle University study, European Journal of Clinical Nutrition)", "url": "https://www.thesun.co.uk/health/39540152/tired-back-pain-deficient-summer-vitamin-d/"},
        {"name": "American Heart Association \u2014 'Heart attack risk halved in adults with heart disease taking tailored vitamin D doses' (TARGET-D trial, Intermountain Health)", "url": "https://newsroom.heart.org/news/heart-attack-risk-halved-in-adults-with-heart-disease-taking-tailored-vitamin-d-doses"}
    ]),
    "body": """It is called the sunshine vitamin, and the assumption that follows is comforting: spend enough time outdoors and the body will make all the vitamin D it needs. New research complicates that picture \u2014 and the people it complicates it for most are precisely those of the diaspora.

## Low Even in the Sun

Researchers at Newcastle University's Human Nutrition and Exercise Research Centre measured vitamin D levels in nearly 300 people living across northern England and, writing in the *European Journal of Clinical Nutrition*, reported that a significant number were running low without any idea they were. The striking part was the timing. Vitamin D is produced in the skin during sun exposure, which is why public-health advice has long focused on topping up only through the darker winter months. Yet the study found that for many people, summer sunshine was not enough to lift levels into a healthy range.

The team focused on two groups thought to be at higher risk: adults aged 65 and over, and people from ethnic-minority backgrounds with, in the study's words, darker skin pigmentation. The results were sobering. More than half of the older adults \u2014 54.8 percent \u2014 had insufficient vitamin D. Among the ethnic-minority participants, the figure was higher still: 72.1 percent, very nearly three in four, were short of the nutrient.

## Why Skin Colour Matters

The reason is basic skin biology. Melanin, the pigment that gives skin its colour, is a natural sunscreen. It protects against sun damage, but it also slows the very reaction that turns sunlight into vitamin D. People with darker skin therefore need considerably more sun exposure to make the same amount, and at the cloudier, higher latitudes of Britain, northern Europe, Canada and the northern United States, that exposure is often simply unavailable for much of the year.

Low vitamin D is not a trivial matter. It is essential for bone development and for the immune system, and deficiency has long been linked to osteoporosis and, in children, rickets. Less obviously, the study's authors note that low levels can show up as everyday symptoms many people would never connect to a nutrient gap: persistent tiredness, back pain, low mood and hair loss. Deficiency has also been associated with a higher risk of heart disease and diabetes.

## The Other Half of the Story

Whether topping up vitamin D actually prevents disease has been one of nutrition's longest-running arguments, and large trials handing everyone the same standard dose have mostly come up empty. A more recent trial suggests the question may have been framed wrongly. In the TARGET-D study, run by Intermountain Health in Utah, researchers did not give a one-size-fits-all dose. They measured each participant's blood level and adjusted the dose over time to push it above a target of 40 nanograms per millilitre \u2014 a level most participants were well below at the start.

The results were notable. Adults with existing heart disease who were dosed to reach and hold that target had a 52 percent lower risk of heart attack over nearly four years than those whose levels were left unmanaged. The lesson, researchers stressed, was about precision: testing first, dosing to a goal, and monitoring to avoid the real dangers of taking too much, which can raise blood calcium to harmful levels. This is an encouraging signal rather than settled proof, and the experts are clear that supplements are no substitute for managing the rest of one's heart health.

## Why It Matters for the Diaspora

For Indian-origin families abroad, this research lands with unusual force, because it describes them almost exactly. The diaspora is concentrated in the cloudy, high-latitude cities where the sun does the least work, and darker skin makes that work harder still. The result is that South Asians in the West sit among the populations most prone to quiet, year-round vitamin D deficiency \u2014 on top of an already elevated burden of diabetes and heart disease, the very conditions low vitamin D is linked to.

The practical takeaways are refreshingly cheap and concrete. A simple blood test, often available through a routine GP or physician visit, can reveal a deficiency that sunshine and diet alone may not fix. For many in the community, a modest daily supplement through the darker months \u2014 and, this research hints, perhaps year-round \u2014 may be sensible, ideally guided by an actual measured level rather than guesswork. It is a small, low-cost adjustment with a potentially outsized payoff for a group that the geography and biology of migration have left especially exposed."""
})

# ============================================================
# ARTICLE 2: Anti-inflammatory diet & genetic risk (lifestyle-health)
# ============================================================
articles.append({
    "headline": "For Those With Alzheimer's in the Family, One Eating Pattern Stood Out, a New Analysis Finds",
    "subheadline": "Among people genetically predisposed to Alzheimer's, researchers found that an anti-inflammatory diet \u2014 not a Mediterranean or a generally 'healthy' one \u2014 was the only pattern tied to a meaningfully lower risk, pointing to inflammation as a lever the high-risk can pull.",
    "slug": "anti-inflammatory-diet-genetic-alzheimers-risk-redii-amed-ahei-inflammation-foods-diaspora-20260625-1900",
    "category": "lifestyle-health",
    "vertical": "wellness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Alzheimer's and dementia run in many Indian families, and the community already carries a high genetic and metabolic risk \u2014 so a finding that the predisposed may benefit most from a specifically anti-inflammatory diet, one that maps neatly onto traditional Indian staples like lentils, leafy greens, turmeric and vegetables, offers an actionable lever rather than a fatalistic shrug.",
    "sources": json.dumps([
        {"name": "New York Post \u2014 'Which diet \u2014 and exact foods \u2014 are great for preventing dementia: study'", "url": "https://nypost.com/2026/06/25/health/which-diet-and-exact-foods-are-great-for-preventing-dementia-study/"},
        {"name": "Wahala, A.J., et al. \u2014 'Adherence to an anti-inflammatory diet is associated with lower Alzheimer's disease mortality: A modifiable risk factor in a national cohort' (PubMed)", "url": "https://pubmed.ncbi.nlm.nih.gov/40517083/"}
    ]),
    "body": """Most dietary advice for protecting the aging brain converges on the same comfortable answer: eat more like the Mediterranean. Fresh produce, whole grains, olive oil, fish. A new analysis does not overturn that, but it adds a sharper, more useful wrinkle \u2014 especially for the people who worry about dementia most, those with it already written into their family tree.

## Three Diets, One Standout

Researchers set out to compare how three distinct eating patterns related to the risk of developing dementia. The first was the Alternate Mediterranean Diet, or AMED, the familiar produce-and-olive-oil template. The second was the Alternative Healthy Eating Index, or AHEI, a broad measure of overall diet quality. The third was the reversed Empirical Dietary Inflammatory Index, or rEDII \u2014 a scoring system built specifically around whether the foods a person eats tend to stoke inflammation in the body or quiet it. People scoring high on the rEDII were, in effect, eating an anti-inflammatory diet.

For the general population, the healthy patterns broadly helped, in line with years of prior research. But the most interesting result emerged when the researchers looked specifically at participants who were at higher risk of Alzheimer's. In that group, only one of the three patterns showed a significant reduction in risk: the anti-inflammatory rEDII diet. A generally healthy plate, on its own, was not enough. Targeting inflammation appeared to be the thing that moved the needle for the predisposed.

## Inflammation as the Lever

The finding fits a growing scientific consensus about what actually drives Alzheimer's at the cellular level. Inflammation is increasingly seen as a hallmark of the disease, and oxidative stress \u2014 much of it arising from chronic, low-grade inflammation \u2014 is thought to speed aging and fuel a cluster of chronic illnesses including Alzheimer's, cancer and diabetes.

"An anti-inflammatory diet is great for the prevention and slowing the progression of Alzheimer's disease," Emily Case, a registered dietitian at Northwell Health, told *The New York Post*, while cautioning that such diets can prevent and delay cognitive decline but not reverse it. She offered a vivid image: inflammation is a bit like a bodily bonfire, and what a person eats can either stoke it or dampen it.

The foods that dampen it are not exotic. Case pointed to antioxidant-rich berries and dark leafy greens; omega-3 sources such as salmon and walnuts; fibre from whole grains, legumes, fruits, vegetables, nuts and seeds; and healthy fats from avocados, olive oil and nuts. "Anything that improves our heart health," she noted, "will also reduce inflammation in our body" \u2014 a reminder that the brain and the cardiovascular system rise and fall together.

A few caveats deserve emphasis. This kind of research shows association rather than proof, the anti-inflammatory benefit was clearest in those already at elevated risk, and no diet is a guarantee against a disease shaped heavily by genetics and age. The message is one of meaningfully shifting the odds, not eliminating them.

## Why It Matters for the Diaspora

For Indian-origin families, the practical resonance is hard to miss. Dementia and Alzheimer's thread through many family histories, and the community carries both a documented genetic vulnerability and a high background rate of the metabolic conditions \u2014 diabetes, heart disease \u2014 that share inflammation as a common root. That places a great many diaspora households squarely in the higher-risk group for whom this research suggests diet matters most.

The encouraging part is how naturally an anti-inflammatory pattern maps onto traditional Indian cooking, when it is done well. Lentils and beans, dark leafy greens like spinach and methi, a spectrum of vegetables, and spices such as turmeric \u2014 long studied for its anti-inflammatory compound curcumin \u2014 sit at the heart of the anti-inflammatory plate. The threats are the modern additions: ultra-processed snacks, deep-fried foods, refined flour and sugar, which push inflammation the wrong way. For families with Alzheimer's in their past, the finding reframes a daily question \u2014 what to cook for dinner \u2014 as one of the few genuinely controllable levers over a future they tend to fear, and points it back toward the kitchen their grandparents would recognise."""
})

# ============================================================
# ARTICLE 3: India-US trade deal "very close" (markets-finance)
# ============================================================
articles.append({
    "headline": "India and America Say a Trade Deal Is 'Very Close' \u2014 but It Hinges on One Word: Advantage",
    "subheadline": "New Delhi insists it will not let the long-awaited pact take effect unless Washington guarantees India a tariff edge over rivals like Vietnam and Bangladesh, with a July deadline now concentrating minds on both sides.",
    "slug": "india-us-trade-deal-very-close-goyal-tariff-advantage-july-deadline-section-301-nri-investor-20260625-1900",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "A US-India trade pact would reshape the cost of everything from Indian pharmaceuticals and textiles to the cross-border businesses many NRIs run or invest in \u2014 and as the largest single bridge between the two economies the diaspora straddles, its terms touch their portfolios, their companies and the broader India growth story they are betting on.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 'India says very close to trade deal with US'", "url": "https://www.reuters.com/world/india/india-says-very-close-trade-deal-with-us-2026-06-25/"},
        {"name": "Outlook Business \u2014 'India\u2013US Trade Deal Very Close, But Will Not Take Effect Without Tariff Advantage, Says Goyal'", "url": "https://www.outlookbusiness.com/news/indiaus-trade-deal-very-close-but-will-not-take-effect-without-tariff-advantage-says-goyal"},
        {"name": "Devdiscourse \u2014 'India-U.S. Trade Deal Nears Completion Amid Strategic Talks'", "url": "https://www.devdiscourse.com/article/business/3940724-india-us-trade-deal-nears-completion-amid-strategic-talks"}
    ]),
    "body": """For months, the on-again, off-again negotiation between the world's largest and fastest-growing major economies has produced more atmospherics than substance. This week the mood music shifted closer to a finale \u2014 but with a crucial condition attached that explains why the deal still is not done.

## 'The Day That Happens, the Deal Is On'

India and the United States are very close to finalising a trade agreement, India's commerce minister Piyush Goyal said on Thursday, a day after wrapping up talks in New Delhi with the US trade chief, Jamieson Greer. Greer's two-day visit was the latest round in a negotiation that has dragged on for months and has been entangled with broader diplomatic strains between the two countries.

Goyal was unusually blunt about the sticking point. The framework of the deal, he said, has been agreed; what remains is the legal and tariff machinery \u2014 and, above all, a guarantee. New Delhi will not let the agreement come into force unless it secures a clear tariff advantage over competing manufacturing economies such as Vietnam, Thailand, the Philippines, China, Malaysia, Bangladesh and Sri Lanka. "A free-trade agreement is basically about getting a comparative advantage over your competitors for market access," Goyal said. The two sides, he added, are working out how Washington will find "the appropriate tools and legal backing" to deliver that edge. "The day that happens, the deal is on."

## How It Got Stuck

The story did not start here. An initial understanding reached in February set an 18 percent tariff on Indian goods in exchange for New Delhi lowering its own trade barriers and buying more American products. Crucially, that rate was lower than the levies facing rivals like Bangladesh and Vietnam \u2014 exactly the competitive edge India prizes.

Then the ground shifted. The US Supreme Court invalidated President Trump's sweeping global tariffs, knocking away the legal scaffolding the interim understanding had rested on and sending negotiators back to find a new mechanism. Talks were further complicated by a US Trade Representative probe, under Section 301, into alleged overcapacity and forced labour in India and other countries. The result is the present paradox: a deal both sides describe as essentially finished, yet not in effect.

A deadline is now sharpening minds. Goyal has said he would be "happy" to see a deal finalised before July 24, when Washington's temporary 10 percent tariff on trading partners expires, and bluntly added: "The faster, the better." A US deputy assistant secretary, Bethany Poulos Morrison, called the two sides "very, very close," framing the pact as opening India's market of 1.4 billion people to American goods on reciprocal terms and part of a broader "Mission 500" goal of $500 billion in two-way trade by 2030.

## The Market Reading

Investors have been treating progress on the deal as a tailwind. Easing Middle East tensions, sliding crude prices and optimism around a near-final agreement helped Indian benchmarks stage their longest weekly winning streak in seven months, with the Sensex closing back near 77,000 and the Nifty above 24,000 in recent sessions. Foreign portfolio investors, who have dumped a record $30.6 billion of Indian stocks so far this year, even staged their biggest single day of buying since February, a tentative sign that clarity on trade could coax overseas money back.

The caveats are real. Both governments have spoken warmly before without crossing the line, one Bloomberg report noted that neither side would say whether they had actually narrowed their differences this week, and the structural obstacles \u2014 the Section 301 probe, the post-Supreme Court legal vacuum \u2014 have not vanished. A framework agreed is not a treaty signed.

## Why It Matters for the Diaspora

For the diaspora, this is more than a macro headline. A US-India trade pact would directly shape the economics of the goods and industries the community is most tied to \u2014 Indian pharmaceuticals, textiles, IT services and the cross-border ventures many NRIs found, fund or work within. A favourable tariff regime makes Indian exporters more competitive and burnishes the long-term India growth story that underpins so many diaspora portfolios and remittance decisions.

It also sits at the emotional centre of the relationship the diaspora embodies. Indian-Americans are, in a sense, the largest living bridge between the two economies, and a deal that deepens commercial ties \u2014 while a breakdown that hardens them \u2014 affects the texture of life on both sides of that bridge. For now, the watchword from New Delhi is patience with a purpose: a deal worth having, Goyal is signalling, is worth holding out for the right terms. The diaspora, like the markets, will be watching the calendar as July approaches."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["vitamin D supplement capsules", "sunlight skin sun exposure person", "dietary supplement pills tablets"],
                          ["vitamin d supplement pills", "sunlight person outdoors"], None),
    articles[1]["slug"]: (["leafy green vegetables spinach healthy", "berries nuts antioxidant healthy food", "lentils legumes beans vegetables"],
                          ["leafy greens healthy food", "berries nuts healthy diet"], None),
    articles[2]["slug"]: (["Piyush Goyal", "India United States flags trade", "shipping containers port export trade"],
                          ["shipping containers cargo trade", "international trade port"], "Piyush Goyal"),
}
img_captions = {
    articles[0]["slug"]: "New research finds vitamin D deficiency is common year-round, especially among people with darker skin pigmentation",
    articles[1]["slug"]: "An anti-inflammatory diet rich in leafy greens, berries and legumes was tied to lower Alzheimer's risk in the genetically predisposed",
    articles[2]["slug"]: "India's commerce minister Piyush Goyal, who said the India-US trade deal is finalised but awaits a tariff-advantage guarantee",
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
