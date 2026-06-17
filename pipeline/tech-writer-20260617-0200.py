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
        "headline": "Washington Told Anthropic to Cut Off Foreigners. Now India Is Asking Who Really Owns the AI It Runs On.",
        "subheadline": "A U.S. government directive that locked non-citizens out of Anthropic's newest models has set off a sovereign-AI reckoning in Bengaluru — and a quiet warning for every Indian engineer building on a borrowed brain.",
        "slug": make_slug("anthropic-foreign-national-suspension-india-sovereign-ai-debate"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For Indian engineers in the U.S. on visas and the Bengaluru teams that serve American startups, the episode is a blunt reminder that access to the AI models their jobs depend on can be revoked by a government directive overnight.",
        "tags": ["ai", "anthropic", "sovereign-ai", "indian-tech", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/13/as-anthropic-suspends-access-to-new-models-india-debates-its-ai-future/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
        "image_caption": "Anthropic CEO Dario Amodei, whose company suspended access to its newest models for foreign nationals after a U.S. government directive.",
        "image_attribution": "Wikimedia Commons",
        "body": """A late-Friday announcement from Anthropic did something no Indian policy white paper had managed in years: it made sovereign AI feel urgent.

The company said it had received a U.S. government directive requiring it to suspend access to its two newest models, Fable 5 and Mythos 5, for all foreign nationals — including its own foreign-national employees. The timing was almost cruel. Days earlier, Anthropic had announced a partnership with Tata Consultancy Services to push enterprise AI adoption across India, a country both Anthropic and OpenAI have repeatedly called their second-largest market after the United States.

For the Indian American engineer reading this between standups, the abstract suddenly turned concrete. If you are on an H-1B at a startup whose product runs on Claude, and a directive can wall off the model from anyone who is not a U.S. citizen, your roadmap is now hostage to a policy you have no vote in.

## "It completely changes things"

Aakrit Vaish, who runs the Indian AI venture platform Activate, told TechCrunch he woke up "shocked and confused." His takeaway was not panic but strategy: "I think this materially changes the way all of us should be thinking about sovereign AI in India." He now plans to push his portfolio companies toward open-source models and away from dependence on a handful of American frontier labs.

Vijay Rayapati, CEO of Atomicwork — roughly 25 employees in the U.S., much of its engineering in Bengaluru — put the competitive stakes plainly. "If your AI team is not made up entirely of U.S. citizens, you are at a competitive disadvantage." That sentence should land hard for the diaspora. The entire economic logic of the Indian engineer abroad has been that talent is borderless. A model-access rule keyed to passport color says otherwise.

## The pile-on

Zoho founder Sridhar Vembu, long a sovereign-tech evangelist, said the move proved "technology is the ultimate weapon," and urged Indian organizations to adopt smaller open-source models — Indian and Chinese alike. Former Infosys CFO and investor Mohandas Pai went bigger, calling for an annual ₹500 billion ($5 billion) AI fund and a ₹2 trillion credit-guarantee program for compute and chips. For scale: India's existing IndiaAI Mission is budgeted at about $1.2 billion over five years. Pai wants roughly four times that, every year.

Not everyone agreed money is the bottleneck. Lightspeed partner Hemant Mohapatra argued the real constraints are talent, compute access, and execution — not the size of a government check. It is a familiar Bengaluru-versus-Delhi argument: the founders say "let us build," the policy crowd says "fund the mission."

## Why an NRI should care

Three reasons, in descending order of how fast they will touch you.

First, jobs. If frontier-model access becomes citizenship-gated, U.S. companies have a new incentive to keep their most AI-dependent work on American-citizen teams. That is a structural headwind for the visa-holding engineer, separate from the H-1B fee fights already roiling Washington.

Second, your startup equity. If you angel-invest in or work at an Indian AI company, the open-source pivot Vaish describes is now the safer architecture. Companies hard-wired to a single U.S. lab carry a geopolitical single point of failure that did not exist on paper a week ago.

Third, the long game. Policy expert Prasanto Roy compared the episode to countries learning the hard way about dependence on SWIFT after Russia's 2022 cutoff. "Even if this is corrected or reversed," he said, "the Anthropic episode shows there's no such thing as a geopolitically neutral foreign LLM. American AI models are bound to American geopolitics."

The White House, for its part, has reportedly signaled it is unlikely to extend the restriction to other labs and is privately blaming Anthropic's handling of alleged jailbreak vulnerabilities. Anthropic disputes the framing and says the action should not have been taken. The directive may yet be softened or reversed.

But the lesson has already been absorbed in Bengaluru, and it is the kind that does not un-learn. India's AI ecosystem has spent three years building on top of other people's models. The question now being asked in founder WhatsApp groups from Indiranagar to Jersey City is no longer whether that was efficient. It is whether it was ever safe."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Tesla Just Handed Indian Families a Six-Seat EV. The Price Tag Tells You Who It's Really For.",
        "subheadline": "Deliveries of the three-row Model Y L have begun in India at ₹62 lakh, with a cheaper rear-wheel-drive variant landing in July — Tesla's clearest signal yet that it is chasing the affluent urban family, not the mass market.",
        "slug": make_slug("tesla-model-y-l-india-deliveries-six-seater-ev-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs weighing a return to India or buying a car for family back home, Tesla's pricing puts a familiar American badge within reach of the upper-middle class — but at a premium that reframes what 'affordable EV' means in India.",
        "tags": ["tesla", "ev", "india", "electric-vehicles", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "LatestLY / ANI", "url": "https://www.latestly.com/"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Tesla_Model_Y_2025_at_Santana_Row_dllu_02.jpg/1280px-Tesla_Model_Y_2025_at_Santana_Row_dllu_02.jpg",
        "image_caption": "A 2025 Tesla Model Y; Tesla has begun delivering the six-seat Model Y L variant to customers in India.",
        "image_attribution": "Wikimedia Commons",
        "body": """Tesla has started handing Indian customers the keys to its six-seater Model Y L, and the most interesting thing about the car is not its 681-kilometre range. It is the ₹61.99 lakh sticker, which quietly answers a question Indian buyers have asked since Elon Musk first flirted with the market: who, exactly, is a Tesla for in India?

The answer, for now, is the urban professional family with money to spend and a garage to charge in. The three-row Model Y L is the flagship of the India range, with six individual seats, up to 2,539 litres of cargo, and a 0-100 km/h time of 5.0 seconds. A cheaper Model Y Premium Rear-Wheel Drive follows in July at ₹50.89 lakh, with 500 km of range. EMIs start around ₹49,990 and ₹39,990 a month respectively, on down payments north of ₹6 lakh.

For context on what those numbers mean: this is not a mass-market play. It sits squarely against the BYD Sealion 7, Kia EV6, BMW iX1 and Volvo EC40 — premium metal, not the Nexon EV territory where most Indian EV volume actually lives.

## Why the diaspora is watching this one closely

There are two NRI audiences here, and they want different things.

The first is the returnee. If you have spent a decade in the Bay Area or New Jersey driving a Tesla and you are weighing a move back to Bengaluru, Mumbai or Delhi, the Model Y L removes a small but real friction: you no longer have to give up the badge, the app, or the one-pedal driving you got used to. Tesla is selling direct-to-consumer, the same model NRIs know from the U.S., and the first showroom is slated for BKC in Mumbai. The ownership experience is being deliberately ported, not reinvented.

The second is the investor. For the diaspora tracking Indian auto stocks, Tesla's arrival is less a threat to Tata Motors and Mahindra than a validation of the premium-EV thesis. India's broader EV expansion kicked off June 15 with 16 EV launches against just 7 new combustion models over the coming cycle — Tata's acti.ev+, Mahindra's INGLO, BYD, and MG's SIGMA architecture all pushing dedicated electric platforms. Tesla entering at the top of the price band does not crater that market; it anchors aspiration above it. The mass-market fight stays with the Indian incumbents.

## The catch nobody puts in the brochure

The Model Y L is imported, and that is the whole story behind the price. Until Tesla localizes — and there is still no committed India factory — these cars carry the weight of India's auto import duties. The ₹62 lakh you pay in Mumbai buys roughly a $45,000 car in California. That gap is tariff, not technology.

That is also why the running soap opera between Washington and New Delhi matters. Tesla's India pricing is hostage to an unresolved trade conversation on import taxes, the same tariff file that Musk and Prime Minister Modi have discussed by phone. Musk has said he is "looking forward to visiting India later this year." If a deal lowers duties, the next Tesla price cut could be steep. For an NRI considering a purchase for parents back home, that is a real reason to ask how much patience your budget has.

## The status symbol that charges overnight

There is a cultural read here too. In much of urban India, the car remains a loud statement of arrival, and for the returning diaspora professional, a Tesla in the porch says something specific — global, technical, a little contrarian. Even a curiosity like Gujarat's first imported Cybertruck, shipped in privately from Dubai, shows the appetite is real before the showrooms are.

Tesla is betting that appetite extends to a six-seat family hauler. The Model Y L is engineered for the joint-family weekend run to the hill station as much as the Monday commute. Whether ₹62 lakh is the right price for that fantasy is now a question being answered one delivery at a time — and the answer will tell Tesla, and every NRI watching from abroad, just how deep India's premium EV market really goes."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America Is About to Get Its First Real AI Law. It's Not Coming From Washington — and That's the Problem.",
        "subheadline": "Colorado's AI Act takes effect June 30 and California's follows in August, even as Congress floats a bill to freeze state rules for three years. For the Indian engineers building the systems, the patchwork is now a compliance headache with their name on the commit.",
        "slug": make_slug("colorado-california-state-ai-laws-patchwork-indian-engineers-compliance"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-American engineers and founders building AI products now face a state-by-state thicket of discrimination and disclosure rules — turning algorithmic fairness from an abstract debate into code, audits, and legal exposure they personally have to ship.",
        "tags": ["ai", "ai-regulation", "colorado", "indian-tech", "silicon-valley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "After The Update (industry newsletter)", "url": "https://www.linkedin.com/"},
            {"name": "Colorado AI Act coverage", "url": "https://www.dev.to/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29500749/pexels-photo-29500749.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A courthouse facade; new U.S. state AI laws create fresh legal exposure for the engineers who build high-risk AI systems.",
        "image_attribution": "Pexels",
        "body": """On June 30, the most consequential AI law in the United States takes effect, and it was not written in Washington. It was written in Denver.

Colorado's AI Act — the first comprehensive state statute targeting high-risk AI systems — requires developers and deployers to exercise "reasonable care" to prevent algorithmic discrimination, to conduct impact assessments, and to give consumers disclosures when an AI system makes a consequential decision about them. California's AI Transparency Act follows on August 2. Together they mark the moment AI regulation in America stopped being a panel-discussion abstraction and became something an engineer has to implement.

That engineer, more often than not in Silicon Valley, is Indian.

## Why this is a diaspora story, not a policy story

Walk the floor of any AI team at a mid-size U.S. SaaS company and you will find Indian-origin engineers and managers carrying the build. When a "reasonable care" standard lands on a hiring-screening model or a lending algorithm, it does not stay in the legal department. It becomes a Jira ticket. Someone has to define what bias testing means in code, instrument the impact assessment, wire up the consumer disclosure, and own the audit trail when a regulator or a plaintiff's lawyer comes asking.

For the diaspora professional, this is a double-edged shift. The downside is obvious: more compliance scaffolding, more documentation, slower shipping, and personal proximity to legal risk that used to live far away from the IDE. The upside is quieter but real. "AI governance engineer" and "responsible-AI lead" are becoming line items on org charts, and the people who already understand both the model internals and the fairness requirements are well positioned to claim them. Compliance, annoyingly, is also a career.

## The patchwork is the point

Here is the part that should worry founders. There is no single American AI law. There is Colorado's, then California's, with more states drafting their own. A startup selling nationwide may soon have to satisfy a dozen overlapping definitions of "high-risk," "consequential decision," and "algorithmic discrimination." For a lean team — and many of the leanest AI teams have heavy Bengaluru engineering components — that fragmentation is a tax measured in engineering hours nobody budgeted.

Congress sees the problem and has floated a fix that creates a different one. The proposed Great American AI Act would preempt state AI-development rules for three years to give the federal government room to write a national standard. Colorado's law takes effect just 26 days after that federal bill was released — a near-perfect illustration of the collision. Build to the state rules now, and a federal preemption could moot the work. Wait for Washington, and you are non-compliant in Denver on June 30. There is no clean answer, only exposure management.

## What the Bay Area and New Jersey engineer should actually do

Three practical moves come out of this.

First, if you are building anything that touches hiring, lending, housing, healthcare or insurance — the classic "high-risk" buckets — assume Colorado's standard applies to your roadmap now, not at some future compliance offsite. Impact assessments are easier to design in than to retrofit.

Second, treat disclosure as a product feature. The laws want consumers told when AI made a consequential call about them. Teams that bolt this on after launch end up with ugly modals and angry users; teams that design it in turn it into a trust signal.

Third, watch the preemption fight the way you would watch a framework migration. If the federal bill advances, the smart engineering posture is modular compliance — abstractions you can re-point from a state standard to a federal one without rewriting the core.

None of this is the glamorous part of AI. There is no demo, no benchmark, no launch tweet. But for the thousands of Indian-origin engineers who write the systems that now sit inside the blast radius of these laws, the message from Denver is simple. The era where someone else worried about whether the model was fair is over. Starting June 30, that someone is you."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art["body"].split())
        print(f"✅ {art['slug']}  ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
