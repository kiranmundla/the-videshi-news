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

gulf_body = """When Washington and Tehran announced the outline of a peace framework on June 14, the loudest sighs of relief may not have come from either capital. They came from the four million Indians who live and work along the Persian Gulf, the people for whom the region's wars are never abstract.

For weeks, the conflict that drew in Iran, Israel, and eventually American firepower had turned the Gulf from a place of opportunity into a place of calculation. Iran launched waves of missiles and drones across the region; most were intercepted, but the sirens were real, and so was the fear among the migrant workforce that keeps the Gulf's economies running. A ceasefire framework, however fragile, changes the arithmetic for a community that has spent the season weighing whether to stay, send money home, or leave.

## A community on edge

The Indian Embassy in Abu Dhabi captured the mood on June 14, issuing an advisory that urged citizens to exercise caution, monitor official channels, and avoid non-essential movement even as tensions appeared to ease. It was the kind of bulletin that lands differently when you are a construction worker in Sharjah or a nurse in Doha than when you are reading it from Delhi.

The numbers behind that anxiety are staggering. India's evacuation machinery, activated when the fighting peaked, brought home more than 4,400 citizens on roughly 19 special flights, including over 2,500 from Iran itself. The Ministry of External Affairs ran a 24/7 control room, and in the busiest stretch more than a million passengers moved back and forth through the region's airports as families recalibrated. For the diaspora, evacuation is not relief so much as rupture — the abandonment, however temporary, of jobs and lives painstakingly built abroad.

## The remittance lifeline

What makes the Gulf indispensable to India is not sentiment but money. The Gulf Cooperation Council states account for an estimated 38 percent of India's total inward remittances, the single largest regional source of the financial transfers that prop up millions of households back home. In the third quarter of the last fiscal year, India's personal transfer receipts climbed to roughly $36.9 billion, a figure that owes much to the men and women laboring in Gulf heat.

When the region wobbles, that lifeline frays. Disrupted flights, shuttered worksites, and frightened workers translate, within weeks, into thinner envelopes arriving in Kerala, Telangana, and Uttar Pradesh. The peace framework, if it holds, is therefore not merely a diplomatic event. It is an economic one, felt in village kitchens thousands of miles from the negotiating table.

## The UAE's reassurance

The Gulf states have not been passive bystanders to their migrants' fear. In March, the United Arab Emirates' ambassador to India, Abdulnasser Alshaali, took the unusual step of publishing an open letter to the Indian community, reassuring the diaspora that the federation's security and stability remained intact and that its residents were valued. That gesture, addressed to a workforce rather than a government, signaled how seriously the Gulf takes the loyalty — and the labor — of its Indian population.

It also underscored a quiet dependency that runs both ways. The UAE needs Indian workers as much as Indian families need UAE wages. A regional war threatens both ends of that bargain, which is why the easing of hostilities is being read in the Gulf's Indian enclaves as a chance to exhale.

## What comes next

A framework is not a treaty, and the diaspora has learned to be skeptical of announcements. The returnees now face the practical question of when, and whether, to go back. Employers must decide how quickly to restart stalled projects. And families that pulled loved ones home must weigh the renewed pull of Gulf salaries against the memory of this summer's sirens.

For now, the calculus has shifted from survival toward cautious normalcy. The four million Indians of the Gulf have weathered the region's volatility before, and history suggests most will stay or return — drawn by wages that no peace deal can replace and no war has yet erased. The framework buys them something rarer than safety. It buys them the freedom to plan again."""

