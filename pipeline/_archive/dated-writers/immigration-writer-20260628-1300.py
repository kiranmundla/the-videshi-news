#!/usr/bin/env python3
"""Immigration news writer — June 28, 2026 1:00 PM PT run."""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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


# ────────────────────────────────────────────
# ARTICLE 1: N-400 Citizenship Fee Hike
# ────────────────────────────────────────────

article1_body = """The path to American citizenship has never been cheap. It is about to get considerably more expensive — and for the hundreds of thousands of Indian-born green-card holders weighing whether to naturalize, the arithmetic just changed.

In June 2026, U.S. Citizenship and Immigration Services published a proposed rule that would nearly double the filing fee for Form N-400, the application for naturalized citizenship. Paper filers would see the cost jump from $760 to $1,330. Online applicants would pay $1,280, up from $710. The fee for requesting a hearing on a denied naturalization — Form N-336 — would climb from $830 to $1,475.

The numbers alone are striking. But the fine print is worse: USCIS also proposes eliminating most fee waivers and reduced-fee options for low-income applicants. For a family of four where both parents hold green cards, the combined cost of naturalizing could exceed $2,600 — before biometrics, legal fees, and the English and civics test preparation that many applicants invest in.

## The Indian-American Calculus

Indians represent the second-largest group of new lawful permanent residents in the United States each year, behind only Mexicans. But thanks to the per-country green-card cap, most Indian nationals wait a decade or longer for their cards — meaning the typical Indian LPR arrives at citizenship eligibility later in life, often with children, mortgages, and the accumulated financial weight of years on a single income while a spouse held an H-4 dependent visa.

For this cohort, the proposed fee hike is not abstract. It lands at a moment when the calculus around naturalization has become unusually urgent.

The Supreme Court ruled this week that border agents no longer need "clear and convincing evidence" before turning away a green-card holder returning from abroad. Travel attorneys are already advising Indian LPRs to think twice before visiting family in India. Naturalization — which confers an unconditional right of reentry — suddenly looks less like a bureaucratic milestone and more like insurance.

## A Closing Window

The proposed rule is not yet final. The public comment period runs through August 24, 2026, and a final rule would likely be published several weeks after that. Immigration attorneys say the practical implication is clear: applicants who file their N-400 before the rule takes effect will pay the current fee.

"If you're eligible and you've been putting it off, the time to file is now," said one immigration lawyer who advises Indian professionals in the Bay Area. "Not just because of the fee, but because the broader policy environment makes citizenship the only truly secure status."

USCIS says the fee increase is necessary to fund its operations, including processing backlogs that have plagued the agency for years. Critics counter that eliminating fee waivers will disproportionately affect immigrants from lower-income backgrounds — including elderly parents sponsored through family-based petitions, who may live on modest fixed incomes.

## The Broader Pattern

The N-400 fee hike does not exist in isolation. It arrives alongside a cascade of cost increases and procedural tightening across the immigration system: the contested $100,000 H-1B filing fee (still in legal limbo after a court stay), the new USCIS signature rule taking effect July 10 that can convert a bad signature into a denial, and the agency's recent memo reframing adjustment of status as an "extraordinary" remedy rather than a routine procedure.

For Indian Americans who have spent years navigating this system — waiting through green-card backlogs, renewing H-1B stamps at overloaded consulates, paying immigration attorneys at every turn — the cumulative message is unmistakable: every step forward now costs more, takes longer, and carries greater risk.

The comment period remains open. Immigration advocacy groups, including the American Immigration Lawyers Association, are urging the public to submit comments opposing the fee increase. Whether those comments alter the final rule remains to be seen. But the deadline — August 24 — is firm, and the window for filing at the current rate is narrowing.

For anyone eligible, the question is no longer whether to naturalize, but whether you can afford to wait."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Becoming American Just Got More Expensive. For Indian Green-Card Holders, the Clock Is Ticking",
    "subheadline": "USCIS proposes nearly doubling the N-400 citizenship fee to $1,330 and eliminating most fee waivers. The public comment window closes August 24 — and immigration lawyers say eligible applicants should file now.",
    "slug": make_slug("uscis-n400-citizenship-fee-hike-indian-green-card-holders"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian LPRs who waited a decade through green-card backlogs now face a sharply higher price tag for naturalization — at the exact moment Supreme Court rulings make citizenship the only truly secure immigration status.",
    "tags": ["citizenship", "n-400", "uscis", "naturalization", "fee-hike", "green-card", "indian-americans"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "NOLO Immigration Legal Updates", "url": "https://www.nolo.com/legal-updates/immigration-law-updates-in-2026.html"},
        {"name": "Federal Register — USCIS Proposed Rulemaking", "url": "https://www.govinfo.gov"},
        {"name": "Reuters — Supreme Court Immigration Rulings", "url": "https://www.reuters.com"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/2025_Naturalization_Ceremony-_Oath_of_Citizenship_%2854813557413%29.jpg/1280px-2025_Naturalization_Ceremony-_Oath_of_Citizenship_%2854813557413%29.jpg",
    "image_caption": "New citizens take the oath of allegiance at a U.S. naturalization ceremony",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}


# ────────────────────────────────────────────
# ARTICLE 2: India's GCC Boom
# ────────────────────────────────────────────

article2_body = """For a decade, the argument against restricting H-1B visas was straightforward: American companies need Indian talent, and if they cannot bring it to the United States, the work will simply move to India. It was treated as a warning. It is now a quarterly earnings slide.

