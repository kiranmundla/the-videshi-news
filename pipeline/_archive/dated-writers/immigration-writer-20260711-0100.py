#!/usr/bin/env python3
"""Immigration writer - 2026-07-11 01:00 AM PT run"""

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


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Supreme Court Saved Birthright Citizenship. Trump Wants a Do-Over",
        "subheadline": "A 6-3 ruling affirmed that children born on American soil to parents on temporary visas are citizens under the 14th Amendment. The president is seeking a rehearing he is unlikely to get.",
        "slug": make_slug("scotus-birthright-citizenship-upheld-trump-rehearing-indian-families"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Over 5.4 million Indians live in the US, with two-thirds on immigrant or temporary visas. Tens of thousands of Indian families on H-1B and H-4 visas have US-born children whose citizenship was directly at stake in this case.",
        "tags": ["birthright-citizenship", "supreme-court", "14th-amendment", "h1b", "indian-americans", "trump"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "NBC/CNN", "url": "https://www.nbcpalmsprings.com/2026/06/29/supreme-court-blocks-trumps-bid-to-limit-birthright-citizenship"},
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/07/09/trump-supreme-court-rehear-birthright-citizenship/"},
            {"name": "Fox News", "url": "https://www.foxnews.com/politics/trump-asks-supreme-court-rehear-birthright-citizenship"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/supreme-court/birthright-citizenship-ruling-rehearing"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/birthright-citizenship-to-end-in-us-trump-administration-appeals-in-supreme-court/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Exterior_of_Supreme_Court_Building_20240601.jpg/1280px-Exterior_of_Supreme_Court_Building_20240601.jpg",
        "image_caption": "The United States Supreme Court building in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": """For Indian families scattered across American suburbs — Plano, Fremont, Edison, Bellevue — the Supreme Court's ruling on birthright citizenship landed as relief wrapped in a warning.

The court voted 6-3 to strike down President Trump's executive order, which sought to deny automatic citizenship to children born on US soil to parents in the country illegally or on temporary visas. Chief Justice John Roberts, writing for the majority, held that the 14th Amendment's citizenship clause covers "all persons born" in the United States and "subject to the jurisdiction thereof" — and that includes the children of H-1B holders, F-1 students, and undocumented immigrants alike.

The ruling itself is not new. Lower courts had blocked the order within days of Trump signing it on his first day back in office, so it never took effect. What is new is the finality — and the fury that followed.

## What the ruling actually says

Five justices held that the executive order violated the Constitution. Conservative Justice Brett Kavanaugh agreed it should be struck down but preferred narrower grounds: he said the order violated federal law without reaching the constitutional question.

Three justices dissented. Justice Clarence Thomas, in a 91-page opinion, argued that the citizenship clause was meant to guarantee citizenship to people "born and domiciled" in the United States, not to the children of every temporary visitor. Justice Neil Gorsuch went further, writing flatly: "Children born to temporary visitors in this country, whether here lawfully or unlawfully, are not citizens."

Justice Samuel Alito, in his own 39-page dissent, warned that the ruling "preserves a powerful incentive to enter or remain in this country illegally" and called out the birth tourism industry specifically.

## Trump pushes for a second chance

Within days, Trump called the decision "absolutely insane" and announced he would seek a rehearing — a procedural move that requires a majority of the sitting justices to agree. Given that six voted against him, the odds are steep.

"American citizenship is not for sale," Trump wrote on Truth Social, claiming that signs advertising birth packages were already going up along the southern border. He urged Congress to pass legislation overturning birthright citizenship, though the majority's constitutional framing means that would likely require amending the Constitution itself — a process that demands two-thirds of both chambers of Congress and three-fourths of state legislatures.

House Speaker Mike Johnson said he would support a legislative effort but offered no details on what such a bill would look like.

## Why this matters to every Indian family on a temporary visa

The executive order, had it survived, would have denied citizenship to babies born after February 19, 2025, to parents on H-1B, H-4, L-1, F-1, and other temporary visas. It would not have applied retroactively, but the chilling effect was immediate. Immigration attorneys reported a spike in inquiries from Indian couples on H-1B visas asking whether their US-born children were safe.

Over 5.4 million Indians live in the United States, roughly 1.5 percent of the country's population. Two-thirds are immigrants, and a large share hold temporary work or student visas. For this community, birthright citizenship is not an abstraction. It is the mechanism by which their American-born children access schools, healthcare, and eventually, the right to sponsor their own parents for green cards.

The ruling preserves that mechanism — for now. But the three dissenting opinions offer a roadmap for future challenges. And the administration's request for rehearing, however unlikely to succeed, signals that the fight is not over.

## What comes next

The losing party has 25 days from the ruling to file a rehearing petition. A majority of justices would need to agree, which means at least one justice from the majority would have to change position. Legal experts call this extremely unlikely.

The more plausible path is legislative. Several Republican members of Congress have called for a constitutional amendment, though such efforts have failed repeatedly over the past two decades. The political appetite is there; the procedural math is not.

For Indian families, the practical advice from immigration attorneys remains unchanged: birthright citizenship is settled law. Children born on US soil are citizens. But the margin — six votes — is narrower than many expected. And the dissents, with their emphasis on "temporary visitors" and "domicile," read less like losing arguments and more like opening briefs for the next case."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "It Now Costs $975 to Appeal Your Deportation. The Government Calls It a Fee Adjustment",
        "subheadline": "The Justice Department proposed tripling some immigration court filing fees, the latest in a cascade of cost increases that immigration advocates say is pricing people out of their right to a hearing.",
        "slug": make_slug("eoir-immigration-court-fees-triple-appeal-deportation-975"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals who face removal proceedings — including green card holders charged with certain offenses — now confront dramatically higher costs to appeal adverse rulings, adding a financial barrier on top of years-long backlogs.",
        "tags": ["immigration-court", "eoir", "filing-fees", "deportation", "appeals", "naturalization"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CNN", "url": "https://www.nbcpalmsprings.com/2020/02/27/trump-administration-looks-to-triple-fees-for-some-immigration-court-filings"},
            {"name": "American Immigration Council", "url": "https://www.americanimmigrationcouncil.org/litigation/challenging-drastic-immigration-court-fee-increases"},
            {"name": "National Immigrant Justice Center", "url": "https://immigrantjustice.org/staff/blog/explainer-trump-and-congresss-punishing-new-immigration-fees"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/gop-aims-to-jail-and-deport-more-migrants-hike-legal-fees"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/11505601/pexels-photo-11505601.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A gavel resting on US dollar bills with the American flag, symbolizing the intersection of law and cost in immigration proceedings",
        "image_attribution": "Pexels",
        "body": """The price of fighting your deportation case just went up. Significantly.

The Trump administration introduced a proposed rule this week that would triple some immigration court filing fees. The headline number: appealing an immigration judge's decision, which currently costs $110, would cost $975 under the new schedule. Two forms used by people applying for cancellation of removal — a form of relief that allows certain long-term residents to avoid deportation — would jump from $100 to more than $300.

The rule, published Friday in the Federal Register by the Justice Department's Executive Office for Immigration Review (EOIR), is not yet final. It must go through a public comment period before it can take effect. But it arrives in a context that makes it feel less like a policy adjustment and more like a pattern.

## A cascade of cost increases

This is not the first fee hike to hit immigrants in recent months. Last November, the administration proposed charging for asylum applications for the first time in American history, along with an 83 percent increase in the naturalization application fee. In 2025, Congress passed H.R.1, which imposed new, non-waivable fees on asylum seekers, increased the cost of appeals, and even created a fee for children seeking protection from abuse under the Special Immigrant Juvenile Status program.

The cumulative effect is striking. An immigrant facing deportation who wants to apply for relief and appeal an unfavorable ruling now confronts a bill that can easily exceed $1,000 in filing fees alone — before paying a lawyer.

EOIR's justification is straightforward: "The fees have remained static, not accounting for inflation or any other intervening changes in EOIR's processing costs." The agency says the increases reflect what it actually costs to process the paperwork.

## The access-to-justice problem

Immigration advocates see it differently. The American Immigration Council, which has challenged earlier versions of these fee increases in federal court, argues that the hikes are designed to deter immigrants from exercising their legal rights. In a previous round of similar proposals during Trump's first term, a federal judge blocked the increases, finding that EOIR had failed to consider their impact on nonprofit legal service providers and pro bono attorneys who represent immigrants who cannot afford counsel.

The math is unforgiving. Immigration courts do not provide lawyers to people facing deportation, unlike criminal courts. An estimated 63 percent of immigrants in removal proceedings lack legal representation. For those who do find pro bono counsel, the organizations providing that representation absorb the filing costs. Tripling those costs means fewer cases taken, fewer appeals filed, and more people deported without their day in court.

"Dramatically increased fees for seeking appeals or reviews of negative decisions ensure that many people will be 'priced out' of seeking review of erroneous denials," the National Immigrant Justice Center wrote in its analysis of the fee structure.

## What this means for the Indian diaspora

Most Indian Americans will never see the inside of an immigration court. But the system is closer than many think. Green card holders convicted of certain offenses — including some that carry no prison time — can be placed in removal proceedings. The Supreme Court recently ruled in a separate case that green card holders can be denied reentry at the border, expanding the universe of people who might find themselves before an immigration judge.

For the roughly 1.2 million Indians with pending green card applications, many of whom hold temporary status for years or decades while waiting, any brush with the system can trigger removal proceedings. The cost of appealing an adverse ruling — now potentially $975 — adds a financial dimension to what is already an agonizing process.

There is also the naturalization question. The 83 percent fee increase proposed for citizenship applications hits Indian nationals disproportionately. Indians face the longest employment-based green card backlogs in the world. By the time many finally become eligible for naturalization, they have spent 15 to 20 years in the United States. A sharp fee increase at the finish line feels less like inflation adjustment and more like a toll.

## The fine print

The proposed rule is open for public comment before it can take effect. The comment period gives advocacy organizations, legal aid groups, and affected individuals a window to push back. In 2021, a similar comment process helped build the record that led a federal judge to block the previous version of these fee increases.

Some applicants may qualify for fee waivers, though the proposed rule's waiver provisions are more limited than what advocates have pushed for. And the fees imposed directly by Congress through H.R.1 are statutory — they cannot be challenged through the EOIR rulemaking process.

For now, the existing fee schedule remains in effect. But the direction is clear. Immigration in America is becoming, dollar by dollar, a system that works better for those who can afford it."""
    }
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
