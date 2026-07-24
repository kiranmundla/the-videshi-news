#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-27 17:00 PDT batch"""
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
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        return r.status_code == 200 and "image" in ct and cl > 5000
    except Exception:
        return False

# ── ARTICLE 1 ────────────────────────────────────────────────────────────────
art1_image = "https://upload.wikimedia.org/wikipedia/commons/0/0e/F20250904AH-2824_%2854778373111%29_%283x4_cropped_on_Zuckerberg_following_the_rule_of_thirds%29.jpg"

art1_body = """Meta began cutting 8,000 jobs on May 20 — its largest single layoff since the Year of Efficiency bloodletting of 2022-23. India was not spared. Product teams, ad sales, marketing, and individual contributor roles across Meta's Indian operations received early-morning termination emails, some as early as 4 a.m. local time. Severance packages ranged between four and six months. There was little warning and no prior discussion.

The cuts represent roughly 10 percent of Meta's global workforce. Another 6,000 open positions were eliminated before anyone could fill them, making the net contraction closer to 14,000 roles — about 17 percent of the headcount Meta would have had if fully staffed.

## The AI reallocation machine

This is not a simple downsizing. Alongside the cuts, Meta is moving approximately 7,000 employees into newly created AI-focused divisions, including teams named Applied AI Engineering, Agent Transformation Accelerator, and Central Analytics. Chief People Officer Janelle Gale outlined the restructuring in an internal memo.

Meta's finance chief Susan Li told analysts the company has "continued to underestimate compute needs even as we have been ramping capacity significantly." When asked about target headcount, she was blunt: "We don't really know what the optimal size of the company will be in the future."

That admission is worth pausing on. A company with nearly 80,000 employees and a projected capital expenditure budget of $125 to $145 billion in 2026 — more than double its 2025 outlay — cannot forecast how many humans it needs.

## Why Indian tech workers should care

Meta's India operations serve as a critical hub for ad technology, content moderation, and product development. The restructuring is not limited to headcount reduction — internal teams are being consolidated under leaner reporting structures as Meta pushes for AI-led operational efficiency. Hierarchy layers are being flattened, management tiers eliminated.

For the tens of thousands of Indian professionals working at FAANG companies on H-1B visas, the signal is unmistakable. Meta is not an outlier. The tech industry has already eliminated approximately 110,000 jobs across 137 companies in 2026, nearly matching the 125,000 cuts recorded across all of 2025. LinkedIn disclosed hundreds of Bay Area job cuts just one day before Meta's round.

H-1B holders who lose their positions face a 60-day grace period to find new employment or leave the country. In a market where hiring has slowed and AI is reshaping which roles companies even want, that window feels increasingly narrow.

## The $145 billion question

In his internal memo, Zuckerberg acknowledged employee frustration. He said Meta "currently does not intend to conduct additional company-wide layoffs in 2026." But targeted cuts have already landed on Reality Labs and at least five other divisions earlier this year. The distinction between company-wide and targeted leaves considerable room.

Meanwhile, over 1,500 employees signed an internal petition objecting to company systems designed to collect employee activity data for AI training purposes. The irony is thick: the workers building the AI infrastructure may themselves be training their replacements.

For Indian American families who moved continents for Big Tech careers, the calculus is shifting. The question is no longer whether AI will change their jobs. It is whether their employers have the imagination to grow with it — or just the spreadsheet to shrink."""

# ── ARTICLE 2 ────────────────────────────────────────────────────────────────
art2_image = "https://images.pexels.com/photos/36706459/pexels-photo-36706459.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"

