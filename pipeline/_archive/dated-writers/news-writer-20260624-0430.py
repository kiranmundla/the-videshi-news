#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (04:30 UTC run)
2 NEW articles, distinct from all prior runs (monsoon, IMO seafarers, NSE IPO,
Iran sanctions, RBI NRI deposits, FII flows, etc.):
  1. Reliance Jio Platforms files DRHP for India's largest-ever IPO (~$4B fresh
     issue, ~$137B valuation, up to 27 crore new shares; Meta + Google backers).
     Markets/economy + diaspora-investor angle.
  2. India's sovereign-AI moment: Sarvam becomes the country's first sovereign-AI
     unicorn ($234M at $1.5B), IndiaAI Mission startups advance, and Bernstein
     warns India risks dependence on foreign LLMs. Tech + diaspora-talent angle.
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


# ─── Article 1: Jio Platforms IPO ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Jio Platforms files for India's largest-ever IPO")
    print("="*60)

    slug = "reliance-jio-platforms-ipo-drhp-largest-india-137-billion-ambani-diaspora-20260624"
    headline = "Ambani Just Filed the Paperwork for India's Biggest-Ever IPO. The Company Is Jio."
    subheadline = "Reliance has lodged draft papers to list Jio Platforms in Mumbai in an offering that could raise about $4 billion and value the business near $137 billion. For a diaspora that already touches Jio through Meta and Google's stakes, it is a rare chance to own a slice of the network that rewired India."

    body = """Mukesh Ambani has spent a decade promising that Jio would one day stand on its own in the public markets. On Friday, he finally set the clock running. Reliance Industries told the stock exchanges that the board of Jio Platforms had approved a draft red herring prospectus and filed it with India's market regulator, SEBI \u2014 the first formal step toward what could become the largest initial public offering in the country's history.

The numbers are the kind that bend a market. The prospectus proposes a fresh issue of up to 27 crore (270 million) new shares. People familiar with the plan say the company is targeting a raise of around 360 billion rupees, roughly $3.8 billion to $4 billion, for about 2.9 percent of its post-issue equity \u2014 a sliver that would still value Jio Platforms at somewhere between $131 billion and $137 billion. Reliance shares jumped almost 3 percent on the news, dragging the Sensex and Nifty up with them.

## The Company Behind the Number

Jio is not just a phone network. Since its disruptive 2016 launch \u2014 which collapsed data prices and pulled hundreds of millions of Indians online for the first time \u2014 Reliance Jio Infocomm has grown into the world's second-largest mobile operator by subscribers in a single country, behind only China Mobile. Jio Platforms, the holding company now headed to market, wraps that telecom business together with cloud, enterprise networking, digital content and a fast-expanding artificial-intelligence arm.

It also already carries some of the biggest names in global technology on its share register. Meta owns close to 10 percent of Jio Platforms and Google about 7.7 percent, stakes bought during a frenzied 2020 fundraising. Reliance still controls more than 66 percent. Ambani used the company's 49th annual general meeting to frame the listing as "the most important value creation milestone this year," and handed his children Akash, Isha and Anant the job of steering the IPO process \u2014 a public signal about succession as much as about capital.

## Why List Now

The timing is bold. Indian equities have cooled sharply: the Sensex is down nearly 10 percent for the year, foreign investors have pulled a record sum out of Indian stocks, and the market has been rattled by the US-Iran war, a patchy monsoon and worries about a hawkish US Federal Reserve. Listing activity has been subdued. Into that uncertainty, Reliance is dropping not one but a wave of mega-deals \u2014 the National Stock Exchange filed its own IPO papers the same week.

The logic is value unlocking. For years analysts have argued that the market struggles to price Jio's digital engine fairly while it sits inside a sprawling oil-to-retail conglomerate, applying a "conglomerate discount" to the whole. A separate listing gives investors a clean way to buy the telecom-and-technology story on its own. The prospectus says most of the proceeds \u2014 an estimated 275 billion rupees \u2014 will go to repaying Reliance Jio Infocomm's debt, positioning it for further 5G build-out, fixed broadband expansion, and AI and cloud services.

## Why the Diaspora Should Care

For overseas Indians, the Jio IPO is a chance to own, directly, the infrastructure that reshaped daily life back home \u2014 the cheap data that lets a parent in Pune video-call a child in New Jersey, the digital payments that move remittances the last mile, the streaming that keeps the diaspora tethered to Indian cricket and cinema. Many NRIs can participate through the non-resident investor route, and the listing will be a marquee test of whether the diaspora's appetite for Indian assets survives a jittery market.

There is a larger point of pride, too. Ambani pitched the listing as proof "that India can build technology companies of global scale, global capability, and global value." A successful Jio float would be the clearest signal yet that India can mint a homegrown tech giant the world wants to own \u2014 the same ambition that animates the country's parallel push into sovereign artificial intelligence.

## What's Next

The DRHP now sits with SEBI for review, a process that typically runs weeks to months, after which Reliance will set the price band, timing and final size. Details could shift before the listing. But the direction is set: barring a market shock, India is heading toward a record-breaking debut, and the diaspora will be watching \u2014 and, in many cases, looking to buy."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing hero image (Mukesh Ambani)...")
    img_url = fetch_wikipedia_person_image("Mukesh Ambani")
    img_caption = "Reliance Industries chairman Mukesh Ambani, whose Jio Platforms has filed for India's largest-ever IPO"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        img_url, ctitle = pick_commons([
            "Mukesh Ambani",
            "Reliance Jio store India",
            "Reliance Industries headquarters Mumbai"
        ])
    if not img_url:
        px = fetch_pexels_image("mumbai stock exchange building india")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Mumbai's financial district; Jio Platforms has filed for what could be India's biggest IPO"

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
            "Reuters (reuters.com, June 2026) \u2014 'Ambani's Jio Platforms files for $3.8 billion IPO that could be India's biggest, sources say': Jio Platforms filed regulatory papers for a Mumbai IPO to raise around $3.8 billion, targeting ~360 billion rupees ($3.81 billion), about 2.9% of post-issue equity, valuing the business around $131 billion; proceeds largely to repay an estimated 275 billion rupees of Reliance Jio Infocomm debt to fund 5G densification, fixed broadband, AI and cloud; Jio is the world's second-largest single-country mobile operator after China Mobile; Meta and Google are major foreign investors; Ambani called it 'the most important value creation milestone this year.'",
            "Outlook Business (outlookbusiness.com, June 2026) \u2014 'Reliance Industries Shares Climb Nearly 3% as Jio Files for IPO': Jio Platforms filed a DRHP with SEBI on Friday for a fresh issue of up to 27 crore shares; sources said the offering could raise about 37,700 crore rupees ($4 billion), valuing the company at roughly $137 billion; Reliance stock rallied ~2.75% to 1,345.45 rupees on the BSE, lifting the Sensex and Nifty.",
            "Wall Street Journal (wsj.com, June 2026) \u2014 'Reliance's Jio Platforms to Seek India Listing': board approved the draft IPO prospectus for submission to SEBI; offering involves up to 270 million new shares, subject to regulatory approval; Reliance owns more than 66% of Jio Platforms, Meta nearly 10%, Google 7.7%; Ambani said the listing will 'demonstrate to the world that India can build technology companies of global scale'; his children Akash, Isha and Anant Ambani will lead the IPO process; the NSE filed for its own IPO the same week; the Sensex has fallen nearly 10% this year."
        ]),
        "diaspora_angle": "The Jio IPO gives overseas Indians a rare, direct way to own the network that rewired daily life back home \u2014 the cheap data behind their video calls, the rails behind their remittances, the streaming that keeps them tied to Indian cricket and cinema \u2014 and, through the NRI investor route, the listing will be a marquee test of whether diaspora appetite for Indian assets holds up in a jittery market.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India's sovereign-AI moment ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India's sovereign-AI push and Sarvam unicorn")
    print("="*60)

    slug = "india-sovereign-ai-sarvam-unicorn-indiaai-mission-foreign-llm-dependence-diaspora-20260624"
    headline = "India Just Got Its First Sovereign-AI Unicorn. The Bigger Question Is Whether It's Building Fast Enough."
    subheadline = "Bengaluru's Sarvam has raised $234 million to build AI models from scratch in India, even as a Wall Street note warns the country risks letting foreign systems power its banks, defence and public services. For a diaspora that staffs the world's AI labs, the contest over who controls the models is suddenly personal."

    body = """India spent the last decade exporting AI talent. Now it is trying, urgently, to keep the AI itself. This week the country marked a milestone in that effort: Bengaluru-based Sarvam closed a $234 million round at a $1.5 billion valuation, becoming what investors are calling India's first sovereign-AI unicorn. The raise, led by HCLTech with $150 million and joined by Bessemer Venture Partners alongside existing backers Khosla Ventures and Peak XV Partners, is part of a planned $300 million Series B.

