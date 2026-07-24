#!/usr/bin/env python3
"""Insert 3 fresh NRI World articles into p2_articles (status=review)."""
import os, json, uuid, datetime, sys
import requests

def load_env(path=os.path.expanduser("~/.env.supabase")):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k, v)

load_env()
URL = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def wc(body):
    return len(body.split())

# ---------------------------------------------------------------------------
# Article 1 — GOPIO-CT 20th Anniversary
# ---------------------------------------------------------------------------
gopio_body = """The Global Organization of People of Indian Origin's Connecticut chapter marked two decades of community work on June 13, honouring five Indian-American leaders and handing $50,000 to local charities at a banquet in Darien. The evening drew several hundred guests and underscored how a once-modest immigrant network has grown into one of the most durable diaspora institutions in the north-eastern United States.

Founded in 2006, GOPIO-CT began as a handful of professionals meeting to swap notes on settling into a new country. Twenty years on, it runs health fairs, college-scholarship drives, senior-citizen programmes and an annual civic-awareness series that has hosted mayors, senators and police chiefs. The anniversary banquet was less a celebration of nostalgia than a stocktaking of that institutional weight.

**Five honourees, one through-line**

The chapter recognised five individuals whose careers span medicine, technology, finance, the arts and public service. Organisers framed the selection deliberately: each honouree, they said, had used professional success as a platform for community return rather than as an end in itself. Speakers returned repeatedly to that theme, arguing that the measure of a diaspora is not the income it generates but the institutions it sustains.

That argument has practical stakes. Connecticut is home to a fast-growing South Asian population concentrated around Stamford, Norwalk and the wealthy suburbs of Fairfield County, many of them drawn by jobs in finance and pharmaceuticals. The community's affluence is well documented; its civic infrastructure is thinner. Groups like GOPIO-CT fill that gap, offering a bridge between newly arrived families and the towns they now call home.

**Money where the mouth is**

The $50,000 donation, split between two local charities, was the evening's concrete gesture. Chapter leaders said the gift reflected a longstanding policy of channelling fundraising back into the broader Connecticut community rather than ring-fencing it for Indian-American causes alone. That posture — visible philanthropy aimed outward — has become a signature of mature diaspora organisations keen to be seen as good neighbours, not just an ethnic bloc.

The strategy carries a quiet political logic. As Indian-Americans grow more numerous and more prosperous, their organisations increasingly seek influence in mainstream civic life: school boards, town councils, hospital trusts. Demonstrating generosity to non-Indian causes builds the goodwill that such ambitions require. GOPIO-CT's leaders have spoken openly about wanting the chapter to be a fixture of Connecticut life, not a parallel society.

**A model under pressure**

The chapter's longevity is notable in a diaspora landscape littered with organisations that flare up around a festival or a cause and then fade. Sustaining volunteer energy across twenty years requires generational handover, and several speakers acknowledged the challenge of drawing younger, American-born members of Indian descent into leadership roles. Second-generation professionals often feel less tethered to origin-country identity than their parents, and competing demands on their time are fierce.

GOPIO-CT's answer has been to broaden its remit beyond cultural programming into areas — health screenings, financial literacy, civic engagement — that appeal across generations. The approach mirrors a wider shift among Indian-American groups, which have moved from organising primarily around Diwali galas toward year-round service that resembles a community foundation more than a cultural club.

**The bigger picture**

The banquet landed at a moment of heightened visibility for the Indian-American community nationally. Diaspora professionals occupy senior posts in government, technology and finance, and organisations from the coasts to the heartland are professionalising their operations. Connecticut's chapter is a smaller node in that network, but its anniversary illustrates the pattern: immigrant associations are maturing into permanent civic actors with budgets, programmes and political standing.

For the families GOPIO-CT serves, the abstractions matter less than the services. A scholarship for a striving student, a free health screening for an uninsured relative, a familiar face at a new town's civic meeting — these are the transactions that knit a diaspora into its adopted home. Two decades in, the chapter's leaders argue, those small acts are the real anniversary worth marking.

What comes next, they said, is continuity: ensuring that the institution outlasts its founders and that the next generation inherits not just a banquet hall full of awards but a working machine for community service. On the evidence of its twentieth year, GOPIO-CT has built something durable enough to try."""

