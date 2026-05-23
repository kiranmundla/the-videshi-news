#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 3:30 AM batch
Topics:
1. USCIS green card bombshell — applicants must return home to apply
2. India's power grid hits record 270 GW amid heatwave and outages
"""

import json, os, uuid, re, requests
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

def sb_patch(table, filters, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, json=data, timeout=30)
    return r.status_code

def make_slug(headline, date_suffix="20260523"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: USCIS Green Card Bombshell
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "The U.S. Just Told Green Card Applicants to Leave the Country and Apply From Home. For Hundreds of Thousands of Indians, the Nightmare Scenario Is Here.",
    "subheadline": "USCIS announced Friday that foreigners seeking permanent residency must now return to their home countries to apply — ending a decades-old practice that allowed people to adjust status from inside the U.S. Immigration lawyers are calling it the most disruptive legal immigration change of the Trump era. For the estimated 400,000 Indians with pending green card applications, the policy means leaving jobs, separating from families, and entering a consular backlog that stretches years.",
    "slug": make_slug("uscis-green-card-apply-from-home-country-india-nri"),
    "category": "nri-world",
    "vertical": "immigration",
    "diaspora_angle": "Indians are the single largest nationality in the U.S. employment-based green card backlog, with wait times that already stretch decades due to per-country caps. This policy change forces them to choose between staying in the U.S. on temporary visas — with no path to permanence — or leaving their jobs, homes, and children's schools to apply from India, where U.S. consular wait times in Mumbai and Delhi already exceed 18 months.",
    "tags": ["USCIS", "green card", "adjustment of status", "immigration", "NRI", "H-1B", "India", "Trump", "consular processing", "I-485", "legal immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters — USCIS tells foreigners seeking green cards: Return to your countries to apply", "url": "https://www.reuters.com/legal/government/uscis-tells-foreigners-seeking-green-cards-return-your-countries-apply-2026-05-22/"},
        {"name": "CNN — Trump administration upends green card process, potentially compelling hundreds of thousands to leave US", "url": "https://www.cnn.com/2026/05/22/politics/green-card-seekers-leave-us-apply"},
        {"name": "USCIS — Adjustment of Status granted only in extraordinary circumstances", "url": "https://www.uscis.gov/newsroom/news-releases/uscis-will-grant-adjustment-of-status-only-in-extraordinary-circumstances"},
        {"name": "The Hindu Business Line — US Green card applications only from home country", "url": "https://www.thehindubusinessline.com/news/us-changes-green-card-process-asks-applicants-to-return-home-for-filing/article71012308.ece"},
        {"name": "Fox News — Trump administration orders green card applicants to leave the US", "url": "https://www.foxnews.com/politics/trump-administration-orders-green-card-applicants-leave-us-apply-from-their-home-countries"}
    ]),
    "score_total": 96,
    "status": "published",
    "published_at": now,
    "body": """On Friday evening, the U.S. Citizenship and Immigration Services published a policy memo that immigration attorneys have spent the weekend calling the single most consequential change to legal immigration since Trump returned to office. The language was bureaucratic. The impact is seismic.

Under Policy Memorandum PM-602-0199, USCIS has declared that adjustment of status — the process by which someone already in the United States applies for a green card without leaving the country — is no longer a standard pathway. It is now "an extraordinary form of relief" to be granted only in limited cases. Everyone else must leave the country, return to their home nation, and apply for an immigrant visa through a U.S. consulate abroad.

"From now on, an alien who is in the U.S. temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances," USCIS spokesman Zach Kahler said in a statement. "This policy allows our immigration system to function as the law intended instead of incentivizing loopholes."

For the roughly 1.4 million people who obtained lawful permanent residence in fiscal year 2024 — and the hundreds of thousands currently in the pipeline — the memo upends a process that has functioned essentially the same way for decades.

## What Changed

Until Friday, adjustment of status was routine. If you were in the U.S. on a valid visa — an H-1B work visa, an L-1 intracompany transfer, an F-1 student visa — and your employer or family member filed an immigrant petition on your behalf, you could submit Form I-485 and wait for your green card while continuing to live and work in America. You kept your job, your kids stayed in school, your life continued with minimal disruption.

The new memo does not technically eliminate this process. But it reframes it so fundamentally that immigration lawyers say the practical effect is the same. USCIS officers are now directed to treat adjustment of status as discretionary and extraordinary — to weigh a series of favorable and negative factors before deciding whether an applicant "merits" the privilege of staying in the U.S. while their case is processed.

Among the negative factors: "choosing AOS when consular processing was readily available abroad." For Indian applicants, consular processing is available at five U.S. consulates and the embassy. This factor alone could be grounds for denial.

The alternative — consular processing — requires applicants to leave the United States, attend an interview at a U.S. embassy or consulate in their home country, and wait for a visa to be issued before re-entering. For countries with long backlogs, this can mean months or years of separation.

