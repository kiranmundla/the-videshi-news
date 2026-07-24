#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-28 05:30 PDT
Writes 3 articles:
1. Amazon $48B India investment (AI/cloud data centers)
2. Hyderabad's Donald Trump Avenue (political drama)
3. Supreme Court birthright citizenship ruling (diaspora impact)
"""

import os, sys, json, uuid, re, io, time, subprocess
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                # Handle export VAR=val and VAR=val
                line = line.replace('export ', '', 1)
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ[k.strip()] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import requests
from PIL import Image

# ── helpers ──────────────────────────────────────────────────────────────

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


def upload_image_to_supabase(jpeg_bytes, filename):
    r = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        },
        data=jpeg_bytes,
        timeout=60,
    )
    if r.status_code not in (200, 201):
        print(f"    ⚠ Supabase upload failed {r.status_code}: {r.text[:200]}")
        return None
    return f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"


def download_image(url, timeout=20):
    """Download image, try curl fallback on 429."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=timeout)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
        if r.status_code == 429:
            print(f"    ⚠ 429 from requests, trying curl...")
    except Exception as e:
        print(f"    ⚠ Download error: {e}")
    # curl fallback
    try:
        tmp = f"/tmp/dl_img_{uuid.uuid4().hex[:8]}.jpg"
        result = subprocess.run(
            ["curl", "-sS", "-A", "TheVideshi/1.0 (thevideshi.com)", "-o", tmp, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=30
        )
        code = result.stdout.strip()
        if code == "200" and os.path.exists(tmp) and os.path.getsize(tmp) > 5000:
            with open(tmp, "rb") as f:
                data = f.read()
            os.remove(tmp)
            return data
    except Exception as e:
        print(f"    ⚠ Curl fallback error: {e}")
    return None


def fetch_wikipedia_person_image(person_name):
    import urllib.parse
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
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
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
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


# Relevance gate for Commons
_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use",
}

_COMMONS_NEGATIVE = {
    "us capitol": ["state capitol", "pennsylvania", "texas capitol", "california state",
                   "harrisburg", "albany", "sacramento", "austin capitol"],
    "white house": ["whitehouse station", "white house tennessee"],
    "supreme court": ["state supreme court", "uk supreme court"],
}

def _keywords(text):
    toks = re.findall(r"[A-Za-z][A-Za-z'-]+", text or "")
    return [t.lower() for t in toks if len(t) >= 4 and t.lower() not in _COMMONS_STOP]

def commons_relevance_ok(commons_title, headline, topic=""):
    title_l = (commons_title or "").lower()
    head_l = (headline or "").lower()
    if not title_l:
        return False
    for concept, bad_tokens in _COMMONS_NEGATIVE.items():
        if concept in head_l:
            for bad in bad_tokens:
                if bad in title_l:
                    return False
    kws = set(_keywords(headline)) | set(_keywords(topic))
    if not kws:
        return True
    return any(kw in title_l for kw in kws)


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            # Use landscape medium
            url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("large")
            if url:
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def source_image(person_name, topic_terms, headline, slug):
    """Multi-source image search. Returns (supabase_url, attribution, caption) or (None, None, None)."""
    candidates = []

    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": "high"})

    # Source 2: Wikimedia Commons
    search_terms = f"{person_name} {topic_terms}" if person_name else topic_terms
    commons_results = fetch_wikimedia_commons_images(search_terms)
    if not commons_results and topic_terms != search_terms:
        commons_results = fetch_wikimedia_commons_images(topic_terms)
    # Relevance gate
    commons_results = [r for r in commons_results if commons_relevance_ok(r.get("title", ""), headline, topic_terms)]
    for r in commons_results[:2]:
        candidates.append({"url": r["url"], "source": "wikimedia_commons", "relevance": "medium", "title": r.get("title","")})

    # Source 3: Pexels (topic/scene fallback, NOT for named people)
    if not candidates:
        pexels_img = fetch_pexels_image(topic_terms)
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels", "relevance": "low"})

    if not candidates:
        print(f"  ✗ No image found for '{slug}'")
        return None, None, None

    best = candidates[0]
    print(f"  → Picking {best['source']} image for '{slug}'")

    img_bytes = download_image(best["url"])
    if not img_bytes:
        print(f"  ✗ Failed to download image for '{slug}'")
        return None, None, None

    compressed = compress_image(img_bytes)
    if len(compressed) < 5000:
        print(f"  ✗ Compressed image too small ({len(compressed)} bytes)")
        return None, None, None

    filename = f"{slug}.jpg"
    final_url = upload_image_to_supabase(compressed, filename)
    attribution = "Wikimedia Commons" if best["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
    return final_url, attribution, best.get("title", "")


def sb_insert(table, data):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json=data,
        timeout=30,
    )
    if r.status_code not in (200, 201):
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None
    result = r.json()
    if isinstance(result, list) and result:
        return result[0]
    return result


