#!/usr/bin/env python3
"""
Videshi News Writer — June 26, 2026 (18:30 UTC / 11:30 PDT run)
2 NEW articles, dedup-checked against last 3 days (40 news articles):
  1. NRI investment BEHAVIOUR shift — GIFT City emerging as a diaspora
     wealth hub. Belong reports 2x inflows; NRIs treating India as a
     portfolio-allocation destination rather than just a remittance/real
     estate market. DISTINCT from covered FCNR-B deposit-rate scheme
     (that piece = RBI hedging + bank deposit rates; this = wealth-mgmt
     platforms, GIFT City mutual funds/AIFs/Nifty, IFSCA licences).
  2. The Big Four are losing their grip on Indian students — broad-based
     decline (US -6.9%, Canada collapse, Australia Level 3 scrutiny, UK
     dependants ban) and the rise of Germany, France, Ireland and the UAE.
     NOT covered (Canada "best time ever" piece is the OPPOSITE angle).
"""
import os, json, requests, urllib.parse, subprocess, io, re
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

_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use","just",
    "here","need","know","quietly","almost","like","could","into","now","its","rare",
    "still","won","four","losing","grip","door","park","earn",
}

def _keywords(text):
    out = []
    for t in re.findall(r"[A-Za-z][A-Za-z'-]+", text or ""):
        tl = t.lower()
        if len(tl) >= 4 and tl not in _COMMONS_STOP:
            out.append(tl)
    return out

def commons_relevance_ok(commons_title, headline, topic=""):
    title_l = (commons_title or "").lower()
    if not title_l:
        return False
    kws = set(_keywords(headline)) | set(_keywords(topic))
    if not kws:
        return True
    return any(kw in title_l for kw in kws)

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
                })
            if results:
                print(f"  \u2713 Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Commons error: {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}'")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None

def download_and_compress(url, slug):
    try:
        r_content = None
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
            if r.status_code == 200 and len(r.content) >= 5000:
                r_content = r.content
        except Exception:
            pass
        if r_content is None:
            tmp = f"/tmp/{slug}_src"
            subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=40, check=True)
            with open(tmp, "rb") as f:
                r_content = f.read()
            if len(r_content) < 5000:
                print(f"  \u26a0 Image too small after curl fallback")
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
            print(f"  \u26a0 Compressed too small")
            return None
        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        requests.delete(upload_url, headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY})
        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg", "x-upsert": "true"}, timeout=30)
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url[:80]}...")
            return public_url
        print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None

def pick_commons(queries, headline, topic="", min_width=800):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        commons = [c for c in commons if commons_relevance_ok(c.get("title", ""), headline, topic)]
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            print(f"  \u2713 Commons pick: {pick.get('title','')}")
            return pick["url"], pick.get("title", "")
    return None, ""

def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
    return None