## Why Indians Are Uniquely Exposed

No nationality is more affected than Indians. This is not an opinion — it is a structural fact of the U.S. immigration system.

India faces the longest employment-based green card backlog of any country, a consequence of per-country caps that limit each nation to 7% of available immigrant visas regardless of demand. The result: an Indian-born software engineer who filed for a green card in 2012 may still be waiting in 2026. The Cato Institute estimates that some Indians in the EB-2 and EB-3 categories face wait times exceeding 90 years.

Under the old system, these applicants waited in the U.S. — working, paying taxes, raising families, building lives. Under the new system, they may be compelled to leave the country and wait from India, where U.S. consular appointment backlogs in Mumbai and Delhi already stretch beyond 18 months for routine immigrant visa interviews.

David J. Bier, director of immigration studies at the Cato Institute, described the policy as "illogical" in a blog post laying out potential cascading impacts. "It will drive talented people to other countries and make America a less competitive place for business," he wrote.

## The Human Cost

The memo's language is abstract — "totality of the circumstances," "extraordinary relief," "administrative grace." The human consequences are not.

Consider a typical case: an Indian engineer on an H-1B visa at a major tech company in the Bay Area. She has been in the U.S. for eight years. Her children attend public school in Cupertino. Her husband, on a dependent H-4 visa, recently received work authorization. Her employer filed her I-140 immigrant petition in 2019, and her priority date — the place in the green card queue — is current. Under the old rules, she would file I-485, receive a work permit and travel document, and continue her life while waiting for final adjudication.

Under the new rules, a USCIS officer could look at her case, note that consular processing is available in India, and deny her adjustment application. She would then need to leave the country, uproot her children, abandon her rental lease, and attend a consular interview in Mumbai — a process that, once initiated, could take anywhere from six months to two years.

Multiply this scenario by the estimated 400,000 Indian nationals in various stages of the green card process, and the scale of disruption becomes clear.

## What "Extraordinary Circumstances" Means — and Doesn't

The memo lists factors that officers should weigh in both directions. Favorable factors include long lawful residence, family ties to U.S. citizens, serious hardship to family members, consistent compliance with visa terms, a steady tax history, and a clean record. Negative factors include status violations, unauthorized employment, fraud, and — crucially — "choosing AOS when consular processing was readily available."

What the memo does not provide is a scoring system, a threshold, or a predictable standard. "USCIS did not publish a fixed checklist," noted Visa Verge, an immigration analysis site. The result is a system in which individual officers have broad discretion, with no clear way for applicants to know in advance whether their case will be approved or denied.

It is also unclear whether the policy applies retroactively to the hundreds of thousands of I-485 applications already pending. USCIS has not publicly addressed this question. Immigration attorneys describe this ambiguity as the most destabilizing aspect of the memo.

## The Legal and Political Response

The response has been swift and sharply divided.

Rep. Ted Lieu of California called the policy "stupid" and warned it "will help competitors such as China and Russia." New York Governor Kathy Hochul said it "betrays the very promise that built this country." Rep. Greg Stanton of Arizona argued it undermines the very worker visa programs that allow the U.S. "to attract the top researchers, doctors, & engineers."

Multiple immigration law firms have signaled they are reviewing the memo for potential legal challenges, though no formal lawsuit has been filed as of Saturday. The memo cites two legal authorities — a 1974 Board of Immigration Appeals decision and the Supreme Court's 2022 ruling in Patel v. Garland — that USCIS says support its position that adjustment of status is discretionary, not an entitlement.

Immigration advocates argue the memo misconstrues both rulings, and that decades of consistent agency practice treating AOS as routine cannot be reversed by a single policy memo without notice-and-comment rulemaking. Whether courts agree will likely be decided in the coming months.

## What NRIs Should Do Now

Immigration attorneys are urging anyone in the green card pipeline to take three immediate steps. First, consult an immigration lawyer — not a Facebook group, not a WhatsApp forward, but a licensed attorney who can assess your specific case. Second, do not make any sudden decisions about leaving the country or withdrawing pending applications until the legal landscape clarifies. Third, document everything: your employment history, tax records, community ties, and children's school enrollment, all of which could serve as evidence of "extraordinary circumstances" if your case is reviewed under the new framework.

The Indian American community — 4.4 million strong, the highest-earning ethnic group in the United States — has spent decades building political and institutional support for a more rational immigration system. The per-country cap, the decades-long backlog, the annual uncertainty — these were already a tax on talent and patience. Friday's memo adds a new layer: the possibility that the country you've lived in for a decade might ask you to leave before it decides whether to let you stay.

