#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
for cand in [Path.home()/".env.supabase", Path.home()/"workspace"/".env.supabase"]:
    if cand.exists():
        for line in cand.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break

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

body1 = """The end of "Duration of Status" has been threatened before. This time it has cleared the last bureaucratic checkpoint that matters.

The White House's Office of Management and Budget has finished its review of a Department of Homeland Security rule that would scrap the open-ended stay framework international students have lived under for four decades. The final rule (catalogued as RIN 1653-AA95) now sits one step from publication in the Federal Register. Once it appears there, the clock starts: the change takes effect 60 days later.

For roughly 360,000 Indian students in the United States — the largest single national cohort on American campuses — this is not an abstract regulatory footnote. It rewrites the basic terms of how long they are allowed to stay.

## What "Duration of Status" actually does

Since 1978, F-1 students have been admitted for "duration of status," shorthand D/S on their paperwork. It means there is no fixed expiry date stamped on their stay. As long as a student stays enrolled full-time, makes normal academic progress and follows the visa rules, they remain in lawful status — whether that takes four years or eight. The same flexibility extends to J-1 exchange visitors and I-visa foreign media.

That elasticity is what makes the American student-to-worker pipeline function. A student can roll from a bachelor's into a master's, pick up Optional Practical Training (OPT), extend into the 24-month STEM OPT window, and enter the H-1B lottery — all without applying for a new period of admission each time.

## What replaces it

The DHS rule swaps D/S for a fixed admission period, capped at four years for most students, after which any additional time requires a formal extension application filed with U.S. Citizenship and Immigration Services. Doctoral candidates, researchers and anyone in a programme that runs long — a large share of the Indian cohort — would be the first to collide with the ceiling. The rule also trims the post-completion grace period from 60 days to 30, and tightens the rules on transferring schools or switching programmes midstream.

The practical effect is to convert a relationship students currently manage through their university's international office into a recurring transaction with a federal agency whose processing times are measured in months, not weeks.

## Why this lands hardest on Indians

Indian students are concentrated precisely in the programmes the rule squeezes: long STEM master's and PhD tracks in computer science, AI, engineering and data science. They also lean most heavily on the OPT-to-H-1B ladder, because for most of them OPT is the only legal bridge to staying and working after graduation.

Stack a fixed four-year cap on top of an H-1B lottery that already rejects most applicants, and the math gets unforgiving. A student who needs an extension to finish a dissertation now files paperwork that could leave them in limbo while USCIS adjudicates — and a pending extension is a far weaker footing than the settled status D/S provided. The shorter grace period compounds it: a graduate who doesn't line up the next step within 30 days has less runway to pivot before falling out of status.

Immigration practitioners point to a second-order effect. The "Day 1 CPT" route — enrolling in another programme to keep work authorisation alive after an H-1B miss — gets considerably narrower under a fixed-term regime, removing one of the few fallbacks Indian graduates have leaned on.

## What happens next

The rule is final, not proposed, which means there is no further public comment period to slow it. Publication could come at any time; the text won't be public until roughly 24 hours before it lands. Litigation is likely — education groups and universities fought an almost identical Trump-era proposal in 2020, and immigration attorneys are already signalling an "arbitrary and capricious" challenge once the rule publishes. A court could pause it, as courts have paused other recent immigration measures.

For now, the advice from campus advisers is unglamorous but concrete: finish on time where possible, avoid programme changes that reset the clock, keep documentation airtight, and treat any extension as something to plan months ahead rather than weeks. The era of not having to think about your end date is closing.

Sources: Bloomberg Law, NAFSA, Outlook Business, The Times of India, ICEF Monitor."""

