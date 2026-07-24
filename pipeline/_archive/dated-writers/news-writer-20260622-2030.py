#!/usr/bin/env python3
"""
Videshi News Writer — June 22, 2026 (20:30 UTC run)
2 NEW articles:
  1. DHS/USCIS proposed rule hikes naturalization fee to $1,330 (paper) /
     $1,280 (online), ~75-80% jump, eliminates fee waivers and reduced-rate
     option; DOJ EOIR separately proposes tripling immigration-court filing
     fees. India is the #2 source of new US citizens. (immigration / diaspora)
  2. US formally notifies (DSCA, Federal Register, June 17) a combined
     $482.2M sustainment-support package for India's AH-64E Apaches ($198.2M,
     Boeing/Lockheed) and M777A2 ultra-light howitzers ($230M, BAE), landing
     just as USTR Greer arrives for trade talks. (geopolitics / defense)
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


# ─── Article 1: USCIS naturalization fee hike to $1,330 ─────────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: USCIS naturalization fee hike to $1,330")
    print("="*60)

    slug = "uscis-naturalization-fee-hike-1330-eliminate-waivers-indian-green-card-holders-20260622"
    headline = "America Just Proposed Making Citizenship Cost $1,330 — and Killing the Discount for Those Who Can't Pay"
    subheadline = "A new DHS rule would raise the naturalization fee by about 75% and scrap the waivers and reduced rates that lower-income applicants rely on. Indians are the second-largest group of new US citizens, and tens of thousands of green-card holders are now staring at a steeper price for the last step."

    body = """Becoming an American is about to get a lot more expensive. Under a proposed rule the Department of Homeland Security released on Monday, the fee to file for US citizenship would jump from $760 to $1,330 for a paper application and from $710 to $1,280 for an online one — increases of roughly 75% and 80%. Just as consequentially, the rule would eliminate the fee waivers and reduced-rate option that have long let lower-income green-card holders apply at little or no cost.

For the Indian diaspora, this is not an abstract policy debate. Indians are the second-largest group of new US citizens after Mexicans: 49,700 people born in India naturalized in fiscal 2024 alone, according to US Citizenship and Immigration Services. Behind that number sits a far larger pool — about 2.8 million India-born residents, the second-biggest foreign-born population in the country — many of whom hold green cards and are working toward the oath.

## What the Rule Would Do

The proposed rule, published in the Federal Register by USCIS, reframes naturalization as a service whose full cost should fall on the applicant. The agency, which it notes is funded almost entirely by the fees it collects rather than by taxpayer appropriations, says the higher charges are needed to "cover the full cost of adjudicating applications" at a time when each case is getting heavier scrutiny.

Two changes do the most damage to accessibility. First, the rule would scrap the fee-waiver program for citizenship applicants — the route used by those on means-tested benefits, those earning at or below 150% of the federal poverty line, or those facing a documented financial hardship. In fiscal 2024, 14.3% of everyone who naturalized did so with an approved fee waiver; women and applicants 65 and older leaned on it most. Second, it would end the reduced-fee option for households earning up to 400% of the poverty line. The combined effect is a sharper, all-or-nothing price: pay the full amount, or do not apply. Fee exemptions for military personnel seeking citizenship would remain.

The naturalization rule does not stand alone. In a separate move, the Justice Department's Executive Office for Immigration Review has proposed tripling — and in some cases far more than tripling — the fees for immigration-court filings. The cost to appeal an immigration judge's decision would rise from $110 to $975; forms for cancellation of removal would climb from $100 to more than $300. Together, the two proposals push up the price of nearly every formal step toward, or away from, legal status.

## Where It Comes From

The fee jump fits a wider pattern. The administration has separately moved to require certain green-card hopefuls already in the US to return to their home countries before seeking permanent status, floated stripping citizenship from some naturalized immigrants over alleged fraud, and last year imposed a $1,000 charge aimed at parole-system use. The naturalization proposal is the cost-of-entry version of the same posture: make the process pricier and the screening tougher.

