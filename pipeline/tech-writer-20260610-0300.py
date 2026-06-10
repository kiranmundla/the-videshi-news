#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-10 03:00 UTC batch"""

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

def validate_image(url):
    """Verify image URL returns HTTP 200 with Content-Type image/* and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {url[:80]}... ({cl} bytes)")
            return True
        else:
            print(f"  ✗ Image failed: status={r.status_code}, ct={ct}, cl={cl}")
            return False
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# ARTICLE 1: xAI Distilling Claude
# ─────────────────────────────────────────────────────────────

art1_headline = "Musk's xAI Got Caught Training on Claude's Outputs. It Kept Going Anyway."
art1_subheadline = "The Information reveals months of covert model distillation — through personal accounts, third-party proxies, and a team in freefall. For Indian AI engineers, the fight over synthetic data just got personal."

art1_body = """When Anthropic revoked xAI's access to Claude in January 2026, the story should have ended there. A competitor's terms of service were breached, the plug was pulled, and the industry moved on.

It didn't.

According to a detailed investigation by The Information's Grace Kay, xAI engineers continued extracting Claude's outputs for months after the cutoff — routing requests through personal subscriber accounts, and when those were banned, through an intermediary service called Blackbox AI. The goal was model distillation: training Grok's coding models on Claude's superior outputs, essentially teaching a weaker student by copying a stronger teacher's homework.

## The Three-Phase Operation

The operation unfolded in three acts. In Phase 1, xAI engineers used official enterprise API access to scrape Claude's responses as training data. Anthropic identified the pattern and shut it down. xAI co-founder Tony Wu acknowledged the block in an internal memo, framing it as both "bad and good news" that would "push us to develop our own coding product."

Phase 2 saw engineers pivot to personal Claude accounts — a move that violated Anthropic's terms of service at an individual level. Anthropic detected the anomalous traffic signatures and executed targeted bans.

Phase 3 involved routing through Blackbox AI, a third-party coding tool that itself uses Claude under the hood. It was distillation through an intermediary, one more layer of indirection in a cat-and-mouse game that exposed just how valuable Claude's reasoning had become.

## A Team Under Pressure

The desperation makes more sense when you look inside xAI. The pretraining team had shrunk to fewer than five people. Four Grok code leads departed within months, along with several co-founders. In one incident, an employee accidentally deleted critical training data, setting the project back two to three weeks.

Meanwhile, Musk's compute empire was being rented out — to Anthropic via SpaceX, and to Google — rather than being used to train xAI's own models. The company that loudly positioned itself as a frontier AI challenger was, behind the scenes, struggling to keep its coding models competitive without borrowing from a rival.

## Why This Matters to Indian Engineers

This isn't just a Silicon Valley boardroom drama. Thousands of Indian-origin engineers work at both xAI and Anthropic, and across the broader AI ecosystem. The fight over model distillation is really a fight over who owns the intellectual output of AI systems — a question that directly affects engineers who build, fine-tune, and deploy these models.

Anthropic has already disclosed detecting "industrial-scale distillation attacks" involving over 24,000 fraudulent accounts and 16 million exchanges with Claude, many traced to Chinese labs including DeepSeek and Moonshot AI. The xAI case is different: a well-funded American competitor with ties to the current administration, doing the same thing under a friendlier flag.

For Indian AI startups building on top of frontier models, the precedent is chilling. If Musk's $50 billion company can't resist the temptation to distill a competitor's model, the pressure on smaller players will only intensify. And the enforcement mechanisms — terms of service, traffic monitoring, account bans — remain flimsy.

Elon Musk previously admitted in a legal proceeding that xAI "partially" used OpenAI models to train Grok, calling it "industry standard practice." Whether the courts and regulators agree will shape the rules of engagement for every AI company worldwide — including the growing cohort of Indian-founded labs racing to build their own frontier models.

