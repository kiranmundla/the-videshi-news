#!/usr/bin/env python3
import json, os, uuid, re, io, requests, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# Load env
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

# Pexels env
pex_file = Path.home() / "workspace" / ".env.pexels"
if pex_file.exists():
    for line in pex_file.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
UA = "TheVideshi/1.0 (thevideshi.com)"
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

# ---------- Image helpers ----------
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                         headers={"User-Agent": UA}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}'")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml" or ii.get("width", 0) < 400:
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
        out = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape",
             "-H", f"Authorization: {PEXELS_KEY}"],
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
    base = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    r = requests.post(
        f"{base}/storage/v1/object/article-images/{filename}",
        headers={"apikey": key, "Authorization": f"Bearer {key}",
                 "Content-Type": "image/jpeg", "x-upsert": "true"},
        data=jpeg_bytes, timeout=60)
    if r.status_code not in (200, 201):
        print(f"    ⚠ Supabase upload failed {r.status_code}: {r.text[:200]}")
        return None
    return f"{base}/storage/v1/object/public/article-images/{filename}"

def source_and_host(candidates_urls, slug):
    """Try each candidate URL, download, compress, upload. Return final supabase URL."""
    for url in candidates_urls:
        if not url:
            continue
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
            if r.status_code != 200 or not r.headers.get("Content-Type", "").startswith("image"):
                print(f"    ⚠ skip {url[:60]} status={r.status_code}")
                continue
            if len(r.content) < 5000:
                print(f"    ⚠ too small {url[:60]}")
                continue
            jpeg = compress_image(r.content)
            final = upload_image_to_supabase(jpeg, f"{slug}.jpg")
            if final:
                print(f"  ✓ hosted: {final}")
                return final
        except Exception as e:
            print(f"    ⚠ download error {url[:60]}: {e}")
    return None

# ---------- ARTICLE 1: Upscale AI ----------
slug1 = make_slug("upscale-ai-2-billion-barun-kar-rajiv-khemani-nvidia-premji-nri")
# Person image: Barun Kar / Rajiv Khemani unlikely on Wikipedia; use Commons data center / AI networking
img1 = source_and_host([
    *( [c["url"] for c in fetch_wikimedia_commons_images("data center server racks network")] ),
    fetch_pexels_image("data center server room network cables"),
], slug1)

