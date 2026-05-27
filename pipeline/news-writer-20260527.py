#!/usr/bin/env python3
"""News writer for The Videshi — 2026-05-27 batch"""

import json
import os
import re
import sys
import time
import uuid
import subprocess
import urllib.parse
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            key = key.replace("export ", "").strip()
            val = val.strip().strip('"').strip("'")
            os.environ[key] = val

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Load Pexels key
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = ""
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                key = key.replace("export ", "").strip()
                val = val.strip().strip('"').strip("'")
                if "PEXELS" in key.upper():
                    PEXELS_KEY = val

import requests

def sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def sb_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=sb_headers(), json=data, timeout=30)
    if r.status_code in (200, 201):
        return r.json()
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None

def sb_patch(table, filters, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filters}"
    r = requests.patch(url, headers=sb_headers(), json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    else:
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
        return False

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    # Validate
                    head = requests.head(url, timeout=10)
                    ct = head.headers.get("Content-Type", "")
                    cl = int(head.headers.get("Content-Length", "0"))
                    if "image" in ct and cl > 5000:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 with image content > 5KB."""
    if not url:
        return False
    try:
        head = requests.head(url, timeout=10, allow_redirects=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = head.headers.get("Content-Type", "")
        cl = int(head.headers.get("Content-Length", "0"))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD
        if "image" in ct:
            r = requests.get(url, timeout=10, stream=True,
                           headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def check_banned_url(url):
    """Check if URL is from a banned source."""
    if not url:
        return True
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ BANNED image source detected: {b}")
            return True
    return False

# ─── ARTICLES ─────────────────────────────────────────────────────────────────

articles = []

# ─── ARTICLE 1: Green Card Process Upended ────────────────────────────────────
articles.append({
    "headline": "Trump Just Ordered Every Green Card Applicant in America to Leave the Country and Reapply From Home",
    "subheadline": "The new rule affects hundreds of thousands of legal immigrants — including an estimated 400,000 Indians in the green card backlog. Immigration lawyers say it could separate families for years.",
    "slug": "trump-green-card-applicants-must-leave-us-apply-from-home-country-20260527",
    "category": "news",
    "vertical": "immigration",
    "sources": json.dumps(["CNN", "Associated Press", "Cato Institute", "Department of Homeland Security"]),
    "person_for_image": "USCIS",  # Not a person article
    "image_search": "US immigration green card passport visa",
    "image_search_fallback": "US passport immigration office",
    "body": """The Trump administration has announced a rule that will upend the lives of hundreds of thousands of legal immigrants living and working in the United States. As of last Friday, anyone applying for a green card — the document that grants permanent residency — must leave the country and complete the application process from their home country.

The policy reverses decades of practice under which immigrants already in the U.S. on valid work or family visas could adjust their status to permanent residency without leaving. Now they must return home, wait for consular processing, and hope to be readmitted — a process that immigration attorneys say can take months to years.

## Who This Hits Hardest

The rule lands squarely on the Indian American community. Indians make up the single largest group in the U.S. green card backlog, with an estimated 400,000 applicants waiting for employment-based green cards alone. Many have been in the queue for over a decade, working on H-1B visas, paying taxes, buying homes, and raising American-born children.

Under the new rule, these workers would have to leave their jobs, uproot their families, and return to India — with no guarantee of a timeline for return. For dual-income households where both spouses hold work authorization tied to a pending green card, the disruption is compounded.

"This is devastating for people who have followed every rule, paid every fee, and waited patiently for years," said David J. Bier, director of immigration studies at the Cato Institute, who described the policy as "illogical" in a detailed analysis of its potential cascading impacts.

## The Administration's Justification

US Citizenship and Immigration Services defended the change. "When aliens apply from their home country, it reduces the need to find and remove those who decide to slip into the shadows and remain in the US illegally after being denied residency," spokesperson Zach Kahler said in a statement.

The agency said exemptions would be available for "extraordinary circumstances," though it did not define what would qualify.

## Legal Challenges Expected

The rule is expected to face immediate legal challenges. Since its announcement, it has drawn a torrent of criticism from immigration attorneys, lawmakers, and advocacy groups across the political spectrum.

New York Governor Kathy Hochul said the policy "betrays the very promise that built this country." California Representative Ted Lieu called it "stupid" and warned it "will help competitors such as China and Russia." Arizona Democrat Greg Stanton said the rule makes "legal immigration harder — on purpose."

The Cato Institute's analysis warned that the policy could trigger a cascade of unintended consequences: employers losing critical workers, housing markets losing buyers, and the U.S. losing its competitive edge in attracting global talent.

## A Pattern of Legal Immigration Restrictions

The green card rule is part of a broader pattern. The administration has already halted refugee admissions for all nationalities except White South Africans, ended Temporary Protected Status for several countries, restricted work and student visas, and proposed making every federal employee sign a non-disclosure agreement.

Last week, the administration announced that H-1B visa registrations dropped 38.5 percent — a decline that immigration experts attribute directly to policy uncertainty and hostile signaling from Washington.

For the estimated 4.4 million Indians living in the United States — the second-largest immigrant community after Mexicans — the cumulative effect of these changes is transforming what it means to build a life in America.

## What Happens Next

Immigration attorneys are advising affected clients to consult legal counsel immediately and not to make any travel decisions before understanding the full scope of the rule and any pending legal challenges.

The rule does not affect naturalized citizens or those who already hold green cards. But for the hundreds of thousands in the pipeline — many of whom have spent the better part of their adult lives in the United States — the question is no longer when they will get their green card. It is whether they can afford to leave everything behind to find out."""
})

# ─── ARTICLE 2: Supreme Court Upholds SIR ─────────────────────────────────────
articles.append({
    "headline": "India's Supreme Court Just Upheld the Government's Power to Purge Voter Rolls. But It Drew One Hard Line.",
    "subheadline": "The court ruled the Election Commission's Special Intensive Revision of electoral rolls is constitutional — but stripped the commission of the power to decide who is and isn't a citizen.",
    "slug": "supreme-court-upholds-sir-electoral-roll-revision-strips-eci-citizenship-power-20260527",
    "category": "news",
    "vertical": "politics",
    "sources": json.dumps(["Supreme Court of India", "LatestLY", "Law Trend", "Dainik Jagran", "DevDiscourse"]),
    "person_for_image": None,
    "image_search": "India Supreme Court building New Delhi",
    "image_search_fallback": "Indian parliament democracy voting",
    "body": """India's Supreme Court delivered a landmark ruling on Wednesday, upholding the Election Commission's controversial Special Intensive Revision (SIR) of electoral rolls — while simultaneously stripping the commission of any authority to determine citizenship status.

The ruling settles a politically explosive legal battle that has raged for months. Opposition parties had challenged the SIR as an unconstitutional overreach that was being used to disenfranchise voters, particularly in states like Bihar and West Bengal where millions of names were removed from voter lists.

## What the Court Said

The Supreme Court ruled that the SIR is "constitutional and legally tenable," affirming the Election Commission's authority under Article 324 of the Constitution and Section 21(3) of the Representation of the People Act, 1950.

"SIR breathes life into the Constitution," the bench observed, emphasizing that the process of cleaning up voter rolls — removing duplicates, deceased voters, and fraudulent entries — is essential for electoral integrity.

In Bihar, the SIR resulted in the removal of 65 lakh (6.5 million) names from voter rolls, a process the commission said was necessitated by rapid urbanization and migration patterns that had left rolls bloated with outdated entries.

The court noted that 99.8 percent coverage was achieved in the Bihar revision, and that the process included Aadhaar as an additional verification tool — a practice it found permissible.

## The Critical Limitation

But the court drew a firm line on one point: the Election Commission cannot decide who is and is not a citizen of India.

This distinction matters enormously. Opposition parties, led by Congress, had argued that the SIR was being used as a backdoor National Register of Citizens (NRC) — a mechanism to strip citizenship from vulnerable populations, particularly Muslims and migrants.

The court ruled that any voter whose name is removed from the roll on grounds related to citizenship must have their case reviewed by the Union Home Ministry within four weeks. Removal from the voter list, the court emphasized, "does not erase citizenship."

This means the Election Commission can clean rolls, verify identities, and eliminate duplicates — but it cannot make the final call on whether someone is Indian.

## The Political Fallout

The ruling was immediately claimed as a victory by both sides.

The BJP welcomed the verdict, with party MP Sudhanshu Trivedi calling it a vindication that exposed the "true character" of the opposition INDIA bloc. "This is a constitutional defeat for those who politicized the integrity of voter rolls," he said.

Congress took a more measured view, acknowledging the constitutional validation of the SIR but pointing to the citizenship limitation as proof that their concerns about overreach were justified.

Activist Yogendra Yadav offered a more skeptical assessment, arguing the ruling was "decided long ago" and that the focus on grievance redressal mechanisms obscured deeper constitutional questions about who controls the definition of Indian citizenship.

## What This Means for NRIs

For Indians living abroad, the ruling has implications for their voting rights. Overseas Indian voters are registered through a separate process, but the SIR framework could theoretically be applied to scrutinize their registrations. The ruling's emphasis on Aadhaar verification also raises questions for NRIs whose Aadhaar cards may have lapsed or been deactivated due to prolonged absence from India.

The Supreme Court's decision is final and cannot be appealed, though specific aspects of SIR implementation in individual states could still be challenged in lower courts.

## The Bigger Picture

The ruling arrives at a charged moment in Indian democracy. With state elections approaching in multiple states and the 2029 general election on the horizon, the integrity of voter rolls has become a front-line political battleground.

The court has tried to thread a needle: affirming the government's power to maintain clean voter rolls while preventing that power from being weaponized to determine who belongs. Whether that distinction holds in practice — in states where political pressure and bureaucratic machinery often blur legal boundaries — remains the unanswered question."""
})

