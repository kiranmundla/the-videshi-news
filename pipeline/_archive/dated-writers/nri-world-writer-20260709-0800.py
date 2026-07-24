#!/usr/bin/env python3
"""NRI World Writer — 2026-07-09 01:00 PDT run"""

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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Five Days, Zero Tickets Required: Lincoln Center's India Week Returns With Garba, Comedy, and the Biggest Silent Disco in South Asian New York",
        "subheadline": "From a sunrise Rajasthani folk concert to an all-star comedy night featuring Aasif Mandvi, New York's most iconic performing arts campus hands its stages to the diaspora — and every event is free.",
        "slug": make_slug("lincoln-center-india-week-2026-free-events-garba-dj-rekha-comedy"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "India Week is the largest curated celebration of Indian arts and culture at a major American performing arts institution, and every event is free — a deliberate message that Indian culture belongs on the country's biggest cultural stages, not behind a paywall.",
        "tags": ["nri", "diaspora", "culture", "new-york", "lincoln-center", "india-week", "events"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Lincoln Center", "url": "https://www.lincolncenter.org/series/summer-for-the-city"},
            {"name": "The Indian EYE", "url": "https://theindianeye.com/2024/07/09/are-you-missing-india-join-the-india-week-at-lincoln-centre-nyc/"},
            {"name": "StageBuddy", "url": "https://stagebuddy.com"},
            {"name": "Lassi With Lavina", "url": "https://www.lassiwithlavina.com/new-york-diary/a-midsummer-nights-free-indian-feast-at-lincoln-center/html"},
            {"name": "Asian American Arts Alliance", "url": "https://aaartsalliance.org"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Lincoln_Center_for_the_Performing_Arts.jpg/1280px-Lincoln_Center_for_the_Performing_Arts.jpg",
        "image_caption": "Lincoln Center for the Performing Arts in New York City, the venue for India Week",
        "image_attribution": "Wikimedia Commons",
        "body": """For a city that can charge three figures for a Broadway seat without blinking, free is a powerful word. Lincoln Center is deploying it five nights running.

India Week, part of Lincoln Center's annual Summer for the City festival, returns from July 10 to 14 with a programme designed to pull Indian arts out of the niche-festival circuit and plant them on the same stages that host the New York Philharmonic and the Metropolitan Opera. Every event is free and open to the public — general admission, first come, first served, with a Fast Track reservation option for those who plan ahead.

## A Week of Firsts and Returns

The programming reads less like a cultural sampler and more like a diaspora homecoming engineered by people who actually know the community.

**Ragamala Dance Company** opens the week with *Avimukta: Where the Seeker Meets the Sacred*, a Bharatanatyam-rooted work performed by the Ramaswamy family — mother Ranee and daughters Aparna and Ashwini — that the *New York Times* has called "rapturous and profound." It is a meditation on ancestry and dissolution, performed outdoors under Manhattan's summer sky.

Then comes **Garba360**, produced by MELA Arts Connect and featuring Ujjval Vyas Musicals with dance instruction by Heena Patel. For the uninitiated, garba is the intoxicating Gujarati folk dance style danced in circles — hand claps, twirls, and a two-step that anyone can pick up in minutes. For the diaspora, it is a piece of Navratri transplanted to a July evening on the Upper West Side.

The **Aakash Odedra Company** presents the U.S. premiere of *Samsara*, an epic dance work inspired by the Chinese novel *Journey to the West*, filtered through Buddhist philosophy and performed with the physical intelligence that has made Odedra one of Britain's most exciting choreographers.

## The Night Everyone Will Talk About

Saturday's comedy lineup alone would sell out a mid-size venue. **Aasif Mandvi** — Peabody Award winner, *Daily Show* correspondent, and current star of Paramount's *Evil* — headlines alongside **Hari Kondabolu**, a regular on NPR's *Wait, Wait... Don't Tell Me* and creator of the documentary *The Problem with Apu*; **Nimesh Patel**, who has toured with Chris Rock and written for some of television's biggest shows; **Aparna Nancherla**, named one of *Rolling Stone*'s "50 Funniest People Right Now"; and **Kiran Deol**, the Emmy-nominated comedian who hosts the evening. Five Indian-American comedians on one of America's most prestigious outdoor stages, on a Saturday night, for free.

## Five Nights of Silent Disco

**DJ Rekha** — born Rekha Malhotra, founder of "Basement Bhangra," one of New York's longest-running club nights, and dubbed the "Ambassador of Bhangra" by the *New York Times* — curates five consecutive nights of silent discos on Lincoln Center's outdoor dance floor beneath a ten-foot disco ball. The rotating DJ roster includes **Ashu Rai**, co-founder of "Desilicious," New York's pioneering South Asian LGBTQIA+ dance party; **Offering Rain**, a Gujarati-Ecuadorian multi-hyphenate who turns diaspora fusion into a dance floor religion; and **Rajuju Brown**, an NBC-recognised emerging artist whose sets have taken him around the world.

## Beyond the Dance Floor

The week's programming stretches in every direction. **SAZ**, the award-winning Rajasthani folk trio presented in collaboration with the Jodhpur RIFF Festival, performs a sunrise concert — a nod to the auspiciousness of early morning in Indian culture. Grammy-nominated singer **Priya Darshini** brings her all-star band to Jazz Underground. **PEN America** hosts a literary conversation with author and television host **Padma Lakshmi**, food writer **Priya Krishna**, and journalist **Yashica Dutt**, moderated by Salil Tripathi.

The legendary Padma Bhushan-awarded percussionist **Vidwan T.H. Vinayakram** — affectionately known as "Vikku ji" — performs *Parampara* with his sons and grandchildren, placing the ancient ghatam (clay pot percussion) at the centre of a meditative Carnatic music set that spans three generations.

And for the Tollywood faithful: S.S. Rajamouli's *RRR*, complete with the Oscar-winning "Naatu Naatu" sequence, screens outdoors under the stars.

## Why It Matters

India Week is not new — Lincoln Center has hosted it for several years as part of its summer programming. But its significance grows each year alongside the diaspora itself. According to the latest census data, the Indian-American population now exceeds 4.8 million, making it one of the fastest-growing ethnic communities in the country.

What Lincoln Center has quietly built is something few institutions have attempted at this scale: a week that treats Indian culture not as a curiosity or a diversity checkbox, but as a main-stage attraction worthy of the same campus that hosts Yo-Yo Ma and the New York City Ballet. That every event is free — no tickets, no waitlists, just show up — is the most radical statement of all.

The week also arrives just months before the Nita Mukesh Ambani Cultural Centre's planned India Weekend at Lincoln Center in September, which will bring the U.S. premiere of *The Great Indian Musical: Civilization to Nation* along with fashion shows and a cricket panel. India's footprint at Lincoln Center is no longer measured in days but in seasons.

For NRIs in the tri-state area — or anyone within driving distance — the message is straightforward: clear your evenings from July 10 to 14. Wear something you can dance in."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nita Ambani Proposes an India-America Health Alliance at AAPI's Sold-Out Tampa Convention. The Diaspora's Physicians Are Listening.",
        "subheadline": "The Reliance Foundation chairperson received the AAPI Humanitarian Award and the Key to the City of Tampa, then outlined a three-pillar partnership — access, capacity, discovery — that would yoke America's largest bloc of Indian-origin doctors to India's public health infrastructure.",
        "slug": make_slug("nita-ambani-aapi-humanitarian-award-india-america-health-alliance-tampa"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian-origin physicians are the single largest ethnic bloc in American medicine, and AAPI is their institutional voice. The proposed India-America Health Alliance would channel diaspora medical expertise back into India's healthcare system — turning professional success abroad into public health impact at home.",
        "tags": ["nri", "diaspora", "healthcare", "aapi", "nita-ambani", "reliance-foundation", "tampa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/2026/07/04/aapi-and-reliance-foundation-a-new-dawn-for-indo-american-health-collaboration/"},
            {"name": "The Indian EYE - AAPI Convention", "url": "https://theindianeye.com/2026/04/06/aapi-announces-44th-annual-convention-in-tampa-fl/"},
            {"name": "AAPI Official", "url": "https://www.aapiusa.org"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/83/The_Prime_Minister%2C_Shri_Narendra_Modi_rededicating_Sir_H.N._Reliance_Foundation_Hospital_and_Research_Centre_to_the_Nation%2C_in_Mumbai_on_October_25%2C_2014._The_Governor_of_Maharashtra%2C_Shri_C._Vidyasagar_Rao_is_also_seen_%28cropped%29.jpg",
        "image_caption": "Nita Ambani, Founder and Chairperson of Reliance Foundation",
        "image_attribution": "Wikimedia Commons",
        "body": """When the American Association of Physicians of Indian Origin holds its annual convention, it is not a small affair. But even by AAPI's standards, the 44th edition in Tampa from July 2 to 5 was a landmark. For the first time in its history, the convention sold out — every seat, every session, every networking dinner.

Then Nita Ambani took the stage and made the crowd think about what comes next.

## The Award and the Key

The Reliance Foundation Founder and Chairperson received two honours in quick succession. First, the AAPI Humanitarian Award, the organisation's highest recognition for contributions to healthcare, education, and community development. Then Tampa Mayor Jane Castor presented Ambani with the Key to the City — one of the highest civic honours an American city can bestow.

"I accept this award with humility and deep gratitude," Ambani said in her acceptance speech. "Humanitarian work is never achieved by one person alone. Behind that person is a dedicated and sincere team — hands that heal, hands that teach, hands that comfort, hands that arrive before dawn and leave long after the world has gone to sleep."

The moment was ceremonial. What followed was not.

## Three Pillars, One Alliance

Ambani used her address to propose what she called an India-America Health Alliance — a formal partnership between AAPI and Reliance Foundation built on three commitments: access, capacity, and discovery.

"I would like to propose a new partnership between AAPI and Reliance Foundation to strengthen healthcare in India and serve humanity beyond borders," she told the audience of thousands. "Three ways to turn diaspora pride into global impact and prove that medicine at its best has no borders."

The proposal is ambitious in scope. Indian-origin physicians are the largest non-white ethnic group in American medicine — AAPI alone claims over 120,000 members and represents a community whose members hold leadership positions at major hospital systems, medical schools, and pharmaceutical companies across the country. Channelling even a fraction of that collective expertise and capital toward India's healthcare gaps would represent one of the most significant diaspora-to-homeland knowledge transfers in decades.

The access pillar would focus on extending healthcare to underserved populations. The capacity pillar would target medical training and institutional development. The discovery pillar would promote collaborative research across borders.

## What AAPI Brought to Tampa

The convention itself underscored the scale and ambition of the Indian-American medical community. Held at the JW Marriott Tampa Water Street under the theme "Stronger Together: United in Care, Undivided in Voice," the event drew physicians, health professionals, and researchers from across the United States for four days of scientific sessions, CME programming, and policy discussions.

AAPI President Dr. Amit Chakrabarty described the sellout as "a milestone made possible by the steadfast support and engagement of our members." Dr. Meher Medavaram, the President-Elect who will assume the presidency at the next convention, called the gathering "one of its kind" for its scholarly exchange and health policy agenda-setting.

The convention also coincided with America's 250th Independence Day celebrations. Ambani wove this into her remarks, extending "heartfelt felicitations to all our sisters and brothers in America" on the occasion — a deft acknowledgement that the room was full of people who hold two countries in their hearts simultaneously.

## The Diaspora Doctor Effect

The proposed alliance taps into a phenomenon that has been building for decades. Indian-origin physicians began arriving in the United States in large numbers after the Immigration and Nationality Act of 1965 opened the doors to skilled professionals from Asia. Six decades later, their children and grandchildren fill the ranks of America's most competitive residency programmes and research laboratories.

But the relationship with India has never been straightforward. Many physicians maintain deep ties — returning for family visits, supporting medical missions, funding hospitals in their hometowns. Others have drifted away from clinical engagement with India, focusing their philanthropic efforts locally. A formal alliance with institutional backing from both AAPI and Reliance Foundation would give the diaspora's medical community a structured pathway to re-engage.

Reliance Foundation's own healthcare footprint in India is substantial. The Sir H.N. Reliance Foundation Hospital in Mumbai is one of the country's premier multi-specialty institutions, and the foundation's community health programmes operate across multiple states.

## What Happens Now

The proposal remains at the announcement stage. The details — governance structure, funding commitments, pilot programmes, the mechanics of cross-border collaboration — are yet to be worked out. Both organisations have signalled willingness, but translating a convention-stage proposal into an operational alliance will require months of negotiation and planning.

What is not in doubt is the appetite. The sold-out convention, the dual honours for Ambani, and the standing ovation that reportedly followed her speech all point to a diaspora medical community that is ready for something bigger than annual meetings and CME credits. Whether the India-America Health Alliance becomes that something will depend on what happens after Tampa."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
