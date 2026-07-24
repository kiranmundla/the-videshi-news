#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 19:30 UTC batch
Topics: 1) SpaceX IPO at $1.75 trillion — largest in history, India's space economy contrast, NRI investor angle
        2) AI layoffs reshoring — tech giants cutting H-1B workers in US while building same teams in India, GCC boom
"""

import json, os, uuid, re, requests, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Supabase config ──
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

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, params, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(slug_base, date_suffix="20260525"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Pexels helper ──
pexels_env = Path.home() / "workspace" / ".env.pexels"
PEXELS_KEY = None
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.split("=", 1)[1].strip()

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=15
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    try:
        img_data = requests.get(image_url, timeout=20).content
        content_type = "image/jpeg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        h = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        r = requests.post(upload_url, headers=h, data=img_data, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return image_url

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')
now_plus1 = (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: SpaceX IPO — $1.75 Trillion, Largest in History
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("spacex-ipo-175-trillion-largest-history-india-isro-starlink-nri-investors")
headline1_prefix = "spacex"
if slug1 not in existing_slugs and not any("spacex" in h and "ipo" in h for h in existing_headlines_lower):
    body1 = """SpaceX has filed for what will be the largest initial public offering in history.

The company founded by Elon Musk to colonize Mars is expected to list on the Nasdaq on June 12, 2026, at a valuation of up to $1.75 trillion. It plans to raise approximately $75 billion in fresh capital — more than two and a half times what Saudi Aramco raised in 2019 in the previous record-setting IPO.

The prospectus, filed confidentially with the SEC and since made public, reveals a company with $18.67 billion in annual revenue, cumulative losses exceeding $30.8 billion, and a $4.28 billion deficit in the first quarter of 2026 alone. Musk retains 85.1 percent voting control. The price-to-sales ratio at the proposed valuation approaches 100 — a number that would make even the most generous tech investor pause.

And yet the roadshow, which begins June 8, is expected to be massively oversubscribed.

## What SpaceX Actually Is

The popular narrative is rockets. The financial reality is internet.

Starlink, SpaceX's satellite internet constellation, generated $3.3 billion in operating income in 2025. It is the company's only profitable division. The rockets — including the 400-foot Starship, which conducted its twelfth test flight from Starbase, Texas, on May 22 — have never turned a profit. Starship's development costs have consumed tens of billions of dollars over the past decade. A thirteenth test flight is scheduled for June 12, the same day as the IPO — a coincidence that reads more like a marketing decision than a launch window constraint.

The prospectus also describes a $26.5 trillion total addressable market — a figure that encompasses telecommunications, AI compute infrastructure, Earth observation, defense, and interplanetary transport. It is the kind of number that either signals visionary ambition or prospectus inflation, depending on whether you believe Elon Musk's timeline for putting humans on Mars.

A Reuters analysis of the 50 largest IPOs in the past five years found that investors who bought in at the IPO price would have been better off investing in an S&P 500 index fund approximately 75 percent of the time. Companies with high valuations at listing tend to underperform.

## What This Means for India's Space Economy

India has more than 400 space technology startups. It recently announced its first space tech unicorn. ISRO — the Indian Space Research Organisation — has been launching satellites since 1975, put a probe on Mars for $74 million in 2014 (less than the production budget of the film *Gravity*), and successfully landed Chandrayaan-3 on the lunar south pole in 2023.

ISRO's annual budget is approximately $2 billion.

SpaceX's proposed valuation of $1.75 trillion is roughly equivalent to 875 years of ISRO's budget. That is not a comparison designed to diminish ISRO — few organizations in history have achieved more with less. It is a comparison designed to illustrate the scale of the capital asymmetry that defines the global space race in 2026.

India's space startups — Agnikul Cosmos, Skyroot Aerospace, Pixxel, Dhruva Space — are building real technology. Agnikul's Agnibaan rocket, with its 3D-printed engine, is genuinely innovative. Skyroot's Vikram-S was the first privately developed Indian rocket to reach space. But these companies are raising tens of millions of dollars. SpaceX is about to raise $75 billion in a single transaction.

