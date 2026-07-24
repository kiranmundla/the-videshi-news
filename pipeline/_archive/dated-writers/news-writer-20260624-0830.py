#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (08:30 UTC run)
2 NEW articles, distinct from all prior runs:
  1. US DHS proposes hiking naturalization (N-400) fees by up to 80% —
     from $760/$710 to $1,330/$1,280 — plus steeper appeal fees and the
     elimination of most low-income waivers. Immigration/diaspora story for the
     ~1M annual applicants, heavily Indian green-card holders.
  2. Amarnath Yatra 2026 gets the largest-ever paramilitary deployment (670 CAPF
     companies) ahead of its July 3 start. Diaspora-faith / safety angle for NRIs
     who travel home for the pilgrimage and for families back in J&K.
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


# ─── Article 1: US naturalization fee hike up to 80% ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: US citizenship fee hike up to 80%")
    print("="*60)

    slug = "us-citizenship-naturalization-fee-hike-80-percent-n400-indians-green-card-20260624"
    headline = "Becoming an American Is About to Get Much More Expensive. Indian Green-Card Holders Will Feel It First."
    subheadline = "A new Trump administration proposal would raise the cost of applying for US citizenship by up to 80 percent \u2014 from $710 to $1,280 online, and $760 to $1,330 on paper \u2014 while scrapping most fee waivers for low-income applicants. For the hundreds of thousands of Indians who form the largest single bloc of new American citizens, the math on naturalization just changed."

    body = """For the roughly one million people who apply to become naturalized US citizens every year, the price of the final step in a long immigration journey is about to jump sharply. Under a proposal published this week in the Federal Register by the Department of Homeland Security, the fee to file Form N-400 \u2014 the application for naturalization \u2014 would rise from $710 to $1,280 for an online filing, and from $760 to $1,330 on paper. Those are increases of 80 percent and 75 percent respectively, and they land on a community in which Indians consistently rank among the very largest groups of new citizens.

The increases do not stop at the application itself. An applicant whose case is denied and who wants to appeal would pay $1,475 for a paper request, up from $830, and $1,425 online, up from $780 \u2014 jumps of nearly 80 percent. DHS is also proposing to eliminate most fee waivers and reduced rates for low-income applicants, while keeping the exemption in place for those seeking citizenship through military service.

## Why DHS Says It Is Doing This

The department frames the move as cost recovery. USCIS is largely funded by the fees it collects, and officials argue the current charges "do not recover the full cost of thoroughly adjudicating applications for naturalization." The agency says the higher fees are needed to pay for the stricter background checks and expanded vetting ordered under President Trump's executive directives. In its own filing, DHS acknowledged that the change "would probably discourage some people from applying," and noted it "no longer believes naturalization benefit requests should get lower fees at the potential expense of other immigration benefits." If fully implemented, the department estimates the increases would raise more than $430 million a year.

The proposal arrives alongside a wider tightening. A separate Justice Department plan would triple some immigration-court filing fees \u2014 lifting the cost to appeal an immigration judge's ruling from $110 to $975 \u2014 and the administration has separately moved to charge for asylum applications for the first time and to revoke the citizenship of some naturalized immigrants accused of fraud or crimes. Taken together, they mark one of the most aggressive efforts in decades to raise the cost and lower the volume of legal immigration.

## Why This Hits Indians Hardest

Indians are, year after year, one of the two or three largest nationalities among newly naturalized US citizens, and the single largest group on many employment-based green-card tracks. For an Indian family that has already spent years \u2014 often more than a decade \u2014 waiting out the green-card backlog, naturalization is the last gate, and the one that finally brings a US passport, visa-free travel, the right to vote, and the ability to sponsor relatives. Pushing that final fee toward $1,300 per person turns a routine filing into a meaningful expense, especially for households naturalizing several family members at once. In rupee terms, Indian outlets have pegged the new paper fee at roughly \u20b91.26 lakh, up from about \u20b972,000.

The removal of fee waivers compounds the effect. Lower-income green-card holders \u2014 including many on the service-sector and care-economy fringes of the diaspora \u2014 have historically relied on those waivers to afford the application at all. Critics, including former DHS officials, warn that the change risks "turning citizenship into a benefit that is less accessible to those of modest means," undercutting the long-standing public-policy goal of encouraging immigrants to naturalize and integrate.

## The 60-Day Clock

The proposal is not yet final. It must go through a 60-day public comment period after publication in the Federal Register, during which immigrant-advocacy groups, employers and individuals can weigh in before DHS can issue a binding rule. That window also creates a practical incentive: green-card holders who are already eligible and were planning to apply may want to file before the higher fees take effect, locking in the current $710 to $760 rate rather than waiting.

## What's Next

Expect a wave of comments, likely legal challenges, and a scramble among eligible applicants to file ahead of any final rule. For the Indian diaspora \u2014 disproportionately represented at exactly the stage of the immigration journey this fee governs \u2014 the message is to check eligibility now, budget for a steeper bill if the rule survives, and watch the comment period closely. Citizenship has always been the prize at the end of the line. It is about to come with a much bigger price tag."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing hero image (USCIS / citizenship / naturalization)...")
    img_url, ctitle = pick_commons([
        "United States Citizenship and Immigration Services building",
        "naturalization ceremony United States citizens",
        "US citizenship oath ceremony",
        "USCIS office",
        "US passport flag citizenship"
    ])
    img_caption = "A US naturalization ceremony; a new DHS proposal would raise citizenship application fees by up to 80 percent"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("american flag passport citizenship")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A US passport and flag; Washington has proposed sharply higher fees to become a naturalized citizen"

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
            "USA Today (usatoday.com, June 2026) \u2014 'New Trump plan would hike US citizenship fees by 80%': DHS proposal published in the Federal Register would raise the naturalization (N-400) fee from $760 to $1,330 for paper applications and $710 to $1,280 online \u2014 increases of 75% and 80%; rejected applicants would pay $1,475 to appeal (up from $830) on paper and $1,425 (up from $780) online; DHS is eliminating some fee waivers for poor applicants while keeping them for military applicants; officials acknowledged the change 'would probably discourage some people from applying' and said fees are needed for stricter background checks; if implemented the increases would cost prospective citizens more than $430 million annually; about 1 million people request naturalization each year.",
            "Washington Examiner (washingtonexaminer.com, June 2026) \u2014 'USCIS boosts citizenship application fee to $1,300': DHS/USCIS proposal released Monday would mean applicants pay $1,330 for paper filings and $1,280 online \u2014 75% and 80% increases over the 2024 fees of $760 and $710; the proposed rule would also eliminate fee waivers and reduced rates for most applicants per a Federal Register notice; in 2016 it cost $595 to apply; former DHS official Adam Klein warned substantially increasing fees 'risks turning citizenship into a benefit that is less accessible to those of modest means.'",
            "TheTravel (thetravel.com, June 2026) \u2014 'U.S. Government To Make Obtaining American Passports Hundreds Of Dollars More Expensive For Certain Applicants': the June 22 DHS proposal significantly increases Form N-400 filing costs; paper applications could rise from $760 to $1,330 and online from $710 to $1,280; appeal cost would rise from $830 to $1,475; service-member fee exemption remains; DHS says current fees 'do not recover the full cost of thoroughly adjudicating applications'; described as the latest in a string of efforts to curb legal immigration; CBS News immigration correspondent Camilo Montoya-Galvez cited on heavier scrutiny of applicants.",
            "Outlook Business (outlookbusiness.com, June 2026) \u2014 'US Plans 75% Citizenship Fee Hike; Indian Green Card Holders May Face Costs Up to \u20b91 Lakh': paper-based N-400 fee would rise from $760 (\u20b971,973) to $1,330 (\u20b91,26,038) and online from $710 to $1,280; paper N-336 appeal fees up 78% to $1,475 and online N-336 up 83% from $780 to $1,425; the rule requires a 60-day public comment period after Federal Register publication before DHS can issue a final rule; DHS says increases recover 'full costs' including expanded screening and vetting; critics argue eliminating waivers would disproportionately affect low-income immigrants.",
            "CNN / NBC Palm Springs (nbcpalmsprings.com, June 2026) \u2014 'Trump administration looks to triple fees for some immigration court filings': a parallel Justice Department (EOIR) proposal would triple some immigration-court filing fees \u2014 e.g. an appeal of an immigration judge's decision rising from $110 to $975, and cancellation-of-removal forms from $100 to more than $300; the administration last November also proposed charging for asylum applications and an 83% fee increase for the naturalization form; the rule publishes Friday in the Federal Register and takes effect only after a public comment period."
        ]),
        "diaspora_angle": "Indians are consistently among the largest groups of new US citizens and the biggest bloc on employment-based green-card tracks, so a proposed 75-80% jump in the N-400 naturalization fee \u2014 toward roughly \u20b91.26 lakh per applicant \u2014 plus the loss of low-income waivers directly raises the cost of the final step for hundreds of thousands of NRI families, with a 60-day comment window before any rule becomes final.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Amarnath Yatra 2026 record security ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Amarnath Yatra 2026 record security")
    print("="*60)

    slug = "amarnath-yatra-2026-record-paramilitary-deployment-670-capf-july-3-security-diaspora-20260624"
    headline = "India Is Mounting Its Biggest-Ever Security Operation for the Amarnath Pilgrimage. Here's Why This Year Is Different."
    subheadline = "Ahead of the 57-day Amarnath Yatra that begins July 3, the government has approved a record 670 companies of central forces \u2014 a multi-layered grid stretching from the Jammu gateway to the Himalayan cave shrine. For the diaspora that travels home for the pilgrimage, and for families across Kashmir, the scale of this year's deployment is unprecedented."

    body = """Every summer, hundreds of thousands of Hindu pilgrims trek through the South Kashmir Himalayas to reach the Amarnath cave shrine and its naturally formed ice lingam. This year, they will do so under the heaviest security blanket the pilgrimage has ever seen. The Union Ministry of Home Affairs has approved the deployment of around 670 companies of Central Armed Police Forces (CAPFs) for the 2026 Yatra \u2014 officials describe it as the highest-ever for the annual event \u2014 to guard a 57-day pilgrimage that begins on July 3 and concludes on August 28.

