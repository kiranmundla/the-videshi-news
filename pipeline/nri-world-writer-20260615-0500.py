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

body_belfast = """When Imran Monin moved to Belfast last year on a skilled-worker visa, he chose the city deliberately. An engineer who came to the United Kingdom from India, he spent his weekends walking the peace lines and reading the murals — trying, in his words, to understand the place he had decided to call home. This week he found himself standing in the rain at one in the morning, evacuated from his flat as acrid smoke from a torched supermarket below him filtered up through the floors.

Monin is not the man at the centre of Belfast's worst street violence in years. That distinction belongs to a 30-year-old Sudanese asylum seeker charged with the attempted murder of a local man in a stabbing on Monday night. But the days of disorder that followed — masked crowds setting fire to homes and cars they believed housed immigrants, water cannon and plastic baton rounds, twenty-seven people left homeless on the first night alone — did not pause to check anyone's nationality. For Belfast's South Asian and wider migrant communities, the message was blunt: the colour of your skin is enough.

## A familiar machinery

What happened in Belfast followed a script that has become grimly familiar across the UK. Within minutes of the stabbing, footage was circulating on X and Facebook, repackaged by far-right accounts with captions about an "invader" and a "migrant invasion." Pages with tens of thousands of followers began posting meeting points for protests, urging men to come in dark clothing and "be prepared to fight." Most chillingly, lists of addresses said to house immigrants were shared online — turning social media into a targeting tool.

Police and politicians have since said the violence was significantly coordinated through online activity, some of it originating outside the island of Ireland entirely. Britain's minister for Northern Ireland, Hilary Benn, called it what it was: "If you are targeting people on the basis of the colour of their skin, how else can you describe them? That is racist thuggery."

## The diaspora caught in the middle

For Indian professionals who arrived in Northern Ireland on skilled-worker routes — filling roles in engineering, healthcare and IT that the region actively recruited for — the unrest carries a particular sting. They came through legal channels, often after years of paperwork, to do exactly the kind of work the UK says it needs. Yet on the street, the distinction between an asylum seeker and a chartered engineer dissolves into a single category: foreign.

This is the quiet anxiety that threads through diaspora life in Britain right now. British Indians are, by most socio-economic measures, among the most successful communities in the country — high rates of homeownership, strong representation in the professions, growing political clout. But mob violence does not consult the census. The same week that saw families with newborns rescued from burning homes also saw mosques in Glasgow go into lockdown and minorities targeted in Newtownabbey.

## The other side of the coin

The story did not end in the smoke. On Saturday, thousands gathered outside Belfast City Hall for an anti-racism rally, carrying signs reading "Your racism is not patriotism" and "Protect people not prejudice." Newlyweds emerged from City Hall, married minutes earlier, to join the crowd. It was, as one of them put it, "a week where you've seen the worst of humanity and the best of humanity in Belfast."

Monin saw both halves himself. The same Irish colleagues who had dropped him home to keep him safe were among those who later helped displaced residents; volunteers handed out tea in the rain; an opposition politician brought blankets to families sheltering in his constituency office. "At that time I realised there are always two sides of the coin," Monin said. "Same place, same city, some are protesting and some are helping in a different way."

For the thousands of Indians building lives across the UK, that is the uneasy bargain of the moment — a country that offers genuine opportunity and genuine welcome, alongside a violence that can erupt without warning and without distinction. The peace lines Monin spent his weekends studying were built to separate two communities defined by what they were not. The newest fault line in Belfast runs along a different border entirely, and the diaspora is learning, again, which side it can be forced onto."""

