#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-15 batch (scheduled videshi-writer-news)
3 articles:
  1. Germany scraps airport transit visa for Indians (travel mobility)
  2. Delhi Malviya Nagar B&B fire — accountability fallout (urban safety)
  3. Andhra Pradesh HC: single mother can get child's passport w/o father consent (diaspora rights)
"""

import json, os, subprocess, re, time, datetime, urllib.parse, requests

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                key = key.strip().replace('export ', '')
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}


# --- Image sourcing ---
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=8):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers=UA, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                width = ii.get("width", 0)
                if url and "image" in mime and width > 300:
                    results.append({"url": url, "title": page.get("title", ""),
                                    "width": width, "height": ii.get("height", 0)})
            print(f"  ✓ Wikimedia Commons: {len(results)} results for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        for photo in data.get("photos", []):
            url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if url:
                print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def validate_image(url):
    """Validate via GET (HEAD on upload.wikimedia.org returns 400 from this host)."""
    try:
        r = requests.get(url, timeout=12, stream=True, allow_redirects=True, headers=UA)
        ct = r.headers.get("Content-Type", "")
        chunk = r.raw.read(12000)
        if r.status_code == 200 and "image" in ct and len(chunk) > 5000:
            print(f"  ✓ Image validated: {r.status_code}, {ct}, {len(chunk)}+ bytes")
            return True
        print(f"  ✗ Image validation failed: {r.status_code}, {ct}, {len(chunk)} bytes")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def pick_commons_image(query, keywords, caption):
    for img in fetch_wikimedia_commons_images(query, 8):
        tl = img["title"].lower()
        if any(kw in tl for kw in keywords) and validate_image(img["url"]):
            return img["url"], caption, "Wikimedia Commons"
    return None, "", ""


def insert_article(article):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=20)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Inserted: {result[0].get('slug', 'unknown')}")
            return True
        print("  ✓ Inserted (no body returned)")
        return True
    print(f"  ✗ Insert failed: {r.status_code} — {r.text[:300]}")
    return False


def finalize(article, image_url, image_caption, image_attribution):
    if image_url:
        article["image_url"] = image_url
        article["image_caption"] = image_caption
        article["image_attribution"] = image_attribution
    else:
        print("  ⚠ No valid image found — inserting without image")
    return insert_article(article)


# ========================================================================
# ARTICLE 1: Germany scraps airport transit visa for Indians
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: Germany scraps airport transit visa for Indians")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Frankfurt Airport terminal", ["frankfurt", "airport", "terminal", "flughafen"],
        "Frankfurt Airport, one of the German hubs now open to Indians for visa-free transit")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Munich Airport terminal", ["munich", "airport", "terminal", "flughafen", "münchen"],
            "Munich Airport, a major transit hub for Indian travellers connecting onward")
    if not image_url:
        px = fetch_pexels_image("airport terminal departure international")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "An international airport transit terminal", "Pexels"

    slug = "germany-scraps-airport-transit-visa-indian-travellers-frankfurt-munich-20260615"

    body = """For years, the most frustrating part of flying from India to the Americas through Europe was not the long-haul leg. It was the paperwork required just to change planes. An Indian passport holder connecting through Frankfurt or Munich on the way to New York or Toronto needed a Schengen Airport Transit Visa — a Category A visa — even if they never left the secure international transit zone. That requirement is now gone.

As of June 3, 2026, Germany has waived the airport transit visa for Indian nationals transiting exclusively by air. The German Embassy in New Delhi confirmed the change, and India's Ministry of External Affairs welcomed it the same week, calling it a step that "would further enhance people-to-people ties between India and Germany." For the thousands of Indians who route through German hubs every week, it removes a bureaucratic hurdle that had no real purpose beyond friction.

## What Actually Changed

Until now, even a passenger who simply walked from one gate to another inside Frankfurt Airport — never clearing immigration, never entering German soil — was technically required to hold a Type A transit visa. The new arrangement scraps that for single-airport air transit. Indian passport holders connecting through Frankfurt, Munich, Berlin and other German international airports to a non-Schengen destination can now do so without applying for any separate transit visa.

The decision operationalises an announcement first made during German Chancellor Friedrich Merz's visit to India in January 2026, when Prime Minister Narendra Modi thanked him for the move. It also follows France, which waived its own airport transit visa requirement for Indian passport holders earlier in 2026 — part of a broader European loosening of friction for Indian flyers.

