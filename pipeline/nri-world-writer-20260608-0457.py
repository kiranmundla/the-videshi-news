#!/usr/bin/env python3
"""NRI World writer — 2026-06-08 04:57 PDT run. Two articles."""

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


# ─── ARTICLE 1 ───────────────────────────────────────────────────────────────

art1_body = """The Reserve Bank of India made an unusual offer last Friday: it would pick up the tab on one of the most tedious costs in cross-border banking, and it wanted NRI depositors to notice.

Governor Sanjay Malhotra announced during the June 5 monetary policy statement that the RBI will absorb the full hedging cost on fresh three-to-five-year Foreign Currency Non-Resident (Bank) deposits — known in banking shorthand as FCNR(B) — mobilised by Indian banks until September 30, 2026. The scheme also exempts these deposits from cash reserve ratio and statutory liquidity ratio requirements, effectively removing two layers of friction that have historically made FCNR deposits expensive for banks to chase.

## What the scheme actually means

The mechanics are worth understanding, because they explain why bankers are calling this a "game-changer."

When an NRI in, say, Houston deposits dollars into an FCNR(B) account with State Bank of India, the bank converts those dollars to rupees to lend domestically. At maturity, it must repay in dollars — which means it needs to lock in a forward exchange rate through a swap contract the day the deposit arrives. That swap has a cost: roughly 3 to 3.5 per cent per annum at current rates, according to Anshul Chandak, Head of Treasury at RBL Bank. Add the interest rate the bank promises the depositor, and the all-in cost can exceed 7 per cent — hardly attractive when domestic term deposits cost less.

By absorbing that hedging bill, the RBI cuts the bank's cost to just the deposit interest rate. The saving, in theory, gets passed on to NRI depositors as higher rates. "This will enable banks to increase deposit rates for non-resident and OCI depositors," Malhotra said at the post-policy press conference.

## The numbers Delhi is chasing

The FCNR scheme is one piece of a coordinated Centre-RBI package unveiled the same day. The government issued an ordinance scrapping capital gains tax for foreign portfolio investors on government bond interest and trading gains, effective retroactively from April 1. The RBI separately offered concessional forex swaps for state-owned companies raising overseas borrowings.

The combined goal: bridge a $40–50 billion gap in India's balance of payments for fiscal year 2027. Sakshi Gupta, principal economist at HDFC Bank, called the target realistic. YES Bank and Emkay Global pegged potential inflows even higher, at $40–60 billion. SBI's managing director Ashwini Kumar Tewari told CNBC-TV18 that his bank alone expects upwards of $10 billion through the FCNR route and plans to "go all out" marketing to NRI customers in the Gulf, the United States, and Europe.

## Why NRIs should pay attention

The context is unambiguous. Since the US-Iran conflict escalated on February 28, 2026, the rupee has depreciated over 5 per cent and touched a record low of 96.83 against the dollar on May 20. In the full fiscal year ending March 2026, the currency fell over 11 per cent. Capital outflows from Indian equities have hit record levels. Credit growth continues to outpace deposit growth — 16.1 per cent versus 12.2 per cent in the latest fortnightly data — leaving banks starved for stable funding.

For NRIs, the practical upshot is simple: Indian banks are about to compete aggressively for your dollars, pounds, and dirhams. FCNR(B) deposits already offer the advantage of zero exchange-rate risk for the depositor — you deposit in foreign currency and receive your principal plus interest in the same currency at maturity. With the RBI subsidising the bank's hedge, the interest rates on offer should improve meaningfully over the next four months.

There are caveats. The scheme runs only until September 30, so the window is narrow. Final guidelines are still being drafted. And the benefit depends entirely on what individual banks choose to offer — the RBI has created the incentive, not mandated the rate.

## A precedent that worked

This is not the first time Delhi has reached into the NRI deposit toolkit during a currency crisis. In 2013, when the rupee was in freefall, the RBI offered a similar FCNR(B) hedging facility. Banks raised over $26 billion, stabilising the currency and rebuilding reserves. The playbook worked then. Whether it works at a larger scale now, against a more turbulent global backdrop, is the trillion-rupee question.

"With the RBI shouldering the hedging costs at roughly 2.5 per cent annually for the contract period, a successful deposit drive should largely alleviate constraints faced on the domestic deposit mobilisation front too," wrote Soumya Kanti Ghosh, group chief economic adviser at SBI, in a research note. He added that the effect should have a "sobering effect" on loan pricing and market-based yields — meaning cheaper credit for Indian borrowers, funded in part by diaspora savings.

For the 35 million-strong Indian diaspora, this is one of those rare moments when the macroeconomic plumbing directly touches personal finance. The rates have not been announced yet. When they are, the smart play is to compare across banks — and move before September."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The RBI Is Picking Up the Tab on NRI Deposits. Banks Are Already Lining Up.",
    "subheadline": "India's central bank will absorb hedging costs on foreign-currency deposits until September, hoping to lure billions from the diaspora as the rupee slides to record lows.",
    "slug": make_slug("rbi-fcnr-nri-deposit-hedging-scheme-banks-rupee"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "NRIs in the US, Gulf, and Europe could see higher interest rates on their Indian bank deposits as the RBI subsidises hedging costs, making FCNR(B) accounts significantly more attractive during a narrow September window.",
    "tags": ["nri", "diaspora", "rbi", "fcnr", "banking", "deposits", "rupee", "nri-finance"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "LiveMint", "url": "https://www.livemint.com/economy/rbi-to-bear-hedging-costs-for-banks-foreign-currency-deposits-flows-of-over-10-bn-seen"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-measures-protect-rupee-seen-drawing-about-40-billion-analysts-say-2026-06-06/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/money-and-banking/coordinated-centre-rbi-measures-target-sustained-dollar-inflows/article69656789.ece"},
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/how-could-nris-benefit-from-rbi-bearing-fcnrb-hedging-costs"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/da/Sanjay_Malhotra_RBI.jpg",
    "image_caption": "RBI Governor Sanjay Malhotra at a monetary policy announcement in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ─── ARTICLE 2 ───────────────────────────────────────────────────────────────

art2_body = """On June 2, at a formal ceremony in Phnom Penh attended by the Governor of the National Bank of Cambodia and officials from the Reserve Bank of India, a payment system built for a billion Indians quietly went live in its ninth country. Indian travellers visiting Cambodia can now open their UPI app, scan a KHQR code at any of 4.5 million Cambodian merchants, and pay directly from their Indian bank account. No currency conversion app. No international card surcharge. No cash.