body_gopioct = """The Global Organization of People of Indian Origin's Connecticut chapter turned twenty this month, and it marked the milestone the way diaspora institutions tend to — with a banquet hall in Darien, five honorees, and a roomful of state lawmakers who understand that the Indian-American vote in Connecticut is no longer a rounding error.

The 20th Anniversary Awards Banquet, held June 13 at the Water's Edge Banquet Hall, is a useful lens on how a community organizes itself once it has settled, prospered, and decided it wants a seat at the table rather than just a invitation to the party. GOPIO-CT was founded in 2006 as a local node of an international network; two decades on, its annual awards have become a reliable barometer of who in the state's Indian-American community is considered to be carrying weight.

## The honorees

This year's five awardees read like a cross-section of the immigrant success story, each slotted into a category that doubles as a statement of values. State Senator Sujata Gadkar-Wilcox, who is also a professor of legal studies at Quinnipiac University, took the award for political leadership — a category that barely existed for the community a generation ago. Dr. Anil Diwan, founder and executive chairman of NanoViricides, was recognized for entrepreneurship and business achievement. Veteran journalist Ajay Ghosh, founder of the Indo-American Press Club, was honored for journalism. Nitin Mhatre, chief executive of First County Bank, received the corporate leadership award. And Professor Hemchandra Shertukde of the University of Hartford was recognized for achievement in engineering and applied sciences.

The spread is deliberate. "We select the awardees who have made an impact in our society and/or those who provide outstanding service," said GOPIO-CT President Mahesh Jhangiani. The unstated logic is that visibility breeds aspiration — that a teenager watching a state senator and a bank CEO collect awards in the same evening absorbs a lesson about what is possible.

## Why the small organizations matter

It is easy to fixate on the marquee names of the Indian diaspora — the tech CEOs, the cabinet secretaries, the billionaires. But the connective tissue of immigrant life is built by organizations like GOPIO-CT: chapters that organize Diwali events, run scholarship funds, lobby local school boards, and turn out for community members in trouble. They are the institutions that translate individual success into collective identity.

GOPIO International's founder president, Dr. Thomas Abraham, who chairs the chapter's awards committee, framed the honorees as "role models for our new generations," crediting the Connecticut chapter with "building up a good image of India and Indian Americans." The language is earnest, almost old-fashioned. But it reflects a real anxiety that runs beneath diaspora celebration: the worry that the second and third generations, fully assimilated and fluent in American life, will let the thread to their heritage go slack.

## A maturing political presence

The presence of multiple Connecticut lawmakers at a community awards banquet is its own data point. Indian Americans in the state have crossed a threshold from courted constituency to participant — Gadkar-Wilcox sits in the state senate, not merely beside it. That shift, repeated across Connecticut, New Jersey, Texas and California, is reshaping how both major American parties think about a community that is wealthy, highly educated, and increasingly willing to organize.

For the diaspora, the GOPIO-CT banquet is a small ritual with a large subtext. Twenty years is long enough for an organization to outlast its founding energy and become an institution — long enough to honor a state senator who might once have been one of its scholarship recipients. The community that gathered in Darien this month is no longer asking permission to belong. It is, increasingly, the one handing out the awards."""

