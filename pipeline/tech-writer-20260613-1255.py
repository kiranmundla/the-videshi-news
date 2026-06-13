#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-13 batch"""
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

# ── ARTICLE 1 ──────────────────────────────────────────────────────────────────
art1_body = """Iowa's governor fired 200 state IT workers last week and handed their jobs to Cognizant. The layoffs triggered an immediate political brawl over outsourcing, H-1B visas, and what happens when Indian IT services expand into American government infrastructure.

## The Deal

On June 9, Gov. Kim Reynolds announced that Iowa would outsource its entire executive-branch IT operation to two private companies. Amazon Web Services will migrate the state's data from dozens of physical data centers and thousands of servers to a cloud-based system. Cognizant Government Solutions — a subsidiary of the New Jersey-based, Nasdaq-listed IT services giant — will take over daily IT operations: managing servers, networks, systems, and providing technical support to every state agency.

Reynolds framed it as modernisation. "This change is an investment in security, agility, and long-term value for Iowans," she said, claiming the transition will save more than $525 million over the next decade. Her office did not release the contracts, the analyses supporting that number, or any studies about how the change would affect state agency operations.

## Three Days to Decide

The affected workers received termination notices the afternoon of June 9 in a bluntly worded letter from the Department of Management. Hours later, they got an email from Cognizant explaining the company's hiring process and inviting them to sign a contract providing their employment information. The deadline: June 12 — three days after they learned they were losing their jobs. Offer letters with job descriptions, salaries, and benefits would follow between June 15 and 25. Workers have until July 10 to accept.

The union representing affected employees pushed back hard. Danny Copley of the American Federation of State, County and Municipal Employees (AFSCME) said workers are "terrified" about losing their pensions, benefits, and job security. Those hired by Cognizant would be removed from the Iowa Public Employees' Retirement System.

"There's a giant lack of communication and consistency through the state as far as management, and it's ridiculous," Copley told the Des Moines Register.

## The H-1B Flashpoint

The announcement immediately collided with America's most combustible immigration debate. Republican gubernatorial candidate Zach Lahn seized on the deal, criticising the outsourcing of state jobs to a company widely associated with the H-1B visa programme. Responding to a post on X that claimed Cognizant and AWS outsource jobs to a significant number of H-1B workers, Lahn wrote: "Want to be competitive? Hire more Iowans."

Reynolds fired back the same day, insisting that "at no point during our negotiations was it even considered to employ H-1B visa holders." She said the state's daily IT operations would "continue to be supported by Iowans, for Iowans."

## Why NRIs Should Watch This Closely

Cognizant is one of the largest employers of Indian-origin tech professionals in the United States. It employed roughly 72,000 people in India as of 2025 and has historically been among the top H-1B sponsors. When a state governor's IT outsourcing deal triggers a political fight about H-1B visas before the contracts are even public, it signals something larger: the Indian IT services model — reliable, cost-effective, increasingly AI-augmented — is expanding into US government territory, and every step of that expansion will be scrutinised through the lens of immigration politics.

For the roughly 600,000 Indians on H-1B visas and the tens of thousands working for Cognizant, TCS, Infosys, and Wipro across the United States, deals like Iowa's are a double-edged sword. They validate the competence and cost-efficiency of Indian IT services. They also paint a target on the industry every election cycle."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Iowa Fires 200 State IT Workers and Hands the Whole Operation to Cognizant",
    "subheadline": "The $525 million outsourcing deal sends Iowa's servers to Amazon and its help desk to a New Jersey-based Indian IT giant. Workers got three days to sign up with their replacement.",
    "slug": make_slug("iowa-cognizant-state-it-outsourcing-h1b"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Cognizant is one of the largest H-1B sponsors and Indian IT employers in the US — this deal expands Indian IT services into American government infrastructure while fuelling anti-outsourcing sentiment that directly affects NRI tech workers.",
    "tags": ["cognizant", "outsourcing", "h-1b", "indian-it", "iowa", "cloud-migration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Des Moines Register", "url": "https://www.desmoinesregister.com/story/news/politics/2026/06/11/iowa-it-layoffs-cognizant-workers-terrified/"},
        {"name": "Des Moines Register", "url": "https://www.desmoinesregister.com/story/news/politics/2026/06/10/iowa-state-it-workers-cognizant-aws-layoffs/"},
        {"name": "Little Village", "url": "https://littlevillagemag.com/gov-reynolds-outsources-it-services/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Cognizant_Technology_Solution%27s_office_in_Teaneck_%2C_New_Jersey.jpg/1280px-Cognizant_Technology_Solution%27s_office_in_Teaneck_%2C_New_Jersey.jpg",
    "image_caption": "Cognizant Technology Solutions headquarters in Teaneck, New Jersey",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}

# ── ARTICLE 2 ──────────────────────────────────────────────────────────────────
art2_body = """India's Unified Payments Interface now works in nine countries. The latest addition — a direct remittance corridor with Nepal — went live on June 6, and the numbers behind it are quietly extraordinary.

