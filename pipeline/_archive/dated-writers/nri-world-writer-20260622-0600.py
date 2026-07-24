#!/usr/bin/env python3
"""
Videshi NRI World Writer — June 22, 2026 (0600 batch)
3 NEW articles (category: nri-world, status: review, is_editorial: False):
  1. Parsi women excommunicated for interfaith marriage — Supreme Court 9-judge bench / diaspora
  2. India Home Senior Center opens in Hicksville, Long Island (July 7) — aging diaspora care
  3. South Asian Heritage Month 2026 UK — "Unity in Diversity" preview
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


# ─── Article 1: Parsi women / Supreme Court excommunication ──────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Parsi women excommunication / Supreme Court")
    print("="*60)

    slug = "parsi-women-interfaith-marriage-excommunication-supreme-court-sabarimala-diaspora-20260622"
    headline = "Marry Out, and You Are Out: India's Top Court Weighs a Rule That Empties the Fire Temple of Its Daughters"
    subheadline = "A nine-judge bench has called the Parsi practice of excommunicating women who marry outside the faith \u201cdiscriminatory.\u201d For a community of barely 50,000 in India \u2014 and a scattered, shrinking diaspora \u2014 the stakes are nothing less than survival."

    body = """For Goolrokh Gupta, the cruelty was precise. Born a Parsi, a practising Zoroastrian, she married a Hindu man under India's Special Marriage Act and went on living her faith as before. Then her community decided she had stopped being one of them. The Valsad Parsi Anjuman in Gujarat barred her from the fire temple and, most woundingly, from attending the last rites of her own parents at the Tower of Silence. A Parsi man who marries a Hindu woman keeps every one of those rights. His wife and children may even be welcomed in. The line is drawn at the daughter, and only the daughter.

Gupta's challenge to that line has now reached the largest bench India's Supreme Court can assemble. On June 16, a nine-judge Constitution bench led by Chief Justice Surya Kant heard her case as part of the sprawling Sabarimala reference, the marathon hearing into how far religious freedom can shield practices that exclude women. What the judges said from the bench should unsettle anyone who assumed the matter was settled custom.

## \u201cA Right By Birth\u201d

\u201cThe right of conscience under Article 25(1) is a right by birth and cannot be taken away by marriage,\u201d Justice B.V. Nagarathna observed. \u201cIn this case, marriage as a basis of classification is discriminatory against women.\u201d She pressed the point with the petitioner's counsel, senior advocate Darius Khambata: \u201cChildren of a Parsi father have the benefit of the Zoroastrian religion. That means it is by birth. The same thing should apply to the wife also.\u201d

Khambata, himself a Parsi, went further than asking the court to strike the practice down. He argued it was never religion at all. \u201cZoroastrianism is a very forward-looking religion,\u201d he submitted, \u201cand this practice is actually man-made, which is why it's difficult to find any religious texts that support this claim.\u201d When Justice Nagarathna asked whether the ban was \u201ceven a matter of religion,\u201d he answered plainly: no. The bench's retort \u2014 \u201cif it's not a matter of religion, file a civil suit\u201d \u2014 captured the strange legal limbo the rule occupies, neither clearly sacred nor clearly secular, but powerful enough to keep a believer from her parents' funeral.

The practice has a paper trail. The 2012 Gujarat High Court ruling that went against Gupta leaned on the colonial-era doctrine of coverture \u2014 the idea that a woman's legal and religious identity merges into her husband's on marriage. That a 21st-century Indian court reached for a Victorian fiction to justify a Zoroastrian exclusion is, in itself, a measure of how little scrutiny these denominational rules have faced.

## Why the Diaspora Is Watching

For Parsis, this is not an abstract debate about Article 25. It is arithmetic. The community in India has dwindled to around 50,000, down from roughly 114,000 in 1941, with deaths outnumbering births for decades. Worldwide, the Zoroastrian population is estimated at well under 200,000, scattered across Mumbai, Karachi, London, Toronto, Sydney, Hong Kong and the United States. A faith that does not accept converts and expels the children of out-marrying women is, quite literally, defining itself toward extinction.