The best evidence that your product works? A competitor secretly using it to train their own."""

art1_sources = [
    {"name": "The Information", "url": "https://www.theinformation.com/articles/how-xai-trained-grok-on-claude"},
    {"name": "The Decoder", "url": "https://the-decoder.com/elon-musks-xai-reportedly-trained-its-coding-models-on-claude-outputs-for-months-before-getting-cut-off/"},
    {"name": "Lapaas Voice", "url": "https://voice.lapaas.com/xai-reportedly-trained-its-coding-models-distilling-claude/"},
    {"name": "OpenTools", "url": "https://opentools.ai/news/xai-trained-its-coding-models-on-claude-outputs-for-months-before-getting-cut-off"}
]

art1_image = "https://upload.wikimedia.org/wikipedia/commons/5/5e/Elon_Musk_-_54820081119_%28cropped%29.jpg"

# ─────────────────────────────────────────────────────────────
# ARTICLE 2: Anthropic 80% Code + AI Pause Call
# ─────────────────────────────────────────────────────────────

art2_headline = "Claude Writes 80% of Anthropic's Code. The Company Wants a Pause Button Before It's Too Late."
art2_subheadline = "The $965 billion AI company says its own model now authors the vast majority of its production software. For five million Indian engineers, the implications are existential."

art2_body = """In May 2026, more than 80 percent of the code merged into Anthropic's production codebase was written not by human engineers, but by Claude — the company's own AI model. Engineers are now shipping eight times as much code per day as they did in 2024. One employee told the company he hadn't personally written a single line of code in five months.

The milestone, disclosed in a report titled "When AI builds itself," represents a transformation that Indian software professionals cannot afford to ignore.

## From Autocomplete to Author

Before Claude Code launched in research preview in February 2025, AI-authored code at Anthropic was in the low single digits. The jump to 80 percent — leadership estimates the total share, including scripts and experimental code, exceeds 90 percent — didn't happen because engineers became lazy. It happened because the tools got genuinely good.

Claude Code doesn't just suggest snippets. Its Dynamic Workflows spin up dozens to hundreds of parallel subagents that plan, execute, review, challenge, verify, and retry work before presenting results. Anthropic's showcase example: migrating the Bun JavaScript runtime from Zig to Rust — 750,000 lines of code, hundreds of coordinating agents, 99.8 percent of existing tests passing, done in 11 days.

The engineering role has shifted from writing code to directing it. Engineers choose projects, set architectural constraints, review generated changes, and decide what gets merged. The bottleneck moved from typing to judgment.

## The Pause Paradox

Here's where the story gets uncomfortable. Even as Anthropic celebrates Claude's coding prowess, its co-founder Jack Clark is publicly warning that the AI industry lacks a "brake pedal." In a widely circulated essay, Clark argues that AI systems are approaching the ability to improve themselves without human intervention — and that policymakers need mechanisms to slow development if things go wrong.

The company is simultaneously preparing for an IPO that could value it at nearly $1 trillion, having recently filed confidentially with the SEC. Its $965 billion post-money valuation, boosted by a $65 billion Series H round, now surpasses OpenAI's $852 billion.

Critics have not been kind. David Sacks, Donald Trump's former AI advisor, posted on X: "You compare it to nukes, threaten half of white-collar jobs, warn recursive self-improvement could end humanity, then race ahead anyway. You want the government to save us from... you." NYU's Gary Marcus called it "the most incredible, cost-free piece of rhetoric."

## What Five Million Indian Engineers Should Be Thinking

India produces roughly 1.5 million engineering graduates annually, and the IT services industry employs over five million. The traditional career ladder — learn a language, get placed at an IT services firm, grind through projects, climb to architect — was built on the assumption that writing code is hard, slow, and valuable.

That assumption just took a direct hit.

If one Anthropic engineer plus Claude can ship eight times the code, the arithmetic for bench-heavy IT services firms is brutal. TCS chairman N. Chandrasekaran recently said AI agents would eventually match his company's 500,000-person headcount. He framed it as a productivity unlock. The other framing is obvious.

The pivot isn't optional. Indian engineers who position themselves as AI directors — the people who set goals, architect systems, review AI-generated output, and make judgment calls — will thrive. Those who define their value by lines of code written will find that metric collapsing to zero, just as it already has at Anthropic.

