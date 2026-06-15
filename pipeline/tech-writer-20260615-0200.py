#!/usr/bin/env python3
import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ---------- Env ----------
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

pex_file = Path.home() / "workspace" / ".env.pexels"
PEXELS_KEY = ""
if pex_file.exists():
    for line in pex_file.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() == "PEXELS_API_KEY":
                PEXELS_KEY = v.strip()

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

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

# ---------- Image sourcing ----------
def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params, headers=UA, timeout=20)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for _, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 600:
                    continue
                results.append({"url": ii.get("thumburl") or ii.get("url", ""),
                                "title": page.get("title", ""), "width": ii.get("width", 0)})
            return results
    except Exception as e:
        print(f"  ! Commons error: {e}")
    return []

def fetch_pexels(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=5&orientation=landscape",
                         headers={"Authorization": PEXELS_KEY}, timeout=20)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                return photos[0]["src"]["large2x"] + ""  # large2x ~1880px
    except Exception as e:
        print(f"  ! Pexels error: {e}")
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

def upload_to_supabase(img_url, filename):
    try:
        r = requests.get(img_url, headers=UA, timeout=30)
        if r.status_code != 200 or not r.headers.get("Content-Type", "").startswith("image"):
            print(f"  ! download failed {r.status_code} for {img_url[:70]}")
            return None
        raw = r.content
        if len(raw) < 5000:
            print(f"  ! image too small ({len(raw)} bytes)")
            return None
        comp = compress_image(raw)
        up = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{filename}",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                     "Content-Type": "image/jpeg", "x-upsert": "true"},
            data=comp, timeout=40)
        if up.status_code in (200, 201):
            print(f"  ✓ uploaded {filename} ({len(comp)//1024} KB)")
            return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ! upload failed {up.status_code}: {up.text[:120]}")
    except Exception as e:
        print(f"  ! upload exception: {e}")
    return None

def source_image(slug, commons_queries, pexels_queries):
    candidates = []
    for q in commons_queries:
        for r in fetch_wikimedia_commons_images(q)[:3]:
            candidates.append(("commons", r["url"]))
        if candidates:
            break
    for q in pexels_queries:
        p = fetch_pexels(q)
        if p:
            candidates.append(("pexels", p))
            break
    for source, url in candidates:
        final = upload_to_supabase(url, f"{slug}.jpg")
        if final:
            attribution = "Wikimedia Commons" if source == "commons" else "Pexels"
            return final, attribution
    return None, None

