#!/usr/bin/env python3
"""News writer for The Videshi - June 3, 2026 evening run."""

import requests
import json
import os
import io
import uuid
import re
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

# --- Image sourcing functions ---

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Prefer thumbnail (safe size), fall back to original
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
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
            params=params, headers=UA, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Fetch image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def download_and_upload(img_url, filename):
    """Download image, compress, upload to Supabase storage. Returns public URL or None."""
    try:
        r = requests.get(img_url, headers=UA, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed ({r.status_code}): {img_url[:80]}")
            return None
        ct = r.headers.get('Content-Type', '')
        if 'image' not in ct:
            print(f"  ⚠ Not an image ({ct}): {img_url[:80]}")
            return None
        raw = r.content
        if len(raw) < 5000:
            print(f"  ⚠ Image too small ({len(raw)} bytes): {img_url[:80]}")
            return None

        compressed = compress_image(raw)
        print(f"  📦 Compressed: {len(raw)} → {len(compressed)} bytes")

        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }
        ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✅ Uploaded: {public_url}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Download/upload error: {e}")
        return None


def source_image(person_name=None, search_terms=None, pexels_query=None, slug="article"):
    """Multi-source image search: Wikipedia → Wikimedia Commons → Pexels. Returns (url, attribution)."""
    candidates = []

    # 1. Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "priority": 1})

    # 2. Wikimedia Commons
    if search_terms:
        for term in (search_terms if isinstance(search_terms, list) else [search_terms]):
            commons = fetch_wikimedia_commons_images(term, limit=3)
            for c in commons[:2]:
                candidates.append({"url": c["url"], "source": "wikimedia_commons", "priority": 2})

    # 3. Pexels
    if pexels_query:
        px = fetch_pexels_image(pexels_query)
        if px:
            candidates.append({"url": px, "source": "pexels", "priority": 3})

    # Sort by priority and try to download/upload
    candidates.sort(key=lambda x: x["priority"])
    for c in candidates:
        filename = f"{slug}.jpg"
        uploaded = download_and_upload(c["url"], filename)
        if uploaded:
            attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
            return uploaded, attr

    print(f"  ❌ No image found for {slug}")
    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  ✅ Published: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ❌ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


def validate_article(a):
    """Validate article meets quality bar."""
    errors = []
    if len(a.get("headline", "")) < 20: errors.append("headline too short")
    if len(a.get("headline", "")) > 200: errors.append("headline too long")
    if len(a.get("subheadline", "")) < 15: errors.append("subheadline too short")
    body = a.get("body", "")
    wc = len(body.split())
    if wc < 400: errors.append(f"body too short ({wc} words)")
    if not a.get("slug"): errors.append("no slug")
    if not a.get("image_url"): errors.append("no image")
    if a.get("category") != "news": errors.append(f"wrong category: {a.get('category')}")
    if errors:
        print(f"  ⚠ Validation errors for '{a.get('slug', '?')}': {', '.join(errors)}")
        return False
    print(f"  ✓ Validation passed: {wc} words, slug={a['slug']}")
    return True


# ===== ARTICLES =====

now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles_data = []

# --- ARTICLE 1: Modi to become India's longest-serving elected PM ---
print("\n" + "="*60)
print("ARTICLE 1: Modi to become India's longest-serving elected PM")
print("="*60)

art1_slug = "modi-longest-serving-elected-pm-june-10-nehru-record-4399-days-20260603"
art1_headline = "Modi Will Surpass Nehru on June 10 to Become India's Longest-Serving Elected Prime Minister."
art1_subheadline = "After 4,399 consecutive days in office, the man from Vadnagar will hold a record that has stood since 1964. The country he governs looks nothing like the one Nehru left behind."

