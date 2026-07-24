#!/usr/bin/env python3
"""
Videshi News Writer — June 20, 2026 (16:30 UTC run)
2 NEW articles:
  1. Canada removals — Indians become the #1 deported nationality in 2026
     (diaspora-safety / immigration); CBSA Q1 data, 6,980 pending inventory
  2. India in no hurry to rush back to Gulf crude as Hormuz reopens — refiners
     stay on Russian barrels, drivers absorbed four pump hikes (economy / energy)
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

UA = "TheVideshi/1.0 (thevideshi.com)"


# ─── Image sourcing functions ────────────────────────────────────

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
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


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


# ─── Article 1: Canada removals — Indians #1 deported nationality ────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Canada removals — Indians #1 deported")
    print("="*60)

    slug = "canada-indians-top-deported-nationality-2026-cbsa-removals-record-pending-inventory-20260620"
    headline = "For the First Time in Six Years, Indians Are the Most Deported Nationality From Canada"
    subheadline = "Canada removed 1,712 Indian citizens in the first quarter of 2026 \u2014 nearly a third of all deportations \u2014 and a record 6,980 Indian cases now sit in the removal queue, a sharp signal of how far the welcome mat has been pulled back for the country's largest immigrant community."

    body = """For a generation of Indian families, Canada was the safe bet \u2014 the friendlier, more open alternative to an America that had grown hostile to newcomers. The latest enforcement figures from Ottawa complicate that story. In the first quarter of 2026, the Canada Border Services Agency removed 1,712 Indian citizens, making Indians the single largest nationality deported from the country and pushing them, for the first time since 2020, ahead of Mexicans.

Those 1,712 removals accounted for 32.5 percent of the 5,260 total deportations carried out between January and March \u2014 nearly one in three. It is a striking concentration for a single nationality, and a clear break from 2025, when Mexican nationals led annual removals with 4,837 against 3,779 Indians.

## A Record Pending Caseload

The bigger warning sits in the backlog. CBSA data shows Indians also hold the largest share of the agency's "removals in progress" inventory \u2014 6,980 cases, just over 22 percent of the 31,482 removals still working through the system. It is the largest such caseload on record for any nationality, and it strongly suggests the pace of Indian removals will continue, perhaps accelerate, through the rest of the year. At the current quarterly rate, total removals of Indian nationals in 2026 could nearly double last year's figure.

Canadian law sorts removals into three categories, and the distinction matters for anyone caught in the system. A departure order requires a person to leave within 30 days and, if complied with, leaves the door open to return later. An exclusion order bars re-entry for one year \u2014 up to five years where misrepresentation is involved. A deportation order, the most severe, permanently bans return unless the government grants special authorisation.

## What Is Actually Driving the Numbers

It would be easy to read the spike as a story about wrongdoing. The reality is more administrative. CBSA and immigration analysts attribute the bulk of removals not to criminality but to the back end of the asylum and study-permit booms of recent years: refused refugee claims, rejected asylum applications, expired permits, and other breaches of temporary-visa conditions. A share of the first-quarter increase was tied to Indian nationals removed over extortion-related violence, but officials stress that most cases are paperwork failures, not crimes.

That nuance is crucial. Indian nationals are Canada's largest international-student population and one of its biggest cohorts of temporary foreign workers, staffing manufacturing, food production, hospitality, caregiving and transport \u2014 sectors with chronic labour shortages. When a community is that large and that concentrated in temporary, time-limited status, it will also be over-represented the moment enforcement tightens. The removals are, in part, the mechanical consequence of the sheer scale of Indian migration to Canada over the past decade.

## A Tighter Canada Under Carney

The enforcement push is policy, not accident. Prime Minister Mark Carney's Liberal government has argued that immigration reform is necessary to bring population growth back into line with housing and public-service capacity, and the opposition Conservatives have pressed for even tighter controls \u2014 making enforcement one of the few issues on which Ottawa's rival camps broadly agree. Canada has paired a reduced permanent-residency target with a roughly 1.3-billion-dollar border-security plan built around drones and surveillance, and has moved to expedite removals.

The shift lands alongside a quieter trend that diaspora commentators have flagged all year: rising numbers of Indians choosing to leave Canada voluntarily, priced out by the cost of living in Toronto and Vancouver, pulled back by ageing parents, and increasingly tempted by an India where salaries, infrastructure and digital convenience have closed the gap.

