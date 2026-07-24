#!/usr/bin/env python3
"""
Videshi News Writer — June 25, 2026 (10:30 UTC / 03:30 PDT run)
2 NEW articles, dedup-checked against last ~40 news articles:
  1. Gold (and silver) crash below $4,000/oz for the first time since Nov 2025
     — down ~25-30% from January record — on a strong dollar, hawkish Fed and
     easing Iran-war fears. India angle: 24k gold off ~Rs 31,000/10g from peak;
     India's own gold-import curbs to defend the rupee are part of the global
     softening. Distinct from the June 23 "market rally hit a wall / monsoon"
     piece (that was equities + monsoon; this is bullion specifically).
  2. Canada's High Commissioner Chris Cooter tells Indian students it's the
     "best time ever" to apply — caps not full, doors open — a deliberate
     counter-narrative to the US/Australia visa crunch. Distinct from the
     recent F-1 duration-of-status, naturalization-fee and EB-2 pieces; this is
     a Canada-study-destination story.
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


# \u2500\u2500\u2500 Article 1: Gold crashes below $4,000 \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Gold crashes below $4,000")
    print("="*60)

    slug = "gold-silver-crash-below-4000-dollar-fed-rate-hike-iran-india-rupee-import-curbs-diaspora-20260625"
    headline = "Gold Just Broke Below $4,000 for the First Time Since November. It's Down a Quarter From Its Peak."
    subheadline = "A surging dollar, a Fed suddenly talking about rate hikes and fading Iran-war fears have wiped roughly 25% off gold since January \u2014 and India's own effort to defend the rupee by curbing gold imports is quietly part of the story."

    body = """The metal that spent 2025 making everyone rich has turned. Gold tumbled below $4,000 an ounce on Wednesday for the first time since November 2025, and slipped further on Thursday to a more than seven-month low near $3,980 \u2014 capping one of the sharpest sell-offs the bullion market has seen in years. Spot gold is now down about 25 to 29% from the all-time high of $5,594.82 it touched on January 29, when war in the Middle East and bets on Federal Reserve rate cuts sent investors stampeding into safe havens. Silver has fallen even harder, shedding more than half its value from a January peak of roughly $122 an ounce to under $57.

The turn has been brutal and fast. Comex front-month gold fell 3.4% in a single session on Wednesday, its largest one-day drop since June 10, and has now logged its longest losing streak in weeks. The catalysts are stacking up in the same direction. The U.S. dollar has climbed to a 13-month high, making dollar-priced gold more expensive for everyone who buys in another currency. And the Federal Reserve \u2014 holding its first meetings under new Chair Kevin Warsh \u2014 has struck a notably hawkish tone, leaving rates unchanged but signalling that the next move could be up.

## From Rate Cuts to Rate Hikes

The whole logic of gold's 2025 boom has flipped. Last year, traders bet the Fed would cut rates, which would erode the appeal of interest-bearing assets and burnish non-yielding gold. Now, with inflation running hot in the wake of the Iran war \u2014 energy prices spiked when the conflict disrupted shipping through the Strait of Hormuz \u2014 markets have swung to pricing in as many as three rate hikes this year, with CME's FedWatch tool showing roughly a two-thirds chance of an increase by September. Higher rates make bonds more attractive than gold and strengthen the dollar, a double blow. "Gold is simply in a bearish momentum trade at this point amid a strong U.S. dollar environment," StoneX analyst Matt Simpson told Reuters.

The easing of geopolitical fear has compounded the move. As a fragile U.S.-Iran framework deal has taken shape and the safe-haven premium has bled out of the market, the very thing that drove gold to records is now draining away. Standard Chartered has noted that at current prices more than 200 tonnes of gold sitting in exchange-traded funds are underwater, and ING has cut its forecasts, now expecting gold to average $4,300 an ounce in the third quarter rather than $4,850.

## The India Connection

For India \u2014 the world's second-largest gold consumer \u2014 the crash is visible at every jeweller's counter. The India Bullion and Jewellers Association reported 24-carat gold closing around Rs 1.45 lakh per 10 grams on June 23, down more than Rs 31,000 from January's record of Rs 1.76 lakh; silver has dropped nearly Rs 1.59 lakh per kilogram from its own high. Indian gold ETFs listed in Mumbai fell about 2% on the day.

