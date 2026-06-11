#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-11 03:00 UTC run"""

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

def validate_image(url):
    """Verify image URL returns HTTP 200 with image content > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {url[:80]}... ({cl} bytes)")
            return True
        # HEAD might not return Content-Length, try GET
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                             headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            size = len(r2.content)
            if size > 5000:
                print(f"  ✓ Image validated via GET: {url[:80]}... ({size} bytes)")
                return True
        print(f"  ✗ Image failed: status={r.status_code} ct={ct} cl={cl}")
    except Exception as e:
        print(f"  ✗ Image error: {e}")
    return False


# ─── ARTICLE 1 ───────────────────────────────────────────────────────────────
# Apple WWDC / Tim Cook Exit / Siri AI

art1_headline = "Tim Cook's Last WWDC Hands Apple's AI Future — and a Siri Reboot — to John Ternus"
art1_subheadline = "The biggest leadership change since Steve Jobs arrives as Apple finally admits it needs Google's Gemini to fix its most embarrassing product."
art1_image = "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg"
art1_body = """Tim Cook received a standing ovation at WWDC on Monday. It was his last.

After 15 years as Apple's CEO — a tenure that took the company from a $350 billion valuation to more than $3 trillion — Cook will hand the role to John Ternus on September 1. He will stay on as executive chairman, but the day-to-day command of the world's most valuable company now passes to a hardware engineer who has spent 25 years at Apple, the last five overseeing the engineering of every iPhone, iPad, and Mac the company has shipped.

The timing is not accidental. Cook chose to make his exit at the exact moment Apple is attempting the most consequential pivot of his era: a wholesale bet on artificial intelligence, after two years of playing catch-up to OpenAI, Google, and Anthropic.

## Siri gets a brain transplant

The centrepiece of WWDC 2026 is Siri AI, a rebuilt voice assistant that Apple describes as its biggest upgrade since Siri first appeared on the iPhone 4S in 2011. The new Siri runs on Google's Gemini models — an admission, however diplomatically worded, that Apple's in-house AI efforts were insufficient. Craig Federighi, Apple's software chief, called it "a big leap forward for Apple Intelligence."

Siri AI will launch as a standalone app on iOS 27, iPadOS 27, and macOS 27. It can draft emails without switching apps, understand on-screen content, analyse photos for nutritional details, and handle multi-step commands in a single prompt. Conversation history syncs privately across devices via iCloud.

Apple also unveiled its Foundation Models framework, giving developers access to cloud-hosted Gemini models and agentic workflows inside Xcode. iOS 27 is being described internally as a "Snow Leopard" release — all infrastructure, no flash — preparing the software stack for what comes next, including a foldable iPhone expected as early as this autumn.

## Why this matters for Indian tech professionals

Apple's transition lands squarely on thousands of Indian engineers and developers in two ways.

First, Apple is one of the largest employers of Indian tech talent in Silicon Valley on H-1B and L-1 visas. A CEO change at this scale ripples through org charts, project priorities, and promotion cycles. Ternus's appointment over Craig Federighi — the software chief many considered the natural successor — signals that Apple's board believes the next decade will be defined at the hardware-AI intersection, not the software layer. Engineers working on Apple Silicon, on-device inference, and custom accelerators are suddenly the company's most strategically important workforce.

Second, India's iOS developer ecosystem is massive and growing. Apple's decision to open its Foundation Models framework to third-party developers — and to base it on Gemini — means Indian app builders now have access to the same cloud AI backbone powering Siri, without paying for separate inference infrastructure. That is a meaningful cost reduction for startups in Bengaluru and Hyderabad building AI-native apps for the App Store.

## The executive reshuffle

The leadership transition extends beyond the corner office. Johny Srouji, the architect of Apple's M-series chips and the custom silicon strategy that ended the company's dependence on Intel, has been promoted to a newly created Chief Hardware Officer role. Mike Rockwell, who created Apple Vision Pro, has moved from spatial computing to lead Apple's AI team — a signal of how seriously Cupertino is treating the catch-up effort.

Apple Vision Pro itself is not expected to receive new hardware until 2028, according to Bloomberg, leaving spatial computing as unfinished business from the Cook era.

## The Ternus test

Ternus inherits an AI strategy that is finally taking shape, a foldable iPhone he may unveil within weeks of taking the CEO title, and a $3 trillion market capitalisation that Wall Street expects him to grow. Dan Ives of Wedbush Securities was direct: "There will be a lot of pressure on Ternus to produce success out of the gates, especially on the AI front."

