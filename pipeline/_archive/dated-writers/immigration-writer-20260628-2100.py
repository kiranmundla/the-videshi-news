#!/usr/bin/env python3
"""Immigration writer for The Videshi — 2026-06-28 21:00 PDT run."""

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


# ── ARTICLE 1 ────────────────────────────────────────────────────────────

art1_body = """A federal judge struck down the $100,000 H-1B visa fee on June 8. Three weeks later, the fee is still effectively in place — and the legal fight that will decide its fate has barely begun.

U.S. District Judge Leo Sorokin, sitting in Boston's Moakley Federal Courthouse, ruled that the fee President Trump imposed by presidential proclamation in September 2025 was an unlawful tax that Congress never authorised. The decision was unambiguous. "The substance and application of the $100,000 payment reveal that it is a tax, regardless of what the payment is called," Sorokin wrote. He cited the Supreme Court's February ruling striking down Trump's emergency tariffs, arguing the same logic applied: the executive branch cannot levy a tax without explicit congressional authority.

For the roughly 500,000 Indian-origin H-1B workers in the United States, and the thousands of companies that sponsor them, the ruling should have been a turning point. It was not.

## The Stay That Changed Everything

Within days of Sorokin's order, the Trump administration appealed to the First Circuit Court of Appeals and secured an administrative stay. The effect was immediate and clarifying: nothing changed on the ground. USCIS continues processing petitions under the existing fee structure, issuing Requests for Evidence as if the ruling never happened. Employers must still budget for the $100,000 charge on new offshore H-1B hires.

The stay creates what immigration attorneys are calling "policy limbo." Companies cannot plan around a fee that may or may not survive appeal. Hiring decisions that take months — finding candidates, filing Labour Condition Applications, preparing petitions — are being made in the dark.

"The uncertainty is almost worse than the fee itself," one immigration partner at a top-10 law firm told Reuters. Employers who paused offshore hiring after the September proclamation now face a second round of paralysis.

## Three Courts, Three Possible Answers

The legal landscape is fragmented. Sorokin's ruling in Boston contradicts an earlier federal court decision in Washington, D.C., where the U.S. Chamber of Commerce lost its challenge and the fee was upheld — at least until its scheduled expiry in September 2026. A third lawsuit, filed in San Francisco by religious groups and labour organisations, is still working through the system.

The result is that three federal appellate circuits — the First, the D.C. Circuit, and the Ninth — may reach three different conclusions about the same fee. That kind of circuit split typically ends at the Supreme Court, which could mean the $100,000 question will not be settled for a year or more.

The White House has signalled confidence. "President Trump has clear legal authority to restrict entry of any class of aliens he determines is not in America's best interests," spokeswoman Taylor Rogers said.

## What Indian Professionals Should Know

The practical implications are stark. The $100,000 fee applies only to *new* H-1B petitions for beneficiaries located abroad — workers being hired from India and brought to the United States for the first time. Change-of-status filings for workers already in the U.S. on another visa (such as F-1 students on OPT) are exempt.

This distinction has already reshaped corporate hiring strategy. Companies are leaning harder on U.S.-educated graduates over offshore recruits, not because the talent pool is better, but because the cost differential is now six figures per hire.

Indian diaspora organisations have been vocal. FIIDS, the Foundation for India and Indian Diaspora Studies, said the ruling "restores predictability and fairness to the employment-based immigration system." Indiaspora's executive director, Sanjeev Joshipura, struck a more cautious note: "One wonders if this is truly the end of the matter. The administration might still create hurdles through procedural means."

He is almost certainly right. Even if the fee is eventually struck down permanently, the nine months it has been in effect have already shifted hiring patterns that will not easily reverse. The damage, like the litigation, is ongoing.

*Sources: Reuters, SHRM, U.S. District Court for the District of Massachusetts, Travel and Tour World, Connected to India*"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "A Judge Killed the $100,000 H-1B Fee. The Government Kept Collecting It",
    "subheadline": "Three weeks after a Boston court ruled Trump's visa surcharge was an unlawful tax, a legal stay has left employers and Indian workers in limbo while three appellate circuits race toward conflicting conclusions.",
    "slug": make_slug("judge-killed-100k-h1b-fee-government-kept-collecting"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The $100K fee directly targets offshore H-1B hires — 71% of whom are Indian. Even if the courts kill it, the months of uncertainty have already pushed companies toward hiring US-based graduates over candidates from India.",
    "tags": ["h1b", "uscis", "immigration", "court-ruling", "fee-hike", "indian-diaspora"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-08/"},
        {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/news/talent-acquisition/federal-court-strikes-down-100k-h-1b-fee"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/h1b-visa-fee-court-stay-united-states/"},
        {"name": "Connected to India", "url": "https://www.connectedtoindia.com/diaspora-groups-call-h-1b-visa-fee-reversal-a-win-for-skilled-immigration-43775.html"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6077326/pexels-photo-6077326.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A gavel strikes in a courtroom, symbolising the legal battle over the H-1B fee",
    "image_attribution": "Pexels",
    "body": art1_body
}


# ── ARTICLE 2 ────────────────────────────────────────────────────────────

art2_body = """For the first time in the H-1B programme's history, being good at your job was not enough. You also had to be expensive.

