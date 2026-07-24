#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

body1 = """A lawsuit filed in Texas this month puts a number on something the Indian tech diaspora has whispered about for years: the price of staying. Rishikesh Raj Meesala, an H-1B contract worker, alleges he paid his employer nearly $100,000 to keep a Michigan job that came with the only thing that mattered — a path to a green card and, eventually, citizenship.

The complaint, brought by Banias Law, reads less like a wage dispute and more like a hostage negotiation. Meesala came to the United States on a student visa, earned a master's degree in 2023, and found work that led to H-1B sponsorship. After joining a Texas-based company run by Indian American executive Sai Jitender Kalagra, he was placed on the "bench" — industry shorthand for a worker who sits without an active client project, and therefore without billable hours.

What followed, according to the filing, was a slow squeeze. Meesala alleges he was required to fund his own salary while benched, and that company officials refused to hand over the pay stubs an H-1B holder needs to transfer to a new employer — unless he paid for them. When he pushed back, the lawsuit claims, the threats turned personal: report him to Immigration and Customs Enforcement, target his father in India, withhold his documents. The complaint frames these acts as labor trafficking, forced labor and unlawful document withholding. None of it has been proven in court, and the employer has not publicly responded.

## Why the bench is a trap

To understand why a skilled engineer would hand over six figures rather than walk away, you have to understand how tightly the H-1B binds a worker to a single employer. The visa is not yours; it belongs to the company that petitioned for you. Lose the job and the clock starts ticking — a 60-day grace period to find a new sponsor or leave the country. For someone with a pending green card application, often years deep into the EB-2 India backlog, leaving means going to the back of a line that already stretches past a decade.

That asymmetry of power is the whole story. A worker on the bench has no income but still needs to maintain status. An unscrupulous "body shop" — a staffing firm that warehouses H-1B workers and rents them to clients — can exploit that gap, demanding payment in exchange for keeping the petition alive. Immigration attorney Mithii Jaiswal, speaking to Financial Express Digital, said the allegations, if proven, point to a deeper structural flaw rather than a single bad actor.

## A diaspora policing itself

The detail that stings most for Indian Americans is that both the alleged victim and the accused are part of the same community. This is not a story of an Indian worker exploited by an American corporation. It is, as alleged, an Indian American executive accused of trapping a fellow Telugu-speaking immigrant. The community that built the H-1B success story is now litigating its underbelly in federal court.

That underbelly has always existed. The "body shop" model — common among smaller Indian-run IT staffing firms — has produced a steady drip of complaints over the past year: withheld wages, confiscated documents, immigration threats used as leverage. What is new is the willingness of workers to sue, and the size of the numbers they are putting on the record.

## What it means for someone on an H-1B today

For the roughly 70% of H-1B holders who are Indian, the practical lesson is unglamorous but urgent. Keep your own copies of every pay stub, I-797 approval notice and LCA. Know that no employer can lawfully demand you pay for your own petition or your own salary — those costs are the employer's legal obligation. And understand that an ICE threat from a boss is itself evidence of coercion, not a reason to comply.

The case also sharpens a larger anxiety. With the $100,000 consular fee lurching in and out of effect through the courts, and the EB-2 India queue frozen, the H-1B has rarely felt more precarious. That precarity is exactly what gives a predatory employer leverage. Meesala's lawsuit is one worker's attempt to take some of that leverage back — and a warning to thousands of others about how high the cost of the American dream can climb when your status is in someone else's hands."""

