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

article1_body = """Immigration lawyers are cancelling their autumn holidays. Behind that small, telling detail lies one of the least-understood deadlines in American immigration — and a date that thousands of wealthy Indian families are now racing to beat.

September 30, 2026 is not the day the EB-5 investor visa program ends. The program is authorised through September 2027. But it is the day a legal protection worth far more than the difference between two dates quietly disappears, and the gap between those two deadlines is where the urgency lives.

## The protection that expires a year early

When Congress passed the EB-5 Reform and Integrity Act in March 2022, it added a "grandfathering" clause to reassure investors burned by a previous program lapse that had frozen thousands of petitions. The clause is narrow but powerful: any I-526E petition properly filed and received by US Citizenship and Immigration Services on or before September 30, 2026 must continue to be adjudicated under today's rules — even if the regional centre program later expires, even if Congress fails to reauthorise it in 2027, even if the law changes underneath it.

File one day after that date, and that statutory shield is gone. The petition may still be accepted while the program remains authorised, but it carries no insurance against the next lapse. For a family committing $800,000 and several years of their lives, that distinction is the whole game.

## The triple deadline

What makes 2026 unusually fraught is that three separate clocks are now converging on the same window, and each one independently rewards filing sooner:

First, the grandfathering cutoff on September 30, 2026. Second, an inflation adjustment to the minimum investment amount, mandated by the RIA itself and due in January 2027 — which is expected to push the rural and targeted-employment-area minimum from $800,000 toward roughly $940,000. Third, the program's underlying authorisation, which expires in September 2027 unless Congress acts. An investor who files before September 30, 2026 locks in the current price, the current rules, and the statutory protection in a single stroke. An investor who waits risks paying more, under less certain rules, with no shield.

The predictable result is a stampede. Major EB-5 deadlines have always triggered last-minute filing surges, and immigration attorneys report exactly that pattern building now: competition for the best regional-centre projects, capacity constraints, and longer timelines for the painstaking source-of-funds documentation every petition requires. Lawyers warn that complex cases take months to prepare properly — meaning the real deadline for starting is well before September.

## Why this matters to Indian families

For India's diaspora, the EB-5 calculus has shifted from exotic to strategic. With the EB-2 employment category listed "unavailable" in the July visa bulletin and the conventional employment-based green card wait stretching past the horizon, families with capital are increasingly treating the $800,000 investment as a way to buy out of a decade-long queue rather than as a speculative bet.

But the same per-country caps that strangle the H-1B-to-green-card path apply to EB-5 too. India is now a high-demand EB-5 country, and retrogression — a backward slide in visa availability — is widely expected as filings surge. That makes the priority date an investor secures by filing early genuinely valuable: it is a place in line that cannot be recreated later. The grandfathering deadline and the looming retrogression point in the same direction: the earlier the filing, the better the position.

The honest caveats matter, because EB-5 is sold hard. Grandfathering protects a petition from program-lapse disruption; it does not guarantee USCIS approval, does not eliminate backlogs or retrogression, and does not speed up processing. Partial or staggered investments are drawing rapid requests for evidence — sometimes within two weeks of filing — under the current administration's tighter scrutiny, so the conservative path is a full investment at the time of filing. And $800,000 placed in a development project is capital genuinely at risk; the visa is contingent on the project creating the required jobs.

For an Indian family weighing the route, the practical message is unromantic but clear. If EB-5 is genuinely on the table, the decision window is now measured in weeks of preparation, not months of deliberation. The date that matters is not when the program ends. It is when the protection ends — and that clock runs out on September 30, 2026."""

