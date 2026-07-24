#!/usr/bin/env python3
"""Immigration writer — 2026-07-14 07:00 PT run"""

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


# ─────────────────────────────────────────────
# ARTICLE 1: Cognizant under two-front legal siege
# ─────────────────────────────────────────────

art1_body = """The company that put the "outsourcing" in Indian IT is facing something it cannot outsource: an escalating legal crisis on two fronts that could reshape how America regulates its largest non-immigrant visa programme.

Cognizant Technology Solutions, a New Jersey-headquartered firm with deep roots in Chennai, is simultaneously contending with a federal appeals court review of fraud allegations and a direct name-check in the Trump administration's sprawling H-1B investigation. For the roughly 300,000 Indian nationals working at Indian IT services firms across the United States, the outcome could rewrite the rules of the road.

## The Whistleblower Case Reaches the Third Circuit

In early March, the U.S. Court of Appeals for the Third Circuit agreed to take up a False Claims Act lawsuit brought by Jean-Claude Franchitti, a former Cognizant assistant vice president turned government whistleblower. The core allegation is straightforward but damaging: Franchitti contends that Cognizant systematically applied for cheaper L-1 intracompany transfer and B-1 business visitor visas for workers from India who were actually performing duties that required the more expensive H-1B specialty occupation visa.

The result, the complaint argues, was that Cognizant shortchanged the government on filing fees — by $1,000 to $6,300 per visa — and underpaid workers, thereby reducing federal payroll tax obligations. A New Jersey district court had already found the theory viable, ruling that the relationship between Cognizant and the government constituted an "implied contractual" or "fee-based" arrangement under the False Claims Act.

Both Cognizant and Franchitti petitioned the Third Circuit for review — Cognizant to overturn the ruling, Franchitti to expand it. The U.S. Chamber of Commerce filed an amicus brief on Cognizant's behalf, underscoring the stakes: if the appeals court affirms, any large employer that routes workers through cheaper visa categories could face treble damages under the FCA.

## The Vance Probe Names Cognizant Directly

Then came July 8. Labour Department Inspector General Anthony D'Esposito, appearing alongside Vice President JD Vance to announce a major H-1B fraud investigation, told Fox Business that his office had received tips from "whistleblowers talking about some of the biggest companies" — and named Cognizant explicitly.

Cognizant declined to comment. But the public naming placed the company at the intersection of two forces: a nine-year-old whistleblower lawsuit that is now reaching its most consequential stage, and a politically charged enforcement campaign with backing from the White House.

The DOL probe is broader than any single company. D'Esposito said his team has already "uncovered widespread schemes in which employers and labour brokers submitted fraudulent applications, exploited foreign workers through coercive wage-kickback arrangements, and undercut American workers." Department of Homeland Security assessments have estimated that as many as 21 percent of H-1B petitions are fraudulent.

## What This Means for Indian IT and Its Workers

The Indian IT services model — deploying technically skilled workers from India to American client sites on a mix of H-1B, L-1, and B-1 visas — has been the economic engine behind hundreds of thousands of Indian families living in the United States. Cognizant alone employed over 70,000 workers in the U.S. at its peak.

If the Third Circuit endorses the theory that using cheaper visa categories for H-1B-level work constitutes fraud against the government, the financial exposure extends well beyond Cognizant. Infosys, Wipro, TCS, and HCL Technologies have all faced similar questions about their visa usage patterns over the years. A similar case against Infosys, *Krawitt v. Infosys*, was dismissed in a California court on narrower grounds — the Third Circuit's ruling could create a split that invites Supreme Court review.

For Indian workers already in the U.S. on these visas, the immediate risk is not deportation but disruption. Companies facing increased scrutiny may slow hiring, shift to domestic talent pipelines, or move work offshore entirely — none of which helps the engineer in Plano or the analyst in Iselin who is waiting for a green card that may take another decade to arrive.

Immigration attorneys say the timing amplifies the uncertainty. "When a company is both in active litigation and named in a government probe, it changes the risk calculus for every petition they file," said one employment lawyer who advises Indian IT firms but was not authorised to speak publicly. "USCIS adjudicators read the news too."

Cognizant's next earnings call will be watched closely — not just for revenue numbers, but for any signal about how the company plans to navigate a legal environment that is turning hostile to the business model that built it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Cognizant Is Under Siege. A Whistleblower Lawsuit and a Federal Probe Are Closing In at the Same Time",
    "subheadline": "The Third Circuit will review False Claims Act allegations that the IT giant used cheap visas for H-1B-level work, weeks after the Labour Department's inspector general named the company in Vance's fraud investigation.",
    "slug": make_slug("cognizant-whistleblower-third-circuit-dol-probe-h1b-fraud"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Over 300,000 Indian nationals work at Indian IT firms in the US — the legal outcome could reshape the visa model that brought them here and slow hiring for years.",
    "tags": ["h1b", "cognizant", "false-claims-act", "dol", "visa-fraud", "indian-it"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/litigation/h-1b-visa-fraud-lawsuit-should-go-to-third-circuit-judge-says"},
        {"name": "Law360", "url": "https://www.law360.co.uk/employment-authority/articles/2310050"},
        {"name": "Milwaukee Journal Sentinel", "url": "https://www.jsonline.com/story/news/politics/2026/07/11/in-targeting-h-1b-visas-jd-vance-ties-fraud-to-immigration-rhetoric/77037382007/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/07/09/opinion/work-visa-fraud-costs-america-big-hail-the-trump-teams-crackdown/"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/us-government-cognizant-eye-early-resolution-to-visa-misuse-case-11734873085834.html"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Cognizant_Technology_Solution%27s_office_in_Bentonville.jpg/1280px-Cognizant_Technology_Solution%27s_office_in_Bentonville.jpg",
    "image_caption": "Cognizant Technology Solutions office in Bentonville, Arkansas",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 2: EU and UK designate India "safe country"
# ─────────────────────────────────────────────

art2_body = """For decades, the Indian passport opened two kinds of doors in the West: one for skilled workers queuing patiently through legal channels, and another — quieter, riskier — for those who slipped in without papers and hoped to stay long enough to build a life. The second door is now being bolted shut, and the locksmiths are in Brussels, London, and Washington simultaneously.

