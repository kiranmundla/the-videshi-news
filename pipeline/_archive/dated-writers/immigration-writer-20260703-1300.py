#!/usr/bin/env python3
"""Immigration writer — July 3, 2026 1:00 PM run"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

# ──────────────────────────────────────────────────────────────
# ARTICLE 1: Birthright Citizenship SCOTUS Ruling
# ──────────────────────────────────────────────────────────────

article1_body = """The Supreme Court struck down President Trump's executive order denying birthright citizenship to children born on American soil to undocumented or temporary-visa parents. The 5-4 ruling on the constitutional question — widened to 6-3 when Justice Brett Kavanaugh concurred on separate statutory grounds — settles a fight that began hours after Trump's inauguration in January 2025. For the roughly 400,000 Indian H-1B professionals raising families in the United States, it removes an existential uncertainty that had hung over every delivery room in the country for eighteen months.

## What the Court Actually Said

The majority held that the Fourteenth Amendment's Citizenship Clause — "All persons born or naturalized in the United States, and subject to the jurisdiction thereof, are citizens" — covers children born to parents who are in the country illegally or on temporary visas such as H-1B, F-1, or L-1. The decision in *Trump v. Barbara* reaffirmed a principle the Court first established in 1898 in *United States v. Wong Kim Ark* and extended in *Plyler v. Doe* in 1982.

Chief Justice Roberts authored the majority opinion, joined by Justices Sotomayor, Kagan, Jackson, and Barrett. Justice Kavanaugh filed a separate concurrence: he found that the executive order violated federal statutes from the 1940s and 1950s codifying birthright citizenship, but stopped short of calling it a constitutional right. That distinction matters. A constitutional holding requires a constitutional amendment to overturn. Kavanaugh's statutory reasoning means Congress could, in theory, rewrite the relevant statutes.

Senator Eric Schmitt of Missouri seized on the opening within hours. "Justice Kavanaugh MAY have left Congress a door," he wrote on X. "I'm filing legislation to walk through it."

Justice Clarence Thomas authored a blistering dissent, calling the ruling a decision that "devalues American citizenship" and arguing the Fourteenth Amendment was written to secure equality for freed slaves, not to grant automatic citizenship to "the children of all foreign birth tourists and illegal aliens."

## Why Indian Americans Are Celebrating — Carefully

Indian American community organisations and lawmakers treated the ruling as a landmark, albeit one that illuminates how precarious the community's position has become.

The Foundation for India and Indian Diaspora Studies called the decision "especially important" for the nearly 5.2 million Indian Americans, including more than 1.2 million individuals stuck in the employment-based green card backlog and over 400,000 H-1B professionals. "Birthright citizenship has been a cornerstone of realising the American Dream for immigrants," said FIIDS President Khanderao Kand. "Millions of families can now look to the future with greater certainty."

Congresswoman Pramila Jayapal of Washington said the ruling reaffirmed that "Donald Trump is not a king, and he cannot, with the stroke of a pen, change our Constitution." Michigan Congressman Shri Thanedar called it "a major win for civil rights and the rule of law," while Virginia's Suhas Subramanyam, the first Indian American elected to Congress from Virginia, said his colleagues would "continue to push for long overdue, commonsense immigration reform."

## The Kavanaugh Problem

The relief is real but conditional. Kavanaugh's concurrence explicitly declined to constitutionalise birthright citizenship for children of temporary or undocumented parents. His opinion frames the question as one of statutory interpretation — meaning future Congresses could redefine who qualifies.

For Indian families on H-1B visas, this is not an abstract concern. The current Congress has already introduced bills that would shrink H-1B duration from six years to two, cap any single nationality at seven per cent of annual allocations, and end the Optional Practical Training programme that serves as the primary bridge between student visas and work authorisation. If a future Congress with the votes to act decides that children of temporary workers should not receive automatic citizenship, Kavanaugh's reasoning provides a legal pathway.

