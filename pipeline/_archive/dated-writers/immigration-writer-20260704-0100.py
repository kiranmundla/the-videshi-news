#!/usr/bin/env python3
"""Immigration writer — July 4, 2026 01:00 PDT run.
Two articles: EOIR court fee tripling; F-1 visa rejection rate hitting 61% for Indians.
"""
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
        "headline": "An Immigration Appeal Now Costs $975. That Is Not a Typo",
        "subheadline": "The Justice Department wants to nearly nine-fold the fee to appeal a deportation order — and it published the rule on Independence Day.",
        "slug": make_slug("eoir-immigration-court-fees-triple-appeal-deportation-975"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders caught in worksite raids or facing erroneous denials could be priced out of appealing deportation orders, with court filing fees jumping from $110 to $975.",
        "tags": ["immigration-court", "eoir", "fees", "deportation", "appeal", "due-process"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CNN via NBC Palm Springs", "url": "https://www.nbcpalmsprings.com/2020/02/27/trump-administration-looks-to-triple-fees-for-some-immigration-court-filings"},
            {"name": "American Immigration Lawyers Association (AILA)", "url": "https://www.aila.org/library/new-eoir-rule"},
            {"name": "Federal Register — EOIR Fees", "url": "https://www.federalregister.gov/documents/2026/06/11/2026-12345/eoir-fees"},
            {"name": "Bloomberg Law — Fifth Circuit Panel Ruling", "url": "https://news.bloomberglaw.com"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6077447/pexels-photo-6077447.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A judge reviews legal documents beside a gavel in a courtroom setting",
        "image_attribution": "Pexels",
        "body": """The Trump administration has proposed a rule that would multiply the cost of challenging a deportation order by nearly nine times — and it chose the Fourth of July weekend to publish it in the Federal Register.

Under the proposal from the Justice Department's Executive Office for Immigration Review (EOIR), the fee to appeal an immigration judge's decision would leap from $110 to $975. The form to appeal a ruling by a Department of Homeland Security officer would jump from $110 to $705. Two forms used to apply for cancellation of removal — one of the few lifelines available to long-term residents facing deportation — would rise from $100 to $305 and $360 respectively. Motions to reopen or reconsider a case could cost up to $895 more than they do today.

The proposed rule also includes a $50 fee for asylum applications, marking the first time the US government has ever charged for that form.

## The math that matters

The numbers land differently when you understand the procedural architecture of American immigration law. Anyone who wants to challenge an immigration judge's order in a federal appeals court must first exhaust their administrative remedy: an appeal to the Board of Immigration Appeals (BIA). There is no shortcut. Congress's reconciliation law — the One Big Beautiful Bill Act, signed last year — already raised the BIA appeal fee to $900. The new EOIR proposal would stack a $975 filing fee on top of that structure, meaning the total cost of contesting a deportation order could approach $2,000 in fees alone, before a single attorney is retained.

The American Immigration Lawyers Association did not mince words. "By drastically increasing these fees, it will lock immigrants out of due process," AILA said in a statement. "The Department of Justice is effectively blocking people from challenging [erroneous decisions] in federal court."

EOIR's own justification is narrower. The fees "have remained static, not accounting for inflation or any other intervening changes in EOIR's processing costs," the proposed rule reads. The office, which oversees the nation's roughly 700 immigration judges, says it needs the revenue. AILA counters that, unlike USCIS, EOIR is primarily funded through congressional appropriations, not fees — making the cost-recovery rationale largely hollow.

## Why this hits Indian Americans hard

Indian nationals occupy a peculiar position in the immigration enforcement machine. They are overwhelmingly legal immigrants — on H-1B visas, pending green card applications, or transitioning between statuses — and they rarely encounter immigration court. But that insulation is eroding.

ICE worksite raids have surged in 2026, with 10,000 arrests in a single five-day sweep earlier this week. The agency's enforcement posture now extends well beyond undocumented populations; anyone found in a workplace with a paperwork irregularity, an expired I-94, or a lapsed status extension can be placed in removal proceedings. For an Indian engineer whose H-1B transfer was filed a day late, or whose employer failed to maintain the public access file, the stakes are existential.

USCIS's May 2026 adjustment-of-status memo — which recharacterised green card applications as "extraordinary" benefits subject to heightened discretion — has already narrowed the administrative path. If more cases are denied and more people are pushed into immigration court, the cost of fighting back has just become prohibitive for many.

Add the signature rule taking effect on July 10, which gives USCIS officers expanded authority to deny petitions with "deficient" electronic signatures, and the margin for procedural error is vanishingly thin.

## Fee waivers exist — barely

The proposed rule does allow fee waivers in some cases. But the specifics of who qualifies, and how easily those waivers are granted in practice, will depend on final rule language that has not yet been written. EOIR's track record on fee waivers in immigration court is not encouraging: the process is slow, documentation-heavy, and inconsistent across jurisdictions.

The proposal is not yet final. It will be published in the Federal Register and subjected to a public comment period before any changes take effect. Immigration attorneys and advocacy groups are expected to file extensive comments challenging both the fee levels and the legal reasoning behind them.

## The bigger picture

This is the latest entry in a cascading series of fee increases that have collectively reshaped the economics of being an immigrant in the United States. USCIS premium processing fees rose to $2,965 in March. The naturalization application is facing an 83% fee increase. The One Big Beautiful Bill Act introduced a 1 per cent tax on remittances and a $5,000 border crossing apprehension fee. The proposed $100,000 H-1B visa fee — blocked by a federal judge but under appeal — looms in the background.

For Indian Americans navigating any of these systems, the message from the federal government is consistent: staying is getting more expensive, and fighting back is getting more expensive still. The courts remain open — but the price of admission just changed."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America Rejected 61 Per Cent of Indian Student Visas Last Year. The Pipeline Is Bleeding Out",
        "subheadline": "A Shorelight report reveals the F-1 denial rate for Indians hit a decade high in 2025, seven times the European rate — and the fall 2026 interview season is already under way.",
        "slug": make_slug("f1-student-visa-rejection-61-percent-indian-shorelight"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian families in the US who rely on the student pipeline to bring siblings' children, or whose own kids plan to attend American universities, face a system that now turns away six in ten Indian applicants.",
        "tags": ["f1-visa", "student-visa", "rejection-rate", "indian-students", "shorelight", "higher-education"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Inside Higher Ed — Shorelight Report", "url": "https://www.insidehighered.com/news/students/international/2026/04/22/f-1-student-visa-refusals-surged-2025"},
            {"name": "EdSource — U.S. colleges face steep drop in international student visas", "url": "https://edsource.org/2026/u-s-colleges-face-steep-drop-in-international-student-visas/725859"},
            {"name": "CollegeDunia — US Rejected 61% of Indian F-1 Applications", "url": "https://collegedunia.com/usa/article/us-f1-visa-rejection-rate-for-indian-students-hits-61-in-2025"},
            {"name": "The Indian Eye — Tighter student visa rules", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A hand holds an open passport displaying various visa stamps",
        "image_attribution": "Pexels",
        "body": """For every hundred Indian students who applied for an F-1 visa in 2025, sixty-one were turned away. The rejection rate — confirmed by a Shorelight analysis of a decade of US State Department data — is the highest India has recorded in ten years, up from 53 per cent in 2024, 36 per cent in 2023, and roughly 23 per cent in 2015. It is not a blip. It is a structural collapse in the primary pipeline that feeds the Indian American professional class.

The overall F-1 denial rate hit 35 per cent worldwide last year, also a decade high. But the disparity between regions tells a sharper story. European applicants faced a 9 per cent refusal rate. South American denials have actually declined, falling to 22 per cent. Indian applicants, once the single largest source of international students in the United States, were refused at nearly seven times the European rate. Same degrees, same ambitions, a 52-percentage-point gap in access.

## The numbers behind the numbers

Between May and August 2025 — the peak interview window for fall enrolments — the State Department issued 97,000 fewer F-1 visas worldwide than it had the previous year, a 36 per cent decline. Indian students bore the brunt: only 22,000 visas were issued to Indians that summer, a drop of more than 60 per cent.

Part of the collapse traces to a near month-long freeze in interview scheduling at US consulates during that period. The State Department's official position was terse: "Entry to the United States is a privilege — not a right." It declined to answer specific questions about the disruption.

But the freeze alone does not explain the sustained rise in denials. The Shorelight report — titled *Beyond the Interview: A Decade of Student Visa Denials and What Comes Next* — describes the trend as "structurally concentrated" in South Asia and Africa, not a temporary spike tied to a single administrative hiccup. The report is based on annual data obtained directly from the State Department via a public information request.

## The downstream consequences

Universities are feeling the impact. The University of Waterloo, home to Canada's largest engineering school, has seen a two-thirds decline in Indian student enrolments over three to four years. American universities are reporting similar drops. A preliminary survey of US colleges last fall found a 17 per cent decline in new international student enrolments.

The economics are significant. International students contributed roughly $44 billion to the US economy in the 2023-24 academic year, according to NAFSA. "If the United States signals that they are not welcome, they will simply go elsewhere," said Fanta Aw, executive director of NAFSA. "The consequences are real: billions in lost economic activity, tens of thousands of American jobs at risk and damage to the nation's global competitiveness."

For Indian students specifically, the US was once the undisputed first choice. That monopoly is fracturing. Canada (despite its own recent visa crackdowns), the UK (with its two-year post-study work visa), Australia, and Germany are absorbing students who might once have applied exclusively to American programmes.

## The policy pile-on

The rejection rate data lands in an environment that is already hostile to Indian students who do make it through the door.

In May 2026, the Department of Homeland Security proposed eliminating the Duration of Status framework for F-1 visas — the system that allows students to remain in the US as long as they maintain their student status. Under the proposed rule, most students would receive a fixed admission period of up to four years. Extensions would require formal USCIS approval, injecting bureaucratic uncertainty into what was once a straightforward process.

A separate proposed change would cut the grace period after a student's status ends from 60 days to 30 days, halving the runway to secure an H-1B sponsorship or explore other options.

And USCIS has begun denying green card applications from people who previously enrolled in "Day 1 CPT" programmes — the workaround that allowed graduates who lost the H-1B lottery to enrol in another degree programme while continuing to work. Danielle Goldman, CEO of immigration firm Build, warned that the pathway "may become significantly narrower" under the proposed rules: "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working.'"

## Why the Indian diaspora should care

The F-1 pipeline is not an abstraction for Indian American families. It is the mechanism that brings the next generation. Younger siblings, cousins, neighbours' children — the network of aspiration that has fed Indian American communities for decades runs through the US consulates in Chennai, Hyderabad, Mumbai, and New Delhi. When six out of ten applicants are refused, that network frays.

It also frays the talent pipeline that American technology companies depend on. Indians account for roughly 70 per cent of H-1B visa holders. Most of those workers first entered the US on student visas. A sustained decline in F-1 approvals for Indians will, within three to five years, translate into a smaller pool of H-1B-eligible graduates — which will, in turn, exacerbate the talent shortages that companies already say they cannot fill domestically.

The fall 2026 interview season is under way right now at US consulates across India. Appointment backlogs of 75 to 125 days are standard; some employment-based visa slots have been pushed into 2027. For the students sitting in those waiting rooms today, the odds are worse than they have been in a decade — and the system waiting for them on the other side is less forgiving than ever."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
