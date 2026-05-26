#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 20:30 UTC batch
Topics: 1) Garden Grove chemical crisis — 50,000 evacuated in Orange County, five miles from Disneyland, NRI impact
        2) Trump's live phone call to Delhi — "Anything India wants, they get" — America@250 celebration with AR Rahman, QUAD tomorrow
"""

import json, os, uuid, re, requests, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Supabase config ──
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

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, params, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(slug_base, date_suffix="20260525"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Pexels helper ──
pexels_env = Path.home() / "workspace" / ".env.pexels"
PEXELS_KEY = None
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.split("=", 1)[1].strip()

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=15
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    try:
        img_data = requests.get(image_url, timeout=20).content
        content_type = "image/jpeg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        h = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        r = requests.post(upload_url, headers=h, data=img_data, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return image_url

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')
now_plus1 = (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Garden Grove Chemical Crisis — 50,000 Evacuated in Orange County
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("garden-grove-chemical-crisis-50000-evacuated-orange-county-nri")
headline1_prefix = "garden grove"
if slug1 not in existing_slugs and not any(headline1_prefix in h for h in existing_headlines_lower):
    body1 = """A 34,000-gallon tank of methyl methacrylate has been overheating at a GKN Aerospace facility in Garden Grove, California, since Thursday. The explosion risk has been eliminated. The evacuation order has not.

As of Monday morning, 50,000 people remain displaced from their homes across six cities in Orange County — Garden Grove, Westminster, Anaheim, Cypress, and parts of surrounding communities. Schools are closed. Businesses are shuttered. Four of five evacuation shelters hit capacity over the weekend. A class-action lawsuit has already been filed.

The facility is five miles from Disneyland. Four miles from Knott's Berry Farm. And directly in the middle of one of the densest South Asian residential corridors in Southern California.

## What Happened

On May 21, a storage tank at GKN Aerospace Transparency Systems on Western Avenue began overheating. The tank contains methyl methacrylate — MMA — a toxic, highly flammable chemical used to manufacture acrylic plastics for aircraft canopies and transparencies. A faulty valve prevented crews from off-loading the chemical or introducing a neutralizing stabilizer.

The temperature inside the tank climbed past 100°F. Officials warned that the tank could rupture, spilling up to 7,000 gallons of toxic material, or explode — potentially triggering secondary explosions in adjacent tanks at the facility.

By Friday, evacuation orders covered a one-mile buffer around the facility. Governor Gavin Newsom declared a state of emergency. President Trump authorized a federal emergency declaration.

Overnight between Sunday and Monday, a crack in the tank was confirmed — paradoxically, this was good news. The crack relieved internal pressure, and the Orange County Fire Authority announced that the catastrophic explosion scenario was "off the table." But the crack also means the tank's structural integrity is compromised. It could fail in other ways. The 7,000 gallons of MMA remain inside.

"The catastrophic event is eliminated," said OCFA Division Chief Craig Covey. "We are now focused on the controlled release and remediation."

The evacuation order remains in force because MMA vapor, even in small concentrations, is a respiratory and neurological hazard. Residents cannot return until officials confirm that any release can be contained and the air quality meets safety thresholds.

## Why This Is a Five-Day Crisis, Not a Five-Hour One

This is not a typical industrial accident. MMA does not behave like a petroleum spill. It is volatile at relatively low temperatures, its vapors are heavier than air and settle into low-lying areas, and it polymerizes — turns into a solid — in uncontrolled conditions, which can generate additional heat and accelerate the chemical reaction.

Fire crews have been spraying the tank with water around the clock to keep its temperature down. The OCFA brought in subject matter experts from federal agencies, chemical manufacturers, and hazardous materials response teams. EPA Administrator Lee Zeldin flew to the site and said authorities were evaluating a "low-volume controlled release" as the safest path forward.

The tank cannot simply be emptied. The faulty valve that started the crisis is the same valve that would ordinarily allow a controlled drain. Until crews can either repair the valve or engineer an alternative extraction method, the 7,000 gallons stay where they are — inside a cracked, compromised vessel.

Firefighters and chemical engineers are essentially improvising. There is no playbook for this specific failure mode.

## The Orange County Map That Matters

The evacuation zone covers Garden Grove, Westminster, and parts of Anaheim — three cities with some of the highest concentrations of Asian and South Asian residents in Southern California.