A "company" of paramilitary forces typically numbers around 80 to 150 personnel, which puts the central deployment alone in the tens of thousands, before the Jammu and Kashmir Police, the Army and railway security are counted. The forces, drawn largely from the CRPF, Border Security Force, Sashastra Seema Bal, Indo-Tibetan Border Police and CISF, began arriving in early June, with the bulk of the deployment slated to be in place by June 25 \u2014 roughly a week before the first pilgrims set out.

## A Grid From Lakhanpur to the Cave

The security plan is built as a multi-layered grid rather than a perimeter. It stretches from Lakhanpur, the gateway into Jammu and Kashmir, all the way up to the cave shrine, covering the twin pilgrimage routes of Pahalgam and Baltal, the base camps at Nunwan and Baltal, the Yatri Niwas in Jammu, and the long, vulnerable stretches of the Jammu-Srinagar National Highway. The Army is positioning troops on dominating heights overlooking the routes and around the shrine itself.

Authorities have layered in technology and specialist units on top of the troop numbers. More than 400 CCTV cameras and high watchtowers have been installed along the route, with drone surveillance, intelligence-based operations and mock emergency drills at the base camps. Specialised police teams \u2014 known locally by names such as Markhor and Snow Leopard units, alongside Special Operations Groups, Quick Reaction Teams and Mobile Rescue Teams \u2014 have been stationed at sensitive points, and districts along the route have been carved into tightly supervised security zones. Officials say the arrangements are being calibrated so that routine counter-terrorism operations elsewhere in the territory are not disrupted.

