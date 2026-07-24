#!/usr/bin/env python3
"""Tech writer — July 5, 2026 14:00 PT run. 3 articles."""

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

# ──────────────────────────────────────────────────────────────────────
# ARTICLE 1: Foxconn Q2 Revenue Surge
# ──────────────────────────────────────────────────────────────────────

foxconn_body = """Foxconn just posted the kind of quarter that makes the rest of the contract electronics industry look like it's running on dial-up. Revenue for the three months ending June hit T$2.513 trillion — roughly $78.7 billion — a 39.8 per cent jump over the same period last year and comfortably above analyst forecasts. June alone was a record-breaker for the month, surging 52.1 per cent year-on-year.

The engine, unsurprisingly, is artificial intelligence. Foxconn's cloud and networking division, which builds the AI server racks that Nvidia designs and the world's hyperscalers devour, posted what the company called "robust" growth. Smart consumer electronics — the segment that includes iPhones — contributed "significant" gains of its own. The combination made Foxconn's second quarter its strongest yet.

## The India Factor

But the story that matters most to the Indian diaspora is not what Foxconn built in Taiwan. It is what it is building in India.

The company has committed roughly $1 billion to expanding its Indian operations. Its factory complex in Sriperumbudur, near Chennai, now employs tens of thousands of workers and contributes nearly half of Apple's exports from the country. A second major facility near Bangalore's Devanahalli — a 300-acre site representing a ₹21,911 crore capital investment — began commercial iPhone shipments earlier this year. Apple CEO Tim Cook has confirmed that for the June quarter, a majority of iPhones sold in the United States were assembled in India.

And iPhones are only part of the picture. In February, Prime Minister Narendra Modi laid the foundation stone for an HCL-Foxconn semiconductor packaging plant in Jewar, Uttar Pradesh — a facility that would move Foxconn's India presence from final assembly into the deeper, higher-value layers of the chip supply chain.

## Why NRIs Should Pay Attention

Foxconn's pivot matters for three reasons. First, the company now holds roughly 40 per cent of the global AI server market and plans to invest $2–3 billion annually in AI infrastructure. As India builds out its own data centre capacity — the government just extended tax-free status for new data centres through 2047 — Foxconn's manufacturing footprint positions the country as a potential node in the global AI hardware supply chain, not just a consumer of it.

Second, the geographic diversification is a direct response to tariff and geopolitical risk. With US tariffs on Chinese goods exceeding 145 per cent on some categories, companies that manufacture primarily in China face punishing economics. Foxconn's ability to route production through India, Mexico, and the United States gives it flexibility that smaller competitors simply do not have. For India, this means a sustained flow of foreign investment and manufacturing jobs that goes well beyond smartphones.

Third, the semiconductor plant signals a structural shift. India has long been an assembler of finished electronics. Foxconn's move into chip packaging — alongside Tata Electronics' fab in Dholera and Micron's facility in Gujarat — suggests the country is finally building the intermediate layers of the semiconductor supply chain. For the hundreds of thousands of Indian engineers working in chip design at Intel, Qualcomm, and AMD in the US, the emergence of a domestic hardware ecosystem creates a career option that did not exist five years ago.

Foxconn cautioned that "volatile global political and economic conditions" remain a risk, without elaborating. Its shares have gained 4.3 per cent this year, underperforming Taiwan's broader market. But the revenue trajectory speaks for itself: two consecutive quarters of near-30-per-cent-or-better growth, driven by a structural shift in global computing demand that shows no sign of slowing."""

# ──────────────────────────────────────────────────────────────────────
# ARTICLE 2: Z.ai GLM-5.2 — Chinese AI Model
# ──────────────────────────────────────────────────────────────────────