What makes Sarvam different from the dozens of Indian startups wiring foreign chatbots into their apps is that it builds the models itself. The company has released foundational models trained from scratch in India \u2014 a 105-billion-parameter model and a 30-billion-parameter version optimised for edge devices that can run on consumer hardware. Co-founder Vivek Raghavan says developers are now making around 10 million API calls a day to its systems, with usage tripling in the three months since India's AI summit. The models are tuned for Indian languages and are being deployed in banking, insurance, government services and defence \u2014 the sensitive sectors where a country least wants to depend on someone else's software.

## A Debate That Turned Real

The urgency is not abstract. In a note to investors this week, brokerage Bernstein warned that India risks becoming dependent on foreign-built AI unless it develops its own large language models, comparing them to strategic assets like fighter jets that can be subject to export controls. "India's core intelligence layer, from enterprise software to defence and space, could be powered by foreign LLMs," the note said. "Enter a geopolitical disruption, and that access could be curtailed overnight."

That scenario stopped being hypothetical when access to some leading Western AI models was reportedly disabled outside the United States, cutting off Indian developers from tools they had built workflows around. Zoho co-founder Sridhar Vembu framed it as a national-security matter, calling technology the "ultimate weapon" of sovereignty. Mohandas Pai, the former Infosys finance chief, urged Prime Minister Narendra Modi to launch a far bigger national AI mission, arguing existing programmes are "too slow, way too small" \u2014 and calling for an annual 50,000 crore rupee fund for deep tech and AI, plus a 200,000 crore rupee guarantee fund to build cloud, hardware and chips.