That is why diaspora Zoroastrians \u2014 many of them in mixed marriages by sheer demographic necessity \u2014 have watched the hearing with an intensity that surprises outsiders. North American Zoroastrian associations have spent years debating whether to recognise children of intermarried members; some accept them, others do not, and the rift runs through families and federations alike. A ruling in Delhi will not bind a trust in Toronto or a congregation in California. But it would lend the weight of India's highest court to the reformers' core claim: that excluding a woman for whom she married is discrimination dressed as doctrine.

The counter-argument, voiced by orthodox trustees in Mumbai and echoed abroad, is that a tiny minority's right to police its own boundaries is precisely what religious freedom protects. Strip a denomination of the power to define membership, they warn, and you hasten the dissolution you claim to prevent. The Supreme Court has shown it feels the force of that fear; it has said repeatedly through the Sabarimala hearing that it does not wish to play a part in \u201cthe annihilation of a religion.\u201d

Yet the bench keeps returning to the asymmetry. The rule does not test faith \u2014 Gupta never abandoned hers. It tests gender. And for a diaspora that has carried its fire across oceans precisely because it would not let the flame go out, the question the judges have forced into the open is an uncomfortable one: whether a community can save itself by turning away its own daughters."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    img_url = pick_commons([
        "Zoroastrian fire temple India",
        "Parsi fire temple Mumbai",
        "Agiary fire temple",
        "Zoroastrian Tower of Silence"
    ])
    if img_url:
        img_attribution = "Wikimedia Commons"
        img_caption = "A Zoroastrian fire temple; India's Supreme Court is weighing whether barring Parsi women who marry outside the faith from such spaces is discriminatory"
    if not img_url:
        px = fetch_pexels_image("ancient temple India heritage")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A heritage temple; the Parsi excommunication practice is before a nine-judge Supreme Court bench"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "CNN \u2014 feature on Parsi women excluded from the community for interfaith marriage (June 21, 2026); ~50,000 Parsis in India, a shrinking, non-converting community; diaspora dimension in Hong Kong, UK and beyond",
            "LiveLaw / Bar and Bench \u2014 Sabarimala reference, Day 11-14 hearings: nine-judge bench (CJI Surya Kant, Justices Nagarathna, Sundresh, Amanullah, Aravind Kumar, Masih, Varale, Mahadevan, Bagchi); petitioner Goolrokh Gupta represented by Sr. Adv. Darius Khambata; Justice Nagarathna's observation that 'marriage as a basis of classification is discriminatory against women'; 2012 Gujarat HC ruling and the coverture doctrine; Valsad Parsi Anjuman Trust"
        ]),
        "diaspora_angle": "Parsi/Zoroastrian communities are among the most globally dispersed of Indian-origin groups \u2014 Mumbai, London, Toronto, Sydney, Hong Kong, the US \u2014 and intensely affected by demographic decline. The Supreme Court's scrutiny of excommunicating women who marry outside the faith speaks directly to diaspora Zoroastrians, who face the same patriarchal membership rules in mixed marriages abroad, and whose North American federations remain split over recognising the children of intermarried members.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India Home Senior Center, Hicksville LI ──────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India Home Senior Center, Hicksville")
    print("="*60)

    slug = "india-home-senior-center-hicksville-long-island-aging-diaspora-care-20260622"
    headline = "The Diaspora Built Itself Around Its Children. Now It Is Building for Its Parents."
    subheadline = "A new India Home senior centre opening in Hicksville on July 7 is a small ribbon-cutting with a large subtext: the first big wave of Indian immigrants to America is growing old, and the community is scrambling to catch up."

    body = """The Indian American story has, for two generations, been told as a story of ascent \u2014 of children sent to good schools, of H-1B visas and start-ups, of spelling bees and corner offices. It is a young story, told by and about the strivers. What it has rarely paused to consider is what happens to the strivers' parents, the ones who came in the 1970s and 1980s, raised the doctors and the engineers, and are now in their seventies and eighties in a country that still feels, in old age, slightly foreign.

A modest event on Long Island this summer is a sign that the community is finally asking. On July 7, the India Home Senior Center will open in Hicksville, the Nassau County town that has become one of the densest concentrations of Indian Americans in the New York suburbs. The project is backed by the Association of Indians in America (AIA National), one of the oldest diaspora organisations in the country, and it extends to Long Island a model that India Home has spent more than a decade refining in Queens.

\u201cThis is a matter of great pride for AIA and the whole community, as this senior center has been established to serve our growing community, the majority of whom reside in and around the Hicksville area,\u201d said Gobind Munjal, AIA's immediate past national president and a member of its board of trustees. The centre, he said, will be \u201ca welcoming space for seniors to connect, engage, and benefit from various programs and services.\u201d

## A Quiet Crisis of Loneliness

Behind the gentle language of \u201cconnection\u201d and \u201cengagement\u201d lies a sharper problem the diaspora does not often discuss openly: isolation. Many elderly Indian immigrants live with adult children in comfortable suburban homes and are, by any material measure, well provided for. But the children leave at dawn for work, the grandchildren disappear into school and screens, and the parents are left in what one India Home elder once memorably called \u201ca big golden-gate jail\u201d \u2014 secure, affluent, and profoundly lonely. They often do not drive, may speak limited English, and find mainstream American senior centres culturally alien, from the food to the festivals to the language of small talk.

India Home was built precisely to answer that. Founded in Queens and led by executive director Dr. Vasundhara Kalasapudi, it has grown over more than a decade from a thrice-weekly programme into a network offering culturally specific care: meals that are vegetarian or halal as needed, Hindi- and Urdu-speaking staff, yoga and bhajans and garba, dementia services, and even an experiment in co-living for South Asian seniors. The Hicksville centre imports that template to a suburban population that has, until now, had to drive into the city to find anything like it.

## Why Long Island, Why Now

The geography is not incidental. The Indian American population of Long Island, and of Hicksville in particular, has swelled over the past two decades, and it is ageing in place. The community that arrived young is now producing its first large cohort of retirees \u2014 people who spent their working lives building American careers and are now navigating Medicare, widowhood and frailty far from the joint-family structures that would once have absorbed them in India.

That demographic shift is reshaping diaspora philanthropy. For years, Indian American giving flowed toward temples, scholarships and homeland causes \u2014 the institutions of arrival and aspiration. Senior care is the institution of permanence: you do not build a centre for your elders unless you have accepted that this is home, and that you will grow old and die here. In that sense the Hicksville ribbon-cutting is a marker of maturity for a community that has, until recently, behaved as though it might always be just passing through.

The need is not unique to New York. From the Bay Area to Houston to the suburbs of Toronto and London, the same wave is cresting: the pioneers of Indian migration entering old age in numbers, often without the caregiving customs they grew up expecting. A handful of culturally specific senior centres, adult day programmes and assisted-living experiments have sprung up to meet it, but supply lags badly behind a population that is both growing and greying.

For now, the families of Hicksville have somewhere to send their parents on a weekday morning \u2014 somewhere with familiar food, a shared language and a card table of contemporaries. It is a small thing, and it is also the diaspora quietly admitting something profound: that the immigrant generation's last chapter will be written here, and that the community owes its elders a place to write it."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    px = fetch_pexels_image("elderly indian people community")
    if px:
        img_url = px
        img_attribution = "Pexels"
        img_caption = "Elderly Indian Americans; a new India Home senior centre opens in Hicksville, Long Island on July 7"
    if not img_url:
        px = fetch_pexels_image("senior citizens community center")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A senior community gathering; the new Hicksville centre extends India Home's culturally specific care to Long Island"
    if not img_url:
        img_url = pick_commons(["senior citizens India", "elderly people gathering"])
        if img_url:
            img_attribution = "Wikimedia Commons"
            img_caption = "Senior citizens; the India Home centre in Hicksville serves Long Island's growing population of elderly Indian Americans"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Global Net News \u2014 'India Home Senior Center to Open in Hicksville, Expanding Support for Long Island's Growing Senior Community' (June 20, 2026): July 7 inauguration; supported by Association of Indians in America (AIA National); quotes from Gobind Munjal, AIA Immediate Past National President and Board of Trustees member",
            "India Home (indiahome.org) \u2014 background on the Queens-based organisation led by executive director Dr. Vasundhara Kalasapudi; culturally specific senior services including halal/vegetarian meals, Hindi/Urdu-speaking staff, dementia care and South Asian senior co-living"
        ]),
        "diaspora_angle": "The first big wave of post-1965 Indian immigrants to the US is now entering old age, and culturally specific senior care \u2014 familiar food, language, festivals \u2014 is becoming one of the diaspora's most urgent and under-met needs. The Hicksville centre, replicating India Home's Queens model on suburban Long Island, signals a shift in diaspora priorities from arrival-and-aspiration institutions (temples, scholarships) toward institutions of permanence, with the same greying wave cresting from the Bay Area to Houston to Toronto and London.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 3: South Asian Heritage Month 2026 UK ───────────────

def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: South Asian Heritage Month 2026 UK")
    print("="*60)

    slug = "south-asian-heritage-month-2026-uk-unity-in-diversity-diaspora-20260622"
    headline = "\u2018Unity in Diversity\u2019: Britain's South Asian Month Tries to Hold a Fracturing Family Together"
    subheadline = "South Asian Heritage Month returns to the UK on July 1 with a theme that is part celebration and part plea \u2014 a bid to keep eight nations, many faiths and a long, painful history under one tent."

    body = """Every July, Britain spends a month telling itself a story about the roughly four million people whose roots run back to the Indian subcontinent. Town halls light up, libraries fill their shelves with Partition memoirs and Kathak performances spill onto festival stages. South Asian Heritage Month, born in 2020, has grown from a House of Commons concept launch into a genuinely national programme of exhibitions, talks and Bollywood dance workshops stretching from Hackney to Sheffield.

