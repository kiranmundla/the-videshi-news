#!/usr/bin/env python3
"""NRI World writer — 2026-07-12 01:00 PT run. Two articles."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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


# ──────────────────────────────────────────────
# Article 1: CBDT AIS Foreign Financial Info
# ──────────────────────────────────────────────

article1_body = """India's Central Board of Direct Taxes has made a move that every NRI with a bank account, mutual fund holding, or rental income back home needs to understand. As of a July 8 order, the CBDT has authorised the Director General of Income-tax (Systems) to upload financial information received from foreign governments into taxpayers' Annual Information Statement — the digital tax dossier that the Income Tax Department uses to cross-verify returns.

In plain terms: if you hold a savings account in New York, a pension fund in London, or a brokerage account in Toronto, India's tax authorities can now display that information right next to your domestic PAN-linked records. The data flows through the Automatic Exchange of Information framework, a network of bilateral tax treaties — known formally as Double Taxation Avoidance Agreements — that India has signed with more than a hundred jurisdictions, including the United States, the United Kingdom, Canada, Australia, and the UAE.

## How the Mechanism Works

Under the AEOI framework, participating countries share financial account data with each other annually. India has been *receiving* this data for years. What changed this month is where that data now lives: inside your AIS and Form 26AS, the two statements that the tax department pre-fills before you even open your return.

The CBDT's order specifies that information must be uploaded within 90 days of receipt. For historical data covering January 2022 through December 2024, the upload clock starts from the date of the order itself. For 2025 data onward, the 90-day window begins from the end of the month in which the information arrives from the foreign jurisdiction.

The information will appear through a new Form No. 168, for which the DGIT (Systems) has been directed to prescribe the technical standards and procedures.

## What This Means for NRIs

The practical impact is significant — and the compliance stakes are high. NRIs who are classified as "Resident and Ordinarily Resident" for Indian tax purposes are already required to disclose foreign assets in Schedule FA of their income tax return. But many have relied on the assumption that India's tax department simply could not see their overseas holdings. That assumption is now demonstrably wrong.

"By making foreign financial information readily accessible to taxpayers, the initiative not only enables individuals to reconcile and accurately report their overseas income and assets but also strengthens the Income Tax Department's data-driven compliance framework," said Amit Maheshwari, Managing Partner at AKM Global.

Ashish Mehta, Partner at Khaitan & Co, put it more bluntly: "Taxpayers should expect greater visibility of foreign account and related information already available with the tax department, making timely reconciliation and accurate disclosure even more important."

The timing is deliberate. India recently announced a six-month Foreign Assets Disclosure Scheme under the Black Money Act, offering taxpayers with undisclosed overseas assets a window to come clean at a combined rate of 60 per cent (30 per cent tax plus 30 per cent penalty) for amounts up to one crore rupees. The AIS integration raises the cost of staying silent — if your foreign accounts now show up in your own tax statement, arguing ignorance becomes considerably harder.

## The US–India Compliance Double Bind

For Indian Americans specifically, the move creates an uncomfortable dual-reporting reality. NRIs in the United States are already required to file FBAR reports (FinCEN Form 114) for foreign accounts exceeding $10,000 in aggregate, and Form 8938 (FATCA) for specified foreign financial assets above higher thresholds. Missing either carries penalties that start at $10,000 per violation and can climb to 50 per cent of the account balance.

Now, the same NRI must also ensure that their Indian AIS matches what they have reported — or failed to report — on their US filings. A mismatch in either direction could trigger scrutiny from both the IRS and India's Income Tax Department. Tax advisors are recommending that NRIs proactively review their AIS once the foreign data is uploaded, reconcile it against their ITR filings, and ensure their FBAR and Form 8938 obligations are current.

