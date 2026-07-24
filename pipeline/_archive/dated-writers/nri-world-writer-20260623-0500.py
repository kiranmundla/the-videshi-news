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

art1_body = """The Indian diaspora in America has spent two decades collecting trophies — for the doctor of the year, the founder of the year, the philanthropist of the year. At the inaugural Icons of Impact Gala in New Jersey this month, the Global Indian Diaspora Alliance (GLO-INDIA) handed out the usual citations to the usual room of nearly 200 achievers. Then the Consul General of India in New York stood up and pitched the crowd something more concrete than a plaque: a database.

The product is the India–USA Trade Facilitation Portal, a government-backed platform built by the Consulate General in New York. Its premise is unglamorous and, for that reason, useful. It connects vetted Indian exporters, manufacturers, artisans and startups directly with American importers and buyers, and it is free to use. For a small manufacturer in Surat or a One District One Product artisan with no Manhattan distributor on speed dial, the absence of a middleman — and a middleman's margin — is the whole point.

## The numbers behind the pitch

Ambassador Binaya S. Pradhan came armed with figures. Bilateral trade between India and the United States reached a record $241 billion over the past year, he told the gala, making America India's largest trading partner for the fourth year running. Both governments have signed up to a target they call "Mission 500" — more than doubling that trade to $500 billion by 2030.

That is a steep curve, and it will not be climbed by the Reliances and Tatas alone. The portal is aimed squarely at the layer beneath them: micro, small and medium enterprises, women-led businesses, the firms that make up the bulk of Indian commerce but rarely have the resources to crack a foreign market. The platform promises virtual exhibitions, webinars on US regulatory compliance, market-entry guidance and sector-specific networking.

## Why the diaspora is the intended workforce

What makes this a diaspora story, rather than a trade-ministry press release, is who the Consul General was actually addressing. Pradhan described the nearly four-million-strong Indian-American community — doctors, founders, professors, policymakers — as a group uniquely placed to "strengthen the India–U.S. partnership and serve as a living bridge between the world's two largest democracies."

"Every great trade relationship is, at its heart, a relationship between people," he said, urging the leaders in the room to mentor entrepreneurs and broker business connections back home.

That framing is a quiet reversal of an old dynamic. For years, the diaspora's economic contribution to India was measured chiefly in remittances — money wired home to family. The portal asks for something different: not the diaspora's cash, but its address book, its knowledge of how American procurement actually works, and its willingness to vouch for a supplier 8,000 miles away.

## A familiar pattern

GLO-INDIA, which says it has more than 18,000 members across five continents, is one of a growing cluster of diaspora organisations that have moved beyond cultural programming into something closer to economic infrastructure. Its president, H.S. Panaser, called the gala a "landmark." The hyperbole is forgivable; the underlying shift is real. Increasingly, the consulates treat community galas not as ceremonial obligations but as distribution channels — places to launch a product to exactly the people who might use it.

Whether the portal works is a separate question. Government-built marketplaces have a mixed record, and a "vetted database" is only as good as the vetting and the maintenance behind it. Small exporters have heard promises of frictionless access before. But the instinct is sound: the diaspora's most valuable export to India was never its money. It was its understanding of the country it now calls home.

For the second-generation professional in New Jersey who has never thought of a Gujarati MSME as their problem to solve, that is the implicit invitation. The trophies were for what the community has already become. The portal is a bet on what it might still do.

## Sources

- The Indian Eye, "Ambassador Pradhan cites New Trade Portal as Central to Mission 500 at GLO-INDIA Gala"
- The Indian Panorama, "Global Indian Diaspora Alliance (GLO-INDIA) Hosts Landmark 'Icons of Impact Gala' in New Jersey"
"""

