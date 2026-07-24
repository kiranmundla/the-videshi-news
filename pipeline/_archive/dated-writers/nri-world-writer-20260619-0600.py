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

raman_body = """Los Angeles voters did not so much choose Nithya Raman as discover, slowly, over the course of a week, that they already had. On the night of California's June 2 primary, the city councilmember from the 4th District trailed in third place, behind Mayor Karen Bass and an unlikely upstart: Spencer Pratt, the former reality-television personality who had built a campaign around the city's homelessness crisis and its handling of the Palisades fire. By the time county registrars finished counting hundreds of thousands of late-arriving mail ballots, Raman had passed Pratt by nearly four points. She will face Bass in November for control of the second-largest city in the United States.

For Indian Americans in Southern California — more than a million South Asians call the state home, the largest such population in the country — the result carries a particular weight. If Raman wins in the autumn, a daughter of the Indian diaspora will run a city of four million people, a $15 billion budget, and the logistical colossus of the 2028 Summer Olympics.

## A long road from Coimbatore

Raman was born in Coimbatore, in Tamil Nadu, and moved with her family to the United States as a child. Before politics she worked in urban planning and on homelessness policy, the issue that has defined her public life and now frames the campaign against Bass. First elected to the council in 2020, she is a member of the Democratic Socialists of America and has governed as a progressive willing to needle her own party's establishment.

That willingness is now pointed directly at the incumbent. In her first major interview after the primary was called, Raman accused Bass of leading the city "into a fiscal hole that has reduced services for every single resident," citing crumbling streets, thinning public services and what she casts as inadequate oversight of homelessness spending. Bass, for her part, enters the runoff with the advantages of incumbency and a steady share of the primary vote — roughly 34 percent to Raman's 29.

## The count, and the noise around it

The mechanics of Raman's comeback became a story of their own. Pratt's election-night lead evaporated as mail ballots — which in California may be counted for up to seven days after Election Day if postmarked on time — broke heavily for the progressive councilmember. The shift drew unverified fraud accusations from national conservative figures, including former President Donald Trump. California election officials pushed back firmly, noting that the slow tabulation is a deliberate feature of a system built to maximize access, not evidence of irregularity. One viral claim about ballots discarded in a Los Angeles neighborhood collapsed when reporters established that the neighborhood did not exist.

For the diaspora, the episode is a reminder of how thoroughly Indian-American candidates have moved from the margins to the center of American electoral life — and how that prominence now comes with the same scrutiny, and the same disinformation, that attends any high-profile race.

## What a runoff means for the community

Indian-American political organizations were quick to claim the moment. Indian American Impact, which has backed more than 200 candidates since 2016, congratulated Raman and framed her advance as proof of "the growing political power of Indian and South Asian American communities in California." Should she prevail, South Asian Americans would lead the two largest cities in the country, given the prominence of other community figures in municipal politics nationwide.

The contest also lands at a delicate moment. The next mayor will manage Los Angeles's relationship with a federal government that has sharpened its posture on immigration — a question of direct concern to a community with deep immigrant roots and mixed-status families. Raman, herself an immigrant, has made protection of immigrant Angelenos a campaign theme.

None of this guarantees victory. Raman faces a sitting mayor with institutional backing and a sizable bloc of Pratt's voters now up for grabs, many of them moderates and independents unlikely to warm to a democratic socialist. But the primary already rewrote the city's political map once. For Indian Americans watching from Artesia to the San Fernando Valley, November now offers the prospect of something that, a generation ago, would have seemed improbable: one of their own at the head of Los Angeles."""

