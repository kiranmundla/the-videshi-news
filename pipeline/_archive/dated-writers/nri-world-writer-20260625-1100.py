#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

body1 = """The numbers arrive every quarter with the reliability of a monsoon, and they keep climbing. India will take in a record $137–140 billion in remittances this financial year, according to SBI Research, up from a confirmed $135.46 billion in FY25. No other country comes close: Mexico, the world's second-largest recipient, collected roughly half that. For a nation running a persistent current-account deficit and a wobbling rupee, the money its citizens send home from abroad has quietly become one of the most dependable lines in the national accounts.

What gets less attention is *who* is now doing the sending — and that shift says more about the diaspora than the headline figure does.

## A corridor in motion

For decades, the archetypal remitter was a construction worker in Dubai or Riyadh, wiring a few hundred dollars a month to a village in Kerala or eastern Uttar Pradesh. The Gulf still matters enormously: roughly nine million Indians live there, four million in the UAE alone, and the region contributes around 38% of total inflows, about $51 billion a year.

But the centre of gravity is drifting west. The Economic Survey 2025-26 noted that the share of remittances from advanced economies — the United States, Britain, Canada, Australia — continues to rise, reflecting a growing contribution from skilled professionals rather than wage labourers. The two flows behave nothing alike. Gulf money is largely survival money, smoothing household budgets back home. Western money increasingly looks like investment: deposits, equities, property, EMIs on flats the sender may one day retire into.

That distinction matters because it changes what the diaspora wants from India, and what India is willing to offer in return.

## Delhi notices

When the rupee came under pressure this month, the Reserve Bank of India did not appeal to patriotism. It offered a trade. Under a new scheme, the RBI will absorb the cost of hedging foreign-currency deposits parked with Indian banks for three to five years, letting overseas Indians earn domestic interest rates — now pushed to 6–7% — without taking on currency risk. Banks are marketing it hard. Nomura reckons it could pull in $55 billion; Axis Bank sees scope for $100 billion.

Lenders are now asking the RBI for permission to offer dollar loans against those deposits, a leverage play that could lift returns toward 12–15%. It is the clearest signal yet that India sees its diaspora not as a charity drive in hard times but as a standing pool of capital to be courted with competitive terms.

The February budget made the same bet in slower motion, doubling the individual cap under the Portfolio Investment Scheme from 5% to 10% and easing the paperwork that long deterred non-residents from buying and selling property at home.

## The view from the kitchen table

For the family abroad, none of this is abstract. A nurse in Manchester, an engineer in Austin, a logistics manager in Toronto — each is now weighing whether the parents' monthly transfer should sit in a savings account or chase 7% in a Mumbai bank, whether the Bengaluru flat is a home or a yield. The diaspora's financial relationship with India is maturing from obligation into portfolio management, and the institutions are racing to keep up.

There is a quieter anxiety underneath the optimism. Remittances financed nearly 47% of India's merchandise trade deficit last year. A flow that large, concentrated among 18.5 million people making private monthly decisions, is not a policy lever the government fully controls. Tighten visa rules in Washington or London, soften the labour market in the Gulf, and the tap loosens. Analysts at Mint have warned against taking the flows for granted precisely because they have become so structurally important.

## What's next

The trajectory points up: a doubling over the decade, a diaspora that is better paid and more digitally connected than any before it, and a fintech market in the US-India corridor that has only had serious Indian-built competition since 2025. For the millions who left, the act of sending money home has always been the most concrete expression of the bond. Increasingly, India is treating that bond as a balance sheet — and pricing it accordingly.

**Sources:** SBI Research; Reserve Bank of India; Economic Survey 2025-26; Reuters; Mint."""