art2_body = """India now has 27 million developers building on GitHub — and the number is accelerating. More than two million developers joined the platform from India in the first months of 2026 alone, accounting for one in every seven new developers globally. No other country comes close to that growth rate.

The milestone, announced by GitHub in April, confirms what Microsoft CEO Satya Nadella predicted late last year: India is on track to become the world's largest developer community. Nadella projects 57.5 million Indian developers by 2030, overtaking the United States in raw numbers for the first time.

## More than headcount

The scale is striking, but the composition matters more. India is now the world's largest open-source contributor base and the second-largest source of open-source contributions overall, behind only the United States. Indian developers have made more than 7.5 million contributions to open-source AI projects on GitHub, making the country the second-largest contributor to open-source AI globally.

What makes this particularly interesting is that India is no longer just contributing labour to other people's projects. Homegrown open-source technologies — Hyperswitch (payments), ERPNext (enterprise resource planning), ToolJet (low-code platforms), and Bruno (API testing) — have achieved global adoption. These are not weekend experiments. They are production-grade tools used by engineering teams worldwide.

## The GitHub Copilot effect

The growth is inseparable from AI tooling. More than 77,000 organisations globally have adopted GitHub Copilot, and Indian developers are among its most active users. TypeScript and Python — both languages central to AI development — lead India's growth on the platform.

GitHub CEO Thomas Dohmke has been unusually direct about India's trajectory. "The convergence of talent and AI tech will make India a powerhouse of AI," he said, noting that India produces roughly 200,000 computer science graduates annually — a pipeline no other country can match at scale.

## What this means for the diaspora

For Indian Americans working in Silicon Valley, this is both validation and competition. The talent pipeline they once represented — IIT graduates heading west on H-1B visas to write code at FAANG companies — is being replicated at massive scale inside India itself.

Indian GCCs (Global Capability Centres) already employ over a million professionals across hundreds of multinational companies. As AI tools flatten the productivity gap between a developer in Bengaluru and one in Mountain View, the case for paying Bay Area salaries weakens. Reuters reported this week that GCC hiring is slowing as companies "hire fewer people, just as a matter of abundant caution" in the AI era.

For NRI investors, the story is more bullish. India's developer density — combined with low-cost infrastructure, English fluency, and now AI-native tooling — makes it the most attractive global talent market for any technology company not named the United States. Freshworks, Zoho, and BrowserStack have already proved the model. The next wave of Indian-built global SaaS companies will be built by this 27-million-strong army.

The question for diaspora professionals is no longer whether India can compete in software. It is whether the career moat they built by moving West still holds — or whether the 27 million back home have washed it away."""

# ── ARTICLE 3 ────────────────────────────────────────────────────────────────
art3_image = "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg"

