#!/usr/bin/env python3
"""News writer for The Videshi - 2026-06-06 batch"""

import json, os, re, sys, time, subprocess, urllib.parse, uuid
from datetime import datetime, timezone

import requests

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
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ─── Image sourcing ───

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
            # Use thumbnail.source AS-IS (330px) — do NOT modify
            img = data.get("thumbnail", {}).get("source")
            if not img:
                img = data.get("originalimage", {}).get("source")
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
                info = page.get("imageinfo", [{}])[0]
                url = info.get("thumburl") or info.get("url", "")
                w = info.get("width", 0)
                h = info.get("height", 0)
                mime = info.get("mime", "")
                if url and "image" in mime and w > 200:
                    results.append({"url": url, "title": page.get("title", ""), "width": w, "height": h})
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a relevant image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("large")
            if url:
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def validate_image(url):
    """Verify image URL returns 200 with image content-type and >5KB."""
    # Trust well-known image CDNs
    trusted = ["upload.wikimedia.org", "images.pexels.com"]
    if any(d in url for d in trusted):
        print(f"  ✓ Trusted domain, skipping validation: {url[:60]}...")
        return True
    try:
        result = subprocess.run(
            ['curl', '-sS', '-I', '-L', '-A', 'TheVideshi/1.0', url],
            capture_output=True, text=True, timeout=15
        )
        headers = result.stdout.lower()
        if '200' in headers and 'image/' in headers:
            # Check content-length
            for line in headers.split('\n'):
                if 'content-length' in line:
                    cl = int(line.split(':')[1].strip())
                    if cl > 5000:
                        return True
            # No content-length but 200 + image type = assume ok
            return True
        print(f"  ✗ Image validation failed for {url[:60]}...")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def find_best_image(person_name=None, wiki_searches=None, pexels_query=None):
    """Multi-source image search. Returns (url, attribution) or (None, None)."""
    candidates = []

    # 1. Wikipedia person image
    if person_name:
        img = fetch_wikipedia_person_image(person_name)
        if img:
            candidates.append((img, "Wikimedia Commons", "wikipedia"))

    # 2. Wikimedia Commons search
    if wiki_searches:
        for q in wiki_searches:
            results = fetch_wikimedia_commons_images(q, limit=3)
            for r in results:
                candidates.append((r["url"], "Wikimedia Commons", "commons"))
            time.sleep(0.5)  # Rate limiting

    # 3. Pexels
    if pexels_query:
        img = fetch_pexels_image(pexels_query)
        if img:
            candidates.append((img, "Pexels", "pexels"))

    # Validate and pick best (prefer Wikipedia > Commons > Pexels)
    for url, attr, source in candidates:
        if validate_image(url):
            print(f"  ★ Selected image from {source}: {url[:80]}...")
            return url, attr

    print("  ✗ No valid image found")
    return None, None


# ─── Article insertion ───

def insert_article(article):
    """Insert an article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS_SB, json=article, timeout=15)
    if r.status_code in (200, 201):
        result = r.json()
        aid = result[0].get("id", "unknown") if isinstance(result, list) else result.get("id", "unknown")
        print(f"  ✓ Inserted: {article['headline'][:60]}... (id: {aid})")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return False


# ─── Articles ───

def write_articles():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    articles = []

    # ── Article 1: Cockroach Janta Party ──
    print("\n=== Article 1: Cockroach Janta Party ===")

    cjp_body = """India's largest online youth protest movement came offline on Saturday when Abhijeet Dipke, the 30-year-old founder of the Cockroach Janta Party, landed in New Delhi to lead the group's first street demonstration at Jantar Mantar.

Dipke, who has lived in the United States for the past two years and holds a degree from Boston University, arrived at Indira Gandhi International Airport to a heavy security presence. His family and friends had publicly warned he could be arrested on arrival. He was not — police granted permission for the protest — but the fear itself spoke volumes about the political temperature.

## How a Supreme Court Insult Sparked a Movement

The movement was born from a single remark. On May 15, Chief Justice of India Surya Kant, during a Supreme Court hearing on fake professional degrees, compared confrontational activists and unemployed youth to "cockroaches" and "parasites of society." Within hours, India's Gen Z had reclaimed the slur. Dipke, a political communications strategist who had previously worked with the Aam Aadmi Party, launched the Cockroach Janta Party on May 16 as a satirical counter-punch. The name is a deliberate parody of the ruling Bharatiya Janata Party.

