#!/usr/bin/env python3
"""Videshi News Writer — 2026-05-31 evening batch"""

import json, os, uuid, re, sys, time
from datetime import datetime, timezone

import requests

# ── Supabase credentials ──
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                val = val.strip().strip('"').strip("'")
                os.environ.setdefault(key.strip(), val)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ.get('SUPABASE_URL', '')
SB_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SB_KEY,
    'Authorization': f'Bearer {SB_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

# ── Image sourcing helpers ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    headers = {"Authorization": PEXELS_KEY}
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                f"https://api.pexels.com/v1/search?query={q}&per_page=5&orientation=landscape",
                headers=headers, timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get('photos', [])
                for p in photos:
                    url = p.get('src', {}).get('large2x') or p.get('src', {}).get('large')
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate that an image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Retry with GET for servers that don't support HEAD properly
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct:
            # Read a chunk to verify size
            data = b''
            for chunk in r.iter_content(8192):
                data += chunk
                if len(data) > 5000:
                    return True
            return len(data) > 5000
    except:
        pass
    return False


def sb_insert(table, payload):
    """Insert a row into Supabase and return the response."""
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        print(f"  ✓ Inserted into {table}")
        return data[0] if isinstance(data, list) and data else data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None


# ── Articles ──

articles = []

# ─── Article 1: UC Berkeley heatwave mortality study ───

art1_slug = "india-heatwave-3400-excess-deaths-per-day-uc-berkeley-study-frontiers-20260531"
art1_headline = "A Single Day of Extreme Heat Kills 3,400 People Across India. A UC Berkeley Study Just Mapped Exactly Where."
art1_subheadline = "The first district-level mortality estimates for Indian heatwaves reveal that Uttar Pradesh alone loses 8,100 people in a five-day event. The researchers are Indian Americans at UC Berkeley."
art1_body = """India's heatwaves kill far more people than the official numbers suggest — and a new study by two Indian American researchers at the University of California, Berkeley has produced the most detailed map yet of where and how many.

Published in the journal *Frontiers in Environmental Health*, the study estimates that a single day of extreme heat causes approximately 3,400 excess deaths across India. A five-day heatwave — the kind that has become routine every pre-monsoon season — kills nearly 30,000.

The researchers, Piyush Narang and Ashok Gadgil of Berkeley's India Energy and Climate Center, adapted findings from a multi-city epidemiological analysis of heat-related mortality across 10 Indian cities and projected them onto every district in the country. They integrated district-level mortality rates from the Civil Registration System with 2024 population projections to build a granular picture that had never existed before in peer-reviewed literature.

## The Worst-Hit Districts

The numbers are staggering. Uttar Pradesh alone accounts for roughly 8,100 excess deaths during a five-day heatwave — more than any other state. Individual districts like Ahmedabad, Jaipur, and Surat each exceed 250 excess deaths in a single heat event.

"Excess deaths" is a public health metric that captures the gap between actual deaths during a heatwave and the number that would be expected based on historical baselines. India's official heatwave death toll — typically reported as a few hundred per year — has long been criticized as a dramatic undercount because most heat deaths are recorded as cardiac arrest, kidney failure, or dehydration rather than heat exposure.

## Why This Matters for the Diaspora

The study arrives at a moment of acute crisis. Over the past week, heatwave to severe heatwave conditions have persisted across northern, central, and eastern India, with temperatures consistently exceeding 45°C (113°F) in Madhya Pradesh, Rajasthan, parts of Uttar Pradesh, and Haryana. In Andhra Pradesh and Telangana, more than 100 people died within three days during a particularly intense May heatwave, according to reports in the Khaleej Times.

For the Indian diaspora, these numbers carry personal weight. Many NRIs have elderly parents and extended family in precisely the districts this study identifies as most vulnerable — the Gangetic plains, western Rajasthan, and the Deccan plateau. The study's district-level granularity means families can now see, for the first time, the specific mortality risk in their home district during a heatwave.

## Climate Change Is Making It Worse

The World Weather Attribution group estimated that the first major heatwave of 2026 — from April 15 to 29 — was made about three times more likely and roughly 1°C hotter due to climate change. At current global warming levels of approximately 1.4°C, the subcontinent can expect similar events about once every five years. If warming reaches 2.6°C by 2100, such heatwaves would hit every two to three years and be 2.2°C more intense.

India's India Meteorological Department (IMD) has projected that June temperatures will remain above seasonal averages across much of southern, western, central, and northern India. The 2026 monsoon is forecast to be the weakest in 11 years, further extending the heat season.

## A Call for Localized Action

The researchers argue that their findings demand a fundamental shift in how India designs its heat resilience architecture. "The results have direct and urgent implications," they write. The top 100 districts — comprising nearly one-third of India's population — accounted for 44 percent of all excess deaths projected for a five-day heatwave.

Most of India's heat action plans are city-level. This study suggests they need to be extended to every high-risk district, with localized early-warning systems, cooling shelters, and targeted healthcare infrastructure.

For a country that records over 5,000 heatwave hours per season and where hundreds of millions of people work outdoors, the stakes could not be higher. The question is whether the data will drive the response before the next wave hits.

*Sources: Frontiers in Environmental Health (Narang & Gadgil, 2026); Carbon Brief DeBriefed, May 29, 2026; World Weather Attribution; India Meteorological Department*"""

