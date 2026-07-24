#!/usr/bin/env python3
"""Tech writer run — 2026-06-29 05:00 PDT"""

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


# ── Article 1: Google Gemini 3 + India Safety Push ──────────────────────

art1_body = """Google has unveiled Gemini 3, the most powerful model in its rapidly expanding AI arsenal, and paired the launch with a pointed message: India is where the rules get written.

The model, which Google describes as a "massive jump in reasoning," arrived the same week Alphabet shed roughly $225 billion in market capitalisation after two marquee AI researchers — Noam Shazeer, co-author of the foundational Transformer paper, and Nobel laureate John Jumper of AlphaFold fame — decamped for OpenAI and Anthropic respectively. The timing was either heroically bold or desperately needed, depending on your read of Sundar Pichai's week.

## What Gemini 3 Actually Does

Gemini 3 is Google's answer to the question every AI lab is racing to crack: sustained, multi-step reasoning. A research variant, Gemini 3 Deep Think, routes complex queries through an extended chain-of-thought process before responding — functionally similar to what OpenAI and Anthropic have done with their own reasoning modes, but running atop Google's proprietary infrastructure.

The numbers are large. Google says the Gemini ecosystem now serves over 650 million monthly active users and 13 million developers. Google Cloud pulled in $20 billion last quarter, though Pichai conceded that compute constraints had suppressed even stronger growth. The cloud backlog nearly doubled quarter on quarter — a waiting list, not a win.

Alongside Gemini 3, Google introduced Antigravity, a next-generation coding interface powered by the model. It offers agent-based, multi-pane development — a shot across the bow of emerging AI-native IDEs like Cursor and Windsurf, and a bet that developers will trust Google's model to write their code.

## India Gets the Safety Pitch

The more strategic play was the India-specific safety announcement. Ahead of New Delhi hosting the AI Impact Summit 2026 — the first Global AI Summit held in the Global South — Google outlined a suite of safety, security, and inclusion initiatives aimed squarely at India's most pressing digital threats.

The focus is practical: digital arrest scams, voice cloning abuse, and the increasingly sophisticated fraud networks that prey on India's 800-million-strong internet user base. Google says it is deploying Gemini-powered detection tools across its Indian products, with a particular emphasis on protecting vulnerable users who may be less equipped to distinguish a deepfake from the real thing.

"It's responding with a level of depth and nuance we haven't seen before," said Tulsee Doshi, head of product for the Gemini programme, describing the model's safety capabilities.

## The Diaspora Angle

For the roughly five million Indian Americans who live between two digital ecosystems, Gemini 3 matters on both sides. Professionally, many work at or compete with the companies building these models — Google, Meta, Microsoft, Anthropic, OpenAI. The brain drain that cost Alphabet $225 billion this week was, in part, a story about Indian-origin researchers moving between labs.

Personally, the safety initiatives touch a nerve. NRIs with elderly parents in India have watched digital fraud become a daily hazard. The RBI reported a 700 per cent increase in AI-enabled financial fraud complaints between 2023 and 2025. Google positioning itself as a safety partner to the Indian government, ahead of a summit that India is hosting, is a bid for regulatory goodwill as much as consumer trust.

## What Comes Next

Gemini 3 Deep Think will roll out to AI Ultra subscribers in coming weeks after additional safety testing. Google also previewed Gemini 3.5 Flash and Gemini Omni, a multi-modal system designed for extreme speed and low latency, for later in the year.

The model launches into a market that is not waiting. Anthropic's restricted-release Fable 5 leads on software engineering benchmarks. OpenAI's GPT-5.1 landed days earlier. And Google is now doing this with a thinner bench, having lost two of the people who built the architecture underpinning everything.

Pichai's bet is that the model — and India — will speak louder than the departures."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Google Launched Its Best AI Model the Same Week It Lost Two of Its Best Researchers. Then It Went to India.",
    "subheadline": "Gemini 3 debuts with a massive reasoning upgrade and a pointed message: New Delhi will help write the rules for AI safety.",
    "slug": make_slug("google-gemini-3-india-ai-safety-summit-pichai"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian Americans work at and compete with the labs building these models; India-specific safety tools address digital fraud targeting NRI families back home.",
    "tags": ["google", "gemini", "ai", "sundar-pichai", "india-ai-summit", "ai-safety"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian EYE", "url": "https://theindianeye.com"},
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Google Cloud UK Summit / Verdict", "url": "https://www.verdict.co.uk"},
        {"name": "LinkedIn / Weekly AI Blast", "url": "https://www.linkedin.com"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
    "image_caption": "Sundar Pichai, CEO of Alphabet and Google, at a corporate event in 2023",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}


# ── Article 2: RBI AI Kill Switch ───────────────────────────────────────

art2_body = """India's central bank wants a kill switch on every AI system that touches your money.

