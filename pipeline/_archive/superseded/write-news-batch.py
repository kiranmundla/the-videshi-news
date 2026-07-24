#!/usr/bin/env python3
"""Write news articles for The Videshi - June 13, 2026 batch"""

import json
import os
import subprocess
import sys
from datetime import datetime

# Load env
def load_env(path):
    env = {}
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    key, val = line.split('=', 1)
                    val = val.strip().strip('"').strip("'")
                    env[key] = val
    except FileNotFoundError:
        pass
    return env

env = load_env('~/.env.supabase')
SUPABASE_URL = env.get('SUPABASE_URL', '')
SUPABASE_KEY = env.get('SUPABASE_SERVICE_ROLE_KEY', '')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing Supabase credentials")
    sys.exit(1)

def insert_article(article):
    """Insert article into Supabase"""
    cmd = [
        'curl', '-sS',
        f'{SUPABASE_URL}/rest/v1/p2_articles',
        '-H', f'apikey: {SUPABASE_KEY}',
        '-H', f'Authorization: Bearer {SUPABASE_KEY}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=representation',
        '-d', json.dumps(article)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        data = json.loads(result.stdout)
        if isinstance(data, list) and data:
            return data[0].get('id'), data[0].get('slug')
        else:
            print(f"  ERROR: {json.dumps(data)[:300]}")
            return None, None
    except json.JSONDecodeError:
        print(f"  ERROR: {result.stdout[:300]}")
        return None, None


# ============================================================
# ARTICLE 1: India as VivaTech 2026 Official AI Partner Country
# ============================================================
article1 = {
    "headline": "India Will Be VivaTech's Official AI Partner Country. No Non-European Nation Has Held That Title Before.",
    "subheadline": "The designation arrives during the India-France Year of Innovation, with India's largest-ever tech delegation heading to Paris next week",
    "slug": "india-vivatech-2026-official-ai-partner-country-paris-showcase",
    "category": "news",
    "vertical": "technology",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Group_Photo_-_VivaTech_Paris_2024.jpg/1280px-Group_Photo_-_VivaTech_Paris_2024.jpg",
    "image_caption": "Delegates gather at VivaTech in Paris, where India will serve as the Official AI Partner Country in 2026",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps(["TechRepublic", "IBEF", "The Mainstream", "Careers360"]),
    "diaspora_angle": "India's AI Partner Country status creates new career and investment corridors for NRIs in technology between Silicon Valley and Indian tech hubs.",
    "published_at": "2026-06-13T08:30:00Z",
    "body": """India will take its biggest-ever technology delegation to Europe next week, arriving in Paris not as a spectator but as VivaTech 2026's Official AI Partner Country — the first time a non-European nation has held the designation at the continent's largest startup and technology event.

The four-day gathering, which runs from June 17 to 20 at Paris Expo Porte de Versailles, will feature India's largest-ever national pavilion at an overseas tech summit. Led by the India Trade Promotion Organisation (ITPO), the showcase brings together government officials, unicorn founders, high-growth startups and technology enterprises operating across AI, aerospace, defence tech, space tech, health tech, deep tech, SaaS, climate tech, mobility, robotics and cybersecurity.

The timing is no accident. The designation arrives during the India-France Year of Innovation 2026 and just days after Prime Minister Narendra Modi and French President Emmanuel Macron jointly inaugurate Bharat Innovates 2026 in Nice on June 14 — a parallel event featuring 120 Indian deep-tech startups selected from over 3,000 applicants. Commerce Minister Piyush Goyal is expected to anchor India's presence at VivaTech alongside senior officials from the Department for Promotion of Industry and Internal Trade (DPIIT), the Ministry of Electronics and Information Technology (MeitY) and the Ministry of Education.

India's pavilion will operate under the theme "Tech for Humanity," a phrase that has become the Modi government's preferred framing for its digital public infrastructure — Aadhaar, UPI and the India Stack — which has drawn interest from dozens of countries trying to replicate the model. The framing is designed to position India as the counterpoint to Silicon Valley's consumer AI race: a country building AI for scale, inclusion and governance rather than chatbots and content generation.

The numbers support the pitch. India's AI market is projected to reach $17 billion by 2027, up from $4 billion in 2023. The country trains roughly 2.5 million STEM graduates annually and is home to over 3,000 AI startups. Sarvam AI, one of the startups expected at VivaTech, is building India's first large language models optimised for Indian languages — a project that directly addresses the gap between English-centric frontier models and the 1.4 billion people who speak 22 officially recognised languages.

For NRIs working in technology, the designation is worth watching closely. India's growing role in global AI governance — it co-chairs the Global Partnership on AI and played a central role in shaping the G20 AI principles in 2023 — is creating new career pathways and investment corridors between Silicon Valley and Bengaluru, between London's fintech ecosystem and Hyderabad's AI labs.

The VivaTech honour also lands at a moment of tension. While India pitches sovereign AI capabilities, its IT services sector is simultaneously reckoning with the disruptive impact of the same technology. TCS last week partnered with Anthropic to give 50,000 workers access to Claude. Infosys cut a similar deal months earlier. Both companies have seen headcount fall as automation reshapes the labour-intensive outsourcing model that built India's technology reputation in the first place.

There is also the question of whether India can convert showcase diplomacy into lasting deals. Bharat Innovates 2026 is expected to produce around 28 innovation-focused memoranda of understanding with French and international partners. But similar summits in the past have produced agreements that struggled to translate into actual commercial partnerships.

Still, the AI Partner Country designation is the strongest signal yet that Europe sees India not merely as a market for its own technology, but as a builder of it. Germany holds VivaTech's Country of the Year title this time; India holds the AI designation. The distinction matters. It says India's technology story has moved beyond outsourcing, and the world's major economies are starting to take notice."""
}

# ============================================================
# ARTICLE 2: Zepto IPO - $837 Million
# ============================================================
article2 = {
    "headline": "Zepto Just Filed to Raise $837 Million. Its Founders Will Not Sell a Single Share.",
    "subheadline": "The quick commerce startup's IPO filing reveals a company that doubled revenue to ₹22,624 crore but lost ₹5,905 crore in the process",
    "slug": "zepto-ipo-837-million-quick-commerce-founders-hold-palicha-vohra-20260613",
    "category": "news",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/11091214/pexels-photo-11091214.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A delivery rider navigates city streets, the kind of last-mile logistics that powers India's quick commerce boom",
    "image_attribution": "Pexels",
    "sources": json.dumps(["Reuters", "Storyboard18", "The Hindu BusinessLine", "Outlook Business"]),
    "diaspora_angle": "Zepto's IPO is a test case for NRI investors watching India's consumer tech sector, with Silicon Valley-trained founders betting on a model that has no Western parallel at this scale.",
    "published_at": "2026-06-13T08:45:00Z",
    "body": """Zepto, the quick commerce company that promises to deliver groceries in ten minutes, has updated its draft prospectus to raise up to $837 million in what is shaping up to be one of India's most closely watched initial public offerings this year.

The filing, submitted to the Securities and Exchange Board of India earlier this week, reveals a company operating at breakneck speed in both directions. Revenue from operations more than doubled to ₹22,624 crore in the financial year ended March 2026, up from ₹11,110 crore the previous year. Losses also widened, reaching ₹5,905 crore from ₹4,700 crore, as the company poured money into expanding its network of dark stores — compact warehouses tucked inside densely populated neighbourhoods — across 66 Indian cities.

The most striking detail in the filing is what the founders chose not to do. Co-founders Aadit Palicha and Kaivalya Vohra, both Stanford dropouts who launched Zepto in 2021 when they were still teenagers, will not sell a single share in the IPO. Their promoter entities — the Lazarus Trust and the Vohra Trust — are sitting out the offer for sale entirely, a move that stands in sharp contrast to several recent Indian startup IPOs where founders cashed out alongside institutional investors.

The selling will instead come from early backers. Nexus Venture Partners is expected to be the largest seller, offloading more than 8.77 crore shares. Other investors trimming their holdings include Contrary Capital, Razor Ventures and Kaiser Foundation Hospitals. The fresh issue component is set at ₹8,010 crore, with proceeds earmarked for dark store expansion, technology and cloud infrastructure, marketing and strategic acquisitions.

Zepto currently operates 1,139 dark stores and serves nearly 4.8 crore annual transacting users, processing more than 23 lakh orders every day. The numbers place it firmly as India's second-largest quick commerce player, behind Eternal's Blinkit but ahead of Swiggy's Instamart. Blinkit has turned profitable at the contribution level; Zepto has not. That gap is the central question the IPO will have to answer.

The company is also transitioning to a marketplace model, where third-party sellers list products on the platform and Zepto earns commissions, advertising revenue and service fees rather than holding all the inventory itself. The shift mirrors the evolution of larger e-commerce platforms like Amazon and Flipkart, but Zepto acknowledged in its filing that it has "limited operating history" under this structure. The marketplace pivot could improve margins but introduces execution risk at a critical moment.

Quick commerce itself has become one of the most fiercely competitive sectors in Indian retail. Blinkit, Instamart and Zepto are all expanding into new categories — electronics, beauty, personal care — while incumbents like Amazon, Flipkart and BigBasket are launching their own rapid delivery services. The sector is betting on India's growing urban consumer base, but the unit economics of delivering a ₹200 order in ten minutes remain challenging.

For NRI investors, Zepto's IPO is a bellwether for India's consumer technology sector. The company was last valued at $7 billion in an October funding round, and is reportedly targeting a July listing. Axis Capital, Morgan Stanley, Goldman Sachs, Motilal Oswal, HSBC, JM Financial and IIFL Capital are managing the offering.

The story is familiar in its broad strokes — a venture-backed startup burning cash to capture market share — but the details are distinctly Indian. Quick commerce has no real Western parallel at this scale. Americans wait two hours for Instacart; Indians wait ten minutes for Zepto. Whether that model can sustain itself as a public company is the billion-dollar question the markets will answer in July."""
}

# ============================================================
# ARTICLE 3: NSE IPO Filing
# ============================================================
article3 = {
    "headline": "India's National Stock Exchange Is About to File Its Own IPO. The Valuation Could Hit ₹6 Trillion.",
    "subheadline": "After a decade of delays, colocation scandals and regulatory hurdles, the NSE is targeting a June 15 filing that would make it one of India's largest-ever listings",
    "slug": "nse-ipo-drhp-filing-june-2026-valuation-6-trillion-colocation-20260613",
    "category": "news",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/IT7A2275_copy_%28cropped%29.jpg/3840px-IT7A2275_copy_%28cropped%29.jpg",
    "image_caption": "The National Stock Exchange of India building in Mumbai, home to the world's largest derivatives exchange",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps(["Angel One", "Livemint", "Outlook Business", "Business Standard"]),
    "diaspora_angle": "An NSE listing would give NRI investors direct exposure to India's capital markets infrastructure for the first time, and could reshape how diaspora money flows into Indian equities.",
    "published_at": "2026-06-13T09:00:00Z",
    "body": """The National Stock Exchange of India has asked its investment bankers to expedite the filing of its draft red herring prospectus, with June 15 set as the target date for a submission that would finally set in motion one of the most anticipated listings in Indian financial history.

NSE is not just any company going public. It is the exchange where most of India's equity trading happens — the platform that handles over 90 per cent of the country's derivatives volume and serves as the backbone of the Indian capital markets. When it lists, the institution that runs the market will itself become a product traded on it.

The IPO has been nearly a decade in the making. NSE first considered going public in the mid-2010s, but the process was derailed by the colocation scandal — allegations that certain brokers were given preferential access to the exchange's trading servers, allowing them to place orders microseconds ahead of others. A high-powered advisory committee set up by SEBI recommended settlements exceeding ₹1,800 crore in connection with the colocation and dark fibre cases. Those settlements are now being finalised as part of the pre-listing cleanup.

The exchange's board approved the IPO on February 6, 2026, after receiving a no-objection certificate from SEBI. An extraordinary general meeting was held on May 25 to amend the articles of association in preparation for listing. The mid-June deadline for the DRHP filing was chosen deliberately to allow the document to be anchored to NSE's March 2026 quarterly financials, which were released earlier this month.

The proposed offering will be entirely through an offer for sale — no fresh capital will be raised. Existing shareholders, including Temasek, Canada Pension Plan Investment Board, Life Insurance Corporation of India and ChrysCapital, are expected to dilute up to 5 per cent of their holdings, depending on market appetite. Estimates for the IPO valuation range from ₹4 trillion to ₹6 trillion, which would make it one of the largest offerings in Indian stock market history.

Recent transactions in the grey market have implied valuations of around ₹4.5 trillion to ₹5 trillion. At the upper end of the range, NSE would be valued at roughly $63 billion — placing it among the most valuable exchange operators in the world, alongside the London Stock Exchange Group and Intercontinental Exchange.

The listing is significant beyond its size. NSE's financials are a direct proxy for the health of India's capital markets. When more Indians trade, NSE earns more. When foreign institutional investors pour money into Indian equities, NSE's transaction fees rise. The exchange also earns revenue from data licensing, index products (it owns the Nifty 50) and technology services.

For NRIs, an NSE listing would offer something that has never existed before: a direct way to invest in India's capital markets infrastructure itself, rather than in individual stocks or funds that trade on it. It is, in effect, a bet on the long-term growth of Indian equity participation — a metric that has been climbing steadily as demat account openings surged past 16 crore.

The timing carries its own risks. Indian markets have been under pressure in 2026, with the Sensex and Nifty down 11-13 per cent year-to-date amid the Iran war's impact on oil prices, foreign investor outflows exceeding $30 billion, and a weakening rupee. BlackRock said this week that India has been "over-punished" and remains a high-conviction long-term trade, but the near-term headwinds are real.

Once the DRHP is filed, SEBI typically takes two to three months to issue final observations, putting the listing itself on track for the second half of 2026. Twenty investment banks are involved in managing the offering — an unusually large syndicate that reflects both the complexity and the prestige of bringing India's primary exchange to market.

The exchange confirmed the broad direction without elaborating. "Pursuant to the NOC issued by SEBI, the board approved an IPO of the company through an offer for sale on February 6, 2026," it said. "No further comments at this stage."

After a decade of false starts, the exchange that built modern Indian trading is about to trade itself."""
}


# Insert all articles
articles = [
    ("Article 1 (VivaTech)", article1),
    ("Article 2 (Zepto IPO)", article2),
    ("Article 3 (NSE IPO)", article3),
]

for label, article in articles:
    print(f"\nInserting {label}...")
    aid, slug = insert_article(article)
    if aid:
        print(f"  ✓ Inserted: id={aid}, slug={slug}")
    else:
        print(f"  ✗ Failed")

print("\nDone.")
