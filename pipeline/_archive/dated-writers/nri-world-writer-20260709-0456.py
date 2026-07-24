#!/usr/bin/env python3
"""NRI World writer — 2026-07-09 05:00 PT run."""

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

# ── Article 1: Operation Hard Ball / Bishnoi Gang ──────────────────────────

article1_body = """The United States Department of Justice has unsealed indictments against 37 defendants tied to three India-based organised crime groups, in what federal prosecutors are calling one of the most significant crackdowns on transnational criminal networks targeting the Indian diaspora in North America.

The operation, codenamed Hard Ball, saw at least 24 suspects arrested across the United States, Canada, and Europe in coordinated raids that spanned more than 50 locations. Law enforcement agencies seized over 2,200 pounds of cocaine and heroin, a dozen firearms, and $40,000 in cash.

## The Charges

At the centre of the indictment is Lawrence Bishnoi, a 33-year-old gang leader who has been imprisoned in India since 2015 yet allegedly continues to orchestrate violence from his jail cell using smuggled cellphones. His North American deputy, Satinderjeet Singh — known as Goldy Brar — is also named as a co-defendant.

The pair face charges of directing the June 2023 assassination of Hardeep Singh Nijjar, a Canadian citizen and Sikh separatist leader who was shot dead outside the Guru Nanak Sikh Gurdwara in Surrey, British Columbia. The killing plunged India-Canada relations into their worst crisis in decades.

First Assistant US Attorney Bill Essayli described the alleged crimes as "some of the most violent and barbaric activities we've seen." No Indian government involvement is alleged in any of the indictments.

## Diaspora in the Crosshairs

For ordinary NRIs, the most alarming detail may be the extortion allegations. Prosecutors say the Bishnoi organisation systematically targeted "prominent cultural, political, and business leaders in India and diaspora communities outside of India." The gang allegedly identified targets through government databases and social media, then contacted victims via encrypted messaging apps including WhatsApp, threatening violence while referencing previous attacks.

In one case cited in the indictment, gang members demanded a $5 million payment from a resident of Thousand Oaks, California, during December and January. Prosecutors say the group selected victims whose targeting would "maximise the likely success of future extortion schemes."

The Bishnoi gang also claimed responsibility for shooting at the Vancouver home of Indian actor and singer Gippy Grewal in November 2023, and for the 2022 killing of Sidhu Moosewala, a Punjabi singer and rapper.

## A Second Gang, a Broader Network

A parallel indictment targets the Bhagwanpuria gang, founded by Jaggu Bhagwanpuria, an imprisoned rival of Bishnoi with more than 1,000 members worldwide and over 100 in the United States. That organisation is accused of contract killings, drug trafficking, kidnapping, and weapons dealing.

A third indictment names the Dhanda Drug Trafficking Organisation, a methamphetamine and cocaine distribution network allegedly run by three Canadians at the US-Canada border. Prosecutors say the Dhanda enterprise works with both the Bishnoi and Bhagwanpuria groups.

## What It Means for the Diaspora

The indictments land at a moment when diaspora safety has become an increasingly visible concern. In recent weeks, Bay Area Hindu temples have been defaced with pro-Khalistan graffiti — a Sherawali temple in Hayward, a Swaminarayan mandir in Newark, and a theft at the Shiv Durga temple in the same region. The Hindu American Foundation has urged temples nationwide to install security cameras and alarm systems.

For the millions of Indians living in the United States and Canada, Operation Hard Ball offers a measure of reassurance that law enforcement is taking transnational threats seriously. But it also confirms what many in the community have long feared: that criminal networks rooted in South Asian underworlds are no longer confined to the subcontinent.

The investigation involved the FBI, the LAPD, the DEA, and the Royal Canadian Mounted Police. Seven fugitives remain at large in the US, two in India, and one in Europe."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Thirty-Seven Charged, Twenty-Four Arrested: The US Crackdown on Indian Crime Gangs That Extorted the Diaspora",
    "subheadline": "Operation Hard Ball has unsealed indictments against three India-based organised crime groups accused of assassinations, extortion of NRIs in California, and trafficking across two continents.",
    "slug": make_slug("operation-hard-ball-bishnoi-gang-us-indictment-diaspora-extortion"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The Bishnoi and Bhagwanpuria gangs directly targeted NRI community leaders and business figures in the US and Canada through extortion, using threats of violence delivered via WhatsApp. A Thousand Oaks, California resident was allegedly threatened with a $5 million demand.",
    "tags": ["nri", "diaspora", "bishnoi", "operation-hard-ball", "crime", "extortion", "us-india", "community-safety"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "CNN", "url": "https://www.cnn.com/2026/07/07/us/us-canada-charges-india-hardeep-singh-nijjar-intl-hnk"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/us-charges-imprisoned-indian-gang-leader-2023-murder-canadian-sikh-separatist-2026-07-08/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/07/07/us-news/murderous-bishnoi-gang-wiped-out-in-mass-raids-across-california-after-barbaric-assassination-spree/"},
        {"name": "IANS", "url": "https://ianslive.in/"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/U.S._Department_of_Justice_headquarters%2C_August_12%2C_2006.jpg/1280px-U.S._Department_of_Justice_headquarters%2C_August_12%2C_2006.jpg",
    "image_caption": "The Robert F. Kennedy Department of Justice Building in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}

# ── Article 2: AIA-NY Gala 2026 ───────────────────────────────────────────

article2_body = """When the Association of Indians in America–New York Chapter held its Annual Benefit Gala at Terrace on the Park in Flushing last month, the seven honourees on stage represented something larger than individual achievement. They were proof that the Indian American community, nearly six decades after AIA's founding in 1967, has embedded itself in the marrow of American professional life — from transplant surgery and interventional cardiology to artificial intelligence and diamond entrepreneurship.

