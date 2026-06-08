#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-08 00:00 UTC run"""
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

# ────────────────────────────────────────────────────────────
# Article 1: AI Is Now the #1 Reason for Job Cuts in America
# ────────────────────────────────────────────────────────────

art1_body = """AI has overtaken every other excuse American employers use to fire people.

In May, companies cited artificial intelligence as the reason behind 38,579 job cuts — the highest monthly figure since outplacement firm Challenger, Gray & Christmas began tracking AI-related layoffs in 2023. For the third consecutive month, automation topped the layoff ledger. And the year-to-date total, 87,714 AI-attributed cuts through May, has already surpassed the combined figure for all of 2024 and 2025.

"AI is now the leading reason companies give for cutting jobs," Andy Challenger, the firm's Chief Revenue Officer, said in the report. "The open question isn't whether AI changes the workforce, but how fast."

## The Numbers Are Getting Loud

The trajectory is hard to ignore. AI accounted for just 7% of announced layoffs in January. By February, it was 10%. March: 25%. April: 26%. In May, it reached nearly 40% of all announced cuts.

Total US employer-announced layoffs hit 97,000 in May, a 16% jump from April and the highest May figure since the pandemic bloodbath of 2020. The technology sector led the carnage, with 38,242 job cuts — its steepest month since August 2024. Year-to-date, tech has shed 123,653 positions, a 66% increase over the same window in 2025. Meta alone axed 8,000 workers, framing the move as an AI pivot.

Yet some observers are skeptical. OpenAI's own Sam Altman accused certain companies of "AI washing" their layoffs — using the technology as a convenient narrative for what amounts to routine cost-cutting or correcting post-pandemic over-hiring. Torsten Sløk of Apollo Global Management found zero evidence of AI-driven displacement in broader payroll data. ADP figures and other labour indicators show no clear aggregate job losses yet.

## What Indian Tech Workers Should Actually Worry About

The macro debate is interesting. The H-1B math is urgent.

Indian nationals hold roughly 73% of all H-1B visas approved in recent years, and the overwhelming majority work in the technology sector — at precisely the companies now leading AI-related restructuring. When an H-1B holder loses their job, they have 60 days to find a new employer willing to sponsor them, or they must leave the country. Sixty days is not a long time when 164 companies have collectively shed over 116,000 positions in 2026.

The pressure is compounding. Companies are not just eliminating roles — they are quietly freezing the entry-level pipeline. Fewer junior positions mean fewer visa petitions. Analysts at CBS News noted in late May that the biggest labour-market impact of AI may not be in layoffs at all, but in the jobs that simply never get posted.

For an Indian engineer at a Bay Area company, the calculus has shifted. The question is no longer whether your employer is "AI-first." It is whether your employer's definition of AI-first still includes you.

## The Paradox Nobody Mentions

The same Challenger report that flagged tech as the biggest job-cutter also named it the biggest job-creator. Technology companies announced 11,000 new positions in May, more than any other sector. The unemployment rate remains steady at 4.3%.

What is happening is not a collapse. It is a reshuffle. Companies are dismantling the workforce that built their pre-AI products and rebuilding one calibrated for a different architecture. The roles being created — AI infrastructure engineers, prompt engineers, machine learning operations specialists — demand different skills than the ones being eliminated.

For the Indian diaspora, this creates a twin challenge. Upskill into the new stack, or risk becoming collateral in a restructuring that moves faster than visa bureaucracy. The 60-day clock does not care about the distinction between a layoff and a transformation."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "AI Is Now America's Top Reason for Firing People. Indian Tech Workers Are in the Crosshairs.",
    "subheadline": "Challenger data shows 87,714 AI-linked job cuts in five months — already more than 2024 and 2025 combined. The H-1B math is getting grim.",
    "slug": make_slug("ai-top-layoff-reason-america-h1b-indian-tech-workers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian nationals hold ~73% of H-1B visas, predominantly in tech. With 60-day grace periods and 116,000+ tech cuts in 2026, the layoff-to-deportation pipeline is an existential concern for NRI workers.",
    "tags": ["ai-layoffs", "h-1b", "indian-tech-workers", "silicon-valley", "automation"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Challenger, Gray & Christmas", "url": "https://www.challengergray.com/"},
        {"name": "The Street", "url": "https://www.thestreet.com/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
        {"name": "WebProNews", "url": "https://www.webpronews.com/"},
        {"name": "LinkedIn / Jared Blikre", "url": "https://www.linkedin.com/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/9300721/pexels-photo-9300721.jpeg",
    "image_caption": "An empty office workspace — a sight growing familiar across Silicon Valley",
    "image_attribution": "Pexels",
    "body": art1_body,
}

# ────────────────────────────────────────────────────────────
# Article 2: India Gets Claude Mythos Access
# ────────────────────────────────────────────────────────────

art2_body = """A select group of Indian organisations — government agencies and private-sector firms, numbering in the single digits — has secured access to Anthropic's Claude Mythos Preview, arguably the most capable AI model on the planet that ordinary customers cannot buy.