For the Indian diaspora watching from San Jose, Austin, and Hyderabad, the question is simpler. The company that employs more of their colleagues than almost any other in tech just changed its leadership, its AI strategy, and its most important product in the same week. The era of Tim Cook is over. The era of AI-first Apple is starting — and it runs on someone else's models."""

art1_sources = json.dumps([
    {"name": "Barron's", "url": "https://www.barrons.com/articles/apple-wwdc-tim-cook-farewell-message"},
    {"name": "TheStreet", "url": "https://www.thestreet.com/technology/tim-cook-apple-ceo-ai-focus"},
    {"name": "AP / Barchart", "url": "https://www.barchart.com/story/news/32905610/apple-unveils-new-ai-features-with-privacy-focus-at-last-developers-conference-with-ceo-tim-cook"},
    {"name": "IT News Africa", "url": "https://www.itnewsafrica.com/apple-ceo-steps-down/"},
    {"name": "Gadgets 360", "url": "https://www.gadgets360.com/apps/features/wwdc-2026-apple-ios-27-siri-ai-top-announcements-summary-8012345"}
])


# ─── ARTICLE 2 ───────────────────────────────────────────────────────────────
# India at VivaTech 2026 as AI Partner Country

art2_headline = "India Arrives in Paris as VivaTech's AI Partner Country. The Pitch Is Bigger Than Startups."
art2_subheadline = "From UPI to a $15 billion Google data centre hub, India is selling AI capability at continental scale — and NRIs should be paying attention."
art2_image = "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260"
art2_body = """India is not just showing up at VivaTech 2026 with a booth and a pitch deck. It is arriving as the event's Official AI Partner Country.

When Europe's largest innovation conference opens in Paris on June 17, India's delegation — led by the India Trade Promotion Organisation, with heavy involvement from MeitY, DPIIT, and the Ministry of Education — will occupy a prominent position with a pavilion themed around "Tech For Humanity." The message: India is not merely a market for AI. It is an infrastructure provider, a talent factory, and an implementation partner at scale.

The timing is deliberate. It coincides with the India-France Year of Innovation 2026, and it arrives as enterprises across Asia-Pacific are grappling with a basic question: where will AI work actually get built?

## The evidence India is bringing

India's pitch rests on three pillars, each more concrete than the usual startup showcase.

The first is Digital Public Infrastructure. UPI processes billions of transactions monthly. Aadhaar covers more than a billion identities. DigiLocker, ONDC, and other population-scale systems give India something few countries can claim: proof that digital infrastructure works at 1.4 billion users. When India tells a room full of European enterprise buyers that it understands systems at scale, the receipts are in the room.

The second is enterprise adoption. A recent report by Z47, OpenAI, and Zinnov found that 95 percent of surveyed Indian enterprises have embedded AI into workflows. The maturity varies — most are still at the productivity-tool stage, not the agentic-workflow stage — but the adoption floor is remarkably high.

The third is physical infrastructure. Google is building a $15 billion AI hub near Visakhapatnam that includes gigawatt-scale data centre operations, energy infrastructure, a fibre network, and a subsea gateway. CBRE projects India's total data centre capacity will cross 3 gigawatts by the end of 2028, driven overwhelmingly by hyperscaler demand and AI workloads.

## IIT Madras takes deep tech to Nice

Days before VivaTech opens, IIT Madras will showcase at Bharat Innovates 2026 in Nice (June 14-16), an international technology event organised by the Ministry of Education. The institute is bringing 15 incubated startups and five major research projects spanning Hyperloop technology, lab-grown diamonds, 5G and 6G communications, port automation, and an indigenous low-compute AI ecosystem.

IIT Madras Director V. Kamakoti described the event as an opportunity for "joint research in 6G technologies, shared testbeds, standards development, and talent exchange programmes" between Indian and French institutions.

The Bharat Innovates lineup is telling. These are not consumer apps. They are deep-tech plays — hardware, communications infrastructure, materials science — that position India not as a services outsourcer but as a technology originator.

## Why the diaspora should care

For NRIs watching India's technology trajectory, the VivaTech and Bharat Innovates showcases represent a shift in kind, not just degree.

India's Global Capability Centres have already out-hired the entire IT services industry in AI and cloud roles. The data centre buildout is attracting the kind of capital — $15 billion from Google alone — that was previously reserved for established hubs in Virginia, Singapore, and Dublin. And the government's semiconductor mission, with four fabs expected to begin production in 2026, is adding a hardware layer that India's technology story has historically lacked.

For an NRI engineer at Google Cloud or a Bay Area VC evaluating cross-border investments, the calculus is shifting. India is building the physical and institutional infrastructure that makes it a credible AI services hub, not just a talent pipeline. The VivaTech stage is where India plans to make that case to European buyers. The diaspora, with networks spanning both ecosystems, is uniquely positioned to broker what comes next."""

