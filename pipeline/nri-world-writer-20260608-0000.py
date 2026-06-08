#!/usr/bin/env python3
"""NRI World Writer — 3 articles for The Videshi, June 8, 2026."""

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
# ARTICLE 1: "We Belong" Impact Summit
# ────────────────────────────────────────────

article1_body = """Three hundred South Asian American leaders walked into the Mayflower Hotel in Washington, D.C. on April 20, carrying a message that needed no explanation: *We Belong.* The annual summit and gala, hosted by Indian American Impact, arrived at a moment when even framing that sentence felt like an act of defiance.

The organisation was marking its tenth anniversary. A decade ago, the idea that South Asian Americans could field a national political infrastructure — one that trains candidates, mobilises voters, and holds meetings with 70 congressional offices in a single day — would have seemed aspirational at best. In 2026, the infrastructure exists. The question is whether it can outpace the headwinds.

## The headwinds are not subtle

Anti-immigrant rhetoric targeting Indian Americans has shifted from the margins to the mainstream. The day after the summit wrapped up, the President amplified racially charged messaging aimed at the community on social media — a stark reminder that belonging, for South Asian Americans, is not a settled matter but a daily negotiation.

It was against this backdrop that former U.S. Surgeon General Dr. Vivek Murthy opened the summit with a conversation on loneliness, community care, and what it means to show up for one another when the political climate tells you to disappear. Murthy, who served as the 19th and 21st Surgeon General, has spent years warning that isolation is a public health crisis. At the Mayflower, he made the case that for immigrant communities, that crisis has a political dimension too.

"When people are isolated, they're easier to target," Murthy told the audience, according to attendees. "Community is not just a nice thing — it's a survival strategy."

## Seventy meetings in a day

The summit's most concrete output was South Asian Hill Day, a coordinated lobbying effort that brought 21 partner organisations to Capitol Hill. Advocates met with more than 70 House and Senate offices, pressing priorities on immigrant rights, voting access, and anti-hate legislation. The coalition included the Sikh Coalition, Stop AAPI Hate, South Asian Americans for Change, and several regional advocacy groups.

U.S. Representative Pramila Jayapal spoke on immigrant rights. Representative Ro Khanna addressed artificial intelligence and its implications for diaspora workers. Representative Raja Krishnamoorthi and Representative Suhas Subramanyam joined sessions on leadership development. Virginia Lieutenant Governor Ghazala Hashmi, the first South Asian woman to win a state senate seat in Virginia, spoke about the gap between legal status and genuine belonging.

The evening gala honoured Pennsylvania State Senator Nikil Saval and former senior Biden advisor Neera Tanden. Former Associate Attorney General Vanita Gupta delivered the closing address, arguing that the current political moment demands not just resilience but organised power.

## A community that punches above its weight — and knows it

South Asian Americans are one of the fastest-growing electorates in the United States, yet their political representation still trails their economic and professional influence. Indian Americans alone head 16 Fortune 500 companies and contribute an estimated 5–6 per cent of all U.S. income taxes, according to a 2024 Indiaspora-BCG report, despite comprising just 1.5 per cent of the population.

Chintan Patel, Executive Director of Indian American Impact, put it bluntly: "At a moment when our communities are being targeted and our loyalty questioned, we came to Washington not to ask for belonging, but to assert it. We met with Congress, organised across generations, and made clear that South Asian Americans are not on the sidelines of this democracy; we are helping shape its future."

For the 300 attendees who filed out of the Mayflower, the message was clear enough. Belonging is not granted. It is built — one Hill Day meeting, one voter registration drive, one election cycle at a time. The machinery now exists. The real test is what the next decade brings."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Three Hundred South Asian Leaders Walked Into the Mayflower Hotel. The Next Day, the President Targeted Them on Social Media.",
    "subheadline": "Indian American Impact's 10th anniversary summit in Washington brought Vivek Murthy, four members of Congress, and 21 advocacy groups to Capitol Hill — just as anti-immigrant rhetoric hit a new pitch.",
    "slug": make_slug("impact-summit-we-belong-south-asian-leaders-dc"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "South Asian Americans organising politically and asserting civic belonging in the face of rising anti-immigrant rhetoric — the core tension of diaspora identity in 2026 America.",
    "tags": ["nri", "diaspora", "south-asian", "politics", "advocacy", "vivek-murthy"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/01/at-a-time-of-rising-hate-south-asian-americans-gather-in-d-c-to-affirm-one-message-we-belong/"},
        {"name": "Indian American Impact", "url": "https://www.iaimpact.org"},
        {"name": "Indiaspora-BCG Impact Report", "url": "https://www.indiaspora.org"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Vivek_Murthy%2C_Surgeon_General_%28profile%29.jpg",
    "image_caption": "Former U.S. Surgeon General Dr. Vivek Murthy, who opened the Impact Summit with a keynote on community care",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": article1_body.strip()
}

# ────────────────────────────────────────────
# ARTICLE 2: Indiaspora "Partners in Progress"
# ────────────────────────────────────────────

article2_body = """For decades, the relationship between India and its diaspora could be summarised in a single word: remittances. Every year, billions of dollars flowed from bank accounts in Houston, London, Dubai, and Sydney back to family homes in Kerala, Gujarat, and Punjab. The money mattered enormously. But it also flattened a far more complex relationship into a wire transfer.

