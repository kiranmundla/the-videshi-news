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
        "headline": "AI's Biggest Rivals Just Agreed on One Thing: Their Own Technology Scares Them",
        "subheadline": "CEOs of OpenAI, Anthropic, Google DeepMind, and Microsoft signed a joint letter urging Congress to mandate screening of synthetic DNA orders before AI makes bioweapons accessible to amateurs.",
        "slug": make_slug("ai-ceos-biosecurity-synthetic-dna-congress-letter"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Indian-origin researchers are deeply embedded in AI safety teams at every signatory company. India's pharmaceutical sector — the world's largest vaccine manufacturer — relies heavily on synthetic DNA for drug development and could face compliance costs from new US screening mandates.",
        "tags": ["ai-safety", "biosecurity", "openai", "anthropic", "deepmind", "regulation", "indian-biotech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com/tech/ai/top-ai-ceos-call-for-law-protecting-against-biological-weapons-38fb3b6d"},
            {"name": "Reuters / Crypto Briefing", "url": "https://cryptobriefing.com/openai-anthropic-synthetic-dna-regulation/"},
            {"name": "The Register", "url": "https://www.theregister.com/2025/06/04/ai_biosecurity_open_letter/"},
            {"name": "Inc.", "url": "https://www.inc.com/kit-eaton/openai-anthropic-meta-agree-critical-decision-ai-safety/91048709"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
        "image_caption": "Anthropic CEO Dario Amodei, one of the signatories of the biosecurity letter to Congress",
        "image_attribution": "Wikimedia Commons",
        "body": """It takes something genuinely alarming to get Sam Altman, Dario Amodei, Demis Hassabis, and Mustafa Suleyman to co-sign the same document. These four men run companies — OpenAI, Anthropic, Google DeepMind, and Microsoft AI — that are locked in the fiercest commercial rivalry in technology. They compete for talent, compute, and market share with a ferocity that makes the old browser wars look quaint. Yet on June 3, they put their names on a single letter addressed to the United States Congress, asking for something the tech industry almost never asks for: more regulation.

The letter, organised by the Foundation for American Innovation and the Institute for Progress, calls on lawmakers to mandate screening of all synthetic DNA and RNA orders placed in the United States. The argument is blunt. AI systems are now good enough at biology to meaningfully lower the barriers that have historically prevented bad actors from designing dangerous pathogens. Voluntary screening by nucleic acid suppliers exists, but the signatories say it leaves gaps that statutory requirements must close.

## When Competitors Agree, Listen

The breadth of the coalition is what makes the letter unusual. Beyond the four AI CEOs, the signatories include Patrick Collison of Stripe, Paul Graham of Y Combinator, Emily Leproust of Twist Bioscience (one of the largest DNA synthesis providers), David Baker (the 2024 Nobel Prize winner in chemistry), former Army Secretary Christine Wormuth, and dozens of national security and life sciences experts. When people who normally cannot agree on a lunch venue sign the same policy proposal, it suggests genuine urgency.

OpenAI's internal red-teaming exercises since early 2024 have apparently produced concerning enough results to convince the company that voluntary norms are insufficient. Tests showed that large language models could outline detailed steps for acquiring materials, designing sequences, and evading detection. A New York Times investigation in April published transcripts of chatbots providing bullet-point instructions for assembling pathogens — transcripts that reportedly "went cold" for the scientists reading them.

## What They Want

The proposals are specific. Vendors who synthesise DNA and RNA sequences would screen every order against databases of known dangerous sequences. Customer verification would become mandatory. Comprehensive risk assessments would be required before orders ship. And recordkeeping for synthesis orders and sequence data would allow tracing of potentially dangerous activity after the fact.

The letter does not name a specific bill or propose legislative language. It positions the request as a national security matter, arriving days after President Trump signed an executive order directing federal agencies to expand AI-enabled cybersecurity tools.

## Why Indian Americans Should Care

The letter's implications ripple directly into the Indian diaspora's professional and economic world. Indian-origin researchers hold prominent positions on the AI safety teams at every signatory company. Anthropic's safety research has drawn heavily from the Indian ML talent pipeline, and Google DeepMind's London and Bangalore offices collaborate on responsible AI development.

But the bigger exposure is pharmaceutical. India is the world's largest manufacturer of vaccines by volume — the Serum Institute of India alone produces over 1.5 billion doses annually. Indian biotech companies including Biocon, Bharat Biotech, and a growing cohort of startups depend on synthetic DNA for drug development, gene therapy research, and vaccine design. If the US imposes mandatory screening requirements, Indian companies with American operations, suppliers, or research partners would face new compliance costs and potential delays in procurement.

For NRI investors tracking Indian pharma stocks or working in US-based biotech, the regulatory trajectory matters. Screening mandates would raise costs for small biotech firms while likely benefiting large incumbents who can absorb compliance overhead — a dynamic that could reshape the competitive landscape of an industry where Indian companies punch well above their weight.

The uncomfortable truth the letter exposes is not new, but AI has sharpened it: the same tools that accelerate vaccine development can accelerate its opposite. The four men who know AI's capabilities best just told Congress they cannot solve this alone. That admission, from an industry allergic to regulation, deserves attention."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Meta Wants Tens of Billions From Shareholders to Build AI. Zuckerberg's Engineers Will Feel It First.",
        "subheadline": "Following Alphabet's record $85 billion equity raise, Meta is exploring a massive stock offering to fund up to $145 billion in AI capital expenditure this year — a move that would dilute every employee holding RSUs.",
        "slug": make_slug("meta-stock-offering-ai-capex-rsu-dilution-indian-engineers"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Meta employs thousands of Indian engineers on H-1B visas whose compensation is heavily weighted toward RSUs. A large equity offering directly dilutes their net worth. NRI investors holding Meta shares through US brokerage accounts face the same arithmetic.",
        "tags": ["meta", "ai-infrastructure", "stock-offering", "alphabet", "capex", "rsu", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Financial Times via Reuters", "url": "https://www.reuters.com/technology/meta-weighs-big-equity-raising-finance-ai-infrastructure-ft-reports-2026-06-06/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/meta-stock-price-today-stock-offering-alphabet-ai-e6782abe"},
            {"name": "MarketWatch / Morningstar", "url": "https://www.morningstar.com/news/marketwatch/20260606225/first-google-then-meta-big-tech-may-increasingly-sell-stock-to-bankroll-820-billion-ai-boom"},
            {"name": "Morningstar", "url": "https://www.morningstar.com/news/dow-jones/202506051520/meta-platforms-slips-on-report-of-plans-for-multibillion-dollar-offering-to-fund-ai-buildout"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0e/F20250904AH-2824_%2854778373111%29_%283x4_cropped_on_Zuckerberg_following_the_rule_of_thirds%29.jpg",
        "image_caption": "Meta CEO Mark Zuckerberg, whose company is exploring a massive equity raise to fund AI spending",
        "image_attribution": "Wikimedia Commons",
        "body": """The world's largest technology companies have discovered that even $100 billion in annual free cash flow is not enough to feed an AI arms race. On Friday, the Financial Times reported that Meta Platforms is considering raising tens of billions of dollars through a stock offering to fund its artificial intelligence ambitions — a move that sent its shares tumbling 5.5% to $593.

The announcement follows Alphabet's own record-breaking equity raise earlier in the week, which was upsized from $80 billion to $84.75 billion on the back of strong investor demand. The Google parent sold $18 billion in common stock and $16.8 billion in mandatory convertible preferred stock, with Berkshire Hathaway taking a $10 billion private placement. Meta's internal discussions reportedly intensified after watching Alphabet's successful execution.

## The Numbers Are Staggering

Meta has raised its capital expenditure guidance for 2026 to between $125 billion and $145 billion, up from an already eye-watering forecast of $115 billion to $135 billion. Alphabet now intends to spend up to $190 billion this year. UBS analysts recently upped their total AI capital expenditure forecast across the industry to $820 billion for 2026 and nearly $990 billion for 2027. More than 85% of that spending is concentrated among four companies: Meta, Alphabet, Microsoft, and Amazon.

A Meta spokesperson told the FT that the share-sale reports were "pure speculation," but added with telling candour that the company would "continue focusing on raising capital in the most flexible ways" to support its AI ambitions. When a company calls something speculation while simultaneously explaining why it would make sense, the speculation is usually well-founded.

## The RSU Arithmetic

For the thousands of Indian engineers at Meta — many of whom relocated on H-1B visas with compensation packages weighted heavily toward restricted stock units — the implications are immediate and personal. A large equity offering dilutes existing shareholders. More shares outstanding means each share represents a smaller slice of the company. The math is not abstract when 40% or more of your annual compensation is denominated in stock.

Meta's stock has already had a rough week. The broader Nasdaq fell 4.2% on Friday in its worst session in over a year, triggered by a semiconductor selloff and a stronger-than-expected May jobs report that raised fears of a Federal Reserve rate hike. Meta's 6.3% weekly decline hit harder than the index-level damage. For an Indian engineer in Menlo Park whose RSU vesting date falls in the next quarter, the compounding effect of a market selloff and potential dilution is uncomfortable.

The pattern is not unique to Meta. Indian tech professionals across Big Tech hold significant portions of their net worth in employer stock — a concentration risk that H-1B constraints make difficult to diversify. Visa holders cannot easily switch employers to rebalance, and many have deferred major financial decisions (buying a house, investing in India) based on stock-price projections that a dilutive offering would revise downward.

## The Bigger Picture

What makes the current moment distinctive is the sheer velocity of capital deployment. The hyperscalers are not merely investing in AI — they are waging a capital war where the entry ticket keeps doubling. Data centres require land, power, water, and custom silicon. The construction timelines stretch years into the future. The returns remain uncertain.

For NRI investors holding Meta or Alphabet shares through US brokerage accounts, the equity raises present a familiar dilemma. Dilution is bad in the short term, but the capital is being deployed into infrastructure that could generate decades of returns — provided the AI monetisation thesis holds. The risk is that $820 billion in annual industry spending creates a glut of compute capacity before demand catches up, repricing the entire sector.

Indian IT services companies face the secondary effect. As hyperscalers build in-house AI capabilities and pour capital into their own infrastructure, the outsourcing contracts that firms like TCS, Infosys, and Wipro depend on could shift in scope and margin. The cloud computing boom enriched Indian IT; the AI capital war may not be as generous.

Meta's share price will recover or it will not. The underlying question for the Indian diaspora is whether the AI infrastructure buildout represents the next great wealth-creation cycle — or the last excess of a bull market running on borrowed conviction."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Amazon Built a Warehouse Robot You Can Talk To. It May Replace 160,000 Jobs.",
        "subheadline": "The e-commerce giant's next-generation Proteus robot understands conversational language and can operate across entire fulfilment centres — part of a $12 billion European push that previews the automation wave heading for India's logistics sector.",
        "slug": make_slug("amazon-proteus-robot-conversational-ai-warehouse-automation"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Amazon is one of the largest H-1B employers in the US and employs tens of thousands in India. Indian engineers build the AI systems powering these robots, while India's own booming e-commerce sector — with over a million warehouse workers — faces the same automation trajectory.",
        "tags": ["amazon", "robotics", "warehouse-automation", "ai", "logistics", "india-ecommerce", "jobs"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/amazon-unveils-new-ai-warehouse-robot-12-billion-europe-push-2026-06-05/"},
            {"name": "Gizmodo", "url": "https://gizmodo.com/amazon-now-has-a-warehouse-robot-that-understands-human-language-2000610947"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/amazons-conversational-proteus-robot-heads-to-europe-in-2027/"},
            {"name": "CoinCentral", "url": "https://coincentral.com/amazon-amzn-stock-holds-firm-after-unveiling-new-ai-warehouse-robot-in-uk/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36522028/pexels-photo-36522028.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "An automated robotic arm handling storage crates in a modern warehouse facility",
        "image_attribution": "Pexels",
        "body": """The original Proteus looked like an oversized Roomba with delusions of grandeur. It hauled heavy carts around Amazon's loading docks, confined to specific areas, controlled through technical commands that required specialised interfaces. Useful, but limited. The kind of machine you worked around, not with.

The new Proteus, unveiled Thursday at Amazon's "Delivering the Future" event in Dartford, England, is a different proposition. It understands plain conversational language. You tell it what needs to be done — in words, not code — and it figures out the priority, the route, and the timing on its own. "It becomes your assistant for material movement," said Scott Dresser, vice president of Amazon Robotics, with the kind of understatement that tends to precede industrial revolutions.

## From Dock to Floor

The upgrade is not merely cosmetic. The current Proteus operates at 25 US facilities, restricted to dock areas where it moves carts weighing up to 400 kilograms. The new version can work across entire warehouse floors — transporting containers, shifting items between stations, and supporting staff throughout the building. The conversational AI lets it interpret context and adapt without constant human micromanagement, a capability that makes its operating envelope essentially the size of the building it inhabits.

Amazon revealed the robot as part of a €10 billion ($11.6 billion) investment in its European fulfilment network. The new Proteus is expected to deploy in Europe in the first half of 2027. Alongside it, Amazon showcased STARK, a robotic tote-handling system first piloted in Barcelona and set to roll out to 15 European sites by next year, and Vulcan, its first robot with a sense of touch. The company now has more than one million robots working across its global fulfilment network.

## The Job Displacement Question

Amazon, as always, insists that automation complements rather than replaces human workers. The company's official line is that robots handle "repetitive and physically demanding tasks" so employees can "focus on higher-skilled roles." The data tells a different story. Internal documents obtained by the New York Times last year revealed that Amazon's automation team expected the company could avoid hiring more than 160,000 US workers by 2027. The robotics team's ultimate goal, per those documents: automate 75% of the company's operations.

The gap between the public narrative and the internal targets is the quiet part that everyone in logistics hears loud and clear.

## The Indian Angle

Amazon's relationship with India operates on multiple planes. The company is one of the largest H-1B visa sponsors in the United States, employing thousands of Indian engineers across its robotics, AI, and cloud divisions. Indian talent builds the machine learning models that power Proteus's conversational abilities. In Bangalore and Hyderabad, Amazon's development centres contribute to the core robotics stack.

But the more consequential exposure may be in India's own logistics sector. India's e-commerce market — led by Flipkart, Amazon India, Meesho, and a growing constellation of quick-commerce startups — employs over a million warehouse workers. The fulfilment centre workforce has grown rapidly, powered by the same consumer demand that makes India one of Amazon's priority markets. If conversational robotics can replace human coordination in European and American warehouses, the technology will eventually arrive at Indian facilities too.

The economics make it inevitable. India's warehouse labour costs are lower than those in the US or Europe, which delays the automation timeline — but they are rising. Quick-commerce players like Blinkit and Zepto are already investing in dark-store automation. Flipkart has experimented with robotic sortation. As the cost of conversational AI drops and the cost of labour rises, the crossover point approaches.

## What to Watch

For Indian engineers at Amazon, the Proteus launch is both opportunity and warning. The teams building these systems are growing, which means more jobs for AI and robotics specialists. But the broader automation trajectory suggests that the warehouse workforce these engineers are replacing will eventually include workers in India too.

For NRI investors, Amazon's $200 billion capital expenditure forecast for 2026 — a more than 50% jump from the previous year — signals that the company views automation as existential infrastructure, not optional spending. The bet is that robots like Proteus will ultimately reduce per-unit fulfilment costs enough to justify the upfront investment.

The new Proteus still looks like a Roomba. The difference is that now, when you talk to it, it talks back — and it already knows where everything goes."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
