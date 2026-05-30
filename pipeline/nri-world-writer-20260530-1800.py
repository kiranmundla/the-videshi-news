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
        "headline": "The Indian Diaspora Wants a Museum in Washington. Eight Years Later, They're Finally Ready to Build It.",
        "subheadline": "A 501(c)(3) led by Atlanta-based educationist Dr Amitabh Sharma is preparing to raise $12-14 million for a 20,000-square-foot India Heritage Center in the US capital — the first museum in America dedicated entirely to India's 11,000-year civilisational story.",
        "slug": make_slug("india-heritage-center-museum-washington-dc-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The proposed India Heritage Center speaks to a gap that millions of Indian Americans have felt for decades: the absence of a permanent, authoritative institution in the United States that tells India's story on India's terms. For a diaspora that has built temples, endowed university chairs, and funded political campaigns, the lack of a dedicated museum in a city lined with them has been a quiet embarrassment. This project would give second- and third-generation Indian Americans a place to encounter their civilisational inheritance — and give non-Indian Americans a reason to understand the culture behind the fastest-growing immigrant community in the country.",
        "tags": ["nri", "diaspora", "museum", "washington-dc", "culture", "heritage"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "IANS", "url": "https://ianslive.in/indian-diaspora-pushes-for-landmark-museum-in-washington-dc--20260530062103"},
            {"name": "Indian Community", "url": "https://indian.community/news/india-heritage-center-to-showcase-11000-years-of-history-in-washington/"},
            {"name": "Andhra Headlines", "url": "https://andhraheadlines.com"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14608587/pexels-photo-14608587.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Every major immigrant community in America eventually builds its monument. The Chinese got theirs in 1990 with the National Museum of Chinese History (now a Smithsonian affiliate). The African American Museum of History and Culture opened on the National Mall in 2016, two decades after Congress authorised it. Japanese Americans, Jewish Americans, Latino Americans — all have permanent institutions in Washington or New York that anchor their stories in brick, glass, and artifact.

Indians have had none. Until, perhaps, now.

## The Pitch

After eight years of planning, research, and what its founder calls "validating humongous amounts of data over 11,000 years," the India Heritage Center is preparing to formally launch its fundraising campaign for a permanent museum in Washington, DC. The project is led by Dr Amitabh Sharma, an Atlanta-based educationist and community organiser who registered the effort as a 501(c)(3) non-profit.

The ambition is not modest. Sharma envisions a 20,000-square-foot complex with ten themed galleries, a 350-seat auditorium, a library, reception facilities, and a gift centre. Visitors would move through India's civilisational arc — from the Indus Valley civilisation and Vedic traditions through scientific innovation, yoga and Ayurveda, the independence movement, and the country's emergence as a modern democratic and technological power. The tools would include VR, AR, immersive audio-visual environments, murals, and physical artefacts.

The estimated price tag: $12 million to $14 million. Funding would come from high-net-worth individuals, corporate sponsors, grants, crowdfunding, and naming opportunities for galleries and facilities.

## Why Washington, Why Now

The choice of Washington is deliberate. The city's museum ecosystem — the Smithsonian complex alone draws 30 million visitors a year — offers unmatched visibility. Sharma's team is already scouting locations in the capital, prioritising areas with heavy foot traffic.

"Indian history and Indian civilisation has never been portrayed in the strength that it deserves," Sharma told IANS. "We felt that it is time that we collected all this data, and then we showcased this to not only our community, our diaspora, our future generations who are totally oblivious of the facts — actual facts of the history — but also to sensitise the multiethnic community."

The timing aligns with a moment of peak Indian American visibility. The community numbers roughly five million, with median household incomes nearly double the national average. Indian Americans hold senior positions across technology, medicine, academia, and — increasingly — elected office. Five Indian Americans appeared on TIME's 2026 list of the 100 Most Influential People. Yet for all that institutional power, the community lacks a permanent cultural institution in the nation's capital that tells India's story comprehensively.

## The Harder Question

Museum-building in Washington is a notoriously long game. The National Museum of African American History and Culture took over a century from its first proposal to opening day. The American Latino Museum, authorised by Congress in 2020, still hasn't broken ground. Even well-funded efforts face years of site negotiations, design competitions, and fundraising plateaus.

Sharma's project does not yet have a confirmed site, and $12 million — while achievable for a community that raised $5.6 million in a single day during India Giving Day 2026 — is a fraction of what major Washington museums typically cost. The African American museum's final bill exceeded $540 million.

But Sharma frames the initiative as a starting point, not a finished blueprint. "This is not my project. It is not your project. It is the entire Indian community's project," he said. Early community response, he added, has been encouraging: "When I reach out to people, people say, yeah, why wasn't it done earlier?"

## What It Would Mean

If realised, the India Heritage Center would be the first dedicated museum in the United States focused on India's full civilisational, cultural, and historical journey. It would sit alongside institutions representing other major communities and civilisations — a permanent Indian presence in a city that functions as the world's museum capital.

For the diaspora, it would offer something that temples and cultural associations cannot: an authoritative, secular, public-facing institution that makes India's story legible to anyone who walks through its doors. For the second and third generations — the ones Sharma describes as "totally oblivious of the facts" — it could become the place where heritage stops being something your parents talk about and starts being something you can see, touch, and share.

The museum is still a proposal, not a building. But proposals are where monuments begin."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Three Months Into the Iran War, Four Million Gulf NRIs Are Still Waiting for Normal. It Isn't Coming Soon.",
        "subheadline": "Cancelled flights, shuttered schools, disrupted remittances, and a Strait of Hormuz that may not fully reopen until a peace deal sticks — the war's collateral damage to the Gulf's Indian community keeps compounding.",
        "slug": make_slug("gulf-nri-iran-war-disruption-flights-schools-three-months"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Gulf is home to roughly four million Indians — the largest single concentration of NRIs anywhere in the world. They drive taxis in Dubai, run trading firms in Sharjah, teach in CBSE schools in Kuwait, and wire billions in remittances home every year. Three months into the Iran war, every layer of that life has been disrupted. Flights home are cancelled or rerouted. Board exams were scrapped. Remittance corridors are squeezed. And the ceasefire that was supposed to bring normalcy keeps slipping. For a diaspora community that has spent decades building stability in a volatile region, this is the worst sustained disruption since the 1990 Gulf War evacuations.",
        "tags": ["nri", "diaspora", "gulf", "iran-war", "flights", "education", "remittances"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"},
            {"name": "CollegeChalo", "url": "https://collegechalo.com"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18341554/pexels-photo-18341554.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On Friday, a Fateh-110 missile launched by Iran struck the Ali Al Salem air base in Kuwait. Kuwaiti air defences intercepted it, but falling debris injured five US service members and destroyed two MQ-9 Reaper drones worth $60 million. Ceasefire talks in Washington ground to a halt after two hours. The Strait of Hormuz remains contested. And KLM, which hasn't flown to the Gulf since March 1, just extended its Dubai cancellations through August 2.

For the roughly four million Indians living in the Gulf states — from construction labourers in Qatar to IT professionals in the UAE to teachers in CBSE-affiliated schools across Kuwait, Bahrain, and Saudi Arabia — these are not distant headlines. They are the daily texture of life three months into a war that was supposed to end quickly.

## The Flights That Aren't Flying

The aviation picture tells the story most viscerally. Air France has suspended Gulf routes until at least June 10. KLM won't resume Riyadh and Dammam flights before July 12. Air Canada has cancelled Dubai and Tel Aviv services through September 7. Aegean, airBaltic, and several other European carriers have pulled out entirely.

Regional carriers have begun adding capacity — Emirates and Gulf Air are operating partial schedules — but the insurance premiums for overflying the region have skyrocketed. That means the NRI worker in Abu Dhabi trying to book a summer trip to Kerala is facing either dramatically higher fares, multiple connections through Southeast Asia, or the realisation that the direct Air India flight they used to take now threads through an active conflict zone.

India's External Affairs Ministry has maintained advisories urging nationals to exercise extreme caution. Evacuation planning, reminiscent of the 2015 Yemen airlift (Operation Raahat) and the 1990 Gulf War evacuation of 170,000 Indians, has been quietly updated — though officials have stopped short of issuing formal departure notices.

## The Schools That Went Silent

The educational disruption has been particularly acute. In early March, both CBSE and CISCE cancelled Class 10 and 12 board examinations across seven countries: Bahrain, Iran, Kuwait, Oman, Qatar, Saudi Arabia, and the UAE. Boards pivoted to internal assessments and alternative evaluations — a workaround that has left parents anxious about whether Indian universities and competitive exam bodies will treat those results as equivalent.

For the estimated 1,000 to 1,500 Indian medical students studying in Iran — drawn by tuition costs a fraction of Indian private medical colleges — the situation is grimmer. Many face a choice between staying for exams like the Olum-e-Paye and evacuating home, potentially losing an entire academic year.

The echoes of 2022 are uncomfortable. When Russia invaded Ukraine, roughly 20,000 Indian students — most of them in medical programmes — were stranded mid-semester. Thousands returned under Operation Ganga, but four years later, many are still navigating re-admission challenges, FMGE delays, and NEET reattempts. The Iran crisis is smaller in scale but structurally identical: cheap overseas education underwritten by family savings, interrupted by someone else's war.

## The Money Pipeline Under Pressure

India received $125 billion in remittances in FY2025, the highest of any country globally. The Gulf states are the single largest source of those flows. But the war has squeezed multiple pressure points simultaneously.

Shipping disruptions through the Strait of Hormuz have driven up insurance and freight costs. India's basmati rice exports to the Gulf have declined — a blow to the NRI households that anchor demand for Indian staples. The broader capital outflow from Gulf states, which averaged $150 billion annually in recent years, could slump by a third this year if the Strait remains contested, according to the Institute of International Finance.

NRI deposits in Indian banks, which had been a reliable source of foreign exchange, fell $2 billion in March alone — a drop attributed largely to Gulf-based depositors pulling money for immediate needs rather than parking it in NRE fixed deposits.

## The Ceasefire That Keeps Slipping

The fundamental problem is that the war has no clear endpoint. The US-Iran ceasefire talks that seemed close to resolution in mid-May unravelled after the US struck a port in southern Iran, drawing retaliatory fire. President Trump's insistence that any deal must permanently prevent Iran from developing nuclear weapons — a non-starter for Tehran's hardliners — has kept negotiations in a loop.

For Gulf NRIs, each failed round of talks extends the uncertainty. Companies are delaying hiring. Families are postponing home purchases. Parents are debating whether to send children back for the next academic year or hold them in India.

## What History Suggests

The Gulf's Indian community has survived disruptions before. The 1990 evacuation from Kuwait and Iraq — the largest civilian airlift in history at the time — displaced hundreds of thousands of Indian workers. Many returned within months. The 2008 financial crisis hammered Dubai's construction sector, sending tens of thousands of labourers home. They came back too.

But each recovery was enabled by a return to regional stability. This time, stability is the thing that hasn't arrived. The Strait of Hormuz — through which a fifth of the world's oil passes — remains a flashpoint. Iranian missile capability, though degraded, continues to threaten civilian infrastructure across the Gulf. And the diplomatic path forward depends on actors in Washington, Tehran, and Jerusalem whose timelines have nothing to do with whether an Indian teacher in Kuwait can get a flight home for her daughter's wedding.

Four million people are waiting. The war continues to not care."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
