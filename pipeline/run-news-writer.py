#!/usr/bin/env python3
"""News writer for The Videshi - May 31, 2026 run"""

import json, os, sys, uuid, re, datetime, time
import requests
from urllib.parse import quote

# Load env from file
env_file = os.path.expanduser("~/.env.supabase")
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            if line.startswith("PEXELS_API_KEY="):
                PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = quote(person_name.replace(' ', '_'))
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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            cmd = f'curl -sS "https://api.pexels.com/v1/search?query={quote(q)}&per_page=5&orientation=landscape" -H "Authorization: {PEXELS_KEY}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate an image URL returns 200 with proper content type and size."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {r.status_code}, {ct}, {cl} bytes")
            return True
        # Try GET if HEAD doesn't give content-length
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            size = 0
            for chunk in r2.iter_content(8192):
                size += len(chunk)
                if size > 5000:
                    print(f"  ✓ Image validated via GET: {size}+ bytes")
                    return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def publish_article(article):
    """Publish an article to Supabase."""
    print(f"\n📝 Publishing: {article['headline']}")
    print(f"   Category: {article['category']}")
    print(f"   Slug: {article['slug']}")
    print(f"   Body length: {len(article['body'].split())} words")

    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article["category"],  # vertical matches category
        "status": "published",
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution"),
        "sources": json.dumps(article.get("sources", [])),
        "published_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=HEADERS,
            json=payload,
            timeout=15
        )
        if r.status_code in (200, 201):
            result = r.json()
            aid = result[0]["id"] if isinstance(result, list) else result.get("id")
            print(f"  ✅ Published! ID: {aid}")
            return True
        else:
            print(f"  ❌ Failed: {r.status_code} - {r.text[:300]}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


# ── ARTICLE 1: India's Military Leadership Reshuffle ──────────────────
def write_article_1():
    print("\n═══ Article 1: Military Leadership Reshuffle ═══")
    
    # Image sourcing - try Anil Chauhan from Wikipedia
    img_url = fetch_wikipedia_person_image("Anil Chauhan")
    img_attr = "Wikimedia Commons"
    if not img_url or not validate_image(img_url):
        img_url = fetch_wikipedia_person_image("Anil Chauhan (general)")
        if not img_url or not validate_image(img_url):
            img_url = fetch_pexels_image("Indian military guard of honour ceremony", "India defense forces")
            img_attr = "Pexels"
            if not validate_image(img_url):
                img_url = None
                img_attr = None

    body = """India's armed forces underwent their most significant leadership transition in years over the weekend, as both the Chief of Defence Staff and the Chief of the Naval Staff retired within hours of each other — and their successors took charge before the country could catch its breath.

General Anil Chauhan, India's second-ever CDS, hung up his boots on Saturday after more than four decades in uniform. His farewell was a solemn affair at the South Block lawns in New Delhi, where he received a tri-services Guard of Honour before laying a wreath at the National War Memorial for the last time as a serving officer.

"It is a matter of great honour to superannuate with such a tribute," Chauhan said, offering what he called a "humble tribute" to those who had laid down their lives in the line of duty.

## A Legacy of Integration

Chauhan took over the CDS post in September 2022, stepping in after the tragic death of India's first CDS, General Bipin Rawat, in a helicopter crash. Over his nearly four-year tenure, he was tasked with one of the most difficult structural reforms in India's military history: integrating the Army, Navy, and Air Force into a more cohesive joint fighting force.

At a recent defence event, Chauhan described joint military structures as one of the "most transformative reforms" India has attempted. He acknowledged the inherent friction between the services but said his approach was deliberately consensus-driven. "I tried to work through consensus," he explained. "Consensus meant taking everyone along and spreading awareness among people."

His tenure saw the release of the Joint Air Defence Doctrine, the creation of the Tri-Services Tele Directory Web Application, and continued progress on the long-debated theatreisation of India's military commands — a process that remains incomplete and will now fall to his successor.

## The Baton Passes

Lieutenant General NS Raja Subramani assumed charge as India's third CDS on June 1, 2026. A decorated Army officer with decades of operational and command experience, Subramani will inherit both the institutional momentum and the unfinished agenda of military integration. His appointment comes at a time when India is navigating an increasingly contested Indo-Pacific, an active naval deployment in the Indian Ocean under Operation Urja Suraksha, and a deepening defence partnership with the United States.

## The Navy Changes Hands Too

Simultaneously, the Indian Navy saw its own leadership transition. Admiral Dinesh K. Tripathi retired on Saturday after just over two years as the 26th Chief of the Naval Staff. "It has been my honour and pleasure to be at the helm of India's Navy — Indian Navy, every Indian's Navy," Tripathi told reporters.

He pointed to the Navy's role during Operation Sindoor and the ongoing Operation Urja Suraksha in the context of the West Asia turmoil as evidence of the service's readiness. "What we have demonstrated as a service is that we are there to protect and promote India's national maritime interests — anytime, anywhere, anyhow," he said.

Admiral Krishna Swaminathan, a specialist in Communication and Electronic Warfare who previously served as Flag Officer Commanding-in-Chief of the Western Naval Command, has taken over as the new Navy Chief. His tenure is expected to run until December 2028, a period that will be critical for the Navy's modernization and its expanding role in securing vital sea lanes.

## What the Diaspora Should Watch

For NRIs tracking India's strategic trajectory, the simultaneous leadership change is more than ceremonial. The new CDS will shape how India projects power across the Indo-Pacific and whether the long-promised integration of its military commands finally becomes operational reality. The new Navy Chief takes charge as the Indian Ocean becomes the world's most contested maritime space — with implications for energy security, trade routes, and the safety of the 3.5 million Indians living in the Gulf region.

The Shangri-La Dialogue in Singapore, which concluded this weekend, offered a preview: US Defence Secretary Pete Hegseth publicly described India as a "powerful" nation with the industrial and logistical capacity for advanced military operations, while India's Defence Secretary held five bilateral meetings in a single day. The new military leadership will determine whether India can convert that diplomatic capital into durable strategic advantage."""

    return {
        "headline": "India Just Replaced Its Top Military Commander and Navy Chief on the Same Day. Here Is What Changes.",
        "subheadline": "General Anil Chauhan retired after four decades in uniform. His successor inherits an unfinished revolution in how India fights wars.",
        "body": body,
        "slug": "india-cds-anil-chauhan-retires-raja-subramani-navy-chief-swaminathan-dual-transition-20260531",
        "category": "news",
        "image_url": img_url,
        "image_attribution": img_attr,
        "sources": ["Ministry of Defence India", "Reuters", "India Sentinels", "Aviation Defence Universe", "The Freedom Press"]
    }


# ── ARTICLE 2: Supreme Court 3-Month Deadline for High Courts ────────
def write_article_2():
    print("\n═══ Article 2: Supreme Court 3-Month Deadline ═══")
    
    # Image sourcing - try Supreme Court of India or CJI Surya Kant
    img_url = fetch_wikipedia_person_image("Surya Kant (judge)")
    img_attr = "Wikimedia Commons"
    if not img_url or not validate_image(img_url):
        img_url = fetch_wikipedia_person_image("Supreme Court of India")
        if not img_url or not validate_image(img_url):
            img_url = fetch_pexels_image("Indian supreme court building", "courtroom justice gavel")
            img_attr = "Pexels"
            if not validate_image(img_url):
                img_url = None
                img_attr = None

    body = """The Supreme Court of India has done something its critics said it would never do: set a hard deadline for High Courts to deliver judgments after reserving them. Three months. Not a suggestion. A mandate.

A bench led by Chief Justice of India Surya Kant, invoking the court's extraordinary powers under Article 142 of the Constitution, issued a sweeping set of directives on Friday aimed at one of the most persistent and quietly devastating failures of the Indian judicial system — the practice of reserving judgments and then taking months, sometimes years, to deliver them.

## The Trigger

The ruling was born from a specific injustice. Four convicts serving life sentences in Jharkhand had their criminal appeals reserved by the Jharkhand High Court in 2022. The judgments were not delivered until three years later. Their petition forced the Supreme Court to confront what it called a "broader institutional concern affecting courts nationwide."

CJI Surya Kant did not mince words. "In my 15 years as a High Court judge, never ever did we reserve a judgment and not deliver it within three months," he said. The court had already, in November 2025, ordered High Courts to submit reports on their judgment timelines — a move that revealed the scale of the problem.

## What the New Rules Require

The guidelines are detailed and enforceable:

**Judgments must be delivered within three months** of being reserved. If a bench fails to meet this deadline, the Registrar General must bring the matter before the Chief Justice of the High Court. The Chief Justice then has two weeks to nudge the bench. If the judgment still does not come, the case may be reassigned to a different bench entirely — a remarkable encroachment on judicial independence that signals just how urgent the court considers the crisis.

**Bail orders must be delivered the same day.** If reserved, they must be pronounced and made public by the following day. The court recognized that for people whose personal liberty hangs in the balance, even a two-day delay is too long.

**Bail and release orders must be communicated to jail authorities immediately**, ensuring that undertrial prisoners are released the same day their bail is granted — or at the very latest, the next day.

**All judgments must be uploaded to High Court websites within 24 hours** of pronouncement. An automated email system must be set up so that the Chief Justice receives a monthly list of all reserved cases, with copies sent to the relevant benches.

## The Scale of the Crisis

The numbers behind the ruling are staggering. India's total case pendency has breached 5.49 crore — that is nearly 55 million unresolved cases across all levels of the judiciary. The 25 High Courts alone account for over 63.6 lakh cases. The Supreme Court itself has approximately 92,385 pending cases.

The crisis has deepened in recent years as digital e-filing, introduced during the pandemic, made it easier to file cases but did not increase the courts' capacity to hear and decide them. The result is a growing gap between input and output that threatens to overwhelm the system.

## Why It Matters for the Diaspora

For NRIs with property disputes, family law cases, business litigation, or inheritance matters pending in Indian courts, the practical impact could be significant. High Court cases that have languished for years with reserved judgments may now face genuine pressure for resolution.

More broadly, the ruling is a test of whether India's judiciary can reform itself from within. Senior advocates in New Delhi acknowledged the significance of the three-month cap but pointed to unfilled judicial vacancies as the deeper structural problem. "The pressure on High Court judges is immense due to unfilled vacancies," a member of the Supreme Court Bar Association said. "However, keeping a judgment reserved for six months to a year dilutes the arguments presented. This deadline will force better judicial discipline."

The Supreme Court was careful to frame its directives as institutional, not personal. "Our directions are not an aspersion on any particular judge or court," the bench noted. But the subtext was unmistakable: a system that makes people wait three years for a judgment it heard in full is a system that has lost the confidence of the people it serves.

The question now is enforcement. India's judiciary has no shortage of well-intentioned circulars and guidelines. What it has lacked is the will to make them stick. The three-month deadline gives CJI Surya Kant's court a chance to prove that this time is different."""

    return {
        "headline": "The Supreme Court Just Set a 3-Month Deadline for High Courts to Deliver Judgments. India Has 5.49 Crore Cases Pending.",
        "subheadline": "Bail orders must now be delivered the same day. If a reserved judgment is not pronounced in 90 days, the case can be reassigned to another bench.",
        "body": body,
        "slug": "supreme-court-3-month-deadline-high-courts-reserved-judgments-bail-same-day-pendency-crisis-20260531",
        "category": "news",
        "image_url": img_url,
        "image_attribution": img_attr,
        "sources": ["LiveLaw", "Bar and Bench", "Dainik Jagran", "Devdiscourse", "Law Trend"]
    }


# ── ARTICLE 3: NYC Mayor Zohran Mamdani's COGE + Bezos ──────────────
def write_article_3():
    print("\n═══ Article 3: Zohran Mamdani COGE + Bezos ═══")
    
    # Image sourcing - try Zohran Mamdani from Wikipedia
    img_url = fetch_wikipedia_person_image("Zohran Mamdani")
    img_attr = "Wikimedia Commons"
    if not img_url or not validate_image(img_url):
        img_url = fetch_pexels_image("New York City Hall government building", "New York City skyline")
        img_attr = "Pexels"
        if not validate_image(img_url):
            img_url = None
            img_attr = None

    body = """New York City's first Indian-origin mayor just launched his own government efficiency commission. Then the world's second-richest man publicly agreed with him. The political alignment between Zohran Mamdani — a self-described democratic socialist — and Jeff Bezos, the founder of Amazon, is as surprising as it is revealing.

Mamdani announced the creation of COGE, the Commission on Government Efficiency, this week, charging it with reviewing the entire New York City Charter to "find ways for our city to work smarter, faster, and more effectively for working people." The commission will hold 10 public hearings across the city, and its proposals could go before voters on the November ballot.

## The Name Is Not an Accident

The acronym invites immediate comparison to DOGE, the Department of Government Efficiency that Elon Musk ran for the Trump administration in early 2025 — a project that led to mass firings of federal workers, cancelled contracts, and slashed services before it was eventually disbanded. Mamdani has been explicit about the distinction.

"Musk manipulated the fact that so many people across this country want to see a government that is more efficient," Mamdani said. "He used that as a justification to simply slash and burn so much of the services that Americans rely on. What we are speaking about is a sincere fulfillment of a vision that city government is operating with the same level of focus that a working-class New Yorker is when they're trying to balance their bills."

COGE will be led by Patrick Gaspard, a former US Ambassador to South Africa and one-time executive director of the Democratic National Committee who also served as president of the Open Society Foundations. Ann Cheng has been proposed as executive director.

## Bezos Weighs In

The endorsement from Jeff Bezos came just days after the two men had clashed publicly. Last week, Bezos appeared on CNBC and told Mamdani to stop "villainizing billionaires," arguing that doubling his tax bill would not help "that teacher in Queens." Mamdani fired back on X: "I know a few teachers in Queens who would beg to differ." The same week, Mamdani's administration announced it had retrieved $9 million from Amazon in unpaid fines for truck pollution violations.

But on COGE, Bezos found common ground. Responding to Mamdani's announcement, Bezos wrote on X: "This is great and they do deserve that. And, with some of the savings, we can zero out taxes on the bottom half of earners. The best way to put money in people's pockets is not to take it out in the first place."

The unlikely alignment underscores a political reality that transcends ideology: government efficiency has become a bipartisan talking point, even if the left and right define it very differently.

## The Diaspora Angle

Zohran Mamdani's ascent to the mayoralty of America's largest city remains one of the most remarkable stories in the Indian diaspora's political history. Born to Ugandan-Indian parents — his mother is the acclaimed filmmaker Mira Nair, known for *Monsoon Wedding* and *The Namesake* — Mamdani grew up straddling continents and cultures. He served in the New York State Assembly before his mayoral win, and has governed with a progressive agenda that includes free buses, universal childcare, and ambitious affordable housing targets.

His willingness to pick fights with billionaires while simultaneously launching efficiency initiatives that billionaires praise reflects a political dexterity that has few parallels in the current crop of American mayors. For Indian Americans watching the political landscape, Mamdani represents something new: not just representation in high office, but the exercise of power in ways that challenge and co-opt the establishment simultaneously.

Senator Marsha Blackburn, a Tennessee Republican, noted the irony. "Remember when Democrats ridiculed President Trump and his administration for tackling government waste?" she said. The fact that a socialist mayor is now embracing the language of efficiency — even while fighting Amazon over pollution fines — suggests the political terrain has shifted in ways that neither party fully controls.

## What Comes Next

COGE's immediate mandate is to identify "outdated bureaucratic barriers that slow infrastructure projects and delay services." Mamdani has already appointed chief savings officers across city agencies, and in March his administration reported savings from technology modernization, space consolidation, and lease management — including the Department of Sanitation vacating unused office space and the Taxi and Limousine Commission cancelling its Slack subscription.

The real test will be whether COGE's recommendations survive the transition from commission report to ballot measure. New Yorkers will have the final say in November. And if Mamdani can prove that government efficiency does not require Musk-style demolition, the model could become a template for progressive governance in American cities — built, in part, by a mayor whose family roots stretch from Kampala to Mumbai to Queens."""

    return {
        "headline": "New York's Indian-Origin Mayor Just Launched His Own DOGE. Jeff Bezos Agreed With Him.",
        "subheadline": "Zohran Mamdani's Commission on Government Efficiency is designed to do what Elon Musk's version never could: make government work without burning it down.",
        "body": body,
        "slug": "zohran-mamdani-nyc-mayor-coge-government-efficiency-bezos-endorsement-diaspora-20260531",
        "category": "news",
        "image_url": img_url,
        "image_attribution": img_attr,
        "sources": ["USA Today", "Fox News", "Bloomberg via 1010 WINS", "Mandatory.com", "Traders Union"]
    }


# ── MAIN ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi News Writer — May 31, 2026")
    print("=" * 60)
    
    articles = [write_article_1, write_article_2, write_article_3]
    
    success_count = 0
    for write_fn in articles:
        article = write_fn()
        # Validate article quality
        word_count = len(article["body"].split())
        if word_count < 400:
            print(f"  ⚠ REJECTED: Body too short ({word_count} words)")
            continue
        if len(article["headline"]) > 200:
            print(f"  ⚠ WARNING: Headline too long ({len(article['headline'])} chars)")
        if len(article.get("subheadline", "")) < 15:
            print(f"  ⚠ REJECTED: Subheadline too short or missing")
            continue
        if article["category"] != "news":
            print(f"  ⚠ REJECTED: Wrong category '{article['category']}'")
            continue
            
        # Check for banned image sources
        img = article.get("image_url", "") or ""
        if any(banned in img for banned in ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat="]):
            print(f"  ⚠ BANNED image source detected, removing image")
            article["image_url"] = None
            article["image_attribution"] = None
        
        if publish_article(article):
            success_count += 1
        time.sleep(1)
    
    print(f"\n{'=' * 60}")
    print(f"✅ Published {success_count}/{len(articles)} articles")
    print(f"{'=' * 60}")
