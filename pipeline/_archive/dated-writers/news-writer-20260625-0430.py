#!/usr/bin/env python3
"""
Videshi News Writer — June 25, 2026 (04:30 UTC run)
2 NEW articles, dedup-checked against last ~40 news articles:
  1. DHS/ICE opens a first-of-its-kind front: fining IMMIGRATION ATTORNEYS for
     filing fraudulent asylum claims. First target = attorney Vinod Doddamani,
     fined $255k+ over 64 allegedly fraudulent documents filed mostly on behalf
     of INDIAN nationals (near-identical persecution declarations). Fresh
     diaspora immigration-enforcement story; distinct from green-card, H-1B fee,
     student-visa, deportation pieces already published.
  2. International Day of Yoga 2026 (June 21): 12th IDY, theme "Yoga for Healthy
     Ageing," 35,000 at Kolkata's Red Road led by Modi, plus 210+ Indian
     missions at ~2,500 venues worldwide — Times Square, Lincoln Memorial,
     Shanghai's Bund, Toronto, Birmingham, UN HQ, WHO Geneva. Positive
     diaspora-soft-power/culture story; nothing on Yoga Day in recent run.
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


# \u2500\u2500\u2500 Article 1: DHS fines immigration attorneys over Indian asylum claims \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: DHS fines immigration attorneys, Indian asylum claims")
    print("="*60)

    slug = "dhs-ice-fines-immigration-attorneys-fraudulent-asylum-claims-indian-nationals-doddamani-20260625"
    headline = "Washington Has a New Target in Its Immigration Crackdown: the Lawyers. The First Big Fine Involves Indian Asylum Claims."
    subheadline = "DHS says it has fined a single attorney more than $255,000 over 64 asylum documents filed mostly for Indian nationals \u2014 declarations it calls near-identical. For a community where word-of-mouth lawyers are how many navigate the system, the message lands close to home."

    body = """The Trump administration has opened a new front in its long campaign against immigration fraud, and for the first time the people in its sights are not the migrants but the attorneys who represent them. The Department of Homeland Security said this week it has begun fining lawyers directly for filing fraudulent asylum claims \u2014 and the first major case it has publicised centres on applications filed largely on behalf of Indian nationals.

James Percival, general counsel for DHS, announced the move on the social platform X, framing it as the next phase of a promise made weeks earlier. "Last month, we put the open borders industrial complex on notice \u2014 fraudulent asylum claims would result in fines against attorneys," he wrote, adding that the agency had now acted. Immigration and Customs Enforcement followed with its own post declaring that "the days of attorneys abusing and defrauding our immigration system are OVER."

## What the Government Alleges

According to a statement DHS shared with Fox News Digital, Homeland Security Investigations filed five notices of intent to fine an attorney named Vinod Doddamani, seeking penalties totalling more than $255,000 over 64 documents the agency alleges were fraudulent. DHS said Doddamani runs a nationwide practice filing asylum applications on behalf of mostly Indian immigrants in the immigration courts.

The crux of the government's case is a pattern. DHS said the declarations Doddamani filed in support of these asylum claims were "identical or nearly identical in language and substance" \u2014 that the sworn accounts of persecution, which are supposed to be the deeply personal core of any asylum claim, contained the same or nearly the same factual narrative and supporting details from one applicant to the next. The fines, the agency said, flow from a directive Percival issued the previous month authorising ICE attorneys to pursue enforcement against immigration lawyers who file false asylum claims in court. The allegations are exactly that \u2014 allegations \u2014 and Doddamani has not been found liable; Fox News Digital said it reached out to him for comment.

## Why Lawyers, and Why Now

Going after attorneys rather than applicants is a deliberate shift in strategy. Asylum fraud cases have historically been slow and individualised: each claim litigated, each migrant pursued one at a time. Fining the lawyer who allegedly mass-produces claims is meant to choke off the supply at its source, and to deter the small number of practitioners who treat asylum declarations as a template to be copied. It also raises hard questions for the much larger number of honest immigration attorneys, who now operate under the knowledge that a pattern in their filings \u2014 however innocent \u2014 could draw a six-figure federal penalty.

