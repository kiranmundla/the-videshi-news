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
        "headline": "The Four-Year Countdown — America Is About to Rewrite the Rules for 360,000 Indian Students",
        "subheadline": "DHS is weeks away from finalising a rule that replaces open-ended student visas with a hard four-year clock. PhD students, OPT holders, and fall 2026 arrivals will feel it first.",
        "slug": make_slug("dhs-duration-of-status-f1-four-year-limit-indian-students"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian students are the largest international cohort in US universities, and this rule change threatens the PhD-to-OPT-to-H-1B pipeline that has defined the diaspora's professional class for a generation.",
        "tags": ["f1-visa", "duration-of-status", "opt", "stem-opt", "indian-students", "dhs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "ICEF Monitor", "url": "https://monitor.icef.com/2026/05/us-to-end-duration-of-status-for-f-j-and-i-visas/"},
            {"name": "Cornell International Services", "url": "https://international.globallearning.cornell.edu/guidance-dhs-proposes-end-duration-status"},
            {"name": "American Institute of Physics", "url": "https://www.aip.org/fyi/visa-and-immigration-policy-elimination-duration-status-international-students"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/tighter-student-visa-rules-may-impact-indians-in-us-expert/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29275615/pexels-photo-29275615.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "University graduates celebrate at a commencement ceremony",
        "image_attribution": "Pexels",
        "body": """For more than thirty years, the deal was simple. An international student arrived in America on an F-1 visa stamped "D/S" — duration of status — and stayed as long as the programme demanded. Finish your PhD in six years? Fine. Roll straight into three years of STEM OPT? No problem. The clock didn't tick because there was no clock.

That is about to change.

The Department of Homeland Security published a proposed rule last August to scrap duration of status entirely. Under the new framework, most F-1 and J-1 visa holders would be admitted for a maximum of four years, full stop. Anyone needing more time — to finish a dissertation, to complete an OPT stint, to transfer programmes — would have to file a formal extension of stay with USCIS, pay the fees, and wait for adjudication.

The public comment period closed in September 2025. According to NAFSA, the final rule could drop any day between now and the end of June, with a 60-day implementation window that would put it in effect for students arriving this fall.

## What Actually Changes

The current system trusts universities to manage student status. Your designated school official signs off on extensions, programme changes, and OPT recommendations. USCIS barely enters the picture until the H-1B lottery.

The proposed rule yanks that authority back to the federal government. Key provisions:

- **Four-year hard cap** on initial admission, regardless of programme length
- **Grace period cut** from 60 days to 30 days after programme completion
- **No programme switching** for graduate students at any point during their studies
- **No lateral or downward enrolment** — complete a master's, and you cannot pursue another master's
- **Formal I-539 extension** required for OPT, STEM OPT, programme overruns, and transfers
- **Language students** capped at 24 months total

That I-539 extension requirement is the quiet earthquake. USCIS currently processes I-539 applications in 1 to 19.5 months, according to its own published timelines. A physics PhD student entering year five would need to file months in advance — and hope the adjudication arrives before their status expires.

## Why Indian Students Are Disproportionately Exposed

India sends more students to American universities than any other country except China. Over 360,000 Indian students were enrolled in US institutions during the 2024-25 academic year, with more than 143,000 actively using OPT work authorisation.

The pipeline is well-understood: bachelor's or master's degree, 12 months of OPT (36 months for STEM), then the H-1B lottery. Remove the seamless bridge between study and work, and the entire architecture wobbles.

PhD students are the most vulnerable. According to American Institute of Physics data, international students represent over 40 per cent of first-year enrolments in physics and astronomy graduate programmes. More than 90 per cent of them take longer than four years to finish. Every single one of those students would need to file for an extension under the new regime.

MBA graduates face a different kind of exposure. They get only 12 months of OPT — no STEM extension — and the H-1B lottery opens just once a year, in March, for an October start. A student who spends ₹60-80 lakh on a US business degree could graduate with no legal pathway to work while waiting for sponsorship.

## The Processing Time Trap

The Department of Homeland Security has not explained how it plans to handle potentially hundreds of thousands of new I-539 applications on top of an existing backlog of 11 million pending cases. Premium processing is not available for I-539 forms. The system that would adjudicate these extensions is the same one that currently takes up to 19.5 months for employment authorisation documents.

Danielle Goldman, co-founder and CEO of immigration platform Build, put it bluntly: the proposed rule would "fundamentally change the flexibility that students have had to apply for Optional Practical Training and Curricular Practical Training."

Universities are already feeling the pressure. International student offices at Cornell, Yale, and Washington University have published guidance urging students not to panic — but also warning that the rule, if finalised, would require far more federal paperwork than anything the current system demands.

## What to Watch

The Keep Innovators in America Act, a bipartisan bill introduced by Representatives Raja Krishnamoorthi, Sam Liccardo, and Jay Obernolte, would codify OPT into federal law and insulate it from executive action. But the bill is in early stages, and it does not address duration of status directly.

Indian families planning fall 2026 arrivals should treat the rule change as likely. That means evaluating universities not just by rankings and ROI, but by the strength of their international student support, employer pipelines, and STEM designations. It means building financial buffers for months of potential limbo. And it means having a backup plan — in Canada, the UK, Australia, or back home — that does not depend on American bureaucracy working faster than it ever has."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "One Hundred and Twenty-Six Thousand Fewer Applications — The H-1B Landscape After the $100,000 Fee",
        "subheadline": "Registrations crashed 27 per cent. Amazon, Google, and Meta all pulled back. But for Indians who stayed in the lottery, the odds have never been better.",
        "slug": make_slug("h1b-registrations-crashed-27-percent-fewer-applicants-odds-improve"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians file the majority of H-1B petitions and dominate the tech-sector pipeline. The 27% registration drop reshapes both the lottery odds and the long-term career calculus for hundreds of thousands of Indian professionals in the US.",
        "tags": ["h1b", "uscis", "h1b-lottery", "tech-hiring", "immigration-fees", "amazon", "google", "meta"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Inc.", "url": "https://www.inc.com/employment/trumps-dollar100000-h-1b-visa-fee-was-just-struck-down-why-many-employers-still-have-a-bigger-problem.html"},
            {"name": "VisaVerge", "url": "https://visaverge.com/immigration-news/h-1b-visa-changes-2026-tech-filings-drop-amid-new-fees/"},
            {"name": "VisaVerge", "url": "https://visaverge.com/immigration-news/2026-h-1b-visa-trends-tech-giants-slash-filings-as-costs-rise/"},
            {"name": "The Register", "url": "https://www.theregister.com/2025/05/08/h1b_registrations_dropped_by_25/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/immigration/judge-agrees-to-partly-pause-order-tossing-100-000-h-1b-fee"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "An open passport displaying travel and visa stamps at an airport",
        "image_attribution": "Pexels",
        "body": """The numbers landed like a thud. For fiscal year 2026, USCIS received 343,981 eligible H-1B registrations — down from 470,342 the previous year. That is a 26.9 per cent decline, or roughly 126,000 fewer people trying to enter the lottery for America's most important skilled-worker visa.

The drop is not subtle, and it is not random. It is the direct consequence of President Trump's September 2025 proclamation imposing a $100,000 fee on every new H-1B hire processed at a consulate outside the United States. Combined with a wage-weighted selection system that favours higher-paid roles, the fee has fundamentally redrawn who applies, who sponsors, and who gets in.

## The Big Tech Pullback

The data tells a story of corporate retreat. Amazon's certified H-1B applications fell from 4,647 in the first quarter of FY 2025 to 3,057 in Q1 FY 2026 — a 34 per cent drop. Google and Meta each cut their filing volumes by approximately 50 per cent year-over-year. Apple, Microsoft, IBM, Salesforce, and Tesla all posted declines, though less dramatic ones.

This is not a story about companies suddenly discovering patriotism. It is about math. A $100,000 fee on top of existing petition costs — which already ran $5,000 to $7,600 — makes sponsoring entry-level or mid-level foreign workers economically irrational. Companies are narrowing their petitions to senior engineers, AI researchers, and specialists whose salaries justify the investment.

The result is a two-tier H-1B programme. At the top, a shrinking number of elite positions where employers will pay any price for talent. Below that, a growing dead zone where roles that once drew H-1B sponsorship now go unfilled or get shipped offshore.

## The Paradox: Better Odds for Fewer Players

Here is the twist nobody expected. With 126,000 fewer registrations competing for the same 85,000 visas — 65,000 regular slots plus 20,000 for advanced degree holders — the selection rate has climbed to roughly 50 per cent, according to immigration attorneys. That is a dramatic improvement from the sub-30 per cent odds that prevailed when the system was clogged with nearly 781,000 registrations in FY 2024.

For an Indian software engineer at a company willing to absorb the $100,000 fee, this is quietly the best H-1B lottery in years. Fewer speculative entries. Fewer duplicate registrations — each beneficiary averaged just 1.01 registrations in FY 2026, down from 1.06 the year before, a sign that the anti-fraud reforms are working. And a wage-weighted system that actually rewards the kind of senior roles Indians disproportionately hold.

USCIS has not been shy about taking credit. "The data indicates that there were far fewer attempts to gain an unfair advantage than in prior years," the agency said, pointing to reforms that include a $215 registration fee (up from $10), mandatory unique passport numbers, and a strict one-entry-per-beneficiary limit.

## The Fee's Legal Limbo

The $100,000 fee itself is now caught in a judicial ping-pong match that shows no signs of settling soon. On June 8, Judge Leo Sorokin in Boston struck it down as an unconstitutional tax, ruling that only Congress has the power to impose such a levy. Twenty Democratic-led states had challenged the policy.

But the administration moved fast. On June 12, the DOJ filed for an emergency stay, and Sorokin agreed to pause his own ruling while the First Circuit Court of Appeals weighs in. A separate federal judge in Washington has already upheld the fee. Cases are also pending in the Northern District of California and the DC Circuit.

The practical effect: the $100,000 fee remains in force, at least for now. Companies that were hoping Sorokin's ruling would give them breathing room are back to planning around the six-figure surcharge.

"The Department of Justice is committed to protecting American workers and fully supports President Trump's America First agenda," a DOJ spokesperson said. "Another court has already ruled in the Administration's favour on this issue."

## What This Means for the Indian Pipeline

India accounts for roughly 72 per cent of all H-1B approvals in a typical year. The registration crash does not change that ratio — if anything, it concentrates the programme further toward high-earning Indian professionals in tech, consulting, and finance.

But the broader ecosystem is fracturing. Entry-level Indians fresh out of OPT — the ones who once relied on consulting firms to sponsor their first H-1B — face a programme that no longer wants them. The wage-weighted lottery penalises lower salaries. The $100,000 fee makes speculative petitions uneconomical. And the consulting firms that built their business models around bulk H-1B sponsorship are pulling back.

The shift is already visible in Labour Condition Application data. Infosys, Tata Consultancy Services, Wipro, and Cognizant — the Indian IT outsourcers that once dominated H-1B filings — have been reducing their petitions for years. The $100,000 fee accelerated a trend that was already in motion.

For Indian professionals navigating this landscape, the calculus is newly stark. If your employer values you enough to spend $100,000 on your visa, your odds of selection have never been better. If they do not, the H-1B may no longer be your path — and the alternatives (EB-1A extraordinary ability, O-1 visas, or the Canadian Express Entry system) deserve a harder look than they did a year ago."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
