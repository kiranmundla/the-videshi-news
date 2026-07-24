#!/usr/bin/env python3
"""Immigration writer — 2026-07-08 19:00 PDT run.
Two fresh analytical pieces not covered in the last 3 days.
"""

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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ─────────────────────────────────────────────────────
# ARTICLE 1: EB-1A Self-Petition Surge
# ─────────────────────────────────────────────────────

art1_body = """For years, the path to a U.S. green card for most Indian professionals ran through a single, narrow corridor: an employer-sponsored petition, an H-1B visa, and a place at the back of a queue that stretches, for many, past the horizon of a working career. The EB-2 India backlog, frozen at a priority date of September 2013 before going fully unavailable in the July 2026 Visa Bulletin, has turned what was designed as a waiting line into something closer to a life sentence.

Now, a growing number of Indian professionals are walking away from that line entirely — and filing their own green card petitions.

## The Numbers Tell the Story

USCIS data shows approximately 7,300 EB-1A Extraordinary Ability petitions were filed in the first quarter of FY2025 alone, a jump of more than 50 per cent from the prior quarter. Full-year filings are tracking nearly 50 per cent higher than the previous year. Filings from India and Nigeria have driven the sharpest increases, while Chinese filings have declined by roughly 40 per cent.

The EB-2 National Interest Waiver has seen an even more dramatic shift — not in filings, but in outcomes. Approval rates have cratered from a pandemic-era peak of 96 per cent in FY2022 to just 55.2 per cent for all of FY2025. In the fourth quarter alone, the rate dropped to 35.7 per cent. The EB-1A approval rate, while more stable, has still eased from its historical 70–75 per cent range to 66.9 per cent for the full year.

The O-1 visa for individuals with extraordinary ability remains the outlier, holding above 90 per cent approval throughout FY2025.

## Why the Pivot Is Happening Now

The math is brutal. Indians who entered the EB-2 employer-sponsored queue a decade ago are still waiting. The July 2026 Visa Bulletin marked EB-2 India as "Unavailable" — no visas will be issued in that category for the rest of the fiscal year. EB-1 India retrogressed to October 2022. Meanwhile, the Trump administration's $100,000 H-1B fee (struck down by a federal judge in June but under appeal), tightening USCIS scrutiny, and the new wage-weighted lottery have made the H-1B path itself more hostile and more expensive.

Self-petitioning through EB-1A or NIW offers a way out of employer dependency. No sponsor is needed. No labour certification. No waiting for a company's immigration counsel to decide your timeline.

"This is not a momentary spike; it is a clear strategic move by global talent, especially Indian professionals, to secure a stable pathway into the U.S. without being dependent on a single employer," Frederick Ng, co-founder of immigration advisory firm Beyond Border, told CXOToday.

## What USCIS Wants to See — and What a Court Just Questioned

The tightening approval rates do not mean USCIS has closed the door. According to analysis by Greenberg Traurig, one of the largest U.S. immigration practices, the agency is applying its frameworks with greater rigour. For NIW cases, adjudicators now demand measurable, demonstrated U.S. impact rather than broad claims about a field's importance. Healthcare, core STEM, and national-security-adjacent work still fares well; vague assertions about "contributing to the tech industry" do not.

For EB-1A, the two-step analysis — first checking whether an applicant meets at least three of ten criteria, then evaluating the overall record — has become more stringent. But in a notable January 2026 ruling, *Mukherji v. Miller*, a federal district court in Nebraska questioned whether USCIS had properly adopted this framework at all. The judge ordered a petition approved after the agency conceded the applicant met five criteria but still denied the case on vague grounds. The ruling is narrow, but immigration attorneys say it provides a new argument for strong cases denied with conclusory reasoning.

USCIS has also quietly expanded what counts as evidence. Product adoption metrics, venture-backed growth, and modern forms of publication — including open-source contributions and industry-standard software adoption — are now explicitly recognised, aligning well with the career profiles of Indian engineers and founders.

## The Dual-Filing Strategy

Immigration lawyers are increasingly advising Indian professionals to file both EB-1A and NIW petitions simultaneously. The logic is straightforward: each creates an independent priority date, and whichever category moves faster can be used for permanent residence. For someone born in India, where EB-2 dates lag EB-1 by over a decade, the EB-1A route can shave years off the wait.

A common playbook: file an EB-2 NIW early to lock in a priority date, maintain status through an O-1A visa (which remains above 90 per cent approval), and build the record needed for an EB-1A petition over the following two to three years. When the EB-1A is approved, the earlier NIW priority date can sometimes be retained.

## What It Means for the Diaspora

The shift represents something larger than a filing trend. For a generation of Indian professionals who built careers in Silicon Valley, Seattle, and Dallas on the assumption that employer sponsorship would eventually lead to permanence, the EB-1A surge is an act of self-determination — an acknowledgement that the system as designed will not deliver in their lifetimes, and that the only viable path forward is one they file themselves.

The irony is sharp. A category created for Nobel laureates and Olympic athletes is now being used by mid-career software architects, AI researchers, and startup founders who have concluded that extraordinary ability is a more realistic path to a green card than simply being very good at a job and waiting in line."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Forget the H-1B Lottery. Indian Professionals Are Filing Their Own Green Cards at Record Rates",
    "subheadline": "EB-1A filings from India have surged more than 50 per cent in a year. Approval rates are tightening, but for thousands of skilled workers, self-petitioning beats waiting decades in the employer-sponsored queue.",
    "slug": make_slug("eb1a-self-petition-surge-indian-professionals-green-card"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals stuck in decades-long green card backlogs are bypassing the employer-sponsored system entirely by self-petitioning through EB-1A and NIW — a strategic shift that could reshape how the diaspora navigates U.S. immigration.",
    "tags": ["eb-1a", "niw", "green-card", "uscis", "self-petition", "h1b", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Mondaq / Greenberg Traurig", "url": "https://www.mondaq.com/unitedstates/work-visas/1801714/what-recent-uscis-data-means-for-eb-2-niw-eb-1a-petitioners"},
        {"name": "CXOToday", "url": "https://cxotoday.com/media-coverage/eb-1a-visa-filings-surge-as-indian-professionals-shift-away-from-h-1b/"},
        {"name": "Boundless Immigration", "url": "https://www.boundless.com/research/uscis-q3-2025-data-eb1a-filings/"},
        {"name": "USCIS Immigration and Citizenship Data", "url": "https://www.uscis.gov/tools/reports-and-studies/immigration-and-citizenship-data"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "An open passport displaying visa stamps at an airport immigration desk",
    "image_attribution": "Pexels",
    "body": art1_body,
}


# ─────────────────────────────────────────────────────
# ARTICLE 2: Dallaspuram Housing Crisis
# ─────────────────────────────────────────────────────

art2_body = """For a decade, the fastest-growing suburbs north of Dallas — Frisco, Prosper, Celina — told an American story that almost wrote itself. Indian-born engineers, drawn by corporate relocations and H-1B visas, bought houses with puja rooms and spice kitchens custom-built by developers who understood their buyers. Collin County's Indian population nearly doubled, from roughly 70,000 to more than 116,000 in five years. The locals called it "Dallaspuram."