articles.append({
    "slug": art1_slug,
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "category": "news",
    "image_search_person": None,
    "image_search_pexels": "India extreme heat sun scorching",
    "image_search_pexels_fallback": "heatwave India summer",
    "image_attribution": "The Videshi",
    "sources": json.dumps(["Frontiers in Environmental Health", "Carbon Brief", "World Weather Attribution", "India Meteorological Department"]),
})


# ─── Article 2: India-Australia Defence Ministers Dialogue ───

art2_slug = "rajnath-singh-richard-marles-india-australia-defence-ministers-dialogue-june-2026"
art2_headline = "India and Australia Will Sit Down for Their Second Defence Ministers' Dialogue on Monday. Co-Production Is on the Table."
art2_subheadline = "Rajnath Singh and Richard Marles will discuss co-development of defence equipment, military interoperability, and Indo-Pacific stability — six months after the inaugural dialogue in Australia."
art2_body = """Defence Minister Rajnath Singh and Australian Deputy Prime Minister and Defence Minister Richard Marles will co-chair the second India-Australia Defence Ministers' Dialogue in New Delhi on Monday, June 1, with discussions centered on co-development, co-production, and military interoperability.

The meeting, announced by India's Ministry of Defence on Sunday, follows the inaugural dialogue held in Australia in October 2025 and reflects a partnership that has matured with striking speed since the two countries elevated their relationship to a Comprehensive Strategic Partnership.

## What Is on the Agenda

The two ministers will review progress on bilateral defence cooperation and identify new avenues for collaboration. According to the Ministry of Defence, the discussions will focus on four areas: strengthening defence and security cooperation, enhancing military interoperability, industry collaboration — including co-development and co-production opportunities — and regional and global security developments of mutual interest.

The co-production angle is particularly significant. India has been aggressively pursuing defence manufacturing partnerships under its Make in India initiative, and Australia — which is itself undergoing a major defence recapitalization as part of the AUKUS framework — represents a natural partner for high-end industrial collaboration. Both countries are net importers of defence equipment and share an interest in diversifying their supply chains away from single-source dependencies.

## The Indo-Pacific Context

The timing is deliberate. The dialogue takes place against the backdrop of the Shangri-La Dialogue in Singapore, where India's Defence Secretary Rajesh Kumar Singh spent the weekend holding bilateral meetings with counterparts from New Zealand, Singapore, Sweden, and the Netherlands. At the same forum, US Defence Secretary Pete Hegseth described India as a "critical anchor" in the Indo-Pacific and announced Javelin anti-tank missile co-production.

The broader strategic picture has sharpened considerably. China notably downgraded its Shangri-La delegation this year, sending no defence minister for the first time since 2021 — a move that diplomats at the forum interpreted as an attempt to avoid tough questions about Beijing's military buildup and recent corruption purges in the People's Liberation Army.

India, by contrast, has been running a full-court diplomatic press. Over the past week, New Delhi has hosted the Quad Foreign Ministers, the BRICS Foreign Ministers, and Myanmar's new president — while its defence secretary was simultaneously working the floor in Singapore.

## Why It Matters for the Diaspora

For the roughly 800,000 people of Indian origin in Australia — one of the fastest-growing diaspora communities in the world — the deepening defence relationship carries practical implications. Stronger government-to-government ties tend to accelerate people-to-people cooperation, including student exchanges, research partnerships, and visa facilitation. Australia is already the third-largest destination for Indian international students, after the US and Canada.

The defence industrial collaboration also creates potential opportunities for Indian-origin engineers and defence technology professionals in both countries. As both nations build out their domestic defence manufacturing bases, the workforce requirements will grow — and Indian technical talent is well-positioned to fill gaps on both sides.

## The Broader Pattern

The India-Australia defence relationship has moved further in the past three years than it did in the previous three decades. Joint exercises have expanded, intelligence-sharing agreements have deepened, and logistics pacts have been operationalized. The second Defence Ministers' Dialogue is not a standalone event — it is the latest node in a network of institutional mechanisms that now binds the two countries at multiple levels.

"The visit underscores the growing depth and maturity of the India-Australia defence partnership," the Ministry of Defence said in its statement. Australia's defence ministry echoed the sentiment, calling it "unprecedented progress."

The real test of the relationship will come when co-development projects move from memoranda of understanding to production lines. Monday's dialogue will signal whether that transition is beginning.

*Sources: Ministry of Defence (India); Australian Department of Defence; IANS, May 31, 2026; Reuters*"""

