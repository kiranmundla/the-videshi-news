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

ALTMAN_IMG = "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg"
INFOSYS_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Aerial_view_of_the_Glass_Pyramid_at_the_Infosys_Campus.jpg/1280px-Aerial_view_of_the_Glass_Pyramid_at_the_Infosys_Campus.jpg"
PHONE_IMG = "https://images.pexels.com/photos/36680543/pexels-photo-36680543.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Washington Just Got First Dibs on OpenAI's Newest Brain. The Indian Engineer Building on It Has to Wait in Line.",
        "subheadline": "OpenAI is releasing GPT-5.6 to a short list of government-approved customers before the public, a precedent that lands hardest on the developers and startups outside the room.",
        "slug": make_slug("openai-gpt-5-6-government-gated-release-altman-developers-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The Indian-American developers, startup founders and cybersecurity engineers who build on top of OpenAI's models now face a future where access to the most powerful AI is rationed by Washington — a structural shift that reshapes who gets to compete.",
        "tags": ["ai", "openai", "regulation", "indian-tech", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/"},
            {"name": "The Information (via TechCrunch)", "url": "https://techcrunch.com/"},
            {"name": "CNN", "url": "https://www.cnn.com/"},
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": ALTMAN_IMG,
        "image_caption": "OpenAI CEO Sam Altman, whose company is staggering the release of GPT-5.6 at the U.S. government's request.",
        "image_attribution": "Wikimedia Commons",
        "body": """When OpenAI ships a new model, the usual ritual is a livestream, a flood of API keys, and a weekend of developers worldwide stress-testing it on everything from legal contracts to Diwali greeting-card generators. GPT-5.6 will not get that launch. On Friday the company confirmed it is staggering the release at the request of the U.S. government, handing the model first to a small group of vetted partners whose names it would not disclose — and whose access, CEO Sam Altman told staff, the government is approving "customer by customer."

The reason is national security. Washington worries that a frontier model capable enough to find novel cyberattacks or assist with weapons design should not go straight into the hands of every developer on Earth. The move follows an export-control order that forced rival Anthropic to pull its most advanced models, which officials judged "on par" with GPT-5.6. Trump signed an executive order this month asking AI labs to submit "covered frontier models" for up to 30 days of government review before release. OpenAI, notably, called this "not our preferred long term model" and warned that such gatekeeping "should not become a permanent standard."

### Why a diaspora newsroom cares about an OpenAI release schedule

Because the people most exposed to this shift are not abstractions. They are the Indian-origin engineers who make up a vast share of the developer base building on these APIs — the founder in Fremont whose two-person startup is a thin wrapper around GPT, the staff engineer at a Bay Area unicorn whose roadmap assumes she can call the newest model the day it ships, the cybersecurity analyst in New Jersey who uses frontier models to red-team his own company's defenses.

For a decade, the implicit deal in Silicon Valley was that compute and capability were available to anyone with a credit card and a clever idea. That is what let a generation of immigrant engineers leapfrog incumbents: you did not need to be Google to build something powerful, you needed an API key. A world where the most capable model is released "customer by customer," with a federal agency deciding who clears the bar, quietly rewrites that deal. The big, well-lawyered incumbents will be in the first cohort. The scrappy outsider — disproportionately the immigrant founder — waits for the "couple of weeks later" general release, if it comes.

### The two-tier future

There is an irony worth naming. The Trump administration originally branded itself as the hands-off, accelerationist alternative to Biden-era AI caution. It is now pressing OpenAI to do voluntarily what critics of heavy regulation always feared: create a tiered system where access to the best tools flows through Washington. OpenAI itself flagged the cost, warning the framework could "restrict access to advanced AI tools for users including developers, businesses, cybersecurity professionals and international partners."

That last phrase — international partners — should prick up ears in the diaspora. India is one of OpenAI's largest user bases by headcount, and Indian startups from Bengaluru to the Bay have built entire companies on timely model access. If frontier releases now route through U.S. security review first, the lag between "available in a Washington-approved pilot" and "available to a developer in Pune" becomes a competitive variable that no amount of engineering talent can close.

### What to watch

Altman's framing was that this is a "short-term step" toward "broader availability in the coming weeks." The tell will be whether the general release actually arrives on that timeline, or whether the preview period quietly becomes the norm. The deeper question is institutional: right now no single agency clearly owns AI regulation. The Anthropic export order came from the Commerce Department; the OpenAI request came from the White House, working through the Office of the National Cyber Director and the Office of Science and Technology Policy. For developers trying to plan a product roadmap, that ambiguity is its own tax.

For the Indian-American engineer who has spent a career betting that the best technology would be available to whoever could use it best, GPT-5.6 is the first model that does not behave that way. It is worth watching not because of what it can do, but because of who decides who gets to find out.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Infosys Says AI Is a $400 Billion Prize, Not a Pink Slip. It's Still Hiring Freshers to Prove It.",
        "subheadline": "While headlines tally six-figure IT job cuts, Salil Parekh is betting the opposite way — keeping campus hiring intact and pitching AI as the industry's largest revenue opening yet.",
        "slug": make_slug("infosys-400-billion-ai-opportunity-fresher-hiring-parekh-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRI families whose children study engineering in India and aim for U.S. tech careers — and for the diaspora professionals invested in Infosys and TCS stock — whether the IT giants keep hiring freshers or quietly stop is the single clearest signal of where the pipeline to Silicon Valley still leads.",
        "tags": ["indian-tech", "infosys", "ai", "it-services", "jobs"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/"},
            {"name": "Xpheno Tech Jobs Outlook (June 2026)", "url": "https://www.xpheno.com/"},
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": INFOSYS_IMG,
        "image_caption": "The glass pyramid at the Infosys campus in Mysuru, the company's flagship training center for new recruits.",
        "image_attribution": "Wikimedia Commons",
        "body": """The story Indian IT has been telling itself for three decades is breaking down, and the numbers are blunt about it. Across the top five services firms, headcount additions fell by 7,389 in FY2026, reversing modest gains the year before. TCS announced plans to cut 12,000 jobs, one of the largest reductions by an Indian corporate employer in memory. Xpheno's June report pegged active tech hiring demand at a 28-month low, with entry-level demand down a brutal 44% year over year.

Into that gloom, Infosys CEO Salil Parekh has placed a contrarian bet. He is calling AI a $400 billion services opportunity — not a force that shrinks the workforce, but the biggest new line of business the industry has seen. And, crucially, he says Infosys will keep hiring freshers, maintaining its campus recruitment into FY27. "We will use AI agents along with humans to focus on different types of work," Parekh said, framing AI as augmentation rather than replacement.

### Why the fresher number is the one to watch

For the diaspora, this is not an abstract HR debate. The campus-hiring pipeline at Infosys, TCS and Wipro is the on-ramp that has fed Indian engineering talent into the global tech economy for a generation. A B.Tech graduate from a tier-two college in Hyderabad gets trained at the Infosys campus in Mysuru — that glass pyramid is its nerve center — billed to a U.S. client, and within a few years many are on an L-1 or H-1B in New Jersey or Texas. When the giants stop hiring freshers, the bottom of that funnel closes first, and the effects ripple to every NRI parent whose kid is in second-year engineering wondering whether the old playbook still works.

That is why Parekh's commitment to keep campus hiring intact matters more than his $400 billion headline. It is a statement that Infosys intends to retrain rather than retrench at the entry level — to take a fresher, teach her to orchestrate AI agents instead of writing boilerplate code, and bill that higher-value work to clients. Whether the math holds is the open question.

### The structural squeeze

Skeptics have a strong case. Generative AI is automating exactly the routine coding, testing and maintenance that entry-level billing was built on. Microsoft and Google now have a meaningful share of their code written by AI, which erodes the outsourced demand that Indian IT lives on. Revenue per employee is rising even as headcount falls — the efficiency dividend is real, but it is being captured by doing the same work with fewer people, not by hiring more of them.

The industry's defenders, including analysts who caution against declaring the IT giants dead, argue the brand is changing rather than collapsing. "The slowdown is not destroying the employer brand of legacy IT companies, but it is changing what those brands stand for," said one. The reputation built on reliability and labor arbitrage is giving way to a harder pitch: that these firms can be the integration layer that gets enterprises from AI hype to working systems.

### What it means for the diaspora investor and the diaspora parent

If you hold Infosys or TCS in your portfolio — and many NRIs do, as a way to keep a stake in the India growth story — Parekh's bet is the thesis to interrogate. A services firm that successfully reprices its workforce around AI and keeps growing revenue per head is a buy. One that is simply shrinking to protect margins while the top line stalls is a value trap dressed as a turnaround.

If you are an NRI parent, the read is more personal. The collapse in entry-level hiring across the sector is real and documented; Infosys keeping its campus intact is the exception, not the rule. The safe assumption for the next cohort is that the path from an Indian engineering degree to a global tech career still exists, but it now demands AI fluency from day one. The companies are betting they can teach it. The students who learn it on their own will not have to wait and see.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An Indian Brand Wants to Sell You a ₹13,000 Phone Built on Its Own Software. The Pitch Is Privacy, Not Specs.",
        "subheadline": "Madhav Sheth's Ai+ has launched the Nova 2 Pro and Neo, the latest push for an indigenous smartphone stack in a market still run by Chinese hardware and Google's Android.",
        "slug": make_slug("ai-plus-nova-2-indian-smartphone-madhav-sheth-indigenous-os-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs who buy unlocked phones on India trips for relatives — and who track the 'Make in India' electronics story as both consumers and investors — an Indian-branded handset on a homegrown software layer is a test of whether the country can move up the value chain from assembly to design.",
        "tags": ["indian-tech", "smartphones", "make-in-india", "consumer-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/"},
            {"name": "DT News", "url": "https://dtnewstv.com/"},
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": PHONE_IMG,
        "image_caption": "Budget smartphones displaying app interfaces; India's sub-₹15,000 segment is the most fiercely contested in the world.",
        "image_attribution": "Pexels",
        "body": """The Indian budget smartphone market does not need another phone. It has Xiaomi, Realme, Vivo, Samsung and a dozen others fighting over every rupee under ₹15,000, with specs that get more generous each quarter. So when Ai+ — the brand from Madhav Sheth, the executive who built Realme's India business before founding NxtQuantum Shift Technologies — launched the Nova 2 Pro and Nova 2 Neo this week, the interesting part was not the hardware. It was the pitch.

The Nova 2 Neo starts at ₹12,999 and the Pro at ₹14,999, both on sale through Flipkart from Friday noon, with MediaTek chips, large displays and the usual battery-and-camera checklist. On a spec sheet, they disappear into the crowd. What Sheth is selling instead is software and sovereignty: handsets built around an India-first stack with privacy as the headline feature, rather than a phone that is simply a vessel for Google's Android and a Chinese contract manufacturer's hardware.

### The made-in-India software question

This is where the diaspora should pay attention, because it is a genuine test of where India sits on the technology value chain. For years "Make in India" in electronics has mostly meant final assembly — screwing together components designed in Shenzhen and Taipei and shipping them with an Indian flag on the box. Real value, and real strategic leverage, lives further up: in chip design, in the operating system, in the software layer that owns the user relationship and the data.

Sheth's bet is that an Indian brand controlling its own software stack — and pitching privacy to a population increasingly wary of where its data goes — can carve out a defensible niche that pure hardware never could. "We have focused on the things that matter most in daily use — performance, battery life, imaging, software quality and privacy," he said, "so that users do not have to compromise based on budget." It is a deliberate framing: not the fastest phone, but the one that does not quietly mine you.

### Why an NRI cares about a ₹13,000 handset

Two reasons, one practical and one strategic. The practical one is familiar to anyone in the diaspora who has been handed a shopping list before a trip home: a phone for a parent, a cousin, a niece starting college. The sub-₹15,000 segment is exactly that gifting sweet spot, and a privacy-forward Indian brand is a different proposition than handing a relative a device whose default apps and data flows are opaque.

The strategic reason is the bigger one. NRI investors and professionals have watched India's digital-infrastructure story — UPI, Aadhaar, ONDC — leapfrog the West on rails the country built itself. The missing piece has always been the device and the OS, the parts still controlled by American and Chinese companies. Every credible attempt at an Indian software stack on Indian-branded hardware is a data point on whether that gap can close. Most will fail; the budget market is a graveyard of ambitious launches. But the direction of travel matters more than any single phone.

### The hard part

Skepticism is warranted. Building a brand against entrenched giants with deep marketing budgets is brutal, and "privacy" is a notoriously hard sell at the bottom of the market, where price wins almost every time. An indigenous software layer also has to clear the chicken-and-egg problem of app support and developer attention that has sunk every non-Android, non-iOS effort before it. Sheth's Realme pedigree buys credibility and supply-chain relationships, but the Nova 2 still has to move volume against rivals offering more raw silicon for the same money.

For now, the Nova 2 is best read not as a product to rush out and buy, but as a signal. If an Indian brand can make privacy and a homegrown stack into selling points rather than footnotes — and survive the budget-segment meat grinder doing it — that is the part of the made-in-India story worth tracking. The phone is cheap. What it is testing is not.
"""
    },
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n{len(inserted)}/{len(articles)} inserted")
for h in inserted:
    print(f"  - {h}")
