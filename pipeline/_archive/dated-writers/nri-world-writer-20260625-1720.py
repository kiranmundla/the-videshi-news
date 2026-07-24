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

art1_body = """For years, the standard advice to a non-resident Indian was simple: send money home, keep an NRE account for emergencies, and treat India as the place your parents live rather than the place your portfolio does. That arrangement is quietly coming apart, and the Reserve Bank of India is the one prising it open.

This month the central bank rolled out a scheme aimed squarely at the diaspora's wallet. To shore up a weakening rupee, the RBI is offering to absorb the cost of hedging foreign-currency deposits parked with Indian banks for three to five years. In plain terms, an overseas Indian can now earn Indian-level interest without taking on the currency risk that has historically made such deposits a gamble. Banks, scenting opportunity, have pushed rates on these foreign currency non-resident (FCNR) deposits to roughly 6 to 7 percent, well above what a dollar saver earns in New York or Dubai.

## The numbers banks are chasing

The estimates being floated are large enough to explain the enthusiasm. Nomura reckons the scheme could pull in about $55 billion, with the bulk arriving in August and September. Axis Bank is more bullish still, sketching scope for around $100 billion. This is not the first time Delhi has reached for the diaspora in a pinch — a near-identical move in 2013 helped steady the rupee during the taper tantrum — but the mechanics this time are more generous.

The RBI has also told domestic lenders they may extend loans to non-residents against those same foreign-currency deposits, including through offshore branches and units in Gujarat's tax-neutral GIFT City. With that leverage layered on, Macquarie analysts estimate returns could approach 12 percent; Axis suggests 15 percent at higher gearing. For a diaspora that has spent a decade watching the rupee slide from 60 to the dollar toward 90, a hedged, leveraged, double-digit return on home soil is a genuinely new proposition.

## From remittance to allocation

The deposit scheme is the loud headline, but a quieter shift sits underneath it. NRI-focused platforms report that overseas Indians are increasingly treating India as a portfolio allocation, not a sentimental obligation. Belong, a GIFT City-based wealth platform, said investment inflows doubled to $6 million in March-April from $3 million in the prior two months, with the strongest demand from the UAE and Qatar. Most of that, the company stressed, was fresh capital remitted from abroad — not idle savings already sitting in Indian accounts being shuffled around.

"Historically, the conversation was around sending money to India or maintaining assets in India for personal reasons," said Ankur Choudhary, Belong's co-founder. "Today, more NRIs are approaching India as an investment destination and thinking about portfolio allocation rather than remittances alone." On his platform, USD fixed deposits remain the favourite, but India-focused mutual funds run out of GIFT City now account for roughly a fifth of inflows, with average mutual-fund tickets around $5,000 earmarked for retirement and children's education.

## Why it matters to the diaspora

The appeal is partly emotional and partly arithmetic. Many NRIs already hold heavy exposure to American or Gulf markets through their day jobs and pensions; India has been the gap in the portfolio, hard to access cleanly without tax headaches or paperwork that defeats the patient. GIFT City, operating under offshore banking rules, is meant to be the clean pipe — a way to hold India-linked assets inside a globally recognised, tax-efficient wrapper rather than wrestling with domestic KYC from six time zones away.

The caveats are real. GIFT City is not yet Singapore or Dubai; its ecosystem of banks, asset managers and insurers is still maturing, and real-estate-linked returns there remain a long-game bet rather than quick yield. The FCNR scheme, for all its sweeteners, is a currency-defence tool first and a diaspora gift second — the government wants the dollars more than it wants to enrich savers, and schemes built to plug a rupee hole can be withdrawn once the hole closes.

Still, the direction is unmistakable. A diaspora long courted for its remittances and its sentiment is now being courted for its capital, on terms designed to compete with the financial centres where it actually lives. For the overseas Indian deciding where the next $20,000 goes, home has, for once, made itself a serious bid."""