body1 = """Two Indian-origin networking veterans just built a $2 billion company in under a year — and they did it by betting on the least glamorous corner of the AI boom.

Upscale AI, the Santa Clara startup founded by **Barun Kar** and **Rajiv Khemani**, said on Monday it raised a $190 million extension to its funding round, lifting its valuation to $2 billion and total capital to roughly $500 million. The new money came with a roster of names that signals exactly how seriously Silicon Valley takes the problem Upscale is chasing: **Nvidia**, **Salesforce Ventures**, Singapore's **Temasek** and Seligman Ventures joined existing backers Premji Invest — the investment arm of Wipro founder **Azim Premji** — along with Tiger Global, Mayfield, Maverick Silicon and Saudi Arabia's Prosperity7.

What makes the speed remarkable is that Upscale has not shipped a product yet. It went from a $100 million seed round last September to unicorn status in January to a $2 billion valuation in June, all on the strength of a thesis and a team.

## The bottleneck nobody talks about

Everyone obsesses over GPUs. Far fewer people think about the wiring between them. As AI clusters swell to thousands of accelerators, the network connecting those chips — moving data between GPUs, memory and storage inside a single rack — has become the choke point. Legacy gear from Cisco and Broadcom was built for a pre-AI internet, not for the tightly synchronized "scale-up" workloads that modern training demands.

Upscale's pitch is a full-stack, open-standards alternative: custom silicon (a chip it calls SkyHammer), the systems around it, and the software to run them, all built to collapse the distance between accelerators into what it describes as a "unified rack." It is leaning on open consortia — Ultra Ethernet, Ultra Accelerator Link, SONiC — rather than a proprietary lock-in, which is precisely what attracted hyperscalers wary of paying Cisco-and-Broadcom rents forever.

## Why the founders matter

Kar and Khemani are not first-timers. Kar, an **IIT Kharagpur** graduate with a PhD from UMass Amherst, was on the founding team at Palo Alto Networks and ran its engineering for 15 years. Khemani, from **IIT Delhi** with a Stanford MBA, co-founded Innovium (sold to Marvell for over $1.2 billion) and Cavium (also acquired by Marvell). The two had already built Auradine together before spinning out Upscale. Their bench of 100-plus engineers is drawn from Marvell, Broadcom, Cisco, AWS, Google and Microsoft.

## The diaspora read

For an Indian engineer in the Bay Area watching layoffs ripple through Big Tech, Upscale is a reminder that the most reliable career hedge is still deep infrastructure expertise — the kind that takes 20 years to accumulate and does not evaporate when a product team gets cut. The founding duo's path, from IIT classrooms to two billion-dollar exits to a third venture, is the diaspora template playing out in real time.

It is also a money story. Premji Invest leading the round means Indian capital is now anchoring frontier American silicon, not just chasing it. And with Intel Capital and Qualcomm Ventures among earlier backers, Upscale sits at a crossroads of US chip incumbents and Indian wealth — the sort of cross-border bet NRIs with an eye on venture exposure will want to track. The risk is plain: a $2 billion valuation with no shipping product is the AI era's signature gamble. But if networking really is the next battleground, the people who wired the last computing era are well positioned to wire this one.

## What's next

Upscale says the capital will fund commercial deployment and the rollout of SkyHammer. The real test arrives when the first racks ship and customers measure whether the latency promises hold against Broadcom's entrenched Tomahawk line. For now, the founders have done the hard part of the AI gold rush — convincing the people selling the shovels to buy theirs too."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Two IIT Grads Built a $2 Billion AI Company in Under a Year. They Haven't Shipped a Product Yet.",
    "subheadline": "Upscale AI, founded by Palo Alto Networks and Cavium veterans Barun Kar and Rajiv Khemani, just pulled in Nvidia and Azim Premji's fund at a $2 billion valuation — on a thesis about the least glamorous corner of the AI boom.",
    "slug": slug1,
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Two IIT-trained, Bay Area networking veterans built a $2 billion AI infrastructure startup backed by Indian capital (Premji Invest) and Nvidia — a live template for diaspora engineers weighing whether deep-infrastructure expertise still beats chasing the AI-app gold rush.",
    "tags": ["ai", "indian-tech", "silicon-valley", "startups", "venture-capital", "semiconductors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/upscale-ai-valued-2-billion-after-funding-extension-2026-06-22/"},
        {"name": "SiliconANGLE", "url": "https://siliconangle.com/upscale-ai-raises-200m-to-develop-scale-up-ai-networking-chips/"},
        {"name": "Interesting Engineering", "url": "https://interestingengineering.com/breaking-the-ai-bottleneck-open-networks"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/upscale-ai-in-talks-to-raise-at-2b-valuation/"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img1,
    "image_caption": "Rows of servers and high-speed networking in a modern AI data center",
    "image_attribution": "Wikimedia Commons" if img1 and "wikimedia" in (img1 or "") else "Pexels",
    "body": body1,
}

# ---------- ARTICLE 2: Qualcomm investor day / data center pivot ----------
slug2 = make_slug("qualcomm-investor-day-dragonfly-data-center-ai-chip-cristiano-amon-nri")
img2 = source_and_host([
    *( [c["url"] for c in fetch_wikimedia_commons_images("semiconductor chip wafer processor")] ),
    fetch_pexels_image("semiconductor chip closeup processor"),
], slug2)

body2 = """For nearly two decades, Qualcomm was a smartphone company that happened to make the best modems in the business. On Wednesday, it will try to convince Wall Street it is something else entirely: an AI data-center contender. The stakes for the thousands of Indian engineers in its ranks — and for NRI investors who have ridden the stock's 40% run this year — are unusually concrete.

The occasion is Qualcomm's **Investor Day on June 24**, where CEO **Cristiano Amon** is expected to lay out a consolidated roadmap for data-center silicon, "physical AI," industrial AI and 6G. The market has already front-run the event. The San Diego chipmaker's shares have surged on reports it has won a custom-silicon engagement with a hyperscale customer and may be circling an acquisition of AI chip startup **Tenstorrent** — led by legendary engineer Jim Keller — for $8 billion to $10 billion.

## From Snapdragon to Dragonfly

Qualcomm's tell came at COMPUTEX in Taipei, where Amon unveiled **Dragonfly**, a new brand covering server CPUs, AI accelerators and custom silicon — a deliberate sibling to the Snapdragon name that powers phones and Windows laptops. In the company's last earnings call, Amon confirmed a "leading hyperscaler custom silicon engagement is on track for initial shipments later this calendar year," alongside a fresh $20 billion buyback.

