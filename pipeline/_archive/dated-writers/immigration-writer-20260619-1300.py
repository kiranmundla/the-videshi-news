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

article1_body = """The H-1B visa has survived four decades of political assault largely because of one quiet feature: dual intent. A worker can hold a temporary visa and pursue a green card at the same time, without the contradiction being held against them. For Indian engineers stuck in a green-card queue that now runs past most working lifetimes, that single legal fiction is the thread the entire American plan hangs on.

A bill introduced in the House on June 4 would cut it.

Republican Congressman Chip Roy of Texas calls his proposal the American White-Collar Worker Jobs Act. It does not abolish the H-1B outright — that distinction matters less than it sounds. Instead it requires every H-1B applicant to demonstrate that they maintain a residence abroad and have no intention of abandoning it. In plain terms, the worker would have to prove they plan to leave. Applying for permanent residency while on an H-1B would no longer be a parallel track; it would be evidence against you.

## What the bill actually does

Three changes sit at the center of Roy's text. First, the reversal of dual intent described above. Second, a mandated labor-market test: employers would have to show a good-faith effort to hire American workers before petitioning for a foreign one, with the Department of Labor and USCIS jointly enforcing it. Third, the bill scraps Optional Practical Training, the post-graduation work authorization that lets international students stay and work after a U.S. degree.

"For its nearly forty-year history, the H-1B visa has been abused, allowing employers to routinely sideline American STEM workers in favour of cheap foreign labour," Roy said, describing the program as a lottery-based pipeline he wants to replace with one that "prioritises merit, enforces real wage standards, and puts America's white-collar workers first."

The bill is backed by US Tech Workers, the Immigration Accountability Project, and the Federation for American Immigration Reform — restrictionist groups whose priorities now align closely with the administration's. It is also not alone. A separate measure, the Fairness for High-Skilled Americans Act, would eliminate OPT entirely and has collected more than two dozen Republican co-sponsors since March 2025.

## Why this lands hardest on Indians

The arithmetic is unforgiving. Indians receive roughly 71% of approved H-1B petitions and dominate the employment-based green-card backlog under EB-2 and EB-3, where per-country caps have stretched waits into the decades. The entire premise of staying on an H-1B for years is that the green card is coming, eventually. Strip dual intent and that premise becomes legally hostile: a worker openly waiting for a green card is, by the new standard, admitting they intend to abandon the foreign residence the visa now requires them to keep.

OPT abolition compounds it from the other end. For a generation of Indian students, the sequence has been degree, then OPT or STEM OPT, then H-1B, then the long green-card wait. OPT is the on-ramp. Closing it does not just affect graduates already here — it changes the calculus for every Indian family weighing whether a U.S. master's degree is still worth the tuition if the work authorization at the end is gone.

## How worried should you be

Less than the headlines suggest, for now. Roy's bill has been introduced, not passed. It sits with the House Judiciary Committee alongside a graveyard of similar proposals that never reached a floor vote. Introducing a bill is cheap; moving one through both chambers is not, and the tech lobby that defeated earlier restrictionist efforts has not vanished.

But the direction of travel is the real signal. Between the now-stayed $100,000 H-1B fee, the wage-weighted lottery replacing the random draw for FY2027, intensified social-media vetting of student visas, and ICE's OPT fraud investigations, the legislative push and the executive push are pointing the same way. Roy's bill may not pass, but it tells you what a passable version would look like.

For Indian professionals, the practical takeaway is not panic but documentation. Workers deep in the green-card queue should keep their approved I-140 priority dates and any portability protections airtight, because those are the protections a future law would have to explicitly override. Students should treat OPT as a benefit that exists today and may not exist for the next cohort. The dual-intent thread has held for forty years. It is worth knowing who is now pulling at it."""

