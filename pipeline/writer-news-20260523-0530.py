#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 05:30 batch
Topics: Kevin Warsh as new Fed Chair + India impact; SEBI finfluencer crackdown
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
# ARTICLE 1: Kevin Warsh — New Fed Chair and India's Reckoning
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "The New Federal Reserve Chair Was Sworn In at the White House, Not the Fed. That Tells You Everything About What Comes Next — and Why India Should Be Worried.",
    "subheadline": "Kevin Warsh took over the world's most powerful central bank on Friday after a 54-45 Senate confirmation — the most divisive in Fed history. He inherits 3.8% inflation, a president who wants rate cuts, and an FOMC that is leaning toward hikes. For India, already bleeding $22 billion in foreign capital and watching the rupee slide toward ₹97, the Warsh era could force the RBI into its first rate hike in years.",
    "slug": make_slug("kevin-warsh-fed-chair-india-rbi-rupee-nri"),
    "category": "news",
    "vertical": "economy",
    "diaspora_angle": "For NRIs, the Warsh appointment is a double squeeze. US mortgage rates just hit 6.51% — the highest since August 2025 — making American homeownership more expensive. Meanwhile, a stronger dollar erodes the rupee value of remittances sent home, and the RBI may be forced to hike rates, increasing EMI costs for families back in India. NRI investors face the worst of both worlds: expensive borrowing in the US and declining returns on Indian equity portfolios.",
    "tags": ["Kevin Warsh", "Federal Reserve", "India", "RBI", "rupee", "FPI outflows", "interest rates", "NRI", "economy", "inflation", "mortgage rates", "markets"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters — Warsh elected chair of U.S. Fed's rate-setting committee", "url": "https://www.reuters.com/business/finance/warsh-elected-chair-us-feds-rate-setting-committee-2026-05-22/"},
        {"name": "Livemint — India weighs rate hike to steady the rupee", "url": "https://www.livemint.com/economy/india-weighs-rate-hike-to-steady-the-rupee-11779346047297.html"},
        {"name": "PaisaKawach — Weekend Global & India Briefing, May 23, 2026", "url": "https://paisakawach.com/news/new-fed-chair-iran-talks-india-markets-weekly-briefing-may-23-2026"},
        {"name": "Realtor.com — Kevin Warsh Is the New Fed Chair. Here's What It Means for Mortgage Rates and Housing", "url": "https://www.realtor.com/research/kevin-warsh-fed-chair-housing-mortgage-rates/"}
    ]),
    "score_total": 93,
    "status": "published",
    "published_at": now,
    "body": """The ceremony told you everything you needed to know before a single word was spoken. Kevin Warsh was sworn in as the 17th Chair of the Federal Reserve on Friday — not at the Fed's headquarters on Constitution Avenue, but in the East Room of the White House, with President Donald Trump presiding and Justice Clarence Thomas administering the oath. His wife, Jane Lauder, held the Bible. The optics were unmistakable: this is the president's man at the Fed.

Trump's remarks were carefully constructed to suggest otherwise. "I want Kevin to be totally independent," he said. "Don't look at me, don't look at anybody, just do your own thing and do a great job." Hours later, at a rally, the same president told supporters that interest rates would come down "very quickly."

The contradiction is not accidental. It is the defining tension of the Warsh era, and its consequences will ripple from Wall Street to Dalal Street, from American mortgage markets to Indian household budgets.

## The Most Divisive Appointment in Fed History

The Senate confirmed Warsh on May 13 by a vote of 54-45 — the narrowest margin for any Fed chair in the institution's 113-year history. The only Democrat to cross the aisle was Senator John Fetterman of Pennsylvania. The vote was a referendum not on Warsh's qualifications — he served as a Fed governor from 2006 to 2011 and was an inflation hawk during the financial crisis — but on his perceived willingness to bend to presidential pressure.

During his confirmation hearings, Warsh was repeatedly questioned about his shift from hawk to dove. As governor, he had dissented against quantitative easing. As nominee, he signalled openness to rate cuts that the data did not support. The inconsistency itself was not disqualifying — good central bankers adjust to conditions. What alarmed senators was the timing: the shift coincided precisely with what the president wanted to hear.

Jerome Powell, whom Warsh replaces, will remain on the Federal Open Market Committee as a rank-and-file governor — an almost unprecedented arrangement driven partly by a Justice Department investigation into expensive Fed office renovations that Powell viewed as politically motivated. Powell is an institutionalist who has said privately that he would not have stayed unless he believed the Fed's independence needed safeguarding.

## The Economy He Inherits

When Trump nominated Warsh in January, the economic picture was benign: inflation was near the Fed's 2% target, rate cuts were widely expected, and AI-driven optimism was propelling markets to records. Five months later, the landscape has inverted.

Headline CPI inflation has climbed to 3.8%. Gasoline prices have surged 21.2% since the Iran war began, dragging consumer prices higher across the board. The 30-year Treasury yield has hit 5.08% — a 19-year high. Mortgage rates have reached 6.51%, up 53 basis points in just 12 weeks. Money markets have fully priced in at least one rate hike in 2026, a complete reversal from the rate cuts that were expected at the start of the year.

Real wage growth — the gains that actually matter to households — has been effectively erased by the combined impact of the Iran oil shock and trade tariffs. The labour market remains stable, which is the one genuinely positive signal in the data. But stable employment with rising inflation is precisely the scenario that argues for holding rates steady or hiking — not cutting.

Warsh's first FOMC meeting is in three weeks. Governor Christopher Waller said this week that the Fed should "no longer signal cuts" and that the next move is "just as likely to be a raise as a cut." Three FOMC members logged soft dissents at the last meeting in favour of future hikes — a deliberate signal, placed on the record before Warsh arrived, that the committee's views are data-driven rather than political.

## Why India Is in the Crosshairs

For India, the Warsh appointment lands at the worst possible moment. Foreign portfolio investors have pulled $22.2 billion from Indian equities in under three months — exceeding the full-year record set in 2025. The rupee has plunged to nearly ₹97 against the dollar, shedding more than 10% of its value in 12 months. The Sensex managed a paltry 0.2% gain last week while the Dow hit an all-time record of 50,579.

The Reserve Bank of India is now openly considering a rate hike for the first time in years. Livemint reported this week that RBI Governor Sanjay Malhotra has held a series of internal meetings to discuss emergency measures after the rupee hit fresh lows. Options on the table include raising the repo rate from its current 5.25%, launching a non-resident Indian deposit scheme to attract dollars (the RBI estimates this could draw up to $50 billion), and selling sovereign dollar bonds.

The mechanisms are straightforward but punishing. A Warsh-led Fed that holds rates steady — let alone hikes — keeps the dollar strong. A strong dollar weakens the rupee. A weak rupee makes India's oil imports more expensive (India imports over 85% of its crude). Expensive oil widens the current account deficit. A wider deficit requires more foreign capital inflows to finance — but those inflows are leaving, not arriving.

The RBI's response to this spiral would almost certainly be to raise its own rates. Higher Indian rates would increase EMI costs for every household with a floating-rate loan — home loans, car loans, personal credit. Emkay Global's strategy team estimated that a ₹10-per-litre fuel price increase (which the government has so far absorbed but cannot indefinitely) could push India's CPI inflation to 4.4% by June, above the RBI's comfort zone.

## The NRI Squeeze

For the 4.4 million Indian Americans, the Warsh era creates a double bind with no easy escape.

On the American side, mortgage rates at 6.51% are the highest since August 2025. For NRIs looking to buy homes in the US — a common aspiration and investment strategy — borrowing costs have jumped significantly in just three months. Realtor.com analysis noted that "the most durable path to housing affordability is not a rate cut when the data isn't calling for one" but rather a Fed that earns the market's trust through inflation control. That is a multi-quarter project at best.

On the Indian side, the rupee's decline means remittances sent home buy more in rupee terms — a short-term silver lining that many NRI families are taking advantage of. But it also means Indian equity portfolios held by NRIs have lost value in dollar terms. The Sensex may be roughly flat in rupee terms, but in dollar terms it is down double digits for the year. NRIs with mutual fund SIPs, direct equity holdings, or real estate investments in India are watching their wealth erode when measured in the currency they earn.

The most exposed group is NRIs who earn in dollars, have EMIs in India, and invest in Indian equities — a profile that describes a significant portion of the diaspora's professional class. They face rising borrowing costs on both sides of the ocean simultaneously.

## What Warsh Does Next Matters More Than What He Says

The next three weeks will reveal whether Warsh is the independent, data-driven chair he claims to be or the rate-cutting ally the president clearly wants. His first FOMC meeting in June is not just a policy decision — it is a credibility test that will set the tone for his entire tenure.

If Warsh holds rates steady and signals that future decisions will be guided by data, bond markets may begin to price out the worst-case scenarios. Long-term yields could stabilise. Mortgage rates might plateau. The rupee's slide could slow as the dollar's trajectory becomes more predictable.

If he signals cuts — or even ambiguity about cuts — in the face of 3.8% inflation, the consequences could be severe. Markets would price in higher long-term inflation, pushing Treasury yields and mortgage rates higher. The dollar could initially weaken but then strengthen as investors flee to safety. And India's RBI would face even more pressure to hike, deepening the domestic slowdown.

"A chair that is not data-dependent cannot be independent," as one analyst put it. "Those are not two separate qualities. They are the same quality."

For India and its diaspora, the answer to that question is worth $22 billion and counting."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: SEBI Finfluencer Crackdown — The Gupta Family Scheme
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "A Mumbai Family Ran a ₹20-Crore Stock Scam on Telegram and WhatsApp. SEBI Just Froze Everything They Own.",
    "subheadline": "Seven members of the Gupta family — a father, his wife, his ex-wife, and four children — allegedly ran pump-and-dump operations across 82 small-cap stocks using X, Telegram, and WhatsApp accounts with tens of thousands of followers. SEBI's 234-page order details a textbook scheme that exploited the same platforms millions of NRIs use to manage their Indian investments.",
    "slug": make_slug("sebi-gupta-family-finfluencer-pump-dump-telegram"),
    "category": "markets-finance",
    "vertical": "regulation",
    "diaspora_angle": "The SEBI crackdown is a direct warning to NRI investors who follow Indian stock tips on social media. Many NRIs invest in Indian equities through discount brokers like Zerodha and Groww, and follow finfluencer accounts on Telegram, WhatsApp, and X for stock picks. The Gupta family's scheme specifically targeted the kind of low-liquidity SME stocks that retail investors — including NRIs — are drawn to for high-return potential. If you follow stock tip channels, this case is a blueprint for how you can be exploited.",
    "tags": ["SEBI", "finfluencer", "pump and dump", "Telegram", "WhatsApp", "SME stocks", "stock market", "regulation", "NRI investors", "India", "retail investors", "fraud"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters — India regulator cracks down on seven in social media stock manipulation case", "url": "https://www.reuters.com/article/india-regulator-stock-manipulation/india-regulator-cracks-down-on-seven-in-social-media-stock-manipulation-case-idUSL1N3OA0ZH"},
        {"name": "The Hindu Business Line — SEBI bars seven family members in social media stock recommendation case", "url": "https://www.thehindubusinessline.com/markets/sebi-bars-seven-family-members-in-social-media-stock-recommendation-case-alleges-2025-cr-illegal-gains/article71011972.ece"},
        {"name": "Livemint — Sebi bars 7 entities over stock manipulation, freezes ₹20 crore gains", "url": "https://www.livemint.com/market/stock-market-news/sebi-bars-7-entities-over-stock-manipulation-freezes-20-crore-gains-11747946410989.html"},
        {"name": "Inshorts — How did a family in Mumbai turn tips on Telegram & WhatsApp into a ₹20-crore scam?", "url": "https://inshorts.com/en/news/how-did-a-family-in-mumbai-turn-tips-on-telegram-whatsapp-into-a-20crore-scam-1747982581131"}
    ]),
    "score_total": 86,
    "status": "published",
    "published_at": now,
    "body": """The scheme was elegant in its simplicity and devastating in its reach. A family in Mumbai — father, sons, wife, ex-wife, and a daughter — built a network of social media accounts with tens of thousands of followers, used those accounts to pump low-liquidity stocks they had already bought, and then sold into the buying frenzy they had manufactured. They did this 537 times across 82 companies over two years. SEBI says they made ₹20.25 crore ($2.1 million) in the process.

