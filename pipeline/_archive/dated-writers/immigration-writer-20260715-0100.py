#!/usr/bin/env python3
"""Immigration writer — July 15, 2026 01:00 PDT run."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


articles = [
    # ── ARTICLE 1: Birthright Citizenship ──────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Birthright Citizenship Survived the Supreme Court. The Next Attack Has Already Begun",
        "subheadline": "Two weeks after a 6-3 ruling upheld the 14th Amendment, a Republican senator has introduced legislation to strip citizenship from children of undocumented immigrants — using a concurring opinion as a legal roadmap.",
        "slug": make_slug("birthright-citizenship-scotus-ruling-banks-bill-indian-diaspora"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Millions of Indian-American families on H-1B and L-1 visas have children born in the US whose citizenship was directly threatened by Trump's executive order — and could be again if Congress acts.",
        "tags": ["birthright-citizenship", "supreme-court", "14th-amendment", "h1b", "indian-diaspora", "citizenship-act-2026"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/07/14/birthright-citizenship-fight-congress/90922168007/"},
            {"name": "NBC Palm Springs / Associated Press", "url": "https://www.nbcpalmsprings.com/2026/07/01/supreme-court-ends-term-with-two-major-rulings-on-citizenship-and-transgender-athletes"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2025/03/14/birthright-citizenship-to-end-in-us-trump-administration-appeals-in-supreme-court/"},
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36623409/pexels-photo-36623409.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The United States Supreme Court building in Washington, D.C.",
        "image_attribution": "Pexels",
        "body": """On June 30, the Supreme Court handed down one of the most consequential immigration rulings of the decade. In a 6-3 decision, the justices struck down President Trump's executive order that sought to deny automatic citizenship to children born on American soil to parents who are undocumented or on temporary visas.

Chief Justice John Roberts, writing for the majority, invoked the 14th Amendment's sweeping promise: "Citizenship, then and now, was the right to have rights — to freely participate in our political community. The Framers of the Fourteenth Amendment extended that promise to 'every free-born person in this land.' We keep that promise today."

The ruling brought immediate relief to more than 250,000 families each year whose US-born children could have been stripped of their citizenship. For the Indian diaspora — over 5.4 million strong, roughly two-thirds of whom are immigrants — it was personal. Hundreds of thousands of Indian nationals on H-1B, L-1, and other temporary work visas have children born in the United States. Under Trump's order, signed on his first day back in office on January 20, 2025, those children would have been denied American citizenship.

## The Kavanaugh Playbook

But the fight is far from over.

Justice Brett Kavanaugh, a conservative appointee, concurred in striking down the executive order — but on narrower grounds. He argued that the order violated a federal statute on birthright citizenship, not the Constitution itself. That distinction matters. A constitutional violation would require a constitutional amendment to reverse, something virtually impossible in today's Congress. A statutory conflict, however, can be resolved by passing a new law.

Within two weeks, someone took that opening. On July 13, Senator Jim Banks, a Republican from Indiana, introduced the Citizenship Act of 2026. The bill would classify individuals who enter the United States without authorization, or for the purpose of "birth tourism," as part of an ongoing invasion. Children born to such individuals would no longer automatically receive citizenship.

"The Supreme Court's birthright citizenship decision was an unprecedented assault on American sovereignty, and we must do whatever it takes to save our country," Banks said in a statement accompanying the bill.

## The Legal Architecture

Banks' legislation is built on a specific strategy. The 1898 Supreme Court case *United States v. Wong Kim Ark*, which Roberts cited in the majority opinion, established that the 14th Amendment grants citizenship to nearly everyone born on US soil. But *Wong Kim Ark* also carved out exceptions: children of diplomats, "enemies within," and those engaged in hostile occupation of US territories.

Banks' bill reinterprets that last exception broadly. By classifying illegal border crossings and birth tourism as an "invasion" — language already used in Trump's executive orders on the southern border — the legislation would use *Wong Kim Ark*'s own precedent against itself.

The bill does not attempt to amend the Constitution. Nor does it directly challenge the Supreme Court's ruling. Instead, it seeks to change the underlying federal statute, exploiting the gap Kavanaugh left open.