def sb_patch(table, filters, data):
    filter_str = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{filter_str}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json=data,
        timeout=30,
    )
    if r.status_code not in (200, 201):
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
        return None
    return r.json()


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: Amazon $48B India Investment
# ═══════════════════════════════════════════════════════════════════════

article1 = {
    "headline": "Amazon Just Committed $48 Billion to India. Most of It Will Be Spent Building the AI Infrastructure Indians Haven't Seen Yet.",
    "subheadline": "CEO Andy Jassy met Modi in New Delhi and announced $13 billion in fresh AI and cloud spending — the largest single technology commitment India has ever received.",
    "slug": "amazon-48-billion-india-investment-jassy-modi-ai-cloud-data-centers-mumbai-hyderabad-20260628",
    "category": "news",
    "vertical": "tech",
    "status": "review",
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com"},
        {"name": "Barron's", "url": "https://www.barrons.com"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com"}
    ]),
    "diaspora_angle": "Indian tech professionals in the US who work at Amazon and AWS now have a concrete reason to consider reverse migration — or at least to watch India's cloud market explode from $48 billion in fresh capital.",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "body": """When Amazon CEO Andy Jassy walked into his meeting with Prime Minister Narendra Modi in New Delhi last Thursday, he brought a number that stopped the room: $48 billion. That is how much Amazon plans to pour into India between 2026 and 2030 — a figure that, by itself, exceeds the GDP of more than half the countries in Africa.

The number is not new in its entirety. Amazon had already pledged $35 billion in December 2025. What Jassy announced was an additional $13 billion, earmarked specifically for expanding artificial intelligence and cloud infrastructure. The fresh capital will go toward enlarging AWS data centre capacity in Mumbai and Hyderabad, giving Indian startups, enterprises, and government agencies access to custom AI chips, managed AI services, and the developer tools needed to build at scale.

"India is becoming such a significant cloud and AI hub around the world, and we have so much demand here that we're continuing to invest in the country on the cloud side and the AI side as well," Jassy said after the meeting.

## The Numbers Behind the Bet

The $48 billion breaks down into two broad streams. More than $21 billion — including the newly announced $13 billion — is dedicated to AI and cloud infrastructure alone. The rest flows into Amazon's marketplace business, logistics network, and content operations. Amazon's cumulative investment in India since it first entered the market in 2010 now exceeds $88 billion.

Modi welcomed the announcement on X, writing, "I welcome Amazon's record $48 billion investment in India. This will create new opportunities for our youth."

The scale places Amazon alongside — and arguably ahead of — its hyperscaler competitors in the race for India. Microsoft committed $17.5 billion to Indian data centres last year. Alphabet-owned Google announced $15 billion over five years for data centre expansion in southern India. Amazon's $21 billion in AI and cloud alone now exceeds both.

## Why India, Why Now

The timing is not accidental. India's AI market is expanding at a compound annual growth rate that most forecasters put north of 25 percent. The US government's recent restrictions on frontier AI model access — which briefly cut Indian developers off from Anthropic's latest tools — have accelerated Delhi's push for sovereign AI capability. India's ₹10,372-crore AI Mission has already backed 12 startups, including India's first AI unicorn Sarvam, with GPU allocations and cash grants.

Amazon's bet is that demand for cloud compute in India will be structurally higher than what the market currently reflects. AWS already serves the National Health Authority, the Government e-Marketplace, HDFC Bank, Axis Bank, and hundreds of startups. The Hyderabad expansion, in particular, is designed to serve the dense cluster of IT services firms, defence contractors, and pharmaceutical companies that have turned the city into India's second technology capital.

## The Jobs and Education Play

Amazon is also staking out ground beyond infrastructure. The company says it will support 3.8 million jobs in India by 2030 and enable $80 billion in cumulative e-commerce exports. It has pledged to extend AI benefits to 15 million small businesses and provide AI education to 4 million government school students by the end of the decade.

These are corporate-ambition numbers, and they should be read with the scepticism such figures deserve. But the capital commitment behind them is real. Amazon has already digitised 12 million small businesses in India, enabled more than $20 billion in cumulative e-commerce exports, supported 2.8 million jobs, and trained over 10 million Indians in cloud skills.

## What This Means for the Diaspora

For Indian tech professionals working in the US, the announcement reshapes the calculus of opportunity. AWS India is no longer a satellite operation running a regional availability zone. It is becoming a primary market, with custom AI hardware and a talent pipeline that Amazon is actively investing to build. The reverse brain drain that has been discussed in abstract terms now has a $48 billion number attached to it.

For NRI investors, the signal is equally clear. India's data centre real estate market — concentrated in Mumbai, Hyderabad, and Chennai — is about to absorb an unprecedented wave of construction. The firms building and servicing those facilities, from power generation to cooling systems, will see demand they have never encountered before.

Jassy's visit to Modi was, at one level, a courtesy call. At another, it was the moment when India's AI infrastructure stopped being a theoretical priority and became a capital expenditure line item with a nine-figure dollar sign in front of it."""
}

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Hyderabad's Donald Trump Avenue
# ═══════════════════════════════════════════════════════════════════════

