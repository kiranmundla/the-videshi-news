#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-31 batch"""
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
        "headline": "Your Visa Application Now Comes With a Social Media Audit — and It Just Got Wider",
        "subheadline": "The State Department has expanded mandatory social media screening to ten more visa categories, including fiancé visas, religious workers, and trafficking survivors. For Indian applicants, the implications reach far beyond H-1B.",
        "slug": make_slug("social-media-visa-screening-expansion-indian-applicants"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals applying for K-1 fiancé visas, R-1 religious worker visas, and dependent categories now face the same social media disclosure requirements that H-1B workers have dealt with since December 2025. With India sending tens of thousands of applicants annually across these categories, the screening expansion affects a far wider swath of the diaspora than the H-1B headlines suggest.",
        "tags": ["visa-screening", "social-media", "state-department", "k1-visa", "r1-visa", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://travelandtourworld.com/news/article/mexico-joins-us-visa-social-media-screening/"},
            {"name": "Stanford Bechtel International Center", "url": "https://bechtel.stanford.edu/immigration/social-media-vetting"},
            {"name": "WR Immigration (Wolfsdorf)", "url": "https://wolfsdorf.com/expanded-screening-and-vetting-for-visa-applicants/"},
            {"name": "McKnight's Senior Living", "url": "https://mcknightsseniorliving.com/home/news/state-department-factors-in-social-media-in-screening/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/267389/pexels-photo-267389.jpeg",
        "body": """The U.S. State Department has quietly extended its mandatory social media screening regime to a significantly broader set of visa categories — and the latest round reaches deep into corners of the immigration system that most Indian applicants assumed were still untouched.

## The New Categories

Under updated guidance published in late May, applicants for A-3 (diplomatic household staff), G-5 (international organization employees' household staff), H-3 (trainees), H-4 dependents of H-3 workers, K fiancé visas, Q cultural exchange visas, R religious worker visas, S witness visas, and T and U visas tied to trafficking and crime victims must now set all social media accounts to "public" and submit them for government review during the visa adjudication process.

The expansion follows a phased rollout that began with F, M, and J student and exchange visitor visas in June 2025, then extended to H-1B workers and their H-4 dependents on December 15, 2025. With this latest round, virtually every nonimmigrant visa category now carries a social media disclosure requirement.

Mexico, the Dominican Republic, Brazil, Colombia, and the Philippines are among the countries whose nationals now face what the State Department describes as the "most stringent" tier of screening. Consular officers are instructed to review public posts, likes, shares, comments, group affiliations, biographical information, and education and work history across all listed platforms.

## What Officers Are Looking For

According to guidance compiled by WR Immigration, consular officers are screening for content suggesting "hostile attitudes" toward the United States, links to or endorsement of groups the U.S. considers terrorist organizations, evidence of antisemitic activity, immigration noncompliance, and posts that appear "threatening, harassing, or hostile toward people or institutions in the U.S." Officers are required to document findings with screenshots and notes in the case file.

Applicants who refuse to set their accounts to public — or who appear to have deleted or hidden activity — may have their applications denied. The State Department has framed the refusal itself as a potential indicator that the applicant is trying to evade the vetting requirement.

## Why This Matters for Indian Americans

The expansion hits several categories that are disproportionately used by the Indian diaspora. K-1 fiancé visas are a common pathway for NRIs marrying spouses from India. R-1 religious worker visas are the primary route for Hindu temple priests, Sikh granthi, and other religious professionals sponsored by Indian-American communities across the country. The H-3 trainee category is used by Indian companies sending employees for short-term training programs in the United States.

In practical terms, an Indian temple in New Jersey sponsoring a priest from Tamil Nadu must now ensure that the candidate's social media accounts are set to public and free of anything a consular officer might interpret as hostile. A software engineer in Hyderabad engaged to an Indian-American in California now faces the same screening when applying for a K-1 visa.

The chilling effect on online expression is already measurable. Immigration attorneys report that clients are preemptively scrubbing their social media accounts, deleting old posts, and in some cases deactivating accounts entirely before filing visa applications. Stanford's Bechtel International Center advises applicants to "search for your name online and ensure what comes up aligns with how you want to present yourself" — a polite way of saying that your decade-old Facebook opinion on Kashmir could now be grounds for a visa denial.

## Processing Delays Ahead

Immigration lawyers warn that the expanded screening will almost certainly increase processing times across the board. Every additional review step adds days or weeks to adjudication. For applicants already waiting months for interview slots at overloaded consulates in Mumbai, Delhi, Chennai, and Hyderabad, the screening creates another layer of delay in an already glacial system.

The State Department has not published specific timelines for how long social media reviews will take, nor has it disclosed how many additional staff have been assigned to the task. What it has made clear is that a U.S. visa is, in its words, "a privilege, not a right" — and that privilege now comes with a social media audit attached.

For the roughly 700,000 Indian nationals who apply for U.S. visas each year, the message is unambiguous: before you apply, clean up your feed."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Copilot Wrote the Code. Your H-1B Petition Wrote Itself Out.",
        "subheadline": "AI coding tools are not just automating tasks — they are structurally reducing the number of developers companies want to sponsor. For Indian engineers on H-1B visas, the shift from 'we need your skills' to 'the machine has those skills' is already reshaping hiring decisions.",
        "slug": make_slug("ai-coding-tools-h1b-developer-demand-structural-shift"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals hold the largest share of H-1B visas in the United States, with software development being the dominant occupation category. As AI coding assistants compress the value of routine engineering work, the entire economic justification for H-1B sponsorship — that these skills cannot be found domestically — is being quietly undermined. For hundreds of thousands of Indian developers in the U.S., this is not a layoff story. It is a structural obsolescence story.",
        "tags": ["h1b", "ai", "developers", "hiring", "silicon-valley", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "InfoWorld", "url": "https://www.infoworld.com/article/4178167/developers-on-h-1b-face-a-tighter-job-market-as-ai-shifts-hiring-priorities.html"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/ai-age-firms-chase-growth-fewer-workers-2026-05-26/"},
            {"name": "CNN", "url": "https://www.cnn.com/2026/05/28/tech/ai-software-engineer-interviews/index.html"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/34804018/pexels-photo-34804018.jpeg",
        "body": """For a generation of Indian engineers, the H-1B visa represented a contract: you bring specialized skills America cannot source domestically, and in return, you get a shot at building a career in the world's largest technology market. That contract is being rewritten — not by politicians, but by software.

## 'Companies Are Not Looking for H-1B Now'

The shift is blunt enough that industry analysts are saying it out loud. "Companies are not looking for H-1B now," Pareekh Jain, CEO of Pareekh Consulting, told InfoWorld this week. "They are building a local workforce and preferring green card holders and citizens."

The driver is not anti-immigrant sentiment in HR departments. It is a cold arithmetic change in what a software developer is worth when AI coding assistants — GitHub Copilot, Claude, ChatGPT, Cursor — can generate, debug, and refactor code at a speed and cost that makes the sponsorship calculus harder to justify. Why pay $100,000 in H-1B fees (thanks to the Trump proclamation) plus legal costs plus relocation for a mid-level developer when a senior engineer with a green card can use AI tools to do the work of three?

Employers are no longer building benches of visa-dependent workers for future projects. They are hiring for immediate, specific needs — and when those needs can be partially met by AI, the H-1B candidate is the first one removed from the shortlist.

## The Junior Developer Is Already Gone

The impact is sharpest at the bottom of the experience ladder. Adarsh ML, a product engineer at Ather Energy who tracks global engineering hiring trends, described the shift in stark terms: "Job opportunities for people with zero to three or four years of experience are not really there anymore."

The typical Indian pathway — graduate from IIT or an NIT, get an MS in the U.S., land an entry-level SDE role on OPT, pray for the H-1B lottery — is fracturing at the employment step. Companies that once hired two or three interns and several freshers per team are replacing those roles with AI agents. What remains are positions for engineers experienced enough to catch the mistakes those agents make.

This creates what Adarsh calls the talent pipeline paradox: "If companies only want people with five years of experience to manage AI agents today, who will have that experience five years from now? There may not be enough experienced developers left."

For Indian graduates, the paradox is compounded by visa constraints. You cannot gain five years of U.S. experience if no one will sponsor your first year.

## AI Literacy Is the New English Fluency

The bar for what counts as a "specialized skill" — the legal standard for H-1B eligibility — is shifting beneath developers' feet. Sanchit Vir Gogia, chief analyst at Greyhound Research, frames it as an existential question for the profession: "The engineer who only produces output grows easier to replace as the output grows easier to generate. The engineer who can validate it, secure it, situate it in a real business, and stand behind the result becomes harder to replace."

AI literacy is no longer a differentiator. It is table stakes. Jain compares it to knowing Excel in the pre-cloud era — a skill so basic that not having it disqualifies you, but having it confers no competitive advantage. For H-1B developers, this means the traditional résumé of languages, frameworks, and years of experience is increasingly insufficient. Companies want cloud infrastructure expertise, data engineering depth, security knowledge, and AI governance skills — the kind of judgment work that AI tools cannot yet replicate.

## The Wider Ripple

The structural shift is not confined to Silicon Valley hiring managers. Reuters reported this week that Standard Chartered plans to cut more than 7,000 jobs while ramping up AI investments, with some of the most affected roles sitting in back-office centers in Chennai and Bengaluru. The airline Southwest is expanding its Hyderabad technology center to 1,000 employees — but explicitly said it is "not intended to operate as a traditional back-office hub."

The message from both sides of the Pacific is converging: India remains critical to global technology operations, but the link between growth and headcount is breaking. More work does not mean more workers. And fewer workers means fewer visas.

## The Planning Horizon

For Indian H-1B holders currently employed, Gogia offers pointed advice: "A high-skilled worker has up to 60 days after a role ends, and the right to begin new employment the moment a valid portability petition is filed. The strategic error is treating that window as a safety net rather than a planning horizon."

In other words, do not wait for the layoff email to start thinking about your next role. The market has already decided that your current skill set, unaugmented by AI fluency and domain depth, is worth less than it was two years ago. The visa clock does not care about your learning curve."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
