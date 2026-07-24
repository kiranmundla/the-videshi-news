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
        "headline": "The PIO Card Is Officially Dead. Hundreds of Thousands of NRIs Still Haven't Switched.",
        "subheadline": "India's free PIO-to-OCI conversion window closed on December 31, 2025 — with no further extension. Now holders must apply for a brand-new OCI card at full price, and the airports are unforgiving.",
        "slug": make_slug("pio-card-dead-oci-conversion-closed-nri-travel"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Hundreds of thousands of NRIs in the US, UK, Canada, Australia, and the Gulf still hold old PIO cards. Since January 1, 2026, those cards are worthless at Indian immigration — no boarding, no entry. The diaspora is now navigating a two-tier system where early converters got a free upgrade and latecomers pay full freight.",
        "tags": ["nri", "diaspora", "pio-card", "oci-card", "india-travel", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Embassy of India, Washington DC", "url": "https://indianembassyusa.gov.in"},
            {"name": "Consulate General of India, Houston", "url": "https://cgihouston.gov.in"},
            {"name": "Whytecroft Ford — OCI Card Rules 2026", "url": "https://www.whytecroftford.com"},
            {"name": "Berry Appleman & Leiden LLP", "url": "https://www.bal.com"},
            {"name": "Consulate General of India, San Francisco", "url": "https://cgisf.gov.in"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/1058959/pexels-photo-1058959.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The Person of Indian Origin card had a good run. Launched decades ago as India's answer to dual citizenship without actually granting it, the PIO card gave millions of overseas Indians a convenient way to visit home — multiple entries, no visa queues, a laminated sense of belonging. Then, on January 9, 2015, the government merged the PIO scheme into the Overseas Citizen of India programme, and the clock started ticking.

For years, that clock was easy to ignore. Extension after extension pushed the PIO travel deadline forward — first to September 2019, then December 2021, then 2023, then 2024. Each time, the Bureau of Immigration quietly accepted the old cards at airports. Each time, the diaspora exhaled.

## The Final Deadline Passed. This Time, It Stuck.

On December 31, 2025, the last extension expired. The Embassy of India in Washington put it bluntly: "No further extension beyond 31.12.2025 will be given." The Indian Consulate in Houston followed up on April 30, 2026, with an even starker notice: "Conversion of PIO card to OCI card has also been discontinued."

That second sentence is the one that stings. The free conversion window — the government's decade-long olive branch to PIO holders — is now closed. Anyone still holding a PIO card who wants to visit India must apply for a brand-new OCI card through VFS Global, the outsourced visa services provider. That means full documentation, full fees, and processing times that can stretch to several months.

## Who Is Actually Affected?

The honest answer: nobody knows the exact number. The PIO scheme issued cards to an estimated several hundred thousand people worldwide, concentrated in the United States, United Kingdom, Canada, Australia, and Gulf states. The government offered free conversion for over a decade. Many converted. Many did not.

The people most likely to be caught are older diaspora members who travel to India infrequently, families who assumed the extensions would continue indefinitely, and those in smaller cities without easy access to VFS centres. There is also a quieter group: people who hold PIO cards for sentimental reasons and never updated their paperwork, not realising the document had become functionally useless.

## The Airport Reality

Since January 1, 2026, airlines are authorised to deny boarding to passengers presenting PIO cards as their India travel document. Indian immigration checkpoints will not accept them. No exceptions, no discretionary waivers.

This is not a hypothetical risk. Legal advisors in the UK report cases of diaspora members being turned away at Heathrow after booking flights to India on the assumption their PIO cards remained valid. The confusion is understandable — for nearly a decade, the government kept extending the deadline, training the diaspora to expect another reprieve.

## What PIO Holders Should Do Now

The path forward is straightforward but not painless. PIO holders must apply for a new OCI card through VFS Global in their country of residence. The application requires a valid foreign passport, proof of Indian origin, photographs, and the applicable fees — typically ranging from $175 to $275 depending on the country, plus VFS service charges.

Processing times vary. The San Francisco consulate's FAQ notes that standard processing can take six to eight weeks, though delays are common during peak travel seasons. Applicants who need to travel to India before the OCI card arrives will need to apply for a standard Indian visa as an interim measure.

For those who hold old, handwritten PIO cards — the earliest generation of the document — the International Civil Aviation Organization's machine-readability requirements add another layer of urgency. These cards are not machine-readable, making them incompatible with modern automated immigration systems regardless of any policy considerations.

## A Lesson in Bureaucratic Inertia

The PIO saga is a case study in how repeated extensions can breed complacency. By pushing the deadline forward six times over a decade, the government inadvertently signalled that the conversion was optional — a suggestion rather than a requirement. When the deadline finally stuck, it caught a significant portion of the diaspora unprepared.

There is also a fairness question that the government has not addressed. NRIs who converted during the free window paid nothing beyond basic processing fees. Those who procrastinated — often for entirely understandable reasons — now face the full cost of a new OCI application. The penalty for delay is financial, and it falls disproportionately on older and less digitally connected members of the community.

India's consular network has stepped up outreach in recent months, with missions in major cities posting reminders on social media and consulate websites. But for a diaspora of over 30 million people, scattered across 200 countries, the message has not reached everyone.

The PIO card is dead. The question for the hundreds of thousands who still hold one is not whether to convert, but how quickly they can navigate the paperwork before the next family wedding, medical emergency, or parent's birthday pulls them home."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "You Moved Abroad and Forgot to Tell Your Bank. That's a FEMA Violation.",
        "subheadline": "Millions of NRIs still operate regular Indian savings accounts years after leaving the country. Under FEMA, every one of those accounts is a compliance problem — and the rules are finally catching up.",
        "slug": make_slug("nri-bank-account-fema-violation-nro-conversion"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Most Indians who move abroad for work or study keep their old savings accounts running — parents use them, EMIs auto-debit from them, fixed deposits sit quietly earning interest. What few realise is that the moment they become an NRI under FEMA, that account is technically illegal. The gap between the law and lived reality is enormous.",
        "tags": ["nri", "diaspora", "fema", "banking", "nro-account", "compliance", "personal-finance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/money/personal-finance/what-happens-to-your-bank-account-after-moving-abroad-and-can-you-use-it-again-if-you-return-to-india-11780244826291.html"},
            {"name": "Livemint — NRE vs NRO for Land Purchase", "url": "https://www.livemint.com/news/trends/nri-explains-why-indians-abroad-keep-delaying-their-return-ill-earn-5-8-crores-11780236175315.html"},
            {"name": "TaxGuru — Sale of Property by NRIs", "url": "https://taxguru.in"},
            {"name": "Whytecroft Ford — FEMA & Repatriation Guide 2026", "url": "https://www.whytecroftford.com"},
            {"name": "Jotwani Associates (Legal Expert Commentary)", "url": "https://www.livemint.com"}
        ]),
        "score_total": 76,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/7821672/pexels-photo-7821672.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Here is the scene that plays out in almost every Indian family with a member abroad: someone moves to the United States, Canada, the UK, or the Gulf for work. They open a local bank account in their new country. Their old State Bank of India or HDFC savings account, the one their parents set up when they were in college, continues to exist. The debit card stays in a drawer in their childhood bedroom. Their mother uses it to pay the electricity bill. A fixed deposit auto-renews every year.

Nobody tells the bank anything. Why would they? The account works fine.

Except under Indian law, it has been illegal since the day they boarded the plane.

## The Rule Most NRIs Don't Know Exists

Under the Foreign Exchange Management Act, a person's residential status determines what type of bank account they are permitted to hold in India. The moment someone leaves India for employment, business, or any purpose that makes them intend to stay abroad for an uncertain period — the legal definition of a Non-Resident Indian — their regular resident savings account must be converted to an NRO (Non-Resident Ordinary) account.

This is not optional. It is not a best practice. It is a legal requirement under FEMA, and failure to comply is a regulatory violation.

"If the bank account holder moved abroad but the account continued to operate during that period, it may amount to a technical FEMA non-compliance because the account was still being used under the wrong residential status," Bhargav Baisoya, a legal associate at Jotwani Associates, told Livemint in a June 2026 report.

The rule applies even when the account holder is not the one making transactions. If a family member in India uses the account — withdrawing cash, paying bills, managing fixed deposits — the violation still rests with the account holder, because the money belongs to someone whose residential status has changed.

## Why Nobody Converts

The reasons are mundane and universal. Converting a savings account to NRO status requires visiting a bank branch or submitting paperwork online, providing a foreign address, and dealing with changed tax treatment on interest income. NRO accounts are subject to Tax Deducted at Source on interest, and repatriation of funds from NRO accounts is capped at $1 million per financial year under the RBI's liberalised remittance scheme.

For many NRIs, especially those who left India as students and gradually became long-term residents abroad, the old savings account represents continuity. It is the account linked to their UPI, their Aadhaar, their old phone number. Converting it means re-linking services, updating records across multiple institutions, and accepting that their relationship with India's banking system has formally changed.

There is also a knowledge gap. Most people learn about visa rules, tax obligations, and health insurance when they relocate. Almost nobody is told about FEMA's bank account conversion requirement. Immigration consultants rarely mention it. HR departments at multinational companies do not include it in relocation packages. The obligation exists in law but not in the lived experience of moving abroad.

## What Happens When Banks Find Out

The enforcement reality is more nuanced than the strict letter of the law might suggest. Baisoya notes that "banks and regulators usually treat genuine oversight differently from deliberate misuse." An NRI with a dormant savings account containing a small balance is unlikely to face penalties. The issue is generally resolved by updating the account status and completing compliance formalities retroactively.

Serious penalties — which can include fines up to three times the amount involved under FEMA — are reserved for cases involving large undisclosed funds, suspicious transactions, or intentional concealment. The Enforcement Directorate, which oversees FEMA compliance, has bigger targets than a software engineer in Seattle whose mother withdraws ₹5,000 a month from his old SBI account.

But the risk is not zero. Banks are increasingly using KYC refreshes and data analytics to identify accounts where the holder's activity pattern suggests they may have moved abroad — passport updates, absence of in-person transactions, IP addresses from foreign locations during net banking sessions. When a bank identifies a potential NRI account operating under resident status, it may freeze the account pending documentation.

## The Return-to-India Complication

For the growing number of NRIs contemplating a return to India — a perennial topic of diaspora debate — the bank account question has a second act. When an NRI moves back and resumes Indian residency, their NRO account should be converted back to a regular resident account.

If the account was never converted to NRO in the first place, the returning NRI faces a paperwork mess: the bank may require an explanation of the gap period, updated KYC documents, and in some cases a declaration that the account was operated in compliance with FEMA during the non-resident period. Most banks resolve this without drama. Some do not.

## What You Should Actually Do

The practical advice is simple, if inconvenient. If you are an NRI and still hold a regular resident savings account in India, contact your bank and initiate the conversion to NRO status. Most major Indian banks — SBI, HDFC, ICICI, Kotak — offer online or postal processes for this. You will need your foreign passport or visa, proof of overseas address, and your existing account details.

If you hold fixed deposits in a resident account, those will need to be converted to NRO fixed deposits or FCNR deposits, each with different tax implications. Consult a chartered accountant familiar with NRI taxation before making changes, particularly if the amounts are significant.

For those who plan to return to India within a year or two, the conversion still matters. FEMA does not have a "short-term exception." The requirement kicks in the day your residential status changes, regardless of your future intentions.

The gap between what the law requires and what millions of NRIs actually do is vast. But as India's banking system becomes more connected, more data-driven, and more aggressive about KYC compliance, that gap is narrowing. The savings account you forgot about is not a ticking time bomb. But it is a compliance issue, and compliance issues have a way of becoming expensive at the worst possible moment."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
