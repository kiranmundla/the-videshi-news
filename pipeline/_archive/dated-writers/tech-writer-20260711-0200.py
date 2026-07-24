#!/usr/bin/env python3
"""Tech writer — 2026-07-11 02:00 PDT run"""
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
    # ─── Article 1: Fed Task Force Indian-Origin Leaders ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Three Indian-Origin Leaders Will Now Help Reshape the Federal Reserve. One of Them Ran India's Central Bank.",
        "subheadline": "Raghuram Rajan, Raj Chetty, and Xbox CEO Asha Sharma have been named to lead three of five task forces reviewing how the world's most powerful central bank operates.",
        "slug": make_slug("rajan-chetty-sharma-fed-task-force-indian-origin"),
        "category": "technology",
        "vertical": "tech-policy",
        "diaspora_angle": "Three Indian Americans now sit at the table where US monetary policy is being redesigned — from balance sheet strategy to AI's impact on jobs — a historic concentration of diaspora influence at the Fed.",
        "tags": ["raghuram-rajan", "raj-chetty", "asha-sharma", "federal-reserve", "indian-diaspora", "ai-policy", "economics"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/finance/feds-warsh-taps-broad-group-central-bank-outsiders-oversee-review-2026-07-10/"},
            {"name": "Investopedia", "url": "https://www.investopedia.com/fed-chair-kevin-warsh-names-members-of-reform-task-force-11754082"},
            {"name": "CNN", "url": "https://www.cnn.com/2026/07/10/economy/fed-warsh-task-force-members/index.html"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/warsh-taps-fed-task-force-chiefs-theyre-global-bankers-business-leaders-and-academics-5bbb10e5"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/raghuram-rajan-xboxs-asha-sharma-roped-in-to-review-policies-of-us-fed-1752206460"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Raghuram_Rajan%2C_IMF_69MS040421048l.jpg/330px-Raghuram_Rajan%2C_IMF_69MS040421048l.jpg",
        "image_caption": "Raghuram Rajan, former Reserve Bank of India governor, now leads a Federal Reserve balance sheet policy task force",
        "image_attribution": "Wikimedia Commons",
        "body": """When Federal Reserve Chairman Kevin Warsh unveiled the leaders of his five new policy task forces on Thursday, the roster read like a who's who of Indian-origin intellectual firepower.

**Raghuram Rajan**, the former Reserve Bank of India governor and University of Chicago finance professor who famously predicted the 2008 financial crisis at Jackson Hole in 2005, will co-lead the balance sheet policy task force. His group will examine the costs, benefits, and institutional implications of the Fed's $6.7 trillion balance sheet — the mountain of Treasuries and mortgage-backed securities accumulated during the Great Financial Crisis and the pandemic. Rajan's co-leads are Harvard economists Karen Dynan and Jeremy Stein, a former Fed governor.

**Raj Chetty**, the Harvard economist widely regarded as one of the most influential social scientists of his generation, will co-lead the data task force alongside former Walmart CEO Doug McMillon and University of Chicago economist Kevin Murphy. Chetty's team is charged with improving "the quality and timeliness of real economic signals" that inform Fed policy — a mandate tailor-made for a researcher who pioneered the use of real-time tax and credit card data to track household well-being at granular levels.

**Asha Sharma**, the Indian-American Xbox CEO who has dominated headlines this week for laying off 1,600 workers at Microsoft's gaming division, rounds out the Indian-origin trio. She will co-lead the productivity and jobs task force with Andreessen Horowitz co-founder Marc Andreessen and Stanford economist Charles I. Jones, who is currently on leave at Anthropic. Their remit: assess the economic impact of artificial intelligence and other general-purpose technologies on the labour market.

## Why Three Task Forces, Not One

Warsh, who took over the Fed chairmanship in June, announced the task force initiative at his first press conference. He has signalled that he wants to fundamentally rethink how the central bank operates — from how it measures inflation to what it does with its balance sheet to whether AI will prove deflationary in the long run.

"The U.S. economy has changed significantly over the last generation, and never more so than right now," Warsh said in a statement. "Each task force will carefully consider whether policymakers' means and methods, analytical tools and policy approaches can be improved upon."

The remaining two task forces cover inflation frameworks, led by Harvard's Greg Mankiw and Nobel laureate Thomas Sargent, and communications, led by former Bank of England governor Mervyn King. All five panels will operate independently and are expected to deliver their findings by the end of 2026.

## The Diaspora Dimension

The concentration of Indian-origin leaders at the highest levels of US economic policymaking is historically unprecedented. Rajan, who served as the IMF's chief economist before returning to India to run the RBI from 2013 to 2016, brings a rare dual perspective: he has operated central bank machinery from the inside on two continents. French President Emmanuel Macron noted in February that "the CEO of Alphabet is Indian, the CEO of Microsoft is Indian, the CEO of IBM is Indian" — but the Fed appointments mark a new frontier beyond corporate boardrooms.

Chetty, born in New Delhi and raised in the United States, has reshaped how economists think about social mobility using massive datasets. His work on the "Opportunity Atlas" — a neighbourhood-by-neighbourhood map of economic mobility in America — has already influenced housing and education policy.

The appointments arrive at a fraught moment for Sharma specifically. Her Xbox restructuring this week drew both professional scrutiny and racist attacks online, with some critics baselessly linking her Indian heritage to the company's hiring of H-1B visa workers. Her Fed role — advising on whether AI creates or destroys jobs — adds an ironic layer to the controversy.

## What It Means for Indian Americans

For the Indian-American professional class, the appointments are a signal that diaspora expertise is being sought at the highest levels of US institutional life — not just in running tech companies, but in redesigning the monetary architecture that governs the world's largest economy. Whether these task forces produce incremental tweaks or structural overhauls, the intellectual direction of American economic policy now runs, in part, through New Delhi, Chennai, and the corridors of IIT and IIM alumni networks.

The task forces will also shape how the Fed thinks about AI — a question that touches every Indian engineer, data scientist, and IT services worker in America. If Warsh's panel concludes that AI is structurally deflationary, it could influence rate-cutting cycles. If it finds AI primarily displaces workers in the near term, the policy response could look very different."""
    },

    # ─── Article 2: Dixon-Vivo JV Approved ───
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Cleared a Chinese Smartphone Giant to Build Phones Under Indian Ownership. It Took 18 Months.",
        "subheadline": "Dixon Technologies will hold 51 per cent of a new joint venture with Vivo, the first major China-India manufacturing partnership approved since the border standoff reshaped investment rules.",
        "slug": make_slug("dixon-vivo-jv-approved-smartphone-india-china"),
        "category": "technology",
        "vertical": "tech-manufacturing",
        "diaspora_angle": "The approval reshapes the India-China tech manufacturing relationship that NRIs and Indian investors have watched warily since 2020 — and positions Dixon as a potential portfolio play for diaspora investors betting on Make in India electronics.",
        "tags": ["dixon-technologies", "vivo", "make-in-india", "smartphone-manufacturing", "india-china", "electronics"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/india-clears-dixon-vivo-jv-domestic-smartphone-manufacturing-2026-07-10/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/dixon-technologies-and-vivo-receive-approval-for-smartphone-manufacturing-joint-venture-in-india/article69794231.ece"},
            {"name": "LiveMint", "url": "https://www.livemint.com/companies/news/dixon-technologies-pins-fy27-growth-hopes-on-vivo-jv-approval-steady-mobile-demand-11747065752741.html"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5554948/pexels-photo-5554948.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "An electronics assembly line — Dixon Technologies will now manufacture smartphones for Vivo under Indian majority ownership",
        "image_attribution": "Pexels",
        "body": """For eighteen months, the Dixon-Vivo joint venture sat in regulatory purgatory. On Thursday, India finally said yes.

Dixon Technologies, India's largest publicly listed electronics manufacturer, announced that the government has approved its joint venture with Chinese smartphone maker Vivo Mobile. The partnership — 51 per cent Dixon, 49 per cent Vivo — will manufacture smartphones and other electronic devices in India, taking over a substantial chunk of Vivo's production orders on the subcontinent.

The approval is significant not because a factory will open, but because of the wall it had to climb through.

## Press Note 3: The China Filter

In April 2020, as Indian and Chinese soldiers squared off in Ladakh, the Modi government introduced Press Note 3 — a regulation requiring senior-level government clearance for any direct investment from countries sharing a land border with India. The rule was aimed squarely at China. It froze billions of dollars in planned Chinese investment and forced companies like Vivo, Xiaomi, and Oppo to rethink their India strategies.

The Dixon-Vivo deal, signed in December 2024, triggered the full weight of this scrutiny. An inter-ministerial panel weighed the geopolitical implications for more than a year before granting approval. The structure itself tells the story: Dixon holds the majority stake, ensuring operational control remains with an Indian company.

"The government amended Press Note 3 in March to allow Chinese entities to invest up to 10 per cent in a non-controlling stake," noted LiveMint, "but the Dixon-Vivo deal still required specific approval given Vivo's 49 per cent share."

## The Numbers Behind the Deal

The commercial logic is straightforward. Vivo sold an estimated 35 million handsets in India in FY2025, while Dixon's mobile phone manufacturing volume stood at around 32 million units. The JV is expected to handle roughly 67 per cent of Vivo's production volumes — translating to 20-22 million units annually.

For Dixon, this could be transformative. Analysts at The Hindu BusinessLine estimate the venture could generate ₹30,000 crore (approximately $3.15 billion) in annual revenue at peak capacity. Dixon's stock has already been on a tear, with brokers initiating coverage at a Buy rating and a target price of ₹16,608, roughly 23 per cent above its current trading level.

Vivo's manufacturing unit in Noida is expected to become part of the JV, and the venture will also be able to manufacture electronic products for other brands — effectively turning Dixon into a multi-brand contract manufacturer with Chinese technology partnerships and Indian ownership.

## What This Means for NRIs

For Indian Americans tracking the Make in India electronics story, the approval signals a pragmatic thaw in the India-China tech cold war. New Delhi has concluded that blocking all Chinese capital is less useful than channelling it through Indian-majority structures. It is a model that could be replicated: Chinese technology and volume, Indian ownership and control, government oversight as the glue.

Dixon Technologies has become the stock market proxy for this bet. The company's revenue crossed ₹48,873 crore in FY2026, with the mobile phone and contract manufacturing business contributing ₹44,257 crore. Its expansion into specialty verticals — aerospace, automotive, defence, and medical electronics — gives it diversification that pure-play smartphone manufacturers lack.

For NRI investors, the risk calculus is clear. The upside is a company positioned at the centre of India's electronics manufacturing ambitions, backed by government policy and expanding partnerships. The downside is geopolitical: any deterioration in India-China relations could freeze the JV's operations or trigger regulatory review. The 51-49 structure is designed to insulate against exactly this, but geopolitics rarely respects corporate governance charts.

## The Bigger Picture

India's smartphone market remains the second-largest in the world, and domesticating its manufacturing has been a stated government priority since the Production-Linked Incentive scheme launched in 2020. Apple, Samsung, and now Vivo are all manufacturing in India — but with different ownership structures and varying degrees of "Indian-ness."

The Dixon-Vivo approval may be remembered as the template: how India learned to take Chinese money without ceding control. Whether the template holds through the next border skirmish is another question entirely."""
    },

    # ─── Article 3: Google Picks 20 AI Startups + BAT VC $100M India Fund ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Google Just Picked 20 Indian AI Startups for Its Accelerator. A New York VC Dropped $100 Million to Bet on More.",
        "subheadline": "From healthcare to climate tech, India's AI startup pipeline is attracting institutional backing from both Silicon Valley and the Indian-American investor class — with agentic AI and physical AI systems leading the new wave.",
        "slug": make_slug("google-accelerator-india-ai-bat-vc-100m-fund"),
        "category": "technology",
        "vertical": "tech-startups",
        "diaspora_angle": "Indian-American VCs and tech executives are increasingly channelling capital back into India's AI ecosystem — and Google's accelerator pipeline offers NRI founders a structured path to scale globally.",
        "tags": ["google", "ai-startups", "india", "venture-capital", "bat-vc", "agentic-ai", "deep-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Nation Press", "url": "https://nationpress.com/google-picks-20-ai-first-indian-startups-for-accelerator-india-2026/"},
            {"name": "The Indian EYE", "url": "https://theindianeye.com/bat-vc-enters-india-with-100-million-ai-focused-fund/"},
            {"name": "Google for Startups", "url": "https://startup.google.com/programs/accelerator/india/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17483871/pexels-photo-17483871.png?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "An artificial intelligence neural network visualization — India's AI startup ecosystem is attracting accelerator and venture capital attention",
        "image_attribution": "Pexels / Google DeepMind",
        "body": """Two announcements this week tell you everything about where India's AI startup ecosystem stands: Google chose 20 Indian startups for its accelerator programme, and a New York venture capital firm showed up with $100 million to find more.

## Google's 2026 India Cohort

On Wednesday, Google announced the 2026 cohort of its Google for Startups Accelerator: India programme, selecting 20 AI-first startups from nearly 2,500 applications. The announcement coincided with the tenth anniversary of Google's accelerator initiatives in India — a decade that has tracked the country's evolution from an outsourcing hub to a genuine AI production centre.

What is striking about this year's cohort is what it is *not* building. The large language model wrapper era — where startups layered a thin interface on top of OpenAI or Anthropic APIs — appears to be fading. Google described the selected startups as focused on "agentic AI and multimodal AI systems capable of operating in physical environments and enterprise workflows." The sectors span healthcare, climate technology, finance, legal services, manufacturing, cybersecurity, and developer tools.

"India's startup ecosystem is moving into a new frontier of agentic workflows and physical AI systems engineered to solve high-stakes, real-world challenges," said Preeti Lobana, Vice President and Country Manager of Google India.

Each startup gains access to Google's AI technology stack, technical mentorship, and go-to-market support. For Indian founders, the programme offers something money alone cannot buy: structured access to Google's infrastructure, engineering talent, and global distribution channels.

## BAT VC's $100 Million India Bet

Separately, BAT VC, a New York-based venture capital firm, announced its formal entry into India with plans to invest up to $100 million through its second fund. The fund targets India-linked startups in AI, deep tech, fintech, and B2B SaaS — essentially the same categories that dominate Google's accelerator.

The firm's India initiative is led by three Indian-American general partners whose careers span the US-India tech corridor. Manish Maheshwari, the former head of Twitter India and a Harvard Mason Fellow, has relocated to Bengaluru to lead operations. Aditya Mishra, who built and sold FaceLogique and held executive roles at Yahoo and Accenture, brings enterprise AI experience. Ravi Metta, former CTO at Finastra and a product engineering leader at Intuit, rounds out the team.

"My move to Bengaluru underscores our conviction in India's potential to lead the next wave of AI-driven global growth," Maheshwari said.

The timing is not accidental. India's AI sector is growing at 32 per cent annually and is projected to reach $23 billion by 2027. The country now has over 450,000 AI and ML professionals. US-India cross-border AI investments grew 180 per cent to $4.7 billion in 2023, and the trajectory has only steepened since.

## The Diaspora Capital Loop

What connects these two announcements is the feedback loop between Indian-American capital, Silicon Valley infrastructure, and Indian engineering talent. Google's accelerator filters the best startups; firms like BAT VC provide growth capital; and Indian-American executives who have worked at Twitter, Google, Meta, and Intuit bring the operational playbook for scaling globally.

This is not philanthropy or nostalgia. India's enterprise SaaS market has surged to $8.7 billion, growing at a 35 per cent compound annual rate — twice the global average. BAT VC's first fund produced exits including Wand AI and Accern, both AI companies with India-US dual operations.

For NRI founders and investors, the landscape has shifted meaningfully. A decade ago, building an AI company in India meant convincing sceptical Western investors that India could produce more than outsourced code. Today, Google is actively selecting Indian AI startups for its own accelerator, and diaspora VCs are relocating to Bengaluru to be closer to deal flow.

## What to Watch

The 20 startups in Google's cohort have not been individually named yet, but the selection criteria — agentic AI, physical AI, enterprise workflows — suggest companies building autonomous systems for manufacturing floors, hospital diagnostics, agricultural monitoring, and legal document processing. These are not chatbot wrappers. They are the infrastructure layer of India's AI economy.

BAT VC's fund, meanwhile, will compete for deals alongside established India-focused firms like Peak XV Partners (formerly Sequoia India), Accel, and Lightspeed. The firm's differentiator is its US-India dual lens: partners who have lived and worked on both sides of the Pacific, investing in companies designed to serve both markets from day one.

If India's AI startup pipeline produces even a handful of global-scale companies over the next five years, these early institutional bets — from Google and the diaspora investor class alike — will look prescient."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