The METR research lab reports that the length of tasks AI can reliably complete on its own has been doubling every four months. In March 2024, Claude handled four-minute tasks. By April 2026, it was managing twelve-hour tasks. The trajectory line doesn't bend.

Anthropic wants a pause button. Indian engineers need a pivot plan."""

art2_sources = [
    {"name": "Anthropic", "url": "https://www.anthropic.com/research/when-ai-builds-itself"},
    {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/ai/anthropic-says-ai-can-build-itself-asks-rivals-to-slow-down"},
    {"name": "AInvest", "url": "https://www.ainvest.com/news/anthropics-co-founder-warns-of-unchecked-ai-development-urges-policymakers-to-introduce-brake-pedal/"},
    {"name": "Fortune", "url": "https://fortune.com/2026/06/04/anthropic-openai-engineers-say-ai-writes-code/"}
]

art2_image = "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg"

# ─────────────────────────────────────────────────────────────
# ARTICLE 3: IISc Semiconductor Training Fab
# ─────────────────────────────────────────────────────────────

art3_headline = "India Just Opened a Semiconductor Training Fab. The Hard Part Is Filling It."
art3_subheadline = "President Murmu inaugurated IISc Bengaluru's clean room facility, part of a push to train 700 students a year. India's chip ambitions now depend on whether the talent pipeline can keep up with the factories."

art3_body = """President Draupadi Murmu virtually inaugurated a Semiconductor Training Fab Facility at the Indian Institute of Science (IISc) in Bengaluru last week — a 3,200-square-foot clean room equipped with lithography stations, a scanning electron microscope, and the kind of hands-on infrastructure that India's chip workforce desperately needs.

The facility, supported by the Ministry of Tribal Affairs, is designed to train around 700 students annually. It builds on IISc's existing semiconductor skilling programmes, which have already trained more than 1,400 participants from Scheduled Tribe communities, delivered over 48,000 hours of specialized instruction, and awarded more than 1,000 national skills certifications across 30 states and 273 institutions.

## The Workforce Gap Nobody Talks About

India's semiconductor story has been dominated by factory announcements: Tata Electronics in Dholera, Micron in Gujarat, CG Semi's OSAT facility, and the broader India Semiconductor Mission (ISM) with its ₹76,000 crore outlay. Four fabrication plants are expected to begin production in 2026.

But fabs without skilled operators are expensive paperweights.

"India's Semiconductor Mission is now in Phase Two," said the National Nanofabrication Facility's technology manager Salim, speaking at the inauguration. "The main idea of having a training fab is to cater to the requirements of building a workforce that can be utilized in the semiconductor industry. Even now, most colleges cover the theoretical aspect, but something that is needed for the industry is practical exposure."

That's a polite way of saying India's engineering colleges produce plenty of graduates who can explain how a transistor works on a whiteboard, but almost none who have operated a lithography machine or maintained a clean room environment. The gap between academic semiconductor education and factory-floor reality is measured in years of training.

## The Numbers Don't Add Up — Yet

The Union Budget 2026-27 allocated ₹1,000 crore for ISM 2.0, with a focus on domestic supply chains, indigenous equipment, and talent development. The government's roadmap targets 3-nanometre and 2-nanometre technology nodes by 2035, with the goal of meeting 70–75 percent of domestic chip demand by 2029.

NASSCOM estimates India will need roughly 300,000 semiconductor professionals by 2030. The Design Linked Incentive (DLI) Scheme has supported 24 semiconductor design startups and attracted nearly ₹430 crore in venture capital. But training 700 students a year at one facility — even a world-class one — barely scratches the surface.

The challenge is compounded by geography. Semiconductor talent isn't evenly distributed. Bengaluru, Hyderabad, and Noida have concentrations of chip design professionals, but the new fabs in Gujarat and Assam will need technicians and process engineers from regions with little existing semiconductor ecosystem.

## The NRI Angle: Come Home, But to What?

For the roughly 300,000 Indian-origin professionals working in the global semiconductor industry — at Intel, TSMC, Samsung, Qualcomm, and dozens of smaller firms — India's chip push is both an opportunity and a question mark.