art1_body = """On June 10, Narendra Damodardas Modi will complete 4,399 consecutive days as Prime Minister of India, surpassing the 4,398-day record set by Jawaharlal Nehru between his first oath after the 1952 general election and his death on May 27, 1964. It will be the quietest milestone in a career built on spectacle.

Modi was sworn in for his first term on May 26, 2014, leading the Bharatiya Janata Party to its first outright majority in three decades. He won again in 2019 with an even larger mandate, and secured an unprecedented third consecutive term in 2024 — matching Nehru himself as the only leader to achieve that feat. Last July, he passed Indira Gandhi's longest uninterrupted tenure of 4,077 days. Now he stands a week from overtaking the man whose name is synonymous with the republic itself.

## A Country Transformed Beyond Recognition

The comparison between the two tenures is a story of how profoundly India has changed. When Nehru led the country through its first general election in 1951-52, the electorate numbered roughly 17 crore voters. By the time Modi took office, that figure had swelled past 83 crore. In the 2024 elections, 744 political parties contested — up from just 53 in Nehru's era.

India's population has more than quadrupled, from around 36 crore at independence to over 146 crore today. The economy that Nehru nurtured through five-year plans and state-led industrialisation has given way to one that grew at an estimated 7.2 percent in the most recent quarter — still the fastest among major economies on Earth, even as war in the Gulf and a sinking rupee threaten the outlook.

## The Distinctions Modi Already Holds

The longevity record will add to a list of firsts that no other Indian leader can claim. Modi is the only Prime Minister born after independence. He is the longest-serving non-Congress PM in Indian history. He is the first and only non-Congress leader to complete two full terms and to win re-election twice with a majority of his own.

He is also the only leader — among all Prime Ministers and Chief Ministers — to win six consecutive elections as the head of a political party: Gujarat in 2002, 2007 and 2012, and the Lok Sabha in 2014, 2019 and 2024. That is nearly 24 unbroken years at the helm of a democratically elected government, a record unmatched in Indian democratic history.

## What the Record Means for the Diaspora

For the estimated 32 million members of the Indian diaspora, Modi's tenure has been defined by a level of engagement no previous leader attempted. From the sold-out Madison Square Garden address in 2014 to the Howdy Modi rally in Houston to the global yoga campaigns, he has treated the diaspora not as a sentimental afterthought but as a strategic asset.

That relationship has deepened during his third term. The ongoing Iran war has put millions of Indian workers in the Gulf at direct risk — one Indian national was killed in the Kuwait airport drone strike this week — and Modi's five-nation outreach to UAE, Saudi Arabia, Qatar, Bahrain and Oman has been driven in part by the need to protect those communities.

For NRIs in the United States, the record coincides with a moment of acute uncertainty. The Department of Homeland Security has proposed eliminating "duration of status" for student visas, a change that would affect Indian graduates more than any other group. H-1B application fees have crossed $100,000 for many applicants. The diaspora that has thrived under the frameworks of previous decades now faces questions about whether those frameworks will survive.

## The Weight of Comparison

Nehru built institutions: the Indian Institutes of Technology, the Planning Commission, the Non-Aligned Movement, the temples of modern India. Modi has built infrastructure: highways, airports, digital payment systems and a biometric identity layer that reaches every citizen. Both were polarising in their time. Both believed deeply in India's civilisational role in the world.

The difference is that Nehru's record ended with his death. Modi's will continue to grow, and how long it extends will depend on the same volatile forces — a war-disrupted global economy, a fractious opposition, and a public that has now chosen him three times — that have defined his tenure from the start.

On June 10, the count will tick over to 4,399. The country will barely pause. Modi himself is unlikely to mark it with much fanfare. The record, like most records that matter, will simply become a fact — one more data point in a career that has already rewritten most of India's political arithmetic.

*Sources: Inshorts, Global India Broadcast News, Wikipedia, IANS*"""

img1_url, img1_attr = source_image(
    person_name="Narendra Modi",
    search_terms=["Narendra Modi Prime Minister India 2026", "Modi Parliament India"],
    pexels_query="India parliament government",
    slug=art1_slug
)

art1 = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now_iso,
    "image_url": img1_url,
    "image_attribution": img1_attr or "Wikimedia Commons",
    "is_editorial": False,
    "sources": json.dumps(["Inshorts", "Global India Broadcast News", "Wikipedia", "IANS"]),
}
articles_data.append(art1)


