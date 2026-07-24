#!/usr/bin/env python3
"""
Videshi News Writer — June 22, 2026 (12:30 UTC run)
2 NEW articles:
  1. Rupee snaps six-session winning streak, ends ~94.68/dollar as hawkish Fed lifts dollar (news / economy) — remittances/NRI angle
  2. ~18,000 Indian seafarers stranded in the Gulf; three killed on MT Settebello; Jaishankar protests to Rubio (news / diaspora-safety)
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
                if ii.get("width", 0) < 600:
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


# ─── Article 1: Rupee snaps winning streak ───────────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Rupee snaps six-session streak near 94.68")
    print("="*60)

    slug = "indian-rupee-snaps-six-session-winning-streak-hawkish-fed-dollar-remittances-nri-20260622"
    headline = "The Rupee's Best Run in Months Just Ended. The Reason Sits in Washington, Not Delhi."
    subheadline = "India's currency snapped a six-day winning streak on Monday to close near 94.68 a dollar, as a hawkish US Federal Reserve lifted the greenback to a one-year high. For the diaspora sending money home, a weaker rupee is a quiet windfall."

    body = """The Indian rupee's strongest stretch in nearly three months came to an end on Monday, a reminder that the currency the diaspora watches every time it sends money home is being steered less by events in India than by the mood of the US Federal Reserve. The rupee snapped a six-session winning streak to close at about 94.68 a dollar, down roughly 0.4 percent from Friday, after a hawkish turn by America's central bank pushed the dollar to its highest level in a year.

The reversal interrupts what had been a genuine recovery. Over the previous six sessions the rupee had climbed about one percent, touching a multi-month high near 94.18 and rebounding sharply from the record low close to 97 a dollar it hit only last month. That rally had two engines: a steep retreat in oil prices as the United States and Iran made what officials called "encouraging progress" at a first round of talks in Switzerland, and a package of measures from the Reserve Bank of India designed to draw dollars into the country. For an economy that is the world's third-largest importer of crude, cheaper oil is the single biggest relief a currency can ask for.

What pulled the rupee back was not bad news from home but a shift in the dollar. The Fed's hawkish signals last week prompted traders to add to bets on a rate increase later this year, keeping the dollar index near the 101 mark, its highest since May 2025. Across Asia, currencies fell between 0.3 and 0.7 percent on Monday in sympathy. As analysts at ING put it, markets may keep testing how much more tightening the Fed will price in for 2026, but "unless there is a fresh Middle East escalation, lower oil prices should contain" the dollar's gains. In other words, the rupee is caught between a falling oil bill that helps it and a strengthening dollar that hurts it.

The RBI's hand is visible throughout. The central bank's short-dollar forward book — a measure of how aggressively it has intervened to support the rupee — is estimated to have swelled to a record near $110 billion, up from $96 billion in April. Policymakers have rolled out a series of steps to attract dollar inflows, including a subsidised swap scheme aimed squarely at non-resident Indians. Yet economists at Goldman Sachs caution against expecting a sharp appreciation: those inflows are "likely to be absorbed by the RBI" as it rebuilds foreign-exchange reserves, which have slipped from a March peak of $728.5 billion to about $681.6 billion. The forward-premium curve, which reflects the cost of hedging against further rupee weakness, steepened on Monday — a sign traders still see depreciation risk ahead.

For the diaspora, the arithmetic of a weaker rupee is double-edged but, on balance, favourable. India is the world's largest recipient of remittances, taking in nearly $138 billion in 2024 and on track for a record $137-140 billion in the current fiscal year, according to SBI Research. Every rupee the currency loses against the dollar means a remittance stretches further at home: a $1,000 transfer that bought roughly 92,000 rupees a year ago now converts to nearly 95,000. For families paying school fees in Hyderabad, EMIs on an apartment in Pune, or simply keeping parents comfortable, the exchange rate is not an abstraction on a screen — it is the difference of a few thousand rupees a month.

