#!/usr/bin/env python3
"""NRI World Writer — July 2, 2026 batch."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / "workspace" / ".env.supabase"
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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ─────────────────────────────────────────────
# ARTICLE 1: AAPI Convention in Tampa
# ─────────────────────────────────────────────

art1_body = """When more than two thousand physicians of Indian origin gather at the JW Marriott Tampa Water Street this week, the optics will be hard to miss. The 44th Annual Convention of the American Association of Physicians of Indian Origin — AAPI, the professional body that has represented Indian-origin doctors in the United States for over four decades — opens on July 2 and runs through July 5, colliding deliberately with the nation's 250th Independence Day celebrations.

"The timing is especially meaningful," AAPI President Dr. Amit Chakrabarty said in his message to members. "The convention coincides with the 250th anniversary of America's independence, and AAPI has partnered with the City of Tampa to mark the milestone with a red-carpet civic reception honouring the Indian-American physician community."

## An industry within a diaspora

The numbers tell a quiet but staggering story. Indian-origin physicians now number more than 80,000 across the United States, making them one of the single largest ethnic groups in American medicine. Many arrived decades ago as international medical graduates, filling residency slots in underserved hospitals that domestic graduates would not touch. They stayed, built practices, ran departments, and eventually ran hospitals. Today, Indian-American doctors lead departments at Johns Hopkins, chair boards at community health systems, and serve as deans at medical schools. The profession remains the diaspora's most concentrated corridor of institutional power outside Silicon Valley.

AAPI itself has tracked that arc. Founded in the early 1980s as a networking body for a then-small community of immigrant physicians, it now functions as a lobbying force, a continuing-education platform, and — for many members — a cultural anchor. Its annual convention is equal parts scientific assembly and family reunion.

## Tampa's waterfront, Tampa's welcome

This year's convention, themed "Stronger Together: United in Care, Undivided in Voice," promises what Dr. Chakrabarty has called "the crowning jewel of everything we've built together." The scientific programme features CME sessions curated by world-class faculty, covering clinical advances, emerging technologies, and health policy. A dedicated full-day track for young physicians and medical students signals the organisation's effort to court the next generation.

But AAPICON, as attendees call it, has never been purely clinical. The programme includes global culinary showcases, high-energy cultural performances, and a family-friendly waterfront slate. Dr. Sagar Galwankar, Convention Chair, described the gathering as "not just an assembly — we are creating a celebration of unity, expertise, and cultural heritage."

Dr. Meher Medavaram, AAPI's President-Elect, will formally assume the presidency during the convention — a ritual that doubles as a leadership transfer ceremony watched closely by the community. "Physicians and healthcare professionals from across the country and internationally will convene to participate in the scholarly exchange of medical advances, develop health policy agendas, and encourage legislative priorities for the coming year," she said.

## The diaspora's dual toast

That the convention coincides with July 4 is, for many attendees, the point. Indian-American physicians have long navigated the peculiar duality of immigrant professional life: filing taxes in a country whose medical boards they studied years to pass, while sending remittances to parents in Hyderabad or Coimbatore. A red-carpet reception from the City of Tampa, on the weekend America turns 250, is not merely a nice gesture. It is a recognition that these physicians are not guests in the system. They are load-bearing walls.

Convention Convener Dr. Raghu Juvvadi captured the mood: "This is the year we raise the bar, celebrate our legacy, and shine together on a national stage." Registration is open to AAPI friends and family — a signal, perhaps, that the organisation sees itself not just as a medical body but as a community institution.

