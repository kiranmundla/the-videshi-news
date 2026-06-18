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

# ============================================================
# ARTICLE 1 — Nikesh Arora / Palo Alto Networks (Indian-origin CEO beat)
# ============================================================
article1_body = """Nikesh Arora has spent the past year making a bet that most cybersecurity CEOs would call reckless: buy faster than the market thinks is prudent, and bet the whole company on the idea that AI agents are about to break every assumption enterprise security was built on. This week he closed another piece of it, completing Palo Alto Networks' $3.35 billion acquisition of Chronosphere, a cloud-monitoring company most consumers have never heard of.

It is the third deal in a string that has become impossible to ignore. Chronosphere follows the $25 billion purchase of CyberArk, the identity-security giant, and a planned acquisition of Portkey, an AI gateway startup. For the Delhi-raised, Air Force Public School alumnus who once ran SoftBank and was Google's chief business officer, this is a wager with his own name on it — Arora personally bought roughly $10 million of Palo Alto stock in March when the shares wobbled.

**Why an Indian American reader should care**

Start with the obvious: a meaningful slice of the engineers building these products are Indian, and Palo Alto Networks is one of the larger employers of Indian tech talent in the Bay Area. When the most acquisitive company in cybersecurity is run by an Indian American and staffed heavily by the diaspora, its strategy is a leading indicator for thousands of careers — what skills get rewarded, which teams grow, which get folded into a larger machine.

But the deeper reason is the thesis itself. Arora's argument is that the rise of autonomous AI agents — software that reasons and acts on a company's behalf — creates an entirely new category of risk. "AI agents have become privileged insiders, reasoning and executing on behalf of users and companies," he wrote on LinkedIn. "With that power comes a new category of risk. You cannot build an agentic enterprise without a centralised control plane to secure it."

**The "platformisation" play**

Chronosphere brings observability — the ability to see, in real time, what is happening across an organisation's applications, infrastructure, and now its AI systems. Its technology will be folded into Cortex AgentiX, Palo Alto's agentic security platform, and its co-founder Martin Mao joins as a senior vice president. The logic is to assemble a single platform that watches everything: identity (CyberArk), AI traffic (Portkey), and system health (Chronosphere).

This is the part that matters for any NRI working in or investing in enterprise software. Arora is betting that customers are tired of stitching together a dozen security vendors and want one company to trust. If he is right, the smaller point-solution startups — many founded by Indian engineers hoping for an acquisition — either get bought or get squeezed. If he is wrong, he has spent close to $30 billion building a conglomerate just as AI commoditises the very tools he bought.

**The market is, for now, convinced**

Palo Alto shares trade near $283, well above their 52-week moving averages and within striking distance of an all-time high around $303. The stock wobbled earlier this year on reports that an Anthropic model could perform some cybersecurity functions on its own — a reminder that the same AI wave Arora is riding could one day erode the moat he is building. He used that dip to buy more.

For the diaspora investor, Palo Alto Networks has become a proxy bet on a specific idea: that securing AI will be a bigger business than building it, and that an Indian American executive with a habit of writing ten-figure cheques is the one to consolidate it. For the diaspora engineer, the same deals are reshaping the org chart in real time.

**The bigger pattern**

Arora is now one of several Indian-origin CEOs reshaping American enterprise tech through aggressive M&A rather than organic product cycles — a contrast with the founder-led, build-it-yourself culture of Silicon Valley's last generation. Whether that approach defines the AI era or gets overtaken by it is the open question. For a community that has supplied an outsized share of both the executives and the engineers, the answer is not academic. It is the shape of the next decade of careers and portfolios."""

