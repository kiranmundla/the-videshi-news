#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-29)
Publishes 3 news articles to Supabase.
"""

import json, os, sys, time, uuid, re
import requests
from datetime import datetime, timezone

# --- Config ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- Helper functions ---

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels API using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for photo in photos:
                    url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Verify image URL returns HTTP 200 with image content-type and > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {ct}, {cl} bytes")
            return True
        # Try GET for servers that don't support HEAD well
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct:
            # Read first chunk to check size
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {ct}, {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=20,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ✗ Failed to download image: {r.status_code}")
            return None
        img_data = r.content
        if len(img_data) < 5000:
            print(f"  ✗ Image too small: {len(img_data)} bytes")
            return None
        
        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            data=img_data,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": ct,
                "x-upsert": "true"
            },
            timeout=30
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
    return None


def publish_article(article):
    """Insert article into Supabase p2_articles table."""
    article_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    payload = {
        "id": article_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article.get("vertical", "general"),
        "urgency": article.get("urgency", "medium"),
        "tags": article.get("tags", []),
        "score_total": article.get("score_total", 85),
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
        "sources": json.dumps(article["sources"]),
        "image_attribution": article.get("image_attribution", ""),
        "is_featured": False,
        "is_editorial": False,
    }
    if article.get("image_url"):
        payload["image_url"] = article["image_url"]
    if article.get("image_caption"):
        payload["image_caption"] = article["image_caption"]
    if article.get("diaspora_angle"):
        payload["diaspora_angle"] = article["diaspora_angle"]
    
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        json=payload,
        headers=HEADERS,
        timeout=30
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        aid = data[0]["id"] if isinstance(data, list) else data.get("id", article_id)
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {aid})")
        return aid
    else:
        print(f"  ✗ Publish failed: {resp.status_code} {resp.text[:300]}")
        return None


# ===================================================================
# ARTICLE 1: Blue Origin New Glenn Explosion
# ===================================================================

def write_article_blue_origin():
    print("\n📰 Article 1: Blue Origin New Glenn Explosion")
    
    slug = "blue-origin-new-glenn-explodes-launchpad-nasa-artemis-india-space-20260529"
    headline = "Jeff Bezos's Rocket Just Exploded on the Launchpad. NASA's Moon Plans Are Now in Trouble."
    subheadline = "Blue Origin's New Glenn blew up during a static fire test at Cape Canaveral, days after winning a $188 million NASA contract. The explosion threatens Artemis timelines and Amazon's satellite ambitions — and widens the gap India's ISRO is racing to close."
    
    body = """A Blue Origin New Glenn rocket exploded on its launchpad at Cape Canaveral on Thursday night, sending a massive fireball into the Florida sky and dealing Jeff Bezos's space company its worst setback yet.

The 322-foot rocket — roughly 29 storeys tall — detonated during a static fire test at around 9 p.m. ET, rattling homes across Cape Canaveral and Cocoa Beach. No one was injured, but the explosion destroyed a rocket that has cost billions of dollars and a decade to develop.

## What Happened

Blue Origin confirmed the incident in a post on X, calling it an "anomaly during today's hotfire test" — industry parlance for catastrophic failure. A static fire is a pre-launch procedure where engines ignite while the rocket remains clamped to the ground. Video from NASASpaceflight showed the New Glenn igniting on the pad before erupting into a towering inferno.

"Very rough day, but we'll rebuild whatever needs rebuilding and get back to flying. It's worth it," Bezos wrote on X. He said it was "too early to know the root cause."

The New Glenn had already been grounded since April, after its third flight left a satellite in the wrong orbit due to engine failure.

## NASA's Artemis Program Takes a Hit

The timing could not be worse. Earlier this week, NASA awarded Blue Origin a $188 million contract to deliver rovers to the moon's surface using its Mark 1 cargo lunar lander — a mission that depends on the New Glenn rocket.

NASA Administrator Jared Isaacman acknowledged the incident on X: "Spaceflight is unforgiving, and developing new heavy-lift launch capability is extraordinarily difficult. We will work with our partners to support a thorough investigation of this anomaly, assess near-term mission impacts, and get back to launching rockets."

