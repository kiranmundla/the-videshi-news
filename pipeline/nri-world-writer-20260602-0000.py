#!/usr/bin/env python3
"""NRI World Writer — 2026-06-02 batch"""
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

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: Texas redistricting and Indian Americans
# ═══════════════════════════════════════════════════════════════════════

art1_headline = "Texas Drew New Congressional Maps to Win Five Seats. Half a Million Indian Americans Got Drawn Out of the Equation."
art1_subheadline = "The Supreme Court let the redistricting stand. The March primary showed record turnout. Now the diaspora's fastest-growing political bloc faces its first real test under maps designed without them in mind."

art1_body = """The numbers are stark. Texas is home to more than 500,000 Indian Americans, concentrated in the suburban crescents around Houston, Dallas, and Austin that have become the economic engine rooms of the state. They are among the most educated, highest-earning, and fastest-growing demographic groups in American politics. And in August 2025, when the Texas Senate approved a new congressional redistricting map on a party-line 19-2 vote, their neighbourhoods were carved up with surgical precision — not because they were the target, but because they happened to live in the wrong postcode for the party doing the carving.

## The Map That Ate the Suburbs

The redistricting, ordered at the urging of President Donald Trump ahead of the 2026 midterms, aimed to flip five Democratic-held seats to Republican. It was the rare mid-decade redraw — Texas last did it in 2003 under Tom DeLay — and it followed a simple logic: take urban and inner-suburban districts that lean Democratic, and slice them open, attaching their constituent parts to vast rural territories where Republican voters dominate.

The Brennan Center for Justice documented one of the more consequential cuts: Fort Bend County, southwest of Houston, where a rapidly growing Asian American population — including one of the densest Indian American communities in the South — had made the area increasingly competitive. In the 2018 and 2020 cycles, an Indian American candidate lost narrowly in the Fort Bend-anchored district. The new map divided the county's Asian community across three separate congressional districts, diluting what had been a cohering political force into fragments too small to swing any single race.

Austin's districts suffered similar treatment. Representatives Greg Casar and Lloyd Doggett, both progressive Democrats, found their constituencies merged into a single District 37, forcing a primary clash. Casar's District 35 was redrawn to exclude most of Austin, severing its Democratic base. Houston's Ninth Congressional District was combined with the vacant 18th to create a new majority-Hispanic district tilted toward Republicans.

## The Court Said Go Ahead

A federal court in El Paso struck the maps down in November 2025, calling them an illegal racial gerrymander. The ruling lasted exactly two weeks. On December 4, the Supreme Court stayed it in a 6-3 decision, concluding the lower court had "failed to honor the presumption of legislative good faith." The maps were cleared for the 2026 elections.

Justice Elena Kagan, writing in dissent alongside Sonia Sotomayor and Ketanji Brown Jackson, offered a pointed rebuke: "We are a higher court than the District Court, but we are not a better one when it comes to making such a fact-based decision."

## The March Primary Told a Different Story

When Texans actually voted in the March 2026 primary, the results complicated the Republican calculus. Turnout exceeded 4.4 million — a record for a midterm primary. Latino voter participation surged 37 percent in majority-Latino regions, with roughly three-quarters voting in the Democratic primary. In January, Democrat Taylor Rehmet had already flipped Texas Senate District 9 by 14 points, a district Trump won just months earlier — a 31-percentage-point swing.

The lesson, as one analysis from MultiState put it: redistricting based on shifting voter behaviour is "aiming at a moving target." Republican gains among Latino voters that seemed durable in 2024 looked considerably less so by March 2026.

## Where Indian Americans Stand

The Carnegie Endowment's 2026 Indian American Attitudes Survey, a nationally representative poll of 1,000 adults conducted in partnership with YouGov, found a community in flux. Roughly seven in ten Indian Americans disapprove of Trump's job performance. The share identifying as Democrat has fallen from 52 percent in 2020 to 46 percent, while the independent share has risen to nearly one-third.

In a hypothetical rerun of the 2024 election, Democratic support remains about ten points below its 2020 high-water mark. Openness to a third candidate has increased. Indian American Republicans, meanwhile, continue to express strong partisan warmth — rating their party at 72 out of 100 across three survey waves.

What this means in Texas is nuanced. Indian Americans are not moving to the GOP in significant numbers, but they are becoming less automatically Democratic — which is precisely the kind of voter a gerrymander struggles to predict. The Fort Bend County districts that were drawn to dilute one political tendency may find themselves facing an electorate that does not vote the way the mapmakers assumed.

Indian-American Congressman Raja Krishnamoorthi, a member of the informal "Samosa Caucus" in the House, has urged the Department of Justice to investigate the maps for Voting Rights Act violations. "These maps target Texans of colour, including our vibrant Indian-American community," he said in a statement.

## The Midterm Test

The November 2026 midterms will be the first general election fought on the new lines. For half a million Indian Americans in Texas, the question is not merely whether their preferred candidates win or lose. It is whether their political infrastructure — the community organisations, the voter registration drives, the candidates drawn from their own neighbourhoods — can survive being distributed across districts designed to make them invisible.

The answer may depend less on the maps themselves than on whether the community's growing political energy — visible in record primary turnout, in the Carnegie data showing rising engagement — can outrun the gerrymander's arithmetic. Texas Republicans built these districts to last a decade. Whether they last through November is another matter entirely."""

