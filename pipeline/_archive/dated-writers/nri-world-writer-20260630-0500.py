#!/usr/bin/env python3
"""
NRI World Writer — June 30 2026, 05:00 PT run
Two fresh NRI World articles for The Videshi.

Article 1: GOPIO-CT 20th Anniversary Awards Banquet
Article 2: FCNR Rate War — Banks Race to Woo NRI Dollars (distinct from existing policy-focused article)
"""

import os, json, requests, datetime, subprocess

# ── env ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.replace("export ", "").strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser("~/workspace/.env.supabase"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

# ── articles ─────────────────────────────────────────────────────────────

articles = []

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: GOPIO-CT 20th Anniversary Awards Banquet
# ═══════════════════════════════════════════════════════════════════════

gopio_body = """When the Global Organization of People of Indian Origin marked two decades in Connecticut on June 13, the five names on the awards programme read less like a guest list and more like a cross-section of the state's Indian American ambition. A state senator, a nanotechnology entrepreneur, a veteran journalist, a community bank CEO, and an engineering professor — all honoured at GOPIO-CT's 20th Anniversary Awards Banquet at the Water's Edge Banquet Hall in Darien.

The evening's chief guest, India's Deputy Consul General in New York, Vishal Harsh, set the tone early. "The achievements of Indian Americans have become a global benchmark," he said. "Communities across the world look to replicate the success and impact you have created in the United States."

## From Legal Scholar to State Senator

Connecticut State Senator Sujata Gadkar-Wilcox, honoured for Political Leadership, used her acceptance speech to locate Indian traditions within the broader American story. She noted how Quinnipiac University's Garba dance and Diwali celebrations now draw students of all backgrounds. "These traditions become part of the American story because immigrants and their families *are* the American story," she said.

Gadkar-Wilcox, who also serves as a Professor of Legal Studies at Quinnipiac, represents the 22nd District spanning parts of Trumbull, Monroe, and Bridgeport. Her presence at the event — alongside Republican State Senator Tony Hwang and Assemblyman Jonathan Jacobson — underscored the bipartisan respect the diaspora community now commands in Hartford.

## Nanotech, Journalism, Banking, Engineering

The night's other honourees spanned an impressive range. Dr. Anil Diwan, founder and executive chairman of NanoViricides (NYSE American: NNVC), received the Entrepreneurship and Business award for his work developing antiviral therapies using proprietary nanotechnology that neutralises viruses mechanically rather than relying solely on host immune responses. His Connecticut-headquartered firm represents a growing strand of Indian-led biotech innovation in the Northeast.

Veteran journalist Ajay Ghosh, founder of the Indo-American Press Club and a career spanning more than 30 years across media, higher education, and healthcare, accepted the Journalism award. "Journalism is facing a crisis as never before," Ghosh warned. "Across the globe, the institution we rely on to inform us, challenge power, and uphold truth is under strain. This is not a local problem — it is global and systemic."

Nitin Mhatre, who became CEO of First County Bank in Fairfield on April 15, took home the Corporate Leadership honour. Under his watch, the independent mutual community bank — which has operated continuously in Fairfield County for more than 174 years — is navigating the complex crosscurrents of regional banking. Professor Hemchandra Shertukde of the University of Hartford, recognised for his nearly four decades in engineering and applied sciences, rounded out the list.

## Twenty Years of Institution-Building

The anniversary itself told a story of patient community-building. GOPIO-CT was inaugurated on March 24, 2006, in the presence of then-Congressman Christopher Shays and Deputy Consul General A.R. Ghanashyam. Over two decades, the chapter has supported more than a dozen charitable organisations in Connecticut, sponsored fundraising for the Bennett Cancer Centre, and regularly hosted soup kitchens at the New Covenant Center in Stamford.

"Since its founding, GOPIO-CT has served as a vibrant platform promoting community service, cultural heritage, civic engagement, and unity among People of Indian Origin in Connecticut and beyond," said chapter president Mahesh Jhangiani.

GOPIO International founder Dr. Thomas Abraham, who chairs the awards committee, noted that the Connecticut chapter's success had become "a model for GOPIO International in shaping the structure and activities of local chapters worldwide."

## Giving Back, Concretely

The evening was not just about recognition. GOPIO-CT presented $25,000 each to two local charities — Future 5, a Stamford-based organisation that prepares under-resourced high school students for post-secondary success, and the Children's Learning Center of Fairfield County. The cheques were received by Future 5's founder Clif McFeely and CLC's CEO Monica Maccera Filpú.

With the South Asian population continuing to grow in Connecticut, GOPIO-CT's mission has evolved from cultural preservation to active participation in public policy, economic development, and community health. The 20th anniversary gala made one thing clear: the diaspora's institutions are no longer just cultural societies. They are civic infrastructure."""

