#!/usr/bin/env python3
"""Videshi lifestyle-health + markets-finance writer — 2026-06-20 02:00 UTC batch.
Topics:
  1. ENDO 2026 (Stanford): semaglutide linked to 15% lower bone-fracture risk in T2D vs other anti-obesity drugs — lifestyle-health
  2. ENDO 2026 (OPTION-VMS): first real-world study of non-hormone fezolinetant for menopause symptoms — lifestyle-health
  3. NRIs rushing to break old FCNR deposits to rebook at higher rates; banks seek RBI nod; ~$1bn at stake — markets-finance
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
        out = subprocess.run(["curl", "-sS", "-A", UA, "-o", "/tmp/_img_dl0620a.bin", url],
                             capture_output=True, timeout=40)
        if os.path.exists("/tmp/_img_dl0620a.bin"):
            with open("/tmp/_img_dl0620a.bin", "rb") as f:
                data = f.read()
            os.remove("/tmp/_img_dl0620a.bin")
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
# ARTICLE 1: Semaglutide lower bone-fracture risk (lifestyle-health)
# ============================================================
articles.append({
    "headline": "Ozempic's Active Ingredient May Quietly Be Protecting Bones, a Study of 60,000 Diabetics Finds",
    "subheadline": "Stanford researchers comparing semaglutide against other weight-loss drugs in people with type 2 diabetes found a 15 percent lower fracture risk \u2014 a reassuring twist for a community where diabetes is rampant and bones are already thinner.",
    "slug": "semaglutide-ozempic-15-percent-lower-bone-fracture-risk-type-2-diabetes-stanford-endo-2026-diaspora-20260620-0200",
    "category": "lifestyle-health",
    "vertical": "preventive-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Indians are among the most diabetes-prone people on earth and tend to have lower bone density than Western populations, so a finding that a wildly popular weight-loss drug many NRIs are already taking may also guard against fractures speaks directly to two health risks the diaspora carries at once.",
    "sources": json.dumps([
        {"name": "Endocrine Society \u2014 Semaglutide linked to lower bone fracture risk (ENDO 2026, Jairo More\u00f1a, Stanford)", "url": "https://www.endocrine.org/news-and-advocacy/news-room/2026/jairo-norena-press-release-endo-2026"},
        {"name": "ENDO 2026 \u2014 Endocrine Society Annual Meeting, Chicago (June 13-16, 2026)", "url": "https://www.endocrine.org/"}
    ]),
    "body": """The drugs that have reshaped how the world treats obesity and diabetes have carried a nagging worry: rapid weight loss can thin the bones and raise the risk of fractures. A large new analysis presented at the Endocrine Society's annual meeting offers a reassuring counterpoint \u2014 in people with type 2 diabetes, the medication behind Ozempic and Wegovy was linked to *fewer* broken bones, not more.

## What the Researchers Did

Scientists at Stanford University set out to answer a specific question: how does semaglutide \u2014 the most powerful of the current generation of weight-loss drugs \u2014 compare with other anti-obesity treatments when it comes to bone health? Earlier evidence had been unsettling. Rapid weight loss using GLP-1 receptor agonists, the class semaglutide belongs to, had been associated with thinner bones, while slower, more moderate weight loss seemed to preserve bone mass. But no one had directly pitted semaglutide against its rivals on fracture risk.

The team, led by Jairo More\u00f1a, then an endocrinology fellow at Stanford University Medical Center, ran a retrospective cohort analysis drawing on the Atropos Health Eos electronic-health-record dataset \u2014 a vast pool representing 161 million patients seen in U.S. community hospitals and academic medical centres between January 2016 and December 2023.

They focused on adults aged 18 and older with type 2 diabetes who had no history of prior fractures and were not on osteoporosis medication. One group received semaglutide (26,324 people); a comparison group received dulaglutide, phentermine-topiramate, or bupropion-naltrexone, with no prior semaglutide use (33,555 people).

## What They Found

The semaglutide group lost more weight \u2014 a greater reduction in body mass index than the comparison group. And crucially, they broke fewer bones. The semaglutide group recorded **794 fractures**, against **1,045** in the control group, which the researchers translated into roughly a **15 percent reduction in fracture risk**.

"Bone fractures are painful, expensive and can seriously affect quality of life \u2014 especially as people get older," More\u00f1a said. "We hope this study encourages monitoring of bone health in weight-loss programs."

He was careful not to oversell the result. The study is observational \u2014 it shows an association, not proof that semaglutide directly strengthens bones \u2014 and the authors recommend prospective trials to confirm the finding. "This work is an important early step toward understanding the impact of semaglutide-induced weight loss on bone health in patients with type 2 diabetes," More\u00f1a said.

## Why It Matters for the Diaspora

