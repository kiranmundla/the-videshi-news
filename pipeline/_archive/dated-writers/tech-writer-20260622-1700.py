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
        "headline": "Every Big Tech Firm Is Cutting H-1B Hiring. Nvidia Just Doubled Down — and Indians Are the Reason.",
        "subheadline": "While Google and Amazon slashed visa sponsorships by up to 40%, Jensen Huang's chipmaker added certifications and pay packages that read like a different economy entirely.",
        "slug": make_slug("nvidia-h1b-hiring-surge-indian-engineers-google-amazon-cuts-jensen-huang"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For Indian engineers who hold roughly 71-73% of US H-1B visas, Nvidia's counter-cyclical hiring is the rare safe harbour in a market where a layoff now triggers a brutal 60-day deadline to find a new sponsor.",
        "tags": ["h1b", "nvidia", "indian-tech", "ai", "silicon-valley", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "Nvidia chief executive Jensen Huang, whose company expanded H-1B hiring while rivals pulled back",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """The numbers tell two stories at once, and which one you live in depends largely on the logo on your badge.

In the first two quarters of fiscal 2026, Nvidia secured certification for roughly **1,200 H-1B positions**, up from about 1,000 in the same window a year earlier — a 20% jump, according to federal labour filings reviewed by *Business Insider*. Over the same stretch, Google's approved H-1B hires reportedly fell to about 2,200 from 5,100, while Amazon's dropped to roughly 4,300 from 6,100. Meta and others have similarly slowed foreign hiring or cut staff outright as they redirect cash toward AI infrastructure.

For the Indian engineer reading this from a cubicle in Sunnyvale or a sublet in Jersey City, that divergence is not abstract. Indians account for an estimated 71% to 73% of approved H-1B beneficiaries in the United States. When the visa music slows, it is overwhelmingly Indian professionals left scanning for a chair.

## Why Nvidia can afford to zig

The simplest explanation is the balance sheet. Nvidia posted a record quarter of around **$81.62 billion**, fueled by insatiable demand for its data-centre chips. A company minting money on that scale can absorb the new $100,000 overseas filing surcharge the Trump administration imposed last September, and can structure offers around the tightened prevailing-wage rules without blinking.

The pay tells the same story. According to compensation data cited by *Outlook Business*, Nvidia research scientists earn between roughly ₹99 lakh and ₹3.41 crore, with principal researchers and engineering directors commanding packages up to ₹4.67 crore — before stock and bonuses. CEO Jensen Huang, himself an immigrant, has repeatedly framed legal immigration as foundational to American technological dominance rather than a cost to be trimmed.

## The stratified market underneath

What is emerging, as immigration trackers have noted, is a two-tier H-1B system. Firms with fat margins and urgent AI or semiconductor needs can still sponsor freely and shape offers around the weighted-selection wage rules. Employers under layoff pressure face a higher hurdle on every petition, now that the $100,000 surcharge sits on top of each filing.

Workers feel that split unevenly. An engineer laid off from a cost-cutting employer must clear the **60-day grace period** in a weaker transfer market, against companies reluctant to shoulder the new fees. A May policy memo added another wrinkle: some H-1B holders pursuing green cards may now have to leave the country for consular processing, a step that can strand families across borders mid-career.

## What it means for the diaspora

For Indian Americans, the lesson is uncomfortably clear. The visa is no longer a generic ticket; it is a function of where you sit in the AI value chain. A specialised researcher in chip architecture or model optimisation at a high-margin firm has rarely been safer. A generalist software engineer at a company chasing efficiency targets has rarely felt more exposed.

The strategic read for families weighing their next move is to treat skills as the real visa. The roles insulated from this slowdown — silicon design, low-level systems, AI infrastructure — are precisely the ones Nvidia is paying crore-plus packages to fill. The federal records behind all of this are public, posted in the USCIS H-1B Employer Data Hub, and they reward one thing above loyalty or tenure: scarcity.

Huang's bet is counter-cyclical by design. For the thousands of Indian engineers watching their peers get pink slips elsewhere, it is also, for now, the most reassuring data point on the board."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Forbes Just Named the 50 Hottest AI Startups. Six Are Run by Indian Americans.",
        "subheadline": "From a cardiologist's medical-scribe tool to the open-source lab behind RedPajama, the diaspora's footprint on Forbes' AI 50 is no longer a curiosity — it's a pattern.",
        "slug": make_slug("forbes-ai-50-2026-indian-american-founders-abridge-perplexity-glean-together"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs deciding whether to join a startup, fund one, or send a resume, the AI 50 is a map of where Indian-American founders are building the most fundable companies in the most competitive sector on earth.",
        "tags": ["ai", "indian-tech", "startups", "forbes", "silicon-valley", "venture-capital"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
            {"name": "Forbes AI 50", "url": "https://www.forbes.com/lists/ai50/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8439082/pexels-photo-8439082.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Engineers at work in an AI startup; six AI 50 companies are led by Indian-American founders",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """Forbes received some 1,900 submissions for its eighth annual **AI 50** this year, more than double last year's count — a measure of how crowded, and how cut-throat, the artificial-intelligence land grab has become. Of the fifty companies that survived the cull, six are led by Indian Americans: **Abridge, Baseten, Codeium, Glean, Perplexity, and Together AI.**

That is not a token sprinkling. It is a cross-section of where the AI economy is actually making money — healthcare, infrastructure, developer tools, enterprise search, consumer answers, and open-source model training — with a diaspora founder at the helm of each.

## The companies, and why they made it

**Abridge**, founded by practising cardiologist Dr Shiv Rao in 2018, attacks the paperwork that swallows clinicians' evenings. It records doctor-patient conversations and uses AI to draft the clinical notes. Ten thousand clinicians already use it, and the company is valued at around $850 million after raising more than $200 million.

**Together AI**, co-founded by CEO Vipul Ved Prakash, has become a backbone for open-source AI. More than 45,000 registered developers use its cloud tools to deploy models, and it produced RedPajama-V2 — at over 30 trillion tokens, the largest open dataset available for training large language models.

**Baseten**, led by Tuhin Srivastava, helps companies run machine-learning workflows on their own cloud or through its platform. It recently raised a $40 million Series B at a $220 million valuation and is pouring the money into GPUs and efficiency.

Rounding out the six are **Perplexity**, the AI answer engine run by Aravind Srinivas; **Glean**, the enterprise-search company; and **Codeium**, the AI coding assistant. Together they span the full stack of the current boom.

## A pattern, not a coincidence

The diaspora's presence on these lists has stopped being remarkable and started being structural. The same names recur across Forbes' franchises — the 30 Under 30 AI cohort this year featured Indian-origin founders at Reducto, Pylon, Delve, Farsight and Vapi, and the Midas List of top investors counted 17 Indian Americans, with Vinod Khosla on top.

The thread running through them is familiar to anyone in the community: the IIT-and-immigration pipeline, the willingness to chase hard technical problems, and an increasingly dense network of Indian-American founders and funders who back one another.

## Why an NRI should read the list closely

For the diaspora, the AI 50 functions as more than a bragging-rights scoreboard. It is a practical map.

If you are an engineer weighing where to spend the next four years, these are companies with proven fundability and founders who understand the visa-and-relocation calculus from the inside. If you are an angel or an LP, the list flags which diaspora-led names the smartest venture firms have already validated. And if you are a parent in Edison or Fremont wondering whether the path your child is on leads anywhere, the answer on this list is unambiguous.

The competition Forbes describes — submissions doubling in a single year — cuts both ways. It means the bar is brutal. It also means that when six of fifty survivors share your community's roots, the result is no longer luck. It is leverage, compounding."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Ransomware Gang Says It Stole Apple and Tesla Secrets — From a Tata Plant in India.",
        "subheadline": "Tata Electronics confirms a 'cybersecurity incident' as a leak group dumps 200,000 files, in the latest crack to appear in India's bid to become the West's factory floor.",
        "slug": make_slug("tata-electronics-cyber-breach-apple-tesla-secrets-world-leaks-ransomware-cert-in"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs invested in India's manufacturing story — and for engineers building the supply chain that lets Apple make iPhones outside China — a breach at its flagship contract manufacturer is a direct test of whether 'Make in India' can be trusted with the world's most valuable trade secrets.",
        "tags": ["cybersecurity", "tata", "apple", "tesla", "india-manufacturing", "cert-in"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "Reuters - Tata Electronics breach", "url": "https://www.reuters.com/technology/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8720589/pexels-photo-8720589.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Code on a screen during a cybersecurity incident; a leak group dumped files it tied to Tata Electronics",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """Tata Electronics said on Monday it had detected a recent "cybersecurity incident," after researchers reported that a ransomware-style leak group calling itself **World Leaks** had posted what it claimed were component design and specification documents belonging to **Apple and Tesla** — both customers of the Indian conglomerate. Security researchers told Reuters the group dumped more than **200,000 files** on the dark web.

The company's statement was carefully bounded. "A few weeks ago, Tata Electronics identified a cybersecurity incident on some of our systems. Our response protocols were deployed immediately, and the incident has had no impact on our operations across businesses, which remain unaffected," it told Reuters. Apple was investigating, a source said, with a "full analysis" under way; a person familiar with the matter said Tata had received a ransom demand. Apple did not respond to requests for comment, and Tata declined to discuss the ransom.

## Why this lands harder than a typical hack

Tata Electronics is not a peripheral vendor. It has emerged as one of Apple's most important manufacturing partners outside China — the cornerstone of Prime Minister Narendra Modi's drive to turn India into an electronics powerhouse and Apple's chosen hedge against its dependence on Chinese assembly. A great many of the iPhones now sold in the United States are built in India, much of that through Tata and Foxconn.

A breach that allegedly reaches Apple and Tesla design files strikes at the one thing that whole strategy is selling: trust. Multinationals do not move sensitive supply chains to a new country for cheaper labour alone. They move them on the promise that intellectual property will be as safe in Gujarat or Tamil Nadu as it was in Shenzhen.

## A pattern of strain

It is also not the group's first bruise. Tata's British Jaguar Land Rover unit was hit by a cyberattack last year that halted output for six weeks. The electronics arm has separately faced scrutiny over alleged contamination of farmland near one of its iPhone-parts plants. The breach is, as Reuters framed it, the latest setback for Apple's India supply chain at a delicate moment in its build-out.

India's Computer Emergency Response Team, CERT-In, the IT-ministry unit that oversees such incidents, had not responded publicly as of Monday. That silence will be watched closely abroad, because the credibility of India's incident-response apparatus is now part of the pitch.

## What it means for the diaspora

For NRIs, this story sits at an awkward intersection of pride and exposure. The same diaspora that celebrates "Make in India" winning Apple's business has a real stake in whether that win survives contact with adversaries who treat a contract manufacturer's network as a side door into Cupertino's secrets.

The investor angle is concrete. Tata Group entities are widely held, directly and through funds, by overseas Indians betting on the manufacturing thesis. A high-profile IP breach is precisely the kind of event that can slow the diversification of orders into India, or hand ammunition to rivals lobbying to keep production in China or Vietnam.

For the thousands of Indian and Indian-origin engineers building this supply chain, the message is less about blame than about stakes. India has spent years persuading the world that it can be the West's trusted factory floor. Incidents like this one are the bill for that ambition — and how Tata and CERT-In respond will say more about whether the trust holds than any ribbon-cutting at a new fab."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
