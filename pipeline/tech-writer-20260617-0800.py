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

article1_body = """Sundar Pichai does not do victory laps. So when Alphabet's chief executive took to X to announce that the company had booked its first-ever $100 billion quarter, the restraint was the point. "Five years ago, our quarterly revenue was at $50B," he wrote, framing a doubling not as a finish line but as proof that the AI bet is finally paying for itself.

For the tens of thousands of Indian engineers inside Google — from Mountain View to Hyderabad — the number lands differently than it does for Wall Street. It is, in effect, a referendum on whether the company that employs so many of them has navigated the AI transition without becoming roadkill. For two years the open question was whether ChatGPT would hollow out Search the way Google once hollowed out the Yellow Pages. The $100 billion quarter is Pichai's answer: not yet, and maybe not at all.

## The numbers behind the milestone

Growth came from every major segment, Pichai said — double-digit gains across Search, YouTube, and Cloud. The detail that should interest anyone tracking Google's competitive position is Search itself, which Pichai called "an expansionary moment." AI Overviews and the newer AI Mode, he claimed, are not cannibalizing queries but adding them. AI Mode now runs in 40 languages with 75 million daily users, and US queries on the feature doubled in a single quarter.

Cloud is the other engine. New customers rose roughly 34 percent year-on-year, and more than 70 percent of existing customers now use Google's AI products. Thirteen separate Cloud product lines each clear a $1 billion annual run rate — the kind of diversification that makes a business durable rather than a one-trick bet on a single model.

## Why the diaspora should care

There is a sharper, more personal reading of this for Indian professionals. Pichai also confirmed that Gemini 3 will ship later this year, and that more than 13 million developers have already built on Google's generative models. A great many of those developers are in India and the diaspora, and Google's full-stack pitch — custom silicon, frontier models, and the platforms billions already use — is increasingly the toolkit they build careers on.

The flip side is the one nobody at the company says out loud. A $100 billion quarter built on AI efficiency is also a quarter that demonstrates how much output AI now extracts per engineer. The same productivity story that thrills shareholders is the one that has frozen headcount across Big Tech. For an H-1B holder at Google, a blockbuster quarter is reassuring about the company's survival and unnerving about the size of the team it will need to get there.

## The Indian-CEO throughline

Pichai's milestone arrives in a season when Indian-origin leaders are posting results across the industry — Satya Nadella at Microsoft, Arvind Krishna at IBM, Nikesh Arora at Palo Alto Networks. The diaspora has long celebrated the symbolism of these appointments. The more useful question now is operational: these executives are not merely occupying corner offices, they are making the capital-allocation calls that decide where AI infrastructure gets built, which research gets funded, and — quietly — how large the engineering workforce of the future will be.

For an NRI weighing whether to stay at a US tech giant, push for a transfer to an India engineering hub, or jump to a startup, Pichai's quarter is a data point about where the gravity is. Google is spending enormous sums on data centers and silicon, and a meaningful share of that build-out touches India, both as a market — where AI Mode and Gemini are localizing fast — and as an engineering base.

## What's next

The real test is Gemini 3. Pichai has positioned it as the model that closes any remaining gap with OpenAI and Anthropic, and he is shipping it into products that already reach billions. If it lands, the $100 billion quarter will look like a floor rather than a peak. If it stumbles, the same Search "expansion" Pichai is celebrating could reverse quickly.

For the diaspora engineers who have hitched their careers to this company, that is the number worth watching — not the revenue Google booked last quarter, but whether the model shipping next quarter keeps the machine that pays them running."""

