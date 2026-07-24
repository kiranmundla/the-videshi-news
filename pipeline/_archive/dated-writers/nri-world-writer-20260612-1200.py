#!/usr/bin/env python3
"""
NRI World Writer — 2026-06-12 12:00 UTC batch
Writes 2 fresh NRI World articles to Supabase p2_articles.
"""

import os, json, uuid, subprocess, re, sys, time
from datetime import datetime, timezone
from pathlib import Path

# ── env ──────────────────────────────────────────────────────────────────
SUPABASE_URL  = "https://lboecaekpynbpyijrbfz.supabase.co"
SUPABASE_KEY  = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY    = os.environ.get("PEXELS_KEY", "")
HEADERS_SB    = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = "TheVideshi/1.0 (thevideshi.com)"

import requests

# ── image helpers ────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
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
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers={"User-Agent": UA}, timeout=15,
        )
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
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
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia error: {e}")
    return []


def fetch_pexels(query):
    """Use curl (urllib gets 403)."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={requests.utils.requote_uri(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            best = photos[0]
            url = best["src"]["large2x"]  # 1200px wide
            print(f"  ✓ Pexels: '{query}' → {url[:80]}...")
            return url, best.get("photographer", "Pexels")
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None, None


def compress_and_upload(img_url, slug):
    """Download, compress to JPEG ≤1200px, upload to Supabase article-images bucket."""
    from PIL import Image
    import io

    print(f"  Downloading {img_url[:80]}...")
    for attempt in range(3):
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 429:
            wait = 2 ** (attempt + 1)
            print(f"  ⚠ 429 rate-limited, retrying in {wait}s...")
            time.sleep(wait)
            continue
        break
    r.raise_for_status()
    raw = r.content
    print(f"  Downloaded {len(raw)} bytes")

    img = Image.open(io.BytesIO(raw))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > 1200:
        ratio = 1200 / img.width
        img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80, optimize=True)
    compressed = buf.getvalue()
    print(f"  Compressed to {len(compressed)} bytes ({img.width}×{img.height})")

    filename = f"{slug}.jpg"
    upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"

    # Try upsert (delete then upload)
    requests.delete(upload_url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    })
    resp = requests.post(
        upload_url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
        },
        data=compressed,
        timeout=30,
    )
    if resp.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded → {public_url}")
        return public_url
    else:
        print(f"  ⚠ Upload failed ({resp.status_code}): {resp.text[:200]}")
        # Fallback: return original URL
        return img_url


# ── article definitions ──────────────────────────────────────────────────

ARTICLES = [
    {
        "slug": "aia-ny-gala-2026-ratna-honorees-indian-american-20260612",
        "headline": "Seven 'Ratnas' and a 57-Year Legacy: Inside the AIA-NY Annual Benefit Gala 2026",
        "subheadline": "The oldest Indian-American organisation honoured a xenotransplantation pioneer, a Harvard AI entrepreneur, and five other trailblazers at a packed Flushing gathering — then announced plans for its 39th Deepavali celebration.",
        "summary": "The Association of Indians in America held its Annual Benefit Gala in New York, honouring seven Indian-American achievers across medicine, law, technology, and philanthropy.",
        "category": "nri-world",
        "vertical": "diaspora",
        "tags": ["Indian American", "AIA", "New York", "diaspora", "gala", "community"],
        "sources": [
            {"name": "The Indian EYE", "url": "https://theindianeye.com/2026/06/11/aia-ny-hosts-grand-annual-benefit-gala-2026-to-honor-individuals-for-outstanding-contributions/"},
            {"name": "Association of Indians in America", "url": "https://www.aianyc.org/"},
        ],
        "diaspora_angle": "Oldest Indian-American organisation (founded 1967) honours new generation of NRI achievers; event bridges generational and professional divides in the community.",
        "score_total": 72,
        "image_search_queries": ["Indian American community gala New York", "Indian American awards ceremony"],
        "image_pexels_query": "Indian American formal event celebration",
        "image_caption": "The Association of Indians in America held its annual gala at Terrace on the Park in Flushing, New York",
        "body": """The chandeliers at Terrace on the Park in Flushing, Queens, have witnessed a fair number of Indian-American milestones since the venue became a fixture of the community's social calendar. On the evening of June 10, they illuminated another: the Association of Indians in America's Annual Benefit Gala 2026, where seven individuals were recognised as "Ratnas" — gems — for their contributions to American civic life.

