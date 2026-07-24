#!/usr/bin/env python3
"""Immigration writer – 2026-07-12 07:00 AM PT run."""
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
        "headline": "The July Visa Bulletin Just Shut Three Doors on Indian Applicants. None Will Reopen Before October",
        "subheadline": "EB-2 India is unavailable. EB-5 unreserved India is unavailable. EB-1 India just slid backward by two months. For hundreds of thousands of Indian professionals waiting for green cards, the rest of fiscal year 2026 is a dead zone.",
        "slug": make_slug("july-visa-bulletin-eb2-eb5-india-unavailable-eb1-retrogression"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian professionals on H-1B visas waiting for EB-2 or EB-5 green cards are completely frozen until October — no approvals, no visa issuance, and the EB-2-to-EB-3 downgrade question is suddenly urgent again.",
        "tags": ["green-card", "visa-bulletin", "eb-2", "eb-5", "eb-1", "uscis", "india-backlog"],
        "urgency": "high",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "VisaNation / Immi-USA", "url": "https://www.immi-usa.com/visa-bulletin/"},
            {"name": "WR Immigration (Wolfsdorf)", "url": "https://wolfsdorf.com/united-states-eb-2-india-unavailable-through-september-30-2026/"},
            {"name": "MC Law Firm", "url": "https://www.mclawfirm.com/blog/u-s-july-2026-visa-bulletin-updates"},
            {"name": "BAL Immigration", "url": "https://bal.com/"},
            {"name": "RJ Immigration Law", "url": "https://rjimmigrationlaw.com/"}
        ]),
        "score_total": 88,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center in Jamaica, Queens, New York",
        "image_attribution": "Wikimedia Commons",
        "body": """The U.S. Department of State's July 2026 Visa Bulletin is the worst in recent memory for Indian nationals. Three employment-based green card categories have either gone dark or retreated, leaving hundreds of thousands of skilled professionals with no path to permanent residency until the fiscal year resets on October 1.

Here is what happened — and what it means for the Indian diaspora.

## EB-2 India: Unavailable

The headline change. The EB-2 category — the primary route for Indian professionals with advanced degrees or exceptional ability, including those filing National Interest Waivers — has been marked "Unavailable" for the remainder of FY 2026. In June, the final action date sat at September 1, 2013. Now it reads "U."

The State Department says plainly that India's pro-rated EB-2 limit has been reached. No immigrant visas will be issued, and no adjustment-of-status applications can be approved under EB-2 India until new fiscal year numbers arrive in October. Immigration law firm WR Immigration estimates the October date will advance to at least the May 2026 level, but cautions that this depends entirely on demand.

For the roughly 400,000 Indian professionals stuck in the EB-2 queue, this is not a surprise — it is the system behaving exactly as its critics have warned. The per-country cap of seven percent, set by Congress decades ago, continues to throttle Indian applicants who represent a wildly disproportionate share of demand.

## EB-5 Unreserved: Also Dark

India's unreserved EB-5 investor visa category followed EB-2 into unavailability. The State Department confirms that India's pro-rated EB-5 unreserved limit has been exhausted for the fiscal year.

There is one lifeline. All three EB-5 set-aside categories — Rural (20 percent of visas), High Unemployment (10 percent), and Infrastructure (2 percent) — remain "Current" for every country, including India and China. For prospective investors, a set-aside project is now one of the only immediately available immigrant visa pathways left.

## EB-1 India: Two Months Backward

The EB-1 category, covering individuals of extraordinary ability, outstanding professors, and multinational executives, retrogressed from December 15, 2022 to October 15, 2022 — a two-month slide in the wrong direction. China, meanwhile, advanced two months to June 1, 2023.

The State Department explicitly warns that India's pro-rated EB-1 limit could be reached before September 30, meaning further retrogression — or outright unavailability — is on the table. For Indian EB-1A self-petitioners who have been treating this category as a backup to EB-2, that safety valve is now under pressure too.

## EB-3 India: The Only Forward Movement

EB-3, covering skilled workers and professionals, offered the month's only good news for Indians. The final action date inched forward from December 15, 2013 to January 1, 2014. Modest, but it moved.

This creates a tactical question that immigration attorneys are already fielding: should Indian EB-2 holders consider an EB-3 "downgrade"? With EB-2 unavailable and EB-3 current to January 2014, some beneficiaries whose EB-3 priority dates are now reachable may find the supposedly lesser category is their faster path to a green card. It is a counterintuitive move, but one that the system's distortions have made rational.

## Why This Keeps Happening

The pattern is structural. India sends more H-1B workers, more green card applicants, and more international students to the United States than any other country. But the per-country cap allocates the same seven percent of employment-based visas to India as it does to countries that file a fraction of the applications.

The result is a backlog measured in decades. An Indian professional who filed an EB-2 petition today could wait 12 to 15 years — or longer — for a green card. The Fairness for High-Skilled Immigrants Act, which would eliminate per-country caps, has been introduced in various forms since 2011. It has never passed.

## What to Do Before October

Immigration attorneys recommend several steps for those caught in the freeze. First, get documentarily qualified now. When October arrives and new numbers become available, cases that are complete will be first in line. Second, evaluate the EB-2-to-EB-3 downgrade seriously — the math may favor it. Third, for those with the means, EB-5 set-aside investments remain current and offer a parallel path.

The October 2026 bulletin should bring broad forward movement as a fresh allocation of employment-based numbers becomes available. But the annual reset is a temporary reprieve, not a fix. Without legislative reform to the per-country caps, next July's bulletin will likely tell the same story."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "USCIS Is Showing Up at Remote Workers' Front Doors. Here Is What Every H-1B Holder Should Know",
        "subheadline": "With the federal government launching its largest H-1B fraud investigation in years, the Fraud Detection and National Security Directorate is increasing unannounced home office visits for remote workers — and what you say at the door can determine your visa's future.",
        "slug": make_slug("uscis-fdns-home-office-site-visits-h1b-remote-workers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders working remotely — the majority of all H-1B workers — face heightened risk of unannounced USCIS site visits at their homes, especially as the DOL's new fraud probe targets consulting firms and third-party placements that employ a large share of Indian tech workers.",
        "tags": ["h1b", "uscis", "fdns", "site-visit", "remote-work", "fraud-probe", "compliance"],
        "urgency": "medium",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Reddy Neumann Brown PC", "url": "https://www.rnlawgroup.com/h-1b-home-office-site-visits/"},
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/uscis-employer-site-visits-what-employers-need-to-know.html"},
            {"name": "Cozen O'Connor", "url": "https://www.cozen.com/"},
            {"name": "Fox Business", "url": "https://www.foxbusiness.com/politics/trump-admin-launches-first-major-h-1b-visa-fraud-investigation"},
            {"name": "Benesch Friedlander (Mondaq)", "url": "https://www.mondaq.com/unitedstates/work-visas/1544890/how-to-prepare-for-unannounced-administrative-site-visits"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12498876/pexels-photo-12498876.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A remote worker at home — USCIS can now conduct unannounced site visits at home offices listed on H-1B petitions",
        "image_attribution": "Pexels",
        "body": """When Vice President JD Vance stood in Milwaukee on July 8 and announced that the Department of Labor had fired off "dozens of subpoenas" targeting H-1B visa fraud, the signal was unmistakable: enforcement is escalating. What received less attention is the enforcement tool that arrives not through the mail but at your front door.

