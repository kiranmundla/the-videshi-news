#!/usr/bin/env python3
"""Immigration writer — July 14, 2026 7:00 PM PT run"""
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


# ──────────────────────────────────────────────
# Article 1: The Fake Degree Scandal
# ──────────────────────────────────────────────

article1_body = """The numbers are ugly. Over 100,000 forged diplomas. Twenty-eight universities implicated. One institution alone — Manav Bharti University in Himachal Pradesh — accused of producing more than 36,000 fake degrees. The certificates, sold for as little as $1,400 apiece, spanned medicine, nursing, engineering, and information technology. Indian authorities seized them in December 2025, and the fallout has been ricocheting through the American immigration system ever since.

The seizure, first reported by Insider Wire and confirmed by Indian law enforcement, exposed what investigators described as an organized criminal enterprise. Forged university seals, fabricated transcripts, and counterfeit certifications were manufactured at industrial scale and marketed to individuals seeking employment abroad — particularly in the United States, where the H-1B visa program makes a bachelor's degree or its foreign equivalent the legal prerequisite for a "specialty occupation" under INA §214(i).

A fraudulent degree does not merely embellish a résumé. It fabricates the statutory basis of the visa itself, invalidating the petition USCIS approved and the Labor Condition Application the employer certified. Every fraudulent credential that slipped through represents a systemic failure.

## The political amplification

The diploma bust landed in Washington at precisely the wrong moment for the Indian diaspora. On July 8, Vice President JD Vance stood at an anti-fraud event in Milwaukee and announced that the Department of Labor had fired off dozens of subpoenas targeting H-1B and PERM visa abuse. Labor Department Inspector General Anthony D'Esposito told reporters that his office had uncovered "widespread schemes in which employers and labor brokers submitted fraudulent applications, exploited foreign workers through coercive wage-kickback arrangements, and undercut American workers by flooding the market with below-wage labor."

The investigation's scope is sweeping. D'Esposito said his team had received whistleblower tips about "some of the biggest companies," including Cognizant, the IT services giant founded in India and headquartered in New Jersey. Department of Homeland Security assessments have suggested that as many as 21 percent of H-1B petitions are fraudulent — a figure that has become a staple of the administration's messaging.

A separate claim, widely circulated in conservative media, traces to former U.S. diplomat Mahvash Siddiqui, who alleged that 80 to 90 percent of the H-1B applications she reviewed from India during her 2005–2007 tenure involved fraudulent documentation. That figure describes a single officer's experience at a single post nearly two decades ago, not a current government assessment. But it has been grafted onto the 2026 diploma seizure as though the two are a single, unbroken story — and politicians have not been rushing to draw the distinction.

## The pushback from the profession

Immigration attorneys are pushing back. Kelly Fortier, a partner at Michael Best who has worked H-1B cases for over twenty years, told the Milwaukee Journal Sentinel that she has never personally encountered companies abusing the program. "If Vice President Vance has concerns about this and if people are concerned about this, I guess I would like to see the evidence, because I personally have not seen it in my day-to-day practice," she said.

Doris Brosnan, an employment attorney at von Briesen & Roper with 27 years of experience specializing in H-1B visas, was blunter. "I can't say that there isn't any fraud. Of course, there's fraud. But the question is, 'How widespread is it, and what's the way to correct it?'"

Both lawyers noted that the program already has safeguards: government regulators visit work sites, and prevailing-wage and actual-wage requirements are designed to prevent employers from undercutting American salaries.

## The collateral damage

The immediate victims of the credential fraud were, paradoxically, the qualified applicants — Indian professionals who earned legitimate degrees from reputable institutions and now face a system that treats them with heightened suspicion. Consular processing times have stretched. Site visits by USCIS's Fraud Detection and National Security directorate have intensified. The social media vetting requirement introduced by the State Department has compounded delays.

USCIS admitted it does not track data on H-1B awardees who obtained degrees from institutions like Manav Bharti University. That gap is itself a scandal. The absence of a credential-verification database means that the enforcement response has been broad and blunt rather than surgical.

For the roughly 600,000 H-1B visa holders currently in the United States — 73 percent of whom are Indian nationals, according to Pew Research — the fake-degree scandal has become a reputational tax. They did not forge anything. They passed interviews, clearances, and credential evaluations. But the political narrative does not make that distinction, and neither, increasingly, does the bureaucracy.

The legitimate Indian professionals who built Silicon Valley's infrastructure, who staff America's hospitals and research labs, who pay taxes and raise families under a system that already makes them wait decades for a green card — they are now paying for someone else's fraud, in a currency they cannot afford: trust."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "One Hundred Thousand Forged Diplomas. The Fraud That Is Rewriting the Rules for Every Indian Visa Applicant",
    "subheadline": "A massive diploma seizure from 28 Indian universities has handed Washington the ammunition to treat an entire community as suspect. Immigration lawyers say the crackdown is painting with far too broad a brush.",
    "slug": make_slug("forged-diplomas-fraud-indian-visa-applicants-trust-crisis"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The actions of a criminal diploma ring are being used to justify sweeping scrutiny of all Indian visa holders, threatening the reputation and processing times for hundreds of thousands of legitimate professionals.",
    "tags": ["h1b", "visa-fraud", "uscis", "fake-degrees", "immigration-enforcement", "indian-diaspora"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Milwaukee Journal Sentinel", "url": "https://www.jsonline.com/story/news/politics/2026/07/10/vice-president-jd-vance-targets-alleged-h-1b-visa-fraud-in-milwaukee/90860820007/"},
        {"name": "Daily Caller", "url": "https://dailycaller.com/2026/07/08/indian-fraud-american-healthcare/"},
        {"name": "Insider Wire / The Asian Mirror", "url": "https://theasianmirror.com/100000-fake-degrees-used-to-exploit-us-h-1b-visa-system/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/07/09/us-news/work-visa-fraud-costs-america-big-hail-the-trump-teams-crackdown/"},
        {"name": "Fox Business", "url": "https://www.foxbusiness.com/politics/trump-admin-launches-its-first-major-h-1b-visa-fraud-investigation"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37012315/pexels-photo-37012315.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Framed diplomas stacked for an academic ceremony",
    "image_attribution": "Pexels",
    "body": article1_body.strip()
}


# ──────────────────────────────────────────────
# Article 2: EB-5 India Cap + Grandfathering Deadline
# ──────────────────────────────────────────────

article2_body = """On June 5, the U.S. Department of State made it official: every available EB-5 unreserved immigrant visa for Indian nationals in fiscal year 2026 had been issued. The window is shut. No more unreserved EB-5 green cards for Indians until the numbers reset on October 1, when fiscal year 2027 begins.