body2 = """In May, a 23-year-old from Rohtak put on the chains of office in a Hertfordshire town and, in doing so, rewrote a small line of British history. A week later, his mother did much the same a rung above him. The story of Tushar Kumar and Parveen Rani is being told as a feel-good local headline. It is also a neat parable of how the Indian diaspora's political ascent in Britain now runs through the council chamber, not just Westminster.

## Two ceremonies, one family

Kumar was appointed Mayor of Elstree and Borehamwood Town Council on 13 May, becoming, by his own account and the local press's, the youngest Indian-origin mayor in UK history. He was first elected a councillor at 20, while still reading political science at King's College London. On 20 May, Rani — already a former deputy mayor — was sworn in as the first Indian-origin Mayor of Hertsmere Borough Council, the larger authority that sits above the town.

The family moved from Haryana to England in 2013, when Tushar was ten. Both mother and son have, between council duties, taught Hindi free of charge to local children — a detail that captures the particular balancing act of the second-generation diaspora politician: rooted enough to teach the mother tongue on weekends, integrated enough to win a British ward.

## The local route up

For years the diaspora's political story in Britain was told through marquee names — a chancellor, a prime minister, a clutch of cabinet ministers. But the deeper change has been happening in town halls. Indian-origin candidates have been steadily accumulating council seats and civic chains across Hertfordshire, the West Midlands, Leicester and outer London, the unglamorous infrastructure from which national careers are eventually built.

Britain is home to roughly 1.9 million people of Indian origin, one of the country's largest minority communities and among its most electorally engaged. The 2026 local elections, a turbulent contest that saw Reform make sweeping gains and Labour lose ground across the north, also quietly returned more minority councillors to chambers up and down the country. The mayoralty — largely ceremonial, often handed to long-serving councillors — has become a visible marker of arrival for communities that a generation ago were petitioning councils rather than presiding over them.

## Why ceremonial still matters

It is easy to be cynical about a mayoral chain. The post wields little executive power; it opens fetes, chairs meetings and represents the borough at civic functions. But symbolism is not nothing, especially for a diaspora that has spent decades negotiating its place in British public life.

Kumar framed his appointment as an invitation. He hoped, he said, that a 23-year-old taking the chair would "inspire more young people to participate in local democracy." Rani's elevation a week later turned a personal milestone into a generational one: a mother and son holding civic office in adjacent authorities, both insisting on staying "rooted to their Indian heritage while proudly serving their diverse British community."

That dual loyalty — to the country left and the country chosen — is the defining condition of diaspora life, and it is rarely resolved so publicly or so warmly.

## The longer game

The more consequential test will come not in the mayor's parlour but at the ballot box for executive office. Indian-origin candidates remain underrepresented relative to their numbers in roles with real budgetary power — directly elected mayors, council leaders, parliamentary seats outside a handful of strongholds. The civic chains are the visible tip; the question is whether the community's electoral weight converts into durable institutional power, or remains concentrated in a few high-profile individuals.

For now, Borehamwood has a mayor who cannot yet rent a car without a young-driver surcharge, and a borough whose first lady of office taught half the neighbourhood's children their Hindi alphabet. It is a small story. It is also, for a community still writing itself into British public life, exactly the kind of small story that adds up.

**Sources:** IANS; India Today Global; India News Stream."""

