#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-29 08:00 PDT"""

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
# ARTICLE 1: Kunal Shah named WhatsApp CEO
# ──────────────────────────────────────────────

art1_body = """Meta has done something it has never attempted before: it went to Bengaluru, found the founder of a fintech startup, and handed him the keys to the world's largest messaging platform.

Kunal Shah, who built CRED from a $1 million personal bet into a company valued at $4.5 billion, has been named global head of WhatsApp, succeeding Will Cathcart after nearly seven years. The appointment, announced on Monday, arrived alongside a $900 million investment by Meta into CRED — a combination of primary capital and secondary share purchases — making Zuckerberg's company a minority investor in one of India's most closely watched fintech firms.

## The Deal Behind the Hire

The $900 million round values CRED at $4.5 billion. Shah will retain his roughly 20 per cent stake in the company but step away from day-to-day operations. Miten Sampat, who has led strategy and finance at CRED since 2020, takes over as interim CEO.

CRED, which started as a credit-card bill payment rewards platform, has since expanded into lending, insurance, wealth management, and commerce. Shah disclosed that the company crossed $325 million in annual revenue (approximately ₹3,200 crore) and recorded its first profitable quarter in 2026. It has also conducted five ESOP buybacks — a rarity in the Indian startup world.

## Why WhatsApp Wants an Indian Founder

India is WhatsApp's single largest market, with more than 500 million users — roughly one in every six people on the app globally. Yet WhatsApp Pay, launched to compete with PhonePe and Google Pay, has never managed to crack India's UPI-dominated payments landscape in a meaningful way.

Meta's Chief Product Officer Chris Cox described Shah as someone with "an intuitive grasp of the immense, global product potential for WhatsApp" and "a natural humanism" in his approach to product building. The subtext is clear: Meta wants someone who understands how payments, commerce, and messaging intertwine in markets where WhatsApp is not just an app but daily infrastructure.

Shah is expected to stay in Bengaluru, at least initially, and run WhatsApp's global operations from India — a symbolic inversion of the usual Silicon Valley playbook where Indian talent moves west to lead.

## What This Means for the Diaspora

The appointment is more than a corporate reshuffle. It marks the first time an Indian-origin founder — someone who built his career entirely in India, without a Stanford degree or a Valley pedigree — has been tapped to run a platform with over three billion users globally.

For NRI investors, the $900 million CRED investment signals that India's fintech ecosystem has reached a point where it attracts not just venture capital but strategic capital from the world's largest technology conglomerates. For Indian tech professionals, Shah's trajectory — from FreeCharge to CRED to WhatsApp — is a reminder that the definition of "global tech leadership" is being rewritten from Bengaluru and Mumbai, not just Mountain View and Menlo Park.

The bigger question, as ever, is execution. WhatsApp's superapp ambitions have stumbled before. Shah now has to prove that the instincts that built a premium fintech brand in India can translate into a commerce and payments engine that works from São Paulo to Jakarta."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Meta Handed WhatsApp to an Indian Founder. It Paid $900 Million for the Privilege.",
    "subheadline": "CRED's Kunal Shah becomes the first India-built entrepreneur to run a three-billion-user platform. Meta's bet is that his fintech instincts can unlock WhatsApp's commerce ambitions.",
    "slug": make_slug("kunal-shah-whatsapp-ceo-meta-900-million-cred"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "An Indian founder who built his career entirely in India — no Valley pedigree — now runs a platform used by 3 billion people, while Meta's $900M CRED investment signals that India's fintech ecosystem has matured into a destination for strategic Big Tech capital.",
    "tags": ["meta", "whatsapp", "cred", "kunal-shah", "indian-tech", "fintech", "silicon-valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/whatsapps-pick-indian-fintech-founder-signals-scale-payment-ambitions-2026-06-25/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/23/whatsapp-gets-new-chief-meta-taps-indias-cred-founder-kunal-shah/"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/meta-cred-kunal-shah-whatsapp-sandbox/"},
        {"name": "Bar and Bench", "url": "https://www.barandbench.com/news/trilegal-cooley-azb-latham-cred-900-million-meta"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/83/Kunal_Shah_in_FreeCharge_T-Shirt_%28cropped%29.jpg",
    "image_caption": "Kunal Shah, founder of CRED and newly appointed global head of WhatsApp",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ──────────────────────────────────────────────
# ARTICLE 2: Oracle's 21,000 AI-Driven Layoffs
# ──────────────────────────────────────────────

art2_body = """Oracle buried the number deep in a regulatory filing. On a Monday evening, in the fine print of its fiscal 2026 annual report, the company disclosed that its global headcount had fallen from 162,000 to 141,000 over the past twelve months — a 13 per cent reduction, or roughly 21,000 jobs.