# ─── ARTICLE 3: Atlassian Cuts 1,600 Jobs ─────────────────────────────────────
articles.append({
    "headline": "Atlassian Just Cut 1,600 Jobs and Replaced Its Indian-Origin CTO With an AI-Focused Leader. The Signal Is Clear.",
    "subheadline": "Sri Viswanath built Atlassian's cloud infrastructure. His departure — and the company's pivot to 'next-gen AI talent' — is a warning shot for every Indian engineer in Silicon Valley.",
    "slug": "atlassian-cuts-1600-jobs-indian-cto-sri-viswanath-ai-replacement-20260527",
    "category": "news",
    "vertical": "technology",
    "sources": json.dumps(["Times Now", "Atlassian Inc.", "Reuters", "CryptoBriefing", "Jagranjosh"]),
    "person_for_image": "Sri Viswanath",
    "image_search": "Atlassian software company office",
    "image_search_fallback": "tech company layoffs office",
    "body": """Atlassian, the Australian software giant behind Jira, Confluence, and Trello, has announced it is cutting 1,600 jobs globally — roughly 10 percent of its workforce — as it restructures around artificial intelligence. Among those departing: Chief Technology Officer Sri Viswanath, the Indian-origin executive who built the company's cloud infrastructure over the past several years.

The move sent a clear signal. Atlassian is not just trimming headcount. It is replacing a generation of engineering leadership with executives whose backgrounds are in AI, machine learning, and automation. Investors welcomed the news. The company's stock rose on the announcement.

## The Numbers

Of the 1,600 positions eliminated, approximately 250 are in India, where Atlassian has a significant engineering presence. The company has centers in Bengaluru that handle core product development, not just back-office functions.

Atlassian CEO Mike Cannon-Brookes framed the cuts as a "reshaping" rather than a cost-cutting exercise. "We're reorganizing our teams to build the next generation of AI-powered products," he said in a statement. "This requires different skills and different leadership."

## The CTO Departure

Sri Viswanath's exit is the most symbolically significant part of the restructuring. As CTO, Viswanath led Atlassian's migration from on-premise software to its cloud platform — a multi-year, technically complex transformation that was central to the company's growth story.

But Atlassian's board has decided that the next phase requires a different kind of technical leadership. Viswanath's replacement, whose appointment has not yet been formally announced, is expected to have deep expertise in large language models, AI agents, and the automation of software development itself.

The message is hard to miss: the skills that built cloud infrastructure — distributed systems, database architecture, DevOps pipelines — are no longer the skills that matter most. What matters now is the ability to build AI systems that can do the work those infrastructures were designed to support.

## The Wider Pattern

Atlassian is not alone. Across the global tech industry, companies are simultaneously cutting traditional engineering roles and hiring for AI-specific positions — a phenomenon that has been particularly acute in India.

Cognizant, the Indian-American IT giant, is planning to cut between 4,000 and 15,000 jobs globally under its "Project Leap" restructuring, with a disproportionate impact on its 250,000-strong Indian workforce. The company is investing the savings in AI and automation capabilities.

Standard Chartered announced it would cut 7,800 jobs in its Chennai and Bengaluru operations. CEO Bill Winters described the move not as cost-cutting but as "replacing in some cases lower-value human capital."

A joint report by Nasscom and Indeed found that 40 percent of employers now prefer demonstrable AI skills or certifications over traditional degrees. Another 32 percent give equal weight to both. Puneet Chandok, president of Microsoft India and South Asia, put it plainly: "The biggest challenge is to get the right talent with the right AI skill."

## What This Means for Indian Tech Workers

For the Indian diaspora in tech — and for India's massive IT workforce — the Atlassian restructuring is a case study in the speed of displacement.

The company is not failing. Its products are used by hundreds of thousands of organizations worldwide. Revenue continues to grow. But the nature of the work that drives that revenue is changing faster than the workforce can adapt.

"The zero-to-two-years experience bucket will go away is my assumption in the next few years," said Deena Dayalan, the global head of digital operations at Kimberly Clark, speaking about entry-level hiring at global capability centers in India. A Nasscom-Zinnov report found that 73 percent of HR leaders are flagging a widening skills gap.

For Indian engineers who spent the last decade mastering cloud, microservices, and container orchestration, the lesson from Atlassian is uncomfortable: those skills bought you a seat at the table. They may not keep you there.

## The Reskilling Race

The question now is whether India's tech workforce can reskill fast enough. IBM India head Sandip Patel has called for a "trifecta" approach — industry, government, and academia working together to bridge the gap.

Some GCCs (Global Capability Centers) are investing in internal reskilling programs. Others are partnering with universities to redesign curricula around AI and machine learning. But the pace of change is outrunning these efforts.

India currently houses over 2,100 GCCs employing 2.36 million people and generating roughly $100 billion in revenue. That engine was built on the assumption that India's vast pool of skilled, affordable workers would always be in demand. AI is testing that assumption in real time."""
})

