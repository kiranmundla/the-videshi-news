#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-07 09:00 UTC run"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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


# ── Article 1: AMD-Samsung 2nm ──────────────────────────────────────────

art1_body = """Lisa Su has a supply problem, and Samsung just became her Plan B.

AMD is in advanced talks with Samsung Foundry to manufacture its next-generation EPYC Venice server CPUs on Samsung's 2nm SF2 process node, according to a report by South Korean outlet Sedaily. The two companies plan to finalise the contract around January 2027 after evaluating whether Samsung's process can meet AMD's performance demands. Industry sources quoted by Sedaily say production is "likely."

The move would mark AMD's first significant departure from its near-exclusive reliance on TSMC for cutting-edge chips. AMD was among the first customers to tape out on TSMC's N2 nanosheet technology — Lisa Su and TSMC chairman C.C. Wei held up a plaque commemorating the milestone at an event late last year. But TSMC's 2nm lines are now massively oversubscribed. Apple, NVIDIA, Qualcomm, and MediaTek all want capacity on the same node, and there simply isn't enough to go around.

## Why Samsung, why now

Samsung Foundry has spent years as the semiconductor industry's perpetual runner-up. Its 3nm gate-all-around process launched before TSMC's but suffered from poor yields that drove customers away. The Korean giant's foundry division reported operating losses through most of 2024 and 2025.

But momentum has shifted. Samsung has secured fresh contracts with Apple for certain chip lines and with Tesla for autonomous driving processors. Its 2nm SF2 node reportedly shows a 12 per cent performance improvement and 25 per cent power efficiency gain over its 3nm predecessor. The industry estimates Samsung's 2nm yield sits below 30 per cent today — compared to TSMC's roughly 60 per cent — but the trajectory is improving fast enough to attract serious customers.

For AMD, the calculus is straightforward. EPYC Venice is a data centre CPU designed for the AI infrastructure buildout that is consuming every available transistor on the planet. If TSMC cannot guarantee enough 2nm wafer starts, AMD either finds a second source or watches NVIDIA and Broadcom eat into its server market share while it waits in line.

## The Indian engineer's stake in this fight

This matters to the Indian diaspora for reasons that go beyond the stock ticker. AMD employs thousands of Indian engineers across its design centres in Austin, San Jose, and Hyderabad. The Hyderabad centre alone handles critical work on EPYC processor design and verification. A dual-sourcing strategy adds complexity — different foundry processes mean different design rules, different verification cycles, and potentially different teams handling each variant.

For Indian semiconductor professionals, the AMD-Samsung deal also redraws the career map. Samsung's renewed competitiveness means its own chip design ecosystem in India — Samsung Semiconductor India Research in Bengaluru employs over 3,000 engineers — could see expanded mandates. If Samsung wins AMD's business, its India R&D teams may inherit new verification and characterisation work.

Then there is the India Semiconductor Mission angle. India has bet heavily on the TSMC ecosystem through its partnerships with Tata Electronics at Dholera. But Samsung has its own India ambitions — its Noida facility already manufactures smartphones, and the company has signalled interest in semiconductor packaging in India. A world where Samsung Foundry is competitive again is a world where India has more than one patron to court for its chip manufacturing dreams.

## What to watch

The contract decision expected in January 2027 will be the proof point. If Samsung's 2nm yields reach the 60 per cent threshold that TSMC has already crossed, the deal likely closes. If they stall in the 30–40 per cent range, AMD stays with TSMC and Samsung's foundry revival remains aspirational. For the thousands of Indian engineers designing the chips that power every cloud data centre on the planet, the outcome will shape whether they are working with one foundry partner or two — and whether India's own chip ambitions have a second suitor at the door.
"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "AMD Is Shopping Samsung for Its Next Server Chips. TSMC Can't Make Them Fast Enough.",
    "subheadline": "Lisa Su's dual-sourcing gambit for 2nm EPYC Venice CPUs could reshape the foundry landscape — and give India's chip ambitions a second suitor.",
    "slug": make_slug("amd-samsung-2nm-epyc-venice-tsmc-supply-crunch"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Thousands of Indian engineers at AMD Hyderabad design EPYC processors; Samsung's foundry revival could expand India R&D mandates and give India Semiconductor Mission a second foundry partner beyond TSMC.",
    "tags": ["semiconductors", "amd", "samsung", "tsmc", "chip-manufacturing", "indian-engineers"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Sedaily (South Korea)", "url": "https://www.sedaily.com"},
        {"name": "WCCFTech", "url": "https://wccftech.com/samsung-is-in-talks-with-amd-to-supply-a-2nm-process/"},
        {"name": "DIGITIMES Asia", "url": "https://www.digitimes.com"},
        {"name": "Zacks Investment Research", "url": "https://www.zacks.com"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/SXSW-2024-alih-OB7A0861-Lisa_Su_%28cropped_2%29.jpg/1280px-SXSW-2024-alih-OB7A0861-Lisa_Su_%28cropped_2%29.jpg",
    "image_caption": "AMD CEO Lisa Su at SXSW 2024",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
    "is_editorial": False
}


# ── Article 2: DeepSeek US Corporate Adoption ──────────────────────────

art2_body = """The cheapest AI model in the market just became the fastest-growing enterprise software vendor in America. And it is Chinese.

