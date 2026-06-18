#!/usr/bin/env python3
"""
NRI World writer — 2026-06-18 18:00 batch
Inserts 3 fresh NRI World articles into Supabase with status='review'.
Topics:
  1. Modi's Paris diaspora address + VivaTech 2026
  2. Shree Siddhivinayak Temple (Toms River NJ) community-hall fundraiser
  3. NRI real-estate investment surge in India 2026
"""
import os, json, sys, datetime
import requests

# ---- credentials ----
def load_env(path):
    env = {}
    if not os.path.exists(path):
        return env
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env

senv = load_env(os.path.expanduser("~/.env.supabase"))
SUPABASE_URL = senv.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
SUPABASE_KEY = (senv.get("SUPABASE_SERVICE_ROLE_KEY") or senv.get("SUPABASE_KEY")
                or os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: missing Supabase credentials"); sys.exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

# ============================================================
# ARTICLE 1 — Modi Paris diaspora address + VivaTech
# ============================================================
body1 = """India's prime minister closed his three-nation European tour on Thursday not in a summit hall but among his own. After two days at the G7 in Évian-les-Bains and a state visit to Slovakia, Narendra Modi arrived in Paris late Wednesday to a scene that has become a fixture of his foreign travel: a knot of expatriates gathered outside his hotel, waving tricolours and pressing children forward for a handshake. Local organisers called it a "Diwali-like" reception. For the roughly 119,000 Indians who call mainland France home, the visit was a rare moment of direct contact with New Delhi.

The centrepiece of the Paris leg was an address to the Indian community on June 18, an event the Embassy of India had been registering attendees for since early June. Such gatherings have grown into a signature of Modi's diplomacy, from Madison Square Garden to Sydney's Olympic Park, and they serve a dual purpose. They energise a diaspora that increasingly sees itself as a stakeholder in India's rise, and they project that constituency back home as evidence of global standing.

France is a smaller stage than the Gulf or North America, where Indian populations number in the millions. But its diaspora is growing, and the relationship sits inside a broader strategic framework. The India-France "Horizon 2047" roadmap, signed during earlier exchanges between the two governments, explicitly names people-to-people ties as a pillar alongside defence and technology. Indian cuisine, yoga, Hindi instruction and fashion have all found footholds in French cities, and officials on both sides have leaned into culture as connective tissue.

The substantive draw in Paris was VivaTech, Europe's largest technology and startup conference, which Modi attended alongside President Emmanuel Macron. India fielded a national pavilion to showcase its startups and digital infrastructure, part of a "Bharat Innovates" push timed to the event. The pitch is straightforward: India wants to be read not merely as a market but as a source of innovation, and the diaspora's engineers and founders are central to that story. Many of the Indian-origin professionals scattered across European tech firms are precisely the audience such pavilions are built for.

For diaspora communities, these visits carry a weight that exceeds their formal agenda. They are a signal that the homeland is paying attention, that remittances and investment flow in both directions, and that an Indian passport or heritage is an asset rather than a liability abroad. The symbolism matters most to first-generation migrants, who often retain the deepest emotional ties to India and turn out in the largest numbers for such events.

There is a harder calculus beneath the celebration. Diaspora goodwill has become a measurable instrument of Indian statecraft. Overseas Indians sent home an estimated $138 billion in remittances last year, the largest such flow of any country, and New Delhi has worked to convert that financial relationship into political and cultural loyalty. Community addresses abroad are the public face of that effort. They also play to domestic audiences, broadcast on Indian television as proof of a leader feted on the world stage.

Critics note that the warmth of these receptions can paper over thornier issues, from visa frictions to the treatment of students and workers who face uncertainty in their host countries. France, like much of Europe, is tightening immigration even as it courts Indian talent and capital. The diaspora address offers reassurance; it does not resolve the underlying tension between open borders for the skilled and closing ones for everyone else.

Still, for the families who waited outside a Paris hotel on a June evening, the visit landed as intended. It affirmed a connection that distance and decades abroad had not severed. As Modi turned from the G7's communiqués to a community hall, the message to Indians in France was unambiguous: wherever they had settled, they remained part of the national project. Whether that sentiment translates into deeper investment ties through VivaTech, or simply a warm memory, will be measured in the months after the motorcade leaves."""

art1 = {
    "headline": "In Paris, Modi Closes a European Tour Among the Diaspora",
    "subheadline": "A community address and a VivaTech pavilion turn the final leg of an India-France visit into a courtship of expatriate talent and capital.",
    "body": body1,
    "slug": "modi-paris-diaspora-vivatech-20260618",
    "category": "nri-world",
    "vertical": "nri-world",
    "urgency": "medium",
    "status": "review",
    "is_editorial": False,
    "is_featured": False,
    "sources": json.dumps([
        {"name": "Dainik Jagran English", "url": "https://english.dainikjagranmpcg.com/"},
        {"name": "Embassy of India, France", "url": "https://eoiparis.gov.in/"},
        {"name": "Livemint", "url": "https://www.livemint.com/"},
        {"name": "DD News", "url": "https://ddnews.gov.in/"}
    ]),
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5f/The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg",
    "image_caption": "Prime Minister Narendra Modi, who addressed the Indian community in Paris on June 18 during the final leg of his European tour.",
    "image_attribution": "Government of India / Wikimedia Commons (GODL-India)",
    "diaspora_angle": "Directly addresses France's ~119,000-strong Indian community and the broader use of diaspora outreach as an instrument of Indian statecraft, including remittance flows and tech-talent recruitment via VivaTech.",
    "tags": ["Modi", "France", "diaspora", "VivaTech", "India-France", "Europe", "NRI"],
    "score_total": 82,
    "published_at": None,
    "created_at": NOW,
}

# ============================================================
# ARTICLE 2 — Siddhivinayak Temple Toms River NJ fundraiser
# ============================================================
body2 = """In a banquet hall in Toms River, New Jersey, the annual Siddhi Singers concert in May raised money for a building that does not yet exist. The Shree Siddhivinayak Temple, a fixture of the central-Jersey Indian community, is trying to fund a dedicated community hall, and its leaders used the evening of music to make the case that a temple in the diaspora must be more than a place of worship.

The fundraiser drew a notable guest list. Vishal Harsh, the Deputy Consul General of India in New York, attended as chief guest, a signal of how seriously Indian officialdom now takes the institutions its emigrants build abroad. Ankur Vaidya, chairman of the Federation of Indian Associations, and Padma Shri Dr. Sudhir Parikh, a long-standing figure in the New York-area Indian community, were also present. Their attendance lent the evening the weight of a regional gathering rather than a parish event.

Dr. Avinash Gupta, the temple's chairman, spoke emotionally about why a community hall has become a priority. For temples founded by immigrants, the sanctuary is only part of the function. The surrounding rooms are where Gujarati and Hindi classes meet, where wedding receptions and naming ceremonies unfold, where elderly parents visiting from India find company, and where second-generation children encounter the rituals their grandparents practised. Without dedicated space, those activities are squeezed into rented halls or overflow into the worship area itself.

The Toms River temple's ambitions track a wider pattern across the Indian diaspora in North America. The first wave of immigrant temples, built through the 1980s and 1990s, focused on consecrating deities and establishing a place to pray. A second phase, now well underway, is about institution-building: classrooms, kitchens, performance spaces and social-service arms that anchor a community across generations. The challenge is always money, and these projects depend almost entirely on congregational giving rather than any outside endowment.

That reliance is precisely why events like the Siddhi Singers concert matter. They are fundraising mechanisms, but they are also demonstrations of collective will. A turnout strong enough to fill a hall tells potential large donors that the community is committed, and it tells visiting dignitaries that the institution is worth their time. The presence of a consular official, in turn, validates the temple in the eyes of its own members.

There is a generational urgency beneath the appeal. Temple leaders across the diaspora worry openly about retaining the children and grandchildren of immigrants, who are American by birth and culture and who may drift from institutions built in an idiom their elders carried from India. A community hall is partly an answer to that anxiety: a flexible, welcoming space where heritage can be taught not as obligation but as celebration, through dance, food, festivals and language. The bet is that a child who grows up performing at the temple will return to it as an adult.

The economics are not trivial. Construction in New Jersey is expensive, permitting is slow, and a volunteer-run board must raise funds while managing the day-to-day costs of an existing temple. Many diaspora congregations spend a decade or more between announcing such a project and cutting a ribbon. Yet the persistence is itself the point. Each fundraiser, each concert, each consular visit adds a layer of momentum and visibility.

For the families who filled the Toms River hall in May, the evening was both a night of devotional music and a statement of intent. The temple that began as a place to pray is determined to become a place to belong, and the community hall it is raising money for is the physical form of that ambition. Whether the building rises in two years or five, the campaign has already done part of its work: it has reminded a scattered community of central-Jersey Indians that the institution they built is still growing, and still theirs."""

art2 = {
    "headline": "A New Jersey Temple Raises Funds, and Makes a Case for Belonging",
    "subheadline": "At the Shree Siddhivinayak Temple in Toms River, a community-hall campaign reflects the diaspora's shift from building places of worship to building institutions.",
    "body": body2,
    "slug": "siddhivinayak-temple-toms-river-community-hall-20260618",
    "category": "nri-world",
    "vertical": "nri-world",
    "urgency": "low",
    "status": "review",
    "is_editorial": False,
    "is_featured": False,
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
        {"name": "Federation of Indian Associations", "url": "https://www.fia-nynjct.org/"}
    ]),
    "image_url": "https://images.pexels.com/photos/36587828/pexels-photo-36587828.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Diaspora temples increasingly serve as cultural and community centres, not only places of worship.",
    "image_attribution": "Thilina Alagiyawanna / Pexels",
    "diaspora_angle": "Chronicles how an immigrant-founded temple in New Jersey is building institutions to retain second-generation Indian-Americans, a pattern across the North American diaspora, with Indian consular backing.",
    "tags": ["temple", "New Jersey", "diaspora", "community", "Hindu", "NRI", "FIA"],
    "score_total": 74,
    "published_at": None,
    "created_at": NOW,
}

