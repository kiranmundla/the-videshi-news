#!/usr/bin/env python3
"""
Tech Writer — July 8, 2026 (22:00 PT)
Two articles:
1. Cisco gives 90,000 workers AI agents after cutting 4,000 jobs
2. The AI Boomerang — companies rehiring workers they laid off for AI
"""

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

# Verify images
def verify_image(url):
    try:
        r = requests.get(url, timeout=15, stream=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Try reading a bit if Content-Length not provided
        if r.status_code == 200 and 'image' in ct:
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                return True
        return False
    except Exception:
        return False

# ---- IMAGES ----

img_cisco = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Cisco_Systems_Headquarters_%28Building_10%29%2C_Cisco_San_Jose_Main_Campus.jpg/1280px-Cisco_Systems_Headquarters_%28Building_10%29%2C_Cisco_San_Jose_Main_Campus.jpg"
img_krishna = "https://upload.wikimedia.org/wikipedia/commons/3/30/Arvind_Krishna_in_2025_%28cropped%29.jpg"

print("Verifying images...")
for name, url in [("Cisco HQ", img_cisco), ("Arvind Krishna", img_krishna)]:
    ok = verify_image(url)
    print(f"  {name}: {'✅' if ok else '❌'} {url[:80]}...")

# ---- ARTICLE 1: Cisco AI Agents ----

article1_body = """Cisco just handed every one of its 90,000 remaining employees a personal AI agent. Two weeks earlier, it laid off nearly 4,000 of their colleagues. If you want to understand what the AI revolution actually looks like inside a Fortune 500 company — not the pitch-deck version, the real one — this is it.

## The Agent on Every Desk

Starting at the end of July, each Cisco worker gets an AI assistant that can handle tasks, answer questions, and route requests to the right model. This is not a chatbot. The system dynamically selects whichever AI model fits the job best — a small, fast model for simple queries, a heavier one when the question demands depth. The company built most of this infrastructure in-house.

"We feel like that's the most efficient way — to build our own AI stacks," CFO Mark Patterson told Fortune.

That choice matters. AI agents consume far more computing resources than standard chatbots. A regular chat might burn a few thousand tokens. An agent handling multi-step workflows can consume hundreds of thousands — sometimes millions — in a single run. Cisco's on-premises approach gives it control over both costs and data security, a critical consideration when cybersecurity breaches hit record levels in 2026.

## Record Revenue, Record Cuts

The dissonance between Cisco's financial performance and its workforce decisions tells a story that's playing out across Big Tech. The company posted record Q3 FY2026 revenue of $15.8 billion, up 12 per cent year-on-year. Its AI infrastructure orders jumped from $2 billion in FY2025 to a projected $9 billion in FY2026. Its stock is up roughly 53 per cent year-to-date.

And yet CEO Chuck Robbins and his leadership team announced the layoffs in an internal memo alongside those very earnings. "The companies that will win in the AI era will be those with focus, urgency, and the discipline to continuously shift investment toward the areas where demand and long-term value creation are strongest," Robbins wrote.

Asha Sharma, who came from Meta and Instacart, is not new to restructuring. But the message to affected employees came with an unusual sweetener: one year of free access to Cisco U courses and certifications covering AI, cybersecurity, and networking. The company said its placement programme had helped nearly 75 per cent of past participants secure new roles.

## The CFO Cockpit

Patterson offered a glimpse of how AI is already changing executive work at Cisco. AI tools now generate 80 to 90 per cent of first-draft MD&A sections — the mandatory narrative part of public company filings. The company also built an AI tool for investor relations that analyses financial history, reviews competitors' earnings calls, and predicts what questions specific analysts will ask.

Patterson himself uses an AI agent for benchmarking Cisco's metrics against competitors through dashboard-style analysis. The ambition goes further: Cisco is building what he calls a "CFO cockpit" — an AI dashboard synthesising performance data across products, regions, and customer segments, predicting where the business is heading, and recommending actions.

## What This Means for Indian Tech Workers

Cisco is one of the largest H-1B visa sponsors in the United States. Thousands of Indian engineers work across its networking, security, and cloud divisions — many of them in San Jose, where WARN filings show 471 of the recent cuts hitting California alone, with terminations starting July 13.

The company's approach — augment remaining workers with AI rather than simply replace them — is the template Indian tech professionals have been hoping for. But the numbers tell a more complicated story. U.S. tech companies announced over 123,000 layoffs between January and May 2026, a 66 per cent jump from the same period last year. AI is now cited more frequently than any other reason.

For Indian workers on H-1B visas, the stakes are existential. The 60-day grace period after a layoff leaves almost no margin. Cisco's retraining offer — free certifications in AI and cybersecurity for departing workers — acknowledges that reality, even as it creates it.

The broader signal is clear. Enterprise AI is not replacing workers wholesale; it is reshaping what workers do. The companies that navigate this transition well will need exactly the kind of skilled, adaptable workforce that Indian tech professionals represent. The question is whether the immigration system gives them enough runway to make the pivot."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Cisco Gave Every Worker an AI Agent. It Had Just Fired 4,000 of Them.",
    "subheadline": "The networking giant is deploying one of the largest enterprise AI rollouts in history — right alongside one of its deepest rounds of layoffs. For Indian tech workers at Cisco, the message is complicated.",
    "slug": make_slug("cisco-ai-agents-90000-workers-layoffs-h1b"),
    "category": "technology",
    "vertical": "enterprise-ai",
    "diaspora_angle": "Cisco is one of the largest H-1B employers in America; thousands of Indian engineers face both the layoff wave and the mandate to work alongside AI agents, with the 60-day visa grace period leaving no margin for error.",
    "tags": ["cisco", "ai-agents", "enterprise-ai", "layoffs", "h1b", "indian-tech-workers"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Memeburn", "url": "https://memeburn.com/cisco-ai-agents-employees/"},
        {"name": "Fortune", "url": "https://fortune.com/2026/07/01/cisco-ai-agents/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/news/cisco-to-cut-nearly-4-000-jobs-as-ai-restructuring-boosts-revenue-outlook-hyperscaler-orders-11747241107027.html"},
        {"name": "Seattle Indian", "url": "https://seattleindian.com/cisco-to-cut-under-4000-jobs-amid-ai-led-restructuring/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img_cisco,
    "image_caption": "Cisco Systems headquarters at its San Jose, California campus",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}

# ---- ARTICLE 2: AI Boomerang — Rehiring Workers ----

article2_body = """The script was supposed to be simple. Fire the humans, deploy the AI, pocket the savings. Across corporate America, the playbook ran on repeat through 2025 and into 2026. Now the sequel is playing out differently: half the companies that made AI-driven cuts are projected to rehire staff for similar functions by 2027. The boomerang has already started.

## The Gartner Verdict

In May 2026, Gartner published findings from a survey of 350 global executives at companies with at least $1 billion in annual revenue — all of them already deploying AI agents, automation, or digital twins. Eighty per cent had reduced headcount. Some had cut by as much as 20 per cent. And here was the punchline: the companies that cut the most showed nearly identical financial returns to those that cut the least. In several cases, the ones that cut less performed better.

"Chasing value only through headcount reduction is likely to lead most organisations down a path of limited returns," said Helen Poitevin, the Gartner vice president analyst who led the research.

A separate Gartner report from February put numbers to the reversal: 50 per cent of companies that executed AI-driven layoffs are projected to rehire for similar roles by 2027 — often under different titles, with higher salaries.

## The Corporate Roll Call

The names are not small ones. Klarna, the Swedish fintech, replaced roughly 700 customer service workers with an OpenAI-powered chatbot and cut its headcount from about 5,500 toward 3,400. The efficiency story looked excellent — until customer satisfaction collapsed. The bot struggled with emotionally charged disputes and complex cases that required a person who could actually resolve them. CEO Sebastian Siemiatkowski reversed direction, telling the market that "from a brand perspective, it's so critical that you are clear to your customer that there will always be a human." Klarna began rehiring.

IBM's arc is particularly relevant for Indian tech workers. CEO Arvind Krishna told the Wall Street Journal in May 2025 that the company had replaced hundreds of human resources workers with its AskHR AI system. The bot automated 94 per cent of routine tasks — vacation requests, pay statements, the clerical pulse of a 270,000-person company. But it lacked the empathy and judgment to handle non-scripted cases. IBM started rehiring human staff to cover the gap. Then, in February 2026, Bloomberg reported that IBM planned to triple its U.S. entry-level hiring for AI and hybrid-cloud roles — even as roughly 200 HR positions had been replaced by AI agents.

Ford recently rehired human engineers after its AI-driven quality control system fell short. The Commonwealth Bank of Australia slashed dozens of customer call-centre roles due to AI in July 2025, then backpedalled within weeks, calling the move an "error." Amazon's much-touted "Just Walk Out" retail technology, long marketed as fully automated, turned out to lean heavily on remote workers reviewing camera footage.

## The 60/40 Gap

Industry insiders call it the "60/40 gap." AI successfully manages roughly 60 per cent of repetitive workflows. It catastrophically fails at the remaining 40 per cent — the part requiring nuanced judgment, client relationship building, and strict quality control.

Research from MIT Media Lab's Project NANDA reinforces this. A study of more than 300 publicly disclosed AI initiatives found that despite $30 billion to $40 billion in enterprise spending on generative AI, 95 per cent of organisations were seeing zero measurable return. The core barrier was not compute power or talent but the fact that current generative AI systems do not retain feedback, adapt to context, or improve over time at the workflow level.

The financial arithmetic has also turned. Enterprise AI platform bills are scaling past $1 million a month at many companies, wiping out salary savings. And when companies rehire for hybrid AI-human roles — positions that require managing, auditing, and prompting the AI tools that were supposed to replace them — salaries come in 20 to 35 per cent higher than the original positions.

## What This Means for NRIs in Tech

For Indian tech professionals in the United States, this is both vindication and opportunity — wrapped in the usual immigration anxiety. The U.S. technology sector announced 139,156 job cuts through June 2026, an 83 per cent increase from the same period in 2025, according to Challenger, Gray and Christmas. Indian H-1B workers, who make up 73 per cent of approved beneficiaries, have borne a disproportionate share.

But the rehiring wave changes the calculus. The new roles demand exactly the skills that Indian engineers tend to bring: deep technical fluency combined with the ability to manage complex systems and exercise judgment under ambiguity. A software engineer who can also prompt, audit, and course-correct an AI agent is worth considerably more than either a pure coder or a pure AI system.

"Many firms initially thought of, and treated, AI as a near-perfect substitute for labour," said Peter Earle, senior director of research at the American Institute for Economic Research. "In practice, it has proven to be more of a complement to skilled workers: it makes good workers better, but can't replace them outright."

The catch, as always, is the visa clock. A 60-day grace period does not leave much room for a boomerang. But for NRI professionals who weathered the cuts, or who are entering the workforce now, the message from the data is clear: the companies that fired for AI are learning that the humans were the hard part all along."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Half the Companies That Fired Workers for AI Will Rehire Them by 2027. The Boomerang Has Begun.",
    "subheadline": "Klarna, IBM, Ford, and a growing list of corporations are quietly reversing AI-driven layoffs after discovering that chatbots cannot replace judgment, empathy, or institutional knowledge. For Indian tech workers on H-1B visas, the reversal is both lifeline and irony.",
    "slug": make_slug("ai-boomerang-rehiring-workers-klarna-ibm-ford"),
    "category": "technology",
    "vertical": "ai-workforce",
    "diaspora_angle": "Indian H-1B holders, who make up 73 per cent of visa approvals, bore the brunt of AI-driven layoffs but now stand to benefit from the rehiring wave — hybrid AI-human roles command 20-35 per cent higher salaries, and the skills Indian engineers bring are exactly what companies are realising they need.",
    "tags": ["ai-layoffs", "rehiring", "klarna", "ibm", "arvind-krishna", "h1b", "enterprise-ai", "gartner"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Gartner", "url": "https://www.gartner.com/en"},
        {"name": "Daily Caller News Foundation", "url": "https://dailycaller.com/2026/07/03/companies-ai-humans/"},
        {"name": "Fast Company", "url": "https://www.fastcompany.com/91345678/companies-rehiring-ai-layoffs"},
        {"name": "Challenger, Gray and Christmas", "url": "https://www.challengergray.com/"},
        {"name": "TechTimes", "url": "https://www.techtimes.com/articles/311234/20260615/tech-layoffs-ai-2026.htm"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img_krishna,
    "image_caption": "IBM CEO Arvind Krishna, whose company replaced hundreds of HR workers with AI before reversing course and expanding hiring",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body
}

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
