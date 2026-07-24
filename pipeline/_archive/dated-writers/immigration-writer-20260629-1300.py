#!/usr/bin/env python3
"""Immigration news writer — 2026-06-29 13:00 PDT run."""

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
    return slug[:70].rstrip('-') + "-20260629"

# ─────────────────────────────────────────────
# Article 1
# ─────────────────────────────────────────────
art1_body = """Two in three American employers have now lost foreign workers because of visa delays, denials, or sheer uncertainty. And rather than waiting for Washington to sort itself out, they are moving the jobs — and the people — somewhere else.

New survey data paints a picture of corporate America in full retreat from its own immigration system. Some 65 per cent of employers reported that foreign employees left the United States over visa-related issues in the past year. Nearly 61 per cent relocated workers to offices abroad after visas were delayed or denied. And 68 per cent said they plan to increase nearshoring or offshoring in 2026 to sidestep immigration barriers entirely.

Canada and the United Kingdom have become the preferred landing zones — countries that, whatever their own bureaucratic quirks, at least offer predictable timelines. For Indian professionals on H-1B visas, the implications cut two ways. Some are being offered soft landings in Toronto or London, their green card sponsorship accelerated to keep them in the corporate fold. Others are simply watching their roles vanish from US headcounts altogether.

## The $100,000 trigger

The shift did not happen overnight, but the September 2025 presidential proclamation — imposing a $100,000 supplemental fee on new H-1B petitions — was the accelerant. For a mid-size tech firm sponsoring five or six engineers a year, that is half a million dollars in new costs before a single line of code is written.

The fee, struck down by a federal judge but still casting a long shadow over corporate planning, coincided with a new wage-weighted H-1B selection system that deprioritises entry-level and mid-career positions — exactly the roles Indian IT professionals have historically filled. Add in the indefinite pause on immigrant visa processing for nationals of 75 countries and the administration's reframing of green card applications as "extraordinary discretionary relief," and the message to employers was clear: plan around America, not through it.

## Green cards as retention tools

Companies that once viewed green card sponsorship as a nice-to-have perk are now treating it as a retention essential. According to the same employer survey, firms are accelerating PERM filings and I-140 petitions for key employees — not out of generosity, but because losing a senior engineer to visa limbo costs more than the legal fees.

For Indian nationals, this is bittersweet. Faster sponsorship is welcome, but it runs headlong into the EB-2 and EB-3 backlogs that stretch decades for India-born applicants. A company can file a green card petition in 2026 and the employee might not receive their card until the 2040s. In the meantime, they remain tethered to a single employer, unable to change jobs freely, start a company, or even take a promotion at a different firm without restarting the process.

## The manufacturing pivot

The trend is not limited to tech. Manufacturers are now building immigration considerations into project planning cycles, identifying foreign experts earlier and adding flexibility to hiring timelines. If a specialised welder or process engineer cannot be brought to Ohio on an H-1B, the company may site the project in Monterrey instead.

For the Indian diaspora, this represents a broader reshuffling of opportunity. The era when an H-1B stamp was a reliable on-ramp to an American career is fading. In its place is a more fragmented landscape — one where the same Indian engineer might find a faster path to permanent residency in Canada, a higher salary in London, or a remote role from Bengaluru that pays in dollars but requires no visa at all.

The question for Indian professionals is no longer whether America wants their talent. The data suggests it does. The question is whether America's immigration system will let it keep them — or whether corporate HR departments will quietly solve the problem by moving the jobs to wherever the talent can legally work.

As one immigration expert told Fortune: "If you lose them, you might not ever get them back, and there might not be another person behind them waiting in the wings to fill that role."

American employers seem to have heard the warning. They are just not waiting for Washington to act on it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Two in Three US Employers Have Lost Foreign Workers to Visa Chaos. Now They're Moving Jobs Out",
    "subheadline": "New data shows 68 per cent of American companies plan to increase offshoring in 2026 as visa delays and the $100,000 H-1B fee upend workforce planning — and Indian professionals are caught in the crossfire.",
    "slug": make_slug("us-employers-relocating-talent-visa-chaos-offshoring"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B workers are being relocated to Canada and the UK by their own employers, while green card sponsorship is being accelerated as a retention tool — but EB-2 India backlogs mean faster filing does not mean faster cards.",
    "tags": ["h1b", "offshoring", "green-card", "canada", "corporate-immigration", "visa-delays"],
    "urgency": "medium",
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "AInvest", "url": "https://www.ainvest.com/news/companies-relocate-talent-expedite-green-cards-1b-visa-uncertainty-2606/"},
        {"name": "HR Executive", "url": "https://hrexecutive.com/when-work-visas-stall-business-cant/"},
        {"name": "Fortune / Allwork.space", "url": "https://allwork.space/2026/06/immigration-expert-warns-companies-need-plan-c/"},
        {"name": "OGC Solutions", "url": "https://ogcsolutions.com/talent-without-borders-navigating-2026-l1-h1b/"}
    ]),
    "score_total": 78,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7109013/pexels-photo-7109013.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Professionals discussing strategy in a modern corporate office",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}

# ─────────────────────────────────────────────
# Article 2
# ─────────────────────────────────────────────
art2_body = """India's six largest IT services firms received 40 per cent fewer H-1B visas this year than last. And the remarkable thing is how little any of them seem to care.