The message from New Delhi is clear: the era of informational asymmetry between India's tax department and its diaspora's overseas financial lives is ending. The data has always been exchanged. Now it is being displayed."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Tax Department Can Now See Your Foreign Bank Accounts. Here Is What Every NRI Needs to Know.",
    "subheadline": "A CBDT order integrates overseas financial data from over a hundred countries into taxpayers' Annual Information Statements, closing one of the last gaps in cross-border tax visibility.",
    "slug": make_slug("cbdt-ais-foreign-financial-information-nri-overseas-accounts-tax"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "NRIs with bank accounts, investments, or property in India now face unprecedented transparency — their overseas financial information from the US, UK, Canada, and other AEOI countries will appear in their Indian tax records, raising the compliance stakes for the 30-million-strong diaspora.",
    "tags": ["nri", "diaspora", "tax", "CBDT", "AIS", "AEOI", "FBAR", "compliance"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/foreign-financial-information-received-under-tax-treaties-to-be-reflected-in-ais-26-as/article71202299.ece"},
        {"name": "CA Club India", "url": "https://www.caclubindia.com/news/cbdt-authorises-dgit-systems-to-upload-global-financial-information-in-ais-under-income-tax-act-2025-26652.asp"},
        {"name": "Livemint", "url": "https://www.livemint.com/money/personal-finance/nri-rental-income-compliance-tenant-uk-address-tax-id-april-2026-new-income-tax-act-2025-rules-2026-form-145-146-15ca-15cb-11745302200131.html"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Aaykar_Bhavan%2C_Income_Tax_Department%2C_Pune.jpg/1280px-Aaykar_Bhavan%2C_Income_Tax_Department%2C_Pune.jpg",
    "image_caption": "Aaykar Bhavan, the Income Tax Department's office in Pune, India",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}


# ──────────────────────────────────────────────
# Article 2: GFS Galaxy Attack — Indian Seafarer Missing
# ──────────────────────────────────────────────

article2_body = """An Indian national is missing and ten others have been rescued after Iran's Islamic Revolutionary Guard Corps attacked a commercial container ship transiting the Strait of Hormuz on Sunday, in the latest incident to put India's vast seafaring community at the centre of an escalating geopolitical crisis.

The vessel, a Cyprus-flagged container ship named GFS Galaxy, sustained "significant engine-room damage" after what Iran described as a warning shot against a ship travelling on an unapproved route. The US Central Command identified the attack as an IRGC strike and said a civilian crew member was missing. India's Ministry of External Affairs condemned the attack, confirming that 11 Indian nationals were on board and that its embassy in Oman was coordinating with local authorities on the search and rescue.

Hours later, Iran announced it was closing the Strait of Hormuz "until further notice." The United States responded with strikes on approximately 140 Iranian military targets — its third round of strikes this week — hitting missile and drone sites, naval capabilities, and coastal surveillance locations. US Central Command said the strikes were carried out "at the direction of the Commander in Chief" in response to Iran's attack on the GFS Galaxy.

## A Pattern of Risk for Indian Crews

The attack is the latest in a series that has placed Indian seafarers in the crosshairs of the Hormuz standoff. In June, three Indian sailors died when the US struck the oil tanker Settebello off Oman, accusing it of violating Washington's blockade of Iran-linked shipping. India summoned the US chargé d'affaires after that incident and condemned "the targeting of commercial shipping and civilian infrastructure."

Earlier in June, 24 Indian crew members were aboard the tanker Marivex when US forces disabled it for sailing toward an Iranian port. All were eventually rescued, but the incident underscored a grim reality: Indian seafarers, who make up a disproportionate share of the world's merchant marine workforce, are bearing the human cost of a conflict they have no part in.

India has more than 300,000 active seafarers working in global shipping fleets, according to government data — among the largest national contingents in the industry. Many work on tankers and cargo ships that transit the Gulf of Oman and the Strait of Hormuz, through which roughly 20 per cent of the world's oil supply flows. The Forward Seamen's Union of India has repeatedly called for stronger protections, arguing that both the US and Iran know the nationalities of crew members on targeted vessels.

## The Diaspora Dimension

The crisis reverberates far beyond the ships themselves. Indian maritime families — concentrated in coastal states like Maharashtra, Gujarat, Kerala, Tamil Nadu, and Andhra Pradesh — live with a particular form of anxiety that most of the diaspora never encounters. When a vessel is struck, information is scarce and slow. Communication systems go down. Families learn from news reports before they hear from shipping companies.

After the Settebello attack, the family of Shivanand Chaurasia — one of the three sailors who died — told reporters he had called home just days before the strike to say everything was fine. He was from Deoria, Uttar Pradesh. The other two victims hailed from Himachal Pradesh and Andhra Pradesh. Indian Shipping Minister Sarbananda Sonowal called their deaths "a profound loss to our maritime family."

The GFS Galaxy attack brings the number of Indian-crewed vessels struck in the Hormuz standoff to at least four since April, when the US began its blockade of Iranian shipping. India has sought to walk a diplomatic tightrope — maintaining its position against attacks on commercial vessels while preserving its relationships with both Washington and Tehran.

## What Comes Next

With Iran's closure of the Strait of Hormuz — even if temporary or partial — the risks for Indian seafarers are likely to intensify. Ships rerouting around the strait face longer journeys and higher insurance premiums. Those attempting passage face the possibility of being caught between Iranian naval forces enforcing closure and US forces enforcing their blockade.

India's foreign ministry has called for "dialogue and diplomacy" to restore stability to the region. For the families of the missing sailor from the GFS Galaxy — and for the thousands of Indian seafarers still at sea in the Gulf — diplomacy cannot come soon enough."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "One Indian Sailor Missing, Ten Rescued After Iran Strikes Container Ship in the Strait of Hormuz",
    "subheadline": "The attack on the GFS Galaxy is the fourth time in three months that a vessel with Indian crew has been hit in the Hormuz standoff. India's 300,000-strong seafaring community is running out of safe passage.",
    "slug": make_slug("gfs-galaxy-iran-attack-indian-seafarer-missing-hormuz-strait"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian seafarers — over 300,000 strong — are disproportionately exposed to the Hormuz standoff. Four ships with Indian crews have been struck since April. Maritime families in coastal India and across the diaspora live with a unique anxiety each time a vessel is hit.",
    "tags": ["nri", "diaspora", "seafarers", "Strait of Hormuz", "Iran", "GFS Galaxy", "Indian Navy", "maritime"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/one-indian-national-missing-after-attack-vessel-off-oman-foreign-ministry-says-2026-07-12/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/07/12/world-news/iran-attacks-ship-announces-strait-of-hormuz-is-closed-and-us-strikes-back-in-response/"},
        {"name": "Reuters (Settebello)", "url": "https://www.reuters.com/world/india-demands-end-us-attacks-ships-after-three-sailors-killed-2026-06-12/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/two-indian-sailors-dead-chief-engineer-missing-after-attack-on-vessel-near-hormuz-seamens-union/article71111903.ece"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/Flickr_-_Official_U.S._Navy_Imagery_-_U.S._Navy_ships_transit_the_Strait_of_Hormuz..jpg/1280px-Flickr_-_Official_U.S._Navy_Imagery_-_U.S._Navy_ships_transit_the_Strait_of_Hormuz..jpg",
    "image_caption": "Naval vessels transiting the Strait of Hormuz, where Indian-crewed commercial ships have repeatedly been struck since April 2026",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}


# ──────────────────────────────────────────────
# Insert
# ──────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
