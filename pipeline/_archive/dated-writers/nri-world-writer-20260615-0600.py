#!/usr/bin/env python3
"""NRI World writer — 2026-06-15 06:00 UTC run"""

import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ── env ──────────────────────────────────────────────────────────────────
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

pexels_env = Path.home() / "workspace/.env.pexels"
for line in pexels_env.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
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

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_bytes, filename):
    """Upload compressed JPEG to Supabase article-images bucket."""
    compressed = compress_image(img_bytes)
    sz = len(compressed)
    print(f"  Compressed to {sz/1024:.0f} KB")
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(
        f"{SB_URL}/storage/v1/object/article-images/{filename}",
        headers=upload_headers,
        data=compressed,
        timeout=30
    )
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"

def download_image(url):
    r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
    r.raise_for_status()
    return r.content

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ── Article 1: India's Tax Information Sharing Overhaul ────────────────

art1_id = str(uuid.uuid4())
art1_slug = make_slug("india-tax-dragnet-nri-cross-border-information-sharing-july-2026")

art1_body = """India's tax authorities are about to get a lot faster at comparing what you report in New Delhi with what your bank tells the IRS in Washington. Starting July 1, 2026, a revamped cross-border tax information-sharing framework will compress response times, assign dedicated tracking officers, and extend its gaze to crypto wallets and offshore trusts — all without creating a single new tax.

The timing is deliberate. On June 9, the Central Board of Direct Taxes convened a webinar with PwC India that drew more than 1,100 participants from 16 overseas jurisdictions, including the United States, the United Kingdom, Australia, Singapore, Japan, and the UAE. The session was pitched as a gentle tutorial on the new Income-tax Act, 2025. In practice, it was a signal flare: the machinery is live, and compliance expectations have been raised.

## What Changes on July 1

The new framework does not impose any fresh levies. Instead, it accelerates the plumbing through which governments exchange financial data on each other's taxpayers. Three shifts matter most for NRIs.

First, the **15-day response window**. When a foreign tax authority requests information that Indian officials already have on file, the revised protocol requires a response within 15 days — a dramatic compression from the months-long silences that were once routine. Second, **mandatory status updates**: if a request cannot be fulfilled immediately, officers must now provide progress reports rather than letting the query sit unacknowledged. Third, India is appointing **dedicated officers** to monitor outbound requests — the ones New Delhi sends to Washington, London, Canberra, and Dubai — ensuring that information India seeks about its own residents' overseas assets is actively tracked.

## Who Should Pay Attention

The framework's reach is broader than many NRIs assume. It covers foreign bank accounts, brokerage accounts, U.S.-listed stocks and ETFs, RSUs, ESOPs and ESPPs, foreign retirement accounts, overseas real estate, crypto holdings, trust interests, and even signing authority on accounts held by others. Critically, the disclosure obligation can apply even when no tax is owed, the account balance is negligible, or the asset was purchased with fully taxed income.

Students who opened a foreign bank account during an American master's programme and never closed it. Tech workers in the Bay Area sitting on vested RSUs from a Nasdaq-listed employer. Gulf returnees who kept a dormant NRE account in Abu Dhabi. Anyone who bought Bitcoin on Coinbase while living abroad. All of them fall within the framework's perimeter.

The heaviest exposure falls on individuals who are **resident and ordinarily resident** in India under the Income-tax Act's day-count rules. Indian tax residency turns on physical presence, not on the label printed on a visa. A person holding a U.S. green card, a Canadian work permit, or a UAE residence visa may still qualify as an Indian tax resident if their days-in-India arithmetic tips the wrong way — and the new system is designed to catch precisely those cases where foreign-reported data diverges from Indian filings.

## The Compliance Checklist

Under the new regime, taxpayers with any cross-border financial exposure need to get several things right. **Schedule FA** (Foreign Assets) in the Indian return must list every foreign account, custodial position, equity interest, immovable property, trust, and signing authority. **Schedule FSI** (Foreign Source Income) captures dividends, interest, capital gains, and rental income from outside India. Choosing the wrong ITR form — filing an ITR-1 when an ITR-2 is required, for instance — can itself trigger a compliance notice.

The penalties for getting it wrong are not gentle. India's Black Money (Undisclosed Foreign Income and Assets) and Imposition of Tax Act treats undisclosed foreign assets with a severity that surprises taxpayers accustomed to the relatively forgiving mechanics of domestic non-disclosure. The intention behind the acquisition is irrelevant: an inherited overseas property, a forgotten student account, a modest foreign dividend — if it goes unreported, the consequences can be disproportionate to the underlying amount.

## The Crypto Dimension

The OECD's Crypto-Asset Reporting Framework, which India has signed onto, will enable automatic exchange of transaction-level data on crypto activity between participating jurisdictions. Offshore exchanges that once felt safely distant from Indian tax authorities are now part of the information grid. Taxpayers using foreign platforms are expected to maintain transaction histories, wallet records, exchange statements, and purchase-cost documentation.

## What NRIs Should Do Now

The practical advice from tax practitioners is straightforward but urgent: review every foreign account, investment, and asset before the July 1 transition; ensure the correct ITR form is selected; complete Schedules FA, FSI, and TR where applicable; and preserve documentation — bank statements, brokerage records, property papers, crypto logs, and foreign tax certificates — in anticipation of cross-border queries that will now move faster than ever before.

The message from New Delhi is not subtle. India is not raising taxes on its diaspora. It is simply making it much harder to be wrong about what you owe."""

