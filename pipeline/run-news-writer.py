#!/usr/bin/env python3
"""News writer for The Videshi — generates 3 articles for the news category."""
import json, os, requests, urllib.parse, time, re, subprocess, hashlib
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), val)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run([
            'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
            f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape'
        ], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{query}'")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Verify image URL returns HTTP 200 with image content type and >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Some servers don't return Content-Length on HEAD, try GET
        if r.status_code == 200 and 'image' in ct:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def find_best_image(person_name=None, topic_queries=None, pexels_query=None):
    """Multi-source image search: Wikipedia > Wikimedia Commons > Pexels."""
    # 1. Wikipedia person image
    if person_name:
        img = fetch_wikipedia_person_image(person_name)
        if img and validate_image(img):
            return img, "Wikimedia Commons"

    # 2. Wikimedia Commons search
    if topic_queries:
        for q in topic_queries:
            results = fetch_wikimedia_commons_images(q)
            for r in results:
                url = r.get("url") or r.get("original_url")
                if url and validate_image(url):
                    return url, "Wikimedia Commons"

    # 3. Pexels fallback
    if pexels_query:
        img = fetch_pexels_image(pexels_query)
        if img and validate_image(img):
            return img, "Pexels"

    return None, None

def insert_article(article):
    """Insert an article into Supabase."""
    print(f"\n📝 Inserting: {article['headline']}")
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('slug', 'unknown')}")
        else:
            print(f"  ✓ Published (response: {str(result)[:100]})")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


# ============================================================
# ARTICLE 1: India's Largest-Ever Defense Deal — 114 Rafale Jets
# ============================================================
def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India's ₹3.25 Lakh Crore Rafale Deal")
    print("="*60)

    # Image: Rafale jet or Dassault Aviation
    img_url, img_attr = find_best_image(
        topic_queries=["Rafale fighter jet Indian Air Force", "Dassault Rafale India"],
        pexels_query="fighter jet military"
    )

    body = """India has formally issued a Letter of Request to France for the procurement of 114 Rafale fighter aircraft in a government-to-government deal estimated at ₹3.25 lakh crore ($34.16 billion), marking the single largest defense acquisition in the country's history.

The Defence Ministry's Acquisition Wing sent the request last week, initiating what officials say could be concluded within a year. Of the 114 jets, 94 are expected to be manufactured in India through a partnership between French aerospace major Dassault Aviation and an Indian company — a centrepiece of the government's Make in India and Atmanirbhar Bharat defence strategy.

## A Critical Gap in the Sky

The Indian Air Force currently operates just 29 fighter squadrons against a sanctioned strength of 42 — a gap that has widened sharply following the retirement of ageing MiG-21 and MiG-27 fleets. The Rafale, a 4.5-generation multirole combat aircraft that has already proven itself in IAF service with 36 jets inducted since 2020, is considered the frontrunner to fill that void.

https://x.com/IAabortedflight/status/1929611736754487766

With this order, India's total Rafale fleet could exceed 200 aircraft when combined with 62 jets already ordered for the Air Force and Navy — including 31 slated for carrier operations. That would make India one of the largest Rafale operators in the world, behind only France itself.

## IAF Chief's France Visit Sets the Stage

The Letter of Request coincides with Indian Air Force Chief Air Chief Marshal Amar Preet Singh's four-day visit to France, which began on June 1. During the trip, he is scheduled to visit Dassault Aviation's Mérignac facility — the Rafale's final assembly line — as well as MBDA, the missile manufacturer behind the Meteor and SCALP systems integrated into the Rafale platform.

Discussions during the visit are expected to cover production timelines, localisation of Indian weapons systems, technical cooperation, and the architecture of a new Rafale assembly line in India. Defence sources indicate the programme will incorporate nearly 50 percent indigenous content, providing a substantial boost to India's aerospace manufacturing ecosystem.

## Modi's France Visit and the Bigger Picture

Prime Minister Narendra Modi is expected to visit France around mid-June for a G7 outreach session, and the Rafale deal is almost certain to feature in bilateral discussions with President Emmanuel Macron. The deal cements a defence relationship that has accelerated dramatically since India's first Rafale order of 36 jets in 2016.

France is now India's second-largest defence supplier after Russia, and the partnership extends beyond fighter jets. The two countries are collaborating on submarine design under Project 75(I), Scorpène-class submarine transfers, and joint development of military engines.

## What It Means for Indian Defence Manufacturing

The deal's Make in India component could transform India's defence industrial base. With 94 jets to be assembled domestically, the programme will require thousands of components sourced from Indian manufacturers, potentially creating an aerospace supply chain that outlasts the Rafale programme itself.

For the diaspora watching from abroad, the deal is a marker of how far India's defence posture has evolved — from decades of dependency on Soviet-era platforms to a diversified, technology-driven acquisition strategy that now spans American, French, Israeli, and Indian systems."""

    article = {
        "headline": "India Just Issued a ₹3.25 Lakh Crore Order for 114 Rafale Jets. It Is the Largest Defence Deal in Indian History.",
        "subheadline": "Of the 114 jets, 94 will be manufactured in India by Dassault Aviation — the biggest Make in India defence programme ever launched.",
        "body": body,
        "slug": "india-114-rafale-jets-325-lakh-crore-defence-deal-france-dassault-make-in-india-20260603",
        "category": "news",
        "vertical": "news",
        "image_url": img_url or "",
        "image_attribution": img_attr or "",
        "sources": json.dumps(["The Hindu BusinessLine", "ANI", "India Strategic", "DevDiscourse", "Madhyamam Online"]),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False
    }

    if not img_url:
        print("  ⚠ No image found, skipping article")
        return False
    return insert_article(article)


