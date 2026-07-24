#!/usr/bin/env python3
"""Travel news writer for The Videshi — 2026-06-27 15:00 run."""

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
        "headline": "Google Wallet Just Made TSA PreCheck Touchless — Here's Why Every NRI Flyer Should Set It Up Before Their Next Trip",
        "subheadline": "A new Google Wallet integration lets TSA PreCheck members clear airport security with a face scan and no physical ID. It's live at 65 airports, covers 100-plus airlines, and works perfectly with Global Entry — the programme most Indian Americans already have.",
        "slug": make_slug("google-wallet-tsa-precheck-touchless-id-nri-global-entry"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Millions of Indian Americans hold Global Entry — which includes TSA PreCheck — and fly frequently between the US and India. This integration eliminates the fumble for documents at security and is especially useful on the long-haul routes NRIs know best.",
        "tags": ["travel", "tsa-precheck", "google-wallet", "airport-security", "global-entry", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TSA.gov", "url": "https://www.tsa.gov/news/press/releases/2026/06/24/tsa-google-wallet-launch-new-tsa-precheck-touchless-id-opt"},
            {"name": "The Points Guy", "url": "https://thepointsguy.com/news/tsa-precheck-touchless-id-google-wallet/"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/google-wallet-brings-tsa-precheck-touchless-id-to-millions-more-travelers/"},
            {"name": "Phone Arena", "url": "https://www.phonearena.com/news/google-wallet-beats-iphone-touchless-airport-security"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2574091/pexels-photo-2574091.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "A traveller enters the security checkpoint at a US airport terminal",
        "image_attribution": "Pexels",
        "body": """The ritual is burned into muscle memory for anyone who flies out of the US more than a few times a year: pull out the boarding pass, fish out the driver's licence (or passport, for those who never bothered with Real ID), hold both up, wait for the nod. As of June 24, a chunk of that choreography is optional.

TSA and Google announced that Google Wallet is now the first digital wallet to support TSA PreCheck Touchless ID — a biometric system that uses facial comparison to verify your identity at the security checkpoint. No physical ID. No boarding pass in hand. You walk up, look at the camera, and walk through.

## What changed

Touchless ID itself isn't brand new. TSA began piloting it with Delta at Detroit and Atlanta in 2021, then expanded to American, Southwest, United, and Alaska Airlines through 2025. By March 2026, more than 60 airports offered it.

The catch was friction. Each airline required a separate manual passport upload through its own app. If you flew United one week and Delta the next, you enrolled twice — a process irritating enough that many PreCheck members simply didn't bother.

Google Wallet eliminates that. Add your passport and boarding pass to Wallet, tap "Get started" when the badge appears, approve the TSA consent page once, and you're enrolled across all 100-plus participating airlines. One opt-in, every carrier.

## How it works at the checkpoint

Dedicated Touchless ID lanes sit within or beside the standard PreCheck queue. A TSA officer directs you to a camera position. The system matches your face against the identity you shared through Wallet. If the match clears, you proceed — no fumbling for documents, no unlocking your phone.

Your passport data stays encrypted on-device until you consent. TSA says biometric templates aren't stored in Wallet itself; matching happens at the checkpoint against records you already provided. Google has stressed that the passport scan and selfie used to create the digital ID remain local or protected.

## The NRI angle

This matters disproportionately to Indian Americans, and for a specific reason: Global Entry.

India became the eleventh country whose citizens are eligible for Global Entry — the CBP Trusted Traveller Programme that expedites customs and immigration clearance at US airports. Global Entry membership automatically includes TSA PreCheck. The two programmes share the same Known Traveller Number.

The Indian American community is one of the most frequent international-travel demographics in the US. The SFO–Delhi, JFK–Mumbai, ORD–Hyderabad, and Newark–Bangalore corridors carry hundreds of thousands of NRI travellers annually. Many already hold Global Entry because it smooths the long immigration lines at JFK Terminal 4 or SFO International after a 16-hour flight from India.

What Touchless ID adds is the other end of the journey — the departure. Instead of reaching for a passport at security before an outbound flight, Global Entry holders with an Android device can now clear the checkpoint with a glance. For families juggling carry-ons, strollers, and shoes-off routines at peak travel hours, the saved minutes are real.

## What it doesn't cover

A few caveats before you delete your TSA PreCheck card from your physical wallet:

- **iPhone users are out — for now.** Apple Wallet holds digital IDs in some states but isn't a TSA Touchless ID partner. There's no announced Apple collaboration yet. Samsung offers a digital passport feature through CLEAR, but that's a separate programme.
- **Not every airport has Touchless ID lanes.** The system operates at 65 airports. Major hubs like JFK, LAX, SFO, ORD, and ATL are covered, but smaller regional airports may not be.
- **Carry your physical ID anyway.** TSA recommends a backup. If the facial match fails or a lane is offline, you'll need something to show.
- **It won't help at immigration abroad.** This is a TSA security-screening feature, not a border-crossing tool. You still need your physical passport for international flights.

## How to set it up

1. Add your US passport as an ID pass in Google Wallet (if not already done).
2. Check in for a flight with a participating airline and save the boarding pass to Wallet.
3. Look for the "Get started" button on the boarding pass in Wallet.
4. Tap it, and approve the secure sharing of your digital ID and trip details with TSA on the consent page.
5. Wait for the Touchless ID badge to appear on your boarding pass. You're set.

The enrolment carries forward — you won't need to repeat it for future flights, regardless of airline.

## The bigger picture

TSA is pushing aggressively toward biometric efficiency. REAL ID enforcement kicked in fully this year, the $45 fee for non-compliant travellers took effect in May, and the agency is framing Touchless ID as the "Golden Age of Travel" initiative. For the roughly 20 million PreCheck members — a number that grew 33 per cent last year alone — the Google Wallet integration makes the fastest lane through security meaningfully easier to access.

For NRIs who already invested in Global Entry for the arrival side, this completes the loop on departure. Set it up before your next flight."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Supreme Court Just Made Your Green Card a Little Less Green — and Every NRI Planning an India Trip Should Read the Fine Print",
        "subheadline": "A 6-3 ruling in Blanche v. Lau lowers the bar for border agents to treat returning green card holders as first-time applicants for admission. For the millions of Indian LPRs who fly home regularly, the legal ground beneath routine travel has shifted.",
        "slug": make_slug("supreme-court-green-card-re-entry-blanche-lau-india-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "India is the largest source country for US green card holders, and Indian LPRs fly to India more frequently than almost any other immigrant group. This ruling means even minor unresolved legal matters — a traffic violation escalated, a tax dispute — could complicate re-entry.",
        "tags": ["travel", "immigration", "green-card", "supreme-court", "nri", "us-india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/government/immigration-supreme-court-accedes-trumps-restrictive-agenda-2026-06-26/"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/supreme-court/3445961/supreme-court-reform-immigration-system-landmark-ruling/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/us-immigration-policy-supreme-court-green-card-holders/"},
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/23/supreme-court-trump-admin-green-card-admission/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg/1280px-Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg",
        "image_caption": "The United States Supreme Court building in Washington, D.C., at dusk",
        "image_attribution": "Wikimedia Commons",
        "body": """For decades, the deal was straightforward: get a green card, build a life in the US, fly home to India when you need to, come back. The re-entry was a formality. Your permanent resident status spoke for itself at the border.

On June 23, the Supreme Court rewrote a piece of that understanding.

In *Blanche v. Lau*, the court ruled 6-3 that Customs and Border Protection officers do not need "clear and convincing evidence" that a lawful permanent resident has committed a crime before classifying them as an "applicant for admission" rather than a returning resident. The distinction sounds bureaucratic. It is not. It determines whether you walk through the arrivals hall or get pulled into a secondary inspection room where removal proceedings can begin.

## What the case was about

Muk Choi Lau, a Chinese citizen and green card holder since 2005, was indicted on trademark counterfeiting charges in New Jersey in 2012. Before his trial, he travelled to China. When he returned, CBP officers didn't simply readmit him — they paroled him into the country, a legal mechanism that treats the entrant as not yet admitted. After Lau pleaded guilty and was convicted, DHS initiated deportation proceedings on the basis that he was an inadmissible applicant, not a returning LPR.

The Second Circuit ruled that the government needed "clear and convincing evidence" of a crime before it could strip a green card holder of their returning-resident status at the border. The Supreme Court overturned that standard.

Justice Clarence Thomas, writing for the majority, was direct: "The Government correctly regarded Lau as an applicant for admission, so it properly charged him with inadmissibility. Nothing in the Immigration and Nationality Act required the border officer to have clear and convincing evidence that Lau had committed a crime involving moral turpitude before deeming him an applicant for admission."

Justice Ketanji Brown Jackson dissented, arguing the ruling "allows the Government to deem an LPR to be 'seeking an admission' first and justify the applicability of an exception later — undermining the statutory scheme as well as the benefits and security that come with having a green card."

## Why this hits Indian green card holders hardest

India is the single largest source country for employment-based green cards in the US. Hundreds of thousands of Indian-born lawful permanent residents live in the US, and their travel patterns to India are among the most frequent of any immigrant group — weddings, festivals, family emergencies, Diwali, summer holidays with children who need to know their grandparents.

Before this ruling, the practical risk of a routine India trip was near zero for a green card holder without a criminal conviction. The key word is *conviction*. The Lau decision changes the trigger point: CBP can now reclassify you at the border based on suspicion — an indictment, a pending charge, even an unresolved matter that might constitute a "crime involving moral turpitude."

The category of "moral turpitude" is broad and often contested. It includes fraud, theft, and counterfeiting, but it also extends to tax evasion, certain DUI offences in some circuits, and dishonesty-related charges. Immigration attorneys have long warned that the term is vague enough to sweep in matters that many people wouldn't consider serious crimes.

## What this means in practice

The ruling does not mean every green card holder faces interrogation at the airport. The vast majority of LPRs with clean records will notice no change. But for those with any brush with the legal system — even unresolved — the calculus of international travel has shifted.

**Before Blanche v. Lau:** A CBP officer needed strong evidence to treat a returning green card holder as a new applicant for admission. The presumption favoured the LPR.

**After Blanche v. Lau:** The officer's assessment of whether there's reason to believe a crime of moral turpitude was committed is enough to trigger reclassification. The standard is lower, the discretion wider.

Immigration attorneys are already advising clients to take specific steps before booking international travel:

- **Review your record.** Any pending legal matter — criminal, civil, or tax-related — should be discussed with an immigration lawyer before travelling.
- **Carry documentation.** Court dispositions, dismissal orders, or proof that charges were dropped can help at the border if a CBP officer raises questions.
- **Understand the INA categories.** The "crime involving moral turpitude" standard is interpreted differently across circuits. Know where your situation falls.
- **Consider timing.** If you have a pending court case, even a minor one, the safest course may be to resolve it before leaving the US.

## The broader context

The Lau decision landed alongside another major immigration ruling this week. On June 25, the court ruled 6-3 in a separate case that asylum seekers standing in Mexico have not "arrived in" the United States and therefore cannot apply for asylum until they physically cross the border. Together, the two decisions represent a significant expansion of executive enforcement power at the border — one targeting undocumented arrivals, the other touching lawful permanent residents.

For the Indian diaspora, the second is the one that lands closer to home. A green card was always understood as a near-guarantee of re-entry. After *Blanche v. Lau*, it's something closer to a strong presumption — one that a border officer, exercising broader discretion, can now override more easily.

The advice from every immigration lawyer contacted for this story was the same: if you have anything unresolved, resolve it before you fly."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
