#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-23 06:00 UTC batch.
Topics:
  1. Age-related weakness is as much brain as muscle — an Ohio University study
     (Journal of Neurophysiology, 66 older adults) used electrical stimulation to
     show weak older adults still had untapped muscle, suggesting the nervous
     system's drive, not just shrinking muscle, limits strength. — lifestyle-health
  2. GLP-1 weight-loss drugs and movement — a study presented at ENDO 2026
     (753 adults, fitness-tracker data) found people took fewer steps and did
     less activity after starting Ozempic/Wegovy-class drugs. — lifestyle-health
  3. India's weakest monsoon in 11 years — a strong El Nino is delaying rains
     and bringing dangerous heat, adding risk to growth, food inflation and
     the rupee even as bigger irrigation and reservoir buffers cushion the blow. — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0600z.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0600z.bin"):
            with open("/tmp/_img_dl0600z.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0600z.bin")
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
# ARTICLE 1: Brain drives age-related weakness (lifestyle-health)
# ============================================================
articles.append({
    "headline": "The Weakness That Comes With Age May Live as Much in the Brain as in the Muscle, a New Study Finds",
    "subheadline": "When researchers gave older adults a jolt of electrical stimulation at the moment they thought they were pushing as hard as they could, the weakest among them produced far more force \u2014 a sign that ageing nerves, not just shrinking muscle, may be holding strength back.",
    "slug": "age-related-weakness-brain-nervous-system-neural-drive-ohio-university-journal-neurophysiology-66-adults-diaspora-20260623-0600",
    "category": "lifestyle-health",
    "vertical": "healthy-aging",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "For NRI families caring for ageing parents across continents \u2014 often advising on health by video call \u2014 the finding reframes the goal from simply lifting weights to keeping the brain-to-muscle connection sharp, suggesting that balance work, coordination and learning new movements deserve a place alongside resistance training in the routines that keep elders independent.",
    "sources": json.dumps([
        {"name": "Journal of Neurophysiology \u2014 Ohio University study on neural drive and strength in older adults (66 participants)", "url": "https://journals.physiology.org/journal/jn"},
        {"name": "Knowridge Science Report \u2014 What Causes Muscle Weakness in Older People?", "url": "https://knowridge.com/2026/06/what-causes-muscle-weakness-in-older-people/"}
    ]),
    "body": """Climbing the stairs gets harder. Rising from a low chair takes a push of the arms. Carrying the groceries in from the car leaves the arms trembling. For decades, the standard explanation for this slow erosion of strength has been simple: muscles shrink with age, and smaller muscles are weaker muscles. A new study suggests that explanation is, at best, only half the story.

## What the Researchers Did

Scientists at Ohio University recruited 66 older adults, with an average age of about 70, and put their leg muscles to a revealing test. Each volunteer sat in a chair and pushed against a resistance as hard as they possibly could. Then, at the exact moment a participant believed they had reached their absolute maximum, the researchers delivered a small burst of electrical stimulation directly to the muscle.

The trick is elegant. If the electrical jolt squeezed out extra force, it meant the muscle itself still had more to give \u2014 and that the person's own brain and nerves had simply failed to summon it. If nothing extra came, the muscle was genuinely maxed out. The findings were published in the Journal of Neurophysiology.

## The Surprising Result

The people who were weakest at the start gained the most from the electrical nudge. On average, their force output jumped by 14.2 percent once the stimulation kicked in. The stronger participants, by contrast, showed only small gains \u2014 their nervous systems were already driving their muscles close to full capacity.

In plain terms: many older adults who look and feel weak are sitting on reserves of muscle power they cannot fully access. The bottleneck is not always the muscle. It is often the signal travelling from the brain, down the nerves, to the muscle fibres.

## Why the Wiring Matters

Every movement \u2014 standing, stepping, reaching, gripping \u2014 begins as an electrical command in the brain that races through the nervous system to the muscle, telling it to contract. With age, that communication can grow slower and less complete. Fewer muscle fibres get recruited, and they fire less forcefully, even when the muscle tissue itself remains capable.

This reframing matters because it widens the toolkit for staying strong. For years, the advice has centred almost entirely on building bigger muscles through weight training and resistance exercise. That advice still holds: lifting builds muscle mass, supports bone, steadies balance and cuts the risk of falls. But the new work suggests that sharpening the nervous system deserves equal billing.

## What Actually Helps

The implication is that activities challenging the brain-body connection \u2014 not just the muscle \u2014 may help preserve real-world strength. Balance drills, coordination training, learning unfamiliar movements, and any activity demanding concentration and quick reactions all keep the neural pathways firing crisply.

That points toward a richer routine for older adults: resistance work to maintain the muscle, paired with movement that keeps the wiring tuned. Dance, tai chi, racquet sports, agility games and practising new physical skills all train the nervous system to recruit muscle efficiently, not merely to make muscle larger.

## The Caveats

This was a modest study \u2014 66 people, a single leg-strength test, a snapshot in time rather than a years-long trial. It shows that untapped muscle capacity exists in weaker older adults; it does not prove that any particular training programme will unlock it in daily life. The researchers note that future therapies might one day stimulate nerves directly to restore function, but those approaches remain experimental.

Still, the core insight is robust and consistent with a growing body of work: healthy ageing depends on keeping both the muscle and the nervous system in good repair, and the brain may hold a key that exercise science has underweighted.

## Why It Matters for the Diaspora

For the Indian diaspora, ageing is frequently a long-distance concern. Adult children settled in the United States, Britain or Canada often help manage the health of parents back in India, or of elders who have joined them abroad, through phone calls, video chats and visits home. The temptation is to reduce "staying strong" to a single instruction \u2014 walk more, or start lifting.

This study argues for a fuller picture. Alongside protein and resistance training, the routines that keep elders independent should protect the brain-to-muscle link: balance practice, coordination, and the mental engagement of learning new movements. Many of these are already woven into Indian life \u2014 yoga's balance postures, the footwork of classical and folk dance, the quick reactions of badminton or carrom played in the courtyard. Encouraging an ageing parent to keep moving in varied, attention-demanding ways \u2014 not just to repeat the same walk \u2014 may do more to preserve the strength that keeps them on their feet and out of hospital than muscle-building alone. For a community that prizes caring for its elders, that is a practical, low-cost prescription worth passing along."""
})