# ============================================================
# ARTICLE 2: Modi-Hlaing Summit — Myanmar Pledges on NE Insurgents
# ============================================================
def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Modi-Hlaing Summit — Myanmar Pledges Action")
    print("="*60)

    # Image: Modi or Myanmar summit
    img_url, img_attr = find_best_image(
        person_name="Narendra Modi",
        topic_queries=["Narendra Modi Min Aung Hlaing summit", "India Myanmar summit 2026"],
        pexels_query="India diplomatic summit"
    )

    body = """Myanmar's president, Min Aung Hlaing, has assured Prime Minister Narendra Modi that Myanmar will not permit Indian insurgent groups to use its territory as a base — the strongest such guarantee in years, delivered during a summit at Hyderabad House in New Delhi on June 1.

The meeting, the first between the two leaders since Hlaing assumed the presidency following Myanmar's parliamentary elections earlier this year, produced a joint statement affirming that "Myanmar's territory would not be permitted to be used against India's security interests." In return, Modi reaffirmed India's support for Myanmar's sovereignty and territorial integrity.

## The 1,643-Kilometre Problem

India shares a 1,643-kilometre porous border with Myanmar, touching four northeastern states — Arunachal Pradesh, Nagaland, Manipur, and Mizoram. For decades, separatist outfits with a history of cross-border movement have operated in this corridor, using Myanmar's ungoverned spaces as staging grounds for attacks on Indian security forces.

Foreign Secretary Vikram Misri, who briefed reporters after the talks, said Modi raised the insurgent presence directly. "The president once again reiterated his assurance that Myanmar was sensitive to these concerns and would do everything necessary to ensure there was action against these groups," Misri said.

## Beyond Security — A Wider Agenda

The summit extended well beyond counter-insurgency. The two leaders discussed a sprawling bilateral agenda that included trade, connectivity, space cooperation, border fencing, and the sensitive issue of Myanmar's detained democracy leader, Aung San Suu Kyi.

India is currently constructing a fence along the Myanmar border — a politically charged project that New Delhi says will enhance security infrastructure without disrupting the deep people-to-people ties that exist along the frontier. Misri confirmed that India has shared details of designated entry points and gates with the Myanmar side and expressed confidence that the project would proceed on a cooperative basis.

## The Free Movement Regime Overhaul

The summit also addressed India's decision to end the Free Movement Regime, which previously allowed people living within 16 kilometres of the border to cross without visas. The cancellation, announced in 2024, was driven by concerns over drug trafficking, arms smuggling, and illegal immigration — but it has been controversial among border communities whose families straddle the international line.

India is now replacing the open regime with a structured entry-point system, maintaining connectivity through controlled gates while establishing a physical security perimeter. The approach attempts to balance the northeast's deeply intertwined cross-border social fabric with New Delhi's legitimate security imperatives.

## What It Means for the Diaspora

For the Indian diaspora, the summit is a reminder of how India's security challenges in the northeast rarely make headlines in the way that tensions with Pakistan or China do, but remain equally consequential. Myanmar's cooperation — or lack of it — directly shapes the security environment for millions of people in some of India's most vulnerable states.

The summit also signals India's pragmatic foreign policy in action: engaging Myanmar's military government on security and connectivity, even as the international community remains divided over the country's democratic backsliding. It is the kind of quiet, strategic diplomacy that New Delhi increasingly favours — prioritising outcomes over posturing."""

    article = {
        "headline": "Myanmar's President Just Promised Modi That Indian Insurgents Will Not Use Its Territory. It Is the Strongest Guarantee in Years.",
        "subheadline": "The summit at Hyderabad House covered border security, fencing, Aung San Suu Kyi, and an expanding agenda from trade to space cooperation.",
        "body": body,
        "slug": "modi-min-aung-hlaing-summit-myanmar-northeast-insurgents-border-security-20260603",
        "category": "news",
        "vertical": "news",
        "image_url": img_url or "",
        "image_attribution": img_attr or "",
        "sources": json.dumps(["India Sentinels", "Ministry of External Affairs", "Press Information Bureau", "GlobalSecurity.org"]),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False
    }

    if not img_url:
        print("  ⚠ No image found, skipping article")
        return False
    return insert_article(article)


