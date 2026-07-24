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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Escape Route Is Closing — NIW Approvals Crashed to 35% and Indian Applicants Are Running Out of Options",
        "subheadline": "The EB-2 National Interest Waiver was supposed to be the workaround for India's decade-long green card backlog. USCIS just made it the hardest it has ever been to get one.",
        "slug": make_slug("niw-approval-rate-crash-indian-applicants-uscis"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For hundreds of thousands of Indian professionals stuck in the EB-2 green card queue — where wait times stretch past a decade — the NIW offered a rare shortcut: self-petition, skip the employer sponsorship, lock in a priority date. Now that shortcut is narrower than ever, and the timing could not be worse.",
        "tags": ["niw", "eb-2", "uscis", "green-card", "immigration", "indian-professionals"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Manifest Law — EB-2 NIW Approval Rates", "url": "https://manifestlaw.com/blog/eb2-niw-approval-rate/"},
            {"name": "Alma Immigration — EB-2 NIW Approval Rates 2026", "url": "https://tryalma.com/resources/eb-2-niw-approval-rate"},
            {"name": "Visa Franchise — EB-2 NIW Approval Rate 2026", "url": "https://visafranchise.com/blog/eb-2-niw-approval-rate/"},
            {"name": "Boundless — USCIS Q3 2025 EB-1A Data", "url": "https://www.boundless.com/research/uscis-q3-2025-eb1a-data/"},
            {"name": "USCIS Immigration and Citizenship Data", "url": "https://www.uscis.gov/tools/reports-and-studies/immigration-and-citizenship-data"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
        "body": """For years, the EB-2 National Interest Waiver was the Indian tech worker's quiet rebellion against a broken system. Instead of waiting in an employment-based queue that stretches past 2035 for India-born applicants, you could self-petition — argue that your work served America's national interest, skip the labor certification, and lock in a priority date while the regular line barely moved.

That door is still technically open. But USCIS is slamming it halfway shut.

## The numbers are brutal

In Fiscal Year 2022, the NIW approval rate stood at 95.7%. Nearly everyone who filed got through. By FY2025, that rate had collapsed to 55.2% — and in the final quarter of the fiscal year, from July through September 2025, it fell to just 35.7%. For the first time in recent memory, USCIS denied more NIW petitions than it approved in a single quarter: 5,356 denials against 2,968 approvals.

The trajectory tells the story in full:

- **FY2022**: 95.7% approval rate (21,973 petitions filed)
- **FY2023**: 79.6% (39,803 filed — an 81% surge)
- **FY2024**: 71% of adjudicated cases (63,549 filed — another 59% jump)
- **FY2025**: 55.2% overall, crashing to 35.7% in Q4 (66,276 filed)

Application volume nearly tripled in three years. The approval rate fell by 40 percentage points. The math is unforgiving.

## What happened

Two forces collided. The first was a Biden-era executive order in January 2022 that broadened the interpretation of "national interest" to include STEM graduates, entrepreneurs, and advanced-degree holders more generously. Filings exploded. The second was USCIS tightening the screws on the Dhanasar standard — the three-prong test that every NIW petitioner must clear — beginning in 2023 and accelerating through 2025.

Under Dhanasar, applicants must demonstrate that their proposed work has substantial merit and national importance, that they are well-positioned to advance that work, and that waiving the labor certification requirement benefits the United States. USCIS officers are now applying each prong with forensic rigor. Generic recommendation letters, vague claims of "impact," and boilerplate descriptions of research areas are drawing Requests for Evidence at rates not seen in years.

The agency is also scrutinizing what counts as "national importance" more narrowly. Technology consulting, generalized software engineering, and routine academic research — the bread and butter of many Indian NIW applicants — are facing pushback that would have been unthinkable in 2022.

## Why this hits Indian professionals hardest

Indian nationals are the largest single group of NIW filers, and the reasoning is straightforward. The EB-2 India queue has a priority date backlog stretching past a decade. For a 35-year-old software engineer who filed a PERM-based I-140 today, the green card might arrive when they are pushing 50. The NIW offered a way to self-petition in parallel, or sometimes instead — locking in a priority date without depending on an employer to sponsor and complete a labor certification that now takes 18-plus months to process.

With approval rates cratering, that safety valve is losing pressure. An Indian applicant who would have filed confidently in 2022 now faces coin-flip odds at best, and the denial carries real costs: thousands of dollars in legal fees, months of preparation, and — critically — no refund on the filing fee even if USCIS says no.

The timing compounds the pain. The June 2026 visa bulletin just retrogressed EB-2 India by ten months. The USCIS adjustment-of-status memo issued on May 21 now treats in-country green card processing as "extraordinary" relief rather than a routine path. And the proposed End H-1B Visa Abuse Act, if passed, would block H-1B holders from adjusting to permanent residency entirely.

## The EB-1A alternative is tightening too

Some Indian professionals have pivoted to the EB-1A extraordinary ability category — a higher bar, but one that moves faster for India-born applicants. USCIS data through Q3 2025 shows EB-1A filings from India surging, but approval rates there are also dipping as RFE volumes climb. The agency appears to be applying the same skeptical posture across the board.

O-1 visas — the temporary work visa for individuals with extraordinary ability — remain a relatively safe harbor, with approval rates above 90%. But an O-1 does not lead directly to a green card, and it requires continuous employer sponsorship.

## What applicants should do now

Immigration attorneys tracking the data offer consistent advice: file early, file strong, and do not rely on templates. The Dhanasar standard rewards specificity — measurable outcomes, documented adoption of your work, independent expert letters that engage with the three prongs directly rather than reciting your resume. The era of filing an NIW with a few recommendation letters and a personal statement is over.

Premium processing, now available for NIW petitions at $2,965, delivers a decision within 45 business days and is widely considered worth the cost in the current environment. A faster answer, even a denial, lets applicants regroup rather than waiting 14 to 19 months for standard processing only to discover their petition was never competitive.

For Indian nationals weighing their options, the calculation has shifted. The NIW is no longer a near-guarantee — it is a contested petition that requires genuine evidence of exceptional work. Those who can clear that bar still have a viable path. Everyone else is back in the queue."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A $200,000 Salary Floor and a Three-Year Freeze — Inside the Bill That Would Gut the H-1B Program",
        "subheadline": "Eight Republican lawmakers want to pause all new H-1B visas, slash the annual cap to 25,000, ban dependents, end OPT, and kill the path to a green card. Indian workers would bear the heaviest blow.",
        "slug": make_slug("end-h1b-visa-abuse-act-2026-bill-indian-workers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals receive roughly 70% of all H-1B approvals annually. A three-year freeze followed by a cap cut to 25,000 — combined with a $200,000 minimum salary and a ban on green card adjustment — would reshape the Indian professional pipeline to America more dramatically than any single policy change in decades.",
        "tags": ["h1b", "congress", "legislation", "immigration-reform", "indian-workers", "opt"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Arizona Republic — Crane, Gosar wrong to pause visas", "url": "https://www.azcentral.com/story/opinion/op-ed/2026/05/18/crane-gosar-wrong-pause-h1b-visas-rural-voters-suffer/84278171007/"},
            {"name": "Rep. Eli Crane — Official Press Release", "url": "https://crane.house.gov/2026/04/22/"},
            {"name": "The Hindu Business Line — Bill for 3-year pause on H-1B visas", "url": "https://www.thehindubusinessline.com/news/world/bill-for-3-year-pause-on-h-1b-visas-introduced-in-us-congress/article69489273.ece"},
            {"name": "LiveMint — Trump allies push bills to pause H-1B visas", "url": "https://www.livemint.com/news/india/trump-allies-push-bills-to-pause-and-scrap-h-1b-visas-what-does-it-mean-for-indians-h1b-visa-news-11777094337764.html"},
            {"name": "Reddy Neumann Brown — The End H-1B Visa Abuse Act Analysis", "url": "https://rnlawgroup.com/the-end-h-1b-visa-abuse-act-a-political-attack-disguised-as-reform/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/34151775/pexels-photo-34151775.jpeg",
        "body": """On April 22, Congressman Eli Crane of Arizona introduced H.R. 8443, formally titled the End H-1B Visa Abuse Act of 2026. Seven Republican cosponsors signed on. The bill's provisions read less like reform and more like demolition: a three-year moratorium on all new H-1B visa issuances, followed by a program so restrictive that it would be unrecognizable to anyone who has navigated the current system.

The legislation has not advanced to committee markup and faces steep odds in a Congress with competing priorities. But its provisions map the outer boundary of where the anti-H-1B movement wants to go — and several of its individual ideas have been floated in executive orders and agency guidance that require no congressional vote at all.

## What the bill proposes

The headline numbers are stark. The annual H-1B cap would drop from 65,000 to 25,000, with the 20,000-slot exemption for U.S. master's degree holders eliminated entirely. The random lottery that currently selects registrations would be replaced with a wage-based system, and the minimum salary for any H-1B position would rise to $200,000 — roughly three times the current effective floor for most filings.

But the bill goes well beyond numbers. It would:

- **Ban third-party staffing placements** — the model used by major IT services firms that employ tens of thousands of Indian H-1B workers at client sites
- **Prohibit H-1B holders from working multiple jobs** simultaneously
- **End Optional Practical Training (OPT)** — the post-graduation work authorization that roughly 290,000 international students use annually, including a large share of Indian STEM graduates
- **Block H-1B holders from adjusting status to permanent residency** — severing the traditional pathway from work visa to green card that hundreds of thousands of Indian professionals are currently navigating
- **Ban H-1B dependents** from accompanying workers to the United States, which would eliminate H-4 visas for spouses and children
- **Require employers to certify** that no qualified American worker is available and that no layoffs have occurred, with penalties for non-compliance
- **Bar federal agencies** from sponsoring or employing nonimmigrant workers

Workers would also be required to leave the United States before changing to another nonimmigrant visa status — a provision that would create gaps in work authorization for anyone attempting to transition between visa categories.

## The Indian exposure

Indian nationals received approximately 72% of all H-1B approvals in recent fiscal years. No other country comes close. The program has functioned as the primary legal channel through which Indian engineers, data scientists, healthcare workers, and business professionals enter the American workforce.

The staffing agency ban would hit the Indian IT services sector — companies like Infosys, Wipro, TCS, and HCLTech — with particular force. These firms built their U.S. operations on the H-1B model, placing Indian workers at American client sites under third-party arrangements. The bill would make that business model illegal.

The OPT elimination compounds the damage at the other end of the pipeline. Indian students account for more than 25% of all international students in the United States, and many use OPT and STEM OPT extensions as a bridge to H-1B sponsorship. Without OPT, the student-to-worker pathway that has fed American tech companies for two decades would cease to exist.

And the green card prohibition — perhaps the bill's most radical provision — would turn the H-1B into a dead-end temporary visa with no possibility of permanence. An Indian engineer who enters on an H-1B would, by law, never be able to adjust to permanent resident status. They would work for up to six years and then leave.

## The political context

The bill's sponsors frame it in populist terms. "American jobs should go to American workers first," wrote Congressman Paul Gosar in an op-ed defending the legislation. Crane called the H-1B program "a pipeline for replacing American workers with cheaper foreign labor." Rosemary Jenks of the Immigration Accountability Project called it "the strongest H-1B bill ever introduced in Congress."

Critics have been equally forceful. An Arizona Republic op-ed warned that the bill would devastate rural healthcare systems that depend on H-1B physicians. Immigration attorney firms have called it "an attempt to dismantle the high-skilled immigration system piece by piece." The argument from the legal community: if abuse exists, punish the abusers — do not eliminate the program.

The bill's prospects in the current Congress are uncertain. It has eight cosponsors, all Republican, and has not been scheduled for a hearing. But individual provisions — particularly the wage-based selection system and restrictions on staffing agencies — mirror executive actions already taken or proposed by the Trump administration. The $100,000 fee imposed on certain H-1B filings in September 2025 and the weighted selection rule finalized in December 2025 both push in the same direction.

## What it means in practice

The bill is unlikely to pass in its current form. But it serves as a policy roadmap for the anti-immigration wing of the Republican Party, and its provisions have a way of surfacing in executive orders, agency memos, and budget riders. Indian professionals tracking the H-1B landscape should pay attention not to whether H.R. 8443 passes, but to which of its ideas show up next in USCIS guidance.

The three-year pause, the staffing ban, the green card prohibition — each of these has been discussed independently in various policy circles. Their consolidation into a single bill signals that the movement to restrict high-skilled immigration is not slowing down. It is organizing.

For the roughly 700,000 Indian nationals currently in the H-1B system, and the hundreds of thousands more in the pipeline through OPT and university programs, the message is clear: the legal infrastructure that brought you here is under sustained political assault, and the next policy change might not require a vote in Congress to take effect."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
