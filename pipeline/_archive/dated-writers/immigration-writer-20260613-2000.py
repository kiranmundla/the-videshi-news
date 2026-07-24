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
        "headline": "The Thirty-Three Per Cent Pay Rise Nobody Asked For — Washington's Quiet Plan to Price Out H-1B Workers",
        "subheadline": "A proposed Department of Labor rule would hike entry-level H-1B wages by a third, threatening the economics of Indian IT staffing firms and thousands of early-career professionals.",
        "slug": make_slug("dol-prevailing-wage-hike-33-percent-h1b-indian-workers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian IT services firms — Infosys, TCS, Wipro, HCL — sponsor the largest share of H-1B petitions and place workers at Level I and II wages. A 33% floor increase would force renegotiation of thousands of client contracts and could push smaller Indian staffing firms out of the US market entirely.",
        "tags": ["h1b", "prevailing-wage", "dol", "indian-it", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "U.S. Department of Labor", "url": "https://www.dol.gov/newsroom/releases/eta/eta20260326-0"},
            {"name": "KPMG GMS Flash Alert", "url": "https://kpmg.com/content/dam/kpmgsites/xx/pdf/2026/04/fa26-089.pdf.coredownload.pdf"},
            {"name": "Lexology / Duane Morris", "url": "https://www.lexology.com/library/detail.aspx?g=a7b2104f-8710-474b-a7b4-a9a4c96f7566"},
            {"name": "National Foundation for American Policy", "url": "https://nfap.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5691305/pexels-photo-5691305.jpeg",
        "image_caption": "A government building in Washington, D.C. flying the American flag",
        "image_attribution": "Pexels",
        "body": """On March 27, the U.S. Department of Labor published a proposed rule that barely made a ripple in the news cycle. No executive order, no presidential proclamation, no prime-time announcement. Just a Notice of Proposed Rulemaking buried in the Federal Register that would, if finalised, do something the $100,000 H-1B fee never could: make hiring Indian tech workers in America permanently more expensive.

The rule targets the prevailing wage system — the formula that determines the minimum salary an employer must pay an H-1B worker. Under the current methodology, which has been in place since 2005, a Level I (entry-level) position is benchmarked at the 17th percentile of wages for that occupation and geography. The DOL wants to move it to the 34th percentile. That is a 33.4 per cent increase overnight.

## The Numbers That Matter

The proposed changes affect all four wage tiers:

- **Level I (Entry):** 17th percentile → 34th percentile (+33.4%)
- **Level II (Qualified):** 34th percentile → 52nd percentile (+24.5%)
- **Level III (Experienced):** 50th percentile → 70th percentile (+20.8%)
- **Level IV (Senior):** 67th percentile → 88th percentile (+21.7%)

For a software developer in the San Francisco metro area, a Level I wage currently sits around $118,000. Under the proposed rule, it would jump to roughly $157,000. For a data analyst in Dallas, the floor moves from approximately $68,000 to $91,000. These are not small adjustments.

The DOL frames the change as overdue. Secretary of Labor Lori Chavez-DeRemer said the rule would "ensure that employers pay foreign workers wages that reflect the real market value of their labor." The department argues that the current 17th-percentile floor effectively allows employers to undercut American workers by hiring H-1B holders at below-market rates.

## Why Indian IT Is in the Crosshairs

The Indian IT services model — pioneered by Infosys, TCS, Wipro, HCL, and scores of smaller staffing firms — has long relied on placing H-1B workers at Level I and Level II wages. These are not necessarily underpaid workers; many are recent graduates or early-career engineers who fit the "entry-level" classification by DOL standards. But they are the backbone of the outsourcing model: bill the client at market rate, pay the worker at the prevailing wage floor, pocket the margin.

A 33 per cent increase to that floor does not just cut margins. It upends them. Smaller Indian staffing firms operating on thin spreads may find it mathematically impossible to sponsor H-1B workers at the new rates. Larger firms will be forced to renegotiate thousands of existing client contracts — or absorb the difference.

The National Foundation for American Policy published an analysis last month concluding the proposed wage levels would likely be ruled illegal if adopted, arguing they are designed to "price high-skilled foreign nationals out of the labor market by significantly raising the required wage" — violating the intent of the Immigration and Nationality Act.

## The Comment Period Is Closed. Now What?

The 60-day public comment period ended on May 26. The DOL is now reviewing submissions and could finalise the rule at any point. Unlike the $100,000 fee — which was imposed by presidential proclamation and is currently tangled in three separate court challenges — this rule went through the Administrative Procedure Act's notice-and-comment process. That makes it significantly harder to challenge in court.

For Indian professionals already in the United States on H-1B visas, the immediate concern is renewal. When an H-1B petition comes up for extension, it must meet the prevailing wage requirement at the time of filing. If the new wage levels are in effect by then, employers will face a choice: raise the salary or withdraw the petition.

For those still in India hoping to enter the H-1B lottery, the calculus changes too. If employers face higher mandatory salaries, they will sponsor fewer workers — and prioritise senior roles over entry-level ones. The pipeline of fresh Indian engineering graduates flowing into American tech firms could narrow considerably.

## The Bigger Picture

The prevailing wage rule is one piece of a coordinated squeeze on the H-1B programme. The $100,000 fee targets the front door. The PROTECT Act, introduced by Rep. Mike Kennedy, seeks to codify that fee in law. The DOL wage rule targets the economics that make sponsorship viable in the first place.

Together, they amount to a message: if you want to hire foreign talent in America, you will pay for the privilege. For Indian IT workers — who account for roughly 72 per cent of all H-1B approvals — that message lands with particular force.

The question now is timing. The DOL has the authority to finalise the rule without further congressional action. When it does, the salary floor for hundreds of thousands of Indian professionals in America will change — and the industry that built itself around that floor will have to rebuild."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's EB-5 Golden Ticket Just Expired for the Year — And the Clock Is Ticking on a Bigger Deadline",
        "subheadline": "The unreserved EB-5 investor visa category has hit its annual cap for Indian applicants, freezing new issuances until October. But a September 30 grandfathering deadline could reshape the entire programme.",
        "slug": make_slug("eb5-india-unreserved-cap-exhausted-fy26-october-pause"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian investors have surged into the EB-5 programme in recent years as the employment-based green card backlog stretches past a decade. With the unreserved category now frozen and a critical grandfathering deadline approaching on September 30, NRI investors face a narrow window to lock in Regional Center protections.",
        "tags": ["eb5", "investor-visa", "green-card", "immigration", "indian-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "AInvest", "url": "https://www.ainvest.com/news/eb-5-visa-cap-reached-indian-applicants-issuances-paused-october-2606/"},
            {"name": "U.S. Department of State - Visa Bulletin", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/"},
            {"name": "EB-5 Reform and Integrity Act of 2022", "url": "https://www.uscis.gov/working-in-the-united-states/permanent-workers/eb-5-immigrant-investor-program"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32269241/pexels-photo-32269241.jpeg",
        "image_caption": "A passport alongside US dollar bills and travel documents",
        "image_attribution": "Pexels",
        "body": """For Indian investors who thought the EB-5 programme was their shortcut past the green card backlog, the U.S. Department of State just pulled the handbrake. The unreserved EB-5 category for Indian applicants has hit its annual visa cap for fiscal year 2026, and no new visas will be issued until the allocation resets on October 1.

The freeze is not a policy change. It is arithmetic. The EB-5 programme allocates roughly 10,000 immigrant visas per year, and no single country can receive more than 7 per cent of the total under per-country caps. Indian demand — driven by tech professionals, real estate investors, and wealthy families seeking a faster green card path — has finally overwhelmed the numbers.

## How India Got Here

Five years ago, Indian nationals were a footnote in EB-5 statistics. The programme was dominated by Chinese investors, who at one point accounted for over 80 per cent of all EB-5 petitions. But as China's own EB-5 backlog grew to a decade-long wait and the employment-based green card queue for Indians stretched past 50 years in some categories, Indian money started flowing into American businesses at unprecedented rates.

The June 2026 Visa Bulletin tells the story. The EB-5 unreserved Final Action Date for India has moved to May 1, 2022 — meaning only petitions filed before that date are currently eligible for processing. The category is now marked "unavailable," joining EB-2 India in the growing list of frozen visa categories this fiscal year.

U.S. embassies and consulates have stopped issuing fresh unreserved EB-5 visas to Indian nationals. Applicants inside the United States seeking adjustment of status through the unreserved category face the same wall. The queue simply ran out of numbers.

## The Set-Aside Lifeline

There is a significant carve-out, however, and it is one that immigration attorneys are urging Indian investors to pay close attention to. The EB-5 Reform and Integrity Act of 2022 created three "set-aside" categories — Rural, High Unemployment Area, and Infrastructure — that are exempt from per-country caps. These categories remain current for Indian applicants even as the unreserved pool is frozen.

The set-aside categories were designed to channel investment into underserved regions. A rural EB-5 project requires a minimum investment of $800,000 in a designated rural area, compared to $1,050,000 for the standard programme. For Indian investors, the attraction is not just the lower price tag — it is the absence of a backlog. While unreserved EB-5 applicants face multi-year waits, set-aside applicants can, in theory, receive concurrent filing benefits and work authorization while their petition is pending.

The catch: project quality. Not every rural or high-unemployment project is created equal, and the EB-5 industry has a well-documented history of fraud and failed developments. Indian investors entering the set-aside categories need to conduct due diligence that goes well beyond the glossy marketing materials.

## The September 30 Deadline

Hovering over the entire EB-5 landscape is a deadline that most applicants are not thinking about carefully enough. Under the EB-5 Reform and Integrity Act, Regional Center EB-5 petitions filed on or before September 30, 2026, receive "grandfathering" protections. These protections ensure that if Congress changes the programme's rules, extends the investment thresholds, or modifies eligibility criteria, petitions already in the system are evaluated under the rules that existed when they were filed.

After September 30, that protection disappears. Any petition filed from October 1 onward will be subject to whatever rules Congress enacts — and given the current administration's posture toward immigration, those rules are unlikely to become more generous.

For Indian investors sitting on the fence, the math is straightforward. Filing a Regional Center petition before September 30 locks in the current $800,000 minimum investment for rural set-aside projects and the existing eligibility framework. Waiting past that date means accepting unknown future terms.

## What This Means for the Diaspora

The EB-5 programme has become the escape valve for wealthy Indian families frustrated by the employment-based green card backlog. An EB-2 applicant from India filing today faces a wait measured in decades. An EB-5 applicant, particularly through the set-aside categories, can potentially receive a green card in two to three years.

But the FY2026 cap exhaustion is a warning signal. Indian demand is now large enough to exhaust annual allocations — and it is growing. As more Indians enter the programme, the unreserved category will become as backlogged as the employment-based categories that drove investors there in the first place.

The window is not closing yet. But the EB-5 programme, once considered India's fast lane to permanent residency, is starting to look more like another queue. For those considering the investment, September 30 is the date circled in red — and the calendar is not slowing down."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}... -> {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
