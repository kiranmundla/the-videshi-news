#!/usr/bin/env python3
"""Immigration writer — 2026-06-26 21:00 PDT run."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── ARTICLE 1 ──────────────────────────────────────────────────────────
article1_body = """The National Interest Waiver was supposed to be the clever play. While the EB-2 employment-based green card line for India stretched past a decade—and EB-3 wasn't much better—a growing number of Indian tech professionals discovered they could sidestep the queue entirely. File an EB-2 NIW, petition on your own behalf, skip the labour certification, skip the employer dependency. For a few triumphant years, it worked spectacularly.

It no longer does—at least, not reliably.

USCIS adjudication data through Q4 of fiscal year 2025, the most recent available, paints a picture that should alarm anyone who assumed self-petition was still a safe bet. The EB-2 NIW approval rate has cratered from roughly 96% in FY2022 to 55.2% for full-year FY2025. The fourth-quarter figure alone was 35.7%—meaning nearly two out of every three petitions filed in that window were denied.

The EB-1A Extraordinary Ability category, the other major self-petition route, held up somewhat better at 66.9% for the full year. But even that slipped to roughly 53% in Q4. The O-1 nonimmigrant visa for extraordinary ability, by contrast, remained above 90% throughout the year—a reminder that temporary status is, paradoxically, more reliably obtainable than permanent residence.

## What Changed

The framework hasn't changed. The *Matter of Dhanasar* test for NIW—that the proposed endeavour has substantial merit, the petitioner is well-positioned to advance it, and on balance it would benefit the United States to waive the labour certification requirement—remains the governing standard. What has changed is how rigorously USCIS officers apply it.

Adjudicators are placing far greater weight on measurable, demonstrated US impact rather than forward-looking potential. Broad claims about advancing a field or working in an important sector no longer suffice. Officers want concrete evidence: adoption of your work by others, deployment at scale, government or industry uptake, verifiable metrics. A recommendation letter that praises your "outstanding contributions" without citing a single specific outcome is, increasingly, dead weight.

The shift is particularly punishing for a profile common among Indian applicants: mid-career software engineers at large tech companies whose work is excellent but organisationally contained. Building an internal tool used by your team at Google does not, under current adjudication practice, demonstrate national-level impact, no matter how technically impressive the tool is.

## The Volume Problem

Part of the squeeze is arithmetic. As the EB-2 India backlog grew more punishing—the July 2026 Visa Bulletin famously marked EB-2 India as "Unavailable"—more applicants pivoted to NIW and EB-1A as alternatives. EB-1A petition filings rose approximately 50% year-over-year in FY2025, according to data compiled by Boundless Immigration. The EB-1A backlog hit 16,000 pending cases, an all-time high.

More filings mean more pressure on a fixed number of adjudicators, longer processing times, and—inevitably—stricter gatekeeping. USCIS has responded with a surge in Requests for Evidence and Notices of Intent to Deny, which keep cases open for months while petitioners scramble to supplement their records.

## A Crack in the Wall

One legal development offers a sliver of hope. In *Mukherji v. Miller* (D. Neb. Jan. 28, 2026), a federal district court questioned whether USCIS properly adopted its two-step "final merits" framework for EB-1A and ordered a petition approved after the agency conceded the petitioner met five of the ten regulatory criteria. The decision is limited to that case and USCIS has not changed its guidance, but immigration attorneys say it provides an additional argument where a strong record has been denied on vague or conclusory reasoning.

## What This Means for Indian Applicants

The practical implications are blunt. NIW is no longer a reliable backdoor around the green-card backlog. It remains a viable pathway for professionals with genuinely demonstrable national-level impact—healthcare workers addressing shortages, AI researchers whose models are deployed across industry, engineers whose open-source contributions are widely adopted. But for the much larger group of competent professionals doing solid work inside a single company, the approval odds have shifted decisively against them.

Immigration attorneys now advise concurrent filings: pursue both EB-1A and NIW simultaneously, and maintain a PERM-based EB-2 or EB-3 case as a parallel track. The logic is simple—with approval rates this volatile, betting on a single category is a gamble most families cannot afford to lose.

