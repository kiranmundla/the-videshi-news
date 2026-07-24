#!/usr/bin/env python3
"""NRI World Writer — 2026-07-04 17:00 PDT run"""

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


# ────────────────────────────────────────────
# ARTICLE 1: Health Camp NJ / Balaji Temple
# ────────────────────────────────────────────

art1_body = """A Hindu temple in central New Jersey is about to double as a walk-in clinic — for the twenty-seventh year running.

On July 19, Health Camp of New Jersey will set up shop inside the Sri Venkateswara (Balaji) Temple in Bridgewater and offer free blood work, EKGs, cancer screenings, dental exams, vision checks and mental-health consultations to anyone who registers. No insurance card required. No co-pay. No questions about immigration status.

Since a handful of Indian American physicians founded the nonprofit in 1999, it has screened more than 15,000 people and flagged over 4,500 cases of undetected chronic disease — diabetes, hypertension, early-stage cancers — that might otherwise have gone undiagnosed until a hospital visit made the bill catastrophic.

## The quiet epidemic

South Asians in the United States face disproportionately high rates of Type 2 diabetes and cardiovascular disease. A landmark study in the *Journal of the American Heart Association* found that South Asians develop coronary artery disease roughly a decade earlier than other ethnic groups, often without the classic risk factors that would trigger a screening referral. Language barriers, unfamiliarity with the American insurance system, and cultural reluctance to discuss symptoms — particularly among first-generation immigrants — mean that many in the community don't see a doctor until something breaks.

Health Camp was built to fill that gap. Its model is deceptively simple: recruit volunteer physicians, dentists, nurses and pharmacists from the community's own medical talent pool; partner with a temple that already functions as a social anchor; and run everything on a single Sunday morning before the crowd disperses after puja.

"Together, we can continue building healthier communities through compassion, prevention, early detection, and timely access to quality healthcare," said Dr. Tushar Patel, the organisation's president.

## From screenings to an FQHC

This year, Health Camp is expanding beyond the annual fair. The organisation has announced plans to establish a Community Health Center Look-Alike — a step toward becoming a Federally Qualified Health Center (FQHC) — that would offer year-round primary medical, dental and mental-health services beginning in September 2026. If approved, it would be one of the few such centres in New Jersey with deep roots in the South Asian community.

The move reflects a broader pattern among Indian American civic organisations: institutions that began as weekend cultural gatherings are professionalising into permanent service providers. Temples host coding classes and SAT prep. Gurudwaras run food banks. And now a nonprofit born in a temple lobby is positioning itself to accept Medicaid patients.

## The partnership model

The July 19 fair is underwritten by a coalition that reads like a cross-section of New Jersey's medical establishment: RWJ Barnabas Health–Somerset, LabCorp, the New Jersey Department of Health, Rutgers Medical School, and SAMHIN, a mental-health organisation focused on South Asian communities. The Ritesh Shah Charitable Pharmacy will provide free medication consultations. Volunteer physicians from the American Association of Physicians of Indian Origin's state chapter will staff the clinical stations.

Hemoglobin A1c testing — the gold standard for diabetes screening — will be available alongside cardiology evaluations, women's health services, physical therapy and dietary counselling. Advance registration closes on July 15.

## Why it matters

The Indian American community is sometimes described, with a mix of pride and discomfort, as a "model minority" — high median incomes, advanced degrees, stable family structures. The label obscures the tens of thousands who work in gas stations, run small motels, drive ride-share cars and lack employer-sponsored coverage. It also obscures the cultural gap: a 62-year-old grandmother in Edison who has never had a mammogram is not a statistical anomaly. She is the reason Health Camp exists.

Twenty-seven years in, the numbers suggest the model works. Whether it can scale into something that outlasts any single generation of volunteer doctors is the next test."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "A New Jersey Temple Has Screened 15,000 People for Free. Now It Wants to Become a Permanent Clinic.",
    "subheadline": "Health Camp of New Jersey, a volunteer-run nonprofit housed in the Balaji Temple in Bridgewater, is preparing to transform from an annual health fair into a year-round Federally Qualified Health Center.",
    "slug": make_slug("nj-balaji-temple-health-camp-fqhc-indian-american"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian American temples are evolving from spiritual centres into critical community health infrastructure, filling gaps left by the US insurance system for underserved South Asian populations.",
    "tags": ["nri", "diaspora", "health", "community", "temple", "new jersey", "south asian health"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/29/health-camp-of-new-jersey-to-host-annual-free-health-fair-in-bridgewater/"},
        {"name": "Health Camp of New Jersey", "url": "https://www.healthcampofnj.org/"},
        {"name": "Journal of the American Heart Association", "url": "https://www.ahajournals.org/doi/10.1161/JAHA.120.017399"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/30367056/pexels-photo-30367056.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750",
    "image_caption": "A healthcare worker performs a blood glucose screening at a community health fair",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}


# ────────────────────────────────────────────
# ARTICLE 2: Indian Diaspora Center TV symposium
# ────────────────────────────────────────────

art2_body = """On a warm Sunday afternoon in late June, a roomful of Indian Americans in Elmont, New York, sat rapt as a woman described reading the evening news on Indian television — entirely from memory, because teleprompters hadn't been invented yet.