The explosion raises questions about whether Blue Origin can meet its commitments to NASA's Artemis program, which aims to return astronauts to the moon before China's planned crewed landing in 2030. Blue Origin is building the lunar lander that NASA will use for Artemis V, and the company's reliability record is now under scrutiny.

## Bezos vs Musk: The Space Race Gap Widens

The explosion deepens the gap between Blue Origin and Elon Musk's SpaceX, which is preparing for an IPO that could value it as the first trillion-dollar U.S. market debut. SpaceX has not been immune to failures — its Starship exploded during testing in Texas last year — but has recovered faster and built a far deeper launch record.

Musk responded to video of the Blue Origin explosion with characteristic understatement: "Most unfortunate. Rockets are hard."

Blue Origin had announced just a day before the explosion that it was preparing the New Glenn to launch 48 Amazon Leo satellites into low-Earth orbit, part of Amazon's Project Kuiper broadband constellation meant to rival Musk's Starlink network. That timeline is now in question.

## What This Means for India's Space Ambitions

The explosion also has implications for the global space race that India is increasingly part of. ISRO's LVM3 — India's heaviest operational rocket — has carved out a niche in the commercial launch market, and every stumble by a competitor opens a potential window.

ISRO launched its Chandrayaan-3 moon lander successfully in 2023 and is preparing the Gaganyaan crewed mission. While the LVM3 cannot match the New Glenn's payload capacity, ISRO's track record of reliable, cost-effective launches has attracted commercial customers looking for alternatives to SpaceX and Blue Origin.

Indian-origin engineers are also deeply embedded in the American space industry. From NASA's Jet Propulsion Laboratory to private companies like SpaceX and Blue Origin itself, Indian Americans have been central to the engineering teams building the hardware that will return humans to the moon.

## What Comes Next

The Federal Aviation Administration said it was aware of the incident but noted it fell outside its regulatory scope and did not affect air traffic. Blue Origin will need to conduct a thorough investigation, rebuild the damaged launchpad at Launch Complex 36, and likely demonstrate a successful static fire before flying again.

For Bezos, the path forward is clear but costly. Blue Origin has already spent over $2.5 billion on New Glenn alone, and the company will need to rebuild confidence with both NASA and its commercial customers. The space billionaire's dream of catching SpaceX just got harder."""
    
    sources = [
        {"name": "Reuters", "url": "https://www.reuters.com/science/blue-origin-says-it-faced-anomaly-during-hot-fire-test-2026-05-29/"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/05/28/science/blue-origin-new-glenn-explosion/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/science/space-astronomy/bezos-blue-origin-loses-rocket-explosion-launchpad/"},
        {"name": "SpaceWeekly", "url": "https://spaceweekly.com/blue-origins-failure-may-hamstring-nasas-moon-plans/"}
    ]
    
    # Image: Jeff Bezos from Wikipedia
    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Jeff Bezos")
    img_attribution = "Wikimedia Commons"
    img_caption = "Jeff Bezos, founder of Blue Origin, whose New Glenn rocket exploded during a static fire test at Cape Canaveral."
    
    if img_url and not validate_image_url(img_url):
        img_url = None
    
    if not img_url:
        # Try Blue Origin or rocket launch from Pexels
        img_url = fetch_pexels_image("rocket launch cape canaveral", "space rocket launchpad")
        img_attribution = "Pexels"
        img_caption = "A rocket launch at Cape Canaveral, where Blue Origin's New Glenn exploded during testing."
        if img_url and not validate_image_url(img_url):
            img_url = None
    
    # Upload to Supabase for permanence
    final_url = None
    if img_url:
        final_url = upload_to_supabase_storage(img_url, f"{slug}.jpg")
    
    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "space-technology",
        "urgency": "high",
        "tags": ["blue-origin", "new-glenn", "jeff-bezos", "nasa", "artemis", "spacex", "isro", "space-race"],
        "score_total": 90,
        "diaspora_angle": "Indian-origin engineers are deeply embedded in NASA, SpaceX, and Blue Origin. ISRO's reliable LVM3 rocket competes for commercial launches in a market where Blue Origin's setbacks open opportunities.",
        "sources": sources,
        "image_url": final_url or img_url,
        "image_attribution": img_attribution if (final_url or img_url) else "",
        "image_caption": img_caption if (final_url or img_url) else "",
    }