article2_body = """Every spring, tens of thousands of Indian students celebrate the same piece of good news: their employer's H-1B petition has been approved. What a growing number are discovering, often too late, is that an approved petition and the right to stay in the country are not the same thing — and the gap between them can mean an unplanned flight home.

The trap lies in a distinction most applicants never think about. An H-1B filing actually asks USCIS for two things at once: approval of the petition itself, and a "change of status" from F-1 student to H-1B worker so the person can begin work on October 1 without leaving the United States. Immigration attorneys report that USCIS is increasingly approving the first while denying the second — and a denied change of status can be far more disruptive than a denied petition.

## How the gap opens

The change-of-status portion requires the applicant to have maintained valid F-1 status continuously, right up to the moment H-1B status would begin. That sounds simple. In practice, the gaps are everywhere: a lapse between the end of OPT employment authorisation and October 1; a brief unemployment stretch that pushed an OPT student past the 90-day limit; a paperwork slip in a STEM extension; a CPT arrangement a later officer deems improper. Any of these can lead USCIS to find that status was not maintained — and to deny the change of status even as it approves the underlying H-1B petition.

When that happens, the worker is not simply turned down. They are expected to depart the United States and obtain an H-1B visa stamp at a US consulate abroad before returning to start the job. The petition is valid; the path back runs through Mumbai, Hyderabad or Chennai.

## Why "just go get it stamped" is a problem

A decade ago, consular stamping was a formality. In 2026 it is anything but. Visa appointment wait times at Indian consulates have stretched for months, third-country stamping options have narrowed, and administrative-processing delays can strand an approved worker abroad for weeks with no certainty. A denial of change of status thus converts a smooth on-paper transition into a costly, uncertain exit — lost income, an employer left waiting, and a family in limbo.

There is a newer wrinkle that makes the calculus worse. Attorneys report that USCIS officers have begun citing travel bans under Section 212(f) as a "negative discretionary factor" when adjudicating change-of-status requests for nationals of affected countries. The legal theory is contested — entry bans technically suspend entry, not the granting of status inside the country — but the practical effect is that some applicants who have done nothing wrong are nudged toward denial, and toward the consular route, precisely where the ban bites hardest.

## Why this matters to Indian students

Indians are the largest international-student population in the United States, with more than 360,000 enrolled in the 2024-25 academic year, and the F-1-to-H-1B pipeline is the spine of the diaspora's professional class. That pipeline is now narrowing at both ends. At the front, a wage-weighted lottery and a proposed $100,000 fee make selection harder. At the back, the change-of-status trap means even selection and approval no longer guarantee an uninterrupted stay.

The risk is compounded by a separate proposal, now cleared by the White House for publication, to replace the longstanding "duration of status" framework with fixed admission periods for F-1 students — and to shrink the post-completion grace period from 60 days to 30. A shorter grace window leaves less room to absorb exactly the kind of timing gaps that sink a change-of-status case.

The takeaways are practical rather than alarmist. Maintaining unbroken F-1 status is no longer a background formality; it is the single most important thing an H-1B-bound student can control, and worth a careful review with counsel before the cap petition is even filed. Documenting every OPT employment date, staying well inside the unemployment limits, and avoiding aggressive CPT arrangements all reduce the chance of a status finding that unravels the change of status later. And anyone whose change of status is denied should understand the consular timeline they may be walking into before they book a flight — because in 2026, the journey out is the easy part. The journey back is the gamble."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The EB-5 Deadline Indian Investors Keep Missing Isn't When the Program Ends",
        "subheadline": "A statutory protection worth more than the price tag expires on September 30, 2026 — a full year before the program itself — and it is colliding with a January 2027 price hike to trigger a filing stampede.",
        "slug": make_slug("eb5-grandfathering-deadline-sept-2026-investment-hike-jan-2027-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "With EB-2 India listed 'unavailable' in the July visa bulletin, wealthy Indian families are increasingly treating the $800,000 EB-5 investment as a way to buy out of a decade-long green card queue — but the grandfathering protection that makes early filing valuable expires September 30, 2026, a year before the program does.",
        "tags": ["eb5", "investor-visa", "green-card", "grandfathering", "ria", "retrogression", "diaspora"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Colombo Hurd Law — EB-5 Grandfathering Deadline: September 30, 2026 Explained", "url": "https://colombohurdlaw.com/"},
            {"name": "Lexology/Buchalter — EB-5 Investors: The September 30, 2026 sunset of the Grandfathering provision", "url": "https://www.lexology.com/"},
            {"name": "Mondaq/Withers LLP — EB-5 Investors Face A Critical Grandfathering Deadline On September 30, 2026", "url": "https://www.mondaq.com/"},
            {"name": "U.S. Immigration Fund / Greenberg Traurig — EB-5 deadline and January 2027 investment adjustment briefing", "url": "https://visaeb-5.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33785777/pexels-photo-33785777.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport and US dollars beside a financial app — the EB-5 investor route now turns on timing as much as money",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your H-1B Was Approved. So Why Might You Still Have to Leave the Country?",
        "subheadline": "USCIS is increasingly approving H-1B petitions while denying the change of status that lets students stay — forcing approved workers into a consular stamping backlog that can strand them abroad for weeks.",
        "slug": make_slug("h1b-approved-change-of-status-denied-f1-students-consular-stamping-trap-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the largest international-student population in the US, and the F-1-to-H-1B pipeline is the spine of the diaspora's professional class — but a denied change of status now converts a smooth on-paper transition into a costly, uncertain exit through India's months-long consular stamping backlog.",
        "tags": ["h1b", "change-of-status", "f1-students", "opt", "consular-stamping", "uscis", "diaspora"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reddy Neumann Brown PC — USCIS Is Citing Travel Bans to Deny Change of Status", "url": "https://www.rnlawgroup.com/"},
            {"name": "Outlook Money — US Visa Proposal May Limit Stay Duration For Foreign Students; How It Impacts Indians", "url": "https://www.outlookmoney.com/"},
            {"name": "IRS — Employers Must Withhold FICA Taxes for Aliens who Change Visa Status to H-1B", "url": "https://www.irs.gov/"},
            {"name": "USCIS Policy Manual — Part F, Students (F, M)", "url": "https://www.uscis.gov/"}
        ]),
        "score_total": 79,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1058959/pexels-photo-1058959.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport at the airport — for some approved H-1B workers, a denied change of status means an unplanned flight home for consular stamping",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article2_body
    }
]

# word count sanity check
for art in articles:
    wc = len(art["body"].split())
    assert 400 <= wc, f"{art['slug']} too short: {wc}"
    print(f"[wc] {art['slug']}: {wc} words")

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
