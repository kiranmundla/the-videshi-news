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

article1_body = """The $100,000 H-1B fee is back. For now.

On June 8, a federal judge in Boston handed foreign workers and their employers what looked like a clean win, striking down the Trump administration's $100,000 charge on new H-1B petitions as an unauthorized tax. Four days later, the same judge took most of it back.

On June 12, U.S. District Judge Leo Sorokin temporarily stayed his own June 8 ruling after the government appealed to the First Circuit Court of Appeals. The practical effect: USCIS is once again permitted to demand the $100,000 fee on H-1B petitions that require consular notification — the very category that covers workers being hired from abroad — while the appeal plays out.

## What actually changed

The whiplash is real, but the legal mechanics are mundane. When a district court vacates a federal policy, the government can ask for that order to be paused so the status quo holds during appeal. Sorokin granted exactly that kind of pause, giving the First Circuit room to weigh in. The administration must file its formal stay request with the appellate court by June 18 for the freeze on his vacatur to stay in place.

The case is now docketed as *State of California, et al. v. Mullin, et al.*, No. 26-1699, in the First Circuit. Twenty Democratic state attorneys general are on the other side of it.

## Why the on-again-off-again matters to Indians

Indians are not a footnote in this fight. They are the fight. Workers born in India account for more than 70 percent of approved H-1B petitions in a typical year, which means any swing in the fee lands disproportionately on Indian engineers, doctors, and the companies that sponsor them.

The cruelest part is the timing. The fee — when it applies — hits petitions filed for workers outside the United States, or those approvable only through a consulate. That is precisely the situation for a newly hired Indian engineer waiting in Bengaluru or Hyderabad for a U.S. employer to file. A worker already inside the country on a change of status may be spared. The same job, the same person, can cost $100,000 more depending only on which side of the ocean the paperwork starts.

For employers, the lesson of the past week is that they cannot plan around a number that changes every few days. An HR team that paused filings after June 8, assuming the fee was dead, woke up on June 12 to find it alive again. Immigration lawyers are now advising clients to budget for the fee on any consular-notification H-1B petition until a court says otherwise — the safest assumption, even if it is the most expensive one.

## The bigger storm

This Boston case is only one of three. The U.S. Chamber of Commerce sued separately in Washington, D.C., and lost a bid for summary judgment, leaving the fee in effect there. A third suit, brought by religious groups and labor organizations, is pending in San Francisco. That sets up the possibility of conflicting rulings across three different appellate circuits — the kind of split that tends to end up at the Supreme Court.

Congress, meanwhile, is circling. Republican Rep. Mike Kennedy has introduced the PROTECT Act to write the $100,000 figure into statute, which would make the separation-of-powers argument that won in Boston irrelevant. If a fee is set by Congress rather than by proclamation, the "unauthorized tax" theory collapses.

## What to watch

The near-term signal is the June 18 deadline for the government's First Circuit filing. After that, the appellate court's decision on whether to maintain the stay will tell Indian workers and their sponsors whether the $100,000 number is a temporary scare or a durable cost of admission.

For now, the honest answer to "is the fee dead?" is: no. It was, for four days. Then it wasn't. Anyone making a six-figure career decision on the assumption that a single Boston ruling settled the matter is reading only the first half of the story."""

