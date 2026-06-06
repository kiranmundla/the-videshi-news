#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-06-06 batch)
Three articles:
1. US strikes Iranian radar sites after drone flare-up at Hormuz (breaking, India energy angle)
2. India quietly rebuilds its oil map — Latin America/Africa pivot (strategic shift)
3. OPT program faces existential threat after ICE finds 10,000 fraud cases (diaspora/student impact)
"""

import json, os, sys, time, uuid, re, subprocess
from datetime import datetime, timezone

import requests
import urllib.parse

# ---------- env ----------
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            k, _, v = line.partition('=')
            v = v.strip().strip('"').strip("'")
            os.environ[k.strip()] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}
UA = 'TheVideshi/1.0 (thevideshi.com)'

# ---------- image helpers ----------

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
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


def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
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
            params=params, headers={"User-Agent": UA}, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page in pages.values():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and mime.startswith("image/") and "svg" not in mime.lower():
                    results.append(url)
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return []


def fetch_pexels(query, per_page=5):
    """Search Pexels for stock photos. Use curl fallback."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key")
        return []
    try:
        cmd = [
            'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
            f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page={per_page}'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            urls = []
            for photo in data.get('photos', []):
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    urls.append(url)
            return urls
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return []


def validate_image(url):
    """Validate image URL returns 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        if r.status_code != 200:
            # Try GET with stream
            r = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True, allow_redirects=True)
            if r.status_code != 200:
                print(f"  ✗ Image HTTP {r.status_code}: {url[:60]}...")
                return False
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' not in ct:
            print(f"  ✗ Not image content-type: {ct}")
            return False
        if cl > 0 and cl < 5000:
            print(f"  ✗ Image too small: {cl} bytes")
            return False
        return True
    except Exception as e:
        print(f"  ✗ Validate error: {e}")
        return False


def best_image(candidates):
    """Pick first valid image from a list."""
    for url in candidates:
        if validate_image(url):
            print(f"  ✓ Selected image: {url[:80]}...")
            return url
    return None


# ---------- article insertion ----------

def insert_article(article):
    """Insert article into Supabase p2_articles."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {data[0].get('slug', 'unknown')}")
            return True
        print(f"  ✓ Inserted (no data returned)")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return False


# ---------- articles ----------