article2 = {
    "headline": "Hyderabad Named a Road After Trump. His Own Allies in India Called It Hypocrisy.",
    "subheadline": "A Congress-ruled state honours the US president with 'Donald Trump Avenue' near the US Consulate — while accusing Modi of being too soft on him.",
    "slug": "hyderabad-donald-trump-avenue-telangana-congress-bjp-us-india-20260628",
    "category": "news",
    "vertical": "geopolitics",
    "status": "review",
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Mandatory", "url": "https://www.mandatory.com"},
        {"name": "LiveMint", "url": "https://www.livemint.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"}
    ]),
    "diaspora_angle": "For NRIs from Hyderabad — and there are hundreds of thousands of them, particularly in the US tech industry — the irony of their city naming a road after a president who has raised tariffs on Indian goods, whose navy killed Indian sailors, and whose immigration policies threaten H-1B holders is impossible to miss.",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "body": """There is now a Donald Trump Avenue in Hyderabad, India. It runs alongside the US Consulate in the city's Financial District, a stone's throw from the offices of Microsoft, Google, and Amazon. The road was renamed on June 23 at a gala event called Freedom 250, hosted to mark the 250th anniversary of American independence. US Ambassador to India Sergio Gor and Telangana Deputy Chief Minister Mallu Bhatti Vikramarka jointly unveiled a ceremonial plaque bearing the new name.

Trump was pleased. "The New Donald J Trump Avenue in Hyderabad, India — The first US President to ever be honoured in this way — Thank you!" he posted on Truth Social on Saturday.

## The Politics Behind the Plaque

What made the gesture noteworthy was not the plaque itself but the political party behind it. Telangana is governed by the Indian National Congress, the main opposition party, which has spent months accusing Prime Minister Narendra Modi of being "compromised" by Trump — of failing to push back on tariffs, of staying silent when US Navy strikes killed Indian sailors during the Iran war, and of not defending Indian workers facing H-1B restrictions.

Modi's Bharatiya Janata Party was quick to pounce. "Rahul Gandhi says President Trump is hurting Indian interests," said BJP spokesperson Shehzad Poonawalla on X. "Then why is his government in Telangana giving the ultimate tribute to him by renaming a road after him?"

The Communist Party of India (Marxist) called the move "outrageous" and demanded its withdrawal.

Congress's defence was pragmatic rather than ideological. The party framed the renaming as a recognition of Hyderabad's "growing role" in the India-US partnership, pointing to the city's status as the second-largest hub for American technology investment in India.

## The Diplomatic Backdrop

The timing was deliberate. The Freedom 250 event took place less than a week after Modi and Trump met on the sidelines of the G7 summit in France, where the two leaders agreed to push forward a trade deal that has been under negotiation for months. Ambassador Gor used his remarks to underscore the economic dimension.

"Nowhere is the high-speed trajectory of our partnership more evident than in Hyderabad. From HITEC City to aerospace and defence, this region represents progress that is defining our bilateral momentum," Gor said.

He went further, tying the gesture to concrete numbers: "With our interim trade agreement and Mission India on track to bring over $20 billion of new investment to the United States, we are proving that America First does not mean America alone."

## A City That Knows Its Leverage

Hyderabad has always played a different game from Delhi. The city is home to the largest concentration of Indian IT services workers, a growing defence corridor, and a pharmaceutical manufacturing cluster that supplies a significant share of the world's generic drugs. Its political class — whether the Telangana Rashtra Samithi that governed the state until 2023 or the Congress government that replaced it — has consistently courted foreign investment with a pragmatism that transcends party ideology.

Naming a road after a sitting foreign president is unusual, but not without precedent in Indian diplomacy. What is unusual is naming it after a president who has never visited the city, whose trade policies have hit Indian exporters with 18 percent tariffs, and whose administration is running a Section 301 probe into alleged overcapacity and forced labour in India.

Trump has not visited Hyderabad during either of his terms in office, though his predecessors Bill Clinton and George W. Bush both did.

## The NRI Angle

For the hundreds of thousands of NRIs from Hyderabad — particularly those working in the American technology industry — the move sits at the intersection of irony and realpolitik. The road that now carries Trump's name leads past the offices of companies whose Indian employees are directly affected by the H-1B restrictions and tariff walls his administration has erected.

But realpolitik has its own logic. Telangana wants investment. The US wants market access. And a road sign, it turns out, is a very cheap way to signal willingness to deal."""
}

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 3: Supreme Court Birthright Citizenship Ruling
# ═══════════════════════════════════════════════════════════════════════

