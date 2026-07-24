#!/usr/bin/env python3
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Gave Up on Building Its Own AI Brain. Sundar Pichai and Jensen Huang Won the Contract.",
        "subheadline": "The new Siri will run on Google's Gemini models powered by NVIDIA's Blackwell chips — a rare capitulation from the most vertically integrated company on earth.",
        "slug": make_slug("apple-siri-google-gemini-nvidia-blackwell-wwdc"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-origin CEOs Sundar Pichai (Google) and Jensen Huang's NVIDIA are the invisible engine behind Apple's biggest AI bet. For the thousands of Indian engineers at all three companies, this partnership reshapes internal power dynamics and career trajectories.",
        "tags": ["apple", "google", "nvidia", "siri", "gemini", "blackwell", "wwdc", "ai", "indian-tech-leaders"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Information", "url": "https://www.theinformation.com/articles/apple-siri-google-gemini-nvidia-blackwell"},
            {"name": "MacRumors", "url": "https://www.macrumors.com/2026/06/04/apple-siri-nvidia-blackwell-chips/"},
            {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/04/apple-nvidia-chips-gemini-siri/"},
            {"name": "PhoneArena", "url": "https://www.phonearena.com/news/chatbot-siri-gemini-nvidia-blackwell-b200"},
            {"name": "Investopedia", "url": "https://www.investopedia.com/apple-wwdc-2026-siri-ai-stock-move"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/42/Jensen_Huang_-_RTX_Blackwell_-_Nvidia_Keynote_-_CES_2025_Las_Vegas_%282%29.jpg",
        "image_caption": "Jensen Huang presenting NVIDIA's Blackwell architecture at CES 2025 in Las Vegas",
        "image_attribution": "Wikimedia Commons",
        "body": """When Apple unveils the overhauled Siri at WWDC on Monday, the company will be making a confession it has spent decades avoiding: it cannot do this alone.

According to reporting from The Information, the new Siri — expected to ship with iOS 27 in September — will route complex queries through Google's custom 1.2-trillion-parameter Gemini model, running on NVIDIA's Blackwell B200 data centre chips inside Google Cloud. Apple tried to get Gemini running on its own Private Cloud Compute servers, built around Apple Silicon. It ran too slowly. So the company that once insisted on designing its own screws now rents someone else's GPUs for its flagship AI product.

## The Three-Company Stack

The arrangement creates a peculiar three-way dependency. Apple controls the user-facing experience and the Siri brand. Sundar Pichai's Google provides the AI model and the cloud infrastructure. Jensen Huang's NVIDIA supplies the chips that make the whole thing move. For a company that has historically treated vertical integration as a religion, this is apostasy.

The irony runs deeper. Google already pays Apple roughly $20 billion a year to remain the default search engine on iPhones. Now Apple pays Google for AI muscle. The two companies are locked in a financial embrace that neither can easily escape — and that regulators are watching with increasing interest.

Apple has approved NVIDIA's hardware-based confidential computing feature for the arrangement, which encrypts user data while it is being processed on the Blackwell chips. The company will retain the "Private Cloud Compute" branding, even though the compute is neither private to Apple nor running on Apple hardware.

## What This Means for Indian Engineers

The deal reshapes the internal calculus at three of the largest employers of Indian tech talent in the United States. At Google, the Gemini team — which includes a significant cohort of Indian-origin AI researchers — now has Apple as a paying customer, adding revenue justification to a project that has consumed billions in compute. At NVIDIA, where H-1B hiring has surged even as Google and Amazon cut back, the Blackwell B200's role in powering Siri adds another proof point for the company's data centre dominance.

At Apple itself, the decision signals something more uncomfortable. The company's internal AI efforts, which employed hundreds of machine learning engineers, were not enough. For Indian engineers at Apple who joined specifically to work on on-device AI, the pivot to Google Cloud raises questions about which teams will grow and which will be quietly reassigned.

The broader market is taking notice. Analysts at Wedbush called WWDC a "pivotal moment" for Apple's AI monetization strategy, with a price target of $400. JPMorgan expects the new Siri to launch alongside the iPhone 18 in September, with a standalone chatbot app embedded in the Dynamic Island.

## The Extensions Play

Perhaps the most consequential feature is one that has received less attention. iOS 27 will reportedly introduce an "Extensions" system that lets users choose which AI service powers Siri — including ChatGPT, Gemini, Claude, and others. Each third-party response will use a distinct voice so users know which model is speaking. A dedicated section of the App Store will host these AI integrations.

This is Apple doing what it does best: turning someone else's technology into a platform it controls. If Extensions work as described, Apple will have effectively commoditised the AI model layer while retaining control of the distribution, the user relationship, and the data access.

For NRI investors holding Apple, Google, or NVIDIA stock — and there are many — the three-way partnership is a net positive. It locks in revenue for Google and NVIDIA, and it gives Apple a credible AI story that it has lacked for two years. The question is whether Apple can execute on a strategy that depends so heavily on companies it has spent its history trying to replace.

WWDC begins June 8. The developer beta drops the same day. The new Siri, when it arrives in September, will be the most expensive admission of inadequacy Apple has ever shipped — and possibly its smartest move in years."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "TCS, Infosys, and Wipro Just Deployed AI to 300,000 Workers. Their Stock Crashed Anyway.",
        "subheadline": "India's IT giants completed one of the world's largest enterprise AI rollouts in six months. Investors responded by wiping 6% off the Nifty IT index in a single session.",
        "slug": make_slug("tcs-infosys-wipro-copilot-300k-ai-stock-crash"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Millions of NRIs have family members working at TCS, Infosys, and Wipro, or hold stock in these companies. The AI disruption paradox — adopt AI or get replaced by it — is deeply personal for the diaspora, especially as Indian IT services firms are the largest H-1B sponsors in the US.",
        "tags": ["tcs", "infosys", "wipro", "microsoft-copilot", "ai-disruption", "indian-it", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Microsoft News", "url": "https://news.microsoft.com/source/asia/features/infosys-tcs-wipro-copilot-300000/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-it-stocks-worst-day-ai-disruption-2026-06-03/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/kotak-flags-ai-insourcing-risks-indian-it/"},
            {"name": "People Matters", "url": "https://www.peoplematters.in/article/ai/infosys-tcs-wipro-copilot-300000-employees-ai"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/2d/Aerial_view_of_the_Glass_Pyramid_at_the_Infosys_Campus.jpg",
        "image_caption": "Aerial view of the Glass Pyramid at the Infosys campus in Mysuru, India",
        "image_attribution": "Wikimedia Commons",
        "body": """In the span of six months, India's three largest IT services companies pulled off something that should have been a victory lap. TCS, Infosys, and Wipro each scaled Microsoft 365 Copilot to more than 100,000 employees, collectively surpassing 300,000 AI-powered seats — one of the largest enterprise AI deployments Microsoft has ever recorded globally.

The numbers are striking. At Infosys, monthly active usage exceeded 91 per cent. TCS reported 86 per cent daily usage, with productivity gains of 20 to 25 per cent in research and content production. Wipro's employees generated 7.5 million AI prompts per month, saving an estimated 250,000 full-time-equivalent days every quarter.

Then the market spoke. On the same day Microsoft trumpeted the milestone, India's Nifty IT index plunged 5.8 per cent — its worst session in four months. TCS led the rout, falling 9 per cent. Infosys dropped 4.3 per cent. Wipro shed 3.7 per cent.

## The Paradox That Won't Resolve

The selloff captures a contradiction that has stalked India's $300 billion IT services sector for over a year. The very tools these companies are deploying to boost productivity are the same ones investors fear will shrink the pie. If Copilot can save 250,000 person-days a quarter at Wipro alone, how many of those days represent jobs that will simply disappear?

Kotak Institutional Equities put the concern bluntly: "We expect new opportunities such as legacy modernization to increase, but do not expect them to compensate for the deflation enough." The brokerage maintained buy ratings on TCS, Infosys, and Tech Mahindra, but slapped a sell on Wipro and flagged that valuations across the sector still do not fully account for AI-led disruption.

Ambit Capital echoed the sentiment, noting that fourth-quarter earnings confirmed the "ongoing challenges" and estimating that deflation would outstrip incremental AI demand. Rishubh Vasa of Indsec Securities went further, projecting the total addressable market of Indian IT companies could shrink 20 to 25 per cent.

## What NRIs Should Watch

For the Indian diaspora, the stakes extend well beyond portfolio allocation. TCS, Infosys, and Wipro collectively employ over a million people in India, and their US operations are among the largest sponsors of H-1B visas. A structural contraction in the IT services model does not just affect stock prices — it reshapes the career pipeline that has funnelled generations of Indian engineers into the American tech workforce.

The 300,000-seat Copilot deployment is, paradoxically, both the strongest evidence that Indian IT can adapt and the clearest signal that adaptation may not be enough. Microsoft's own Work Trend Index describes the emerging model as the "Frontier Firm" — organisations that redesign work around human-agent teams, where AI handles execution and humans focus on judgment and creativity.

The problem for Indian IT services is that their traditional value proposition was precisely the execution layer. When a bank hired TCS to maintain a legacy codebase or Wipro to run a help desk, it was paying for reliable human labour at Indian wage rates. If AI agents can do that work faster and cheaper, the question is not whether Indian IT firms will deploy AI — they clearly will, and aggressively — but whether AI transforms them from labour arbitrage businesses into something more durable, or whether it simply accelerates the commoditisation of the services they sell.

The Nifty IT index is now down 22 per cent in 2026, following a 26 per cent drop in 2025. For NRI investors who once treated Indian IT stocks as a reliable proxy for the sector's growth, the message is unambiguous: the market is pricing in a future where productivity gains flow to clients, not to the companies that deliver them.

Microsoft's Judson Althoff insists the impact is "no longer limited to productivity gains" but is "reshaping how organisations operate, compete, and grow." He may be right. The question India's IT giants must answer is whether they are the ones doing the reshaping — or the ones being reshaped."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic Just Gave India Access to Its Most Dangerous AI. Delhi Wants It Hosted on Indian Soil.",
        "subheadline": "Claude Mythos, the cybersecurity model that found 10,000 zero-day vulnerabilities, is now available to Indian banks, telecom firms, and CERT-In. The government is pushing for sovereign hosting.",
        "slug": make_slug("anthropic-claude-mythos-india-cybersecurity-sovereign"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's push for sovereign AI hosting of Anthropic's models signals a broader shift in how the country approaches critical tech infrastructure — relevant to NRI investors and tech professionals tracking India's AI governance trajectory and cybersecurity modernization.",
        "tags": ["anthropic", "claude-mythos", "cybersecurity", "india", "sovereign-ai", "project-glasswing", "cert-in"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Gadgets 360", "url": "https://www.gadgets360.com/ai/news/anthropic-project-glasswing-expansion-claude-mythos-india"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/india-gets-access-claude-mythos-ai-anthropic/"},
            {"name": "AInvest", "url": "https://www.ainvest.com/news/indian-firms-early-access-anthropic-mythos/"},
            {"name": "Digit", "url": "https://www.digit.in/news/general/anthropic-expands-claude-mythos-cybersecurity-initiative-india/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/5474024/pexels-photo-5474024.jpeg",
        "image_caption": "Digital security visualization representing cybersecurity threat detection and AI-powered defense",
        "image_attribution": "Pexels",
        "body": """Anthropic, the San Francisco AI company behind Claude, has expanded its most powerful cybersecurity model to India — and the Indian government is already negotiating to host it domestically.

Under the expansion of Project Glasswing, Anthropic's initiative to protect critical infrastructure, approximately 150 new organisations across more than 15 countries now have access to Claude Mythos Preview. India is among them, alongside Canada, Australia, France, Germany, Japan, and South Korea. The total number of participating organisations has reached roughly 200, with partners including Samsung, SK Telecom, Okta, Swift, Euroclear, and NATO.

In India, access is tightly controlled. The recipients are not the usual IT services suspects — TCS, Infosys, and Wipro are notably excluded. Instead, Mythos access has gone to organisations operating critical infrastructure: banks, telecom providers, power utilities, and cybersecurity agencies. CERT-In, India's national computer emergency response team, has received a preview. An Indian government official confirmed to The Hindu Business Line that both public and private organisations in cybersecurity and financial services domains now have access.

## What Mythos Can Do

Claude Mythos is not a chatbot. It is a frontier AI model specifically designed to find and exploit software vulnerabilities — the kind of flaws that nation-state hackers use to breach power grids, banking systems, and telecommunications networks. During its initial testing phase with 50 organisations globally, Mythos identified more than 10,000 previously unknown security flaws across major operating systems and web browsers.

The partners with early access include Amazon Web Services, JPMorgan Chase, CrowdStrike, Microsoft, and NVIDIA. The fact that Anthropic chose to include Indian institutions in the second wave — ahead of many other countries — reflects both the scale of India's digital infrastructure and the severity of the threats it faces. A successful cyberattack on many of the systems now protected by Mythos could affect more than 100 million people, according to Anthropic.

## The Sovereign Hosting Push

The more consequential story, however, is what Delhi wants next. Indian government officials are pushing for sovereign hosting of Anthropic's Claude models within India, arguing that sensitive sectors cannot operate on foreign-hosted infrastructure due to jurisdictional, compliance, and national security concerns.

This is not a routine ask. Sovereign hosting would require Anthropic to deploy its models on servers physically located in India, subject to Indian data protection laws and potentially accessible to Indian regulatory authorities. For a company that has built its brand around AI safety and careful deployment, the request creates a tension between commercial expansion and governance philosophy.

The push mirrors a broader pattern across India's digital infrastructure strategy. UPI runs on Indian servers. Aadhaar's biometric database is domestically hosted. The Indian government has repeatedly insisted that data generated by Indian citizens should remain within Indian jurisdiction — a position that has complicated operations for global cloud providers and social media platforms alike.

## Why NRIs Should Pay Attention

For the Indian diaspora, particularly those working in cybersecurity, cloud infrastructure, and enterprise software, Anthropic's India expansion represents a potential career opportunity and investment signal. Anthropic opened its Bengaluru office earlier this year — its second in Asia after Tokyo — and has been hiring aggressively for roles focused on Indian language support and enterprise partnerships. The company's India revenue run rate has doubled since October 2025.

The exclusion of IT services companies from Mythos access is also telling. It suggests that Anthropic and the Indian government view cybersecurity AI as a national security tool, not a commercial product to be resold through outsourcing contracts. This distinction matters as India builds out its own AI governance framework — one that may ultimately look quite different from the permissive regulatory environments in the US and UK.

The expansion also signals a competitive dynamic worth watching. OpenAI, Google DeepMind, and Meta AI have all announced India-focused initiatives in recent months. Anthropic's Mythos deployment gives it a differentiated position: not as a general-purpose AI provider, but as the company that governments and critical infrastructure operators trust with their most sensitive systems.

Whether that trust extends to sovereign hosting remains an open question. But the fact that Delhi is asking suggests it considers the answer important enough to negotiate."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