# ============================================================
# ARTICLE 3 — NRI real estate investment surge
# ============================================================
body3 = """The money is coming home, and increasingly it is buying property. Institutional investment in Indian real estate rose roughly 25% year-on-year to about $1.6 billion in the first quarter of 2026, according to Colliers, while private-equity inflows into the sector roughly doubled to around $637 million over the same period on Knight Frank's count. Within that surge, a familiar constituency is reasserting itself: non-resident Indians, whose appetite for property back home has strengthened as the rupee, interest rates and a wave of new luxury supply align in their favour.

For the diaspora, Indian real estate has always been more than an asset class. A flat in Mumbai or a plot near the family's ancestral town is at once an investment, a hedge, a retirement plan and an emotional tether. What has changed in 2026 is the calculus around it. A softer rupee stretches dollar, pound and dirham savings further. Developers, chasing premium buyers, have flooded metros with branded residences and gated townships aimed squarely at returning or investing Indians. And digital tools now let an NRI in New Jersey or Dubai tour, finance and close on a property without boarding a plane.

The macro backdrop is supportive. India's real-estate sector is projected to approach $1 trillion in value by 2030, according to industry-promotion body IBEF, on the back of urbanisation, a growing middle class and sustained demand for both housing and office space. In the first quarter of 2026, office assets dominated institutional flows, accounting for roughly half the total, as global occupiers continued to expand in India's services hubs. That commercial strength reassures NRI investors that the broader market has structural momentum, not merely a residential bubble.

There is nuance in the numbers. Domestic capital drove about three-quarters of the quarter's institutional inflows, while foreign investment actually declined by an estimated 23%, a reminder that global allocators remain selective. But the headline institutional figures and the NRI retail story are distinct. Even as large foreign funds trimmed exposure, individual diaspora buyers, motivated by currency advantage and personal ties rather than portfolio rebalancing, have stayed active in the residential premium segment.

Geopolitics is adding an unexpected tailwind in the Gulf, home to the largest concentration of overseas Indians. Analysts have argued that a de-escalation in regional tensions could firm up incomes and confidence among the Gulf's vast Indian workforce, supporting both local housing demand and the remittances that flow into Indian property purchases. For the millions of Indians in the UAE, Saudi Arabia and Qatar, stability in the region translates fairly directly into the capacity to invest at home.

The risks are real and worth naming. Indian real estate has a long history of project delays, opaque pricing and developer defaults, and NRIs investing from afar are especially exposed to them. Regulatory reform, notably the Real Estate Regulation Act, has improved transparency, but enforcement remains uneven across states. Currency works both ways: a rupee that recovers would erode the very advantage drawing buyers in now. And the premium-housing boom that developers are marketing to the diaspora could outrun genuine demand if the broader economy stumbles.

For the diaspora investor, the practical questions are familiar. Title verification, tax treatment of rental income and capital gains, repatriation of proceeds, and the reliability of a developer all demand diligence that distance complicates. The platforms promising frictionless cross-border purchases have lowered the barrier to entry but not the need for caution.

What the first-quarter data make clear is that Indian property remains a magnet for diaspora capital, pulled by a mix of cold financial logic and something less quantifiable. As one quarter's figures show institutional money and NRI demand rising in tandem, the sector is once again positioning itself as the place where the diaspora's earnings abroad find a foothold at home. Whether 2026 proves a durable upswing or another cyclical peak, the impulse behind it, to own a piece of the country one left, shows no sign of fading."""

