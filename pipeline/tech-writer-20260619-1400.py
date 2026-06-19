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

article1_body = """Google has finally given its smart speaker a brain transplant. On June 17 it opened pre-orders for the Google Home Speaker — a $99.99 device built from the ground up around Gemini, the company's flagship AI model — with shipping to begin on June 25. The same week, Sundar Pichai's company began pushing Android 17 to Pixel phones, layering Gemini deeper into the operating system that runs most of the world's smartphones.

For Indian Americans, the interesting part is not the hardware. It is what the rollout reveals about how the most consequential Indian-origin executive in technology is trying to win the AI race: by smuggling Gemini into the everyday devices people already own, rather than asking them to download yet another chatbot.

## The strategy beneath the speaker

The Home Speaker is modest on paper — a quad-core processor, a dedicated chip for on-device AI tasks, Wi-Fi 6, and a single 58mm driver that Google claims delivers 2.5 times the bass of the old Nest Mini. But it is the first hardware Google has designed specifically for conversational Gemini, and the company has been explicit that this is the template for its entire smart-home line.

The catch is the business model. Some of the more advanced features will sit behind a monthly subscription, the same pairing of cheap hardware and paid AI that Amazon and Apple are now chasing. Google is betting that once Gemini lives in your kitchen, your watch, and your phone, the subscription becomes hard to cancel.

Android 17 makes the same wager at far greater scale. The update lets Pixel users generate video and original music through Gemini, create AI avatars, and — in a feature debuting in India — screen unknown callers before picking up. The most powerful capabilities, including multi-step app automation and an "Auto Browse" mode for Chrome, will arrive later this summer.

## Why the diaspora should pay attention

Three reasons, each pointing at a different part of the Indian American experience.

First, the talent. Pichai, born in Madurai and a product of IIT Kharagpur, sits atop a company whose AI infrastructure push is increasingly run by other immigrants — Amin Vahdat, promoted in December to chief technologist for Google's AI build-out, among them. For the tens of thousands of Indian engineers inside Alphabet, Gemini's success is not abstract. It determines which teams get funded, which products survive the next reorganization, and whose stock options stay above water.

Second, the home market. India is not a footnote in this launch; it is a test bed. The India-specific call-screening feature signals that Google views the country's hundreds of millions of Android users as central to Gemini's growth. NRIs with family back home will likely see relatives running Gemini-powered Pixels and, eventually, Home Speakers before the features reach saturation in the West.

Third, the competitive stakes. Pichai is fighting a two-front war. OpenAI just poached Noam Shazeer, a co-lead of the Gemini models, underscoring how brutal the talent fight has become. At the same time, Google is quietly building a rival to Nvidia's chip empire on the back of its own Tensor Processing Units. The Home Speaker is the consumer-facing tip of a far larger bet that Google can own the full stack — model, chip, and device.

## The quieter signal

There is a telling detail in how Google shipped Gemini to the Mac this month: Pichai revealed the desktop app was built largely by Antigravity, Google's own autonomous coding tool, going from idea to working prototype in days. For Indian software professionals — many of whom built careers writing exactly the kind of code these tools now generate — it is a reminder that the firm led by one of their own is also racing to automate parts of their craft.

That tension defines the moment. The diaspora has never had more representation at the top of American technology. It has also never faced a clearer signal that the work itself is changing underneath them. A $99 speaker that talks back is the friendly face of a much harder transition — and Sundar Pichai is selling both."""

