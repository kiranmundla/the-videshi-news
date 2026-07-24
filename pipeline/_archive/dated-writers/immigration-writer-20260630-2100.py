#!/usr/bin/env python3
"""Immigration writer — June 30, 2026 evening run.

Two articles:
1. Supreme Court birthright citizenship ruling (Trump v. Barbara) — Indian diaspora angle
2. DOJ birth tourism crackdown — what Indian visa holders need to know
"""

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


# ──────────────────────────────────────────────
# ARTICLE 1: Supreme Court Birthright Ruling
# ──────────────────────────────────────────────

article1_body = """The United States Supreme Court on Tuesday handed the Indian diaspora its most consequential immigration victory in years — and most families on H-1B visas barely knew the fight was happening.

In a 6–3 ruling in *Trump v. Barbara*, the court struck down President Donald Trump's executive order that sought to deny birthright citizenship to children born on American soil to parents without permanent residency. The order, signed on Trump's first day back in office in January 2025, would have classified children of H-1B holders, F-1 students, and other temporary visa holders as non-citizens from the moment of birth.

Chief Justice John Roberts, writing for a 5–4 constitutional majority, was blunt. "The trouble is that there is scant evidence for this dramatically revisionist view," he wrote, dismissing the administration's argument that the 14th Amendment's framers never intended birthright citizenship to extend beyond the children of freed slaves. The amendment's text — "all persons born or naturalized in the United States, and subject to the jurisdiction thereof" — says what it says.

## The numbers behind the relief

Indians are, by a wide margin, the nationality most exposed to the order's reach. In 2023 alone, 72.3 per cent of the 386,000 H-1B visas issued went to Indian nationals. Add F-1 students, L-1 intracompany transferees, and their dependents, and the population of Indian-origin temporary visa holders in America runs well into the hundreds of thousands. Many have children who are American citizens by birth — children who, under Trump's order, would have been rendered stateless.

A study published this year in *Demography*, a peer-reviewed journal from Duke University Press, found that while Latinos would bear the largest absolute impact of ending birthright citizenship, the Asian population — driven heavily by Indian and Chinese temporary visa holders — would experience the largest *relative* impact. The study projected 41 "unauthorised" births per 1,000 unauthorised Asians, compared with 17 per 1,000 among Latinos.

## The Kavanaugh caveat

The ruling was not as clean a victory as the headline suggests. Justice Brett Kavanaugh concurred with the outcome but disagreed with the constitutional reasoning. In his view, the executive order violated existing federal law from the 1940s and 1950s — not the 14th Amendment itself. The distinction matters enormously. If the restriction violates only statute, Congress can change the statute. If it violates the Constitution, only a constitutional amendment can revive it.

Senator Eric Schmitt of Missouri seized on the opening within hours. "Justice Kavanaugh MAY have left Congress a door," he wrote on X. "I'm filing legislation to walk through it." Trump himself urged Congress to act, posting that "No long and unwieldy Constitutional Amendment is necessary!"

For Indian families, this means the legal shield is real but not permanent. A future Congress could, in theory, pass legislation to narrow birthright citizenship — though the five-justice constitutional majority makes any such law vulnerable to an immediate court challenge.

## What this means in practice

The practical effect is immediate and sweeping. Children born in the United States to parents on H-1B, H-4, F-1, L-1, or any other temporary visa remain American citizens, full stop. No agency can deny them passports, Social Security numbers, or any other benefit of citizenship.

For the Indian family navigating the green card backlog — where EB-2 India is currently unavailable until October and wait times stretch into decades — this ruling removes one existential worry. Their American-born children will not be caught in the same bureaucratic limbo that traps their parents.

House Speaker Mike Johnson called the ruling "disappointing" and said Congress would examine the "serious challenges" of birth tourism. But immigration attorneys say any legislative attempt to restrict birthright citizenship for children of legal visa holders would face insurmountable political and legal obstacles. The constituency is too large, the constitutional precedent too settled, and the economic argument — that the children of skilled immigrants disproportionately become high-achieving professionals — too compelling.

For now, the 14th Amendment holds. The children are American. The question is whether Washington will try again."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Supreme Court Settled Birthright Citizenship. For Indian H-1B Families, the Relief Is Real but Fragile",
    "subheadline": "A 6–3 ruling in Trump v. Barbara preserves citizenship for children born to temporary visa holders — but Justice Kavanaugh left Congress a door, and some Republicans are already walking through it.",
    "slug": make_slug("scotus-birthright-citizenship-indian-h1b-families"),
    "category": "immigration",
    "vertical": "immigration",
    "is_editorial": False,
    "diaspora_angle": "Indians hold 72% of H-1B visas and have hundreds of thousands of American-born children whose citizenship was directly threatened by Trump's executive order — this ruling is the most consequential immigration win for the Indian diaspora in years.",
    "tags": ["birthright-citizenship", "supreme-court", "h1b", "14th-amendment", "trump-v-barbara", "indian-diaspora"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/us-supreme-court/supreme-court-rejects-trump-bid-restrict-birthright-citizenship-2026-06-30/"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/30/supreme-court-trump-birthright-citizenship/90733478007/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/06/30/us-news/supreme-court-strikes-down-trump-birthright-citizenship-order/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/politics/policy/supreme-court-trump-birthright-citizenship-ruling-5b01c20c"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/h-1b-workers-kids-would-lose-citizenship-under-birthright-order"},
        {"name": "Duke University Press — Demography", "url": "https://read.dukeupress.edu/demography/article/doi/10.1215/00703370-11897685"}
    ]),
    "score_total": 88,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg/1280px-Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg",
    "image_caption": "The United States Supreme Court building in Washington, D.C., at dusk",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip(),
}


# ──────────────────────────────────────────────
# ARTICLE 2: DOJ Birth Tourism Crackdown
# ──────────────────────────────────────────────

article2_body = """Hours after the Supreme Court affirmed that children born on American soil are American citizens, the Department of Justice made clear it intends to punish anyone who travels to the United States specifically to exploit that fact.

