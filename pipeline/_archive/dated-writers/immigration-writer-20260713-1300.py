#!/usr/bin/env python3
"""Immigration writer — July 13, 2026, 1:00 PM PT run."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ---------------------------------------------------------------------------
# ARTICLE 1: The Remittance Tax
# ---------------------------------------------------------------------------

article1_body = """The One Big Beautiful Bill Act arrived with hundreds of pages of tax cuts, Medicaid changes, and border-enforcement funding. Buried inside was a provision that sent the Indian diaspora into a panic: a new excise tax on money sent out of the United States.

The panic was not entirely misplaced. The original House proposal in May 2025 slapped a 5 per cent levy on every dollar a non-citizen wired abroad. For an H-1B professional sending $2,000 a month to parents in Hyderabad or Pune, that would have meant $100 extra per transfer — roughly $1,200 a year in dead-weight cost for the privilege of supporting family.

But the version President Trump signed into law on July 4, 2025, looks almost nothing like the one that launched the scare.

## What actually passed

The final rate is 1 per cent, not 5. The Senate knocked it down from 3.5 per cent in its markup, and the enrolled bill codified the lower figure as Internal Revenue Code Section 4475.

More importantly, the exemptions swallow most of the tax's bite. Transfers made from a US bank account, funded by a US-issued debit card, or charged to a US-issued credit card are entirely excluded. Digital wallets like Apple Pay, Google Pay, and Venmo — which route through bank accounts or cards — fall outside the scope as well.

The tax applies only to cash-based transfers: physical cash, money orders, and cashier's checks handed to a remittance provider like a Western Union or MoneyGram retail counter. The Joint Tax Committee estimates the provision will raise roughly $10 billion over a decade, a figure that implicitly concedes just how narrow the taxable base is.

## Who is actually paying

If you are an Indian-American tech professional wiring money through Wise, Remitly, or your Chase bank account, you owe nothing. If you are funding transfers through Zelle or your bank's international wire desk, you owe nothing. The architecture of modern digital remittances — bank-to-bank, card-to-app — routes around the tax entirely.

The burden lands on lower-income immigrant workers who rely on cash-based services: agricultural labourers on H-2A visas, small-business owners without robust banking relationships, and undocumented workers who lack access to US financial institutions. For them, a 1 per cent levy on a $500 cash transfer adds $5 — not devastating, but cumulative across a year of monthly transfers.

India remains the world's largest remittance recipient, pulling in $129 billion in 2024 according to World Bank data. Roughly 28 per cent of that — about $36 billion — originates in the United States. The Global Trade Research Initiative, a Delhi-based think tank, initially projected a 10 to 15 per cent drop in flows, but that estimate was calibrated to the 5 per cent rate. At 1 per cent with bank and card exemptions, most analysts expect the actual impact on India-bound flows to be negligible.

## The loopholes and the workarounds

The law includes anti-conduit provisions under Section 7701(l) to prevent senders from routing cash through intermediaries to dodge the tax. But the simplest workaround requires no cleverness at all: switch from cash to a debit card at the same Western Union counter. The company's own guidance tells customers they can pay with a debit card at retail locations and skip the tax entirely.

WorldRemit, which processes transfers exclusively through digital channels, has told its customers flatly that they will not be affected. The Asian Development Bank, in research published for its July 2025 outlook, concluded that "the low rate of the tax and the many ways to avoid it will considerably limit its impact."

## Why it still matters

The symbolic weight is harder to dismiss than the fiscal weight. The provision was originally drafted to apply only to non-citizens — a two-tier system that would have taxed an H-1B holder's transfer to India while exempting a naturalised citizen's identical transaction to the same bank account. Lobbying from Mexico and the banking industry shrank the rate and broadened the base to include all senders, but the legislative intent was clear: remittances are a revenue target, and immigrants are the constituency Congress is willing to tax.

