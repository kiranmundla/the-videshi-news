#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-25 04:00 UTC run"""
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
        "headline": "Your Instagram Is Now a Visa Requirement — The Quiet Expansion of America's Social Media Dragnet",
        "subheadline": "Since March 30, all H-1B, H-4, and 13 other nonimmigrant visa categories require applicants to make social media profiles public for State Department screening. Here's what Indian applicants need to know.",
        "slug": make_slug("social-media-visa-screening-h1b-indian-applicants"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders and their H-4 dependent spouses now face social media scrutiny during visa stamping and renewals. With hundreds of thousands of Indians traveling to consulates in India, Canada, and Mexico for visa stamps each year, this policy change adds a new layer of anxiety to an already stressful process. Any old social media post — a political opinion, a joke, a reshared meme — could theoretically flag an application.",
        "tags": ["h1b", "social-media-screening", "visa-stamping", "h4", "ds-160", "uscis"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Phillips Lytle LLP", "url": "https://phillipslytle.com"},
            {"name": "Travel And Tour World", "url": "https://travelandtourworld.com"},
            {"name": "VisaVerge", "url": "https://visaverge.com"},
            {"name": "American Bazaar", "url": "https://americanbazaaronline.com"},
            {"name": "U.S. Department of State", "url": "https://state.gov"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/607812/pexels-photo-607812.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On March 30, 2026, the U.S. Department of State quietly flipped a switch that affects virtually every Indian professional, student, and dependent seeking to enter or remain in the United States. Applicants for 15 nonimmigrant visa categories — including H-1B, H-4, L-1, O-1, and several others — must now make their social media accounts public so consular officers can review them before issuing a visa.

The policy isn't new in concept. Student visa applicants (F, M, and J categories) have faced social media screening since mid-2025, when the State Department first began requiring public profiles and expanded its vetting infrastructure. What changed in March is the scope: it now covers the workhorses of the Indian immigration pipeline, the H-1B and its dependent H-4 visa.

## What the Policy Actually Requires

During the DS-160 application process, applicants must declare every social media account they've used in the past five years. The State Department's guidance instructs consular officers to review public posts for content that suggests "support for terrorism," "hostility toward U.S. institutions," ties to illegal activity, or antisemitic rhetoric — categories that are broad enough to invite subjective interpretation.

Applicants who keep their accounts private may face processing delays. Those who fail to disclose an account risk outright denial.

The law firm Phillips Lytle, which advises corporate immigration clients, noted in a March advisory that the policy "grants consular officers significant latitude in evaluating subjective online content" and cautioned that "the lack of clear, uniform standards creates inconsistency across posts." That is diplomatic language for: your visa outcome may depend on which officer reads your timeline.

## The Indian Calculus

For the estimated 730,000 H-1B holders in the United States — a population disproportionately Indian — this matters every time they travel internationally and need a visa stamp. India's U.S. consulates in Mumbai, Chennai, Hyderabad, Delhi, and Kolkata already have wait times that stretch months. Now add the processing overhead of officers scrolling through years of Instagram posts and LinkedIn activity.

H-4 dependent spouses, the vast majority of whom are Indian women, face the same screening — for a visa that doesn't even grant work authorization without a separate EAD application that is itself politically embattled.

The timing compounds the stress. The $100,000 fee on new H-1B petitions, the shift from a random lottery to a wage-weighted selection process, and the recent USCIS memo restricting adjustment of status have already made the Indian professional's immigration calculus considerably grimmer. Social media screening is one more friction point layered onto a system already straining under policy whiplash.

## What Officers Are Looking For (and What They're Not Telling You)

The State Department has been deliberately vague about implementation. Officers are directed to check for "threats to U.S. national security" and content inconsistent with the stated purpose of the visa. A cable sent to embassies and consulates in early 2026 reportedly provides additional internal guidance, but the department has not made those standards public.

Immigration attorneys who advise Indian clients say the practical risk isn't a single inflammatory post — it's the ambiguity. A political opinion that reads as mainstream in India might register differently with an American officer unfamiliar with the context. A reshared news article about Kashmir or a meme about American politics could, in theory, be flagged.

"The problem isn't that they're checking social media," said one Bay Area immigration attorney who advises tech workers. "The problem is that nobody knows where the line is."

## The Student Pipeline Is Already Feeling It

The expansion to work visas follows what happened to students. After the State Department ordered embassies to halt new student visa interviews last year to prepare for social media vetting, the effects were measurable. A Brookings Institution analysis published on May 21 projected a 29% decline in new F-1 visa issuances for 2025. Indian and Chinese students, who together receive 43% of all F-1 visas, bore the brunt.

The concern now is whether the same chilling effect will ripple through the work visa pipeline. H-1B registrations for FY2027 already dropped 38.5% — from 343,981 to 211,600 — driven primarily by the new $100,000 fee and the weighted lottery. Social media screening adds another deterrent, particularly for applicants who might otherwise have considered the process merely bureaucratic rather than invasive.

## What Indian Applicants Should Do

Immigration lawyers advising Indian clients recommend a few practical steps. First, audit your social media history — not to delete posts (which could itself raise flags if detected), but to understand what's publicly visible. Second, ensure every account you've ever used is disclosed on the DS-160; undisclosed accounts are a bigger problem than any single post. Third, set expectations: processing times for stamping appointments may stretch further as consular sections adjust to the new screening workload.

The policy is unlikely to be reversed under the current administration. The question now is whether it will deter talent from coming — or simply make their journey more unpleasant.

For the Indian professional community in the U.S., the answer is probably both."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "627,000 Indians Stuck, a 29% Student Visa Crash, and a $100K Fee — Brookings Maps the Full Damage to America's Talent Pipeline",
        "subheadline": "A comprehensive Brookings Institution analysis reveals the Trump administration has simultaneously attacked every segment of the high-skill immigration system. The numbers paint a picture that should alarm every Indian in the green card queue.",
        "slug": make_slug("brookings-talent-pipeline-report-indian-immigration"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India accounts for roughly half of the 1.2 million green card backlog — an estimated 627,000 Indians and their families waiting in a queue that effectively doesn't move. The Brookings report documents how every rung of the ladder — from student visas to OPT to H-1B to green card — is being simultaneously restricted, leaving Indian professionals with fewer options and longer waits than at any point in modern immigration history.",
        "tags": ["green-card-backlog", "h1b", "f1-visa", "brookings", "opt", "talent-pipeline", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
            {"name": "USCIS", "url": "https://www.uscis.gov"},
            {"name": "NAFSA", "url": "https://www.nafsa.org"},
            {"name": "Cato Institute", "url": "https://www.cato.org"},
            {"name": "Gulte", "url": "https://www.gulte.com/overseas/412452/tough-times-ahead-for-h-1b-hopefuls"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7683629/pexels-photo-7683629.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On May 21, Brookings published what may be the most complete accounting yet of what the Trump administration has done to America's high-skill immigration system. The 28-minute read, authored by Tara Watson's team at the Center for Economic Security and Opportunity, doesn't cherry-pick a single policy to be outraged about. It maps the entire pipeline — from the first F-1 visa application to the final green card — and shows how each segment is being squeezed simultaneously.

For Indians, who dominate nearly every stage of this pipeline, the report reads less like policy analysis and more like a damage assessment.

## The Numbers

Start with the scale. Brookings estimates approximately 1.2 million immigrants and their families are trapped in the green card backlog. Of those, roughly 627,000 were born in India. That's not a queue — it's a demographic held in indefinite suspension, with EB-2 and EB-3 priority dates that haven't meaningfully advanced in years.

The 140,000 annual cap on employment-based green cards hasn't changed since 1990. The 7% per-country ceiling means India, which generates enormous demand for EB visas, is allocated the same number as countries that file a handful of applications each year. Spouses and children count against the cap too, so only about half of those 140,000 visas go to actual workers.

## The Student Visa Collapse

The pipeline starts bleeding at the very top. Brookings projects a 29% decline in new F-1 visa issuances for 2025, based on reported data through the first eight months of the calendar year. Indian and Chinese students — who together account for 43% of all F-1 visas — are the most affected.

The causes are layered. The administration's travel ban blocked new nonimmigrant visas for 38 countries. DHS proposed capping F-1 stays at four years, which would gut doctoral programs. The State Department halted new student visa interviews to implement social media screening. And then there were the SEVIS terminations — 1,800 students had their immigration status revoked without warning, often for minor infractions or political speech.

NAFSA estimates that the 17% decline in international student enrollment during fall 2025 cost the U.S. economy $1.1 billion and 23,000 jobs. California and New York face the largest losses.

## OPT Under Threat

After graduation, 72% of international students use Optional Practical Training to work in the U.S. for 12 months (36 months for STEM graduates) while seeking longer-term visa sponsorship. OPT is the bridge between studying and working — and USCIS Director Joseph Edlow has indicated he wants to effectively end it.

Former DHS Secretary Kristi Noem told Congress that her department was "reevaluating whether the current regulatory framework — including the scope and duration of practical training — appropriately serves U.S. labor market, tax, and national security interests." That kind of language typically precedes a rulemaking. If OPT disappears or shrinks, the pipeline from F-1 to H-1B breaks entirely.

For Indian STEM graduates — who constitute a significant share of OPT participants — this is existential. Many rely on the three-year STEM OPT window to secure H-1B sponsorship. Without it, they'd need to leave the country upon graduation.

## The H-1B Squeeze

The Brookings report documents three simultaneous restrictions on H-1B:

**The $100,000 fee.** Announced in September, it applies to new H-1B petitions (renewals and status changes are exempt). Only about 85 companies have paid it so far. Legal challenges are pending, including one from the U.S. Chamber of Commerce. The fee is designed to eliminate "low-wage registrations," but its actual effect is to make sponsoring mid-career and early-career workers prohibitively expensive.

**The weighted lottery.** Since February 27, the H-1B lottery is no longer random. It now weights selection toward higher-salaried applicants. FY2027 data shows the result: 71.5% of selected registrants hold a U.S. master's degree or higher, up from 57% the previous year. Good for senior hires. Devastating for entry-level workers and anyone whose field doesn't pay top-quintile salaries.

**The registration plunge.** H-1B registrations fell 38.5%, from 343,981 in FY2026 to 211,600 in FY2027. USCIS spun this as proof that "the days of abusing the program with mass, low-wage registrations are over." That framing ignores the most obvious explanation: companies and workers are self-selecting out of a system that has become too expensive and unpredictable to navigate.

Despite this, H-1B demand still exceeds supply — the cap was hit within 25 days of the FY2027 application opening.

## The Competitors Are Paying Attention

While Washington restricts, other countries recruit. China launched its K-visa — a direct equivalent of the H-1B — in late 2025, paired with active campaigns to attract foreign STEM talent. Canada and Germany have expanded their skilled worker programs. Research cited in the Brookings report shows that American H-1B restrictions lead directly to increased offshoring to India, China, and Canada by multinational corporations.

This is the part that should worry Indian professionals who plan to stay. The question isn't just whether America will let you in — it's whether the economic engine that makes American salaries and career opportunities worth the immigration hassle will still be running at full speed once the talent starts flowing elsewhere.

## What This Means for Indians in the Queue

The Brookings report doesn't offer solutions. Its purpose is to document the erosion, and it does so with data that is difficult to argue with. The takeaway for Indian immigrants is stark: every rung of the ladder is being pulled away simultaneously. Students face fewer visa slots and social media screening. Graduates may lose OPT. Workers face a $100,000 fee and a lottery rigged toward higher salaries. And at the end of it all, 627,000 Indians wait for a green card under a per-country cap that hasn't been updated in 36 years.

The Cato Institute estimates that college-educated immigrants paid $8.8 trillion more in taxes than they received in benefits between 1994 and 2023. The Social Security Trustees Report shows that high immigration scenarios reduce the program's long-term deficit by 26%. The economic case for high-skill immigration isn't debatable. The political will to act on it is another matter entirely.

For now, the pipeline narrows. And the people most affected are overwhelmingly Indian."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