art2_body = """India wants the diaspora's money. The diaspora, increasingly, wants to send it. And yet for the four million Indians in the United States and the roughly two million in Canada, one of the most basic ways to bet on India's growth story — buying an Indian mutual fund — is quietly off-limits at most fund houses. The barrier is not Indian law. It is American paperwork.

## The law says yes

Start with what is permitted. Under the Foreign Exchange Management Act of 1999, specifically the Reserve Bank of India's Notification FEMA 20(R) issued in November 2017, a non-resident Indian may subscribe to units of an Indian mutual fund, on either a repatriation or non-repatriation basis, using an NRE or NRO bank account. Delhi has, if anything, been rolling out the welcome mat — easing rules to let overseas Indians channel savings into the domestic market.

So an NRI in London or Dubai or Singapore can generally walk into the Indian equity story through the front door. An NRI in New Jersey or Toronto often cannot.

## The wall America built

The obstruction is American and Canadian securities regulation, layered on top of FATCA — the Foreign Account Tax Compliance Act. FATCA requires foreign financial institutions to report on accounts held by US taxpayers, and it threatens steep penalties for getting it wrong. For an Indian asset management company, onboarding a retail investor in Ohio means absorbing a compliance burden — extra reporting, extra legal exposure, extra cost — that the modest fees on a mutual-fund unit simply do not justify.

The result is a striking gap. Of the roughly 44 SEBI-registered fund houses tracked by industry body AMFI, around 36 accept lump-sum subscriptions from resident Indians without fuss. But only eight to ten houses, depending on which registrar's list you consult, actively onboard NRIs based in the United States or Canada. For Indians elsewhere in the world, the menu is far longer.

It is a peculiar form of exclusion. The wealthiest, most financially literate slice of the diaspora — the cohort India most wants to court — is the one most likely to be turned away, precisely because of where it pays tax.

## Workarounds, and their catches

Money finds a way, and the workarounds are multiplying. The most talked-about is GIFT City, the international financial centre in Gujarat that operates under a separate regulator, the IFSCA. Funds domiciled there can be structured to accept NRI and foreign capital in US dollars, often without the investor needing a PAN card or an Indian bank account, and frequently with favourable tax treatment — no Indian capital-gains tax, with the liability falling instead in the country of residence.

Fintech startups have noticed. A wave of them is racing to secure GIFT City licences to build one-stop platforms for NRIs, bundling payments, fund distribution and broking into a single regulated stack. One such platform reported that inflows nearly doubled between the January–February and March–April periods this year, led by users in the UAE and Qatar, with most money flowing into dollar-denominated fixed deposits.

But GIFT City is not a retail solution for everyone. Many of its richer products — alternative investment funds, portfolio management services — carry minimum tickets running into hundreds of thousands of dollars, gated behind "accredited investor" thresholds. The schoolteacher in Sacramento who wants to put $500 a month into an Indian index fund is still largely stuck.

## A structural problem, not a temporary one

Some in the industry caution that the recent surge in NRI inflows is cyclical — a defensive move driven by global market jitters rather than a permanent change in behaviour. That may be true of the volumes. The structural barrier is more durable.

Until either American compliance costs fall or Indian fund houses decide the US-Canada market is worth the trouble, the diaspora's two largest and richest communities will keep investing in India the hard way — through a thin slice of accommodating AMCs, through GIFT City's dollar wrappers, or not at all. India has spent years asking its overseas children to come home, financially. For millions of them, the door home runs through a tax form they did not design and cannot avoid.

## Sources

- Oquilia, "NRI Mutual Fund Investment: FEMA Rules, Gift Mode, and Why Some AMCs Refuse US/Canada NRIs"
- Livemint, "Startups chase GIFT City licences to win NRI investors, but will the rush last?"
"""

