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
        "headline": "The FBI Just Filed Federal Charges in the Maple Shade Double Murder. The Suspect Has Been Free in India for Nine Years.",
        "subheadline": "New court filings reveal a tangled web of H-1B workers, a love triangle, and a DNA breakthrough from a company laptop shipped 8,000 miles — in a case that has haunted New Jersey's Indian community since 2017.",
        "slug": make_slug("fbi-federal-charges-maple-shade-murder-nazeer-hameed-nri"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The case strikes at the heart of H-1B community life in suburban New Jersey — shared apartment complexes, shared employers, shared bus rides — and raises uncomfortable questions about what happens when justice crosses borders and the US-India extradition treaty is tested.",
        "tags": ["nri", "diaspora", "crime", "fbi", "extradition", "h1b", "new-jersey"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Courier-Post", "url": "https://www.courierpostonline.com/story/news/crime/2026/05/26/fox-meadow-maple-shade-murder-sasikala-anish-narra-nazeer-hameed/90243631007/"},
            {"name": "India Weekly", "url": "https://indiaweekly.biz"},
            {"name": "GG2.net", "url": "https://gg2.net"},
            {"name": "SJ Magazine", "url": "https://sjmagazine.net"},
            {"name": "Burlington County Prosecutor's Office", "url": "https://burlpros.org"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/10481266/pexels-photo-10481266.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On the evening of March 23, 2017, police responded to a call at the Fox Meadows apartment complex in Maple Shade, New Jersey. Inside a ground-floor unit on Hamilton Road, they found Sasikala Narra, 38, and her six-year-old son Anish dead from multiple slash wounds. The boy had been nearly decapitated. Both had defensive injuries. The scene was, in the words of Maple Shade Police Chief Christopher Fletcher, "unimaginable."

Eight years, two continents, and one company laptop later, federal prosecutors filed charges on May 13 against Nazeer Hameed, the man they say killed them both and then quietly returned to India.

## The H-1B corridor

The story of what happened at Fox Meadows is, in many ways, a story about the transient world of H-1B contract workers in the mid-Atlantic. Hameed, Sasikala's husband Hanumanth Narra, and dozens of other Indian IT professionals all lived in the same apartment complex while working for Cognizant Technology Solutions on a contract in Philadelphia. They shared bus rides to work, ate in the same kitchens, and orbited the same small social circle.

According to the newly unsealed federal complaint, the motive appears rooted in that proximity. Hanumanth Narra was allegedly having an affair with an unnamed woman in the Fox Meadows community. Hameed, the complaint states, had a "close personal relationship" with the same woman — who had also served as his sponsor and reference for his H-1B visa application.

On the morning after the murders, a coworker who rode the same bus as Hameed told investigators he had appeared "unfazed" when she mentioned the killings. He claimed not to have known about them, though his apartment was 480 feet from the victims' door.

## The DNA breakthrough

Investigators interviewed more than 70 people in the weeks following the murders, but Hameed was not initially among them. It would take years to connect him genetically to the crime scene — and the link came from an unlikely source.

Hameed had returned to India in September 2017, six months after the killings and just two weeks after the FBI publicized a $25,000 reward. He told an FBI agent who phoned him in October 2017 that he had left for a relative's medical emergency and planned to return within a year. He never did.

Attempts to obtain his DNA through Indian authorities failed repeatedly. The breakthrough came through his employer. Cognizant, headquartered in New Jersey and subject to US law, shipped Hameed's company-issued laptop from India to investigators — an 8,000-mile chain of custody that took months. In December 2024, DNA recovered from the laptop matched blood found at the crime scene.

"I'm actually mad at myself I didn't think of it sooner," lead investigator Detective Cunningham told SJ Magazine.

## The extradition wall

Hameed was indicted in February 2025 on two counts of first-degree murder. Authorities held off on announcing the charges until November, hoping to pursue extradition quietly. It didn't work.

The federal fugitive charge, filed May 13 in Camden federal court, focuses specifically on Hameed's flight from prosecution. The FBI has posted a $50,000 reward for information leading to his arrest. He is listed on the FBI's Most Wanted website and considered armed and dangerous.

Former New Jersey Governor Phil Murphy made a direct diplomatic appeal to Indian Ambassador Vinay Kwatra, writing that the "heinous crime shocked our state." Burlington County Prosecutor LaChia Bradshaw said on May 26 that her office would pursue Hameed with "tenacious" resolve.

But extradition between the United States and India remains notoriously difficult. The bilateral treaty exists, but successful transfers are rare, bogged down by procedural layers, sovereign reluctance, and cases that drag on for years.

## What it means for the community

For the Indian diaspora in the tri-state area, the Maple Shade case has lingered as an open wound. The victims were not public figures. They were a software engineer and her first-grader, embedded in the unremarkable rhythms of immigrant life — school pickups, apartment leases, office commutes.

The case also exposes the vulnerability of tightly knit H-1B communities where visa status, employment, and housing are often entangled. When something goes catastrophically wrong, the usual safety nets — calling the police, going to authorities, staying in the country — don't always apply in the same way.

Hameed remains free in India. The FBI is asking anyone with information to contact the Newark Field Office or the nearest US embassy. For Hanumanth Narra, there is still no trial, no verdict, and no justice — only the knowledge that the man accused of killing his wife and son is living without restraint on the other side of the world."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Americans Are Getting More Moderate, More Disillusioned, and More Scared. A New Carnegie Survey Maps the Shift.",
        "subheadline": "The 2026 Indian American Attitudes Survey finds that one in four respondents has been called a slur since 2025, moderates are now the largest ideological bloc, and neither major party is winning the community's trust.",
        "slug": make_slug("carnegie-2026-indian-american-attitudes-survey-political-shift"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For 5.2 million Indian Americans navigating dual identity, the survey captures a community caught between rising discrimination at home and deteriorating US-India relations abroad — redefining what political belonging looks like for the diaspora.",
        "tags": ["nri", "diaspora", "politics", "survey", "discrimination", "indian-american"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/russia-eurasia/research/2026/02/indian-americans-in-a-time-of-turbulence-2026-survey-results"},
            {"name": "YouGov", "url": "https://yougov.com"},
            {"name": "Pew Research Center", "url": "https://pewresearch.org"},
            {"name": "Stop AAPI Hate / AAPI Equity Alliance", "url": "https://aapiequityalliance.org"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8846666/pexels-photo-8846666.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """There are 5.2 million people of Indian origin in the United States. They are, by most standard measures, one of the country's most educated, highest-earning, and politically engaged immigrant communities. And right now, they are also one of the most unsettled.

The 2026 Indian American Attitudes Survey (IAAS), published by the Carnegie Endowment for International Peace in partnership with YouGov, offers the most comprehensive snapshot yet of a diaspora community in political flux. Based on a nationally representative survey of 1,000 Indian American adults conducted between November 2025 and January 2026, the findings paint a portrait of a group that is drifting away from both parties, experiencing rising discrimination, and changing how it lives in response.

## The partisan drift

Indian Americans remain disproportionately Democratic — but less so with each passing survey. The share identifying as Democrats has fallen from 52 percent in 2020 to 46 percent in 2026. Republican identification has ticked up modestly, from 15 to 19 percent. But the real movement is toward the middle: independents now account for 29 percent of Indian Americans, up six points since 2020.

The ideological picture reinforces this centrist drift. Moderates are now the single largest bloc at 32 percent, a four-point jump from 2024. Self-identified liberals declined from 25 to 21 percent. Conservatives held steady at 22 percent.

Beneath the toplines, demographic fault lines are widening. Education polarization has intensified — Democratic identification dropped 13 points among those without a college degree, while holding steady among graduates. Income polarization followed a similar pattern, with Democrats consolidating support among households earning above $100,000 while losing ground everywhere below.

Religion adds another layer. Hindus remain the most Democratic-leaning group. Christians are the most Republican-leaning — and the only subgroup where GOP identification grew between 2024 and 2026.

## The discrimination numbers

If the political data suggests a community pulling apart, the discrimination data suggests something pulling it together — though not in a way anyone would choose.

Since the start of 2025, one in four Indian American respondents has been called a racial slur. Nine percent report being physically threatened. Eight percent received hate mail. Six percent had property damaged. Four percent were physically assaulted.

Nearly half — 48 percent — say they encounter racist posts targeting Indians or Indian Americans "very or somewhat often" on social media. The emotional toll is pronounced: 50 percent report feeling angry, 33 percent anxious, 31 percent fearful, and 26 percent hopeless after seeing anti-Indian content online.

These numbers sit against a backdrop of documented escalation. A report by Stop AAPI Hate and Moonshot found that anti-South Asian slurs in violent, extremist online spaces in the US doubled between January 2023 and August 2024. The Carnegie researchers describe the United States as an "epicenter of anti-Indian digital racism."

## Living differently

What makes the discrimination findings especially striking is the behavioral toll. Indian Americans are not just enduring hostility — they are restructuring their daily lives around it.

The survey asked respondents whether they had avoided certain activities since the start of 2025 due to concerns about discrimination. Significant minorities reported modifying how they speak in public, what they wear, where they go, and how they participate in community life.

Most, however, are not planning to leave the country. A majority still recommend the United States for employment — a pragmatic endorsement that coexists, somewhat uncomfortably, with the community's growing unease.

## Trump, Modi, and the bilateral crack

Seventy-one percent of Indian Americans disapprove of Trump's job performance — a figure substantially higher than the general US population. Only 20 percent approve of his handling of US-India relations, down from 35 percent at the end of his first term and well below the 48 percent who approved of Biden's stewardship.

Opposition to Trump's immigration policies is especially sharp. Seventy-four percent oppose deporting immigrants to third countries. Two-thirds oppose the proposed $100,000 fee on new H-1B visa petitions — a policy that would disproportionately affect Indian-origin workers, who constituted 71 percent of new H-1B petitions in fiscal year 2024.

Yet broad disapproval of Trump has not translated into a Democratic surge. The Democratic Party's feeling thermometer rating among Indian Americans fell from 60 in 2024 to 53 in 2026. Harris's personal rating dropped ten points. The community's most-cited reason for not supporting the GOP? Intolerance of minorities, at 27 percent — up ten points from 2024. The top reason for avoiding the Democratic Party? That it's "too influenced by its left-wing," at 19 percent.

## The emerging picture

The Carnegie survey captures a community that is, in aggregate, neither moving right nor consolidating left. It is instead moving toward something less tidy: a centrist disaffection, shot through with real fear, real discrimination, and a pragmatic refusal to commit fully to either side.

For a diaspora that has spent decades building wealth, raising families, and accumulating political influence, the question is no longer simply who to vote for. It is what kind of country they are building their lives in — and whether it still wants them."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