Founded in 1967, AIA-NY holds the distinction of being the oldest Indian-American organisation in the United States, predating even the wave of professional immigration that followed the Hart-Celler Act. That history was on display as more than 300 guests — physicians, entrepreneurs, diplomats, and first-generation college students — gathered for an evening that was part celebration, part institutional memory exercise.

## The Seven Honourees

The Ratna awards this year spanned medicine, law, technology, and community service, reflecting the breadth of Indian-American professional life in 2026.

**Dr. Dattatreyudu Nori**, a radiation oncologist who has treated thousands of cancer patients over a career spanning five decades, received the evening's most sustained ovation. A Padma Bhushan recipient, Dr. Nori has been a fixture of New York's medical community and a quiet but persistent advocate for cancer screening in South Asian populations, where awareness has historically lagged.

**Dr. Aprajita Mattoo** brought the frontier of transplant medicine to the stage. A researcher in xenotransplantation — the science of transplanting animal organs into human patients — Dr. Mattoo's work sits at the cutting edge of a field that could reshape organ donation. Her recognition signals the community's growing comfort celebrating science that is ambitious, not just commercially successful.

**Dr. Sahil Khera**, a structural heart specialist at Mount Sinai, was honoured for both his clinical work and his efforts to expand access to cardiac interventions among underserved populations. **Dr. Jagat Rawal** received recognition for decades of medical practice and community health advocacy.

**Pulkita Kini**, the youngest honouree, stood out for a different reason. A Harvard MBA graduate who pivoted into artificial intelligence entrepreneurship, Kini represents a generational shift in the diaspora's professional identity — from the doctor-lawyer-engineer triad that defined the immigrant experience for decades toward the builder-founder archetype that increasingly characterises Indian Americans in technology.

**Jessica Kalra, Esq.** was recognised for her legal work serving the community, while **Manish Dhadda** received the award for his philanthropic and business contributions.

## More Than a Dinner

New York State Comptroller Thomas DiNapoli addressed the gathering, joined by representatives from the Indian consulate in New York. The speeches struck a familiar but pointed note: the Indian-American community's economic and civic contributions are enormous, yet institutional visibility — the kind that translates into political capital and cultural permanence — remains a work in progress.

AIA's answer to that gap has always been institutional persistence. The organisation has survived leadership transitions, funding droughts, and the existential question that haunts every immigrant institution: whether the next generation will care enough to show up. The room in Flushing suggested the answer, for now, is yes.

The evening also served as a launchpad for AIA-NY's next milestone: the **39th annual Deepavali Celebration**, planned for October 2026. That event, which has grown into one of the largest public Diwali celebrations on the East Coast, remains the organisation's most visible contribution to the cultural calendar.

## What It Means for the Diaspora

The Ratna list tells a story about where Indian America is heading. The mix of a Padma Bhushan oncologist and a twentysomething AI entrepreneur, of a xenotransplantation researcher and a community lawyer, suggests a diaspora that is simultaneously deepening its roots in established professions and branching into new ones. AIA's willingness to honour both ends of that spectrum — legacy and emergence — is what has kept it relevant for nearly six decades.

For the three hundred guests at Terrace on the Park, the evening was a reminder that community institutions are not just social clubs. They are the infrastructure through which a diaspora tells itself who it is, who it was, and who it might become. At 57, AIA-NY is still doing that work.""",
    },
    {
        "slug": "gulf-war-nri-kerala-property-boom-real-estate-20260612",
        "headline": "Coming Home to Concrete: How the Gulf War Is Fuelling a Kerala Property Rush Among NRIs",
        "subheadline": "Four months of conflict in West Asia have pushed Gulf-based Keralites to hedge their futures with flats and plots back home — even as construction costs surge 35 per cent and builders struggle to keep up.",
        "summary": "The ongoing West Asia conflict is driving Gulf-based Keralite NRIs to buy property in India at an accelerating pace, creating a real estate mini-boom in Kochi, Calicut, and Thrissur even as construction costs soar.",
        "category": "nri-world",
        "tags": ["NRI", "Kerala", "real estate", "Gulf war", "property", "investment", "West Asia"],
        "sources": [
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/for-kerala-realty-the-west-asia-war-is-a-double-edged-sword-11780943881520.html"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/some-lenders-hike-rates-fx-deposits-non-resident-indians-2026-06-10/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/money-and-banking/sbi-icici-hdfc-bank-raise-fcnrb-rates-to-attract-nri-funds-after-rbi-forex-swap-move/article71088760.ece"},
        ],
        "diaspora_angle": "Gulf-based Keralite NRIs — one of India's largest remittance communities — are reassessing permanent settlement plans; war is accelerating a generational shift from 'earn abroad, retire home' to 'invest now, return sooner.'",
        "score_total": 78,
        "image_search_queries": ["Kerala real estate construction Kochi", "Kerala apartment building"],
        "image_pexels_query": "Kerala waterfront buildings Kochi cityscape",
        "image_caption": "New residential developments in Kochi, Kerala, where NRI property demand has surged amid the West Asia conflict",
        "body": """For three decades, the economic equation of Kerala's Gulf migrants held a comforting symmetry: earn in dirhams and riyals, send money home, build a house, and return when the body said so. The Iran-US conflict, now in its fourth month, has disrupted that calculus with the blunt arithmetic of geopolitical risk.

