#!/usr/bin/env python3
"""
Videshi News Writer — June 25, 2026 (00:30 UTC run)
2 NEW articles, dedup-checked against last ~45 news articles:
  1. ~300 Indian and Bangladeshi migrant workers in Singapore left unpaid after
     KPA Engineering and SK Industries shuttered; 100+ turned up at MOM's
     Bendemeer services centre June 22; MOM/TADM investigating, Migrant Workers'
     Centre engaged 300+ with food/transport. Fresh diaspora migrant-safety
     story, distinct from Gulf wages, remittances, student visas, UAE consular.
  2. Padma Awards 2026 second investiture (June 23): two Indian-American
     physicians honoured — Dr Dattatreyudu Nori (Padma Bhushan, radiation
     oncology, Weill Cornell) and Prof. Prateek Sharma (Padma Shri,
     gastroenterology, University of Kansas). Distinct diaspora-achievement /
     medicine angle; prior Padma coverage was all cinema/arts figures.
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


# \u2500\u2500\u2500 Article 1: Singapore unpaid migrant workers \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Singapore unpaid Indian/Bangladeshi migrant workers")
    print("="*60)

    slug = "singapore-migrant-workers-unpaid-kpa-engineering-sk-industries-mom-tadm-india-bangladesh-20260625"
    headline = "Two Firms Shut, 300 Workers Unpaid: Indians and Bangladeshis Turn Up at Singapore's Manpower Ministry"
    subheadline = "Most are owed two months' wages, some as much as $7,000. When their bosses went silent and the worksite was locked, more than a hundred showed up at the ministry's door \u2014 a rare public stand in a city that runs on migrant labour."

    body = """On the morning of June 22, more than a hundred men gathered outside the Ministry of Manpower's services centre in Bendemeer, in northern Singapore. Most were from India and Bangladesh. They had come not to apply for anything, but because they did not know where else to go: the companies that employed them had shut down, their bosses had stopped answering the phone, and many had not been paid in two months.

By the ministry's own account, the two firms at the centre of the case are KPA Engineering, which provided air-conditioning and mechanical-ventilation services, and a related company, SK Industries. The Migrant Workers' Centre (MWC), the welfare arm of Singapore's national trade union body, said it had since engaged more than 300 affected workers from the two companies \u2014 a number that makes this one of the larger wage-default episodes the city-state has seen in recent years.

## "We Trusted Our Boss"

The accounts the workers gave were strikingly consistent. Dinesh, a 36-year-old supervisor at KPA Engineering, said he was owed almost $7,000 in salary unpaid since April. He had worked for the company for eleven years. Asked why he had not raised the alarm sooner, he gave an answer that explains how these situations build quietly before they break: "We trusted our boss. Our salary was delayed before, but it was eventually settled. We thought it would be the same this time. Now our bosses are gone, and we don't know what is going to happen."

Another worker, who gave his name only as Sampath, said several men had gone without pay for two months despite repeatedly raising it. The first hard sign of collapse came when they could not reach their employers over the weekend for the coming week's work schedule. Some then found their worksite at Tagore Lane locked. The workers' monthly salaries, the union said, ranged from roughly $600 to $1,300 \u2014 modest sums against which recruitment debts and remittances home are balanced, leaving almost no cushion when pay stops.

## What the Authorities Are Doing

Ng Hwei Min, general manager of the Tripartite Alliance for Dispute Management (TADM), the body that mediates employment disputes, said the ministry is investigating the claims and reaching out to the employers. Crucially, officials are allowing the affected workers to change employers so they can find new jobs while their cases are resolved \u2014 a provision that lets them stay in Singapore and keep earning rather than being sent home with nothing. "MOM will take the necessary and appropriate enforcement action against the companies should they be found to have breached any of the employment laws," Ng said.

The Migrant Workers' Centre moved on the practical emergencies first. Michael Lim, director of the NTUC's migrant workers segment, said many of the men had little or no money for food or transport when the centre met them at the ministry. MWC arranged meals and transport, offered advice on filing salary claims through TADM, and said temporary shelter would be provided to anyone who needed it.

## Why It Matters for the Diaspora

Public demonstrations by migrant workers are uncommon in Singapore, and that is precisely what made this one register. The city-state relies on more than a million work-permit holders across construction, marine, manufacturing and maintenance \u2014 the very sectors that Indians and Bangladeshis dominate. Wage disputes are among the most common grievances these workers face, and the protections on paper are real: valid claimants can stay in the country and seek new work while their cases proceed. But this episode exposes the gap between protection and prevention. By the time the system engaged, three hundred men had already gone unpaid for two months.

