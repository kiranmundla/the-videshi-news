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
        "headline": "The Puja Room Is Empty — How the H-1B Crackdown Broke Dallas's Indian Housing Boom",
        "subheadline": "Collin County home prices have fallen 9 per cent in a year. The Indian families who built the suburbs of Frisco and Celina are leaving, and nobody is lining up to replace them.",
        "slug": make_slug("puja-room-empty-h1b-crackdown-dallas-indian-housing-boom"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B workers drove one of America's most extraordinary suburban housing booms in North Texas. Now, between the $100K petition fee, FHA mortgage bans for non-permanent residents, and 123,000 tech layoffs, they are selling at a loss and considering moves back to India. This is the first major data point showing the H-1B crackdown's direct impact on Indian-American homeownership and wealth.",
        "tags": ["h1b", "housing", "dallas", "collin-county", "fha-mortgage", "indian-diaspora"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "New York Post / Bloomberg", "url": "https://nypost.com/2026/06/05/real-estate/trumps-crackdown-on-h1b-visa-abuse-sends-dallas-home-prices-down/"},
            {"name": "Redfin", "url": "https://www.redfin.com/"},
            {"name": "Pew Research Center", "url": "https://www.pewresearch.org/"},
            {"name": "John Burns Research and Consulting", "url": "https://jbrec.com/"},
            {"name": "U.S. Census Bureau", "url": "https://www.census.gov/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7578858/pexels-photo-7578858.jpeg",
        "image_caption": "A suburban home with a For Sale sign in the front yard",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For years, the suburbs north of Dallas ran on a single fuel source: Indian money. H-1B workers poured into corporate campuses along the Telecom Corridor and its sprawling offshoots, bought five-bedroom homes in Frisco and Prosper, and turned Collin County into the fastest-growing county in America among those with a population above one million. Builders designed model homes with north-facing puja rooms and optional spice kitchens. At peak demand, South Asians represented 70 per cent of sales at one North Texas homebuilder.

That market is now in reverse.

## The Numbers

Collin County home prices fell nearly 9 per cent year-over-year as of February, according to Redfin data — more than double the 4 per cent drop recorded across the broader Dallas-Fort Worth metro area. The retreat of Indian buyers, once the dominant force behind new home construction in the area, is functioning like a release valve on one of America's most overheated regional housing markets.

The federal government granted nearly 32,000 new H-1B approvals in the Dallas area alone during the Biden administration, topping Silicon Valley, Seattle, San Francisco, and Washington, according to a Bloomberg investigation citing USCIS data. Only the New York City metro area ranked higher. The workers who arrived on those visas settled in Prosper, Frisco, and Celina, where the population more than tripled in five years. In Frisco — a city of 235,000 roughly 30 miles north of downtown — the share of Indian residents ballooned from about 6 per cent in the early 2010s to nearly 20 per cent by the mid-2020s.

Then came the policy squeeze.

## A Triple Blow

The H-1B crackdown arrived in stages. Trump raised minimum salary thresholds and directed the programme to prioritise the highest-paid applicants. The Labour Department launched "Project Firewall," targeting alleged employer abuse. In September 2025, a presidential proclamation imposed a $100,000 fee on new H-1B petitions — effectively pricing out the staffing firms and mid-tier tech contractors that had been the biggest sponsors of Indian workers in markets like Dallas.

Simultaneously, the Department of Housing and Urban Development barred non-permanent residents, including H-1B holders, from accessing FHA-insured mortgages starting May 2025. The share of FHA loan volume issued to non-permanent residents fell from 6 per cent in April to virtually zero by late summer, according to John Burns Research and Consulting.

The third blow was structural, not political: over 123,000 tech jobs were cut by early summer 2026, with AI consistently cited as the primary driver.

## What It Looks Like on the Ground

In the Mustang Lakes subdivision in Celina, Ravi Vavilala — an Indian-born naturalised citizen — bought a five-bedroom home in late 2023 for $895,000. He was laid off from his IT job in March. The house is now listed below what he paid, at $873,000, struggling to compete against builder incentives being offered down the street. Before his next showing, he moved his religious items out of sight. "Because the market is very slow, I want to attract all types of buyers," he told Bloomberg.

Real estate agent Neeraj Gupta, who came to Dallas on an H-1B visa in 2000 and spent two decades in IT before switching to real estate, says his phone — once ringing constantly with buyers — now rings with sellers looking to cut losses. Some clients absorb monthly rental losses of $300 to $1,500 while waiting for the market to turn. One client, a senior IT director holding two Frisco homes each valued above $1 million, is weighing a move back to India. Another financed an $800,000 home almost entirely with debt; the property is now worth less than the loan balance.

## Why This Matters Beyond Dallas

The dynamics in North Texas are a preview for every tech-heavy metro where H-1B workers have long propped up housing demand. Roughly three-quarters of H-1B workers approved in fiscal year 2023 were born in India, according to Pew Research Center. States most exposed include New York, New Jersey, California, Washington, Virginia, and Texas. In Seattle, analysts project home prices could cool by 2 to 5 per cent in H-1B-dense neighbourhoods as new hiring contracts.

Housing analyst Alex Barron of El Paso's Housing Research Center poses the blunt question: "Who is there to replace them?"

For the Indian families who built equity, community, and temples in the suburbs of North Texas, the answer is not reassuring. The puja room may have been a selling point in 2023. In 2026, it is being cleared for the next showing."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "One Hundred and Fifty-Five Dollars — The Price Canada Charges for the Workers America Wants $100,000 For",
        "subheadline": "As the US prices out skilled Indian professionals with six-figure visa fees, Canada, the UK, and Australia are rolling out the welcome mat. The global talent race is no longer theoretical.",
        "slug": make_slug("canada-155-dollars-vs-america-100000-h1b-talent-race"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders are the single largest group affected by the $100K fee. Many are now treating Canadian work permits as insurance policies. India's top IT firms have already cut H-1B filings by 46%, and four major US employers including Walmart and TCS have paused new sponsorships entirely. For Indians stuck in multi-decade green card backlogs, Canada's Express Entry system offers permanent residency in months rather than decades.",
        "tags": ["h1b", "canada", "talent-competition", "global-mobility", "indian-diaspora", "work-permit"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
            {"name": "Niskanen Center", "url": "https://www.niskanencenter.org/the-global-race-for-talent-other-nations-are-outpacing-the-u-s-on-high-skill-immigration/"},
            {"name": "TechGig / USCIS Data", "url": "https://content.techgig.com/technology/indian-it-firms-cut-h-1b-visas-by-46-impact-on-tech-jobs/articleshow/113218969.cms"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/"},
            {"name": "Immigration consultant Amir Ismail", "url": "https://amirismail.com/canada-h1b-alternative-2026/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
        "image_caption": "An open passport displaying various travel and visa stamps",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """Here is a number that tells you everything about the global talent market in 2026: the United States charges $100,000 for a new H-1B work visa petition. Canada charges $155 for an open work permit and processes it in two weeks. The arithmetic is not subtle.

The price gap was always there in spirit — America's immigration system has been slower, more capricious, and more employer-dependent than its peers for decades. But the Trump administration's September 2025 proclamation imposing a $100,000 fee on new H-1B petitions turned a structural disadvantage into a numerical absurdity. And the rest of the world has noticed.

## The Competitors Are Not Waiting

A new Brookings Institution report published this week, "How the Trump Administration Is Eroding the Immigrant Talent Pipeline," catalogues the damage: F-1 student visa issuances to Indians are down 29 per cent, 1.2 million people sit in the employment-based green card queue, and the H-1B cap for fiscal year 2027 was hit in just 25 days after the application window opened on March 4 — despite the new fee.

But the report's most consequential section is not about American policy. It is about what other countries are doing with the opening. Canada, the UK, Australia, and Singapore are all updating and expanding their high-skill visa regimes specifically to attract the workers America is pushing away.

Canada has been the most aggressive. When Ottawa opened 10,000 H-1B Open Work Permits in 2023, all spots filled within 48 hours. The programme is explicitly aimed at foreign-born tech professionals already in the United States who cannot or will not pay $100,000 to stay. The wage gap remains — US tech salaries run roughly 46 per cent higher than Canadian equivalents — but Canadian permanent residency through the Express Entry system can arrive in months. An Indian national in the EB-2 employment-based queue may wait decades for the same outcome in America.

The Niskanen Center, a Washington think tank, published its own assessment: "By restricting pathways for high-skilled workers while peer economies broaden theirs, the U.S. risks exporting innovation and eroding competitiveness."

## The Corporate Response

The fee has already changed corporate behaviour. News reports indicate that only about 85 companies have actually paid the $100,000. Four major employers — Walmart, TCS, Cognizant, and Intuitive Surgical — have paused new H-1B sponsorships entirely. Walmart said it remains "committed to hiring the best talent" but is being "thoughtful" about visa hiring. TCS is "focusing on local hiring." Cognizant's recent job postings specify that applicants must be authorised to work without sponsorship.

India's top six IT services companies — TCS, Infosys, HCL Technologies, Wipro, Tech Mahindra, and LTIMindtree — have reduced their H-1B visa filings by 46 per cent over the past five years, according to USCIS data. Companies that once built their entire US delivery model on bringing engineers from Hyderabad and Bengaluru now employ 50 to 80 per cent of their American workforce locally. They are also nearshoring to Canada and Latin America.

Bloomberg estimates that if Infosys, TCS, and Cognizant maintained their prior hiring volumes under the new fee, they would face a combined $2.25 billion in costs — a figure that makes offshoring to Pune look less like a cost-saving measure and more like a survival strategy.

## The Diaspora Calculation

For Indian professionals already in the United States, the calculation has shifted from "How do I stay?" to "Where else can I go?" Immigration consultants report that Canadian PR applications from Indian H-1B holders have surged. Only about 12 per cent of those who obtained Canadian permits actually relocated — most use them as insurance — but the trend line matters more than the conversion rate.

The wage gap keeps many rooted in the US for now. But wages are a snapshot. Green card wait times are a timeline. An Indian software engineer earning $180,000 in Seattle with a 2015 EB-2 priority date faces a wait that could stretch past 2040. The same engineer can land Canadian PR in under a year, buy a home without visa restrictions, and sponsor family members without a decade-long queue.

The United States spent a generation building the world's most powerful magnet for skilled immigration. The $100,000 fee did not turn it off. But it gave every competitor nation a price tag to undercut — and $155 is a very easy number to beat."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