# ---------- Articles ----------
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Tech Back Office Is Now the Brain. Its Workforce Is About to Cross 2.36 Million.",
        "subheadline": "A US cybersecurity firm just opened a Bengaluru capability center and pledged to grow it 50% in six months. The reason was not cost — it was talent the company could not find anywhere else.",
        "slug": make_slug("india-gcc-boom-2-36-million-nable-bengaluru-capability"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs weighing a return to India, the global capability center boom now offers headquarters-grade work — product, R&D, and AI engineering — at home rather than a back-office demotion.",
        "tags": ["india-tech", "gcc", "bengaluru", "ai", "jobs", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — N-able opens India GCC", "url": "https://www.reuters.com/technology/"},
            {"name": "Reuters — India's GCC model shifts from cost to capability", "url": "https://www.reuters.com/world/india/"},
            {"name": "Nasscom-Zinnov GCC report 2026", "url": "https://nasscom.in/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_caption": "A technology park in Bengaluru, the hub of India's global capability center boom",
        "_commons_q": ["Bagmane Tech Park Bangalore", "Manyata Tech Park Bangalore", "Bengaluru IT park building"],
        "_pexels_q": ["modern glass office tower Bangalore", "corporate office building India"],
        "body": """When a mid-sized American cybersecurity company decides where to plant its next engineering center, the choice usually comes down to a spreadsheet. N-able, which sells IT-management and data-protection software to more than 500,000 organizations, did the math and landed in Bengaluru. But its chief executive was unusually blunt about what the math actually said.

"The reason we're in Bengaluru is capability," John Pagliuca told Reuters as the firm opened its Global Capability Center on Monday. "Our priority is to build for the long term, with the right people and a strong foundation, not to pursue a short-term headcount play." The center already employs more than 100 people. Pagliuca says he wants it at least 50% larger by the end of the year.

That sentence — capability, not cost — is the whole story of where India's technology economy has arrived, and it matters a great deal to Indians abroad.

## The number that keeps climbing

India's global capability centers — the in-house offshore arms of multinationals, as distinct from outsourcing vendors like TCS or Infosys — are on track to employ **2.36 million people by the end of 2026**, according to a report from the industry body Nasscom and the consultancy Zinnov. There are now more than 2,100 such centers, generating close to $100 billion in revenue. India is, by a wide margin, the largest GCC hub on earth.

What has changed is not the size but the nature of the work. For two decades the pitch was simple: skilled people at scale, cheap. Executives at a recent Reuters summit in Bengaluru described a different model. GCCs are no longer back-office support units; they are integrated hubs that mirror their parent companies, running everything from product development to R&D to corporate strategy. At Target, the Bengaluru operation is described internally as an "integrated headquarters." IBM calls its India operation a "macrocosm" of the whole enterprise. In some cases, work once anchored at headquarters is now owned and executed end-to-end from India.

Microsoft's India head, Puneet Chandok, put the country's edge plainly: a talent pool of 27 million developers on GitHub, the world's deepest digital public infrastructure, and a policy environment that lets firms scale fast.

## Why an NRI should read this twice

For the Indian professional in the Bay Area or New Jersey, the GCC boom rewrites an old assumption. Going back to India used to mean trading frontier work for a quieter, lower-stakes role. Increasingly, it does not. The hardest skills to hire for in these centers — AI engineering, applied machine learning, cloud security, threat research — are exactly the skills minted in American big tech. A senior engineer in Seattle now has a credible option to do comparable, sometimes identical, work in Bengaluru, Hyderabad, or Pune, often leading global programs rather than supporting them.

That option is becoming more attractive precisely as the American side wobbles. US tech layoffs hit a near two-year high in May, and AI is now the leading reason companies give for cutting jobs. For an H-1B holder watching colleagues get pink slips, a senior role at a GCC is no longer a step down — it is increasingly a step sideways with a green-card-free path and family nearby.

## The strain underneath the boom

The model is not frictionless. Bengaluru, where most centers cluster, is choking on congestion and rising costs, and the competition for AI and cybersecurity talent is brutal — multinationals, domestic firms, and now newcomers like N-able all chasing the same shortlist. That is why states are scrambling to peel work away from the metros: Maharashtra, Karnataka, and Telangana have rolled out fresh GCC incentives, and Kerala just signed a partnership to court mid-market multinationals to its tech parks. Pune is positioning itself as the spillover destination of choice.

The talent crunch is also a wage story. As GCCs move up the value chain and compete for the same engineers as Google and Microsoft, the cost advantage that built the industry is narrowing. That is the quiet tension in Pagliuca's "capability, not cost" line — the cost gap is shrinking, so capability is the only durable reason to be there.

For the diaspora, the takeaway is clarity. The work in India is getting more serious, the pay is rising toward global benchmarks, and the demand is concentrated in exactly the AI and security skills that Indian engineers abroad already have. The back office became the brain while no one was looking. The next question for a lot of NRIs is whether the brain wants to come home."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Bay Area Tech Layoffs Hit 9,284 — Already Worse Than All of Last Year. For H-1B Workers, the Clock Starts Ticking.",
        "subheadline": "Fresh WARN filings push 2026's regional job cuts past the entire first half of 2025, with six months still to run. For visa holders, a layoff opens a 60-day countdown that most American colleagues never have to think about.",
        "slug": make_slug("bay-area-tech-layoffs-9284-h1b-60-day-grace-warn"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "A pink slip means a 60-day grace period to find a new sponsor or leave the country — a deadline that turns every layoff round into an immigration emergency for thousands of Indian engineers on H-1B and L-1 visas.",
        "tags": ["layoffs", "h1b", "silicon-valley", "immigration", "ai", "jobs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "OpenTools — Bay Area tech layoffs 2026", "url": "https://opentools.ai/"},
            {"name": "Challenger, Gray & Christmas via LinkedIn", "url": "https://www.linkedin.com/"},
            {"name": "Santa Cruz Sentinel / California EDD WARN notices", "url": "https://edd.ca.gov/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_caption": "Office workstations in a Silicon Valley technology company",
        "_commons_q": ["Silicon Valley office", "tech company office cubicles"],
        "_pexels_q": ["empty office desks workstations", "silicon valley office building"],
        "body": """The numbers arrive the way layoffs always do in California — quietly, in a state filing. Five more Bay Area technology companies told the Employment Development Department they would cut a combined 370 jobs: Ubisoft (93 in San Francisco), Salesforce (86 in San Francisco), Quizlet (79), Verily Health (58 in San Bruno), and ServiceNow (54 at its Santa Clara headquarters). All permanent.

That round pushed the region's 2026 tally to **9,284 jobs**, according to WARN-notice data compiled by the Santa Cruz Sentinel — a figure that already exceeds the roughly 4,700 cuts across the nine-county Bay Area in the entire first half of 2025. The pace is nearly double last year's, with six months still on the clock.

For most workers, a layoff is a financial shock and a LinkedIn update. For the tens of thousands of Indian engineers in the Bay Area on H-1B and L-1 visas, it is something sharper: the start of a 60-day countdown.

## The deadline Americans never see

When an H-1B worker loses a job, federal rules give a grace period of up to 60 days — or until the existing petition expires, whichever is shorter — to find a new employer willing to file a fresh petition, switch to another status, or leave the United States. There is no extension for a soft job market. The clock does not care that hiring has slowed. For a family with a mortgage, a child in school, and a spouse on an H-4 visa, two months is brutally short.

This is why each Bay Area layoff round lands differently in Indian-American households than in the headlines. A 54-person cut at ServiceNow is a rounding error in a quarterly report. Inside those 54 could be a half-dozen visa holders for whom the layoff is simultaneously a career setback and an immigration emergency.

## AI is the axe and the alibi

The driver is no longer ambiguous. Big Tech announced more than 38,000 job cuts in May alone — the most in nearly two years — and the tech sector has shed 123,653 positions in 2026, a 65% jump over the same stretch last year, per Challenger, Gray & Christmas. "AI is now the leading reason companies give for cutting jobs," the firm's Andrew Challenger said.

Meta alone accounts for an outsized share of the regional pain — about 3,715 Bay Area jobs eliminated this year as it reorganizes around AI engineering. Mark Zuckerberg has conceded the company "made mistakes" in its AI workforce transition and pledged no further company-wide layoffs in 2026, but the damage to the regional total is already done.

The cruelty of the moment is that the same AI wave is hiring even as it fires. LinkedIn's 2026 Workforce Confidence Index reported a 47% year-over-year jump in postings for AI and machine-learning engineers, with senior base salaries now topping $310,000 at major hyperscalers. "We're not seeing a contraction — we're seeing a reallocation," said Brookings labor economist Priya Nambiar. The problem is that skills don't transfer automatically, and tech-sector unemployment for workers without cloud or AI credentials sits near 6.1%, against 3.8% for the sector as a whole.

## What it means for the diaspora

The practical advice circulating in Indian engineering circles has hardened into a checklist. Keep the I-797 approval notice and recent pay stubs accessible. Know the exact petition expiry date, not just the visa stamp. Line up an immigration attorney before a layoff, not after. And understand that the 60-day window can sometimes be bridged by filing a change of status — to a dependent visa, a student visa, or a B-2 visitor status — to buy time, though each carries trade-offs.

There is a darker structural read, too. Layoffs at H-1B-heavy firms have drawn political fire: lawmakers have demanded answers from major companies about visa use amid cuts, and at least one state — Iowa — has turned its IT operations over to a contractor while local politicians campaign explicitly against "H-1B outsourcing firms." For Indian workers, the layoff cycle is colliding with a hardening political mood, which makes finding a new sponsor not just harder but slower.

The 9,284 figure will keep climbing; WARN notices lag the actual decisions by weeks. For the diaspora, the lesson of this year's data is unsentimental: in a market where AI is reallocating rather than simply shrinking, the workers most exposed are the ones whose right to stay is tied to a single employer's spreadsheet."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "$1.3 Trillion Vanished From AI Chip Stocks in a Week. Then They Had Their Best Day in a Year.",
        "subheadline": "A single cautious sentence from Broadcom triggered one of the sharpest semiconductor selloffs in years — and a violent rebound days later. For Indian-American investors and tech workers paid in stock, the whiplash is the new normal.",
        "slug": make_slug("ai-chip-stocks-1-3-trillion-rout-rebound-broadcom-nvidia"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-American households are heavily concentrated in tech equities and equity compensation — RSUs, ESPPs, and chip-heavy index funds — so a $1.3 trillion swing in AI semiconductors lands directly on diaspora net worth, not just on Wall Street screens.",
        "tags": ["semiconductors", "nvidia", "broadcom", "ai", "markets", "investing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "WSJ — Semiconductor stocks jump to best day in more than a year", "url": "https://www.wsj.com/"},
            {"name": "AInvest — AI chip stocks down in June", "url": "https://www.ainvest.com/"},
            {"name": "TradingNews — Broadcom price forecast", "url": "https://tradingnews.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_caption": "A close-up of a semiconductor wafer used in advanced AI chips",
        "_commons_q": ["semiconductor wafer", "silicon wafer integrated circuit", "computer chip macro"],
        "_pexels_q": ["semiconductor chip closeup macro", "silicon wafer microchip"],
        "body": """It took one sentence to erase roughly $1.3 trillion in market value. In early June, Broadcom reiterated rather than raised its 2026 outlook — a perfectly respectable result from a company growing AI revenue 143% year over year — and the AI chip complex went into free fall. The stock dropped nearly 13% in a session, dragging the whole semiconductor index down more than 10% from a record. Put volume outnumbered calls four to one. This was not routine profit-taking; it was a panic.

Then, just as abruptly, the sector staged its best day in more than a year. The PHLX Semiconductor Index soared nearly 8% in a single session — its sharpest one-day gain since April 2025. The roll call of winners read like a diaspora investor's portfolio: Micron up 12%, Lam Research up 13%, Applied Materials up 11%, AMD up 8%, Qualcomm up 6%, Nvidia up 2%.

For the Indian-American household, this whiplash is not abstract. It is the net-worth chart.

## Why this hits Indian-American wealth squarely

Indian-American families are among the most concentrated tech investors in the country — by employment, by equity compensation, and by index exposure. A software engineer at Nvidia, AMD, Qualcomm, or Micron is often paid substantially in restricted stock units. A spouse running a household portfolio is frequently overweight the same Nasdaq names. And the default 401(k) and brokerage allocation — an S&P 500 or Nasdaq-100 index fund — is now so top-heavy with AI semiconductors that a chip selloff is effectively a household event.

So when $1.3 trillion evaporates and then largely reflows within a week, the people feeling it most acutely are not faceless institutions. They are the same engineers whose paychecks already rise and fall with these companies. The concentration cuts both ways: it amplified the gains of the past two years, and it amplifies every reset.

## The reset was about expectations, not demand

The important read on Broadcom's report was forward-looking. Management guided to roughly $29.4 billion in current-quarter revenue, above the $28.5 billion Wall Street consensus, and AI semiconductor revenue grew 143% to $10.8 billion — accelerating from 106% the prior quarter. By any conventional measure, the business is firing on all cylinders. The market punished a headline miss, not a deterioration in demand.

That distinction is the whole investing lesson. Even after the shock, the four largest hyperscalers have lifted their 2026 AI spending plans to about $750 billion. The buildout did not stop. What broke was the assumption that every quarter would deliver an upside surprise. When a stock is priced for perfection, "merely excellent" reads as bad news.

## The case for not flinching

Analysts who covered the rout were nearly unanimous that it looked like a violent expectations reset rather than the end of the AI cycle. Broadcom and AMD were singled out as the names with the clearest exposure to custom-silicon and AI-infrastructure demand. JPMorgan, ahead of Qualcomm's June 24 investor day, raised its price target to $265 from $160, citing a stronger long-term data-center and AI story. Broadcom's one-year total shareholder return remains up roughly 57%, and its five-year return tops 800% — which is precisely why the pullback is being reassessed rather than treated as a structural break.

None of that is a guarantee. The sector is volatile, valuations are stretched, and a genuine slowdown in hyperscaler spending would change the math overnight. India's own semiconductor story — the Micron plant in Gujarat, the Tata-PSMC fab, the broader India Semiconductor Mission — rides on the same wave of AI-driven memory and packaging demand, so a sustained chip downturn would ripple back home as well.

## The diaspora takeaway

For an Indian-American investor with a heavy tech tilt, the week was a stress test of temperament more than of thesis. The fundamentals that drove the rally are intact; the prices simply got ahead of them and then snapped back. The practical move is unglamorous: know your true concentration (RSUs plus index funds plus individual stocks often add up to far more chip exposure than people realize), rebalance on the way up rather than panic on the way down, and treat single-stock swings of this size as the cost of admission to the AI trade. The $1.3 trillion that vanished was never really gone — but the next time it disappears, it might not come back so fast."""
    }
]

# ---------- Source images, then insert ----------
for art in articles:
    cq = art.pop("_commons_q", [])
    pq = art.pop("_pexels_q", [])
    print(f"Sourcing image for: {art['slug']}")
    img_url, attribution = source_image(art["slug"], cq, pq)
    if img_url:
        art["image_url"] = img_url
        art["image_attribution"] = attribution
    else:
        print(f"  (no image sourced — inserting without hero)")

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  [img={'yes' if art.get('image_url') else 'NONE'}]")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