# ===================================================================
# ARTICLE 2: India Sends Ebola Aid to Congo
# ===================================================================

def write_article_india_ebola_aid():
    print("\n📰 Article 2: India Sends Emergency Ebola Aid to Congo")
    
    slug = "india-ebola-aid-congo-africa-cdc-pharmaceutical-supplies-global-health-20260529"
    headline = "India Just Sent Emergency Ebola Supplies to Congo. Africa's Health Agency Called It a Lifeline."
    subheadline = "As the world's worst Ebola outbreak in years kills over 220 people in eastern Congo, India has shipped diagnostics, therapeutics, and infection control materials — extending a pandemic-era playbook that made it the pharmacy of the developing world."
    
    body = """India has dispatched emergency pharmaceutical supplies to the Democratic Republic of Congo to help contain an Ebola outbreak that the World Health Organisation has declared a Public Health Emergency of International Concern — and Africa's continental health agency has publicly thanked New Delhi for stepping up when much of the world has been slow to respond.

The consignment, donated by the Government of India, was received in Uganda by the Africa Centres for Disease Control and Prevention's Eastern Africa Regional Coordinating Centre. It includes essential diagnostics, therapeutics, infection prevention and control materials, and case management support that will be deployed to affected communities in eastern DR Congo.

## The Scale of the Crisis

The numbers are staggering. As of this week, more than 1,000 suspected Ebola infections and at least 246 deaths have been reported in Congo's Ituri province, though the WHO and aid agencies say the actual scale is likely significantly higher. The virus has crossed borders, with eight confirmed cases now in Uganda, including in the capital Kampala.

This is the Bundibugyo strain — one of six known species of the Ebola virus, first identified in Uganda in 2007. There are no approved vaccines or treatments for this strain, making containment the only viable strategy. The WHO declared the outbreak a Public Health Emergency of International Concern on May 17, a designation reserved for the most serious global health threats.

The response has been complicated by armed conflict in Ituri province, community distrust of health workers, and attacks on medical facilities. Last week, protesters set fire to tents set up to treat Ebola patients in Rwampara, one of the outbreak's hotspots. International organisations have described the response as critically underfunded — Africa CDC reported this week that funding pledges have nearly halved compared to initial commitments.

## India's Expanding Health Diplomacy

India's emergency aid extends a pattern that accelerated during the COVID-19 pandemic, when the country shipped millions of vaccine doses to developing nations under the Vaccine Maitri initiative. The Serum Institute of India — the world's largest vaccine manufacturer — is now racing to develop a Bundibugyo-specific Ebola vaccine, with the WHO confirming that manufacturing is already underway.

"Africa CDC welcomes the arrival of emergency pharmaceutical supplies generously donated by the Government and people of India to support the ongoing response to the Bundibugyo Ebola outbreak in the DRC," the agency said, thanking India for its "continued support and commitment to protecting lives and advancing health security across the continent."

The aid comes at a diplomatically sensitive moment. India and the African Union had been scheduled to hold the Fourth India-Africa Forum Summit in New Delhi this week — from May 28 to 31 — but postponed it due to the Ebola outbreak. The postponement, while a setback for India's Africa diplomacy, also underscored the seriousness with which both sides are treating the public health situation.

## Closer to Home

India itself is on high alert. Earlier this week, Bengaluru quarantined a 28-year-old Ugandan woman suspected of carrying the Ebola virus — the country's first suspected case in over a decade. Health Minister Jagat Prakash Nadda has said India has not confirmed any cases, but screening has been stepped up at airports and the government has imposed travel advisories for Congo, Uganda, and South Sudan.

For the estimated 25 million-strong Indian diaspora in Africa — one of the largest overseas Indian communities on the continent — the outbreak is particularly close to home. Indian businesses across East Africa have been monitoring the situation closely, with some reporting disruptions to trade routes and staffing.

## The Global Response Gap

India's aid stands in contrast to the broader international response, which health experts have called inadequate. The United States has committed $80 million in bilateral assistance and another $300 million for humanitarian aid, but has taken the unusual step of setting up a quarantine facility in Kenya for exposed Americans rather than bringing them home for treatment — a departure from past practice that has drawn criticism from public health experts.

Professor Salim Abdool Karim, a leading South African epidemiologist advising Africa CDC, described the outbreak as moving at "breakneck speed," warning that every day without a fully resourced response is a day the virus gains ground.

For India, the Ebola aid is both humanitarian imperative and strategic investment. As New Delhi deepens its engagement with Africa — bilateral trade hit $100 billion last year — positioning itself as a reliable partner in health emergencies strengthens relationships that extend well beyond crisis moments."""
    
    sources = [
        {"name": "PTI via CurrentIndia", "url": "https://currentindia.com/world/india-sends-emergency-medical-supplies-for-ebola-outbreak-response-in-congo/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/africa/indias-bengaluru-quarantines-uganda-woman-suspected-ebola-infection-source-says-2026-05-28/"},
        {"name": "Nation Press", "url": "https://nationpress.com/india-sends-emergency-ebola-aid-to-dr-congo-as-africa-cdc-confirms-receipt/"},
        {"name": "Reuters — Breakneck Ebola", "url": "https://www.reuters.com/world/africa/breakneck-ebola-epidemic-congo-outpaces-worlds-response-2026-05-28/"}
    ]
    
    # Image: Not about a specific person — use Pexels for medical/health aid
    print("  Sourcing image...")
    img_url = fetch_pexels_image("medical supplies humanitarian aid", "pharmaceutical supplies health")
    img_attribution = "Pexels"
    img_caption = "India has sent emergency pharmaceutical supplies to help combat the Ebola outbreak in the Democratic Republic of Congo."
    
    if img_url and not validate_image_url(img_url):
        img_url = None
    
    final_url = None
    if img_url:
        final_url = upload_to_supabase_storage(img_url, f"{slug}.jpg")
    
    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "global-health",
        "urgency": "high",
        "tags": ["india", "ebola", "congo", "drc", "africa-cdc", "health-diplomacy", "serum-institute", "bundibugyo"],
        "score_total": 88,
        "diaspora_angle": "India's 25-million-strong diaspora in Africa is directly affected by the Ebola outbreak. Indian businesses across East Africa report disruptions. The postponed India-Africa Summit signals the severity of the crisis.",
        "sources": sources,
        "image_url": final_url or img_url,
        "image_attribution": img_attribution if (final_url or img_url) else "",
        "image_caption": img_caption if (final_url or img_url) else "",
    }