## The Fine Print Matters

This is not visa-free entry into Germany, and the distinction is important. The exemption applies only to passengers making a single airport transit before continuing to a non-Schengen country. Travellers who want to leave the airport, enter Germany, or visit for tourism, business or family still need the appropriate Schengen visa.

German authorities have also flagged specific exclusions. The waiver does not cover passengers transiting through two or more airports within the Schengen Area, those who need to collect and recheck baggage during the connection, or travellers holding open tickets that require additional airport processing. In practice, that means a clean single-stop connection through one German hub qualifies; a multi-leg European itinerary may not.

## Why the Diaspora Should Care

For the Indian diaspora, Germany is not a destination so much as a gateway. Lufthansa Group alone operates more than 70 weekly flights between India and Europe, and Frankfurt and Munich are among the busiest connecting points for Indians flying onward to North America. The waiver directly benefits NRIs and their families who fly back and forth — students returning to US universities, professionals routing to Canada, parents visiting children abroad.

The change also reflects a warming travel relationship. The number of Indians staying overnight in Germany crossed 775,000 between January and October 2025, and the German National Tourist Office has set a target of one million overnight stays by Indian tourists in 2026. Removing the transit-visa irritant is a low-cost way for Berlin to signal that Indian travellers are welcome.

## A Pattern Across Europe

Germany's move fits a wider 2026 trend. France waived its airport transit visa for Indians in April. At the same time, the European Union is rolling out its Entry/Exit System and the ETIAS pre-travel authorisation regime, which will add digital screening layers for visa-exempt travellers in the coming year. The net effect is a Europe that is simultaneously easing friction for legitimate transit while tightening digital tracking at its borders.

For now, the practical takeaway for Indian flyers is simple. If your itinerary involves a single connection through a German airport to a non-Schengen destination, you no longer need to spend time, money and anxiety on a transit visa. Just confirm with your airline that your specific routing qualifies — and that you will not need to re-clear baggage — before you book.

**Sources:** German Embassy New Delhi, Ministry of External Affairs (India), Livemint, LatestLY/ANI, HDFC ERGO travel advisory, Travel + Leisure Asia"""

    article = {
        "headline": "Germany Just Scrapped the Airport Transit Visa for Indians. Frankfurt and Munich Are Now Open Gateways.",
        "subheadline": "From June 3, Indian passport holders can connect through German airports to non-Schengen destinations without a Type A transit visa. The fine print still matters.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-mobility",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Frankfurt and Munich are among the busiest connecting hubs for Indians flying to North America, so scrapping the transit visa directly eases travel for NRIs, students and visiting families.",
        "sources": ["German Embassy New Delhi", "Ministry of External Affairs (India)", "Livemint", "LatestLY / ANI", "Travel + Leisure Asia"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: Delhi B&B fire accountability fallout
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: Delhi Malviya Nagar B&B fire — accountability fallout")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Delhi Fire Service", ["fire", "delhi", "service", "brigade"],
        "Delhi Fire Service personnel; the Malviya Nagar blaze killed 23 people")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Malviya Nagar New Delhi", ["malviya", "delhi", "saket", "south delhi"],
            "South Delhi's Malviya Nagar, where a B&B fire killed 23")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "New Delhi street", ["delhi", "street", "india"],
            "A street in New Delhi")
    if not image_url:
        px = fetch_pexels_image("fire truck firefighter emergency")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "Firefighters respond to a blaze", "Pexels"

    slug = "delhi-malviya-nagar-bnb-fire-23-dead-inspector-sacked-building-violations-20260615"

    body = """The fire that tore through a five-storey bed-and-breakfast in South Delhi's Hauz Rani locality on June 3 was not just a tragedy. It was, in the words of the officials now investigating it, an entirely preventable one. Twenty-three people died — including eight members of a single family, the Agarwals, and roughly 15 foreign nationals from Central Asia and Africa. More than 30 others were seriously injured. Nearly two weeks later, the focus has shifted from the flames to the question of how the building was ever allowed to operate.

## A Death Trap by Design

The establishment, operating under a bed-and-breakfast licence that permitted just six rooms, was allegedly running about 25 rooms spread across a basement, ground floor and five upper storeys — including the terrace. It did not hold a fire No Objection Certificate. Investigators say the building's design turned a containable fire into a mass-casualty event.

