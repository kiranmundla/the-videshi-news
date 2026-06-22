#!/usr/bin/env python3
"""
Videshi News Writer — June 22, 2026 (08:30 UTC run)
2 NEW articles:
  1. BRICS National Security Advisers' Meeting opens in New Delhi, chaired by
     Ajit Doval; Wang Yi & Shoigu attend; theme = non-traditional security
     (cyber, AI, counter-terrorism). Diaspora angle: geopolitics shaping the
     world NRIs live in. (geopolitics)
  2. Iran oil deal cut crude, but airfares — including the India routes the
     diaspora flies — are set to stay high. (economy / travel-cost)
"""

import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone
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
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
            return pick["url"]
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




# ─── Article 1: Starmer resigns; India-UK trade deal in the balance ──────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Starmer resigns, India-UK FTA")
    print("="*60)

    slug = "keir-starmer-resigns-uk-prime-minister-burnham-india-uk-trade-deal-july-15-20260622"
    headline = "Starmer Just Quit. The Man Likely to Replace Him Has Said Nothing About the India Trade Deal That Starts in Three Weeks."
    subheadline = "Keir Starmer resigned as British prime minister on Monday, clearing the way for Andy Burnham to become Britain's seventh leader in a decade. The India-UK free trade pact is set to take effect on July 15 — and the diaspora is about to find out whether a change at the top changes anything."

    body = """Keir Starmer resigned as Britain's prime minister on Monday, ending a turbulent two years in Downing Street and setting off a Labour leadership contest that is widely expected to install Andy Burnham, the mayor of Greater Manchester, as the country's seventh prime minister in a decade.

In an emotional address outside Downing Street, Starmer said he had listened to his parliamentary party and accepted that he was no longer the man to lead it into the next general election. He asked Labour's organising committee to set a timetable: nominations open July 9, close in mid-July, and a new leader is to be in place by the time Parliament rises for the summer — September at the latest. He did not name Burnham, whose decisive by-election win in Makerfield on Friday, beating Nigel Farage's Reform UK, had drained away what remained of Starmer's support.

For most of the world, this is a story about Britain's long political instability — the highest turnover of prime ministers in nearly two centuries, arriving on the tenth anniversary of the Brexit vote. For the Indian diaspora, and for India itself, the timing carries a sharper edge.

## A Trade Deal Due to Start in Three Weeks

Britain's free trade agreement with India is scheduled to come into force on July 15 — barely three weeks away, and squarely in the window of a leadership handover. The Comprehensive Economic and Trade Agreement, signed in July 2025 and worth more than £4.8 billion ($6.5 billion), was confirmed for implementation only this month, after Starmer met Prime Minister Narendra Modi at the G7 summit in France and the two governments agreed to push ahead despite a dispute over Britain's incoming steel tariffs.

The deal is among the most consequential India has struck with a Western economy. It cuts Indian tariffs on Scotch whisky from 150% toward 40%, lowers duties on British cars, and in return gives 99% of Indian exports — textiles, footwear, gems and jewellery, marine products, auto parts — duty-free access to the British market. A parallel Double Contributions Convention spares Indian workers on short UK postings from paying social-security levies twice. British exporters have been given 28 days to register to claim the tariff cuts.

## What a New Prime Minister Could Mean

The conventional wisdom in Westminster is that the deal is too far along, and too uncontroversial across party lines, for a new leader to unpick. It was negotiated under a Conservative government and finished under Labour; its July 15 start date is already gazetted. A Burnham government would inherit it as a fact, not a choice.

But a leadership change is rarely frictionless. Markets reacted immediately on Monday: sterling slipped toward its 2026 low against the dollar, near $1.32, and ten-year gilt yields held around 4.85% — close to their highest since the 2008 financial crisis — on concern that Burnham, seen as more willing to borrow and spend, could unsettle Britain's already strained public finances. A weaker pound changes the arithmetic for every NRI who sends money to or from Britain, and for Indian exporters pricing goods into a market whose currency is sliding.

There is a more direct worry, too. Burnham has so far set out little by way of a foreign-trade agenda, and a new chancellor — reports suggest he would replace Rachel Reeves — would bring fresh priorities to a Treasury that has guarded its credibility with bondholders. The steel dispute that nearly delayed the India deal once is unresolved; Britain's new steel tariff regime takes effect July 1, two weeks before the FTA goes live.

## Why the Diaspora Should Watch Closely

Britain is home to roughly 1.9 million people of Indian origin, one of the diaspora's oldest and most established communities, and a hub for Indian students, professionals on intra-company transfers, and family-run export businesses. The trade deal touches all of them — the price of an India-made garment on a British high street, the cost of a UK posting, the ease of moving goods and money between two of the diaspora's home countries.

The likeliest outcome is continuity: a new face in Downing Street, the same July 15 start for a deal years in the making. But "likeliest" is not "certain," and a political transition layered onto an unresolved steel row and a sliding pound is exactly the kind of weather that can blow a carefully timed agreement off course. For a diaspora that has spent this year watching tariffs and currency swings whipsaw its plans, the next three weeks in London are worth following — because the deal that was supposed to make life cheaper and trade easier is about to change hands at the very moment it comes alive."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Andy Burnham")
    img_caption = "Andy Burnham, the Greater Manchester mayor widely expected to become Britain's next prime minister"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        img_url = fetch_wikipedia_person_image("Keir Starmer")
        img_caption = "Keir Starmer, who resigned as British prime minister on Monday"
    if not img_url:
        img_url = pick_commons([
            "10 Downing Street London",
            "Houses of Parliament London",
            "Palace of Westminster"
        ])
        img_caption = "10 Downing Street, London, as Britain prepares for a change of prime minister"

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
            "Reuters \u2014 UK's Starmer to resign, says he will ensure orderly transfer of power (June 22, 2026): Starmer announced resignation outside Downing Street; nominations open July 9, close mid-July, new leader by September; Burnham won Makerfield by-election Friday beating Reform UK; Britain's seventh PM since Brexit",
            "WSJ / Reuters \u2014 Sterling Falls, Gilt Yields Rise as U.K. Prime Minister Starmer Resigns (June 22, 2026): sterling fell ~0.3% to ~$1.319 near 2026 low; 10-year gilt yields ~4.85%; concern Burnham favours higher spending/borrowing; reports he would replace Chancellor Rachel Reeves",
            "Reuters \u2014 UK-India trade deal worth over $6 billion to start July 15 (June 2026): FTA worth \u00a34.8bn ($6.5bn), signed July 2025, to come into force July 15 after Starmer-Modi talks at G7; India cuts whisky tariffs 150%\u219240%, autos toward 10% under quota; 28-day business registration window; steel dispute over UK tariffs effective July 1",
            "UK Parliament publications \u2014 UK-India Comprehensive Economic and Trade Agreement (CETA): signed 24 July 2025; 99% of Indian exports to enter UK duty-free; Double Contributions Convention spares duplicate social levies; entry into force 60 days after exchange of notifications"
        ]),
        "diaspora_angle": "Britain is home to about 1.9 million people of Indian origin, and the India-UK trade deal due to take effect July 15 touches the price of goods, the cost of UK postings, and the value of money moved between two of the diaspora's home countries \u2014 all now in play during a prime-ministerial handover and a sliding pound.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Court strikes down $100,000 H-1B fee; appeal looms ──────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: H-1B $100k fee struck down, appeal pending")
    print("="*60)

    slug = "h1b-100000-fee-struck-down-judge-sorokin-appeal-first-circuit-indian-physicians-20260622"
    headline = "A Boston Judge Killed the $100,000 H-1B Fee. The Government Wants It Back Before You Can Exhale."
    subheadline = "Judge Leo Sorokin ruled the fee an illegal tax Congress never authorised, handing a reprieve to the Indian workers and doctors who make up the bulk of H-1B holders. But the decision is paused, three courts are now split, and the fight is heading to appeal."

    body = """For the Indian professionals, students and physicians who form the backbone of America's high-skilled visa system, the past month has been an exercise in whiplash. A federal judge in Boston struck down the Trump administration's $100,000 fee on new H-1B visas, calling it an unlawful tax. Days later, the same judge paused his own ruling. The Department of Homeland Security has asked an appeals court to let the fee stand. And two other federal courts are weighing the same question, raising the prospect of contradictory rulings that only the Supreme Court could settle.