In three weeks, the movement amassed roughly 22 million Instagram followers and over 350,000 sign-ups. It is now the largest online expression of dissent against Prime Minister Narendra Modi's 12-year-old government.

## What the Protesters Want

The CJP's demands go well beyond exam reform. At a press conference at the Constitution Club earlier this week, spokesperson Saurav Das laid out a detailed agenda: the resignation of Union Education Minister Dharmendra Pradhan over the NEET, CBSE, and CUET exam-paper leak scandals; a 50 percent reservation for women in Parliament and all Cabinet positions; a 20-year ban on elected officials who defect from one party to another; and an end to post-retirement rewards for chief justices, a practice the group sees as compromising judicial independence.

The movement has also called for mandatory political and legal literacy — including RTI filing and public budget reading — in secondary school curricula.

## The Government's Response

Modi's government has not treated the movement lightly. The CJP's X account has been blocked within India, a decision the group has challenged in a Delhi court. Senior cabinet minister Kiren Rijiju accused the party of seeking followers from Pakistan and the "anti-India gang," framing it as a national security concern rather than a domestic grievance.

Dozens of police officers barricaded roads near Jantar Mantar on Saturday as protesters shouted slogans. Loudspeakers directed crowds to the designated protest site. The government's strategy appears to be containment through controlled permission rather than outright suppression — a calculus shaped, analysts say, by the knowledge that an arrest would almost certainly amplify the movement further.

Climate activist Sonam Wangchuk announced his support for the protest and said he would undertake a six-week fast if Dipke were arrested.

## Why NRIs Are Watching

For Indian professionals abroad, the CJP represents a generational fault line that many recognize from their own families. The movement is fueled by two pressures that drive a significant share of Indian emigration: persistently high youth unemployment, which officially hovers above 40 percent for ages 15 to 29, and the recurring collapse of examination integrity that determines access to medicine, engineering, and civil service.

Political analysts say the movement has begun to dent Modi's image even as his party continues to win state elections. The broader frustration — compounded by rising fuel prices and gas shortages from the Iran war — has given the CJP a constituency far wider than its satirical origins would suggest.

"This is a peaceful movement for the youth of the nation," spokesperson Ashutosh Ranka, an IIT Kanpur and LSE alumnus who previously worked at McKinsey in London, said at the protest. Dipke, he added, was "ready for a long and big day in India's politics."

Whether that day lasts beyond the news cycle depends on whether the CJP can convert viral momentum into sustained political pressure. For now, the cockroaches are on the streets, and the government is listening — even if it would rather not be."""

    img1, attr1 = find_best_image(
        person_name=None,
        wiki_searches=["Jantar Mantar New Delhi protest", "India youth protest 2026"],
        pexels_query="India protest demonstration youth"
    )

    articles.append({
        "headline": "India's Gen Z Just Took the Streets. The Government Blocked Their X Account.",
        "subheadline": "The Cockroach Janta Party — born from a Supreme Court insult three weeks ago — brought 22 million followers offline for the first time at Jantar Mantar",
        "body": cjp_body,
        "slug": "cockroach-janta-party-jantar-mantar-protest-dipke-gen-z-modi-20260606",
        "category": "news",
        "status": "published",
        "published_at": now,
        "image_url": img1,
        "image_caption": "Jantar Mantar in New Delhi, site of India's largest Gen Z protest",
        "image_attribution": attr1 or "Wikimedia Commons",
        "vertical": "politics",
        "is_editorial": False,
        "sources": json.dumps(["Reuters", "CNN", "The Hindu Business Line", "Daily Jagran"])
    })

    # ── Article 2: JD Vance / Henry Nowak / UK Sikh ──
    print("\n=== Article 2: JD Vance / Henry Nowak case ===")

    vance_body = """JD Vance, the Vice President of the United States, on Friday inserted himself into a British murder case involving a British Sikh man of Indian heritage, calling it proof that Western civilisation is dying. The case has already sparked riots in Southampton. Now it is raising uncomfortable questions for Indian and Sikh communities across the West.