# ============================================================
# ARTICLE 2: GLP-1 users move less (lifestyle-health)
# ============================================================
articles.append({
    "headline": "People on Ozempic-Style Drugs Are Moving Less, Not More \u2014 and Doctors Say That Undercuts the Benefit",
    "subheadline": "A study of 753 adults using fitness-tracker data found that daily steps and exercise actually fell after people started GLP-1 weight-loss medications, raising the risk that muscle is lost along with fat unless physical activity is built in deliberately.",
    "slug": "glp1-weight-loss-drugs-less-physical-activity-steps-decline-endo-2026-muscle-loss-diaspora-20260623-0600",
    "category": "lifestyle-health",
    "vertical": "metabolic-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "GLP-1 drugs have spread fast among diaspora Indians battling the high rates of diabetes and obesity that run in South Asian families, and this finding is a pointed warning \u2014 for a group already prone to losing muscle and storing dangerous fat, taking the medication without keeping up movement risks trading one health problem for another.",
    "sources": json.dumps([
        {"name": "ENDO 2026 (Endocrine Society annual meeting) \u2014 study on GLP-1 use and physical activity, 753 adults, All of Us / NIH data", "url": "https://www.endocrine.org/meetings-and-events/endo"},
        {"name": "New York Post \u2014 GLP-1 users may be making a major weight-loss mistake, new study suggests", "url": "https://nypost.com/"},
        {"name": "People \u2014 People Cut Back on Physical Activity Once They Start GLP-1s for Obesity, Research Says", "url": "https://people.com/"}
    ]),
    "body": """The assumption seems obvious: lose weight, feel lighter, and surely you move more. A new study of people taking GLP-1 weight-loss drugs found the opposite. After starting medications such as Ozempic and Wegovy, people did not become more active \u2014 they became less active. And experts warn that the gap could quietly undermine the very health gains the drugs are meant to deliver.

## What the Study Found

Researchers analysed daily activity for 753 adults with obesity, drawing on data from the National Institutes of Health's All of Us Research Program, which links participants' health records with readings from Fitbit-style wearable trackers. The team compared each person's movement before they began a GLP-1 medication with their movement afterward. The findings were presented at ENDO 2026, the Endocrine Society's annual meeting in Chicago.

The numbers moved in the wrong direction. Average daily steps fell from about 5,047 to 4,487. Moderate-to-vigorous physical activity dropped from 28 minutes a day to 22. The steepest declines showed up in men and in people who already had joint or muscle pain. Other factors \u2014 age, heart failure, prior stroke \u2014 did not change the pattern.

## Why a Drop in Activity Is a Problem

GLP-1 medications \u2014 a class that includes semaglutide, liraglutide, dulaglutide and tirzepatide \u2014 work largely by suppressing appetite, and they have helped millions lose substantial weight. But the weight they strip away is not only fat. These drugs reduce both fat mass and lean muscle mass, a well-documented side effect.

That is precisely why movement matters more, not less, for people taking them. "GLP-1 drugs like semaglutide, liraglutide, dulaglutide and tirzepatide reduce both fat and lean muscle mass," study lead Sajana Maharjan, MD, of HSHS St. John's Hospital in Springfield, Illinois, noted in an Endocrine Society release, adding that physical activity is "essential for preserving strength and long-term health." If a person sheds muscle while also moving less, they can emerge lighter on the scale but weaker, with poorer metabolic resilience than the number suggests.

## A Counterintuitive Finding

"While many assume that weight loss leads naturally to increased physical activity, our study suggests otherwise," Maharjan said. The research, described as the first of its kind, found no evidence that dropping weight on these drugs nudged people to walk or exercise more. If anything, reduced appetite and lower energy intake may leave some users with less drive to be active.

The takeaway from the researchers is blunt. "The findings in our study reinforce that exercise cannot be optional for people taking these medications," Maharjan said. "People need targeted interventions that encourage physical activity alongside medication for obesity."

## The Caveats

The study was presented at a conference, and such findings typically await full peer-reviewed publication before they are considered settled. It is also observational: it shows that activity fell after people started the drugs, but cannot prove the medication itself caused the decline, as opposed to other life factors. The cohort was mostly women, with an average age in the early 50s, so the pattern may differ in other groups.

Even with those limits, the signal aligns with what doctors increasingly emphasise: the drugs are a tool, not a cure, and they work best as part of a programme that protects muscle and movement.

## How to Read It

The practical message is to treat exercise \u2014 especially resistance or strength training \u2014 as a non-negotiable companion to the medication, not an afterthought. Lifting weights, resistance bands, bodyweight exercises and adequate protein all help preserve the lean muscle the drugs tend to erode. Walking targets, however modest, give the body a floor of daily activity to defend against the slide the study documented.

## Why It Matters for the Diaspora

For the Indian diaspora, this lands on familiar ground. South Asians develop type 2 diabetes and obesity-related disease at higher rates and often younger ages than many other populations, and frequently while appearing slim \u2014 a pattern doctors tie to a tendency to store fat around the organs and carry relatively little muscle. GLP-1 drugs have been embraced quickly within diaspora communities grappling with exactly these conditions.

That makes the warning especially relevant. For a group already predisposed to low muscle mass, losing more muscle while moving less is a poor trade. The lesson is not to avoid the medication \u2014 for many it is genuinely life-changing \u2014 but to pair it with deliberate strength training, enough protein and a daily-step habit, so the weight that comes off is fat, and the strength that keeps a person healthy stays on. NRI patients starting these drugs would do well to ask their doctor not just about dosing, but about the exercise and protein plan that should go with it."""
})

