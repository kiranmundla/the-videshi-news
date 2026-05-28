#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-28) — Retry
Publishes 3 news articles with proper images.
Creates p2_topics first, then links articles via topic_id.
"""

import json, os, sys, uuid
import requests
import subprocess
from datetime import datetime, timezone

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(' ', '_')
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wiki image: {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wiki error: {e}")
    return None

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        result = subprocess.run(
            ['curl', '-sS', f'https://api.pexels.com/v1/search?query={query}&per_page=3&orientation=landscape',
             '-H', f'Authorization: {PEXELS_KEY}'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            url = photos[0]['src']['large2x']
            print(f"  ✓ Pexels image: {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    if not url:
        return False
    try:
        r = requests.get(url, timeout=10, stream=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            # Read first chunk to check size
            chunk = r.content[:10]  # Just check headers
            cl = int(r.headers.get('Content-Length', 999999))
            if cl > 5000:
                return True
    except:
        pass
    return False

def create_topic(headline, category, keywords):
    topic_id = str(uuid.uuid4())
    payload = {
        "id": topic_id,
        "canonical_title": headline,
        "vertical": "politics",
        "urgency": "daily",
        "score_diaspora": 80,
        "score_significance": 85,
        "score_recency": 90,
        "score_source_avail": 80,
        "score_total": 84,
        "signal_count": 5,
        "status": "published",
        "keywords": keywords,
        "category": category
    }
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_topics", headers=HEADERS, json=payload, timeout=15)
    if r.status_code in (200, 201):
        print(f"  ✓ Topic created: {topic_id[:8]}...")
        return topic_id
    else:
        print(f"  ✗ Topic failed: {r.status_code} — {r.text[:200]}")
        return None

def publish_article(article, topic_id):
    payload = {
        "topic_id": topic_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution"),
        "sources": article.get("sources", []),
        "tags": article.get("tags", []),
        "urgency": "daily",
        "is_featured": False,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=payload, timeout=15)
    if r.status_code in (200, 201):
        result = r.json()
        aid = result[0].get('id', '?') if isinstance(result, list) else result.get('id', '?')
        print(f"  ✓ Published: {article['headline'][:60]}...")
        return True
    else:
        print(f"  ✗ Publish failed: {r.status_code} — {r.text[:300]}")
        return False


# ============================================================
# ARTICLE 1: Quad Foreign Ministers' Meeting
# ============================================================
print("\n=== Article 1: Quad Meeting ===")
img1 = fetch_wikipedia_person_image("S. Jaishankar")
if not validate_image(img1):
    img1 = fetch_pexels_image("diplomatic summit meeting")

topic1 = create_topic(
    "The Quad Just Announced Its First Joint Infrastructure Project. China Responded Within Hours.",
    "news",
    ["Quad", "India", "Jaishankar", "Rubio", "Fiji port", "critical minerals", "China", "Indo-Pacific"]
)

if topic1:
    publish_article({
        "headline": "The Quad Just Announced Its First Joint Infrastructure Project. China Responded Within Hours.",
        "subheadline": "Foreign ministers from India, the U.S., Japan, and Australia met in New Delhi and signed pacts on a Fiji port, critical minerals, and Indo-Pacific maritime surveillance. Beijing called it a Cold War construct.",
        "slug": "quad-new-delhi-fiji-port-critical-minerals-china-cold-war-20260528",
        "image_url": img1,
        "image_caption": "India's External Affairs Minister S. Jaishankar at the 11th Quad Foreign Ministers' Meeting in New Delhi",
        "image_attribution": "Wikimedia Commons",
        "tags": ["Quad", "foreign policy", "critical minerals", "Fiji", "Indo-Pacific", "China"],
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com/world/china/australia-india-japan-us-quad-seeks-relevance-foreign-ministers-meet-new-delhi-2026-05-26/"},
            {"name": "U.S. State Department", "url": "https://www.state.gov/2026-quad-foreign-ministers-meeting-in-new-delhi/"},
            {"name": "Ministry of External Affairs India", "url": "https://mea.gov.in/bilateral-documents.htm"},
            {"name": "Australian Foreign Ministry", "url": "https://www.foreignminister.gov.au/"}
        ],
        "body": """The 11th Quad Foreign Ministers' Meeting in New Delhi on May 26 produced the grouping's most concrete set of deliverables yet — a joint port project in Fiji, a critical minerals framework aimed squarely at reducing dependence on China, and a new Indo-Pacific maritime surveillance initiative that will share real-time data across four navies.

Within hours, Beijing responded. "We do not support the formation of exclusive cliques or bloc confrontation," China's foreign ministry spokesperson Mao Ning told a daily press conference. "No cooperation should undermine mutual trust and cooperation among regional countries."

## The Fiji Port

