#!/usr/bin/env python3
"""Immigration writer — 2026-06-12 04:01 UTC batch"""
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
        "headline": "Seven Hundred and Fifty Dollars to Skip the Line — America's New Fast Pass for Visa Interviews",
        "subheadline": "The State Department will let B-1/B-2 visa applicants pay $750 for an interview within ten business days. For Indian families waiting months to visit their children in the US, the maths just changed.",
        "slug": make_slug("750-dollar-fast-pass-visa-interview-state-department"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Directly affects NRI families — parents waiting months for tourist visa interviews to visit children in the US can now pay $750 to get an appointment within 10 days, but with no guarantee of approval.",
        "tags": ["visa", "b1-b2", "state-department", "interview", "consulate", "nri-families"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/news/india/us-visa-update-pay-750-skip-the-queue-11718112000000.html"},
            {"name": "Fast Company", "url": "https://www.fastcompany.com/91350000/us-travel-rule-change-july-750"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/policy/immigration/state-department-750-fee-fast-track-visa-interviews"},
            {"name": "Federal Register", "url": "https://www.federalregister.gov/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/The_United_States_State_Department_Headquarters_Building.jpg/1280px-The_United_States_State_Department_Headquarters_Building.jpg",
        "image_caption": "The U.S. State Department headquarters in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": """Every Indian who has helped a parent apply for a US tourist visa knows the drill. You file the DS-160, pay the $185 fee, and then stare at a calendar that offers interview slots three months out — if you are lucky. At certain consulates, the wait stretches past six months. For the retired couple in Hyderabad who just want to see their grandchild's first birthday in New Jersey, those months are not an abstraction. They are a wall.

Starting July 1, the State Department is selling a way around that wall. For an additional $750 — non-refundable, on top of the $185 base fee — applicants for B-1 and B-2 visitor visas can secure an interview appointment within ten business days. The total outlay: $935, or roughly ₹79,000 at current exchange rates.

## How It Works

The programme, published as a "temporary final rule" in the Federal Register this week, will run as a six-month pilot from July 1 through December 31, 2026. It applies exclusively to B-1 (business) and B-2 (tourism) non-immigrant visas — the category that covers family visits, medical trips, and short business meetings.

Applicants who opt in will be able to jump the queue at selected US embassies and consulates. The State Department has not yet published the list of participating posts, but given the scale of Indian demand — India consistently ranks among the top three countries for US visitor visa applications — at least one Indian consulate is likely to be included.

There is a catch, and it is significant: paying $750 buys you an appointment, not a visa. The State Department's language is explicit — the expedited service "in no way guarantees visa issuance." Applicants will still face the same eligibility screening, the same officer interview, and the same risk of administrative processing delays. If your visa is denied, the $750 is gone.

There is also a speed element. Once an expedited slot opens, the applicant has between five and ten minutes to complete payment. Miss that window, and the appointment is released back into the pool.

## The Revenue Maths

The State Department projects 25,705 applicants per year will purchase the service, generating an estimated $19.3 million in annual revenue. That projection alone tells you the department expects meaningful demand — and it knows exactly where that demand lives.

The timing is not accidental. The pilot launches three weeks before FIFA World Cup matches begin across American stadiums, with over a million foreign tourists expected. It also sits upstream of the 2028 Los Angeles Olympics. The department explicitly cited both events in its Federal Register notice as motivation for testing the service now.

## What It Means for the Indian Diaspora

For NRI families, this creates a two-tier system that was always informal and is now official. Affluent applicants — business travellers, families with dual incomes in the US — can buy their way to a faster appointment. The retired schoolteacher in Pune who saved for a year to visit her son in Dallas is staring at the same $935 price tag and making a harder calculation.

The counterargument is straightforward: the regular appointment system still exists, the $750 is optional, and faster processing at selected consulates could free up capacity for everyone else. The State Department frames this as purely additive — a "premium addition" that supplements, not replaces, the standard track.

But immigration attorneys are already noting the perverse incentive. If expedited appointments consume a meaningful share of interview slots at high-demand posts, the regular wait could quietly lengthen. The State Department has not disclosed how many expedited slots each consulate will offer, nor whether they come from the existing pool or are genuinely incremental.

For now, the programme is a pilot. Whether it becomes permanent depends on demand and, inevitably, on the politics of charging foreign nationals nearly a thousand dollars for the privilege of asking permission to visit. The embassies and consulates participating will be announced before July 1 on travel.state.gov. Indian applicants should watch that page closely — and keep the credit card handy."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Half a Million AI Agents, Half a Million Humans — TCS Just Told You What Happens to the H-1B Pipeline",
        "subheadline": "India's largest IT company says it will have as many AI agents as employees within three years. For the hundreds of thousands of Indians whose American dreams depend on IT outsourcing firms sponsoring their visas, the implications are existential.",
        "slug": make_slug("tcs-ai-agents-h1b-pipeline-indian-it-hiring"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian IT companies are the largest sponsors of H-1B visas. If TCS, Infosys, and Wipro slow hiring permanently due to AI, the entire H-1B pipeline that brings 70% of visa holders to America begins to shrink.",
        "tags": ["h1b", "tcs", "ai", "indian-it", "hiring", "automation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-tcs-chair-says-ai-agents-may-equal-headcount-dampen-hiring-2026-06-09/"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/indias-largest-it-company-to-cut-mass-hiring-as-ai-starts-taking-over-human-work"},
            {"name": "TradeBrains", "url": "https://tradebrains.in/it-stocks-focus-us-court-strikes-down-h1b-fee/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/46/Natarajan_Chandrasekaran_-_India_Economic_Summit_2011.jpg",
        "image_caption": "N. Chandrasekaran, Chairman of Tata Sons and TCS, at an India Economic Summit",
        "image_attribution": "Wikimedia Commons",
        "body": """N. Chandrasekaran does not traffic in speculation. The chairman of Tata Sons, the conglomerate that controls India's largest IT services firm, is the kind of executive who delivers forecasts like weather reports — flatly, with full confidence in the data behind them. So when he told the TCS annual general meeting this week that the company expects to have as many AI agents as human employees within three years, nobody in the room treated it as hyperbole.

TCS currently employs roughly 584,500 people. Do the arithmetic. Chandrasekaran is describing a near future where half a million artificial agents sit alongside half a million humans, collaborating on the software services work that made TCS India's most valuable IT company. "Some of the work being done will go to AI agents," he said. "That will be the nature of the transition that we have to go through not only as a company, as an industry, and as a country."

## The Numbers Already Tell the Story

This is not a pivot announcement. It is the formalisation of a trend already visible in TCS's own headcount data. In the fiscal year ending March 2026, TCS shed 23,000 employees on a net basis. The previous July, it cut 12,000 jobs outright. Chandrasekaran was careful to say TCS does not plan further "downsizing" — but he was equally clear that the era of mass hiring is over.

"We just want to have the right talent," he said, a sentence that sounds anodyne until you consider what "right" means in a company that once recruited 40,000 fresh graduates in a single year. TCS spent ₹1,268 crore on restructuring last year. The restructuring is not done.

The broader Indian IT sector tells the same story at smaller scale. TCS shares have fallen 32% in 2026. The Nifty IT index is down 25%. Infosys, Wipro, and HCLTech are all navigating the same transition — fewer bodies, more automation, lower margins on the traditional labour-arbitrage model that built a $315 billion industry.

## Why This Is an Immigration Story

Here is the part that does not show up in TCS's earnings call but reshapes the lives of hundreds of thousands of Indian professionals in America: Indian IT services companies are, collectively, among the largest sponsors of H-1B visas in the United States. TCS, Infosys, Cognizant, Wipro, and HCLTech together account for a significant share of the roughly 85,000 H-1B petitions filed each year. Indian nationals hold approximately 70% of all active H-1B visas.

If these companies permanently slow hiring, the downstream effect on H-1B sponsorship is mechanical. Fewer hires in India means fewer workers deployed to US client sites. Fewer deployments means fewer H-1B petitions. Fewer petitions means a smaller pipeline of Indian professionals entering the American workforce through the IT services route.

This does not mean H-1B demand disappears — AI companies like Anthropic, OpenAI, and Nvidia are ramping up their own H-1B hiring, as we reported last week. But the nature of the demand is shifting. The traditional path — engineering degree from an Indian university, campus placement at TCS or Infosys, deployment to a US client within two years — is narrowing. The replacement path runs through AI expertise, specialised skills, and direct hiring by American tech firms that are themselves competing fiercely for talent.

## What It Means for Indians Already in the US

For the Indian professional on an H-1B sponsored by an IT services firm, Chandrasekaran's comments carry a specific risk. If your employer is reducing its US onsite footprint, the probability of your role being redesignated, relocated, or eliminated increases. And under current immigration law, you have 60 days after losing your job to find a new sponsor — a window that feels generous until you are inside it.

The irony is bitter. The same week that a federal judge struck down Trump's $100,000 H-1B fee — a ruling celebrated across the Indian IT industry — the chairman of India's largest IT company announced that the industry's fundamental labour model is being replaced by machines. The fee is gone. The jobs may follow.

For the next generation of engineers in Hyderabad, Bangalore, and Pune, the message is unambiguous: the visa to America still exists, but the company that used to hand you one on your first day no longer guarantees to need you at all."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your Green Card Application Just Became 'Extraordinary' — What the USCIS Memo Means for 400,000 Indian Applicants",
        "subheadline": "A May 21 policy memo reframes adjustment of status as an act of 'administrative grace.' For Indian professionals who have waited a decade or more, the shift from routine to exceptional could force them out of the country mid-application.",
        "slug": make_slug("uscis-adjustment-status-extraordinary-memo-indian-green-card"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian green card applicants form the longest backlog in the employment-based system. This memo's push toward consular processing could force hundreds of thousands to leave the US — their jobs, homes, children's schools — to apply from India instead.",
        "tags": ["green-card", "uscis", "adjustment-of-status", "consular-processing", "eb2", "eb3"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/employment-law-compliance/uscis-memo-signals-heightened-scrutiny-adjustment-status-cases"},
            {"name": "Harris Beach Murtha", "url": "https://www.harrisbeachmurtha.com/uscis-adjustment-memo-explained/"},
            {"name": "Beacon Journal", "url": "https://www.beaconjournal.com/story/opinion/2026/06/11/applying-for-a-green-card-just-got-a-lot-more-complicated/"},
            {"name": "NBC Palm Springs", "url": "https://www.nbcpalmsprings.com/2026/06/09/trump-administration-orders-green-card-applicants-to-leave-us/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36984942/pexels-photo-36984942.jpeg",
        "image_caption": "The U.S. Immigration and Customs Enforcement building in Washington, D.C.",
        "image_attribution": "Pexels",
        "body": """For twenty years, the process worked like this: you got your H-1B, your employer filed a green card petition, and when your priority date became current — a wait that for Indian-born applicants now stretches well past a decade — you filed Form I-485 to "adjust" your status from temporary worker to permanent resident. You did it all without leaving the country. It was not easy. It was not fast. But it was, in the bureaucratic sense of the word, routine.

On May 21, USCIS issued Policy Memorandum PM-602-0199 and declared that it is no longer routine. Adjustment of status, the memo says, is "extraordinary relief" — an act of "administrative grace" that "permits applicants to dispense with the ordinary consular visa process." The ordinary path, the memo argues, is for you to leave the United States and apply for your immigrant visa at a US consulate abroad.

The next day, USCIS told reporters that foreign nationals in the US who want green cards would "generally be expected to return home to apply." The Department of Homeland Security walked that back within the week, describing the memo as a reminder of existing discretion. The legal community has been parsing the gap between those two statements ever since.

## What the Memo Actually Does

Read carefully, PM-602-0199 does not repeal any statute, eliminate any green card category, or add a new eligibility requirement. It does not, strictly speaking, bar anyone from filing I-485 inside the United States. What it does is instruct USCIS adjudicators to treat adjustment of status as exceptional rather than default — and to scrutinise each application through a new discretionary lens.

Officers are now directed to consider whether an applicant violated immigration law, made false statements to a government agency, entered the country in a manner inconsistent with their stated purpose, or engaged in conduct after admission that diverged from the terms of their visa. They must weigh family ties, moral character, and immigration history. They are told, implicitly, that the preferred route is consular processing abroad.

The SHRM (Society for Human Resource Management) published the most measured legal analysis: the memo "does not prevent foreign nationals from applying for adjustment of status from within the US and does not restrict USCIS officers from approving adjustment applications." But it "signals that USCIS intends to apply heightened discretionary scrutiny" — focusing on cases where conduct "appears inconsistent with the purpose of their temporary admission."

## Why Indian Applicants Are Uniquely Exposed

No nationality is more exposed to this shift than Indians. The employment-based green card backlog for Indian-born applicants is the longest in the system — EB-2 India priority dates were recently declared "Unavailable" for the remainder of fiscal year 2026, meaning the State Department has issued every available visa in that category. EB-3 India is similarly backlogged. Applicants who filed I-140 petitions a decade ago are still waiting.

These are not undocumented workers. They are engineers, doctors, researchers, and managers who have maintained valid H-1B status, paid taxes, bought homes, enrolled children in American schools, and followed every rule in a system that asks them to wait fifteen or twenty years for a card that citizens of most other countries receive in under two years. The adjustment-of-status pathway allowed them to file I-485 during that wait — and with it, to obtain work authorisation independent of their employer and advance parole for travel. Without adjustment, they lose both.

If USCIS begins routinely denying or delaying I-485 applications in favour of consular processing, Indian applicants face an impossible choice: leave the country — your job, your mortgage, your child's school — to sit in a consular queue in Mumbai or Chennai, or stay and risk a denied application with no in-country fallback.

## The Legal Landscape

Immigration attorneys are divided on how aggressively the memo will be applied. The statutory text of Section 245 of the Immigration and Nationality Act allows anyone "lawfully admitted for temporary resident status" to apply for adjustment. Congress has expanded that eligibility repeatedly over the decades, adding exceptions for lapsed visas, special immigrant juveniles, and other categories. The legislative history, most attorneys argue, supports a broad reading.

But statutory text and agency enforcement do not always agree. The memo gives individual adjudicators a framework to exercise more discretion — and in the current political environment, "more discretion" tends to flow in one direction. Several law firms are already advising clients with pending I-485 applications to ensure their files are impeccable: no gaps in status, no unauthorised employment, no inconsistencies in prior filings.

Legal challenges are expected. The memo's characterisation of adjustment as "extraordinary" contradicts decades of administrative practice in which USCIS approved hundreds of thousands of I-485 petitions annually as a matter of course. Whether courts will defer to the agency's reinterpretation or strike it down — as they did with the $100,000 H-1B fee — remains an open question.

For the 400,000-odd Indian nationals in the employment-based green card queue, the answer to that question is not academic. It is whether they can keep living in the country they have called home for a decade while they wait for a government that asked them to be patient to finally keep its end of the bargain."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
