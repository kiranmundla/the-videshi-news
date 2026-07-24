#!/usr/bin/env python3
"""Immigration writer — 2026-06-29 05:00 PDT run."""

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


# ─── Article 1: Denaturalization + H-1B Fraud ───────────────────────────────

article1_body = """The Department of Justice wants Neeraj Sharma's American passport back.

Sharma, an India-born businessman who ran Magnavision LLC out of Piscataway, New Jersey, is one of 17 people targeted in the government's latest wave of denaturalization filings. His alleged crime is familiar to anyone who has watched the H-1B staffing industry closely: he filed eleven petitions with USCIS claiming that foreign workers would be employed at a major global financial institution, complete with letters on the bank's official letterhead bearing forged executive signatures.

None of the positions existed. None of the workers were placed there. The whole thing was fabricated to secure H-1B visas.

In December 2017, Sharma applied for U.S. citizenship. On the Form N-400 — under penalty of perjury — he stated that he had never committed a crime for which he was not arrested, never given false information to a government official, and never lied to secure immigration benefits. USCIS approved the application. He was convicted of visa fraud in 2021. Now the government wants to undo the naturalization entirely.

## The Broader Campaign

Sharma is not an isolated case. The Justice Department has filed 29 civil denaturalization cases in May and June 2026 combined, a pace that dwarfs both the 25-case annual average during Trump's first term and the 11-case average that prevailed from 1990 to 2017, according to the Migration Policy Institute. The administration's stated goal is 1,600 referrals — a number that suggests this machinery is still warming up.

The targets so far have included individuals accused of sexual abuse, healthcare fraud, drug trafficking, and identity fraud. But the expansion into H-1B-related fraud marks a turn that should register with the Indian diaspora specifically, given that Indians are far and away the largest nationality in the H-1B program.

In a separate case in Sacramento, two men — Sridhara Babu Rajidi and Murali Krishna Mada — pleaded guilty to conspiring to file fraudulent H-1B petitions through the University of California, claiming that beneficiaries would work on UC projects that never existed. Their sentencing is scheduled for July 30, 2026. Both face up to five years in prison and $250,000 fines.

"American citizenship is a privilege, and it must be earned honestly," said DHS Secretary Markwayne Mullin. "We will continue to use every lawful avenue to denaturalize and remove aliens."

## What This Means for Indian Americans

The legal mechanism is blunt: under the Immigration and Nationality Act, naturalized citizenship can be revoked if it was obtained through concealment of a material fact or willful misrepresentation. The government does not need a criminal conviction to pursue denaturalization — it is a civil proceeding, with a lower evidentiary standard.

For the roughly 700,000 Indians who have naturalized in the past decade, many through the H-1B to green card to citizenship pipeline, the implication is clear. Anything false or misleading in your original H-1B petition, your green card application, or your N-400 answers can resurface years — even decades — later.

This is particularly pointed for those who passed through IT staffing firms, where the line between legitimate placement and speculative filing has historically been thin. Client letters describing projects that were aspirational rather than confirmed, or work locations that shifted after filing, are the kind of details that the Fraud Detection and National Security Directorate at USCIS is now trained to flag.

On June 26, Democracy Forward Foundation filed a federal lawsuit against USCIS challenging the expanded denaturalization program, arguing that the administration is stretching far beyond the traditional focus on violent crime and national security threats. The case — *Democracy Forward Foundation v. USCIS*, No. 1:26-cv-02263 — will test whether the courts see this expansion as lawful enforcement or overreach.

## The Uncomfortable Arithmetic

The administration's June 2025 denaturalization memo explicitly broadened priorities to include individuals who "engaged in fraud against private individuals, funds, or corporations" — language capacious enough to cover a wide range of white-collar immigration offenses.

For naturalized Indian Americans who filed everything cleanly, none of this is an immediate threat. But the expansion has shifted the underlying assumption. Citizenship was once treated as the final chapter — the point at which you stopped worrying about your immigration file. The Sharma case makes clear that it is not. The N-400 is not a formality. It is a sworn declaration that can be litigated for the rest of your life.

Immigration attorneys are advising naturalized clients with any irregularities in their filing history to conduct a thorough review of their records now, before the government does it for them. In the current climate, the cost of a preemptive audit is a fraction of the cost of defending a denaturalization action."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "He Filed 11 Fake H-1B Petitions. Now the Government Wants His Citizenship Back",
    "subheadline": "The DOJ's expanding denaturalization campaign has reached the heart of the Indian staffing industry. Naturalized citizens who came through the H-1B pipeline should pay attention.",
    "slug": make_slug("doj-denaturalization-h1b-fraud-magnavision-sharma-indian"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian Americans who naturalized through the H-1B-to-green-card-to-citizenship pipeline face a newly aggressive DOJ willing to revoke citizenship over prior visa fraud, making this a direct concern for the Indian IT staffing community.",
    "tags": ["h1b", "denaturalization", "uscis", "doj", "fraud", "citizenship", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "U.S. Department of Justice", "url": "https://www.justice.gov/opa/pr/justice-department-moves-strip-us-citizenship-17-naturalized-sex-offenders-fraudsters-drug"},
        {"name": "USCIS", "url": "https://www.uscis.gov/newsroom/news-releases/justice-department-moves-to-strip-us-citizenship-from-17-naturalized-sex-offenders-fraudsters-drug"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/"},
        {"name": "VisaVerge", "url": "https://www.visaverge.com/news/doj-moves-to-denaturalize-business-owner-alleges-h-1b-fraud-in-us-citizenship/"},
        {"name": "The Indian EYE", "url": "https://theindianeye.com/"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/2014-04-04-Robert-F-Kennedy-Department-of-Justice-Building-Washington-DC.jpg/1280px-2014-04-04-Robert-F-Kennedy-Department-of-Justice-Building-Washington-DC.jpg",
    "image_caption": "The Robert F. Kennedy Department of Justice Building in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ─── Article 2: American White-Collar Worker Jobs Act ────────────────────────

article2_body = """Chip Roy has a two-year plan for the H-1B visa. Literally.

