#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-16 10:00 UTC batch.
Topics:
  1. Dapagliflozin (SGLT2) prevents heart failure in genetic cardiomyopathy carriers (Nature Medicine, DECLARE-TIMI 58) — lifestyle-health
  2. Four minutes of strength work (FAST-2, Penn State, PLOS One) restores function in older adults — lifestyle-health
  3. GIFT City IFSC rising as NRI investment magnet in 2026 — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl10.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl10.bin"):
            with open("/tmp/_img_dl10.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl10.bin")
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

def source_image(slug, commons_queries, pexels_queries):
    candidates = []
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
# ARTICLE 1: Dapagliflozin + genetic cardiomyopathy (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Common Diabetes Pill Erased Heart Failure in People Born With a Risky Gene. The Trial Result Is Stunning.",
    "subheadline": "Re-analysing the 12,000-patient DECLARE-TIMI 58 trial, Harvard and MIT researchers found that dapagliflozin \u2014 an inexpensive SGLT2 inhibitor already used for type 2 diabetes \u2014 cut heart-failure hospitalisation about eight times more powerfully in people carrying inherited cardiomyopathy gene variants. Among carriers with no prior heart failure, none on the drug developed it, against 12.8 per cent on placebo.",
    "slug": "dapagliflozin-sglt2-genetic-cardiomyopathy-heart-failure-declare-timi-nature-medicine-diaspora-20260616",
    "category": "lifestyle-health",
    "vertical": "health-science",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "South Asians carry both an unusually high burden of type 2 diabetes \u2014 the exact population already prescribed SGLT2 inhibitors \u2014 and a documented predisposition to inherited cardiac disease and young-onset heart failure, so a cheap drug many NRIs already swallow daily may double as a genetic-risk shield, making family history and genetic testing newly worth discussing with a doctor.",
    "sources": json.dumps([
        {"name": "Nature Medicine (Dapagliflozin and heart failure risk in carriers of cardiomyopathy-associated genetic variants)", "url": "https://www.nature.com/nm/"},
        {"name": "Fox News Health (Diabetes drug could slash risk of fatal heart condition in one group)", "url": "https://www.foxnews.com/health/diabetes-drug-could-slash-risk-fatal-heart-condition-one-group-scientists-reveal"},
        {"name": "DECLARE-TIMI 58 trial, TIMI Study Group / Harvard Medical School", "url": "https://timi.org/"}
    ]),
    "body": """For years, a diagnosis of inherited cardiomyopathy came with a cruel asymmetry. Doctors could tell a patient that a gene they were born with had loaded the dice toward heart failure, but they had little to actually offer in return \u2014 watchful waiting, lifestyle advice, and the hope that symptoms would hold off. A new analysis published in Nature Medicine suggests that asymmetry may be closing, and the tool turning out to help is one that millions of people already have in their medicine cabinets.

## What the Researchers Did

Scientists from Harvard Medical School, Mass General Brigham and MIT went back to the DECLARE-TIMI 58 trial, a large randomised study of more than 12,000 adults with type 2 diabetes and elevated cardiovascular risk. The original trial tested dapagliflozin, an SGLT2 inhibitor \u2014 a class of drug that lowers blood sugar by flushing glucose out through the kidneys and that has, over the past few years, become foundational in cardiovascular and kidney medicine.

The twist in this re-analysis was genetic. Among the trial participants, about 121 carried rare inherited gene variants linked to cardiomyopathy, a progressive disease of the heart muscle. The researchers asked a sharp question: did the drug behave differently in people born with that genetic vulnerability?

## The Finding

It behaved dramatically differently. After a median follow-up of 4.2 years, dapagliflozin lowered hospitalisation for heart failure in everyone \u2014 but the reduction was roughly eight times stronger in carriers of the genetic variant than in non-carriers.

The most striking number came from carriers who had never had heart failure before. Among that group, 12.8 per cent of those on placebo went on to develop heart failure, while not a single carrier taking dapagliflozin did. Zero events. Co-lead author Shinwan Kany, a visiting scientist at the Cardiovascular Research Center with Mass General Brigham and the Broad Institute, framed the shift bluntly: historically, finding a cardiomyopathy gene meant telling a patient they were high-risk without a specific preventive therapy to offer. "These data show we do have tools to lower risk in these individuals."

## The Necessary Caution

This is a hypothesis-generating finding, not yet a mandate. The analysis rests on a small subgroup \u2014 just 121 carriers \u2014 carved out of a larger trial that was not designed around genetics, and the authors are clear that the results need confirmation in dedicated studies. Andrew Freeman, a cardiologist at National Jewish Health who was not involved, called the work "important and provocative" but warned it "should be viewed as an exciting hypothesis-generating finding, not yet a practice-changing mandate for all patients with these genetic variants."

Still, the direction is encouraging. SGLT2 inhibitors are already proven to cut heart-failure hospitalisation across a broad range of patients, including those with diabetes, chronic kidney disease and established heart failure. What this study adds is the tantalising possibility that genetic information could one day identify the people who benefit most \u2014 and that treating them early, before symptoms appear, might prevent the disease rather than merely manage it.

## Why the Diaspora Should Take Note

The relevance to the Indian diaspora runs along two lines at once. First, South Asians carry one of the world's heaviest burdens of type 2 diabetes, which means a very large slice of the community is already exactly the kind of patient prescribed SGLT2 inhibitors. For many NRIs, the drug now under this new genetic spotlight may already be the pill they take each morning.

Second, the diaspora's relationship with heart disease is uniquely fraught. South Asians develop cardiovascular disease younger and at lower body weights than most other groups, and inherited cardiac conditions thread through many families' histories \u2014 the cousin who collapsed young, the uncle with an enlarged heart. This research reframes that family history as potentially actionable rather than merely ominous. If future trials confirm the signal, genetic screening could flag high-risk relatives, and a cheap, widely available drug could be started years before the first symptom of shortness of breath or fluid retention.

## The Bigger Picture

The study sits at the leading edge of what cardiologists call precision prevention \u2014 the idea that genetics will increasingly tell doctors not just who is at risk, but who will respond best to which therapy. "These findings are very encouraging because they suggest we may be entering an era where heart failure prevention becomes more precise and more genetically informed," Freeman said.

For now, the practical message is restrained but real. Heart failure does not begin when symptoms begin; in genetically vulnerable people, the risk is laid down years earlier. Anyone with a strong family history of cardiomyopathy or unexplained young heart failure has fresh reason to raise genetic testing with their doctor \u2014 and, if they have diabetes, to understand that the drug controlling their blood sugar may be quietly guarding their heart as well. As always, the decision to start or change any medication belongs in a clinic, not a WhatsApp group."""
})