This year it carries a theme heavy with intent: \u201cUnity in Diversity.\u201d Running from July 1 to 31, the 2026 edition asks what binds South Asians together across what its organisers call \u201cextraordinary diversity\u201d \u2014 eight countries, hundreds of languages, multiple faiths, and millennia of shared and distinct histories. It is, on its face, a warm and unobjectionable slogan. Read against the moment, it is something more pointed.

## A Theme That Knows the Cracks

The phrase \u201cUnity in Diversity\u201d is not chosen in a vacuum. The South Asian diaspora in Britain is, in 2026, anything but a single bloc. The fault lines that run through the subcontinent \u2014 Hindu and Muslim, India and Pakistan, caste and class \u2014 have followed their people to Leicester, Birmingham and east London, and have flared into open friction in recent years. Hindu-Muslim tensions that erupted on the streets of Leicester in 2022 left a lasting wariness. Debates over caste discrimination have split community organisations. To label a heritage month \u201cUnity in Diversity\u201d is to acknowledge, however gently, that the unity cannot be assumed.

The month's founders, Jasvir Singh CBE and Dr Binita Kane, have always framed it as more than a cultural showcase. SAHM was conceived partly as an act of historical reckoning \u2014 a way to teach Britain about Partition, about empire, about the Indian soldiers who fought its wars and the migrants who rebuilt its mills and its National Health Service. The 2026 theme leans into that civic ambition: not merely to celebrate samosas and saris, but to argue that a shared commitment to community and belonging can hold a diverse diaspora together where politics pulls it apart.

