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

article1_body = """A federal judge struck down Donald Trump's $100,000 H-1B fee three weeks ago. Someone forgot to tell the adjudicators.

In offices from Vermont to California, US Citizenship and Immigration Services is still firing off Requests for Evidence that demand the six-figure payment — including, immigration lawyers say, from workers who are plainly exempt from it. The fee may be legally dead. On the ground, it is undead.

## What the court actually did

In September, Presidential Proclamation 10973 slapped a $100,000 charge on new H-1B petitions that require consular processing abroad. On June 8, US District Judge Leo Sorokin in Massachusetts vacated it, calling it an unauthorized tax dressed up as a regulatory fee. The government promptly appealed and asked the First Circuit to keep the fee alive while it litigates — which means that whether employers must pay could flip more than once before any of this is settled.

That legal whiplash is the backdrop. The day-to-day reality is messier.

## The RFE machine keeps running

The Murthy Law Firm, one of the larger India-focused immigration practices in the country, reports seeing RFEs demanding the $100,000 fee in nearly every petition that involves consular processing — regardless of whether the worker falls squarely inside the exemptions USCIS itself published. Lawyers describe demands landing even where:

- the worker already holds a valid, previously issued H-1B visa stamp; or
- the petition is not new at all, but an extension, amendment, or change involving an existing H-1B employee.

None of those should trigger the charge under the agency's own guidance. Yet the demands arrive anyway, and when attorneys respond explaining why the fee does not apply, the files frequently go silent. Some sit for months. In a few cases, lawyers say, adjudication simply stalls until the worker's existing visa stamp expires — at which point a denial issues, the petition having quietly run out the clock.

Premium processing, the paid service that is supposed to guarantee a 15-day answer, has not reliably broken the logjam.

## Why this lands hardest on Indians

Roughly seven in ten H-1B visas go to Indian nationals. That single statistic is why a procedural snarl in Camp Springs becomes a household anxiety in Hyderabad and Hillsboro. The workers most exposed here are not the headline cases of brand-new hires being flown in from abroad. They are the people already inside the system — the engineer in San Jose filing a routine three-year extension, the analyst switching employers, the family that planned a trip home to India and now wonders whether stepping out for visa stamping means stepping into a $100,000 demand or an indefinite hold.

For an Indian professional, the calculus has shifted from "is my petition strong?" to "can I afford to leave the country at all?" An RFE that should never have issued still has to be answered, lawyered, and waited out. Each one is billable hours, sleepless nights, and a calendar held hostage to a visa stamp's expiry date.

## What employers are doing

Companies are not waiting for the courts to find their footing. Immigration counsel report a quiet pivot toward alternatives that sidestep the fee fight entirely: cap-exempt H-1B sponsorship through universities and nonprofits, L-1 intracompany transfers for staff who can be routed through an overseas office first, and O-1 visas for workers who can credibly claim extraordinary ability. Remote-work arrangements that keep an employee outside the consular-processing trap are also back on the table.

For Indian workers, that menu is double-edged. The L-1 and O-1 routes are narrower and harder to qualify for, and a shift toward cap-exempt employers can mean trading a Big Tech salary for a university paycheck. The alternatives exist; they are not equivalents.

## What to watch

The First Circuit's decision on the government's stay request is the next domino. If it lets the fee stand during appeal, the RFEs gain retroactive cover. If it does not, USCIS will be issuing demands for a fee no court currently authorizes — and applicants will have a stronger hand in refusing them.

Either way, the lesson of the past month is that for H-1B holders, a courtroom win is not the same as relief. The proclamation can be struck down in Boston and still be alive in your inbox. Until the agency's adjudication guidance catches up with the law, the safest assumption for an Indian H-1B worker weighing a trip abroad is the cynical one: the fee is gone on paper, and very much present in practice.

**Sources:** Bloomberg Law, Murthy Law Firm, WR Immigration (Wolfsdorf), aviationa2z."""

