#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-30 03:00 UTC batch"""
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


# ── ARTICLE 1: Nvidia N1X PC Chip + Computex ──────────────────────────────

art1_body = """Jensen Huang has never been subtle. But on Friday, even by his standards, the Nvidia CEO dropped a hint so transparent it barely qualifies as one.

"A new era of PC." That was the message posted simultaneously by Nvidia, Microsoft, and Arm on X, accompanied by latitude-longitude coordinates pointing to the Taipei Music Center — the venue where Huang will deliver his Computex keynote on June 1. The coordinated teaser all but confirms what the industry has anticipated for months: Nvidia is about to enter the consumer laptop chip market.

## The N1X: Blackwell Comes to Your Backpack

The chip in question is the N1X, a system-on-chip rumored to pack roughly 20 Arm-based CPU cores alongside an integrated GPU built on Nvidia's Blackwell architecture — the same family that powers its data center monsters. Performance estimates put the integrated graphics in RTX 5070 territory, which would be extraordinary for a chip that doesn't need a discrete GPU.

Dell, Lenovo, and ASUS are reportedly preparing laptops around the N1X, with devices expected to hit shelves by late 2026. The original timeline was 2025, but Nvidia delayed the launch to iron out software compatibility — a tacit acknowledgment that Windows on Arm still has rough edges.

Microsoft's participation in the teaser is the more telling signal. Redmond has been pushing Windows on Arm through its Qualcomm partnership (the Snapdragon X series already powers Copilot+ PCs), but adding Nvidia to the mix would transform a two-horse race into a genuine platform war against Intel and AMD's x86 dominance.

## $150 Billion a Year — In Taiwan Alone

The PC chip reveal comes amid Nvidia's broader show of force in Taiwan. Earlier this week, Huang announced that Nvidia would spend up to $150 billion annually with Taiwanese suppliers — up from roughly $100 billion today. He called Taiwan "the epicentre of the AI revolution" at a launch event for Nvidia's planned Taiwan headquarters, which will break ground this year and aims to be operational by 2030.

The spending figure is staggering. It exceeds India's entire IT services sector revenue ($315 billion annually) if sustained over just two years. It also represents a pointed geopolitical statement: despite escalating US-China tensions over Taiwan, Nvidia is doubling down on the island rather than diversifying away from it.

TSMC CEO C.C. Wei, Foxconn Chairman Young Liu, and Quanta Computer Chairman Barry Lam all met with Huang during his pre-Computex rounds. Taiwan's server exports have surged from $571 million in 2017 to $60 billion last year — a trajectory that Nvidia's investment will only accelerate.

## Why Indian Engineers Should Pay Attention

The N1X matters for the Indian tech diaspora on multiple levels. First, the practical: if Nvidia ships a laptop chip with RTX 5070-class graphics and competitive battery life, it changes the calculus for every engineer running local AI workloads, training models on their machine, or simply wanting a laptop that handles both code and CUDA without a discrete GPU. That demographic skews heavily Indian at companies like Google, Microsoft, and Meta.

Second, the supply chain: MediaTek — which is designing custom AI chips and recently doubled its data center revenue forecast to $2 billion — is reportedly building custom silicon for Google using Intel's EMIB packaging. The N1X reportedly uses a MediaTek-designed CPU complex, putting Indian engineers at MediaTek's growing design centers directly in the product pipeline.

Third, the Qualcomm rivalry: Qualcomm's San Diego headquarters and its Hyderabad engineering center employ thousands of Indian engineers working on the Snapdragon X series. An Nvidia entry into the same market would intensify competition — good for innovation, but potentially disruptive for teams that bet their roadmap on being the only serious Arm contender in Windows PCs.

Huang's Monday keynote at the Taipei Music Center begins at 8 PM Pacific on Sunday — prime time for the Bay Area's engineering community. Whatever he unveils, the PC will never quite look the same again."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Nvidia Just Teased a PC Chip That Could Reshape Every Engineer's Laptop. Indian Tech Workers Should Watch Monday's Keynote.",
    "subheadline": "A coordinated social media blitz from Nvidia, Microsoft, and Arm all but confirms the N1X — a Blackwell-based laptop chip — will debut at Computex. Meanwhile, Huang pledges $150 billion a year to Taiwan.",
    "slug": make_slug("nvidia-n1x-pc-chip-computex-taiwan-150-billion"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian engineers at FAANG companies who do local AI/ML work stand to gain from Nvidia laptop chips with integrated RTX-class graphics. MediaTek and Qualcomm — both major employers of Indian engineers — are directly affected by this market entry.",
    "tags": ["nvidia", "computex", "arm", "pc-chips", "taiwanese-supply-chain", "indian-engineers"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Barron's", "url": "https://www.barrons.com/articles/nvidia-pc-chip-gtc-computex"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-taiwan-expanding-role-ai-computex-2026-05-29/"},
        {"name": "TweakTown", "url": "https://www.tweaktown.com/news/nvidia-microsoft-new-era-pc-computex/"},
        {"name": "CryptoBriefing", "url": "https://cryptobriefing.com/nvidia-microsoft-arm-n1x-laptop-processors/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
    "body": art1_body
}


# ── ARTICLE 2: TSMC Energy Efficiency Pivot ──────────────────────────────

art2_body = """For half a century, the semiconductor industry obeyed one commandment: make the transistor smaller. Moore's Law was less a law than a lifestyle — shrink, pack, repeat. It made chips faster, cheaper, and more powerful with each generation. It worked beautifully. Until AI came along and started melting the data centers.

