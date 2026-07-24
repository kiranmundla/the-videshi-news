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

article1_body = """A federal court told U.S. Citizenship and Immigration Services to start processing the work-permit applications it had frozen for nearly half a year. Weeks later, the people whose lives depend on those approvals say nothing has actually moved.

The agency quietly paused adjudication of Optional Practical Training applications, STEM OPT extensions, and a swath of green-card filings through internal memos issued in December and January. The stated reason was enhanced vetting for nationals of countries on the administration's expanded travel-ban list. The practical effect was a wall: graduates with job offers in hand, biometrics done, fees paid, and no way to know when — or whether — they would be cleared to work.

## The ruling that changed little

In April, USCIS carved out a narrow exception for physicians, who often begin four-year residencies on OPT. Everyone else stayed in limbo. Then a court ordered the agency to resume evaluating the held applications. USCIS posted a terse response: it "strongly disagrees with the Court's order but will follow its terms pending possible further judicial review."

Following the terms, it turns out, is not the same as catching up. A representative for Press Unpause, the grassroots group that has pushed USCIS to lift the hold, told *Inside Higher Ed* that members have not heard of a single application being processed since the ruling — nor of any refunds being issued. NAFSA, the international-education association, said it was "pleased" with the decision but warned it was "too soon to see it play out on campuses."

For an agency that was already sitting on a substantial backlog, resuming work and clearing it are separate problems. There is no public timeline for either.

## Why Indian graduates are at the center of this

No group has more riding on OPT than Indian students. India sends the largest contingent of international students to American campuses, and the post-study work window is the single most important reason many of them choose the U.S. over Canada, the U.K., or Australia. OPT gives a graduate 12 months of work authorization; the STEM extension stretches that to three years, long enough to ride out two or three H-1B lottery attempts. Lose the OPT clock and the entire pathway from classroom to green card collapses.

The financial damage is already concrete. Students paid the standard filing fees, and some paid an extra $1,800 to expedite applications through premium processing — only to learn afterward that the pause made expedited handling meaningless. USCIS has said it cannot refund those fees until the hold is fully lifted. So the money is gone, the work permit has not arrived, and start dates are slipping.

One F-1 graduate with an MBA from a top program and a job lined up at a major tech firm told *Inside Higher Ed* his employer has already pushed his start date once while waiting on OPT approval. He is not confident they will do it again. That is the quiet arithmetic playing out in thousands of inboxes: an employer's patience is finite, and a delayed authorization can cost the offer entirely.

## The bigger signal

The processing freeze does not sit in isolation. USCIS Director Joseph Edlow has said openly that he wants a system that can "remove the ability for employment authorizations for F-1 students beyond the time that they are in school." Officials have also floated that OPT is "undermining" American workers — a framing that has migrated from national-security language toward labor-market politics. A proposed rule to curtail or end OPT outright is widely expected.

For an Indian student weighing an American degree right now, the message is uncomfortable. A court win that produces no movement is, functionally, not a win at all. The safest assumption is that the work-permit pipeline remains unreliable, that timelines are no longer something a university DSO can promise, and that the program itself is a political target rather than a settled benefit.

Graduates already in the queue have little to do but wait, document everything, and keep employers informed. Those still choosing where to study would be wise to read the delay not as a glitch but as the new baseline.

Sources: *Inside Higher Ed*; ICEF Monitor; USCIS statements."""

