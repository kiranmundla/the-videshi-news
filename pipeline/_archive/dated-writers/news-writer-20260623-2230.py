#!/usr/bin/env python3
"""
Videshi News Writer — June 23, 2026 (20:30 UTC run)
2 NEW articles, both fresh & distinct from prior runs (which covered CDSCO drug
quality, Adani Mundra airport, study-abroad slowdown, Anil Menon ISS, July visa
bulletin EB-2/EB-5, $750 expedited visa, CUET results, FCRA rules, Russian
crude, NSE IPO, India-China normalising, PMI, SpaceX wipeout, NEET re-exam,
Iran sanctions, FII return, USTR trade talks, UK PM Starmer resigns, Documented
Dreamers, F-1 duration of status, USCIS citizenship fee hike, Apache/M777 FMS,
RBI NRI deposits, Tata Electronics cyber breach):
  1. India tops the world's skilled-migration map (Deel Global Talent data):
     #1 source for US H-1B and #2 for UK skilled-worker visas and EU Blue
     Cards, with Indian hires commanding a wage PREMIUM over locals — debunking
     the cheap-labour myth. Plus early reverse-migration signals. (migration —
     diaspora-talent angle)
  2. UK-India Week 2026 opens at the University of Warwick: 10th edition of the
     biggest event in the UK-Indian calendar, anchored by a Gujarat ⇄ West
     Midlands state-to-region partnership on investment, advanced manufacturing,
     clean energy and life sciences. (diplomacy — diaspora-bridge angle)
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


# ─── Article 1: DC Circuit revives nationwide expedited removal ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: DC Circuit revives nationwide expedited removal")
    print("="*60)

    slug = "dc-circuit-revives-nationwide-expedited-removal-trump-deportation-indians-overstay-20260623"
    headline = "A US Court Just Cleared the Way to Deport People From Anywhere in America \u2014 Without a Judge"
    subheadline = "A divided federal appeals court has revived the Trump administration's power to fast-track deportations of undocumented immigrants found anywhere in the country, not just at the border. The two-year test at the centre of the ruling is exactly where visa overstays \u2014 a quiet but real slice of the Indian story in America \u2014 are most exposed."

    body = """A federal appeals court in Washington handed the Trump administration a major victory on Tuesday, clearing the way for immigration agents to rapidly deport undocumented immigrants found anywhere in the United States \u2014 without first putting them before an immigration judge. For the Indian community in America, the ruling lands on an uncomfortable fault line: the process turns on a two-year presence test, and visa overstays are exactly the kind of case it is built to catch.

The US Court of Appeals for the District of Columbia Circuit ruled 2-1 to overturn an August 2025 decision that had blocked the Department of Homeland Security from expanding "expedited removal" \u2014 a fast-track deportation tool \u2014 across the entire country. The two judges in the majority, Justin Walker and Neomi Rao, were both appointed by President Donald Trump; the dissenter, Robert Wilkins, was appointed by President Barack Obama.

## What Expedited Removal Actually Does

Expedited removal lets immigration officers deport someone in days, sometimes hours, with no hearing before a judge. For nearly three decades it was used almost exclusively at the border, against people caught within 100 miles of it and within two weeks of arriving. In January 2025, the administration moved to apply it nationwide \u2014 to anyone, anywhere in the US, who cannot prove they have been continuously present in the country for two years or more.

A trial judge, US District Judge Jia Cobb, blocked that expansion last year, warning it left "too much room for error," including the rapid removal of people with legitimate reasons to stay. The DC Circuit disagreed. Writing for the majority, Judge Walker said DHS was entitled to apply "expedited removal to the maximum extent allowed by Congress," and that immigrants are given notice and a chance to object \u2014 including by proving two years' continuous presence \u2014 which satisfies due process.

## The Two-Year Line Is the Whole Game

The ruling matters to the Indian community for one specific reason: the burden of proof. Under the revived policy, the onus is on the individual to demonstrate, on the spot, that they have been in the country for at least two years. Those who cannot are exposed to summary removal. Asylum seekers who pass a credible-fear screening are exempt, as are people who can document the two-year threshold.

This is the zone where visa overstays sit. India is one of the largest sources of legal immigration to the United States, but a less-discussed corner of that story is the population that arrived on valid student, work or visitor visas and then fell out of status \u2014 a lapsed F-1, an expired H-1B with no extension, a B-2 visitor who stayed. People in that situation are not "border crossers," but under a nationwide expedited-removal regime they can still be swept up if they cannot immediately prove how long they have been present. Carrying documentation suddenly stops being paperwork and becomes a shield.