Since June 12, the European Union's first-ever common list of safe countries of origin has been in force. India is on it, alongside Bangladesh, Colombia, Egypt, Kosovo, Morocco, and Tunisia. The designation means that any Indian national who claims asylum in an EU member state will be channelled into an accelerated procedure. The burden of proof flips: instead of the government needing to show the applicant is not at risk, the applicant must prove they face a "well-founded fear of persecution" — a high bar for nationals of the world's largest democracy.

The United Kingdom went further earlier. India was added to the UK's "safe states" list in November 2023, which makes asylum claims by Indian nationals effectively inadmissible unless "exceptional circumstances" apply. Home Secretary Yvette Cooper has since redeployed a thousand civil servants from the now-defunct Rwanda deportation scheme to a Returns and Enforcement programme targeting illegal workers, beginning with sectors like car washes and beauty salons where undocumented Indians are known to work.

## The Channel Crossings Surge

The UK's move was driven by numbers that made headlines. Indian arrivals on small boats crossing the English Channel surged 60 percent in 2023, reaching 1,192 — making Indians the second-largest group after Afghans in the first quarter of that year, accounting for 18 percent of all arrivals.

Home Office data shows Indian asylum seekers have one of the lowest acceptance rates of any nationality, which gave the government its justification: if few claims succeed, the argument goes, the claims are not genuine.

LGBTQ+ advocacy groups have pushed back. Rainbow Migration called the designation "cruel," noting that India criminalised homosexuality until 2018 under Section 377, and that social stigma and violence against queer Indians remain pervasive despite the legal change. The House of Lords' Secondary Legislation Scrutiny Committee flagged the same concern, noting that the Home Office promised guidance on "exceptional circumstances" but had not published it by the time the regulation was debated.

## The American Enforcement Wave

Across the Atlantic, the numbers tell a parallel story. India's Ministry of External Affairs confirmed in June that 1,076 Indian nationals had been deported from the United States in 2026 alone. The 2025 total was 3,567.

The deportations span a spectrum — from individuals with criminal records to those who overstayed visas or crossed borders without documents. India has accepted deportees without objection, maintaining what MEA spokesperson Randhir Jaiswal called a posture of "continuous dialogue with the US regarding migration and mobility to ensure that legal migration is facilitated while illegal migration is effectively curbed."

