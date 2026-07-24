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

article1_body = """A decade ago, an Indian engineer who wanted Europe picked London or, failing that, Dublin. Today a growing share of them are landing in Frankfurt, Munich and Berlin — and the German state is no longer merely tolerating their arrival. It is actively recruiting them.

Speaking this month at a programme hosted by the Indian Mission to the United Nations, Florian Lodi, Germany's Commissioner for Multilateral Affairs, said India had become the single highest-priority country in Germany's international migration policy. The framing matters. Berlin is not describing Indians as one immigrant group among many. It is describing them as the people it most wants.

## The numbers behind the courtship

The figures Lodi cited are striking even by the standards of a diaspora accustomed to talking about itself in superlatives. Roughly 180,000 Indians contributed to Germany's workforce in 2025 — a 656 percent jump over the previous decade. More than 60,000 Indian students are now enrolled at German universities, making Indians the largest single group of foreign students in the country, having overtaken China. Over half of them, by Lodi's account, find work in Germany after graduating.

That last statistic is the one that separates Germany from the diaspora's older destinations. In Britain and Canada, the post-study pathway has narrowed sharply as both governments have tightened visa regimes. In Germany, the Skilled Immigration Act has done the opposite, smoothing the route from a student visa to a work permit to permanent residence. For an Indian family weighing where to send a child — and where that child might eventually settle — the calculus has quietly inverted.

## A "triple win," and its limits

Lodi called the arrangement a "triple win": good for the migrants, good for a German economy facing acute labour shortages, and good for India's surplus of skilled workers. The phrase is diplomatic, but it is not wrong. Germany's working-age population is shrinking; its engineering and IT sectors have vacancies they cannot fill domestically; and India produces more STEM graduates than its own labour market can absorb.

Yet the diaspora experience in Germany is not the frictionless story the slogans suggest. Research from the Bertelsmann Stiftung has found that while Indian students stay at high rates, skilled migrants are more likely to leave — citing bureaucratic complexity, difficulty bringing family into the labour market, and the slow grind of social integration in a country where language remains a barrier outside the office. The number of Indians living in Germany more than doubled between 1990 and 2015, but staying is not the same as belonging.

## The shape of a new diaspora node

What is forming in Germany is recognisably different from the established Indian communities of New Jersey or Southall. It skews young, technical and recent. It clusters around university towns and industrial hubs rather than around temples and grocery corridors built over two generations. The institutions that anchor older diasporas — the weekend Tamil schools, the regional associations, the Diwali melas that draw thousands — are only beginning to take root.

That is the quiet challenge ahead. Germany has solved the recruitment problem with remarkable speed. Whether it can become a place where Indians build the dense, self-sustaining community life that turned the United States and Britain into permanent homes is a longer question, and one that visa reform alone cannot answer. For now, the trajectory is unmistakable: Europe's largest economy has decided that its future is, in part, an Indian one — and the diaspora is arriving to test the promise.
"""