The story has stopped writing itself. Home prices in those Collin County suburbs fell nearly 9 per cent year-over-year as of February 2026, double the broader Dallas-Fort Worth decline. Tradition Homes, a luxury builder in the region, has seen its South Asian buyer share collapse from 70 per cent to below 30 per cent. More than 125 high-end properties sit waiting for buyers who are no longer coming.

## The Compounding Crunch

No single policy broke the market. Several hit at once.

The Trump administration imposed a $100,000 fee on new H-1B petitions (struck down by a federal judge in June, but under appeal). USCIS introduced a wage-weighted lottery that disadvantages entry-level and mid-level salaries. The Department of Housing and Urban Development, in May 2025, barred non-permanent residents — including all H-1B holders — from Federal Housing Administration-insured mortgages, closing the primary on-ramp for first-time buyers who lacked the down payment for conventional loans. FHA loans to non-permanent residents went from roughly 6 per cent of originations to nearly zero within months.

Then came the state. In January, Governor Greg Abbott ordered state agencies and public universities to freeze new H-1B petitions. In late April, Attorney General Ken Paxton's office issued civil investigative demands to almost 30 North Texas businesses, probing alleged visa misuse. Texas, which attracted more corporate headquarters relocations than any other state since 2018, was now actively scrutinising the visa programme that staffed them.