article2_body = """For years the story of the AI boom had one undisputed villain-hero: Nvidia, the chipmaker whose graphics processors power nearly every large model on earth. That monopoly is now under its most serious assault yet — not from a rival chip startup, but from Nvidia's own biggest customers.

This week Amazon confirmed it is in "exploratory early conversations" to sell its custom Trainium chips to outside companies, a move first reported by Bloomberg. Peter DeSantis, Amazon's AI chief, said AWS has opened talks with potential buyers. Almost simultaneously, The Wall Street Journal detailed how Google is borrowing Nvidia's own playbook — financial guarantees, circular financing, a new $5 billion cloud venture with Blackstone — to push its Tensor Processing Units into rival data centers.

The shift matters far beyond Silicon Valley boardrooms. For the Indian engineers and investors who sit at nearly every layer of this industry, the chip wars are about to reshape careers and portfolios alike.

## Why the customers are revolting

The logic is brutally simple economics. The four largest US hyperscalers — Google, Amazon, Microsoft, and Meta — have collectively guided to between $700 billion and $725 billion of capital spending in 2026, up roughly 75% from 2025. A punishing share of that goes to Nvidia, whose chips command fat margins. Building silicon in-house, even at lower performance, lets these giants claw back some of that money.

Amazon's Trainium effort has been more than a decade in the making, dating to its 2015 acquisition of Annapurna Labs. Anthropic alone has committed hundreds of billions of dollars to run workloads on the chips. Google's TPUs, born from a 2013 "thought experiment" by researcher Jeff Dean, now train Gemini and power Anthropic's models too.

Nvidia's Jensen Huang is unbothered, at least publicly. He has dismissed Google's ability to compete meaningfully, arguing Anthropic is its only significant external TPU customer and challenging anyone to "demonstrate the cost advantage of TPUs." But Nvidia's stock tells a more anxious story: up only 11% this year against an 88% gain for the broader semiconductor index, as investors bet the spending pie is being sliced among more players.

## The diaspora is on every side of this fight

Here is what makes the chip war unusually personal for Indian Americans: they are building all of it.

Indian-origin engineers staff the silicon teams at Google, Amazon, and Nvidia alike. Sanjay Mehrotra runs Micron, which makes the high-bandwidth memory stacked on top of nearly every AI accelerator — and which is sold out of HBM through all of 2026. Jayshree Ullal's Arista Networks builds the high-speed plumbing that lets hundreds of thousands of these chips talk to each other. Nikesh Arora's Palo Alto Networks secures the data centers they sit in. Whichever chip wins, the diaspora's fingerprints are on the hardware.

For NRI investors, the calculus is trickier. A world where Nvidia's monopoly erodes is not necessarily bad — it could be a windfall for Micron, Arista, Broadcom, and the custom-chip designers. But it raises the risk that the AI infrastructure trade, which has minted enormous paper wealth, is entering a more crowded and lower-margin phase. J.P. Morgan now projects $5.5 trillion in AI-related capex through 2030, yet warns that the more these giants spend, the more they must earn back to justify it.

## What to watch

The near-term signal is adoption. Amazon's chip ambitions hinge on whether outside customers actually buy Trainium racks rather than defaulting to Nvidia. Google's depends on whether its Blackstone-backed cloud venture wins business from CoreWeave and Nebius. If either gains traction, the AI hardware market stops being a one-horse race — and the engineers, many of them Indian, who can move fluently between CUDA, TPUs, and Trainium become the most valuable people in the building.

For a community whose professional fortunes are tied to American technology more tightly than almost any other, the breakup of Nvidia's monopoly is not a spectator sport. It is a referendum on where the next decade of jobs and returns will come from."""

