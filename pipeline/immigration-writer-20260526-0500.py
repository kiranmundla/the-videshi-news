#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-26 05:00 PDT"""
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
        "headline": "Plan C — Apple, Google and the Corporate Scramble to Keep Their Best Engineers From Disappearing",
        "subheadline": "Silicon Valley's biggest firms are telling H-1B workers not to leave the country. Behind that advice sits a $900 billion retention crisis and a workforce where 80 percent of companies have immigrants running the show.",
        "slug": make_slug("plan-c-apple-google-h1b-corporate-retention-crisis"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian engineers are the largest H-1B demographic and the primary population affected by travel advisories, consular backlogs, and the corporate Plan C contingency playbook. For anyone on an H-1B weighing a trip home for a wedding or family emergency, this is the calculation that now governs their life.",
        "tags": ["h1b", "corporate-retention", "apple", "google", "silicon-valley", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "WebProNews / Fortune Workforce Innovation Summit", "url": "https://www.webpronews.com/trumps-visa-squeeze-leaves-tech-talent-stranded-and-forces-companies-to-rethink-retention/"},
            {"name": "Cato Institute (David Bier)", "url": "https://www.cato.org/"},
            {"name": "Erickson Immigration Group (Hiba Mona Anver)", "url": "https://www.ericksonimmigration.com/"},
            {"name": "Forbes (Stuart Anderson)", "url": "https://www.forbes.com/"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7652180/pexels-photo-7652180.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """Late last year, Apple and Google sent a message to their visa-holding employees that no corporate memo should ever need to contain: don't leave the country. The risk of not getting back in had become too high.

That advisory — quiet, internal, and devastating in its implications — captures where corporate America now stands on immigration. Not debating policy in Washington. Not lobbying for reform. Simply trying to prevent its own workforce from evaporating across international borders.

## The $900 Billion Problem Nobody Talks About

At Fortune's Workforce Innovation Summit this spring, the mood among HR executives was less optimistic brainstorming and more battlefield triage. Hiba Mona Anver, a partner at the Erickson Immigration Group, laid it out in terms that erased any remaining ambiguity.

"The issue now is whether or not there is the possibility that this individual will run into some sort of interruption in their ability to remain in the United States," Anver told attendees. She described cases where policy shifts stranded employees in India for months, separated from families, with no clear return date. "Many have still not been able to make their way back to the United States, and this happened barely six months ago."

The numbers behind the anxiety are staggering. U.S. companies spent nearly $900 billion managing employee turnover in 2023. High-skilled foreign workers — the exact category the H-1B was designed to serve — prove twice as likely to leave as their domestic counterparts. Once gone, they tend to stay gone.

David Bier of the Cato Institute distilled the shift in a single sentence: "Talent retention is really the new recruitment." His data point landed harder than any policy paper: 80 percent of companies have an immigrant or H-1B holder serving as CEO, CTO, or VP of engineering. More than half of America's billion-dollar startups count an immigrant among their founders.

## Plan A Is Dead. Plan B Is Dying.

The old corporate playbook was straightforward. Plan A: file renewals on time. Plan B: use premium processing if there's a delay. That framework assumed a system that functioned, however slowly, within predictable parameters.

Those parameters no longer exist. New social media vetting requirements force applicants to make their accounts public. Processing times have stretched well past premium deadlines — sometimes without refunds. Requests for evidence now arrive on already-approved labor condition applications, probing education, experience, and supervisory duties in ways that echo regulations courts rejected in 2020.

Anver's prescription was blunt: companies need Plan C. Not for delays. Not for complications. For the genuine possibility that an employee simply cannot return to the United States after traveling abroad.

## The Wage Floor That Changes Everything

The Department of Labor's proposed prevailing wage increases add another layer of pressure. The rules, floated in March, would lift required H-1B wages by 21 to 33 percent depending on experience level. Bloomberg reported the specific figures: $162,000 annually for an entry-level software engineer in San Francisco. $132,000 in New York. $113,000 in Dallas.

For Indian professionals — who received 71 percent of H-1B approvals in the most recent fiscal year — this isn't an abstract policy debate. It's a direct calculation that determines whether their employer can afford to keep sponsoring them. Small and mid-size companies that rely on H-1B talent face the starkest math: sponsor at the new rates, offshore the work, or simply go without.

## The Hyderabad Trap

The human cost plays out in consulate waiting rooms across India. One mechanical engineering consultant described a December visa appointment in Hyderabad that slid to March, then later still. His work with a Detroit automotive supplier — a project dependent on his physical presence — hung in limbo for months.

Stuart Anderson, writing for Forbes, expects further limits on H-1B qualifications, curbs on work at client sites, and tighter rules for international students. That last category matters enormously: international students fill 75 to 80 percent of full-time graduate spots in AI-related computer science programs at U.S. universities. Proposed changes to Optional Practical Training and STEM extensions could discourage them from staying after graduation.

Immigration attorney Jonathan Grode of Green & Spiegel captured the cumulative effect: "The constant barrage of negative news and regulation on the H-1B front is having an effect." Top talent, he said, now looks to Germany, Canada, and other countries racing to attract skilled workers.

## What This Means for Indian Professionals

For the roughly 600,000 Indians in the H-1B queue and the tens of thousands more entering the workforce each year, the corporate Plan C era introduces a brutal new variable. Your employer's willingness to sponsor you is no longer the only question. Whether you can physically remain in the same country as your job — and your family — is now genuinely uncertain.

The companies telling their workers not to travel aren't being paranoid. They're reading the same policy memos, the same processing timelines, the same consular backlog data that every Indian H-1B holder refreshes on their phone at 2 a.m. The difference is that Apple and Google can afford Plan C. The question is whether the system leaves anyone else with a plan at all."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Washington Wanted to Stop Outsourcing. Its Immigration Crackdown Is Sending 50,000 Tech Jobs to Bangalore.",
        "subheadline": "A quarter of major tech companies are expanding India teams in direct response to H-1B restrictions. The $100,000 visa fee and 30 percent wage hike have made offshoring the rational economic choice — exactly the outcome the policy was supposed to prevent.",
        "slug": make_slug("h1b-crackdown-offshoring-50000-jobs-bangalore-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For Indians in the US, the offshoring wave creates a paradox: more jobs in India, but a devalued premium for the American career path they sacrificed years to build. For those considering the move to America, the math has shifted — Bangalore now competes not just on cost but on opportunity.",
        "tags": ["h1b", "offshoring", "india", "tech-jobs", "bangalore", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "WhispersInTheCorridors", "url": "https://www.whispersinthecorridors.com/detail/153085-Big+tech+firms+shifting+jobs+from+US+to+India.html"},
            {"name": "WhispersInTheCorridors (Offshoring Prediction)", "url": "https://www.whispersinthecorridors.com/detail/145940-%2020perentage%20more%20offshoring%20to%20India%20by%20MNCs%20likely.html"},
            {"name": "WebProNews / Fortune", "url": "https://www.webpronews.com/trumps-visa-squeeze-leaves-tech-talent-stranded-and-forces-companies-to-rethink-retention/"},
            {"name": "Bloomberg (DOL Wage Data)", "url": "https://www.bloomberg.com/"},
            {"name": "Cato Institute", "url": "https://www.cato.org/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1409469/pexels-photo-1409469.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """For two decades, American politicians ran on a simple promise: bring the jobs home. Stop the outsourcing. Keep the work in the United States. The H-1B visa program, whatever its flaws, was part of that bargain — let skilled workers come to America, and the work stays on American soil.

Washington just broke that deal. And the jobs are moving to Bangalore anyway.

## The Numbers Don't Lie

Industry tracking data from early 2026 shows a pronounced shift: 25 percent of major tech companies — including Google, Amazon, Microsoft, Uber, and eBay — are actively expanding engineering teams in India. Another 20 percent are creating entirely new roles that didn't previously exist in their Indian operations.

The projected scale is significant. Analysts estimate 50,000 IT jobs will shift from the United States to India by the end of 2026, driven not by the traditional cost arbitrage that fueled the outsourcing era of the 2000s, but by a straightforward regulatory calculation: it is now cheaper and less risky to hire an engineer in Hyderabad than to sponsor one in Houston.

The arithmetic is hard to argue with. A new H-1B petition carries a $100,000 surcharge fee. The Department of Labor wants to raise prevailing wages by 21 to 33 percent, pushing entry-level software engineering salaries to $162,000 in San Francisco and $132,000 in New York. Add legal fees, premium processing costs, the risk of denial, and the possibility that your employee gets stuck abroad at a consulate for months — and the business case for keeping the work in the US collapses for all but the most essential roles.

## The Accenture Model Goes Mainstream

Consulting giants like Accenture pioneered the India delivery model decades ago. What's changed is that product companies — firms that historically insisted on co-located engineering teams — are now following the same playbook.

The shift isn't purely about saving money. It's about operational continuity. When Apple and Google are telling visa-holding employees not to travel abroad because they might not get back in, the message to every CFO is clear: your US-based workforce has become a liability if it depends on immigration status.

Companies respond rationally. If a senior engineer in Mountain View costs $250,000 fully loaded, carries visa risk, and might disappear into a consular backlog for six months, while the same engineer in Bangalore costs $80,000 with zero immigration overhead and no travel restrictions — the spreadsheet writes itself.

## The Irony Washington Cannot See

This is the outcome that anti-outsourcing rhetoric was supposed to prevent. The entire political case against H-1B reform rested on protecting American jobs from foreign competition. Instead, by making it prohibitively expensive and bureaucratically treacherous to employ foreign talent on American soil, the policy is doing exactly what its architects claimed to oppose: moving the work overseas.

David Bier of the Cato Institute has tracked this dynamic closely. Foreign-born workers account for nearly 20 percent of the U.S. civilian workforce. Their economic footprint reached $1.7 trillion in activity in 2023. More than half of America's billion-dollar startups were co-founded by immigrants. When you make it harder for those people to work in the US, the work follows them home.

The H-1B Modernization Rule, the $100,000 fee, the DOL wage increases, the social media vetting, the consular backlogs, the USCIS adjustment-of-status memo — each policy was presented as a standalone correction. Taken together, they form an escalating series of incentives for companies to do exactly what politicians spent 20 years telling them not to do.

## What Bangalore Gets

India's tech sector is the obvious beneficiary. The country already employs roughly 5 million IT workers. Adding 50,000 roles from multinational operations represents a meaningful injection of high-value positions — not the call center and back-office work that defined the first outsourcing wave, but product engineering, machine learning, and infrastructure work that commands premium salaries even by Indian standards.

Bangalore, Hyderabad, and Pune are seeing the sharpest growth. Companies aren't just backfilling existing positions. They're building new centers of gravity — teams with enough critical mass to operate autonomously rather than serving as satellite offices dependent on US headquarters.

For India's tech ecosystem, the timing is almost too convenient. The country has invested heavily in engineering education, startup infrastructure, and digital connectivity. The returning tide of work from America arrives into a market that's genuinely ready to absorb it.

## The Diaspora Calculation Shifts

For Indian professionals already in the United States, the offshoring wave creates an uncomfortable paradox. The American dream premium — the salary differential, the career trajectory, the quality of life — is narrowing. Not because India has caught up in absolute terms, but because the cost of maintaining an American career has skyrocketed.

When your H-1B renewal costs $100,000, your green card is 13 years away, your spouse can't work, and your employer is building a parallel team in Bangalore that does exactly what you do — the calculation changes. Some engineers are making the move voluntarily. Others are being nudged by employers who frame it as "an exciting opportunity to lead our India operations" rather than what it actually is: a hedge against the visa system.

For prospective immigrants still in India weighing the American path, the signal is even clearer. The jobs are coming to you. The salary gap is shrinking. The immigration gauntlet is lengthening. The question is no longer whether America is worth it — it's whether the math still works.

## The Policy Feedback Loop Nobody Wants

Here's where it gets genuinely strange. As more companies shift work to India, the domestic political argument for restricting immigration strengthens. Fewer H-1B workers in the US means fewer visible foreign workers "taking American jobs." Politicians can point to declining visa numbers as proof their policies worked.

But the jobs didn't go to Americans. They went to Indians — in India. The same work, done by the same talent pool, just on the other side of a border that Washington spent billions trying to make irrelevant in the age of globalization.

Fifty thousand jobs this year. The question for 2027 is whether the number doubles — and whether anyone in Washington notices the difference between keeping jobs in America and simply making them invisible."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