museum_body = """For eight years, a small group of Indian-American organizers has been quietly assembling something the United States has never had: a museum devoted entirely to India's civilizational story. Now the team behind the proposed India Heritage Center is preparing to take its plan public, with an ambitious campaign to build a permanent institution in Washington, D.C.

The project is led by Dr. Amitabh Sharma, an Atlanta-based educationist and community leader, who describes the goal in terms that are as much corrective as celebratory. "Indian history and Indian civilization has never been portrayed in the strength that it deserves," he told the news agency IANS. "It is time that we told our story, telling our story in a very compelling narrative."

## Ten galleries, eleven thousand years

The vision is concrete. Organizers envision a 20,000-square-foot complex with ten themed galleries, a 350-seat auditorium, a library, reception spaces and a gift center. The exhibits would trace India's journey across more than 11,000 years — from ancient civilizations through scientific and spiritual traditions, periods of adversity, the independence movement, and its emergence as a modern democratic nation.

Rather than glass cases and placards, the planners are betting on technology. Immersive installations, virtual and augmented reality, interactive audio-video systems, murals and artifacts are all part of the proposed design — a museum built for visitors raised on screens rather than catalogues.

## A museum for the second generation

The deeper motivation is generational. Sharma says the center is intended not only for the diaspora but for "mainstream Americans and other communities seeking a deeper understanding of India's history and culture." For Indian-American parents, that dual audience speaks to a familiar anxiety: how to pass on a civilizational inheritance to children who are fluent in American life but increasingly distant from the specifics of where their families came from.

It is a problem the diaspora keeps trying to solve in pieces — weekend language classes, temple youth programs, heritage camps. A permanent national institution in the capital would be a more durable answer, a place that exists whether or not any given family makes the effort in any given year. Sharma frames it as a way for younger Indian Americans "to connect with their roots and heritage" while educating the broader public.

## Why Washington

The choice of Washington is deliberate. Organizers cite the city's visibility and international reach, and the symbolic value of placing India's story among the institutions that define how the United States narrates the world's cultures. The capital already hosts museums dedicated to the African American, Native American and other experiences; the absence of a dedicated India institution, organizers argue, is a gap worth closing.

Sharma has been careful to cast the project in inclusive terms. The center, he says, would highlight India's traditions of coexistence and cultural diversity, including its history as a refuge for persecuted communities — a framing that positions the museum as a civilizational showcase rather than a partisan or sectarian statement, a distinction that matters in a diaspora that does not vote, worship or remember as a monolith.

## The hard part

The vision is expansive; the path is not yet clear. Eight years of research and content development have produced a plan, but a 20,000-square-foot museum in Washington requires land, capital and the kind of sustained institutional fundraising that has tripped up more than one diaspora ambition. The organizers are now launching what they describe as a major campaign — the moment at which a long-private idea meets the public test of whether the community will pay for it.

The diaspora has shown it can write big checks. Indian Americans have given American universities billions of dollars over the past two decades, and temple-building across the country has demonstrated an appetite for permanent cultural infrastructure. Whether that generosity extends to a national museum — a slower, less personal kind of giving than a family's gift to an alma mater or a local temple — is the question the next phase will answer. For now, the India Heritage Center remains a blueprint: ambitious, detailed, and waiting to see whether the community that imagined it will build it."""