In a memo to all DOJ employees on Tuesday, Assistant Attorney General Colin McDonald directed federal prosecutors to prioritise investigations of "birth tourism" schemes nationwide. The memo, posted on social media by the department's official account, outlined the criminal statutes available: visa fraud, money laundering, identity theft, and wire fraud. "The Department of Justice will zealously protect the sanctity of United States citizenship by investigating and prosecuting those who fraudulently exploit our immigration system," McDonald wrote.

The timing was deliberate. With the constitutional path to restricting birthright citizenship now blocked by the court's ruling in *Trump v. Barbara*, the administration has shifted to enforcement as its primary tool. If it cannot change who qualifies for citizenship, it can raise the cost of getting there fraudulently.

## The machinery is already running

The DOJ memo is not the beginning of this campaign — it is an escalation. In April 2026, Immigration and Customs Enforcement launched a dedicated effort to uncover birth tourism fraud through its Homeland Security Investigations arm. The House Oversight Committee, led by Chairman James Comer, has sent letters to businesses that market maternity services to foreign nationals, including operations in Miami and other cities.

Three recent prosecutions illustrate the pattern. In 2024, a husband-and-wife team running "USA Happy Baby" was sentenced to 41 months in prison for helping Chinese clients give birth in America for fees of tens of thousands of dollars. A Turkish-language birth tourism ring netted its operator 27 months and a million dollars in restitution in 2022. And in 2020, "You Win USA" — a 100-person operation serving over 500 Chinese customers at $40,000 to $80,000 each — sent its founder to prison for three years.

Every major prosecution to date has targeted Chinese nationals. But the enforcement net is widening. The State Department has revoked over 100 visas linked to birth tourism in North Africa alone and dismantled a network involving more than 100 foreign nationals using fraudulent documents in West Africa.

## India is now on the radar

In December 2025, the U.S. Embassy in New Delhi issued an unusually direct advisory: travelling to America on a B-1/B-2 visitor visa with the primary intent of giving birth will result in immediate visa denial. Embassy officials said the warning was triggered by recent spikes in appointment requests from late-term expectant mothers.

The advisory recommended that pregnant travellers carry employer letters, detailed travel itineraries, and physician notes confirming planned medical care in India — documentation designed to establish that childbirth in America, if it happens, is incidental to a legitimate visit rather than its purpose.

For the Indian diaspora, the practical distinction matters. An Indian couple on H-1B and H-4 visas who have a child while lawfully living and working in the United States are not engaging in birth tourism. Their child's citizenship is a consequence of their legal presence, not a scheme. The DOJ's enforcement targets are different: visa applicants who misrepresent the purpose of their travel, intermediaries who market citizenship-by-delivery packages, and organised networks that facilitate the fraud.

## The legislative push

Congress is not standing still. The Ban Birth Tourism Act, filed on 20 May, would bar admission to any foreign national whose primary purpose of entry is to secure citizenship for a child. Representative Andy Ogles of Tennessee filed a separate bill — titled, with characteristic subtlety, the "Anchors Away Act" — seeking to ban "all pregnant aliens from entering the USA."

Neither bill is likely to pass in its current form. But they signal the direction of travel. House Speaker Mike Johnson told reporters that birth tourism "has been abused" and that Congress would "continue to look at that."

For Indian green card applicants already navigating a system that demands years of patience, the message is straightforward: legitimate presence is not under threat. But anyone contemplating a visitor visa with delivery plans should understand that the full weight of federal law enforcement is now pointed in their direction. The DOJ has named its priority. It is not bluffing."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The DOJ Declared War on Birth Tourism. Indian Visa Holders Should Read the Fine Print",
    "subheadline": "After the Supreme Court preserved birthright citizenship, the Justice Department directed prosecutors to prioritise fraud cases — and the U.S. Embassy in Delhi has already started asking questions.",
    "slug": make_slug("doj-birth-tourism-crackdown-indian-visa-holders"),
    "category": "immigration",
    "vertical": "immigration",
    "is_editorial": False,
    "diaspora_angle": "The U.S. Embassy in New Delhi has already warned Indian visa applicants about birth tourism scrutiny, and pregnant travellers on B-1/B-2 visas now face heightened documentation requirements — Indian families on H-1B/H-4 visas are not the target, but they need to understand the distinction.",
    "tags": ["birth-tourism", "doj", "visa-fraud", "uscis", "indian-diaspora", "b1-b2-visa"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/us-doj-directs-prosecutors-prioritize-birth-tourism-probes-following-court-2026-06-30/"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/30/doj-birth-tourism-supreme-court-ruling/90814507007/"},
        {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/30/trump-admin-birth-tourism-crackdown-birthright-citizenship-ruling/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/us-cracks-down-on-birth-tourism-networks-revokes-hundreds-of-visas-worldwide/article69360621.ece"},
        {"name": "VisaHQ", "url": "https://www.visahq.com/discussion/774095/us-embassy-tells-indian-visa-seekers-birth-tourism-will-mean-instant-denial/"}
    ]),
    "score_total": 82,
    "status": "review",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "An open passport displaying travel entry and exit stamps at an airport",
    "image_attribution": "Pexels",
    "body": article2_body.strip(),
}


# ──────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
