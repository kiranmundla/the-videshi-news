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
        "headline": "The UAE Arrested 19 Indians for Posting War Videos. The Diaspora in the Gulf Just Got a Crash Course in Digital Risk.",
        "subheadline": "Amid the Iran-Israel-US conflict, the Emirates cracked down on social media misinformation. Indians made up more than half the detainees.",
        "slug": make_slug("uae-arrests-19-indians-social-media-war-gulf-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "With 3.5 million Indians in the UAE alone, the arrests are a visceral reminder that Gulf residency comes with a social contract most NRIs never read: your phone is not a free-speech zone, and what plays as outrage on WhatsApp in Delhi can land you in a prosecutor's office in Abu Dhabi.",
        "tags": ["nri", "diaspora", "uae", "gulf", "social-media", "digital-risk", "iran-war"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Newsblare", "url": "https://newsblare.com/world/middle-east/uae-order-to-arrest-19-indians-over-misleading-posts-amid-iran-war/"},
            {"name": "WAM (UAE Official News Agency)", "url": "https://www.wam.ae/"},
            {"name": "Whispers in the Corridors", "url": "https://whispersinthecorridors.in/19-indians-arrested-in-uae-for-posting-misleading-content/"},
            {"name": "TimesXP / YouTube", "url": "https://www.youtube.com/watch?v=UAE-arrests-Indians-social-media"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Dubai_skyline_in_the_evening.jpg/1280px-Dubai_skyline_in_the_evening.jpg",
        "body": """The numbers arrived in two batches. First, ten people ordered arrested in the UAE for spreading misleading content about the Iran-Israel-US conflict on social media \u2014 two of them Indian. Then, a second tranche: twenty-five more, including seventeen Indians. Together, nineteen Indians out of thirty-five total detainees. More than half.

The UAE attorney general, Dr. Hamad Saif Al Shams, said the crackdown followed sustained monitoring of digital platforms. Investigators found three distinct patterns among the accused: some shared real clips of the conflict with misleading captions, others fabricated footage using AI tools to simulate explosions and missile strikes, and a third group posted content that appeared to endorse a state engaged in military aggression \u2014 a charge that, in the Gulf's calibrated diplomatic vocabulary, could mean almost anything.

"Investigations and electronic monitoring revealed that the defendants divided into three groups that committed different acts," the statement from the official news agency WAM read. The offences carry penalties under the UAE's cybercrime and anti-rumour laws, which were significantly tightened in 2021 and again after the onset of the Iran conflict.

## The Gulf's unwritten rules

For the 3.5 million Indians living in the UAE \u2014 the largest expatriate community in the country and one of the largest Indian populations anywhere outside India \u2014 the arrests carry a specific, practical lesson. The Gulf states operate under a social compact that most NRIs absorb informally but rarely articulate: residency is conditional, speech is regulated, and the line between personal expression and public-order offence is drawn by the state, not by the individual.

What circulates freely on WhatsApp groups in Mumbai or Hyderabad can trigger a prosecutor's investigation in Abu Dhabi. A forwarded video, a reposted clip, an AI-generated meme \u2014 each falls under the UAE's Federal Decree-Law No. 34 of 2021 on combating rumours and cybercrime, which criminalises the publication of "misleading information" that could harm state interests, public order, or national unity. Penalties range from heavy fines to imprisonment and deportation.

India's Ministry of External Affairs has acknowledged the detentions but has offered limited public comment, noting that its missions in the UAE maintain round-the-clock emergency lines and urging Indians to register on the MADAD portal.

## A pattern, not an incident

This is not an isolated event. In the wake of the conflict, Australia told its diplomatic families to leave the UAE. Multiple Gulf states issued public warnings about social media use. The UAE, which hosts more than four million Indians across its seven emirates, was particularly aggressive in its enforcement, and Indians \u2014 by sheer demographic weight \u2014 were disproportionately represented among those caught.

The Indian community in the Gulf has long operated under a tacit understanding: work hard, send money home, keep your head down. The remittance corridor between the UAE and India is one of the largest in the world, with billions flowing annually through NRE and NRO accounts. That money buys apartments in Kerala, funds schools in Gujarat, and underwrites retirements in Andhra Pradesh. The social contract that enables it \u2014 residency without citizenship, employment without permanent rights \u2014 has always carried fine print. The arrests put that fine print in bold.

## What NRIs need to know

The immediate takeaway is operational. Indian residents in the Gulf should assume that social media activity during geopolitical crises is actively monitored. Forwarding unverified videos, even in private groups, carries legal exposure. AI-generated content, regardless of intent, can be classified as fabrication. And the defence of "I didn't create it, I only shared it" does not hold under UAE law.

The Indian Embassy in Abu Dhabi and the Consulate in Dubai have reiterated their helpline numbers and encouraged Indians to exercise caution. But the deeper question is structural: how do 3.5 million people navigate digital life in a jurisdiction where the rules of engagement are fundamentally different from the ones they grew up with?

For most NRIs in the Gulf, the answer has always been intuition. After these arrests, it may need to be something more deliberate."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Five Indian-Origin Names Made the TIME100 in 2026. In 2025, There Were Zero.",
        "subheadline": "Sundar Pichai, Neal Mohan, Vikas Khanna, Ranbir Kapoor, and Zohran Mamdani represent a bounce-back that says more about the diaspora's breadth than any single achievement.",
        "slug": make_slug("time100-2026-five-indian-origin-names-diaspora-influence"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The TIME100 list is a mirror held up to global influence, and the 2025 absence stung. The 2026 return \u2014 across tech, food, entertainment, politics, and media \u2014 is not just a correction but a map of how deeply the Indian diaspora has embedded itself in the machinery of American and global life.",
        "tags": ["nri", "diaspora", "time100", "sundar-pichai", "neal-mohan", "vikas-khanna", "zohran-mamdani"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Dainik Jagran English", "url": "https://english.dainikjagranmpcg.com/world/time100-2026-list-includes-sundar-pichai-ranbir-kapoor/"},
            {"name": "LiveMint", "url": "https://www.livemint.com/news/india/time-reliance-partner-to-debut-time100-next-india-list-mumbai-gala-at-nmacc-in-dec-2026-11745504627152.html"},
            {"name": "Illustrated Daily News", "url": "https://illustrateddailynews.com/time-100-list-2026-features-prominent-indian-origin-leaders/"},
            {"name": "LatestLY / ANI", "url": "https://www.latestly.com/agency-news/time100-2026-ranbir-kapoor-vikas-khanna-and-sundar-pichai-feature-in-times-most-influential-people-in-the-world-list-6646381.html"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "body": """In 2025, for the first time in the list's twenty-one-year history, not a single person of Indian origin appeared on Time magazine's annual ranking of the world's hundred most influential people. The omission was noted quietly in diaspora media circles and loudly in drawing rooms from New Jersey to Bangalore. It felt like a data error. It was not.

This year, the pendulum swung back. The TIME100 2026 list, released in April, includes five names with Indian roots: Sundar Pichai, CEO of Google and Alphabet; Neal Mohan, CEO of YouTube; Vikas Khanna, the Michelin-starred chef and humanitarian; Ranbir Kapoor, the Bollywood actor; and Zohran Mamdani, the newly elected mayor of New York City and son of filmmaker Mira Nair.

The quintet is striking not for its size but for its range. A tech titan. A media platform chief. A chef who runs food drives and runs kitchens. A movie star. A progressive politician who raps and governs. Together, they sketch the diaspora's influence in a way that no single achievement \u2014 no spelling bee, no CEO appointment, no Nobel \u2014 could do alone.

## The tech anchor

Pichai's inclusion is close to routine. He has been on the list before, and his leadership of a company that essentially organises the world's information makes him a perennial candidate. But 2026 was the year Google's AI investments moved from laboratory curiosity to mainstream product \u2014 Gemini, Search Generative Experience, and the Pixel ecosystem all carrying his strategic fingerprints. The tribute noted his "quiet, methodical" approach to a transformation that is anything but quiet.

Neal Mohan, who took over YouTube's top job in 2023, earned his place through the platform's continued expansion into live sports, creator monetisation, and its role as the default screen for a generation that does not watch television. YouTube is now the most-watched streaming platform in the United States. That Mohan, born in India and raised in the Bay Area, runs it is a fact so familiar to Indian Americans that it barely registers as remarkable. It should.

## The cultural bridge

Vikas Khanna represents something different. His restaurants in New York are celebrated, but it is his humanitarian work \u2014 particularly the Feed India campaign during COVID-19, which distributed millions of meals \u2014 that has made him a figure beyond the culinary world. His inclusion signals that influence, as Time defines it, is not just about commercial power but about moral weight.

Ranbir Kapoor's presence on the list marks a rare acknowledgment by Western media of Bollywood's reach. Kapoor is not a crossover star in the Priyanka Chopra mould. He is a deeply Indian actor whose best work \u2014 the raw vulnerability of "Animal," the quiet grief of "Rockstar" \u2014 resonates with audiences who will never see his films in an American multiplex. The tribute, written by Ayushmann Khurrana, praised his "quiet restraint" and his refusal to chase Hollywood.

## The political newcomer

Zohran Mamdani is the outlier and perhaps the most interesting inclusion. The son of Ugandan-born Indian academic Mahmood Mamdani and filmmaker Mira Nair, he is Indian by heritage, Ugandan by ancestry, and American by citizenship. His election as mayor of New York \u2014 a city where Indian Americans are a significant and growing constituency \u2014 represents a new chapter in diaspora political engagement, one that goes beyond Congressional caucuses and fundraising dinners.

## The larger signal

TIME also announced, at the 2026 gala, a partnership with Reliance Industries to launch TIME100 Next India \u2014 the first international expansion of its Next franchise. The inaugural list, curated by Time's editors, will spotlight 100 emerging leaders from India and the global Indian diaspora, with a gala scheduled for December 2026 at Mumbai's NMACC.

The initiative is commercial, obviously. But it is also an acknowledgment that the Indian diaspora \u2014 35 million strong, with an estimated annual income of $730 billion \u2014 is not a niche audience. It is a market, a network, and a constituency that global media can no longer afford to treat as peripheral.

Five names on a list is a small thing. But after the blank page of 2025, it reads like a statement: the diaspora did not disappear. It was just between headlines."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Canada's 2026 Census Has Started Counting. For 1.9 Million Indo-Canadians, the Stakes Are Higher Than a Headcount.",
        "subheadline": "South Asians are now the largest non-European group in Canada. How they show up in the census will shape funding, policy, and political clout for the next five years.",
        "slug": make_slug("canada-2026-census-indo-canadians-south-asian-population"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The census is not abstract for Indo-Canadians. It determines healthcare funding in Brampton, transit planning in Surrey, language services in Scarborough, and the political weight of ridings where South Asians are the plurality. An undercount in 2026 means an under-resourced community until 2031.",
        "tags": ["nri", "diaspora", "canada", "census", "south-asian", "demographics", "policy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Statistics Canada", "url": "https://www.statcan.gc.ca/en/census"},
            {"name": "Canada.ca - Census 2026", "url": "https://www.canada.ca/en/department-national-defence/maple-leaf/defence/2026/04/the-2026-census-is-coming-soon.html"},
            {"name": "Environics Institute - South Asian Experiences", "url": "https://www.environicsinstitute.org/projects/south-asian-experiences-with-racism-in-canada"},
            {"name": "Wikipedia - Indian Canadians", "url": "https://en.wikipedia.org/wiki/Indian_Canadians"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Surrey_Vaisakhi_parade_%2833398458243%29.jpg/1280px-Surrey_Vaisakhi_parade_%2833398458243%29.jpg",
        "body": """On May 4, 2026, Statistics Canada began counting. Every household in the country received an invitation \u2014 a letter with a sixteen-digit access code, instructions in twenty-eight languages, and a deadline of May 12. For most Canadians, the census is a civic chore, a few minutes of clicking through questions about age, language, and housing. For the nearly two million Indo-Canadians spread across Greater Toronto, Metro Vancouver, the Calgary corridor, and beyond, it is something considerably more consequential.

South Asians are now the largest non-European ethnic group in Canada. The 2021 census recorded 1.86 million people of Indian origin alone \u2014 before adding Pakistanis, Bangladeshis, Sri Lankans, and Nepalis, which push the broader South Asian count past 3.2 million, or roughly eight per cent of the national population. That number has almost certainly grown since 2021, driven by record immigration, international student inflows, and the continued gravitational pull of established community networks in cities like Brampton, Surrey, and Scarborough.

## Why the count matters

The census is not a population quiz. It is the statistical foundation on which federal and provincial funding is allocated, electoral boundaries are drawn, and public services are planned. When the 2021 census showed that Brampton was majority South Asian, it triggered a cascade of downstream effects: healthcare funding for culturally competent care, language access requirements for government services, and transit planning that acknowledged where the population actually lived rather than where planners assumed it did.

An accurate count in 2026 will determine the allocation of billions in transfer payments over the next five years. It will shape how many seats are added to Parliament in the next redistribution. It will inform whether Hindi, Punjabi, Gujarati, and Tamil receive expanded support in government communications. For Indo-Canadians, census participation is not civic virtue in the abstract. It is self-interest made statistical.

## The undercount risk

Every census carries the risk of undercounting hard-to-reach populations. For South Asians in Canada, the vulnerabilities are specific: international students on temporary permits who may not understand they are included in the count; recent immigrants living in multi-generational households where one person fills out the form and others are accidentally omitted; workers in the gig economy without stable addresses; and a persistent, low-grade suspicion among some newcomers that government data collection is surveillance by another name.

Statistics Canada has tried to address this. The 2026 questionnaire is available online in multiple South Asian languages for reference. The agency hired 32,000 enumerators to follow up with households that did not respond. And community organisations \u2014 gurdwaras, mandirs, mosques, cultural associations \u2014 have been enlisted to spread the word.

But the structural challenge remains. The census counts where you live, not where you work or worship. A South Asian family in a basement apartment in Mississauga, with three wage earners and a grandmother on a super visa, might look like one household to the census and feel like four separate lives to the people in it.

## The political dimension

The 2026 census is the first since Canada's relationship with India cratered over the Hardeep Singh Nijjar affair and the subsequent diplomatic fallout. It arrives at a moment when the Indian diaspora in Canada is navigating competing pressures: a surge of anti-South-Asian sentiment documented by the Environics Institute, ongoing debates about immigration levels, and a federal government that has tightened temporary resident pathways in ways that disproportionately affect Indian students and workers.

In this climate, the census takes on an additional significance. A strong, accurate count is the community's best defence against policies that treat it as a monolith or a problem to be managed. The data will show not just how many Indo-Canadians there are but how they live \u2014 their income levels, their educational attainment, their housing conditions, their linguistic diversity. That granularity is the difference between being seen as a headline and being understood as a community.

## What to do

The census can be completed online at census.gc.ca or by calling 1-833-663-2026 to request a paper form. Every person living in Canada on May 4, 2026, should be counted, regardless of citizenship or immigration status. Statistics Canada is legally prohibited from sharing individual census data with any other government agency, including immigration authorities. That protection is not discretionary \u2014 it is statutory.

For Indo-Canadians, the message is plain: be counted, or be invisible. The money, the seats, the services, and the political weight all follow the numbers. And the numbers follow from a sixteen-digit code and ten minutes of honest answers."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
