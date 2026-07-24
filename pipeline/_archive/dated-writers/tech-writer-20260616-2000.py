#!/usr/bin/env python3
import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ---- Load env ----
for ef in [Path.home()/".env.supabase", Path.home()/"workspace"/".env.pexels"]:
    if ef.exists():
        for line in ef.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS = os.environ.get("PEXELS_API_KEY", "")
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
           "Content-Type": "application/json", "Prefer": "return=representation"}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height*ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(src_url, slug):
    try:
        r = requests.get(src_url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ image fetch failed {r.status_code} len={len(r.content)}")
            return None
        data = compress_image(r.content)
        if len(data) < 10000:
            print("  ⚠ compressed image too small"); return None
        fn = f"{slug}.jpg"
        up = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{fn}",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                     "Content-Type": "image/jpeg", "x-upsert": "true"},
            data=data, timeout=60)
        if up.status_code in (200, 201):
            pub = f"{SB_URL}/storage/v1/object/public/article-images/{fn}"
            print(f"  ✓ uploaded {fn} ({len(data)//1024} KB)")
            return pub
        print(f"  ⚠ upload failed {up.status_code}: {up.text[:120]}")
    except Exception as e:
        print(f"  ⚠ upload error: {e}")
    return None

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
def make_slug(base):
    s = re.sub(r"[^a-z0-9\s-]", "", base.lower())
    s = re.sub(r"\s+", "-", s.strip())
    return s[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")

# ============ ARTICLES ============
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Wants a Quarter of Every iPhone Made in India. The Wells Next to the Factory Are the Catch.",
        "subheadline": "Foxconn just signed for a new Tamil Nadu component plant and Apple is targeting 25% of global iPhone output from India — even as a pollution row threatens to shut a key Tata supplier.",
        "slug": make_slug("apple-india-iphone-25-percent-foxconn-tata-manufacturing"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs who fled India partly because the 'Made in China' supply chain never came home, Apple shifting a quarter of iPhone production to Tamil Nadu and Karnataka is the clearest sign yet that high-end manufacturing — and the jobs around it — is finally arriving in India.",
        "tags": ["apple", "iphone", "foxconn", "tata-electronics", "india-manufacturing", "supply-chain"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye / WSJ", "url": "https://theindianeye.com/apple-to-assemble-nearly-25-iphones-in-india/"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/tata-says-india-pollution-board-drops-scrutiny-apple-iphone-parts-plant-2026-06-16/"},
            {"name": "MacRumors / Bloomberg", "url": "https://www.macrumors.com/2026/06/16/apple-2028-iphones-1-4nm-a22-pro/"},
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_src": "https://images.pexels.com/photos/4211136/pexels-photo-4211136.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "Circuit boards of modern smartphones on an assembly line",
        "image_attribution": "Pexels",
        "body": """Apple has set a number, and it is a big one. According to a Wall Street Journal report this week, the company wants to assemble nearly **25% of the world's iPhones in India** within the next two to three years — up from roughly 7% today. To get there, Apple and its suppliers are pouring concrete across southern India faster than at any point in the company's history.

The supporting moves arrived almost on top of each other. Foxconn, Apple's largest assembler, signed a fresh agreement with the Tamil Nadu government to set up a mobile-component manufacturing facility, adding to the Karnataka plant it is bringing online that is eventually meant to churn out 20 million smartphones a year. Tata Group — which already runs an iPhone plant in Karnataka — is building what it says will be India's biggest iPhone assembly factory in Tamil Nadu, a 20-line site meant to employ 50,000 workers within 12 to 18 months.

The strategic logic is the diversification story NRIs have heard for years, now with hard capital behind it. Apple is trying to build a supply chain in which its products are no longer overwhelmingly made in one country. India has reportedly been chosen as the primary site to manufacture a new budget iPhone, and Apple is working with local contractors to lay out the production plan — something it had previously only done in China.

## The well water problem

Then there is the part of the story that does not fit the triumphant narrative. A Tata Electronics components plant in Hosur, Tamil Nadu — which makes back panels and enclosures for iPhones — spent the week under a pollution cloud, literally. The Tamil Nadu Pollution Control Board alleged that wastewater discharged from the facility overflowed a rainwater harvesting pond and contaminated groundwater in open wells on adjacent farmland, and it threatened a forced shutdown unless Tata gave a satisfactory explanation.

By Tuesday, the board had dropped its scrutiny after Tata commissioned an independent lab analysis it said showed "full compliance with all regulatory norms." But the episode — five state inspections between December 2025 and May 2026, complaints from farmers stretching back months — is a reminder that India's manufacturing ascent runs straight through real villages, real water tables, and a regulatory apparatus that is still finding its footing. It joins a list of supply-chain stumbles: a 2024 fire at the same Hosur plant, a 2023 fire at a Pegatron facility, and a Reuters investigation into hiring practices at a Foxconn plant.

## Why it lands differently for the diaspora

For an Indian engineer in Cupertino or a hardware manager in Austin, this is not abstract. The skills that make iPhones — precision tooling, quality systems, supply-chain management — are exactly the disciplines that the diaspora has spent two decades mastering abroad. As Apple deepens its India footprint, the demand for people who can bridge Silicon Valley standards and Tamil Nadu shop floors is rising, and a meaningful slice of that talent is expected to be returnees or cross-border operators with one foot in each world.

There is an investment angle too. Tata's electronics ambitions, the broader India Semiconductor Mission, and the component ecosystem now forming around Apple are creating listed and soon-to-list plays that NRI investors have been waiting for — a way to bet on "India makes things" rather than only "India writes code."

And there is a longer arc visible in the chip news that landed the same day: Bloomberg reported Apple's 2028 iPhones will move to 1.4-nanometer A22 Pro chips, with TSMC making most of them and Intel possibly making some. India is not yet in that conversation at the leading edge — its fabs are starting with mature nodes and memory. But the assembly base now being built is the on-ramp. China became indispensable to Apple by starting exactly where India is starting: putting the pieces together, then slowly climbing the value chain.

The wells of Hosur are a warning that the climb will not be clean or simple. But a quarter of every iPhone is a target Apple has never set for any country other than China — and that, for a diaspora that grew up being told the good jobs were always somewhere else, is the headline."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Took 120 of Its Hardest Science Startups to France. They Came Back With $100 Million in Deals.",
        "subheadline": "At Bharat Innovates 2026 in Nice, IIT Madras spinouts including rocket-maker Agnikul and a hyperloop venture signed commercial MoUs — a bid to be seen as a builder of frontier tech, not the world's back office.",
        "slug": make_slug("bharat-innovates-2026-iit-madras-agnikul-deep-tech-mous"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs weighing whether to move money — or themselves — back to India, deep-tech ventures finally signing real international contracts changes the calculus: the bet is no longer just on Indian IT services, but on Indian hard science with global customers.",
        "tags": ["deep-tech", "iit-madras", "agnikul", "startups", "india-innovation", "space-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/agnikul-hyperloop-and-other-iit-m-start-ups-sign-mous-of-100-million-at-bharat-innovates-2026/article69000000.ece"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/india-120-deep-tech-startups-nice-bharat-innovates-2026-cohort"},
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_src": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/IIT_Madras_campus_main_gate.jpg/1280px-IIT_Madras_campus_main_gate.jpg",
        "image_caption": "The main gate of the Indian Institute of Technology Madras in Chennai",
        "image_attribution": "Wikimedia Commons",
        "body": """India spends a lot of energy insisting it is more than a software shop for the world. This week, in the south of France, a few of its companies tried to prove it with signatures.

At **Bharat Innovates 2026** in Nice — part of the India-France Year of Innovation — IIT Madras and its global arm announced seven commercial Memoranda of Understanding between Indian deep-tech startups and international partners, predominantly French, plus two institutional MoUs aimed at investment and market access. The institute pegged the combined value at nearly **$100 million**. The startups in the room included names that are becoming shorthand for India's hard-tech ambitions: rocket-maker **Agnikul Cosmos**, industrial-inspection firm Detect Technologies, **TuTr Hyperloop**, and iElectron Technologies.

The framing was deliberate. "The MoUs exchanged are not just ceremonial — they are commercial, actionable, and backed by serious financial commitments," said V. Kamakoti, director of IIT Madras. The event was the centerpiece of a Ministry of Education push that put a curated cohort of 120 research-heavy Indian companies in front of international investors and policymakers, with one message: India can be a builder of frontier technology, not just a back office for it.

## The patient-capital problem

The reason an event like this matters is structural. Deep tech does not move at the speed of a food-delivery app. A semiconductor design or a satellite payload can take years to commercialize, and that timeline has long made such ventures hard to fund in an Indian market that prized quick consumer-app returns. Two of the institutional MoUs target exactly that gap: a partnership between IITM Global and Agna Capital to set up a "Bharat Innovates Fund" for high-potential deep-tech ventures, and a collaboration with SouthwestX to help Indian startups scale into the German and French markets.

It is part of a broader thaw. India's space sector — once the exclusive turf of state-run ISRO — has been opened to private firms, with a 10-billion-rupee fund to help space startups grow. Just days earlier, Bengaluru's SatSure won a 246-million-rupee ($2.6 million) government grant to build AI-powered Earth-observation models, part of a national push toward "sovereign AI." The deep-tech funding environment, while still small, is rebounding: Indian startups raised roughly $243-256 million in the most recent week tracked, a fourth straight week of gains.

## Why the diaspora should read past the press release

For the Indian American professional, the significance is less about any single $100 million figure and more about what it signals for where serious technical careers can now be built. For two decades, the implicit deal was that if you wanted to work on genuinely hard engineering — orbital rockets, hyperloop systems, frontier AI — you did it at a Western lab or a Bay Area startup. A cohort of IIT spinouts signing commercial contracts with European industrial partners chips away at that assumption.

It also reframes the NRI investment thesis. The familiar way to "invest in India" has been IT-services stocks and, more recently, quick-commerce IPOs. Deep tech offers a different shape of bet — higher risk, longer horizon, but tied to defensible intellectual property rather than labor arbitrage. Vehicles like the new Bharat Innovates Fund are early attempts to give diaspora and institutional money a structured way in, though most of these companies remain private and years from liquidity.

The caution is warranted. MoUs are intentions, not revenue, and India's deep-tech sector has a history of grand announcements that outpace delivery. The real test will be whether the Nice signatures turn into shipped products and recurring contracts — whether Agnikul's rockets fly on schedule, whether TuTr's hyperloop moves beyond the test track.

But the diaspora has watched India clear a higher bar before. The IT-services industry was once dismissed as glorified outsourcing; it became a $315 billion engine. If even a handful of this week's 120 companies make the same jump in hard tech, the question for the next generation of Indian engineers abroad will not be whether to come home — it will be which frontier to come home to."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Judge Killed Trump's $100,000 H-1B Fee. A Day Later, It Was Back. Tech's Indian Workforce Is on a Legal Seesaw.",
        "subheadline": "A Boston judge ruled the six-figure visa fee an unlawful tax, then an appeals stay reinstated it — leaving the IT firms and Bay Area engineers who depend on H-1B caught between rulings.",
        "slug": make_slug("h1b-100000-fee-struck-down-reinstated-appeal-tech-workers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indians receive more than 70% of H-1B visas, and the tech industry runs on them — so the whiplash of a $100,000 fee being struck down and then reinstated within a day directly governs whether thousands of engineers can keep, change, or take new jobs in the US.",
        "tags": ["h-1b", "tech-jobs", "immigration-policy", "indian-it", "silicon-valley", "visas"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
            {"name": "AInvest", "url": "https://www.ainvest.com/news/us-court-temporarily-reinstates-100000-h-1b-fee-amid-government-appeal-2606/"},
            {"name": "The Indian Eye / Politico", "url": "https://theindianeye.com/100000-h-1b-visa-fee-us-judge-blocks/"},
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_src": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Passport_stamps_of_the_United_States_Visum_AT.jpg",
        "image_caption": "A United States visa and entry stamps in a passport",
        "image_attribution": "Wikimedia Commons",
        "body": """If you hold an H-1B visa, or are waiting on one, this was a week to keep the lawyer on speed dial.

A federal judge in Boston, Leo Sorokin, struck down the Trump administration's **$100,000 fee on new H-1B petitions**, ruling it an unlawful tax that Congress never authorized. "The substance and application of the $100,000 payment reveal that it is a tax, regardless of what the payment is called," he wrote, leaning on the Supreme Court's February decision against Trump's emergency-powers tariffs. The fee, imposed by a September 2025 proclamation, had landed like a wrecking ball on an industry built around the visa.

Relief lasted about a day. On June 15, a court granted the government a stay while it appeals to the First Circuit — **temporarily reinstating the fee** and reversing, for now, the win that 20 Democratic state attorneys general had just secured. The legal merits will be argued for months. The practical effect is that employers and workers are back to budgeting around a six-figure charge they thought was dead.

## Why this is a tech story first

It is tempting to file the H-1B fight under immigration. But the program is, in practice, the staffing backbone of the American technology industry. People born in India have received **more than 70% of approved H-1B petitions every year since 2015**. The fee directly reshapes how — and whether — the biggest names in tech can hire.

The strain was already visible before the courthouse drama. Official US data showed H-1B approvals for India's six largest IT firms — TCS, Cognizant, Infosys, HCL, Wipro and Tech Mahindra — fell **40% this year to 11,041**, with TCS taking the steepest cut. Those firms have responded by leaning harder on offshore delivery from India and local hiring in the US; Wipro now says 80% of its US workforce is locally hired. A $100,000 surcharge on each remaining petition only accelerates that retreat from the visa.

For the FY2027 cap, the squeeze compounds with a separate change: a new wage-weighted lottery that gives senior, higher-paid candidates up to four times the selection odds of entry-level ones. An estimated 143,000 Indian students on OPT and STEM OPT now face a system where a fresh-graduate role carries roughly a 15% chance of selection, down from the old equal-odds ~30%.

## What it means on the ground

For a mid-career engineer at Google or Microsoft already on H-1B, the immediate question is mobility. The fee, as litigated, applies to new petitions and consular processing — so changing employers, or being laid off and needing a new sponsor, is where the risk concentrates. With Bay Area tech layoffs already topping 9,000 this year and the 60-day grace clock unforgiving, the difference between "fee struck down" and "fee reinstated" can decide whether a displaced worker can realistically find a new sponsor or has to leave the country.

For the IT services giants, the calculus is colder. Each company has spent years cutting H-1B dependence precisely to insulate itself from this kind of shock; analysts estimate the medium-term revenue hit at a manageable 5-7%. The people without that buffer are individual applicants — the new graduate, the consultant on a client site, the spouse whose H-4 work authorization hangs off a primary visa now in legal limbo.

Notably, the political coalition against the fee is not the usual one. Several Republican lawmakers backed the court's decision, arguing less about Silicon Valley and more about how a $100,000 penalty would gut healthcare and education staffing in rural America. Others, like Utah's Mike Kennedy, want to codify the fee through Congress so a court cannot undo it — which would make it far harder to challenge.

That is the real signal for the diaspora. The courts may settle this particular fee, but the direction of travel is clear: the US is steadily raising the price and lowering the odds of the visa that built Indian-American tech. The smart move for anyone on, or hoping for, an H-1B is to treat this week's seesaw not as noise but as the new normal — and to plan, hedge, and document accordingly."""
    },
]

# ---- source images ----
for art in articles:
    print(f"Sourcing image for: {art['slug']}")
    final = upload_to_supabase(art.pop("image_src"), art["slug"])
    if final:
        art["image_url"] = final
    else:
        print("  ⚠ no image — inserting without hero")
        art["image_url"] = None

# ---- insert ----
ok = 0
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:60]}")
        ok += 1
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDONE: {ok}/{len(articles)} inserted")
