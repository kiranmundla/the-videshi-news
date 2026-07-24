#!/usr/bin/env python3
"""Immigration writer — 2026-07-10 19:00 PDT run. Two articles."""

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


# ─── ARTICLE 1: Social Media Vetting Expansion ──────────────────────────────

article1_body = """The next time you renew your green card, extend your H-1B, or apply for a travel document, expect a new question on the form: list every social media account you have used in the past ten years. Even the ones you closed.

The U.S. Citizenship and Immigration Services has announced that updated versions of forms covering permanent residence, naturalization, employment authorization, and travel documents will require applicants to disclose comprehensive personal details, including a decade's worth of social media handles. The State Department's DS-160, already requiring five years of disclosure since 2019, is expanding its scope in parallel. The combined effect covers virtually every immigration touchpoint an Indian professional might encounter during a career in the United States.

## The Standard Nobody Has Written

The policy rationale is straightforward enough. Under the administration's enhanced vetting framework, launched on January 20, 2025, immigration is framed as a privilege whose grant must align with "U.S. national interests." Applicants should expect to surrender a degree of privacy in exchange for the benefit of living and working in the country.

What the government has not provided is equally important: a definition of what constitutes objectionable content. The executive order directing the enhanced screening references "anti-American views," but no regulation, guidance document, or FAQ has clarified what that means in practice. Does criticism of a sitting president qualify? Does attending a protest? Does a college-era tweet from an account you forgot existed?

"So far, what constitutes 'anti-Americanism' has remained undefined," noted a Reuters analysis published this week. "The government has not provided clear, real-world guidance on what specific types of social media content may be considered 'objectionable' or contrary to U.S. interests."

For the roughly 600,000 H-1B holders in the country — 73 percent of whom are Indian nationals — the ambiguity is the point of concern. An undefined standard is, by nature, one that cannot be prepared for.

## The Delays Are Already Here

The operational consequences have not waited for the new forms to be finalized. When the State Department expanded social media vetting to H-1B and H-4 visa categories in December 2025, U.S. consulates in India needed time to build out their new review infrastructure. The solution was blunt: visa appointments scheduled for November and December were abruptly rescheduled to March 2026 and beyond.

The result was chaos. Foreign-national employees who had traveled to India for the holidays found themselves stranded for months, unable to return to their jobs. Chennai and Hyderabad, which process the largest volume of IT professional visas, were hit hardest.

The delays have rippled into 2026. With consular officers now required to review social media content as a standard part of adjudication, appointment backlogs have grown rather than shrunk. Immigration attorneys describe "chaotic implementation" and "no consistent logic between consulates" as each post adjusts to the additional workload.

## At the Border, Your Phone Is Fair Game

Social media review no longer stops at the application form. Customs and Border Protection officers are increasingly searching the electronic devices of foreign nationals entering the United States, including laptops and phones. During these stops, officers may ask travelers to unlock their devices, giving them direct access to social media accounts, private messages, and browsing history.

These searches fall within existing border authority — the Supreme Court has held that the Fourth Amendment's protections are diminished at the border — but their rising frequency has alarmed both workers and employers. Companies are now advising H-1B employees to avoid downloading sensitive corporate documents to personal devices before international travel, and to assume that any device they carry could be searched.

## What This Means for Indian Professionals

For the Indian professional navigating the U.S. immigration system, the practical implications are immediate.

Every form filed going forward will require a thorough audit of one's digital footprint — not just active accounts, but dormant ones, closed profiles, and platforms used once during college. Omitting an account, even inadvertently, risks being treated as a credibility issue rather than a clerical error.

The DS-160 already requires that social media profiles be set to public before a visa interview. "Restricting visibility during the process may be viewed as an attempt to withhold information," warned immigration law firm Boundless in guidance issued to applicants.

More than 14 immigration forms are expected to incorporate the expanded social media questions, including the I-485 (adjustment of status), N-400 (naturalization), I-765 (employment authorization), and I-131 (travel document). For an Indian worker on an H-1B who files multiple forms over the course of a green card application, the disclosure requirement will apply at every stage.

The administration has emphasized that no widespread pattern of visa denials based solely on social media activity has emerged — yet. But as one Reuters analysis concluded: "The long-term structural impact is still unfolding."

For three hundred and sixty thousand Indian students in the country and hundreds of thousands of working professionals, the unfolding has already begun."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Government Wants Ten Years of Your Social Media Handles. It Has Not Defined What Gets You Denied",
    "subheadline": "Updated USCIS forms will require a decade of social media disclosure across virtually every immigration application. The definition of 'objectionable' content remains conspicuously absent.",
    "slug": make_slug("uscis-social-media-vetting-ten-years-handles-immigration-forms"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals — who make up 73% of H-1B holders — face an undefined content standard that could affect every green card, naturalization, and work authorization filing they submit.",
    "tags": ["uscis", "social-media-vetting", "h1b", "immigration", "visa-forms", "ds-160"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/legalindustry/stricter-vetting-slower-processing-how-new-immigration-form-changes-are--pracin-2026-07-06/"},
        {"name": "Boundless Immigration", "url": "https://www.boundless.com/immigration-resources/us-expands-social-media-vetting-to-more-visas/"},
        {"name": "Herman Legal Group", "url": "https://www.lawfirm4immigrants.com/new-dhs-social-media-rule-2026-spouses-students-workers/"},
        {"name": "Hughes Law Group / Medium", "url": "https://medium.com/@hugheslawgrouppc/how-expanded-uscis-vetting-is-affecting-immigration-cases-in-the-usa-2026"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/267389/pexels-photo-267389.jpeg",
    "image_caption": "Social media app icons on a smartphone screen — the same platforms USCIS now requires applicants to disclose",
    "image_attribution": "Pexels",
    "body": article1_body
}


# ─── ARTICLE 2: Student Visa Crackdown's Economic Cost ──────────────────────

article2_body = """Removing a state from the union takes a constitutional amendment. Removing a state's worth of economic output apparently takes a policy memo.

