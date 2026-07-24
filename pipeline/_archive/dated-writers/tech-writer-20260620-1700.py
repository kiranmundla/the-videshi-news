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

adobe_body = """Shantanu Narayen has spent 18 years turning Adobe from a maker of boxed software into a subscription machine. On his way out, he is doing something that would once have been heresy: giving the software away.

On Adobe's fiscal second-quarter earnings call on June 11, Narayen confirmed the company is leaning hard into freemium versions of its AI products and has paused price increases on the Creative Cloud suite. The bet is simple. Get hundreds of millions of casual users into Acrobat, Express and Firefly for free, then convert a slice of them into paying customers once they are hooked.

The early numbers are loud. Adobe said freemium monthly active users jumped to more than 90 million from 50 million a year earlier. Acrobat and Express monthly active users climbed past 850 million, up from 700 million. Adobe lifted its full-year revenue guidance to a range of $26.5 billion to $26.6 billion, from a prior $25.9 billion to $26.1 billion. Annual recurring revenue from its AI-first offerings more than tripled year over year, and David Wadhwani, who runs the creativity business, pointed to 45 percent quarter-over-quarter growth in generative-AI credit consumption.

## Why a free Adobe matters to the diaspora

For Indian Americans, this is not abstract. Adobe is one of the largest employers of Indian engineers in the Bay Area and India alike, with a sprawling Noida and Bengaluru workforce that builds the very Firefly and Acrobat features now being handed out for free. A strategy that prioritizes user acquisition over near-term revenue changes what gets built, who gets hired, and which teams get the budget. Engineers reading the tea leaves know that "freemium at scale" means more investment in consumer-facing AI and infrastructure to serve a billion-plus free users, and less in legacy desktop tooling.

There is also a founder-and-creator angle. The Indian diaspora is thick with side-hustlers, YouTubers, designers and small-agency owners who have long paid the Creative Cloud tax in dollars while earning in a mix of currencies. A free Firefly assistant that can drive multi-step creative workflows, plus a price freeze on the paid suite, lowers the cost of starting a content business. Adobe said video-generation credit usage rose eightfold year over year and audio generation doubled, a sign that creators are moving from still images into the more lucrative, more competitive world of AI video.

## The succession question

Narayen told the board in March he would step down after over 18 years, staying on as chair to support his successor. Adobe has a special committee, led by independent director Frank Calderoni, weighing internal and external candidates. The internal bench is notably deep and notably Indian-heritage adjacent: Wadhwani on the creativity side and Anil Chakravarthy, now president of the rebranded Customer Experience Orchestration business, are both seen as contenders alongside outside names.

Whoever wins inherits Narayen's wager. Freemium is a land grab that works only if conversion follows. Adobe is betting that AI makes its tools indispensable enough that free users eventually pay, and that the 90 million number becomes a funnel rather than a charity. Wall Street has been patient so far, rewarding the ARR growth while tolerating the near-term revenue drag.

## What to watch

The real test comes over the next two quarters. If freemium MAUs keep compounding but paid conversions stall, the price freeze starts to look like a defensive crouch against Canva, CapCut and a swarm of cheaper AI-native rivals rather than an offensive play. If conversions hold, Narayen will have engineered one more transition on his way out, and handed his successor a far larger top of the funnel than he inherited.

For the Indian professional whose stock grants are tied to Adobe's share price, and for the creator who finally got Firefly for free, the same number matters most: how many of those 90 million free users open their wallets."""