For the Indian diaspora, the story is a reminder that migration's most vulnerable layer is not the engineer on a work visa in Silicon Valley but the air-conditioning technician in Bendemeer, whose entire financial life rests on an employer who can simply switch off the phone. India and Bangladesh together supply a vast share of the Gulf's and Southeast Asia's blue-collar workforce, and cases like this one feed directly into a live policy debate about how origin countries protect their workers abroad \u2014 from pre-departure contracts to embassy welfare funds. What happens next in Singapore \u2014 whether the workers recover their wages, and how hard the enforcement bites \u2014 will be watched well beyond the two shuttered firms at the centre of it.
"""

    img_url, _ = pick_commons([
        "Migrant workers Singapore construction",
        "Foreign workers Singapore dormitory",
        "Construction workers Singapore",
        "Ministry of Manpower Singapore building"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Migrant workers in Singapore, where more than 300 Indian and Bangladeshi employees of two shuttered firms were left unpaid"

    if not img_url:
        px = fetch_pexels_image("construction workers site asia")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "More than 300 migrant workers from India and Bangladesh were left unpaid after two Singapore firms shut down"

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
            "The Straits Times / STOMP (stomp.sg, June 23, 2026) \u2014 'Over 100 migrant workers turn up at MOM office claiming unpaid wages; ministry probing 2 firms': more than 100 migrant workers, primarily from India and Bangladesh, turned up at a Ministry of Manpower office on June 22 over claims they are owed wages by a now-shuttered company; workers said they are employed by KPA Engineering (air-conditioner maintenance) or SK Industries; TADM general manager Ng Hwei Min said the ministry will investigate and is assisting workers and reaching out to employers; NTUC's Michael Lim said the Migrant Workers' Centre had met more than 300 affected workers; worker 'Sampath' from India said several had gone unpaid for two months.",
            "NTUC / Migrant Workers' Centre (ntuc.org.sg, June 2026) \u2014 'MWC provides help to migrant workers over alleged unpaid salaries at KPA Engineering and SK Industries': on 22 June 2026 more than 100 migrant workers of the two firms sought help at MOM's Bendemeer Services Centre; 36-year-old KPA Engineering supervisor Dinesh said he is owed almost $7,000 unpaid since April after 11 years with the company ('We trusted our boss... Now our bosses are gone'); most workers earn between $600 and $1,300 per month; MWC provided food and transport assistance and offered temporary shelter.",
            "Human Resources Director (hcamag.com, June 2026) \u2014 'MOM probes 2 firms after 100-plus migrant workers claim unpaid wages': MOM is investigating KPA Engineering and SK Industries after workers showed up over unpaid wages and housing concerns; TADM's Ng Hwei Min said workers are being allowed to change employers while the situation is addressed, and that 'MOM will take the necessary and appropriate enforcement action against the companies should they be found to have breached any of the employment laws'; MWC engaged more than 300 affected workers, many with little money for food or transport.",
            "Channel NewsAsia (CNA, June 2026) \u2014 'Over 100 migrant workers seek help over wages, housing; MOM probes 2 firms': the Ministry of Manpower is investigating KPA Engineering and SK Industries after more than 100 migrant workers showed up at the ministry's Bendemeer services centre on June 22 seeking help for unpaid salaries and housing arrangements; authorities said they will assist affected workers and take 'necessary and appropriate enforcement action' if the firms are found to have breached employment laws."
        ]),
        "diaspora_angle": "India and Bangladesh supply much of Singapore's blue-collar workforce, and the unpaid air-conditioning technicians of KPA Engineering and SK Industries are a reminder that migration's most exposed layer feeds directly into the live debate over how origin countries protect their lowest-paid workers abroad.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: Padma Awards 2026 honour two Indian-American doctors \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Padma Awards honour Indian-American doctors Nori & Sharma")
    print("="*60)

    slug = "padma-awards-2026-indian-american-doctors-dattatreyudu-nori-prateek-sharma-medicine-diaspora-20260625"
    headline = "Two Indian-American Doctors Just Got One of India's Highest Honours. Both Spent Their Careers Fighting Cancer."
    subheadline = "At the second Padma investiture in New Delhi, a radiation oncologist from New York and a gastroenterologist from Kansas were honoured \u2014 a quiet reminder that the diaspora India celebrates is not only its CEOs and chess prodigies, but its physicians."

    body = """When President Droupadi Murmu conferred the Padma Awards at Rashtrapati Bhavan on June 23, the headlines went, as they usually do, to the film stars and cricketers in the hall. But among the 65 honourees at the second civil investiture of the year were two names that will mean far more to a hospital ward than a movie set: Dr Dattatreyudu Nori, awarded the Padma Bhushan, and Professor Prateek Sharma, awarded the Padma Shri. Both are Indian-American physicians. Both have spent their lives on cancer.

