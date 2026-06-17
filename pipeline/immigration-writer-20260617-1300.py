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

article1_body = """The Trump administration has spent the better part of a year making the H-1B visa more expensive to use. A $100,000 fee, a wage-weighted lottery, sharper scrutiny at the consulate. Now comes the quietest and possibly most consequential lever of all: the wage itself.

A proposed Department of Labor rule, working its way through the federal review process, would rewrite how the government calculates the "prevailing wage" — the salary floor an employer must promise before it can sponsor a foreign worker on an H-1B, H-1B1 or E-3 visa, or pursue a green card through the PERM labor-certification process. The change sounds technical. Its effects are not.

## The math, briefly

Under the current system, in place since 2005, the Labor Department pegs its four wage levels to roughly the 17th, 34th, 50th and 67th percentiles of local pay for a given occupation. The proposed rule lifts those anchors to the 34th, 52nd, 70th and 88th percentiles. In plain terms: every rung of the ladder moves up, and the top rung moves up the most.

The agency's own estimate is that the average certified wage would climb by about $14,000 a year per worker. Immigration lawyers who have run the numbers for specific roles arrive at sharper figures. Bloomberg Law reported that an entry-level automotive engineer in Detroit would see the required wage rise by roughly $16,000; a software engineer in Silicon Valley sponsored through the program by about $40,000.

For a worker, a higher mandated salary sounds like a gift. The catch is what it does to the employer's willingness to sponsor at all.

## Why Indians should read past the headline

Indians collect more than 70% of approved H-1B petitions in a typical year, and they dominate the EB-2 and EB-3 green-card queues that run through PERM. That makes this rule a tax on the exact population The Videshi's readers belong to — but an oddly shaped one.

The wage rule interacts with the new wage-weighted lottery that debuted in the FY 2027 cycle, where higher offered wages buy more lottery entries. A higher Level I floor could, in theory, nudge more registrations into higher-paid brackets and improve the odds for the workers who clear them. The Penn Wharton Budget Model projected the weighted lottery would lift average selected compensation by around 10% with minimal effect on US-born wages.

But the same arithmetic squeezes from the other side. Entry-level roles — the rung most new Indian graduates and recent STEM OPT workers occupy — become the most expensive relative to their old cost. Attorneys quoted in the Bloomberg coverage were blunt: companies that already pay well will still feel "wage inflation that hasn't been planned for," and many will simply look elsewhere. "Everything we see coming out of this administration is to curb foreign workers in the US," said one immigration partner.

"Elsewhere" is the operative word. Multinationals can expand a Bengaluru or Hyderabad global capability center instead of fighting the US wage math — a shift already visible in the offshoring data, and one that relocates the job, not the worker.

## The timing reprieve

There is a narrow piece of good news for anyone in this year's cycle. The rule is not retroactive. It would apply only to prevailing-wage determinations and Labor Condition Applications filed on or after its effective date. FY 2027 cap petitions, whose LCAs were filed before the June 30, 2026 deadline, are expected to be unaffected. Approved PERM determinations and existing LCAs stay as they are.

For Indian professionals weighing a green-card downgrade strategy or a fresh PERM filing, that timing matters: a determination locked in before the rule bites is grandfathered at today's lower floor.

## What's next

The comment window has closed, and the rule now sits in the queue for finalization. The Labor Department tried a near-identical increase in January 2021; a federal court vacated it before it took effect. Litigation is a near-certainty this time too, which means the effective date — and therefore the grandfathering cutoff — remains a moving target.

For now, the advice from the immigration bar is the same advice it has been giving all year: file early, lock in determinations while you can, and assume the cost of being an Indian professional in America is going up faster than your salary.

Sources: Bloomberg Law; US Department of Labor; Penn Wharton Budget Model; Lexology."""

