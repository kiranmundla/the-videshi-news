#!/usr/bin/env python3
"""Videshi NRI World Writer — 2026-06-14 18:00 UTC"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Supabase setup ────────────────────────────────────────────
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

# ── Image compression & upload ──────────────────────────────
from PIL import Image

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_bytes, filename):
    """Upload compressed image to Supabase storage bucket 'article-images'."""
    compressed = compress_image(img_bytes)
    print(f"  Compressed: {len(compressed)//1024} KB")
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(
        f"{SB_URL}/storage/v1/object/article-images/{filename}",
        headers=upload_headers,
        data=compressed,
        timeout=30,
    )
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"

def download_image(url):
    """Download an image from a URL."""
    r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
    r.raise_for_status()
    return r.content

# ── Source images ─────────────────────────────────────────────
print("Sourcing images...")

# Article 1: Oil tanker — Wikimedia Commons
img1_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Kerfons_oil_tanker_and_gendarmerie_maritime.jpg/1280px-Kerfons_oil_tanker_and_gendarmerie_maritime.jpg"
try:
    img1_bytes = download_image(img1_url)
    print(f"  Article 1 image: {len(img1_bytes)//1024} KB downloaded")
except Exception as e:
    print(f"  ⚠ Article 1 image download failed: {e}")
    img1_bytes = None

# Article 2: Hindu Temple Sunnyvale CA — Wikimedia Commons
img2_url = "https://upload.wikimedia.org/wikipedia/commons/d/d1/Hindu_Temple_Sunnyvale_CA.jpg"
try:
    img2_bytes = download_image(img2_url)
    print(f"  Article 2 image: {len(img2_bytes)//1024} KB downloaded")
except Exception as e:
    print(f"  ⚠ Article 2 image download failed: {e}")
    img2_bytes = None

# ── Article 1 ──────────────────────────────────────────────────
art1_id = str(uuid.uuid4())
art1_slug = make_slug("indian-sailors-crossfire-us-navy-gulf-tanker-strikes")

art1_image_url = ""
if img1_bytes:
    try:
        art1_image_url = upload_to_supabase(img1_bytes, f"{art1_id}.jpg")
        print(f"  ✅ Article 1 image uploaded: {art1_image_url[:60]}...")
    except Exception as e:
        print(f"  ⚠ Article 1 upload failed: {e}")

art1_body = """Three Indian seafarers are dead, and dozens more have been plucked from burning tankers in the Gulf of Oman after the United States Navy struck three Indian-crewed vessels in a single week — the deadliest escalation yet in Washington's blockade of Iranian oil exports.

The toll is no longer abstract. Shivanand Chaurasia, 35, a father of two from Deoria in Uttar Pradesh, was among the crew aboard the Palau-flagged MT Settebello when a U.S. aircraft fired precision munitions into the ship's engine room on Wednesday. His wife Sushila Devi, the family's sole remaining adult, sat on the floor of their home and wept. "If he had told us about the dangers, I would have called him back," she told reporters. "The government should not allow people to go there."

Chaurasia was the sole earner. His family now has nothing except a death it did not see coming.

## Three ships, four days

The sequence was rapid and relentless. On Monday, U.S. forces disabled the Marivex, another Palau-flagged tanker, with precision strikes. On Wednesday came the Settebello — 24 Indian crew, three dead, 21 rescued by Oman's navy after the ship issued a distress call reporting an engine fire. On Thursday, Hellfire missiles tore into the engine room of the Guinea-Bissau-flagged MT Jalveer, carrying 20 Indian seafarers. All survived, evacuated again by Omani forces.

In each case, U.S. Central Command offered the same explanation: the crews "repeatedly failed to comply with directions from American forces" while attempting to transport oil from Iran.

India's response has been uncharacteristically sharp. The Ministry of External Affairs summoned U.S. chargé d'affaires Jason Meeks — twice in 48 hours, a diplomatic rarity — to convey what spokesperson Randhir Jaiswal called India's "deepest concerns over the ongoing attacks."

"These attacks must cease and end," Jaiswal told reporters at an inter-ministerial briefing on Thursday. "We also call for dialogue and diplomacy so that we can have an early return to peace and stability in the region."

## A country that runs on its sailors

The numbers explain why Delhi is agitated. India is the world's second-largest supplier of merchant seafarers after the Philippines, with more than 300,000 sailors working across global shipping fleets. Over 18,000 are currently deployed in the Middle East alone. These are not high-net-worth expats. They are working-class men — overwhelmingly from Kerala, Goa, Tamil Nadu, and small towns across North India — for whom the sea is the most reliable route out of poverty.

