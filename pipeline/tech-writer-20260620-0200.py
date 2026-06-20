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

body1 = """The tech industry's 2026 cull crossed a grim milestone this month: by mid-June, trackers counted more than 183,000 jobs eliminated across roughly 250 separate layoff events — an average of over 1,100 cuts a day. The number is not a recession statistic. Hiring is steady elsewhere in the economy, jobless claims are low, and the companies doing the cutting are, by and large, profitable. What is shrinking is the headcount they believe they need now that artificial intelligence writes code, drafts contracts and answers support tickets.

For Indian engineers in the United States, the abstraction has a sharper edge. Indian nationals hold the largest single share of H-1B visas, and at least 15 of the 25 biggest H-1B sponsors in fiscal 2026 have announced significant reductions. Oracle cut some 30,000 roles globally in April. Meta shed roughly 8,000. Amazon and Microsoft have continued trimming across divisions. When a green-card holder loses a job, they have time to look around. When an H-1B worker is laid off, a 60-day clock starts — and it is more brutal than most realize.

## The 60-day trap, explained

The grace period under USCIS rules begins on the last actual day of employment, not when severance ends or HR finishes offboarding. Severance pay, COBRA coverage and "garden leave" do not extend status. A worker who assumes their three-month payout buys them three months of legal presence can quietly slide into unlawful presence, which can trigger a three- or ten-year re-entry bar. Within those 60 days, the options are narrow: find a new sponsoring employer willing to file a transfer, switch to another visa category, or leave.

That is why a small industry of immigration advisers has sprung up around the layoffs — survival guides, free consultations, EB-5 investor pitches promising a path to residency that does not depend on any single employer. The marketing is opportunistic, but the underlying anxiety is real. Tying your family's right to live in a country to one manager's reorg decision was always a gamble. In 2026 the house started winning more often.

## Why this lands hardest on Indians

The diaspora's exposure is structural. Decades of H-1B dependence built a generation of Indian professionals whose mortgages, children's schools and decade-long green-card queues are all anchored to continuous employment. For an Indian engineer stuck in the EB-2 or EB-3 backlog — where waits can stretch past a decade — a layoff is not a career setback, it is an existential threat to a life carefully assembled in New Jersey or the Bay Area.

There is a second-order effect, too. As US firms automate routine engineering and shift remaining work to global capability centres in Bengaluru and Hyderabad, the calculus of staying versus returning shifts. Some of the laid-off are not job-hunting in America at all; they are taking the reverse flight, betting that India's own AI build-out offers more durable ground.

## What's next

The legal weather is unsettled. A recent court ruling struck down a proposed six-figure H-1B entry fee, a relief for workers but a reminder that visa policy is now a live political battlefield heading into a contentious season. For Indian professionals, the practical advice from immigration lawyers is unglamorous but urgent: know your I-94 date, keep an updated résumé, maintain a financial cushion that survives a 60-day shock, and understand portability before you need it. The era when a good job at a brand-name company felt like a settled life is, for visa holders, over. Optionality is the new job security."""

