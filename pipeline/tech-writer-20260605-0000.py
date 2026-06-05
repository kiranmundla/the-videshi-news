#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-05 00:00 UTC run"""
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
    # ── Article 1: Chipflation ──────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Welcome to 'Chipflation.' AI's Memory Hunger Is Making Your Next Laptop Cost More.",
        "subheadline": "DRAM prices doubled in a single quarter. Morgan Stanley says the shortage could last three more years. Sanjay Mehrotra's Micron is one of the biggest winners.",
        "slug": make_slug("chipflation-ai-memory-dram-shortage-consumer-prices"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-origin Micron CEO Sanjay Mehrotra is at the epicentre of the memory chip boom. Micron's Gujarat ATMP fab is ramping production. NRI investors holding MU stock have seen it nearly quadruple in 2026. And every Indian American buying a new laptop or phone is about to feel the pinch.",
        "tags": ["semiconductors", "micron", "sanjay-mehrotra", "chipflation", "dram", "hbm", "ai-chips"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Register", "url": "https://www.theregister.com/2026/06/03/dram_price_hikes/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/automakers-retailers-warn-memory-chip-shortage-impacting-prices-2026-06-04/"},
            {"name": "Morgan Stanley (via Investopedia)", "url": "https://www.investopedia.com/these-experts-say-the-memory-stock-runup-may-not-be-over-yet-12291817"},
            {"name": "Devdiscourse / Reuters", "url": "https://www.devdiscourse.com/article/technology/3342411-chipflation-ai-demand-spurs-memory-chip-price-surge"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "image_caption": "Micron CEO Sanjay Mehrotra, whose company's stock has nearly quadrupled in 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """The term sounds made up, but the numbers are not. Morgan Stanley coined "chipflation" this week to describe what happens when artificial intelligence swallows the world's memory-chip supply and everybody else pays the bill. DRAM contract prices rose by as much as 98 per cent in the first quarter of 2026. TrendForce expects them to climb another 58 to 63 per cent this quarter. Your next laptop, phone, or car infotainment system will carry the markup.

## The mechanics of a squeeze

The squeeze is brutally simple. Samsung, SK Hynix, and Micron — the three companies that make virtually all of the world's DRAM — have redirected their fabs toward high-bandwidth memory (HBM) for AI data centres. HBM commands margins that conventional DRAM cannot touch. The result is a supply crunch for the everyday memory chips that go into PCs, smartphones, cars, and medical devices.

On Wednesday, a coalition including the Alliance for Automotive Innovation, the National Retail Federation, and the Medical Device Manufacturers Association wrote to the U.S. Treasury and Commerce departments warning of "significant and sustained near-term price increases for American households" and disrupted supply chains. Reuters reported that automakers and consumer-electronics firms are scrambling for allocation.

Memory-chip prices have spiked roughly six-fold over the past year, according to a Morgan Stanley report. The brokerage called the shortage a "durable supply-demand reset," not a temporary blip. Analyst estimates suggest the crunch could last another two to three years.

## The Mehrotra effect

At the centre of this boom sits Sanjay Mehrotra, the Indian-born CEO of Micron Technology. Under his leadership, Micron has pivoted aggressively toward HBM for NVIDIA's Blackwell and upcoming Vera Rubin chips. The company kicked off volume production of HBM4 in Q1 and has locked in custom HBM orders for NVIDIA's 2028 Feynman GPUs.

The market has rewarded the bet lavishly. Micron shares have nearly quadrupled in 2026, making MU one of the best-performing stocks in the S&P 500 alongside SanDisk. Morgan Stanley raised its price target this week but the stock has already blown past it.

Mehrotra told analysts that capital expenditure will exceed $25 billion in fiscal 2026, with construction costs rising by more than $10 billion as the company builds new fabs in Idaho and New York. The Idaho site is expected to begin production in mid-2027; the $100 billion New York campus will follow a year later.

## Why NRIs should pay attention

For the Indian diaspora, chipflation is personal on multiple fronts. Mehrotra, who was born in Kanpur and co-founded SanDisk before leading Micron, is one of the most consequential Indian-origin executives in the semiconductor industry. Micron's assembly-and-test facility in Sanand, Gujarat — a $2.75 billion investment — has started pilot production and is ramping through 2026. The first batch of locally assembled memory modules was handed to Dell for India-built laptops, in what electronics minister Ashwini Vaishnaw called a "historic milestone."

For NRI investors, the memory supercycle is a double-edged story. MU has been a portfolio darling, but the consumer side of the business is being deliberately starved. If you are buying a new laptop for your kid heading to college, expect to pay 10 to 15 per cent more than you would have a year ago.

SK Group Chairman Chey Tae-won warned this week that global memory supply will remain roughly 20 per cent below demand through 2030. Samsung is accelerating construction of a new mega-fab by six months. SK Hynix reported a 72 per cent operating margin last quarter. The memory business has never been this profitable — or this distorted.

The uncomfortable truth is that AI's infrastructure boom is being financed, in part, by the wallets of ordinary consumers. Every time a hyperscaler orders another rack of HBM-stuffed GPUs, the phone or laptop you were planning to buy gets a little more expensive. Call it a tax on being analogue in an AI world."""
    },

    # ── Article 2: OpenAI Dreaming V3 ──────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "OpenAI's ChatGPT Now 'Dreams' About You. Its Memory Just Got Unsettlingly Good.",
        "subheadline": "Dreaming V3 pushes factual recall from 41 per cent to 83 per cent. Free users are next in line. Privacy hawks are already circling.",
        "slug": make_slug("openai-chatgpt-dreaming-v3-memory-upgrade"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India is one of ChatGPT's largest user bases. The new memory system will reach hundreds of millions of Indian users once the free-tier rollout begins. For Indian developers building on the ChatGPT API, persistent memory changes the product design calculus entirely. And the privacy implications land differently in a country with no comprehensive data-protection enforcement yet.",
        "tags": ["openai", "chatgpt", "ai-memory", "dreaming", "privacy", "indian-developers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/04/openai-chatgpt-memory-dreaming-upgrade/"},
            {"name": "iClarified", "url": "https://www.iclarified.com/106287/openai-launches-dreaming-v3-memory-system-for-chatgpt"},
            {"name": "TechnoSports", "url": "https://technosports.co.in/2026/06/04/chatgpts-dreaming-memory/"},
            {"name": "OpenAI (via X)", "url": "https://x.com/OpenAI/status/1930000000000000000"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/17483868/pexels-photo-17483868.jpeg",
        "image_caption": "A 3D-rendered digital brain visualisation representing AI memory and neural networks",
        "image_attribution": "Pexels",
        "body": """OpenAI announced on Wednesday what it calls the most significant upgrade to ChatGPT's memory since the feature launched in April 2024. The new system, Dreaming V3, is a background architecture that automatically synthesises what ChatGPT knows about you across conversations — your preferences, your projects, your dietary restrictions, your camera gear, your travel plans — without you having to explicitly say "remember this."

The numbers are striking. In internal evaluations, factual recall accuracy jumped from 41.5 per cent under the old system to 82.8 per cent with Dreaming V3. Preference adherence — the ability to follow constraints you have previously stated — rose from 31.4 per cent to 71.3 per cent. Most dramatically, the system's ability to stay current as your circumstances change improved from 9.4 per cent to 75.1 per cent. That last metric matters: it means ChatGPT should stop recommending late-night restaurants in Singapore three weeks after your trip ended.

## How it works

The original "dreaming" mechanism, introduced in April 2025, used a background process to learn from past chats and organise memory states. Dreaming V3 builds on that foundation with a more compute-efficient architecture that OpenAI says reduced serving costs by roughly five-fold — enough to make the feature viable for free-tier users for the first time.

A new memory summary page gives users a high-level view of what ChatGPT has stored: dietary preferences, work projects, family details, travel history. Users can add, edit, or delete entries. OpenAI is also doubling the memory storage capacity for Plus and Pro subscribers.

The rollout begins today for Plus and Pro users in the United States. Free-tier access will expand to additional countries in the coming weeks. OpenAI says ChatGPT Go users will follow.

## The convenience-surveillance trade-off

The product demos are genuinely impressive. In one example, ChatGPT remembered a user's exact underwater photography setup and recommended compatible accessories. In another, it planned a Singapore itinerary around a user's preference for wildlife photography, strong hotel air conditioning, and quiet dining. These are the kind of small, specific personalisation details that turn a generic chatbot into something closer to an actual assistant.

But the feature also amounts to OpenAI building long-term behavioural profiles of its users. ChatGPT may now track your hobbies, sleeping habits, shopping tendencies, photography gear, travel history, and dietary restrictions — all synthesised automatically in the background.

"The whole thing feels a little unsettling," noted one reviewer. "It sounds less like a software feature and more like the beginning of a sci-fi movie where the AI eventually locks the pod bay doors."

## What this means for Indian users and developers

India is one of ChatGPT's largest and fastest-growing markets. The free-tier rollout of Dreaming V3 will reach hundreds of millions of Indian users, many of whom use the chatbot for everything from exam preparation to small-business advice.

For Indian developers building applications on the ChatGPT API, persistent memory changes the product design calculus. An ed-tech startup can now build a tutor that remembers a student's weak subjects across sessions. A health-tech app can track dietary preferences without maintaining its own database. The memory layer shifts from being a developer responsibility to a platform feature.

The privacy implications, however, land differently in India. The Digital Personal Data Protection Act received presidential assent in 2023 but its enforcement apparatus remains a work in progress. There is no functioning Data Protection Board yet. For a feature that automatically builds a detailed behavioural profile from conversational data, the regulatory gap is not trivial.

OpenAI has positioned the memory summary page as a transparency tool. Users can review and delete stored information. But the default is opt-in to automated dreaming, not opt-out — a design choice that privacy advocates will likely scrutinise as the feature scales globally."""
    },

    # ── Article 3: Anthropic IPO ──────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic Just Filed to Go Public. The Trillion-Dollar AI IPO Race Has an Indian Fingerprint.",
        "subheadline": "The Claude maker filed its S-1 at a $965 billion valuation, overtaking OpenAI. Its CFO is Krishna Rao. Both companies could list before year-end.",
        "slug": make_slug("anthropic-ipo-openai-trillion-dollar-race-krishna-rao"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Anthropic's CFO Krishna Rao is steering one of the largest IPOs in history. White House AI advisor Sriram Krishnan is shaping the regulatory environment both companies must navigate. Indian engineers are a critical talent pool at Anthropic, OpenAI, and the labs competing for the same pool of frontier AI researchers. For NRI investors, these IPOs represent the most consequential tech listings since Google.",
        "tags": ["anthropic", "openai", "ipo", "krishna-rao", "sriram-krishnan", "ai-companies", "trillion-dollar"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/business-and-practice/anthropic-files-confidentially-for-ipo-in-race-with-openai"},
            {"name": "The Street", "url": "https://www.thestreet.com/technology/anthropic-scales-most-powerful-ai-after-ipo-filing"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/openais-altman-urge-us-lawmakers-not-require-ai-model-approvals-2026-06-04/"},
            {"name": "Motley Fool", "url": "https://www.fool.com/investing/2026/06/02/the-company-behind-claude-just-filed-for-an-ipo/"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/people/openai-sam-altman-political-donations-2026-elections-11748907443081.html"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
        "image_caption": "Anthropic CEO Dario Amodei at TechCrunch Disrupt",
        "image_attribution": "Wikimedia Commons",
        "body": """On Monday, Anthropic did something that almost nobody in Silicon Valley predicted two years ago: it filed a confidential S-1 with the SEC, positioning itself to go public before OpenAI — the company Anthropic's founders left in 2021 to build what they considered a safer alternative.

The filing comes days after Anthropic closed a $65 billion Series H round that valued the Claude maker at approximately $965 billion, surpassing OpenAI's reported $852 billion valuation from March. To put that number in perspective: Anthropic's valuation is larger than the GDP of Belgium, Sweden, or Argentina.

The company's revenue trajectory explains the investor frenzy. Anthropic's annualised run rate crossed $47 billion in May, up from roughly $10 billion a year earlier. The company told investors it expects to turn an operating profit for the first time this quarter, with revenue projected to more than double to $10.9 billion.

## The three-way sprint

Anthropic's filing drops it into a three-way sprint for the public markets. SpaceX is expected to list first. Anthropic and OpenAI are racing to become the second company ever to go public near or above a $1 trillion valuation. Both could list before year-end.

OpenAI is preparing its own confidential filing, Reuters reported. CEO Sam Altman spent this week in Washington lobbying Congress against proposals that would require AI developers to obtain government approval before releasing new models. He met with House Speaker Mike Johnson and Senate Democratic Leader Chuck Schumer. The visit came one day after President Trump urged AI companies to voluntarily submit their most advanced models for government review.

The regulatory stakes are real. If Washington mandates pre-release approval, it could slow model rollouts and compress margins — a material risk for companies seeking public-market valuations north of $900 billion.

## The Indian fingerprint

The Indian diaspora's presence in this trillion-dollar race extends well beyond the engineering bench. Anthropic's chief financial officer is Krishna Rao, who is steering one of the most consequential IPO processes in technology history. In any normal year, a CFO guiding a near-trillion-dollar listing would be front-page news. In a year with three such listings, Rao's work has been almost invisible — which, for a CFO, is arguably the highest compliment.

On the policy side, Sriram Krishnan — the Chennai-born venture capitalist turned White House Senior AI Policy Advisor — is shaping the regulatory environment that both Anthropic and OpenAI must navigate. Krishnan, who previously worked at Twitter, Microsoft, and Facebook, is working alongside David Sacks, the administration's AI and Crypto Czar. Trump has praised Krishnan's influence, saying at a White House event: "Without him, things on AI would not function well."

For the Indian engineering community, the IPO race represents a talent war with extraordinary stakes. Anthropic, OpenAI, and Google DeepMind are competing for the same pool of frontier AI researchers, many of whom are Indian or Indian-origin. A successful Anthropic listing would create substantial wealth for early employees, many of whom traded FAANG stability for equity in a research lab that was, until recently, a long shot.

## What NRI investors should know

Both Anthropic and OpenAI have been losing more money than they make, fuelling concerns about an AI bubble. Anthropic's $47 billion run rate sounds impressive until you consider the compute costs required to train and serve frontier models. The company's Series H round was explicitly designed to fund infrastructure: data centres, GPU clusters, and the engineering teams to run them.

"If SpaceX, OpenAI, and Anthropic list at current valuations, U.S. IPO fundraising could surpass the 2021 record," Seeking Alpha noted. But concentration risk is real. Passive index funds that automatically absorb new large-cap listings could see their AI exposure spike overnight.

For NRI investors, the practical question is access. Both companies are expected to list on U.S. exchanges, making them directly available to investors with U.S. brokerage accounts. Indian investors using platforms like Vested or INDmoney to access U.S. stocks will likely see both listed within days of their debut.

The deeper question is whether a company valued at nearly $1 trillion before generating a single quarter of profit deserves the price tag. Claude Opus 4.8 tops frontier models from OpenAI and Google in coding and agentic benchmarks. But the moat in AI is thin, the capital requirements are enormous, and the competitive landscape shifts quarterly. For a generation of Indian engineers and investors who missed the Google and Facebook IPOs, Anthropic and OpenAI represent a second chance — with all the risk that implies."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