# Source image for Article 1: Pexels tax documents
print("📷 Sourcing image for Article 1...")
try:
    img1_raw = download_image("https://images.pexels.com/photos/6863202/pexels-photo-6863202.jpeg?auto=compress&cs=tinysrgb&w=1200")
    art1_image_url = upload_to_supabase(img1_raw, f"{art1_id}.jpg")
    art1_image_caption = "Tax documents and a calculator on a desk — the tools of cross-border compliance"
    art1_image_attribution = "Pexels"
    print(f"  ✅ Article 1 image uploaded: {art1_image_url[:80]}...")
except Exception as e:
    print(f"  ❌ Image upload failed: {e}")
    art1_image_url = "https://images.pexels.com/photos/6863202/pexels-photo-6863202.jpeg?auto=compress&cs=tinysrgb&w=1200"
    art1_image_caption = "Tax documents and a calculator on a desk"
    art1_image_attribution = "Pexels"


# ── Article 2: India Scraps Bond Taxes ─────────────────────────────────

art2_id = str(uuid.uuid4())
art2_slug = make_slug("india-bond-tax-scrapped-foreign-investors-billion-three-days")

art2_body = """One billion dollars in government bonds, purchased in three trading sessions. That is the speed at which foreign money began flowing into India's debt market after New Delhi did something it had resisted for years: it scrapped withholding and capital gains taxes on foreign investments in government securities.

The measures, unveiled on June 6 as part of a broader package to shore up the rupee and stabilise the current account, have moved faster than even their architects expected. Before the announcement, foreign investors had bought a cumulative $1.6 billion of Indian government bonds in the entire year to date. In the six sessions starting June 5, they net-purchased 155.5 billion rupees — overtaking the prior five months' total in a single week.

## The Oil Shock Backstory

The context is important, because this was not generosity. India's economy is under pressure from an oil-price spike driven by the Iran conflict, and the rupee has fallen 5.86 per cent this year — trailing only the Indonesian rupiah as Asia's worst-performing currency. Foreign portfolio investors had been pulling money out of Indian equities for months, and the government needed to plug the capital-account hole.

The response was a coordinated salvo. Policymakers scrapped both withholding tax and capital gains tax on foreign investments in government bonds. They broadened the pool of securities available to overseas investors without investment caps. The Reserve Bank of India introduced concessional foreign-exchange swaps to incentivise banks to raise foreign-currency deposits from NRIs. And state-owned enterprises were given fresh leeway to borrow overseas at subsidised swap rates of 1.5 per cent.

"We believe that these changes are a game-changer for debt flows," said Jennifer Taylor, head of emerging-market debt and systematic fixed income at State Street Investment Management, which manages about $5.6 trillion.

## The Bloomberg Index Prize

The immediate market impact — yields have fallen 10 to 30 basis points across the curve — is notable but secondary. The real prize is something that has eluded India for years: inclusion in Bloomberg's Global Aggregate Index, the flagship benchmark tracked by trillions of dollars in passive and quasi-passive fixed-income money.

Bloomberg Index Services is expected to seek investor feedback later this month on whether Indian government bonds should be added to the index. India's finance minister reportedly met with central bank officials in the weeks before the tax cuts specifically to push for this entry. Inclusion in the Bloomberg index would follow India's 2024 entry into JPMorgan's Government Bond Index-Emerging Markets, which itself triggered billions in inflows.

Niel Clement, portfolio manager for emerging-market fixed income at BNP Paribas Asset Management (€1.6 trillion in assets), said the reforms would "broaden opportunities for overseas investors, redirect flows to the onshore market and provide a constructive boost to India's bid for inclusion." M&G Investments (£376 billion in assets) added that while the tax exemptions improve near-term appeal, Bloomberg inclusion would be the bigger structural driver.

## What It Means for NRIs

For NRIs who have traditionally parked money in FCNR deposits and NRE fixed deposits, the bond-market overhaul introduces a new dimension. Government securities now offer yields around 6.9 per cent with zero tax friction for non-resident buyers — a combination that competes directly with the 7.1 per cent NRI deposit rates that banks have been dangling since the RBI's deposit-mobilisation push.

The RBI's concessional swap facility, open until October 16 for deposits mobilised by September 30, sweetens the deal further. Banks can now offer leverage on FCNR deposits — a feature last seen during the 2013 taper tantrum, when it successfully pulled billions in NRI money into the Indian banking system. Underlying deposits carry a one-year lock-in period, and the swap cannot be cancelled once executed.

Citi has sharply revised India's balance-of-payments forecast for the current fiscal year, now projecting a $5 billion surplus against an earlier estimate of a $60 billion deficit. If that revision holds, it would stabilise the rupee and make Indian fixed-income assets — bonds and deposits alike — considerably more attractive on a currency-adjusted basis.

## The Risks That Remain

Not everyone is rushing in. "The bigger issue for offshore investors is still the currency," said Rong Ren Goh, head of macro and thematics for Asian fixed income at Eastspring Investments ($250 billion in assets). The recent pace of rupee depreciation has eroded the carry advantage of Indian debt, and investors want clearer signs of stabilisation before making large allocations.

The broader backdrop is also challenging. Global interest-rate volatility remains elevated, and the oil shock that triggered India's crisis has not resolved. M&G's Low Guan Yi cautioned that "the pickup in interest-rate volatility across many markets and the shift from monetary easing to tightening in response to inflationary pressures from energy and food prices" remain headwinds.

India, in other words, has bought itself time and credibility — but not immunity. The bond-tax abolition is a structural reform that will outlast the current crisis. Whether the current crisis outlasts the patience of foreign investors is a different question entirely."""

