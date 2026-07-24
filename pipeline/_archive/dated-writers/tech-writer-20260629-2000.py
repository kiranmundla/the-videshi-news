#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-29 20:00 PDT run"""
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
# Article 1: OpenAI India MD hire
# ─────────────────────────────────────────────
art1_body = """OpenAI has appointed Prabhjeet Singh, formerly the president of Uber India and South Asia, as its first Managing Director for India. Singh will join in September and report to Kiran Mani, who oversees the Asia Pacific region — making him the most senior OpenAI executive on Indian soil.

The move is not subtle. India is already OpenAI's second-largest market globally, with more than 100 million weekly active ChatGPT users and a top-five ranking for API usage. The company opened its first office in New Delhi last November; Mumbai and Bengaluru offices are expected before year-end.

## An operator, not a researcher

Singh's profile tells you what OpenAI wants in India: scale, not labs. Over nearly 11 years at Uber, he expanded the ride-hailing company from a handful of Indian cities into a nationwide platform spanning Auto, Moto and Shuttle verticals. He pushed Uber's integration with India's Open Network for Digital Commerce (ONDC) and led electric mobility partnerships — all of which required navigating India's regulatory thicket, something OpenAI badly needs as the country drafts its AI governance framework.

Before Uber, Singh was an Associate Partner at McKinsey and worked at Lehman Brothers. He holds an engineering degree from IIT Kharagpur and a management degree from IIM Ahmedabad — credentials that practically telegraph "Indian tech executive who stayed connected."

## Why NRIs should care

For the Indian American tech community, the appointment has several layers. First, it signals that OpenAI views India not merely as a user base to be harvested but as a market worth dedicated C-suite attention. That matters for Indian entrepreneurs building on OpenAI's APIs, for enterprise clients at companies like Reliance and Tata Group (both existing OpenAI partners), and for the growing Indian AI research community that has long felt underrepresented in Silicon Valley's frontier labs.

Second, it highlights a pattern worth watching. Sam Altman has repeatedly called India's AI adoption "amazing" and has signalled intent to invest across the AI stack in the country. With Google DeepMind, Anthropic and Meta AI all deepening their India presence, the competition for Indian AI talent — both in-country and in the diaspora — is intensifying.

Third, for the tens of thousands of Indian engineers working at US tech companies on H-1B visas, OpenAI's India expansion represents an alternative geography. As AI companies build genuine operations in India (not just cost centers), the "return to India" calculus shifts. A Managing Director role in Delhi with global scope is not the same as being outsourced to Bengaluru.

## The competitive landscape

OpenAI is late to the India game by some measures. Google has operated AI research labs in Bengaluru for years. Anthropic recently launched a Seoul office and is eyeing India. And homegrown players like Sarvam AI — which just became India's newest AI unicorn with a $234 million round at a $1.5 billion valuation — are building full-stack AI businesses designed specifically for Indian languages and use cases.

Singh's challenge will be to carve out a defensible position against both global rivals and local champions, while managing a regulatory environment that remains in flux. India's draft AI governance guidelines are still under stakeholder consultation, and the newly formed AI Governance Expert Group has yet to define clear compliance frameworks.

If he can pull it off, OpenAI will have a genuine second home market. If he can't, it will have burned through another expensive India experiment — a fate that has claimed plenty of American tech companies before it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI Just Named Its First India Chief. He Ran Uber There for a Decade.",
    "subheadline": "Prabhjeet Singh, an IIT Kharagpur and IIM Ahmedabad alumnus, will oversee OpenAI's second-largest market — 100 million weekly ChatGPT users and growing.",
    "slug": make_slug("openai-prabhjeet-singh-india-md-uber-chatgpt"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "OpenAI's India expansion signals growing AI job opportunities for diaspora professionals and returning NRIs, while creating a competitive market for Indian entrepreneurs building on its APIs.",
    "tags": ["openai", "ai", "indian-tech", "silicon-valley", "chatgpt", "india-expansion"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/openai-taps-ex-uber-regional-chief-india-leadership-2026-06-27/"},
        {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com/technology/openai-appoints-former-uber-india-chief-prabhjeet-singh-as-its-first-india-managing-director"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/openai-names-prabhjeet-singh-as-managing-director-for-its-india-ops"},
        {"name": "afaqs!", "url": "https://www.afaqs.com/news/uber-india-head-prabhjeet-singh-joins-openai-as-india-managing-director"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/OpenAI_brain_network_visualization.png/1280px-OpenAI_brain_network_visualization.png",
    "image_caption": "OpenAI neural network visualization representing the company's AI architecture",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}

# ─────────────────────────────────────────────
# Article 2: South Korea $576B chip investment
# ─────────────────────────────────────────────
art2_body = """South Korea on Monday unveiled the single largest national semiconductor investment in history: more than $576 billion over the coming decade, anchored by Samsung Electronics and SK Hynix, the world's two largest memory chipmakers.

