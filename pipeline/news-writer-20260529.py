#!/usr/bin/env python3
"""News writer for The Videshi — 2026-05-29 evening batch."""

import json, os, re, time, urllib.parse, sys
import requests

# ── Supabase config ──
SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Check image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD fails
        r2 = requests.get(url, timeout=10, stream=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get("Content-Type", "")
        if r2.status_code == 200 and "image" in ct2:
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def sb_insert(table, payload):
    """Insert a row into Supabase."""
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0]
        return data
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
    return None


# ═══════════════════════════════════════════════════════════════
# ARTICLE 1: H-1B $100,000 Fee Court Challenge
# ═══════════════════════════════════════════════════════════════

article1 = {
    "headline": "A Federal Judge Just Asked the Government: Is There Any Limit to What Trump Can Charge for an H-1B Visa?",
    "subheadline": "Only 85 employers have paid the $100,000 fee since September. Now 20 state attorneys general want a court to kill it — and the judge's questions suggest they might have a case.",
    "slug": "federal-judge-h1b-100000-fee-trump-power-limits-states-lawsuit-20260529",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": "2026-05-29T22:30:00Z",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/government/us-judge-questions-scope-trumps-power-impose-100000-h-1b-visa-fee-2026-05-29/"},
        {"name": "ICEF Monitor", "url": "https://monitor.icef.com/"},
        {"name": "U.S. District Court, District of Massachusetts", "url": ""}
    ]),
    "body": """The H-1B visa used to cost an employer somewhere between $2,000 and $5,000. Since September, the price has been $100,000. On Friday, a federal judge in Boston made clear he wants to know whether that number has any legal ceiling at all — or whether the president could set it at a million dollars if he felt like it.

## The Courtroom Exchange That Should Worry Every Indian Tech Worker

U.S. District Judge Leo Sorokin heard arguments in a lawsuit brought by 20 Democratic state attorneys general challenging President Donald Trump's September proclamation that imposed the fee on new H-1B visa applications for highly skilled foreign workers. The program offers 65,000 visas annually, with another 20,000 for workers with advanced degrees.

The numbers tell the story of the fee's impact before any court has ruled on its legality. As of February 15, U.S. Citizenship and Immigration Services had received exactly 85 payments of the $100,000 fee. The previous year, the agency processed tens of thousands of H-1B petitions. The fee has effectively shut the door.

"The effect is to incentivize companies to train up and hire American workers," Tiberius Davis, a lawyer for the U.S. Department of Justice, told the court.

## 'It's a Very Sweeping Power'

Judge Sorokin — appointed by President Barack Obama — pressed Davis on the logical endpoint of the government's argument. If the president can impose a $100,000 fee under his immigration authority, Sorokin asked, could he also impose a $100,000 fee on Americans wanting to marry non-citizens? Could he force a company to forfeit 10 percent of its equity to bring in a single foreign worker?

Davis's answer was striking in its candor: Trump possibly could take those hypothetical actions. "It's a very sweeping power," he said.

The government urged the judge to follow the reasoning of U.S. District Judge Beryl Howell in Washington, D.C., who ruled in a related case brought by the U.S. Chamber of Commerce that Trump's broad immigration powers gave him the authority to impose the fee.

## The States' Counter: This Is a Tax, Not a Fee

James Richardson, representing California, argued that what Trump had really done was impose an unconstitutional tax without Congressional authority. He invoked the Supreme Court's February ruling striking down Trump's sweeping tariffs, arguing it established a precedent: Congress does not delegate taxing authority through ambiguous statutory language.

"Congress does not delegate a tax authority in ambiguous language," Richardson told the court.

The distinction matters. A fee is compensation for a government service. A tax is a revenue-raising measure that only Congress can impose. If the court agrees this is a tax disguised as a fee, the entire $100,000 H-1B proclamation falls.

## What This Means for Indian Americans

Indians account for the overwhelming majority of H-1B visa holders. For years, the visa has been the primary pathway for Indian engineers, software developers, and other skilled professionals to build careers in the United States after graduating from American universities.

The $100,000 fee has already reshaped the landscape. Major technology companies that once filed thousands of H-1B petitions annually have dramatically cut applications. Smaller companies and startups — which relied on H-1B hires but cannot absorb a six-figure fee per worker — have been effectively locked out of the program.

For the roughly 450,000 Indian Americans already on H-1B visas, the fee does not apply to extensions filed from within the country, under updated USCIS guidance from October 2025. But for anyone trying to enter the United States on a new H-1B visa, the economics have become prohibitive.

## What Happens Next

Judge Sorokin did not issue an immediate ruling. The case — State of California et al v. Mullin — is pending in the U.S. District Court for the District of Massachusetts. A decision could come in the coming weeks.

If the judge sides with the states, it would mark the second major judicial rebuke of Trump's use of executive authority to reshape economic policy, following the Supreme Court's tariff ruling in February. If he sides with the government, the $100,000 fee stays — and the precedent it sets for presidential power over immigration fees would have no visible limit.

Either way, the 85 employers who have paid the fee are watching. And so are the tens of thousands who decided it was not worth paying at all.""",
}

