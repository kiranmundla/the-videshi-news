#!/usr/bin/env python3
"""Immigration writer — June 10, 2026 4:00 PM UTC run."""

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
# ARTICLE 1: SAVE America Act — Impact on Naturalized Indian American Voters
# ---------------------------------------------------------------------------

article1_body = """The House of Representatives passed the SAVE America Act on Wednesday by a vote of 218 to 213, sending a bill to the Senate that would require every voter in a federal election to present documentary proof of United States citizenship before registering to vote. For roughly 2.8 million naturalized Indian Americans, the bill introduces a burden that native-born citizens rarely think about: producing a single, hard-to-replace document on demand.

## What the bill requires

The legislation mandates that anyone registering to vote in a federal election must present one of the following in person: a United States passport, a birth certificate listing a place of birth in the United States, a naturalization certificate, or a Consular Report of Birth Abroad. Non-enhanced driver's licences and state identification cards — the documents most Americans reach for at a polling place — would not suffice on their own, because they do not indicate citizenship status.

Mail-in voters would face a parallel requirement: enclose a copy of an eligible identification document when both requesting and returning an absentee ballot.

The bill also directs states to share unredacted voter rolls with the Department of Homeland Security for citizenship verification. There is no federal funding attached to help states build the systems needed to comply.

## Why this matters for Indian Americans

Indian Americans are one of the fastest-growing naturalized citizen groups in the country. The 2020 census counted more than 4.4 million people of Indian origin in the United States, with large concentrations in Texas, New Jersey, California, Illinois, and Virginia. A significant share are first-generation immigrants who obtained citizenship through naturalization.

The naturalization certificate — the document this bill would effectively require — is a single physical copy issued by USCIS. There is no digital equivalent, no wallet card, no app. If it is lost, damaged, or stolen, the replacement process involves filing Form N-565, paying a fee of $555, and waiting 12 to 18 months for a new copy. During that window, a naturalized citizen who had misplaced their certificate could be unable to register to vote.

Name discrepancies add another layer. Indian immigrants who anglicised a first name, adopted a spouse's surname at marriage, or whose birth certificates from India use different transliterations may find that their naturalization certificate does not match their current state identification. Under the bill's language, documents with non-matching names could not be used together for registration.

## The political arithmetic

The SAVE Act passed the House on a straight party-line vote. Speaker Mike Johnson framed it as common sense. "Americans need an ID to drive, to open a bank account, to buy cold medicine," he told reporters. "So why would voting be any different?"

Democrats see it differently. House Minority Leader Hakeem Jeffries called the bill "a desperate effort by Republicans to distract" and said it was designed for "voter suppression, not voter identification."

The bill's path through the Senate is uncertain. It would need 60 votes to clear a filibuster, and Senate Minority Leader Chuck Schumer has said Democrats will block it "under any circumstances." President Trump has signalled he may pursue executive orders on proof-of-citizenship requirements if the Senate fails to act.

## The broader pattern

The SAVE Act arrives at a moment when Indian Americans are exercising political power at record levels. Voter turnout among Asian Americans rose 27 per cent between 2016 and 2020, and Indian Americans now hold seats in the United States Senate, the House, and multiple state legislatures.

For a community that has spent years navigating H-1B lotteries, green card backlogs, and naturalization interviews to earn the right to vote, the prospect of being turned away at a registration desk for lacking the right piece of paper carries a particular sting. The naturalization oath ceremony promises that citizenship is permanent and unconditional. The SAVE Act does not revoke that citizenship — but it does add a documentary checkpoint that falls unevenly on those who were not born with it.

The Senate will decide whether that checkpoint becomes law."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Show Your Papers to Vote — The Bill That Could Trip Up 2.8 Million Indian Americans at the Registration Desk",
    "subheadline": "The House passed the SAVE America Act 218-213, requiring documentary proof of citizenship to register. For naturalized Indian Americans, that means producing a single, irreplaceable document — or losing access to the ballot box.",
    "slug": make_slug("save-america-act-naturalized-indian-americans-voting"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Roughly 2.8 million naturalized Indian Americans would need to produce a naturalization certificate — a single physical document with no digital equivalent — to register to vote in federal elections. Replacement takes 12-18 months and costs $555. Name discrepancies between Indian birth certificates and US identification create additional hurdles.",
    "tags": ["save-act", "voting-rights", "naturalized-citizens", "indian-americans", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "NBC News", "url": "https://www.nbcnews.com/politics/congress/house-passes-save-america-act-sending-trump-backed-election-bill-senate-rcna213730"},
        {"name": "Wikipedia — Safeguard American Voter Eligibility Act", "url": "https://en.wikipedia.org/wiki/Safeguard_American_Voter_Eligibility_Act"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/white-house/4602200/watch-live-trump-ice-cbp-funding-bill/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Capitol_Building_Full_View.jpg/1280px-Capitol_Building_Full_View.jpg",
    "image_caption": "The US Capitol Building, where the House passed the SAVE America Act 218-213",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ---------------------------------------------------------------------------
# ARTICLE 2: 287(g) Expansion — Local Police as Immigration Enforcers
# ---------------------------------------------------------------------------

article2_body = """President Trump signed the Secure America Act into law on Wednesday morning, and buried within its $70 billion in enforcement funding is a provision that could reshape daily life for Indian immigrants in American suburbs: a 1,075 per cent expansion of 287(g) agreements, the programme that deputises local police officers to enforce federal immigration law.

## What 287(g) actually means