# ─── PUBLISH ──────────────────────────────────────────────────────────────────

for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {art['headline'][:80]}...")
    print(f"{'='*60}")

    # Check for duplicate
    slug_check = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?select=id&slug=eq.{art['slug']}&limit=1",
        headers=sb_headers(), timeout=10
    )
    if slug_check.status_code == 200 and slug_check.json():
        print(f"  ⚠ Slug already exists, skipping: {art['slug']}")
        continue

    # Validate body length
    word_count = len(art["body"].split())
    if word_count < 400:
        print(f"  ✗ Body too short ({word_count} words), skipping")
        continue
    print(f"  ✓ Body: {word_count} words")

    # Image sourcing
    img_url = None

    # 1. Wikipedia for person articles
    if art.get("person_for_image"):
        img_url = fetch_wikipedia_person_image(art["person_for_image"])
        # Try alternate names
        if not img_url and " " in art["person_for_image"]:
            # Try with disambiguation
            for suffix in ["(engineer)", "(businessman)", "(computer scientist)"]:
                img_url = fetch_wikipedia_person_image(f"{art['person_for_image']} {suffix}")
                if img_url:
                    break

    # 2. Pexels fallback
    if not img_url:
        img_url = fetch_pexels_image(art["image_search"], art.get("image_search_fallback"))

    # 3. Validate
    if img_url and check_banned_url(img_url):
        img_url = None
    if img_url and not validate_image(img_url):
        print(f"  ✗ Image validation failed, proceeding without image")
        img_url = None

    # Build record
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    # Determine image attribution
    img_attr = None
    if img_url:
        if "wikipedia" in img_url.lower() or "wikimedia" in img_url.lower():
            img_attr = "Wikimedia Commons"
        else:
            img_attr = "The Videshi"

    record = {
        "id": art_id,
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"],
        "category": art["category"],
        "vertical": art["vertical"],
        "status": "published",
        "published_at": now,
        "sources": art["sources"],
        "image_url": img_url,
        "image_attribution": img_attr,
    }

    result = sb_insert("p2_articles", record)
    if result:
        print(f"  ✓ Published: {art['slug']}")
        print(f"    ID: {art_id}")
        print(f"    Image: {'Yes' if img_url else 'No'}")
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")

print("\n✓ News writer batch complete")