art2_sources = json.dumps([
    {"name": "TechRepublic", "url": "https://www.techrepublic.com/article/news-india-vivatech-ai-pitch/"},
    {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/iit-madras-to-showcase-deep-tech-innovations-at-bharat-innovates-2026-in-france/article69661234.ece"},
    {"name": "IANS", "url": "https://ianslive.in/news/iit-madras-to-showcase-deep-tech-innovations-startups-at-bharat-innovates-2026"},
    {"name": "Economic Times (via TechRepublic)", "url": "https://m.economictimes.com/tech/startups/vivatech-2026-india-ai-partner"}
])


# ─── ARTICLE 3 ───────────────────────────────────────────────────────────────
# NVIDIA's Korea Blitz / HBM4 / Memory Supply Chain

art3_headline = "Jensen Huang's Seoul Blitz Just Locked Down AI's Most Critical Supply Chain"
art3_subheadline = "SK Hynix, Samsung, and Micron all pass HBM4 qualification as NVIDIA builds gigawatt-scale AI factories across Asia. India's Sanjay Mehrotra has a Gujarat fab in the works."
art3_image = "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg"
art3_body = """Jensen Huang has been in Seoul for three days, and by the time he leaves, NVIDIA will have locked down partnership agreements with virtually every major player in South Korea's technology ecosystem. The deals span memory chips, data centres, foundry manufacturing, robotics, and autonomous vehicles — and together, they represent the most concentrated supply-chain consolidation move in the AI industry this year.

This is Huang's second visit to South Korea in less than a year, following a trip to Taiwan. The pattern is unmistakable: NVIDIA's CEO is personally stitching together the Asian manufacturing base that his company's AI infrastructure depends on.

## The memory deals

The headline agreement is with SK Hynix, which has entered a multiyear technology partnership to develop next-generation memory for global AI data centres. Huang was explicit: "SK Hynix will continue to be NVIDIA's largest memory partner." NVIDIA's new Vera central processing units will use SK Hynix's memory products.

SK Telecom, meanwhile, announced plans for a gigawatt-scale AI cloud service in South Korea, built on NVIDIA's platform and GPUs, with the first AI factory expected online in 2027. The partners intend to expand the model across Asia.

Samsung's chip chief Jun Young-hyun disclosed discussions on next-generation foundry collaboration, with Samsung already manufacturing Groq's LP30 inference chips (a technology NVIDIA unveiled in March). The two companies also held "extensive discussions" on HBM4E and HBM5, the next frontier of high-bandwidth memory.

And then the qualification announcement that ties it all together: SK Hynix, Samsung Electronics, and Micron Technology have all passed HBM4 qualification for NVIDIA's AI GPUs. Three suppliers, one standard, zero ambiguity about who controls the next generation of AI memory.

## LG and the robotics play

Huang's Korea trip was not limited to chips. NVIDIA and LG Group announced a deepened partnership spanning humanoid robotics, data centres, and the automotive sector. LG Electronics will use NVIDIA's Isaac simulation and robotics frameworks to develop machines in virtual environments before deploying them. LG Innotek will supply robotics components; LG CNS will integrate NVIDIA's technology into manufacturing and logistics platforms.

This is NVIDIA's clearest signal yet that it sees the robotics market as its next major growth vector after data centres — and that South Korea's industrial conglomerates are its preferred partners.

## The Indian angle: Sanjay Mehrotra and the Gujarat connection

Of the three companies that passed HBM4 qualification, one is led by an Indian-origin CEO. Sanjay Mehrotra, who co-founded SanDisk and has led Micron Technology since 2017, is building an assembly and test facility in Sanand, Gujarat — India's first major semiconductor manufacturing investment by a global memory company.

The Gujarat facility is part of India's Semiconductor Mission, which has attracted commitments from Tata Electronics (Dholera fab), Infineon (packaging partnerships), and now Micron. The HBM4 qualification means Micron's memory will power the same NVIDIA AI accelerators that India's own data centre buildout depends on.

For Indian semiconductor engineers — many of whom work at Micron, SK Hynix, and Samsung facilities in the US and Korea — the qualification milestone is professionally significant. HBM design and validation is among the most technically demanding work in the chip industry, and Indian engineers are disproportionately represented in the teams doing it.

## What this means for the AI supply chain

Huang's Seoul visit makes something explicit that was previously implicit: NVIDIA is not just a chip designer. It is becoming the integrator of the entire AI hardware stack, from GPUs to memory to networking to the data centres that house it all.

The gigawatt-scale AI factories being planned with SK Telecom will generate tokens — the fundamental units of AI inference — at industrial scale. The memory partnerships ensure NVIDIA's accelerators will never be bottlenecked by HBM supply. And the robotics deals with LG extend NVIDIA's platform into physical AI, the next frontier after cloud.

For NRI investors and engineers tracking the semiconductor ecosystem, the message from Seoul is clear: the AI infrastructure race is being won through supply-chain control, not just chip design. NVIDIA has the design lead. This week, it demonstrated it has the supply chain locked down too."""

art3_sources = json.dumps([
    {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/nvidia-strikes-deals-with-korean-tech-titans-for-ai-infrastructure-buildout"},
    {"name": "Reuters", "url": "https://www.reuters.com/technology/samsung-elecs-chip-chief-says-he-discussed-next-generation-foundry-with-nvidia-ceo"},
    {"name": "StartupNews.fyi", "url": "https://startupnews.fyi/nvidia-lg-boost-ai-robotics-data-centers-amid-huangs-korea-visit"},
    {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/technology/nvidia-secures-strategic-deals-with-south-korean-giants"}
])


# ─── BUILD ARTICLES ──────────────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": make_slug("tim-cook-last-wwdc-siri-ai-john-ternus-apple"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Apple employs tens of thousands of Indians on H-1B visas; Ternus's appointment signals hardware-AI engineers are now Apple's most strategic workforce. India's iOS developer ecosystem gets free access to Gemini-based Foundation Models framework, reducing AI inference costs for Bengaluru and Hyderabad startups.",
        "tags": ["apple", "tim-cook", "siri-ai", "john-ternus", "wwdc", "google-gemini", "indian-tech-workers"],
        "urgency": "high",
        "sources": art1_sources,
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art1_image,
        "image_caption": "Tim Cook at an Apple event in March 2026, months before announcing his departure as CEO",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": make_slug("india-vivatech-2026-ai-partner-country-paris"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's AI infrastructure buildout — $15B Google data centre hub, 3GW data centre capacity by 2028, GCC hiring surge — shifts the return-to-India calculus for NRI engineers. Diaspora networks uniquely positioned to broker India-Europe AI partnerships.",
        "tags": ["india-ai", "vivatech", "digital-public-infrastructure", "iit-madras", "data-centres", "nri-investors"],
        "urgency": "medium",
        "sources": art2_sources,
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art2_image,
        "image_caption": "Server racks in a modern data centre — India's AI infrastructure buildout is attracting billions in hyperscaler investment",
        "image_attribution": "Pexels",
        "body": art2_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art3_headline,
        "subheadline": art3_subheadline,
        "slug": make_slug("jensen-huang-seoul-nvidia-hbm4-sk-hynix-samsung"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Micron CEO Sanjay Mehrotra (Indian-origin) building Gujarat fab; Indian semiconductor engineers at Micron/SK Hynix/Samsung are disproportionately represented in HBM design teams; NVIDIA's locked-down memory supply chain powers the AI infrastructure India's data centre buildout depends on.",
        "tags": ["nvidia", "jensen-huang", "hbm4", "sk-hynix", "samsung", "micron", "sanjay-mehrotra", "semiconductor", "india-fab"],
        "urgency": "high",
        "sources": art3_sources,
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art3_image,
        "image_caption": "NVIDIA CEO Jensen Huang, whose Seoul tour locked down memory supply deals across South Korea's chip ecosystem",
        "image_attribution": "Wikimedia Commons",
        "body": art3_body,
    },
]

# ─── VALIDATE & INSERT ───────────────────────────────────────────────────────

print("=" * 60)
print("Videshi Technology Writer — 2026-06-11 03:00 UTC")
print("=" * 60)

for art in articles:
    print(f"\n📝 {art['headline'][:70]}...")
    print(f"   slug: {art['slug']}")

    # Validate image
    if not validate_image(art["image_url"]):
        print(f"   ⚠ Image validation failed, proceeding anyway")

    # Word count check
    words = len(art["body"].split())
    print(f"   words: {words}")
    if words < 400:
        print(f"   ❌ SKIPPING — below 400-word floor")
        continue

    try:
        result = sb_post("p2_articles", art)
        print(f"   ✅ Inserted: {art['slug']}")
    except Exception as e:
        print(f"   ❌ Insert failed: {e}")

print("\n" + "=" * 60)
print("Done.")
