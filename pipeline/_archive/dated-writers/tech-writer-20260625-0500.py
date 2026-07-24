#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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
        "headline": "Accenture Beat on Profit and Still Fell 7%. The Reason Is the One Job Indians Do Most for It.",
        "subheadline": "The consulting giant's revenue missed and it trimmed its full-year outlook — as the same AI it is selling clients starts eating the advisory work that built its India headcount.",
        "slug": make_slug("accenture-q3-earnings-ai-consulting-cannibalization-india-workforce-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Accenture employs more people in India than in any other country — over 300,000 — so when its consulting demand softens and AI starts replacing advisory billable hours, the squeeze lands first on the Indian and Indian-American professionals who staff its delivery centers and US client teams.",
        "tags": ["accenture", "ai", "it-services", "indian-tech", "layoffs", "earnings"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Zacks – ACN Q3 Earnings Call", "url": "https://www.zacks.com/stock/news/accenture-q3-earnings"},
            {"name": "Traders Union – Accenture pullback", "url": "https://tradersunion.com/news/accenture-q3-2026"},
            {"name": "MarketBeat – Accenture Earnings", "url": "https://www.marketbeat.com/stocks/NYSE/ACN/earnings/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Accenture_office_building_in_Gachibowli_%28August_2019%29.jpg/1280px-Accenture_office_building_in_Gachibowli_%28August_2019%29.jpg",
        "image_caption": "Accenture's office building in Gachibowli, Hyderabad, one of its largest delivery hubs in India",
        "image_attribution": "Wikimedia Commons",
        "body": """Accenture did the thing companies are supposed to be rewarded for. On June 18 it reported fiscal third-quarter earnings of $3.80 a share, beating the $3.70 analysts expected, generated $3.6 billion in free cash flow, raised its dividend 10%, and handed shareholders $2.2 billion through dividends and buybacks. The stock fell nearly 7%.

The market was not reading the profit line. It was reading two other numbers: revenue of $18.72 billion that missed consensus by a hair, and a full-year growth outlook the company quietly trimmed to 3-4%. For a firm whose entire pitch is that it helps the world's biggest companies reinvent themselves, slowing growth and weaker bookings are the only numbers that matter. And the reason they are slowing is the most uncomfortable one possible for Accenture.

## The product is starting to eat the business

On the earnings call, management's framing was almost philosophical: clients, they said, are moving from *using* AI to *running on* AI, with 100 new advanced AI projects in the quarter. That sounds like demand. But the same shift is hollowing out the work that fills Accenture's timesheets. A large slice of the company's revenue has always come from people — consultants billing hours to design systems, migrate data, and manage processes. When a bank can hand that work to an AI agent, it needs fewer Accenture bodies on site.

CFO Angie Park acknowledged the friction directly, pointing investors toward execution in cybersecurity, mid-market expansion, and a deliberate push toward "platform and non-FTE revenue" — corporate language for *making money from something other than headcount*. Late-quarter disruption in the Middle East and delayed managed-services awards widened the range of possible fourth-quarter outcomes, but the structural story underneath is the one diaspora professionals should watch.

## Why this lands hardest on Indians

Accenture employs more people in India than anywhere else on earth — north of 300,000, far more than its US staff. Its Bengaluru, Hyderabad, Chennai, and Pune delivery centers are the engine room of the entire company, and its US client-facing teams are thick with Indian-American managers and H-1B and L-1 visa holders who shuttle between the two.

When Accenture says it wants more revenue from platforms and less from full-time-equivalent labor, that is not an abstraction in Dublin or New York. It is a direct statement about the kind of work that has employed hundreds of thousands of Indian engineers for two decades. The "pyramid" model — armies of junior staff doing the repetitive build-and-maintain work, supervised by a thin layer of partners — is exactly what generative AI is best at compressing.

For the NRI watching from New Jersey or the Bay Area, there are two distinct exposures here. The first is career: if you are a consultant or delivery lead whose value was running large teams through predictable projects, the ground is shifting under that role across the entire IT-services sector, not just Accenture. The second is portfolio: Accenture is a bellwether. TCS, Infosys, Wipro, HCLTech, and Cognizant — the firms that employ even more of the diaspora's relatives back home and tens of thousands on US visas — sell the same labor-heavy services and face the same compression. Accenture reports earlier and cleaner than most of them, which is why its stock just told you what the Street thinks is coming.

## What's next

Accenture's bet is that it can pivot fast enough — buying its way into platform and software revenue through acquisitions, leaning into cybersecurity and high-end AI strategy work that machines can't yet do, and reskilling its workforce toward agent-orchestration rather than manual delivery. Management insists the appetite for "large-scale reinvention" is intact, and on the evidence of 100 new AI engagements, demand for *help with AI* is real.

The open question is whether that higher-value work can grow fast enough to replace the volume of routine labor it displaces — and whether the Indian professionals who built the old model get reskilled into the new one or simply counted out of it. The next read comes from the Indian IT majors' own results in the coming weeks. If they echo Accenture's trimmed guidance and soft bookings, the diaspora's single largest employment base is entering a genuinely new phase."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Meta Just Made AI Glasses Cheap Enough to Go Mass-Market. The First Test Will Be the Indian Diaspora's Wishlist.",
        "subheadline": "At $299 and running Meta's first in-house Superintelligence model, the new Meta Glasses drop the price barrier — and put a camera-and-AI face computer within reach of the NRI early adopter.",
        "slug": make_slug("meta-ai-glasses-299-muse-spark-superintelligence-nri-wearables"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-Americans are among the heaviest early adopters of AI gadgets and the most frequent international travelers and video-callers home — exactly the use cases (live translation, hands-free capture) Meta is selling — making the diaspora a natural first market for a sub-$300 AI wearable.",
        "tags": ["meta", "ai", "smart-glasses", "wearables", "muse-spark", "consumer-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters (via WIXX)", "url": "https://www.wixx.com/meta-cheaper-ai-smart-glasses-299"},
            {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com/tech/meta-lower-cost-ai-smart-glasses-299"},
            {"name": "Current India", "url": "https://currentindia.com/meta-smart-glasses-kylie-jenner-cheaper-ray-ban"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Ray-Ban_Meta_Gen_1_smart_glasses_with_charging_case.jpg/1280px-Ray-Ban_Meta_Gen_1_smart_glasses_with_charging_case.jpg",
        "image_caption": "Meta's Ray-Ban smart glasses with charging case, the predecessor to the new lower-cost Meta Glasses line",
        "image_attribution": "Wikimedia Commons",
        "body": """Meta has spent years and billions of dollars trying to convince people that a camera and an AI assistant belong on your face. On June 23 it removed the last obvious objection: price. The new range, simply called Meta Glasses, starts at $299 — roughly ₹28,000 — undercutting the cheapest Ray-Ban Meta model by about $80 and sitting far below the $800 Ray-Ban Display glasses launched last year.

This is also the first time Meta has shipped smart eyewear under its own name rather than borrowing Ray-Ban's or Oakley's. Built with EssilorLuxottica, the lineup comes in three frame styles — the rectangular Adventurer, the bolder Fury, and a slim oval "Meta Glasses by Kylie" co-designed with Kylie Jenner — across 26 frame-and-lens combinations, with a premium Starfire edition at $399.

## What's actually new

The hardware story is familiar: no display, but a built-in camera, open-ear speakers, multiple microphones, prescription-lens support through a new Rx swap program, and over eight hours of battery. You talk to it; it answers, translates conversations in real time, identifies what you're looking at, and captures photos and video hands-free.

The genuinely new part is the brain. These are the first Meta glasses to run Meta AI powered by **Muse Spark** — the first model out of the company's Superintelligence Labs. Until now, Meta's wearables leaned on the same assistant tech as its apps. Putting a purpose-built, in-house model on the device is Meta signaling that glasses, not phones, are where it intends to win the AI-hardware race. The numbers give it a running start: global smart-glasses shipments hit 9.6 million units last year, and Meta accounted for about 76% of them, according to IDC. A week earlier, Snap launched true augmented-reality glasses at $2,195 — a reminder that Meta's strategy is the opposite, trading the display for a price ordinary people will pay.

## Why the diaspora is the obvious first market

Strip away the celebrity launch and look at the three headline features: live translation, hands-free capture, and an always-available AI assistant. It is hard to design a product more precisely aimed at the Indian diaspora's daily life.

Consider the NRI who flies to Mumbai or Hyderabad twice a year and navigates relatives, vendors, and bureaucracy in a mix of Hindi, Telugu, Tamil, and English. Real-time translation in your ear is not a gimmick for that person; it is genuinely useful. Consider the parent who wants to record a child's first steps or a grandparent's blessing over video without holding up a phone. Consider the engineer in Sunnyvale or Edison who already owns the AirPods, the Oura ring, and the standing desk — the textbook early adopter Meta needs to seed the category. Indian-Americans over-index on exactly this profile: high household tech spend, heavy international calling, and a cultural premium on staying connected across continents.

The diaspora connection runs deeper than the customer base. Meta's hardware and AI org is thick with Indian-origin engineers and managers, and the Reuters team that broke the launch filed it from Bengaluru — a small marker of how much of Meta's product and reporting orbit now runs through India. And in a neat twist that landed the same week, Meta named CRED founder Kunal Shah to run WhatsApp after a $900 million investment, putting an Indian founder in charge of the app that is itself the diaspora's lifeline home. The face computer and the messaging app it will eventually plug into are increasingly being built and led by the same community that will buy them first.

## The catch

Two cautions. First, the obvious one Meta would rather you not dwell on: this is a camera you wear on your face, owned by a company whose business is data. A cheaper price means more of them in more rooms, and the privacy questions that dogged earlier models do not get smaller at scale. Second, India availability and pricing for the full lineup remain unconfirmed at launch — the $299 figure is US pricing, and Meta's wearables have historically reached India late and marked up. For now, the diaspora member most likely to be wearing a pair this summer is the one who lives in California or London, not Bengaluru.

Still, the threshold has moved. A face-worn AI device with a credible in-house model now costs less than a mid-range phone. Whether that turns smart glasses from a gadget into a habit will be decided by exactly the kind of connected, mobile, gadget-hungry users the diaspora is full of."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Wall Street Bank Just Told India Its AI Is a 'Fighter Jet' It Doesn't Own. The Warning Is a Gift to the Diaspora's Startups.",
        "subheadline": "Bernstein says India risks running its banks, defense and government on foreign AI models that could be switched off in a crisis — and the case for homegrown 'sovereign AI' has never paid off faster for founders like Sarvam.",
        "slug": make_slug("bernstein-india-foreign-llm-dependence-sovereign-ai-fighter-jet-warning"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The sovereign-AI push is creating a new class of Indian deep-tech companies — many founded or funded by returning diaspora technologists — and the geopolitical risk Bernstein flags (foreign AI access cut overnight) is precisely the same export-control logic the US just used against Anthropic, making this a live investment and career thesis for NRIs in AI.",
        "tags": ["sovereign-ai", "india-ai", "sarvam", "deep-tech", "geopolitics", "llm"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint – Naukri founder AI bets", "url": "https://www.livemint.com/companies/news/info-edge-ai-startup-portfolio-sarvam"},
            {"name": "IBS Intelligence – Sarvam unicorn", "url": "https://ibsintelligence.com/ibsi-news/sarvam-ai-attains-unicorn-status-234m"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17489157/pexels-photo-17489157.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Rows of servers in an AI data center, the compute backbone behind large language models",
        "image_attribution": "Pexels",
        "body": """Brokerages do not usually reach for military metaphors. So when Bernstein, in a note to investors this week, compared artificial intelligence to "fighter jets" — strategic assets that can be subject to export controls — it was making a deliberately blunt point about India. The country, the bank warned, risks becoming dependent on foreign AI systems unless it builds its own large language models.

"India's core intelligence layer, from enterprise software to defence and space, could be powered by foreign LLMs," the report said. "Enter a geopolitical disruption, and that access could be curtailed overnight."

A few weeks ago that would have read as analyst hand-wringing. It does not anymore, because the exact scenario Bernstein describes just happened to someone else.

## The warning that stopped being hypothetical

Washington recently moved to cut foreign nationals off from Anthropic's most capable models — the kind of access restriction that, applied at national scale, is precisely the "switched off overnight" risk India runs if its banks, hospitals, courts, and defense systems are quietly wired to American or Chinese models. An LLM is not a one-time purchase like a server. It is a service, delivered from someone else's cloud, governed by someone else's government. If the foundation of your economy's "intelligence layer" sits behind a foreign export-control regime, you have built a skyscraper on rented land.

That is the case for what India calls **sovereign AI**: models trained in India, on Indian languages and data, hosted on Indian infrastructure, that no foreign authority can revoke. For years it sounded like protectionist ambition. Bernstein's note reframes it as basic risk management.

## The diaspora is already building the answer

The timing could hardly be better for a specific group of founders — and many of them are diaspora technologists who came home to build. Last week, **Sarvam AI** became India's first sovereign-AI unicorn, raising $234 million at a $1.5 billion valuation in a round led by HCLTech's $150 million strategic cheque, with Bessemer Venture Partners joining existing backers Khosla Ventures and Peak XV. Sarvam's full-stack platform — model, inference infrastructure, and enterprise apps, built for Indian languages and already deployed in banking, insurance, government, and defense — is the literal embodiment of what Bernstein says India needs. The company handles more than two million interactions a day and processes around 10 million API calls.

It is not alone. Info Edge, the Naukri founder's investment vehicle, has quietly poured ₹1,003 crore across 54 startups, including IndiaAI Mission–selected voice-AI firm Gnani.ai. The government is funding compute access for chosen startups through that mission. IIT Madras and Unicorn India just announced a ₹600 crore deep-tech fund. The capital, the policy, and the geopolitical justification are converging at once.

## Why an NRI should care

Two reasons, one practical and one financial.

Practically, sovereign AI is becoming one of the most credible reasons for a senior AI researcher or ML engineer in the US to consider an India move — or at least an India bet. For a decade the "return to India" pitch struggled against the reality that the frontier work, the compute, and the pay were all in California. Sovereign AI changes the pitch: there is now mission-driven, nationally strategic, well-funded work being built at home, and it specifically values people who trained at the labs and companies the diaspora populates. Sarvam's lead investor is HCLTech; its co-founder Vivek Raghavan talks about diffusing the technology across citizens, small businesses, and government. That is a different kind of job than optimizing ad click-through.

Financially, this is an emerging-thesis the diaspora can actually access. Indian deep-tech is moving from a curiosity to a category with strategic-investor validation (HCLTech, Bessemer, government grants) and a clear macro tailwind that a major Wall Street bank just underlined in public. Sriram Viswanathan of Celesta Capital expects India's deep-tech startups to attract materially higher capital over the next 12 months as the ecosystem matures.

The risk Bernstein flagged is real, and so is the caveat: building sovereign LLMs that match the frontier is brutally expensive, and India is starting years behind on compute. Homegrown models may end up "good enough for India" rather than world-beating — which, for a country that wants to control its own intelligence layer, may be exactly the point. For the diaspora technologist deciding where the next decade of interesting, consequential AI work will happen, the answer just got a little less obvious — and a little more interesting."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