Section 287(g) of the Immigration and Nationality Act allows ICE to enter formal agreements with state and local law enforcement agencies. Officers who complete a four-week training course gain the authority to question individuals about their immigration status, issue immigration detainers, and initiate removal proceedings — powers normally reserved for federal agents.

Before this bill, roughly 150 law enforcement agencies across the country participated in 287(g). The new funding is designed to push that number past 1,600. ICE has said the money will cover training costs, overtime reimbursements, and the administrative infrastructure needed to onboard hundreds of new partner agencies simultaneously.

## The geography of risk

The expansion is not abstract. It maps directly onto the suburbs where Indian Americans have built their lives over the past two decades.

Collin County, Texas — home to Frisco and Plano, where the Indian population has grown by more than 200 per cent since 2010 — already sits in a state that has aggressively courted 287(g) partnerships. Middlesex County, New Jersey, which includes Edison and Iselin, has seen local officials debate the programme for years. Alameda County, California, which covers Fremont and the broader Tri-City area, has historically resisted cooperation with ICE — but the new federal funding creates financial incentives that could shift the calculus for cash-strapped departments.

In practical terms, a 287(g) agreement means that an Indian H-1B holder pulled over for a broken tail light in Frisco could be asked about their immigration status by the officer writing the ticket. A family reporting a burglary in Edison could find the responding officer running their information through immigration databases. An expired registration sticker in Fremont could trigger a detainer request before the driver makes it home.

## The legal grey zone

For the roughly 730,000 Indians currently holding H-1B visas, lawful presence is not always easy to prove on the spot. Work authorisation documents do not fit in a wallet. Employment Authorisation Documents expire and sometimes take months to renew. Receipt notices from USCIS are not universally recognised by local officers as proof of status.

Immigration attorneys have long warned that 287(g)-trained officers, while competent in their core policing duties, receive only a fraction of the training that federal immigration agents undergo. The result is a system prone to errors. A 2022 Department of Homeland Security Office of Inspector General report found that some 287(g) partners had issued detainers against United States citizens, and others had failed to follow required notification procedures.

The errors carry disproportionate consequences for legal immigrants. An erroneous detainer can result in hours or days in detention, missed work, and in some cases jeopardised immigration petitions. For someone in the middle of a green card application — a process that, for Indians, can take a decade or longer — even a brief detention can trigger cascading bureaucratic complications.

## What the community can do

Immigration lawyers recommend three practical steps for H-1B holders and green card applicants living in areas likely to see 287(g) expansion. First, carry a photocopy of your current I-797 approval notice and a valid passport at all times. Second, programme the number of an immigration attorney into your phone. Third, know that you have the right to remain silent about your immigration status during a routine traffic stop — but also know that exercising that right may escalate the encounter.

The larger question is whether Indian American civic organisations, which have grown increasingly politically active, will push back against 287(g) adoption in their communities. In places like Edison, where Indian Americans make up more than a third of the population and hold seats on the township council, that pushback has institutional channels. In newer suburban settlements in Texas and Georgia, where the community is large but politically nascent, the response may be slower to organise.

## The new normal

The Secure America Act's funding runs through September 30, 2029. The 287(g) expansion it enables is designed to be permanent — once a local department enters an agreement and trains its officers, the infrastructure persists even if federal priorities shift. For Indian families who moved to American suburbs for good schools, safe streets, and a measure of distance from the immigration system that shapes so much of their lives, that distance just shrank considerably."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "One Thousand Per Cent More Local Cops With Immigration Powers — and They're Coming to Your Suburb",
    "subheadline": "The Secure America Act funds a 1,075% expansion of 287(g) agreements, turning police in Indian-heavy suburbs like Frisco, Edison, and Fremont into de facto immigration enforcers. For 730,000 H-1B holders, a traffic stop just became something else entirely.",
    "slug": make_slug("287g-expansion-local-police-immigration-indian-suburbs"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The 287(g) expansion directly targets suburbs where Indian Americans concentrate — Collin County TX (Frisco/Plano), Middlesex County NJ (Edison), Alameda County CA (Fremont). For 730,000 Indian H-1B holders, a broken tail light or expired registration could trigger an immigration interrogation by a locally trained officer. The programme converts routine encounters with police into potential immigration events.",
    "tags": ["287g", "local-police", "ice", "h1b", "suburbs", "immigration-enforcement", "secure-america-act"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "VisaVerge — Secure America Act Analysis", "url": "https://www.visaverge.com/news/senate-passes-70-billion-secure-america-act-backing-trump-deportation-plan/"},
        {"name": "Associated Press via Audacy", "url": "https://www.audacy.com/kdkaradio/news/politics/immigration-enforcement-funding-trump-congress-republicans-c395a434f47fa41a7131369847091910"},
        {"name": "Washington Examiner — Trump Signs Bill", "url": "https://www.washingtonexaminer.com/news/white-house/4602200/watch-live-trump-ice-cbp-funding-bill/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Immigration_and_Customs_Enforcement_%28ICE%29_Enforcement_and_Removal_Operations_%28ERO%29_in_Los_Angeles%2C_California%2C_June_12%2C_2025_-_70.jpg/1280px-Immigration_and_Customs_Enforcement_%28ICE%29_Enforcement_and_Removal_Operations_%28ERO%29_in_Los_Angeles%2C_California%2C_June_12%2C_2025_-_70.jpg",
    "image_caption": "ICE Enforcement and Removal Operations officers during a field operation in Los Angeles, June 2025",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}

# ---------------------------------------------------------------------------
# Insert articles
# ---------------------------------------------------------------------------

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
