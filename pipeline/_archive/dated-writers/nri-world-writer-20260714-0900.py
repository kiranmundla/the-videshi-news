#!/usr/bin/env python3
"""NRI World Writer — 2026-07-14 09:00 PT"""

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

# ─────────────────────────────────────────────────────────────
# ARTICLE 1: Operation Hardball — Bishnoi Indictment
# ─────────────────────────────────────────────────────────────

art1_body = """The U.S. Department of Justice has charged Lawrence Bishnoi, the imprisoned head of one of India's most feared criminal gangs, with directing the 2023 assassination of Sikh separatist leader Hardeep Singh Nijjar in Canada — a killing that ruptured relations between Ottawa and New Delhi and sent tremors through diaspora communities across North America.

A federal indictment unsealed in the Central District of California alleges that Bishnoi, 33, orchestrated the hit from an Indian jail cell using smuggled cellphones. He allegedly provided a co-conspirator with photographs and multiple addresses of Nijjar, who was gunned down by two masked assailants as he drove out of the parking lot of a Sikh temple in Surrey, British Columbia, on June 18, 2023.

## Operation Hardball

The charges against Bishnoi and his North American deputy, Satinderjeet Singh — known as "Goldy Brar" — form part of a sweeping federal investigation dubbed "Operation Hardball." Across three separate indictments, U.S. authorities charged 37 defendants tied to India-based organized crime groups with racketeering, extortion, and international drug trafficking. Twenty-four were arrested or already in custody at the time the indictments were announced.

"Transnational criminal gangs who spread fear, drugs, and violence will face the full force of justice and the weight of the federal government," First Assistant U.S. Attorney Bill Essayli said at a press conference in Los Angeles.

The investigation also targeted a rival gang led by Jaggu Bhagwanpuria, himself incarcerated in India but accused of running international operations from behind bars, and a methamphetamine distribution network operating at the U.S.-Canada border.

## India Responds

On Tuesday, India's foreign ministry addressed the indictment for the first time. Spokesperson Randhir Jaiswal said India remains "committed to working with its partners in combating transnational organised crime through close law enforcement and security cooperation."

Asked about the possibility of Bishnoi's extradition — which U.S. prosecutors have said they intend to seek — Jaiswal responded that New Delhi would deal with any such request "according to established legal obligations and judicial processes."

Notably, the U.S. indictment makes no allegation that the Indian government was involved in or had prior knowledge of the Nijjar killing. Essayli went further at the press conference, saying "India is very happy with today's operation." This stands in contrast to the diplomatic crisis triggered in 2023 when then-Canadian Prime Minister Justin Trudeau alleged "credible allegations" of Indian government complicity — a claim New Delhi dismissed as "absurd."

## A Diaspora Under Siege

For the estimated 770,000 Sikhs in Canada and hundreds of thousands more in the United States, the indictment underscores a chilling reality. According to the Wall Street Journal, U.S. prosecutors allege that Bishnoi "systematically used high-profile killings to terrorize the Indian diaspora."

The gang routinely targeted "prominent religious, social, and political leaders with violence," the indictment states, using these acts to "terrorise and extort members of the community." In one instance cited in the filing, Singh threatened a man — who turned out to be an undercover U.S. agent — with graphic violence: "I'm going to get the Mexicans to cut your ears. You'll wish you could wear glasses your entire life afterwards."

Singh remains at large, with a $50,000 FBI bounty on his head.

The case also revives questions about a separate plot uncovered in 2023, in which U.S. prosecutors charged an Indian government official with planning to assassinate the founder of Sikhs for Justice, a U.S.-based advocacy group. That alleged conspiracy unravelled when the operative unwittingly hired an undercover Drug Enforcement Administration agent in New York.

## What Comes Next

Canada and India have been working to repair relations in recent months, with both sides aiming to conclude a free trade agreement by year-end. The U.S. indictment, by attributing the killing to a criminal gang rather than state actors, may paradoxically ease the diplomatic path forward — even as it raises uncomfortable questions about how a jailed gangster managed to run a transnational assassination operation from inside an Indian prison.

For diaspora communities on both sides of the border, the legal proceedings offer a measure of accountability. But the fear that Bishnoi's network exploited — the vulnerability of immigrants far from home, navigating unfamiliar legal systems, often reluctant to draw attention — does not dissolve with an indictment.

As one Sikh community leader in Surrey told local media after the charges were announced: "We are glad the law is catching up. But the damage to our sense of safety — that takes longer to repair."

*This is a developing story.*"""

