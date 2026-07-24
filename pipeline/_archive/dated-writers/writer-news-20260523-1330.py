#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 13:30 batch
Topics: Iran deal MOU being fine-tuned (Gulf leaders urge Trump to accept);
        India's financial hemorrhage — $21B foreign exodus, rupee at 97, NRI deposits crashing
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
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

def make_slug(headline, date_suffix="20260523"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-22T00:00:00Z",
    "order": "published_at.desc",
    "limit": "50"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Iran Deal MOU Being Fine-Tuned — Gulf Leaders Urge Trump to Accept
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("iran-deal-mou-fine-tuned-gulf-leaders-trump-india-hormuz")
if slug1 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Gulf Leaders Just Told Trump to Take the Iran Deal. The MOU Is Being 'Fine-Tuned.' For Nine Million Indians Trapped by the Strait of Hormuz Closure, the Next 72 Hours Could Change Everything.",
        "subheadline": "After 24 hours of intensive negotiations in Tehran, Pakistan's military chief left with what Islamabad called 'encouraging progress towards a final understanding.' Iran says a memorandum of understanding is being finalised with 30- to 60-day timelines. Gulf leaders called Trump on Saturday and encouraged him to accept the framework. Trump, who says he is a 'solid 50/50' on whether to resume the war, told CBS he has seen Iran's draft and the two sides are 'getting a lot closer.' For India — whose $102 billion remittance lifeline from the Gulf has been choked, whose rupee has collapsed to record lows, and whose 1.1 million returned workers are still looking for jobs — a deal would be the single most consequential geopolitical event of the year.",
        "slug": slug1,
        "category": "news",
        "vertical": "geopolitics",
        "diaspora_angle": "The Iran war has been an economic disaster for the Indian diaspora in the Gulf. Over 1.1 million Indians have returned from the Gulf since February, flooding a domestic job market already under stress. NRI deposits have fallen by ₹19,000 crore ($2 billion) in a single month. Remittance inflows — which fund entire village economies in Kerala, Bihar, and UP — fell from $16.16 billion to $14.41 billion year-on-year. The Strait of Hormuz closure pushed oil past $100 a barrel, which directly hit India's current account deficit and dragged the rupee to its weakest level in history. For the 9 million Indians who live and work in the Gulf, and the tens of millions of family members who depend on their earnings, whether Trump accepts or rejects the MOU in the next 72 hours is not a foreign policy question. It is a question of whether the money comes back.",
        "tags": ["Iran", "Trump", "Gulf", "Strait of Hormuz", "MOU", "peace deal", "Pakistan", "India", "NRI", "remittances", "oil", "rupee", "Gulf workers", "Saudi Arabia", "UAE", "Qatar"],
        "urgency": "critical",
        "sources": json.dumps([
            {"name": "CNN — Gulf leaders encourage Trump to accept Iran's latest proposal to end the war", "url": "https://www.cnn.com/2026/05/23/middleeast/iran-us-progress-framework-diplomacy-intl"},
            {"name": "Reuters — US and Iran report progress on talks ending war", "url": "https://www.reuters.com/world/us-iran-report-progress-talks-ending-war-2026-05-23/"},
            {"name": "New York Post — Iran war agreement being 'fine-tuned' as Trump meets with Gulf allies", "url": "https://nypost.com/2026/05/23/world-news/iran-war-agreement-being-fine-tuned/"},
            {"name": "Reuters — Analysis: Three months in, is Trump losing the Iran war?", "url": "https://www.reuters.com/world/analysis-three-months-is-trump-losing-iran-war-2026-05-23/"},
            {"name": "Inshorts — NRI deposits fall by nearly ₹19,000 crore in March amid West Asia crisis", "url": "https://inshorts.com/en/news/nri-deposits-fall-by-nearly-19000-crore"}
        ]),
        "score_total": 97,
        "status": "published",
        "published_at": now,
        "body": """Something shifted on Saturday. After three months of war, six weeks of a fragile ceasefire, and weeks of stalled negotiations that seemed to go in circles, the language coming out of Tehran, Islamabad, and Washington changed.

"An MoU is being fine-tuned," a Pakistani security official told Reuters, referring to a memorandum of understanding that would serve as the framework for ending the US-Iran war.

Pakistan's military, which has been mediating between Washington and Tehran, said Field Marshal Asim Munir's 24-hour marathon of talks in Tehran had been "highly productive" and resulted in "encouraging progress towards a final understanding." Iran's foreign ministry said a framework agreement was taking shape with 30- to 60-day timelines for detailed negotiations. And Gulf leaders — from Saudi Arabia, the UAE, Qatar, Jordan, Egypt, Turkey, and Pakistan — got on a call with President Trump and encouraged him to accept.

"The call was very positive. Good progress is being made. Regional leaders were supportive of the progress and of the breakthrough President Trump achieved with the talks," a regional diplomat on the call told CNN.

## What's Actually on the Table

The negotiators have been working through a 14-point plan that addresses the core issues: formally ending hostilities, reopening the Strait of Hormuz, unfreezing Iran's blocked overseas assets, and establishing a framework for further negotiations on the nuclear program and sanctions.

Iran's foreign ministry spokesman Esmail Baghaei laid out Tehran's position clearly. The memorandum would cover ending the war, lifting the US naval blockade, and releasing frozen assets — but not the nuclear program, at least not at this stage. "Since we are not discussing the nuclear issue at this stage, there will be no negotiation on the details of lifting sanctions either," Baghaei said.

That's the sticking point. The US — and especially Israel — wants the nuclear program and Iran's enriched uranium stockpile addressed in any deal. Iran wants to deal with the war first and the nuclear question later. The MOU being "fine-tuned" reportedly threads this needle by establishing a 30- to 60-day window for detailed negotiations on the harder issues after the immediate crisis is resolved.

Israeli Prime Minister Benjamin Netanyahu convened a security consultation Saturday evening, with his main concern being that a narrow interim agreement would reopen the Strait of Hormuz and ease sanctions without addressing enriched uranium. The US has been reassuring Israel on this point, though the details remain unclear.

## Trump's 50/50

Trump, in his characteristic style, is keeping everyone guessing.

"Either we reach a good deal or I'll blow them to a thousand hells," he told Axios in a phone interview Saturday. He described the chances of an agreement as a "solid 50/50" and said he could decide by Sunday whether to resume military strikes. He told CBS he had seen Iran's draft proposal and that both sides were "getting a lot closer."

The contradictions are deliberate. Trump skipped his own son's wedding this weekend, citing Iran as one of the reasons he needed to stay in Washington. Vice President JD Vance was spotted arriving at the White House Saturday. Secretary of State Marco Rubio, who is in India for talks with Prime Minister Modi, told reporters: "Even as I speak to you now, there's some work being done. There is a chance that, whether it's later today, tomorrow, in a couple of days, we may have something to say."

Meanwhile, Republican hawks in the Senate are urging Trump to reject any deal that doesn't fully address the nuclear program. Senator Lindsey Graham warned that allowing Iran to be perceived as a force capable of terrorising the Strait "in perpetuity" would be "a nightmare for Israel." Senator Roger Wicker, chairman of the Armed Services Committee, said the negotiations would "define" Trump's legacy and urged him to "finish what we started."

Iran, for its part, is not backing down either. Chief negotiator Mohammad Bagher Ghalibaf warned that Iran "will not back down from the rights of our nation" and that if Trump restarts the war, "it will definitely be more crushing and bitter for America than the first day."

## Why India Cannot Afford Another Week of This

For India, every day the Strait of Hormuz remains effectively closed is another day of economic bleeding.

The numbers published this week tell the story. NRI deposits in Indian banks fell by nearly ₹19,000 crore ($2 billion) in March alone — from $167.58 billion to $165.65 billion — according to fresh RBI data released Saturday. Annual NRI deposit inflows dropped from $16.16 billion in FY25 to $14.41 billion in FY26. The remittance pipeline that funds entire district economies across Kerala, UP, Bihar, and Rajasthan is drying up.

Foreign investors have pulled $21 billion out of Indian stocks since the war began, with $13 billion leaving in March alone — the fastest pace on record. Bank of America's latest research says the foreign exodus from Indian equities will continue into 2027. The rupee hit a historic low of 97 per dollar in May, driven by oil import costs and a trade deficit that has ballooned to $120 billion.

Over 1.1 million Indians have returned from the Gulf since February, according to government figures. The jobs waiting for them at home are scarce. India's own employment engine is stalling — Gulf remittances are down, AI-driven layoffs are accelerating, and the heatwave is hammering agricultural output.

## The 72-Hour Window

The diplomatic calendar is unusually compressed. The Eid holiday begins soon, which creates a natural deadline — both sides want to reach an understanding before the Islamic world goes on break. Baghaei said "we must wait and see what will happen in the next three to four days."

Trump's decision calculus is being shaped by multiple pressures. Gas prices in the US are near historic highs heading into Memorial Day weekend — a politically toxic combination. His approval ratings have been damaged by the war's economic fallout. The Gulf allies he relies on — Saudi Arabia, the UAE, Qatar — are all telling him the same thing: take the deal.

Against that, the hawks in his own party are warning that a deal that doesn't denuclearise Iran will be seen as capitulation. Israel is lobbying hard to ensure the nuclear program is on the table. And Trump himself has spent three months promising maximum pressure and total victory.

For the Indian diaspora, the outcome is existential. A deal that reopens the Strait of Hormuz and stabilises oil markets would be the single biggest positive shock to India's economy this year. It would restart the Gulf employment machine that supports millions of Indian families. It would take pressure off the rupee, ease inflation, and allow the RBI to cut rates instead of defending the currency.

If Trump walks away and resumes strikes, the opposite happens. Oil spikes higher. The rupee falls further. More Indians come home from the Gulf. And the remittance economy that has been a lifeline for India's poorest states continues to bleed.

Three months of war, ₹19,000 crore in vanished NRI deposits, 1.1 million displaced workers, a currency at record lows. The MOU is being fine-tuned. The Gulf leaders have said take it. Trump says he is 50/50. For millions of Indians on both sides of the Arabian Sea, the next 72 hours are the most consequential since February 28.
"""
    })