A major report released in March by Indiaspora argues that this framing is obsolete. *India and its Diaspora: Partners in Progress*, unveiled at the 2026 Indiaspora Forum in Bengaluru, contends that the world's largest diaspora — 35 million people of Indian heritage spread across more than 200 countries, earning an estimated $730 billion annually — has evolved into something that a Western Union receipt cannot capture.

## Beyond the wire transfer

The four-day forum, held at the JW Marriott Prestige Golfshire on the outskirts of Bengaluru against the scenic backdrop of the Nandi Hills, drew leaders from 23 countries. Technologists, investors, philanthropists, artists, policymakers, and scholars spent four days mapping a new blueprint for diaspora-India engagement — one centred on investment, technology partnerships, and institutional credibility rather than personal remittances.

The shift is measurable. India-U.S. bilateral trade hit a record $241 billion last year, making America India's largest trading partner for the fourth consecutive year. Indian Americans co-founded 72 of 648 American unicorns as of 2024, collectively valued at $195 billion. Sixteen Indian-origin CEOs run Fortune 500 companies, employing 2.7 million Americans and generating nearly $1 trillion in revenue.

"In 1991, India opened its doors to the world. Today, the world is knocking on India's door," said MR Rangaswami, founder and chairman of Indiaspora. "At this inflection point, India has the opportunity to unlock the power of a 35-million-strong diaspora, bringing capital, capability, and credibility as true partners in India's journey to 2047."

## The credibility gap

But the report is not merely celebratory. Drawing on insights from more than 200 leaders across 24 countries, it documents structural barriers that still throttle deeper engagement. NRI investors who want to buy Indian equities face a compliance maze that rivals a visa application. Philanthropists describe red tape that makes donating to an Indian cause harder than wiring money to a family member. Dual-taxation headaches — FBAR filings, FATCA disclosures, the ambiguities of the India-US tax treaty — discourage the very capital flows India claims to want.

The report builds on Indiaspora's earlier work with Boston Consulting Group. The first study, *Small Community, Big Contributions* (2024), quantified the Indian American economic footprint: 1.5 per cent of the U.S. population paying 5–6 per cent of all income taxes, holding 10 per cent of U.S. patents, and claiming 13 per cent of scientific publications. A second report (2025) documented the Indian community in the UAE. *Partners in Progress* widens the lens to all 200-plus countries where the diaspora lives and works.

## What the diaspora wants

The survey respondents in the report are strikingly optimistic. Many envision an India that by 2047 — the centenary of independence — stands among the world's leading economies, drives global innovation, reduces inequality, and delivers a high quality of life for its citizens. The diaspora does not merely want to observe this transformation; it wants to participate in it.

"India @100 is an inspiring vision not just for the people of India, but for the 35 million members of the Indian diaspora that live elsewhere," said Sanjeev Joshipura, Indiaspora's Executive Director. "In the countries we call home, we create positive outcomes for society, serve as cultural ambassadors, and build a bridge between our country of residence and India."

The report's practical recommendations — streamlined NRI investment onboarding, mutual recognition of professional credentials, a digital engagement platform beyond the existing Pravasi Bharatiya portal — read less like aspirations and more like an engineering specification.

