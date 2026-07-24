#!/usr/bin/env python3
"""Technology writer — 2026-07-12 20:00 PT run. 3 articles."""

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
    # ---------------------------------------------------------------
    # ARTICLE 1: OpenAI Codex Micro hardware launch July 15
    # ---------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "OpenAI Is Launching Its First Hardware Product on Tuesday. It Is a Keyboard for Coders.",
        "subheadline": "The Codex Micro, a programmable macro pad built with accessory maker Work Louder, signals that the AI race is now spilling from the cloud onto your desk — and Indian developers are its biggest audience.",
        "slug": make_slug("openai-codex-micro-hardware-keyboard-developers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian developers are the single largest demographic using AI coding tools like GitHub Copilot and OpenAI Codex. A dedicated hardware accessory targeting developer workflows directly impacts the millions of Indian engineers in Silicon Valley and at IT firms globally.",
        "tags": ["openai", "codex", "hardware", "developer-tools", "ai-coding", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TechJuice", "url": "https://www.techjuice.pk/openai-codex-micro-programmable-keypad-developers/"},
            {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/30/openai-codex-hardware-teaser/"},
            {"name": "TechLusive", "url": "https://www.techlusive.in/news/openais-first-hardware-device-is-coming-on-july-15-heres-what-it-is"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33349204/pexels-photo-33349204.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A developer's workspace with illuminated keyboards and multiple screens displaying code",
        "image_attribution": "Pexels",
        "body": """Sam Altman's company has spent two years talking about AI devices that will replace the smartphone. On Tuesday, it will ship something far less glamorous — and far more telling about where the AI industry actually is.

The Codex Micro, launching on July 15 in partnership with boutique keyboard maker Work Louder, is a compact macro pad with 13 mechanical switches, a joystick and a touch sensor. It is designed to give software engineers dedicated physical controls for OpenAI's Codex coding assistant — a one-touch way to accept AI-generated code, trigger rewrites, run tests and navigate between suggestions without leaving the editor.

## Not the Jony Ive gadget

To be clear, this is not the AI consumer device that former Apple design chief Jony Ive is building with OpenAI, a pocket-sized, screenless object that reportedly gathers information through cameras and microphones. That project, born from OpenAI's $6.4 billion acquisition of Ive's studio io last year, remains scheduled for the second half of 2026 at the earliest.

The Codex Micro is far more modest. It is an accessory, not a standalone device — closer to a Stream Deck for AI developers than an iPhone killer. Work Louder's existing Creator Micro 2 retails for about $199, and pricing for the OpenAI variant is expected to land in the same neighbourhood.

But modesty should not be mistaken for insignificance. OpenAI slapping its brand on a physical product, even a peripheral, marks a strategic turn. It signals that the company's battlefield has shifted from model benchmarks to developer workflows — from who has the best model to who has the stickiest daily tools.

## Why Indian engineers should pay attention

India is the world's largest exporter of software talent, and Indians account for the majority of H-1B visa holders in American tech companies. That workforce has become the most avid user base for AI coding assistants. GitHub's own data shows developers using Copilot complete tasks up to 55 per cent faster, and adoption rates in Indian IT services firms — TCS, Infosys, Wipro, HCL Tech — have been climbing steeply since 2025.

A dedicated hardware layer on top of Codex matters because it lowers the friction of adoption further. For an Indian engineer at a Bay Area startup or an IT services professional on a client site in New Jersey, the calculation is practical: anything that shaves seconds off repetitive AI interactions compounds over an eight-hour coding day.

The bigger question is what comes next. If the Codex Micro sells well, it validates a model where AI companies own not just the intelligence but the physical interface around it — the same vertical integration playbook that made Apple's hardware-software lock-in so formidable. OpenAI's ambitions clearly extend further. But Tuesday's launch will test whether developers want AI tools integrated into their hands, not just their screens.

## The competitive context

OpenAI is not alone in this push. Anthropic's Claude Code, Google's Gemini Code Assist and Amazon's CodeWhisperer are all vying for the same developer attention. None of them, however, has attempted hardware. That makes the Codex Micro both a first-mover advantage and a high-wire act: if developers shrug, it reinforces the view that AI tools belong purely in software. If they buy it, OpenAI builds a physical moat at a time when its software edges — model quality, speed, price — are narrowing by the quarter.

For the Indian developer community, the subtext is worth reading carefully. The tools they use shape the platforms they build on, and the platforms they build on shape their career trajectories. When OpenAI starts selling hardware to coders, it is making a bet on permanence. Indian engineers, who have navigated more platform shifts than most, will recognise the stakes."""
    },

    # ---------------------------------------------------------------
    # ARTICLE 2: Jensen Huang on AI agents vs coding
    # ---------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "Jensen Huang Says His Engineers Prefer Building AI Agents to Writing Code. The Implications for Indian Tech Workers Are Enormous.",
        "subheadline": "The NVIDIA CEO's remarks redefine what it means to be a software engineer — and challenge the skill sets that millions of Indian H-1B workers were hired for.",
        "slug": make_slug("jensen-huang-nvidia-ai-agents-engineers-coding"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NVIDIA employs thousands of Indian-origin engineers. Huang's vision of software work shifting from code-writing to agent-building has direct implications for the skill sets that Indian H-1B workers bring to Silicon Valley and the career paths available to them.",
        "tags": ["nvidia", "jensen-huang", "ai-agents", "agentic-ai", "software-engineering", "h-1b", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/my-engineers-prefer-building-ai-agents-than-writing-code-nvidia-ceo-jensen-huang"},
            {"name": "CMSWire", "url": "https://www.cmswire.com/digital-experience/nvidia-ceo-jensen-huang-at-adobe-summit-agentic-is-here/"},
            {"name": "Fast Company", "url": "https://www.fastcompany.com/91350000/nvidia-ceo-jensen-huang-jobs-ai"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "NVIDIA CEO Jensen Huang speaking about the future of AI and software engineering",
        "image_attribution": "Wikimedia Commons",
        "body": """Jensen Huang has never been one for diplomatic understatement. On Friday, the NVIDIA CEO offered his bluntest take yet on the future of software engineering: his own engineers, the people building chips that power the global AI boom, now prefer constructing AI agents to writing Python.

"Coding is like typing, and so they're gonna do less typing," Huang said, according to a report by Inshorts. He added that agentic AI is not eliminating engineering jobs but creating new ones — with engineers now focused on building agents, designing benchmarks and establishing guardrails rather than grinding through lines of code.

## From code to orchestration

The shift Huang describes is not hypothetical. At NVIDIA — now the world's most valuable company by market capitalisation — 100 per cent of software engineers are supported by AI agents. The engineers are not idle; they are busier than ever. But the nature of their work has changed. They spend less time writing boilerplate and more time orchestrating systems of agents that do the writing for them.

Huang has drawn this analogy repeatedly in recent months. At Adobe Summit, he compared it to radiology: when AI made scan analysis superhuman, demand for radiologists went up, not down, because faster analysis meant more patients and more complexity requiring human judgment. The same dynamic, he argues, is playing out in software.

At a Stanford event, he was even more direct: "Most people will lose their job to somebody who uses AI — not to AI itself." And at GTC 2026, he proposed a new productivity metric for engineers: token consumption. "That $500,000 engineer at the end of the year, I'm going to ask him, how much did you spend in tokens?" Huang said. "If that $500,000 engineer did not consume at least $250,000 worth of tokens, I am going to be deeply alarmed."

## What this means for Indian engineers

This is not an abstract philosophical debate for the Indian diaspora. Indians represent the largest group of H-1B visa holders in the United States, and the overwhelming majority work in technology. The traditional value proposition of the Indian software engineer — deep technical expertise in writing, debugging and maintaining code — is the exact capability that Huang says is being automated.

That does not mean Indian engineers are obsolete. Quite the opposite, if Huang's thesis is correct. The shift from code-writing to agent-building demands a different set of skills: systems thinking, prompt engineering, evaluation design, safety architecture. Indian engineers who make that pivot fast will be more valuable than ever. Those who do not risk being priced out by the very agents they were hired to build before.

The Indian IT services sector faces an even sharper reckoning. Companies like TCS, Infosys and Wipro built empires on the ability to deploy large teams of engineers to write and maintain software for Western enterprises. If the unit of value shifts from lines of code to agent orchestration, the body-shop model faces a structural challenge. The services giants know this — TCS recently announced plans to recruit up to 8,900 forward-deployed engineers, and Infosys is embedding AI agents inside American hospitals — but the transition is far from complete.

## The NVIDIA economy and India's role

India plays a quietly enormous role in NVIDIA's own supply chain. The company has major engineering operations in Bengaluru and Hyderabad, where Indian engineers work on chip design, driver software and AI framework development. Huang's vision of agent-first engineering will reshape these teams as much as any in Santa Clara.

For Indian-origin professionals across Silicon Valley, the message from the CEO of the most important company in AI is unambiguous: the engineers who thrive will be the ones who learn to direct intelligence, not just write it. Coding is becoming typing. The question is what comes after the keyboard."""
    },

    # ---------------------------------------------------------------
    # ARTICLE 3: Zetwerk IPO SEBI approval
    # ---------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "Zetwerk Just Got SEBI's Green Light for a $450 Million IPO. The Manufacturing Unicorn Is Riding the AI Data Centre Boom.",
        "subheadline": "Backed by Khosla Ventures and Lightspeed, the B2B platform that connects factories across India, the US and Mexico is betting that the AI infrastructure buildout will carry it to public markets.",
        "slug": make_slug("zetwerk-sebi-ipo-approval-manufacturing-ai-data-centre"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Zetwerk's IPO, backed by Indian-American VC Vinod Khosla's firm and managing factories in the US and Mexico, offers NRI investors exposure to India's manufacturing boom — and to the global AI data centre construction wave that is driving its revenue growth.",
        "tags": ["zetwerk", "ipo", "sebi", "manufacturing", "ai-data-centres", "khosla-ventures", "indian-startup"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/zetwerk-gets-sebi-approval-for-ipo-issue-likely-to-include-fresh-shares-and-ofs"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/zetwerk-receives-sebi-nod-for-ipo/"},
            {"name": "Inc42", "url": "https://inc42.com/features/indian-startup-ipo-tracker-2026/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/34718922/pexels-photo-34718922.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A vast industrial factory floor with machinery and structured workstations",
        "image_attribution": "Pexels",
        "body": """India's markets regulator has cleared Zetwerk Manufacturing Businesses for an initial public offering that could raise up to ₹4,200 crore — roughly $450 million — in what would be one of 2026's most watched listings by Indian-American investors.

The Securities and Exchange Board of India (SEBI) approved the IPO on Friday, according to Outlook Business and The Hindu BusinessLine. The offering will comprise a fresh issue of equity shares and an offer for sale by existing shareholders. The final valuation, expected to be in the range of $3.5 billion to $4 billion, will be determined through the book-building process.

## From startup to manufacturing platform

Founded in 2018 by Amrit Acharya, Srinath Ramakkrushnan, Vishal Chaudhary and Rahul Sharma, Zetwerk operates a technology-enabled manufacturing platform that connects industrial demand with a distributed network of suppliers and factory floors. It started by coordinating the production of industrial machine components — the decidedly unglamorous pipes, castings and metal parts that keep factories running — and has since expanded into electronics, defence hardware, aerospace components and consumer products including laptops and wearables.

The company has raised over $793 million to date from investors including Vinod Khosla's Khosla Ventures, Lightspeed Venture Partners, Greenoaks Capital, Peak XV Partners, Accel and Baillie Gifford. The involvement of Khosla Ventures, one of the most prominent Indian-American-led venture firms in Silicon Valley, gives Zetwerk an automatic audience among NRI investors tracking the India growth story.

## The AI data centre connection

What makes Zetwerk's IPO timing particularly interesting is its exposure to the global AI infrastructure buildout. CEO Amrit Acharya has said the company expects to cross $2 billion in revenue in FY26, driven in part by manufacturing contracts linked to AI data centres. As hyperscalers — Google, Microsoft, Amazon, Meta — pour hundreds of billions into AI compute capacity, the demand for the physical infrastructure that houses those chips is exploding.

Data centres need server racks, cooling systems, power distribution units, cable assemblies and custom metal enclosures — precisely the kind of contract manufacturing that Zetwerk orchestrates. The company's platform, powered by its proprietary Zetwerk OS software, manages sourcing, production planning, supplier coordination and quality control across its factory network. It is not the kind of AI story that makes venture capitalists' eyes light up at demo day. But it is the kind that produces revenue.

## The financial picture

Zetwerk's financials tell a more complicated story than the AI-tailwind narrative suggests. Gross merchandise value dipped 11 per cent in FY25 to ₹12,798 crore from ₹14,443 crore the year before. But the company slashed its net loss by 60 per cent to ₹371 crore, down from ₹918 crore in FY24, signalling improving unit economics even as the top line compressed.

The IPO will be managed by Kotak Mahindra Capital, JM Financial, Avendus Capital, Pantomath Capital and the Indian arms of HSBC, Morgan Stanley and Goldman Sachs — a seven-bank syndicate that reflects both the deal's size and the competitive pressure among bankers to win Indian tech mandates.

## Why NRI investors should care

Zetwerk's listing will test a question that Indian public markets have been circling for two years: is there an appetite for manufacturing-as-a-platform stories, or does "Indian tech IPO" still mean software and services? If Zetwerk can convince the market that it is a technology company that happens to make physical things — rather than a factory that happens to use software — it could open the door for a category of listings that India's capital markets have historically undervalued.

For NRI investors, the thesis is straightforward. India's manufacturing sector is growing on the back of three tailwinds: the China-plus-one supply chain diversification, the government's production-linked incentive schemes and, now, the global AI infrastructure buildout. Zetwerk sits at the intersection of all three. The IPO will reveal whether the public markets agree that that intersection is worth $4 billion.

The company also operates manufacturing facilities in the United States, Mexico and Europe — a geographic spread that gives it exposure to the nearshoring trend and makes it more than just an India play. For an NRI portfolio looking for India-linked exposure with global optionality, that combination is hard to find on the stock exchange today."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
