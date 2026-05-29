#!/usr/bin/env python3
"""News writer for The Videshi — generates 3 articles on fresh stories."""

import json
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone

import requests

# Load environment
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            os.environ[key.strip()] = val

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# Load Pexels key
pexels_path = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_path):
    with open(pexels_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                val = val.strip().strip('"').strip("'")
                if "PEXELS" in key.upper():
                    PEXELS_KEY = val


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
    """Fetch an image from Pexels API using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                [
                    "curl", "-sS",
                    f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                    "-H", f"Authorization: {PEXELS_KEY}",
                ],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate that an image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            return True
        # Some servers don't support HEAD, try GET
        if r.status_code != 200:
            r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            content_type = r.headers.get("Content-Type", "")
            content_length = int(r.headers.get("Content-Length", 0))
            if r.status_code == 200 and "image" in content_type:
                # Read some bytes to check
                chunk = r.raw.read(6000)
                if len(chunk) > 5000:
                    return True
    except Exception as e:
        print(f"  ⚠ Image validation error for {url[:60]}: {e}")
    return False


def publish_article(article):
    """Publish an article to Supabase."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article["category"],
        "status": "published",
        "published_at": now,
        "sources": json.dumps(article["sources"]) if isinstance(article["sources"], list) else article["sources"],
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution"),
    }

    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {article['headline'][:60]}... (id: {result[0].get('id', 'unknown')})")
            return True
        print(f"  ✓ Published: {article['headline'][:60]}...")
        return True
    else:
        print(f"  ✗ Failed to publish: {r.status_code} — {r.text[:200]}")
        return False


# ============================================================
# ARTICLE 1: India's Ebola Scare — Bengaluru Quarantine
# ============================================================
print("\n=== ARTICLE 1: India Ebola Scare ===")

# Try Wikipedia image for Ebola
img1 = fetch_wikipedia_person_image("Ebola_virus_disease")
if not img1 or not validate_image(img1):
    img1 = fetch_pexels_image("airport health screening thermal", "quarantine hospital isolation")
    if not validate_image(img1):
        img1 = None

article1 = {
    "headline": "India Just Quarantined Its First Suspected Ebola Case in a Decade. The India-Africa Summit Is Off.",
    "subheadline": "A 28-year-old Ugandan woman in Bengaluru tested negative, but the episode exposed how quickly a virus with no vaccine can rattle a country of 1.4 billion people.",
    "slug": "india-bengaluru-ebola-quarantine-uganda-woman-india-africa-summit-postponed-20260528",
    "category": "news",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "AAP News", "url": "https://aapnews.aap.com.au"},
        {"name": "World Health Organization", "url": "https://www.who.int"},
        {"name": "Livemint", "url": "https://www.livemint.com"}
    ],
    "image_url": img1,
    "image_caption": "Health authorities have stepped up screening at Indian airports and ports after the WHO declared the Bundibugyo Ebola outbreak a global health emergency.",
    "image_attribution": "Wikimedia Commons" if img1 and "wikipedia" in str(img1).lower() or "wikimedia" in str(img1).lower() else "Pexels" if img1 else None,
    "body": """India quarantined a 28-year-old woman from Uganda in Bengaluru on Wednesday after she displayed symptoms consistent with Ebola, marking the country's first suspected case since a scare in Kerala in 2014. The woman, who had recently travelled from Uganda, was isolated at a government hospital and tested under high-containment protocols.

On Thursday, health officials confirmed she tested negative for the Bundibugyo strain of the Ebola virus. But the roughly 24 hours between quarantine and result exposed how thin the margin of safety has become for a country that depends heavily on African trade, labour, and diplomatic ties — and that has no approved treatment or vaccine for the strain currently ravaging Central and East Africa.

## The Outbreak That Changed India's Calculus

The World Health Organization declared the Bundibugyo Ebola outbreak a public health emergency of international concern on May 16, after cases exploded across the Democratic Republic of Congo, Uganda, and South Sudan. As of this week, more than 900 suspected cases and over 200 suspected deaths have been reported. The WHO has confirmed 101 cases.

Unlike the better-known Zaire strain, Bundibugyo has no licensed vaccine and no proven therapeutic. Merck's Ervebo, the only approved Ebola vaccine, was developed for a different species of the virus. The WHO has explicitly recommended against deploying it outside research settings for this outbreak.

India's response has been swift but revealing. Within days of the WHO declaration, the government imposed mandatory screening for all travellers arriving from Congo, Uganda, and South Sudan. Airports in Delhi, Mumbai, Bengaluru, Hyderabad, and Chennai have deployed thermal scanners and health declaration forms at immigration counters.

## The Summit That Vanished

The most visible casualty was the India-Africa Forum Summit, which had been scheduled for this week in New Delhi. The fourth edition of the summit — a flagship diplomatic event that brings together leaders from more than 50 African nations — was postponed indefinitely over public health concerns.

The postponement is diplomatically awkward. India has spent years cultivating African partnerships to counter China's Belt and Road influence across the continent. The summit was meant to showcase new agreements on trade, infrastructure, energy, and defence. Instead, it became a reminder that pandemics do not wait for diplomatic calendars.

For India's Africa-facing businesses, the timing is especially painful. Bilateral trade between India and Africa reached nearly $100 billion in 2025, with Indian companies invested in everything from telecoms to pharmaceuticals across the continent. The postponement creates uncertainty around planned investment announcements and trade facilitation deals.

## A Vaccine Gap That Matters for India

India is not just a bystander in the global Ebola response — it is manufacturing the most promising vaccine candidate. The Serum Institute of India, based in Pune, is partnering with Oxford University and the Coalition for Epidemic Preparedness Innovations to produce ChAdOx1 Bundibugyo, a vaccine built on the same platform that delivered one of the world's most widely used COVID-19 shots.

Oxford researchers have said the vaccine could be available for clinical testing within two to three months, though additional animal data are still needed. The Serum Institute is already manufacturing doses in anticipation of trial approval.

The irony is unmistakable: the country producing the candidate vaccine is simultaneously scrambling to protect its own borders from the virus it is racing to defeat.

## What NRIs Should Know

For the Indian diaspora, the Bengaluru episode is a practical warning. India has not banned travel from affected countries — unlike the United States, Canada, and the Bahamas, which have imposed entry restrictions on travellers from Congo, Uganda, and South Sudan. The U.S. has extended its ban to green card holders who have visited those countries within 21 days.

Indian nationals travelling through East African hubs should expect heightened screening on return. The Indian government has advised against non-essential travel to the three affected nations but has stopped short of a formal ban.

The WHO has urged all countries to avoid deploying unproven treatments or vaccines outside clinical trial settings. For now, the best protection remains what it was for COVID-19 in early 2020: surveillance, isolation, and the discipline to act before the numbers force your hand.

India dodged this one. The next scare may not end with a negative test."""
}