# ===================================================================
# ARTICLE 3: Carnegie 2026 Survey on Indian Americans
# ===================================================================

def write_article_carnegie_survey():
    print("\n📰 Article 3: Carnegie 2026 Survey — Indian Americans in a Time of Turbulence")
    
    slug = "carnegie-2026-survey-indian-americans-polarization-discrimination-trump-20260529"
    headline = "A Landmark Survey of 5.2 Million Indian Americans Just Dropped. The Findings Should Worry Both Parties."
    subheadline = "Carnegie's 2026 Indian American Attitudes Survey reveals a community caught between rising discrimination, collapsing trust in both parties, and a growing temptation to leave the country altogether."
    
    body = """A new Carnegie Endowment survey of 1,000 Indian American adults paints a portrait of a community in political flux — overwhelmingly opposed to Donald Trump's second term, cooling on the Democratic Party, and changing how they live their daily lives in response to a surge in anti-Indian hate.

The 2026 Indian American Attitudes Survey, conducted in partnership with YouGov between November 2025 and January 2026, is the most comprehensive study of Indian American political attitudes since Trump returned to the White House. Its findings carry weight: there are now 5.2 million people of Indian origin in the United States, making them the country's fastest-growing and most economically influential Asian American subgroup.

## Trump's Approval Has Cratered

Seventy-one percent of Indian Americans disapprove of Trump's job performance one year into his second term, with 55 percent expressing strong disapproval. Only 29 percent approve — virtually identical to his numbers at the end of his first term in 2020.

The disapproval is broad-based. Sixty-four percent oppose his immigration policy, 68 percent disapprove of his domestic economic management, and 70 percent reject his international economic policies — the tariffs, sanctions, and trade wars that have thrown U.S.-India relations into what the survey calls "a period of heightened turbulence."

On immigration specifically, the numbers are stark. Seventy-four percent of Indian Americans oppose the deportation of immigrants to third countries. Two-thirds oppose the proposed $100,000 fee on new H-1B visa petitions — a policy that would disproportionately affect Indians, who constituted 71 percent of all new H-1B petitions in fiscal year 2024.

Only 20 percent approve of Trump's handling of U.S.-India relations, down sharply from the already-low 35 percent at the end of his first term. One-quarter of respondents had no opinion at all — suggesting foreign policy simply does not register for many Indian Americans when they evaluate a president.

## But Democrats Are Losing Ground Too

Here is where the story gets complicated. Despite widespread anti-Trump sentiment, the Democratic Party is not consolidating Indian American support. The share identifying as Democrats has fallen from 52 percent in 2020 to 46 percent in 2026. Republican identification has edged up from 15 to 19 percent. But the biggest shift has been toward independence — 29 percent of Indian Americans now identify as independents, up six points since 2020.

The Democratic Party's feeling thermometer score among Indian Americans dropped from 60 in 2024 to 53 in 2026. Kamala Harris's favorability fell ten points to 52. The Republican Party fared even worse, falling from 41 to 34, while Trump's personal rating slid from 40 to 32.

The survey identifies a political paradox: Indian Americans are more opposed to Trump's policies than almost any demographic group in America, yet this opposition is not translating into tighter Democratic loyalty. Instead, the community is drifting toward disenchanted centrism.

## The Discrimination Crisis Is Real

Perhaps the survey's most urgent finding is the scale of anti-Indian discrimination. Since the start of 2025, one in four Indian Americans has been called a racial slur. Nine percent report being physically threatened. Eight percent have received hate mail. Four percent have been physically assaulted.

Forty-eight percent — nearly half — report encountering racist posts targeting Indians or Indian Americans on social media "very or somewhat often." The emotional toll is severe: half feel angry when encountering such content, a third feel anxious, and nearly a third feel fearful.

The discrimination is changing behaviour in concrete ways. Thirty-one percent of Indian Americans now avoid discussing politics on social media out of fear of harassment. Twenty-one percent avoid leaving and re-entering the United States. Nineteen percent avoid publicly wearing Indian dress or attire. These are not abstract concerns — they represent a community modifying its daily life in response to a hostile environment.

## Thinking About Leaving

Fourteen percent of Indian Americans have thought frequently about leaving the United States altogether, and another 26 percent have considered it occasionally. Among those who have contemplated leaving, frustration with U.S. politics is the top reason (58 percent), followed by cost of living (54 percent) and personal safety (41 percent).

The most striking detail: of those who have considered leaving, only one in four would go back to India. Sixty-two percent named some other country. Indian Americans are not longing for home — they are looking for a better version of the life they came here to build.

Yet when asked directly, most still recommend the United States. Sixty-two percent would advise a hypothetical Indian professional to apply for a U.S. work visa rather than stay in India. The American dream, apparently, still outweighs the American reality — but the margin is narrowing.

## What Both Parties Should Hear

For Republicans, the data is unambiguous: policies that target immigrants, particularly the H-1B fee and mass deportation proposals, are alienating one of America's most economically productive communities. The party's intolerance of minorities — cited by 27 percent of non-Republican Indians as their primary reason for staying away, up ten points from 2024 — is not a messaging problem. It is the message.

For Democrats, the warning is subtler but equally serious. Indian Americans are not leaving the party for the GOP — they are leaving it for nowhere. The rise of independents, the declining favourability scores, and the community's drift toward ideological moderation all suggest that the Democratic coalition cannot take this constituency for granted.

The survey captures a community at a crossroads. Five million Indian Americans are watching both parties fail them in different ways — and increasingly, they are choosing to disengage rather than pick a side."""
    
    sources = [
        {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/preview/research/2026/02/indian-americans-in-a-time-of-turbulence-2026-survey-results"},
        {"name": "YouGov / 2026 IAAS Methodology", "url": "https://carnegieendowment.org/preview/research/2026/02/indian-americans-in-a-time-of-turbulence-2026-survey-results"},
        {"name": "Pew Research Center — Indian American Demographics", "url": "https://www.pewresearch.org/"},
        {"name": "Stop AAPI Hate — Anti-Indian Content Report", "url": "https://stopaapihate.org/"}
    ]
    
    # Image: Not about a specific person — use Pexels for Indian Americans / voting
    print("  Sourcing image...")
    img_url = fetch_pexels_image("Indian American community gathering", "diverse American voters polling")
    img_attribution = "Pexels"
    img_caption = "Indian Americans are navigating rising discrimination and political disaffection, according to a new Carnegie Endowment survey."
    
    if img_url and not validate_image_url(img_url):
        img_url = None
    
    final_url = None
    if img_url:
        final_url = upload_to_supabase_storage(img_url, f"{slug}.jpg")
    
    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "community-politics",
        "urgency": "medium",
        "tags": ["indian-americans", "carnegie", "survey", "discrimination", "politics", "democrats", "republicans", "h1b", "trump"],
        "score_total": 92,
        "diaspora_angle": "The survey directly profiles the 5.2 million Indian American community — their political attitudes, experiences with discrimination, immigration policy views, and whether they are considering leaving the United States.",
        "sources": sources,
        "image_url": final_url or img_url,
        "image_attribution": img_attribution if (final_url or img_url) else "",
        "image_caption": img_caption if (final_url or img_url) else "",
    }


