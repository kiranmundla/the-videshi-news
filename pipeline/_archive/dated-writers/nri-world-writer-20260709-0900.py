#!/usr/bin/env python3
"""NRI World Writer — July 9, 2026 09:00 AM PT run"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load Supabase env
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


# ─────────────────────────────────────────────
# ARTICLE 1: Modi Melbourne event outcomes
# ─────────────────────────────────────────────

article1_body = """Australia and India struck a historic uranium export deal on Thursday in Melbourne, as Prime Minister Narendra Modi wrapped up the centrepiece of his three-nation Indo-Pacific tour with a CEO forum, a landmark energy agreement, and a stadium reception that drew thousands of Indian Australians — and a handful of determined opponents.

The uranium arrangement, finalised during bilateral talks between Modi and Australian Prime Minister Anthony Albanese, commits Australia to exporting uranium for India's civilian nuclear energy programme. India has targeted 100 gigawatts of nuclear capacity by 2047 and has long coveted Australia's reserves — the world's largest — while Canberra wants to reduce its trade dependence on China.

"Australia and India are close partners and even closer friends," Albanese told reporters after the signing. "The arrangement facilitates Australian uranium exports to India to help increase the share of non-fossil fuel power capacity."

A nuclear cooperation pact between the two countries has existed since 2014, but actual exports remained minimal over fears the material could be diverted to India's weapons programme. The new agreement locks in safeguards ensuring nuclear fuel is used exclusively for peaceful purposes.

## Half a Billion Dollars in a Single Announcement

The energy deal was not the only headline. AustralianSuper, Australia's largest pension fund with more than A$400 billion in assets under management, announced it would invest a further A$500 million (roughly $347 million) in India's National Investment and Infrastructure Fund. For a diaspora community that has spent decades arguing India is a reliable destination for long-term capital, the commitment was a validation in hard currency.

Modi used the India-Australia CEO Forum to make his pitch directly. "India provides a safe, stable and sustainable growth option for your funds," he told the room of business leaders, urging investment in India's road, port, rail, and urban infrastructure. He also floated cooperation on low-carbon aluminium projects, signalling an expansion of the two countries' energy partnership beyond uranium and renewables.

Albanese, evidently impressed, called Modi a "living bridge" between Australia and India — language that has historically been used to describe the diaspora itself.

## Outside Marvel Stadium, Two Australias

The warmth inside Melbourne's corporate conference rooms collided with something uglier outside Marvel Stadium, where Modi was scheduled to address the diaspora on Thursday evening.

A group of roughly two dozen far-right protesters gathered outside the arena, shouting anti-immigration slogans and holding banners demanding the expulsion of Indians from Australia. They were comprehensively outnumbered — by thousands of people waving Indian tricolours, banging drums, and queuing for entry in Melbourne's winter chill.

Police maintained a heavy presence. The confrontation, such as it was, lasted longer in social media clips than it did on the ground.

The scene encapsulated a tension that Indian Australians have navigated with increasing frequency. Around one million people in Australia claim Indian ancestry — making them the country's largest overseas-born population. That visibility has brought both political clout and backlash.

## The Diaspora's Growing Weight

Modi's three-nation tour — Indonesia, then Australia, then New Zealand — has been an exercise in diaspora diplomacy. In Jakarta he signed defence deals worth ₹5,500 crore, including the BrahMos cruise missile system. In Melbourne, the deliverables were economic and symbolic: the uranium deal, the AustralianSuper investment, and the "living bridge" framing that positions the Indian community not as a lobbying group but as a structural pillar of the bilateral relationship.

For the million-strong Indian Australian community, the takeaway was straightforward: when their prime minister visits, deals get signed, capital moves, and the host country's leader reaches for the most generous metaphors available. The far-right protesters outside the stadium made it equally clear that not everyone is celebrating.