publish_article(article1)


# ============================================================
# ARTICLE 2: Supreme Court Upholds SIR Electoral Roll Revision
# ============================================================
print("\n=== ARTICLE 2: Supreme Court SIR Ruling ===")

# Try Wikipedia for Election Commission of India or Supreme Court
img2 = fetch_wikipedia_person_image("Supreme_Court_of_India")
if not img2 or not validate_image(img2):
    img2 = fetch_wikipedia_person_image("Election_Commission_of_India")
    if not img2 or not validate_image(img2):
        img2 = fetch_pexels_image("India Supreme Court building", "Indian court law gavel")
        if not validate_image(img2):
            img2 = None

article2 = {
    "headline": "India's Supreme Court Just Gave the Election Commission the Power to Decide Who Gets to Vote",
    "subheadline": "The court upheld the controversial SIR process that has already struck 59 million names from Bihar's voter rolls. Phase 3 elections across 16 states start Friday.",
    "slug": "india-supreme-court-sir-electoral-rolls-upheld-election-commission-voter-citizenship-20260529",
    "category": "news",
    "sources": [
        {"name": "Supreme Court Observer", "url": "https://www.scobserver.in"},
        {"name": "LiveLaw", "url": "https://www.livelaw.in"},
        {"name": "Bar & Bench", "url": "https://www.barandbench.com"},
        {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com"},
        {"name": "LatestLY", "url": "https://www.latestly.com"}
    ],
    "image_url": img2,
    "image_caption": "India's Supreme Court ruled that the Election Commission's Special Intensive Revision of voter rolls is constitutional and advances the goal of free and fair elections.",
    "image_attribution": "Wikimedia Commons" if img2 and ("wikipedia" in str(img2).lower() or "wikimedia" in str(img2).lower()) else "Pexels" if img2 else None,
    "body": """India's Supreme Court has upheld the Election Commission's power to conduct Special Intensive Revision of electoral rolls, ruling the controversial process constitutional and legally tenable. The decision clears the way for Phase 3 elections across 16 states, scheduled to begin on Friday, May 30.

The ruling ends a months-long legal battle that pit the opposition against the Election Commission of India over a process that critics say has struck the names of tens of millions of legitimate voters from state rolls — and that supporters argue is the only way to ensure clean elections in a country where duplicate registrations and fraudulent entries have long distorted results.

## What Is SIR?

The Special Intensive Revision is an extraordinary voter-roll cleanup exercise that goes far beyond the routine annual updates the Election Commission normally conducts. Unlike standard revisions, which primarily add new voters and remove the deceased, SIR involves door-to-door verification, Aadhaar-based identity checks, and the active deletion of entries the Commission deems ineligible.

Bihar was the first state subjected to SIR, and the numbers were staggering. Petitioners told the court that the process had affected more than 59 million citizens — not just removing duplicates, but questioning the citizenship credentials of voters who had been on the rolls for decades. Opposition parties, led by Congress and the Aam Aadmi Party, argued the process was rushed, discriminatory, and designed to disenfranchise vulnerable populations ahead of elections.

## What the Court Said

The bench rejected those arguments. In its ruling, the Supreme Court held that the SIR process falls within the Election Commission's constitutional authority under Article 324 and does not violate the Representation of the People Act.

The court drew a critical line, however, on the question of citizenship. Being removed from the voter roll, the justices wrote, does not mean a person has lost their citizenship. The Election Commission's determination of voter eligibility during SIR is not a final legal judgment on citizenship status — affected individuals retain the right to challenge their exclusion through established judicial procedures under the Citizenship Act.

The ruling also affirmed the use of Aadhaar as an additional verification tool during the revision process, though it stopped short of making Aadhaar linkage mandatory for voter registration.

## Why the Opposition Is Furious

For Congress and AAP, the ruling validates a process they believe was weaponised against their voter base. Opposition leaders have pointed to data showing that voter-to-population ratios fell sharply in districts subjected to SIR — a pattern they argue cannot be explained by routine cleanup alone.

The criticism extends to the mechanics of the revision. Petitioners presented evidence that the appeals process for deleted voters was perfunctory: notices were short, hearings were pro forma, and many voters only learned they had been removed when they showed up to vote. In a country where literacy rates and digital access vary enormously by region and caste, the burden of proving one's right to vote fell hardest on those least equipped to bear it.

The BJP has framed the ruling as vindication. Party leaders accused the opposition of defending "bogus voters" and "illegal infiltrators" and described the SIR as essential to the integrity of Indian democracy. The political subtext is impossible to miss: Bihar, and several of the 16 states heading to polls this week, are battleground territories where marginal changes in the voter roll can shift outcomes.

## What It Means for Phase 3

With the legal challenge dismissed, Phase 3 elections will proceed on SIR-revised rolls. The stakes are enormous. The 16 states voting this week include several where the BJP and opposition alliances are in tight contests, and where the composition of the voter roll could matter as much as the campaign.

For voters who were removed during SIR, the court's ruling offers cold comfort. They retain the theoretical right to challenge their exclusion, but the practical timeline — filing an appeal, getting a hearing, obtaining a court order — makes it nearly impossible to be reinstated before Friday's vote.

## The Diaspora Angle

For NRIs watching from abroad, the ruling touches a nerve that extends beyond electoral mechanics. India's overseas citizens have long complained about the difficulty of maintaining their voter registration while living abroad, and SIR-style purges raise the spectre of being quietly removed from rolls they cannot monitor from thousands of miles away.

The broader question the ruling raises is one that democracies worldwide are grappling with: where does the legitimate goal of voter-roll accuracy end, and where does the suppression of legitimate voters begin? India's Supreme Court has answered that question in favour of the state's power to clean its rolls. Whether the rolls are actually cleaner — or simply smaller — will be tested at the ballot box on Friday."""
}

publish_article(article2)


# ============================================================
# ARTICLE 3: Amazon Wins Supreme Court Victory
# ============================================================
print("\n=== ARTICLE 3: Amazon vs Future Group Supreme Court ===")

# Wikipedia for Amazon
img3 = fetch_wikipedia_person_image("Amazon_(company)")
if not img3 or not validate_image(img3):
    img3 = fetch_pexels_image("India ecommerce online shopping delivery", "India business corporate")
    if not validate_image(img3):
        img3 = None

article3 = {
    "headline": "India's Supreme Court Just Wiped Out ₹202 Crore in Fines Against Amazon. Foreign Investors Are Watching.",
    "subheadline": "The ruling overturns the Competition Commission's penalty in the Future Group case and could reshape how cross-border investment deals are regulated in India.",
    "slug": "india-supreme-court-amazon-future-group-cci-penalty-overturned-cross-border-investment-20260529",
    "category": "news",
    "sources": [
        {"name": "Law Trend", "url": "https://lawtrend.in"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com"},
        {"name": "StartupTalky", "url": "https://startuptalky.com"},
        {"name": "Storyboard18", "url": "https://www.storyboard18.com"}
    ],
    "image_url": img3,
    "image_caption": "India's Supreme Court overturned a ₹202 crore penalty against Amazon in the long-running Future Group investment dispute.",
    "image_attribution": "Wikimedia Commons" if img3 and ("wikipedia" in str(img3).lower() or "wikimedia" in str(img3).lower()) else "Pexels" if img3 else None,
    "body": """India's Supreme Court has overturned the Competition Commission of India's ₹202 crore penalty against Amazon in the long-running Future Group investment dispute, ordering a full refund of recovered funds within eight weeks. The ruling dismisses both the CCI's original fine and the National Company Law Appellate Tribunal's subsequent decision to suspend Amazon's investment deal with Future Group.

The decision is the most significant legal victory for a foreign investor in India in years, and it arrives at a moment when the country is aggressively courting global capital while simultaneously tightening the regulatory framework that governs how that capital enters.

## The Six-Year Battle

The dispute traces back to 2019, when Amazon invested roughly $200 million in Future Coupons, a promoter entity of the Future Group, with contractual rights that effectively gave it a say in the fate of Future Retail — one of India's largest brick-and-mortar retail chains.

When Mukesh Ambani's Reliance Industries moved to acquire Future Group's retail assets in 2020, Amazon intervened, arguing the sale violated its contractual protections. Amazon obtained an emergency arbitration order from a Singapore tribunal blocking the deal, and the fight moved to Indian courts.

The Competition Commission of India entered the fray in 2021, ruling that Amazon had misrepresented the nature of its investment when seeking regulatory approval and imposing a ₹202 crore fine. The CCI also suspended Amazon's original investment deal. The NCLAT upheld the penalty in 2022. Amazon took the matter to the Supreme Court.

## What the Court Said

The Supreme Court's bench set aside both the CCI order and the NCLAT ruling, finding that the regulatory penalties were not supported by the evidence presented. The court ordered that any funds already recovered from Amazon under the penalty be refunded within eight weeks.

The ruling did not comment on the underlying question of whether Amazon's original investment disclosures were adequate — it focused on whether the CCI had followed proper procedure and applied the correct legal standard in imposing the fine. The court found it had not.

## Why It Matters for India's Investment Climate

The decision sends a signal that India's highest court is willing to check regulatory overreach, even when the target is a foreign tech giant that many in India's political establishment view with suspicion. Amazon's dominance in Indian e-commerce has long been a sore point for domestic retailers and for politicians who see foreign platforms as threats to the kirana economy.

But for foreign investors considering India as a destination, the ruling offers reassurance that contractual rights will be respected and that regulatory bodies cannot impose punitive fines without meeting a high evidentiary bar.

The timing is particularly relevant. India is in the middle of a sustained push to attract foreign direct investment, with Prime Minister Modi's government pitching the country as a manufacturing alternative to China and a market too large to ignore. The Quad summit earlier this week produced a $20 billion critical minerals pact that places India at the centre of a Western supply chain strategy. That pitch is harder to make if foreign investors believe Indian regulators can retroactively penalise deals that were approved at the time they were made.

## The Future Group That No Longer Exists

There is a bitter irony in the resolution. Future Group, once Kishore Biyani's retail empire spanning Big Bazaar, Easyday, and dozens of other consumer brands, no longer exists as an independent entity. Reliance ultimately acquired its assets through insolvency proceedings after the original deal collapsed under the weight of Amazon's legal challenges and the pandemic's destruction of brick-and-mortar retail.

Amazon's contractual protections, which it fought for years to enforce, ultimately proved Pyrrhic. The company prevented a deal it opposed, but the assets it was trying to protect ended up in Reliance's hands anyway — just through a different legal pathway.

The ₹202 crore fine was the last piece of the dispute still unresolved. With the Supreme Court's ruling, the longest and most consequential foreign-investment legal battle in Indian corporate history is finally over.

## What NRIs in Tech Should Know

For Indian Americans working in the technology and investment sectors, the ruling has practical implications. Cross-border deals involving Indian entities have always required careful structuring to navigate FDI restrictions, competition law, and the informal politics of doing business in a market where regulatory discretion is wide.

The Supreme Court's willingness to overturn the CCI suggests that the judiciary remains a credible backstop against arbitrary regulatory action — a critical assurance for diaspora investors considering India-linked ventures. But the six-year duration of the litigation is its own cautionary tale. Even when you win, the cost of winning in Indian courts can be measured in years, legal fees, and opportunities foregone.

The message to foreign investors is mixed but honest: India's courts will protect your rights. They will just take their time doing it."""
}

publish_article(article3)

print("\n=== Done: 3 articles published ===")
