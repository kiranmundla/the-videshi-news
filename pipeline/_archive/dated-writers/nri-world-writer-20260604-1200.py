#!/usr/bin/env python3
"""NRI World Writer — 2026-06-04 12:00 UTC run"""

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
    # ─── Article 1: India Leads US Unicorn Founders ───
    {
        "id": str(uuid.uuid4()),
        "headline": "India Now Leads the World in US Unicorn Founders. The Number Is 96 and Climbing.",
        "subheadline": "A fresh count puts Indian-born entrepreneurs atop the global leaderboard for billion-dollar US startups, with IIT alumni forming the backbone of a pipeline that shows no sign of slowing.",
        "slug": make_slug("india-leads-us-unicorn-founders-96-iit-pipeline"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian immigrants and their children now dominate US startup creation at the highest tier — a direct consequence of decades of IIT-to-Silicon-Valley migration and a growing willingness among NRI founders to bet on American markets rather than return home.",
        "tags": ["nri", "diaspora", "startups", "silicon-valley", "unicorn", "iit", "entrepreneurs"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "GKToday", "url": "https://gktoday.in/topic/india-leads-in-us-unicorn-founders/"},
            {"name": "Stanford University Venture Capital Initiative", "url": "https://www.gsb.stanford.edu/faculty-research/centers-initiatives/venture-capital-initiative"},
            {"name": "Global Finance Magazine", "url": "https://www.gfmag.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7580644/pexels-photo-7580644.jpeg",
        "image_caption": "Business professionals in discussion at a modern office",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """India is now the single largest source country for immigrant founders of billion-dollar startups in the United States. As of June 3, 2026, Indian-born entrepreneurs have founded or co-founded 96 privately held US companies valued at a billion dollars or more — placing India firmly ahead of every other nation in what has become the most closely watched metric of global entrepreneurial talent.

The numbers come from updated tracking by the Stanford University Venture Capital Initiative and corroborating data compiled by multiple research outlets. Across the broader landscape, immigrants have founded or co-founded 455 of 775 US unicorns, accounting for 59 per cent of the total. Indian-origin founders represent roughly one-fifth of that immigrant cohort — a share that has grown steadily over the past decade and shows no sign of levelling off.

## The IIT pipeline holds

The institutional backbone of this dominance remains the Indian Institutes of Technology. IIT Delhi has produced 16 unicorn founders and IIT Bombay another 14, according to a June 2025 report linked to the Stanford initiative. The numbers are striking not just in absolute terms but in conversion rate: startups founded by Indian entrepreneurs who relocate to the United States are 6.5 times more likely to reach unicorn status than the average US startup, according to research by Stanford professor Ilya Strebulaev.

That multiplier reflects a combination of factors. IIT graduates enter the US with strong quantitative training, deep peer networks that span venture capital and Big Tech, and a cultural willingness to take concentrated bets. Many spend years at Google, Microsoft, or Amazon before striking out on their own — a pattern that gives them both domain expertise and access to capital.

## Where the founders cluster

The sectors where Indian-origin founders dominate read like a map of the modern economy. Fintech, software-as-a-service, and developer infrastructure have been the traditional sweet spots. But the latest cohort is branching into AI infrastructure, healthcare technology, and climate-adjacent enterprise tools — sectors where deep technical fluency matters more than consumer branding.

Notable Indian-origin unicorn founders include Laks Srini of TriNet Zenefits and Jyoti Bansal of AppDynamics, but the newer names are less likely to be household-familiar. They run companies that sell to other companies, often with a modest public profile and a very immodest valuation.

## What it means for the diaspora

For the roughly five million Indian Americans in the United States, the unicorn numbers are both a source of pride and a data point in a longer argument. Indian Americans have the highest median household income of any ethnic group in the country, and the startup pipeline reinforces a narrative of disproportionate economic contribution that community organisations like Indiaspora and GOPIO regularly cite in policy discussions.

The numbers also carry weight in immigration debates. When 59 per cent of America's most valuable startups have at least one immigrant founder, the case for skilled immigration becomes harder to dismiss — and Indian-origin entrepreneurs are the single largest piece of that evidence.

But there is a less celebratory dimension. The same pipeline that produces unicorn founders in San Francisco also represents a brain drain from India. Every IIT graduate who builds a billion-dollar company in Delaware rather than Bengaluru is a reminder that India's own startup ecosystem, despite its growth, still cannot match the capital availability, regulatory predictability, and market depth of the United States.

## The road ahead

India's lead is unlikely to narrow soon. The IIT system continues to produce roughly 16,000 graduates a year, many of whom enter US graduate programmes before joining the startup ecosystem. The H-1B visa pipeline, despite periodic political turbulence, remains the primary gateway. And the cultural infrastructure — founder networks, angel syndicates, IIT alumni associations in every major US tech hub — only compounds the advantage.

The question is whether India can build a parallel pathway that keeps more of that talent at home. Until it does, the unicorn leaderboard will keep telling the same story: the most successful Indian entrepreneurs are building American companies."""
    },

    # ─── Article 2: GIFT City NRI Investment Surge ───
    {
        "id": str(uuid.uuid4()),
        "headline": "NRI Investors Are Flooding Into GIFT City. The Numbers Just Tripled in Three Months.",
        "subheadline": "Retail participation in Gujarat's international financial hub nearly tripled in Q4 FY26, as new mutual fund schemes and lower minimums finally make India's offshore platform accessible to ordinary diaspora investors.",
        "slug": make_slug("gift-city-nri-retail-investors-triple-q4-fy26"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "GIFT City was built to capture NRI money that currently sits in foreign bank accounts and global equity markets. The tripling of retail participation signals that the diaspora is finally treating it as a serious alternative to investing through US or UK brokerages.",
        "tags": ["nri", "diaspora", "investment", "gift-city", "mutual-funds", "ifsca", "finance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Money", "url": "https://outlookmoney.com/invest/retail-participation-in-gift-city-funds-nearly-triples-in-q4-fy26-as-new-schemes-nri-interest-gain-traction"},
            {"name": "IFSCA Quarterly Bulletin", "url": "https://ifsca.gov.in/"},
            {"name": "Belong (GIFT City Platform)", "url": "https://getbelong.com/blog/top-gift-city-funds-for-nris"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/GIFT_City%2C_Gandhinagar%2C_India_Sep_27%2C_2025_07-28-42_AM_from_IndiGo_flight.jpeg/1280px-GIFT_City%2C_Gandhinagar%2C_India_Sep_27%2C_2025_07-28-42_AM_from_IndiGo_flight.jpeg",
        "image_caption": "Aerial view of GIFT City in Gandhinagar, Gujarat",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Something is shifting in Gujarat's skyline of glass towers, and it is not just the architecture. The International Financial Services Centres Authority has released its latest quarterly bulletin, and the headline number is hard to ignore: retail participation in GIFT City-based fund schemes jumped 177.5 per cent in the January-March quarter of FY26, from 1,239 investors in December 2025 to 3,438 by March 2026.

Stretch the lens back six months and the growth is even more dramatic. In September 2025, these same retail schemes had just 255 investors. By March, that figure had surged roughly 1,250 per cent. More than three-fourths of all new investors entering GIFT City's fund ecosystem in Q4 FY26 came from the retail segment — a category that, until recently, was little more than a rounding error in a market dominated by institutional money and alternative investment funds.

## What changed

The answer is partly product, partly access. Between June 2025 and February 2026, four asset management companies launched retail mutual fund schemes at GIFT City that NRIs can access for as little as 500 dollars. The Sundaram India Mid Cap GIFT Fund and the Edelweiss Greater China Fund were among the new offerings. A Tata India Dynamic Equity Fund and a DSP Global Equity Fund, already established, continued to pull in participants.

For diaspora investors accustomed to the friction of investing in India — the NRE and NRO account maze, the FEMA compliance headaches, the rupee conversion risk — GIFT City offers a genuinely different proposition. The entire zone operates in foreign currency. Investments are denominated in dollars, not rupees. And the regulatory framework, overseen by IFSCA rather than SEBI, is designed to feel closer to a Singapore or Dubai fund structure than a domestic Indian one.

## The broader picture

The total investor base across all GIFT City fund schemes rose to 9,594 in March 2026, up from 6,721 in December 2025. Commitments have crossed 26.3 billion dollars, with actual investments at 13.2 billion dollars. Nineteen fund management entities have relocated schemes from foreign jurisdictions to GIFT City, bringing 9.14 billion dollars in commitments with them.

The NRI share of individual investors stands at 57 per cent, followed by Indian residents at 37 per cent. The composition tells a clear story: GIFT City is primarily an NRI product, and its growth depends on whether the diaspora finds its offerings competitive with what they can already buy through Vanguard, Fidelity, or Interactive Brokers.

## Why NRIs are paying attention

The appeal is partly tax-driven. GIFT City funds benefit from a favourable tax regime — no securities transaction tax, no commodity transaction tax, and certain capital gains exemptions that do not apply to domestic Indian investments. For an NRI in the United States, the calculus involves comparing these advantages against FATCA reporting obligations and the IRS treatment of foreign mutual funds as Passive Foreign Investment Companies, which can trigger punitive tax rates.

The more compelling draw may be simpler: access to Indian markets without the rupee risk. An NRI who wants exposure to Indian mid-cap stocks but does not want to convert dollars to rupees, open an NRE account, and navigate SEBI regulations can now buy a GIFT City fund denominated in dollars. The entry point is low, the structure is familiar, and the regulator is actively courting the diaspora.

## The sceptic's view

Numbers can flatter. A jump from 255 to 3,438 retail investors sounds explosive, but in absolute terms, it is still a small club. India's domestic mutual fund industry has over 200 million investor accounts. Even compared to the estimated 18 million NRIs worldwide, 3,438 retail investors is barely a whisper.

The question is trajectory. If the next four quarters replicate the growth pattern of Q4 FY26, GIFT City's retail base could cross 50,000 by mid-2027 — still modest by global standards but large enough to attract more asset managers and more competitive products. The virtuous cycle of more funds, lower fees, and greater awareness is precisely what IFSCA is banking on.

For NRIs who have spent years complaining that investing in India is needlessly complex, GIFT City is starting to look like a serious answer. Whether it becomes the default answer depends on what happens in the next twelve months."""
    },

    # ─── Article 3: Chandrayaan-3 Goddard Award ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Chandrayaan-3 Just Won America's Highest Astronautics Honour. The Diaspora Felt It as a Personal Milestone.",
        "subheadline": "ISRO's lunar lander received the AIAA Goddard Astronautics Award in Washington, with Ambassador Kwatra accepting on behalf of a mission that has quietly become the Indian diaspora's favourite proof of concept.",
        "slug": make_slug("chandrayaan-3-goddard-astronautics-award-aiaa-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For Indian Americans working in aerospace, Chandrayaan-3's recognition by the AIAA is not just a national achievement but a personal validation — a signal that the scientific tradition they carry has earned the highest regard of the American institution that defines their professional world.",
        "tags": ["nri", "diaspora", "isro", "chandrayaan", "space", "aiaa", "science", "india-us"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/aiaa-honors-chandrayaan-3-with-goddard-astronautics-award/"},
            {"name": "AIAA", "url": "https://aiaa.org/news/aiaa-announces-2026-premier-award-winners/"},
            {"name": "Blitz India Media", "url": "https://blitzindiamedia.com/chandrayaan-3-wins-prestigious-2026-goddard-award/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/aa/Chandrayaan-3_%E2%80%93_Image_of_Vikram_lander_on_lunar_surface_taken_by_Pragyan_rover_navcam_at_1104_IST%2C_30_August_2023_from_15_meters_away_%28with_text%29.webp",
        "image_caption": "Chandrayaan-3's Vikram lander on the lunar surface, photographed by the Pragyan rover",
        "image_attribution": "Wikimedia Commons / ISRO",
        "is_editorial": False,
        "body": """On May 21, in a conference hall in Washington DC, India's Ambassador to the United States, Vinay Kwatra, walked to a podium and accepted a small plaque on behalf of the Indian Space Research Organisation. The occasion was the AIAA ASCEND 2026 Conference. The award was the Goddard Astronautics Award — the highest honour the American Institute of Aeronautics and Astronautics bestows for achievement in the field of astronautics.

The recipient was Chandrayaan-3, the mission that on August 23, 2023, made India the first nation to land a spacecraft near the Moon's south pole.

The citation was measured, as these things tend to be: "For the groundbreaking landing of ISRO's Chandrayaan-3 near the lunar south pole region, to deepen our understanding of the moon and beyond." But in Indian-American living rooms, WhatsApp groups, and aerospace offices across the country, the reaction was anything but measured.

## What the award means

The Goddard Astronautics Award was established in the 1940s, endowed by Esther Goddard in memory of her husband Robert, the American rocket pioneer whose liquid-fuel experiments in the 1920s laid the groundwork for everything that followed. Previous recipients include teams behind the James Webb Space Telescope and the Mars rovers. It is not given lightly, and it is not given often to non-American entities.

For ISRO to receive it is a statement from the American aerospace establishment that India's space programme has arrived — not as an aspirant, not as a promising developing-world story, but as a peer. The Chandrayaan-3 mission delivered data on the chemical composition of lunar south-polar soil, confirmed the presence of elements that could sustain future manufacturing operations on the Moon, and did all of it on a budget that would not cover the catering bill for a typical NASA mission.

## The diaspora dimension

The roughly 400 AIAA members in India and the four AIAA student branches at Indian universities are a fraction of the story. The more significant population is the thousands of Indian-origin engineers and scientists working in American aerospace — at NASA's Jet Propulsion Laboratory, at Boeing, at Lockheed Martin, at SpaceX, and at the growing constellation of commercial space startups.

For this community, the Goddard Award carries a particular resonance. Many of them grew up watching ISRO launches on Doordarshan, chose careers in aerospace partly because of India's space programme, and now find themselves in positions where they collaborate with ISRO on joint projects. The award validates not just a mission but a tradition — the idea that Indian scientific culture, with its emphasis on frugal engineering and first-principles thinking, can compete at the highest level.

Ambassador Kwatra, in his remarks at the ceremony, outlined Prime Minister Modi's Space Vision 2047, which envisions deep space exploration, human spaceflight, and a dramatically expanded commercial space sector. He called for strengthened collaboration between the governments, industries, and research institutions of India and the United States — a diplomatic ask that carries more weight when delivered alongside AIAA's most prestigious hardware.

## From Chandrayaan to Gaganyaan

The award arrives at a moment when India's space ambitions are accelerating. The Gaganyaan human spaceflight programme is in advanced testing. ISRO's commercial arm, NewSpace India Limited, is processing a growing backlog of satellite launch contracts. And a cohort of Indian space startups — Skyroot Aerospace, Agnikul Cosmos, Pixxel — are attracting venture capital from Silicon Valley funds whose partners are, in many cases, Indian-origin themselves.

The circularity is the point. Indian engineers train at IITs, move to the US, work at NASA or SpaceX, invest in Indian space startups, and watch ISRO win American awards. The loop reinforces itself, and each turn widens it.

## A quiet reckoning

There is something worth noting about the timing. The Goddard Award was announced in December 2025 and presented in May 2026 — nearly three years after the Chandrayaan-3 landing itself. The lag is partly procedural; AIAA awards follow nomination cycles. But it also reflects the time it takes for the significance of a mission to settle.

In August 2023, the landing was a news event — dramatic, briefly viral, quickly displaced by the next cycle. Three years later, the scientific data from Chandrayaan-3 has been cited in dozens of peer-reviewed papers, ISRO has used the mission architecture to plan Chandrayaan-4, and the south-pole landing site has become a reference point in Artemis programme planning. The award recognises not the headline but the harvest.

For Indian Americans who have spent decades explaining where they come from and what their country can do, the Goddard Award is a satisfying data point. ISRO did not just land on the Moon. It landed in a place no one else had reached, collected data no one else had, and did it cheaply enough to make the rest of the world take notes. That is a story the diaspora does not need to embellish."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