article3_body = """Satya Nadella has spent the past three years turning Microsoft into the most aggressive AI company on earth. This month he issued a warning about exactly that kind of company — and then shipped a product that deepens his own grip on the market.

The contradiction is instructive, and for the Indian professionals who make up a large share of Microsoft's workforce, it is also a roadmap for where the most valuable jobs are heading.

## The warning and the product

In a widely circulated essay, Nadella cautioned against AI power concentrating in the hands of a few giants, framing the central question of the era as "who gets to keep the value" that AI creates. He published it, awkwardly, the same week Reuters reported a proposed shareholder class-action accusing Microsoft of hiding slowing Azure growth and ballooning AI costs. The company spent $37.5 billion on capital expenditure last quarter alone — up nearly 66% year over year.

Days later, Microsoft made Copilot Cowork generally available with a new usage-based pricing model. Cowork is an AI agent designed to run long, multi-step tasks on its own — even when a user's computer is switched off — acting on documents inside a customer's Microsoft 365 tenant. It is billed on top of the existing Copilot license ($30 per user per month for large enterprises) through "Copilot Credits," metered across model use, context retrieval, tool calls, and runtime.

In plain terms: Microsoft is no longer selling software that helps you work faster. It is selling autonomous workers, priced by how hard they think.

## Why this lands hard on the diaspora

Indian engineers, consultants, and IT-services firms have built much of their economic model on doing exactly the kind of structured, multi-step knowledge work Cowork is designed to automate — code migrations, document processing, ticket resolution, back-office orchestration. The Indian IT giants felt it first: Wipro built an entire center in Bengaluru to run Anthropic's Claude, Cognizant wired ServiceNow's AI agents into its own, and HCLTech took a stake in the Indian AI startup Sarvam. The companies that sold cheap human labor are scrambling to sell orchestration instead.

For an Indian professional inside Microsoft, the message is sharper still. Nadella has restructured the Copilot organization into a single unified effort spanning experience, platform, Microsoft 365 apps, and AI models. He has hedged the company's bets beyond OpenAI, routing workloads through Anthropic and xAI, and is building in-house models — Project Polaris for GitHub Copilot, the Maia accelerators that run them — to reduce dependence on any one lab. Each of those moves reshuffles teams, and Indian engineers are heavily represented in the units being merged and re-pointed.

## The pricing tells the real story

The shift to usage-based billing is the part worth dwelling on. When software was sold per seat, a developer's job was to use the tool. When it is sold per task completed, the tool starts doing the job. Microsoft has only 15 million paid Microsoft 365 Copilot seats against 450 million subscribers — a gap that explains why Nadella is so eager to prove agents can justify their cost. Usage-based pricing is how he plans to monetize work itself, not access to a feature.

For NRIs tracking this as investors, the tension Nadella embodies is the whole thesis. Microsoft is warning about AI concentration while racing to dominate it; its AI business has crossed a $37 billion annual run rate, up 123% year over year, even as shareholders sue over the cost of getting there. That is either the safest bet in technology or the most expensive, depending on whether agents like Cowork actually deliver.

## The takeaway

The instinct, watching a man warn against the thing he is building, is to call it hypocrisy. It is closer to a survival strategy. Nadella is telling the market what the risks are precisely because he intends to be the one who manages them.

For the diaspora that powers so much of his company, the lesson is colder and more useful: the work that can be described as a series of steps is the work being automated first. The careers that survive will belong to the people who design the agents, price them, and decide what value they are allowed to keep — which is, not coincidentally, exactly the job Satya Nadella has given himself."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Google Put Gemini in a $99 Speaker. The Real Target Is the Phone in Every Indian Pocket.",
        "subheadline": "Sundar Pichai is smuggling his AI into the devices people already own — and India is the test bed, not the afterthought.",
        "slug": make_slug("google-gemini-home-speaker-android-17-sundar-pichai-india-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian Americans sit on both sides of this launch — as the engineers inside Alphabet whose teams live or die by Gemini, and as NRIs whose families in India are Google's first test market for its AI-everywhere strategy.",
        "tags": ["sundar-pichai", "google", "gemini", "ai", "android", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Seeking Alpha — Gemini-powered speaker on sale June 25", "url": "https://seekingalpha.com/news/hey-google-when-does-the-new-gemini-powered-ai-speaker-go-on-sale"},
            {"name": "The Bridge Chronicle — Android 17 for Pixel: Gemini AI features", "url": "https://www.thebridgechronicle.com/tech/google-rolls-out-android-17-pixel-gemini-ai"},
            {"name": "Reuters — Google's Gemini co-lead Noam Shazeer to join OpenAI", "url": "https://www.reuters.com/technology/googles-gemini-co-lead-noam-shazeer-join-openai"},
            {"name": "Livemint — Google brings Gemini app to Mac, built by AI", "url": "https://www.livemint.com/technology/google-gemini-app-mac-sundar-pichai-antigravity"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Alphabet and Google CEO Sundar Pichai, who is steering the company's Gemini-everywhere strategy.",
        "image_attribution": "Wikimedia Commons",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nvidia's Biggest Threat Isn't a Rival. It's the Customers Now Selling Their Own Chips.",
        "subheadline": "Amazon and Google are pushing custom AI silicon into the open market — and Indian engineers are building hardware on every side of the fight.",
        "slug": make_slug("amazon-trainium-google-tpu-nvidia-ai-chip-war-indian-engineers-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin engineers staff the silicon, memory, networking, and security layers of the AI stack at once, so the breakup of Nvidia's monopoly directly shapes diaspora careers and NRI investment portfolios.",
        "tags": ["nvidia", "amazon", "google", "ai-chips", "semiconductors", "indian-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Barron's — Amazon's New Weapon: Selling Custom AI Chips", "url": "https://www.barrons.com/articles/amazon-trainium-ai-chips-nvidia"},
            {"name": "WSJ — Google Is Using Nvidia's Playbook to Build a Rival AI Chip Business", "url": "https://www.wsj.com/tech/google-tpu-nvidia-ai-chip-business"},
            {"name": "Barron's — Nvidia's Biggest Threat Isn't AMD, It's Its Own Best Customers", "url": "https://www.barrons.com/articles/nvidia-stock-ai-chips-hyperscalers-threat"},
            {"name": "Investor's Business Daily — Hyperscaler AI capex and debt", "url": "https://www.investors.com/news/technology/nvidia-stock-ai-data-centers-debt"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Close-up of microchips on a circuit board, the contested hardware at the center of the AI chip war.",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Satya Nadella Warned Against AI Monopolies. Days Later He Started Charging by the Task.",
        "subheadline": "Microsoft's new usage-based Copilot agents reveal where the most valuable work is heading — and what it means for the Indians who do so much of it.",
        "slug": make_slug("satya-nadella-microsoft-copilot-cowork-usage-pricing-ai-agents-diaspora"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Microsoft's pivot to billing for autonomous AI work hits the structured, multi-step knowledge tasks that Indian engineers and IT-services firms built their economic model on, redrawing which careers survive.",
        "tags": ["satya-nadella", "microsoft", "copilot", "ai-agents", "it-jobs", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Computerworld — Microsoft launches Copilot Cowork with usage-based pricing", "url": "https://www.computerworld.com/article/microsoft-copilot-cowork-usage-based-pricing"},
            {"name": "Memeburn — Nadella warns against AI monopoly from AI giants", "url": "https://memeburn.com/2026/06/microsoft-satya-nadella-ai-monopoly-warning"},
            {"name": "eWeek — Nadella says Microsoft will exploit its new OpenAI deal", "url": "https://www.eweek.com/news/microsoft-openai-deal-nadella"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Microsoft CEO Satya Nadella, who is reshaping Copilot around autonomous, usage-billed AI agents.",
        "image_attribution": "Wikimedia Commons",
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  [{wc} words] {art['headline'][:60]}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
