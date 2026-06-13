#!/usr/bin/env python3
"""Insert 3 news articles into Supabase for The Videshi."""
import json
import os
import sys
import datetime
import requests

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            key = key.replace("export ", "").strip()
            val = val.strip().strip('"').strip("'")
            os.environ[key] = val

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ─── ARTICLE 1: Trump Iran Peace Deal ───
articles.append({
    "headline": "Trump Says Iran Deal Will Be Signed Sunday. The Strait of Hormuz Will Reopen 'Immediately.'",
    "subheadline": "The announcement sent crude prices tumbling to a two-month low and triggered India's best market day in two months. But Tehran says it has not yet finalised a signing date.",
    "slug": "trump-iran-peace-deal-sunday-hormuz-strait-reopen-crude-oil-india-impact-20260613",
    "category": "news",
    "vertical": "geopolitics",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/Flickr_-_Official_U.S._Navy_Imagery_-_U.S._Navy_ships_transit_the_Strait_of_Hormuz..jpg/1280px-Flickr_-_Official_U.S._Navy_Imagery_-_U.S._Navy_ships_transit_the_Strait_of_Hormuz..jpg",
    "image_caption": "U.S. Navy ships transit the Strait of Hormuz, the critical oil shipping lane at the centre of the conflict",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "A reopened Hormuz would ease global crude prices, directly lowering fuel and grocery costs for NRIs, while reducing the risk to Indian seafarers who have been caught in the crossfire.",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "sources": json.dumps(["Reuters", "USA Today", "The Times", "Bloomberg", "NY Post", "Barron's"]),
    "body": """The war that began with American and Israeli strikes on Iran on February 28 may be entering its final chapter. President Donald Trump declared on Saturday that a peace deal with Tehran is "scheduled to get signed tomorrow," and that the Strait of Hormuz — the narrow waterway through which a fifth of the world's oil passes — would reopen to all traffic "immediately" after the signing.

"Our relationship with Iran is a much different and better one than previous Administrations have had," Trump wrote on Truth Social, contrasting the emerging agreement with the Obama-era nuclear deal. "Unlike Obama's Hundreds of Billions of Dollars in payments to them, including 1.7 Billion Dollars in green, cold cash, no money will exchange hands."

The announcement capped a week of accelerating diplomacy. Pakistani Prime Minister Shehbaz Sharif, who has served as the principal mediator between Washington and Tehran, said on Saturday that the framework for a memorandum of understanding had been agreed and that Islamabad was "preparing for the electronic signing." Vice President JD Vance and special envoy Steve Witkoff are expected to represent Trump at the ceremony, which may take place in Geneva — conveniently close to the G7 summit in nearby Evian-les-Bains.

## Tehran Is Not Ready to Celebrate

Iran, however, has been more cautious. Foreign Ministry spokesperson Esmaeil Baghaei told state media that the signing "will not be tomorrow," though he did not rule out it happening "in the coming days." The Islamic Revolutionary Guard Corps went further, saying the agreement had "not yet been finalised."

The gap between Trump's certainty and Tehran's hedging has become a familiar pattern in these negotiations. The two sides have appeared close to a deal multiple times since a ceasefire took hold in April, only for timelines to slip.

The sticking points remain significant. Iran wants Washington to lift its naval blockade and unfreeze roughly $24 billion in sanctioned assets. The United States wants Iran to verifiably abandon its nuclear weapons programme. Trump said on Saturday that Tehran "no longer" wants a nuclear weapon and signalled that American forces would eventually "go in and get the Nuclear Dust, buried deep under the powerful sunken granite mountains."

Iranian Foreign Minister Seyed Abbas Araghchi has framed the negotiations differently, declaring Iran the "true winner" of the war and insisting that any deal must include Tehran retaining control over the Strait of Hormuz — which it sees as sovereign territory, not a concession to be granted.

## What It Means for India

For India, few geopolitical developments carry more immediate economic consequence. The Iran war has driven Brent crude above $100 per barrel for most of the past three months, pushing India's oil import bill up 53 per cent in April alone. State-owned fuel retailers raised petrol and diesel prices four times in May. The Reserve Bank of India has revised its inflation forecast for the current fiscal year upward to 5.1 per cent, and the government is preparing to let its fiscal deficit widen to 4.8 per cent of GDP — half a percentage point above the February target.

Markets responded to the peace signals with unmistakable relief. On Friday, the BSE Sensex surged 1,695 points — its best session in two months — while the Nifty 50 jumped nearly 2 per cent to close at 23,622. Brent crude fell 4 per cent to $87 a barrel, a near two-month low. Analysts said sustained lower oil prices could reverse some of the record $30 billion in foreign equity outflows India has seen this year.

The human cost has been just as stark. Three Indian seafarers have been killed in U.S. strikes on tankers transiting the Gulf in the past week alone, and opposition parties have demanded that Prime Minister Modi raise the issue directly with Trump at their bilateral meeting on the sidelines of the G7 summit on Wednesday.

## The Week Ahead

If a deal is signed, the immediate test will be whether the Strait of Hormuz actually reopens and oil begins flowing at pre-war volumes. Analysts at Barclays wrote on Friday that a confirmed agreement "would remove a major macro tail risk" and benefit emerging markets and cyclical sectors most.

But the deal is framed as a memorandum of understanding — an interim framework, not a final peace. Under its reported terms, American and Iranian officials would have 60 days to work out the logistics of dismantling Iran's nuclear capabilities. The harder negotiations, in other words, have not yet begun.

Trump, as is his custom, left the threat of force on the table. "Hopefully, this process will all work out quickly, easily, and smoothly," he wrote. "If it doesn't, we have the ultimate alternative, hopefully never to be used again."

Sources: Reuters, USA Today, The Times, Bloomberg, NY Post, Barron's"""
})