The focus on Indian nationals is not incidental. Indians have become one of the fastest-growing groups crossing into the United States without authorisation over the past few years, and asylum has been one of the few legal avenues available to many of them once inside the country. That has, in turn, created a cottage industry of legal help of wildly varying quality, advertised through community networks, WhatsApp groups and word of mouth rather than through bar directories.

## Why It Matters for the Diaspora

For the Indian diaspora, the danger in a story like this runs in two directions. The first is the obvious one: anyone who knowingly files a false claim is exposed, and the government is signalling it will now pursue the enabler as aggressively as the applicant. The second is subtler and affects far more people. When a single attorney's filings are flagged, every client that lawyer ever represented can find their own case reopened and re-scrutinised \u2014 including those whose claims were entirely genuine. History bears this out: in past attorney-fraud cases, thousands of applications tied to a single discredited lawyer were pulled back for review, and honest applicants were swept up alongside the fraudulent ones.

The practical lesson for NRIs and recent arrivals is unglamorous but vital. Verify that an immigration lawyer is actually licensed and in good standing in the state where they practise \u2014 every state bar maintains a public registry. Be wary of any representative who promises a guaranteed outcome, reuses a stock persecution story, or fills in the personal details for you. An asylum declaration is a sworn statement; its facts have to be your own. In an enforcement climate this aggressive, the cheapest lawyer found through a community forum can turn out to be the most expensive decision a family ever makes \u2014 not because the fee was high, but because the filing was fatal to a future in America.
"""

    img_url, ititle = pick_commons([
        "U.S. Immigration and Customs Enforcement headquarters",
        "Immigration court United States",
        "Department of Homeland Security building Washington",
        "Executive Office for Immigration Review"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "U.S. immigration enforcement signage; DHS has begun fining attorneys over allegedly fraudulent asylum filings made largely for Indian nationals"

    if not img_url:
        px = fetch_pexels_image("courthouse law justice gavel")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "DHS says it has fined an immigration attorney over fraudulent asylum claims filed mostly on behalf of Indian nationals"

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
            "Fox News (foxnews.com, June 2026) \u2014 'ICE opens up new front in war on fraud with new first-of-its-kind policy: On notice': DHS general counsel James Percival announced on X that the department fined an attorney over $255,000 for filing multiple fraudulent asylum claims on behalf of Indian immigrants; in a statement to Fox News Digital, DHS said Homeland Security Investigations filed five notices of intent to fine attorney Vinod Doddamani for allegedly filing 64 fraudulent documents on behalf of primarily Indian nationals; DHS said Doddamani operates a nationwide practice filing asylum applications for mostly Indian immigrants and that the supporting declarations were 'identical or nearly identical in language and substance'; the fines follow a directive Percival issued the prior month authorising ICE attorneys to act against lawyers filing false asylum claims; ICE posted that 'the days of attorneys abusing and defrauding our immigration system are OVER'; Fox News said it reached out to Doddamani for comment.",
            "U.S. Department of Justice (justice.gov, 2026) \u2014 'Ten Indian Nationals Indicted for Visa Fraud Conspiracy' and historical asylum-fraud cases: context on federal immigration-fraud enforcement, including that conspiracy to commit visa fraud carries up to five years in prison and a $250,000 fine and that defendants are subject to deportation; prior attorney-fraud matters (e.g. the Earl Seth David firm, with at least 25,000 applications identified, and Maryland attorney Patrick Tzeuton's 1,100-plus asylum applications) illustrate how a single discredited lawyer's entire client roster can be pulled back for review.",
            "lohud.com / Department of State guidance (June 2026) \u2014 'NY warns of immigration scams: How to spot fake USCIS officials and websites': official guidance urging applicants to verify that an attorney is licensed and in good standing via each state's public attorney registry, to beware of phishers posing as attorneys or notaries, and to recognise that businesses may provide translation and form support but cannot give legal advice or charge for free USCIS forms."
        ]),
        "diaspora_angle": "Indians are among the fastest-growing groups seeking U.S. asylum, and DHS's new policy of fining the attorneys behind allegedly fraudulent claims means even genuine applicants tied to a flagged lawyer can see their cases reopened \u2014 making it essential for NRIs to verify a lawyer's license and never let anyone fabricate their persecution story.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: International Day of Yoga 2026 \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: International Day of Yoga 2026 global celebration")
    print("="*60)

    slug = "international-day-of-yoga-2026-kolkata-modi-global-diaspora-times-square-healthy-ageing-20260625"
    headline = "From Times Square to the Bund, the World Rolled Out Its Mat Again. India's Quietest Export Just Had Its Biggest Day."
    subheadline = "The 12th International Day of Yoga drew 35,000 to Kolkata's Red Road and millions across 2,500 venues in more than 210 Indian missions \u2014 a single morning in which the diaspora became, for a few hours, India's most visible ambassadors."

    body = """On the morning of June 21, as the sun came up over the Hooghly, 35,000 people unrolled their mats along Kolkata's historic Red Road and moved through the same sequence of poses, led by Prime Minister Narendra Modi. Several thousand miles away, the sun had not yet set on a day that had begun hours earlier in Shanghai and would end well after dark in Buenos Aires. This was the 12th International Day of Yoga, and by the time the planet had finished turning, it had become the most widely observed in the event's history.