On Friday, the Securities and Exchange Board of India dropped a 234-page order that reads like a forensic autopsy of India's finfluencer economy. Seven members of the Gupta family have been barred from the securities market. Their bank accounts have been frozen. And the case has become the most detailed public documentation of how social media stock manipulation actually works in India — a country where 14 crore retail investors now trade stocks, many of them guided by tips from anonymous accounts on Telegram and WhatsApp.

## How the Scheme Worked

The architecture was a classic pump-and-dump, executed with the tools of the smartphone age.

Hemant Gupta was the patriarch. His sons Rohan and Aniket were the operators — the ones who ran the social media accounts and managed the trading. The family's other members — Sharon, Leana, Rajani, and Purvangi Gupta — held trading accounts that served as "beneficiaries," receiving and liquidating the stocks the operators had pumped.

Rohan Gupta operated an X (formerly Twitter) account called @WealthSolitaire with approximately 13,600 followers. Aniket Gupta ran @desiwallstreet, which had about 40,500 followers. Between them, the family also operated several WhatsApp groups and Telegram channels with thousands of subscribers — the kind of stock-tip groups that have proliferated across India's retail investing landscape since the pandemic-era trading boom.

The playbook was the same every time. First, the family would quietly accumulate shares of a small or micro-cap company — typically an SME-listed stock with low trading volumes, where even modest buying pressure can move the price. These are the stocks that retail investors are drawn to for their potential to deliver quick, outsized returns.