A new analysis from the Peterson Institute for International Economics has calculated the cumulative cost of the administration's international student crackdown: between $240 billion and $481 billion in annual GDP a decade from now. That upper figure is roughly the size of Wisconsin's entire economy — gone, not because factories closed or crops failed, but because the pipeline that feeds America's most productive workforce was quietly shut off.

## The Numbers Behind the Number

The study, authored by PIIE researcher Michael A. Clemens alongside Amy Nice of Cornell University and Jeremy Neufeld of the Institute for Progress, traces the damage to a simple statistic: F-1 student visa issuance ran approximately one-third below normal through September 2025, following a series of rule changes that made it harder for foreign nationals to study at U.S. universities and remain to work after graduating.

That one-third drop matters because of what comes after graduation. Thirty-five percent of doctoral-level STEM workers in the United States are foreign-born and U.S.-trained. These are not abstract numbers. They represent the researchers building the next generation of AI models, the engineers designing semiconductor fabs, the scientists running clinical trials. When the student pipeline contracts, the high-skill labor force contracts with it — not immediately, but inexorably, as fewer PhDs and master's graduates enter the workforce each year.

"In comparable past episodes, neither foreign-trained workers from abroad nor U.S.-born students stepped in to fill the gap," Clemens wrote. "We see no reason this time will be different."

## Indian Students Are Half the Story

The crackdown has not been evenly distributed. According to data compiled by the American Immigration Lawyers Association, Indian nationals account for 50 percent of tracked visa revocations — a share that far exceeds their 31 percent representation in the international student population.

India sent 363,000 students to the United States in the 2024-25 academic year, making it the single largest source of international enrollment. Indian students are also disproportionately concentrated in STEM fields and on Optional Practical Training, the post-graduation work authorization pathway that has become a critical bridge to the H-1B visa.

That concentration makes them especially vulnerable. When the government introduced the "Catch and Revoke" program — allowing ICE to terminate a student's SEVIS record based on State Department visa revocations, criminal database flags, or AI-assisted social media screening — OPT holders bore the brunt. Fifty percent of affected students were on OPT, according to AILA. A SEVIS termination strips work authorization immediately, meaning an Indian engineer at a Silicon Valley startup or a data scientist at a research lab can lose the right to work overnight.

Between March and May 2025, more than 4,700 international students had their SEVIS records terminated. Most were eventually restored, but restored SEVIS records did not mean restored visas — the revocations remained in effect, and ICE subsequently re-terminated some records shortly after restoration.

## The Structural Squeeze

The four-year fixed visa limit introduced in August 2025 added a structural constraint. Many graduate and doctoral programs — particularly in the sciences and engineering fields where Indian students cluster — require five to seven years to complete. Under the new system, students must apply for formal extensions, introducing uncertainty and processing delays into what was previously a straightforward enrollment.

A separate proposal expected in early 2027 would restrict both the 24-month STEM OPT extension and Curricular Practical Training, the two most commonly used pathways for Indian graduates to gain work experience before entering the H-1B lottery. Immigration attorney Sara Goldman told The Indian Eye that thousands of Indian professionals in AI, machine learning, and software engineering "could face uncertainty if they lose access to this pathway after repeated H-1B lottery rejections."

The "Day 1 CPT" route — enrolling in another master's program to maintain work authorization while waiting for H-1B selection — may also narrow significantly. "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" Goldman said.

## Who Fills the Gap

The Peterson Institute study addresses the most common counterargument directly: that American-born workers will simply step in. The research finds no evidence that international students are "crowding out" opportunities for U.S.-born STEM majors. The labor market for doctoral-level scientists and engineers has, for decades, depended on foreign talent not as a substitute for domestic talent, but as a complement to it.

When that complement disappears, the studies suggest, the work does not get done domestically. It moves overseas, or it simply does not get done at all.

The administration has said these measures are designed to curb visa abuse, ensure national security, and prioritize American workers. What the Peterson Institute analysis quantifies is the price: an economy-sized hole where a workforce used to be."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Student Visa Crackdown Will Cost America Half a Trillion Dollars. Indian Students Are Half the Story",
    "subheadline": "A Peterson Institute analysis finds the international student squeeze could erase up to $481 billion in annual GDP within a decade. Indian nationals account for 50 percent of tracked visa revocations.",
    "slug": make_slug("student-visa-crackdown-gdp-cost-piie-indian-students"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian students are 31% of international enrollment but 50% of visa revocations — and they dominate the STEM OPT pipeline that feeds the H-1B workforce.",
    "tags": ["f1-visa", "student-visa", "OPT", "STEM", "immigration", "h1b", "indian-students"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Investopedia / Peterson Institute", "url": "https://www.investopedia.com/international-student-crackdown-blows-a-wisconsin-sized-hole-in-us-economy-analysis-shows-12013372"},
        {"name": "PIIE Research Paper", "url": "https://www.piie.com/publications/working-papers/2026/class-dismissed-effect-international-student-exclusion-us-stem-workforce"},
        {"name": "Collegedunia (AILA data)", "url": "https://collegedunia.com/usa/article/us-sevis-termination-rules-2026-what-indian-f1-students-must-know"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/tighter-student-visa-rules-may-impact-indians-in-us-expert/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8093017/pexels-photo-8093017.jpeg",
    "image_caption": "Graduates in caps and gowns celebrate commencement — a milestone now clouded by visa uncertainty for international students",
    "image_attribution": "Pexels",
    "body": article2_body
}


# ─── INSERT ──────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