Orange County is home to an estimated 90,000 Indian Americans. The broader AAPI population exceeds 600,000. The cities in the evacuation zone — particularly Garden Grove, Westminster, and Anaheim — sit within the residential and commercial orbit of one of the largest South Asian economic corridors in the region.

Indian grocery stores along Brookhurst Street. Hindu and Sikh temples within the evacuation radius. Dental practices, medical offices, and IT consulting firms run by Indian American families — all shuttered. The Patel Brothers on Katella Avenue, the single most recognizable Indian grocery chain in the country, sits just outside the mandatory zone but well within the area of voluntary evacuation advisories.

For Indian families in the zone, the disruption is layered. Many are multigenerational households — grandparents who flew in on B-2 visitor visas, parents who work from home on H-1B-sponsored remote arrangements, children in local school districts. When an evacuation order hits a multigenerational household, you are not evacuating four people. You are evacuating eight. Some of those eight do not drive. Some do not speak English as their first language. Some have chronic health conditions that make temporary shelter arrangements medically complicated.

The evacuation shelters — at Garden Grove High School, Cypress College, Magnolia High School, and Christ Cathedral — hit capacity by Saturday. Families with the resources to do so went to hotels in Irvine, Tustin, or further into South County. Families without those resources stayed in their cars, stayed with friends, or returned to homes within the evacuation zone against official orders — because the alternative was sleeping on a gymnasium floor with eighty strangers.

## GKN Aerospace's Track Record

GKN Aerospace is not a small operation. It is a subsidiary of Melrose Industries, a British engineering conglomerate. The Garden Grove facility manufactures transparent acrylic and polycarbonate components for military and commercial aircraft — cockpit canopies, cabin windows, sensor housings.

The facility has a documented history of environmental violations. A proposed class-action lawsuit, filed within 48 hours of the crisis, alleges that GKN failed to maintain safety systems, did not adequately monitor chemical storage conditions, and delayed reporting the overheating to local authorities.

The lawsuit will take months to resolve. The evacuation will take days, possibly weeks. The respiratory and neurological health monitoring of residents exposed to MMA vapors — even at low concentrations — will take years.

## Disneyland Stayed Open

One detail that has drawn attention and criticism: Disneyland, located five miles from the GKN facility, remained open throughout the crisis. Disney issued a statement saying it was monitoring the situation in coordination with local authorities.

The park draws approximately 50,000 visitors per day. The evacuation zone displaces approximately 50,000 residents. One group was told to leave their homes. The other was told to enjoy their vacation.

The optics are not great. But they are also not unusual. Disneyland has remained open during wildfires, during the pandemic (briefly), and during virtually every other crisis that has not physically reached its property line. The park is its own jurisdiction in all but name, and its economic footprint in Anaheim — approximately $8.5 billion annually — gives it a gravitational pull that municipal emergency orders rarely override.

## What This Means for NRIs in Orange County

For the Indian diaspora in Southern California, the Garden Grove crisis is a stress test of something that rarely gets discussed: what happens when an industrial disaster hits a neighborhood where a significant portion of residents are immigrants.

The evacuation communications were issued in English and Vietnamese (Westminster has a large Vietnamese community). Hindi, Gujarati, Punjabi, and Telugu — languages spoken by tens of thousands of Orange County residents — were not included in initial emergency broadcasts.

FEMA's emergency alert system does not translate into South Asian languages. Orange County's 211 information hotline has translation services, but the wait times during a crisis with 50,000 displaced people exceeded two hours on Friday.

The Indian Consulate in San Francisco — the closest Indian consular office — has not issued a public advisory about the Garden Grove crisis. There is no official communication channel between the Indian government and the approximately 90,000 Indian nationals and Indian Americans in Orange County who may be affected.

For Indian families in the evacuation zone, the practical response has been what it always is: the community organized itself. WhatsApp groups circulated in Gujarati and Hindi with shelter locations, air quality updates, and offers of temporary housing. Gurdwaras opened their doors. Temple committees sent volunteers. The formal emergency infrastructure did not account for them. The informal infrastructure — the one built on family networks, religious institutions, and group chats — did.