The numbers tell part of the story. India's Ministry of External Affairs, working with the Indian Council for Cultural Relations, said more than 210 Indian missions and embassies organised yoga sessions at over 2,500 historic and public venues around the world. This year's theme, "Yoga for Healthy Ageing," was chosen to speak to a planet that is living longer \u2014 a framing the World Health Organization, which marked the day at the Palais des Nations in Geneva, explicitly endorsed. "As people live longer, our goal is not just more years, but better years," WHO Director-General Dr Tedros Adhanom Ghebreyesus said in a video message.

## The Diaspora as Stage

It is in the cities of the diaspora that the day acquires its real power. In New York, the Consulate General of India coordinated a mass gathering in Times Square, where the session was led by H. R. Nagendra, the yoga teacher long associated with the Prime Minister himself. In Washington, hundreds gathered at the Lincoln Memorial in the presence of India's Ambassador to the United States, Vinay Kwatra, with "Ayurveda Corners" set up alongside to explain traditional wellness practices.

The picture repeated across continents. In Shanghai, the Indian consulate held a major session at the Bund Finance Center. In Toronto, the diaspora and curious locals gathered in front of the Ontario Legislative Building. Birmingham's Victoria Square filled with practitioners, as did open-air venues in Germany and Sweden. In Buenos Aires, an Olympic Park festival featured, for the first time, dedicated sessions for persons with disabilities. From the United Nations headquarters in New York outward, the day stitched together a single, loosely synchronised global movement \u2014 made possible, in no small part, because the Common Yoga Protocol has been translated into all six official UN languages.

## The Soft Power Underneath

It is easy to be cynical about a state-coordinated wellness event, and yoga's annual diplomatic outing is unmistakably an exercise in soft power. India proposed the International Day of Yoga at the United Nations in 2014, and the General Assembly adopted it with record co-sponsorship; every June since, the celebration has doubled as a showcase of Indian cultural reach. This year the choreography extended even underwater, with around 40 Indian Navy submariners performing yoga beneath the surface, and into record books, after a nationwide live session on June 14 drew more than four lakh simultaneous participants and a Guinness World Record.

But to read it only as statecraft is to miss what actually happens on the ground. The crowds in Times Square and on the Toronto legislature lawn were not, for the most part, diplomats. They were software engineers and grandmothers and second-generation kids dragged along by their parents, plus a substantial number of people with no Indian heritage at all, for whom yoga long ago stopped being foreign. That is the quiet achievement the day measures: a practice that left India and became, simply, part of how the world tries to stay well.

## Why It Matters for the Diaspora

For the Indian diaspora, the International Day of Yoga is one of the rare moments when the culture they carry becomes the main event in the cities they live in \u2014 not a festival tucked into a community hall, but a gathering on the steps of a national monument, organised by their own consulate, open to everyone. It is a form of belonging that runs in both directions: a chance to share something of home with neighbours and colleagues, and a reminder from India that the link is valued.

