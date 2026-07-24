#!/usr/bin/env python3
import json, os, uuid, re, io, requests, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ---- Load env ----
for envname in [".env.supabase"]:
    env_file = Path.home() / envname
    if env_file.exists():
        for line in env_file.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

pex = Path.home() / "workspace" / ".env.pexels"
if pex.exists():
    for line in pex.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ---- Image helpers ----
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                         headers=UA, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}'")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params, headers=UA, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 400:
                    continue
                results.append({"url": ii.get("thumburl") or ii.get("url", ""),
                                "title": page.get("title", ""), "width": ii.get("width", 0)})
            if results:
                print(f"  ✓ Commons: {len(results)} for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    import subprocess
    try:
        url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"
        out = subprocess.run(["curl", "-sS", url, "-H", f"Authorization: {PEXELS_KEY}"],
                             capture_output=True, text=True, timeout=30).stdout
        data = json.loads(out)
        photos = data.get("photos", [])
        if photos:
            src = photos[0]["src"].get("large2x") or photos[0]["src"].get("large")
            print(f"  ✓ Pexels for '{query}'")
            return src
    except Exception as e:
        print(f"  ⚠ Pexels error '{query}': {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_image_to_supabase(jpeg_bytes, filename):
    r = requests.post(
        f"{SB_URL}/storage/v1/object/article-images/{filename}",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                 "Content-Type": "image/jpeg", "x-upsert": "true"},
        data=jpeg_bytes, timeout=60)
    if r.status_code not in (200, 201):
        print(f"    ⚠ Supabase upload failed {r.status_code}: {r.text[:200]}")
        return None
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"

def download_bytes(url):
    import subprocess
    try:
        r = requests.get(url, headers=UA, timeout=40)
        if r.status_code == 200 and r.content and len(r.content) > 5000:
            return r.content
    except Exception:
        pass
    # curl fallback (Wikimedia 429s on requests)
    try:
        out = subprocess.run(["curl", "-sS", "-A", UA["User-Agent"], "-o", "/tmp/_img.bin", url],
                             capture_output=True, timeout=60)
        data = Path("/tmp/_img.bin").read_bytes()
        if len(data) > 5000:
            return data
    except Exception:
        pass
    return None

def source_and_host(slug, person=None, commons_queries=None, pexels_query=None):
    """Try Wikipedia person -> Commons -> Pexels; download, compress, upload. Returns (url, attribution)."""
    candidates = []
    if person:
        wi = fetch_wikipedia_person_image(person)
        if wi:
            candidates.append((wi, "Wikimedia Commons"))
    for q in (commons_queries or []):
        for r in fetch_wikimedia_commons_images(q)[:2]:
            candidates.append((r["url"], "Wikimedia Commons"))
    if pexels_query:
        px = fetch_pexels_image(pexels_query)
        if px:
            candidates.append((px, "Pexels"))
    for url, attribution in candidates:
        raw = download_bytes(url)
        if not raw:
            continue
        try:
            jpeg = compress_image(raw)
        except Exception as e:
            print(f"    ⚠ compress failed: {e}")
            continue
        if len(jpeg) < 10000:
            continue
        final = upload_image_to_supabase(jpeg, f"{slug}.jpg")
        if final:
            print(f"  ✅ hosted image ({attribution}): {final}")
            return final, attribution
    print("  ⚠ No image hosted — leaving blank")
    return None, None

# ============ ARTICLES ============
articles_meta = [
    {
        "headline": "Salesforce Just Paid $3.6 Billion for an AI It Already Sells. Its Own Engineers Are Paying a Different Price.",
        "subheadline": "Marc Benioff bought a customer-service agent startup to bolster Agentforce — days after a third round of layoffs and a record 11-day stock slide. For the Indians who staff its cloud, the math is unsettling.",
        "slug_base": "salesforce-fin-acquisition-agentforce-layoffs-h1b-indian-engineers-nri",
        "diaspora_angle": "Salesforce employs thousands of Indian engineers on H-1B visas across San Francisco, Hyderabad and Bengaluru; as the company spends billions on AI agents while cutting Agentforce-adjacent roles, those workers face the sharpest version of the industry's automate-or-be-automated bind.",
        "tags": ["salesforce", "ai-agents", "h1b", "layoffs", "enterprise-software"],
        "urgency": "high",
        "score_total": 80,
        "vertical": "tech",
        "sources": [
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/salesforces-stock-seals-longest-losing-streak-on-record-as-newest-ai-acquisition-sparks-anxiety"},
            {"name": "Business Insider via DQIndia", "url": "https://www.dqindia.com/news/salesforces-usd-1-2-billion-agentforce-arr-sits-alongside-fresh-job-cuts"},
            {"name": "StartupNews.fyi", "url": "https://startupnews.fyi/salesforce-layoffs-agentforce-mulesoft-staff-get-30-week-severance"},
        ],
        "image": {"person": "Marc Benioff",
                  "commons": ["Salesforce Tower San Francisco", "Marc Benioff"],
                  "pexels": "san francisco skyline office tower"},
        "image_caption": "Salesforce chief executive Marc Benioff, whose company is spending billions on AI agents even as it cuts staff",
        "body": """Marc Benioff has a theory about artificial intelligence, and last week he put $3.6 billion behind it. Salesforce agreed to buy Fin, a startup whose flagship product is an "AI Agent" that resolves customer queries across chat, email, text and phone — capabilities that sound a great deal like Agentforce, the agent platform Salesforce already markets as its future. The company says Fin will "build on the strength" of Agentforce. Investors heard something less reassuring: that the firm leading the enterprise-AI charge still needs to buy in what it claims to have built.

The market's verdict was brutal. Salesforce shares fell for an eleventh straight session, shedding more than 22% over the streak — the longest losing run in the company's history. The stock is down roughly a third this year. RBC's Rishi Jaluria warned of "execution risk" piling up: Fin lands on top of last year's Informatica purchase and this month's Contentful deal, leaving Salesforce, in his words, with "a lot to integrate."

## The paradox in the numbers

What makes the spending spree jarring is the backdrop. On May 27th Salesforce reported that Agentforce had crossed $1.2 billion in annual recurring revenue, up 205% year on year — a genuinely impressive figure for a product barely a year old. Less than two weeks later, the company began its third round of layoffs in nine months.

A California WARN filing confirmed 86 roles eliminated in San Francisco — 63 in technology and product, 21 in administration, two in sales — with further cuts in Washington state and overseas that Salesforce declined to quantify. The affected teams worked on Agentforce, the MuleSoft integration tool and Marketing Cloud. The company insists its core Agentforce engineering was spared, and that the cuts are "re-engineering," not retrenchment. But the sequence is hard to unsee: announce record AI revenue, freeze engineering hiring, commit $300 million to Anthropic, then trim the humans adjacent to the very product the AI revenue is built on.

## Why the diaspora should read the fine print

For the Indian technologists who form a substantial slice of Salesforce's 80,000-strong workforce — in San Francisco on H-1Bs, and in the company's large Hyderabad and Bengaluru centres — this is not an abstract debate about software margins. It is a question about the next renewal cycle.

The cruelty of the visa math is specific. A laid-off H-1B holder has 60 days to find a new sponsor or leave the country, and Salesforce's affected US employees stay on payroll only until August 7th. Sixty days is not long to find a sponsoring employer in a sector where, by mid-June, 2026 layoffs had already passed 183,000. The severance — up to 30 weeks for some — softens the financial blow but does nothing for immigration status, which runs on a separate, unforgiving clock.

There is a second-order worry, too. Salesforce is San Francisco's largest private employer and a bellwether for enterprise software, the category that absorbed a generation of Indian engineers who chose the stability of B2B SaaS over the volatility of consumer tech. If the seat-based pricing model that funded all those jobs is now under question — and Benioff himself has mused about charging "by the task" rather than by the user — then the headcount logic of an entire industry shifts. Fewer seats sold can mean fewer seats staffed.

## The bet beneath the bet

Benioff's wager is that owning the agent layer outright — buying Fin rather than partnering — is worth the integration pain and the short-term stock punishment. He may be right; Agentforce's growth suggests real demand. But the strategy contains an uncomfortable admission for his own staff: if AI agents are good enough to be worth $3.6 billion, they are good enough to do work that people used to do.

For NRI engineers weighing whether to stay at a marquee SaaS name or jump to an AI-native startup, the Salesforce episode is a useful, if sobering, data point. The companies that built the cloud are now spending their cash piles to automate parts of it — and the people who built that cloud are being asked, politely and with generous severance, to prove they are not the part that gets automated next.

For now, the safest reading is the oldest one: in a downturn, keep the skills current, keep the network warm, and keep one eye on the WARN filings. The 60-day clock waits for no one."""
    },
    {
        "headline": "India's Insurance Salesman Just Went Public. Turtlemint's Muted Debut Is a Warning for the IPO Class of 2026.",
        "subheadline": "The Mumbai insurtech raised ₹883 crore at a ₹4,500 crore valuation — but a near-zero grey-market premium and a 19% wider loss tell NRI investors to read past the hype.",
        "slug_base": "turtlemint-ipo-insurtech-india-grey-market-premium-nri-investors",
        "diaspora_angle": "NRIs chasing exposure to India's fintech boom — many through the same broking apps now lining up to list — get a real-time stress test in Turtlemint: a loss-making distributor priced richly against a profitable peer, debuting into investor caution rather than euphoria.",
        "tags": ["turtlemint", "ipo", "fintech", "insurtech", "nri-investors"],
        "urgency": "medium",
        "score_total": 72,
        "vertical": "economy",
        "sources": [
            {"name": "Inc42", "url": "https://inc42.com/buzz/turtlemint-ipo-issue-subscribed-45-on-day-1/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/turtlemint-ipo-opens-today-gmp-risks-financials-and-key-things-to-know"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/money-and-banking/turtlemint-fintech-solutions-ipo-should-you-subscribe/"},
        ],
        "image": {"person": None,
                  "commons": ["Bombay Stock Exchange building Mumbai", "National Stock Exchange of India"],
                  "pexels": "stock exchange trading floor india"},
        "image_caption": "The Bombay Stock Exchange in Mumbai, where Turtlemint is set to list on June 29",
        "body": """Turtlemint, a Mumbai company that sells insurance policies through a network of small-town agents armed with an app, opened its initial public offering on June 19th. The numbers look like a success: ₹882.67 crore raised, a ₹4,513 crore valuation at the top of the ₹144–152 price band, ₹397 crore locked in from 32 anchor investors including ICICI Prudential, Mirae Asset and a clutch of insurers. And yet the most telling figure was the one in the unofficial market: a grey-market premium hovering between zero and ₹3 a share. Translation — the speculators who normally bid up hot listings see almost no quick gain here.

## What Turtlemint actually does

Strip away the "insurtech" label and Turtlemint is a distribution business. About 98% of its revenue comes from selling life and non-life insurance, with mutual funds, loans and deposits making up the rest. Its distinctive bet is the PoSP model — "point of sale person" — which lets a network of assisted agents sell policies in Tier 3 and Tier 4 towns where a purely digital pitch falls flat. It is, in effect, technology wrapped around the very human business of an Indian insurance agent talking a customer through a policy.

The growth is real. Revenue jumped 80% year on year to ₹741 crore in the first nine months of FY26. So are the losses: the net loss widened 19% to ₹185 crore over the same period. The IPO is a mix of a ₹661 crore fresh issue and ₹222 crore offer-for-sale, with proceeds earmarked for technology, payroll, working capital and unspecified "inorganic" expansion — corporate-speak for acquisitions.

## The valuation question NRIs should ask

Here is the part worth pausing on. At its upper band, Turtlemint trades at roughly 5.3 times FY25 proforma revenue, or 3.8 times annualised nine-month revenue. Its only listed peer, PB Fintech — the parent of Policybazaar — trades at about 10.9 times trailing revenue. On paper, Turtlemint looks cheaper. But PB Fintech has been profitable for three years; Turtlemint loses money at the EBITDA level. A discount to a profitable peer is not the same as a bargain when the thing being discounted is still burning cash.

Retail demand reflected that ambivalence: the issue was 45% subscribed on day one, with non-institutional investors taking up barely 1% of their quota. The anchor book did the heavy lifting. Shares list on the BSE and NSE on June 29th.

## Why this is the diaspora's story too

For non-resident Indians, Turtlemint is less interesting as a single trade than as a thermometer. A wave of Indian fintech and consumer names is queuing for the public markets — Razorpay filed confidentially just days earlier, PhonePe is preparing a $1.5 billion float, Kuku FM, Zetwerk and others are in the pipeline, and Jio is expected to file its draft prospectus for what could be India's largest-ever listing. Many NRIs access these names through the same broking platforms, like Zerodha and Groww, that have themselves become IPO candidates. The diaspora is both audience and, increasingly, shareholder.

Turtlemint's quiet debut suggests the easy money phase is over. India's primary market raised less in the first half of 2026 than a year earlier, and investors are no longer rewarding growth-at-any-cost. They are asking the unfashionable questions: When does this make a profit? What is it worth against a peer that already does? Is the grey-market premium telling me something the roadshow isn't?

For an NRI investor sitting in New Jersey or London, the practical takeaways are mundane but useful. First, the rules: most listed-equity IPO access for NRIs runs through an NRO/NRE demat account, and the OFS-versus-fresh-issue split matters because OFS money goes to exiting shareholders, not into the business. Second, the discipline: a richly valued, loss-making distributor debuting into a cautious market is exactly the kind of listing where the GMP and the subscription numbers earn their keep as warning lights.

None of this means Turtlemint will fail. Its Tier 3–4 reach is a genuine moat, and management insists profitability is "very soon." But the muted reception is the market's way of saying that in 2026, the burden of proof has shifted back to the company. For a diaspora that has watched India's startups raise, splurge and stumble through a long funding winter, that shift is the real headline — and it applies to every name still waiting in the IPO queue behind Turtlemint."""
    },
    {
        "headline": "DoorDash Built a Chatbot That Orders Your Dinner. The Engineers Who Built It Tell a Bigger Story.",
        "subheadline": "'Ask DoorDash' is the latest gig-economy app to bolt on an AI agent — part of a costly platform rebuild overseen by an Indian-origin finance chief, and a preview of where consumer tech jobs are heading.",
        "slug_base": "doordash-ask-doordash-ai-chatbot-agentic-gig-economy-indian-engineers-nri",
        "diaspora_angle": "DoorDash, Uber, Instacart and their peers employ large cohorts of Indian engineers — many on H-1B and OPT — and their pivot to agentic AI, led at DoorDash by CFO Ravi Inukonda, reshapes both the product these workers build and the security of the jobs that build it.",
        "tags": ["doordash", "ai-agents", "gig-economy", "indian-engineers", "consumer-tech"],
        "urgency": "medium",
        "score_total": 70,
        "vertical": "tech",
        "sources": [
            {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/doordash-dash-launches-ai-powered-chatbot-to-streamline-ordering-and-reservations"},
            {"name": "DoorDash Newsroom", "url": "https://about.doordash.com/"},
        ],
        "image": {"person": None,
                  "commons": ["DoorDash delivery", "food delivery courier bag"],
                  "pexels": "food delivery app smartphone restaurant"},
        "image_caption": "A food-delivery courier; DoorDash is rebuilding its platform around AI agents",
        "body": """DoorDash has taught a chatbot to order dinner. "Ask DoorDash," launched on June 11th in select markets, lets a customer place food and grocery orders and book restaurant reservations using photos and plain-text prompts — snap a picture of a dish, describe a craving, and the agent does the rest. It is a small feature with a large amount of strategy behind it, and for the Indian engineers who populate America's consumer-tech firms, it is worth more than a passing glance.

## A feature riding a $1 billion rebuild

"Ask DoorDash" is not a standalone gimmick. Finance chief Ravi Inukonda — one of the growing roster of Indian-origin executives running the money at Silicon Valley platforms — has framed it as one piece of a sweeping technical overhaul. DoorDash is stitching together a "unified tech stack" that absorbs its recent acquisitions, including the restaurant-reservation platform SevenRooms and the European delivery firm Deliveroo. That integration, Inukonda told investors, is a significant chunk of the company's 2026 spending.

The context is unforgiving. DoorDash shares have fallen about a third over the past year, and the company is pouring money into autonomous delivery and AI even as Wall Street frets about when the returns arrive. Every gig-economy platform is now racing to bolt agentic AI onto its app: Uber and Instacart are pushing the same way, each betting that a conversational layer will keep users inside its walls rather than defecting to a rival — or to a general-purpose assistant that could one day place the order for them.

## Why the diaspora is in the frame

Companies like DoorDash, Uber, Lyft, Airbnb and Instacart are major employers of Indian technologists in the United States, a great many of them on H-1B visas or OPT extensions after a US master's degree. The shift these firms are making — from human-operated marketplaces to AI-mediated ones — changes the work twice over.

First, it changes what gets built. An engineer who spent three years optimising a checkout funnel is now asked to build and supervise an agent that replaces parts of that funnel. The skill premium moves toward machine-learning fluency, prompt and evaluation pipelines, and the unglamorous plumbing of stitching acquired companies into one stack. For Indian engineers who entered consumer tech through web and mobile development, that is a re-skilling mandate, not an optional course.

Second, it changes how many people are needed to build it. The gig platforms have not announced DoorDash-specific cuts tied to this feature, but the broader pattern is stark: tech layoffs in 2026 had passed 183,000 by mid-month, and consumer-tech firms under share-price pressure have been among the trimmers. For a worker whose right to remain in the country is tied to continuous employment, "the platform is becoming more efficient" is a sentence with a double meaning.

## The Indian thread runs deeper than headcount

There is an irony worth naming. The agentic-AI wave washing over American gig apps is being shaped, in part, by Indian talent on both sides of the ocean — Indian-origin executives like Inukonda steering the strategy in California, and Indian engineering centres building the back ends in Bengaluru and Hyderabad. India is also where many of these consumer models will be stress-tested at scale: it is one of the world's largest mobile-first markets, and lessons learned there increasingly flow back into global products.

For the NRI reader, "Ask DoorDash" is a small, useful signal of three things at once. As a consumer, expect the apps in your pocket to start answering in sentences rather than menus. As an investor, note that these features are being funded out of share-price weakness, not strength — the spending is defensive. And as a professional, recognise that the gig economy, long a steady employer of immigrant engineers, is reorganising around agents that do tasks people used to do.

The dinner order is trivial. The trajectory is not. Every consumer platform that an Indian engineer might work for is making the same pivot at the same time, and the question facing that engineer is no longer whether to learn the new tools but how fast. DoorDash just made the timeline a little more concrete."""
    },
]

# ---- Source images, build payloads, insert ----
inserted = []
for meta in articles_meta:
    slug = make_slug(meta["slug_base"])
    img = meta.get("image", {})
    image_url, attribution = source_and_host(
        slug,
        person=img.get("person"),
        commons_queries=img.get("commons"),
        pexels_query=img.get("pexels"),
    )
    art = {
        "id": str(uuid.uuid4()),
        "headline": meta["headline"],
        "subheadline": meta["subheadline"],
        "slug": slug,
        "category": "technology",
        "vertical": meta["vertical"],
        "diaspora_angle": meta["diaspora_angle"],
        "tags": meta["tags"],
        "urgency": meta["urgency"],
        "sources": json.dumps(meta["sources"]),
        "score_total": meta["score_total"],
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "body": meta["body"],
    }
    if image_url:
        art["image_url"] = image_url
        art["image_caption"] = meta["image_caption"]
        art["image_attribution"] = attribution
    wc = len(meta["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {slug}  ({wc} words, img={'yes' if image_url else 'NONE'})")
        inserted.append((meta["headline"], wc, bool(image_url)))
    except Exception as e:
        print(f"❌ {slug}: {e}")

print("\n=== SUMMARY ===")
for h, wc, hasimg in inserted:
    print(f"  • [{wc}w, img={'Y' if hasimg else 'N'}] {h}")
print(f"Total inserted: {len(inserted)}/{len(articles_meta)}")