Four days later, on June 6, India and Nepal linked UPI to Nepal's National Payments Interface, enabling faster and cheaper cross-border remittances between the two countries.

The nine-country map now reads: Singapore, the UAE, France, Mauritius, Nepal, Bhutan, Qatar, Sri Lanka, and Cambodia. For NRIs who travel across these corridors — and millions do, particularly between India, the Gulf, and Southeast Asia — this is no longer a novelty. It is becoming the default way to pay.

## From payments app to sovereign infrastructure

But the bigger story is not the map. It is the blueprint.

The RBI's Annual Report for 2025–26, released on June 1, quietly repositioned the digital rupee — the e₹ — from a retail payments experiment into something far more strategic: India's hedge against SWIFT dependency and geopolitical payment risk.

The headline developments buried in the report deserve closer reading. Programmable welfare delivery is already live: pilots in Gujarat, Puducherry, and Chandigarh have deployed programmable e₹ tokens for Public Distribution System food subsidies — tokens that can only be redeemed for eligible commodities at identified fair-price shops, eliminating leakage at the point of disbursement. A new Unified Markets Interface has been launched for tokenised financial assets, with a pilot for tokenising certificates of deposit using wholesale e₹ for settlement.

And then the cross-border play: the RBI has signed memoranda of understanding with the Monetary Authority of Singapore and held bilateral discussions with the Central Bank of the UAE to operationalise cross-border e₹ pilots in 2026–27. India is also participating in BIS Project Rialto, which tests foreign-exchange settlement via automated market makers and wholesale central bank digital currencies, and Project Mandala, which embeds anti-money-laundering compliance into transactions using zero-knowledge proofs.