## A Crackdown Already Running at Scale

The decision feeds into an enforcement push that is already operating at record volume. Nearly 900,000 people have been deported under the administration, with removal flights hitting a new monthly high in May. DHS celebrated the ruling, with its general counsel saying on social media that the court had "vindicated" the decision to apply the law "as written," and repeating the administration's offer of a $2,600 stipend to those who self-deport.

Civil-rights groups see it differently. Make the Road New York, the advocacy organisation that brought the original challenge, has argued the crackdown has spread fear that people will be "seized suddenly by masked agents and removed from the US with little recourse." The dissent and the lower court both warned that speed comes at the cost of accuracy \u2014 and that wrongful removals, once carried out, are hard to undo.

## Why the Diaspora Should Care

For the overwhelming majority of Indians in America \u2014 citizens, green-card holders, and those in valid visa status \u2014 nothing changes overnight. But the ruling sharpens a message that immigration lawyers have been pressing for months: status lapses that were once a bureaucratic headache now carry real, fast-moving consequences. An H-1B holder between jobs, a student who has dropped below a full course load, a family member whose extension is pending \u2014 all have a stronger reason than ever to keep their paperwork current and their proof of continuous presence close to hand.

It also reshapes the calculus for mixed-status families, where one member's lapsed status can now trigger a far swifter process than the years-long immigration-court backlog most people assumed they could rely on. The practical advice from the immigration bar is blunt: know your status, document your time in the country, and have a lawyer's number ready before you need it.

## What's Next