# ============================================================
# ARTICLE 3: India-Australia Defence Dialogue — Maritime Cooperation
# ============================================================
def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: India-Australia Defence Dialogue")
    print("="*60)

    # Image: Rajnath Singh or India-Australia defense
    img_url, img_attr = find_best_image(
        person_name="Rajnath Singh",
        topic_queries=["India Australia defence cooperation", "Rajnath Singh Richard Marles"],
        pexels_query="navy warship Indian Ocean"
    )

    body = """India and Australia have agreed to deepen maritime security cooperation and explore undersea domain awareness as part of a broadening defence partnership, following the second edition of the India-Australia Defence Ministers' Dialogue held in New Delhi on June 1.

Defence Minister Rajnath Singh and Australian Deputy Prime Minister and Defence Minister Richard Marles co-chaired the dialogue at the Manekshaw Centre, building on the inaugural meeting held in October 2025. The two leaders endorsed significant progress in the bilateral relationship and agreed to renew and strengthen the Joint Declaration on Defence and Security Cooperation.

## The Maritime Pivot

At the heart of the dialogue was a shared recognition that the Indo-Pacific's security architecture depends on credible maritime cooperation between like-minded democracies. The two sides discussed progress toward finalising a Joint Maritime Security Collaboration Roadmap — a framework document that will govern joint exercises, intelligence sharing, and coordinated patrols.

Both ministers agreed to advance collaborative maritime domain awareness activities using maritime patrol aircraft and to explore opportunities to enhance undersea domain awareness — a capability area that has gained urgency as submarine activity in the Indian Ocean increases. The reference to undersea awareness is notable: it signals that the two countries are moving beyond surface-level cooperation toward the more sensitive and strategically significant domain of submarine detection and tracking.

## Coast Guard and Cyber Cooperation

The dialogue also encouraged deeper cooperation between the Indian Coast Guard and Australia's Maritime Border Command, reflecting a shared interest in tackling non-traditional maritime threats including drug trafficking, illegal fishing, and people smuggling.

https://x.com/rajaborijfnews/status/1929572102439375277

Beyond the maritime domain, the two sides discussed defence technology cooperation, cyber security, and space situational awareness — areas where Australia's Five Eyes intelligence access and India's growing indigenous defence ecosystem create natural complementarities.

## The Quad and the Indo-Pacific

The timing of the dialogue is significant. India and Australia are both members of the Quad — alongside the United States and Japan — and their bilateral defence relationship has accelerated dramatically since the 2020 Comprehensive Strategic Partnership. The Malabar naval exercise, once restricted to India and the US, now regularly includes Australia and Japan.

For India, Australia represents a partner with no historical baggage in the subcontinent, strong alignment on Indo-Pacific security, and growing economic ties — particularly in critical minerals, education, and energy. For Australia, India is the critical swing state in the Indo-Pacific: a major maritime power with the world's largest navy by hull count and an increasingly assertive posture in the Indian Ocean.

## What It Means for the Diaspora

The India-Australia relationship has a strong people-to-people dimension. Australia is home to over 900,000 people of Indian origin, the country's fastest-growing diaspora community. Defence cooperation reinforces a broader bilateral relationship that includes a free trade agreement signed in 2022, a surge in Indian student enrolments, and growing cricket diplomacy.

For diaspora members watching the Indo-Pacific's security architecture take shape, the India-Australia defence dialogue is a reminder that the region's future will be shaped not by any single alliance, but by a web of bilateral and multilateral partnerships that India is systematically building."""

    article = {
        "headline": "India and Australia Just Agreed to Track Submarines Together. The Indo-Pacific's Security Map Is Being Redrawn.",
        "subheadline": "The second defence ministers' dialogue advanced a maritime roadmap, undersea domain awareness, and coast guard cooperation — the deepest bilateral defence agenda yet.",
        "body": body,
        "slug": "india-australia-defence-dialogue-maritime-cooperation-undersea-awareness-rajnath-marles-20260603",
        "category": "news",
        "vertical": "news",
        "image_url": img_url or "",
        "image_attribution": img_attr or "",
        "sources": json.dumps(["Ministry of Defence India", "Insight Pulse", "Press Information Bureau", "The Diplomat Nepal"]),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False
    }

    if not img_url:
        print("  ⚠ No image found, skipping article")
        return False
    return insert_article(article)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("🗞️ The Videshi News Writer — Starting")
    print(f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    results = []
    results.append(("Rafale Deal", write_article_1()))
    time.sleep(1)
    results.append(("Modi-Hlaing Summit", write_article_2()))
    time.sleep(1)
    results.append(("India-Australia Defence", write_article_3()))

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, success in results:
        status = "✓ Published" if success else "✗ Failed"
        print(f"  {status}: {name}")
    
    published = sum(1 for _, s in results if s)
    print(f"\n📊 {published}/{len(results)} articles published")
