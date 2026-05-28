#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-28 20:00 UTC run"""
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
        "headline": "12 Million Applications and Nobody Picking Up the Phone",
        "subheadline": "Nineteen Democrats just sent USCIS Director Joseph Edlow a letter asking where the money went. The backlog has grown by 2 million cases since January 2025 — while filing fees keep climbing.",
        "slug": make_slug("uscis-12-million-backlog-democrats-demand-answers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals file more H-1B petitions, more I-140 immigrant worker petitions, and more adjustment-of-status applications than any other nationality. When the backlog swells to 12 million, Indians are statistically the single largest group left waiting — and the least likely to see movement, given the per-country green card cap.",
        "tags": ["uscis", "backlog", "processing-delays", "h1b", "green-card", "congress"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Congressman Seth Moulton Press Release", "url": "https://moulton.house.gov/news/press-releases/moulton-leads-letter-demanding-answers-backlog-uscis"},
            {"name": "Quiver Quantitative", "url": "https://www.quiverquant.com/news/Press+Release%3A+Moulton+and+18+Democrats+Seek+Answers+on+USCIS+Application+Backlog+from+Mullin+and+Edlow"},
            {"name": "American Immigration Lawyers Association", "url": "https://www.aila.org/"},
            {"name": "USA Today", "url": "https://www.usatoday.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3927131/pexels-photo-3927131.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Stacks of pending files — a visual metaphor for the 12 million immigration applications sitting in USCIS queues",
        "body": """Congressman Seth Moulton and eighteen Democratic colleagues sent a letter this week to Homeland Security Secretary Markwayne Mullin and USCIS Director Joseph B. Edlow that contained exactly four questions. Not forty. Not four hundred. Four. The brevity was the point. When nearly 12 million immigration applications are stuck in a processing pipeline that appears to be actively shrinking, the questions don't need to be complicated.

## The Numbers That Don't Add Up

Here is the arithmetic that prompted the letter. Since January 2025, USCIS filing fees have increased — in some categories, dramatically. The agency now charges $215 just to register for the H-1B lottery, up from $10. Premium processing fees have climbed. Biometrics appointments cost more. Supplemental congressional funding was appropriated specifically to reduce wait times.

The backlog grew by 2 million cases anyway.

That is not a rounding error. That is a structural failure large enough to warrant its own congressional investigation, and the Moulton letter is, in effect, the opening salvo. The four questions the lawmakers posed cut to the core of the discrepancy: if revenue is up, why are processing times worse? What percentage of fee revenue is being spent on actual case adjudication versus other functions? Have USCIS funds or personnel been redirected to enforcement activities? And which specific policy changes since January 2025 have contributed to the slowdown?

## What 12 Million Looks Like

To put the number in perspective, 12 million pending applications is roughly the population of Ohio. It is larger than the entire population of Portugal. It represents every type of immigration benefit the agency processes: naturalization applications, green card petitions, work permits, travel documents, asylum cases, H-1B transfers, and more.

The American Immigration Lawyers Association has documented a 46% surge in case processing times across multiple categories. Employment Authorization Document (EAD) renewals — the cards that literally allow work-visa holders to earn a paycheck — are taking months longer than the agency's own posted targets. Premium processing, the paid express lane that is supposed to guarantee a response within 15 business days, has itself experienced delays.

For immigration attorneys, the frustration is quotidian. Phones go unanswered. Online case status trackers show no updates for months. Congressional inquiry responses, once a reliable backstop for stalled cases, have slowed to a trickle.

## The Enforcement Diversion Question

The most politically charged question in the Moulton letter is the third one: whether USCIS resources have been diverted to support enforcement operations run by Immigration and Customs Enforcement or other DHS components. USCIS is, by statute, a benefits-adjudication agency. It is not supposed to be in the deportation business. It is funded almost entirely by applicant fees, not taxpayer dollars — which means the people stuck in the backlog are, in a very direct sense, paying for the agency that isn't processing their paperwork.

If fee revenue is being redirected to enforcement — funding detention, supporting removal operations, or staffing initiatives unrelated to case adjudication — then applicants are effectively subsidizing their own bureaucratic limbo. The letter doesn't accuse. It asks. But the question itself carries an unmistakable implication.

## Why This Hits Indian Americans Hardest

The per-country cap on employment-based green cards means Indian nationals already face the longest wait times in the system — decades, in some EB-2 and EB-3 categories. Every month of processing delay at USCIS compounds that structural disadvantage. An H-1B worker waiting for a green card needs periodic EAD renewals, H-1B extensions, and travel document reauthorizations. Each of those is a separate application feeding into the 12 million backlog.

A single Indian professional on the green card track might have five or six active applications with USCIS at any given time. Multiply that across roughly 400,000 Indians in the employment-based green card queue, and the math gets grotesque. The backlog isn't just a number. It is a chokepoint that determines whether someone can accept a promotion, change jobs, travel to see family, or simply continue working legally.

The Moulton letter landed on a Tuesday. By Friday, neither USCIS nor DHS had issued a public response. The questions remain unanswered. The backlog remains 12 million. The filing fees remain due.

## What Happens Next

Congressional letters are a Washington ritual — often performative, occasionally consequential. This one has teeth primarily because the financial discrepancy it highlights is mathematically verifiable. Fee revenue is a matter of public record. Processing times are posted on the USCIS website. The gap between the two is widening in a direction that demands explanation.

Whether that explanation comes voluntarily or through subpoena will depend on factors well beyond immigration policy. But for the 12 million applicants whose lives are on hold — and for the disproportionate share of them who happen to be Indian — the letter represents something simpler: the first time anyone in Washington has publicly asked why more money is producing fewer results."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "'Come Home' — Sridhar Vembu's Open Letter and the Question 700,000 Indian Engineers Can't Stop Asking",
        "subheadline": "The Zoho founder told Indians in America to pack up and rebuild in India. The advice landed in the middle of the worst immigration policy environment in a generation. Not everyone agrees — but almost everyone is listening.",
        "slug": make_slug("sridhar-vembu-come-home-indian-engineers-h1b-diaspora"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Vembu's letter speaks directly to the roughly 700,000 Indian nationals on H-1B visas and the hundreds of thousands more in the green card queue. For many, the 'stay or go' question is no longer hypothetical — the adjustment of status memo, EB-2 retrogression, and $100K filing fees have made it the central planning question of their professional lives.",
        "tags": ["sridhar-vembu", "zoho", "reverse-brain-drain", "h1b", "indian-diaspora", "green-card"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "LiveMint", "url": "https://www.livemint.com/news/trends/zohos-sridhar-vembu-tells-indians-in-america-bharat-mata-needs-your-talent-says-respect-comes-from-one-source-11777283858842.html"},
            {"name": "ET Edge Insights", "url": "https://etedge-insights.com/featured-insights/u-s-h-1b-fee-hike-zoho-founder-urges-skilled-indians-to-return-and-rebuild-in-homeland-mea-flags-humanitarian-concerns/"},
            {"name": "Connected to India", "url": "https://connectedtoindia.com/"},
            {"name": "Global Net News", "url": "https://globalnet.news/us-immigration-agency-clarifies-green-card-application-rules-for-h-1b-visa-holders/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A passport full of stamps — the physical record of a life lived between two countries",
        "body": """Sridhar Vembu did not bury the lede. "Please come back home," wrote the Zoho founder in an open letter addressed to "brothers and sisters from Bharat." "Bharat Mata needs your talent. Our vast youthful population needs the technology leadership you gained over the years to guide them towards prosperity."

The letter, posted on X and amplified across Indian media within hours, landed at the precise moment when the question it raised — should I stay in America or should I go? — had become the dominant conversation in every Indian WhatsApp group from San Jose to Stamford.

## The Context That Made It Viral

Vembu's letter did not arrive in a vacuum. It arrived in the wake of a USCIS policy memo that reclassified adjustment of status as "extraordinary relief," effectively telling most green card applicants to leave the country and apply from abroad. It arrived after the EB-2 India priority date retrogressed by ten months in a single visa bulletin. It arrived alongside a $100,000 per-petition H-1B filing fee that has already caused registrations to crash by 38.5 percent. And it arrived the same week that 19 Democratic lawmakers sent a letter demanding to know why USCIS is sitting on nearly 12 million unprocessed applications.

In other words, it arrived when the ground was already shaking.

## What Vembu Actually Said

The letter is worth reading in full because it is considerably more nuanced than the headlines suggest. Vembu does not merely tell people to leave America. He constructs an argument about civilizational self-respect that draws on India's economic trajectory, the limits of American political hospitality, and the structural nature of anti-immigrant sentiment.

"You may think the next election will fix this," Vembu wrote, "but your choice would be between people who hate our Bharatiya civilisation and people who hate civilisation itself. That is the 'hard right' vs 'woke left' battle. You are mere bystanders to that conflict."

The framing is deliberately provocative. Vembu is not making an immigration policy argument. He is making a cultural one: that the respect Indians command globally depends on India's own technological and economic strength, and that the talent currently stuck in American visa queues would be better deployed building that strength at home.

He compared the current moment to the Sindhi community's experience during Partition — people who lost everything, rebuilt in India, and thrived. "It may take five years to rebuild your lives," he wrote, "but it will make you stronger. Do not live in fear. Make the bold move."

## The Diaspora's Response: Divided

The reaction among Indian professionals in the United States has been predictably split — and the fault lines are revealing.

Those sympathetic to Vembu's argument tend to be mid-career professionals who have already spent a decade or more in the green card queue and are running out of patience with a system that seems designed to extract maximum fees while delivering minimum certainty. For someone who arrived in 2012, filed for PERM in 2015, got an I-140 approval in 2017, and is now watching the EB-2 date move backward, the calculation has shifted. The American Dream is not dead, exactly, but it is taking so long to process that the dreamer is aging out.

Those who push back tend to point out that Vembu's advice is easier to give from his position — a billionaire founder who can live anywhere — than to follow for a mid-level engineer with a mortgage in Sunnyvale, children in American schools, and a spouse whose H-4 EAD is perpetually at risk. "Come home" is not a plan. It is a bumper sticker.

There is also a third camp, quieter but growing, that has already started making contingency plans without waiting for billionaire advice. Some are exploring Canada's new accelerated PR pathway for H-1B holders. Others are looking at the Gulf Cooperation Council countries, where American companies are increasingly setting up engineering offices. A few are negotiating remote-work arrangements that would let them return to India while keeping their American salaries — at least until the tax implications become clear.

## The Numbers Behind the Emotion

Roughly 700,000 Indian nationals currently hold H-1B status in the United States. Hundreds of thousands more are in the employment-based green card queue, some with priority dates stretching back to the early 2010s. The adjustment of status memo, the EB-2 retrogression, the $100K filing fee, the H-4 EAD uncertainty, and the NIW approval rate collapse have collectively narrowed every pathway that Indian professionals have traditionally used to build permanent lives in the United States.

Meanwhile, India's economy is growing at 6-7 percent annually. Bangalore, Hyderabad, and Pune are producing engineering jobs at rates that would have seemed implausible a decade ago. The salary gap between a senior engineer in the Bay Area and one in Bangalore has compressed significantly — especially once you factor in the cost of living, the visa anxiety premium, and the sheer psychic toll of planning your life in 12-month increments tied to USCIS processing windows.

## The Question That Won't Go Away

Vembu's letter will fade from the news cycle within a week. The question it surfaced will not. Every Indian professional in the United States is now running some version of the same spreadsheet: years remaining in the green card queue versus career opportunities in India versus children's school enrollment versus aging parents versus risk tolerance versus what it means to live in a country where your legal status depends on a bureaucratic process that is 12 million applications deep and getting slower.

No open letter can answer that spreadsheet. But Vembu's contribution was to say out loud what many have been calculating in private: that staying in America is no longer the default option. It is a bet. And the odds are getting longer."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