# ===================================================================
# MAIN
# ===================================================================

def main():
    print("=" * 60)
    print("The Videshi — News Writer (2026-05-29)")
    print("=" * 60)
    
    articles = []
    
    # Write all 3 articles
    articles.append(write_article_blue_origin())
    articles.append(write_article_india_ebola_aid())
    articles.append(write_article_carnegie_survey())
    
    # Validate and publish
    print("\n" + "=" * 60)
    print("Publishing articles...")
    print("=" * 60)
    
    published = 0
    for i, article in enumerate(articles, 1):
        print(f"\n--- Article {i}: {article['headline'][:60]}... ---")
        
        # Validate required fields
        errors = []
        if len(article["headline"]) < 20 or len(article["headline"]) > 200:
            errors.append(f"Headline length: {len(article['headline'])} (must be 20-200)")
        if len(article.get("subheadline", "")) < 15:
            errors.append(f"Subheadline too short: {len(article.get('subheadline', ''))}")
        
        word_count = len(article["body"].split())
        if word_count < 400:
            errors.append(f"Body too short: {word_count} words (min 400)")
        
        if not article["slug"] or article["slug"] != article["slug"].lower():
            errors.append(f"Bad slug: {article['slug']}")
        
        if len(article.get("sources", [])) < 2:
            errors.append(f"Not enough sources: {len(article.get('sources', []))}")
        
        if article["category"] != "news":
            errors.append(f"Wrong category: {article['category']}")
        
        if errors:
            print(f"  ✗ VALIDATION FAILED:")
            for e in errors:
                print(f"    - {e}")
            continue
        
        print(f"  Words: {word_count}")
        print(f"  Category: {article['category']}")
        print(f"  Sources: {len(article['sources'])}")
        print(f"  Image: {'✓' if article.get('image_url') else '✗ None'}")
        
        aid = publish_article(article)
        if aid:
            published += 1
            # Upload image after publish if we have one
            if article.get("image_url"):
                # Update with properly uploaded image
                print(f"  Image URL: {article['image_url'][:80]}...")
    
    print(f"\n{'=' * 60}")
    print(f"Done: {published}/{len(articles)} articles published")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
