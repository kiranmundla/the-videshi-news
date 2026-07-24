#!/usr/bin/env python3
"""NRI World writer – 2026-06-28 17:00 PT run.

Articles:
1. Kunal Shah appointed Global Head of WhatsApp
2. INS Sudarshini at America's Sail250 celebrations
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── env ──────────────────────────────────────────────────────────────────────
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


# ── articles ─────────────────────────────────────────────────────────────────
articles = [
    # ── Article 1: Kunal Shah → WhatsApp ──────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "The App the Diaspora Lives On Just Got an Indian Boss",
        "subheadline": "Kunal Shah, who built CRED from a million dollars of personal capital into a $4.5 billion fintech, will lead WhatsApp globally — the clearest sign yet that Meta's future runs through India.",
        "slug": make_slug("kunal-shah-whatsapp-ceo-cred-meta-indian-diaspora-fintech"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "WhatsApp is the communication backbone of virtually every diaspora family — the morning prayers forwarded from Ahmedabad, the group chat that settles who is cooking for the potluck, the voice notes that keep grandparents present across oceans. An Indian founder now runs it.",
        "tags": ["nri", "diaspora", "technology", "whatsapp", "cred", "kunal-shah", "meta"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/metas-whatsapp-be-led-by-indian-startup-founder-kunal-shah-2026-06-22/"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/best-of-the-week-whatsapp-gets-a-new-boss-india-gets-the-spotlight-11751038860396.html"},
            {"name": "MediaNama", "url": "https://www.medianama.com/2026/06/223-kunal-shah-steps-down-as-cred-ceo-to-lead-whatsapp-at-meta/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/22/cred-founder-kunal-shah-to-lead-whatsapp-globally/"},
            {"name": "Global Leaders Today", "url": "https://globalleaderstoday.online/meta-names-cred-founder-kunal-shah-as-global-head-of-whatsapp/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/83/Kunal_Shah_in_FreeCharge_T-Shirt_%28cropped%29.jpg",
        "image_caption": "Kunal Shah, founder of CRED and the new global head of WhatsApp",
        "image_attribution": "Wikimedia Commons",
        "body": """There is no app more synonymous with the Indian diaspora than WhatsApp. It is the family group chat that never sleeps, the voice note from a mother who refuses to type, the forwarded-as-received news bulletin that arrives before any newspaper. More than 500 million Indians use it. For the roughly 37 million Indians scattered across the globe, it is the umbilical cord to home.

That app now has an Indian at the helm.

On June 22, Meta announced that Kunal Shah — the 47-year-old founder of CRED, one of India's most closely watched fintech startups — would take over as global head of WhatsApp, succeeding Will Cathcart, who had led the platform since 2019. Alongside the appointment, Meta disclosed a $900 million investment in CRED at a $4.5 billion valuation, giving it a 20 percent minority stake. Shah will step back from day-to-day operations at CRED, where Miten Sampat, head of strategy and finance since 2020, becomes interim CEO.

The appointment slots Shah into a lineage of Indian-born executives now running the world's most consequential technology platforms — Satya Nadella at Microsoft, Sundar Pichai at Alphabet, Arvind Krishna at IBM, Shantanu Narayen at Adobe. But Shah's path diverges from the typical playbook. He has no engineering degree, no Stanford MBA, no decade-long climb through a Valley hierarchy. He built businesses in India, for India, and got noticed precisely because of what that taught him.

## From FreeCharge to CRED to Menlo Park

Shah's first major venture, FreeCharge, turned mobile recharges into a gateway for digital payments. Snapdeal acquired it in 2015 for a reported $450 million. After a few years of angel investing and deliberate pause — a rarity in Indian startup culture — Shah launched CRED in 2018 with $1 million of his own money. The premise was deceptively simple: reward people for paying their credit card bills on time.

Between 2019 and 2025, CRED grew to 17 million members and built a full stack of financial services — payments, lending, insurance, wealth, and credit cards — generating annual revenue of roughly $325 million. It conducted four ESOP buybacks. In 2026, it posted its first profitable quarter. The company raised more than $900 million from global investors before Meta's separate $900 million injection.

"CRED is ready for its next phase," Shah wrote on X, announcing his departure. "I am stepping back and @miten steps in as interim CEO."