# ============================================================
# ARTICLE 2: Four-minute FAST-2 strength training (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Four Minutes a Day Rebuilt Strength in 74-Year-Olds. The Routine Needs No Gym and No Hour You Do Not Have.",
    "subheadline": "A Penn State trial published in PLOS One tested a stripped-down programme of four moves \u2014 push-ups, chair stands, two-arm rows and stair stepping, 30 seconds each \u2014 in adults averaging 74. Marked gains in physical function showed up in just 12 weeks, dismantling the biggest excuse older adults give for skipping strength work: that it takes too long.",
    "slug": "four-minute-strength-training-fast-2-older-adults-penn-state-plos-one-diaspora-elders-20260616",
    "category": "lifestyle-health",
    "vertical": "fitness",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Ageing NRI parents and grandparents \u2014 often sedentary, intimidated by gyms, and culturally unaccustomed to formal strength training \u2014 are exactly the group at highest risk of the rapid muscle loss that steals independence, and a four-minute, no-equipment routine doable in a living room removes nearly every barrier the diaspora's elders cite.",
    "sources": json.dumps([
        {"name": "PLOS One (Functional Activity Strength Training (FAST)-2 in older adults)", "url": "https://journals.plos.org/plosone/"},
        {"name": "New York Post (Just four minutes of key exercise can quadruple fitness in older adults)", "url": "https://nypost.com/"},
        {"name": "Penn State College of Medicine", "url": "https://med.psu.edu/"}
    ]),
    "body": """Ask an older adult why they do not lift weights and the answer is almost never that they think it is useless. It is that they think it is impossible \u2014 too time-consuming, too complicated, too tied to gyms full of machines and people half their age. A new study from Penn State College of Medicine takes a wrecking ball to that excuse. It found that as little as four minutes of the right exercises, done at home with almost no equipment, produced marked improvements in physical function in people whose average age was 74.

## A Deliberately Minimal Programme

The research, published in the journal PLOS One, tested a regimen the team called FAST-2, short for Functional Activity Strength Training. It was built around just four movements: push-ups, chair stands, two-arm rows and stair stepping. Each exercise was performed for 30 seconds, followed by 30 seconds of rest \u2014 a structure simple enough to do in a living room with a set of resistance bands and an adjustable stepper, the only equipment participants were given.

About 100 adults, averaging 74 years old, were assigned either this routine or no exercise programme at all. After 12 weeks, the contrast was clear: the exercisers showed marked improvement in measures of overall physical function, the everyday capacities \u2014 rising from a chair, climbing stairs, carrying groceries \u2014 that determine whether an older person stays independent or slides toward needing help.

## Why So Little Did So Much

"The human body is designed to improve very quickly," said lead author Christopher Sciamanna. "And just a few repetitions of an exercise performed regularly can lead to huge improvements. Exercise is about forward thinking \u2014 think about what you want to be able to do and train for it."

That philosophy \u2014 training for function rather than aesthetics \u2014 is the study's quiet revolution. The four chosen moves map directly onto the physical tasks of daily living. Chair stands rehearse the act of getting up; stair stepping rehearses the stairs; rows and push-ups rebuild the pulling and pushing strength that fades first. The team built FAST-2 on earlier evidence that shorter routines can be just as effective as longer ones, and the design was explicitly aimed at the barrier that keeps most people away.

"There are huge problems with people wanting to do exercise. If we can make it short, we're partway there," co-author Smita Dandekar said.

## The Problem It Solves

The stakes are not cosmetic. Strength training is one of the best-established defences against the loss of independence in later life \u2014 it helps older adults recover from illness and injury, travel more easily and stay active for longer. Yet fewer than 20 per cent of older adults meet the recommended two days a week of muscle-strengthening activity. The gap between what works and what people actually do is enormous, and the leading suspect is the belief that meaningful strength work demands a serious time commitment.

By collapsing that commitment to four minutes of actual effort, the FAST-2 study attacks the excuse at its root. It is hard to argue you do not have four minutes.

## Why This Matters Acutely for the Diaspora

Few groups stand to gain more than the ageing parents and grandparents of the Indian diaspora. Many arrived in the US, UK or Canada later in life to help raise grandchildren, and they tend to be sedentary by habit, unfamiliar with and often intimidated by Western gym culture, and raised in a tradition where formal strength training was never part of daily life. They are also, like all South Asians, predisposed to lose muscle mass relatively early \u2014 a vulnerability The Videshi has reported on repeatedly, and one that compounds the diaspora's elevated risks of diabetes and frailty.

For this population, a gym membership is a non-starter, but a four-minute routine in the living room, perhaps alongside a grandchild, is entirely plausible. There is no commute, no equipment beyond a band and a step, no spectacle, and no embarrassment. The cultural and practical barriers that keep diaspora elders away from strength work mostly dissolve when the programme fits inside a television advertisement break.

## The Practical Bottom Line

The honest caveats apply: this was a single 12-week trial of around 100 people, and anyone with heart conditions, joint problems or balance issues should clear a new routine with a doctor and start gently, using a chair or wall for support. Push-ups can be done against a counter; chair stands can begin with the hands assisting.

But the headline is liberating. The most protective form of exercise for staying independent in old age does not require an hour, a gym or athletic history. It requires four minutes, a chair, a step and the willingness to begin. For a diaspora watching its elders age far from the support systems of home, that is a remarkably low price for keeping a parent on their own two feet."""
})