body2 = """On a recent Tuesday in Nice, India's commerce minister stood inside Galeries Lafayette and paid for something with a phone. The transaction itself was trivial. The symbolism was not. India's Unified Payments Interface — the QR-code rail that processes more than 20 billion transactions a month at home — is now live in its ninth country, and the government is treating each new flag like a diplomatic win.

UPI is now accepted in Singapore, the UAE, France, Mauritius, Nepal, Bhutan, Qatar, Sri Lanka and Cambodia, with East Asian and Central Asian markets reportedly next. The model varies by country. In France it runs through local acquirer partnerships; in Malaysia, NPCI's international arm has signed a reciprocal deal so Indian travelers can scan DuitNow codes and Malaysians can eventually scan UPI codes. The ambition is no longer just convenience for tourists. It is to make an Indian-built public utility part of the world's payment plumbing.

## Why an NRI should care beyond the novelty

For the diaspora, the immediate appeal is obvious: the next trip to Paris or Dubai may not require fumbling for a card with foreign-transaction fees. But the deeper story is about what UPI represents — a piece of "digital public infrastructure" that India is exporting as soft power, and increasingly as a template other countries want to license rather than build from scratch.

That matters for NRIs who work in fintech, invest in it, or simply think about where India's economy is headed. UPI's overseas push is the visible tip of a larger play that includes Aadhaar-based identity, the ONDC open-commerce network and DigiLocker. Collectively, these are the rails that companies like PhonePe, Razorpay and Paytm ride — and several of those names are now lining up for public listings that NRI investors can access. Razorpay has filed confidentially. PhonePe is preparing. The global credibility of UPI is, indirectly, part of their valuation story.

## The hard part is monetization

There is a catch the cheerleading tends to skip. UPI is famously, deliberately near-free. That is wonderful for adoption and terrible for anyone hoping to make money moving the payments. Cross-border expansion adds settlement complexity, currency conversion and compliance costs without an obvious revenue model attached. NPCI's international subsidiary is signing agreements at a rapid clip, but turning diplomatic photo-ops into a self-sustaining business is the unsolved problem.

For now, the strategic value is doing the work. Every country that accepts UPI deepens India's case that its digital stack is a credible alternative to Western card networks — a pitch with particular resonance in the Global South, where many nations are wary of routing their citizens' payments through Visa and Mastercard.

## What's next

Watch East Asia, where officials have signaled the next wave of agreements, and watch whether reciprocity actually materializes — plenty of these deals let Indians pay abroad long before foreigners can pay in India. For the diaspora, the takeaway is twofold. As a traveler, your home payment app is slowly becoming a global one. As an investor or builder, the international footprint of UPI is a leading indicator for the Indian fintech companies preparing to ask the public markets for money. The phone tap in Nice was small. The bet behind it is not."""