## Why It Matters for the Diaspora

For Indian students and workers already in Canada, the message is not panic but precision. The removals are overwhelmingly about status \u2014 a lapsed permit, a refused claim, a missed deadline \u2014 rather than conduct. That makes vigilance the best defence: track expiry dates, file renewals early, take legal advice the moment a claim is refused, and never let a departure order quietly mature into an exclusion or deportation order that closes Canada off for years.

It also reframes a bigger decision for prospective migrants weighing Canada against the United States, the United Kingdom or Australia. The country that once marketed itself as the diaspora's open door is now visibly tightening it, and the asylum-and-permit route that carried hundreds of thousands of Indians north is the very channel now generating record removals. For families investing life savings in a child's overseas future, the new arithmetic rewards legal precision over optimism."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "Toronto's skyline; Indians are now the largest nationality deported from Canada"
    img_attribution = "Wikimedia Commons"

    for q in ["Toronto skyline Canada", "Canada Border Services Agency", "Pearson International Airport Toronto", "Toronto city Ontario"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "border" in t or "cbsa" in t:
                img_caption = "Canada Border Services Agency; Indians topped Canada's removals for the first time since 2020"
            elif "airport" in t or "pearson" in t:
                img_caption = "Toronto Pearson airport; Canada removed 1,712 Indian citizens in the first quarter of 2026"
            else:
                img_caption = "Toronto's skyline; Indians are now the largest nationality deported from Canada in 2026"
            break

    if not img_url:
        px = fetch_pexels_image("Toronto Canada city skyline")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A Canadian city skyline"

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
            "Canada Border Services Agency (CBSA) \u2014 Immigration removal statistics and removals-in-progress inventory by top citizenships (Q1 2026)",
            "VisaVerge \u2014 Canada Deportation Stats 2026: Indian Nationals Lead Removals (CBSA Q1 2026 data)",
            "Inshorts \u2014 Indians become most deported nationality from Canada in 2026 (April 30, 2026)",
            "Dainik Jagran English \u2014 Canada Deported 2,831 Indians in 2025 as Enforcement Tightens"
        ]),
        "diaspora_angle": "Indians are Canada's largest immigrant, student and temporary-worker community, so the country becoming its top deported nationality in 2026 \u2014 with a record 6,980 cases still pending removal \u2014 directly raises the stakes for hundreds of thousands of Indian families to track permit deadlines and file renewals early before a lapsed status hardens into a multi-year re-entry ban.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India in no hurry to return to Gulf crude as Hormuz reopens ──

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India in no hurry on Gulf crude post-Hormuz")
    print("="*60)

    slug = "india-no-hurry-gulf-crude-hormuz-reopens-russian-oil-pump-price-hikes-refiners-20260620"
    headline = "The Gulf's Oil Is Flowing Again Through Hormuz. India Is in No Rush to Go Back."
    subheadline = "With two months of crude already in tank and Russian barrels still cheap, Indian refiners are letting Middle Eastern suppliers wait \u2014 even as the war's legacy lingers in a record import bill and four straight hikes at the pump that diaspora families feel on every trip home."

    body = """For four months, the Strait of Hormuz \u2014 the narrow channel that normally carries about a fifth of the world's traded oil \u2014 was effectively shut, choked by the war between Iran on one side and the United States and Israel on the other. This week, under an interim U.S.-Iran agreement, the waterway began reopening, and Gulf producers are scrambling to turn stockpiled crude into exports. India, the world's third-largest oil importer, has every reason to celebrate. Instead, its refiners are in no hurry to rush back.

## Two Months in the Tank

The reason is simple inventory math. Indian refiners have enough crude to last roughly two months, so there is no need to scramble for the Middle Eastern cargoes now expected to flow through the reopened strait. According to a Bloomberg report, Gulf producers have already approached Indian buyers to start lifting committed volumes under their long-term annual contracts \u2014 and the buyers are not eager to oblige. New Delhi has yet to give state refiners the green light to send tankers into the Persian Gulf to load those contract volumes.

That caution reflects a hard lesson from the war. India had been among the biggest buyers of Middle Eastern crude, drawn by the favourable economics of geographic proximity \u2014 a closeness that turned into a vulnerability the moment tanker traffic seized up. When Hormuz closed, Indian refiners pivoted hard to Russian oil, helped by a sanction waiver from Washington, and that pivot has stuck.

## Russia Stays Cheap, and India Stays Loyal

Even with the strait reopening, the case for Russian barrels remains strong. Moscow's cargoes are still cheap, carrying discounts of one to two dollars a barrel to dated Brent, and those discounts may widen as global supply improves. Crucially, Russian crude is bought on a delivered basis \u2014 the seller arranges the shipping \u2014 which insulates Indian buyers from the freight-rate spike now hitting the market as global buyers rush to secure tankers amid doubts over how durable the ceasefire really is.

The numbers show how decisively India has rebalanced. In May, Russia was India's largest single supplier at about 1.92 million barrels a day, roughly 36.5 percent of total imports, while the UAE leapt to second place. Even as Washington's waivers on Russian crude formally expired, Indian refiners are expected to keep buying \u2014 the industry, sources say, has largely engineered workarounds. State-owned Indian Oil Corp has issued tenders to charter vessels for Gulf cargoes, but company sources caution that this is market-testing, not a signal of imminent return.

## The War's Bill Lands at Home

The disruption was not free, and ordinary Indians have already paid part of the cost. India's energy import bill soared by nearly 82 percent year-on-year in May, hitting about 18.7 billion dollars against 10.3 billion a year earlier, as crude imports rose 7.5 percent and LNG imports jumped 16 percent month-on-month. To manage the squeeze, the government urged energy conservation and \u2014 for the first time in years \u2014 allowed fuel retailers to raise pump prices. Indian drivers absorbed four separate hikes at the pump over a single month.

Analysts expect the reopening to release a wave of supply that should ease prices over time. Kpler estimated that some 93 million barrels of stranded non-Iranian crude could flood out of the Persian Gulf, with tens of millions more in Iranian barrels freed as U.S. restrictions lift. But traffic through Hormuz could take four to six months to return to pre-war levels, and shippers remain wary while questions linger over the transit terms Iran is setting.

## Why It Matters for the Diaspora

For the diaspora, oil is never just oil \u2014 it is the rupee, the airfare and the household budget back home. A bloated import bill widens India's trade deficit and weighs on the rupee, the same currency in which every remittance is ultimately spent. The four pump-price hikes ripple straight into transport, food and the cost of a family visit, the everyday inflation NRIs notice the moment they land.

India's refusal to rush back to Gulf crude is, in that sense, a quiet act of strategic patience that serves the diaspora's interests too. By keeping cheap Russian barrels flowing and forcing Gulf suppliers to compete for its custom, New Delhi is protecting itself against the next Hormuz shock and softening the price pressure that lands on Indian wallets at home and abroad. The strait is open again \u2014 but India has learned not to depend on it."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "An oil tanker at sea; India is in no hurry to resume Gulf crude purchases as the Strait of Hormuz reopens"
    img_attribution = "Wikimedia Commons"

    for q in ["crude oil tanker ship", "oil refinery India", "Strait of Hormuz tanker", "petroleum tanker sea"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "refiner" in t or "refinery" in t:
                img_caption = "An oil refinery; Indian refiners have two months of crude in tank and are in no rush to return to the Gulf"
            else:
                img_caption = "A crude oil tanker; India is letting Gulf suppliers wait even as the Strait of Hormuz reopens"
            break

    if not img_url:
        px = fetch_pexels_image("oil tanker ship sea crude")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A crude oil tanker at sea"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "OilPrice.com \u2014 India Isn't Rushing Back to Middle Eastern Oil Despite Hormuz Reopening (June 19, 2026)",
            "The Hindu BusinessLine / Bloomberg \u2014 Indian refiners in no hurry to return to West Asian oil as Hormuz reopens (June 19, 2026)",
            "Reuters \u2014 India's May oil supply from UAE tops pre-war levels as imports rise (June 18, 2026)",
            "Reuters \u2014 Hormuz reopening to release wave of oil supply, depress prices (Kpler estimates, June 17, 2026)"
        ]),
        "diaspora_angle": "India's strategy after the Hormuz reopening \u2014 staying on cheap Russian crude rather than rushing back to Gulf suppliers \u2014 directly shapes the rupee, the trade deficit and pump prices, the everyday inflation NRIs feel on remittances and every trip home after India absorbed a record energy bill and four fuel-price hikes during the war.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    print("\n" + "="*60)
    print(f"DONE. Inserted IDs: {[i for i in ids if i]}")
    print("="*60)
