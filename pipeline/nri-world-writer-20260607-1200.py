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
        "headline": "A Chhattisgarh Boy Who Worked Night Shifts at 17 Just Wrote Houston's Largest Hospital Cheque.",
        "subheadline": "Brij and Sunita Agarwal's $5.5 million gift to St. Luke's Health-Sugar Land will rename the patient tower and fund a primary care clinic in one of Houston's fastest-growing — and most underserved — suburbs.",
        "slug": make_slug("brij-sunita-agarwal-houston-hospital-donation-sugar-land"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Agarwals' trajectory — from a small town in Chhattisgarh to running 150 restaurants across Texas and writing a record hospital cheque — embodies the Indian-American philanthropy boom that now exceeds $5 billion annually, reshaping the healthcare and education infrastructure of the very suburbs the diaspora has made home.",
        "tags": ["nri", "diaspora", "philanthropy", "healthcare", "houston", "indian-american"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AInvest", "url": "https://www.ainvest.com/news/indian-american-couple-donates-5-5-million-expand-healthcare-infrastructure-houston-2606/"},
            {"name": "Bharat Horizon", "url": "https://bharathorizon.com/indian-american-couple-donates-5-5-million-for-houston-healthcare-expansion/"},
            {"name": "GG2", "url": "https://gg2.net/indian-american-couple-gives-1-million-to-us-university/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Memorial_Hermann_Sugar_Land_Med_Center.jpg/1280px-Memorial_Hermann_Sugar_Land_Med_Center.jpg",
        "image_caption": "A medical centre in Sugar Land, Texas, one of Houston's fastest-growing suburbs",
        "image_attribution": "Wikimedia Commons",
        "body": """The numbers on the cheque are large: $5.5 million, the single biggest donation St. Luke's Health-Sugar Land Hospital has ever received. The story behind them is larger still.

Brij Agarwal arrived in Houston from Chhattisgarh in 1979, a 17-year-old with no money and limited English. He attended night classes at the University of Houston while working full-time during the day — the classic immigrant arithmetic of trading sleep for opportunity. Three decades later, he runs the VKC Group, a hospitality empire that operates more than 150 restaurants across Texas, Colorado, and New Mexico.

Now Agarwal and his wife Sunita have redirected a portion of that success into the medical infrastructure of the suburb they call home.

## What the money will do

The $5.5 million will fund two things. First, an expansion of clinical programmes at St. Luke's Health-Sugar Land, a hospital that serves one of Houston's fastest-growing corridors. Second — and arguably more consequential — the establishment of a primary care clinic in a nearby community where access to a family doctor remains stubbornly difficult.

Sugar Land has transformed over the past two decades from a quiet exurb into a sprawling city of more than 110,000, with a significant Indian-American population. Growth has outpaced healthcare infrastructure, a gap the Agarwals' gift is designed to narrow.

In recognition, the hospital's main patient tower and pavilion will be renamed in the family's honour.

## A pattern, not an anomaly

The Agarwals are not first-time philanthropists, and this is not an impulse donation. In 2022, they pledged $1 million to UH Sugar Land to equip a manufacturing laboratory and establish an advanced design centre. Through matching programmes — the George Foundation and the Texas Research Incentive Programme — that million tripled to $3.5 million in total impact. They had earlier helped fund the first UH Sugar Land building and created a Presidential Endowment for engineering scholarships.

The pattern is deliberate: invest where you live, multiply through institutional leverage, and target the infrastructure that immigrants and their children actually use — universities, hospitals, clinics.

"I would not have graduated from college if it wasn't for the UH System," Agarwal has said. "That is why I am so passionate about supporting UH."

## The broader current

Indian-American philanthropy now exceeds $5 billion annually, according to a 2024 survey by the India Philanthropy Alliance, Indiaspora, and Dalberg. The community gives roughly 1.8 per cent of household income to charitable causes — below the American average of about 2 per cent, but rising rapidly.

What has shifted in recent years is *where* the money goes. Earlier generations of NRI donors directed funds overwhelmingly toward India — temples, schools, disaster relief. The newer cohort, the Agarwals included, is increasingly channelling philanthropy into American institutions: hospitals in Houston, labs at state universities, community clinics in the suburbs that the diaspora has quietly reshaped.

There is a practical logic at work. NRIs disproportionately populate healthcare, technology, and small-business sectors. Their donations tend to target the infrastructure they understand: medical systems that treat their parents, engineering programmes that train their children, clinics that serve their employees.

## What the donation says

A $5.5 million hospital cheque from a first-generation immigrant is a data point, not a trend in itself. But plotted alongside similar gifts — the Agrawals are part of a widening cohort of Indian-American donors making seven-figure commitments to American healthcare and education — it begins to trace a shift in how the diaspora sees its role.

The older framing was contribution *to India from abroad*. The emerging one is contribution *to the place you actually live*, an acknowledgement that building a life in America means building American institutions, too.

Brij Agarwal spent his first years in Houston working nights. His latest cheque will keep a hospital running through them."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Doubled the Limit for NRI Investors. Then They Tried to Open an Account.",
        "subheadline": "The RBI and Finance Ministry just raised how much NRIs can invest in Indian stocks. But a GPS check, an Aadhaar OTP that won't arrive abroad, and two incompatible KYC systems mean most diaspora investors still can't get past the login screen.",
        "slug": make_slug("nri-kyc-friction-sebi-gift-city-digital-onboarding"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For millions of NRIs who want to participate in India's equity markets, the problem is no longer the limit — it is the paperwork. SEBI's geo-tagging requirement, Aadhaar-dependent e-signatures, and incompatible KYC systems between the regulator and GIFT City create a friction tax that specifically penalises the diaspora.",
        "tags": ["nri", "diaspora", "investment", "sebi", "rbi", "gift-city", "kyc", "fintech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/companies/startup-policy-forum-seeks-easier-kyc-rules-for-nri-investor-11780655285635.html"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/invest/rbi-proposes-higher-investment-limits-in-equity-instruments-for-nris-ocis-and-other-overseas-indians"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/invest/retail-participation-in-gift-city-funds-nearly-triples-in-q4-fy26"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/33785776/pexels-photo-33785776.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A smartphone displaying investment charts alongside a passport and US dollars — the reality of NRI investing",
        "image_attribution": "Pexels",
        "body": """On June 5, the Reserve Bank of India and the Finance Ministry announced what sounded like a gift to the diaspora. Individual NRIs and OCIs can now invest up to 10 per cent of a listed Indian company's paid-up capital through the Portfolio Investment Scheme — double the earlier 5 per cent cap. The aggregate ceiling for all NRI investors jumped from 10 per cent to 24 per cent. And for the first time, all Persons Resident Outside India (PROIs) — not just NRIs and OCIs — can participate on the same terms.

The policy intent is clear: attract more of the diaspora's patient capital into Indian equities, especially as foreign portfolio investors pulled out nearly ₹2.25 trillion in 2026 alone, exceeding the ₹1.66 trillion outflow of 2025.

There is just one problem. Most NRIs cannot actually open an account.

## The GPS wall

Under SEBI's KYC Master Circular, any new securities account opened via Video-based Customer Identification Process (V-CIP) must geo-tag the customer's live GPS location and verify that they are physically present in India.

Read that again. An NRI sitting in New Jersey, Dubai, or London — the exact people the policy is designed to attract — cannot complete digital onboarding for a brokerage account because the system requires them to be standing inside India when they do it.

"The only alternative for them is to follow the offline process of couriering notarized KYC documents and account opening forms," said Ankur Choudhary, co-founder and CEO of Belong, a GIFT City-based investment platform.

In 2026, when you can open a bank account in Singapore from a phone on a beach in Bali, India's securities regulator is asking NRIs to FedEx notarised paperwork.

## The Aadhaar trap

Even if the geo-tagging requirement were waived, another barrier awaits. SEBI's digital KYC process requires investors to electronically sign account-opening documents, and most financial intermediaries rely on Aadhaar-based e-Sign — the cheapest, most widely integrated option.

The catch: most long-term NRIs either do not have Aadhaar, or cannot receive Aadhaar-linked OTPs on their overseas phone numbers. The system was built for resident Indians. NRIs are an afterthought.

"As far as NRIs are concerned, most do not have Aadhaar, and even if they do, receiving OTPs linked to Aadhaar can be a challenge while abroad," said Kranthi Bathini, director of equity strategy at WealthMills Securities. "As a result, much of the process ends up becoming physical."

## Two kingdoms, one investor

There is a third layer of friction, and it is entirely self-inflicted. India's financial markets are now supervised by two regulators for NRI investors: SEBI for domestic-listed securities and IFSCA for products routed through GIFT City. Each has its own KYC framework, its own onboarding process, and its own compliance requirements.

IFSCA, to its credit, permits fully digital video KYC for NRI clients in jurisdictions deemed low-risk for money laundering. An NRI in Toronto cleared by IFSCA to invest in a GIFT City mutual fund may still need to start the KYC process from scratch — and courier physical documents — to buy shares on the BSE through a SEBI-registered broker.

"This lack of interoperability creates duplication and prevents investors from experiencing a truly unified investment journey across Indian financial markets," Choudhary said.

## The fix on the table

This week, the Startup Policy Forum — an alliance of India's new-age financial companies — submitted a formal recommendation to SEBI and the Finance Ministry proposing three specific changes.

First, scrap the India-only geo-tagging requirement for NRI video KYC. Second, allow uploaded wet signatures to be verified during video calls, eliminating the Aadhaar e-Sign dependency. Third, make the KYC systems of SEBI and IFSCA interoperable, so that an NRI cleared by one regulator does not have to repeat the process for the other.

"The diaspora is a natural pool of patient capital at a time Indian markets need it most," said Shweta Raj Kohli, president and CEO of the Startup Policy Forum. "But NRI investors face unnecessary friction. The regulatory fixes are small relative to the opportunity."

## The money that is already moving

The irony is that NRI capital *is* finding its way into Indian markets — through GIFT City, which has fewer of these barriers. Retail investor participation in GIFT City funds nearly tripled in Q4 FY26, jumping from 1,239 investors in December 2025 to 3,438 by March 2026. New fund launches, like the Marcellus Global Equities Fund opening June 8, are specifically targeting NRI investors with $5,000 minimum investments and fully digital onboarding.

The money wants to come. The regulators have raised the ceiling. Now someone needs to open the door."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