article2_body = """For most of the Indian diaspora's history, "Europe" meant a short list: Britain first, then the Netherlands, Germany and a scattering of others. Slovakia did not feature. This week it did.

Prime Minister Narendra Modi's state visit to Slovakia, at the invitation of his counterpart Robert Fico, made him the first Indian head of government ever to travel to the small Central European country. For the few thousand Indians who have made Bratislava and its industrial hinterland home, the visit was less about diplomacy than about recognition — proof that their corner of the map had become large enough to matter.

## A community measured in years, not generations

The Indian presence in Slovakia is new and still small, but it is growing fast. Diaspora members who spoke to news agency IANS ahead of the visit described a community that has roughly multiplied within a single year, drawn by work in the automobile sector and allied manufacturing that has made Slovakia one of the densest car-producing economies in the world per capita.

"It's a very privileged and historical moment for us," said Avinash Vijay Kumar, who hails from Kerala and has lived in Bratislava for nearly eighteen years — making him something of an elder in a community where most arrivals are far more recent. "Already a lot of opportunities have been created, a large number of people are working in sectors like automobile, and such opportunities for Indians will grow in the future."

Another member captured the velocity of the change in a single comparison. When India's President visited previously, he said, the Indian community in Slovakia numbered around 6,000. Within roughly a year, and with the Prime Minister's visit as a marker, far larger numbers are expected to follow.

## Why Central Europe, and why now

The Slovak story is a microcosm of a broader redrawing of the diaspora's geography. As traditional Anglophone destinations tighten immigration rules and post-study work routes, Central and Eastern European economies — labour-short, manufacturing-heavy and increasingly open to skilled foreign workers — have become unexpected magnets. Slovakia's car plants need engineers and technicians; India produces them in surplus. The match is pragmatic rather than romantic, but pragmatism is how most diasporas begin.

"Companies in this region, particularly in Slovakia, highly value Indian workers," said community member Manoj Whagle, who called the visit a matter of "great pride." The sentiment is familiar to anyone who has watched Indian communities take hold elsewhere: first the workers arrive, then the families, then the institutions.

## The living-bridge framing

Modi has spent much of his European travel this season leaning on the phrase "living bridge" — a description of the diaspora as a permanent connective tissue between India and its host nations. In larger communities, that framing can feel like rhetoric layered over a reality that long predates it. In Slovakia, it describes something genuinely in the making.

The community here has not yet built the temples, the cultural associations or the weekend language classes that mark a settled diaspora. What it has is a foothold, a fast-rising headcount, and now a prime ministerial visit that signals New Delhi is paying attention.

There is a strategic logic to that attention. As India deepens trade and defence ties with the European Union, its diaspora becomes a quiet asset — a network of professionals embedded in host economies who can act as informal ambassadors. Slovakia, a member of both the EU and the eurozone, is a useful node in that map even if its Indian population is modest. For the residents themselves, the visit was simpler than geopolitics. It was the first time many of them had seen their adopted home treated as a place worth an Indian Prime Minister's time. For a community of a few thousand far from the diaspora's traditional centres, that attention is its own form of arrival — confirmation that even the smallest outposts of Indians abroad are now counted, courted and, increasingly, expected to grow.
"""