article2_body = """The money chasing India's data centers is no longer just American hyperscalers. On Wednesday, Canada Pension Plan Investment Board — one of the largest and most conservative pools of capital on earth — said it would put 70 billion rupees, about $740 million, into CtrlS Datacenters and a related joint venture. When a pension fund that exists to pay Canadian retirees decides Indian server farms are a safe place to park money, it is telling you something about where the AI boom is physically landing.

The structure is worth reading closely. CPP Investments will spend 40 billion rupees to buy an 8.2 percent stake in CtrlS, then commit up to 30 billion rupees more to a joint venture that will build data-center campuses across India. CPP takes 48 percent of that JV; CtrlS keeps 52 percent. This is not a passive bet on a stock — it is patient capital signing up to pour concrete.

## The shovel, not the gold

For NRI investors who have spent two years trying to figure out how to play the AI wave without simply buying Nvidia, the CtrlS deal points at a quieter trade: the infrastructure underneath the models. Every chatbot query, every Gemini video, every enterprise Copilot rollout has to run on a server sitting in a building with power and cooling. India's data-center market is projected to nearly double to $13.11 billion by 2034, according to IMARC Group, driven by digitalization, cloud adoption, and rising AI workloads.

The CtrlS investment also arrives in the same week as a flurry of related signals. Adani recruited an Apple supplier to build AI hardware in India. Yotta Data Services, the country's biggest Nvidia GPU operator, is heading for an IPO. The picture forming is of an entire domestic AI-infrastructure stack — chips, GPUs, and now the buildings to house them — being capitalized at once.

## Why this matters to the diaspora

Two reasons, one financial and one personal. Financially, this is the first time NRI investors have a credible menu of India-based, AI-infrastructure exposure that is not simply a proxy for the Nifty. Yotta's coming IPO will be a listed pure-play; CtrlS, still private, is the kind of name that often precedes a public offering. For diaspora investors who want India growth with an AI tilt, the plumbing layer is suddenly investable.

Personally, the build-out reshapes the return-to-India calculus. For years, the pitch to bring senior infrastructure and cloud talent home was thin — the interesting hyperscale work was in Virginia and Oregon, not Mumbai and Hyderabad. CPP's money, alongside the hyperscalers already building Indian regions, is changing that. The next decade of data-center engineering jobs will not all be in the United States, and a meaningful share of the new ones will sit in India.

## The power problem

There is a catch buried in the optimism, and it is the same one that haunts the global AI build-out: electricity. A data-center campus is, at bottom, a machine for converting power into compute. India's grid is improving but strained, and the surge in hyperscale construction led by Amazon, Microsoft, and Google is competing for the same megawatts that homes and factories need. The smart-money bet embedded in deals like CtrlS is that compute follows cheap, available power — and that India can supply it at scale.

## What's next

Watch whether CPP's entry triggers a wave of similar institutional commitments. Sovereign and pension funds tend to move in herds; the first mover de-risks the trade for everyone behind it. If Singapore's GIC, Abu Dhabi's funds, or the big US endowments follow CPP into Indian data centers, the $13 billion projection for 2034 will start to look conservative.

For the diaspora, the read is simple. The AI story in India has graduated from software demos and startup pitches to hard infrastructure backed by some of the most cautious capital in the world. When the pension funds show up, the speculative phase is ending and the build-out phase has begun."""

