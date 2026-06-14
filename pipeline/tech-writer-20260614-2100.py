#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-14 21:00 UTC run"""
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
    # ── ARTICLE 1: Sarvam AI at G7 ──────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Sarvam AI Gets a Seat at the G7 Table. It's the Only Indian Company There.",
        "subheadline": "The IIT Madras-incubated startup will join Sam Altman, Dario Amodei, and Demis Hassabis at a working lunch with world leaders in Evian-les-Bains this week — a first for an Indian AI company.",
        "slug": make_slug("sarvam-ai-g7-summit-evian-pratyush-kumar-india-sovereign"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's sovereign AI ambitions now have a voice at the world's most powerful governance table — a signal to NRI engineers and investors that Indian-built AI is being taken seriously at the highest levels.",
        "tags": ["sarvam-ai", "g7-summit", "india-ai", "sovereign-ai", "pratyush-kumar"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/tech-executives-attend-g7-summit-leaders-address-ai-online-safety-2026-06-12/"},
            {"name": "Livemint", "url": "https://www.livemint.com/technology/tech-news/meity-picks-sarvam-ai-to-lead-indias-sovereign-llm-effort-vaishnaw-vows-global-competition-11745611234567.html"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/ai-tech/sarvam-ai-to-open-source-indiaai-missions-foundational-llms"},
            {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/tech-executives-to-attend-g7-summit-as-leaders-address-ai-online-safety/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/26804169/pexels-photo-26804169.jpeg",
        "image_caption": "AI industry leaders gather at a global technology summit",
        "image_attribution": "Pexels",
        "body": """When the G7 leaders sit down for a working lunch in Evian-les-Bains, France, on June 17, the guest list will read like a roll call of Western AI's commanding heights: Sam Altman of OpenAI, Demis Hassabis of Google DeepMind, Dario Amodei of Anthropic, and Arthur Mensch of Mistral AI. But one name will stand apart from the Silicon Valley and European contingent — Pratyush Kumar, co-founder of Bengaluru-based Sarvam AI.

It is the only Indian AI company on the invitation list.

## A table set for eleven

Reuters reported on June 12 that French officials have assembled a roster of AI executives to meet with G7 heads of state during the three-day summit. The attendees include Marc Benioff of Salesforce, Aidan Gomez of Cohere, Robin Rombach of Black Forest Labs, Victor Riparbelli of Synthesia, Alex Wang of Meta, and Ren Ito of Sakana AI.

The lunch is designed to address AI regulation, infrastructure, and online safety — questions that until recently were debated almost exclusively among American and European players. Kumar's presence signals that the G7 now views India's AI trajectory as geopolitically significant enough to include in those conversations.

## From IIT Madras to the sovereign stack

Sarvam AI was incubated at IIT Madras and co-founded by Kumar, a former NVIDIA researcher, alongside Vivek Raghavan. The startup has positioned itself as India's leading sovereign AI company — the firm tasked by the government's IndiaAI Mission with building the country's first indigenous large language model.

Under the programme, Sarvam received access to 4,096 NVIDIA H100 GPUs and ₹98.68 crore in subsidised compute — the mission's single largest allocation. The company is developing three model variants: Sarvam-Large for reasoning, Sarvam-Small for real-time applications, and Sarvam-Edge for on-device tasks, all built with native fluency across ten Indian languages. In June, it announced plans to open-source the models, responding to public pressure about taxpayer-funded AI remaining proprietary.

The startup has also partnered with IITM Pravartak Technologies Foundation to deploy sovereign AI across public administration, defence, and financial services — sectors where data sovereignty is not an abstract principle but a national security requirement.

## Why G7 matters for India's AI ambitions

For an Indian AI company, a seat at the G7 is more than optics. The summit's AI discussions will shape regulatory frameworks, compute-sharing agreements, and safety standards that will define how foundational models are built and deployed globally. India — with 1.5 million STEM graduates annually, government-backed GPU infrastructure, and a stated ambition to build "AI in India, for India" — has a direct stake in whether those frameworks accommodate sovereign models or default to American and European standards.

The IndiaAI Mission has already onboarded over 38,000 GPUs through its compute portal, offered at roughly 42% below market rates. It aims for 100,000 public GPUs by December 2026. At the India AI Impact Summit in February, firms including Microsoft, NVIDIA, and Adani collectively pledged over $200 billion in AI-related investments.

## What NRIs should watch

For Indian engineers at American AI labs — and there are many, from OpenAI's CTO Vijaye Raji to Anthropic's CTO Rahul Patil to Apple's new AI VP Amar Subramanya — Sarvam's G7 invitation raises an interesting question: whether sovereign AI efforts can create a credible alternative career path back home.

For NRI investors, the signal is more concrete. Sarvam's valuation is reportedly approaching $1.5 billion in ongoing funding talks. The company's competitor Krutrim, founded by Ola's Bhavish Aggarwal, recently pivoted from model development to cloud services after struggling with the economics of building large-scale AI systems. Sarvam's government backing and open-source strategy represent a different bet — that subsidised compute and institutional support can sustain what private capital alone could not.

Whether Kumar's lunch with world leaders translates into anything beyond symbolism will depend on what India brings to the table. But the fact that it has a seat at all is, by itself, a first."""
    },

    # ── ARTICLE 2: Asha Sharma Xbox Reset ────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Asha Sharma's 100-Day Verdict on Xbox: 'This Cannot Continue'",
        "subheadline": "The Indian-origin CEO's reset memo reveals a gaming division bleeding money at 3% margins, a hardware crisis that has quintupled component costs, and a parent company that hasn't ruled out selling the whole thing.",
        "slug": make_slug("asha-sharma-xbox-ceo-reset-microsoft-spinoff-layoffs"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "An Indian-origin executive now holds the reins of one of gaming's most consequential turnarounds — and her decisions will ripple through thousands of Indian engineers at Microsoft's global workforce.",
        "tags": ["asha-sharma", "xbox", "microsoft", "satya-nadella", "gaming", "indian-ceo"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "GeekWire", "url": "https://www.geekwire.com/2026/microsoft-ceo-satya-nadella-on-xbox-we-have-to-turn-this-into-a-sustainable-business/"},
            {"name": "The Information", "url": "https://www.theinformation.com/articles/microsoft-xbox-asha-sharma-spinoff"},
            {"name": "Gizmodo", "url": "https://gizmodo.com/xbox-ceo-is-preparing-gamers-for-when-hardware-is-a-luxury-2000613948"},
            {"name": "Kotaku", "url": "https://kotaku.com/xbox-ceo-next-halo-fallout-elder-scrolls-faster-2000613950"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16776036/pexels-photo-16776036.jpeg",
        "image_caption": "An Xbox gaming controller — the hardware at the centre of Microsoft's restructuring debate",
        "image_attribution": "Pexels",
        "body": """Asha Sharma did not wait for the hundred-day grace period to expire before delivering the diagnosis. In a memo co-written with Xbox publishing head Matt Booty and sent to employees on June 12, the Indian-origin CEO of Microsoft's gaming division was blunt: Xbox will finish the fiscal year at roughly a 3% margin. Microsoft has poured over $20 billion into the division over five years. Annual revenue has fallen.

"This cannot continue," Sharma wrote.

## The numbers behind the reset

Hours after the memo, Microsoft CEO Satya Nadella appeared on the New York Times' Hard Fork podcast and offered an equally candid assessment. "No one can accuse Microsoft of not having invested for the last 25 years," he said. "And now we have to turn this into a sustainable business."

Nadella added, with a chuckle, that "there's more monetization of Xbox games happening on YouTube than at Microsoft" — a line that is both darkly funny and arithmetically devastating for a division that acquired Activision Blizzard for $69 billion just three years ago.

The immediate crisis is hardware. Sharma's memo disclosed that console storage components are already twice as expensive as they were last autumn, and memory prices are expected to reach five times their level a year ago. Xbox's next-generation console, codenamed Project Helix, is caught in the squeeze. "We are currently unable to make as many consoles as players want to buy," the memo acknowledged.

## Layoffs, cuts, and franchise bets

Bloomberg reported that Xbox is planning major layoffs next month. The Information, citing three sources with direct knowledge, said Sharma is cutting lower-performing studios and projects to redirect investment into proven franchises: Halo, Fallout, The Elder Scrolls, and Minecraft. The game development budget will remain flat for fiscal year 2027, but the distribution will shift sharply.

It is a direct reversal of the strategy pursued under Phil Spencer, Sharma's predecessor, who spent a decade acquiring studios and building a diverse content library for Xbox's Netflix-style Game Pass subscription. Sharma's thesis is that breadth without profitability is not a strategy — it is a subsidy.

## The spinoff question

Perhaps the most consequential revelation is structural. The Information reported that Nadella and CFO Amy Hood have not ruled out restructuring Xbox entirely — spinning it out as a wholly owned subsidiary like LinkedIn or GitHub, forming a joint venture, or selling the division outright. No decision is imminent, but the discussions are active.

For Sharma, the next twelve months are effectively an audition. How quickly her franchise-first, cost-discipline approach shows results will determine whether Xbox remains inside Microsoft or finds a new home.

## Why this matters to Indian professionals

Sharma's appointment in February made her one of the most prominent Indian-origin executives in gaming — a $200 billion global industry with remarkably few Indian faces at the top. Her trajectory — she previously served as Microsoft's EVP and held leadership roles at Instacart and Palo Alto Networks — mirrors the career arc of many Indian-American executives who rise through operations and strategy roles in Silicon Valley.

The restructuring she is leading will also affect Indian engineers directly. Microsoft's India operations employ tens of thousands of workers, and the company's gaming division has engineering teams across multiple countries. Layoffs at Xbox will not be geographically contained.

For NRI investors holding Microsoft stock — and MSFT remains one of the most widely held equities among Indian-American households — the Xbox question is material. Microsoft's share price has slid nearly 10% since its Build conference in early June, and the gaming division's restructuring is part of the weight dragging on sentiment, alongside broader concerns about AI capital expenditure returns.

Sharma has been handed the hardest job in gaming. Whether she can turn a quarter-century of subsidised entertainment into a sustainable business will define not just Xbox's future, but a new chapter in the growing roster of Indian-origin leaders reshaping Big Tech from the inside."""
    },

    # ── ARTICLE 3: Alphabet $84.75B equity raise ────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Sundar Pichai Is Selling $85 Billion of Alphabet to Win the AI Race. Investors Are Divided.",
        "subheadline": "The largest equity offering in tech history includes a $10 billion anchor from Warren Buffett's Berkshire Hathaway. Alphabet plans to spend up to $190 billion this year alone — and it ordered three million TPUs from Intel.",
        "slug": make_slug("sundar-pichai-alphabet-85-billion-equity-ai-berkshire"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Sundar Pichai's most consequential financial gamble reshapes the company tens of thousands of Indian engineers call home — and it may determine whether Google or OpenAI defines the next era of computing.",
        "tags": ["sundar-pichai", "alphabet", "google", "ai-spending", "berkshire-hathaway", "indian-ceo"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/alphabet-raise-8475-billion-upsized-equity-offering-fund-ai-ambitions-2026-06-03/"},
            {"name": "Bloomberg", "url": "https://news.bloombergtax.com/tax-accounting/alphabet-upsizes-offering-for-ai-spending-to-85-billion-1"},
            {"name": "Motley Fool", "url": "https://www.fool.com/investing/2026/06/14/alphabet-raising-84-billion-win-ai-wars-celebrate-worry/"},
            {"name": "Ainvest", "url": "https://www.ainvest.com/news/alphabets-85b-raise-forever-stock-opportunity-or-ais-biggest-capital-test-2606130030/"},
            {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/alphabet-googl-places-an-order-with-intel-to-manufacture-more-than-three-million-tensor-processing-units-in-2028-1505893/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Sundar Pichai, CEO of Alphabet and Google",
        "image_attribution": "Wikimedia Commons",
        "body": """For most of its two decades as a public company, Alphabet bought back its own stock. Now, under Sundar Pichai, it is doing the opposite — and at a scale that has no precedent in technology.

Earlier this month, Alphabet announced an $84.75 billion equity offering, upsized from an initial $80 billion plan within 48 hours. The structure tells its own story: $18 billion in Class A and Class C common shares, $16.75 billion in depositary shares, a $40 billion at-the-market programme beginning in Q3, and a $10 billion private placement anchored by Warren Buffett's Berkshire Hathaway.

It is the largest equity raise in tech history. And it is being used for a single purpose: winning the AI infrastructure race.

## The arithmetic of ambition

Alphabet's annual capital expenditure forecast now stands at $180 billion to $190 billion for 2026 — a figure that would have been unthinkable three years ago, when the company's total capex was roughly $32 billion. The combined AI infrastructure spending by major tech companies is on track to exceed $700 billion this year, up from prior expectations of about $600 billion.

The money is going into data centres, custom chips, and the raw compute capacity that underpins everything from Google Search's AI Overviews to the Gemini model family, which Alphabet says is nearing 900 million monthly active users.

On the chip front, Reuters reported that Google has placed an order with Intel to manufacture more than three million tensor processing units (TPUs) in 2028. The move would bolster Intel's struggling foundry business and reduce Google's dependence on TSMC, whose capacity constraints have pushed several AI chip designers to explore alternatives. Analyst Gil Luria of D.A. Davidson noted that both Google and NVIDIA have strategic reasons to support Intel's US-based manufacturing, particularly given the current administration's push for domestic chip production.

## The market's mixed verdict

Alphabet's stock fell 1.2% after the initial offering announcement and slipped further — as much as 5% — when the full capex guidance became clear. The concern is straightforward: dilution. Alphabet is selling new shares, which means existing shareholders own a smaller piece of the company.

But the offering was massively oversubscribed. The first tranche alone raised $45 billion. TD Cowen raised its price target to $475, citing expectations that Google's data centre capacity will grow more than tenfold from 2022 to 2031. Analysts note that Alphabet's demand for AI services is exceeding available supply — a situation where additional capacity is not speculative but responsive.

The Berkshire Hathaway anchor is perhaps the most telling signal. Buffett, historically sceptical of technology investments, is effectively endorsing Pichai's bet that AI infrastructure spending will generate durable returns.

## What Pichai is really buying

The spending is aimed at three interlocking goals. First, Google Cloud, which grew 63% year-over-year to $20 billion in the most recent quarter, with operating income tripling to $6.6 billion. Cloud's backlog has nearly doubled quarter-over-quarter to $460 billion. Second, the Gemini ecosystem, where Alphabet is competing directly with OpenAI and Anthropic for developer and enterprise adoption. Third, custom silicon — TPUs — that give Google cost and performance advantages over rivals who rely entirely on NVIDIA GPUs.

The Intel TPU order fits into a broader pattern. Apple recently signed a $1 billion annual deal to route its rebuilt Siri through Google Cloud on NVIDIA Blackwell GPUs. The combination of cloud growth, captive chip production, and external licensing revenue creates an economic flywheel that Pichai is betting will justify the dilution.

## The diaspora dimension

For Indian engineers at Google — and they are present at every level, from DeepMind researchers to Cloud sales teams to the TPU hardware division — the equity raise has immediate implications. Alphabet stock is a significant component of total compensation at the company. Dilution affects everyone holding RSUs.

But the spending also creates opportunities. Google's data centre expansion, its Cloud hiring, and its TPU engineering all require talent at scale. Indian professionals, who already account for a disproportionate share of H-1B visa holders at Alphabet, stand to benefit from the infrastructure buildout — provided the AI bet pays off.

For NRI investors, the question is simpler but no less consequential: is Pichai spending to win, or spending because he has no choice? The answer may be both. In an AI race where falling behind on compute means falling behind permanently, the cost of not spending may be higher than the cost of dilution. Buffett, at least, seems to think so."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
