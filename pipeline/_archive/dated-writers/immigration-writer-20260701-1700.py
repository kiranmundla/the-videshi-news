#!/usr/bin/env python3
"""Immigration writer — 2026-07-01 17:00 PDT run."""
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


# ── ARTICLE 1 ──────────────────────────────────────────────────────────────────

art1_headline = "Twelve States Now Punish Employers for Hiring Mistakes. Yours May Be One of Them"

art1_subheadline = "Indiana's FAIRNESS Act and Tennessee's new criminal penalties take effect today, joining a growing patchwork of state immigration enforcement laws that could trip up IT staffing companies and the H-1B workers they employ."

art1_body = """As of 1 July, the state of Indiana can shut down your business for hiring the wrong person.

Senate Enrolled Act 76, branded the FAIRNESS Act by Governor Mike Braun, is the broadest state-level immigration enforcement law in the country. It covers every employer, in every industry, with no minimum headcount. The Indiana Attorney General can investigate tips, audit payrolls, and seek escalating penalties — from a five-day suspension of operating authorisation for a first offence to permanent revocation for repeat violators. Fines run up to $10,000 per violation.

"The FAIRNESS Act means that illegal immigration is no longer just a federal issue," Attorney General Todd Rokita said at a press conference on 30 June, one day before the law took effect. "Indiana can, and should, provide some enforcement."

The safe harbour is E-Verify. Employers who can prove they used the federal electronic verification system — or a comparable programme — are shielded from liability. Those who rely on paper I-9 forms are not so fortunate: compliance specialists estimate error rates above 90 per cent in paper-based systems, meaning a single audit could uncover dozens of technical violations.

Indiana is not alone. Tennessee enacted new immigration laws effective the same day, including criminal penalties — a Class E felony — for any state or local official who leaks information about immigration enforcement operations. Residents who ignore a federal deportation order for more than 90 days now face a Class A misdemeanour, punishable by nearly a year in jail. The ACLU has filed a lawsuit to block that provision.

Ohio's E-Verify Workforce Integrity Act, which took effect in March, imposes penalties up to $25,000 per violation on nonresidential construction contractors. Florida has required E-Verify for private employers with 25 or more workers since 2023. Alabama, Arizona, Georgia, Mississippi, North Carolina, South Carolina, and Utah all maintain their own employer mandates.

Maryland, meanwhile, moved in the opposite direction on 1 July: a new data-privacy law now prohibits certain businesses from selling consumer data to government agencies engaged in civil immigration enforcement, adding a layer of protection for immigrant communities.

The Fisher Phillips law firm, in a nationwide employer briefing published this week, counted more than a dozen states with active or incoming employer-facing immigration enforcement provisions — a number that has roughly doubled since 2023.

## What This Means for the Indian Diaspora

The immediate target of these laws is unauthorised employment, not H-1B holders. But the ripple effects matter.

IT staffing and consulting firms — the backbone of the H-1B ecosystem for Indian workers — are especially exposed. Many operate across state lines, placing contractors at client sites in Indiana, Tennessee, and Ohio. A single documentation error, or a gap between an employee's visa expiration and renewal approval, could trigger an investigation. The FAIRNESS Act's "knowingly or intentionally" standard offers some protection, but E-Verify compliance is now effectively mandatory in any state with enforcement teeth.

For H-1B workers themselves, the practical concern is employer behaviour. Companies facing state-level penalties on top of federal scrutiny may slow-walk international hiring, tighten internal compliance reviews, or default to domestic candidates rather than risk an audit. In a labour market already chilled by the $100,000 H-1B fee (recently struck down by a federal judge, but under appeal), any additional friction compounds the problem.

The broader pattern is unmistakable: immigration enforcement is decentralising. What was once a federal monopoly is becoming a 50-state patchwork, and the states with the largest Indian-American populations — Texas, California, New Jersey, Illinois — are watching Indiana's experiment closely.

If you work for an IT staffing company, ask your employer whether they use E-Verify. If you are an employer, the question is simpler: do you use it everywhere, or only where the law requires it? After 1 July, the answer matters more than it used to."""

art1_sources = json.dumps([
    {"name": "South Bend Tribune", "url": "https://www.southbendtribune.com/story/news/local/2026/06/30/indiana-fairness-act-begins-july-1-prohibits-hiring-undocumented-immigrants/90757699007/"},
    {"name": "Fisher Phillips / JDSupra", "url": "https://www.jdsupra.com/legalnews/employer-cheat-sheet-for-workplace-laws-1436889/"},
    {"name": "Faegre Drinker", "url": "https://www.faegredrinker.com/en/insights/publications/2026/6/the-fairness-act-indianas-new-immigration-law-with-a-july-1-2026-deadline-for-employers"},
    {"name": "The Tennessean", "url": "https://www.tennessean.com/story/news/politics/2026/06/29/new-tennessee-laws-july-1-immigration-child-influencers/90694461007/"}
])


# ── ARTICLE 2 ──────────────────────────────────────────────────────────────────

art2_headline = "He Filed Fake H-1B Petitions Under UC Davis's Name. Now He Faces Five Years"

art2_subheadline = "Two East Bay men pleaded guilty to conspiracy to commit visa fraud after filing bogus H-1B petitions that claimed workers would be employed at the University of California. Their sentencing on 30 July comes as USCIS signals zero tolerance for staffing company fraud."