pramaana_body = """The hottest seed round in Silicon Valley this week did not come from another chatbot startup. It came from a former Google engineer trying to make AI prove it is right.

Pramaana Labs, founded by IIT Madras alumnus Ranjan Rajagopalan, raised $27 million in seed funding led by Khosla Ventures, with Accel, Nexus Venture Partners, Premji Invest, BoldCap and Unbound joining. A seed round of that size is unusual even in the current AI frenzy, and it signals where smart money thinks the next bottleneck lies: not in making AI more fluent, but in making it accountable.

## The accountability gap

Pramaana's pitch attacks a problem every regulated industry knows well. Today's AI can draft a tax return, a legal brief or a clinical note, but a human still has to check it, because when AI is wrong in a high-stakes domain, no one can be held responsible. "AI has an accountability gap," Rajagopalan said. "The world's hardest problems are not unsolvable. They are unformalized."

The company's approach borrows from formal verification, a decades-old computer-science technique for mathematically proving that software behaves correctly. Pramaana encodes the actual rules of a domain, the US tax code, clinical protocols, financial regulations, into a formal language using tools like the open-source Lean proof language. When a user asks a question, the system translates it into a formal statement, runs it through a proof engine, and either returns a machine-checkable proof that the answer is correct or tells the user exactly which rule breaks and why. It refuses to answer before it can prove.

## Why the diaspora should care

This is a quietly Indian story at every layer. The founder is an IIT Madras graduate and ex-Google engineer, the archetype of the diaspora technologist who trades a Big Tech badge for a startup gamble. The backers include Premji Invest, the Wipro chairman's family office, and Nexus and Accel, both deeply wired into the India-US venture corridor. For NRIs who track where Indian-origin founders are placing bets, Pramaana sits at the intersection of two trends: the migration of senior Indian engineers out of FAANG and into AI startups, and the rise of "verifiable AI" as an investable category.

There is a career signal here too. As layoffs hollow out middle-tier software roles, the engineers who survive are the ones working on what AI cannot yet do reliably. Formal verification, proof engines and domain formalization are exactly the kind of hard, defensible skills that command Nvidia-sized salaries rather than pink slips. For an Indian engineer at a Bay Area firm wondering which way to specialize, the Pramaana thesis is a hint: the premium is shifting from generating answers to guaranteeing them.

## A different kind of AI bet

Most AI money in 2026 has chased scale, bigger models, more compute, larger context windows. Khosla Ventures, an early OpenAI backer, leading a seed round on the opposite thesis is notable. Vinod Khosla, who recently warned that India's $200 billion IT services industry "will be gone," has been blunt that the value is moving up the stack toward provably correct systems and away from commodity coding labor that AI can replicate.

Pramaana is stealth-no-more but still early. It has not disclosed customers, and turning the US tax code or clinical guidelines into machine-verifiable logic is brutally hard, domain by domain. The company says its system has never produced a confidently wrong verified answer, a claim that will be tested the moment real enterprises in tax, law and healthcare put it to work.

## What to watch

The signal to track is adoption in a single regulated vertical. If Pramaana can show a CPA firm or a hospital trusting its proofs enough to reduce the human-in-the-loop, the category becomes real. For the diaspora's engineers and investors, it is a reminder that the next wave of AI value may belong less to the labs building ever-bigger brains and more to the startups, often founded by Indian technologists, teaching those brains to show their work."""