What is less obvious is that India is not just a victim of the slide \u2014 it is part of the cause. With the rupee under pressure near record lows and a hefty oil-import bill draining foreign-exchange reserves, New Delhi has been actively discouraging gold buying this year. Because gold, like oil, is paid for in dollars, every tonne India imports adds to demand for foreign currency and weighs on the rupee. By dampening that demand, India is trying to protect its currency \u2014 and in doing so is removing one of the biggest sources of physical demand from the global market, helping push prices lower still.

## Why It Matters for the Diaspora

For the Indian diaspora, gold is never just a trade \u2014 it is the asset class woven into weddings, festivals and family savings from New Jersey to Dubai. NRIs are among the most active cross-border gold buyers, and a 25% correction reshapes a lot of calculations at once. For those who bought near the top, paper losses are real. For those sitting on cash, the sell-off is the first genuine buying window in over a year, with the wedding and Diwali seasons ahead. And for the millions of diaspora families who send money home, the math has shifted: a stronger dollar means remittances stretch further in rupees, even as the gold those rupees might buy has suddenly become cheaper.

The caveats are loud. Central banks are still buying, analysts say a true collapse is unlikely, and several see a long period of consolidation rather than a crash to come. Some, like USA Today's sources, still float a return toward $5,000 if the Fed reverses course. But the message from this week's tape is unambiguous: the easy money in gold is, for now, over \u2014 and for a diaspora that treats the metal as both ornament and insurance, that calls for a colder, more deliberate eye than the past two years required.
"""

    img_url, ititle = pick_commons([
        "gold bars bullion",
        "gold bullion bars stacked",
        "gold ingots"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Gold bullion bars; spot gold fell below $4,000 an ounce for the first time since November 2025"

    if not img_url:
        px = fetch_pexels_image("gold bars bullion")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Gold prices fell below $4,000 an ounce, down about 25% from January's record high"

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
            "Reuters (reuters.com, June 25, 2026) \u2014 'Gold under pressure near 7-month low as Fed rate-hike bets boost dollar': spot gold down 0.5% at $3,980.88 per ounce as of 0738 GMT; bullion fell below $4,000 for the first time since November 2025 on Wednesday and is down 29% from a record high of $5,594.82 reached on January 29; the dollar held near a 13-month high; traders expect three Fed rate hikes this year and price about a 67% chance of a September increase; spot silver fell to $56.85; analyst Matt Simpson (StoneX): 'Gold is simply in a bearish momentum trade at this point amid a strong U.S. dollar environment.'",
            "Investopedia (investopedia.com, June 24, 2026) \u2014 'Markets News': spot gold on Wednesday fell 3% to below $4,000 per ounce, a level not touched since November; silver declined more than 6% to $58; gold is down almost 30% from a January peak of around $5,600 and silver down more than 50% from a high of roughly $122; tumbles followed the Fed's first policy meeting under new Chair Kevin Warsh; CME FedWatch shows traders pricing in at least one hike by year-end.",
            "USA Today (usatoday.com, June 2026) \u2014 'Will gold hit $5,000 again this year?': rising interest-rate expectations are pushing gold lower; geopolitical tensions like the Iran war and tariffs are driving inflation fears; weak demand in India is dragging on global gold prices; analyst notes India has been discouraging citizens from buying gold to support the rupee, because high oil-import costs already strain foreign-exchange reserves and gold imports further increase demand for foreign currency.",
            "Dainik Jagran English (english.dainikjagranmpcg.com, June 24, 2026) \u2014 'Silver Prices Crash Rs 10,566/kg, Gold Falls Rs 2,522': per India Bullion and Jewellers Association (IBJA) data, on Tuesday June 23 silver fell Rs 10,566 per kg and gold Rs 2,522 per 10 grams; 24-carat gold closed at Rs 1.45 lakh per 10 grams vs Rs 1.47 lakh a day earlier; gold hit an all-time high of Rs 1.76 lakh per 10 grams on January 29, 2026 and has since corrected by more than Rs 31,000; silver, after a high of Rs 3.86 lakh/kg in January, has dropped nearly Rs 1.59 lakh.",
            "Reuters (reuters.com, June 24, 2026) \u2014 'Gold ETFs could see fresh outflows on rising bets on Fed monetary tightening': spot gold slipped below $4,000 for the first time since November 2025 under a firmer dollar and elevated-rate expectations; World Gold Council data shows ETFs saw net outflows of 16 tonnes in May; Standard Chartered notes more than 200 tonnes of gold in ETFs are in loss-making territory at current prices; ING cut its forecasts to average $4,300/oz in Q3 and $4,600 in Q4."
        ]),
        "diaspora_angle": "Gold is the asset class woven into diaspora weddings, festivals and family savings, and NRIs are among the world's most active cross-border gold buyers \u2014 so a 25% crash from January's record reshapes their calculations at once: paper losses for recent buyers, a first real buying window before Diwali for those holding cash, and a stronger dollar that stretches remittances further in rupees even as the gold those rupees buy has cheapened.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: Canada tells Indian students it's the 'best time ever' \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Canada 'best time ever' for Indian students")
    print("="*60)

    slug = "canada-best-time-ever-indian-students-cooter-caps-not-full-us-australia-visa-crunch-diaspora-20260625"
    headline = "Canada Has a Message for Indian Students: This Is the 'Best Time Ever' to Apply."
    subheadline = "As the US dangles visa expiry dates and Australia doubles its fees, Canada's envoy in Delhi insists the doors never closed \u2014 the student caps aren't even full, and Ottawa wants Indians to come."

    body = """While Washington floats putting an expiry date on the student visa and Canberra doubles its graduate-visa fees, Canada is going the other way \u2014 and saying so out loud. Chris Cooter, Canada's High Commissioner to India, told ANI this week that it is "probably the best time ever to apply as an Indian student," insisting that a widespread belief in India that Canada has slammed its doors shut is simply wrong. "There is a kind of misperception in India that Canada is shutting the doors. That is not at all the case," he said.

