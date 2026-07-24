#!/usr/bin/env python3
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
        "headline": "The Government Says It Can Charge You $100,000 to Marry a Foreigner — A Federal Judge Wants Receipts",
        "subheadline": "In a Boston courtroom on Friday, a DOJ lawyer told a skeptical judge that presidential immigration power has essentially no ceiling — and 20 state attorneys general said that argument proves their case.",
        "slug": make_slug("boston-court-hearing-100k-h1b-fee-judge-sorokin-state-ag"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The outcome of this case could determine whether the $100K H-1B fee — which has already cratered new visa applications — survives or gets struck down. For the roughly 400,000 Indian H-1B holders and their employers, this hearing may be the most consequential two hours of the year.",
        "tags": ["h1b", "100k-fee", "court-challenge", "uscis", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/government/us-judge-questions-scope-trumps-power-impose-100000-h-1b-visa-fee-2026-05-29/"},
            {"name": "Lexology", "url": "https://www.lexology.com/library/detail.aspx?g=100k-h1b-fee-fast-tracked"},
            {"name": "Envoy Global", "url": "https://www.envoyglobal.com/resources/lawsuit-challenges-100000-h1b-visa-entry-fee"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7178551/pexels-photo-7178551.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """U.S. District Judge Leo Sorokin spent Friday morning doing what federal judges occasionally do best: asking a government lawyer to follow his own logic to its conclusion and watching the answer land badly.

The setting was a Boston courtroom. The case, *California v. Mullin*, is one of at least three active lawsuits challenging the Trump administration's $100,000 fee on new H-1B visa petitions — a fee announced by presidential proclamation last September and widely regarded as the single most effective tool the administration has deployed to shrink legal immigration without touching a single statute.

## Eighty-five payments

The numbers tell the story before the lawyers do. As of mid-February, exactly 85 employers had paid the $100,000 fee, according to a government filing. Before the proclamation, employers typically paid between $2,000 and $5,000 in H-1B petition fees. The program offers 65,000 visas annually, plus 20,000 for workers with advanced degrees.

Do the arithmetic: a program designed to serve 85,000 beneficiaries a year now has 85 paying customers. The fee hasn't modified the H-1B program. It has functionally ended it for new applicants.

Tiberius Davis, the DOJ lawyer defending the fee, did not dispute this. "The effect is to incentivize companies to train up and hire American workers," he told the court, arguing that the president had imposed the fee under his "sweeping" authority to restrict entry of foreign nationals deemed detrimental to U.S. interests.

## The hypotheticals

Sorokin, an Obama appointee, accepted that the statutory language is broad. "It's clearly broad language," he said. Then he started testing its limits.

Could the president, under this theory, impose a $100,000 fee on Americans who want to marry non-citizens in order for those spouses to enter the country? Could he force a company seeking to bring in a foreign worker to forfeit 10% of its equity to the government?

Davis's answer was striking in its candor: the president possibly could do those things. "It's a very sweeping power," he said.

For any Indian engineer on an H-1B watching this exchange from a laptop in Sunnyvale or Jersey City, that answer lands differently than it does in a law review article. The government is not just defending a specific fee. It is arguing for a theory of executive power over immigration that has no articulable boundary — one where the president can unilaterally set the price of admission at whatever number discourages people from applying.

## The tariff card

James Richardson, arguing for California and the coalition of 20 state attorneys general, played the card the states had been holding since February: the Supreme Court's ruling striking down Trump's sweeping tariffs imposed under national emergency authority.

The parallel is hard to miss. In the tariff case, the Court found that Congress does not hand over its taxing power through ambiguous statutory language. Richardson argued the same principle applies here: what the administration calls a "fee" is functionally a tax on H-1B applications, imposed without congressional authorization.

"Congress does not delegate a tax authority in ambiguous language," Richardson told the court.

The argument matters because the only other federal court to rule on the $100,000 fee — Judge Beryl Howell in Washington, D.C. — upheld it in December 2025, finding the president's immigration powers broad enough to encompass it. That ruling is now on appeal to the D.C. Circuit, with expedited briefing already completed. If Sorokin reaches a different conclusion, the split between circuits would accelerate the path to the Supreme Court.

## What this means for Indian H-1B holders

The $100,000 fee has not merely raised costs. It has frozen a pipeline. Companies that once sponsored dozens of H-1B workers annually have pulled back entirely. The FY2027 H-1B registration season saw a 38% collapse in applications. For Indian nationals — who historically account for roughly 70% of all H-1B approvals — the fee represents the sharpest single restriction on legal work immigration in decades.

If Sorokin rules for the states, the fee could be enjoined in the 20 plaintiff states, creating a patchwork where H-1B sponsorship costs depend on which state filed the petition. If the D.C. Circuit reverses Howell, the fee could be suspended nationwide. And if the circuits split, the Supreme Court will almost certainly take the case in its next term.

Sorokin did not indicate when he would rule. But for the first time in eight months, a federal judge has looked at the government's argument for unlimited presidential power over immigration fees and responded with the most dangerous question a lawyer can face: "Is there any limit?"

The government said it couldn't name one. That may be the answer that loses the case."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Seventy-Two Billion Dollars, One Side Deal, and a Bill That Can't Get Off the Senate Floor",
        "subheadline": "The largest immigration enforcement funding package in American history missed its deadline because Republicans can't agree on a $1.8 billion IRS fund that has nothing to do with immigration.",
        "slug": make_slug("72-billion-reconciliation-immigration-stalled-irs-fund"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The reconciliation bill doesn't just fund ICE raids — it contains fee increases and enforcement expansion that would reshape the legal immigration system Indian families navigate daily, from green card applications to work permits.",
        "tags": ["reconciliation", "congress", "ice-funding", "immigration-enforcement", "legislation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/05/29/irs-weaponization-fund-immigration-enforcement-funding/"},
            {"name": "CNN", "url": "https://www.cnn.com/2026/04/22/politics/senate-gop-70b-immigration-plan/index.html"},
            {"name": "American Immigration Council", "url": "https://www.americanimmigrationcouncil.org/research/reconciliation-spending-provisions-immigration-enforcement-border"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29704418/pexels-photo-29704418.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """The Senate left Washington for Memorial Day recess on May 21 without sending President Trump the immigration enforcement reconciliation bill he wanted on his desk by June 1. The reason has almost nothing to do with immigration.

A $1.8 billion anti-weaponization fund — born from a settlement between Trump and the IRS over the leak of his tax returns — has become the obstacle that neither Republican leadership nor the White House can clear. Multiple GOP senators want guardrails on the fund, including a prohibition on payments to violent criminals. Acting Attorney General Todd Blanche met with the Republican caucus on May 21 and declined to agree to that condition. Democrats, sensing an opening, are preparing amendments that could fracture the majority entirely.

Meanwhile, the largest immigration enforcement funding package ever proposed sits in legislative purgatory.

## The numbers

The reconciliation bill would direct $72 billion to immigration enforcement through 2029. The breakdown: $30.73 billion to Immigration and Customs Enforcement, $22.57 billion to Customs and Border Protection, and $2.5 billion in broader Department of Homeland Security appropriations. By comparison, ICE's total budget in fiscal year 2024 was roughly $9.5 billion. This bill would more than triple that agency's resources over four years.

The bill passed the House earlier this year. Senate GOP leaders unveiled their version in April after months of failing to resolve a parallel DHS shutdown standoff with Democrats. The reconciliation pathway — which requires only a simple majority and bypasses the 60-vote filibuster — was supposed to be the clean solution. It has become anything but.

## Why Indian Americans should care

Immigration enforcement funding bills are easy to dismiss as someone else's problem if you hold a valid H-1B or are waiting in the EB-2 India queue. They shouldn't be.

The reconciliation package, as analyzed by the American Immigration Council, doesn't simply fund more Border Patrol agents and detention beds. It contains provisions that would impose mandatory and "cost-prohibitive" fees on a range of immigration benefit applications — the same applications that Indian families file for work permits, green card adjustments, and family sponsorship.

Because reconciliation bills bypass normal appropriations rules, these spending provisions arrive without the oversight guidelines that typically govern how agencies deploy federal dollars. There are no committee directives specifying how the money must be used. ICE and CBP would have broad discretion to allocate the funds across enforcement priorities for 51 months.

For a community where nearly every family has at least one member whose immigration status depends on timely, predictable processing by USCIS or a consulate, the prospect of a massively expanded enforcement apparatus operating alongside a chronically underfunded benefits system is not abstract. It's the gap between a green card approval and a Notice to Appear.

## The IRS problem

The irony is hard to overstate. A bill designed to fund the deportation of undocumented immigrants is being held up by a dispute over whether the government should compensate people who claim the IRS was "weaponized" against them.

The anti-weaponization fund is part of a settlement agreement between Trump and the IRS, arising from a civil lawsuit filed in January over the leak of his tax returns by an independent contractor. Senate Republicans don't object to the fund's existence — they object to the absence of guardrails. They want violent convicts excluded from compensation. The White House has so far refused.

If enough Republicans side with Democratic amendments to restrict the fund, the bill changes in ways that could provoke a presidential veto. If House Republicans reject the Senate's version, the bill goes to conference committee — adding weeks or months to a process that has already missed its deadline.

## What happens next

The Senate returns from recess in early June. The bill's supporters will attempt to pass it before the July 4 recess. But with the IRS fund dispute unresolved and Democrats preparing procedural maneuvers, the timeline is generous.

For Indian Americans tracking the legislative landscape, the takeaway is this: the bill that would most dramatically reshape immigration enforcement in a generation is not dead, but it is stuck in a way that has nothing to do with immigration policy and everything to do with internal Republican negotiations over a tax-return lawsuit settlement.

Congress is, in other words, doing exactly what Congress does — holding a consequential bill hostage to an unrelated dispute, while the people affected by both wait for someone to blink.

The June 1 deadline will pass. The question is whether the bill does too."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