motel_body = """The American roadside motel is one of the country's most familiar institutions, and for decades a quiet truth has sat behind its neon signs: a remarkable share of them are owned by Indian Americans, and a striking number of those owners share a single surname. In San Francisco, that story is finally being moved from folklore into a museum.

The Tenderloin Museum is building the first permanent exhibition in the United States devoted to Indian American hotelier history, an installation slated to open in 2027 as part of the museum's expansion into a newly acquired space. It is an unusual subject for a permanent exhibit — not a war, not a movement, but a business model — and that is precisely what makes it a landmark for the diaspora.

## From SRO to empire

The exhibit traces a specific lineage: the journey from managing single-room-occupancy hotels in San Francisco's gritty Tenderloin to commanding hotel ownership across the country. Indian Americans today own an estimated 60 percent of America's hotels and motels, and by widely cited industry counts roughly 70 percent of those owners carry the surname Patel — a Gujarati clustering so pronounced it spawned the affectionate shorthand "Patel motel."

That dominance did not arrive fully formed. It began with a handful of immigrants, some undocumented, who leased cheap residential hotels in mid-century San Francisco and built, family by family and lease by lease, a network that would eventually stretch nationwide. The model — relatives pooling capital, living on-site, working punishing hours, then helping the next arrival do the same — became a template for an entire community's ascent.

## A historian's eight years

The intellectual spine of the exhibit is Mahendra K. Doshi's book, "Surat to San Francisco: How the Patels from Gujarat Established the Hotel Business in California 1942-1960." Doshi spent eight years on the project and interviewed more than 160 trailblazing hoteliers and their descendants, bringing a specific strand of the South Asian diaspora into documented focus for the first time.

On May 21, the museum hosted Doshi for a lecture paired with a community screening of "Patel Motel Story," a 2025 short documentary inspired by his research that premiered at the Tribeca Film Festival. The pairing of an octogenarian's archival labor with a festival film captures the moment this history is having: old enough to need preserving, fresh enough to draw a crowd.

## The institutions line up

What separates this from a one-off cultural event is the weight behind it. The exhibition is being developed with the Indo-American Hotelier Exhibition Funds Development Committee and backed by the American Hotel and Lodging Association, the Asian American Hotel Owners Association, and the AAHOA Charitable Foundation, alongside the Bhartiya Mandal Foundation. A fundraising gala, "The Indian American Dream," was held on April 4 at the San Francisco War Memorial to underwrite the work.

That coalition matters. AAHOA alone represents thousands of hotel owners controlling a substantial slice of American lodging. When trade bodies of that scale put money and name behind a museum exhibit, they are not merely funding nostalgia. They are staking a claim that this immigrant business story belongs in the permanent record of American enterprise.

## Why a museum, and why now

There is a deeper logic to housing this story in the Tenderloin specifically. The neighborhood is where the pioneers actually began, in the SROs that newcomers leased when nothing else was available to them. To anchor the exhibit there is to insist that the glittering national hotel empire and the down-at-heel residential hotel are parts of the same continuous story.

For a diaspora often celebrated for doctors, engineers, and tech founders, the hotelier exhibit honors a less glamorous but equally consequential path to American success — one built on hospitality, sacrifice, and the willingness to live behind the front desk. Committee members have framed it as a tribute to founders who, used to long hours of hard work, persevered and risked everything to find success in America.

When it opens, the exhibit will do for the Patel motel what plaques and halls of fame have long done for other immigrant trades. It will tell visitors that the unremarkable sign they have driven past a thousand times marks something worth remembering."""