gopio = {
    "id": str(uuid.uuid4()),
    "headline": "GOPIO Connecticut Marks 20 Years, Honours Five Leaders and Gives $50,000 to Charity",
    "subheadline": "A two-decade-old diaspora chapter shows how Indian-American immigrant networks are maturing into permanent civic institutions.",
    "slug": "gopio-connecticut-20th-anniversary-diaspora-20260625",
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Chronicles how an Indian-American community organisation in Connecticut has evolved over 20 years into a durable civic institution, a model relevant to NRI communities across the United States.",
    "tags": ["GOPIO", "Connecticut", "Indian-American", "diaspora philanthropy", "community organisation", "United States"],
    "urgency": "normal",
    "sources": [
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/19/gopio-ct-marks-20th-anniversary-honors-distinguished-leaders/"},
        {"name": "GOPIO International", "url": "https://www.gopio.net/"},
    ],
    "score_total": 68,
    "status": "review",
    "is_editorial": False,
    "published_at": NOW,
    "image_url": "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/gopio-ct-20th-anniversary-keynote-20260624.jpg",
    "image_caption": "A speaker addresses the GOPIO-CT 20th anniversary banquet in Darien, Connecticut.",
    "image_attribution": "The Indian Eye",
    "body": gopio_body,
    "word_count": wc(gopio_body),
}

# ---------------------------------------------------------------------------
# Article 2 — President Murmu's Europe diaspora tour
# ---------------------------------------------------------------------------
murmu_body = """President Droupadi Murmu carried India's diaspora diplomacy deep into Europe this month, addressing Indian communities in Portugal and Slovakia during a two-nation state visit that mixed bilateral business with the now-familiar choreography of a presidential meeting with overseas nationals. Her stop in Slovakia was the first by an Indian head of state in 29 years, a gap that itself signalled how the map of India's engagement is widening beyond its traditional western capitals.

In Lisbon, Ms Murmu addressed members of a Portuguese-Indian community estimated at around 125,000 — one of the larger and older Indian populations in continental Europe, with roots reaching back to the Portuguese colonial presence in Goa, Daman and Diu. Many in the audience hold Portuguese citizenship through that lineage, and the community has become a significant onward gateway to the rest of the European Union for newer migrants from the subcontinent.

**Two countries, two diasporas**

The communities Ms Murmu addressed could hardly be more different in size and shape. Portugal's Indian population is substantial, established and increasingly visible in business and local politics. Slovakia's is tiny by comparison — a few thousand professionals, students and workers, many tied to the country's growing automotive and technology sectors. Yet the presidential script was consistent: a call to stay rooted in Indian culture while contributing fully to the host society, and an assurance that New Delhi sees its overseas citizens as partners in the country's development.

That message has become standard issue in Indian diaspora diplomacy, but the choice of venues was the real signal. By travelling to a small central-European state that has seldom featured in Indian foreign policy, the government underlined a strategy of cultivating relationships across the entire European Union rather than concentrating on Britain, Germany and the Gulf.

**Why Slovakia, why now**

The 29-year gap since the last Indian presidential visit gave the Slovakia leg unusual weight. Bratislava and New Delhi used the occasion to talk up cooperation in defence manufacturing, automobiles and technology — sectors where Slovakia, a manufacturing hub inside the EU, offers Indian firms a foothold in European supply chains. For the small Indian community there, the visit was a rare moment of high-level attention and a marker of the country's rising place on India's diplomatic itinerary.

Diaspora engagement and commercial diplomacy increasingly travel together. Overseas Indian communities serve as informal ambassadors, easing the way for trade and investment, and governments on both sides have learned to use diaspora gatherings to lend warmth to otherwise technical bilateral agendas. Ms Murmu's events followed that template, pairing community receptions with business-focused talks.

**The diaspora as foreign-policy asset**

India has spent the past decade formalising its relationship with the roughly 35 million people of Indian origin living abroad, building portals, simplifying paperwork and courting overseas investment. Presidential and prime-ministerial visits now routinely include a diaspora address, a ritual that flatters the community while reminding it of obligations — remittances, investment, advocacy — that New Delhi hopes it will fulfil.

The strategy has measurable returns. India remains the world's largest recipient of remittances, and its diaspora's political clout in Western capitals has become a tangible diplomatic resource. Events like those in Lisbon and Nitra are the soft-power scaffolding around that hard arithmetic, designed to keep emotional ties strong enough to sustain the flows.

**Beyond the set piece**

For the communities themselves, the value of a presidential visit is partly symbolic and partly practical. Symbolically, it confers recognition — a sense that the mother country has not forgotten emigrants who left, in some cases, generations ago. Practically, such visits often unlock administrative attention to long-standing community requests, from consular services to cultural funding.

Whether the warmth translates into durable engagement depends on follow-through. Diaspora communities have heard the rhetoric of partnership many times, and goodwill erodes when grand gestures are not matched by responsive consulates and workable policies. Ms Murmu's tour reset the relationship at the top; the harder work of sustaining it falls to the diplomatic machinery left behind.

What the visit confirmed is the breadth of India's diaspora ambition. From a 125,000-strong community in Portugal to a few thousand professionals in Slovakia, New Delhi is treating every node of its overseas population as worth a presidential visit — and, increasingly, as worth weaving into the country's economic and strategic plans."""