The Reserve Bank of India last week published draft guidelines titled "Guidance on Regulatory Principles for Model Risk Management, 2026" — a dry name for what may be the most comprehensive AI governance framework any financial regulator has proposed anywhere. The rules would require every bank and regulated financial institution in India to build the ability to instantly override, suspend, or deactivate any AI system in use. The RBI is calling it a "kill switch arrangement," and it is not optional.

## What the Guidelines Demand

The framework is sweeping. Banks will need to maintain a complete inventory of every AI and machine-learning model in use, whether built in-house or purchased from third-party vendors. Each model must undergo independent validation. Board-level oversight is mandatory — not as a rubber stamp, but as active governance with a risk management committee receiving regular reports.

The most striking provisions target the black-box problem. The RBI wants explainability thresholds for AI-driven decisions — meaning the system must be able to articulate, in comprehensible terms, why it approved or denied a loan, flagged a transaction as fraudulent, or recommended a particular investment. Banks must also test their AI systems under adversarial attacks and abnormal scenarios, monitor for bias and discriminatory outcomes, and continuously assess whether a model's accuracy has drifted from its baseline.

For generative AI models that interact with customers — think chatbots, virtual assistants, automated advisory tools — the guidelines add another layer: mandatory cybersecurity controls and explicit safeguards against hallucination, the industry's polite term for AI confidently fabricating information.

"The guidance does add governance and explainability friction, but mostly where the stakes are highest — around credit, pricing and autonomous decisions," said Ajay Sirikonda, partner at EY India. "Elsewhere, it removes the bigger blocker: uncertainty. Banks have sat on AI not because it was costly, but because no one had said what was allowed."

## The Third-Party Problem

Perhaps the most consequential provision concerns third-party AI. India's fintech ecosystem — from PhonePe and Razorpay to Paytm and CRED — relies heavily on AI models built by external vendors. Under the new framework, banks remain fully responsible for outcomes generated by these third-party models, even when the bank did not build or control the system.

This is a direct response to the current reality: dozens of Indian banks and NBFCs have deployed AI-powered lending tools from fintech partners without conducting independent audits of how those tools make decisions. The RBI is saying, in effect, that ignorance of your own AI is no longer a defence.

The "kill switch" requirement applies to third-party models too. If a vendor's credit-scoring algorithm starts producing anomalous results at 2 a.m. on a Saturday, the bank must be able to shut it down immediately — not file a support ticket.

## Why NRIs Should Care

For Indian Americans with financial lives that span both countries, the implications are direct. Millions of NRIs hold accounts with Indian banks, invest through Indian brokerages, send remittances via UPI-linked services, and use Indian digital payment platforms. These systems are increasingly run by AI — from fraud detection to KYC verification to dynamic pricing.

The RBI's framework means the AI approving your remittance transfer, scoring your home loan application in Bengaluru, or managing your mutual fund portfolio through Zerodha or Groww will now operate under explicit rules. If the model discriminates, drifts, or hallucinates, there is a mandated process for catching it, and a switch for stopping it.

The timing is not accidental. India's banking sector has seen a surge in AI adoption, accelerated by the pandemic and UPI's explosive growth. The RBI reported a sharp rise in AI-enabled financial fraud. The central bank is trying to stay ahead of a curve that, in other sectors, regulators have conspicuously failed to anticipate.

## What Happens Next

The draft guidelines are open for public feedback until July 24. Industry executives expect the final framework to be largely intact, with perhaps minor calibrations on timelines and scope. When enacted, it will apply to all banks and regulated financial institutions — a universe that includes every institution NRIs deal with.