Critics argue the math cuts against decades of bipartisan logic. "While USCIS is largely a fee-funded agency and must recover its operational costs, substantially increasing naturalization fees risks turning citizenship into a benefit that is less accessible to those of modest means," former DHS official Adam Klein told Newsweek, warning that higher fees "could undermine" the civic and economic integration that naturalization is meant to encourage. Immigrant-rights groups note that citizenship already costs hundreds of dollars and that removing waivers would erect, in effect, a wealth test for the final step.

Crucially, none of this is law yet. As a proposed rule, it must run a 60-day public-comment period and survive the rest of the federal rulemaking process — a stretch that, in past fee fights, has invited lawsuits and revisions.

## Why It Matters to NRIs

For an Indian green-card holder, the calculus is suddenly less comfortable. The well-paid software engineer in Texas will absorb a $570 increase as an annoyance; the elderly parent sponsored by a US-citizen child, the recent graduate between jobs, or the single-income family that planned to apply once the budget allowed may now find the door heavier to push. The end of the over-65 and low-income relief is felt most acutely by exactly those applicants.

There is also a timing question. Anyone close to eligibility — five years as a lawful permanent resident, three if married to a US citizen — has reason to weigh filing before any final rule takes effect, since the current $760/$710 schedule and the existing waiver still apply until then. The comment window is the moment for diaspora organizations, which have mobilized against fee hikes before, to be heard. For a community that has made naturalization a defining marker of arrival — second only to Mexico in turning green cards into passports — the price of that last step is now, quite literally, on the table."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "United States naturalization ceremony",
        "United States Citizenship and Immigration Services building",
        "USCIS oath ceremony new citizens",
        "US citizenship ceremony oath of allegiance"
    ])
    img_caption = "New citizens take the oath of allegiance at a US naturalization ceremony; a proposed rule would raise the citizenship fee to $1,330"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("american flag citizenship")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "An American flag; a proposed DHS rule would sharply raise the cost of applying for US citizenship"

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
            "Bloomberg Law \u2014 Trump DHS Proposal Would Hike Naturalization Fees for Immigrants (June 22, 2026): DHS proposal (RIN 1615-AD08) released Monday would raise naturalization application costs to as much as $1,330; USCIS last updated fees in 2024 ($760 paper / $710 online); agency says increases needed to cover full cost of adjudicating applications; comes as administration plans to strip some naturalized immigrants of citizenship over alleged fraud",
            "Washington Examiner \u2014 USCIS boosts citizenship application fee to $1,300 (June 22, 2026): DHS/USCIS proposal would set fees at $1,330 (paper) and $1,280 (online), increases of 75% and 80%; previous 2024 rule was $760/$710; in 2016 it cost $595; rule would eliminate fee waivers and reduced rates for most applicants per Federal Register notice; former DHS official Adam Klein quoted to Newsweek warning it risks making citizenship less accessible",
            "News Dive \u2014 Trump's proposal seeks to raise citizenship application costs by $570 (June 22, 2026): paper applications rise $760\u2192$1,330, online $710\u2192$1,280; eliminates fee waivers and reduced fees for households at or below 400% of the federal poverty level; military naturalization fee exemptions unchanged; 60-day public comment period; USCIS primarily fee-funded",
            "CNN via NBC Palm Springs \u2014 Trump administration looks to triple fees for some immigration court filings (June 2026): DOJ Executive Office for Immigration Review proposes raising the fee to appeal an immigration judge's decision from $110 to $975, and cancellation-of-removal forms from $100 to more than $300; rule to be published in the Federal Register, effective after public comment",
            "USCIS Naturalization Statistics \u2014 FY 2024 (USCIS, ELIS): top countries of birth for new citizens were Mexico (107,700) and India (49,700), followed by the Philippines (41,200); total naturalizations 818,500; 14.3% of those naturalized in FY2024 had an approved fee waiver, highest among women and applicants 65 and older",
            "Congressional Research Service / Migration Policy Institute \u2014 US naturalization data: India is the second-largest foreign-born population in the US at ~2.8 million; roughly 42% of India-born US residents are not currently eligible for naturalization; eligibility generally requires 5 years as a lawful permanent resident (3 if married to a US citizen)"
        ]),
        "diaspora_angle": "Indians are the second-largest group of new US citizens (49,700 naturalized in FY2024) and the second-biggest foreign-born population at ~2.8 million, so a proposed near-doubling of the naturalization fee and the end of low-income and over-65 waivers lands directly on tens of thousands of Indian green-card holders weighing the final step to a US passport.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: US notifies $482M defense sustainment package for India ─────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: US $482M Apache/M777 sustainment package for India")
    print("="*60)

    slug = "us-notifies-482-million-apache-m777-howitzer-sustainment-india-defense-fms-20260622"
    headline = "Washington Just Cleared $482 Million to Keep India's Apaches and Big Guns Firing — Days Before the Trade Fight Resumes"
    subheadline = "The Pentagon's security agency has formally notified Congress of a sustainment package for India's AH-64E Apache helicopters and M777 howitzers. The defense relationship keeps deepening even as tariffs, a stalled trade deal and the deaths of three Indian sailors strain the wider partnership."

    body = """The United States has formally notified the proposed sale of an estimated $482.2 million in sustainment support and related equipment for two of the Indian military's American-supplied workhorses — its AH-64E Apache attack helicopters and its M777A2 ultra-light howitzers. The notification, issued in the Federal Register on June 17 by the Defence Security Cooperation Agency, which runs the US Foreign Military Sales programme, follows the State Department's May 18 heads-up to Congress that the deals were coming.

The timing is pointed. The clearance lands just as US Trade Representative Jamieson Greer arrives in New Delhi this week for two days of high-stakes trade talks, and against a backdrop of real friction — a 50% tariff that has held up a bilateral trade pact, a US Section 301 probe into India, and diplomatic strain after three Indian sailors were killed in US Navy strikes on commercial ships in the Gulf. The message from Washington is that the security side of the relationship is moving forward even when the commercial side is stuck.

## What's in the Package

These are not new weapons. Both notifications cover sustainment — the unglamorous but essential business of keeping equipment that India already owns combat-ready. The larger of the two, valued at about $230 million, is long-term support for the M777A2 Ultra-Light Howitzers: ancillary items, spare parts, repair-and-return services, training, technical assistance, field service representatives and depot capability. The principal contractor is BAE Systems, whose howitzer line runs through Cumbria in the United Kingdom.

The second package, worth roughly $198.2 million, covers the AH-64E Apaches: engineering, technical and logistics support from the US government and contractors, technical data and publications, and personnel training. Boeing and Lockheed Martin are the named principal contractors. The State Department said the proposed sales would advance American foreign-policy and national-security goals by "strengthening the strategic partnership with India."

Both platforms were chosen for India's hardest terrain. The M777, light enough to be slung under a helicopter, was inducted through the same Foreign Military Sales route specifically to give Indian artillery reach in high-altitude, mountainous theatres — the kind of ground that defines the disputed frontiers with China and Pakistan. The Apache, among the most advanced attack helicopters in service, gives the Indian Army precision strike and battlefield support. Keeping both fleets flying and firing is exactly what a sustainment contract buys.

## A Relationship on Two Tracks

The deal is a reminder that the US-India bond has hardened most where it touches defense. Over the past two decades India has gone from a marginal customer of American arms to one of Washington's significant defense partners, and sustainment packages like this one lock in that dependency for years: once an air force flies Apaches and an army fires M777s, it needs a steady pipeline of American spares, training and technical help to keep them operational.

That deepening sits awkwardly beside the trade picture. India's commerce minister Piyush Goyal said this week that the trade deal "is taking a little longer to sign" because of the tariff dispute, even as he pressed for terms better than those offered to Asian rivals like Vietnam before a July 24 deadline. President Donald Trump, who met Prime Minister Narendra Modi on the sidelines of the G7 in France on June 17, called Modi a "tough negotiator" and, asked about the defense relationship, said the US "would be there to help" if India were attacked. The defense notification is the concrete version of that rhetoric.

## Why the Diaspora Should Care

For the Indian-American community, the US-India strategic partnership is more than geopolitics — it is the framework that shapes everything from H-1B policy to investment flows to how the two governments treat each other's citizens. Diaspora advocacy groups have long pushed Washington and New Delhi closer precisely because a sturdier relationship tends to translate into smoother treatment of the people who move between the two countries.

The defense track has been the partnership's most reliable engine, advancing through tariff spats and diplomatic rows alike. A $482 million sustainment package is modest in dollar terms — it buys spare parts, not squadrons — but it signals continuity at a moment when the headlines are dominated by what is going wrong. As Greer sits down with Goyal this week, the contract is a quiet reminder that the strategic floor under the relationship is holding, even while the commercial ceiling is still being negotiated. For an Indian-origin family watching from Edison or the Bay Area, that floor is what makes the rest of it feel durable."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "AH-64 Apache Indian Air Force",
        "Indian Army M777 howitzer",
        "Boeing AH-64E Apache helicopter",
        "M777 howitzer firing"
    ])
    img_caption = "An AH-64E Apache attack helicopter; the US has notified a $482 million package to sustain India's Apache and M777 howitzer fleets"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("attack helicopter military")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A military attack helicopter; Washington cleared a $482 million sustainment package for India's US-supplied platforms"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The CSR Journal \u2014 US Clears USD 482 Million Support Package for India's Apache Helicopters and M777 Howitzers (June 22, 2026): US formally notified a proposed sale of sustainment support services and associated equipment valued at an estimated $482.2 million; notification issued by the Defence Security Cooperation Agency (DSCA); follows State Department informing Congress on May 18; M777A2 package ~$230M, Apache package ~$198.2M",
            "Elrisala / PTI \u2014 US notifies sale of support services for India's Apache helicopters, M777A2 howitzers (June 2026): DSCA issued the arms sales notification in the Federal Register on June 17; State Department informed US Congress on May 18; India inducted M777A2 howitzers via FMS to bolster artillery in mountainous terrain; Indian Army operates AH-64E Apaches for precision strike",
            "IANS \u2014 US clears $428.2 million military support package for India covering Apache helicopters, M777 Howitzers (May 19, 2026): State Department approved two Foreign Military Sales; M777A2 sustainment ~$230M with BAE Systems as principal contractor; Apache follow-on support ~$198.2M with Boeing and Lockheed Martin; announced via congressional notifications May 18 by Bureau of Political-Military Affairs",
            "Reuters \u2014 India seeks tariff advantage over peers in push to finalise US trade deal (June 22, 2026): USTR Jamieson Greer to visit India Tuesday for two-day talks; follows June 17 Modi-Trump meeting at G7 in France; deaths of three Indian sailors in US Navy strikes on commercial ships in the Gulf added to tensions; India seeking edge over ASEAN rivals before July 24 tariff deadline; Feb agreement set 18% tariffs",
            "Reuters \u2014 Trump says he had good meeting with India's Modi, working on trade deals (June 17, 2026): Trump called Modi a 'tough negotiator'; said the US would defend India \u2014 'If they were attacked, we would be there to help them' \u2014 when asked about the US-India defense relationship",
            "Outlook Business \u2014 US Approves Two Big Defence Deals for India \u2014 But There's a Catch (May 19, 2026): both packages are sustainment, not fresh weapons purchases; $230M M777A2 package (BAE Systems) and $198.2M Apache package (Boeing, Lockheed Martin); designed to keep existing equipment operational and combat-ready"
        ]),
        "diaspora_angle": "The US-India strategic partnership is the framework that shapes H-1B policy, investment and how the two governments treat each other's citizens, and the defense track has been its most reliable engine \u2014 so a $482M sustainment package clearing just as trade talks teeter signals to the diaspora that the strategic floor under the relationship is holding even when the commercial side stalls.",
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