Across the Persian Gulf states where an estimated 2.1 million Keralites live and work, conversations that once centred on school admissions and gold prices have shifted to a more urgent question: is it time to go back?

## The Numbers Are Moving

India's real estate developers have noticed. Prestige Group, Sobha Ltd, and several mid-tier Kerala builders report a sharp uptick in NRI inquiries since the conflict escalated in March. Credai Kerala CEO Sethunath told Livemint what the numbers already suggested: "People are thinking of coming back."

The demand is concentrated in three corridors — **Kochi**, where the IT and metro infrastructure make it attractive to younger NRIs eyeing remote work; **Calicut (Kozhikode)**, where emotional ties to northern Kerala's Malabar coast run deep; and **Thrissur**, the cultural capital where gold, temples, and property have always been intertwined.

Ticket sizes are climbing too. Where Gulf NRIs once defaulted to plots of land — the classic "I'll build when I retire" hedge — brokers say the shift is toward ready-to-move flats and gated communities. The reasoning is pragmatic: if you might need to relocate quickly, an empty plot in Palakkad is less useful than a furnished apartment in Kochi.

## The 35 Per Cent Problem

But Kerala's property boom has a supply-side migraine. Construction costs have surged roughly 35 per cent since the war began, driven by a tangle of factors that would be familiar to anyone who has watched a conflict ripple through global supply chains.

Steel and cement prices have climbed as shipping routes through the Strait of Hormuz face disruption. More acutely, Kerala's construction industry depends heavily on migrant labour from other Indian states — workers who are themselves responding to a tighter national labour market and better-paying alternatives elsewhere. The result: builders can sell but cannot always deliver on time.

For NRI buyers, the irony is thick. The same geopolitical instability that is pushing them to invest in Kerala property is also making that property more expensive and slower to build.

## The FCNR Tailwind

Running alongside the property rush is a quieter but financially significant development. The Reserve Bank of India's recent policy moves have made Foreign Currency Non-Resident (FCNR) deposits dramatically more attractive. Several banks — HDFC, SBI, ICICI, AU Small Finance Bank, Yes Bank — have hiked FCNR rates by up to 300 basis points, responding to the RBI's easing of the interest rate ceiling on these deposits.

The math is compelling. An NRI parking dollars in an FCNR account can now earn rates that approach equity-like returns when the rupee's depreciation is factored in. Industry estimates suggest the rate hikes could attract $35-40 billion in fresh NRI deposits — money that, in Kerala's case, often finds its way into real estate, gold, or family business expansion.

For Gulf NRIs specifically, the FCNR move offers a hedging mechanism: park dollars at high interest now, and use the returns to fund property purchases later if the security situation stabilises. It is, in effect, a way to keep one foot in the Gulf and one in Kerala simultaneously.

## A Generational Shift

What makes this moment different from earlier Gulf crises — the 1990 Kuwait invasion, the 2008 financial crash, the 2015 oil price collapse — is the demographic profile of the NRIs making decisions. The current generation of Gulf Keralites is younger, more digitally connected, and more likely to have children who have grown up in the Gulf and consider it home rather than a temporary posting.

For this cohort, "going back" is not a retirement plan; it is a strategic pivot. Many are exploring hybrid arrangements — maintaining Gulf employment while establishing a physical base in Kerala, enabled by remote work and improved connectivity. The property they are buying reflects this: urban apartments with good internet, not ancestral land in the village.

