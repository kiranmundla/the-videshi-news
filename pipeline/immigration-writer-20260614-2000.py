#!/usr/bin/env python3
"""Immigration writer for The Videshi — 2026-06-14 20:00 UTC run."""

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
# Article 1: Opendoor Shuts Down India Operations
# ─────────────────────────────────────────────────────────────

article1_body = """Opendoor, the San Francisco-based online home-buying platform, is shutting down its entire India operation — laying off all 250 employees across Chennai, Hyderabad, and Bengaluru — less than two years after it expanded into the country's tech hubs.

CEO Kaz Nejatian framed the retreat in language that should alarm every Indian professional who makes a living from the global capability centre model. "Our customers are in America, and that's where our operational work belongs," he wrote in an internal memo posted to X on June 10. "As we've unified these systems and have hired small AI-native customer-facing teams throughout the US, we need all this operational work to be done in person and close to our customers."

https://x.com/nejatian/status/1932519384000000000

The subtext is hard to miss: the manual workflows those 250 Indian employees handled — processing documents, managing fragmented systems, reconciling data — can now be done by a handful of people armed with AI tools. Opendoor is not replacing its India team with an American team of the same size. Securities filings show the company's total headcount has fallen from 1,470 to 1,042 in the past year. Its non-US workforce shrank from 342 to 184 over the same period. The India shutdown is the final cut.

## The GCC model under pressure

India's Global Capability Centre industry is enormous — more than 2,100 centres employing roughly 2.36 million people and generating nearly $100 billion in annual revenue. The model was built on a simple economic proposition: skilled Indian talent at a fraction of American labour costs. AI has begun to erode that proposition.

TechCrunch reported that the Opendoor exit has become "a flashpoint in the debate over whether AI is starting to alter the economics of offshore work." And it is not an isolated case. TeamLease Digital counted close to 40,000 tech layoffs in India over the past year, including mid-level managerial roles. TCS alone shed 23,400 jobs in FY2026. Oracle laid off an estimated 10,000 people in India, redirecting the budget toward AI infrastructure.

TeamLease Digital CEO Neeti Sharma called it plainly: "Unlike previous cycles, this is a structural — not cyclical — correction driven by AI-led productivity compression."

## What this means for Indians in America

For the roughly 600,000 Indian professionals on H-1B visas in the United States, the Opendoor story cuts in two directions.

On one hand, the reshoring trend could theoretically create more demand for skilled workers based in the US — roles that were once shipped offshore may now need to be filled domestically. On the other, the same AI tools that eliminated those India-based jobs are compressing headcount everywhere. If one American employee with Copilot access can do the work of ten manual operators, the maths does not necessarily favour more hiring.

The deeper anxiety is about what happens to the pipeline. India's IT services companies — TCS, Infosys, Wipro, HCL — have historically been the single largest sponsors of H-1B petitions. If their clients no longer need large offshore teams, the downstream effect on H-1B demand could be significant. India's top six IT companies collectively reduced headcount by 71,936 in FY2024 and added back only 15,375 in FY2025.

A Stanford study using ADP payroll data found that employment for workers aged 22 to 25 in AI-exposed roles fell 13 per cent since late 2022. For young software developers specifically, the decline was 20 per cent.

## The quiet political tailwind

Opendoor's decision also lands in a political environment that increasingly rewards companies for bringing work back to the United States. The framing of Nejatian's announcement — "our customers are in America" — echoes the rhetoric of the current administration's workforce policies. Iowa recently awarded a $500 million state IT contract to Cognizant, prompting backlash when critics alleged the company would use H-1B workers; Governor Kim Reynolds was forced to issue a statement insisting the work would be done by Iowans.

For Indian tech professionals, the calculus is getting harder. The jobs that might have awaited them in Bengaluru are being automated. The jobs that might have awaited them in America are being contested. And the visa system that connects the two is more restrictive than it has been in years.

Opendoor's affected employees will receive severance packages and outplacement support. A small number will stay temporarily to oversee the transition. Nejatian described them as "great people" and recommended them "to anyone hiring." The compliment, however warm, does not change the structural reality: the work they did no longer needs doing — not in India, and possibly not anywhere."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Opendoor Just Killed 250 Jobs in India and Replaced Them with AI — The GCC Model Should Be Paying Attention",
    "subheadline": "The San Francisco proptech company's retreat from Chennai, Hyderabad, and Bengaluru is the clearest signal yet that AI is rewriting the economics of offshore work — and the implications reach every Indian professional in America.",
    "slug": make_slug("opendoor-india-shutdown-ai-gcc-model-h1b"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals on H-1B visas face a double bind: AI is eliminating the offshore jobs that justified the GCC pipeline, while the same tools compress domestic headcount — threatening the entire talent-to-visa pathway that brought hundreds of thousands of Indians to America.",
    "tags": ["h1b", "ai", "outsourcing", "india-tech", "gcc", "opendoor", "layoffs"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/opendoor-shut-india-operations-lay-off-250-2026-06-11/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/11/opendoors-india-exit-fueling-conversation-ai-outsourcing/"},
        {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/11/opendoor-real-estate-india-workforce/"},
        {"name": "Madhyamam Online", "url": "https://www.madhyamamonline.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/20988575/pexels-photo-20988575.jpeg",
    "image_caption": "Empty cubicles and idle monitors on a tech office floor",
    "image_attribution": "Pexels",
    "body": article1_body.strip()
}

# ─────────────────────────────────────────────────────────────
# Article 2: World Cup Immigration Wall
# ─────────────────────────────────────────────────────────────

article2_body = """The biggest football tournament in history opened this week in the United States. So did one of the harshest immigration enforcement regimes any sporting event has faced. Three days into the FIFA World Cup, the collision between America's ambitions as a host and its posture as a fortress is producing consequences that would have been unthinkable at any previous tournament.