"The building's design made escape almost impossible for the occupants," Chief Fire Officer Abhilash Kumar Malik told the Press Trust of India. "The windows had been permanently sealed, resulting in no ventilation. Such buildings act like a shaft, where heat and smoke can engulf the entire structure within seconds."

Residents described a sensor-operated entrance gate that stopped working once the fire broke out, trapping guests behind a door they could not open while sealed glass windows cut off any alternative escape. It was, by every account, a structure built for occupancy and not for survival.

## The Accountability Question

The early arrests have drawn sharp criticism. Police booked a 65-year-old cook, Keshav Singh Negi, under five serious criminal provisions and sent him to 14 days' judicial custody, accusing him of shutting a door and switching off the electricity before fleeing. Civil society members, social workers and residents have alleged he is being made a scapegoat while the hotel's owners and the officials who signed off on it are shielded.

"The primary responsibility for safety lapses in a hotel lies with its management and owners, not with a low-level employee," critics argued, according to The420.in. Former MCD City Zone chairperson Renuka Gupta questioned why no action under the culpable-homicide provisions had been taken against officials, blamed building-department engineers for 20 rooms allegedly constructed illegally, and asked why the Delhi Tourism Development Corporation allowed the property to keep operating for two months after its licence expired in March.

The Municipal Corporation of Delhi has since terminated the health officer who inspected the hotel on June 2 — a single day before the fire — alleging he conducted a "superficial" inspection and recommended a licence based on a "false" report. A second officer has been transferred to MCD headquarters. The owner of the building has been arrested.

## A Citywide Reckoning

In the immediate aftermath, the Delhi government announced a citywide crackdown on guest houses and other establishments operating in violation of fire-safety norms and building by-laws. Non-compliant premises would be sealed and those responsible prosecuted, the Chief Minister's office said. It was the deadliest fire the capital had seen since 2022, and the pattern it exposed — overcrowded, unlicensed, poorly ventilated lodgings packed into dense neighbourhoods — is hardly unique to one address.

The Hauz Rani property was reportedly popular with patients being treated at a nearby hospital and their relatives, the kind of budget accommodation that fills up precisely because it is cheap and close to where people need to be.

## Why This Hits the Diaspora

For NRIs, the fire is a pointed warning. Diaspora families returning to India routinely book budget hotels, guest houses and B&Bs for medical visits, weddings and pilgrimages — often the same congested, informally regulated lodgings that proliferate around hospitals and city centres. The presence of foreign nationals among the dead underscores that these are not abstract risks. The Ministry of External Affairs is in contact with the relevant embassies over the foreign victims.

The harder truth is that licensing on paper guaranteed nothing here. Until the citywide crackdown moves beyond announcements and the accountability extends past a cook to the owners and officials who enabled the violations, travellers — diaspora and domestic alike — are left to do their own due diligence on fire exits, ventilation and crowding before they check in.

**Sources:** Press Trust of India, Reuters, The Business Standard, Hindustan Times, The420.in, The Indian EYE"""

    article = {
        "headline": "23 Died in a Delhi B&B That Should Never Have Been Open. The Inspector Who Cleared It Has Been Sacked.",
        "subheadline": "A six-room licence, 25 rooms in reality, sealed windows and no fire NOC. As Delhi promises a citywide crackdown, critics ask why a cook was arrested before the owners and officials.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "urban-safety",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "NRI families visiting India for medical care, weddings and pilgrimages routinely stay in exactly the kind of budget, informally regulated lodgings that turned deadly in Malviya Nagar.",
        "sources": ["Press Trust of India", "Reuters", "The Business Standard", "Hindustan Times", "The420.in"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: AP High Court — single mother passport without father consent
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: AP HC single-mother passport ruling")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Indian passport", ["passport", "india", "republic of india"],
        "An Indian passport; courts have repeatedly affirmed a single parent's right to obtain one for a minor")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Andhra Pradesh High Court building", ["high court", "andhra", "amaravati", "court"],
            "The Andhra Pradesh High Court")
    if not image_url:
        px = fetch_pexels_image("passport travel document")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "A passport and travel documents", "Pexels"

    slug = "andhra-high-court-single-mother-child-passport-without-father-consent-20260615"

    body = """For a separated or estranged parent in India, one of the most quietly painful bureaucratic battles is the simplest-sounding one: getting a passport for your own child. Passport offices have routinely demanded the consent and signature of both parents — even when one has vanished, refuses to cooperate, or is locked in a matrimonial dispute. The Andhra Pradesh High Court has now reaffirmed, in clear terms, that this insistence is unlawful.