The announcement itself was not unexpected. The July Visa Bulletin had already signaled that retrogression or unavailability was likely. But its timing has created an uncomfortable collision with a second, far more consequential deadline: September 30, 2026, the date by which Regional Center EB-5 petitions must be filed to receive grandfathering protection under the EB-5 Reform and Integrity Act of 2022.

That deadline is now eleven weeks away, and for a certain class of Indian immigrants, it may represent the last clean shot at an employer-independent green card for years.

## What the grandfathering deadline means

The EB-5 Reform and Integrity Act (RIA), signed in March 2022, reauthorized the Regional Center program — the most popular EB-5 pathway, through which investors pool capital into government-designated projects that create jobs — through September 30, 2027. But the law includes a critical provision: petitions "properly filed" on or before September 30, 2026, are grandfathered. USCIS must continue adjudicating them even if Congress later allows the Regional Center program to lapse.

Petitions filed after that date carry no such protection. If the program sunsets in 2027 and is not reauthorized, late filers could see their cases administratively closed.

For Indian-born applicants, this matters more than for most nationalities. India is already a high-demand chargeability area in EB-5. The unreserved category, which accounts for 68 percent of all EB-5 visas, has now been fully allocated. Filing before the grandfathering deadline locks in both the priority date and the statutory protection — a two-for-one that will not be available after September.

## The EB-5 landscape for Indian investors

The investment minimums are not trivial: $800,000 for projects in a Targeted Employment Area (TEA), and $1,050,000 for all other areas. The total cost, including legal fees, project due diligence, and filing expenses, typically runs to $900,000 to $1.2 million.