The fight is not over. The ruling lifts the block "for now," and the challengers can seek review by the full DC Circuit or the Supreme Court, which has yet to weigh in on whether nationwide expedited removal squares with the Constitution's due-process guarantees. In the meantime, the policy can be enforced, and DHS has signalled it intends to use the authority aggressively. For a community that has built much of its American success on legal, documented migration, the new rules raise the cost of any gap in that documentation \u2014 and put a premium on knowing, and being able to prove, exactly where you stand."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: ICE / DHS / immigration enforcement / courthouse. No single named person as hero.
    img_url, ctitle = pick_commons([
        "US Immigration and Customs Enforcement officers",
        "Department of Homeland Security building Washington",
        "ICE detention facility United States",
        "E. Barrett Prettyman Courthouse Washington DC",
        "US immigration enforcement"
    ])
    img_caption = "US immigration enforcement; a divided appeals court revived nationwide fast-track deportations"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("courthouse government building law")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A federal appeals court revived the administration's power to fast-track deportations nationwide"

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
            "Reuters (reuters.com, June 23, 2026) \u2014 'Trump administration can expand fast-track deportation process, US appeals court rules': a panel of the US Court of Appeals for the DC Circuit ruled 2-1 to overturn an August 2025 decision by US District Judge Jia Cobb that blocked DHS from expanding expedited removal; the policy, adopted January 2025, covers non-citizens apprehended anywhere in the US who cannot show two years' continuous presence; Judge Justin Walker (Trump appointee) wrote that DHS could apply expedited removal 'to the maximum extent allowed by Congress' and that migrants receive notice and a chance to object.",
            "CNN (cnn.com, June 23, 2026) \u2014 'Trump effort to expand speedy deportations of migrants can proceed, appeals court rules': the DC Circuit allows the administration to widen who is subject to expedited removal, which permits removal without a hearing before an immigration judge; Judges Walker and Neomi Rao (both Trump appointees) in the majority, Judge Robert Wilkins (Obama appointee) dissenting; DHS General Counsel James Percival celebrated the ruling on X and repeated a $2,600 self-deportation stipend offer.",
            "Bloomberg Law (news.bloomberglaw.com, June 23, 2026) \u2014 'Trump Fast Deportation Rule Cleared by Appeals Court for Now': divided court lifted the hold on the January 2025 policy; the rule expands a tool previously used only near the border and only for recent arrivals; District Judge Jia Cobb had held the expansion left too much room for irreversible error.",
            "Washington Examiner (washingtonexaminer.com, June 23, 2026) \u2014 'ICE may deport illegal immigrants without judge approval, appeals court rules': exemptions for those who prove two consecutive years of US presence and asylum seekers who pass credible-fear screening; nearly 900,000 deported under the administration with removal flights at a new high in May."
        ]),
        "diaspora_angle": "The revived policy turns on a two-year continuous-presence test enforced anywhere in the US \u2014 the exact zone where Indian visa overstays (lapsed F-1s, expired H-1Bs, overstayed visitor visas) are most exposed, making current documentation and proof of time in the country an urgent priority for anyone in or near a status gap, and reshaping the calculus for mixed-status diaspora families who can no longer count on the slow immigration-court backlog.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Sensex plunges 893 points, snapping a 7-session rally ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Sensex plunges 893 points on weak PMI, monsoon worry")
    print("="*60)

    slug = "sensex-falls-893-points-nifty-pmi-three-month-low-monsoon-it-metals-drag-20260623"
    headline = "India's Market Rally Just Hit a Wall. The Warning Sign Wasn't Oil \u2014 It Was the Monsoon."
    subheadline = "The Sensex tumbled 893 points and the Nifty fell 1.16% on Tuesday, snapping a seven-session rally, after a survey showed private-sector growth cooling to a three-month low and a patchy monsoon spooked investors. For diaspora investors who watch Indian equities and the rupee, it was a reminder of how fast the mood can turn."

    body = """India's stock market, which had been on its best run in months, hit a wall on Tuesday. The benchmark Sensex closed 893 points lower \u2014 down 1.16% at 76,200.68 \u2014 and the broader Nifty 50 fell an identical 1.16% to 23,824.10, snapping a seven-session winning streak. The trigger was not the geopolitics that had dominated headlines for weeks, but two distinctly domestic worries: a sudden cooling in business activity and a monsoon that is still running well short of normal.

The fall wiped out part of a powerful rally. Over the previous seven sessions, the Sensex and Nifty had surged 4.4% and 4.1% respectively, lifted by tumbling oil prices and easing Middle East tensions after the US-Iran deal reopened shipping through the Strait of Hormuz. Brent crude, which spiked above $126 a barrel during the Iran war, has since collapsed about 39% and slipped further on Tuesday to around $77. But with that tailwind largely priced in, investors went looking for the next signal \u2014 and what they found gave them reason to book profits.

## A Cooling Economy and a Late Monsoon

The day's decisive data point was the closely watched purchasing managers' survey, which showed India's private-sector growth easing to a three-month low in June. Services activity slumped to a 17-month low and manufacturing growth slowed to a three-month low, as demand and business confidence cooled. It was a jarring counterpoint to the narrative of India as the world's fastest-growing major economy, and it dovetailed with mounting anxiety over the monsoon \u2014 the rains that water more than half of India's farmland and shape rural demand for everything from tractors to soap. Three weeks into the season, the rain gauges have been running roughly a third below normal.

The combination spooked a market that had run hard and fast. "Soft PMI readings, combined with persistent concerns over the monsoon shortfall, have dented investor confidence and sparked profit-taking after the recent rally," said Anita Gandhi, head of institutional business at Arihant Capital Markets.

## IT and Metals Lead the Fall

The selling was broad but concentrated in two heavyweight sectors. The Nifty IT index slid 2.2% after Jefferies and Morgan Stanley flagged soft demand signals in the wake of bellwether Accenture's weak outlook \u2014 a warning that the global technology-services spending that underpins India's biggest export industry may be slowing. Adding to the pressure were rising expectations of a possible US Federal Reserve rate hike later this year, which would squeeze the American client budgets that Indian IT firms depend on.

The Nifty Metals index fell even harder, dropping 3.2% as global metal prices weakened and Fed-hike fears dimmed the demand outlook for industrial commodities. Fourteen of the 16 major sectors ended in the red. The lone bright spot was pharmaceuticals: the Nifty Pharma index rose nearly 1% and touched an all-time high during the session, a defensive haven as the rest of the market sold off. Across the exchanges, decliners swamped advancers by nearly two to one.

## A Rally Built on Borrowed Calm

Tuesday's reversal exposed the fragile foundation of the recent surge. Much of the gain had rested on relief \u2014 cheaper oil, a Middle East ceasefire, and the return of foreign investors who, after pulling a record $30 billion out of India, had begun buying back in. Those are real positives, but they are also external and reversible. The PMI and monsoon worries were a reminder that the domestic engine \u2014 consumer demand, business investment, the farm economy \u2014 has its own rhythm, and right now that rhythm is slowing.

## Why the Diaspora Should Care

For the millions of non-resident Indians with money tied to India, Tuesday was a useful jolt. Many in the diaspora hold Indian equities directly, through mutual funds, or via the NRI deposit and investment routes that banks have been marketing hard \u2014 including the Reserve Bank's recent push to draw dollar deposits and shore up the rupee. A 1.16% single-day drop is not a crisis, but the reasons behind it speak directly to NRI portfolios: the health of the IT sector that employs so much of the diaspora and drives so many Indian holdings, the trajectory of the rupee, and the strength of the domestic demand story that underpins long-term returns.

The monsoon angle in particular is one diaspora investors often underweight. India's rains remain the single biggest swing factor for rural consumption, food inflation and, ultimately, the interest-rate decisions that move the rupee \u2014 the exchange rate that determines how far remittances stretch and what Indian assets are worth in dollar terms. A weak monsoon can ripple all the way to the value of an NRI's portfolio back home.

## What's Next

Attention now turns to whether the monsoon catches up in the coming weeks \u2014 the India Meteorological Department's forecasts will be watched closely \u2014 and to global cues, especially any firming of expectations around a Fed rate move. Technical analysts see the Nifty holding key support around the psychological 24,000 mark, with resistance overhead near 24,180; a decisive break either way will set the near-term tone. After a rally powered largely by falling oil and easing war fears, the market is now being asked a harder question: whether India's domestic growth story is strong enough to carry it from here."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: BSE / NSE / Indian stock market / Mumbai financial district. No single named person.
    img_url, ctitle = pick_commons([
        "Bombay Stock Exchange building Mumbai",
        "National Stock Exchange India building",
        "BSE building Dalal Street Mumbai",
        "stock market trading screen India",
        "Mumbai Bandra Kurla Complex financial"
    ])
    img_caption = "India's stock market; the Sensex fell 893 points on Tuesday, snapping a seven-session rally"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("stock market trading screen finance chart")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Indian equities tumbled on Tuesday as weak business data and monsoon worries triggered profit-taking"

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
            "Reuters (reuters.com, June 23, 2026) \u2014 'IT, metals drag Indian shares; weak business data, monsoon worries weigh': the Nifty 50 and Sensex each fell 1.16% to 23,824.10 and 76,200.68; both opened flat then slipped after PMI data showed private-sector growth at a three-month low, services at a 17-month low, manufacturing at a three-month low; the Nifty IT index slid 2.2% (Jefferies/Morgan Stanley flagged soft demand after Accenture's weak outlook; Fed rate-hike expectations), the Nifty Metals index lost 3.2%; 14 of 16 major sectors declined; the Nifty and Sensex had gained 4.1% and 4.4% over the previous seven sessions; Brent fell 0.7% to $77.4, down ~39% from a $126.4 wartime peak; quote from Anita Gandhi, Arihant Capital Markets.",
            "The Hindu BusinessLine (thehindubusinessline.com, June 23, 2026) \u2014 'Stock Market Today, June 23: Sensex falls 893 points, Nifty ends lower as IT and metal stocks drag markets': Sensex settled 893.39 points (1.16%) lower at 76,200.68 and Nifty 50 fell 278.80 points (1.16%) to 23,824.10; Nifty Metal -3.22%, Nifty IT -2.23%, Nifty Pharma +0.92% and hit an all-time high of 25,294.50 during the session; of 4,447 stocks traded, 1,492 advanced and 2,788 declined; private-sector growth slipped to a three-month low in June per PMI.",
            "Background \u2014 India market context (June 2026): the recent rally was driven by falling crude prices and easing Middle East tensions after the US-Iran deal reopened the Strait of Hormuz, plus the return of foreign investors after a record ~$30 billion of outflows; the RBI has been marketing NRI deposit schemes to draw dollar inflows and support the rupee; India's monsoon, three weeks in, was running roughly a third below normal, raising concerns for rural demand and food inflation."
        ]),
        "diaspora_angle": "NRIs hold Indian equities directly, through funds, and via the NRI deposit routes banks (and the RBI) have been pushing to shore up the rupee \u2014 so a sell-off driven by a slowing IT sector, Fed-hike fears and a weak monsoon speaks straight to diaspora portfolios, where the rupee's path determines how far remittances stretch and what Indian assets are worth in dollars.",
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