def write_article_1():
    """US Strikes Iranian Radar Sites After Shooting Down Four Drones Over Hormuz"""
    print("\n=== Article 1: US-Iran Hormuz Escalation ===")
    
    headline = "The US Just Struck Iranian Radar Sites After Shooting Down Four Drones Over Hormuz. India's Oil Lifeline Is in the Crossfire."
    subheadline = "Saturday's exchange marks the sharpest flare-up since the April ceasefire. With Brent crude at $93 and India's LPG under-recovery at ₹700 per cylinder, every escalation lands directly on Indian household budgets."
    slug = "us-strikes-iran-radar-hormuz-drones-india-oil-lpg-june-2026"
    
    body = """The fragile calm over the Strait of Hormuz shattered on Saturday when U.S. Central Command said it shot down four Iranian attack drones and then struck two Iranian coastal surveillance radar installations — one in Goruk, the other on Qeshm Island, both overlooking the waterway through which a fifth of the world's oil once flowed freely.

The Pentagon described the action as defensive. A U.S. official told Reuters the drones were targeting regional maritime traffic, not American warships. Iran's coastal radar sites, the military said, were taken out to prevent further launches. But defensive or not, the exchange was the most significant since a shaky ceasefire took hold in April, and it immediately complicated an already difficult diplomatic track.

## A War That Was Supposed to End Weeks Ago

The U.S.-Israeli military campaign against Iran began on February 28. Within weeks, most of Iran's drone and missile manufacturing capacity was destroyed. President Trump himself estimated that Iran retains roughly 21 to 22 percent of its pre-war missile inventory. Yet more than three months later, Tehran has not signed a deal.

The sticking points are structural. Iran wants sanctions relief on crude exports, access to frozen oil revenue, the lifting of the U.S. naval blockade on its ports, and — critically — leverage over the Strait of Hormuz itself. Tehran has also made a ceasefire in Lebanon between Israel and Hezbollah a precondition for any broader peace deal with Washington.

Hezbollah leader Naim Qassem rejected a U.S.-brokered pact with the Lebanese government this week, and Israeli forces continued strikes in southern Lebanon on Friday. The parallel conflicts are feeding each other, and every breakdown on the Lebanon front pushes a Hormuz resolution further away.

Trump, campaigning in Wisconsin on Friday, vowed a quick end to the war. But the domestic political pressure is real: gas prices have spiked, farmers are feeling the squeeze, and even Republican voters in rural districts are expressing frustration. "The market is much more comfortable, calm, and complacent around the outcome," Dan Pickering of Pickering Energy Partners told Barron's. "That's either going to be right or wrong."

## What This Means for India

For India, every day the strait stays closed costs money. The Indian crude oil basket stood at $100.13 per barrel as of June 3, with the monthly average at $98.12, compared with $106.23 in May. Brent crude settled at $93.09 on Friday before the latest strikes were announced.

But the headline crude price understates the pain. India's state-run oil marketing companies are absorbing an under-recovery of ₹700 on every LPG cylinder sold, according to Sujata Sharma, joint secretary in the petroleum ministry. The cumulative daily under-recovery across the three OMCs — Indian Oil, Bharat Petroleum, and Hindustan Petroleum — stands at approximately ₹550 crore.

India traditionally sourced nearly 90 percent of its cooking gas from West Asia. That supply line is now severely disrupted. Refiners have scrambled to diversify, pulling in cargoes from Venezuela, Brazil, Angola, and Nigeria. But alternative suppliers cannot fully replace the volume, proximity, or pricing that Gulf producers offered.

Goldman Sachs estimated this week that global oil demand fell by 4 to 5 million barrels per day in April — a 4 to 5 percent decline — driven largely by the Hormuz closure. The bank warned that the longer the strait stays shut, the more volatile prices will become.

## The NRI Angle

For the roughly 4.5 million Indians in the Gulf states, the war is not an abstraction. Shipping disruptions have affected everything from trade flows to remittance corridors. The UAE, Saudi Arabia, and Oman — the three largest sources of NRI remittances to India — are all navigating the fallout.

The India-Oman CEPA, signed just last week with tariffs zeroed out on 98 percent of bilateral trade, was designed for a world in which goods could move freely through Hormuz. That assumption now looks fragile.

## What Comes Next

Market analysts increasingly doubt the war will end on Trump's timeline. "If peace is breaking out, that is a good thing," Pickering told Barron's. "But normal is pretty far off." He projected oil prices in the mid-$70s to low-$80s even after a deal, with the supply chain needing months to recover.

For India, the arithmetic is simple. Every additional week of Hormuz closure adds roughly $1 billion to the national fuel import bill. The government has so far avoided passing the full cost to consumers. How long that lasts depends on whether Saturday's strikes were a one-off, or the start of a new cycle.

*Sources: Reuters, Barron's, Livemint, Goldman Sachs research note, U.S. Central Command statement*"""

    # Image sourcing
    print("  Sourcing image...")
    candidates = []
    
    # Try Wikimedia Commons for Strait of Hormuz
    commons = fetch_wikimedia_commons("Strait of Hormuz military")
    candidates.extend(commons)
    time.sleep(1)
    
    commons2 = fetch_wikimedia_commons("USS aircraft carrier Persian Gulf")
    candidates.extend(commons2)
    time.sleep(1)
    
    # Pexels fallback
    pexels = fetch_pexels("oil tanker ocean")
    candidates.extend(pexels)
    
    image_url = best_image(candidates)
    image_caption = "A naval vessel in the Persian Gulf region near the Strait of Hormuz"
    image_attribution = "Wikimedia Commons"
    
    if image_url and 'pexels.com' in image_url:
        image_attribution = "Pexels"
        image_caption = "An oil tanker at sea — the Strait of Hormuz normally carries a fifth of global oil traffic"
    
    if not image_url:
        print("  ⚠ No valid image found, trying broader search...")
        pexels2 = fetch_pexels("military ship navy")
        image_url = best_image(pexels2)
        if image_url:
            image_attribution = "Pexels"
            image_caption = "A naval vessel at sea in the context of maritime security operations"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "politics",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url or "",
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "is_editorial": False,
        "sources": json.dumps(["Reuters", "Barron's", "Livemint", "Goldman Sachs", "U.S. Central Command"])
    }
    return insert_article(article)


