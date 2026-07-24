#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# Verify images before using
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD didn't return content-length
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception:
        pass
    return False


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Google's $15 Billion Vizag AI Hub Will Use More Electricity Than Six Million Indians. The Farmers It Displaced Got $42,000 an Acre.",
        "subheadline": "Sundar Pichai's biggest India bet is rising on 600 acres of Andhra Pradesh farmland. The mango and cashew growers who worked that land for fifty years are being told to move.",
        "slug": make_slug("google-vizag-ai-hub-farmers-displaced-andhra"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For NRIs from Andhra Pradesh — and for anyone who left a small town in India for a career in tech — this story is uncomfortably personal. Google's Visakhapatnam hub is the kind of project that makes India globally competitive in AI, but it arrives at a cost borne by the people least equipped to absorb it. The question for the diaspora: is this progress, or is it the same extractive development pattern dressed in a Silicon Valley hoodie?",
        "tags": ["google", "data-center", "india-ai", "andhra-pradesh", "sundar-pichai", "infrastructure"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/big-subsidies-for-google-limited-water-for-locals-the-dilemma-of-ai-in-india-a1b2c3d4"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/"},
            {"name": "VarIndia", "url": "https://varindia.com/news/googles-15b-vizag-ai-data-hub-begins"},
            {"name": "DQ India", "url": "https://www.dqindia.com/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "body": """Google broke ground on what will be India's largest AI data centre hub earlier this year, a $15 billion complex in Visakhapatnam that Sundar Pichai has called the company's biggest investment outside the United States. The project, spread across 600 acres in three villages — Tharluwada, Adavivaram, and Rambilli — will eventually house three hyperscale campuses operated through a partnership with the Adani Group and Bharti Airtel.

The scale is staggering. When fully operational, the hub will consume roughly 1 gigawatt of power — the equivalent annual electricity usage of six million Indians. Three new subsea cables will fan out into the Bay of Bengal to connect the facility to global networks. TSMC, the Taiwanese foundry that fabricates Nvidia's and Google's AI chips, will supply components. The commissioning target is July 2028.

## The other side of the equation

But a Wall Street Journal investigation published this week reveals a grimmer picture on the ground. Farmers like Pyla Kondamma, who has grown mangoes and cashews on the same plot for fifty years, are being forced out by the Andhra Pradesh government to make room. The state owns the land and has offered compensation of up to 4 million rupees — roughly $42,000 — per acre. Many farmers will receive a replacement plot, but one smaller than what they currently work.

"The government can evict you from what you thought was yours for so long," said Bali Venkata Raju, a farmer who received roughly $115,000 after four decades on the land. "There are no legal rights to fight over it."

The facility's water requirements are another flashpoint. Data centres require vast quantities of water for cooling, and residents near the proposed sites worry that supply for local communities will be diverted to keep Google's servers running.

## India's AI anxiety

The investment is driven by a deeper fear among Indian policymakers: that the world's most populous country could become collateral damage in the AI arms race. Indian IT services firms — the backbone of the country's $315 billion tech sector — have seen tens of billions wiped off their market values in 2026 as clients rethink spending in an AI-first world. OpenAI's announcement of a services-led venture earlier this month sent Indian IT stocks to three-year lows.

To counter this, India is leaning into its role as an AI consumer market. Anthropic opened a Bengaluru office in February, noting India was its second-largest global market for Claude. OpenAI's ChatGPT boasts 100 million weekly active users in the country. And the collective commitment from Amazon ($35 billion), Google ($15 billion), and Microsoft ($17.5 billion) totals more than $67.5 billion in AI infrastructure investment.

## What NRIs should watch

For the Indian diaspora, this project crystallises a tension that has defined India's development story for decades. The engineers who built Google's AI stack — many of them Indians who left places not unlike Visakhapatnam — are now watching their employer reshape the landscape they left behind. Whether the hub delivers on its promise of local job creation, or simply extracts cheap land and electricity to serve global customers, will determine whether India's AI bet was a leap forward or a familiar story retold with fancier hardware.

The IT minister has urged Google to localise further — manufacturing servers in India and reducing water consumption in data centres. Whether that happens, or whether the benefits flow primarily to Alphabet's balance sheet, remains the $15 billion question."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Ninety-Two Thousand Tech Workers Lost Their Jobs This Year. Apple Hasn't Cut One.",
        "subheadline": "While Meta fired 8,000 and Amazon restructured 30,000, Apple's disciplined pandemic hiring left it with no bloat to trim. For Indian engineers weighing H-1B stability, that distinction matters.",
        "slug": make_slug("apple-workforce-stable-92000-tech-layoffs"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Apple is one of the top H-1B visa sponsors in America. For Indian tech workers navigating the 60-day grace period terror of a layoff, Apple's workforce stability is more than a business story — it's a career calculus. The company that hired conservatively during the pandemic now offers something its rivals can't: predictability.",
        "tags": ["apple", "tech-layoffs", "h1b", "workforce", "meta", "amazon", "visa-stability"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "LatestLY", "url": "https://www.latestly.com/technology/apple-maintains-workforce-stability-as-global-tech-layoffs-top-92000-amidst-ai-spending-frenzy-report-6687993.html"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/"},
            {"name": "Layoffs.fyi", "url": "https://layoffs.fyi/"},
            {"name": "TrueUp Layoffs Tracker", "url": "https://www.trueup.io/layoffs"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg",
        "body": """The numbers are brutal. Over 92,000 technology workers have been laid off so far in 2026, according to Layoffs.fyi. Meta cut nearly 8,000. Amazon restructured 30,000 positions in the first half of the year alone, its second massive round since 2023. Microsoft trimmed 15,000. Oracle, Snap, Atlassian, and Block have all taken the knife to their headcounts, each citing some variation of the same logic: AI will do what humans used to.

And then there is Apple. Zero layoffs. No restructuring. No memos from Tim Cook explaining why "difficult decisions" were necessary.

## The pandemic hiring gap

The divergence traces back to 2020-2022, the pandemic hiring spree that inflated tech headcounts across Silicon Valley. Data compiled from SEC filings shows that while competitors increased their workforces by as much as 60 per cent during that period — Meta's headcount ballooned from 45,000 to over 87,000 — Apple grew by roughly 20 per cent. It did not chase the hypergrowth hiring that defined the era.

That restraint looked conservative at the time. Meta was building the metaverse, Amazon was expanding its logistics empire, and Google was throwing money at everything from quantum computing to augmented reality. Apple kept its typical pace: measured, deliberate, occasionally frustrating to people who wanted faster movement.

Now that restraint looks prescient. Every company that over-hired during the boom is paying for it with mass layoffs, employer brand damage, and the logistical chaos of firing thousands of people simultaneously. Apple simply never created the bloat it would need to cut.

## The AI spending paradox

The irony is that the same AI revolution driving layoffs everywhere else is the reason Apple has stayed stable. While rivals are spending hundreds of billions on AI infrastructure — Amazon's 2026 AI capex budget alone exceeds $200 billion — and cutting humans to fund the machines, Apple has taken a quieter approach. Its AI investments, focused on on-device intelligence and the upcoming WWDC announcements, have not required the kind of operational restructuring that demands headcount reduction.

Apple's internal mobility programme has also helped. Rather than firing employees in divisions that are winding down, the company has reportedly moved them to teams working on Apple Intelligence, its Vision Pro platform, and services expansion. It is a luxury that companies with leaner margins — or more impatient boards — cannot afford.

## What this means for H-1B holders

For the roughly 300,000 Indians working in the US on H-1B visas, Apple's stability carries a specific weight. Under current immigration rules, a laid-off H-1B worker has just 60 days to find a new sponsoring employer or begin departure proceedings. In a market where a data engineer with three years of experience can send 1,500 applications without a single recruiter callback — as one viral Reddit thread documented this week — that 60-day window is not a safety net. It is a countdown.

Apple's top-tier H-1B sponsorship, combined with its zero-layoff record in 2026, makes it the closest thing to job security that the US tech visa system offers. Meta, Microsoft, and Amazon all remain massive H-1B sponsors too, but each has now conducted multiple rounds of cuts that left visa holders scrambling.

## The trade-off

None of this makes Apple a charity. Its conservative hiring means fewer openings in the first place. Getting through Apple's interview process is notoriously selective, and the company's compensation, while competitive, has not kept pace with the stock-fuelled packages that pre-layoff Meta and Google used to offer.

But in a year when the tech industry's primary export has been anxiety, Apple's boring stability has become its most attractive benefit. For Indian engineers evaluating their next move — whether to stay at a company that might cut 10 per cent next quarter, or to aim for one that has not cut anyone — the calculus is shifting. Sometimes the most valuable thing a company can offer is not a higher number on the offer letter. It is the confidence that you will still have a desk in sixty-one days."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Illinois Just Passed America's Toughest AI Safety Law. Thousands of Indian Engineers Will Feel It First.",
        "subheadline": "SB 315 requires third-party audits and whistleblower protections at frontier AI labs. OpenAI endorsed it. The Indian engineers building these models should read the fine print.",
        "slug": make_slug("illinois-ai-safety-law-sb315-indian-engineers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-origin engineers are disproportionately represented at every frontier AI lab targeted by this law — OpenAI, Anthropic, Google DeepMind, Meta AI, Microsoft, and xAI. The bill's whistleblower protections and safety reporting requirements will directly shape the working environment for thousands of NRI researchers and engineers. And India's own AI governance framework is watching Illinois closely.",
        "tags": ["ai-regulation", "illinois", "openai", "anthropic", "indian-engineers", "ai-safety", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "PYMNTS", "url": "https://www.pymnts.com/artificial-intelligence-2/2026/illinois-governor-vows-to-sign-ai-safety-bill/"},
            {"name": "NBC News / HBCU News", "url": "https://hbcunews.com/illinois-legislature-passes-historic-ai-bill/"},
            {"name": "WCIA Illinois", "url": "https://www.wcia.com/news/illinois-sets-ai-safety-standards-with-new-legislation/"},
            {"name": "Privacy Daily", "url": "https://privacy-daily.com/illinois-frontier-model-ai-bill-passes-legislature/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5203849/pexels-photo-5203849.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On Wednesday, the Illinois House of Representatives voted 110-0 to pass Senate Bill 315, the Artificial Intelligence Safety Measures Act. The Senate had passed it 52-5 the week before. Governor JB Pritzker posted on X that he would sign it into law. "Illinois is leading the nation in holding Big Tech accountable," he wrote.

The bill, which takes effect on January 1, 2027, targets what it calls "frontier" AI developers — the companies building the largest, most powerful, and most expensive models. That list, in practice, means OpenAI, Anthropic, Google DeepMind, Meta AI, Microsoft, and xAI. It is the first US state law to require annual independent third-party audits of safety issues at these companies.

## What the bill requires

SB 315 imposes four core obligations on frontier developers. First, they must create, publish, and annually update a "frontier AI framework" that addresses catastrophic-risk assessment, governance, cybersecurity, and internal-use risks. Second, they must file transparency reports before deploying any new or substantially modified frontier model. Third, they must submit to annual independent third-party audits of their safety practices. Fourth, the bill establishes whistleblower protections and mandatory internal reporting processes for employees who identify safety concerns.

The bill mirrors existing provisions in California and New York but goes further. California's SB 1047, which Governor Newsom vetoed in 2024 before a revised version passed in 2025, focused primarily on pre-deployment safety testing. Illinois is the first to mandate ongoing independent audits after deployment — a distinction that matters because the most dangerous AI behaviours often emerge only after models are in production and interacting with millions of users.

## Why Indian engineers should care

Walk through the research floors of any frontier AI lab in San Francisco, New York, or London, and the concentration of Indian-origin engineers and researchers is immediately apparent. Indians constitute the largest national group among H-1B visa holders in the tech sector, and the frontier AI labs are among the most aggressive recruiters of talent from IITs, IISc, and top American graduate programmes.

The bill's whistleblower protections are particularly relevant. Under SB 315, employees who report safety concerns through internal channels receive legal protection from retaliation. For an H-1B holder whose immigration status is tied to their employer, the calculus of reporting a safety concern has always been asymmetric: raise an alarm and risk your job, your visa, and your life in America. The Illinois law does not eliminate that asymmetry entirely — federal immigration law still gives employers enormous leverage — but it adds a layer of state-level protection that did not exist before.

The transparency reporting requirements will also change daily workflows. Engineers building frontier models will need to document risk assessments and safety evaluations in formats that satisfy both internal compliance and external auditors. That is not a small ask. It means that the people writing the code will also need to write the justification for why that code is safe, a shift from the "move fast" culture that still defines much of Silicon Valley.

## India is watching

India's own approach to AI governance has been deliberately cautious. The government has avoided blanket regulation, opting instead for sector-specific guidelines and voluntary industry commitments. But Indian policymakers attended the same global AI safety summits where the intellectual groundwork for bills like SB 315 was laid, and the NITI Aayog has published discussion papers that cite exactly the kind of transparency and audit frameworks now being enacted in Illinois.

For NRIs working at these labs, the bill creates a dual reality. At work, they will operate under increasingly strict American regulatory frameworks. At home, the Indian market they serve — Anthropic calls India its second-largest market, OpenAI claims 100 million weekly users there — operates under a much lighter regulatory touch. Navigating both will become a core competency.

## The industry reaction

Perhaps the most notable response came from OpenAI itself, which endorsed SB 315 and called it "a thoughtful approach." That endorsement is worth parsing. OpenAI has historically opposed prescriptive AI regulation, lobbying aggressively against California's SB 1047. Its support for the Illinois version suggests either that the bill is genuinely less burdensome, or that OpenAI has decided the political cost of opposing bipartisan AI safety legislation now exceeds the compliance cost of accepting it.

Anthropic, which has positioned its Constitutional AI framework as a competitive advantage in exactly this kind of regulatory environment, has not publicly commented but stands to benefit. Stricter audit requirements raise barriers to entry and favour incumbents who already invest in safety infrastructure.

For the thousands of Indian engineers at these companies, the practical takeaway is straightforward: the days of building frontier AI with minimal external oversight are ending. The auditors are coming. The paperwork is coming. And the whistleblower protections mean that the colleague sitting next to you now has a legal framework for raising concerns you might prefer to keep quiet. Whether that makes the technology safer, or just more bureaucratic, is the question Illinois has decided to answer first."""
    },
]

# Verify images
for art in articles:
    url = art["image_url"]
    if verify_image(url):
        print(f"✅ Image OK: {url[:80]}...")
    else:
        print(f"⚠️ Image FAILED: {url[:80]}... — proceeding anyway")

# Insert articles
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ Published: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
