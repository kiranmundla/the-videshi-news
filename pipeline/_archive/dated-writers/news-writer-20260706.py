#!/usr/bin/env python3
"""News writer for July 6, 2026 — two articles for the 'news' category."""

import json, os, sys, time, uuid, requests, urllib.parse, io
from datetime import datetime, timezone

# ── Supabase setup ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

# ── Image helpers ───────────────────────────────────────────────────────────

def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6",
        "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers=UA, timeout=15)
        if r.status_code != 200:
            return []
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
                "title": page.get("title", ""),
                "width": ii.get("width", 0),
                "height": ii.get("height", 0),
            })
        return results
    except Exception as e:
        print(f"  ⚠ Commons search error: {e}")
        return []


def fetch_pexels_image(query):
    """Search Pexels via curl (urllib gets 403)."""
    import subprocess
    pexels_key = os.environ.get("PEXELS_API_KEY", "")
    if not pexels_key:
        print("  ⚠ No PEXELS_API_KEY set")
        return None
    encoded = urllib.parse.quote(query)
    cmd = [
        "curl", "-sS", "-H", f"Authorization: {pexels_key}",
        f"https://api.pexels.com/v1/search?query={encoded}&per_page=3&orientation=landscape"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        data = json.loads(result.stdout)
        for photo in data.get("photos", []):
            src = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if src:
                return src
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
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
        print(f"    ⚠ Supabase upload failed {r.status_code}: {r.text[:200]}")
        return None
    return f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"


def download_image(url):
    """Download image bytes, using curl as fallback for Wikimedia 429s."""
    import subprocess
    try:
        r = requests.get(url, headers=UA, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
    except:
        pass
    # curl fallback
    try:
        result = subprocess.run(
            ["curl", "-sS", "-A", "TheVideshi/1.0 (thevideshi.com)", "-o", "/tmp/img_dl.tmp", "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout.strip().startswith("200"):
            with open("/tmp/img_dl.tmp", "rb") as f:
                data = f.read()
            if len(data) > 5000:
                return data
    except:
        pass
    return None


def source_and_upload_image(queries, slug, fallback_pexels_query=None):
    """Try Commons queries, then Pexels fallback. Returns (url, attribution) or (None, None)."""
    for q in queries:
        print(f"  Searching Commons: {q}")
        results = fetch_wikimedia_commons_images(q, limit=5)
        for img in results:
            title = img.get("title", "").lower()
            # Skip SVG, logos, flags, icons
            if any(x in title for x in ["flag of", "coat of arms", "logo", "icon", ".svg"]):
                continue
            url = img["url"]
            print(f"    Trying: {img['title'][:60]} ({img['width']}x{img['height']})")
            data = download_image(url)
            if data:
                try:
                    compressed = compress_image(data)
                    supabase_url = upload_image_to_supabase(compressed, f"{slug}.jpg")
                    if supabase_url:
                        print(f"    ✓ Uploaded to Supabase: {supabase_url[:60]}...")
                        return supabase_url, "Wikimedia Commons"
                except Exception as e:
                    print(f"    ⚠ Compress/upload error: {e}")
                    continue

    # Pexels fallback
    if fallback_pexels_query:
        print(f"  Falling back to Pexels: {fallback_pexels_query}")
        pexels_url = fetch_pexels_image(fallback_pexels_query)
        if pexels_url:
            data = download_image(pexels_url)
            if data:
                try:
                    compressed = compress_image(data)
                    supabase_url = upload_image_to_supabase(compressed, f"{slug}.jpg")
                    if supabase_url:
                        print(f"    ✓ Uploaded Pexels to Supabase: {supabase_url[:60]}...")
                        return supabase_url, "Pexels"
                except Exception as e:
                    print(f"    ⚠ Pexels compress/upload error: {e}")

    return None, None


def insert_article(article):
    """Insert article into Supabase p2_articles table."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  ✓ Inserted article: {article['slug']} (id={aid})")
        return aid
    else:
        print(f"  ✗ Insert failed {r.status_code}: {r.text[:300]}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 1: OPEC+ Output Increase — India's Oil Relief
# ═══════════════════════════════════════════════════════════════════════════

article1_slug = "opec-output-increase-oil-prewar-levels-india-relief-rupee-inflation-20260706"

article1_body = """OPEC+ approved yet another increase in oil output targets on Sunday, pushing Brent crude below $72 a barrel — almost exactly where it was before the first American and Israeli bombs fell on Iran in late February. For India, a country that imports nearly 90 per cent of its crude, the implications are immense.

The oil-producing alliance agreed to raise quotas by 188,000 barrels per day from August, the third consecutive monthly increase as the group gradually unwinds production cuts first imposed in 2023. Seven core members — Saudi Arabia, Russia, Iraq, Kuwait, Algeria, Kazakhstan and Oman — have now restored nearly 800,000 barrels per day since April.

## The Hormuz Factor

The increases have been largely symbolic until now. The U.S.-Israeli war on Iran effectively shut the Strait of Hormuz to tanker traffic for months, cutting off the world's most important oil choke point and sending Brent crude above $126 a barrel in April. Saudi Arabia, Kuwait and Iraq — all of whom rely on the strait to export — saw production plummet to 33.13 million barrels per day in May, down from 42.77 million in February.

But the fragile memorandum of understanding between Washington and Tehran, signed on June 17, has begun to restore order. Ships are passing through the strait again — 160 vessels moved through from Monday to Saturday last week, according to Reuters data. Oil exports from the Persian Gulf are climbing, even if they remain below pre-war levels.

Trump used his July 4 speech at Mount Rushmore to claim credit: "We knocked the hell out of Iran. They want to settle so badly. We gave them a week off for a funeral, because we're nice." Negotiations between the two countries are set to resume in Pakistan on July 11, after the conclusion of Ayatollah Khamenei's week-long funeral procession.

## What Cheaper Oil Means for India

The arithmetic is stark. India spent roughly $180 billion on crude imports in the last fiscal year, and every $10 drop in the price of a barrel saves the economy an estimated $15 billion annually. With Brent now at $71.70 — down 43 per cent from the April peak — the relief extends across the entire macroeconomic dashboard.

**Inflation eases.** Fuel and transport costs feed into the price of everything from vegetables to manufactured goods. The Reserve Bank of India, which had warned of an oil-driven inflation spike in its April monetary policy statement, now faces a far more benign price environment. Input cost inflation already fell to a five-month low in June, according to the latest PMI data.

**The rupee recovers.** India's currency had crashed to a record low near 97 per dollar in May, battered by high energy costs and sustained foreign selling. It has since recovered to around 94.50 — among the best-performing Asian currencies in June — helped by cheaper oil and central bank measures to draw dollar inflows. Goldman Sachs has raised its 2026 growth forecast for India by 30 basis points and now expects a balance of payments surplus of 0.7 per cent of GDP.

**The fiscal maths improve.** Lower oil prices reduce the subsidy burden on cooking gas and fertiliser, both of which are sensitive to crude. The government has more room to maintain its deficit targets without squeezing capital expenditure — a critical priority for the infrastructure push that underpins India's growth story.

**Foreign money returns.** Global fund managers, who had pulled $27 billion from Indian equities this year, are reassessing. U.S.-listed India-focused ETFs recorded positive inflows last week for the first time in over a month, according to Elara Capital. "India is among the most oversold markets we track," said Todd McClone of William Blair Investment Management. "This macro improvement strengthens the case to act."

## Risks Remain

The relief is real, but it is also fragile. The U.S.-Iran ceasefire has been punctuated by flare-ups — Iran launched missiles at American bases in Kuwait and Bahrain just last weekend, and Trump openly threatened to "militarily complete the job." A collapse of the peace talks would send oil prices spiralling again.

OPEC+ itself is fracturing. The UAE left the alliance in May over production quota disputes. Iraq has signalled it may follow. If discipline breaks down, the resulting price war could create volatility that hurts producers and consumers alike.

And the broader demand picture is mixed. Chinese oil imports have weakened. A coordinated release of strategic petroleum reserves by the International Energy Agency has added supply. These factors have helped push prices down, but they also reflect a global economy that is not firing on all cylinders.

## The Diaspora Angle

For the 32 million Indians living abroad, cheaper oil translates into tangible benefits. A stronger rupee means remittances buy more. Lower inflation protects family purchasing power back home. A healthier current account reduces the risk of the kind of currency crisis that eroded NRI savings in 2013.

And for the growing number of diaspora investors in Indian equities, the oil-driven market recovery has been significant. India's stock market has reclaimed the $5 trillion valuation milestone, with the Sensex near six-week highs. The Nifty 50 has gained over 14 per cent since early April.

The story of Indian oil, for now, is one of relief. The question is whether the geopolitics will let it last.

*Sources: Reuters, OPEC+, S&P Global PMI, Goldman Sachs, Elara Capital, Fox Business, MarketWatch*"""

article1 = {
    "headline": "Oil Just Fell to Pre-War Levels. For India, the Breathing Room Is Enormous.",
    "subheadline": "OPEC+ keeps adding supply, Brent is back below $72, and India's inflation, rupee and fiscal maths are all improving at once. But the ceasefire holding it together is fragile.",
    "slug": article1_slug,
    "body": article1_body,
    "category": "news",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "OPEC+", "url": "https://www.opec.org"},
        {"name": "Goldman Sachs Research", "url": "https://www.goldmansachs.com"},
        {"name": "S&P Global PMI", "url": "https://www.spglobal.com"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com"},
    ]),
    "diaspora_angle": "Cheaper oil strengthens the rupee, protects family purchasing power, and makes remittances go further — the single most direct macroeconomic benefit for NRIs.",
    "image_caption": "",
    "image_attribution": "",
    "image_url": "",
}

# ═══════════════════════════════════════════════════════════════════════════
# ARTICLE 2: NATO Ankara Summit — India's Balancing Act
# ═══════════════════════════════════════════════════════════════════════════

article2_slug = "nato-ankara-summit-india-defence-ukraine-iran-nuclear-balancing-act-20260706"

article2_body = """The most consequential NATO summit in years opens in Ankara on Tuesday, and India will not be in the room. But on issue after issue — Iran's nuclear programme, the future of Ukraine, the global defence industry boom, and the expanding definition of who counts as a Western ally — the decisions made in Turkey's capital this week will shape New Delhi's strategic calculus for years to come.

The two-day gathering brings together leaders from all 32 NATO member states, along with invited guests from the Indo-Pacific — Japan, South Korea, Australia and New Zealand. The agenda is sweeping: a reaffirmation of the Article 5 collective defence pact, a pledge of €70 billion in military aid to Ukraine for 2026, a defence industry forum where deals worth tens of billions of dollars will be announced, and difficult conversations about Iran.

## The Five Per Cent Demand

The summit's dominant tension is money. The United States wants every NATO ally spending five per cent of GDP on defence by 2035 — a target that would require most European members to more than double their current budgets. Trump has threatened to punish laggards and reward compliant allies with preferential access to American weapons.

"Some allies are doing more than others," said Matt Whitaker, the U.S. ambassador to NATO. "President Trump expects all allies to step up immediately."

For India, this has direct consequences. A Europe that spends dramatically more on defence becomes a bigger buyer in the global arms market — and a bigger competitor for the platforms India wants. France's Rafale jets, which India already operates, are in growing demand across NATO. So are missile defence systems, naval frigates, and advanced drones. Higher European defence budgets could mean longer delivery queues and higher prices for Indian procurement.

But the same dynamic creates opportunities. India's own defence industry — led by HAL, BEL, and a growing tier of private manufacturers — has been positioning itself as an alternative supplier. Canada recently signalled interest in Indian-made defence equipment as part of its $500 billion defence expansion. A NATO hungry for volume could open doors that were previously closed.

## Iran: The Elephant in the Room

European officials are privately worried that Iran will overshadow everything else in Ankara. The summit declaration is expected to state that "Iran must never have a nuclear weapon" and call for freedom of navigation in the Strait of Hormuz — both issues that directly touch India's interests.

India, which sent a deputy minister to Khamenei's funeral last week (despite being personally invited to send a higher-ranking representative), is walking its familiar tightrope. New Delhi has quietly benefited from the U.S.-Iran ceasefire — the reopening of the Hormuz strait and the collapse in oil prices have been an unambiguous economic gift. But it has also maintained back-channel ties with Tehran, wary of being seen to side entirely with Washington.

The NATO statement on Iran's nuclear programme will set the tone for broader multilateral discussions. If it signals a harder Western stance — backed by Trump's threat to "militarily complete the job" — India may face pressure to take a clearer position, particularly as the peace talks resume in Pakistan on July 11.

## Ukraine: The $70 Billion Question

NATO's €70 billion military aid pledge to Ukraine is the alliance's largest single-year commitment since the war began in 2022. The United States is not expected to contribute funding directly, leaving the burden on European allies and Canada.

For India, which has maintained its studied neutrality on the Russia-Ukraine conflict, the size of the commitment matters. It signals that the war remains the West's defining security priority — and that diplomatic space for neutral parties like India continues to narrow. Indian diplomats have noted privately that Western patience with Delhi's balancing act is wearing thin, particularly as Russia's war economy grows increasingly dependent on Indian oil purchases and sanctions workarounds.

The summit will also feature Trump's bilateral meeting with Ukrainian President Volodymyr Zelensky, their first since the failed Swiss peace summit. Any breakthrough — or breakdown — in the Ukraine peace process has ripple effects for India's own diplomatic positioning.

## The Indo-Pacific Expansion

Perhaps the most significant long-term development for India is NATO's deepening engagement with the Indo-Pacific. South Korea's President Lee Jae Myung will attend the summit and deliver a keynote at the defence industry forum, marking Seoul's most ambitious NATO outreach yet.

Japan, Australia and New Zealand are also sending delegations. The message is clear: NATO no longer sees itself as a purely Euro-Atlantic alliance. Its strategic perimeter now extends to the Pacific, and the countries it considers partners are increasingly the same ones India works with in the Quad and other minilateral groupings.

This creates both alignment and friction. India and NATO share concerns about China's military expansion, supply chain vulnerabilities, and the weaponisation of critical technologies. But India is not, and does not aspire to be, a NATO partner in any formal sense. The closer NATO's Indo-Pacific friends draw to the alliance, the more India must define what its own non-aligned security identity actually means in practice.

## What the Diaspora Should Watch

For the 1.8 million Indians in Britain, the defence spending debate is personal: London's £15 billion boost could accelerate recruitment of Indian-origin defence and tech professionals. For the three million in the United States, Trump's approach to allies and adversaries shapes the broader geopolitical environment in which diaspora communities navigate dual identities.

And for all NRIs, the Iran outcome matters most. A durable peace deal means stable oil, a strong rupee, and economic predictability. A collapse means the return of the $120 barrel — and everything that comes with it.

The Ankara summit is, in the end, about the architecture of the world India's diaspora lives in. The seat may be empty, but the stakes are not.

*Sources: Reuters, NATO, GOV.UK, Devdiscourse, Fox Business, The Sun*"""

article2 = {
    "headline": "NATO's Biggest Summit in Years Starts Tomorrow. India Isn't at the Table — but It's on Every Agenda.",
    "subheadline": "Ankara will host 32 leaders, €70 billion in Ukraine aid, a defence industry bonanza, and the Iran question. Every outcome touches India's strategic calculus.",
    "slug": article2_slug,
    "body": article2_body,
    "category": "news",
    "vertical": "geopolitics",
    "status": "review",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "NATO", "url": "https://www.nato.int"},
        {"name": "GOV.UK", "url": "https://www.gov.uk"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com"},
        {"name": "The Sun", "url": "https://www.thesun.co.uk"},
    ]),
    "diaspora_angle": "NATO defence spending reshapes the job market for diaspora defence and tech professionals, while the Iran outcome directly determines oil prices, rupee strength, and economic stability for NRI families.",
    "image_caption": "",
    "image_attribution": "",
    "image_url": "",
}


# ═══════════════════════════════════════════════════════════════════════════
# MAIN — Source images, then insert articles
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        sys.exit(1)

    print("\n" + "="*70)
    print("ARTICLE 1: OPEC+ Oil Output → India Relief")
    print("="*70)

    # Image sourcing for Article 1: oil/OPEC theme
    img1_url, img1_attr = source_and_upload_image(
        queries=[
            "Strait of Hormuz oil tanker",
            "oil tanker Persian Gulf",
            "crude oil refinery India",
            "OPEC meeting oil production",
        ],
        slug=article1_slug,
        fallback_pexels_query="oil refinery industrial"
    )
    if img1_url:
        article1["image_url"] = img1_url
        article1["image_attribution"] = img1_attr
        article1["image_caption"] = "An oil tanker passes through the Strait of Hormuz, the critical shipping lane that carries a fifth of the world's oil supply"
    else:
        print("  ⚠ No image found for article 1")

    print(f"\n  Inserting article 1...")
    insert_article(article1)

    print("\n" + "="*70)
    print("ARTICLE 2: NATO Ankara Summit — India's Balancing Act")
    print("="*70)

    # Image sourcing for Article 2: NATO/Ankara theme
    img2_url, img2_attr = source_and_upload_image(
        queries=[
            "NATO summit leaders meeting",
            "NATO headquarters flag",
            "Ankara Turkey government building",
            "NATO defence alliance summit 2026",
        ],
        slug=article2_slug,
        fallback_pexels_query="NATO flags international summit"
    )
    if img2_url:
        article2["image_url"] = img2_url
        article2["image_attribution"] = img2_attr
        article2["image_caption"] = "NATO leaders gather for a summit that will shape the alliance's response to Iran, Ukraine, and the global defence industry"
    else:
        print("  ⚠ No image found for article 2")

    print(f"\n  Inserting article 2...")
    insert_article(article2)

    print("\n" + "="*70)
    print("DONE — 2 articles written and inserted with status='review'")
    print("="*70)