article2_body = """The Indian engineer who lands at a U.S. airport on an H-1B visa is sold a clean story: skilled worker, sponsoring employer, the American dream on a six-year clock. A new book argues the reality is often closer to indenture.

*Wild Wild East: Exiled Americans, Enslaved Indians and the Systemic Abuse of the H-1B Visa Programme*, by award-winning journalist Tanul Thakur, was reviewed by The Indian Express on June 13. The result of a multi-year investigation, it documents what Thakur calls a transnational machine of wage theft and labor manipulation stretched across the United States and India — and it puts a dollar figure on the harm: at least $121.48 million in wage violations over twenty years.

## The "body shop" at the center

The book's villain is not the H-1B program itself but the ecosystem that grew up around it. At the core are the consultancies known colloquially as "desi body shops" — staffing firms, often Indian-owned, that recruit workers in India, bring them over on H-1B visas, and then place them with American clients while skimming wages, withholding pay between projects, and binding workers with threats about their immigration status.

Thakur's reporting connects three actors: large outsourcing companies, these smaller body shops, and what he describes as compromised educational institutions that helped manufacture the paper qualifications the system needed. Through individual biographies, the book traces how a worker who arrives owing a recruiter, unsure of their own legal standing, and dependent on a single employer for their right to stay, becomes easy to exploit.

## Why this is a diaspora story, not a true-crime one

It would be easy to file this under crime reporting and move on. That would miss the point for Indian Americans, because the same structural features the book criticizes still shape millions of ordinary, lawful H-1B lives.

The vulnerability Thakur describes is not exotic. It is built into the visa's design. An H-1B worker's right to remain in the country is tied to a specific employer. Switching jobs requires a new petition. Falling out of status — even briefly, even through no fault of your own — can unravel years of green-card progress. That dependence is what a bad-faith body shop weaponizes, but it also quietly disciplines honest workers at honest companies, who think twice before reporting a problem or negotiating harder.

The book lands at a moment when the program is already under siege from the other direction. Washington has imposed a $100,000 fee on many new petitions, recast the lottery to favor higher wages, and expanded vetting. Indian workers are being told simultaneously that the program is too expensive to use and too abused to trust. Thakur's account complicates the abuse narrative without excusing the abusers: the fraud is real, he argues, but it thrives because the visa makes workers powerless, and the people who profit most from that powerlessness are rarely the ones the new fees punish.

## The uncomfortable mirror

For the Indian American professional class, *Wild Wild East* is an uncomfortable mirror. Many of its readers arrived through the same pipeline — perhaps through a reputable employer, perhaps through a body shop they would rather not name. The community's prosperity in the United States is genuinely a product of the H-1B program. So, the book insists, is a quieter history of exploitation that the success stories tend to crowd out.

## What it changes

A book does not reform a visa category. But Thakur's $121 million figure and his named cases add evidence to arguments immigration advocates have made for years: that the H-1B's employer-tied structure is the root problem, and that fixes aimed at "abuse" — higher fees, tougher lottery odds — punish workers without touching the leverage that makes abuse possible.

For Indian families weighing whether to send a child into the U.S. tech pipeline, the book is worth reading not as a warning to stay away, but as a manual for asking the right questions: Who is the real employer? Who holds the visa? And what happens to the paycheck between projects? The answers, Thakur shows, have not always been the ones the brochures promised."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The $100,000 H-1B Fee Was Dead for Four Days. A Boston Judge Just Brought It Back",
        "subheadline": "A district court vacated Trump's six-figure H-1B charge on June 8, then stayed its own ruling on June 12 as the government appealed. For Indian workers hired from abroad, the fee is live again.",
        "slug": make_slug("h1b-100k-fee-reinstated-sorokin-stay-first-circuit-appeal-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians make up more than 70% of H-1B approvals, and the reinstated $100,000 fee falls hardest on engineers and doctors hired from India through consular processing — the exact group the on-again-off-again ruling whipsaws most.",
        "tags": ["h1b", "uscis", "immigration", "100k-fee", "court-ruling", "first-circuit"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "WR Immigration (Wolfsdorf)", "url": "https://wolfsdorf.com/court-temporarily-reinstates-uscis-authority-to-collect-100000-h-1b-consular-processing-fee-pending-appeal/"},
            {"name": "Reuters", "url": "https://www.reuters.com/legal/government/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-08/"},
            {"name": "Associated Press / Audacy", "url": "https://www.audacy.com/news/national/federal-judge-strikes-down-trumps-100000-fee-on-new-h-1b-visas"},
        ]),
        "score_total": 86,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36869355/pexels-photo-36869355.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Classical courthouse columns, evoking the federal court battle over the H-1B fee",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A New Book Puts a $121 Million Price Tag on H-1B Exploitation — and It Names the 'Desi Body Shops'",
        "subheadline": "Tanul Thakur's 'Wild Wild East' traces two decades of wage theft across the US-India tech pipeline, arguing the visa's employer-tied design is what makes abuse possible.",
        "slug": make_slug("wild-wild-east-tanul-thakur-h1b-body-shops-wage-theft-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The H-1B's employer-tied structure that the book criticizes still quietly shapes millions of lawful Indian American lives, making this an uncomfortable mirror for a community whose prosperity rode the same pipeline.",
        "tags": ["h1b", "immigration", "labor", "book", "tanul-thakur", "body-shops"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/h-1b-visa-fraud-uncovering-the-exploitation-of-indian-tech-workers/"},
            {"name": "The Indian Express (review, June 13, 2026)", "url": "https://indianexpress.com/"},
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A software developer at work, representing the Indian tech workers at the center of the H-1B program",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article2_body
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art["body"].split())
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