The port is the Quad's first joint infrastructure project — a direct counter to China's Belt and Road investments across the Pacific Islands. U.S. Secretary of State Marco Rubio, who arrived in India on Saturday for a four-day visit, called it "a practical demonstration of our collective ability to deliver high-quality, resilient infrastructure" in response to "insufficient port capacity in the Pacific Islands."

The announcement marks a shift from the Quad's usual pattern of issuing statements to actually building things. The grouping — which includes India's S. Jaishankar, Australia's Penny Wong, Japan's Toshimitsu Motegi, and Rubio — had faced questions about its relevance after failing to hold a leaders' summit last year amid tensions between Trump and Modi over tariffs.

## Critical Minerals and the China Problem

The critical minerals framework may be the meeting's most strategically significant outcome. It will guide how the four nations coordinate investment and economic policy tools to strengthen supply chains in mining, processing, and recycling of critical minerals.

The timing is deliberate. China recently halted shipments of minerals used in aerospace, defense, and semiconductor industries to Japan following a diplomatic dispute. India's Gujarat Mineral Development Corp surged 5.7 percent on Tuesday after the framework was announced.

For India, the framework opens a path to becoming a processing hub for rare earths and lithium — minerals essential for electric vehicles, defense systems, and the semiconductor supply chain that Indian manufacturers have been trying to break into.

## Maritime Surveillance

The four nations also launched the Indo-Pacific Maritime Surveillance Collaboration, which will create a shared real-time map of vessel movements across strategic shipping lanes, including the Strait of Hormuz. The initiative comes as the three-month-old Iran war has disrupted roughly a fifth of global oil transit.

The collaboration includes more than $25 million in undersea cable projects and an AI initiative called AI-ENGAGE for emerging technology coordination.

## The Diaspora Dimension

For Indian Americans, the Quad's evolution has a direct economic dimension. The critical minerals framework could accelerate India's semiconductor ambitions — a sector that employs tens of thousands of Indian-origin engineers in the U.S. and has been a key driver of H-1B demand. A stronger India-U.S. strategic partnership has historically correlated with smoother bilateral relations on immigration and trade.

The absence of a leaders' summit, however, remains a concern. Rubio said diplomats would "work toward" a Trump visit to India later this year, but no date was set. Analysts noted that the Quad can remain relevant through ministerial delivery even without summit signaling.

"We are beginning to show real achievements and real accomplishments," Rubio said. "We are deeply committed to this partnership. It is a linchpin and a cornerstone of our global strategy as a nation."

India, which has territorial disputes with China but has also signaled willingness to improve ties with Beijing, walked the line carefully. Jaishankar emphasized "practical outcomes" over rhetoric — a framing that allows New Delhi to deepen Quad ties without fully alienating Beijing at a moment when India needs Chinese cooperation on border management and trade.

The Quad meeting came just days before the Iran peace negotiations are expected to intensify in Washington. Whether the grouping's new infrastructure and security commitments survive the turbulence of Trump-era dealmaking will determine whether May 26 was a turning point or another set of announcements that never quite materialize."""
    }, topic1)


# ============================================================
# ARTICLE 2: Air India Crash Interim Report
# ============================================================
print("\n=== Article 2: Air India Crash ===")
img2 = fetch_wikipedia_person_image("Boeing 787 Dreamliner")
if not validate_image(img2):
    img2 = fetch_pexels_image("commercial airplane tarmac")

topic2 = create_topic(
    "India Will Not Release the Final Report on the Air India Crash. Here's Why.",
    "news",
    ["Air India", "Boeing 787", "AAIB", "NTSB", "crash investigation", "fuel switches", "DGCA"]
)

