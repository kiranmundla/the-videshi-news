#!/usr/bin/env python3
"""
Videshi News Writer — June 26, 2026 (00:30 UTC / June 25 17:30 PDT run)
2 NEW articles, dedup-checked against last ~50 news/nri-world articles:
  1. Canada's record work-permit expiry wave — ~1.4M permits expire in 2026,
     ~770k+ by end-June, Indians roughly half; only 380k PR spots; out-of-status
     risk, maintained status, restoration window. Diaspora-central. NOT covered
     (prior Canada pieces were the "best time ever to apply" framing and the
     defence-procurement story, not the expiry/out-of-status wave).
  2. "RAMageddon" memory-chip surge — DRAM up to ~89% q/q, Apple raises Mac/iPad
     prices, IDC sees worst-ever smartphone decline (~14%); India angle: world's
     #2 smartphone market + Micron's Sanand (Gujarat) plant. NOT covered.
"""
import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
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
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  \u2713 Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  \u26a0 Download failed ({r.status_code}): {url[:80]}")
            try:
                tmp = f"/tmp/{slug}_src"
                subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
                with open(tmp, "rb") as f:
                    content = f.read()
                if len(content) < 5000:
                    return None
                r_content = content
            except Exception:
                return None
        else:
            r_content = r.content
        ct = r.headers.get("Content-Type", "") if r.status_code == 200 else "image/jpeg"
        if "image" not in ct and len(r_content) < 5000:
            print(f"  \u26a0 Not an image or too small: {ct}, {len(r_content)} bytes")
            return None

        from PIL import Image
        img = Image.open(io.BytesIO(r_content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()

        if len(compressed) < 5000:
            print(f"  \u26a0 Compressed image too small: {len(compressed)} bytes")
            return None

        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"

        requests.delete(upload_url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY
        })

        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=30)

        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def pick_commons(queries, min_width=900):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            return pick["url"], pick.get("title", "")
    return None, ""


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# \u2500\u2500\u2500 Article 1: Canada work-permit expiry wave hits Indians \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Canada work-permit expiry wave")
    print("="*60)

    slug = "canada-work-permit-expiry-wave-2026-indians-out-of-status-pgwp-pr-shortage-20260625"
    headline = "Canada Issued Millions of Work Permits. Now They're Expiring \u2014 and Indians Are Half the Wave."
    subheadline = "About 1.4 million permits lapse in Canada this year against just 380,000 permanent-residency slots. The arithmetic doesn't work, and the people it strands are disproportionately Indian."

    body = """For a decade, Canada was the destination that said yes. It handed out study permits and post-graduation work permits at a record clip, and a generation of young Indians built their futures on the promise that the document in their hand was a bridge to something permanent. In 2026, that bridge is running out of road.

Canada is now living through the single largest work-permit expiry wave in its history. According to immigration analysts reading the federal government's own data, roughly 1.4 million work permits will expire across 2026 \u2014 about 770,000 of them by the end of June alone \u2014 with a further wave already queued for 2027. And no nationality is more exposed than Indians, who for years have accounted for close to half of Canada's temporary-resident approvals.

## The Arithmetic of a Squeeze

The crunch is not an accident; it is arithmetic catching up. Canada issued historically high volumes of work permits during the pandemic-recovery years \u2014 more than 765,000 under the International Mobility Program in 2023, and over 900,000 across its main programs in 2024. Permits issued in a tight window expire in a tight window, and that window is now.

What makes 2026 different is what waits on the other side. The government's 2026\u20132028 immigration plan allocates only about 380,000 permanent-residency spots for the year. Set that against 1.4 million expiring permits and the gap exceeds a million people \u2014 even if every one of them qualified, which they do not. Immigration consultant Kanwar Seirah has warned that by mid-2026, at least two million people in Canada could be living without legal status, with Indians making up roughly half, a figure he called "a very conservative estimate."

## Four Doors, Most of Them Narrowing

When a permit lapses, the holder lands in one of a handful of situations, and only some are survivable. A person who applied to renew before their permit expired enters "maintained status" \u2014 the right to stay, and usually to keep working under the same conditions, while the file is processed. But processing now drags: a work-permit application from inside Canada already takes around 258 days, and peak-volume months are projected to stretch that further.

Those who missed the deadline fall out of status. They must stop working immediately, and have a 90-day window to apply for restoration \u2014 paying an extra fee, and hoping an officer agrees. Restoration is not guaranteed. And for a large share of this wave, the government's own assumption, analysts say, is the bluntest outcome of all: that people will simply go home. Toronto immigration lawyer Lou Janssen Dangzalan has called that assumption "overly optimistic about compliance behaviour."

## A Planned Reset, Not a Glitch

Ottawa is not hiding the intent. It has said openly that it wants to bring Canada's temporary-resident population down from roughly 7% of the country to under 5% by the end of 2027. To hit that target with 1.4 million permits expiring and only 380,000 PR places, the math demands that large numbers leave. Some analysts have described it, uncharitably but not inaccurately, as a "planned failure" at scale \u2014 a deliberate narrowing of pathways meant to induce departure. The one-off TR-to-PR pathway of 2021, which fast-tracked 90,000 people, is pointedly not being repeated.

There are still real options for those who act early: bridging open work permits for people with a pending PR application, employer-backed permits via a fresh labour-market assessment, the Canadian Experience Class for those with a year of skilled Canadian work, and provincial nominee programs, whose allocations rose more than 65% this year. The common thread is that waiting is the worst strategy.

## Why It Matters for the Diaspora

For Indian families, this is not an abstract policy debate \u2014 it is a household one. The students who went north on the understanding that a Canadian degree plus Canadian work experience equalled a Canadian future are precisely the cohort now staring at an expiry date with no PR slot behind it. Many are spousal-permit holders whose status is tethered to a partner's, in communities concentrated in Ontario, British Columbia and Alberta where the squeeze will land hardest.

The reverberations reach back to India, too. A returning cohort means foregone remittances, the awkward economics of a foreign degree that no longer guarantees foreign settlement, and a fresh wave of talent re-entering a domestic job market that is itself tightening. For the next aspirant weighing destinations, the lesson of 2026 is sobering: an open door is not the same as a settled future, and the country that once said yes the loudest is now doing the quiet math of who it can afford to keep."""

    img_url, ititle = pick_commons([
        "Immigration Refugees and Citizenship Canada building",
        "Canada immigration office",
        "Toronto Pearson International Airport arrivals",
        "Canada border services",
        "Parliament Hill Ottawa"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Canada faces its largest-ever work-permit expiry wave in 2026, with Indians making up roughly half of those affected"

    if not img_url:
        px = fetch_pexels_image("canada flag immigration document passport")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "About 1.4 million Canadian work permits expire in 2026 against only 380,000 permanent-residency slots"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "ImmigrationNewsCanada (immigrationnewscanada.ca, March 2026) \u2014 '300,000+ Work Permits Set To Expire By End Of March 2026: What Happens Now?': IRCC ATIP data shows 314,538 work permits projected to expire Jan\u2013Mar 2026 (single largest quarter in history), ~770,000+ by end-June 2026 and ~1.4 million for full-year 2026; the 2026\u20132028 Immigration Levels Plan allocates only 380,000 PR spots for 2026; the largest expiring groups are PGWP and spousal open-work-permit holders, disproportionately from India (close to 50% of temporary-resident approvals); four outcomes (renewal, maintained status, out-of-status/90-day restoration with $229 fee, departure); current inside-Canada work-permit processing ~258 days; government targets reducing temporary residents from ~7% to under 5% of population by end-2027; Toronto lawyer Lou Janssen Dangzalan called the assumption people will leave 'overly optimistic about compliance behaviour.'",
            "Livemint (livemint.com, 2026) \u2014 'Canada immigration: Over 1 million Indians at risk of losing legal status, warns consultant': immigration consultant Kanwar Seirah (citing IRCC data) said ~1,053,000 work permits expired by end-2025 and another 927,000 are set to expire in 2026; ~315,000 expiries expected in Q1 2026 alone vs 291,000+ in Q4 2025; he estimated at least two million people in Canada could be without legal status by mid-2026, with Indians roughly half \u2014 'a very conservative estimate'; recent measures have made renewal and PR transition more restrictive, especially for temporary workers and international students.",
            "Fragomen / The Times of India (fragomen.com, June 2026) \u2014 'Canada Committed To Increase Immigration, Delays a Temporary Glitch, Says Expert': partner David Crawford notes Indian nationals are the largest source of new Canadian permanent residents annually, and discusses the government's efforts to cut processing delays and increase skilled-worker recruitment, plus advice for Indian students aiming to settle via PR."
        ]),
        "diaspora_angle": "Indians make up roughly half of Canada's temporary-resident approvals, so the 2026 expiry wave \u2014 1.4 million permits lapsing against just 380,000 PR slots \u2014 puts a uniquely large share of Indian students, workers and their spouses at risk of falling out of status or being forced to leave, with knock-on effects for remittances and a talent influx back into India.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: 'RAMageddon' memory surge and India's gadget bill \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: RAMageddon memory surge hits India's gadget prices")
    print("="*60)

    slug = "ramageddon-memory-chip-price-surge-apple-hikes-india-smartphone-laptop-prices-micron-2026-20260625"
    headline = "AI's Hunger for Memory Just Made Your Next Phone More Expensive. India Will Feel It Hardest."
    subheadline = "Memory-chip prices have leapt as much as 89% in a single quarter as AI data centres swallow the supply. Apple is already raising prices \u2014 and the world's second-biggest phone market is squarely in the blast radius."

    body = """The AI boom has minted trillion-dollar fortunes and reordered the technology industry. It has also, quietly, made the device in your pocket more expensive \u2014 and the bill is about to land in the one of the world's largest smartphone markets.

The culprit is a shortage of memory chips so acute that the tech press has christened it "RAMageddon." Prices of DRAM, the memory in virtually every phone, laptop and television, rose as much as 98% in the first quarter of 2026, and industry tracker TrendForce expects another 58\u201363% jump in the current quarter. A separate analysis put the quarter-on-quarter rise in some consumer memory modules at up to 89%. This is not a normal cyclical wobble. It is a structural reallocation of the world's chip-making capacity toward the high-margin memory that artificial-intelligence data centres devour.

## When Apple Blinks, Everyone Pays

The clearest signal came this week from the company with the most pricing power on earth. Apple raised prices on its iPads and MacBooks, saying it could "no longer shield customers" from soaring memory costs \u2014 lifting its entry MacBook from $599 to $699 and an iPad Air from $599 to $749, among other increases. "We have never seen a component price increase this much, this quickly," the company said.

If Apple, with the industry's deepest supplier relationships, is raising prices, smaller rivals have nowhere to hide. Dell, HP, Lenovo, Xiaomi and Microsoft have all signalled or enacted increases. The demand picture is grim: research firm IDC expects the global smartphone market to suffer its biggest-ever annual decline this year, nearly 14%, with PCs down 11.3%.

## Why the Squeeze Won't Ease Soon

The shortage is being driven from the top. Memory makers Micron, Samsung and SK Hynix are pouring capacity into high-bandwidth memory for AI accelerators \u2014 Micron alone just reported quarterly revenue quadrupling to over $41 billion and locked in some $22 billion of long-term, take-or-pay customer commitments. With the most profitable buyers underwriting whole factory expansions, ordinary consumer memory is an afterthought. Micron's leadership has said it has no clear line of sight on when supply will catch up with demand, and several analysts expect the crunch to persist into 2027.

## India in the Blast Radius

For India, this is not a distant Silicon Valley story \u2014 it is a price tag. India is the world's second-largest smartphone market, and one overwhelmingly built on the affordable and mid-range handsets that are most sensitive to component costs. When the memory inside a sub-\u20b920,000 phone jumps in price, there is little margin to absorb it; the increase flows straight to the buyer. The same logic hits the budget laptops that power India's vast student and gig-economy base, and the data-centre build-out that India's own technology ambitions depend on.

There is an irony, too. India has spent the past two years courting exactly this industry. Micron is building its first Indian assembly-and-test facility at Sanand in Gujarat, the flagship of a national push to plant the country on the semiconductor map. That plant packages and tests memory rather than fabricating the silicon wafers at the heart of the shortage, so it offers no quick relief at the checkout counter \u2014 but it is a marker of where India wants to be when the next cycle turns.

## What the Diaspora Should Watch

For the global Indian, the effects ripple in both directions. NRIs shopping for phones and laptops in the United States, Britain or the Gulf are already seeing the same hikes Apple just confirmed, and the festive-season upgrade may cost meaningfully more this year. For families back home, the squeeze lands on aspirational purchases \u2014 a student's first laptop, a parent's new phone \u2014 at a time when a weak rupee is already making imported electronics dearer.

But there is a longer game worth tracking. Diaspora investors and technologists have a front-row seat to a structural shift: memory has gone from commodity to strategic asset, and the companies that control it are being valued accordingly. India's bet on domestic chip packaging, however modest against the scale of the shortage, is part of a slow attempt to stop being only a price-taker in a market the AI era has turned upside down. For now, though, the simplest advice is the oldest: if you were planning to buy a gadget, buying sooner may cost less than buying later."""

    img_url, ititle = pick_commons([
        "DRAM memory module",
        "DDR4 RAM module",
        "computer memory chips",
        "semiconductor memory wafer",
        "RAM stick computer"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Memory modules like these have surged in price as AI data centres absorb global chip supply"

    if not img_url:
        px = fetch_pexels_image("computer memory ram chips circuit")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A memory-chip shortage dubbed 'RAMageddon' is pushing up phone and laptop prices worldwide"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters (reuters.com, June 25, 2026) \u2014 'Apple raises prices of MacBooks, iPads as memory costs skyrocket': Apple raised iPad and MacBook prices, saying it could no longer shield customers from soaring memory and storage costs; entry MacBook Neo from $599 to $699, MacBook Air 512GB to $1,299 from $1,099, MacBook Pro 1TB to $1,999 from $1,699, iPad Air 128GB from $599 to $749; 'We have never seen a component price increase this much, this quickly'; DRAM prices rose as much as 98% in Q1 2026 and are set to jump another 58\u201363% in the current quarter per TrendForce; surge dubbed 'RAMageddon' driven by AI data-centre buildout; IDC estimates the smartphone market will see its biggest-ever annual decline of ~14% this year and PCs will fall 11.3%; Tim Cook had warned of 'significantly higher memory costs.'",
            "Reuters (reuters.com, June 25, 2026) \u2014 'Micron forecasts strong quarterly results on soaring memory chip demand' / 'Micron joins rivals pitching AI deals as cure for memory's boom-bust cycle': Micron said customers including Nvidia committed $22 billion in long-term take-or-pay deals across 16 strategic customer agreements; remaining performance obligations ~$100 billion; CEO Sanjay Mehrotra said there is no line of sight on when memory supply will catch up with demand; memory makers are prioritizing high-bandwidth memory for AI, leaving consumer electronics makers scrambling and driving product prices up; SK Hynix plans to raise up to $29.4 billion.",
            "Wccftech / SigmaIntel (wccftech.com, June 2026) \u2014 'Memory Shortages Have Destroyed The Consumer Segment As DRAM Prices Surge By Up To 89% In Q2 2026': consumer DRAM prices rose up to 89% quarter-on-quarter; a 16Gb DRAM module averaged $28.5 vs $19.2 prior quarter (+49%); a 16GB DDR4 stick rose to $207.1 from $137 (+51%); 96Gb LPDDR5X modules rose to $145.9 from $77.1 (+89%), the single biggest jump.",
            "TechCrunch (techcrunch.com, June 24, 2026) \u2014 'The memory chip crunch is paying off for this US company': the AI boom has produced a serious memory-chip shortage some predict could persist through 2027; Micron's shares rose from ~$83 in early 2024 to $1,048.51, with Q3 revenue quadrupling to $41.45 billion and profit rising from $1.88 billion to $28.2 billion year-over-year; Micron also struck a deal to supply Anthropic and invested in its funding round."
        ]),
        "diaspora_angle": "India is the world's second-largest smartphone market and overwhelmingly price-sensitive, so the AI-driven 'RAMageddon' memory surge \u2014 already forcing Apple and rivals to raise prices \u2014 will hit Indian buyers of budget phones and laptops hard, even as Micron's new Sanand plant in Gujarat marks India's bet to climb the semiconductor ladder; NRIs face the same hikes abroad and a longer-term investment story in memory's shift from commodity to strategic asset.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-26 00:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (Canada permit expiry wave): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (RAMageddon memory surge): {'OK id=' + str(id2) if id2 else 'FAILED'}")