For a diaspora that sometimes struggles to be seen as more than a collection of individual success stories, AAPI's Tampa gathering is a reminder that the collective muscle exists. Whether it gets used — for advocacy, for policy, for shaping the next generation of Indian-American healthcare leaders — is the question the next four days may begin to answer."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Two Thousand Indian-Origin Doctors Just Took Over Tampa's Waterfront. The Timing Was Not an Accident.",
    "subheadline": "AAPI's 44th annual convention opens on America's 250th birthday weekend, blending scientific sessions with a red-carpet civic reception from the City of Tampa.",
    "slug": make_slug("aapi-convention-tampa-indian-physicians-america-250th"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian-origin physicians form one of the largest ethnic groups in American medicine. AAPI's convention, timed to America's 250th, is both a professional assembly and a statement of belonging.",
    "tags": ["nri", "diaspora", "aapi", "physicians", "healthcare", "community", "tampa", "july-4th"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Global Net News", "url": "https://globalnet.news/aapis-2026-annual-convention-in-tampa-a-historic-celebration-of-unity-innovation-and-americas-250th-anniversary/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/04/01/aapi-announces-44th-annual-convention-in-tampa-fl/"},
        {"name": "AAPICON 2026", "url": "https://www.aapiconvention.org/"},
        {"name": "South Asian Herald", "url": "https://southasianherald.com/aapi-launches-preparations-for-44th-annual-convention-in-tampa-set-for-july-2026/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6129507/pexels-photo-6129507.jpeg",
    "image_caption": "Healthcare professionals in a hospital setting — Indian-origin physicians form one of the largest ethnic groups in American medicine",
    "image_attribution": "Pexels",
    "body": art1_body.strip(),
}


# ─────────────────────────────────────────────
# ARTICLE 2: YJA Convention in New Jersey
# ─────────────────────────────────────────────

art2_body = """There are 915 spots. Every one of them is gone. The 17th Biennial Convention of Young Jains of America opens this week in New Jersey — July 2 through July 5, the same weekend America turns 250 — and its theme reads like a doctoral thesis on the diaspora condition: "The Art of the In-Between."

For a community whose American footprint is tiny by Hindu or Sikh standards — the Jain population in the United States is estimated at roughly 150,000 to 200,000 — the sell-out is remarkable. All three age cohorts (high school, college, and 22-to-29) filled within days of each registration phase opening. Waitlists opened and filled too. The unsubsidized ticket, priced at $599, was positioned as a way for those who could afford it to cover the actual cost of attendance. Many chose it voluntarily.

## What happens inside

The convention splits neatly between daylight and dark. During the day: breakout sessions on Jainism's core tenets — *ahimsa* (non-violence), *aparigraha* (non-possessiveness), *anekantavada* (multiplicity of viewpoints) — led by a mix of monks who flew in from India, scholars, and young professionals from within the community. The sessions are calibrated for range: first-time attendees get introductory programming; veterans get deep dives on philosophy, professional identity, and faith in a secular world.

After sundown, the convention pivots to cultural spectacle: a talent show, a Garba night, a formal dance, and a series of mixers designed to do what diaspora gatherings have always done — help young people find others who understand the specific texture of their lives.

The food deserves its own paragraph. Every meal served over four days is strictly Jain: no onions, no potatoes, no garlic, no root vegetables, no meat, no animal byproducts. The convention's hospitality suite, open around the clock, stocks only Jain-compliant snacks. In a country where explaining your dietary restrictions at a restaurant requires a small lecture, the relief of eating without caveats is, for many attendees, the convention's most underrated luxury.

## The in-between, defined

The theme — "The Art of the In-Between" — is doing more work than it appears. For second- and third-generation Jain Americans, the "in-between" is not a metaphor. It is Tuesday. It is explaining to a college roommate why you do not eat potatoes. It is practising *pratikraman* (daily introspective meditation) in a dorm room while your hallmates pre-game for a party. It is loving a country whose consumer culture runs on appetites that your faith asks you to examine.

YJA has been building infrastructure for this in-between since its founding. The organisation is run entirely by youth volunteers — more than 250 of them across committees, regional chapters, and local representatives — and operates with a sophistication that belies its size. Pre-convention events in June spanned cities from Chicago to the coasts, each designed to warm up relationships before the main gathering.

The outgoing co-chairs, Harshita Jain and Mahima Shah, set the tone in their farewell letter: "We proved that YJA is a movement of young people rooted in Jain values, daring to dream big in a modern world." The language is aspirational, but the operational reality backs it up. Regional retreats, monthly programming, a publishing arm (Young Minds), and a biennial convention that books out in phases — this is an organisation that treats continuity as seriously as any Fortune 500 succession plan.

## Why it matters beyond the ballroom

Jain Americans punch above their demographic weight. The community's median household income is among the highest of any religious group in the United States. Its members are disproportionately represented in medicine, finance, technology, and the diamond trade. JAINA, the parent organisation, runs large-scale conventions of its own, drawing thousands of families.

But YJA's focus on the 14-to-29 bracket addresses a question that every small diaspora faith community must eventually face: will the next generation stay? The sell-out suggests the answer, for now, is that they want to — provided someone builds a space where being Jain and being American does not require choosing.

The convention runs through July 5. By the time it ends, 915 young Jains will have spent four days inside a world where the in-between is not a problem to be solved but a condition to be inhabited. For a community navigating faith, identity, and belonging in a country that does not always know it exists, that may be enough."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Nine Hundred Young Jains Just Sold Out a Convention in New Jersey. Their Theme: 'The Art of the In-Between.'",
    "subheadline": "The 17th biennial Young Jains of America convention opens this week with 915 attendees across three age cohorts — every spot taken, every waitlist full.",
    "slug": make_slug("yja-convention-young-jains-america-new-jersey-in-between"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Young Jain Americans navigate between an ancient faith built on non-violence and non-attachment and a consumer culture that runs on the opposite. YJA's sold-out convention is the infrastructure they built for that in-between.",
    "tags": ["nri", "diaspora", "jain", "youth", "community", "identity", "new-jersey", "convention"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "YJA Convention 2026", "url": "https://convention.yja.org/"},
        {"name": "YJA Official", "url": "https://yja.org/events/2026-convention/"},
        {"name": "Young Minds (YJA Medium)", "url": "https://youngminds.yja.org/"},
        {"name": "YJA Biennial Conventions", "url": "https://yja.org/convention/biennial-conventions/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/03/Das_Lakshana_%28Paryusana%29_celebrations%2C_New_York_City_Jain_temple_2.JPG",
    "image_caption": "Jain community celebrations at a temple in New York City",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}


# ─────────────────────────────────────────────
# Insert both articles
# ─────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
