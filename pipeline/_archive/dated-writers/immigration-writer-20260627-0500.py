#!/usr/bin/env python3
"""Immigration writer — 2026-06-27 05:00 PT run."""
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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


articles = [
    # ── Article 1: U-Visa Fraud Ring ──
    {
        "id": str(uuid.uuid4()),
        "headline": "They Staged Armed Robberies to Get U-Visas. An Indian National Just Pleaded Guilty",
        "subheadline": "Federal prosecutors say at least 11 Indian nationals participated in a scheme that faked convenience-store holdups in Massachusetts so clerks could claim crime-victim visas — a con that cost participants up to $20,000 and now carries prison time and deportation.",
        "slug": make_slug("staged-robbery-u-visa-fraud-indian-nationals-guilty-plea-boston"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The case reinforces a harsh reality for undocumented Indians: desperation to regularize status is fueling criminal schemes that tarnish the broader diaspora's credibility at the worst possible time, when USCIS is tightening scrutiny across every visa category.",
        "tags": ["visa-fraud", "u-visa", "immigration-enforcement", "indian-diaspora", "doj"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "U.S. Department of Justice", "url": "https://www.justice.gov/usao-ma/pr/illegal-alien-india-pleads-guilty-visa-fraud-conspiracy"},
            {"name": "Worcester Telegram & Gazette", "url": "https://www.telegram.com/story/news/courts/2026/06/24/man-pleads-guilty-to-helping-stage-robbery-of-worcester-liquor-store/90680755007/"},
            {"name": "NOLO Immigration Legal Updates", "url": "https://www.nolo.com/legal-updates/immigration-law-updates-in-2026.html"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/John_Joseph_Moakley_United_States_Courthouse_September_2024.jpg/1280px-John_Joseph_Moakley_United_States_Courthouse_September_2024.jpg",
        "image_caption": "John Joseph Moakley United States Courthouse in Boston, where the visa fraud case was heard",
        "image_attribution": "Wikimedia Commons",
        "body": """Mitul Patel, a 40-year-old Indian national living without legal status in Worcester, Massachusetts, pleaded guilty on June 25 in federal court in Boston to one count of conspiracy to commit visa fraud. His crime was not complicated. It was theatrical.

Beginning in March 2023, Patel and at least 10 other Indian nationals participated in a scheme organized by Rambhai Patel — no relation — that staged armed robberies of convenience stores, liquor shops, and fast-food restaurants across Massachusetts and several other states. The objective was not money. It was paperwork.

## The scheme

The U-visa is a nonimmigrant category reserved for victims of serious crimes who cooperate with law enforcement. It offers a path to lawful status and, eventually, a green card. The scheme exploited this by manufacturing the crimes entirely.

Here is how it worked: Rambhai Patel would recruit store clerks and owners willing to play the part of a "victim." A designated "robber" — Indian national Tanveer Sidhu, who pled guilty in October 2025 — would enter the store with an apparent firearm, threaten the clerk, grab cash from the register, and flee to a getaway car driven by Balwinder Singh, also since convicted.

The entire interaction was captured on the store's surveillance video — by design. Five minutes after the "robber" escaped, the clerk would call police to report the "crime." Armed with a police report documenting their supposed victimhood, participants then filed U-visa applications with USCIS.

Each "victim" paid Rambhai Patel for the privilege of being robbed. According to court documents, one participant paid $20,000. In turn, Rambhai Patel compensated store owners for the use of their premises.

At least six stores were hit. At least two participants submitted U-visa applications based on the staged incidents.

## The unraveling

The FBI, USCIS, ICE, and Massachusetts State Police unraveled the ring with assistance from law enforcement spanning New York, Seattle, Louisville, Cleveland, and St. Louis. In March 2026, 11 defendants were charged by criminal complaint. Ten were subsequently indicted in April.

Rambhai Patel and Sidhu had already been convicted. Mitul Patel's guilty plea on June 25 makes him the latest to fall. He faces up to five years in federal prison, three years of supervised release, a $250,000 fine, and deportation. Sentencing is scheduled for July 29 before U.S. District Court Judge Myong J. Joun.

The remaining defendants — charged across Massachusetts, Ohio, Kentucky, and Missouri — are presumed innocent pending trial.

## Why this matters to the diaspora

The case lands at a moment when the Indian immigrant community can least afford it.

USCIS is tightening scrutiny on every visa pathway. The $100,000 H-1B fee remains in legal limbo. EB-2 India has gone "Unavailable" on the July visa bulletin. Adjustment of status is being restricted to "extraordinary circumstances." The administration has signaled repeatedly that fraud detection is a top enforcement priority.

A scheme like this does not exist in isolation. Every fraudulent U-visa application consumes adjudication resources, adds to the 10,000-case annual U-visa cap, and delays legitimate victims who actually need protection. And it provides ammunition to lawmakers already inclined to restrict immigration pathways.

For the roughly 1.2 million Indians in the undocumented population — many of whom overstayed a valid visa and have no criminal record — the case is a reminder that desperation makes people vulnerable to exploitation. Rambhai Patel charged thousands of dollars for participation in a con that carries a five-year prison sentence and guaranteed deportation.

The broader Indian American community, meanwhile, watches from a different vantage. The community is the second-largest immigrant group in the United States, disproportionately represented in skilled-worker visa queues, and deeply invested in the perception that Indian immigration is lawful and meritocratic. Cases like this complicate that narrative at precisely the wrong time."""
    },

    # ── Article 2: Adjustment of Status Restricted ──
    {
        "id": str(uuid.uuid4()),
        "headline": "The Green Card You Could Get Without Leaving America? USCIS Just Made It 'Extraordinary'",
        "subheadline": "A policy memo has quietly upended decades of immigration practice: foreign nationals in the US on work visas must now demonstrate exceptional circumstances to adjust status domestically, or return to India for consular processing — disrupting careers, families, and years of planning.",
        "slug": make_slug("uscis-adjustment-of-status-extraordinary-consular-processing-india-h1b"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the hundreds of thousands of Indian H-1B and L-1 workers who assumed they would file I-485 in the US and continue working while their green card processed, this policy forces an agonizing choice: leave America to apply from India, risking career disruption and reentry uncertainty, or try to prove 'extraordinary circumstances' under standards USCIS has not yet defined.",
        "tags": ["adjustment-of-status", "consular-processing", "green-card", "h-1b", "uscis", "i-485"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS", "url": "https://www.uscis.gov/newsroom/news-releases/us-citizenship-and-immigration-services-will-grant-adjustment-of-status-only-in-extraordinary"},
            {"name": "NOLO Immigration Legal Updates", "url": "https://www.nolo.com/legal-updates/immigration-law-updates-in-2026.html"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/uscis-limits-adjustment-of-status-new-2026-policy-impact/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/us-asks-foreign-nationals-to-apply-for-green-cards-from-home-country/"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center in New York, where adjustment-of-status applicants attend biometrics appointments",
        "image_attribution": "Wikimedia Commons",
        "body": """For more than three decades, foreign nationals lawfully present in the United States — including hundreds of thousands of Indian H-1B and L-1 workers — could count on one thing: if their employer sponsored them for a green card and a visa number became available, they could file Form I-485 and adjust their status to permanent resident without ever leaving the country.

That assumption is now officially unreliable.

## What changed

On May 22, 2026, USCIS issued a policy memo declaring that adjustment of status under Section 245(a) of the Immigration and Nationality Act is "a matter of discretion and administrative grace" — an "extraordinary relief" that is "not designed to supersede the regular consular processing of immigrant visas."

The language is careful but the intent is blunt. USCIS spokesperson Zach Kahler framed it plainly: "From now on, an alien who is in the US temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances."

No effective date was listed. Immigration attorneys assume it applies immediately — including to applications already filed.

## How adjustment of status used to work

The traditional path for an Indian professional on an H-1B went roughly like this: your employer files a PERM labor certification, then an I-140 immigrant petition. When your priority date becomes current on the visa bulletin, you file I-485 — adjustment of status — and remain in the US with work and travel authorization while USCIS processes your case. You keep your job, your kids stay in school, and life continues.

The alternative — consular processing — means flying to India, attending a medical exam and interview at the US consulate in Mumbai, Chennai, Hyderabad, Kolkata, or Delhi, and waiting for visa issuance. It requires leaving your job, pulling your family out of their routine, and hoping that nothing goes wrong at the consulate that delays your return.

For decades, adjustment of status was the default for anyone already in the US. Consular processing was for people applying from abroad.

## What the memo actually requires

The memo does not eliminate adjustment of status entirely. It instructs USCIS officers to treat it as a discretionary benefit and to weigh "the totality of the circumstances" before granting it. Applicants now bear "the burden of showing why administrative discretion should be favorably exercised."

Officers are told to consider family ties, immigration status history, moral character, and "any other relevant factor." Crucially, the memo states that an applicant's "attempt to avoid the ordinary consular immigrant visa process" is itself an adverse factor that must be offset by "unusual or even outstanding equities."

When denying an adjustment request, officers must issue a written notice explaining which negative factors outweighed the positive ones.

After backlash from the business community, Kahler clarified on May 23 that exceptions would be made for applicants who provide an "economic benefit or otherwise are in the national interest" — though the memo itself does not define either standard.

## Where it gets complicated for Indians

The timing could hardly be worse for Indian nationals in employment-based queues.

The July 2026 visa bulletin moved EB-2 India to "Unavailable" — the first time in recent memory the category has gone completely dark. EB-1 India retrogressed by 3.5 months. The only forward movement was in EB-3, which advanced a single month.

For someone who has waited a decade in the EB-2 queue, filed I-140 years ago, and now faces a category that is unavailable, the AOS policy adds a second layer of uncertainty: even when EB-2 reopens and their date becomes current, filing I-485 in the US is no longer guaranteed.

The practical consequences cascade. An H-1B worker who leaves for consular processing in India faces:

- **Career disruption**: Leaving the US for weeks or months for an interview with no guaranteed timeline. Consulate appointment backlogs in India currently run 75 to 125 days for employment-based visas.

- **Reentry risk**: The Supreme Court's June 25 ruling expanded border officials' authority to treat returning green card holders as applicants for admission. For someone in the middle of the permanent residency process, leaving the country carries more risk than ever.

- **The 180-day unlawful presence trap**: Anyone who has accrued more than 180 days of unlawful presence — which can happen inadvertently during status gaps — triggers a three-year or ten-year bar on reentry the moment they depart.

- **No defined timeline**: The memo offers no processing benchmarks for how long an overseas consular case should take, and the State Department's own backlogs are substantial.

## The dual-intent question

One area of ambiguity works partially in Indians' favor. The memo acknowledges that H-1B and L-1 visas are "dual intent" categories, meaning their holders are legally permitted to pursue permanent residency while working on temporary visas. The memo suggests that being in a dual-intent category will not itself count as a negative factor.

But it is not a positive one either. Maintaining lawful status in a dual-intent category is "not sufficient, on its own, to warrant a favorable exercise of discretion," the memo states. Something more is needed — though what that something is remains undefined.

## What to do now

Immigration attorneys are advising clients to prepare as though adjustment of status will be scrutinized. That means assembling documentation of positive equities: letters from employers describing the applicant's economic contribution, evidence of community ties, tax compliance records, children enrolled in US schools, and property ownership.

For applicants with approved I-140s whose priority dates are not yet current, the advice is simpler and bleaker: wait, and hope the policy is challenged in court or reversed before your date arrives.

Legal challenges are expected. The memo represents a dramatic departure from decades of administrative practice, and several immigration law organizations have signaled they are exploring litigation. But court relief, if it comes, will not come quickly.

In the meantime, the path to a green card for Indians in the US just acquired a forced detour through the country they left years ago — one that comes with no guarantee of a smooth return."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