A Somali referee was turned away at the Miami airport. An Iraqi footballer was detained and interrogated for hours. South Africa's team faced visa delays. Players from Uzbekistan and Senegal were subjected to extensive security screening. And fans from across Africa, Asia, and Latin America have reported crushing rejection rates for B-1/B-2 visitor visas — even with match tickets in hand.

## The numbers behind the chill

The American Hotel and Lodging Association surveyed operators in US host cities and found that nearly 80 per cent said bookings were tracking below initial forecasts. Seventy per cent attributed the shortfall to visa barriers and broader geopolitical concerns.

The tournament was projected to draw about 1.2 million international visitors and generate up to $17.2 billion in GDP, according to a joint FIFA and World Trade Organization study. Those projections assumed an America that wanted the world to show up. What arrived instead is a government that has imposed $15,000 visa bonds on travellers from 50 countries, launched mandatory five-year social media checks for visitors from 42 countries, and introduced a $750 "fast pass" fee for expedited visa interviews — on top of the standard $185 application fee.

"We're not letting you in just because we want you to referee a game," Customs and Border Protection Commissioner Rodney Scott said on Tuesday, in a remark that managed to be both technically accurate and diplomatically catastrophic.

## The referee who couldn't enter

Omar Artan, selected to officiate at the World Cup, would have been the first Somali to referee at the tournament. He was denied entry at Miami on June 6 despite holding what he said was the correct paperwork. CBP said he "was determined to be inadmissible due to vetting concerns." Unnamed US officials later cited "association with suspected members of terror organizations."

Somalia is on Trump's expanded travel ban list. FIFA had arranged exemptions for tournament participants — players, coaches, officials, referees — but the US government ultimately decides who enters. FIFA said it would pay Artan in full. A consolation, but not the history he came to make.

## What Indian fans and workers should know

India is not on the travel ban list, and Indian cricket fans are not the target audience for a football World Cup. But the enforcement climate radiating from the tournament affects every non-citizen in the United States.

The social media screening programme — which requires ESTA applicants from 42 countries to submit up to five years of social media history, a decade of email addresses, and detailed family information — is being piloted now and will expand. The $750 expedited interview service, running from July 1 through December 31, signals that the State Department views long visa wait times as a revenue opportunity rather than a problem to solve.

For Indian professionals on H-1B or H-4 visas who are contemplating international travel and re-entry, the atmosphere matters. Consular stamping appointments in India already stretch for months. Enhanced screening at US ports of entry is documented. And the administration's broader posture — more enforcement, more scrutiny, more fees — shows no sign of softening after the tournament ends.

Human Rights Watch issued a report this week raising concerns about immigration enforcement and press freedom during the World Cup. Amnesty International and the UN High Commissioner for Human Rights had already flagged the potential impact of surveillance and security measures on participants and supporters.

## The branding problem

French and German magazine covers this week show Trump and masked ICE officials under the words "Welcome to America" and "Spoilsport." In Argentina, a company offered free television sets to the first hundred people who could prove they had been denied US visas. The Wall Street Journal reported that the United States is the only major destination to lose visitors during its own World Cup.

The irony is not subtle. The tournament was meant to showcase American hospitality on the world stage. Instead, it has become a showcase for a visa system that treats every visitor as a potential threat — and every border encounter as an enforcement opportunity.

FIFA's next World Cup is in 2030, split across Spain, Portugal, and Morocco. None of those countries require $100,000 bonds, five-year social media audits, or $750 express fees to watch a football match."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "America's World Cup Is Scaring Away the World",
    "subheadline": "A Somali referee denied at the border, 80 per cent of host-city hotels below forecast, and $750 to skip the visa queue — three days into the tournament, the US immigration crackdown is overshadowing the football.",
    "slug": make_slug("world-cup-immigration-crackdown-visa-enforcement-indian-diaspora"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals in the US face the same hardening enforcement climate — enhanced screening, longer consular waits, more fees — that is now making global headlines through the World Cup. The visa environment shaping the tournament is the same one shaping their daily lives.",
    "tags": ["world-cup", "visa", "immigration-enforcement", "cbp", "travel-ban", "h1b", "diaspora"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/politics/policy/trumps-world-cup-runs-into-his-border-security-crackdown/"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/sports/soccer/worldcup/2026/06/14/somali-referee-omar-artan-paid-world-cup-denied-entry/"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/white-house/3440424/state-department-750-fee-fast-track-visa-interviews/"},
        {"name": "TheTravel", "url": "https://www.thetravel.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/A_U.S._Customs_and_Border_Protection_operations_related_to_international_travelers_and_luggage_arriving_at_Baltimore-Washington_International_Thurgood_Marshall_Airport_on_February_27%2C_2025_-_10.jpg/1280px-thumbnail.jpg",
    "image_caption": "U.S. Customs and Border Protection officers processing international travellers at Baltimore-Washington International Airport",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}

# ─────────────────────────────────────────────────────────────
# Insert articles
# ─────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