body2 = """A U.S. visa, the State Department likes to repeat, "is a privilege, not a right." Increasingly, keeping that privilege means handing over your social media history — and Indian applicants now sit squarely inside the dragnet.

What began in June 2025 as a screening requirement aimed at students has metastasised into one of the broadest online-surveillance regimes in U.S. visa history. The most recent expansion, effective March 30, 2026, added 14 more visa categories to mandatory social media vetting. The program now reaches F, M and J students, H-1B workers and their H-4 dependents, fiancé(e) applicants, religious workers, and a long tail of other categories. For the Indian diaspora — the single largest source of H-1B workers and international students — there are few visa lines left that the policy does not touch.

## What you have to disclose

The mechanics are blunt. The social media fields on the DS-160 application form, once optional, are now required. Applicants must list every social media handle and platform they have used in the past five years — including dormant accounts. Omitting a platform can itself be grounds for denial.

The most consequential instruction is the privacy one: the State Department has asked affected applicants to set their accounts to "public" so consular officers can review posts, tagged photos, connections and any discrepancies between an online profile and the rest of the application — a mismatch between a LinkedIn work history and a DS-160, for instance, can trigger scrutiny.

## The "hostile attitudes" problem

What officers are screening for is where the policy gets slippery. The published guidance flags content that could be read as supporting terrorism, antisemitism, or threats to national security. But it also instructs officers to weigh undefined "hostile attitudes" toward the United States and "political activism" — categories with no clear boundary.

USCIS has separately said that "any involvement in anti-American or terrorist organizations" and evidence of "antisemitic activity" will count as an "overwhelmingly negative factor" in discretionary decisions. Immigration lawyers warn that handing officers vague standards plus a "satisfaction of the consular officer" threshold is a recipe for inconsistent, unpredictable outcomes — the kind that are nearly impossible to appeal.

## Why this is an Indian story

Three reasons. First, scale: Indians dominate the H-1B and student categories that the vetting now blankets, so a larger share of Indian applicants run through enhanced screening than any other nationality. Second, the H-4 inclusion sweeps in spouses and dependent children — meaning a single family's filing can multiply into several separate social media reviews.

Third, and most practically, the screening is slow. Enhanced vetting routinely lands applicants in "administrative processing" — a 221(g) refusal that shows up as "Refused" in official records even when it is merely a temporary review step. For an Indian H-1B holder who travelled home to get a visa stamped, that limbo can mean weeks or months stranded abroad, away from a job and a mortgage, with no firm date for resolution. Layered on top of already-stretched appointment backlogs at Indian consulates, the cumulative delay is the real cost.

## The political pushback

The policy has critics inside Washington. Representative Raja Krishnamoorthi, the Illinois Democrat and one of the most prominent Indian-American voices in Congress, has called the student-visa freeze and "sweeping, undefined social media vetting" a "reckless decision" and a "strategic blunder," arguing it pushes global talent toward countries that welcome it. He has separately pressed Homeland Security Secretary Kristi Noem to explain what standards DHS uses to assess the data it collects and what analysis it has done on the impact to legitimate travel.

Those objections have not changed the rules. The vetting stands, and the category list keeps growing.

## What applicants can do

The guidance from immigration counsel is defensive and specific: list every platform used in the last five years, including old or inactive ones; make accounts public before the interview rather than scrambling at the consulate; ensure consistency between your online presence and your application; and build extra time into travel plans, because administrative processing can stretch a routine stamping into a months-long wait. None of it guarantees a fast outcome — but the alternative, an unexplained omission or a flagged inconsistency, is far worse.

Sources: U.S. Department of State, Boundless, NAFSA, Travel Noire, Bloomberg Law, The Indian Eye."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Rule That Ends 'Stay as Long as You Study' Just Cleared Its Last Hurdle",
        "subheadline": "A DHS rule replacing open-ended student status with a four-year cap has cleared White House review and now awaits only publication. Indian students, the largest cohort on U.S. campuses, are first in line to feel it.",
        "slug": make_slug("dhs-duration-of-status-final-rule-omb-cleared-four-year-cap-f1-indian-students"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Roughly 360,000 Indian students — concentrated in the long STEM master's and PhD programmes the rule squeezes hardest, and most dependent on the OPT-to-H-1B ladder — would have to start asking USCIS for permission to finish their degrees.",
        "tags": ["f1-visa", "duration-of-status", "opt", "uscis", "students", "dhs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law — White House Reviewing Rule to Limit Foreign Students' Status", "url": "https://news.bloomberglaw.com/daily-labor-report/white-house-reviewing-rule-to-limit-foreign-students-status"},
            {"name": "Outlook Business — US Clears Visa Rule Change", "url": "https://www.outlookbusiness.com/economy-and-policy/us-clears-visa-rule-change-foreign-students-may-face-stay-limits"},
            {"name": "ICEF Monitor — US to end Duration of Status for F, J, and I visas", "url": "https://monitor.icef.com/2026/06/us-to-end-duration-of-status-for-f-j-and-i-visas/"},
            {"name": "The Indian Eye — Tighter student visa rules may impact Indians", "url": "https://theindianeye.com/"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "International students walking on a university campus; a new DHS rule would cap how long they can stay.",
        "image_attribution": "Pexels",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Set Your Accounts to Public: U.S. Visa Vetting Now Reaches H-1B and H-4 Indians",
        "subheadline": "Mandatory social media disclosure that started with students has expanded across more than a dozen visa categories — and the Indian diaspora, which dominates the H-1B and student lines, runs through the screening more than any other nationality.",
        "slug": make_slug("us-visa-social-media-vetting-expansion-h1b-h4-students-india-ds160-disclosure"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians make up the largest share of H-1B and student applicants now subject to mandatory social media screening, and the inclusion of H-4 dependents means a single family's filing can trigger several separate reviews — each one a chance to land in months-long administrative processing.",
        "tags": ["social-media-vetting", "ds-160", "h1b", "h4", "students", "consular-processing"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Boundless — U.S. Expands Social Media Vetting to More Applicants", "url": "https://www.boundless.com/blog/social-media-vetting-expansion/"},
            {"name": "NAFSA — Eleven Things to Know About the New Social Media Vetting Guidelines", "url": "https://www.nafsa.org/"},
            {"name": "Travel Noire — State Department Requests Visa Applicants Make Social Media Public", "url": "https://travelnoire.com/"},
            {"name": "The Indian Eye — Raja Krishnamoorthi terms freezing of student visas reckless", "url": "https://theindianeye.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/16229745/pexels-photo-16229745.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A smartphone displaying social media apps; U.S. visa applicants must now disclose five years of accounts.",
        "image_attribution": "Pexels",
        "body": body2
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"[{wc} words] {art['headline'][:60]}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
