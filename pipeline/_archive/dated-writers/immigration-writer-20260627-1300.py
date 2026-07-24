#!/usr/bin/env python3
"""Immigration writer — 2026-06-27 13:00 PT run."""

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


# ── ARTICLE 1 ─────────────────────────────────────────────────────────────
article1_body = """Australia was never supposed to be the answer. For decades, Indian engineers, developers, and data scientists pointed their careers at one destination: the United States. The H-1B visa was the ticket, Silicon Valley was the stage, and a green card was the endgame — however distant.

Then America started charging $100,000 just to file the paperwork. It weighted the H-1B lottery by salary, froze consular appointments for months, and proposed killing OPT. And while Washington was busy raising the drawbridge, Canberra quietly rolled out the welcome mat.

The numbers are startling. According to Deel's 2026 Global Talent Map, Indian nationals active on its platform in Australia surged **724 percent year-over-year** — dwarfing the 142 percent growth in the UK, 139 percent in the US, and 131 percent in Ireland. The data suggests not a trickle of adventurous expats, but a genuine redistribution of the global Indian tech workforce.

"Since the United States restricted its H-1B visa, Australia has attracted a greater share of skilled Indian workers, while hiring of Indian workers has noticeably declined in the US and Canada," said Lauren Thomas, economist at Deel. Half of US-based employees working in AI roles at top VC-funded startups on the platform are foreign nationals — the demand hasn't changed, but where it's being met has.

## Why Australia, specifically

The appeal is structural, not sentimental. Australia's points-based immigration system — Subclass 189 (independent skilled), 190 (state-nominated), and 491 (regional) — offers something the US green card queue never could: a timeline. An Indian software engineer with strong English scores, relevant experience, and a willingness to consider regional cities can receive a permanent residency invitation within months, not decades.

The Australia-India Economic Cooperation and Trade Agreement (AI-ECTA) sweetens the deal further, granting special post-study work arrangements for eligible Indian graduates — a bilateral perk that has no equivalent in the US relationship.

And the salaries are not trivial. Senior software engineers in Australia command AUD 130,000 to AUD 180,000 annually (roughly $85,000 to $118,000), with AI and cybersecurity specialists crossing AUD 200,000. Factor in the 38-hour work week, universal healthcare, and the absence of a green card Sword of Damocles, and the calculus starts to shift.

## But July 1 changes the math

Starting July 1, 2026, Australia's employer-sponsored visa salary thresholds will rise from AUD 76,515 to AUD 79,499 for Core Skills occupations. Specialist Skills thresholds will climb higher still. The increase is modest — roughly 4 percent — but it narrows the pool of eligible positions and puts pressure on employers to justify every sponsorship.

For Indian workers eyeing the 482 Skills in Demand visa as an entry point, the message is clear: apply before the threshold rises, or bring a salary offer that clears the new bar. Existing 482 holders with approved nominations before July 1 are grandfathered, but anyone changing employers afterward will face the new requirements.

## The bigger picture

India is now the world's largest exporter of high-skilled talent, dominating the H-1B in the US, the Skilled Worker programme in the UK, the EU Blue Card in Germany, and the Golden Visa in the UAE. Deel's data shows Indian nationals are the top work-visa nationality in Singapore and rank first or second in virtually every major skilled migration programme on the planet.

Germany, for its part, has issued nearly a third of its Opportunity Card permits to Indians and now employs 137,000 Indian professionals in skilled positions — up from 23,000 in 2015. The country even allows IT specialists to obtain an EU Blue Card without a university degree, provided they have three years of experience and meet a salary threshold of €45,630.

For the Indian professional stuck in a 15-year EB-2 backlog, paying a $100,000 filing fee, and watching consular wait times balloon past four months, these alternatives are no longer theoretical. They are the plan.

The question is whether Washington notices before the talent pipeline redirects permanently — or whether it already has, and simply doesn't care."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Australia Became the Surprise Winner of America's H-1B Crackdown",
    "subheadline": "Indian tech talent on Deel's platform in Australia surged 724 percent in a single year. The US wasn't the only country that noticed.",
    "slug": make_slug("australia-724-percent-indian-tech-talent-surge-h1b-spillover"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "For Indians exhausted by the H-1B lottery and EB-2 backlog, Australia's points-based PR pathway now offers a timeline measured in months rather than decades.",
    "tags": ["h1b", "australia", "immigration", "skilled-migration", "tech-talent", "deel"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "CFOtech Australia", "url": "https://cfotech.com.au/story/australia-draws-indian-tech-workers-after-us-visa-curbs"},
        {"name": "CXOToday", "url": "https://cxotoday.com/press-release/deel-india-dominates-global-visa-programs-as-worlds-1-exporter-of-high-skilled-talent/"},
        {"name": "Deel Global Talent Map Report 2026", "url": "https://www.deel.com/resources/global-talent-map"},
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Skyline_of_Sydney_CBD%2C_Sydney_Harbour_Bridge%2C_2023.jpg/1280px-Skyline_of_Sydney_CBD%2C_Sydney_Harbour_Bridge%2C_2023.jpg",
    "image_caption": "Sydney CBD skyline and Harbour Bridge, 2023",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip(),
}

# ── ARTICLE 2 ─────────────────────────────────────────────────────────────
article2_body = """Homeland Security Secretary Markwayne Mullin walked into a House Appropriations subcommittee hearing on June 26 and made a promise that would have sounded absurd five years ago: the federal government would process your immigration application using artificial intelligence, and the first system would go live within 30 days.

