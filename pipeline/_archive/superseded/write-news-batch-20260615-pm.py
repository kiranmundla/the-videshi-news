#!/usr/bin/env python3
"""
Videshi News Writer - News batch for June 15, 2026 (PM run)
Fresh diaspora-focused immigration stories, deduped against published set.
Articles:
1. EB-2 India green card cap exhausted for FY2026 (no visas until Oct 1)
2. Canada's 2026 Express Entry overhaul (category-based draws, 43% temp visa cut)
3. State Dept $750 expedited B-1/B-2 visa interview pilot (July 1)
"""

import os, json, requests, time, re, urllib.parse
from datetime import datetime, timezone

# Load env
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── Image sourcing functions ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page_id, page in pages.items():
                for ii in page.get("imageinfo", []):
                    mime = ii.get("mime", "")
                    if mime.startswith("image/") and "svg" not in mime:
                        url = ii.get("thumburl") or ii.get("url")
                        if url:
                            results.append({
                                "url": url,
                                "title": page.get("title", ""),
                                "width": ii.get("thumbwidth", ii.get("width", 0)),
                                "height": ii.get("thumbheight", ii.get("height", 0))
                            })
            print(f"  \u2713 Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query, per_page=5):
    """Search Pexels for images."""
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            headers={"Authorization": PEXELS_API_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                best = photos[0]
                url = best["src"]["large2x"]
                print(f"  \u2713 Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def validate_image_url(url):
    """Verify image URL returns 200 and is > 5KB."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  \u2713 Image validated: {cl} bytes, {ct}")
            return True
        else:
            print(f"  \u2717 Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
            if r.status_code == 200 and "image" in ct and cl == 0:
                body = r.content
                if len(body) > 5000:
                    print(f"  \u2713 Image validated (body read): {len(body)} bytes")
                    return True
            return False
    except Exception as e:
        print(f"  \u2717 Image validation error: {e}")
        return False


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=15
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  \u2713 Article inserted: {data[0].get('id', 'unknown')}")
            return data[0]
        print(f"  \u2713 Article inserted (raw): {r.text[:100]}")
        return data
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


def pick_commons_image(query, caption, fallback_pexels_query, fallback_caption):
    """Try Commons first, then Pexels. Returns (url, caption, attribution)."""
    for img in fetch_wikimedia_commons_images(query, 6):
        if validate_image_url(img["url"]):
            return img["url"], caption, "Wikimedia Commons"
    px = fetch_pexels_image(fallback_pexels_query)
    if px and validate_image_url(px):
        return px, fallback_caption, "Pexels"
    return None, "", ""


# ── ARTICLE 1: EB-2 India Green Card Cap Exhausted ──

def write_eb2_article():
    print("\n=== ARTICLE 1: EB-2 India Cap ===")
    image_url, image_caption, image_attribution = pick_commons_image(
        "United States Department of State Harry S Truman Building Washington",
        "The U.S. Department of State, which announced the EB-2 visa allocation for India is exhausted for fiscal 2026",
        "green card united states immigration",
        "A United States permanent resident card on official immigration documents"
    )

    body = """The door has closed for the year. The U.S. State Department, in coordination with U.S. Citizenship and Immigration Services, has confirmed that the entire annual allocation of EB-2 employment-based green cards for Indian nationals has been exhausted for fiscal year 2026. No further EB-2 immigrant visas will be issued to applicants born in India until the new fiscal year begins on October 1, 2026.

For the hundreds of thousands of Indian professionals — software engineers, doctors, researchers, and academics — who have spent years, sometimes a decade or more, waiting in the EB-2 backlog, it is the bluntest possible reminder that the American green card system was never built to absorb the demand India sends it.

## What Has Actually Happened

The EB-2 category covers foreign nationals holding advanced degrees or possessing exceptional ability in the sciences, arts, or business. It is one of the two principal routes — alongside EB-3 — by which Indians on H-1B visas eventually convert temporary work status into permanent residency.

Under the Immigration and Nationality Act, the worldwide employment-based green card ceiling is fixed at roughly 140,000 a year. EB-2 receives 28.6 percent of that total. On top of that sits a second, more punishing limit: no single country may claim more than 7 percent of all employment-based and family-sponsored visas issued in a year. For a country that supplies a vastly disproportionate share of America's skilled-visa workforce, that 7 percent cap is the binding constraint.

In practice, India receives only about 2,800 EB-2 green cards annually — a number wildly out of step with the size of its applicant pool. The State Department's May 22 notice simply formalised the mathematics: the numbers ran out months before the fiscal year did.

"As a result, U.S. embassies and consulates will not issue additional EB-2 visas to applicants from India until the current fiscal year ends," the department said. Eligibility rules themselves are unchanged; there are simply no visa numbers left to assign.

## What It Means for Applicants

The immediate consequences are procedural but painful. Adjustment-of-status applications filed on Form I-485 inside the United States, and consular cases abroad, may remain pending — frozen in place — until fresh numbers become available in October. USCIS will continue to accept filings, but no final approval can be granted while the category sits at "unavailable."

Immigration attorneys are urging affected applicants to keep their underlying status valid and their documentation current during the wait, and to monitor each month's Visa Bulletin closely. The June 2026 bulletin had already signalled the squeeze, with the EB-2 India final action date retrogressing to September 1, 2013 — meaning only those who filed more than twelve years ago were even theoretically in line.

Some practitioners are advising clients to weigh alternative routes. The EB-1A category for individuals of extraordinary ability, the EB-5 investor visa, and concurrent filings are all being discussed more seriously as the EB-2 queue stretches, by some estimates, into multi-decade territory for newer applicants.

## The Structural Problem Nobody Is Fixing

This is not a one-off administrative hiccup. It is, increasingly, the normal operating model of American skilled immigration. The per-country cap was designed in an era when no single nation dominated the applicant pool. India's technology workforce broke that assumption years ago, and Congress has repeatedly failed to pass legislation that would phase out the country caps.

There are flickers of movement. A member of the President's Advisory Commission on Asian Americans, Native Hawaiians and Pacific Islanders, Ajay Bhutoria, has recommended that the government recapture more than 230,000 unused employment-based green cards that went to waste between 1992 and 2025 — visas lost to bureaucratic delay that could be processed over and above the annual ceiling. Separate legislation in Congress would phase out the country quota entirely and capture unused visas for nurses and doctors. Neither has become law.

## Why NRIs Should Care

For the Indian diaspora, the EB-2 exhaustion is more than a statistic — it is a referendum on the predictability of building a life in America. Families who relocated on the promise of an eventual green card now face open-ended uncertainty, with children ageing out of dependent status and careers tethered to employer-sponsored petitions.

It also sharpens a question the diaspora is increasingly asking aloud: whether the United States remains the obvious destination at all. Canada, Australia, and the United Kingdom have been actively courting the same skilled Indian talent. Each fiscal-year freeze makes the alternatives look a little more attractive — and makes the case for reverse migration to a fast-growing India a little louder.

The numbers reset on October 1. But for anyone counting on EB-2 to deliver a green card this decade, the reset only restarts a queue that was already moving in geological time."""

    article = {
        "headline": "America Has Run Out of EB-2 Green Cards for Indians. The Next Ones Come in October.",
        "subheadline": "The State Department says India's entire fiscal-2026 EB-2 allocation is exhausted. No new employment-based green cards will be issued to Indian applicants until October 1 — a freeze that lays bare the per-country cap crushing skilled NRIs.",
        "body": body.strip(),
        "slug": "eb2-india-green-card-cap-exhausted-fy2026-no-visas-until-october-per-country-cap-20260615b",
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "diaspora_angle": "Hundreds of thousands of Indian professionals on H-1B visas depend on EB-2 for their green cards, and the freeze leaves families and careers in open-ended limbo.",
        "sources": json.dumps([
            "U.S. Department of State / travel.state.gov",
            "Berry Appleman & Leiden LLP (BAL)",
            "India-West",
            "Travelobiz",
            "The Indian Eye",
            "June 2026 Visa Bulletin"
        ]),
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ── ARTICLE 2: Canada Express Entry 2026 Overhaul ──

def write_canada_article():
    print("\n=== ARTICLE 2: Canada Express Entry ===")
    image_url, image_caption, image_attribution = pick_commons_image(
        "Parliament Hill Ottawa Canada immigration",
        "Parliament Hill in Ottawa, where Canada sets the immigration policy reshaping its Express Entry system for 2026",
        "Canada flag city skyline",
        "The Canadian flag against a city skyline"
    )

    body = """As one door narrows in the United States, another is being deliberately reshaped to the north. Canada's 2026 immigration plan has rewritten the rules of its flagship Express Entry system, and for the many Indian professionals who treat Canada as a primary alternative to the American green card, the message is stark: the era of broad, volume-driven applications is over.

Ottawa has slashed generic temporary visa allocations by roughly 43 percent and pivoted almost entirely toward targeted, occupation-specific selection. Immigration, Refugees and Citizenship Canada (IRCC) has made category-based draws — not raw ranking scores — the engine of who gets invited to apply for permanent residence.

## From Lottery to Labour Market

For most of its history, Express Entry rewarded candidates who scored highest on the Comprehensive Ranking System (CRS), a points formula based on age, education, language, and work experience. General all-program draws still exist, but IRCC has been explicit that they no longer drive outcomes for most applicants. Occupation, sector, and language ability now carry decisive weight.

Announced by Immigration Minister Lena Metlege Diab on February 18, the 2026 categories sharpen that focus further. Canada has introduced new priority streams for medical doctors with Canadian work experience, researchers, and senior managers in construction, transportation, health, education, and business services. New categories now also cover transport occupations — pilots, aircraft mechanics, and inspectors — and highly skilled military recruits brought in by the Canadian Armed Forces.

IRCC has renewed the categories that were working: French-language proficiency, healthcare and social services, education, trade occupations, and selected STEM roles. Crucially, it has raised the minimum work-experience requirement for renewed categories to one full year, tightening the bar for everyone in the pool.

## Why It Matters for Indian Applicants

Indians have for years been the single largest source of Express Entry invitations, and the diaspora pipeline into Canada — students converting to work permits, IT professionals, nurses, and tradespeople — has been one of the most reliable migration routes out of India. The 2026 restructuring does not close that pipeline, but it does narrow and channel it.

The practical effect is that a strong CRS score is no longer enough. A candidate must now fall squarely inside a targeted category, with the exact occupation codes, verified work experience, and, increasingly, employer backing aligned to a documented provincial labour shortage. Advisory firms working with Indian applicants describe federal reviews that immediately filter out candidates who do not flawlessly match a category-based draw.

For the healthcare and STEM workers who make up a large share of Indian applicants, the news is broadly favourable — those sectors remain explicit priorities. But for the speculative, generalist applicant who once relied on a high score and a bit of patience, the path has effectively closed.

## The Squeeze on Temporary Visas

The deeper structural shift is the 43 percent cut to generic temporary visas. Canada spent the post-pandemic years admitting historically high volumes of temporary residents — international students and temporary foreign workers — and is now, in the government's own framing, "taking back control to return immigration to sustainable levels." That rebalancing hits Indian students and temporary workers first, because they form the largest cohort.

Employer-backed work permits now demand exact alignment with provincial labour shortages and rigorous, verified employer support. The days of submitting standard paperwork and hoping for the best, immigration consultants warn, are gone.

## What NRIs Should Watch

For Indian families weighing North American destinations, the two announcements of mid-2026 — America's EB-2 freeze and Canada's category-based tightening — should be read together. Both countries are signalling that skilled, sector-aligned talent is welcome while generalist, volume-based migration is being squeezed out.

The strategic takeaway for prospective NRIs is to stop thinking in terms of which country is "easier" and start thinking in terms of precise occupational fit. A nurse, a physician, a STEM specialist, or a tradesperson with verifiable Canadian experience is in a stronger position than at almost any point in the past decade. A generalist applicant without a targeted occupation is, in both countries, increasingly out of luck.

Canada's first 2026 draw targeting medical doctors with Canadian work experience was scheduled to take place on or before February 20, a signal of where the invitations — and the opportunities — are now flowing. For the Indian diaspora, the lesson is the same on both sides of the 49th parallel: the future of skilled migration belongs to the specific, not the general."""

    article = {
        "headline": "Canada Has Rewritten Its Immigration Rulebook for 2026. Here Is What It Means for Indians.",
        "subheadline": "Ottawa slashed generic temporary visas by 43 percent and made occupation-based draws the core of Express Entry. For Indian professionals, a high score is no longer enough — only a precise sector fit gets you in.",
        "body": body.strip(),
        "slug": "canada-express-entry-2026-overhaul-category-based-draws-temporary-visa-cut-indian-professionals-20260615b",
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "diaspora_angle": "Indians are the single largest source of Canadian Express Entry invitations, and the 2026 overhaul reshapes the most reliable migration route out of India away from the American green card backlog.",
        "sources": json.dumps([
            "Immigration, Refugees and Citizenship Canada (Canada.ca)",
            "Fragomen, Del Rey, Bernsen & Loewy LLP",
            "Forbes of India",
            "Immigration.ca",
            "Speaking notes of Minister Lena Metlege Diab"
        ]),
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ── ARTICLE 3: $750 Expedited B-1/B-2 Visa Pilot ──

def write_visa_fee_article():
    print("\n=== ARTICLE 3: $750 Expedited Visa Fee ===")
    image_url, image_caption, image_attribution = pick_commons_image(
        "United States visa passport visa stamp",
        "A U.S. visa, the document at the centre of the State Department's new expedited interview pilot",
        "passport visa airport travel",
        "A traveller's passport and travel documents at an airport"
    )

    body = """The wait for a U.S. visitor visa interview can stretch beyond a year at some of the world's busiest consulates. Starting July 1, travellers willing to pay will be able to skip to the front of that line — for an extra $750.

The State Department has unveiled a pilot programme, formalised in a Temporary Final Rule published in the Federal Register on June 9, that creates a "Nonimmigrant Visa Appointment Expedite Fee." Applicants for B-1 and B-2 visas — the business and tourism categories — who pay the fee at participating consular posts will be guaranteed an interview appointment within ten business days, instead of waiting months or, in some cities, years.

## What the Fee Buys

The $750 charge sits on top of the standard $185 nonimmigrant visa application fee, bringing the total to roughly $935. In return, the applicant gets a faster appointment slot and, where available, enhanced options for the return of an approved passport.

What it does not buy is just as important. The State Department has been emphatic that the fee "will not expedite any processing steps, including any time needed for administrative processing," and that it "in no way guarantees visa issuance." Every applicant still faces a full consular interview and the complete security-vetting regime. The money buys a place in the queue, not a verdict.

The programme is deliberately limited. It runs only from July 1 through December 31, 2026, is offered only at a restricted set of posts to be named on travel.state.gov before launch, and is capped in quantity. The State Department projects about 25,705 applicants a year will buy the service, generating roughly $19.3 million in annual revenue.

## The World Cup Connection

The timing is not accidental. The 2026 FIFA World Cup is expected to draw more than a million foreign visitors to American stadiums, with the 2028 Los Angeles Olympics on the horizon. "In the wake of the 2026 FIFA World Cup and ahead of the 2028 Olympic and Paralympic Games in Los Angeles, the Department has determined that now is the time to test the demand for and provision of a new fee-based expedited interview appointment service," the State Department wrote.

The pressure is real. Wait times for B-1/B-2 interviews can reach 16 months in Abu Dhabi, while in Istanbul the next slot is less than half a month away. The disparity is exactly the kind of bottleneck the pilot is designed to relieve — for those who can pay.

## Why It Lands Hard on Indians

For the Indian diaspora, this is not an abstract policy experiment. India consistently generates one of the highest volumes of B-1/B-2 applications in the world, driven by NRIs bringing parents over for visits, weddings, births, and graduations, and by business travellers shuttling between the two economies. Indian consulates have long posted some of the longest visitor-visa wait times anywhere.

That makes the $750 fee a genuine relief valve for a family desperate to get a parent to a grandchild's birth on time — and, simultaneously, a fresh equity problem. As New York immigration attorney Michael Cataliotti put it, $750 "is a lot of money in this country, but it's an exorbitant amount in many of the countries where people are applying for these visas." For a middle-class family in India, the combined $935 outlay per applicant is a serious sum, and a multi-person family trip multiplies it quickly.

## Part of a Wider Pattern

The expedite fee is the latest in a string of changes reshaping how foreigners apply to enter the United States under the second Trump administration. The government now requires visitors from some 50 countries to post bonds of up to $15,000 against overstays, has launched a "Trump Gold Card" offering residence for $1 million, and has introduced a separate $250 "visa integrity fee." Each measure adds cost and friction to the system — and each tilts access further toward those with means.

## What NRIs Should Watch

The practical question for the diaspora is which consular posts in India make the participating list, expected before July 1. If the major posts — New Delhi, Mumbai, Chennai, Hyderabad, Kolkata — are included, the fee could meaningfully shorten the agonising waits that have kept families apart and disrupted business plans.

But it also entrenches a two-tier system in which the speed of seeing your own family in America is, increasingly, a function of what you can afford to pay. For a diaspora that prizes family reunions above almost everything, that trade-off will be felt keenly at kitchen tables from Bengaluru to Edison."""

    article = {
        "headline": "Pay $750 and Skip the U.S. Visa Line. For Indian Families, the New Fee Cuts Both Ways.",
        "subheadline": "From July 1, B-1/B-2 applicants can buy an interview within ten business days for $750 on top of the standard fee. It is relief for families facing year-long waits at Indian consulates — and a new equity problem.",
        "body": body.strip(),
        "slug": "us-state-department-750-expedited-b1-b2-visa-interview-fee-pilot-july-2026-indian-families-20260615b",
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "diaspora_angle": "Indian consulates post some of the world's longest visitor-visa waits, so the expedite fee directly affects NRIs trying to bring parents and family to the US for births, weddings, and graduations.",
        "sources": json.dumps([
            "U.S. Federal Register (Public Notice 13003, RIN 1400-AG13)",
            "USA Today",
            "Washington Examiner",
            "Fox News / Associated Press",
            "Skift",
            "Immigration Analytics"
        ]),
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ── Main ──

if __name__ == "__main__":
    print("Starting Videshi News Writer - News batch (June 15 PM)")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")

    results = []

    r1 = write_eb2_article()
    results.append(("EB-2 India Cap", r1))
    time.sleep(1)

    r2 = write_canada_article()
    results.append(("Canada Express Entry", r2))
    time.sleep(1)

    r3 = write_visa_fee_article()
    results.append(("$750 Expedited Visa", r3))

    print("\n=== SUMMARY ===")
    for name, r in results:
        status = "\u2713 INSERTED" if r else "\u2717 FAILED"
        article_id = r.get("id", "?") if isinstance(r, dict) else "?"
        print(f"  {status}: {name} (id={article_id})")

    print("\nDone.")