article3 = {
    "headline": "The Supreme Court Is About to Rule on Whether Babies Born to H-1B Parents Are American Citizens",
    "subheadline": "A decision expected as early as Monday could strip birthright citizenship from hundreds of thousands of children born each year to parents on temporary visas — including the quarter-million Indians on H-1B status.",
    "slug": "supreme-court-birthright-citizenship-h1b-indian-parents-14th-amendment-ruling-20260628",
    "category": "nri-world",
    "vertical": "immigration",
    "status": "review",
    "is_editorial": False,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "USA Today", "url": "https://www.usatoday.com"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com"},
        {"name": "CNN", "url": "https://www.cnn.com"},
        {"name": "Arizona Republic", "url": "https://www.azcentral.com"}
    ]),
    "diaspora_angle": "This ruling directly affects the quarter-million Indians currently on H-1B visas in America and their families — if upheld, babies born to H-1B holders in the US would not be American citizens, potentially leaving them stateless.",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "body": """The most consequential immigration case in a generation is about to be decided, and Indian families in America are at the centre of it.

The US Supreme Court is expected to rule as early as Monday on President Donald Trump's executive order that would deny birthright citizenship to children born in the United States if neither parent is an American citizen or legal permanent resident. The order, signed on Trump's first day back in office in January 2025, has been on hold since lower courts blocked it. Now the nine justices will have the final word.

If upheld, the ruling would affect an estimated 320,000 babies born each year to parents who are either undocumented or on temporary visas — a category that includes the roughly 250,000 Indian nationals currently holding H-1B work visas, along with those on L-1, F-1, and other non-immigrant statuses.

## What the Order Says

Trump's executive order instructed federal agencies not to recognise US citizenship for any child born in America on or after February 19, 2025, if the mother is an unauthorised immigrant or on a temporary visa and the father is not a citizen or lawful permanent resident. The language is sweeping: it covers H-1B workers, international students, tourists, and any other temporary visa category.

The constitutional question hinges on the 14th Amendment's Citizenship Clause, ratified in 1868, which states: "All persons born or naturalized in the United States, and subject to the jurisdiction thereof, are citizens of the United States." For more than 150 years, this has been interpreted to grant automatic citizenship to virtually anyone born on US soil, with narrow exceptions for the children of foreign diplomats or members of an enemy occupying force.

Trump's administration argues that "subject to the jurisdiction thereof" should be read more narrowly — that it should not apply to people who owe allegiance to another country and are in the United States only temporarily.

## What Legal Experts Expect

Most constitutional scholars consider the executive order a long shot. The lower courts that blocked it found it "inconsistent with the Constitution's 14th Amendment." During oral arguments in April, even some conservative justices appeared sceptical.

"The Constitution is quite clear," said David Leopold, chair of the immigration practice at UB Greensfelder. "Anybody who's born in the United States and under the jurisdiction of the United States is a US citizen. Period, end of story."

But the court has a 6-3 conservative majority, and Trump took the extraordinary step of personally attending oral arguments — a move without modern precedent for a sitting president. The court gave him two major immigration wins on Thursday, upholding his border "metering" policy and allowing the end of Temporary Protected Status for Haitians and Syrians. Both were decided 6-3 along ideological lines.

## The Stakes for Indian Families

The Indian community in America is uniquely exposed. Indians are the largest single nationality among H-1B visa holders, accounting for roughly 70 percent of approvals in recent years. Many H-1B families have been in the United States for a decade or more, stuck in the green card backlog that can stretch to 30 years for Indian nationals due to per-country caps.

Their children, born in American hospitals, attending American schools, speaking English as a first language, have always been citizens. If the court upholds Trump's order, those born after February 2025 would not be.

"People are panicked," immigration attorney David Leopold told Bloomberg Law. "Employees are going to be desperate for information."

The executive order does not specify what status these children would hold. They would not automatically receive their parents' visa status. In many cases, they would be stateless — citizens of neither the United States nor India, since India does not grant citizenship by descent to children born abroad unless at least one parent is an Indian citizen at the time of birth, and many H-1B holders have already surrendered Indian passports for OCI cards.

## The Healthcare Dimension

There is a dimension to the case that received little attention during oral arguments: healthcare. Newborns in the United States routinely receive tests within hours of birth — for jaundice, heart defects via pulse oximetry, and rare metabolic conditions through a heel prick. These tests are administered through programmes tied to citizenship or legal status.

"Kids are sort of the afterthought with all of this," said Bruce Lesley, president of First Focus on Children, a bipartisan children's policy organisation. "They kept sitting around talking about allegiance and all this BS, but the people this affects are babies. The harm is to babies."

If birthright citizenship is stripped, hospitals would face immediate uncertainty about which newborns qualify for Medicaid coverage and which do not. The Migration Policy Institute estimates that upholding the order would add 2.7 million people to the unauthorised population by 2045 and 5.4 million by 2075.

## What Happens Next

The Supreme Court has set Monday, June 29, as its next day to issue rulings. The birthright citizenship case is among the final few remaining before the term ends, which is expected no later than July 2. Legal analysts widely expect the court to strike down Trump's order — but after Thursday's 6-3 immigration rulings, nothing is certain.

For Indian families across America, the next few days will determine whether the citizenship their American-born children have always held was a constitutional right or a policy that one executive order can take away."""
}

