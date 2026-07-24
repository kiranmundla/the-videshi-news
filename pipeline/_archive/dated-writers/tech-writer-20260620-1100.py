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

PICHAI_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg/330px-Sundar_Pichai_-_2023_%28cropped%29.jpg"
KRISHNA_IMG = "https://upload.wikimedia.org/wikipedia/commons/3/30/Arvind_Krishna_in_2025_%28cropped%29.jpg"
MODI_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg/330px-The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg"

body1 = """Sundar Pichai has spent two years convincing the world that Google caught up in artificial intelligence. The harder question now is whether he can keep the people who got him there.

Within 48 hours this week, Google lost two of the most decorated minds in its AI ranks. Noam Shazeer, a vice president of engineering and co-lead of the Gemini models, announced on Wednesday that he is leaving for OpenAI — less than two years after Google reportedly paid about $2.7 billion in a licensing deal with his startup Character.AI that brought him back. Two days later, John Jumper, the Nobel laureate behind DeepMind's protein-folding breakthrough, said he was leaving for Anthropic.

Shazeer is not a replaceable hire. He co-authored the 2017 "Attention Is All You Need" paper that introduced the Transformer — the architecture underneath virtually every large language model in use today, Gemini and ChatGPT included. Sam Altman, who has chased him for the better part of a decade, called him "one of the people I have most wanted to work with since the very beginning" of OpenAI. "Only took 10 years," Altman wrote. "I think it will be worth the wait."

### The scarcest resource isn't silicon

Most coverage of the AI race fixates on bottlenecks investors can model: chip supply, data-center power, high-bandwidth memory. The Shazeer and Jumper exits are a reminder that the scarcest input is a few hundred human brains. There is a thin layer of researchers with the experience to define where frontier models go next, and they are being bid for like free agents.

That bidding war has a distinct Indian accent. Pichai, a Chennai-born IIT Kharagpur graduate, runs the company doing the bidding. Many of the engineers fielding counter-offers — and writing the counter-offers — are Indian or Indian-American, clustered in exactly the Mountain View and Sunnyvale teams now being raided. When a Shazeer-tier name walks, the reshuffle ripples down through the org charts where diaspora engineers actually sit.

### Why this lands close to home

For an Indian engineer on an H-1B at Google, a star departure is not gossip. It is a signal about where stability and equity upside are migrating. The instinct in a layoff-heavy year — tech has shed more than 180,000 jobs in 2026 — is to cling to a big, safe employer. But the people with the most leverage are doing the opposite: moving toward smaller, faster labs where the work and the payout concentrate. The visa math complicates that calculus. A salaried researcher at Google has a sponsored, transferable status; jumping to a younger lab can mean re-filing petitions and resetting green-card priority dates that, for Indian nationals, already stretch out over a punishing wait.

There is also a quieter opportunity. Every senior exit opens a senior seat. Google has historically backfilled top AI roles from within, and the bench it promotes from is heavily diaspora. The same churn that looks like instability from one angle is a promotion ladder from another.

### Pichai's containment problem

Google's official line was gracious — "we are grateful for Noam's meaningful contributions" — but the loss is real, and analysts said so plainly. D.A. Davidson's Gil Luria called Shazeer's departure "a significant loss" for Google's AI efforts. The deeper worry for Pichai is that a $2.7 billion acqui-hire did not buy loyalty; it bought roughly 20 months. If money cannot anchor the very top of the talent stack, retention becomes a problem no balance sheet solves.

Pichai's counter-argument is that Gemini's momentum no longer depends on any single researcher. The Gemini 3.5 family shipped at I/O in May, the model is now the default across Search, and Alphabet's stock has tripled the S&P 500's return since ChatGPT's debut. Institutions, the bet goes, now beat individuals.

That is the theory every incumbent tells itself right before a rival proves otherwise. For the diaspora professionals who make up so much of Google's AI workforce, the next few quarters will reveal which is true — and whether the smart move is to stay inside the machine Pichai built, or follow the people walking out of it."""

