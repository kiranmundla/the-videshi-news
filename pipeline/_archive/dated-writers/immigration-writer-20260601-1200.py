#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-01 12:00 UTC run"""

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
        "headline": "Your Client Site Just Became Off-Limits — USCIS Quietly Bans STEM OPT Workers From Consulting Placements",
        "subheadline": "A website update with no formal rulemaking has gutted the staffing model that Indian IT graduates depend on — and it's part of something bigger.",
        "slug": make_slug("stem-opt-offsite-ban-indian-it-consulting-staffing"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals represent 65% of all H&L visa applicants and roughly 20% of all student visa applicants in the US. The IT consulting and staffing model — where employers place STEM OPT graduates at client sites — is the primary career entry point for thousands of Indian STEM graduates each year. This ban disrupts that pipeline at the exact moment the H-1B lottery has become nearly impossible to win.",
        "tags": ["stem-opt", "f1-visa", "uscis", "it-consulting", "indian-students", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Littler Mendelson", "url": "https://www.littler.com/news-analysis/asap/uscis-issues-changes-site-placement-stem-opt-f-1-visa-holders"},
            {"name": "Sharma Law Offices", "url": "https://elawimmigration.com/"},
            {"name": "ICEF Monitor", "url": "https://monitor.icef.com/"},
            {"name": "Duke University Career Hub", "url": "https://careerhub.students.duke.edu/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/36985997/pexels-photo-36985997.jpeg",
        "body": """For years, the arrangement worked like clockwork. An Indian student graduates from a US university with a STEM degree. A staffing firm or IT consulting company hires them under STEM OPT — the 24-month work authorization extension available to F-1 visa holders. The company places them at a client site: a bank in Charlotte, a tech firm in Seattle, a hospital system in Dallas. The student gains experience. The employer bills the client. Everyone moves on.

USCIS just killed that model — and did it with a website edit.

## The Quiet Rule That Changed Everything

Without issuing a formal rule, publishing a Federal Register notice, or opening a public comment period, USCIS updated its STEM OPT eligibility page to include an explicit prohibition: the training experience "may not take place at the place of business or worksite of the employer's clients or customers."

The language is unambiguous. Staffing agencies and consulting firms "may not assign or contract out students to work for one of their customers or clients, and assign, or otherwise delegate, their training responsibilities to the customer or client." The only permissible arrangement is placement at the employer's own facility — its own office, its own internal IT department, its own lab.

For Indian IT consulting firms that have built their business model around placing junior engineers at client sites, the prohibition is existential. For the thousands of Indian STEM graduates who depend on those placements as their entry point into the American workforce, it is devastating.

## Why This Matters More Than It Sounds

The STEM OPT extension is not a minor program. Over 170,000 students were authorized to work under OPT and STEM OPT as of the most recent data — a 600% increase from 2007. For Indian graduates, the math was simple: a 12-month OPT period followed by a 24-month STEM extension provided a three-year runway to find an employer willing to sponsor an H-1B petition.

But the H-1B lottery has become a wall. With the $100,000 fee proclamation discouraging new filings and a wage-weighted selection system tilted toward senior workers, fresh graduates face near-impossible odds. STEM OPT was the bridge. Now USCIS is removing the planks.

The off-site ban hits Indian workers disproportionately for a structural reason: India's IT services industry — Infosys, TCS, Wipro, and hundreds of smaller firms — operates on a client-placement model. These companies employ a significant share of Indian STEM graduates on OPT and STEM OPT. Under the new guidance, that entire pipeline is non-compliant.

## The Justification — and the Gaps

USCIS frames the prohibition around enforcement logistics. Because ICE has the authority to conduct site visits to verify that employers are meeting training plan requirements, the student must physically work at a location ICE can inspect — which means the employer's own premises. If the student is at a client site, ICE has no authority to visit that location.

The reasoning has a surface logic, but immigration attorneys are pointing out a glaring problem: remote work. Millions of American workers — including those on H-1B visas — work from home. If a STEM OPT worker's employer is in New Jersey and the worker is remote from Texas, which site does ICE visit? The guidance doesn't say.

What makes the change particularly alarming is the process — or lack of one. USCIS updated its website. No proposed rule. No notice-and-comment period. No transition guidance for the thousands of STEM OPT workers currently placed at client sites with valid Form I-983 training plans. As Littler Mendelson noted in its analysis, "current holders of this employment authorization extension and their employers are unsure whether a previously approved Form I-983 is still valid if the employee is currently placed off-site."

## Part of a Larger Pattern

The off-site ban doesn't exist in isolation. USCIS Director Joseph Edlow has publicly stated he wants to "remove the ability for employment authorizations for F-1 students beyond the time that they are in school." The Department of Homeland Security has launched a formal review of the entire OPT program. A January 2026 executive action paused OPT processing for nationals of 39 countries. And a separate proposal to replace "duration of status" with fixed admission periods could make STEM OPT transitions procedurally impossible.

Taken together, the pattern is clear: the administration is systematically narrowing every pathway that allows international students to work in the United States after graduation. The off-site ban is one brick in a wall that's being built fast.

## What Indian Graduates Should Do Now

Immigration attorneys are advising STEM OPT workers currently placed at client sites to consult legal counsel immediately. Those whose Form I-983 training plans list a client location as the worksite may need to transition to an on-site role at their employer's own office — if one exists. Students considering STEM OPT applications should verify that the prospective employer can provide the training experience at its own location, not at a client site.

For the broader Indian student community watching from campuses across the country, the message is grimmer: the path from graduation to employment to H-1B to green card is narrowing at every junction. The STEM OPT bridge is still standing — but USCIS is testing how much weight it can bear."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "'Could You Seize 10% of a Company's Equity?' — A Federal Judge Just Stress-Tested the $100,000 H-1B Fee",
        "subheadline": "In a Boston courtroom, the government's own lawyer conceded that Trump's immigration powers might have no limit. Only 85 employers have actually paid the fee.",
        "slug": make_slug("h1b-100k-fee-boston-judge-sorokin-authority-limits"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals hold the majority of H-1B visas. The $100,000 fee has already collapsed new H-1B filings — only 85 payments made as of February. Indian tech workers and the companies that employ them are the fee's primary casualties, and the Boston courtroom will determine whether this fee survives legal scrutiny.",
        "tags": ["h1b", "100k-fee", "court-ruling", "uscis", "immigration", "indian-workers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/government/us-judge-questions-scope-trumps-power-impose-100000-h-1b-visa-fee-2026-05-29/"},
            {"name": "State of California et al v. Mullin, D. Mass., No. 25-cv-13829", "url": "https://www.reuters.com/legal/government/us-judge-questions-scope-trumps-power-impose-100000-h-1b-visa-fee-2026-05-29/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/34817076/pexels-photo-34817076.jpeg",
        "body": """The lawyer for the United States government stood in a Boston courtroom on Friday and said, essentially, that the President of the United States might have the power to force a company to hand over 10 percent of its equity as a condition of hiring a foreign worker.

He did not say this to make a point. He said it because a federal judge asked him, and he could not find the limiting principle.

## The Question That Stopped the Room

U.S. District Judge Leo Sorokin was hearing arguments in *State of California et al v. Mullin*, a lawsuit brought by 20 Democratic state attorneys general challenging the $100,000 fee that President Trump imposed on new H-1B visa applications through a September 2025 proclamation. Before the proclamation, employers typically paid between $2,000 and $5,000 in filing fees. The increase was not incremental — it was a 2,000 percent spike designed to make the program unusable.

Sorokin pressed Tiberius Davis, the Department of Justice lawyer defending the fee, on a basic constitutional question: if the president has the authority to impose a $100,000 fee on H-1B applications, is there any limit to that authority?

Could the president impose a $100,000 fee on Americans wanting to marry non-citizens in order for those spouses to enter the country? Could the government force a company that wants to bring in a foreign worker to forfeit 10 percent of its equity?

Davis responded that Trump "possibly could" take those hypothetical actions. "It's a very sweeping power," he told the court.

## Eighty-Five Payments

The number that defines the $100,000 fee's impact is not a dollar figure — it is a headcount. As of February 15, 2026, USCIS had received exactly 85 payments of the new fee. Eighty-five. Out of a program that processes roughly 85,000 petitions in a typical year.

"The effect is to incentivize companies to train up and hire American workers," Davis told Sorokin, framing the collapse in applications as the policy working as intended.

The math behind that collapse is straightforward. A mid-size tech company sponsoring five H-1B workers now faces $500,000 in fees alone — before legal costs, before premium processing, before the annual lottery gamble. For Indian IT services firms that once filed hundreds of petitions, the fee is not a deterrent. It is a shutdown.

The 85 companies that did pay are overwhelmingly large multinationals with enough budget to absorb the cost for irreplaceable talent. Everyone else has stopped filing. The H-1B program, which offers 65,000 visas annually plus 20,000 for workers with advanced degrees, has effectively been priced out of reach for most employers.

## The Tariff Precedent

James Richardson, representing California, made an argument that may prove more consequential than the fee itself. He cited the U.S. Supreme Court's February 2026 ruling striking down Trump's sweeping tariffs — which had been imposed under a law meant for national emergencies — arguing it established a principle that applies directly to the H-1B fee.

"Congress does not delegate a tax authority in ambiguous language," Richardson told Sorokin.

The argument reframes the $100,000 fee not as a legitimate exercise of immigration enforcement power but as an unconstitutional tax imposed without congressional authorization. The president used Section 212(f) of the Immigration and Nationality Act — which allows restricting entry of aliens deemed detrimental to U.S. interests — as the legal basis. Richardson contends that section authorizes entry restrictions, not revenue extraction.

The distinction matters. If the fee is a restriction on entry, the president arguably has broad authority under existing law. If it is a tax, it requires an act of Congress. The Supreme Court's tariff ruling — which found that sweeping presidential fee-imposition under emergency powers constituted an unconstitutional tax — gives the states their strongest precedent.

Davis urged Sorokin to follow the reasoning of U.S. District Judge Beryl Howell in Washington, D.C., who ruled in a related case brought by the U.S. Chamber of Commerce that Trump's immigration powers were broad enough to sustain the fee. That ruling created a circuit split that many observers expect will eventually reach the Supreme Court.

## What This Means for Indian Workers

Indian nationals account for the overwhelming majority of H-1B visa holders. According to USCIS data, India-born workers received approximately 72 percent of all H-1B approvals in recent fiscal years. The $100,000 fee was never sector-neutral — it was aimed squarely at the technology and IT services industries where Indian workers concentrate.

The practical effects are already visible. Companies that once sponsored multiple H-1B workers are now sponsoring one or none. Indian IT consulting firms have reported shifting work to offices in India, Canada, and Mexico rather than paying the fee. Graduate students finishing STEM programs at American universities are reconsidering whether to enter the H-1B lottery at all when the employer's cost of entry is six figures before the first day of work.

The Boston hearing did not produce a ruling. Judge Sorokin took the arguments under advisement. But the exchange revealed something important about the government's legal position: it has no limiting principle. The same authority that justifies a $100,000 fee justifies a $1,000,000 fee. The same logic that permits a fee permits equity forfeiture.

Whether federal courts accept that position — or follow the Supreme Court's tariff logic and call it what critics say it is, an unauthorized tax — will determine the future of skilled immigration to America. For the hundreds of thousands of Indian professionals whose careers depend on the answer, the waiting has only begun."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
