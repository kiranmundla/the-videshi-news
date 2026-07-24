#!/usr/bin/env python3
"""NRI World Writer — 2026-07-08 17:00 PDT"""
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
# ARTICLE 1: Tushar Kumar — UK's Youngest Indian-Origin Mayor
# ────────────────────────────────────────────

art1_headline = "At Twenty-Three, a Haryana-Born Councillor Becomes the Youngest Indian-Origin Mayor in Britain"

art1_subheadline = "Tushar Kumar, a King's College London graduate who was first elected at twenty, has been appointed mayor of Elstree and Borehamwood — the latest in a growing wave of young Indian-origin politicians winning civic office across Britain and America."

art1_body = """When the Elstree and Borehamwood Town Council convened on May 13 for its annual mayor-making ceremony, the chain of office was placed around the neck of a twenty-three-year-old Labour councillor from Haryana. Tushar Kumar became the youngest Indian-origin person to hold the title of mayor anywhere in the United Kingdom — and quite possibly the youngest mayor of any background in the country's recent civic history.

The appointment would have been improbable even a decade ago. Kumar arrived in Britain as a child, grew up in Borehamwood — the Hertfordshire town better known for its film studios than its politics — and stood for his first council election at twenty, winning a seat in 2023. He studied political science at King's College London, where he also served as a student representative. Before entering the council chamber, he worked as a policy advisor for the Department for Work and Pensions.

His mother, Parveen Rani, is the person he credits most directly. "She taught me that public service is not about titles," Kumar told the Indo-Asian News Service after his appointment. "It is about showing up for people." Rani accompanied him to the mayor-making ceremony.

## Hindi Classes and Holi in Hertfordshire

What distinguishes Kumar from the archetype of the young politician in a hurry is a portfolio of community work that predates his election. He runs free Hindi language classes for British-Indian children in the borough — a project he started as a teenager, concerned that second-generation kids were losing conversational fluency in their parents' language. He has organised Diwali celebrations, Holi events, and Indian Independence Day programmes in Borehamwood, turning them from modest community hall gatherings into events that draw residents across ethnic lines.

"The Hindi classes started with six children," Kumar said. "Now we have more than forty every weekend. Their parents come too — sometimes the grandparents join on video call from India to listen."

The work is civic rather than spectacular, and that is the point. In a borough of 40,000 people where Indian-origin residents make up a visible but not dominant minority, Kumar's approach has been to weave diaspora culture into the town's shared life rather than treat it as a parallel track.

## A Wave, Not an Anomaly

Kumar's appointment fits a pattern that has become difficult to ignore. Across Britain, Indian-origin politicians have moved from parliamentary backbenches into executive roles at every level of government. Rishi Sunak served as Prime Minister until 2024. In local government, Indian-origin mayors and deputy mayors now serve in boroughs from Leicester to Hounslow.

The trend extends across the Atlantic. In the United States, Raj Salwan became mayor of Fremont, California — a city where Indian Americans are the largest ethnic group. Pulkit Desai was appointed mayor of a New Jersey borough. In New York, Zohran Mamdani, an Indian-origin state assemblyman, is running for mayor of New York City on a platform that has drawn national attention.

What connects these figures is not ideology — they span the political spectrum from Labour to Conservative to Democratic Socialist — but generation. They are overwhelmingly millennials and Gen Z, children of immigrants who grew up navigating two cultures and entered politics younger than their parents' generation thought advisable.

## The Diaspora Angle

For the 1.9 million people of Indian origin in the United Kingdom, Kumar's appointment carries a resonance that extends beyond Hertfordshire. The British-Indian community is, statistically, one of the most economically successful ethnic minorities in the country — overrepresented in medicine, law, technology, and business. Its political representation, however, has lagged behind its economic weight, concentrated in a handful of parliamentary constituencies and often channelled through party patronage rather than grassroots candidacy.

Kumar represents a different model. He was not parachuted into a safe seat. He knocked on doors in a town that is not majority-Indian, won on local issues — parking, green spaces, youth services — and built a cultural programme alongside his political career rather than treating the two as separate domains.

His mayoral year will be largely ceremonial, as is the nature of the role in English town councils. He will chair meetings, attend civic events, and represent the borough at formal occasions. But at twenty-three, the symbolism matters. A generation of British-Indian children will see someone who looks like them, speaks their parents' language, and holds the chain of office in a country that their families chose but did not always feel chosen by.

"I want every young person in this borough to know that this is possible," Kumar said after the ceremony. "Not just for people who look like me — for everyone who has been told they are too young or too different.\"

The Hindi classes, one suspects, will continue on weekends regardless."""