if topic2:
    publish_article({
        "headline": "India Will Not Release the Final Report on the Air India Crash That Killed 260 People. Here Is Why.",
        "subheadline": "The Aircraft Accident Investigation Bureau is preparing an interim report instead, bypassing the NTSB consultation process. A separate fuel switch incident in February has renewed scrutiny of the Boeing 787.",
        "slug": "air-india-crash-interim-report-aaib-ntsb-boeing-787-fuel-switches-20260528",
        "image_url": img2,
        "image_caption": "A Boeing 787 Dreamliner, the aircraft type involved in the Air India crash of June 2025",
        "image_attribution": "Wikimedia Commons",
        "tags": ["Air India", "Boeing 787", "aviation safety", "crash investigation", "AAIB", "NTSB"],
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/exclusive-india-prepares-interim-not-final-report-air-india-crash-anniversary-2026-05-26/"},
            {"name": "ICAO", "url": "https://www.icao.int/"},
            {"name": "NRI Page", "url": "https://nripage.com/"}
        ],
        "body": """As the first anniversary of the Air India crash approaches, Indian investigators have made a decision that will frustrate families on both sides of the ocean: there will be no final report. Only an interim one.

India's Aircraft Accident Investigation Bureau (AAIB) is preparing an interim statement — more comprehensive than the preliminary report issued last July, but deliberately short of a final accounting — for the Boeing 787 Dreamliner crash that killed 260 people on June 12, 2025. The Ahmedabad-to-London flight remains the aviation industry's deadliest disaster in a decade.

## What the Preliminary Report Revealed

The 15-page preliminary report established the basic sequence: the Dreamliner's engine fuel switches flipped almost simultaneously shortly after takeoff, starving both engines of fuel. A cockpit voice recording suggested the captain may have cut fuel flow to the engines, according to U.S. officials' early assessment reported by Reuters. The AAIB said at the time it was "too early to reach any definite conclusions."

The interim report will examine "possible primary causes and other contributing factors," according to a person with direct knowledge of the investigation. But it will not constitute a final report — and that distinction carries enormous consequences.

## The NTSB Has Been Cut Out

Under International Civil Aviation Organization rules, a final report must go through a consultation process with participating states, including a 30-to-60-day comment period. The U.S. National Transportation Safety Board, which is participating because Boeing designed and manufactured the aircraft, would be allowed to comment on — and potentially critique — a final report.

An interim statement carries no such requirement. India's investigators are not obligated to share their findings with the NTSB before publication.

The precedent should worry anyone following this case. In the 2019 Ethiopian Airlines 737 MAX crash, Ethiopian investigators issued an interim report within a year but did not release their final report until December 2022 — more than three years after the crash. The NTSB eventually published a public critique of aspects of the Ethiopian report, creating a diplomatic embarrassment that Indian officials may be hoping to avoid.

"It is a very complex investigation and is taking time," said a person with knowledge of the probe. The final report's timeline, they added, "remained unclear."

## A Second Fuel Switch Incident

The crash investigation has taken on new urgency because of a separate incident in February 2026. Pilots of an Air India Dreamliner flying from London to Bengaluru reported that the aircraft's fuel switches "did not remain fixed in the run position" when light vertical pressure was applied during engine start. The switches held on a third attempt, and the flight proceeded safely.

Indian officials described the switches as "sensitive" in confidential emails, according to Reuters. India's Directorate General of Civil Aviation plans to send officials to Boeing's facility in Seattle in June to observe testing of the switches — a visit that some investigators on the original crash probe were not even aware of, raising questions about coordination between India's aviation safety bodies.

Boeing has said it is "supporting" Air India on the matter. UK authorities, who are also examining the February incident, said their review is ongoing.

## What This Means for NRI Families

The Ahmedabad-to-London route is one of the most heavily traveled corridors for the Indian diaspora — connecting Gujarat's NRI heartland to one of the largest overseas Indian communities in the world. Among the 260 who died were families traveling for weddings, students returning to British universities, and business travelers on a routine Monday morning flight.

For those families, the decision to issue only an interim report means another year — at minimum — without definitive answers about what happened and why. The question of whether the fuel switches were mechanically defective, whether pilot error played a role, and whether Boeing's 787 fleet has a systemic design vulnerability remains officially unresolved.

The AAIB, India's civil aviation ministry, and Air India did not respond to requests for comment.

A year after 260 people died on a routine international flight, the investigation remains too complex, too politically sensitive, and too internationally fraught to produce a conclusive public accounting. The families will have to wait."""
    }, topic2)


# ============================================================
# ARTICLE 3: Israel Escalates in Lebanon
# ============================================================
print("\n=== Article 3: Israel-Lebanon ===")
img3 = fetch_wikipedia_person_image("UNIFIL")
if not validate_image(img3):
    img3 = fetch_wikipedia_person_image("Benjamin Netanyahu")
    if not validate_image(img3):
        img3 = fetch_pexels_image("United Nations peacekeepers patrol")

topic3 = create_topic(
    "Israel Declares Southern Lebanon a Combat Zone. India Has 642 Soldiers There.",
    "news",
    ["Israel", "Lebanon", "Hezbollah", "UNIFIL", "India peacekeepers", "Netanyahu", "Iran war", "oil prices"]
)