gopio_sources = json.dumps([
    {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/19/gopio-ct-marks-20th-anniversary-honors-distinguished-leaders/"},
    {"name": "Global Net News", "url": "https://globalnet.news/gopio-connecticut-to-celebrate-20th-anniversary/"},
    {"name": "Malayalam Daily News", "url": "https://malayalamdailynews.com/gopio-ct-marks-20th-anniversary-honors-distinguished-leaders/"},
    {"name": "The Indian Panorama", "url": "https://theindianpanorama.news/gopio-ct-to-honor-five-indian-american-achievers-at-its-20th-anniversary/"}
])

articles.append({
    "headline": "Five Indian Americans, Five Fields, One State: Inside GOPIO-CT's 20th Anniversary Honours",
    "subheadline": "A state senator, a nanotech founder, a journalist, a bank CEO, and an engineering professor — Connecticut's diaspora organisation celebrated two decades by showcasing the community's breadth.",
    "body": gopio_body.strip(),
    "slug": "gopio-ct-20th-anniversary-indian-american-honors-connecticut-diaspora-20260630",
    "category": "nri-world",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/29410669/pexels-photo-29410669.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An elegantly set awards banquet table, reflecting the formal celebration at GOPIO-CT's milestone event",
    "image_attribution": "Pexels",
    "sources": gopio_sources,
    "tags": "{Indian American,GOPIO,Connecticut,diaspora,community,awards}",
    "diaspora_angle": "GOPIO-CT's 20th anniversary banquet in Darien honoured five Indian American leaders spanning politics, biotech, journalism, banking, and engineering — illustrating the community's growing institutional depth and bipartisan political standing in the American Northeast.",
    "score_total": 68,
    "published_at": NOW,
    "vertical": "nri-world",
    "urgency": "medium",
})


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: FCNR Rate War — Banks Racing to Woo NRI Dollars
# ═══════════════════════════════════════════════════════════════════════

fcnr_body = """When the Reserve Bank of India announced on June 5 that it would bear the full hedging cost for banks raising fresh three-to-five-year foreign currency deposits, it fired a starting pistol that every bank in India heard. Within days, FCNR(B) deposit rates — long an afterthought offering 2-3 per cent — exploded upward. Some banks are now dangling rates as high as 7.50 per cent, and the race is still accelerating.

For non-resident Indians sitting on surplus dollars, this is the most lucrative FCNR window in recent memory. But not all offers are equal, the clock is ticking, and the fine print deserves a close read.

## What Changed, and Why

The RBI's June monetary policy included two headline measures aimed at pulling dollar liquidity into the banking system. First, it offered a concessional forex swap facility, effectively absorbing the hedging cost that normally makes FCNR deposits unattractive for banks to offer at competitive rates. Second — and more dramatically — it removed the interest rate ceiling on FCNR(B) deposits for maturities of three to five years, but only for deposits mobilised before September 30, 2026.

The logic is straightforward. With domestic deposit growth slowing to 12 per cent and credit growth holding steady at 17.7 per cent, banks need funding. The rupee has faced pressure from the Iran-linked oil shock and capital outflows. Fresh FCNR dollars help on both fronts. SBI's economists estimate $40-45 billion could flow in through this route; Nomura has pegged the figure higher, at $55 billion, with the bulk expected in August and September.

On June 24, the RBI added another sweetener: banks can now extend loans to non-residents against their FCNR deposits, including through offshore branches and GIFT City operations. They can also issue standby letters of credit against these accounts. For NRIs who want liquidity without breaking their deposit, that is a meaningful addition.

## The Rate Table: Who Is Offering What

The rate dispersion is striking. At one end, smaller and mid-sized banks have moved aggressively:

AU Small Finance Bank has raised its peak FCNR(B) rate to **7.10 per cent** on US dollar deposits, up from 5.15 per cent — a jump of nearly 200 basis points. Yes Bank is in the same territory at **7.05-7.10 per cent**. Karur Vysya Bank and Tamilnad Mercantile Bank have both moved to **7 per cent** for three-to-five-year tenures, up from the 2.6-3.9 per cent range. City Union Bank has matched at **7.10 per cent**. Outlook Money reports that some banks are offering rates touching **7.50 per cent**.

The large private banks have been more measured. HDFC Bank moved to **6 per cent** for three-to-five-year deposits effective June 10. Kotak Mahindra Bank is at **6-6.15 per cent** depending on deposit size. ICICI Bank is at **6.50 per cent**.

State Bank of India, the country's largest bank, has been the most conservative. Its five-year FCNR rate for deposits up to $1 million stands at **5.75 per cent** — up from 3.05 per cent, but still well below what smaller banks are offering.

## What NRIs Should Actually Do

The headline rates look attractive, but several details matter.

**Lock-in period.** These are special promotional rates in most cases, and banks have imposed a one-year lock-in. Premature withdrawal after the lock-in but before maturity will attract a penalty — the exact terms vary by bank.

**Tax treatment.** FCNR(B) deposits remain fully exempt from Indian income tax on both principal and interest. The deposits are held in foreign currency (typically US dollars), which means there is no exchange rate risk during the deposit tenure. Both principal and interest are fully repatriable.

**The September 30 deadline.** The RBI's ceiling removal and hedging subsidy apply only to deposits mobilised before the end of September 2026. Once that window closes, rates will almost certainly snap back. This is a limited-time programme, not a permanent shift.

**Big bank versus small bank.** The rate gap between AU Small Finance Bank at 7.10 per cent and SBI at 5.75 per cent is material over a three-to-five-year horizon. On a $100,000 deposit over five years, the difference works out to roughly $6,750 in additional interest. Against that, larger banks offer more extensive service networks and may be perceived as carrying lower institutional risk.

**Loan against deposit.** The June 24 circular opens a useful option: NRIs can now borrow against their FCNR deposits rather than breaking them. This provides interim liquidity — for a property purchase in India, for instance — while the deposit continues earning interest.

## The Bigger Picture

For the RBI, this is about rupee defence and banking system liquidity, not NRI generosity. But the effect is real: Indian banks have hiked FCNR rates by 300-450 basis points in under a month, the most aggressive repricing in years. The smart play for NRIs with dollars to spare is to lock in before September, compare rates across at least three or four banks, read the premature withdrawal penalty clauses carefully, and think of the loan-against-deposit facility as a useful hedge against needing the money early.

The window is open. It will not stay open forever."""

fcnr_sources = json.dumps([
    {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/money-and-banking/banks-kick-off-rate-hikes-on-fcnr-b-deposits/article71085514.ece"},
    {"name": "Outlook Money", "url": "https://www.outlookmoney.com/personal-finance/bank-that-offers-highest-fcnrb-rate-after-rbi-withdrew-interest-rate-ceiling-for-3-5-years-deposits"},
    {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-rbi-allow-domestic-banks-extend-loans-against-overseas-fx-deposits-2026-06-23/"},
    {"name": "AU Small Finance Bank (PR Newswire)", "url": "https://www.morningstar.com/news/pr-newswire/20260611in35879/au-small-finance-bank-raises-fcnr-deposit-rates-to-710-strengthens-end-to-end-nri-banking-proposition"},
])

articles.append({
    "headline": "The Rate War for NRI Dollars: Indian Banks Are Offering Up to 7.5% on Foreign Currency Deposits",
    "subheadline": "The RBI removed interest rate ceilings and is subsidising hedging costs until September 30. Banks have responded with the most aggressive FCNR repricing in years. Here's what it means for your money.",
    "body": fcnr_body.strip(),
    "slug": "fcnr-rate-war-nri-deposits-banks-7-percent-rbi-september-deadline-20260630",
    "category": "nri-world",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_04.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_04.jpg",
    "image_caption": "The Reserve Bank of India headquarters in Mumbai, which triggered a bank-level rate war with its June FCNR policy changes",
    "image_attribution": "Wikimedia Commons",
    "sources": fcnr_sources,
    "tags": "{NRI,FCNR,RBI,banking,deposits,finance,diaspora}",
    "diaspora_angle": "A practical guide for NRIs weighing the best FCNR deposit rates after the RBI's unprecedented June 2026 policy changes — comparing bank-by-bank offers, tax treatment, lock-in terms, and the September 30 deadline that makes this a limited-time opportunity.",
    "score_total": 78,
    "published_at": NOW,
    "vertical": "nri-world",
    "urgency": "high",
})


# ── insert ───────────────────────────────────────────────────────────────

def insert_article(art):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=art)
    if r.status_code in (200, 201):
        data = r.json()
        row = data[0] if isinstance(data, list) else data
        print(f"  ✅ Inserted: {row.get('slug', '?')} (id={row.get('id','?')})")
        return True
    else:
        print(f"  ❌ FAILED ({r.status_code}): {r.text[:300]}")
        return False


print("=" * 60)
print("NRI World Writer — June 30, 2026")
print("=" * 60)

ok = 0
for i, art in enumerate(articles, 1):
    print(f"\n[{i}/{len(articles)}] {art['headline'][:70]}...")
    # Validate body length
    words = len(art["body"].split())
    print(f"  Word count: {words}")
    if words < 400:
        print(f"  ⚠️  Body too short ({words} words). Skipping.")
        continue
    if insert_article(art):
        ok += 1

print(f"\nDone: {ok}/{len(articles)} articles inserted.")