DeepSeek, the Hangzhou-based AI startup, topped Ramp's June 2026 list of trending software vendors — a ranking that tracks first-time corporate purchases across Ramp's platform of thousands of US businesses. The significance is not in the absolute numbers, which remain tiny. It is in the direction: American companies are now paying DeepSeek directly, routing corporate data through China-hosted servers, because Silicon Valley's AI bills have become too high to ignore.

## The numbers behind the shift

Context matters. Ramp's April 2026 AI Index showed Anthropic and OpenAI commanding 34.4 per cent and 32.3 per cent adoption among its business users, respectively. DeepSeek sat at 0.1 per cent. Trending does not mean dominant — it means accelerating from a low base.

But "trending" on Ramp means new money flowing in a new direction. Ara Kharazian, lead economist at Ramp Economics Lab, flagged the shift as unprecedented. "In probably the biggest sign that companies are looking for cheaper alternatives to OpenAI and Anthropic, some are willing to use cheaper, Chinese models, sending US data back and forth from China-hosted servers," Kharazian said.

This is not companies self-hosting DeepSeek's open-weight models behind their own firewalls. That would be the cautious play. These are direct payments to DeepSeek's cloud API, which means prompts, documents, and source code leaving American networks for servers governed by PRC data laws. DeepSeek's own terms of service are explicit: "To provide you with our services, we directly collect, process, and store your Personal Data in the People's Republic of China."

## Why this matters for Indian tech workers

The AI cost crunch that is pushing some companies toward DeepSeek is the same force reshaping employment at the companies Indian engineers work for in disproportionate numbers. OpenAI employs hundreds of Indian-origin researchers and engineers. Anthropic's safety and alignment teams include prominent Indian AI scientists. If enterprise customers start splitting budgets between American and Chinese AI providers, the revenue that funds those jobs grows more slowly.

For Indian IT services companies — TCS, Infosys, Wipro, HCL Tech — the DeepSeek question is more immediate. These firms are embedding AI into thousands of client projects. A client that asks its IT vendor to integrate DeepSeek instead of GPT-4 is asking for a fundamentally different risk calculus. Data residency provisions in Indian IT contracts were already complex; adding a Chinese AI provider with PRC data laws makes compliance an order of magnitude harder.

DeepSeek's rise also intersects with India's own AI ambitions. The company's open-weight models — V3 and R1 — have already been downloaded millions of times, including by Indian startups building localised AI applications. Sarvam AI, Krutrim, and other Indian foundation model companies have studied DeepSeek's mixture-of-experts architecture closely. If DeepSeek can build frontier-class models at a fraction of American costs, it validates the thesis that you do not need $10 billion in compute to compete in AI — a thesis that Indian AI companies need to be true.

## The $7.4 billion war chest

DeepSeek is reportedly raising $7.4 billion in its first external funding round at a valuation between $52 billion and $59 billion, with Tencent, CATL, NetEase, and JD.com among investors. That capital could fund the infrastructure needed to serve enterprise customers at scale — and at prices that American AI companies cannot match without cutting margins they have barely started earning.

