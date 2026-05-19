#!/usr/bin/env python3
"""Videshi Writer — NEWS categories (news, nri-world, technology, markets-finance)
Run: 2026-05-19 ~03:42 PDT
"""
import os, json, requests, sys
from datetime import datetime, timezone

SUPA_URL = os.environ["SUPABASE_URL"]
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ["SUPABASE_ANON_KEY"])
HEADERS = {
    "apikey": SUPA_KEY,
    "Authorization": f"Bearer {SUPA_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def supa(method, path, data=None, params=None):
    url = f"{SUPA_URL}/rest/v1/{path}"
    r = requests.request(method, url, headers=HEADERS, json=data, params=params)
    if r.status_code >= 400:
        print(f"ERROR {r.status_code}: {r.text}")
        sys.exit(1)
    return r.json() if r.text else None

# ── Article 1: Telangana Student I-65 Crash ─────────────────────────────
art1 = {
    "topic_id": "80865e39-8e18-43ce-9ea1-1f1a68ee145b",
    "headline": "She Was Riding Home From Her Part-Time Job on Boxes of Mangos. Navya Gadusu Never Made It.",
    "subheadline": "A 25-year-old Telangana MS student was killed on Interstate 65 near Chicago after a minivan — with its rear seats removed and five passengers sitting unrestrained on fruit crates — was struck from behind at highway speed.",
    "body": """Navya Gadusu left Cheruvugattu village in Telangana's Nalgonda district two years ago to chase a Master of Science degree in the United States. On Saturday night, she was riding home from a part-time job in a red minivan on northbound Interstate 65 near Crown Point, Indiana, when a Chevrolet Suburban slammed into the vehicle from behind. She was pronounced dead at 12:16 AM on Sunday at Franciscan Health Crown Point. She was 25.

The details of the crash, as pieced together by Indiana State Police and local media, are as harrowing as they are preventable.

**A Minivan With No Rear Seats**

The minivan was carrying seven adults. Only the two front seats were installed. The remaining five passengers — Navya among them — were sitting on boxes of mangos in the cargo area, without seat belts or any restraint. The van was travelling in the right lane at roughly 10 to 15 mph, following another vehicle that had broken down and was limping along the highway.

The driver of a Chevrolet Suburban, approaching at normal interstate speed, did not realise how slowly the minivan was moving. He swerved left to avoid it but clipped the van's rear-left side, sending it careening off the road and into a ditch. The disabled vehicle ahead was not hit.

Four people were rushed to local hospitals and later transferred to trauma centres in the Chicago area. Three sustained serious injuries. Navya died of blunt-force traumatic injuries.

**A Village in Grief**

In Cheruvugattu, the news arrived through Navya's friends in the US before any official channel could reach her family. Her relatives told ANI they had immediately contacted Telangana minister Komatireddy Venkat Reddy and were coordinating with the Indian Embassy.

The Indian Consulate General in Chicago issued a statement expressing "heartfelt condolences" and confirming it was in contact with Gadusu's family and friends assisting the injured. Northbound I-65 was shut for two hours while investigators worked the scene.

**A Pattern That Won't Stop**

Navya's death is not an isolated tragedy. It lands in a grim and growing catalogue of Indian students killed in accidents, assaults, and unexplained circumstances across the United States. In the past two years alone, families in Telangana, Andhra Pradesh, Karnataka, and Gujarat have received the same devastating phone call — a child sent abroad for a better future, returned in a coffin.

What makes this case particularly wrenching is its preventability. The minivan had been deliberately stripped of its rear seating. Five people were perched on fruit crates on a highway where traffic routinely moves at 70 mph. No seat belts. No crash protection. Indiana State Police are still investigating whether any traffic violations will be filed.

The arrangement — passengers packed into cargo space, following a broken-down car at walking speed on an interstate — speaks to the economic realities many Indian students navigate in America. Part-time jobs with odd hours. Shared rides to save money. Improvised transport that would never pass scrutiny but becomes normalised through repetition.

**What NRI Families Should Know**

Road crashes remain the leading cause of non-natural death for young Indians in the United States. The National Highway Traffic Safety Administration recorded over 40,000 traffic fatalities in the US in 2024. Indian students, who often lack their own vehicles and rely on shared rides with acquaintances, are disproportionately exposed to unsafe arrangements — overcrowded cars, unfamiliar drivers, vehicles with mechanical issues.

Consular officials have repeatedly urged Indian students to avoid unlicensed ride-shares, always wear seat belts, and report unsafe vehicles. But advice only travels so far when the alternative is a $60 Uber after a midnight shift.

**What's Next**

The Indiana State Police investigation is ongoing. The Lake County Coroner's Office has completed its report. Navya Gadusu's family is working with Indian consular officials to repatriate her remains to Nalgonda.

She had gone to America to study. She was riding home from work. She was sitting on a box of mangos. And now she is gone.""",
    "diaspora_angle": "Navya Gadusu's death on I-65 highlights the dangerous transit conditions many Indian students endure in the US — overcrowded vehicles, stripped seating, no restraints — driven by economic pressures that consular advisories alone cannot fix.",
    "vertical": "diaspora",
    "tags": ["Indian Students", "NRI Safety", "Road Accident", "Telangana", "Chicago", "US Safety", "Student Deaths Abroad"],
    "urgency": None,
    "sources": [
        {"url": "https://www.nripage.com/articles/road-accidents/2026/05/18/indian-student-navya-gadusu-killed-in-i-65-crash-near-crown-point", "name": "NRI Page — Indian Student Navya Gadusu Killed in I-65 Crash"},
        {"url": "https://www.dailyprabhat.com/24-year-old-telangana-student-killed-in-us-road-accident-near-chicago/", "name": "Daily Prabhat (ANI) — Telangana student killed in US road accident"},
        {"url": "https://www.asiannews18.com/telangana-student-navya-dies-road-accident-chicago", "name": "Asian News 18 — Telangana student Navya dies in road accident"},
    ],
    "slug": "navya-gadusu-telangana-student-killed-i65-crash-chicago-20260519",
    "word_count": 720,
    "status": "published",
    "is_featured": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "category": "nri-world",
}

# ── Article 2: Lenskart Smart Glasses ────────────────────────────────────
art2 = {
    "topic_id": "4114eac0-2697-4cdf-b1f0-c966d83ceaa7",
    "headline": "Lenskart Just Launched India's Answer to Meta Ray-Bans — and It Speaks Hinglish",
    "subheadline": "B by Lenskart ships with the same Qualcomm chip as Meta's smart glasses, a Gemini-powered AI assistant fluent in 40+ languages, and a price tag that undercuts every Western competitor.",
    "body": """For the past two years, the smart glasses market has been a two-horse race between Meta's Ray-Ban partnership and whatever prototype a Chinese manufacturer happened to demo at CES. India — the world's largest eyewear market by volume — has been a spectator. That changed this month.

Lenskart, the Faridabad-founded company that has fitted more Indian faces with glasses than any other brand, has launched B by Lenskart: a pair of AI-powered smart glasses engineered in India, priced for India, and built around an AI assistant that understands Hinglish out of the box.

**The Hardware**

The spec sheet is surprisingly competitive. B by Lenskart runs on Qualcomm's Snapdragon AR1 — the same chip inside Meta's Ray-Ban smart glasses — paired with a 12-megapixel Sony camera that shoots 4K stills and HD video. The frame weighs 40 grams, which Lenskart claims makes it the lightest smart glasses in its class. Three microphones and directional speakers handle calls and music with three sound modes: Discreet, Normal, and Boosted.

The charging case delivers up to 48 hours of juice on the go. A temple-tip cable lets the glasses charge off a phone or power bank while still being worn — a small but clever concession to Indian commuters who may not have a desk to dock at. Japanese ultra-thin blue light lenses come standard. An LED indicator lights up whenever the camera is recording, the same privacy cue Meta adopted after early backlash.

**Buddy: The AI That Gets Indian Context**

The real differentiator is Buddy, B by Lenskart's AI assistant powered by Google's Gemini. Buddy understands more than 40 languages including natural Hinglish and several Indian regional languages — a feature no Western smart glasses offer. More importantly, Buddy uses the camera to see what the wearer sees and provide contextual responses in real time.

Ask it to read a restaurant menu, translate a road sign, identify a plant, or summarise a document you are looking at, and it responds in whichever language feels natural. For a market where code-switching between English and Hindi (or Tamil, Telugu, Bengali) is the norm rather than the exception, this is not a gimmick. It is a baseline requirement that Meta's glasses still cannot meet.

**Price and Demand**

B by Lenskart will retail at ₹27,000 at commercial launch — roughly $320, which puts it in the same bracket as Meta Ray-Ban smart glasses in the US. But early-access customers who joined the waitlist (opened March 31, 2026) can grab a pair for ₹22,000, approximately $260. As of May 12, more than 35,000 people had registered — a signal that Indian consumers are ready for smart eyewear if the price and language support are right.

The product first appeared at Lenskart's IPO event in November 2025, positioning it as the company's flagship hardware play as it transitions from a purely retail eyewear brand to a wearable technology platform.

**Why This Matters for the Diaspora**

For NRIs, the significance is less about buying a pair of Lenskart glasses in New York and more about what the product represents. An Indian company, with Indian engineering, building a device that competes head-to-head with Meta on specs and undercuts it on price — in a category that Silicon Valley has owned since Google Glass.

Peyush Bansal, Lenskart's co-founder and CEO, was explicit about the ambition: "We wanted to create smart glasses that are eyewear first — comfortable, stylish, and practical enough to be worn all day. This is our first step into wearable technology, and we are excited to build this category alongside our customers in India before taking it to global markets."

The "India first, global next" strategy mirrors what companies like Jio, Ola Electric, and Zoho have attempted in their respective categories. Whether Lenskart can actually crack Western markets remains to be seen, but the template — build for Indian complexity first, then export — is becoming a recognisable playbook.

**What's Next**

Early-access shipments are rolling out now through the Lenskart app and website. The companion app manages media storage, settings, and conversations with Buddy. Commercial launch at ₹27,000 is expected in the coming weeks. Lenskart has not yet announced plans for international availability.""",
    "diaspora_angle": "An Indian company has built smart glasses that match Meta's hardware and speak Hinglish natively — a landmark for the 'build in India, compete globally' thesis that NRIs in tech have championed for years.",
    "vertical": "technology",
    "tags": ["Lenskart", "Smart Glasses", "Google Gemini", "AI", "Wearable Tech", "Made in India", "Peyush Bansal"],
    "urgency": None,
    "sources": [
        {"url": "https://technuter.com/artificial-intelligence/lenskart-brings-ai-powered-smart-glasses-to-india-with-early-access-launch.html", "name": "Technuter — Lenskart brings AI-powered smart glasses to India"},
        {"url": "https://www.newspointapp.com/english/tech/b-by-lenskart-smart-glasses-launched-for-early-access-price-features-and-all-the-details-toi/articleshow/145048208ad10aa07707de12271f4d4a6549c37a", "name": "NewsPoint — B by Lenskart smart glasses: Price, features, details"},
        {"url": "https://cellit.in/lenskart-brings-ai-powered-smart-glasses-india", "name": "CellIT — Lenskart AI-powered smart glasses early access launch"},
    ],
    "slug": "lenskart-b-smart-glasses-gemini-india-meta-competitor-20260519",
    "word_count": 730,
    "status": "published",
    "is_featured": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "category": "technology",
}

# ── Article 3: Bombay HC Bulldozer Culture ───────────────────────────────
art3 = {
    "topic_id": "2e648a58-e53c-4161-ace7-9816461cb16f",
    "headline": "Bombay High Court Draws a Line: 'Don't Allow Bulldozer Culture to Enter Maharashtra. This Is Not UP.'",
    "subheadline": "A division bench slammed the Chhatrapati Sambhajinagar municipal corporation for demolishing an AIMIM corporator's home without notice, calling the action 'arbitrary' and warning against the spread of extrajudicial demolitions.",
    "body": """The Bombay High Court's Aurangabad bench delivered one of the sharpest judicial rebukes against demolition-as-governance in recent memory on Monday, condemning the Chhatrapati Sambhajinagar Municipal Corporation for razing properties linked to AIMIM corporator Mateen Patel and resident Hanif Khan without following basic legal procedure.

"Don't allow bulldozer culture to enter Maharashtra," Justice Siddheshwar Thombre told the civic body's lawyers. "This is not UP or Bihar."

The remark — pointed, political, and deliberately geographic — lands in a debate that has consumed Indian public life for the past four years: whether state governments can use demolition drives as a tool of punishment against those accused of crimes, particularly in communally charged contexts.

**What Happened in Sambhajinagar**

On May 13, the Chhatrapati Sambhajinagar Municipal Corporation (CSMC) carried out a demolition drive targeting Mateen Patel's residence and office. Patel is a sitting AIMIM corporator. In the same drive, a house allegedly linked to a TCS employee evading arrest in a criminal case was also razed.

But the demolitions did not stop at the named targets. Adjacent properties — including a building material shop owned by Amjad Khan and a house registered in Patel's father's name — were also destroyed without prior intimation. Amjad Khan told the court his shop had valid permissions under the Gunthewari regularisation scheme and claimed losses exceeding ₹20 lakh.

The division bench noted that mandatory safeguards prescribed by the Supreme Court — including a 15-day notice period — were not followed. "No compliance with the last notice was made. The action is arbitrary. The action has made the entire family homeless," the bench stated.

The court also questioned whether the civic body had bothered to identify which specific portions of the structures were illegal before bringing in the bulldozers. "The authorities should have scrutinised which part or portion of the house was illegal," the bench observed.

**The 'Bulldozer Model' and Its Spread**

What makes the Bombay High Court's intervention significant is its explicit attempt to prevent a governance model from migrating across state lines.

The so-called bulldozer model gained national prominence in Uttar Pradesh under Chief Minister Yogi Adityanath, where demolitions of properties belonging to accused persons — often conducted within hours of an alleged crime — became a signature law-and-order tactic. The approach was replicated in Madhya Pradesh and, to varying degrees, in other BJP-governed states.

Critics, including the Supreme Court itself, have warned that demolitions carried out without due process amount to collective punishment and violate the right to shelter. In a landmark September 2024 ruling, the Supreme Court laid down detailed guidelines requiring advance notice, identification of specific illegal portions, and an opportunity for the owner to respond before any demolition.

The Sambhajinagar demolitions appear to have disregarded every one of those safeguards.

**Why NRIs Should Watch This**

For Indians abroad who own property in India — or whose families do — the bulldozer debate is not abstract. Property rights, municipal discretion, and the rule of law directly affect the security of NRI investments in real estate, which the RBI estimates at tens of billions of dollars annually.

The question the Bombay High Court is grappling with is fundamental: can a municipal corporation demolish your home because someone in it is accused of a crime, without giving you a chance to respond? If you are an NRI with ancestral property in a city where political tensions run high, the answer to that question matters enormously.

More broadly, the judiciary's willingness to draw geographic and procedural lines — "This is not UP" — signals that at least some courts view the bulldozer approach not as efficient governance but as extrajudicial overreach that must be contained.

**What's Next**

The matter is listed for further hearing on June 15. The CSMC's assistant government pleader had argued that the petitions were "infructuous" since the buildings were already demolished — a position the bench appeared unimpressed by. Advocates for the petitioners said the demolition was carried out despite assurances that legal procedure would be followed.

The homes are gone. The question now is whether the court will order compensation, hold officials accountable, or simply issue directions that arrive too late for the families already sleeping without a roof.""",
    "diaspora_angle": "NRIs with property in India should pay close attention: the Bombay HC is drawing a line against demolitions carried out without notice, a practice that directly threatens the security of diaspora real estate investments.",
    "vertical": "law",
    "tags": ["Bombay High Court", "Bulldozer Culture", "Maharashtra", "Property Rights", "Supreme Court Guidelines", "AIMIM", "Demolitions"],
    "urgency": None,
    "sources": [
        {"url": "https://bharathorizon.com/politics/law-order/bombay-hc-slams-sambhajinagar-demolition-warns-against-bulldozer-culture.html", "name": "Bharat Horizon — Bombay HC slams Sambhajinagar demolition, warns against bulldozer culture"},
    ],
    "slug": "bombay-hc-bulldozer-culture-maharashtra-sambhajinagar-20260519",
    "word_count": 740,
    "status": "published",
    "is_featured": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "category": "news",
}

articles = [art1, art2, art3]

for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"INSERTING ARTICLE {i}: {art['headline'][:60]}...")
    result = supa("POST", "p2_articles", art)
    article_id = result[0]["id"] if result else "UNKNOWN"
    print(f"  → Article ID: {article_id}")
    print(f"  → Slug: {art['slug']}")
    print(f"  → Category: {art['category']}")

    # Update topic status to published
    topic_id = art["topic_id"]
    print(f"  → Marking topic {topic_id} as published...")
    supa("PATCH", f"p2_topics?id=eq.{topic_id}", {"status": "published"})
    print(f"  ✓ Topic marked published")

print("\n\n✅ All 3 articles inserted successfully.")
