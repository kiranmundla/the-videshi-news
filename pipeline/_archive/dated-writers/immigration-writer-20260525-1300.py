#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-25 13:00 PDT batch"""
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


# ─────────────────────────────────────────────
# ARTICLE 1: Rubio-Jaishankar New Delhi Showdown
# ─────────────────────────────────────────────

article1_body = """Somewhere between the diplomatic pleasantries and the press conference microphones in New Delhi, Marco Rubio and S. Jaishankar had what might generously be called a frank exchange of views. The subject: whether Washington's sweeping visa overhaul is, as Rubio insists, a neutral act of "modernisation" — or, as the data strongly suggests, a policy whose heaviest burden falls squarely on India.

## "Not Targeted at India," Says the Man Whose Policies Target India

Speaking alongside India's External Affairs Minister on Sunday, Rubio deployed the word "modernisation" with the frequency of a man who'd rehearsed it on the flight over. "The changes that are happening now are not India-specific; it is global, it's being applied across the world," he said. He invoked his Cuban immigrant parents. He praised Indian investment of "over $20 billion" in the American economy. He urged patience during what he called a "period of transition."

Jaishankar was less diplomatic about the diplomacy. "I apprised Secretary Rubio of challenges that legitimate travellers face in respect of visa issuance," he said. Then the sharper line: "While we cooperate to deal with illegal and irregular mobility, our expectation is that legal mobility would not be adversely impacted as a consequence. After all, this is very relevant to our business, technology, and research cooperation."

Translation: we know the difference between illegal border crossings and an H-1B engineer at Google, and we'd like you to know it too.

## The Numbers Rubio Didn't Mention

While Rubio was framing the conversation around sovereignty and border security, the US Citizenship and Immigration Services was releasing data that told a rather different story. H-1B registrations for fiscal year 2027 plunged 38.5%, from 343,981 to just 211,600. The agency celebrated this as proof that "the days of abusing the programme with mass, low-wage registrations are over."

Indians account for roughly 71% of all approved H-1B applications. The six largest Indian IT firms — TCS, Cognizant, Infosys, HCL, Wipro, and Tech Mahindra — collectively received 11,041 H-1B visas as of March 2026, a 40% decline from 18,469 the previous year. TCS alone saw approvals drop by more than 3,200.

On the green card front, a USCIS memo issued on May 22 now requires foreign nationals to physically return to their home countries to apply for permanent residency — upending years of established practice where H-1B holders could adjust status without leaving. For Indians facing green card backlogs stretching decades, this isn't an inconvenience. It's a potential exile.

## Rubio on Anti-India Racism: "Every Country Has Stupid People"

When pressed about rising anti-Indian sentiment in the United States, Rubio offered a response that was either refreshingly honest or diplomatically reckless, depending on one's perspective. "I'm sure there are stupid people here," he said, gesturing vaguely at India. "There are stupid people in the United States that make dumb comments all the time."

He pivoted quickly to reassurance: "Our nation has been enriched by people who come to our country from all over the world, have become Americans, have assimilated into our way of life, and have contributed greatly." The word "assimilated" doing rather a lot of work in that sentence.

## What This Means for the Diaspora

For the roughly 1.2 million Indians on temporary work visas in the US, the Rubio-Jaishankar exchange wasn't abstract diplomacy — it was two governments negotiating the terms of their professional future.

The fact that India's foreign minister raised visa concerns directly with the US Secretary of State signals that New Delhi views the immigration crackdown as a bilateral irritant, not a domestic American matter to be quietly endured. That's significant. When immigration policy becomes foreign policy, the leverage dynamics change.

But leverage is slow. The DOL's proposed 30-33% wage hikes for H-1B positions, the $100,000 fee per new worker, and the consular processing mandate are all moving forward on their own timelines. For an H-1B holder in Cupertino watching this press conference, the relevant question isn't whether Rubio considers the policy "India-targeted." It's whether their employer will still find it economical to sponsor them next year."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Rubio Tells India Its Workers Aren't the Target — The Numbers Say Otherwise",
    "subheadline": "In a tense New Delhi press conference, the US Secretary of State insisted visa reforms are 'global modernisation.' India's foreign minister wasn't buying it, and neither should you.",
    "slug": make_slug("rubio-jaishankar-india-visa-reforms-not-targeted"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "India's foreign minister directly raised H-1B and visa concerns with the US Secretary of State — elevating the immigration crackdown from domestic policy to a bilateral diplomatic issue. For Indian Americans, this signals New Delhi is now treating visa restrictions as a negotiating point in the India-US relationship, but the policy machinery rolls on regardless.",
    "tags": ["h1b", "rubio", "jaishankar", "india-us-relations", "green-card", "diplomacy"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Fox News", "url": "https://foxnews.com/politics/rubio-pushes-back-indias-concerns-us-visa-curbs-says-policy-must-america-first-trump"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/world/rubio-says-h-1b-visa-changes-not-aimed-at-indian-a-38-5-per-cent-drop-in-registration-green-card-rules-say-differently-11779683463679.html"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/world/new-uscis-policy-could-force-h-1bs-seeking-green-cards-to-apply-from-home-countries/article69608919.ece"},
        {"name": "Indian Economic Observer", "url": "https://www.indianeconomicobserver.com/rubio-says-us-visa-changes-not-india-specific-part-of-global-migration-overhaul-praises-indian-investment-in-us/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": article1_body,
}


# ─────────────────────────────────────────────
# ARTICLE 2: Indian IT Firms H-1B Crater
# ─────────────────────────────────────────────

article2_body = """For two decades, the pipeline worked like clockwork: Indian IT services firms recruited engineers in Bengaluru and Hyderabad, trained them, shipped them to client sites in New Jersey and Texas on H-1B visas, and billed American companies handsomely for the privilege. That pipeline is now running at 60% capacity — and the companies are scrambling to pretend this was the plan all along.

