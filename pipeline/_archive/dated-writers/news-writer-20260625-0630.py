#!/usr/bin/env python3
"""
Videshi News Writer — June 25, 2026 (06:30 UTC run)
2 NEW articles, dedup-checked against last ~40 news articles:
  1. Zohran Mamdani's slate sweeps NY congressional primaries (June 23, 2026).
     Indian-origin NYC mayor (son of filmmaker Mira Nair) becomes Democratic
     kingmaker as his three endorsed candidates (Lander, Avila Chevalier,
     Valdez) win, ousting two incumbents (Goldman, Espaillat). Fresh
     diaspora-politics story; only prior Mamdani mention was the US Open box item.
  2. PMRC Scheme 2026 — India's Prime Minister Research Chair scheme to draw
     Indian-origin researchers home from global labs. Up to Rs 60 lakh/yr +
     Rs 5 crore grants, 13 priority sectors, 120 researchers over 5 years,
     applications open June 1 - July 15. Fresh diaspora reverse-brain-drain story.
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


# \u2500\u2500\u2500 Article 1: Mamdani slate sweeps NY congressional primaries \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Mamdani slate sweeps NY primaries")
    print("="*60)

    slug = "zohran-mamdani-slate-sweeps-new-york-congressional-primaries-kingmaker-lander-espaillat-20260625"
    headline = "An Indian-Origin Mayor Just Became the Most Powerful Kingmaker in Democratic Politics. All Three of His Picks Won."
    subheadline = "Zohran Mamdani, the son of filmmaker Mira Nair, watched his entire endorsed slate sweep New York's congressional primaries on Tuesday \u2014 ousting two sitting members of Congress and signalling that the city's first South Asian mayor now reaches far beyond City Hall."

    body = """Eighteen months ago, Zohran Mamdani was a state assemblyman few outside his Queens district could name. On Tuesday night he was being called a kingmaker. All three of the candidates the New York City mayor endorsed in the Democratic congressional primaries won their races, two of them by knocking off sitting members of Congress \u2014 a result the Associated Press described as a "resounding show of force" and that one outlet flatly labelled a "political earthquake."

For the Indian diaspora, the ascent is hard to overstate. Mamdani, 34, is the son of the acclaimed filmmaker Mira Nair and the Columbia academic Mahmood Mamdani, and was born in Kampala to a family of Indian origin before the family settled in New York. When he won the mayoralty last year, he became the city's first South Asian and first Muslim mayor. Now, barely six months into the job, he has shown he can move votes in races that have nothing to do with running City Hall.

## What Happened on Tuesday

The headline results were the two incumbents who lost. Former city comptroller Brad Lander, whom Mamdani backed, defeated two-term Representative Dan Goldman in a race the AP called less than ten minutes after polls closed; Lander won by close to 32 points, making Goldman one of the few sitting House members to lose renomination this year. In the 13th Congressional District covering Upper Manhattan and the Bronx, community organiser Darializa Avila Chevalier upset Representative Adriano Espaillat, the chair of the Congressional Hispanic Caucus and the first Dominican American elected to Congress, who had held the seat for nearly a decade.

The third win came in an open seat. State Assemblywoman Claire Valdez, a Mamdani ally and, like Avila Chevalier, a member of the Democratic Socialists of America, won the primary to succeed retiring Representative Nydia Velazquez \u2014 defeating Brooklyn Borough President Antonio Reynoso by some 20 points even though Velazquez had endorsed a different candidate. In a heavily Democratic city, all three are now strong favourites to enter Congress in November.

## A Test of Two Wings of the Party

The races doubled as a proxy fight between Mamdani's insurgent left and the Democratic establishment led, in New York, by House Minority Leader Hakeem Jeffries, who campaigned against several of Mamdani's picks. The mayor framed the night as vindication of a movement rather than a personal win. "Last June was not the end, it was the beginning," he told supporters, referencing his own come-from-behind mayoral primary a year earlier. Speaking alongside Senator Bernie Sanders in Brooklyn, he added: "We need a Democratic Party with backbone."

Not every progressive bet paid off. In the race to replace retiring Representative Jerry Nadler, where Mamdani stayed neutral, the more establishment-aligned Micah Lasher prevailed. But the overall verdict was clear enough that even Republican critics seized on it; Representative Mike Lawler declared that the Democratic Party had "officially become the party of Zohran." The next test comes quickly: a Denver primary will measure whether the Mamdani model travels beyond the East Coast.

## Why It Matters for the Diaspora