This is not a complaint. It is a description. And it is a pattern that repeats every time a natural disaster, industrial accident, or public health emergency hits a community where the immigrant population is large enough to matter but not large enough — or not organized enough politically — to be reflected in the official emergency response apparatus.

The tank has cracked. The explosion is off the table. The evacuation continues. And 50,000 people — including an uncounted but significant number of Indian and South Asian families — wait for the all-clear to go home."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "A Chemical Tank Has Been Threatening to Explode in Orange County for Five Days. Fifty Thousand People Are Evacuated. The Facility Is Five Miles from Disneyland. And Nobody Is Issuing Emergency Alerts in Hindi.",
        "subheadline": "A 34,000-gallon tank of methyl methacrylate at a GKN Aerospace facility in Garden Grove, California, has been overheating since May 21. The explosion risk has been eliminated after a crack relieved pressure, but 50,000 residents across six cities remain evacuated. Governor Newsom declared a state of emergency. Trump authorized a federal emergency declaration. The evacuation zone sits in one of the densest South Asian residential corridors in Southern California — Orange County is home to approximately 90,000 Indian Americans. Evacuation communications were issued in English and Vietnamese. Hindi, Gujarati, Punjabi, and Telugu were not included. The Indian Consulate has not issued a public advisory. Disneyland, five miles away, stayed open.",
        "slug": slug1,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "Orange County is home to approximately 90,000 Indian Americans. The evacuation zone — Garden Grove, Westminster, parts of Anaheim — sits in one of the densest South Asian residential corridors in Southern California. Indian grocery stores along Brookhurst Street. Temples within the evacuation radius. Multigenerational households with grandparents on visitor visas, parents on H-1B remote work, and children in local schools — all displaced. The evacuation shelters hit capacity within 48 hours. Emergency communications were issued in English and Vietnamese but not in Hindi, Gujarati, Punjabi, or Telugu. FEMA alerts do not translate into South Asian languages. The Indian Consulate in San Francisco has not issued a public advisory. WhatsApp groups in Gujarati and Hindi became the de facto emergency communication channel. Gurdwaras and temple committees organized shelter and food. This is the pattern every time a disaster hits an area with a significant Indian population — the formal emergency infrastructure does not account for them, and the informal infrastructure built on family networks and religious institutions fills the gap.",
        "tags": ["Garden Grove", "chemical crisis", "Orange County", "California", "GKN Aerospace", "methyl methacrylate", "evacuation", "NRI", "Indian Americans", "emergency response", "Disneyland", "state of emergency", "environmental disaster"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Overheating chemical tank in California no longer at risk of exploding, fire officials say", "url": "https://www.reuters.com/world/us/potential-crack-california-chemical-tank-may-prevent-explosion-fire-official-says-2026-05-25/"},
            {"name": "Fox LA — Garden Grove chemical crisis reaches 5th day", "url": "https://www.foxla.com/news/garden-grove-chemical-leak-gkn-aerospace-evacuation"},
            {"name": "USA Today — California officials race to avoid chemical tank explosion", "url": "https://www.usatoday.com/story/news/nation/2026/05/24/garden-grove-chemical-tank-explosion-risk/"},
            {"name": "Wikipedia — Garden Grove chemical leak", "url": "https://en.wikipedia.org/wiki/Garden_Grove_chemical_leak"},
            {"name": "People — Disneyland to Remain Open Amid Ongoing Chemical Incident", "url": "https://people.com/disneyland-open-garden-grove-chemical-crisis/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now_iso,
        "body": body1
    })
    print(f"✓ Article 1 prepared: Garden Grove chemical crisis / NRI impact")