article2_body = """The number that should worry American universities this summer is not a visa wait time or a rejection rate. It is the share of Indian students who have simply given up. Education consultants in Hyderabad — one of the densest pipelines of US-bound students anywhere in the world — say applications are down 70 to 80 percent this cycle.

That is not a slowdown. It is a market walking away.

## What the consultants are seeing

The collapse traces back to two things happening at once: a prolonged freeze on visa appointment slots, and a sharp rise in rejection rates for the interviews that do happen. American authorities promised to release appointment slots in phases. Months on, students say the promised slots have not materialized in any reliable way, and even those who managed to book have not received confirmations.

"By this time usually, most students are done with their visa interviews and are preparing to fly," said Sanjeev Rai of Hyderabad Overseas Consultant. "This year, we're still refreshing the portal every day hoping for a slot to open. It's the worst in years."

Arvind Manduva of the I20 Fever consultancy put a number on it: "If slots aren't released in the next few days, thousands of dreams will be shattered. We are seeing about an 80% drop. We're getting panic calls every day from students and their parents."

The students themselves are doing the math and cutting their losses. "I really could not wait. I might just lose out on a year," one applicant said, explaining why he withdrew his application altogether. A lost year, for a 22-year-old, is a long time to gamble on a portal that will not load a slot.

## Why this lands hardest on Indian families

For Indian middle-class families, an American degree has long been treated as one of the highest-return investments available — a path that justifies liquidating savings, taking education loans against property, and sending an only child halfway across the world. That calculus assumes the visa is a formality at the end of an admissions process, not the chokepoint that decides everything.

This year inverts the assumption. Admission letters mean nothing without an interview slot, and interview slots have become the scarcest commodity in the system. Consultants note that students from earlier cycles would, by mid-June, already be through their interviews and packing. The contrast is what is feeding the panic.

The downstream effects ripple straight into the diaspora. Fewer arriving students means fewer future H-1B candidates, fewer green-card aspirants, and a thinner pipeline into the Indian-American professional class that the community has spent two generations building. The families already here — uncles, cousins, parents who were going to host the new arrivals — are watching the on-ramp narrow.

## A redirected generation

The students are not abandoning the idea of studying abroad. They are abandoning America specifically. Consultants report applicants pivoting to the U.K., Canada, and increasingly continental Europe, where this cycle has emerged as a credible alternative destination. Each of those countries has its own tightening rules, but none has produced the appointment vacuum that India is experiencing for US visas right now.

The official data already pointed this way before the consultants did. New US student visas issued to Indian nationals fell 63 percent last summer compared with 2024 — by far the steepest drop of any major sending country. The 70-to-80 percent figure being quoted now suggests the trend has not stabilized; it has accelerated.

For an Indian student admitted to a US program this fall, the practical advice is unsentimental: secure backup admissions in other countries, do not assume a slot will appear, and treat the visa interview as the real bottleneck rather than the acceptance letter. For American universities that have leaned on Indian enrollment to balance their budgets, the warning is blunter still. The customers are not complaining anymore. They are leaving.

Sources: *The Indian Eye*; *Inside Higher Ed*; This Week in Study Abroad."""