body2 = """While Silicon Valley pours hundreds of billions into AI chips, Arvind Krishna is betting that the next computing arms race will be won somewhere else entirely. IBM has committed more than $10 billion over the next five years to quantum computing — and its Indian-American chief executive is staking the 115-year-old company's relevance on getting there first.

The pledge, announced earlier this month, spans research, manufacturing, acquisitions and a proposed $1 billion CHIPS Act award to build Anderon, what IBM calls America's first dedicated quantum chip foundry. Krishna's claim is unusually specific for a field long mocked as perpetually "ten years away": IBM, he insists, will deliver the world's first large-scale, fault-tolerant quantum computer by 2029, with practical "quantum advantage" arriving as soon as this year.

### What quantum actually buys

Classical computers process bits as ones and zeros. Quantum machines use qubits, which can hold both states at once, letting them attack problems that would take today's best supercomputers millions of years. Krishna frames it as a complement to AI rather than a competitor. "AI is great at predicting a bit of the future," he has said. "Quantum computes the future." At IBM's Think conference, his team — working with the Cleveland Clinic and Japan's RIKEN — simulated protein complexes of more than 12,000 atoms by stitching quantum hardware to classical supercomputers, a step toward real drug discovery.

The skepticism is warranted. Even Pichai has said useful quantum machines are five to ten years out, and error rates remain stubbornly high. IBM's stock is down sharply this year, and quantum is being asked to carry a growth story that hybrid cloud and consulting no longer fully deliver.

### The diaspora's stake in a quantum bet

For Indian Americans, this is more than another big-tech roadmap. Krishna — a Dhakuria-born IIT Kanpur graduate who took over IBM in 2020 — is now one of the most visible diaspora executives steering a piece of U.S. national technology strategy, sitting alongside the CHIPS Act and Commerce Department in a way few foreign-born CEOs do.

It also reshapes a career map. India's IT economy was built on a cheap-labor model that AI is now hollowing out; quantum is one of the few frontiers where the talent pool is still being formed rather than automated. IBM has been seeding it deliberately — quantum and AI hubs in Illinois and a new MIT-IBM research lab in Cambridge — and its India research arm has long been a pipeline for exactly this kind of deep-physics work. For a diaspora engineer weighing where to specialize, "quantum-classical" expertise is a bet on scarcity rather than commoditization.

### Why the timing is pointed

Krishna's announcement also reads as a strategic hedge. IBM spent the spring tying itself to the AI boom from the application layer — a Google Cloud practice launched on June 4, industry-specific agents for Gemini Enterprise, the $5 billion Project Lightwell with Red Hat to secure the open-source software supply chain. But selling AI services puts IBM in a crowded field against Accenture, TCS and the hyperscalers, all of them squeezing the same enterprise budgets. Quantum is a field IBM has led for years and where few rivals can match its hardware. Owning the frontier, rather than renting someone else's, is the move of a company that watched the cloud era reward the platform owners and intends not to repeat the mistake.

The risk is obvious: if 2029 slips, a $10 billion bet on a technology most customers cannot yet use will look like vanity. Krishna is pushing back on both the "quantum is sci-fi" crowd and the "quantum is oversold" crowd, arguing the field has moved "from science to engineering."

For NRIs tracking IBM as an employer, an investment, or a barometer of where the diaspora's technical edge is heading, the message is the same one Krishna keeps repeating: the gap is closing faster than most people appreciate. Whether he is right will define both his legacy and the next chapter of American computing — engineered, in no small part, by Indian hands."""