For people of Indian origin, this lands on two of the community's most pressing health fault lines at once.

The first is diabetes. South Asians are among the most diabetes-prone populations in the world, developing the disease earlier, at lower body weights, and at higher rates than most other groups. Type 2 diabetes is woven through countless NRI families, and GLP-1 drugs have become a common part of treatment for diabetes and obesity alike. A great many Indian-origin patients are already on semaglutide or a cousin of it.

The second is bone health. Indians tend to have lower bone mineral density than Western populations, compounded by widespread vitamin D deficiency \u2014 even in sunny climates, because of diet, skin pigmentation and limited sun exposure \u2014 and by diets that are often low in calcium. Osteoporosis and fragility fractures are a quiet, underdiagnosed problem in the community, particularly among post-menopausal women. A diabetes drug that does not appear to worsen \u2014 and may even improve \u2014 fracture risk is genuinely good news for a population already carrying thinner bones.

## What To Actually Do

The practical takeaways are measured, not dramatic. If you or a family member has type 2 diabetes and is taking or considering semaglutide, this evidence is reassuring rather than a reason to celebrate: it suggests the drug is unlikely to be undermining bone health, and may be helping. But it does not replace the basics of protecting bones \u2014 especially during any period of significant weight loss.

That means ensuring adequate calcium and vitamin D, both of which are commonly low in Indian diets and bodies; doing weight-bearing and resistance exercise, which builds and preserves bone and muscle; and, for older adults and post-menopausal women, asking a doctor about a bone-density scan. As More\u00f1a's own advice underscores, anyone on a serious weight-loss programme \u2014 drug-assisted or not \u2014 should have their bone health monitored. The headline is encouraging, but the foundations still matter."""
})

# ============================================================
# ARTICLE 2: Non-hormone menopause drug fezolinetant real-world study (lifestyle-health)
# ============================================================
articles.append({
    "headline": "A Non-Hormone Pill for Menopause Just Passed Its First Real-World Test \u2014 on Hot Flashes and Mood Alike",
    "subheadline": "In a study of 656 women, the FDA-approved drug fezolinetant eased hot flashes, night sweats, anxiety and depression within weeks \u2014 an option that matters for the many South Asian women who avoid or cannot take hormone therapy.",
    "slug": "fezolinetant-non-hormone-menopause-hot-flashes-mood-real-world-option-vms-study-endo-2026-diaspora-20260620-0200",
    "category": "lifestyle-health",
    "vertical": "womens-health",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "Menopause remains a taboo, under-treated subject in many Indian families, and cultural wariness about hormone therapy leaves countless diaspora women suffering in silence \u2014 so evidence that a non-hormonal pill measurably eases hot flashes, sleep loss and mood is exactly the kind of option that could reach women who would never consider hormones.",
    "sources": json.dumps([
        {"name": "Endocrine Society \u2014 Non-hormone medication addresses menopausal symptoms in women (ENDO 2026, OPTION-VMS, Pauline M. Maki)", "url": "https://www.endocrine.org/news-and-advocacy/news-room/2026/maki-press-release-endo-2026"},
        {"name": "ENDO 2026 \u2014 Endocrine Society Annual Meeting, Chicago (June 13-16, 2026)", "url": "https://www.endocrine.org/"}
    ]),
    "body": """Hot flashes are the symptom most people picture when they think of menopause \u2014 and for good reason: about 80 percent of women experience them. For decades the most effective relief has been hormone therapy, but many women either cannot take hormones or do not want to. A new real-world study presented at the Endocrine Society's annual meeting offers fresh evidence that a non-hormonal pill works \u2014 and not just on the flashes, but on the mood disturbances that often shadow them.

## What the Study Looked At

The research, called OPTION-VMS, is described as the first real-world study of FDA-approved non-hormone treatments for menopausal vasomotor symptoms \u2014 the medical term for hot flashes and night sweats. It was presented at ENDO 2026 in Chicago and led by Pauline M. Maki, professor of psychiatry, psychology and obstetrics and gynaecology at the University of Illinois Chicago College of Medicine.

"Hot flashes are a common and bothersome symptom of menopause experienced by about 80 percent of women. Both hormonal and non-hormonal treatments are available to women," Maki said. "This study, called OPTION-VMS, is the first real-world study of the effect of these medications on hot flashes, sleep and mood."

The analysis included 656 women aged 40 to 75 with bothersome menopausal vasomotor symptoms who were prescribed a non-hormone therapy \u2014 either fezolinetant, an SSRI or SNRI antidepressant, or other drugs such as gabapentin and oxybutynin. Researchers tracked changes in hot flashes from the start of treatment to 12 weeks, and changes in depression and anxiety at 4, 8 and 12 weeks.

## What They Found

Among the 201 women taking **fezolinetant**, hot flashes and night sweats improved significantly from before treatment through 4, 8 and 12 weeks. Just as striking, their **depressive and anxiety symptoms also improved \u2014 as early as four weeks** \u2014 and the gains held through the full 12 weeks.

The benefit on mood was not unique to fezolinetant. The 329 women on SSRIs or SNRIs and the 126 on other non-hormone treatments also saw their depression and anxiety scores fall from baseline through 12 weeks. But fezolinetant stands apart because it is purpose-built for menopause: it targets the brain pathway that triggers hot flashes directly, rather than borrowing an antidepressant for the job.

"These findings show that in the real world, fezolinetant shows benefits similar to what was seen in clinical trials," Maki said. "That's important because clinical trials generally have restrictive criteria for study enrollment. Study participants are generally healthier than the general population." In other words, the drug appears to work for ordinary women, not just the carefully screened volunteers of a trial.

"The demonstration that non-hormonal treatments are effective in the real world provides women with reassurance that there are solutions for women's menopause symptoms that work," Maki added.

## Why This Resonates in Diaspora Homes

In many Indian families, menopause remains something endured quietly rather than discussed, let alone treated. The hot flashes, broken sleep, irritability and low mood are often dismissed \u2014 by the women themselves as much as by those around them \u2014 as something to simply get through. Doctors are frequently not consulted, and when they are, hormone therapy is often met with deep cultural wariness, shaped by long-standing fears about hormones and cancer that linger well past what the current evidence supports.

That wariness leaves a large gap. A great many South Asian women who would never consider hormone therapy are suffering symptoms that are genuinely treatable. A non-hormonal, FDA-approved pill that measurably eases hot flashes and lifts mood is precisely the kind of option that can reach those women \u2014 it sidesteps the hormone objection entirely.

There is also a mental-health dimension that matters here. Anxiety and depression around menopause are real and often unspoken in a community where mental-health stigma runs high. A treatment that improves both the physical symptom and the mood within weeks addresses two burdens that are usually borne in silence.

## What To Actually Do

The message is not that every woman should ask for fezolinetant. It is that menopausal symptoms are treatable, and that hormones are no longer the only effective route. A woman struggling with hot flashes, disrupted sleep or low mood around menopause has options worth a frank conversation with a doctor \u2014 hormonal and non-hormonal alike. For those who have ruled out hormones, whether for medical reasons or personal preference, this study is a reminder that effective alternatives exist and are now backed by real-world evidence. The first step, in a community where the subject is too often avoided, is simply naming the problem and seeking care."""
})