article3_body = """India has spent two years insisting it needs its own foundational AI models — sovereign systems, trained on Indian languages and data, not rented from Silicon Valley. This week one of the country's largest IT firms put real money behind the slogan. HCLTech agreed to buy a 10.5 percent stake in Sarvam AI, valuing the Bengaluru startup at $1.5 billion and turning a national-pride talking point into a balance-sheet commitment.

The mechanics: HCLTech will acquire 41,421 equity shares and fund Sarvam's research into next-generation models for agentic AI, coding, and cybersecurity. The investment is part of a round, co-led by Bessemer Venture Partners with Khosla Ventures and Peak XV still participating, that is targeting $300 million. For HCLTech, the logic is to build language models and AI solutions it can sell to its global enterprise clients, and to accelerate sovereign-AI offerings for governments and regulated industries that cannot, for legal reasons, run their workloads on American models.

## The deflation paradox

There is an irony here that anyone working in Indian IT will recognize. The conventional wisdom for two years has been that generative AI is an extinction-level threat to the IT-services model — that if a coding agent can do the work of a junior engineer, the entire pyramid of Indian outsourcing collapses. TCS cut 12,000 middle-management jobs. Analysts downgraded the whole sector.

Yet here is HCLTech doing the opposite of retreating: buying into the technology that is supposed to disrupt it. Wipro opened a Claude lab in Bengaluru. TCS partnered with Anthropic. The Indian IT giants have concluded that the way to survive AI deflation is not to hide from it but to own a piece of the stack — and, increasingly, to back a homegrown alternative to the American labs.

## Why the diaspora should care

For Indian professionals abroad, the Sarvam deal carries two distinct signals. The first is about the kind of work that will exist. Sovereign AI — models trained for governments, banks, and defense, where data cannot leave national borders — is a genuinely new category, and it is being built in India for India. That creates senior research and engineering roles at home that did not exist a year ago, the kind that might actually tempt a diaspora researcher at OpenAI or DeepMind to consider a move.

The second is geopolitical, and it has teeth. The push for sovereign AI accelerated after Washington pressured American labs to restrict foreign-national access — a debate that has Indian engineers inside US AI companies watching their own status nervously. If the political winds in Washington keep tightening around who can touch frontier models, an Indian sovereign-AI ecosystem becomes not just a matter of national pride but a career hedge. A researcher who finds the US increasingly unwelcoming now has somewhere credible to land.

## The HCLTech bet in context

HCLTech is making a calculated wager that its enterprise clients — banks, hospitals, governments — will pay a premium for AI that is auditable, locally hosted, and legally clean. That is a different business from reselling OpenAI's API with a consulting wrapper. It is higher-margin, stickier, and far harder for a US lab to replicate, because it depends on relationships with regulated Indian and global institutions that the services firms already own.

Microsoft partnered with Sarvam back in 2024 for voice-based generative AI, a sign the startup's language work was credible early. HCLTech's stake deepens that validation and gives Sarvam a captive enterprise channel.

## What's next

The number to watch is whether Sarvam closes the full $300 million round and, more importantly, whether the models it ships can compete on quality rather than just sovereignty. A locally hosted model that is meaningfully worse than Gemini or Claude is a compliance product, not a competitive one. If Sarvam can be both sovereign and good, HCLTech's 10.5 percent will look cheap — and India's claim to its own AI stack will stop being aspirational."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Sundar Pichai Just Booked Google's First $100 Billion Quarter. The Real Test Ships Next.",
        "subheadline": "Alphabet's CEO says AI is expanding Search, not eating it — and for the tens of thousands of Indian engineers inside Google, the milestone is a referendum on the bet that pays their salaries.",
        "slug": make_slug("sundar-pichai-google-alphabet-100-billion-quarter-gemini-3-ai"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Google's record quarter is a referendum on whether the company employing tens of thousands of Indian engineers has survived the AI transition — and on whether the next model, Gemini 3, keeps the machine that pays them running.",
        "tags": ["sundar-pichai", "google", "alphabet", "gemini", "ai", "indian-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/sundar-pichai-hails-googles-first-usd-100-billion-quarter/"},
            {"name": "Google I/O 2026 keynote (blog.google)", "url": "https://blog.google/technology/ai/google-io-2026-keynote-sundar-pichai/"},
            {"name": "Mint", "url": "https://www.livemint.com/technology/google-io-2026-highlights-gemini-3-5-flash-antigravity-2-0-ai-overhaul-in-google-search-announced.html"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg/330px-Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Alphabet and Google CEO Sundar Pichai, who announced the company's first $100 billion quarter.",
        "image_attribution": "Wikimedia Commons",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Canadian Pension Fund Just Bet $740 Million on Indian Server Farms. For NRI Investors, That's the Tell.",
        "subheadline": "CPP Investments is buying into CtrlS Datacenters as India's data-center market races toward $13 billion — and the AI boom finally has an India-based infrastructure trade.",
        "slug": make_slug("cpp-investments-ctrls-datacenters-india-ai-infrastructure-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "When one of the world's most conservative pension funds pours $740 million into Indian data centers, it signals a credible, India-based AI-infrastructure trade for NRI investors — and a new wave of hyperscale engineering jobs that won't all sit in the United States.",
        "tags": ["data-centers", "ctrls", "cpp-investments", "ai-infrastructure", "india-tech", "nri-investing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/cpp-investments-invest-740-million-indias-ctrls-datacenters/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Server racks inside a modern data center, the physical infrastructure underpinning the AI boom.",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "HCLTech Just Bought a Piece of the AI That Was Supposed to Kill It. The Target: India's Own Models.",
        "subheadline": "A $1.5 billion bet on Sarvam AI turns India's sovereign-AI slogan into a balance-sheet commitment — and gives diaspora researchers a credible reason to look home.",
        "slug": make_slug("hcltech-sarvam-ai-stake-sovereign-ai-india-it-services"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "As Washington tightens who can touch frontier AI models, India's push for a sovereign-AI stack — now backed by HCLTech's stake in Sarvam — becomes both a source of new senior research jobs at home and a career hedge for Indian engineers inside US AI labs.",
        "tags": ["hcltech", "sarvam-ai", "sovereign-ai", "indian-tech", "it-services", "ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-hcltech-buy-105-stake-sarvam-ai-valuing-startup-15-billion/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/9242888/pexels-photo-9242888.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An engineer works on a circuit board, representing India's push to build its own AI hardware and model stack.",
        "image_attribution": "Pexels",
        "body": article3_body
    }
]

for art in articles:
    try:
        wc = len(art["body"].split())
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