bat_body = """King Charles III spent an evening this month doing something he has done, in one form or another, for two decades: celebrating the Indian diaspora's contribution to British life. The occasion was the 20th anniversary gala of the British Asian Trust, the charity he founded in 2007 to tackle poverty across South Asia, and the event drew hundreds of guests to London and raised more than £1 million for its causes.

For Britain's 1.9 million-strong Indian-origin population — the country's largest ethnic minority and, by several measures, its wealthiest — the gala was a familiar kind of milestone: a moment of recognition from the very top of the British establishment, and a reminder of how far the community's institutions have travelled.

## Twenty years of a royal experiment

The British Asian Trust began as a bet that the prosperous British South Asian diaspora could be mobilized to fund development back in the subcontinent. Founded by the then-Prince of Wales together with a group of British Asian business leaders, the charity says it has since reached more than 18.8 million people across India, Pakistan, Bangladesh and Sri Lanka, working on education, livelihoods, mental health and anti-trafficking programs.

That model — diaspora wealth, channelled through a British institution, into South Asian development — is itself a statement about the community's arrival. The Trust's leadership reflects it. Its vice-chairs, Asif Rangoonwala and Shalni Arora, presented the King with a framed photograph of a 2007 charity cricket match between India and Pakistan, a nod to the soft-power diplomacy the organization has long practiced.

## "A source of inspiration"

The King's continued involvement, even after his accession, is not incidental. "We are grateful for the continued interest our Royal Founding Patron, His Majesty the King, takes in the Trust's work," said Hitan Mehta, the charity's chief executive, who was himself awarded an OBE for services to the British Asian community. "His deep and longstanding support for the British Asian Trust is a source of inspiration for our ambitions."

The British Asian Trust marked the occasion on social media as well, thanking the monarch for his presence at the annual dinner and reception.

For a community that has produced a prime minister in Rishi Sunak, captains of British industry, and a disproportionate share of the country's doctors and entrepreneurs, royal patronage is no longer a novelty. But it remains a marker of a particular kind of belonging — the recognition not merely of individual success but of the diaspora as a permanent, organized, philanthropically serious part of British civic life.

## The diaspora as donor, not just recipient

What makes the Trust notable is the direction of the money. For much of the 20th century, the story of South Asians in Britain was one of arrival and struggle — of migrants who came for work and remitted earnings home to families. The British Asian Trust inverts that narrative. Here the diaspora is the donor class, pooling significant wealth to fund development in the countries their parents and grandparents left.

That shift mirrors a broader pattern across the global Indian diaspora, where communities that once measured their connection to the homeland in remittances now increasingly express it through institutional philanthropy — endowed scholarships, hospital wings, disaster-relief funds and charities like the Trust. The gala's £1 million haul is modest against the scale of South Asian poverty, but the principle it embodies is not: a community confident enough in its own standing to give, at scale, through institutions that bear its name.

## A relationship that outlasts the crown's holder

Perhaps the quietest significance of the evening was its continuity. The Trust was founded by a prince and is now sustained by a king; its diaspora backers have stayed the course for two decades. In a period when Britain's relationship with its former empire is the subject of intense and often uncomfortable debate, the British Asian Trust offers a different register — neither apology nor nostalgia, but a working partnership between a monarchy and a migrant community that has become, unmistakably, British. For the 18.8 million people the charity says it has reached, that partnership has had concrete results. For the diaspora that funds it, the evening was a reminder that recognition, once earned, tends to endure."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "She Was in Third Place on Election Night. A Week of Counting Made Her a Contender to Run Los Angeles.",
        "subheadline": "Coimbatore-born councilmember Nithya Raman overtook a reality-TV upstart to reach the November runoff against Mayor Karen Bass — a race that could put a daughter of the diaspora atop America's second-largest city.",
        "slug": make_slug("nithya-raman-la-mayoral-runoff-karen-bass-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "More than a million South Asians live in California, the largest such population in the U.S. A Raman victory in November would place an Indian-born immigrant at the head of Los Angeles, its $15B budget and the 2028 Olympics — a marker of how far Indian-American political power has moved from the margins to the center.",
        "tags": ["nri", "diaspora", "indian-american", "politics", "los-angeles", "california"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "NBC Palm Springs", "url": "https://www.nbcpalmsprings.com/2026/06/09/incumbent-karen-bass-and-progressive-nithya-raman-advance-to-los-angeles-mayoral-runoff"},
            {"name": "New York Post", "url": "https://nypost.com/2026/06/16/us-news/nithya-raman-reveals-the-exact-moment-she-decided-to-run-against-karen-bass-in-la-mayor-bid/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/09/indian-american-impact-congratulates-nithya-raman-for-advancing-to-the-runoff-election-for-los-angeles-mayor/"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/15/Nithya_Raman%2C_2022.jpg",
        "image_caption": "Los Angeles City Councilmember Nithya Raman, who advanced to the November mayoral runoff against incumbent Karen Bass",
        "image_attribution": "Wikimedia Commons",
        "body": raman_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Ten Galleries, Eleven Thousand Years: The Diaspora's Plan to Build India a Museum in Washington",
        "subheadline": "After eight years of planning, organizers are launching a campaign for the India Heritage Center — what would be the first U.S. institution devoted entirely to India's civilizational story.",
        "slug": make_slug("india-heritage-center-museum-washington-dc-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A permanent national museum answers a problem the diaspora keeps solving in pieces — how to pass a civilizational inheritance to a second generation fluent in American life but distant from its roots. It also tests whether a community that gives generously to universities and temples will fund a slower, less personal kind of cultural infrastructure.",
        "tags": ["nri", "diaspora", "indian-american", "culture", "washington-dc", "philanthropy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "IANS Live", "url": "https://ianslive.in/indian-diaspora-pushes-for-landmark-museum-in-washington-dc--20260530062103"},
            {"name": "India West", "url": "https://indiawest.com/india-heritage-museum-planned-for-washington-d-c/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2846216/pexels-photo-2846216.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A museum gallery interior, illustrating the kind of immersive exhibition space planned for the proposed India Heritage Center",
        "image_attribution": "Pexels",
        "body": museum_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Twenty Years On, a King Still Toasts the Diaspora That Helped Him Build a Charity",
        "subheadline": "King Charles III joined the British Asian Trust's 20th-anniversary gala in London, where the diaspora-funded charity raised over £1 million and underscored how Britain's wealthiest minority became a donor class.",
        "slug": make_slug("king-charles-british-asian-trust-20-years-diaspora-philanthropy"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The British Asian Trust inverts the old migrant narrative: instead of remitting earnings home, Britain's 1.9 million Indian-origin residents now pool wealth through a British institution to fund South Asian development — a marker of a community confident enough in its standing to give at scale.",
        "tags": ["nri", "diaspora", "british-indian", "uk", "philanthropy", "king-charles"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Connected to India", "url": "https://www.connectedtoindia.com/king-charles-celebrates-indian-diaspora-at-british-asian-trust-anniversary-gala/"},
            {"name": "British Asian Trust", "url": "https://www.britishasiantrust.org/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/ac/King_Charles_III_%28July_2023%29.jpg",
        "image_caption": "King Charles III, Royal Founding Patron of the British Asian Trust, which marked its 20th anniversary in London",
        "image_attribution": "Wikimedia Commons",
        "body": bat_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
