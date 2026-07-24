#!/usr/bin/env python3
import json, os, uuid, re, requests, urllib.parse, subprocess
from datetime import datetime, timezone
from pathlib import Path

# ---- Load env ----
for envname in [".env.supabase"]:
    f = Path.home() / envname
    if f.exists():
        for line in f.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

PEXELS_KEY = None
pf = Path.home() / "workspace" / ".env.pexels"
if pf.exists():
    for line in pf.read_text().strip().splitlines():
        if "PEXELS_API_KEY" in line and "=" in line:
            PEXELS_KEY = line.split("=", 1)[1].strip()

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = "TheVideshi/1.0 (thevideshi.com)"

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

# ---- Image sourcing ----
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                         headers={"User-Agent": UA}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_pexels(query, per_page=8):
    if not PEXELS_KEY:
        return None
    try:
        out = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page={per_page}&orientation=landscape",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=30)
        data = json.loads(out.stdout)
        photos = data.get("photos", [])
        # prefer larger, landscape
        for p in photos:
            src = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
            if src:
                print(f"  ✓ Pexels image for '{query}': {src[:80]}")
                return src
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def verify_image(url):
    """GET (not HEAD) the image, check 200 + image/* + >5KB."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0") or "0")
        body = r.raw.read(20000) if cl == 0 else b""
        size_ok = cl > 5000 or len(body) > 5000
        if r.status_code == 200 and ct.startswith("image/") and size_ok:
            print(f"  ✓ verified image ({ct}, {cl or len(body)} bytes)")
            return True
        print(f"  ✗ image failed verify: status={r.status_code} ct={ct} cl={cl}")
    except Exception as e:
        print(f"  ⚠ verify error: {e}")
    return False

# ---- Build images ----
# 1. Nadella -> Wikipedia person
nadella_img = fetch_wikipedia_person_image("Satya Nadella")
if not nadella_img or not verify_image(nadella_img):
    nadella_img = fetch_pexels("microsoft headquarters building")
    verify_image(nadella_img)

# 2. Upscale AI -> data center networking (company/infra story, two founders, no dominant single face)
upscale_img = fetch_pexels("data center network server cables")
if not upscale_img or not verify_image(upscale_img):
    upscale_img = fetch_pexels("server room data center")
    verify_image(upscale_img)

# 3. InfoEdge -> Sanjeev Bikhchandani Wikipedia, fallback to venture/startup imagery
infoedge_img = fetch_wikipedia_person_image("Sanjeev Bikhchandani")
if not infoedge_img or not verify_image(infoedge_img):
    infoedge_img = fetch_pexels("startup founders meeting office")
    verify_image(infoedge_img)

print("\nFinal images:")
print(" nadella:", nadella_img)
print(" upscale:", upscale_img)
print(" infoedge:", infoedge_img)

# ---- Articles ----
nadella_body = """Satya Nadella has spent a decade as the steady elder statesman of the AI boom, the Microsoft chief executive whose billions helped turn OpenAI from a research lab into a colossus. Over the weekend he picked a very public fight with the very companies he helped build.

In an interview with *The Wall Street Journal*, Nadella warned that the AI industry risks repeating the worst mistakes of globalization — concentrating power in a handful of "frontier" model makers while hollowing out the industries and workers underneath them. "You can't say, hey, all white-collar jobs are gone and this could even be a weapon, and we will use all the power to build data centres," he said. The barb was aimed squarely at OpenAI and Anthropic, the two labs Microsoft has poured money into.

## The reset

The argument arrived alongside a product. Microsoft made Copilot Cowork — an autonomous agent that runs longer, multi-step tasks — generally available worldwide this week, and crucially made it model-agnostic. Users can pick cheaper models, not just the most powerful ones. Microsoft is reportedly even weighing whether to host a version of DeepSeek, the ultra-low-cost Chinese provider that OpenAI and Anthropic have accused of copying their models.

The self-interest is not hidden. Microsoft's distribution muscle — Office, Azure, Windows — is worth far more in a world where AI is a commodity that businesses mix and match than in one where a single lab owns the smartest model. The company has begun building its own in-house models to cut the per-query cost of running AI at scale. Nadella's framing — "build a frontier ecosystem, not just a frontier model" — is both a philosophy and a sales pitch.

Not everyone is convinced. Melius Research analyst Ben Reitzes publicly questioned the pivot, and Copilot's roughly 15 million paid subscribers remain a modest figure for a company of Microsoft's reach. AI software costs have climbed 20% to 37%, and enterprise customers have pushed back on pricing — the gap between Nadella's rhetoric about cheaper, broader AI and what his own products deliver is real.

## Why the diaspora should read the subtext