art1_sources = json.dumps([
    {"name": "NRIGlobe", "url": "https://nriglobe.com/news/texas-senate-approves-gop-favored-redistricting-map-implications-for-nris-and-indian-american-representation/"},
    {"name": "MultiState", "url": "https://multistate.us/resources/texas-redistricting-2026-latino-voter-shifts-challenge-gop"},
    {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/emissary/2026/02/indian-american-survey-democrat-indpendent-trump"},
    {"name": "Wikipedia – 2025-2026 United States Redistricting", "url": "https://en.wikipedia.org/wiki/2025%E2%80%932026_United_States_redistricting"},
    {"name": "Brennan Center for Justice", "url": "https://www.brennancenter.org/our-work/research-reports/redistricting-mid-cycle-assessment"}
])

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Rubio, anti-Indian hate, and the Carnegie data
# ═══════════════════════════════════════════════════════════════════════

art2_headline = "Rubio Called Anti-Indian Hate 'Stupid Stuff.' The Data Says It's Something Else Entirely."
art2_subheadline = "The Secretary of State dismissed online racism as trolls and bots. A nationally representative survey of Indian Americans found that one in four has been called a slur since the start of 2025."

art2_body = """When US Secretary of State Marco Rubio was asked in New Delhi last week about rising racist commentary targeting Indians in America, his answer was brisk. "People say stupid stuff all the time on social media and in every country in the world, unfortunately," he said. He suggested that some of the offending posts might come from "a troll, a bot." He emphasised that the United States remains a welcoming country and that isolated offensive comments should not be taken as representative of the nation.

It was a diplomatic answer. It was also one that sits uncomfortably next to the Carnegie Endowment's 2026 Indian American Attitudes Survey — the most comprehensive empirical portrait of the community's experience with discrimination to date.

## The Numbers Behind the 'Stupid Stuff'

The Carnegie survey, conducted in partnership with YouGov between November 2025 and January 2026, polled 1,000 Indian American adults across the country. Its findings on discrimination are difficult to dismiss as the work of bots.

Forty-eight percent of respondents — nearly half the community — report encountering racist posts targeting Indians or Indian Americans on social media "very or somewhat often" since the start of 2025. The content is not ambiguous. The survey showed respondents a specific anti-Indian tweet and asked how frequently they see messages like it. The answer, for roughly half the diaspora, was: regularly.

But the hostility does not stop at screens. One in four Indian Americans reports being called a slur since the beginning of 2025. Nine percent have been physically threatened. Eight percent have received hate mail. Six percent have suffered property damage. Four percent have been victims of physical assault. Roughly one in eight reports experiencing some other form of harassment.

The emotional toll is measurable. Half of all respondents say they feel angry when encountering anti-Indian content online. One-third report anxiety. Thirty-one percent report fear. One in five feels hopeless.

## From Online Slurs to Real-World Consequences

Stop AAPI Hate, the coalition that has tracked anti-Asian incidents since 2020, documented a sharp escalation in anti-South Asian online threats. In a joint report with the tech firm Moonshot, the group found that anti-South Asian slurs in "violent, extremist online spaces" in the US doubled between January 2023 and August 2024.

"It's disturbingly high, the number of incidents our community members experience," said Manjusha Kulkarni, co-founder of Stop AAPI Hate. "Because so much of our world is online, that is real-world hate."

Kulkarni has described specific incidents that mirror the digital vitriol: an Indian American man harassed at a Virginia restaurant and told to "go home and do Bharatanatyam in your living room"; another receiving hate mail declaring, "America has spoken and we don't want people of your ethnicity poisoning the DNA of this country."

The Carnegie survey confirms that the threat has changed behaviour. A meaningful share of respondents report avoiding certain activities — speaking a South Asian language in public, wearing traditional clothing, visiting certain neighbourhoods — out of concern about harassment.

## A Community That Responded With Organisation

The community's response has been neither silent nor passive. On April 20, 2026, Indian American Impact convened its "We Belong" summit at the Mayflower Hotel in Washington, DC, gathering elected officials, organisers, and advocates from across the country. Virginia Lieutenant Governor Ghazala Hashmi spoke on immigrant rights. Stop AAPI Hate's Kulkarni presented data. Dozens of South Asian elected officials participated.

"At a moment when our communities are being targeted and our loyalty questioned, we came to Washington not to ask for belonging, but to assert it," said Chintan Patel, Executive Director of Indian American Impact. The timing proved grimly apt: the very next day, the President amplified racist rhetoric targeting Indian Americans on social media.

Even Vivek Ramaswamy — the son of Indian immigrants, Republican gubernatorial candidate in Ohio, and hardly a figure associated with identity politics — felt compelled to denounce the hard-right demonisation of Indians in a *New York Times* column. When a Republican political figure publicly rebukes his own ideological flank on anti-Indian bigotry, the phenomenon has moved well beyond trolls and bots.

## The Political Paradox

What makes the discrimination data particularly politically volatile is that it has not neatly benefited either party.

Nearly half of Indian Americans fault the Republican Party for discrimination against their community. At least one-third view the GOP as intolerant of minorities. This suggests a ceiling on Republican growth among Indian Americans, no matter how aggressively the party courts them.

But that disapproval has not translated into renewed Democratic consolidation. The Carnegie survey found that Democratic identification has fallen from 52 percent in 2020 to 46 percent, with the independent share rising to nearly a third. Ratings of the Democratic Party and its leaders have declined over the past two years, even as opposition to Trump remains broad-based.

The result is a kind of political homelessness. Indian Americans are being pushed away from the Republican Party by discrimination and rhetoric, and drifting from the Democratic Party by a less tangible but measurable disillusionment. The community that is growing fastest — 5.2 million strong, with median household incomes roughly double the national average — is also the one that neither party seems fully equipped to hold.

## What 'Welcoming' Actually Means

Rubio was not wrong that America is, in many structural ways, a welcoming country for Indian immigrants. The economic data is unambiguous: Indian Americans are among the highest-earning, most-educated demographic groups in the United States. They lead Fortune 500 companies, win spelling bees at statistically improbable rates, and staff the technology sector that undergirds the American economy.

But welcoming and safe are not the same thing. The Carnegie data shows a community that has achieved extraordinary economic success while simultaneously experiencing extraordinary levels of everyday hostility. One in four has been called a slur. Nine percent have been physically threatened. Half encounter racist content on their phones regularly.

Calling that "stupid stuff" may be diplomatically convenient. For the 5.2 million Indian Americans navigating it daily, the word that comes to mind is probably different."""

art2_sources = json.dumps([
    {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/26/marco-rubio-dismisses-racism-against-indians-in-us/"},
    {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/research/2026/02/indian-americans-in-a-time-of-turbulence-2026-survey-results"},
    {"name": "AAPI Equity Alliance / Stop AAPI Hate", "url": "https://aapiequityalliance.org/south-asian-hate-surges-in-u-s/"},
    {"name": "The Indian Eye – Impact Summit", "url": "https://theindianeye.com/2026/05/15/at-a-time-of-rising-hate-south-asian-americans-gather-in-dc/"}
])

# ═══════════════════════════════════════════════════════════════════════
# PUBLISH
# ═══════════════════════════════════════════════════════════════════════

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": make_slug("texas-redistricting-indian-americans-midterms-fort-bend"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Over 500,000 Indian Americans in Texas face diluted political representation after new congressional maps divided key suburban communities — including Fort Bend County's growing South Asian bloc — across multiple districts ahead of the 2026 midterms.",
        "tags": ["nri", "diaspora", "indian-americans", "texas", "redistricting", "midterms", "voting", "political-representation"],
        "urgency": "medium",
        "sources": art1_sources,
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/18347166/pexels-photo-18347166.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": make_slug("rubio-anti-indian-hate-carnegie-survey-discrimination"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A nationally representative survey found that 48% of Indian Americans regularly encounter anti-Indian racism online and 25% have been called a slur since 2025 — numbers that challenge the Secretary of State's dismissal of the phenomenon as trolls and bots.",
        "tags": ["nri", "diaspora", "indian-americans", "discrimination", "hate-crimes", "carnegie-survey", "rubio", "stop-aapi-hate"],
        "urgency": "high",
        "sources": art2_sources,
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/4631061/pexels-photo-4631061.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": art2_body,
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