## From One Calendar to Another

There is a small but telling change in the dates. For its first six years, the month ran from July 18 to August 17 \u2014 a window chosen to honour the South Asian solar calendar and to bracket a cluster of charged anniversaries: the royal assent of the Indian Independence Act on July 18, and the independence days of Pakistan, India, the Maldives and Bhutan. Aligning the celebration with the very dates of Partition was deliberate, a refusal to let the trauma be forgotten.

The shift to a clean July 1\u201331 calendar makes the month easier for schools, councils and the NHS to programme, and it is now the dates the organisers themselves publish. But it also quietly loosens the link to Partition's anniversary, trading historical resonance for institutional convenience \u2014 a small illustration of how a grassroots commemoration becomes, with success, a fixture of the official calendar.

## What It Means Beyond Britain

South Asian Heritage Month is a distinctly British invention, but its reach is now watched across the diaspora. The United States, Canada and Australia have their own, more fragmented observances \u2014 South Asian or Asian American and Pacific Islander heritage months, Diwali proclamations, Vaisakhi parades \u2014 and organisers in those countries study the British model for how a single, well-branded month can win recognition from governments, employers and broadcasters. The BBC and major UK institutions now mark SAHM as a matter of course; that institutional buy-in is precisely what diaspora advocates elsewhere covet.