For South Asian Americans, who have spent a generation moving from donor lists and advisory boards into elected office, Mamdani represents a different kind of arrival. This is not a diaspora figure carefully positioned in the political centre, but one reshaping the direction of a major party on his own terms \u2014 and winning. Whatever one makes of his democratic-socialist politics, the signal is that an Indian-origin politician can now sit at the very centre of American political power, dispensing endorsements that topple veteran incumbents.

That carries weight in both directions. It expands the sense of what is possible for the roughly five million Indian Americans, and especially for a younger generation that increasingly sees electoral politics as a viable path rather than a closed door. It also makes Mamdani a lightning rod: his stances on Israel, immigration enforcement and the economy place him squarely in the country's fiercest debates, and the diaspora is no monolith in how it views them. What is no longer in question is his reach. The mayor of New York has become a national force \u2014 and he got there as the son of a Bhubaneswar-rooted filmmaker who taught the world to see India on screen, before her son taught American politics to reckon with him.
"""

    img_url = fetch_wikipedia_person_image("Zohran Mamdani")
    img_attribution = "Wikimedia Commons"
    img_caption = "New York City Mayor Zohran Mamdani, whose three endorsed candidates swept the city's Democratic congressional primaries"

    if not img_url:
        img_url, ititle = pick_commons([
            "Zohran Mamdani",
            "New York City Hall",
            "United States Capitol building"
        ])

    if not img_url:
        px = fetch_pexels_image("new york city hall politics")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Mamdani-backed candidates swept New York's Democratic congressional primaries on Tuesday"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-politics",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Fox 5 NY / Associated Press (fox5ny.com, June 2026) \u2014 'Mamdani-backed candidates win New York House primaries, oust 2 incumbents': candidates backed by NYC Mayor Zohran Mamdani swept several Democratic congressional primaries; Darializa Avila Chevalier defeated five-term Rep. Adriano Espaillat, chair of the Congressional Hispanic Caucus; former comptroller Brad Lander defeated two-term Rep. Dan Goldman; Assembly member Claire Valdez won the primary to succeed retiring Rep. Nydia Velazquez; AP called the wins a 'resounding show of force'; House Democratic Leader Hakeem Jeffries had campaigned against Mamdani's candidates.",
            "Washington Examiner (washingtonexaminer.com, June 2026) \u2014 'A big night for Mamdani as socialists keep winning Democratic primaries': Lander defeated Goldman by nearly 32 points in a race AP called less than 10 minutes after polls closed, making Goldman the fifth sitting House member to lose renomination this year; Avila Chevalier, 32, upset Espaillat, 71; Valdez beat Brooklyn Borough President Antonio Reynoso by about 20 points for the open Seventh District seat; in the race to replace retiring Rep. Jerry Nadler, where Mamdani stayed neutral, Micah Lasher won.",
            "Fox News (foxnews.com, June 2026) \u2014 \"'Party of Zohran': Mamdani emerges as Democratic kingmaker after socialist allies sweep NYC primaries\": all three Democratic Socialist candidates Mamdani backed won; Rep. Mike Lawler said the Democratic Party had 'officially become the party of Zohran, AOC, & Bernie'; Avila Chevalier and Valdez are members of the Democratic Socialists of America, as is Mamdani.",
            "USA Today (usatoday.com, June 2026) \u2014 'Mamdani in 3, NYC mayor sweeps Democratic establishment: takeaways': the 34-year-old democratic socialist expanded his influence on June 23 by sweeping all three Democratic primaries for Congress after endorsing the opponents of more mainstream contenders; his choices were pitted against those of House Minority Leader Hakeem Jeffries in a successful early test of establishing a new faction within the national party.",
            "The Wall Street Journal (wsj.com, June 2026) \u2014 'Key Takeaways From the New York House Primaries': all three candidates Mamdani endorsed won their congressional primaries, in races dominated by conversations about Israel, legacy candidates and AI; speaking alongside Sen. Bernie Sanders in Brooklyn, Mamdani said 'We need a Democratic Party with backbone'; a Congressional race in Denver will test whether Democratic Socialists can win outside the East Coast."
        ]),
        "diaspora_angle": "Zohran Mamdani \u2014 New York's first South Asian mayor and the son of filmmaker Mira Nair \u2014 has become a national Democratic kingmaker barely six months into office, showing that an Indian-origin politician can now sit at the centre of American power and reshape a major party, even as his democratic-socialist politics divide a diaspora that is no monolith.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: PMRC Scheme 2026 to draw researchers home \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: PMRC Scheme 2026 reverse brain drain")
    print("="*60)

    slug = "india-pm-research-chair-pmrc-scheme-2026-bring-indian-origin-researchers-home-60-lakh-fellowship-20260625"
    headline = "India Is Offering Its Scientists Abroad Up to Rs 60 Lakh a Year to Come Home. The Real Question Is Whether Money Is Enough."
    subheadline = "The Prime Minister Research Chair Scheme wants 120 Indian-origin researchers back from labs like OpenAI, DeepMind and Anthropic over five years, with grants of up to Rs 5 crore. Applications close July 15 \u2014 and the diaspora is doing the maths."

    body = """For decades, the traffic of Indian scientific talent has run almost entirely one way: out. Researchers of Indian origin have helped build the breakthroughs coming out of OpenAI, Google DeepMind, Anthropic and Meta, and have populated the faculty of nearly every elite Western university. Very little of that work has happened in India. The government's newest attempt to change that arithmetic is now open for applications \u2014 and it is putting real money on the table.

