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
        "headline": "The Wage Floor Just Doubled — And Indian H-1B Workers Are Standing on It",
        "subheadline": "The Department of Labor wants to nearly double the minimum salary companies must pay H-1B workers. The comment period just closed, and the Indian IT workforce is squarely in the crosshairs.",
        "slug": make_slug("dol-prevailing-wage-hike-h1b-perm-indian-workers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals account for the majority of H-1B petitions filed at Level I and Level II wages — the two tiers hit hardest by the proposed rule. IT services firms that sponsor thousands of Indian workers each year would face dramatically higher labor costs, potentially reducing sponsorship volumes and reshaping the economics of the H-1B-to-green-card pipeline for an entire generation of Indian tech professionals.",
        "tags": ["h1b", "prevailing-wage", "dol", "perm", "immigration", "indian-workers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fredrikson & Byron (ABIL Analysis)", "url": "https://www.fredlaw.com/alert-dol-releases-long-anticipated-prevailing-wage-proposed-rule"},
            {"name": "Goel & Anderson LLP", "url": "https://www.goellaw.com/dol-proposes-significant-increases-to-prevailing-wage-levels-for-h-1b-and-perm-programs/"},
            {"name": "Murthy Law Firm", "url": "https://www.murthy.com/"},
            {"name": "U.S. Department of Labor Federal Register NPRM", "url": "https://www.govinfo.gov"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/4691477/pexels-photo-4691477.jpeg",
        "body": """The Department of Labor dropped a proposed rule on March 27 that would redraw the wage map for every H-1B worker and every employer trying to sponsor one for a green card. The 60-day public comment period closed on May 26. What comes next could reshape the economics of hiring foreign talent in America — and no community has more at stake than Indians on work visas.

## The Numbers That Matter

The proposed rule takes aim at the four-tier prevailing wage system that determines the minimum salary an employer must offer when filing an H-1B petition or a PERM labor certification for a green card.

Here is what changes:

- **Level I (entry-level):** Jumps from the 17th percentile to the 34th percentile
- **Level II (qualified):** Rises from the 34th percentile to the 52nd percentile
- **Level III (experienced):** Moves from the 50th percentile to the 70th percentile
- **Level IV (fully competent):** Climbs from the 67th percentile to the 88th percentile

In practical terms, the entry-level wage floor roughly doubles. A software developer position in a mid-tier metro that currently requires a $75,000 salary under Level I might need to offer $95,000 or more under the new math. For Level II — where a large chunk of H-1B petitions land — the jump is similarly steep.

## Why Indian Workers Bear the Brunt

Indian nationals receive approximately 72% of all H-1B approvals in any given year. A disproportionate share of those petitions are filed at Level I and Level II, particularly by IT services and consulting firms that place workers across client sites nationwide.

The DOL's own rationale is straightforward: foreign workers should be paid comparably to American workers in similar roles. But critics argue the rule ignores the realities of how wage levels are assigned. A Level I designation does not necessarily mean underpayment — it often reflects entry-level experience, a rotational training role, or geographic wage variation that the OEWS data captures imperfectly.

The consulting model that Indian IT giants have built over decades — hiring workers at competitive but not top-tier wages, placing them on projects, and sponsoring green cards through PERM — would face a structural cost increase that could reduce sponsorship volumes significantly.

## The PERM Domino Effect

The wage hike does not stop at H-1B renewals. It flows directly into the PERM labor certification process, which is the first step toward an employment-based green card for most Indian workers.

PERM requires employers to prove they could not find a qualified American worker at the prevailing wage. If that wage floor rises sharply, two things happen: first, employers face higher baseline costs for every green card case they file. Second, the labor market test becomes harder to pass cleanly, because a higher advertised wage attracts more American applicants — which is precisely the DOL's intent.

For the hundreds of thousands of Indians already in the green card backlog, this creates an uncomfortable paradox. Their existing PERM certifications are grandfathered and unaffected. But anyone starting the process after the rule takes effect enters a more expensive, more scrutinized pipeline. The backlog splits into two classes: those who got in before the door narrowed, and those who didn't.

## What the Industry Is Saying

Immigration attorneys describe the rule as more moderate than the 2020 interim final rule — a Trump-era attempt to raise wages even more aggressively, which was ultimately vacated by federal courts. The current NPRM goes through standard notice-and-comment rulemaking, giving it a stronger procedural foundation. But the economic impact remains substantial.

"By eliminating the current entry-level wage classification and requiring entry-level workers to be offered wages currently at Level II in the OEWS wage system, many smaller employers and nonprofit employers could be shut out of the H-1B and PERM system," noted an analysis by Fredrikson & Byron, prepared with the Alliance of Business Immigration Lawyers.

Legal challenges are considered likely if the rule is finalized. The 2020 predecessor was struck down partly because it bypassed proper rulemaking. This version fixes that procedural gap, but the substantive arguments — that the wage levels are arbitrary, economically disruptive, and exceed DOL's statutory authority — remain available to challengers.

## The Timeline

The comment period is now closed. DOL will review submissions and could issue a final rule within several months. If finalized, it would typically take effect 30 to 60 days after publication. The rule applies prospectively — existing prevailing wage determinations, LCAs, and certified PERM cases remain untouched.

For Indian professionals currently on H-1B visas or early in their green card journey, the calculation is simple: every delay in starting a PERM case now carries a new risk — that the wage floor rises before the paperwork goes in. Those already in the pipeline have dodged this particular bullet. Those outside it may want to move faster than they planned."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Congress Built the Road. USCIS Just Declared It a Footpath.",
        "subheadline": "A new USCIS memo calls in-country green card processing an 'extraordinary' privilege. Seven decades of legislation say otherwise — and the lawsuits are already being drafted.",
        "slug": make_slug("pm-602-0199-aos-legal-challenge-indian-green-card"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals are the single largest group filing for adjustment of status through employment-based categories. If AOS is effectively curtailed, Indians face the worst outcome of any nationality: consular processing in a country where visa appointment wait times already stretch 6 to 12 months, combined with a green card backlog measured in decades. The memo threatens to turn a difficult process into a logistically impossible one.",
        "tags": ["green-card", "adjustment-of-status", "uscis", "pm-602-0199", "legal-challenge", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/"},
            {"name": "Outlook Money (India)", "url": "https://www.outlookmoney.com/"},
            {"name": "Law Offices of Michael D. Baker (PM-602-0199 Analysis)", "url": "https://mikebakerlaw.com/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/36984937/pexels-photo-36984937.jpeg",
        "body": """On May 21, U.S. Citizenship and Immigration Services released Policy Memo PM-602-0199. Buried in bureaucratic language was a radical claim: that adjusting immigration status from within the United States — the process roughly half of all green card recipients use — is not a standard procedure but an "extraordinary form of relief" granted at the agency's discretion.

The Department of Homeland Security walked the panic back within days, clarifying that no blanket policy change had occurred and that officers would continue evaluating cases individually. But immigration attorneys across the country are not reassured. The memo's language, they argue, is not a clarification of existing law. It is a rewriting of it. And the legal challenges are coming.

## What the Memo Actually Says

PM-602-0199 instructs USCIS officers to treat adjustment of status — the process by which someone already in the U.S. on a temporary visa applies for a green card without leaving the country — as a discretionary benefit reserved for exceptional cases. The default pathway, under the memo's framework, is consular processing: applicants leave the United States, apply through a U.S. embassy or consulate in their home country, and wait abroad for approval.

The practical effect, if applied broadly, would be seismic. Approximately 1.4 million people obtained lawful permanent residence in fiscal year 2024. Former USCIS official Doug Rand estimates that roughly half of those applications were submitted from within the United States. Sending those applicants abroad would overwhelm a consular system already struggling with backlogs.

## Seven Decades of Congress Saying the Opposite

Here is where the legal argument gets sharp. Adjustment of status was not invented by agency policy. Congress authorized it in 1952 as part of the Immigration and Nationality Act. Lawmakers have amended and expanded the provision repeatedly in the decades since.

In 1990, Congress reauthorized the INA and explicitly allowed H-1B and L-1 visa holders to pursue permanent residency without affecting their temporary status — the concept known as dual intent. A later update let H-1B workers switch employers while their green card cases were pending, on the assumption they would remain in the country throughout the process. Another provision granted the possibility of adjustment of status even for applicants with up to 180 days of status violations, specifically for employment-based cases.

"You don't create a roadway, and expand it and expand it, and then suddenly turn it into a one-lane highway with an off-ramp to nowhere," Angelo Paparelli, a partner at Vialto Law, told Bloomberg Law.

The core legal argument writes itself: Congress did not build a 70-year framework around in-country processing only for an agency memo to declare it extraordinary.

## The Consular Non-Reviewability Problem

Beyond the constitutional questions, the memo creates a procedural trap that immigration lawyers find particularly troubling.

When a green card application is denied through adjustment of status inside the United States, the applicant has options: motions to reopen, requests for reconsideration, and in some cases, limited judicial review. These are not formalities — they are the mechanisms that catch errors, correct misunderstandings, and provide due process.

Consular processing offers no comparable safeguards. Under the longstanding doctrine of consular non-reviewability, decisions made by consular officers abroad are essentially immune from judicial scrutiny. An applicant denied a green card at a U.S. consulate in Mumbai or Chennai has almost no avenue for appeal.

For Indian applicants, this asymmetry is not abstract. India-based consulates already face some of the longest visa appointment wait times in the world — six to twelve months in many categories. Forcing employment-based applicants into that queue, while stripping them of the procedural protections available inside the U.S., amounts to a double penalty.

## How Broadly Will Officers Apply It?

The honest answer is that nobody knows yet. Several prominent immigration attorneys have told clients that for standard employment-based categories — H-1B holders with clean records, consistent employment, and properly maintained status — the memo is unlikely to change outcomes immediately.

"It's business as usual for major common employment-based categories like H-1B holders," said Caroline Tang, a shareholder at Ogletree Deakins, in an interview with Bloomberg Law. But she and others expect increased scrutiny of whether applicants have maintained the terms of their temporary status when they file.

The categories most at risk are applicants who have overstayed their visas, those who changed status while adjustment cases were pending, and applicants from countries the administration has flagged for higher usage of public assistance programs. DHS officials have said as much in background statements.

## The Lawsuits Are Forming

Bloomberg Law's analysis is direct: the memo "shuns decades of legal immigration norms" and is "a likely target of legal challenges." The administration is already defending related cases in multiple courts — the $100,000 H-1B fee, the Gold Card program, mandatory detention policies. Adding a challenge to PM-602-0199 to that docket is a matter of when, not whether.

The strongest line of attack will likely be that the memo contradicts the plain text and legislative history of Section 245 of the INA, which authorizes adjustment of status. The 2020 precedent matters here: when the Trump administration attempted to radically alter prevailing wage rules without proper rulemaking, courts struck it down. A policy memo carries even less legal weight than a rule.

For the roughly 400,000 Indian nationals with approved I-140 petitions waiting in the employment-based green card backlog, the stakes are existential. Most are inside the United States, working, paying taxes, raising families. The adjustment of status pathway is not a shortcut for them — it is the only mechanism that makes a multi-decade wait survivable. Take it away, and you are asking people to leave the country they have called home for years, sit in a consular queue for months, and complete the process from 8,000 miles away with fewer legal protections.

The memo says that is an extraordinary request. Congress — repeatedly, over 70 years — has said it is the ordinary one."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