## Why the Heightened Posture

The scale reflects a security environment that has stayed tense across the past year, and the pilgrimage has historically been a target. Officials note that some companies retained from earlier operations in Jammu and Kashmir are being folded into the Yatra grid, and that the railway corridor \u2014 increasingly used by pilgrims travelling on Vande Bharat and other trains through Udhampur, Katra, Reasi, Banihal and Qazigund \u2014 is getting its own intensified cover. With more than 3.5 lakh pilgrims reported to have registered since the process opened in mid-April, planners are bracing for a heavy turnout that itself raises the stakes of crowd management and safety.

## Why the Diaspora Should Care

The Amarnath Yatra is not only a domestic event. For many in the diaspora, it is a pilgrimage worth flying home for \u2014 NRIs from the Gulf, North America, the UK and Australia routinely time summer trips to India around it, and overseas registration and helicopter-booking channels feed directly into the turnout. A smoothly run, heavily secured Yatra is, for those travellers, the difference between a once-in-a-lifetime spiritual journey and a cancelled plan.

There is a wider stake, too. For the large Kashmiri and J&K-origin diaspora, the annual deployment is also a barometer of how their home region is governed and policed. The same arrangements that reassure a pilgrim can deepen unease among residents who experience the build-up as militarisation of daily life \u2014 a tension that plays out every year and is felt keenly by families abroad watching from a distance. The story of this Yatra, in other words, is read very differently depending on which part of the diaspora is reading it.

