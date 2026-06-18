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

body1 = """In a fast-growing Dallas suburb where roughly one in three residents is now Asian — most of them Indian — a man stood outside city hall, a cigarette dangling from his mouth, and tore an Indian tricolor in half while a crowd cheered "F*ck India." The video, filmed at an immigration-related protest in Frisco, Texas, ran for less than a minute. It has done far more damage than its length suggests.

By June 16, six Indian American members of Congress had issued a joint statement condemning the act. For a community that prides itself on quiet success — top incomes, top schools, a near-invisible footprint in American crime statistics — the episode has forced an uncomfortable question into the open: what happens when the model minority becomes the target?

## A Suburb Reshaped, and Resented

Frisco's transformation is the story of Indian America in miniature. Two decades ago it was a modest exurb north of Dallas. Then came the tech corridors, the corporate relocations, and the H-1B engineers who followed them. Today the city's Asian population sits near a third of the total, anchored by Indian families drawn by jobs, schools, and the gravitational pull of an established community.

That growth has not gone uncontested. In recent months, Frisco city council meetings have drawn speakers warning of an "Indian takeover" — language local leaders have called divisive and misleading. The flag-tearing was not an isolated outburst so much as the loudest expression of a resentment that has been building at the municipal microphone for a while.

The man in the video, identified as Clayton Walker, defended himself as exercising free speech and later claimed he was receiving threats. "All I did was exhibit my right to freedom of speech as an American," he wrote online. The lawmakers who condemned him conceded the point on principle while drawing a line on conduct.

## The Congressional Response

"We strongly support the constitutional right to freedom of expression for all Americans," read the statement from Representatives Raja Krishnamoorthi, Ami Bera, Pramila Jayapal, Ro Khanna, Shri Thanedar, and Suhas Subramanyam. "At the same time, we condemn the tearing of an Indian flag outside Frisco City Hall alongside hateful anti-India rhetoric, which continues to fuel anti-Indian violence and xenophobia."

The framing matters. The six lawmakers — the largest Indian American delegation ever to sit in Congress — did not treat the incident as a flag-desecration story. They treated it as a safety story. "The Indian American community is an important part of our nation and deserves to feel safe and respected," they said, warning that hate "cannot be tolerated or ignored."

That shift in vocabulary, from offense to fear, is the real signal. For first-generation NRIs who measured their American belonging in mortgages and merit scholarships, the flag was a stand-in for something less negotiable: the sense that the country they chose has chosen them back.

## The Diaspora's Dilemma

The episode lands on a community caught between two instincts. One is to keep its head down — the strategy that built the affluence in the first place. The other is to push back publicly, the way a maturing political bloc is expected to.

The presence of six members of Congress willing to put their names to a condemnation suggests the second instinct is winning. A generation ago there would have been no such delegation to call. The fact that there is one now is itself a measure of how far the community has come — and of how much it now feels it has to defend.

Frisco's leaders have distanced themselves from the rhetoric heard at council meetings. But the deeper anxiety is not about one man with a lighter and a flag. It is about whether the backlash to immigration in a tech-driven boomtown will keep finding an ethnic target, and whether the diaspora's hard-won comfort was always more conditional than it felt.

For now, the community is doing what it has learned to do in America: organizing, speaking, and refusing to be told it does not belong.

## Sources

The incident and congressional response were reported by IANS, India-West, and the offices of the Indian American members of Congress."""

