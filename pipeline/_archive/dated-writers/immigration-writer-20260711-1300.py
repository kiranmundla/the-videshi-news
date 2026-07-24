#!/usr/bin/env python3
"""Immigration writer — 2026-07-11 1:00 PM PT run"""
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

articles = [
    # ─── ARTICLE 1: Federal Judge Blocks USCIS Nationality Discrimination ───
    {
        "id": str(uuid.uuid4()),
        "headline": "A Federal Judge Just Told USCIS It Cannot Penalise Immigrants for Their Nationality",
        "subheadline": "Judge Algenon Marbley's ruling in Ohio blocks the agency from treating country of origin as a 'significant negative factor' when deciding immigration benefits — a practice that courts across the country have now rejected.",
        "slug": make_slug("federal-judge-blocks-uscis-nationality-discrimination-ohio"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals comprise 73% of H-1B holders and the largest share of employment-based green card applicants — any USCIS policy that uses nationality as a negative factor in benefits decisions hits this community harder than any other.",
        "tags": ["uscis", "federal court", "nationality discrimination", "immigration benefits", "h1b", "green card", "administrative procedure act"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Columbus Dispatch", "url": "https://www.dispatch.com/story/news/courts/2026/07/06/trump-uscis-immigration-benefits-policy-blocked-by-federal-judge-in-ohio/90823065007/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/h-1bs-opt-and-h-4-visas-whats-changing-for-indians-under-trumps-immigration-plan"},
            {"name": "Milwaukee Journal Sentinel", "url": "https://www.jsonline.com/story/news/politics/2026/07/10/in-targeting-h-1b-visas-jd-vance-ties-fraud-to-immigration-rhetoric/90855218007/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36984943/pexels-photo-36984943.jpeg",
        "image_caption": "The United States Supreme Court building in Washington, D.C.",
        "image_attribution": "Pexels",
        "body": """The Trump administration has been told, again, that it cannot treat immigrants differently based on where they were born.

U.S. District Judge Algenon Marbley issued a preliminary injunction on July 6 blocking two USCIS policies that had quietly reshaped how the agency processes immigration benefits. The first paused pending applications for people from certain countries. The second directed adjudicators to treat an applicant's nationality as a "significant negative factor" when deciding whether to grant work authorisation, permanent residency, and other immigration benefits.

The ruling, issued from the Southern District of Ohio, is the latest in a growing chain of federal court decisions that have found the same USCIS policies unlawful. Courts in California, Massachusetts, Arkansas, Maryland, Indiana, and Rhode Island have reached similar conclusions.

## What USCIS Was Doing

The challenged policies were not formal regulations. They were internal guidance changes that expanded on President Trump's entry-restriction proclamations — originally designed to control who enters the country — and applied them to people already living and working lawfully in the United States.

Under the policies, USCIS adjudicators were instructed to weigh an applicant's country of origin against them when reviewing benefit applications. In practice, this meant that professionals who had held valid work authorisation for years — a hospital pharmacist, a registered nurse, a cancer researcher, a university professor, engineers — found their renewals and applications indefinitely paused with no explanation.

The 25 plaintiffs in the Ohio case are citizens of Burma, Canada, Iran, Nigeria, Syria, Tanzania, and Venezuela. Their legal argument was straightforward: Congress gave USCIS the authority to process immigration benefits, not to create a nationality-based scoring system on its own.

## The Court's Reasoning

Judge Marbley's 69-page opinion is methodical. The core holding rests on the Administrative Procedure Act: USCIS exceeded its statutory authority by implementing policies that were never authorised by Trump's entry restrictions and never went through the notice-and-comment rulemaking process.

"The question instead is whether USCIS has the legal authority to enact its Challenged Policies in the first place, which is a purely legal question that this Court is well-equipped to address," Marbley wrote.

The administration had argued that the policies were shielded from judicial review because they involved national security. Marbley rejected that outright: "National security cannot be 'a talisman used to ward off inconvenient claims.'"

In a notable section of the opinion, Marbley reviewed public statements made by Trump and Vice President JD Vance during and after the 2024 campaign, including remarks the judge described as expressing "outright hostility toward immigrants" from countries in the Caribbean, South America, Africa, and Asia. He stressed, however, that these statements were "important but not essential" to his conclusion — the legal reasoning stood independently.

## Why This Matters for Indian Americans

The ruling does not mention India or Indian nationals specifically, and none of the plaintiffs are Indian. But the precedent it establishes is directly relevant.

Indians account for approximately 73 percent of H-1B visa holders and a disproportionate share of employment-based green card applicants. Any USCIS policy that introduces nationality as a negative variable in benefits adjudication creates an outsized risk for this population — not because of any wrongdoing, but because of sheer numbers.

The ruling also arrives during a week when the broader immigration enforcement apparatus has escalated sharply. Vice President Vance announced a sweeping H-1B fraud investigation on July 8. The Labor Department's Inspector General has issued dozens of subpoenas. Indian IT services firm Cognizant was named by a whistleblower. And the Unified Regulatory Agenda released by the Departments of Homeland Security, Labor, and State outlines at least six major rule changes — from prevailing wage increases to the elimination of automatic H-4 EAD extensions — expected to take effect in August or shortly after.

Against that backdrop, a federal court reaffirming that USCIS cannot freelance its own nationality-based screening criteria is not abstract. For the Indian professional renewing an H-1B extension, the H-4 spouse waiting on a work permit, or the EB-2 applicant watching the visa bulletin freeze, it is a guardrail.

## The Limits

The injunction is preliminary. It does not permanently strike down the policies or resolve the lawsuit. It bars enforcement against the 25 named plaintiffs while the litigation continues. Trump's travel restrictions and entry proclamations remain in effect.

But the pattern of federal courts reaching the same conclusion — that USCIS overstepped its authority — suggests the administration will face increasing difficulty defending these policies. Judge Marbley cited rulings from at least six other jurisdictions that have already found the same.

For now, the system's answer to "can the government use where you were born against you when deciding your immigration benefits?" is no. The question is how long that answer holds."""
    },

    # ─── ARTICLE 2: Chip Roy Bill Would End STEM OPT and Dual Intent ───
    {
        "id": str(uuid.uuid4()),
        "headline": "A Bill in Congress Would Kill STEM OPT, End Dual Intent, and Ban Post-Layoff H-1B Hiring. Here Is What It Says",
        "subheadline": "Representative Chip Roy's American White-Collar Worker Jobs Act proposes the most sweeping structural overhaul of the H-1B program in its 40-year history — and its timing, during a week of Xbox layoffs and federal fraud probes, is not accidental.",
        "slug": make_slug("chip-roy-bill-stem-opt-dual-intent-h1b-overhaul"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The bill would eliminate STEM OPT — the post-graduation work pathway used by over 360,000 Indian students in the US — and end 'dual intent,' the legal principle that allows H-1B holders to simultaneously pursue green cards, dismantling the career ladder that hundreds of thousands of Indian professionals have built their American lives around.",
        "tags": ["h1b", "stem opt", "dual intent", "chip roy", "immigration reform", "green card", "indian students", "legislation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Office of Rep. Chip Roy", "url": "https://roy.house.gov/media/press-releases/rep-roy-introduces-legislation-end-h-1b-abuse-protect-american-tech-workers"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/h-1b-visa-reform-2026-h-r-9157-wage-based-selection-act/"},
            {"name": "American Bazaar Online", "url": "https://www.americanbazaaronline.com/2026/06/05/american-white-collar-worker-jobs-act-explained/"},
            {"name": "Times of India", "url": "https://timesofindia.indiatimes.com/technology/tech-news/new-bill-by-chip-roy-targeting-h-1bs-seeks-to-end-lottery-opt/articleshow/131354678.cms"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Chip_Roy_118th_Congress.jpg",
        "image_caption": "Representative Chip Roy (R-TX), sponsor of the American White-Collar Worker Jobs Act of 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """There is a bill sitting in the House Judiciary Committee that, if enacted, would fundamentally alter the architecture of employment-based immigration to the United States. It has not attracted the attention of a fraud probe or a Supreme Court ruling, but its provisions are more structurally consequential than either.

H.R. 9157, the American White-Collar Worker Jobs Act of 2026, was introduced by Representative Chip Roy (R-TX) on June 4. It does not tinker with fees or processing times. It proposes to dismantle several of the pillars that Indian professionals and students have relied on for decades to build careers in America.

## What the Bill Would Do

The legislation targets five distinct mechanisms in the current system. Each one, on its own, would constitute a major policy change. Together, they represent a comprehensive reimagining of who gets to work in the United States and on what terms.

**End the H-1B lottery.** The current system selects H-1B recipients by random drawing from the pool of eligible registrations. In fiscal year 2026, approximately 442,000 registrations competed for 85,000 slots — a selection rate near 27 percent. Roy's bill would replace this lottery with a wage-based ranking system. Employers offering the highest salaries relative to the prevailing wage would receive priority. The bill sets a new wage floor at the 75th percentile for the occupation in the specific geographic area. For a software developer in San Francisco, where the current Level I prevailing wage is approximately $134,000, the new floor would be substantially higher.

**Eliminate STEM OPT.** Optional Practical Training allows international students to work in the United States for up to 12 months after graduation, with a 24-month extension available for STEM graduates. India sent 360,000 students to the U.S. in the 2024-25 academic year — the largest single national contingent — and STEM OPT is the primary pathway by which these students gain work experience and transition to H-1B sponsorship. The bill would abolish the programme entirely.

**End dual intent.** Under current law, H-1B visa holders can simultaneously maintain non-immigrant status while pursuing permanent residency — a legal concept known as "dual intent." This is the mechanism that allows an H-1B worker to file for an employment-based green card without jeopardising their visa status. Roy's bill would require H-1B applicants to demonstrate that they maintain a residence abroad and do not intend to abandon it, effectively ending the H-1B-to-green-card pipeline that hundreds of thousands of Indian professionals are currently navigating.

**Ban post-layoff H-1B hiring.** Companies that have recently conducted layoffs would be prohibited from hiring H-1B workers. This provision has gained particular resonance this week: Microsoft announced 4,800 job cuts, including 1,600 from its Xbox division, while holding approval for 2,273 H-1B positions this year. Under the bill, that would be illegal.

**Require domestic recruitment proof.** Employers would need to demonstrate "good-faith efforts" to hire American workers before turning to the H-1B programme — a requirement that goes beyond the current labour condition application, which asks only that the employer attest to paying the prevailing wage.

## The Legislative Context

The bill builds on Representative Eli Crane's (R-AZ) End H-1B Visa Abuse Act of 2026, which proposes a three-year pause on all H-1B visa issuances. Both bills are backed by the Federation for American Immigration Reform (FAIR), the Immigration Accountability Project, and U.S. Tech Workers.

Roy framed the bill in terms that echo the broader political moment. "For its nearly forty-year history, the H-1B visa has been abused, allowing employers to routinely sideline American STEM workers in favour of cheap foreign labour, while masking layoffs and wage suppression as 'shortages,'" he said in a statement.

The bill's introduction on June 4 preceded — but now sits alongside — a flurry of enforcement actions and regulatory proposals. Vice President Vance's July 8 fraud probe announcement, the Unified Regulatory Agenda's package of rule changes expected in August, and the Xbox layoffs controversy have all created a political environment in which restrictionist legislation faces less resistance than it might have a year ago.

## Prospects and Precedent

Immigration reform bills are introduced routinely in Congress. Most die in committee. This one faces the same structural obstacles: a narrowly divided House, a Senate that has shown little appetite for comprehensive immigration legislation, and a president who has pursued restrictions primarily through executive action rather than legislation.

But the bill's individual provisions are worth tracking regardless of its prospects as a whole. Several of them — the wage-based selection system, the domestic recruitment requirement, the post-layoff hiring ban — overlap with regulatory changes the administration is already pursuing through the Unified Agenda. Even if the bill itself does not pass, its provisions may surface as amendments to reconciliation packages or standalone measures.

## What It Means for Indian Professionals

For the Indian student planning to study in the United States, the elimination of STEM OPT would remove the primary bridge between graduation and employment. For the H-1B worker in year three of a green card wait, the end of dual intent would force a choice between maintaining non-immigrant status and pursuing permanent residency — a choice the current system does not require. For the Indian IT consulting firm placing engineers at client sites, the wage-based selection and post-layoff ban would restructure the economics of the staffing model entirely.

None of this is law yet. But the bill is not an abstraction either. It is a detailed, 14-page legislative text with specific provisions that map directly onto the lived experience of Indian professionals in America. Its existence — and the political tailwinds behind it — is worth knowing about before August arrives."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
