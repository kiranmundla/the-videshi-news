#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# Validate image URL
def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✅ Image valid: {url[:60]}... ({cl} bytes)")
            return True
        else:
            print(f"  ⚠️ Image check failed: status={r.status_code} ct={ct} cl={cl}")
            return False
    except Exception as e:
        print(f"  ❌ Image validation error: {e}")
        return False

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Ontario Just Killed All Nine of Its Immigration Streams. Indians in Canada Have Until Monday to Figure Out What's Next.",
        "subheadline": "The province that receives more Indian immigrants than any other in Canada revoked its entire nominee program framework today — and hasn't said what replaces it.",
        "slug": make_slug("ontario-oinp-nine-streams-revoked-indian-immigrants"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Ontario is Canada's top destination for Indian immigrants — home to Brampton, Mississauga, and the Greater Toronto Area. The Human Capital Priorities stream was the primary Express Entry pathway for Indian IT workers, while the Master's Graduate stream served thousands of Indian international students. With these streams now legally void and no replacement rules published, Indians in the OINP pipeline face immediate uncertainty about their PR applications.",
        "tags": ["canada", "oinp", "ontario", "provincial-nominee", "express-entry", "indian-immigrants"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Ontario.ca – 2026 OINP Updates", "url": "https://www.ontario.ca/page/2026-ontario-immigrant-nominee-program-updates"},
            {"name": "ICC Immigration", "url": "https://iccimmigration.ca/ontario-overhauls-oinp-streams-in-2026-what-it-means-for-canada-pr-applicants/"},
            {"name": "Liberty Immigration", "url": "https://libertyimmigration.ca/breaking-ontario-to-completely-overhaul-all-oinp-immigration-streams-by-may-2026/"},
            {"name": "Moving2Canada", "url": "https://moving2canada.com/oinp-overhauled/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Ontario's immigration program didn't just get reformed today. It got razed.

As of May 30, 2026, all nine streams of the Ontario Immigrant Nominee Program — the province's primary tool for selecting permanent residents — have lost their legal authority. The Human Capital Priorities stream, the Master's Graduate stream, the PhD Graduate stream, the In-Demand Skills stream, the three Employer Job Offer streams, the French-Speaking Skilled Worker stream, the Skilled Trades stream, and the Entrepreneur stream: every one of them is now legally void under amendments to Ontario Regulation 421/17.

The province confirmed the changes in a brief notice posted yesterday on its program updates page. Applications already submitted will be assessed under the old rules. Everything else enters a void.

## What Ontario Says Is Coming — Eventually

The restructuring was authorized under the Working for Workers Seven Act, 2025, which gave Ontario's immigration minister expanded authority to create and dissolve nominee streams on a faster timeline. Stakeholder consultations in late 2025 and early 2026 hinted at a dramatically different architecture: a unified Employer Job Offer stream split into two tiers by skill level, a Priority Healthcare pathway, an Exceptional Talent stream, and a redesigned Entrepreneur program.

None of these have been formally launched. No eligibility criteria have been published. No timelines have been confirmed.

What Ontario has said is that the new system will use more targeted draws — inviting candidates based on specific occupations, wage levels, and regional labor shortages rather than broad intake. The OINP director will have expanded authority to issue tailored invitations, moving the program closer to a federal Express Entry-style selection model.

Employer verification is also getting tighter. Candidates applying under any employer-backed pathway will need their employer to be pre-registered with the OINP before an application can even be submitted — formalizing a portal-based system that had been running informally.

## Why This Matters for Indians

Ontario isn't just any Canadian province for Indian immigrants. It's *the* province.

The Greater Toronto Area — Brampton, Mississauga, Scarborough, and Toronto proper — is home to the largest concentration of Indian-origin residents in Canada. Brampton alone is roughly 55% South Asian. Indians account for the largest share of Ontario's permanent resident intake year after year.

The streams that just disappeared weren't abstractions. The Human Capital Priorities stream was the primary Express Entry-linked pathway for Indian IT professionals — software engineers, data analysts, project managers — looking to convert their Canadian work experience into permanent residency. The Master's Graduate stream was the obvious next step for the thousands of Indian international students who complete degrees at Ontario universities every year. The In-Demand Skills stream served Indian workers in sectors like food processing, agriculture, and construction where demand has consistently outstripped local supply.

All of these are now frozen.

## The Transition Gap

For Indians currently in the OINP Expression of Interest pool, the key question is whether existing profiles will carry over to the new system. Ontario hasn't confirmed. Candidates who spent months optimizing their Comprehensive Ranking System scores, gathering employer documentation, and aligning their occupations with Ontario's priority lists may need to start over if the new streams use different selection criteria.

The timing compounds the uncertainty. Canada's broader immigration landscape is already shifting: federal Express Entry draws have favored category-based selections in healthcare, STEM, and French-language proficiency, and the national Immigration Levels Plan for 2026-2028 cuts overall targets while redirecting volume toward economic categories. Ontario's overhaul adds another variable to an equation that was already getting harder to solve.

For Indian H-1B holders in the United States eyeing Canada as a hedge against America's green card backlog, the calculus just got more complicated. Canada had positioned itself as the stable alternative — the country actively recruiting skilled Indian workers while the US made them wait decades. Ontario's message today is less welcoming: we want you, but on our terms, in our sectors, and we'll tell you the rules when we're ready.

## What to Do Now

Immigration consultants are advising affected candidates to hold their applications and watch Ontario's program updates page closely. Anyone with a pending Expression of Interest should document their current profile and supporting materials in case re-registration is required. Candidates with valid employer job offers should confirm their employer's OINP registration status immediately — the new rules make unregistered employer offers worthless.

The province has said more announcements will follow. For the tens of thousands of Indian nationals whose Canadian futures depend on Ontario's nominee program, the wait just became the entire plan."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Texas Can Now Arrest People for 'Illegal Re-Entry' — Even Green Card Holders. A Federal Court Just Said So.",
        "subheadline": "The Fifth Circuit cleared the way for Texas to enforce SB 4, a state law that treats crossing the border as a state crime and lets local magistrates issue removal orders. One provision applies to lawful permanent residents.",
        "slug": make_slug("texas-sb4-state-immigration-arrests-green-card-holders"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian Americans hold one of the largest pools of US green cards and pending green card applications. Many travel internationally through Texas airports (DFW and Houston IAH are major hubs for India-bound flights). A state law that treats re-entry as a crime even for green card holders, combined with state-level removal authority, creates a new legal risk for Indian permanent residents and their families transiting through or living in Texas.",
        "tags": ["texas", "sb4", "green-card", "state-immigration-enforcement", "fifth-circuit", "indian-americans"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/05/30/federal-appeals-court-allows-red-state-enforce-migrant-arrest-law/"},
            {"name": "Fox 7 Austin", "url": "https://www.fox7austin.com/"},
            {"name": "Courthouse News Service", "url": "https://www.courthousenews.com/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6077447/pexels-photo-6077447.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Immigration enforcement in the United States has always been a federal monopoly. As of Friday, Texas is running a parallel operation.

The U.S. Court of Appeals for the Fifth Circuit issued an order on May 29 clearing the way for Texas to enforce Senate Bill 4, the state law that makes crossing the border without authorization a state criminal offense. The ruling paused a preliminary injunction from U.S. District Judge David Alan Ezra, who had blocked key provisions of the law after finding that two Honduran immigrants faced likely arrest and removal once they took effect.

Governor Greg Abbott called it "a major border security victory." For Indian Americans — particularly the hundreds of thousands holding green cards and the millions more with pending immigration applications — the ruling opens a legal frontier that didn't exist before.

## What SB 4 Actually Does

The law, signed by Abbott in 2023 and the subject of rolling litigation since, creates state-level criminal offenses for immigration violations that were previously handled exclusively by federal authorities. The provisions now cleared for enforcement include:

**State-level re-entry offense.** Crossing into Texas without authorization becomes a state misdemeanor on first offense, escalating to a felony for repeat violations. The provision that should alarm every immigrant in America: it applies to "people now holding green cards or other lawful federal status," according to the Fifth Circuit's description of the reactivated sections.

**State magistrate removal authority.** Texas magistrates — local judicial officers, not federal immigration judges — can issue orders requiring individuals to leave the United States. A separate offense criminalizes refusing to comply with such an order.

**Continued prosecution despite federal proceedings.** Even if a defendant has a pending federal immigration case, Texas magistrates must continue their state prosecution independently.

## The Green Card Problem

The re-entry provision is where SB 4 crosses from border enforcement into something that touches every immigrant with legal status.

A green card holder flying into Dallas/Fort Worth International Airport from Delhi is, by definition, re-entering the United States. So is a permanent resident driving back from a weekend in Cancún through a Texas border crossing. Under a plain reading of the reactivated SB 4 provisions, Texas law enforcement could theoretically treat these entries as state offenses — even though the individuals hold valid federal authorization to live and work in the country permanently.

Whether Texas would actually prosecute green card holders is a different question from whether it legally can. The Fifth Circuit's order didn't address the merits in detail — Judge Leslie Southwick was the lone dissenter, and the brief order "provided no detailed reasoning beyond pausing the prior block." But the mere existence of the authority creates a chilling effect.

## Why Indian Americans Should Pay Attention

The Indian American community has an unusually high stake in this fight, for reasons that have nothing to do with the southern border.

First, Indians represent one of the largest populations of green card holders and green card applicants in the United States. Approximately 1.2 million Indian nationals are in the employment-based green card backlog alone. Many have been living in the US on H-1B visas for a decade or more, and those who have finally received their green cards travel internationally with the assumption that re-entry is routine. SB 4 complicates that assumption in Texas.

Second, Texas is not a state Indian Americans can avoid. DFW and Houston's George Bush Intercontinental are two of the busiest airports in the country for India-bound flights. The Dallas-Fort Worth metroplex and Houston are home to large and growing Indian diaspora communities. Austin's tech corridor employs thousands of Indian-origin workers.

Third, the precedent matters beyond Texas. If a state can criminalize re-entry and authorize local magistrates to issue removal orders — functions that have been exclusively federal since the Immigration and Nationality Act of 1952 — other states will follow. Florida, Iowa, and Oklahoma have already signaled interest in similar legislation.

## The Legal Road Ahead

The Fifth Circuit's order is not a final ruling. It allows enforcement while the underlying appeal plays out, which could take months. The original injunction from Judge Ezra ran 78 pages and found significant constitutional problems with the re-entry provisions. The case will almost certainly reach the Supreme Court, which has previously held — in Arizona v. United States (2012) — that states cannot enact their own immigration enforcement schemes where federal law occupies the field.

But the current Court is different from the one that decided Arizona, and the Trump administration has shown little interest in opposing state-level immigration enforcement. The Department of Justice has not intervened against SB 4.

For Indian green card holders in Texas, the practical advice from immigration attorneys is straightforward: carry your green card and passport at all times, keep copies of your I-551 stamp or approval notice accessible digitally, and be prepared to assert your federal status if stopped. The legal landscape hasn't changed in theory — federal law still governs immigration. In practice, a Texas state trooper with arrest authority under SB 4 may not check the federal register before reaching for handcuffs."""
    },
]

# Validate images
for art in articles:
    print(f"\nValidating image for: {art['headline'][:60]}...")
    validate_image(art["image_url"])

print("\n--- Publishing articles ---\n")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