Shipping Minister Sarbananda Sonowal called the deaths a "profound loss to our maritime family" and said the government had directed all agencies to "remain on heightened alert and maintain readiness to respond to any contingency involving Indian seafarers."

x-official:https://x.com/sarbanandsonwal/status/1932779820238385479

But critics want more than vigilance memos. "India has responded with a routine diplomatic protest and apparent efforts to downplay the significance of the attacks," said Brahma Chellaney, a strategic affairs analyst in New Delhi. "Had the victims been Chinese sailors instead, Beijing would almost certainly have reacted very differently."

The opposition has been blunter. The Aam Aadmi Party urged Prime Minister Modi to raise the matter directly with President Trump at the upcoming G7 sidelines. Congress said the government's policies had "emboldened external powers to act against Indian interests with impunity."

## Another death, another indignity

Separately, a fourth Indian sailor died last week — not from a missile, but from the quieter cruelty of neglect. Nishanth Uirthanathan, 35, suffered fatal medical complications aboard the MT Celestial while docked at Duqm Port in Oman on June 11. The Forward Seamen's Union of India said his body remained on the vessel for more than two days without proper refrigeration, with the crew "using cold water bottles in a desperate attempt to slow decomposition."

The Indian embassy in Muscat said it was making arrangements for repatriation. For the families back home, the wait is measured in something worse than days.

## What comes next

Manoj Yadav, general secretary of the Forward Seamen's Union, warned that the attacks could deter workers from taking seafaring jobs entirely, worsening an industry already short on labour. "The repeated incidents demonstrate the alarming deterioration of safety and security in one of the world's most important maritime corridors," he said.

Iran, which has its own reasons to amplify the story, condemned the strikes as "clear evidence of America's ongoing policy of armed robbery and state piracy." The geopolitics are complicated. The human cost is not. Three men left their families to earn a living on the water. They are not coming home."""

art1 = {
    "id": art1_id,
    "headline": "Three Dead, Three Ships Hit: Indian Sailors Are Caught in the Crossfire of America's Iran Blockade",
    "subheadline": "In the deadliest week for Indian merchant seafarers in years, U.S. Navy strikes on three tankers off Oman killed three crew and forced scores to abandon ship — prompting India to summon the American diplomat twice and demand the attacks stop.",
    "slug": art1_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "India has 300,000+ seafarers working globally, many from working-class families who depend on maritime income. The Gulf crisis threatens both lives and livelihoods across the diaspora.",
    "tags": ["nri", "diaspora", "indian-sailors", "gulf-crisis", "maritime", "us-india"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-summons-top-us-diplomat-second-time-protest-strikes-ships-off-oman-source-2026-06-12/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-demands-end-us-attacks-ships-after-three-sailors-killed-2026-06-11/"},
        {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com/international/iran-us-war-us-hits-third-ship-with-indian-onboard-in-oman"},
        {"name": "New York Post", "url": "https://nypost.com/2026/06/12/world-news/us-disables-third-oil-tanker-trying-to-break-through-blockade-on-iran-ports/"},
        {"name": "IANS Live", "url": "https://ianslive.in/news/iran-condemns-us-attack-on-commercial-vessels-that-killed-three-indian-sailors-20260612"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art1_image_url,
    "image_caption": "An oil tanker at sea — Indian-crewed vessels have been repeatedly struck by U.S. forces off the coast of Oman",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ── Article 2 ──────────────────────────────────────────────────
art2_id = str(uuid.uuid4())
art2_slug = make_slug("silicon-valley-indian-americans-fbi-doj-hindu-temple-hate-crimes")

art2_image_url = ""
if img2_bytes:
    try:
        art2_image_url = upload_to_supabase(img2_bytes, f"{art2_id}.jpg")
        print(f"  ✅ Article 2 image uploaded: {art2_image_url[:60]}...")
    except Exception as e:
        print(f"  ⚠ Article 2 upload failed: {e}")

art2_body = """Two dozen of Silicon Valley's most prominent Indian Americans walked into a room with the FBI, the Department of Justice, and police chiefs from four Bay Area cities this week. The subject was not a business deal or a policy briefing. It was fear.

A string of attacks on Hindu and Jain temples across the Bay Area — defacements, thefts, pro-Khalistan graffiti scrawled on sacred walls — has rattled a community that, for all its wealth and professional stature, suddenly finds its places of worship treated as soft targets.

The meeting, organized by community leader Ajai Jain Bhutoria, brought together officials from the DOJ's Community Relations Service — including Vincent Plair and Harpreet Singh Mokha — alongside representatives from the FBI and police departments in San Francisco, Milpitas, Fremont, and Newark.

