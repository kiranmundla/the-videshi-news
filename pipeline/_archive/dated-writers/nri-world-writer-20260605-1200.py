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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A New Manhattan Restaurant Maps the Diaspora Through Its Menu. The Atlas Is Delicious.",
        "subheadline": "Chef Aarthi Sampath's Drāvida traces South Asian flavours from Trinidad to Sri Lanka to Guyana — cuisines born in migration, now served in a restored East Village building with century-old brick ovens.",
        "slug": make_slug("dravida-restaurant-nyc-aarthi-sampath-south-asian-diaspora-cuisine"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Drāvida represents a new wave of diaspora dining that refuses to flatten South Asian food into a single 'Indian' category — it celebrates the culinary traditions born when Indians moved to the Caribbean, East Africa, Southeast Asia and beyond, giving second-generation diners a menu that mirrors their own layered identities.",
        "tags": ["nri", "diaspora", "food", "restaurants", "new-york", "culture"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Restaurant India", "url": "https://www.restaurantindia.in/news/restaurant-india-news-chef-aarthi-sampath-debuts-dr-vida-celebrating-south-asian-diaspora-cuisine-in.n16339"},
            {"name": "NewsFlixBharat", "url": "https://newsflixbharat.com/menka-soni-becomes-first-indian-american-woman-elected-to-redmond-city-council-takes-oath-on-bhagavad-gita/"},
            {"name": "CookUnity / Industry Reports", "url": "https://www.cookunity.com"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/3531700/pexels-photo-3531700.jpeg",
        "image_caption": "Hands preparing a South Asian dish with aromatic spices in a cooking pan",
        "image_attribution": "Pexels",
        "body": """When Aarthi Sampath sat down to write the concept for her first restaurant in 2019, she had a problem that most chefs would envy: too many cuisines to choose from. Not because she couldn't decide on a style, but because the food she wanted to cook didn't belong to any single country. It belonged to a diaspora.

Six years and one pandemic later, Drāvida opened this week at 211 1st Avenue in Manhattan's East Village. The name nods to the Dravidian cultures of southern India, but the menu roams far wider — through Trinidad, Guyana, Sri Lanka, Pakistan, Nepal, South Africa, and the Indo-Malay world. Every dish on it was shaped by migration.

## Home Cooking, Restaurant Stage

Sampath, who moved from Mumbai to New York in 2013, spent her first decade in the city's most exacting kitchens: Junoon, The Breslin, the Rainbow Room. She won on *Chopped* and *Beat Bobby Flay*, building a national television profile that would have supported a conventional fine-dining launch. She chose to go sideways instead.

"This restaurant is for New Yorkers who haven't seen their food represented," she told Restaurant India. "For the communities that built this city and whose cuisines haven't always had a place at the table."

The result is a menu that reads like an itinerary of indentured-labour routes and merchant-ship landings. Doubles, the Trinidadian street snack of fried bara and curried chickpeas, sits alongside Oxtail Bunny Chow — a South African dish born in Durban's Indian quarter, served in a hollowed-out loaf of bread. Idli and Shrimp borrows the South Indian staple and threads it through Indonesian influence. The Nasi Kandar Feast is an Indo-Malay spread of rice, curries, and accompaniments that could plausibly appear at a hawker stall in Penang.

None of these dishes are Indian in the way that butter chicken or biryani are Indian. They are what Indian food becomes when it travels — when it lands in a new country, absorbs local ingredients, and produces something that belongs fully to neither place and entirely to both.

## The Building Tells Its Own Story

Drāvida occupies two floors of a restored hundred-year-old building that includes original brick ovens. The ground floor is a 40-seat dining room. Below it, a 20-seat speakeasy called Jam and Jaggery serves cocktails built on South Asian flavours — a Passionfruit Lassi, a Dravida Highball with floral and citrus notes, an Orange Cream that riffs on childhood desserts. The drinks list is less a gimmick than a statement: even the bar program refuses to treat South Asian ingredients as "exotic" add-ons. They are the foundation.

## A Larger Shift

Drāvida arrives in a market that is quietly rewriting the economics of South Asian dining in America. For decades, Indian restaurants in the United States occupied two lanes: budget buffets or aspirational tasting menus modelled on Western fine dining. A newer cohort — Dhamaka, Semma, Adda, Masalawala — has pushed regional specificity, showcasing Bihari or Chettinad or Bengali cooking that mainstream "Indian" menus once ignored.

Sampath's contribution is to push the frame outward from India itself. Drāvida is not a regional Indian restaurant. It is a diaspora restaurant, a category that barely existed five years ago and that now reflects the actual eating habits of South Asian families who have lived through multiple migrations.

There is a commercial logic as well. Through CookUnity, the meal-delivery platform, Sampath already sells approximately 50,000 meals a week across American markets. That scale gave her a data set few restaurant entrepreneurs possess: she knows which diaspora flavours Americans are already buying, even when they don't know the geography behind them.

## What It Means

For the roughly five million Indian Americans in the United States, Drāvida carries a recognition that standard restaurant categories tend to erase. Most diaspora families cook from multiple traditions at home — a weeknight dal followed by a weekend curry adapted from a grandmother's Trinidad recipe, followed by a Malaysian-style noodle dish learned from a college roommate. No single national cuisine captures that.

Sampath's bet is that a restaurant can. Whether she's right will be settled at the table, one plate of Doubles at a time."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Diaspora Just Got Its Own Trade Portal. India's New York Consulate Built It.",
        "subheadline": "At GLO-INDIA's inaugural Icons of Impact gala, Ambassador Binaya Pradhan unveiled a digital platform connecting Indian exporters with American buyers — a practical tool aimed at doubling bilateral trade to $500 billion by 2030.",
        "slug": make_slug("glo-india-gala-trade-portal-diaspora-mission-500"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The India-USA Trade Facilitation Portal positions diaspora professionals as the connective tissue in bilateral commerce, offering MSMEs, women-led businesses, and ODOP artisans a bridge to American markets that previously required expensive intermediaries.",
        "tags": ["nri", "diaspora", "trade", "business", "glo-india", "mission-500"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/04/ambassador-pradhan-cites-new-trade-portal-as-central-to-mission-500-at-glo-india-gala/"},
            {"name": "Ministry of Commerce and Industry", "url": "https://commerce.gov.in"},
            {"name": "GLO-INDIA", "url": "https://gloindia.org"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/8847041/pexels-photo-8847041.jpeg",
        "image_caption": "Professionals deliberating at a diaspora networking event",
        "image_attribution": "Pexels",
        "body": """For a community that has produced CEOs at Microsoft, Google, and IBM, the Indian diaspora's infrastructure for actually *doing business* between the two countries has remained remarkably informal. Most cross-border deals still run through personal networks, WhatsApp groups, and introductions at Diwali galas. On June 4, India's Consulate General in New York tried to change that.

At the inaugural Icons of Impact gala hosted by the Global Indian Diaspora Alliance (GLO-INDIA), Ambassador Binaya S. Pradhan introduced the India-USA Trade Facilitation Portal — a free, government-backed digital platform that connects verified Indian exporters, manufacturers, artisans, and startups directly with American importers and buyers.

## The Numbers Behind the Portal

The launch comes at a moment when the bilateral relationship is producing records. India-US trade hit $241 billion over the past year, making the United States India's largest trading partner for the fourth consecutive year. Both governments have set a target they call Mission 500: doubling that figure to $500 billion by 2030.

Those are macro numbers. The portal is a micro tool — and that is precisely the point. It is designed for the businesses that the macro figures tend to miss: small and medium enterprises without trade-show budgets, women-led firms without Washington lobbyists, One District One Product artisans who make exquisite goods but have never navigated a US customs form.

The platform offers virtual exhibitions, webinars on American regulatory compliance, market-entry guidance, sector-specific networking, and dedicated support for MSMEs. It costs nothing to use. In a country where micro-enterprises contribute roughly 30 per cent of GDP but struggle disproportionately with export bureaucracy, that matters.

## Why the Diaspora Is the Delivery Mechanism

Ambassador Pradhan, addressing an audience of nearly 200 diaspora leaders, academics, and legislators, framed the portal as an extension of the community itself. "Every great trade relationship is, at its heart, a relationship between people," he said. The four million Indian Americans in the United States, he argued, include doctors, business founders, professors, policymakers, and entrepreneurs whose understanding of both countries positions them as a "living bridge between the world's two largest democracies."

It is a familiar metaphor, but the portal gives it a concrete application. A diaspora entrepreneur who runs a grocery distribution business in New Jersey can now introduce a spice cooperative in Rajasthan to his American retail contacts through a verified, government-supported channel. A tech founder in the Bay Area can discover an MSME in Pune building components she needs. The matchmaking is the same kind that happens at gala dinners; the portal is trying to make it happen at scale.

## GLO-INDIA's Bet

The gala itself was a statement of ambition. GLO-INDIA, which claims more than 18,000 members across five continents, used its inaugural Icons of Impact event to position the organisation as a serious player in the diaspora's institutional landscape. H.S. Panaser, GLO-INDIA's president, called the evening a platform to "spotlight significant new initiatives aimed at strengthening economic ties."

That language is diplomatic, but the subtext is competitive. The Indian diaspora in the United States is served by a crowded field of organisations — Indiaspora, GOPIO, TiE, ASEI, and dozens of regional and linguistic associations. What most of them lack is a *transactional* tool: something that converts networking into verifiable business activity. The Trade Facilitation Portal, by attaching itself to GLO-INDIA's event, signals that the organisation intends to be more than a social club.

## The Harder Question

Whether a government portal can actually shift trade volumes is a different matter. India has a long history of launching digital platforms that start strong and decay into bureaucratic neglect. The portal's survival will depend on whether the Consulate maintains it as a living product — updating exporter databases, refreshing webinar calendars, and responding to user queries at the speed of commerce rather than the speed of government.

The diaspora, for its part, has proven it can build economic bridges when the incentives align. Remittances to India are on track to exceed $140 billion in the current fiscal year. NRI investment in GIFT City funds tripled in the last quarter. The capital and the intent are there.

What has been missing is plumbing — reliable, institutionalised channels through which small-scale business can flow as easily as large-scale capital. The Trade Facilitation Portal is a plumbing project. It is not glamorous. It may, however, be exactly what Mission 500 requires."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Man Tore an Indian Flag Outside Frisco City Hall. The Community's Response Said More Than the Video.",
        "subheadline": "An anti-immigration protest in a fast-growing North Texas suburb turned personal on June 3 when a protester ripped the Indian tricolour while anti-India slogans echoed behind him. For Frisco's Indian American families, the incident crystallised tensions they had been navigating quietly for months.",
        "slug": make_slug("frisco-texas-indian-flag-torn-protest-diaspora-community"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Frisco incident exposes the friction between rapid Indian American demographic growth in Sun Belt suburbs and a broader nativist backlash — forcing a community that has largely preferred quiet achievement to confront the limits of that strategy.",
        "tags": ["nri", "diaspora", "hate-crime", "community-safety", "texas", "indian-american"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "NRI Page", "url": "https://nripage.com/article/frisco-city-hall-indian-flag-video-raises-community-concern"},
            {"name": "NRI Page", "url": "https://nripage.com/article/indian-americans-contributions-stand-out-after-frisco-flag-incident"},
            {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/research/2026/02/indian-americans-in-a-time-of-turbulence-2026-survey-results"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/33953254/pexels-photo-33953254.jpeg",
        "image_caption": "Indian Americans gathered at a community event celebrating cultural heritage",
        "image_attribution": "Pexels",
        "body": """The video is fifteen seconds long and requires no narration. A man stands outside Frisco City Hall on the afternoon of June 3, 2026, tears an Indian national flag, and walks away. Behind him, voices chant anti-India slogans. The clip, shared widely on X by conservative commentator Elijah Schaffer and attributed to Channel6ixNEWS, had been viewed hundreds of thousands of times before most of Frisco's Indian American families saw it over dinner.

Frisco is a fast-growing suburb in the Dallas-Fort Worth metroplex. Its population has roughly tripled in two decades. A significant share of that growth has come from Indian American families — software engineers, healthcare professionals, and small-business owners drawn by strong schools, new construction, and corporate campuses. The city's changing demographics have been part of local public debate for months. The flag-tearing made that debate visceral.

## What Happened

The incident occurred during what reports describe as an anti-immigration protest outside Frisco City Hall. The available reporting, primarily from NRI Page and social media accounts, does not include an official police statement confirming arrests, charges, or whether the episode is being investigated as a hate crime. No mainstream Texas outlet has, as of this writing, published a detailed account.

That gap itself is part of the story. For Indian Americans watching the video, the absence of institutional response is a familiar experience. The Carnegie Endowment's 2026 Indian American Attitudes Survey, published in February, found that one in four Indian Americans reported being called a slur since the start of 2025. Nine per cent said they had been physically threatened. Six per cent reported property damage. Roughly one in eight cited some other form of harassment. The numbers are not catastrophic, but they are not marginal either — and they describe a community of nearly five million people.

## Beyond the Video

The community's response to the Frisco incident was swift, but it took a particular form. Rather than organising counter-protests or demanding arrests — the playbook followed by other minority communities after similar episodes — Indian American voices online pivoted almost immediately to a recitation of contributions. NRI Page published a video commentary headlined "Indian Americans' Contributions Cannot Be Erased," listing the community's presence in technology, medicine, education, entrepreneurship, and public life.

It is a response that reflects both pride and calculation. Indian Americans have built their position in the United States largely through professional achievement, economic integration, and strategic invisibility. The community tends to avoid confrontation, preferring to let résumés speak for themselves. When a man tears your flag, though, a résumé does not quite meet the moment.

Some community members have begun to ask whether that instinct — respond to hatred with a list of accomplishments — is adequate. "We keep proving our worth," one commenter on the NRI Page post wrote. "At what point do we stop auditioning for acceptance in a country where we pay taxes, create jobs, and raise families?"

## The North Texas Context

Frisco is not an isolated case. North Texas has experienced a broader pattern of tensions around immigration, demographic change, and public criticism of Indian immigration specifically. Anti-Indian rhetoric has found traction in corners of social media that frame the H-1B visa programme and Indian population growth as threats to American workers — a narrative that elides the distinction between immigration policy (a legitimate subject of debate) and ethnic hostility (which is not).

For Indian American families in Frisco, the distinction matters daily. Their children attend schools where they are sometimes the plurality. Their businesses serve diverse customers. Their temple events draw hundreds. They are, by most measures, among the most integrated immigrant communities in American history. The flag-tearing is a reminder that integration does not confer immunity.

## What Comes Next

The incident has renewed discussion about public safety, free speech, and how local leaders should respond when political protests include actions or language that residents experience as threatening. Some community organisations have called for Frisco officials to issue a formal statement condemning the flag-tearing. Others have advocated for enhanced security at temples and cultural centres.

The deeper question is structural. Indian Americans are the fastest-growing Asian-alone group in the United States, having surpassed Chinese Americans in the 2020 census with a 55 per cent growth rate over the preceding decade. That growth is concentrated in exactly the kind of Sun Belt suburbs — Frisco, Sugar Land, Alpharetta, Edison — where demographic change is most visible and most politically charged.

The community's response to this particular moment will likely shape how it navigates the next one. A torn flag is cheap symbolism. How a community of five million answers it is not."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