The practical effects will take months to materialize. The anxiety has already arrived."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: India's Power Grid Hits Record 270 GW
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "India's Power Grid Just Hit a Record 271 Gigawatts. Four Straight Days of Records. And the Worst of Summer Is Still Ahead.",
    "subheadline": "The heatwave that has pushed temperatures past 48°C in parts of Uttar Pradesh and shut schools across northern India is now stress-testing the country's electricity infrastructure like never before. On May 21, India's peak power demand hit 270.82 GW — the fourth consecutive daily record. Chennai is rationing power. Delhi's demand is running 7% above last year. And coal still generates 70% of India's electricity.",
    "slug": make_slug("india-power-grid-record-270gw-heatwave-crisis"),
    "category": "news",
    "vertical": "infrastructure",
    "diaspora_angle": "For NRIs with elderly parents in India, the power crisis is visceral. Power cuts in northern and southern India are hitting hardest at night — when cooling is most critical for the elderly, the sick, and the very young. The heatwave's toll on India's grid also raises questions about the country's energy transition timeline and the investment case for India's booming power sector.",
    "tags": ["heatwave", "India", "power grid", "electricity", "270 GW", "coal", "El Nino", "Delhi", "Chennai", "renewable energy", "infrastructure", "NRI", "energy"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters — Scorching heat drives India's power demand to a record 270 GW amid outages", "url": "https://www.reuters.com/business/energy/scorching-heat-drives-indias-power-demand-record-270-gw-amid-outages-2026-05-21/"},
        {"name": "Reuters — India battles power cuts as heatwave boosts electricity demand to record", "url": "https://www.reuters.com/business/energy/india-battles-power-cuts-heatwave-boosts-electricity-demand-record-2026-05-22/"},
        {"name": "Phys.org — India generates record power as demand surges in severe heat wave", "url": "https://phys.org/news/2026-05-india-generates-record-power-demand-surges-severe-heat-wave.html"},
        {"name": "OilPrice.com — India's Power Demand Hits Record High as Heat Drives Coal Use", "url": "https://oilprice.com/Energy/Energy-General/Indias-Power-Demand-Hits-Record-High-as-Heat-Drives-Coal-Use.html"},
        {"name": "LiveMint — India's peak power demand hits record 270GW as temperature soars", "url": "https://www.livemint.com/news/india/indias-peak-power-demand-hits-record-270gw-as-temperature-soars-11779602404158.html"}
    ]),
    "score_total": 91,
    "status": "published",
    "published_at": now,
    "body": """At 3:45 PM on Thursday, May 21, as the temperature in New Delhi touched 45.3°C and the asphalt on Ring Road went soft underfoot, India's electricity grid hit a number that no grid planner expected to see this early in the season: 270.82 gigawatts of peak demand. The country's power ministry confirmed it was the fourth consecutive daily record, surpassing the previous day's mark of 265.44 GW. And the summer is not even halfway done.

The number itself tells a story of a country being reshaped by heat. When India's power ministry set its peak demand forecast for 2026 at 270 GW, it was projecting a worst-case scenario for mid-June — the traditional apex of pre-monsoon heat. Instead, the country blew through that ceiling in May, driven by an El Niño weather pattern that has delivered above-average heat wave days across the subcontinent weeks earlier than normal.

"Peak demand could rise further if heat waves continue to remain severe across major parts of the country," warned Ankit Jain, vice president at ICRA Limited, the credit rating agency. The India Meteorological Department has forecast that they will.

## Inside the Grid Under Stress

The headline number — 270.82 GW met without major grid failure — sounds like a success story. In some ways, it is. India's power infrastructure has expanded dramatically over the past decade, and the grid's ability to serve 271 GW of simultaneous demand is a genuine engineering achievement.

But the aggregate number masks localised pain. According to data from Grid-India, the national grid operator, localised power outages have been reported during nighttime hours in several regions — precisely when cooling demand from residential air conditioners and fans peaks. The national energy deficit stood at 0.2% and the peak deficit at 0.1% in April, small numbers that translate into real blackouts in states where distribution infrastructure is weakest.

In Chennai, power cuts have become frequent enough that the state electricity board has published rationing schedules. In Uttar Pradesh — India's most populous state, where Banda recorded the season's highest temperature of 48.2°C — extended outages have left residents without fans or refrigeration for hours at a stretch. In Mohali, Punjab, a 17-hour outage in one neighbourhood this week was traced to a single damaged feeder cable — the kind of infrastructure failure that extreme heat makes both more likely and more consequential.

Delhi's peak power demand through May 20 stood at 8,039 MW, compared to 7,533 MW during the same period last year — a 7% increase that the city's power distribution companies attribute almost entirely to cooling demand.

## The Coal Dependency Problem

India has about 228 GW of non-fossil power capacity — solar, wind, hydropower, nuclear. That sounds like a lot until you consider that coal still generates more than 70% of the country's electricity. On the day India hit its all-time demand record, thermal generation — overwhelmingly coal — covered 62% of the load.

The intermittent nature of renewable energy means that solar power contributes heavily during daytime peak hours but drops to zero after sunset, precisely when residential cooling demand surges. The gap is filled by coal and gas plants, many of which are running at or near maximum capacity.

Coal stocks at power plants stood at roughly 16.5 operational days as of this week — adequate by historical standards but uncomfortably thin given the pace of drawdown. If the heatwave persists through the end of May, as the IMD forecasts, those reserves will be tested.

The Strait of Hormuz blockade — which has been in effect since February — has compounded the problem by driving up global fuel, gas, and logistics costs. India imports a significant portion of its natural gas, and the higher costs are squeezing the margins of gas-fired power plants that would otherwise help fill the evening demand gap.

## Schools Shut, Roads Melt, Hospitals Fill

The human side of the crisis is playing out in newspaper headlines and hospital admission logs across northern India. Schools in Lucknow have been closed. Districts in Prayagraj and Patna have preponed summer vacations. The India Meteorological Department has issued "heatwave to severe heatwave" warnings for Delhi, Punjab, Haryana, eastern Uttar Pradesh, and parts of Rajasthan through May 27 — with no significant relief expected until monsoon rains arrive, possibly in early June.

India has recorded over 300 suspected heatstroke cases this season, though health officials acknowledge that the true figure is likely much higher — heatstroke deaths among outdoor labourers, the homeless, and the elderly in rural areas often go unreported or misclassified.

The national electricity demand record is not just a number on a grid operator's dashboard. It is a proxy for the intensity of human discomfort — each gigawatt representing millions of air conditioners, coolers, fans, and refrigerators running at maximum capacity in a desperate bid to make indoor life bearable.

## What This Means for NRIs

For the diaspora, India's power crisis is often experienced through anxious phone calls home. Elderly parents in Delhi or Chennai or Lucknow who describe hours-long power cuts. Relatives who have invested in inverters and generators as insurance against an unreliable grid. The cousin in Kanpur whose small business lost a day's production because the factory's power was cut during peak hours.

The crisis also raises investment questions. India's power sector has been one of the strongest performers on the BSE this year, driven by demand growth that exceeds capacity additions. Renewable energy companies — particularly solar manufacturers and developers — have seen sharp stock appreciation. But the uncomfortable truth exposed by this week's records is that India's energy transition is running years behind its demand curve. The country needs both more renewable capacity and more grid-scale storage to avoid repeating this crisis every summer.

## What Comes Next

The IMD's forecast for the next week is unrelenting: severe heatwave conditions across northwest India through May 28, with temperatures 5.1°C above normal in multiple regions. The monsoon's advance to the Kerala coast is expected around May 26, but its northward progression to the plains of the Gangetic belt — where the heat is most intense — typically takes another three to four weeks.

Until then, India's grid operators will continue to manage demand records that arrive faster than anyone planned for. The power ministry has urged "judicious use of electricity." State governments have issued advisories to stay indoors between 11 AM and 4 PM. And coal trains will continue rolling toward power plants that are burning through their stockpiles at a pace that leaves little margin for error.

The 270 GW number will almost certainly be broken again before summer ends. The question is whether India's infrastructure — grid, coal supply, distribution networks, and the last-mile connections that bring power to homes and hospitals — can keep pace with a climate that is moving faster than the models predicted."""
})