british_body = """For decades, the story of British Indians was told in the language of arrival — of corner shops, NHS wards, and the long climb of newcomers. A run of recent studies suggests the story now needs a different vocabulary, one borrowed from the language of established wealth. By several measures, British Indians have become the most economically successful ethnic group in the United Kingdom, and the data is forcing a quiet reassessment of what the diaspora has become.

The most arresting figures come from a London School of Economics analysis published earlier this year, which found that Indian-origin households are now the wealthiest ethnic group in Britain. Median household wealth among Indian families more than doubled over roughly a decade, climbing from about £93,000 to £206,000 between 2012 and 2023. That is not the trajectory of a community still finding its feet. It is the trajectory of one that has arrived and is compounding.

## A portrait of success

A separate study from the Policy Exchange think tank, surveying Britain's ethnic minorities, reached a complementary conclusion: British Indians rank as the country's most successful minority group across a broad set of indicators. Their homeownership rate, around 71 percent, sits well above the national average of roughly 63 percent. In education they trail only the British Chinese, and on measures of social integration they score as the most integrated minority in the country.

For a population of more than 1.9 million, these are not marginal advantages. They describe a community that has converted the classic immigrant emphasis on education and property into durable, heritable advantage — the kind that shapes neighborhoods, schools, and eventually politics.

## The rise of the "MINTs"

Perhaps the most intriguing finding is geographic. Analysts have begun tracking a phenomenon they call the "MINTs" — Minorities in Towns — aspirational British Indian families moving out of the big-city enclaves where immigrants traditionally clustered and into provincial and suburban towns once considered the heartland of the white middle class.

The migration is more than a housing-market footnote. As British Indians disperse into towns across the Midlands and the South, they are becoming a swing constituency in places that decide general elections. A community once concentrated in a handful of urban seats is spreading into the marginal districts where British politics is actually won and lost, and the major parties have noticed.

## From minority to constituency

That shift reframes the diaspora's relationship with power. For years, British Indian political influence was discussed in terms of symbolism — a Cabinet minister here, a peer there, the milestone of a British Indian prime minister. The new data points to something more structural: a voting bloc with rising wealth, high turnout propensity, and a geographic spread that makes it impossible for either Labour or the Conservatives to take for granted.

The community's institutions are pressing the point. A white paper from Aston University, provocatively titled "A Diaspora That Built a Nation," was launched at the House of Lords, an explicit bid to recast British Indians not as guests who succeeded but as builders woven into the national story. The choice of venue was itself a statement about where the community now expects to be heard.

## The uses and limits of a label

There is a risk in all of this, and it is the familiar one that attends any "model minority" narrative. Aggregate success obscures the families who have not risen — the older labor-migrant communities, the pockets of deprivation that averages paper over, the assumption that an entire group can be summed up by its median. Wealth statistics flatter, and they can also be weaponized to dismiss the disadvantages that persist within and beyond the group.

Still, the broad direction is hard to dispute. In the space of two generations, British Indians have moved from the periphery of British economic life to a position near its center, accumulating wealth, property, and political weight along the way. The corner-shop story has not ended so much as graduated. The question now facing the community — and the country — is what a confident, prosperous, geographically dispersed diaspora chooses to do with the influence it has earned."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Fragile Peace in the Gulf Is the Best News Four Million Indians Have Had All Summer",
        "subheadline": "The US-Iran framework announced June 14 barely registered in Delhi headlines. In the Gulf's Indian enclaves, where remittances and safety hang on the region's stability, it changed everything.",
        "slug": make_slug("gulf-peace-framework-four-million-indians-remittances-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Gulf accounts for an estimated 38% of India's inward remittances, money that props up millions of households in Kerala, Telangana, and Uttar Pradesh. For the four million Indians working the region, a regional war is not abstract geopolitics but a question of whether to stay, send money home, or evacuate. The peace framework buys them the freedom to plan again.",
        "tags": ["nri", "diaspora", "gulf", "uae", "remittances", "us-iran", "evacuation", "mea"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/middle-east/"},
            {"name": "Ministry of External Affairs, Government of India", "url": "https://www.mea.gov.in/"},
            {"name": "Reserve Bank of India - Remittances Survey", "url": "https://www.rbi.org.in/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8434127/pexels-photo-8434127.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Workers rappel down the calligraphy-clad facade of Dubai's Museum of the Future, a reminder of the migrant labor force that keeps the Gulf's economies running",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": gulf_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The 'Patel Motel' Built an American Empire. Now San Francisco Is Putting It in a Museum.",
        "subheadline": "The Tenderloin Museum is opening the first permanent US exhibition on Indian American hotelier history — tracing a path from leased residential hotels to ownership of 60% of the nation's lodging.",
        "slug": make_slug("patel-motel-tenderloin-museum-indian-american-hotelier-exhibition"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For a diaspora celebrated for doctors, engineers, and tech founders, the hotelier exhibit honors a less glamorous but equally consequential path to American success — one built on hospitality, sacrifice, and living behind the front desk. Anchoring it in the Tenderloin SROs where the pioneers began insists that the national hotel empire and the down-at-heel residential hotel are parts of one continuous immigrant story.",
        "tags": ["nri", "diaspora", "patel-motel", "tenderloin-museum", "san-francisco", "hospitality", "aahoa", "indian-american"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Tenderloin Museum", "url": "https://www.tenderloinmuseum.org/"},
            {"name": "Asian Hospitality", "url": "https://www.asianhospitality.com/"},
            {"name": "Today's Hotelier (AAHOA)", "url": "https://www.todayshotelier.com/"}
        ]),
        "score_total": 71,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/30171418/pexels-photo-30171418.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A classic American roadside motel sign, the everyday emblem of a hospitality industry in which Indian Americans own an estimated 60% of properties",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": motel_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "British Indians Are Now the UK's Wealthiest Ethnic Group. The Data Is Reshaping British Politics.",
        "subheadline": "Median household wealth more than doubled to £206,000 in a decade. A new class of aspirational families moving to provincial towns — the 'MINTs' — is becoming a constituency neither party can ignore.",
        "slug": make_slug("british-indians-wealthiest-ethnic-group-mints-uk-politics-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "In two generations British Indians moved from the periphery of British economic life — corner shops and NHS wards — to a position near its center, accumulating wealth, property, and political weight. As the 'MINTs' disperse from urban enclaves into the marginal towns where elections are decided, a community once discussed in terms of symbolism is becoming structurally powerful. The question now is what a confident, prosperous diaspora does with the influence it has earned.",
        "tags": ["nri", "diaspora", "british-indians", "uk", "wealth", "mints", "politics", "lse"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "London School of Economics", "url": "https://www.lse.ac.uk/"},
            {"name": "Policy Exchange - Portrait of Modern Britain", "url": "https://policyexchange.org.uk/"},
            {"name": "Aston University", "url": "https://www.aston.ac.uk/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/31406151/pexels-photo-31406151.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A diverse crowd crosses a central London street, in a country where British Indians now rank as the wealthiest and most integrated ethnic minority",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": british_body,
    },
]

# word count check
for art in articles:
    wc = len(art["body"].split())
    print(f"WORDS [{art['slug'][:45]}]: {wc}")

print("---")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
