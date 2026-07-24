#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 10:30 UTC batch
Topics: 1) Ebola outbreak — 900+ cases, US bans green card holders (first time ever), India travel advisory, no vaccine
        2) Indian markets surge to 2-week high + Brent crude drops 5.5% + $23.86B foreign outflows + Kevin Warsh new Fed chair → NRI money implications
"""

import json, os, uuid, re, requests, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Supabase config ──
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

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, params, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(slug_base, date_suffix="20260525"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')
now_plus1 = (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Ebola — 900+ Cases, US Bans Green Card Holders (First Time), India Travel Advisory, No Vaccine
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("ebola-bundibugyo-us-green-card-ban-title-42-india-travel-advisory-who")
headline1_prefix = "the us just banned green card holders"
if slug1 not in existing_slugs and not any(headline1_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The US Just Banned Green Card Holders From Entering the Country Over Ebola. It Has Never Done That Before. India Has Told Its Citizens to Stay Away From Three African Nations. There Is No Vaccine.",
        "subheadline": "On Friday, the CDC extended the Ebola travel ban to lawful permanent residents who have been in the Democratic Republic of Congo, Uganda, or South Sudan in the previous 21 days — the first time green card holders have been included in a US health-based entry restriction. The ban was issued under Title 42, the same public health law used during COVID to close the southern border. The WHO has declared the outbreak a Public Health Emergency of International Concern. The strain is Bundibugyo — rare, with a 50 percent fatality rate, and no approved vaccine or treatment exists for it. There are now more than 900 suspected cases in the DRC, including 101 confirmed, with 177 suspected deaths. The virus has spread from rural Ituri province to the cities of Goma and Bunia, and crossed into Uganda, which has five confirmed cases and two deaths. India's Ministry of External Affairs has advised citizens to avoid non-essential travel to all three affected nations. The CDC has set up enhanced screening at Dulles and Atlanta airports. And the FIFA World Cup — the largest mass-gathering event of the year, hosted across the United States, Canada, and Mexico starting June 14 — is three weeks away.",
        "slug": slug1,
        "category": "news",
        "vertical": "health",
        "diaspora_angle": "If you are an Indian American with a green card and you have been in the Democratic Republic of Congo, Uganda, or South Sudan in the past 21 days, you cannot come home. Not to your house. Not to your family. Not to the country where you have lived, worked, and paid taxes, potentially for decades. The CDC issued the order on Friday under Title 42, and it applies to you regardless of how long you have held your green card, regardless of whether you show any symptoms, regardless of whether you were anywhere near the outbreak zone. Green card holders have historically been shielded from US entry restrictions. The CDC's COVID-era Title 42 order did not apply to them. Trump's various travel bans did not apply to them. This is the first time the US government has used a health emergency to bar lawful permanent residents from entering. For the 4.4 million Indian Americans — many of whom hold green cards and some of whom have professional or humanitarian connections to East Africa — the precedent matters as much as the virus itself. If the government can invoke Title 42 to ban green card holders over Ebola, the legal framework now exists to do the same for any future pathogen, in any future country, under any future administration. India's MEA has advised citizens to avoid non-essential travel to the DRC, Uganda, and South Sudan. For NRIs planning summer trips that route through African hubs — Nairobi, Addis Ababa, Johannesburg — the advisory does not apply to transit countries, but the anxiety is real. And with the FIFA World Cup starting June 14, bringing millions of travellers from every continent into US cities, the question of whether Bundibugyo can be contained before the world's largest mass-gathering event is not theoretical. It is three weeks away.",
        "tags": ["Ebola", "Bundibugyo", "green card", "Title 42", "CDC", "WHO", "PHEIC", "DRC", "Congo", "Uganda", "South Sudan", "India", "travel advisory", "NRI", "FIFA", "World Cup", "immigration", "health", "pandemic", "Africa"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — US extends Ebola travel ban to Green Card holders (May 23)", "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/us-extends-ebola-travel-ban-green-card-holders-2026-05-23/"},
            {"name": "Reuters — More than 900 suspected Ebola cases identified in DRC, WHO chief says (May 24)", "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/more-than-900-suspected-ebola-cases-identified-drc-who-chief-says-2026-05-24/"},
            {"name": "Reuters — US adds Atlanta area airport for Ebola screening, CDC says", "url": "https://www.reuters.com/us-adds-atlanta-ebola-screening-cdc-2026-05-24/"},
            {"name": "WHO — Ebola outbreak DRC 2026", "url": "https://www.who.int/emergencies/disease-outbreak-news/item/2026-DON562"},
            {"name": "Livemint — India advises against travel to DRC, Uganda and South Sudan following Ebola emergency", "url": "https://www.livemint.com/news/india/india-advises-against-travel-drc-uganda-south-sudan-ebola-emergency"},
            {"name": "CNN — Inside the epicenter of the Ebola outbreak in DRC as the virus spreads", "url": "https://www.cnn.com/2026/05/24/health/ebola-outbreak-drc-epicenter/"}
        ]),
        "score_total": 87,
        "status": "published",
        "published_at": now_iso,
        "body": """On Friday afternoon, while most of Washington was emptying out for the Memorial Day weekend, the Centers for Disease Control and Prevention issued an order that has no precedent in American public health history.