art3_body = """Amazon cited AI efficiency when it eliminated 16,000 corporate roles. Microsoft invoked AI when it cut more than 15,000 positions. Across Big Tech, the explanation for layoffs has become almost reflexive: we are doing more with less, and AI is why.

Jensen Huang has a problem with that story. And he said so plainly.

In an interview with Singapore broadcaster CNA on May 26, the Nvidia CEO pushed back directly on the practice of blaming artificial intelligence for job cuts. "I think the narrative that connects AI to job loss for many of the CEOs that are doing it, it is just too lazy," Huang said.

## The chronology argument

Huang's sharpest critique is not about AI's capabilities. It is about timing.

"AI has just arrived. How is it possible they're already losing jobs?" he asked. "How is it possible that AI became productive and useful only six months ago, and they were somehow laying people off two years ago because of AI?"

The logic is straightforward. Generative AI tools only became deployable at enterprise scale within the last year or two. If a company was reducing headcount before that window, attributing those cuts to AI is not an explanation — it is a reframing of older, less flattering decisions: cost pressure, over-hiring during cheap-capital years, or strategic pivots away from underperforming businesses.

At Nvidia's GTC conference earlier this year, Huang was even more pointed. Speaking with CNBC's Jim Cramer, he framed the issue as a leadership failure: "For companies with imagination, you will do more with more. For companies where the leadership is just out of ideas, they have nothing else to do."

## Why Huang is saying this now

The timing matters. Nvidia is the company selling the chips that power every major AI buildout. Its largest customers — Microsoft, Amazon, Google, Meta — are the same companies using AI to justify workforce reductions. Huang just publicly questioned their framing.

This is not altruism. It is strategic positioning. If executives keep overstating AI's role in layoffs and that narrative eventually collapses, it creates a credibility problem for the entire AI investment thesis — the thesis on which Nvidia's $5 trillion market capitalisation depends.

Huang also said he "really hates" the way some leaders use AI as a talking point while scaring employees. His advice to workers: "You're not losing your job to AI, but to someone who uses AI better." He predicted there will be more jobs in five years than today, comparing the current moment to the arrival of the personal computer.

## The Indian professional's dilemma

For Indian tech workers — both in the US and in India — Huang's comments land in a complicated space. The fear is real. The tech industry has already eliminated approximately 110,000 jobs in 2026 across 137 companies, and Indian professionals on H-1B visas are disproportionately concentrated in the companies doing the cutting.

But Huang's argument offers a useful counter-frame. If AI is not actually the cause of most layoffs — if the real causes are overcapacity, margin pressure, and lack of strategic vision — then the correct response is not to fear the technology but to become indispensable with it.

India's 27 million developers on GitHub, its booming GCC sector, and the pipeline of 200,000 CS graduates entering the workforce annually suggest the country is better positioned than most to ride this transition. The challenge for Indian Americans is whether their employers will use AI to grow or merely to shrink while calling it progress.

Huang is drawing a line: companies with imagination will hire more, not fewer. The question for every Indian engineer reading this is whether their company sits on the right side of that line — and what they plan to do if it does not."""


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Meta's 8,000 Layoffs Reach India. For H-1B Workers, the Clock Is Ticking.",
        "subheadline": "Product teams, ad sales, and marketing roles hit across India as Meta spends $145 billion on AI and asks whether it even knows how many humans it needs.",
        "slug": make_slug("meta-layoffs-india-h1b-ai-restructuring"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian professionals at Meta — both in India and on H-1B in the US — face an uncertain future as the company flattens hierarchies and redirects resources to AI. H-1B holders get 60 days to find new work or leave the country.",
        "tags": ["meta", "layoffs", "h-1b", "ai-restructuring", "india-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/meta-layoffs-hit-product-teams-in-india-as-ai-restructuring-flattens-org-hierarchy-99362.htm"},
            {"name": "AI Eating the World", "url": "https://www.aieatingtheworld.com/articles/meta-layoffs-2026-8000-jobs-cut-ai-restructuring"},
            {"name": "Business Review Live", "url": "https://businessreviewlive.com/meta-india-cuts-jobs/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": art1_image,
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Developer Army Hits 27 Million. The West Should Pay Attention.",
        "subheadline": "India now adds one in seven new developers globally, leads open-source AI contributions, and is on track to overtake the US by 2030. The talent pipeline that built Silicon Valley is being replicated at home.",
        "slug": make_slug("india-27-million-developers-github-open-source"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "The talent pipeline NRIs once represented — IIT grads heading west on H-1B — is being replicated at massive scale inside India. For diaspora professionals, it is both validation and competition for the career moat they built by moving West.",
        "tags": ["india-developers", "github", "open-source", "satya-nadella", "gcc"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Pune News / IANS", "url": "https://pune.news/technology/indias-developer-community-surges-to-27-million-on-github-434849/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/convergence-of-talent-and-ai-tech-will-make-india-a-powerhouse-of-ai-says-github-ceo-thomas-dohmke/article69512345.ece"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/india-gcc-model-shifts-cost-capability-as-ai-talent-strains-bite-2026-05-27/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": art2_image,
        "body": art2_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Jensen Huang Calls AI Layoff Excuses 'Lazy.' He Has a Point.",
        "subheadline": "The Nvidia CEO says companies blaming AI for job cuts are covering for bad strategy. For Indian tech workers caught in the crossfire, his argument matters.",
        "slug": make_slug("jensen-huang-ai-layoffs-lazy-excuse-nvidia"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian tech professionals on H-1B are disproportionately concentrated at the companies doing the cutting. Huang's counter-narrative — that AI should create more jobs, not fewer — offers both reassurance and a challenge to upskill.",
        "tags": ["nvidia", "jensen-huang", "ai-layoffs", "workforce", "silicon-valley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TheStreet", "url": "https://www.thestreet.com/employment/nvidias-ceo-has-a-blunt-message-on-ai-and-layoffs-in-2026-jensen-huang-layoffs-employments-jobs"},
            {"name": "Business Insider via CNA", "url": "https://www.businessinsider.com/nvidia-jensen-huang-ai-layoffs-lazy-ceos-2026"},
            {"name": "Fortune", "url": "https://fortune.com/2026/03/jensen-huang-ai-layoffs-imagination/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": art3_image,
        "body": art3_body,
    },
]

# Verify images before inserting
for art in articles:
    img = art["image_url"]
    if verify_image(img):
        print(f"✅ Image OK: {img[:80]}...")
    else:
        print(f"⚠️  Image check failed, keeping anyway: {img[:80]}...")

print()

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ Published: {art['slug']}")
        print(f"   → {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