Meta's chief product officer, Chris Cox, framed the hire in terms that went beyond the usual corporate lauding. "We were looking for a leader with an intuitive grasp of WhatsApp's global product opportunity, the ability to navigate the disruption expected from artificial intelligence, and the leadership skills required to run the world's largest communication platform," Cox wrote in an internal memo reviewed by Reuters. He called Shah "one of India's most respected entrepreneurs."

## Why This Matters to the Diaspora

Mark Zuckerberg has made no secret of his desire to turn WhatsApp into something closer to a superapp — a single platform for messaging, payments, commerce, and customer service. WhatsApp Pay has been live in India since 2020 but has struggled against PhonePe and Google Pay in the fiercely contested UPI market. WhatsApp's paid business messaging tools, meanwhile, already generate more than $2 billion annually, with Status ads gaining traction.

Shah brings precisely the skill set that job description demands. He understands India's regulatory maze — CRED secured full RBI authorisation as a payment aggregator in March 2026. He understands consumer behaviour in a market where trust is earned, not assumed. And he understands payments architecture from the ground up.

For the diaspora, the implications are direct. WhatsApp is already how millions of NRIs send money home, coordinate family logistics, and stay plugged into communities thousands of miles away. If Shah succeeds in deepening commerce and financial services within the app, the platform could become the single interface through which the diaspora manages its dual life — paying a plumber in Pune from Palo Alto, buying Diwali gifts for cousins in Chennai, splitting a restaurant bill in London.

"While it's come very far, the delta between WhatsApp today and its full potential is massive," Shah said. "I look forward to working with Mark, Chris and the leadership across Meta for the next step in WhatsApp's journey."

## The Bigger Pattern

Shah's appointment is not an isolated data point. It reflects a structural shift in how global technology companies think about leadership. The old model sent Indians to the Valley to manage American products. The new model pulls founders out of India's own startup ecosystem — people who built companies amid power cuts and regulatory thickets and user bases that demand frugal engineering — and hands them global mandates.

Meta's $900 million bet on CRED, twinned with the WhatsApp appointment, makes the strategy explicit. India is not just WhatsApp's largest market. It is the laboratory where the superapp thesis will be proved or disproved. And Meta has decided the person best positioned to run that experiment is someone who has already done it once, at a smaller scale, with his own money on the line.

The diaspora, scrolling through its morning group chats, may not notice the change immediately. But the person deciding what WhatsApp becomes next now understands exactly what those group chats mean.""",
    },
    # ── Article 2: INS Sudarshini at Sail250 ──────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Tall Ship Has Sailed 13,000 Miles to Help America Celebrate Its Birthday. The Diaspora Turned Out to Watch.",
        "subheadline": "INS Sudarshini's five-month voyage from Kochi to Baltimore — with stops in Oman, Egypt, France, and the Canary Islands — culminates in community outreach events that have drawn Indian Americans across the mid-Atlantic.",
        "slug": make_slug("ins-sudarshini-sail250-baltimore-indian-navy-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The ship's community outreach events in Norfolk and Baltimore draw Indian Americans from across the mid-Atlantic corridor — one of the largest concentrations of the diaspora in the US — offering a rare moment of visible Indian presence in a quintessentially American celebration.",
        "tags": ["nri", "diaspora", "indian-navy", "sail250", "baltimore", "cultural-exchange"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/27/ins-sudarshini-arrives-in-baltimore-for-sail250-maryland-celebrations/"},
            {"name": "Ainvest", "url": "https://www.ainvest.com/news/indian-navys-ins-sudarshini-arrives-in-us-for-250th-anniversary-celebrations/"},
            {"name": "7Globe", "url": "https://7globe.in/meet-ins-sudarshini-indian-navys-sailing-ambassador-in-us/"},
            {"name": "Asian News Network India", "url": "https://asiannewsindia.com/indian-navys-tall-ship-ins-sudarshini-arrives-in-baltimore-usa/"},
            {"name": "India Strategic", "url": "https://www.indiastrategic.in/ins-sudarshini-makes-maiden-canary-islands-call-ahead-of-trans-atlantic-voyage-under-lokayan-26/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/2f/INS_Sudarshini_%28A77%29_en-route_to_Sri_Lanka.jpg",
        "image_caption": "INS Sudarshini under sail during a previous transoceanic voyage",
        "image_attribution": "Wikimedia Commons",
        "body": """On June 26, a three-masted barque flying the Indian naval ensign glided into the Port of Baltimore after transiting the Chesapeake and Delaware Canal and passing beneath some of the mid-Atlantic's most storied bridges. INS Sudarshini — her name means "beautiful lady" in Sanskrit — had been at sea, on and off, for five months, covering more than 13,000 nautical miles from her home port of Kochi.