zai_body = """The day after Anthropic's most advanced AI models were pulled from public access by order of the US government, a lab in Beijing dropped the open-source model that may define the rest of 2026. GLM-5.2, built by Z.ai — the Tsinghua University spinoff formerly known as Zhipu AI — is now the highest-ranked open-source large language model in the world. And it was trained entirely on Huawei Ascend chips, without a single Nvidia GPU in the pipeline.

The performance numbers are difficult to dismiss. On FrontierSWE, a benchmark that evaluates whether an AI agent can complete real-world engineering projects, GLM-5.2 scores 74.4 per cent — one percentage point behind Anthropic's Claude Opus 4.8 and ahead of OpenAI's GPT-5.5 at 72.6. On SWE-bench Pro, which tests autonomous resolution of real GitHub issues, it scores 62.1 to GPT-5.5's 58.6. It does all of this at roughly one-sixth the API cost of its American rivals.

"It is just a tick below Opus 4.8 and right up there with GPT 5.5," David Sacks, the White House AI and crypto czar, said on the All-In podcast. He added, pointedly, that "we cannot afford to do things that slow our companies down" — a not-so-subtle jab at the very government restrictions that helped fuel GLM-5.2's adoption.

## The Architecture

GLM-5.2 is a Mixture-of-Experts model with 744 billion total parameters but only 40 billion active at any given time — a design that keeps inference costs low without sacrificing capability. It supports a one-million-token context window, five times its predecessor's capacity, allowing developers to process entire codebases in a single pass. The model is released under the MIT licence, one of the most permissive in open-source software, meaning anyone can use, modify, and commercially deploy it without royalties.

Z.ai's stock has surged more than 2,000 per cent since its Hong Kong listing in January, pushing its market capitalisation past HK$1 trillion — roughly $128 billion. The company's founder, Tang Jie, has publicly stated that Z.ai could produce a model on par with Anthropic's Fable by the first quarter of 2027.

## What This Means for Indian Tech

The implications for Indian developers and IT companies are immediate and practical.

India is home to the world's largest developer community, and the cost of AI tooling matters enormously. At approximately $1.40 per million input tokens and $4.40 per million output tokens, GLM-5.2 undercuts GPT-5.5 and Claude by a factor of six. For Indian startups building AI-powered products — and the $676 million that flowed into Indian AI startups in the first half of 2026 suggests there are plenty — that cost differential is the difference between a viable business model and a cash burn problem.

The open-source licence removes another barrier. Indian IT services giants like TCS, Infosys, and HCLTech, which are pivoting aggressively toward AI-driven delivery, can deploy GLM-5.2 on their own infrastructure without per-query fees or usage restrictions. Sarvam, India's newest AI unicorn, has built its strategy around sovereign AI models that run on local infrastructure — a philosophy that aligns naturally with an MIT-licensed frontier model.

But there is a geopolitical dimension that Indian policymakers cannot ignore. GLM-5.2 was built on Huawei hardware, which is subject to US export controls. India has so far avoided choosing sides in the US-China technology rivalry, maintaining relationships with both American hyperscalers and Chinese equipment vendors. A world in which the most capable open-source AI runs on Chinese chips and the most capable closed-source AI is subject to US government suspension creates a fragmented landscape that India will need to navigate with considerable care.

The international developer community has already begun voting with its keyboards. In the three weeks since GLM-5.2's release, it has been integrated into Cloudflare Workers AI, appeared on every major leaderboard, and generated 2-bit quantised versions small enough to run on high-end consumer hardware. Whether Washington's restrictions on American models accelerated this shift or merely coincided with it, the outcome is the same: the AI frontier is no longer an exclusively American property."""

# ──────────────────────────────────────────────────────────────────────
# ARTICLE 3: Skyroot Aerospace — India's First Private Orbital Rocket
# ──────────────────────────────────────────────────────────────────────