India's global capability centre ecosystem — the corporate R&D and technology hubs that multinationals operate across Bengaluru, Hyderabad, Pune, and Chennai — has crossed 2,100 centres employing 2.36 million professionals and generating nearly $100 billion in annual revenue, according to a 2026 Nasscom-Zinnov report. That is not a back-office story. These are product teams, AI research labs, cybersecurity operations, and clinical analytics divisions that used to report to managers in Sunnyvale and Redmond. Increasingly, they report to no one but themselves.

## The $100,000 Catalyst

The Trump administration's $100,000 H-1B filing fee — imposed in September 2025 and currently suspended in legal limbo after a federal court ruled it exceeded statutory authority — did not invent offshoring. But it accelerated a shift that was already underway.

Between 2017 and 2025, the number of Indian employees on H-1B visas at TCS, Infosys, Wipro, and HCL Technologies nearly halved, falling from 34,507 to 17,997. Crisil Intelligence estimates that Indian IT firms will pass 30 to 70 percent of the new visa costs to clients — but the deeper strategic response has been to move the work, not absorb the fee.

"This imposition of $100,000 H-1B fees has simply made it more difficult, whereas sourcing through offshore centres in India has long been a much more predictable path for US enterprises to gain access to technical talent at scale," noted an analysis in Computerworld.

The numbers tell the story in a different register. GCC hiring rebounded 12 to 14 percent quarter-on-quarter in Q4 FY26, according to staffing firm Quess Corp, with new centres launched by companies ranging from French drugmaker Sanofi (expanding to 4,500 employees in Hyderabad) to American cybersecurity firm N-able (opening a new Bengaluru centre and planning 50 percent headcount growth by year's end).

## Not the Old Outsourcing

The crucial distinction — one that the Indian diaspora is watching closely — is that this is not the call-centre outsourcing of 2005. Microsoft India's head Puneet Chandok points to the country's 27 million developers on GitHub and its digital public infrastructure as competitive advantages that did not exist a decade ago. Target operates its Bengaluru facility as an "integrated headquarters." IBM describes its India operations as a "macrocosm" of the entire enterprise.

Pari Natarajan, CEO of research firm Zinnov, frames the shift in almost philosophical terms: "The idea that talent must physically move to headquarters to create value is steadily losing relevance. What has fundamentally changed is trust. Capability, not proximity to headquarters, now determines where leadership sits."

## The Diaspora Paradox

For Indian Americans working in technology, the GCC boom creates an unusual tension. Their employers are investing heavily in India — building the very centres that could, in theory, absorb the roles those same employees perform in the United States. The 7,300 tech workers who returned to India from the U.S. in the first half of 2026, driven by H-1B restrictions and layoffs, represent the human edge of this structural realignment.

Yet the domestic Indian job market is struggling to absorb them. Active technology job openings in India fell to 93,000 in June 2026, a 14 percent monthly decline and a 28-month low, according to staffing firm Xfino. Returning professionals often face salary expectations misaligned with Indian market realities — the cost-of-living arbitrage that once made H-1B salaries feel modest now works in reverse.

The GCCs hire aggressively, but they hire on Indian terms: Indian salaries, Indian benefits, Indian career tracks. For someone who spent a decade building a life in the Bay Area or Seattle — kids in American schools, a mortgage, a 401(k) — the transition is not just financial. It is existential.

## What Comes Next

Projections from Nasscom-Zinnov see the GCC ecosystem reaching 2,400 centres and $105 to $110 billion in revenue by 2030, expanding at roughly 10 percent annually. LTIMindtree is scaling centres in Vancouver and Mexico alongside India. The delivery model is no longer offshore versus onshore — it is a distributed mesh where geography matters less than capability.

The irony is not lost on anyone in the immigration debate. The policy designed to "protect American workers" may be doing precisely what its architects intended — reducing dependence on foreign labour within the United States. But the work has not disappeared. It has moved to where the talent is. And the talent, for now, is increasingly in India.

For Indian Americans, the question is no longer whether their skills are valued. It is where."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "America Made H-1B Workers Too Expensive. India Built a $100 Billion Industry to Absorb Them",
    "subheadline": "India's global capability centres now employ 2.36 million people and generate $100 billion in revenue. The H-1B crackdown didn't kill the work — it moved the address.",
    "slug": make_slug("india-gcc-boom-100-billion-h1b-crackdown-talent-shift"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian Americans in tech watch their employers invest in India GCCs while their own visa status shrinks — and the 7,300 who returned to India in H1 2026 find a job market that wants them, but on very different terms.",
    "tags": ["gcc", "india-tech", "h1b", "offshoring", "bengaluru", "nearshoring", "talent-shift"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Nasscom-Zinnov GCC Report 2026", "url": "https://nasscom.in"},
        {"name": "Computerworld", "url": "https://www.computerworld.com"},
        {"name": "YourStory — GCC Hiring Q4 FY26", "url": "https://yourstory.com"},
        {"name": "Xfino Staffing Data", "url": "https://ainvest.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Manyata_Embassy_Business_Park.jpg/1280px-Manyata_Embassy_Business_Park.jpg",
    "image_caption": "Manyata Embassy Business Park in Bengaluru, one of India's largest tech corridors housing dozens of global capability centres",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}


# ────────────────────────────────────────────
# INSERT
# ────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
