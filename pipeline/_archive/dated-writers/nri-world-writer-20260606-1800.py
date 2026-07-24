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
        "headline": "85 Per Cent of Indian Households Have No Will. For NRIs, the Fallout Is Worse.",
        "subheadline": "A new study exposes India's estate planning vacuum just as the country enters its largest-ever intergenerational wealth transfer — and NRIs with assets in two jurisdictions are walking into a legal minefield.",
        "slug": make_slug("india-will-crisis-nri-estate-planning-inheritance"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NRIs with property and financial assets in both India and their country of residence face the worst consequences of India's will-making deficit — cross-border probate, FEMA complications, frozen NRO accounts, and family disputes that span continents and legal systems.",
        "tags": ["nri", "diaspora", "estate-planning", "inheritance", "will", "property", "fema"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/money/personal-finance/indias-wealth-boom-has-a-problem-84-8-of-households-do-not-have-a-will-study-finds-11780562078877.html"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/"},
            {"name": "PolicyBazaar Estate Planning Guide", "url": "https://www.policybazaar.com/"},
            {"name": "Mondaq", "url": "https://www.mondaq.com/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/18394078/pexels-photo-18394078.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A multigenerational Indian family outdoors — the wealth they build together rarely survives the generation that earned it without a will",
        "image_attribution": "Pexels",
        "body": """India is in the middle of its largest intergenerational wealth transfer in history. The generation that rode the post-liberalisation wave — buying flats in Pune, accumulating gold, opening PPF accounts, investing in mutual funds — is ageing. Their children, many of them settled in the United States, Canada, the United Kingdom, and the Gulf, are about to inherit assets they may never have seen in person.

There is one problem. Almost nobody wrote anything down.

## The numbers are staggering

A study published this week by *1 Finance Magazine* found that 84.8 per cent of Indian households do not have a will. That is not a rounding error. It is a structural failure of financial literacy that cuts across income levels, education, and geography.

More troubling still: 62.5 per cent of respondents said they have no plans to make one. Not "haven't got around to it." Not "plan to do it soon." They simply do not intend to.

The study found that 46.7 per cent of families have never discussed wills, inheritance, or estate planning at all. Only 21.8 per cent have had what the researchers describe as a "detailed conversation." In a country where family is the organising unit of economic life, the silence is remarkable.

## The inheritance paradox

The findings expose a pattern the researchers call the "inheritance paradox." Among those who expect to receive family wealth — people who know, in broad terms, that a flat in Noida or a bank account in Ahmedabad will one day be theirs — 79.8 per cent have not prepared a will of their own. Inheritance, the study suggests, is treated as a passive entitlement rather than an active financial responsibility.

The result is predictable. Nearly one in three households — 30.5 per cent — reported some form of inheritance dispute. Among those, 7.3 per cent described major conflicts that involved legal proceedings, family estrangement, or both.

Here is the grim irony: families that have already experienced a dispute are nearly twice as likely to have a will (54.1 per cent) compared with families that have not (29.7 per cent). Conflict, not prudence, is what finally drives people to a lawyer's office.

## For NRIs, every gap widens

If the domestic picture is bleak, the NRI version is worse. A Non-Resident Indian with assets in two countries faces a tangle of overlapping legal systems, tax regimes, and banking regulations that a missing will turns into a full-blown crisis.

Start with probate. A will executed in the United States is, in theory, valid for Indian property. In practice, it must be probated in an Indian court — a process that routinely takes six months to a year, often longer, and typically requires the claimant to be physically present. For an NRI living in Houston or Toronto, that means repeated trips, mounting legal fees, and months of limbo during which the property sits idle.

Without a will, the picture is grimmer. Indian succession law defaults to the Hindu Succession Act, the Indian Succession Act, or Muslim personal law depending on religion — and none of these default frameworks account for the practical reality of heirs who live 8,000 miles away. An NRI who inherits a property intestate in India must apply for letters of administration, a process that invites every distant relative with a claim to contest the application.

Then there is the money. Under FEMA regulations, NRIs can repatriate up to $1 million per financial year from their NRO account, including sale proceeds from inherited property. But to move the funds, they must file Form 15CA and Form 15CB, the latter certified by a Chartered Accountant. Without a will specifying the inheritance clearly, the documentation chain becomes a bottleneck. Banks freeze accounts. Chartered accountants refuse to certify. And the family's most liquid wealth sits in a regulatory purgatory.

## The dual-will solution nobody uses

Estate planning advisors have long recommended that NRIs maintain two wills — one for Indian assets, governed by Indian law, and one for assets in their country of residence. The Indian will should be registered with the local sub-registrar to strengthen its legal standing. The foreign will should be drafted to explicitly exclude Indian assets, avoiding a jurisdictional clash.

This is not exotic advice. It is standard practice for anyone with cross-border assets. Yet the 1 Finance study suggests that the overwhelming majority of Indians — including those with children abroad — have not taken even the first step.

The consequences are not hypothetical. Property lawyers across India report a steady stream of NRI clients who arrive years after a parent's death, armed with a US passport and a power of attorney, only to discover that a cousin has occupied the ancestral home, a tenant has stopped paying rent, or a sibling has sold the family land using a forged document.

## What changes?

The study's authors argue for introducing estate planning into school curricula — a long-term fix for a problem that is already here. In the near term, the answer is simpler and less comfortable: families need to have the conversation.

For NRIs specifically, the checklist is short but non-negotiable. Draft a will for Indian assets. Register it. Appoint an executor who is physically present in India. Ensure NRE and NRO account nominations are current. And have the conversation — the one about who gets the flat in Bandra, who manages the family farm, and what happens to the gold — before it becomes a courtroom argument.

As Shraddha Nileshwar of 1 Finance put it: "Many families realise the importance of a will only after an inheritance dispute arises. By then, relationships may be strained and assets tied up."

In a diaspora community that has built extraordinary wealth across two continents, the irony is hard to miss. They plan for retirement, for their children's education, for every stock trade and insurance policy. The one thing they do not plan for is what happens to all of it when they are gone."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Jaishankar Convened All Eight US Consulates in New York. The Agenda Was the Diaspora.",
        "subheadline": "India's External Affairs Minister chaired a rare all-consulates conference in New York on Saturday, reviewing bilateral ties across nine diplomatic posts — from Atlanta to Seattle — with diaspora support front and centre.",
        "slug": make_slug("jaishankar-consul-generals-conference-new-york-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The conference signals India's deepening investment in its US diplomatic infrastructure specifically to serve its nearly four million-strong diaspora — from consular services and trade portals to political outreach and community safety.",
        "tags": ["nri", "diaspora", "jaishankar", "consulate", "india-us", "diplomacy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
            {"name": "The Indian Eye - Trade Portal", "url": "https://theindianeye.com/"},
            {"name": "Bhaskar English", "url": "https://www.bhaskarenglish.in/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/7b/The_official_portrait_of_External_Minister_Subrahmanyam_Jaishankar.jpg",
        "image_caption": "External Affairs Minister S. Jaishankar, who chaired the all-consulates conference in New York",
        "image_attribution": "Wikimedia Commons",
        "body": """India's External Affairs Minister S. Jaishankar did something unusual on Saturday. He gathered the heads of all eight Indian consulates in the United States — New York, Los Angeles, Seattle, San Francisco, Atlanta, Houston, Chicago, and Boston — along with the Embassy in Washington, for a single conference in New York.

The purpose, as Jaishankar described it in a post on X, was to review "bilateral ties and support for diaspora activities." The phrasing was diplomatic. The signal was not. India is treating its US consular network not merely as a visa-stamping operation but as a distributed infrastructure for managing the world's largest diaspora relationship.

## Nine posts, one agenda

The conference brought together the diplomatic leadership of every Indian mission in the United States. That is nine posts covering a country where nearly four million people of Indian origin live, work, pay taxes, run businesses, and — increasingly — vote.

The review reportedly covered the full spectrum of India-US ties: trade, defence cooperation, technology partnerships, and consular services. But the emphasis on "diaspora activities" is the tell. India's US consulates have quietly expanded their mandate in recent years — from traditional passport and visa services to trade facilitation, community outreach, and political engagement.

The timing is deliberate. India-US bilateral trade hit a record $241 billion over the past year, making the United States India's largest trading partner for the fourth consecutive year. Both countries have committed to an ambitious "Mission 500" target — $500 billion in bilateral trade by 2030. And the interim trade agreement that has been "99 per cent done" for weeks is expected to be finalised imminently, following three days of negotiations in Delhi that concluded on June 4.

## The trade portal and the living bridge

Days before the conference, India's Consul General in New York, Ambassador Binaya Pradhan, used the inaugural GLO-INDIA "Icons of Impact" Gala to unveil a new India-USA Trade Facilitation Portal — a digital platform developed by the consulate to connect Indian exporters, manufacturers, and artisans directly with American buyers.

The portal is designed for small and medium enterprises that lack the resources to navigate cross-border trade independently. It offers virtual exhibitions, webinars on US market compliance, sector-specific networking, and dedicated support for women-led businesses and artisans under the One District One Product initiative.

"Every great trade relationship is, at its heart, a relationship between people," Pradhan told an audience of nearly 200 diaspora leaders, describing the Indian-American community as a "living bridge" between the two democracies.

The phrase is not new — Indian officials have used it for years. What is new is the infrastructure being built to make it literal. The consulates are no longer just processing OCI renewals. They are actively brokering commercial relationships, hosting business delegations, and building digital platforms that position the diaspora as an economic intermediary.

## Jaishankar's broader week

The New York conference capped a packed diplomatic week for Jaishankar. On Friday, he met United Nations Secretary-General António Guterres in New York, discussing the "current global order" and "regional flashpoints" — a diplomatic euphemism that, in June 2026, encompasses the Iran-US hostilities in the Gulf, the ongoing Ukraine conflict, and the aftermath of the Kuwait airport attack that killed an Indian national last week.

Jaishankar's post after the Guterres meeting struck a notable tone: he thanked the UN chief for "clear and consistent support for India's growth and development" — a framing that positions India not as a supplicant but as a country whose growth is a global public good.

For the four million Indians in the United States, the subtext is reassuring. India's diplomatic machinery is not treating them as an afterthought. The consulates are being directed, from the top, to serve diaspora interests — commercial, consular, and political — with a level of coordination that would have been unthinkable a decade ago.

## What it means for NRIs

The practical implications are already visible. Consular camps — where Indian officials travel to cities without a consulate to process passport renewals, OCI applications, and Aadhaar enrolments — have expanded in frequency and geographic reach. The trade portal opens a direct channel for diaspora entrepreneurs. The political engagement, through events like the India Caucus membership drive and the GLO-INDIA gala, gives the community a structured voice in Washington.

None of this is charity. India needs its diaspora. The $135 billion annual remittance flow, the startup founders, the venture capital networks, the political donors, the cultural ambassadors — they are strategic assets that require maintenance. Saturday's conference in New York was, at its core, a maintenance check.

The question for the diaspora is whether the attention translates into better services on the ground. OCI processing times remain frustratingly long. Consular appointment slots in cities like San Francisco and Houston are booked weeks in advance. Property disputes in India remain a nightmare for NRIs trying to navigate the system from 8,000 miles away.

Jaishankar's conference was a statement of intent. The delivery, as always, will be measured in appointment wait times and passport turnaround days — not in posts on X."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