skyroot_body = """For decades, if you wanted to put a satellite into orbit from Indian soil, you called ISRO. That monopoly is about to end.

Skyroot Aerospace, a Hyderabad-based startup founded by two former ISRO engineers, has announced a launch window of July 12 to August 4 for the maiden flight of Vikram-1 — the first privately developed orbital-class rocket in Indian history. The launch will take place from the Satish Dhawan Space Centre in Sriharikota, the same spaceport where ISRO's heavyweights have lifted off for half a century.

The mission, called "Aagaman" — Sanskrit for "arrival" — is as much a statement as a test flight.

## The Hardware

Vikram-1 stands seven stories tall and is built with an all-carbon composite structure, a material choice that keeps weight down without compromising structural integrity. Its propulsion systems are developed entirely in-house, including 3D-printed liquid engines and high-thrust solid-fuel boosters. The rocket is designed to carry payloads of up to 350 kilograms into low Earth orbit at an altitude of 450 kilometres.

This is not Skyroot's first launch. In November 2022, its smaller Vikram-S became the first privately built rocket to reach space from Indian soil, validating the core technology stack in a suborbital flight. Vikram-1 is the full orbital step — a far more demanding engineering challenge that requires stage separation, precise guidance systems, and sustained thrust across multiple phases of ascent.

"We want to understand how the vehicle performs from lift-off through every phase of ascent," said Pawan Kumar Chandana, Skyroot's co-founder and CEO. "This data cannot be fully replicated through ground testing."

## The Money Behind It

Skyroot's ambitions are backed by serious capital. In May, the company raised $60 million from Singapore's GIC and Sherpalo Ventures, pushing its valuation past $1 billion and making it India's first space-tech unicorn. Total funding now stands at well over $100 million — a figure that would have been unthinkable for an Indian private space venture even three years ago.

The investment thesis is straightforward. The global small-satellite launch market is growing rapidly as constellations for communications, earth observation, and internet connectivity proliferate. Companies like Rocket Lab and Firefly Aerospace have carved out the commercial niche in the West. India, despite having one of the world's most capable space agencies, has had no private-sector equivalent — until now.

The Indian government has set an ambitious target: a $44 billion space economy by 2033, up from $8.4 billion today. Achieving that requires private launch capacity. ISRO, which is focused on marquee missions like Chandrayaan, Gaganyaan, and India's planned space station, simply cannot service the volume of commercial small-satellite launches the market demands.

## The Diaspora Connection

For the thousands of Indian aerospace engineers working at SpaceX, Blue Origin, Boeing, and Lockheed Martin in the United States, Skyroot represents something that did not exist when they left India: a credible private space company with the technology, funding, and regulatory backing to build a commercial launch programme.

The founders' pedigree is part of the pitch. Chandana worked as a scientist at ISRO before co-founding Skyroot with Naga Bharath Daka. Their team draws heavily from ISRO's talent pool — engineers who built the systems that put Chandrayaan on the Moon now apply that expertise to a venture designed from the start for high-cadence commercial launches.

India's private space ecosystem extends beyond Skyroot. Agnikul Cosmos, also based in the south, is developing its own small launch vehicle with a single-piece 3D-printed engine. Pixxel operates a constellation of hyperspectral imaging satellites. Dhruva Space builds satellite platforms. Together, they represent a nascent but rapidly maturing industry that could transform India from a country that launches satellites into one that builds the infrastructure for a space-based economy.

If Vikram-1 reaches orbit later this month, India will join a small club of nations where private companies can deliver payloads to space. For a country whose diaspora includes some of the finest aerospace talent in the world, that milestone carries weight well beyond the technical achievement."""

