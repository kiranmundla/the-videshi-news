#!/usr/bin/env python3
"""NRI World Writer - 2026-06-07 06:00 UTC"""
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
        "headline": "A Mother and Son From Haryana Just Became Mayors of Two British Councils. Neither Planned a Career in Politics.",
        "subheadline": "Parveen Rani and Tushar Kumar, who moved from Rohtak to Hertfordshire in 2013, were sworn in as mayors of neighbouring councils within a single week — the first mother-son pair to hold simultaneous mayoral offices in UK history.",
        "slug": make_slug("haryana-mother-son-mayors-hertfordshire-uk-parveen-tushar"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A Haryana family's civic rise in Britain illustrates how diaspora communities are moving from cultural preservation into political leadership — and redefining what representation looks like in local government.",
        "tags": ["nri", "diaspora", "uk", "politics", "haryana", "community-leadership"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Bharat Horizon", "url": "https://bharathorizon.com/mother-son-duo-make-history-as-mayors-in-uk-council/"},
            {"name": "Blitz India Media", "url": "https://blitzindiamedia.com/tushar-kumar-becomes-youngest-indian-origin-mayor-in-uk/"},
            {"name": "Beauty and the Best Magazine", "url": "https://beautyandthebestmagazine.com/from-haryana-to-history-in-hertsmere/"},
            {"name": "NRI Focus", "url": "https://nrifocus.com/nri-watch-indian-origin-mother-and-son-get-elected-as-mayors-in-the-uk-at-the-same-time/"},
            {"name": "BBC", "url": "https://www.bbc.co.uk/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/31282737/pexels-photo-31282737.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A Victorian council chamber in an English town hall, representing Britain's civic tradition",
        "image_attribution": "Pexels",
        "body": """When Sunil Dahiya boarded a flight from Rohtak to London in 2013, he carried no political blueprints. His wife Parveen and their two sons — Tushar, then ten — came with the modest ambitions of most migrant families: stability, education, a fresh start. Twelve years later, Parveen Rani and Tushar Kumar have become the first mother-and-son duo in British history to hold simultaneous mayoral offices in separate councils, a distinction that has drawn attention from Hertfordshire to Haryana.

On 13 May 2026, Tushar Kumar was sworn in as Mayor of Elstree and Borehamwood Town Council, becoming the youngest Indian-origin mayor in the United Kingdom at 23. Seven days later, his mother Parveen Rani was elected Mayor of Hertsmere Borough Council — the first person of Indian heritage ever to hold that office. The twin appointments in neighbouring Hertfordshire councils have been described by civic historians as unprecedented.

## From Rohna to the Council Chambers

The family's ancestral roots trace to Rohna village in Sonipat district, Haryana, though they had been living in Rohtak before emigrating. Sunil Dahiya, a businessman, told PTI that neither he nor his wife had harboured political ambitions when they arrived in Britain. "We had not come with any specific thing in mind," he said. "Tushar was just ten then."

What the family did bring was a deep instinct for community work. Parveen Rani threw herself into local civic life, eventually founding the Hindi Shiksha Parishad UK, an initiative offering free Hindi classes to British-born children of Indian heritage. The programme aimed at a familiar diaspora anxiety: the slow erosion of language across generations. Through cultural events, educational workshops, and persistent outreach, she built a reputation that transcended the Indian community.

Her civic portfolio grew steadily. She served as Cabinet Member for Streetscene, Parks, Leisure and Culture on Hertsmere Borough Council, then as deputy mayor, and later as Global Envoy for Film and Television — a fitting role in a borough that houses Elstree Studios, the birthplace of Star Wars and Indiana Jones.

## The Youngest Mayor in the Room

Tushar's path was no less intentional. A political science graduate from King's College London, he became a councillor at 20 while still an undergraduate — young enough that some constituents initially mistook him for a canvasser rather than a candidate. He joined Elstree and Borehamwood Town Council in 2023 and served as deputy mayor before his elevation.

"The UK has given me so much — it's given me friends, education, healthcare — and I want to give something back," he told the BBC after his swearing-in. His message to young people has been consistent: age is not a qualification for leadership, and waiting for a "right time" is itself a form of disengagement.

Both mother and son were first elected as local councillors in 2023. Their rapid ascent reflects not nepotism or inheritance — British local politics operates on far slimmer margins of patronage — but rather a visible record of community service in a borough where roughly 10 per cent of residents are of South Asian heritage.

## What Diaspora Leadership Looks Like Now

The Rani-Kumar story resonates because it sits at the intersection of several currents shaping diaspora life in 2026. The Indian community in Britain, numbering roughly 1.8 million, has long punched above its weight in business, medicine, and academia. Political representation has lagged, particularly at the local level, where decisions about housing, parks, schools, and streetlighting are made — the mundane infrastructure of belonging.

Tushar's father noted that the family stays rooted in its Haryanvi identity. They visit India regularly. Parveen's Hindi classes were, in one sense, a political act: an assertion that cultural continuity and civic integration are not opposing forces.

The mother-son achievement has drawn congratulations from the Indian High Commission in London and community organisations across the UK. In Haryana, where the family maintains connections, the news has been received with a mixture of pride and bemusement — a reminder that the Indian diaspora's story is no longer only about departure, but about arrival.

## A Borough, Not a Metaphor

It would be easy to read too much symbolism into two mayoral chains draped over members of the same household. But Hertsmere is a real place with real problems — housing pressure, green-belt disputes, the economics of a post-pandemic commuter belt. The test for both mayors will be governance, not narrative.

Still, when Tushar Kumar gavels his first full council meeting and his mother does the same in the chamber next door, something will have shifted. For every NRI child who has sat through a weekend Hindi class wondering what the point was, the answer may be sitting in the mayor's chair."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "It's June and the NRI Tax Clock Is Ticking. Here's Everything That Changed This Year.",
        "subheadline": "Budget 2026 scrapped the TAN requirement for property deals, widened reporting thresholds, and opened a six-month amnesty window for undisclosed foreign assets. For the five million NRIs filing Indian returns, the rules have never been more different — or more forgiving.",
        "slug": make_slug("nri-tax-filing-season-budget-2026-changes-guide"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Every NRI with Indian income, property, or investments must navigate a tax system that changed more in 2026 than in the previous five years combined. The reforms reward compliance and punish ignorance in roughly equal measure.",
        "tags": ["nri", "diaspora", "tax-filing", "budget-2026", "property", "nro-account"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "LiveMint", "url": "https://www.livemint.com/money/personal-finance/itr-want-to-file-income-tax-returns-as-an-nri-check-here-for-i-t-slabs-surcharge-rate-rebate-marginal-relief-11749139032870.html"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/banking/how-rental-income-in-india-can-be-managed-through-an-nro-account"},
            {"name": "CAalley", "url": "https://caalley.com/budget-2026-brings-tax-relief-investment-flexibility-for-overseas-indians/"},
            {"name": "Tata Capital", "url": "https://www.tatacapital.com/blog/tax/union-budget-2026-for-nris/"},
            {"name": "TaxScan", "url": "https://www.taxscan.in/property-transactions-and-income-tax-rules-in-india-compliance-essentials-for-fy-2026-27/451547/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/5476028/pexels-photo-5476028.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Indian rupee notes and coins, representing the financial decisions NRIs face during tax season",
        "image_attribution": "Pexels",
        "body": """June has arrived, and with it the annual ritual that unites every NRI with property, investments, or ageing parents in India: the income tax return. Filing season runs through 31 July for most individuals, but for non-resident Indians scattered across time zones, the real deadline is understanding what changed — because this year, quite a lot did.

The Union Budget 2026, delivered in February, overhauled several rules that directly affect the diaspora's financial relationship with India. Combined with the Reserve Bank of India's equity-limit reforms announced on 5 June and a slew of regulatory simplifications, the 2026 tax year is arguably the most NRI-friendly in a decade. It is also, characteristically, the most confusing.

## The TAN Is Dead. Long Live the PAN.

The single most practical change for NRIs buying or selling property in India: the Tax Deduction and Collection Account Number (TAN) is no longer mandatory for property transactions. From FY 2026-27, PAN-based TDS payment is sufficient.

This sounds bureaucratic. It is not. Any NRI who has tried to sell an inherited flat in Mumbai or buy a plot in Bengaluru knows the TAN requirement added weeks of paperwork, trips to chartered accountants, and occasionally a trip back to India. The PAN-only regime removes one of the most common friction points in cross-border property transactions.

Meanwhile, the Statement of Financial Transactions (SFT) threshold for property deals has risen from ₹30 lakh to ₹45 lakh. Below that line, sub-registrar offices are no longer required to report the transaction to the Income Tax Department. This does not mean the income is tax-free — it simply means fewer automatic flags on smaller deals.

## The Amnesty You Probably Need

Budget 2026 introduced the Foreign Assets of Small Taxpayers Disclosure Scheme (FAST-DS 2026), a six-month window allowing NRIs to regularise previously undisclosed foreign income or assets.

The terms: undisclosed foreign income or assets up to ₹1 crore can be declared by paying 30 per cent tax plus an additional 30 per cent levy, with immunity from prosecution. For assets acquired but not declared up to ₹5 crore, immunity from penalty and prosecution is available for a fee of ₹1 lakh.

The scheme is aimed at a specific and large demographic — young professionals, tech workers, and students who moved abroad, accumulated overseas savings or stock options, and never quite got around to reporting them on their Indian returns. The government's message is clear: come clean now, cheaply, or face the consequences later, expensively.

## The NRO Account: Your Rental Income's Only Legal Home

For the millions of NRIs who hold property in India — whether ancestral homes in Kerala, investment flats in Noida, or holiday apartments in Goa — the NRO (Non-Resident Ordinary) account remains the only compliant channel for receiving rental income.

Rental income earned in India cannot be credited to a regular resident account once an individual becomes an NRI. The resident account must either be closed or converted to an NRO account, and all domestic income — rent, dividends, pension — must flow through it.

The structured pattern works like this: rent arrives from the tenant into the NRO account; property expenses (maintenance, municipal taxes, loan EMIs) are paid from the same account; surplus funds can be maintained to earn interest, transferred abroad within the Liberalised Remittance Scheme limits, or reinvested in Indian financial instruments.

The mistake NRIs most commonly make, according to banking advisers, is maintaining a dormant resident savings account and continuing to receive rent there. The RBI classifies this as non-compliance, and it can complicate everything from future property sales to repatriation of funds.

## The October 28 Trap

This one catches expats every year, and 2026 is no different. India's tax residency is determined by the number of days spent in the country during a financial year (April to March). The threshold is 182 days.

The arithmetic is ruthless: if you leave India after late October, you will have spent more than 182 days on Indian soil that financial year, qualifying as a tax resident. India will then assert jurisdiction over your global income — including the foreign salary you earn in London, Dubai, or San Francisco for the rest of that fiscal year.

The corollary is equally important: even if you leave early enough to maintain NRI status, salary credited to an Indian bank account is treated as "received in India" and pulled into the tax net. The fix is simple but non-obvious: ensure your overseas employer pays into a foreign bank account first. You can always remit to an NRE account later.

## Equity Investment Limits Just Doubled

On 5 June, the RBI announced that individual NRI and OCI investment limits in listed Indian equities under the Portfolio Investment Scheme are being doubled from 5 per cent to 10 per cent. The aggregate ceiling for all NRI investors in a single company rises from 10 per cent to 24 per cent.

The reform is significant on paper. In practice, NRI holdings currently amount to a negligible 0.7 per cent of Sensex market capitalisation, well below even the old limits. Market experts have noted that the bottleneck was never the limit itself but the labyrinthine KYC processes, repatriation paperwork, and taxation ambiguities that discouraged participation.

Whether the raised ceiling translates into actual inflows will depend on whether the government follows through with the process simplifications that experts have been demanding.

## What to Actually Do

For the NRI filing returns this month, the checklist is straightforward but demands attention:

File under the correct regime. The new tax regime under Section 115BAC offers a higher exemption threshold (₹4 lakh) and restructured slabs, but comes with fewer deductions. Run the numbers for both regimes before committing.

Report everything. FBAR and FATCA obligations in the US, UK, and Canada have not softened. The Indian government's new amnesty window is an opportunity, not a permanent fixture.

Update your bank accounts. If you still hold an active resident savings account receiving Indian-source income, convert it to NRO before the financial year ends.

Consider the FAST-DS window. If you have unreported foreign assets, the disclosure scheme's terms are unlikely to get more generous.

The Indian tax system has made genuine concessions to NRIs in 2026. The question, as always, is whether the diaspora notices before July 31."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