article2_body = """For years, the hardest part of bringing your parents to America for a wedding, a birth, or a winter visit was the wait — the months-long queue for a B-1/B-2 visitor visa appointment at a US consulate in India. A revived federal pilot adds a second hurdle that hits where it hurts: the wallet.

The State Department's visa bond pilot program empowers consular officers to demand refundable bonds of up to $15,000 from certain applicants for B-1 (business) and B-2 (tourist) visas. The typical figure is $10,000, but officers may set it at $5,000 or $15,000. The money comes back only if the visitor complies fully with their visa terms and leaves the United States on time.

## How it works

The bond is not universal. It targets applicants from countries flagged for high overstay rates, weak vetting systems, or citizenship-by-investment schemes that let people buy a passport. An officer who decides a particular applicant is a flight risk can condition the visa on posting the bond before travel.

For a family, the arithmetic compounds quickly. Two parents at $10,000 to $15,000 each, plus $5,000 for a dependent child, can mean $25,000 or more locked up with the US government for the duration of a visit. That is capital most middle-class Indian families would rather not freeze, even temporarily — and even though, on paper, it is fully refundable.

The pilot revives a policy first floated in late 2020 that never took hold, sidelined by the collapse in travel during the pandemic. Its return fits the administration's broader posture: tighter interviews worldwide, expanded travel bans, and a general presumption of skepticism toward temporary visitors.

## Why this lands on the diaspora

India is not currently among the highest-overstay-rate countries that bond programs have historically targeted, and the official list of affected nationalities will determine who actually pays. But Indian families are uniquely exposed to anything that raises the cost or friction of the B-2 visa, because the visitor visa is the backbone of diaspora family life.

It is how grandparents meet grandchildren. It is how a mother comes for a daughter's delivery, how a father attends a son's graduation, how relatives fill the seats at a Bay Area or New Jersey wedding. The H-1B worker building a life in America depends on the B-2 to keep that life connected to home. A $15,000 conditional bond turns a routine family visit into a financial decision.

There is also a knock-on effect at the consulate. Bond determinations are discretionary and case-by-case, which means more officer time per applicant — and officer time is precisely the bottleneck that has kept Indian visitor-visa wait times stubbornly long. A program that adds a layer of judgment to each B-2 interview risks lengthening the very queues that already frustrate Indian travelers.

## The refundable-bond fine print

"Refundable" is carrying a lot of weight in the official description. The bond returns only on demonstrated compliance — timely departure, no unauthorized work, no status violations. Recovering it requires the visitor to have done everything correctly and, presumably, to navigate a reclamation process after leaving the country. For families unfamiliar with the mechanics, the risk of forfeiting money through a paperwork slip is real, even when the underlying visit was entirely legitimate.

Immigration advocates have warned that bonds of this size function less as a compliance tool than as a wealth filter, effectively pricing lower-income applicants out of family travel while wealthier ones absorb the cost. For the Indian diaspora, where extended-family obligations cross oceans constantly, that filter cuts close.

## What to watch

The decisive document is the list of countries whose nationals are subject to the bond, along with the consular guidance on when officers should impose it. Families planning to bring relatives over should track whether India appears on any affected-nationality list, build the possibility of a bond into their timeline and budget, and keep meticulous records of every visit's entry and exit.

The visa interview was already the anxious part. Now the approval can come with an invoice attached.

Sources: The Indian EYE; US Department of State."""