# ─── Article 1: NRI investment shift — GIFT City as a diaspora wealth hub ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: NRI investment shift to GIFT City wealth hub")
    print("="*60)

    slug = "nri-investment-shift-gift-city-wealth-hub-belong-doubles-inflows-portfolio-allocation-india-mutual-funds-aif-20260626"
    headline = "The Diaspora Used to Send Money Home. Now It's Investing in India \u2014 and GIFT City Is the New Address."
    subheadline = "A digital wealth platform built for NRIs just doubled its inflows in two months, almost all of it fresh money wired in from abroad. It is the clearest sign yet of a quiet shift: overseas Indians are no longer just remitting to family \u2014 they are building India into a global portfolio, and Gujarat's tax-neutral finance city is where they are doing it."

    body = """For decades, the financial relationship between Indians abroad and the homeland followed a familiar script. Money flowed one way \u2014 to parents, to a flat being built back home, to a family obligation \u2014 and it flowed because of the heart, not the spreadsheet. India was a place you supported, not a place you invested in. That script is now being rewritten, and the early numbers are striking.

Belong, a digital wealth platform built specifically for non-resident Indians, said this week that its investment inflows doubled to $6 million in March-April from $3 million in the first two months of the year, with the strongest demand coming from investors in the UAE and Qatar. The detail that matters most is not the doubling itself but where the money came from: a majority of it was fresh capital remitted from overseas, not savings already parked in Indian bank accounts. NRIs are wiring new dollars into India for the express purpose of investing.

## From Remittance to Allocation

"Historically, the conversation was around sending money to India or maintaining assets in India for personal reasons," said Ankur Choudhary, the platform's co-founder and chief executive. "Today, more NRIs are approaching India as an investment destination and thinking about portfolio allocation rather than remittances alone." Founded in 2024, the company has crossed 25,000 users across more than 80 countries, facilitated nearly $20 million in investments, and is growing 25 to 30 percent month on month. Its annualised assets-under-management run rate has reached $36 million.

The behaviour underneath the growth is what India's policymakers have been hoping to see. Average ticket sizes tell the story: more than $20,000 in dollar-denominated fixed deposits used to park surplus cash, and around $5,000 in India-focused mutual funds aimed at long-term goals such as retirement and children's education. Many of these investors already hold deep exposure to global markets through their countries of residence; they are now deliberately raising their India weighting, treating it as an asset class rather than a sentimental obligation.

## Why GIFT City Is the Doorway

The address for this shift is the Gujarat International Finance Tec-City \u2014 GIFT City \u2014 the country's tax-neutral international financial centre, regulated by the International Financial Services Centres Authority (IFSCA). For an NRI, its appeal is structural: a globally aligned regulatory framework, the ability to hold investments in foreign currency, tax advantages on certain products, and the ability to invest directly from an overseas bank account without first routing money through the domestic banking system. Belong describes itself as the first fully digital platform to hold three IFSCA licences \u2014 payment service provider, broker-dealer and distributor \u2014 letting NRIs access India-linked and global products through a single account. India-focused mutual funds based out of GIFT City already account for roughly a fifth of its inflows, and the firm plans to launch GIFT Nifty derivatives trading for NRIs next.

This sits alongside a broader, deliberate push by New Delhi to court diaspora dollars. The Reserve Bank of India recently moved to subsidise the hedging cost on foreign-currency non-resident deposits and to let domestic banks lend against those deposits through their overseas branches and GIFT City, with banks raising rates to around 6 to 7 percent. Brokerage Nomura estimates the deposit drive alone could pull in about $55 billion, while Axis Bank sees scope for as much as $100 billion. The wealth-platform boom is the retail, equity-tilted cousin of that wholesale, deposit-driven effort \u2014 two sides of the same campaign to turn the 35-million-strong diaspora into a durable source of capital.

## Why It Matters for the Diaspora

For NRIs, the change is less about a single platform and more about a maturing set of options. A worker in Dubai or a doctor in London who once had to choose between a low-yield foreign savings account and the friction of investing back home can now build an India allocation in dollars, from abroad, with tax efficiency and without surrendering liquidity. It reframes India in the diaspora imagination \u2014 not only as the country you came from and send money to, but as a growth market you want a stake in.

The risks are the ordinary ones of any emerging-market bet: currency swings, the reliability of a young fintech, and tax-residency rules that differ sharply between, say, the Gulf and the United States. But the direction of travel is unmistakable. The remittance, that most emotional of financial transactions, is being joined by something colder and more confident \u2014 the allocation. And for the first time, India is selling itself to its own diaspora not as a duty, but as an opportunity."""

    topic = "GIFT City Gandhinagar Gujarat international finance tec-city tower IFSC building skyline"
    img_url, _ = pick_commons([
        "GIFT City Gandhinagar",
        "Gujarat International Finance Tec-City",
        "GIFT City tower Gandhinagar Gujarat",
        "Gandhinagar GIFT City skyline",
    ], headline, topic)
    img_attribution = "Wikimedia Commons"
    img_caption = "GIFT City in Gandhinagar, Gujarat \u2014 India's tax-neutral international financial centre, now a hub for NRI investment"
    if not img_url:
        px = fetch_pexels_image("modern financial district skyline towers")
        if px:
            img_url = px; img_attribution = "Pexels"
            img_caption = "A modern financial district; GIFT City has become the gateway for NRIs investing in India"

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
            "The Hindu BusinessLine (thehindubusinessline.com, 24 June 2026) \u2014 'Belong reports 2x jump in investment inflows as NRIs boost India allocation via GIFT City': NRI-focused wealth platform Belong reported investment inflows doubling to $6 million in March-April from $3 million in January-February, strongest demand from UAE and Qatar; a majority of recent inflows came from fresh capital remitted from overseas rather than funds already in Indian bank accounts; CEO Ankur Choudhary said NRIs increasingly treat India as a portfolio-allocation destination rather than only a remittance market; platform has crossed 25,000 users in 80+ countries, facilitated ~$20 million in investments/transactions, growing 25-30% MoM since launching GIFT City USD fixed deposits, AUM run rate ~$36 million; GIFT City India-focused mutual funds ~20% of inflows; FD average >$20,000, mutual funds ~$5,000; plans to launch GIFT Nifty trading for NRIs; first fully digital platform with three IFSCA licences (PSP, Broker-Dealer, Distributor); founded 2024; cites IFSCA framework, foreign-currency holdings, tax advantages and direct overseas-account investing.",
            "Reuters \u2014 'India File: Rupee gets diaspora lifeline \u2014 banks cash in': India has turned to its ~37 million-strong diaspora for support; RBI scheme announced earlier this month offers to absorb the cost of hedging foreign-currency deposits placed with Indian banks for three to five years, letting overseas Indians earn relatively high domestic rates without currency risk; banks have raised rates on such deposits to around 6-7%; Nomura estimates potential ~$55 billion in inflows, Axis Bank sees scope for ~$100 billion; banks seeking RBI approval to offer dollar loans to such clients via overseas branches or GIFT City.",
            "Reuters \u2014 'India's RBI to allow domestic banks to extend loans against overseas FX deposits': the Reserve Bank of India said in a notice on Tuesday that domestic lenders may extend loans to non-residents against foreign-currency deposits, including via offshore branches and GIFT City; banks may issue standby letters of credit against such deposits and place a lien on accounts; RBI swap covers only the principal, not interest; part of broader measures to bolster dollar inflows and shore up the rupee.",
            "Background \u2014 GIFT City / IFSCA: the Gujarat International Finance Tec-City (GIFT City) is India's first international financial services centre, regulated by the International Financial Services Centres Authority (IFSCA), offering a tax-neutral, globally aligned regulatory regime, foreign-currency-denominated products and direct cross-border investing; the centre has been positioned by the government as a hub for NRI and global wealth management, with multiple foreign universities also cleared to operate there."
        ]),
        "diaspora_angle": "Overseas Indians are shifting from sending remittances to actively building India into a global investment portfolio \u2014 wiring fresh dollars abroad into GIFT City mutual funds, fixed deposits and soon Nifty derivatives \u2014 giving NRIs in the Gulf, US and UK a tax-efficient, foreign-currency way to take a growth stake in India rather than treating it only as a place to support family.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ─── Article 2: The Big Four lose their grip on Indian students ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Big Four lose grip on Indian students")
    print("="*60)

    slug = "indian-students-abroad-big-four-decline-us-canada-uk-australia-destination-shift-germany-uae-ireland-mea-data-20260626"
    headline = "For a Generation, 'Study Abroad' Meant America, Canada, Britain or Australia. That Era Is Quietly Ending."
    subheadline = "Indian student numbers in the US fell at their sharpest pace in a decade this year, Canada's intake has collapsed, and Australia has slapped India with its highest tier of visa scrutiny. As the traditional Big Four pull up the drawbridge, a new map of where India's young go to learn \u2014 and to build a future \u2014 is taking shape."

    body = """For most of the past two decades, the Indian study-abroad dream had four addresses: the United States, Canada, the United Kingdom and Australia. The "Big Four" absorbed the overwhelming majority of the more than a million Indians who leave each year for a foreign degree, and the pipeline seemed permanent. In 2026, that assumption is breaking, and the data behind the break is now official.

The number of Indian students enrolled in US institutions fell 6.9 percent in a single year \u2014 from 378,787 in February 2025 to 352,644 in February 2026 \u2014 the sharpest annual drop in over a decade, India's Ministry of External Affairs confirmed in a written reply to the Rajya Sabha. Drawn from the US Department of Homeland Security's SEVIS data, the decline was broad-based, spanning school, vocational, undergraduate and postgraduate enrolment. India remains the largest source of foreign students in America, but for the first time since 2019, its lead over China has narrowed.

## A Collapse, Not a Dip

Canada's story is starker still. Having overtaken the US in 2023 to become the single largest destination for departing Indian students at 233,532, the figure crashed to 137,608 the following year \u2014 a drop of nearly 96,000 in twelve months, the largest absolute decline for any destination on record. Three policy decisions drove it and all three remain in force: a national study-permit cap that cut new approvals by roughly 35 percent, a tightening of post-graduate work-permit rules that severed the permanent-residency pathway for many college diploma graduates, and visa rejection rates for Indians that climbed toward 80 percent in early 2025.

The other two pillars are wobbling too. Australia has moved India to "Level 3" \u2014 its highest tier of immigration scrutiny \u2014 with reported student-visa rejection rates of around 40 percent. The United Kingdom's ban on most taught-master's students bringing dependants has cooled demand sharply after the post-pandemic peak. The cumulative effect is visible in the aggregate: the total number of Indians going abroad to study fell from 9.08 lakh in 2023 to 7.7 lakh in 2024 and 6.26 lakh in 2025, a roughly 31 percent decline in two years, the Ministry of Education told Parliament, citing Bureau of Immigration data.

## The New Map

What is rising is as telling as what is falling. According to the QS Global Student Flows 2026 report, of the roughly 800,000 Indians currently studying overseas, the US accounts for 30 percent, the UK 15, Canada 11 and Australia 10 \u2014 while "the rest of the world" has climbed to a record 25 percent. Germany, France, Ireland and the United Arab Emirates are the clear beneficiaries, drawing students with low or no tuition fees, English-taught programmes, clearer work pathways and, crucially, stability of policy. The decision drivers have changed: where students once chased rankings and brand names, they now weigh return on investment, job prospects, permanent-residency routes and affordability.

India itself is part of the rebalancing. New Delhi has cleared 14 foreign institutions to establish campuses on Indian soil and approved five overseas universities to operate from GIFT City in Gujarat, betting that some of the outbound demand can be met at home. Whether a domestic campus of a foreign university carries the same migratory promise as the degree-plus-work-visa-plus-PR package that once made the Big Four irresistible is, for now, an open question.

## Why It Matters for the Diaspora

The student pipeline has always been the diaspora's renewal mechanism \u2014 the way each generation of Indian families plants a child in a new country who later becomes a citizen, a professional, a community anchor. As the Big Four tighten, that renewal is being redirected rather than reduced: the next wave of the Indian diaspora may speak German or settle in Dublin or Dubai rather than Toronto or Sydney. For families weighing where to send a son or daughter, the lesson of 2026 is that the safe, default choice is no longer safe or default. And for the established diaspora in the US, UK, Canada and Australia, a thinning student inflow has real consequences \u2014 fewer young arrivals to refresh community institutions, temples, businesses and the political constituencies that have only recently begun to find their voice. The map of where Indians go to study is being redrawn, and with it, the map of where the diaspora of 2040 will live."""

    topic = "international students university graduation campus airport departure students studying"
    img_url, _ = pick_commons([
        "international students university campus",
        "students graduation ceremony university",
        "university students studying campus",
        "airport departures terminal travellers",
    ], headline, topic)
    img_attribution = "Wikimedia Commons"
    img_caption = "International students on a university campus; Indian enrolment in the traditional Big Four destinations is declining"
    if not img_url:
        px = fetch_pexels_image("international students university campus graduation")
        if px:
            img_url = px; img_attribution = "Pexels"
            img_caption = "Students on a university campus; Indian enrolment in the US, Canada, UK and Australia is falling"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "education",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Collegedunia (collegedunia.com) \u2014 'Indian Students in US Fall 6.9% to 3.52 Lakh \u2014 Sharpest Drop in a Decade as per Parliament Data': Indian student enrolment in US institutions fell 6.9% in a single year, from 378,787 in February 2025 to 352,644 in February 2026, the sharpest year-on-year drop in over a decade; confirmed by India's MEA in a written reply to the Rajya Sabha on 2 April 2026; data drawn from US DHS SEVIS Mapping Tool; decline broad-based across school, vocational, undergraduate and postgraduate; India remains the largest source country but its gap with second-ranked China narrowed for the first time since 2019.",
            "The Daily Jagran (thedailyjagran.com, 13 Feb 2026) \u2014 'Indian Students Going Abroad Fall 31% In Just 2 Years Amid Visa Rules Tightening': Ministry of Education MoS Sukanta Majumdar told the Rajya Sabha that over 9.08 lakh Indian students went abroad in 2023, dropping to 7.7 lakh in 2024 and 6.26 lakh in 2025 \u2014 about a 31% decline in two years (Bureau of Immigration data); attributed to strict visa policies and bank-loan challenges; government says 14 foreign institutions have been approved to set up campuses in India and five overseas universities cleared to operate in GIFT City, Gujarat, under NEP 2020.",
            "Collegedunia (collegedunia.com) \u2014 'Where Indian Students Study Abroad: Destination Shift, Official MEA Data': Canada overtook the USA in 2023 as the largest destination for Indian student departures at 233,532, then fell to 137,608 the next year \u2014 a drop of nearly 96,000, the largest absolute decline for any destination; three causes still in force \u2014 a ~35% national study-permit cap (Jan 2024), tightened PGWP rules removing the PR pathway for many college diploma graduates, and IRCC rejection rates approaching 80% for Indian applicants in early 2025; 427,085 Indian students enrolled in Canadian institutions as of 1 January 2025, a legacy of the 2021-2023 surge expected to contract.",
            "ICEF Monitor (monitor.icef.com) \u2014 'The number of Indian students abroad fell in 2025': MEA 2025 data shows more than 1.2 million Indian students enrolled in higher education abroad, -5.7% fewer than the 1.33 million in 2024; stricter regulatory environments in Australia, Canada, the UK and the US (the 'Big Four') introduced market uncertainty; destinations other than the Big Four \u2014 Germany, New Zealand, France, Ireland \u2014 increasingly considered as English-taught programmes expand.",
            "LeapScholar / QS Global Student Flows 2026 (leapscholar.com) \u2014 'Study Abroad Trends 2026: Where Indians Are Going': nearly 800,000 Indian students currently studying overseas; distribution USA 30%, UK 15%, Canada 11%, Australia 10%, Germany 9%, Rest of World 25% (a record high); combined Big Four enrolments forecast to decline ~0.5% annually through 2030 as students diversify toward Germany, France and the UAE, prioritising job-readiness, ROI and PR pathways over rankings.",
            "Shiksha (shiksha.com) \u2014 'Study Abroad Trends for Indian Students in 2026-2027': total Indian students abroad ~1.2-1.3 million with a 5-6% decline in 2025 stabilising in 2026; US admissions declining amid limited interview slots; Canada study-permit cap; UK dependants ban reducing demand; Australia reporting ~40% rejection rates and India shifted to 'Level 3' of visa scrutiny; rising interest in Germany, Japan, Ireland and the UAE."
        ]),
        "diaspora_angle": "The student pipeline is the diaspora's renewal mechanism, and as the Big Four \u2014 the US, Canada, UK and Australia \u2014 tighten visas and caps, the next generation of overseas Indians is being redirected toward Germany, Ireland and the UAE, meaning a thinner inflow of young arrivals to refresh the established diaspora's community institutions, businesses and emerging political voice in the traditional destinations.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-26 18:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (NRI investment shift / GIFT City wealth hub): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (Big Four lose grip on Indian students): {'OK id=' + str(id2) if id2 else 'FAILED'}")
