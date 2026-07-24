#!/usr/bin/env python3
"""
Videshi News Writer — June 23, 2026 (10:30 UTC run)
2 NEW articles (both fresh, distinct from prior runs which covered SpaceX,
NEET re-exam, Iran sanctions/oil, foreign-investor return, USTR Delhi trade,
China normalisation, PMI/business confidence, RBI NRI deposits, Jio IPO, NSE
IPO, Russian crude pivot):
  1. CUET UG 2026 results declared — NTA posts scorecards for ~1.16 million
     who sat India's single biggest gateway to central-university seats, with
     female candidates nearly matching male for the first time. (education —
     diaspora-family college-admissions angle)
  2. Centre tightens FCRA foreign-funding rules for NGOs — new gazette
     notification forces disclosure of the ultimate donor behind donor-advised
     funds and intermediary vehicles, bars foreign nationals as key
     functionaries, and excludes proselytisation. (policy — diaspora-giving
     and charity angle)
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


# ─── Article 1: CUET UG 2026 results declared ──────────────────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: CUET UG 2026 results declared")
    print("="*60)

    slug = "cuet-ug-2026-result-declared-nta-scorecard-central-university-admissions-diaspora-20260623"
    headline = "India Just Released the Results of the Exam That Decides a Million College Futures"
    subheadline = "The National Testing Agency declared the CUET UG 2026 scorecards on Tuesday for the roughly 1.16 million students who sat the country's single largest gateway to central-university seats \u2014 and for the first time, the number of women taking it has drawn almost level with men, a quiet shift that the diaspora's own college-bound families will feel directly."

    body = """The National Testing Agency declared the results of the Common University Entrance Test (Undergraduate) 2026 on Tuesday, posting scorecards on cuet.nta.nic.in for the millions of students whose admission to India's central and participating universities now hinges on the numbers they downloaded today. It is one of the most consequential days on India's academic calendar: CUET is the single common gateway through which more than 250 universities \u2014 including roughly 50 central universities such as Delhi University, Banaras Hindu University and Jawaharlal Nehru University \u2014 fill their undergraduate seats.

The scale is staggering. According to the NTA's statistics, 15,68,867 unique candidates registered for CUET UG 2026, of whom 11,64,098 actually appeared. Between them they sat a sprawling 49,05,176 individual subject tests out of more than 67 lakh registered, a measure of how many students attempt several subjects to keep their options open across courses and colleges. The examination was conducted in computer-based mode in two windows \u2014 from May 11 to 31, and again on June 6 and 7 \u2014 after a calendar stretched by the sheer logistics of testing well over a million candidates.

## A Quiet Milestone in the Numbers

Buried in the gender breakdown is a genuinely notable shift. Among unique candidates, 7,94,257 were male and 7,74,607 were female \u2014 a gap of fewer than 20,000 in a field of more than a million and a half. Indian higher education has spent decades closing the distance between how many young men and how many young women compete for its most sought-after seats, and a near-even CUET cohort is one of the clearer signs that the gap, at least at the point of entry, is narrowing fast. Three candidates registered as transgender, a reminder that the test's official record-keeping now reflects categories that did not appear on Indian mark sheets a generation ago.

The mechanics matter for how those numbers translate into seats. CUET UG 2026 carried a maximum of 250 marks per subject \u2014 50 questions of five marks each \u2014 with one mark deducted for every wrong answer and nothing gained or lost for a question left blank. The NTA does not set a single national pass mark; instead, each participating university publishes its own cut-offs against the percentile and normalised scores once results are out. In practice, students chasing the most competitive programmes at Delhi University, BHU or JNU typically need scores well into the high 700s and 800s, and the next few weeks will turn entirely on those university-by-university lists.

## Why the Diaspora Should Care