def write_article_2():
    """India Quietly Rebuilds Its Oil Map — Venezuela Is Now Its Fourth-Largest Supplier"""
    print("\n=== Article 2: India Oil Sourcing Pivot ===")
    
    headline = "India Is Quietly Rebuilding Its Oil Map. Venezuela Just Became Its Fourth-Largest Supplier."
    subheadline = "As Hormuz stays shut, Indian refiners are locking in crude from Latin America and Africa. The shift is starting to look less like a stopgap and more like a structural overhaul of how India buys energy."
    slug = "india-oil-pivot-venezuela-latin-america-africa-hormuz-crude-sourcing-2026"
    
    body = """For decades, India's oil sourcing strategy had a single geographic center of gravity: West Asia. The Persian Gulf states — Saudi Arabia, Iraq, the UAE, Kuwait — supplied the bulk of India's 5 million barrels per day of crude imports. The proximity was unbeatable, the shipping lanes were secure, and the pricing was competitive.

Three months into the Hormuz blockade, that map has been redrawn.

## The New Suppliers

According to Kpler data cited in industry reports this week, Indian refiners have significantly increased crude purchases from four countries that barely registered in India's import mix a year ago: Venezuela, Brazil, Angola, and Nigeria.

Venezuela has emerged as the most striking case. The South American producer is on track to become India's fourth-largest crude supplier in May 2026 — a remarkable ascent for a country that was under sweeping U.S. sanctions just two years ago. The easing of some sanctions, combined with Venezuela's heavy crude grades that suit Indian refinery configurations, has created a natural fit.

Brazil, already a growing supplier, has ramped up shipments through Petrobras and independent producers. Angola and Nigeria, both members of OPEC, have found willing buyers in Indian refiners desperate to replace lost Gulf volumes.

Meanwhile, Russia remains India's dominant alternative supplier. Kpler data shows India is still scheduled to receive approximately 1.9 million barrels per day of Russian oil in May, along with about 41,000 bpd from Iraq — one of the few Gulf producers still managing to get cargoes through.

## Why This Is Not Temporary

There is a growing consensus among Indian energy officials and industry analysts that the current diversification is not a temporary fix. Three factors are driving a more permanent shift.

First, the Hormuz crisis has exposed a vulnerability that policymakers have discussed for years but never acted on. India's dependence on a single chokepoint for nearly half its energy imports was a known risk. The war has turned that theoretical risk into a lived reality.

Second, the economics have shifted. Russian crude, discounted since the Ukraine war began in 2022, remains the cheapest option for Indian refiners. Latin American heavy crudes, while more expensive to ship, are priced competitively enough to work at current Brent levels above $90.

Third, the geopolitics have evolved. India's willingness to buy from Venezuela — despite American pressure — signals a more assertive posture on energy sovereignty. New Delhi has made it clear that it will buy oil from whoever sells it at reasonable prices, regardless of where Washington draws its red lines.

## The LPG Problem

Crude is only part of the picture. The sharpest pain point for Indian consumers is liquefied petroleum gas. India traditionally sourced nearly 90 percent of its cooking gas from West Asia, and that supply line has been severely disrupted.

Sujata Sharma, joint secretary in the petroleum ministry, told reporters this week that state-run oil marketing companies are absorbing an under-recovery of ₹700 on every LPG cylinder sold. The cumulative daily loss across Indian Oil, Bharat Petroleum, and Hindustan Petroleum is approximately ₹550 crore — more than $65 million per day.

Unlike crude, LPG is harder to diversify. The infrastructure for importing LPG from non-Gulf sources — ships, port terminals, storage — was built for Middle Eastern supply chains. Rebuilding those logistics will take years, not months.

## What NRIs Should Watch

For the Indian diaspora, the oil map reshuffling has direct economic implications. A sustained period of high crude prices will pressure the rupee, push up inflation, and potentially delay the RBI's rate-cutting cycle. Indian consumers are already paying more for petrol and diesel than they were six months ago, and the subsidy burden on LPG will eventually force a political reckoning.

The structural pivot also opens investment opportunities. Indian companies building LNG import terminals, pipeline infrastructure, and strategic storage facilities are likely to see accelerated government support. The India Strategic Petroleum Reserves Limited programme, which currently holds about 36.7 million barrels, is under pressure to expand.

For India's refining sector — already one of the world's most competitive — the new sourcing mix is a manageable challenge. The question is whether the political will exists to make the diversification permanent, or whether it will be quietly abandoned the moment Hormuz reopens.

*Sources: Kpler data via The Indian Eye, Livemint, Goldman Sachs, Indian petroleum ministry briefing*"""

    # Image sourcing
    print("  Sourcing image...")
    candidates = []
    
    # Wikimedia Commons: oil tankers, refineries
    commons = fetch_wikimedia_commons("Indian oil refinery")
    candidates.extend(commons)
    time.sleep(1)
    
    commons2 = fetch_wikimedia_commons("oil tanker crude carrier")
    candidates.extend(commons2)
    time.sleep(1)
    
    # Pexels
    pexels = fetch_pexels("oil refinery industrial")
    candidates.extend(pexels)
    
    image_url = best_image(candidates)
    image_caption = "An oil refinery — India is restructuring its crude sourcing away from the Persian Gulf"
    image_attribution = "Wikimedia Commons"
    
    if image_url and 'pexels.com' in image_url:
        image_attribution = "Pexels"
    
    if not image_url:
        pexels2 = fetch_pexels("cargo ship ocean freight")
        image_url = best_image(pexels2)
        if image_url:
            image_attribution = "Pexels"
            image_caption = "A cargo vessel at sea — India is diversifying oil imports to Latin America and Africa"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "economy",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url or "",
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "is_editorial": False,
        "sources": json.dumps(["Kpler", "The Indian Eye", "Livemint", "Goldman Sachs", "Indian petroleum ministry"])
    }
    return insert_article(article)