The opportunity is real. Infineon's India operations are already moving beyond traditional engineering support into global ownership roles, driven by AI data center demand. India's NoPo Nanotechnologies is targeting the advanced materials gap in the chip supply chain. Tata's partnership with PSMC (Powerchip) for the Dholera fab is progressing.

The question mark is whether returning means a career upgrade or a step backward. Compensation gaps remain significant. The ecosystem outside Bengaluru is nascent. And the practical training infrastructure — the kind of facility IISc just opened — is still being built, not operating at scale.

## Beyond Silicon Dreams

India's semiconductor ambitions are credible in a way they weren't five years ago. The investments are real, the geopolitical tailwinds are strong (every chip not made in China is a chip the West wants made somewhere else), and the talent base in design is already globally competitive.

But the IISc training fab is a reminder that hardware ambitions require human infrastructure too. The clean room in Bengaluru can train 700 students a year. India needs to train 700 a week.

The factories are rising in Gujarat and Assam. The question is whether the people to run them will be ready when the machines are."""

art3_sources = [
    {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/president-inaugurates-semiconductor-training-fab-at-iisc-bengaluru/"},
    {"name": "AInvest", "url": "https://www.ainvest.com/news/india-semiconductor-growth-navigating-ai-adoption-and-global-competition/"},
    {"name": "DIGITIMES Asia", "url": "https://www.digitimes.com/news/a20250524PD210.html"},
    {"name": "NASSCOM Community", "url": "https://community.nasscom.in/communities/semiconductor/catalyzing-semicon-ecosystem"}
]

art3_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/IISc_2.jpg/1280px-IISc_2.jpg"

# ─────────────────────────────────────────────────────────────
# Validate images and assemble articles
# ─────────────────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": make_slug("xai-distilling-claude-grok-coding-models-anthropic"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian AI engineers work at both xAI and Anthropic; model distillation precedent affects Indian AI startups building on frontier models; IP ownership of AI-generated outputs is directly relevant to the Indian tech workforce",
        "tags": ["ai", "xai", "anthropic", "elon-musk", "model-distillation", "silicon-valley", "ip-ethics"],
        "urgency": "high",
        "sources": json.dumps(art1_sources),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art1_image,
        "image_caption": "Elon Musk, whose xAI was caught distilling Anthropic's Claude to train its own coding models",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body.strip()
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": make_slug("anthropic-claude-80-percent-code-ai-pause-indian-engineers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's 5M+ IT workforce faces existential pressure as AI-authored code crosses 80% at a frontier lab; TCS, Infosys hiring models under direct threat; engineers must shift from code writers to AI directors",
        "tags": ["ai", "anthropic", "claude", "software-engineering", "indian-it", "automation", "ipo"],
        "urgency": "high",
        "sources": json.dumps(art2_sources),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art2_image,
        "image_caption": "Dario Amodei, CEO of Anthropic, whose AI model now writes the majority of the company's production code",
        "image_attribution": "Wikimedia Commons",
        "body": art2_body.strip()
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art3_headline,
        "subheadline": art3_subheadline,
        "slug": make_slug("iisc-semiconductor-training-fab-india-chip-workforce"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "300,000 Indian-origin semiconductor professionals worldwide are evaluating return-to-India opportunities; training infrastructure gap is the key question for NRIs considering the move; India needs to scale from 700 trainees/year to 700/week",
        "tags": ["semiconductor", "india", "iisc", "workforce", "training", "chip-manufacturing", "nri"],
        "urgency": "medium",
        "sources": json.dumps(art3_sources),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art3_image,
        "image_caption": "The Indian Institute of Science (IISc) campus in Bengaluru, home to the new semiconductor training fab",
        "image_attribution": "Wikimedia Commons",
        "body": art3_body.strip()
    }
]

# Validate all images
print("Validating images...")
for art in articles:
    print(f"\n{art['slug']}:")
    if not validate_image(art["image_url"]):
        print(f"  ⚠ Image validation failed, proceeding anyway (URL is from Wikimedia)")

# Insert articles
print("\n\nInserting articles...")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