The Prime Minister Research Chair (PMRC) Scheme 2026, launched by the Department of Higher Education under the Ministry of Education, invites accomplished Indian-origin researchers, scientists and technologists from "globally reputed universities, laboratories, research institutions and industries" to relocate to premier Indian institutions. The Press Information Bureau announced the scheme in early June, and the application window for both fellows and host institutions opened on June 1, with a deadline of July 15.

## What's on Offer

The financial package is among the most generous India has ever assembled for returning academics. According to figures circulating widely in the research community, the scheme runs across three tiers. Young Research Fellows, up to five years past their PhD, can receive Rs 15-20 lakh a year plus a one-time research grant of Rs 1-1.5 crore and Rs 30 lakh in relocation support. Senior Fellows can draw Rs 20-40 lakh annually with grants up to Rs 2.5 crore. At the top, Research Chairs \u2014 those a decade or more past their doctorate \u2014 can command Rs 40-60 lakh a year, one-time research grants of Rs 3-5 crore, and Rs 50 lakh in relocation costs, alongside generous residential and medical allowances.

The scheme aims to place at least 120 distinguished researchers over five years, from 2026-27 to 2030-31. It spans 13 thematic areas the government considers national priorities: advanced computing including AI, quantum and supercomputing; semiconductors; energy, sustainability and climate change; cybersecurity; healthcare and medtech; biotechnology; advanced materials and critical minerals; space and defence; next-generation communications; manufacturing and Industry 4.0; agri and food technologies; the blue economy; and atomic energy. Seven lead institutions \u2014 the IITs at Delhi, Bombay, Madras, Kanpur, Hyderabad and Dhanbad, plus IISc Bengaluru \u2014 anchor the programme, with other top NIRF-ranked institutions and national labs under DST, DBT, ICMR and CSIR eligible to host.

## Who Can Apply

Eligibility is drawn deliberately wide across the diaspora. The scheme is open to Indian citizens working overseas, to Overseas Citizen of India (OCI) cardholders, and to Persons of Indian Origin (PIOs) \u2014 anyone, in effect, with both Indian roots and a record of excellence at a globally recognised institution. Beyond the money, fellows are expected to lead original research, mentor doctoral and postdoctoral students, co-design curricula and build international collaborations, with the government framing the whole effort as a contribution to Atmanirbhar Bharat and the Viksit Bharat 2047 vision.

## The Harder Question

The scheme arrives with an honest dose of scepticism, including from Indian commentators. As one analysis put it, the launch raises a larger question: why would the world's best AI researchers choose India over Silicon Valley? Money matters, but a senior researcher's decision rarely turns on salary alone. It turns on the quality of the lab, the availability of compute and equipment, the ease of getting grants and equipment through customs, the freedom from bureaucratic friction, and whether a spouse can find work and children a school. These are exactly the frictions that pushed many of these researchers abroad in the first place, and a fellowship cheque does not, by itself, resolve them.

## Why It Matters for the Diaspora