"We're building systems in right now to be able to do that through an automated system," Mullin told lawmakers. "We're going to deploy the first one in 30 days."

The initial rollout will target the Deferred Action for Childhood Arrivals (DACA) programme, which has accumulated a substantial backlog. But Mullin's ambitions stretch far wider. DHS is also developing a mobile application — briefed to and approved by the president — that would let applicants submit immigration paperwork from their phones with built-in error prevention.

"Why can't we move this to a system that you can't submit the paperwork until it is filled out correctly?" Mullin asked, rhetorically. "The technology is there, we just have to adapt it."

## The problem it's meant to solve

USCIS is drowning. The agency is managing over **11 million pending cases** as of early 2026 — the largest backlog in its history. Employment-based adjustment of status (Form I-485) takes 9 to 35 months. Regular I-140 immigrant worker petitions range from 2.5 to 25.5 months. Even premium processing, which costs $2,965 as of March 2026, only guarantees a decision within 45 calendar days — and that clock doesn't start until "all prerequisites for adjudication" are received.

For Indian nationals, the wait is compounded by per-country limits that stretch EB-2 green card processing beyond 15 years and EB-3 into similar territory. The July 2026 Visa Bulletin showed EB-2 India as "unavailable" — meaning no new cases are being processed at all. Every additional day of USCIS processing delay compounds a system already engineered to make Indians wait longest.

## What AI could actually do

Immigration attorneys see two potential uses. The first is triage: AI could flag incomplete or improperly formatted applications before they enter the queue, reducing the Requests for Evidence (RFEs) that currently bounce thousands of petitions back to applicants and restart processing clocks. USCIS has been issuing RFEs at elevated rates, and each one can add months to an already glacial timeline.

The second is pattern recognition. AI systems trained on historical adjudication data could identify straightforward cases — routine H-1B extensions, EAD renewals, standard I-140 petitions — and route them to expedited processing, freeing human officers for complex or contested filings.

Mullin pointed to early success with H-2A agricultural worker visas, where processing times have already improved under modernisation efforts. But H-2A is a vastly simpler programme than the multi-layered employment-based system that most Indian applicants navigate.

## The sceptics have a point

Immigration lawyers are cautiously optimistic — emphasis on cautiously. USCIS has attempted digital modernisation before. The agency's online filing system remains clunky and incomplete; many forms still require paper filing. The myUSCIS portal, launched with similar fanfare, has been plagued by outages and limited functionality.

More fundamentally, the bottleneck for Indian applicants is not processing speed but visa number availability. No amount of AI can conjure additional EB-2 India visa numbers from a system that caps every country at 7 percent of annual employment-based visas, regardless of demand. An Indian engineer and a Luxembourgish one get the same allocation — a structural absurdity that no algorithm can fix.

There are also due-process concerns. AI-assisted adjudication of asylum claims, for instance, raises questions about whether applicants receive meaningful human review. DHS has already begun using AI for fraud detection and background screening; extending it to adjudication decisions moves into less tested territory.

## What it means for the diaspora

If the AI platform works as advertised — and that remains a substantial "if" — the most immediate beneficiaries would be applicants stuck in the RFE loop or waiting for routine approvals on forms that should never have taken months. EAD renewals, I-140 approvals, and H-1B extensions could theoretically see compressed timelines.

But the Indian green card backlog, the per-country caps, and the structural shortage of visa numbers are legislative problems, not technological ones. Mullin's AI can speed up the queue. It cannot shorten the line.

For the 1.8 million Indians with pending employment-based petitions, the honest answer remains what it has always been: Congress is the bottleneck, and Congress is not in a hurry."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "DHS Says It Will Process Your Visa With AI in 30 Days. Immigration Lawyers Have Questions",
    "subheadline": "Homeland Security Secretary Mullin unveiled an AI overhaul of immigration processing and a mobile app for applicants. The 11-million-case backlog is listening.",
    "slug": make_slug("dhs-ai-visa-processing-overhaul-mobile-app-uscis-backlog"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "AI-assisted processing could speed up routine H-1B and EAD approvals for Indian applicants, but it cannot fix the per-country visa caps and EB-2 backlog that are legislative, not technological, problems.",
    "tags": ["uscis", "ai", "immigration", "processing-times", "backlog", "technology"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "IANS", "url": "https://ianslive.in/news/us-plans-ai-push-for-visa-processing-20260626"},
        {"name": "Nolo - 2026 Immigration Legal Updates", "url": "https://www.nolo.com/legal-updates/2026-immigration-legal-updates"},
        {"name": "Manifest Law - USCIS Processing Times June 2026", "url": "https://manifestlaw.com/uscis-processing-times/"},
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in New York",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip(),
}

# ── INSERT ─────────────────────────────────────────────────────────────────
articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
