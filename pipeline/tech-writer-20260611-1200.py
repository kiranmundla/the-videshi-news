#!/usr/bin/env python3
"""
Technology writer for The Videshi — June 11, 2026
3 articles:
1. TCS ends mass hiring, expects AI agents to match employee headcount
2. Jensen Huang declines US Senate hearing on AI chip exports
3. NVIDIA RTX Spark reinvents the personal computer
"""

import os, json, time, uuid, requests, urllib.parse, subprocess
from datetime import datetime, timezone
from io import BytesIO

# ── env ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.replace('export ', '').strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ.get('SUPABASE_URL', '')
SB_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

def sb_headers():
    return {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

# ── image sourcing ──────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                w = ii.get("width", 0)
                if w < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": w,
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        cmd = [
            'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
            f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{query}': {url[:60]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def download_and_compress(url, max_width=1200, quality=80):
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed: HTTP {r.status_code}")
            return None
        ct = r.headers.get('Content-Type', '')
        if 'image' not in ct and len(r.content) < 5000:
            print(f"  ⚠ Not a valid image (Content-Type: {ct}, size: {len(r.content)})")
            return None
        from PIL import Image
        img = Image.open(BytesIO(r.content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True)
        data = buf.getvalue()
        size_kb = len(data) / 1024
        print(f"  ✓ Compressed: {img.width}x{img.height}, {size_kb:.0f} KB")
        if len(data) < 5000:
            print(f"  ⚠ Too small after compression ({len(data)} bytes), skipping")
            return None
        return data
    except Exception as e:
        print(f"  ⚠ Download/compress error: {e}")
        return None

def upload_to_supabase(img_bytes, filename):
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    try:
        r = requests.post(url, data=img_bytes, headers=headers, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:70]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

def source_image(person_name=None, topic_queries=None, pexels_query=None, slug="article"):
    candidates = []
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": 3})
    if topic_queries:
        for q in topic_queries[:3]:
            commons = fetch_wikimedia_commons_images(q)
            for c in commons[:2]:
                candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": 2})
            time.sleep(0.5)
    if pexels_query:
        pex = fetch_pexels_image(pexels_query)
        if pex:
            candidates.append({"url": pex, "source": "pexels", "relevance": 1})

    candidates.sort(key=lambda x: x["relevance"], reverse=True)
    for c in candidates:
        print(f"  Trying {c['source']}: {c['url'][:70]}...")
        img_bytes = download_and_compress(c["url"])
        if img_bytes:
            filename = f"{slug}.jpg"
            sb_url = upload_to_supabase(img_bytes, filename)
            if sb_url:
                attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return sb_url, attr
        time.sleep(1)

    print("  ✗ No image found from any source")
    return None, None

def insert_article(article):
    url = f"{SB_URL}/rest/v1/p2_articles"
    r = requests.post(url, json=article, headers=sb_headers(), timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id')
        print(f"  ✓ Inserted article: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1: TCS Ends Mass Hiring — AI Agents to Match Headcount
# ═══════════════════════════════════════════════════════════════════
def write_tcs_ai_agents():
    print("\n═══ Article 1: TCS Ends Mass Hiring / AI Agents ═══")
    slug = "tcs-ends-mass-hiring-ai-agents-match-headcount-20260611"

    print("  Sourcing image...")
    img_url, img_attr = source_image(
        person_name="N. Chandrasekaran",
        topic_queries=["Tata Consultancy Services headquarters", "TCS Mumbai"],
        pexels_query="Indian technology office corporate",
        slug=slug
    )

    headline = "TCS Will Stop Hiring En Masse. Half a Million AI Agents Will Pick Up the Slack."
    subheadline = "Tata Consultancy Services chairman N. Chandrasekaran told shareholders that within three years, TCS expects as many AI agents working alongside employees as there are employees themselves — and the era of hiring tens of thousands of graduates in a single quarter is over."

    body = """At the annual general meeting of Tata Consultancy Services on June 9, chairman N. Chandrasekaran made a statement that would have been unthinkable five years ago: TCS, India's largest IT services company and the country's biggest private-sector employer, will no longer hire at the scale that defined it for three decades.

"We used to go and hire 30,000, 40,000 people in one quarter," Chandrasekaran said. "We will not do that going forward."

What TCS will do instead is deploy AI agents — software systems that can handle tasks previously done by human employees — at a scale that matches its workforce. The company currently employs roughly half a million people worldwide. Within three years, Chandrasekaran expects an equivalent number of AI agents operating alongside them.

## The Numbers Behind the Shift

The shift isn't prospective. It is already well underway. TCS cut approximately 12,000 jobs last July. Net headcount fell by more than 23,000 in FY2026. In the same period, AI-related revenue reached an annualised run rate of $2.4 to $2.5 billion, growing at a compounded quarterly growth rate of 22.4 percent. The maths is blunt: revenue from AI is rising faster than the headcount it is replacing is falling.

TCS shares have dropped roughly 32 percent year-to-date in 2026, reflecting investor anxiety about how quickly AI will cannibalise the traditional labour-arbitrage model that made Indian IT a $315 billion industry. But the stock decline also reflects something more fundamental — the market doesn't yet know how to price an IT services company that employs as many machines as people.

Two days after the AGM, on June 11, TCS announced a strategic partnership with Anthropic to equip 50,000 associates with Claude, Anthropic's AI assistant. The deal — which covers consulting, engineering, and operations staff — is a concrete down payment on Chandrasekaran's vision. TCS employees will use Claude to write code, analyse data, and handle client work that once required junior engineers billing hours.

## What This Means for the H-1B Pipeline

For Indian professionals in the United States, the implications cut deep. TCS has historically been one of the largest sponsors of H-1B visas. The company's hiring pipeline worked like a conveyor belt: recruit from Indian engineering colleges, train on proprietary platforms, deploy to client sites in the US on project-based visas. That pipeline created the template for an entire generation of Indian immigration to America.

If TCS stops hiring 30,000 to 40,000 people per quarter, the downstream effects on visa sponsorship are significant. Fewer entry-level hires in India means fewer bodies to deploy abroad. The H-1B system doesn't collapse — demand for senior, specialised engineers remains strong — but the volume-based model that sent thousands of Indian IT workers to American offices every year is contracting.

This matters beyond TCS. Infosys, Wipro, HCLTech, and Tech Mahindra are all moving in the same direction, though none has stated the shift as explicitly as Chandrasekaran. The broader Indian IT industry employed roughly 5.4 million people as of early 2026. If even a fraction of those jobs are displaced by AI agents, the knock-on effects on Indian immigration patterns, remittance flows, and the domestic economy will be substantial.

## The Investor Problem

NRI investors who hold TCS stock — and there are a great many of them, given that TCS is one of the most widely held Indian equities among the diaspora — face a valuation puzzle. The traditional bull case for Indian IT was straightforward: a large, English-speaking workforce that could deliver software services at a fraction of Western costs. AI agents undermine that thesis by making the cost of the workforce less relevant. If a machine can do what a junior developer does, the advantage of hiring that developer in Pune instead of Portland disappears.

Chandrasekaran is betting that TCS can pivot from selling labour to selling AI-augmented outcomes — a fundamentally different product. The Anthropic partnership is part of that bet. So is the $2.5 billion AI revenue run rate. But the transition requires TCS to cannibalise its own business model before competitors or clients do it for them.

"Every company, every business has to consider whether they need a hundred people or can manage with ten," Chandrasekaran told shareholders. That sentence applies to TCS's own clients, who may decide they need fewer TCS consultants, not more. It also applies to TCS itself.

## The Bigger Picture

India's IT industry was built on a simple insight: talented Indian engineers could do the same work as their Western counterparts for a fraction of the price. That insight powered $315 billion in annual revenue, millions of jobs, and the largest wave of skilled immigration in modern history. Chandrasekaran's announcement doesn't repudiate that achievement. It acknowledges that the era it defined is ending.

The question for every Indian professional — in India and abroad — is whether the next era creates as many opportunities as the last one. Chandrasekaran's own framing suggests it will create different ones: fewer positions, higher-skilled, working alongside AI rather than being replaced by it. Whether that's optimism or corporate euphemism, only the next three years will tell."""

    image_caption = "N. Chandrasekaran, chairman of Tata Sons and TCS, announced the company will stop mass hiring and deploy AI agents at scale"
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "https://www.reuters.com/technology/tcs-deploy-ai-agents-equal-half-million-workforce-2026-06-09",
            "https://www.thehindubusinessline.com/info-tech/tcs-chandrasekaran-agm-ai-agents-2026/article69655432.ece",
            "https://www.outlookbusiness.com/enterprise/tcs-mass-hiring-ends-chandrasekaran-agm"
        ]),
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr,
        "is_editorial": False,
        "tags": ["TCS", "AI agents", "N Chandrasekaran", "Indian IT", "H-1B", "Anthropic", "hiring"],
        "score_total": 78
    }
    return insert_article(article)


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2: Jensen Huang Declines Senate Hearing on AI Chip Exports
# ═══════════════════════════════════════════════════════════════════
def write_huang_senate():
    print("\n═══ Article 2: Jensen Huang Declines Senate Hearing ═══")
    slug = "jensen-huang-declines-senate-hearing-ai-chip-exports-china-20260611"

    print("  Sourcing image...")
    img_url, img_attr = source_image(
        person_name="Jensen Huang",
        topic_queries=["NVIDIA headquarters Santa Clara", "US Senate Banking Committee hearing"],
        pexels_query="semiconductor chip technology",
        slug=slug
    )

    headline = "Jensen Huang Won't Testify Before the Senate. Elizabeth Warren Isn't Letting It Go."
    subheadline = "The NVIDIA CEO declined an invitation to appear before the Senate Banking Committee on AI and export controls — and the senator who invited him made sure everyone noticed."

    body = """Jensen Huang, the chief executive of the most valuable company on Earth, has declined to testify before the United States Senate. The invitation came from Senator Elizabeth Warren, who chairs the Senate Banking Committee, for a hearing scheduled on June 11 titled "AI and the American Dream: Promoting Innovation, Affordability, and American Dominance."

Huang offered to host lawmakers at NVIDIA's headquarters in Santa Clara instead. Warren declined the counter-offer and made her displeasure public.

"If Mr. Huang has time to attend a $1 million-a-head dinner at Mar-a-Lago and fly across the world to meet with President Xi Jinping," Warren said in a statement, "he should be able to find time to answer questions from the American people's elected representatives."

## The Stakes

This is not a routine scheduling conflict. NVIDIA's market capitalisation now exceeds $3.5 trillion. Its chips power the vast majority of AI training and inference workloads globally. The company reported revenue of $44.1 billion in Q1 of fiscal year 2027, a figure that would have been inconceivable three years ago. And at the heart of Warren's hearing is a question that has consumed Washington for the past two years: whether American AI chips are finding their way to China despite export controls, and whether NVIDIA has done enough to prevent it.

The Commerce Department has been progressively tightening restrictions on AI chip exports to China since October 2022. Each round of controls has been followed by reports of workarounds — chips re-routed through third countries, custom designs that fall just below restricted performance thresholds, and a growing Chinese effort to build domestic alternatives. China is reportedly planning a $295 billion data centre buildout using domestically produced chips, a direct response to American restrictions.

NVIDIA occupies an awkward position in this debate. The company has complied with every export regulation, developing China-specific chips like the H20 that operate within the permitted performance envelope. But compliance hasn't satisfied critics who argue that any sale of advanced computing hardware to China accelerates its military and surveillance capabilities. Nor has it satisfied investors, who see China restrictions as a cap on NVIDIA's addressable market.

## The Warren Factor

Warren has a history of going after technology executives who decline Congressional invitations. Her committee has subpoena power, and while subpoenaing the CEO of America's most valuable company would be politically fraught, the threat adds weight to the invitation. More practically, Warren's public rebuke ensures that Huang's absence is the story, not whatever testimony the hearing produces from other witnesses.

The hearing proceeded without Huang. Other witnesses addressed topics ranging from AI's impact on employment to the competitive dynamics between American and Chinese AI development. But the empty chair — metaphorical though it was — drew more attention than any prepared statement.

## What This Means for the Diaspora

NVIDIA employs thousands of Indian-origin engineers at its Santa Clara headquarters and across its global operations. The company's senior leadership includes several Indian Americans, and its stock is among the most widely held by NRI investors, particularly those in the technology sector. Any regulatory action that constrains NVIDIA's business — tighter export controls, new compliance requirements, or Congressional pressure on pricing — has a direct impact on diaspora wealth and employment.

More broadly, the semiconductor export control debate intersects with India's own chip ambitions. The Indian government has committed over $10 billion to building a domestic semiconductor ecosystem, with fabrication plants planned in Gujarat and Assam. India's strategy depends partly on partnerships with American chipmakers — and those partnerships exist within the regulatory framework that Warren's committee is scrutinising. Tighter controls on China could, paradoxically, benefit India by redirecting investment toward friendly nations. Or they could create a compliance environment so restrictive that companies avoid any non-Western supply chain.

Indian Americans working at the intersection of chip design and trade policy — and there are quite a few — are watching this hearing not as spectators but as stakeholders. The rules that emerge from these debates will shape which companies they can work for, which markets their products can reach, and which countries their employers invest in.

## The Broader Pattern

Huang's decision to skip the hearing fits a pattern among technology leaders who prefer to engage Congress on their own terms. Tim Cook, Mark Zuckerberg, and Sundar Pichai have all testified before Congress, sometimes voluntarily and sometimes not. But those appearances typically came after public pressure made avoidance more costly than attendance.

NVIDIA is not yet at that tipping point. The company's financial performance is so extraordinary — revenue nearly tripling year over year — that shareholders are unlikely to punish Huang for dodging a single hearing. But Washington's interest in AI governance is only increasing, and the questions Warren wants to ask aren't going away.

Huang may eventually find that a trip to Capitol Hill is less disruptive than the alternative: a subpoena, a hostile regulatory environment, or a public narrative that NVIDIA's CEO is too important to answer questions about how his chips are used."""

    image_caption = "NVIDIA CEO Jensen Huang, who declined Senator Warren's invitation to testify before the Senate Banking Committee on AI chip exports"
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "https://www.peoplematters.in/news/technology/nvidia-ceo-declines-senate-ai-hearing-warren-criticizes-44321",
            "https://www.ainvest.com/news/nvidia-ceo-jensen-huang-declines-senate-hearing-2026",
            "https://barchart.com/story/news/nvidia-jensen-huang-senate-banking-committee-2026"
        ]),
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr,
        "is_editorial": False,
        "tags": json.dumps(["Jensen Huang", "NVIDIA", "Senate", "Elizabeth Warren", "AI chips", "China", "export controls", "semiconductors"]),
        "score_total": 82
    }
    return insert_article(article)


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3: NVIDIA RTX Spark — The AI PC Reborn
# ═══════════════════════════════════════════════════════════════════
def write_rtx_spark():
    print("\n═══ Article 3: NVIDIA RTX Spark AI PC ═══")
    slug = "nvidia-rtx-spark-ai-pc-arm-blackwell-mediatek-20260611"

    print("  Sourcing image...")
    img_url, img_attr = source_image(
        topic_queries=["NVIDIA Blackwell GPU", "NVIDIA RTX graphics card", "NVIDIA Computex"],
        pexels_query="gaming computer PC hardware technology",
        slug=slug
    )

    headline = "NVIDIA Wants to Replace Your Entire PC With a Chip the Size of a Playing Card"
    subheadline = "The RTX Spark is NVIDIA's first desktop system-on-chip: an ARM-based Blackwell GPU with 128 GB of unified memory that delivers one petaflop of AI compute in a box smaller than a Mac Mini. It arrives in autumn 2026 with partners including ASUS, Dell, HP, Lenovo, and Microsoft."

    body = """For thirty years, a personal computer has meant the same basic architecture: a CPU from Intel or AMD, a discrete GPU for heavy lifting, separate sticks of RAM, and a motherboard to tie it all together. NVIDIA's RTX Spark, announced at Computex 2026, proposes to end that arrangement.

The RTX Spark is a system-on-chip — a single piece of silicon, built in partnership with MediaTek, that integrates a 20-core ARM-based Grace CPU and a Blackwell-generation GPU. It shares 128 GB of unified LPDDR5X memory between the CPU and GPU. It delivers what NVIDIA claims is one petaflop of AI compute. And it fits in a desktop enclosure roughly the size of Apple's Mac Mini.

That last detail matters more than the spec sheet. NVIDIA has never sold a consumer desktop platform before. The RTX Spark is not a graphics card you slot into someone else's machine. It is the machine.

## What Makes It Different

The unified memory architecture is the crucial technical decision. Traditional PCs divide memory between the CPU and GPU, with a bus connecting the two. That bus is a bottleneck. Large AI models — the kind that software developers, designers, and researchers increasingly need to run locally — require more memory than most discrete GPUs offer. An RTX 4090 has 24 GB of VRAM. A Mac Studio with M4 Ultra offers 192 GB of unified memory. The RTX Spark, at 128 GB unified, sits between those two reference points but adds raw GPU throughput that Apple's chips cannot match.

NVIDIA is pitching this at what it calls "AI-native" workloads: running large language models locally, training small models on personal data, rendering with AI denoising, and developing AI applications. The one-petaflop figure translates to the ability to run models with tens of billions of parameters on a single desktop, without needing a cloud connection or a workstation that costs five figures.

The ARM CPU is the other notable choice. NVIDIA has used its Grace CPU in data centres since 2023, but bringing ARM to the consumer desktop breaks the Intel-AMD duopoly that has defined PC computing since the 1980s. Microsoft is a listed RTX Spark partner, which suggests that Windows on ARM — historically a mixed experience — will receive first-class NVIDIA driver support for the first time.

## The Partners

NVIDIA announced six hardware partners for RTX Spark systems: ASUS, Dell, HP, Lenovo, Microsoft, and MSI. These are not reference designs or developer kits. They are consumer products scheduled for autumn 2026, with price points that NVIDIA has not yet disclosed.

The partner list signals intent. Dell and HP sell to enterprises. ASUS and MSI sell to enthusiasts and gamers. Lenovo covers both. Microsoft's presence — presumably with a Surface-branded variant — suggests that Redmond sees RTX Spark as a serious platform, not an experiment.

MediaTek's involvement is equally significant. The Taiwanese chipmaker has been gaining ground in smartphone and tablet SoCs but has never had a presence in desktop computing. Co-designing an ARM chip with NVIDIA's Blackwell GPU IP gives MediaTek a foothold in a market it has never addressed, and gives NVIDIA a manufacturing partner with deep experience in power-efficient ARM designs.

## Why the Diaspora Should Pay Attention

Three reasons.

First, Indian software engineers — in the Bay Area, in Hyderabad, in Bengaluru — are among the most likely early adopters. Running AI models locally is increasingly table stakes for the kind of development work that Indian tech professionals do. The ability to fine-tune a model on a 128 GB machine at your desk, without paying for cloud GPU time, changes the economics of AI development. NVIDIA is explicitly targeting this audience.

Second, NRI investors have made NVIDIA one of the most widely held stocks in diaspora portfolios. The company's market capitalisation now exceeds $3.5 trillion. Every new product category NVIDIA enters — and the consumer desktop is a genuinely new category — is either a revenue growth story or a distraction. The RTX Spark represents NVIDIA's bet that AI compute will move from the cloud to the edge, from data centres to desktops. If that bet is right, it opens a consumer market that NVIDIA has never directly addressed.

Third, India's own technology ecosystem stands to benefit. MediaTek already has significant engineering operations in India. NVIDIA has been expanding its Indian footprint. If ARM-based desktops become mainstream, Indian hardware and software companies gain a new platform to build for — and Indian engineers gain a new architecture to master.

## The Competition

Apple's Mac Studio is the obvious comparison. It offers more unified memory (up to 192 GB), a mature software ecosystem, and Apple's integrated design philosophy. But it lacks the raw GPU compute that NVIDIA's Blackwell architecture provides. For AI workloads specifically, the RTX Spark should offer significantly better performance per dollar — though Apple's advantage in battery efficiency is irrelevant for a desktop.

Intel and AMD are not standing still. Both are developing AI-focused consumer chips, and both have ARM-based designs in various stages of development. But neither has announced anything as integrated or as ambitious as the RTX Spark. NVIDIA's advantage is that it controls the GPU architecture, the CUDA software ecosystem, and now the CPU design — a vertical integration that neither Intel nor AMD can currently match in the AI-native space.

## What Comes Next

NVIDIA has not announced pricing. That is the variable that will determine whether the RTX Spark is a mainstream product or a niche workstation. If it lands in the $1,500 to $2,500 range, it competes directly with gaming PCs and Apple's Mac lineup. If it lands above $3,000, it becomes a professional tool. The autumn 2026 launch window gives NVIDIA six months to finalise pricing and build supply — and gives competitors six months to respond."""

    image_caption = "NVIDIA's new RTX Spark platform combines an ARM-based Grace CPU and Blackwell GPU into a single desktop system-on-chip"
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "https://www.gizbot.com/news/nvidia-rtx-spark-desktop-soc-computex-2026",
            "https://www.geeky-gadgets.com/nvidia-rtx-spark-arm-blackwell-desktop",
            "https://www.communicationstoday.co.in/nvidia-rtx-spark-mediatek-arm-desktop-ai-pc"
        ]),
        "image_url": img_url,
        "image_caption": image_caption,
        "image_attribution": img_attr,
        "is_editorial": False,
        "tags": ["NVIDIA", "RTX Spark", "AI PC", "ARM", "Blackwell", "MediaTek", "Computex", "desktop computing"],
        "score_total": 75
    }
    return insert_article(article)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — Technology Writer — June 11, 2026")
    print("=" * 60)

    results = {}
    results["tcs_ai_agents"] = write_tcs_ai_agents()
    results["huang_senate"] = write_huang_senate()
    results["rtx_spark"] = write_rtx_spark()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, art_id in results.items():
        status = f"✓ {art_id}" if art_id else "✗ FAILED"
        print(f"  {name}: {status}")

    success = sum(1 for v in results.values() if v)
    print(f"\n{success}/{len(results)} articles inserted successfully")
