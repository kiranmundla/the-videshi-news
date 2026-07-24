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
        "headline": "Five South Asian Candidates Just Won Georgia Primaries. The Peach State's Political Map Is Being Redrawn.",
        "subheadline": "From the first Sikh elected official in Georgia history to a potential first South Asian lieutenant governor, Tuesday's results mark a generational shift in who holds power in America's most contested battleground.",
        "slug": make_slug("south-asian-georgia-primaries-jyot-singh-nabilah-parkes"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian and South Asian Americans are no longer a quiet donor class in American politics — they are winning primaries, building political infrastructure, and reshaping representation in one of the country's most competitive states.",
        "tags": ["nri", "diaspora", "politics", "indian-american", "georgia", "elections"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/21/indian-american-impact-congratulates-endorsed-candidates-on-historic-wins-in-georgia/"},
            {"name": "Indian American Impact", "url": "https://www.indianamericanimpact.com/"},
            {"name": "The American Bazaar", "url": "https://www.americanbazaaronline.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5130431/pexels-photo-5130431.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Georgia State Capitol in Atlanta, where a new generation of South Asian American lawmakers is heading.",
        "body": """When Jyot Singh won the Democratic primary for Georgia House District 97 on Tuesday, he did not merely defeat his opponents. He ended a wait that Georgia's Sikh community did not know it was enduring. Singh is now on track to become the first Sikh elected official in the state's history.

He was not the only South Asian name on the winners' list. Across multiple races in Georgia's May primaries, Indian and South Asian American candidates compiled a record that Indian American Impact — the PAC that endorsed all of them — called "historic." The organisation, which has backed more than 200 candidates since its founding in 2016, had reason to be pleased. Every single one of its Georgia endorsements either won outright or advanced to runoff elections.

## The headline races

The most closely watched result belonged to Nabilah Islam Parkes, who advanced to a runoff in the race for lieutenant governor. If she wins, she would become the first South Asian and Asian American lieutenant governor nominee from any party in Georgia history. Parkes, who already served as a state senator representing the 7th district, has built her profile on healthcare access and immigrant community advocacy — issues that resonate well beyond Atlanta's South Asian enclaves.

Saira Draper won a competitive primary for State Senate District 44. Rahul Garabadu advanced to a runoff in State Senate District 7. And Akbar Ali, already the youngest state legislator in Georgia, secured the Democratic nomination for House District 106, ensuring he will continue in the role he has already been filling.

## Why Georgia, why now

Georgia is home to more than 600,000 Asian American residents, a number that has grown sharply over the past decade. Metro Atlanta, in particular, has become one of the fastest-growing Indian American population centres in the country, driven by the technology sector, healthcare, and higher education. The state's South Asian population is no longer concentrated in a few zip codes. It has spread into suburban districts — Gwinnett, Forsyth, DeKalb — where primary elections are genuinely competitive.

This demographic shift has political consequences. Indian American Impact has marshalled upwards of $20 million in candidate support and voter mobilisation since its inception. Chintan Patel, the organisation's executive director, framed Tuesday's results as evidence of "the growing political power and representation of our communities." That is not boilerplate. In Georgia, where statewide elections are routinely decided by tens of thousands of votes, a well-organised ethnic voting bloc is no longer a footnote. It is a factor.

## A pattern, not a fluke

The Georgia results follow a national trend. Indian Americans have been winning elections at every level — from school boards in New Jersey to congressional seats in California. But Georgia is different. It is not a blue state where diverse candidates benefit from automatic Democratic supermajorities. It is a genuine swing state, where winning a primary means facing a real general election, where coalitions must be broad and arguments must be persuasive.

The candidates who won on Tuesday were not running as ethnic representatives. Singh's platform centred on education and infrastructure. Draper focused on housing affordability. Parkes built a campaign around economic relief for working families. Their South Asian heritage was a fact, not a platform — which, paradoxically, is how ethnic political power matures.

## What comes next

For the NRI community watching from abroad, these results carry a particular resonance. The Indian diaspora has long measured its success in America through corporate titles and academic honours. Political office — especially in the South, especially in contested races — is a different kind of marker. It suggests a community that is not merely succeeding within American institutions but beginning to shape them.

The runoff elections for Parkes and Garabadu will determine whether this wave crests or recedes. But the signal from Tuesday is clear enough: in Georgia, South Asian Americans are no longer just voting. They are governing."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Chaiiwala, the UK's Biggest Indian Street Food Chain, Is About to Open in America. It Already Has 900 US Sites in Mind.",
        "subheadline": "The Leicester-born brand that turned karak chai and samosa chaat into a £89 million business across 115 UK stores is targeting Houston for its first permanent American location — with ambitions that make its British success look like a warm-up.",
        "slug": make_slug("chaiiwala-us-expansion-houston-indian-street-food"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Chaiiwala's transatlantic expansion is a test case for whether diaspora comfort food can break into the American mainstream QSR market — and whether the NRI communities in Houston, New York, and beyond will serve as a launchpad or a ceiling.",
        "tags": ["nri", "diaspora", "business", "food", "chaiiwala", "restaurants", "uk"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Grocer", "url": "https://www.thegrocer.co.uk/chaiiwala-sales-jump-35-amid-global-expansion/700469.article"},
            {"name": "Hospitality Week", "url": "https://hospitality-week.co.uk/chaiiwala-hosts-texas-pop-up-events-ahead-of-2026-us-launch/"},
            {"name": "Restaurant Online", "url": "https://www.restaurantonline.co.uk/Article/2026/05/01/chaiiwala-opens-first-24-hour-drive-thru"},
            {"name": "Foodservice Equipment Journal", "url": "https://www.foodserviceequipmentjournal.com/chaiiwala-teases-us-market-with-pop-up-series/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/34324342/pexels-photo-34324342.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A vendor pours chai into small glasses — the street-side ritual that Chaiiwala is packaging for the American QSR market.",
        "body": """In 2015, Sohail Ali and Muhummed Ibrahim opened a small Indian street food café in Leicester, a city in England's Midlands with one of the highest concentrations of South Asians in Britain. They called it Chaiiwala. The menu was simple: karak chai brewed strong enough to wake the dead, samosa chaat, roti wraps, Bombay bowls. The kind of food that every desi family eats at home but that British high streets had somehow never formalised into a chain.

A decade later, Chaiiwala has 115 locations across the UK, 23 in Canada, a handful in Dubai, global sales of £89.4 million (up 35% in 2024), and a plan to open 500 stores worldwide over the next decade. It has also scoped 900 potential US sites. The first permanent American location is expected to open in 2026, most likely in Houston, Texas.

## The Houston play

Earlier this year, Chaiiwala completed a series of pop-up events in Houston — a city the company identified as a priority market. Houston is not an accidental choice. It has one of the largest and most diverse South Asian populations in the American South, with well-established Indian, Pakistani, and Bangladeshi communities that span Sugar Land, the Hillcroft corridor, and suburban Fort Bend County.

Nazibur Rahman, Chaiiwala's country manager for the US and Canada, described the pop-ups as "a total success." The company is now in discussions with local franchise partners. The strategy mirrors what worked in Canada: find operators who understand the community, let them adapt to local tastes, and build outward from a diaspora-dense beachhead.

## More than a desi niche

What makes Chaiiwala interesting — and potentially formidable in the American market — is that it has already escaped the ethnic food ghetto in Britain. Its customers are not exclusively South Asian. The drive-thru format, now operating at five UK locations including a new 24-hour site in Blackburn, attracts the same late-night crowd that would otherwise default to McDonald's or KFC. High-protein breakfast wraps, launched last year, sold more than a million units in their first 12 weeks. A container-format store at the Watford Gap motorway services targets lorry drivers and road-trippers who have never heard of karak chai and do not care about its provenance, only that it tastes good.

CFO Abdul Piranie has said the brand's strategy is about "introducing more people to what we have to offer" through formats that meet customers where they already are — petrol stations, hospital cafeterias, university campuses, airports. This is not the approach of a niche ethnic eatery. It is the playbook of Pret A Manger or Wingstop.

## The American obstacle course

Success in the UK does not guarantee success in the US. The American QSR landscape is brutally competitive, dominated by incumbents with deep pockets and decades of brand recognition. Indian food, despite its global popularity, remains underrepresented in America's fast-casual tier. There is no Indian equivalent of Chipotle or Sweetgreen — a format that translates complex flavours into quick, customisable, counter-service meals at scale.

Chaiiwala is not the only brand attempting this. Chaiwale & Co., a California-based Indian fusion café, recently opened a franchised location in San Diego. Curry Up Now, the Bay Area chain, has been expanding with mixed results. The market is ready for an Indian QSR breakout; the question is whether any single brand can achieve the consistency and supply-chain discipline required to scale nationally.

## What NRIs should watch for

For diaspora observers, Chaiiwala's US launch is a bellwether. The brand was built by British-born South Asians for a British audience that happened to include their own community. It did not apologise for what it was or dilute its identity for mainstream acceptance. If that formula translates across the Atlantic — if Americans will queue at a drive-thru for samosa chaat the way they queue for chicken sandwiches — it will mark a genuine shift in how Indian food is perceived and consumed in the world's largest restaurant market.

The 900-site ambition may sound like corporate bravado. But Chaiiwala's trajectory in the UK suggests it is, at minimum, a serious attempt. The diaspora built the customer base. The question now is whether America is ready for what the diaspora already knows."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Asma Khan Is Moving Darjeeling Express Again. The Fourth Time Might Be the One That Sticks.",
        "subheadline": "The Netflix-famous chef, cookbook author, and accidental feminist icon is taking her all-female kitchen from Soho to a two-floor site on Rupert Street — a move that says as much about London's diaspora dining scene as it does about one woman's stubbornness.",
        "slug": make_slug("asma-khan-darjeeling-express-chinatown-london-move"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Asma Khan's restaurant is one of the most visible expressions of Indian diaspora culture in London — a place where Bengali and Hyderabadi home cooking, feminist employment principles, and the immigrant's stubborn refusal to stay put converge in a single dining room.",
        "tags": ["nri", "diaspora", "food", "london", "asma-khan", "darjeeling-express", "restaurants"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "London The Inside", "url": "https://londontheinside.com/best-new-restaurants-london/"},
            {"name": "Hot Dinners", "url": "https://www.hot-dinners.com/2025/Gastroblog/Latest-news/asma-khans-darjeeling-express-is-on-the-move-again"},
            {"name": "The Staff Canteen", "url": "https://www.thestaffcanteen.com/news/asma-khan-to-move-darjeeling-express"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/fb/Asma2023.jpg",
        "image_caption": "Asma Khan, the founder of Darjeeling Express and the first British chef profiled on Netflix's Chef's Table.",
        "body": """Asma Khan has a habit of moving. In 2014, Darjeeling Express was a pop-up at a Soho pub called The Sun & 13 Cantons. In 2017, it became a permanent fixture in Kingly Court. Then came the pandemic, a relocation to Covent Garden, a stint back in Kingly Court, and a pop-up interlude in Kensington. Now, a decade after she first served kosha mangsho to curious Londoners, Khan is moving again — this time to 36-40 Rupert Street, in the heart of Chinatown, taking over the space that once housed Hovarda.

Darjeeling Express 4.0, as it might fairly be called, will be substantially larger than any of its predecessors. Two floors. Room for 130 diners. A kitchen big enough that Khan's all-female team — the detail she mentions before anything else — will no longer be cooking in what amounted to a galley.

## The significance of the kitchen

The all-female kitchen is not a gimmick. It is the structural foundation of everything Khan has built. Her cooks are not professionally trained chefs recruited through the usual London restaurant pipeline. They are women — many of them first-generation immigrants, some former housewives — who learned to cook in their families' kitchens in India. Khan has described them as "the real stars of the show," and she means it literally: she says she needs a bigger space specifically so diners can see them work.

"We are the only restaurant in the world with a female founder and all-female kitchen of housewives," Khan told The Staff Canteen. "I need to show them off because they are my pride and joy."

This is not standard hospitality marketing. Khan, who was born into a Rajput-Bengali family in Aligarh and trained as a constitutional lawyer at Cambridge, came to professional cooking late and sideways. She started a supper club in her Kensington home in 2012, driven by recipes her family had been cooking for generations. The trajectory from home cook to Netflix star — she was the first British chef profiled on Chef's Table, in 2019 — happened without her ever adopting the vocabulary or ego structure of London's professional chef class.

## What Rupert Street means

The new location is on the western edge of Chinatown, a neighbourhood that has been quietly diversifying its restaurant offering for years. Khan's arrival signals something about the district's evolution: the old binary of "Chinatown or the West End" is dissolving into a more fluid geography of Asian dining in central London. An Indian restaurant on Rupert Street, between the old Cantonese stalwarts and the theatre district, is no longer a novelty. It is a statement of belonging.

The site is backed by Shaftesbury Capital, the property company that manages much of Soho and Chinatown. Their support — Khan credits them with finding a space that keeps her team "front and centre" — suggests a commercial bet that Darjeeling Express has graduated from cult favourite to reliable destination.

## The menu: bigger, not different

Khan has promised an expanded menu that leans into the dishes her regulars already love: kathi rolls, keema, samosa, vada pav, falooda. She has hinted at bringing back a midweek biryani — the dish that made Darjeeling Express's supper clubs legendary. The cuisine remains a mix of Bengali, Hyderabadi, and Kolkatan traditions, drawn from family recipes rather than restaurant trends.

For the Indian diaspora in London — a city with no shortage of Indian restaurants, from high-end Mayfair establishments to Tooting curry houses — Darjeeling Express occupies an unusual position. It is neither a fine-dining temple nor a budget canteen. It is something closer to what the food actually is at home: unpretentious, generous, cooked by women who learned it from their mothers.

## A diaspora story in four moves

Each of Darjeeling Express's relocations tells a different chapter of the immigrant restaurant story. The pop-up was the arrival: uncertain, borrowed, provisional. Kingly Court was the establishment of a foothold. Covent Garden was ambition. The return to Kingly Court was pragmatism. And Rupert Street, if it works, is permanence — a two-floor restaurant with a proper lease and a landlord invested in its success.

Khan herself has drawn the analogy. "Our story has been unconventional from the start," she has said. "This move is an affirmation for every individual that you belong anywhere and everywhere."

The restaurant is expected to open in summer 2026. Whether it stays put this time is, of course, an open question. Asma Khan has a habit of moving. But the spaces keep getting bigger."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
