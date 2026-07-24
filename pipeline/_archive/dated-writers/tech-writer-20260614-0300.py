#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-14 03:00 UTC batch."""

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
# ARTICLE 1: Apple Siri AI + Amar Subramanya
# ─────────────────────────────────────────────

art1_body = """Apple spent two years trying to fix Siri in-house. It failed. So it turned to Google — and handed the rebuild to an Indian-origin engineer who had spent most of his career at the companies Apple was trying to beat.

At WWDC 2026 on June 9, Apple unveiled Siri AI, a ground-up reconstruction of its personal assistant built on a new generation of Apple Foundation Models developed in collaboration with Google's Gemini team. The man standing beside Craig Federighi on stage to explain it was Amar Subramanya, Apple's vice president of artificial intelligence, who took over the role last December after John Giannandrea's departure.

## The Architect

Subramanya is a veteran of Google and Microsoft — exactly the pedigree you would expect Apple to avoid, and exactly the pedigree it needed. His career has spanned search ranking, machine learning infrastructure, and large-scale model training at two of the three companies that have defined the modern AI stack.

At Apple, Subramanya now oversees a family of five foundation models, from the on-device AFM Core to the cloud-based AFM Cloud Pro, the company's most capable reasoning model. During the post-keynote tech talk, he was characteristically precise: "Every model is a significant leap both in quality and capability compared to our previous generation."

The models are not rebranded Gemini. Federighi was emphatic about this, pointing to an empty chart and declaring: "The amount of Google Assistant we use is none." What Apple did take from Google was training methodology — its models are "refined using outputs from Gemini frontier models" and its most demanding inference runs on Nvidia GPUs inside Google's cloud, routed through Apple's Private Cloud Compute architecture.

## What Siri AI Actually Does

The new Siri emerges from the Dynamic Island in iOS 27's Liquid Glass design and operates as both a system-level service and a standalone app. It can analyse on-screen content, browse the web, understand images, and execute multi-step tasks across apps. Apple calls this the "agentic" layer — the AFM Cloud Pro model handles complex reasoning and tool use that would previously have required switching to a third-party chatbot.

For the first time, users can revisit and extend past Siri conversations across devices. The system decides dynamically whether to process requests locally on Apple Silicon or route them to Private Cloud Compute servers. Privacy, Federighi stressed, remains "non-negotiable."

There is a catch. Siri AI will not be available in the EU or China at launch due to regulatory hurdles — a limitation that could affect NRIs in London and other European cities who use iPhones as their primary device.

## Why NRIs Should Care

Subramanya's appointment is the latest in a pattern that has become almost unremarkable: an Indian-origin executive taking a decisive role at a company worth $3 trillion. But the specifics matter. Apple's AI team struggled for years under Giannandrea, burning through timelines and internal morale. One executive reportedly described the state of Siri development as "ugly" during an all-hands meeting in March 2025.

The company brought in Subramanya specifically to fix the problem. That he did so by orchestrating a collaboration with his former employer — without ceding control of the product — is a manoeuvre that will resonate with Indian technologists who have navigated similar cross-company dynamics in the Valley.

For the roughly 500,000 Indian-origin engineers working at Apple, Google, and Microsoft in the US, Subramanya's elevation is not merely symbolic. He now controls one of the most consequential AI deployments on the planet — one that will reach more than a billion devices by the end of the year. The Siri that annoyed you for a decade just got an Indian-origin brain. This time, it might actually work."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Apple Handed Its Broken AI to an Indian-Origin Engineer. He Rebuilt It With Google's Help.",
    "subheadline": "Amar Subramanya, Apple's new VP of AI, orchestrated a Gemini collaboration that produced five foundation models and a Siri overhaul years overdue.",
    "slug": make_slug("apple-amar-subramanya-siri-ai-gemini-wwdc"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin VP of AI Amar Subramanya now controls Apple's most consequential AI deployment, following a career at Google and Microsoft — a trajectory that mirrors hundreds of thousands of Indian technologists in the Valley.",
    "tags": ["apple", "siri-ai", "amar-subramanya", "google-gemini", "indian-tech-leaders", "wwdc-2026"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/08/craig-federighi-details-apples-collaboration-with-google-for-siri-ai-in-ios-27/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-wwdc-2026-siri-ai-child-safety-key-takeaways/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/06/09/apple-reveals-long-delayed-siri-ai-makeover-at-worldwide-developers-conference/"},
        {"name": "Computerworld", "url": "https://www.computerworld.com/article/siri-ai-is-all-apple-it-just-needed-google-to-get-there/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/30530426/pexels-photo-30530426.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A smartphone displaying an AI assistant interface — Apple's Siri AI aims to become the definitive on-device intelligence layer",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 2: Musk Terafab + ASML
# ─────────────────────────────────────────────

art2_body = """Elon Musk addressed employees of ASML, Europe's most valuable company, on June 11 — the same day SpaceX finalised its IPO pricing at $135 per share. The topic was not rockets. It was Terafab, his plan to build the largest semiconductor factory on Earth.

