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

body_eb5 = """The clock that matters most to Indian families chasing a green card by cheque is not the visa bulletin. It is a calendar date: September 30, 2026. After that, the rulebook that made the EB-5 investor visa the fastest legal escape from the H-1B trap starts to expire — and the State Department has already warned that one of its most attractive lanes for Indians is about to slam shut.

For a category that was supposed to be the workaround, EB-5 is suddenly running its own race against time.

## The escape hatch Indians have been buying

EB-5 lets a foreign national put $800,000 into a qualifying U.S. project (or $1,050,000 outside a targeted employment area) and, in exchange, file for a green card without an employer sponsor. For Indians stuck in the EB-2 queue — where the final action date has retrogressed to September 1, 2013, and waits run past fifteen years — the math has been brutal enough to justify writing the cheque.

The numbers show it. Of roughly 13,520 EB-5 petitions filed worldwide between April 2022 and July 2025, nearly 22% came from India, making it the second-largest source after China. The surge tracks almost perfectly with the bad news elsewhere: the $100,000 H-1B fee fight, the rollback of H-4 spousal work permits, the weighted lottery that favours the highest bidders, and a USCIS policy note nudging green card applicants to file from their home countries. Each tightening of the screws on temporary status sends another mid-career engineer to an immigration lawyer's office asking about the investor route.

## Why the unreserved lane is about to retrogress

Here is the catch. EB-5 splits into two worlds. The "reserved" set-asides — rural, high-unemployment, and infrastructure projects — remain current for India as of the June 2026 bulletin. The "unreserved" category, which covers older pre-2022 filings and projects outside those targeted zones, sits frozen at a May 1, 2022 final action date, and the State Department has flagged that it could retrogress or go unavailable "in the next month" as it tries to stay within the FY 2026 visa limit.

Charles Oppenheim, the former State Department official widely regarded as the architect of the visa bulletin, called the warning unsurprising. The department, he said, had been "overly aggressive" in advancing the India unreserved date to May 2022, and a correction was always coming. All available EB-5 numbers for Indian applicants will be used under the FY 2026 cap — the only question is whether they run out in summer or limp to the fiscal-year line on September 30.

If the unreserved date does retrogress, applicants inside the U.S. lose the single biggest perk of filing right now: the ability to submit Form I-526E and Form I-485 together. That concurrent filing is what lets an investor pull an interim work permit and travel document while the petition crawls forward. Take it away, and the wait to even file the I-485 stretches by years.

## The September 30 deadline nobody should ignore

Layered on top is the grandfathering cliff written into the EB-5 Reform and Integrity Act of 2022. Investors who file before September 30, 2026 are locked into the current Regional Center Program rules. File after, and they are exposed to whatever Congress does — or fails to do — when the authorization lapses. Source-of-funds documentation alone takes four to six weeks to assemble properly, which means an investor who starts the paperwork in late summer is already cutting it fine.

## What this means for the diaspora

For an Indian professional who has spent a decade in H-1B limbo, the EB-5 decision has narrowed to a few hard weeks. The reserved rural lane still offers a current date and the fastest processing — I-526E approvals in four to nine months — but carries its own retrogression risk as cases pile in. The unreserved lane, the one many older filers are sitting in, is the one being warned about. And the grandfathering deadline applies to everyone.

There are real-world complications Indians face that others do not: RBI and Liberalised Remittance Scheme limits on moving capital abroad, Tax Collected at Source on remittances that can throttle funding timelines, and FEMA scrutiny of offshore loan structures. None of those clocks care about the visa bulletin either.

The uncomfortable truth is that EB-5 was always the rich cousin's path — $800,000 is not a rounding error for most H-1B families. But for those who can write the cheque, the message from Washington this month is unambiguous: the window that made it worth the money is closing on two fronts at once, and the math gets worse after September 30."""

