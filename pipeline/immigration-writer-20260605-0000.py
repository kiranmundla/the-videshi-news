#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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
        "headline": "The World Cup Starts Next Week. Rights Groups Say It Will Be Played in a 'Climate of Fear.'",
        "subheadline": "Advocacy coalitions warn of social media screening, racial profiling, and arbitrary detention as the biggest sporting event in history meets the most aggressive immigration enforcement regime in decades.",
        "slug": make_slug("world-cup-climate-of-fear-immigration-indian-diaspora-travel"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian fans traveling to World Cup games — and Indian Americans hosting visiting family — face heightened screening at ports of entry, social media vetting, and the background risk of enforcement sweeps in World Cup host cities. For anyone on a visa, the calculus of attending a match now includes a non-trivial immigration risk.",
        "tags": ["world-cup", "immigration", "travel-advisory", "ice", "cbp", "social-media-screening"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/sports/soccer/rights-group-warn-climate-fear-us-world-cup-games-2026-06-04/"},
            {"name": "The Worcester Telegram & Gazette", "url": "https://www.telegram.com/story/news/regional/2026/06/04/world-cup-travel-warning-new-england/90404145007/"},
            {"name": "TheTravel", "url": "https://www.thetravel.com/dhs-world-cup-travel-warning-2026/"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/sports-games/3307244-world-cup-2026-safety-concerns-amid-us-political-climate"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/2026_FIFA_World_Cup_Federal_Interagency_Coordination_Plan_%2855118098627%29.jpg/1280px-2026_FIFA_World_Cup_Federal_Interagency_Coordination_Plan_%2855118098627%29.jpg",
        "image_caption": "Federal officials at a 2026 FIFA World Cup interagency security coordination meeting",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """The 2026 FIFA World Cup kicks off on June 11. Forty-eight teams. Eleven American host cities. An estimated two million visitors descending on a country that, in the five months since federal agents shot and killed a nurse named Alex Pretti on a Minneapolis street, has not resolved the most basic question of what its immigration enforcement apparatus is allowed to do to people.

On Wednesday, the Sport & Rights Alliance — a coalition that includes Amnesty International, Human Rights Watch, and Transparency International — issued what amounts to a red-flag advisory for anyone planning to attend. "FIFA's weak response to the human rights threats documented by local groups and global civil society organisations means that we are witnessing a distinctively dangerous climate of fear, uncertainty, and repression," said Andrea Florence, the coalition's executive director.

The White House called the criticism "ridiculous scare tactics driven by liberal activist groups and the left-wing media." A spokesman said President Trump was focused on making the tournament "the safest and most secure in history."

## What the advocacy groups are actually warning about

The concerns are specific, not hypothetical. Immigrant advocacy organizations in New England — working with the Fair Immigration Reform Movement — published a travel advisory listing five concrete risks for World Cup visitors:

Denial of entry, arrest, detention, or deportation. Screening of social media accounts and searches of electronic devices at ports of entry. Aggressive immigration enforcement, including racial profiling. Restrictions on free speech, protest, and assembly. Limited access to legal representation if detained.

These are not theoretical scenarios. Switzerland's Breel Embolo, who played in the 2022 World Cup, was blocked from entering the United States just days before the tournament despite having entered the country without issue in 2025. His visa application was placed "under review" — no explanation given. A conditional fine from a 2018 incident in Basel, long since adjudicated, appears to have triggered additional scrutiny.

## The enforcement machinery in the background

The World Cup arrives at a moment when Immigration and Customs Enforcement and Customs and Border Protection are operating without regular congressional funding — a standoff that has lasted since mid-February, when Democrats refused to appropriate money for the agencies after the Pretti and Renée Good shootings in Minneapolis.

The Senate began voting Thursday on a roughly $70 billion bill to fund ICE and CBP for three years, through the end of Trump's term. Democrats are trying to attach amendments requiring federal agents to carry proper identification and use judicial warrants. Republicans want a clean bill with no conditions.

Meanwhile, DHS has been actively discouraging unlawful visitors from attending. The CBP Home App — originally designed for asylum seekers — is being promoted as a self-deportation tool. "KIND REMINDER: If you're here illegally, please self-deport via the CBP Home App & get a free trip home," the White House posted on X. DHS is offering $2,600 and a flight to anyone who voluntarily leaves.

## What this means for Indian visitors and the diaspora

For the roughly 4.8 million Indian Americans in the United States, and for the tens of thousands of Indian nationals who will fly in to watch matches in New York, Houston, Dallas, and the Bay Area, the calculus is complicated.

Anyone entering on a B-1/B-2 tourist visa should expect more thorough screening than usual. Social media accounts may be examined. Electronic devices can be searched at the border without a warrant — this has been settled law since 2013, but enforcement has intensified under the current administration's Online Presence Review, which now applies to all H-1B applicants and their dependents.

Indian Americans on H-1B, H-4, or other nonimmigrant visas face a different set of risks. The current enforcement climate has produced warrantless arrests of people going about their daily lives — including legal residents. A federal judge in Ohio is currently hearing testimony in a class-action lawsuit seeking to ban such arrests entirely. The outcome of that case could reshape enforcement practices in time for the tournament.

For Indian families hosting relatives who are visiting on tourist visas, the advice from immigration attorneys is consistent: carry all documentation at all times, avoid areas where enforcement operations are active, and understand that filming or observing an ICE operation — which Alex Pretti was doing when he was killed — carries real physical risk in the current environment.

## The gap between FIFA's promises and reality

FIFA President Gianni Infantino has repeatedly promised the world will be "welcomed" to the United States. The organization did not respond to Reuters' request for comment on Wednesday's advisory.

The gap between that promise and the reality on the ground is the core concern. More than 1.2 million people are expected in the New York–New Jersey metro area alone. Security screenings will be implemented at Penn Station and World Cup shuttle bus locations. New York officials said the screenings will involve magnetometers and be "more detailed than just a bag check."

CBP has separately warned that drones are prohibited near all stadiums, fan events, and team facilities, with fines up to $100,000.

For Indian cricket fans accustomed to traveling to ICC events around the world, the World Cup should have been a celebration. The tournament is the first to include 48 teams, the first hosted across three countries, and the first in which India — should it qualify for the knockout rounds — could play on American soil in front of the largest diaspora crowd in the sport's history. Instead, the conversation has shifted from which matches to attend to whether attending is worth the risk."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Federal Judge in Columbus Is Deciding Whether ICE Can Arrest You Without a Warrant",
        "subheadline": "An ACLU class-action lawsuit heard testimony this week from immigrants stopped in parking lots and on highways by unmarked vehicles, handcuffed without paperwork, and held without explanation. If the plaintiffs win, warrantless immigration arrests across Ohio would be banned.",
        "slug": make_slug("ohio-warrantless-ice-arrests-class-action-indian-visa-holders"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Columbus, Ohio — the epicenter of ICE enforcement in the state — has a rapidly growing Indian American community concentrated in the tech and healthcare sectors. The outcome of this lawsuit could determine whether legal visa holders in Ohio's immigration-heavy workforce face the constant background risk of being stopped, detained, and questioned without a warrant or probable cause.",
        "tags": ["ice", "warrantless-arrests", "ohio", "aclu", "fourth-amendment", "immigration-enforcement"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Columbus Dispatch", "url": "https://www.dispatch.com/story/news/courts/2026/06/04/ice-immigration-warrant-arrests-ohio-federal-court-deportation/90393997007/"},
            {"name": "The Cincinnati Enquirer", "url": "https://www.cincinnati.com/story/news/2026/06/04/cuban-immigrant-detained-ohio-jail-warrantless-ice-arrest/90393982007/"},
            {"name": "The Columbus Dispatch (enforcement data)", "url": "https://www.dispatch.com/story/news/2026/06/04/columbus-ohio-trump-ice-enforcement-immigration-arrests/90394001007/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/U.S._Immigration_and_Customs_Enforcement_%28ICE%29_Enforcement_and_Removal_Operations%27_%28ERO%29_officers_in_West_Palm_Beach%2C_Florida_on_February_14%2C_2025_-_4.jpg/1280px-U.S._Immigration_and_Customs_Enforcement_%28ICE%29_Enforcement_and_Removal_Operations%27_%28ERO%29_officers_in_West_Palm_Beach%2C_Florida_on_February_14%2C_2025_-_4.jpg",
        "image_caption": "ICE Enforcement and Removal Operations officers during an operation in West Palm Beach, Florida",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """A woman born in Peru pulls into a parking spot at Easton Town Center in Columbus, Ohio. She is on her way to work. Before she can get out of her car, a pickup truck cuts in front of her and blocks her path. Two men get out. They order her to open the door. The moment she does, they handcuff her. They put her in their truck. They drive her to a second parking lot, where other detainees are waiting. Nobody shows her a warrant. Nobody tells her why she is being arrested.

This happened. She testified about it on June 3, under oath, in the courtroom of Chief Judge Sarah D. Morrison of the U.S. District Court for the Southern District of Ohio.

She was one of three witnesses to testify on the first day of a hearing that could reshape immigration enforcement across the entire state. The ACLU of Ohio has filed a class-action lawsuit seeking a preliminary injunction to ban federal immigration agents from making warrantless arrests anywhere in Ohio. The hearing is expected to last three days.

## What the witnesses described

The three people who testified on Tuesday shared a common experience. All were stopped or pulled over by people in unmarked vehicles. All were handcuffed. None were shown any paperwork. None were given information about why they were being arrested. None had any significant criminal history.

One of the men, who entered the country legally in 2022 on a visa that has since expired, said he felt "kidnapped." "I felt devastated, finished inside," he told the court.

A second key witness is scheduled to testify on June 4 via video from Butler County Jail. Leosdanis Mulet-Zaldivar, a 35-year-old Cuban immigrant, entered the United States in 2022 under a Cuban humanitarian parole program. He was arrested in December without a warrant. He remains detained. "I am extremely worried that if I cannot be released soon, my family will not have enough money for food," he said in a court filing.

If the lawsuit succeeds, warrantless immigration arrests across Ohio would be expunged from the record. Future such arrests would be prohibited.

## Columbus: the enforcement epicenter

The lawsuit is not an abstraction. Columbus has been the epicenter of immigration enforcement in Ohio since Trump began his second term, according to federal data recently published by the White House.

Between January 25, 2025, and May 26, 2026, ICE arrested 552 people in Columbus. Another 223 were arrested in nearby Westerville, where the only ICE field office in central Ohio is located. The White House published the data on an interactive, space-themed webpage that frames immigrants as "aliens among us." It includes some criminal charges and countries of origin but does not specify how many apply to each category.

The data sit alongside findings from the independent Data Deportation Project, which obtained ICE records through an open records lawsuit. That data showed a 26-county area in central and eastern Ohio was linked to the Westerville field office.

## Why this matters for Indian visa holders

Columbus has one of the fastest-growing Indian American populations in the Midwest. The city's tech sector, anchored by companies like JPMorgan Chase, Nationwide, and a constellation of IT consulting firms, employs thousands of Indian nationals on H-1B visas. The healthcare system draws H-1B nurses and physicians. Ohio State University enrolls hundreds of Indian students on F-1 visas.

None of these people are the targets of immigration enforcement operations. But the testimony in Judge Morrison's courtroom describes a system that does not distinguish. Unmarked vehicles. No warrants. No paperwork. No explanation. The woman at Easton Town Center entered the country on a visa. She was going to work. She was handcuffed in a parking lot.

The Fourth Amendment to the U.S. Constitution protects against unreasonable searches and seizures. The question before Judge Morrison is whether immigration enforcement agents are bound by it — whether they need a warrant, or at minimum probable cause and an individualized determination, before they can detain someone on American soil.

For Indian Americans in Ohio, the practical implications are immediate. An H-1B holder driving to work in Dublin or Westerville passes through the same corridors where 775 people have been arrested in the last seventeen months. An F-1 student walking near campus occupies the same geography. The risk is not about immigration status. It is about being in the wrong place, in the wrong vehicle, when an unmarked truck pulls up.

## The legal battle ahead

The case names ICE, U.S. Customs and Border Protection, and the Department of Homeland Security as defendants. It seeks class-action status — meaning a ruling would apply to all Ohio immigrants, not just the named plaintiffs.

This is not the only legal challenge to the Trump administration's enforcement tactics. Federal judges have mostly ruled against the administration's efforts to force states and cities to cooperate with ICE, including a recent ruling dismissing a challenge to a Boston city ordinance limiting cooperation. The Justice Department last week filed four new lawsuits against states that have refused to approve unmarked license plates for federal immigration agents' vehicles.

The Ohio case is different because it goes to the core mechanism of enforcement: whether an agent can stop you, handcuff you, and detain you without a piece of paper signed by a judge. The Supreme Court of Ohio is also set to hear arguments over a school district's secret plan for responding to ICE operations on school grounds — another sign of how deeply enforcement has penetrated everyday institutional life.

Judge Morrison's ruling, expected in the coming weeks, will not settle the constitutional question permanently. But it will determine, for the immediate future, whether immigration enforcement in Ohio must meet the same standard that applies to every other law enforcement agency in the country: get a warrant first."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
