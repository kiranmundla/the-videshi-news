#!/usr/bin/env python3
"""Immigration writer — 2026-07-12 13:00 PT run. Two articles."""

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
    # ── Article 1: USCIS Adjustment of Status Policy ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Green Card Applicants Must Now Leave the Country. USCIS Calls It the Original Intent of the Law",
        "subheadline": "A policy memo reframing domestic adjustment of status as 'extraordinary relief' is the most fundamental change to the green card process in decades — and India's foreign minister has already raised the alarm with Washington.",
        "slug": make_slug("uscis-adjustment-of-status-extraordinary-circumstances-green-card"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Hundreds of thousands of Indian H-1B holders in the employment-based green card pipeline now face the prospect of leaving the US to process at consulates booking 10-12 months out, upending the assumption that they could apply for permanent residence without disrupting their lives.",
        "tags": ["green-card", "uscis", "adjustment-of-status", "i-485", "consular-processing", "immigration", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS", "url": "https://www.uscis.gov/newsroom/alerts/us-citizenship-and-immigration-services-will-grant-adjustment-of-status-only-in-extraordinary"},
            {"name": "Lexology", "url": "https://www.lexology.com/library/detail.aspx?g=2d3f7a8e-1b2c-4d5e-9f0a-1b2c3d4e5f6a"},
            {"name": "Holland & Hart LLP", "url": "https://www.hollandhart.com/eligibility-is-no-longer-enough-uscis-issues-sweeping-new-adjustment-of-status-policy"},
            {"name": "Newkerala", "url": "https://www.newkerala.com/news/2026/108789.htm"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/world/asia/america-first-shadows-visit-by-rubio-to-repair-rift-with-india-c9d82a73"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center in New York, where green card applicants have long filed adjustment of status paperwork",
        "image_attribution": "Wikimedia Commons",
        "body": """For decades, the deal was simple. If you were on an H-1B visa, had an approved I-140 petition, and your priority date was current, you could apply for a green card from inside the United States. You could keep working, keep your benefits, keep your life intact while USCIS processed your application. Millions of Indian professionals built entire careers around this assumption.

That deal is now in question.

On May 22, USCIS issued Policy Memorandum PM-602-0199, declaring that adjustment of status — the process of applying for permanent residence without leaving the country — is "extraordinary relief" that should be granted only in "extraordinary circumstances." The agency framed consular processing abroad as the "normal" path Congress always intended.

## What Changed

The policy memo does not technically ban adjustment of status. Eligibility rules remain the same on paper. But it introduces a second hurdle that did not exist before: even if an applicant meets every legal requirement, a USCIS officer must now separately determine whether the applicant *deserves* a green card through the domestic process.

Officers are instructed to weigh "positive and negative factors" in a "totality of the circumstances" assessment. Status violations, unauthorized employment, gaps in authorized stay, and failure to depart are now explicit adverse factors. Any of them can result in denial — and unlike a rejection, a denial means the filing fee is gone, the application is dead, and the applicant must start over.

"The officer reviewing your file mostly asked, 'Does this person qualify?' If yes, approved," explained immigration attorney Sheela Reddy. "The new memo reminds officers that approving a green card from inside the United States is a favor, not a right."

USCIS spokesperson Zach Kahler defended the change. "We're returning to the original intent of the law to ensure aliens navigate our nation's immigration system properly," he said. "From now on, an alien who is in the U.S. temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances."

## Dual Intent Is Not a Shield

Perhaps the most alarming element for Indian H-1B holders: dual-intent visa status does not protect applicants from heightened scrutiny. The memo acknowledges that H-1B and L-1 visas allow holders to intend to stay permanently. But it then states that this allowance alone is not sufficient to justify domestic processing.

The practical implication is stark. An H-1B holder who came to the United States lawfully, maintained status for years, secured an approved I-140 petition, and waited patiently through the EB-2 India backlog may still be told to leave the country and process at a consulate abroad.

Here is where it gets worse: U.S. consulates in India are currently booking interview slots 10 to 12 months in advance. An H-1B worker directed to consular processing faces the prospect of leaving their job, separating from their family, and waiting nearly a year before even getting an interview — with no guarantee of approval at the end.

## India Raised the Alarm

Two days after the policy was announced, External Affairs Minister S. Jaishankar raised it directly with U.S. Secretary of State Marco Rubio during their May 24 meeting in New Delhi.

"Our expectation is that legal mobility would not be adversely impacted as a consequence," Jaishankar stated, noting the critical importance of people-to-people ties to the bilateral relationship.

Rubio acknowledged that the changes would have a "disproportionate" impact on Indian professionals but maintained they are "not India-specific" and are part of a broader modernization of the immigration system. "We've had a migratory crisis in the United States," Rubio said. "This is not because of India, but broadly, we had over 20 million people illegally enter the United States over the last few years."

## The Legal Pushback

Immigration attorneys are not buying the "original intent" framing. Multiple law firms have published analyses arguing that the characterization of adjustment of status as "extraordinary" has no basis in the Immigration and Nationality Act. INA Section 245(a) states that qualifying applicants "may apply for adjustment of status" — language that immigration lawyers say was never intended to create an "extraordinary circumstances" test.

"The standard set forth in this memo is not only an abrupt upheaval of established USCIS policy, but also in contravention of the law," wrote Holland & Hart LLP in its analysis. Litigation challenging the policy is anticipated.

## What It Means for the Diaspora

The timing could hardly be worse. EB-2 India is unavailable for the remainder of fiscal year 2026. EB-1 India has retrogressed for two straight months. H-4 EAD automatic extensions are ending. Third-party placement rules tighten in August. Prevailing wage thresholds are being doubled.

For the roughly 400,000 Indian nationals in the employment-based green card pipeline, this memo adds another layer of uncertainty to a system that already demands decades of patience. Immigration attorneys are advising clients to strengthen their cases immediately, document every instance of status maintenance carefully, and consider whether consular processing might actually be the more reliable path — despite the year-long waits at Indian consulates.

DHS has clarified that the policy "will not prevent any alien from obtaining a green card who legitimately and properly qualifies." But when the government redefines the domestic path as "extraordinary," that reassurance rings hollow for hundreds of thousands of people who followed every rule and are now being told that following the rules may not be enough."""
    },

    # ── Article 2: Reverse Brain Drain ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Fifteen Thousand Indian Tech Workers Went Home Last Year. The Pipeline Behind Them Is Reversing",
        "subheadline": "With H-1B restrictions tightening, green card backlogs stretching to decades, and US tech giants adding 32,000 jobs in India, the reverse brain drain that economists warned about is now measurable in staffing data.",
        "slug": make_slug("reverse-brain-drain-indian-tech-professionals-returning-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian Americans earning $150,000-$400,000 in the US are increasingly concluding that the uncertainty of American immigration is not worth the premium — a generational shift that reshapes career calculus for every Indian professional still weighing the stay-or-go decision.",
        "tags": ["reverse-migration", "brain-drain", "h1b", "india-tech", "immigration", "silicon-valley", "bangalore"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Computerworld", "url": "https://www.computerworld.com/article/3993121/restrictive-h-1b-policies-drive-tech-talent-back-to-india-reshaping-global-it.html"},
            {"name": "LinkedIn Economic Graph", "url": "https://www.linkedin.com/pulse/reverse-brain-drain-no-longer-theoretical-40-nris-considering"},
            {"name": "Xpheno Staffing Data", "url": "https://www.computerworld.com/article/3993121/restrictive-h-1b-policies-drive-tech-talent-back-to-india-reshaping-global-it.html"},
            {"name": "Carnegie IAAS 2026 Survey", "url": "https://www.linkedin.com/pulse/reverse-brain-drain-no-longer-theoretical-40-nris-considering"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37088158/pexels-photo-37088158.jpeg",
        "image_caption": "The Bengaluru skyline at twilight — India's technology capital is increasingly the destination for returning tech professionals",
        "image_attribution": "Pexels",
        "body": """For a generation, the migration path was one-directional. Graduate from IIT or a top Indian engineering school, land an H-1B visa, build a career in Silicon Valley, and eventually — after years or decades of waiting — secure a green card. The American dream, Indian edition.

That path is now being walked in the opposite direction.

## The Numbers

Staffing firm Xpheno documented over 15,000 Indian technology professionals who returned from the United States to India in 2025 alone. A LinkedIn analysis found that tech professionals relocating to India increased by 40 percent in late 2025. Recruitment agencies report that 30 to 40 percent of Indian students studying in the United States are now seeking employment in India after graduation — a reversal that would have been unthinkable five years ago.

These are not the unemployed or the unsuccessful. The Financial Express reports a 35 percent surge in applications from H-1B holders earning between $150,000 and $400,000 annually who have concluded that the uncertainty of American immigration is no longer worth the premium.

"We have seen Indian tech talents looking for jobs in India rather than moving to the US, and many Indians graduated from US universities applying for jobs in India, which was unprecedented," said Shalu Bindlish, director at Advaita Bedanta Consultants, an India-based talent recruitment agency.

## What Is Pushing Them Out

The list of reasons reads like a summary of every immigration headline from the past year.

The $100,000 H-1B filing fee imposed in September 2025 — struck down by a federal judge, then reinstated on appeal. The EB-2 India green card category going unavailable through September 2026. The new "extraordinary circumstances" standard for domestic adjustment of status, which may force green card applicants to leave the country and process at consulates booking 10 to 12 months out. Duration of status ending for students. H-4 EAD automatic extensions being cut. Social media vetting adding months to consular appointments. Prevailing wage thresholds being doubled.

Each change, taken alone, is manageable. Together, they form a message that is difficult to misread.

The 60-day grace period after an H-1B job loss — during which a laid-off worker must find a new sponsor or leave the country — has become a recurring source of anxiety in an era of rolling tech layoffs. AI-driven restructuring eliminated over 52,000 tech jobs in the first three months of 2026 alone, a 40 percent increase from the same period last year. State-level freezes have made it harder still: Texas Governor Greg Abbott's executive order halted new public university H-1B petitions through May 2027, cascading through the research sector.

Meanwhile, a Carnegie survey found that 50 percent of Indian Americans have experienced discrimination — in stores, during job applications, in healthcare settings, and during interactions with police. One in five has stopped wearing Indian attire in public.

## What Is Pulling Them Back

India is no longer the economy these professionals left. U.S. tech giants collectively added over 32,000 jobs in India during 2025, an 18 percent year-over-year increase, according to Xpheno. Meta, Apple, Google, Amazon, Microsoft, and Netflix are all expanding Indian operations — partly because visa restrictions make it harder to bring talent to the United States, and partly because India's talent pool in AI, cloud, and product engineering has matured.

For the first time, the top four H-1B approvals for new employment went exclusively to American companies: Amazon with 4,644 approvals, Meta with 1,555, Microsoft with 1,394, and Google with 1,050, according to the National Foundation for American Policy. These same companies are now building the teams they need in Bengaluru, Hyderabad, and Chennai instead.

"This shift has been ongoing for a few years now," said Ashutosh Sharma, VP and research director at Forrester. "The imposition of $100,000 H-1B fees has simply made it more difficult, whereas sourcing through offshore centers in India has long been a much more predictable path for US enterprises to gain access to technical talent at scale."

LinkedIn data shows AI engineering talent is eight times more likely to migrate across borders than average professionals, with India serving as a net exporter. But visa restrictions are now constraining America's ability to attract that talent, pushing companies to establish operations where the engineers increasingly choose to remain.

## What This Means for the Diaspora

The reverse migration is not a rejection of America. It is a rational response to a system that asks Indian professionals to wait decades for permanent residency while making every intermediate step more expensive, more uncertain, and more hostile.

For the two million Indian-born professionals still in the United States — many with children in American schools, mortgages on American homes, and careers built over a decade or more — the calculation is existential. Leave and join the return migration to an India that finally has comparable opportunities? Or stay and bet that the system will eventually deliver on its decades-old promise?

The answer, for a growing number, is to stop waiting."""
    },
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