body2 = """The most telling immigration statistic of the week did not come from Washington. It came from a London law firm, which reported a steady rise since October 2025 in inquiries about the UK Global Talent Visa — overwhelmingly from Indian engineers, researchers and technology professionals currently living and working in the United States.

A Y & J Solicitors, which advises Global Talent applicants, says the majority of those reaching out are Indian nationals on H-1B visas: senior engineers and researchers in San Francisco and Seattle who have, in the firm's telling, simply done the math. "What I'm hearing from clients isn't panic. It's arithmetic," said chief executive Yash Dubal. "They've worked out that another decade of conditional residency in the US is no longer the better deal."

That sentence captures a quiet shift. For thirty years the calculation ran one way: endure the H-1B lottery, the employer dependence and the green card wait, because the United States was where the money and the opportunity were. The pull was strong enough to absorb almost any amount of bureaucratic pain. The pain has now risen to meet the pull.

## What the UK is selling

The appeal of the Global Talent Visa, launched in 2020, is precisely what the H-1B is not. It requires no employer sponsor, no minimum salary threshold and no Immigration Skills Charge. It is the worker's visa, not the company's — which means a layoff does not threaten your immigration status. Applicants endorsed as exceptional talent can settle in the UK after three years; those endorsed under exceptional promise after five.

Since August 2025, digital technology applicants have been assessed directly by the Home Office under a dedicated scheme, and the numbers are striking: a visa-stage approval rate of 99.2% across 2024 and 2025 for applicants who secured endorsement. The application fee is £766. Set that against a $100,000 H-1B consular fee that has been blocked, reinstated and appealed within the span of a single fortnight, and the contrast does the marketing on its own.

For Indian software engineers, the endorsement criteria are unusually legible. The Home Office accepts GitHub contribution graphs, accepted pull requests to major projects and documented leadership on repositories with significant traction as evidence of standing. For a generation that built its careers in open source, the UK is, as one adviser put it, "speaking our language now."

## Not the only door

Britain is not the only country reading the room. Canada continues to process work permits for roughly $155 in two weeks, a figure that looks almost satirical next to the H-1B's six-figure fee. Germany, Ireland, France and Portugal are courting the same 2026/2027 cohort of Indian students and professionals who once treated the United States as the default. The talent that America spent decades attracting is now being actively recruited away from it.

The crucial caveat is that interest is not the same as departure. History suggests most H-1B holders treat foreign permits as insurance policies rather than exit tickets — when Canada opened 10,000 open work permits to H-1B holders in 2023, the spots filled in 48 hours, but only a small fraction actually moved. US tech salaries remain markedly higher than British or Canadian ones, and that wage gap is a powerful anchor. Inquiries to a law firm are a leading indicator of anxiety, not a headcount of people boarding flights.

## Why it matters for the diaspora

Still, the direction of travel should worry anyone invested in the Indian American story, because the people writing these inquiries are not marginal. They are senior engineers and researchers — the high earners and future founders the H-1B program was supposed to retain. When the most employable workers start hedging, it tends to be an early signal, not a fringe one.

For an Indian professional weighing options, the practical takeaway is that the monopoly is over. The United States is no longer the only credible route to a stable, settled life in a high-income country, and the alternatives have lowered their friction at the exact moment America raised its own. Whether that produces a genuine exodus or merely a generation of well-hedged engineers depends on choices still being made in courtrooms and federal register notices. But the arithmetic Dubal describes is real, and more of his future clients are running it every week."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "An H-1B Worker Says He Paid His Boss $100,000 to Keep His Green Card Hopes Alive",
        "subheadline": "A Texas lawsuit alleges labor trafficking inside the Indian-run staffing world — and exposes how completely the visa binds a worker to a single employer.",
        "slug": make_slug("h1b-worker-paid-employer-100k-lawsuit-texas-labor-trafficking-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Around 70% of H-1B holders are Indian, and this case — where both the worker and the accused executive are Indian American — exposes the body-shop exploitation that thousands of benched contract workers quietly fear.",
        "tags": ["h1b", "lawsuit", "labor-trafficking", "body-shop", "immigration", "green-card"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "American Bazaar", "url": "https://americanbazaaronline.com/2026/06/15/indian-h-1b-worker-sues-texas-employer-482841/"},
            {"name": "TelecomLive / Financial Express", "url": "https://telecomlive.in/"},
            {"name": "Tupaki", "url": "https://english.tupaki.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6077326/pexels-photo-6077326.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A judge's gavel in a courtroom, where the labor-trafficking lawsuit will be litigated.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America's Best Indian Engineers Are Quietly Asking Britain for a Way Out",
        "subheadline": "A London law firm reports a steady rise in UK Global Talent Visa inquiries from US-based H-1B holders — no employer, no salary floor, settlement in three years.",
        "slug": make_slug("uk-global-talent-visa-indian-h1b-engineers-us-exodus-arithmetic"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The senior Indian engineers and researchers the H-1B was built to retain are now running the numbers on leaving — an early warning sign for the entire Indian American tech story.",
        "tags": ["h1b", "uk-global-talent-visa", "reverse-migration", "tech", "immigration", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "WCIA / EIN Presswire", "url": "https://www.wcia.com/business/press-releases/ein-presswire/"},
            {"name": "Gherson Solicitors", "url": "https://www.gherson.com/"},
            {"name": "Amir Ismail (RCIC)", "url": "https://amirismail.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14936005/pexels-photo-14936005.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The London skyline, destination for a rising number of US-based Indian tech professionals.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body2
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art['body'].split())
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