There is something fitting, too, in this year's theme. A diaspora is, almost by definition, a community thinking about the long arc \u2014 about parents ageing far away, about building lives that last in new countries, about what wellbeing means when home is split across continents. "Yoga for Healthy Ageing" is a gentle idea, but for millions of overseas Indians who turned out on a June morning, it was also a small, shared act of continuity. The mats will be rolled back up until next June. The habit, increasingly, stays out all year.
"""

    img_url, ititle = pick_commons([
        "International Day of Yoga",
        "Narendra Modi yoga day",
        "Yoga day celebration India",
        "International Yoga Day Times Square"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Participants mark the International Day of Yoga, observed on June 21 across India and more than 2,500 venues worldwide"

    if not img_url:
        px = fetch_pexels_image("group yoga outdoor sunrise")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The 12th International Day of Yoga drew millions to mass sessions in India and at Indian missions around the world"

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
            "The Indian EYE / IANS (theindianeye.com, June 2026) \u2014 'Indian Navy Takes Yoga Under Water as Nation Marks International Yoga Day 2026': India marked the 12th International Day of Yoga on Sunday June 21 with a mega event led by PM Narendra Modi at Kolkata's Red Road where thousands joined a mass session under the theme 'Yoga for Healthy Ageing'; around 40 Indian Navy personnel performed yoga underwater; Modi said yoga has evolved beyond physical exercise into a global movement promoting harmony and unity.",
            "Press Information Bureau / Ministry of Ayush (pib.gov.in; ianslive.in, June 15, 2026) \u2014 'PM Modi to lead International Day of Yoga 2026 celebrations in Kolkata': the main national celebration was held at Kolkata's historic Red Road under PM Modi; theme 'Yoga for Healthy Ageing'; more than 210 Indian Missions abroad, coordinating with the ICCR, organised celebrations at nearly 2,500 locations worldwide; a nationwide live yoga session on June 14 drew more than four lakh simultaneous participants, a Guinness World Record; the UN General Assembly adopted India's proposal for an International Day of Yoga in 2014.",
            "sujatawde.com (June 21, 2026) \u2014 'India's Yoga Resonates Across the World': the 12th IDY saw events at 2,500+ venues via 210+ Indian missions; in the US a large session was held at the Lincoln Memorial with Ambassador Vinay Kwatra and 'Ayurveda Corners,' and the Consulate General in New York coordinated a gathering at Times Square led by H. R. Nagendra; sessions were held at Shanghai's Bund Finance Center, the Ontario Legislative Building in Toronto, Birmingham's Victoria Square, and venues in Germany and Sweden; a Buenos Aires festival at Olympic Park featured first-of-their-kind sessions for persons with disabilities; the Common Yoga Protocol has been translated into the UN's six official languages.",
            "World Health Organization (who.int, June 2026) \u2014 'WHO celebrates the power of yoga for healthy ageing': WHO marked the 12th International Day of Yoga on 21 June 2026 at the Palais des Nations in Geneva with the theme 'yoga for healthy ageing'; Director-General Dr Tedros Adhanom Ghebreyesus said 'As people live longer, our goal is not just more years, but better years. Yoga supports this through gentle movement, breathing and mindfulness.'",
            "Tripura Star News (tripurastarnews.com, June 23, 2026) \u2014 'International Day of Yoga 2026 Emerges As A Global Movement With Unprecedented Participation': 35,000 participated at Kolkata's Red Road; yoga sessions were organised across continents including the United States, France, Germany and Egypt, from the United Nations Headquarters in New York to cities across Europe, West Asia, Africa and East Asia; Union Minister of State for Ayush Prataprao Jadhav credited citizens, practitioners and institutions for the day's success."
        ]),
        "diaspora_angle": "The International Day of Yoga is one of the few mornings each year when overseas Indians' own culture becomes the main public event in cities from New York to Toronto to Shanghai \u2014 a two-way act of belonging, organised by their consulates and open to everyone, that this year's 'Healthy Ageing' theme made quietly personal for a community thinking across continents and generations.",
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
