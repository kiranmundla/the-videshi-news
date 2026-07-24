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
        "headline": "No Interview, No Problem — USCIS Wants to Reject Asylum Claims on Paper Alone",
        "subheadline": "A leaked regulation would let officers deny applications without ever meeting the applicant, upending decades of asylum practice and catching thousands of Indian applicants in a bureaucratic dragnet.",
        "slug": make_slug("uscis-asylum-no-interview-rejection-one-year-rule-indian"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Thousands of Indian nationals — from IT workers who overstayed visas to Sikh and Muslim families fleeing religious persecution — have pending asylum applications with USCIS. Many filed more than a year after entering the US, often after exhausting other visa options. The proposed rule would let officers reject these cases without a single interview, routing applicants directly into deportation proceedings where they face an overburdened immigration court system with 3.3 million pending cases.",
        "tags": ["asylum", "uscis", "immigration", "deportation", "indian-diaspora"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CBS News", "url": "https://www.cbsnews.com/news/trump-asylum-rejection-plan/"},
            {"name": "LiveMint", "url": "https://www.livemint.com/news/us-news/trump-admin-weighs-plan-to-reject-asylum-applications-without-interviewing-applicants-amid-massive-backlog-11780320795347.html"},
            {"name": "News9", "url": "https://www.news9.com/politics/trump-administration-plan-would-allow-for-quick-asylum-rejections-documents-show/"},
            {"name": "USCIS Processing Times 2026", "url": "https://www.alonsoandalonsolaw.com/blog/uscis-processing-times/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/36984942/pexels-photo-36984942.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """For decades, the American asylum system operated on a foundational premise: before the government could reject your claim, someone had to look you in the eye and listen. That premise is about to be discarded.

Internal federal documents obtained by CBS News reveal that the Department of Homeland Security is developing a regulation that would empower USCIS officers to reject asylum applications without interviewing the applicants — a procedural shortcut aimed squarely at the 1.5 million pending affirmative asylum cases clogging the agency's docket.

## The one-year tripwire

The proposed rule targets a specific provision of immigration law: the requirement that asylum seekers file their applications within one year of arriving in the United States. Under current practice, USCIS officers interview virtually all applicants before making a decision, giving them an opportunity to explain why they missed the deadline — a serious medical condition, inadequate legal counsel, or changed country conditions are all recognised exceptions.

The new regulation would strip away that interview. If an officer reviewing the paper record determines the applicant filed after the one-year mark and finds no obvious exception, the case gets denied on the spot. The applicant is then placed in deportation proceedings before a Department of Justice immigration court, where they must argue their case in an adversarial setting — often without legal representation.

https://x.com/USCIS/status/1929574839218438144

A USCIS spokesperson confirmed the agency is "considering multiple options" to address the backlog, including routing "deficient" applications directly to immigration courts. The spokesperson framed the move as efficiency: "This would allow USCIS to avoid wasting time on asylum applications that it would otherwise refer to immigration proceedings."

## The numbers behind the backlog

The scale of the asylum backlog is staggering. USCIS had 1.5 million pending affirmative asylum applications as of last fall. The DOJ's immigration courts — which handle deportation cases — had 3.3 million pending claims as of March, with 2.3 million of those involving asylum requests.

Combined, the system is processing cases at a pace that leaves applicants waiting years, sometimes the better part of a decade, for a hearing. The average USCIS processing time for an asylum application has hovered around 180 days in recent quarters, but that figure masks enormous variation. Many applicants wait far longer, particularly those from countries with high denial rates or complex geopolitical situations.

## Where Indian applicants stand

India is not typically associated with asylum flows, but the numbers tell a different story. Indian nationals have filed thousands of asylum applications in recent years, driven by a range of claims: Sikh families citing religious persecution, Muslims alleging communal violence, Dalit individuals claiming caste-based discrimination, and activists facing political reprisals.

Many Indian asylum seekers arrived in the United States on valid visas — H-1B, F-1, B-1/B-2 — and applied for asylum only after their status expired or their circumstances in India changed. That pattern means a substantial number filed more than a year after entry, precisely the cases the new regulation would target for summary denial.

The one-year filing deadline has always been a minefield for Indian applicants. Immigration lawyers who represent Indian clients say the deadline is frequently missed not out of negligence but because asylum is often a last resort — something considered only after an H-1B transfer falls through, a green card petition stalls, or conditions back home deteriorate beyond what was expected.

## The immigration court bottleneck

Routing denied applicants into immigration court sounds like due process. In practice, it means entering a system that is barely functional. With 3.3 million cases pending and a corps of roughly 600 immigration judges, the average wait for a hearing stretches well beyond two years in most jurisdictions. Some courts in New York and California have backlogs exceeding five years.

For Indian applicants specifically, the shift from an affirmative asylum interview — conducted by a trained asylum officer in a non-adversarial setting — to a removal hearing before an immigration judge represents a dramatic change in stakes. In court, the government is represented by a trial attorney whose job is to argue for deportation. Applicants who cannot afford a private lawyer often appear pro se, a disadvantage that immigration advocates say leads to higher denial rates.

Immigration attorney Conchita Cruz of the Asylum Seeker Advocacy Project warned that the regulation would "wrongfully" place applicants in deportation proceedings without allowing them to explain why they missed the filing deadline. "The government would be changing the rules on immigrants who have been navigating a complex immigration process, often for many years," she said.

## What this means for the diaspora

The proposed regulation is part of a broader pattern: an administration that is systematically raising the cost — financial, procedural, emotional — of every immigration pathway. For the Indian diaspora, the asylum pipeline has always been a quiet, rarely discussed channel. But for the families using it, the difference between an interview and a paper rejection is the difference between being heard and being deported.

The regulation has not yet been published in the Federal Register, and legal challenges are virtually certain once it is. But for the estimated thousands of Indian nationals with pending asylum claims that were filed after the one-year mark, the clock just started ticking in a direction they did not expect."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The $70 Billion Vote That Could Reshape Immigration Enforcement Hits the Senate Floor Today",
        "subheadline": "Senate Republicans are pushing to advance the largest immigration enforcement package in American history — but Trump just contradicted his own attorney general on whether a controversial slush fund is really dead.",
        "slug": make_slug("senate-70b-ice-cbp-reconciliation-vote-anti-weaponization"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "A $70 billion ICE and CBP funding package covering three years would dramatically expand workplace enforcement — including FDNS site visits to H-1B employers, audits of I-9 records at Indian IT staffing firms, and the operational capacity to sustain the current pace of deportation operations. For the 600,000-plus Indian nationals on temporary work visas, the bill's passage means a more aggressive enforcement apparatus with more officers, more technology, and more funding to scrutinise every filing.",
        "tags": ["ice", "cbp", "senate", "reconciliation", "enforcement", "h1b", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CNN", "url": "https://www.cnn.com/2026/06/03/politics/anti-weaponization-fund-trump"},
            {"name": "Fox News", "url": "https://www.foxnews.com/politics/gop-demands-trump-kill-controversial-2b-fund-before-reviving-ice-funding-package"},
            {"name": "MarketWatch/Morningstar", "url": "https://www.morningstar.com/news/marketwatch/20260601219/trump-backs-down-on-his-anti-weaponization-fund-funding-for-immigration-enforcement-should-now-get-the-senates-ok"},
            {"name": "News9", "url": "https://www.news9.com/politics/doj-anti-weaponization-fund/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/2023_United_States_Capitol_118th_Congress%2C_sunrise.jpg/1280px-2023_United_States_Capitol_118th_Congress%2C_sunrise.jpg",
        "body": """The largest immigration enforcement funding package in American history could clear a critical hurdle in the Senate as early as today — but the road to a vote has been a masterclass in political chaos, with the president himself muddying the waters at the worst possible moment.

Senate Majority Leader John Thune told reporters Wednesday morning that he is "hopeful" of teeing up a vote-a-rama later today to advance the $70 billion reconciliation bill that would fund Immigration and Customs Enforcement and Customs and Border Protection through the end of Trump's term. The bill, which requires only 51 votes under budget reconciliation rules, would represent the single largest investment in immigration enforcement infrastructure in American history.

## The anti-weaponization wrench

The bill was supposed to pass before the Memorial Day recess. Instead, Senate Republicans pulled the plug after an explosive closed-door meeting with Acting Attorney General Todd Blanche over the administration's $1.776 billion "anti-weaponization fund" — a settlement mechanism created from Trump's lawsuit against the IRS over leaked tax returns that critics said could funnel payments to January 6th defendants and presidential allies.

The backlash was bipartisan in spirit, if not in vote count. Senator Mitch McConnell called the fund "utterly stupid, morally wrong." Senator John Kennedy of Louisiana compared the reconciliation process to "a broken arm with a bone sticking out." Democrats pledged to force amendment votes that would put vulnerable Republicans on record supporting or opposing the fund.

On Tuesday, Blanche delivered what Senate leaders wanted to hear: the Department of Justice would not move forward with the fund. "We are not moving forward with the fund, period," Blanche told a House Appropriations subcommittee. When pressed by Democratic Representative Grace Meng — "Not moving forward, ever?" — Blanche replied, "Correct."

## Then Trump spoke

Hours after Blanche's definitive statement, an interview Trump taped the same day was released on the New York Post's podcast. Asked if he had dropped the fund, Trump said: "No, a court ruled against it." He argued that people targeted by what he called a "crooked government" deserve compensation. "I think they should be reimbursed for a crooked government," he said.

The contradiction set off a familiar dynamic in Washington: staff scrambling to reconcile a principal's public statements with the policy position they had just locked down. A Republican aide downplayed the damage. "I don't feel concerned about what he said," the aide told CNN. "Him saying a court ruled against it is about as close to 'yes I'm dropping it' as we will get."

Senator Lindsey Graham proposed a compromise on X — creating a fund available through the Federal Tort Claims Act for those who can prove their cases. Associate Attorney General Stanley Woodward Jr. responded, "We're on it," in a post that was later deleted.

Thune, for his part, said Wednesday morning that Blanche's comments were "extremely helpful" and that "most of our members feel pretty satisfied." But he acknowledged uncertainty about whether four or more Republican holdouts might still block the bill.

## What is in the $70 billion

Strip away the political theatre and the bill is straightforward in its ambition. The $70 billion funds ICE and CBP operations for approximately three years, covering:

**Personnel**: Thousands of additional ICE Enforcement and Removal Operations officers, Homeland Security Investigations agents, and CBP officers — the largest hiring surge since the agency's creation in 2003.

**Technology**: Expanded surveillance and biometric systems at ports of entry and along the border, plus upgrades to the TECS and ENFORCE databases used for immigration case tracking.

**Detention capacity**: Funding for additional detention beds and facilities, expanding the system's capacity to hold individuals in removal proceedings.

**Worksite enforcement**: Resources for the Fraud Detection and National Security directorate (FDNS), which conducts site visits to employers who sponsor H-1B and other work visa holders.

## The Indian diaspora dimension

For Indian nationals in the United States — the majority on H-1B, L-1, or F-1 visas — the enforcement implications of this bill are specific and material.

FDNS site visits to H-1B employer worksites have already increased substantially under the current administration. The bill would provide funding to sustain and expand that pace. Indian IT staffing and consulting firms, which sponsor a significant share of H-1B petitions, have historically been a primary target of these compliance checks.

The expanded ICE operations also affect the roughly 800,000 Indian nationals in the green card backlog. Many hold valid work authorisation, but administrative errors — an expired EAD, a gap in status due to processing delays — can trigger enforcement attention. A more heavily resourced ICE has more capacity to act on such discrepancies.

The bill does not create new immigration law. It does not change visa caps, alter the green card backlog, or modify asylum standards. What it does is give the existing enforcement apparatus significantly more money to do what it already does — and for three full years, insulated from the annual appropriations fights that have periodically starved these agencies of funds.

## What happens next

If Thune can secure a majority to proceed, the Senate would enter a vote-a-rama — an extended session where senators can offer an unlimited number of amendments. Democrats have telegraphed their intent to force politically uncomfortable votes on the anti-weaponization fund, ICE tactics, and other wedge issues.

The bill is expected to pass eventually along party lines. The question is whether today's vote begins that process or whether Trump's podcast comments give holdouts an excuse to demand yet another round of assurances. For the Indian diaspora watching from the other side of the enforcement apparatus, the outcome is the same either way: more resources, more officers, more scrutiny. The only variable is timing."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
