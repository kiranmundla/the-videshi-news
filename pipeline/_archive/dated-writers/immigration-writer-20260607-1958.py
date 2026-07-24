#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-07 20:00 UTC run"""

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
        "headline": "Dropped in San José — Indian Nationals Caught in America's Third-Country Deportation Web",
        "subheadline": "Costa Rica has received two deportation flights from the US in as many weeks. Both carried Indian citizens to a country with which they have no legal, cultural, or familial ties.",
        "slug": make_slug("costa-rica-third-country-deportation-indian-nationals"),
        "category": "immigration",
        "vertical": "immigration",
        "is_editorial": False,
        "diaspora_angle": "Indian nationals are being deported not to India, but to Costa Rica — a country where they have no ties, no language, and no path forward. For the broader Indian community in the US, these flights signal that undocumented status now carries consequences that extend far beyond a plane ticket home.",
        "tags": ["deportation", "costa-rica", "ice", "third-country-removal", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "LawStreet Journal", "url": "https://lawstreet.co/international/indian-national-among-30-deportees-in-second-us-to-costa-rica-third-country-transfer-flight"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/06/costa-rica-to-facilitate-us-deportation-of-indian-migrants/"},
            {"name": "UN OHCHR", "url": "https://www.ohchr.org/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/A_United_States_Immigration_and_Customs_Enforcement_%28ICE%29_Enforcement_and_Removal_Operations_%28ERO%29_officer_patrols_a_removal_flight_%2850044711591%29.jpg/1280px-A_United_States_Immigration_and_Customs_Enforcement_%28ICE%29_Enforcement_and_Removal_Operations_%28ERO%29_officer_patrols_a_removal_flight_%2850044711591%29.jpg",
        "image_caption": "An ICE Enforcement and Removal Operations officer aboard a deportation flight",
        "image_attribution": "Wikimedia Commons",
        "body": """Costa Rica received its second deportation flight from the United States last Friday. Thirty people were on board, drawn from ten countries. One of them was Indian.

It was the second consecutive flight to San José's Juan Santamaría International Airport carrying an Indian citizen — not home to India, but to a Central American country with which they share no language, no legal status, and no family. The first flight, a week earlier, carried 25 people from eight countries. An Indian national was on that one too.

## The Agreement Nobody Voted On

The flights operate under a bilateral agreement signed in March by Costa Rican President Rodrigo Chaves and US Special Envoy Kristi Noem. Under its terms, Costa Rica agreed to accept up to 25 third-country nationals expelled from the United States each week. The cap was breached on only the second flight.

The United States foots the bill. The International Organization for Migration provides food and accommodation for the first seven days. After that, migrants must figure out their own next steps — a timeline that legal experts have called grossly inadequate for people who may lack travel documents, financial resources, or ties to any country willing to take them.

Costa Rica's Immigration Chief Omer Badilla has said the deportees are "in full freedom" and staying in a hotel, though the Ombudsman's Office had to threaten legal action just to learn where the first group was being housed. Forty-eight hours after their arrival, inspectors still hadn't been allowed inside.

## A Network of 27 Countries

Costa Rica is not an outlier. It is the latest addition to a deportation architecture that now spans at least 27 countries. Panama and Guatemala signed similar agreements earlier. So did South Sudan, Rwanda, Guyana, and several Caribbean island nations including Dominica and St. Kitts and Nevis. Most of these agreements have never been made public.

The financial dimension is staggering. El Salvador received nearly $6 million to imprison deportees. Equatorial Guinea got $7.5 million. Eswatini, $5.1 million. A February 2026 report from Senate Democrats on the Foreign Relations Committee estimated the programme has cost American taxpayers at least $40 million, with individual removals running as high as $1 million per person. One Jamaican man was flown to Eswatini — despite a court ruling that he should have been sent to Jamaica — and later transferred back to Jamaica anyway, both legs at US expense.

Migrant arrests in the United States increased elevenfold during the first year of Trump's second term, driving a fivefold increase in deportations. Third-country transfers have become Washington's preferred tool for managing the volume, particularly for nationalities whose home countries are slow to accept returns.

## The Courts Are Pushing Back

The legal framework around these flights is the subject of active litigation. US District Judge Brian Murphy barred the federal government from sending migrants to third countries without first assessing potential claims under the UN Convention Against Torture. In a subsequent ruling, he found the entire third-country removal policy violated federal immigration law and migrants' right to due process.

Multiple federal judges have now ruled that before deporting a person to a third country, the Department of Homeland Security must provide meaningful notice and a real opportunity to raise country-specific claims. Despite those rulings, the flights have continued. Reports indicate that many individuals learn they are being sent to a third country only while already airborne, and that even when a receiving country has not credibly committed to refrain from torture or persecution, DHS typically gives individuals just 24 hours' notice with no guaranteed access to an attorney.

Costa Rica's own Constitutional Chamber set a precedent in 2025 when it ruled that authorities had violated the fundamental rights of migrants by withholding information on migration status, blocking access to legal counsel, and failing to offer the option of seeking refuge.

## What This Means for the Indian Diaspora

India accepted 1,076 deportees from the US in 2026 through the first five months. Those were direct repatriations, processed through the Ministry of External Affairs with nationality verification checks that can take weeks. The third-country route bypasses that process entirely. An Indian national dropped in Costa Rica is not in India's consular care. They are in a country that speaks Spanish, has no Indian embassy, and offers seven days of IOM-funded lodging before the clock runs out.

For the estimated 725,000 undocumented Indians living in the United States — a population that includes visa overstayers, Day-1 CPT beneficiaries whose programmes collapsed, and asylum seekers whose claims were never adjudicated — the Costa Rica flights carry a message that is hard to misread. The deportation machinery is no longer constrained by the logistics of sending people home. Washington has built a network of willing countries, and the flights are running on schedule.

The UK attempted a similar arrangement with Rwanda in 2022. Courts killed it before a single flight departed. In the United States, courts have raised objections too. But the planes are still flying."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Eleven Million Cases and Counting — The USCIS Machine That's Grinding Indian Immigration to a Halt",
        "subheadline": "A record backlog, rising fees, and vanishing automatic extensions have turned the US immigration processing system into a toll booth with no exit — and Indian applicants are paying the steepest price.",
        "slug": make_slug("uscis-11-million-backlog-indian-processing-crisis"),
        "category": "immigration",
        "vertical": "immigration",
        "is_editorial": False,
        "diaspora_angle": "Indian nationals account for roughly 627,000 of the estimated 1.2 million people stuck in the employment-based green card backlog alone. The processing crisis hits them hardest because they wait the longest — and every fee hike, every extension removal, and every policy pause compounds years of accumulated delay.",
        "tags": ["uscis", "backlog", "processing-times", "green-card", "h4-ead", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
            {"name": "Manifest Law", "url": "https://manifestlaw.com/uscis-processing-times-may-2026/"},
            {"name": "Alonso & Alonso Law", "url": "https://alonsoandalonsolaw.com/uscis-processing-times/"},
            {"name": "Mondaq", "url": "https://www.mondaq.com/unitedstates/work-visas/1583898/uscis-announces-inflation-adjusted-premium-processing-fee-increase-effective-march-1-2026"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center in Queens, New York",
        "image_attribution": "Wikimedia Commons",
        "body": """The numbers are not abstract. They are people — engineers in Sunnyvale refreshing their case status for the 400th time, H-4 spouses in New Jersey who lost the right to work because a renewal took too long, families in Frisco who cannot visit a dying parent in India because their travel document has been pending for 21 months.

US Citizenship and Immigration Services is managing a record backlog of more than 11 million pending cases. That figure — disclosed in USCIS processing data earlier this year — represents every asylum claim, every green card application, every work permit renewal, and every citizenship petition sitting in an agency queue. For Indian nationals, who account for the largest share of employment-based immigration demand, the bottleneck is not just inconvenient. It is structurally ruinous.

## The Numbers Behind the Gridlock

Processing times across major petition types have ballooned. An I-140 petition for an EB-3 skilled worker — the standard employer-sponsored green card pathway — now takes up to 24 months through regular processing. An I-485 adjustment of status for employment-based applicants averages 11.5 months across all field offices. An I-131 travel document — the advance parole that allows green card applicants to leave and re-enter the country — sits at 21 months. For someone whose mother is ill in Hyderabad, 21 months is not a processing time. It is an answer.

The I-130 petition for spouses of US citizens has stretched to 17 months. Family reunification for permanent residents filing in the F2A category can take 50 to 115 months — nearly a decade at the long end.

Even premium processing, the paid expedite lane, no longer comes cheap. Effective March 1, 2026, DHS raised the fee for premium processing on I-129 and I-140 petitions from $2,805 to $2,965 — a 5.72 per cent inflation adjustment. The H-2B and R-1 categories rose to $1,780. OPT and STEM OPT premium processing hit $1,780. These are add-on fees, layered on top of the base filing costs, and they buy a 15-business-day decision window for temporary petitions. For the I-485, premium processing does not exist. You wait.

## The Extension Trap

In October 2025, USCIS ended automatic extensions of employment authorization documents for most renewal categories. Before that change, an H-4 EAD holder who filed a timely renewal could continue working while the agency processed the application. Now, if you filed your I-765 renewal on or after October 30, 2025, you do not receive an automatic extension. You must wait for approval before you can work.

For H-4 spouses — overwhelmingly Indian women married to H-1B holders with approved I-140 petitions — this is devastating. The H-4 EAD was always a fragile instrument, dependent on the primary worker's visa status and employer sponsorship. Now it has a gap built into it: the weeks or months between filing a renewal and receiving the new card, during which you are legally present but forbidden from earning a living.

The typical I-765 processing time hovers around two months for certain categories. But "typical" is an average that conceals a long tail. Some applications take six months. A few take longer. In that gap, mortgage payments still come due. Childcare costs don't pause. And the psychological toll of being professionally sidelined in a country where you have built a career compounds with each passing week.

## Who Carries the Weight

Brookings Institution research published in May estimated the employment-based green card backlog at roughly 1.2 million applicants and their families. Of those, approximately 627,000 were born in India. The per-country cap of 7 per cent on annual green card allocations — unchanged since 1990 — means Indian nationals compete for the same small slice of visas as citizens of countries that send a fraction of the applicants.

The result is a queue that, for EB-2 India applicants, stretches back more than a decade. The July 2026 visa bulletin closed all employment-based categories for India. EB-2 India's annual allocation was exhausted before the fiscal year's end. EB-3 India fared no better. For the thousands of Indian professionals who filed I-485 applications years ago and have been waiting for a visa number to become current, the bulletin was a locked door with no date on the key.

## The System Is Charging More and Delivering Less

The mathematics are perverse. A typical Indian H-1B worker whose employer files an I-140 with premium processing now pays $2,965 for the expedite alone, on top of base filing fees exceeding $700. If they need an H-4 EAD for their spouse, that is another $410 plus $1,780 if they want premium processing. Advance parole for travel: $630, no premium option, 21-month wait.

Add the $100,000 fee imposed on new H-1B petitions since September 2025 — a measure so punitive that only about 85 companies have paid it — and the total cost of participating in the US immigration system has reached levels that would have been unimaginable five years ago.

USCIS has said the additional revenue from fee increases will support "faster adjudication, reduce backlogs, and improve processing efficiency." The 11 million pending cases suggest otherwise. For Indian families caught in the gears of this system — filing renewals, waiting for interviews, tracking visa bulletin movements, paying fees that climb faster than their salaries — the question is no longer whether the machinery is broken. It is whether anyone in Washington has an incentive to fix it."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
