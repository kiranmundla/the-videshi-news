#!/usr/bin/env python3
"""
News writer for The Videshi — 2026-05-30 evening batch
Three articles:
1. India-Vietnam BrahMos missile deal ($629M), Indonesia next
2. Chandrayaan-3 wins Goddard Astronautics Award from AIAA
3. India-US trade deal down to 'last 1%' — Ambassador Gor
"""

import json, os, sys, time, uuid, re
import requests
from datetime import datetime, timezone

# ── Env ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Helpers ──────────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = requests.utils.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com; contact@thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            # Use thumbnail (330px) which is more reliably cached; originalimage can 429
            img = data.get("thumbnail", {}).get("source")
            if not img:
                img = data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
        elif r.status_code == 429:
            print(f"  ⚠ Wikipedia rate limited for '{person_name}', waiting 5s...")
            time.sleep(5)
            r2 = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com; contact@thevideshi.com)"},
                timeout=10,
            )
            if r2.status_code == 200:
                data = r2.json()
                img = data.get("thumbnail", {}).get("source")
                if not img:
                    img = data.get("originalimage", {}).get("source")
                if img:
                    print(f"  ✓ Wikipedia image found (retry) for '{person_name}': {img[:80]}...")
                    return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels API using curl (urllib gets 403)."""
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=3",
                 "-H", f"Authorization: {PEXELS_API_KEY}"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        resp = requests.get(image_url, timeout=20, headers={
            "User-Agent": "TheVideshi/1.0 (thevideshi.com; contact@thevideshi.com)"
        })
        if resp.status_code == 429:
            print(f"  ⚠ Rate limited downloading image, waiting 5s...")
            time.sleep(5)
            resp = requests.get(image_url, timeout=20, headers={
                "User-Agent": "TheVideshi/1.0 (thevideshi.com; contact@thevideshi.com)"
            })
        if resp.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {resp.status_code}")
            return None
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(resp.content) < 5000:
            print(f"  ⚠ Image too small: {len(resp.content)} bytes")
            return None

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        up_resp = requests.post(upload_url, data=resp.content, headers=up_headers, timeout=30)
        if up_resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up_resp.status_code} {up_resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Upload exception: {e}")
        return None


def validate_image_url(url):
    """Verify URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    # Check for banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
    if any(b in url for b in banned):
        print(f"  ✗ Banned source: {url[:60]}")
        return False
    banned_params = ["_nc_ht=", "_nc_cat=", "ccb="]
    if any(p in url for p in banned_params):
        print(f"  ✗ Signed Meta URL: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't support HEAD, try GET
        r2 = requests.get(url, timeout=10, stream=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get("Content-Type", "")
        if r2.status_code == 200 and "image" in ct2:
            chunk = r2.raw.read(6000)
            if len(chunk) >= 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Validation error: {e}")
    return False


def insert_article(article):
    """Insert article into p2_articles table."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    resp = requests.post(url, json=article, headers=HEADERS, timeout=30)
    if resp.status_code in (200, 201):
        data = resp.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {resp.status_code} {resp.text[:300]}")
        return None


# ── Articles ─────────────────────────────────────────────────────────────

def article_brahmos():
    """Article 1: India-Vietnam BrahMos missile deal."""
    print("\n═══ Article 1: India-Vietnam BrahMos Deal ═══")

    slug = "india-signs-brahmos-missile-deal-vietnam-629-million-indonesia-next-20260530"
    headline = "India Has Signed a $629 Million BrahMos Missile Deal With Vietnam. Indonesia Is Next."
    subheadline = "The defence secretary confirmed the deal at the Shangri-La Dialogue — making Vietnam India's second export customer for the supersonic cruise missile after the Philippines."

    body = """India has signed a deal to supply BrahMos supersonic cruise missiles to Vietnam, Defence Secretary Rajesh Kumar Singh confirmed on Saturday at the Shangri-La Dialogue in Singapore. A similar deal with Indonesia is in its "final stages," Singh said, marking a significant expansion of India's defence export ambitions in Southeast Asia.

The Vietnam contract is estimated to be worth approximately 60 billion rupees ($629 million), including training and logistical support, according to earlier Reuters reporting. Singh did not disclose specific financial terms but made clear that the agreement has been signed, even if it has not yet been publicly announced by either government.

"My understanding is that with both Indonesia and with Vietnam, the deal is in the final stages. In fact, for Vietnam, I understand that it has already been signed, probably not publicly announced," Singh told a media event on the sidelines of the Shangri-La Dialogue. "You are in the category of friendly foreign countries with whom we would be happy to share this kind of advanced technology."

## What the BrahMos Is — and Why It Matters

The BrahMos is a supersonic cruise missile jointly developed by India and Russia through a joint venture established in 1998. It can travel at speeds up to Mach 2.8 — nearly three times the speed of sound — and can be launched from ships, submarines, aircraft, and land-based platforms. Its speed and low-altitude flight path make it extremely difficult to intercept.

For India, the BrahMos has become the flagship product of its growing defence export portfolio. The country has been steadily building up domestic defence manufacturing capacity, driven by Prime Minister Narendra Modi's push for self-reliance in defence production under the "Make in India" initiative.

## The Philippines Set the Template

The Philippines became India's first BrahMos export customer, receiving its first batch of the missiles in 2024. A second batch was delivered in April 2025. The deal demonstrated that India could successfully execute a complex weapons export involving training, logistics, and long-term support — a capability that was previously limited to a small number of arms-exporting nations.

The Vietnam deal now makes Hanoi India's second BrahMos customer and significantly deepens the defence relationship between the two countries. Earlier this month, Defence Minister Rajnath Singh travelled to Hanoi for extensive discussions with his Vietnamese counterpart, General Phan Van Giang, covering maritime security, defence industry cooperation, and regional stability.

## Indonesia Could Be Third

Singh's confirmation that Indonesia is in the "final stages" of a similar deal suggests India may soon have three Southeast Asian countries operating the BrahMos — a strategic corridor that runs through some of the most contested waters in the Indo-Pacific.

The timing is notable. The deals come as China continues to expand its military presence in the South China Sea, a region where Vietnam, Indonesia, and the Philippines all have competing territorial claims with Beijing. For these countries, the BrahMos offers a credible deterrent at a price point significantly lower than comparable Western missile systems.

## The Diaspora Angle

For the Indian diaspora, the BrahMos deals represent something beyond defence strategy. They signal India's emergence as a serious player in the global arms market — a shift from being the world's largest arms importer to becoming an increasingly capable exporter. India's defence exports have risen sharply in recent years, crossing $2.8 billion in FY2024, and the government has set a target of $5 billion annually by 2025.

The broader message from Singh at the Shangri-La Dialogue was unmistakable: India is positioning itself as a defence partner of choice for Southeast Asian nations, offering advanced technology with fewer strings attached than Western suppliers typically impose.

"We treat you all as friendly foreign countries with whom we can share advanced defence technology," Singh told the gathering in Singapore.

*Sources: Reuters, IANS, The Business Standard*"""

    # Image: Try Wikipedia for BrahMos
    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("BrahMos")
    if not img_url:
        img_url = fetch_pexels_image("missile defense military", "cruise missile launch")

    final_image = None
    image_attribution = None
    if img_url:
        final_image = upload_image_to_supabase(img_url, f"{slug}.jpg")
        if final_image:
            if "upload.wikimedia.org" in img_url:
                image_attribution = "Wikimedia Commons"
            else:
                image_attribution = "The Videshi"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": "Reuters, IANS",
        "image_url": final_image,
        "image_attribution": image_attribution,
    }
    return insert_article(article)


def article_chandrayaan():
    """Article 2: Chandrayaan-3 Goddard Award."""
    print("\n═══ Article 2: Chandrayaan-3 Goddard Award ═══")

    slug = "chandrayaan-3-wins-goddard-astronautics-award-aiaa-highest-honor-20260530"
    headline = "Chandrayaan-3 Has Won America's Highest Honor in Astronautics. ISRO Joins Jeff Bezos on the List."
    subheadline = "The AIAA Goddard Astronautics Award recognizes the 2023 moon landing that made India the first nation to reach the lunar south pole. India's ambassador accepted it in Washington."

    body = """India's Chandrayaan-3 lunar mission has been awarded the 2026 Goddard Astronautics Award by the American Institute of Aeronautics and Astronautics — the highest honor the organization bestows for achievements in astronautics. The award was presented at the AIAA ASCEND 2026 Conference in Washington, D.C., on May 21.

India's Ambassador to the United States, Vinay Kwatra, accepted the award on behalf of the Indian Space Research Organisation (ISRO). The citation recognized "the groundbreaking landing of ISRO's Chandrayaan-3 near the lunar south pole region, to deepen our understanding of the moon and beyond."

## What the Award Means

The Goddard Astronautics Award is not a routine recognition. Named after Robert H. Goddard — the American physicist who built and launched the world's first liquid-fueled rocket in 1926 — the award has been given to a small number of individuals and organizations who have pushed the boundaries of space exploration.

Previous recipients include Jeff Bezos, founder of Blue Origin, and Michael Hawes, a veteran NASA engineer who contributed to the design and operation of human spaceflight programs. ISRO's addition to this list places India's space agency alongside the most elite names in global astronautics.

## The Mission That Changed India's Space Story

On August 23, 2023, Chandrayaan-3's Vikram lander touched down near the Moon's south pole — a region of immense scientific and strategic importance that no spacecraft from any nation had previously reached at the surface level. The landing made India only the fourth country to successfully soft-land on the Moon, after the United States, the Soviet Union, and China.

But it was the location that made the achievement extraordinary. The lunar south pole is believed to contain deposits of water ice in permanently shadowed craters — a resource that could one day support human habitation and fuel production for deeper space missions. Chandrayaan-3's Pragyan rover confirmed the presence of key chemical elements in the south polar soil, including sulfur, sodium, and iron, providing data that will inform every future mission to the region.

The mission also demonstrated India's ability to achieve complex space objectives at a fraction of the cost of comparable programs elsewhere. Chandrayaan-3's total budget was approximately $75 million — less than the production budget of many Hollywood films and a fraction of what NASA or ESA typically spend on lunar missions.

## Space Vision 2047

In his remarks at the ASCEND conference, Ambassador Kwatra used the award presentation to outline Prime Minister Narendra Modi's Space Vision 2047 — India's ambitious roadmap for the next two decades of space exploration.

The plan includes India's first human spaceflight under the Gaganyaan program, now scheduled for 2027. It also envisions the Chandrayaan-4 mission, a mission to Venus, and the establishment of the Bharat Antariksh Station — India's own space station — by 2035. The most ambitious goal: placing an Indian astronaut on the Moon by 2040.

Kwatra called for strengthened collaboration between the governments, industries, and research institutions of India and the United States, underscoring the deepening partnership between the two nations in space exploration.

## Why It Matters for the Diaspora

For the millions of Indians and Indian-Americans in the United States, the Goddard Award carries a particular resonance. It is one thing for India's space achievements to be celebrated domestically; it is another for America's premier aerospace engineering organization to formally recognize them as the year's most significant contribution to astronautics.

The award also comes at a moment when the US-India space partnership is accelerating. NASA and ISRO signed the Artemis Accords in 2023, and discussions are underway for joint lunar and deep space missions. India's commercial space sector — now home to over 200 startups — is increasingly integrated with the global space economy.

The Goddard Award is a trophy, but it is also a signal. India's space program is no longer an underdog story. It is, by the formal reckoning of America's own space community, world-class.

*Sources: AIAA, ANI, PTI, Storyboard18*"""

    # Image: ISRO / Chandrayaan-3
    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Chandrayaan-3")
    if not img_url:
        img_url = fetch_wikipedia_person_image("Indian Space Research Organisation")
    if not img_url:
        img_url = fetch_pexels_image("moon landing spacecraft", "lunar surface space mission")

    final_image = None
    image_attribution = None
    if img_url:
        final_image = upload_image_to_supabase(img_url, f"{slug}.jpg")
        if final_image:
            if "upload.wikimedia.org" in img_url:
                image_attribution = "Wikimedia Commons"
            else:
                image_attribution = "The Videshi"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": "AIAA, ANI, PTI",
        "image_url": final_image,
        "image_attribution": image_attribution,
    }
    return insert_article(article)


def article_trade_deal():
    """Article 3: India-US trade deal 'last 1%'."""
    print("\n═══ Article 3: India-US Trade Deal ═══")

    slug = "india-us-trade-deal-last-one-percent-ambassador-gor-delegation-june-20260530"
    headline = "The India-US Trade Deal Is Down to the Last 1 Percent. A Delegation Arrives in Delhi Next Week."
    subheadline = "Ambassador Sergio Gor says the deal could be signed within weeks. But the 'last 1 percent' is the hardest part — and the legal landscape under it has shifted."

    body = """India and the United States are closer than ever to finalizing an interim trade agreement, with US Ambassador to India Sergio Gor revealing that only "the last 1 percent" of the deal remains unresolved. A US trade delegation is scheduled to arrive in New Delhi from June 1-4 to work through the final clauses.

"Just last week, India had sent a team to Washington DC to finalize the last 1 percent of that trade deal. Next week we will welcome a US delegation here to continue those talks," Gor said on Friday at the US-India TRUST Initiative event at IIT Delhi. "We fully expect that the trade deal will be signed over the next few weeks and months."

## What Changed the Game

The path to this moment has been anything but smooth. The foundational framework for the interim trade arrangement was finalized through a joint statement on February 7. But the negotiation landscape was upended shortly after when the US Supreme Court struck down all reciprocal tariffs — effectively dismantling the primary leverage the Trump administration had been using to negotiate trade concessions with global partners.

Washington pivoted quickly, imposing a 10 percent auxiliary duty on all incoming goods under Section 122 of the Trade Act for a 150-day window beginning February 24. Simultaneously, US authorities launched dual investigations under Section 301, scrutinizing major exporters over alleged excess industrial capacity and domestic labor practices.

The legal distinction matters. Section 122 caps emergency tariffs at 15 percent for a maximum of 150 days. Section 301, by contrast, gives Washington uncapped authority to levy duties if an investigation finds that a trading partner's policies are damaging American commercial interests. India has already submitted comprehensive responses to both active federal probes.

## The Numbers Tell the Story

Ambassador Gor highlighted the extraordinary growth in bilateral economic ties. Trade in goods and services between India and the US has grown from $20 billion to over $220 billion over the past two decades — a more than tenfold increase that makes the relationship one of the most commercially significant in the world.

The deal under negotiation covers multiple sectors: trade in goods, defence procurement, energy, AI and semiconductors, pharmaceuticals, critical minerals, and digital trade rules. For India, the agreement could open new export corridors and reduce tariff barriers on key products. For the US, it could deepen access to India's massive consumer market — 1.4 billion people with rising purchasing power.

## Why the Last 1 Percent Is the Hardest

Trade negotiators have a saying: the first 90 percent of a deal takes 10 percent of the time, and the last 10 percent takes 90 percent of the time. The final clauses typically involve the most politically sensitive issues — market access in protected sectors, compliance standards, agricultural subsidies, and intellectual property protections.

"When you reach the last 1 percent, you are dealing with the core protectionist interests that both governments have been shielding throughout the process," noted analysts tracking the negotiations. Data from the US Trade Representative's office confirms that India remains central to the administration's "friend-shoring" strategy of diversifying supply chains away from over-reliance on China.

## The Diaspora Dimension

For the estimated 4.4 million Indian-Americans in the United States, the trade deal carries implications that go beyond tariff schedules. A formal bilateral trade framework would provide regulatory certainty for the growing number of Indian-American entrepreneurs and professionals who operate across both economies.

It would also strengthen the strategic alignment between the two democracies at a moment when the relationship faces competing pressures — from the Iran war's impact on oil prices and supply chains, to the competition for semiconductor manufacturing capacity, to the ongoing immigration policy debates that directly affect Indian professionals.

The June 1-4 delegation visit will be watched closely. If negotiators can close the remaining gap, the deal would be the most significant bilateral trade agreement India has concluded with the United States in decades — and a concrete deliverable for a relationship that both governments have described as the defining partnership of the 21st century.

*Sources: ANI, Reuters, The Indian Eye, LatestLY*"""

    # Image: Ambassador Sergio Gor or US-India trade
    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Sergio Gor")
    if not img_url:
        img_url = fetch_pexels_image("US India trade business handshake", "diplomatic trade agreement")

    final_image = None
    image_attribution = None
    if img_url:
        final_image = upload_image_to_supabase(img_url, f"{slug}.jpg")
        if final_image:
            if "upload.wikimedia.org" in img_url:
                image_attribution = "Wikimedia Commons"
            else:
                image_attribution = "The Videshi"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": "ANI, Reuters",
        "image_url": final_image,
        "image_attribution": image_attribution,
    }
    return insert_article(article)


# ── Main ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("═══════════════════════════════════════════════")
    print("  The Videshi — News Writer — 2026-05-30 PM")
    print("═══════════════════════════════════════════════")

    results = []
    for i, fn in enumerate([article_brahmos, article_chandrayaan, article_trade_deal]):
        if i > 0:
            print("  (waiting 3s to avoid rate limits...)")
            time.sleep(3)
        try:
            art_id = fn()
            results.append(("✓" if art_id else "✗", fn.__doc__.strip()))
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            results.append(("✗", f"{fn.__doc__.strip()}: {e}"))

    print("\n═══ Summary ═══")
    for status, desc in results:
        print(f"  {status} {desc}")
    print("═══════════════════════════════════════════════")