The CDC temporarily banned lawful permanent residents — green card holders — from entering the United States if they had been in the Democratic Republic of Congo, Uganda, or South Sudan in the previous 21 days.

Green card holders have never been included in a US health-based entry restriction before. Not during COVID. Not during the 2014 Ebola outbreak in West Africa that killed 11,000 people. Not during SARS, MERS, H1N1, or any other pathogen that triggered emergency public health orders. The CDC's own COVID-era Title 42 order, which was used to expel millions of asylum seekers at the southern border between 2020 and 2023, explicitly exempted green card holders.

This time, the CDC said the extension was "necessary to stop the virus from entering the country."

"Applying this authority to lawful permanent residents for a limited period of time provides a balance between protecting public health and managing emergency response resources," the agency said in a statement.

The order was issued under Title 42 of US public health law — the same statute that became the most contentious immigration tool of the pandemic era.

## The Outbreak

The Ebola outbreak that triggered this order is the most serious the world has seen in a decade, and it involves a strain of the virus for which there is no approved vaccine and no proven treatment.

The pathogen is the Bundibugyo ebolavirus — one of five known Ebola species. It was first identified in 2007 in the Bundibugyo district of Uganda. Unlike the more common Zaire strain, which caused the devastating 2014-2016 West African epidemic and for which two vaccines (Ervebo and Zabdeno/Mvabea) now exist, Bundibugyo has no vaccine in advanced development and no FDA-approved therapeutic. The case fatality rate in previous Bundibugyo outbreaks has been approximately 25-50 percent, but with delayed detection and overwhelmed health systems, the effective mortality can be much higher.

The current outbreak began in Ituri province, a conflict-affected region in northeastern DRC where healthcare infrastructure has been degraded by years of fighting between government forces and armed groups. The virus spread undetected for weeks — local authorities were initially testing for the Zaire strain and coming up negative, not realising they were dealing with Bundibugyo.

By the time the outbreak was confirmed in early May, it had already moved from rural villages into cities.

As of Sunday, WHO Director-General Tedros Adhanom Ghebreyesus reported more than 900 suspected cases, including 101 confirmed, with 177 suspected deaths. The virus has reached Goma — a city of over two million people on the Rwandan border — and Bunia, the capital of Ituri province. Both cities are partially under the control of the M23 rebel group, cutting them off from the resources of Congo's central government.

The outbreak has crossed international borders. Uganda has reported five confirmed cases and two deaths. South Sudan, which shares a porous border with DRC's outbreak zone, has not yet confirmed cases but is considered high-risk.

On May 17, the WHO declared the outbreak a Public Health Emergency of International Concern — the highest level of alarm the organisation can raise.

## What the US Has Done

The US response has escalated rapidly over the past week.

On Monday, May 19, the Trump administration initially banned non-citizens who had travelled to the DRC, Uganda, or South Sudan in recent weeks from entering the United States. US citizens and green card holders were exempt, consistent with decades of precedent.

On Saturday, May 24, the CDC added Hartsfield-Jackson Atlanta International Airport as a second screening site for Americans returning from the affected countries. Washington's Dulles International Airport had been designated earlier in the week. Enhanced screening includes temperature checks, symptom assessment, and post-arrival public health monitoring for 21 days — the maximum incubation period for Ebola.

On Friday, May 23, the CDC took the unprecedented step of extending the ban to green card holders.

The legal mechanism is Title 42, Section 265 of the US Code, which authorises the Surgeon General (delegated to the CDC director) to "prohibit, in whole or in part, the introduction of persons and property" from foreign countries when there is "serious danger of the introduction of a communicable disease."

The provision had been used sparingly before COVID. Its invocation against green card holders is new legal territory.

## Why Green Card Holders Were Included