For the hundreds of thousands of Indian engineers inside Microsoft, Google, Amazon and the IT services giants, Nadella's warning is more than boardroom theory. The "white-collar jobs are gone" anxiety he is pushing back against describes their jobs most directly. When Anthropic's Dario Amodei predicts AI could wipe out half of entry-level white-collar work by 2029, the entry-level white-collar work he is describing is disproportionately done by young Indian coders — in Hyderabad and Bengaluru, and on H-1B visas in New Jersey and the Bay Area.

Nadella, born in Hyderabad, is effectively arguing that the industry has no "societal permission" to automate away those jobs while demanding unlimited capital. A model-agnostic, commodity-AI world is also, not coincidentally, one where the Indian IT outsourcing model — TCS, Infosys, Wipro, Cognizant — has more room to survive. If the smartest model is no longer a moat, the integration, services and customization layer where Indian firms and Indian engineers live becomes the value. That is the opposite of the "one lab to rule them all" future that has had India's $250 billion services industry running scared.

For NRI investors, the read is subtler. Microsoft's stock has sold off, and bulls are calling it a buying opportunity on the theory that distribution beats model supremacy over time. Bears counter that a model-agnostic Microsoft is admitting it can no longer win the model race outright. Both can be true at once.

## What's next

Watch three things. First, whether Microsoft actually hosts DeepSeek — that would be a genuine break, handing a Chinese model a vast new audience at OpenAI's and Anthropic's expense. Second, whether "model-agnostic" Copilot adoption finally moves the subscriber needle. Third, and most relevant to the diaspora, whether the rhetoric about protecting workers survives the next earnings cycle, when the pressure to show that AI is cutting costs — meaning headcount — returns with force.

Nadella has reframed the debate. Whether Microsoft's products, and its own workforce decisions, follow the framing is the test that matters."""

upscale_body = """The AI gold rush has minted a familiar set of winners: Nvidia, which sells the picks, and the labs that train ever-larger models. The quieter fortune is being made in the plumbing — and an Indian-American duo just raised $190 million to build it.

Santa Clara-based Upscale AI said this week it had closed a $190 million Series A-1 extension, lifting its valuation to $2 billion barely seven months after emerging from stealth. The round was led by Premji Invest, the investment arm of Wipro founder Azim Premji, and drew in Nvidia itself, Salesforce Ventures, Temasek and Tiger Global. Total funding now stands at $500 million.

## The bottleneck nobody photographs

Upscale does not make AI chips. It makes the networking fabric that connects them — the switches and silicon that move data between thousands of GPUs, memory pools and storage in a modern AI cluster. It is the least glamorous layer of the stack and, increasingly, the most important.

The reason is brutal arithmetic. An AI model's calculations run one after another. If a single data transfer between GPUs lags unexpectedly, every subsequent computation waits — leaving multimillion-dollar accelerators sitting idle. "Networking is one of the most critical bottlenecks," said chief executive Barun Kar. Upscale's answer is a custom chip it calls SkyHammer, built for "deterministic latency" — predictable data movement that avoids the stalls. It supports open standards such as UALink and Ultra Ethernet, positioning the startup as an open-architecture alternative to Cisco and Broadcom's proprietary gear.

## The Indian fingerprints

The founders' résumés read like a tour of Silicon Valley's Indian engineering diaspora. Kar is an alum of Palo Alto Networks, Juniper and Motorola. Executive chairman Rajiv Khemani previously founded Innovium, a data-center networking chip company that Marvell bought for about $1.1 billion — a track record that explains why investors who understand the unforgiving economics of switching silicon wrote checks so quickly. The two built Upscale inside Auradine, Khemani's earlier AI and blockchain infrastructure venture, before spinning it out.

That Premji Invest led the round — an Indian-rooted fund that has previously backed CrowdStrike and Sysdig — adds a neat symmetry. Indian capital and Indian-American operators, building the connective tissue of the American AI build-out.

## Why it matters to the diaspora

For NRI engineers, Upscale is a useful counter-narrative to the layoff headlines. While Oracle, Accenture and others trim workforces in the name of AI efficiency, the infrastructure layer is hiring hard, and the people designing the highest-end networking silicon are overwhelmingly veterans of exactly the kind of careers Indian engineers in the Valley have built. Hardware and systems roles — less exposed to the "AI will write the code" anxiety hanging over application software — are quietly becoming the safer harbor.

For NRI investors, the deal is a reminder that the most defensible AI bets may not be the model labs at all. Upscale sits in the same lane as Arista Networks, run by Indian-American CEO Jayshree Ullal, which has ridden AI data-center demand to a soaring valuation. The "sell the shovels" thesis that made Nvidia the most valuable company on earth extends down into the racks, and a cluster of Indian-led firms occupies that floor. Whether Upscale, still pre-revenue at scale, justifies a $2 billion price tag depends on landing the "neocloud" and hyperscale customers it is courting — a crowded, capital-hungry race against incumbents with decades of relationships.

## What's next

The company plans to use the cash to accelerate delivery of SkyHammer-based systems and chase deployments with large infrastructure providers. The open-standards bet is the wager to watch: if hyperscalers tire of being locked into proprietary networking, Upscale's interoperable fabric is well placed. If the giants hold their grip, even a $2 billion startup can be squeezed.

Either way, the lesson for diaspora professionals is the same one that has held through every Valley boom: when everyone is chasing the shiny object, the durable careers and the durable returns are often one layer down, in the infrastructure that makes the shiny object work."""

