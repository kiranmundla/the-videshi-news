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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Five Percent of Every Dollar You Send Home — Congress Is Coming for NRI Remittances",
        "subheadline": "A proposed excise tax on all non-citizen money transfers would hit H-1B workers, green card holders, and OPT students — even when they're moving money between their own accounts.",
        "slug": make_slug("remittance-tax-five-percent-nri-h1b-green-card-congress"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian Americans send roughly $38 billion a year back to India from the US — the single largest remittance corridor in the world. A 5% excise tax would skim nearly $2 billion off those transfers annually, hitting H-1B workers supporting families, green card holders paying EMIs on properties back home, and students on OPT sending savings to parents. Even moving money between your own US and Indian bank accounts would trigger the tax if you're not a citizen.",
        "tags": ["remittance-tax", "nri", "h1b", "green-card", "congress", "reconciliation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Holland & Knight", "url": "https://www.hklaw.com/en/insights/publications/2025/05/another-surprise-in-the-one-big-beautiful-bill-excise-tax-on-remittances"},
            {"name": "Tax Foundation", "url": "https://taxfoundation.org/research/all/federal/remittance-tax-big-beautiful-bill/"},
            {"name": "The Conference Board", "url": "https://www.conference-board.org/publications/excise-tax-on-remittances"},
            {"name": "SurgePay / Medium", "url": "https://medium.com/@surgepay/india-gets-135-billion-in-remittances-where-does-it-actually-go"},
            {"name": "Associated Press", "url": "https://apnews.com/article/congress-reconciliation-immigration-bill"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6289170/pexels-photo-6289170.jpeg",
        "body": """India is the world's largest recipient of remittances. In fiscal year 2024-25, the country received $135.4 billion from its diaspora, with the United States alone accounting for 27.7% of that total — roughly $38 billion. The US-India corridor is now the single most valuable remittance pipeline on earth, having overtaken the Gulf states for the first time in history.

Congress wants a cut.

## The Provision Nobody Read

Buried in the reconciliation legislation that passed the House last year — the grandly named "One Big, Beautiful Bill Act" — sits Section 4475 of the Internal Revenue Code, as newly proposed: a 5% excise tax on every remittance transfer initiated by a non-citizen or non-national of the United States.

The Republican Study Committee has recommended carrying this provision forward into the Senate's $72 billion immigration enforcement package now making its way through Congress. The Senate returned from Memorial Day recess this week with the bill still unfinished.

The provision's architects framed it as a tool to discourage undocumented immigration. But the text reaches far beyond that target. As Holland & Knight's analysis noted, the tax applies to "any other person who initiates a remittance, whether they are in the US legally or illegally." That means H-1B holders. Green card holders. L-1 executives. F-1 students on OPT. J-1 researchers.

The only people exempt: US citizens and US nationals (a narrow category that includes American Samoans and certain Northern Mariana Islanders). If you hold a green card but haven't naturalized, you pay.

## How It Works

Remittance transfer providers — banks, fintechs like Remitly and Wise, money transfer operators — would be required to collect the 5% tax at the point of transfer and remit it quarterly to the Treasury. The provider carries secondary liability if the tax isn't collected.

There is a refundable tax credit for anyone with a valid Social Security number. So an H-1B worker who files US taxes could, in theory, reclaim the 5% when they file their annual return. But the cash is withheld upfront. For someone sending $2,000 a month to parents in Hyderabad — a common figure among Indian tech workers — that's $100 a month locked up until April of the following year.

And the provision contains what lawyers call an "anti-conduit rule," designed to prevent people from routing transfers through intermediaries to avoid the tax.

## The Math for Indian Americans

India's diaspora in the United States numbers roughly 4.8 million, making it the largest immigrant group in the country after Mexicans. RBI data shows that remittances from the US to India have been growing at double-digit rates, tracking toward $40 billion in FY2025-26.

At a 5% rate, the excise tax would generate approximately $1.9 billion to $2 billion annually from the US-India corridor alone. For context, that's more than double the entire annual budget of USCIS's fraud detection and national security directorate.

The burden falls heaviest on workers who are already under the most immigration pressure. An H-1B holder earning $120,000 a year and remitting $24,000 annually to family in India would face a $1,200 upfront tax — on top of the $100,000 visa fee their employer now owes, the income taxes they already pay at a higher effective rate than most Americans (because non-residents cannot claim several common deductions), and the uncertainty of a green card backlog that stretches to 2060 and beyond.

## The Constitutional Question

Legal experts have raised concerns about the provision's structure. The Tax Foundation noted that requiring financial institutions to verify citizenship status at the point of every transaction creates an enormous compliance burden. Banks already collect W-9 forms, but a W-9 alone may not satisfy the new verification requirements.

More fundamentally, critics argue the tax creates a two-tier system: US citizens can send money abroad freely, while legal permanent residents doing the identical transaction are penalized. Whether that distinction survives equal protection scrutiny is an open question that no court has yet addressed.

## What NRIs Should Do Now

The provision passed the House but remains in flux in the Senate. The reconciliation bill's path forward is uncertain — disagreements over an unrelated IRS fund and other provisions have stalled floor action. Immigration attorneys recommend that affected workers keep records of all international transfers and consult a tax advisor about their specific situation.

For the millions of Indian Americans who wire money home every month — for parents' medical bills, siblings' education, property EMIs, or simply family support — the message from Congress is blunt: your contribution to the world's largest remittance corridor is now a revenue opportunity."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The $100,000 Boomerang: H-1B Fees Are Sending Thousands of Tech Jobs Back to India",
        "subheadline": "Trump's visa restrictions were supposed to create American jobs. Instead, multinationals are accelerating offshoring to Bangalore, Hyderabad, and Pune at rates not seen since the early 2000s.",
        "slug": make_slug("h1b-fees-offshoring-tech-jobs-india-boomerang"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For Indian Americans working in US tech, the offshoring surge is a two-front squeeze: their visa status is under attack at home, while the work they do is being relocated to the country they left. H-1B holders who spent years building careers in Silicon Valley now face the possibility that their own positions could be offshored — not because of their performance, but because their employer decided it's cheaper to hire three engineers in Hyderabad than pay $100,000 to keep one in San Jose.",
        "tags": ["h1b", "offshoring", "tech-jobs", "india", "tcs", "infosys", "wipro"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Whispers in the Corridors", "url": "https://whispersinthecorridors.com/20-more-offshoring-to-india-by-mncs-likely/"},
            {"name": "Whispers in the Corridors", "url": "https://whispersinthecorridors.com/big-tech-firms-shifting-jobs-from-us-to-india/"},
            {"name": "CIO.com", "url": "https://www.cio.com/article/h1b-math-100000-fee-enterprise-it-economics/"},
            {"name": "Nasscom / IPA Newspack", "url": "https://ipanewspack.com/indian-it-firms-invested-1billion-in-us-talent-training-nasscom/"},
            {"name": "Trak.in", "url": "https://trak.in/stories/tcs-infosys-cognizant-h1b-fee-hit-2026-trump-policy/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg",
        "body": """The policy was straightforward in theory: make it expensive to hire foreign workers, and companies will hire Americans instead. The $100,000 H-1B visa fee, effective September 2025, was designed to do exactly that. Nine months later, the data tells a different story.

Multinational corporations are not replacing H-1B workers with American hires. They are replacing them with engineers in Bangalore, Hyderabad, and Pune.

## The Numbers

Industry analysts tracking hiring patterns across major tech firms report that offshoring to India by multinational corporations is projected to increase by 20% in 2026. Google, Amazon, Microsoft, Uber, and eBay have all expanded their India-based engineering teams since the fee took effect, with 25% of surveyed companies adding headcount in Indian offices and 20% creating entirely new roles that did not previously exist in their India operations.

The arithmetic is brutal. A senior software engineer in San Jose costs roughly $250,000 a year in total compensation. Add the $100,000 visa fee (amortized over six years, that's about $16,600 annually, or $5 to $7 extra per billable hour, according to Forrester), and the calculation tips decisively toward offshore delivery.

An equivalent engineer in Hyderabad costs $40,000 to $60,000. For the price of one H-1B worker plus the new fee, a company can hire three to four engineers in India. The quality gap that once justified the premium has narrowed considerably — India now produces more computer science graduates annually than any other country.

## The Indian IT Giants' Exposure

The major Indian IT services firms — the ones the $100,000 fee was most explicitly aimed at — face staggering potential liabilities. Bloomberg's analysis of four years of consular processing data found that Infosys, TCS, and Cognizant collectively face a theoretical $2.25 billion in fees if they maintained prior H-1B hiring volumes.

Infosys alone processed over 10,400 H-1B workers through US consulates between 2020 and 2024. At $100,000 per petition, that's a $1.04 billion exposure. TCS faces $650 million. Cognizant, $560 million or more.

But these companies are not paying those fees. They are doing what any rational economic actor would do: restructuring delivery to avoid the cost entirely.

Nasscom, the Indian IT industry's trade body, has been remarkably candid about the adjustment. H-1B workers now account for less than 1% of the total employee base of the top ten Indian and India-centric companies, down from a much larger share a decade ago. The industry invested over $1 billion in US-based training and hiring programs — not out of altruism, but as a strategic pivot away from visa dependency.

"Given this trajectory, we anticipate only a marginal impact for the sector," Nasscom said in a statement, effectively acknowledging that the H-1B channel is becoming irrelevant to their business model.

## The Paradox

The Trump administration's stated goal was to "incentivize companies to train up and hire American workers," as a Justice Department attorney told a federal judge in Boston last week during the hearing on the fee's legality.

What's actually happening is more complicated. Companies are hiring some American workers — but at a pace that doesn't remotely offset the offshore shift. When an H-1B position in the US is eliminated, the work doesn't simply transfer to an American employee at the same desk. It transfers to a team in India, often at a different scale entirely. One onshore role becomes two or three offshore roles, creating a net export of intellectual work.

For India's domestic tech sector, the irony is rich. After years of worrying about protectionist US policies killing their US-facing business model, Indian IT firms are finding that those same policies are driving more work their way. Pune and Hyderabad are hiring. The GCC (Global Capability Center) buildout — where multinationals establish their own captive tech centers in India rather than outsourcing to TCS or Infosys — is accelerating.

## What This Means for Indian Americans

For the roughly 600,000 Indian-born workers currently on H-1B visas in the United States, the offshoring surge creates a quiet, corrosive anxiety. The value proposition they once offered employers — specialized skills, delivered onshore, at a competitive cost — is being undermined not by their own shortcomings but by a policy that makes their physical presence in America prohibitively expensive.

Some are already seeing the effects. Teams that once had five onshore engineers and three offshore now have two onshore and eight offshore. The onshore roles that survive are increasingly limited to client-facing positions, architectural leadership, and compliance-sensitive work — roles that require physical presence for regulatory or relationship reasons.

The workers who remain face a grimmer calculus than ever: a $100,000 fee hanging over their employer's head, a green card backlog stretching decades into the future, and the slow erosion of the very positions that justify their continued presence.

The policy was supposed to make America more attractive to American workers. For thousands of Indian engineers, it's making India more attractive to American companies."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