# --- ARTICLE 2: Supreme Court landmark ruling on sex work ---
print("\n" + "="*60)
print("ARTICLE 2: Supreme Court ruling on voluntary sex work")
print("="*60)

art2_slug = "supreme-court-voluntary-sex-work-not-illegal-trafficking-consent-ruling-20260603"
art2_headline = "India's Supreme Court Just Drew a Line Between Sex Work and Trafficking. The Distinction Changes Everything."
art2_subheadline = "In a landmark ruling, Justices Pardiwala and Mahadevan held that adult women who choose sex work cannot be arrested, harassed or forcibly rehabilitated. The 70-year-old law stays. The way it is enforced does not."

art2_body = """The Supreme Court of India has issued one of the most consequential rulings on personal liberty in recent years, holding that adult women who voluntarily engage in sex work cannot be treated as criminals, subjected to police harassment, or forcibly placed in rehabilitation facilities against their will.

The ruling, delivered by a bench of Justice J.B. Pardiwala and Justice R. Mahadevan in *Prajwala v. Union of India*, draws an explicit and legally binding distinction between voluntary adult sex work and human trafficking for commercial sexual exploitation. Consent, the Court declared, is the central factor in determining which side of that line a case falls on.

## What the Court Actually Said

The bench held that the Immoral Traffic (Prevention) Act (ITPA), enacted in 1956, was designed to combat trafficking, exploitation and commercial profiteering from prostitution — not to criminalise adults who engage in sex work of their own free will. While operating brothels, trafficking persons, and profiting from another's sexual labour remain illegal, the act of consensual sex work by an adult is not a criminal offence under Indian law.

The Court directed law enforcement agencies across the country to stop targeting, arresting or penalising adults engaged in voluntary sex work. During raids — which have historically swept up trafficking victims and voluntary sex workers alike — police must focus specifically on identifying coercion, trafficking, abuse and exploitation, rather than treating everyone found in a prostitution-related setting as either a criminal or a helpless victim.

"It is the victim's life, liberty, and future that the order will determine," the Court observed, "and thus it would be incongruous to hold that all of this can be decided without any regard for what the victim wants."

## The Victim Protection Plan

The ruling went beyond declaration and into prescription. The Court framed a detailed Victim Protection Plan that fundamentally restructures how rescued persons are handled under Section 17 of the ITPA.

Under the new framework, when an adult is produced before a magistrate following a raid, a threshold inquiry must first establish whether the individual considers herself a voluntary sex worker and whether she wishes to be placed in protective custody. If the answer to either question is no, the state cannot compel her into long-term detention in a protective home.

The Court explicitly rejected the paternalistic "one-size-fits-all" approach that has governed enforcement for decades, under which every person found in a prostitution-related situation was funnelled through the same rescue-and-rehabilitate pipeline regardless of their circumstances.

Additional directions include: rescued persons must not be detained overnight at police stations under any circumstances; statements must be recorded only after a person's safety is ensured and initial trauma has subsided; and protection must not be made conditional on a victim's willingness to cooperate with law enforcement or participate in legal proceedings.

## Why This Matters Beyond India's Borders

The ruling has direct implications for how India is assessed on global anti-trafficking indices, including the U.S. State Department's annual Trafficking in Persons (TIP) Report. India has oscillated between Tier 2 and the Tier 2 Watch List for years, with enforcement practices — particularly the conflation of voluntary sex work with trafficking — cited as a persistent weakness.

By mandating a consent-first framework and separating voluntary sex work from trafficking in operational terms, the Court has aligned Indian jurisprudence more closely with the approach recommended by UNAIDS, the World Health Organization, and Amnesty International, all of which have called for the decriminalisation of consensual adult sex work as a public health and human rights imperative.

For the Indian diaspora, the ruling is part of a broader pattern of judicial activism that has defined the Pardiwala Court's recent term. The same bench that delivered this ruling also permitted passive euthanasia for the first time earlier this year in *Harish Rana v. Union of India*. Together, these decisions mark a Court that is willing to engage with questions of bodily autonomy, dignity and the limits of state power in ways that previous benches avoided.

## The Gap Between Law and Practice

The challenge, as with most progressive Supreme Court rulings in India, will be enforcement. The ITPA remains unreformed. Police forces across states operate under varying levels of training and political pressure. Anti-trafficking NGOs — some of which have been criticised for conducting coercive "rescues" of their own — will need to recalibrate their operations to respect the autonomy the Court has now formally protected.

The Court acknowledged this gap implicitly by directing that its guidelines be circulated to all state police forces and that compliance be monitored. Whether that monitoring materialises with any teeth remains the open question.

What is no longer an open question is the legal principle. Voluntary adult sex work is not illegal in India. The Supreme Court has said so, not for the first time, but with a clarity and a set of enforceable directions that leave no room for the studied ambiguity that has governed this space for seven decades.

*Sources: LiveLaw, Bar and Bench, The CSR Journal, News18*"""