## The Nepal Corridor

India and Nepal have launched a peer-to-peer cross-border remittance link that integrates UPI with Nepal's National Payments Interface (NPI). The system, implemented by NPCI International Payments Ltd (NIPL) and Nepal Clearing House Ltd (NCHL), allows citizens of both countries to send money instantly through mobile banking apps and digital wallets.

Users in India can transfer money to Nepal using the recipient's mobile number or Virtual Payment Address (VPA). Users in Nepal can send funds to India using UPI IDs. No bank account details need to be shared. No currency exchange counters. No waiting.

Nepal is the second country, after Singapore, to achieve full payment-system-level peer-to-peer connectivity with UPI. The corridor is live through select banks: Everest Bank, Global IME Bank, Machhapuchchhre Bank, Nabil Bank, and Nepal SBI Bank on the sending side, with Himalayan Bank, NMB Bank, and Siddhartha Bank enabled for receiving.

## The Scale

The UPI numbers for May 2026 set records again: 23.2 billion transactions worth ₹29.9 trillion ($358 billion). Transaction volume grew 24 per cent year-on-year. Value grew 19 per cent. These are not aspirational targets from a government white paper — they are actual throughput from a single month on a single payment rail.

UPI is now accepted in nine countries: Singapore, the United Arab Emirates, France, Mauritius, Nepal, Bhutan, Qatar, Sri Lanka, and Cambodia. Indian travellers across these markets can pay using their existing UPI apps — Google Pay, PhonePe, Paytm — without converting currency or carrying cash.

## The Architecture of Ambition

The Nepal launch is part of a larger blueprint. The Reserve Bank of India's Utkarsh 2029 plan lays out an aggressive roadmap for UPI internationalisation, CBDC expansion for cross-border payments, and AI-powered financial regulation. The central bank wants international trade to be settled in Indian Rupees, reducing dependence on the US dollar.

NPCI's international arm is quietly building what amounts to a global payment protocol rooted in Indian infrastructure. Every new country added to the UPI network extends India's financial soft power — and creates commercial infrastructure that Indian fintech companies can build on.

## Why This Matters to the Diaspora

For NRIs, the UPI expansion solves a practical problem. Sending money to relatives in Nepal — a corridor used by hundreds of thousands of Indian workers and families — was until recently a process involving bank visits, remittance fees, and multi-day settlement. It now takes seconds on a phone.

But the bigger story is strategic. UPI is India's most successful technology export, and its international expansion is creating a payment ecosystem where Indian emigrants are the default users. Every country added to the UPI network makes it slightly easier to be Indian abroad — and slightly harder for Western payment processors to argue that their own rails are the only viable option for cross-border commerce.

For Indian fintech professionals in the Bay Area and beyond, UPI's global buildout is also a career signal. The infrastructure demands engineers who understand both the NPCI stack and global payment compliance. That intersection of skills is rare, and it is almost entirely populated by people of Indian origin.