# ──────────────────────────────────────────────────────────────────────
# BUILD ARTICLES LIST
# ──────────────────────────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Foxconn Just Had Its Best Quarter in Years. India Is the Reason Wall Street Should Care.",
        "subheadline": "Revenue surged 40 per cent on AI server demand, but the real story is a billion-dollar bet on Indian manufacturing — from iPhones to semiconductor packaging.",
        "slug": make_slug("foxconn-q2-ai-revenue-india-manufacturing-expansion"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Foxconn's $1B India expansion — from iPhone assembly to semiconductor packaging — creates hardware manufacturing jobs and career paths for NRI engineers considering a return, while positioning India as a node in the global AI infrastructure supply chain.",
        "tags": ["foxconn", "ai-servers", "india-manufacturing", "nvidia", "apple", "semiconductors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/foxconn-second-quarter-revenue-jumps-company-cautions-geopolitics-2026-07-05/"},
            {"name": "Wall Street Journal / Morningstar", "url": "https://www.morningstar.com/news/dow-jones/202605140517/foxconn-posts-strong-results-on-ai-hardware-sales"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/foxconn-projects-30-capex-growth-in-2026-amid-robust-ai-demand/article69539497.ece"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/foxconns-devanahalli-plant-to-begin-iphone-shipments-from-june/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Dingpu_Plant%2C_Hon_Hai_Precision_Ind._20160801.jpg/1280px-Dingpu_Plant%2C_Hon_Hai_Precision_Ind._20160801.jpg",
        "image_caption": "Foxconn's Dingpu manufacturing plant in Taiwan, headquarters of the world's largest contract electronics maker",
        "image_attribution": "Wikimedia Commons",
        "body": foxconn_body.strip()
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Chinese Lab Built an AI Model That Rivals Claude and GPT. It Used Zero Nvidia Chips.",
        "subheadline": "Z.ai's GLM-5.2 matches frontier American models at one-sixth the cost, runs on Huawei hardware, and ships under an MIT licence. For Indian developers, it changes the maths on AI adoption.",
        "slug": make_slug("zai-glm-52-chinese-ai-model-huawei-open-source"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "At one-sixth the cost of US frontier models and with an MIT licence, GLM-5.2 is immediately relevant to Indian startups and IT services giants pivoting to AI — while raising geopolitical questions about India's position between US and Chinese tech ecosystems.",
        "tags": ["ai", "china", "open-source", "zhipu-ai", "huawei", "indian-developers", "geopolitics"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/new-inexpensive-chinese-ai-model-is-catching-up-with-anthropic-openai-their-home-2026-07-02/"},
            {"name": "Tech Startups", "url": "https://techstartups.com/2026/06/25/chinese-ai-startup-z-ai-targets-agi-as-glm-5-2-beats-gpt-5-5-and-narrows-the-gap-with-openai-and-anthropic/"},
            {"name": "Decrypt", "url": "https://decrypt.co/313850/china-z-ai-releases-glm-5-2-rivals-claude-opus-nvidia"},
            {"name": "Dev.to", "url": "https://dev.to/composiodev/glm-52-chinas-open-frontier-model-dropped-the-day-anthropic-got-banned-2026-3m0n"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17483849/pexels-photo-17483849.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Abstract visualisation of a neural network — the architecture underpinning frontier AI models like GLM-5.2",
        "image_attribution": "Pexels / Google DeepMind",
        "body": zai_body.strip()
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's First Private Orbital Rocket Is Ready to Fly. The Launch Window Opens in a Week.",
        "subheadline": "Skyroot Aerospace's Vikram-1 — seven stories tall, carbon composite, 3D-printed engines — will attempt to reach orbit from Sriharikota as early as July 12. A $1 billion valuation says the market believes it can.",
        "slug": make_slug("skyroot-vikram-1-india-first-private-orbital-rocket-launch"),
        "category": "technology",
        "vertical": "space-tech",
        "diaspora_angle": "For Indian aerospace engineers at SpaceX, Blue Origin, and Boeing, Skyroot represents a credible private space company in India — a career path and investment opportunity that did not exist five years ago.",
        "tags": ["skyroot-aerospace", "vikram-1", "indian-space", "private-launch", "startup-unicorn", "isro"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indias-skyroot-aerospace-readies-countrys-first-private-orbital-rocket-launch-2026-07-02/"},
            {"name": "Techlusive", "url": "https://www.techlusive.in/news/indias-first-private-orbital-rocket-set-to-launch-this-month-all-about-vikram-1-6828e9a5b0b27"},
            {"name": "Nagaland Post / PTI", "url": "https://www.nagalandpost.com/index.php/skyroot-sets-launch-window-for-indias-first-private-orbital-rocket/"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/isro-targets-five-commercial-small-rocket-sslv-launches-this-fiscal-skyroot-agnikul-cosmos-set-for-first-launches-11746068792972.html"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Vikram-S_rocket%27s_Mission_Prarambh_%28cropped_wide%29.png/1200px-Vikram-S_rocket%27s_Mission_Prarambh_%28cropped_wide%29.png",
        "image_caption": "Skyroot Aerospace's Vikram-S rocket during Mission Prarambh at Sriharikota, India's first private space launch in 2022",
        "image_attribution": "Wikimedia Commons",
        "body": skyroot_body.strip()
    },
]

# ──────────────────────────────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────────────────────────────

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
