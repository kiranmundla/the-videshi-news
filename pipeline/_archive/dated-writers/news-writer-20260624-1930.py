#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (19:30 PDT run)
2 NEW articles, dedup-checked against last ~45 news articles:
  1. US student-visa "Duration of Status" rule clears White House review — DHS
     plan to replace open-ended F-1 stay with fixed admission periods (max 4 yrs,
     USCIS-approved extensions, 30-day grace). ~363,000 Indian students are the
     single largest affected group. Distinct from prior green-card/H-1B/citizenship-
     fee coverage; this is the STUDENT pipeline + OPT/CPT angle.
  2. Parsi gender-discrimination case at the Supreme Court — a Parsi-Zoroastrian
     woman who married a Hindu (and her minor son) challenge the 1908 Petit v.
     Jeejeebhoy precedent and Nagpur Panchayat Rule 5(2) that strip religious
     identity/temple access from women who marry out, while Parsi men keep theirs.
     Fresh human-interest / community-rights diaspora story, distinct from all
     recent migration/economy coverage.
"""
import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error: {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  \u2713 Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  \u26a0 Download failed ({r.status_code}): {url[:80]}")
            try:
                tmp = f"/tmp/{slug}_src"
                subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
                with open(tmp, "rb") as f:
                    content = f.read()
                if len(content) < 5000:
                    return None
                r_content = content
            except Exception:
                return None
        else:
            r_content = r.content
        ct = r.headers.get("Content-Type", "") if r.status_code == 200 else "image/jpeg"
        if "image" not in ct and len(r_content) < 5000:
            print(f"  \u26a0 Not an image or too small: {ct}, {len(r_content)} bytes")
            return None

        from PIL import Image
        img = Image.open(io.BytesIO(r_content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()

        if len(compressed) < 5000:
            print(f"  \u26a0 Compressed image too small: {len(compressed)} bytes")
            return None

        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"

        requests.delete(upload_url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY
        })

        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=30)

        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def pick_commons(queries, min_width=900):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            return pick["url"], pick.get("title", "")
    return None, ""


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# \u2500\u2500\u2500 Article 1: US student-visa Duration of Status rule \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: US student-visa Duration of Status rule")
    print("="*60)

    slug = "us-student-visa-duration-of-status-fixed-term-f1-opt-indian-students-dhs-rule-20260624"
    headline = "America Wants to Put an Expiry Date on the Student Visa. India's 363,000 Students Are First in Line."
    subheadline = "For decades an F-1 visa let you stay as long as you stayed enrolled. A rule that just cleared the White House would swap that for a fixed clock \u2014 and every extra year, every job after graduation, would need Washington's sign-off."

    body = """For as long as most Indian families can remember, the deal with an American student visa was simple: get admitted, stay enrolled, and you could remain in the United States for as long as your studies lasted. That arrangement, known in immigration law as "Duration of Status," is about to end.

The White House Office of Management and Budget has completed its review of a Department of Homeland Security proposal to scrap the open-ended framework and replace it with fixed admission periods \u2014 generally tied to a programme's length and capped at four years. Once the rule is published in the Federal Register, expected later this year, F-1 students, J-1 exchange visitors and certain media-visa holders would no longer be admitted for "as long as they comply." They would be admitted until a date. Stay past it, even to finish the same degree, and they would have to apply to U.S. Citizenship and Immigration Services for an extension.

## Why Indians Are the Most Exposed

No nationality has more at stake. Indian students are now the single largest international cohort in the United States, with 363,019 enrolled in the 2024-25 academic year, according to the Open Doors report. They are concentrated precisely in the multi-year master's and doctoral programmes \u2014 and the post-graduation work pathways \u2014 that the new clock would complicate most.

The change matters less for a tidy two-year master's that finishes on schedule and more for the messy reality of how degrees actually unfold: a PhD that runs six or seven years, a thesis that slips a semester, a switch of advisor or department, a master's that rolls into a doctorate. Under the current system, a university's international-student office could absorb most of that internally. Under the proposed one, each deviation could mean a formal USCIS extension application \u2014 with fees, biometrics, paperwork and the processing delays that have become a defining feature of the American immigration system.

## The OPT Question

The sharper anxiety is about what happens after the gown comes off. Optional Practical Training (OPT) and its STEM extension let international graduates work in the United States for up to three years after a degree \u2014 for most Indian students, the bridge between a classroom and an H-1B, and the entire financial logic of borrowing tens of lakhs of rupees for an American education in the first place. Curricular Practical Training (CPT) does the same during a course.