body_bhalla = """Some legacies arrive with a flag. Last week, Representative Tom Suozzi presented Varinder Bhalla with a Special Congressional Award — including an American flag flown over the U.S. Capitol and a formal citation — in recognition of four decades of community service. The honor is the kind of ceremonial gesture that Washington produces by the hundred. But the story behind Bhalla's award is one that quietly shaped the legal standing of Indian Americans for generations after.

## The 1981 fight that opened doors

Bhalla's journey as a community organizer began in 1981, when, as vice president of the Association of Indians in America, he led a campaign with a deceptively dry objective: to have Indian Americans formally recognized as a minority group eligible for federal contracts. It worked. That reclassification — which sounds like bureaucratic housekeeping — unlocked government contracting opportunities for thousands of Indian small-business owners across the country. For an immigrant community then still finding its footing, it was a structural advantage that compounded over decades, helping seed the entrepreneurial class that is now taken for granted.

It is the kind of victory that rarely makes the highlight reels of diaspora history, precisely because it was procedural. There was no ribbon-cutting, no monument. But every Indian-American contractor who bid on a federal project in the years that followed was operating on ground that Bhalla and his colleagues had cleared.

## Stopping a bill in its tracks

A year later, in 1982, Bhalla turned to defense. An immigration bill then under consideration sought to restrict naturalized citizens from sponsoring family members for permanent residency — a provision that would have struck directly at the chain-migration pathways through which much of the Indian diaspora had built itself in America. Working alongside then-AIA President Gopal Khanna, Bhalla helped organize a petition drive that delivered 17,000 signatures to the House Judiciary Committee in Washington. The resolution, proposed by Congressman Romano Mazzoli and Senator Alan Simpson, was effectively halted.

For a community that was, at the time, numerically small and politically inexperienced, mobilizing 17,000 signatures and getting them into the right hands on Capitol Hill was no small feat. It was an early demonstration that the diaspora could organize not just to celebrate its culture, but to defend its interests in the machinery of American government.

## The American Dream, with receipts

Suozzi called Bhalla "a wonderful example of the American Dream" — the standard phrase for these occasions. But the citation pointed to a fuller picture. Bhalla's service did not stop at the water's edge. He helped establish anti-hunger programs in New Delhi and organized an eye camp in his hometown of Amritsar that provides free eyeglasses to underprivileged children. It is the dual loyalty that defines diaspora philanthropy: a man who fought for Indian Americans' standing in the United States while never quite letting go of the obligations he carried from home.

This is what makes Bhalla's recognition more than a routine congressional courtesy. The Indian-American community in 2026 is affluent, visible and politically courted — a constituency that presidents and prime ministers go out of their way to address. But that standing did not materialize on its own. It was assembled, decision by decision and petition by petition, by an earlier generation of organizers who did the unglamorous work of arguing the community into the legal and political frameworks of their adopted country.

## Honoring the architects

There is a tendency in diaspora storytelling to celebrate the destination and skip the construction. The astronaut, the CEO, the senator — these are the figures the community holds up. Less visible are the people who, decades ago, made sure the doors those figures walked through were unlocked in the first place.

Bhalla, now being honored for forty years of that work, belongs to that quieter category. The flag flown over the Capitol is a fitting symbol: not because it marks a single dramatic achievement, but because it acknowledges the long, patient labor of someone who helped a community claim its place under it. As the Indian diaspora's elder organizers age, recognitions like this one carry a second purpose — reminding a comfortable, successful generation exactly whose shoulders it is standing on."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "An Indian Engineer Evacuated His Belfast Flat at 1 A.M. The Mob Did Not Stop to Check Nationalities.",
        "subheadline": "Days of anti-immigrant violence in Northern Ireland have left South Asian and migrant communities afraid to leave home — and exposed how quickly the diaspora's hard-won success can be erased on the street.",
        "slug": make_slug("belfast-riots-indian-migrants-skilled-workers-northern-ireland-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian professionals who arrived in the UK on skilled-worker visas — filling roles the country actively recruited for — are being swept up in anti-immigrant violence that makes no distinction between an asylum seeker and a chartered engineer, exposing the fragility beneath the diaspora's socio-economic success.",
        "tags": ["nri", "diaspora", "uk", "belfast", "community-safety", "hate-crime", "skilled-workers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Times", "url": "https://www.thetimes.com/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "Associated Press / Reflector", "url": "https://www.reflector.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/9816117/pexels-photo-9816117.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Police and demonstrators face off on a city street at night during civil unrest",
        "image_attribution": "Pexels",
        "body": body_belfast
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Twenty Years On, a Connecticut Diaspora Group Hands Out Awards to a State Senator It Once Might Have Mentored",
        "subheadline": "GOPIO-CT's 20th anniversary banquet honored five Indian Americans across politics, business, journalism and engineering — a snapshot of a community that no longer asks permission to belong.",
        "slug": make_slug("gopio-ct-20th-anniversary-awards-connecticut-indian-american-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Local diaspora organizations like GOPIO-CT are the connective tissue of immigrant life — translating individual success into collective identity and political clout, and reflecting the anxiety that later generations may let the thread to their heritage go slack.",
        "tags": ["nri", "diaspora", "usa", "connecticut", "gopio", "community-organization", "awards"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
            {"name": "GOPIO International", "url": "https://gopio.net/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14636319/pexels-photo-14636319.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A spacious banquet hall set with round tables for a formal community event",
        "image_attribution": "Pexels",
        "body": body_gopioct
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "He Got Indian Americans Recognized for Federal Contracts in 1981. Congress Just Gave Him a Flag.",
        "subheadline": "Varinder Bhalla's Special Congressional Award honors four decades of unglamorous, structural work that helped build the legal footing the Indian-American community now takes for granted.",
        "slug": make_slug("varinder-bhalla-congressional-award-indian-american-aia-federal-contracts"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Diaspora storytelling celebrates the astronaut, the CEO and the senator while skipping the construction — the earlier generation of organizers who did the procedural, defensive work of arguing the community into America's legal and political frameworks in the first place.",
        "tags": ["nri", "diaspora", "usa", "new-york", "community-leadership", "philanthropy", "aia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
            {"name": "Office of Rep. Tom Suozzi", "url": "https://suozzi.house.gov/"}
        ]),
        "score_total": 66,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20417783/pexels-photo-20417783.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The United States Capitol dome with the American flag flying against a blue sky",
        "image_attribution": "Pexels",
        "body": body_bhalla
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   {art['slug']} — {wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