The gap is not about engineering talent. India has that in abundance. The gap is about capital markets, regulatory frameworks, and the willingness of a country's financial system to deploy enormous sums of money on long-duration, high-risk bets.

## Starlink and the India Question

There is a specific, immediate tension between SpaceX and India: Starlink.

SpaceX's satellite internet service operates in more than 80 countries. India is not one of them. Despite significant demand — particularly in rural areas where terrestrial broadband remains inconsistent — Starlink's India entry has been blocked by the Telecom Regulatory Authority of India (TRAI) over spectrum allocation disputes, security concerns about foreign-controlled satellite networks, and resistance from incumbent telecom operators who see satellite internet as a competitive threat.

Jio, owned by Reliance Industries, has announced its own satellite broadband venture. Bharti Enterprises backs OneWeb, a Starlink competitor now merged with Eutelsat. The Indian government's preference appears to be channeling satellite internet demand through domestic players rather than allowing a foreign company — particularly one controlled by a single individual who also runs the world's most prominent social media platform, a major defense contractor, and soon the world's most valuable public company — to operate critical telecommunications infrastructure on Indian soil.

For rural India, the policy question is whether regulatory protection of domestic incumbents is worth the cost of delayed connectivity. For SpaceX investors, the question is whether the $26.5 trillion total addressable market in the prospectus includes India's 1.4 billion people or quietly excludes them.

## For NRI Investors

The SpaceX IPO will be accessible to Indian Americans through their U.S. brokerage accounts. For NRIs with demat accounts in India, direct participation in the IPO is not possible — Indian residents cannot buy shares listed on the Nasdaq through domestic brokers. However, indirect exposure through U.S.-listed ETFs that include SpaceX after listing (most major index funds will eventually add it) will be available.

The more interesting question for the diaspora is philosophical rather than financial. Thousands of Indian-origin engineers work at SpaceX — in propulsion, avionics, Starlink ground systems, and mission operations. Many of them are H-1B holders or recent green card recipients. They helped build the technology that makes a $1.75 trillion valuation conceivable. Some hold employee stock that will become liquid at IPO. For them, June 12 is not an abstract market event. It is a payday that may define the trajectory of their financial lives.

But the broader question is whether India — a country that has demonstrated world-class space engineering capability on a shoestring budget — can build the capital structures and regulatory environments that allow its own space companies to scale to SpaceX's ambitions. The talent exists. The engineering heritage exists. The 400 startups exist. What does not yet exist is a financial ecosystem willing to write a $75 billion check on the premise that rockets will eventually be profitable.