Immigration specialists warn that folding these into a fixed-term, USCIS-gated framework removes the flexibility students have relied on. "The duration-of-status rule that has been proposed is going to fundamentally change the flexibility that students have had to apply for Optional Practical Training and Curricular Practical Training," Danielle Goldman, co-founder and chief executive of the immigration platform Build, told reporters. The proposal also trims the grace period after a programme ends from 60 days to 30 \u2014 halving the window a graduate has to leave, find further study, or change status.

## What's Still Uncertain

The rule is not yet law. DHS first floated the idea in August 2025 and formally proposed eliminating Duration of Status for F-1 visas in May 2026; the OMB clearance is a procedural milestone, not the finish line. It must still be published, and could face the same kind of legal challenge that recently felled the administration's separate attempt to impose a $100,000 H-1B fee, which a federal judge struck down as unlawful. Europe's student-sending countries are watching too, but none has India's exposure.

## Why It Matters for the Diaspora

For Indian parents, the calculation around an American degree has always balanced a very large cost against a fairly reliable path: study, work on OPT, move to an H-1B, and perhaps one day a green card. Each link in that chain has been tightened in the past year \u2014 the citizenship-fee hike, the green-card filing changes, the H-1B fee fight \u2014 and the student visa was the one part that still ran on autopilot. Putting a clock on it changes the risk profile of the whole journey.

