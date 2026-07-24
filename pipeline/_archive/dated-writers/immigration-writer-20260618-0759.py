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

eb5_body = """The wealthiest legal route to a U.S. green card for Indians has just run out of road. The State Department, in coordination with U.S. Citizenship and Immigration Services, confirmed this week that every available EB-5 unreserved immigrant visa chargeable to India for fiscal 2026 has been issued. No more will be granted to Indian investors until October 1, when the fiscal 2027 numbers reset.

For a category that was supposed to be the express lane — write a large check, skip the decade-long employment queues — the message is blunt: even money now waits in line.

## What just happened

The EB-5 program lets foreign nationals secure permanent residency by investing in U.S. enterprises that create American jobs. The standard threshold is $1.05 million, or $800,000 for projects in targeted employment areas. In return, investors and their families historically moved years faster than the EB-2 and EB-3 crowd stuck behind India's per-country cap.

That advantage has been narrowing, and this week it hit a wall. The State Department said the annual allocation of EB-5 unreserved visas available to India was fully consumed by June 5. The exhaustion follows the same fate for the EB-2 category, which the department declared fully used for Indian applicants back on May 22.

What makes the timing sting is that fiscal 2026 actually had *extra* supply. Under the EB-5 Reform and Integrity Act of 2022, unused reserved visas from fiscal 2024 were rolled into the unreserved pool this year. Even with that cushion, Indian demand drained the well months before the fiscal year ends.

## Why Indians blew through the quota

The surge is not hard to explain. As EB-2 and EB-3 India backlogs ballooned past a decade — and as the June visa bulletin pushed EB-2 India *backward* by more than ten months to a September 2013 cutoff — affluent Indian families increasingly treated EB-5 as the only category where a finish line was actually visible.

There was also a deadline-driven rush at the front end. USCIS fees for the initial EB-5 petition (Forms I-526 and I-526E) jumped from $3,675 to $11,160 on April 1, with the I-829 condition-removal fee climbing to $9,525. Investors raced to file before the increase, swelling the pipeline of approved petitions all chasing the same finite pool of visa numbers.

## What it means for the diaspora

For Indian families weighing EB-5, three practical realities now apply.

First, the door is not shut — it is paused. Visa issuance is expected to resume October 1 when fiscal 2027 numbers become available. Petitions already approved do not vanish; they queue for the next allocation.

Second, the "buy your way out of the backlog" pitch needs an asterisk. EB-5 remains dramatically faster than EB-2 or EB-3 for India-born applicants, but the category now has a backlog and a final-action date of its own. A check no longer guarantees a green card on a predictable timeline.

Third, concurrent filing still matters. India- and China-born investors who select a strategic Regional Center project can file their adjustment of status alongside the initial EB-5 petition, which — per current processing times — can deliver a green card in roughly 12 months from filing for those who get in before a category retrogresses. That window is exactly what just closed for this fiscal year.

The broader lesson for the diaspora is uncomfortable. Across EB-1, EB-2, EB-3 and now EB-5, every employment-based avenue for Indians is bottlenecked at once. The category that was meant to be the pressure-release valve has filled up too. For Indian professionals doing the math on permanent residency, fiscal 2027 cannot come soon enough — and even then, the relief may be measured in weeks, not years."""