# ============================================================
# ARTICLE 2 — Opendoor exits India (top employers / offshoring beat)
# ============================================================
article2_body = """When an American company shuts an Indian office, the usual story is cost-cutting. Opendoor's decision to wind down its entire India operation is something stranger, and more unsettling for the diaspora: the company says the work itself no longer needs to exist.

CEO Kaz Nejatian announced the move in a note to staff, closing offices in Chennai and Bengaluru and affecting roughly 250 employees. "Our customers are in America, and that's where our operational work belongs," he wrote. The framing was not "we found cheaper labour elsewhere." It was that the back-office workflows the India team was built to handle — manual processes stitched across fragmented systems — can now be absorbed by a single integrated platform and a smaller set of AI tools.

**Why this is bigger than one company**

India hosts more than 2,100 Global Capability Centers employing roughly 2.36 million people and generating close to $100 billion in annual revenue. A single 250-person shutdown is a rounding error in that picture. What makes it worth the diaspora's attention is the logic, not the headcount.

For thirty years, the deal underpinning the Indian American story was wage arbitrage: Western companies paid Indian wages for process work instead of American wages, and the resulting industry built entire cities and funded an entire generation's migration to the United States. Opendoor is arguing that AI has changed the arithmetic. When software can do data entry, customer support, and process auditing more accurately than a human, the cost advantage of offshoring that work evaporates — and companies would rather concentrate what remains close to the customer.

Outsourcing analysts quoted in coverage of the move — including Better Tomorrow Ventures' Sheel Mohnot and HFS Research's Phil Fersht — flagged exactly this pattern: US companies redesigning operations around AI and automation, then pulling the most repeatable layer of work back onshore.

**The diaspora sits on a fault line**

For an Indian American family, this story cuts two ways at once. Many in the community arrived precisely because the IT-services and GCC model created a pipeline — campus to Infosys or TCS or a captive center, then an H-1B, then a green card. If AI hollows out the entry-level, repeatable layer that pipeline was built on, the on-ramp that brought a previous generation to New Jersey and the Bay Area narrows for the next.

The timing sharpens it. In the same week, Tata Consultancy Services signaled it may slow hiring, and India's broader tech hiring hit a 28-month low for fresh graduates. The conveyor belt that converted Indian engineering degrees into American careers is, by several measures, jamming.

**But the other side of the ledger matters too**

Opendoor's own numbers show its global workforce fell from 1,470 at the end of 2024 to 1,042 a year later. This is a company getting smaller everywhere, not a triumphant reshoring of hundreds of American jobs. Some roles shifted to existing US teams; most simply vanished. That nuance is easy to lose in the politically charged "jobs coming home" framing the move has attracted in conservative American media.

For the diaspora professional already in the US, the lesson is about which skills survive. The work being eliminated is "repeatable execution and coordination." The work still being hired — at Amazon, which is bringing on 11,000 engineers even as it cuts 30,000 roles elsewhere — is AI infrastructure, machine-learning engineering, and applied AI product development. The diaspora has always been good at moving up the value chain when forced to. It is about to be forced again.

**What to watch**

The question is whether Opendoor is an outlier or a template. If more US firms conclude that AI plus a unified platform makes offshore operations centers obsolete rather than merely cheaper-elsewhere, the GCC boom that has defined Indian tech employment for a generation faces its first existential test. For NRIs weighing a return to India, or sending kids into Indian engineering programs as a hedge, the calculus just got more complicated. The cost advantage that built the bridge between the two countries is the very thing AI is now eroding."""