## The remittance corridor that matters most

For the diaspora, the India-UAE CBDC corridor is the one to watch. Over $20 billion flows annually between the two countries in remittances — overwhelmingly from Indian workers in the Gulf sending money home. Today, that money passes through a chain of correspondent banks, each taking a cut and adding a day. A live CBDC corridor would settle those payments in near real-time, at a fraction of the cost, with compliance baked into the transaction itself.

India already processes over 200 billion UPI transactions a year. Building CBDC infrastructure for welfare delivery, trade finance, and cross-border settlement simultaneously, at this scale, is without precedent. The Payments Vision 2028 framework introduced alongside the annual report includes offline e₹ capability — critical for rural India — and an expanded MuleHunter.ai fraud detection system with a new mule account registry.

## What NRIs gain — and what is still missing

The practical benefits are stacking up. UPI abroad means NRIs returning to India or visiting countries in the network can leave their international cards at home. The Cambodia launch, facilitated by NPCI International Payments Limited and Acleda Bank, demonstrates that the interoperability model works even in smaller economies. The Nepal link directly serves the massive cross-border economic relationship between the two countries.

What is still missing is the last mile for NRI-to-India remittances through UPI itself. Today, UPI's international capability is limited to person-to-merchant payments by Indian travellers abroad — you can pay at a shop in Singapore, but you cannot yet send money from your US bank account to your family in Lucknow via UPI. That use case remains the domain of SWIFT, wire transfers, and fintech intermediaries like Wise and Remitly.

The CBDC corridor, if it works as designed, closes that gap. It does not merely match the speed of existing fintech solutions — it changes the underlying rails. Instead of rupee-dollar conversion happening through a chain of intermediaries, each adding latency and cost, the transaction would settle directly between central-bank-issued digital currencies.

India's 35-million-strong diaspora sends home more than $135 billion annually — the largest remittance inflow of any country on earth. Even a modest reduction in the cost and friction of those transfers, applied at that scale, reshapes the economics of being an NRI. The infrastructure is being laid. The question now is how fast it reaches the people it is being built for."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's UPI Is Now Live in Nine Countries. The Endgame Is Bigger Than Payments.",
    "subheadline": "Cambodia and Nepal are the latest additions to India's expanding digital payments network, but the RBI's real ambition — a sovereign digital currency that rewires how $135 billion in diaspora remittances move — is only now coming into focus.",
    "slug": make_slug("upi-nine-countries-cbdc-digital-rupee-nri-remittance"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "UPI abroad lets NRIs pay at merchants in 9 countries without cash or international cards. The India-UAE CBDC corridor, once live, could fundamentally reduce the cost and speed of the $20+ billion annual Gulf-India remittance flow.",
    "tags": ["nri", "diaspora", "upi", "digital-rupee", "cbdc", "remittance", "fintech", "payments"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "ET Edge Insights", "url": "https://www.etedge-insights.com/technology/fintech/upi-goes-global-india-cambodia-enable-real-time-qr-payments/"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/uae-joins-singapore-france-mauritius-nepal-sri-lanka-and-other-top-destinations-as-cambodia-becomes-the-9th-country/"},
        {"name": "Crypto & Fintech Weekly (LinkedIn)", "url": "https://www.linkedin.com/pulse/crypto-fintech-weekly-uae-india-asia-week-ending-7-june-2026"},
        {"name": "Ainvest", "url": "https://www.ainvest.com/news/cryptooindia-posted-on-2026-06-06-indias-upi-links-with-nepals-national-payments-interface-enabling-faster-and-cheaper-cross-border-remittances/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/12935064/pexels-photo-12935064.jpeg",
    "image_caption": "A contactless payment using a smartphone and QR code scanner at a retail counter",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ─── INSERT ──────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