The same logic is reshaping how the diaspora moves money. A recent survey of Gulf-based NRIs found that nearly half of remittances are now driven by investment and retirement planning rather than routine family support, with Indian equities the favoured destination. A softer rupee, paired with a domestic stock market that the diaspora increasingly treats as a wealth-building venue, turns the act of sending money home into something closer to a strategic allocation than an obligation. The flip side is felt by those on the receiving end of dollar-denominated costs: anyone in India paying for a US college, a software subscription or an imported good watches the bill rise as the rupee falls.

None of this is settled. The next move hinges on two forces largely outside India's control — whether the fragile US-Iran framework holds and keeps oil contained, and whether the Fed under its new leadership leans further into tightening. For now, the message from Monday's session is the one the diaspora has long understood instinctively: the rupee in your remittance app is priced in a language spoken in Washington and in the oil futures pits, as much as in Mumbai."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    for q in ["Indian rupee banknotes", "Reserve Bank of India building", "Indian rupee currency", "Indian rupee notes money"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "The Indian rupee snapped a six-session winning streak on Monday to close near 94.68 against the US dollar"
            img_attribution = "Wikimedia Commons"
            break

    if not img_url:
        pex = fetch_pexels_image("indian rupee currency money")
        if pex:
            img_url = pex
            img_caption = "The rupee ended its six-day rally as a stronger dollar weighed on Asian currencies"
            img_attribution = "Pexels"

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
            "Reuters — 'Rupee snaps six-session winning streak as firmer dollar pinches' (June 22, 2026): the rupee ended at 94.6775 per dollar, down 0.4% from Friday's close, after rising about 1% over the preceding six sessions; the dollar index hovered near a one-year peak around the 101 handle, its highest since May 2025, after a hawkish Fed turn; Asian currencies fell 0.3%-0.7%; Brent crude declined nearly 2% after US-Iran talks in Switzerland showed encouraging progress; 1-year forward implied yield up 10bps at 2.95%; ING noted lower oil prices should contain USD gains absent fresh Middle East escalation",
            "Reuters — 'Indian rupee's oil relief capped by RBI's FX book, interest payment hedges, bankers say' (mid-June 2026): RBI short-dollar forward book estimated near an all-time high of ~$110 billion, up from $96 billion in April; rupee recovered to ~94.50 after sliding to an all-time low near 97 last month; India's FX reserves fell from a March peak of $728.5 billion to $681.6 billion; Goldman Sachs said it does not expect significant INR appreciation as inflows are absorbed by the RBI rebuilding FX buffers",
            "Livemint — 'Rupee opens 4 paise lower at 94.36 against US dollar' (June 22, 2026): rupee opened 4 paise weaker at 94.36; had rallied 0.8% the prior week to close at 94.32, its strongest weekly gain in nearly three months, touching a multi-month high of 94.18 over a six-session winning streak; Brent crude for August fell 1.7% to $79.24 after Iran indicated encouraging progress in Switzerland talks",
            "The HinduBusinessLine / SBI Research — 'India's remittances to reach record $140 billion in FY26': remittances expected at $137-140 billion in FY26 before stabilising at $135-137 billion in FY27; inflows of ~$110 billion through December, up from $100 billion a year earlier; IOM World Migration Report 2026 ranked India the largest remittance recipient with nearly $138 billion in 2024, more than double the ~$53 billion of 2010"
        ]),
        "diaspora_angle": "India is the world's largest recipient of remittances — a record ~$137-140 billion expected this fiscal year — so every move in the rupee directly changes how far a diaspora dollar stretches when it lands in family accounts, school fees and investments back home.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Indian seafarers stranded in the Gulf ────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: ~18,000 Indian seafarers stranded in the Gulf")
    print("="*60)

    slug = "indian-seafarers-stranded-gulf-oman-hormuz-us-navy-strikes-settebello-jaishankar-protest-20260622"
    headline = "Nearly 18,000 Indians Are Trapped at Sea in the Gulf. Three Have Already Come Home in Coffins."
    subheadline = "Indian crews man the tankers caught between a US blockade and Iran's threats around the Strait of Hormuz. As food and water run short on stranded ships, New Delhi has lodged its strongest protest yet with Washington."

    body = """The men who keep the world's oil moving are overwhelmingly Indian, and right now thousands of them are stuck on ships they cannot sail, in waters they cannot safely cross. India's shipping ministry says nearly 18,000 Indian mariners remain in the Gulf region, caught between a US naval blockade of Iranian oil and Tehran's on-again, off-again threats to shut the Strait of Hormuz. For a maritime workforce that supplies a large share of the world's commercial crews, the standoff has turned one of the planet's busiest shipping lanes into a place of fear, shortages and, for three families, grief.

The human cost became undeniable earlier this month. On June 9, the Palau-flagged tanker MT Settebello was struck by US forces in the Gulf of Oman, its engine room hit by precision munitions after, Washington says, the crew failed to comply with directions enforcing the blockade on Iranian oil shipments. Of the 24 Indian crew aboard, 21 were rescued by the Omani navy; three were confirmed dead. The Ministry of External Affairs said the seafarers had been identified and that their remains would be brought home. It was not an isolated event: US Central Command says it disabled several commercial vessels within a single week, including the Palau-flagged MT Marivex and, on June 11, the Guinea-Bissau-flagged MT Jalveer, which was carrying 20 Indian seafarers and was struck by two Hellfire missiles near Oman's Shinas port. Its crew were all rescued.

The shipping operator's account sharply contradicts the US version. iOS Marine, which operates the Settebello, said in a public statement that "no warning call, message, or communication was ever successfully established" before American forces opened fire, and that the tanker had "remained stationary at its position for approximately 10 days prior to the incident" — neither transiting the area nor making evasive manoeuvres. The International Maritime Organization's secretary-general, Arsenio Dominguez, condemned the violence and called attacks on civilian mariners "simply unacceptable," demanding an investigation into the Settebello strike.

For those still at sea, conditions have grown dire. Manoj Yadav, general secretary of the Forward Seamen's Union of India, told CBS News that many crews are out of patience and increasingly out of supplies, with seafarers reporting shortages of food, water and medical care. "They were absolutely not feeling well. Many called us and said they are not able to sail further," he said, adding that some described feeling "like they are in jail." A fourth Indian mariner, Second Officer Nishanth Uirthanathan, died aboard the MT Celestial Sea while awaiting medical evacuation at Oman's Duqm Port; the union said his body remained on board for three days without refrigeration. The toll has begun to spill onto the streets at home, where students protested in New Delhi against the killing of the sailors.

New Delhi's diplomatic response has hardened by the day. External Affairs Minister S Jaishankar said he spoke with US Secretary of State Marco Rubio to convey India's "strong protest at the attacks by the US Navy in the Gulf that killed three Indian mariners," calling such "lethal actions against commercial shipping" unjustified. The Ministry of External Affairs has twice summoned the US charge d'affaires in Delhi, lodging formal protests and rejecting Washington's operational justifications, telling the United States that using deadly force against civilian ships is "unacceptable and undermines international maritime commerce." Indian officials have stressed that the vessels involved were foreign-flagged, even as the crews aboard them were Indian — the precise tangle that makes protecting these workers so difficult.

The episode lands at a delicate moment for India-US ties. The protests over dead and stranded seafarers are unfolding just as US Trade Representative Jamieson Greer prepares to arrive in Delhi for talks aimed at finalising a trade framework before a July 24 tariff deadline, and only days after Prime Minister Narendra Modi and President Trump met on the sidelines of the G7. A relationship that both capitals describe as strategically vital is being tested by the most basic of duties a state owes its citizens abroad: keeping them alive.

For the diaspora, the story cuts close. Indian seafarers are a vast, largely invisible global workforce, sending home wages that sustain families across Kerala, Goa, Andhra Pradesh and beyond, and crewing the tankers and container ships that underpin the world economy. Their plight is a reminder that the Indian presence abroad is not only doctors and engineers in Western suburbs but also the men on the bridge of a tanker off the Omani coast, whose safety can hinge on a missile fired in a conflict they had no part in. As New Delhi works to repatriate the dead and bring the living home, the question for thousands of families is simpler and more urgent than any trade deal: when does the next call come, and what will it say?"""

    img_url = None
    img_caption = ""
    img_attribution = ""

    for q in ["oil tanker Gulf of Oman", "crude oil tanker ship", "Strait of Hormuz tanker", "merchant ship tanker sea"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "An oil tanker at sea; nearly 18,000 Indian mariners remain in the Gulf region amid US strikes on commercial vessels"
            img_attribution = "Wikimedia Commons"
            break

    if not img_url:
        pex = fetch_pexels_image("oil tanker ship sea")
        if pex:
            img_url = pex
            img_caption = "Indian crews man many of the tankers caught in the standoff around the Strait of Hormuz"
            img_attribution = "Pexels"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Indian EYE — 'Jaishankar voices strong protest to Rubio over death of Indian seafarers' (June 2026): EAM S Jaishankar said he spoke to US Secretary of State Marco Rubio to convey India's strong protest over US Navy attacks in the Gulf that killed three Indian mariners, calling lethal actions against commercial shipping unjustified; MT Settebello came under fire on Wednesday in the Gulf of Oman after US forces accused it of violating the naval blockade on Iranian ports; of 24 Indian crew, 21 rescued and 3 confirmed dead; MEA summoned US Charge d'Affaires Jason Meeks, the second such summons; MEA spokesperson Jaiswal noted the ships involved were foreign-flagged",
            "CBS News / Opera News (via Forward Seamen's Union of India) — '14 dead, thousands stranded: Inside the plight of mariners trapped in the Strait of Hormuz': India's commercial shipping ministry said nearly 18,000 Indian mariners remain in the region; union general secretary Manoj Yadav described unbearable conditions, shortages of food, water and medical care, with seafarers saying they felt 'like in jail'; a fourth Indian mariner, Second Officer Nishanth Uirthanathan, died aboard MT Celestial Sea awaiting medical evacuation at Duqm Port, his body left unrefrigerated for three days; students protested in New Delhi on June 15 over the killings",
            "Defcon Level / US Naval Forces Central Command — 'Three Indian Mariners Killed in Gulf of Oman Tanker Incident' (June 2026): CENTCOM forces disabled the tanker MT Settebello around June 10 by firing precision munitions into its engine room after the crew failed to comply during enforcement of the blockade on Iranian oil; three Indian mariners killed, 21 rescued; India summoned the US deputy chief of mission and lodged a formal protest; Ports, Shipping and Waterways Minister Sarbananda Sonowal confirmed the deaths and said bodies would be repatriated",
            "The Indian EYE — 'Strait of Hormuz Crisis Poses New Test for India-US Ties' / Reuters trade coverage (June 2026): MT Jalveer (Guinea-Bissau flag), carrying 20 Indian seafarers, struck June 11 in the Gulf of Oman, the third vessel targeted in a week alongside MT Marivex and MT Settebello; iOS Marine, Settebello's operator, denied any warning was given and said the ship had been stationary ~10 days; IMO Secretary-General Arsenio Dominguez condemned the attacks; USTR Jamieson Greer due in India June 23-24 for trade talks ahead of a July 24 tariff deadline, days after the Modi-Trump G7 meeting on June 17"
        ]),
        "diaspora_angle": "Indian seafarers crew a large share of the world's commercial fleet and send wages home to families across Kerala, Goa and Andhra Pradesh; with nearly 18,000 stranded in the Gulf and four already dead, the standoff is a stark reminder that the diaspora abroad includes the mariners whose safety can hinge on a conflict they have no part in.",
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
