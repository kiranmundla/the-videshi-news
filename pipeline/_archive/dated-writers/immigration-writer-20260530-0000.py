#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-30 batch"""

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
        "headline": "The Green Card 'Shortcut' That Stopped Working",
        "subheadline": "EB-2 National Interest Waiver denials now exceed EB-1A rejections for the first time — and Indian applicants flooding into both categories are finding neither route as reliable as it once was.",
        "slug": make_slug("niw-denial-rate-surpasses-eb1a-indian-green-card"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For years, Indian engineers and researchers treated the EB-2 NIW as the workaround — a self-petitioned green card that bypassed the employer-dependent PERM process and the decades-long EB-2 India backlog. The reversal in denial rates means that the pathway most Indians considered 'easier' is now statistically harder to win than the EB-1A, which requires extraordinary ability. With EB-1A filings from India surging and approval rates falling, Indian professionals face a narrowing set of viable self-petition options at precisely the moment the H-1B system is contracting around them.",
        "tags": ["niw", "eb-1a", "green-card", "uscis", "indian-immigrants", "self-petition"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Manifest Law — USCIS I-140 RADP Data", "url": "https://manifestlaw.com/blog/immigration/news/eb-2-niw-denials-now-outpace-eb-1a/"},
            {"name": "Boundless — USCIS Q3 2025 EB-1A Data", "url": "https://www.boundless.com/research/uscis-eb-1a-data/"},
            {"name": "AILA — Beyond the H-1B Visa", "url": "https://www.aila.org/"},
            {"name": "USCIS I-140 Summary Tables", "url": "https://www.uscis.gov/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """For a certain generation of Indian software engineers, the EB-2 National Interest Waiver was the quiet exit ramp from immigration purgatory. No employer sponsorship required. No PERM labor certification. No dependence on a company that could lay you off and collapse your entire immigration timeline. You filed a self-petition, argued that your work served the national interest under the three-pronged *Matter of Dhanasar* framework, and waited — but at least the wait was on your own terms.

That calculus just broke.

## The Numbers Nobody Expected

USCIS data for the first quarter of fiscal year 2025 shows something that would have seemed absurd two years ago: EB-2 NIW petitions are now denied more frequently than EB-1A petitions for extraordinary ability.

The denial rate for NIW petitions hit 37.2 percent — more than eight times what it was in fiscal year 2022, when only 4.3 percent of NIW petitions were rejected. Meanwhile, the EB-1A denial rate held at 25.1 percent, roughly in line with its recent historical average.

| Fiscal Year | EB-1A Denial Rate | EB-2 NIW Denial Rate |
|-------------|-------------------|----------------------|
| FY 2022     | 23.2%             | 4.3%                 |
| FY 2023     | 28.6%             | 20.3%                |
| FY 2024 Q4  | 27.7%             | 29.0%                |
| FY 2025 Q1  | 25.1%             | 37.2%                |

The reversal is complete. What began as a gradual convergence has flipped into a full inversion. The category everyone called "easier" is now statistically the harder one to win.

## What Changed

Three forces are compressing NIW approval rates simultaneously.

First, the volume problem. The pandemic-era remote work boom and the growing awareness of NIW among Indian tech professionals created a surge in filings. USCIS received 20,124 EB-2 petitions (the NIW proxy) in Q1 alone, compared to 7,338 for EB-1A. The agency approved only 4,722 of those NIW petitions and denied 2,799 — leaving thousands in limbo with processing backlogs that nearly doubled to 4.3 months of pending cases.

Second, the scrutiny ratchet. Since mid-2022, adjudicators have demanded increasingly granular evidence under *Dhanasar*'s three prongs: that the proposed endeavor has substantial merit and national importance, that the petitioner is well-positioned to advance it, and that the benefit to the United States outweighs requiring a labor certification. Generic claims about "advancing technology" no longer clear the bar. Officers want quantifiable adoption metrics, patent portfolios with demonstrable downstream impact, and letters that go beyond boilerplate affirmations.

Third, the institutional signal. USCIS appears to be recalibrating the NIW as a genuinely selective category rather than a high-volume processing channel. The agency's own data shows it cannot adjudicate cases fast enough — approvals plus denials consistently trail new filings — and tighter standards may be serving as de facto demand management.

## The Indian EB-1A Surge

Indian applicants are reading the data and adjusting. EB-1A filings from India increased sharply over the past year, according to Boundless Immigration Research, even as filings from China — historically the dominant EB-1A origin country — declined by roughly 40 percent.

The shift makes strategic sense. EB-1A offers a faster queue (the EB-1 India final action date currently sits at March 2023, years ahead of EB-2 India at September 2013), allows self-petitioning, and bypasses PERM entirely. For a senior Indian engineer with a strong publication record, patents, or leadership of significant projects, EB-1A may now offer both better odds and a shorter wait.

But the surge comes with its own compression. The overall EB-1A approval rate dropped from 70.5 percent to 60.65 percent over the past year, and Requests for Evidence (RFEs) are becoming routine. More applicants entering the pool means more competition for a finite number of approvals, and USCIS is extending the *Kazarian* two-step test with increasing rigor — first checking whether at least three of the ten regulatory criteria are met, then conducting a "final merits review" of the totality of evidence.

## What This Means for Indian Professionals

The practical takeaway is uncomfortable: neither of the two major self-petition green card routes is a sure thing anymore.

For those considering NIW, the era of filing with a solid resume and a few recommendation letters is over. Successful petitions now require specific, quantifiable evidence of national impact — patents with traceable commercial adoption, open-source projects with measurable community usage, published research with demonstrated policy influence. Immigration attorneys report that the single biggest predictor of NIW denial is vagueness: applicants who describe their work in general terms rather than documenting precise outcomes.

For those pivoting to EB-1A, the standard remains high but the criteria are at least well-defined. The ten-criteria framework rewards applicants who have accumulated visible markers of distinction — awards, media coverage, judging roles, authorship of scholarly articles, evidence of original contributions, high salary relative to peers. The key difference is that EB-1A asks "are you extraordinary?" while NIW asks "does America need you more than it needs the normal hiring process?" The second question, it turns out, is the one USCIS now finds harder to answer favorably.

For Indian professionals currently on H-1B with approved I-140s, the calculus becomes even more complex. The May 21 USCIS policy memo restricting adjustment of status means that even with an approved immigrant petition, the path from I-140 to green card now potentially runs through consular processing abroad — adding months of uncertainty to a timeline that already stretches a decade or more.

The immigration system has never been kind to Indian applicants. It is now becoming actively adversarial to the specific strategies Indian professionals developed to navigate it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The B-2 Bridge Is Collapsing Under Their Feet",
        "subheadline": "Laid-off H-1B workers used to buy time by switching to visitor visas. USCIS is now denying those applications at sharply higher rates — and the 60-day clock keeps ticking.",
        "slug": make_slug("b2-visitor-visa-crackdown-h1b-layoffs-indian-workers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals hold roughly 70 percent of all H-1B visas, making them disproportionately affected by tech layoffs — and disproportionately dependent on fallback strategies like B-2 visitor status changes. The crackdown on B-2 conversions doesn't just affect job-seekers. It threatens entire families: spouses on H-4 visas lose status when the H-1B holder does, children in American schools face mid-semester disruption, and mortgages don't pause because USCIS denied a change-of-status request. For Indians with pending green card applications that have been in the queue for a decade, a denied B-2 conversion can mean abandoning not just a job search but an entire immigration timeline.",
        "tags": ["h1b", "layoffs", "b2-visa", "uscis", "indian-workers", "tech-layoffs", "change-of-status"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Storyboard18 — 60 days or leave?", "url": "https://storyboard18.com/"},
            {"name": "VisaVerge — H-1B Portability & Transfer Rules 2026", "url": "https://visaverge.com/"},
            {"name": "Global India Broadcast News — AI impact on overseas Indians", "url": "https://globalindiabroadcastnews.com/world-news/ai-impact-on-overseas-indians-is-highest-how-h-1b-workers-are-struggling-after-layoffs-at-meta-and-amazon"},
            {"name": "Layoffs.fyi", "url": "https://layoffs.fyi/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6861306/pexels-photo-6861306.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The playbook used to be straightforward, if stressful. You get laid off from your H-1B job. The 60-day grace period starts. You fire off applications, call recruiters, ping every LinkedIn connection who ever mentioned their company was hiring. If the clock runs out before you find a new sponsor, you file for a B-2 change of status — a visitor visa that lets you stay in the country for up to six months while you keep searching.

It was never a guaranteed strategy. But it worked often enough that immigration attorneys described it as the standard fallback for H-1B workers caught between jobs. It was the bridge.

The bridge is now collapsing.

## The RFE Spike

Immigration attorney Rajiv Khanna, one of the most widely cited H-1B practitioners in the country, described the shift bluntly: USCIS is issuing a "significant spike in RFEs and Notices of Intent to Deny" on B-1/B-2 change-of-status applications filed by laid-off H-1B workers.

The Requests for Evidence are not perfunctory. Officers are examining whether the applicant truly intends a temporary visitor stay, has sufficient funds to cover living expenses without employment, maintains a residence abroad, and presents a request that aligns with the stated purpose of admission. A record that looks thin on finances or future plans triggers denial.

The pattern is consistent across multiple attorney accounts. Some officers now question whether job hunting itself constitutes activity appropriate for B-2 status. Others probe whether a later H-1B filing would undercut the claim that the applicant genuinely intended to be a visitor. The legal standard has not changed — attorney Emily Neumann has noted that "the law itself has not changed and job searching is not employment" — but the adjudication climate has shifted materially.

## The Scale of the Problem

The numbers frame the human cost. Layoffs.fyi data shows more than 110,000 employees have lost their jobs at 144 technology companies in 2026 alone. A disproportionate number are Indian H-1B workers: USCIS data shows that Indians accounted for 283,772 of the 406,348 H-1B petitions approved in FY2025 — roughly 70 percent of the total.

When Meta announces that AI-driven restructuring will eliminate thousands of positions and its stock price rises on the news, the human translation is specific. An engineer in Bellevue with a wife on H-4 status and a son in third grade receives a layoff email at 11 PM Bangalore time. His H-1B clock starts. He has 60 days to find a new employer willing to sponsor his visa, switch to another status, or leave the country. If his B-2 application gets denied — as is now happening with increasing frequency — his options narrow to one: departure.

The 60-day grace period, introduced by the Obama administration in 2017, was designed as a humanitarian buffer. It was never designed to absorb the weight of mass layoffs in an industry where Indian nationals constitute the overwhelming majority of visa holders. And it certainly was not designed to function in an environment where the fallback strategy — B-2 conversion — is being actively undermined by the same agency that grants it.

## Why the Crackdown Now

Three factors are converging to make B-2 change-of-status harder for former H-1B holders.

The first is the broader adjustment-of-status policy memo issued by USCIS on May 21. While that memo primarily targets green card applicants, its core philosophy — that staying in the United States while changing immigration categories is a privilege, not a right — is bleeding into B-2 adjudication. Officers are applying a more skeptical lens to any application that seeks to extend a person's presence in the country beyond their original visa category.

The second is volume. When layoffs hit thousands of H-1B workers simultaneously, the USCIS service center handling change-of-status requests sees a corresponding spike. More applications means more scrutiny per application, longer processing times, and a bureaucratic incentive to deny borderline cases rather than issue RFEs and extend adjudication timelines.

The third is political context. The current administration has consistently framed immigration enforcement as a priority. Approving B-2 conversions that effectively extend a foreign worker's stay by six months after their employment ends runs counter to that narrative, even when the applicant's conduct is entirely lawful.

## The Real Options Left

For Indian H-1B workers facing layoffs, the practical landscape is narrowing.

**The H-1B transfer** remains the strongest option — and the most time-sensitive. Under the American Competitiveness in the Twenty-First Century Act (AC21), workers with approved I-140 petitions that have been pending for at least 365 days qualify for one-year H-1B extensions past the normal six-year limit. A transfer to a new employer does not reset that clock, but the worker must confirm the immigrant petition remains valid and has not been withdrawn by the previous employer. Finding a sponsor within 60 days, though, is the challenge — especially when companies are cutting headcount, not adding it.

**The O-1 visa** works for a narrow subset: applicants who can demonstrate extraordinary ability in their field. Approval rates remain above 90 percent, making it one of the most reliable categories — for those who qualify. The evidentiary bar is high, but Indian engineers with strong publication records, patents, or significant open-source contributions may find it viable.

**The B-2 conversion**, while legally available, now carries enough denial risk that attorneys are advising clients to treat it as a last resort rather than a first move. If you file, bring comprehensive financial documentation, a clear itinerary that looks like a genuine visit rather than extended residence, and evidence of ties to India.

**The dependent visa** — switching to H-4 if your spouse holds an H-1B — remains an option for some families, though it restricts employment to those with H-4 EAD authorization, a benefit that is itself under regulatory threat.

**Departure and return** is increasingly what remains when every other door closes. For families who have spent a decade building lives in the United States — children in American schools, equity in American homes, friendships and professional networks rooted in American cities — the suggestion to "just go back" carries a weight that no policy memo adequately captures.

The system was never designed to protect the people it invited in. But it used to at least leave them a bridge to cross while they figured out their next step. That bridge is getting shorter every month."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