art3_body = """Washington has a museum for almost everyone. The African American story has its monument on the National Mall; the American Indian, the Holocaust, the spy, the postage stamp — all have their dedicated halls. What the capital does not have is a permanent institution telling the story of India, a civilisation that supplies one of the most influential immigrant communities in the country. A group of Indian-Americans has decided, after nearly eight years of quiet preparation, to fix that.

## Eleven thousand years, validated

The project is the India Heritage Center, led by Atlanta-based educationist and community leader Dr Amitabh Sharma. The pitch is ambitious to the point of audacity: a permanent museum in or near Washington, D.C., narrating India's journey from ancient civilisation to modern nationhood — a span Sharma puts at more than 11,000 years.

What is notable is less the scale than the caution. Sharma says the team spent years not raising money or scouting sites but gathering and validating historical material. "It took us a long time to amalgamate or to collate humongous amount of data over 11,000 years and then to get that data validated," he told IANS, "so that tomorrow nobody can raise a finger or raise an objection."

That defensiveness is telling. For a diaspora acutely conscious that its homeland's history is often narrated by others — and frequently contested — the instinct is to build a case that cannot be picked apart before laying a single brick.

## The blueprint

The India Heritage Center is registered as a 501(c)(3) non-profit and estimates the total project cost at between $12 million and $14 million. The vision is a 20,000-square-foot complex with ten galleries, a 350-seat auditorium, a library, reception facilities and a gift centre. Organisers plan to lean heavily on technology — virtual and augmented reality, immersive audio-visual systems, murals and artefacts — to present India's story to a global audience rather than only to homesick Indians.

Funding is to come from high-net-worth individuals, corporate sponsors, grants, crowdfunding and community contributions, with naming rights to galleries dangled as an incentive. Site selection in the Washington area is still under way.

## Why now, and why here

Sharma is careful to frame the museum as collective property. "This is not my project. It is not your project. It is the entire Indian community's project," he said, adding that the most common reaction he hears is a slightly indignant "why wasn't it done earlier?"

The timing is not accidental. The Indian-American community has, in a generation, moved from the margins to the centre of American life — running corporations, sitting in Congress, shaping technology. With that arrival comes a familiar second-generation anxiety: the children and grandchildren of immigrants growing up with a thinning connection to where their families came from. A museum is, among other things, an answer to that worry — a place to take a teenager who knows the Marvel canon better than the Mahabharata.

## A crowded idea

The India Heritage Center is not alone in the impulse. The Global Organization of People of Indian Origin has floated its own proposal for an Indian Diaspora Museum, complete with a "Migration Theatre" tracing the journey from India to distant shores — though its backers have suggested Delhi, not Washington, as the home. The competing visions point to a diaspora wrestling with the same question in different cities: who gets to tell the story, and where should it be told?

For now, the India Heritage Center has a registration, a budget, a decade of validated research and an encouraging response from the community. What it does not yet have is a building, the bulk of $14 million, or a site. The hardest part of any monument is not the marble. It is persuading a scattered, busy, generous community that the story is worth the cost of telling — permanently, and in the one city where America keeps its official memory.

## Sources

- IndiaPost / IANS, "Indian Diaspora Pushes For Landmark Museum In Washington"
- The Indian Eye, "GOPIO proposes Indian Diaspora Museum to honor global Indian journey"
"""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Diaspora Has Spent 20 Years Collecting Trophies. India Just Handed It a Database Instead.",
        "subheadline": "At a New Jersey gala for Indian-American achievers, the Consul General launched a free trade portal — and asked the room for its address book, not its cash.",
        "slug": make_slug("glo-india-icons-of-impact-gala-trade-facilitation-portal-mission-500-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The India-USA Trade Facilitation Portal reframes the diaspora's economic role: not remittances, but using its knowledge of American markets to connect small Indian exporters with US buyers as part of the $500bn Mission 500 trade target.",
        "tags": ["nri", "diaspora", "trade", "GLO-INDIA", "Mission 500", "Indian American"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/04/ambassador-pradhan-cites-new-trade-portal-as-central-to-mission-500-at-glo-india-gala/"},
            {"name": "The Indian Panorama", "url": "https://theindianpanorama.news/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/15551978/pexels-photo-15551978.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Elegantly dressed guests gathered at an evening community gala reception",
        "image_attribution": "Pexels",
        "body": art1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Says NRIs Can Buy Its Mutual Funds. For Indians in America and Canada, Most Fund Houses Say No Anyway.",
        "subheadline": "The barrier isn't Indian law — it's FATCA. Only eight to ten of India's 44 fund houses will onboard US and Canadian NRIs, pushing the diaspora's richest cohort toward GIFT City workarounds.",
        "slug": make_slug("nri-mutual-funds-fatca-us-canada-amc-refuse-gift-city-fema-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The US and Canadian diaspora — India's wealthiest and most courted overseas communities — are the ones most often locked out of Indian mutual funds, because FATCA compliance costs make AMCs refuse them. A structural exclusion built into the diaspora's tax status.",
        "tags": ["nri", "diaspora", "FATCA", "mutual funds", "GIFT City", "NRI investment", "FEMA"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Oquilia", "url": "https://oquilia.com/"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/startups-chase-gift-city-licences-to-win-nri-investors-but-will-the-rush-last"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/28682349/pexels-photo-28682349.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A stock trading app interface showing market data on a smartphone",
        "image_attribution": "Pexels",
        "body": art2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Washington Has a Museum for Almost Everyone. A Group of Indian-Americans Is Tired of the Gap.",
        "subheadline": "After eight years validating 11,000 years of history, the team behind the India Heritage Center wants a $14 million permanent home for India's story in the US capital.",
        "slug": make_slug("india-heritage-center-museum-washington-dc-amitabh-sharma-diaspora-history"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A second-generation anxiety made physical: as Indian-Americans reach the center of US life, they worry their children are losing the connection to India's history. The India Heritage Center is a bet that a permanent museum in Washington can hold that thread.",
        "tags": ["nri", "diaspora", "museum", "India Heritage Center", "heritage", "Indian American"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "IndiaPost / IANS", "url": "https://www.indiapost.com/"},
            {"name": "IANS Live", "url": "https://ianslive.in/"}
        ]),
        "score_total": 71,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29608796/pexels-photo-29608796.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A bright museum hallway lined with exhibits and open walkways",
        "image_attribution": "Pexels",
        "body": art3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