On Thursday, TSMC's Senior Vice President of Business Development Kevin Zhang said what the entire chip industry has been thinking but few have articulated so bluntly: energy efficiency, not computing power, is now the primary constraint shaping chip design.

"The area customers most want improvement in is energy efficiency," Zhang told reporters at a conference in Amsterdam. "This is true across the board, whether you are the edge guy, smartphone, mobile, IoT application, or high-performance AI data center."

## The Physics Problem Nobody Can Outrun

The numbers explain the panic. AI data centers now consume electricity at rates that would have seemed absurd five years ago. A single Nvidia H100 GPU draws around 700 watts. Multiply that across hundreds of thousands of chips in a hyperscaler's fleet, and you get power bills that rival small cities. Microsoft, Google, Amazon, and Meta are all scrambling to secure power — signing nuclear deals, leasing gas plants, and lobbying for grid upgrades.

TSMC, which manufactures AI chips for virtually every major player (Nvidia, AMD, Google, Amazon, Meta, Microsoft), is responding by reorienting its entire technology roadmap. Zhang said transistor density improvements remain important, but the company is increasingly leaning on advanced packaging, chip stacking, and photonics — technologies that boost performance without proportionally increasing power consumption.

The target is ambitious: TSMC expects its A14 chip generation, due around 2028, to deliver over 20% higher computing performance while cutting power consumption by up to 30% compared to its current N2 technology.

## When China Zigs, TSMC Zags

