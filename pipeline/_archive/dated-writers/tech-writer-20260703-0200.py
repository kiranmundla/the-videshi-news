#!/usr/bin/env python3
"""The Videshi Technology Writer — 2026-07-03 02:00 PDT run."""
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

# ──────────────────────────────────────────────
# ARTICLE 1: OpenAI 5% Government Stake
# ──────────────────────────────────────────────

article1_body = """Sam Altman has a proposition for Washington: take a piece of the machine.

The OpenAI chief executive has been in early talks with the Trump administration about handing over a 5 per cent equity stake in the company, the Financial Times reported on Thursday. The proposed arrangement would channel the shares into a public investment vehicle — modelled on Alaska's Permanent Fund, which distributes oil royalties to state residents — so that ordinary Americans, not just Silicon Valley insiders, share in AI's expected windfall.

The idea is not limited to OpenAI. Altman has suggested that rival AI labs — including Anthropic, Google, and Meta — make similar contributions, creating a de facto sovereign wealth fund seeded by the industry's most valuable companies. At OpenAI's most recent valuation of $852 billion, a 5 per cent slice would be worth roughly $42.6 billion.

## The political math

Altman has pitched the concept to an unusually broad coalition: President Trump, Commerce Secretary Howard Lutnick, Treasury Secretary Scott Bessent, and Senator Bernie Sanders. That last name is not a typo. Sanders introduced legislation last month calling for a government fund financed by AI companies that would pay every American citizen $1,000 a year. Altman's proposal is gentler — equity, not a tax — but it borrows the same underlying logic: the public helped build the datasets that trained these models, so the public deserves a cut.

Trump, for his part, has been publicly musing about "giving the public a stake" in AI firms since June. In August 2025, his administration took a 10 per cent stake in Intel, worth $8.9 billion, as part of a broader chips-and-national-security play. The OpenAI proposal extends that precedent from hardware to software — from silicon to intelligence.

## Why now

The timing is not accidental. OpenAI and Anthropic are both preparing for initial public offerings, and neither wants to walk into a regulatory buzzsaw. Over the past month, Washington has flexed hard: the Trump administration ordered Anthropic to suspend foreign access to its most advanced model, Fable 5, citing national security. It then asked OpenAI to delay the broad release of GPT-5.6, restricting it to a small number of government-approved partners. Both restrictions have since been partially lifted, but the message was unmistakable — the era of "move fast and ship it" is over.

Anthropic, for its part, has distanced itself from the equity-sharing concept. A source told Reuters on Thursday that Anthropic and the White House have not discussed any government stake in the company. Google, Meta, and xAI — Elon Musk's AI venture — have not publicly commented.

## The Indian angle

For the estimated 300,000 Indian-origin professionals working at American AI and tech companies, the proposal lands in complicated territory. Sriram Krishnan, the Indian American entrepreneur who serves as the White House's senior AI policy advisor, is at the centre of these conversations. His dual credibility — trusted by both the administration and the Valley — makes him a pivotal figure in shaping whatever framework emerges.

The implications reach further. India's own sovereign AI push — anchored by startups like Sarvam (freshly valued at $1.5 billion) and backed by the India AI Mission's goal of building 20 homegrown models — could find itself navigating a world where American AI companies are partially government-owned. That shifts the competitive calculus. It also raises questions about whether India should demand similar equity arrangements from foreign AI companies operating on Indian data and Indian users.

For Indian engineers and researchers at OpenAI, Anthropic, and Google's DeepMind, the more immediate question is what government ownership means for compensation. Stock options are the lifeblood of Silicon Valley hiring. Diluting existing equity by 5 per cent — or more, if the concept expands — directly affects the people building these systems. Many of those people hold H-1B visas and have spent years waiting for green cards while their paper wealth accumulates in restricted stock units tied to companies whose regulatory future is suddenly uncertain.

Any deal would likely require an act of Congress, which means months of debate, lobbying, and political theatre. But the fact that Altman is volunteering equity — rather than waiting for Washington to take it — suggests he has concluded that some version of this is inevitable. The only question is whether the industry gets to design its own cage, or whether Congress builds it for them."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI Just Offered the US Government a 5% Stake. It Wants Every AI Company to Do the Same.",
    "subheadline": "Sam Altman has pitched Trump, Bernie Sanders, and the Treasury Secretary on a sovereign wealth fund seeded by AI equity. Anthropic says it's not interested.",
    "slug": make_slug("openai-5-percent-stake-government-ai-sovereign-wealth-fund"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin AI professionals face equity dilution; White House AI advisor Sriram Krishnan is central to the talks; India's sovereign AI ambitions must now account for partially government-owned American competitors.",
    "tags": ["openai", "ai-regulation", "sam-altman", "trump", "sovereign-wealth-fund", "indian-tech"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/openai-proposes-handing-trump-administration-5-stake-ft-reports-2026-07-03/"},
        {"name": "Financial Times (via CNN)", "url": "https://www.cnn.com/2026/07/02/tech/openai-trump-5-percent-stake/index.html"},
        {"name": "Gizmodo", "url": "https://gizmodo.com/america-first-sam-altman-proposes-us-led-international-forum-for-ai-and-5-stake-for-trump-admin-2000623456"},
        {"name": "Reuters (Anthropic response)", "url": "https://www.reuters.com/technology/artificial-intelligence/trump-administration-anthropic-have-not-discussed-government-taking-stake-it-2026-07-03/"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
    "image_caption": "OpenAI CEO Sam Altman at a meeting in February 2025",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}

# ──────────────────────────────────────────────
# ARTICLE 2: HCLTech $1.14B European AI Deal
# ──────────────────────────────────────────────

article2_body = """The obituary for Indian IT services has been written so many times this year that it has become its own genre. On Friday, HCLTech offered a rebuttal worth $1.14 billion.