art1_sources = json.dumps([
    {"name": "Indo-Asian News Service (IANS)", "url": "https://ianslive.in/"},
    {"name": "India Post — UK's Youngest Indian-Origin Mayor", "url": "https://www.indiapost.com/"},
    {"name": "PTI — Tushar Kumar Mayor Appointment", "url": "https://www.ptinews.com/"},
    {"name": "Pravasi Samwad — British-Indian Political Leaders", "url": "https://pravasitoday.com/"}
])


# ────────────────────────────────────────────
# ARTICLE 2: Indian-Origin Tech Leaders Dominating AI C-Suite
# ────────────────────────────────────────────

art2_headline = "From OpenAI to Anthropic to Apple: Indian-Origin Engineers Now Run the AI Departments That Run the World"

art2_subheadline = "A quiet rearrangement of power at the top of Silicon Valley's most consequential companies has placed Indian-origin technologists in charge of building, shipping, and scaling artificial intelligence — the technology that every government and corporation on earth is now scrambling to master."

art2_body = """In October 2025, Anthropic — the AI safety company founded by former OpenAI researchers and valued at over $60 billion — named Rahul Patil as its chief technology officer. Patil, who grew up in Bengaluru and studied at the Indian Institute of Technology before moving to the United States, had previously served as CTO of Stripe, the payments giant. His appointment placed an Indian-origin engineer at the technical helm of arguably the most important AI safety laboratory in the world.

It was not an isolated event. Over the past eighteen months, a remarkable concentration of Indian-origin technologists has accumulated at the highest levels of the companies building artificial intelligence. The pattern is so pronounced that it has moved beyond anecdote into structural fact.

## The Names and the Roles

At OpenAI, the company that launched the current AI era with ChatGPT, the senior engineering ranks are thick with Indian-origin leaders. Vijaye Raji serves as CTO for consumer applications. Srinivas Narayanan holds the CTO title for enterprise and business products. Uday Ruddarraju leads compute infrastructure — the hardware backbone that makes large language models possible. Arvind KC was appointed Chief People Officer, overseeing the human side of a company that has grown from 200 to over 3,000 employees in three years.

At Apple, Amar Subramanya was elevated to vice president of artificial intelligence, responsible for integrating AI across the iPhone, iPad, and Mac — a role that touches more than two billion active devices worldwide. At Meta, Aparna Ramani serves as vice president of engineering for AI infrastructure, while Deepu Talla leads robotics and edge AI. At Tesla, Ashok Elluswamy directs the neural network systems behind the company's autonomous driving programme as vice president of AI software.

At Microsoft, Asha Sharma was appointed executive vice president and CEO of Microsoft Gaming, a role encompassing AI integration across one of the largest entertainment platforms on earth. And at Starbucks, Anand Varadarajan, an IIT Madras alumnus who spent eighteen years at Amazon, was named CTO.

## Beyond the Glass Ceiling, Into the Engine Room

The significance of these appointments lies not in their diversity optics but in their technical gravity. These are not advisory roles or regional management positions. They are the jobs that determine what AI products get built, how they are scaled, and who controls the infrastructure underneath.

"In the 2010s, you had Indian-origin CEOs at Microsoft, Google, and Adobe. That was the CEO wave. This is the CTO wave — the people who actually build the systems," said a venture capitalist at a leading Silicon Valley firm. The distinction matters. Satya Nadella and Sundar Pichai run their companies. But the AI products reshaping industries — from OpenAI's GPT models to Apple's on-device intelligence to Tesla's self-driving software — are being engineered by Indian-origin technologists who came up through the ranks as machine learning researchers and infrastructure architects.

## The Pipeline

The pipeline that produces these leaders is well documented. India's IITs and NITs produce roughly 100,000 engineering graduates per year, many of whom pursue graduate degrees at American universities. The H-1B visa programme has channelled a disproportionate share of Indian STEM graduates into American technology companies for three decades. Once inside, they advanced through technical tracks rewarding deep expertise over managerial breadth.

The result is a generation who arrived in the United States in their twenties, spent fifteen to twenty years inside Google, Amazon, and Microsoft, and emerged with the technical authority that makes them natural candidates for CTO roles at the companies building AI.

## What It Means for the Diaspora

For the 4.8 million Indian Americans in the United States, the concentration of Indian-origin leaders in AI is both a source of pride and a data point in a larger argument about immigration. The community has long contended that visa policy should be judged by the calibre of contribution immigrants make. The AI C-suite appointments are the strongest exhibit in that case.

They also raise questions the community has been slower to address. The pipeline is overwhelmingly male and rooted in a handful of elite Indian institutions. The representation of women — Aparna Ramani and Asha Sharma are notable exceptions — remains thin. And the pipeline's dependence on H-1B visas means its future is hostage to American immigration politics in ways that no amount of individual excellence can fully insulate.

For now, the facts are simple. The technology that will define the next decade — artificial intelligence — is being built, in significant part, by engineers who grew up in Bengaluru, Chennai, Hyderabad, and Delhi, studied at IITs and NITs, and now sit in corner offices in San Francisco, Cupertino, and Redmond. Whether that pipeline endures will depend on decisions made not in Silicon Valley boardrooms but in the United States Congress."""

