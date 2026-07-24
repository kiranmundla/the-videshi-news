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
        "headline": "Six Months of America's Remittance Tax: The One Per Cent Levy That Rewired How the Diaspora Sends Money Home",
        "subheadline": "What began as a five per cent scare in Congress ended up as a one per cent excise tax on certain transfers. Half a year into enforcement, the real effects are subtler — and more uneven — than either side predicted.",
        "slug": make_slug("us-remittance-tax-one-percent-six-months-nri-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Every H-1B holder, green card carrier, and naturalised citizen who sends money to family in India now operates under this law. The exemptions favour those who bank digitally; the tax bites hardest on cash-and-counter senders — a distinction that splits the diaspora along class lines.",
        "tags": ["nri", "diaspora", "remittance", "tax", "one-big-beautiful-bill", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wikipedia — One Big Beautiful Bill Act", "url": "https://en.wikipedia.org/wiki/One_Big_Beautiful_Bill_Act"},
            {"name": "KPMG UK — Impact for Individuals", "url": "https://kpmg.com/uk/en/home/insights/2025/07/the-one-big-beautiful-bill-and-the-impact-for-individuals.html"},
            {"name": "Center for Global Development", "url": "https://www.cgdev.org/blog/even-1-percent-us-remittance-tax-hits-poor-countries-hard"},
            {"name": "CNN — One Year Later", "url": "https://www.cnn.com/2026/07/12/politics/one-big-beautiful-bill-democrats-midterms/index.html"},
            {"name": "RSM US — Excise Tax Analysis", "url": "https://rsmus.com/insights/tax-alerts/2025/one-big-beautiful-bill-act-imposes-1-percent-excise-tax-on-cross-border-remittances.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/United_States_Capitol_-_west_front_edit.jpg/1280px-United_States_Capitol_-_west_front_edit.jpg",
        "image_caption": "The United States Capitol in Washington, D.C., where the One Big Beautiful Bill Act was passed",
        "image_attribution": "Wikimedia Commons",
        "body": """When the One Big Beautiful Bill Act landed on Donald Trump's desk on July 4, 2025, Indian WhatsApp groups from Edison to Fremont lit up with a single question: how much will this cost me?

The answer, it turns out, depends almost entirely on *how* you send money — not how much.

## From five per cent panic to one per cent reality

The legislative journey was a study in incremental compromise. House Republicans introduced the remittance tax in May 2025 at a punishing five per cent. Indian diaspora organisations, remittance firms, and the Mexican government mounted a furious lobbying campaign. The House version was softened to 3.5 per cent. By the time the Senate finished its markup, the rate had been whittled to one per cent — and the scope had shifted. The original bill targeted non-citizens exclusively. The final law applies the excise to all senders, citizens included, but carves out an exemption so wide that most middle-class remitters walk straight through it.

Transfers sent from a US bank account, credit union, or investment account are exempt. Transfers funded by a US-issued debit or credit card are exempt. Cryptocurrency transfers are exempt. Anything under fifteen dollars is exempt.

What is left? Cash-counter remittances — the kind made at wire-transfer storefronts with cash, money orders, or cashier's checks. Prepaid card reloads and certain online bill-payment channels that do not originate from a regulated financial institution also fall within the net.

## Who actually pays

For the typical Indian-American software engineer in Seattle wiring money through their Chase or SBI NRI account, the tax is a non-event. Bank-to-bank transfers — the dominant channel for the tech-professional diaspora — fall squarely within the exemption.

The burden lands elsewhere: on construction workers and restaurant staff who remit weekly wages through cash-based transfer shops, on undocumented workers who cannot open regulated bank accounts, and on elderly family members who prefer the familiarity of a neighbourhood hawala-adjacent counter. In practical terms, the tax draws a line between the banked and the unbanked diaspora.

The Joint Committee on Taxation estimates the levy will generate roughly ten billion dollars over a decade — a figure that reflects both the narrow taxable base and the assumption that many senders will simply switch to exempt channels.

## The macroeconomic ripple

India received a record $145 billion in remittances in fiscal 2025-26, with the United States contributing just over a quarter. A one per cent tax on a narrow slice of those flows will not move the national needle. The Global Trade Research Initiative initially warned of a ten-to-fifteen per cent drop in inflows — but that projection was pegged to the original five per cent rate on all non-citizen transfers, a bill that no longer exists.

The Center for Global Development estimates real-world losses at roughly $1.5 billion for Mexico and proportionally less for India, where bank-based transfers dominate. The Reserve Bank of India has not flagged the tax as a material risk to foreign-exchange reserves or to the rupee, which has its own, larger problems to manage.

## The political afterlife

A year after signing, the law has become a midterm weapon. Democrats are running ads in battleground districts framing the entire One Big Beautiful Bill — including its Medicaid cuts, food-stamp rollbacks, and tax breaks for the wealthy — as a betrayal of working families. Republicans counter with the law's populist provisions: a larger standard deduction, the SALT cap adjustment, and the child tax credit expansion.

For the Indian-American community, the remittance tax occupies a peculiar position. It is symbolically offensive — a levy that began as a nativist swipe at immigrants — but practically toothless for most of its members. The real sting is reserved for the least visible segment of the diaspora: the cash-economy workers who send small sums home at real cost.

## What to do

If you are still remitting through a cash-counter service, the simplest defence is to open a basic US bank account — most credit unions require minimal documentation — and route transfers through it. Wise, Remitly, and similar digital platforms that debit from a US bank account are exempt. If you are already banking digitally, the tax does not touch you.

The one per cent levy is a blunt instrument applied to a shrinking channel. Its real legacy may be less about revenue and more about accelerating a shift that was already underway: pushing the diaspora's last cash holdouts into the regulated financial system, whether they are ready or not."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Banks Are Offering NRIs Up to Seven Per Cent on Dollar Deposits. The Window Closes in Eleven Weeks.",
        "subheadline": "The RBI's special swap facility has removed the hedging cost that kept FCNR(B) rates stuck below four per cent. Indian Bank alone is targeting two billion dollars by September. Here is what NRIs need to know before the deadline.",
        "slug": make_slug("rbi-fcnr-deposits-nri-seven-percent-dollar-swap-window"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For NRIs parking idle dollars in US savings accounts yielding under one per cent, or even in Treasuries at four-and-a-half per cent, this is a rare moment when parking money in India carries no currency risk and pays meaningfully more — but only until September 30.",
        "tags": ["nri", "diaspora", "banking", "rbi", "fcnr", "deposits", "investment"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/money-and-banking/indian-bank-sees-fresh-fcnr-b-deposits-worth-140-million-since-new-rbi-rule-optimistic-of-clocking-2-b-till-sept/article71206428.ece"},
            {"name": "Reuters — Policy Support Lifts Foreign Inflows", "url": "https://www.reuters.com/world/india/policy-support-lifts-foreign-inflows-into-indian-banks-14-month-high-2026-07-08/"},
            {"name": "Livemint — Why FCNR Deposits Are Attractive", "url": "https://www.livemint.com/money/personal-finance/why-fcnr-deposits-at-6-7-1-rates-are-attractive-for-nris-11718440680944.html"},
            {"name": "Value Research Online — RBI Dollar Deposits", "url": "https://www.valueresearchonline.com/stories/56732/rbi-is-offering-nris-up-to-7-on-dollar-deposits/"},
            {"name": "Reuters — RBI Concessional Swaps", "url": "https://www.reuters.com/world/india/indias-rbi-offers-concessional-swaps-allows-leverage-nri-deposits-drive-forex-2026-06-09/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Mumbai%2C_reserve_bank_of_india_01.jpg/1280px-Mumbai%2C_reserve_bank_of_india_01.jpg",
        "image_caption": "The Reserve Bank of India headquarters in Mumbai, which launched the special forex swap window for NRI deposits",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, FCNR(B) deposits were the driest corner of NRI banking — rates stuck in the three-to-four per cent range, barely competitive with a US Treasury bill, and locked up for three to five years. That arithmetic changed overnight on June 8, when the Reserve Bank of India opened a special forex swap window that fundamentally altered the economics of dollar deposits in Indian banks.

The mechanics are straightforward. When a bank takes a dollar deposit from an NRI and converts it to rupees for domestic lending, it normally bears a hedging cost of roughly three per cent per annum to protect against rupee depreciation. That cost ate into what banks could offer depositors. Under the new scheme, the RBI absorbs the entire hedge by swapping dollars with banks at par — same rate in, same rate out — on its own balance sheet. Banks pass the savings to NRIs as higher interest rates.

## What the banks are offering

The rate hikes have been swift and substantial. HDFC Bank moved first, lifting its three-to-five-year FCNR(B) rate by 265 basis points to six per cent. ICICI Bank followed at 6.5 per cent. State Bank of India introduced a tiered structure: 5.75 per cent on deposits above one million dollars for four-to-five-year terms, six per cent at the five-year mark. Bank of Baroda matched at six per cent for dollars, with lower but still elevated rates for sterling, euros, and Canadian and Australian dollars.

At the aggressive end, AU Small Finance Bank is offering 7.1 per cent — the ceiling implied by the RBI's removal of interest-rate caps on these deposits. Most NRIs dealing in meaningful sums, however, are likely to stick with the top-tier banks where repatriation is smooth and documentation demands are manageable.

Indian Bank, a mid-sized public-sector lender, disclosed on July 10 that it has already raised $140 million in fresh FCNR(B) deposits since June. Its managing director, Binod Kumar, told reporters the bank has a visible pipeline of one billion dollars and is targeting two billion by September. Before this window, Indian Bank's total FCNR(B) balance stood at $457 million.

## The comparison that matters

The relevant benchmark for most NRIs is not an Indian rupee fixed deposit — that carries currency risk — but a US Treasury bill or a high-yield savings account. As of early July, the one-year Treasury yield sits around 4.3 per cent. A three-year Treasury note is in the same range. Against that, a three-year FCNR(B) deposit at six per cent, carrying zero currency risk (you deposit dollars, you receive dollars), with interest income exempt from Indian tax for eligible NRI and OCI holders, is a genuine premium.

The catch is liquidity. There is a hard one-year lock-in, and premature withdrawal after that year is at the bank's discretion. You are also relying on the bank's credit — India's deposit insurance covers only five lakh rupees (roughly $6,000 at current rates), which is negligible for any dollar deposit worth making. Stick to SBI, HDFC, ICICI, or Axis unless you have a specific reason not to.

## Why the RBI is doing this

This is not generosity. It is forex-reserve management. The rupee fell to nearly 97 per dollar earlier this year, its weakest level ever, under pressure from Middle East tensions, oil prices, and foreign portfolio investor outflows. The RBI's reserves needed reinforcement.

The FCNR(B) swap is one piece of a coordinated package that also includes subsidised swaps for external commercial borrowings by public-sector enterprises, elimination of capital-gains tax on government bonds for foreign portfolio investors, and a doubling of the individual overseas-investor cap in listed Indian equities from five to ten per cent.

Economists at IDFC First Bank estimate the FCNR(B) window alone could attract $40 billion in inflows. Jefferies is more bullish, projecting $60 to $70 billion. The numbers depend heavily on how aggressively banks market the product to NRIs in the US, UK, and Gulf — where the bulk of overseas Indian savings sit.

The 2013 precedent offers some guidance. The last time the RBI opened a similar window, during a severe rupee crisis, banks raised roughly $34 billion in FCNR(B) deposits. The current scheme is more generous — no hedging cost at all, versus a partial subsidy in 2013 — and the overseas Indian population is substantially larger.

## The deadline

The deposit window closes on September 30, 2026. Swaps can be executed with the RBI until October 16. After that, rates revert to whatever banks can offer once they are bearing their own hedging costs again — which, in practice, means a drop of 200 to 300 basis points.

For NRIs with idle dollar balances — whether parked in a US savings account, sitting in a brokerage sweep, or recently vested in RSUs — the window is narrow and the premium is real. The decision is not complicated. The timing is."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