article3_body = """The case landed quietly on June 15. A 54-year-old man from India, living in Oregon, named in a civil complaint by the US Attorney's office, accused of using a second identity decades ago to win the permanent residency and then the citizenship that a judge had once denied him. It was, court records note, the first denaturalization case filed in Oregon during President Trump's second term.

It will not be the last. And for naturalized Indian Americans, the trend behind that single filing is worth understanding clearly, without panic and without denial.

## A campaign, not a one-off

A week earlier, on June 8, the Department of Justice announced it had filed denaturalization actions against 17 people across multiple federal districts. Among them was Neeraj Sharma, an India-born staffing-company executive in New Jersey accused of filing eleven fraudulent H-1B petitions — complete with forged signatures of corporate executives — and then lying on his own naturalization application in 2017.

Denaturalization is not new. The law has always allowed the government to revoke citizenship that was "illegally procured" or obtained through "concealment of a material fact or willful misrepresentation." What is new is the volume and the visibility. The administration has signaled that stripping citizenship is a priority enforcement tool, and the cases are being announced in batches rather than handled as rare, individual anomalies.

## What it actually targets — and what it doesn't

It is important to be precise, because fear travels faster than fact in immigrant communities. The cases made public so far share a common spine: alleged fraud, concealment, or material lies in the original immigration or naturalization process. Sharma is accused of visa fraud and perjury. The Oregon defendant is accused of using a fabricated identity after a deportation order. These are not citizens being punished for ordinary conduct after naturalizing.

For the overwhelming majority of naturalized Indian Americans — who filed honestly, disclosed what they were asked to disclose, and earned their citizenship through years of lawful status — the legal exposure from this campaign is, on the available evidence, minimal.

But the chilling effect is broader than the legal one. When citizenship is publicly reframed as conditional and revocable, every naturalized American is invited to wonder about the durability of their own status. That anxiety is already measurable: recent polling found that roughly half of South Asian adults now know someone carrying their immigration documents everywhere they go. A denaturalization campaign, however narrowly targeted in practice, feeds directly into that unease.

## The civil-versus-criminal distinction matters

Most of these recent actions are civil, not criminal. That is not a comfort — it is a warning. Criminal denaturalization carries a high burden of proof and the right to appointed counsel. Civil denaturalization carries a lower evidentiary bar, no guaranteed lawyer, and no statute of limitations. The government can reach back decades, as the Oregon case reaching to a 1990s application demonstrates.

For the diaspora, the practical takeaways are unglamorous but real. Keep copies of your original immigration filings — the I-485, the naturalization application, the supporting evidence. Understand what you attested to. If there were errors or omissions in a long-ago application, consult an immigration attorney about your exposure before, not after, a problem surfaces.

## The larger frame

This campaign does not exist in isolation. It runs alongside a rewritten adjustment-of-status memo that treats green cards as "extraordinary" relief, a wave of H-1B cost increases, and a general tightening across the legal-immigration system. The throughline is a posture that treats every immigration benefit — including the one supposedly most permanent — as provisional and reviewable.

For Indians who built American lives on the premise that citizenship was the finish line, the message is sobering: the paperwork that got you here is worth keeping, and worth being able to defend. Not because most people are at risk, but because the system has stopped treating the finish line as final.

Sources: Statesman Journal; The Indian EYE; US Department of Justice."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The H-1B's Next Squeeze Isn't a Fee — It's a Rewrite of the Word 'Prevailing'",
        "subheadline": "A Labor Department rule would raise mandated wages by up to $40,000 a year for some H-1B roles. For Indian professionals, it is help and headwind in the same stroke.",
        "slug": make_slug("dol-prevailing-wage-overhaul-h1b-perm-india-software-engineers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians take 70%+ of H-1B petitions and dominate the EB-2/EB-3 PERM queues, so a wage-floor rewrite raises both their salaries and the odds employers stop sponsoring entry-level desi talent.",
        "tags": ["h1b", "prevailing-wage", "dol", "perm", "green-card", "uscis"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law — H-1B Wage Overhaul Proposal Adds to Sticker Shock", "url": "https://news.bloomberglaw.com/daily-labor-report/h-1b-wage-overhaul-proposal-adds-to-sticker-shock-for-employers"},
            {"name": "US Department of Labor — Proposed Prevailing Wage Rule", "url": "https://www.dol.gov/newsroom/releases"},
            {"name": "Penn Wharton Budget Model — Higher Prevailing Wages and the H-1B Lottery", "url": "https://budgetmodel.wharton.upenn.edu/issues/2026/4/9/higher-prevailing-wages-h1b-visa-lottery"},
            {"name": "Lexology — DOL Proposes Significant Increases to Prevailing Wage Levels", "url": "https://www.lexology.com/"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6590651/pexels-photo-6590651.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "US dollar bills in close-up, illustrating the wage floors at the center of the proposed H-1B prevailing-wage rule",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A $15,000 Price Tag Just Got Attached to Your Parents' Visit",
        "subheadline": "A revived State Department pilot lets consular officers demand refundable bonds of up to $15,000 on B-1/B-2 visas — turning a routine family trip into a financial decision.",
        "slug": make_slug("visa-bond-pilot-15000-b2-visitor-visa-india-family-visits"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The B-2 visitor visa is the backbone of diaspora family life — how grandparents meet grandchildren and relatives attend weddings — so a five-figure conditional bond strikes at the heart of how NRIs stay connected to home.",
        "tags": ["b2-visa", "visa-bond", "state-department", "visitor-visa", "consulate"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE — US Pilot Program Mandates Bonds of up to $15,000 for Visitor Visas", "url": "https://theindianeye.net/"},
            {"name": "US Department of State — Visa Bond Pilot Program", "url": "https://travel.state.gov/content/travel/en/News/visas-news.html"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6354991/pexels-photo-6354991.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Travelers walking through an airport terminal with luggage, evoking the family visits affected by the new visa bond pilot",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Citizenship Was Supposed to Be the Finish Line. A Wave of Denaturalization Cases Says Otherwise",
        "subheadline": "An Oregon filing on June 15 and a 17-person DOJ sweep signal a campaign to revoke naturalized citizenship. Here is what it actually targets — and what it doesn't.",
        "slug": make_slug("denaturalization-campaign-widening-naturalized-indian-americans-doj"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Naturalized Indian Americans built lives on the premise that citizenship was permanent; a visible denaturalization campaign — even one narrowly targeting fraud — reframes that status as reviewable and feeds measurable anxiety across the community.",
        "tags": ["denaturalization", "citizenship", "doj", "uscis", "naturalization", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Statesman Journal — Federal government seeks to strip citizenship from Oregon immigrant", "url": "https://www.statesmanjournal.com/"},
            {"name": "The Indian EYE — H-1B visa fraud by Indian leads to revocation of US citizenship", "url": "https://theindianeye.net/"},
            {"name": "US Department of Justice — Denaturalization Actions", "url": "https://www.justice.gov/opa/pr"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36595112/pexels-photo-36595112.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The facade of a historic American courthouse, where civil denaturalization cases are now being filed in growing numbers",
        "image_attribution": "Pexels",
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   [{art['slug']}] words={wc}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