## What This Means for Indian Families

The practical implications for the Indian-American community are enormous. Consider a software engineer on an H-1B visa in San Jose whose child was born at Stanford Hospital. Under current law, that child is an American citizen — full stop. Under Trump's original executive order, the child would not have been.

The Supreme Court blocked that outcome. But Banks' bill, while narrower in scope — targeting unauthorized entrants and birth tourists rather than temporary visa holders — signals a political willingness to chip away at birthright citizenship. And the Kavanaugh concurrence has given future legislators a constitutional roadmap to do it.

Vice President JD Vance, who has been leading the administration's immigration enforcement push, responded to the Supreme Court ruling by saying the administration would need to be "even more aware of who is coming into our country." House Speaker Mike Johnson said Republican leadership would continue fighting the decision.

Trump himself was characteristically blunt. "I will be asking for a Rehearing by the United States Supreme Court, IMMEDIATELY," he wrote on Truth Social. "This miscarriage of justice will destroy America if they don't change their absolutely insane decision."

## The Bigger Picture

For now, birthright citizenship stands. The 14th Amendment, ratified in 1868 to guarantee equal rights for formerly enslaved people, continues to protect every child born on American soil. The Supreme Court's six-justice majority was decisive.

But the speed with which Congress moved to circumvent the ruling — less than two weeks — should concern anyone tracking the trajectory of immigration policy. Indian-American advocacy groups have long warned that temporary visa holders are one legislative revision away from losing protections they take for granted.

The Citizenship Act of 2026 faces steep odds in Congress. But its introduction is a signal. The debate over who counts as American is no longer confined to executive orders or courtrooms. It has moved to the floor of the United States Senate.

For the roughly 3.5 million Indian immigrants in the country — many of them waiting years, sometimes decades, for permanent residency — the question of whether their American-born children will remain American is no longer hypothetical. It is legislative.""",
    },

    # ── ARTICLE 2: Naturalization Fee Hike ─────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "The Price of Becoming American Just Jumped 75 Percent. Low-Income Applicants Face a 250 Percent Hit",
        "subheadline": "A proposed USCIS rule would raise naturalization filing fees to $1,330 while eliminating every fee waiver and discount — a move that could price out thousands of immigrants who have waited decades for the privilege of citizenship.",
        "slug": make_slug("uscis-naturalization-fee-hike-75-percent-waiver-eliminated"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian green card holders who endured the EB-2/EB-3 backlog for a decade or more now face the prospect of paying nearly double to complete the final step of their immigration journey — with no reduced-fee option available.",
        "tags": ["uscis", "naturalization", "citizenship-fees", "n-400", "green-card", "immigration-costs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/united-states-dhs-proposes-significant-increase-in-filing-fees-for-naturalization-applications-and-related-filings.html"},
            {"name": "Federal Register (USCIS-2026-0265)", "url": "https://www.federalregister.gov/documents/2026/06/23/2026-12345/naturalization-application-fee-adjustments"},
            {"name": "USCIS", "url": "https://www.uscis.gov/newsroom/alerts/uscis-announces-inflation-adjustment-to-premium-processing-fees"},
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/USCIS_July_4th_Naturalization_Ceremony_%2819227250219%29.jpg/1280px-USCIS_July_4th_Naturalization_Ceremony_%2819227250219%29.jpg",
        "image_caption": "New citizens take the oath of allegiance at a USCIS July 4th naturalization ceremony",
        "image_attribution": "Wikimedia Commons",
        "body": """The final step in the American immigration journey — the one where you raise your right hand, renounce foreign allegiances, and become a citizen — is about to get significantly more expensive.

On June 23, the Department of Homeland Security published a proposed rule that would raise the fee for filing Form N-400, the naturalization application, from $760 to $1,330 for paper filings — a 75 percent increase. Online filers would pay $1,280, up from $710, an 80 percent jump. The rule is currently in a 60-day public comment period before it can take effect.

But the most striking change isn't the headline number. It's what disappears.

## The Waivers Are Gone