USCIS has released the selection data from the FY 2027 H-1B cap season — the first to use the new wage-weighted lottery that replaced the decades-old random draw. The numbers confirm what immigration lawyers feared and what Indian IT workers felt: the system has tilted decisively against entry-level hires, and the ripple effects are remaking the entire skilled-immigration pipeline.

## The Numbers

Under the old random lottery, every registered H-1B candidate had roughly a 30 percent chance of selection, regardless of salary. The new system, finalised on December 29, 2025, and effective February 27, 2026, assigns lottery entries based on the Department of Labor's prevailing wage levels:

- **Level IV** (senior, fully competent): 4 entries — estimated 61% selection probability
- **Level III** (experienced): 3 entries — estimated 46%
- **Level II** (mid-level): 2 entries — estimated 31%
- **Level I** (entry-level): 1 entry — estimated 15%

That last figure is the one that matters most to the 143,000 Indian students currently on Optional Practical Training in the United States. Many are recent graduates in their first or second jobs, offered salaries that fall squarely at Level I or Level II. Their odds of making it through the lottery have been cut nearly in half.

Independent modelling suggests the actual Level I selection rate may be even lower — potentially 10 to 12 percent — depending on how aggressively employers adjusted their registrations upward.

## Registration Volumes Collapsed

The data also reveals a dramatic fall in overall registration volumes. Just a few years ago, the system saw a record-breaking 780,000-plus registrations, driven partly by staffing firms submitting multiple entries for the same candidate. The FY 2027 numbers show a sharp reversal.

Two factors drove the decline. First, USCIS now ties selections to a unique beneficiary's passport rather than the number of employer entries, eliminating the incentive for multiple-registration gaming. Second, the electronic registration fee jumped from $10 to $215, creating a financial threshold that forced employers to submit registrations only for candidates they were genuinely committed to hiring.

The combination produced what USCIS wanted: a smaller, higher-quality applicant pool skewed toward senior professionals.

## The $100,000 Fee Completed the Pivot

While the wage-weighted lottery changed *who* gets selected, the $100,000 supplemental fee changed *where* companies look for talent.

The fee, imposed by presidential proclamation in September 2025, applies to new H-1B petitions filed for beneficiaries located outside the United States. Change-of-status filings for workers already in the country — mainly F-1 students on OPT — are exempt.

The arithmetic is brutal. A single offshore hire now costs a six-figure investment before the employee's first day of work. For all but the largest multinationals, high-volume foreign recruitment is no longer viable. The rational move, as immigration analysts at Adams and Reese noted, is to "prioritise U.S.-educated F-1 visa-holder students on OPT and STEM OPT who are currently residing in the U.S."

That is precisely what is happening. Companies are accelerating their OPT-to-H-1B pipeline while winding down direct-from-India recruitment.

## What This Means for the Indian Diaspora

The new system creates a two-tier reality for Indian tech professionals.

**If you are already in the United States** — on OPT, in a mid-to-senior role at a company willing to pay Level III or IV wages — your odds are better than they have ever been. The lottery is no longer a coin flip; it is a wage test, and experienced Indian engineers at major tech firms clear it comfortably.

**If you are in India** hoping to come to the United States via H-1B, the door has narrowed considerably. The combination of the wage-weighted lottery, the $100,000 offshore fee, and the general tightening of the immigration system has made the traditional outsourcing-to-H-1B pathway prohibitively expensive for most employers.

Immigration attorneys are already advising Indian professionals to explore alternatives. L-1 intracompany transfer visas, O-1 extraordinary ability visas, and the Canadian and Australian skilled-worker programmes are all seeing increased interest from candidates who would previously have bet everything on the H-1B lottery.

The programme is functioning "in alignment with recent regulatory goals," USCIS says. For the hundreds of thousands of Indian workers whose plans depended on a system that treated every applicant equally, that alignment feels a lot like a door closing.

*Sources: USCIS FY 2027 H-1B Selection Data, Mondaq/Adams and Reese, Lexology/Duane Morris, Collegedunia, Reuters*"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The H-1B Lottery Is No Longer a Lottery. The First Data Shows Who Won",
    "subheadline": "USCIS released the results of its new wage-weighted H-1B selection system. Entry-level workers — disproportionately Indian — saw their odds cut nearly in half.",
    "slug": make_slug("h1b-lottery-wage-weighted-fy2027-data-entry-level-odds-halved"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians hold 71% of all H-1B approvals and 48% of OPT participants are Indian nationals. The new wage-weighted system and $100K fee together are reshaping who gets to stay in America — and who gets left behind in the queue.",
    "tags": ["h1b", "uscis", "immigration", "h1b-lottery", "wage-weighted", "indian-tech-workers"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Mondaq / Adams and Reese", "url": "https://www.mondaq.com/unitedstates/work-visas/1789182/analyzing-the-fy-2027-lottery-data-and-the-impact-of-the-100000-fee"},
        {"name": "Lexology / Duane Morris", "url": "https://www.lexology.com/library/detail.aspx?g=h1b-fy-2027-lottery-consistency"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/trumps-h-1b-visa-fee-hike-puts-focus-skilled-tech-labor-access-2025-09-22/"},
        {"name": "Collegedunia", "url": "https://collegedunia.com/usa/article/h1b-fy2027-indian-opt-students-uscis-accounts-march-31"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6804071/pexels-photo-6804071.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Software developers work together in a tech office, the kind of workplace where H-1B visa decisions shape careers",
    "image_attribution": "Pexels",
    "body": art2_body
}


# ── INSERT ────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