## A pattern, not an incident

The latest flashpoints tell a familiar story. The BAPS Shri Swaminarayan Mandir in Newark, one of the Bay Area's largest Hindu temples, was defaced with anti-India and pro-Khalistan graffiti. Weeks later, a copycat attack hit the Vijay's Sherawali Temple in Hayward, this time with identical pro-Khalistan messaging. In between, the Shiv Durga temple in the same area was robbed.

The Hindu American Foundation, which has been coordinating with temple leaders and police, has urged congregations to install security cameras and alarm systems. "Another Bay Area Hindu temple attacked with pro-Khalistan graffiti," HAF said in a post on X. "HAF is in touch with temple leaders and in contact with the police."

Newark police called the Swaminarayan temple incident a "targeted act" and opened a hate crime investigation. "We're deeply saddened when these types of acts occur, and we think they're senseless and they have no room," said Captain Jonathan Arguello.

## 'US soil is being used for terrorist activities'

At the Silicon Valley meeting, the mood was sharper than any press statement. Attendees told federal officials bluntly that American soil was being used to promote what they described as terrorist activities against India. The community's frustration, according to multiple people present, centred on a perceived gap between the severity of the attacks and the pace of law enforcement's response.

India's External Affairs Minister S. Jaishankar weighed in from Delhi. "Extremists and separatist forces outside India should not get space," he said. "Our consulate has lodged a complaint with the government and the police there."

The U.S. State Department's Bureau of South and Central Asian Affairs condemned the Swaminarayan temple vandalism directly on X, welcoming "efforts by the Newark Police Department to ensure that those responsible are held accountable."

## A community that pays its dues

The anxiety sits oddly against the community's outsize contribution to American life. Indian Americans are the highest-income ethnic group in the United States, pay an estimated five to six percent of all federal income taxes, and have co-founded 72 American unicorns valued at a combined $195 billion. Sixteen Indian-origin CEOs run Fortune 500 companies, collectively employing 2.7 million Americans.

None of which, apparently, inoculates a temple wall against a can of spray paint.

The Coalition of Hindus of North America has called the pattern a manifestation of growing "Hinduphobia" in the region. "Freedom of religion means little when sacred spaces that are meant to be an oasis of peace and calm are vandalised with no consequences," CoHNA said. "We are sad but not shocked — authorities, media and other groups have regularly downplayed or ignored the growing Hinduphobia in the region."

## What the community wants

The ask from the Silicon Valley meeting was concrete: faster investigation timelines, federal-level coordination when incidents cross jurisdictions, and recognition that the attacks are not isolated vandalism but part of a wider ideological campaign targeting Hindu and Indian-American institutions on American soil.

Whether those asks translate into action remains to be seen. Bhutoria and other attendees left the meeting with assurances but no announcements. In the meantime, temples across the Bay Area are budgeting for security cameras they never thought they would need, and community leaders are scheduling the next round of conversations with law enforcement.

For a diaspora that has always measured its American success story in degrees earned, companies built, and taxes paid, the new metric is more primal: whether the temple down the street will still look the same tomorrow morning."""

art2 = {
    "id": art2_id,
    "headline": "Silicon Valley's Indian Americans Take Their Case to the FBI as Hindu Temple Attacks Spread Across the Bay Area",
    "subheadline": "A group of prominent Indian Americans held an extraordinary meeting with federal officials and four police departments this week, demanding faster action on a wave of anti-Hindu vandalism and theft targeting Bay Area temples.",
    "slug": art2_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The Bay Area's Indian-American community — among the wealthiest and most professionally accomplished in the country — confronts the unsettling reality that its sacred spaces are being targeted, forcing community leaders into unfamiliar territory as security advocates.",
    "tags": ["nri", "diaspora", "hate-crimes", "hindu-temple", "bay-area", "silicon-valley", "community-safety"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/group-of-indian-americans-meet-senior-officials-to-address-hate-crimes-against-hindus/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/alarm-bells-as-hate-speech-and-crimes-against-hindus-on-the-rise-across-us-and-canada/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/hindu-temple-defaced-with-anti-india-graffiti/"},
        {"name": "Indiaspora Report via The Indian Eye", "url": "https://theindianeye.com/small-community-big-contributions-as-indian-americans-pay-about-5-6-of-all-income-taxes-in-the-us/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art2_image_url,
    "image_caption": "A Hindu temple in Sunnyvale, California — Bay Area temples have faced a wave of vandalism and hate-motivated attacks",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ── Insert articles ──────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