ISRO put a spacecraft on Mars for less than the cost of a Manhattan apartment building. SpaceX is about to raise enough capital to buy every apartment building in Manhattan. Both facts are true. Both facts matter. The distance between them is where India's space future will be decided."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "SpaceX Is About to Become the Largest IPO in History. It Is Valued at $1.75 Trillion. India's Entire Space Budget — the One That Put a Probe on Mars for $74 Million — Would Take 875 Years to Match That Number.",
        "subheadline": "Elon Musk's SpaceX has filed for a Nasdaq listing on June 12 at a valuation of up to $1.75 trillion, with plans to raise $75 billion — more than double Saudi Aramco's record. The company's prospectus reveals $18.67 billion in annual revenue, $30.8 billion in cumulative losses, and a $26.5 trillion claimed addressable market. Musk retains 85.1 percent voting control. For India's 400-plus space startups, the IPO is both inspiration and indictment: ISRO has proven world-class engineering capability on a fraction of the budget, but the capital gap between Indian space ventures raising millions and SpaceX raising $75 billion in a single offering defines the structural limits of India's space ambitions. Starlink, SpaceX's only profitable division, remains blocked from entering India over spectrum and security disputes. Thousands of Indian-origin engineers at SpaceX hold employee stock that will become liquid at listing.",
        "slug": slug1,
        "category": "news",
        "vertical": "technology",
        "diaspora_angle": "If you are an Indian engineer at SpaceX, June 12 may be the most important day of your financial life. Employee stock that has been illiquid for years will suddenly have a market price attached to a $1.75 trillion valuation. For some, this will mean generational wealth. For others — those who joined recently at high internal valuations — the math may be less favorable. But the IPO is also a mirror for the Indian space ecosystem. ISRO proved that world-class space engineering does not require Silicon Valley budgets. Chandrayaan-3 landed on the Moon for a fraction of what SpaceX spends on a single Starship test. India has 400 space startups and its first unicorn. What it does not have is a financial system that writes $75 billion checks on speculative technology bets. The question for every Indian-American in aerospace, for every NRI investor deciding whether to buy SpaceX at a 100x price-to-sales multiple, and for every policymaker in New Delhi blocking Starlink's entry into the Indian market, is the same: Does India want to compete in the space economy as it exists in 2026, or does it want to compete in the space economy as it existed in 2014 when Mangalyaan reached Mars orbit? The answer to that question requires not better rockets — India already builds those — but better capital markets, faster regulatory decisions, and the willingness to let private companies fail expensively on the path to succeeding spectacularly. ISRO's $2 billion annual budget produces extraordinary results. SpaceX's $1.75 trillion valuation produces extraordinary expectations. India needs both.",
        "tags": ["SpaceX", "IPO", "Elon Musk", "ISRO", "India space", "Starlink", "NRI", "investors", "Nasdaq", "Agnikul", "Skyroot", "technology", "Chandrayaan", "satellite internet", "TRAI"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — SpaceX debut draws a crowd, but few recent hot IPOs outpace the market", "url": "https://www.reuters.com/technology/spacex-debut-draws-crowd-few-recent-hot-ipos-outpace-market-2026-05-25/"},
            {"name": "The Hindu BusinessLine — SpaceX and the Big Bang IPO bubble", "url": "https://www.thehindubusinessline.com/opinion/spacex-and-the-big-bang-ipo-bubble/article71010000.ece"},
            {"name": "Inc42 — India Must Build Its Space Tech Companies The Way NASA Built SpaceX", "url": "https://inc42.com/features/india-must-build-space-tech-companies-nasa-built-spacex/"},
            {"name": "SpaceX S-1 Filing / SEC Prospectus", "url": "https://www.sec.gov/"}
        ]),
        "score_total": 84,
        "status": "published",
        "published_at": now_iso,
        "body": body1
    })
    print(f"✓ Article 1 prepared: SpaceX IPO $1.75T / India space economy")