# ═══════════════════════════════════════════════════════════════
# ARTICLE 2: Vinesh Phogat Supreme Court Relief
# ═══════════════════════════════════════════════════════════════

article2 = {
    "headline": "Vinesh Phogat Gets Supreme Court Green Light for Asian Games Wrestling Trials After Motherhood Absence",
    "subheadline": "The Supreme Court overruled the Wrestling Federation of India and allowed the 31-year-old to compete in trials starting May 30 — but warned that courts should not become the default referee in sports disputes.",
    "slug": "vinesh-phogat-supreme-court-asian-games-wrestling-trials-motherhood-20260529",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": "2026-05-29T22:35:00Z",
    "sources": json.dumps([
        {"name": "Jan Path News Network", "url": "https://janpathnewsnetwork.digibharatsoft.in/"},
        {"name": "SCC Online", "url": "https://scconline.com/"}
    ]),
    "body": """India's most famous wrestler just won a fight that did not happen on a mat. The Supreme Court on Friday cleared Vinesh Phogat to compete in the selection trials for the 2026 Asian Games, overruling the Wrestling Federation of India's objections and giving her a shot at representing the country in Aichi-Nagoya, Japan this September.

## The Dispute

The controversy began when the WFI imposed eligibility criteria that effectively barred Phogat from the trials. Vinesh, 31, had taken time away from competition following the birth of her daughter — a period during which she was unable to participate in the mandatory ranking tournaments the federation required for trial eligibility.

Phogat challenged the criteria in the Delhi High Court, arguing the rules were arbitrary, discriminatory against athletes returning from maternity, and lacked discretion for exceptional athletes with proven track records. The High Court agreed and directed the WFI to allow her to compete in the trials scheduled for May 30-31 at Indira Gandhi Stadium in New Delhi.

The court also ordered that the trials be video-recorded with independent observers from the Sports Authority of India and the Indian Olympic Association present — an unusual level of judicial scrutiny over a domestic sports selection process.

## WFI Fights Back, Then Loses

The WFI moved the Supreme Court the same day, calling the High Court order "ex facie illegal" and arguing it undermined the federation's authority over its own selection framework. The bench of Justices P.S. Narasimha and Alok Aradhe heard the matter on urgent footing.

But the court sided with Vinesh. Justice Narasimha, while granting relief, added a pointed observation: sports disputes cannot be treated like medical admissions cases, and courts should not become the default mechanism for resolving them. He reminded all parties that the principle of "country first" applied — acknowledging Vinesh's extraordinary record while signaling that this level of judicial intervention in sports governance should be the exception, not the norm.

The matter has been posted for further hearing on June 1.

## A Career Defined by Fighting for the Right to Fight

For Vinesh Phogat, the courtroom has become as familiar as the wrestling ring. She was at the center of India's wrestler protests in 2023, when she and other top athletes accused the then-WFI president Brij Bhushan Sharan Singh of sexual harassment. The protests led to Singh's removal and an overhaul of the federation's leadership.

Then came the Paris Olympics heartbreak. Vinesh was disqualified from the gold medal match in the 50kg category after being found overweight by 100 grams — a margin so small it became a national controversy. She appealed to the Court of Arbitration for Sport for a joint silver medal and lost.

Through it all, Phogat has continued to compete at the highest levels. Her Olympic and World Championship medals make her one of India's most decorated wrestlers regardless of gender. Her return to the mat after motherhood has drawn widespread support from athletes, women's rights advocates, and the general public.

## What It Means for Athletes and Motherhood

The case has implications beyond wrestling. India has no standardized maternity protection policy for elite athletes — no guaranteed pathway back to competition, no mandatory accommodations for returning mothers, and no clear guidelines for how federations should handle eligibility for athletes who take time off for childbirth.

Vinesh's case puts pressure on the Sports Ministry and individual federations to develop such policies. The Supreme Court's intervention, however reluctant, sends a signal: if federations fail to create reasonable accommodation, courts will step in.

## The Trial Begins Tomorrow

Vinesh Phogat will step onto the mat at Indira Gandhi Stadium on May 30 for the women's wrestling trials. A strong performance could send her to the Asian Games in Aichi-Nagoya, where she would compete in the women's freestyle category — potentially the defining chapter of a career that has been as much about institutional resistance as athletic excellence.

All eyes are now on the mat. And on the stopwatch. The 31-year-old has proven, repeatedly, that being told "no" is just the beginning of her argument.""",
}