art2_body = """Sampath Rajidi ran two visa servicing companies out of Dublin, California — S-Team Software Inc. and Uptrend Technologies LLC. Sreedhar Mada was the Chief Information Officer of the University of California Agriculture and Natural Resources division in Davis. Between June 2020 and January 2023, the two men conspired to submit fraudulent H-1B visa petitions that falsely claimed foreign workers would be employed at the University of California.

The positions did not exist. The workers never set foot on a UC project. Instead, Rajidi used Mada's name and the credibility of his university title to clear USCIS approval, then marketed the visa holders to private-sector clients. It was a textbook body-shopping scheme dressed in academic clothing.

Both men pleaded guilty to conspiracy to commit visa fraud on 17 April, U.S. Attorney Eric Grant announced. They face sentencing by U.S. District Judge Troy L. Nunley on 30 July. The maximum statutory penalty is five years in prison and a $250,000 fine.

The investigation was led by four federal agencies — the State Department's Diplomatic Security Service, Homeland Security Investigations, the Treasury Inspector General for Tax Administration, and USCIS's own Fraud Detection and National Security Directorate. The multi-agency response signals the government's appetite for prosecuting visa fraud well beyond simple administrative denial.

## A Pattern, Not an Anomaly

The Rajidi-Mada case is not an isolated incident. It fits a pattern that Indian-origin IT staffing companies have been associated with for over a decade, and one that has become a favourite data point for lawmakers seeking to restrict or eliminate the H-1B programme.

In the most recent congressional session alone, four separate bills have proposed ending or dramatically curtailing H-1B visas. The sponsors routinely cite fraud statistics. A 2024 USCIS report found that nearly 30 per cent of H-1B site visit inspections resulted in adverse findings — the worker was not at the listed worksite, or the job did not match the petition.

Every fraudulent petition depletes the annual H-1B cap of 85,000 visas. When Rajidi secured visas for workers who never performed the claimed role, he took a slot from a legitimate applicant — likely another Indian national, given that Indians account for roughly 71 per cent of all H-1B beneficiaries.

The damage extends beyond the cap. Fraud cases provide political ammunition. Representative Harriet Hageman's American White-Collar Worker Jobs Act of 2026, which would cap any employer's non-immigrant workforce at 5 per cent, explicitly cites fraudulent use of the programme as justification. Senator Chuck Grassley has pointed to staffing company abuses in every immigration hearing this session.

## What Legitimate H-1B Workers Should Know

If you work for a staffing or consulting company — or if your employer subcontracts through one — the Rajidi-Mada case is a reminder to verify the basics. Your H-1B petition lists a specific job at a specific worksite. If your actual work has nothing to do with what the petition describes, or if your "employer of record" has never assigned you a project, the petition may have been fraudulently filed. You are not the criminal in that scenario, but you are the one whose visa is at risk.

USCIS site visits are increasing. Officers now arrive unannounced at worksites to confirm that H-1B employees are performing the described role. If you are not at the listed address, or if the role does not exist, the visit triggers an investigation that can lead to petition revocation.

For Indian professionals weighing an offer from a lesser-known IT staffing company, due diligence is not optional. Check the company's H-1B filing history on the Department of Labor's disclosure database. Look for patterns — dozens of petitions filed for the same generic job title at the same address, or a company with five employees sponsoring fifty visas. If the numbers do not add up, the employer may be selling access to the H-1B cap, not a real job.

The H-1B programme's legitimacy rests on the premise that every petition represents a genuine need for a specific worker in a specific role. Every case like Rajidi and Mada's erodes that premise — and moves the political needle closer to the programme's abolition."""

art2_sources = json.dumps([
    {"name": "U.S. Department of Justice — Eastern District of California", "url": "https://www.justice.gov/usao-edca/pr/east-bay-men-plead-guilty-conspiracy-commit-h1-b-visa-fraud-claiming-clients-would"},
    {"name": "USCIS", "url": "https://www.uscis.gov/news/news-releases/uscis-efforts-lead-to-two-guilty-pleas-in-h-1b-fraud-conspiracy-case"},
    {"name": "Livemint — H-1B Legislation", "url": "https://www.livemint.com/news/india/us-lawmakers-intensify-push-against-h-1b-visas-is-2026-its-death-knell-11747843024479.html"},
    {"name": "ICE — H-1B Fraud Cases", "url": "https://www.ice.gov/news/releases/indian-national-pleads-guilty-false-work-visa-scheme"}
])


# ── BUILD ARTICLES ─────────────────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": make_slug("state-immigration-enforcement-july-1-indiana-fairness-act"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "IT staffing companies that place H-1B workers across state lines face heightened E-Verify enforcement, and the compliance burden could slow international hiring in states with large Indian-American populations.",
        "tags": ["immigration", "e-verify", "indiana", "state-law", "h1b", "it-staffing", "enforcement"],
        "urgency": "high",
        "sources": art1_sources,
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Indiana_State_Capitol_building.jpg/1280px-Indiana_State_Capitol_building.jpg",
        "image_caption": "The Indiana State Capitol in Indianapolis, where the FAIRNESS Act was signed into law",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": make_slug("h1b-fraud-uc-davis-rajidi-mada-guilty-plea"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Every fraudulent H-1B petition depletes the annual cap of 85,000 visas, directly reducing slots available to legitimate Indian applicants and fuelling the legislative push to abolish the programme.",
        "tags": ["h1b", "visa-fraud", "uscis", "staffing-company", "uc-davis", "prosecution"],
        "urgency": "medium",
        "sources": art2_sources,
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center in New York, one of dozens of offices processing H-1B petitions",
        "image_attribution": "Wikimedia Commons",
        "body": art2_body,
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