The Texas Republican introduced the American White-Collar Worker Jobs Act on June 4, a bill that would gut the most valuable features of the H-1B program as Indian tech workers know it. Dual intent — the legal doctrine that allows you to work on a temporary visa while simultaneously pursuing a green card — would be eliminated. STEM OPT, the post-graduation work authorization that keeps hundreds of thousands of Indian students in the U.S. labor market, would be scrapped entirely. And the maximum duration of H-1B status would be slashed from six years to two.

If passed, it would transform the H-1B from a career-building pathway into something closer to a short-term work permit with an expiration date and no forwarding address.

## The Fine Print

The bill retains the annual cap of 65,000 H-1B visas but replaces the lottery system with a wage-based selection, prioritizing petitions linked to higher salaries. Employers hiring H-1B workers would need to pay above the 75th percentile of wages in the local area — a threshold designed to make the visa economically unviable for entry-level and mid-level positions, precisely the roles that Indian IT services firms fill most frequently.

There is also a per-company cap: no employer may have more than 5% of its U.S. workforce on nonimmigrant visas. For large IT outsourcers like TCS, Infosys, and Wipro — whose onshore teams have historically relied heavily on H-1B workers — this provision alone could require a radical restructuring of their American operations.

The bill would impose a 7% per-country cap on annual H-1B allocations, mirroring the existing green card per-country limit that has already created a multi-decade backlog for Indian nationals. Applied to H-1B visas, it would dramatically reduce Indian representation in the program, given that Indians currently account for roughly 72% of all H-1B approvals.

And companies would be required to advertise positions domestically and offer them to equally or better qualified American workers before filing an H-1B petition — a "recruit Americans first" mandate that echoes labor condition application requirements but with sharper teeth.

## The Dual Intent Death Sentence