# ============================================================
# ARTICLE 3: NRIs breaking old FCNR deposits to rebook at higher rates (markets-finance)
# ============================================================
articles.append({
    "headline": "NRIs Are Breaking Their Own Bank Deposits to Chase a Better Rate \u2014 and Banks Want the RBI's Blessing",
    "subheadline": "A new scheme pays NRIs up to 7.1 percent on dollar deposits, but only on fresh money. Those who locked in months ago at half that rate are now paying penalties to break and rebook \u2014 and lenders fear $1 billion could walk out the door.",
    "slug": "nris-break-fcnr-deposits-rebook-higher-rates-banks-seek-rbi-approval-1-billion-penalty-nri-investor-20260620-0200",
    "category": "markets-finance",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "diaspora_angle": "This is a pure diaspora money story: it is NRIs who hold these dollar deposits, NRIs being courted by the new higher rates, and NRIs now weighing whether to pay a penalty to break an old deposit and rebook \u2014 a decision facing anyone in the community who parked dollars in an Indian bank in the past year.",
    "sources": json.dumps([
        {"name": "Outlook Money \u2014 Banks Seek RBI Approval To Let NRIs Rebook Deposits At Higher Rates", "url": "https://www.outlookmoney.com/banking/banks-seek-rbi-approval-to-let-nris-rebook-deposits-at-higher-rates"},
        {"name": "Outlook Business \u2014 Why NRIs Are Rushing to Break Old Deposits and Reinvest at Higher Rates", "url": "https://www.outlookbusiness.com/"},
        {"name": "The Hindu BusinessLine \u2014 RBI temporarily withdraws interest rate ceiling on fresh FCNR(B) deposits of 3-5 yr tenor", "url": "https://www.thehindubusinessline.com/"}
    ]),
    "body": """A peculiar thing is happening in the world of NRI banking: people are paying penalties to break deposits they opened only months ago. The reason is a sweetened government scheme that has suddenly made yesterday's dollar deposits look like a bad deal \u2014 and it has set off a scramble that India's banks are now asking the Reserve Bank of India to help them manage.

## How We Got Here

To defend a weakening rupee, the RBI this month rolled out a package designed to pull dollars in from the Indian diaspora. The centrepiece is a concessional foreign-currency swap window, open until September 30, under which the central bank effectively absorbs the cost banks would normally pay to hedge currency risk on Foreign Currency Non-Resident (Bank), or FCNR(B), deposits. With that cost lifted, banks can pay depositors far more.

And they have. Interest rates on three- to five-year FCNR(B) dollar deposits have jumped to between **6 percent and 7.1 percent**, up from the 3.35 to 4 percent such deposits earned earlier. On June 17, the RBI went further, temporarily scrapping the interest-rate ceiling on these deposits and on NRE rupee deposits of three years and longer. For an NRI, the pitch is compelling: park dollars with an Indian bank, earn roughly 7 percent in dollars, and get every dollar back at maturity regardless of where the rupee goes.

## The Catch \u2014 and the Scramble

Here is the problem. The RBI's largesse applies only to **fresh** deposits and deposits that have already matured. Anyone holding an existing FCNR(B) deposit \u2014 booked before the scheme \u2014 continues to earn the lower rate they originally agreed to.

That has left a particular group of NRIs feeling stranded: those who opened deposits in the past two or three months, locking in around 3.5 to 4 percent just before rates nearly doubled. They are watching new depositors earn almost twice as much on identical money.

Many are not waiting. Bankers told *The Economic Times* that some large depositors have already begun prematurely closing their existing term deposits and moving the funds to other banks offering the higher rates under the new scheme. They are doing this despite real costs: under RBI rules, FCNR(B) deposits carry a mandatory one-year lock-in, no interest is paid on withdrawals before one year, and withdrawals after a year incur a penalty of one percentage point off the contracted rate. For depositors who have crossed the one-year mark, the maths still works \u2014 the jump to 7 percent more than offsets the penalty \u2014 so they are willing to take the hit.

## Why Banks Are Worried

For lenders, this churn is a headache. When a depositor breaks an FCNR(B) deposit and moves it to a rival bank, the original bank loses the money entirely. To stop the bleeding, banks have asked the RBI for permission to let existing depositors **break and rebook within the same bank** under the new scheme \u2014 keeping the customer, and the dollars, in house.

The stakes are concrete. Bankers estimate that nearly **$1 billion** of deposits could be withdrawn prematurely if the RBI does not allow in-house rebooking of deposits placed over the past three years. The eligible deposits under the special scheme must be in multiples of $1 million and carry a minimum one-year lock-in, and the RBI's swap facility covers only US dollar deposits, though banks may accept other currencies.

The RBI has not yet ruled on the request, leaving banks and depositors in limbo over whether the cleaner, penalty-free path will open.

## What It Means for NRIs

For overseas Indians, this is not abstract policy \u2014 it is a live decision. A few things follow.

First, **the new rates are genuinely attractive and time-limited**. The window for the enhanced scheme runs to September 30, and FCNR(B) deposits carry no rupee risk: dollars go in, dollars come out. For new money, the case is strong.

Second, **if you booked a deposit recently at the old rate, do the arithmetic before breaking it**. If your deposit has not completed one year, breaking it means forfeiting interest entirely \u2014 often a losing move. If it has crossed a year, the one-percentage-point penalty may well be worth swallowing to jump to 7 percent, but the calculation depends on your remaining tenor and exact rate.

Third, **wait and ask before acting hastily**. Banks are lobbying for a penalty-free, in-house rebooking option. If the RBI grants it, depositors may be able to upgrade without shifting banks or paying as much. It is worth asking your bank directly whether such an option is coming before you trigger a penalty.

The broader picture is a rare moment of leverage for the diaspora. India wants these dollars badly enough to pay up for them \u2014 and for once, the saver, not the bank, holds the better hand. The trick is to move deliberately, not in a panic."""
})

# ============================================================
# IMAGE SOURCING
# ============================================================
img_specs = {
    articles[0]["slug"]: (["semaglutide injection pen insulin", "diabetes blood glucose test", "human bone density skeleton x-ray"],
                          ["diabetes injection pen", "blood sugar test diabetes"], None),
    articles[1]["slug"]: (["menopause woman middle aged", "woman portrait older south asian", "medication pills tablets health"],
                          ["middle aged woman thoughtful", "woman health wellbeing"], None),
    articles[2]["slug"]: (["Indian rupee dollar currency notes", "bank building India finance", "US dollar banknotes money"],
                          ["us dollar indian rupee notes", "bank finance building"], None),
}
img_captions = {
    articles[0]["slug"]: "A semaglutide injection pen; a study of 60,000 diabetics linked the drug to 15% fewer fractures",
    articles[1]["slug"]: "A study of 656 women found the non-hormone drug fezolinetant eased hot flashes and mood within weeks",
    articles[2]["slug"]: "US and Indian currency; NRIs are breaking old dollar deposits to rebook at sharply higher rates",
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