article3_body = """The map of where young Indians go to build their lives abroad is being redrawn, and the most dramatic line on it is not a rise but a collapse. Between 2023 and 2024, the number of Indian nationals leaving to study in Canada fell 41 percent. It is the sharpest reversal in any major destination, and it tells the story of how quickly diaspora geography can turn.

The figures come from India's Ministry of External Affairs, which tracks nationals declaring study as their purpose of travel — the most granular official measure of where the next generation of the diaspora is forming. They show the first overall contraction in Indian student departures since the pandemic, down 15 percent in a single year. But the aggregate hides the real drama: the destinations that fell, fell hard, and the ones that rose are rising on durable foundations.

## The Anglophone retreat

Canada's 41 percent drop is the headline, but it is not alone. Departures to the United States fell 13 percent. The United Kingdom slid 28 percent. Australia dipped 12 percent. The four destinations that defined Indian student migration for two decades — the English-speaking countries where the largest, most established diaspora communities already live — all contracted in the same year.

The causes are political as much as economic. Canada capped study permits and curtailed post-graduation work rights, hollowing out the very pathway that had made it attractive. The United States has grown harder to enter and, for many families, harder to imagine settling in. Britain restricted the right of students to bring dependants. In each case, the message Indian families heard was the same: the door is narrowing, and the welcome is conditional.

## Where the flow is going instead

The destinations on the rise are unfamiliar names on a diaspora map dominated for decades by London, Toronto and the American campus town. Germany surged 49 percent, becoming the standout beneficiary and the largest source of foreign students for India after overtaking China within its borders. Russia rose 34 percent. Ireland climbed 30 percent. Singapore, France and New Zealand all gained.

The common thread is structural, not faddish. Germany offers near-free public tuition and a legislated route from study to work. Ireland and Singapore pair English-language instruction with open post-study pathways. The Gulf, increasingly, offers satellite campuses of elite American universities — Georgetown, Carnegie Mellon, Cornell — without the American visa lottery attached. Where the older destinations have made staying harder, the newcomers have made it easier, and Indian families have noticed.

## A diaspora's centre of gravity, shifting

This is more than an education-sector story. Student migration is the leading edge of diaspora formation. The Indian communities of the United States and Britain were seeded, in large part, by students who arrived to study and stayed to build. The places that capture today's students are likely to host tomorrow's settled communities, with all the temples, associations and family networks that follow.

For two decades that meant the Anglophone world. The 2024 data suggests the next chapter will be written, at least partly, in Berlin, Dublin and Dubai. The diaspora is not shrinking — over 1.8 million Indian students were enrolled overseas in 2024, up from roughly 1.3 million two years earlier. It is relocating.

There are second-order effects worth watching. A diaspora dispersed across more countries is harder to organise but also more resilient, less exposed to the policy whims of any single government. It also reshapes language and culture: the next generation of overseas Indians may be as comfortable in German or Arabic as in English, and the community's centre of gravity may drift away from the familiar institutions of North America. And the families making these choices are asking a sharper question than their predecessors did. The old question was where to get the best degree. The new one is where a degree still leads to a life.
"""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Germany Just Named India Its Top Migration Priority. 180,000 Indians Are Already at Work There.",
        "subheadline": "A 656 percent jump in a decade and the largest foreign-student body in the country have made Indians the people Berlin most wants to recruit — and a new kind of diaspora node is forming around them.",
        "slug": make_slug("germany-india-top-migration-priority-180000-workers-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Germany is rapidly becoming a major new hub of the Indian diaspora, displacing older Anglophone destinations as immigration rules tighten elsewhere. For NRIs and their families, it reshapes the calculus of where to study, work and settle in Europe.",
        "tags": ["nri", "diaspora", "germany", "europe", "skilled-migration", "students"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TheDialog via LinkedIn — Germany Prioritizes Indian Talent", "url": "https://www.linkedin.com/posts/germany-india-migration-policy"},
            {"name": "QS — Global Student Flows: Europe", "url": "https://www.qs.com/global-student-flows-europe/"},
            {"name": "Bertelsmann Stiftung — Indian high-skilled migrants and international students in Germany", "url": "https://www.bertelsmann-stiftung.de/en/our-projects/germany-and-asia/project-news/indian-high-skilled-migrants"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37120347/pexels-photo-37120347.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Brandenburg Gate in Berlin; Germany now hosts the largest group of Indian foreign students of any country.",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Modi Just Became the First Indian PM to Visit Slovakia. For a Few Thousand Indians There, It Was a Moment of Arrival.",
        "subheadline": "A diaspora that has roughly multiplied in a single year, drawn by Slovakia's car plants, found itself suddenly counted as India's Prime Minister came calling on Central Europe.",
        "slug": make_slug("modi-slovakia-first-visit-indian-diaspora-central-europe-automobile"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Central and Eastern Europe is emerging as an unexpected new frontier for the Indian diaspora as labour-short manufacturing economies recruit Indian engineers and technicians. Modi's first-ever visit signals New Delhi is tracking even the diaspora's smallest, fastest-growing outposts.",
        "tags": ["nri", "diaspora", "slovakia", "europe", "modi", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "IANS — 'Matter of great pride': Indian diaspora in Slovakia on PM Modi's visit", "url": "https://ianslive.in/matter-of-great-pride-indian-diaspora-slovakia-modi-visit"},
            {"name": "PMINDIA — PM addresses the Indian Diaspora in Europe", "url": "https://www.pmindia.gov.in/en/news_updates/pm-addresses-indian-diaspora-europe/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/21625704/pexels-photo-21625704.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Bratislava, Slovakia, where a small but fast-growing Indian community is concentrated around the country's automobile sector.",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Students Are Fleeing Canada — Departures Fell 41 Percent in a Year. The Diaspora's Map Is Being Redrawn.",
        "subheadline": "Official Indian government data shows the sharpest reversal in any major destination, as the Anglophone world tightens its doors and Germany, Ireland and the Gulf rise to take its place.",
        "slug": make_slug("indian-students-canada-collapse-41-percent-diaspora-map-germany-shift"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Student migration is the leading edge of diaspora formation — the places that capture today's students host tomorrow's settled communities. The 2024 collapse in Canada, US, UK and Australia, paired with surges into Germany and the Gulf, signals where the Indian diaspora's next generation will take root.",
        "tags": ["nri", "diaspora", "students", "canada", "germany", "migration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Collegedunia — Where Indian Students Study Abroad: MEA Data", "url": "https://collegedunia.com/news/where-indian-students-study-abroad-mea-data"},
            {"name": "Careers360 — Indian students look beyond US; Germany posts record growth", "url": "https://news.careers360.com/indian-students-germany-record-growth-2024-25"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7942484/pexels-photo-7942484.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "International university graduates; Indian student departures to Canada fell 41 percent between 2023 and 2024.",
        "image_attribution": "Pexels",
        "body": article3_body
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