President Lee Jae Myung, flanked by the chiefs of both companies, cast the initiative as a "great leap forward" built on the "triple axis" of semiconductors, physical AI and data centres. "We must secure the core elements of AI faster than any other country," he said in a televised address.

The numbers are staggering. Samsung and SK Hynix will invest 800 trillion won ($518 billion) to build two new chip fabrication sites each in South Korea's southwestern region. An additional 81 trillion won will fund a chip packaging cluster in the Chungcheong area near Seoul. Regional governments in Gwangju and South Jeolla province will kick in another 5-20 trillion won.

## The AI memory race

The investment is not a gamble on some speculative technology. It is a doubling-down on what is already working. High-bandwidth memory (HBM) chips — the specialised modules that power AI training and inference — have become the bottleneck of the entire artificial intelligence industry. Every NVIDIA GPU, every Google TPU, every hyperscaler data centre needs them by the rack. Samsung and SK Hynix make roughly 80 per cent of the world's supply.

SK Hynix briefly surpassed $1.3 trillion in market capitalisation last week, approaching Samsung as Korea's most valuable company for the first time. South Korea's benchmark Kospi index surged past 9,000 points, driven almost entirely by the chip rally. Both companies have redirected 70-80 per cent of their advanced process capacity and new capital expenditure toward HBM and DDR5/LPDDR5X production.

## India's semiconductor gap

For India, the contrast is uncomfortable but instructive. India's entire semiconductor investment to date amounts to roughly $10 billion — $2.75 billion for Micron's assembly and test facility in Gujarat (which opened in February under CEO Sanjay Mehrotra, an Indian-origin executive), and the rest split across Tata Electronics' planned fabrication plant in Dholera and a handful of smaller initiatives under the India Semiconductor Mission.

Those projects are themselves under pressure. Supply chain disruptions caused by the West Asia conflict have affected the availability of speciality gases, chemicals and metals needed for fab construction, raising concerns that Tata's Dholera timeline may slip. India's semiconductor ambitions remain focused on mature-node manufacturing (40nm and above) and assembly — not the cutting-edge HBM and advanced logic nodes where Korea and Taiwan compete.

## Why NRIs should pay attention

For Indian Americans working in the semiconductor industry — and there are tens of thousands at companies like Intel, Qualcomm, Micron, Texas Instruments and Broadcom — Korea's move reshapes the global talent map. Seoul is building chip cities; India is building chip assembly plants. The gap in ambition and capital is a 50-to-1 ratio.

That said, India's strategy is not without logic. Micron's Sanand facility is already shipping DDR5 DRAM modules to Dell and will test tens of millions of chips this year, scaling to hundreds of millions in 2027. India is building the back end of the semiconductor supply chain — the assembly, testing and packaging that turns raw wafers into finished products. It is a necessary, if unglamorous, step.

The question is whether India can move up the value chain before the next generation of AI chips makes today's fabs obsolete. Korea just bet $576 billion that the answer matters. India's bet, so far, is fifty times smaller.