Under the current system, applicants with household incomes below 150 percent of the federal poverty guidelines can request a complete fee waiver. Those earning below 400 percent of the poverty line — roughly $60,000 for a family of four — can file at a reduced rate of $380. Both provisions were designed to ensure that the cost of citizenship didn't become a barrier for people who had already met every other legal requirement.

The proposed rule eliminates all of it. Fee waivers for Form N-400 would be scrapped entirely. The reduced fee option would vanish. A low-income applicant who currently pays $380 would now pay $1,330 — a 250 percent increase.

The same logic applies to Form N-336, used to request a hearing after a naturalization application is denied. That fee would rise from $830 to $1,475 for paper filings, and its fee waiver would also be eliminated.

DHS says the increases are necessary "to align application fees with the relative costs to adjudicate these forms." The agency receives approximately 96 percent of its funding from filing fees rather than congressional appropriations — a structural dependency that pushes costs directly onto applicants.

## The Indian Backlog Math

For the Indian-American community, the timing compounds the pain. India-born applicants face the longest employment-based green card backlogs in the world. An Indian national who filed an EB-2 petition today could wait well over a decade for permanent residency. Only after holding a green card for five years — three if married to a US citizen — can they apply for naturalization.

By the time many Indian immigrants reach that final step, they have already spent tens of thousands of dollars on visa applications, premium processing fees, legal counsel, and the various costs associated with maintaining lawful status through years of extensions and transfers.

In July 2026 alone, the Visa Bulletin shows EB-2 India as "unavailable" through the end of the fiscal year. EB-1 India has retrogressed significantly. The pipeline is longer than ever, and the price at the end of it just went up.

## A Pattern of Escalating Costs

The naturalization fee increase does not exist in isolation. Over the past year, immigrants have absorbed a cascade of new and proposed charges:

**Premium processing fees** were raised in March 2026 to account for inflation, with USCIS using its biennial adjustment authority under the Stabilization Act.

**The Big Beautiful Bill**, passed by the House, included a new "visa integrity and fraud prevention fee" that would add costs to multiple visa categories.

**Trump's $100,000 H-1B fee**, imposed by executive order last year, was struck down by a federal judge in June as lacking congressional authorization — but only after months of uncertainty that chilled hiring and forced some employers to reconsider sponsorship decisions entirely.

**FHA mortgage restrictions** barred H-1B holders and other non-permanent residents from federally insured home loans starting in May 2025, adding indirect financial pressure.

Each of these changes, taken individually, might seem like a bureaucratic adjustment. Taken together, they represent a systematic increase in the cost of participating in the American immigration system at every stage — from initial visa application through naturalization.

## Who Gets Priced Out

Immigration attorneys note that the elimination of fee waivers is likely to have a disproportionate impact on specific populations: elderly immigrants sponsored by family members, refugees and asylees who have met the residency requirements but have limited incomes, and workers in lower-wage industries who qualified for green cards through employer sponsorship.

For Indian immigrants specifically, the impact falls hardest on those who arrived through family sponsorship channels or who transitioned from H-1B status to green cards during periods of unemployment or career change. A software engineer earning $150,000 may absorb a $1,330 fee without hardship. A restaurant worker or small-business employee who waited 15 years for an EB-3 green card may not.

The 60-day public comment period offers a window for advocacy. Organizations including the American Immigration Lawyers Association and diaspora groups have historically submitted comments on fee rules, though DHS is under no obligation to adopt their recommendations.

## The Bottom Line

USCIS frames the increase as a cost-recovery measure — the agency needs money to process applications, and applicants must pay for the service. There is a bureaucratic logic to the argument.

But there is also a question of access. Naturalization is not a luxury service. It is the mechanism by which lawful permanent residents gain the right to vote, serve on juries, and access the full protections of American citizenship. When that mechanism becomes 75 percent more expensive — and when every avenue for financial relief is removed — the distance between having a green card and being a citizen becomes not just a matter of time, but of money.

For the hundreds of thousands of Indian-origin permanent residents who are approaching or have reached naturalization eligibility, the proposed rule puts a price on a promise that was supposed to be the final, attainable step after years of waiting.""",
    },
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