## What's Next

Expect the deployment to complete by the final week of June, followed by route sanitisation drives, road-opening operations and a steady ramp-up of pilgrim movement once the Yatra opens on July 3. The government's bet is that an unprecedented show of force will keep a high-profile, high-turnout pilgrimage incident-free through late August. For pilgrims at home and the diaspora travelling in, the next two months will test whether the largest-ever security operation delivers the safe passage it promises."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing hero image (Amarnath / Kashmir pilgrimage / security)...")
    img_url, ctitle = pick_commons([
        "Amarnath cave shrine pilgrimage",
        "Amarnath Yatra pilgrims Kashmir",
        "Pahalgam Kashmir mountains pilgrimage",
        "Baltal Amarnath route",
        "Kashmir Himalayas pilgrimage trail"
    ])
    img_caption = "Pilgrims on the Amarnath Yatra route in the Kashmir Himalayas; the 2026 pilgrimage has drawn a record security deployment"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("Himalayas mountain pilgrimage trail Kashmir")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The Kashmir Himalayas; the 2026 Amarnath Yatra is being guarded by a record paramilitary deployment"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Asian Nama (asiannama.com, May 29 2026) \u2014 'Centre Deploys Record 670 CAPF Companies for Amarnath Yatra Security': the Union MHA, in consultation with the J&K administration and security agencies, approved deployment of 670 companies of Central Armed Police Forces for the 57-day pilgrimage beginning July 3 and concluding August 28 \u2014 described as the highest-ever deployment for the annual pilgrimage; the grid extends from Lakhanpur to the cave shrine, covering the Baltal and Pahalgam routes, base camps at Baltal and Nunwan, Yatri Niwas Bhagwati Nagar Jammu and the Jammu-Srinagar National Highway; additional CAPF companies began arriving from early June with deployment to be completed by June 25; the Army will hold strategic heights overlooking the routes.",
            "South Asia Terrorism Portal (satp.org, May 2026) \u2014 '581 paramilitary companies to be deployed for Amarnath Yatra security in J&K': reporting on the deployment build-up, with the largest contingents drawn from the CRPF (219 companies), BSF (143), SSB (97), ITBP (62) and CISF (60); nearly 80 companies retained from Operation Sindoor in J&K were also folded into Yatra security; deployment in place by the second week of June covering Lakhanpur to the Nunwan (Pahalgam) and Baltal base camps.",
            "Kashmir Media Service (kmsnews.org, June 2026) \u2014 reporting on Amarnath Yatra 2026 security: more than 400 CCTV cameras installed and high watchtowers erected along the route, modern surveillance infrastructure at key points and base camps, mock drills at Nonwan/Nunwan base camp in Pahalgam; specialist units including Markhor teams, Snow Leopard units, Special Operations Group, Mobile Rescue Teams and Quick Reaction Teams deployed; districts divided into security zones; phased induction of additional CAPFs under the J&K Yatra security operation; observers note residents experience the recurring build-up as militarisation of the territory.",
            "New Kerala / Alfaaz The Words (newkerala.com, alfaazthewords.in, June 2026) \u2014 'Amarnath Yatra 2026: CAPF Deployed for Security' and 'Multi-layered security arrangements planned': the 57-day pilgrimage begins July 3 and concludes August 28 coinciding with Shravan Purnima; pilgrims access the cave via the Pahalgam or Baltal routes with helicopter services available; security intensified along the Jammu-Srinagar railway corridor through Udhampur, Katra, Reasi, Banihal and Qazigund as authorities expect many pilgrims to travel by rail including Vande Bharat trains; more than 3.5 lakh pilgrims registered since registration opened on April 15."
        ]),
        "diaspora_angle": "The Amarnath Yatra draws NRIs who fly home each summer for the pilgrimage and is watched closely by the large Kashmiri and J&K-origin diaspora, so a record 670-company security deployment for the July 3-August 28 Yatra matters both as the safety guarantee that makes the trip possible and as a barometer of how their home region is being governed.",
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