The CDC's statement did not elaborate extensively on the reasoning, but the epidemiological logic is straightforward: Bundibugyo has a 21-day incubation period, during which an infected person may be asymptomatic and undetectable by screening. There is no rapid diagnostic test for Bundibugyo that can be deployed at airports. And unlike COVID, where most infections were mild, Ebola kills a significant proportion of those it infects.

The practical concern is that a green card holder returning from eastern DRC could pass through airport screening, return to their community, develop symptoms days or weeks later, and trigger a domestic transmission chain before the disease is identified.

The Wall Street Journal reported that doctors and hospitals in the DRC are struggling to keep up with the outbreak's spread, with healthcare workers themselves becoming infected and supplies running critically low. "What we have are not even enough for several days," one health worker told the paper.

The fear is that the same inadequacy of containment infrastructure that allowed Bundibugyo to spread across DRC and into Uganda could, with one missed case, cross an ocean.

## India's Response

India's Ministry of External Affairs issued a travel advisory telling Indian citizens to avoid non-essential travel to the DRC, Uganda, and South Sudan.

The advisory follows the WHO's PHEIC declaration and mirrors similar advisories issued by other governments. India has also implemented enhanced border surveillance and quarantine protocols at international airports, though the specifics of screening procedures have not been detailed.

The advisory is relevant for several categories of Indian nationals: humanitarian workers (India has a significant presence in African development projects), business travellers (Indian companies have operations in East African mining and telecommunications), students (a small but growing number of Indian students study in Uganda and Kenya), and diplomatic personnel.

For the broader Indian diaspora, the concern is less about direct travel to the outbreak zone and more about the precedent being set and the secondary effects on global movement.

## The Green Card Precedent

For the 4.4 million Indian Americans — approximately 2.8 million of whom are estimated to hold green cards or be in the naturalisation pipeline — the CDC's order matters beyond Ebola.

A green card is supposed to be a near-permanent right to live and work in the United States. Holders pay taxes, serve in the military, own businesses, and raise American children. The legal distinction between a green card holder and a citizen is narrow: green card holders cannot vote, cannot hold certain government positions, and can lose their status through extended absence or criminal conviction. But they have always been treated as functionally present residents for the purpose of entry restrictions.

The COVID-era travel bans demonstrated that executive authority over immigration can expand rapidly during public health emergencies. But even at the height of the pandemic, when the US banned travellers from China, Europe, Brazil, India, and dozens of other countries, green card holders were exempt.

The Ebola order breaks that line.

Immigration attorneys have already flagged the implications. If Title 42 can be used to bar green card holders from entry based on a health emergency in a specific set of countries, the legal framework exists for future administrations to expand the scope — to more countries, for more diseases, for longer durations.

This does not require congressional action. Title 42 is an existing statute. The CDC director has the authority to issue the order. The only check is judicial review, and courts have historically been deferential to the executive branch on public health and immigration matters.

## The FIFA Question

The timing of the outbreak coincides with the approach of the largest mass-gathering event of the year.

The 2026 FIFA World Cup begins on June 14, with matches hosted across 16 cities in the United States, Canada, and Mexico. The tournament is expected to draw approximately 5.5 million spectators to stadiums, with millions more travelling internationally for fan events, watch parties, and tourism.

The participating nations include several from West and Central Africa — Ghana, Cameroon, and Nigeria have qualified. While these countries are geographically distant from the DRC outbreak zone, the movement of millions of people through international airports over a six-week period creates the conditions for any infectious disease to spread.

Harris County, Texas — home to Houston, which will host multiple World Cup matches — said last week that officials were monitoring the situation but assessed the risk from Ebola as "low" for World Cup events. Harris County Health Authority Dr. Ericka Brown Hidalgo noted that the DRC is "geographically vast" and that many travellers from the country come from areas far from the outbreak.

But the WHO's own assessment is less sanguine. The organisation raised the risk of national-level spread in the DRC to "very high" on Friday — the highest internal classification before a pandemic declaration.

## What Bundibugyo Means

Most people who followed the 2014 Ebola crisis associate the disease with the Zaire strain — the most lethal of the five known Ebola species, with a case fatality rate that historically ranged from 60 to 90 percent. The 2014-2016 West African epidemic killed 11,325 people and infected 28,616.

Bundibugyo is different. It is rarer — only two previous outbreaks have been recorded (2007 in Uganda, 2012 in DRC). Its case fatality rate is lower, approximately 25-50 percent. But in a crucial respect, it is more dangerous: there is no vaccine.