The self-petition escape hatch hasn't closed entirely. But the lock is being changed, and fewer keys fit."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Self-Petition Escape Hatch Is Closing. NIW Approvals Just Hit Their Lowest Rate on Record",
    "subheadline": "EB-2 National Interest Waiver approval rates fell from 96% to 35.7% in three years. For Indian tech workers treating it as a backdoor around the green-card backlog, the math just changed.",
    "slug": make_slug("niw-eb1a-approval-rate-record-low-indian-tech-self-petition"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian tech professionals have increasingly turned to NIW and EB-1A self-petitions to circumvent the decade-plus EB-2 India green card backlog, but crashing approval rates mean this escape route is no longer a safe bet.",
    "tags": ["niw", "eb-1a", "green-card", "uscis", "self-petition", "backlog"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "LexBlog — Immigration Law Analysis", "url": "https://www.lexblog.com/2026/06/11/what-recent-uscis-data-means-for-eb-2-niw-eb-1a-petitioners/"},
        {"name": "Boundless Immigration", "url": "https://www.boundless.com/research/uscis-q3-2025-data-eb1a-filings/"},
        {"name": "Manifest Law", "url": "https://manifestlaw.com/eb-2-niw-denials-outpace-eb-1a/"},
        {"name": "Stelmakh & Associates", "url": "https://stelmakhlaw.com/eb-1a-eb-2-niw-approval-rate-declines/"},
        {"name": "USCIS I-140 Adjudication Data", "url": "https://www.uscis.gov/tools/reports-and-studies/immigration-and-citizenship-data"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in Queens, New York",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}

# ── ARTICLE 2 ──────────────────────────────────────────────────────────
article2_body = """Oracle had its most profitable year in history. Revenue hit $67 billion for the fiscal year ending May 2026, driven by a ravenous appetite for cloud infrastructure and artificial intelligence. Profits were sharply up. The stock, before the layoff news, was a darling of the AI trade.

Then the company filed its annual 10-K with the Securities and Exchange Commission on June 22 and dropped a line that no major American technology company had put in writing before: "The adoption and deployment of AI technologies across our operations have resulted, and may continue to result, in reductions to our workforce."

Twenty-one thousand people lost their jobs over the past twelve months. Oracle's full-time headcount fell from roughly 162,000 to 141,000—a 13% reduction. Severance and restructuring costs ballooned to $1.84 billion, nearly five times the $374 million spent the year before. This was not a trimming. It was an amputation carried out during a banner year.

## The Indian Dimension

Of those 21,000 cuts, an estimated 12,000 hit Oracle's Indian operations—its development centres in Bengaluru, Hyderabad, and Pune. The All India IT and ITES Employees' Union called the terminations "forceful and illegal retrenchment." Affected employees in India were offered an N+2 severance formula, where N is years of service paid out in months, with unvested stock units reportedly forfeited on termination.

The pain extends further. Oracle has also been rescinding offer letters issued to prospective employees at engineering colleges across India, effectively slamming the door on a cohort that had already planned their careers around a seat at the company.

For Indians working at Oracle in the United States on H-1B visas, the calculus is more desperate. A layoff triggers a 60-day grace period—sixty days to find a new employer willing to sponsor and file an H-1B transfer, or face the prospect of leaving the country. For workers mid-stream in the green card process, a layoff can reset years of PERM labour certification progress. An approved I-140 petition offers some protection, but an unapproved one evaporates with the job.

## The AI Admission

What distinguishes Oracle's filing is the candour. Technology companies have been shedding tens of thousands of workers since 2023—over 40,480 tech jobs cut across more than 70 companies in 2026 alone, according to Layoffs.fyi—but the standard explanation has been "restructuring," "realignment," or the vague corporate favourite, "increased efficiency." Oracle named the machine.

The Oracle Health division, built on the $28.3 billion Cerner acquisition, bore the brunt. Between 8,000 and 10,000 of the cuts came from that unit as the company consolidated redundant functions and replaced manual workflows with automated systems. But the language in the 10-K was broader than any single division. It was a statement about the direction of the company, and implicitly, the industry.

AI capital expenditure at Oracle surged 162% to $55.7 billion. The company is simultaneously its own largest customer for AI automation and a cautionary exhibit for everyone who works there.

## The H-1B Paradox

The optics are not lost on anyone watching. Even as Oracle eliminated 21,000 roles, the company filed roughly 3,126 H-1B visa petitions across fiscal years 2025 and 2026, including 436 in fiscal 2026 alone, according to USCIS disclosure data and an analysis published on Medium. Immigration attorneys caution that the timing of layoffs and visa petitions often reflects different budgets, different teams, and different business units—the world rarely divides into a clean narrative of "fired Americans, hired foreigners." But the aggregate picture is jarring, and it feeds a political environment already hostile to the H-1B programme.

For Indian professionals in the US tech sector, the Oracle episode crystallises a set of uncomfortable truths: record corporate profits do not guarantee job security; AI displacement is no longer speculative; the 60-day H-1B grace period is dangerously short for a job market this tight; and the green card backlog transforms every layoff from a career setback into an existential one.

## What Comes Next

The Oracle filing is likely a template, not an outlier. As more companies adopt AI across operations—and as SEC disclosure requirements make it harder to euphemise the consequences—other 10-K filings will contain similar language. The question for Indian tech workers, whether in Hyderabad or Hillsboro, is whether the ecosystem they built their careers in still has room for the humans who made it possible."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Oracle Made $67 Billion. Then It Cut 21,000 Workers and Blamed the Machine",
    "subheadline": "The tech giant's SEC filing is the first from a major US company to formally attribute mass layoffs to AI adoption. For Indians on both sides of the Pacific, it is a double hit.",
    "slug": make_slug("oracle-21000-layoffs-ai-sec-filing-indian-h1b-workers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "An estimated 12,000 of Oracle's 21,000 job cuts hit Indian operations, while H-1B holders at Oracle in the US face the 60-day grace period with green card processes at risk of resetting.",
    "tags": ["oracle", "layoffs", "ai", "h1b", "tech-workers", "india"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The People's Board", "url": "https://thepeoplesboard.com/oracle-cuts-21000-jobs-names-ai-as-a-cause/"},
        {"name": "Gulte", "url": "https://gulte.com/this-is-huge-oracle-fires-21000-employees-in-one-year/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/oracle-begins-layoffs-affecting-thousands-cnbc-reports-2026-04-01/"},
        {"name": "Mike McNelis (Medium)", "url": "https://medium.com/@mikemcnelis/oracle-fired-30000-people-with-a-6-am-email-then-filed-3126-foreign-worker-visa-petitions"},
        {"name": "American Bazaar Online", "url": "https://americanbazaaronline.com/social-media-speculates-oracle-layoffs-may-be-linked-to-h1b-hiring/"},
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Oracle_HQ_Foster_City_Homes_%2828195324%29.jpg/1280px-Oracle_HQ_Foster_City_Homes_%2828195324%29.jpg",
    "image_caption": "Oracle headquarters campus in Foster City, California",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}

# ── INSERT ─────────────────────────────────────────────────────────────
articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
