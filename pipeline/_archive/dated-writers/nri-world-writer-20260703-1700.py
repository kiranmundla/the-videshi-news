#!/usr/bin/env python3
"""NRI World writer — 2026-07-03 17:00 run
Articles:
  1. FISI UK Golden Jubilee — 50 years of diaspora advocacy in Britain
  2. Two Duke cardiologists lead the American Heart Association
"""

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


# ── Article 1: FISI UK Golden Jubilee ──────────────────────────────────

art1_body = """They called it FISI — the Friends of India Society International — and when a handful of British Indians founded it in 1976, the name was aspirational at best. India had just emerged from Indira Gandhi's Emergency. The diaspora in Britain numbered in the low hundreds of thousands, politically invisible and culturally marginal. The idea that a volunteer organisation in West Kensington could influence how Westminster thought about India struck most people as quixotic.

Fifty years on, FISI UK held its Golden Jubilee on June 28 at The Bhavan, the Indian arts centre in West Kensington that has itself become a landmark of diaspora culture in London. The guest list told the story of how far both the organisation and the community it represents have travelled: two members of the House of Lords (Lord Rami Ranger and Lord Uday Nagaraju), a sitting MP (Navendu Mishra), India's Deputy High Commissioner to the UK (Kartik Pande), and a keynote from Manoj Ladwa, founder of the India Global Forum, the premier platform for UK-India business and policy dialogue.

## From emergency activism to diaspora diplomacy

FISI UK was born from a specific conviction: that the Indian diaspora had both the right and the responsibility to speak up for India on the global stage. During the late 1970s and 1980s, when India's voice was largely absent in British political corridors, FISI's founders — Dheeraj Shah, Hasmukh Shah, Bharat Shah, Rajnikant Mistry, Jayu Shah, and Mayur Shah among them — set about building relationships with parliamentarians, countering what they saw as misrepresentation of India in the British press, and advocating for the interests of British Indians.

"For the past fifty years, FISI UK has stood as a quiet yet highly resilient voice for India within the British Parliament, the media, and the wider community," said President Madhuresh Mishra in his welcome address. The word "quiet" is deliberate. FISI has never been a mass-membership movement; it has operated more as a nexus of influence, connecting diaspora leaders with policymakers in a register that Westminster understands.

Ladwa, in his keynote, captured the shift in more strategic terms. The diaspora, he argued, is "no longer just a bridge between the two countries, but has transformed into a powerful engine of growth." With UK-India trade, advanced technology partnerships, and shared values driving the bilateral relationship into new territory, organisations like FISI sit at a pivot point.

## SMRITI: preserving the trailblazers

The most forward-looking moment of the evening came with the unveiling of SMRITI — a new initiative dedicated to documenting and preserving the lives of Indians who shaped history on British soil, from Swami Vivekananda to Dadabhai Naoroji. The project has three prongs: a Heritage Magazine, curated Heritage Tours across the UK, and — perhaps most ambitiously — a Blue Plaque campaign to mark the buildings where these figures lived, studied, and worked.

Blue Plaques are a peculiarly British institution. English Heritage's scheme, running since 1866, has placed roughly 1,000 plaques across London, but only a fraction honour South Asians. FISI's campaign would lobby for additions, directing public attention to a history that most Londoners walk past without noticing.

## What fifty years looks like

The celebration concluded with the Golden Jubilee Awards, honouring contributions across youth leadership, community service, cultural ambassadorship, and lifetime achievement. A Golden Jubilee Magazine was released. And the founding members, some now in their eighties, were formally honoured for building something that outlasted them.

The British Indian community now numbers around 1.9 million — the country's largest ethnic minority group. It includes members of Parliament, peers, CEOs, and the sitting Prime Minister's wife. FISI's founding premise — that the diaspora should have a political voice — is no longer controversial. But the organisation's next chapter, preserving the institutional memory of how that voice was built, may be its most important yet.

x-official:https://x.com/FISI_UK/status/1939728192640274520"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "They Started Fighting for India in Westminster During the Emergency. Fifty Years Later, They Want Blue Plaques.",
    "subheadline": "FISI UK, the oldest Indian advocacy organisation in Britain, celebrated its golden jubilee with a new initiative to map every Indian trailblazer who lived on British soil.",
    "slug": make_slug("fisi-uk-golden-jubilee-50-years-westminster-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "FISI UK was founded by British Indians in 1976 to give the diaspora a political voice in Westminster. Its 50-year journey mirrors the trajectory of the British Indian community itself — from political invisibility to mainstream influence. The SMRITI initiative now aims to preserve that history for future generations.",
    "tags": ["nri", "diaspora", "uk", "british-indians", "fisi", "heritage", "advocacy"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Asian Independent", "url": "https://theasianindependent.co.uk"},
        {"name": "MPPOST", "url": "https://mppost.com/fisi/"},
        {"name": "Samaj Weekly", "url": "https://samajweekly.com"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Former_Congregational_Chapel_%28now_Bhavan_Indian_Arts_Centre%29%2C_Challoner_Street%E2%80%93Castletown_Road%2C_West_Kensington%2C_London_W.14_%28July_2025%29_%282%29.jpg/1280px-Former_Congregational_Chapel_%28now_Bhavan_Indian_Arts_Centre%29%2C_Challoner_Street%E2%80%93Castletown_Road%2C_West_Kensington%2C_London_W.14_%28July_2025%29_%282%29.jpg",
    "image_caption": "The Bhavan Indian Arts Centre in West Kensington, London — venue for the FISI UK Golden Jubilee",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ── Article 2: AHA Indian American leadership ──────────────────────────

art2_body = """The American Heart Association announced its volunteer leadership for fiscal year 2026-27 on July 1, and the top two names tell a story that extends well beyond cardiology. Dr. Manesh R. Patel, an interventional cardiologist at Duke Health, is now the organisation's volunteer president — the first South Asian to hold the role in the AHA's 102-year history. Serving alongside him as volunteer president-elect is Dr. Svati H. Shah, a physician-scientist who specialises in cardiometabolic genetics, also at Duke.

