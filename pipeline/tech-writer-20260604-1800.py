#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-04 18:00 UTC run"""

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
    # ── Article 1: Indian IT + Microsoft Copilot 300K ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Infosys, TCS and Wipro Just Armed 300,000 Workers With AI. The Irony Writes Itself.",
        "subheadline": "India's three largest IT outsourcers have each crossed 100,000 Microsoft Copilot seats in six months, making them the world's fastest enterprise AI adopters — and raising hard questions about the headcount model that built them.",
        "slug": make_slug("infosys-tcs-wipro-300000-microsoft-copilot-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Hundreds of thousands of Indian engineers at TCS, Infosys and Wipro now work alongside AI copilots daily. For NRIs who built careers in IT services — and the next generation hoping to follow them — this is the clearest signal yet that the industry's labour-arbitrage model is being rewritten from the inside.",
        "tags": ["indian-it", "microsoft-copilot", "ai-adoption", "tcs", "infosys", "wipro", "enterprise-ai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Microsoft Source Asia", "url": "https://news.microsoft.com/source/asia/features/infosys-tcs-wipro-scale-microsoft-365-copilot-300000/"},
            {"name": "People Matters", "url": "https://www.peoplematters.in/article/technology/infosys-tcs-wipro-300000-copilot-ai-42700"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/enterprise-ai-microsoft-puneet-chandok/article69254321.ece"},
            {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/indias-it-giants-are-automating-themselves/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Microsoft CEO Satya Nadella, whose company announced the 300,000-seat Copilot milestone",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """India's three largest IT services firms have each crossed 100,000 Microsoft 365 Copilot licences, taking their combined deployment past 300,000 seats in under six months. Microsoft announced the milestone on June 3, calling Infosys, TCS and Wipro "frontier firms" for enterprise AI adoption — and placing India at the centre of the world's fastest large-scale AI rollout.

The numbers are difficult to dismiss as corporate theatre. In December 2025, each company had deployed roughly 50,000 Copilot seats. By early June, that figure had doubled across the board. Copilot is now embedded in coding workflows, consulting engagements, back-office operations and client delivery at all three firms. This is not a pilot programme with a blog post attached. It is a quarter of the industry's 1.15 million-strong combined workforce working alongside AI every day.

## The usage numbers are striking

Microsoft's India head, Puneet Chandok, offered specific figures in an interview with The Hindu Business Line. At Infosys, monthly active usage of Copilot exceeds 91 per cent. TCS reports 86 per cent daily active usage, with teams claiming 20 to 25 per cent productivity improvements in research and content tasks, along with two times faster insight generation. Wipro's monthly active usage sits at 95 per cent, with the company saying it saves more than 250,000 FTE-days every quarter.

These are not the tepid adoption curves that plagued earlier enterprise software rollouts. They suggest that Indian IT workers are not merely logging into Copilot to satisfy a licence mandate — they are using it for real work, at remarkable consistency.

## The labour-arbitrage paradox

The irony here is structural, not incidental. India's IT outsourcing industry was built on a single economic principle: skilled technology labour is cheaper in Bangalore than in Boston. TCS, Infosys and Wipro grew into global giants by selling that arbitrage to Western enterprises. At peak, TCS alone employed more than 600,000 people.

Now the same companies are deploying tools explicitly designed to make each worker more productive — which, over time, means doing more work with fewer people. As Communications Today put it bluntly: "The very companies that perfected the headcount-driven model are investing heavily in tools designed to make each worker more productive."

This does not mean mass layoffs are imminent. But it does mean the relationship between headcount and revenue, the foundational metric of Indian IT for three decades, is shifting. Wipro's claim of saving 250,000 FTE-days per quarter translates to roughly 4,000 full-time equivalent roles per quarter — in productivity terms, not in actual cuts. Scale that across three firms over several years, and the arithmetic starts to reshape hiring plans.

## What this means for NRIs in IT

For the hundreds of thousands of Indian engineers already inside these firms, the immediate effect is a new kind of daily workflow. Copilot handles first drafts of code reviews, summarises meeting transcripts, generates client presentation outlines and pulls data across enterprise platforms. The engineers who learn to direct these tools effectively will likely see their value rise. Those who resist may find their roles narrowing.

For the next generation — engineering graduates in India eyeing TCS or Infosys as a first career step, or H-1B holders hoping to move from services to product companies — the signal is more complicated. If AI copilots can handle the rote work that once required a junior engineer, the entry point into these firms may demand higher skills from day one. The traditional apprenticeship model, where fresh graduates learned on the job through repetitive coding tasks, is being quietly compressed.

Microsoft's global numbers add context. Copilot now has 20 million paid seats worldwide, with quarterly additions growing by more than 250 per cent. Customers with more than 50,000 seats have quadrupled year-on-year. The three Indian firms represent the sharpest concentration of adoption anywhere in the world — a distinction that is both a competitive advantage and a preview of what the rest of the industry will face.

## The bottom line

Judson Althoff, CEO of Microsoft's commercial business, framed the milestone in aspirational terms: AI impact at this scale is "no longer measured solely by time saved" but by "how organisations operate, compete, and grow." That is the optimistic reading. The realistic reading is simpler: the companies that built India's IT empire on human capital are now building their future on the assumption that less human capital, augmented by AI, will be enough."""
    },

    # ── Article 2: UPI goes live in Cambodia ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Your PhonePe Now Works in Phnom Penh. UPI Just Landed in Its Ninth Country.",
        "subheadline": "India's digital payments network went live in Cambodia on June 2, connecting to 4.5 million merchants and pushing UPI's international footprint deeper into Southeast Asia.",
        "slug": make_slug("upi-live-cambodia-npci-ninth-country-digital-payments"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For NRIs who travel frequently, UPI's expanding international reach means one less reason to carry foreign currency or pay steep card transaction fees. Cambodia joins a growing list of countries where an Indian Google Pay or PhonePe account works at the checkout counter — a quiet convenience that reflects India's growing digital-infrastructure influence.",
        "tags": ["upi", "digital-payments", "india-cambodia", "npci", "fintech", "digital-public-infrastructure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/money-and-banking/upi-cambodia-qr-code-merchants/article69254890.ece"},
            {"name": "Livemint", "url": "https://www.livemint.com/technology/upi-goes-live-cambodia-indian-tourists-khqr-merchants/"},
            {"name": "Madhyamam Online", "url": "https://www.madhyamamonline.com/en/business/upi-live-cambodia-indian-tourists-payments"},
            {"name": "The Asset", "url": "https://www.theasset.com/article/52411/interoperable-digital-payment-systems-bridge-more-markets"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12935064/pexels-photo-12935064.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A smartphone scanning a QR code at a retail checkout counter",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The Reserve Bank of India confirmed on June 4 that UPI payments went live in Cambodia on June 2, launched at a ceremony in Phnom Penh attended by the National Bank of Cambodia's governor and RBI representatives. Indian travellers can now scan KHQR codes — Cambodia's national QR standard — at more than 4.5 million merchant outlets across the country, paying directly from their linked Indian bank accounts through familiar UPI apps.

The integration was built through a partnership between NPCI International Payments Limited, the overseas arm of India's National Payments Corporation, and ACLEDA Bank, Cambodia's largest commercial bank and the designated operator of the KHQR network. It works the way domestic UPI does: scan, authenticate, pay. The transaction settles in real time, the merchant sees Cambodian riel, and the Indian user pays in rupees.

## Nine countries and counting

Cambodia is the ninth country where UPI now works for merchant payments, joining Bhutan, France, Mauritius, Nepal, Qatar, Singapore, Sri Lanka and the United Arab Emirates. The pattern is clear — each new corridor targets destinations where Indian tourists and business travellers spend money, replacing the friction of foreign-currency exchange and the transaction fees of international debit cards.

The RBI's latest annual report notes that efforts are under way to link UPI with fast-payment systems in additional countries. The pipeline is active. India and Ghana announced a six-month timeline to operationalise UPI integration, which would mark UPI's first footprint in West Africa. A partnership between PayU and 8B is working to bring UPI acceptance to Kazakhstan, Uzbekistan and Kyrgyzstan. And as of February 2026, India has signed memorandums of understanding with 23 countries for sharing or cooperation on the India Stack — the broader digital public infrastructure that includes UPI, Aadhaar and DigiLocker.

## The mechanics of payment diplomacy

What makes UPI's expansion distinctive is its architecture. Unlike Visa or Mastercard, which operate as private networks with merchant discount rates, UPI was built as public digital infrastructure — zero-cost at the core, interoperable across banks, and now being exported as a government-to-government technology-sharing initiative.

Ritesh Shukla, managing director of NPCI International, described the Cambodia launch as extending "India's digital payment innovations to global markets through trusted partnerships." The phrasing is diplomatic, but the subtext is strategic: India is positioning UPI as an alternative to the card networks that dominate global retail payments, offering a model that developing countries can adopt without paying Western intermediary fees.

Cambodia's adoption follows a pattern seen elsewhere. Singapore's PayNow-UPI link, operational since 2023, allows real-time transfers between the two countries. In the UAE, Indian tourists can use Google Pay and BHIM to scan NEOPAY or Network International QR codes at shops and duty-free counters, seeing the price in dirhams but settling in rupees. France enables UPI payments at merchants through a Lyra network partnership, targeting the significant Indian tourist flow through Paris.

## Why NRIs should pay attention

For Indians living abroad, UPI's international expansion has a practical everyday dimension. Any NRI who maintains an Indian bank account — and most do, given family obligations, investments and property — can now use that account for payments in a growing list of countries. The convenience is modest when visiting Phnom Penh, but the direction of travel matters: as UPI corridors multiply, the friction of being an Indian abroad with Indian money keeps shrinking.

The bigger picture is what UPI represents for India's technology influence. A decade ago, the country's most visible digital export was IT services — engineers writing code for American banks. Today, it is public digital infrastructure: a payments system designed in India, built for Indian scale, and now being adopted by countries from Southeast Asia to West Africa. For the diaspora, that shift from services exporter to standards setter carries a different kind of pride — and potentially a different kind of opportunity, as the companies building UPI's international layer look for talent that understands both Indian systems and global markets.

The second phase of the Cambodia integration, which will enable Cambodian travellers to make payments at UPI-enabled merchants in India, is expected to follow. When it does, the corridor becomes truly bilateral — and the template becomes harder for other countries to ignore."""
    },

    # ── Article 3: Google Gemma 4 12B ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Google Just Open-Sourced an AI That Runs on a Laptop. Indian Developers Stand to Gain the Most.",
        "subheadline": "Gemma 4 12B fits in 16GB of memory, handles text, images and audio natively, and ships under an Apache 2.0 licence. For India's cost-conscious AI ecosystem, this changes the economics of building.",
        "slug": make_slug("google-gemma-4-12b-open-source-local-ai-indian-developers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Sundar Pichai's Google is open-sourcing frontier AI capabilities that Indian developers and startups can build on without paying for expensive cloud inference. For NRI engineers evaluating whether India's AI ecosystem can compete globally, Gemma 4 signals that the tools gap is narrowing faster than expected.",
        "tags": ["google", "gemma", "open-source-ai", "sundar-pichai", "indian-developers", "local-ai", "deep-learning"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Google AI Blog (via LinkedIn)", "url": "https://www.linkedin.com/posts/nickadobos_gemma-4-12b-activity-7202948201937408000"},
            {"name": "Digit.in", "url": "https://www.digit.in/ai/google-gemma-4-12b-local-ai-model-pcs.html"},
            {"name": "BrightCoding", "url": "https://www.blog.brightcoding.dev/google-gemini-3-revolution/"},
            {"name": "Google Developers Blog", "url": "https://developers.googleblog.com/en/gemma-4-12b/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Alphabet and Google CEO Sundar Pichai, whose company released Gemma 4 under an open-source licence",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Google has released Gemma 4 12B, an open-source AI model that runs entirely on a laptop with 16GB of RAM, handles text, images and audio through a single architecture, and ships under an Apache 2.0 licence that imposes no usage restrictions. It is, by a meaningful margin, the most capable AI model you can run locally without paying anyone for the privilege.

The release, announced through Google's developer channels this week, represents a specific bet: that the future of AI is not only in massive cloud-hosted models but also in smaller, efficient ones that developers can run on their own hardware, modify freely, and deploy without per-token costs. For India's vast developer community — and the growing ecosystem of Indian AI startups building on open models — this is not a theoretical distinction.

## What makes Gemma 4 different

The technical architecture is worth understanding. Unlike most multimodal AI models, which bolt separate encoders for vision and audio onto a language model, Gemma 4 12B processes all modalities through its core language-model backbone. Images pass through a lightweight embedding module rather than a full vision encoder. Raw audio signals are projected directly into the same token space as text. The result is a model that handles text, images and audio natively, without the memory overhead of running multiple sub-models.

Google says Gemma 4 12B delivers benchmark performance approaching its larger 26B-parameter sibling, but at less than half the memory footprint. It includes Multi-Token Prediction drafters to reduce inference latency — meaning it generates responses faster without sacrificing quality. And it is the first mid-sized Google model with native audio input support, opening the door to voice-first applications that previously required cloud-scale compute.

The 16GB memory requirement matters because it maps precisely to the hardware that millions of developers already own. A MacBook Air with M-series silicon, a mid-range Windows laptop with a recent GPU, or a Linux workstation with a decent amount of RAM — any of these can run Gemma 4 12B at usable speeds. No cloud subscription. No API rate limits. No per-query billing.

## Why India's AI builders should care

India has more software developers than any country except the United States, and a disproportionate share of them work at smaller companies or as independents where cloud AI costs are a genuine constraint. Running inference on GPT-4 or Claude through API calls costs money per token — money that adds up quickly when you are building a product that handles thousands of user queries daily.

Open models like Gemma 4 eliminate that variable cost. A startup in Bangalore building a regional-language chatbot can run Gemma 4 on a single server and pay only for electricity. A developer in Hyderabad prototyping a multimodal search tool can iterate locally without worrying about API bills. An NRI engineer evaluating whether to build an AI product for the Indian market can test feasibility on a laptop before committing to infrastructure.

This is not hypothetical demand. Indian AI startups like Sarvam AI and Krutrim have built significant businesses around making AI work for Indian languages and Indian use cases, often by fine-tuning open models rather than training from scratch. Gemma 4's Apache 2.0 licence means these companies can modify, fine-tune and deploy the model commercially without restrictions — a freedom that proprietary models from OpenAI and Anthropic do not offer.

## The Sundar Pichai factor

It is impossible to discuss Google's AI strategy without noting that its CEO is Sundar Pichai, born in Chennai and educated at IIT Kharagpur. Pichai has consistently pushed Google toward open-sourcing its AI research, from the original TensorFlow framework to the Gemma model family. This is not sentimentality — it is competitive strategy. By making its models freely available, Google builds an ecosystem of developers who know Google's tools, use Google's infrastructure, and are more likely to choose Google Cloud when they need to scale.

But the effect on Indian AI development is real regardless of the motive. Google's DeepMind and Brain labs employ significant numbers of Indian-origin researchers. The models they build, and open-source, flow directly into the hands of developers across India who lack the resources to train such models themselves. Each release like Gemma 4 compresses the gap between what a well-funded American AI lab can do and what an Indian startup can access.

## The competitive landscape

Gemma 4's release arrives alongside NVIDIA's push to put AI on personal computers through its RTX Spark chips, and Meta's continued commitment to open-sourcing its Llama model family. The convergence is notable: the industry's largest companies are betting that local, on-device AI will be as important as cloud AI — and they are competing to be the default choice for developers who want to run models on their own hardware.

For Indian developers and NRI engineers watching this unfold, the practical takeaway is straightforward. The cost of experimenting with serious AI has dropped to nearly zero. The models are open, the hardware is sufficient, and the licence terms are permissive. What remains is the harder part: building products that people actually want to use."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