NRI investors watching both markets should note that the semiconductor supercycle shows no sign of cresting. But the companies positioned to capture its value are building in Korea, Taiwan and, increasingly, the United States — not yet in India."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "South Korea Just Bet $576 Billion on Chips. India Has Bet $10 Billion. That Ratio Tells a Story.",
    "subheadline": "Samsung and SK Hynix will build four new mega-fabs as the AI memory race intensifies. India's chip projects face delays and a 50-to-1 investment gap.",
    "slug": make_slug("south-korea-576-billion-chips-samsung-sk-hynix-india-gap"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Tens of thousands of Indian Americans work at semiconductor firms like Intel, Qualcomm and Micron — Korea's massive bet reshapes the global chip talent map and raises questions about India's ability to compete.",
    "tags": ["semiconductor", "samsung", "sk-hynix", "india-chips", "micron", "ai-infrastructure"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "CNN", "url": "https://www.cnn.com/2026/06/29/business/south-korea-chip-investment-samsung-sk-hynix/index.html"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/korea-taps-samsung-sk-hynix-576-billion-ai-chip-drive-2026-06-29/"},
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/indias-chip-projects-face-delays-amid-west-asia-conflict-report-1751075553615"},
        {"name": "Micron Technology", "url": "https://www.globenewswire.com/news-release/2026/02/28/3034211/0/en/Micron-Celebrates-Opening-of-India-s-First-Semiconductor.html"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg",
    "image_caption": "Close-up of a microprocessor circuit board with intricate AI chip architecture",
    "image_attribution": "Pexels",
    "body": art2_body
}

# ─────────────────────────────────────────────
# Article 3: Big Tech investing in Indian startups
# ─────────────────────────────────────────────
art3_body = """India's startup ecosystem raised $1.1 billion in a single week ending June 26, powered by a $900 million Meta investment in fintech unicorn CRED and a flurry of deals across AI, proptech and space tech. The week also saw real estate platform Square Yards become India's 131st unicorn.

But beneath the headline numbers, a structural shift is underway. The biggest technology companies in the world — Meta, Google, Microsoft, Amazon and HCLTech — are increasingly choosing strategic minority investments in Indian startups over outright acquisitions. They want access to India's innovation without the headaches of integration.

## Why invest, not acquire?

The logic is straightforward, if unsentimental. Acquisitions in India carry regulatory complexity that American and European companies have learned to avoid. The Competition Commission of India has grown more assertive (ask Apple, currently facing a potential $38 billion antitrust fine). Cross-border M&A triggers compliance cascades across tax, data localisation and foreign exchange rules. And Indian founders, having built companies during a funding boom that valued independence, are reluctant sellers.

"Startups can play a critical role in the execution of an innovation strategy due to their unmatched agility," said Anushree Verma, Senior Director Analyst at Gartner. "Tech giants invest rather than acquire to retain flexibility while accelerating ecosystem growth," added Biswajeet Mahapatra, Principal Analyst at Forrester.

The result is a new species of deal. Meta's $900 million in CRED is not a buyout — it is a bet on Kunal Shah's ability to build India's next financial super-app, with Meta getting strategic alignment between WhatsApp Pay and CRED's 50-million-strong creditworthy user base. Google and Microsoft have made similar plays across AI and enterprise software. HCLTech's $150 million lead investment in Sarvam AI gave it a partner for sovereign AI deployment without the burden of building models in-house.

## The funding picture

India's startup ecosystem is on track to mint eight to ten unicorns in 2026, up from seven in 2024 — though still far from the 45 unicorns of the 2021 boom. This year's crop includes Juspay, KreditBee, Skyroot Aerospace, Sarvam AI and Square Yards. Total unicorn valuation now exceeds $394 billion across 131 companies, with Bengaluru (54 unicorns), Delhi NCR and Mumbai leading.

Last week's funding also surfaced a deep-tech trend worth watching. AI startup JustAI raised $17 million in a Series A from Base10, Y Combinator, Peak XV Partners and HubSpot founder Dharmesh Shah. QOSMIC, a space-tech AI chip startup, pulled in $3.3 million from Accel and Prosus. These are not consumer apps chasing growth; they are infrastructure plays building real intellectual property.

## The diaspora dimension

For NRI investors and returning founders, this shift matters on multiple levels. The venture capital model in India is maturing — early backers are now pressuring unicorns for actual exits, not just higher valuations. A Mint analysis of 139 VC-backed unicorns found that only 77 have generated a liquidity event. Thirty-four are pursuing IPOs, and 26 have no visible path to an exit.

That creates both risk and opportunity. Risk, because many NRI investors who put money into India's startup boom between 2018 and 2022 are still waiting for returns. Opportunity, because Big Tech's strategic investment model offers a new exit pathway — minority stakes can be sold to the next strategic investor, or grow alongside an IPO.

For Indian Americans in Silicon Valley debating whether to start something in India or invest from afar, the message from last week's funding data is clear: India's startup market is open for serious capital, but the days of easy unicorn-minting and quick exits are over. The companies that will reward their backers are the ones building defensible technology — not the ones burning cash to acquire users.

Meta, Google and Microsoft appear to agree. They are placing their bets accordingly."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Big Tech Is Buying Into India's Startups — Without Buying Them",
    "subheadline": "Meta, Google, Microsoft and Amazon are choosing minority investments over acquisitions in India's $394 billion startup ecosystem. Last week alone, Indian startups raised $1.1 billion.",
    "slug": make_slug("big-tech-india-startup-investments-minority-stakes-cred"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "NRI investors who backed India's startup boom await returns as the market matures — Big Tech's strategic investment model offers new exit pathways but demands defensible technology over user acquisition.",
    "tags": ["indian-startups", "venture-capital", "meta", "google", "cred", "unicorns"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/big-tech-companies-turn-investors-as-startup-partnerships-trump-acquisitions/article69750147.ece"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/from-cred-to-square-yards-indian-startups-raised-1-1-bn-this-week/"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/start-ups/indias-unicorns-next-test-delivering-investor-exits-11750778413655.html"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/14/sarvam-becomes-indias-newest-ai-unicorn-with-234-million-funding-round-led-by-hcltech/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6913232/pexels-photo-6913232.jpeg",
    "image_caption": "Professionals reviewing investment data in a technology-focused meeting",
    "image_attribution": "Pexels",
    "body": art3_body
}

# ─────────────────────────────────────────────
# Insert all articles
# ─────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