The strategic logic is a bet on AI agents. Amon argues that as software shifts from chatbots (about 10,000 tokens per task) to reasoning (100,000) to autonomous agents (around 1 million), global token demand explodes — from an estimated 31.7 billion tokens in a 10-second window this year to 1.27 trillion by 2030. Qualcomm wants a chip at every layer of that "compute continuum," from the wearable on your wrist to the rack in the data center.

## Why the diaspora should watch closely

Qualcomm employs a deep bench of Indian engineers, many on H-1B and L-1 visas, across its San Diego, Bay Area and **Hyderabad** and **Bengaluru** design centers. A successful data-center pivot is not abstract for them — it determines whether the next decade of headcount growth happens in modem teams that are shrinking (handset revenue fell 13% last quarter) or in the AI silicon groups that are hiring. For an engineer weighing an internal transfer, Dragonfly is the part of the company to be inside.

There is also an India angle in the supply chain. Qualcomm has steadily expanded its India R&D footprint, and a serious server-chip business means more high-end design work routed to those centers, not just verification and support. For NRIs tracking where the value-added engineering lands, that matters.

## The skeptics' case

Not everyone is convinced. J.P. Morgan, while flagging Qualcomm could reach $3 billion in data-center revenue by fiscal 2027 and as much as $35 billion by 2031, has stayed on the sidelines "awaiting evidence of execution." One valuation analysis pegged the stock as roughly 34% overvalued after the rally. The handset business is wrestling with memory-supply constraints, and Nvidia now competes directly in PC chips.

That is the tension Amon must resolve on Wednesday. A smartphone giant has tried to muscle into data centers before and stumbled — Qualcomm itself abandoned a server-chip effort years ago. For Indian engineers and NRI investors alike, the question is not whether the AI story is exciting. It is whether, this time, Qualcomm can ship."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Qualcomm Spent 20 Years as a Phone-Chip Giant. On Wednesday It Has to Prove It Can Build for the Data Center.",
    "subheadline": "At its June 24 Investor Day, CEO Cristiano Amon will unveil the Dragonfly data-center roadmap and possibly a $10 billion acquisition — a pivot that will shape the careers of the thousands of Indian engineers inside Qualcomm.",
    "slug": slug2,
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Qualcomm's make-or-break data-center pivot will decide whether its large cohort of Indian engineers — in San Diego, the Bay Area, Hyderabad and Bengaluru — sees growth in shrinking handset teams or booming AI-silicon groups, and whether NRI investors' 40% stock run holds.",
    "tags": ["semiconductors", "qualcomm", "ai-chips", "data-center", "indian-tech", "h1b"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "SiliconANGLE", "url": "https://siliconangle.com/qualcomm-shares-surge-on-earnings-beat-20b-buyback-data-center-timeline/"},
        {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/QCOM/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/qualcomm-ai-pivot-data-center"},
        {"name": "Gizmochina", "url": "https://www.gizmochina.com/qualcomm-dragonfly-data-center-chip-brand/"},
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img2,
    "image_caption": "A close-up of a semiconductor wafer, the building block of modern AI chips",
    "image_attribution": "Wikimedia Commons" if img2 and "wikimedia" in (img2 or "") else "Pexels",
    "body": body2,
}

# ---------- ARTICLE 3: Jabil-Adani India AI manufacturing ----------
slug3 = make_slug("jabil-adani-ai-data-center-manufacturing-india-liquid-cooled-racks-nri")
img3 = source_and_host([
    *( [c["url"] for c in fetch_wikimedia_commons_images("data center cooling racks industrial")] ),
    fetch_pexels_image("server manufacturing assembly hardware factory"),
], slug3)