else:
    print(f"✗ Article 1 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: The Great AI Reshore — Laying Off H-1B Workers, Hiring in India
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("ai-layoffs-reshore-h1b-fired-us-hired-india-gcc-tech-2026")
headline2_prefix = "same companies"
if slug2 not in existing_slugs and not any("reshore" in h or ("fired" in h and "hired" in h and "india" in h) for h in existing_headlines_lower):
    body2 = """By mid-May 2026, more than 113,000 technology jobs had been eliminated across 179 companies globally. The pace is running roughly a third faster than the same period in 2025. The companies doing the cutting include Meta (8,000), Oracle (30,000, of which 12,000 were in India), Intel (24,000-27,000), Amazon, Cisco, and SAP. The stated reason, in virtually every earnings call and press release, is the same: artificial intelligence.

Here is what the earnings calls do not say: many of the same companies eliminating positions in the United States are simultaneously expanding teams in India.

## The Numbers

India now hosts 2,117 Global Capability Centres — the corporate term for what used to be called "offshore development centres" and before that "outsourcing hubs." These GCCs employ 2.36 million people and represent a $98.4 billion market, according to Zinnov's India GCC Report for FY26. The sector is expected to add 450,000 new jobs this year alone.

Google, Amazon, Microsoft, Uber, and eBay are all expanding Indian operations in 2026. Twenty-five percent of companies surveyed are growing teams. Twenty percent are creating entirely new roles. The growth is driven by a combination of cost arbitrage (a senior engineer who costs $150,000-$180,000 in the United States costs $40,000-$50,000 in India for comparable output), H-1B visa restrictions (registrations plummeted 38.5 percent from FY2026 to FY2027), and the discovery that AI does not actually eliminate the need for humans — it changes which humans you need and where they sit.

"Firms that cut staff by 50 percent after adopting AI tools were coming back within months saying they still needed people to manage them," said Ramani Dathi, CFO of TeamLease, India's largest staffing company. TeamLease is now advising clients to keep 20-30 percent of their workforce on outsourced or variable models.

Senior global leadership roles based in India are growing at approximately 40 percent per year, surpassing 6,500 in 2024 and on track to exceed 30,000 by 2030. These are not junior coding positions. They are product leadership, AI engineering, and strategic decision-making roles.

"The question many ask is not 'how much can we offshore?' but 'what can India lead?'" said Neeti Sharma, CEO of TeamLease Digital. "Engineering, AI, and product execution are increasingly India-owned."

## The H-1B Squeeze

For Indian technology workers in the United States, the arithmetic is brutal.

H-1B registrations dropped 38.5 percent in a single year — from 343,981 in FY2026 to 211,600 in FY2027. USCIS simultaneously shifted approval criteria toward higher degrees and higher salaries: 71.5 percent of selected registrants now hold U.S. master's degrees or higher, up from 57 percent the previous year. Only 17.7 percent of approvals went to the lowest wage category.

Translation: the United States is making it harder for Indian tech workers to arrive, harder for them to stay if they are laid off (the 60-day clock to find new employment or leave the country), and simultaneously telling them that the same job they were doing in San Jose is now being done by someone in Bangalore — employed by the same company, often reporting to the same manager, but at a quarter of the cost.

For the approximately 800,000 Indians in the green card backlog — some of whom have been waiting more than a decade — the GCC expansion raises an existential question: What exactly are they waiting for?

## The Paradox at the Heart of This

The old model was simple. Indian companies like TCS, Infosys, and Wipro hired large numbers of engineers in India, trained them, and deployed them on projects for American clients — sometimes in India, sometimes on-site in the United States on H-1B visas. The value proposition was cost: the same work, done by equally qualified people, at a fraction of the price.

AI has compressed the bottom of that pyramid. Routine coding, testing, support, and back-office operations — the work that justified headcount in the hundreds of thousands — can increasingly be done by machines. TCS lost nearly 24,000 people in FY26. Infosys trimmed its base, letting go of trainees and junior staff throughout 2025.

But the top of the pyramid is expanding. The roles moving to India are more senior, more valuable, and more strategically important than ever before. Product development that used to be managed from Silicon Valley is being led from Bangalore and Hyderabad. AI research that required proximity to Stanford is being conducted in labs in Pune and Chennai. The centre of gravity, as Zinnov's Sidhant Rastogi puts it, "is moving gradually from the US to India."

The paradox: India is simultaneously losing routine jobs and gaining strategic ones. The country is winning better work and a thinner organisational pyramid at the same time.

## What This Means for the Diaspora

For an Indian engineer on an H-1B in California, the GCC boom in India is not abstract market data. It is a competing career path.

The financial calculus has shifted. An engineer earning $180,000 in San Jose — with $3,500 in monthly rent, $1,200 for childcare, $800 in student loan payments, and the perpetual uncertainty of visa renewal — takes home less disposable income than a peer earning $65,000 in Bangalore in a comparable role with domestic benefits, family proximity, and no immigration anxiety.

This does not mean the exodus has begun. The pull factors of the American technology ecosystem — access to the world's largest venture capital market, the density of talent in a few square miles of the Bay Area, the path to permanent residency and citizenship — remain powerful. But for the first time, the question "Should I go back?" is being answered with spreadsheets rather than sentiment.

The companies facilitating this shift are not Indian outsourcers. They are Google and Amazon and Microsoft — American companies that have concluded, through the cold logic of quarterly earnings, that the most efficient way to build technology in 2026 is to hire senior Indian engineers in India rather than sponsor H-1B visas for them in the United States.

The irony is inescapable. The same immigration system that forced Indian workers to wait 10-15 years for a green card is now incentivizing the companies that employed them to move the work to where the workers already had citizenship all along.

## The Real Question

Rastogi frames the central tension precisely: "The real question is whether India can move up to higher-value work faster than AI removes the routine work at the bottom."

If India succeeds — if its GCCs become genuine centres of product innovation rather than cost-optimized support functions — then the reshore is not a threat to the Indian technology ecosystem. It is an upgrade.

If India does not succeed — if the GCC expansion proves to be the last iteration of the same cost-arbitrage model that has defined Indian IT for two decades, just with fancier titles — then the 450,000 new jobs this year will be as vulnerable to the next wave of AI as the routine coding jobs were to this one.

For the Indian diaspora in America, the calculation is even more personal. Every GCC expansion announcement from Google or Amazon is both a validation and a warning. A validation that the talent that built Silicon Valley came from India and can build the same things from India. A warning that the H-1B pipeline — the mechanism that brought 4.8 million Indian Americans to the United States — is being made redundant not by policy alone, but by the companies that used to depend on it.

The bridge between Bangalore and the Bay Area has always carried traffic in one direction. For the first time, the heaviest loads are moving the other way."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The Same Companies Firing Indian Engineers in San Jose Are Hiring Indian Engineers in Bangalore. The Salary Is a Quarter of the Cost. The Work Is the Same. And the H-1B Pipeline That Connected Them Is Collapsing.",
        "subheadline": "By mid-May 2026, more than 113,000 tech jobs have been eliminated across 179 companies — a pace running one-third faster than last year. Meta cut 8,000. Oracle cut 30,000. Intel cut up to 27,000. But India's Global Capability Centres are adding 450,000 jobs this year alone, now employing 2.36 million people across 2,117 centres in a $98.4 billion market. Google, Amazon, Microsoft, Uber, and eBay are all expanding Indian operations. H-1B registrations have plummeted 38.5 percent in a single year. A senior engineer who costs $180,000 in the US costs $50,000 in India. Senior leadership roles based in India are growing 40 percent annually, on track to exceed 30,000 by 2030. The companies are not outsourcing support work — they are moving product leadership, AI engineering, and strategic decision-making. For 800,000 Indians in the green card backlog, the question is existential: What are they waiting for, when the same companies are building the same teams in the country they left?",
        "slug": slug2,
        "category": "news",
        "vertical": "technology",
        "diaspora_angle": "If you are an Indian engineer in America on an H-1B visa, this article describes the ground shifting beneath your feet. The companies that sponsored your visa are building teams in the country you left — not for junior coding work, but for AI engineering, product leadership, and strategic roles. H-1B registrations dropped 38.5 percent in one year. The 60-day clock after a layoff gives you two months to find a new sponsor or leave. The green card backlog stretches 10-15 years. Meanwhile, a comparable role in Bangalore pays a quarter of the San Jose salary but delivers more disposable income after rent, childcare, and student loans. This is not about outsourcing. Google is not sending support tickets to India. Google is sending product leadership to India. Amazon is not offshoring QA. Amazon is building AI engineering centres in India. The distinction matters because it changes the calculus for every Indian-American in tech. The old argument for staying was that the best work happened in Silicon Valley. If the best work is increasingly happening in Bangalore and Hyderabad — led by the same companies, often reporting to the same global org charts — then the immigration sacrifice required to remain in the United States needs to deliver correspondingly greater career returns. For many, it no longer does. The bridge between India and America has always carried traffic west. The heaviest loads are now moving east. And the immigration system that created the Indian-American tech workforce may be the very mechanism that is making it obsolete.",
        "tags": ["AI", "layoffs", "H-1B", "GCC", "India", "technology", "reshore", "Google", "Amazon", "Microsoft", "Silicon Valley", "Bangalore", "immigration", "NRI", "diaspora", "green card", "TeamLease", "Zinnov"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine — India may see delayed and cushioned impact of global tech layoffs", "url": "https://www.thehindubusinessline.com/info-tech/india-may-see-delayed-and-cushioned-impact-of-global-tech-layoffs/article71007203.ece"},
            {"name": "Storyboard18 — AI layoffs 2026: Amazon, Meta, Oracle, Cisco among tech firms cutting jobs", "url": "https://storyboard18.com/"},
            {"name": "USCIS — FY2027 H-1B Registration Data", "url": "https://www.uscis.gov/"},
            {"name": "Zinnov — India GCC Report FY26", "url": "https://zinnov.com/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now_plus1,
        "body": body2
    })
    print(f"✓ Article 2 prepared: AI reshore — firing in US, hiring in India")
else:
    print(f"✗ Article 2 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# PUBLISH + IMAGE SOURCING
# ══════════════════════════════════════════════════════════════

if not articles:
    print("\n⚠ No new articles to publish. Exiting.")
    exit(0)

print(f"\n📝 Publishing {len(articles)} articles...")

for i, art in enumerate(articles):
    art_id = art["id"]
    print(f"\n--- Article {i+1}: {art['headline'][:80]}...")

    try:
        result = sb_post("p2_articles", art)
        print(f"  ✓ Inserted: {art_id}")
    except Exception as e:
        print(f"  ✗ Insert failed: {e}")
        continue

    if i == 0:
        img_url = fetch_pexels_image("rocket launch night sky spacex", "spacecraft launch pad rocket")
    else:
        img_url = fetch_pexels_image("software engineer office India Bangalore", "modern technology office workspace")

    if img_url:
        filename = f"{art['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        try:
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {"image_url": final_url})
            print(f"  ✓ Image linked")
        except Exception as e:
            print(f"  ⚠ Image PATCH failed: {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY
# ══════════════════════════════════════════════════════════════

print("\n📉 Applying score decay to older news articles...")
try:
    old_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=7)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.35",
        "limit": "200"
    })
    for a in old_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 35})
    print(f"  Decayed {len(old_arts)} articles (>7d → 35)")

    mid_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=3)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.50",
        "limit": "200"
    })
    mid_arts = [a for a in mid_arts if a["id"] not in {x["id"] for x in old_arts}]
    for a in mid_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 50})
    print(f"  Decayed {len(mid_arts)} articles (3-7d → 50)")
except Exception as e:
    print(f"  ⚠ Decay error: {e}")

# ══════════════════════════════════════════════════════════════
# GIT COMMIT + PUSH
# ══════════════════════════════════════════════════════════════

print("\n📦 Committing and pushing...")
repo_dir = Path.home() / "workspace" / "the-videshi-news"
try:
    subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True, timeout=15)
    result = subprocess.run(
        ["git", "commit", "-m", f"news: SpaceX IPO + AI reshore ({now.strftime('%Y-%m-%d %H:%M')} UTC)"],
        cwd=repo_dir, capture_output=True, text=True, timeout=15
    )
    print(f"  Commit: {result.stdout.strip()[:100]}")
    push = subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True, text=True, timeout=30)
    if push.returncode == 0:
        print("  ✓ Pushed to main → Vercel auto-deploy")
    else:
        print(f"  ⚠ Push issue: {push.stderr[:200]}")
except Exception as e:
    print(f"  ⚠ Git error: {e}")

print("\n✅ News writer batch complete.")