Justice Battu Devanand held that a single parent is entitled to apply for a passport for a minor child without the consent or signature of the other parent, provided the declarations prescribed under the Passport Rules are furnished. The Court directed the passport authorities to process the application and issue the child's passport within the stipulated time.

## What the Court Said

The ruling rested on a principle the judiciary has stated repeatedly: neither the Passports Act, 1967 nor the Passport Rules, 1980 bar a single parent from seeking a minor's passport without the other parent's consent. The framework already anticipates exactly this situation. A parent who cannot obtain the other's consent can file a declaration — known as Annexure C — affirming that no court order prohibits the issuance and that the child is in their custody.

"It would be unreasonable to compel a single parent who is no longer in contact with the other parent to suffer procedural obstacles in securing a passport for a child," the Court observed. Denying a passport in such circumstances, it noted, could infringe fundamental rights under Articles 19 and 21 of the Constitution. The insistence on documents not required by law was, the judge held, simply unjustified.

The Court also leaned on a long constitutional thread. The right to travel abroad has been recognised as part of personal liberty under Article 21 ever since the Supreme Court's landmark ruling in Maneka Gandhi v. Union of India — a precedent that courts across the country continue to invoke when passport authorities take a mechanical, obstructive approach.

## Not an Isolated Ruling

The Andhra Pradesh decision is the latest in a striking run of high court judgments saying the same thing. In recent months the Allahabad High Court held that parental disputes and pending matrimonial or criminal matters between parents are not grounds to deny a minor a passport, noting that Section 6 of the Passports Act exhaustively lists the limited reasons — national security, pending criminal proceedings, specific court orders — for which an application can be refused. Parental discord is not on that list.

The Telangana High Court has ordered passports issued to infants for urgent medical travel without paternal consent. The Madhya Pradesh High Court reached a similar conclusion in a custody dispute. Together, the rulings form a consistent body of law: where the prescribed declarations are filed and no court has issued a prohibitory order, the passport office cannot sit on an application indefinitely.

## Why the Diaspora Should Pay Attention

For the Indian diaspora, this is far from academic. NRI families are full of cross-border custody arrangements, separations that span continents, and single parents who need to move a child quickly — for school admissions abroad, for medical treatment, to reunite with a parent who has already emigrated. In many of these cases the other parent is unreachable, uncooperative, or actively obstructing travel.

Until now, a passport clerk's demand for the absent father's signature could freeze a child's entire future in place. These rulings hand single parents a concrete tool: file the Annexure C declaration, ensure no prohibitory court order exists, and the passport office is legally bound to act.

The practical advice flowing from the judgment is straightforward. A single parent applying for a minor's passport should submit the prescribed annexures — typically Annexure C and the supporting declaration — and, if the application stalls, cite this growing line of high court authority. The courts have made the legal position unambiguous; the remaining gap is enforcement at the counter, where awareness of the rules is still uneven.

For estranged and single parents in the diaspora, the message from Amaravati is reassuring: your child's passport is not hostage to a signature you cannot get.

**Sources:** Andhra Pradesh High Court (Shaik Shabana v. Union of India), LiveLaw, ApniLaw, Allahabad High Court rulings (LiveLaw), Telangana High Court / O.P. Jindal Child Rights Clinic"""

    article = {
        "headline": "A Single Mother Can Now Get Her Child an Indian Passport Without the Father's Signature. The Andhra Court Just Said So.",
        "subheadline": "Justice Battu Devanand ruled that the prescribed declarations are enough — no paternal consent required. It joins a growing line of high court judgments protecting single parents.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-rights",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Cross-border custody and long-distance separations are common in NRI families; the ruling gives single parents abroad a clear path to obtain a child's passport without an uncooperative ex's signature.",
        "sources": ["Andhra Pradesh High Court (Shaik Shabana v. Union of India)", "LiveLaw", "ApniLaw", "Allahabad High Court (LiveLaw)", "Telangana High Court / Child Rights Clinic"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"VIDESHI NEWS WRITER — {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = []
    results.append(("Germany transit visa", write_article_1()))
    results.append(("Delhi B&B fire", write_article_2()))
    results.append(("AP HC passport ruling", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'✓ SUCCESS' if success else '✗ FAILED'}: {name}")
    print(f"{'='*60}\n")
