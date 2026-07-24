#!/usr/bin/env python3
"""
Videshi News Writer — June 23, 2026 (00:30 UTC run)
2 NEW articles (both fresh, distinct from the most recent news pieces):
  1. UK PM Keir Starmer resigns; Andy Burnham the frontrunner to succeed him.
     What a Labour leadership change means for Britain's ~1.9m-strong Indian
     diaspora and the now-in-force India-UK CETA. (geopolitics / diaspora)
  2. India-US trade talks intensify as USTR Jamieson Greer arrives in New Delhi
     for two days, with New Delhi seeking a tariff edge over Asian peers — all
     shadowed by the deaths of three Indian seafarers in US Gulf strikes.
     (geopolitics / trade)
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

UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error: {e}")
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



# ─── Article 1: Starmer resigns / Burnham frontrunner / UK Indian diaspora ──

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Starmer resigns — what it means for British Indians")
    print("="*60)

    slug = "uk-pm-keir-starmer-resigns-andy-burnham-frontrunner-british-indian-diaspora-ceta-20260623"
    headline = "Britain Is About to Change Prime Ministers Again. Its 1.9 Million Indians Have a Stake in Who's Next."
    subheadline = "Keir Starmer resigned on Monday, the sixth UK prime minister in a decade, with Greater Manchester mayor Andy Burnham the clear frontrunner to replace him within weeks. For Britain's largest ethnic minority — and for a freshly-in-force India-UK trade deal — the succession is more than a Westminster drama."

    body = """Keir Starmer walked out of 10 Downing Street on Monday morning and, his voice cracking, told the country he was done. "I am putting the country I love first. I will resign as leader of the Labour Party," he said, ending a premiership that began with a landslide just two years ago and collapsed under the weight of dismal polling, lost local elections and a revolt by more than 80 of his own MPs. He is the sixth British prime minister in ten years — a churn that has become the defining feature of post-Brexit politics.

The frontrunner to replace him is Andy Burnham, the 56-year-old mayor of Greater Manchester, who returned to Parliament only last week after winning a by-election in Makerfield. Within hours of Starmer's announcement, a potential rival, Wes Streeting, threw his support behind Burnham, prompting Labour figures to predict less a contest than a coronation. Nominations open on July 9 and a new leader — and prime minister — could be installed by mid-July. The pound and British government bonds rallied on the prospect of a quick, orderly handover.

## Why Britain's Indians Are Watching

This is not a distant foreign story for the diaspora. People of Indian origin are Britain's single largest ethnic minority, numbering close to 1.9 million, and they are woven through British public life — in medicine and the National Health Service, in technology and finance, in small business and in Parliament itself, where the benches now hold more MPs of Indian heritage than ever before. A change at the top of British politics reverberates through a community that has spent decades building influence in the country it calls home.

Burnham is generally seen as further to the left than Starmer and one of Labour's most gifted communicators, with a populist economic message built around the cost of living and the regions outside London. His record as a "metro mayor" has made him a familiar champion of Britain's diverse northern cities, including the large South Asian communities of Greater Manchester. But he has yet to spell out a detailed agenda on the economy, immigration or foreign affairs — the very areas the diaspora cares most about — and he inherits a brutal fiscal inheritance, with UK borrowing costs the highest in the G7.

## A Trade Deal at a Delicate Moment

The timing is especially sensitive for India-UK relations. The Comprehensive Economic and Trade Agreement (CETA), signed in July 2025, is due to enter into force on July 15 — squarely in the window when a new prime minister is expected to be taking office. The deal eliminates tariffs on 99% of Indian exports to Britain, slashes duties on Scotch whisky and British cars heading the other way, and — crucially for professionals — includes a Double Contribution Convention that exempts Indian workers posted to the UK from paying social-security contributions there for up to three years.

The mobility chapter also carves out structured routes for Indian talent: short-term business visitors, intra-corporate transferees, an annual allocation of service-supplier visas, 3,000 post-study work places a year for Indian graduates, and 1,800 slots reserved for chefs, yoga instructors and classical musicians. None of it creates a path to permanent settlement, and Britain retains full control of its points-based immigration system — but the package is the most consequential India-UK economic agreement in a generation. A new government will be responsible for implementing it.

## What's Next

Whoever succeeds Starmer will take charge of a country in a sour mood, with Nigel Farage's Reform UK leading national polls and demanding an early general election. Burnham, if installed, will have to prove he can steady both the markets and his party while honouring commitments — including the India trade deal — made by his predecessor. For Britain's Indians, the practical questions are concrete: will CETA's professional visa routes open smoothly on schedule, will the broader immigration climate harden or ease, and will a Burnham government keep New Delhi as close a partner as Starmer's did?