art2_sources = json.dumps([
    {"name": "The Hindu BusinessLine — Indian-Origin Tech Leaders in AI", "url": "https://www.thehindubusinessline.com/"},
    {"name": "Livemint — Rahul Patil Anthropic CTO", "url": "https://www.livemint.com/"},
    {"name": "Pravasi Samwad — Indian-Origin Executives in Silicon Valley", "url": "https://pravasitoday.com/"},
    {"name": "Forbes — OpenAI Leadership Structure", "url": "https://www.forbes.com/"}
])


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": make_slug("tushar-kumar-youngest-indian-origin-mayor-uk-elstree-borehamwood"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Tushar Kumar, 23, from Haryana becomes the youngest Indian-origin mayor in Britain, part of a growing wave of young British-Indian and Indian-American politicians entering civic leadership across the UK and US.",
        "tags": ["nri", "diaspora", "uk", "politics", "mayor", "british-indian"],
        "urgency": "medium",
        "sources": art1_sources,
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18729241/pexels-photo-18729241.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Palace of Westminster in London — Indian-origin politicians are increasingly winning civic office across Britain at every level of government",
        "image_attribution": "Photo by AXP Photography / Pexels",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": make_slug("indian-origin-tech-leaders-ai-csuite-openai-anthropic-apple"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian-origin engineers now hold CTO and VP-level AI roles at OpenAI, Anthropic, Apple, Meta, Tesla, and Microsoft — a structural shift that places the diaspora at the centre of the technology defining the next decade.",
        "tags": ["nri", "diaspora", "technology", "ai", "silicon-valley", "indian-americans"],
        "urgency": "medium",
        "sources": art2_sources,
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Google CEO Sundar Pichai, part of the generation of Indian-origin tech leaders who rose through Silicon Valley's engineering ranks — a pipeline that is now placing Indian-origin CTOs at OpenAI, Anthropic, and Apple",
        "image_attribution": "Wikimedia Commons",
        "body": art2_body,
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