It will not stop Indian students from coming; America's universities and labour market remain too magnetic for that. But it adds a layer of bureaucratic fragility to a plan that families bet their savings on, and it strengthens the pitch already being made by the United Kingdom, Canada, Germany and a newly aggressive France, all of which have spent the past year simplifying \u2014 not complicating \u2014 the lives of Indian students. The message Indian families will take from this is the one they have been hearing all year: the American door is still open, but the hinges are getting stiffer."""

    img_url, _ = pick_commons([
        "University campus students United States",
        "American university campus students walking",
        "College campus students United States"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Students on a US university campus; Indians are now the largest international student group in America, with over 363,000 enrolled in 2024-25"

    if not img_url:
        px = fetch_pexels_image("university students campus walking")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Indian students are the largest international cohort in US universities and the group most exposed to the proposed visa change"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Outlook Business (outlookbusiness.com, June 2026) \u2014 'US Clears Visa Rule Change, Foreign Students May Face Stay Limits, Here's What It Means For Indians': the White House Office of Management and Budget completed its review of a DHS proposal to replace the current student-visa system with fixed admission periods; if implemented, F-1 visa holders could receive fixed stay periods instead of flexible 'duration of status' and may need additional approval to stay longer; the proposal could affect nearly 3.6 lakh Indian students and is expected to be published in the Federal Register before taking effect later this year.",
            "Outlook Money (outlookmoney.com, June 22, 2026) \u2014 'US Visa Proposal May Limit Stay Duration For Foreign Students; Here's How It Impacts Indians': DHS has proposed replacing the duration-of-status framework with fixed admission periods for F, J and certain I visa holders; Indian students, at 363,019 in 2024-25 per the Open Doors report, are the largest international student community and among the most affected; the proposal reduces the post-completion grace period from 60 days to 30 days and adds requirements for students who transfer institutions or change programmes; DHS first proposed the changes in August 2025 and the White House review is now complete.",
            "The Indian Eye (theindianeye.com, June 2026) \u2014 'Tighter student visa rules may impact Indians in US: Expert': on May 5, 2026 DHS proposed eliminating the 'Duration of Status' framework for F-1 visas, replacing it with a fixed admission period of up to four years, with any extension (including continued study or post-graduation work authorisation) requiring USCIS approval; Danielle Goldman, co-founder and CEO of Build, said the move 'is going to fundamentally change the flexibility that students have had to apply for Optional Practical Training and Curricular Practical Training' (OPT/CPT).",
            "Curly Tales (curlytales.com, June 24, 2026) \u2014 'US Student Visas To Have Expiry Date? What This Means For Indians': under the current duration-of-status framework students may remain as long as they are enrolled and can extend studies or transfer universities without a fresh admission period; the new rule would end this and impose a fixed period of stay, likely requiring visa extensions with additional documentation, biometrics, more scrutiny and processing delays; the rule has not been finalised and awaits enforcement."
        ]),
        "diaspora_angle": "Indian students are the largest international cohort in the United States, and putting a fixed clock on the F-1 visa \u2014 with USCIS sign-off needed for extensions and OPT work after graduation \u2014 injects fresh bureaucratic risk into the study-work-H-1B-green-card path that NRI families stake their savings on.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: Parsi gender-discrimination Supreme Court case \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Parsi gender-discrimination Supreme Court case")
    print("="*60)

    slug = "parsi-women-interfaith-marriage-supreme-court-1908-petit-jeejeebhoy-nagpur-panchayat-discrimination-20260624"
    headline = "She Was Born a Parsi and Never Left Her Faith. Because She Married a Hindu, Her Son Can't Set Foot in the Temple."
    subheadline = "A 1908 ruling decided that only Parsi men could pass on the religion. More than a century later, a mother and her young son are asking India's Supreme Court to undo it \u2014 a case that goes to the heart of who gets to belong to one of the world's smallest, oldest communities."

    body = """The boy is twelve. He plays video games, frets about a French exam, and has been raised, his parents say, entirely within the Zoroastrian faith \u2014 photographs from his Navjote, the religious initiation, show him in the traditional white dagli and coat. What he does not know is that the same community that watched him grow up will not fully claim him. His mother is a Parsi. His father is not. And by a rule more than a century old, that single fact places him outside the gates.

His case, brought before the Supreme Court of India by the boy through his mother, is the latest and most pointed challenge to one of the most quietly painful fault lines in Indian community life: the rule that a Parsi-Zoroastrian woman who marries outside the faith forfeits her religious identity \u2014 and that of her children \u2014 while a Parsi man who does exactly the same keeps his, and passes it on.

## A Rule Older Than Most Republics

The legal architecture dates to 1908. After Suzanne Bri\u00e8re, a French woman who converted to Zoroastrianism upon marrying into the Tata family, sought to be laid to rest in Bombay's Tower of Silence, orthodox hardliners objected. The case reached the Bombay High Court, in Dinshaw M. Petit v. Sir Jamsetjee Jejeebhoy, and the judges defined the community in strictly patriarchal terms: only Parsi men could transmit religious identity, regardless of whom they married. Converts, and the children of Parsi mothers with non-Parsi fathers, were shut out. Bri\u00e8re lost; she is buried in Paris, a continent from the resting place she is said to have wanted.

That judgment still governs day-to-day practice. Children of a Parsi woman who marries out can be barred from initiation, from entering the fire temple, and from Parsi-only welfare, housing and education programmes. Many progressive priests and community members reject the rule and quietly defy it. But it remains the default, enforced unevenly across the country's anjumans and panchayats.

## What the Court Is Now Weighing

The current matter has two fronts. One is a direct constitutional challenge to the continued reliance on the 1908 Petit precedent. Senior advocates have not minced words: Percival Billimoria called the old ruling "blatantly discriminatory to women" and "downright racist," and "a blot on the fair name of an otherwise industrious and loved community," telling the court it was astonishing such a rule still operated in modern constitutional India. The asymmetry, lawyers argue, treats "Parsi" not as a religion anyone can practise but as a racial lineage that only men can carry.

The second front is more immediate and human. In a related plea, the Supreme Court has asked the Nagpur Parsi Panchayat whether a woman who married a non-Parsi can be permitted to pray at the city's agiary. Senior advocate Shyam Divan argued that his client was born to Parsi parents, raised in the faith, never renounced it, and married a Hindu man under the Special Marriage Act \u2014 a law enacted precisely to allow interfaith marriage without conversion. He noted that Nagpur has only one fire temple and the nearest alternative is in Indore, some 400 kilometres away, and that similar women are already permitted to pray in Mumbai, Delhi, Kolkata and Pune. He challenged Rule 5(2) of the Nagpur Panchayat's constitution, which holds that a Parsi woman who marries a non-Parsi man, and her children, will not be accepted as Parsi Zoroastrians.

The bench has signalled sympathy. Hearing the broader Sabarimala reference, which folds in seven large questions on religious freedom, Justice B.V. Nagarathna observed that "the right of conscience under Article 25(1) is a right by birth and cannot be taken away by marriage," and that using marriage as a basis of classification "is discriminatory against women." If children of a Parsi father inherit the faith by birth, she reasoned, the same should hold for the children of a Parsi mother.

## Why It Matters for the Diaspora

The Parsis are among the world's smallest religious communities \u2014 a few tens of thousands in India, and dwindling \u2014 and that scarcity is exactly why the question cuts so deep. A community shrinking each generation cannot easily afford to turn away its own daughters and grandchildren, yet the orthodox case rests on guarding precisely that boundary. For the global Zoroastrian diaspora, scattered across North America, Britain, Australia and the Gulf, where interfaith marriage is even more common than in India, the outcome is existential. Many overseas associations have already moved, formally or informally, to include the children of Parsi women; a ruling from India's top court would give that inclusion a constitutional spine \u2014 or, if it goes the other way, harden a divide that already splits families across continents.

For a diaspora that loves to tell the story of how its ancestors arrived in India as refugees and promised to dissolve into it like sugar in milk, the case poses an uncomfortable mirror: what is left of a promise of belonging when the community leaves its own women, and their children, standing outside the gate?"""

    img_url, _ = pick_commons([
        "Fire Temple Zoroastrian India",
        "Parsi Zoroastrian temple",
        "Tower of Silence Mumbai",
        "Zoroastrian Faravahar symbol"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "A Parsi (Zoroastrian) fire temple in India; a Supreme Court case challenges rules that bar the children of Parsi women who marry outside the faith"

    if not img_url:
        px = fetch_pexels_image("temple india heritage architecture")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A Supreme Court case challenges century-old rules excluding the children of Parsi women who marry outside the community"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "CNN (cnn.com, June 2026) \u2014 'A century-old rule shuts my daughter out of her own community. A court case could change that': first-person account explaining that the legal boundaries of who qualifies as a Parsi stem from a landmark 1908 Bombay High Court case involving French national Suzanne Bri\u00e8re, who converted to Zoroastrianism after marrying into the Tata family; when she sought burial in Bombay's Tower of Silence, orthodox hardliners objected and the court defined the community in patriarchal terms \u2014 only Parsi men could pass on religious identity; the judgment bars children of Parsi women who marry outside the faith from initiation, places of worship, and Parsi-only welfare, housing and education programmes; Bri\u00e8re is buried in P\u00e8re Lachaise Cemetery in Paris.",
            "LiveLaw (livelaw.in, 2026) \u2014 'Supreme Court Asks Nagpur Parsi Panchayat If Woman Who Married Outside Community Can Be Permitted To Offer Prayers At Aghyari': the Court heard a plea challenging Rule 5(2) of the Nagpur Parsi Panchayat constitution, which holds that a Parsi or Irani Zoroastrian woman who marries a non-Parsi man and bears children will not be accepted as Parsi, along with her children; Senior Advocate Shyam Divan argued the petitioner was born to Parsi parents, raised in the faith, never renounced it, and married a Hindu man under the Special Marriage Act; he noted Nagpur has only one Agiary and the nearest alternative is in Indore (~400 km away), and that similar arrangements already exist for women in Mumbai, Delhi, Kolkata and Pune.",
            "Bar and Bench (barandbench.com, 2026) \u2014 'Excommunication of Parsi women who marry non-Parsis appears discriminatory: Supreme Court in Sabarimala case': a nine-judge bench led by CJI Surya Kant, hearing the Sabarimala reference, orally observed that excommunicating Parsi Zoroastrian women for interfaith marriages is discriminatory; Justice B.V. Nagarathna observed that 'the right of conscience under Article 25(1) is a right by birth and cannot be taken away by marriage' and that marriage as a basis of classification is discriminatory against women; Senior Advocate Darius Khambata argued for a Parsi woman who married a Hindu man and faced exclusion.",
            "LawBeat (lawbeat.in, 2026) \u2014 'SC Hears Plea Challenging 1908 Dinshaw Ruling on Parsi Identity': a writ petition under Article 32, filed by a minor child through his mother (a Parsi-Zoroastrian woman married to a non-Parsi man), challenges continued reliance on the 1908 Dinshaw M. Petit v. Sir Jamsetjee Jejeebhoy decision treated as determinative of 'who is a Parsi'; Senior Advocate Percival Billimoria called the 1908 judgment 'blatantly discriminatory to women' and 'downright racist' and 'a blot on the fair name of an otherwise industrious and loved community'; he noted children of a Parsi man married to a non-Parsi woman are treated as Parsis, while children of a Parsi woman married to a non-Parsi man are not, an asymmetry grounded in racial lineage rather than theology."
        ]),
        "diaspora_angle": "Interfaith marriage is even more common in the global Zoroastrian diaspora than in India, so a Supreme Court ruling on whether the children of Parsi women belong to the faith would either give overseas communities' growing inclusion a constitutional foundation or harden a divide already splitting Parsi families across continents.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    print("\n" + "="*60)
    print(f"DONE. Inserted IDs: {[i for i in ids if i]}")
    print("="*60)
