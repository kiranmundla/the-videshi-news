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

art1_body = """The phone calls to immigration lawyers started before the policy was even formally posted. On Friday, U.S. Citizenship and Immigration Services confirmed it is rolling back a 2023 rule that had quietly become a lifeline for one specific, anxious group: the now-adult children of Indian green-card applicants who have spent their entire conscious lives in America and are running out of time to stay.

The agency is restoring the way it calculates a child's age under the Child Status Protection Act (CSPA), a piece of arcane immigration arithmetic that decides whether a 21-year-old gets to keep the future their parents built — or gets shown the door of the only country they remember.

## What Actually Changed

The CSPA exists because the green-card backlog is so long that children grow up and "age out" of their parents' applications before a visa ever becomes available. To stop that, the law lets applicants "freeze" a child's age at a certain point in the process. The whole fight is over *which* point.

Until 2023, USCIS froze a child's age based on the visa bulletin's **Final Action Date** — the moment a green card actually becomes available. The Biden administration changed that to the earlier **Dates for Filing** chart, which lets applicants submit paperwork sooner. For families stuck in the India employment-based queue, that shift mattered enormously: it pulled the freeze point years earlier, locking in more children under the magic age of 21 before the clock ran out.

Friday's announcement reverses that. USCIS says it is "restoring previous practices," arguing the 2023 change created "inconsistent treatment" between applicants filing inside versus outside the United States. In plain terms: the freeze point moves back to the later date, and a wave of young people who thought they were protected may no longer be.

## Why Indians Are the Story

This is not a policy that lands evenly across nationalities. It lands almost entirely on India.

There are an estimated 200,000-plus "documented dreamers" — children who grew up legally in the U.S. as dependents on a parent's work visa — and the overwhelming majority are Indian or Chinese. The reason is the per-country cap: no nation can claim more than 7% of the 140,000 employment-based green cards issued each year. Indians make up roughly half of new applicants entering the employment queue but receive a sliver of the supply. Analysts at the Cato Institute have estimated the wait for some Indian applicants stretches past eight decades.

Do the math on a human timescale and the cruelty becomes obvious. A child who arrived from Hyderabad at age four on an H-4 dependent visa, who went through American elementary school, high school, and college, hits 21 long before the family's green card number comes up. The CSPA was the one mechanism keeping that child in line. Narrow the freeze, and they fall out — forced to scramble for an F-1 student visa, find their own employer sponsor, or leave.

## What Families Can Do Now

Immigration attorneys are urging affected families not to panic but to move fast and get specific advice. The practical levers right now:

- **File while you can.** Families whose children are close to 21 should review, with counsel, whether filing adjustment-of-status applications quickly can still lock in a more favorable age calculation before the reversal fully bites.
- **Map a backup status.** For children approaching the cliff, an F-1 student visa remains the most common bridge — but with student-visa scrutiny also tightening, early planning is essential.
- **Watch the courts and Congress.** The current law is ambiguous, and advocates argue only Congressional action can truly fix the age-out trap.

Dip Patel, founder of the advocacy group Improve the Dream, put it bluntly: "We need bipartisan legislation to properly address the issue." Bills like the America's CHILDREN Act have circulated for years with bipartisan sponsors and no finish line.

## The Bigger Picture

For the Indian diaspora, this reversal is a reminder that the backlog is not an abstract number on a visa bulletin. It is a countdown clock running underneath real families — and a single policy memo can reset it in the wrong direction overnight. The children most affected did everything right: they grew up American in every way the law does not recognize. Whether they get to stay now depends on arithmetic written in Washington, and on a Congress that has spent two decades not finishing the job."""

