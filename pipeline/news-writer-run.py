#!/usr/bin/env python3
"""News writer run — 2026-06-02"""

import json, os, re, sys, time, uuid, urllib.parse, subprocess
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import requests

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                img_url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image for '{q}': {img_url[:80]}...")
                return img_url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct:
            if cl > 5000 or cl == 0:  # Accept 0 content-length (HEAD may not return it)
                print(f"  ✓ Image OK: {r.status_code}, {ct}, {cl} bytes")
                return True
        print(f"  ✗ Image fail: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image error: {e}")
    return False

def make_sources(source_list):
    """Convert source name list to the format Supabase expects."""
    return [{"name": s, "url": ""} for s in source_list]

def sb_insert(article):
    """Insert article into Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=headers,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0].get('id')
        return True
    else:
        print(f"  ✗ Insert failed: {r.status_code} — {r.text[:500]}")
        return None


# ============================================================
# ARTICLE 1: India-Australia Defence Ministers' Dialogue
# ============================================================
print("\n=== Article 1: India-Australia Defence Ministers' Dialogue ===")

art1_body = """India and Australia have agreed to jointly track maritime activity across the Indian and Pacific Oceans, putting teeth behind a defence partnership that has moved from ceremonial to operational in less than two years.

Defence Minister Rajnath Singh and Australia's Deputy Prime Minister and Defence Minister Richard Marles co-chaired the second India-Australia Defence Ministers' Dialogue at the Manekshaw Centre in New Delhi on June 1. The first had been held in Canberra just eight months earlier, in October 2025. The pace alone signals urgency.

## A Maritime Roadmap Takes Shape

The centrepiece of the meeting was a Joint Maritime Security Collaboration Roadmap — a document that, once finalised, will formalise shared patrols, surveillance flights, and intelligence exchange across the Indian Ocean Region.

Both sides agreed to accelerate maritime domain awareness activities using their respective long-range maritime patrol aircraft. India and Australia will also begin exploring undersea domain awareness cooperation — a capability area that until recently was reserved for the most intimate of defence partnerships.

The Indian Coast Guard and Australia's Maritime Border Command, the two agencies responsible for day-to-day maritime enforcement, will deepen direct engagement. Later this month, the two countries will co-host a Search and Rescue exercise and tabletop drill in Chennai under the auspices of the Indian Ocean Rim Association's Working Group on Maritime Safety and Security.

## A New MoU on Defence Equipment

Beyond the maritime domain, the ministers announced work on a new Memorandum of Understanding covering the supply of defence equipment and services. The MoU opens the door for co-development and co-production — an area India has been pushing aggressively as it tries to become a net defence exporter rather than the world's largest importer.

Joint research in sensor systems and other emerging technologies will be pursued through existing bilateral defence science mechanisms. Australia has invited India to participate in its Defence Science, Technology and Research Summit later in 2026.

## Military Exercises Expand

India is expected to increase its participation in Exercise Talisman Sabre 2027, Australia's flagship multinational military exercise. Both countries will continue to train together through Malabar, Tarang Shakti, and several navy-to-navy engagements.

The scope of cooperation has quietly expanded into areas that would have been unthinkable a decade ago: amphibious warfare, littoral operations, submarine rescue, and multinational humanitarian missions.

An Indian military instructor will be placed at the Australian Defence College during 2028-29 — a small but symbolically significant step toward building institutional memory between two armed forces that spent most of the Cold War on opposite sides of strategic alignment.

## The Quad in the Background

Neither minister used the word "alliance." But the joint statement underscored growing strategic alignment among Quad partners — India, Australia, Japan, and the United States — on maritime surveillance and information sharing.

The India-Australia defence relationship is no longer aspirational. It is being built, exercise by exercise, patrol by patrol, and MoU by MoU. The Chennai drill this month will be the next test of whether operational ambition can keep pace with diplomatic intent.

