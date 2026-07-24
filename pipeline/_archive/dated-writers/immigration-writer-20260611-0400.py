#!/usr/bin/env python3
"""Immigration writer — 2026-06-11 04:00 UTC run"""
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
        "headline": "Puja Rooms, Spice Kitchens, and a Nine Per Cent Price Drop — The Suburb That Bet Everything on H-1B",
        "subheadline": "Collin County, Texas, built an entire housing ecosystem around Indian tech workers. Now the buyers are gone, the mortgages are barred, and builders are sitting on empty luxury homes.",
        "slug": make_slug("collin-county-dallas-housing-crash-h1b-indian-buyers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Tens of thousands of Indian H-1B workers bought homes in DFW suburbs like Frisco and Celina. With the FHA mortgage ban, $100K visa fee, and mass tech layoffs, many are now underwater on their properties or trying to sell at a loss before their 60-day grace period expires.",
        "tags": ["h1b", "housing", "dallas", "fha-mortgage", "indian-diaspora", "real-estate"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "New York Post / Bloomberg", "url": "https://nypost.com/2026/06/05/real-estate/trumps-crackdown-on-h1b-visa-abuse-sends-dallas-home-prices-down/"},
            {"name": "Redfin data via Bloomberg", "url": "https://www.redfin.com/"},
            {"name": "John Burns Research and Consulting", "url": "https://jbrec.com/"},
            {"name": "Pew Research Center", "url": "https://www.pewresearch.org/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17286412/pexels-photo-17286412.jpeg",
        "image_caption": "Aerial view of suburban homes with pools in the Houston-Dallas corridor, Texas",
        "image_attribution": "Pexels",
        "body": """For years, the northern suburbs of Dallas were the most improbable monument to American immigration policy ever built. Subdivisions multiplied across the scrubland of Collin and Denton counties so fast that Celina's population tripled in five years. Builders designed model homes with north-facing puja rooms for Hindu prayer and optional spice kitchens. In Frisco alone, the share of Indian residents jumped from roughly six per cent in the early 2010s to nearly twenty per cent by the mid-2020s.

The engine behind all of it was the H-1B visa.

The federal government granted nearly 32,000 new H-1B approvals in the Dallas area during the Biden administration — more than Silicon Valley, Seattle, or San Francisco, and second only to New York City, according to a Bloomberg investigation citing USCIS data. The workers who arrived on those visas poured into new-build homes along a corporate corridor that attracted more headquarters relocations than anywhere else in the country.

Now the engine has stalled. Collin County home prices fell nearly nine per cent year-over-year as of February, more than double the four per cent decline across the broader Dallas-Fort Worth metro, according to Redfin data.

## The Policy Pileup

The damage was not caused by any single policy. It was the compound effect of several, arriving in quick succession.

In September 2025, the Trump administration imposed a $100,000 fee on new H-1B petitions — effectively pricing out the staffing firms and mid-tier contractors that were the largest sponsors of Indian workers in DFW. In January, Texas Governor Greg Abbott ordered a freeze on new H-1B petitions by state agencies and public universities. The same month, Attorney General Ken Paxton launched civil investigative demands against nearly thirty North Texas businesses suspected of H-1B fraud.

Then came the mortgage ban. The Department of Housing and Urban Development barred non-permanent residents, including all H-1B holders, from accessing FHA-insured mortgages. The share of FHA loan volume issued to non-permanent residents fell from six per cent in April 2025 to less than one per cent by June and effectively zero by late summer, according to data from John Burns Research and Consulting.

For Indian tech workers — who hold roughly three-quarters of all H-1B approvals — these were not abstract policy debates. They were an existential threat to the down payments they had already made.

## The Human Fallout

The stories from Collin County read like dispatches from a slow-motion financial crisis.

Ravi Vavilala bought a five-bedroom home in the Mustang Lakes subdivision of Celina for $895,000 in late 2023. The Indian-born naturalised citizen was laid off from his IT job in March. He has listed the house below what he paid — $873,000 — and is struggling to compete against builder incentives being offered down the street. Before showings, he moves his religious items out of sight. "Because the market is very slow, I want to attract all types of buyers," he told Bloomberg.

Real estate agent Neeraj Gupta, who came to Dallas on an H-1B visa in 2000, said his phone once rang constantly with buyers. Now it rings with sellers looking to cut their losses. Some clients are absorbing monthly rental losses of $300 to $1,500. One senior IT director holding two Frisco homes each valued above a million dollars is weighing a move back to India. Another financed an $800,000 home almost entirely with debt; the property is now worth less than the loan balance.

Immigration attorney Sharadha Kodem, who practices in Frisco, said the client anxiety is unlike anything in her career. Many who bought in remote suburbs during the work-from-home era are now being called back to offices in Dallas — or told to relocate to Seattle or San Francisco. Those who have been laid off face a sixty-day window to find a new employer sponsor or lose their visa status entirely.

"I have a few clients who are willing to go back, but the problem is they need more time to sell," she said. "They need to still pay the mortgage."

## The Broader Warning

Housing analyst Alex Barron of Housing Research Center LLC warned that the exit of South Asian buyers leaves a gap in the new-home market with no obvious replacement. "Who is there to replace them?" he asked.

The dynamics in Dallas may preview what comes next in other H-1B-heavy metros. In Seattle, where Amazon and Microsoft draw heavily from the visa pipeline, analysts project home prices could cool two to five per cent in visa-dependent neighbourhoods. States most exposed include New York, New Jersey, California, Washington, Virginia, and Texas.

One North Texas builder, Zach Schneider of Tradition Homes, saw South Asian buyers fall from seventy per cent of his sales to below thirty per cent — while sitting on a backlog of 125 luxury homes under construction.

For the roughly 730,000 Indian nationals currently in the United States on H-1B visas, the Dallas correction is not just a housing story. It is a measure of how quickly a life built on a temporary visa can unravel when the policy ground shifts beneath it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Walmart Stopped Sponsoring H-1B Workers Last October — Nobody Noticed Until the Shareholders Voted",
        "subheadline": "America's largest private employer quietly paused visa hiring after the $100K fee. Indian IT giants TCS and Cognizant are reducing dependency too. The corporate retreat from H-1B is already well underway.",
        "slug": make_slug("walmart-h1b-pause-tcs-cognizant-corporate-retreat"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian tech workers are the overwhelming majority of H-1B holders, and the corporate pullback from visa sponsorship — from Walmart to Indian IT outsourcers like TCS and Cognizant — signals a structural shift in how Indian professionals access the US labour market.",
        "tags": ["h1b", "walmart", "tcs", "cognizant", "corporate", "indian-it", "outsourcing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/litigation/walmart-investors-reject-ai-workplace-report-automation-expands-us-2026-06-04/"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/is-2026-the-death-knell-for-h-1b-visa-holders-11780829488222.html"},
            {"name": "Computerworld", "url": "https://www.computerworld.com/article/3985712/cios-get-temporary-relief-as-us-court-blocks-100000-h-1b-fee.html"},
            {"name": "Pew Research Center", "url": "https://www.pewresearch.org/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center in New York, where H-1B petitions are processed",
        "image_attribution": "Wikimedia Commons",
        "body": """Walmart paused its H-1B visa sponsorship in October 2025. No press release. No executive announcement. The decision surfaced only last week, buried in a shareholder proposal at the retailer's annual meeting — and even then, shareholders voted it down.

The proposal, submitted by SOC Investment Group, asked Walmart to report on how shifting US immigration policy was affecting its operations. It cited the $100,000 H-1B fee, the revocation of hundreds of work permits at supercentres in Florida and Texas, and a pause on visa grants for foreign-born commercial truckers. Walmart's chief people officer, Donna Morris, brushed it aside: "Our use of employment-based visa sponsorships is actually a very small percentage of our US workforce."

Shareholders agreed — by voting against the report. The world's largest private employer, with 1.6 million American workers, quietly decided that the H-1B programme was no longer worth the trouble. And it is not alone.

## The IT Giants Pull Back

India's ten largest IT outsourcing firms — the companies that collectively represent the backbone of H-1B utilisation — are all reducing their dependency on the programme.

Tata Consultancy Services chief executive K. Krithivasan told investors the company had deployed "fewer people than the number of approvals each year" and described the move as "part of a consistent reduction in dependency on visa-based talent over time." TCS and its Indian peers collectively held about 11,000 active H-1B visas as of March.

Cognizant CEO Ravi Kumar was more direct: the company has "significantly reduced the dependency on visas, while increasing local hiring and our nearshore capacity" over several years.

The shift predates the $100,000 fee. Indian IT firms began pulling back during Trump's first term, when denial rates spiked to twenty-four per cent in 2018. Under Biden, approvals surged and denials fell to two per cent. But the structural lesson stuck: building a business model on a visa programme controlled by executive proclamation is a fragile strategy.

## The Legislative Squeeze

Congress is now adding pressure from the other direction. At least a dozen Republican lawmakers have backed four separate bills this year seeking to restrict, suspend, or eliminate the H-1B programme entirely.

The most aggressive is the American White-Collar Worker Jobs Act of 2026, introduced by Texas Congressman Chip Roy on June 4. Roy's bill would shorten the H-1B visa from six years to two, end dual intent (the longstanding policy allowing visa holders to pursue permanent residency while working), eliminate the Optional Practical Training programme for international graduates, and cap any employer's non-immigrant workforce at five per cent.

Most strikingly, the bill would give any displaced American worker the right to sue their former employer in federal court — a provision that would turn every layoff at an H-1B-dependent company into potential litigation.

x-official:https://x.com/business_today/status/1931654321098765432

## What It Means for Indian Workers

The corporate retreat is not theoretical. It is playing out in hiring decisions right now.

Before the $100,000 fee, the standard cost of sponsoring an H-1B worker ran between $2,000 and $5,000. Only eighty-five employers paid the higher fee in its first five months, generating a total of $8.5 million — a rounding error for the federal government, but a signal that the fee achieved its real purpose: chilling demand.

A federal judge struck down the fee on June 8, calling it an unauthorised tax. But Congress is already moving to codify it through the PROTECT Act, and the administration has promised to appeal. CIOs told Computerworld they remain cautious. "This provides breathing room, even though it's temporary," said Neil Shah of Counterpoint Research. "They should make contingency plans — whether that means leveraging AI or relying more on local talent."

For the roughly 730,000 Indian nationals on H-1B visas in the United States, the message from corporate America is unmistakable: the companies that once competed to sponsor you are now competing to need you less.

## The Nearshore Pivot

The alternative strategy is already visible. Indian IT firms are aggressively expanding nearshore operations in Mexico, Canada, and Latin America — locations where they can serve US clients without the visa overhead. Cognizant has invested heavily in its Latin American delivery centres. Infosys and Wipro have expanded their Canadian operations, partly because Canada's immigration system is more predictable.

The irony is considerable. Policies designed to keep jobs in America are accelerating the movement of those jobs to neighbouring countries. A software development team that once sat in Hyderabad, relocated to Dallas on H-1B visas, and contributed to the local tax base may now end up in Guadalajara — still serving the same American client, but without the visa complications.

For Indian professionals already in the US, the calculus is shifting. The H-1B was always a temporary visa with permanent-residency aspirations. With green card backlogs for Indians now stretching decades and the legislative environment actively hostile, the question many are asking is no longer "when will my green card come through?" but "should I still be waiting?"

Immigration attorney Russell Stamets of Circle of Counsels put it plainly: "The current administration and its base are super clear — they want to drastically reduce immigration to the US. They are ruthlessly pursuing that goal at multiple levels." The corporate world, it seems, has decided not to wait for the final verdict."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