Whether New Delhi treats it as such is another matter. The Indian diaspora has heard promises before. What *Partners in Progress* makes clear is that this time, the diaspora is not waiting for an invitation. It is drafting the agenda."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The World's Largest Diaspora No Longer Wants to Be Defined by Wire Transfers. It Has a Blueprint Instead.",
    "subheadline": "Indiaspora's 'Partners in Progress' report, drawn from 200 leaders across 24 countries, maps how 35 million overseas Indians are shifting from remittance senders to strategic partners in India's rise.",
    "slug": make_slug("indiaspora-partners-progress-diaspora-blueprint"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The diaspora's evolving relationship with India — from one-way remittance flows to two-way investment, technology, and institutional partnerships — and the structural barriers that remain.",
    "tags": ["nri", "diaspora", "indiaspora", "remittance", "investment", "india-at-100"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Indiaspora Press Release", "url": "https://www.globenewswire.com/news-release/2026/03/23/indiaspora-releases-partners-in-progress"},
        {"name": "Indiaspora YouTube (2026 Forum)", "url": "https://www.youtube.com/@Indiaspora"},
        {"name": "Indiaspora-BCG Small Community Big Contributions (2024)", "url": "https://www.indiaspora.org"}
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7580644/pexels-photo-7580644.jpeg",
    "image_caption": "Business professionals networking at a diaspora leadership conference",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": article2_body.strip()
}

# ────────────────────────────────────────────
# ARTICLE 3: IAMA SEVA Clinic Chicago
# ────────────────────────────────────────────

article3_body = """In a strip of suburban Illinois twenty miles west of the Loop, a free clinic run by Indian American doctors has quietly become one of the most ambitious community health experiments in the Midwest. The Seva Community Health Clinic, operated by the Indian American Charitable Foundation (IAMA-CF), now opens six days a week, offers women's health services, runs community seminars, and has added telehealth visits that reach patients who cannot make the drive to Willowbrook.

None of this was true a year ago. In 2024, the clinic operated on a limited schedule with a handful of volunteer physicians. The transformation, celebrated at a gala attended by 375 physicians and supporters at Ashton Place on April 18, reflects a community that has decided free healthcare for underserved populations is not a side project but a mission.

## A model that scales on goodwill

The clinic's model is deceptively simple: Indian American physicians volunteer their time, the IAMA Charitable Foundation provides the infrastructure, and patients — regardless of immigration status, insurance, or ability to pay — walk in and receive care. What makes the 2025–2026 expansion notable is the scope. Six days a week is not a pop-up clinic; it is a functioning healthcare outpost. The addition of a dedicated women's health clinic addresses a gap that community health providers across the country struggle to fill.

Dr. Samir Shah, president of the foundation, told attendees at the gala that the clinic had "fundamentally changed what we offer and who we can reach." Telehealth capabilities now allow patients to consult physicians remotely — a critical upgrade for elderly patients and those without reliable transportation in the sprawling western suburbs of Chicago.

"We're not just treating illness," Shah said. "We're building a healthcare home for people who don't have one."

## The physician pipeline

Indian American doctors are not a small presence in U.S. healthcare. An estimated 50,000 India-born physicians practise in the country, many of them highly specialised. They constitute roughly one in seven doctors in some states. Yet the IAMA clinic represents something distinct from individual professional success: it is an institutional commitment, sustained by collective effort over three decades.

The gala's chief guest, Dr. Bobby Mukkamala — the first physician of Indian heritage to serve as president of the American Medical Association — brought both national visibility and personal credibility to the evening. Mukkamala, a Flint, Michigan otolaryngologist who survived brain surgery before ascending to the AMA's top post, has made healthcare access a centrepiece of his tenure.

The keynote address came from Dr. Subrahmanyam Dravida, president of EKAL-USA, a foundation that operates single-teacher schools in rural India. Dravida drew a thread between the clinic's work in Chicago's western suburbs and Ekal Vidyalaya's efforts in India's tribal belt, arguing that community-driven healthcare and education are "two instruments playing the same chord."

## Awards and legacy

The evening's awards underlined the depth of the community's commitment. Dr. Thomas John received the Lifetime Achievement Award. Dr. Ngozi Ezike — notably, not of Indian origin — received the Distinguished Physician Award, a recognition that the clinic's mission extends beyond ethnic boundaries. A posthumous honour for the late Dr. Usharani Nimmagadda acknowledged a family whose legacy of service stretches across generations.

Dr. Meher Medavaram, president of IAMA-IL, situated the evening in a broader context: Indian American medical associations exist in nearly every major metropolitan area. Many run charitable programmes. Few have achieved the scale and consistency of the Seva clinic. The Illinois model, Medavaram suggested, is exportable — if other chapters can match the volunteer commitment.

## The diaspora angle that needs no explanation

For an immigrant community that arrived in America largely through the medical profession, running a free clinic is not charity in the conventional sense. It is an expression of the compact that brought many here: the belief that medical training is not merely a career path but a debt to be repaid. In Willowbrook, 375 physicians dressed for a gala understood that instinctively. The telehealth link, the women's health clinic, the six-day schedule — these are not abstract policy goals. They are what happens when a community decides its professional capital belongs to everyone."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian American Doctors Built a Free Clinic in Suburban Chicago. Now It Opens Six Days a Week.",
    "subheadline": "The IAMA Charitable Foundation's Seva clinic has added women's health, telehealth, and a near-daily schedule — a quiet expansion that makes it one of the most ambitious diaspora-run health projects in the country.",
    "slug": make_slug("iama-seva-free-clinic-chicago-expansion"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian American physicians channelling professional success into free healthcare for underserved populations — a direct expression of the immigrant compact that brought many to the U.S. through medicine.",
    "tags": ["nri", "diaspora", "healthcare", "chicago", "iama", "community-service"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/07/service-to-underserved-seva-indian-american-physicians-celebrate-legacy-leadership-and-harmony-in-healing/"},
        {"name": "India Abroad (YouTube)", "url": "https://www.youtube.com/@IndiaAbroad"},
        {"name": "IAMA Charitable Foundation", "url": "https://iamacf.org"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5722158/pexels-photo-5722158.jpeg",
    "image_caption": "Healthcare professionals providing community medical services",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": article3_body.strip()
}

# ────────────────────────────────────────────
# PUBLISH
# ────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