# ═══════════════════════════════════════════════════════════════
# ARTICLE 3: Indian Americans Win Big in Georgia Primaries
# ═══════════════════════════════════════════════════════════════

article3 = {
    "headline": "Indian Americans Just Won a Wave of Historic Primaries in Georgia. One Will Be the State's First Sikh Elected Official.",
    "subheadline": "Five South Asian candidates won or advanced to runoffs in Tuesday's Georgia primaries — a state with 600,000 Asian American residents that is rapidly becoming a testing ground for Indian American political power.",
    "slug": "indian-americans-georgia-primaries-sikh-elected-official-nabilah-parkes-20260529",
    "category": "nri-world",
    "vertical": "nri-world",
    "status": "published",
    "published_at": "2026-05-29T22:40:00Z",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
        {"name": "Indian American Impact", "url": "https://indianamericanimpact.com/"}
    ]),
    "body": """Georgia just sent a message about the future of Indian American politics, and it was not subtle. In Tuesday's primary elections, five South Asian candidates either won outright or advanced to runoff elections across the state — from the lieutenant governor's race down to state house seats. One of them is poised to become the first Sikh elected official in Georgia history.

## The Wins

The results, confirmed by Indian American Impact, the national political organization that endorsed and supported several of the candidates:

**Nabilah Islam Parkes** advanced to a runoff in the race for lieutenant governor. If she wins the runoff and the general election, she would become the first South Asian and Asian American lieutenant governor nominee from any party in Georgia's history. Parkes, who previously ran for Congress in 2020, has built her campaign around healthcare access, cost of living, and immigrant community protections.

**Jyot Singh** won outright in State House District 97. Singh is on track to become the first Sikh elected official in Georgia — a milestone for a community that has grown significantly in the Atlanta metro area over the past two decades but has had virtually no representation in state government.

**Saira Draper** won a competitive primary for State Senate District 44, adding to the growing bench of South Asian women in Georgia politics.

**Rahul Garabadu** advanced to a runoff in the State Senate District 7 race, a competitive seat that could flip depending on runoff turnout.

**Aisha Yaqoob Mahmood**, already serving in the state legislature, won her primary race comfortably.

## Why Georgia Matters

Georgia is home to more than 600,000 Asian American residents, a population that has grown by over 50 percent in the past decade. The Indian American community, concentrated in the Atlanta suburbs of Gwinnett, Forsyth, and DeKalb counties, has become a significant voting bloc — one that both parties are competing to win.

The state was decided by fewer than 12,000 votes in the 2020 presidential election. In that margin, Asian American voters — and Indian Americans specifically — played a measurable role. Since then, voter registration drives, community organizing, and candidate recruitment efforts by groups like Indian American Impact have accelerated.

"Last night's results in Georgia speak to the growing political power and representation of our communities," said Chintan Patel, Executive Director of Indian American Impact. "Each of these leaders will fight every day to lower costs for working families, protect fundamental freedoms, and fiercely defend immigrant communities."

## The Broader Pattern

Georgia's results are part of a national trend. Indian Americans are running for office at every level of government — from school boards to the U.S. Senate — in numbers that would have been unimaginable a decade ago. The 2024 election cycle saw a record number of Indian American candidates nationwide. The 2026 midterms are on track to break that record again.

What has changed is not just the number of candidates but the infrastructure supporting them. Organizations like Indian American Impact, AAPI Victory Fund, and state-level South Asian political action committees now provide the fundraising, voter contact, and endorsement networks that make campaigns viable.

The candidates themselves reflect the diversity of the community. Jyot Singh is a Sikh running in a suburban district. Nabilah Islam Parkes is a Bangladeshi American progressive running statewide. Saira Draper is an attorney and community organizer. Their campaigns are not built around identity alone — they are running on housing, healthcare, education, and economic issues that affect all Georgians.

## What Comes Next

The runoff elections in Georgia are scheduled for later this summer. Nabilah Islam Parkes's lieutenant governor race will be the highest-profile test — a statewide contest that will determine whether Georgia's growing Asian American electorate can deliver a breakthrough at the executive level.

For the candidates who won outright, the general election in November will be the next hurdle. In Georgia's increasingly competitive political landscape, no seat is safe — but no seat is out of reach either.

The Indian American community in Georgia did not arrive at this moment overnight. It arrived through decades of immigration, community building, business creation, and — now — political candidacy. Tuesday's primaries were not the beginning of that story. But they may be the chapter where it becomes impossible to ignore.""",
}