According to official US government data, Tata Consultancy Services, Cognizant, Infosys, HCL Technologies, Wipro, and Tech Mahindra collectively received 11,041 H-1B approvals as of 31 March 2026, down from 18,469 the previous year. TCS took the steepest hit, losing 3,242 approvals to land at just 2,885. Infosys, at 3,195, was the only firm in the group to post an increase.

A decade ago, this would have been a crisis. These companies built a $250 billion industry partly on the ability to move engineers from Hyderabad and Pune to client sites in Dallas and New Jersey on H-1B visas. That model is not dead, but it is on life support — and the companies have spent years preparing for exactly this moment.

## The quiet transformation

Between 2017 and 2025, the number of Indian employees on H-1B visas working for TCS, Infosys, Wipro, and HCL nearly halved, falling from 34,507 to 17,997. The decline did not begin with the $100,000 fee or the wage-weighted lottery. It started in 2018, when H-1B denial rates spiked to 24 per cent, forcing firms to rethink their delivery models.

The result has been a systematic shift toward local hiring in the United States, expanded offshore delivery from India, and the opening of nearshore centres in Canada, Mexico, and Eastern Europe. As Cognizant CEO Ravi Kumar told analysts: the company has "significantly reduced the dependency on visas, while increasing local hiring and our nearshore capacity."

TCS chief executive K. Krithivasan went further, noting the firm deployed "fewer people than the number of approvals each year" — meaning TCS was already using fewer H-1Bs than it was granted, treating them as insurance rather than necessity.

## The subcontractor squeeze

But the transition is not free. Three of India's top five IT firms recorded more than a 20 per cent year-on-year increase in subcontracting expenses in the December 2025 quarter. TCS led with a 26.6 per cent jump to ₹3,560 crore. Infosys followed at 23.9 per cent (₹4,092 crore), and HCLTech at 23.3 per cent (₹4,775 crore).

The arithmetic is straightforward: when you cannot bring your own engineer from India on an H-1B, you hire a locally available subcontractor at a premium rate. Phil Fersht, CEO of HFS Research, called subcontracting "an operational necessity" given higher visa fees and longer processing times. The risk, he warned, is that temporary subcontracting becomes structural, permanently eroding margins.

CRISIL Intelligence estimates the $100,000 fee will trim 10 to 20 basis points from IT services companies' operating margins, with firms passing 30 to 70 per cent of the incremental cost through to clients. For now, that pass-through is holding. But clients, too, have limits.

## What it means for the H-1B worker