art2_body = """If your employer told you back in April that your H-1B was "selected," there is a date you should have circled in red: **June 30**. That is the last day for petitioners to file a complete FY 2027 H-1B cap petition — and this year, missing it or fumbling it carries higher stakes than it has in a long time.

For tens of thousands of Indian professionals — students finishing OPT, workers hoping to move off a dependent status, candidates abroad waiting to start — this five-day stretch is the difference between an October 1 start date and another year in limbo.

## Selected Is Not the Same as Safe

A lottery selection is permission to *apply*, not an approval. Once USCIS notifies a registrant, the sponsoring employer has a hard filing window — April 1 through June 30 — to submit a fully documented petition. Any petition not received by the deadline is voided, and the H-1B number gets reallocated, potentially to a waitlisted registrant in a future round.

This year that window is unusually unforgiving for three reasons, all of which hit Indian applicants disproportionately because Indians account for an estimated 71% of approved H-1B petitions.

## The New Rules Behind This Filing Season

**A wage-weighted lottery, for the first time.** FY 2027 is the debut of the system that replaced the old purely random draw. Each registration now gets entries based on the Department of Labor wage level of the offered job: Level IV positions get four entries, Level I gets one. The result, per Fragomen, was a selection rate above 50% on average this year — up sharply from 35% in 2025 — partly because demand collapsed and staffing firms registered far fewer low-wage candidates.

That higher selection rate is genuinely good news for Indian master's-degree graduates. But there is a catch buried in the filing requirements.

**You must now prove the wage level you registered at.** The redesigned Form I-129 — only the February 27, 2026 edition is accepted — requires petitioners to include "evidence of the basis of the wage level selected" during registration. USCIS is actively checking that the registration wage level, the Labor Condition Application wage, and the actual offered salary all line up. A mismatch can trigger a Request for Evidence or an outright denial. In other words, the wage level that helped you win the lottery is now a claim you have to defend.

**The petition itself must match the registration.** The new I-129 demands more detail about the offered position and requires consistency with the Standard Occupational Classification (SOC) code chosen at registration. Selection notices must be attached. Employers cannot substitute beneficiaries — the notice is valid only for the named person.

## What This Means If You Are Indian and Waiting

The practical takeaways for diaspora applicants in the final stretch:

- **Confirm your employer has filed — do not assume.** With heightened scrutiny on every petition, lawyers are warning employers not to file in the last 48 hours. If you have not had confirmation, ask now.
- **Expect more RFEs, especially on wage.** The wage-level evidence requirement is new, and the cases most exposed are those selected at higher wage levels where the offered salary sits near the boundary.
- **A win still is not an approval.** Selection guaranteed a filing slot, not a visa. The specialty-occupation standard, the employer-employee relationship, and every other requirement still apply.

## The Quiet Shift Underneath

Step back and the FY 2027 cycle tells a larger story about the program Indians rely on most. Demand fell. The $100,000 supplemental fee on certain consular petitions scared off volume filers. The lottery now rewards higher pay over sheer numbers. For an Indian software engineer with a U.S. master's degree and a Level III or IV salary, the odds have arguably never been better. For an entry-level candidate at Level I, the door has narrowed considerably.

Either way, none of it matters if the petition does not land by Tuesday. After years in which the lottery was the hard part, this year the paperwork — and a single calendar date — may decide who gets to stay."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Age-Out Clock Just Got Reset for 200,000 'Documented Dreamers' — Most of Them Indian",
        "subheadline": "USCIS is rolling back a 2023 rule that shielded the grown children of green-card applicants from losing status at 21. For families stuck in the India backlog, the safety net just got smaller.",
        "slug": make_slug("documented-dreamers-cspa-age-out-reversal-uscis-h4-children-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The overwhelming majority of the 200,000+ documented dreamers are children of Indian H-1B and H-4 families trapped in a decades-long green-card backlog, and USCIS's reversal of the CSPA age-calculation rule directly raises the risk that they age out of legal status at 21.",
        "tags": ["cspa", "documented-dreamers", "h4", "green-card-backlog", "uscis", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law — DHS Drops Age-Out Protections for Kids of Green Card Seekers", "url": "https://news.bloomberglaw.com/daily-labor-report/dhs-drops-age-out-protections-for-kids-of-green-card-seekers"},
            {"name": "Fragomen — H-4 Kids of Indian H-1B Workers Face US Visa Expiry at 21", "url": "https://www.fragomen.com/insights/h-4-kids-of-indian-h-1b-workers-face-us-visa-expiry-at-21-what-next.html"},
            {"name": "Bipartisan Policy Center — Documented Dreamers: An Explainer", "url": "https://bipartisanpolicy.org/explainer/documented-dreamers/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/36622165/pexels-photo-36622165.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "International graduates in caps and gowns at a U.S. university commencement",
        "image_attribution": "Pexels",
        "published_at": now,
        "body": art1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Five Days Left: The June 30 H-1B Deadline That Decides Who Starts Work on October 1",
        "subheadline": "FY 2027's first wage-weighted lottery handed Indian applicants better odds than they've had in years. A new Form I-129 and a hard filing cutoff could still take it all away.",
        "slug": make_slug("h1b-fy2027-june-30-filing-deadline-form-i129-wage-level-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians make up an estimated 71% of approved H-1B petitions, so the June 30 FY 2027 filing deadline and the new wage-level evidence requirements determine whether tens of thousands of Indian professionals secure an October 1 start or lose their selection slot.",
        "tags": ["h1b", "fy2027", "uscis", "form-i129", "wage-level", "h1b-lottery"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen — H-1B Cap Lottery Results FY 2027: What Employers Should Do Now", "url": "https://www.fragomen.com/insights/h-1b-cap-lottery-results-fy-2027-what-employers-should-do-now.html"},
            {"name": "Mondaq — H-1B FY2027 Cap Reached: USCIS Announces Filing Season And Key Requirements", "url": "https://www.mondaq.com/unitedstates/work-visas/h-1b-fy2027-cap-reached-uscis-announces-filing-season-and-key-requirements"},
            {"name": "Reuters — The $100,000 question: Navigating the new H-1B lottery system", "url": "https://www.reuters.com/legal/legalindustry/100000-question-navigating-new-h-1b-lottery-system-2026-03-24/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An open passport displaying entry and visa stamps",
        "image_attribution": "Pexels",
        "published_at": now,
        "body": art2_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  word count: {wc} | {art['slug']}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