For the global AI governance conversation, the move is notable. India is not banning AI in banking — far from it. It is saying: deploy it, but give us the kill switch."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Central Bank Just Gave Every Bank an AI Kill Switch. Here's What It Means for Your Money.",
    "subheadline": "The RBI's sweeping new framework demands explainability, board-level oversight, and the ability to shut down any AI system instantly — including those from third-party fintechs.",
    "slug": make_slug("rbi-ai-kill-switch-banking-guidelines-model-risk"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Millions of NRIs hold Indian bank accounts, invest through Indian brokerages, and use UPI-linked services that are increasingly AI-driven — these rules directly govern the systems handling their money.",
    "tags": ["rbi", "ai-regulation", "banking", "fintech", "india", "artificial-intelligence"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Inc42", "url": "https://inc42.com/features/project-kill-switch-can-rbi-protect-banks-nbfcs-from-rogue-ai-actors/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com"},
        {"name": "EY India (via Outlook Business)", "url": "https://www.outlookbusiness.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_02.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_02.jpg",
    "image_caption": "The Reserve Bank of India headquarters in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}


# ── Article 3: Foxconn Bengaluru iPhone Factory ─────────────────────────

art3_body = """The first iPhones have rolled off Foxconn's production line at its new facility near Bengaluru, and Apple is not slowing down.

Karnataka's Commerce and Industries Minister M.B. Patil confirmed that Foxconn's unit at the Information Technology Investment Region in Devanahalli — roughly 40 kilometres from central Bengaluru — has begun commercial iPhone shipments as of June. The announcement marks a concrete milestone in Apple's accelerating bet on India: the company now aims to assemble nearly 25 per cent of all iPhones in India within the next two to three years, up from around 15 per cent today.

"This isn't just a manufacturing milestone — it marks a strategic shift," Patil wrote on social media. "With rising geopolitical and tariff pressures, India is fast becoming Apple's preferred production hub."

## The Scale of the Build-Out

The numbers behind Apple's India push are stacking up fast. Foxconn has bought roughly 300 acres of land in the Devanahalli-Doddaballapur corridor. The new plant aims to eventually produce 20 million smartphones annually — mostly iPhones. Foxconn's total investment in its India subsidiary now stands at $2.82 billion, after a fresh $37.2 million infusion this month raised its stake in the local unit to 99.99 per cent.

Meanwhile, Tata Electronics — which already operates an iPhone assembly plant in Karnataka — is planning what would be India's largest iPhone factory in Tamil Nadu. The facility, expected to be operational within 12 to 18 months, will host 20 assembly lines and employ 50,000 workers. Tata also makes iPhone enclosures at its Hosur facility and plans to launch 100 Apple-focused retail stores across India.

Apple's third Indian manufacturer, Pegatron — now majority-owned by Tata Electronics — adds further capacity. Together, the three contract manufacturers are on a trajectory to produce over 50 million iPhones annually in India.

## Why the Shift

The arithmetic is driven by tariffs as much as ambition. With U.S.-China trade tensions showing no sign of easing and tariffs on Chinese-manufactured goods remaining elevated, Apple has been systematically redirecting production. Tim Cook confirmed that for the June quarter, the majority of iPhones sold in the United States were manufactured in India — a statement that would have been unthinkable three years ago.

India's Production Linked Incentive (PLI) scheme has sweetened the deal. The government has significantly increased allocations for electronics manufacturing, and Apple's suppliers have been among the programme's biggest beneficiaries. A Wall Street Journal report noted that India has been selected as the primary site to manufacture a new budget iPhone — and Apple has begun working with local contractors to lay out a production plan, something it previously did only in China.

The geopolitical logic is straightforward: no company that makes 1.2 billion phones wants all of them assembled in one country that may or may not be in a trade war with its largest market.

## The Cybersecurity Shadow

The expansion comes under a cloud. Tata Electronics this month confirmed a major cybersecurity breach after ransomware group World Leaks published over 200,000 files — totalling 630 GB — allegedly containing component design papers, manufacturing specifications, and confidential documents from Apple, Tesla, TSMC, and Qualcomm. Tata has since restricted remote access to sensitive systems across all facilities, hired a global forensic consultant, and is working directly with Apple's security team on remediation.

The breach underscores a tension in Apple's India strategy: as it builds a critical manufacturing corridor far from Cupertino, protecting intellectual property across a sprawling supply chain becomes exponentially harder. India's rapid industrial scale-up has outpaced the cybersecurity infrastructure needed to support it.

## What It Means for the Diaspora

For Indian Americans, the story cuts three ways. As investors, Apple's India bet is reshaping the fortunes of listed Indian companies — Tata group stocks have been a beneficiary of the manufacturing expansion, and the broader electronics manufacturing ecosystem (Dixon Technologies, Kaynes Technology, Amber Enterprises) has attracted significant NRI capital.

As consumers, the expanding Indian supply chain means the iPhone in your pocket may increasingly be Made in India — a shift with both practical and emotional resonance for the diaspora.

And as professionals, Apple's deepening India footprint is creating thousands of high-skill engineering and supply chain management roles that didn't exist five years ago, offering a reverse-migration pull for NRIs who left India precisely because such opportunities were scarce.

Apple's bet on India is no longer aspirational. It is shipping."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Foxconn's New Bengaluru Factory Just Shipped Its First iPhones. Apple Wants a Quarter of All Production in India.",
    "subheadline": "The Devanahalli plant goes live as Apple targets 25% India manufacturing — but a massive Tata data breach reminds everyone what scale costs.",
    "slug": make_slug("foxconn-bengaluru-iphone-factory-apple-25-percent-india"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRIs are invested in Tata and India's electronics manufacturing ecosystem; the iPhones they buy may soon be Made in India; high-skill roles in Apple's supply chain create reverse-migration opportunities.",
    "tags": ["apple", "foxconn", "india-manufacturing", "tata-electronics", "iphone", "make-in-india"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian EYE", "url": "https://theindianeye.com"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com"},
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Wall Street Journal (via The Indian EYE)", "url": "https://theindianeye.com"}
    ]),
    "score_total": 76,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4211136/pexels-photo-4211136.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Smartphone circuit boards in production at an electronics manufacturing facility",
    "image_attribution": "Pexels",
    "body": art3_body.strip(),
}


# ── Insert all articles ─────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