## What the Government Has Built So Far

India approved its IndiaAI Mission in 2024 with an outlay of about 10,371 crore rupees, covering public AI compute infrastructure and indigenous foundational models. Several startups selected under the mission are now advancing: voice-AI firm Gnani.ai, which received 177 crore rupees in grants for AI processors, has shipped speech-to-speech and text-to-speech systems, while Sarvam's adoption has surged. But officials concede the model needs to evolve. MeitY Secretary S Krishnan said the central question is how many models India can afford, and experts argue the government should shift from upfront grants to milestone-based funding tied to measurable outcomes such as enterprise adoption and open-source contributions.

## Why the Diaspora Should Care

This is, in a quiet way, a diaspora story. Indians and people of Indian origin run or sit near the top of nearly every major AI lab in the United States \u2014 the talent that built the frontier models India now worries about depending on. The sovereign-AI push is an attempt to give that talent a reason to build at home, or at least to build for home, and a growing number of returnee founders and US-based investors are betting it will work. Celesta Capital's Sriram Viswanathan, an early backer of Indian deep tech, expects the country's startups to attract sharply higher capital over the next year as the ecosystem matures.

For NRIs, the stakes are double-edged. Many work for the very Western labs whose dominance India is trying to reduce; many also want India to succeed on its own terms. The deposits they send home, the startups they fund, and the companies they may one day return to all run on digital rails that India increasingly wants to own end to end \u2014 from the data network Jio is about to take public to the AI models that will sit on top of it.