body2 = """For the first time in modern history, India has overtaken England as the largest source of migrants to Australia — a milestone that closes a chapter opened by the British Empire and announces, in the dry language of census data, that the future of Australian multiculturalism speaks with an Indian accent.

According to figures released by the Australian Bureau of Statistics for 2025-26, there are now 971,020 India-born residents in Australia, edging past the 970,950 born in England. The margin — a few dozen people — is almost comically thin. The trend behind it is not.

## A Half-Million in a Decade

The Indian-born population has grown by more than 500,000 since 2015. Over the same period, the England-born population has declined steadily from a 2013 peak above one million. One curve was always going to cross the other; this year it did.

The top five migrant source countries now read: India (971,020), England (970,950), China (732,000), New Zealand (638,000), and the Philippines (412,530). Australia's overseas-born population has climbed to 8.8 million — about 32 percent of the country's 27.6 million people. Nearly a third of Australians were born somewhere else, and more of them were born in India than anywhere.

## The Age Gap That Explains Everything

The most consequential number is not the headline figure but the median age. The India-born population's median age is 36.1 years. The England-born population's is approaching 60.

That two-decade gap is the quiet engine of the whole story. The Indian community is not just larger; it is in the prime of its working and family-forming years, filling shortages in healthcare, IT, and construction while the older European cohort moves toward retirement. For a country worried about who will staff its hospitals and build its houses, a young, skilled, English-speaking population is an economic asset dressed as a demographic statistic.

For the diaspora itself, the youth skew means something else: this is a community still being built. Weekend Telugu and Tamil classes, new temples, cricket leagues, and Diwali melas are not nostalgia projects. They are the infrastructure of a population that expects to be here for generations.

## Migration Meets the Housing Crunch

The milestone arrives at an awkward political moment. Australia is grappling with its worst housing shortage in a generation, and migration has become a lightning rod. Populist parties such as One Nation have tied record migration to soaring rents and property prices, turning the newcomers into a convenient explanation for a structural problem.

The counterargument is inconvenient for the populists: Australia cannot build its way out of the housing crisis without importing the very tradespeople and construction workers it needs. Migration, industry experts argue, is less the cause of the shortage than part of its solution. The 2025-26 permanent migration program remains weighted toward the skilled stream, with a planned intake of 185,000 and a growing emphasis on "core skills."

## What It Means for the Next Wave

For Indians weighing a move, the signal is mixed but legible. The door remains open, but it is being reshaped around occupations that serve infrastructure and essential services. There is even discussion of raising the age limit for employer-sponsored permanent migration to 55 in some sectors — a potential opening for mid-career professionals who once assumed they had aged out.

The deeper point is harder to quantify. A community that arrives as the single largest migrant group does not assimilate quietly into someone else's story; it helps write the next one. England gave Australia its language, its parliament, and its cricket. India is now positioned to shape what the country becomes next — not as a guest, but as a founding partner in the version of Australia taking form right now.

## Sources

Figures are drawn from the Australian Bureau of Statistics 2025-26 release, as reported by VideshChalo and corroborated by demographic analyses of Australia's overseas-born population."""