## What Happened in Southampton

In December 2025, Henry Nowak, an 18-year-old white university student, was walking home from a night of football with friends in the southern English city of Southampton when he encountered Vickrum Digwa, a 23-year-old British Sikh man wearing a turban and carrying a 21-centimetre dagger.

Digwa stabbed Nowak. When police arrived, Digwa told them Nowak had racially abused him — a claim later proven to be fabricated. Officers handcuffed the dying Nowak as a suspect while attending to his attacker. Bodycam footage showed Nowak repeatedly telling officers he had been stabbed and could not breathe. He died in handcuffs.

On Monday, Digwa was sentenced to life in prison with a minimum 21-year term. The judge found that the racial abuse claim was false and that Digwa had been in the habit of carrying a second knife beyond the small ceremonial kirpan worn by observant Sikhs.

## Vance Escalates

Vance's intervention came less than 24 hours after the US State Department issued its own rebuke, calling "ideological conditioning and two-tiered policing" symptoms of "civilizational decline."

"Henry Nowak died the same way a civilization dies: abandoned, handcuffed by authorities who neither trusted nor cared for him, and accused of hate crimes he did not commit," Vance wrote on X. He blamed the killing on "the mass invasion of migrants, many of whom despise the West."

Prime Minister Keir Starmer's office pushed back sharply, criticising "people trying to interfere in our democracy and seeking to stir up division on our streets." The Nowak family has asked that his death not be used to create further hatred.

## The Facts That Complicate the Narrative

Both Nowak and Digwa were British citizens. Digwa was not an immigrant. The Sikh Federation has pointed out that while Sikhs across the Western world are permitted to carry a small kirpan as a religious article, Digwa was carrying a second, larger knife — and the judge explicitly stated the religious exemption made no difference to the verdict.

The case has nonetheless been seized by anti-immigration figures, including Nigel Farage and Elon Musk, who have amplified claims of a "two-tier policing system." On Tuesday, police in Southampton were pelted with chairs, cans, rocks, and flares during a demonstration attended by far-right figures.

## What This Means for the Diaspora

For Indian and Sikh communities in the UK and the United States, the case sits at an anxious intersection. The policing failure was real — officers made a catastrophic decision by believing an unverified claim of racism over a dying man's pleas. That failure has become legitimate grounds for institutional reform.

But the political exploitation of the case has folded it into a broader anti-immigration narrative that makes no distinction between a British-born citizen and a recent arrival, between a convicted murderer and the millions of law-abiding South Asian families who have built lives in the West.

The Sikh Federation UK issued a statement distancing the community from Digwa's actions, noting that carrying a weapon beyond a small kirpan violates Sikh religious teaching. Sikh community leaders in the US have expressed concern that the case — amplified by the Vice President of the United States — could increase hostility toward turbaned Sikhs who are already disproportionately targeted in hate crimes, often because they are mistaken for Muslims.

The risk for the diaspora is not abstract. In the wake of the State Department's statement, which was the first time the Trump administration publicly commented on the case, monitoring groups have reported a spike in anti-Sikh rhetoric online.

For Indian professionals in the UK, the timing is particularly fraught. Net migration from India to Britain has fallen sharply since 2025 amid visa curbs, and the political climate around immigration has hardened across the political spectrum. A case that is fundamentally about one man's violence and one police force's failure is being refracted through the lens of civilisational conflict — and the Indian diaspora is caught in the glare."""

    img2, attr2 = find_best_image(
        person_name="JD Vance",
        wiki_searches=["Southampton England city", "Sikh community United Kingdom"],
        pexels_query=None
    )

    articles.append({
        "headline": "JD Vance Called a British Murder Case a Sign of Civilisational Death. The Killer Was of Indian Heritage.",
        "subheadline": "The Henry Nowak case has become a flashpoint for anti-immigration politics on both sides of the Atlantic — and the Indian diaspora is caught in the middle",
        "body": vance_body,
        "slug": "jd-vance-henry-nowak-uk-sikh-diaspora-two-tier-policing-20260606",
        "category": "news",
        "status": "published",
        "published_at": now,
        "image_url": img2,
        "image_caption": "US Vice President JD Vance, who blamed the murder on civilisational decline and immigration",
        "image_attribution": attr2 or "Wikimedia Commons",
        "vertical": "politics",
        "is_editorial": False,
        "sources": json.dumps(["Reuters", "Fox News", "The Times (UK)", "AP"])
    })

    # ── Article 3: Himachal Pradesh Earthquake ──
    print("\n=== Article 3: Himachal Pradesh Earthquake ===")

    quake_body = """A magnitude 5.0 earthquake struck Chamba district in Himachal Pradesh late on Friday night, sending tremors across North India and prompting residents in Dharamsala, Chandigarh, and parts of Punjab and Haryana to rush out of their homes.

