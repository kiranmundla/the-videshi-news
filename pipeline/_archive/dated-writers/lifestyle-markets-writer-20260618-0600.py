#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-18 06:00 UTC batch.
Topics (distinct from the 02:00 batch):
  1. Ultra-processed foods harm beyond their nutrients — it's how they're made (Tufts, AJPH) — lifestyle-health
  2. The most addictive foods aren't only the sugary ones — refined starches drive cravings (Michigan/Gearhardt) — lifestyle-health
  3. India-US interim trade deal nears as USTR Greer visits June 23-24; first tranche eyed by mid-July — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0600.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0600.bin"):
            with open("/tmp/_img_dl0600.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0600.bin")
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
# ARTICLE 1: Ultra-processed foods — it's how they're made (lifestyle-health)
# ============================================================
articles.append({
    "headline": "It May Not Be Just What's in Ultra-Processed Foods That Hurts You \u2014 It's How They're Made",
    "subheadline": "A new Tufts University analysis of two decades of US health data found that people who ate more ultra-processed foods had worse health and a higher risk of early death \u2014 even after accounting for the nutrition inside the food. The processing itself, the researchers argue, may carry an independent harm.",
    "slug": "ultra-processed-foods-processing-independent-harm-tufts-ajph-nhanes-mortality-diaspora-20260618",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Indian and South Asian families increasingly lean on packaged namkeen, instant mixes, sugary biscuits and ready meals as life gets busier abroad \u2014 and this research suggests the industrial processing in those products may damage health in ways that reading the nutrition label alone will never reveal.",
    "sources": json.dumps([
        {"name": "American Journal of Public Health / Tufts Food is Medicine Institute \u2014 Ultra-processed food, processing, and mortality (NHANES 1999\u20132018)", "url": "https://ajph.aphapublications.org/"},
        {"name": "Tufts University \u2014 Friedman School of Nutrition Science and Policy (news release)", "url": "https://nutrition.tufts.edu/"},
        {"name": "Medical Xpress \u2014 'It may not just be what's in ultra-processed foods, but how they're made'", "url": "https://medicalxpress.com/"}
    ]),
    "body": """For years, the case against ultra-processed foods rested on what was inside them: too much sugar, too much salt, too many refined grains and fats. Eat better versions of those products, the thinking went, and the danger fades. A new study from Tufts University complicates that comfortable idea. It suggests the harm may lie not only in the ingredients but in the very act of industrial processing \u2014 something no nutrition label captures.

## What the Researchers Did

The study came from the Food is Medicine Institute at Tufts University's Friedman School of Nutrition Science and Policy and was published in the American Journal of Public Health. Researchers drew on a large and well-respected dataset: ten consecutive cycles of the National Health and Nutrition Examination Survey (NHANES), spanning 1999 to 2018, linked to the National Death Index to track who died and when.

Participants had reported what they ate through detailed 24-hour dietary recalls. The researchers then classified every food by how heavily it was processed \u2014 from minimally processed items like fruits and vegetables up to ultra-processed foods, the industrially manufactured products built from ingredients and additives you would never find in a home kitchen.

The crucial move was statistical. The team measured the link between ultra-processed food intake and health both before and after adjusting for the nutritional quality of those foods. In other words, they tried to separate the effect of the bad nutrition from the effect of the processing itself.

## What They Found

The pattern was consistent and troubling. People who ate more ultra-processed foods had worse health markers \u2014 higher body weight, higher blood pressure, poorer blood sugar control \u2014 and a higher long-term risk of death.

The headline finding is what survived the adjustment. Even after accounting for the overall nutritional quality of the food, heavier ultra-processed food eaters still fared worse. That residual harm is the signal the researchers care about. It implies that something about ultra-processed foods beyond their sugar, salt and fat content is doing damage.

## Why Processing Itself Might Matter

If it is not just the nutrients, what is it? The study's senior author, cardiologist Dariush Mozaffarian, who directs the Food is Medicine Institute, points to several suspects that conventional nutrition metrics ignore.

One is physical structure. Industrial processing breaks down the natural cellular architecture of food, which changes how quickly the body digests and absorbs it and how full it makes you feel. Another is the loss of beneficial compounds \u2014 the fragile phytochemicals and fibers stripped away during manufacturing. A third is what gets added: emulsifiers, stabilizers and other additives that may disturb the gut. And a fourth is contamination from the manufacturing and packaging process itself, including chemicals that migrate from plastic and the by-products of high-heat industrial cooking.

None of these show up when you scan a label for calories, sodium or grams of sugar. That is precisely the point: the current way societies measure and regulate food may be missing an entire dimension of risk.

## The Caveats

This is an observational study, and that limit matters. It can show a strong, consistent association between ultra-processed food and poor outcomes, but it cannot by itself prove that processing causes the harm. People who eat a lot of ultra-processed food often differ in many other ways \u2014 income, activity, access to fresh food \u2014 and while the researchers adjusted for a great deal, no statistical model is perfect. Dietary recalls also rely on memory and are imperfect. The honest reading is that this is powerful, biologically plausible evidence that strengthens an already large body of research \u2014 not the final word. Larger controlled trials, some already underway, are needed to nail down cause and effect.

## Why It Lands for the Diaspora

For Indian and South Asian families abroad, the finding is quietly important. Migration and busy dual-income life push households toward convenience: packaged namkeen and chips, sugary biscuits with chai, instant noodles, frozen parathas, ready-to-heat curries and bottled sauces. Many of these feel culturally familiar and even homemade in spirit \u2014 but they are, in manufacturing terms, ultra-processed.

The community also carries an elevated, earlier risk of diabetes and heart disease, which means the metabolic toll of these foods may bite harder and sooner than it does in the general population. The study reframes the goal: it is not enough to hunt for the low-sugar biscuit or the reduced-sodium snack. The act of choosing genuinely fresh, minimally processed food \u2014 dal cooked from scratch, fresh vegetables, fruit, plain dairy \u2014 may matter in its own right.

## What To Actually Do

Aim for foods that look close to how they grew or were made at home. Build meals around whole ingredients you cook yourself: lentils and beans, vegetables, fruit, whole grains, eggs and plain dairy. Treat heavily packaged snacks and ready meals as occasional, not daily, staples \u2014 and do not be reassured by a virtuous-looking nutrition panel on an ultra-processed product. The label is necessary, but this research suggests it is not sufficient. The simplest rule remains the oldest one: the less a food has been transformed by a factory before it reaches your plate, the safer the bet."""
})