article2_body = """For years, the fight over the H-1B visa played out in Washington — in lottery rules, wage tiers, and a $100,000 fee now stuck in the courts. Texas just opened a second front, and it is using a tool nobody expected: state consumer-protection law.

The state cannot run the H-1B program. Immigration is a federal monopoly, and no governor or attorney general can grant, deny, or revoke a visa. But Texas has discovered that it does not need to touch the visa to make life difficult for the companies that use it. All it needs is a theory about business fraud — and "ghost offices" gave it one.

## The ghost-office trigger

In January, reports surfaced of shell businesses sponsoring unusually large numbers of H-1B workers while showing little or no real commercial activity — addresses with no operations, payrolls with no projects, companies that existed mainly on petitions. The response from Austin was swift and three-pronged.

Governor Greg Abbott ordered every state agency to stop filing H-1B applications for state employees through May 2027. Attorney General Ken Paxton issued civil investigative demands to employers suspected of misrepresenting their operations, compelling them to hand over employee rosters, financial records, and descriptions of the services they actually provide. And House Speaker Dustin Burrows directed a legislative committee to examine whether the state has enough visibility into how employers use the program.

Crucially, none of this requires proving an immigration violation. Paxton's theory rests on deceptive-trade-practice law — did the company misrepresent itself? — which is why it can proceed without a single federal hook.

## Why the model travels

That is exactly what should worry the diaspora. The consumer-protection statutes Paxton is leaning on are not unique to Texas; nearly every state has a close cousin. An attorney general in any state with a heavy concentration of H-1B employers could copy the playbook tomorrow, no new legislation required. Texas may be first, but the architecture is portable.

And it dovetails neatly with where the federal government is already heading. USCIS uses data-driven targeting to flag suspicious petitions — odd worksite arrangements, inconsistent business records — and conducts site visits where officers interview staff and demand documents. The Department of Labor's "Project Firewall," launched in September, ramped up scrutiny of wage violations. State pressure does not create new federal power so much as give cover for the aggressive use of powers that already exist.

## The Indian exposure

Here is the uncomfortable part for the diaspora. The "ghost office" framing maps almost exactly onto the Indian-American IT-services ecosystem — the staffing firms and subcontractors that place engineers at client sites, the third-party-placement model, the smaller consultancies that scaled fast. These are disproportionately Indian-owned and Indian-staffed, and they are precisely the structures that "remote workforces, third-party worksites, and fast-scaling operations" describe.

Most of these firms are entirely legitimate. That is the problem with a fraud dragnet: it is built to catch the bad actors, but it sweeps up the compliant ones in audits, subpoenas, and site visits all the same. An Indian engineer placed by a consultancy at a Fortune 500 client may have done nothing wrong and still find their employer under a civil investigative demand, their petition under a microscope, their extension delayed while the company proves it is real.

For workers, the practical advice is unglamorous but vital: the facts in your petition need to match your daily reality. Job duties, work location, supervision, and salary should line up with what was filed. When an officer shows up unannounced — and increasingly they do — the gap between the paperwork and the desk you actually sit at is what gets a petition revoked.

## The bigger drift

Step back and a pattern emerges. The H-1B debate has shifted from "how many visas?" to "fraud and abuse," and that reframing is doing real work. Congress is weighing the bipartisan H-1B and L-1 Visa Reform Act, with stricter wage floors and expanded compliance tools. Texas lawmakers have asked DHS, the State Department, and Labor to coordinate investigations. Each move treats sham worksites and displacement not as isolated misconduct but as systemic rot to be excised.

For the Indian diaspora — the program's single largest constituency, and the backbone of the IT-services model now in the crosshairs — that drift is the story beneath the story. The lottery and the fee grab headlines. But the quieter shift, toward treating the whole program as a fraud problem to be policed by anyone with a consumer-protection statute, may reshape who can sponsor an Indian worker, and on what terms, for years.

**Sources:** Bloomberg Law (K&L Gates analysis), Texas Office of the Attorney General, US Department of Labor."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The $100K H-1B Fee Is Dead in Court. USCIS Keeps Demanding It Anyway",
        "subheadline": "A judge struck down Trump's six-figure charge in June. Lawyers say the agency is still issuing Requests for Evidence demanding it — even from workers who are exempt.",
        "slug": make_slug("h1b-100k-fee-rfe-limbo-uscis-demands-exempt-workers-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Roughly 70% of H-1B visas go to Indians, so an RFE storm demanding a fee no court currently authorizes lands hardest on Indian professionals weighing extensions, employer changes, and trips home for visa stamping.",
        "tags": ["h1b", "uscis", "rfe", "100000-fee", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/legal-exchange-insights-and-commentary/texas-pushes-h-1b-enforcement-beyond-the-federal-status-quo"},
            {"name": "Murthy Law Firm", "url": "https://www.murthy.com/"},
            {"name": "WR Immigration (Wolfsdorf)", "url": "https://wolfsdorf.com/"},
            {"name": "aviationa2z", "url": "https://www.aviationa2z.com/index.php/2026/06/25/h-1b-visa-fee-uncertainty-continues-after-court-stay-on-trumps-100k-rule/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/United_States_Passport_Visa_Pages.jpg/1280px-United_States_Passport_Visa_Pages.jpg",
        "image_caption": "The visa pages of a United States passport, where H-1B stamping decisions are recorded.",
        "image_attribution": "Wikimedia Commons",
        "body": article1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Texas Found a Way to Police H-1B Visas Without Touching the Program",
        "subheadline": "Using consumer-protection law and 'ghost office' investigations, the state has opened a second front on the visa — and the playbook copies easily to other states.",
        "slug": make_slug("texas-h1b-ghost-office-enforcement-consumer-protection-indian-it"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The 'ghost office' fraud framing maps onto the Indian-owned IT-staffing and subcontractor model, meaning compliant Indian-run firms and the engineers they place risk getting swept into audits, subpoenas, and site visits.",
        "tags": ["h1b", "texas", "fraud", "enforcement", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Bloomberg Law (K&L Gates analysis)", "url": "https://news.bloomberglaw.com/legal-exchange-insights-and-commentary/texas-pushes-h-1b-enforcement-beyond-the-federal-status-quo"},
            {"name": "Texas Office of the Attorney General", "url": "https://www.texasattorneygeneral.gov/"},
            {"name": "US Department of Labor (Project Firewall)", "url": "https://www.dol.gov/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5483059/pexels-photo-5483059.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "An empty open-plan office floor with vacant cubicles, the kind of 'ghost office' setup investigators say can mask H-1B sponsorship fraud.",
        "image_attribution": "Pexels",
        "body": article2_body,
    },
]

for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']} ({wc} words)")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