infoedge_body = """For most of its life, Info Edge was a story about consumer internet. The Delhi-based firm built Naukri, India's dominant job portal, and made its fortune as an early backer of Zomato and the insurance aggregator PB Fintech — bets that turned into multibillion-dollar public companies. This week, founder Sanjeev Bikhchandani's company quietly told shareholders that the next decade looks different.

In a letter filed with India's stock exchanges on 22 June, Info Edge carved out its artificial-intelligence and deeptech investments as a standalone book for the first time, disclosing that it has deployed ₹1,003 crore (about $120 million) across 54 startups in those sectors since 2020. Nearly half of all its startup investments over the past 12 months have gone into AI and deeptech — a sharp turn from the consumer-tech playbook that built the firm.

## The numbers behind the pivot

The split is telling. Info Edge has put ₹455 crore into 30 deeptech companies and ₹614 crore into 28 AI firms, running the money through Redstart Labs, the deeptech fund Capital 2B, and its Info Edge Ventures vehicles. The early scorecard is honest about the difference between the two. The AI portfolio shows a gross internal rate of return of roughly 31% and 2.1 times invested capital — respectable for a young book. The deeptech portfolio, still early in its cycle, sits at a 15% IRR and 1.2 times — the slow-burn nature of robotics, biotech and space tech laid bare.

"Both AI and deeptech are absolutely transformational in their ability to create new business models," said Chinmaya Sharma, a partner at Info Edge Ventures. "More importantly, they've become topics of strategic interest for the country." The portfolio names hint at the breadth of the bet: voice-AI platform Gnani.ai, skin-health startup Ahammune, electric air-taxi firm ePlane, Zomato founder Deepinder Goyal's air-mobility venture LAT Aerospace, and health-tracking company Temple.

## Part of a bigger shift

Info Edge's disclosure lands amid a flood of capital into Indian deeptech. This week alone, Bengaluru's SwishX was picked for Anthropic and AWS's first agentic-AI accelerator; Amazon committed another $13 billion to Indian data centers; and Santa Clara's Upscale AI, founded by Indian-American veterans and backed by Azim Premji's fund, raised at a $2 billion valuation. The smart money, Indian and global, is rotating from food delivery and fintech toward the harder, slower science.

## Why NRIs should care

For the Indian diaspora, Info Edge's pivot is a signal worth reading. Many NRIs hold Indian equities directly or through funds, and Info Edge is among the most-watched listed proxies for India's startup economy — owning a stake in it has long been a way to own a slice of Zomato and PB Fintech before they were household names. The firm is now effectively offering public-market investors early, diversified exposure to Indian AI and deeptech, sectors that are otherwise locked behind private rounds NRIs cannot easily access.

There is a return-to-India angle, too. The diaspora's most common professional anxiety — what happens to a mid-career engineer in the Bay Area as AI reshapes the job — increasingly has an Indian answer. The deeptech and AI ventures Info Edge is funding are precisely the kind of companies that recruit experienced operators from abroad, and the kind that make moving back a credible career move rather than a step down. A robotics or space-tech startup in Bengaluru with patient capital behind it is a very different proposition than the call-center-era image many NRIs still carry.

## What's next

The honesty about the deeptech scorecard — a 1.2x multiple after years of investing — is the part to respect. Deeptech is a decade game, not a quarterly one, and Info Edge is signalling it has the patience to wait. For diaspora investors, the takeaway is not to chase a single name but to note where India's savviest internet investor is now pointing its capital. When the firm that spotted Zomato early starts putting half its money into AI and deeptech, it is describing the next decade of where Indian technology — and Indian careers — are headed."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Microsoft Bankrolled the AI Giants. Now Satya Nadella Is Picking a Fight With Them.",
        "subheadline": "The Hyderabad-born CEO warns AI can't 'hollow out' white-collar work — the work his own Indian engineers do most — while a model-agnostic Copilot quietly reshapes the race.",
        "slug": make_slug("satya-nadella-ai-reset-warning-copilot-model-agnostic-openai-anthropic-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Nadella's warning against AI 'hollowing out' white-collar jobs lands directly on the young Indian engineers — in Hyderabad, Bengaluru and on H-1B visas in the US — whose entry-level coding roles are most exposed, and a commodity-AI world gives India's services giants room to survive.",
        "tags": ["ai", "microsoft", "satya-nadella", "indian-tech", "h1b", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com/tech/ai/microsofts-satya-nadella-we-cant-let-ai-giants-eat-the-economy"},
            {"name": "TheStreet", "url": "https://www.thestreet.com/technology/microsofts-ceo-sends-the-ai-industry-a-strong-warning"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/nadellas-warning-why-microsoft-now-fights-the-ai-giants-it-helped-create/"},
            {"name": "Stocktwits", "url": "https://stocktwits.com/news-articles/markets/equity/melius-researchs-ben-reitzes-slams-satya-nadella"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": nadella_img,
        "image_caption": "Microsoft CEO Satya Nadella, who has called for an AI 'reset' away from a few dominant model makers.",
        "image_attribution": "Wikimedia Commons" if (nadella_img and "wikipedia" in nadella_img or (nadella_img and "wikimedia" in nadella_img)) else "Pexels",
        "is_editorial": False,
        "body": nadella_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Everyone's Chasing AI Chips. An Indian-American Duo Just Raised $190 Million Building the Wires Between Them.",
        "subheadline": "Upscale AI hit a $2 billion valuation with Nvidia and Azim Premji's fund backing it — and its founders' résumés read like a tour of Silicon Valley's Indian engineering diaspora.",
        "slug": make_slug("upscale-ai-190-million-2-billion-networking-barun-kar-khemani-premji-nvidia-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "While layoff headlines hit Indian software engineers, the AI infrastructure layer — led by diaspora veterans like Upscale's Barun Kar and Rajiv Khemani and Arista's Jayshree Ullal — is hiring and offers NRI engineers and investors a more defensible bet than the model labs.",
        "tags": ["ai", "semiconductors", "indian-tech", "venture-capital", "silicon-valley", "data-center"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/upscale-ai-valued-2-billion-after-funding-extension-2026-06-22/"},
            {"name": "Data Center Dynamics", "url": "https://www.datacenterdynamics.com/en/news/nvidia-backs-ai-networking-switch-silicon-startup-upscale-in-190m-raise/"},
            {"name": "SiliconANGLE", "url": "https://siliconangle.com/2026/06/22/ai-networking-provider-upscale-ai-raises-190m-2b-valuation/"},
            {"name": "Ventureburn", "url": "https://ventureburn.com/2026/06/upscale-ai-raises-190m-for-ai-networking-expansion/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": upscale_img,
        "image_caption": "Networking cables linking servers inside a data center — the bottleneck Upscale AI's silicon aims to solve.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": upscale_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Firm That Spotted Zomato Early Just Put Half Its Money Into AI and Deeptech",
        "subheadline": "Info Edge has quietly poured ₹1,003 crore into 54 AI and deeptech startups — and for NRI investors it's a rare public-market window into India's next tech decade.",
        "slug": make_slug("info-edge-ai-deeptech-1003-crore-54-startups-bikhchandani-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Info Edge is among the most-watched listed proxies for India's startup economy, giving NRI investors early, diversified exposure to AI and deeptech they otherwise can't reach — and the ventures it funds are exactly the kind that make a return-to-India career move credible.",
        "tags": ["ai", "deeptech", "indian-startups", "venture-capital", "investing", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/info-edge-ai-deeptech-bets-early-scorecard"},
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/deeptech-ai-cornered-half-of-infoedges-startup-bets-in-the-last-12-months"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indiamart-doubles-down-ai-curb-fake-listings-2026-06-25/"}
        ]),
        "score_total": 71,
        "status": "review",
        "published_at": now,
        "image_url": infoedge_img,
        "image_caption": "Info Edge founder Sanjeev Bikhchandani, whose firm is rotating capital from consumer tech to AI and deeptech." if (infoedge_img and ("wikipedia" in infoedge_img or "wikimedia" in infoedge_img)) else "Startup founders at work — Info Edge is backing 54 AI and deeptech ventures across India.",
        "image_attribution": "Wikimedia Commons" if (infoedge_img and ("wikipedia" in infoedge_img or "wikimedia" in infoedge_img)) else "Pexels",
        "is_editorial": False,
        "body": infoedge_body
    }
]

# word count sanity
for a in articles:
    wc = len(a["body"].split())
    print(f"  [{wc} words] {a['headline'][:60]}")

print("\nInserting...")
for art in articles:
    if not art["image_url"]:
        print(f"⚠ no image for {art['slug']} — skipping image, inserting anyway")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