# ─── ARTICLE 2: Bharat Innovates 2026 ───
articles.append({
    "headline": "Modi and Macron Will Inaugurate India's Largest Deep-Tech Showcase in Nice Tomorrow. 120 Startups Made the Cut.",
    "subheadline": "Bharat Innovates 2026 brings Indian founders in semiconductors, space, biotech and quantum computing to the French Riviera. Twenty-eight MoUs with French and international partners are expected.",
    "slug": "bharat-innovates-2026-nice-france-modi-macron-120-startups-deep-tech-20260613",
    "category": "news",
    "vertical": "tech",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Prime_Minister_of_Bharat_Shri_Narendra_Damodardas_Modi_with_President_of_France_Mr._Emmanuel_Macron.jpg/1280px-Prime_Minister_of_Bharat_Shri_Narendra_Damodardas_Modi_with_President_of_France_Mr._Emmanuel_Macron.jpg",
    "image_caption": "Prime Minister Narendra Modi with French President Emmanuel Macron at an earlier bilateral meeting",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "Indian-origin founders and researchers in Europe and the US now have a direct government-backed platform to connect with French capital and research labs — this is the India-France innovation corridor coming alive.",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "sources": json.dumps(["Ministry of Education (India)", "Careers360", "YourStory", "Devdiscourse", "Impressive Times"]),
    "body": """Prime Minister Narendra Modi and French President Emmanuel Macron will jointly inaugurate Bharat Innovates 2026 in Nice on Saturday — the first time an Indian government initiative has commandeered one of France's largest exhibition halls to pitch Indian deep-tech startups directly to global capital.

The three-day event at the Palais des Expositions de Nice, running from June 14 to 16, will feature 120 Indian startups selected from over 3,000 applicants, around 15 higher education institutions including IITs, IISc and BITS Pilani, and more than 500 investors — a mix of venture capital firms, sovereign wealth funds and global corporate leaders.

"The maiden edition of Bharat Innovates 2026 will showcase India's deep tech innovators and start-ups to global investors and industry in Nice," the Ministry of Education said on Friday. External Affairs Minister S. Jaishankar and Commerce Minister Piyush Goyal will accompany Modi.

## Not a Pitch Day. A Platform.

The event is more than a showcase. It is designed as an operational bridge between Indian research labs and European markets, built around two mechanisms: the Incubator Innovation Bridge and the Industry Innovation Bridge. Both are structured to connect Indian founders with multinational corporations, universities and startup ecosystems abroad.

Around 28 innovation-focused Memorandums of Understanding are expected to be signed with French and international partners — covering everything from semiconductor R&D to climate tech collaboration.

The startups in the compendium have collectively raised over $1.5 billion, hold more than 1,500 patents, and include two publicly listed companies: ideaForge and Ather Energy. The sectors they represent — advanced computing, semiconductors, space technology, biotechnology, quantum computing, energy, healthcare and manufacturing — read like a blueprint for the kind of industrial base India has been trying to build since the Make in India push began a decade ago.

## The France Connection

The event is part of the India-France Year of Innovation, launched in February 2026 when the bilateral partnership was elevated to a "Special Strategic Partnership." France is not India's largest trade partner, but it has become one of its most important technology collaborators — in defence, nuclear energy, space and, increasingly, artificial intelligence.

Principal Scientific Adviser Prof. Ajay Kumar Sood, who chaired the committee that selected the 120 startups, stressed the need for "a stronger culture of research-led innovation to accelerate the growth of globally competitive deep-tech enterprises." The implicit argument: India can no longer rely solely on IT services and software outsourcing. The next wave has to come from hardware, biology and materials science.

## Why the Diaspora Should Watch

For Indian-origin engineers, researchers and investors based in Europe and the United States, Bharat Innovates is a signal that New Delhi is serious about building institutional pipelines — not just bilateral meetings — between Indian innovation and global capital. The event structure includes one-to-one investor meetings, not just panel discussions, and the compendium itself is designed as a deal-ready document with sector-specific market insights and technology benchmarks.

A parallel healthcare roundtable, organised by YourStory, brought together six biotech founders working on cancer therapy, surgical AI, genomics, a blood test for Parkinson's and pesticide-free crop protection. The through-line was consistent: India is shifting from importing medical technology to building it.

Modi's visit to Nice is the first stop on a six-day European tour that includes meetings in Paris, the G7 summit in Evian-les-Bains and a historic first-ever visit by an Indian prime minister to Slovakia. Trade, AI cooperation and the Iran war are all on the agenda — but the Nice event is the one where India's startup ecosystem gets to make its case directly to the people who write the cheques.

Sources: Ministry of Education (India), Careers360, YourStory, Devdiscourse, Impressive Times"""
})