# Source image for Article 2: RBI building in Mumbai (Wikimedia Commons)
print("📷 Sourcing image for Article 2...")
try:
    img2_raw = download_image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_04.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_04.jpg")
    art2_image_url = upload_to_supabase(img2_raw, f"{art2_id}.jpg")
    art2_image_caption = "The Reserve Bank of India headquarters in Mumbai's Fort district"
    art2_image_attribution = "Wikimedia Commons"
    print(f"  ✅ Article 2 image uploaded: {art2_image_url[:80]}...")
except Exception as e:
    print(f"  ❌ Image upload failed: {e}")
    art2_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_04.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_04.jpg"
    art2_image_caption = "The Reserve Bank of India headquarters in Mumbai"
    art2_image_attribution = "Wikimedia Commons"


# ── Insert articles ────────────────────────────────────────────────────

articles = [
    {
        "id": art1_id,
        "headline": "India's Tax Dragnet Tightens Around NRIs. The July 1 Overhaul Will Make Hiding Assets Nearly Impossible.",
        "subheadline": "A new cross-border information-sharing framework compresses response times to 15 days, assigns dedicated tracking officers, and pulls crypto into the net — all without creating a single new tax.",
        "slug": art1_slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NRIs across the US, UK, Canada, and the Gulf face tighter scrutiny on foreign bank accounts, RSUs, property, and crypto holdings as India's tax information exchange system accelerates from July 1.",
        "tags": ["nri", "diaspora", "tax", "CBDT", "FBAR", "FATCA", "cross-border", "compliance"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/ampstories/news/india-tightens-global-tax-information-sharing-what-does-it-mean-for-taxpayers"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/india-tightens-foreign-tax-information-sharing-from-july-1-2026-targeting-cross-border-assets/"},
            {"name": "TaxScan", "url": "https://www.taxscan.in/top-stories/cbdt-webinar-decodes-new-income-tax-act-2025-with-global-focus-on-international-tax-transfer-pricing-1447458"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art1_image_url,
        "image_caption": art1_image_caption,
        "image_attribution": art1_image_attribution,
        "body": art1_body,
    },
    {
        "id": art2_id,
        "headline": "India Scrapped Bond Taxes for Foreign Investors. One Billion Dollars Arrived in Three Days.",
        "subheadline": "The abolition of withholding and capital gains taxes on government securities has triggered a buying spree, compressed yields, and revived India's bid for Bloomberg index inclusion — all while the rupee fights a losing battle against oil prices.",
        "slug": art2_slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NRIs choosing between FCNR deposits and government bonds now face a genuinely competitive choice — zero-tax bonds at 6.9% versus 7.1% deposit rates with RBI-backed swap incentives.",
        "tags": ["nri", "diaspora", "bonds", "tax", "RBI", "investment", "Bloomberg", "FCNR"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-bond-tax-moves-catalyse-foreign-debt-inflows-bolster-bid-global-index-2026-06-10/"},
            {"name": "Reuters", "url": "https://www.reuters.com/markets/rates-bonds/indian-rupee-bonds-get-boost-iran-peace-deal-eye-fed-move-2026-06-13/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/case-capital-gains-tax-changes-equities-weaker-than-bonds-indias-chief-economic-2026-06-13/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art2_image_url,
        "image_caption": art2_image_caption,
        "image_attribution": art2_image_attribution,
        "body": art2_body,
    },
]

print("\n📝 Inserting articles...")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\nDone.")