# ============================================================
# ARTICLE 3: India's weak monsoon / El Nino economic risk (markets-finance)
# ============================================================
articles.append({
    "headline": "India Faces Its Weakest Monsoon in 11 Years \u2014 but This Time the Economy Is Better Armoured",
    "subheadline": "A strengthening El Ni\u00f1o has delayed the rains and brought dangerous heat, threatening harvests, food prices and growth. Yet bigger reservoirs and far wider irrigation mean the damage may be more contained than the alarming headlines suggest.",
    "slug": "india-weakest-monsoon-11-years-el-nino-heat-food-inflation-growth-rupee-irrigation-buffers-nri-investor-20260623-0600",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "A poor monsoon feeds straight into the things NRIs watch most closely about India \u2014 food inflation that erodes the rupee's value, the central bank's room to cut rates, and the strength of the currency their remittances and investments are denominated in \u2014 making this year's rains a quiet but real input into diaspora financial decisions.",
    "sources": json.dumps([
        {"name": "Reuters \u2014 India File: Searing El Ni\u00f1o tests crop buffers, exposes workers", "url": "https://www.reuters.com/world/india/india-file-searing-el-nio-tests-crop-buffers-exposes-workers-2026-06-16/"},
        {"name": "Reuters \u2014 India likely won't export sugar for years as El Nino, ethanol squeeze supply", "url": "https://www.reuters.com/"},
        {"name": "India Meteorological Department / RBI Monetary Policy statements on monsoon and inflation risk", "url": "https://mausam.imd.gov.in/"}
    ]),
    "body": """Every summer, the arrival of the monsoon is the single most watched economic event in India \u2014 more than any budget or central-bank meeting. The rains water the crops that feed 1.4 billion people, replenish the reservoirs that power cities, and shape the prices of everything from onions to lentils. This year, the news is worrying: India is staring at its weakest monsoon in 11 years. But a closer look suggests the economy is better prepared to absorb the blow than it once was.

## What Is Happening to the Rains

The India Meteorological Department is forecasting the lowest levels of precipitation since 2015, with the rains arriving late and central and northern regions running drier than normal. June rainfall in parts of the country has been more than 40% below average. The culprit is a strengthening El Ni\u00f1o \u2014 the periodic warming of the Pacific that scrambles weather worldwide and, in India, typically suppresses the monsoon.

The timing is awkward. The shortfall lands on an economy already contending with elevated oil prices and a weak rupee. The Reserve Bank of India has pared its growth forecast and raised its inflation estimate for the year, citing the monsoon explicitly among the key risks it is watching.

## Why the Damage May Be Contained

Here is the more reassuring part of the story. Compared with the drought of 11 years ago, India is structurally better insulated against a weak monsoon, and economists across the private sector broadly agree.

The biggest reason is irrigation. About 55% of India's gross cropped area is now irrigated, up from roughly 40% in 2010\u201311, which loosens the link between rainfall and output. "With 55% of the gross cropped area now irrigated, output is less tied to rainfall," Barclays chief India economist Aastha Gudwani noted. Water buffers are also unusually full: reservoir storage is around 29%, above the 10-year average, thanks to abundant rains the previous year. Some analysts argue that reservoir levels now matter more for food production and inflation than the season's rainfall total alone.

## The Heat Is the Bigger Threat

If rainfall is less decisive than it used to be, the heat may be more dangerous. "We find that the probability of high temperatures is stronger than the probability of low rains, and the quantum of rise in temperatures during El Ni\u00f1o years is rising," HSBC chief India economist Pranjul Bhandari wrote, warning that perishables like fruit and vegetables are the most vulnerable to scorching weather.

The human cost is stark. A study by researchers at the India Energy and Climate Centre at the University of California, Berkeley, found that a single day of extreme heat can cause an estimated 3,400 excess deaths nationwide, and a five-day heatwave nearly 30,000. Millions who work outdoors \u2014 farm labourers, construction workers, street vendors \u2014 are most exposed, and India has already logged soaring power demand and heatstroke cases this season.

## The Market Read-Through

For markets, the monsoon feeds two channels: food inflation and rural demand. A weak season can push up prices of vegetables, pulses and sugar \u2014 India is now expected to produce less sugar than it consumes this year, and may not export for some time \u2014 which in turn limits how much room the RBI has to cut interest rates. Softer rural incomes can also dent demand for everything from motorcycles to consumer goods, weighing on company earnings.

Yet the cushions matter. Fuller reservoirs, wider irrigation and an agricultural sector less hostage to rainfall mean the worst-case spiral of failed harvests and runaway food inflation is less likely than the bleak headlines imply. The wildcard is heat, which the buffers do little to soften.

## How to Read It

For investors, the sensible posture is watchful rather than alarmed. The monsoon's progress through July and August \u2014 not just June's slow start \u2014 will determine the final picture, and a late recovery in the rains can rescue a poor beginning. Food inflation prints and the RBI's commentary will be the clearest signals of whether the season is denting the broader economy.

## Why It Matters for NRIs

For the diaspora, the monsoon is not the distant agricultural curiosity it may seem. Its fingerprints land squarely on the variables NRIs track: food inflation shapes the rupee's purchasing power and the RBI's rate path, and a weaker currency directly affects the value of remittances sent home and of rupee-denominated investments and property.

A poor monsoon that stokes inflation could keep the RBI cautious on rate cuts and add pressure on a rupee already strained by oil and foreign outflows \u2014 a backdrop that makes the central bank's recent push to lure diaspora dollar deposits all the more pointed. For NRIs weighing when to remit, how to time investments, or whether to lock in fixed deposits, this year's rains are a real, if indirect, input. The encouraging counterpoint is that India's economy is no longer as hostage to the clouds as it once was \u2014 a structural strengthening that, over the long run, makes the country a steadier place to keep one's money."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["elderly person physiotherapy strength exercise", "senior balance exercise older adult", "older adult walking exercise outdoor"],
                          ["senior fitness exercise older adult", "elderly physiotherapy strength"], None),
    articles[1]["slug"]: (["person walking fitness tracker steps", "people jogging walking exercise outdoor", "weight training dumbbell exercise gym"],
                          ["walking exercise outdoor fitness", "strength training weights"], None),
    articles[2]["slug"]: (["monsoon rain India farmer field", "India agriculture paddy field farmer", "drought dry cracked field india"],
                          ["monsoon rain india agriculture", "farmer field india crops"], None),
}
img_captions = {
    articles[0]["slug"]: "A study of 66 older adults found weaker participants had untapped muscle strength their nervous systems were not fully activating",
    articles[1]["slug"]: "A study of 753 adults found daily steps and exercise fell after people began GLP-1 weight-loss medications",
    articles[2]["slug"]: "India faces its weakest monsoon in 11 years as a strengthening El Ni\u00f1o delays the rains and brings dangerous heat",
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