Both are children of Indian immigrants. Both trained at elite American medical institutions. And both now lead the scientific and medical direction of an organisation whose guidelines shape how cardiovascular disease is treated worldwide.

## The president: from Emory to the top

Patel described the appointment as a reflection of his family's journey. His parents came to the United States from India, and his path through American medicine — Emory University School of Medicine, then residency and fellowship at Duke — is the kind of trajectory that has become almost a cliché of Indian-American achievement. Except that it hasn't, quite, when it comes to the leadership suites of legacy medical organisations.

"By 2050, nearly half the world's population may face some form of cardiovascular disease or its risk factors," Patel wrote in a statement. "That is the scale of the opportunity in front of us." As volunteer president, he functions as the AHA's lead volunteer scientific and medical officer. He brings more than 500 peer-reviewed publications, a 2023 AHA Physician of the Year award, and extensive experience chairing the organisation's Scientific Sessions Program.

His research focus — interventional cardiology, antithrombotic therapies, and the development of personalised care delivery systems — reflects a discipline that increasingly depends on precision approaches rather than one-size-fits-all treatments.

## The president-elect: precision medicine and immigrant grit

Shah's story parallels Patel's but diverges in specialisation. She is the Ursula Geller Distinguished Professor of Research in Cardiovascular Diseases at Duke, directs the Duke Center for Precision Health, and runs the Adult Cardiovascular Genetics Clinic. Her research integrates genomic, metabolomic, and proteomic data to identify novel mechanisms of cardiometabolic disease — the kind of work that sits at the intersection of genetics and clinical practice.

She credited her immigrant parents, and her mother's perseverance in particular, for inspiring her career. Shah earned her public health degree from Johns Hopkins and her medical degree from the University of Washington, completed her residency at Brigham and Women's Hospital, and came to Duke for a cardiology fellowship in 2001.

## What it means for the diaspora

Indian-Americans now constitute roughly 5.4 million people in the United States. They are overrepresented in medicine — the American Association of Physicians of Indian Origin counts more than 80,000 members — but underrepresented in the upper echelons of medical society leadership. Patel and Shah's simultaneous appointment to the AHA's top two volunteer positions is, in that context, a marker of generational arrival.

It is also a reminder that cardiovascular disease is not an abstract research interest for the Indian diaspora. South Asians face disproportionately high rates of heart disease, often developing it at younger ages and with different risk profiles than other populations. An AHA led by researchers who understand these dynamics — not just scientifically but personally — matters.

The two will serve through June 30, 2027. Their first Scientific Sessions under this leadership, the AHA's flagship annual conference, will be closely watched."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Two Duke Cardiologists Now Lead the American Heart Association. Both Are Children of Indian Immigrants.",
    "subheadline": "Dr. Manesh Patel becomes the first South Asian to serve as AHA volunteer president. His president-elect, Dr. Svati Shah, runs one of the country's leading precision cardiovascular genetics programmes. Both start July 1.",
    "slug": make_slug("duke-cardiologists-patel-shah-aha-leadership-indian-american"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Two Indian-American doctors simultaneously leading the AHA marks a generational milestone for a community that is overrepresented in medicine but underrepresented in legacy medical leadership. South Asians also face disproportionately high cardiovascular risk, making this appointment personally significant for the diaspora.",
    "tags": ["nri", "diaspora", "indian-american", "healthcare", "aha", "cardiology", "achievement"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "American Bazaar Online", "url": "https://americanbazaaronline.com"},
        {"name": "American Heart Association Press Release", "url": "https://newsroom.heart.org"},
        {"name": "Cardiovascular Business", "url": "https://cardiovascularbusiness.com"},
        {"name": "NRI ConnectMyIndia", "url": "https://nri.connectmyindia.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5207102/pexels-photo-5207102.jpeg",
    "image_caption": "A healthcare professional with a stethoscope and heart symbol — cardiology at the centre of the AHA's mission",
    "image_attribution": "Pexels",
    "body": art2_body,
}


articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
