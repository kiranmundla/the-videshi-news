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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Shrey Parikh Spelled 32 Words in 90 Seconds. The Diaspora's Spelling Bee Dynasty Now Stretches to 31 of 37 Champions.",
        "subheadline": "A 14-year-old from Rancho Cucamonga won the 101st Scripps National Spelling Bee with a record-breaking spell-off, continuing a run of Indian-origin dominance that began with Nupur Lala in 1999.",
        "slug": make_slug("shrey-parikh-scripps-spelling-bee-2026-indian-american-dynasty"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian Americans have won 31 of the last 37 Scripps National Spelling Bee titles — an extraordinary cultural phenomenon rooted in diaspora parenting, community coaching networks, and the immigrant drive toward academic excellence that defines the Indian American experience.",
        "tags": ["nri", "diaspora", "spelling-bee", "indian-american", "education", "shrey-parikh"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com/2026/05/29/shrey-parikh-is-the-2026-scripps-national-spelling-bee-champion/"},
            {"name": "Audacy", "url": "https://www.audacy.com/sports/shrey-parikh-bounces-back-battles-nerves-and-dominates-spell-off-to-win-the-national-spelling-bee"},
            {"name": "LatestLY", "url": "https://www.latestly.com/world/us/indian-american-teen-shrey-parikh-wins-scripps-national-spelling-bee-2026-with-record-32-words-watch-video-6683207.html"},
            {"name": "TV Insider", "url": "https://www.tvinsider.com/1214847/meet-shrey-parikh-winner-of-the-2026-scripps-national-spelling-bee-after-rare-spell-off/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Scripps_National_Spelling_Bee_%2855301276503%29.jpg/1280px-Scripps_National_Spelling_Bee_%2855301276503%29.jpg",
        "body": """Shrey Parikh was shaking. He has said so himself. In a hall in Washington where children routinely face words most adults cannot pronounce, the 14-year-old from Rancho Cucamonga, California, was staring at the culmination of a six-year spelling career that had taken him from a tied 89th finish in 2022 to third place in 2024 to something very nearly derailed altogether in 2025, when a virus knocked him out at his own school bee on the word "calipers."

That detour makes the ending harder to script. On May 28, Parikh correctly spelled 32 words in 90 seconds during the Scripps National Spelling Bee's third-ever spell-off, setting a new record and clinching the 101st championship with the word "bromocriptine" — a polypeptide alkaloid that mimics the activity of dopamine. The dopamine, one suspects, was already flowing.

## The Diaspora's Longest Winning Streak

Parikh becomes the 31st champion of Indian heritage in the last 37 editions of the Bee, a streak that began when Nupur Lala won in 1999 and has become one of the most statistically remarkable phenomena in American competitive academics. Indian-origin children now account for roughly 84 percent of recent champions, a figure that bears no relation to the community's share of the U.S. population — approximately 1.5 percent.

The numbers invite easy narratives about "tiger parenting" or cultural obsession with rote memorization. The reality is more layered. Parikh's coach, Sohum Sukhatankar, was himself a co-champion in 2019. Sam Evans, another coach, has worked with each of the past three champions. Vijaya Ganesh rounds out the coaching team. What has emerged is not a stereotype but an infrastructure — a self-reinforcing ecosystem of coaching, online bees, study guides, and community networks that operates almost entirely within the diaspora.

"Whenever I would quiz him, he would take notice of his missed words. He'd analyze every missed word he had, try to figure out why he missed it," Sukhatankar told reporters. "All the time I coached him, he'd never miss a word twice."

## The Long Road Through School Bees and Setbacks

Parikh, whose family immigrated from Telangana, attends Day Creek Intermediate School in San Bernardino County. He plays snare drum, bass drum, timpani, triangle, glockenspiel, and marimba in his school band. He recently qualified for the California state Mathcounts competition. He visits India frequently to spend time with his grandparents.

None of that prevented the low point. In 2025, woozy with fever, he blanked at his school spelling bee — a competition any speller of his caliber would consider trivial — and missed his regional bee entirely. For months, he was out of competition.

"At my school bee last year, I was really dejected and just very upset," Parikh said. "It didn't even sink in until the next day. I had a really tough time, but I'm glad I was able to bounce back."

He rededicated himself, winning online bees against many of the same competitors he faced in Washington. Evans noted that Parikh's work ethic stood apart. "I've really never seen someone put this much effort into spelling bees, into learning everything that he possibly can," Evans said. "Shrey is relentless."

## The Spell-Off and the Finish

The final narrowed from nine semifinalists to four: Parikh, Kushi Gottimukkala of North Carolina, Sarv Dharavane of Georgia, and Ishaan Gupta of New Jersey. One by one, the field contracted until Parikh and Gupta — both Indian American — stood alone.

After words like "cywyddau" and "fais-dodo," judges triggered the spell-off, giving each contestant 90 seconds and a buzzer. Parikh spelled 32 words correctly. Gupta managed 25 — a formidable total by any measure, but not enough.

Parikh walked away with $52,500 in cash, a custom Rookwood Pottery trophy, and the distinction of having produced the most dominant spell-off performance in the format's short history.

## What the Streak Actually Means

"When it comes to competition, he goes all the way," his father, Guarav Parikh, told reporters.

The Indian American spelling bee pipeline is now a generation deep. Former champions coach current competitors. Regional networks share word lists. Parents who grew up watching the Bee in India now train children born in San Bernardino, Aurora, and McGregor, Texas. The infrastructure is replicable, community-driven, and almost entirely volunteer-run.

For the diaspora, the Bee has become something more than an academic competition. It is a visible, nationally televised reminder that the children of immigrants — many from families who arrived with little beyond graduate degrees and determination — can dominate a discipline that rewards sustained effort, analytical thinking, and an appetite for knowledge that borders on obsessive.

Parikh practiced five hours a day. His favorite word is "muntjac," a small deer from Southeast Asia. He is 14 years old, and he just set a record."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Eleven Indian Americans Won Soros Fellowships This Year. They Represent a Third of the Entire Class.",
        "subheadline": "The 2026 Paul & Daisy Soros Fellowships for New Americans selected 30 winners from 3,070 applicants. Eleven were of Indian origin, spanning medicine, physics, law, bioengineering, and literature.",
        "slug": make_slug("soros-fellowship-2026-eleven-indian-americans-graduate"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian Americans making up more than a third of the nation's most prestigious immigrant fellowship class reflects how the diaspora's investment in education and academic excellence translates into outsized representation at the highest levels of American graduate study.",
        "tags": ["nri", "diaspora", "fellowship", "soros", "education", "graduate-school", "indian-american"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com/2026/05/05/11-indian-americans-win-soros-fellowships-for-new-americans/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/six-promising-young-indian-americans-awarded-paul-daisy-soros-fellowship/"},
            {"name": "MIT News", "url": "https://news.mit.edu/2026/six-mit-awarded-2026-paul-and-daisy-soros-fellowships-0428"},
            {"name": "The Indian Eye (8 winners)", "url": "https://theindianeye.com/8-indian-americans-win-paul-and-daisy-soros-fellowships/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/8093018/pexels-photo-8093018.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """The Paul & Daisy Soros Fellowships for New Americans is one of the most competitive graduate school programs in the country. It is restricted to immigrants and the children of immigrants. Each fellow receives up to $90,000 to pursue graduate studies at institutions like Harvard, MIT, Stanford, and Yale. The application pool this year was 3,070.

Thirty were selected. Eleven are of Indian origin. That is more than a third of the class, from a community that constitutes about 1.5 percent of the American population.

## The Names and Their Fields

The cohort reads like a cross-section of where Indian American academic ambition is pointing in 2026.

In medicine and biological sciences: Akshaya Vijaya Annapragada is pursuing an MD/PhD at Johns Hopkins, applying machine learning to cancer detection. Ananthan Sadagopan, raised in a household immersed in Tamil culture and the Vedas, is working toward a PhD in biological and biomedical sciences at Harvard. Arya Rao, the daughter of Konkani physicians, is enrolled in the joint Harvard-MIT MD/PhD program using artificial intelligence to study therapeutic design. Ronak Desai, also at Harvard-MIT, is using AI to design new antibiotics. Yasa Baig, an immigrant from India, is completing a PhD in bioengineering at Stanford. Vivasvan Vykunta rounds out the medical cohort, pursuing an MD/PhD at UCSF.

In physics and engineering: Avinash (Avi) Vadali, who grew up attending the Hindu Temple of Greater Chicago, is beginning a PhD in condensed-matter physics at MIT. Ria Das, also affiliated with MIT, is researching conceptual change in computer science.

In law and policy: Akhil Rajan, a JD/PhD candidate at Yale, previously served in the Biden-Harris White House and spent part of his childhood in India.

In the humanities: Malavika Kannan, born in Johnstown, Pennsylvania, and raised in Central Florida in a tight-knit community of Indian immigrant families, is pursuing an MFA in literature. She writes about identity, culture, and politics for The Washington Post, Teen Vogue, and The San Francisco Chronicle.

And Dhruv Gaur, a PhD student in economics at MIT, is studying the effects of severe marginalization on health.

## A Fellowship Built for Immigrant Stories

The fellowship was established by Paul Soros — himself a Hungarian immigrant — and his wife Daisy to honor the contributions of new Americans. The selection criteria emphasize creativity, originality, and initiative, not just GPA. The program explicitly asks: what has this person done with the opportunities that immigration made possible?

The Indian American fellows answer that question in strikingly different ways. Keerthana Hogirala was born in Tirupati and immigrated at age six. Her parents worked multiple jobs to maintain the employment required to extend their immigration status. She took on responsibilities for her family's well-being and her brother's education from childhood. After more than a decade of uncertainty, her family gained citizenship. She is now pursuing graduate study at Harvard Medical School.

Jaspreet Kaur, a DACA recipient from India and Harvard graduate, is pursuing an MFA in writing for screen and television at USC, creating films to uplift intersectional narratives of underrepresented communities.

## What a Third of the Class Looks Like

Indian Americans have appeared prominently in the Soros Fellowship for years. But 11 of 30 is unusually high even by the community's standards.

The pattern is consistent with broader data. Indian Americans hold 10 percent of U.S. patents, make up 10 percent of doctors, and account for 11 percent of unicorn startup founders, according to data compiled by financial analyst Sarthak Ahuja. Seventy-eight percent hold college degrees, more than double the national average.

But the Soros numbers also reflect something specific to the immigrant experience. These are not legacy admits or children of wealth — or at least, not primarily. They are the children of software engineers, cancer researchers, physicians, and families who arrived on H-1B visas and spent years navigating the green card backlog. The fellowship exists precisely to recognize what that particular trajectory produces.

Each fellow will receive up to $90,000 toward their graduate studies. The institutions receiving them — Harvard, MIT, Stanford, Yale, Johns Hopkins, UCSF, USC — are not diversifying their classes as charity. They are recruiting talent that the immigration system, for all its dysfunctions, continues to deliver.

The 2026 Soros class is a snapshot of what happens when a diaspora invests relentlessly in education, and the returns are measured not in remittances but in research papers, patent filings, and the quiet accumulation of institutional influence across American academia."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The IRS Just Raised FBAR Penalties Again. Most NRIs Don't Know They're on the Hook.",
        "subheadline": "For 2026, penalties for failing to report foreign bank accounts have been adjusted upward for inflation. Dual citizens, NRIs with NRE/NRO accounts, and anyone with signing authority over a foreign account should pay attention.",
        "slug": make_slug("irs-fbar-penalties-2026-nri-foreign-accounts-compliance"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "FBAR compliance is one of the most commonly overlooked obligations facing NRIs in the U.S. — particularly those who maintain NRE/NRO accounts in India, hold retirement funds from previous employment abroad, or have signing authority over family accounts back home.",
        "tags": ["nri", "diaspora", "fbar", "irs", "tax-compliance", "fatca", "foreign-accounts"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Morningstar / ACCESS Newswire", "url": "https://www.morningstar.com/news/accessnewswire/newsroom-irs-tightens-fbar-penalties-for-2026"},
            {"name": "CA Club India", "url": "https://www.caclubindia.com/articles/foreign-assets-rsus-and-foreign-bank-accounts-in-itr-schedule-fa-reporting-notices-and-penalty-explained-52937.asp"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/tax/worked-in-the-us-uk-or-canada-form-40-can-help-defer-tax-on-foreign-pension-accounts"},
            {"name": "IRS FBAR FAQ", "url": "https://www.irs.gov/businesses/small-businesses-self-employed/fbar-filing-requirements"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6927374/pexels-photo-6927374.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """Every year, around this time, American tax professionals issue the same warning, and every year, a sizable number of NRIs discover it too late. The Foreign Bank Account Report — FBAR, formally FinCEN Form 114 — must be filed by any U.S. person whose combined foreign financial accounts exceeded $10,000 at any point during the calendar year. For 2026, the penalties for failing to do so have been adjusted upward again.

Non-willful violations now carry higher inflation-adjusted penalties per account, per year. Willful violations remain subject to the greater of $100,000 (adjusted for inflation) or 50 percent of the account balance. The IRS coordinates FBAR enforcement with the Financial Crimes Enforcement Network (FinCEN), and information sharing under FATCA and bilateral tax treaties has made undisclosed accounts substantially more visible.

## Who This Actually Affects

The FBAR obligation catches a wider net than most NRIs expect. The $10,000 threshold is an aggregate — not per account. It captures bank accounts, brokerage accounts, certain pension accounts, and even signing authority over accounts held by others.

For the Indian diaspora, this creates several common exposure points.

**NRE and NRO accounts in India.** Any U.S. tax resident who maintains a Non-Resident External (NRE) or Non-Resident Ordinary (NRO) account with an Indian bank must include it in their FBAR calculation. If your NRE fixed deposits, NRO savings, and any other foreign accounts together crossed $10,000 at any point during the year, the filing obligation is triggered. Given prevailing NRE fixed deposit rates of 6-7 percent, many NRIs hold balances well above this threshold.

**Retirement accounts from previous employment abroad.** NRIs who previously worked in India, the UK, Canada, or Australia and retain provident fund balances, EPF accounts, or pension funds in those countries are also caught. India's Outlook Money recently highlighted Form 40 as a mechanism for returning NRIs to defer Indian tax on foreign retirement accounts, but the FBAR obligation runs in the opposite direction — it is a U.S. requirement, regardless of what India requires.

**Signing authority over family accounts.** If you have signing authority over a parent's or relative's bank account in India — a common arrangement for managing elderly parents' finances from abroad — that account must also be reported, even if you have no financial interest in it.

## The Gap Between Obligation and Awareness

"FBAR is the obligation most often missed by taxpayers who don't think of themselves as having anything offshore," a spokesperson for Clear Start Tax, a national tax relief firm, told ACCESS Newswire on June 3. "Dual citizens, U.S. residents with retirement accounts in their home country, business owners with vendor accounts abroad — the rule applies to far more taxpayers than people assume."

The filing is separate from income taxes. A taxpayer can be fully compliant on their 1040 and still face FBAR penalties for failing to file the disclosure. The form is due April 15, with an automatic extension to October 15 — but many NRIs do not realize it exists until they receive a notice.

FATCA — the Foreign Account Tax Compliance Act — runs parallel to FBAR but with different thresholds and a different form (Form 8938, filed with the tax return). FATCA requires reporting of specified foreign financial assets exceeding $50,000 for individual filers ($200,000 for married filing jointly living abroad). The two obligations overlap but do not replace each other. Filing one does not satisfy the other.

## India's Side of the Mirror

The compliance pressure is not one-directional. India has its own reporting requirements for residents who hold foreign assets, enforced through Schedule FA in the income tax return. The Income Tax Act, 2025, through Section 263, requires any resident (other than not ordinarily resident) who holds foreign assets, financial interests, signing authority, or beneficiary interests to file a return regardless of income level.

For NRIs contemplating a return to India, the tax residency change creates its own timing mismatches. Foreign retirement accounts that were tax-deferred in the U.S. may trigger Indian tax obligations the moment residency status shifts — even if no withdrawal has been made.

## What to Do Now

The October 15 FBAR extension deadline gives procrastinators a few more months. But the penalties for non-filing are not academic. For accounts with substantial balances — and many NRIs with NRE fixed deposits, PPF accounts, and equity holdings in India hold six- or seven-figure balances in aggregate — a willful violation penalty of 50 percent of the account balance is financially devastating.

The minimum protective steps: confirm whether your combined foreign accounts crossed $10,000 at any point in 2025; check whether you have signing authority over anyone else's foreign account; file FinCEN Form 114 electronically through the BSA E-Filing System; and if you have missed prior years, consult a tax professional about the IRS Streamlined Filing Compliance Procedures, which offer reduced penalties for taxpayers who can certify their non-compliance was non-willful.

The IRS is not getting less interested in foreign accounts. It is getting more."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