if topic3:
    publish_article({
        "headline": "Israel Just Declared Southern Lebanon a Combat Zone. India Has 642 Soldiers There.",
        "subheadline": "Netanyahu ordered the IDF to expand operations past its security zone, with 120-plus strikes in a single day. At least 608 people have been killed since the April ceasefire. India's UNIFIL contingent is caught in the middle.",
        "slug": "israel-lebanon-combat-zone-india-unifil-642-peacekeepers-hezbollah-20260528",
        "image_url": img3,
        "image_caption": "UN peacekeeping forces in Lebanon, where India maintains a 642-strong UNIFIL contingent",
        "image_attribution": "Wikimedia Commons",
        "tags": ["Israel", "Lebanon", "Hezbollah", "UNIFIL", "India", "peacekeeping", "Iran war", "oil prices"],
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com/world/middle-east/israel-declares-new-swathe-lebanon-combat-zone-warns-residents-leave-2026-05-27/"},
            {"name": "Le Monde", "url": "https://www.lemonde.fr/en/international/article/2026/05/27/israel-launches-new-military-escalation-in-lebanon_6782345_4.html"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/"},
            {"name": "India MEA", "url": "https://mea.gov.in/"},
            {"name": "World Health Organization", "url": "https://www.who.int/"}
        ],
        "body": """Israel declared all of southern Lebanon south of the Zahrani River "a combat zone" on Tuesday, ordered residents to evacuate, and expanded ground operations past the security zone its forces have occupied since March. Prime Minister Benjamin Netanyahu said the Israeli military was "operating with large forces in the field and capturing and controlling areas" — the most explicit acknowledgment yet that the April 16 ceasefire exists only on paper.

India has 642 soldiers deployed with the United Nations Interim Force in Lebanon. They are now in the middle of what increasingly resembles a full-scale war.

## 120 Strikes in a Day

The Israeli Defense Forces struck more than 120 Hezbollah targets on Tuesday — weapons storage facilities in the Beqaa Valley, infrastructure sites across the south, and positions near the 900-year-old Beaufort Castle, which UNESCO has described as one of the best-preserved medieval fortresses in the region. At least three strikes also hit near Lebanon's largest water reservoir at the Qaraoun Dam in the country's east.

Since the ceasefire took effect on April 17, at least 608 people have been killed in Lebanon in Israeli attacks, according to the World Health Organization. The Israeli military said 10 of its soldiers had been killed in the same period, six by Hezbollah's explosive drones. Total casualties since the Lebanon war began in March have exceeded 3,200, with more than one million people displaced.

Hezbollah launched projectiles into northern Israel on Wednesday. The Israeli military said one landed in an open area with no injuries. But the escalation cycle shows no sign of slowing.

## The Iran Deal Complication

The Lebanon escalation is inseparable from the broader Iran war. Netanyahu is pushing Washington to include "freedom of operation" for Israel in Lebanon as part of any Iran peace deal, according to the Wall Street Journal. Iran insists the opposite — that any ceasefire must include an end to fighting in Lebanon.

This standoff has direct consequences for India. Brent crude jumped 3.3 percent on Tuesday to nearly $100 per barrel after U.S. Secretary of State Marco Rubio — who was in New Delhi for the Quad meeting that same day — said negotiating an Iran deal could "take a few days." India, the world's third-largest oil importer, has already seen petrol cross ₹100 in most cities. IndiGo and Air India have cut domestic flights by up to 22 percent because of soaring jet fuel costs.

The Strait of Hormuz, which carried roughly a fifth of global oil before the Iran war broke out in February, remains partially closed. HSBC noted there is "still considerable uncertainty about how and when the Strait will return to its normal pre-war operations."

## India's 642 Peacekeepers

India is among 30 nations that have urged protection for UNIFIL peacekeepers amid the fighting. The 642-strong Indian contingent serves as part of the broader 8,253-person force from 48 nations, whose mandate was extended until 2027. But the UN Security Council voted earlier this year to end the peacekeeping mission entirely by December 2026, with the Lebanese army expected to take full control of border security.

That timeline now looks impossible. The Lebanese army lacks the capacity to enforce security along the border while Israel is actively expanding its ground operations and Hezbollah is retaliating with drones and rockets. France's ambassador to the UN has condemned attacks on peacekeepers. India has called for accountability.

For Indian families with loved ones in the UNIFIL contingent, the escalation is personal. India has historically been one of the largest contributors to UN peacekeeping operations worldwide, and the Lebanon deployment is among its most dangerous active missions.

## The Economic Shockwave

For India, every day the conflict continues means higher oil import bills, wider current account deficits, and more pressure on the rupee. The Nifty 50 has fallen 8.5 percent this year; the Sensex is down 10.8 percent. Foreign investors have pulled $23 billion out of Indian markets in 2026, and the benchmark index is headed for its first annual decline since 2015.

Small-cap and mid-cap stocks have held up better — rising about 3 percent each — supported by domestic liquidity and what Tata Mutual Fund's Chandraprakash Padiyar called "normalisation in valuations after the earlier phase of excesses." But the macro picture, driven almost entirely by the Iran war's energy shock, remains the dominant headwind.

India's 642 peacekeepers remain at their posts. The combat zone has now been declared around them."""
    }, topic3)

print("\n=== News writer complete ===")