The two approved Ebola vaccines — Merck's Ervebo and Johnson & Johnson's Zabdeno/Mvabea — were developed specifically for the Zaire strain. They have not been validated against Bundibugyo, and there is no crossover efficacy data that would justify emergency deployment.

This means the response relies entirely on traditional public health measures: case identification, contact tracing, isolation, and supportive care. In a conflict zone like Ituri province, where armed groups control territory, healthcare workers are targeted, and population movement is constant, those measures are extraordinarily difficult to implement.

CNN reported on Sunday that suspected Ebola patients had escaped from a health centre in the DRC, highlighting the difficulty of containment in an environment where trust in authorities is low and fear of isolation is high.

## What This Means for NRI Families

For Indian Americans, the Ebola outbreak intersects with several existing anxieties.

**Travel:** Summer is peak travel season for Indian Americans visiting family in India and elsewhere. Some common routing through African hub airports — Nairobi (Kenya Airways), Addis Ababa (Ethiopian Airlines), Johannesburg (South African Airways) — puts travellers in proximity to the affected region even if they are not visiting DRC, Uganda, or South Sudan. The current US ban applies only to those who have physically been in those three countries. Transit through their airports, however, could trigger additional screening.

**Healthcare workers:** Indian Americans are disproportionately represented in the US healthcare workforce. Approximately 20 percent of practising physicians in the United States are of Indian origin. In the event of a domestic Ebola case — however unlikely — the healthcare system's response would lean heavily on these professionals, as it did during COVID.

**Immigration precedent:** The green card ban arrives in a context where Indian Americans are already navigating an increasingly hostile immigration environment. The USCIS adjustment-of-status memo, the EB-2 retrogression, the H-1B fee hikes, the naturalisation freeze in 39 countries — each of these has chipped away at the assumption that legal immigration status provides stability and predictability. The Ebola ban adds a new dimension: health emergencies can now be used to restrict the movement of permanent residents.

**World Cup planning:** Many Indian American families have purchased tickets for World Cup matches, particularly India's historic first appearance in the tournament. The question of whether Ebola poses a risk at the event is understandably top of mind, even if the actual probability of transmission in a US stadium is extremely low.

## The Uncertain Trajectory

The fundamental uncertainty is whether the outbreak can be contained before it becomes a pandemic.

The WHO has deployed teams to the DRC and is working with Uganda to strengthen surveillance at the border. The UK has committed £20 million ($26.87 million) to fund response efforts, supporting the WHO and NGOs in surveillance, worker protection, and infection control.

But the structural challenges are immense. The outbreak zone is in a conflict area. Two of the affected cities — Goma and Bunia — are under rebel control, limiting the central government's ability to deliver supplies and coordinate response. Healthcare workers are themselves becoming infected. Supplies are critically short.

And the disease is spreading. The jump from 51 confirmed cases (when the WHO declared the PHEIC on May 17) to 101 confirmed cases (as of Sunday) represents a near-doubling in one week. The 900-plus suspected cases, many of which have not yet been tested, suggest the actual scope of the outbreak is significantly larger than confirmed numbers indicate.

For India and for the Indian diaspora, the immediate practical response is clear: follow the MEA's travel advisory, avoid non-essential travel to the three affected nations, monitor airline transit routes, and stay informed.