The Padma Awards \u2014 the Padma Vibhushan, Padma Bhushan and Padma Shri, in descending order \u2014 are among India's highest civilian honours, announced each year on Republic Day and presented at ceremonial functions in the months that follow. The 2026 list, approved by the President, ran to well over a hundred names. Notably, it included four foreign nationals, two of them Americans \u2014 and both of those Americans are doctors of Indian origin.

## The Brachytherapy Pioneer

Dr Dattatreyudu Nori's story is the kind the diaspora tells about itself. Born in 1947 in Mantada, a village in Krishna district of what is now Andhra Pradesh, he studied at Kurnool Medical College and Osmania Medical College before building a career in the United States that would make him one of the most recognised radiation oncologists in the world. For decades he was a fixture at Memorial Sloan Kettering Cancer Center and then at NewYork-Presbyterian / Weill Cornell Medical Center, where he served as professor and executive vice-chairman of radiation oncology.

His signature contribution is in high-dose-rate brachytherapy \u2014 a technique that delivers radiation with precision directly to a tumour while sparing healthy tissue, and which he helped introduce and refine for cancers of the cervix, prostate, lung, and head and neck. Since the 1970s it has become a globally accepted standard of care. The New England Journal of Medicine once called him "a recognized leader in his specialty"; the United States gave him the Ellis Island Medal of Honor. He has also worked to seed cancer care back home and across the developing world, helping establish institutions including a cancer institute for women and children in Hyderabad and advising the UN's International Atomic Energy Agency on treatment guidelines. This is not, in fact, his first Padma \u2014 he received the Padma Shri in 2015. The Padma Bhushan, a higher honour, recognises a body of work that has now spanned more than four decades.

## The Man Who Spent a Career on One Disease

Professor Prateek Sharma's recognition is narrower in focus and no less deep. Born in Chandigarh and trained at M.S. University of Baroda before completing his residency and fellowship in the United States, he is now a professor of medicine at the University of Kansas School of Medicine and a past president of the American Society for Gastrointestinal Endoscopy. He has devoted essentially his entire career to a single condition: Barrett's esophagus, the change in the lining of the food pipe caused by long-standing acid reflux that can be a precursor to esophageal cancer.

It is an unglamorous specialism with enormous stakes. Acid reflux affects roughly one in seven adults; a fraction of those go on to develop Barrett's, and esophageal adenocarcinoma \u2014 the cancer it can lead to \u2014 has been rising for decades and still carries grim survival odds compared with breast or colon cancer. Sharma has authored more than 350 papers on the subject, pioneered imaging and endoscopic techniques to catch the disease earlier, and now chairs his society's artificial-intelligence institute, working on tools to help endoscopists spot what the human eye misses. His Padma Shri is, in effect, India honouring a quiet, decades-long campaign against a cancer most people have never heard of.

## Why It Matters for the Diaspora

There is a familiar shorthand for Indian-American success \u2014 the tech CEO, the spelling-bee champion, the Silicon Valley founder. The Padma list this year quietly widens that frame. Indian-origin physicians are one of the most consequential and least celebrated parts of the diaspora: by some counts, doctors of Indian origin make up around one in ten physicians in the United States, and the American Association of Physicians of Indian Origin is among the largest ethnic medical bodies in the country. Honouring Nori and Sharma is India claiming a share of that legacy \u2014 acknowledging that the talent it exported has, in turn, advanced care for patients on every continent, including its own.