The access comes through Project Glasswing, Anthropic's invitation-only programme that uses Mythos to find and fix vulnerabilities in the software that runs critical infrastructure. This week, the San Francisco-based AI lab expanded the programme from roughly 50 initial partners to approximately 150 organisations across more than 15 countries. India made the list.

"We can confirm the expansion includes organizations from India," an Anthropic spokesperson told *The Hindu BusinessLine*. The identities of the specific organisations remain officially undisclosed, though sources indicate they span cybersecurity and financial services.

## What Mythos Actually Does

Claude Mythos is not a chatbot with a better vocabulary. It is a specialised large language model designed to identify software vulnerabilities that human auditors routinely miss. In its first weeks of deployment across the initial 50 partners, Mythos uncovered more than 10,000 high- or critical-severity security flaws across their codebases. Partners now use it not just to find bugs, but to write patches, run penetration testing, and migrate legacy code to memory-safe languages.

Anthropic describes Project Glasswing as targeting organisations "where a successful cyberattack could have far-reaching ramifications, potentially affecting more than 100 million people." The sectors covered include power, water, healthcare, communications, and hardware infrastructure.

The UK AI Security Institute independently tested Mythos in a cyber range environment. It ranked highest among all models tested, with Claude Opus 4.6 in second place, followed by a tie between GPT-5.4 and GPT-5.3 Codex.

## Why India's Inclusion Matters

India's digital public infrastructure — UPI, Aadhaar, DigiLocker, ONDC — processes transactions for 1.4 billion people. A vulnerability in any of these systems is not a theoretical concern; it is a geopolitical one. The inclusion of Indian organisations in Glasswing signals that Anthropic views India's software stack as globally significant enough to warrant its most restricted tools.

