#!/usr/bin/env python3
"""News writer for The Videshi - June 9, 2026 batch"""

import json
import os
import subprocess
from datetime import datetime, timezone

# Load env
env_vars = {}
with open(os.path.expanduser('~/.env.supabase')) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            if line.startswith('export '):
                line = line[7:]
            key, val = line.split('=', 1)
            env_vars[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = env_vars['SUPABASE_URL']
SUPABASE_KEY = env_vars['SUPABASE_SERVICE_ROLE_KEY']

def insert_article(article):
    """Insert article into Supabase via curl."""
    payload = json.dumps(article)
    result = subprocess.run(
        [
            'curl', '-sS', '-w', '\n%{http_code}',
            f'{SUPABASE_URL}/rest/v1/p2_articles',
            '-X', 'POST',
            '-H', f'apikey: {SUPABASE_KEY}',
            '-H', f'Authorization: Bearer {SUPABASE_KEY}',
            '-H', 'Content-Type: application/json',
            '-H', 'Prefer: return=representation',
            '-d', payload
        ],
        capture_output=True, text=True, timeout=30
    )
    output = result.stdout.strip()
    lines = output.split('\n')
    http_code = lines[-1] if lines else 'unknown'
    body = '\n'.join(lines[:-1])
    return http_code, body

now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

# ============================================================
# ARTICLE 1: Apache helicopter shot down
# ============================================================
article1 = {
    "headline": "Iran Downed a US Apache Over the Strait of Hormuz. India's Fragile Oil Lifeline Just Got More Fragile.",
    "subheadline": "A Shahed drone reportedly struck the helicopter. Both pilots survived, but the ceasefire Trump promised is unravelling — and India's $90-a-barrel nightmare is back on the table.",
    "slug": "iran-shoots-down-us-apache-hormuz-india-oil-ceasefire-shahed-drone-20260609",
    "category": "news",
    "vertical": "news",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/U_S_Army_AH-64_Apache_Attack_Helicopter_%289483759%29.jpg/1280px-U_S_Army_AH-64_Apache_Attack_Helicopter_%289483759%29.jpg",
    "image_caption": "A US Army AH-64 Apache attack helicopter in flight",
    "image_attribution": "Wikimedia Commons",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "sources": json.dumps(["Reuters", "CNN", "Wall Street Journal", "NY Post", "RBI"]),
    "body": """An Iranian Shahed drone struck a US Army AH-64 Apache helicopter patrolling the Strait of Hormuz late on Monday night, sending the aircraft into the water off the coast of Oman and marking the first American helicopter loss since the Gulf war began in February. Both crew members were rescued by an unmanned Navy surface drone — a Saronic Corsair, part of the AI-driven Task Force 59 — after spending roughly two hours in the water. It was the first time such a vessel had been used for a combat rescue.

President Donald Trump confirmed the shootdown on Tuesday in a Truth Social post: "I have just been informed by our Great Military that last night the Iranians shot down one of our highly sophisticated Apache Helicopters while patrolling over the Strait of Hormuz. There were two pilots involved, both are safe and uninjured. Nevertheless, the United States must, of necessity, respond to this attack."

The incident came barely 24 hours after Iran and Israel exchanged their most intense missile strikes since the April 8 ceasefire, and just hours after a US F/A-18 Super Hornet disabled an oil tanker in the Gulf of Oman that had attempted to run America's blockade of Iranian ports. Iran's parliamentary speaker, Mohammad Bagher Ghalibaf, responded with a warning to Washington: "We prefer the language of diplomacy, but we speak other languages far more fluently. Break your commitments, and we'll switch to what we speak best."

## What It Means for India

For New Delhi, every escalation in the Hormuz corridor is an economic body blow. Before the war, approximately 20 percent of the world's crude oil and liquefied natural gas passed through the strait. Iran's blockade has already pushed India's crude import bill sharply higher. The Indian crude basket, which hovered around $75 per barrel a year ago, is now threatening $90.

India's economy grew 7.7 percent in FY26, but economists have warned that sustained oil above $85 per barrel could shave a full percentage point off that figure. The Reserve Bank of India last week announced emergency forex measures — concessional swaps for NRI deposits, leverage on FCNR accounts — partly to shore up reserves against the energy import shock.

The timing could not be worse. Just days ago, US Energy Secretary Chris Wright said ship traffic through Hormuz was rising "very meaningfully," suggesting the waterway was slowly reopening. That optimism is now in tatters. Wright himself acknowledged it would take "many months" to restore normal flows even after a deal is signed — and no deal appears close.

## The Ceasefire That Isn't

Trump told reporters at JFK Airport on Monday night — where he had gone to watch the Knicks lose Game 3 of the NBA Finals — that a deal with Iran could come "in two or three days." He has made similar claims repeatedly since April with nothing to show for it. His approval ratings are at record lows ahead of November's midterm elections, and a durable Iran deal remains his most elusive foreign policy prize.

Israel's military chief Eyal Zamir poured cold water on ceasefire hopes on Tuesday, calling Monday's Israeli strikes on Iran "preparation for a much more significant and heavy blow." Tehran has insisted that any peace deal requires Israel to end its Lebanon campaign — a condition Israel has flatly refused, arguing Lebanon should be treated separately.

For the 1.4 billion Indians watching oil prices on every newscast, the geopolitics are secondary to the arithmetic. India imports roughly 85 percent of its crude. Every dollar added to the barrel translates into higher petrol pump prices, wider current account deficits, and inflationary pressure that eventually shows up in grocery bills.

The RBI's current account data, released Monday, showed India posted a surprise $7.1 billion surplus in Q4 FY26 — driven largely by a surge in NRI remittances from the Gulf, where workers have been sending money home as a precaution against the deepening crisis. That surplus is a buffer, but a thin one. If Hormuz stays choked, the full-year FY27 current account deficit could balloon to 2.4 percent of GDP by some estimates.

The Apache helicopter is out of the water. The ceasefire, for all practical purposes, is too.

*Sources: Reuters, CNN, Wall Street Journal, NY Post, RBI data*"""
}

# ============================================================
# ARTICLE 2: Dubai road crash kills 7 Indian workers
# ============================================================
article2 = {
    "headline": "Seven Indian Workers Died on a Dubai Highway. A Truck Stopped. A Bus Didn't.",
    "subheadline": "A minibus carrying workers slammed into a stalled truck on Emirates Road. Seven are dead, nine injured. The Indian Consulate is at the hospital.",
    "slug": "dubai-emirates-road-crash-seven-indian-workers-killed-minibus-truck-20260609",
    "category": "news",
    "vertical": "news",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Dubai_Highway_%285647316726%29.jpg/1280px-Dubai_Highway_%285647316726%29.jpg",
    "image_caption": "A multilane highway in Dubai, similar to Emirates Road where the fatal crash occurred",
    "image_attribution": "Wikimedia Commons",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "sources": json.dumps(["IANS", "PTI", "Dubai Police", "Indian Consulate Dubai"]),
    "body": """Seven Indian workers were killed and nine others injured on Monday when the minibus carrying them slammed into the back of a truck that had stalled on Emirates Road in Dubai. It was the kind of accident that kills blue-collar migrant workers in the Gulf with grim regularity — mechanical failure meets human error on a high-speed highway — and it will barely register in most news cycles. For the families in India waiting for monthly remittances that will no longer arrive, it will register for the rest of their lives.

Brigadier Juma Salem bin Suwaidan, Director of the General Department of Traffic at Dubai Police, said preliminary investigations showed the truck had come to a sudden stop in the middle of the road after a mechanical breakdown. The minibus driver, he said, "failed to pay attention and maintain a safe distance" and rear-ended the truck at speed. Five of the nine survivors sustained serious injuries; four were classified as moderate. All were rushed to hospital.

The Indian Consulate General in Dubai confirmed the deaths in a post on X: "Deeply saddened by the tragic road accident in Dubai that claimed the lives of several Indian workers." Consular officials visited the hospital, met the injured, and said they were "working closely with local authorities to provide all possible assistance and support."

## The Gulf's Invisible Workforce

India has roughly 8.9 million nationals living and working in the six Gulf Cooperation Council states — the UAE, Saudi Arabia, Qatar, Kuwait, Bahrain, and Oman. They form the backbone of the region's construction, logistics, hospitality, and domestic work sectors. Their remittances, which hit a record $43.5 billion in the January-March quarter of FY26 alone, are a structural pillar of India's balance of payments.

But the workers themselves occupy a precarious space. Many are transported to job sites in minibuses and labour trucks that navigate some of the fastest highways in the world alongside luxury SUVs doing 140 kilometres an hour. Safety standards for worker transport vehicles, while improving, remain inconsistent. Seatbelt enforcement is lax. Overcrowding is common. And when a truck stalls at highway speed, the consequences are catastrophic.

This is not an isolated incident. In 2023, a bus carrying workers in Abu Dhabi crashed into a barrier, killing 12 people including several Indians. In 2019, a similar rear-end collision on a Dubai highway killed 17. The pattern is depressingly familiar: a vehicle breaks down on a fast road, a following vehicle cannot stop in time, and the people inside — almost always migrant workers — pay the price.

## What Happens Next

Dubai Police said specialists from the Traffic Accident Investigation Section were dispatched to the scene to inspect the site and collect evidence. Traffic patrols secured the area and cleared the damaged truck and minibus to restore traffic flow. Investigations are ongoing, but the immediate cause — a stalled truck and an inattentive bus driver — appears straightforward.

The harder questions are systemic. Are worker transport vehicles required to carry the same safety features as passenger vehicles? Are drivers screened and trained for high-speed highway conditions? Are broken-down vehicles removed from active lanes quickly enough?

India's External Affairs Ministry has not yet issued a statement. The Consulate in Dubai remains the primary point of contact for affected families. For those families, the bureaucratic language of "all possible assistance" translates into a few concrete things: repatriation of remains, insurance claims if any coverage exists, and help navigating a foreign legal system in a language most of them do not speak.

Seven workers left home to build someone else's city. They will return in coffins.

*Sources: IANS, PTI, Dubai Police, Indian Consulate General Dubai*"""
}

# ============================================================
# ARTICLE 3: NRI remittances hit record $43.5B
# ============================================================
article3 = {
    "headline": "NRI Remittances Hit $43.5 Billion in One Quarter. The Gulf Crisis Is the Reason.",
    "subheadline": "India posted a surprise current account surplus in Q4 FY26 — and the money flowing home from frightened workers in West Asia is what made it possible.",
    "slug": "nri-remittances-record-43-billion-q4-fy26-current-account-surplus-gulf-crisis-20260609",
    "category": "news",
    "vertical": "news",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_04.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_04.jpg",
    "image_caption": "The Reserve Bank of India headquarters in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "sources": json.dumps(["Reserve Bank of India", "Reuters", "Livemint", "Hindu Business Line", "IDFC First Bank"]),
    "body": """India's current account swung into a surprise surplus in the January-March quarter of FY26, and the single biggest reason is the money that frightened NRI workers in the Gulf sent home. Personal transfer receipts — the Reserve Bank of India's term for remittances from Indians working overseas — surged to $43.5 billion in Q4 FY26, up from $36.9 billion in the preceding quarter and $33.9 billion a year ago. It is the highest single-quarter remittance figure India has ever recorded.

The data, released by the RBI on Monday, showed the current account surplus at $7.1 billion, or 0.7 percent of GDP — a sharp reversal from the $13.2 billion deficit in Q3 FY26. For the full fiscal year, the current account deficit stood at $25.2 billion, or 0.6 percent of GDP, roughly in line with the previous year.

The numbers tell a story that is part relief, part alarm. The surplus is good news for a country under siege from rising oil prices and global uncertainty. But the surge in remittances is not a sign of prosperity — it is a sign of fear.

## Why the Money Is Flowing Home

Gaura Sengupta, Chief Economist at IDFC First Bank, identified the driver bluntly: "The positive surprise on the current account was due to remittances. The West Asia crisis may have resulted in precautionary transfer of funds."

Roughly 8.9 million Indians live and work in the Gulf Cooperation Council countries. As the US-Iran war has intensified and the Strait of Hormuz has narrowed to a trickle of its former traffic, workers across the UAE, Saudi Arabia, Qatar, and Kuwait have been moving money out — hedging against the possibility that the conflict disrupts their employment, their banks, or their ability to transfer funds at all.

It is a rational response to an irrational situation. The Hormuz blockade has upended energy markets, spiked inflation across the region, and created real anxiety about economic stability in countries whose wealth is built on oil exports and the free movement of capital through the strait. Workers are not sending money home because they earned more. They are sending it because they may not be able to later.

## The Services Cushion

Remittances were not the only bright spot. Net services receipts — driven by India's IT and business process outsourcing sectors — rose to $60.4 billion in Q4 from $53.3 billion a year ago. Computer services and other business services led the gains, underscoring India's continued dominance as the world's back office even as merchandise trade weakens.

The merchandise trade deficit, however, widened sharply to $83.4 billion in the quarter, up from $59.3 billion a year ago. Rising crude oil prices are the primary culprit. India imports roughly 85 percent of its crude, and the Hormuz-driven price spike has ballooned the energy import bill.

## The FY27 Storm Ahead

The Q4 surplus, welcome as it is, may be the calm before a much rougher year. IDFC First Bank forecasts a current account deficit of 2.4 percent of GDP for FY27, assuming an average crude price of $90 per barrel — a level that is now plausible given the Apache helicopter shootdown over Hormuz and the collapse of ceasefire momentum.

India's balance of payments recorded a surplus of $7.2 billion in Q4, but for the full year FY26, it was in deficit to the tune of $23.6 billion. Foreign exchange reserves declined by $23.6 billion over the year, compared to just $5 billion the year before. The RBI's emergency measures — concessional swaps for FCNR deposits, relaxed leverage on NRI accounts — are designed to attract dollar inflows and rebuild the buffer.

The irony is not lost on economists: India's external accounts are being rescued by the very crisis that threatens to wreck them. Gulf workers are sending money home because they fear the war will strand them. That money is keeping India's current account afloat. But if the war drags on, those same workers may lose their jobs, their visas, and their ability to remit at all.

For now, $43.5 billion in a single quarter is a record. Whether it is a high-water mark or a warning depends on what happens next in the Strait of Hormuz.

*Sources: Reserve Bank of India, Reuters, Livemint, Hindu Business Line, IDFC First Bank*"""
}

# Insert all articles
articles = [
    ("Apache Hormuz", article1),
    ("Dubai Workers", article2),
    ("NRI Remittances", article3),
]

for name, article in articles:
    code, body = insert_article(article)
    if code == '201':
        try:
            resp = json.loads(body)
            if isinstance(resp, list) and resp:
                print(f"✓ {name}: inserted (id={resp[0].get('id', 'N/A')}, slug={resp[0].get('slug', 'N/A')})")
            else:
                print(f"✓ {name}: inserted (HTTP {code})")
        except:
            print(f"✓ {name}: inserted (HTTP {code})")
    else:
        print(f"✗ {name}: HTTP {code}")
        print(f"  Response: {body[:300]}")