India's third-largest software services exporter announced that it had won a deal with a major European company to build an AI-driven operating model for global digital workplace and enterprise network management. The contract spans four and a half years, with an option to extend for five more. HCLTech did not name the client, but described the engagement as entirely new business — not a renewal, not an upsell, not an existing account expanding scope. A cold win, in other words, in a market that has spent the past six months questioning whether Indian IT firms can win anything at all.

HCLTech's shares jumped 4.6 per cent at the open, dragging the Nifty IT index up 2.5 per cent and extending a fragile recovery that began on Thursday after the sector hit its lowest level in more than five years.

## The context is brutal

The Nifty IT index has crashed 33 per cent from its February peak, making Indian IT the worst-performing sector on the Indian market in 2026. Infosys, TCS, Wipro, Tech Mahindra — all have suffered double-digit declines even as they continue to generate healthy cash flows. The culprit is a toxic combination of slowing discretionary technology spending, compressed pricing from AI-assisted delivery, and a pervasive fear that generative AI will eventually automate the work that Indian IT companies do for a living.

Palantir's CEO Alex Karp poured accelerant on that fire last week when he called the token-based pricing of AI labs like OpenAI and Anthropic a "wealth tax" on enterprises — a line that, paradoxically, sent Indian IT stocks soaring on Thursday as investors reasoned that if AI-as-a-service is overpriced, old-fashioned systems integration might look attractive again.

## Why this deal matters

The HCLTech contract pushes back against the "AI will kill IT services" narrative in a specific, testable way. The deal is explicitly about building an AI-driven operating model — meaning HCLTech is not selling services that AI threatens to replace, but selling the capability to deploy AI itself. That is a different business, and one that the company has been positioning for aggressively.

In June, HCLTech led a $150 million investment in Sarvam, the Bengaluru-based AI startup that hit unicorn status at a $1.5 billion valuation. The logic was transparent: combine Sarvam's Indian-language AI models with HCLTech's global enterprise relationships and 220,000-person engineering workforce to create an AI services stack that neither company could build alone. The European deal suggests that logic is already generating pipeline.

HCLTech reports its first-quarter results for fiscal 2027 on July 13, followed by TCS on July 9, Infosys on July 17, and Wipro on July 18. Analysts expect a muted quarter across the board — TCS is forecast to post just 0.2 per cent sequential dollar revenue growth, with margins contracting 90 basis points from annual wage hikes. The management commentary that investors actually care about will focus on whether AI is cannibalising existing contracts or creating new ones.

## What NRIs should watch

For the tens of thousands of Indian professionals employed by HCLTech, Infosys, TCS, and Wipro — both in India and on H-1B and L-1 visas in the United States and Europe — the next two weeks of earnings are a referendum on job security. A $1.14 billion deal is one data point. But it is a data point that says the work is shifting, not disappearing.

NRI investors tracking IT stocks face a different calculus. The sector is now trading at valuations not seen since 2021, and the Nifty IT index's 29 per cent decline over the past year has wiped out more than ₹6 lakh crore in market capitalisation. The question is whether this is a buying opportunity or a value trap. HCLTech's deal — and the earnings season that follows — will help answer that.

The broader signal is subtler. Indian IT built a $283-billion-a-year industry on the premise that global companies would rather pay Indian engineers to manage their technology than do it themselves. AI changes the unit economics of that premise, but it does not eliminate the premise itself. Someone still has to deploy the models, integrate them with legacy systems, manage the data pipelines, and keep the lights on. Friday's deal suggests that someone is still, for now, HCLTech."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "HCLTech Just Won a $1.14 Billion AI Deal in Europe. Indian IT's Worst Year Might Be Turning.",
    "subheadline": "The contract is entirely new business — not a renewal — and lands as the sector trades at five-year lows. Earnings season starts next week.",
    "slug": make_slug("hcltech-114-billion-ai-deal-europe-indian-it-recovery"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "HCLTech employs tens of thousands of Indian professionals on H-1B and L-1 visas; the deal signals that AI is transforming, not eliminating, IT services jobs; NRI investors face a critical earnings season with IT stocks at five-year lows.",
    "tags": ["hcltech", "indian-it", "ai-deal", "enterprise-ai", "nifty-it", "earnings"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-hcltech-wins-114-billion-deal-with-european-firm-2026-07-04/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/ai-fears-cheap-valuations-and-weak-earnings-whats-really-driving-indias-it-stocks"},
        {"name": "Livemint", "url": "https://www.livemint.com/market/stock-market-news/nifty-it-jumps-over-4-infosys-tcs-shares-surge-up-to-5-should-you-buy-it-stocks-at-this-juncture-11751432437750.html"},
        {"name": "Reuters (India markets)", "url": "https://www.reuters.com/markets/asia/indian-shares-outperform-asia-oil-drops-it-rebounds-2026-07-03/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/HCL_Tech_Noida_SEZ_Campus.png/1280px-HCL_Tech_Noida_SEZ_Campus.png",
    "image_caption": "HCLTech's SEZ campus in Noida, one of the company's major global delivery centres",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body
}

# ──────────────────────────────────────────────
# Insert articles
# ──────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
