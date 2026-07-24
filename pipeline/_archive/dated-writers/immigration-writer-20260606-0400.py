#!/usr/bin/env python3
"""Immigration writer — 2026-06-06 04:00 UTC run"""
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
    {
        "id": str(uuid.uuid4()),
        "headline": "They Want to Kill OPT Entirely — and 95,000 Indian Graduates Are in the Crosshairs",
        "subheadline": "A conservative legal foundation has formally petitioned DHS to rescind the entire post-completion OPT program, arguing Congress never authorized it. If they succeed, the bridge from F-1 student visa to H-1B work visa effectively collapses.",
        "slug": make_slug("landmark-legal-petition-kill-opt-program-indian-stem-graduates"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals are the largest cohort of F-1 and STEM OPT participants. The program is the primary bridge from graduation to H-1B sponsorship. Killing it would strand tens of thousands of Indian STEM graduates with degrees but no legal path to work in the US.",
        "tags": ["opt", "stem-opt", "f1-visa", "uscis", "landmark-legal", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/op-eds/4595474/reduce-fraud-preserve-jobs-by-eliminating-opt-program/"},
            {"name": "Landmark Legal Foundation", "url": "https://landmarklegal.org/landmark-urges-dhs-to-end-unauthorized-opt-work-program/"},
            {"name": "ICE / DHS", "url": "https://www.ice.gov/"},
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29646491/pexels-photo-29646491.jpeg",
        "image_caption": "Graduates celebrating at a university commencement ceremony",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The Optional Practical Training program has long been the quiet workhorse of American immigration — the mechanism that lets international graduates stay and work for up to three years after finishing a STEM degree, buying time while they chase an H-1B lottery ticket. Roughly 95,000 foreign nationals used it last year alone, up 21 percent from the year before.

Now a conservative legal powerhouse wants it dead.

## The Petition

On May 21, Landmark Legal Foundation — the public-interest law firm that helped craft the legal architecture for several Trump-era immigration actions — filed a formal petition with the Department of Homeland Security demanding that it rescind post-completion OPT entirely. Not reform it. Not tighten it. Kill it.

The petition rests on a deceptively simple argument: Congress authorized the F-1 visa "solely" for study. Post-completion OPT participants are no longer studying. Therefore, DHS created a de facto work visa category without congressional approval. In legal terms, Landmark invokes the "major questions doctrine" — the Supreme Court principle that agencies cannot make decisions of vast economic and political significance without clear legislative authority.

"Post-completion OPT is a textbook example of executive overreach," said Michael O'Neill, Landmark's vice president for legal affairs. "It bypasses Congress, undermines immigration law, and puts American graduates at a disadvantage in their own job market."

## Why It Matters

The argument is not frivolous. DHS has the administrative authority to rescind OPT through the standard rulemaking process under the Administrative Procedure Act — no act of Congress required. The Supreme Court has already shown appetite for applying the major questions doctrine aggressively, most notably in its 2022 decision striking down the EPA's broad climate regulations. If DHS decides to act on the petition, the timeline could move faster than most applicants expect.

Landmark's filing arrives alongside fresh ammunition. Two weeks before the petition went public, ICE Director Todd Lyons announced that investigators had identified more than 10,000 possible fraud cases within OPT. On-site visits to employers found OPT participants being managed by employees based in India. Shell companies, Lyons alleged, were helping recent graduates maintain legal status without genuine sponsorship from an American corporation.

The fraud findings feed directly into Landmark's broader case: that OPT has metastasized from a limited training opportunity into a parallel work visa pipeline operating outside congressional oversight and riddled with abuse.

## The Indian Calculus

For Indian students in the United States — the largest single national group in the F-1 pipeline — the stakes are existential.

The pathway is well-worn: earn a master's in computer science or engineering from an American university, secure a STEM OPT authorization, work for a sponsoring employer, and hope to land one of the roughly 85,000 new H-1B visas available each year. Without OPT, that bridge vanishes. Graduates would face a binary choice on commencement day: find an employer willing to sponsor an H-1B petition immediately, or leave.

The math is brutal. Brookings projects a 29 percent decline in F-1 student visa issuances for 2025, a trend already thinning the pipeline. Indian enrollment, after years of record growth, has begun to plateau. If OPT is eliminated on top of these headwinds, the entire student-to-worker pipeline — the conveyor belt that has fed Silicon Valley, Big Pharma, and Wall Street with Indian engineering talent for decades — would seize.

Tech employers would feel the squeeze acutely. OPT participants are cheaper to employ: companies pay no Social Security or Medicare taxes on them. That built-in subsidy, which Landmark frames as an unfair market distortion, is precisely what makes OPT graduates attractive hires. Remove it, and employers must compete for domestic talent at higher cost — or move roles offshore.

## What Happens Next

DHS is under no obligation to act on the petition. It could sit on a shelf indefinitely. But the political winds favor action. The administration has already imposed a $100,000 fee on new H-1B petitions, replaced the random lottery with a wage-weighted selection system, and launched Project Firewall to investigate employer compliance. Eliminating OPT would fit neatly into the broader project of constricting every segment of the high-skill immigration pipeline.

For Indian students weighing whether to pursue a degree in the United States, the calculus just got harder. The $50,000-per-year bet on an American education was always a gamble. Without the three-year OPT runway to recoup that investment, the gamble may no longer be worth taking.

Eleven states, led by Kansas, have already filed an amicus brief with the Supreme Court supporting the legal theory that OPT exceeds DHS's statutory authority. The courts have not yet ruled definitively. But the question is no longer whether OPT faces a serious challenge. It is whether DHS will wait for the courts to decide — or pull the plug first."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "'These Are Global Laws' — What the State Department Said While 200,000 Workers Paid $100,000 for Their Visas",
        "subheadline": "A senior U.S. diplomat insisted H-1B rules don't target India. The same week, DHS revealed that 70 percent of visa applicants opted to pay a six-figure fee rather than wait seven months for standard processing.",
        "slug": make_slug("state-department-global-laws-200k-paid-100k-h1b-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals make up 75% of H-1B holders. The 'global rules' framing ignores that the $100K fee, wage-weighted lottery, and PM-602 consular processing shift disproportionately impact Indians due to their dominant presence in the visa pipeline and the longest employment-based green card backlogs of any nationality.",
        "tags": ["h1b", "state-department", "uscis", "100k-fee", "india", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/state-dept-official-says-h-1b-visa-rules-are-global-not-targeted-at-india/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/world/over-2-lakh-paid-100000-for-h-1b-visas-says-dhs-secretary-mullin/article69329000.ece"},
            {"name": "U.S. Department of State", "url": "https://www.state.gov/"},
            {"name": "Aviationa2z", "url": "https://www.aviationa2z.com/index.php/2026/06/03/dhs-reveals-massive-demand-for-h-1b-visas/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c9/The_United_States_State_Department_Headquarters_Building.jpg",
        "image_caption": "The U.S. State Department headquarters in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Andrew Pigott chose his words carefully. Speaking at the New York Foreign Press Centre on June 5, the senior State Department official addressed the question that had been gnawing at Indian diplomatic circles for months: Are these new visa rules aimed at India?

"There are no visa laws that target India," Pigott said. "These are global visa laws that are being implemented with clarity, clear instructions that are being applied across the board."

The timing was not accidental. A high-level U.S. Trade Representative delegation had just wrapped four days of talks in New Delhi, working to advance a bilateral trade agreement. Immigration remained the elephant in every room.

## The Numbers Tell a Different Story

Three days before Pigott's remarks, DHS Secretary Markwayne Mullin sat before the Senate Appropriations Subcommittee and disclosed figures that complicate the "global, not targeted" framing considerably.

Of the 286,000 H-1B applications received in fiscal year 2026, more than 200,000 applicants — over 70 percent — had paid the $100,000 premium processing fee that the Trump administration imposed last September. Those who paid got their cases adjudicated in roughly 15 days. Everyone else? Seven and a half months.

The fee was designed to be punishing. It effectively priced out the mid-tier IT staffing firms and outsourcing contractors that were the heaviest users of the H-1B pipeline — companies disproportionately headquartered in India or serving Indian-born workers in the United States. The result is a two-tier immigration system operating in plain sight: one lane for employers who can afford six figures per petition, and a slow lane for everyone else.

Pew Research Center data shows that roughly three-quarters of H-1B approvals in recent years went to Indian-born workers. When a rule hits 75 percent of a program's participants harder than anyone else, calling it "global" is technically accurate and practically meaningless.

## The Bureaucratic Squeeze

The $100,000 fee is only one piece of a broader tightening that has reshaped the H-1B landscape in 2026. Consider what has landed since February:

A **wage-weighted lottery** replaced the random selection system on February 27. Under the new rules, applicants at the highest salary level receive four entries into the selection pool; those at the entry level receive one. The system explicitly favors higher-paid positions — roles more likely to be filled by experienced professionals at major corporations than by early-career workers at staffing firms. For Indian IT companies that built their American operations on volume hiring at competitive wages, the math has shifted decisively against them.

A **policy memo** issued on May 21, designated PM-602-0199, reframed adjustment of status — the process of obtaining a green card while remaining in the United States — as a discretionary act of "extraordinary" grace rather than a standard pathway. USCIS spokesperson Zach Kahler later clarified that applicants providing an "economic benefit" would likely still qualify, but the discretionary language injected uncertainty into a process that Indians, more than any other nationality, depend on. With roughly 627,000 Indian-born applicants stuck in the employment-based green card backlog, any new variable in adjustment of status reverberates through hundreds of thousands of lives.

And starting **July 10**, USCIS will impose stricter signature requirements on H-1B and green card filings, granting officers broader authority to deny petitions with "deficient" signatures unless they are handwritten or use an authorized electronic signature. Minor clerical errors that previously triggered a Request for Evidence — an annoyance, but a survivable one — may now result in outright denials. For employers already absorbing the $100,000 fee and navigating the wage-weighted lottery, the margin for procedural error has narrowed to nearly nothing.

## The Diplomatic Tightrope

Pigott's statement fits a pattern: the administration frames each individual policy as neutral and meritocratic while the cumulative effect falls unevenly on one country's nationals. The State Department defends the rules diplomatically. DHS presents their scale and fiscal impact. USCIS reshapes who gets selected and how cleanly applications must be prepared.

Indian IT professionals feel much of that pressure not because the rules name them, but because of their dominant position in the pipeline. A salary-weighted system, by design, favors the highest-paid positions. A $100,000 fee, by design, favors the wealthiest sponsors. A stricter adjustment-of-status standard, by design, affects those with the longest backlogs. In each case, "by design" and "targeting India" produce the same practical outcome through different legal reasoning.

Whether Pigott's assurance eases concern in New Delhi may depend less on the rhetoric than on how the rules play out when the next filing cycle opens. The numbers — 286,000 applicants, 200,000 paying $100,000, a weighted system in force since February, and new filing traps arriving July 10 — will do their own talking."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