murmu = {
    "id": str(uuid.uuid4()),
    "headline": "President Murmu Courts Indian Communities in Portugal and Slovakia on Europe Tour",
    "subheadline": "A two-nation visit, including the first by an Indian head of state to Slovakia in 29 years, widens New Delhi's diaspora diplomacy across the EU.",
    "slug": "president-murmu-portugal-slovakia-diaspora-tour-20260625",
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Examines how India is extending its diaspora outreach to smaller European states, addressing the 125,000-strong Indian community in Portugal and a small but growing population in Slovakia.",
    "tags": ["Droupadi Murmu", "Portugal", "Slovakia", "diaspora diplomacy", "Europe", "Indian diaspora", "remittances"],
    "urgency": "normal",
    "sources": [
        {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
        {"name": "Press Information Bureau", "url": "https://pib.gov.in/"},
        {"name": "India Tribune", "url": "https://indiatribune.com/"},
    ],
    "score_total": 71,
    "status": "review",
    "is_editorial": False,
    "published_at": NOW,
    "image_url": "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/murmu-portugal-slovakia-diaspora-20260624.jpg",
    "image_caption": "President Droupadi Murmu, who toured Portugal and Slovakia to meet the Indian diaspora.",
    "image_attribution": "Wikimedia Commons",
    "body": murmu_body,
    "word_count": wc(murmu_body),
}

# ---------------------------------------------------------------------------
# Article 3 — International Day of Yoga 2026 across Australia
# ---------------------------------------------------------------------------
yoga_body = """From the lawns of Canberra's Old Parliament House to beachfronts on the Gold Coast and parks in Perth, Indian-Australian communities turned out in force on June 21 to mark the 12th International Day of Yoga, in one of the diaspora's largest synchronised cultural displays of the year. The events, anchored by India's diplomatic missions and a web of community organisations, doubled as a soft-power showcase and a celebration of how deeply yoga has embedded itself in mainstream Australian life.

In the national capital, High Commissioner Nagesh Singh led a mass session at Old Parliament House, a venue whose symbolism — the seat of Australian democracy for more than six decades — was not lost on organisers. Hundreds of participants, Indian and non-Indian alike, rolled out mats on the historic lawns, an image that captured the dual purpose of the day: cultural pride for the diaspora and an open invitation to the wider public.

**A nationwide footprint**

The geographic spread was the story. Events ran from Canberra to Perth on the west coast, from Sydney and Melbourne to the Gold Coast in Queensland, where GOPIO's local chapter organised a beachside gathering. The breadth reflects an Indian-Australian population that has grown rapidly to become one of the country's largest migrant communities, with significant concentrations in every major city.

That demographic weight has translated into organisational muscle. What began as embassy-led ceremonies has expanded into a decentralised network of community groups, yoga studios, temples and cultural associations capable of staging simultaneous events across a continent. The 2026 edition leaned on that infrastructure, with local organisers handling logistics while diplomatic missions provided the headline framing.

**Healthy ageing as theme**

This year's global theme emphasised yoga's role in healthy ageing — a message with particular resonance for a diaspora whose first major migration waves are now moving into their senior years. Organisers paired the standard asana sessions with talks on wellness, mobility and mental health, repositioning the day from a one-off spectacle toward a year-round message about preventive health.

The framing is shrewd. Yoga's appeal in Australia has long since outgrown its Indian origins; it is now a mainstream fitness and wellness practice with millions of local adherents. By foregrounding healthy ageing, organisers tied the diaspora's cultural export to a public-health conversation that concerns all Australians, reinforcing yoga's status as a shared rather than a borrowed tradition.

**Soft power on the mat**

International Day of Yoga, established at India's initiative through the United Nations in 2015, has become one of New Delhi's most successful soft-power instruments. Each June it generates a wave of favourable imagery in dozens of countries, with diplomats and diaspora communities working in concert. Australia, with its large Indian population and warm bilateral ties, has become one of the day's most enthusiastic stages.

For the Indian government, the return on investment is reputational: yoga associates India with wellness, antiquity and benign influence, a welcome contrast to harder-edged geopolitics. For the diaspora, the day offers something more personal — a sanctioned, high-visibility moment to share a piece of home with neighbours and colleagues, and to see Australian officials and ordinary citizens embrace it.

**Community as engine**

The role of grassroots organisations was central. GOPIO Gold Coast and similar bodies elsewhere did the unglamorous work of permits, venues and volunteers that turns a diplomatic initiative into a genuine community event. Their involvement signals the maturity of Indian-Australian civic life, which has moved well beyond festival-organising into sustained programming around health, culture and youth.

That maturity matters for the community's long-term place in Australia. Visible, well-run public events build the social capital that helps a migrant population integrate without dissolving its identity. Yoga Day, repeated annually and scaled across the country, has become a reliable vehicle for exactly that — a moment when being Indian-Australian is celebrated in public squares rather than confined to private homes.

As the mats were rolled up on June 21, organisers were already talking about next year, and about extending the wellness programming beyond a single day. The ambition reflects a community confident enough in its numbers and its standing to treat a cultural celebration not as a fleeting event but as a fixture of the Australian calendar — one it intends to keep growing."""

yoga = {
    "id": str(uuid.uuid4()),
    "headline": "Indian-Australians Mark 12th International Day of Yoga From Canberra to the Gold Coast",
    "subheadline": "Diplomatic missions and community groups staged synchronised events nationwide, with this year's healthy-ageing theme resonating for a maturing diaspora.",
    "slug": "australia-international-day-of-yoga-2026-diaspora-20260625",
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Shows how Australia's large and increasingly organised Indian community turned International Day of Yoga into a nationwide soft-power and community-building event.",
    "tags": ["International Day of Yoga", "Australia", "Indian-Australian", "GOPIO Gold Coast", "soft power", "diaspora", "wellness"],
    "urgency": "normal",
    "sources": [
        {"name": "South Asian Herald", "url": "https://southasianherald.com/australia-marks-12th-international-day-of-yoga/"},
        {"name": "High Commission of India, Canberra", "url": "https://www.hcicanberra.gov.in/"},
    ],
    "score_total": 66,
    "status": "review",
    "is_editorial": False,
    "published_at": NOW,
    "image_url": "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/australia-yoga-day-2026-diaspora-20260624.jpg",
    "image_caption": "Participants gather for an outdoor group yoga session marking International Day of Yoga.",
    "image_attribution": "Pexels",
    "body": yoga_body,
    "word_count": wc(yoga_body),
}

ARTICLES = [gopio, murmu, yoga]

for a in ARTICLES:
    print(f"  {a['slug']}: {a['word_count']} words, headline {len(a['headline'])} chars, sub {len(a['subheadline'])} chars")

print("\nInserting...")
resp = requests.post(
    f"{URL}/rest/v1/p2_articles",
    headers=HEADERS,
    data=json.dumps(ARTICLES),
)
print("HTTP", resp.status_code)
if resp.status_code >= 300:
    print(resp.text[:2000])
    sys.exit(1)
rows = resp.json()
for r in rows:
    print(f"  inserted id={r['id']} slug={r['slug']} status={r['status']} category={r['category']}")
print(f"\nDone: {len(rows)} articles inserted with status=review.")