# ═══════════════════════════════════════════════════════════════
# IMAGE SOURCING + PUBLISHING
# ═══════════════════════════════════════════════════════════════

articles = [
    (article1, ["H-1B visa", "U.S. federal courthouse"], "federal courthouse immigration", "US immigration court visa"),
    (article2, ["Vinesh Phogat", "Vinesh Phogat (wrestler)"], "Indian wrestling competition", "wrestling athlete India"),
    (article3, ["Nabilah Islam Parkes", "Georgia State Capitol"], "Indian American politician Georgia", "South Asian American community"),
]

published = 0

for art, wiki_names, pexels_q, pexels_fallback in articles:
    print(f"\n{'='*60}")
    print(f"Processing: {art['headline'][:70]}...")

    # Image sourcing: Wikipedia first
    img_url = None
    img_attr = None
    for name in wiki_names:
        img_url = fetch_wikipedia_person_image(name)
        if img_url:
            img_attr = "Wikimedia Commons"
            break

    # Fallback to Pexels
    if not img_url:
        img_url = fetch_pexels_image(pexels_q, pexels_fallback)
        if img_url:
            img_attr = "Pexels"

    # Validate
    if img_url and not validate_image(img_url):
        print(f"  ⚠ Image validation failed, skipping image")
        img_url = None

    if img_url:
        art["image_url"] = img_url
        art["image_attribution"] = img_attr
        print(f"  ✓ Image set: {img_url[:80]}...")
    else:
        print(f"  ⚠ No image found — publishing without image")

    # Publish
    result = sb_insert("p2_articles", art)
    if result:
        art_id = result.get("id", "unknown")
        print(f"  ✓ Published: {art['slug']} (id={art_id})")
        published += 1
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