Had Trump's order stood, an estimated 4.8 million future U.S.-born children would have been stripped of citizenship by 2045, according to the Migration Policy Institute. The number balloons to 12.8 million by 2075.

## The Broader Picture

The birthright victory arrives in a week that has otherwise tightened every constraint Indian immigrants face. The Supreme Court simultaneously greenlit the termination of Temporary Protected Status for over a million people, a signal that executive immigration power remains broad. Immigration court filing fees have nearly tripled — from $110 to $975 to appeal a deportation ruling. Naturalisation fees jumped 75 per cent. EB-2 India is unavailable through the end of the fiscal year.

The children born to Indian H-1B workers in American hospitals are American citizens. That much is settled. What remains unsettled is whether those children's parents will ever be allowed to stay."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Your American-Born Child Is Still American. The Supreme Court Made Sure of That",
    "subheadline": "The Court struck down Trump's birthright citizenship order 6-3, but Justice Kavanaugh left Congress a door that Indian H-1B families should not ignore.",
    "slug": make_slug("scotus-birthright-citizenship-indian-h1b-families"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B families with US-born children had their citizenship rights reaffirmed, but the Kavanaugh concurrence means Congress could still legislate away birthright citizenship for children of temporary visa holders.",
    "tags": ["birthright-citizenship", "scotus", "h1b", "fourteenth-amendment", "indian-american", "trump-v-barbara"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "New York Post", "url": "https://nypost.com/2026/07/01/us-news/supreme-court-strikes-down-trump-birthright-citizenship-order/"},
        {"name": "IANS Live", "url": "https://www.ianslive.in/news/us-supreme-court-birthright-citizenship-ruling-wins-praise-from-indian-americans-20260701"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/07/01/supreme-court-birthright-citizenship/"},
        {"name": "Fox News", "url": "https://www.foxnews.com/politics/government-watchdog-targets-weapons-mass-reproduction-supreme-court-ruling"},
        {"name": "Nolo", "url": "https://www.nolo.com/legal-updates/2026-immigration-legal-updates.html"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Exterior_of_Supreme_Court_Building_20240601.jpg/1280px-Exterior_of_Supreme_Court_Building_20240601.jpg",
    "image_caption": "The United States Supreme Court building in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}

# ──────────────────────────────────────────────────────────────
# ARTICLE 2: Trump's Gold Card Immigration Programme
# ──────────────────────────────────────────────────────────────

article2_body = """Treasury Secretary Howard Lutnick announced in May that the first Gold Card applicant had been approved. The fanfare was considerable. The programme, which lets wealthy foreign nationals invest $1 million or $2 million for a fast-tracked green card, was supposed to represent America's red carpet for the world's best and brightest. Three months in, the carpet is gathering dust.

Research by immigration attorney Mona Shah found that USCIS has received just 338 Gold Card requests since the programme launched. Of those, only 165 successfully processed the filing fee. Of those 165, only 59 submitted the actual Form I-140G petition. One has been approved. The rest are pending, in litigation, or abandoned.

For the 1.2 million Indian nationals languishing in the employment-based green card backlog — some with priority dates stretching back to 2013 — the Gold Card was briefly floated as a possible escape hatch. It is not.

## The Per-Country Trap

The Gold Card's fatal flaw for Indian immigrants is structural. The programme does not create a new visa category with its own allocation. Instead, it slots applicants into existing employment-based preference categories: EB-1 for those claiming "extraordinary ability" or EB-2 for "exceptional ability" with a national interest waiver. Both categories remain subject to the per-country limit that caps any single nation at roughly seven per cent of annual employment-based visas.

That limit is the reason Indian professionals wait decades for green cards in the first place. The July 2026 Visa Bulletin confirmed that EB-2 India is completely unavailable through September 30 — no immigrant visas will be issued in the category until the new fiscal year begins on October 1. EB-1 India has retrogressed to October 15, 2022, meaning only applicants with priority dates before that can receive final action. Even EB-5, the traditional investor route at $800,000, is now showing strain for Indian nationals.

An Indian engineer who writes a $2 million cheque for a Gold Card will still face years of waiting behind the same per-country bottleneck as someone who filed an employer-sponsored I-140 petition a decade ago.

## Why the Uptake Is So Low

Beyond the India-specific backlog problem, the Gold Card faces design issues that explain its dismal numbers.

First, the qualifying standard is unclear. The programme tries to squeeze wealthy investors into visa categories designed for people with demonstrated professional excellence. Handing over money is not, by any reading of immigration law, proof of "extraordinary ability in the sciences, arts, education, business, or athletics." Legal challenges are already underway — the American Association of University Professors has filed suit in *AAUP v. Department of Homeland Security*, arguing the programme distorts the statutory criteria for EB-1 and EB-2 visas.

Second, the price point occupies an awkward middle ground. At $1 million to $2 million, it is too expensive for most H-1B professionals and too cheap to attract the ultra-wealthy who have simpler options. The existing EB-5 investor programme requires $800,000 in a targeted employment area and comes with a clearer legal framework. Wealthy individuals from countries without backlog problems — most of the world, in practice — can use EB-5 or EB-1A with less legal risk.

Third, the programme exists in a regulatory grey zone. The Gold Card was announced via executive action, not legislation. Its authority derives from a creative reinterpretation of existing visa categories, which means any future administration could revoke it or any court could strike it down. For someone committing $2 million, regulatory permanence matters.

## The Deeper Irony

The Gold Card's failure is a microcosm of the immigration system's dysfunction for Indian nationals. The problem was never a lack of money or talent. Indian H-1B holders are among the highest-paid workers in America, with median salaries well above $100,000. Indian-born founders have created companies worth hundreds of billions of dollars. The constraint is a per-country cap written into law in 1990, when India sent far fewer immigrants and nobody anticipated that one country would account for 71 per cent of H-1B beneficiaries.

Every workaround — whether it is the Gold Card, the EB-5 programme, the EB-1A "extraordinary ability" self-petition, or the national interest waiver — eventually runs into the same wall. The per-country limit does not care how much money you have, how many patents you hold, or how many American jobs your company created. It cares where you were born.

The EAGLE Act, which would have eliminated per-country caps on employment-based green cards, failed again in the most recent legislative session. Congressional attention has shifted to restricting H-1B visas, not fixing the backlog. The Gold Card, for all its branding, does not change the arithmetic.

One applicant has been approved. Over a million Indians remain in line."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Trump's Gold Card Has 59 Real Applicants. The Green Card Backlog Has a Million Indians",
    "subheadline": "The $2 million fast-track green card programme was supposed to roll out the red carpet. Instead, per-country caps make it useless for the very people most desperate for a solution.",
    "slug": make_slug("gold-card-59-applicants-indian-green-card-backlog-per-country"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The Gold Card programme funnels applicants into EB-1/EB-2 categories still subject to per-country caps, making it essentially useless for Indians who face the longest green card backlogs — EB-2 India is unavailable through September 2026.",
    "tags": ["gold-card", "green-card", "per-country-cap", "eb1", "eb2", "indian-immigrant", "backlog"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Nolo - 2026 Immigration Legal Updates", "url": "https://www.nolo.com/legal-updates/2026-immigration-legal-updates.html"},
        {"name": "Capitol Immigration Law Group - July 2026 Visa Bulletin", "url": "https://cilawgroup.com/2026/06/18/july-2026-visa-bulletin/"},
        {"name": "WR Immigration - EB-2 India Unavailable", "url": "https://wolfsdorf.com/eb-2-india-unavailable-through-september-30-2026/"},
        {"name": "Wolfsdorf - June 2026 Visa Bulletin Analysis", "url": "https://wolfsdorf.com/june-2026-visa-bulletin-sharp-retrogression/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8850753/pexels-photo-8850753.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A 'We the People' scroll on an American flag — the constitutional promise at the heart of the immigration debate",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}

# ──────────────────────────────────────────────────────────────
# Insert articles
# ──────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
