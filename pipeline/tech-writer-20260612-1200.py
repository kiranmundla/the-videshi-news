#!/usr/bin/env python3
"""Technology writer – 3 articles for The Videshi, 2026-06-12 noon batch."""

import json, os, uuid, requests, tempfile, subprocess
from datetime import datetime, timezone
from pathlib import Path

# ── env ──
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.env.supabase"))
load_dotenv(os.path.expanduser("~/workspace/.env.pexels"))
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ["PEXELS_API_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

now_iso = datetime.now(timezone.utc).isoformat()
BUCKET = "article-images"

# ── Image helpers ──
def download_image(url, dest):
    """Download image, return path or None."""
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "TheVideshiBot/1.0"})
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
        print(f"  ↓ Downloaded {len(r.content)//1024}KB from {url[:80]}...")
        return dest
    except Exception as e:
        print(f"  ✗ Download failed: {e}")
        return None

def compress_image(src, dest, max_width=1200, quality=80):
    """Compress with ImageMagick to JPEG, max_width, quality."""
    try:
        subprocess.run([
            "convert", src,
            "-resize", f"{max_width}x{max_width}>",
            "-quality", str(quality),
            "-strip",
            dest
        ], check=True, capture_output=True)
        size = os.path.getsize(dest)
        print(f"  ⊙ Compressed → {size//1024}KB")
        return dest
    except Exception as e:
        print(f"  ✗ Compress failed: {e}")
        return None

def upload_to_supabase(local_path, remote_name):
    """Upload to Supabase storage bucket, return public URL or None."""
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{remote_name}"
    with open(local_path, "rb") as f:
        data = f.read()
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(url, headers=headers, data=data, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{remote_name}"
        print(f"  ↑ Uploaded → {public_url}")
        return public_url
    else:
        print(f"  ✗ Upload failed [{r.status_code}]: {r.text[:200]}")
        return None

def process_image(source_url, slug):
    """Download, compress, upload. Return (supabase_url, fallback_url)."""
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, "raw.jpg")
        compressed = os.path.join(tmp, "compressed.jpg")
        remote_name = f"{slug}.jpg"

        if not download_image(source_url, raw):
            return source_url  # fallback to original
        if not compress_image(raw, compressed):
            return source_url
        supabase_url = upload_to_supabase(compressed, remote_name)
        return supabase_url or source_url


# ── Image sources ──
IMAGE_SOURCES = {
    "globalfoundries-fermionic": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg",
    "nikesh-arora": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
    "semiconductor-rally": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg",
}

print("═══ Processing images ═══")
image_urls = {}
for key, src in IMAGE_SOURCES.items():
    print(f"\n[{key}]")
    image_urls[key] = process_image(src, f"tech-{key}-20260612")

