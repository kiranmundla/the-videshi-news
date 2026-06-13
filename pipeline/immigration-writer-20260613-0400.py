#!/usr/bin/env python3
"""
Immigration writer - 2026-06-13 04:00 UTC
Two articles:
1. Iowa's $525M Cognizant deal and the state-level H-1B backlash
2. Rhode Island court vacates USCIS hold policies — implications for Indian immigrants
"""
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
        "headline": "Iowa Just Handed Cognizant Half a Billion Dollars — and Accidentally Made H-1B a Campaign Issue",
        "subheadline": "A Republican candidate for governor is campaigning on banning H-1B outsourcing firms from state contracts. The irony: the sitting governor just gave one the biggest IT deal in Iowa history.",
        "slug": make_slug("iowa-cognizant-h1b-outsourcing-state-contract-campaign"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian IT services companies like Cognizant — which was founded in Chennai and employs tens of thousands of Indian H-1B workers — are becoming explicit political targets in US state elections, signalling that the anti-outsourcing backlash is moving from Washington to statehouses.",
        "tags": ["h1b", "cognizant", "outsourcing", "iowa", "state-politics"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Des Moines Register", "url": "https://www.desmoinesregister.com/story/news/politics/2026/06/11/iowa-it-layoffs-reynolds-aws-cognizant-union-warning/90496471007/"},
            {"name": "East Texas News (AP)", "url": "https://www.easttexasnews.com/"},
            {"name": "The Rural Feminist (Substack)", "url": "https://theruralfeminist.substack.com/"},
            {"name": "USCIS H-1B Employer Data Hub", "url": "https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17581789/pexels-photo-17581789.jpeg",
        "image_caption": "A state capitol dome under clear skies, where outsourcing contracts are becoming election flashpoints",
        "image_attribution": "Pexels",
        "body": """On June 9, Iowa Governor Kim Reynolds announced a deal that will transform how the state manages its information technology: a partnership with Amazon Web Services and Cognizant Government Solutions worth more than $525 million over ten years. Two hundred state IT employees were handed termination notices the same afternoon.

Within hours, the deal had become something Reynolds almost certainly did not intend — a live political test case for how America treats Indian IT outsourcing firms.

## The Contract, the Layoffs, and the Three-Day Deadline

The restructuring is straightforward in outline. AWS will migrate Iowa's data from dozens of on-premise servers to a cloud platform. Cognizant, the New Jersey-headquartered firm with deep roots in Chennai, will take over daily IT operations for the executive branch — managing servers, networks, and helpdesk support for state agencies.

The 192 employees who currently do that work were notified via a blunt letter from the Department of Management director. Shortly after, Cognizant sent its own email: sign a consent form by Friday, June 12 — three days after receiving a termination notice — or forfeit your shot at a job offer. Offer letters would arrive between June 15 and June 25, with salaries, benefits, and job descriptions unspecified until then.

"They're terrified because there is nothing concrete that they know that they're getting," Todd Copley, president of AFSCME Council 61, told the Des Moines Register. Workers will lose access to the Iowa Public Employees' Retirement System, a detail the governor's announcement omitted.

## Enter the H-1B Question

The controversy might have remained a labour dispute. Then Zach Lahn, a Republican candidate for governor, pulled the thread.

Responding to data from LayOffHedge, a layoff tracker, identifying Cognizant as the third-largest H-1B visa employer in the United States and Amazon as the second, Lahn posted on X: "As governor, state contracts will not go to H1B outsourcing firms." He has campaigned on banning H-1B hiring in state government and state universities, and requiring that government contracts disclose how many positions go to Iowans versus foreign workers.

Reynolds fired back within hours: "At no point during our negotiations was it even considered to employ H-1B visa holders. The state's daily IT operations will continue to be supported by Iowans, for Iowans."

## The Illinois Precedent Nobody Wants to Discuss

The reassurance landed differently for anyone who remembers Illinois.

In 2013, Illinois awarded Cognizant a $71.4 million contract to upgrade its Medicaid IT systems. The contract language appeared to prohibit offshoring. Almost immediately after signing, Cognizant filed federal applications for more than 100 H-1B visas designated for the Illinois work and began recruiting programmers in Chennai and Bangalore, holding open interviews for applicants with Medicaid systems experience.

The gap between what was said and what happened is precisely the concern now being raised in Iowa. As one analyst noted, the phrase "Iowa-based workforce" is not the same as "Iowans" — an H-1B visa holder working at a desk in Des Moines is technically an Iowa-based worker.

Democrats have piled on from their own angle. House Minority Leader Brian Meyer called the deal a "government privatization scheme" and noted Cognizant's 2019 settlement of $25 million over Foreign Corrupt Practices Act charges.

## What This Means for Indian Tech Workers

Cognizant was founded in 1994 as an in-house technology unit of Dun & Bradstreet, originally based in Chennai. Today it employs roughly 350,000 people globally, with major operations across India. For decades, the company — alongside Infosys, TCS, and Wipro — has been the pipeline through which hundreds of thousands of Indian engineers have built careers in the United States on H-1B visas.

The Iowa episode is a warning sign for that pipeline. The political attack is no longer coming only from Washington, where Congress debates national fee schedules and lottery rules. It is arriving at the state level, where a single gubernatorial candidate can turn "no H-1B outsourcing firms" into a campaign applause line — and where governors feel compelled to publicly deny any connection to the programme, even when working with companies that depend on it.

For the roughly 730,000 Indian nationals currently in the H-1B system, the Iowa fight illustrates a deepening paradox: the companies that sponsor them are simultaneously indispensable to American IT infrastructure and politically toxic in the communities where they operate.

The contract has not been made public. Iowa's Rural Feminist newsletter has filed a public records request under Iowa Code Chapter 22 seeking the full terms. Until the contract language is released, every assurance about an "Iowa-based workforce" remains exactly what it is: a press statement, not a binding commitment."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Rhode Island Judge Just Wrote the Playbook for Challenging USCIS — Indian Applicants Should Read It",
        "subheadline": "The court vacated Trump's hold on immigration benefits for 39 countries. India is not on the list. The legal reasoning applies to everyone.",
        "slug": make_slug("rhode-island-court-uscis-hold-vacated-indian-applicants"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "While India is not among the 39 travel-ban countries directly affected, the court's reasoning — that USCIS cannot unilaterally freeze adjudications without Congressional authority — provides the legal template that advocacy groups could use to challenge the 'adjustment of status as extraordinary' memo affecting 400,000 Indian green card applicants.",
        "tags": ["uscis", "court-ruling", "green-card", "adjustment-of-status", "travel-ban"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS Official Alert", "url": "https://www.uscis.gov/newsroom/alerts/court-order-on-hold-policies"},
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/"},
            {"name": "Phillips Lytle LLP", "url": "https://www.phillipslytle.com/"},
            {"name": "Lexology (Littler Mendelson)", "url": "https://www.lexology.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29500749/pexels-photo-29500749.jpeg",
        "image_caption": "A federal courthouse in New York, where legal challenges to immigration policies are reshaping the system",
        "image_attribution": "Pexels",
        "body": """On June 12, USCIS posted a terse compliance notice on its website. Three policy memoranda — PM 602-0192, PM 602-0194, and PA 2025-26 — "should be treated as if they are not in effect." The agency added, in a tone that reads more like a protest than an acknowledgment: "USCIS strongly disagrees with the Court's order but will follow its terms pending possible further judicial review."

The court order came from Chief Judge John J. McConnell Jr. of the U.S. District Court for the District of Rhode Island. His June 5 ruling, with final judgment entered on June 11, vacated a suite of Trump administration policies that had frozen work permits, green cards, citizenship applications, and asylum claims for people from 39 countries subject to the administration's travel bans.

India is not on the list. But the legal reasoning in the 135-page opinion is arguably more important for Indian immigrants than the immediate relief it provides to the 39-country nationals it directly affects.

## What the Court Actually Said

The policies in question were adopted by USCIS in late 2025, implementing Presidential Proclamations 10949 and 10998. They paused adjudication of all immigration benefits — work authorisation, green cards, naturalisation — for nationals of countries the administration designated as "high risk." The list includes Iran, Nigeria, Venezuela, and Sudan, among others.

The practical consequences were severe. People already living in the United States lost their jobs when work permits expired and were not renewed. Spouses were separated. Families that had followed every rule of the legal immigration system found themselves, as McConnell wrote, in "indeterminate legal limbo."

The court ruled on four grounds:

First, USCIS lacked statutory authority to implement the challenged policies. The Immigration and Nationality Act gives the president broad power to restrict *entry* of noncitizens — but it does not authorise the government to halt the *adjudication of benefits* for those already present in the country. This is a critical distinction.

Second, the policies violated the Administrative Procedure Act. USCIS enacted sweeping changes without notice-and-comment rulemaking, without adequate explanation, and without assessing the consequences.

Third, the court found that USCIS justified its actions "with pretextual concerns of 'national security' that mask anti-immigrant sentiments that it is forbidden from letting influence its decision-making."

Fourth, the vacatur applies agency-wide. This is not a ruling limited to the individual plaintiffs. Every application affected by these policies must now be processed as though the hold never existed.

## Why Indian Applicants Should Care

The immediate beneficiaries are nationals of the 39 travel-ban countries. But the court's reasoning attacks the legal foundation that USCIS has used to reshape immigration policy through executive action — the same foundation underlying measures that directly affect Indian applicants.

Consider the USCIS memo issued on May 21, 2026, reframing adjustment of status as an "extraordinary" form of relief and pushing applicants toward consular processing abroad. That memo affects an estimated 400,000 Indian nationals with pending green card applications. It was issued without notice-and-comment rulemaking. It was not authorised by any specific statutory provision. And it represents precisely the kind of unilateral policy shift that McConnell's ruling says the APA prohibits.

The Rhode Island decision does not directly vacate the adjustment-of-status memo — different case, different policies, different plaintiffs. But it provides a detailed legal template for challenging it. Immigration attorneys across the country are already studying the opinion for exactly this purpose.

"The court's detailed analysis provides a strong legal foundation that attorneys can draw on when representing affected applicants," noted one immigration law firm's advisory published this week.

## The Government Will Appeal

USCIS has signalled it will seek appellate review. The government's position, articulated by DHS General Counsel James Percival, is that the animus claims are a gambit "from the Left." The administration will likely seek a stay of the order while the appeal proceeds.

This matters because the appellate outcome could determine whether the legal reasoning extends beyond the 39-country context. If the circuit court upholds McConnell's analysis — particularly the distinction between restricting entry and freezing adjudications — it becomes binding precedent that could reshape how courts evaluate USCIS policy changes affecting all immigrant categories, including the employment-based backlog that traps Indian applicants for decades.

The travel bans themselves remain in effect. The court was careful to distinguish between the proclamations restricting entry (which it left untouched) and the USCIS policies freezing adjudications for people already inside the country (which it struck down). For Indian applicants, this distinction is everything: the adjustment-of-status memo operates in the same space — not at the border, but inside the bureaucracy.

## What Happens Next

In the short term, USCIS must resume processing the frozen applications. The compliance notice says updated instructions are forthcoming. For the approximately 39 countries affected, this means work permits that should have been renewed months ago will finally be adjudicated.

For Indian immigrants, the short-term impact is indirect but strategically significant. The legal community now has a federal court opinion that says USCIS cannot use executive proclamations as authority to unilaterally halt the processing of immigration benefits. That principle does not stop at the borders of the 39-country list. It applies wherever USCIS has adopted policy changes without the procedural safeguards that the law requires.

The Rhode Island decision may have been written for 39 countries. But its legal logic was written for everyone stuck in the system — and that includes the hundreds of thousands of Indian professionals who have been waiting, in some cases for over a decade, for an agency that keeps finding new reasons not to act."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
