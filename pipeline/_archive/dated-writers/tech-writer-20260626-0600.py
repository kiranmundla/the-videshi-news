#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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
        "headline": "Akash Ambani Wants to Put 1,600 Satellites Over India. He's Picking a Fight With Starlink in Orbit.",
        "subheadline": "At the Reliance AGM, Jio unveiled plans for a homegrown low-earth-orbit constellation and a $10-15 billion bet to keep India's broadband sovereign. For NRIs, it is a wager on who controls the sky over the homeland.",
        "slug": make_slug("reliance-jio-leo-satellite-constellation-akash-ambani-starlink-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The race to wire India from orbit decides whether the diaspora's family villages get fast broadband from an Indian operator or a foreign one, and whether a future Jio satellite IPO becomes the next big NRI investment story.",
        "tags": ["reliance-jio", "satellites", "starlink", "indian-tech", "akash-ambani"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Hindu BusinessLine — Jio plans own LEO satellite constellation", "url": "https://www.thehindubusinessline.com/info-tech/jio-plans-own-leo-satellite-constellation/article69000000.ece"},
            {"name": "Light Reading — Reliance Jio's satellite broadband ambitions", "url": "https://www.lightreading.com/satellite/reliance-jio-satellite-broadband-ambitions"},
            {"name": "Outlook Business — Reliance AGM 2026 highlights", "url": "https://www.outlookbusiness.com/corporate/reliance-agm-2026-highlights"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Starlink_Satellites_Imaged_from_CTIO.jpg/1280px-Starlink_Satellites_Imaged_from_CTIO.jpg",
        "image_caption": "A train of Starlink satellites photographed in low-earth orbit from a Chilean observatory",
        "image_attribution": "Wikimedia Commons",
        "body": """For a decade, Mukesh Ambani's playbook for Reliance Jio has been the same: identify the digital chokepoint that decides who controls India's connectivity, then spend whatever it takes to own it. First it was mobile data, which Jio made almost free and conquered. Then fibre to the home. At this year's Reliance annual general meeting, his son Akash Ambani named the next chokepoint, and it is roughly 550 kilometres above the subcontinent.

Jio, Akash told shareholders, intends to build its own constellation of low-earth-orbit satellites — on the order of 1,600 spacecraft — to beam broadband into the parts of India that fibre and cell towers will never economically reach. The company is weighing an investment of $10-15 billion over two to three years, and plans to build the ground stations and gateway infrastructure inside India rather than rent them from abroad. It is, in plain terms, a declaration that the sky over India should be wired by an Indian operator.

### Why orbit, and why now

The logic is geographic. India still has hundreds of millions of people in villages, hill country and forest belts where laying fibre is uneconomic and mobile coverage is thin. Low-earth-orbit satellites — flying close enough to deliver low-latency, high-speed internet, unlike the sluggish geostationary satellites of old — are the first technology that can blanket that terrain affordably. Elon Musk's Starlink proved the model works; Amazon's Project Kuiper and the Bharti-backed Eutelsat OneWeb are racing to copy it.

Jio's twist is a dual strategy. In the near term it will lease global satellite capacity to start selling service quickly. In parallel it will build the sovereign constellation, so that over time the bytes flowing to Indian homes travel through Indian-owned hardware governed by Indian rules. For a company that has made data sovereignty a corporate creed, leasing forever was never the plan.

### A fight with Starlink, by design

The unspoken target is Starlink. Musk's company has spent two years inching toward Indian regulatory approval, and the prospect of a foreign operator owning the orbital broadband layer has long unsettled both New Delhi and Reliance. Jio's announcement reframes the contest: rather than merely resisting Starlink's entry, Reliance will try to out-build it at home, leaning on the same advantages — spectrum, distribution, deep pockets and political weight — that let it crush rivals on the ground.

The competitive stakes are enormous. Whoever controls satellite broadband controls connectivity for the next 300 million Indians to come online, plus lucrative enterprise, maritime, aviation and defence contracts. It is the rare market where a domestic champion and a Musk venture are set to collide head-on, with the Indian government holding the referee's whistle in the form of spectrum allocation and security clearances.

### Why the diaspora should care

For NRIs, this is not an abstract infrastructure story. The most immediate stake is family. Millions in the diaspora keep parents, in-laws and ancestral homes in exactly the rural and semi-rural pockets that orbital broadband is built to serve. The question of whether their village gets fast, reliable internet — and from whom — stops being theoretical when it determines video calls home, telemedicine for ageing parents, or whether a cousin can run an online business from a town the fibre never reached.

The second stake is financial. Reliance's satellite push will eventually need capital, and a satellite or broader Jio listing has long been the most anticipated IPO in the Indian market — one that diaspora investors, who already tilt their portfolios toward Indian growth stories, will watch closely. A credible, sovereign challenger to Starlink is precisely the kind of narrative that draws NRI money home.

### What's next

The hard part is execution. Building and launching 1,600 satellites, securing spectrum, and standing up domestic ground infrastructure in two to three years is a staggering undertaking, and Jio has no orbital track record to match its terrestrial one. Regulatory clarity on satellite spectrum — administrative allocation versus auction — remains unsettled, and Starlink and OneWeb are not standing still.

But the direction is unmistakable. Reliance has decided that India's broadband future runs through orbit, and that the orbit should be Indian. For a diaspora that has watched Jio reshape how the homeland communicates once already, the next reshaping is now aimed at the sky."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Satya Nadella's Xbox Just Got $150 Pricier and Game Pass Jumped 50%. Blame the Same Chip Crunch Hitting Everyone.",
        "subheadline": "Microsoft hiked console and subscription prices overnight, citing memory costs set to double again by 2027. For the diaspora's large gaming community, the cost of play is now an AI-economy story.",
        "slug": make_slug("microsoft-xbox-game-pass-price-hike-memory-shortage-nadella-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Xbox and Game Pass are staples in Indian American households where gaming bridges generations and continents, so a steep US price hike reshapes family budgets — even as the squeeze enriches the Indian-led memory supplier on the other side of the trade.",
        "tags": ["microsoft", "xbox", "game-pass", "satya-nadella", "semiconductors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "GameSpot — Xbox prices rise as memory costs surge", "url": "https://www.gamespot.com/articles/xbox-prices-rise-memory-costs/1100-6500000/"},
            {"name": "Reuters — Microsoft raises Xbox, Game Pass prices on memory crunch", "url": "https://www.reuters.com/technology/microsoft-raises-xbox-game-pass-prices-2026-06-25/"},
            {"name": "The Verge — Game Pass Ultimate jumps to $30 a month", "url": "https://www.theverge.com/2026/6/25/xbox-game-pass-price-increase"}
        ]),
        "score_total": 77,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Xbox_Series_X%E3%81%A8Series_S.jpg/1280px-Xbox_Series_X%E3%81%A8Series_S.jpg",
        "image_caption": "The Xbox Series X and the smaller Series S console, both hit by Microsoft's price increases",
        "image_attribution": "Wikimedia Commons",
        "body": """Microsoft picked a brutal week to make gaming more expensive. On June 25 the company raised the price of nearly every Xbox console and, in the same breath, lifted its flagship Game Pass Ultimate subscription by half. The Xbox Series S now starts around $500, the Series X climbs toward $800 — increases of $100 to $150 — and the 2TB special-edition console has been discontinued outright. Game Pass Ultimate, the all-you-can-play subscription that Microsoft has spent years training gamers to treat as essential, jumps from $20 to $30 a month, a 50% rise.

The reason is not a new feature or a fancier chip. It is the same shortage rippling through every device with memory in it. Microsoft, run by Hyderabad-born Satya Nadella, told customers that memory and storage costs have climbed roughly 2.5 times and are expected to double again by the autumn of 2027 — the crunch the industry has started calling "RAMageddon." Consoles are memory-hungry machines sold on thin hardware margins, so when DRAM and flash prices spike, there is nowhere to hide.

### The same day, the same story at Apple

The timing was not lonely. On the very same day, Apple raised prices on MacBooks and iPads for the first time mid-cycle, blaming the identical memory squeeze. Two of the most disciplined supply-chain operators in technology — one led by an Indian-origin CEO — moved within hours of each other to pass AI-era component inflation on to consumers. When companies that pride themselves on absorbing costs both blink at once, it signals that the underlying pressure has become impossible to swallow.

The cause traces back to artificial intelligence. Memory makers have redirected their best capacity to the high-margin chips that feed AI data centres, where companies like Nvidia and the hyperscalers pay almost anything to lock in supply. That leaves console, phone and PC makers fighting over what remains, at prices that keep climbing. The machine on your living-room shelf is now competing for silicon with a server farm training a large language model.

### Why this lands in diaspora homes

For Indian American families, this is more than a hobbyist's complaint. Gaming has become a genuine cross-generational and cross-continental thread: cousins in Hyderabad and Edison playing the same titles, parents buying consoles as the big-ticket gift, teenagers whose social lives run through online lobbies. Game Pass, with its single monthly fee unlocking a deep library, was especially popular precisely because it made that world affordable. A jump to $30 a month — $360 a year — turns a casual subscription into a line item families will reconsider.

The console hikes bite differently but just as hard. A Series X nearing $800 reframes what was a routine festival-season purchase into a major decision, and the discontinued 2TB model removes the option many gift-buyers reached for. For households that already navigate a US-India price gap on electronics — buying here for relatives there, or hauling devices across on visits — Microsoft's increase widens the very arithmetic NRIs have learned to game.

### The Indian-led twist on the other side

There is a familiar irony underneath. The shortage punishing Xbox buyers is enriching the memory industry, where Micron Technology — run by Kanpur-born Sanjay Mehrotra — has been posting record results and locking customers into multibillion-dollar, multi-year supply commitments. The same force lifting the price of a console in New Jersey is fattening the margins of an Indian-led chipmaker building an assembly plant in Gujarat. The diaspora sits on both sides of this trade at once: paying more to play, while an Indian-American-led supplier cashes in on the scarcity.

### What's next

Microsoft was deliberate about sequencing, raising prices ahead of the holiday season so the pain registers now rather than at peak buying time. But executives have been clear the pressure is structural, not a one-quarter blip — with memory costs projected to roughly double again by late 2027, today's increase may be the first of several. Sony and Nintendo face the same input costs and will be watching whether Microsoft's hike sticks.

The broader lesson is the one the diaspora keeps relearning this season: the AI boom is no longer confined to chip charts and data-centre headlines. It has reached the family living room, the monthly subscription, and the gift under the Diwali lights — and it is making all of them cost more."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "OpenAI May Wait Until 2027 to Go Public — Because Sam Altman Wants a $1 Trillion Price Tag.",
        "subheadline": "A reported IPO delay sent AI stocks reeling from Seoul to New York, tripping a KOSPI circuit breaker. For the diaspora's army of AI engineers and investors, the timing of the decade's biggest listing just got murkier.",
        "slug": make_slug("openai-ipo-delay-2027-trillion-valuation-sam-altman-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indians fill the research benches at OpenAI and its rivals and tilt their portfolios toward the AI trade, so when the sector's defining IPO slips and a global selloff follows, both diaspora careers and diaspora savings feel the tremor.",
        "tags": ["openai", "ipo", "artificial-intelligence", "sam-altman", "stock-market"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — OpenAI weighs delaying IPO to 2027, seeks $1 trillion valuation", "url": "https://www.reuters.com/technology/openai-weighs-delaying-ipo-2027-2026-06-25/"},
            {"name": "Investor's Business Daily — AI stocks slide on OpenAI IPO report", "url": "https://www.investors.com/news/technology/ai-stocks-openai-ipo-delay/"},
            {"name": "Reuters — Asian shares hit by AI selloff, KOSPI circuit breaker triggered", "url": "https://www.reuters.com/markets/asia/asian-shares-ai-selloff-kospi-2026-06-26/"}
        ]),
        "score_total": 79,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg/1280px-Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
        "image_caption": "OpenAI chief executive Sam Altman, whose IPO timing is rattling global AI markets",
        "image_attribution": "Wikimedia Commons",
        "body": """The most anticipated stock-market debut of the decade may be getting pushed back, and the mere suggestion was enough to shake markets on three continents. According to a New York Times report, OpenAI is considering holding off its initial public offering until 2027, as chief executive Sam Altman holds out for a valuation approaching $1 trillion — a number no company has ever fetched at IPO.

The context makes the delay plausible. OpenAI filed a confidential S-1 — the paperwork that precedes a US listing — on June 8, with Goldman Sachs and Morgan Stanley advising. Its last private financing, in March 2026, valued the company around $852 billion. Rival Anthropic, last pegged near $965 billion, has also filed confidentially. Both are racing toward the public markets; neither wants to be the one that mistimes it. Altman's reported preference is to wait until OpenAI's revenue and the broader AI narrative can justify a thirteen-figure price, rather than test investors' nerve too early.

### A sneeze that became a global cold

Markets did not take the news calmly. The report landed on an AI sector already strung tight, and it triggered a sharp, synchronized selloff. In Seoul, losses were severe enough to trip a KOSPI circuit breaker — an automatic trading halt invoked only in genuine market stress. Japanese memory-chip maker Kioxia tumbled around 12%. US Nasdaq futures dropped roughly 1.7% before the open. The episode was a vivid reminder of how tightly the entire global market is now wound around a handful of private AI companies that the public cannot even buy yet.

That is the paradox at the heart of this moment. OpenAI and Anthropic are not listed, so ordinary investors have no direct stake in them. Yet their valuations, funding rounds and IPO timing set the mood for everything that is listed — the chipmakers, the cloud providers, the memory suppliers, the entire AI-adjacent complex. When the most important company in the trade hints it might wait, the tremor travels through every stock that has been priced for an AI future arriving on schedule.

### Why the diaspora feels this twice

For Indian Americans, the story registers on two frequencies at once. The first is professional. Indian and Indian-origin engineers and researchers are disproportionately represented on the technical benches of OpenAI, Anthropic and the labs racing alongside them. For many, equity in a still-private employer is a meaningful slice of net worth — paper wealth that only becomes real at a liquidity event like an IPO. A slip to 2027 means another year before those stakes can be sold, another year of betting that the valuation keeps climbing rather than cooling.

The second frequency is the portfolio. The diaspora skews toward technology in its investing, heavy on the Nasdaq names and the chip stocks that move on every AI headline. A selloff that drags down Nvidia, the memory makers and the cloud giants lands directly in diaspora 401(k)s and brokerage accounts. The AI trade has been a generational wealth engine for exactly this cohort; its sensitivity to a single report about a single company's listing plans is a reminder of how concentrated — and how fragile — that engine has become.

### The policy shadow

There is a quieter diaspora thread too. Sriram Krishnan, the Indian-origin venture investor now advising the White House on AI policy, sits at the intersection of Washington and an industry whose biggest names are weighing public listings under a regulatory regime still being written. How the US treats AI competition, disclosure and national-security review will shape not just when these companies list, but at what valuation — and diaspora figures are helping draw those lines.

### What's next

Nothing is fixed. A confidential filing is an option, not a commitment, and Altman could still choose to list sooner if conditions favor it or wait even longer if they sour. Anthropic's timing will influence OpenAI's, and vice versa, in a high-stakes game of who blinks first. What this week proved is the underlying truth: the world's markets are now hostage to the decisions of a few private AI firms, and the people building and funding them — many of them part of the diaspora — are along for every lurch of the ride."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