The virtual appearance at ASML's closed-door technology conference was no casual fireside chat. ASML CEO Christophe Fouquet has publicly confirmed that Musk is "very serious" about the project, and the company described the session as part of Musk "becoming part of the broader semiconductor ecosystem." ASML shares surged more than 9.5% on the day.

## The Numbers

Terafab's scale has ballooned since its first mention. The initial proposal was a $20 billion facility in Texas. Current filings put the first phase at $55 billion, with total projected costs reaching $119 billion across all phases. The factory would target 2-nanometre process technology and eventually deliver a terawatt of computing power per year, supplying chips for Tesla's Optimus robots, SpaceX's satellite constellation, and xAI's training infrastructure.

Intel has already signed on as a foundry partner, though SpaceX's IPO filings note that the agreement allows either side to back out. Tesla and SpaceX staffers have reportedly contacted Applied Materials, Tokyo Electron, and Lam Research about sourcing photomasks, substrates, and etching equipment.

The critical dependency is ASML itself. The Dutch company holds a global monopoly on extreme ultraviolet (EUV) lithography machines — the tools that print circuitry at the nanometre scale. Every advanced chip factory in the world, from TSMC's Arizona plants to Samsung's Korean fabs, runs on ASML equipment. Without ASML's buy-in, Terafab is a very expensive warehouse.

## Why It Matters Beyond Musk

The timing is not accidental. The global chip supply chain remains concentrated in Taiwan, where TSMC produces the vast majority of leading-edge semiconductors. TSMC's CEO C.C. Wei said on June 4 that demand will outpace supply "for years," even with expanded US manufacturing. Google is now splitting its next-generation TPU across three foundries — TSMC, Samsung, and Intel — just to secure enough capacity.

Terafab represents a different thesis entirely: vertical integration by a consumer of chips, rather than diversification by a designer. If it works, it would be the first time a non-semiconductor company built a leading-edge fab from scratch since the industry consolidated in the 1990s.

## The Indian Engineer Question

Here is where the NRI angle sharpens. Building a 2-nanometre fab requires thousands of process engineers, lithography specialists, and semiconductor physicists. The US does not produce enough of them domestically — a point Intel CEO Lip-Bu Tan has made repeatedly. India's semiconductor workforce, trained at IITs and in the fabs of Samsung, TSMC, and GlobalFoundries, is one of the few talent pools deep enough to staff such a project.

Micron's Gujarat ATMP facility, inaugurated by PM Modi in February, and Tata Electronics' ₹91,000 crore fab in Dholera are already pulling Indian-origin engineers back from overseas postings. A Terafab in Texas would compete directly for that same talent — potentially offering the kind of compensation packages that make an H-1B transfer to Austin a compelling career move.

For NRI semiconductor professionals currently weighing a return to India against staying in the US, Terafab adds a third variable to an already complex calculation. Intel's involvement means the project would likely draw heavily from the same Indian-origin engineering bench that already staffs its Hillsboro and Chandler operations.