The Fraud Detection and National Security Directorate, known as FDNS, has been quietly expanding its Administrative Site Visit and Verification Program to include something that would have seemed unusual five years ago — unannounced visits to the home offices of H-1B workers. With remote and hybrid work now standard across the technology sector, the home address listed on a Labor Condition Application is increasingly where USCIS comes knocking.

For Indian H-1B holders — who account for 73 percent of all H-1B workers — the combination of the new federal fraud probe and rising home visits creates a landscape that demands preparation, not panic.

## What FDNS Is Looking For

A home site visit is not, on its own, an accusation. Many visits are random compliance reviews, part of USCIS's routine verification that the information on an H-1B petition matches reality. The officer is checking six things: that the employee lives at the listed address, that they are actively employed by the petitioning employer, that their job duties match the petition, that their salary is unchanged, that the employer-employee relationship is intact, and that no material changes have occurred that would require an amended petition.

That last point catches people. If you were approved for a software engineer role and your duties have shifted toward product management, that discrepancy — even an innocent one — can trigger further scrutiny.

## They Do Not Call First

FDNS officers conduct unannounced visits. There is no advance notice, no email, no phone call. Most arrive during normal business hours. If the employee is not home, the officer may leave contact information and request a callback.

Immigration attorneys uniformly advise that employers should train remote H-1B workers about the process before it happens. Knowing that a visit is possible, and knowing what to say, makes the difference between a routine compliance check and a case that gets flagged for investigation.