article2_body = """When ICE's acting director Todd Lyons stepped to a podium in May and called Optional Practical Training "a magnet for fraud," he was not announcing a new rule. He was announcing a hunt. Investigators, he said, had identified more than 10,000 foreign students working for "highly suspect" employers — and that figure came from only the top 25 OPT employers. "This is only the tip of the iceberg," Lyons said. For the hundreds of thousands of Indian graduates who use OPT as the bridge between a U.S. degree and an H-1B, the words that should worry them most were the last ones: "more actions are forthcoming."

OPT lets international students on F-1 visas work in the United States for a year after graduation, with a two-year extension for STEM degrees. It is not a small program. In 2024-25, close to 300,000 international graduates participated, and Indians are among the largest national groups in it. For most, it is the single most important year of their American life — the window in which they convert a student visa into a career and, they hope, a path to staying.

## What investigators say they found

The picture ICE painted was of organized abuse, not paperwork sloppiness. Homeland Security Investigations officers described empty buildings with locked doors listed as worksites for hundreds of students. Residential addresses recorded as employment sites with no employees present. Clusters of shell companies sharing websites and management while denying any relationship to one another. In one North Texas case, an employer reported three OPT employees while SEVIS records showed more than 500.

HSI said it had visited problematic worksite employers in Virginia, Texas, Georgia, Illinois, New York, New Jersey, North Carolina and Florida — a geography that maps closely onto where Indian IT staffing and consulting firms cluster. "We are uncovering evidence of organized fraud that spans national and international borders," Lyons said. "This is not accidental. It is deliberate, coordinated, and criminal."

## Why honest students are exposed too

Here is the uncomfortable part for the diaspora: most companies that hire F-1 students do none of this, and the students themselves are usually the last to know whether their employer is clean. A graduate accepts an offer, files an I-983 training plan, and starts work. If that employer turns out to be a shell, the student's name now sits in the same federal records as a flagged entity — through no fault of their own.

The collateral consequences are already visible. Immigration lawyers report more frequent site visits, sharper requests for evidence on subsequent H-1B and I-140 petitions, and reputational exposure for anyone whose employer lands on an investigator's list. A clean record is no longer enough if the company attached to it is dirty.

## The political backdrop

The crackdown does not exist in isolation. It runs alongside a legislative push to kill OPT outright — Rep. Chip Roy's American White-Collar Worker Jobs Act and the earlier Fairness for High-Skilled Americans Act both target the program — and a broader administration argument that OPT is an "uncontrolled guest worker pipeline" Congress never authorized. The fraud findings give that argument fuel. Every shell company HSI uncovers becomes a talking point for ending the program for everyone.

## What Indian students and graduates should do now

The defensive moves are concrete. First, verify your employer is real before accepting OPT or STEM OPT work — a physical office, a verifiable supervisor, a business that exists beyond a website. Second, keep your I-983 training plan current: if the worksite, supervisor, or training description on file does not match what you actually do, that gap is the first thing an investigator finds. Third, make sure your supervisor knows they are responsible for the training the form describes, because on a site visit their answers are checked against your paperwork.

OPT has long been treated by some employers as a compliance afterthought. The cost of that treatment is now rising fast, and the people who pay it first are not the firms running the schemes — they are the students whose names appear in the same files. For Indian graduates banking their American future on a single post-study year, the safest assumption is that someone is now checking."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Texas Bill Wants to End the One H-1B Feature Indians Quietly Depend On",
        "subheadline": "Chip Roy's American White-Collar Worker Jobs Act would scrap dual intent and abolish OPT. Even if it never passes, it shows where the next squeeze is aimed.",
        "slug": make_slug("chip-roy-white-collar-worker-jobs-act-dual-intent-opt-h1b-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold about 71% of H-1B approvals and dominate the EB-2/EB-3 green-card backlog, so a bill ending dual intent and OPT strikes directly at the legal mechanics that let Indian workers wait out the queue.",
        "tags": ["h1b", "opt", "dual-intent", "chip-roy", "green-card", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/us-bill-eyes-major-h-1b-overhaul-seeks-to-end-green-card-track"},
            {"name": "Swadesi (PTI)", "url": "https://www.swadesi.com/news/us-congress-bill-seeks-to-end-h-1b-green-card-pathway/"},
            {"name": "Congress.gov — H.R.2315", "url": "https://www.congress.gov/bill/119th-congress/house-bill/2315/text"},
            {"name": "The Times of India", "url": "https://timesofindia.indiatimes.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Chip_Roy_118th_Congress.jpg",
        "image_caption": "Rep. Chip Roy of Texas, who introduced the American White-Collar Worker Jobs Act in June 2026",
        "image_attribution": "Wikimedia Commons",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "ICE Says OPT Is a 'Magnet for Fraud.' Indian Graduates Are the Ones Exposed",
        "subheadline": "Investigators flagged 10,000 students at suspect employers and promised 'more actions are forthcoming' — and a clean record is no longer enough if your company isn't.",
        "slug": make_slug("ice-opt-fraud-crackdown-10000-students-suspect-employers-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are among the largest groups using OPT and STEM OPT as the bridge from a US degree to an H-1B, so an enforcement sweep that taints students by association with shell-company employers threatens careers built entirely on that post-study year.",
        "tags": ["opt", "stem-opt", "f1-visa", "ice", "students", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "ICEF Monitor", "url": "https://monitor.icef.com/2026/05/us-immigration-officials-allege-opt-is-being-widely-abused/"},
            {"name": "Fox News", "url": "https://www.foxnews.com/politics/ice-drops-uncontrolled-fraud-bombshell-involving-thousands-foreign-students"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An open passport with travel and entry stamps, symbolizing the F-1 student visa and OPT work-authorization process",
        "image_attribution": "Pexels",
        "body": article2_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']} — {wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