*Sources: Ministry of Defence press statement, IANS, Australian Defence Ministry statement*"""

# Image
art1_img = fetch_wikipedia_person_image("Rajnath Singh")
if not art1_img or not validate_image(art1_img):
    art1_img = fetch_pexels_image("naval warship ocean military", "navy destroyer Indian Ocean")
    if art1_img and not validate_image(art1_img):
        art1_img = None

art1 = {
    "headline": "India and Australia Just Agreed to Map Each Other's Oceans. A Joint Rescue Drill in Chennai Will Start This Month.",
    "subheadline": "At their second Defence Ministers' Dialogue in New Delhi, Rajnath Singh and Richard Marles signed off on a maritime roadmap, a new defence equipment MoU, and deeper undersea surveillance cooperation.",
    "slug": "india-australia-2nd-defence-ministers-dialogue-rajnath-singh-marles-maritime-roadmap-20260602",
    "body": art1_body,
    "category": "news",
    "vertical": "geopolitics",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": art1_img,
    "image_attribution": "Wikimedia Commons" if art1_img and "wikimedia" in (art1_img or "") else ("Pexels" if art1_img else None),
    "is_editorial": False,
    "score_total": 0,
    "sources": make_sources([
        "Ministry of Defence, Government of India",
        "IANS",
        "Australian Defence Ministry",
        "Impressive Times"
    ])
}
art1_id = sb_insert(art1)
print(f"  → Article 1: {art1_id}")


# ============================================================
# ARTICLE 2: Indo-Pacific Defence Realignment
# ============================================================
print("\n=== Article 2: Indo-Pacific Defence Realignment ===")

art2_body = """The 2026 Shangri-La Dialogue ended on Sunday with a message that was unmistakable, even if no one said it plainly: the era of waiting for Washington is over.

At Asia's premier annual defence summit in Singapore, the theme that emerged was not a specific flashpoint — not Taiwan, not the Strait of Hormuz, not the South China Sea — but a structural shift. Indo-Pacific nations are arming themselves, and they are arming each other, at a pace that has no precedent since the Cold War.

## The US Says Two Things at Once

US Defense Secretary Pete Hegseth arrived in Singapore to reassure Asian allies that Washington's attention had not drifted despite the three-month-old war with Iran. "We can do two things at one time," he told the forum.

But he also pressed partners to spend more. His target: 3.5 percent of GDP on defence — a number that would represent a massive increase for most Asian nations. He praised Asian partners for outperforming their European counterparts and took a direct shot at NATO, saying Western Europe "might take note."

The mixed message — we are here, but you should be ready in case we are not — was heard clearly.

## Japan Steps Into the Centre

Japan's Defence Minister Shinjiro Koizumi said he believed the US commitment was "unwavering." But his actions told a different story. Tokyo is positioning itself as a "connecting point" for closer regional cooperation, moving beyond its traditional US-anchored posture.

In April, Japan unveiled its biggest overhaul of defence export rules in decades, scrapping restrictions on overseas arms sales and opening the door to export warships, missiles, and other weapons. At Shangri-La, Koizumi met bilaterally with counterparts from across the region, laying the groundwork for a web of partnerships that does not require Washington at the centre of every strand.

## The Philippines, New Zealand, and the Five Powers

The Philippines' Defence Secretary Gilberto Teodoro was blunt. Manila is deepening ties with Japan, Australia, Canada, and New Zealand — "buttressing" the US role, he said, not replacing it. "The commitment of the United States becomes more solid when more actors come in."

New Zealand, meanwhile, is weighing Japanese and British warships to replace its ageing ANZAC-class frigates. Defence Minister Chris Penk said the Five Power Defence Arrangement — a 54-year-old pact linking New Zealand, Australia, Singapore, Malaysia, and the UK — was being pursued "at a more intense level."

## India: Defence Exports and Strategic Autonomy

India entered the Shangri-La Dialogue with its own headline: a BrahMos missile deal with Vietnam, its third Southeast Asian customer. Hegseth called India a "critical anchor" in South Asia.