For NRIs in medicine, the recognition lands as something more personal than a press release. It says the long, unflashy work \u2014 the clinical trials, the 350th paper, the residents trained who went on to chair their own departments \u2014 is seen and valued back home. The film stars will always get the louder applause. But on June 23, two doctors who spent their lives shrinking tumours stood in Rashtrapati Bhavan and were counted among the nation's finest. For a community that produces physicians the way some countries produce athletes, that recognition was overdue.
"""

    img_url = fetch_wikipedia_person_image("Dattatreyudu Nori")
    img_attribution = "Wikimedia Commons"
    img_caption = "Dr Dattatreyudu Nori, the Indian-American radiation oncologist awarded the Padma Bhushan in 2026 for his pioneering work in cancer treatment"

    if not img_url:
        img_url = fetch_wikipedia_person_image("Prateek Sharma (gastroenterologist)")
        img_caption = "Professor Prateek Sharma, the University of Kansas gastroenterologist awarded the Padma Shri in 2026 for his work on esophageal cancer"

    if not img_url:
        img_url, _ = pick_commons([
            "Rashtrapati Bhavan New Delhi",
            "Padma Award ceremony Rashtrapati Bhavan",
            "Droupadi Murmu"
        ])
        img_caption = "President Droupadi Murmu conferred the 2026 Padma Awards at Rashtrapati Bhavan, honouring two Indian-American physicians among the recipients"

    if not img_url:
        px = fetch_pexels_image("doctor hospital oncology medicine")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Two Indian-American cancer specialists were among the recipients of India's 2026 Padma Awards"

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
            "Nation Press (nationpress.com, June 2026) \u2014 'Padma Awards 2026: President Murmu to honour 65 awardees today at Rashtrapati Bhawan': the 2026 list includes four foreign nationals \u2014 two Americans, one Russian, one Georgian; Dr Dattatreyudu Nori (US) receives the Padma Bhushan for Medicine and Professor Prateek Sharma (US) the Padma Shri in the same field; the June 23 ceremony, the second civil investiture of the cycle, conferred 65 awards and was attended by PM Narendra Modi, Home Minister Amit Shah and Vice-President C.P. Radhakrishnan; an earlier ceremony on 25 May 2026 had conferred 65 awards.",
            "Dainik Bhaskar English (bhaskarenglish.in, June 23, 2026) \u2014 'Padma Awards 2026: President Murmu Confers 65; 2 Padma Vibhushan': live coverage of the June 23 investiture at which President Droupadi Murmu conferred the Padma Awards, noting 'Indian-American radiation oncologist Dr Dattatreyudu Nori conferred Padma Bhushan award' among the honourees, alongside recipients across arts, science, sport and social service.",
            "IANS (ianslive.in, 2026) \u2014 'Dr Nori Dattatreyudu conferred Padma Bhushan for pioneering contribution to cancer treatment': the radiation oncologist was awarded the Padma Bhushan for outstanding contribution to medicine; he served as principal investigator on numerous US National Cancer Institute clinical trials and is noted for pioneering high-dose-rate and remote after-loading brachytherapy, a globally accepted standard since the 1970s that delivers targeted radiation while minimising damage to healthy tissue; for 2026 the President approved 131 Padma Awards (5 Padma Vibhushan, 13 Padma Bhushan, 113 Padma Shri).",
            "Wikipedia (en.wikipedia.org) \u2014 'Dattatreyudu Nori' and 'Prateek Sharma (gastroenterologist)': Nori, born 1947 in Mantada, Andhra Pradesh, trained at Kurnool and Osmania Medical Colleges, is a professor at NewYork-Presbyterian/Weill Cornell, received the Padma Shri (2015) and Padma Bhushan (2026), and holds the Ellis Island Medal of Honor. Sharma, born in Chandigarh, MBBS from M.S. University of Baroda (1991), is a professor of medicine at the University of Kansas School of Medicine, president of the American Society for Gastrointestinal Endoscopy and chair of its AI Institute, known for work on Barrett's esophagus, GERD and esophageal cancer, with the Padma Shri awarded in 2026.",
            "The University of Kansas Cancer Center (kucancercenter.org, 2026) \u2014 'Understanding Barrett's Esophagus': profiles Prateek Sharma, MD, who has 'dedicated his entire career' to Barrett's esophagus; acid reflux affects roughly 15% of adults, about one in ten with long-standing reflux progress to Barrett's, and esophageal adenocarcinoma now comprises about 80% of esophageal cancer cases (up from 20% decades ago); Sharma has authored more than 350 papers on the condition."
        ]),
        "diaspora_angle": "Indian-origin physicians make up roughly one in ten doctors in the United States, and honouring radiation oncologist Dattatreyudu Nori and gastroenterologist Prateek Sharma is India claiming a share of a diaspora legacy that is usually defined by tech CEOs \u2014 telling NRI doctors that decades of unflashy clinical work are seen and valued back home.",
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