The cost of sending them home: $1.84 billion in severance and restructuring charges. A year earlier, that figure was $374 million.

## AI as the Stated Cause

Oracle did not dress it up. "The adoption and deployment of AI technologies across our operations have resulted, and may continue to result, in reductions to our workforce," the filing stated. It is among the most explicit acknowledgements by a major tech company that artificial intelligence is directly displacing employees — not at some abstract future date, but right now, in the current fiscal year.

The timing is notable. Oracle is simultaneously spending at an extraordinary rate on AI infrastructure. The company said it expects net capital expenditure of roughly $70 billion in the current fiscal year, funded partly through $40 billion in new debt and equity issuance. It has signed massive data centre deals with OpenAI and Meta to compete more aggressively with Amazon Web Services, Microsoft Azure, and Google Cloud.

In other words: Oracle is spending billions to build the machines that replaced the workers.

## The Bigger Picture

Oracle is not alone. A running tally of AI-cited layoffs across major tech firms in 2026 now exceeds 60,000 jobs: Amazon cut 16,000 corporate roles in January; Meta shed roughly 8,000 in May while reallocating thousands more into AI-focused positions; PayPal announced 4,500 cuts; Cisco eliminated nearly 4,000; Intuit dropped 3,000; and Atlassian, Snap, Salesforce, Coinbase, and GitLab together account for thousands more.

According to Layoffs.fyi, 196 tech companies have laid off more than 119,800 employees so far this year. The question is no longer whether AI will reshape the labour market. It is how fast, and who bears the cost.

## The H-1B Shadow

What Oracle's filing does not say — but what thousands of Indian professionals already know — is that these layoffs hit visa-dependent workers disproportionately hard. Oracle is a significant H-1B sponsor. For an Indian-origin engineer or cloud specialist on an H-1B visa, a layoff does not just mean unemployment. It triggers a 60-day grace period to find a new employer willing to sponsor a visa transfer, or face departure from the country.

The 60-day clock is unforgiving. In a market where multiple major employers are cutting simultaneously, the pool of open, visa-sponsoring roles shrinks precisely when it is needed most. Many workers have mortgages, children in American schools, and spouses who have built careers of their own — all of it threatened by a line in a 10-K filing they may never read.

## What NRIs Should Watch

Oracle's stock is down roughly 10 per cent this year and has fallen 48 per cent from its September 2025 record. The company is betting that AI infrastructure revenue will eventually compensate for the restructuring pain. For Indian investors who hold Oracle directly or through index funds, the calculus is straightforward: the company is trading present-day earnings for a future dominated by cloud and AI contracts.

For Indian professionals in the broader tech industry, the message is blunter. The companies that once competed to sponsor your visa are now competing to reduce headcount. The skills that commanded premium salaries two years ago — database administration, manual testing, routine cloud operations — are precisely the roles AI is automating first. The survivors will be those who move up the complexity ladder: AI engineering, infrastructure architecture, security, and the emerging field of AI governance.