The larger concern — whether the precedent of banning green card holders will be expanded, whether Bundibugyo will cross more borders, whether the World Cup will proceed without incident — has no answer yet. The virus, like so many crises of 2026, is still moving."""
    })
    print(f"✅ Article 1 queued: {slug1}")
else:
    print(f"⏭️  Article 1 skipped (duplicate): {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Indian Markets Surge + Oil Drops + $23.86B Foreign Outflows + Kevin Warsh New Fed Chair → NRI Money
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("india-markets-surge-oil-drops-warsh-fed-chair-nri-money-mortgages")
headline2_prefix = "indian markets jumped to a two-week"
if slug2 not in existing_slugs and not any(headline2_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Indian Markets Jumped to a Two-Week High on Monday. Oil Fell 5.5 Percent. And the Man Who Now Controls US Interest Rates Was Sworn In by Trump Three Days Ago. Here Is What All of This Means for Your Money.",
        "subheadline": "On Monday, the Nifty 50 rose 1.32 percent to 24,031 and the Sensex gained 1.42 percent to 76,489 — their highest levels since May 8 — as Brent crude fell 5.5 percent to $97.8 per barrel on hopes that a US-Iran deal might reopen the Strait of Hormuz. Banking stocks led the rally, with HDFC Bank up 2.6 percent and ICICI Bank up 2.3 percent. But the numbers beneath the headline are less reassuring. Foreign portfolio investors have now pulled $23.86 billion from Indian stocks in 2026, already surpassing all of last year's record outflows — the most sustained foreign exit from Indian equities in history. India raised petrol and diesel prices for the fourth time in May. And in Washington, Kevin Warsh was sworn in on Friday as the new Federal Reserve chair, replacing Jerome Powell, with a mandate from Trump to 'do your own thing and do a great job' — a presidential wish-list that includes cutting rates at a time when US consumer sentiment has fallen to the lowest level of Trump's second term and 30-year mortgage rates have climbed above 6.5 percent. For the 4.4 million Indians in America, the convergence of these three events — India market rally, oil price drop, new Fed chair — is not abstract. It determines whether your SIP in an Indian mutual fund recovers or bleeds, whether your home mortgage rate in New Jersey or Fremont rises or falls, and whether the rupee your parents receive when you send money home buys more or less.",
        "slug": slug2,
        "category": "news",
        "vertical": "economy",
        "diaspora_angle": "Every Indian American household operates in two economies simultaneously. Your salary is in dollars. Your parents' expenses are in rupees. Your mortgage is set by the Fed. Your SIP returns are set by the Nifty. Your fuel costs are set by crude oil. Your savings are split between a 401(k) in US equities and, for many, mutual funds or real estate in India. When markets move — as they did on Monday, with Indian stocks surging, oil dropping, and the new Fed chair taking over with a political mandate to cut rates — the effects ripple through both halves of this financial life simultaneously. Here is a plain-language breakdown of what happened today and what it means for specific financial decisions NRI families are making right now. Your India SIPs: The Nifty's 1.32 percent jump looks good in a portfolio notification, but the $23.86 billion in foreign outflows this year means institutional investors are selling into every rally. If you are doing a systematic investment plan, the falling NAVs of the past three months mean your SIP is buying more units at lower prices — which is exactly what SIPs are designed for. Do not stop your SIP because of a bad quarter. The value of rupee-cost averaging appears only when markets recover. Your US mortgage: The new Fed chair, Kevin Warsh, was Trump's pick specifically because Trump wanted someone who would cut rates. But Warsh inherits an economy where inflation has not fully retreated and mortgage rates are at 6.5 percent — a nine-month high. If Warsh cuts rates aggressively, your 2027 refinance window opens. If he holds because inflation persists, your 30-year fixed stays above 6 percent through the year. For NRIs buying homes — and Indian Americans are among the highest-income homebuying demographics in the US — the difference between 6 percent and 5.5 percent on a $600,000 mortgage is roughly $200 a month. Your remittances: The rupee at ₹95 means your $1,000 transfer home buys ₹95,000 instead of the ₹85,000 it bought in January. Good for sending money. Bad for India's import bill. If oil drops further on a real Iran deal, the rupee should strengthen toward ₹90, reducing your remittance purchasing power but stabilising your parents' cost of living. This is the fundamental tension: what is good for your transfer is bad for their expenses, and vice versa. Your 401(k): US equities are rallying on the same oil-drop optimism. The S&P 500 is near all-time highs. Your 401(k), if allocated to a standard target-date fund, is benefiting. But consumer sentiment at the lowest of Trump's second term suggests the rally may be fragile. The risk is a correction if the Iran deal falls apart, oil spikes back above $110, and the new Fed chair is forced to hold rates to contain inflation.",
        "tags": ["Nifty", "Sensex", "BSE", "NSE", "oil", "Brent", "crude", "Kevin Warsh", "Federal Reserve", "Fed", "Powell", "mortgage", "rates", "SIP", "mutual fund", "remittance", "rupee", "NRI", "401k", "HDFC", "ICICI", "FPI", "foreign investors", "Trump", "Iran", "Hormuz"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — Indian shares jump to two-week high as oil drops on Mideast peace talk hopes (May 25, 2026)", "url": "https://www.reuters.com/world/india/indian-shares-open-higher-us-iran-peace-deal-optimism-2026-05-25/"},
            {"name": "Reuters — Analysis: Trump and Warsh's fates are now tied, for better or worse (May 25, 2026)", "url": "https://www.reuters.com/world/us/trump-warshs-fates-are-now-tied-for-better-or-worse-2026-05-25/"},
            {"name": "Reuters — Iran and US play down hopes for imminent breakthrough in war (May 25, 2026)", "url": "https://www.reuters.com/world/iran-us-play-down-hopes-imminent-breakthrough-2026-05-25/"},
            {"name": "Arihant Capital Markets — analyst commentary on banking sector reversal", "url": ""},
            {"name": "University of Michigan — Consumer Sentiment Index, May 2026 preliminary", "url": ""}
        ]),
        "score_total": 83,
        "status": "published",
        "published_at": now_plus1,
        "body": """On Monday morning, if you opened your Groww app or Zerodha dashboard, you saw green. The Nifty 50 was up 1.32 percent. The Sensex was up 1.42 percent. Your mutual fund SIPs, which have been bleeding for weeks, showed a small recovery. Your parents, if they track the markets, might have called to say things are looking better.