articles.append({
    "slug": art2_slug,
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "category": "news",
    "image_search_person": "Rajnath Singh",
    "image_search_pexels": "India Australia defence military",
    "image_search_pexels_fallback": "India defence minister meeting",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps(["Ministry of Defence (India)", "Australian Department of Defence", "IANS", "Reuters"]),
})


# ─── Article 3: China downgrades Shangri-La delegation ───

art3_slug = "china-downgrades-shangri-la-dialogue-delegation-no-defence-minister-india-deepens-ties-20260531"
art3_headline = "China Sent No Defence Minister to the Shangri-La Dialogue This Year. Everyone at the Forum Noticed."
art3_subheadline = "For the first time since 2021, Beijing downgraded its delegation to researchers and mid-level officials — while India, the US, and Australia used the forum to announce new defence partnerships."
art3_body = """At the Shangri-La Dialogue in Singapore this weekend, the biggest story was not what happened in the conference rooms but who was missing from them.

China sent no defence minister to the 23-year-old forum this year — the first time since 2021 it has declined to send a ministerial-level representative. Instead, Beijing dispatched a delegation heavy on researchers and mid-level officials, a downgrade that diplomats, academics, and defence officials at the event described as conspicuous and deliberate.

"Where is China?" became the unofficial refrain of the weekend, according to Reuters.

## Why Beijing Stayed Away

The reasons are layered. Diplomats at the forum suggested Beijing wanted to avoid a repeat of last year's dialogue, when US Defence Secretary Pete Hegseth described China as a threat in the Indo-Pacific and urged Asian allies to boost defence spending. China responded at the time by accusing the United States of vilification.

But the absence may also reflect internal turbulence. China's military has been rocked by a series of anti-corruption purges that have removed senior officers across the People's Liberation Army, the Rocket Force, and the defence procurement apparatus. Sending a minister to Singapore to field questions about military readiness and internal discipline — in front of defence chiefs from 40 countries — may have been a risk Beijing chose not to take.

Chong Ja Ian, a political scientist at the National University of Singapore, told Reuters that the research-heavy delegation raised questions about "representativeness and authoritativeness." In other words: the people China sent may not have had the authority to say anything meaningful.

## The Vacuum India and the US Filled

China's retreat left a vacuum that India and the United States moved aggressively to fill.

India's Defence Secretary Rajesh Kumar Singh spent the weekend conducting bilateral meetings with counterparts from Singapore, New Zealand, Sweden, and the Netherlands. On Friday, he addressed leading think tanks on "India's Defence Diplomacy for a Stable, Secure and Inclusive Indo-Pacific," laying out New Delhi's vision for regional security. On Sunday, Defence Minister Rajnath Singh announced the second India-Australia Defence Ministers' Dialogue, to be held in New Delhi on Monday.

Hegseth struck a more measured tone than last year but still cautioned that "no state, including China, can impose its hegemony and hold the security or prosperity of our nation and our allies in question." He added that US-China relations were "better than they had been in many years" — a diplomatic half-step that acknowledged Beijing's sensitivity while maintaining the underlying message.

The Pentagon also used the forum's margins to announce Javelin anti-tank missile co-production with India, calling New Delhi a "critical anchor" in the Indo-Pacific. India separately signed an undersea-domain awareness partnership with Japan and held logistics talks with the Philippines.

## The Strategic Signal

Veteran Singapore diplomat Bilahari Kausikan offered a characteristically blunt assessment. The Shangri-La Dialogue, he said, was always primarily about "anchoring the U.S. in Southeast Asia" and ensuring its defence chief comes to Singapore at least once a year. "Whether China is represented by its defence minister is a secondary factor. It would be nice but not essential."

But for Southeast Asian nations caught between the two powers, China's absence carries a different kind of message. The forum is one of the few multilateral settings where smaller countries can engage directly with major-power defence officials. When one of the two largest military powers in the world chooses not to send a minister, it signals either disengagement or a willingness to cede diplomatic space — neither of which is reassuring to countries navigating the increasingly charged waters of the South China Sea, the Taiwan Strait, and the Indian Ocean.

## What It Means for the Diaspora

For the Indian diaspora, the Shangri-La Dialogue matters because the Indo-Pacific framework is not abstract geopolitics — it is the architecture within which India's trade routes, energy supplies, and strategic partnerships are being built. India's growing prominence at forums like this one reflects a diplomatic confidence that has a direct bearing on everything from US visa policy to defence technology transfers to the business environment for Indian companies abroad.

The contrast this weekend was stark: China retreating from a marquee multilateral event while India's diplomatic and defence establishment operated at full tempo across Singapore, New Delhi, and multiple capital cities simultaneously. That is a shift that will be studied in foreign ministries from Washington to Canberra to Jakarta.

*Sources: Reuters; IANS, May 31, 2026; Ministry of Defence (India); Devdiscourse*"""