The core decision came from U.S. District Judge Leo Sorokin, who sided with California and 19 other states that had challenged the policy. "The Court finds that the Policy imposes a tax on H-1B petitions without the requisite delegation by Congress," Sorokin wrote, concluding that the executive branch had exceeded its authority and violated the Administrative Procedure Act, the law governing how federal agencies issue rules. He vacated the fee on June 8, then agreed on June 12 to stay his decision while the First Circuit Court of Appeals considers the government's motion.

## Why This Lands Hardest on Indians

No nationality has more at stake. Roughly three-quarters of all H-1B approvals go to workers from India, and Indians also make up the largest single group of international students who feed into the program after graduation. The $100,000 fee, announced as a way to stop foreign workers from "taking American jobs," set off a wave of panic when it was unveiled — employers froze offers, students recalculated their futures, and families abroad wondered whether the American pathway they had planned around was still open.

The reprieve was felt most acutely in an unexpected corner: medicine. The American Association of Physicians of Indian Origin welcomed the ruling as "a healthcare victory," warning that the fee would have fallen hardest on rural hospitals, safety-net institutions and underserved communities that depend on international medical graduates. "Many hospitals would have struggled to absorb such a financial burden," said AAPI president Dr. Amit Chakrabarty. "The consequences would have been immediate — fewer physicians, longer wait times, and reduced access to care." International medical graduates, many of them Indian-trained, are a cornerstone of care in precisely the places that struggle most to recruit.