# ─── ARTICLE 3: India CPI Inflation ───
articles.append({
    "headline": "India's Inflation Just Hit Its Highest Level of 2026. Food and Fuel Are Doing the Damage.",
    "subheadline": "Retail prices rose 3.93 per cent in May — still below the RBI's 4 per cent target, but accelerating fast. The central bank has already revised its full-year forecast to 5.1 per cent.",
    "slug": "india-cpi-inflation-may-2026-highest-food-fuel-rbi-forecast-20260613",
    "category": "news",
    "vertical": "economy",
    "image_url": "https://images.pexels.com/photos/28672822/pexels-photo-28672822.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Fresh produce at a street market in Delhi, where vegetable prices have climbed sharply in recent months",
    "image_attribution": "Pexels",
    "diaspora_angle": "Rising food and fuel inflation will hit remittance-dependent families hardest — the rupees NRIs send home are buying less each month, and a weak monsoon could make it worse.",
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "sources": json.dumps(["Ministry of Statistics (India)", "Reuters", "Mint", "The Hindu BusinessLine", "Capital Market"]),
    "body": """India's retail inflation rose to 3.93 per cent in May, the highest reading since the government reset its Consumer Price Index in January, as higher food and fuel costs worked their way through an economy still absorbing the shock of the Iran war.

The figure, released by the Ministry of Statistics on Friday, is the second consecutive monthly increase — up from 3.48 per cent in April and 3.4 per cent in March. It came in marginally below the median estimate of 4.1 per cent in a Mint poll of 16 economists, but the direction of travel has the Reserve Bank of India worried enough to revise its full-year inflation forecast upward to 5.1 per cent from 4.6 per cent.

## Food Is the Story

Food inflation accelerated to 4.78 per cent in May from 4.2 per cent in April, driven by a set of items that will be painfully familiar to anyone who has visited an Indian vegetable market this year. Tomato prices surged 48.4 per cent year-on-year. Ginger was up 32.5 per cent. Silver and gold jewellery saw the steepest price jumps of any category — 155 per cent and 41 per cent respectively — reflecting both global precious metal trends and domestic hoarding behaviour.

Rural India is feeling the squeeze more than urban centres. Rural inflation hit 4.25 per cent against 3.53 per cent in cities, a gap that reflects rural households' higher exposure to food prices and the fact that fuel price hikes hit transport-dependent agricultural supply chains first.

Not everything is going up. Potato prices are down nearly 24 per cent. Peas fell 11.5 per cent. Motor vehicles are cheaper than a year ago. But these pockets of deflation are not enough to offset the structural pressures building in the system.

## Fuel Lit the Fuse

Transport inflation jumped to 1.75 per cent in May from a 0.01 per cent decline in April — a sharp reversal that directly reflects the four fuel price hikes state-owned retailers imposed during the month. Petrol and diesel inflation rose to 6 per cent, up from 0.5 per cent as recently as March.

The pass-through from global oil prices to Indian pump prices has been unusually fast this year. With Brent crude trading above $100 for most of the past three months — before Friday's retreat to $87 on Iran peace hopes — the government has been unable to continue absorbing the cost through subsidies without blowing out the fiscal deficit.

Core inflation, which strips out food and fuel, has been quietly firming for three straight months, reaching 3.73 per cent in May. This is the number the RBI watches most closely, because it reflects underlying demand-side pressures rather than supply shocks. Three months of acceleration narrows the room for the rate cuts that markets had been hoping for.

## What Happens Next

The RBI projected quarterly inflation at 4.2 per cent in Q1, 5.1 per cent in Q2, 5.9 per cent in Q3 and 5.4 per cent in Q4 — a trajectory that would take headline inflation well above the 4 per cent target by the monsoon months. Interest rate swap markets are pricing in at least 25 basis points of rate hikes over the next three months.

Two wild cards could push prices higher still. First, the India Meteorological Department's forecast of a below-normal monsoon under El Niño conditions threatens kharif sowing and could keep food prices elevated well into the autumn. Second, if the Iran peace deal that Trump announced on Saturday collapses, crude prices could spike back above $100, restarting the fuel-price pass-through cycle.

For remittance-dependent households — and there are tens of millions of them — the arithmetic is unforgiving. The rupee has weakened to 95 against the dollar this year, which means more rupees per dollar sent home. But if those rupees buy less at the vegetable market, the gain is illusory.

Bank of Baroda economist Madan Sabnavis offered practical advice to farmers: wait for the rains before sowing. For policymakers, the advice is more fraught. Cushion the fuel-price pass-through, manage buffer stocks and hope that the monsoon cooperates. The margin for error, for the first time in two years, is shrinking.

Sources: Ministry of Statistics (India), Reuters, Mint, The Hindu BusinessLine, Capital Market"""
})

# Insert each article
for i, article in enumerate(articles, 1):
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=headers,
        json=article,
        timeout=30,
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        if isinstance(data, list) and data:
            print(f"Article {i} ✓ id={data[0].get('id','?')} slug={data[0].get('slug','?')}")
        else:
            print(f"Article {i} ✓ response: {str(data)[:200]}")
    else:
        print(f"Article {i} ✗ HTTP {resp.status_code}: {resp.text[:300]}")

print("\nDone.")