But India's position is distinct from the broader hedging pattern. New Delhi is not joining a bloc. It is building a defence export portfolio — the BrahMos sales to the Philippines, Indonesia, and now Vietnam represent a deliberate strategy to become a provider of security goods, not just a consumer.

Defence Secretary Rajesh Kumar Singh held bilateral meetings with counterparts from Singapore, Sweden, the Netherlands, Australia, New Zealand, and the European Union on the sidelines. Each meeting expanded a different thread of India's growing defence network.

## AUKUS Goes Aquatic

The AUKUS triad — Australia, the UK, and the US — unveiled a joint plan to develop aquatic drones for tasks like subsea cable defence. The initiative appears to be a response to threats exposed by the Iran-US war, where disruption of undersea infrastructure became a real risk. AUKUS had originally focused on submarine power projection in the Pacific; the pivot toward undersea infrastructure protection suggests a broader mandate.

## The Takeaway

Singapore's Defence Minister Chan Chun Sing captured the moment best: nations should "develop flexible partnerships with like-minded countries forming coalitions of the able and willing."

The Shangri-La Dialogue has always been a place where speeches matter less than sideline conversations. This year, the conversations all pointed in the same direction. The Indo-Pacific's security architecture is being rebuilt — not around a single superpower, but around a mesh of partnerships that can hold even if one node weakens.

For India, the question is whether strategic autonomy can coexist with this new mesh. For now, the answer appears to be yes — as long as New Delhi keeps building things other countries want to buy.

*Sources: Reuters, Livemint, IISS Shangri-La Dialogue, ANI*"""

art2_img = fetch_pexels_image("military naval fleet ships formation", "defense summit meeting international")
if art2_img and not validate_image(art2_img):
    art2_img = None

art2 = {
    "headline": "Every Country at the Shangri-La Dialogue Had the Same Message. Arm Yourself. And Find Partners Who Will Arm With You.",
    "subheadline": "Asia's premier defence summit ended with a clear takeaway: Indo-Pacific nations are racing to deepen security ties with each other — not because the US is leaving, but because they are no longer sure it will stay.",
    "slug": "shangri-la-dialogue-2026-indo-pacific-defence-hedging-japan-india-philippines-aukus-20260602",
    "body": art2_body,
    "category": "news",
    "vertical": "geopolitics",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": art2_img,
    "image_attribution": "Pexels" if art2_img else None,
    "is_editorial": False,
    "score_total": 0,
    "sources": make_sources([
        "Reuters",
        "Livemint",
        "IISS Shangri-La Dialogue",
        "ANI",
        "Ministry of Defence, Government of India"
    ])
}
art2_id = sb_insert(art2)
print(f"  → Article 2: {art2_id}")


# ============================================================
# ARTICLE 3: Lebanon Partial Ceasefire
# ============================================================
print("\n=== Article 3: Lebanon Partial Ceasefire ===")

art3_body = """Lebanon announced a partial ceasefire between Israel and Hezbollah on Monday — and almost immediately, the fighting continued.

The arrangement, brokered with US involvement and announced by Lebanon's embassy in Washington, calls on Israel to refrain from airstrikes on Beirut and its Hezbollah-controlled suburbs. In return, Hezbollah would halt its rocket and drone attacks on Israeli territory.

It is, by any measure, a limited deal. It does not cover southern Lebanon, where Israeli ground forces are pushing deeper than at any point in 25 years, toward the Zaharani River. It does not address Gaza. And it does not resolve the larger US-Iran war that ignited in March.

## What Trump Claimed

US President Donald Trump announced the deal before Lebanon did, saying he had spoken to Israeli Prime Minister Benjamin Netanyahu and, through intermediaries, to Hezbollah. No US president has ever communicated with Hezbollah — a designated terrorist organisation — making the claim itself historically significant.

Netanyahu, however, pushed back almost immediately. Israel would continue military operations in southern Lebanon, he said. "If Hezbollah does not cease attacking our cities and citizens — Israel will attack terror targets in Beirut," his office stated.

