#!/usr/bin/env python3
"""
Videshi Lifestyle-Health & Markets-Finance Writer — 2026-06-03 run
Produces 2 lifestyle-health articles and 1 markets-finance article.
"""

import requests
import json
import os
import io
import uuid
import re
import subprocess
from datetime import datetime, timezone

# --- ENV ---
def load_env(path):
    """Load .env file into os.environ"""
    if not os.path.exists(path):
        print(f"  ⚠ Env file not found: {path}")
        return
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

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- IMAGE SOURCING ---
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
    """Search Wikimedia Commons for CC-licensed images."""
    import urllib.parse
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
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(*queries):
    """Search Pexels for an image using curl (urllib gets 403)."""
    for q in queries:
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image to JPEG."""
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


def download_image(url):
    """Download image bytes from a URL."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code == 200 and r.headers.get('Content-Type', '').startswith('image'):
            if len(r.content) > 5000:
                return r.content
            else:
                print(f"  ⚠ Image too small ({len(r.content)} bytes): {url[:80]}")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None


def upload_to_supabase(img_bytes, filename):
    """Upload compressed image to Supabase storage bucket 'article-images'."""
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    try:
        r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Supabase upload error: {e}")
    return None


def source_image(article_slug, person_name=None, wiki_queries=None, pexels_queries=None):
    """Multi-source image compare. Returns (supabase_url, attribution) or (None, None)."""
    candidates = []

    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": 3})

    # Source 2: Wikimedia Commons
    if wiki_queries:
        for q in wiki_queries:
            results = fetch_wikimedia_commons_images(q, limit=3)
            for r in results[:2]:
                candidates.append({"url": r["url"], "source": "wikimedia_commons", "relevance": 2})
            if results:
                break

    # Source 3: Pexels
    if pexels_queries:
        pexels_img = fetch_pexels_image(*pexels_queries)
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels", "relevance": 1})

    # Pick best
    if not candidates:
        print("  ✗ No image candidates found")
        return None, None

    candidates.sort(key=lambda c: c["relevance"], reverse=True)
    best = candidates[0]
    print(f"  → Selected: {best['source']} image")

    # Download, compress, upload
    raw = download_image(best["url"])
    if not raw:
        # Try next candidate
        for c in candidates[1:]:
            raw = download_image(c["url"])
            if raw:
                best = c
                break
    if not raw:
        print("  ✗ Could not download any candidate image")
        return None, None

    compressed = compress_image(raw)
    size_kb = len(compressed) / 1024
    print(f"  → Compressed to {size_kb:.0f} KB")
    if size_kb < 10:
        print("  ⚠ Compressed image too small, skipping")
        return None, None

    filename = f"{article_slug}.jpg"
    supabase_url = upload_to_supabase(compressed, filename)
    attribution = "Wikimedia Commons" if best["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
    return supabase_url, attribution


def insert_article(article):
    """Insert article into p2_articles."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS_SB, json=article, timeout=20)
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) and result else "unknown"
        print(f"  ✓ Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ============================================================
# ARTICLE 1: Microrobots Repair Spinal Cord Injuries
# ============================================================
def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Microrobots Repair Spinal Cord Injuries")
    print("="*60)

    slug = "microrobots-spinal-cord-injury-repair-eth-zurich-nature-materials-20260603"
    headline = "Scientists Built Living Microrobots That Repaired Spinal Cord Injuries in Mice. India Has One of the Highest Rates of Such Injuries in the World."
    subheadline = "A team at ETH Zurich combined stem cells with magnetoelectric nanoparticles to create tiny machines that can be guided to injury sites and stimulate nerve regrowth. The study, published in Nature Materials, restored movement in paralysed mice within weeks."

    body = """A spinal cord injury is one of the most devastating things that can happen to the human body. Once the nerve fibres are severed, they almost never grow back. Scar tissue forms a wall. The connection between brain and muscle goes dark.

For decades, scientists have tried to bridge that gap using transplanted stem cells and electrical stimulation. The results have been modest at best. The cells often die before they integrate. Implanted electrodes carry infection risks. And getting the treatment precisely where it needs to go remains a fundamental challenge.

Now a team at ETH Zurich has published a study in *Nature Materials* that takes an entirely different approach, one that reads more like science fiction than clinical research. They built living microrobots — biohybrid machines smaller than the width of a human hair — that can be steered through the body using magnets, guided to the exact site of a spinal cord injury, and activated to stimulate nerve regrowth.

## How the Microrobots Work

The researchers combined two components into a single unit they call an NPCbot. The living part consists of neural progenitor cells derived from induced pluripotent stem cells, which are ordinary body cells reprogrammed in the laboratory to regain their developmental potential. These cells can differentiate into neurons and astrocytes, the support cells that maintain the nervous system.

The technical part is a set of magnetoelectric nanoparticles with a layered structure. The inner layer responds to magnetic fields. The outer layer converts that magnetic response into electrical signals. When an external magnetic field is applied, these nanoparticles generate precisely calibrated electrical stimulation that nudges the stem cells toward becoming functional nerve tissue.

The combination is elegant: the magnets allow clinicians to steer the microrobots to the injury site, and the same magnetic field simultaneously stimulates the cells to mature and integrate.

## From Zebrafish to Mice

The team first tested the NPCbots in zebrafish larvae with spinal cord injuries. Within three days, the treated fish had regained near-normal swimming ability. That was promising but not definitive — zebrafish are known for their regenerative abilities.

The real test came in mice, whose spinal cords do not repair themselves. The researchers injected roughly half a million microrobots, suspended in a gel, into injured mice. They used magnets to position the microrobots at the injury site, then applied magnetic stimulation for 30 minutes daily over two weeks.

By day 34, the treated mice had regained significant movement. Electrical tests confirmed that signals were travelling from brain to muscle with greater strength. The microrobots had gathered at the injury site and produced neuron-like and astrocyte-like cells. No significant side effects were observed.

## Why This Matters for South Asians

India has one of the highest rates of spinal cord injury in the world, estimated at 15 to 20 per million people annually. Road accidents are the leading cause, and the country's trauma care infrastructure means many patients receive delayed treatment that worsens outcomes. The economic burden falls disproportionately on young men in their productive years.

For the Indian diaspora, many of whom have ageing parents in India with limited access to advanced rehabilitation, the prospect of a treatment that could restore function after spinal cord injury carries enormous emotional weight. A technology that can be injected rather than surgically implanted, guided non-invasively using magnets, and activated without embedded electrodes could eventually make advanced nerve repair accessible in settings where current surgical interventions are impractical.

## What Comes Next

The researchers are clear that clinical application is still years away. The next steps involve tracking the microrobots in larger animals, understanding what happens to the nanoparticles over time, and developing safe methods to steer them in bigger bodies. The leap from mice to humans is always the hardest.

But the principle has been demonstrated. Living machines, guided by magnets, can reach injured nerve tissue and coax it back to life. For the millions of people worldwide living with spinal cord injuries, including hundreds of thousands across India and the diaspora, this study represents something that has been vanishingly rare in the field: genuine, measurable progress.

*Sources: Nature Materials (June 2, 2026); ETH Zurich press release; Phys.org; The Times*"""

    # Image sourcing
    img_url, img_attr = source_image(
        slug,
        wiki_queries=["spinal cord injury treatment", "magnetoelectric nanoparticles neural", "ETH Zurich biomedical"],
        pexels_queries=["spinal cord medical research", "neuroscience laboratory microscope"]
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "lifestyle-health",
        "vertical": "culture",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "source": "The Videshi",
        "sources": json.dumps(["Nature Materials", "ETH Zurich", "Phys.org", "The Times"]),
        "image_url": img_url or "",
        "image_attribution": img_attr or "",
        "is_editorial": False
    }

    return insert_article(article)


# ============================================================
# ARTICLE 2: Yoga Reduces Cancer Survivor Symptoms (ASCO 2026)
# ============================================================
def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Yoga Reduces Cancer Survivor Symptoms")
    print("="*60)

    slug = "yoga-cancer-survivors-insomnia-fatigue-anxiety-asco-2026-south-asian-heritage"
    headline = "A Four-Week Yoga Programme Just Showed It Can Sharply Reduce Insomnia and Anxiety in Cancer Survivors. The Practice Was Born in India."
    subheadline = "A large randomised trial presented at the 2026 ASCO meeting found that yoga significantly reduced fatigue, mood disturbance, and sleep problems after cancer treatment. For the diaspora community, the findings are both validation and vindication."

    body = """Cancer treatment saves lives, but it often leaves survivors struggling with what comes after. Chronic insomnia, debilitating fatigue, persistent anxiety, and mood disturbances affect the majority of people who have completed chemotherapy and radiation. Standard survivorship care addresses the disease but rarely the aftermath.

A new randomised controlled trial, presented at the 2026 American Society of Clinical Oncology annual meeting in Chicago, offers compelling evidence that a structured yoga programme can meaningfully address these symptoms, and it does so with a practice that has been part of Indian culture for thousands of years.

## The Study

The trial was led by researchers at the University of Rochester Medical Center and conducted across multiple community cancer care sites in the United States. It enrolled 410 adult cancer survivors with an average age of 54. Roughly three-quarters were breast cancer survivors. None had practised yoga regularly in the three months before the study.

Participants were randomly assigned to two groups. Half received standard survivorship care. The other half received the same standard care plus enrollment in the Yoga for Cancer Survivors programme, known as YOCAS.

The YOCAS protocol involved two instructor-led 75-minute sessions per week over four weeks. Each session combined 18 poses from Gentle Hatha and Restorative yoga traditions, alongside breathing exercises and mindfulness training.

## The Results

The outcomes were measured through validated questionnaires, and the differences were striking. Survivors in the yoga group experienced moderate-to-large reductions in overall mood disturbance, small-to-medium reductions in anxiety, and medium-to-large reductions in fatigue compared with those who received standard care alone.

Perhaps most significant were the improvements in sleep. The researchers found that yoga's beneficial effects on mood and fatigue appeared to be mediated through improved sleep quality, suggesting that the practice addresses a root cause rather than merely treating symptoms.

Insomnia is one of the most common and persistent complaints among cancer survivors. It worsens fatigue, impairs cognitive function, and is associated with higher rates of depression and anxiety. A non-pharmaceutical intervention that can improve sleep quality in this population addresses a genuine unmet need.

## A Practice Rooted in Indian Tradition

For the South Asian diaspora, these findings carry a particular resonance. Yoga has been practised on the Indian subcontinent for millennia, long before it became a global wellness industry. The Hatha yoga poses and pranayama breathing exercises used in this trial trace their lineage directly to classical Indian traditions.

Yet the journey of yoga from Indian ashrams to American cancer clinics has not been straightforward. Many first-generation immigrants grew up with yoga as a spiritual and physical discipline but watched it become commercialised and decontextualised in the West. The ASCO presentation represents something different: rigorous clinical evidence, gathered through a randomised trial at major medical centres, confirming what generations of Indian families have known intuitively.

Cancer rates among South Asians are rising, particularly breast cancer among women in the diaspora, where incidence is approaching that of the general US population. A culturally familiar practice that can improve survivorship outcomes is not just clinically relevant — it is personally meaningful.

## What Survivors Should Know

The YOCAS programme is not hot yoga or power yoga. It consists of gentle, restorative poses accessible to people recovering from cancer treatment. The sessions are structured and instructor-led, which matters for consistency and safety. The four-week timeframe is manageable, and the twice-weekly schedule is realistic for people rebuilding their lives after treatment.

The study's authors noted that the benefits appeared to stem from yoga's effect on sleep, which then cascaded into improvements in mood and energy. This aligns with a growing body of evidence that sleep is the foundation on which post-treatment recovery is built.

For cancer survivors in the diaspora community, especially those who may already have a cultural connection to yoga, the message is straightforward: this is not alternative medicine. This is an evidence-based intervention, tested in a rigorous clinical trial, that works.

*Sources: ASCO 2026 Annual Meeting; University of Rochester Medical Center; Fox News; News-Medical.net*"""

    # Image sourcing - yoga is a great Commons/Pexels topic
    img_url, img_attr = source_image(
        slug,
        wiki_queries=["yoga therapy health", "hatha yoga practice", "yoga meditation wellness"],
        pexels_queries=["yoga gentle practice wellness", "yoga meditation healing"]
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "lifestyle-health",
        "vertical": "culture",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "source": "The Videshi",
        "sources": json.dumps(["ASCO 2026", "University of Rochester Medical Center", "Fox News", "News-Medical.net"]),
        "image_url": img_url or "",
        "image_attribution": img_attr or "",
        "is_editorial": False
    }

    return insert_article(article)


# ============================================================
# ARTICLE 3: Microsoft loses $200B+ despite biggest AI week
# ============================================================
def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: Microsoft AI Paradox — Stock Drops Despite Build")
    print("="*60)

    slug = "microsoft-stock-drops-200-billion-build-conference-ai-spending-nri-investors-20260603"
    headline = "Microsoft Just Lost Over $200 Billion in Market Value During Its Biggest AI Week of the Year. If You Hold MSFT, Here Is What Is Happening."
    subheadline = "The stock fell more than 7 per cent across two sessions despite an Nvidia partnership, seven new AI models, an autonomous agent launch, and a quantum computing breakthrough. Wall Street is sending a clear message about the gap between AI announcements and AI earnings."

    body = """Microsoft held its annual Build developer conference this week and delivered what should have been a triumphant showcase. The company announced a sweeping partnership with Nvidia to bring advanced AI to Windows devices. It launched seven new proprietary MAI foundation models. It unveiled Scout, an autonomous personal agent for Microsoft 365. And it revealed the Majorana 2 quantum chip, which it claims is 1,000 times more reliable than its predecessor and could make commercially viable quantum computers possible by 2029.

The market's response was unambiguous. Microsoft shares fell 4.2 per cent on Tuesday and another 3.3 per cent on Wednesday, wiping out more than $200 billion in market capitalisation in two sessions. For context, that is roughly the entire market value of Netflix.

## The Disconnect

The sell-off was not about any single announcement failing to impress. It was about a broader shift in how Wall Street is evaluating AI spending.

Microsoft is expected to spend more than $80 billion on capital expenditure this fiscal year, most of it on AI infrastructure — data centres, chips, networking equipment. The company has been increasing capex at a pace that would have been unthinkable five years ago. And investors are increasingly asking the same question: when does all of this spending turn into proportional revenue?

The challenge is that Microsoft's AI products — Copilot for Microsoft 365, Azure AI services, GitHub Copilot — are growing, but not at the rate needed to justify the capital being deployed. Enterprise adoption of Copilot has been slower than expected, with many companies still in pilot phases rather than full rollouts.

When CEO Satya Nadella talks about AI transforming every product Microsoft makes, investors want to see it in the quarterly numbers, not just in conference keynotes.

## The Quantum Question

The Majorana 2 announcement added a layer of complexity. Microsoft claimed it used AI to redesign its quantum chip, achieving a 1,000-fold improvement in qubit stability. The company said it now expects to have commercially useful quantum machines by 2029, matching IBM's timeline.

But the physics community pushed back sharply. Scientists pointed out that the results came from a handful of instances on a single device and have not been peer-reviewed. Microsoft retracted a high-profile quantum computing paper in 2021 after outside experts found flaws in the data. The company's previous Majorana 1 announcement also drew scepticism.

Barron's noted that the quantum news was unlikely to meaningfully help the stock, calling it a story for researchers rather than investors.

## What This Means for NRI Investors

Microsoft is one of the most widely held stocks among Indian diaspora investors in the United States. Many tech workers in the H-1B pipeline hold significant MSFT positions through their employer stock plans. For NRI families with diversified US portfolios, Microsoft is often one of the top five holdings.

The two-day decline is a reminder that even the strongest companies can lose significant value when expectations outpace reality. Microsoft remains a fundamentally sound business — its cloud revenue is growing, its Office franchise is a cash machine, and its partnership with OpenAI gives it a genuine AI moat. The question is not whether Microsoft will benefit from AI, but whether it will benefit enough to justify the tens of billions being spent right now.

For investors with a long time horizon, the correction may represent an opportunity. But for those holding concentrated MSFT positions through employer stock grants, the volatility underscores the importance of diversification. A single stock dropping 7 per cent in two days can meaningfully affect a household's net worth when that stock is also your employer.

## The Bigger Picture

Microsoft's Build week sell-off is not just a Microsoft story. It is a signal about where the entire AI trade is heading. The market is transitioning from the "announce and rally" phase to the "show me the earnings" phase. Companies that can demonstrate AI is driving actual revenue growth will be rewarded. Those that cannot, regardless of how impressive their product announcements are, will face pressure.

Broadcom reports earnings after the close today, and it is the next major test of this thesis. The chip designer is expected to report $22 billion in revenue, with AI chips accounting for nearly half. If Broadcom delivers, it will reinforce the idea that the AI infrastructure buildout is real. If it disappoints, the re-rating of AI stocks could accelerate.

For NRI investors watching from both sides of the Pacific, the message is the same: the AI revolution is not a straight line, and even the best companies will have weeks like this one.

*Sources: Reuters; Barron's; Scientific American; MarketBeat; StockTwits; Investors.com*"""

    # Image: Microsoft / Satya Nadella
    img_url, img_attr = source_image(
        slug,
        person_name="Satya Nadella",
        wiki_queries=["Microsoft Build conference", "Microsoft headquarters Redmond"],
        pexels_queries=["technology stock market trading screen", "artificial intelligence data center"]
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "markets-finance",
        "vertical": "economy",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "source": "The Videshi",
        "sources": json.dumps(["Reuters", "Barron's", "Scientific American", "MarketBeat", "StockTwits", "Investors.com"]),
        "image_url": img_url or "",
        "image_attribution": img_attr or "",
        "is_editorial": False
    }

    return insert_article(article)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Videshi Lifestyle-Health & Markets-Finance Writer")
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # Check skip list
    skip_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/image-skip-list.json")
    skip_list = []
    if os.path.exists(skip_path):
        try:
            with open(skip_path) as f:
                skip_list = json.load(f)
        except:
            pass

    results = []
    for writer_fn in [write_article_1, write_article_2, write_article_3]:
        try:
            art_id = writer_fn()
            results.append(art_id)
        except Exception as e:
            print(f"\n  ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append(None)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    success = sum(1 for r in results if r)
    print(f"  Articles published: {success}/3")
    for i, r in enumerate(results):
        status = f"✓ {r}" if r else "✗ FAILED"
        print(f"  Article {i+1}: {status}")
    print("=" * 60)