The pitch is pointed, and the timing is no accident. Indian families planning the September 2026 and January 2027 intakes are navigating the most turbulent study-abroad market in years. In the United States, the Department of Homeland Security has advanced a rule that would replace the open-ended "duration of status" framework with fixed admission periods for student-visa holders \u2014 and Indians, at 363,000 the largest foreign-student group in America, would be hit hardest. Australia doubled its Temporary Graduate Visa fee to AUD 4,600 in March. The UK is trimming its post-study Graduate Route from two years to 18 months for those graduating from January 2027. Against that backdrop, Cooter is making a deliberate counter-offer.

## The Caps Aren't Full

Cooter's central argument is arithmetic. Canada did impose a cap on international students a couple of years ago, he acknowledged, but for reasons he framed as housekeeping rather than retreat: a housing crunch and a crop of "fly-by-night colleges" that needed cleaning up. "But we've done that," he said \u2014 and crucially, the country has not come close to filling the cap that remains. "Students are welcome. We haven't even reached those caps. So actually, this is probably the best time ever to apply as an Indian student, because we want you there and there's space in these caps."

The scale, he argued, speaks for itself. Canada currently hosts around 400,000 international students \u2014 "more than the EU, UK, and Australia combined," and more than the United States hosts, by his account. He pointed to Canadian universities' global standing, noting McGill and the University of Toronto sit near the top of world rankings. "So yes, you are very, very welcome as students," he said. "Parents and students, please do consider Canada."

## Reading the Fine Print

The reassurance lands against a harder set of recent numbers, and prospective applicants will weigh both. Study-permit approvals for Indian students fell sharply in 2025, with rejection rates spiking, and Canada's earlier cap and tightened Post-Graduation Work Permit rules \u2014 which now require study in specific eligible fields \u2014 are precisely what fed the "doors are closing" perception Cooter is trying to dispel. His message is less that nothing changed and more that the worst of the adjustment is over and the system is reopening with room to spare.

Cooter also conceded the part Indian applicants complain about most: the visa process itself. "Both the business people and the students tell us about the problems they have with getting the visa. It seems inconsistent or it takes too long," he said, adding that Ottawa is "actively at work on fixing those problems" following Prime Minister Mark Carney's visit to India earlier this year. "I'd like to see us be best in class," he said. "If we have to have visas, let's do it better than everybody else."

## Why It Matters for the Diaspora

