#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-08 02:00 PDT run"""

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
    # ── Article 1: H-1B Overhaul Bill ──────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "A New Bill Wants to Kill the H-1B-to-Green-Card Pipeline. Big Tech Should Be Nervous.",
        "subheadline": "The American White-Collar Worker Jobs Act would slash visa duration to two years, eliminate OPT, and end dual intent — a direct strike at the Indian talent pipeline that powers Silicon Valley.",
        "slug": make_slug("h1b-overhaul-bill-green-card-opt-tech-industry"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Three-quarters of all H-1B holders are Indian nationals. The bill would upend the life plans of hundreds of thousands of Indian engineers at Google, Microsoft, Meta, and Amazon — and devastate the US business model of Infosys, TCS, and Wipro.",
        "tags": ["h-1b", "immigration", "silicon-valley", "indian-tech-workers", "green-card"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/world/us-lawmaker-proposes-major-h-1b-visa-overhaul-seeks-to-end-green-card-pathway/article71068304.ece"},
            {"name": "Nagaland Post / IANS", "url": "https://nagalandpost.com"},
            {"name": "Ainvest", "url": "https://ainvest.com"},
            {"name": "Gulte", "url": "https://gulte.com"},
            {"name": "NY Post", "url": "https://nypost.com"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Capitol_at_Dusk_2.jpg/1280px-Capitol_at_Dusk_2.jpg",
        "image_caption": "The United States Capitol building at dusk in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": """The most consequential piece of immigration legislation to hit Congress this year arrived last week with the subtlety of a WARN notice. Representative Chip Roy of Texas introduced the American White-Collar Worker Jobs Act of 2026, a bill that, if enacted, would fundamentally dismantle the pathway that has delivered hundreds of thousands of Indian engineers to American technology companies over the past two decades.

The legislation targets every load-bearing pillar of the H-1B programme. It would replace the current lottery with a wage-based selection system, favouring applicants whose employers offer the highest salaries. It would slash the maximum visa duration from six years to two. It would eliminate the Optional Practical Training programme, which allows foreign graduates of American universities to work in the US for up to three years after completing their degrees. And it would kill the concept of "dual intent" — the legal fiction that permits H-1B holders to simultaneously work on a temporary visa and pursue a green card.

That last provision is the quiet bomb. For Indian nationals, the H-1B has never truly been a temporary work permit. It is the first rung of a ladder that stretches through years of visa extensions, employer sponsorship, and the notoriously backlogged employment-based green card queue — a wait that can exceed a decade for Indian-born applicants. Ending dual intent would force every H-1B holder to certify that they maintain a residence abroad and have no intention of staying permanently. For the engineer at Google who bought a house in Sunnyvale and enrolled her children in local schools, this is not an abstract policy shift.

## Who gains, who bleeds

The wage-based selection model is designed to favour the highest bidders. In practice, that means Big Tech. An L5 software engineer at Google earning $250,000 would rank far above an IT consultant at an outsourcing firm billing at $80,000. The bill's sponsors may frame this as protecting American workers, but its sharpest blade is aimed squarely at the Indian IT services industry.

Companies like Infosys, TCS, Wipro, and Cognizant have built their American operations around the H-1B programme, rotating thousands of engineers through US client sites on relatively modest salaries. A wage-based lottery would effectively price them out. That is not an unintended consequence — it is the point. Kevin Lynn, president of US Tech Workers, one of the bill's backers, said it would "effectively address many of the egregious aspects" of a system that has "enabled corporations to displace our most productive workers with cheaper and more quiescent foreigners."

The OPT elimination deserves its own alarm. Over 200,000 foreign students — a large proportion of them Indian — are working in the US under OPT at any given time. The programme serves as Silicon Valley's de facto farm system, converting IIT and NIT graduates into junior engineers at startups and established firms alike. Without OPT, companies would need to sponsor an H-1B visa from day one, a process so uncertain and expensive that many would simply stop hiring international graduates.

## The Trump multiplier

The bill lands on fertile ground. The Trump administration has already imposed a $100,000 fee on new H-1B petitions, tightened prevailing wage requirements, and barred non-permanent residents from FHA-insured mortgages. H-1B denial rates are climbing again. In Dallas, the combined effect of these policies has driven home prices sharply lower in neighbourhoods where Indian tech workers once formed the majority of buyers, according to analysis by John Burns Research and Consulting. The housing data offers a preview of what could unfold in the Bay Area, Seattle, and northern New Jersey if the talent pipeline is further constricted.

## What happens next

Roy, who is retiring from Congress, is unlikely to shepherd this bill through committee hearings himself. But the legislation's core proposals — wage-based selection, shorter visa terms, and the end of H-1B as a green card on-ramp — enjoy broad Republican support and align with the administration's stated priorities. Even if this specific bill dies, its provisions are likely to resurface in budget reconciliation or as executive orders.

For Indian tech professionals in the US, the message is unambiguous: the era of the H-1B as a reliable immigration pathway is closing. The bill does not target merit or skill — it targets permanence. And for a community that has built careers, families, and mortgages on the assumption of eventual permanent residency, permanence is the whole game."""
    },

    # ── Article 2: Meta / Zuckerberg / Muse Spark ─────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Zuckerberg Says AI Spending Is Forcing Meta to 'Take Down' Its Workforce. His Flagship AI Model Just Stumbled.",
        "subheadline": "Meta's first closed-source model, Muse Spark, still has no developer API two months after its debut — even as the company cuts 8,000 jobs and promises investors the AI bet will pay off.",
        "slug": make_slug("zuckerberg-meta-ai-layoffs-muse-spark-stumble"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Meta employs thousands of Indian engineers across its Bay Area offices — the same offices that absorbed the heaviest cuts. The layoffs hit integrity, cybersecurity, and content design teams disproportionately, roles where Indians are heavily represented.",
        "tags": ["meta", "mark-zuckerberg", "ai-layoffs", "muse-spark", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Street", "url": "https://www.thestreet.com/technology/mark-zuckerberg-and-meta-face-first-tough-test-after-layoffs"},
            {"name": "Yahoo Finance / Reuters", "url": "https://finance.yahoo.com/sectors/technology/articles/mark-zuckerberg-says-meta-layoffs-133110471.html"},
            {"name": "OpenTools / Bloomberg", "url": "https://opentools.ai"},
            {"name": "The Next Web", "url": "https://thenextweb.com"},
            {"name": "TipRanks", "url": "https://www.tipranks.com"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0e/F20250904AH-2824_%2854778373111%29_%283x4_cropped_on_Zuckerberg_following_the_rule_of_thirds%29.jpg",
        "image_caption": "Mark Zuckerberg, CEO of Meta Platforms",
        "image_attribution": "Wikimedia Commons",
        "body": """Mark Zuckerberg has never been accused of excessive candour. So when he told employees at a company town hall last week that Meta needs to "take down" its workforce size to fund its artificial intelligence ambitions, the words carried unusual weight.

The admission came during a question-and-answer session where Zuckerberg explained the cold arithmetic behind Meta's restructuring. The company has two primary expenses — infrastructure and people. Increasing spending in one area means reducing available resources in the other. With Meta's AI infrastructure budget guided at $125 to $145 billion for 2026 alone, the equation leaves little room for sentimentality.

The numbers tell the rest of the story. Meta has laid off approximately 8,000 employees — roughly 10 per cent of its global workforce — with notifications rolling out in waves beginning in late May. Another 7,000 workers have been reassigned to AI-focused teams. Six thousand planned hires have been cancelled. And filings from late May indicate an additional 1,400 cuts are scheduled for July 22, hitting software engineers, data scientists, and content designers in particular.

In the Bay Area alone, 3,196 workers were cut across five offices. The teams hit hardest — integrity, cybersecurity, and content design — are precisely the ones where Indian engineers have been disproportionately represented.

## The Muse Spark problem

All of this might be easier to swallow if the AI products were arriving on schedule. They are not.

Muse Spark, Meta's first closed-source AI model, was unveiled in April with considerable fanfare. Developed by the TBD Lab within Meta Superintelligence Labs — the division led by Alexandr Wang, whom Zuckerberg recruited with a $14.3 billion investment in Wang's company Scale AI — the model was supposed to mark Meta's entry into the lucrative business of selling paid API access to developers. It was a strategic departure from the open-source Llama models that had defined Meta's AI identity. Where Llama gave everything away, Muse Spark was designed to generate revenue.

Two months later, the developer API still does not exist.

Wang himself had told developers on X shortly after the April debut: "The Muse Spark API will be coming soon." The timeline slipped from April to May, then to June. As of early June, there was no confirmed launch date. Reuters, citing people familiar with the matter, reported that the delays stem from software bugs and infrastructure problems discovered during testing.

A Meta spokesperson said the company is testing the API with early partners and expects to release it this month. That may be true. But it does not answer the question investors are beginning to ask more pointedly: if Meta cut thousands of jobs to fund AI, why is the first major AI product two months behind schedule?

## The sequence matters

The individual facts — layoffs, a delayed model, rising capex — are not individually alarming. Layoffs happen. Products slip. Capital expenditure on AI is a story shared by every technology company with ambitions. What makes Meta's situation distinctive is the sequence.

In May, Zuckerberg told employees that the layoffs were necessary to fund AI. Days later, Meta filed plans for yet more cuts in July. Meanwhile, the flagship model that was supposed to prove the AI investment is working sits behind a locked API door. OpenAI, Anthropic, and Google have all made developer access a launch-day feature for their frontier models. Meta is the only major AI company that has unveiled a closed-source model and then withheld API access for nearly two months without a confirmed release date.

For Meta's Indian engineering workforce, the stakes are particularly sharp. Many of the 3,196 Bay Area employees who lost their jobs are on H-1B visas, which give them only 60 days to find a new employer sponsor before they must leave the country. The restructuring is not merely a career disruption — it is a potential immigration crisis for the individuals affected.

## What Zuckerberg does not know

Pressed on whether more layoffs might follow, Zuckerberg offered an uncharacteristically honest answer: "I wish that I can tell you that I have a crystal ball plan for the next three years of how all this stuff is going to play out. I don't. I don't think anyone does."

That admission is worth taking at face value. The AI spending race has no precedent. No company has ever redirected this much capital from headcount to infrastructure at this speed, and the returns remain speculative. Meta's core advertising business continues generating substantial cash flow, and the stock still carries a consensus Strong Buy rating from analysts.

But the gap between investment and execution is now measurable. A company that fires thousands to fund AI and then cannot ship its flagship AI product on time has handed its critics a data point they did not previously possess. Markets are patient with vision. They become less patient when products fall behind schedule — especially when the payroll of the people who were supposed to build those products has already been redirected to servers."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