Sources told *The Hindu BusinessLine* that entities like TCS, Infosys, and CERT-In (India's national cybersecurity agency) are expected to evaluate the model for use across critical systems. For Indian IT services firms, the access has a dual purpose: defend their own infrastructure, and potentially build Mythos-powered cybersecurity offerings for global clients.

For the Indian diaspora, the implications cut both ways. NRI cybersecurity professionals — a growing cohort at companies like Palo Alto Networks, CrowdStrike, and Microsoft's security division — now work alongside tools that can outperform experienced human analysts. The career premium for understanding how to deploy and govern these models is rising fast.

## The Clock Is Ticking

Anthropic is not being generous out of altruism. The company warned in its announcement: "Within 6 to 12 months, we expect that many other AI companies will have Mythos-class models, and they could release them without safeguards."

That is the real threat model. The defensive window — the period during which only trusted organisations have access to frontier cybersecurity AI — is finite. If Indian organisations do not embed these capabilities into their infrastructure now, they will face adversaries armed with equivalent tools but unburdened by responsible-use guardrails.

The race, as always, is against the clock."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Made Anthropic's Cybersecurity A-List. Only a Handful of Firms Got In.",
    "subheadline": "Project Glasswing's expansion gives Indian government agencies and IT firms access to Claude Mythos — the AI model that found 10,000 critical vulnerabilities in its first weeks.",
    "slug": make_slug("india-anthropic-claude-mythos-project-glasswing-cybersecurity"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian IT firms like TCS and Infosys could build Mythos-powered cybersecurity offerings for global clients. NRI security professionals at Palo Alto Networks, CrowdStrike, and Microsoft now work alongside AI that can outperform human analysts.",
    "tags": ["anthropic", "claude-mythos", "cybersecurity", "india", "project-glasswing"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Inshorts", "url": "https://www.inshorts.com/"},
        {"name": "ainvest", "url": "https://www.ainvest.com/"},
        {"name": "Wikipedia - Claude Mythos", "url": "https://en.wikipedia.org/wiki/Claude_Mythos"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
    "image_caption": "Anthropic CEO Dario Amodei at TechCrunch Disrupt 2023",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ────────────────────────────────────────────────────────────
# Article 3: Google Cuts Cloud & Mandiant Cybersecurity Teams
# ────────────────────────────────────────────────────────────

art3_body = """Sundar Pichai's Google has quietly cut employees across its Cloud division, including members of its Threat Intelligence Group and staff at Mandiant — the cybersecurity firm Google acquired for $5.4 billion in 2022. The layoffs, which occurred over the past two weeks, are part of what the company calls a routine restructuring. The people who lost their jobs might use a different word.

Google has not confirmed how many employees were affected. A company spokesperson offered the standard deflection: "We regularly evaluate our internal structures to ensure we are best positioned to meet the evolving demands of our customers and the industry." In at least one case, according to Business Insider, employees were told the cuts were linked to "reinvesting in growth areas, such as AI."

## The AI Paradox at Google Cloud

The logic is circular in a way that has become familiar across Big Tech. Invest billions in AI. Use AI as the justification for cutting the workforce. Redirect the savings into more AI. Repeat.

Google Cloud is a $41 billion annual run-rate business that has only recently become profitable. The pressure to maintain margins while simultaneously pouring capital into AI infrastructure — data centres, custom TPU chips, Gemini model training — creates a zero-sum dynamic. Every dollar saved from human cybersecurity analysts is a dollar available for GPU clusters.

But the Mandiant cuts feel particularly jarring. Google paid $5.4 billion for Mandiant precisely because its human threat intelligence capabilities were considered among the best in the world. Mandiant's analysts tracked state-sponsored hackers, published groundbreaking research on cyber threats, and provided incident response for Fortune 500 companies and governments. The unit was supposed to be Google Cloud's crown jewel in security.

Now, AI-based tools are increasingly handling functions that Mandiant's human analysts once performed: monitoring, detection, threat analysis, and pattern recognition. The technology that Google is building is, in effect, making the people who built Google's cybersecurity moat redundant.

## What It Means for Indian Engineers at Google

Google employs tens of thousands of Indian-origin engineers across its global operations, with particularly heavy concentrations in Cloud, AI, and enterprise services. Hyderabad and Bengaluru host some of Google's largest engineering offices outside the United States. In the US, Indian nationals make up a significant share of Google's H-1B workforce.

The restructuring is not yet massive in scale — early reports describe a "small number of roles." But the direction is significant. Cloud has been one of the fastest-growing divisions at Google, and one of the most active in H-1B sponsorship. If the growth engine starts cutting, the ripple effects through Google's Indian workforce could be substantial.

Employees who posted about their layoffs on LinkedIn described being caught off-guard. Several had been with the company for years. One former Threat Intelligence Group member noted the irony of being let go from a cybersecurity team at a time when cybersecurity threats, by every available metric, are accelerating.

## A Broader Pattern

Google is not alone. The layoff tracker Layoffs.fyi counts 164 companies shedding a combined 116,379 positions in 2026, with the tech sector leading "by a wide margin." The common thread is the same: AI investment up, headcount down.

For Pichai, the challenge is reputational as well as operational. He has spent years positioning Google as an employer that invests in people, not just technology. The Cloud division was supposed to be the growth story that made Wall Street comfortable with Google's massive AI capital expenditure. Cutting the cybersecurity teams that gave Cloud its credibility undercuts that narrative.

For Indian engineers watching from Hyderabad or Mountain View, the message is clear: in the age of AI, even the most specialised human expertise has an expiration date. The clock is ticking, and Google just moved the hands forward."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Google Is Quietly Gutting Its Cybersecurity Teams. Sundar Pichai's AI Bet Eats Its Own.",
    "subheadline": "Mandiant analysts — the $5.4 billion acquisition that was supposed to be Google Cloud's crown jewel — are among the latest casualties of AI restructuring.",
    "slug": make_slug("google-cloud-mandiant-layoffs-cybersecurity-ai-restructuring"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Google employs tens of thousands of Indian engineers, with Hyderabad and Bengaluru hosting some of its largest offices. Cloud has been a major H-1B sponsorship pipeline, and restructuring there directly affects Indian-origin engineers in the US.",
    "tags": ["google", "sundar-pichai", "mandiant", "cybersecurity", "layoffs", "google-cloud"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Business Insider", "url": "https://www.businessinsider.com/"},
        {"name": "TechLusive", "url": "https://www.techlusive.in/"},
        {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/"},
        {"name": "Storyboard18", "url": "https://www.storyboard18.com/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
    "image_caption": "Alphabet and Google CEO Sundar Pichai",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
}

# ────────────────────────────────────────────────────────────
# Publish all articles
# ────────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