f1_body = """The two-minute conversation that decides an Indian student's American future just got harder. Consular officers across U.S. missions are subjecting F-1 student visa applicants to sharply tougher questioning in 2026, scrutinising academic logic, money trails and career plans in interviews that often last less than 120 seconds — and rejecting more applicants who fumble the answers.

For the roughly 300,000 Indians who make up the largest cohort of international students in the United States, the shift turns what was once a procedural formality into the highest-stakes job interview of their lives.

## What changed at the window

According to a roundup of study-abroad developments this week, consular officers are now placing heightened emphasis on four areas: academic progression, course and university selection, source of funds, and post-graduation intentions. The pattern is consistent across posts — large unexplained bank deposits and weak justifications for a chosen program are the fastest ways to a refusal.

The interviews themselves remain brutally short. Officers are making decisions within two minutes, which means applicants get almost no room to recover from a shaky opening answer. A student who cannot explain in a sentence why they chose a particular master's program, or why their funding statement shows a sudden six-figure deposit, can be denied before they finish their second response.

Layered on top is the social-media regime that took hold over the past year. The DS-160 now requires applicants to disclose every social media handle used in the previous five years and to set those profiles to public for review. Consular officers are explicitly instructed to treat restricted visibility as a red flag — an apparent attempt to hide something — and to scan for any content suggesting hostility toward the United States.

## Why Indian students are uniquely exposed

The funding question lands hardest on Indian families. Education abroad is frequently financed through a patchwork of loans, gold-backed credit, family contributions and recently liquidated assets — exactly the kind of activity that produces the "large unexplained deposit" now drawing scrutiny. A transfer that is entirely legitimate in Indian financial practice can read as a red flag to an officer trained to spot manufactured bank balances.

The post-graduation question is equally fraught. Officers want to hear genuine intent to study, yet Indian students are often candid about wanting to use STEM OPT and the H-1B pathway afterward. Threading that needle — demonstrating real academic purpose without tripping the "intending immigrant" wire — has become an art form.

There is a silver lining, and it is squarely in India's wheelhouse. STEM fields remain the strongest bet. Programs in artificial intelligence, cybersecurity, data science, engineering and healthcare continue to draw favourable outcomes, thanks to STEM OPT extension eligibility and strong graduate employment rates — precisely the disciplines Indian applicants dominate.

## How to prepare

For the diaspora's incoming cohort, the practical playbook is tightening:

- **Document the money.** Be ready to explain every significant deposit with paperwork — loan sanction letters, sale deeds, gift affidavits. "My uncle helped" is not an answer; a paper trail is.
- **Own the academic logic.** Know exactly why this program, this university, this city — in one crisp sentence. Vagueness reads as a cover story.
- **Clean and open the socials.** Make profiles public well before the interview, list every handle honestly, and assume an officer will look. Omitting an account can sink an otherwise strong case.
- **Lean into STEM credibility.** A coherent technical narrative tied to a high-employment field is the single best signal an applicant can project.

The pipeline that funnels Indian talent into American universities — and eventually into American tech — now runs through a two-minute gate that is narrower than it has been in years. For families who have already wired tuition and signed leases, the interview is no longer a rubber stamp. It is the whole game."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Even the Million-Dollar Green Card Line Is Full: EB-5 India Runs Dry Until October",
        "subheadline": "The category that was supposed to let wealthy Indians skip the decade-long backlog has exhausted its fiscal 2026 visas — proof that for India-born applicants, every employment-based lane is now jammed.",
        "slug": make_slug("eb5-india-unreserved-visas-exhausted-fiscal-2026-october-reset"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "EB-5 was the affluent Indian family's escape hatch from the EB-2/EB-3 backlog; its exhaustion until October means even seven-figure investments now face a queue and a retrogression date of their own.",
        "tags": ["eb5", "green-card", "visa-bulletin", "investor-visa", "india-backlog"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "India-West News", "url": "https://www.indiawest.com/news/eb-5-visa-limit-reached-for-indians-until-october/"},
            {"name": "Fragomen, Del Rey, Bernsen & Loewy LLP", "url": "https://www.fragomen.com/insights/can-you-avoid-the-upcoming-eb-5-government-fee-increases.html"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/uscis-limits-adjustment-of-status-new-2026-policy-impact/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An open passport displaying visa stamps, illustrating the U.S. immigrant visa process",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": eb5_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Two-Minute Gate: F-1 Visa Interviews Get Tougher Just as India Files for Fall",
        "subheadline": "Consular officers are grilling student-visa applicants on funding, course choice and career plans — and a shaky answer or a locked-down social profile can mean a refusal in under two minutes.",
        "slug": make_slug("f1-student-visa-interviews-tougher-2026-india-funding-social-media-scrutiny"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India sends the largest cohort of international students to the U.S.; the new emphasis on explaining bank deposits and social media history hits Indian families' loan-and-gold financing patterns hardest, even as STEM fields remain a strong bet.",
        "tags": ["f1-visa", "student-visa", "opt", "stem-opt", "social-media-vetting", "study-abroad"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "This Week in Study Abroad (Radius)", "url": "https://www.linkedin.com/pulse/this-week-study-abroad-twisa-vol-9-visa-interviews"},
            {"name": "Fragomen, Del Rey, Bernsen & Loewy LLP", "url": "https://www.fragomen.com/insights/visa-applicants-now-required-to-disclose-social-media-use-prior-contact-information.html"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/social-media-vetting-rules-will-dictate-visa-interview-restart"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "International students walking on a U.S. university campus",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": f1_body
    }
]

for art in articles:
    try:
        wc = len(art["body"].split())
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