PhonePe, Razorpay, and Pine Labs are already building on UPI's international rails. As the protocol reaches more countries, the startups that can bridge Indian payment infrastructure with global commerce will have an outsized opportunity — and the diaspora engineers who understand both worlds will be the ones building it."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "UPI Now Works in Nine Countries. The Transaction Numbers Are Staggering.",
    "subheadline": "A new cross-border corridor with Nepal went live this week. In May alone, India's payment rails processed 23.2 billion transactions worth $358 billion.",
    "slug": make_slug("upi-nepal-corridor-nine-countries-record-transactions"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "UPI's international expansion turns India's payment infrastructure into a global network that NRIs can use abroad — and creates career opportunities for diaspora engineers who understand both Indian and international payment systems.",
    "tags": ["upi", "fintech", "india", "nepal", "digital-payments", "npci", "remittances"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/economy/india-nepal-upi-npi-digital-corridor-remittances/"},
        {"name": "GKToday", "url": "https://www.gktoday.in/upi-npi-corridor-launched-india-nepal-remittances/"},
        {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/law-order/india-nepal-cross-border-upi-remittance/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/money-and-banking/india-nepal-cross-border-remittance-upi-npi/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6289170/pexels-photo-6289170.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Mobile phone-based digital money transfer between two devices",
    "image_attribution": "Pexels",
    "body": art2_body
}

# ── ARTICLE 3 ──────────────────────────────────────────────────────────────────
art3_body = """Microsoft has eliminated between 200 and 400 employees in its Azure cloud research and development division in China. The cuts represent roughly half of Azure's workforce in Beijing and Shanghai. The AI teams in the same cities were not touched.

## What Was Cut — and What Was Not

The layoffs are concentrated in Azure's R&D functions — the engineers who build and maintain Microsoft's cloud infrastructure. Affected employees are eligible for severance packages of up to seven months' pay based on tenure. A subset has been offered relocation to Canada, where Microsoft has significant engineering operations.

Crucially, several China-based divisions were excluded from the cuts: Microsoft's DevDiv developer group, the Microsoft Technology Center Asia, and the company's AI teams in Shanghai and Suzhou. That distinction is the story. Microsoft is not retreating from China wholesale — it is retreating from commoditised cloud R&D while preserving its AI research presence.

A Microsoft spokesperson confirmed the reductions with a statement saying the company "regularly evaluates its business priorities and makes adjustments to align with customer needs." The company declined to elaborate further.

## The Pattern

This is the third time in under two years that Microsoft has made significant workforce reductions in China. The consistency of the pattern — cut infrastructure, keep AI — reveals a structural shift in how Satya Nadella's Microsoft allocates engineering resources globally.

Microsoft is not alone. Meta cut 8,000 employees in May, framing the layoffs as reallocation toward AI. Amazon eliminated 16,000 corporate roles in January. Verizon's CEO told Bloomberg that AI would replace a large share of its customer service workforce. The justification is always the same: the company is not shrinking; it is redirecting capital toward artificial intelligence.

But Microsoft's China cuts add a geopolitical dimension. The US-China tech rivalry has made it increasingly awkward for American companies to maintain large R&D centres in China, particularly in sensitive areas like cloud infrastructure. By concentrating cuts in Azure R&D while preserving AI research, Microsoft is threading a needle: reducing its exposure to geopolitical risk without losing access to China's deep pool of AI talent.

## The India Dimension

While Microsoft cuts in China, the company's operations in India continue to grow. Microsoft's India Development Center in Hyderabad and Bengaluru is one of its largest engineering hubs outside the United States. Nadella — who grew up in Hyderabad before joining Microsoft in 1992 — has consistently expanded the company's Indian footprint, positioning it as a counterweight to both China and the United States in Microsoft's global engineering map.

For Indian engineers at Microsoft, the China cuts reinforce a trend: India's engineering operations are becoming more central to the company's AI strategy, not less. The relocation offers to Canada (rather than India) for affected Chinese employees suggest that Microsoft sees the two talent pools as complementary but distinct — China for AI research, India for product engineering and services, Canada as a neutral ground for sensitive infrastructure work.

## What NRIs Should Take Away

The broader lesson is about where big tech is placing its bets. AI divisions are being protected and expanded. Traditional cloud infrastructure R&D is being compressed. The engineers who are safe are the ones working on AI — and Indian engineers, who are disproportionately represented in big tech's AI and cloud product teams, are well positioned for now.

But "for now" carries a caveat. Microsoft's Azure layoffs in China are a preview of what happens when AI productivity gains reach the point where even R&D headcount can be reduced. Indian engineering centres — with their cost advantages and deep talent pools — will likely be among the last to face this compression. They will not be immune to it forever."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Microsoft Cuts Half Its Azure Team in China. The AI Engineers Were Spared.",
    "subheadline": "Between 200 and 400 employees in Azure cloud R&D are being eliminated in Beijing and Shanghai. Some were offered relocation to Canada. The AI units were left untouched.",
    "slug": make_slug("microsoft-azure-china-layoffs-ai-teams-spared"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Microsoft's India engineering centres are growing while China shrinks — Indian engineers in big tech's AI divisions are well positioned as companies restructure globally around AI.",
    "tags": ["microsoft", "azure", "china", "layoffs", "ai", "satya-nadella", "india-tech"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "TheStreet", "url": "https://www.thestreet.com/technology/microsoft-ceo-sends-another-shocking-message-to-employees"},
        {"name": "Digitimes", "url": "https://www.digitimes.com/news/microsoft-azure-china-layoffs/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
    "image_caption": "Satya Nadella, CEO of Microsoft",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body
}

# ── INSERT ─────────────────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
