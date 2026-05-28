#!/usr/bin/env python3
"""News writer for The Videshi — 2026-05-28 evening run."""

import json, os, re, sys, time, uuid, requests, urllib.parse
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

# ── Wikipedia image fetcher ──────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

# ── Pexels image fetcher ─────────────────────────────────────────────────────
def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Uses curl internally (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                src = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if src:
                    print(f"  ✓ Pexels image found for '{q}': {src[:80]}...")
                    return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

# ── Supabase image upload ────────────────────────────────────────────────────
def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage. Returns public URL."""
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15)
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            return None
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return None

        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        ur = requests.post(upload_url, headers=upload_headers, data=r.content, timeout=20)
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: HTTP {ur.status_code} — {ur.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None

# ── Supabase helpers ──────────────────────────────────────────────────────────
def sb_insert(table, data):
    """Insert a row into Supabase."""
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=20)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    print(f"  ⚠ Insert failed: HTTP {r.status_code} — {r.text[:300]}")
    return None

def sb_patch(table, filters, data):
    """Patch a row in Supabase."""
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=data, timeout=20)
    if r.status_code in (200, 204):
        return True
    print(f"  ⚠ Patch failed: HTTP {r.status_code} — {r.text[:300]}")
    return False

# ── Article definitions ──────────────────────────────────────────────────────
articles = [
    {
        "headline": "Rubio Just Committed India to $500 Billion in American Purchases. Reliance Is Building the First U.S. Refinery in 50 Years.",
        "subheadline": "The Secretary of State's four-day India visit produced a trade pledge, a nuclear energy roadmap, and a Texas refinery that will process American shale — all while the Iran war rewrites the global oil map.",
        "slug": "rubio-india-visit-500-billion-deal-reliance-texas-refinery-energy-nuclear-20260528",
        "category": "news",
        "sources": "Reuters, Fox Business, Upstox, U.S. State Department",
        "image_person": "Marco Rubio",
        "image_fallback_query": "US India diplomatic meeting",
        "image_fallback_query2": "oil refinery Texas",
        "body": """Secretary of State Marco Rubio wrapped a four-day visit to India over the weekend with a pledge that would reshape trade between the world's largest and fifth-largest economies: New Delhi has committed to buying $500 billion in American goods over the next five years, with the bulk flowing through energy, technology, and agriculture.

Rubio, who also holds the title of National Security Advisor, met with Prime Minister Narendra Modi and External Affairs Minister S. Jaishankar in New Delhi before heading to a Quad foreign ministers' meeting. Energy dominated the agenda. India imports nearly 88 percent of its crude oil, and more than half of it transits the Strait of Hormuz — the same waterway that has been choked by the Iran conflict since February.

"We want to sell them as much energy as they'll buy," Rubio told reporters in Miami before the trip. "There's a lot to work on with India. They're a great ally, a great partner."

## A Refinery That Changes the Map

The most concrete outcome was not a diplomatic communiqué but a construction project. President Trump announced that Reliance Industries, India's largest privately held energy company, will invest in a $300 billion refinery complex at the Port of Brownsville, Texas — the first new major oil refinery built in the United States in half a century.

"America is returning to REAL ENERGY DOMINANCE," Trump posted on Truth Social. The facility will process 100 percent American shale oil, supply domestic markets, support exports, and generate thousands of jobs in South Texas. Reliance has not yet publicly commented on the announcement, but the deal reflects a deepening strategic calculus: India wants secure energy supply, and the U.S. wants India to stop buying Iranian and Russian crude.

Venezuela recently overtook Saudi Arabia and the United States to become India's third-largest crude supplier — a development that worries Washington. "India cannot be a strategic energy partner for Washington while Indian firms are repeatedly surfacing in sanctions designations involving Iranian energy flows, shadow fleet shipping, and Russian sanctions evasion," said Max Meizlish, a research fellow at the Foundation for Defense of Democracies.

## Nuclear Ambitions

Beyond oil, the visit accelerated nuclear cooperation. India hit a milestone earlier this month when its Prototype Fast Breeder Reactor achieved a self-sustaining stage — making India only the second country after Russia to run a commercial fast-breeder reactor. A 20-member U.S. Executive Nuclear Industry Delegation visited India to explore investment opportunities in small modular reactors and advanced nuclear technologies.

India's Parliament recently passed the SHANTI Bill, which opens the country's civilian nuclear sector to private investment for the first time. The government plans to scale nuclear capacity from 8.8 gigawatts to 100 gigawatts by 2047, creating what officials estimate will be a $300 billion market.

## What It Means for NRIs

For the 4.4 million Indian Americans in the United States, the Rubio visit signals a phase-shift in the bilateral relationship. The energy partnership alone could reshape job markets in Texas, Louisiana, and the Gulf Coast — regions where Indian-American professionals already cluster in the petrochemical and technology sectors.

The $500 billion trade pledge, if fulfilled, would also make the U.S.-India corridor one of the largest bilateral trade relationships in the world, second only to U.S.-China. But the fine print matters. India's track record on defense procurement commitments has been uneven, and the trade pledge is non-binding.

For now, the direction is clear. As U.S. Ambassador Sergio Gor put it: "Big things lie ahead."
""",
    },
    {
        "headline": "India Quarantined Its First Suspected Ebola Patient in a Decade. She Tested Negative.",
        "subheadline": "A 28-year-old Ugandan woman was isolated in Bengaluru after developing symptoms. The scare triggered airport screenings, a travel advisory for three African countries, and the postponement of the India-Africa summit.",
        "slug": "india-ebola-scare-bengaluru-quarantine-ugandan-woman-negative-preparedness-20260528",
        "category": "news",
        "sources": "Reuters, LiveMint, CNN, Devdiscourse, WHO",
        "image_person": None,
        "image_fallback_query": "airport health screening passengers",
        "image_fallback_query2": "medical quarantine hospital isolation",
        "body": """India's first Ebola scare in more than a decade ended with a negative test — but not before it forced the country to confront a global outbreak that the World Health Organisation says is moving at "breakneck speed."

A 28-year-old Ugandan woman, identified as Nagire Latifa, was quarantined at the Epidemic Diseases Hospital in Bengaluru on Wednesday after developing mild body aches. She had arrived in southern India from Ahmedabad, having traveled from East Africa. Samples were sent to the National Institute of Virology in Pune. The results came back negative.

But the incident — which would have been India's first confirmed Ebola case since 2014 — exposed how thin the margin is between a false alarm and a public health crisis.

## A Virus Without a Vaccine

The current outbreak involves the Bundibugyo strain of Ebola, for which no approved vaccine or treatment exists. The WHO has declared it a public health emergency of international concern. As of this week, there have been more than 1,077 suspected cases globally, 121 confirmed, and at least 246 suspected deaths. Congo remains the epicenter, but cross-border spread to Uganda has been confirmed.

Uganda sealed its border with Congo on Tuesday. The United States has imposed travel bans on people arriving from Congo, Uganda, and South Sudan, and is setting up a quarantine facility at Laikipia Air Base in Kenya to isolate exposed American citizens rather than bring them home — a sharp break from precedent during previous outbreaks.

## India's Response

Health Minister Jagat Prakash Nadda had initially said India had no reported cases. Within 24 hours, the Bengaluru quarantine changed that calculus. The government has since activated a multi-layered response:

India's Directorate General of Civil Aviation has issued pandemic-style preparedness guidelines for airlines, requiring them to isolate symptomatic passengers, provide protective gear, and coordinate with airport health authorities. Screening and surveillance measures are now in effect at all international airports and major entry points.

The government has issued travel advisories urging citizens to avoid non-essential travel to Congo, Uganda, and South Sudan. And in the most dramatic signal of concern, the India-Africa Forum Summit scheduled for this week in New Delhi was postponed over public health concerns on the continent.

The Mumbai civic body, BMC MARD, has separately issued alerts to healthcare workers, emphasizing that no vaccine exists, diagnostics are limited, and the fatality rate is high.

## What NRIs Should Know

For Indian Americans with family in Bengaluru, Hyderabad, Mumbai, and other cities with high international traffic, the negative result is reassuring but the broader picture is not. The Bundibugyo strain is less studied than the Zaire strain that drove the 2014 West Africa epidemic, and the WHO has warned that the outbreak is "outpacing" the global response.

India has roughly 800,000 nationals living and working in East and Central Africa. The postponement of the India-Africa summit suggests New Delhi is taking the risk seriously — a notable shift from 2014, when India was slower to activate screening.

The woman in Bengaluru has been placed under a 21-day isolation watch, standard protocol even after a negative result. Her condition remains stable.

If you are planning travel to India or to East Africa, the government's advisory is blunt: avoid non-essential travel to Congo, Uganda, and South Sudan. If you develop symptoms after returning, contact health authorities immediately.
""",
    },
    {
        "headline": "EB-2 India Is Shut for the Year. Green Card Approvals Are Frozen Until October.",
        "subheadline": "The State Department has exhausted all available EB-2 immigrant visas for Indian applicants in FY2026. Final approvals will not resume until the new fiscal year begins on October 1.",
        "slug": "eb2-india-green-card-frozen-fy2026-visa-numbers-exhausted-october-20260528",
        "category": "news",
        "sources": "U.S. State Department, NRI Page, USA Today, VisaHQ",
        "image_person": None,
        "image_fallback_query": "US immigration visa passport stamp",
        "image_fallback_query2": "green card application documents",
        "body": """If you are an Indian professional waiting for an EB-2 green card, the U.S. State Department has a four-month message: wait.

All available Employment-Based Second Preference immigrant visas for applicants chargeable to India have been issued for fiscal year 2026. That means no new EB-2 green cards will be approved for Indian nationals until the fiscal year resets on October 1, 2026.

The announcement, confirmed in the latest visa bulletin, hits a population that has been waiting years — sometimes more than a decade — for permanent residency. The June 2026 Visa Bulletin listed India's EB-2 Final Action Date as September 1, 2013. That is not a typo. Indian professionals filing today are joining a line that stretches back 13 years.

## How the System Works Against Indian Applicants

The EB-2 category covers professionals with advanced degrees or people with exceptional ability in science, business, and the arts. It receives 28.6 percent of all employment-based immigrant visas annually — roughly 40,000 slots. But a separate per-country cap limits how many visas any single nationality can receive.

For India, demand has exceeded supply for two decades. The result is a backlog that the Cato Institute has estimated at over 800,000 applicants, with wait times stretching to 50 years for some categories when family members are included.

The FY2026 exhaustion means even applicants whose priority dates are current cannot receive final approval. Their cases may continue through processing steps — document review, interviews, background checks — but the last step, actual visa issuance, is locked until new numbers become available.

## The Compounding Crisis

This freeze arrives at the worst possible time. The Trump administration announced on May 21 that most green card applicants would need to pursue consular processing abroad rather than adjusting status inside the United States. While USCIS issued a partial clarification on May 26 — stating that H-1B holders may still qualify for in-country adjustment on a case-by-case basis — the combined effect is paralyzing.

Indian H-1B workers now face a triple bind: a 13-year backlog, a new requirement to potentially leave the country to get a green card, and a fiscal-year freeze that stops all EB-2 approvals regardless.

The tech industry, where Indian nationals hold a disproportionate share of H-1B visas, is already responding. Immigration attorneys report a surge in EB-1 filings — the "extraordinary ability" category with shorter backlogs — and an increase in Canadian permanent residency applications. Canada's Express Entry system processes most applications in six months.

## What Changes on October 1

The annual visa limit resets at the start of FY2027. At that point, EB-2 India applicants whose priority dates are eligible may receive final action again — assuming the new fiscal year's allocation is not consumed even faster.

There is no legislative fix on the horizon. The EAGLE Act, which would have eliminated per-country caps, has been introduced in multiple Congressional sessions and has never reached a floor vote. The Fairness for High-Skilled Immigrants Act has had a similar trajectory.

## What You Can Do Now

If your I-140 is approved and your priority date is before September 2013, your case should continue through processing. File any pending documentation — medical exams, affidavits, civil documents — now so you are ready when numbers become available in October.

If you are considering switching to EB-1, consult an immigration attorney about whether your profile qualifies. The "extraordinary ability" threshold is high but not impossible for senior engineers, researchers, and executives.

If you are exploring alternatives, Canada's Express Entry, Australia's skilled migration program, and the UK's High Potential Individual visa all accept applicants with the profile typical of EB-2 India petitioners.

The system was not designed for a country that produces this many qualified applicants. Until Congress changes it, the math will keep producing the same result.
""",
    },
]

# ── Publish ───────────────────────────────────────────────────────────────────
now = datetime.now(timezone.utc).isoformat()

for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"Article {i}: {art['headline'][:60]}...")
    print(f"{'='*60}")

    # Image sourcing
    img_url = None
    img_attribution = "The Videshi"

    if art.get("image_person"):
        img_url = fetch_wikipedia_person_image(art["image_person"])
        if img_url:
            img_attribution = "Wikimedia Commons"

    if not img_url:
        img_url = fetch_pexels_image(art["image_fallback_query"], art.get("image_fallback_query2"))

    # Upload to Supabase storage if we got an image
    final_image_url = None
    if img_url:
        art_id = str(uuid.uuid4())
        filename = f"{art_id}.jpg"
        final_image_url = upload_image_to_supabase(img_url, filename)
    else:
        art_id = str(uuid.uuid4())
        print("  ⚠ No image found — publishing without image (no image > wrong image)")

    # Build article body - trim whitespace
    body = art["body"].strip()

    # Word count check
    word_count = len(body.split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ⚠ BELOW 400 word minimum! Skipping.")
        continue

    # Build the record
    record = {
        "id": art_id,
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": body,
        "category": art["category"],
        "status": "published",
        "published_at": now,
        "sources": art["sources"],
        "image_attribution": img_attribution,
    }

    if final_image_url:
        record["image_url"] = final_image_url

    # Insert
    result = sb_insert("p2_articles", record)
    if result:
        print(f"  ✓ Published: {art['slug']}")
        print(f"    ID: {art_id}")
        if final_image_url:
            print(f"    Image: {final_image_url[:80]}...")
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")

print("\n" + "="*60)
print("Done! Published articles.")