For the millions of Indian-origin researchers and professionals scattered across the West, PMRC is the most concrete signal yet that India wants them back not as occasional guest lecturers but as permanent contributors \u2014 and is willing to pay competitively to get them. For mid-career scientists weighing whether their work could have more impact, and more visibility, at an Indian institution than as one name among thousands at a Western lab, the scheme reframes the calculation. It will not reverse the brain drain on its own; no single programme could. But it converts a vague national aspiration into a specific offer with a deadline attached. Whether enough of the diaspora says yes by July 15 \u2014 and, more importantly, whether those who do find the working conditions match the cheque \u2014 will be the real measure of whether India's long talent exodus has finally begun to turn around.
"""

    img_url, ititle = pick_commons([
        "Indian Institute of Technology Delhi campus",
        "Indian Institute of Science Bangalore",
        "science laboratory research India",
        "IIT Bombay campus"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "India's IITs and IISc anchor the Prime Minister Research Chair Scheme 2026, which seeks to bring Indian-origin researchers home from global labs"

    if not img_url:
        px = fetch_pexels_image("scientist laboratory research")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The PMRC Scheme 2026 offers Indian-origin researchers up to Rs 60 lakh a year to relocate to top Indian institutions"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Press Information Bureau, Ministry of Education (pib.gov.in, June 2, 2026) \u2014 'Prime Minister Research Chair (PMRC) Scheme 2026': the Department of Higher Education invites applications for a flagship national initiative to attract accomplished Indian-origin researchers, scientists, technologists and professionals from globally reputed universities, laboratories, research institutions and industries to premier government HEIs, national laboratories and research centres across India; the scheme connects global Indian talent with India's research ecosystem across 13 thematic areas of national priority including advanced computing (AI, quantum, supercomputing), semiconductors, energy/sustainability/climate, cybersecurity, healthcare and medtech, biotechnology, advanced materials, space and defence, next-generation communications, manufacturing, agri and food technologies, blue economy and atomic energy.",
            "Jagran Josh (jagranjosh.com, June 3, 2026) \u2014 'PMRC Scheme 2026: Fellowship, Eligibility, Host Institutes and How to Apply': the scheme, launched by the Department of Higher Education under the Ministry of Education, brings top Indian-origin researchers and professionals from overseas to India; applications from fellows and host institutions opened June 1 through the PMRC portal; eligible host institutions include IIT Delhi, IIT Bombay, IIT Madras, IIT Kanpur, IIT Hyderabad, IIT (ISM) Dhanbad and IISc Bengaluru, plus top-100 NIRF institutions and national labs under DBT, DST, CSIR and ICMR.",
            "Inc42 (inc42.com, June 2026) \u2014 'India Wants Its AI Talent Back; But What's The Incentive?': researchers of Indian origin have helped shape breakthroughs at OpenAI, Google DeepMind, Anthropic and Meta, yet very few of these breakthroughs happen in India; the PMRC scheme seeks to attract accomplished Indian-origin researchers to premier universities and national laboratories, covering 13 strategic sectors with research grants, infrastructure support and institutional backing; the launch raises the question of why the world's best AI researchers would choose India over Silicon Valley.",
            "ImpressiveTimes (impressivetimes.com, June 2026) \u2014 'PM Research Chair Scheme 2026 Launched to Attract Global Talent': the initiative offers three categories \u2014 Young Research Fellows, Senior Research Fellows and Research Chairs; it is open to Indian citizens working overseas, OCI cardholders and PIOs with demonstrated research excellence; seven premier institutions (IIT Delhi, Bombay, Madras, Kanpur, Hyderabad, ISM Dhanbad and IISc Bengaluru) are designated lead institutions; the government said the scheme will accelerate research excellence and contribute to a Viksit Bharat.",
            "Research-community fellowship summary (LinkedIn, June 2026) \u2014 'India Offers Rs 60 Lakh/Year Research Fellowships to Indian-Origin Researchers': the PMRC scheme will place at least 120 distinguished researchers at India's top institutions over five years (2026-27 to 2030-31); Young Research Fellows: Rs 15-20 lakh/year, Rs 1-1.5 crore grant, Rs 30 lakh relocation; Senior Fellows: Rs 20-40 lakh/year, Rs 1.5-2.5 crore grant; Research Chairs: Rs 40-60 lakh/year, Rs 3-5 crore grant, Rs 50 lakh relocation; applications open June 1 and close July 15, 2026; open to Indian nationals, OCIs and PIOs."
        ]),
        "diaspora_angle": "The PMRC Scheme 2026 is India's most concrete and generous attempt yet to reverse its brain drain, offering Indian-origin researchers abroad up to Rs 60 lakh a year and Rs 5 crore grants to relocate to the IITs and IISc \u2014 putting a specific, deadline-bound offer in front of millions of diaspora scientists, even as the harder questions of lab quality and bureaucratic friction remain unanswered.",
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