The gala drew more than 300 guests, including New York State Comptroller Thomas P. DiNapoli, State Senator John C. Liu, Nassau County Executive Bruce Blakeman, and representatives of the Consulate General of India. The honourees, designated as the community's "Ratnas" — jewels — were chosen for leadership, professional excellence, and dedication to lifting others.

## The Jewels

Dr. Dattatreyudu Nori, the evening's most decorated honouree, has spent more than five decades advancing cancer care at institutions including Memorial Sloan Kettering and Cornell Medical Center. He has authored over 300 scientific publications and received both the Padma Shri and the Padma Bhushan — India's fourth- and third-highest civilian honours — along with the Ellis Island Medal of Honor.

Dr. Sahil Khera, Interventional Director of the Structural Heart Program at Mount Sinai, has performed more than 2,000 structural heart procedures and leads training for the next generation of cardiologists.

Dr. Aprajita Mattoo of NYU Langone drew particular attention. A transplant nephrologist and assistant professor, she has played a critical role in the historic pig-to-human kidney transplant trials at NYU — work that could eventually reshape organ transplantation for the millions of Americans living with end-stage kidney disease.

Manish Dhadda, co-founder of VIBHOR, represented the entrepreneurial tradition of the Indian diamond trade in New York, while attorney Jessica Kalra brought experience from Senator Hillary Clinton's office and the Department of State to her current practice in government and real estate law.

Dr. Jagat Rawal, a Queens physician for three decades and president of the American Association of Physicians of Indian Origin's Queens-Long Island chapter, was recognised for keeping his practice open through the pandemic and administering COVID-19 vaccinations at a time of acute community need.

The youngest honouree, Pulkita Kini, is building Tara AI to help publishers control and monetise AI-generated content. A Harvard MBA candidate with stints at Microsoft and Cloudflare, she embodies the next wave of Indian American leadership in technology.

## Why Galas Like This Matter

Community galas are easy to dismiss as self-congratulatory affairs. But AIA-NY's is worth watching for what it indexes. The organisation was founded in 1967, when Indian Americans numbered in the low tens of thousands. Today, the community is roughly five million strong, and its professional footprint — in medicine, law, technology, finance — is disproportionate to its size.

The honourees this year span three generations. Nori arrived in the US in the 1970s and built a career in an era when Indian doctors were still a novelty in American hospitals. Kini, not yet thirty, is launching an AI startup in a field that did not exist five years ago. Between them sit cardiologists, nephrologists, diamond merchants, and lawyers who together illustrate the breadth — and the intergenerational continuity — of Indian American aspiration.

AIA-NY President Beena Kothari acknowledged her team and thanked Grand Sponsor Dr. Samir Sharma, while announcing the chapter's 39th Deepavali celebration and live fireworks, scheduled for October 3 at Overlook Beach, Babylon, Long Island.

The cultural programme featured tabla and sitar artists and closed with a performance by singer Kunal Lamba. But the real performance was in the data: seven individuals, seven disciplines, one community that keeps showing up."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Seven Jewels, One Community: Inside AIA–New York's 2026 Gala Honouring the Diaspora's Finest",
    "subheadline": "From a Padma Bhushan oncologist to a Harvard MBA building an AI startup, the oldest Indian American organisation celebrated the professionals who define the community's ambition.",
    "slug": make_slug("aia-ny-annual-gala-2026-ratna-honorees-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "AIA-NY, founded in 1967 as the first national association of Asian Indians in America, honoured seven professionals across medicine, law, tech, and business — a snapshot of the Indian American community's evolution from a small immigrant group to a five-million-strong professional powerhouse.",
    "tags": ["nri", "diaspora", "indian-american", "aia-ny", "community", "gala", "new-york", "healthcare", "ai"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian EYE", "url": "https://theindianeye.com/2026/06/11/aia-ny-hosts-grand-annual-benefit-gala-2026-to-honor-individuals-for-outstanding-contributions/"},
        {"name": "Association of Indians in America", "url": "https://www.aianyc.org/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/bb/The_President%2C_Shri_Pranab_Mukherjee_presenting_the_Padma_Shri_Award_to_Dr._Dattatreyudu_Nori%2C_at_a_Civil_Investiture_Ceremony%2C_at_Rashtrapati_Bhavan%2C_in_New_Delhi_on_April_08%2C_2015.jpg",
    "image_caption": "Dr. Dattatreyudu Nori receiving the Padma Shri from President Pranab Mukherjee at Rashtrapati Bhavan in 2015",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body
}

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