But for families stuck in the EB-2 or EB-3 employment-based green card backlog — where wait times for Indian nationals can stretch beyond a decade, and children risk aging out of dependent status at 21 — the EB-5 program offers something no other pathway does: a route to permanent residency that does not depend on an employer's sponsorship, an H-1B lottery selection, or a congressional vote on per-country caps.

The reserved categories offer some relief. Under the RIA, 20 percent of EB-5 visas are set aside for rural projects, 10 percent for high-unemployment areas, and 2 percent for infrastructure. As of now, all three reserved categories remain current for Indian applicants — meaning there is no per-country backlog and visas are immediately available. Immigration attorneys have been steering Indian clients toward rural set-aside projects specifically because of this advantage.

"The rural set-aside is the fastest path right now," said Joseph Barnett of WR Immigration. But he and other practitioners warn that the window may not stay open indefinitely. As filings accumulate, reserved categories could themselves retrogress.

## Why this matters to the diaspora

The EB-5 program has historically been associated with wealthy Chinese investors. But Indian demand has surged in recent years, driven by three converging forces: the EB-2/EB-3 backlog that can leave a family in immigration limbo for a generation, the increasing restrictions on the H-1B pathway under the current administration, and the aging-out crisis facing children of long-term visa holders.

Oliver Yang of Reid & Wise noted that the cap being hit "underscores the significant volume of Indian investors already in the unreserved visa pipeline." Dennis Tristani of Tristani Law added that unused unreserved visa numbers will not flow into reserved categories this fiscal year — meaning the reserved pathway is even more critical than usual.

The practical calculus is straightforward, if daunting. An Indian family with the financial resources faces a choice: continue waiting in an employment-based backlog that may stretch another fifteen years, during which their children could age out, their H-1B status could be challenged, and the policy environment could shift further against them — or commit roughly a million dollars to an EB-5 filing before September 30 and lock in grandfathering protection, a priority date, and access to a reserved category that is still current.

Neither option is comfortable. But one of them has a deadline, and the clock is now audible.

## What to do before September 30

EB-5 filings are not quick. The process — selecting a project, conducting due diligence on the Regional Center, assembling source-of-funds documentation, and preparing the I-526E petition — typically takes weeks to months. Indian applicants who are seriously considering the EB-5 route should be in active conversations with immigration counsel now, not in the final weeks of September.

The direct (stand-alone) EB-5 program, which involves investing in and directly managing a new commercial enterprise, is permanently authorized under the Immigration and Nationality Act and does not face a sunset or grandfathering issue. But it requires hands-on business management and is far less common.

For most Indian investors, the Regional Center pathway remains the practical choice — and September 30 is the hard boundary that separates a protected filing from an unprotected one."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's EB-5 Window Just Closed. The Backup Plan Has an Eleven-Week Deadline",
    "subheadline": "Indian nationals have exhausted their unreserved EB-5 investor visas for fiscal year 2026. A September 30 grandfathering deadline now looms over every family weighing the million-dollar bet on permanent residency.",
    "slug": make_slug("india-eb5-cap-hit-grandfathering-deadline-september"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "For Indian families trapped in decades-long green card backlogs and facing H-1B uncertainty, the EB-5 investor visa has become the only employer-independent path to permanent residency — and its most important deadline is eleven weeks away.",
    "tags": ["eb5", "green-card", "investor-visa", "immigration", "indian-diaspora", "green-card-backlog"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Berry Appleman & Leiden LLP (BAL)", "url": "https://www.bal.com/immigration-news/united-states-eb-5-unreserved-visa-limit-met-for-india/"},
        {"name": "Envoy Global", "url": "https://www.envoyglobal.com/resources/news-alerts/india-eb-5-unreserved-visa-cap-reached-for-fy-2026"},
        {"name": "EB5Investors.com", "url": "https://www.eb5investors.com/news/india-exhausts-eb5-unreserved-visa-cap"},
        {"name": "US Immigration Advisor", "url": "https://usimmigrationadvisor.com/eb-5-visa-india/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in New York City",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}


# ──────────────────────────────────────────────
# Insert articles
# ──────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