body3 = """India has spent years pitching itself as the place that designs the world's software and, lately, assembles its iPhones. The next ambition is harder and more lucrative: building the physical guts of the AI boom. A new alliance between an Apple supplier and an Adani company is the most concrete bet yet that it can.

Florida-based **Jabil**, one of the world's largest contract electronics manufacturers, and **Adani Enterprises** announced plans this week to form a strategic alliance to build a vertically integrated AI and data-center hardware manufacturing platform in India. The companies want to produce high-density, liquid-cooled AI racks, servers, storage and networking systems — plus the unglamorous but essential gear around them: power distribution units, coolant distribution units, transformers, switchgear and thermal management.

The framing is deliberately enormous. The partners said they are targeting "multi-gigawatt" AI rack capacity and a global infrastructure market opportunity they pegged at over $3 trillion across seven years. Jabil CEO **Mike Dastoor**, who raised the company's annual profit forecast on Wednesday partly on AI strength, called India "a market we believe will become increasingly important for both domestic and global AI infrastructure demand."

## The timing is not an accident

India's data-center pipeline just hit **8.33 gigawatts**, according to Knight Frank — more than five times existing operational capacity. Reliance, separately, is building what Akash Ambani calls a "sovereign AI backbone" in Jamnagar with Nvidia GB300 GPUs. The country is projecting $50 billion-plus in spending across data centers, cloud and AI. Adani alone has committed to $100 billion on renewable-powered, AI-ready data centers by 2035.

What the Jabil deal adds is the manufacturing layer. Until now, India has largely imported the racks and servers that fill its data centers. Making them domestically — using surface-mount technology and complex "box-build" assembly — moves the country up the value chain from operator to producer, and opens an export lane to hyperscalers worldwide.

## Why NRIs should care

For the Indian diaspora, this is the semiconductor-and-hardware story finally extending beyond chips into systems. An NRI tracking the India-fab narrative — Micron's Gujarat plant, Tata's Dholera ambitions — now has a parallel thread in AI hardware assembly, a segment with lower technical barriers than leading-edge fabs but enormous volume.

It is also a returnee story. Building giga-scale rack manufacturing requires exactly the supply-chain, thermal-engineering and operations talent that Indian professionals have spent careers accumulating at Jabil, Flex, Foxconn and the hyperscalers. For diaspora engineers who have weighed a move back, a credible domestic AI-hardware industry changes the calculus — these are senior roles that did not exist in India two years ago.

And for NRI investors, Adani Enterprises stock has outperformed a falling Nifty 50 over the past year, extending gains after the announcement. The Jabil tie-up is the kind of catalyst that keeps the conglomerate's infrastructure-to-AI pivot in the spotlight, for better and worse, given the scrutiny the group still attracts.

## The fine print

The companies were candid that they are still working on "definitive agreements and operational frameworks" — this is an intent to partner, not a ground-breaking. No financial details, no site, no timeline. India's broader hardware ambitions have a history of grand announcements that move slowly. But the demand signal is real, the capital is committed, and for once the manufacturing piece — not just the buildout — is on the table. If it lands, India would be assembling the machinery of the AI age, not merely renting it."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Designs the World's Software and Assembles Its iPhones. Now an Adani-Jabil Deal Wants It to Build the AI Machine Itself.",
    "subheadline": "Apple supplier Jabil and Adani Enterprises plan a multi-gigawatt platform to manufacture liquid-cooled AI racks and servers in India — a bid to move the country from data-center operator to hardware producer.",
    "slug": slug3,
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "A Jabil-Adani plan to manufacture AI server racks in India opens senior supply-chain and hardware-engineering roles that did not exist two years ago — a fresh data point for diaspora professionals weighing a return and NRI investors tracking India's climb up the AI value chain.",
    "tags": ["indian-tech", "data-center", "ai-infrastructure", "adani", "manufacturing", "make-in-india"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-supplier-jabil-adani-partner-build-ai-data-center-infra-platform-india-2026-06-15/"},
        {"name": "Business Wire", "url": "https://www.businesswire.com/news/home/adani-enterprises-jabil-ai-data-center-india"},
        {"name": "Press Trust of India", "url": "https://www.ptinews.com/adani-jabil-ai-data-centre-hardware-manufacturing"},
        {"name": "Reuters (Jabil earnings)", "url": "https://www.reuters.com/technology/jabil-raises-annual-profit-forecast-data-center-demand-2026-06-18/"},
    ]),
    "score_total": 74,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img3,
    "image_caption": "Liquid-cooled server racks of the kind used in modern AI data centers",
    "image_attribution": "Wikimedia Commons" if img3 and "wikimedia" in (img3 or "") else "Pexels",
    "body": body3,
}

articles = [art1, art2, art3]

for art in articles:
    if not art.get("image_url"):
        print(f"  ⚠ No image for {art['slug']} — inserting without hero (no image > wrong image)")
        art.pop("image_caption", None)
        art.pop("image_attribution", None)
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  [img={'yes' if art.get('image_url') else 'NONE'}]")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