else:
    print(f"  ⚠ Skipping Iran deal MOU article — slug already exists: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: India's Financial Hemorrhage — $21B Foreign Exodus, Rupee at 97, NRI Deposits Crashing
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("india-financial-crisis-rupee-97-nri-deposits-foreign-exodus")
if slug2 not in existing_slugs:
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The Rupee Just Hit 97 to the Dollar. Foreign Investors Have Pulled $21 Billion. NRI Deposits Crashed ₹19,000 Crore in a Single Month. Inside India's Quiet Financial Emergency.",
        "subheadline": "Fresh RBI data released Saturday showed NRI deposits fell by nearly $2 billion in March, the steepest monthly decline in over a decade. Bank of America says the foreign investor exodus from Indian equities will not reverse until 2027. The rupee has lost 12 percent of its value in 12 months, hitting an all-time low of 97.15 per dollar. India's trade deficit has swollen to $120 billion. And the government keeps saying everything is fine. For the millions of NRIs who hold savings in Indian banks, send money home to families, or are considering investments in India — this is the story no one in Delhi wants to talk about.",
        "slug": slug2,
        "category": "news",
        "vertical": "economy",
        "diaspora_angle": "This story hits NRIs in three places simultaneously. First, their deposits: the ₹19,000 crore decline means the real value of NRI savings in Indian banks is eroding from both the deposit side (money leaving) and the currency side (rupee falling). NRE and NRO accounts are now worth significantly less in dollar terms than they were a year ago. Second, their remittances: the money NRIs send home to families buys less every month as inflation and the weak rupee eat into purchasing power. Third, their investments: the Sensex is among the worst-performing major indices globally in 2026, and BoA is telling clients the pain will continue into 2027. For NRIs who have been treating India as a safe long-term bet — parking money in FDs, buying property, investing in mutual funds — the ground is shifting under them.",
        "tags": ["rupee", "Indian economy", "NRI deposits", "RBI", "foreign investors", "Bank of America", "trade deficit", "inflation", "oil prices", "Iran war", "Sensex", "FII", "NRE", "NRO", "remittances"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Inshorts — NRI deposits fall by nearly ₹19,000 crore in March amid West Asia crisis", "url": "https://inshorts.com/en/news/nri-deposits-fall-by-nearly-19000-crore"},
            {"name": "Livemint — BofA Sees Foreign Exodus from Indian Stocks Extending Into 2027", "url": "https://www.livemint.com/market/stock-market-news/bofa-sees-foreign-exodus-from-indian-stocks-extending-into-2027"},
            {"name": "Ainvest — Goyal: India doesn't interfere in exchange rate", "url": "https://www.ainvest.com/news/goyal-india-doesnt-interfere-in-exchange-rate"},
            {"name": "Headlines Briefing — India Asset Outflows Surge Amid Currency Crisis", "url": "https://headlinesbriefing.com/india-asset-outflows-surge-amid-currency-crisis"},
            {"name": "The Hindu Business Line — Global uncertainty slows overseas remittances under LRS in FY26", "url": "https://www.thehindubusinessline.com/money-and-banking/global-uncertainty-slows-overseas-remittances-under-lrs"}
        ]),
        "score_total": 92,
        "status": "published",
        "published_at": now,
        "body": """The Reserve Bank of India released its latest bulletin data on Saturday. Buried in the tables, a number that should have been front-page news: outstanding NRI deposits in Indian banks fell by nearly ₹19,000 crore — roughly $2 billion — in a single month. From $167.58 billion at the end of February to $165.65 billion at the end of March.

It is the steepest monthly decline in NRI deposits in over a decade. And it is only one data point in a broader picture of financial stress that India's government has been remarkably reluctant to discuss.

## The Numbers

Start with the currency. The Indian rupee has fallen 12.36 percent against the US dollar over the past 12 months. In May 2026, it hit an all-time low of 97.15 per dollar — a level that would have been unthinkable a year ago, when the currency was trading around 86. The RBI has been intervening aggressively, burning through foreign exchange reserves and announcing a $5 billion dollar-rupee swap auction. The rupee clawed back to around 95.9, but analysts say the reprieve is temporary.

Foreign investors have withdrawn $21 billion from Indian equities since the Iran war began on February 28. In March alone, $13 billion left — the fastest monthly outflow on record. To put that in perspective: India attracted $44 billion in foreign portfolio investment across all of 2023. In three months, nearly half that amount walked out the door.

Bank of America's latest research note, published this week, says the foreign exodus is not close to ending. "It definitely does not look like a 2026 event," the bank's analysts wrote, projecting that foreign investment in Indian stocks will remain negative through 2027. Without a meaningful expansion in earnings growth, India's premium valuations — which were already stretched before the war — will remain under pressure.

India's trade deficit has ballooned to $120 billion, driven primarily by the oil import bill. India imports roughly 85 percent of its crude oil, and with Brent above $100 a barrel since the Strait of Hormuz closure, the arithmetic is punishing. Every $10 increase in oil prices costs India approximately $15 billion a year in additional import costs.

And the annual inflow of NRI deposits — money sent from overseas Indians specifically into bank deposits — fell from $16.16 billion in FY25 to $14.41 billion in FY26. Outward remittances under the Liberalised Remittance Scheme also dipped 2 percent to $28.9 billion, reflecting the uncertainty that the war has injected into every financial decision NRIs make.

## What the Government Is Saying

Union Commerce Minister Piyush Goyal stated this week that "India doesn't interfere in exchange rate." The RBI, meanwhile, has been doing exactly that — intervening in the spot market, conducting swap auctions, and exploring additional measures to attract foreign currency inflows. The contradiction is the point: the government wants to project stability while the central bank fights to prevent a rout.

India's foreign exchange reserves, which peaked at $704 billion in September 2024, have fallen to approximately $610 billion — still substantial, but the pace of decline is concerning. At the current rate of intervention, the reserves provide roughly 9-10 months of import cover, down from nearly 12 months a year ago.

The Sensex is among the worst-performing major indices globally in 2026. After a strong 2024 that saw the index touch 85,000, it has given back most of those gains. The combination of foreign outflows, a weak rupee, compressed earnings, and the energy shock has made India unattractive to the global capital that spent the previous three years pouring money in.

## What This Means for NRIs

For the estimated 32 million Indians living abroad, these numbers translate into real and immediate financial pain.

**Deposits are eroding.** An NRI who held $100,000 in an NRE fixed deposit a year ago has seen its rupee equivalent grow (because the rupee fell), but the underlying dollar value of India-denominated assets has shrunk. More importantly, the ₹19,000 crore monthly decline signals that NRIs as a group are pulling money out — likely repatriating funds to dollar or dirham accounts that feel safer. For Indian banks that depend on NRI deposits as a source of stable foreign currency, this trend is a structural concern, not a blip.

**Remittances buy less.** The money NRIs send home to families — for education, medical bills, elderly care, property — stretches less each month. Inflation in India has been running at 4-5 percent, and the prices of essentials that remittance-dependent families buy (cooking gas, food, fuel) have risen even faster because of the oil shock. A construction worker in Dubai sending ₹25,000 home to his family in Bihar is buying them less food, less medicine, and less security than the same transfer bought six months ago.

**Investment returns have vanished.** NRIs who invested in Indian mutual funds, direct equities, or real estate during the boom years of 2023-24 are sitting on significant paper losses. The Sensex decline has wiped out gains. Property markets in tier-2 cities, which saw a surge of NRI buying in 2023-24, have gone quiet as buyers wait out the uncertainty. Bank of America's forecast of continued foreign outflows through 2027 suggests the equity market will not recover quickly.

## The RBI's Record Dividend — A Band-Aid on a Bullet Wound

One piece of seemingly good news: the RBI transferred a record surplus of ₹2.87 lakh crore to the central government this month. Economists initially cheered, saying it would help the government manage its rising subsidy burden without aggressive borrowing.

But the relief is illusory. The record transfer is partly a consequence of the very crisis it is meant to address — the RBI's aggressive foreign exchange interventions generated trading profits that inflated its surplus. And the structural challenges remain: slowing consumption, fiscal stress, lower-than-expected tax collections, and subsidy requirements that keep rising because oil keeps rising.

"The RBI's surplus transfer may offer only a limited fiscal cushion amid West Asia pressures," economists at The Hindu Business Line wrote. The ₹2.87 lakh crore is large, but it is fighting against a trade deficit that has expanded by multiples of that amount.

## The Deeper Problem

India's financial vulnerability to the Iran war exposes a structural weakness that predates the conflict. The country's dependence on imported energy — 85 percent of crude, a growing share of natural gas — means that any disruption to Middle Eastern oil flows hits India harder than almost any other major economy. China has strategic petroleum reserves that cover months of imports. India's strategic reserve covers roughly 9.5 days.

The remittance dependence tells a similar story. India receives more remittances than any country in the world — over $125 billion in FY25 — but that money comes overwhelmingly from the Gulf, where the war has directly disrupted economies. Kerala alone depends on Gulf remittances for an estimated 36 percent of its state domestic product.

These are not problems that can be solved in the next quarter or the next budget. They are structural features of India's economy that the war has turned into structural vulnerabilities. The rupee at 97, the $21 billion in fleeing foreign capital, the ₹19,000 crore in vanishing NRI deposits — these are symptoms of a deeper condition.

## What Happens Next

The immediate trajectory depends on the Iran deal. If the MOU being negotiated this weekend leads to a reopening of the Strait of Hormuz and a decline in oil prices, India gets a reprieve. The rupee stabilises. Foreign investors reconsider. NRI deposits stop declining.

If the deal collapses and Trump resumes strikes, the trajectory gets worse — potentially much worse. Oil above $120 would push India's trade deficit past $150 billion. The rupee could test 100 per dollar. Foreign investors would accelerate their exit.

But even in the optimistic scenario, the scars of the past three months are real. Foreign capital that left Indian markets does not come back overnight — Bank of America says not until 2027. NRI confidence in Indian deposits has been shaken by the currency collapse. The 1.1 million workers who returned from the Gulf need jobs that India's domestic economy is not generating fast enough.

For NRIs, the lesson is uncomfortable but clear: the "India growth story" that made rupee-denominated assets look attractive for the past decade has been stress-tested by a war that India had no role in starting and no power to stop. The story may ultimately prove durable. But this month's RBI data suggests that a lot of NRIs are no longer willing to bet their savings on it.
"""
    })
else:
    print(f"  ⚠ Skipping India financial crisis article — slug already exists: {slug2}")


# ── Insert articles ──
if articles:
    print(f"\nInserting {len(articles)} articles...")
    for i, article in enumerate(articles, 1):
        try:
            result = sb_post("p2_articles", article)
            print(f"  ✓ Article {i}: {article['headline'][:80]}...")
            print(f"    Slug: {article['slug']}")
            if result:
                print(f"    ID: {result[0]['id'] if isinstance(result, list) else result.get('id', 'ok')}")
        except Exception as e:
            print(f"  ✗ Article {i} FAILED: {e}")
else:
    print("\nNo new articles to insert (all duplicates).")

print("\nDone.")