# ============================================================
# ARTICLE 2: Food addiction — not just sugar, refined starches (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Most Addictive Foods Aren't Only the Sugary Ones. A New Study Points the Finger at Refined Starch.",
    "subheadline": "Researchers analyzing why ultra-processed foods are so hard to stop eating found that the usual villain \u2014 sugar \u2014 is only half the story. Rapidly digested refined carbohydrates, even in savory snacks with little or no added sugar, may be just as powerful a driver of cravings.",
    "slug": "ultra-processed-food-addiction-refined-starch-not-just-sugar-gearhardt-michigan-diaspora-snacking-20260618",
    "category": "lifestyle-health",
    "vertical": "health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asian snacking culture is built on refined-flour and rapidly-digested treats \u2014 namkeen, sev, mathri, fried maida snacks and white-rice indulgences \u2014 and this research suggests these savory staples may hijack appetite as effectively as anything sweet, a blind spot for a community already prone to diabetes.",
    "sources": json.dumps([
        {"name": "Food addiction research led by Ashley Gearhardt, University of Michigan \u2014 ultra-processed foods and refined carbohydrates", "url": "https://lsa.umich.edu/psych"},
        {"name": "CNN Health \u2014 'Addiction to ultraprocessed foods is real and increasing'", "url": "https://www.cnn.com/health"}
    ]),
    "body": """Anyone who has ever opened a packet of chips meaning to eat a few \u2014 and finished the bag \u2014 knows the feeling the science is trying to explain. New research into why ultra-processed foods are so hard to resist has reached a conclusion that upends a common assumption: it is not mainly the sugar. Rapidly digested refined starches may be just as much to blame.

## Rethinking the Villain

Public health messaging has long cast added sugar as the prime mover behind cravings and overeating. The new analysis, led by food-addiction researcher Ashley Gearhardt at the University of Michigan, argues that focusing on sugar alone misses much of the picture.

The clue is in which foods people find hardest to stop eating. Many of the most habit-forming items named in the research are not sweet at all. Potato chips, fast-food chicken tenders, breakfast sandwiches, hash browns, garlic bread, store-bought macaroni and cheese \u2014 these savory products topped the list alongside the expected cookies, cakes and candy. As Gearhardt put it, many potato chips contain little or no added sugar, yet they still deliver rapidly absorbed carbohydrates.

That common thread \u2014 refined carbohydrate that the body converts quickly into glucose \u2014 turns out to unite both the sweet and the savory offenders.

## The Blood-Sugar Rollercoaster

The mechanism is a familiar one, applied in a new way. Refined flours and starches are digested fast, spiking blood sugar shortly after eating. The starch in something like a potato chip behaves much the same way as the sugar in a cookie. That quick high is followed by a sharp drop, and the resulting empty, unsatisfied feeling in the stomach can drive a person to reach for more.

It is a loop that resists willpower: eat, spike, crash, crave, repeat. And it helps explain why savory snacks with no sweetness at all can be every bit as compulsive as dessert.

## It Is the Combination

Refined carbohydrate is not acting alone. The research stresses that the most irresistible foods deliver high levels of fat and rapidly digested carbohydrate together, in an energy-dense package \u2014 a combination rarely found in nature. Gearhardt described it as fat and carbs working in synergistic packages that create the addictive bite.

That synergy is largely a product of industrial design. Manufacturers engineer the precise mix of crunch, fat, salt and fast carbohydrate that lights up the brain's reward circuitry. The result is food built, intentionally or not, to override the body's natural signals that say enough.

## The Caveats

It is worth being precise about the language. The food industry's representatives argue that this kind of research does not prove specific foods cause clinical addiction in the medical sense, and that is a fair caution \u2014 "food addiction" remains a debated and evolving concept, not a settled diagnosis. The findings describe which foods are most habit-forming and offer a plausible biological reason, rather than proving that snacks are addictive the way a drug is. Individual responses also vary widely. None of this means anyone should feel they have a disease for finishing a bag of chips; it means the deck is genuinely stacked, by design, against easy moderation.

## Why It Lands for the Diaspora

For South Asians, the savory twist in this research hits especially close to home. The community's snacking culture is built largely on refined carbohydrate: namkeen and sev, mathri and fried maida snacks, samosas and pakoras, and generous helpings of white rice and refined-flour breads. Much of it is not sweet \u2014 and so it has long escaped the suspicion reserved for sugary treats.

This study suggests that escape was unearned. A bowl of crisp, salty namkeen may set off the same rapid blood-sugar spike and crash, and the same drive to keep eating, as anything from the dessert table. For a population already facing high rates of diabetes and insulin resistance at lower body weights, that is a meaningful blind spot. The festive and everyday foods that feel innocent precisely because they are not sweet may be quietly doing real work on appetite and metabolism.

## What To Actually Do

The takeaway is not guilt but strategy. Treat refined-starch snacks \u2014 sweet or savory \u2014 as the genuinely hard-to-moderate foods they are, and design around them rather than relying on willpower in the moment. Keep them out of easy reach and buy them in single portions rather than family-size bags. Pair any indulgence with protein, fiber or fat \u2014 nuts with the chips, dahi with the snack \u2014 to blunt the blood-sugar spike that fuels the next craving. Lean on slower carbohydrates that do not trigger the same rollercoaster: whole grains, lentils, roasted chana, fruit and vegetables. And recognize the loop for what it is. The empty feeling that arrives 30 minutes after a fast-carb snack is not a failure of discipline \u2014 it is the chemistry working exactly as the product was designed to make it work."""
})

