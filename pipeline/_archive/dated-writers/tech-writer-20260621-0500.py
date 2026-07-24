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
        "headline": "ISRO Bet Its Reputation on a Reliable Rocket. After Two Failures, the Workhorse Flies Again Within Days.",
        "subheadline": "The PSLV — the launcher that built India's commercial space business — returns to the pad in late June after back-to-back failures rattled foreign customers. For diaspora investors in NewSpace, the stakes are credibility.",
        "slug": make_slug("isro-pslv-return-to-flight-failures-launch-newspace-nri"),
        "category": "technology",
        "vertical": "space-tech",
        "diaspora_angle": "NRIs increasingly back India's private space startups and watch ISRO's launch reliability as the bedrock that makes those investments — and India's pitch as a low-cost launch hub — credible.",
        "tags": ["isro", "space-tech", "pslv", "indian-tech", "newspace"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Indian Defence News", "url": "https://www.indiandefensenews.in/2026/06/isro-targets-pslv-relaunch-by-early.html"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/science/isro-lines-up-7-launches-including-uncrewed-gaganyaan-mission-by-march-2026/article.ece"},
            {"name": "Wikipedia — 2026 in spaceflight", "url": "https://en.wikipedia.org/wiki/2026_in_spaceflight"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/PSLV-C50%2C_CMS-01-_Lift-off_003.jpg/1280px-PSLV-C50%2C_CMS-01-_Lift-off_003.jpg",
        "image_caption": "A Polar Satellite Launch Vehicle lifts off from the Satish Dhawan Space Centre at Sriharikota.",
        "image_attribution": "Wikimedia Commons",
        "body": """India's space agency is about to do the most unglamorous thing in rocketry: fly the same machine it has flown more than fifty times, and hope nothing goes wrong.

The Indian Space Research Organisation is preparing to launch its Polar Satellite Launch Vehicle in late June or early July — a return-to-flight that matters far more than its modest payload suggests. The PSLV is ISRO's workhorse, the rocket that turned a government science program into a credible commercial launch provider. It is also the rocket that has failed twice in a row.

## Context & Background

For two decades the PSLV was the rocket you could set your watch by. It carried Chandrayaan-1 to the Moon, the Mangalyaan orbiter to Mars on a famously thin budget, and a record 104 satellites on a single 2017 flight. Its success rate sat above 90 percent, and that reliability is what NewSpace India Limited, ISRO's commercial arm, has been selling to foreign customers paying to ride along.

Then the streak broke. In May 2025 the PSLV failed to inject the Earth-observation satellite EOS-09 into orbit. In January 2026 it stumbled again, unable to place EOS-N1 where it belonged. Both failures occurred during the rocket's third stage — the phase that pushes a payload toward orbital insertion. ISRO has insisted the two faults were unrelated rather than a sign of systemic rot, and has pointed to components it did not manufacture itself, switching vendors for the parts in question.

## Current Developments

Union Minister Jitendra Singh has confirmed the next PSLV flight is targeted for the end of June or early July, calling it a comeback attempt. The agency says foreign clients have not pulled their payloads — a quiet but important vote of confidence, because the alternative is watching satellites migrate to SpaceX's relentlessly cheap rideshare manifests.

The pressure is not isolated to one rocket. ISRO has lined up an ambitious 2026: roughly 18 launches, the human-rated LVM3 for the first uncrewed Gaganyaan test flight carrying the Vyommitra humanoid robot, and a transition toward an industry-built PSLV manufactured by an HAL–L&T consortium under a technology-transfer deal. India's private sector is moving in parallel — Skyroot Aerospace is preparing the maiden orbital flight of its Vikram-I rocket, with the payload fairing already at Sriharikota.

## Diaspora Impact

For the Indian diaspora, this is no longer abstract national pride. Diaspora capital is flowing into Indian space startups: Skyroot just crossed unicorn status with backing from GIC, BlackRock and the founders of Swiggy, and NRI angels and funds are increasingly visible on cap tables from Agnikul to Dhruva Space. The entire investment thesis rests on a simple assumption — that India can put things into orbit reliably and cheaply.

A third consecutive PSLV failure would undercut that thesis at exactly the moment private players are trying to raise their next rounds and sign their first international contracts. A clean flight does the opposite: it reassures the foreign satellite operators NSIL courts, validates the low-cost-launch story diaspora investors are betting on, and buys ISRO room to focus on the bigger prize — putting Indian astronauts in orbit in 2027.

## What's Next

Watch the third stage. That is where both failures happened, and it is where a watching industry — domestic and diaspora — will be holding its breath. A countdown that ends in orbit restores a 90 percent reliability record and the commercial momentum behind it. Anything else turns a string of bad luck into a pattern, and patterns are what scare away the customers and capital India's space ambitions now depend on."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Won't Legalize Crypto, but It Just Made the Paperwork Punishing. NRIs With Wallets, Take Note.",
        "subheadline": "New penalties under the Income-tax Act took effect in April, and exchanges are scrambling to automate compliance. The 30% tax and 1% TDS aren't going anywhere — and the reporting net is tightening around anyone with an Indian tax footprint.",
        "slug": make_slug("india-crypto-tax-reporting-penalties-vda-nri-investors"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "NRIs who trade crypto or hold Indian wallets face a flat 30% tax, 1% TDS and now stiff reporting penalties — a compliance burden that quietly shapes whether the diaspora keeps its digital assets onshore or offshore.",
        "tags": ["crypto", "web3", "fintech", "india-regulation", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/money-and-banking/zebpay-partners-with-koinx-to-simplify-crypto-tax-reporting-for-users/article.ece"},
            {"name": "CoinDesk", "url": "https://www.coindesk.com/policy/2026/02/02/india-crypto-budget-2026"},
            {"name": "Mint", "url": "https://www.livemint.com/money/personal-finance/itr-2026-bitcoin-crypto-itr-2-itr-3.html"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7267491/pexels-photo-7267491.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A stack of Bitcoin tokens, the kind of digital asset India taxes at a flat 30 percent.",
        "image_attribution": "Pexels",
        "body": """India has settled on a curious crypto policy: it will not ban digital assets, it will not legitimize them, and it will tax and document them until trading them feels like filing for a mortgage.

This week ZebPay, one of India's oldest crypto exchanges, announced a partnership with the tax-software platform KoinX to let users generate compliance reports without leaving the app. It is a small product update with a large subtext: the cost of staying compliant in Indian crypto has risen to the point that exchanges now compete on how painlessly they can help you do your taxes.

## Context & Background

India's crypto regime rests on two punitive pillars introduced in 2022. Gains from virtual digital assets — the official term for cryptocurrencies and NFTs — are taxed at a flat 30 percent, plus cess, with no distinction between short- and long-term holdings and no ability to offset losses against gains. On top of that sits a 1 percent tax deducted at source on transfers, designed less to raise revenue than to create a paper trail of every trade.

The industry has argued for years that this framework strangles liquidity and pushes Indian traders toward offshore platforms. The government's reply has been consistent: the friction is the point. New Delhi leans toward not legislating formal crypto regulation, preferring partial oversight through registration and taxation rather than the legitimacy that full regulation might confer.

## Current Developments

The 2026 Union Budget left the 30 percent tax and 1 percent TDS untouched — but sharpened enforcement. Under new provisions in the Income-tax Act, 2025, reporting entities such as exchanges that fail to file required statements on crypto transactions face a penalty of 200 rupees per day for as long as the lapse continues. File inaccurate or misleading information, or fail to correct it in time, and a flat 50,000-rupee penalty applies. These took effect on April 1.

The Central Board of Direct Taxes has signaled it is watching the market evolve, particularly crypto derivatives, which currently sit outside the tax net and which officials say they will study before acting. For now, individual filers must declare crypto income in the dedicated "Schedule VDA" of their returns, using ITR-2 or ITR-3 — the simplest ITR-1 form does not even contain the field.

## Diaspora Impact

For the Indian diaspora, this is a quietly consequential story. Many NRIs maintain Indian bank accounts, hold residual tax obligations, or trade on Indian exchanges where the rupee on-ramp is convenient. The flat 30 percent rate, the un-offsettable losses and the 1 percent TDS already make Indian crypto activity expensive relative to jurisdictions like the United States, where capital-gains treatment and loss harvesting apply. The new reporting penalties add a layer of administrative risk on top.

The practical effect is a slow sorting: diaspora investors with meaningful crypto exposure increasingly keep it on US or offshore platforms governed by friendlier rules, while Indian-resident family members shoulder the heavier domestic regime. For an NRI helping aging parents manage finances back home, or holding a legacy wallet on an Indian exchange, the message is to get the Schedule VDA paperwork right — because the cost of getting it wrong just went up.

## What's Next

The open question is crypto derivatives. The CBDT has flagged them as the next frontier, and how India taxes futures and options on digital assets will signal whether the regime keeps tightening or finally finds an equilibrium. Until then, the safest assumption for anyone with an Indian crypto footprint is that the documentation burden only grows — and that the next exchange feature you see will be another tool to help you survive it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Every Tech Boss Says AI Will Gut Entry-Level Jobs. The CEO Who Employs 350,000 People Is Hiring 20,000 Graduates Anyway.",
        "subheadline": "Cognizant's Ravi Kumar S. is betting against the doom consensus — and the bet runs straight through India's campuses, where the company plans 20,000 fresh hires in 2026 even as it restructures.",
        "slug": make_slug("cognizant-ravi-kumar-graduate-hiring-ai-jobs-india-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Cognizant is one of the largest employers of Indian tech graduates and a major H-1B sponsor; its contrarian hiring bet directly shapes the career ladder that funnels Indian engineers toward the diaspora.",
        "tags": ["cognizant", "indian-tech", "ai-jobs", "it-services", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "People Matters", "url": "https://www.peoplematters.in/news/talent-management/cognizant-hired-20000-graduates-despite-ai-disruption-plans-more-in-2026"},
            {"name": "StockTitan — Cognizant/Pearson study", "url": "https://www.stocktitan.net/news/CTSH/"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/cognizant-ceo-ravi-kumar-bets-on-more-entry-level-hires/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Software engineers collaborate in a modern technology office.",
        "image_attribution": "Pexels",
        "body": """The fashionable view in Silicon Valley is that artificial intelligence is about to hollow out the bottom of the corporate pyramid — that the junior analyst, the entry-level coder and the rookie consultant are the first casualties of a technology that does routine work for free. Cognizant's chief executive thinks that view is, in his word, fearmongering.

Ravi Kumar S., who runs an IT services company with more than 350,000 employees and roughly 27 billion dollars in revenue, says Cognizant hired 20,000 entry-level graduates last year and expects to hire even more in 2026. Speaking at Fortune's COO Summit, he pushed back directly against the warnings of OpenAI's Sam Altman and Anthropic's Dario Amodei. "There was a little bit of fearmongering," he said. "I think there will be more jobs."

## Context & Background

Kumar's optimism is not naive cheerleading; it is a thesis about shape. His argument is that AI handles the routine middle layer of knowledge work — the repetitive tasks that once justified armies of mid-level staff. That compresses the middle of the pyramid but expands the base and the edges. Front-end roles generate prompts, interpret outputs and validate results. Back-end roles handle verification and authentication. The base, in his telling, widens rather than collapses.

This is happening alongside real pain. Cognizant has run layoffs and restructuring under a plan internally tied to its AI transformation, and rivals have cut harder — Oracle shed 19 percent of its workforce, and Tata Consultancy Services trimmed staff last year. Cognizant's twist is that even as it restructures, total headcount has kept climbing; it ended the January–March 2026 quarter with 357,600 employees, up 6,000 from the prior quarter.

## Current Developments

The bet comes with data attached. A Cognizant–Pearson study released on June 18 found that 96 percent of HR leaders expect entry-level jobs to involve managing AI systems, and 94 percent anticipate new AI-created entry-level roles within five years. Tellingly, 67 percent now place more value on liberal-arts degrees, and Kumar describes his ideal hires as a history major who can steer agentic tools or a biology graduate moving into life sciences — not only the classic computer-science recruit.

The hiring is concentrated where the talent is cheapest and deepest. Cognizant added more than 16,000 associates in India in 2025 and is targeting roughly 20,000 campus hires in India in 2026, against about 2,000 in the United States. Over 340,000 of its associates have completed AI skilling as the firm shifts from a linear staffing model to one where humans supervise networks of AI agents.

## Diaspora Impact

For the Indian diaspora, Cognizant sits at a sensitive chokepoint. It is one of the largest employers of Indian engineering graduates and a significant H-1B and L-1 sponsor — a company whose hiring decisions help determine how many young Indians get onto the ladder that, for a generation, has led from a Chennai or Hyderabad campus to a green card and a Bay Area mortgage.

Kumar's contrarian stance matters because the prevailing narrative — that AI ends the entry-level IT job — threatens the very mechanism that built much of the US Indian-American tech community. If he is right, the on-ramp survives in altered form: fewer people doing rote code and ticket triage, more doing AI supervision and validation, with the premium shifting toward judgment and adaptability over raw technical repetition. If he is wrong, an entire pipeline narrows. Either way, the diaspora's next cohort is being sorted on his bet right now.

## What's Next

The proof will be in the margins. Kumar dismisses token-consumption metrics as a vanity number and wants to be judged on project outcomes, delivery speed and client value delivered with a flatter, broader workforce. If Cognizant can show better economics while hiring graduates that its rivals are shedding, it forces a rethink across the consulting sector. If it cannot, the layoffs will outrun the campus offers — and the optimism will read, in hindsight, as exactly the fearmongering's mirror image."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