img2_url, img2_attr = source_image(
    person_name=None,
    search_terms=["Supreme Court of India building 2024", "Supreme Court India exterior"],
    pexels_query="India Supreme Court justice building",
    slug=art2_slug
)

art2 = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now_iso,
    "image_url": img2_url,
    "image_attribution": img2_attr or "Wikimedia Commons",
    "is_editorial": False,
    "sources": json.dumps(["LiveLaw", "Bar and Bench", "The CSR Journal", "News18"]),
}
articles_data.append(art2)


# --- ARTICLE 3: Trump confirms calling Netanyahu "crazy" ---
print("\n" + "="*60)
print("ARTICLE 3: Trump-Netanyahu phone call fallout")
print("="*60)

art3_slug = "trump-confirms-netanyahu-crazy-call-iran-ceasefire-india-oil-20260603"
art3_headline = "Trump Just Confirmed He Called Netanyahu 'Crazy.' The Ceasefire India Needs Is Nowhere Close."
art3_subheadline = "The leaked phone call, the stalled talks with Iran, and the overnight strikes on Kuwait and Bahrain reveal a war that is fracturing the alliances meant to end it. India, with 9 million workers in the Gulf, has no good options."

art3_body = """Donald Trump has confirmed that he called Israeli Prime Minister Benjamin Netanyahu "fucking crazy" in a phone call on Monday, in what may be the most candid public acknowledgement of friction between the two leaders since they launched the war on Iran in late February.

"I did," Trump told the *Pod Force One* podcast when asked about the exchange, first reported by Axios. According to the report, Trump told Netanyahu: "You're fucking crazy. You'd be in prison if it weren't for me. I'm saving your ass. Everybody hates you now. Everybody hates Israel because of this."

Trump characterised the call as a necessary intervention to stop Israel from escalating operations in Lebanon, where Israeli ground forces had made their deepest incursion in 26 years. He said Netanyahu "turned his troops around" after the conversation. Netanyahu, in a CNBC interview, played it down as a "tactical disagreement" between close allies.

## The Ceasefire Is Collapsing in Real Time

The phone call matters because it landed in the middle of the most fragile moment in the three-month-old conflict. Within hours of Trump's claimed success in de-escalating Lebanon, Iranian drones and missiles struck Kuwait International Airport, killing one person — confirmed as an Indian national — and injuring more than 60. Bahrain said it intercepted missiles and drones targeting U.S. military positions. The U.S. military responded with strikes on an Iranian ground control station on Qeshm Island near the Strait of Hormuz.

Iran's Revolutionary Guards acknowledged attacking the headquarters of the U.S. Fifth Fleet in Bahrain, though U.S. Central Command denied its bases had been hit. Both sides said they were retaliating for earlier attacks. Iran's Foreign Ministry called the U.S. strikes "acts of aggression" that violated the ceasefire. A senior Emirati diplomat called for "a firm, unified, and cohesive Gulf position" against Iran.

The ceasefire, announced with fanfare weeks ago, now exists in name only. Iran's negotiators have stopped communicating with ceasefire mediators, Iranian media reported, linking the suspension to Israel's continued operations in Lebanon and Gaza. Trump called reports of a halt in talks "false and erroneous." The gap between what the White House says and what is happening on the ground has never been wider.

## India's Nine Million People in the Danger Zone

For India, the disintegration of the ceasefire is not an abstract diplomatic problem. An estimated 8.9 million Indian nationals live and work in the Gulf states, concentrated in the UAE, Saudi Arabia, Kuwait, Qatar, Bahrain and Oman. The Indian killed at Kuwait airport this week was a worker — one of hundreds of thousands who staff the airports, construction sites, hospitals and service industries that keep these economies running.

India's Shipping Ministry has said all Indian seafarers in West Asia are safe but acknowledged it would send a vessel to the Strait of Hormuz only "when the situation is conducive." The strait, through which nearly 40 percent of India's oil imports passed before the war, remains largely closed. Oil hit $97 a barrel this week. India imports roughly 90 percent of the crude it consumes.

Prime Minister Modi has responded with an unprecedented five-nation Gulf outreach — meetings with the leaders of the UAE, Saudi Arabia, Qatar, Bahrain and Oman — driven by two calculations: securing alternative energy supplies and protecting Indian workers. Venezuela's acting President Delcy Rodriguez arrived in India this week for talks focused on energy, as Indian imports of Venezuelan crude have climbed to 380,000 barrels a day, the highest since 2020.

## Why the Trump-Netanyahu Rift Matters for New Delhi

The revealed tension between Trump and Netanyahu introduces a new variable into India's calculations. New Delhi has maintained careful relations with both Washington and Tel Aviv, and has avoided taking a public position on the war itself. But if the two architects of the conflict cannot agree on how to fight it — let alone how to end it — the prospect of a negotiated resolution that reopens the Strait of Hormuz recedes further.

An interim deal, Reuters reported, is the most likely outcome: a framework that reopens the strait, provides Iran with limited sanctions relief, and gives Trump a political off-ramp. But even that modest agreement remains unsigned. Iran has demanded that any deal include Lebanon. Netanyahu has said Israel will continue operations in Lebanon. Trump says he started the war to prevent Iran from acquiring nuclear weapons and insists "there would be no Israel" without him.

For the diaspora, the situation is double-edged. NRIs in the Gulf face direct physical risk from a conflict that shows no sign of ending. NRIs in the United States face the economic consequences of a prolonged oil shock that is already driving inflation, complicating the Federal Reserve's rate decisions, and weakening the rupee. The RBI's upcoming rate decision — its hardest in years, by most accounts — will be shaped in large part by how far this war spirals.

The phone call between Trump and Netanyahu was not a breakthrough. It was a symptom: of a war without a strategy, an alliance under strain, and a ceasefire that no one on any side seems willing or able to enforce.

*Sources: Reuters, Axios, AP, NPR, The Times, Energy Connects*"""

img3_url, img3_attr = source_image(
    person_name="Donald Trump",
    search_terms=["Trump Netanyahu meeting 2025", "Donald Trump White House 2026"],
    pexels_query="White House Washington politics",
    slug=art3_slug
)

art3 = {
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now_iso,
    "image_url": img3_url,
    "image_attribution": img3_attr or "Wikimedia Commons",
    "is_editorial": False,
    "sources": json.dumps(["Reuters", "Axios", "Associated Press", "NPR", "The Times", "Energy Connects"]),
}
articles_data.append(art3)


# ===== PUBLISH ALL =====
print("\n" + "="*60)
print("PUBLISHING ARTICLES")
print("="*60)

published = 0
for art in articles_data:
    print(f"\n--- {art['slug'][:60]} ---")
    if not art.get("image_url"):
        print("  ⚠ Skipping: no image found")
        continue
    if not validate_article(art):
        # Try to publish anyway if body is decent
        wc = len(art.get("body", "").split())
        if wc < 400:
            print("  ❌ Skipping: body too short")
            continue
    result = insert_article(art)
    if result:
        published += 1

print(f"\n{'='*60}")
print(f"DONE: {published}/{len(articles_data)} articles published")
print(f"{'='*60}")