## The Questions at the Door

Officers focus on verifying what the petition says. Expect questions in four categories.

Employment verification: What company do you work for? What is your job title? When did you start? Who is your supervisor? Are you full-time?

Job duties: What are your primary responsibilities? What projects are you working on? What tools and technologies do you use? Who assigns your work?

Worksite: Do you work from this address? Is this your primary location? Do you report to another office? Do you work at client sites?

Compensation: What is your current salary? Are you paid hourly or salaried? Do you receive benefits?

The officer may also ask to see your workspace and may photograph it. They will want to confirm that you are working in a professional setting consistent with the specialty occupation described in your petition.

## What Not to Do

Immigration attorneys agree on the danger zones. Do not volunteer information beyond what is asked. Do not speculate about company strategy, hiring decisions, or colleagues' visa statuses. Do not lie or exaggerate — inconsistencies between your answers and the petition are exactly what FDNS is trained to spot. And do not refuse to engage entirely, which can itself trigger an adverse finding.

You have the right to request that your immigration attorney be present, either in person or by phone. If the officer arrives unexpectedly and your attorney is unavailable, you can ask the officer to reschedule. Most will accommodate the request.

## Why This Matters Now

The timing is not coincidental. The Trump administration's July 8 announcement specifically named the H-1B program and employment-based green cards as targets. Labor Department Inspector General Anthony D'Esposito told Fox Business that investigators have identified "employers and labor brokers" who submitted fraudulent applications and exploited foreign workers through coercive wage-kickback schemes. Cognizant, the IT services giant founded in India, was named as one company that whistleblowers have flagged.

Department of Homeland Security assessments have estimated that as many as 21 percent of H-1B petitions involve fraud — a statistic that immigration attorneys dispute. Kelly Fortier, a partner at Michael Best with over 20 years of H-1B experience, told the Milwaukee Journal Sentinel: "I would like to see the evidence, because I personally have not seen it in my day-to-day practice."

But disputed or not, the stat is driving policy. FDNS site visits are expected to increase, and the focus on third-party placements — where an H-1B worker is employed by one company but works at a client site — puts Indian IT consulting firms squarely in the crosshairs.

## A Compliance Checklist

Keep these documents accessible at your home office: a copy of your approved H-1B petition and I-797 approval notice, your certified Labor Condition Application, recent pay stubs confirming the prevailing wage, your current job description matching the petition, and your employer's contact information for HR and immigration counsel.

Review your petition periodically. If your role has evolved — new title, different duties, changed work location — talk to your employer's immigration counsel about whether an amended petition is needed. A proactive amendment is always better than an adverse FDNS finding.

The fraud probe will run its course, and most H-1B holders who are working legitimate jobs at legitimate companies have nothing to fear from a compliance visit. But legitimacy alone is not enough. You also need to be prepared."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
