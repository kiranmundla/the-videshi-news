#!/usr/bin/env python3
"""Technology writer for The Videshi — 2026-07-08 14:00 PT run.

Articles:
1. Synopsys kills fab software for AI chip design pivot
2. India's AI hiring surges while overall IT jobs shrink
3. Syntiant files for Nasdaq IPO, betting on edge AI chips
"""

import json, os, uuid, re, subprocess, requests, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ────────────────────────────────────────────────────────────
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# Load Pexels key
pexels_env = Path.home() / "workspace/.env.pexels"
PEXELS_KEY = ""
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if "PEXELS" in k.upper():
                PEXELS_KEY = v.strip()

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

# ── Image sourcing helpers ──────────────────────────────────────────────

def search_commons(query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in sorted(pages.items(), key=lambda x: x[1].get("index", 999)):
                info = page.get("imageinfo", [{}])[0]
                thumb = info.get("thumburl") or info.get("url")
                mime = info.get("mime", "")
                if thumb and "image" in mime:
                    results.append({
                        "url": thumb,
                        "title": page.get("title", ""),
                        "width": info.get("thumbwidth", info.get("width", 0)),
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Commons search error: {e}")
    return []

def search_pexels(query):
    """Search Pexels for stock photos via curl (not urllib — gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                # Pick the first landscape/large photo
                for p in photos:
                    src = p.get("src", {})
                    url = src.get("large2x") or src.get("large") or src.get("original")
                    if url:
                        return url
    except Exception as e:
        print(f"  ⚠ Pexels search error: {e}")
    return None

def verify_image(url):
    """Verify an image URL returns 200 and is > 5KB."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code} %{size_download}",
             "-A", "TheVideshi/1.0 (thevideshi.com)", url],
            capture_output=True, text=True, timeout=15
        )
        parts = result.stdout.strip().split()
        if len(parts) >= 2:
            code, size = parts[0], float(parts[1])
            return code == "200" and size > 5000
    except:
        pass
    return False

# ── Source images ────────────────────────────────────────────────────────

print("Sourcing images...")

# Article 1: Synopsys — semiconductor fabrication / chip design
img1 = None
img1_caption = ""
img1_attribution = ""

commons_results = search_commons("semiconductor fabrication clean room wafer")
for c in commons_results:
    title_lower = c["title"].lower()
    # Avoid unrelated images
    if any(bad in title_lower for bad in ["logo", "flag", "map", "portrait"]):
        continue
    if verify_image(c["url"]):
        img1 = c["url"]
        img1_caption = "Inside a semiconductor fabrication clean room where chip manufacturing tools monitor production quality"
        img1_attribution = "Wikimedia Commons"
        print(f"  ✓ Article 1 image: {c['title']}")
        break

if not img1:
    pexels_url = search_pexels("semiconductor chip fabrication clean room")
    if pexels_url and verify_image(pexels_url):
        img1 = pexels_url
        img1_caption = "Semiconductor fabrication equipment used in modern chip manufacturing"
        img1_attribution = "Pexels"
        print(f"  ✓ Article 1 fallback Pexels image")

# Article 2: India AI hiring — tech office / software developers
img2 = None
img2_caption = ""
img2_attribution = ""

pexels_url2 = search_pexels("software developer coding office team")
if pexels_url2 and verify_image(pexels_url2):
    img2 = pexels_url2
    img2_caption = "Software developers at work as India's tech sector undergoes an AI-driven hiring shift"
    img2_attribution = "Pexels"
    print(f"  ✓ Article 2 image from Pexels")

if not img2:
    commons2 = search_commons("software development India technology office")
    for c in commons2:
        if verify_image(c["url"]):
            img2 = c["url"]
            img2_caption = "Technology professionals at work in India's IT sector"
            img2_attribution = "Wikimedia Commons"
            print(f"  ✓ Article 2 fallback Commons: {c['title']}")
            break

# Article 3: Syntiant IPO — AI chip / circuit board
img3 = None
img3_caption = ""
img3_attribution = ""

commons3 = search_commons("integrated circuit AI chip processor closeup")
for c in commons3:
    title_lower = c["title"].lower()
    if any(bad in title_lower for bad in ["logo", "flag", "map"]):
        continue
    if verify_image(c["url"]):
        img3 = c["url"]
        img3_caption = "A microprocessor chip — the kind of ultra-low-power AI silicon that Syntiant designs for edge devices"
        img3_attribution = "Wikimedia Commons"
        print(f"  ✓ Article 3 image: {c['title']}")
        break

if not img3:
    pexels_url3 = search_pexels("microchip circuit board AI processor closeup")
    if pexels_url3 and verify_image(pexels_url3):
        img3 = pexels_url3
        img3_caption = "An AI processor chip designed for low-power edge computing applications"
        img3_attribution = "Pexels"
        print(f"  ✓ Article 3 fallback Pexels image")

# ── Articles ─────────────────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Synopsys Just Killed the Software That Runs Chip Factories. It Wants to Design the Chips Instead.",
        "subheadline": "The EDA giant told Samsung, SK Hynix, and a dozen other chipmakers their factory monitoring tools are end-of-life. AI chip design pays better — and India's 5,000 Synopsys engineers are pivoting with it.",
        "slug": make_slug("synopsys-kills-fab-software-ai-chip-design"),
        "category": "technology",
        "vertical": "semiconductor",
        "diaspora_angle": "Synopsys employs over 5,000 engineers in Bangalore, Hyderabad, and Noida who are being reoriented from legacy analytics to AI chip design — and India's new fabs will need alternative manufacturing software.",
        "tags": ["semiconductor", "ai", "chip-design", "eda", "synopsys", "india-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/synopsys-cut-chip-fab-manufacturing-control-software-shift-ai-design-sources-say-2026-07-07/"},
            {"name": "Data Center Dynamics", "url": "https://www.datacenterdynamics.com/en/news/synopsys-sells-its-processor-ip-solutions-business-to-globalfoundries/"},
            {"name": "CoinCentral", "url": "https://coincentral.com/synopsys-inc-snps-stock/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img1 or "",
        "image_caption": img1_caption,
        "image_attribution": img1_attribution,
        "body": """The nervous system of the world's chip factories is being switched off — and the company that built it says it has found something more profitable to do.

Synopsys, the American electronic design automation giant that supplies the software behind many of the world's most advanced semiconductors, has told more than ten chipmakers that it will stop developing two core manufacturing analytics products. The affected tools — the Equipment Engineering System and Fault Detection and Classification platform — monitor fabrication equipment in real time and flag anomalies before they cascade into defective chips.

Samsung Electronics, SK Hynix, Kioxia, and Qorvo are among the manufacturers that received "end of life" notices in April and May, Reuters reported on Monday. Synopsys will honour existing maintenance contracts but will release no new versions. A few dozen staff have already been laid off.

## AI design pays more

The reason is straightforward: AI chip design is where the margins are.

Synopsys completed its $35 billion acquisition of engineering software firm Ansys last year and has been aggressively repositioning itself as the premier tool maker for companies designing AI accelerators. In March, it unveiled technology aimed at enabling AI agents to take over large parts of the chip design process — a market where clients like Nvidia, AMD, and Apple pay handsomely for cutting-edge capabilities.

The factory-floor analytics business, by contrast, was acquired from South Korean firm BISTel in 2021 and required chipmakers to share tightly-held manufacturing data — a hard sell for companies like Samsung, which was already building its own in-house replacement.

"While we are discontinuing certain manufacturing analytics products, which are older diagnostic tools not in our customers' critical paths of production, we continue to invest in new capabilities in this area," a Synopsys spokesperson told Reuters. Samsung confirmed the transition and said there would be "no negative impact on production."

Last week, Synopsys also sold its processor IP business — including RISC-V cores and neural network processing units — to GlobalFoundries for an undisclosed sum, further concentrating its portfolio on high-margin AI design tools.

## What this means for Indian engineers

Synopsys employs more than 5,000 engineers across Bangalore, Hyderabad, and Noida — one of the largest EDA engineering concentrations outside the United States. As the company shifts resources from factory analytics to AI-driven chip design, those Indian engineering teams are being reoriented toward higher-value work: building the tools that help the world's biggest chipmakers design AI accelerators, automotive processors, and next-generation mobile chips.

For Indian engineers considering EDA careers, the signal is clear — manufacturing analytics is a shrinking space, while AI-assisted chip design is expanding rapidly.

## India's fabs need a plan B

The move also carries implications for India's own semiconductor ambitions. The country's five new fabrication plants — including the Tata-ASML facility in Dholera and CG Semi's packaging plant in Sanand — will need manufacturing analytics software of exactly the kind Synopsys is discontinuing. With the incumbent vendor walking away, these fabs will either need to source alternatives, build tools in-house, or look to Indian startups to fill the gap.

That gap could become an opportunity. India's nascent semiconductor software ecosystem, still small compared to the design tools built from Bangalore and Hyderabad, might find unexpected demand from the country's own fab buildout.

## What comes next

Synopsys plans to conclude maintenance obligation talks with each chipmaker by July. The broader trend is unmistakable: in semiconductor software, as in semiconductor hardware, AI is consuming everything else. The companies that once kept chip factories running are now racing to design the AI chips that those factories produce.

For Synopsys, the bet is that designing the brain is worth more than monitoring the body."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's AI Jobs Just Grew 16 Per Cent While Overall IT Hiring Shrank. The Industry's Two-Speed Future Is Here.",
        "subheadline": "New data from India's largest job portal shows AI roles surging even as the $315 billion IT sector cuts heads — a split that every NRI weighing a career move should understand.",
        "slug": make_slug("india-ai-hiring-boom-it-jobs-shrink-naukri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The traditional IT services pipeline that moved millions of Indian engineers to the US on H-1B visas is narrowing, while AI-skilled Indians are more in demand than ever — a career-shaping divergence for NRIs.",
        "tags": ["india-tech", "ai", "hiring", "it-services", "jobs", "h1b", "nri-careers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/ai-hiring-outpaces-overall-it-recruitment-india-report-shows-2026-07-03/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indian-it-firms-face-muted-q1-as-ai-shift-weak-demand-weigh-2026-07-06/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/top-it-companies-likely-to-post-subdued-q1-fy27-revenue-growth-says-brokerage"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img2 or "",
        "image_caption": img2_caption,
        "image_attribution": img2_attribution,
        "body": """If you work in Indian IT, your future depends entirely on which side of a widening divide you sit on.

New data from Naukri, India's largest jobs portal, reveals a striking divergence: hiring for artificial intelligence roles within the IT sector rose 16 per cent year-on-year in June, while overall IT job postings declined 3 per cent. Across all 14 sectors tracked, AI and machine learning positions jumped 25 per cent — the fastest-growing skills category in the country.

The numbers confirm what India's IT giants have been signalling for months. TCS Chairman N. Chandrasekaran has said "the day is not far" when the company will have an equal number of AI agents and employees. Last July, TCS cut more than 12,000 jobs; in the fiscal year ended March 2026, its net headcount fell by over 23,000.

"The divergence is important because it shows where tech companies are still investing," said Hitesh Oberoi, CEO of Info Edge, which owns Naukri. "AI is increasingly becoming a core capability area, especially as demand shifts towards more senior and specialised talent."

## The numbers behind the split

India's $315 billion IT services sector — the country's largest private employer and the most common pathway for Indian engineers to reach the United States — is being reshaped at a speed that has caught even veterans off guard.

Nine brokerages surveyed by Reuters expect the sector's top companies to report just 2.8 per cent constant-currency revenue growth in the April-June quarter, even as rupee-denominated numbers are inflated by the currency's depreciation. Citi expects a fourth consecutive year of subdued growth. JPMorgan sees revenue growth staying below 3-4 per cent for the "foreseeable future."

The Nifty IT index has slumped roughly 28 per cent in 2026 — the worst-performing major sector in India — as markets price in the risk that AI-powered automation will compress the industry's labour-intensive model. Nomura calls it a "perfect storm," with Middle East conflict-driven uncertainty compounding AI-driven pricing pressure.

But within this carnage, AI-specific roles are multiplying. Companies are hiring fewer traditional developers and more machine learning engineers, data scientists, and AI infrastructure architects. The insurance and consumer goods sectors showed the largest increases in AI job postings, suggesting the boom extends well beyond IT services.

## Why the diaspora should care

For the millions of Indian-origin tech workers in the United States, this split has direct career implications.

The traditional IT services pipeline — the one that moved generations of engineers from Hyderabad and Bangalore to client sites in New Jersey and Dallas — is under structural pressure. Companies are no longer building large benches of engineers waiting for projects. With AI tools compressing delivery timelines and team sizes, the model that sustained decades of H-1B placements is narrowing.

At the same time, AI-skilled Indian engineers are more in demand than ever. Major tech companies continue to hire Indian AI researchers and ML engineers, and the premium for these skills is rising both in India and abroad.

For NRIs considering a return to India, the data presents a nuanced picture: the overall IT job market is weaker, but someone with AI expertise would find more opportunity in India today than at any point in the country's tech history.

For NRI investors, the split underscores why the Nifty IT index's decline may not fully reflect the health of India's tech sector. The old revenue model is shrinking. The new one — smaller teams, higher billing rates, AI-embedded services — is growing. The question is whether incumbent IT giants can transition fast enough.

## What to watch

TCS reports first-quarter earnings on Thursday, followed by HCLTech on July 13, then Infosys and Wipro later this month. Analysts will be scrutinising three things: AI deal bookings, attrition in AI-skilled talent, and whether AI revenue can offset the decline in traditional services.

The gap between India's AI job growth and its IT sector contraction is not a temporary dislocation. It is the industry's new architecture — and the engineers who recognised that early are already on the right side of it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An Intel-Backed Chipmaker Just Filed to Go Public. It Thinks the AI Race Ends on Your Wrist, Not in a Data Centre.",
        "subheadline": "Syntiant makes ultra-low-power AI chips for earbuds, wearables, and cars. Its Nasdaq filing arrives as Cerebras's cautionary IPO cools and India's semiconductor push targets the exact same edge market.",
        "slug": make_slug("syntiant-ipo-edge-ai-chip-intel-nasdaq"),
        "category": "technology",
        "vertical": "semiconductor",
        "diaspora_angle": "India's semiconductor mission targets the same edge-device chip market that Syntiant plays in, and NRI engineers at Intel, Qualcomm, and TI work on directly competing edge AI processors.",
        "tags": ["semiconductor", "ipo", "edge-ai", "startup", "ai-chip", "intel", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/markets/deals/semiconductor-software-company-syntiant-corp-files-us-ipo-2026-07-06/"},
            {"name": "SiliconAngle", "url": "https://siliconangle.com/2026/07/06/syntiant-makes-low-power-chips-device-ai-files-initial-public-offering/"},
            {"name": "Stocktwits", "url": "https://stocktwits.com/news/after-cerebras-listing-intel-backed-ai-chip-firm-syntiant-files-for-ipo/"}
        ]),
        "score_total": 68,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img3 or "",
        "image_caption": img3_caption,
        "image_attribution": img3_attribution,
        "body": """The AI chip race has been defined by scale — Nvidia's massive GPU clusters, billion-dollar data centres, megawatt power demands. Syntiant is betting the future runs on a fraction of a watt.

The Irvine, California-based chipmaker filed for an initial public offering on the Nasdaq on Monday under the ticker SYTN, seeking to raise capital for its ultra-low-power AI processors designed to run machine learning models directly on devices. Intel Capital, Microsoft Global Finance, and Knowles Corp are among its backers.

Founded in 2017, Syntiant has raised $311 million to date, with its most recent round in December 2024 valuing the company at $646 million. Its Neural Decision Processors draw microwatts of power — a thousand times less than a standard mobile processor — enabling always-on voice recognition, audio processing, computer vision, and sensor fusion on battery-powered devices.

The chips are already deployed in earbuds, wearables, industrial systems, and automobiles. In late 2024, Syntiant acquired Knowles Corp's consumer MEMS microphone business, adding manufacturing capacity in China and Malaysia and the ability to bundle its AI chips with the microphones that feed them data.

## The financial picture

Syntiant posted a net loss of $20.9 million on revenue of $64.5 million for the first quarter of 2026, compared with a net loss of $14.1 million on revenue of $66.6 million a year earlier. Revenue dipped slightly while losses widened — a pattern common among semiconductor companies investing aggressively in R&D ahead of an inflection point.

Citigroup, BofA Securities, UBS Investment Bank, and Needham are the lead underwriters. The company plans to list under the symbol SYTN.

The IPO arrives at a complicated moment for AI chip companies going public. Cerebras Systems, which designs massive wafer-scale AI training chips, listed on Nasdaq in May but has since fallen 45 per cent from its opening price. Retail sentiment has turned bearish, raising questions about whether public markets are ready to value pre-profit AI chip companies generously.

## A different kind of AI chip

Syntiant's pitch is fundamentally different from Cerebras's or Nvidia's. Where cloud AI chips are measured in teraflops and consume kilowatts, Syntiant's processors are measured in tera-operations-per-watt and consume microwatts. The company calls this "physical AI" — machine intelligence that runs at the point of interaction rather than in a distant server.

The market for on-device AI is growing rapidly. Apple, Qualcomm, and Google are all investing in running AI models locally on phones and PCs, but Syntiant is targeting the tier below that — the billions of small, battery-powered devices where even a mobile processor draws too much power.

More than $260 billion of equity issuance is expected to arrive this year, according to JP Morgan, and AI-related IPOs have been a centrepiece of the revival. But the Cerebras experience suggests investors are beginning to differentiate between AI chip companies with clear paths to profitability and those still burning cash.

## The India connection

India's semiconductor mission is targeting exactly this segment of the chip market. The country's new OSAT and advanced packaging plants — including the CG Semi facility in Sanand that began operations this month — are designed for the kind of mid-complexity chips used in automotive, IoT, and wearable applications, not the bleeding-edge AI training processors that require TSMC's most advanced nodes.

For NRI engineers, many of whom work at Intel, Qualcomm, and Texas Instruments on edge AI processors, Syntiant represents both a competitor and a validation of their niche. The edge AI talent pool is disproportionately Indian, a function of India's deep bench in signal processing, embedded systems, and low-power design.

For NRI investors already exposed to Nvidia and AMD through the cloud AI trade, Syntiant offers a conceptual hedge — a bet that AI's long-term value will be distributed across billions of small devices, not concentrated in a few hundred data centres. The IPO will test whether public markets agree.

## What to watch

Syntiant has not yet disclosed a price range or share count; the IPO process typically takes four to six weeks from filing. Investors should watch the company's device deployment numbers, its revenue trajectory from the Knowles microphone business, and whether the edge AI narrative can sustain a premium valuation in a market that just punished Cerebras for lacking profitability.

In a world obsessed with bigger, hotter, more powerful AI chips, Syntiant is making the opposite bet. Whether that makes it a visionary or a footnote depends on how many of the world's 20 billion connected devices can learn to think for themselves."""
    },
]

# ── Insert ──────────────────────────────────────────────────────────────
print("\nInserting articles...")
for art in articles:
    if not art["image_url"]:
        print(f"  ⚠ No image for: {art['slug']} — skipping image")
    try:
        sb_post("p2_articles", art)
        print(f"  ✅ {art['slug']}")
    except Exception as e:
        print(f"  ❌ {art['slug']}: {e}")

print("\nDone.")
