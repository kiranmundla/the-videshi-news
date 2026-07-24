#!/usr/bin/env python3
"""Immigration writer — 2026-06-07 08:00 UTC run."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


articles = [
    # ── Article 1: The K-Visa Gambit / Global Talent War ──
    {
        "id": str(uuid.uuid4()),
        "headline": "The K-Visa Gambit — China Built an H-1B Alternative and Indian Engineers Are Reading the Fine Print",
        "subheadline": "As Washington raises barriers, Beijing, Ottawa, and Berlin are rolling out the welcome mat for the very STEM workers America is pricing out — and the competition for Indian talent has never been this explicit.",
        "slug": make_slug("china-k-visa-global-talent-war-indian-engineers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian professionals on H-1B visas, who represent roughly 72% of all recipients, are now the most sought-after talent pool in a global bidding war. China's K-visa, Canada's Express Entry tweaks, and Germany's Chancenkarte all target the same frustrated engineer in Sunnyvale wondering whether waiting 128 years for a green card is the best career plan.",
        "tags": ["h1b", "k-visa", "china", "brain-drain", "global-talent", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
            {"name": "NBC News", "url": "https://www.nbcnews.com/news/china-woos-foreign-tech-talent"},
            {"name": "EqualOcean", "url": "https://equalocean.com/briefing/20250930230142587"},
            {"name": "USCIS Data", "url": "https://www.uscis.gov/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
        "image_caption": "An open passport displaying various visa stamps at an airport",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For decades, the talent pipeline ran in one direction. Indian engineers graduated, crammed for the GRE, landed at a US university, got an H-1B, and spent the next decade or two waiting for a green card. The system was creaky, undersized, and maddeningly slow — but it was the only serious game in town.

That monopoly is ending.

## Beijing Enters the Chat

In October 2025, China quietly launched the K-visa, a category explicitly designed to attract young foreign STEM graduates. The requirements are almost comically lax by American standards: a bachelor's degree in a STEM field from a recognised university, no employer sponsorship required, no lottery, no $100,000 fee. Holders can enter, reside, and work in China while Beijing sorts out the implementation details.

The timing was surgical. The K-visa announcement came weeks after the Trump administration slapped a $100,000 fee on new H-1B petitions — a move that effectively priced out the mid-tier IT services firms that had been the biggest pipeline for Indian workers entering the American labour market.

"The symbolism is powerful: while the US raises barriers, China is lowering them," Matt Mauntel-Medici, an Iowa-based immigration attorney, told reporters. "The timing couldn't be more exquisite."

Interest from India has been immediate. China is already seen as an increasingly appealing destination amid warming bilateral relations, and the K-visa removes the single biggest friction point for STEM professionals: the need for a job offer before you can even apply.

## The Competition Gets Crowded

China is not alone. A Brookings Institution report published this week documented the scale of what it called a "global talent poaching" response to American restrictions.

Canada has continued to refine its Express Entry system, which awards points for age, education, and work experience — no lottery, no employer sponsorship required for the initial application. Germany launched the Chancenkarte, or "Opportunity Card," a points-based job-seeker visa that lets qualified professionals move to Germany first and find work after. South Korea and New Zealand have relaxed their own skilled-migration rules.

The Brookings researchers put it bluntly: "Evidence suggests that increased American restrictions on H-1B visa holders may lead to greater offshoring from multi-national corporations, particularly to China, India, and Canada."

NVIDIA CEO Jensen Huang, whose company is one of the few tech giants still aggressively hiring H-1B workers, warned on the BG2 Pod that the $100,000 fee could set the bar "a little too high" for immigrants hoping to build careers in America. He described talent inflows as a "KPI for America's future."

## The Numbers That Should Worry Washington

The data trail is unambiguous. F-1 student visa issuances — the traditional entry point for the talent pipeline — fell 29% since 2023, according to Brookings. Over 1.2 million people sit in the employment-based green card queue, the vast majority of them Indian nationals. Wait times for EB-2 India are measured in decades, not years. The H-1B lottery now requires a $100,000 fee per petition and prioritises the highest-paid applicants, shutting out the early-career workers who were once the programme's bread and butter.

Meanwhile, 123,000 tech jobs have been cut in 2026 alone, with AI cited as the primary driver. For an Indian engineer laid off from a mid-level tech role, the 60-day grace period to find a new sponsor now comes with a backdrop of shrinking opportunity and ballooning cost.

## Why This Matters to the Diaspora

For the estimated 4.4 million Indian Americans, the K-visa gambit is not an abstract geopolitical storyline. It is a direct challenge to the assumption that undergirds most NRI career planning: that America is, and will remain, the default destination.

Consider the calculus facing a 28-year-old IIT graduate on OPT. The H-1B lottery odds have worsened. The $100,000 fee means fewer employers will sponsor. OPT itself faces an existential legal challenge from the Landmark Legal Foundation. And even if everything goes right, the green card queue stretches to the 2150s.

China's K-visa, for all its unknowns — age caps remain unspecified, citizenship is essentially impossible, and the domestic backlash from Chinese graduates facing 17.7% youth unemployment is real — at least offers clarity of access. So does Canada's Express Entry. So does Germany's Chancenkarte.

The question is no longer whether Indian talent has alternatives to America. It is whether America has noticed that the alternatives are getting better.""",
    },
    # ── Article 2: GCC Boom ──
    {
        "id": str(uuid.uuid4()),
        "headline": "T-Mobile Just Opened a 1,000-Person Tech Centre in Hyderabad — and It Won't Need a Single H-1B Visa",
        "subheadline": "India's Global Capability Centre boom is turning America's immigration crackdown into a $65 billion advantage, and the companies doing the hiring are the same ones that used to sponsor H-1B workers.",
        "slug": make_slug("gcc-boom-tmobile-hyderabad-h1b-reverse-brain-drain"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For Indian Americans who built careers through the H-1B pipeline, the GCC explosion represents both vindication and vertigo. The same skills that once required a US visa now command competitive salaries in Bengaluru and Hyderabad. Some diaspora professionals are quietly exploring 'reverse migration' — taking GCC leadership roles in India that offer comparable responsibility without the immigration anxiety.",
        "tags": ["gcc", "h1b", "reverse-brain-drain", "hyderabad", "india-tech", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/t-mobile-opens-india-tech-centre-hire-nearly-1000-by-2027-2026-06-05/"},
            {"name": "Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/india-fast-tracks-gcc-policy-as-us-tightens-h1b-visas/article68647882.ece"},
            {"name": "Nasscom-Zinnov Report", "url": "https://nasscom.in/"},
            {"name": "Vestian Research", "url": "https://vestian.com/insights/global-capability-centers-help-build-without-h1bs/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35175238/pexels-photo-35175238.jpeg",
        "image_caption": "Modern office buildings in the HITEC City tech district of Hyderabad, India",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """When T-Mobile inaugurated its new Global Capability Centre in Hyderabad last week — 250,000 square feet of leased space, plans for nearly 1,000 employees by 2027, capabilities spanning software engineering, DevOps, cybersecurity, and data analytics — the US telecom giant did not need to file a single H-1B petition.

That is the point.

## The Arithmetic of Avoidance

India now hosts over 1,700 Global Capability Centres employing roughly 2 million professionals and generating $65 billion in annual revenue. The sector is projected to grow at a 29% compound annual rate through 2030, according to a Nasscom-Zinnov report from May. Two-thirds of new GCCs choose Bengaluru or Hyderabad.

These are not the call centres of the 2000s. GCCs have evolved from low-cost outsourcing hubs into strategic nodes where companies like JPMorgan Chase, Goldman Sachs, and Microsoft conduct core business functions: product development, AI research, cybersecurity operations, strategic analysis. The work that used to require bringing an Indian engineer to Seattle on an H-1B now gets done in the same time zone as Chennai.

The migration of work rather than workers has accelerated sharply since September 2025, when the Trump administration imposed a $100,000 fee on new H-1B petitions. Research from Vestian, a corporate real estate advisory, found that for every H-1B visa rejection, companies hire an average of 0.42 employees abroad. Among the most globally integrated firms, the ratio approaches 1:1.

"Instead of bringing Indian talent to America, you establish operations in India where that talent already exists," Vestian's analysis concluded. "This eliminates visa dependencies while providing access to the same high-quality professionals."

## India Sees Its Chance

New Delhi is not passively absorbing the windfall. Seeing opportunity in Washington's latest H-1B curbs, the Indian government is fast-tracking a national policy on Global Capability Centres, according to officials at the Ministry of Electronics and Information Technology.

"We hope to accelerate efforts to grow the GCC ecosystem," a senior government official told the Hindu Business Line. "Things are already in place. Indian IT companies can probably operate from here, instead of sending their employees outside the country."

The ministry has convened an industry-led panel to draw up the national framework, focusing on talent development, infrastructure, and expansion beyond the metros into tier-2 and tier-3 cities. Finance Minister Nirmala Sitharaman, during the Union Budget 2025-26, announced that a national framework would be formulated to guide states in promoting GCCs. Karnataka, Tamil Nadu, and Uttar Pradesh already have state-level GCC policies with fiscal incentives and infrastructure support.

The top six Indian IT services firms — TCS, Infosys, HCL Technologies, Wipro, Tech Mahindra, and LTIMindtree — have reduced their H-1B visa issuances by 46% over the past five years, according to USCIS data. They now employ 50 to 80% of their US workforce locally, supplementing with L-1 intra-company transfers, nearshore operations in Canada and Latin America, and — increasingly — GCC operations in India.

## The Diaspora Paradox

For Indian Americans who spent years navigating the H-1B-to-green-card pipeline, the GCC explosion creates a strange new landscape. The skills that once required enduring a decade-long immigration queue now command competitive compensation in Bengaluru and Hyderabad, often with leadership responsibilities that would take years longer to reach in the US.

Some are taking notice. Executive search firms report a growing category of "reverse migration" enquiries — diaspora professionals in their late 30s and 40s, often with green cards or citizenship already secured, exploring GCC leadership roles that offer comparable seniority without the immigration anxiety that defined their younger years.

The calculus differs for those still in the queue. An H-1B holder in Sunnyvale, watching T-Mobile hire 1,000 people in Hyderabad to do the same work, faces a pointed question: why endure a 128-year green card wait when the work itself has moved?

## What Washington Loses

The policy feedback loop is now plainly visible. Washington restricts the H-1B programme to protect American jobs. Companies respond by moving the jobs, not the workers. India builds the infrastructure to absorb them. The American worker whom the restrictions were designed to help finds that the alternative employer is not hiring domestically at all — it is hiring in Hyderabad.

Gaurav Vasu, CEO of research firm UnearthInsight, offered a measured assessment: "GCCs could actually stand to benefit, provided companies don't take a protectionist stance. For now, India continues to be the largest hub, and headquarters still see it as a critical choice."

The irony is structural. Every H-1B restriction that makes it harder to bring an Indian engineer to Dallas makes it marginally easier for India to keep that engineer in Hyderabad. T-Mobile's new tech centre is not a protest against American immigration policy. It is simply the most rational response to it.""",
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