Oracle's filing is not an outlier. It is a preview."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Oracle Quietly Cut 21,000 Jobs Last Year. It Blamed AI.",
    "subheadline": "A regulatory filing reveals the scale of Oracle's AI-driven restructuring — and the 60-day visa clock it starts for thousands of Indian workers.",
    "slug": make_slug("oracle-21000-layoffs-ai-h1b-indian-workers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Oracle is a major H-1B visa sponsor. For Indian professionals on work visas, these AI-driven layoffs trigger a 60-day grace period to find new sponsorship or leave the country — a personal crisis buried inside a corporate filing.",
    "tags": ["oracle", "layoffs", "ai", "h1b-visa", "indian-tech-workers", "silicon-valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/oracle-workforce-shrinks-about-21000-employees-amid-ai-adoption-2026-06-23/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/oracle-ai-job-cuts-stock-price/"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/oracle-stock-falls-annual-filing-reveals-21000-jobs-cut/"},
        {"name": "Memeburn", "url": "https://memeburn.com/2026/06/ai-layoffs-2026-major-tech-firms/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Oracle_Redwood_City_February_2013_panorama.jpg/1280px-Oracle_Redwood_City_February_2013_panorama.jpg",
    "image_caption": "Oracle's former Redwood City headquarters in California",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}


# ──────────────────────────────────────────────
# ARTICLE 3: The Tokenmaxxing Backlash
# ──────────────────────────────────────────────

art3_body = """Uber burned through its entire 2026 AI budget in four months. Microsoft quietly cancelled its employees' Claude Code licences and told them to use its own Copilot instead. One unnamed enterprise reportedly racked up $500 million in a single month after giving workers unrestricted access to Anthropic's Claude.

Welcome to the tokenmaxxing backlash — the moment when corporate America looked at its AI bills and flinched.

## From Enthusiasm to Sticker Shock

The term "tokenmaxxing" — treating rising AI token consumption as a proxy for productivity — entered the corporate lexicon sometime in early 2026. Engineering teams at companies like Uber and Meta were ranked on internal leaderboards by how many tokens they consumed. The logic was simple: more AI usage equals more output.

The maths, as it turns out, was not.

A Reuters analysis published this week found that the shift from flat subscription pricing to usage-based billing has made AI costs unpredictable and, in many cases, significantly higher than planned. Token prices have risen roughly 60 per cent since February, driven by surging demand for agentic AI — systems that autonomously carry out multi-step tasks — and a crippling shortage of memory chips. Uber's CTO Praveen Neppalli Naga acknowledged the company was "heading back to the drawing board" on AI spending.

Research from Jellyfish, which analysed 7,548 engineers, found that those given the largest token budgets achieved only twice the throughput at ten times the cost. The return on investment, in other words, was abysmal.

## The C-Suite Turns

The backlash is now coming from the top. Microsoft CEO Satya Nadella — himself one of the architects of the current AI arms race — has begun publicly arguing that smaller, cheaper models can handle a large share of corporate needs. Nikesh Arora, the Indian-origin CEO of Palo Alto Networks, has echoed the sentiment. So has Coinbase's Brian Armstrong.

Nadella's positioning is revealing. Microsoft has trailed its peers in developing its own frontier AI models, and its Copilot product has lost ground to Google's Gemini among enterprise subscribers. Rather than compete on raw model power, Microsoft is pivoting to a strategy of commoditising AI models — offering access to multiple providers, including open-source options, at various price points. "No one wants to be dependent on a small group of frontier models," Nadella told the Wall Street Journal.

Gartner estimates that AI coding costs will surpass the average developer's salary by 2028. Goldman Sachs equity research head James Covello put it bluntly: "At some point, you've got to make money." A Federal Reserve report in 2026 formally listed AI as a top systemic financial risk.

## What Indian Tech Needs to Hear

For India's IT services giants — TCS, Infosys, Wipro, HCL Tech, Cognizant — this is both threat and opportunity. The threat is obvious: if AI tools can replace routine coding, testing, and operations work, the labour arbitrage model that built a $250 billion industry is under pressure. Accenture's recent guidance cut, which wiped billions off Indian IT stocks, was an early tremor.

But the tokenmaxxing backlash also reveals a gap that Indian IT is uniquely positioned to fill. Enterprises are realising they need help not just adopting AI, but governing it — managing costs, selecting the right model for each task, building internal guardrails, and measuring actual ROI. This is consultative, relationship-heavy work that cannot be automated. It is, in many ways, the next iteration of what Infosys and TCS have always sold: the ability to manage complexity at scale for Western enterprises that cannot do it themselves.

For Indian engineers working at American tech companies, the message is more immediate. The companies spending billions on AI infrastructure are simultaneously cutting the humans those tools were supposed to augment. The 119,800 tech layoffs in 2026 are not happening despite the AI investment — they are happening because of it. The engineers who survive will be those who understand not just how to use AI, but how to make it cost-effective.

The era of unlimited token budgets is over. The era of AI governance has barely begun."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Uber Blew Its AI Budget in Four Months. Now the Whole Industry Is Pulling Back.",
    "subheadline": "The 'tokenmaxxing' era is over. Enterprises are discovering that AI tools cost more than the humans they were supposed to replace — and Indian IT could benefit from the reckoning.",
    "slug": make_slug("tokenmaxxing-backlash-ai-costs-enterprise-indian-it"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "India's IT services industry — and the hundreds of thousands of Indian engineers at American tech companies — sits at the centre of this reckoning. The tokenmaxxing backlash creates both risk (more layoffs) and opportunity (AI governance consulting) for the diaspora.",
    "tags": ["ai-costs", "tokenmaxxing", "enterprise-ai", "indian-it", "uber", "microsoft", "satya-nadella"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/cheaper-ai-is-better-soaring-bills-are-reshaping-how-businesses-choose-models-2026-06-29/"},
        {"name": "Morningstar", "url": "https://www.morningstar.com/news/marketwatch/wasted-ai-budgets-uber-microsoft-nvidia-trigger-hiring"},
        {"name": "AI Magazine", "url": "https://aimagazine.com/articles/why-uber-has-already-burned-through-its-ai-budget"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/microsoft-satya-nadella-ai-giants-economy/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/BalticServers_data_center.jpg/1280px-BalticServers_data_center.jpg",
    "image_caption": "A data centre server room — the physical infrastructure behind surging AI costs",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
}


# ──────────────────────────────────────────────
# INSERT ALL
# ──────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