Hezbollah lawmaker Hassan Fadlallah said the militia would support a full ceasefire across all Lebanon as a precursor to the withdrawal of Israeli troops. He did not say whether the group would stop its strikes on Israeli territory.

## Iran Says No Separate Peace

Hours before the ceasefire announcement, Iranian state media reported that Tehran was suspending indirect peace negotiations with the US, citing the war in Lebanon. The head of Iran's Revolutionary Guards Quds Force, Esmaeil Qaani, threatened to expand Iran's blockade of the Strait of Hormuz to the Bab el-Mandeb Strait — the chokepoint at the mouth of the Red Sea that controls access to the Suez Canal.

Iranian Foreign Minister Abbas Araqchi was unambiguous: "The ceasefire between Iran and the US is unequivocally a ceasefire on all fronts, including in Lebanon. Its violation on one front is a violation of the ceasefire on all fronts."

Iran has already severely disrupted maritime traffic through the Gulf, which before the war supplied one-fifth of the world's oil and liquefied natural gas. Oil prices rose 4 percent on Monday.

## What This Means for India

India is watching from multiple angles. It is the world's third-largest oil importer, and the Strait of Hormuz has been a lifeline for its energy security for decades. A Bab el-Mandeb blockade would compound the disruption, threatening Indian exports that transit the Red Sea and Suez Canal.

India has already pivoted its oil imports toward Venezuela, Brazil, and Angola to reduce its dependence on Gulf crude. But there is no substitute for stable shipping lanes. Every week the Hormuz disruption continues, India's forex reserves take a hit — they have already fallen $47 billion in three months as the RBI defends the rupee.

The partial ceasefire offers a sliver of hope that the broader US-Iran war could be contained. But Monday's events suggest the path to de-escalation runs through Tehran, not Beirut — and Tehran has just walked away from the table.

## The Numbers

The conflict in Lebanon has killed 3,433 people and displaced more than one million. At least 26 Israeli soldiers and two civilians have been killed. Hezbollah's use of fibre-optic drones — difficult to detect and intercept — has been particularly deadly for the Israeli military.

A UN Security Council emergency meeting on Lebanon was scheduled for Monday afternoon. Lebanon said it would seek to expand the ceasefire in talks with Israel in Washington on Wednesday.

*Sources: Reuters, Associated Press, NPR, Tasnim News Agency*"""

art3_img = fetch_pexels_image("beirut lebanon city skyline", "mediterranean city coast")
if art3_img and not validate_image(art3_img):
    art3_img = None

art3 = {
    "headline": "Lebanon Just Announced a Partial Ceasefire Between Israel and Hezbollah. Nobody Has Stopped Fighting.",
    "subheadline": "The deal calls on Israel to spare Beirut while Hezbollah halts attacks on Israel. Southern Lebanon remains a war zone. Iran says there is no separate peace — any ceasefire must cover all fronts.",
    "slug": "lebanon-partial-ceasefire-hezbollah-israel-trump-iran-war-oil-india-impact-20260602",
    "body": art3_body,
    "category": "news",
    "vertical": "geopolitics",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": art3_img,
    "image_attribution": "Pexels" if art3_img else None,
    "is_editorial": False,
    "score_total": 0,
    "sources": make_sources([
        "Reuters",
        "Associated Press",
        "NPR",
        "Tasnim News Agency"
    ])
}
art3_id = sb_insert(art3)
print(f"  → Article 3: {art3_id}")


# ============================================================
# Summary
# ============================================================
print("\n=== Summary ===")
results = [
    ("India-Australia Defence Dialogue", art1_id, bool(art1_img)),
    ("Indo-Pacific Defence Hedging", art2_id, bool(art2_img)),
    ("Lebanon Partial Ceasefire", art3_id, bool(art3_img)),
]
for name, aid, has_img in results:
    status = "✓" if aid else "✗"
    img_status = "🖼️" if has_img else "⚠️ no image"
    print(f"  {status} {name} ({img_status})")

success = sum(1 for _, aid, _ in results if aid)
print(f"\n{success}/{len(results)} articles published.")