For Indian families, study abroad is one of the largest financial and emotional decisions they make \u2014 often a multi-crore bet on a child's future and, frequently, the first foothold for a new branch of the diaspora. The destination chosen shapes everything that follows: the odds of a post-study work permit, a path to permanent residency, and whether relatives already settled abroad are nearby. With the traditional "Big Four" of the US, UK, Canada and Australia all tightening at once, an open and explicit invitation from one of them is significant news for the lakhs of students weighing where to go.

It is also a reminder that these doors are political, and they swing. Cooter's overture follows a thaw in India-Canada relations after a bruising diplomatic freeze, and a high commissioner publicly courting Indian students is itself a signal of warming ties. For diaspora parents, the prudent course is to treat the welcome as genuine but verify the details \u2014 check current PGWP-eligible fields, confirm processing timelines, and weigh the long-term residency math \u2014 because in a market this volatile, the most generous-sounding invitation still has to be read in full.
"""

    img_url, ititle = pick_commons([
        "University of Toronto campus building",
        "McGill University campus Montreal",
        "Canada university campus students"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "A Canadian university campus; Canada's envoy says it is the 'best time ever' for Indian students to apply"

    if not img_url:
        px = fetch_pexels_image("university campus students")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Canada's High Commissioner urged Indian students to apply, saying the student caps are not full"

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
            "The Indian Eye (theindianeye.com, June 23, 2026) \u2014 'Cooter encourages Indian students to apply in Canada': Canadian High Commissioner to India Chris Cooter said there is a 'misperception in India that Canada is shutting the doors,' which 'is not at all the case'; Canada imposed a student cap a couple of years ago over housing shortages and 'fly-by-night colleges' but has addressed that; Canada hosts around 400,000 international students, 'more than the EU, UK, and Australia combined'; 'Students are welcome. We haven't even reached those caps. So actually, this is probably the best time ever to apply as an Indian student'; Ottawa is 'actively at work on fixing' visa delays after PM Mark Carney's February-March 2026 India visit; McGill and University of Toronto cited as top-100 universities.",
            "Devdiscourse / ANI (devdiscourse.com, June 2026) \u2014 '\"Best time to ever apply as an Indian student\": Canadian envoy says not shutting doors on Indian students': Cooter told ANI that the perception Canada has become less welcoming is inaccurate; the cap was introduced due to housing shortages and quality concerns at some institutions; Canada hosts around 400,000 international students; intake remains below the cap; envoy reassured students and parents they are 'very, very welcome.'",
            "Outlook Money (outlookmoney.com, June 22, 2026) \u2014 'US Visa Proposal May Limit Stay Duration For Foreign Students': DHS has proposed replacing the 'duration of status' framework with fixed admission periods for F, J and certain I visa holders; Indian students, the largest international student community in the US at 363,019 in 2024-25 per the Open Doors report, could be among the most affected; the proposal also reduces the post-completion window from 60 to 30 days; the White House review is complete and the rule is closer to formalisation.",
            "Collegedunia (collegedunia.com, 2026) \u2014 'Where Indian Students Are Going Instead of US and UK in 2026': F-1 visa issuances to Indian students fell 69% in June-July 2025; Canada study-permit approvals for Indian students fell 50% in 2025 with rejection rates near 80% and PGWP now requiring study in specific eligible fields; the UK Graduate Route is being cut from 2 years to 18 months for January 2027 graduates; Australia's Temporary Graduate Visa fee doubled to AUD 4,600 on March 1, 2026.",
            "Newspatrolling / Prodigy Finance (newspatrolling.com, June 2026) \u2014 'Indian Students Turn to UK as US Visa Crisis and Australia Crackdown Bite': data shows a sharp rise in UK- and Germany-bound applications from Indian students as US and Australia visa uncertainty reshapes Class of 2026 decisions; per the Higher Education Policy Institute, Indian students issued a UK study visa in Q1 2025 numbered 19,300, a 31% increase over Q1 2024, with a grant rate of 96%."
        ]),
        "diaspora_angle": "Study abroad is one of the largest financial and emotional decisions Indian families make and often the first foothold for a new branch of the diaspora; with the US, UK, Canada and Australia all tightening at once, an explicit invitation from Canada's envoy \u2014 caps unfilled and doors open \u2014 is significant for the lakhs of students choosing a destination, even as recent approval data and a warming India-Canada relationship counsel reading the welcome in full.",
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