For Indian workers, the elimination of dual intent is the provision with the most devastating downstream consequences. Under current law, an H-1B holder can simultaneously pursue permanent residency — a feature that has allowed hundreds of thousands of Indians to remain employed, raise families, buy homes, and build lives in America while waiting through the EB-2/EB-3 backlog that stretches past the year 2060 for Indian-born applicants.

Without dual intent, an H-1B holder would need to maintain a residence abroad and demonstrate no intent to abandon it. The bill explicitly states that "the alien has a residence in a foreign country which the alien has no intention of abandoning." That language turns every green card filing into a potential visa violation — and every American mortgage, school enrollment, and 401(k) contribution into evidence of immigrant intent.

The practical effect: Indian workers would need to choose between building a career in America and building a life there.

## The OPT Problem

The elimination of STEM OPT would be equally consequential. The program currently allows international students in STEM fields to work in the U.S. for up to three years after graduation — a period that often bridges the gap between completing a degree and securing H-1B sponsorship. Indian students are the largest national group in STEM OPT, and for many, it is the only legal pathway from an American classroom to an American paycheck.

Without it, the pipeline that feeds Indian talent into Silicon Valley, Wall Street, and American research institutions would narrow to a trickle.

## Who Supports It — and Why It Matters

The bill is backed by the Federation for American Immigration Reform, the Immigration Accountability Project, and U.S. Tech Workers — organizations that have long argued the H-1B program suppresses wages and displaces American workers. Co-sponsor Representative Eli Crane of Arizona has separately proposed a three-year moratorium on all H-1B issuances.

"For its nearly forty-year history, the H-1B visa has been abused, allowing employers to routinely sideline American STEM workers in favor of cheap foreign labor," Roy said. "It's time to end this lottery-based pipeline and replace it with a system that prioritizes merit."

India's major IT services firms have anticipated this direction. TCS chief executive K. Krithivasan noted the company has been "reducing dependency on visa-based talent over time," while Cognizant CEO Ravi Kumar pointed to "significantly reduced dependency on visas" coupled with increased local hiring and nearshore capacity.

## The Odds

The bill faces long odds. Comprehensive H-1B reform has stalled in Congress for decades, and any legislation that touches the tech industry's labor supply draws fierce lobbying from both sides. The bill was referred to committee and has not yet been scheduled for a hearing.

But odds and signals are different things. The bill codifies a direction — away from immigration as a career pathway, toward immigration as a temporary transaction — that already shapes executive action on fees, processing times, denial rates, and enforcement. Whether or not it passes, the American White-Collar Worker Jobs Act tells Indian workers what a significant faction of the U.S. Congress believes the H-1B program should look like.

It looks nothing like the program they came here for."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "A Bill in Congress Would End the H-1B-to-Green-Card Pipeline. Indian Tech Workers Are the Target",
    "subheadline": "The American White-Collar Worker Jobs Act would kill dual intent, scrap STEM OPT, and cap H-1B terms at two years — turning a decades-old career pathway into a revolving door.",
    "slug": make_slug("chip-roy-h1b-bill-dual-intent-stem-opt-indian-tech"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The bill directly targets the career model that hundreds of thousands of Indian tech workers have followed: H-1B to green card to citizenship. Killing dual intent and STEM OPT would fundamentally alter the calculus of studying and working in America.",
    "tags": ["h1b", "legislation", "stem-opt", "dual-intent", "green-card", "immigration", "congress"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Rep. Chip Roy Press Release", "url": "https://roy.house.gov/"},
        {"name": "LiveMint", "url": "https://www.livemint.com/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
        {"name": "Nagaland Post / IANS", "url": "https://www.nagalandpost.com/"},
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Capitol_Building_Full_View.jpg/1280px-Capitol_Building_Full_View.jpg",
    "image_caption": "The United States Capitol Building in Washington, D.C., where the American White-Collar Worker Jobs Act was introduced",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}


# ─── Insert ──────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