USCIS framed the decline as vindication. "The days of abusing the program with mass, low-wage registrations are over," the agency posted on X in May, noting that H-1B registrations now average just 1.01 per beneficiary — effectively one submission per person, down from the duplicate-laden cycles of years past.

For an Indian mid-career engineer hoping to work onsite in America, the picture is stark. The wage-weighted selection system now favours senior, higher-paid roles, pushing entry-level and mid-career positions to the back of the queue. The $100,000 supplemental fee — even if currently enjoined by a federal court — has chilled employer appetite for new sponsorships. And the recent USCIS rule requiring green card applicants to return to their home country for consular processing upends the lives of anyone who has built a life in the US while waiting in the backlog.

India's IT giants will survive the H-1B contraction. They have spent nearly a decade preparing for it. The question is whether the Indian professionals who once relied on those companies for their American careers will find the same resilience — or whether the path to the United States, for an entire generation of engineers, is simply narrower than it used to be."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's IT Giants Just Lost 40 Per Cent of Their H-1B Visas. They Barely Noticed",
    "subheadline": "TCS, Infosys, Wipro, and their peers received 11,041 H-1B approvals this year — down from 18,469. But after a decade of reducing visa dependency, the companies are more worried about subcontractor costs than visa counts.",
    "slug": make_slug("india-it-giants-h1b-visas-40-percent-drop-subcontractors"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian mid-career engineers face a narrowing path to US onsite assignments as IT firms shift to local hiring and the wage-weighted H-1B lottery deprioritises entry-level and mid-career roles — the exact positions these companies historically filled.",
    "tags": ["h1b", "tcs", "infosys", "wipro", "it-services", "outsourcing", "offshoring"],
    "urgency": "medium",
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Mint", "url": "https://www.livemint.com/companies/it-u-h-1b-visas-green-card-immigration-tcs-infosys-cognizant-green-cards-hiring-11779598845829.html"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/indian-it-majors-see-rise-in-subcontractor-costs-in-q3-fy26-amid-h1b-visa-disruptions/article69111841.ece"},
        {"name": "CRISIL / NewKerala", "url": "https://www.newkerala.com/news/2025/137854.htm"},
        {"name": "USCIS", "url": "https://www.uscis.gov/newsroom"}
    ]),
    "score_total": 82,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16323580/pexels-photo-16323580.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A software developer working at dual monitors in a modern office",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────
