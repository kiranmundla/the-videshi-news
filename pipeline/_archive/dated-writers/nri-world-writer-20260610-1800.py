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
        "headline": "Modi Just Became India's Longest-Serving Elected PM. The Diaspora's Response Says Everything.",
        "subheadline": "US senators, Silicon Valley CEOs, and Indian American community leaders rushed to congratulate the prime minister as he crossed 4,399 consecutive days in office — surpassing Nehru's record.",
        "slug": make_slug("modi-longest-serving-pm-diaspora-celebrates-4399-days"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The speed and warmth of the diaspora's response — from Capitol Hill to Cupertino — reveals how deeply Modi's tenure has reshaped the Indian American community's political identity and its relationship with New Delhi.",
        "tags": ["nri", "diaspora", "modi", "india-politics", "indian-american"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Connected to India", "url": "https://www.connectedtoindia.com/indian-american-diaspora-leaders-applaud-modis-record-breaking-run-as-prime-minister/"},
            {"name": "The Times (UK)", "url": "https://www.thetimes.com/world/asia/article/super-powered-narendra-modi-soars-past-nehru-as-longest-serving-pm"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/us-congratulates-pm-modi-for-becoming-indias-longestserving-elected-pm"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5f/The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg",
        "image_caption": "Official portrait of Prime Minister Narendra Modi",
        "image_attribution": "Wikimedia Commons",
        "body": """On Wednesday, Narendra Modi became India's longest-serving elected prime minister, logging 4,399 consecutive days in office and edging past the record set by Jawaharlal Nehru, the country's first leader. Within hours, the congratulations streaming in from Washington, Silicon Valley, and Indian American living rooms made one thing clear: this milestone belongs to the diaspora almost as much as it belongs to New Delhi.

## The Numbers Behind the Record

Nehru held office from May 1952 until his death in May 1964 — 4,398 days as an elected leader. His earlier stint, from independence in 1947 to the first general election, was as head of an interim government. Indira Gandhi served longer in total but her tenure was fractured, interrupted by the post-Emergency defeat in 1977.

Modi's run has been unbroken: three consecutive mandates, each larger than the last. No Indian prime minister has done that before. The BJP and its supporters have been keen to frame the achievement in contrast to the Nehru-Gandhi dynasty — the tea seller's son outpacing the Harrow-educated aristocrat.

## Capitol Hill Weighs In

The American political establishment did not wait long. Senator John Cornyn of Texas, co-chair of the Senate India Caucus, called the tenure "nothing short of transformational" and credited Modi with lifting 250 million people out of poverty while turning India into the world's fastest-growing major economy. Senator Bill Hagerty of Tennessee praised the "comprehensive, global, and strategic" US-India partnership forged under Modi's watch.

US Ambassador to India Sergio Gor described the record as "a powerful testament to decades of dedicated public service and leadership." That an American ambassador would celebrate a foreign leader's longevity in office is itself a marker of how central the India relationship has become to Washington's strategic calculus.

## Silicon Valley's Quiet Endorsement

Nikesh Arora, CEO of Palo Alto Networks and one of the most prominent Indian-origin executives in American tech, offered his congratulations — a gesture that carried weight in a community that has watched Modi cultivate Silicon Valley ties more aggressively than any Indian leader before him. From the 2015 Digital India pitch at SAP Center in San Jose to the string of CEO roundtables on every US visit, the Modi government has treated the tech diaspora as both audience and ambassador.

## A Community Divided, But Paying Attention

Not everyone in the diaspora is celebrating. Progressive Indian American organisations have long criticised Modi's record on press freedom, minority rights, and the treatment of Muslims in India. The milestone arrives at a moment when a Carnegie Endowment survey found that one in four Indian Americans reports being called a slur since January, and many have begun self-censoring in public spaces.

But even Modi's critics would struggle to deny the structural shift his tenure has produced in the diaspora's political standing. The India Caucus is now among the largest country-focused caucuses in Congress. Indian Americans donate to both parties at record levels. And the community's visibility — from Kamala Harris's vice presidency to the appointment of Sriram Krishnan as AI policy adviser — owes something to the diplomatic machinery Modi built.

## What the Diaspora Actually Cares About

For the average NRI wiring money home or renewing an OCI card, the record matters less as a political symbol and more as a signal of continuity. Modi's government has pushed through UPI internationalisation, the trade facilitation portal, and liberalised NRI deposit schemes — all policies that directly touch diaspora wallets. The RBI's decision last week to absorb hedging costs on foreign currency deposits, expected to draw $35–40 billion from NRI accounts, landed in the same news cycle as the PM's record.

Continuity has a price, though. The longer Modi stays, the louder the question becomes: what comes after? The BJP has no visible succession plan, and the diaspora — which has invested heavily in the Modi brand — has reason to think about that more carefully than most.

## The View from Abroad

In London, The Times ran the milestone under the headline "Super-powered Narendra Modi soars past Nehru," noting temple bells ringing across India and rose-petal processions in BJP strongholds. The British Indian community, 1.8 million strong, has its own complicated relationship with the Modi era — navigating UK visa crackdowns and rising anti-Indian sentiment even as Indian-origin figures dominate the New Year Honours list.

The record is set. The celebrations will fade. What endures is the question the diaspora has been asking itself for twelve years: does Modi's India make it easier or harder to be Indian abroad? The answer, as always, depends on whom you ask."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Three Bay Area Hindu Temples Hit in Weeks. A Pattern Is Forming.",
        "subheadline": "Pro-Khalistan graffiti, a theft, and broken windows — the wave of vandalism targeting Hindu worship spaces in Northern California has the community demanding answers and installing cameras.",
        "slug": make_slug("bay-area-hindu-temple-vandalism-khalistan-graffiti-hate-crime"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For Indian Americans in the Bay Area — home to one of the densest concentrations of Hindu temples in the US — the attacks strike at the heart of community life, turning Sunday worship into a security calculation.",
        "tags": ["nri", "diaspora", "hate-crime", "hindu-temple", "bay-area", "community-safety"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/alarm-bells-as-hate-speech-and-crimes-against-hindus-on-the-rise-across-us-and-canada/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/hindu-temple-defaced-with-anti-india-graffiti-weeks-after-another-such-incident/"},
            {"name": "Jazzbaat24", "url": "https://jazzbaat24.com/breaking-news/baps-swaminarayan-temple-vandalized-in-new-york-indian-consulate-urges-swift-action/2595"},
            {"name": "US State Department (Bureau of South and Central Asian Affairs)", "url": "https://x.com/State_SCA"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Akshardham_Hindu_Temple_in_Jersey_City.jpg/1280px-Akshardham_Hindu_Temple_in_Jersey_City.jpg",
        "image_caption": "Akshardham Hindu Temple in Jersey City, one of many diaspora worship spaces facing security concerns",
        "image_attribution": "Wikimedia Commons",
        "body": """A devotee living near the Sherawali Temple in Hayward, California, discovered the damage first thing in the morning: pro-Khalistan graffiti sprayed in black ink across an exterior wall. It was the third Hindu worship space in the Bay Area to be targeted in a matter of weeks, and the community's patience had already run out.

## The Timeline

The sequence began with the Shri Swaminarayan Mandir in Newark, where anti-India and anti-Hindu graffiti appeared on the temple walls. Newark police called it a "targeted act" and opened an investigation. A week later, the Shiv Durga Temple — also in the East Bay — reported a theft. Then came the Sherawali Temple in Hayward, a copycat defacement that the Hindu American Foundation flagged publicly on X.

"Another Bay Area Hindu temple attacked with pro-Khalistan graffiti," HAF wrote. "HAF is in touch with temple leaders and in contact with the police."

The pattern is difficult to ignore. Three temples, three incidents, one region, all within weeks of each other. The Bay Area — home to one of the largest concentrations of Indian Americans in the country — has become ground zero for a tension that most diaspora members thought was confined to geopolitics.

## The Response

The US State Department's Bureau of South and Central Asian Affairs condemned the vandalism in a public statement, welcoming "efforts by the Newark Police Department to ensure that those responsible are held accountable." India's External Affairs Minister S. Jaishankar addressed the incidents directly: "Extremists and separatist forces outside India should not get space. Our consulate has lodged a complaint with the government and the police there."

HAF has urged temples across the region to install security cameras and alarm systems — practical advice that carries an uncomfortable subtext. Hindu temples in America, many of them open-door community centres that double as cultural hubs and weekend schools, are now being advised to think like potential targets.

## A National Problem

The Bay Area is not alone. In New York, the BAPS Swaminarayan Temple — a cornerstone of the city's Indian diaspora for decades — was desecrated earlier this month. Worshippers arriving for morning prayers found broken windows and defaced walls. The Indian Consulate condemned the attack and called on US authorities to act. Law enforcement is treating it as a hate crime.

Across the border in Canada, extortion threats have targeted Hindu temples, and in Australia, Brisbane's Shree Laxmi Narayan Temple was vandalised by Khalistan supporters, the latest in a string of attacks dating back to 2023. The Indian High Commission in Canberra issued a strongly worded statement about "the frequency and impunity with which the vandals appear to be operating."

## Why It Matters to the Diaspora

For the Indian American community, temples are more than places of worship. They are where children learn Hindi or Tamil on Saturday mornings, where grandparents find community after emigrating, where festivals like Diwali and Navratri bring together families who may live an hour's drive apart. An attack on a temple is an attack on the infrastructure of diaspora life.

The incidents arrive against a backdrop of rising concern about hate crimes targeting South Asians. A recent Carnegie Endowment survey found that one in four Indian Americans has experienced a slur since January 2026. FBI preliminary data for 2025 shows hate crimes against Asian Americans remain at more than double pre-pandemic levels.

## What Comes Next

Temple administrators across the Bay Area are now sharing security protocols — camera placement, alarm system vendors, volunteer patrol schedules. Some have reached out to local interfaith coalitions. Others are pressing elected officials for enhanced protection of religious sites.

The Hindu American Foundation has called for a federal investigation into whether the incidents are coordinated. So far, police have treated each case separately. But the community sees a pattern, and it wants the authorities to see one too.

"We're not asking for special treatment," one temple board member in Fremont told a local reporter. "We're asking to worship without looking over our shoulders."

The cameras are going up. The question is whether they will be enough."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Banks Just Hiked NRI Deposit Rates by 300 Basis Points. Here's Why Your Dollar Suddenly Matters More.",
        "subheadline": "The RBI is absorbing hedging costs on foreign currency deposits for the first time since 2013. Banks are expected to hoover up $35–40 billion from the diaspora by September.",
        "slug": make_slug("rbi-nri-deposit-rate-hike-fcnr-hdfc-sbi-dollar"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For NRIs who have parked dollars in low-yield savings accounts abroad, the RBI's move creates a rare arbitrage window — higher returns than US Treasuries, with the central bank eating the currency risk.",
        "tags": ["nri", "diaspora", "rbi", "nri-deposits", "fcnr", "banking", "remittance"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/some-lenders-hike-rates-fx-deposits-non-resident-indians-2026-06-10/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-banks-could-raise-35-40-billion-via-rbis-foreign-currency-deposit-scheme-2026-06-08/"},
            {"name": "India Tribune", "url": "https://indiatribune.com/india-world-top-receiver-remittances-workers-overseas/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/General_Post_Office_and_Reserve_Bank_of_India%2C_Kolkata%2C_India.jpg/1280px-General_Post_Office_and_Reserve_Bank_of_India%2C_Kolkata%2C_India.jpg",
        "image_caption": "Reserve Bank of India building in Kolkata, headquarters of the central bank's eastern operations",
        "image_attribution": "Wikimedia Commons",
        "body": """If you are an NRI with dollars sitting in an American savings account earning 4 per cent, Indian banks would very much like to have a word. Several of them hiked rates on foreign currency non-resident (FCNR) deposits by as much as 300 basis points on Wednesday, in what amounts to an aggressive pitch for diaspora dollars backed by the full machinery of the Reserve Bank of India.

## What Happened

The RBI announced last Friday that it would absorb the complete hedging cost for three- to five-year FCNR deposits — the mechanism banks use to protect themselves against rupee-dollar fluctuations. By eating that cost, the central bank effectively gave lenders permission to offer NRIs significantly better rates without blowing up their own balance sheets.

They did not wait long. HDFC Bank, India's largest private lender, hiked rates by 235–265 basis points to 6 per cent on three- to five-year deposits. State Bank of India raised rates by up to 300 basis points, now offering between 5.25 and 6 per cent depending on deposit size and tenure. AU Small Finance Bank went to 7.1 per cent on three-year deposits. Yes Bank landed at 7 per cent and above.

For context, three-year US Treasuries currently yield around 4.2 per cent. An NRI parking dollars in an FCNR deposit at 6–7 per cent is earning a meaningful premium — and the RBI is picking up the tab on the currency risk.

## Why Now

The rupee is having a terrible year. It is Asia's second-worst-performing currency in 2026, down 6 per cent so far, and it hit record lows in May. The RBI needs dollars, and NRIs have them — India's diaspora sent home $137.7 billion in remittances in 2024 alone, making the country the world's largest recipient of worker transfers.

The FCNR scheme is a redux of a playbook the RBI used in 2013, during the "taper tantrum" that sent the rupee tumbling after the US Federal Reserve signalled it would scale back bond purchases. That time, HDFC Bank alone mobilised $3.4 billion. This time, Punjab National Bank's CEO Ashok Chandra told Reuters the banking sector could collectively raise $35–40 billion by September.

"It is a win-win situation for non-resident Indians and for the banks," Chandra said, before adding that PNB alone aims to raise $2.5–3 billion. The bank plans to market the deposits "aggressively" across the United States, Canada, the United Kingdom, and the Middle East.

## What NRIs Should Know

The maths is straightforward but the fine print matters. FCNR deposits are denominated in foreign currency — you deposit dollars, you get dollars back at maturity — so the principal is insulated from rupee depreciation. The interest rate is fixed for the tenure. And because the RBI is covering the hedge, banks can offer rates they normally could not sustain.

The catch: these are three- to five-year lock-ins. Your money is not liquid. And the rates, while attractive relative to US Treasuries, are not wildly above what a high-yield US savings account might offer once you factor in FDIC insurance and instant access. The real appeal is for NRIs who were already planning to park money in India — for a future property purchase, family support, or retirement planning — and now get a materially better return on that intent.

Federal Bank's executive director Harsh Dugar offered a note of caution: "Unlike 2013 where the interest differential between US and India was in the range of 5–6 per cent, compared to 1–2 per cent presently, the relative attractiveness is lower." Translation: this is a good deal, not a once-in-a-generation deal.

## The Bigger Picture

The RBI's move sits inside a broader push to draw diaspora capital home. Last week, the central bank also signalled it is open to banks providing guarantees to offshore lenders who lend to NRIs, who can then place those borrowed funds as FCNR deposits — a leverage play that Jefferies flagged as potentially "key to the extent of mobilisation under this scheme."

India also recently launched a digital trade facilitation portal targeting NRI businesses, expanded UPI to nine countries, and liberalised rules around NRI property investment. The message is consistent: we want your dollars, and we will make it easier to send them.

For the 18 million-strong Indian diaspora, the deposit rate hike is the most tangible of these moves — a direct, measurable improvement in the return on money they were sending home anyway. Whether $40 billion actually materialises depends on how many NRIs trust the lock-in, how the rupee behaves over the next quarter, and whether competing instruments in the US and Gulf keep pace.

The banks are betting big. The RBI is backstopping the bet. And NRIs, for once, are the ones being courted."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