body_students = """The American degree was always sold to Indian families as a two-part bargain: pay the tuition, then earn it back on Optional Practical Training before the H-1B lottery decides your fate. In the summer of 2026, both halves of that deal are wobbling — and the data shows Indian students are already voting with their feet.

## A 78% collapse

The headline number is stark. In July and August 2025, U.S. F-1 student visa issuances to Indians fell 78% compared with the same months a year earlier — the steepest drop among major source countries, ahead of Nepal's 83% and well past China's 33%. That is not a slow cooling. That is a market reading the room and deciding the trip may not be worth it.

The reasons are stacking up. The State Department's interview-waiver overhaul, effective October 1, 2025, ended the dropbox route for every F-1, F-2, J-1, and M-1 applicant. Where some students once renewed by mail, now every single one — regardless of age — must sit for an in-person interview. The old age-based exemptions for applicants under 14 and over 79 are gone too.

## The Mumbai and Hyderabad squeeze

The pain is not evenly spread. Mumbai and Hyderabad, the two consulates that process the bulk of India's STEM applicants, are showing the longest queues — roughly 2.5-month waits for the next available student visa slot. Worse, both cities concentrate exactly the applicants most likely to get caught in extended administrative processing: students heading into computer science, AI, electrical engineering, and biotechnology, the fields flagged on the U.S. Technology Alert List.

The arithmetic is punishing. A Mumbai-based STEM applicant who books today might reach the interview stage in mid-June, then face a four-to-six-month security review — pushing a decision to October or November, long after the August start date for Fall 2026. Immigration advisers are now telling students to book at New Delhi or Chennai, where waits run shorter, even if it means a domestic flight across the country. A trip to Delhi, as one guide put it, is cheaper than a deferral fee.

## OPT is the whole ROI

Strip away the visa-queue mechanics and the real anxiety is about what comes after graduation. OPT — 12 months of post-study work, extended to 36 for STEM graduates — is the bridge that makes a $60,000-to-$100,000 degree pencil out. It is the runway to repay education loans, gain experience, and hope an employer files an H-1B petition before the clock runs out.

That bridge is under review. Proposals circulating in 2026 would scrap the long-standing "duration of status" framework that lets students stay as long as they remain enrolled, replacing it with a fixed visa term tied to the I-20 plus a 30-day grace period. Other proposals float tighter CPT and OPT monitoring and possible STEM OPT restrictions. None is final. But for a family weighing a deposit cheque this spring, "not final" is not the same as "safe."

The blunt framing came from an Indian commentator quoted earlier in the cycle: without OPT, a U.S. university becomes "an overpriced diploma without job prospects." NAFSA estimates international students, led by Indians, pour roughly $33 billion into the U.S. economy. Kill the work pathway, the argument runs, and watch that money — and those students — go elsewhere.

## What the diaspora should weigh

For Indian admits sitting on a Fall 2026 offer, the advice from counsellors has turned pragmatic rather than panicked. STEM applicants at Delhi or Chennai are generally told to pay the deposit and proceed — a one-month wait plus a 60-day processing hold still lands a visa by late July. Those at Mumbai, Hyderabad, or Kolkata are told to book elsewhere or, in the worst cases, defer. The reasoning cuts against wishful thinking: deferring to Fall 2027 does not make the policy environment clearer, it just delays the same decision by a year.

For non-STEM and MBA admits, the calculus is harder, because their OPT runs only 12 months with no extension. If the post-study work bridge narrows, the return on a $150,000 American MBA changes materially — and no amount of waiting resolves that.

The deeper signal for the diaspora is generational. For two decades, the U.S. STEM degree was the default first step in the Indian middle-class migration story. The 78% drop suggests that default is being questioned in real time, with Canadian, British, and Australian campuses circling the students America is making wait. The families doing the math this year are not anti-American. They are just unwilling to bet six figures on a runway that Washington keeps threatening to shorten."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The EB-5 Escape Hatch Is Closing on Indians From Two Directions at Once",
        "subheadline": "Washington has warned the EB-5 unreserved category for India may retrogress within weeks, even as a September 30 grandfathering deadline narrows the investor-visa window the H-1B backlog made so attractive.",
        "slug": make_slug("eb5-unreserved-retrogression-september-30-grandfathering-deadline-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "EB-5 became the fastest legal green card route for Indians stuck in the 15-year EB-2 backlog, but the unreserved lane is about to retrogress and the September 30 grandfathering deadline is forcing investor families into a few hard weeks of decisions.",
        "tags": ["eb5", "green-card", "visa-bulletin", "investor-visa", "immigration", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "EB5Investors.com — Retrogression looms for Indian EB-5 investors", "url": "https://www.eb5investors.com/news/retrogression-looms-indian-eb5-investors-june-visa-bulletin"},
            {"name": "VisaVerge — Indian EB-5 Visa Retrogression Warning", "url": "https://www.visaverge.com/news/indian-eb-5-visa-retrogression-warning-may-2026-update/"},
            {"name": "Murthy Law Firm — June 2026 Visa Bulletin", "url": "https://www.murthy.com/2026/05/13/june-2026-visa-bulletin/"},
            {"name": "Angel One — US Flags Possible EB-5 Delays for Indian Applicants", "url": "https://www.angelone.in/news/us-flags-possible-eb5-delays-indian-applicants"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/11391951/pexels-photo-11391951.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
        "image_caption": "A seedling sprouting from stacked coins, symbolizing investment-based immigration like the EB-5 program.",
        "image_attribution": "Pexels",
        "body": body_eb5
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Student Visas to America Fell 78% — and the OPT Bridge They Came For Is Wobbling",
        "subheadline": "The end of dropbox renewals, 2.5-month consulate queues in Mumbai and Hyderabad, and proposals to curb OPT are forcing Indian families to rethink the default first step of the American dream.",
        "slug": make_slug("indian-f1-student-visa-78-percent-drop-opt-dropbox-ended-2026"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For two decades the US STEM degree was the default first step in the Indian middle-class migration story; an 78% collapse in F-1 issuances and threats to OPT are forcing families to question a six-figure bet on a shrinking post-study work runway.",
        "tags": ["f1-visa", "opt", "stem-opt", "student-visa", "immigration", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "ICEF Monitor — US student visa issuances fell 36% in summer 2025", "url": "https://monitor.icef.com/2026/03/us-student-visa-issuances-fell-by-36-in-summer-2025/"},
            {"name": "Collegedunia — US F-1 Visa Administrative Processing Surge", "url": "https://collegedunia.com/news/us-f1-visa-administrative-processing-surge-india"},
            {"name": "Collegedunia — Indian OPT Students Travelling Home Must Check F-1 Stamp", "url": "https://collegedunia.com/news/indian-opt-students-f1-visa-stamp-summer-2026"},
            {"name": "IDP — US Student Visa Rules 2026: Key Changes", "url": "https://www.idp.com/india/blog/us-student-visa-rules-2026/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1454360/pexels-photo-1454360.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
        "image_caption": "College students with backpacks walking together on a university campus.",
        "image_attribution": "Pexels",
        "body": body_students
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  [{art['slug']}] word count: {wc}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
