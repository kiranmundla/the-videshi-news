#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-31 09:00 UTC batch"""

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

# Verify images before inserting
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return url
        # Try GET if HEAD fails
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct:
            return url
    except Exception as e:
        print(f"  ⚠️ Image verification failed for {url}: {e}")
    return None


articles = [
    # ── Article 1: Microsoft Copilot Super App ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Satya Nadella's Microsoft Is Building an AI Super App. It Could Change How Every Indian Developer Works.",
        "subheadline": "The company plans to unify GitHub Copilot, chat, and a new agentic workflow tool called Autopilot into a single platform — and it's releasing homegrown AI models to break free from OpenAI.",
        "slug": make_slug("microsoft-copilot-super-app-satya-nadella-build"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Satya Nadella's Microsoft employs more H-1B visa holders than any other US company. The Copilot super app and new homegrown AI models directly affect tens of thousands of Indian engineers in Redmond, Hyderabad, and Bengaluru — and reshape the AI coding tools that Indian developers worldwide rely on daily.",
        "tags": ["microsoft", "satya-nadella", "copilot", "ai-coding", "indian-tech-leaders", "github"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fortune", "url": "https://fortune.com/2026/05/30/microsoft-copilot-super-app/"},
            {"name": "The Information", "url": "https://www.theinformation.com/articles/microsoft-to-release-new-coding-model"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-microsoft-windows-pc-debut-2026-05-31/"},
            {"name": "Digit.in", "url": "https://www.digit.in/news/general/microsoft-plans-super-app-copilot.html"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "body": """When Satya Nadella took over Microsoft in 2014, the company was a Windows-and-Office monolith losing ground to every startup with a GitHub account. Twelve years later, Nadella has turned it into a $3.2 trillion AI juggernaut — and now he wants to consolidate the sprawl.

Microsoft is building what insiders call a "super app" that will merge its constellation of Copilot AI tools into a single platform. According to Fortune, the project — developed under the slogan "Delivering one Copilot" — will combine GitHub Copilot, Copilot Chat, Copilot Cowork, and a new agentic workflow tool internally codenamed Autopilot. Jacob Andreou, Microsoft's recently appointed head of Copilot, is leading the effort.

The timing is deliberate. Microsoft's Build developer conference kicks off in San Francisco next week, where the company is expected to preview elements of the unified app alongside a suite of homegrown AI models — including a coding model built entirely in-house, without OpenAI's involvement.

## Why This Matters for Indian Engineers

Microsoft's AI ambitions rest disproportionately on Indian talent. The company consistently ranks as the largest employer of H-1B visa holders in the United States, with tens of thousands of Indian engineers across Redmond, the Bay Area, and its massive campuses in Hyderabad and Bengaluru. GitHub Copilot, which now has millions of active users, was built in significant part by Indian engineering teams.

The super app isn't just a product consolidation. It's a bet that developers — the majority of whom at Microsoft are Indian or Indian-origin — will prefer a single AI interface over toggling between half a dozen tools. For the Indian developer working on Azure microservices in Hyderabad or debugging a React app in Seattle, the difference between three separate Copilot windows and one unified surface is the difference between friction and flow.

## Breaking Up With OpenAI

The more consequential move may be the homegrown models. Microsoft has relied heavily on OpenAI's GPT family to power Copilot since its launch. But the partnership has frayed. The two companies renegotiated terms earlier this year to reduce mutual dependency, and OpenAI's own ambitions — a reported IPO, a services venture that spooked Indian IT stocks — have made the relationship increasingly competitive.

Microsoft is now developing its own coding model, transcription models, reasoning engines, and image generators. Mustafa Suleyman, the company's AI CEO and DeepMind co-founder, is expected to unveil several of these at Build. If the in-house models perform well enough, Microsoft could substantially reduce its OpenAI licensing costs while gaining full control over its AI stack.

For Indian IT services companies, this matters in a different way. Cognizant, Infosys, and Wipro all build enterprise solutions on top of Microsoft's AI platform. A shift in the underlying model layer — from OpenAI to Microsoft-native — could force rearchitecting of consulting engagements that were designed around specific GPT capabilities.

## The Competitive Pressure

Nadella has reason to move fast. Anthropic's Claude Code has quietly overtaken GitHub Copilot as the preferred AI coding tool among many developers, particularly for complex, multi-file reasoning tasks. Google's Gemini-powered coding tools are gaining traction. And the reported super app comes as Microsoft stock has lost more than 7 per cent this year, with investors questioning whether its early AI lead is durable.

The Nvidia partnership adds another dimension. Reuters reported Saturday that the first Windows PCs powered by Nvidia's chips will debut at Computex and Build next week — a joint Microsoft-Nvidia effort that could reshape the laptop market. For Indian hardware engineers at both companies, it's a convergence of the two biggest bets in tech.

The super app is expected to launch by end of summer 2026. For the estimated 300,000 Indian-origin engineers who touch Microsoft's ecosystem daily — as employees, contractors, or enterprise developers — it will be the single most consequential product decision Nadella has made since acquiring GitHub in 2018."""
    },

    # ── Article 2: DeepSeek V4-Pro Permanent Price Cut ──
    {
        "id": str(uuid.uuid4()),
        "headline": "DeepSeek Just Made Its 75% Price Cut Permanent. Indian IT's Margin Problem Got Worse.",
        "subheadline": "The Chinese AI lab's V4-Pro model now costs 7 to 17 times less than comparable Western models. For Infosys, TCS, and Wipro, the implications are existential. For Indian startups, it's a gift.",
        "slug": make_slug("deepseek-v4-pro-permanent-price-cut-indian-it"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's $250 billion IT services industry — employer of millions of Indian-origin workers globally — faces direct margin pressure from plummeting AI inference costs. Meanwhile, Indian AI startups like O-Health and Sarvam AI can now access frontier-class models at a fraction of Western pricing, potentially leapfrogging their Silicon Valley peers.",
        "tags": ["deepseek", "ai-pricing", "indian-it-services", "infosys", "tcs", "wipro", "ai-startups"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VentureBeat", "url": "https://venturebeat.com/ai/deepseek-v4-pro-price-cut-permanent/"},
            {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/a20250525PD200.html"},
            {"name": "TechBooky", "url": "https://www.techbooky.com/deepseek-slashes-v4-pro-pricing/"},
            {"name": "Gizmodo", "url": "https://gizmodo.com/deepseek-v4-models-cost-savings/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17483871/pexels-photo-17483871.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """There is a number that should keep every Indian IT services CEO awake at night: 75 per cent.

That's the discount DeepSeek, the Hangzhou-based AI lab, has now made permanent on its flagship V4-Pro model. What began as a temporary promotional rate has become the new floor for frontier AI inference pricing — and the maths is brutal. At $0.44 per million input tokens and $0.87 per million output tokens, DeepSeek's V4-Pro is roughly seven times cheaper on inputs and seventeen times cheaper on outputs than Anthropic's Claude Sonnet or OpenAI's GPT-5.5.

For Indian AI startups, this is Christmas in May. For India's $250 billion IT services industry, it's the sound of a business model cracking.

## The Margin Squeeze

The core proposition of companies like TCS, Infosys, Wipro, and Cognizant has always been labour arbitrage: hire brilliant Indian engineers at a fraction of Silicon Valley rates, then charge Western clients a premium for their work. AI was supposed to be the next chapter of this story — Indian IT firms would deploy AI tools to make their engineers more productive, capturing the efficiency gains as margin.

DeepSeek's pricing demolishes the assumption that AI infrastructure carries premium costs. If a Bengaluru startup can access frontier-class AI reasoning for $0.87 per million output tokens, the value of a consulting engagement built around the same capability at ten times the price becomes difficult to justify.

Salil Parekh, whose $8.7 million compensation package was disclosed this week in Infosys's annual report, is navigating this squeeze in real time. Infosys forecast revenue growth of just 1.5 to 3.5 per cent for fiscal 2027 — below analyst expectations. Indian IT stocks slid to three-year lows this month after OpenAI announced a services venture that could compete directly with traditional consulting.

## The Startup Windfall

But every disruption has two sides, and the cheaper side is where Indian startups are placing their bets.

Akshar Keremane, co-founder of Bangalore-based O-Health — a Gates Foundation-backed startup deploying AI in hospitals and rural clinics — told Bloomberg that DeepSeek's pricing "allows users to experiment at a model capability and scale that wasn't available earlier." For startups operating in India, where customer willingness to pay for AI services is a fraction of US levels, the cost reduction is the difference between a viable product and a demo.

Sarvam AI, Krutrim, and dozens of other Indian deep-tech startups now have access to models that perform within striking distance of GPT-5.5 at a seventeenth of the cost. The 1-million-token context window — large enough to process entire codebases or lengthy legal documents — removes another barrier that kept Indian builders on the sidelines of frontier AI.

## The Geopolitical Wrinkle

DeepSeek's pricing advantage isn't just about efficiency. The company, which is reportedly seeking $7.35 billion in its first external funding round at a valuation exceeding $50 billion, benefits from Chinese infrastructure costs that are structurally lower than those in the United States. When hosted in China, its cache-read pricing is reportedly 87 times cheaper than equivalent Western cloud offerings.

For Indian enterprises and government bodies evaluating AI providers, this creates an uncomfortable choice. DeepSeek's V4 models are MIT-licensed and open-weight — technically, anyone can run them locally without sending data to Chinese servers. But the diplomatic calculus between India's deepening US tech partnerships and China's aggressive AI pricing is a variable that no quarterly earnings call has yet addressed.

## What NRI Investors Should Watch

The Indian IT services sector employs millions of people, supports hundreds of thousands of H-1B and L-1 visa holders in the US, and remains a cornerstone of NRI investment portfolios. DeepSeek's permanent price cut doesn't kill this industry overnight — enterprise relationships, regulatory compliance, and domain expertise still matter. But it compresses the timeline for transformation.

Gartner projects that inference costs for large models could fall by more than 90 per cent by 2030. If that trajectory holds, the Indian IT firm of 2030 will look nothing like the one that prints quarterly results today. The firms that survive will be those that stop selling AI as a premium service and start treating it as plumbing — cheap, reliable, and invisible.

For the NRI engineer at Google debating a return to India to join a startup, DeepSeek's pricing just made that bet considerably more attractive."""
    },

    # ── Article 3: AI Cracks Erdős Math Problems ──
    {
        "id": str(uuid.uuid4()),
        "headline": "AI Just Solved Maths Problems That Stumped Humans for 80 Years. India's Number Theory Tradition Should Take Note.",
        "subheadline": "OpenAI disproved a foundational Erdős conjecture, and DeepMind's AlphaProof Nexus cracked nine more. The breakthroughs are reshaping what mathematicians — and the IITs that produce them — think machines can do.",
        "slug": make_slug("ai-erdos-math-problems-openai-deepmind-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India produces more mathematics graduates than any country except China, and IIT-trained researchers hold senior positions at OpenAI, DeepMind, and every major AI lab. These breakthroughs in AI-assisted mathematics directly affect the career landscape for Indian-origin researchers and reshape a field where India has outsized intellectual heritage — from Ramanujan to modern combinatorics.",
        "tags": ["ai-mathematics", "openai", "deepmind", "erdos", "iit", "ramanujan", "indian-researchers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/science/ai-math-erdos-problem-openai/"},
            {"name": "New Scientist", "url": "https://www.newscientist.com/article/2473000-mathematicians-stunned-by-ais-biggest-breakthrough/"},
            {"name": "Physics World", "url": "https://physicsworld.com/a/ai-led-solutions-of-erdos-problems-spark-debate/"},
            {"name": "Medium (Luhui Dev)", "url": "https://luhuidev.medium.com/deepmind-alphaproof-nexus-explained/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6238050/pexels-photo-6238050.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """In 1946, Paul Erdős posed a deceptively simple question about dots on a flat surface: how many pairs of dots can be exactly the same distance apart? He set an upper bound. Mathematicians assumed he was right. For eighty years, no one proved otherwise.

Last week, an unreleased AI model from OpenAI did.

The model didn't just nudge the bound — it demolished it. By borrowing an obscure technique from algebraic number theory, it constructed vast lattices in higher dimensions and collapsed them into two-dimensional arrangements that yielded far more equidistant pairs than Erdős had believed possible. The "chain of thought" reasoning ran more than 75,000 words — the length of the first Harry Potter novel — and cost, by one estimate, less than $1,000 in compute.

"My immediate reaction was disbelief," said Will Sawin, a mathematician at Princeton. "Then I looked at it more and convinced myself that it does work."

Days later, Google DeepMind's AlphaProof Nexus — a formal proof system combining large language models with the Lean proof assistant — announced it had solved nine open Erdős problems, some unsolved for 56 years, and proved 44 conjectures from the Online Encyclopedia of Integer Sequences. Demis Hassabis, DeepMind's CEO, narrowed his timeline for artificial general intelligence from 2030-35 to "as early as 2029."

## Why India's Maths Community Should Pay Attention

India's relationship with pure mathematics is older than most nations. Srinivasa Ramanujan's notebooks, scrawled in a Madras boarding house a century ago, contained results so original that Cambridge professors spent decades verifying them. Today, the Indian Institutes of Technology produce more mathematics and computer science graduates per year than any system outside China, and a disproportionate share of senior researchers at OpenAI, DeepMind, Google Brain, and Meta AI hold IIT or ISI degrees.

These breakthroughs land squarely in their professional world. The Erdős problems aren't obscure puzzles — they're foundational questions in combinatorics, number theory, and discrete geometry that define research careers. When an AI solves one, it doesn't eliminate the mathematician. But it does change what the mathematician's job looks like.

Thomas Bloom at the University of Manchester demonstrated this within days. After seeing OpenAI's technique — using number theory to attack a geometry problem — Bloom and his team applied the same cross-domain strategy to disprove another Erdős conjecture, the sum-product problem, which had stood since 1976. "Once you know that something might be possible, you're willing to try harder to get it to work," he said.

This is the pattern that matters: AI as a scout, not a replacement. The model found a path that humans hadn't considered — bridging algebraic number theory and discrete geometry, two fields with "about as much in common as the marathon and pole vault," as the Wall Street Journal put it. Human mathematicians then followed the trail and pushed further.

## The IIT Pipeline Question

For the tens of thousands of Indian students preparing for JEE Advanced each year with dreams of a research career, these results raise a practical question: what skills will matter in a field where machines can generate proofs?

The answer, at least for now, is taste and direction. AI models are remarkably good at executing within a defined problem space. They're poor at choosing which problems matter. The researchers who prompted OpenAI's model made deliberate choices about framing — and the model's "breakthrough" came not from a eureka moment but from an exhaustive, patient combination of known techniques applied with a persistence no human would sustain.

Kevin Buzzard at Imperial College London noted that "the ideas to produce the counterexample were already in the literature — it takes some ingenuity to put them together." The ingenuity, in this case, was computational rather than conceptual. For Indian mathematicians trained in rigorous proof traditions, the opportunity is in learning to direct these tools rather than compete with them.

## What Comes Next

Hassabis's revised AGI timeline — 2029 — is aggressive but no longer absurd. AlphaProof Nexus's ability to work across graph theory, optimisation, algebraic geometry, and quantum optics suggests that mathematical reasoning may be the domain where AI makes the fastest progress, precisely because correctness is verifiable.

For NRI researchers at these labs, the next few years will determine whether AI-assisted mathematics becomes a genuine field or a novelty. The early evidence — human teams building on AI-generated proofs within days of their publication — suggests the former.

Ramanujan worked alone in Madras with little formal training and no computational tools. A century later, his intellectual descendants in Mountain View and London have tools that would have seemed miraculous to him. The question is no longer whether AI can do mathematics. It's whether mathematicians are ready to let it."""
    },
]

# Verify images and publish
for art in articles:
    img = verify_image(art["image_url"])
    if img:
        art["image_url"] = img
        print(f"  ✅ Image verified: {img[:80]}...")
    else:
        print(f"  ⚠️ Image failed verification, keeping URL anyway: {art['image_url'][:80]}...")

    try:
        sb_post("p2_articles", art)
        print(f"✅ Published: {art['slug']}")
        print(f"   Title: {art['headline']}")
    except Exception as e:
        print(f"❌ Failed: {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles processed.")
