#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
        "headline": "Sriram Krishnan Is Leaving the White House. He Shaped America's AI Policy on the Way Out.",
        "subheadline": "The Chennai-born advisor helped write the playbook for US AI dominance — from Stargate to government equity stakes. Now he's building something new.",
        "slug": make_slug("sriram-krishnan-leaving-white-house-ai-advisor"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Krishnan is one of the most powerful Indian Americans in tech policy. His departure raises questions about who will carry the diaspora's voice in AI governance — and whether his planned policy institute will extend Indian-origin influence beyond government.",
        "tags": ["sriram-krishnan", "white-house", "ai-policy", "indian-american", "trump-administration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/06/sriram-krishnan-is-leaving-his-role-as-white-house-ai-advisor/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/white-house-ai-policy-adviser-krishnan-leave-position-information-reports-2026-06-06/"},
            {"name": "The Information", "url": "https://www.theinformation.com/articles/white-house-ai-advisor-sriram-krishnan-to-depart"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/da/MS200024.jpg",
        "image_caption": "Sriram Krishnan, Senior White House Policy Advisor on Artificial Intelligence",
        "image_attribution": "Wikimedia Commons",
        "body": """When Sriram Krishnan walked into the White House in January 2025, he was a venture capitalist from Andreessen Horowitz with a resume that read like a roadmap of Silicon Valley: Microsoft, Facebook, Twitter, Snap, Yahoo. When he announced his departure on Saturday — effective end of June — he was arguably the most influential Indian American in the machinery of US technology policy.

His exit, confirmed through a post on X and corroborated by The Information and Reuters, closes an 18-month chapter in which a Chennai-born engineer helped define how the world's most powerful government thinks about artificial intelligence.

## The Architect's Inventory

Krishnan's fingerprints are on nearly every major AI decision the Trump administration has made. The AI Action Plan he co-authored prioritised data centre construction over regulation, a posture that unlocked hundreds of billions in private-sector infrastructure commitments. The $500 billion Stargate initiative — the largest AI infrastructure project ever announced — bore his influence. President Trump himself said in December 2025 that "without him, things on AI would not function well."

The executive orders followed in sequence: one challenging state-level AI regulations that threatened to fragment the market, another establishing voluntary cybersecurity reviews for frontier models before public release. Most recently, the administration endorsed the concept of government equity stakes in major AI companies — a proposal that originated with OpenAI's Sam Altman but gained institutional momentum under Krishnan's watch.

Time named him a Person of the Year in 2025 as an "Architect of Artificial Intelligence." His closest collaborator, David Sacks — the investor who served as AI and crypto czar before stepping into an advisory role — drew a public tribute from Krishnan on his way out.

## What Comes Next

Krishnan told supporters he plans to "build institutions" that tackle challenges for "America and its allies." The Washington Post reported he is setting up a policy institute staffed with engineers, designed to maintain his influence over AI governance from outside government. The model is familiar in Washington — the revolving door between policy-making and policy-advising — but Krishnan's version would be unusually technical, populated by builders rather than lobbyists.

"Whether it is energy, data centres or a clear path for Americans to experience the benefits of AI, there are many tough issues we all need to navigate together," he wrote.

## The Diaspora Question

For the Indian American technology community, Krishnan's tenure was more than a policy footnote. He was the person in the room when trillion-dollar decisions about compute infrastructure, model safety, and international AI diplomacy were being made. His background — IIT-educated, product-led, immigrant-to-insider — mirrored the trajectory of tens of thousands of Indian engineers in the Bay Area, Seattle, and New York who build the systems these policies govern.

His departure creates a vacuum. No obvious successor with comparable diaspora credentials has been named. The White House has not announced a replacement, and the AI policy apparatus Krishnan helped build will need to run on institutional memory until one arrives.

For NRI professionals working at frontier AI labs — the engineers at OpenAI, Anthropic, Google DeepMind, and Meta AI who will feel the downstream effects of whatever policy framework emerges — the question is pointed: who advocates for them now?

Krishnan's planned institute may provide part of the answer. An organisation led by an Indian American who shaped the rules from inside government, now building the analytical infrastructure to shape them from outside, would be unprecedented in the AI policy space. Whether it becomes a genuine centre of gravity or a well-funded think tank with diminishing returns will depend on execution.

The man who helped write America's AI playbook is leaving the building. The playbook stays behind."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Trump Wants a Piece of OpenAI. Your AI Stock Options Just Got Complicated.",
        "subheadline": "The president is exploring government equity stakes in AI companies, with dividends for every American household. Indian engineers holding RSUs at frontier labs should pay attention.",
        "slug": make_slug("trump-government-equity-ai-openai-rsu-indian-engineers"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Tens of thousands of Indian engineers hold RSUs and stock options at AI companies that could be affected. Government equity stakes could dilute holdings, alter IPO valuations, and reshape the wealth-creation engine that H-1B workers have relied on for decades.",
        "tags": ["trump", "ai-policy", "openai", "government-equity", "rsu", "indian-engineers", "anthropic"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/06/trump-federal-government-shares-artificial-intelligence-companies/84084917007/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/us-officials-eye-government-stakes-ai-companies-notus-reports-2026-06-05/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/openai-anthropic-government-stakes-ai-stocks-9ddd52b7"},
            {"name": "TradingView", "url": "https://www.tradingview.com/news/reuters.com,2026-06-05:newsml_L1N3RG18F:0/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20417783/pexels-photo-20417783.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "The US Capitol dome in Washington, DC, where AI policy is being reshaped",
        "image_attribution": "Pexels",
        "body": """On Thursday, aboard Air Force One, President Trump confirmed what had been percolating through Washington's back channels for weeks: the US government is exploring taking equity stakes in major artificial intelligence companies.

"There are concepts where pieces could be given to the American public, where the American public essentially becomes a partner with the companies," Trump told reporters. "We are looking."

The idea is simple in theory, radical in practice. AI companies would voluntarily cede shares to the federal government. Returns from those holdings would flow to public purposes — potentially including dividend payments to every American household. It is, depending on your vantage point, either the most innovative wealth-distribution mechanism since Social Security or a recipe for government overreach into the private sector.

## How We Got Here

The concept traces back to Sam Altman, who first pitched it directly to Trump in early 2025. As OpenAI prepares for what could be the largest technology IPO in history, Altman has revisited the proposal with senior administration officials in recent weeks. The framing is strategic: if AI companies share their upside with the public, the political backlash against data centres, job displacement, and concentrated wealth becomes more manageable.

NOTUS broke the story on June 4. Within 24 hours, Trump put his weight behind it publicly.

The administration already has precedent. Under Trump's second term, the federal government acquired a 10 per cent stake in Intel, equity positions in companies that produce critical minerals, and a "golden share" in US Steel that gives Washington veto power over certain decisions. AI would be the next frontier.

Senator Bernie Sanders, operating from the opposite end of the political spectrum, has proposed something far more aggressive: a 50 per cent government stake in the nation's largest AI companies, imposed through a one-time stock tax. Trump, asked about Sanders's plan, offered a surprising response: "As far as economics is concerned, we have some things that aren't that far apart."

## What It Means for the Engineer in Cupertino

The policy discussion in Washington tends to focus on macro abstractions — national competitiveness, public dividends, regulatory frameworks. But in the apartment complexes of Sunnyvale and the townhouses of Bellevue, the implications are intensely personal.

Tens of thousands of Indian engineers at OpenAI, Anthropic, Google, Meta, Microsoft, and dozens of smaller AI companies hold restricted stock units and options that form the core of their financial planning. These are the compensation packages that justify years on H-1B visas, the deferred wealth that underwrites down payments and children's college funds.

A government equity stake — even a voluntary one — would dilute existing shareholders. The size of that dilution matters enormously. A 2-3 per cent stake might be absorbed as a cost of doing business. A Sanders-style 50 per cent would be existential. The actual number, if this ever materialises, will fall somewhere in between, and the uncertainty itself is a drag.

For employees at pre-IPO companies like OpenAI and Anthropic, the calculus is more acute. Both are preparing blockbuster public offerings — OpenAI has begun confidential filing preparations, while Anthropic filed for its IPO on Monday. If the government negotiates equity before these companies go public, the IPO price could be set against a different share structure than employees were promised when they signed their offer letters.

## The Regulatory Insurance Premium

PitchBook analyst Harrison Rolfes frames the trade-off bluntly: "I do think it's like a regulatory insurance policy." Companies that give up equity get something in return — a government that is invested, literally, in their success. That means friendlier regulation, faster permitting for data centres, and a political shield against the 71 per cent of Americans who, according to a May YouGov poll, think AI is moving too fast.

D.A. Davidson analyst Gil Luria agrees, noting that AI labs "would rather have a seat at the table than an adversarial relationship with the government." The unspoken alternative — the one that makes voluntary equity attractive — is something more radical, like nationalisation.

Anthropic, notably, has said it is not in discussions with the administration about equity participation. That leaves it outside whatever protective arrangement emerges, a position that could prove either principled or costly.

## The Bottom Line

For NRI engineers mapping their financial futures around AI equity, the message is unsettling but clear: the rules of the game may be changing. The stock that was going to fund your child's Stanford tuition might now also fund an AI dividend for 130 million American households. Whether that is fair, wise, or inevitable depends on details that do not yet exist.

What does exist is a president who wants a piece of the action, a senator who wants half of it, and an industry that is trying to figure out how much it can afford to give away before the government stops asking and starts taking."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic's Mythos Can Find Thousands of Cyber Flaws. The NSA Wants It Anyway.",
        "subheadline": "The AI model that got its maker blacklisted by the Pentagon is now being deployed inside America's most secretive spy agency. The Indian engineers caught in the middle are watching closely.",
        "slug": make_slug("anthropic-mythos-nsa-pentagon-blacklist-cybersecurity"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Anthropic employs hundreds of Indian-origin AI researchers and engineers. Its CFO Krishna Rao is Indian-origin. The company's ethical stance — refusing to build tools for mass surveillance and autonomous weapons — resonates deeply with Indian American engineers who work across the national security-tech boundary.",
        "tags": ["anthropic", "mythos", "nsa", "pentagon", "cybersecurity", "ai-safety", "national-security"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/05/nsa-said-to-be-readying-anthropics-mythos-for-use-in-cyber-operations/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/blacklisted-ai-company-anthropic-white-house-ease-tensions-ahead-ipo-sources-say-2026-06-05/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/articles/security-chiefs-unfazed-by-federal-ai-oversight-2026-06-05"},
            {"name": "Financial Times", "url": "https://www.ft.com/content/anthropic-nsa-mythos-deployment"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/National_Security_Agency%2C_2013.jpg/1280px-National_Security_Agency%2C_2013.jpg",
        "image_caption": "The National Security Agency headquarters at Fort Meade, Maryland",
        "image_attribution": "Wikimedia Commons",
        "body": """Anthropic built the most powerful cybersecurity AI model in existence, then tried to control who could use it. The US government responded by blacklisting the company. Now, in a twist that captures the absurdity and gravity of AI governance in 2026, the NSA has quietly brought Mythos inside its walls anyway.

According to the Financial Times, Anthropic has deployed roughly half a dozen engineers to the National Security Agency to help America's premier signals intelligence service use Mythos for certain applications. The exact nature of those applications remains classified. Whether the engineers or the model are actively involved in the NSA's offensive hacking operations is unclear.

What is clear is that the same model the Pentagon tried to punish Anthropic for withholding is now operating inside one of the most sensitive intelligence environments on earth.

## The Model That Sees Too Much

Mythos occupies a singular position in the AI landscape. Early testing by a select group of companies found that it can identify hundreds — and possibly thousands — of cybersecurity vulnerabilities in digital systems far faster than human security teams can patch them. The Wall Street Journal reported that this gap between discovery and remediation is what alarmed national security officials in the first place.

Anthropic responded to its own model's capabilities with unusual restraint. Rather than release Mythos broadly, the company restricted access to 150 organisations across 15 countries that manage critical infrastructure affecting more than 100 million people. The logic was defensive: if Mythos can find flaws faster than anyone can fix them, giving it to the wrong people would be catastrophic.

The Pentagon wanted more. Specifically, it wanted Anthropic to license its models for "all lawful purposes" — language broad enough to encompass mass domestic surveillance and lethal autonomous weapons systems. Anthropic drew two red lines: no mass surveillance of Americans, no autonomous killing machines. The Pentagon walked away from a $200 million contract. Then it did something unprecedented: it designated Anthropic, an American AI company, as a "supply-chain risk" to national security.

## Blacklisted but Not Unwanted

The designation was the bureaucratic equivalent of a grenade. It restricted any defence contractor from integrating Anthropic's technology into military projects. Anthropic sued the Pentagon in March, arguing the move was retaliatory. As of Thursday, both sides were still submitting legal briefs.

Yet even as the Pentagon fought Anthropic in court, other parts of the government were pulling in the opposite direction. Anthropic employees met with Treasury Secretary Scott Bessent this spring to discuss Mythos and potential presidential actions on AI. Those discussions, according to a US official, directly influenced the executive order Trump signed on June 2, which established a voluntary framework for frontier AI cybersecurity testing.

CEO Dario Amodei visited the White House recently. The relationship is warming — driven partly by Anthropic's approaching IPO, which could value the company near $1 trillion, and partly by the practical reality that the US government needs Mythos more than it needs to make a point.

## The Indian Engineers in the Room

Anthropic's workforce is disproportionately drawn from the same talent pool that populates Google Brain, DeepMind, and OpenAI's research labs — and a significant fraction of that pool is Indian-origin. The company's CFO, Krishna Rao, is Indian American. Dozens of Indian researchers and engineers work on the safety and capabilities teams that built Mythos.

For these engineers, the Pentagon standoff was more than a corporate drama. It was a test of whether an AI company could maintain ethical guardrails against the most powerful military in history and survive. So far, the answer appears to be yes — commercially, at least. Anthropic raised $65 billion in its Series H round, pushing its valuation to $900 billion. The IPO filing followed days later.

But the moral ledger is more complicated. Anthropic refused to build tools for mass surveillance, then sent engineers to help the NSA — an agency whose core mission involves, among other things, large-scale signal interception. The company would argue there is a meaningful distinction between supporting defensive cybersecurity and enabling warrantless domestic surveillance. Critics would argue the distinction is thinner than Anthropic's press releases suggest.

## The Uncomfortable Middle

For Indian American engineers weighing offers from frontier AI labs, the Anthropic saga distils a question that will define the next decade of their careers: what does it mean to build responsibly when your most responsible product is also the most dangerous?

Mythos can protect critical infrastructure from cyberattacks. It can also, in the wrong hands, supercharge them. Anthropic chose to restrict access rather than maximise revenue, and the US government punished it for the restraint, then came asking for access through the back door.

The model is inside the NSA now. The lawsuit is still active. The IPO is coming. And somewhere in the middle, a few Indian engineers are writing code that both governments and hackers would pay a fortune for — trying to make sure it serves the right side."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