The US has also expanded financial deterrents. A visa bond pilot programme now covers 50 countries, requiring B-1 and B-2 applicants to post refundable deposits of up to $15,000. While India is not currently on the list, the programme's expansion — and its 97 percent compliance rate — signals that the infrastructure for broader application exists.

## What the Diaspora Should Understand

The legal and irregular migration tracks have always existed in parallel, but the crackdown on one is now spilling onto the other. Indian professionals on H-1B visas report increased scrutiny at consulates. Parents visiting on B-2 tourist visas face longer wait times and more pointed questions. The association — however unfair — between irregular Indian migration and the broader Indian diaspora is one that policymakers on both sides of the Atlantic are not trying very hard to disentangle.

For the estimated 4.8 million Indian Americans in the United States and over a million in the UK and EU combined, the message from Western capitals is clear: legal pathways remain open, but the tolerance for anything outside them has evaporated. The safe country designations and deportation campaigns are not about the engineer in Cupertino or the doctor in London — but the political environment they create affects everyone carrying an Indian passport."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The West Is Building a Deportation Fast Lane for Indians. Brussels, London, and Washington Are All on Board",
    "subheadline": "The EU's new safe-country list, the UK's accelerated returns programme, and over a thousand US deportations in 2026 add up to a coordinated crackdown on irregular Indian migration that is reshaping the political climate for the entire diaspora.",
    "slug": make_slug("eu-uk-us-india-safe-country-deportation-fast-track-crackdown"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "While legal Indian immigrants queue for decades, irregular migration from India is triggering a coordinated Western enforcement response that increases scrutiny on all Indian passport holders.",
    "tags": ["eu", "uk", "deportation", "safe-country", "asylum", "irregular-migration", "india", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "European Parliament", "url": "https://www.europarl.europa.eu/news/en/press-room/20260205IPR25807/asylum-vote-on-new-rules-on-safe-countries-of-origin-and-safe-third-countries"},
        {"name": "UK Parliament", "url": "https://www.parliament.uk/business/news/2024/february/lords-committee-raises-concerns-over-lack-of-essential-information-on-immigration-law-change-to-declare-india-and-georgia-as-safe-states/"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/how-trumps-immigration-crackdown-is-affecting-indians-1076-deportations-in-2026-11749131600629.html"},
        {"name": "Amnesty International", "url": "https://www.amnesty.org/en/latest/news/2026/02/eu-approval-of-safe-country-rules-another-attack-on-the-right-to-asylum/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2025/11/08/india-a-safe-list-for-uk-to-fast-track-illegal-migrants-return/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/European_Parliament_Strasbourg_Hemicycle_-_Diliff.jpg/1280px-European_Parliament_Strasbourg_Hemicycle_-_Diliff.jpg",
    "image_caption": "The European Parliament hemicycle in Strasbourg, where legislators voted to designate India a safe country of origin",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 3: Indian graduates sue over employer-fraud H-1B denials
# ─────────────────────────────────────────────

art3_body = """They did everything right. They graduated from American universities. They found employers willing to sponsor them. They filed their paperwork and waited for the system to work. Then the system told them they were guilty — not of anything they did, but of what their employers had done.

Nearly 70 Indian nationals have filed a lawsuit in federal district court in Washington state against the U.S. government, alleging that the Department of Homeland Security denied their H-1B specialty occupation visas because of fraud committed by their previous employers. The workers say they had no knowledge of the fraud. They were never given a chance to respond to the allegations. And the denials followed them even after they moved on to legitimate companies.

## Guilt by Association

The plaintiffs had been employed through training programmes for foreign graduates of American colleges — pathways designed to bridge the gap between a degree and a career. Some of their employers, it turned out, had submitted fraudulent applications, misrepresented job positions, or operated shell companies. When federal investigators caught the fraud, the government revoked or denied the workers' visa petitions — treating them as complicit by default.

According to the complaint filed in Washington state, "the agency assumed that anybody who" was associated with the fraudulent employer was themselves fraudulent, without conducting individual assessments or offering due process.

The workers had since found employment at legitimate companies. Their new employers filed fresh H-1B petitions on their behalf. But DHS denied those too, citing the earlier association. The stain of the original employer's fraud, in effect, had become permanent.

## The Timing Makes It Worse

The lawsuit lands at a moment when the Trump administration is actively expanding its fraud enforcement apparatus. Vice President JD Vance announced on July 8 that the Department of Labour had issued dozens of subpoenas as part of a major H-1B fraud investigation. Labour Department Inspector General Anthony D'Esposito said his office had "uncovered widespread schemes in which employers and labour brokers submitted fraudulent applications, exploited foreign workers through coercive wage-kickback arrangements, and undercut American workers."

Nobody disputes that fraud exists. A Department of Homeland Security review estimated that up to 21 percent of H-1B petitions may be fraudulent. But the question the lawsuit poses is different: when the government catches the fraudsters, should it also punish the workers who were their victims?

Immigration attorneys have long warned about this dynamic. Smaller staffing firms and so-called body shops — intermediaries that place workers at client sites — are where most H-1B fraud concentrates. The workers they employ are often recent graduates with limited options, willing to take whatever sponsorship they can get in a system where the H-1B lottery rejects three out of four applicants.

"These workers are the most vulnerable people in the entire chain," said one immigration lawyer who has handled similar cases. "They cannot control what their employer puts on the petition. They cannot audit the LCA. They are completely dependent on the system behaving honestly, and when it does not, they are the ones who pay."

## The Structural Problem

The H-1B programme ties a worker's legal status to their employer in a way that creates inherent power imbalances. An H-1B holder who discovers their employer is fraudulent faces an impossible choice: report it and risk deportation, or stay silent and hope nobody notices. There is no visa category for "whistleblower in good faith."

This structural bind is what makes the Washington state lawsuit significant beyond its 70 plaintiffs. If the court rules that DHS cannot deny future visa petitions based solely on a prior employer's fraud — without evidence that the worker participated in or knew about the scheme — it would establish a precedent that separates the worker's fate from the employer's misconduct.

If it rules the other way, the message to every Indian graduate in America is grimly clear: choose your first employer carefully, because if they turn out to be crooked, your immigration future may be over before it begins.

## A Broken Feedback Loop

The irony is that the government's own crackdown may be creating the problem it claims to solve. As enforcement tightens and legitimate companies grow cautious about sponsoring H-1B workers, graduates are pushed toward the margins — toward the smaller firms, the body shops, the companies willing to take a chance. The very entities most likely to commit fraud are the ones that benefit most from a system that makes it harder for workers to go elsewhere.

Until the programme is reformed to give workers some measure of independence from their sponsors — through portable work authorisation, a formal whistleblower pathway, or at minimum a right to respond before their petitions are denied — the most qualified and law-abiding applicants will continue to absorb the costs of a system that was not designed with their interests in mind."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "They Did Not Commit Fraud. Their Employers Did. The Government Punished Them Anyway",
    "subheadline": "Nearly 70 Indian graduates are suing the US government for denying their H-1B visas over fraud they did not know about, did not commit, and were never given a chance to contest.",
    "slug": make_slug("indian-graduates-sue-h1b-denial-employer-fraud-due-process"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian graduates are the most vulnerable link in the H-1B chain — punished for employer fraud they had no part in, with no due process and no path to clear their names.",
    "tags": ["h1b", "fraud", "lawsuit", "indian-graduates", "due-process", "uscis", "dhs"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/litigation/indian-grads-sue-over-h-1b-denials-based-on-employers-fraud"},
        {"name": "Milwaukee Journal Sentinel", "url": "https://www.jsonline.com/story/news/politics/2026/07/11/in-targeting-h-1b-visas-jd-vance-ties-fraud-to-immigration-rhetoric/77037382007/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/07/09/us-news/vance-labor-watchdog-launch-immigration-fraud-probe-to-protect-american-jobs/"},
        {"name": "Fox News", "url": "https://www.foxnews.com/politics/fury-erupts-us-brand-fires-1600-employees-after-securing-thousands-foreign-worker-visas"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16151491/pexels-photo-16151491.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A neoclassical government building in Washington, where federal courts hear immigration cases",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}


# ─────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