Modi departs Melbourne on Friday for Auckland, where he will become the first Indian Prime Minister to visit New Zealand in four decades. Three hundred and fifty thousand Indian New Zealanders are expected to greet him — and, if Melbourne is any guide, a few will be there to object."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Uranium, Half a Billion Dollars, and a Wall of Indian Flags: What Actually Happened When Modi Landed in Melbourne",
    "subheadline": "Australia struck a historic uranium export deal, its largest pension fund committed $347 million to India, and far-right protesters outside Marvel Stadium were outnumbered a thousand to one. For a million Indian Australians, the message was hard to miss.",
    "slug": make_slug("modi-melbourne-uranium-deal-australiansuper-diaspora-marvel-stadium"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "One million Indian Australians are the country's largest overseas-born population. The uranium deal and AustralianSuper investment validate the community's decades-long argument that India is a reliable destination for Australian capital — while the far-right protest outside Marvel Stadium underscores the backlash their visibility now attracts.",
    "tags": ["nri", "diaspora", "australia", "modi", "uranium", "investment", "marvel-stadium", "melbourne"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/indias-modi-meet-australias-albanese-with-uranium-defence-agenda-2026-07-08/"},
        {"name": "The India Eye", "url": "https://theindianeye.com/"},
        {"name": "The Business Standard", "url": "https://thehindubusinessline.com/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Marvel_Stadium_from_an_aerial_perspective._Feb_2019.jpg/1280px-Marvel_Stadium_from_an_aerial_perspective._Feb_2019.jpg",
    "image_caption": "Marvel Stadium in Melbourne's Docklands, venue for the 'Melbourne Meets Modi' diaspora event",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 2: Pratik Trivedi becomes CEO of CTS Corporation
# ─────────────────────────────────────────────

article2_body = """On July 6, Pratik Trivedi became the Chief Executive Officer and President of CTS Corporation, a NASDAQ-listed manufacturer of sensors, connectivity components, and actuators that serves the aerospace, defence, medical, and transportation industries. The appointment, which came after a focused two-year succession planning process, adds another Indian-origin name to the expanding roster of diaspora executives running American public companies.

Trivedi's promotion from Chief Operating Officer was announced on June 25. His predecessor, Kieran O'Sullivan, who held the CEO role for 14 years, will remain as Executive Chair. It was the kind of orderly handover that corporate boards design to signal stability — and, in CTS's case, the market agreed. The company's stock has risen nearly 38 per cent over the past 12 weeks, and analysts at Zacks gave it their highest rating.

## A Career Built in American Industry

Before joining CTS in April 2024, Trivedi held senior roles at two of America's most consequential industrial firms. At Eaton, the power management company with $23 billion in annual revenue, he oversaw business units spanning electrical, aerospace, and vehicle segments. At Cummins, the engine and power solutions giant, he gained deep operational experience in the kind of global manufacturing networks that CTS depends on.

His trajectory follows a familiar pattern for Indian-origin executives in American industry: technical education, operational roles in large manufacturers, a proven record of scaling complex businesses, and — eventually — the top job. What distinguishes his appointment is the company itself. CTS is not a household name, but its products are embedded in systems most people interact with daily. The company's sensors help aircraft fly safely, its actuators position medical equipment precisely, and its frequency control products keep telecommunications networks synchronised.

## The Expanding Indian-Origin C-Suite

Trivedi's appointment arrives in a season thick with similar headlines. Shailesh Jejurikar, an IIM Lucknow alumnus, took over as CEO of Procter & Gamble in January after 35 years at the consumer goods giant. Salim Ramji, of Indian-Tanzanian descent, leads Vanguard Group and its $9 trillion in assets. Sabih Khan, from Moradabad, now serves as Apple's Chief Operating Officer.

The pattern extends beyond the corner office. A recent analysis by The Videshi found that Indian-origin engineers now lead AI divisions at OpenAI, Anthropic, and Apple — the companies that are, arguably, building the infrastructure of the next economy.

What these appointments share is not just ethnicity but a specific career architecture: deep technical expertise, long tenures that build institutional knowledge, and a willingness to spend years in operational roles that most MBA graduates would find unglamorous. Trivedi spent two decades learning how factories work before being asked to run one.

## What CTS Gets

For CTS, the timing matters. The company projects sales between $560 million and $580 million for 2026, with adjusted earnings per share of $2.35 to $2.45 — an 18 per cent growth rate in markets that reward consistency. Its customers are aerospace prime contractors, medical device manufacturers, and defence agencies: buyers who value predictability over disruption.

Robert Profusek, CTS's Lead Independent Director, described the succession as a plan designed "to establish a foundation for CTS's long-term growth and stability." That is corporate-speak, but the substance is real. Trivedi inherits a company with strong margins, diversified end markets, and a product portfolio that benefits from every major secular trend — electrification, autonomous vehicles, precision medicine — without depending on any single one.

For the diaspora, the appointment is a quiet milestone. Not every Indian-origin CEO runs a trillion-dollar asset manager or a consumer brand. Some run the companies that make the sensors inside the machines that keep the world precise. That matters too."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "From Eaton's Factory Floors to a NASDAQ Corner Office: Pratik Trivedi Is CTS Corporation's New Chief Executive",
    "subheadline": "The Indian-origin executive took the helm of the $560-million sensor and components maker on July 6, extending the diaspora's quiet takeover of American industry's C-suite.",
    "slug": make_slug("pratik-trivedi-cts-corporation-ceo-indian-origin-nasdaq"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Trivedi's appointment extends the growing list of Indian-origin CEOs running American public companies — from P&G to Vanguard to Apple's COO — a pattern rooted in deep technical expertise and long operational tenures that the diaspora's career architecture uniquely produces.",
    "tags": ["nri", "diaspora", "ceo", "indian-american", "cts-corporation", "nasdaq", "pratik-trivedi", "corporate-leadership"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Intellectia / NASDAQ", "url": "https://intellectia.ai/news/stock/cts-corp-appoints-new-ceo-effective-july-2026"},
        {"name": "Seeking Alpha", "url": "https://seekingalpha.com/"},
        {"name": "CTS Corporation", "url": "https://www.ctscorp.com/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/18471565/pexels-photo-18471565.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Industrial sensors and electronic components of the kind CTS Corporation manufactures for aerospace, medical, and defence clients",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}


# ─────────────────────────────────────────────
# Insert both articles
# ─────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