They are not looking better. They are looking less bad. There is a difference, and for Indian American families managing money across two countries, understanding the difference is the entire financial question of 2026.

Here is what actually happened on Monday, what is driving it, and what it means for the specific financial instruments and decisions that NRI families deal with every month.

## What Happened in Indian Markets

India's benchmark Nifty 50 rose 1.32 percent to close at 24,031.70. The BSE Sensex gained 1.42 percent to reach 76,488.96. Both indexes hit their highest levels since May 8, 2026 — a two-week high.

The trigger was oil. Brent crude futures fell 5.5 percent on Monday to $97.8 per barrel, their lowest in two weeks. The decline was driven by President Trump's Saturday claim that a memorandum of understanding to end the Iran war had been "largely negotiated," which raised hopes that the Strait of Hormuz would reopen to commercial shipping.

For India, which imports 85 percent of its crude oil, every dollar drop in crude translates directly into reduced import costs, a narrower current account deficit, and less pressure on the rupee. When oil drops 5.5 percent in a single day, Indian markets celebrate because the math of India's economy improves overnight.

Banking stocks led the rally. HDFC Bank jumped 2.6 percent. ICICI Bank gained 2.3 percent. The broader financials index surged 2.2 percent. This matters because banking stocks were among the worst hit during the sell-off that has defined 2026 — dragged down by their high foreign investor holdings and by concerns that the energy crisis would damage loan demand and asset quality.

"Banking stocks were among the worst hit in this sell-off due to higher foreign investor holding and concerns over macroeconomic impact of the Iran war. We are seeing some reversal of that now as there are signs of progress in U.S.-Iran talks," said Anita Gandhi, head of institutional business at Arihant Capital Markets.

Fifteen of the sixteen major sector indexes rose. The small-cap and mid-cap indexes gained 1.4 percent and 0.9 percent, respectively. Oil marketing companies — BPCL, HPCL, Indian Oil — gained between 3.2 and 4.3 percent, despite India raising petrol and diesel prices for the fourth time in May on the same day.

## The Number Beneath the Rally: $23.86 Billion

A one-day rally does not erase a structural problem. And the structural problem with Indian markets in 2026 is that foreign investors are leaving.

Foreign portfolio investors have now sold $23.86 billion worth of Indian stocks so far this year. That number has already surpassed all of 2025's record annual outflows — and we are only in May.

This is the most sustained foreign exit from Indian equities in history. The outflows are driven by a combination of factors: the energy crisis making India's growth outlook uncertain, the rupee's decline making Indian assets less attractive in dollar terms, rising US Treasury yields offering better risk-adjusted returns, and a general flight from emerging markets toward the perceived safety of US assets.

What this means in practical terms is that every rally in Indian markets is being sold into by foreign institutions. Monday's surge was real — but the question is whether it has staying power when the largest category of institutional investors is systematically reducing its India allocation.

For NRI investors with SIPs in Indian mutual funds, this creates an uncomfortable dynamic. Your monthly investment is buying units at cheaper prices (good for long-term rupee-cost averaging), but the funds themselves are dealing with persistent outflows that force fund managers to sell holdings to meet redemptions (bad for near-term NAV recovery).

The right response, for most long-term investors, is to continue SIPs. The wrong response is to interpret a one-day rally as the bottom and increase allocations on the assumption that the worst is over. The $23.86 billion exit says the worst may not be over.

## The New Man at the Fed

Three days before Monday's Indian market rally, in a ceremony at the White House that included cabinet secretaries and Supreme Court justices, Kevin Warsh was sworn in as the 17th chair of the Federal Reserve, replacing Jerome Powell.

For every Indian American with a mortgage, a car loan, a credit card balance, or a dollar-denominated savings account, Warsh is now the single most consequential person in their financial life.

