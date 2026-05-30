#!/usr/bin/env python3
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
        "headline": "The Blue Tigers Walked Into India House in London. The Diaspora Was Already Waiting.",
        "subheadline": "India's national football team received a rousing community welcome at the High Commission ahead of their Unity Cup third-place clash with Zimbabwe at Charlton Athletic's ground in south-east London.",
        "slug": make_slug("blue-tigers-india-house-london-unity-cup-diaspora-welcome"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Unity Cup reception at India House is a rare moment where Indian football and the UK diaspora meet face to face — a reminder that community support abroad extends beyond cricket.",
        "tags": ["nri", "diaspora", "football", "blue-tigers", "unity-cup", "london", "uk"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "PTI via Swadesi", "url": "https://swadesi.com/news/indian-football-team-gets-rousing-diaspora-welcome-in-uk-mpr3a0j7"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/sports-games/3354961-indian-football-team-celebrated-by-uk-diaspora-before-unity-cup-match"},
            {"name": "All India Football Federation", "url": "https://www.the-aiff.com/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/32/Gurpreet_Singh_Sandhu_2019_AFC_Asian_Cup.jpg",
        "body": """The scene at India House on Thursday evening was not what you would expect for a football team ranked 124th in the world. There were no TV crews jostling for position, no screaming fans behind barricades. Instead, there was something rarer: a room full of the Indian diaspora in London showing up for a sport that most of the community still considers an afterthought.

The Indian men's football team — the Blue Tigers — are in England for the Unity Cup, a four-nation tournament that brings together teams from India, Nigeria, Jamaica, and Zimbabwe. The tournament celebrates AfroCentric and global diaspora communities, and for India, it represents one of those small, meaningful windows of international exposure that the team rarely gets outside of Asian competition.

## A reception at the High Commission

The High Commission of India hosted a special reception where the players interacted with community members, shared insights about their training, and posed for the kind of group photos that will end up on family WhatsApp groups from Southall to Wembley.

India's Deputy High Commissioner to the UK, Kartik Pande, led an interactive session with captain Gurpreet Singh Sandhu and defenders Sandesh Jhingan and Rahul Bheke — three men who, between them, have spent years playing professional football in leagues that most of the Indian diaspora doesn't follow.

"Those who follow know that Indian football has seen encouraging progress in recent years, symbolised by grassroots participation, youth development and growing public interest," Pande said in his welcome address. The careful phrasing — "those who follow" — acknowledged an obvious truth: most don't.

## Football as a bridge

Kalyan Chaubey, president of the All India Football Federation (AIFF), spoke in Hindi and drew a connection between sport and the recently concluded India-UK Free Trade Agreement. "Football is a character-building sport, and for India to progress up the ranks of football, England's cooperation is important as a pioneer in the sport," he said. "India, on the other hand, can offer yoga and meditation mental health insights, given our rich cultural traditions."

It was a diplomatic speech at a diplomatic venue, but the underlying point was genuine enough. Football remains the world's most universal sport, and India's absence from the global stage has always been conspicuous.

## The match ahead

The Blue Tigers will face Zimbabwe on Saturday at The Valley, home ground of Charlton Athletic Football Club in south-east London. It is a third-place match — defending champions Nigeria face Jamaica in the final — but for the Indian team, any competitive international minutes on English soil carry weight.

The players issued a direct appeal to the diaspora in London: come out and support us. Whether the stands at The Valley will have a meaningful Indian contingent remains to be seen.

## Why it matters for the diaspora

For the 1.8 million-strong Indian community in the UK, cricket is the default sport. The IPL gets more WhatsApp forwards than any football fixture. But the Unity Cup offers something different: a chance to watch the national football team play live, in London, against international opposition. It is the kind of event that builds a new kind of diaspora connection — not through nostalgia or tradition, but through a sport that the rest of the world already speaks fluently.

The Blue Tigers walked into India House and found a community waiting. Whether that community shows up at The Valley on Saturday will say more about Indian football's diaspora future than any FIFA ranking ever could."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The UAE Is Overhauling Indian Passport Services. Four Million NRIs Will Notice the Difference.",
        "subheadline": "Kerala-based Alhind Group replaces BLS International as the outsourcing partner for Indian consular services across all seven emirates, with 16 new centres opening from July 1.",
        "slug": make_slug("uae-alhind-indian-passport-service-centers-16-new"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For the four million Indians in the UAE — the largest NRI concentration anywhere in the world — passport renewal and OCI processing is a routine fact of life. A change in who runs the service centres affects everyone.",
        "tags": ["nri", "diaspora", "uae", "passport", "alhind", "bls-international", "consular-services"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "VisaHQ", "url": "https://www.visahq.com/"},
            {"name": "Pravasi Samwad", "url": "https://pravasisamwad.com/"},
            {"name": "India Embassy Abu Dhabi", "url": "https://www.indembassyuae.gov.in/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1381722/pexels-photo-1381722.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """If you are one of the four million Indians living in the United Arab Emirates, there is a reasonable chance you have spent a morning at a BLS International service centre — clutching photocopies, checking queue numbers, and wondering whether the person ahead of you really needed to bring their entire extended family.

That experience is about to change. India's Embassy in Abu Dhabi has awarded Kerala-based Alhind Group a multi-year outsourcing contract to replace BLS International, which has handled Indian passport and visa services in the UAE since 2011. The transition takes effect on July 1, 2026.

## What is actually changing

Alhind will open 16 service centres covering every emirate, including secondary cities such as Al Ain, Kalba, and Khor Fakkan — areas that have historically been underserved. The current BLS network, while functional, has been concentrated in major urban centres like Dubai, Abu Dhabi, and Sharjah, forcing residents in smaller cities to travel for routine paperwork.

The centres will handle the full spectrum of consular services: passport renewals, OCI card processing, police clearance certificates, Indian visa applications, apostille and attestation services, and Global Entry verification.

## The pricing promise

Alhind has announced a single all-inclusive service fee of AED 19 — approximately ₹430 — above government charges. This is a notable simplification. Under the current system, additional charges for premium lounges, courier services, and other add-ons have been a consistent source of irritation for applicants.

The company also says it will deploy a new digital back-office system to reduce turnaround times, though specific targets have not been disclosed.

## Why the switch matters

BLS International has been the incumbent for 15 years — an unusually long run for any government outsourcing contract. During that period, the Indian population in the UAE has grown significantly, and the volume of consular services has expanded accordingly.

The UAE hosts the largest concentration of NRIs anywhere in the world. Workers in construction, retail, hospitality, and the professional services sector depend on passport services for everything from employment renewals to emergency travel. For many, a passport centre visit is their primary point of contact with the Indian government.

## The Alhind Group

Alhind is headquartered in Kozhikode, Kerala, and operates primarily in travel, tourism, and immigration services. The company has built a significant presence across the Gulf states, where the Malayali diaspora is particularly well-established. Whether this regional familiarity translates into better service delivery across the broader Indian community — which includes significant Gujarati, Punjabi, Tamil, and Hindi-speaking populations — remains to be seen.

## What NRIs should do now

The transition is set for July 1. Applicants with pending cases at BLS centres should ensure their applications are completed before the handover. For new applications after that date, Alhind will publish centre locations and appointment booking details in the coming weeks.

For the millions of Indians who have built their lives in the UAE — from labourers in Ajman to bankers in DIFC — the change is less about which company runs the counter and more about whether the process itself gets any easier. Fifteen years is a long time. The bar, frankly, is not high."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "GOPIO-Manhattan Has a New Leadership Team. The Bigger Story Is Why Diaspora Organisations Still Matter.",
        "subheadline": "The Global Organisation of People of Indian Origin's Manhattan chapter swore in its 2026–27 executive committee at Bharatiya Vidya Bhavan, with a Congressional primary candidate in the audience — a sign of the community's growing political weight.",
        "slug": make_slug("gopio-manhattan-new-leadership-2026-diaspora-organizations"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Diaspora organisations like GOPIO serve as the institutional backbone of Indian community life abroad — connecting new immigrants, building political networks, and maintaining cultural ties that individual families cannot sustain alone.",
        "tags": ["nri", "diaspora", "gopio", "new-york", "community-organization", "political-engagement"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
            {"name": "hi INDiA", "url": "https://hiindia.com/"},
            {"name": "Pravasi Samwad", "url": "https://pravasisamwad.com/"}
        ]),
        "score_total": 65,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16100484/pexels-photo-16100484.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On a Sunday afternoon in May, a group of Indian Americans gathered at the Bharatiya Vidya Bhavan in Manhattan to watch their new community leaders take an oath of office. There were no TV cameras. The event did not trend on social media. A Congressional primary candidate showed up, which tells you everything about who these organisations matter to — and why.

The Manhattan chapter of the Global Organisation of People of Indian Origin — GOPIO-Manhattan — inducted its newly elected executive committee and board of trustees for the 2026–27 term on May 17. Professor Rajasekhar Vangapaty was sworn in as president, leading a team that includes Bhavya Gupta as executive vice president, Dr. Vimal Goyle as vice president, Raj Punjabi as secretary, and Braj Aggarwal as treasurer.

## The room and its politics

GOPIO International Chairman Dr. Thomas Abraham, President Prakash Shah, and General Secretary Siddarth Jain all attended — the kind of top-level representation that signals the Manhattan chapter's importance within the global network.

But the more telling presence was Vichal Kumar, a candidate in the New York Democratic Congressional primary, who addressed the gathering and congratulated the new leadership. Politicians showing up at diaspora community events is not new, but the frequency is increasing. Indian Americans are now among the fastest-growing donor demographics in American politics, and organisations like GOPIO serve as concentrated access points.

## What GOPIO actually does

Founded in 1989 at the First Global Convention of People of Indian Origin in New York, GOPIO was originally focused on fighting human rights violations against people of Indian origin abroad. That remains part of the mission, but the organisation has evolved into something broader: a networking platform, a cultural anchor, and increasingly, a political springboard.

The Manhattan chapter was established in 2020, during the pandemic — an unlikely time to launch a community organisation, but also a period when diaspora Indians in New York felt acutely isolated. The chapter has since grown into a regular convener of community events, business networking sessions, and cultural programmes.

## The diaspora organisation question

There is a perennial debate in diaspora communities about whether formal organisations still serve a purpose. In an age of WhatsApp groups, Instagram communities, and Zoom calls, do people really need to show up at Bharatiya Vidya Bhavan on a Sunday to connect with their community?

The answer, based on who keeps showing up, appears to be yes. Diaspora organisations serve functions that informal networks cannot: they provide institutional continuity, they create pathways for political engagement, and they offer a visible, accountable point of contact for everyone from new immigrants seeking guidance to elected officials seeking constituents.

## The bigger picture

Indian Americans are now the highest-earning ethnic group in the United States, with a median household income well above the national average. They are overrepresented in technology, medicine, and finance. But political representation has lagged — a gap that organisations like GOPIO, Indian American Impact, and the Indian American Forum are actively working to close.

The upcoming GOPIO Convention in Mumbai, announced during the ceremony, is another reminder that these organisations operate in both directions. They help the diaspora engage with American politics, and they help the diaspora maintain its connection to India. It is a dual mandate that no WhatsApp group can replicate.

Professor Vangapaty spoke about "collaborative and inclusive leadership" in his welcome address. It is the kind of language that community leaders everywhere use. But in a political moment where Indian Americans are simultaneously more visible and more targeted than ever, the words carry more weight than they might have a decade ago."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
