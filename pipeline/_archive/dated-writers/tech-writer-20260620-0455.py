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
        "headline": "Nikesh Arora Is Buying the Whole Security Stack. The Bill Is Already Past $28 Billion.",
        "subheadline": "Palo Alto Networks just closed its $3.3 billion Chronosphere deal weeks after swallowing CyberArk for $25 billion. For the Indians who fill its engineering ranks, the consolidation is the career.",
        "slug": make_slug("nikesh-arora-palo-alto-chronosphere-cyberark-agentic-security-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Palo Alto Networks, run by Indian-origin CEO Nikesh Arora, is consolidating the cybersecurity industry around AI agents — reshaping the job market for the thousands of Indian engineers who staff security teams in Santa Clara, Bengaluru and beyond.",
        "tags": ["nikesh-arora", "palo-alto-networks", "cybersecurity", "ai-agents", "indian-tech", "silicon-valley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CRN", "url": "https://www.crn.com/news/security/2026/palo-alto-networks-completes-3-3b-acquisition-of-chronosphere-for-ai-observability-push"},
            {"name": "Palo Alto Networks", "url": "https://www.paloaltonetworks.com/company/press/2026"},
            {"name": "StockTitan", "url": "https://www.stocktitan.net/news/PANW/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg/330px-Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "image_caption": "Palo Alto Networks chairman and CEO Nikesh Arora speaking at TechCrunch Disrupt",
        "image_attribution": "Wikimedia Commons",
        "body": """Palo Alto Networks has finished buying Chronosphere, a $3.3 billion deal for an observability company most people outside the data centre have never heard of. It is the smaller of two purchases the cybersecurity giant has digested in a matter of weeks. The larger one — the $25 billion acquisition of identity firm CyberArk — closed earlier this year. Add the two and Nikesh Arora, the company's chairman and chief executive, has spent more than $28 billion reshaping what his company sells.

The logic is not subtle, and Arora has stopped pretending it is. "The AI cycle is moving fast," he told analysts when the Chronosphere deal was first announced. Translation: the window to own the plumbing of AI security is open now, and it will not stay open. So he is buying his way to the front of the line rather than building.

### What he is actually assembling

Strip away the brand names and a pattern emerges. CyberArk secures identities — the credentials that let a human, a machine, or now an AI agent do things inside a corporate network. Chronosphere watches the system and tells you when something is going wrong. Palo Alto's own Cortex platform, rebranded AgentiX, is meant to be the brain that ties it together: detect a problem, investigate the root cause, and fix it automatically, without a human in the loop.

That last phrase is the whole strategy. Arora is betting that the next wave of cyberattacks will be fought by software agents on both sides, and that enterprises will pay a premium to buy the defence as one package rather than stitching together a dozen vendors. He calls it the end of "identity silos." Wall Street, which has pushed the stock toward record highs, calls it a moat.

### Why an Indian engineer should read past the deal

For the tens of thousands of Indian-origin engineers who work in cybersecurity — at Palo Alto itself, at the firms it is absorbing, and at the customers buying its tools — this consolidation is not abstract. It is the shape of the job market for the next five years.

Two things follow from a company buying $28 billion of capability in a year. First, the centre of gravity in security work is shifting from people who configure firewalls and write detection rules to people who build and supervise the agents that do that work automatically. That is good news for the machine-learning engineer and bad news for the analyst whose entire day is triaging alerts. Indian professionals are heavily represented in both camps, and the gap between them is about to widen.

Second, Palo Alto's Bengaluru and India operations sit squarely inside this machine. Companies that go on acquisition sprees tend to consolidate engineering, and India is where a lot of the cost-effective depth lives. The same Global Capability Centre trend pulling US firms to set up shop in Bengaluru "for the talent, not the discount" applies here: a security giant with an agentic roadmap needs more researchers, not fewer, and India is one of the few places it can hire them at scale.

### The CyberArk wrinkle

There is a geopolitical footnote that diaspora investors should not miss. As part of the CyberArk deal, Palo Alto said it intends to pursue a secondary listing on the Tel Aviv Stock Exchange under the ticker "CYBR," a nod to CyberArk's Israeli roots. For an NRI building a tech-heavy portfolio, it is a reminder that the company is now a genuinely global security conglomerate, with engineering centres spread across the US, Israel and India, and exposure to all three.

The risk in Arora's plan is the oldest one in deal-making: integration. Buying observability, identity and a security platform is easy on a slide. Making them behave as one product — and convincing customers to rip out incumbents to get it — is the hard part. Insiders have been selling stock even as Arora himself bought $10 million more in March, a split signal that captures the uncertainty.

What is not uncertain is the direction. An Indian-origin executive is now the most aggressive consolidator in cybersecurity, building the security layer for an AI era that will be defended, and attacked, by software. For the diaspora that staffs the industry, the question is no longer whether the agents are coming. It is which side of the agent you will be paid to build."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Qualcomm Is Reportedly Spending $10 Billion to Finally Crash Nvidia's Party",
        "subheadline": "The Snapdragon maker is in talks to buy AI-chip startup Tenstorrent days before an investor day where it will lay out a data-centre plan. For the Indian engineers who power Qualcomm, the pivot is personal.",
        "slug": make_slug("qualcomm-tenstorrent-ai-chip-data-center-pivot-jim-keller-indian-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Qualcomm employs thousands of Indian engineers across Hyderabad, Bengaluru and San Diego; its bet to leap from phone chips into AI data-centre silicon decides what those engineers build next — and whether India's chip-design talent gets a seat at the AI hardware table.",
        "tags": ["qualcomm", "tenstorrent", "ai-chips", "semiconductors", "nvidia", "indian-engineers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/qualcomm-talks-buy-tenstorrent-information-reports-2026-06-15/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/qualcomm-stock-ai-chip-data-center"},
            {"name": "The Information", "url": "https://www.theinformation.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/34924856/pexels-photo-34924856.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Close-up of a computer circuit board showing electronic components",
        "image_attribution": "Pexels",
        "body": """Qualcomm has spent two decades being extraordinarily good at one thing: the chips inside your phone. Snapdragon processors and 5G modems run a huge share of the world's Android handsets, and even Apple has leaned on Qualcomm modems. It is a strong, profitable, and — investors increasingly worry — boring business.

So the company is trying something it has never really pulled off. According to The Information, Qualcomm is in talks to buy Tenstorrent, a private AI-chip startup, for between $8 billion and $10 billion. The deal is not signed. But the timing tells you everything: Qualcomm's investor day lands on June 24, and management is expected to unveil a data-centre chip strategy, name a major customer, and put real revenue numbers behind its AI ambitions. The stock has already jumped more than 6% on the speculation and is up roughly 68% over three months.

### Why buy instead of build

Being the best at mobile silicon does not make you competitive in the data centre. That market — training and running large AI models — belongs to Nvidia, with AMD pushing for scraps. Qualcomm barely registers. The engineering challenges, the customers, and the competitive landscape are all different.

Tenstorrent is a shortcut to relevance, and it comes in two parts. The first is technology: Tenstorrent builds flexible AI chips around RISC-V, an open chip-design standard that lets customers avoid being locked into proprietary architectures. As AI workloads get more specialised, off-the-shelf designs fit worse, and that openness is suddenly valuable.

The second part is a person. Tenstorrent's CEO is Jim Keller, the legendary engineer who has shaped chip designs at AMD, Apple, Tesla and Intel. A $10 billion price tag for a pre-revenue-scale startup is, in large part, a bet on Keller and the team he has assembled. As one analysis put it, for Qualcomm the people and the intellectual property may matter as much as the products.

### The Indian angle runs deep

Qualcomm is not a peripheral employer of Indian talent — it is one of the most important. The company runs large engineering operations in Hyderabad and Bengaluru, and Indian engineers are woven through its design teams in San Diego. When Qualcomm decides where to point its R&D, it is also deciding what a meaningful slice of India's chip-design workforce will spend the next decade building.

For years that meant modems and mobile SoCs — important, lucrative, but mature. A pivot into AI data-centre silicon changes the assignment. It means more work on high-performance compute, networking, and the messy thermal and power problems that come with cramming AI accelerators into racks. For an Indian engineer weighing whether to stay in mobile or chase the AI hardware wave, Qualcomm's bet decides whether they can do both inside the same company.

There is a national dimension too. India's own semiconductor push is overwhelmingly about design talent rather than fabrication — the country has the engineers but not yet the leading-edge fabs. A US chip giant building a serious AI-silicon business, staffed in part from India, is exactly the kind of pipeline that lets Indian designers work on frontier hardware without leaving the industry. RISC-V, the open standard at Tenstorrent's core, is also a favourite of Indian academic and startup chip efforts, from IIT-Madras's Shakti processors onward. A Qualcomm-Tenstorrent tie-up would put serious money and scale behind an architecture the Indian ecosystem has already bet on.

### The caution

Wall Street is excited but not convinced. J.P. Morgan has Qualcomm on "Positive Catalyst Watch" yet stays neutral, "awaiting evidence of execution." That hedge is the whole story. Qualcomm has talked about diversifying beyond phones for years; automotive and IoT have grown, but the data-centre dream has stayed a dream. Buying Keller's team and Tenstorrent's IP is a credible move, not a guaranteed one. Integration is hard, and Nvidia is not standing still.

For the diaspora watching from a Qualcomm cubicle or an NRI brokerage account, June 24 is the date that matters. If the investor day delivers a named hyperscaler customer and real revenue targets, the pivot becomes plausible. If it is more vision than numbers, the 68% run-up starts to look like a story the market told itself. Either way, the engineers building it will speak with more than a few Indian accents."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Chip Bet Has a Quiet Winner: A Bengaluru Startup Making the 'Power Brain' for AI Data Centres",
        "subheadline": "Peak XV just led a $15 million round into C2i, which builds the power-delivery silicon that keeps GPUs alive. It is the part of India's semiconductor story that doesn't need a billion-dollar fab.",
        "slug": make_slug("c2i-peak-xv-power-chip-india-semiconductor-design-ai-data-center-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "India's semiconductor mission is mostly about design IP, not fabs — and design-led startups like C2i are where NRI investors and returning engineers can actually get exposure to the chip story without waiting a decade for a factory.",
        "tags": ["india-semiconductors", "c2i", "peak-xv", "deep-tech", "ai-data-centers", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Press Information Bureau", "url": "https://pib.gov.in/PressReleasePage.aspx"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/indian-semiconductor-startups-chip-story-france"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/india-semiconductor-design-startups-2026/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6636497/pexels-photo-6636497.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Macro shot of a circuit board highlighting electronic components",
        "image_attribution": "Pexels",
        "body": """When Indians talk about the country's chip ambitions, the conversation usually turns to fabs: the Tata Electronics plant in Dholera, Micron's assembly site in Gujarat, the multi-billion-dollar factories meant to end India's reliance on Taiwan. Those projects are real, expensive, and years from maturity. They are also not where the most interesting early returns are showing up.

The quieter story is design. And one of its clearest examples just raised money. C2i, a Bengaluru deep-tech startup, has closed a $15 million round led by Peak XV Partners (the firm formerly known as Sequoia Capital India). It follows an earlier $4 million round led by Yali Capital, taking the company's total to roughly ₹170 crore, plus support under the government's Design Linked Incentive scheme.

### What C2i actually makes

C2i does not build the flashy AI accelerators that grab headlines. It builds the power-delivery system that keeps them running. In the company's own framing, it makes an "intelligent power brain" for data centres — system-level silicon that manages how electricity is delivered to high-performance AI hardware so that it runs reliably and efficiently around the clock.

This is unglamorous and enormously important. Modern AI racks burn through staggering amounts of power, and a meaningful share of that energy is lost or mismanaged before it reaches the chips. Peak XV's Rajan Anandan, who led the deal, said C2i's approach can extend GPU lifespan and unlock "billions of dollars in industry savings." The company expects its first silicon back from fabrication by mid-year and will then validate performance.

It is, in other words, exactly the kind of bet that fits India's actual strengths: deep engineering, IP creation, and a problem the whole AI industry has, rather than a commodity nobody needs.

### Why the diaspora should care about a power chip

For NRIs, C2i is less a stock tip — it is private and early — than a signal about where Indian chip money is flowing and how to read it.

The first lesson is that India's semiconductor opportunity is bifurcated. Fabs are a generational, capital-crushing project best left to governments and giants. Design is fast, capital-light, and already producing companies that ship. The trio of Indian chip startups that recently pitched in France — VerveSemi in analogue, AGNIT in gallium nitride, Netrasemi in edge-AI SoCs — make the same point. India is competitive in design today, in ways it will not be in leading-edge manufacturing for years. An NRI investor trying to "play the India chip story" should understand which half they are actually buying.

The second lesson is about who is funding it. Peak XV, Khosla Ventures, Bessemer and a clutch of domestic funds are now writing cheques to Indian deep-tech, and Zoho's Sridhar Vembu has personally backed several chip startups. This is patient, technical capital — the kind that did not exist in Indian venture a decade ago, when money chased food delivery and e-commerce. For diaspora professionals thinking about angel investing or joining a startup back home, deep tech is no longer a place you go to die for lack of funding.

The third lesson is personal. Companies like C2i are precisely the landing spots for the "ghar wapsi" engineer — the Indian who spent a decade at Nvidia, AMD or Intel and now wants to build hardware at home without taking a vow of poverty. Design-led startups can pay for senior chip talent in a way fabs and pure-research labs cannot, because the path to revenue is shorter. The returning power-electronics architect from San Jose is the ideal C2i hire.

### The reality check

None of this means India has cracked silicon. C2i still has to get working chips back from the foundry — almost certainly a Taiwanese one — and prove they perform. The fabrication that India lacks is still the fabrication these startups depend on. And $15 million, while real, is a rounding error next to what Nvidia spends in a weekend.

But that is the point of the design-first path: you do not need to win the fab war to build a valuable chip company. You need a hard problem, good engineers, and customers who will pay to solve it. AI data centres have handed India all three. For the diaspora, C2i is a small deal with a large message — the part of India's chip dream that is working right now is the part built on brains, not buildings."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