# ============================================================
# ARTICLE 3: India-US interim trade deal nears (markets-finance)
# ============================================================
articles.append({
    "headline": "An India-US Trade Deal Is Suddenly Close. The US Trade Chief Visits This Month to Seal the First Tranche.",
    "subheadline": "US Trade Representative Jamieson Greer travels to New Delhi on June 23-24 to put final touches on an interim agreement, with India's commerce minister signaling the first tranche could be done by mid-July. With a US-Iran truce cooling oil and the World Bank lifting its growth forecast, the macro backdrop has rarely looked better.",
    "slug": "india-us-interim-trade-deal-greer-visit-june-tranche-mid-july-nri-investor-markets-20260618",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "An India-US trade pact sits at the center of the diaspora's two worlds \u2014 it shapes the export sectors and equities many NRIs invest in, the rupee that governs how far their remittances stretch, and the broader US-India relationship that frames diaspora life in America.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 'US Trade Representative Greer to visit India on June 23-24 for talks'", "url": "https://www.reuters.com/world/india/"},
        {"name": "Reuters \u2014 'India's May trade gap narrows as exports rise; U.S. trade talks in focus'", "url": "https://www.reuters.com/markets/"},
        {"name": "Reuters \u2014 'India's stock benchmarks log longest winning run in 2 months as oil prices ease'", "url": "https://www.reuters.com/markets/asia/"}
    ]),
    "body": """After months of friction and the threat of punishing tariffs, an India-US trade agreement has moved abruptly within reach. The clearest sign came this week: US Trade Representative Jamieson Greer is scheduled to travel to New Delhi on June 23-24 to give what an Indian official called the final touches to an interim deal between the two governments.

## What Is Actually Happening

Greer's visit is the diplomatic capstone on talks that have gained momentum fast. India's trade minister, Piyush Goyal, said earlier this month that the first tranche of a bilateral trade agreement could be concluded by mid-July \u2014 a strikingly concrete timeline for negotiations that not long ago looked stuck amid Washington's tariff threats on Indian goods.

The structure matters. This is being framed as an interim or first-tranche deal, not a sweeping comprehensive pact. The two sides appear to be aiming to lock in an early-harvest agreement \u2014 settling the areas where they can agree now and pricing in the politically harder questions for later rounds. For markets, even a partial deal would remove a large cloud of uncertainty that has hung over Indian exporters and the broader relationship.

## The Backdrop Just Got Friendlier

The trade news lands amid a sudden run of good macroeconomic luck for India. A preliminary US-Iran peace framework \u2014 which would halt the conflict in West Asia and reopen the Strait of Hormuz \u2014 sent oil prices tumbling, with Brent dropping toward three-month lows. For a country that imports more than 80 percent of its crude, cheaper oil is close to an unalloyed positive: it shrinks the import bill, eases inflation, narrows the current account deficit and takes pressure off the rupee.

The data has cooperated too. India's May trade gap narrowed as exports rose, with a healthy services surplus underpinning the external accounts. And the World Bank recently upgraded India's growth forecast for the 2027 financial year to 6.6 percent, even as it trimmed estimates for major economies elsewhere \u2014 a reminder that India remains one of the fastest-growing large economies in the world.

## How Markets Are Reacting

Investors have been buying the improving story. India's benchmark indices logged their longest winning streak in two months, with the Nifty and Sensex each climbing around 4 percent over four sessions, propelled chiefly by the slide in oil prices. Information-technology stocks, sensitive to the US outlook, firmed up, and defence shares surged after the country posted record production and exports.

Perhaps most significant for the medium term, foreign portfolio investors \u2014 who have sold a record sum of Indian equities this year \u2014 turned net buyers after a long stretch of selling. A concrete trade deal could accelerate that shift, giving global funds one more reason to return to a market they had been steadily exiting.

## The Caveats

Optimism should be tempered with memory: India-US trade talks have raised hopes before, only to stall over agriculture, dairy, data and tariff lines that touch sensitive domestic constituencies on both sides. A first tranche by mid-July is a target, not a signed document, and interim deals can slip. The US-Iran framework that is cushioning oil prices is itself preliminary and reversible; if it unravels, crude could climb back and erase much of the recent macro relief. And a partial trade deal, by definition, leaves the thorniest issues unresolved for future negotiation. The direction of travel is genuinely encouraging \u2014 but a prudent investor treats a near-deal as a near-deal, not a done one.

## Why It Lands for the Diaspora

Few stories sit so squarely at the intersection of the diaspora's two homes. An India-US trade agreement directly shapes the export-facing sectors \u2014 pharmaceuticals, textiles, engineering goods, IT services \u2014 that populate many NRI portfolios. It moves the rupee, which determines how much value a remittance carries when it reaches family in India. And it sets the tone of the broader US-India partnership that frames the diaspora's standing and prospects in America.

For NRIs invested in Indian equities, the combination now in play \u2014 a possible trade deal, cheaper oil, cooling inflation, returning foreign money and a World Bank upgrade \u2014 is about as supportive a setup as the market has offered this year. The sensible response is to treat it as a reason for measured confidence rather than a green light to chase the rally: stay diversified, keep a long horizon, and let a confirmed deal, rather than the anticipation of one, drive any big allocation decisions.

## The Bottom Line

India and the United States appear closer to a trade agreement than they have been in a long while, with a senior US official flying in this month and a mid-July target on the table. Paired with falling oil, easing inflation and a brightening growth outlook, it has lifted Indian markets to their best run in months. For the diaspora watching both countries at once, it is a milestone worth tracking \u2014 with the standard reminder that, in trade talks, close is not the same as closed."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["ultra processed food snacks", "junk food packaged snacks", "processed food supermarket"],
                          ["ultra processed food", "packaged snack food"], None),
    articles[1]["slug"]: (["potato chips snack bowl", "savory snacks fried", "namkeen indian snack"],
                          ["potato chips snack", "fried snacks bowl"], None),
    articles[2]["slug"]: (["cargo container ship port trade", "shipping containers port", "international trade cargo"],
                          ["cargo container ship", "shipping port containers"], "Piyush Goyal"),
}
img_captions = {
    articles[0]["slug"]: "Packaged ultra-processed foods; a Tufts analysis found their industrial processing may harm health independent of the nutrition they contain",
    articles[1]["slug"]: "Savory snacks like potato chips and fried namkeen deliver rapidly digested refined starch that researchers link to hard-to-stop cravings",
    articles[2]["slug"]: "Indian Commerce Minister Piyush Goyal, who said the first tranche of an India-US trade deal could be concluded by mid-July",
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