## A Legal Fight Far From Over

The government is not backing down. In a filing to the First Circuit, DHS argued that the one-time fee is not properly a tax at all, and that even if it were, the president has the authority to impose it under federal immigration law. "Every day that passes more aliens can petition and enter the country despite the President's determination that their entry would be detrimental," the department wrote, asking the court to let it keep collecting the fee while it appeals.

The legal landscape is now genuinely fractured. Sorokin's ruling in Boston contradicts an earlier federal decision that upheld the fee. The U.S. Chamber of Commerce sued separately in Washington, D.C., and is appealing a denial there. A third lawsuit, brought by religious groups and labor organizations, is pending in San Francisco. With cases live in three appellate circuits, divided rulings are a real possibility — the classic setup for a Supreme Court showdown. The fee, in any case, is currently scheduled to expire in September 2026, adding a clock to an already tangled fight.

## What Diaspora Families Should Do Now

For NRIs and aspiring immigrants, the practical reality is uncertainty, not resolution. Because Sorokin paused his own ruling, the fee's status while the appeal proceeds is precisely the thing now before the First Circuit. Immigration advocates caution that the broader squeeze on the Indian pathway has not eased: the administration's separate push to cap student stays, narrow Optional Practical Training, and tighten the F-1-to-H-1B route remains in motion, and a proposed cut in the post-study grace period from 60 to 30 days would give graduates even less room to maneuver after repeated H-1B lottery rejections.

The lesson of the past month is that a single court win does not close the matter. The $100,000 fee may be illegal in the eyes of a Boston judge, but it is alive on appeal, contested in two other cities, and ticking toward an expiry date — and the doctors, engineers and graduate students who built their American plans around the H-1B will be watching the First Circuit closely. For now, the advice from immigration lawyers is the same it has been all year: assume nothing is settled, keep documents current, and don't time an irreversible move to a ruling that could be reversed next week."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = pick_commons([
        "United States federal courthouse Boston",
        "John Joseph Moakley United States Courthouse",
        "United States District Court Massachusetts",
        "gavel court"
    ])
    img_caption = "The federal courthouse in Boston, where Judge Leo Sorokin struck down the $100,000 H-1B fee"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("courthouse columns law")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A courthouse facade; a federal judge struck down the $100,000 H-1B fee"

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
            "Associated Press (via NPR Illinois / Montana Public Radio) \u2014 Federal judge strikes down Trump's $100,000 fee on new H-1B visas (June 9, 2026): Judge Leo Sorokin in Boston sided with 20 states; ruled fee an unauthorized tax violating the Administrative Procedure Act; nearly three-quarters of H-1B approvals go to Indian workers; Chamber of Commerce case in D.C. and another in San Francisco; fee scheduled to expire September 2026",
            "Bloomberg Law \u2014 Trump's $100,000 H-1B Visa Application Fee Rejected by Judge (June 2026): Sorokin sided with California and 19 other states; called the decree an unlawful tax that must be vacated; government said it would appeal",
            "Bloomberg Tax \u2014 DHS Says Trump H-1B Fee Isn't a Tax, Should Continue on Appeal (June 2026): DHS told First Circuit the fee is not a tax and is within presidential authority; Sorokin vacated June 8, stayed his decision June 12 pending appeal; one of at least three lawsuits (D.C. Circuit and N.D. California)",
            "The Indian EYE \u2014 AAPI Applauds Court Ruling Blocking $100,000 H-1B Physician Visa Requirement (June 2026): AAPI president Dr. Amit Chakrabarty called it 'a healthcare victory'; warned fee would hit rural hospitals, safety-net institutions and underserved communities reliant on international medical graduates"
        ]),
        "diaspora_angle": "Roughly three in four H-1B visas go to Indian workers, and Indians are the largest group of international students feeding the program \u2014 so a court fight over the $100,000 fee directly decides whether the American pathway thousands of diaspora families planned around stays open or stays priced out.",
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