The security establishment has noticed. Multiple US government agencies have already banned DeepSeek from government devices. The question is whether the private sector, driven by quarterly budget pressures, will exercise the same caution. For Indian engineers building AI products on American platforms, and for Indian IT firms advising Fortune 500 clients on AI strategy, the answer to that question shapes the next five years of their business.
"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "DeepSeek Just Topped America's Fastest-Growing Software List. The Security Implications Are Enormous.",
    "subheadline": "US companies are routing corporate data through Chinese servers to cut AI costs. Indian engineers and IT firms are caught in the crossfire.",
    "slug": make_slug("deepseek-trending-us-corporate-ai-data-security-indian-tech"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian engineers at OpenAI/Anthropic face revenue pressure as clients explore cheaper Chinese alternatives; Indian IT services firms (TCS, Infosys, Wipro) must navigate data residency risks when clients request DeepSeek integration; Indian AI startups studying DeepSeek's cost-efficient architecture.",
    "tags": ["deepseek", "ai", "data-security", "china", "indian-it-services", "openai"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "TechRepublic", "url": "https://www.techrepublic.com/article/news-us-firms-try-deepseek-ai-costs-rise/"},
        {"name": "9to5Mac Security Bite", "url": "https://9to5mac.com"},
        {"name": "Ramp AI Index", "url": "https://ramp.com"},
        {"name": "South China Morning Post", "url": "https://www.scmp.com"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/60504/security-protection-anti-virus-software-60504.jpeg",
    "image_caption": "Digital security interface symbolising the data privacy risks of Chinese AI adoption",
    "image_attribution": "Pexels",
    "body": art2_body.strip(),
    "is_editorial": False
}


# ── Article 3: Foxconn Record Revenue / AI Pivot ───────────────────────

art3_body = """The company that built its empire assembling iPhones now earns more from building AI servers. And the gap is widening every month.

Foxconn — formally Hon Hai Precision Industry — posted record May revenue of NT$859.4 billion (roughly $27.2 billion), a 39.57 per cent jump from the same month last year. The previous May record, set in 2025, was NT$615.7 billion. For the first five months of 2026, accumulated revenue hit NT$3.82 trillion, up 31.79 per cent year-over-year — another all-time high. The company has raised its full-year 2026 revenue target to NT$11 trillion ($350.5 billion).

The driver is not phones. It is AI racks.

## The AI server pivot, by the numbers

AI servers now account for roughly 40 per cent of Foxconn's Cloud and Networking Products segment revenue, making them a larger contributor than smartphone assembly. The company holds over 40 per cent of the global AI server market and expects AI server rack shipments to more than double over the course of 2026.

Foxconn's language in its latest earnings release is unusually direct for a company that refuses to give numeric guidance: "AI racks are expected to maintain a continued growth trend. Based on current visibility, Q2 performance is tracking well above the previously anticipated growth." In Foxconn's restrained corporate vocabulary, "well above" is the equivalent of shouting.

The momentum extends beyond internal manufacturing. At Computex 2026 in Taipei, Foxconn announced a collaboration with Intel to develop next-generation AI infrastructure and computing platforms. Separately, it struck a deal with SK Group to explore joint development of AI servers, data centre solutions, and energy infrastructure. Both partnerships position Foxconn not merely as a contract manufacturer but as an AI infrastructure integrator — the company that turns purchase orders from Microsoft, Google, and Amazon into the physical hardware that runs the world's largest language models.

## India's manufacturing stake

Foxconn's AI pivot has a direct India dimension. The company operates massive manufacturing complexes in Sriperumbudur (Tamil Nadu) and Bengaluru, primarily assembling iPhones for Apple. It has committed to expanding Indian operations significantly — a planned $1.5 billion electronics manufacturing cluster in Karnataka and additional investments in Telangana are in various stages of approval.

As AI server assembly becomes Foxconn's fastest-growing business, the question of whether India gets a share of that manufacturing shifts from theoretical to urgent. Foxconn's AI racks require different skills from smartphone assembly — precision cooling systems, high-density power delivery, fibre optic integration — but the fundamental manufacturing disciplines overlap. India's abundant engineering talent, lower labour costs, and existing Foxconn infrastructure make it a logical candidate for AI server assembly lines, particularly as US-China trade tensions push diversification.

For NRI investors, Foxconn's pivot matters because it reshapes the investment thesis for the entire Apple-NVIDIA supply chain. Foxconn is not publicly traded on US exchanges, but its fortunes directly affect Apple (its largest customer) and NVIDIA (whose server platforms Foxconn assembles). The company is already positioned as a key manufacturing partner for NVIDIA's upcoming Vera Rubin generation of AI supercomputing platforms. When cloud hyperscalers place their next round of infrastructure orders — and cloud capex is projected to exceed $725 billion in 2026 — Foxconn is the company that turns those purchase orders into physical servers.

## The integrator trap

The risk, as analysts have noted, is the classic integrator's dilemma. Foxconn can grow quickly, stay strategically important, and still earn only modest margins if the real profit sits in silicon (NVIDIA), software (Microsoft), or proprietary system design (Google). Assembly is a lower-margin business than design, no matter how sophisticated the assembly becomes.

But Foxconn's Computex partnerships suggest it is aware of the trap. Collaborating with Intel on "next-generation AI infrastructure" and with SK Group on "energy solutions" signals ambitions beyond closing the box. If Foxconn can own more of the rack-level design and deployment stack, it moves from manufacturer to AI builder. Its May revenue numbers suggest the market is already paying for that bet.
"""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Foxconn Now Makes More Money From AI Servers Than iPhones. Its May Revenue Broke Every Record.",
    "subheadline": "The world's largest electronics manufacturer posted a 40 per cent revenue surge on AI rack demand — and India's manufacturing ambitions are next in line.",
    "slug": make_slug("foxconn-record-may-revenue-ai-servers-india-manufacturing"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Foxconn's India manufacturing expansion could extend to AI server assembly; NRI investors track the Apple-NVIDIA supply chain that Foxconn anchors; India's engineering talent pool positions it for AI infrastructure manufacturing.",
    "tags": ["foxconn", "ai-infrastructure", "nvidia", "india-manufacturing", "server-racks", "apple"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "CoinCentral", "url": "https://coincentral.com"},
        {"name": "Seeking Alpha", "url": "https://seekingalpha.com"},
        {"name": "Crypto Briefing", "url": "https://cryptobriefing.com"},
        {"name": "AInvest", "url": "https://ainvest.com"}
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg",
    "image_caption": "Server racks in a modern data centre, the type of AI infrastructure driving Foxconn's record revenue",
    "image_attribution": "Pexels",
    "body": art3_body.strip(),
    "is_editorial": False
}


# ── Publish ─────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