art3 = {
    "headline": "Why NRI Money Is Pouring Back Into Indian Property",
    "subheadline": "A softer rupee, a premium-housing boom and a $1.6bn institutional surge are pulling diaspora capital toward Indian real estate in 2026.",
    "body": body3,
    "slug": "nri-real-estate-investment-surge-india-20260618",
    "category": "nri-world",
    "vertical": "nri-world",
    "urgency": "medium",
    "status": "review",
    "is_editorial": False,
    "is_featured": False,
    "sources": json.dumps([
        {"name": "Colliers India", "url": "https://www.colliers.com/en-in"},
        {"name": "Knight Frank India", "url": "https://www.knightfrank.co.in/"},
        {"name": "IBEF", "url": "https://www.ibef.org/industry/real-estate-india"},
        {"name": "Hindu Business Line", "url": "https://www.thehindubusinessline.com/"}
    ]),
    "image_url": "https://images.pexels.com/photos/11505497/pexels-photo-11505497.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "India's metros are seeing a wave of premium residential supply aimed at returning and investing non-resident Indians.",
    "image_attribution": "Keith Lobo / Pexels",
    "diaspora_angle": "Explains the 2026 surge in NRI real-estate investment in India, the currency and supply dynamics driving it, the Gulf diaspora's role, and the risks diaspora buyers face purchasing from abroad.",
    "tags": ["NRI", "real estate", "investment", "India", "diaspora", "property", "Gulf"],
    "score_total": 79,
    "published_at": None,
    "created_at": NOW,
}

ARTICLES = [art1, art2, art3]

# ---- word-count sanity check ----
for a in ARTICLES:
    wc = len(a["body"].split())
    a["word_count"] = wc
    flag = "OK" if 600 <= wc <= 800 else "**OUT OF RANGE**"
    print(f"[{a['slug']}] words={wc} {flag}")

# ---- insert ----
endpoint = f"{SUPABASE_URL}/rest/v1/p2_articles"
results = []
for a in ARTICLES:
    r = requests.post(endpoint, headers=HEADERS, data=json.dumps(a), timeout=30)
    if r.status_code in (200, 201):
        rep = r.json()
        aid = rep[0].get("id") if isinstance(rep, list) and rep else "?"
        print(f"INSERTED: {a['slug']} -> id={aid}")
        results.append((a["slug"], "ok", aid))
    else:
        print(f"FAILED: {a['slug']} -> {r.status_code}: {r.text[:300]}")
        results.append((a["slug"], "fail", r.text[:300]))

print("\n=== SUMMARY ===")
for slug, status, info in results:
    print(f"{status.upper():6} {slug} {info}")
