#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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
        "headline": "Britain Spent Years Talking About Its Minorities as One Block. A New Report Says the Indians Quietly Walked Off With the Trophy.",
        "subheadline": "A Policy Exchange study names British Indians the country's most successful ethno-religious group — 71% own their homes — and warns the political class it is reading the diaspora wrong.",
        "slug": make_slug("british-indians-most-successful-ethnic-group-policy-exchange-mints-homeownership"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For 1.9 million British Indians, the report is both flattering and double-edged: it confirms a generational success story while flagging that 'model minority' framing can flatten internal differences and turn a community into a political bargaining chip.",
        "tags": ["nri", "diaspora", "uk", "british-indians", "policy-exchange"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/british-indians-the-most-successful-ethnic-group-in-the-uk/"},
            {"name": "Mint", "url": "https://www.livemint.com/news/indian-community-most-successful-migrant-group-in-the-uk-finds-report-woven-into-the-growth-story.html"},
            {"name": "GOV.UK Ethnicity Facts and Figures", "url": "https://www.ethnicity-facts-figures.service.gov.uk/housing/owning-and-renting/home-ownership/latest/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33372732/pexels-photo-33372732.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A street in London's historic district, where British Indian families increasingly own rather than rent their homes",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """British politics has a habit of bundling everyone who is not white into a single category, debating "ethnic minorities" or "South Asians" as if they were one undifferentiated mass. A report from the think-tank Policy Exchange, drawing fresh attention this week, argues that the habit is not just lazy but actively misleading — and it has a case study to prove it.

The case study is the British Indian community, which the report calls "one of the most successful ethno-religious groups in modern Britain." With a population now exceeding 1.9 million, British Indians are the largest Asian community in the country, and on almost every socio-economic indicator that matters, they sit at or near the top.

## The numbers behind the headline

Start with property, the most British of all measures of arrival. Some 71% of British Indians own their homes, against a national average closer to 63%. They are the ethnic group least likely to live in socially rented housing — a quiet inversion of the stereotype that has clung to immigrant communities for decades. Official census figures put Indian home ownership in England and Wales at 68%, just ahead of the white British rate, depending on how the categories are sliced.

On education, British Indian students rank second among all ethnic groups, trailing only their Chinese peers. The community is heavily over-represented in the professions — medicine, engineering, technology, law — and posts hourly pay rates and employment levels above the national figure. The think-tank's earlier framing, in a study titled *A Portrait of Modern Britain*, described a community "woven into the growth story" of the country rather than perched on its margins.

What gives the findings bite is the political argument layered on top. The report coins the awkward but memorable label "MINTs" — "minorities in towns" — to describe families moving out of the big cities into provincial towns and villages, where they integrate fully with white neighbours rather than clustering. "The rise of MINTs is being driven by aspirational, asset-owning and business-minded British Indian families," the report notes, predicting they will become an "increasingly critical voter constituency" precisely because Britain's electoral battlegrounds are in exactly those provincial towns.

## The flattery and its traps

For the diaspora, this is the kind of write-up that gets forwarded around family WhatsApp groups with a tricolour emoji. It is genuinely earned. The arc — from the dockworkers and shopkeepers of the post-war waves, through the East African Gujaratis expelled in the 1970s, to today's IT consultants and consultant cardiologists — is one of the most documented immigrant success stories anywhere in the West.

But "most successful minority" is a label worth handling carefully. It tends to flatten a community that is anything but uniform: a third-generation Punjabi family in Leicester and a recently arrived software engineer on a skilled-worker visa in Reading have little in common beyond a passport stamp. Aggregate triumph can obscure the strivers and the strugglers who do not fit the narrative.

There is a sharper risk, too. The report itself notes that British Indians believe social class, not race, is the real barrier to success in the UK — a finding that cuts against the dominant grammar of British race politics. When a community is held up as the proof that the system works, its success can be weaponised in arguments it never asked to join, used as a stick to beat other minorities or to dismiss structural disadvantage entirely.

## Why it matters to the diaspora

The practical takeaway is about power, not pride. A community that owns its homes, educates its children to the hilt, and is now spreading into the marginal seats that decide British elections has leverage it has historically been slow to use. British Indians have produced a Prime Minister, a chancellor, and a long bench of MPs across both major parties, yet still tend to under-organise as a voting bloc relative to their numbers.

The report's quiet message to Westminster is that treating "the ethnic minority vote" as a single thing is a strategic error — and that the diaspora is wealthy, dispersed, and increasingly decisive. For a community that spent its first decades in Britain keeping its head down, being told it now sits at the centre of the electoral map is a notable place to arrive. The question the report leaves open is what British Indians choose to do with the spot."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A New Mandir Opens in Oxford This Weekend. Getting There Took Years, a King's Message, and a Lot of Volunteers With Orange Lanyards.",
        "subheadline": "The Oxford Hindu Mandir & Community Centre holds its grand opening on June 21, the latest sign that the diaspora is building permanent institutions, not just renting halls.",
        "slug": make_slug("oxford-hindu-mandir-grand-opening-community-centre-uk-diaspora-temple"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For Oxford's Hindu families, a purpose-built mandir replaces decades of borrowed rooms and improvised festivals — a marker of a community that has stopped seeing itself as temporary and started laying down roots in brick and stone.",
        "tags": ["nri", "diaspora", "uk", "oxford", "hindu-temple", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Oxford Hindu Mandir & Community Centre", "url": "https://oxfordhindutemple.org/grand-opening"},
            {"name": "GOV.UK Ethnicity Facts and Figures", "url": "https://www.ethnicity-facts-figures.service.gov.uk/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35655151/pexels-photo-35655151.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A priest performs aarti with a lit diya, the kind of ceremony that marked the Oxford mandir's opening",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For years, the Hindus of Oxford did what diaspora communities everywhere do before they have a building of their own: they borrowed. Community halls for Diwali, a school gym for a wedding blessing, someone's living room for a weekly bhajan. This weekend, that improvisation comes to an end. On Sunday, June 21, the Oxford Hindu Mandir & Community Centre throws open its doors with a grand opening that has been years in the making.

The day is staged to be a statement, not just a service. It begins not inside but outside, on the Green, with dhol and bhangra and a Kalash Yatra procession — a line of devotees carrying sacred pots — winding its way to the temple, led by the local Nepalese group and accompanied by drummers. Inside, the morning unfolds through the lighting of the diya, prayers welcoming the deities, children performing a Ganesha dance, and a re-enactment of the triumph of Lord Rama, before the whole thing closes with aarti at four in the afternoon.

## A King, an MP, and a High Sheriff

What is striking about the running order is who is on it. The opening ceremony features a message from The King, read by the Lord-Lieutenant, alongside the declaration formally opening the temple. The speeches list reads like a roll-call of the local establishment: Anneliese Dodds, the MP for Oxford East; the High Sheriff of Oxfordshire, Jawaid Malik; the Oxford City Council leader and Lord Mayor; and the chairman of the county's civic and faith groups.

That guest list is the real news. A mandir opening attended by the monarch's representative and the constituency's Member of Parliament is not a community keeping to itself; it is a community being formally folded into the civic furniture of an English city. The temple is being recognised, in the most British of ways, by the people who hand out the recognition.

## The unglamorous business of permanence

The grand-opening page is full of the small, practical details that betray how seriously the organisers take their new responsibility. There are notes on staggered arrivals to manage parking, reminders to stay hydrated in the forecast heat, instructions to queue calmly at the entrance "with dignity, especially families with children and elders," and guidance to note the fire exits and remove shoes before the prayer hall. Volunteers will wear orange lanyards. Donations can be made online in advance or by card on the day.

It is unglamorous stuff, and that is precisely the point. A community renting a hall does not write a safety briefing. A community that owns a building, expects thousands through its doors, and intends to be there for generations does. The afternoon programme — bhajans from Nepalese, Bengali, South Indian and North Indian groups in turn — quietly maps the spread of the congregation it serves, a single mandir holding together regional traditions that back home might worship in entirely separate temples.

## Part of a wider building boom

Oxford's opening does not happen in isolation. Across the English-speaking diaspora, this has been a season of brick-and-mortar milestones — from a $8.5 million Bharatiya Learning Center in Pennsylvania to new Swaminarayan and Hindu cultural centres in the American South. The pattern is consistent: communities that arrived as guests, kept their festivals portable, and assumed they might one day go home are now investing in permanent institutions for children who will not.

For the second and third generations, a building changes the texture of belonging. A child who grows up attending weekend classes, Janmashtami, and a friend's wedding in the same familiar hall inherits a faith with an address, not just a memory passed down at home. The Oxford mandir's organisers have, in effect, bet that their community is staying. This weekend, with dhol on the Green and a message from the King inside, they make that bet public."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "NRIs Sent India a Record $135 Billion. The Catch: Wiring Money the Old Way Quietly Skims Billions Off the Top.",
        "subheadline": "India is the world's largest remittance recipient by a mile, but a thicket of new tax forms and stubbornly high bank-wire fees mean the diaspora keeps leaving money on the table.",
        "slug": make_slug("nri-remittances-record-135-billion-fees-tax-forms-145-146-compliance"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Every NRI who sends money home is part of this $135 billion flow — and most are losing 3-5% per transfer to fees and choosing the wrong account type, even as Delhi piles on fresh compliance paperwork they will have to navigate.",
        "tags": ["nri", "diaspora", "remittances", "finance", "fcnr", "tax"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "VisaVerge / Economic Survey 2025-26", "url": "https://www.visaverge.com/news/india-remittance-trends-2026-fy25-total-hits-135-4-billion/"},
            {"name": "Mint", "url": "https://www.livemint.com/money/personal-finance/sending-money-abroad-2026-income-tax-forms-145-146-foreign-remittances.html"},
            {"name": "The Hindu BusinessLine / SBI Research", "url": "https://www.thehindubusinessline.com/economy/indias-remittances-to-reach-record-140-billion-in-fy26-sbi-research/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5476028/pexels-photo-5476028.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Indian rupee notes and coins, the destination of a record $135 billion in diaspora remittances",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The number is staggering, and India has earned the right to repeat it. Overseas Indians sent home roughly $135.4 billion in FY25, according to the Economic Survey 2025-26 — enough to make India the world's largest remittance recipient for the fourth year running, ahead of Mexico ($68 billion) by a distance that is almost embarrassing. SBI Research expects the figure to push to $137-140 billion in FY26. To put it in perspective, this single private flow is larger than India's net foreign direct investment and larger still than the "hot money" of foreign portfolio investment.

For all the macroeconomic celebration, the story at the level of the individual NRI is less triumphant. Behind the $135 billion sit roughly 18.5 million people making a monthly, deeply personal decision about how to move money that keeps parents comfortable, pays EMIs on apartments, and puts siblings through college. And a great many of them are doing it the expensive way.

## The quiet tax of moving money

The World Bank pegs the global average cost of sending $200 to India at about 4.8% — just under the international 5% target, but a meaningful drag when applied to tens of billions. The gap between channels is the part NRIs underestimate. A traditional bank wire runs 4-6%. A specialist transfer service such as Wise costs roughly 0.9-1.1%. Gulf exchange houses land somewhere in between at 1.5-2.5%.

On a single $5,000 transfer, the difference between a bank wire and a low-cost service can be $150-250. For a family wiring money every month, the annual leakage runs into thousands of dollars — money that simply evaporates into spreads and fees because the sender defaulted to the bank they already knew. Multiply that inertia across millions of households and the diaspora is collectively gifting the financial plumbing a sum that would itself rank as a respectable remittance corridor.

## NRE versus NRO: the other costly default

The second avoidable mistake is structural. NRIs routinely park money in the wrong account type. Income earned abroad belongs in an NRE (Non-Resident External) account, where the rupee deposits and the interest are fully repatriable and tax-free in India. Income earned within India — rent, dividends, a local pension — belongs in an NRO account, which is taxed and has tighter repatriation limits.

The incentive to get it right is real. SBI's NRE fixed-deposit rates have been quoted at 7.15-7.65% for one-to-three-year tenures — tax-free in India and well above what savers earn in the US or UK. Combined NRE and NRO deposits already sit at around ₹18.4 lakh crore, and the government has been dangling dollar-denominated FCNR schemes promising returns near 7% to pull in more. The diaspora that picks the wrong account, or leaves cash idle abroad, is leaving both yield and tax efficiency on the table.

## Now add the paperwork

As if to complicate the calculus, Delhi has been tightening the compliance screws. The Income Tax Department has replaced the long-familiar Forms 15CA and 15CB with new Forms 145 and 146 for reporting foreign remittances. Form 145 is a self-declaration filed by the remitter, capturing the nature of the payment, the amount, the TDS deducted, and full details of both parties — and it must be completed before certain payments to non-residents, foreign companies, or NRIs are processed.

The stated aim is transparency and cleaner tax compliance. The practical effect for NRIs and their families is another layer of forms that banks and authorised dealers may demand before releasing a transfer. Money that used to move on a phone tap now occasionally stalls behind a declaration.

## What it means for the diaspora

The headline flow is a genuine source of strength for India's external accounts, a private safety net more reliable than fickle foreign investment. But the individual lesson runs the other way: the system is not optimised for the sender. The diaspora's record generosity coexists with widespread, fixable inefficiency — overpaying on fees, mis-using account types, and now navigating fresh compliance.

The fix is unglamorous and entirely within each NRI's control: compare the true all-in cost of transfer channels rather than trusting the bank wire, match the account type to the source of the income, and budget time for the new forms. The $135 billion will keep flowing. Whether it arrives with billions skimmed off along the way is, for once, a decision the diaspora gets to make."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