Trump chose Warsh specifically because he wanted a Fed chair who would lower interest rates. At the swearing-in ceremony, Trump said he wanted Warsh to "do your own thing and do a great job," adding that "Kevin understands that when the economy is booming that is a good thing. We want it to boom. We don't want to see it stifled."

The subtext was unmistakable: cut rates. Stimulate growth. Help us win the midterms.

But Warsh inherits an economy that does not make rate cuts straightforward.

Consumer sentiment, as measured by the University of Michigan, fell to the lowest level of Trump's second term in the latest reading. Confidence among independents — the key midterm voting bloc — and even Republicans tumbled. People feel poor, and they feel uncertain.

At the same time, the 30-year fixed mortgage rate has climbed above 6.5 percent — a nine-month high. Housing is effectively frozen for many buyers. Prices have continued rising under Trump despite campaign pledges that they would fall "from day one."

Inflation has not fully retreated. Since March 2025, the core PCE inflation gauge has remained stubbornly above the Fed's 2 percent target, partly due to energy costs driven by the Iran war.

This creates a dilemma for Warsh: cut rates to stimulate growth (as Trump wants), and risk reigniting inflation. Hold rates to contain inflation, and risk a recession as consumers and businesses pull back under the weight of high borrowing costs.

## What This Means for Your Mortgage

If you are an Indian American homeowner with a variable-rate mortgage or a homebuyer waiting for rates to drop before purchasing, Warsh's decisions over the next 12 months will determine your monthly payment.

The numbers are stark. On a $600,000 mortgage — roughly the median for Indian American homebuyers in metro areas like the Bay Area, New Jersey, or the DC suburbs:

At 6.5 percent (current 30-year fixed): Your monthly payment is approximately $3,792.

At 6.0 percent (if Warsh cuts modestly): Your monthly payment drops to approximately $3,597 — a savings of $195 per month, or $2,340 per year.

At 5.5 percent (if Warsh cuts aggressively): Your monthly payment drops to approximately $3,406 — a savings of $386 per month, or $4,632 per year.

The question is whether Warsh will cut at all in 2026, and if so, how quickly. If the Iran deal materialises and oil drops significantly, the inflation pressure eases, giving Warsh room to cut. If the deal collapses and oil spikes back above $110, he is trapped — high inflation prevents rate cuts, and high rates prevent economic recovery.

For NRIs in the homebuying window, the practical advice is: do not wait for a specific rate. If you find the right property at a price you can afford at current rates, buy it. You can always refinance later if rates drop. What you cannot do is time the market based on the outcome of a peace negotiation in the Middle East.

## What This Means for Your Remittances

The rupee closed around ₹95.50 to the dollar on Monday, recovering slightly from its record low of ₹97 earlier in the month.

If you are sending money home to India — and approximately 40 percent of Indian Americans report sending regular remittances — the weak rupee means your dollars buy more rupees. A $1,000 transfer at ₹95 delivers ₹95,000 to your family. At the ₹83-85 range that prevailed a year ago, the same transfer delivered only ₹83,000-85,000.

This is the remittance paradox: what is good for you as a sender is bad for your family as recipients. Your $1,000 buys more rupees, but those rupees buy less. Petrol at ₹113 per litre. LPG hiked four times since February. Food prices elevated by supply chain disruptions. The nominal increase in rupees received is partially or fully offset by the inflation your family is experiencing.

If a real Iran deal brings oil down and the rupee strengthens back toward ₹88-90 over the next quarter, your remittance purchasing power decreases — but your family's cost of living stabilises. For most NRI families, stabilisation of their parents' expenses is worth more than a favourable exchange rate.

## What This Means for Your 401(k)

US equities have rallied alongside Indian markets on the same oil-price optimism. If your 401(k) is allocated to a standard target-date fund or an S&P 500 index fund — as most Indian Americans' retirement savings are — your portfolio is benefiting from Monday's move.

But the underlying economic data is less encouraging than the market's mood. Consumer confidence is at its lowest in this administration. Tariff uncertainty — Trump's proposed 50 percent levy on the EU, the ongoing China tariffs, the Supreme Court challenge to tariff authority — creates persistent uncertainty for corporate earnings.

The risk scenario is that the Iran deal falls apart, oil spikes back above $110, the Fed is forced to hold rates or even consider hikes, and both US and Indian markets correct sharply. This is not the base case — most analysts expect some form of deal — but it is the scenario that would hurt NRI finances most, because it would simultaneously hit your 401(k), your Indian SIPs, your mortgage rate, and your family's living costs.

## The Practical Takeaway

For Indian American families navigating Monday's news, the actionable items are:

