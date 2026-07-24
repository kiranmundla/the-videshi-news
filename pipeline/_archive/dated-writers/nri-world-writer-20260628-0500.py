#!/usr/bin/env python3
"""NRI World Writer — 2026-06-28 05:00 PDT run.
Two articles:
  1. NRI tax filing season — July 31 deadline
  2. Ratha Yatra at 50 — ISKCON's chariot festival goes global
"""
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

# ──────────────────────────────────────────────
# ARTICLE 1: NRI Tax Filing Season
# ──────────────────────────────────────────────

art1_body = """The July 31 deadline is five weeks away, and for the millions of Indians who live abroad but earn anything in India — rent from a flat in Pune, interest on an NRO fixed deposit, dividends from old Reliance shares — it is the annual reminder that geography does not exempt you from the Income Tax Department.

Filing an income tax return as a non-resident Indian has never been simple. But this year's round, for financial year 2025–26 (assessment year 2026–27), carries a few wrinkles that deserve attention before the clock runs out.

## The residential-status trap

Everything in the Indian tax code starts with a single question: what is your residential status for the year? The answer determines whether India can tax only your Indian-sourced income (non-resident), a limited slice of your foreign income (resident but not ordinarily resident, or RNOR), or your entire global income (resident and ordinarily resident).

The dividing lines hinge on how many days you spent in India. If you were physically present for 182 days or more, you are a resident. A subtler 120-day rule can catch high-earning Indian citizens or PIOs who spent between 120 and 181 days on Indian soil and whose Indian income exceeded ₹15 lakh. Miscounting even a short trip — that week at a cousin's wedding — can push you across the line.

Getting this wrong is not a rounding error. It can mean India taxing a US salary or a London rental that should have been left alone.

## What NRIs actually owe India

For those who are genuinely non-resident, the taxable basket is narrower than most people assume — but it is not empty. The big items: NRO savings and fixed deposit interest (taxable; NRE and FCNR interest is generally exempt), rental income from Indian property, capital gains from selling Indian shares, mutual funds, or real estate, dividends from Indian companies, and any salary received in India.

Foreign salary earned and received outside India? Generally not taxable in India for a non-resident.

## The schedule nobody told you about

Ask any chartered accountant who works with NRI clients and they will tell you: Schedule FA is the form section that catches people. It requires disclosure of foreign assets — bank accounts held abroad, overseas investments, foreign property, even signing authority over a foreign account.

The common assumption is "I'm an NRI, why would India care about my foreign bank account?" The answer lies in the residential-status logic above. If you qualify as Resident or RNOR in any given year, Schedule FA is mandatory — even if the asset earned nothing, even if it is a dormant account with $500 sitting in it. The penalty for missing it: up to ₹10 lakh per undisclosed asset under the Black Money (Undisclosed Foreign Income and Assets) and Imposition of Tax Act, 2015.

A few minutes double-checking past returns is worth substantially more than that notice.

## New this year

The ITR forms for AY 2026–27 carry a handful of changes. ITR-1 (Sahaj) now allows income from up to two house properties, which is a relief for NRIs who hold more than one flat in India and previously had to file the longer ITR-2. Requirements for reporting foreign retirement benefits have been removed. And the e-filing portal now offers Excel utilities for ITR-1 through ITR-4, letting you prepare offline before uploading — a convenience for anyone juggling time zones.

## The DTAA is not a get-out-of-jail card

India has Double Taxation Avoidance Agreements with over 90 countries, including the United States, the United Kingdom, Canada, and Australia. These treaties can lower the tax rate on certain Indian income or give you credit in your country of residence for tax paid in India. But DTAA benefit is not automatic. To claim it, you need a Tax Residency Certificate from your country of residence, Form 10F filed electronically, and correct disclosure in the ITR. If these documents are not in place before a payment is made, the deductor will withhold tax at the standard domestic rate, and you will have to chase a refund.

## The American wrinkle: FBAR and FATCA

For NRIs in the United States, the compliance burden is double-barrelled. On the Indian side, you file an ITR. On the American side, you must report any Indian financial account exceeding $10,000 in aggregate value on FinCEN Form 114, the Report of Foreign Bank and Financial Accounts (FBAR), due April 15 with an automatic extension to October 15. If the combined value of your "specified foreign financial assets" — including Indian mutual funds, shares, and insurance policies — exceeds $50,000 at the end of the tax year (higher thresholds for certain filers), you must also file Form 8938 under FATCA with your US return.

Neither filing obligation is optional. Neither triggers the other. And the penalties for non-compliance — $10,000 per FBAR violation for non-wilful cases, potentially much steeper for wilful ones — are not theoretical.

## The practical checklist

With five weeks left, here is the minimum an NRI should do:

**1.** Confirm your residential status using actual passport travel dates — not a rough estimate.

**2.** Download your Annual Information Statement (AIS) and Form 26AS from the e-filing portal. Check that TDS credits match what was actually deducted.

**3.** Classify bank interest correctly: NRE interest is exempt; NRO interest is not. Do not merge them.

**4.** If you sold Indian property, shares, or mutual funds during the year, calculate capital gains and check the applicable DTAA article before assuming a rate.

**5.** Validate your Indian bank account (preferably NRO) on the e-filing portal so any refund has somewhere to land.

**6.** If your residential status tipped to Resident or RNOR, fill in Schedule FA honestly.

**7.** E-verify the return after filing. The window for manual verification is 30 days — and it must reach the Centralised Processing Centre in Bengaluru by speed post.

The Indian tax department is not going to chase you across continents for a ₹15,000 NRO interest bill. But it will hold your refund, flag your PAN, and make future filings considerably more unpleasant. For the price of an afternoon, it is worth getting it right."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The July 31 Deadline Is Coming. Here's What Every NRI Filing an Indian Tax Return Needs to Know.",
    "subheadline": "Schedule FA, the DTAA paper trail, the FBAR double bind — a practical guide to the traps that catch diaspora taxpayers every year.",
    "slug": make_slug("nri-india-itr-july-deadline-schedule-fa-dtaa-fbar-guide"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Every NRI with Indian income faces the July 31 ITR deadline. The compliance burden is uniquely diaspora-shaped — juggling two tax systems, two sets of forms, and penalties that can reach ₹10 lakh per missed disclosure.",
    "tags": ["nri", "diaspora", "tax", "itr", "fbar", "schedule-fa", "dtaa", "compliance"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "CAClubIndia — NRI ITR Filing Guide", "url": "https://www.caclubindia.com/articles/nri-itr-filing-in-india-complete-guide-on-taxable-income-tds-refund-dtaa-and-nronre-accounts-55810.asp"},
        {"name": "CA Arun Acharya — Schedule FA (LinkedIn)", "url": "https://www.linkedin.com/pulse/one-schedule-nris-almost-always-miss-their-itr-ca-arun-acharya/"},
        {"name": "Mint — ITR Filing Precautions AY 2026-27", "url": "https://www.livemint.com/money/personal-finance/income-tax-returns-heres-what-precautions-should-taxpayers-take-while-filing-their-itr-11750854600081.html"},
        {"name": "IRS — FBAR Reporting (IRM 4.26.16)", "url": "https://www.irs.gov/irm/part4/irm_04-026-016"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8927687/pexels-photo-8927687.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Tax documents and currency on a desk during filing season",
    "image_attribution": "Pexels",
    "body": art1_body,
}

# ──────────────────────────────────────────────
# ARTICLE 2: Ratha Yatra at 50
# ──────────────────────────────────────────────

art2_body = """Fifty years ago, a small band of saffron-robed devotees in New York City did something that had never been done outside India: they pulled a wooden chariot carrying deities of Lord Jagannath, Balaram, and Subhadra down the streets of Manhattan. The procession — known as Ratha Yatra, the "chariot journey" — barely had a location to stage from until a young property developer named Donald Trump, then still building his real-estate empire, lent them a plot near Fifth Avenue for the chariot assembly.