def write_article_3():
    """ICE Finds 10,000 OPT Fraud Cases. A Petition to Kill the Program Could Affect 200,000 Indian Graduates."""
    print("\n=== Article 3: OPT Fraud / Indian Students ===")
    
    headline = "ICE Just Found 10,000 Cases of OPT Fraud. A Legal Petition Could Kill the Program Entirely."
    subheadline = "The Optional Practical Training programme is how most Indian graduates stay in the US after college. A conservative legal foundation has petitioned DHS to shut it down — and the Trump administration may be listening."
    slug = "opt-fraud-ice-10000-cases-dhs-petition-indian-students-stem-2026"
    
    body = """Two weeks ago, Immigration and Customs Enforcement dropped a number that sent a chill through every Indian student visa holder in America: more than 10,000 possible cases of fraud in the Optional Practical Training programme.

Acting ICE Director Todd Lyons announced the findings at a press conference after investigators conducted on-site visits to employers participating in the programme. What they found was damning. In some cases, OPT participants were being managed by employees based in India — not by supervisors at the U.S. companies that had ostensibly hired them. In others, shell companies were helping recent graduates remain in the country without genuine sponsorship from a U.S. employer.

The findings have energised a legal effort that could go much further than catching individual fraudsters. The Landmark Legal Foundation, a conservative legal organisation, has submitted a formal petition to the Department of Homeland Security asking it to rescind post-completion OPT entirely — not reform it, not tighten oversight, but eliminate it.

## What OPT Actually Is

Optional Practical Training allows international students on F-1 visas to work in the United States for up to 12 months after graduation. Students in STEM fields — science, technology, engineering, and mathematics — get an extension of up to 24 additional months, for a total of 36 months of post-graduation work authorization.

For Indian students, OPT is not a nice-to-have. It is the bridge between graduation and an H-1B visa. Without it, most international graduates would have to leave the country immediately after completing their degrees, with no legal pathway to gain the work experience that H-1B petitions require.

The numbers are staggering. According to USCIS data, more than 200,000 international students were on OPT or STEM OPT in fiscal year 2025. Indian nationals represent the largest single group, accounting for roughly 40 percent of all OPT participants. Chinese nationals are the second-largest group.

## The Legal Argument

The Landmark Legal Foundation's petition makes several arguments for why DHS can — and should — kill post-completion OPT without any action from Congress.

The centrepiece is the "major questions doctrine," a legal principle the Supreme Court has increasingly relied on to strike down executive actions of broad economic significance that lack clear congressional authorization. The foundation argues that OPT affects large segments of the labour market, involves substantial fiscal consequences including tax exemptions tied to foreign student employment, and operates outside the congressionally set visa caps that govern programmes like H-1B.

In other words, OPT functions as an end run around the limits Congress set on work visas. The programme allows hundreds of thousands of foreign workers into the U.S. labour market each year through an administrative mechanism that was never designed for that scale.

The petition also notes that OPT participants and their employers are exempt from Social Security and Medicare taxes — a subsidy that effectively makes OPT workers cheaper to hire than American citizens or green card holders doing the same job.

## What the Trump Administration Might Do

The Trump administration has already demonstrated its willingness to crack down on immigration programmes through executive action. The $100,000 fee imposed on new H-1B petitions in September 2025 priced out many mid-tier sponsors. The ban on FHA mortgages for non-permanent residents took effect last May. And the administration's broader posture on immigration has been consistently restrictive.

Eliminating OPT would not require legislation. The programme was created through regulation under the Administrative Procedure Act, and it can be rescinded through the same process. DHS would need to go through a notice-and-comment rulemaking period, but the outcome would be within the administration's control.

Whether the administration will act on the petition is unclear. But the ICE fraud findings have given OPT's critics powerful ammunition, and the political environment — with the 2026 midterms approaching and immigration a top voter issue — favours action.

## What Indian Students Should Do Now

Immigration attorneys who work with Indian students say the key is to assume nothing about the programme's future and act accordingly.

Students currently on OPT should ensure their employment is genuine, documented, and with a company that can demonstrate real supervision and a legitimate business purpose. Shell company arrangements, remote management from India, or positions that exist primarily to maintain visa status are exactly the patterns ICE is targeting.

Students approaching graduation should consider whether employer-sponsored H-1B petitions are feasible, and whether their employer is willing to pay the now-$100,000 filing fee. Those in STEM fields should prioritize companies with strong track records of successful H-1B sponsorship.

And every Indian student considering a U.S. degree should factor in the possibility that the post-graduation work pathway may look very different by the time they finish. OPT is not guaranteed. It never was.

*Sources: Washington Examiner, ICE press conference, Landmark Legal Foundation petition, USCIS data, Pew Research Center*"""

    # Image sourcing
    print("  Sourcing image...")
    candidates = []
    
    # Wikimedia Commons: university, graduation, students
    commons = fetch_wikimedia_commons("international students university graduation")
    candidates.extend(commons)
    time.sleep(1)
    
    commons2 = fetch_wikimedia_commons("F-1 visa OPT students United States")
    candidates.extend(commons2)
    time.sleep(1)
    
    # Pexels
    pexels = fetch_pexels("university graduation students diverse")
    candidates.extend(pexels)
    
    image_url = best_image(candidates)
    image_caption = "International graduates at a US university — OPT is the primary post-graduation work pathway"
    image_attribution = "Wikimedia Commons"
    
    if image_url and 'pexels.com' in image_url:
        image_attribution = "Pexels"
    
    if not image_url:
        pexels2 = fetch_pexels("college campus students")
        image_url = best_image(pexels2)
        if image_url:
            image_attribution = "Pexels"
            image_caption = "Students on a US college campus — the OPT programme is under unprecedented scrutiny"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "education",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url or "",
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "is_editorial": False,
        "sources": json.dumps(["Washington Examiner", "ICE", "Landmark Legal Foundation", "USCIS", "Pew Research Center"])
    }
    return insert_article(article)


# ---------- main ----------
if __name__ == '__main__':
    print("=" * 60)
    print("The Videshi — News Writer Batch (2026-06-06)")
    print("=" * 60)
    
    results = []
    results.append(("US-Iran Hormuz Strikes", write_article_1()))
    time.sleep(2)
    results.append(("India Oil Pivot", write_article_2()))
    time.sleep(2)
    results.append(("OPT Fraud / Indian Students", write_article_3()))
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, success in results:
        status = "✓ PUBLISHED" if success else "✗ FAILED"
        print(f"  {status}: {name}")
    print("=" * 60)
    
    failures = sum(1 for _, s in results if not s)
    if failures:
        print(f"\n⚠ {failures} article(s) failed to publish")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} articles published successfully")
