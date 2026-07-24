#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-28 08:00 PT"""
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


# ─────────────────────────────────────────────────────────────
# ARTICLE 1: Vishal Sikka / Hang Ten Systems
# ─────────────────────────────────────────────────────────────

art1_body = """Vishal Sikka spent twelve years building SAP's technology platform, then four turbulent ones trying to drag Infosys into the future. Now 59, the Stanford-trained computer scientist has decided to skip the reformation and build the replacement.

His new startup, Hang Ten Systems, emerged from stealth this week with $32 million in seed funding — one of the largest seed rounds ever raised by an Indian-origin founder — and a pitch that should unsettle the boardrooms of TCS, Infosys, and Wipro: artificial intelligence can now do what their armies of engineers do, faster and cheaper, and the gap is widening every day.

"Every single enterprise will be transformed by AI," Sikka said in a statement accompanying the launch. "A few are already reaping massive benefits, building in days what used to take years. But most are stuck at the starting line, or worse."

## The thesis that bites back

Traditional IT services companies — the Infosyses and TCSes of the world — scale linearly. More work means more engineers. More engineers mean more managers. The model has generated a $283 billion global industry and employed millions of Indian professionals, but Sikka is betting that its economics have been broken by generative AI.

Hang Ten's model uses agentic code generation — autonomous AI systems that write, modify, and maintain enterprise software — paired with a reusable skills library and domain expertise in finance, HR, and product development. The company claims it can deliver what a traditional services engagement would, at a fraction of the cost and time.

Mayfield led the seed round, with Aramco Ventures contributing a strategic investment. Yahoo co-founder Jerry Yang has joined Hang Ten's board, and the founding team is a reunion of Sikka's previous ventures: CTO Navin Budhiraja, chief design officer Sanjay Rajagopalan, and SVP of forward deployed engineering Tao Liu all worked alongside him at SAP, Infosys, or VianAI, his previous AI startup.

## Already shipping, not just pitching

Unlike most seed-stage companies, Hang Ten already has paying enterprise clients. Siemens Gamesa Renewable Energy and healthcare giant Fresenius are among the first customers, with Vinod Philip, CEO of Siemens Gamesa, calling the startup a source of "sound trusted guidance on AI."

That Hang Ten launched only a month ago and is already delivering projects speaks to both Sikka's network and the urgency enterprises feel to adopt AI. "Traditional services scale linearly with headcount," Mayfield managing partner Navin Chaddha told TechCrunch. "Hang Ten is built so its leverage grows with every project."

## Why NRIs should pay attention

For the hundreds of thousands of Indian tech workers employed by IT services firms — whether at TCS's offices in Hyderabad or Infosys's delivery centres in Pune — Hang Ten represents the most articulate version of their industry's existential threat. It is not some abstract AI consultancy; it is a company founded by the man who ran Infosys, staffed by people who worked at Infosys, building tools designed to replace the work Infosys does.

The timing is pointed. Infosys shares have fallen more than 35 per cent this year, according to LiveMint. Nasscom's own projections suggest AI could create a $400 billion market for Indian IT — but the companies' old delivery models will not get them there. TCS has already shed thousands of employees in a restructuring that Jefferies analysts have linked directly to AI-driven productivity demands.

For Indian engineers in the United States, the implications cut both ways. The same AI tools that threaten offshore delivery centres could also compress the number of engineers companies need onshore. But for those who can work *with* these tools rather than be replaced by them, the opportunity is considerable. Sikka is hiring across delivery, engineering, sales, and management, with plans to expand to multiple global locations.

The irony is hard to miss: the man whom Narayana Murthy pushed out of Infosys in 2017 may now be building the thing that makes Infosys's traditional model irrelevant. In his LinkedIn announcement, Sikka borrowed the surfing metaphor that gave his company its name: "When there are big waves around, it is time to surf. Not just to surf, but to hang ten."

The wave, it seems, is already here."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Man Who Ran Infosys Now Wants to Make It Obsolete",
    "subheadline": "Vishal Sikka's new AI startup Hang Ten Systems raised $32 million to replace traditional IT services with agentic code generation — a direct shot at the $283 billion outsourcing industry that made him famous.",
    "slug": make_slug("vishal-sikka-hang-ten-ai-startup-infosys-threat"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "A former Infosys CEO is building an AI company that could displace the IT services model employing hundreds of thousands of Indian tech workers in the US and India — a direct threat to the careers built on the H-1B-to-TCS pipeline.",
    "tags": ["ai", "indian-tech", "silicon-valley", "startup", "it-services", "infosys", "vishal-sikka"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Mitrade / TechCrunch", "url": "https://www.mitrade.com/insights/news/live-news/article-3-1844931-20260626"},
        {"name": "The Mainstream", "url": "https://themainstream.co.in/hang-ten-systems-secures-32-million-seed-funding/"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/from-cred-to-square-yards-indian-startups-raised-1-1-bn-this-week/"},
        {"name": "BitcoinWorld / CoinDesk", "url": "https://bitcoinworld.co.in/former-infosys-ceo-vishal-sikka-launches-ai-native-it-services-startup/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/VishalSikkaSapphireOrlando2010.jpg/3840px-VishalSikkaSapphireOrlando2010.jpg",
    "image_caption": "Vishal Sikka, former Infosys CEO and founder of Hang Ten Systems, at a technology conference",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}


# ─────────────────────────────────────────────────────────────
# ARTICLE 2: H-1B $100K Fee Legal Battle
# ─────────────────────────────────────────────────────────────

art2_body = """The most expensive visa fee in American history is alive, dead, and alive again — all within the same month.