The answers will come from a leader the country has not yet formally chosen. But the speed of the expected handover means the diaspora will not have to wait long to find out who will be steering Britain — and its relationship with India — through the rest of a turbulent decade."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "10 Downing Street London",
        "Andy Burnham mayor",
        "Palace of Westminster London",
        "Whitehall London government"
    ])
    img_caption = "10 Downing Street in London; Keir Starmer resigned as prime minister on June 22, 2026"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("10 downing street london")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Westminster, London, where Labour is set to pick Keir Starmer's successor within weeks"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters \u2014 UK's Starmer resigns, paving way for orderly transfer of power (June 22, 2026): Prime Minister Keir Starmer said he was quitting; frontrunner Andy Burnham, 56, who won a by-election in Makerfield last week, could become Britain's seventh leader in 10 years as early as next month; Wes Streeting backed Burnham; nominations open July 9, close mid-July, new leader by September or a mid-July coronation; the pound and gilts rallied",
            "People / PA \u2014 UK Prime Minister Keir Starmer Resigns (June 22, 2026): Starmer, 63, is the sixth prime minister in 10 years; resigned outside 10 Downing Street, became emotional thanking wife Victoria; came hours after Donald Trump pre-announced the resignation on Truth Social, saying Starmer 'failed badly' on immigration and energy",
            "Fox News \u2014 Keir Starmer resigns after Labour revolt and local election losses (June 22, 2026): more than 80 Labour MPs publicly called for Starmer to resign; ministers Jess Phillips and Miatta Fahnbulleh resigned and called for an orderly transition; criticism over the UK's handling of the US-Iran crisis",
            "GOV.UK / Press Information Bureau \u2014 UK-India Comprehensive Economic and Trade Agreement (CETA): signed July 24, 2025; eliminates tariffs on 99% of Indian exports to the UK; Double Contribution Convention exempts Indian workers and employers from UK social-security contributions for up to three years; Scotch whisky tariff cut from 150% to 75% immediately, to 40% by 2035; aims to double bilateral trade",
            "Free trade agreements of the United Kingdom (Wikipedia) / Ahlawat Associates 2026 Guide: the India-UK CETA will enter into force on July 15, 2026; the mobility chapter provides ~20,000 annual UK service-supplier visas for Indian nationals, 3,000 post-study work visas a year, 1,800 slots for chefs/yoga instructors/classical musicians, with no path to permanent settlement"
        ]),
        "diaspora_angle": "People of Indian origin are Britain's largest ethnic minority at close to 1.9 million, so a change of prime minister \u2014 just as the India-UK trade deal with its new professional-visa routes enters into force on July 15 \u2014 directly shapes the immigration climate, economic ties and political influence the British-Indian community depends on.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India-US trade talks / Greer visit / seafarers shadow ──────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India-US trade talks as USTR Greer arrives in Delhi")
    print("="*60)

    slug = "india-us-trade-deal-talks-ustr-jamieson-greer-delhi-tariff-edge-seafarers-deaths-20260623"
    headline = "America's Top Trade Envoy Lands in Delhi Tuesday. India Wants a Better Deal Than Its Rivals — and an Apology at Sea."
    subheadline = "US Trade Representative Jamieson Greer arrives for two days of talks as New Delhi pushes for a tariff edge over Vietnam and other Asian economies. The negotiations are unfolding under the shadow of three Indian sailors killed in US strikes in the Gulf."

    body = """The most senior American trade official is due in New Delhi on Tuesday for two days of negotiations, and India arrives at the table wanting two things that do not usually sit together: a commercial advantage over its Asian rivals, and accountability for the deaths of three of its citizens at the hands of the US Navy.

US Trade Representative Jamieson Greer's visit follows the first meeting in more than a year between Prime Minister Narendra Modi and President Donald Trump, held June 17 on the sidelines of the G7 summit in France — a thaw after a long stretch of strained ties. Both governments now want to convert that diplomatic warming into a signed trade pact, and the clock is loud: a temporary US 10% tariff on trading partners expires on July 24, and Indian officials would like a deal locked in before then. "The faster, the better," Commerce Minister Piyush Goyal said on Monday.

## India Wants to Beat the Field

New Delhi's ambition is not merely a deal but a better deal than its neighbours. "We are trying to work out with the US how they will ensure that we will get a comparative advantage, so that our exporters can benefit," Goyal said, framing the talks as a contest for preferential access against regional competitors such as Vietnam and other ASEAN economies. An initial understanding reached in February set tariffs on Indian goods at 18% in exchange for India lowering trade barriers and buying more American products — a rate that, at the time, undercut levies on rivals like Bangladesh and Vietnam.

That arrangement was knocked off course when the US Supreme Court invalidated Trump's sweeping global tariffs, and a continuing US Section 301 probe into alleged overcapacity and forced labour still hangs over the relationship. India now wants assurances written into any agreement that Washington will not slap on fresh tariffs after the ink dries, and is wary of renewed threats should the talks stall. Greer's office said the negotiations aim at "achieving fair, balanced, and reciprocal trade."

## The Shadow Over the Table

The talks are taking place against a far darker backdrop. In June, three Indian seafarers were killed when US forces struck the tanker MT Settebello in the Gulf of Oman, part of a campaign by US Central Command to enforce a blockade on Iranian oil. They were the first merchant sailors killed since the blockade began, and their deaths drew an unusually sharp rebuke from New Delhi. External Affairs Minister S. Jaishankar told US Secretary of State Marco Rubio that India lodged its "strong protest," calling the lethal actions against commercial shipping "not justified." The foreign ministry twice summoned American diplomats.

The episode cuts to a raw nerve for India, which supplies roughly 12% of the global merchant-shipping workforce — about 300,000 people — meaning Indian nationals crew vessels on virtually every major shipping route. With a fragile US-Iran peace deal now reducing tensions in the Strait of Hormuz and tanker traffic resuming, the immediate danger may be easing. But the deaths have injected a question of dignity and sovereignty into a relationship India is simultaneously trying to deepen on trade.

## Why It Matters to the Diaspora

For the Indian diaspora in the United States, a trade deal is more than an abstraction. Lower tariffs and smoother commerce strengthen the business and professional ties that bind Indian-American entrepreneurs, exporters and the technology sector to the home country. A pact that gives Indian goods a competitive edge could ripple through diaspora-owned businesses and the broader bilateral economy that so many NRIs are invested in, literally and figuratively.

But the seafarers' deaths are a reminder that the US-India relationship is not only about deals and dollars. The diaspora has watched New Delhi push back against Washington — protesting at the United Nations, summoning diplomats, demanding answers — even as it courts an American trade pact. How India balances those two impulses, commerce and conscience, over the next 48 hours in its own capital will say a great deal about the partnership the diaspora straddles every day."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "shipping containers port India trade",
        "cargo ship container terminal",
        "Mundra port India",
        "container ship ocean freight"
    ])
    img_caption = "A container terminal; US Trade Representative Jamieson Greer arrives in New Delhi for two days of trade talks"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("cargo ship container port")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Container shipping; India is pushing for a tariff edge over Asian rivals in talks with the US trade envoy"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters \u2014 India seeks tariff advantage over peers in push to finalise US trade deal (June 22, 2026): USTR Jamieson Greer to visit India Tuesday for two-day talks; New Delhi pushing for a pact on better terms than other Asian economies; follows the June 17 Modi-Trump meeting at the G7 summit in France; deaths of three Indian sailors in US Navy attacks added to tensions; February understanding set 18% tariffs on Indian goods; Washington's temporary 10% tariff expires July 24; a continuing US Section 301 probe persists; Trade Minister Piyush Goyal said 'the faster, the better'",
            "Reuters \u2014 India seeks preferential access through trade deal with US (June 22, 2026): Goyal said the US trade deal is taking longer to sign due to the 50% tariff imposed on goods; India aims to gain preferential access through the pact, speaking at a media conclave in New Delhi",
            "The Indian EYE \u2014 Strait of Hormuz Crisis Poses New Test for India-US Ties: India confirmed three Indian seafarers died after an attack on the vessel MT Settebello; US CENTCOM said it disabled multiple commercial vessels enforcing a blockade on Iranian oil; MT Marivex, MT Settebello and MT Jalveer all struck within a week in the Gulf of Oman, all with Indian crew",
            "The Indian EYE \u2014 Jaishankar voices strong protest to Rubio over death of Indian seafarers: EAM S. Jaishankar said he told US Secretary of State Marco Rubio of India's 'strong protest' at US Navy attacks in the Gulf that killed three Indian mariners, calling such lethal actions against commercial shipping 'not justified'; the MEA summoned the US Charg\u00e9 d'Affaires Jason Meeks",
            "New York Gazette \u2014 US Strikes on Ships Off Oman Continue After Deaths of Indian Sailors: the three killed on the Settebello were the first merchant sailors killed since the US began enforcing its blockade in April; India supplies 12% of the global merchant-shipping workforce, about 300,000 people, per Indian government figures; India's UN envoy Parvathaneni Harish said India was 'firmly opposed to attacks on merchant shipping'"
        ]),
        "diaspora_angle": "A US-India trade pact giving Indian goods a competitive edge would strengthen the business and professional ties Indian-American entrepreneurs and the tech sector depend on, even as the deaths of three Indian seafarers in US Gulf strikes force the diaspora to watch New Delhi balance courting Washington on trade with demanding accountability for its citizens.",
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