# ── Insert articles ──
print(f"\n{'='*60}")
print(f"Publishing {len(articles)} articles...")
for a in articles:
    try:
        res = sb_post("p2_articles", a)
        print(f"  ✓ [{a['category']}] {a['headline'][:80]}...")
        print(f"    ID: {a['id']}, Slug: {a['slug']}")
    except Exception as e:
        print(f"  ✗ FAILED: {a['headline'][:60]}... — {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY — age out older articles
# ══════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print("Running score decay...")
try:
    resp = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?status=eq.published&score_total=gt.30&select=id,score_total,published_at",
        headers=HEADERS, timeout=30
    )
    all_arts = resp.json()
    now_dt = datetime.now(timezone.utc)
    decayed = 0
    for art in all_arts:
        if not art.get("published_at"):
            continue
        pub = datetime.fromisoformat(art["published_at"].replace("Z", "+00:00"))
        age_hours = (now_dt - pub).total_seconds() / 3600
        if age_hours > 48:
            new_score = max(30, int(art["score_total"] * 0.97))
            if new_score < art["score_total"]:
                sb_patch("p2_articles", f"id=eq.{art['id']}", {"score_total": new_score})
                decayed += 1
    print(f"  Decayed {decayed} articles (of {len(all_arts)} eligible)")
except Exception as e:
    print(f"  Score decay error: {e}")

print(f"\n{'='*60}")
print("Writer batch complete!")