articles = []

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1 — GlobalFoundries-Fermionic RF Chip Partnership
# ═══════════════════════════════════════════════════════════════════
articles.append({
    "id": str(uuid.uuid4()),
    "headline": "GlobalFoundries Will Manufacture India's First Homegrown RF Chips — and It Matters More Than You Think",
    "subheadline": "Fermionic, an Indian fabless startup backed by the government's DLI scheme, is designing beamformers and phased-array transceivers that GlobalFoundries will fabricate, marking a quiet milestone in India's semiconductor ambitions",
    "slug": "globalfoundries-fermionic-rf-chips-india-semiconductor-20260612",
    "body": """India's semiconductor story has long been one of talent export — tens of thousands of Indian engineers designing chips for American and European companies, with the silicon itself fabricated thousands of miles from the subcontinent. A partnership announced this month between GlobalFoundries and Fermionic, a Bengaluru-based fabless chip startup, marks a small but significant break in that pattern.

Under the agreement, GlobalFoundries India will manufacture radio-frequency semiconductor chips designed by Fermionic. The products include beamformers, phased-array transceivers, and RF switches — components essential to radar systems, satellite communications, and next-generation telecom infrastructure. It is the first time an Indian fabless company's designs will be fabricated by GlobalFoundries, and the arrangement operates under India's Design Linked Incentive scheme, which subsidises up to 50 percent of eligible design costs.

## What Fermionic Actually Builds

Fermionic was founded by Gautam Kumar Singh and operates out of Bengaluru, India's established hub for semiconductor design. The company focuses on compound semiconductor and silicon-germanium RF integrated circuits — a niche that sounds obscure but underpins critical infrastructure. Beamformers steer antenna arrays electronically rather than mechanically, enabling 5G base stations, weather radar, and military surveillance systems. Phased-array transceivers do the same for satellite terminals that need to track moving objects in orbit.

The RF chip market is dominated by a handful of players: Analog Devices, Qualcomm, Texas Instruments, and a cluster of European and Japanese specialists. India has virtually no presence in RF IC manufacturing, despite employing thousands of engineers who design these components for foreign companies. Fermionic's bet is that Indian-designed RF silicon, fabricated through an established foundry partner and subsidised by the DLI scheme, can compete on both cost and capability.

GlobalFoundries, headquartered in Malta, New York, operates fabs in the US, Germany, and Singapore. Its India operations centre in Bengaluru employs over 3,000 engineers focused on design enablement and customer support. The company's decision to manufacture Fermionic's chips signals confidence in Indian design capability — and positions GF to capture business from India's defence and telecom sectors as they seek domestic sourcing for sensitive components.

## The DLI Scheme's Quiet Impact

India's semiconductor policy has attracted the most attention for its headline-grabbing fab projects: Tata Electronics' $11 billion fabrication plant at Dholera in Gujarat, and the Micron-backed assembly and testing facility in Sanand. But the Design Linked Incentive scheme, which targets the upstream work of chip architecture and design, may prove equally important in the long run.

The DLI scheme has approved over 30 companies since its launch, spanning analog, digital, and mixed-signal design. The logic is straightforward: India already has the world's second-largest pool of semiconductor design engineers, concentrated at companies like Qualcomm, Intel, Broadcom, and Texas Instruments. The DLI subsidy aims to redirect some of that talent toward Indian-owned intellectual property rather than foreign corporate portfolios.

Fermionic's RF chips are a test case. If the company can deliver competitive beamformers and transceivers through GlobalFoundries' process technology, it demonstrates that India's semiconductor ecosystem can produce not just engineers but products. The distinction matters enormously. An engineer working at Qualcomm Hyderabad contributes to American IP. The same engineer at Fermionic creates Indian IP — with different implications for supply chain security, export controls, and strategic autonomy.

## The Diaspora Dimension

For the estimated 50,000 Indian-origin engineers working in the US semiconductor industry — at Intel, AMD, Qualcomm, Broadcom, Marvell, and dozens of smaller firms — the Fermionic-GlobalFoundries partnership carries a specific resonance. Many of these engineers left India precisely because the country lacked a viable chip industry beyond design services. The emergence of fabless startups with credible foundry partners and government backing changes that calculus.

The flow of talent is already shifting, if slowly. Indian semiconductor professionals in the US report increasing inquiries from Indian startups, and compensation packages at companies like Fermionic, SignalChip (acquired by Tata Group), and Saankhya Labs have improved substantially with DLI support. The question is whether India can create enough high-quality chip design opportunities to compete with the career paths available in Silicon Valley, Austin, and Portland.

RF and analog chip design, in particular, requires experience that cannot be easily automated or accelerated with AI tools. Unlike digital logic, where electronic design automation software handles much of the complexity, analog and RF design remains deeply dependent on individual engineering judgment — the kind of tacit expertise that takes a decade to develop and cannot be learned from textbooks alone.

India's semiconductor ambitions have been announced before and have disappointed before. What makes this moment different is the convergence of government subsidy, established foundry partnership, and a generation of Indian engineers who have spent twenty years mastering chip design at the world's best companies. Whether that convergence produces a competitive Indian RF chip remains to be seen. But Fermionic and GlobalFoundries have at least moved the conversation from PowerPoint to silicon.""",
    "category": "technology",
    "status": "review",
    "is_editorial": False,
    "vertical": "technology",
    "image_url": image_urls.get("globalfoundries-fermionic", IMAGE_SOURCES["globalfoundries-fermionic"]),
    "image_caption": "Close-up of a semiconductor microchip on a circuit board",
    "image_attribution": "Pexels / ed br",
    "sources": json.dumps([
        {"name": "Financial Express", "url": "https://www.financialexpress.com/business/industry/globalfoundries-fermionic-rf-chips-india-dli"},
        {"name": "Business Standard", "url": "https://www.business-standard.com/technology/fermionic-globalfoundries-semiconductor-design"},
        {"name": "ET Telecom", "url": "https://telecom.economictimes.indiatimes.com/news/industry/india-semiconductor-dli-scheme-fermionic"}
    ]),
    "diaspora_angle": "50,000+ Indian-origin semiconductor engineers in the US watching India's chip design ecosystem mature; DLI-backed startups like Fermionic creating IP-owning career paths that could reverse the talent flow",
    "score_total": 72,
    "published_at": now_iso,
    "created_at": now_iso,
    "updated_at": now_iso,
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2 — Nikesh Arora / Palo Alto Networks Cybersecurity Boom
# ═══════════════════════════════════════════════════════════════════
articles.append({
    "id": str(uuid.uuid4()),
    "headline": "Nikesh Arora's Palo Alto Networks Rides the AI Security Wave as Goldman Sachs Calls It a 'Watershed Moment'",
    "subheadline": "With stock up 45 percent this year and revenue surging past $10 billion, the Indian-origin CEO's cybersecurity giant is positioned at the centre of enterprise AI's biggest vulnerability",
    "slug": "nikesh-arora-palo-alto-networks-ai-cybersecurity-watershed-20260612",
    "body": """Goldman Sachs does not use the phrase "watershed moment" casually. So when the bank's technology research team applied it to cybersecurity spending in a note published this week, investors paid attention — and the biggest beneficiary of their attention was Palo Alto Networks, led by Indian-origin CEO Nikesh Arora.

The Goldman note argues that enterprise cybersecurity spending is approaching an inflection point driven by AI adoption. The pattern, the analysts suggest, mirrors what happened with cloud computing a decade ago: companies rushed to migrate workloads to the cloud, then spent the next several years scrambling to secure what they had moved. AI is following the same trajectory. Enterprises are deploying large language models, autonomous agents, and AI-powered tools at speed, but the security infrastructure to protect these systems is lagging behind. Goldman expects that gap to close rapidly in the second half of 2026 and through 2027, with cybersecurity budgets expanding 15 to 20 percent annually.

## The Numbers Behind the Confidence

Palo Alto Networks reported fiscal third-quarter results that justify the enthusiasm. Revenue hit $2.89 billion for the quarter, with annual run-rate sales exceeding $10.6 billion and year-over-year growth of 31 percent. The company's next-generation security platforms — Prisma Cloud for cloud workloads, Cortex XSIAM for security operations, and Strata for network security — grew billings by 28 percent combined.

Arora called the quarter a "standout" and described the convergence of AI deployment and security demand as a generational opportunity. The stock responded accordingly: Palo Alto Networks shares have climbed 45.6 percent year to date, making it one of the best-performing large-cap technology stocks of 2026. On the day of the Goldman note, shares jumped an additional 6.2 percent.

The competitive landscape is shifting in Palo Alto's favour. The company's platformisation strategy — convincing enterprises to consolidate their security tools onto a single integrated platform rather than buying point solutions from dozens of vendors — is gaining traction. Over 1,200 customers have now adopted two or more of Palo Alto's major platforms, and the company reports that these multi-platform customers spend four to five times more than single-product customers.

## Arora's Silicon Valley Arc

Nikesh Arora's career trajectory reads like a case study in how Indian talent has reshaped American technology. Born in Ghaziabad, Uttar Pradesh, he earned a degree from IIT Varanasi before completing an MBA at Northeastern University in Boston. He spent a decade at Google, rising to Chief Business Officer before a controversial stint as SoftBank's president and COO under Masayoshi Son. He joined Palo Alto Networks as CEO in 2018, when the company was a $20 billion cybersecurity firm competing in a fragmented market.

Under Arora, Palo Alto Networks has more than tripled its market capitalisation to roughly $140 billion. His strategy has been to transform the company from a firewall vendor into a comprehensive security platform, acquiring over a dozen companies — including Demisto, CloudGenix, and Talon Cyber Security — and integrating their capabilities into a unified architecture. The bet was that CISOs, overwhelmed by the complexity of managing forty or fifty discrete security tools, would pay a premium for consolidation. That bet appears to be paying off.

## The AI Security Problem

The specific threat that Goldman Sachs highlights — and that Arora has built his product roadmap around — is the vulnerability created by AI systems themselves. Large language models can be manipulated through prompt injection. AI agents with access to corporate databases can be tricked into exfiltrating data. Generative AI tools can produce convincing phishing emails at scale. The attack surface is expanding faster than most security teams can monitor.

Palo Alto's response has been to embed AI into its own security products. Cortex XSIAM uses machine learning to correlate security alerts, reducing the volume of incidents that human analysts need to review by over 90 percent, according to the company. Prisma Cloud now includes AI model scanning, which checks deployed machine learning models for known vulnerabilities and misconfigurations.

The irony is not lost on security professionals: AI is simultaneously the threat and the defence. Companies need AI-powered security tools to protect against AI-powered attacks. This creates what analysts call a "security arms race" — and companies like Palo Alto Networks, CrowdStrike, and Zscaler are positioned as the arms dealers.

## What NRI Investors Are Watching

For Indian diaspora investors, Palo Alto Networks occupies a distinctive position. It is the largest cybersecurity company in the world by market capitalisation, led by an Indian-origin CEO, with significant engineering operations in India. The company's Bengaluru office employs over 2,000 engineers working on core product development — not outsourced support, but primary R&D.

PANW stock is held widely by NRI investors both directly and through technology-focused ETFs. The Goldman Sachs note has focused attention on the broader cybersecurity sector, with CrowdStrike, Fortinet, and Zscaler also seeing buying interest. But it is Arora's company, with its platform breadth and AI integration story, that Goldman identified as the primary beneficiary of the coming spending cycle.

The cybersecurity market is projected to reach $300 billion globally by 2028. Nikesh Arora's task is to ensure that Palo Alto Networks captures an outsized share of that growth. If the Goldman analysts are right about the AI security inflection, the "watershed moment" may be as much about Arora's career as it is about the sector he leads.""",
    "category": "technology",
    "status": "review",
    "is_editorial": False,
    "vertical": "technology",
    "image_url": image_urls.get("nikesh-arora", IMAGE_SOURCES["nikesh-arora"]),
    "image_caption": "Nikesh Arora, CEO of Palo Alto Networks, at TechCrunch Disrupt 2015",
    "image_attribution": "Wikimedia Commons / TechCrunch (CC BY 2.0)",
    "sources": json.dumps([
        {"name": "Goldman Sachs Research", "url": "https://www.goldmansachs.com/insights/articles/cybersecurity-spending-inflection"},
        {"name": "CNBC", "url": "https://www.cnbc.com/2026/06/11/palo-alto-networks-cybersecurity-ai-watershed.html"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/palo-alto-networks-stock-goldman-sachs-cybersecurity"}
    ]),
    "diaspora_angle": "Indian-origin CEO Nikesh Arora (IIT Varanasi, ex-Google) leads the world's largest cybersecurity company by market cap; 2,000+ engineers in Bengaluru on core R&D; PANW widely held by NRI investors",
    "score_total": 78,
    "published_at": now_iso,
    "created_at": now_iso,
    "updated_at": now_iso,
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3 — Semiconductor Stocks Best Day in Over a Year
# ═══════════════════════════════════════════════════════════════════
articles.append({
    "id": str(uuid.uuid4()),
    "headline": "Chip Stocks Just Had Their Best Day in Over a Year — Here's What Drove the PHLX Index Up 8 Percent",
    "subheadline": "From Applied Materials to Intel to Micron, the semiconductor rally reflects an AI infrastructure buildout that shows no sign of slowing, with tens of thousands of Indian engineers at the centre of it",
    "slug": "semiconductor-stocks-phlx-rally-oracle-micron-ai-20260612",
    "body": """The Philadelphia Semiconductor Index surged approximately eight percent on Wednesday, its best single-day performance since April 2025. The rally swept across the entire chip sector: Applied Materials rose 11 percent, Lam Research gained 13 percent, Micron jumped 12 percent, Marvell climbed 11 percent, ARM added 11 percent, AMD gained 8 percent, Intel rose 9.3 percent, Qualcomm advanced 6 percent, and even NVIDIA — already the world's most valuable company — added 2.2 percent.

The catalyst was a convergence of earnings results and forward guidance that collectively painted a picture of AI infrastructure demand accelerating beyond what most analysts had modelled. The message from boardrooms across Silicon Valley, Boise, and Austin was consistent: the buildout is not slowing down, the order books are full, and the constraint is manufacturing capacity, not customer appetite.

## Oracle's $638 Billion Signal

The rally was sparked in part by Oracle's fiscal fourth-quarter results, released after Tuesday's close. Revenue grew 21 percent to $17.4 billion. Cloud infrastructure revenue surged 93 percent. But the number that moved markets was Oracle's remaining performance obligations — essentially its backlog of signed contracts — which hit $638 billion, an astonishing figure for a company that many investors still associate with legacy database software.

CEO Safra Catz announced capital expenditure guidance of $70 billion for fiscal year 2027, almost entirely directed at AI data centre infrastructure. Oracle is building GPU clusters for companies that cannot get enough capacity from Amazon Web Services, Microsoft Azure, or Google Cloud. The backlog suggests that enterprise AI demand is not a bubble but a sustained infrastructure cycle — the kind of multi-year buildout that the semiconductor industry has not seen since the smartphone revolution.

## Micron and the Memory Bottleneck

Micron Technology added fuel to the rally with its fiscal third-quarter results, reporting revenue guidance of approximately $35.5 billion and earnings per share of $19.15, both well above consensus estimates. CEO Sanjay Mehrotra — born in Kanpur, India, and a co-founder of SanDisk before leading Micron — described the AI memory market as supply-constrained through at least 2027.

The bottleneck is high-bandwidth memory, or HBM, the specialised DRAM chips stacked vertically and attached directly to AI accelerators. NVIDIA's next-generation Blackwell GPUs require HBM3E modules, and the demand for these components has outstripped Micron's, Samsung's, and SK Hynix's combined production capacity. Micron's HBM revenue tripled year-over-year, and the company has pre-sold its entire HBM production through mid-2027.

For investors, the memory cycle is significant because it tends to amplify semiconductor industry profits during upcycles. Unlike logic chips, which are custom-designed and priced through long-term contracts, memory chips are commodities whose prices swing with supply and demand. When AI demand pushes HBM prices higher, Micron's margins expand dramatically — and the stock follows.

## Intel's Surprising Rally

Intel's 9.3 percent single-day jump was notable for different reasons. The company has spent the past two years executing a painful turnaround under CEO Pat Gelsinger's successor, losing market share to AMD in data centre processors and to TSMC in manufacturing. But Intel's foundry division has begun to show signs of life: the company recently secured its first major external customer for its Intel 18A manufacturing process, and the CHIPS Act subsidies are flowing.

Intel's stock, which traded below $20 as recently as late 2025, closed at $116.96 — a recovery that reflects both improving fundamentals and the broader AI tide lifting all semiconductor boats. The company employs thousands of Indian engineers at its design centres in Bengaluru and Hyderabad, and its fortunes are closely watched by the Indian technology community.

## The Indian Engineering Backbone

What the PHLX rally obscures, beneath the ticker symbols and percentage gains, is the human infrastructure behind the semiconductor boom. Indian engineers constitute an estimated 20 to 25 percent of the US semiconductor workforce, concentrated in design, verification, and architecture roles. At Qualcomm, the Hyderabad and Bengaluru offices are among the company's largest. AMD's India design centre in Hyderabad handles critical work on EPYC server processors. Broadcom, Marvell, and Synopsys all maintain major Indian operations.

Sanjay Mehrotra at Micron is the most visible Indian-origin leader in the current rally, but the Indian presence extends deep into the engineering ranks at every company that moved the PHLX index on Wednesday. The chip industry's dependence on Indian talent is structural, not incidental — and it creates a direct financial link between the semiconductor cycle and the Indian diaspora's wealth.

NRI investors with portfolios tilted toward technology — through individual stocks or ETFs like the iShares Semiconductor ETF (SOXX) and VanEck Semiconductor ETF (SMH) — saw meaningful gains on Wednesday. The question is whether the rally represents a repricing of structural AI demand or a short-term surge that will fade. The Oracle backlog, the Micron supply constraints, and the hyperscaler capital expenditure guidance all point toward the former.

## What Comes Next

The semiconductor cycle is notoriously boom-and-bust. The last major downturn, in 2022-2023, wiped hundreds of billions of dollars from chip stocks. But the current cycle is different in one important respect: the demand driver is not consumer electronics, which is cyclical and discretionary, but enterprise AI infrastructure, which is being treated as capital expenditure essential to competitive survival.

Every major technology company — Google, Microsoft, Meta, Amazon, Apple, Oracle, and dozens of others — has committed to multi-year AI infrastructure buildouts. Their capital expenditure plans for 2026 and 2027 collectively exceed $400 billion. That money flows directly to semiconductor companies: NVIDIA for GPUs, Broadcom for custom ASICs, Micron for HBM, Applied Materials and Lam Research for the fabrication equipment that makes it all possible.

The PHLX index's eight percent day was not an anomaly. It was the market digesting the scale of what is being built and repricing the companies that build it accordingly. For the tens of thousands of Indian engineers who design, verify, and manufacture these chips, the rally is both financial and professional — a validation of the industry they have helped build over three decades.""",
    "category": "technology",
    "status": "review",
    "is_editorial": False,
    "vertical": "technology",
    "image_url": image_urls.get("semiconductor-rally", IMAGE_SOURCES["semiconductor-rally"]),
    "image_caption": "Stock market trading screens showing market data",
    "image_attribution": "Pexels / Pixabay",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/chip-stocks-best-day-2026-06-11"},
        {"name": "CNBC", "url": "https://www.cnbc.com/2026/06/11/semiconductor-stocks-rally-phlx-oracle-micron.html"},
        {"name": "Bloomberg", "url": "https://www.bloomberg.com/news/articles/2026-06-11/chip-stocks-surge-oracle-ai-backlog"}
    ]),
    "diaspora_angle": "Indian engineers comprise 20-25% of US semiconductor workforce; Sanjay Mehrotra (Kanpur-born) leads Micron through AI memory boom; NRI portfolios with SOXX/SMH ETFs directly benefiting from the rally",
    "score_total": 80,
    "published_at": now_iso,
    "created_at": now_iso,
    "updated_at": now_iso,
})

# ── Insert ──
url = f"{SUPABASE_URL}/rest/v1/p2_articles"
for a in articles:
    resp = requests.post(url, headers=HEADERS, json=a)
    if resp.status_code in (200, 201):
        row = resp.json()
        if isinstance(row, list):
            row = row[0]
        print(f"✓ Inserted: {row['slug']}  (id={row['id']})")
    else:
        print(f"✗ FAILED [{resp.status_code}]: {a['slug']}")
        print(f"  {resp.text[:300]}")

print(f"\nDone — {len(articles)} articles submitted at {now_iso}")