else:
    print(f"✗ Article 1 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Trump's "Anything India Wants, They Get" — The Delhi Call
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("trump-anything-india-wants-they-get-delhi-call-ar-rahman-quad")
headline2_prefix = "anything india wants"
if slug2 not in existing_slugs and not any(headline2_prefix in h for h in existing_headlines_lower):
    body2 = """On Sunday evening in New Delhi, the United States Ambassador to India, Sergio Gor, hosted what he called the "grandest-ever celebration" of the United States on Indian soil — a star-studded gala marking the upcoming 250th anniversary of American independence.

The show opened with a live telephone call from the President of the United States.

"I just want to say hello to everybody," Donald Trump said over the speakers. "I love the Prime Minister. Modi is great. He is my friend. And we have never been closer to India. And India can count on me and our country 100 percent."

Then he said this: "Anything India wants, they get."

The audience — a mix of Indian government officials, business leaders, diplomats, and cultural figures — cheered. Secretary of State Marco Rubio, standing onstage, smiled. External Affairs Minister S. Jaishankar, who spoke next, offered measured diplomatic praise.

And then A.R. Rahman took the stage and played "Jai Ho."

## The Spectacle

The event was unmistakably a production. Ambassador Gor, who has been in New Delhi for approximately five months, orchestrated an evening that included the US Marine Corps band Orient Express (flown in from Japan), the Village People (flown in from wherever the Village People currently reside), and a full performance by the two-time Academy Award winner A.R. Rahman — accompanied by choreographer Shiamak Davar's dance troupe.

Rahman performed "Jai Ho," "Chaiyya Chaiyya," and "Maa Tujhe Salaam." The audience was on its feet.

The Village People played "Y.M.C.A." — a song that has become, through a series of cultural mutations that no one fully understands, the unofficial anthem of the Trump political movement.

"I don't know anyone who is a better event producer than all of our ambassadors, that Sergio has put on here today," Rubio said from the stage, complimenting Gor. It was the kind of thing you say when you know the president is on the phone and the cameras are rolling.

## What Trump Said — and What It Means

"Anything India wants, they get" is one of those sentences that sounds like policy but reads like affection. It is the language of a personal relationship being projected onto a bilateral one. It is the way Trump speaks about allies he is currently courting — warm, transactional, and carefully unspecific.

Twenty-four hours earlier, Rubio and Jaishankar had held a joint press conference in New Delhi where the specific things India wants were discussed in detail — and the answers were considerably less generous.

On visas: Jaishankar raised concerns about "challenges that legitimate travelers face in respect of visa issuance." Rubio said the reforms were "not India-specific" and that there would be "some bumps on that road."

On H-1B: Registrations have dropped 38.5 percent. India's top IT firms lost 40 percent of their H-1B approvals in the latest cycle. TCS alone lost 3,242 visas. Rubio called it "modernization."

On anti-Indian racism: Rubio acknowledged that "every country in the world has stupid people" and said India should not listen to them. This is true but not exactly a policy response.

On trade: India committed to purchasing $500 billion in US goods over the next five years. This is the number that Gor highlighted and that the US side wants headlined. It is a purchasing commitment, not a trade deal — India is agreeing to buy American energy, defense equipment, and technology, not receiving reciprocal access to American markets.

On Iran: Rubio used New Delhi as his stage to tell reporters that the US would give diplomacy "every chance to succeed" before dealing with Iran "another way." He described a "pretty solid thing on the table" involving the Strait of Hormuz and Iran's nuclear material. India — which depends on Middle Eastern oil routes that run through the Strait — listened carefully and said nothing publicly.

So when Trump says "anything India wants, they get," the question is: which India? And which anything?

## The QUAD Meeting

The timing of the gala was not accidental. On Monday — today — New Delhi hosts the Quad Foreign Ministers' Meeting, bringing together Rubio, Jaishankar, Australian Foreign Minister Penny Wong, and Japanese Foreign Minister Toshimitsu Motegi.

The Quad — the informal strategic grouping of the US, India, Japan, and Australia — has been the primary vehicle through which India and the United States have built their security partnership in the Indo-Pacific. Its agenda includes maritime cooperation, critical minerals supply chains, cybersecurity, semiconductor collaboration, and the ongoing effort to present a democratic counterweight to China's regional influence.

Jaishankar, speaking ahead of the meeting, described the Indo-Pacific as poised to become "a big energy lifeline" — a pointed reference to the fact that the Strait of Hormuz crisis has forced India to completely redraw its oil supply map in 90 days, and the Indo-Pacific shipping routes that bypass the Middle East are now strategically essential.

Rubio, for his part, used his India visit to reinforce the message that the US-India relationship is about more than trade numbers. "If I think about all of the key issues and all of the key opportunities of the modern economy, India and the United States together are perfectly positioned to work together," he said at the gala.

The Quad meeting is where that positioning gets tested. The pleasantries happened at the gala. The negotiations happen in the conference room.

## What the Diaspora Heard

For the Indian diaspora in the United States, Trump's call and the Delhi gala exist in a dissonant key.

"Anything India wants, they get" is a phrase that resonates differently when you are an Indian national who has been waiting 300 days for a B-2 visa appointment at the Mumbai consulate. Or when you are an Indian-born software engineer whose H-1B registration was among the 38.5 percent that got rejected. Or when you are the parent of an Indian student whose F-1 visa appointment was frozen when Rubio paused student visa scheduling worldwide.

The warmth is real. Trump's personal regard for Modi is well-documented and, by all available evidence, genuine. Rubio's respect for Jaishankar — whom he called "truly a wise gentleman" at the gala — appears sincere. The strategic convergence between the US and India is not performance; it is structural.

But "anything India wants, they get" sits uneasily next to "the changes, while they may be having a disproportionate impact on a place like India that provides so many high-skilled workers to the US economy, it is not a system that is targeted at India" — which is what Rubio said at the press conference one day before Trump's phone call.

The relationship between the two countries is at its warmest in diplomatic history. The relationship between the two countries' immigration systems is at its most hostile in a decade. Both of these things are true at the same time. Both are being said by the same administration, to the same audience, on the same four-day trip.

A.R. Rahman played "Maa Tujhe Salaam" to a cheering crowd that included the Secretary of State who, hours earlier, had told India's foreign minister that the pain its citizens were experiencing at American consulates was a "period of adjustment."

The music was spectacular. The dissonance was louder.

## What Comes Next

The Quad meeting on Monday will produce a joint statement. It will reference maritime security, supply chains, technology cooperation, and the rules-based international order. It will not reference H-1B denials, visa wait times, or the fact that Indian IT firms just lost 40 percent of their visa approvals.

India will buy $500 billion in American goods. America will sell India energy and weapons. The strategic partnership will deepen. And 4.8 million Indian Americans will continue to navigate a system that tells them, through one channel, that they are welcome — and through another, that they are being "modernized" out of the queue.

Trump said "anything India wants, they get." The QUAD communiqué will be released later today. Watch what India actually gets."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Trump Called Into a Delhi Gala and Said 'Anything India Wants, They Get.' A.R. Rahman Played 'Jai Ho.' The Village People Played 'Y.M.C.A.' Twenty-Four Hours Earlier, Rubio Had Told India Its Visa Pain Was a 'Period of Adjustment.'",
        "subheadline": "At the America@250 celebration in New Delhi on Sunday, President Trump surprised the audience with a live phone call declaring 'I love Modi' and 'anything India wants, they get.' A.R. Rahman performed 'Jai Ho' and 'Maa Tujhe Salaam.' The US Marine Corps band and the Village People were flown in. Secretary of State Rubio called it the grandest celebration of the US ever held in India. But the gala capped a four-day visit in which Rubio told India that its citizens' visa pain was a 'period of adjustment,' that H-1B reforms were 'not India-specific,' and that immigration modernization would have 'some bumps.' India committed to $500 billion in US goods purchases. On Monday, the Quad Foreign Ministers meet in New Delhi to discuss Indo-Pacific security, maritime cooperation, and the structural partnership that exists alongside the structural immigration hostility.",
        "slug": slug2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "For 4.8 million Indian Americans, the Delhi gala exists in a dissonant key. 'Anything India wants, they get' resonates differently when you have been waiting 300 days for a B-2 visa at the Mumbai consulate — or when your H-1B registration was among the 38.5 percent rejected — or when your child's F-1 appointment was frozen. The warmth is real: Trump's regard for Modi is genuine, and Rubio's respect for Jaishankar appears sincere. The strategic convergence is structural, not theatrical. But 'anything India wants, they get' was said by the same president whose administration reduced Indian IT firms' H-1B approvals by 40 percent, proposed a $250 visa integrity fee, and froze student visa scheduling worldwide. A.R. Rahman played 'Maa Tujhe Salaam' to a cheering crowd that included the Secretary of State who had told India's foreign minister, hours earlier, that their citizens' visa pain was 'a period of adjustment.' The music was spectacular. The dissonance was louder. India will buy $500 billion in American goods. America will sell India energy and weapons. And 4.8 million Indian Americans will continue navigating a system that tells them through one channel that they are welcome and through another that they are being 'modernized' out of the queue.",
        "tags": ["Trump", "Modi", "Rubio", "Jaishankar", "Delhi", "QUAD", "India-US relations", "America@250", "A.R. Rahman", "diplomacy", "visa", "H-1B", "NRI", "diaspora", "Sergio Gor", "Indo-Pacific"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "India Outbound — Trump joins in over a call, Rubio, A R Rahman star in America@250 celebrations in Delhi", "url": "https://indiaoutbound.info/io-exclusive/trump-joins-in-over-a-call-rubio-a-r-rahman-star-in-america250-celebrations-in-delhi/"},
            {"name": "The Bridge Chronicle — Trump Joins Delhi Event via Call, Praises PM Modi", "url": "https://thebridgechronicle.com/trump-joins-delhi-event-via-call-praises-pm-modi"},
            {"name": "Fox News — Rubio pushes back on India's concerns over US visa curbs", "url": "https://foxnews.com/politics/rubio-pushes-back-indias-concerns-us-visa-curbs-says-policy-must-america-first-trump"},
            {"name": "The Indian Eye — Marco Rubio arrives in India for Historic First Visit", "url": "https://theindianeye.com/2026/05/23/marco-rubio-arrives-in-india-for-historic-first-visit/"},
            {"name": "The Indian Eye — New Delhi to host Quad Foreign Ministers on May 26", "url": "https://theindianeye.com/2026/05/25/new-delhi-quad-foreign-ministers-may-26/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now_plus1,
        "body": body2
    })
    print(f"✓ Article 2 prepared: Trump Delhi call / QUAD meeting")
else:
    print(f"✗ Article 2 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# PUBLISH + IMAGE SOURCING
# ══════════════════════════════════════════════════════════════

if not articles:
    print("\n⚠ No new articles to publish. Exiting.")
    exit(0)

print(f"\n📝 Publishing {len(articles)} articles...")

for i, art in enumerate(articles):
    art_id = art["id"]
    print(f"\n--- Article {i+1}: {art['headline'][:80]}...")

    try:
        result = sb_post("p2_articles", art)
        print(f"  ✓ Inserted: {art_id}")
    except Exception as e:
        print(f"  ✗ Insert failed: {e}")
        continue

    if i == 0:
        img_url = fetch_pexels_image("chemical factory industrial emergency", "hazmat firefighters chemical plant")
    else:
        img_url = fetch_pexels_image("India American flag diplomatic celebration", "India United States flags diplomacy")

    if img_url:
        filename = f"{art['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        try:
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {"image_url": final_url})
            print(f"  ✓ Image linked")
        except Exception as e:
            print(f"  ⚠ Image PATCH failed: {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY
# ══════════════════════════════════════════════════════════════

print("\n📉 Applying score decay to older news articles...")
try:
    old_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=7)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.35",
        "limit": "200"
    })
    for a in old_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 35})
    print(f"  Decayed {len(old_arts)} articles (>7d → 35)")

    mid_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=3)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.50",
        "limit": "200"
    })
    mid_arts = [a for a in mid_arts if a["id"] not in {x["id"] for x in old_arts}]
    for a in mid_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 50})
    print(f"  Decayed {len(mid_arts)} articles (3-7d → 50)")
except Exception as e:
    print(f"  ⚠ Decay error: {e}")

# ══════════════════════════════════════════════════════════════
# GIT COMMIT + PUSH
# ══════════════════════════════════════════════════════════════

print("\n📦 Committing and pushing...")
repo_dir = Path.home() / "workspace" / "the-videshi-news"
try:
    subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True, timeout=15)
    result = subprocess.run(
        ["git", "commit", "-m", f"news: Garden Grove chemical crisis + Trump Delhi call QUAD ({now.strftime('%Y-%m-%d %H:%M')} UTC)"],
        cwd=repo_dir, capture_output=True, text=True, timeout=15
    )
    print(f"  Commit: {result.stdout.strip()[:100]}")
    push = subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True, text=True, timeout=30)
    if push.returncode == 0:
        print("  ✓ Pushed to main → Vercel auto-deploy")
    else:
        print(f"  ⚠ Push issue: {push.stderr[:200]}")
except Exception as e:
    print(f"  ⚠ Git error: {e}")

print("\n✅ News writer batch complete.")