The woman was Sheila Chaman, one of Doordarshan's most recognisable news presenters from the era when a single state-run channel was the only screen in the house. She was speaking at the Indian Diaspora Center's 2026 annual symposium, held at the Kerala Center on June 28, under the title "Indian Television — Yesterday, Today and Tomorrow." The event was organised in collaboration with the Global Organization of People of Indian Origin's Manhattan chapter (GOPIO-Manhattan) and the Indian American Kerala Cultural and Civic Center.

## From one channel to nine hundred

Chaman, who has co-authored a new book called *Doordarshan Diaries: The Golden Era of Television*, walked the audience through a transformation that many in the room had lived but few had documented. Indian television began on September 15, 1959, with a makeshift studio and a small transmitter. For decades, Doordarshan was the only game in town: a few hours of programming a day, focused on education, agriculture and national development. Colour arrived on August 15, 1982, in time for the Asian Games, and the medium's reach exploded.

The real rupture came in the early 1990s. CNN's coverage of the Gulf War, beamed into Indian living rooms via satellite, shattered Doordarshan's monopoly overnight. Private channels — Star TV, Zee TV, Sony — poured in. Today, India has more than 900 satellite television channels, and Doordarshan itself operates around 50 of them. Citing a study by the Indian Institute of Management Ahmedabad, Chaman noted that India's television audience is projected to reach 1.03 billion viewers by 2029.

## The Narasimha Rao connection

The symposium fell on the birth anniversary of former Prime Minister P.V. Narasimha Rao, and panellist Ramu Damodaran — a former Doordarshan news presenter who had served in Rao's office before joining the United Nations — used the coincidence to draw a direct line between economic liberalisation and media freedom.

"P.V. Narasimha Rao is rightly remembered for launching India's economic liberalisation," Damodaran said. "Equally significant, however, was his commitment to liberalising the human mind. One visible expression of that vision was opening Indian television to new channels and new opportunities, giving viewers a genuine choice in what they could watch."

It was an apt observation for a diaspora audience. Many in the room had left India during the licence-raj years and watched the country's media landscape transform from afar. The panel's implicit argument was that economic reform and media pluralism were two sides of the same coin — and that the Indian diaspora, which had been agitating for both from Silicon Valley to Wall Street, had a stake in preserving that history.

## An accidental television journalist

Former Indian Ambassador T.P. Sreenivasan, who now hosts "Around and Inside" on the Kerala-based Asianet TV, offered a wry counterpoint. "It is ironic," he said, "that the oldest member of this panel is speaking about the newest trends in television." After retiring from the Indian Foreign Service, Sreenivasan became what he called an "accidental television journalist," drawn in by the rapid expansion of regional news channels.

He pointed to the rise of small regional broadcasters — what he dryly described as "tea shop stations" — as one of the most significant developments in Indian media. Several have grown into influential organisations, proving that quality journalism can flourish outside the big networks.

Moderator Sree Sreenivasan, the digital media expert who co-founded the South Asian Journalists Association and hosts the *Sunday NYT Readalong*, steered the discussion toward the harder questions. During open remarks, panellists lamented the slide of Indian television news into sensationalism — the shouting matches, the exaggerated chyrons, the retreat from accountability.

"It is clear that audiences should demand better coverage, as democracy in India and abroad depends on it," Damodaran said.

## Building a library of diaspora memory

The symposium is part of a larger project. The Indian Diaspora Center, housed in the Dr. Thomas Abraham Library at the Kerala Center, collects books, publications and archival material on the global Indian community. GOPIO has been placing "India Collections" in public libraries across the New York metropolitan area — book donations from the Consulate General of India and community members — to make the diaspora's history accessible beyond temple lobbies and community-centre basements.

As a parting gesture, speakers were handed rare First Day Covers from the U.S. Postal Service, originally released during the first Global Convention of People of Indian Origin in New York in 1989, featuring Mahatma Gandhi stamps. It was the kind of small, deliberate act of preservation that the Centre was built to champion: making sure that one generation's history doesn't evaporate before the next one thinks to ask about it."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "They Read the News from Memory, Without Teleprompters. Now a New York Library Is Making Sure the Diaspora Remembers.",
    "subheadline": "The Indian Diaspora Center's annual symposium brought Doordarshan veterans and digital-age journalists under one roof in Elmont, New York, to document a media revolution that shaped how millions of Indians — at home and abroad — understood their country.",
    "slug": make_slug("indian-diaspora-center-doordarshan-tv-symposium-elmont"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "A New York–based diaspora centre is building a permanent archive of Indian community history, using events like this symposium to document the cultural touchstones — Doordarshan chief among them — that connected generations of NRIs to home.",
    "tags": ["nri", "diaspora", "doordarshan", "indian television", "cultural preservation", "GOPIO", "new york"],
    "urgency": "low",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/07/02/indian-diaspora-center-hosts-2026-annual-symposium-on-the-topic-indian-tv-yesterday-today-and-tomorrow/"},
        {"name": "GOPIO International", "url": "https://www.gopio.net/"},
        {"name": "IIM Ahmedabad Television Industry Study", "url": "https://www.iima.ac.in/"}
    ]),
    "score_total": 68,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8348468/pexels-photo-8348468.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750",
    "image_caption": "A panel discussion at a community cultural event",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}


articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