# Article 3
# ─────────────────────────────────────────────
art3_body = """For years, the EB-1A extraordinary ability green card was the province of Nobel laureates, Olympic athletes, and the occasional tech executive with a shelf of patents. It was never meant for a 32-year-old software architect in Sunnyvale with a handful of conference papers and a GitHub profile.

Now it might be their best option. And that is creating problems of its own.

EB-1A filings are up roughly 50 per cent year-over-year, according to the latest USCIS data through Q3 of fiscal year 2025. Filings from India and Nigeria have surged particularly sharply, while those from China have declined by about 40 per cent. The approval rate has slipped to 67 per cent — the lowest in three years — and the backlog has grown 67 per cent in a single quarter, to approximately 2.5 months of pending cases.

The National Interest Waiver, the EB-1A's slightly more accessible sibling under the EB-2 category, is faring worse. Its approval rate has cratered to 54 per cent, down 13 percentage points, while its backlog has nearly doubled to 4.3 months.

## Why Indians are pivoting

The logic is not complicated. The EB-2 India employment-based green card queue stretches decades. The July 2026 visa bulletin shows EB-2 India as effectively "unavailable" — no new cases will move forward until the new fiscal year begins in October. EB-3 India is similarly frozen.

Meanwhile, the H-1B programme that was supposed to be a bridge has become a toll road. The $100,000 supplemental fee, the wage-weighted lottery, employer reluctance to sponsor new petitions — all of it has pushed Indian professionals to look for routes that do not depend on an employer's willingness to file paperwork and write cheques.

The EB-1A and NIW are self-petition categories. You file for yourself. You do not need an employer sponsor, a labour certification, or a PERM filing. For a mid-career Indian professional with published research, patents, peer review experience, or a track record of building something that moved the needle in their field, these categories represent the only realistic path to a green card that does not involve a 20-year wait.

## The RFE wave

But USCIS has noticed the surge — and it is responding with scrutiny. The growing backlog is driven largely by a wave of Requests for Evidence (RFEs) and Notices of Intent to Deny (NOIDs). When USCIS issues an RFE, the case sits in limbo for two to three months while the applicant compiles additional documentation. The full impact of this review surge may not appear in approval data for another six months.

An August 2025 policy update has pushed EB-1A adjudication toward a more rigid, non-discretionary framework. Officers are now expected to evaluate evidence strictly against the statutory criteria rather than exercising subjective judgment. In principle, this is fairer. In practice, it means weaker applications that might once have squeaked through on a sympathetic adjudicator's read are now being bounced.

The "judge of the work of others" criterion, for example — one of the 10 regulatory criteria an EB-1A applicant can use — now requires proof of actual service on review panels, not just an invitation. Peer review requests from a journal's editorial system alone will not suffice.

## The NIW tightening

The NIW is taking an even harder hit. USCIS appears to be applying stricter standards to "national interest" arguments, especially in technology, consulting, and research — fields where Indian applicants are heavily concentrated.

A January 2026 policy manual update clarified two things: letters from governmental or quasi-governmental entities now carry explicit weight, and STEM graduates whose degree ties to a critical or emerging technology get a formal boost under prong two of the *Dhanasar* framework. That helps some applicants — but it also raises the bar for everyone else. If USCIS is giving extra credit for government backing and national-security alignment, a startup founder building a SaaS tool has to work harder to prove their endeavour serves the national interest.

## What to do with this information

For Indian professionals weighing their options, the data points in one direction: file early, file strong, and do not wait for conditions to improve. The competition for EB-1A and NIW slots is only increasing. The O-1 visa, with approval rates still above 90 per cent, remains a reliable bridge for those who qualify, buying time while a green card petition works through the system.

Immigration attorneys recommend submitting comprehensive initial filings — publications, media coverage, awards, detailed expert letters — rather than relying on the RFE process to fill gaps. An RFE is not a rejection, but it adds months to an already lengthening timeline.

The escape route from the H-1B trap exists. It is just getting more crowded, and the door is closing a little more each quarter."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The Escape Route Through EB-1A Is Getting Crowded. Indian Filings Are Surging — and So Are Denials",
    "subheadline": "EB-1A applications from India have spiked 50 per cent. NIW approval rates have fallen to 54 per cent. For Indian professionals fleeing the H-1B trap, the self-sponsored green card path is the best option left — and it is getting harder.",
    "slug": make_slug("eb1a-niw-india-filings-surge-approval-rates-fall"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals are increasingly turning to self-petition green card categories like EB-1A and NIW to escape the H-1B uncertainty and decades-long EB-2 India backlog — but surging demand and tighter USCIS scrutiny mean the window is narrowing.",
    "tags": ["eb-1a", "niw", "green-card", "uscis", "self-petition", "india-backlog"],
    "urgency": "medium",
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Boundless", "url": "https://www.boundless.com/blog/uscis-q3-2025-data-eb1a-niw-trends"},
        {"name": "Manifest Law", "url": "https://manifestlaw.com/reports/eb1a-niw-trends-2026"},
        {"name": "Colombo & Hurd / Medium", "url": "https://medium.com/@colombohurd/eb-1a-petitions-in-2026-understanding-shift-from-discretionary-review"},
        {"name": "AILA", "url": "https://www.aila.org/library/did-the-national-interest-waiver-just-get-easier"}
    ]),
    "score_total": 80,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A hand holding an open passport with various travel and visa stamps",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}

# ─────────────────────────────────────────────
# Insert all
# ─────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