meta_body = """For years, a job in Meta's AI division was the prize that Indian engineers in the Bay Area chased: top salaries, frontier work, a seat at the table where the future was being built. This month, reporting suggests it has become something closer to a punishment posting.

A wave of accounts, surfaced by Wired and amplified across the tech press, describes conditions inside Meta's Applied AI and superintelligence teams as "soul-crushing." Engineers hired to build products for billions of users say they are instead slogging through data preparation, readying training sets for a smaller cadre of AI scientists. More than 1,600 workers reportedly signed a petition against an initiative to monitor US employees' keyboard and mouse activity to generate AI training data.

## A culture under strain

Chris Cox, Meta's chief product officer, addressed the "difficult" and "brutal" conditions during a meeting with Instagram employees, according to Wired, describing the experience as "running a marathon in the middle of a hailstorm" while a teammate gets replaced. On AI, he struck an unusually deflating note for a company that has staked hundreds of billions on it: "It is neither god, nor is it the devil. And it's nowhere near as good as you think it is, and it is nowhere near as bad as you think it is."

Mark Zuckerberg, in an internal memo this month, acknowledged the turbulence. "Given the complexity of these changes, we've made mistakes and will almost certainly make more," he wrote, pledging stability going forward. He reportedly said he would not carry out additional mass layoffs this year and would cap how many employees report to a single manager, after cases on the Applied AI team where one manager oversaw 50 workers.

## Why this lands hard for Indian tech workers

Indians make up roughly 71 to 73 percent of approved H-1B beneficiaries in the United States, and Meta's engineering ranks are thick with them. For a visa holder, morale is not a soft issue, it is a risk calculation. A "soul-crushing" assignment is something an American citizen can quit on principle. An H-1B holder weighing the same exit faces a 60-day clock to find a new sponsor or leave the country. That asymmetry keeps many Indian engineers in roles they would otherwise walk away from, absorbing the churn while their citizen colleagues have an easier exit.

The monitoring petition cuts the same way. Surveillance of keyboard and mouse activity is the kind of policy a secure employee pushes back on loudly. For someone whose immigration status is tied to staying employed at this specific company, signing a petition against management carries a weight it simply does not for a green-card holder or citizen. The result is a two-tier workforce experiencing the same upheaval very differently.

## The retention paradox

Meta is simultaneously the place engineers most want to leave and the place paying the most to keep them. Zuckerberg has been writing nine-figure offers to poach top AI researchers, even as the rank and file describe drudgery and instability. Meta has pledged $600 billion in US infrastructure and jobs over three years and just signed fresh computing deals with data-center developer Crusoe for roughly 1.6 gigawatts of capacity. The money is flowing to chips and concrete, not necessarily to the day-to-day experience of the people doing the work.

For the diaspora, that paradox is the story. The compensation that drew a generation of Indian engineers to Menlo Park is still there. The sense of building something meaningful, the thing that made the long hours and the visa anxiety worth it, is what employees say is fraying.

## What to watch

The tell will be attrition data and the next H-1B filing season. If Meta's senior Indian engineers begin quietly moving to Nvidia, OpenAI, Anthropic or back to India's booming GCC sector, the morale problem becomes a talent problem. Zuckerberg's no-more-layoffs pledge buys time. Whether it buys loyalty from a workforce that cannot easily leave is the question that will define Meta's AI push through the rest of 2026."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Adobe Is Giving Its Software Away. Shantanu Narayen's Parting Bet Is a 90-Million-User Gamble.",
        "subheadline": "On his way out after 18 years, Adobe's CEO paused Creative Cloud price hikes and went all-in on freemium AI. The diaspora's engineers and creators are watching where the budget flows.",
        "slug": make_slug("adobe-shantanu-narayen-freemium-firefly-creative-cloud-price-nri-creators"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Adobe is a major employer of Indian engineers and a core tool for the diaspora's creators and founders; a free-first AI strategy reshapes what gets built, who gets hired, and the cost of starting a content business.",
        "tags": ["adobe", "shantanu-narayen", "ai", "indian-tech-leaders", "firefly", "silicon-valley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/adobe-inc-adbe-accepts-a-tradeoff-to-drive-business-growth-1648321/"},
            {"name": "The Register", "url": "https://www.theregister.com/2026/03/13/adobe_ceo_shantanu_narayen_steps_down/"},
            {"name": "CMSWire", "url": "https://www.cmswire.com/digital-experience/adobe-doubles-down-on-agentic-ai-at-summit-2026/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/01/Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg",
        "image_caption": "Shantanu Narayen, chairman and CEO of Adobe Inc., who is leaning into freemium AI products on his way out after 18 years.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": adobe_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An IIT Madras Engineer Just Raised $27 Million to Make AI Prove It's Right",
        "subheadline": "Pramaana Labs, led by Khosla Ventures, is betting the next AI bottleneck isn't fluency but accountability. The founder and the backers are a map of the India-US tech corridor.",
        "slug": make_slug("pramaana-labs-27-million-seed-khosla-ai-formal-verification-iit-madras-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "A diaspora founder, ex-Google and IIT Madras, backed by India-US venture firms, is building 'verifiable AI' — exactly the hard, defensible skill that protects Indian engineers as AI hollows out middle-tier coding roles.",
        "tags": ["pramaana-labs", "khosla-ventures", "ai", "indian-founders", "startups", "venture-capital"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "GlobeNewswire", "url": "https://www.globenewswire.com/news-release/2026/06/18/pramaana-labs-raises-27m-led-by-khosla-ventures.html"},
            {"name": "The Tech Portal", "url": "https://thetechportal.com/2026/06/18/pramaana-labs-seed-funding-khosla-ventures/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/270623/pexels-photo-270623.png?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Lines of code on a screen; Pramaana Labs applies formal verification to make AI answers mathematically provable.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": pramaana_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Meta's AI Dream Job Has Turned 'Soul-Crushing.' For Indians on H-1B, Quitting Isn't an Option.",
        "subheadline": "Drudgery, a keyboard-monitoring petition and a no-more-layoffs pledge expose a two-tier workforce — where citizens can walk and visa holders can't.",
        "slug": make_slug("meta-ai-unit-morale-soul-crushing-h1b-indian-engineers-zuckerberg-retention"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indians are ~72% of H-1B holders and fill Meta's engineering ranks; a morale crisis hits them differently because the 60-day visa clock turns 'I'd quit' into 'I can't leave.'",
        "tags": ["meta", "h1b", "indian-engineers", "ai", "tech-jobs", "silicon-valley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "New York Post", "url": "https://nypost.com/2026/06/15/business/metas-ai-unit-turns-into-soul-crushing-real-world-hell/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-signs-new-ai-computing-deals-with-data-center-firm-crusoe-2026-06-18/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Meta_HQ_2023.png/1280px-Meta_HQ_2023.png",
        "image_caption": "Meta's headquarters in Menlo Park, California, where AI teams are reporting 'soul-crushing' working conditions.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": meta_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  [{art['slug']}] words={wc}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
