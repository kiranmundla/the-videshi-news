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
        "headline": "Satya Nadella Just Publicly Fired at His Own Executive Over an AI 'Addiction' Memo",
        "subheadline": "A leaked Microsoft document outlined plans to 'make people addicted' to Scout, the company's new AI agent. Nadella's response was swift, blunt, and sent to 50 top engineers.",
        "slug": make_slug("nadella-slams-scout-addiction-memo-microsoft"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Nadella's rebuke reinforces a Silicon Valley leadership model increasingly shaped by Indian-origin CEOs — one where ethical guardrails on AI are set at the top, not delegated to compliance teams.",
        "tags": ["microsoft", "satya-nadella", "ai-ethics", "scout", "indian-tech-leaders"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "New York Post", "url": "https://nypost.com/2026/06/05/business/microsofts-satya-nadella-slams-company-exec-for-outlining-plan-to-make-people-addicted-to-scout-ai-tool/"},
            {"name": "404 Media", "url": "https://www.404media.co/"},
            {"name": "Android Authority", "url": "https://www.androidauthority.com/microsoft-scout-addicted-ai/"},
            {"name": "CXOToday", "url": "https://cxotoday.com/news-analysis/get-users-addicted-to-microsoft-scout-satya-nadella-disagrees-but/"},
            {"name": "The Information", "url": "https://www.theinformation.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Satya Nadella, Chairman and CEO of Microsoft",
        "image_attribution": "Wikimedia Commons",
        "body": """When Microsoft unveiled Scout at its Build 2026 conference in San Francisco on June 2, the pitch was smooth: an always-on personal AI agent that manages your calendar, triages your inbox, and prepares your meetings while you do the actual thinking. The kind of tool that makes knowledge workers feel like they have a chief of staff.

What Microsoft did not plan to unveil was the internal document that made Scout sound less like a productivity assistant and more like a slot machine.

## The Memo That Went Sideways

A confidential strategy document titled "ClawPilot: Overview and Plan with Project Lobster," obtained by 404 Media, laid out a three-phase roadmap for Scout's rollout. Phase one carried a name that would make any tech ethicist wince: **"Make people addicted."**

The document, co-authored by Microsoft Corporate Vice President Omar Shahine and colleague Jakob Werner, instructed teams to "continue shipping the standalone ClawPilot experience. Pilot the UX, grow the user base, and build the skill and tool ecosystem that makes people depend on it daily." The authors noted this was "already happening organically" among the 1,000-plus Microsoft employees using the tool internally — including Nadella himself.

Phases two and three outlined plans to link Scout to other AI tools and expand its capabilities, completing the arc from "addictive app to agentic platform."

## Nadella's Response Was Not a PR Statement

Within hours of the leak, Satya Nadella posted a blistering message on an internal board, sent to approximately 50 of Microsoft's top software engineers, according to The Information.

"This is absolutely a non-goal! If anything we are doing the exact opposite," Nadella wrote. "We want to make sure AI empowers and adds real value to human endeavour and broad economic growth! We should make our teams clear about this."

He then attached the 404 Media report and added a line that left little room for interpretation: "Not sure what this document is or who is writing and leaking this nonsense! They may want to go work elsewhere."

Microsoft's official response, issued to media outlets, was notably more measured: "Our goal isn't more screen time. It's more time back."

## The Credibility Problem

The episode would be easy to dismiss as an embarrassing internal document that said the quiet part loud — if not for 404 Media's pushback. The outlet noted that the document was not a rogue brainstorm. It was authored by the corporate VP leading the Scout team, a person Nadella presumably chose for the role. Shahine's name also appears on Microsoft's official blog post announcing Scout.

"The document we reported on was not some random document," 404 Media responded. The tension between Nadella's disavowal and the authorship trail remains unresolved.

## Why Indian Americans Should Pay Attention

For the Indian diaspora in tech, this episode matters on two levels.

First, it is the latest instance of an Indian-origin CEO setting the ethical boundary on AI at a company that employs tens of thousands of Indian engineers. Nadella joins a cohort — Sundar Pichai at Google, Arvind Krishna at IBM, Shantanu Narayen at Adobe — who are navigating the tension between shipping AI fast and shipping it responsibly. His willingness to publicly rebuke a senior executive, rather than bury the story in HR, is a leadership signal that carries weight across Redmond's campuses in Hyderabad and Bengaluru as much as in Seattle.

Second, Scout itself is the kind of tool that will be built, deployed, and maintained by large numbers of Indian engineers on H-1B and L-1 visas. The ethical framework within which they build it — whether the goal is user empowerment or user dependency — directly shapes the professional environment they inhabit. When the CEO says the goal is value, not addiction, that is not just a PR line. It is a directive that filters into product specs, sprint goals, and performance reviews.

The AI industry is moving fast enough that the gap between "useful" and "addictive" is measured in features, not years. That Nadella chose to draw the line in public, rather than in a quiet meeting, tells you something about the stakes he sees."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Oracle Cut 30,000 Jobs. Twelve Thousand Were in India.",
        "subheadline": "The largest single-company layoff in enterprise software history has slashed 40% of Oracle's India workforce — while the company's AI revenue grew 243% and its stock hit record highs.",
        "slug": make_slug("oracle-30000-layoffs-12000-india-ai-paradox"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Oracle India was a career anchor for tens of thousands of engineers, DBAs, and ERP specialists who built stable middle-class lives in Bengaluru and Hyderabad. The layoffs have sent shockwaves through a talent pool that feeds the Indian American tech pipeline.",
        "tags": ["oracle", "layoffs", "india-tech", "ai-restructuring", "enterprise-software"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "StartupNews.fyi", "url": "https://startupnews.fyi/2026/06/03/big-tech-re-skilling-how-oracles-30000-global-layoffs-are-impacting-it-hubs-in-india-and-the-us/"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/digital/oracle-layoffs-employees-allege-job-status-was-altered-ahead-of-workforce-reduction/"},
            {"name": "IndMoney", "url": "https://www.indmoney.com/articles/stocks/oracle-layoffs-2026"},
            {"name": "LiveMint", "url": "https://www.livemint.com/companies/news/laid-off-oracle-techie-lands-job-in-45-days/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Oracle-October2011.JPG/1280px-Oracle-October2011.JPG",
        "image_caption": "Oracle Corporation headquarters in Redwood City, California",
        "image_attribution": "Wikimedia Commons",
        "body": """Oracle Corporation is entering the final phase of what may be the largest single-company workforce reduction in enterprise software history. Nearly 30,000 employees — roughly 18% of its global headcount — are being shown the door. Of those, an estimated 10,000 to 12,000 are in India, representing a staggering 40% contraction of Oracle's workforce in the country.

The separation dates for the latest tranche fall between June 1 and June 15. Some employees learned their fate through early-morning emails. Others discovered it when their access to company systems was revoked without warning.

## Record Revenue, Record Layoffs

The dissonance is difficult to ignore. Oracle reported third-quarter fiscal 2026 revenue of $17.2 billion, up 22% year-on-year. Cloud revenue surged 44% to $8.9 billion. Oracle Cloud Infrastructure's AI business grew 243%. The company's remaining performance obligations — essentially its backlog — climbed a staggering 325% to $553 billion.

This is not a company in distress. It is a company restructuring for a world where AI infrastructure generates more revenue per engineer than traditional enterprise services ever did. Oracle plans to spend nearly $50 billion in capital expenditure during fiscal 2026, much of it on AI data centres and cloud infrastructure.

The human cost of that pivot is concentrated in roles that built Oracle's business over two decades: database administrators, ERP implementation specialists, cloud infrastructure professionals, and operations staff. These are not niche positions. They represent the backbone of enterprise IT across India and the United States.

## India Bears the Brunt

India was one of Oracle's largest global employment bases, with roughly 30,000 workers before the cuts. The 12,000 affected roles span engineering, architecture, NetSuite's India Development Centre, SaaS and Virtual Operations Services, and core tech offices in Bengaluru.

The severance structure for Indian employees follows the N+2 formula: the number of years worked, paid out in months, plus notice pay, leave encashment, gratuity, and an additional two-month salary — though that last piece is reportedly contingent on voluntary resignation.

The Oracle Health division, formed after the $28.3 billion Cerner acquisition, absorbed between 8,000 and 10,000 cuts globally. A demographic survey compiled by employee advocacy groups found that over 60% of affected workers were over 40, with more than 20% having spent 15 or more years at the company.

## The Dirty Allegations

The layoffs have also surfaced uncomfortable claims. According to Storyboard18, some employees allege that their job classifications were altered ahead of the workforce reduction — a move that, if substantiated, could carry legal implications. Oracle has not publicly responded to these allegations, and the claims remain unproven. Employment lawyers and labour advocates are monitoring the situation.

## What This Means for the Diaspora

For Indian Americans in enterprise tech, Oracle's restructuring is a case study in the new math of the industry. Companies are not cutting because business is bad. They are cutting because AI makes it possible to do the same work — or more — with fewer people. Oracle's AI revenue growth of 243% and its simultaneous elimination of 18% of its workforce are not contradictory. They are causally linked.

The immediate question for the thousands of displaced Indian engineers is absorption. India's tech job market is already under pressure in 2026, with Amazon, Meta, Pinterest, and Epic Games all announcing layoffs this year. The supply of senior enterprise professionals is about to spike at a moment when demand for those specific skills is contracting.

One viral Reddit post offers a counterpoint. A laid-off Oracle engineer in India reported landing three job offers within 45 days by pivoting aggressively into AI engineering — spending a month upskilling on transformers, attention mechanisms, and LLM architecture before applying to 10-15 positions daily. He joined as an AI engineer. "I was soaking in knowledge like a sponge," he wrote.

That trajectory — from Oracle DBA to AI engineer in 45 days — may be aspirational, but it captures the only durable strategy in a market where the companies doing the firing are also the ones creating the new roles. The skills are different. The urgency is real."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Approved Its Sixth Semiconductor Plant. This One Has Foxconn's Name on It.",
        "subheadline": "The HCL-Foxconn joint venture near Delhi's new Jewar airport will produce 36 million display driver chips annually, with commercial production slated for 2027.",
        "slug": make_slug("hcl-foxconn-semiconductor-plant-jewar-india-sixth"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For NRI investors and engineers watching India's chip ambitions, the HCL-Foxconn JV represents a test of whether India can move from policy announcements to functioning fabs — and whether the diaspora's semiconductor expertise will find a path home.",
        "tags": ["semiconductor", "india-chip-mission", "hcl", "foxconn", "make-in-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/india-approves-hcl-foxconn-joint-venture-for-semiconductor-unit/"},
            {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com/business/indias-semiconductor-push-from-consumer-to-creator-opinion/"},
            {"name": "Blura", "url": "https://admin.blura.in/news/hcl-and-foxconn-plan-rs-3706-crore-semiconductor-unit-in-up"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/3665442/pexels-photo-3665442.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Close-up of a microchip on a printed circuit board",
        "image_attribution": "Pexels",
        "body": """India's cabinet has approved the country's sixth semiconductor plant under the India Semiconductor Mission, this time a joint venture between HCL Group and Taiwan's Foxconn. The facility, which will cost ₹3,706 crore ($435 million), will be built near the upcoming Jewar airport in Uttar Pradesh, and is expected to begin commercial production in 2027.

Information and Broadcasting Minister Ashwini Vaishnaw confirmed the approval in a cabinet briefing in New Delhi. The plant will have a capacity of 20,000 wafers per month and will produce 36 million display driver chips annually — the kind of components that go into smartphones, televisions, automotive dashboards, and industrial displays.

## The Significance of the Sixth

Six approved plants in under three years would have seemed implausible when Prime Minister Narendra Modi launched the India Semiconductor Mission. The programme has accelerated sharply, driven by a combination of central subsidies (up to 50% of project cost), state-level incentives, and geopolitical tailwinds from the US-China chip war.

Gujarat has emerged as the epicentre, hosting the Tata-Powerchip fabrication project in Dholera (an $11 billion venture targeting 28nm chips at 50,000 wafers per month), Micron's $2.7 billion ATMP facility in Sanand, the CG Power-Renesas initiative, and the Kaynes Semicon unit. Assam has Tata's OSAT facility. And now Uttar Pradesh enters the map with HCL-Foxconn at Jewar.

The geographic distribution is deliberate. States are competing aggressively with additional capital subsidies, tax exemptions, land rebates, power concessions, and skilling programmes. UP's Semiconductor Policy 2024 is among the most ambitious, linking chip investments with electronics manufacturing, logistics infrastructure, and data centre development near the Delhi-NCR economic corridor.

## Where Foxconn Fits

Foxconn's involvement lends credibility that pure domestic ventures cannot easily match. The Taiwanese manufacturing giant is the world's largest electronics contract manufacturer, assembling iPhones, PlayStation consoles, and servers for the world's biggest brands. Its expertise in high-volume precision manufacturing — and its willingness to invest in a country with no operational chip fabs — is a signal that global supply chain diversification away from China is no longer theoretical.

The HCL Group brings its own heft. While better known in the West for its IT services arm HCL Technologies, the parent group has deep roots in Indian hardware manufacturing dating back to its founding by Shiv Nadar in 1976.

## The Reality Check

Display driver chips are not the bleeding edge. They are not 3nm logic processors or HBM memory stacks for AI accelerators. They are mature-node commodity semiconductors — essential, but not the kind of product that puts India on TSMC's competitive radar.

This is by design. India's chip strategy is pragmatic: start with assembly, testing, and packaging (ATMP), move to mature-node fabrication, build the talent pipeline, and then — eventually — pursue advanced nodes. The Tata-Powerchip fab in Dholera, targeting 28nm, is the most ambitious fabrication project, and even that is two generations behind the frontier.

The Adani-Tower Semiconductor $10 billion fab in Maharashtra, which would have been the most aggressive play, has been paused over concerns about commercial demand. That pause is a reminder that government subsidies can build fabs, but only market demand can keep them running.

## The Diaspora Question

For Indian Americans working in the semiconductor industry — and there are tens of thousands at Intel, Qualcomm, Broadcom, NVIDIA, Texas Instruments, and the EDA firms that enable chip design — India's fab push raises a persistent question: is there a path home?

The answer is slowly shifting from "not yet" to "maybe, for the right role." The talent deficit is real. India needs an estimated 85,000 semiconductor professionals by 2027, according to the India Semiconductor Mission, and its engineering colleges are not producing them at that pace. The diaspora's expertise in process engineering, yield management, and design verification is exactly what these new fabs will need — once they are operational.

The HCL-Foxconn plant will create over 4,000 direct jobs. Multiply that across six approved projects and the employment opportunity is substantial. The harder question is whether the roles, compensation, and career trajectories will be compelling enough to pull senior engineers away from fab complexes in Arizona, Oregon, and Texas.

For now, the answer is an investment thesis rather than a career move. India's chip story is being written in cabinet approvals, ground-breaking ceremonies, and subsidy disbursements. The chapter where it is written in functioning production lines and shipped wafers has not yet begun."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