For the Indian community specifically, the month is a double-edged opportunity. It offers a prominent platform \u2014 but a shared one, under a South Asian umbrella that folds Indians together with Pakistanis, Bangladeshis, Sri Lankans, Nepalis and others at a time when some in the Indian diaspora increasingly assert a distinct Hindu or Indian identity rather than a pan-South Asian one. \u201cUnity in Diversity\u201d is, in that light, as much an internal argument as an external celebration: a reminder that the tent only works if everyone agrees to stay inside it.

When the displays go up in July, most visitors will see the joyful surface \u2014 the dance, the food, the family photographs. But the organisers have chosen their words carefully. In a year when the diaspora's divisions are easier to name than its commonalities, declaring \u201cunity\u201d is not a description. It is an aspiration, and a quietly urgent one."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    img_url = pick_commons([
        "South Asian festival UK",
        "Diwali celebration London",
        "Indian cultural festival Britain",
        "Mela festival UK"
    ])
    if img_url:
        img_attribution = "Wikimedia Commons"
        img_caption = "A South Asian cultural celebration in the UK; South Asian Heritage Month 2026 runs July 1-31 under the theme 'Unity in Diversity'"
    if not img_url:
        px = fetch_pexels_image("indian festival celebration colorful")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A South Asian festival; the UK's South Asian Heritage Month returns in July with the theme 'Unity in Diversity'"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "South Asian Heritage Month official site (southasianheritage.org.uk) \u2014 2026 theme 'Unity in Diversity', running 1\u201331 July 2026; framing around eight countries, hundreds of languages and multiple faiths; co-founders Jasvir Singh CBE and Dr Binita Kane",
            "Wikipedia / SAHM history \u2014 first observed 2020 after a 2019 House of Commons concept launch; ran 18 July\u201317 August from 2020\u20132025 to bracket Partition-era independence anniversaries (Indian Independence Act royal assent July 18; Pakistan, India, Maldives, Bhutan independence days) before moving to a 1\u201331 July calendar"
        ]),
        "diaspora_angle": "South Asian Heritage Month is the UK's most institutionally successful diaspora commemoration, and its 2026 'Unity in Diversity' theme is studied by Indian, Pakistani and Bangladeshi community organisers in the US, Canada and Australia as a model for winning government and broadcaster recognition. For the Indian diaspora it is a double-edged platform \u2014 prominent but shared under a pan-South Asian umbrella, at a moment when some assert a distinct Indian or Hindu identity, making 'unity' as much an internal aspiration as an external celebration.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    ids.append(write_article_3())
    print("\n" + "="*60)
    print(f"DONE. Inserted IDs: {[i for i in ids if i]}")
    print("="*60)