The question is no longer whether Musk is serious about chipmaking. ASML's engagement answers that. The question is whether the talent exists to make it real — and where that talent will choose to go."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Musk's $55 Billion Chip Factory Courts ASML. Indian Engineers Are the Talent It Needs.",
    "subheadline": "Terafab's plan for 2-nanometre chips requires thousands of process engineers the US cannot produce domestically. India's semiconductor workforce is watching.",
    "slug": make_slug("musk-terafab-asml-semiconductor-indian-engineers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Terafab would compete with India's Dholera and Gujarat fabs for the same Indian-origin semiconductor talent, adding a third option for NRI engineers weighing career moves between the US and India.",
    "tags": ["elon-musk", "terafab", "asml", "semiconductor", "intel", "indian-engineers", "spacex"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/musk-speak-chip-tool-giant-asml-event-ahead-spacex-ipo-2026-06-12/"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/musk-terafab-semiconductor-asml-spacex-ipo/"},
        {"name": "ainvest", "url": "https://www.ainvest.com/news/elon-musk-to-pitch-55-billion-chip-megafactory-to-asml-ahead-of-spacex-ipo/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/ae/ASML_headquarters_Veldhoven.jpg",
    "image_caption": "ASML headquarters in Veldhoven, Netherlands — the company holds a global monopoly on EUV lithography machines essential for advanced chipmaking",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 3: GitHub outages + AI traffic surge
# ─────────────────────────────────────────────

art3_body = """Last year, GitHub handled one billion commits for the entire calendar year. It now processes 1.4 billion every month. The platform that 100 million developers depend on is buckling under traffic it did not expect — traffic generated, in large part, by the AI coding tools GitHub itself evangelised.

In its May 2026 Availability Report, published this week, GitHub acknowledged nine separate incidents that degraded performance across the platform. That was one fewer than April, which is the kind of improvement that makes you wince rather than celebrate.

## What Broke

The problems are not exotic. Load balancer misconfigurations caused 15% of API requests to return erroneous 401 authentication errors on June 10, breaking CI/CD pipelines worldwide. Earlier incidents knocked out GitHub Actions, the platform's automation service, with some users receiving false "account suspended" notices. The pattern is consistent: infrastructure built for human-scale development is being overwhelmed by machine-speed workflows.

Jakub Oleksy, GitHub's SVP of software engineering, was candid: "We acknowledge that we have work to do." The company had planned a 10x capacity expansion back in October 2025. By February 2026, it was clear that 30x would be needed. GitHub has since migrated 40% of its core traffic to Azure (up from 8% in February) and doubled effective capacity in four months.

It is still not enough. GitHub also briefly halted new Copilot subscriptions to manage the cost impact of its AI services and adjust pricing for shifting model provider policies. The platform that once charged $10 per month for AI-assisted coding now offers metered billing that can run to $750 per month for heavy agentic workflows.

## The AI Coding Paradox

The irony is structural. GitHub's parent company, Microsoft, has spent billions positioning Copilot as the future of software development. Satya Nadella has called AI-assisted coding "the most transformative tool for developers since the IDE." GitHub's own COO Kyle Daigle noted that Actions usage has grown from 500 million minutes per week in 2023 to 2.1 billion minutes per week now.

But every AI-generated pull request, every agentic workflow that autonomously creates branches and commits, every Copilot suggestion that spawns a new file — all of it flows through GitHub's infrastructure. The platform is simultaneously the beneficiary and the victim of the AI coding revolution.

A security dimension compounds the problem. On June 5, GitHub's anti-fraud system disabled 73 Microsoft-owned repositories in 105 seconds after detecting Miasma, a self-replicating credential-stealing malware that specifically targets AI coding assistants like Claude Code, Gemini CLI, and Cursor. The malware waits for a developer to open an infected package inside an AI tool, then steals authentication credentials and attempts to spread through accessible repositories.

## Why Indian Developers Bear the Brunt

India is GitHub's second-largest developer market after the United States, with an estimated 15 million users. Indian developers disproportionately rely on GitHub Actions for CI/CD automation, and many work in time zones where US-evening outages hit during peak working hours.

The pricing shift matters even more. GitHub Copilot's move from a flat $19-per-month subscription to metered billing that can reach $750 creates a stark divide. For developers at TCS, Infosys, or Wipro — where per-seat software budgets are tightly controlled — the economics of AI-assisted coding just got harder to justify. For independent Indian developers and small startups building on GitHub, the cost of agentic workflows may price them out entirely.

The reliability question is equally pointed. When a load balancer misconfiguration breaks CI/CD pipelines, it does not distinguish between a developer in San Francisco and one in Bengaluru. But the Bengaluru developer is more likely to be on a client deadline that does not accommodate a four-hour GitHub outage during their workday.

GitHub remains indispensable. That is precisely the problem. When the platform that hosts your code, runs your tests, and powers your AI assistant goes down nine times in a month, indispensable starts to feel uncomfortably like fragile."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "GitHub Is Drowning in AI-Generated Code. India's 15 Million Developers Feel It First.",
    "subheadline": "Nine outages in May, a 30x capacity crunch, and Copilot bills that can hit $750 a month — GitHub's AI bet is straining the platform Indian developers cannot leave.",
    "slug": make_slug("github-ai-outages-india-developers-copilot"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "India is GitHub's second-largest market with 15 million developers. Outages during US evenings hit Indian working hours, and Copilot's metered pricing disproportionately affects Indian IT shops with tight per-seat budgets.",
    "tags": ["github", "ai-coding", "copilot", "india-developers", "microsoft", "devops"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Register", "url": "https://www.theregister.com/2026/06/12/github_outages_ai_coding/"},
        {"name": "Medium / Cyber Security", "url": "https://medium.com/@cybersecurity/microsofts-github-got-hacked-and-your-ai-coding-assistant-may-have-been-the-target"},
        {"name": "Hacker News / Headlines Briefing", "url": "https://headlinesbriefing.com/github-outage-disrupts-api-with-401-errors/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/1181675/pexels-photo-1181675.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A developer works across multiple monitors — GitHub's infrastructure is straining under AI-generated traffic that has grown from 1 billion commits per year to 1.4 billion per month",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}


# ─────────────────────────────────────────────
# INSERT ALL ARTICLES
# ─────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