body3 = """When Narendra Modi and Mark Carney shook hands on the sidelines of the G7 summit in Evian, France, this week, the photograph carried a subtext that mattered far more to the millions of Indians in Canada than to the trade negotiators in the room. "I am deeply grateful for your concern for the Indian diaspora," Modi told the Canadian prime minister. For a community that spent two years caught in the crossfire of a diplomatic collapse, gratitude was the right word.

It was the fourth meeting between the two leaders in under a year — a cadence that would be unremarkable between friendly nations and is remarkable between these two. As recently as 2023, India and Canada were expelling each other's diplomats and suspending visa services.

## From Rupture to Reset

The break came in September 2023, when then–Prime Minister Justin Trudeau publicly alleged that Indian agents were involved in the killing of a Khalistani separatist on Canadian soil. New Delhi rejected the claim as "absurd" and "politically motivated," retaliated with diplomatic expulsions, and suspended visa services for Canadians. Merchandise trade limped on, but the relationship's human plumbing — visas, travel, family visits — seized up.

The people who felt that seizure most acutely were not ministers but ordinary Indo-Canadians: students unable to bring parents over, families postponing weddings, professionals stranded by paperwork. A geopolitical quarrel had become a kitchen-table problem in Brampton and Surrey.

Carney's election changed the temperature. The reset began at last year's G7 in Kananaskis, where the two leaders agreed to return high commissioners to each other's capitals and restart ministerial dialogue. This week's meeting in Evian extended that thaw into ambition.

## Trade as the Glue

Carney was blunt about the goal: doubling India-Canada trade by the end of the decade, with a Comprehensive Economic Partnership Agreement targeted for completion in 2026. The leaders welcomed the recent visit of India's commerce minister Piyush Goyal to Canada and anticipated a Canadian trade mission to India later this year.

Behind the economic language sits a diaspora logic. Talent mobility, higher education, and "people-to-people ties" appear in every joint statement because they are where the two economies actually touch. Indian students remain one of Canada's largest international cohorts; Indo-Canadian professionals staff its tech and healthcare sectors. A trade deal that smooths mobility is, in practice, a diaspora deal.

The two governments also agreed to deepen cooperation on defence, energy, and information security, and Carney invited Modi to visit Canada before year's end — an invitation unthinkable eighteen months ago.

## What the Diaspora Gets

For the roughly 1.8 million people of Indian origin in Canada, the reset is less about CEPA clauses than about restored normalcy. Working high commissions mean faster visas. Resumed ministerial channels mean the next flare-up has somewhere to go besides the front page. And a leadership relationship measured in four meetings a year means the community is no longer hostage to a single accusation.

There is a harder truth underneath the warmth. The Khalistan question that detonated the 2023 crisis has not been resolved; it has been managed into the background while both governments pursue interests they cannot afford to lose. The diaspora benefits from that pragmatism, but it also knows the underlying fault line remains.

For now, the mood is one of cautious relief. A community that learned how quickly two governments can make its life difficult is watching them, just as deliberately, make it easier again.

## Sources

The meeting and its outcomes were reported by Inshorts, Livemint, and the Indian Ministry of External Affairs via the Prime Minister's Office."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Man Tore an Indian Flag Outside a Texas City Hall. Six Members of Congress Decided It Was a Safety Story.",
        "subheadline": "In Frisco, where one in three residents is now Asian, a viral act of contempt has forced the Indian American community to confront a question its success was supposed to settle: does it belong?",
        "slug": make_slug("frisco-indian-flag-torn-congress-condemn-diaspora-safety"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The flag-tearing has shifted how Indian Americans talk about belonging — from offense to fear — and shows a maturing diaspora willing to push back publicly through its largest-ever congressional delegation rather than keep its head down.",
        "tags": ["nri", "diaspora", "indian-american", "frisco", "community-safety", "texas"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "IANS", "url": "https://ianslive.in/indian-american-lawmakers-condemn-anti-india-act-in-texas"},
            {"name": "Rep. Krishnamoorthi (House.gov)", "url": "https://krishnamoorthi.house.gov/media/press-releases"},
            {"name": "India-West", "url": "https://www.indiawest.com/"},
            {"name": "Livemint", "url": "https://www.livemint.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/38064876/pexels-photo-38064876.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Indian national tricolor flying against a clear sky",
        "image_attribution": "Pexels",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Passed England as Australia's Largest Migrant Group. The Margin Was a Few Dozen People; the Trend Is Generational.",
        "subheadline": "With 971,020 India-born residents and a median age two decades younger than the English-born population, the diaspora is no longer assimilating into Australia's story — it is helping write the next one.",
        "slug": make_slug("india-overtakes-england-australia-largest-migrant-group-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Becoming Australia's single largest migrant group means the Indian community is now a founding partner in what the country becomes — its weekend language schools, temples, and cricket leagues are the infrastructure of a population that expects to stay for generations.",
        "tags": ["nri", "diaspora", "australia", "migration", "demographics", "census"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Australian Bureau of Statistics (via VideshChalo)", "url": "https://www.videshchalo.com/news/indian-diaspora-news/study-work-in-australia-indian-migrants-now-largest-foreign-born-population/"},
            {"name": "Australian Bureau of Statistics", "url": "https://www.abs.gov.au/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/36352144/pexels-photo-36352144.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A large crowd gathers outside the Sydney Opera House",
        "image_attribution": "Pexels",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "'Grateful for Your Concern About the Diaspora': Modi and Carney Just Turned a Two-Year Freeze Into a Trade Ambition",
        "subheadline": "Their fourth meeting in under a year targets a doubling of India-Canada trade by 2030 — but for 1.8 million Indo-Canadians, the real prize is the restoration of the visas and family ties a diplomatic collapse had frozen.",
        "slug": make_slug("modi-carney-g7-india-canada-reset-diaspora-trade-cepa"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The India-Canada thaw is, in practice, a diaspora deal: the trade talks center on talent mobility, education, and people-to-people ties, and a working diplomatic relationship means 1.8 million Indo-Canadians are no longer hostage to a single accusation.",
        "tags": ["nri", "diaspora", "canada", "india-canada", "g7", "trade", "cepa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inshorts", "url": "https://inshorts.com/"},
            {"name": "Livemint", "url": "https://www.livemint.com/"},
            {"name": "Narendra Modi (official) / MEA PMO", "url": "https://www.narendramodi.in/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5f/The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg",
        "image_caption": "Indian Prime Minister Narendra Modi, official portrait",
        "image_attribution": "Wikimedia Commons",
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    if wc < 400:
        print(f"⚠️  {art['slug']} only {wc} words — skipping")
        continue
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