# ═══════════════════════════════════════════════════════════════════════
# IMAGE SOURCING & INSERT
# ═══════════════════════════════════════════════════════════════════════

articles = [
    (article1, "Andy Jassy", "Amazon CEO India investment AI data center", "Andy Jassy meeting Prime Minister Modi in New Delhi"),
    (article2, "Donald Trump", "Donald Trump Avenue Hyderabad road sign India", "The newly unveiled Donald Trump Avenue plaque near the US Consulate in Hyderabad"),
    (article3, None, "US Supreme Court building Washington DC", "The US Supreme Court building in Washington, where a ruling on birthright citizenship is expected this week"),
]

print("=" * 60)
print("Videshi News Writer — 2026-06-28 05:30 PDT")
print("=" * 60)

results = []
for art_data, person, topic, default_caption in articles:
    slug = art_data["slug"]
    print(f"\n{'─' * 40}")
    print(f"Processing: {slug}")
    print(f"{'─' * 40}")

    # Source image
    img_url, attribution, img_title = source_image(person, topic, art_data["headline"], slug)
    if img_url:
        art_data["image_url"] = img_url
        art_data["image_attribution"] = attribution
        art_data["image_caption"] = default_caption
        print(f"  ✓ Image uploaded: {img_url[:60]}...")
    else:
        print(f"  ✗ No image — article will be inserted without hero image")

    # Insert article
    result = sb_insert("p2_articles", art_data)
    if result:
        art_id = result.get("id", "unknown")
        print(f"  ✓ Article inserted: id={art_id}")
        results.append({"id": art_id, "slug": slug, "headline": art_data["headline"]})
    else:
        print(f"  ✗ Failed to insert article: {slug}")

print(f"\n{'=' * 60}")
print(f"DONE — {len(results)} articles inserted")
for r in results:
    print(f"  • {r['slug']}")
print(f"{'=' * 60}")