# ============================================================
# ARTICLE 3: GIFT City as NRI investment magnet (markets-finance)
# ============================================================
articles.append({
    "headline": "India Built a Tax-Light Financial City to Lure NRI Money Home. In 2026, GIFT City Is Finally Pulling.",
    "subheadline": "Once dismissed as a policy experiment, the GIFT City IFSC in Gujarat has become one of 2026's most talked-about destinations for NRI investments, India-focused funds and cross-border wealth structuring \u2014 offering a progressive regulatory regime and attractive tax incentives. But for all the momentum, its liquidity and depth still trail established hubs like Dubai and Singapore.",
    "slug": "gift-city-ifsc-nri-investment-magnet-2026-tax-incentives-dubai-singapore-comparison-diaspora-20260616",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "GIFT City is being engineered specifically as the on-ramp for NRI and OCI capital into India \u2014 a tax-efficient, dollar-friendly gateway that lets the diaspora invest in India-linked assets without routing through Dubai or Singapore \u2014 making the practical question of whether it is ready yet a direct, money-on-the-table decision for globally mobile Indians.",
    "sources": json.dumps([
        {"name": "Bar and Bench (GIFT City 2026: India's rising magnet for NRI investments)", "url": "https://www.barandbench.com/"},
        {"name": "International Financial Services Centres Authority (IFSCA)", "url": "https://ifsca.gov.in/"},
        {"name": "Mint (Can India remain the preferred emerging market for foreign investors?)", "url": "https://www.livemint.com/"}
    ]),
    "body": """For most of the past decade, GIFT City was a punchline as much as a project \u2014 a gleaming financial district rising out of the Gujarat plain that critics dismissed as an ambitious policy experiment in search of actual business. In 2026, the verdict is shifting. India's first International Financial Services Centre has become one of the year's most compelling destinations for NRI investments, India-focused funds and cross-border wealth structuring, drawing the attention of non-resident Indians, global family offices, private wealth managers and investment funds worldwide.

## What GIFT City Actually Is

GIFT City \u2014 Gujarat International Finance Tec-City \u2014 houses an International Financial Services Centre, or IFSC, a special zone designed to operate by global financial rules rather than India's ordinary domestic ones. Regulated by the International Financial Services Centres Authority, the IFSCA, it offers a deliberately progressive framework: transactions are conducted in foreign currency, primarily US dollars, and a suite of tax incentives is layered on to make it attractive against established offshore centres.

The strategic intent is unmistakable. India has long watched diaspora and global capital flow into hubs like Dubai and Singapore on its way to Indian assets, with India capturing little of the intermediation. GIFT City is the attempt to bring that activity onshore \u2014 to build a domestic gateway where NRIs can hold India-linked global investments, structure offshore vehicles and manage wealth in a tax-efficient, dollar-denominated environment without leaving the Indian regulatory perimeter.

## Why the Momentum Is Real Now

The timing is not accidental. Global wealth is on the move in 2026, and India is working hard to capture more of it. The same week analysts were debating GIFT City's rise, the broader machinery of Indian policy was visibly tilting toward pulling in foreign and diaspora money \u2014 the Reserve Bank absorbing hedging costs on NRI dollar deposits, easing investment limits for NRIs and OCIs in equities, and streamlining access to government securities. GIFT City is the structural centrepiece of that same campaign, the permanent address rather than a temporary incentive.

For NRIs specifically, the appeal is concrete. The centre allows the diaspora to invest in India-linked funds and global assets through a tax-efficient onshore route, to set up offshore investment structures under a clear regulatory regime, and to do so in dollars \u2014 sidestepping both the currency friction and the perception of regulatory opacity that have historically pushed NRI money toward Dubai's DIFC or Singapore.

## The Honest Caveats

Enthusiasm should not outrun reality. GIFT City today sits in what observers candidly call a transitional phase. The intent is strong and the regulatory framework under the IFSCA is genuinely progressive, but the ecosystem is still maturing: liquidity is building rather than built, participation is growing rather than deep, and the market depth that defines a top-tier global financial centre has not yet arrived.

The comparison that matters is competitive. Dubai's DIFC and Singapore are established hubs with decades of accumulated liquidity, talent and trust. GIFT City is asking the diaspora to back a rising challenger, not a finished product. For an NRI deciding where to route serious capital, that distinction is the whole question \u2014 the tax incentives may be more attractive, but the depth, the range of counterparties and the ease of exit may not yet match what Dubai or Singapore offer today.

## The Wider Backdrop

GIFT City's push also lands at a delicate moment for Indian markets. Aggregate foreign holdings in Indian equities have fallen to a 14-year low of around 14.7 per cent, even as domestic institutional holdings have climbed. The rupee has fallen about 6 per cent this year, hitting an all-time low near 97 to the dollar in May before the RBI intervened. India still trades at a near-40 per cent premium to the MSCI Emerging Markets index \u2014 a reflection of its earnings visibility and domestic-demand strength, but also a vulnerability when global investors turn cautious.

Against that mixed picture, GIFT City represents India's bet that structural reform, not just cyclical incentives, will keep diaspora and global capital engaged. The currency erosion that worries foreign investors is precisely the problem a dollar-denominated onshore centre is meant to neutralise.

## What It Means for the Diaspora

For globally mobile Indians, GIFT City is graduating from a headline to a genuine option worth understanding. An NRI weighing how to invest in India \u2014 through funds, offshore structures or India-linked global assets \u2014 now has a domestic, dollar-friendly, tax-advantaged gateway that did not credibly exist a few years ago.

The prudent posture is engaged but clear-eyed. The incentives are real and the regulatory direction is encouraging, which makes GIFT City worth evaluating seriously, especially for diaspora investors already routing money through Dubai or Singapore who may find a more tax-efficient path home. But it remains a hub on the rise, not at the summit, and the practical questions \u2014 liquidity, depth, ease of exit \u2014 deserve scrutiny before significant capital follows the headlines. India has built the on-ramp it long lacked. Whether it is wide enough yet for an individual NRI's money is a judgement still worth making case by case."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
print(f"\n{'='*60}\nSourcing images\n{'='*60}")
img_specs = {
    articles[0]["slug"]: (["human heart anatomy model", "cardiology heart medical", "medication pills tablets pharmacy"],
                          ["human heart medical anatomy", "prescription pills medication white"]),
    articles[1]["slug"]: (["senior exercise resistance band", "older adults fitness elderly", "elderly woman exercising home"],
                          ["older adults exercising resistance bands", "senior woman stretching exercise home"]),
    articles[2]["slug"]: (["GIFT City Gujarat skyline", "GIFT City towers Gandhinagar", "Gandhinagar financial district building"],
                          ["modern financial district skyscrapers skyline", "business towers city skyline glass"]),
}
img_captions = {
    articles[0]["slug"]: "A model of the human heart; an SGLT2 diabetes drug sharply cut heart-failure risk in carriers of cardiomyopathy genes",
    articles[1]["slug"]: "An older adult exercising with a resistance band, the kind of minimal strength work the FAST-2 trial tested",
    articles[2]["slug"]: "The skyline of GIFT City, India's International Financial Services Centre in Gujarat",
}
for art in articles:
    cq, pq = img_specs[art["slug"]]
    url, attribution = source_image(art["slug"], cq, pq)
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