The timing is pointed. Earlier this week, Huawei unveiled what it called the "Tau Scaling Law" — an alternative framework to Moore's Law that focuses on system-level performance gains through chip stacking and integration rather than transistor shrinkage. Huawei claims its approach could achieve transistor density equivalent to 1.4 nanometers by 2031, potentially matching TSMC's expected 2028 timeline without access to the advanced lithography machines (specifically ASML's EUV tools) that US sanctions have blocked.

Two competing visions of the semiconductor future, then: TSMC betting on energy-efficient miniaturization with the world's best manufacturing tools, and Huawei trying to engineer around sanctions through architectural innovation. For India — which is building its semiconductor ecosystem from scratch — the question is which path to follow.

## India's Five Fabs Face a Moving Target

India now has five announced semiconductor facilities at various stages of development: Tata Electronics in Dholera (with ASML equipment), Micron in Gujarat, Intel's substrate plant in Odisha, CG Semi, and the Tata-PSMC packaging facility. Collectively, they represent India's most ambitious industrial policy bet in decades.

But TSMC's pivot complicates the picture. If the cutting edge of chipmaking is moving from pure lithographic shrinkage toward advanced packaging, photonics, and 3D chip stacking, India's fab investments need to account for that shift. Advanced packaging, in particular, is an area where India could compete — it requires precision manufacturing but not necessarily the multi-billion-dollar EUV lithography that only ASML produces.

For the estimated 30,000-plus Indian engineers working at semiconductor companies in the US — at Intel, Qualcomm, AMD, Texas Instruments, Broadcom, and TSMC's own Arizona facility — this shift reshapes career trajectories. Power management, thermal design, and packaging engineering are becoming as valuable as traditional logic design. Engineers with expertise in these areas will find themselves increasingly in demand, whether they stay in the US or consider roles at India's emerging fab ecosystem.

The era of "just make the transistor smaller" is ending. What replaces it will be messier, more interdisciplinary, and potentially more accessible to countries like India that are late to the lithography game but early enough to the packaging revolution."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "TSMC Says the Chip Industry's Fifty-Year Playbook Is Obsolete. Energy, Not Speed, Now Drives Design.",
    "subheadline": "The world's largest chipmaker says AI's insatiable power appetite is forcing a fundamental shift — from shrinking transistors to cutting watts. India's five fabs face a moving target.",
    "slug": make_slug("tsmc-energy-efficiency-chip-design-ai-india-fabs"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "30,000+ Indian semiconductor engineers in the US face career trajectory shifts as the industry pivots from pure lithography to packaging, thermal, and power engineering. India's fab ecosystem must adapt to a moving target where advanced packaging matters as much as node shrinkage.",
    "tags": ["tsmc", "semiconductors", "energy-efficiency", "india-fabs", "chip-design", "ai-infrastructure"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/energy-use-forcing-rethink-ai-chip-design-tsmc-says-2026-05-29/"},
        {"name": "TrendForce", "url": "https://www.trendforce.com/news/2026/05/29/tsmc-energy-efficiency-ai-chip-design/"},
        {"name": "Reuters (Huawei)", "url": "https://www.reuters.com/technology/huawei-bets-speed-over-shrinking-transistors-2026-05-29/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art2_body
}


# ── ARTICLE 3: India GCC $100B Transformation ──────────────────────────

art3_body = """There is a number that should make every Indian technology professional pause: 2,100. That is how many global capability centers now operate in India, employing 2.36 million people and generating nearly $100 billion in annual revenue. India is, by a wide margin, the world's largest GCC hub.

But a series of conversations at the Reuters India Summit in Bengaluru this week revealed something more uncomfortable: the model that built this empire is breaking, and AI is holding the hammer.

## From Back Office to Boardroom

The original GCC pitch was straightforward — skilled talent at scale, at low cost. American and European companies sent their routine IT operations to Bengaluru, Hyderabad, and Pune. Indian engineers maintained systems, wrote code, and ran processes for a fraction of what it would cost in San Francisco or London.

That story is over. Executives at the summit described a fundamentally different reality. GCCs are no longer back-office support units but integrated hubs that mirror their parent companies. They manage everything from product development to R&D to corporate affairs. Microsoft India head Puneet Chandok credited the country's 27 million GitHub developers and digital public infrastructure. Target runs its Bengaluru operation as an "integrated headquarters." IBM calls its India center a "macrocosm" of the global enterprise.

American Airlines is doubling its Hyderabad tech hub to 800 people by early 2027, focused on software engineering, AI, and cybersecurity. Southwest Airlines is expanding its Hyderabad GCC to 1,000 employees. JPMorgan, Walmart, McDonald's, Nvidia, and Eli Lilly have all expanded India technology operations.

Indian GCCs hit $98.4 billion in revenue last fiscal year — reaching industry projections four years ahead of schedule.

## The AI Paradox: More Output, Fewer People

Here is where the story gets complicated. AI is simultaneously making GCCs more valuable and threatening to hollow them out.

Kimberly-Clark's India-built AI platform cut content creation time from 24 days to two hours. Daimler Truck's Indian engineers are "generating IP faster" using AI tools. Epsilon, the Publicis marketing arm, is delivering dramatically more work without proportional hiring increases.

"What has changed is the amount of work that we are delivering, the new responsibilities that we have picked up," said Pratik Nath, Epsilon India's managing director. The subtext: same headcount, vastly more output.

Lalit Ahuja, CEO of ANSR (which helps firms build GCCs), put it more directly: growth in India from a people standpoint will taper over time. "Companies are hiring fewer people, just as a matter of abundant caution."

The implications cascade. India's $315 billion IT sector — dominated by services giants TCS, Infosys, Wipro, and HCL — is already feeling the squeeze. TCS shed 25,000 jobs in nine months while doubling fresher intake. OpenAI's new services venture is explicitly targeting the work that Indian IT companies do. Nasscom's own forecast for FY27 projects only 1.5% to 3.5% revenue growth in constant currency terms.

## Patent Filings and the Capability Ladder

There is a counterargument, and it is not trivial. As AI reduces routine work, GCCs are climbing the value chain into areas that are harder to automate and more valuable to their parent companies.

Patent filings in India rose 11.3% to over 90,000 in fiscal 2024, with nearly half from multinational companies. Executives say this understates GCC contributions, since much of the intellectual property generated in India is filed through parent entities in the US and Europe. Daimler Truck's India head predicted AI would "accelerate" patent creation. Novo Nordisk's Bengaluru center now plays a central role in global drug launches — including the company's recently launched oral obesity pill in the United States.

This is the new GCC value proposition: not cheap labor, but integrated capability. Not cost savings, but intellectual property.

## What This Means for the Diaspora

For the roughly 400,000 Indian technology professionals in the United States, this shift reconfigures the career map in both directions.

Returning to India no longer means taking a downgrade. GCC leadership roles — running product development for a Fortune 500 company from Bengaluru — now carry compensation, scope, and strategic weight that would have been unthinkable a decade ago. An Indian-American VP of Engineering at a San Francisco startup might find a comparable role at Target India or Microsoft India with better purchasing power and closer proximity to family.

But the ground is also shifting underfoot. If AI-augmented GCCs can do more with fewer people, the total number of high-paying tech jobs in India may plateau even as revenue grows. The winners will be specialists — in AI, cybersecurity, product management, and domain expertise — rather than generalists who built their careers on volume coding.

Bengaluru's civic constraints add another wrinkle. Congestion, rising costs, and intense talent competition are pushing some GCCs to explore tier-two cities. For NRIs evaluating a return, the destination matters as much as the job.

The $100 billion GCC empire is not collapsing. But it is transforming from a labor arbitrage machine into something more complex, more selective, and more consequential. The engineers and managers who navigate that transition — whether from Mountain View or Marathahalli — will define India's next chapter in global technology."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's $100 Billion GCC Empire Is Being Rebuilt by AI. The Old Model Won't Survive.",
    "subheadline": "With 2,100 centers and 2.36 million workers, India's global capability centers generate more revenue than most countries' tech sectors. But AI is reshaping what these hubs do — and how many people they need.",
    "slug": make_slug("india-gcc-100-billion-ai-transformation-diaspora"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Directly affects 400,000+ Indian tech professionals in the US evaluating career moves. GCC leadership roles now offer Fortune 500 scope from Bengaluru, but AI-driven productivity gains may plateau total headcount growth even as revenue grows.",
    "tags": ["gcc", "india-tech", "ai-disruption", "bengaluru", "outsourcing", "career-decisions"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/india-gcc-model-shifts-cost-capability-2026-05-27/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/global-firms-bring-more-work-in-house-india-hubs-ai-2026-05-27/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/ai-turbocharge-patent-creation-india-tech-hubs-2026-05-28/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/global-firms-use-ai-india-hubs-ad-work-in-house-2026-05-29/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37088158/pexels-photo-37088158.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "body": art3_body
}

# ── Publish ──────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