Once their positions were built, the operators would launch a coordinated social media campaign. Rohan and Aniket would post "buy" recommendations on X, praising the company's fundamentals, projecting strong returns, and creating urgency. Simultaneously, the same tips would be pushed to WhatsApp groups and Telegram channels. The posts were designed to look like independent research — the kind of conviction-driven stock picks that finfluencers have made their brand.

As retail investors responded to the tips and began buying, the stock price would rise. At that point, the family members holding the shares — the "beneficiaries" — would sell into the artificial demand, locking in profits before the price inevitably collapsed back to reality.

SEBI's analysis showed that the family's combined gross trade value nearly doubled during the examination period — from ₹548 crore to ₹1,023 crore. Their combined squared-off profits rose from ₹17 crore to ₹58 crore. The alleged unlawful gains of ₹20.25 crore represent the portion SEBI could directly attribute to the pump-and-dump coordination across the 82 stocks, though the final figure may change after the investigation concludes.

## The Raid

SEBI had been watching. In January 2026, after obtaining court approval, the regulator carried out search and seizure operations at the Gupta family's premises. Electronic devices were confiscated. Chat records were extracted. Trading data was cross-referenced with social media posting timestamps.

The evidence was damning. SEBI found that stock recommendations posted on @WealthSolitaire and @desiwallstreet correlated precisely with buying activity in the family's trading accounts in the days before — and selling activity in the days after. The pattern repeated across dozens of stocks and hundreds of posts.

