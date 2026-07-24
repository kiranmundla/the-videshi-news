#!/usr/bin/env python3
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Qualcomm's ByteDance Deal Signals a New Front in the AI Chip War",
        "subheadline": "The San Diego chipmaker lands its first major data-centre ASIC customer — and thousands of Indian engineers in Hyderabad and Bangalore are at the centre of the pivot.",
        "slug": make_slug("qualcomm-bytedance-ai-asic-chip-deal-india-engineers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Qualcomm employs thousands of Indian chip designers in Hyderabad, Bangalore, and Chennai. This deal reshapes their career trajectory from mobile SoCs to cutting-edge AI inference silicon — and puts Indian engineering talent at the heart of the next chip battleground.",
        "tags": ["qualcomm", "bytedance", "ai-chips", "semiconductors", "indian-engineers", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/qualcomm-strikes-ai-chip-deal-with-tiktok-owner-bytedance-bloomberg-news-reports-2026-05-26/"},
            {"name": "Bloomberg News", "url": "https://www.bloomberg.com/news/articles/2026-05-26/qualcomm-strikes-ai-chip-deal-with-bytedance"},
            {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/qualcomm-bytedance-asic-ai-chip.html"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Closeup of electronic microchips on a circuit board — the kind of silicon at the centre of Qualcomm's new AI push. Photo: Pexels",
        "body": """Qualcomm has spent three decades as the company that made your phone's brain. Now it wants to make the brain for artificial intelligence itself.

On Monday, Bloomberg reported that ByteDance — the Chinese parent of TikTok — has agreed to buy millions of Qualcomm-designed application-specific integrated circuits (ASICs) for its AI data centres. ByteDance becomes the first major customer for Qualcomm's nascent AI infrastructure division, and the deal sent Qualcomm shares up roughly 5 per cent in a single session.

The implications reach far beyond San Diego's headquarters. They stretch to Hyderabad's HITEC City, to Bangalore's Outer Ring Road, and to Chennai's IT corridor — where thousands of Qualcomm's chip architects and verification engineers have spent years refining mobile system-on-chip designs. Many of them will now be retooled to work on AI inference silicon.

## From Snapdragon to the Server Rack

Qualcomm's pivot has been telegraphed for months. At CES 2026, the company unveiled its Dragonwing IQ10 robotics chip and hinted at custom silicon for cloud workloads. But landing ByteDance — a company that runs one of the world's most compute-hungry recommendation engines — is a different order of magnitude.

The ASICs are designed to support ByteDance's AI agent software, the layer that powers everything from TikTok's eerily accurate content feed to the company's nascent generative AI products. Unlike Nvidia's general-purpose GPUs, ASICs are custom-built for specific workloads, trading flexibility for raw efficiency. For ByteDance, that means lower power bills and faster inference at scale.

For Qualcomm, it means a credible second act beyond smartphones, a market where growth has plateaued and Chinese competitors like MediaTek are closing the gap.

## What This Means for Indian Engineers

Qualcomm's India operations are not satellite offices. The company's Hyderabad campus is its largest design centre outside the United States, employing several thousand engineers across chip architecture, RF design, modem development, and software. Bangalore and Chennai add thousands more.

These teams built the Snapdragon platform that powers most of the world's Android phones. Now, the same talent pipeline is being redirected. Engineers who once optimised power-performance ratios for mobile CPUs will increasingly work on AI inference accelerators — silicon designed to run large language models and recommendation systems at hyperscale.

For Indian professionals in the semiconductor space, the shift opens a new career vector. AI chip design commands a salary premium of 20-40 per cent over traditional mobile SoC roles, according to industry recruiters. And unlike some AI roles that require proximity to model training teams in the Bay Area, chip design work can be distributed — which is precisely how Qualcomm's India centres already operate.

## The Geopolitical Undercurrent

There is an uncomfortable subtext to this deal. ByteDance is a Chinese company purchasing American-designed chips for AI data centres, at a moment when Washington has spent three years trying to constrain China's access to advanced AI hardware. Qualcomm's ASICs are not GPUs, and they may not fall under the same export controls that have targeted Nvidia's H100 and AMD's MI300. But the optics are delicate, and regulatory scrutiny is likely.

For Indian-origin engineers caught between American employers and Chinese customers, the geopolitics are more than abstract. India's own semiconductor mission — backed by $18.2 billion in newly approved projects — positions the country as a potential neutral ground in the chip cold war. Engineers with Qualcomm ASIC experience will be highly sought after if India's fab ambitions materialise.

## The Bigger Picture

Qualcomm is not the only company chasing custom AI silicon. Broadcom designs ASICs for Google and Meta. Marvell builds them for Amazon and Microsoft. But Qualcomm's entry adds a new competitor with deep mobile IP, massive India-based engineering scale, and a decades-long relationship with the ARM instruction set that increasingly underpins AI inference workloads.

Whether this deal proves to be Qualcomm's inflection point or a footnote depends on execution. But for the thousands of Indian engineers who will design, verify, and tape out these chips, the next chapter of their careers just got considerably more interesting."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Pichai's Alphabet Lands the Biggest AI Deal of the Year — Powering Apple's Siri",
        "subheadline": "Apple will pay Google roughly $1 billion a year to run Gemini under the hood of its voice assistant. For Indian-origin tech leaders, it is a full-circle moment.",
        "slug": make_slug("apple-google-gemini-siri-deal-sundar-pichai-wwdc"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Sundar Pichai's Alphabet cements its position as the foundational AI infrastructure provider for 2 billion Apple devices. Indian engineers at both companies are central to the integration, and NRI investors holding both AAPL and GOOGL have reason to pay close attention.",
        "tags": ["apple", "google", "gemini", "siri", "sundar-pichai", "ai", "wwdc-2026"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Barron's", "url": "https://www.barrons.com/articles/apple-stock-price-ai-record-high"},
            {"name": "eMarketer", "url": "https://www.emarketer.com/content/apple-leans-on-google-gemini-next-gen-siri-overhaul"},
            {"name": "Apple Gadget Hacks", "url": "https://apple.gadgethacks.com/news/apple-chooses-googles-gemini-ai-new-siri-2026/"},
            {"name": "CDO Magazine", "url": "https://cdomagazine.tech/articles/apple-taps-google-gemini-power-next-generation-siri"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Sundar Pichai, CEO of Alphabet, whose Gemini AI models will power Apple's next-generation Siri. Photo: Wikimedia Commons",
        "body": """When Apple announces its next-generation Siri at WWDC on June 8, the voice assistant will sound like Apple. But underneath, it will think like Google.

Apple has agreed to a multi-year deal worth approximately $1 billion annually to license Alphabet's Gemini AI models as the foundational intelligence layer for Siri. The partnership, confirmed by multiple reports and first detailed by Bloomberg, represents the most consequential AI deal of 2026 — and it was closed under the watch of Sundar Pichai, the Madurai-born CEO who has quietly turned Alphabet into the AI infrastructure company that even its fiercest rival cannot do without.

## The Deal

The arrangement is more than a simple licensing agreement. Apple evaluated AI models from OpenAI, Anthropic, and Google before selecting Gemini as the backbone for Siri's overhaul. Under the deal, Gemini will power Siri's summarisation, planning, cross-app actions, and contextual understanding across Apple's estimated 2 billion active devices.

Apple will retain control over user data through its Private Cloud Compute infrastructure, routing queries through Apple-managed servers rather than directly to Google. Siri's responses will be shaped by Apple's UX layer, but the reasoning engine beneath will be Gemini — specifically, models optimised for on-device and hybrid inference.

The arrangement echoes the existing Google Search deal, where Apple collects billions annually to keep Google as the default search engine on Safari. That deal has drawn antitrust scrutiny. This one will likely attract even more.

## Pichai's Quiet Victory

For Sundar Pichai, the deal validates a strategy that looked uncertain as recently as 2024, when OpenAI's ChatGPT threatened to relegate Google's AI to second place. Pichai invested aggressively in Gemini — shipping the 2.0 Ultra and 3.5 Flash models, embedding AI into Search, Workspace, and Android, and building out the cloud infrastructure to serve it all.

Landing Apple as a customer is the payoff. It means Gemini will run on iPhones, iPads, Macs, and Apple Watches — devices that Google's own Pixel line cannot match in market penetration. For Alphabet shareholders, the revenue is meaningful. For Pichai personally, it cements his legacy as the executive who kept Google relevant in the age of generative AI.

He is not the only Indian-origin leader shaping this deal. Neal Mohan, the Indian-American CEO of YouTube (an Alphabet subsidiary), has pushed Gemini integration into YouTube's creator tools. On Apple's side, the engineering teams building Siri's new architecture include significant Indian-origin talent across machine learning, natural language processing, and systems engineering.

## What NRI Investors Should Watch

The Apple-Google AI partnership has direct implications for diaspora investors, many of whom hold both AAPL and GOOGL in their portfolios.

For Apple, the deal is an admission that its internal AI efforts — branded Apple Intelligence — were not sufficient to compete. The company is paying to outsource its reasoning layer, which carries both cost and dependency risk. Analysts at Investor's Business Daily argued that Apple's true advantage lies not in model development but in owning the "trusted endpoint" — the device, the identity, the payments, the apps. If that thesis holds, the $1 billion annual Gemini fee is a rounding error on a platform that generated $394 billion in revenue last year.

For Alphabet, the deal diversifies Gemini's revenue beyond Google's own products. If Gemini can serve Apple's 2 billion devices reliably, it becomes the default AI middleware layer for the consumer internet — a position of enormous strategic power.

WWDC on June 8 will be the first public demonstration of the integrated system. Apple is expected to showcase a conversational Siri capable of multi-step task execution, on-screen awareness, and natural language Shortcuts — all powered by Gemini. The keynote begins at 10 AM Pacific, or 10:30 PM IST, for those watching from Bangalore.

## The Larger Pattern

Pichai. Nadella. Mehrotra. Krishna. The list of Indian-origin executives running trillion-dollar technology platforms continues to grow. What makes the Apple-Gemini deal distinctive is that it places an Indian-led company's AI at the core of another company's most personal product — the voice assistant that 2 billion people talk to every day.

For the Indian diaspora, it is worth pausing on what that represents. Not just individual success, but institutional influence — the kind that shapes the AI infrastructure the entire world will run on."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Tech Hubs Are Filing More Patents Than Ever. AI Is About to Accelerate That.",
        "subheadline": "Global capability centres in Hyderabad, Bangalore, and Gurugram generated $98.4 billion in revenue last year — four years ahead of schedule. Now AI tools are turning them into IP factories.",
        "slug": make_slug("india-gcc-patents-ai-innovation-hubs-nasscom"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For NRIs weighing return-to-India decisions or considering investment in Indian tech, the GCC transformation signals that India's role is shifting from execution to invention. The patent surge means more senior, IP-generating roles — and higher salaries — in Indian tech hubs.",
        "tags": ["india-gcc", "patents", "innovation", "nasscom", "ai", "hyderabad", "bangalore", "nri-careers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/litigation/ai-turbocharge-patent-creation-india-tech-hubs-executives-say-2026-05-27/"},
            {"name": "Nasscom", "url": "https://nasscom.in/knowledge-center/publications/gcc-india-landscape-2024"},
            {"name": "Nasscom-Zinnov GCC Report", "url": "https://nasscom.in/knowledge-center/publications/gcc-india-report-2025"}
        ]),
        "score_total": 74,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36926207/pexels-photo-36926207.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Hyderabad's tech parks house some of the world's largest global capability centres. Photo: Pexels",
        "body": """For years, the standard critique of India's technology sector went something like this: clever engineers, cheap labour, someone else's ideas. India executed. It did not invent.

That narrative is cracking. At a Reuters summit this week, executives from Publicis Groupe's Epsilon, Kimberly-Clark, and Daimler Truck described a new reality: their Indian global capability centres (GCCs) are generating patents, trade secrets, and proprietary technology at an accelerating pace — and artificial intelligence is about to push the rate even higher.

"The number of IPs, the patents and the trade secrets created by GCCs in India is already increasing," said Radhakrishnan Kodakkal, head of Daimler Truck Innovation Center India. "AI would accelerate it."

## The Numbers

India's GCC ecosystem is no longer a rounding error. According to a Nasscom-Zinnov report, Indian GCCs generated approximately $98.4 billion in revenue in the last fiscal year — hitting an industry target four years ahead of schedule. Patent filings in India rose 11.3 per cent to over 90,000 in fiscal 2024, with nearly half originating from multinational companies.

But those figures understate reality. Much of the intellectual property created in Indian centres is filed through parent entities in the United States and Europe. "At Kimberly-Clark, we do not do any patent filing from India. Whatever we do, we do through the U.S. because of the difficulty here," said Deena Dayalan, the company's global head of digital operations.

The difficulty is structural. India's patent office has fewer than 1,000 examiners, compared to over 8,000 at the US Patent and Trademark Office. Filing takes five to six months — roughly double the American timeline — and approval stretches into years. A separate request is required to initiate substantive review, a step the US system handles automatically.

## The AI Accelerant

What changes the equation is AI's effect on the work itself. Engineers at Indian GCCs who once spent their days on maintenance coding, quality assurance, or process automation are increasingly being freed to work on higher-value problems — the kind that produce patentable inventions.

AI coding assistants handle the routine. Human engineers focus on architecture, novel algorithms, and system design. The result is a workforce that is not just cheaper than its Western counterparts but increasingly productive on the metrics that matter most: original intellectual property.

Pratik Nath, managing director of Epsilon India, put it directly: "I see more and more IP work happening here."

For the roughly 1,700 GCCs operating in India — housing teams from Google, Microsoft, Amazon, Goldman Sachs, Walmart, and dozens of others — the shift redefines their strategic value. A centre that generates patents is harder to offshore, harder to downsize, and harder to replace than one that merely processes tickets.

## What This Means for the Diaspora

For Indian Americans working in technology, the GCC transformation creates a new set of calculations.

First, the return-to-India proposition is improving. Senior roles in patent-generating GCCs command salaries that, adjusted for purchasing power, rival mid-level positions in the Bay Area. An NRI engineer who returns to lead an innovation team at a Hyderabad GCC may find the intellectual challenge comparable to what they left behind — with a fraction of the housing cost.

Second, the investment thesis is sharpening. India's technology services exports have traditionally been valued on labour arbitrage — how cheaply Indian firms could deliver work. A sector that generates intellectual property commands a different multiple. For NRI investors evaluating Indian tech stocks — Infosys, TCS, Wipro, and the newer pure-play GCC operators — the patent surge signals a structural upgrade in the value chain.

Third, the skills gap is narrowing in unexpected ways. Indian GCCs are now training engineers not just in execution but in invention methodology — how to identify patentable innovations, document them, and navigate the filing process. This capability was once concentrated in R&D labs in Silicon Valley and Cambridge. It is now being industrialised in Bangalore and Gurugram.

## The Bottleneck

India's patent infrastructure remains the weakest link. The backlog is real, the examiner shortage is chronic, and the procedural friction discourages domestic filing. Recent digitisation efforts — online filing, centralised application allocation, video hearings — have helped, but the gap with Western patent offices remains wide.

If India wants to fully capitalise on its GCC-driven innovation surge, patent reform is not optional. The engineers are ready. The AI tools are in place. The bureaucracy needs to catch up.

For now, though, the direction is clear. India's tech hubs are no longer just building someone else's products. They are building their own ideas — and filing the paperwork to prove it."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