For the Indian diaspora, CUET is not a distant domestic story \u2014 it is increasingly the door their own children walk through. A growing number of NRI and Overseas Citizen of India families want their children to do at least part of their undergraduate education in India, whether for the cost, the cultural grounding, or a specific programme, and CUET has become the standard route in. Many central universities and several private institutions reserve supernumerary seats for NRI and foreign-national applicants, but those candidates are still measured against the same scorecard architecture the NTA released today. A diaspora parent in New Jersey or London comparing options for a child finishing high school abroad is now reading the same percentile tables as a parent in Patna.

There is a practical, calendar-driven urgency too. Indian university admissions move quickly once CUET results drop: counselling registrations, document verification and seat allotment can all unfold within weeks, and the timelines rarely bend for families operating across time zones. For households juggling a foreign academic year, visa or OCI paperwork, and the narrow Indian admissions window, missing a counselling deadline can cost an entire year. The result declaration is the starting gun, and diaspora families who want an Indian option on the table need to be watching cut-offs and counselling notices as closely as any family in Delhi.

## What's Next

The NTA is expected to publish subject-wise toppers and the list of candidates who scored a perfect 100th percentile in the coming days, the headline figures that dominate India's results-season coverage. The real action, though, shifts immediately to the universities: Delhi University's CSAS portal, BHU, JNU and dozens of others will roll out their own cut-offs and counselling schedules, and the gap between a strong CUET score and an actual seat will be decided there. For the more than a million students \u2014 and the diaspora families among them \u2014 who refreshed cuet.nta.nic.in on Tuesday, the wait for a number is over. The wait for a seat has just begun."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: exam hall / university / students. No single named person.
    img_url, ctitle = pick_commons([
        "Delhi University campus building",
        "Banaras Hindu University campus",
        "Jawaharlal Nehru University campus",
        "students examination hall India",
        "university examination India"
    ])
    img_caption = "A central-university campus in India; the NTA declared CUET UG 2026 results on June 23 for roughly 1.16 million candidates"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("university students exam hall")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Students in an examination hall; CUET UG 2026 results were declared on June 23 for over a million candidates"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "education",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Careers360 (news.careers360.com) \u2014 CUET 2026 Result Date Time (OUT) LIVE: cuet.nta.nic.in results link out (June 23, 2026): NTA released CUET UG 2026 results today, June 23, on cuet.nta.nic.in; statistics \u2014 15,68,867 unique candidates registered, 11,64,098 unique candidates appeared, 67,56,327 subject tests registered, 49,05,176 subject tests appeared; gender-wise unique candidates \u2014 Male 7,94,257, Female 7,74,607, Transgender 3; exam conducted May 11-31 and June 6-7, 2026; total 250 marks per subject (50 questions x 5 marks), +5 correct / -1 incorrect / 0 unattempted; more than 250 universities including ~50 central universities accept CUET scores; NTA does not fix national passing marks \u2014 cut-offs set by individual participating universities",
            "Careers360 / Shiksha / Jagran Josh \u2014 CUET UG 2026 scorecard and result process (June 17-23, 2026): scorecard downloadable at cuet.nta.nic.in using application number and date of birth/password; scorecard shows student name, parent name, gender, category, roll number, course/subject, exam date/shift, raw scores, percentile scores and qualifying status; competitive programmes at Delhi University, BHU and JNU typically require scores in the 750-850 range; NTA to publish subject-wise toppers and 100th-percentile candidates via press release; counselling and seat allotment by participating universities follow result declaration",
            "Collegedunia / NTA notification \u2014 CUET toppers and 100-percentile distribution context (2025 comparison): in CUET UG 2025, 13,54,699 registered and 10,71,735 appeared; 2,679 candidates scored 100 percentile in one subject, 150 in two subjects, 17 in three subjects and just 1 candidate in four of five subjects, illustrating how rare multi-subject perfect percentiles are; NTA highlights the highest overall scorers across all subjects in its results press release"
        ]),
        "diaspora_angle": "CUET is increasingly the door diaspora families' own children walk through for an Indian undergraduate education, and NRI/OCI applicants are measured against the same scorecard and the same fast-moving counselling calendar that the NTA's results just set in motion \u2014 a deadline that does not bend for families operating across time zones.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Centre tightens FCRA foreign-funding rules ──────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Centre tightens FCRA foreign-funding rules")
    print("="*60)

    slug = "centre-tightens-fcra-rules-ngo-foreign-funding-donor-disclosure-diaspora-giving-20260623"
    headline = "India Just Rewrote the Rules on Foreign Money for Its Charities \u2014 and Diaspora Donors Are in the Frame"
    subheadline = "A new Home Ministry notification forces NGOs to name the ultimate source behind donor-advised funds and intermediary vehicles, bars most foreign nationals from running them, and excludes proselytisation \u2014 tightening the pipe through which billions in diaspora generosity reaches India each year."

    body = """The Indian government has overhauled the rules that govern how the country's charities and non-profits take in foreign money, issuing a gazette notification this week that significantly tightens the Foreign Contribution Regulation Act framework. The amendments, notified by the Union Home Ministry, reach into almost every part of how an NGO registers, who is allowed to run it, where the money can be spent, and \u2014 most consequentially for the diaspora \u2014 how far back the government can trace the original source of a donation.

The single biggest change for overseas givers is a new transparency rule on layered donations. If foreign money reaches an Indian NGO through "intermediary remittance vehicles" or "Donor Advised Funds," the organisation must now disclose the ultimate donor \u2014 the original source of the money \u2014 in its application. That strikes directly at one of the most common ways the diaspora gives: through US and UK charitable intermediaries, community foundations and donor-advised funds that pool many individual gifts before routing them to projects in India. Until now, such structures could obscure who was really behind a grant; under the amended rules, that anonymity largely disappears.

## What Else Changes

The notification layers on several other requirements. NGOs must now choose their activities from a predefined list of approved purposes \u2014 spanning religious, educational, social, cultural and economic work \u2014 and specify the exact states or union territories where the funds will be used, locking registrations to a declared scope. Faith-based activity such as religious education and the preservation of traditions is explicitly allowed, but proselytisation and religious conversion efforts are just as explicitly excluded from the eligible categories, a distinction that has been at the centre of several recent enforcement actions.

The rules also harden the gatekeeping around who controls these organisations. Any association with foreign nationals \u2014 other than persons of Indian origin \u2014 as its key functionaries will "ordinarily not be considered" for registration or prior permission, though the central government keeps the power to grant case-by-case exceptions. The very definition of "key functionary" has been broadened to capture company directors, partners, trustees, members of governing bodies and even the Karta of a Hindu Undivided Family \u2014 anyone, in effect, who exercises real control. To weed out dormant licences, organisations must now have spent at least Rs 10 lakh of foreign contributions on their declared activities over the previous two financial years to stay eligible for renewal. NGOs must disclose their social media accounts, file a detailed activity report alongside financial statements, and \u2014 under the prior-permission route \u2014 wait until at least 75% of an earlier instalment is verified as spent, via field inspection, before the next tranche is released.

## Why the Diaspora Should Care

For the Indian diaspora, this is unusually close to home, because the diaspora is one of the largest sources of the foreign contributions the rules govern. NRIs and OCIs send money not just to family but to temples and gurdwaras, school and scholarship funds, hospitals, disaster relief and the village-development and educational charities that dot the giving landscape of every major Indian community abroad. Much of that generosity flows precisely through the donor-advised funds and intermediary platforms the new disclosure rule targets. A diaspora donor who gives through a US foundation to an Indian non-profit should expect that the recipient will now have to name them as the ultimate source \u2014 a meaningful shift for anyone who valued the discretion such structures offered.

The practical fallout is twofold. Diaspora-linked organisations \u2014 especially those with foreign nationals on their boards, or those whose work brushes against the proselytisation line \u2014 may find registration and renewal harder, and some smaller groups could struggle with the heavier compliance load of activity reports, social-media disclosure and the Rs 10 lakh spending floor. At the same time, donors who want their gifts to land cleanly will increasingly need to check that the charity they support is FCRA-compliant under the new regime, because money sent to an organisation that later loses its licence can be frozen or, under the broader FCRA framework, even taken over. The era of giving to India without asking hard questions about a charity's paperwork is ending.

## What's Next

The amendments are now in force, and the real test will be how the Home Ministry applies them at renewal time, when thousands of FCRA registrations come up for review against the new spending threshold, donor-disclosure and key-functionary norms. The tightening also sits inside a charged backdrop: foreign funding of Indian civil society has become a recurring point of friction with Washington and a frequent subject of enforcement raids, and the government has framed the changes as being about transparency and national security rather than restriction. For the diaspora, the message is plainer. The pipe through which their generosity reaches India is narrower and far more closely watched than it was a week ago, and giving well now means giving with the paperwork in mind."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: government / parliament / NGO / currency. No single named person.
    img_url, ctitle = pick_commons([
        "North Block Secretariat New Delhi",
        "Ministry of Home Affairs India building",
        "Parliament House New Delhi",
        "Indian rupee banknotes currency",
        "Rashtrapati Bhavan New Delhi"
    ])
    img_caption = "A government building in New Delhi; the Union Home Ministry tightened FCRA foreign-funding rules for NGOs in a June 2026 gazette notification"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("government building official India")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A government building; new FCRA rules tighten how Indian NGOs receive and report foreign funds"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "policy",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Hindu BusinessLine \u2014 Centre tightens FCRA rules for NGOs receiving foreign funds (June 23, 2026): amended FCRA rules require NGOs to have spent foreign contributions on chosen activities over the last two years; under Prior Permission, the second or any later instalment released only after at least 75% of the previous instalment is utilised, verified by field inquiry; NGOs must provide social media account details in registration/renewal applications; money via 'intermediary remittance vehicles' or 'Donor Advised Funds' requires disclosure of the ultimate donor (original source); annual returns must include a detailed activity report alongside financial statements; NGOs prohibited from producing or broadcasting 'news or current affairs' content",
            "LiveMint \u2014 Social media disclosure, donor transparency and more: key changes for NGOs as government revises FCRA norms (June 23, 2026): new requirement that associations spend at least Rs 10 lakh of foreign contributions on declared activities during the previous two financial years to renew or avoid cancellation; subsequent Prior Permission instalments released only after 75% utilisation, with field inspections; foreign nationals (other than persons of Indian origin) as key functionaries face stricter eligibility; definition of 'key functionary in relation to a person other than an individual' expanded to include company directors, partners in firms, trustees, the Karta of a Hindu Undivided Family, and any person exercising management control",
            "PTI via Swadesi / CSR News (csrnews.in) \u2014 Centre amends rules for receiving foreign funds (June 22-23, 2026): Union Home Ministry gazette notification amending FCRA Rules, 2011; NGOs must choose from a predefined list of purposes and specify state/UT of operation, recorded in the registration certificate; faith-based activities (religious education, preservation of faith traditions) permitted but proselytisation/religious conversion explicitly excluded; associations with foreign nationals (other than persons of Indian origin) as key functionaries 'ordinarily not be considered' for registration or prior permission, with central-government exceptions possible; measures aimed at enhancing transparency, accountability and monitoring of foreign funding"
        ]),
        "diaspora_angle": "NRIs and OCIs are among the largest sources of the foreign contributions these rules govern \u2014 much of it flowing through the donor-advised funds and intermediary platforms the new disclosure rule targets \u2014 so diaspora donors should expect Indian charities to now name them as the ultimate source, and will increasingly need to verify a charity's FCRA compliance before they give.",
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
