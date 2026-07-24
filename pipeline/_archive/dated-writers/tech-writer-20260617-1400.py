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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The World's Cybersecurity Firms Are Quietly Moving to Bengaluru. India's Tech Job Map Is Being Redrawn.",
        "subheadline": "As US visa fights make importing Indian engineers expensive, multinationals are building the jobs in India instead — and India's captive-center workforce is on track to hit 2.36 million this year.",
        "slug": make_slug("india-gcc-boom-cybersecurity-n-able-bengaluru-talent-h1b-pivot"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For Indian engineers weighing whether the H-1B ladder is still worth climbing, the GCC boom signals that the best jobs at American firms may increasingly be in Bengaluru and Hyderabad, not Silicon Valley.",
        "tags": ["india-tech", "gcc", "cybersecurity", "h1b", "bengaluru", "jobs"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/us-cybersecurity-firm-n-able-opens-india-gcc-plans-50-local-workforce-expansion-2026/"},
            {"name": "Business Wire", "url": "https://www.businesswire.com/news/home/n-able-bengaluru-office"},
            {"name": "Reuters (T-Mobile GCC)", "url": "https://www.reuters.com/technology/t-mobile-opens-india-tech-centre-hire-nearly-1000-2027/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36665297/pexels-photo-36665297.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A modern high-rise in Bengaluru, the city absorbing the bulk of India's new global capability centers",
        "image_attribution": "Pexels",
        "body": """When the American cybersecurity firm N-able opened a new office in Bengaluru this week, it did something that would once have been unremarkable and is now revealing. It announced plans to expand its India headcount by at least half before the year is out — not to cut costs, its chief executive insisted, but because that is where the engineers are.

"The reason we're in Bengaluru is capability," CEO John Pagliuca told Reuters. "Our priority is to build for the long term, with the right people and a strong foundation, not to pursue a short-term headcount play." The careful wording matters. For two decades, the standard story about an American company opening an India office was about arbitrage: the same work, done cheaper. Pagliuca went out of his way to say the opposite.

He is not alone. T-Mobile opened a global capability center, or GCC, in Hyderabad this month with plans to hire nearly 1,000 people by 2027. The advisory firm Aeries Technology landed a mandate to help a global tax-and-finance platform stand up a GCC in a Tier-II Indian city. According to a Nasscom and Zinnov report, India's GCC workforce is projected to reach 2.36 million employees by the end of 2026, with AI and cybersecurity skills driving most of the demand.

### From back office to brain trust

The term "global capability center" is doing a lot of quiet work. A GCC is a captive office a multinational owns outright — not an outsourcing vendor like Infosys or Cognizant that it hires by contract. The first wave, in the 2000s, handled the unglamorous middle: payroll runs, help-desk tickets, code maintenance. The current wave is different. N-able says its Bengaluru team will build defensive AI capabilities — automated threat detection, faster incident response — for the more than 500,000 organizations it protects worldwide. That is core product, not back office.

The shift has been building for years, but two forces have accelerated it sharply in 2026. The first is the AI talent crunch: Pagliuca named AI engineering, applied machine learning, cloud security, and threat research as the hardest skills on earth to hire, and India produces them at a scale no other country matches. The second is American immigration policy.

### The visa math has flipped

A US federal judge struck down the Trump administration's $100,000 H-1B application fee on Monday, ruling it an unauthorized tax — only for an appeals court to reinstate it days later while the government appeals. That seesaw is exactly the problem. A company that once solved a talent gap by sponsoring an Indian engineer onto an H-1B and flying them to Seattle now faces a six-figure fee, a weighted lottery that favors the highest salaries, and the real possibility the whole arrangement is litigated away mid-cycle.

Faced with that uncertainty, the rational move for a CFO is brutally simple: build the team in India. The engineer stays in Bengaluru, the company avoids the fee and the lottery entirely, and the work gets done. What Washington intended as protection for American workers is, at the margin, quietly relocating high-end technical jobs out of the United States.

### Why this lands close to home for the diaspora

For the Indian American reading this from New Jersey or the Bay Area, the GCC boom cuts two ways, and both are personal.

If you are early in your career and weighing whether the H-1B path is still worth the gamble, the message is sobering: the most interesting work at American firms is increasingly being staffed in India, where there is no visa lottery to lose. The traditional move-to-America playbook that brought a generation of Indian engineers to Silicon Valley is narrowing.

If you are already established here — a senior manager, a director, a founder — the same trend is an opportunity. Someone has to run these centers, set their technical agenda, and bridge the Bengaluru team to headquarters. Those are exactly the roles that diaspora professionals, fluent in both worlds, are positioned to win. The GCC boom does not erase the US-India tech corridor; it rebuilds it, with more of the traffic flowing the other way.

The deeper signal is about leverage. For thirty years, India's pitch to global tech was labor — capable hands at a good price. The 2026 version of that pitch is capability: the brains that design the system, not just the ones that maintain it. As N-able's careful phrasing made clear, even the companies doing the hiring have stopped pretending otherwise."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Tata Just Put an Amazon Veteran in Charge of BigBasket. The 10-Minute Grocery War Is About to Get Uglier.",
        "subheadline": "Amit Nanda replaces co-founder Hari Menon as India's $11.5 billion quick-commerce market squeezes the original online grocer between Blinkit, Zepto and Amazon's own delivery push.",
        "slug": make_slug("bigbasket-amit-nanda-amazon-tata-quick-commerce-war-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRIs who use BigBasket to stock their parents' kitchens in India — and those holding Tata-linked stocks — have a direct stake in whether the original online grocer can survive the 10-minute delivery onslaught.",
        "tags": ["india-tech", "quick-commerce", "tata", "bigbasket", "ecommerce", "startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/retail-consumer/indias-bigbasket-names-former-amazon-veteran-amit-nanda-ceo-2026/"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/tata-owned-bigbasket-names-former-amazon-executive-amit-nanda-as-ceo.htm"},
            {"name": "BestMediaInfo", "url": "https://bestmediainfo.com/bigbasket-appoints-amit-nanda-ceo"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7843985/pexels-photo-7843985.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A delivery van loaded with fresh produce crates, the front line of India's quick-commerce battle",
        "image_attribution": "Pexels",
        "body": """BigBasket helped invent online grocery shopping in India. This week it admitted that may no longer be enough. The Tata-owned company named Amit Nanda, an 11-year Amazon India veteran, as its chief executive, with co-founder Hari Menon stepping back to the board after running the business from its founding in 2011.

The handoff is polite — Menon stays on as mentor — but the subtext is not subtle. BigBasket pioneered the scheduled, next-day grocery delivery that a generation of urban Indians grew up on. Then the ground moved. India's quick-commerce market, built on the promise of groceries at your door in ten minutes, has swelled to roughly $11.5 billion in just five years. And BigBasket's measured, warehouse-and-schedule model suddenly looked like the slow option.

### The pincer

Look at the names BigBasket is now fighting. Eternal's Blinkit and the IPO-bound Zepto are pure quick-commerce players built from day one around dark stores and ten-minute promises. Swiggy's Instamart comes with a food-delivery network attached. Walmart-backed Flipkart has Minutes; Reliance has JioMart. And then there is Amazon, whose new "Now" service brings the world's most ruthless logistics operator directly into BigBasket's lane.

That last threat explains the hire. Nanda spent more than a decade at Amazon India, most recently as Director of Selling Partner Services, running the third-party marketplace that is the engine of Amazon's Indian business. Tata did not pluck a grocery lifer; it poached someone who knows precisely how the company now eating BigBasket's lunch actually operates. Earlier this month it also installed Seshu Kumar Tirumala as chief operating officer. This is a leadership team assembled for a street fight.

### What Tata is really buying

BigBasket is not a standalone startup. It sits inside Tata Digital, the conglomerate's bet on a consumer "super app" spanning groceries, electronics, pharmacy and payments. Sajith Sivanandan, who runs Tata Digital and chairs BigBasket, called Nanda "an excellent choice to lead bigbasket" through its quick-commerce push. The company has promised to roll out 10-minute delivery nationwide by the end of fiscal 2026 — a target that sounds less like ambition and more like survival.

The hard truth is that quick commerce is a brutal business. The ten-minute promise requires a dense web of small "dark stores" near customers, each one a fixed cost that bleeds money until order volume catches up. Zepto's own IPO filings show a company doubling revenue while burning through cash. Winning means out-spending and out-executing rivals who are equally willing to lose money for market share. Tata has the balance sheet for that war. The open question is whether it has the speed.

### Why the diaspora should watch this one

This is not abstract for the Indian American audience. A large share of NRIs use exactly these apps as a remote-control lifeline — ordering groceries, medicines and household supplies to elderly parents back in India from an apartment in Edison or Fremont. When BigBasket's reliability slips or its catalog thins because it is losing the dark-store war, that is felt directly in a Bay Area kitchen at 2 a.m., placing an order across twelve and a half time zones.

There is a financial angle too. Tata's listed entities are a staple of NRI India-exposure portfolios, and quick commerce is now one of the most capital-hungry experiments inside the group. Zepto and Swiggy are heading to the public markets; how BigBasket fares against them will shape how investors price the entire sector.

And there is a quieter lesson for the diaspora's many founders and operators. BigBasket did everything a first mover is supposed to do — it built the category, earned the trust, scaled the brand — and still found itself outflanked by rivals who simply moved faster. In Indian consumer tech, being first has rarely been the same thing as being safe. Nanda's job is to prove that being best, and fastest, still can be."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Startup Money Is Flowing Again — and This Week the Smart Capital Bet on Boring",
        "subheadline": "A $30 million round for a consumer-AI startup backed by Airtel and PhonePe's CEO headlines a fourth straight week of funding gains, as investors pivot from hype to companies that actually make money.",
        "slug": make_slug("india-startup-funding-rebound-equal-ai-consumer-ai-nri-investors-discipline"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRI angel investors and the growing crowd putting diaspora money into Indian startups, the shift toward profitable, distribution-backed companies signals where the next decade of cross-border bets is heading.",
        "tags": ["india-tech", "startups", "venture-capital", "ai", "fintech", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Tech Startups (VC Roundup)", "url": "https://techstartups.com/2026/06/15/venture-capital-startup-funding-roundup-june-15-2026/"},
            {"name": "LinkedIn Startup & VC Report (June 8-14)", "url": "https://www.linkedin.com/pulse/startup-venture-capital-report-usa-canada-india-june-8-14-2026"},
            {"name": "Reuters (HCLTech-Sarvam)", "url": "https://www.reuters.com/technology/indias-hcltech-buy-105-stake-sarvam-ai-valuing-startup-15-billion-2026/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A robotic hand reaching into a digital network, illustrating the AI bets driving India's funding rebound",
        "image_attribution": "Pexels",
        "body": """After a grim stretch, India's startup funding tap is open again — and the money is going somewhere telling. The week of June 8 to 14 brought in roughly $256 million across 28 deals, a 53% jump on the week before and the fourth consecutive weekly rebound, according to a closely watched startup and venture-capital report. But the headline number matters less than the kind of companies getting funded.

Take the deal that drew the most attention from investors who pay attention to signals rather than logos. Equal AI raised $30 million from Prosus and Tomales Bay, with an Airtel investor and PhonePe's CEO joining as strategic angels — building consumer AI aimed at India's 500-million-plus internet users. The interesting part is who wrote the checks: the people who control distribution to hundreds of millions of Indian phones are now investing in the AI that will run on top of their platforms. In a market where reaching users is the hardest problem, that is a moat being purchased in advance.

### The flight to substance

A year ago, Indian venture money chased growth at any cost — gross merchandise value, user counts, the vanity metrics of the zero-interest-rate era. This week's deals read differently.

Mygate, a housing-society management platform, raised ₹225 crore after a three-year gap, having grown revenue 80% while cutting losses 61% — and was rewarded with relatively low dilution precisely because it funded growth from revenue rather than perpetual fundraising. Exponent Energy pulled in ₹200 crore for 15-minute EV charging, drawing TDK and Hitachi Ventures into their first India bets — industrial giants validating the engineering, not the pitch deck. GPS Renewables landed ₹635 crore for biogas infrastructure, the month's largest climate-tech round.

The pattern is unmistakable. Capital is rotating toward companies with real revenue, defensible technology, or strategic backers who bring more than money. The market is rewarding discipline.

### The shadow over it all: who owns the AI?

This rebound is happening against an unsettling backdrop. Days earlier, Anthropic abruptly withdrew an advanced model for foreign nationals after the US government cited national-security concerns — the first known instance of an AI model itself, not just chips, being subjected to export controls. For India's startup ecosystem, it landed like a cold shower. Most Indian AI startups are "wrappers": applications built on top of foreign foundation models from OpenAI, Anthropic and Google, with no control over the technology underneath. India became Claude's second-largest market globally, and then learned how fragile that dependency is.

That fear is reshaping where the smart money goes. HCLTech's $150 million bet on Sarvam AI — part of a $234 million round valuing the Bengaluru startup at $1.5 billion — is explicitly a wager on sovereign AI: homegrown models, Indian inference infrastructure, applications tuned for local languages and government use. Sarvam is not selling a thin wrapper; it is trying to own both the capability and the distribution. After the Anthropic scare, "build it here" has gone from policy slogan to investment thesis.

### Why diaspora investors should read the tea leaves

A rising share of the capital flowing into Indian startups now comes from the diaspora — NRI angels, US-based micro-funds, and returnee founders who raise in Bengaluru on relationships built in Silicon Valley. For them, this week's data is a useful map.

First, the discipline signal is real: the companies getting funded have revenue and unit economics, which means diaspora angels chasing the next consumer-app rocket ship are fishing in a pond the institutions have already drained. Second, the operator-as-investor model — exemplified by PhonePe's CEO backing Equal AI — is becoming the most credible early-stage signal in Indian tech. Money from someone who has actually run the commercial problem now outranks money from a generic fund. Diaspora investors with real operating experience in their domain have an edge they should use.

And third, the sovereign-AI thesis is the cross-border opportunity of the decade. The Anthropic episode proved that building on borrowed foundations is a strategic risk, not just a technical convenience. The startups that control their own AI stack — and the investors early enough to back them — are positioning for a market where language, compliance and national interest all point the same direction: toward Indian-owned intelligence. For a diaspora that has spent decades exporting talent to American AI labs, funding the Indian alternative is starting to look like the better trade."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")

print(f"\n{len(inserted)} inserted")
for h in inserted:
    print(" -", h)