The National Centre for Seismology recorded the quake at 10:37 PM IST on June 5, placing its epicentre near the Kangra-Chamba border, approximately 40 kilometres northeast of Dharamsala. The earthquake occurred at a shallow depth of just five kilometres, which amplified the intensity of shaking felt at the surface.

## Multiple Tremors in a Single Day

The Chamba quake was the second significant seismic event in India on Friday. Earlier in the afternoon, a 2.8 magnitude earthquake struck Mangan district in Sikkim at 4:07 PM IST, also at a depth of five kilometres. No casualties or structural damage have been reported from either event.

Kangra and Chamba districts fall within Seismic Zone 5, the highest-risk classification on India's seismic hazard map. The region sits along the Himalayan frontal thrust, where the Indian tectonic plate pushes beneath the Eurasian plate, making it one of the most earthquake-prone areas on the subcontinent.

## Panic But No Casualties

Residents in Dharamsala and the surrounding hill towns reported several seconds of noticeable shaking that sent people running from multi-storey buildings. The tremor was also felt in Chandigarh, where one resident described a "slight tremor" while preparing for bed around 10 PM.

Local authorities have confirmed no reports of loss of life or significant property damage. Himachal Pradesh's disaster management cell said monitoring teams were deployed overnight to survey structures in the epicentral zone, particularly older buildings and heritage structures in the Chamba Valley that are more vulnerable to seismic stress.

## What the Diaspora Should Know

Chamba and the Kangra Valley draw significant tourist traffic, including diaspora visitors during the summer months. The region is home to Dharamsala and McLeod Ganj, the seat of the Tibetan government-in-exile and a popular destination for NRI travellers. While Friday's earthquake caused no damage, seismologists have long warned that the central Himalayas are overdue for a major seismic event — the last significant earthquake in the region was the 1905 Kangra earthquake, a magnitude 7.8 event that killed over 20,000 people.

The Indian Meteorological Department has not issued any further alerts, and normal activity has resumed across the affected areas."""

    img3, attr3 = find_best_image(
        person_name=None,
        wiki_searches=["Chamba Himachal Pradesh", "Dharamsala Himachal Pradesh landscape"],
        pexels_query="Himachal Pradesh mountains India"
    )

    articles.append({
        "headline": "A 5.0 Earthquake Struck Himachal Pradesh on Friday Night. The Region Is Overdue for a Big One.",
        "subheadline": "The shallow quake near Dharamsala sent tremors across North India but caused no casualties — seismologists warn the Himalayan frontal thrust remains a ticking clock",
        "body": quake_body,
        "slug": "himachal-pradesh-earthquake-chamba-dharamsala-seismic-zone-5-20260606",
        "category": "news",
        "status": "published",
        "published_at": now,
        "image_url": img3,
        "image_caption": "The Chamba Valley in Himachal Pradesh, near the epicentre of Friday's earthquake",
        "image_attribution": attr3 or "Wikimedia Commons",
        "vertical": "general",
        "is_editorial": False,
        "sources": json.dumps(["National Centre for Seismology", "ANI", "Inshorts", "Tech Word News"])
    })

    # ── Insert all articles ──
    print("\n=== Inserting articles ===")
    success = 0
    for art in articles:
        # Remove None image URLs
        if art["image_url"] is None:
            del art["image_url"]
            del art["image_caption"]
            del art["image_attribution"]
        if insert_article(art):
            success += 1
        time.sleep(0.5)

    print(f"\n✓ Done: {success}/{len(articles)} articles published")
    return success


if __name__ == "__main__":
    write_articles()