She was not there on a combat mission. She was there for a birthday party — America's 250th.

The Indian Navy's sail training ship is participating in Sail250, the sprawling series of maritime celebrations marking the United States' semiquincentennial. Tall ships from navies around the world are assembling along the eastern seaboard throughout the summer of 2026, and India's contribution is a vessel built at Goa Shipyard, designed by the British naval architect Colin Mudie, and capable of carrying 20 sails across 1,035 square metres of canvas.

## A Voyage Measured in Port Calls

INS Sudarshini's expedition — designated Lokayan 26 by the Indian Navy — began in Kochi in January. The itinerary reads like a study in maritime diplomacy: Oman, Egypt, Malta, France, Morocco, and then a maiden call at Las Palmas in the Canary Islands in April, the first visit by any Indian naval vessel to the Spanish archipelago. From there, the ship made a trans-Atlantic crossing to Norfolk, Virginia, where it joined an international fleet for the Sail250 Virginia celebrations from June 19 to 23.

At Norfolk, INS Sudarshini sailed in the Parade of Sail alongside tall ships from a dozen countries and marched in the City Crew Parade — events attended by tens of thousands of spectators along the Virginia waterfront. The Indian Navy's crew, many of them young cadets learning traditional seamanship aboard the vessel, represented India in a setting normally dominated by the Atlantic maritime powers.

## The Diaspora Angle

What made the Norfolk and Baltimore stops matter beyond naval protocol was the community dimension. The mid-Atlantic corridor — stretching from northern Virginia through Washington, D.C., Maryland, and into Delaware — is home to one of the largest concentrations of Indian Americans in the country. Fairfax County alone has more than 100,000 residents of Indian origin. The Baltimore-Washington metropolitan area adds tens of thousands more.

The Indian Navy said INS Sudarshini would undertake "maritime engagement and community outreach activities" in Baltimore ahead of the Sail250 Maryland events, language that in practice means opening the ship to visitors, hosting receptions, and engaging with the local Indian community. During the earlier Canary Islands stop, the Navy explicitly invited the Indian diaspora to visit the ship and meet the crew — a model it has replicated at subsequent ports.

For Indian Americans accustomed to seeing India's presence at American celebrations limited to a float in a parade or a booth at a cultural festival, a 54-metre sailing ship in Baltimore's Inner Harbour registers differently. It is, as the Navy's own framing puts it, a floating ambassador — one that embodies the concept of "Vasudhaiva Kutumbakam," the Sanskrit phrase meaning "the world is one family" that India has elevated to a diplomatic calling card.

## More Than Symbolism

The Lokayan 26 expedition is not purely ceremonial. It serves a practical training function — cadets aboard INS Sudarshini learn celestial navigation, sail handling, and seamanship skills that cannot be replicated on modern powered vessels. But it also fits into India's broader strategy of expanding its maritime footprint beyond the Indian Ocean, a theatre where the Navy has traditionally been dominant.

India's participation in Sail250 sends a specific signal: that India considers itself not merely an Indian Ocean power but a global maritime nation with the confidence to sail its vessels across oceans and park them alongside the navies of the United States, Britain, France, and Canada.

For the diaspora, the symbolism cuts closer to home. Many Indian Americans in the mid-Atlantic work in defence, intelligence, and government — sectors where India's strategic posture is a daily consideration. Seeing an Indian tall ship at a celebration of American independence creates a quiet resonance: the two democracies, different in scale and history, sharing the same harbour.

## What Comes Next

INS Sudarshini will continue community outreach in Baltimore before the Sail250 Maryland events, which are part of a summer-long series of celebrations across the eastern seaboard. The ship is expected to make additional stops before beginning its return voyage.

The vessel's presence may be temporary, but the image it leaves is not: India's tricolour alongside the Stars and Stripes in one of America's oldest ports, with the Indian diaspora watching from the dock. It is a reminder that the threads connecting India and the United States are not only digital, financial, or diplomatic. Sometimes they are made of canvas and rope, and they have been sailing for five months to get here.""",
    },
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
