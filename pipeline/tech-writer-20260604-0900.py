#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-04 09:00 UTC batch"""

import json, os, uuid, re, io, requests, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ── Load env ──
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace" / ".env.pexels"]:
    if env_file.exists():
        for line in env_file.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Image helpers ──

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": "1200", "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers=UA, timeout=15)
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
                print(f"  ✓ Wikimedia Commons: {len(results)} results for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    import subprocess
    try:
        q = urllib.parse.quote(query)
        cmd = f'curl -sS "https://api.pexels.com/v1/search?query={q}&per_page=5" -H "Authorization: {PEXELS_KEY}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    """Download, compress, upload to Supabase article-images bucket. Returns public URL."""
    try:
        r = requests.get(img_url, headers=UA, timeout=20)
        r.raise_for_status()
        raw = r.content
        if len(raw) < 5000:
            print(f"  ⚠ Image too small ({len(raw)} bytes), skipping upload")
            return None
        compressed = compress_image(raw)
        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        }
        up = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{filename}",
            headers=upload_headers, data=compressed, timeout=30,
        )
        up.raise_for_status()
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
        return public_url
    except Exception as e:
        print(f"  ⚠ Upload failed: {e}")
        return None


def source_image(article_slug, person_name=None, topic_queries=None, pexels_query=None):
    """Multi-source compare: Wikipedia → Wikimedia Commons → Pexels. Returns (url, attribution, caption_source)."""
    candidates = []

    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append(("wikipedia", wiki_img))

    for q in (topic_queries or []):
        commons = fetch_wikimedia_commons_images(q)
        for c in commons[:2]:
            candidates.append(("wikimedia_commons", c["url"]))
        if candidates:
            break

    if pexels_query and not candidates:
        pxl = fetch_pexels_image(pexels_query)
        if pxl:
            candidates.append(("pexels", pxl))

    if not candidates:
        print(f"  ⚠ No image found for {article_slug}")
        return None, None

    source_name, best_url = candidates[0]
    filename = f"{article_slug}.jpg"
    final_url = upload_to_supabase(best_url, filename)
    if not final_url:
        # Try next candidate
        for src, url in candidates[1:]:
            final_url = upload_to_supabase(url, f"{article_slug}.jpg")
            if final_url:
                source_name = src
                break

    attribution = "Wikimedia Commons" if source_name in ("wikipedia", "wikimedia_commons") else "Pexels"
    return final_url, attribution


# ═══════════════════════════════════════════════════════
# ARTICLE 1: US Closes Chip Export Loophole
# ═══════════════════════════════════════════════════════
print("\n📰 Article 1: US Closes Chip Export Loophole")

art1_id = str(uuid.uuid4())
art1_slug = make_slug("us-closes-chip-export-loophole-china-nvidia-amd")

art1_img, art1_attr = source_image(
    art1_slug,
    topic_queries=["US China semiconductor export control", "semiconductor chip AI"],
    pexels_query="semiconductor chip closeup",
)