In one detailed example involving Afcom Holdings, an SME-listed company, SEBI traced how the family accumulated shares over several days, then launched a Telegram and X campaign praising the company and projecting strong returns. As retail investors piled in, the price rose. The family sold. The stock subsequently fell back.

"The Operators by posting stock recommendations on various scrips on their X Accounts and social media platforms induced the general public to deal in the securities purely based on misleading and unsolicited stock tips and thus enabling the beneficiaries to liquidate their holdings at an inflated price," SEBI said in the order.

## Why This Matters for NRI Investors

The Gupta family scheme is not an outlier. It is a template — and it targets exactly the kind of investor that many NRIs have become.

Since the pandemic, millions of Indians — both in India and abroad — have opened discount brokerage accounts with platforms like Zerodha, Groww, and Upstox. Many NRIs use these platforms to invest in Indian equities while working overseas, drawn by India's growth story and the familiarity of Indian markets. And many of these investors supplement their own research with stock tips from social media — X accounts, Telegram channels, WhatsApp groups, and YouTube finfluencers.

The problem is structural. India's SME exchange has grown explosively — IPO activity has boomed, and small-cap stocks have delivered spectacular returns for early investors. But the same low liquidity that creates the potential for outsized gains also creates the vulnerability to manipulation. A stock that trades ₹5-10 lakh per day can be moved significantly by a few hundred investors acting on a finfluencer's recommendation. That is exactly what the Gupta family exploited.

SEBI has been tightening the regulatory noose around finfluencers for years. In 2023, it banned registered investment advisers from associating with finfluencers. In 2024, it proposed rules requiring all individuals offering stock advice on social media to register as research analysts. The Gupta case is the most aggressive enforcement action yet — a family-wide ban, asset freezes, and a 234-page order that names specific X handles, Telegram channels, and trading patterns.

## The Bigger Picture

India now has approximately 14 crore (140 million) demat accounts — up from roughly 4 crore before the pandemic. The retail investor base has quadrupled in five years. But the regulatory infrastructure, disclosure requirements, and investor protection mechanisms have not kept pace.

The rise of finfluencers is a symptom of this gap. When traditional financial media and registered advisers cannot reach the millions of new investors entering the market through their phones, that vacuum gets filled by anonymous accounts on Telegram and X. Some of these accounts provide genuine analysis. Many do not. And the line between the two is invisible to the retail investor following a tip at midnight.

The Gupta family case will not be the last. SEBI's order explicitly notes that this is an interim order during the pendency of investigation — meaning the full enforcement action is still ahead. And the ₹20.25 crore in impounded gains, while headline-grabbing, is almost certainly a fraction of the total damage inflicted on the retail investors who bought the stocks the family was dumping.

For NRI investors managing Indian portfolios from abroad, the lesson is both simple and worth repeating: if a stock tip comes from an anonymous social media account, the person giving the tip has almost certainly already bought the stock — and is waiting for you to buy it so they can sell. The tip is not advice. It is the exit strategy."""
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