For Indian families in the US, the practical advice is simple. If you send money home through a bank, a card, or a digital service, nothing changes. If you use cash at a storefront, consider switching to a card — the same counter, the same service, zero tax. The panic was real. The actual cost, for most NRIs, is not."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Remittance Tax Is Six Months Old. Most NRIs Have Not Paid a Cent",
    "subheadline": "The Big Beautiful Bill's 1 per cent levy on international money transfers exempts bank accounts, debit cards, and credit cards — leaving only cash-based senders on the hook.",
    "slug": make_slug("remittance-tax-six-months-nri-exemptions-cash"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian Americans sending money home through banks or digital services owe nothing under the new remittance tax; only cash-based transfers at storefront services are taxed at 1 per cent.",
    "tags": ["remittance-tax", "big-beautiful-bill", "nri", "money-transfer", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Baker McKenzie InsightPlus", "url": "https://insightplus.bakermckenzie.com/bm/tax/united-states-one-big-beautiful-bill-act-introduces-new-excise-tax-on-remittance-transfers"},
        {"name": "Asian Development Bank Blog", "url": "https://blogs.adb.org/blog/your-questions-answered-what-will-be-the-impact-of-the-new-us-remittance-tax"},
        {"name": "RSM US", "url": "https://rsmus.com/insights/tax-alerts/2025/one-big-beautiful-bill-act-imposes-excise-tax-on-remittances.html"},
        {"name": "Western Union", "url": "https://www.westernunion.com/us/en/remittance-tax.html"},
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6694563/pexels-photo-6694563.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Cash and a smartphone calculator during a financial transaction",
    "image_attribution": "Pexels",
    "body": article1_body,
}

# ---------------------------------------------------------------------------
# ARTICLE 2: The Global Recruitment War for Indian Talent
# ---------------------------------------------------------------------------

article2_body = """Within days of the Trump administration's $100,000 H-1B fee proclamation in September 2025, Germany's ambassador to India posted a video on X that read less like diplomacy and more like a job advertisement.

"Our migration policy is reliable, it's modern, and it's predictable," said Philipp Ackermann. "We do not change our rules fundamentally overnight."

The subtext was unmistakable: if America is going to price you out, we will take you in. And Germany is not the only country making the pitch.

## Germany: the loudest recruiter

Germany's courtship of Indian tech talent is not new, but the urgency has sharpened. The country faces a demographic crisis — nearly a quarter of its working population is within a decade of retirement, the highest ratio in the European Union. Its Skilled Immigration Act, reformed in 2024, streamlined pathways that would have felt alien to anyone familiar with the H-1B lottery.

The numbers tell the story. German universities offer graduates an 18-month post-study job-seeker visa. No lottery, no employer sponsorship, no cap. Graduates can work any job — full-time, in any sector — while searching for a position in their field. Once they land a qualifying role paying at least €45,300 (roughly $49,000), they can switch to an EU Blue Card. From there, permanent residency takes 21 months with basic German language skills, or 33 months without.

Ackermann's video included a number that caught attention: "The average Indian working in Germany earns more than the average German working in Germany." It is a factual claim — Indian workers in Germany cluster in engineering, IT, and pharmaceutical roles that pay above the national median — but it is also a recruiting line aimed squarely at professionals weighing their options.

## The EU Blue Card: no lottery, no drama

The EU Blue Card, available across 25 member states, is the closest European equivalent to the H-1B. The differences are structural. There is no annual cap, no random lottery, and no single-employer tethering that leaves workers vulnerable during layoffs. Holders can move between EU countries after 12 months, bring their families immediately, and access a defined path to permanent residency.

The Observer Research Foundation, in a comparative analysis, noted that the Blue Card offers "lower barriers to entry, a transparent income requirement, and better workplace and family rights" than the H-1B. The trade-off is compensation: US tech salaries, especially in equity-heavy roles, remain substantially higher than European equivalents. A senior software engineer in San Francisco earns roughly double what the same role commands in Berlin or Munich.

But for professionals stuck in the EB-2 India green card backlog — which hit "Unavailable" status in the July 2026 visa bulletin — the calculus has changed. A Blue Card holder can become a permanent resident in Germany in under three years. An Indian national in the EB-2 queue today could wait decades.

## Canada's quieter play

Canada has been less theatrical but no less strategic. Its Express Entry system, which scores applicants on age, education, language ability, and work experience, has consistently drawn from the Indian talent pool. In 2024, India was the largest source country for Canadian permanent residents.

The Canadian pitch is different from Germany's. It leans on proximity to the US market, English as a working language, and a points-based system that rewards exactly the profile the American system now penalises: young, highly educated, mid-career professionals. Canada also offers a two-year post-graduation work permit for international students, no lottery required.

The challenge is saturation. Canada's housing market is strained, and political sentiment toward immigration has cooled. The country reduced its permanent residency targets for 2025 and 2026, and several provinces tightened nominee programs. For Indian workers, Canada remains attractive, but the window is narrower than it was.

## The UK and the Gulf

Britain's Skilled Worker Visa, which replaced the old Tier 2 system, remains an option but a more expensive one. Visa fees, the Immigration Health Surcharge (£1,035 per year), and employer sponsorship requirements add up. The UK's post-study route gives graduates two years to find work (three for PhD holders), but the salary threshold for switching to a Skilled Worker Visa has risen, and political rhetoric around cutting net migration has intensified.

The Gulf states — particularly the UAE and Saudi Arabia — continue to recruit Indian professionals for engineering, healthcare, and financial services roles. Dubai's Golden Visa programme offers 10-year residency for investors, entrepreneurs, and highly skilled workers, though it lacks the social safety nets and labour protections that European systems provide.

## What this means for Indian professionals in America

None of these destinations replicate the combination of compensation, career trajectory, and ecosystem density that the United States offers at its best. Silicon Valley has no true equivalent. The H-1B, for all its dysfunction, remains the gateway to the world's largest and most liquid technology labour market.

But the calculation is no longer just about money. It is about certainty. An Indian professional on an H-1B today faces a wage-weighted lottery for initial selection, a $100,000 fee that is being litigated in two federal circuits simultaneously, a Day 1 CPT crackdown that eliminated one fallback, an EB-2 green card queue that has gone dark until October, and a political environment where "end the H-1B scam" is applause-line material for sitting members of Congress.

Germany offers lower pay but a visa you can plan around. Canada offers proximity but tightening capacity. The EU Blue Card offers mobility across a continent but a smaller tech market.

The competition for Indian talent is no longer theoretical. The question for every professional weighing their options is not whether alternatives exist. It is whether any of them are good enough to leave."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Germany, Canada, and the EU Want the Indian Talent America Is Pushing Away",
    "subheadline": "As the US stacks fees, lotteries, and investigations against skilled workers, rival economies are advertising stability, speed, and an open door.",
    "slug": make_slug("germany-canada-eu-blue-card-indian-talent-recruitment"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals stuck in America's green card backlog and H-1B uncertainty now face active recruitment from Germany, Canada, and the EU, which offer faster residency paths and no lottery systems.",
    "tags": ["eu-blue-card", "germany", "canada", "h1b-alternative", "immigration", "brain-drain"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Marketplace (APM)", "url": "https://www.marketplace.org/2026/02/12/germany-tries-to-attract-tech-workers/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/world/germany-courts-indian-skilled-workers-as-us-h-1b-visa-fee-hike-hits-tech-industry/article69845901.ece"},
        {"name": "Observer Research Foundation", "url": "https://www.orfonline.org/expert-speak/us-h-1b-vs-eu-blue-card"},
        {"name": "Expatrio", "url": "https://www.expatrio.com/studying-in-germany/germany-vs-usa-post-study-work-visa"},
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "An open passport displaying various international travel stamps",
    "image_attribution": "Pexels",
    "body": article2_body,
}

# ---------------------------------------------------------------------------
# Insert
# ---------------------------------------------------------------------------

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  —  {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
