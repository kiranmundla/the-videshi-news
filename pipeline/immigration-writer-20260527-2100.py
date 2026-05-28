#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-27 21:00 PDT run"""
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
        "headline": "33 Days to File or Lose It Forever — The FY2027 H-1B Petition Window Is Closing and the Rules Have Changed",
        "subheadline": "Wage-weighted selection, a new Form I-129, electronic-only fees, and a $100,000 consular processing surcharge have made this the most procedurally treacherous H-1B season in the program's history. If your employer got selected, here's what has to happen before June 30.",
        "slug": make_slug("h1b-fy2027-june-30-filing-deadline-guide-indian"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians represent 71% of approved H-1B petitions. For the tens of thousands of Indian professionals whose employers received FY2027 lottery selections, the June 30 deadline is absolute — miss it and the selection evaporates permanently, with no extensions. The new $100,000 consular processing fee hits Indian workers hardest since most new H-1B hires require stamping at Indian consulates already overwhelmed by demand.",
        "tags": ["h1b", "fy2027", "filing-deadline", "uscis", "visa", "wage-selection"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS", "url": "https://www.uscis.gov/working-in-the-united-states/h-1b-specialty-occupations"},
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/united-states-preparing-for-the-fy-2027-h-1b-cap.html"},
            {"name": "Lozano Law Firm", "url": "https://abogadolozano.com/h1b-fy2027-lottery-results-selected/"},
            {"name": "RJ Immigration Law", "url": "https://rjimmigrationlaw.com/h-1b-visa-changes-for-fy-2027/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8061949/pexels-photo-8061949.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "H-1B petition documents — FY2027 filing window closes June 30, 2026",
        "body": """The clock started on April 1. It stops on June 30. In between, every employer with an FY2027 H-1B lottery selection must assemble a Labor Condition Application, compile credential evaluations, cross-reference wage levels across three different government databases, and file a petition package that can survive a level of USCIS scrutiny not seen in any prior H-1B season.

Thirty-three days remain.

## The rules changed underneath you

This is the first H-1B cycle to use wage-weighted selection. The old system was a coin flip — every registration got an equal shot. The new one gives Level IV positions (highest-paid) the most lottery entries and Level I (lowest-paid) the fewest. For Indian professionals, who account for 71% of approved H-1B petitions, the math is stark: the median selection rate for Level IV positions jumped to roughly 75%, while Level I dropped to single digits.

But selection is only the entrance. USCIS now cross-references three numbers — the wage level declared during March registration, the prevailing wage on the Labor Condition Application, and the actual salary in the offer letter. A mismatch between any two can trigger a denial. Last cycle, this wasn't a concern. This cycle, immigration attorneys report it's the single most common reason petitions are getting returned.

## The LCA bottleneck

Before any H-1B petition can be filed, the employer must submit a Labor Condition Application to the Department of Labor. Certification typically takes 7 to 10 business days, but during peak season — which is right now — processing stretches to two weeks or more.

Any employer that hasn't filed the LCA yet is already in trouble. A mid-June LCA submission leaves almost no buffer for DOL processing, petition assembly, and the filing itself. Immigration attorneys who handle high volumes of H-1B cases say the realistic last date to submit an LCA and still make the June 30 deadline is the first week of June.

## The new Form I-129

USCIS released a redesigned Form I-129 effective April 1, 2026. Petitions filed on the old edition are rejected outright — not returned for correction, rejected. The new form includes fields for wage-level documentation and aligns with the wage-weighted selection system.

If you haven't verified your form version, do it today. The edition date (02/27/26) is printed in the lower left corner of the first page.

## The fee stack

Electronic-only payments are now mandatory — paper checks are no longer accepted. The base filing fee is $780. The ACWIA training fee runs $750 for small employers (25 or fewer employees) or $1,500 for larger ones. The fraud detection fee is $500. Employers where more than half the workforce holds H-1B or L-1 status pay an additional $4,000.

Premium processing — which guarantees a decision within 15 business days — now costs $2,965, up from $2,805 after an inflation adjustment.

And then there's the new $100,000 consular processing surcharge. Introduced under Presidential Proclamation 10973, this fee applies to petitions where the beneficiary is outside the United States and will need consular visa stamping. It does not apply to change-of-status petitions — meaning F-1 students switching to H-1B inside the U.S. are exempt — but for anyone requiring a new visa stamp at a consulate, the fee is inescapable.

For Indian workers, this is particularly punishing. The four U.S. consulates in India are already drowning in interview backlogs after the Rubio-era appointment freeze. Adding a six-figure fee on top of a multi-month wait for a stamping appointment creates what immigration lawyers are calling a "double gate."

## What happens if you miss June 30

The selection is permanently voided. No extensions, no grace period, no appeal. The H-1B number gets reallocated to a waitlisted registration in a potential secondary lottery over the summer. Your employer would need to re-register in March 2027 and hope the odds hold again — at a time when the wage-weighted system has dramatically reduced selection rates for mid-tier positions.

## The practical checklist

For Indian professionals whose employers received a selection notice, the next 33 days should look like this:

**This week**: Confirm your employer has filed (or is filing) the LCA with the correct SOC code, wage level, and worksite location. Verify the wage level matches what was declared during registration.

**By June 7**: Have all educational credentials — diploma, transcripts, foreign degree evaluation — assembled and verified. If you need a credential evaluation from a NACES-member agency, processing takes 10-15 business days.

**By June 14**: Employer support letter should be finalized. The letter must tie each major job duty to a specific academic discipline — vague descriptions are the leading cause of Requests for Evidence.

**By June 21**: Complete petition package should be assembled and ready for filing. If using premium processing, budget for the $2,965 fee on top of all other costs.

**By June 28**: File. Do not wait until June 30. Electronic filing systems can experience outages, and USCIS has no obligation to extend the deadline for technical difficulties.

## The broader picture

H-1B registrations dropped 38.5% for FY2027 — a direct consequence of the wage-weighted system discouraging low-wage filings. But for those who made it through the narrower gate, the stakes are higher than ever. In a labor market where the EXILE Act threatens to eliminate the H-1B entirely and the DOL is proposing a 30% prevailing wage increase, each approved petition carries more weight than it did a year ago.

The June 30 deadline doesn't care about any of that. It only cares about whether the paperwork is in."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "They Fired 115 Immigration Judges and Replaced Them with Prosecutors — Inside the Largest Court Overhaul in U.S. History",
        "subheadline": "The DOJ just swore in 77 new 'deportation judges' with enforcement backgrounds, plus five military lawyers on temporary assignment. For the estimated 300,000 Indians with pending immigration cases, the bench that decides their fate has been fundamentally restocked.",
        "slug": make_slug("deportation-judges-doj-77-fired-115-indian-cases"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are among the fastest-growing nationalities in U.S. immigration court dockets, with an estimated 300,000+ pending cases. Many involve asylum seekers, H-1B workers facing status complications, and green card applicants whose adjustment-of-status cases have been rerouted to immigration judges. A bench stacked with enforcement-background judges shifts the odds against favorable outcomes — particularly for Indians seeking discretionary relief like cancellation of removal or asylum based on religious persecution claims.",
        "tags": ["immigration-court", "deportation", "judges", "doj", "asylum", "trump"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/government/trump-administration-brings-record-new-class-immigration-judges-2026-05-21/"},
            {"name": "EOIR / DOJ", "url": "https://www.justice.gov/eoir/office-chief-immigration-judge"},
            {"name": "AILA", "url": "https://www.aila.org/practice/immigration-courts/featured-issue-us-immigration-courts-under-trump-2-0"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6077447/pexels-photo-6077447.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Immigration courtroom — the DOJ has replaced over a hundred judges with enforcement-background appointees",
        "body": """The ceremony took place on a Wednesday in Washington, D.C. Seventy-seven new immigration judges raised their right hands. Five military lawyers did the same. Acting Attorney General Todd Blanche called it "the largest immigration judge class in agency history." He credited President Trump's "decisive leadership."

What he did not mention: the 115 immigration judges who had been fired to make room.

## The arithmetic of a court overhaul

Since January 2025, the Trump administration has removed at least 115 immigration judges from the bench. Another hundred-plus have resigned, retired, or accepted buyouts. The departures came from across the ideological spectrum but disproportionately affected judges known for granting asylum claims or exercising discretion in deportation cases.

The replacements look different. Many of the 77 new permanent judges come from criminal prosecution or immigration enforcement backgrounds — ICE attorneys, DOJ trial counsel, Border Patrol legal advisors. Five temporary judges were detailed from the Pentagon, where Defense Secretary Pete Hegseth authorized military and civilian lawyers to serve six-month rotations on the immigration bench.

The Justice Department says it has now hired 153 permanent immigration judges in fiscal year 2026 — the most in a single year. The total bench sits near 700, roughly where it was before the purge, but with a fundamentally altered composition.

## What changed for Indians

Immigration judges are not part of the independent federal judiciary. They work for the Executive Office for Immigration Review, which reports to the Attorney General. They don't have life tenure. They serve at the pleasure of the administration. And the cases they hear — asylum, cancellation of removal, bond hearings, adjustment of status — are the cases where judicial temperament matters most.

For Indians, the stakes are concrete. An estimated 300,000 Indian nationals have pending cases in immigration courts, making them one of the fastest-growing demographics on the docket. These cases span a wide range:

**Asylum seekers** — Indians fleeing religious persecution (Sikhs, Christians, Muslims in certain states), political violence, or caste-based discrimination. Asylum grant rates vary enormously by judge — from above 80% to below 5% in some courts. A bench restocked with enforcement-background judges is expected to compress that range toward the bottom.

**H-1B workers in status limbo** — The new consular processing mandate and the PM-602-0199 memo have pushed some H-1B holders into removal proceedings when they can't adjust status domestically. These cases require a judge willing to exercise prosecutorial discretion. The new bench composition makes that less likely.

**Green card applicants rerouted to court** — When USCIS denies an adjustment-of-status application, the case can be referred to an immigration judge for removal proceedings. With EB-2 India now unavailable for the rest of FY2026 and NIW approval rates cratering to 35%, more Indian applicants may find themselves in court rather than at a USCIS window.

## The backlog shell game

The Justice Department frames the overhaul as a backlog-reduction measure. The pending caseload in immigration courts has declined from roughly 4 million to 3.53 million since Trump took office — a reduction of 470,000 cases.

But immigration attorneys point out that much of the decline comes from administrative closures, stipulated removals, and in absentia deportation orders rather than full hearings. When a judge orders someone deported without a hearing because they didn't appear in court — sometimes because they never received the notice — that's a "resolved" case in the DOJ's statistics. It's not justice in any recognizable form.

The National Association of Immigration Judges, which represents the judges themselves, has been largely silenced. The Supreme Court recently upheld restrictions on immigration judges' ability to speak publicly about their working conditions — a ruling The Videshi covered last week. The combination of a speech gag and a mass replacement creates an environment where institutional knowledge is erased and dissent is impossible.

## The military judges

The five temporary judges drawn from the military are a new experiment. Under an agreement between the DOJ and the Pentagon, military and civilian lawyers working for the Defense Department can serve up to six months as immigration judges. They receive a crash course in immigration law and are deployed to courts with the heaviest backlogs.

Critics argue that military lawyers — trained in courts-martial and military discipline — bring an enforcement mindset that is fundamentally incompatible with asylum adjudication, where the question is whether someone faces persecution, not whether they violated a regulation. Supporters counter that any warm body on the bench is better than a four-year wait for a hearing.

## What comes next

The administration has signaled it intends to continue hiring. Attorney General Blanche's office projects reaching 800 immigration judges by the end of FY2026, which would represent a net increase even after the firings. Each new cohort is drawn from the same enforcement-heavy pipeline.

For the Indian community, the practical implications are straightforward: if you have a pending immigration case — asylum, adjustment, bond hearing, anything requiring a judge — the person who decides it may be different from the person who was assigned it six months ago. And the replacement is statistically more likely to have spent their career removing people from the country than protecting their right to stay.

The judges who exercised discretion, who weighed equities, who considered the full picture of a family's ties to America — many of them are gone. The bench is being rebuilt in a different image. The cases are the same. The outcomes will not be."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