art2_body = """It started with a stabbing. On the evening of June 8, a 30-year-old Sudanese man was charged with attempted murder following a knife attack in Northern Ireland. Within hours, masked groups were moving through the streets of Belfast, setting homes and businesses ablaze, targeting anyone they believed to be an immigrant. Among their targets: an Indian grocery store on the Shankill Road, torched before it ever opened its doors.

A month later, the hate has not cooled. On the eve of July 12 — the date when Protestant loyalist communities in Northern Ireland mark the 1690 Battle of the Boyne with bonfires — a replica mosque was erected atop a pyre of wooden pallets in the town of Moygashel and set alight before police could remove it. A 56-year-old man has been charged with incitement to hatred. Britain's minister for Northern Ireland called the display "a sickening and cowardly act of intimidation."

## "People Are Scared"

The June 9–11 riots left 27 people homeless. *The Times* described the violence as "spontaneous pogroms." *The Irish Times* called it "a race-based pogrom." Rioters went door-to-door in parts of Belfast, attempting to identify houses occupied by immigrants. Water cannons — a measure associated with Northern Ireland's worst sectarian violence — were deployed for the first time in years.

For the roughly 10,000 Indians living in Northern Ireland, the majority concentrated in Belfast, the violence struck close to home.

Dr Satyavir Singhal, chairman of the Indian Community Centre and a consultant doctor who has lived in Northern Ireland for 25 years, said the Indian community was "deeply shaken."

"People are scared," Dr Singhal told the BBC. "I personally am hurt and deeply saddened by the incident."

The Indian-origin owner of the grocery store on Shankill Road — who had lived in Northern Ireland for 18 years and had recently purchased the property to start a new business — said he was left "heartbroken."

Dr Singhal noted that the Indian community has been a part of Northern Ireland since the 1930s. "We've been living and working together. There has never been a problem like this," he said. He offered to sit down with those responsible: "There are no issues on this planet that cannot be solved by talking to each other."

## A Pattern, Not an Aberration

The violence in Belfast did not erupt in a vacuum. Race hate crime in Northern Ireland has reached its highest level since records began in 2004, according to Amnesty International. Across the wider UK, an average of four to five anti-Muslim incidents were reported every week in June alone, with more than 40 per cent involving arson or firebombing, according to the Muslim Council of Britain.

The trend extends well beyond Northern Ireland. In the United States, FBI data released this month showed anti-Sikh hate crimes surging 3,700 per cent over the past decade, with anti-Hindu incidents hitting a record. In New Zealand, anti-Indian rhetoric became so heated in recent months that a minister was caught on camera calling the Indian community a "butter chicken tsunami" — days before Prime Minister Modi arrived for a historic state visit.

For the Indian diaspora, the arithmetic of vulnerability is becoming harder to ignore. Indians are now the largest foreign-born population in the UK, numbering over 900,000. In Northern Ireland, their presence is smaller but growing — doctors, shopkeepers, students, IT professionals who chose Belfast for its relative affordability and perceived safety.

## Counter-Protests and Solidarity

The Belfast riots did produce a counter-narrative. On June 13, large crowds of counter-protesters gathered in Belfast and Derry, holding banners reading "Riots don't speak for Belfast" and "Belfast stands against racism." Community organisations mobilised interfaith solidarity events. Local politicians across party lines condemned the violence.

But for those whose homes and businesses were destroyed, solidarity rallies are cold comfort. The Indian grocery store on the Shankill Road sits gutted. Its owner's 18-year investment in Northern Ireland — his citizenship application, his children's schooling, his place in the community — now carries a different weight.

## The Broader Reckoning

The UK's Combatting Antisemitism, Hate and Extremism Bill 2026, currently before Parliament, proposes criminal penalties for hate speech — but its scope is limited to antisemitic conduct. A Change.org petition calling for the bill to be expanded to cover hate crimes against Indians and all ethnic communities has gathered thousands of signatures. Indian Australian community leaders have launched a parallel push in Canberra, arguing that "legal protections should not depend on one's ethnic or religious background."

Northern Ireland's history of sectarian conflict is well documented. What is newer — and what the June riots made brutally visible — is the way anti-immigrant sentiment has begun to fill the space once occupied by Catholic-Protestant hostility. Community organisers in Belfast say sectarian tensions have increasingly been replaced by hostility towards ethnic minorities.

For Northern Ireland's Indian community, the question is no longer whether the hate is real. It is whether the institutions meant to protect them — the police, the courts, the legislature — will move as fast as the arsonists."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Thirty-Seven Defendants, Three Gangs, One Assassination: Inside the US Indictment That Finally Named Nijjar's Killers",
        "subheadline": "Operation Hardball charges Lawrence Bishnoi with directing the 2023 murder of a Sikh leader from an Indian prison cell. India says it will cooperate. The diaspora is still counting the cost.",
        "slug": make_slug("operation-hardball-bishnoi-nijjar-indictment-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Bishnoi gang systematically used high-profile killings to terrorize the Indian diaspora in North America, targeting religious, social, and political leaders. The indictment is the most significant legal action yet addressing transnational criminal threats to Sikh and Indian communities abroad.",
        "tags": ["nri", "diaspora", "sikh", "canada", "united-states", "organized-crime", "community-safety"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/americas/india-says-committed-combating-organised-crime-after-us-indictment-canada-murder-2026-07-14/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/world/india/the-jailed-mob-boss-the-u-s-is-linking-to-a-canada-hit-job-a8d8a82a"},
            {"name": "CNN", "url": "https://www.cnn.com/2026/07/08/americas/us-charges-lawrence-bishnoi-nijjar-murder/index.html"},
            {"name": "US Department of Justice", "url": "https://www.justice.gov/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Robert_F._Kennedy_Department_of_Justice_Building.jpg/1280px-Robert_F._Kennedy_Department_of_Justice_Building.jpg",
        "image_caption": "The Robert F. Kennedy Department of Justice Building in Washington, D.C., headquarters of the federal prosecutors who unsealed the Bishnoi indictment",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An Indian Grocery Store Burned Before It Opened. A Mosque Replica Set Ablaze on a Bonfire. Inside Northern Ireland's Summer of Hate.",
        "subheadline": "Belfast's June riots left 27 people homeless and an Indian community shaken. A month later, the arsonists have moved on to bonfires — and the 10,000 Indians in Northern Ireland are still waiting for the institutions to catch up.",
        "slug": make_slug("belfast-riots-indian-community-northern-ireland-hate"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Northern Ireland's Indian community — roughly 10,000 people, many of them doctors, shopkeepers, and IT professionals who chose Belfast for its affordability — found itself at the centre of anti-immigrant riots in June 2026. The violence, including the arson of an Indian grocery store, exposed the growing vulnerability of diaspora communities in the UK.",
        "tags": ["nri", "diaspora", "united-kingdom", "northern-ireland", "belfast", "hate-crime", "community-safety", "anti-immigrant"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/uk/belfasts-minority-groups-living-fear-after-racist-thuggery-2026-06-12/"},
            {"name": "CNN", "url": "https://www.cnn.com/2026/07/11/europe/northern-ireland-bonfire-mosque-hate-crime-intl/index.html"},
            {"name": "Just Earth News", "url": "https://justearthnews.com/sections/world/anti-immigrant-riots-shock-northern-ireland-indian-community-says-people-are-scared/"},
            {"name": "Wikipedia - 2026 Northern Ireland Riots", "url": "https://en.wikipedia.org/wiki/2026_Northern_Ireland_riots"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36623322/pexels-photo-36623322.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Belfast City Hall — the city where anti-immigrant riots in June 2026 left the Indian community shaken and an Indian grocery store in ashes",
        "image_attribution": "Pexels",
        "body": art2_body,
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