On June 13 this year, that same procession marked its golden anniversary. More than 25,000 devotees thronged Fifth Avenue as three 25-foot-high chariots, jewel-toned and balloon-adorned, rolled south toward Washington Square Park. For the occasion, organisers shipped one of the original 1976 chariots from Florida back to New York — a relic from the days when Hare Krishna was still the curiosity of the counterculture, not a global movement with over a million devotees in 80 countries.

## From hippie ashram to diaspora institution

The International Society for Krishna Consciousness (ISKCON) was founded in New York in 1966 by A.C. Bhaktivedanta Swami Prabhupada, who had arrived from India the previous year with the mission of spreading Krishna consciousness in the West. The early movement drew heavily from the countercultural moment — young Americans who dropped out, moved into ashrams, and adopted Sanskrit names.

The Ratha Yatra was always the most public-facing expression of that mission. Its prototype is the annual Jagannath Rath Yatra in Puri, Odisha, widely considered the world's oldest street festival, where millions of devotees pull colossal chariots through the city's broad avenues. What Prabhupada wanted was a transplant: the same energy, the same ritual, in the middle of Manhattan.

The transplant took. From a single chariot in 1976, ISKCON's Ratha Yatra circuit now spans dozens of cities across the United States, Europe, and beyond. London's Ratha Yatra — which ran from Park Lane to Trafalgar Square on May 24 this year — is billed as Europe's largest, with over 16,000 plates of free prasadam distributed in a single afternoon. The Indian High Commissioner to the UK attended; so did devotees who had flown in from across the continent.

