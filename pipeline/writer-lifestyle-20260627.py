#!/usr/bin/env python3
"""
Videshi Lifestyle-Health & Markets-Finance Writer — 2026-06-27
Writes:
  1. lifestyle-health: Yale study — 45% of adults 65+ improved over 12 years; positive aging attitudes key
  2. markets-finance: RBI's FCNR deposit scheme — NRI dollar bonanza, $55B+ inflows expected
"""

import os, sys, json, re, io, time, uuid, subprocess, urllib.parse, datetime
import requests
from PIL import Image

# ── env ──────────────────────────────────────────────────────────────────────

def load_env(path):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing SUPABASE env")
    sys.exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── image helpers ────────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
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
            params=params, headers={"User-Agent": UA}, timeout=15
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
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []


# ── Commons relevance gate ──────────────────────────────────────────────────

_COMMONS_NEGATIVE = {
    "us capitol": ["state capitol", "pennsylvania", "texas capitol", "harrisburg", "austin capitol"],
    "white house": ["whitehouse station", "white house tennessee"],
    "supreme court": ["state supreme court", "uk supreme court"],
}
_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use",
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
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        cmd = [
            "curl", "-sS", "-H", f"Authorization: {PEXELS_API_KEY}",
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels: {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


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


def download_image(url):
    """Download image, with curl fallback for Wikimedia 429s."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
        if r.status_code == 429:
            print(f"  ⚠ 429 from requests, trying curl...")
    except Exception:
        pass
    # curl fallback
    try:
        tmp = f"/tmp/dl_{uuid.uuid4().hex[:8]}.img"
        subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
        data = open(tmp, 'rb').read()
        os.remove(tmp)
        if len(data) > 5000:
            return data
    except Exception as e:
        print(f"  ⚠ curl fallback failed: {e}")
    return None


def upload_image_to_supabase(jpeg_bytes, filename):
    r = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        },
        data=jpeg_bytes, timeout=60,
    )
    if r.status_code not in (200, 201):
        print(f"  ⚠ Upload failed {r.status_code}: {r.text[:200]}")
        return None
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  ✓ Uploaded to Supabase: {filename}")
    return public_url


def source_and_upload_image(slug, queries_wiki_commons, pexels_query, headline):
    """Multi-source image pipeline. Returns (url, attribution, caption) or (None, None, None)."""
    candidates = []

    # Wikimedia Commons
    for q in queries_wiki_commons:
        results = fetch_wikimedia_commons_images(q, limit=5)
        results = [r for r in results if commons_relevance_ok(r.get("title", ""), headline, q)]
        for r in results[:2]:
            candidates.append({"url": r["url"], "source": "wikimedia_commons", "title": r.get("title", "")})
        if candidates:
            break

    # Pexels fallback
    if not candidates and pexels_query:
        px = fetch_pexels_image(pexels_query)
        if px:
            candidates.append({"url": px, "source": "pexels", "title": ""})

    # Pick best and upload
    for cand in candidates:
        print(f"  Trying candidate: {cand['source']} — {cand['url'][:80]}...")
        raw = download_image(cand["url"])
        if not raw:
            continue
        compressed = compress_image(raw)
        if len(compressed) < 5000:
            print(f"  ⚠ Compressed too small ({len(compressed)} bytes), skipping")
            continue
        filename = f"{slug}.jpg"
        final_url = upload_image_to_supabase(compressed, filename)
        if final_url:
            attr = "Wikimedia Commons" if cand["source"] == "wikimedia_commons" else "Pexels"
            return final_url, attr, cand.get("title", "")
        
    print("  ⚠ No image sourced")
    return None, None, None


# ── article insert ───────────────────────────────────────────────────────────

def insert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed {r.status_code}: {r.text[:300]}")
        return None


# ═════════════════════════════════════════════════════════════════════════════
# ARTICLE 1: Yale Aging Study
# ═════════════════════════════════════════════════════════════════════════════

def write_yale_aging_article():
    print("\n═══ ARTICLE 1: Yale Positive Aging Study ═══")
    
    slug = "yale-study-45-percent-adults-65-improved-cognition-physical-function-positive-aging-attitudes-levy-geriatrics-diaspora-20260627"
    headline = "Nearly Half of Adults Over 65 Actually Got Sharper or Stronger — and Their Mindset Made the Difference"
    subheadline = "A Yale study tracking 11,000 older Americans for 12 years found that positive beliefs about aging were strongly linked to measurable improvements in cognition and walking speed"
    
    body = """Aging, in the popular imagination, is a long slide — memory fading, muscles weakening, independence shrinking. But a major Yale University study, published in the journal *Geriatrics*, turns that assumption on its head: nearly half of adults aged 65 and older actually improved in cognitive function, physical function, or both over a 12-year period.

The finding is not from a small, hand-picked group. Lead researcher Becca R. Levy, a professor of social and behavioral sciences at the Yale School of Public Health and an international authority on the psychosocial dimensions of aging, drew on data from more than 11,000 participants in the Health and Retirement Study, a federally funded, nationally representative longitudinal survey of older Americans.

## What They Measured — and What They Found

The researchers tracked two metrics: cognition, assessed through a global performance evaluation covering memory, attention, and math skills, and physical function, measured by walking speed — a metric geriatricians call a "vital sign" because of its strong links to disability, hospitalisation, and mortality.

Over the follow-up period, 45.15% of participants improved in at least one domain. About 32% improved cognitively, 28% improved physically, and many experienced gains that crossed thresholds considered clinically meaningful — not trivial fluctuations, but real, measurable progress.

"Many people equate aging with an inevitable and continuous loss of physical and cognitive abilities," Levy said. "What we found is that improvement in later life is not rare, it's common, and it should be included in our understanding of the aging process."

## The Attitude Factor

The most striking part of the study was not that some people improved — it was *who* improved. Those with positive self-perceptions of aging were significantly more likely to show gains. They agreed with statements like "I am as happy now as when I was younger" and disagreed with "The older I get, the more useless I feel."

This aligns with a growing body of evidence that age beliefs are not merely psychological comfort — they have biological consequences. Prior research has linked negative age stereotypes to higher cortisol levels, increased cardiovascular risk, and even structural brain changes. Levy's own earlier work demonstrated that people with positive aging views lived an average of 7.5 years longer than those with negative ones.

If extrapolated to the entire US population, the researchers noted, the findings would suggest that more than 26 million older Americans are experiencing improvement in functioning — a figure that challenges the near-universal narrative of decline.

## Why This Matters for the Diaspora

For Indian families navigating aging across continents — parents in Delhi or Chennai, children in Dallas or Toronto — this study carries a particular resonance.

Indian culture has traditionally treated aging with reverence: elders hold authority, wisdom, and a central place in the family. But that cultural framework is being tested. NRI families increasingly grapple with the distance between these ideals and the realities of managing a parent's health from 8,000 miles away — and the Western medical system they interact with often defaults to decline-focused frameworks.

The Yale finding offers a counterweight. It suggests that how a family talks about aging, the expectations they set, and whether they treat an older parent's years as a period of continued growth rather than managed decline may actually shape health outcomes. The Indian joint-family instinct — keeping elders engaged, purposeful, and central — may be doing more biological good than anyone realised.

Yet ageism runs deeper than many acknowledge. One study found that 80% of Americans falsely believed all older people develop dementia. Another showed that 1 in 5 people over 50 in the US face medical ageism — having symptoms dismissed as simply "getting old." For NRIs whose parents are in the American healthcare system, awareness of this bias is itself protective.

## The Bigger Picture

The study does not argue that every older person will improve, or that attitude alone overrides disease. But it shifts the baseline assumption: decline is not inevitable, improvement is common, and the stories we tell ourselves about aging are not just stories — they are, in measurable ways, self-fulfilling.

For a diaspora culture that has always believed its elders have more to give, the science is catching up.

*Sources: Yale School of Public Health, Health and Retirement Study (HRS), Geriatrics (2026), MedicalXpress*"""

    # Source image
    img_url, img_attr, img_title = source_and_upload_image(
        slug,
        queries_wiki_commons=["elderly couple walking park", "older adults exercise walking", "senior citizens healthy aging"],
        pexels_query="happy elderly couple walking outdoors",
        headline=headline
    )

    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "lifestyle-health",
        "vertical": "aging-health",
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "sources": json.dumps([
            "Yale School of Public Health",
            "Health and Retirement Study (HRS)",
            "Geriatrics (2026)",
            "MedicalXpress"
        ]),
        "diaspora_angle": "Indian culture's reverence for elders may have biological backing — positive aging attitudes predict measurable cognitive and physical gains, a counterweight for NRI families navigating Western decline-focused medical frameworks.",
        "image_url": img_url,
        "image_caption": "An older couple walking together outdoors — walking speed is considered a vital sign by geriatricians",
        "image_attribution": img_attr or "Pexels",
    }

    if not img_url:
        del article["image_url"]
        del article["image_caption"]
        del article["image_attribution"]

    return insert_article(article)


# ═════════════════════════════════════════════════════════════════════════════
# ARTICLE 2: RBI FCNR Deposit Scheme — NRI Dollar Bonanza
# ═════════════════════════════════════════════════════════════════════════════

def write_fcnr_article():
    print("\n═══ ARTICLE 2: RBI FCNR Deposit Scheme ═══")
    
    slug = "rbi-fcnr-nri-dollar-deposits-scheme-55-billion-inflows-6-7-percent-rates-leveraged-returns-rupee-banks-diaspora-20260627"
    headline = "The RBI Just Made Dollar Deposits in India More Rewarding Than They've Been in a Decade — Here's What NRIs Need to Know"
    subheadline = "India's central bank is absorbing all hedging costs on foreign currency deposits, banks are offering 6–7% on the dollar, and leveraged returns could approach 15% — with an estimated $55 billion in inflows by September"
    
    body = """The Reserve Bank of India has opened a window that may be the most lucrative opportunity for NRI depositors since the taper tantrum rescue of 2013. If you hold dollars and have been parking them in low-yield US savings accounts, the math has just changed — dramatically.

## What the RBI Did

In early June, the RBI announced a special swap facility for Foreign Currency Non-Resident (Bank) deposits — FCNR(B), in banker shorthand. Under this scheme, the central bank will absorb the *entire* cost of hedging rupee-dollar currency risk on fresh FCNR(B) deposits with tenors of three to five years. The facility is open until September 30, 2026.

This is a big deal. Normally, when an NRI places a dollar deposit with an Indian bank, the bank converts the dollars to rupees and lends them out domestically. But the bank then carries the risk that the rupee weakens before the deposit matures — so it hedges, at a cost of roughly 2.9% to 3% per year. That hedging cost gets passed on to the depositor as a lower interest rate.

By absorbing that cost entirely, the RBI has freed banks to offer rates that match or exceed what domestic depositors earn on rupee fixed deposits — without the NRI taking on any currency risk.

## What Banks Are Offering

Within days of the announcement, major banks scrambled to raise FCNR(B) rates. The jumps are staggering:

- **SBI** raised three-to-five-year dollar deposit rates by 230–265 basis points to 5.25–6.00%
- **HDFC Bank** went from 3.40–3.65% to 6.00% for the same tenors
- **ICICI Bank** and **Axis Bank** hiked rates by up to 310 and 305 basis points respectively
- **South Indian Bank** is offering up to 7.00% on large deposits and targeting $1 billion in fresh FCNR inflows by September
- **YES Bank** is at 6.50–6.60%, **Canara Bank** at 6.50%, and **Punjab National Bank** at 6.00–6.10%

For context: US Treasury rates on equivalent maturities hover around 4%. A guaranteed, tax-free 6–7% dollar return from an Indian bank, backed by a central bank swap, is difficult to find anywhere in global fixed income.

## The Leverage Play — and Why Analysts See 12–19% Returns

The headline rates are just the starting point. The RBI has also allowed Indian banks to extend loans to FCNR depositors against their deposits — both through their offshore branches and through GIFT City, India's tax-neutral financial hub.

This means an NRI can deposit, say, $500,000, borrow against it, and re-deposit the borrowed funds — effectively multiplying returns through leverage. Macquarie analysts estimate that with this structure, annualised returns could approach 12%. Axis Bank's own estimates suggest leveraged returns could climb as high as 15–19%, depending on the extent of leverage and the bank's pricing.

"The talk of 'equity-like' returns is mathematically real, but it is heavily reliant upon a classic leveraged arbitrage play," said P.V. Joy, head of retail liabilities at Federal Bank. "It is a phenomenal, low-risk windfall for ultra-high-net-worth individuals while this special RBI window remains open, but regular retail NRI depositors should expect their steady, guaranteed 6.25% yield."

## How Big Could This Get?

Estimates vary, but they are uniformly large:

- **Nomura** projects potential inflows of around $55 billion, with the bulk expected in August and September as the September 30 deadline approaches
- **Axis Bank** sees scope for up to $100 billion
- **Emkay Global** pegs likely flows at $50–55 billion, or 1.2% of GDP
- **Jefferies** estimates $50–70 billion
- **Macquarie** projects $30–50 billion

For comparison, the 2013 FCNR scheme — launched during a genuine rupee crisis — brought in over $20 billion. This time, the incentive structure is significantly richer.

As of March 2026, outstanding FCNR(B) deposits stood at $33.8 billion. The new scheme could double or triple that within months.

## Why the RBI Is Doing This

The immediate motivation is the rupee, which has been under sustained pressure. Foreign portfolio investors pulled a net $13.7 billion out of India in March alone, mostly from equities. While the rupee has since stabilised around ₹94–95 to the dollar, the RBI wants a durable buffer.

FCNR inflows serve multiple purposes: they shore up foreign exchange reserves, ease pressure on the rupee, improve bank liquidity, and — critically — could push down domestic borrowing costs. Bank stocks have already responded: the Nifty Bank index has risen nearly 7.2% over the past month, outperforming the broader market.

Some analysts have questioned whether the measures were necessary given India's still-robust forex reserves. The RBI, says one unnamed analyst quoted by Mint, "is effectively subsidising FCNR(B) inflows by taking on the hedging cost. If the rupee depreciates over the next three to five years, that cost will ultimately be borne by the RBI."

## What NRIs Should Actually Do

For the typical NRI with disposable savings in the US, Canada, or the UK, the straightforward play is simple: open or top up an FCNR(B) deposit for three to five years at your existing Indian bank. Returns of 6–7% are guaranteed, tax-free in India, and fully repatriable with no limits. No currency risk.

The leveraged route — borrowing against your deposit to re-invest — is real, but suited primarily to high-net-worth individuals comfortable with margin structures. Federal Bank's Joy puts it plainly: "Regular NRI depositors should expect their steady, guaranteed 6.25% yield."

The window closes September 30. After that, the special swap facility expires, and rates are likely to retreat to their pre-June levels of around 3–3.5%.

*Sources: Reserve Bank of India, Reuters, Mint, The Hindu Business Line, Nomura, Axis Bank, Macquarie, Emkay Global, Jefferies*"""

    # Source image
    img_url, img_attr, img_title = source_and_upload_image(
        slug,
        queries_wiki_commons=["Reserve Bank of India building", "RBI Mumbai headquarters", "Indian rupee currency"],
        pexels_query="Indian rupee currency notes coins",
        headline=headline
    )

    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "markets-finance",
        "vertical": "nri-investment",
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "sources": json.dumps([
            "Reserve Bank of India",
            "Reuters",
            "Mint",
            "The Hindu Business Line",
            "Nomura",
            "Axis Bank",
            "Macquarie",
            "Emkay Global",
            "Jefferies"
        ]),
        "diaspora_angle": "NRIs can earn 6–7% tax-free on dollar deposits in India with zero currency risk under a special RBI window that closes September 30 — leveraged returns could approach 15% for high-net-worth individuals.",
        "image_url": img_url,
        "image_caption": "The Reserve Bank of India headquarters in Mumbai — the central bank is absorbing all hedging costs on NRI dollar deposits until September",
        "image_attribution": img_attr or "Wikimedia Commons",
    }

    if not img_url:
        del article["image_url"]
        del article["image_caption"]
        del article["image_attribution"]

    return insert_article(article)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"=== Videshi Writer: Lifestyle-Health & Markets-Finance — {datetime.datetime.utcnow().isoformat()} ===")
    
    results = {}
    
    # Article 1: Yale Aging
    art1_id = write_yale_aging_article()
    results["yale_aging"] = art1_id
    
    # Article 2: FCNR
    art2_id = write_fcnr_article()
    results["fcnr_deposits"] = art2_id
    
    print(f"\n=== SUMMARY ===")
    for k, v in results.items():
        status = f"✓ {v}" if v else "✗ FAILED"
        print(f"  {k}: {status}")
    
    failed = [k for k, v in results.items() if not v]
    if failed:
        print(f"\n⚠ {len(failed)} article(s) failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} articles inserted successfully")