articles.append({
    "slug": art3_slug,
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "category": "news",
    "image_search_person": None,
    "image_search_pexels": "Singapore Shangri-La dialogue defence",
    "image_search_pexels_fallback": "international defence forum diplomacy",
    "image_attribution": "The Videshi",
    "sources": json.dumps(["Reuters", "IANS", "Ministry of Defence (India)", "Devdiscourse"]),
})


# ── Publish loop ──

now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"Article {i}: {art['headline'][:60]}...")
    print(f"{'='*60}")

    # Image sourcing
    img_url = None
    img_attr = art.get("image_attribution", "The Videshi")

    # 1. Try Wikipedia for person articles
    if art.get("image_search_person"):
        img_url = fetch_wikipedia_person_image(art["image_search_person"])
        if img_url:
            img_attr = "Wikimedia Commons"

    # 2. Fallback to Pexels
    if not img_url:
        img_url = fetch_pexels_image(
            art.get("image_search_pexels", ""),
            art.get("image_search_pexels_fallback")
        )
        img_attr = "The Videshi"

    # 3. Validate
    if img_url and not validate_image_url(img_url):
        print(f"  ⚠ Image validation failed, dropping: {img_url[:60]}")
        img_url = None

    if not img_url:
        print("  ⚠ No valid image found — publishing without image")

    # Count words
    word_count = len(art["body"].split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ✗ BELOW 400-word floor — skipping")
        continue

    # Build payload
    article_id = str(uuid.uuid4())
    payload = {
        "id": article_id,
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "body": art["body"],
        "slug": art["slug"],
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": now_iso,
        "sources": json.loads(art["sources"]),
        "is_editorial": False,
        "image_attribution": img_attr,
    }
    if img_url:
        payload["image_url"] = img_url

    result = sb_insert("p2_articles", payload)
    if result:
        print(f"  ✓ Published: {art['slug']}")
        print(f"  ID: {article_id}")
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")

    time.sleep(1)

print("\n✅ News writer batch complete.")