body3 = """Every other summer, ten thousand Telugu-speaking Americans descend on a convention centre in a mid-sized US city, fill it with literary recitals, fashion shows, startup pitches and a thunderous live concert flown in from Hyderabad, and then go home. To an outsider it looks like a very large family reunion. To the diaspora, the convention circuit is something more deliberate: the load-bearing infrastructure of a community determined not to let the next generation forget where it came from.

## A calendar of belonging

The Telugu Association of North America (TANA), founded in 1977 and one of the oldest Indo-American organisations in the country, held its 19th biennial convention in Dallas this year, with organisers projecting around 10,000 attendees from across the world. The rival-cum-sibling American Telugu Association (ATA) will hold its own 19th conference and youth convention at the Baltimore Convention Center from 31 July to 2 August. Between them sit dozens of smaller "ATA Days" and regional gatherings — one in Mesa, Arizona last year drew more than 4,000 people on its own.

The scale is striking, but the more telling detail is the programming. Alongside the celebrity concerts and food festivals come literary committees flying in *avadhanam* scholars to perform feats of Telugu poetic memory, youth conventions built explicitly for American-born teenagers, business meets, SAT-prep workshops and 5K runs. This is not nostalgia tourism. It is a community building institutions to do the work that geography no longer does automatically.

## The second-generation problem

Behind the festivity sits a quiet anxiety familiar to every immigrant community: language and culture do not survive a generation by accident. The child raised in Plano or Edison speaks English at school, absorbs American pop culture, and has no village to return to each summer. Left alone, fluency in Telugu — or Tamil, or Gujarati, or Punjabi — erodes within a generation.

The conventions are, in part, an organised response. The youth tracks, the language recitals, the cultural competitions for children are engineered to give American-born kids a reason to engage with a heritage that the home country can no longer enforce. When ATA partners with IIT Hyderabad on educational programmes, or TANA's literary committee builds a weekend around classical Telugu verse, the target audience is as much the bored teenager in the back row as the nostalgic parent in the front.

## Soft power, two ways

India has noticed. Consular officials are now fixtures at these galas, and the government's pitch — diaspora as a "living bridge" — is recited from convention stages as readily as from Delhi podiums. The flow runs both ways. The associations channel charity back to Andhra Pradesh and Telangana; the home states court the conventions for investment and goodwill; politicians on both sides of the ocean find a ready-made audience of affluent, organised, civically engaged voters.

There is a faint irony in it. The same community that the conventions worry is losing its language is also, collectively, one of the most successful migrant groups in America — overrepresented in medicine, technology and entrepreneurship, and increasingly in politics. The cultural anxiety and the material confidence coexist. You build a youth convention precisely because you have the money and the institutions to do so, and precisely because you fear that success, unattended, dissolves the very identity that made it possible.

## What's next

The convention model is maturing from spectacle into infrastructure: year-round language classes, startup incubators, mentorship networks and seva drives that outlast the weekend. Whether the second and third generations show up not just for the concert but for the *avadhanam* — whether they bring their own American-born children back in twenty years — is the open question the organisers cannot yet answer.

For now, the chairs are booked, the literary stalwarts are confirmed, and somewhere in Baltimore a teenager who can barely order food in Telugu is about to spend a weekend surrounded by ten thousand people who insist that she is, unmistakably, one of them.

**Sources:** TeluguOne; South Asian Herald; India Tribune; IndiaPost."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Diaspora's Money Is Pouring Home at Record Levels. It's Also Quietly Changing Shape.",
        "subheadline": "India will take in nearly $140 billion in remittances this year. The bigger story is the shift from Gulf wages to Western capital — and how Delhi is racing to court it.",
        "slug": make_slug("india-remittances-record-140-billion-gulf-west-corridor-shift-rbi-nri-deposits"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For 18.5 million Indians abroad, sending money home is shifting from obligation to investment — and India is now pricing the bond with competitive interest rates, equity caps and property rule changes aimed squarely at the diaspora.",
        "tags": ["nri", "diaspora", "remittances", "rbi", "nri-deposits", "gulf", "finance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "SBI Research / The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/indias-remittances-to-reach-record-140-billion-in-fy26-sbi-research/article69000000.ece"},
            {"name": "Reuters — India File", "url": "https://www.reuters.com/world/india/"},
            {"name": "Mint — Diaspora dollars", "url": "https://www.livemint.com/economy"},
            {"name": "State of NRI Remittances 2026", "url": "https://indian.community/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18804128/pexels-photo-18804128.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Hands exchanging currency at a bank counter, where billions in diaspora remittances change form each year",
        "image_attribution": "Pexels",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A 23-Year-Old and His Mother Just Became Mayors a Week Apart. Both Still Teach Hindi on Weekends.",
        "subheadline": "Tushar Kumar and Parveen Rani's back-to-back Hertfordshire mayoralties are a feel-good headline — and a window into how the diaspora's British political climb now runs through the council chamber.",
        "slug": make_slug("tushar-kumar-parveen-rani-uk-mayors-hertfordshire-diaspora-council-politics"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Britain's 1.9-million-strong Indian community is building political power from the ground up — in town halls and civic chains — and the Kumar-Rani story captures the second-generation balancing act of staying rooted while serving a chosen country.",
        "tags": ["nri", "diaspora", "uk", "british-indian", "politics", "local-elections"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "IANS / IANSlive", "url": "https://ianslive.in/23-year-old-councillor-becomes-youngest-indian-origin-mayor-in-uk"},
            {"name": "India Today Global", "url": "https://www.indiatoday.in/"},
            {"name": "India News Stream", "url": "https://indianewsstream.com/23-year-old-councillor-becomes-youngest-indian-origin-mayor-in-uk/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16712338/pexels-photo-16712338.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A civic building in London, where Indian-origin councillors are steadily taking on mayoral and council roles",
        "image_attribution": "Pexels",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Every Summer, 10,000 Telugu-Americans Fill a Convention Center. It's Not Really About the Concert.",
        "subheadline": "From TANA in Dallas to ATA in Baltimore, the diaspora's convention circuit has become the load-bearing infrastructure of a community trying to keep its language alive one generation at a time.",
        "slug": make_slug("telugu-american-convention-circuit-tana-ata-diaspora-language-second-generation"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The biennial Telugu conventions are an organised answer to the second-generation problem every immigrant community faces — how to pass on a language and culture that the home country can no longer enforce from 12,000 km away.",
        "tags": ["nri", "diaspora", "telugu", "tana", "ata", "culture", "community"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "TeluguOne — 19th TANA Convention", "url": "https://www.teluguone.com/news/content/19th-tana-convention-advanced-registration-opened-156-216868.html"},
            {"name": "South Asian Herald — ATA Day Arizona", "url": "https://southasianherald.com/american-telugu-association-hosts-grand-ata-day-celebration-in-arizona-with-4000-attendees/"},
            {"name": "India Tribune — ATA 19th Conference", "url": "https://indiatribune.com/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36121661/pexels-photo-36121661.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A Bharatanatyam dancer in traditional attire, the kind of classical performance that anchors diaspora cultural conventions",
        "image_attribution": "Pexels",
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