## The Damage in Numbers

India's six largest IT services companies — Tata Consultancy Services, Cognizant, Infosys, HCL Technologies, Wipro, and Tech Mahindra — received a combined 11,041 H-1B visa approvals as of March 31, 2026. That's down 40% from the 18,469 they received the previous year.

The carnage wasn't evenly distributed. TCS, India's largest IT firm by revenue, took the worst hit: its approvals fell by 3,242 to roughly 2,885 — a drop of over 50%. Wipro's approvals cratered by 62%. Tech Mahindra shed 59%.

The lone exception was Infosys. The Bengaluru-based firm secured 3,195 approvals, the highest in the group and the only one to post a year-over-year increase. Infosys has been quietly repositioning itself as a higher-value employer, and the numbers suggest it's working — at least relative to the pack.

## The Triple Squeeze

Three policy shifts are compressing the traditional IT services visa model simultaneously.

First, the $100,000 annual fee per new H-1B worker — signed into effect by Trump in September 2025 — has made entry-level visa deployments economically irrational. An analyst at Anand Rathi Institutional Equities put it plainly: the fee, "coupled with a wage-weighted selection process giving a preference to higher wage talent," acts as "a barrier to entry level jobs, relatively lower pay IT jobs."

Second, USCIS has overhauled its selection criteria. For fiscal year 2027, 71.5% of selected H-1B registrants held a US master's degree or higher — up from 57% the year before. Only 17.7% of selected registrations were in the lowest wage category. The agency called this proof that it was "closing the door on the low-wage and low-skilled foreign labour pipeline."

Third, the new consular processing requirement for green cards means H-1B workers who might have stayed in the US for years while their applications inched forward now face the prospect of returning to India — potentially for years — during the process. That makes long-term visa-dependent workforce planning significantly riskier for employers.

## The Adaptation Playbook

Publicly, the IT firms are treating the contraction as a strategic evolution rather than a crisis. Cognizant's CEO Ravi Kumar has spoken of "significantly reducing dependency on visas, while increasing local hiring and our nearshore capacity." TCS chief K. Krithivasan noted the firm deployed "fewer people than the number of approvals each year" — framing the decline as consistent with a planned trend.

The reality is more complex. Industry analysts expect sub-contractor costs to rise as firms shift more work offshore, with onshore delivery handled by more expensive local hires or third-party sub-contractors. The model that made Indian IT services globally competitive — arbitraging Indian talent costs against American billing rates — is being squeezed from both ends.

Some firms are already pivoting. Google, Amazon, and Microsoft have expanded engineering teams in India through 2026, with one survey showing 25% of major tech firms increasing Indian staff and 20% creating entirely new roles. The irony is hard to miss: the same policy environment making it harder to bring Indians to America is making it more attractive to bring American jobs to India.

## What It Means If You Work at One of These Firms

For the roughly 1.9 million employees at India's top IT companies, the message from Washington is unmistakable: the era of high-volume, mid-tier visa sponsorship is over. The H-1B is being repositioned as a programme for elite hires — people with US advanced degrees commanding six-figure salaries.

If you're an Indian IT services employee with a bachelor's degree and a few years of experience hoping for a US posting, the path just got dramatically narrower. If you're already in the US on an H-1B through one of these firms, your renewal and green card prospects are more uncertain than at any point in the last decade.

The companies will adapt. They always do. The question is whether the individual engineers — the ones who studied for GRE exams, waited for lottery results, and built lives around the promise of an American career — will have that same flexibility."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Big Six IT Firms Lost 40% of Their H-1B Visas. Only Infosys Survived.",
    "subheadline": "TCS approvals cratered by half. Wipro fell 62%. A $100,000 fee, tighter wage rules, and a new preference for US master's degrees are gutting the business model that built Indian IT.",
    "slug": make_slug("indian-it-firms-h1b-approvals-crash-tcs-infosys"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "If you work for TCS, Wipro, HCL, Cognizant, or Tech Mahindra — or were hoping for a US posting through one of them — the visa pipeline that powered Indian IT careers in America for two decades is contracting fast. Infosys is the lone holdout, but the structural shift toward US-educated, high-salary applicants means the traditional path is closing for mid-career engineers.",
    "tags": ["h1b", "tcs", "infosys", "wipro", "indian-it", "uscis", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/companies/it-u-h-1b-visas-green-card-immigration-tcs-infosys-cognizant-green-cards-hiring-11779598845829.html"},
        {"name": "CNBC TV18", "url": "https://www.youtube.com/watch?v=B2dzb6wDrSg"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/h-1b-registrations-down-in-fy27-more-approvals-for-higher-degrees-salaries/article69608747.ece"},
        {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/headlines/3397411-h-1b-registrations-down-in-fy27-more-approvals-for-higher-degrees-salaries"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/31321047/pexels-photo-31321047.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": article2_body,
}


# ─────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