## What's Next

Expect more raises, louder calls for a bigger mission, and pressure on New Delhi to match rhetoric with rupees. Whether India can build models good enough to keep its own banks, hospitals and defence systems off foreign infrastructure is now one of the defining questions of its tech decade \u2014 and the diaspora, on both sides of the contest, has a stake in the answer."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing hero image (AI / data center topic)...")
    img_url, ctitle = pick_commons([
        "artificial intelligence data center server room",
        "data center servers India",
        "semiconductor chip processor",
        "server room computing",
        "GPU artificial intelligence computing"
    ])
    img_caption = "A data-center server hall; India is racing to build sovereign AI models trained at home"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("data center server room artificial intelligence")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Servers in a data center; India is pushing to build its own foundational AI models"

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
            "TechCrunch (techcrunch.com, June 2026) \u2014 'Sarvam becomes India's newest AI unicorn with $234 million funding round led by HCLTech': Sarvam raised $234 million at a $1.5 billion valuation, becoming India's newest AI unicorn; $150 million from HCLTech as lead strategic investor, with Bessemer Venture Partners and existing backers Khosla Ventures and Peak XV Partners; targeting $300 million total for Series B; follows launch of open-source 30B and 105B parameter models; models designed for Indian languages and deployed in banking, insurance, government services and defence; HCLTech to combine Sarvam's models with its enterprise relationships and engineering workforce.",
            "The Hindu BusinessLine (thehindubusinessline.com, June 23, 2026) \u2014 'IndiaAI Mission companies set to advance to next growth stage': Sarvam co-founder Vivek Raghavan said models process ~10 million API calls daily, with usage tripled in three months since the AI summit; Sarvam released foundational models trained from scratch in India including a 105B model and a 30B edge model that runs on consumer hardware; Gnani.AI deploying capital into foundational models, training data and talent, shipping Prisma v2.5, TTS and speech-to-speech models; MeitY Secretary S Krishnan said the goal is to determine how many models India can afford; experts urged a shift from upfront grants to milestone-based funding.",
            "Memeburn (memeburn.com, June 2026) \u2014 'Anthropic Curbs Push India Into Sovereign AI Debate in 2026': access to leading Western AI models was reportedly disabled outside the US; Mohandas Pai urged PM Modi to launch a stronger national AI mission, calling existing programmes 'too slow, way too small,' and called for an annual 50,000 crore rupee deep-tech/AI fund plus a 200,000 crore rupee guarantee fund for cloud, hardware and chips; Zoho's Sridhar Vembu framed technology as the 'ultimate weapon' of sovereignty; India approved the IndiaAI Mission in 2024 with a ~10,371.92 crore rupee outlay for public AI compute and indigenous foundational models.",
            "Livemint (livemint.com, June 2026) \u2014 'Week after Sarvam, Naukri founder's AI startup investments double in value' and 'Indian deep-tech to see funding surge amid sovereign push': Info Edge's Sanjeev Bhikchandani backs Gnani.ai, which received 177 crore rupees in IndiaAI grants; Bernstein warned India risks dependence on foreign AI unless it builds its own LLMs, comparing them to 'fighter jets' subject to export controls, noting 'India's core intelligence layer... could be powered by foreign LLMs' and access 'could be curtailed overnight'; Celesta Capital's Sriram Viswanathan expects Indian deep-tech to attract higher capital over the next 12 months; Skyroot Aerospace raised $60M at a $1.1B valuation on May 7, Sarvam $234M at $1.5B on June 15."
        ]),
        "diaspora_angle": "Indians and people of Indian origin run or sit near the top of nearly every major AI lab in the United States \u2014 the very talent that built the frontier models India now worries about depending on \u2014 so India's sovereign-AI push is an attempt to give that diaspora a reason to build at home or for home, even as many NRIs work for the Western labs whose dominance New Delhi is trying to reduce.",
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
