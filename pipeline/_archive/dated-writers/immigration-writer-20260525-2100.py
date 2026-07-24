#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-25 21:00 PDT run"""
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
        "headline": "A Florida Republican Wants to Kill the H-1B Entirely — Inside the EXILE Act",
        "subheadline": "Rep. Greg Steube has introduced legislation to abolish the H-1B visa program outright, calling it a 'corrupt system' that displaces American workers. For the 71% of H-1B holders who are Indian nationals, the bill is an existential shot across the bow.",
        "slug": make_slug("exile-act-greg-steube-abolish-h1b-indian-workers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold roughly 71% of all approved H-1B visas. If the EXILE Act were to pass, it would not merely restrict Indian tech workers' path to America — it would eliminate it entirely. For hundreds of thousands of Indian engineers, doctors, and researchers currently on H-1B visas, and for the pipeline of students planning their careers around the program, this bill represents the most radical legislative threat to Indian professional migration in decades.",
        "tags": ["h1b", "exile-act", "greg-steube", "immigration", "congress"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fox News", "url": "https://www.foxnews.com/politics/greg-steube-exile-act-end-h1b-visa-program"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/world/rubio-says-h-1b-visa-changes-not-aimed-at-indian-a-38-5-per-cent-drop-in-registration-green-card-rules-say-differently-11779683463679.html"},
            {"name": "USCIS FY2027 H-1B Data", "url": "https://www.uscis.gov/"},
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/57/Greg_Steube_117th_Congress.jpeg",
        "body": """The legislation is called the EXILE Act — Ending Exploitative Imported Labor Exemptions Act — and it does exactly what the acronym suggests. Introduced by Rep. Greg Steube, a Florida Republican, the bill proposes something no serious piece of legislation has attempted in the H-1B program's 35-year history: total abolition.

"American workers have been ripped off by the corrupt H-1B visa program for far too long," Steube wrote on X. "Corporations have repeatedly abused this system to help their bottom line by importing cheaper foreign labor which has suppressed wages and left millions of Americans locked out of good-paying jobs."

The bill arrives at a moment when the H-1B program is already under siege from multiple directions — a $100,000 per-petition fee imposed by presidential proclamation last September, a 38.5% collapse in FY2027 registrations, and a Department of Labor proposal to raise minimum H-1B wages by up to 33%. But Steube's approach dispenses with reform entirely. He wants the program dead.

## What the EXILE Act Would Do

The bill's mechanism is straightforward: it would repeal Section 101(a)(15)(H)(i)(b) of the Immigration and Nationality Act, the provision that created the H-1B nonimmigrant classification. No phase-out. No transition period in the current draft. The program would simply cease to exist.

That provision currently authorizes up to 85,000 new H-1B visas per year — 65,000 through the general lottery and 20,000 reserved for holders of advanced degrees from U.S. universities. In FY2025, USCIS approved 406,348 H-1B petitions total (including renewals and transfers), of which 283,772 — roughly 70% — went to Indian nationals.

Steube framed the bill as a defense of the American workforce: "Our workers and young people continue to be displaced and disenfranchised by the H-1B visa program that awards corporations and foreign competitors at the expense of our workforce. We cannot preserve the American dream for our children while forfeiting their share to non-citizens."

## The Political Context: Three Bills, Three Directions

The EXILE Act exists in a legislative environment that has become almost comically fractured on the question of what to do with H-1B visas.

In one corner, Steube wants to abolish the program. In another, the One Big Beautiful Bill Act — which passed the House by a single vote (215-214) and is now heading to the Senate — imposes a $100,000 fee on each H-1B petition while keeping the program alive. And separately, a bipartisan House bill from two Republicans and two Democrats proposes waiving that very same $100,000 fee for doctors and nurses, arguing it will cripple healthcare staffing.

The Senate, meanwhile, recently advanced its own immigration bill that would actually expand the number of H-1B visas available — a direct contradiction of the abolition Steube is proposing.

These four pieces of legislation cannot all become law. They represent fundamentally incompatible visions of America's relationship with foreign talent, and the fact that all four are actively moving through Congress simultaneously tells you everything about the state of the immigration debate in Washington.

## Why This Matters More to Indians Than Anyone Else

The arithmetic is unforgiving. Indians account for 71% of approved H-1B petitions. China is a distant second at roughly 12%. No other country comes close.

India's six largest IT services firms — TCS, Cognizant, Infosys, HCL Technologies, Wipro, and Tech Mahindra — collectively received 11,041 H-1B visas as of March 2026, already a 40% decline from the previous year. Under the EXILE Act, that number would go to zero.

But the impact extends far beyond IT outsourcing companies, which have long been the program's most visible (and most criticized) users. The H-1B is the primary legal pathway for Indian engineers at Google, Indian doctors in rural hospitals, Indian researchers at universities, and Indian data scientists at financial firms. There is no alternative visa category that can absorb this volume of skilled workers. The O-1 visa, designed for individuals of "extraordinary ability," approves roughly 15,000 petitions per year total, across all nationalities and fields. It is not a substitute.

## The Bill's Chances — and Why They Still Matter

To be blunt: the EXILE Act is unlikely to become law. It has no cosponsors as of its introduction. The tech industry's lobbying apparatus — which spent $78 million on immigration-related lobbying in 2025 alone — would mobilize against it. And the Trump administration, despite its hostility toward immigration broadly, has shown no appetite for killing the H-1B program. Trump himself has praised the visa category on multiple occasions, and his $100,000 fee approach explicitly assumes the program continues to exist.

But the bill matters for a reason beyond its legislative prospects. It moves the Overton window. Two years ago, a bill to abolish H-1B would have been dismissed as fringe nativism. Today, it arrives in a context where USCIS has already declared green card applications an "extraordinary act of grace," where H-1B registrations have already fallen by 38.5%, and where the Department of Labor is proposing to price out a significant share of entry-level H-1B positions.

Steube's bill may not pass. But it tells you where the floor of the debate has moved. And for the 283,772 Indians who received H-1B approvals last year, the floor is starting to feel uncomfortably close to a trapdoor.

## What Indian H-1B Holders Should Watch

The EXILE Act will likely be referred to the House Judiciary Committee, where it will join a growing stack of immigration bills awaiting action. Its fate depends on whether it attracts cosponsors and, more importantly, whether committee leadership decides to schedule it for markup.

For now, the more immediate threats remain the $100,000 petition fee (already in effect via presidential proclamation), the DOL wage hike (comment period closing May 26), and the USCIS policy memo restricting adjustment of status. The EXILE Act is, at this stage, a political statement rather than an imminent policy change.

But political statements have a way of becoming policy proposals, and policy proposals have a way of becoming law — especially when the wind is blowing in one direction. Indian professionals in the United States would be wise to track this one."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "1.2 Million Indians, Four Consulates, and a System That Cannot Handle What Washington Just Demanded",
        "subheadline": "The USCIS memo forcing green card applicants to process from their home country sounds like a procedural tweak. For Indian nationals facing decade-long backlogs and a consular infrastructure built for a fraction of the demand, it is a logistical catastrophe.",
        "slug": make_slug("consular-processing-india-green-card-logistics-crisis"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India has just four U.S. consular posts processing immigrant visas — Mumbai, New Delhi, Chennai, and Hyderabad — for the single largest source country of employment-based green card applicants. Indians already face EB-2 backlogs stretching past 2012 and EB-3 backlogs past 2010. The consular processing mandate doesn't just change where Indians apply — it forces them to uproot families, abandon careers, and wait in a country they left years ago for an appointment slot that may not exist.",
        "tags": ["green-card", "consular-processing", "uscis", "backlog", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS Policy Memo (May 22, 2026)", "url": "https://www.uscis.gov/"},
            {"name": "Tupaki English", "url": "https://english.tupaki.com/latest-news/us-green-card-policy-change-claims-indian-immigrants-concern-1488573"},
            {"name": "Dainik Bhaskar English", "url": "https://www.bhaskarenglish.in/international/news/us-h1b-green-card-rules-tightened-indian-professionals-concerns-138007222.html"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/world/rubio-says-h-1b-visa-changes-not-aimed-at-indian-a-38-5-per-cent-drop-in-registration-green-card-rules-say-differently-11779683463679.html"},
            {"name": "WaitVisa.com", "url": "https://waitvisa.com/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33500646/pexels-photo-33500646.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """When USCIS spokesman Zach Kahler announced on May 22 that foreign nationals "who are in the US temporarily and want a green card must return to their home country to apply, except in extraordinary circumstances," the statement was 31 words long. The bureaucratic disruption it unleashed will take years to measure.

The policy shift — from adjustment of status (filing for a green card while remaining in the United States) to mandatory consular processing (returning to your home country to complete the application at a U.S. embassy or consulate) — affects every employment-based green card applicant currently in America on a temporary visa. For Indian nationals, who represent the largest single bloc of employment-based green card seekers, the consequences are not just inconvenient. They are structurally unworkable.

## The Bottleneck Nobody in Washington Discussed

The United States maintains four consular posts in India that process immigrant visas: the embassy in New Delhi, and consulates in Mumbai, Chennai, and Hyderabad (Kolkata handles only nonimmigrant visas). Together, these four offices serve a population of 1.4 billion people in a country that sends more employment-based green card applicants to the United States than any other nation on earth.

As of May 2026, wait times for visa appointments at Indian consulates vary widely — Kolkata shows a 30-day median wait for nonimmigrant appointments, but immigrant visa processing at the four posts follows a separate and more constrained schedule. The State Department does not publish real-time wait times for immigrant visa interviews at individual posts, which means applicants are flying blind until they enter the queue.

Here is the math that Washington either did not do or did not care about: an estimated 1.2 million Indian nationals currently in the United States have pending or potential green card applications. The four Indian consular posts that process immigrant visas were designed to handle a steady stream of new applicants from India — people applying from within the country. They were not built to absorb a sudden, policy-driven wave of applicants who must now return from the United States, many of whom have cases that were previously being adjudicated domestically by USCIS field offices.

## The EB-2 and EB-3 Catch-22

The consular processing mandate collides with a second, older problem: India's country-specific green card backlog.

Under current law, no single country can receive more than 7% of the total employment-based green cards issued in a given year — roughly 9,800 out of 140,000. India's demand dwarfs this cap. The result is a backlog that, for EB-2 (advanced degree professionals), currently stretches to priority dates around 2012-2013. For EB-3 (skilled workers), the dates are even further back, hovering around 2010-2011.

What this means in practice: an Indian software engineer who filed an I-140 (immigrant worker petition) in 2013 is still waiting for a green card in 2026. Under the old system, that engineer could remain in the United States on an H-1B visa (renewed indefinitely while the green card application was pending), continue working, raise their children in American schools, pay American taxes, and wait.

Under the new system, that same engineer is expected to return to India to complete consular processing. But their priority date has not become current — they are still years away from a green card being available. So they must choose: stay in the United States and hope the "extraordinary circumstances" exception applies, or return to India and wait — potentially for years — with no guarantee of when (or whether) they will be called for a consular interview.

If they leave, their H-1B status terminates. Their spouse's H-4 EAD (work authorization) terminates. Their children, who may be U.S. citizens by birth, face a choice between staying in America without their parents or uprooting to India.

## The Employer Problem

The disruption does not stop at the individual. American employers who sponsored these green card applications face their own crisis.

A senior engineer at a Fortune 500 company who has been working on critical projects for a decade cannot be casually replaced. If that engineer must return to India for consular processing — a journey that, given the backlog, could take months or years before an interview is scheduled — the employer loses institutional knowledge, project continuity, and the investment they made in sponsoring the green card in the first place.

The employer also loses the legal leverage that kept the employee in the United States. An H-1B worker waiting for a green card is, by design, tied to their sponsoring employer. Remove the worker from the country, and the employer's retention tool disappears. The worker, now in India, can simply take a job elsewhere — in Bangalore, London, Toronto, or any of the dozen countries actively recruiting the exact talent pool that America is pushing out.

## What "Extraordinary Circumstances" Actually Means

The USCIS memo does include an exception: adjustment of status remains available in "extraordinary circumstances." Immigration attorneys have noted that the memo specifically mentions several factors that adjudicators should weigh — U.S. citizen children, deep community ties, home ownership, established employment, and the impracticality of consular processing.

A legal analysis published on LinkedIn by immigration attorney Aaron Finkle argued that the memo "contains important protections being completely ignored in the panic," noting that H-1B, O-1, and E-3 holders are in "dual intent" visa categories, meaning applying for a green card is explicitly not inconsistent with maintaining their nonimmigrant status.

But "extraordinary circumstances" is a discretionary standard, not a right. Each case will be adjudicated individually by a USCIS officer who has been told, in writing, that the default expectation is consular processing. The memo gives officers permission to approve domestic adjustment — it does not require them to.

For Indian applicants, this means their green card outcome now depends not on the law or their qualifications or their wait time, but on which officer reviews their case and how that officer interprets "extraordinary." That is not a system. It is a lottery layered on top of a lottery.

## The Numbers That Should Worry Washington

India is the United States' most important source of skilled labor. Indians account for 71% of H-1B approvals. Indian companies have invested over $20 billion in the American economy. Indian-origin professionals hold leadership positions at Google, Microsoft, Adobe, IBM, and dozens of other Fortune 500 companies.

Secretary of State Marco Rubio, speaking in New Delhi on May 25, acknowledged this explicitly: "I accept the contribution that Indians have made to the US economy." He described the visa overhaul as "modernization" and urged India to "give the reform process time."

But modernization implies an upgrade. What the consular processing mandate delivers, at least for Indian nationals, is a system that was already the slowest in the world made slower still — by routing cases through consulates that lack the capacity to handle them, in a country where applicants may no longer have homes to return to, for green cards that may not become available for another decade.

The 1.2 million Indians affected are not asking for special treatment. They are asking for the system to be physically capable of processing what it demands. Right now, it is not."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
