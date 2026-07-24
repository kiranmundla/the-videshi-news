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
        "headline": "New York's Senate Just Told the Governor to Declare India Independence Day. It's the Third Year Running.",
        "subheadline": "Resolution J1935 sailed through with bipartisan warmth, but the annual ritual is starting to carry weight beyond symbolism for the state's half-million Indian Americans.",
        "slug": make_slug("ny-senate-india-independence-day-resolution-2026-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The resolution is a direct recognition of the Indian-American community's growing clout in New York politics, and the floor speeches reveal how legislators now see the diaspora as a permanent feature of the state's identity rather than a visiting constituency.",
        "tags": ["nri", "diaspora", "new-york", "indian-independence-day", "politics"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/new-york-state-senate-adopts-resolution-for-august-15-2026-as-india-independence-day/"},
            {"name": "Swadesi News", "url": "https://swadesi.com/ny-senate-adopts-india-independence-day-resolution-2026/"},
            {"name": "India Weekly", "url": "https://indiaweekly.biz/new-york-senate-urges-recognition-of-indias-independence-day/"},
            {"name": "NY Senate Legislature", "url": "https://legislation.nysenate.gov/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/New_York_State_Capitol%2C_Albany_New_York.jpg/1280px-New_York_State_Capitol%2C_Albany_New_York.jpg",
        "body": """The New York State Senate has adopted Resolution J1935, urging Governor Kathy Hochul to proclaim August 15, 2026, as India Independence Day across the state. The vote itself was unremarkable — bipartisan, swift, no dissenting voices. What mattered was the floor debate that preceded it, where senator after senator stood to talk about India not as a geopolitical partner or a trade ally but as something closer to home.

Senator Jeremy Cooney, the Rochester Democrat who sponsored the measure, set the tone early. "Across the globe, Indians are making lasting impacts in their communities, and this is an opportunity to join together and celebrate and reflect on our shared history, culture, and heritage," he told colleagues. It was the third consecutive year Cooney has shepherded this resolution through. The first time, in 2024, the gesture was novel. By now, the machinery has become routine — which is precisely the point.

## The speeches told the real story

The legislative record matters less than the rhetoric. Senator Joseph Addabbo Jr. quoted Gandhi — "the future depends on what we do in the present" — and called it a message that "continues to inspire Indian Americans and future generations." Senator John Liu, who represents parts of Queens with one of the largest Indian-American populations in the Western Hemisphere, was more direct: "India has been around for thousands of years. It has been a civilisation. It has been a country. It has been a model of democracy for actually a lot longer than our country."

Senator Jeremy Zellner went further still, calling the Indian-American community "woven into the fabric of our everyday life" in his district. "They are our neighbours raising families here, working in critical professions, and helping shape the character of our region," he said. Senator Toby Ann Stavisky urged lawmakers to continue a "tradition of friendship" between the two nations, arguing that the similarities outweigh the differences.

These are not perfunctory remarks. They are legislators publicly acknowledging a constituency that, in New York alone, now numbers well over 500,000 — accounting for more than 2.8 percent of the New York City metropolitan area's population. Indian Americans in the state hold one of the highest educational attainment rates of any ethnic group, with 71 percent holding at least a bachelor's degree, more than double the national average.

## From resolution to recognition

The India Consulate General in New York issued a formal thank-you, noting the "warm recognition of India's rich heritage and the invaluable contributions of the Indian-American community." For the consulate, the resolution is a diplomatic asset — proof that the diaspora's relationship with its adopted home is not merely economic but civic and cultural.

For the diaspora itself, the resolution carries a different kind of weight. It arrives at a moment when Indian Americans are navigating a paradox: growing political influence alongside rising anti-Indian sentiment online and, in some cases, on the street. The 2026 Indian American Attitudes Survey, published by the Carnegie Endowment, found that 48 percent of Indian Americans report seeing racist content targeting them on social media "very or somewhat often" since the start of 2025. One in four has been called a slur.

A state senate resolution does not fix that. But it does something subtler — it places the Indian-American community inside the official narrative of New York, not as a footnote or a one-off recognition but as an annual civic event. The resolution explicitly notes that New York City was the site of a critical milestone: Bhicaji Balsara successfully litigating to become the first known naturalised citizen from India, right there in the city.

## What the resolution cannot do

Hochul has yet to formally issue the proclamation, though she has done so in previous years and there is no reason to expect otherwise. The resolution is non-binding — it memorialises the governor to act, which is legislative politeness for "please do this." She almost certainly will.

The harder question is whether these annual gestures translate into anything tangible for the community. Indian Americans now have six members in the U.S. House of Representatives, up from one a dozen years ago. The community's median household income is among the highest of any ethnic group in the country. But political representation at the state and local level remains thin in New York, and the community's internal diversity — linguistic, religious, caste-based — makes bloc voting more aspiration than reality.

For now, the resolution is what it is: a small, annual acknowledgement that India's independence matters to New York because New York's Indians matter to New York. The third time around, that is starting to sound less like a courtesy and more like a fact."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Murder in Southampton Has Left Britain's 500,000 Sikhs Defending a Faith They Didn't Put on Trial",
        "subheadline": "Vickrum Digwa stabbed a teenager, lied about racism, and got life in prison. The backlash has landed on every Sikh who carries a kirpan.",
        "slug": make_slug("southampton-stabbing-uk-sikh-kirpan-backlash-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The case has put the British Sikh diaspora — one of the UK's most established and integrated South Asian communities — in the crosshairs of a national debate about policing, race, and religious exemptions, forcing community leaders to distance themselves from one man's crime while defending centuries-old religious practice.",
        "tags": ["nri", "diaspora", "uk", "sikh", "kirpan", "policing", "hate-crime"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/uk/uk-police-under-pressure-after-dying-student-was-handcuffed-2026-06-02/"},
            {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com/trending/i-cant-breathe-how-an-indian-sikh-murder-accused-ignited-huge-knife-crime-and-racism-debate-in-uk"},
            {"name": "Associated Press via Audacy", "url": "https://www.audacy.com/national-news/the-case-of-a-uk-teen-who-died-from-a-stab-wound-while-handcuffed-by-police-stirs-debate"},
            {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/politics/3415671-uk-police-under-pressure-after-dying-student-was-handcuffed"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/A_view_of_the_Sikhism_Gurdwara_Sri_Guru_Singh_Sabha%2C_Southall_London_United_Kingdom.jpg/1280px-A_view_of_the_Sikhism_Gurdwara_Sri_Guru_Singh_Sabha%2C_Southall_London_United_Kingdom.jpg",
        "body": """The sentencing was supposed to close the case. On Monday, Southampton Crown Court handed Vickrum Digwa, a 23-year-old British Sikh, a life sentence with a minimum of 21 years for the murder of Henry Nowak, an 18-year-old university student stabbed to death on a residential street in December 2025. But what happened in the hours after — the release of police bodycam footage, the protests outside the police station, the incendiary statements from politicians — has turned a criminal case into a national reckoning. And the community paying the steepest price for one man's actions is the one that had nothing to do with them.

## What happened on the night

The facts, as established by the court, are brutal in their simplicity. Nowak was walking back to his student accommodation after a night out. He and Digwa did not know each other. Digwa, who was carrying an 8-inch Sikh dagger in addition to a smaller ceremonial kirpan, stabbed Nowak five times — in the legs, the groin, and through the chest, severing a vein behind his collarbone and slicing a lung.

When police arrived, Digwa told them he was the victim — that Nowak had racially abused him. Officers took his word for it. Bodycam footage, released this week with the family's permission, shows Nowak lying on the street, pale and bleeding, telling officers "I've been stabbed" and "I can't breathe." One officer replied: "I don't think you have, mate." Nowak was handcuffed as a suspect. He died that night.

Judge William Mousley was unsparing in his sentencing remarks. He told Digwa he did not believe Nowak had said anything racist, calling the claim "completely at odds with his previous character." Then the judge said something that landed far beyond the courtroom: "Your actions have stirred up racial tension in Southampton and across the country which have made many Sikhs worried about their own safety even though they have done absolutely nothing wrong."

## The political firestorm

The footage detonated. Prime Minister Keir Starmer said he "felt sick" watching it and acknowledged "serious questions" about how "allegations of racism informed or fed into the decision-making." Cabinet Office Minister Nick Thomas-Symonds called the police conduct "shocking." Hampshire Police apologised to Nowak's family, admitting that Digwa's lies had misled officers. One officer has resigned. The Independent Office for Police Conduct is investigating.

But Nigel Farage, whose Reform UK party leads in opinion polls, seized the moment with characteristic bluntness. "The fear of being called racist was greater than dealing with Henry Nowak's murder," he said. "We should respond to this with pure cold rage." Protests erupted outside Southampton police station on Tuesday, with hundreds chanting "I can't breathe." Anti-immigration activist Tommy Robinson was among them. More protests have been advertised for the coming days.

The National Police Chiefs' Council has announced a review of its race guidance, which critics say encouraged officers to treat racial complaints with disproportionate credulity. A source close to Home Secretary Shabana Mahmood told reporters that the wording would be reviewed "to ensure there is no ambiguity, so everyone is equal in the eyes of the law."

## The diaspora pays the price

None of this has anything to do with the roughly 524,000 Sikhs living in the United Kingdom — a community that has been part of British life for over a century, that runs businesses from Southall to Glasgow, that has produced military heroes, entrepreneurs, and a former Prime Minister's in-laws. But the case has collapsed several distinct issues — knife crime, policing failures, religious exemptions, race relations — into a single inflammatory symbol, and the kirpan is at the centre of it.

Under UK law, Sikhs are permitted to carry the kirpan as a religious article. The exemption has existed for decades and has overwhelmingly functioned without incident. Digwa carried a small kirpan but also an 8-inch sheathed dagger that he claimed was religiously significant. The court made clear the weapon was not a standard ceremonial blade — it was a lethal weapon that happened to share a name with a religious object.

For British Sikhs, the distinction is existential. Community organisations have been quick to condemn Digwa's actions, but they now face a public conversation in which their faith's most visible symbol — the kirpan, one of the five articles of faith (kakkar) — is being discussed in the same breath as knife crime statistics. Sikh leaders worry that the far-right's instrumentalisation of the case will lead to harassment of turban-wearing men on the street, a pattern that has recurred throughout the post-9/11 era whenever South Asians become entangled in crime or terrorism stories that have nothing to do with their broader community.

## What happens next

The legal process continues. Digwa's mother, Kiran Kaur, 53, was convicted of assisting an offender after attempting to hide the murder weapon. She will be sentenced on July 17. The police investigation into officer conduct is ongoing. The political debate will almost certainly intensify as Reform UK, which has made cultural grievance its electoral calling card, pushes for changes to religious exemptions.

For the diaspora, the calculation is familiar and exhausting: one person's crime becomes a community's burden. The Sikh community in Britain did not stab Henry Nowak, did not lie to the police, and did not write the guidance that officers followed. But it is their gurdwaras, their kirpans, and their children's safety that are now part of the conversation. The judge was right to name it. Whether anyone else will listen is another matter entirely."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "London Just Held Its First Global Indian Restaurant Awards. The Winners Tell You Where the Diaspora's Culinary Power Actually Sits.",
        "subheadline": "Sanjeev Kapoor took Global Chef of the Year, the Cinnamon Club won best restaurant, and 250 restaurateurs gathered for an evening that treated Indian food abroad as an industry, not a novelty.",
        "slug": make_slug("global-indian-restaurant-awards-london-2026-diaspora-chefs"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The inaugural London awards ceremony marks the moment when the Indian restaurant industry abroad stopped being an immigrant story and started being a global business narrative — with diaspora chefs, restaurateurs, and MBE-holders setting benchmarks that restaurants in India are now trying to meet.",
        "tags": ["nri", "diaspora", "uk", "restaurants", "indian-cuisine", "awards", "london"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Restaurant India", "url": "https://restaurantindia.in/news/indian-restaurant-congress-awards-debuts-in-london-bringing-together-250-global-restaurateurs.nid-25803.html"},
            {"name": "Good Curry Guide", "url": "https://goodcurryguide.net/indian-restaurant-congress-awards-winners/"}
        ]),
        "score_total": 65,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Sanjeev_kapoor_at_the_Launch_of_new_restaurant_%27Arola%27_at_J_W_Marriott.jpg",
        "body": """The Indian Restaurant Congress held its first-ever London edition last week, bringing 250 restaurateurs, chefs, and hospitality executives to a single room for a conference and awards ceremony that, in its own quiet way, marked something significant: the Indian restaurant industry abroad finally has its own Oscars.

The event, organised by Restaurant India and its publishing arm Entrepreneur APAC, has been running in Mumbai, Delhi, and Bengaluru for over a decade. But this was the first time it crossed borders — and the choice of London was deliberate. Britain has the oldest and deepest Indian restaurant culture outside the subcontinent, with an estimated 12,000 curry houses, fine-dining establishments, and everything in between. The question the congress asked, implicitly, was whether that ecosystem had grown large and sophisticated enough to merit a global awards infrastructure. The answer, judging by the turnout, was yes.

## The winners

The inaugural Global Indian Restaurant Awards were judged by a panel that included George Shaw, former BBC journalist and editor of the Good Curry Guide; Andy Hayler, one of Britain's most respected food critics; Rashmi Uday Singh, the Indian TV host and author; and Rajesh Suri, former CEO of the Tamarind Collection Group.

Sanjeev Kapoor — India's most recognised chef, with a television career spanning three decades and a restaurant portfolio that stretches from Mumbai to Dubai — took the Global Indian Chef of the Year award. It was an unsurprising but politically significant choice: Kapoor represents the bridge between India's domestic culinary establishment and the diaspora's restaurant industry abroad.

The Cinnamon Club, housed in the Grade II-listed Old Westminster Library building near the Houses of Parliament, won Global Indian Restaurant of the Year. Its executive chef and CEO, Vivek Singh, has built the Cinnamon Collection into one of London's most respected hospitality groups. Singh was also a panellist at the conference, speaking on the evolution from chef to entrepreneur.

Other winners told a story of depth rather than novelty. Kahani, the Chelsea fine-dining restaurant run by Chef Peter Joseph, took Best Fine Dining. Benares, Atul Kochhar's Michelin-starred establishment in Mayfair, won Best Chef-Led Restaurant. Jamavar, the Leela-backed restaurant that brought the grand Indian hotel dining experience to London, was named Best Indian Restaurant Brand. Colonel Saab — which serves Indian military mess-inspired cuisine on the ground floor of the Holborn Hall — won Best Indian Restaurant in the United Kingdom.

## What the conference revealed

The awards were the centrepiece, but the conference sessions beforehand were arguably more revealing. The headline panel — "Beyond the Kitchen: Chefs, Restaurateurs & the Global Rise of Indian Brands" — featured Atul Kochhar, the first Indian chef to win a Michelin star, alongside Cyrus Todiwala OBE, Romy Gill MBE, and Dipna Anand.

The conversation circled a theme that would have been unthinkable a generation ago: scaling. Indian restaurants abroad are no longer family operations surviving on thin margins and weekend crowds. They are brands, some with private-equity backing, international expansion plans, and supply-chain partnerships with companies like Nestlé Professional and Cobra Beer (Molson Coors). Kate Alexander, head of Food & Commercial Channels at Nestlé Professional UK & Ireland, was a speaker. So was Samson Sohail, head of Global Sales at Cobra Beer.

Roughly 25 to 30 percent of Indian restaurant brands have now scaled globally, with presence in the United States, UAE, United Kingdom, and Saudi Arabia. The traffic is increasingly two-way: as Indian brands open in London and New York, global restaurant formats — from ramen bars to Scandinavian minimalism — are reshaping dining in Mumbai and Delhi.

## The diaspora's culinary infrastructure

For the Indian diaspora, the restaurant industry has always been more than commerce. It is, in many communities, the first point of contact between the host culture and the immigrant one — the place where non-Indians first encounter a dosa, a biryani, a thali. The curry house in Britain, the tandoori joint in the Gulf, the fast-casual Indian chain in America: these are cultural institutions, even if they do not always get treated as such.

The London awards ceremony was, in a sense, the industry's way of treating itself the way it deserves to be treated — with rigour, with critical standards, and with the understanding that Indian food abroad is not a subset of Indian food in India but a parallel tradition with its own masters, its own innovations, and its own economics. The fact that some of the winners hold MBEs and OBEs — honours from the British state — is not incidental. It is evidence of how deeply the diaspora's culinary labour has been absorbed into the host nation's cultural fabric.

The congress has already announced plans for future international editions. If the London debut is any guide, the next one will have no trouble filling the room."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
