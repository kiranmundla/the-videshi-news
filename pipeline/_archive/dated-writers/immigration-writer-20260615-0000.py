#!/usr/bin/env python3
"""Immigration writer — 2026-06-15 00:00 UTC"""
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
        "headline": "Green Card, No Credit — America Just Cut Off Its Own Immigrant Entrepreneurs",
        "subheadline": "The SBA has barred green card holders from every federal small-business loan programme, even as a new study shows Indian immigrants founded more billion-dollar startups than any other nationality.",
        "slug": make_slug("sba-green-card-loan-ban-immigrant-entrepreneurs-indian"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian Americans on green cards who own or co-own small businesses — from gas stations to tech consultancies — are now locked out of SBA-backed financing, the most affordable lending channel available to small firms.",
        "tags": ["sba", "green-card", "small-business", "immigration", "entrepreneurship"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "NPR / WAMC", "url": "https://www.wamc.org/2026-06-12/door-shuts-on-some-immigrant-entrepreneurs-as-u-s-restricts-small-business-loans"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/us/new-rule-bar-green-card-holders-us-small-business-administration-loans-2026-02-14/"},
            {"name": "U.S. Small Business Administration", "url": "https://www.sba.gov/article/2026/03/07/sba-bans-foreign-nationals-accessing-sba-backed-loans"},
            {"name": "NerdWallet", "url": "https://www.nerdwallet.com/article/small-business/green-card-holders-sba-loans"},
            {"name": "NFAP Study (via The Hindu Business Line)", "url": "https://www.thehindubusinessline.com/news/world/india-is-largest-source-for-immigrant-founders-of-us-unicorns-but-still-not-shooting-for-the-stars/article69654321.ece"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/bf/Kelly_Loeffler%2C_official_portrait_%282025%29.jpg",
        "image_caption": "SBA Administrator Kelly Loeffler, who announced the ban on green card holder lending",
        "image_attribution": "Wikimedia Commons",
        "body": """The Small Business Administration did something in March that no previous administration — Republican or Democratic — had ever done. It told every green card holder in America that they could no longer borrow through any SBA-backed loan programme. Not the flagship 7(a). Not the 504. Not microloans. Not surety bonds. Nothing.

The rule is blunt: to qualify for an SBA loan, a business must now be 100 per cent owned by United States citizens. Not permanent residents. Not people who have lived and paid taxes in the country for decades. Citizens only.

"SBA's small-business loans are for American citizens, and we're unapologetic about it," Administrator Kelly Loeffler told Newsmax.

## What Changed

Before March 2026, the SBA allowed businesses with up to 5 per cent foreign national ownership to access its loan programmes. Legal permanent residents — people the government itself has vetted and authorised to live and work in the country indefinitely — were eligible borrowers as a matter of course.

The Trump administration eliminated that exception in stages. First, a February policy notice barred green card holders from the 7(a) and 504 programmes effective March 1. Then, in a second notice, the SBA extended the ban to its microloan and surety bond guarantee programmes, effective April 1. The policy cites Executive Order 14159, titled "Protecting the American People Against Invasion."

The SBA's own numbers reveal how modest the affected lending was. In fiscal year 2025, the agency approved 3,358 loans to businesses with at least partial permanent resident ownership — roughly 4 per cent of its 85,000 total approvals. The agency characterises this as a necessary prioritisation of finite lending authority amid "record demand for capital."

## The Arithmetic of Exclusion

The timing is grimly ironic. A new study published this month by the National Foundation for American Policy found that immigrants have founded or co-founded 59 per cent of all privately held American startup companies valued at more than one billion dollars — 455 of 775 unicorns tracked. When you add the children of immigrants, the share rises to 66 per cent.

India leads every other country on the list. Indian immigrants have founded or co-founded 96 American unicorns, more than Israel (60), the United Kingdom (47), or China (41). Among them is Perplexity AI, co-founded by Aravind Srinivas, valued at $20 billion.

These are not the people the SBA is worried about. The billion-dollar founders have access to venture capital, not government microloans. But the ecosystem that produced them — the landscape of Indian-owned consulting firms, IT staffing agencies, restaurants, motels, gas stations, and medical practices that dot every American metro area — depends heavily on affordable early-stage credit. The SBA was, for many, the first lender willing to take a chance.

"I don't know where our business would be without this," Cristina Foanene, whose glass company in Fresno has received three SBA loans over a decade, told NPR. She and her husband moved from Romania twenty years ago, hired thirty workers, and built a manufacturing operation. She is now a citizen. Under the new rules, her younger self would not qualify.

## Why This Hits Indian Americans Hard

Census data shows that roughly 15 per cent of America's population is foreign-born, but immigrants run between 20 and 25 per cent of all businesses. Indian Americans are disproportionately represented in this cohort. According to the most recent American Community Survey, Indian immigrants have among the highest rates of self-employment and business ownership of any immigrant group.

Many of these businesses sit in an awkward middle: too established for bootstrapping, too small for venture capital, too new for conventional bank credit. The SBA filled that gap with loan guarantees that made private lenders comfortable extending affordable terms. Without it, the alternatives are thin.

"The alternative — it's just really scarce," said Eda Henries, who runs a firm that helps small businesses raise and manage funds. She reports that private lenders issuing SBA loans are now taking longer to verify every owner's citizenship status, and some deals have collapsed mid-underwriting.

Eight business owners who are legal permanent residents and had applied for SBA loans this year declined to speak to NPR on the record, citing fear of drawing attention to their immigration status.

## The Legislative Response

Democrats in Congress have moved to reverse the policy. Senator Ed Markey and Representative Nydia Velázquez — ranking members of the Senate and House small-business committees — introduced a bill to restore SBA loan eligibility for legal permanent residents.

Whether the bill advances in the current Congress is another question. But the underlying tension is now visible: the same administration that created the $5 million "Gold Card" programme to attract wealthy foreign investors has simultaneously locked out the permanent residents already building businesses on American soil.

For the Indian professional who arrived on an H-1B, survived the green card backlog, and finally received permanent residency — only to discover that the government still does not consider them American enough to borrow from its small-business agency — the message is difficult to misread.

## What to Do Now

Immigration attorneys and small-business advisers recommend three steps for affected green card holders: first, explore conventional bank lending and Community Development Financial Institutions (CDFIs), which are not bound by SBA citizenship rules. Second, if a naturalisation application is pending, consider expediting it. Third, monitor the Markey-Velázquez bill and any legal challenges to the SBA policy — the rule was implemented without a standard notice-and-comment period, which could make it vulnerable in court.

The SBA, for its part, insists the policy does not prevent non-citizens from owning businesses or accessing conventional bank loans. That is technically true. It is also beside the point. The SBA exists precisely because conventional bank loans are harder to get."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Ninety-Six Unicorns and Counting — India Now Leads the World in American Startup Founders",
        "subheadline": "A new NFAP study finds Indian immigrants have founded more billion-dollar American companies than any other nationality, even as Washington tightens every visa pathway that brought them here.",
        "slug": make_slug("india-96-unicorn-founders-nfap-study-immigration"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian-born founders have created 96 US unicorns worth billions — more than any other nationality — but nearly all arrived on student or work visas now under threat from fee hikes, processing holds, and tighter rules.",
        "tags": ["unicorn", "startup", "nfap", "indian-founders", "h1b", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/world/india-is-largest-source-for-immigrant-founders-of-us-unicorns-but-still-not-shooting-for-the-stars/article69654321.ece"},
            {"name": "Swadesi / PTI", "url": "https://www.swadesi.com/en/international/india-born-entrepreneurs-found-96-us-unicorns/"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/world/indian-immigrants-built-96-unicorns-in-america-now-worth-more-than-germanys-stock-market-11749000000000.html"},
            {"name": "NFAP (National Foundation for American Policy)", "url": "https://nfap.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7580992/pexels-photo-7580992.jpeg",
        "image_caption": "Indian American tech professional in a modern office workspace",
        "image_attribution": "Pexels",
        "body": """The numbers arrived quietly, in a research paper from the National Foundation for American Policy. But they are worth reading twice. Of the 775 privately held American startups currently valued at one billion dollars or more, 455 — or 59 per cent — were founded or co-founded by immigrants. When you include the children of immigrants, the share rises to two-thirds.

India sits at the top of the table. Indian-born entrepreneurs have founded or co-founded 96 American unicorns, more than Israel (60), the United Kingdom (47), China (41), or Canada (30). Six Indian-origin founders — Mohit Aron, Jyoti Bansal, Ashutosh Garg, Arvind Jain, Sachin Nayyar, and Ajeet Singh — have each built two or more billion-dollar companies.

The highest-valued Indian-founded unicorn is Perplexity AI, created by Aravind Srinivas, currently worth $20 billion. Below it stretches a roster that includes Rippling (Prasanna Sankar), Cohesity (Mohit Aron), FalconX (Prabhakar Reddy and Raghu Yarlagadda), and Carta (Manu Kumar), among dozens of others.

## The Pipeline That Built Them

The study, authored by Stuart Anderson and published in June 2026, contains a detail that ought to concern anyone tracking American immigration policy. Of the Indian founders on the list, 76 first entered the United States as international students. They came on F-1 visas, studied at American universities, transitioned to H-1B work visas, and eventually built companies that collectively employ hundreds of thousands of people.

That pipeline is now under sustained pressure from multiple directions simultaneously.

The $100,000 H-1B fee — struck down by a federal judge on June 8 but temporarily reinstated while the First Circuit hears the government's appeal — has already reduced H-1B registrations by 27 per cent. The Department of Homeland Security has proposed capping F-1 student visas at four years with mandatory departure, replacing the longstanding "duration of status" framework. USCIS approval rates for EB-1A extraordinary ability petitions — the green card category that many founders use — have dropped below 50 per cent, down from roughly 90 per cent five years ago. And the Department of Labor has proposed a 33 per cent increase in prevailing wage requirements for H-1B positions.

Each of these changes, taken individually, might seem like a reasonable tightening of immigration rules. Taken together, they form a systematic constriction of the very pathway that produced the 96 unicorns the NFAP study celebrates.

## India's Paradox

The Hindu Business Line, reporting on the NFAP data, noted an irony: despite leading the unicorn founder table, Indian immigrants "are not playing in the big leagues yet." The majority of the 96 Indian-founded unicorns are valued below $10 billion. The truly massive companies — SpaceX ($1.5 trillion), Anthropic ($965 billion), OpenAI ($852 billion) — were founded by immigrants from South Africa, the UK, and elsewhere.

The explanation, according to researchers, is partly cultural and partly structural. Indian immigration to the United States has historically been channelled through the H-1B programme, which ties workers to employer sponsors for years before they achieve the independence to start companies. The green card backlog — which currently stretches decades for Indian-born applicants in the EB-2 category — means many founders could not legally strike out on their own until well into their thirties or forties.

"The natural trait of the non-entrepreneurial Indian middle class is to be great employees and executives," one expert told The Hindu Business Line. The data suggests that is changing rapidly. The growth trajectory is steep: in 2018, the United States had 91 unicorn companies, of which 50 had an immigrant founder. By April 2026, the total had grown to 775, with 455 immigrant-founded. That is a 750 per cent increase in unicorn count and an 800 per cent rise in immigrant-founded unicorns over eight years.

## What the Numbers Mean for the Backlog

For the estimated 400,000 Indian nationals waiting in the employment-based green card queue, the NFAP study is both validation and frustration. It proves that the immigration system, whatever its flaws, has generated extraordinary economic value. It also highlights the absurdity of a framework in which someone can build a billion-dollar company while waiting fifteen years for permanent residency because of a per-country cap set by Congress in 1990.

The study found that nearly 80 per cent of all American unicorns have either an immigrant founder or an immigrant in a key leadership role — as CEO, CTO, or VP of engineering. The companies with at least one immigrant founder employ an average of 833 people each.

Meanwhile, the EB-2 visa category for India exhausted its entire fiscal year 2026 allocation in June, with no new visas available until October. The EB-5 investor visa for India has hit the same wall. And the NIW (National Interest Waiver) approval rate has collapsed to roughly a coin flip.

## The Question Washington Isn't Asking

The policy debate in Washington currently centres on whether the H-1B programme displaces American workers. The NFAP data suggests a different question: what happens when you constrict the pipeline that generates companies employing hundreds of thousands of Americans?

The answer, of course, is that those founders go elsewhere. Canada, the United Kingdom, Singapore, and the UAE have all launched fast-track visa programmes explicitly targeting the kind of high-skilled immigrant entrepreneur that American policy is making it harder to become.

Ninety-six unicorns is a remarkable number. It is also a lagging indicator. The founders who will build the next hundred are in American universities and workplaces right now. Whether they stay depends on decisions being made in Washington this year — decisions that, so far, point in one direction."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
