#!/usr/bin/env python3
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
        "headline": "No More Flights to Chennai for a Stamp — Visa Renewals Are Coming Home",
        "subheadline": "A State Department pilot launching in December will let 20,000 H-1B holders renew their visas inside the United States. Most of those slots will go to Indian nationals.",
        "slug": make_slug("domestic-visa-renewal-pilot-h1b-india-december"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B workers have long endured the absurd ritual of flying back to India — or to a third-country consulate — just to get a visa stamp renewed. Wait times at Indian consulates stretch 6 to 12 months. The domestic renewal pilot is designed primarily for them: the State Department has said the 'vast majority' of the 20,000 initial slots will go to Indian nationals.",
        "tags": ["h1b", "visa-renewal", "state-department", "india", "consulate"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/30/us-to-launch-new-plan-for-work-visas-in-december/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/"},
            {"name": "U.S. Department of State", "url": "https://travel.state.gov/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
        "body": """Every Indian tech worker in America knows the drill. Your H-1B visa stamp is expiring. You need to renew it. But you can't do that here — you have to fly to a U.S. consulate abroad, typically back to India, and sit in a queue that stretches six, eight, sometimes twelve months for an appointment. You'll burn vacation days, buy international flights, and spend weeks away from the job that's supposedly so important the U.S. government approved a special visa for it.

That ritual is about to change, at least for 20,000 people.

## The Pilot

The U.S. State Department has confirmed it will launch a domestic visa renewal pilot program in December, allowing certain H-1B holders already inside the country to renew their visa stamps without leaving. Over a three-month window, 20,000 renewals will be processed — and the agency has been unusually direct about who this is for.

"The vast majority of those will be Indian nationals living in the US," said Julie Stufft, Deputy Assistant Secretary of State for Visa Services. "Because Indians are the largest skilled group of workers in the United States, we hope that India will benefit quite a bit from this program."

The announcement came as part of the broader India-U.S. joint statement, with Prime Minister Modi highlighting the initiative during his address to the Indian diaspora at the Ronald Reagan Center. A federal register notice — the first official documentation of eligibility criteria, application steps, and timelines — is expected in the coming weeks.

## Why This Matters More Than It Sounds

On paper, this is a bureaucratic tweak. In practice, it addresses one of the most persistent irritants in the lives of hundreds of thousands of Indian professionals.

The visa stamp is not the same as the visa status. An H-1B worker whose status is valid can live and work in the U.S. perfectly legally — but the moment they leave the country, they need a valid stamp in their passport to get back in. For many Indians, the stamp expiration becomes a de facto travel ban. Skip the family wedding. Cancel the client meeting in London. Don't risk a flight home when your father is sick, because you might not make it back for months.

The State Department has acknowledged the problem is acute in India specifically. "The wait time of 6, 8, and 12 months is not what we need and is not indicative of how we view India," Stufft said. The domestic renewal program, she added, "will allow our missions in India to concentrate on new applicants."

## What We Know — and What We Don't

The pilot will process applications domestically, meaning no in-person interview at a foreign consulate. Applicants will submit documentation from within the U.S. and receive their renewed visa stamp by mail.

A few details remain unclear pending the federal register notice:

- **Eligibility criteria**: The earlier 2024 pilot was limited to H-1B holders whose prior stamps were issued by specific consulates within specific date ranges. The December program may have broader or different eligibility windows.
- **Slot allocation**: The 2024 pilot released roughly 4,000 slots per week on a first-come, first-served basis. Similar mechanics are expected.
- **Fee structure**: Standard visa application fees will likely apply, but additional costs — if any — haven't been announced.
- **Expansion timeline**: Stufft indicated the program "will expand as it goes on," suggesting this is a proof of concept for a permanent domestic renewal option.

## The Bigger Picture

The domestic renewal concept isn't new — the State Department ran a limited pilot in early 2024 for H-1B holders stamped at consulates in India and Canada. That program was narrow but successful enough to justify this larger follow-up.

For the Indian tech workforce, the timing is loaded. The $100,000 H-1B fee has cratered new applications. EB-2 India green card numbers are exhausted for the fiscal year. Layoffs continue to push H-1B holders into 60-day grace period scrambles. Against that backdrop, a program that removes even one layer of bureaucratic pain carries outsize significance.

It also matters diplomatically. The domestic renewal pilot is a visible, tangible deliverable from the Modi-Trump bilateral engagement — the kind of thing that affects real people in a way that joint statements about "strategic convergence" never quite manage.

Twenty thousand slots is a start. For the roughly 600,000 Indian H-1B holders in the United States, the question is whether December marks the beginning of the end of the consulate-or-nothing era — or just another pilot that quietly expires."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Scare Is Over — DHS Says Green Card Applicants Can Stay Put",
        "subheadline": "After days of panic over whether adjustment of status applicants would be forced to return home, the Department of Homeland Security has walked it back. Most applicants will not need to leave.",
        "slug": make_slug("dhs-green-card-adjustment-status-uturn-stay-us"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders pursuing green cards through the EB-2 and EB-3 categories have the most at stake. With backlogs stretching decades, many have built entire lives in the U.S. while waiting — mortgages, children in school, careers spanning multiple employers. A requirement to leave the country during processing would have been catastrophic for this population specifically.",
        "tags": ["green-card", "adjustment-of-status", "dhs", "uscis", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/ujbcwtde94va/"},
            {"name": "Tupaki English", "url": "https://english.tupaki.com/"},
            {"name": "Murthy Law Firm", "url": "https://www.murthy.com/2026/05/22/newsflash-uscis-reinforces-that-adjustment-of-status-is-discretionary-not-a-right/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36984942/pexels-photo-36984942.jpeg",
        "body": """For about a week, a particular kind of dread settled over Indian immigrant communities across the United States. The question wasn't abstract or theoretical — it was visceral: would the government force green card applicants to leave the country and wait abroad while their cases were decided?

On Friday, the Department of Homeland Security said no. Most applicants can stay.

## How the Panic Started

On May 21, USCIS issued Policy Memorandum PM-602-0199, a document that reminded officers and the public that adjustment of status — the process by which someone already in the U.S. applies for a green card without going through consular processing abroad — is "an act of administrative grace, not an entitlement."

The language was technically accurate. Adjustment of status has always been discretionary. But the timing and framing sent a signal that immigration lawyers and applicants read as ominous. If AoS is discretionary, could USCIS start denying cases that would previously have been approved? Could applicants be told to go home and process through their local consulate instead?

Within days, the interpretation escalated. Social media and community forums buzzed with reports — some accurate, some distorted — that a "forced return" policy was imminent. Employers started fielding panicked calls from sponsored employees. Immigration attorneys scrambled to parse the memo's operational implications.

## What DHS Actually Said

The clarification, issued May 30, was blunt by bureaucratic standards. Federal officials emphasized that no sweeping policy change had been implemented. The adjustment of status framework remains operational. Most applicants will continue to be allowed to stay in the United States while their cases are reviewed.

The key points:

- **No blanket requirement to leave.** The earlier memo did not create a new rule requiring departure. It restated existing law.
- **Case-by-case discretion continues.** Immigration officers retain authority to evaluate individual cases, including the option to refer certain applicants to consular processing — but this authority existed before the memo and hasn't been expanded.
- **Existing procedures are intact.** The I-485 adjustment of status process has not been modified or suspended.

The clarification stopped short of withdrawing the May 21 memo. The memo's core assertion — that AoS is discretionary — remains on the books, because it's legally correct. What DHS walked back was the implication that this discretion would be wielded as a blunt instrument.

## Why This Hit Indians Hardest

Roughly 400,000 approved I-140 petitions for Indian nationals are sitting in the EB-2 and EB-3 backlogs, waiting for visa numbers that may not arrive for decades. For these applicants, adjustment of status isn't just a convenience — it's the architecture of their entire American lives.

While waiting for a green card that might take 15 to 40 years, Indian professionals on H-1B visas use pending AoS applications to maintain stability. Filing an I-485 unlocks employment authorization documents (EADs) and advance parole travel documents. It provides a measure of security — not permanent residency itself, but the infrastructure to keep living, working, and traveling while the bureaucratic clock ticks.

A policy that forced these applicants to leave and process through consulates in India would mean:

- Uprooting families, some of whom have been in the U.S. for over a decade
- Pulling children out of American schools mid-year
- Abandoning jobs, since consular processing offers no work authorization during the wait
- Joining consulate appointment queues that stretch 6 to 12 months in major Indian cities
- Losing the EAD and advance parole benefits that come with a pending I-485

The DHS clarification means none of that is happening — at least not as a matter of policy.

## The Residual Uncertainty

The walk-back is reassuring, but it isn't a guarantee. The May 21 memo remains in effect. USCIS officers still have discretion to refer individual cases to consular processing, and the criteria for when that discretion might be exercised haven't been spelled out in detail.

Immigration attorneys note that "case-by-case" can be a double-edged phrase. It provides flexibility, but also opacity. An applicant with a minor compliance issue — a gap in employment, a prior visa overstay, an incorrect address filing — could theoretically be singled out for consular processing rather than in-country adjustment.

For now, though, the system continues as it has. The roughly 1.4 million green cards issued annually will still include a substantial portion processed through adjustment of status from within the United States. The fear of a forced-departure mandate has, for the moment, subsided.

## What to Do Now

Immigration lawyers are advising clients to take the same precautions they always should:

- **Keep your records clean.** Ensure every employer change, address update, and status extension is properly filed and documented.
- **Don't assume discretion equals certainty.** The AoS process is discretionary. Always has been. Act accordingly.
- **Monitor USCIS guidance.** The memo is still active. Future policy updates could shift the interpretation again.
- **Consult an attorney if your case has complications.** Prior overstays, gaps in status, or pending RFEs deserve professional review.

The scare may be over. The underlying anxiety — about a system that can upend lives on a single policy memo — is not going anywhere."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