On June 8, US District Judge Leo Sorokin ruled that the Trump administration's $100,000 H-1B filing fee amounted to an unauthorised tax and exceeded the government's legal authority. For a few days, tech companies and the immigration attorneys who serve them exhaled. Then, on June 12, the same judge issued an administrative stay of his own ruling, allowing the fee to remain enforceable while the government appeals to the First Circuit Court of Appeals.

The result is policy limbo. Companies that sponsor H-1B workers — from Google and Microsoft to Infosys and TCS — must continue budgeting for a cost that a federal judge has declared illegal but that the government insists is valid. The Department of Homeland Security has argued that the district court got it wrong and asked the appeals court to maintain the stay throughout the appellate process.

## Why this is a tech industry problem, not just an immigration story

The $100,000 fee does not apply to every H-1B petition, but its chilling effect extends to every employer that relies on skilled foreign labour. Indian professionals account for roughly 72 per cent of all H-1B visas issued, and the fee has already reshaped workforce planning at companies across sectors.

Tech companies, which consume the bulk of H-1B allocations, face a simple calculus: at $100,000 per petition on top of existing legal and processing fees, the cost of hiring a foreign engineer can approach a full year's salary. For startups without deep pockets, that calculation increasingly favours hiring domestically — or not hiring at all.

The Indian IT services giants face an even sharper pressure. TCS, Infosys, and Wipro use H-1B and L-1 visas to rotate employees between India and client sites in the United States. A six-figure per-petition fee would fundamentally alter the economics of onshore delivery, potentially accelerating the shift toward remote work from India — which, paradoxically, is what the fee's proponents in Washington say they want.

## USCIS is not waiting for the courts

While the legal battle plays out, US Citizenship and Immigration Services has not paused enforcement. USCIS continues issuing Requests for Evidence on H-1B filings and fee compliance, according to Hindustan Times. Immigration attorneys say employers should prepare for additional scrutiny during the application process, regardless of the appeal's outcome.

The American Association of Physicians of Indian Origin has called the court's original ruling a "critical victory," noting that the fee would disproportionately impact rural hospitals and safety-net institutions where International Medical Graduates — many of them Indian — fill critical vacancies. "This is not a political victory — it is a healthcare victory," said AAPI president Dr Amit Chakrabarty.

## The parallel tracks NRIs are navigating

For Indian professionals already in the US on H-1B visas, the fee uncertainty adds another layer to an already precarious immigration landscape. More than 100,000 tech workers have lost jobs globally this year, and roughly 25,000 of those are estimated to be H-1B holders who face a 60-day grace period to find new sponsorship or leave the country.

Meanwhile, India's own tech job market has hit a 28-month low, with active openings falling to 93,000 in June — a 14 per cent drop from the previous month. The return migration of 7,300 tech workers in the first half of 2026 is expected to outpace outbound movement before year's end.

Companies are now evaluating alternative immigration pathways: cap-exempt H-1B programmes through universities and research institutions, L-1 intracompany transfers, O-1 visas for individuals with extraordinary ability, and expanded remote arrangements. Some are shifting headcount to Canada, the UK, and Singapore, where skilled-worker visa regimes are more predictable.

The First Circuit's decision will not arrive for months. In the meantime, the $100,000 question hangs over every tech hiring conversation that crosses a border — and for an industry whose workforce is deeply, structurally Indian, that is nearly all of them."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "A $100,000 Price Tag on Every H-1B Hire. A Judge Said No. The Government Said Wait.",
    "subheadline": "The most controversial visa fee in US history is stuck in legal limbo, leaving tech companies and hundreds of thousands of Indian professionals planning for a cost nobody can confirm will stick.",
    "slug": make_slug("h1b-100k-fee-court-battle-tech-industry-legal-limbo"),
    "category": "technology",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals hold 72% of H-1B visas, and the $100,000 fee directly impacts every tech worker's sponsorship economics — from startups deciding whether to hire internationally to IT services firms rethinking their US delivery models.",
    "tags": ["h-1b", "immigration", "tech-industry", "indian-tech", "silicon-valley", "visa"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "AviationA2Z", "url": "https://aviationa2z.com/index.php/2026/06/26/h-1b-visa-fee-uncertainty-continues-after-court-stay-on-trumps-100k-rule/"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/j5yho0cyttb9/"},
        {"name": "The Indian EYE", "url": "https://theindianeye.com/aapi-applauds-court-ruling-blocking-100000-h1b-physician-visa-requirement/"},
        {"name": "AINvest", "url": "https://ainvest.com/post/tech-talent-faces-challenges-finding-jobs-in-india-upon-h-1b-return-20260626/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in New York, where H-1B visa petitions are processed",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}


# ─────────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