body3 = """OpenAI does not usually share country-level numbers. So when the company confirmed that India makes up roughly 20 percent of ChatGPT's one billion monthly active users — more than 200 million people — it was less a data point than a declaration of strategy. India is no longer a promising secondary market for the world's most valuable AI startup. It is the engine.

The trajectory is steep. India's share of the ChatGPT base climbed from 11 percent in 2024 to 13 percent in mid-2025 to 20 percent now, even as the overall pie ballooned to a billion users. By Sensor Tower's count, ChatGPT sits far ahead of rivals globally — Gemini at 472 million, DeepSeek at 68 million, Meta AI at 61 million, Grok at 50 million — and India is doing a disproportionate amount of the lifting at the top of that list.

## A market won on price, not just enthusiasm

OpenAI did not stumble into this. It opened a New Delhi office, then re-engineered its pricing for a country that loves software but does not pay Silicon Valley prices for it. The sub-$5 "ChatGPT Go" tier was launched in India first and later made free for a year for Indian users — a land-grab that prioritizes scale over near-term revenue. The strategy works on adoption and fails, for now, on monetization: India generates enormous usage and modest dollars, a gap OpenAI is betting it can close as incomes and habits mature.

The deeper commitment came at the India AI Impact Summit, where OpenAI announced "OpenAI for India" and named the Tata Group as its anchor partner. As part of the Stargate infrastructure push, OpenAI will become the first customer of TCS's HyperVault data-center business, starting at 100 megawatts with room to scale toward a gigawatt. The point is sovereign capacity — running advanced models inside India to satisfy data-residency and government-workload requirements. Tata, in turn, plans to roll out ChatGPT Enterprise to hundreds of thousands of TCS employees, one of the largest corporate AI deployments anywhere.

## What it means for the diaspora

For Indian Americans, the story cuts two ways. For the engineer or founder, India's emergence as OpenAI's largest growth market makes it a serious place to build — the user base, the data-center investment and the enterprise contracts are all landing there, not just in California. The cross-border career, already common, gets another on-ramp.

For the worker, the same data carries a warning. The companies OpenAI is partnering with — TCS, HCLTech, Cognizant — are the IT-services giants that employ the diaspora's parents, cousins and former classmates. They are racing to sell "intelligence" instead of labor precisely because AI is eating the labor. Venture capitalist Vinod Khosla recently predicted India's $200 billion IT industry "will be gone" in its current form. ChatGPT's Indian boom and the IT sector's anxiety are the same phenomenon viewed from two ends.

## What's next

The numbers will keep climbing; OpenAI's executives have said India is on track to become its single largest market. The open questions are whether usage ever converts to meaningful revenue, whether the Tata data centers ship on schedule, and whether homegrown efforts like Sarvam AI can claim a sliver of the sovereign-AI market before the American incumbents lock it down. For the diaspora, the safe assumption is this: the AI tools reshaping work in San Jose and the ones reshaping it in Hyderabad are increasingly the same tools, built by the same company, trained on the same ambition."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Tech's 2026 Layoffs Just Passed 183,000. For Indians on H-1B, the Real Clock Is 60 Days.",
        "subheadline": "The cuts aren't a recession — they're an AI restructuring. And no group is more exposed to the fallout than Indian visa holders.",
        "slug": make_slug("tech-layoffs-2026-h1b-60-day-grace-indian-workers-ai-restructuring"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indians hold the largest share of H-1B visas, and a layoff triggers a brutal 60-day deadline to find a new sponsor or leave the US — making the 2026 AI-driven cuts an existential threat, not just a career setback.",
        "tags": ["h1b", "layoffs", "ai", "indian-tech", "immigration", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CSMPLT / EIN Presswire", "url": "https://www.einpresswire.com/"},
            {"name": "People Matters", "url": "https://www.peoplematters.in/"},
            {"name": "LatestLY", "url": "https://www.latestly.com/"},
            {"name": "Daily Caller", "url": "https://dailycaller.com/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7071/space-desk-office-workspace.jpg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An empty open-plan office, emblematic of the 2026 tech layoff wave across major US employers",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Switched On UPI in a Nice Department Store. It's Now in Nine Countries — and That's the Point.",
        "subheadline": "India's homegrown payment rail is becoming an export of soft power. For NRIs, it's both a travel perk and a tell on where Indian fintech is headed.",
        "slug": make_slug("upi-global-expansion-france-nine-countries-nri-fintech-digital-public-infrastructure"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "UPI's overseas rollout means NRIs can soon pay abroad with their home apps — but it's also a leading indicator for Indian fintech firms like Razorpay and PhonePe now lining up IPOs that diaspora investors can access.",
        "tags": ["upi", "fintech", "india-tech", "digital-payments", "nri-investors", "ondc"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
            {"name": "PR Newswire (NPCI International)", "url": "https://en.prnasia.com/"},
            {"name": "Mint", "url": "https://www.livemint.com/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12935064/pexels-photo-12935064.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A contactless QR-code payment made with a smartphone, the core of India's UPI system",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "One in Five ChatGPT Users Is Now Indian. OpenAI Just Told the World Where Its Future Is.",
        "subheadline": "India makes up 20% of ChatGPT's billion users — and OpenAI is pouring data centers and Tata partnerships into the market. The diaspora sits on both sides of the trade.",
        "slug": make_slug("chatgpt-india-200-million-users-openai-for-india-tata-stargate-diaspora"),
        "category": "technology",
        "vertical": "ai",
        "diaspora_angle": "India is becoming OpenAI's largest market, drawing data-center investment and enterprise deals that make it a serious place to build — even as the same AI boom threatens the IT-services jobs that employ much of the diaspora's network.",
        "tags": ["openai", "chatgpt", "ai", "india-tech", "tata", "sam-altman"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
            {"name": "OpenAI", "url": "https://openai.com/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/"},
            {"name": "Mint", "url": "https://www.livemint.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
        "image_caption": "OpenAI CEO Sam Altman, who has called India the company's fastest-growing market",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body3
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art['body'].split())
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