## The diaspora's quiet anchor

For the Indian diaspora specifically, the Ratha Yatra has become something more than a religious observance. It is a public assertion of cultural presence — a day when Indian festivals are not tucked away in community centres and temple basements but paraded through Fifth Avenue and Trafalgar Square, witnessed by tourists, World Cup visitors, and double-decker buses.

"We don't see anything like this back home," Patrick Ornelas, a visitor from Salt Lake City, told Religion News Service after stumbling upon the Manhattan procession.

The Brooklyn ISKCON temple, which anchors the New York event, houses about 40 full-time monks and draws around 500 regular attendees. But the annual Ratha Yatra is its largest outreach, regularly engaging tens of thousands — most of them Indian-American families who maintain their devotional lives outside the ashram model.

That shift matters. In the 1990s, ISKCON moved from a monastic model to congregational membership: devotees who attend events, chant at home, and keep their day jobs. For diaspora families trying to give their children a connection to India's spiritual traditions, the local ISKCON centre has become what the neighbourhood temple is back home.

## The economics of devotion

None of this runs on air. The 50th-anniversary procession in Manhattan cost approximately $160,000, sourced entirely from donations. Over 400 volunteers contributed to the event — one group cooked bread, rice, and curries through the night in shifts to feed the pilgrims; another took turns guarding the chariots against vandalism.

Sarvopama Das, 79, a devotee who flew in from Chicago, had volunteered to serve watermelon at the very first Ratha Yatra in 1976. "We thought we were cool talking about karma in the hippie days," he told Religion News Service. "Now it's in the dictionary!"

Among the thousands gathered in Washington Square Park after the procession were many younger devotees. Payal Mazumdar, 15, attends weekly Bhagavad Gita classes at the Brooklyn temple. "I have a really bad overthinking problem," she said. "But through the ISKCON community and philosophies, it felt like I had a support system on my side."

## Beyond the chariot

The timing of the anniversary could hardly have been better choreographed. Across June, ISKCON made headlines not for theology but for pop culture: monks had gone viral chanting with Knicks fans outside Madison Square Garden during the NBA championship run, leading to an uptick in temple enquiries. At the Ratha Yatra, a monk named Mahamantra sold Hare Krishna T-shirts designed in the Knicks' neon-orange logo style.

"I'm excited for if the Knicks win," he said, "but I'm most excited to be with people dancing and chanting."

The chariots, meanwhile, will not rest. In the coming weeks, they will be transported to other American cities for their own annual Ratha Yatras — growing ISKCON, organisers hope, with every turn of the wheel. For the diaspora, the message is characteristically unsubtle: the chariot only moves when someone reaches for the rope."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Fifty Years Ago, a Handful of Hare Krishnas Pulled a Chariot Down Fifth Avenue. Now 25,000 Show Up.",
    "subheadline": "ISKCON's Ratha Yatra in Manhattan just marked its golden anniversary — a milestone in how the Indian diaspora practises faith in public.",
    "slug": make_slug("iskcon-ratha-yatra-50th-anniversary-nyc-diaspora-chariot-festival"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The Ratha Yatra is the diaspora's most visible public expression of Hindu devotion in the West. For Indian-American families, ISKCON centres have become anchors of cultural continuity — the neighbourhood temple transplanted to Brooklyn and Trafalgar Square.",
    "tags": ["nri", "diaspora", "iskcon", "ratha-yatra", "hindu", "community", "culture", "new-york", "london"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Religion News Service — Hare Krishnas celebrate 50-year Ratha Yatra milestone in Manhattan", "url": "https://religionnews.com/2026/06/15/hare-krishnas-celebrate-a-50-year-milestone-with-a-parade-of-chariots-in-manhattan/"},
        {"name": "ISKCON News — 57 Years Celebrating Rathayatra in London", "url": "https://iskconnews.org/57-years-celebrating-rathayatra-festival-of-chariots-on-the-streets-of-london/"},
        {"name": "Religion News Service — NYC Ratha Yatra details", "url": "https://religionnews.com/2026/06/15/hare-krishnas-celebrate-a-50-year-milestone-with-a-parade-of-chariots-in-manhattan/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Rath_Yatra_or_Chariot_Festival_held_in_CT%2C_USA.jpg/1280px-Rath_Yatra_or_Chariot_Festival_held_in_CT%2C_USA.jpg",
    "image_caption": "Devotees pull a decorated Ratha Yatra chariot at an ISKCON festival in the United States",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ──────────────────────────────────────────────
# Insert
# ──────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