And underneath all of it, the tech sector was shedding workers. AI-driven restructuring and cost cuts have sent layoff waves through precisely the companies that sponsored the most H-1B visas.

## The 30-Year Mortgage Versus the 60-Day Clock

For Indian families who already bought, the math is devastating. When an H-1B worker is laid off, they have 60 days to find a new sponsor, change visa status, or leave the country. The mortgage payment, however, does not stop on Day 61.

"We have a 30-year mortgage and a 60-day grace period," one Indian software manager in Dallas told VisaVerge after being laid off in March. "Those two timelines don't match."

Real estate agent Neeraj Gupta told Bloomberg that clients are now calling to sell homes, with some willing to lock in losses or simply hand keys back to lenders on properties worth less than their remaining debt. One homeowner who bought in late 2023 for $895,000 has dropped his asking price to $873,000 and removed religious items from view to attract a broader set of buyers. Another, who financed an $800,000 home almost entirely with debt, now owes more than the property is worth.

## Beyond Dallas

The pattern is not confined to Texas. Northern Virginia suburbs near the Dulles technology corridor, Raleigh's Research Triangle, and Seattle's Eastside — all areas where South Asian professionals concentrate — are experiencing similar softening. Housing Research Center analyst Alex Barron has described South Asians as "the most important first-time buyer group" for builders in fast-growth markets.

Eli Beracha, a Florida International University professor who co-authored a 2025 paper on H-1B housing impacts, warns that the downside effect of an exodus is amplified in suburbs that were built to absorb those buyers. "Housing has already been built for those buyers," he told Propmodo. When they leave, the oversupply is structural, not cyclical.

## The Community Cost

The housing numbers are the most visible symptom, but the community erosion runs deeper. Indian grocery stores, tutoring centres, and places of worship — institutions that grew alongside the population surge — are seeing fewer new members. Local landlords who once had waiting lists for rentals near top-rated school districts report longer listing times and higher turnover. Immigration lawyers in the area say more companies are requiring remote H-1B workers to return to offices, triggering relocations, long commutes, or returns to India.

The tax base that funded new schools and roads during the five-year boom is now at risk.

## What Comes Next

For the Indian professionals still in these suburbs, the calculation has shifted from "when will I get my green card" to "can I afford to stay long enough to find out." Some are pivoting to self-petition routes like the EB-1A, which does not depend on an employer. Others are looking at Canada, the UK, or Germany. A few are going home.

The houses they leave behind — the ones with the custom vastu-compliant layouts and the second kitchens designed for Indian cooking — will eventually find new buyers. But they will not find the same community. Dallaspuram was not just a housing market. It was an ecosystem built on the assumption that skilled immigrants who played by every rule would eventually be allowed to stay. That assumption is no longer safe."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "They Built Suburbs With Puja Rooms and Spice Kitchens. Now the Houses Sit Empty",
    "subheadline": "North Texas boomtowns that Indian H-1B workers turned into thriving enclaves are seeing home prices collapse, buyers vanish, and families face the impossible arithmetic of a 30-year mortgage against a 60-day visa clock.",
    "slug": make_slug("dallaspuram-housing-crisis-indian-h1b-texas-suburbs"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B families who built communities in North Texas suburbs now face plummeting home values, FHA mortgage bans, and the 60-day layoff clock — a crisis that extends to every Indian-heavy tech suburb in the country.",
    "tags": ["housing", "h1b", "dallas", "texas", "fha-mortgage", "indian-community", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Bloomberg / Propmodo", "url": "https://propmodo.com/visa-policy-shifts-trigger-home-price-declines-in-fast-growing-suburbs/"},
        {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/h-1b-layoffs-strain-u-s-homeowners-amid-mortgage-visa-rules/"},
        {"name": "Gulte", "url": "https://www.gulte.com/news/trumps-h-1b-curbs-shake-texas-real-estate/"},
        {"name": "USCIS H-1B Data", "url": "https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8469940/pexels-photo-8469940.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A suburban home with a 'for sale' sign on the front lawn",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ─────────────────────────────────────────────────────
# Insert
# ─────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