art2_body = """Timed to the United States' approaching 250th birthday, Forbes has published its inaugural "Forbes 250: America's Most Successful Immigrants," a roll call of living arrivals who reshaped American enterprise. Twenty-six of the names are of Indian origin — a single community supplying more than a tenth of the entire list, and a useful reminder of how thoroughly the diaspora has woven itself into the upper reaches of American business.

The marquee names are the ones the diaspora already recites at dinner tables: Microsoft chief executive Satya Nadella, Alphabet and Google boss Sundar Pichai, IBM's Arvind Krishna and Adobe's Shantanu Narayen. Together they run companies whose combined market value runs into the trillions, and whose products sit on nearly every desk and phone on the planet.

## Beyond the four CEOs

What gives the list its texture is the names below the headline. Cybersecurity figure Jay Chaudhry of Zscaler appears alongside Palo Alto Networks chief Nikesh Arora. Venture capital is thick with Indian names — Vinod Khosla, who co-founded Sun Microsystems before becoming one of Silicon Valley's most influential investors; Hemant Taneja of General Catalyst, a backer of Stripe and Snap; AngelList co-founder Naval Ravikant, an early bettor on Uber and Twitter.

The roster runs wider than tech, too. Former PepsiCo chair Indra Nooyi makes it, as does Nobel-winning economist Abhijit Banerjee, author and television personality Padma Lakshmi, and aviation entrepreneur Rakesh Gangwal, who co-founded IndiGo. Semiconductor leaders Sanjay Mehrotra of Micron — earlier the founder of SanDisk — and Jitendra Mohan sit beside Toast co-founder Aman Narang, clean-energy pioneer K.R. Sridhar of Bloom Energy, and Kiva co-founder Premal Shah. Data-infrastructure figure Neha Narkhede and software entrepreneur Jyoti Bansal round out a list that spans semiconductors, hospitality technology, investment management and public-policy research.

## A familiar arc

Strip away the corporate titles and the biographies rhyme. Khosla arrived in 1976; Nadella in the late 1980s; Pichai in the early 1990s on the way to a Stanford graduate programme. Most came as students or early-career engineers, carried little beyond a degree and a plane ticket, and built their fortunes inside a single working lifetime. It is the diaspora's foundational story — the one parents tell children to explain why the family left — rendered in Forbes' clinical bullet points.

That arc is also why the list lands differently inside the community than outside it. For the broader American reader, it is a tidy immigration-pride story ahead of a national anniversary. For an Indian-American family, it is a scoreboard with personal stakes: proof that the path from an IIT lecture hall or a small-town engineering college to the corner office is not a fluke but a pattern, and a quiet argument in every dinner-table debate about whether the children should chase the safe profession or the risky founder's road.

## The thing the list can't measure

There is an unspoken tension in celebrating a list like this. The same week Forbes was toasting immigrant achievement, Indian-American lawmakers were on Capitol Hill warning the community about a rise in anti-Indian sentiment, and a British MP was making headlines for saying Indians were taking local jobs. The diaspora's visibility at the top of the economy is precisely what makes it a target lower down; success and backlash have a way of arriving together.

A list of 26 chief executives and investors also flattens the diaspora into its most flattering silhouette. It says nothing of the H-1B engineer waiting two decades for a green card, the Gulf construction worker remitting his wages, or the small-business owner running a motel or a pharmacy — the far larger population on whose backs the headline names are, statistically, the outliers.

Read generously, though, the list is less a trophy than a map. It marks where the diaspora has reached, and it quietly raises the question of where it has not — the boardrooms it has cracked versus the elected offices, museums and cultural institutions where its presence remains thin. The names on the page are an achievement. They are also, for a community fond of measuring itself, an instruction to keep climbing."""