Continue your India SIPs. The rally is encouraging but do not increase allocation on a single day's movement. The $23.86 billion in foreign outflows is a structural headwind that will take quarters, not days, to reverse.

Do not make mortgage decisions based on Fed speculation. If you can afford a home at current rates, the opportunity is now. Refinancing options will emerge if and when rates drop.

Monitor the Iran deal as a financial indicator, not just a news story. A real deal that reopens Hormuz is the single event most likely to improve every dimension of NRI finances simultaneously — lower oil, stronger rupee, lower inflation in India, room for Fed cuts in the US. Its failure would be the single event most likely to damage all of them.

Understand that the new Fed chair has a political mandate to cut rates but an economic reality that may prevent it. Warsh's actions, not his appointment, will determine your financial year.

And remember: you operate in two economies. One rallied on Monday. Both remain fragile. The prudent response is not optimism or pessimism. It is diversification, discipline, and a very close watch on the Strait of Hormuz."""
    })
    print(f"✅ Article 2 queued: {slug2}")
else:
    print(f"⏭️  Article 2 skipped (duplicate): {slug2}")


# ── Insert articles ──
for article in articles:
    try:
        result = sb_post("p2_articles", article)
        print(f"✅ Inserted: {article['slug']} → {article['id']}")
    except Exception as e:
        print(f"❌ Insert failed for {article['slug']}: {e}")

print(f"\n{'='*60}")
print(f"Published {len(articles)} articles")
print(f"{'='*60}")

# ── Source images for articles ──
PEXELS_KEY = ""
pexels_env = Path.home() / "workspace" / ".env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if "pexels" in k.lower():
                PEXELS_KEY = v.strip()

def search_pexels(query, per_page=5):
    if not PEXELS_KEY:
        return []
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": per_page, "orientation": "landscape"},
        timeout=15,
    )
    if r.status_code == 200:
        return r.json().get("photos", [])
    return []

def get_pexels_image_url(query):
    photos = search_pexels(query)
    if photos:
        return photos[0]["src"]["large2x"]
    return None

image_queries = {
    slug1: "medical laboratory health worker protective equipment africa",
    slug2: "stock market trading floor screens financial data",
}

for art in articles:
    slug = art["slug"]
    query = image_queries.get(slug, "")
    if not query:
        continue
    img_url = get_pexels_image_url(query)
    if img_url:
        try:
            sb_patch("p2_articles", {"id": f"eq.{art['id']}"}, {"image_url": img_url})
            print(f"🖼️  Image set for {slug}: {img_url[:80]}...")
        except Exception as e:
            print(f"⚠️  Image PATCH failed for {slug}: {e}")
    else:
        print(f"⚠️  No Pexels image found for {slug}")

# ── Score decay for news articles older than 12h ──
try:
    decay_articles = sb_get("p2_articles", {
        "select": "id,score_total,published_at",
        "status": "eq.published",
        "category": "eq.news",
        "score_total": "gt.40",
        "published_at": "lt." + (now - timedelta(hours=12)).isoformat().replace('+00:00', 'Z'),
        "order": "published_at.desc",
        "limit": "50"
    })
    decayed = 0
    for a in decay_articles:
        age_hours = (now - datetime.fromisoformat(a["published_at"].replace('Z', '+00:00'))).total_seconds() / 3600
        if age_hours > 48:
            decay = 3
        elif age_hours > 24:
            decay = 2
        else:
            decay = 1
        new_score = max(40, a["score_total"] - decay)
        if new_score != a["score_total"]:
            sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": new_score})
            decayed += 1
    print(f"\n📉 Score decay: {decayed} news articles decayed")
except Exception as e:
    print(f"⚠️ Score decay error: {e}")

# ── Git commit & push ──
try:
    repo = Path.home() / "workspace" / "the-videshi-news"
    subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True, timeout=30)
    msg = f"news: Ebola green card ban + India markets surge NRI money ({now.strftime('%Y-%m-%d %H:%M UTC')})"
    subprocess.run(["git", "commit", "-m", msg, "--allow-empty"], cwd=repo, capture_output=True, timeout=30)
    push = subprocess.run(["git", "push"], cwd=repo, capture_output=True, timeout=60)
    if push.returncode == 0:
        print("🚀 Git push successful → Vercel deploy triggered")
    else:
        print(f"⚠️ Git push issue: {push.stderr.decode()[:200]}")
except Exception as e:
    print(f"⚠️ Git error: {e}")

print("\n✅ Writer pipeline complete")