art1 = {
    "id": art1_id,
    "headline": "Washington Just Closed the Loophole That Let Chinese AI Firms Buy Nvidia Chips Through Malaysia",
    "subheadline": "Hundreds of thousands of Blackwell GPUs may have reached Chinese subsidiaries in Southeast Asia. The Commerce Department's weekend guidance shuts the door — but leaves another one ajar.",
    "slug": art1_slug,
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian semiconductor professionals working at Nvidia, AMD, and TSMC are on the front line of the US-China chip war. Every shift in export controls reshapes hiring, project assignments, and visa considerations for tens of thousands of Indian engineers in the Valley and beyond.",
    "tags": ["semiconductors", "export-controls", "nvidia", "amd", "us-china", "indian-tech"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters via TBS News", "url": "https://tbsnews.net/tech/us-takes-step-halt-nvidia-ai-chip-shipments-chinese-firms-outside-china-1115086"},
        {"name": "Communications Today", "url": "https://communicationstoday.co.in/us-moves-to-block-ai-chip-exports-to-chinese-firms-abroad/"},
        {"name": "EverMX", "url": "https://evermx.com/us-closes-nvidia-and-amd-ai-chip-export-loophole/"},
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": art1_img or "",
    "image_caption": "Advanced semiconductor chips used in AI data centres are at the centre of US-China export controls",
    "image_attribution": art1_attr or "",
    "body": """For roughly a year, some of the most powerful AI chips ever manufactured have been quietly flowing to Chinese companies — not directly to Beijing, but through a legal gap that let subsidiaries in Malaysia and other Southeast Asian nations buy them without a US export licence. On June 1, Washington finally moved to shut that door.

The US Department of Commerce issued guidance clarifying that export licence requirements for advanced AI accelerators now apply to any entity headquartered in China, regardless of where it is physically located. The affected hardware includes Nvidia's Blackwell and Rubin GPU architectures and AMD's MI350x — the very chips powering the largest AI training runs on the planet.

## How the Gap Opened

The loophole traces back to May 2025, when the Commerce Department chose not to enforce the AI Diffusion Rule drafted in the final weeks of the Biden administration. That rule had created a tiered licensing framework for chip exports. With enforcement suspended, a practical ambiguity emerged: the location test for licence requirements looked at where a purchasing entity was physically based, not where its parent company was headquartered.

Chinese AI companies spotted the gap immediately. By directing purchases through subsidiaries incorporated in less-restricted jurisdictions such as Malaysia, they could acquire Nvidia Blackwell chips and AMD advanced accelerators without the licensing scrutiny that direct Chinese buyers would face. One chip industry source with deep supply-chain knowledge estimated that hundreds of thousands of advanced chips may have moved through this channel during the roughly twelve-month enforcement gap.

"The floodgates have quietly opened," warned an anonymous paper that circulated in Washington policy circles just before the weekend guidance was issued.

## What Changes — and What Does Not

The Bureau of Industry and Security says it will now enforce licence requirements based on an entity's headquarters, not its local office address. This effectively closes the most obvious route for Chinese subsidiaries to acquire restricted silicon.

But critics note that the guidance does not address a second vulnerability. Former State Department official Chris McGuire pointed out that TSMC and other foundries are still not required to perform enhanced due diligence to ensure advanced AI chips they manufacture are not destined for Chinese front companies. "This is a HUGE problem," McGuire wrote. The guidance also does not require data centres that already hold these chips to return or decommission them.

Nvidia said the change does not alter its own compliance posture, noting that the Commerce Department had already imposed a direct licence requirement on the company. AMD did not immediately comment.

## Why Indian Engineers Should Pay Attention

The US-China chip war is not an abstract geopolitical chess match for Indian semiconductor professionals. Tens of thousands of Indians work at Nvidia, AMD, Qualcomm, and Intel on H-1B and L-1 visas. Every policy shift can reshape project assignments, team structures, and internal compliance requirements at these companies.

Beyond employment, the tightening export regime creates strategic opportunity for India. The TRUST Initiative between Washington and New Delhi — which advanced to factory-floor implementation earlier this month — positions India as a trusted semiconductor partner precisely because it sits outside the US-China control framework. Micron's Gujarat fab, Tata Electronics' Dholera plant, and the growing ecosystem of Indian chip design startups all benefit from a world in which supply chains are reorganising around geopolitical trust boundaries.

For NRI investors tracking Nvidia and AMD, the immediate market impact is modest — both stocks are up sharply in 2026, and closing a known leak does not fundamentally alter demand trajectories. But the episode is a reminder that the semiconductor industry's biggest risk factor is not technology but policy, and policy can shift over a single weekend.""",
}

# ═══════════════════════════════════════════════════════
# ARTICLE 2: NVIDIA Cosmos 3 + Isaac GR00T Physical AI
# ═══════════════════════════════════════════════════════
print("\n📰 Article 2: NVIDIA Cosmos 3 + Isaac GR00T Physical AI")

art2_id = str(uuid.uuid4())
art2_slug = make_slug("nvidia-cosmos-3-isaac-groot-humanoid-robots-physical-ai")

art2_img, art2_attr = source_image(
    art2_slug,
    person_name="Jensen Huang",
    topic_queries=["NVIDIA humanoid robot", "humanoid robot artificial intelligence"],
    pexels_query="humanoid robot technology",
)

art2 = {
    "id": art2_id,
    "headline": "Jensen Huang Wants NVIDIA to Be the Android of Humanoid Robots. Cosmos 3 and Isaac GR00T Are His Opening Move.",
    "subheadline": "NVIDIA's new open-source physical AI model and a six-foot reference robot aim to do for humanoids what CUDA did for GPUs — standardise the stack so everyone builds on NVIDIA.",
    "slug": art2_slug,
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian AI researchers at Stanford, UC San Diego, and NVIDIA's own labs are among the earliest adopters of Isaac GR00T. India's massive manufacturing automation opportunity — from Tata and Mahindra factories to warehouse logistics — could be a prime market for affordable humanoid platforms.",
    "tags": ["nvidia", "robotics", "physical-ai", "cosmos-3", "computex-2026", "indian-tech"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "NVIDIA Press Release (GlobeNewsWire)", "url": "https://www.globenewswire.com/news-release/2026/06/01/3036270/0/en/NVIDIA-Launches-Cosmos-3.html"},
        {"name": "Interesting Engineering", "url": "https://interestingengineering.com/innovation/nvidia-launches-cosmos-3-chip-fab-tools-and-humanoid-robot-platform"},
        {"name": "Engadget", "url": "https://www.engadget.com/ai/nvidias-isaac-gr00t-platform-gives-researchers-access-to-frontier-humanoid-robotics-060038498.html"},
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": art2_img or "",
    "image_caption": "NVIDIA CEO Jensen Huang at a recent keynote unveiling the company's physical AI vision",
    "image_attribution": art2_attr or "",
    "body": """Jensen Huang has been saying "the next wave is physical AI" for two years. At GTC Taipei last week, he finally showed what he meant — and it involves a six-foot-tall robot with seventy-five degrees of freedom, an open-source world model, and the kind of full-stack platform play that turned NVIDIA's GPUs into the default infrastructure of the AI era.

The two headline launches were Cosmos 3, an open foundation model for physical AI, and the Isaac GR00T reference humanoid, a joint hardware platform built on a Unitree H2 chassis. Together, they represent NVIDIA's most ambitious attempt yet to standardise the development of robots and autonomous vehicles on its own software and silicon.

## Cosmos 3: One Model to Rule the Physical World

Cosmos 3 is what NVIDIA calls the world's first "fully open omnimodel." Built on a mixture-of-transformers architecture, it pairs a reasoning transformer with an expert generation transformer. The result is a single system that can understand text, images, video, ambient sound, and physical actions — then generate all of them with what NVIDIA claims is leading physics accuracy.

The practical impact is speed. Training a robot to navigate a warehouse or an autonomous vehicle to handle a tricky intersection currently requires months of simulation, data collection, and evaluation. Cosmos 3 promises to compress that cycle to days by generating synthetic training data that is physically plausible. NVIDIA has formed the Cosmos Coalition — including Agile Robots, Black Forest Labs, Runway, and Skild AI — to push the model's capabilities further.

"The big bang of physical AI is just around the corner," Huang said. "Cosmos 3 gives developers a generational leap in ability to build robots, autonomous vehicles and vision AI that perceive, reason, plan and act in the physical world."

## Isaac GR00T: A Reference Design, Not a Product

The Isaac GR00T reference humanoid is not a product NVIDIA plans to sell. It is a standardised development platform that the company hopes will become for humanoid robots what Android became for smartphones — a common base that dozens of hardware makers build on, all running NVIDIA's software and chips.

The reference design is substantial. Standing nearly six feet tall and weighing 150 pounds, it uses a Unitree H2 chassis with 31 degrees of freedom across the body. Dual Sharpa Wave tactile five-finger hands add another 22 degrees of freedom. The onboard brain is a Jetson AGX Thor T5000 running a Blackwell GPU with 2,070 FP4 teraflops of AI performance and 128GB of unified memory.

Stanford Robotics Center, UC San Diego, ETH Zurich, and the Allen Institute for AI are among the first institutions to adopt the platform. "Robotics moves fastest when researchers can build on open platforms, share code and test ideas on real machines," said Stanford's executive director Steve Cousins.

## What This Means for Indian Engineers and India's Factory Floor

NVIDIA's physical AI push intersects with India in several ways. Indian researchers are heavily represented at the academic institutions adopting Isaac GR00T — Stanford and UC San Diego both have significant Indian faculty and PhD student populations in robotics and computer vision.

More practically, India's manufacturing sector is in the early stages of a massive automation push. Tata, Mahindra, and Reliance are investing billions in smart factories. The Foxconn-HCL plant in Tamil Nadu, the Tata Electronics fab in Dholera, and dozens of automotive assembly lines are potential early adopters of humanoid platforms that can handle repetitive physical tasks.

Today, those factories rely on fixed-path industrial robots. Humanoid platforms that can navigate unstructured environments — loading docks, mixed-use warehouses, quality inspection lines — represent a step change. India's labour cost advantage has traditionally made automation less urgent, but with labour shortages in specific manufacturing niches and a government push toward high-value production, the calculus is shifting.

For Indian engineers in Silicon Valley, the takeaway is career positioning. Physical AI is one of the few areas where demand for robotics, computer vision, and simulation expertise is growing faster than supply. NVIDIA is not the only player — Tesla, Figure, Boston Dynamics, and Agility Robotics are all scaling — but its platform strategy means the Isaac GR00T ecosystem will need developers who can build on it. That is a familiar playbook for anyone who watched CUDA become the lingua franca of AI computing.""",
}

# ═══════════════════════════════════════════════════════
# ARTICLE 3: Intel Crescent Island GPU
# ═══════════════════════════════════════════════════════
print("\n📰 Article 3: Intel Crescent Island GPU")

art3_id = str(uuid.uuid4())
art3_slug = make_slug("intel-crescent-island-gpu-cheap-memory-ai-inference")

art3_img, art3_attr = source_image(
    art3_slug,
    person_name="Lip-Bu Tan",
    topic_queries=["Intel data center GPU", "Intel Computex"],
    pexels_query="data center server room",
)

art3 = {
    "id": art3_id,
    "headline": "Intel's Crescent Island Skips the Memory Everyone Else Is Fighting Over. That Might Be the Point.",
    "subheadline": "By choosing cheap LPDDR5X over scarce HBM, Intel's new AI inference GPU trades raw bandwidth for massive capacity — and a price tag that could open doors for Indian cloud providers.",
    "slug": art3_slug,
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Thousands of Indian engineers work at Intel's design centres in Folsom, Santa Clara, and Bengaluru. Crescent Island's cost-efficient inference approach could be especially relevant for India's growing domestic cloud providers and AI startups that cannot afford HBM-heavy hardware.",
    "tags": ["intel", "ai-inference", "semiconductors", "computex-2026", "indian-tech", "gpu"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "TheStreet", "url": "https://www.thestreet.com/technology/intels-new-ai-chip-skips-the-costly-memory-nvidia-relies-on"},
        {"name": "WCCFTech", "url": "https://wccftech.com/intel-crescent-island-xe3p-gpu-scales-to-480-gb-of-cost-optimized-lpddr5x-memory/"},
        {"name": "Zacks", "url": "https://www.zacks.com/stock/news/2462781/can-intels-expanded-ai-infrastructure-portfolio-drive-future-growth"},
        {"name": "Barchart / Intel PR", "url": "https://www.barchart.com/story/news/34267853/intel-announces-new-ai-innovations-at-computex"},
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": art3_img or "",
    "image_caption": "Intel CEO Lip-Bu Tan unveiled the company's AI inference GPU strategy at Computex 2026",
    "image_attribution": art3_attr or "",
    "body": """In a semiconductor industry consumed by a single question — who can get the most HBM? — Intel just offered a different answer: what if you did not need it at all?

At Computex 2026, Intel pulled the curtain back on Crescent Island, a data centre GPU designed specifically for AI inference. The chip's most notable feature is not what it includes but what it leaves out. Instead of the high-bandwidth memory that powers every competing accelerator from Nvidia and AMD, Crescent Island uses LPDDR5X — the low-power memory more commonly found in smartphones and thin laptops.

It is an unconventional bet, and a deliberate one.

## The Memory Trade-Off

The global AI chip market is in a supply crunch. Nvidia's Vera Rubin and AMD's MI450X both depend on HBM4, which is manufactured by only three companies — Samsung, SK Hynix, and Micron — using advanced packaging capacity that is booked solid for years. The result is a seller's market where HBM commands premium prices and long lead times.

Intel's Crescent Island sidesteps this entirely. The reference design carries 160GB of LPDDR5X, and Intel says partners can build cards with up to 480GB. At 350 watts and air-cooled on a standard PCIe form factor, the card can drop into the servers companies already operate. Stack eight of them in one machine and you get 3.8 terabytes of local GPU memory.

The trade-off is bandwidth. Crescent Island delivers roughly 684 GB/s of memory throughput — far below what an HBM-equipped accelerator provides. For training massive foundation models, this would be a serious limitation. But for inference — the everyday work of running models to answer queries, generate text, or process images — the bottleneck is often capacity, not speed. Keeping a large model or a swarm of smaller AI agents resident in memory matters more than moving data at maximum velocity.

"Efficiently handle large, token-intensive workloads while reducing total cost of ownership" is how Intel positions the design. Translation: it is cheap, and it works for the growing majority of AI workloads that do not need to train a frontier model from scratch.

## Intel's Broader Computex Statement

Crescent Island is part of a larger portfolio Intel unveiled at Computex. The company also launched Xeon 6+ processors built on its 18A process technology, offering up to 288 Efficient-cores and the ability to consolidate nine older servers into one. New 800 Series Ethernet controllers round out the data centre story.

Under CEO Lip-Bu Tan, who took the helm in early 2025, Intel has pivoted from trying to match Nvidia's top-end performance to finding the gaps Nvidia leaves open. The company's stock reflects the bet's credibility — up over 190 per cent year-to-date, making it one of the strongest large-cap chip trades of 2026.

Eric Demers, the veteran GPU architect Tan recruited to lead Intel's fresh GPU effort, is targeting customer sampling for Crescent Island in the second half of 2026, with production expected in 2027.

## The India Angle: Cost-Efficient Inference Changes the Math

For India's AI ecosystem, Crescent Island is potentially more relevant than the headline Nvidia and AMD chips that dominate tech coverage. The reason is economics.

Indian cloud providers like Yotta, E2E Networks, and Jio Platforms are building AI inference capacity for a market where the willingness to pay per query is a fraction of Silicon Valley rates. HBM-heavy accelerators — at tens of thousands of dollars per card, with multi-year lead times — are a difficult proposition for companies serving Indian enterprise and consumer markets.

A 160GB inference card that uses commodity memory, fits in existing server racks, and costs significantly less per gigabyte of capacity could accelerate the economics of running AI models locally in India rather than routing everything through US cloud regions. For Indian AI startups building agentic systems, customer service bots, and vernacular language models — workloads that are inference-heavy and latency-sensitive — the capacity-over-bandwidth trade-off may be exactly right.

Intel has a substantial engineering presence in India, with design centres in Bengaluru and Hyderabad employing thousands of engineers. NRI investors who have watched Intel's dramatic turnaround in 2026 should note that the company's strategy is not to out-Nvidia Nvidia. It is to own the tier of AI infrastructure where cost, power, and deployment simplicity matter more than peak performance — a tier that describes most of the world's actual AI workloads.""",
}


# ═══════════════════════════════════════════════════════
# Insert all articles
# ═══════════════════════════════════════════════════════
articles = [art1, art2, art3]

for art in articles:
    # Remove empty image fields
    if not art["image_url"]:
        art.pop("image_url", None)
        art.pop("image_caption", None)
        art.pop("image_attribution", None)
    try:
        sb_post("p2_articles", art)
        print(f"✅ Published: {art['slug']}")
    except Exception as e:
        print(f"❌ Failed: {art['slug']}: {e}")

print(f"\n🎯 Done — {len(articles)} articles processed")