art3_body = """For the Indian professional posted to London on a multi-year assignment, one line on the payslip has long stung more than the rest: a national insurance deduction of around 12 percent, paid into a British social-security system whose pension they will almost certainly never draw, while often still contributing to India's own. From 15 July, that double charge begins to fall away — and the diaspora, not the headlines about tariffs, may be the quiet winner of the new India-UK trade pact.

India's commerce minister Piyush Goyal travelled to London this week, from 25 to 27 June, for talks ahead of the rollout of the India-UK Comprehensive Economic and Trade Agreement (CETA) and its companion Double Contribution Convention (DCC), both of which take effect on 15 July. He is meeting Britain's business and trade secretary Peter Kyle to iron out implementation — tariff cuts, customs facilitation — but for the community abroad the DCC is the clause that matters at the kitchen-table level.

## What the Double Contribution Convention actually does

Under the DCC, Indian workers temporarily posted to the UK, and their employers, are exempted from paying UK social-security contributions for up to three years, provided they keep contributing in India. The reverse applies to Britons posted to India. It ends the absurdity of paying twice into two systems for a benefit collected from neither.

The sums are not trivial. For a software engineer, consultant or finance professional on a typical expatriate package, the saving can run to several thousand pounds a year, and far more for the employer matching the contribution. India's IT and professional-services firms, which rotate thousands of staff through British client sites, have lobbied for exactly this for years; New Delhi treated it as a red line in the CETA negotiations precisely because the diaspora's mobility is one of India's chief exports.

## A deal aimed at people, not just goods

Most trade agreements are about widgets and whisky. This one has an unusually human core. Alongside the DCC, the two sides have been negotiating market access in services and "mechanisms to ease the mobility of professionals" — diplomatic language for making it simpler for Indians to work in Britain and bill clients there without bureaucratic friction.

That focus reflects a basic truth about the corridor. The India-UK relationship is carried less by cargo ships than by people: the 1.9-million-strong Indian-origin population already in Britain, the students who arrive each autumn, and the rotating cohort of professionals on assignment. Goyal underlined the point by addressing the India Global Forum in London on the theme "Capital, Innovation and the UK-India Moment," and by lining up meetings with HSBC and Rolls-Royce — institutions that move money and people across the corridor as much as products.

## The shadow over the celebration

The timing is awkward in one respect. The trade pact's people-first framing arrives just as Britain's politics around immigration has turned sharp. A British MP recently drew outrage for claiming the country should stop "importing millions of Pakistanis and Indians," and Indian-American lawmakers across the Atlantic have warned of rising anti-Indian sentiment. A treaty that makes it cheaper and easier for Indian professionals to work in Britain is, to some domestic audiences, exactly the wrong signal — and the diaspora knows that visibility and resentment often travel together.

There are practical limits, too. The DCC covers posted workers on temporary assignment, not the broader population of settled migrants or those on standard work visas, and the three-year window means longer postings eventually revert to the old rules. The convention eases the cost of mobility; it does not rewrite Britain's immigration settlement.

For the engineer in Canary Wharf or the consultant rotating between Mumbai and Manchester, though, the change is concrete in a way that trade statistics rarely are. From the middle of July, the money that vanished into a pension they would never see comes home instead. In a relationship long described in the grand language of strategic partnership, the diaspora's reward is refreshingly small and specific: a fatter payslip, and one less reason to feel like a guest paying for a club they can't join."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Delhi Spent Years Wanting the Diaspora's Remittances. Now It Wants Its Portfolio.",
        "subheadline": "A new RBI deposit scheme and the rise of GIFT City are reframing overseas Indians from senders of money home into investors in India — on terms built to compete with Dubai and New York.",
        "slug": make_slug("rbi-fcnr-deposit-scheme-gift-city-nri-investment-shift-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Overseas Indians are being courted with hedged, leveraged double-digit returns and tax-efficient GIFT City products that let them treat India as a serious portfolio allocation rather than just a place to send remittances.",
        "tags": ["nri", "diaspora", "gift-city", "fcnr", "rbi", "nri-investment", "remittances"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — India File: Rupee gets diaspora lifeline", "url": "https://www.reuters.com/world/india/"},
            {"name": "Reuters — RBI to allow loans against overseas FX deposits", "url": "https://www.reuters.com/world/india/"},
            {"name": "The Hindu BusinessLine — Belong reports 2x jump in NRI inflows via GIFT City", "url": "https://www.thehindubusinessline.com/"},
            {"name": "Bar & Bench — GIFT City 2026: India's rising magnet for NRI investments", "url": "https://www.barandbench.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Gujarat_International_Finance_Tec-City%2C_Gujarat_382355%2C_India_-_panoramio.jpg",
        "image_caption": "Gujarat International Finance Tec-City (GIFT City), India's tax-neutral financial hub courting NRI capital",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Forbes Named America's 250 Most Successful Immigrants. Twenty-Six Are Indian.",
        "subheadline": "Timed to the US's 250th anniversary, the list reads like a diaspora scoreboard — and quietly maps both how far Indian-Americans have climbed and where they still haven't.",
        "slug": make_slug("forbes-250-immigrants-26-indian-origin-leaders-diaspora-nadella-pichai"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Forbes immigrant list is a measure of how thoroughly the Indian diaspora has woven itself into the top of the American economy — and an instruction, for a community fond of measuring itself, on the boardrooms and offices it still hasn't cracked.",
        "tags": ["nri", "diaspora", "indian-american", "forbes", "satya-nadella", "sundar-pichai", "achievement"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "India-West — Forbes 2026 Honors 26 Indian-Origin Leaders", "url": "https://www.indiawest.com/"},
            {"name": "InduQin — 26 Indian Americans Honored on Forbes' Landmark Immigrant List", "url": "https://induqin.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Microsoft CEO Satya Nadella, one of 26 Indian-origin leaders on the inaugural Forbes 250 immigrants list",
        "image_attribution": "Wikimedia Commons",
        "body": art2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Quiet Clause in the India-UK Trade Deal That Puts Money Back in Diaspora Payslips",
        "subheadline": "From 15 July, a Double Contribution Convention ends the double social-security charge on Indian professionals posted to Britain — the human core of a deal usually sold on tariffs.",
        "slug": make_slug("india-uk-ceta-double-contribution-convention-diaspora-professionals-goyal"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For the thousands of Indian professionals rotated through British client sites, the Double Contribution Convention ends years of paying into a UK pension they would never collect — a small, specific win for the diaspora inside a sweeping trade pact.",
        "tags": ["nri", "diaspora", "india-uk", "ceta", "double-taxation", "social-security", "uk-indians"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — India's Goyal to visit UK ahead of trade deal implementation", "url": "https://www.reuters.com/world/india/"},
            {"name": "The Indian Awaaz — Piyush Goyal to Visit United Kingdom from 25-27 June", "url": "https://theindianawaaz.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/63/Piyush_Goyal_crop.jpg",
        "image_caption": "Indian Commerce Minister Piyush Goyal, in London for talks ahead of the India-UK trade pact rollout",
        "image_attribution": "Wikimedia Commons",
        "body": art3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   word count {art['slug']}: {wc}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