body3 = """When the United States restricted exports of its most advanced AI models this spring, it handed India a problem and a prod. The problem: the country's booming AI ambitions suddenly depend on technology a foreign government can switch off. The prod: build your own, faster.

That tension was on open display at the G7 summit in France this week, where Prime Minister Narendra Modi — seated near President Donald Trump — argued that frontier AI should be a "global public good." Washington had unilaterally curbed access to Anthropic's top-tier Mythos and Fable models for non-American users. "Access to these critical AI technologies must also be widespread and inclusive," Modi said. "All democratic nations should have access to such AI models so that they can protect their critical information infrastructure and counter growing cyber threats."

The diplomatic language masked a hard lesson India is now internalizing: technological dependence is strategic vulnerability, however friendly the supplier looks on the surface.

### The money is moving toward sovereignty

The clearest evidence is where capital is flowing. This week Bengaluru's Sarvam AI became India's newest AI unicorn, raising $234 million at a $1.5 billion valuation in a round led by HCLTech — the IT giant putting in $150 million as a strategic investor, with Bessemer, Khosla Ventures and Peak XV alongside. Sarvam is building a full-stack "sovereign AI" business: models tuned for Indian languages, its own inference infrastructure, and applications for banking, government and defense.

It is not alone. Wipro just opened a Bengaluru center of excellence for Anthropic's Claude and pledged to train 10,000 employees on it; TCS announced an Anthropic alliance on June 11. The IndiaAI Mission, the country's national compute-and-models push, has become the organizing framework for a five-layer stack — semiconductors, data centers, energy, applications and language models — that India now wants to control end to end.

### Why NRIs should read the fine print

For the diaspora, this is one of the more consequential shifts in years, and it cuts two ways.

For investors, a sovereign-AI build-out is an emerging asset class with a domestic tailwind: government procurement mandates, tax incentives and a captive market of 1.4 billion people. Sarvam, the data-center partnerships like Jabil-Adani's $50 billion infrastructure plan, and the IT majors repositioning around AI are all ways to buy into it. But the same week's caution flag matters too — Indian venture funding has been thin and choppy in 2026, and "sovereign" narratives can outrun revenue.

For engineers, the calculus on returning to India is genuinely changing. The old pitch was lifestyle and proximity to family at the cost of frontier work. Sovereign AI inverts part of that: the most interesting model-building in the country is no longer a backwater, and HCLTech-scale money is now chasing it. A diaspora researcher who once had to be in California to work on foundation models can increasingly do it in Bengaluru.

### The weak link India keeps naming

The honest counterpoint comes from India's own commentators, who note that the private sector's historically thin R&D culture is the missing piece. Government demand can prime the pump, but durable AI capability requires Indian corporations to treat research as a competitive necessity, not an optional cost. The five layers — chips, data centers, energy, apps, models — need parallel progress, and India is still far behind on the first.

That is the real test for NRIs to watch over the next year. The export curbs gave India both the motive and the political cover to go it alone, and the money has started to follow. Whether it produces a genuine homegrown stack — or a well-funded dependency wearing a sovereign label — will shape where the diaspora's next generation builds, invests and, increasingly, returns to work."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Google Just Lost Two of Its AI Crown Jewels in 48 Hours. Sundar Pichai's Real Problem Is Retention.",
        "subheadline": "Gemini co-lead Noam Shazeer left for OpenAI and a Nobel laureate decamped to Anthropic — a brain drain that runs straight through the diaspora-heavy teams Pichai built.",
        "slug": make_slug("google-ai-talent-drain-shazeer-openai-pichai-gemini-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian engineers make up much of Google's AI workforce, and a star exodus reshapes where stability, equity upside and promotion ladders sit for diaspora professionals on H-1B status.",
        "tags": ["ai", "google", "sundar-pichai", "openai", "silicon-valley", "indian-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/google-shake-up-highlights-how-human-brains-may-be-the-scarcest-ai-resource-of-all"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/googles-gemini-co-lead-noam-shazeer-join-openai-2026-06-18/"},
            {"name": "LiveMint", "url": "https://www.livemint.com/companies/news/google-paid-2-7-billion-to-rehire-ai-legend-noam-shazeer-quits-openai"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": PICHAI_IMG,
        "image_caption": "Alphabet and Google CEO Sundar Pichai, photographed in 2023",
        "image_attribution": "Wikimedia Commons",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Everyone Is Betting on AI Chips. Arvind Krishna Just Bet $10 Billion That IBM Wins With Quantum.",
        "subheadline": "IBM's Indian-American CEO says fault-tolerant quantum computing arrives by 2029 — and is staking the company's relevance, and a slice of U.S. tech strategy, on getting there first.",
        "slug": make_slug("ibm-arvind-krishna-quantum-10-billion-bet-2029-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Arvind Krishna is steering a piece of U.S. national tech strategy, and quantum is one of the few frontiers where the talent pool is still forming rather than being automated — a scarcity bet for diaspora engineers.",
        "tags": ["quantum-computing", "ibm", "arvind-krishna", "ai", "indian-tech", "chips-act"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TheStreet", "url": "https://www.thestreet.com/technology/ibm-ceo-sends-strong-message-on-quantum-computing"},
            {"name": "IBM Newsroom", "url": "https://newsroom.ibm.com/announcements"},
            {"name": "Constellation Research", "url": "https://www.constellationr.com/blog-news/ibm-ceo-krishna-touts-quantum-computing-use-cases-quantum-ai-continuum"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": KRISHNA_IMG,
        "image_caption": "IBM Chairman and CEO Arvind Krishna, photographed in 2025",
        "image_attribution": "Wikimedia Commons",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America Restricted Its Best AI Models. India's Answer Is a Scramble to Build Its Own.",
        "subheadline": "At the G7, Modi called frontier AI a 'global public good.' Back home, $234 million flowed into a new sovereign-AI unicorn — a shift NRIs should read closely.",
        "slug": make_slug("india-sovereign-ai-us-export-curbs-modi-g7-sarvam-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Sovereign AI changes the return-to-India calculus for diaspora engineers and opens an emerging investment class for NRIs — but the 'sovereign' label can outrun revenue, so the fine print matters.",
        "tags": ["ai", "india-tech", "sovereign-ai", "sarvam-ai", "indiaai-mission", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Digit", "url": "https://www.digit.in/news/general/india-at-g7-2026-access-to-frontier-ai-models.html"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/16/sarvam-becomes-indias-newest-ai-unicorn-with-234-million-funding-round-led-by-hcltech/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-wipro-opens-ai-center-anthropics-claude-bengaluru-2026-06-16/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": MODI_IMG,
        "image_caption": "Indian Prime Minister Narendra Modi, official portrait",
        "image_attribution": "Wikimedia Commons",
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']} ({wc} words)")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