# ============================================================
# ARTICLE 3 — US curbs Anthropic frontier models for foreign nationals (AI policy / diaspora angle)
# ============================================================
article3_body = """For years the implicit promise of working at an American AI lab was simple: you might be born in Hyderabad or Chennai, but inside the building you had the same tools as everyone else. That promise quietly broke last week. The US Commerce Department ordered Anthropic to block access to its two most advanced models — Claude Fable 5 and Mythos 5 — for "any foreign national anywhere in the world," including researchers inside American labs who help build them.

Because Anthropic could not separate users by citizenship in real time, it did the only thing it could: it shut the flagship models down for everyone. Commerce Secretary Howard Lutnick signed the letter, invoking the 2018 Export Control Reform Act against an AI model for the first time, and warned of criminal and civil penalties for non-compliance. The cited reason was a "jailbreak" vulnerability that officials feared a foreign military intelligence service could exploit. Anthropic called the flaws minor and the move abrupt, but complied.

**Why this lands hard on the diaspora**

This is not abstract policy for Indian Americans. A very large share of the researchers and engineers at frontier labs — Anthropic, OpenAI, Google DeepMind, Meta — are Indian nationals on H-1B or other visas. A directive that bars "foreign nationals" from using the most capable models, even while sitting at their desks in San Francisco building those very models, draws a line straight through the diaspora's professional life.

The logic is jarring. As one analysis put it, US leadership in AI was built "not just on capital and computing power, but also on global talent. Barring them from using the very systems they help develop risks a broad aptitude loss." An Indian researcher could spend the day improving Mythos 5 and be legally barred from querying it. The order does not distinguish between a green-card-holding scientist who has lived in California for fifteen years and a hostile actor abroad.

**The sovereignty argument gets louder**

The episode has supercharged a debate already running hot in India. Ravi Venkatesan, the former Microsoft India chairman, argued that any Indian enterprise that has embedded a US frontier model into a core workflow — credit underwriting, customer service, supply-chain decisions — has "effectively accepted dependency on the continued goodwill of a foreign government." He called it a sovereignty risk, and he is not alone.

The market answered almost immediately. Three days after the Anthropic order, Bengaluru's Sarvam AI raised $234 million at a $1.5 billion valuation — led by HCLTech — to build sovereign Indian models for agentic AI, coding, and cybersecurity. The "access isn't ownership" argument, once the preserve of policy panels, suddenly had a unicorn behind it.

**What an NRI should take from this**

First, regulatory volatility is now a feature of the AI stack, not a bug. Even G7 allies are affected: UK Prime Minister Keir Starmer requested a carve-out for British nationals and was reportedly refused as "completely illogical." If London cannot get an exemption, Indian enterprises betting their workflows on a single US model should assume they could be cut off without warning.

Second, the diaspora's dual identity is becoming a professional liability in a way it rarely has been. An engineer who is "Indian enough" to be restricted but "American enough" to have built the thing is caught in a contradiction Washington has not bothered to resolve. The order, critics note, was issued "without a clear articulation of the standards that trigger such directives, how they are applied and how they may be challenged."

Third, this is, perversely, an opportunity. The capability gap between closed frontier models and the best open-weight alternatives — Mistral, Google's Gemma, India's own Sarvam and BharatGen — has narrowed for most enterprise use cases. For NRI founders and investors, a world where US frontier access is politically contingent makes the case for building, and backing, models that cannot be switched off by a letter from Commerce.

The era of unrestricted frontier AI is over. For the Indians who built much of it, the question now is whether to keep waiting for access to be restored — or to go build the thing nobody can take away."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Nikesh Arora Just Closed His Third Big Deal in a Year. He's Betting $30 Billion That AI Will Break Security as We Know It.",
        "subheadline": "Palo Alto Networks completed its $3.35 billion buy of Chronosphere — the latest in a buying spree by the Indian American CEO who keeps putting his own money on the line.",
        "slug": make_slug("nikesh-arora-palo-alto-chronosphere-cyberark-agentic-ai-bet"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Palo Alto Networks is a major Bay Area employer of Indian engineers, and its Indian American CEO's aggressive AI-security strategy is a leading indicator for thousands of diaspora careers and portfolios.",
        "tags": ["nikesh-arora", "palo-alto-networks", "cybersecurity", "indian-tech", "silicon-valley", "ai-agents"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CRN", "url": "https://www.crn.com/news/security/2026/palo-alto-networks-completes-3-3b-acquisition-of-chronosphere"},
            {"name": "Palo Alto Networks", "url": "https://www.paloaltonetworks.com/company/press/2026"},
            {"name": "Morningstar / MarketWatch", "url": "https://www.morningstar.com/news/marketwatch/2026-palo-alto-networks-ceo-stock-purchase"},
            {"name": "AI Magazine", "url": "https://aimagazine.com/articles/palo-alto-networks-bid-to-secure-the-agentic-enterprise"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg/330px-Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "image_caption": "Palo Alto Networks Chairman and CEO Nikesh Arora speaking at TechCrunch Disrupt",
        "image_attribution": "Wikimedia Commons",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Opendoor Is Shutting Its Entire India Operation. The Reason Isn't Cost — It's That AI Made the Work Disappear.",
        "subheadline": "The real-estate platform is winding down its Chennai and Bengaluru offices, affecting 250 employees, and says the back-office work simply no longer needs to exist offshore.",
        "slug": make_slug("opendoor-india-exit-ai-offshoring-gcc-diaspora-tech-jobs"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The wage-arbitrage offshoring model that built India's tech industry and funded a generation of NRI migration faces its first AI-driven existential test — reshaping the pipeline that brought the diaspora to America.",
        "tags": ["opendoor", "offshoring", "ai-jobs", "india-tech", "gcc", "h1b", "layoffs"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TheStreet", "url": "https://www.thestreet.com/real-estate/real-estate-tech-firm-exits-key-hub-cuts-100s-of-jobs"},
            {"name": "udreamjob / TechCrunch", "url": "https://udreamjob.com/opendoor-india-exit-entry-level-work"},
            {"name": "The Port Journal", "url": "https://theportjournal.com/tcs-opendoor-ai-india-tech-jobs"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8171308/pexels-photo-8171308.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A software professional working in an open-plan technology office",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Washington Just Barred 'Foreign Nationals' From Anthropic's Best AI — Including the Indian Engineers Who Built It.",
        "subheadline": "A first-of-its-kind US export order forced Anthropic to pull Claude Fable 5 and Mythos 5 offline worldwide, drawing a line straight through the diaspora's professional life.",
        "slug": make_slug("us-curbs-anthropic-frontier-ai-foreign-nationals-indian-diaspora-sovereignty"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "A huge share of frontier-AI-lab researchers are Indian nationals on visas — and a US order barring 'foreign nationals' from the top models puts the diaspora's dual identity at the center of a sovereignty fight.",
        "tags": ["anthropic", "ai-policy", "export-controls", "h1b", "indian-researchers", "sovereign-ai", "sarvam"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "PYMNTS / Bloomberg", "url": "https://www.pymnts.com/news/artificial-intelligence/2026/commerce-dept-threatened-anthropic-with-criminal-charges"},
            {"name": "WebProNews / Reuters", "url": "https://www.webpronews.com/us-export-controls-force-anthropic-to-pull-frontier-ai-models-offline"},
            {"name": "Mint (Ravi Venkatesan)", "url": "https://www.livemint.com/opinion/anthropic-frontier-ai-models-india-sovereign-ai"},
            {"name": "New York Post", "url": "https://nypost.com/2026/06/trump-officials-g7-anthropic-ai-models"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2004161/pexels-photo-2004161.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Lines of source code displayed on a developer's screen",
        "image_attribution": "Pexels",
        "body": article3_body
    }
]

# word-count guard
for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']} — {wc} words")

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