Credai Kerala and state government officials are aware that this demand surge could be temporary. If the conflict de-escalates, some NRIs will cancel bookings and stay put. But the deeper trend — Gulf NRIs treating Kerala property as a risk-management tool rather than a retirement dream — may outlast the war that triggered it.

## What to Watch

The next three months will be telling. If FCNR inflows hit projected levels and builders manage to navigate the cost squeeze, Kerala could see its strongest NRI real estate quarter in a decade. If construction delays mount and the conflict drags on, the boom risks turning into a bottleneck of frustrated buyers and overextended developers.

Either way, the symmetry of the old Gulf equation — earn there, build here, return someday — has cracked. For millions of Keralites, the someday is arriving faster than anyone planned.""",
    },
]

# ── main pipeline ────────────────────────────────────────────────────────

def source_image(article):
    """Multi-source image search: Wikimedia Commons → Pexels. Pick best."""
    candidates = []

    # Wikimedia Commons
    for q in article["image_search_queries"]:
        results = fetch_wikimedia_commons(q, limit=3)
        for r in results:
            candidates.append({"url": r["url"], "source": "wikimedia_commons", "width": r["width"]})

    # Pexels fallback
    purl, photographer = fetch_pexels(article["image_pexels_query"])
    if purl:
        candidates.append({"url": purl, "source": "pexels", "width": 1200})

    if not candidates:
        print(f"  ⚠ No image found for {article['slug']}")
        return None, "The Videshi"

    # Prefer Wikimedia (wider editorial license), then Pexels
    # Filter out tiny images
    good = [c for c in candidates if c["width"] >= 600]
    if not good:
        good = candidates

    # Prefer wikimedia_commons over pexels
    wikimedia = [c for c in good if c["source"] == "wikimedia_commons"]
    best = wikimedia[0] if wikimedia else good[0]

    # Try candidates in priority order; fall back on failure
    for c in ([best] + [x for x in good if x != best]):
        attribution = "Wikimedia Commons" if c["source"] == "wikimedia_commons" else "Pexels"
        try:
            final_url = compress_and_upload(c["url"], article["slug"])
            return final_url, attribution
        except Exception as e:
            print(f"  ⚠ Failed to download/upload ({e}), trying next candidate...")
            continue

    print(f"  ⚠ All image candidates failed for {article['slug']}")
    return None, "The Videshi"


def insert_article(article, image_url, image_attribution):
    """Insert article into Supabase p2_articles."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"].strip(),
        "slug": article["slug"],
        "category": article["category"],
        "tags": article["tags"],
        "sources": json.dumps(article["sources"]),
        "diaspora_angle": article["diaspora_angle"],
        "score_total": article["score_total"],
        "status": "review",
        "vertical": article.get("vertical", "diaspora"),
        "image_url": image_url or "",
        "image_caption": article["image_caption"],
        "image_attribution": image_attribution,
        "published_at": now,
        "created_at": now,
        "updated_at": now,
    }

    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=payload,
        timeout=30,
    )

    if resp.status_code in (200, 201):
        returned = resp.json()
        rid = returned[0]["id"] if isinstance(returned, list) and returned else art_id
        print(f"  ✓ Inserted: {article['slug']}  (id={rid})")
        return rid
    else:
        print(f"  ✗ Insert failed ({resp.status_code}): {resp.text[:300]}")
        return None


def main():
    print("=" * 60)
    print("NRI World Writer — 2026-06-12 12:00 UTC")
    print("=" * 60)

    results = []

    for i, article in enumerate(ARTICLES, 1):
        print(f"\n--- Article {i}/{len(ARTICLES)}: {article['slug']} ---")

        # Source image
        print("  Sourcing image...")
        image_url, attribution = source_image(article)

        # Insert
        print("  Inserting into Supabase...")
        art_id = insert_article(article, image_url, attribution)
        results.append({
            "slug": article["slug"],
            "headline": article["headline"],
            "id": art_id,
            "image_url": image_url,
            "status": "review",
        })

    print("\n" + "=" * 60)
    print("RESULTS:")
    for r in results:
        status = "✓" if r["id"] else "✗"
        print(f"  {status} {r['slug']}")
        print(f"    headline: {r['headline']}")
        print(f"    id: {r['id']}")
        print(f"    image: {r['image_url'][:80] if r['image_url'] else 'NONE'}...")
    print("=" * 60)


if __name__ == "__main__":
    main()

