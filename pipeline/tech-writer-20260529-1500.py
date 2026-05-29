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


# Validate image URLs
def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        print(f"  ⚠️ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
        return False
    except Exception as e:
        print(f"  ⚠️ Image validation error: {e}")
        return False


articles = [
    # ARTICLE 1: RBI Digital Rupee Cross-Border
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Digital Rupee Is Going International. For NRIs, That Changes Everything.",
        "subheadline": "The RBI's annual report reveals cross-border CBDC pilots with Singapore and the UAE — the two corridors that matter most to the Indian diaspora.",
        "slug": make_slug("rbi-digital-rupee-cross-border-uae-singapore-nri"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Over 4 million Indians live in the UAE and 600,000+ in Singapore — two of the largest remittance corridors to India. A working cross-border digital rupee could slash the cost and time of sending money home, bypassing SWIFT fees and correspondent banking delays that NRIs have endured for decades.",
        "tags": ["digital-rupee", "cbdc", "rbi", "upi", "cross-border-payments", "nri-remittances", "fintech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-rbi-plans-expansion-digital-rupee-through-welfare-schemes-cross-border-2026-05-29/"},
            {"name": "Livemint", "url": "https://www.livemint.com/economy/rbi-to-expand-e-rupee-pilot-to-include-cross-border-payments-welfare-transfers-and-domestic-retail-11748520849000.html"},
            {"name": "TradingView News", "url": "https://www.tradingview.com/news/reuters.com,2026:newsml_L4N3RK0CK:0-rbi-to-explore-cbdc-pilot-in-cross-border-transactions/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5239819/pexels-photo-5239819.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """India's central bank just signalled where it wants to take the digital rupee next — and for the first time, the destination is international.

In its 2025-26 annual report released on Friday, the Reserve Bank of India revealed that it has signed a digital assets memorandum of understanding with the Monetary Authority of Singapore and is in active discussions with the Central Bank of the UAE to pilot cross-border payments using central bank digital currency. The RBI is also participating in multilateral projects led by the Bank for International Settlements.

## Why This Matters More Than UPI Abroad

India's UPI already works in eight countries. But UPI abroad is essentially a convenience layer — it lets Indian tourists pay at shops in Singapore or Dubai using their existing bank accounts. Cross-border CBDC is a fundamentally different proposition. It would enable real-time settlement between central banks, potentially eliminating the correspondent banking chain that currently adds two to three days and $15-25 in fees to every international wire transfer.

For a Malayali nurse in Abu Dhabi sending ₹50,000 home every month, or a software engineer in Singapore remitting savings quarterly, the difference between a 2% fee and a near-zero digital settlement is not trivial. India received $129 billion in remittances in 2025, the highest of any country. The UAE and Singapore are among the top five source corridors.

## The Programmability Play

The more intriguing element is what the RBI calls "programmability." During 2025-26, the central bank ran CBDC pilots across Gujarat, Puducherry, and Chandigarh where food subsidy beneficiaries received government payments directly in digital rupees — with built-in conditions on how the money could be spent.

This is not a feature that excites libertarians, but it is one that interests treasurers and compliance departments. Programmable money could allow an Indian subsidiary of an American company to receive regulatory-compliant payments that automatically satisfy transfer pricing rules, or enable escrow arrangements for cross-border trade that settle without intermediaries.

## The Adoption Paradox

There is a catch. Retail e-rupee circulation actually fell during the year — from ₹10.16 billion to ₹7.71 billion as of March 2026. Over 8 million Indians have used the e-rupee, and 120 million transactions worth ₹28,000 crore have been processed since the 2022 launch, but daily usage remains negligible compared to UPI's 500 million daily transactions.

The RBI appears to be betting that cross-border utility, not domestic convenience, will drive the next phase of adoption. That is a reasonable bet. Nobody in India needs an alternative to UPI for buying chai. But anyone who has tried to wire $10,000 from Dubai to Mumbai on a Friday afternoon knows exactly how broken the existing system is.

## What NRI Investors Should Watch

The RBI also quietly announced that its cloud platform for financial firms — Indian Financial Services Cloud — has gone live in beta mode with nine users, making it one of the first central bank-operated cloud platforms globally. Combined with the CBDC push, this signals a broader ambition: India wants to build the financial infrastructure stack that other countries license, the way UPI's architecture has already been studied and adapted by nations from Brazil to the Philippines.

For NRIs in finance, payments, or fintech, the opportunity set is expanding. For everyone else, the practical question is simpler: within two to three years, sending money home from the Gulf or Southeast Asia could be as instant and cheap as a UPI payment between two Indian bank accounts. The technology is nearly there. The politics and regulation, as always, will determine the timeline."""
    },

    # ARTICLE 2: ASML-Tata Electronics
    {
        "id": str(uuid.uuid4()),
        "headline": "ASML Just Agreed to Equip India's First Real Chip Factory. Here's What That Actually Means.",
        "subheadline": "Tata Electronics' $11 billion Dholera fab signed a strategic partnership with the Dutch lithography monopoly. For Indian semiconductor engineers, this is a zero-to-one moment.",
        "slug": make_slug("asml-tata-electronics-dholera-chip-fab-india-semiconductor"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Thousands of Indian-origin engineers work at ASML, TSMC, Intel, and other semiconductor companies globally. The Dholera fab creates a return-to-India pathway for NRI chip professionals — and an investment thesis for those watching India's semiconductor ambitions.",
        "tags": ["semiconductor", "tata-electronics", "asml", "dholera", "india-chips", "manufacturing", "make-in-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "EE Times", "url": "https://www.eetimes.com/asml-tata-electronics-partner-on-indias-first-300-mm-fab/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/tata-electronics-partners-asml-to-boost-indias-semiconductor-manufacturing-push/article69591342.ece"},
            {"name": "Zacks", "url": "https://www.zacks.com/stock/news/2463091/asml-expands-globally-joins-tata-for-india-semiconductor-hub"},
            {"name": "eeNews Europe", "url": "https://www.eenewseurope.com/en/tata-electronics-and-asml-partner-on-india-semiconductor-fab/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5118462/pexels-photo-5118462.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """When Narendra Modi and Dutch Prime Minister Rob Jetten stood together at The Hague on May 16 to witness Tata Electronics and ASML sign a Memorandum of Understanding, most Indian media treated it as another diplomatic photo-op. It was considerably more than that.

ASML is not just any European company. It is the sole manufacturer of the extreme ultraviolet lithography machines without which no chip smaller than 7 nanometres can be produced. Every advanced processor in your iPhone, your car, and the AI servers powering ChatGPT passes through an ASML machine. The company had revenues of €32.7 billion last year. There is no substitute, no competitor, no alternative supplier.

And it just agreed to equip India's first commercial 300-millimetre semiconductor fabrication facility.

## What Tata Is Actually Building

The Dholera fab, located in Gujarat's special investment region, represents an $11 billion bet by Tata Electronics. The numbers are specific: 50,000 wafer starts per month, process nodes ranging from 28nm to 110nm, and a product mix targeting automotive chips, radio-frequency SoCs for Bluetooth and Wi-Fi, IoT devices, power management ICs, and display drivers.

These are not cutting-edge chips. TSMC manufactures at 3nm; Intel is pushing toward 18A. But the 28nm node is the workhorse of the global economy — it powers the chips in your car's braking system, your washing machine's controller, your building's elevator. And there is a chronic global shortage of exactly this class of semiconductor that the pandemic exposed and the AI boom has worsened, as fab capacity worldwide has tilted toward leading-edge nodes.

Tata's technology partner is Taiwan's Powerchip Semiconductor Manufacturing Corporation (PSMC), which provides the process technology know-how. ASML provides the lithography tools — the deep ultraviolet (DUV) systems that pattern circuits onto silicon wafers with nanometre precision. The MoU also covers workforce training, supply chain development, and R&D infrastructure.

## What It Means for Indian Semiconductor Professionals

There are an estimated 50,000 to 70,000 Indian-origin engineers working in the global semiconductor industry — at Intel in Oregon, ASML in Veldhoven, TSMC in Hsinchu, Samsung in Austin. Many left India because there was nowhere to do front-end semiconductor manufacturing at home.

Dholera changes that equation. The fab will need process engineers, lithography specialists, yield engineers, quality assurance teams, and equipment maintenance crews — roles that currently do not exist in India's employment landscape. Tata has already begun recruiting, and the ASML partnership specifically includes a training programme to build local lithography expertise.

For NRI semiconductor professionals weighing a return to India, the calculus has shifted. The question is no longer "is there an industry to return to?" but "how quickly will it mature?"

## The Bigger Picture

India now has ten approved semiconductor projects worth approximately ₹1.6 lakh crore across six states. Micron's $2.75 billion ATMP facility in Sanand, Gujarat has moved into commercial production. CG Semi's OSAT unit in Sanand has completed its pilot line. Over 270 Indian universities have been given access to advanced chip design tools, with students logging 1.2 million design hours in 2025 alone.

None of this makes India a semiconductor superpower next year, or the year after. The Dholera fab is expected to begin production by late 2027 at the earliest. Building a semiconductor ecosystem — the chemical suppliers, the gas delivery systems, the ultra-pure water treatment, the specialised logistics — takes a decade. South Korea started in the 1980s and did not achieve global competitiveness until the 2000s.

But the ASML partnership removes a critical bottleneck. It signals that the world's most strategically important equipment maker considers India a viable long-term market. For an industry where credibility is measured in decades, that endorsement matters more than the dollar figures suggest."""
    },

    # ARTICLE 3: Apple AI Overhaul with Amar Subramanya
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple's Biggest AI Gamble Is Ten Days Away. An Indian-Origin Engineer Is Calling the Shots.",
        "subheadline": "Amar Subramanya, who built Google's Gemini and spent a stint at Microsoft, is now VP of AI at Apple — and WWDC on June 8 will be his first public test.",
        "slug": make_slug("apple-amar-subramanya-ai-siri-wwdc-indian-engineer"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Amar Subramanya adds to the extraordinary roster of Indian-origin leaders running AI at America's most valuable companies — Pichai at Google, Nadella at Microsoft, and now Subramanya at Apple. For Indian engineers in Silicon Valley, his appointment signals that the pipeline from IIT labs to the C-suite of trillion-dollar companies remains wide open.",
        "tags": ["apple", "siri", "ai", "wwdc", "amar-subramanya", "indian-tech-leaders", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "MacRumors", "url": "https://www.macrumors.com/2026/05/22/macrumors-show-wwdc26-siri-accessibility/"},
            {"name": "WindowsForum", "url": "https://windowsforum.com/threads/apple-names-amar-subramanya-vp-of-ai-as-giannandrea-retires-siri-roadmap-focus.367825/"},
            {"name": "IndMoney", "url": "https://www.indmoney.com/articles/us-stocks/who-is-amar-subramanya-apples-new-ai-chief"},
            {"name": "Bloomberg via Gizbot", "url": "https://www.gizbot.com/news/apple-siri-overhaul-leaks-ahead-of-wwdc-2026-dynamic-island-integration-ai-chatbot-and-more-116064.html"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14314636/pexels-photo-14314636.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On June 8, Apple will stand in front of the world's developers and attempt to prove that it has not irreversibly fallen behind in artificial intelligence. The person responsible for making that case is Amar Subramanya, a University of Washington PhD who spent over a decade at Google building the infrastructure behind Gemini, briefly served as corporate vice president of AI at Microsoft, and was hired by Apple late last year as Vice President of AI.

Subramanya reports directly to Craig Federighi, Apple's software chief — a reporting line that signals urgency. His predecessor, John Giannandrea, reported to Tim Cook. The restructuring pushed AI closer to the team that ships software, not the team that runs the company.

## What WWDC Will Reveal

Bloomberg's Mark Gurman has reported illustrations of a redesigned Siri experience that amounts to Apple's most dramatic software overhaul in years. According to leaked details, Siri will move into the Dynamic Island, gain a dedicated chatbot-style app with conversation history, and — most significantly — support multiple AI models.

Apple is testing a system that lets users route queries to ChatGPT, Google's Gemini, and Anthropic's Claude directly from Siri. A leaked interface mockup shows a model-selection menu, allowing users to choose their preferred AI backend. This is architecturally radical for Apple, a company that has historically refused to let third parties anywhere near the core user experience.

The new Siri will also replace Spotlight search entirely. A "Search or Ask" prompt, triggered by swiping down from the top of the display, will combine system search, app shortcuts, and AI conversations in a single interface.

## Subramanya's Mandate

Subramanya's appointment in late 2025 followed Apple's acknowledgement that its AI-enhanced Siri — supposed to ship with iOS 26 — needed more time. The delays were public and embarrassing. While OpenAI, Google, and Anthropic were releasing increasingly capable AI assistants, Apple's Siri remained the punchline it had been for years.

His mandate is narrower and harder than Giannandrea's was. He runs Apple Foundation Models, machine learning research, and AI safety and evaluation. He does not run the broader services or operations that Giannandrea oversaw. The focus is pure: build the models, make them work on-device within Apple's privacy constraints, and ship.

His background makes him uniquely qualified for this specific problem. At Google, Subramanya was VP of Engineering for Gemini — he did not just study large language models, he built the production systems that serve them at Google's scale. At Microsoft, he saw how enterprise AI products actually reach customers. At Apple, he inherits a company with 2.2 billion active devices, custom silicon designed for on-device inference, and a privacy architecture that constrains what data can leave the phone.

## The Indian AI Leadership Pipeline

Subramanya's appointment extends a pattern that has become impossible to ignore. Sundar Pichai runs Google, which developed Gemini. Satya Nadella runs Microsoft, which funded and partnered with OpenAI. Now Subramanya leads Apple's AI — the third leg of the consumer AI race.

Add Arvind Krishna at IBM, Shantanu Narayen (who announced his departure from Adobe in March after 18 years to make room for an "AI-first" successor), Nikesh Arora at Palo Alto Networks, and Sanjay Mehrotra at Micron — which just crossed $1 trillion in market capitalisation — and the picture is striking. Indian-origin executives are not merely participating in the AI era; they are, in measurable and specific ways, building the infrastructure that defines it.

For the tens of thousands of Indian engineers working at Apple in Cupertino, Hyderabad, and Bengaluru, Subramanya's appointment carries practical significance. His team's work will determine the AI features that ship on every iPhone, iPad, and Mac. His hiring decisions will shape career trajectories. And his success or failure at WWDC on June 8 will be the first public signal of whether Apple's AI ambitions have finally found the engineering leadership they needed.

The keynote begins at 10 AM Pacific Time. The Indian American tech community will be watching with more than casual interest."""
    },
]


for art in articles:
    print(f"\nValidating image for: {art['slug']}")
    if not validate_image(art['image_url']):
        print(f"  ❌ Skipping article due to bad image")
        continue
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