article3_body = """In late May, USCIS issued a policy memo that, read literally, threatened to rewrite four decades of practice for hundreds of thousands of immigrants — and then spent the following weeks insisting it did not mean what it appeared to say. For Indian families on H-1B and H-4 visas, the episode is a case study in how policy-by-memo creates damage even when it is never fully enforced.

## What the memo said

Policy Memorandum PM-602-0199, dated May 22, recast "adjustment of status" — the process by which someone already in the U.S. converts a temporary visa into a green card without leaving — as "extraordinary discretionary relief." The default, the memo signaled, would shift toward consular processing: leave the country, return to a U.S. embassy in your home nation, and file from there.

For most categories of applicant, that would be a seismic change. People have adjusted status on American soil since Congress created the process in 1952, a section of law amended more than twenty times since. As the American Immigration Council pointed out, "At no time has Congress written this 'extraordinary discretionary relief' standard into the law that USCIS is now claiming Congress intended all along."

DHS framed it as a return to statutory design. "An alien who is in the U.S. temporarily and wants a Green Card must return to their home country to apply," the department said. A USCIS spokesman argued the shift would reduce the incentive for denied applicants to "slip into the shadows."

## The walk-back

The backlash was immediate, and USCIS soon clarified that most applicants will not, in fact, need to leave the country. The George W. Bush Presidential Center's June immigration update noted dryly that the agency "later clarified that most applicants won't need to leave the United States," and that adjustment of status "may continue as it always has for many applicants."

So the literal threat receded. But the Bush Center's analysts made the sharper point: a policy memo like this is corrosive even if it is never implemented. "Immigration policy through executive action does not provide a stable environment for anyone who deals with our immigration system — including businesses, churches, schools, families, and, yes, immigrants themselves."

## Why Indian families felt this acutely

For most Indian green-card aspirants, the immediate stakes are muted for a brutal reason: their priority dates are not current. With EB-2 and EB-3 India backlogs stretching to wait times routinely estimated at 50 to 100 years, the question of how to file is academic when there is nothing to file against.

But the memo cut deepest precisely for the Indians whose dates do move — those filing under EB-1 or EB-2 NIW, where movement is faster, and those rare cases where a priority date becomes current. For them, a consular-processing requirement is not theoretical. It means leaving the U.S. with no guaranteed return date, exposed to consular backlogs that have already pushed stamping appointments in India to multi-month waits.

The H-4 dimension is what makes it personal. Spouses and children who have lived in the U.S. for years — kids in American schools, partners with their own careers and EAD authorizations — would face the possibility of family separation during a consular process that can run months or longer. A memo that "most" people can ignore still hangs over every family that cannot be sure it falls inside the "most."

Zoho founder Sridhar Vembu used the moment to renew his appeal for Indian professionals to return home: "Please come home. Even if you feel it is hardship and sacrifice, self-respect should dictate your course." It is a sentiment that lands differently depending on whether you have a backlog measured in decades or a flight to catch.

The lesson for Indian families is procedural but vital: nothing has formally changed for the vast majority of adjustment-of-status filers, but the ground is no longer stable. Anyone with a current or near-current priority date should get individualized legal advice before traveling, and treat agency memos as weather, not climate — capable of shifting overnight.

Sources: George W. Bush Presidential Center; American Immigration Council; *IBTimes*; VisaVerge."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Court Told USCIS to Restart Frozen Work Permits. Indian Grads Say Nothing Has Moved",
        "subheadline": "OPT and green-card applications were ordered back into processing weeks ago. No approvals, no refunds, and employers' patience is running out.",
        "slug": make_slug("opt-green-card-processing-resume-court-order-india-limbo-no-refunds"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian students are the largest group on OPT, and the post-study work window is the main reason many choose the US over Canada or the UK — a court win that produces no actual approvals leaves their classroom-to-green-card pathway frozen.",
        "tags": ["opt", "stem-opt", "uscis", "f1", "international-students", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Inside Higher Ed — Intl. Students Still in Limbo, Even With USCIS Pause Over", "url": "https://www.insidehighered.com/news/global/international-students-us/2026/06/16/international-students-still-limbo-even-uscis"},
            {"name": "ICEF Monitor — OPT abuse allegations", "url": "https://monitor.icef.com/2026/05/us-immigration-officials-allege-opt-is-being-widely-abused/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6147148/pexels-photo-6147148.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "International students on a university campus; OPT work authorization is the bridge between graduation and employment for most Indian graduates.",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Students Are Quitting on America: Consultants Report an 80% Drop This Cycle",
        "subheadline": "A visa-slot freeze and surging rejection rates have Hyderabad's education consultants watching the US-bound pipeline collapse — and students are pivoting to the UK, Canada, and Europe.",
        "slug": make_slug("indian-students-70-80-percent-drop-us-universities-visa-slot-freeze"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Fewer Indian students arriving means a thinner pipeline of future H-1B candidates and green-card aspirants — the on-ramp into the Indian-American professional class is narrowing in real time.",
        "tags": ["f1", "student-visa", "international-students", "visa-appointments", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye — Visa crisis prompts 70-80% drop in Indian students opting for US Universities", "url": "https://www.theindianeye.com/visa-crisis-prompts-a-70-80-drop-in-indian-students-opting-for-us-universities/"},
            {"name": "Inside Higher Ed — New Student Visas Dropped 35.6% Last Summer", "url": "https://www.insidehighered.com/news/global/international-students-us/2026/new-student-visas-dropped"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/19579986/pexels-photo-19579986.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Graduating students at a university commencement; Indian enrollment in US programs is reported down sharply this admissions cycle.",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "USCIS Floated Sending Green-Card Filers Home to Apply, Then Walked It Back. The Damage Was Already Done",
        "subheadline": "A May memo recast adjustment of status as 'extraordinary relief.' The agency says most won't have to leave — but for Indians with current priority dates, the threat was real.",
        "slug": make_slug("uscis-adjustment-status-memo-consular-processing-walkback-h4-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians filing under EB-1 or EB-2 NIW, where dates move faster, and H-4 families with kids in US schools face the real prospect of separation during consular processing — even though USCIS says 'most' applicants are unaffected.",
        "tags": ["green-card", "adjustment-of-status", "h4", "eb1", "niw", "uscis", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "George W. Bush Presidential Center — Monthly immigration update: June 2026", "url": "https://www.bushcenter.org/catalyst/immigration/monthly-immigration-update-june-2026"},
            {"name": "VisaVerge — USCIS Limits Adjustment of Status: New 2026 Policy Impact", "url": "https://www.visaverge.com/uscis/uscis-limits-adjustment-of-status-new-2026-policy-impact/"},
            {"name": "IBTimes — New USCIS Rule: Who Has to Leave US for a Green Card?", "url": "https://www.ibtimes.sg/new-uscis-rule-who-has-leave-us-green-card"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8061944/pexels-photo-8061944.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport and visa paperwork; a May USCIS memo briefly threatened to push green-card filers toward consular processing abroad.",
        "image_attribution": "Pexels",
        "body": article3_body
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
