#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-28 15:00 UTC run"""
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

# Verify images before using
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return url
    except Exception:
        pass
    return None

# ── Image URLs ──
img_vera = verify_image("https://images.pexels.com/photos/17489157/pexels-photo-17489157.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940")
img_amd = verify_image("https://images.pexels.com/photos/34924856/pexels-photo-34924856.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940")
img_anthropic = verify_image("https://images.pexels.com/photos/8386437/pexels-photo-8386437.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940")

print(f"Image check — Vera: {'✅' if img_vera else '❌'}, AMD: {'✅' if img_amd else '❌'}, Anthropic: {'✅' if img_anthropic else '❌'}")

articles = [
    # ── ARTICLE 1: NVIDIA Vera CPU ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Nvidia's Vera CPU Is an ARM Chip That Outperforms Intel and AMD. Indian Engineers Helped Build It.",
        "subheadline": "The 88-core Olympus processor, purpose-built for agentic AI, has posted benchmark numbers that no ARM chip has ever matched — and thousands of Indian engineers in Bangalore and Pune contributed to its design.",
        "slug": make_slug("nvidia-vera-cpu-arm-agentic-ai-india-engineers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NVIDIA employs thousands of engineers across Bangalore, Pune, and Hyderabad — many of whom contributed to the Vera CPU architecture and its supporting software stack. For Indian chip designers weighing career moves, Vera signals that ARM-based data center processors are no longer a niche bet. And for NRI investors tracking NVIDIA, Vera opens a new $200 billion server CPU market opportunity on top of the GPU business.",
        "tags": ["nvidia", "vera-cpu", "arm", "agentic-ai", "semiconductors", "indian-engineers", "data-center"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "NVIDIA Newsroom", "url": "https://nvidianews.nvidia.com/news/nvidia-launches-vera-cpu-purpose-built-for-agentic-ai"},
            {"name": "Phoronix", "url": "https://www.phoronix.com/review/nvidia-vera-cpu-benchmarks"},
            {"name": "WCCFTech", "url": "https://wccftech.com/nvidia-vera-cpu-88-olympus-arm-cores-outperforms-amd-epyc-intel-xeon-first-benchmarks/"},
            {"name": "SiliconANGLE", "url": "https://siliconangle.com/2026/05/21/nvidia-reinvents-cpu-age-agentic-ai/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": img_vera or "",
        "body": """For two decades, the data center CPU market belonged to Intel and AMD. x86 was the architecture. Xeon and EPYC were the names that mattered. ARM chips were for phones, maybe the odd edge server, and the occasional thought experiment from analysts who liked to provoke.

That era may have just ended.

NVIDIA's Vera CPU — an 88-core, ARM-based processor designed from scratch for agentic AI — has posted its first independent benchmarks, and the numbers are striking. In Phoronix testing, Vera delivered 63% better performance than NVIDIA's own Grace CPU, and consistently outperformed both AMD EPYC and Intel Xeon processors across compilation, memory bandwidth, and AI inference workloads. No ARM chip has ever come close.

## Built for the Agent Era

Vera isn't trying to be a general-purpose processor. Jensen Huang's pitch is precise: as AI moves from simple question-and-answer chatbots to agents that plan, reason, run code, and call tools, the CPU orchestrating those workflows becomes the bottleneck. Vera is built to eliminate it.

The architecture reflects that focus. Each of the 88 custom Olympus cores supports NVIDIA's Spatial Multithreading — allowing two tasks per core for consistent performance in multi-tenant AI factories. The memory subsystem uses LPDDR5X to deliver 1.2 TB/s of bandwidth at half the power draw of conventional server DDR5. A single Vera rack can sustain more than 22,500 concurrent AI environments running independently at full performance.

The customer list reads like a who's-who of the AI industry: Anthropic, OpenAI, Meta, Oracle Cloud Infrastructure, ByteDance, Alibaba Cloud, CoreWeave, and Cloudflare are all deploying or planning to deploy Vera. Manufacturing partners include Dell, HPE, Lenovo, Supermicro, Foxconn, and a dozen Taiwanese ODMs.

## The India Connection

What the press releases don't mention is where much of this work happened. NVIDIA's India engineering centers — spanning Bangalore, Pune, and Hyderabad — employ thousands of engineers working on GPU architecture, CUDA software, networking, and now CPU design. India is not peripheral to NVIDIA's roadmap; it is embedded in it.

For the roughly 50,000 Indian-origin professionals working in semiconductor design across the United States and India, Vera carries a specific signal. ARM-based server processors are now a mainstream career path, not a speculative one. The skills required — low-power design, custom core architecture, high-bandwidth memory integration — are exactly what India's chip design ecosystem has been building for years through GCCs at Qualcomm, Intel, AMD, and Arm itself.

## What It Means for NRI Investors

NVIDIA's GPU dominance is well understood. But Vera opens a second front. The company estimates that server CPUs represent a $200 billion addressable market by 2027 — a market where it previously had zero share. If Vera captures even a fraction of that, NVIDIA's revenue diversification story changes materially.

The competitive implications are equally significant. Intel, already struggling with fabrication delays, now faces an ARM competitor with better benchmarks and a built-in ecosystem advantage — every Vera CPU is designed to pair seamlessly with NVIDIA GPUs through NVLink-C2C interconnects. AMD, despite strong EPYC momentum, must contend with the reality that its largest customers are also adopting Vera.

Vera is in full production and will ship through partners in the second half of 2026. For Indian engineers, investors, and the broader diaspora watching the chip industry reshape itself in real time, this is not a side story. It is the main event."""
    },
    # ── ARTICLE 2: AMD Lisa Su $10B Taiwan ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Lisa Su Says AI Is 'Still in the Third Inning.' AMD Is Betting $10 Billion on It.",
        "subheadline": "AMD's chair and CEO commits the company's largest-ever regional investment to Taiwan's semiconductor ecosystem — and warns the global CPU market is 'tight' with no relief in sight.",
        "slug": make_slug("amd-lisa-su-10-billion-taiwan-third-inning-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "AMD's India R&D centers in Hyderabad and Bangalore — with over 6,000 engineers — are deeply involved in EPYC server chip development and AI software optimization. Taiwan's supply chain health directly determines whether those engineers' work reaches production on schedule. For NRI investors, Su's 'third inning' thesis means the AI infrastructure buildout has years of runway left.",
        "tags": ["amd", "lisa-su", "taiwan", "semiconductors", "ai-chips", "tsmc", "chiplets"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CommonWealth Magazine", "url": "https://english.cw.com.tw/article/article.action?id=4795"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-spend-150-billion-year-taiwan-2026-05-28/"},
            {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/a20260527PD212.html"},
            {"name": "TechSpot", "url": "https://www.techspot.com/news/108234-amd-ceo-lisa-su-says-tsmc-chips-made.html"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": img_amd or "",
        "body": """Lisa Su does not do hyperbole. The AMD chair and CEO is an engineer by training and temperament — measured, data-driven, and allergic to the kind of breathless futurism that pervades Silicon Valley keynotes. So when she says the AI computing boom is "still in the third inning," it is worth taking seriously.

Speaking at a CommonWealth Magazine summit in Taipei last week, Su laid out AMD's biggest bet yet: more than $10 billion in co-investment with Taiwan's semiconductor ecosystem, spanning advanced packaging, substrates, test capacity, and rack-scale integration. It is the single largest regional commitment AMD has ever made.

## Why Taiwan, Why Now

The investment is not about sentimentality — Su's family roots trace to Tainan — but about industrial reality. "The only place in the world that has every part of the semiconductor ecosystem — from basic materials all the way to rack-scale manufacturing — is right here in Taiwan," Su told the audience.

The timing matters. AMD's newest server chip, Venice, has entered production ramp at TSMC's 2-nanometer process — the most advanced fabrication technology available anywhere. The company's flagship AI accelerator, the MI450, packs over 300 billion transistors across more than 20 chiplets. Both depend entirely on Taiwan's packaging and substrate supply chain.

And that supply chain is under pressure. Su warned that the global CPU market is "tight," with demand outpacing forecasts. Memory is in shortage. Power for data centers is constrained. "Together, we simply didn't quite predict demand to go up this fast," she acknowledged.

## The Chiplet Revolution

For non-engineers, Su offered a surprisingly clear explanation of why chiplets matter. Moore's Law — the principle that chips get smaller and cheaper over time — is slowing down. Instead of building one enormous chip that is difficult to manufacture, AMD cuts its processors into smaller pieces (chiplets) and reassembles them using advanced packaging.

"When I was getting my PhD, I honestly thought this kind of technology could never work," Su admitted. "It's amazing what the engineering capability of the entire industry ecosystem has been able to build."

The next frontier, she said, is integrating optics and photonic interconnects into chip systems — an area where India's growing photonics research community, particularly at IISc Bangalore and IIT Madras, could play a meaningful role.

## What This Means for India's Chip Ambitions

AMD employs more than 6,000 engineers across Hyderabad and Bangalore, making India one of its largest R&D centers outside the United States. These teams work on EPYC server processor design, AI software optimization (including the ROCm open-source stack that competes with NVIDIA's CUDA), and verification — the painstaking process of ensuring chips work before they go to fabrication.

Taiwan's supply chain stability is not an abstract geopolitical concern for these engineers. It directly determines whether their designs reach production on time. AMD's $10 billion commitment is, in practical terms, an investment in the pipeline that connects India's design talent to the world's most advanced manufacturing.

For NRI investors watching the semiconductor sector, Su's "third inning" thesis carries a specific implication: the AI infrastructure buildout has years of runway remaining. AMD's stock has more than quadrupled in the past year, but Su is signaling that the company — and the industry — are far from the late innings where returns plateau.

## US-Made Chips Will Cost More

One additional data point Su disclosed: chips manufactured at TSMC's new Arizona facilities will cost 5 to 20 percent more than their Taiwan-produced equivalents. She called the premium "worth it" for supply chain resilience, but the cost gap underscores why Taiwan remains the center of gravity — and why AMD just committed $10 billion to keep it that way.

Whether you are an Indian chip designer in Hyderabad working on next-generation EPYC silicon, a Bay Area engineer at AMD's Santa Clara headquarters, or an NRI investor trying to gauge how much AI infrastructure spending has left to run, Su's answer is the same: we are in the third inning, and the game is far from over."""
    },
    # ── ARTICLE 3: Anthropic Pentagon Standoff ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic Refused to Let the Pentagon Use Its AI for Mass Surveillance. Now It's Blacklisted.",
        "subheadline": "The standoff between the AI safety company and the U.S. Department of Defense — with a May 31 deadline looming — has become the most consequential AI governance fight in years. Indian AI researchers are watching closely.",
        "slug": make_slug("anthropic-pentagon-supply-chain-risk-ai-safety"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Anthropic employs a significant number of Indian-origin AI researchers and engineers, many on H-1B visas, who face direct career uncertainty from the standoff. The case also sets precedent for how AI companies can resist government overreach — a question that matters deeply as India drafts its own AI governance framework. For Indian tech workers choosing between AI labs, the ethics-vs-government-contracts tradeoff just became very real.",
        "tags": ["anthropic", "pentagon", "ai-safety", "ai-governance", "defense", "h1b", "claude"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Venable LLP", "url": "https://www.venable.com/insights/publications/2026/03/pentagons-anthropic-supply-chain-risk-dec"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/anthropics-courtroom-clash-with-pentagon-puts-ai-guardrails-on-trial/"},
            {"name": "Seeking Alpha / Bloomberg", "url": "https://seekingalpha.com/news/4475123-under-secretary-emil-michael-says-anthropic-pentagon-talks-have-stopped"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/musk-says-spacex-did-not-commit-long-term-colossus-lease-anthropic-2026-05-27/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": img_anthropic or "",
        "body": """On March 5, 2026, the U.S. Department of Defense did something it had never done to an American technology company: it designated Anthropic — the maker of Claude, one of the world's most capable AI models — as a "supply chain risk to national security."

The label, historically reserved for foreign adversaries like Huawei, effectively bars the Pentagon and its contractors from doing business with Anthropic. President Trump went further, directing every federal agency to immediately cease using the company's technology. The GSA pulled Anthropic from government procurement platforms. And Under Secretary of Defense Emil Michael recently confirmed that negotiations between the two sides have stopped entirely.

The catalyst was deceptively simple. Anthropic refused to remove safety guardrails that prevent Claude from being used for mass domestic surveillance and autonomous weapons systems. The Pentagon wanted unrestricted access. Anthropic said no. Defense Secretary Pete Hegseth gave the company until 5:01 PM on a Friday to agree. It didn't.

## The Legal Battle

Anthropic sued in March, calling the designation "unprecedented" and "legally unsound." The case was argued May 19 before a three-judge panel of the D.C. Circuit Court, with at least one judge expressing deep skepticism about the government's legal theory.

The core legal question is whether a supply chain risk designation under 10 U.S.C. § 3252 — a statute designed to protect military systems from foreign interference — can be applied to a domestic company over a commercial disagreement about terms of use. Anthropic argues it cannot. The government insists it is protecting national security.

A federal judge has issued a temporary injunction pausing the designation, but the underlying dispute remains unresolved. A Polymarket prediction contract pegged to a May 31 deadline for resolution traded at just 3% probability of the designation being removed — suggesting bettors expect this fight to drag on.

## The Competitive Fallout

While Anthropic litigates, its competitors have moved aggressively. OpenAI secured a classified network deployment deal within hours of Anthropic's blacklisting. Microsoft, NVIDIA, and SpaceX have all signed new defense AI contracts. Google and xAI are also engaged.

The irony is thick. Anthropic was founded by former OpenAI researchers who left specifically because they believed AI safety was not being taken seriously enough. Now that commitment to safety has cost the company its government business — while competitors who adopted more permissive terms have expanded theirs.

Elon Musk added a twist last week, revealing that SpaceX had only agreed to a 180-day lease of its Colossus AI training clusters to Anthropic, not the multi-year commitment previously reported. "If compute gets super tight I said we might need it back at some point," Musk wrote on X.

## Why Indian AI Workers Should Care

This is not merely a Washington policy fight. Anthropic employs a significant number of Indian-origin AI researchers and engineers, many on H-1B visas. Company instability — loss of government revenue, regulatory uncertainty, reputational risk — directly affects their immigration status. Under current rules, an H-1B holder who loses their job has 60 days to find a new employer or leave the country.

More broadly, the Anthropic standoff is setting precedent for the relationship between AI companies and governments worldwide. India is actively drafting its own AI governance framework, and the question of whether a company can refuse to remove safety guardrails from military applications is directly relevant. If the U.S. government can blacklist a domestic AI company for maintaining ethical boundaries, what leverage do companies have anywhere?

For Indian AI professionals choosing between labs — Anthropic versus OpenAI versus Google DeepMind versus Meta AI — the calculus has shifted. Anthropic's principled stand has earned admiration in the research community but created material career risk. OpenAI's pragmatic approach has secured government contracts but drawn criticism from safety researchers. There is no comfortable middle ground.

## The Bigger Picture

The Anthropic-Pentagon standoff is, at bottom, a fight about who controls the most powerful technology of the era. The government wants unrestricted access to frontier AI. One company said no. The consequences of that refusal — for Anthropic, for the AI industry, and for the thousands of Indian-origin professionals building these systems — are still unfolding.

The May 31 deadline on Polymarket may pass without resolution. But the question it represents will not. Every AI company, every AI researcher, and every government writing AI policy is now watching to see whether saying no to the Pentagon is something a company can survive."""
    },
]

for art in articles:
    if not art["image_url"]:
        print(f"⚠️  No valid image for {art['slug']} — publishing without image")
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
