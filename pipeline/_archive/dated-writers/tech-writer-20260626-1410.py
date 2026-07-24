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
        "headline": "OpenAI Just Hired Uber's India Boss to Run the Country. The Job Is Less About Code Than Conquest.",
        "subheadline": "Prabhjeet Singh, who spent a decade scaling Uber's India business, becomes OpenAI's most senior leader in a market it now treats as second only to the United States.",
        "slug": make_slug("openai-prabhjeet-singh-india-managing-director-uber-chatgpt"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For Indian engineers and founders, OpenAI building a real India org under a heavyweight operator signals jobs, India-specific pricing, and a faster pipeline of products that NRIs' families back home will actually use.",
        "tags": ["openai", "india", "ai", "indian-tech", "chatgpt"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/openai-taps-ex-uber-regional-chief-india-leadership-2026-06-26/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Smartphone_with_ChatGPT_app_%2852917381673%29.jpg/1280px-Smartphone_with_ChatGPT_app_%2852917381673%29.jpg",
        "image_caption": "A smartphone running the ChatGPT app, the consumer product OpenAI is racing to scale in India",
        "image_attribution": "Wikimedia Commons",
        "body": """OpenAI has found the person to run its most important market after America, and tellingly, it did not pick a researcher. On Friday the company confirmed that Prabhjeet Singh, who stepped down the same day as president of Uber's India and South Asia business, will join in September as Managing Director for India. He becomes the firm's most senior leader in the country.

The choice says a great deal about where OpenAI thinks the hard problems lie. Singh is not a model builder. He is an operator who spent a decade turning Uber from a battered, pandemic-hit business into one that logged 11.6 billion kilometres of rides across India in 2025. An IIT Kharagpur and IIM Ahmedabad graduate who came up through McKinsey, he will own consumer growth, enterprise adoption, partnerships, regulatory engagement and operations. He reports to Kiran Mani, the former JioStar executive OpenAI made its Asia-Pacific chief in June.

**Why a logistics man for an AI company**

OpenAI's India problem is not whether people will use ChatGPT. They already do, in enormous numbers. The problem is the one Uber knew intimately: how to convert a vast, price-sensitive, regulation-heavy market into durable revenue without torching cash. India is reportedly among ChatGPT's largest user bases by headcount, yet paid conversion lags the West by a wide margin. Singh's entire career has been about extracting steady business from exactly that kind of market, one rupee-conscious customer at a time.

The hire also fits a pattern. OpenAI has been stacking its India bench for months: Mani at the APAC helm, Meta veteran Pragya Mishra leading public policy, and new leaders across marketing, communications, enterprise and infrastructure. The company has said it plans to open a New Delhi office. This is no longer a sales outpost run from San Francisco. It is the scaffolding of a country business.

**The diaspora read**

For Indian-origin technologists, three things matter here. First, jobs. A senior MD with a mandate across enterprise and infrastructure means hiring, and OpenAI's India roles will compete directly with Google, Microsoft and Amazon for the same engineering and go-to-market talent. For an H-1B holder weighing whether to stay in the Bay Area or return, a credible OpenAI India org changes the math.

Second, pricing and product. Operators like Singh win in India by localising aggressively. Expect India-specific ChatGPT pricing, payment rails tuned to UPI, and features built for Indian languages and use cases. NRIs watching their parents fumble with English-only apps have a direct stake in whether OpenAI builds for Bharat or merely for metros.

Third, the competitive signal. OpenAI is planting a flag in a market where Google has spent years and billions, where Amazon just pledged another $13 billion, and where the government is building its own sovereign AI stack under the IndiaAI Mission. A heavyweight India MD is OpenAI's admission that it cannot win the country on model quality alone.

**The risk**

Singh inherits a delicate brief. India's draft AI governance framework is still taking shape, data-localisation pressure is real, and OpenAI faces an ongoing copyright suit in Delhi from a coalition of Indian news publishers. Regulatory engagement is explicitly in his remit, and it may prove the hardest part of the job. Uber spent years negotiating with transport authorities and state governments; OpenAI's fights will be over data, content and the terms on which a foreign AI company operates in a market determined to build its own.

There is also the question of expectations. Uber's India business took years to claw back to growth after FY21, when revenue nearly halved. AI adoption curves are steeper, but monetisation is murkier. Singh is being handed a market that loves the product and resists paying for it, wrapped in a policy environment that grows more assertive by the quarter.

**What's next**

Singh starts in September. Watch for an India pricing announcement, a formal office opening, and the shape of his leadership team, which will reveal whether OpenAI is building a consumer machine, an enterprise sales org, or both. For the diaspora, the deeper signal is simpler: the company at the centre of the AI boom now treats India not as a download statistic but as a country to be won, and it has hired a closer to do it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Amazon Just Promised India Another $13 Billion. The Real Story Is Who Gets to Own the Cloud Underneath the AI Boom.",
        "subheadline": "Andy Jassy's pledge takes Amazon's planned India spend to $48 billion through 2030, deepening a hyperscaler land grab that runs straight through Mumbai and Hyderabad.",
        "slug": make_slug("amazon-aws-13-billion-india-ai-cloud-jassy-modi-48-billion"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Every NRI engineer working on AWS, Azure or Google Cloud has a stake in whether India becomes a core hyperscaler hub, because it determines where the next decade of cloud and AI jobs, data residency, and India-built products actually live.",
        "tags": ["amazon", "aws", "india", "cloud", "ai", "data-centers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/amazon-invest-additional-13-billion-india-2026-06-25/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/25/amazon-ups-india-bet-with-fresh-13b-ai-infrastructure-investment/"},
            {"name": "Barron's", "url": "https://www.barrons.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/07/Andy_Jassy.jpg",
        "image_caption": "Amazon CEO Andy Jassy, who announced the additional $13 billion India investment after meeting Prime Minister Narendra Modi",
        "image_attribution": "Wikimedia Commons",
        "body": """Andy Jassy flew to New Delhi this week, sat down with Narendra Modi, and left behind a number: an additional $13 billion. With it, Amazon's planned investment in India climbs to $48 billion between 2026 and 2030, and its cumulative bet on the country since 2010 now tops $88 billion. The fresh money has one main destination, and it is not warehouses. It is data centres in Mumbai and Hyderabad.

This is the third India commitment Amazon has made in as many years, and each one has followed the same choreography: Jassy meets Modi, then announces a bigger figure. In 2023 it was $15 billion. In December 2025, $35 billion. Now $48 billion. Strip out the e-commerce and fulfilment spending and Amazon says more than $21 billion of that will go specifically into AI and cloud infrastructure through 2030.

**The hyperscaler land grab**

Amazon is not moving in a vacuum. It is sprinting against the same rivals it fights everywhere. Microsoft pledged $17.5 billion for India in December. Google said in October it would spend $15 billion building an AI hub and data-centre capacity in the south. Behind them, Reliance, Adani, Australia's AirTrunk and Canada's CPP Investments are all pouring money into Indian data-centre projects. India has become, in the industry's phrase, the next frontier for hyperscalers.

The logic is brutal and simple. AI runs on compute, compute runs on data centres, and data centres increasingly need to sit inside the country whose data and customers they serve. New Delhi has sweetened the deal with policy: tax exemptions for foreign cloud providers on services sold overseas, provided the workloads run from Indian soil. That single incentive reframes India from a cost-saving back office into a place where global AI can be both built and exported.

**Why the diaspora should care**

For Indian-origin technologists abroad, the abstraction resolves into something concrete: where the jobs are. AWS revenue grew 28% year over year last quarter to $37.6 billion, its fastest pace in years, and Amazon's full-year 2026 capital expenditure plan runs to roughly $200 billion. When a company spends at that scale and points a growing share at India, it is also pointing its hiring there.

That matters to an NRI engineer at AWS in Seattle weighing a transfer to Hyderabad, to a cloud architect in New Jersey watching India regions fill out, and to founders whose startups now get access to custom AI chips and managed AI services without leaving the country. The promise of the AWS, Microsoft and Google build-out is that an Indian developer no longer has to emigrate to work on frontier infrastructure. The frontier is being poured in concrete outside Mumbai.

**The catch**

There are two. First, money is not capacity. Amazon declined to break down exactly how the $48 billion splits across data centres, fulfilment, content and operating costs, and long-term corporate pledges routinely blend capital and operating spend. A headline number is a statement of intent, not a finished facility.

Second, the buildout is increasingly financed by debt. A Wall Street Journal analysis this week pegged nearly $160 billion of the $850 billion in hyperscaler and neocloud capex this year as debt-funded. Amazon faces real cash-flow pressure as it races Microsoft and Google, and the India spend lands inside that strain, not outside it. If AI demand softens, the data centres in Mumbai and Hyderabad become very expensive bets.

**What's next**

Watch for the physical milestones: when the new Mumbai and Hyderabad capacity actually comes online, how many India-region AI services launch, and whether Amazon discloses a real jobs figure rather than a dollar one. The deeper contest is over who owns the layer beneath India's AI boom. Amazon, Microsoft and Google are each betting tens of billions that it will be them. For the diaspora, the prize is not abstract. It is the question of whether the next decade of cloud careers gets built in Hyderabad or somewhere a visa away."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Qualcomm Spent $4 Billion on Software That Speaks Every Chip's Language. The Target Is Nvidia's Walled Garden.",
        "subheadline": "The $3.92 billion all-stock purchase of Modular is Cristiano Amon's clearest bet yet that Qualcomm's future is in data centres and AI software, not just the phone chips that built it.",
        "slug": make_slug("qualcomm-modular-4-billion-ai-software-nvidia-data-center-amon"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian engineers dominate Qualcomm's design centres in Hyderabad, Bengaluru and Chennai, so a pivot from smartphone chips into data-center AI reshapes the work and the career ladder for tens of thousands of them.",
        "tags": ["qualcomm", "ai-chips", "modular", "nvidia", "semiconductors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/qualcomm-buy-startup-modular-4-billion-ai-software-push-2026-06-24/"},
            {"name": "Reuters (Bloomberg report)", "url": "https://www.reuters.com/technology/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Cristiano_Amon_%28President_%26_CEOQualcomm%29_%2854916855494%29_%28cropped%29.jpg",
        "image_caption": "Qualcomm President and CEO Cristiano Amon, who is steering the company toward data centers and AI software",
        "image_attribution": "Wikimedia Commons",
        "body": """Qualcomm has spent twenty-five years as the company inside your phone. This week it told Wall Street that two-thirds of its future lies elsewhere, and then it spent nearly $4 billion to prove it. The chipmaker agreed to buy Modular, a four-year-old AI software startup, in an all-stock deal valued at $3.92 billion. Qualcomm will issue up to 19.2 million shares to Modular's owners.

Modular does not make chips. It makes software that runs AI models across different processors, from Nvidia to AMD and beyond, without rewriting code for each one. In an industry where Nvidia's dominance rests as much on its CUDA software lock-in as on its silicon, that is a pointed acquisition. Qualcomm is buying a neutral layer that sits above everyone's hardware, and it is paying a steep premium: Modular was valued at $1.6 billion just nine months ago.

**The pivot, in plain terms**

Qualcomm built its fortune on smartphone modems and Snapdragon chips. That market is mature, cyclical and increasingly saturated. Under CEO Cristiano Amon, the company has been hunting for the next act, and it has settled on the data centre. At its investor day this week Qualcomm laid out a future in which the majority of its business is no longer phones, courting customers like Meta and Microsoft Azure for AI server chips.

Modular is the software half of that strategy. Qualcomm can design competitive AI accelerators, but raw silicon is useless if developers cannot easily run their models on it. By owning software that abstracts away the underlying chip, Qualcomm lowers the switching cost for any company that wants an alternative to Nvidia. Amon's pitch is that the future belongs to developer-friendly platforms, not proprietary walled gardens, and the Modular deal is him putting money behind the slogan. It is not Qualcomm's only move, either: the company has reportedly been in talks to acquire AI chip startup Tenstorrent for as much as $8 to $10 billion.

**Why this lands in India**

Qualcomm's engineering heart beats heavily in India. Its design centres in Hyderabad, Bengaluru and Chennai employ tens of thousands of engineers, many of them working on exactly the modem and mobile silicon that defined the old Qualcomm. A strategic shift from handsets to data-centre AI is not an abstract Wall Street story for them. It is a question of which teams grow, which skills get rewarded, and whether a chip designer's career in Hyderabad now runs through AI infrastructure rather than smartphones.

For the broader diaspora, the deal is a useful tell about where semiconductor value is migrating. The money is moving from the device in your pocket to the server racks training and serving AI models. Indian engineers, whether in California, Austin or Hyderabad, sit across that whole supply chain, and the firms that employ them are repositioning fast. An Indian-American chip professional reading Qualcomm's investor day should hear a clear message: the prestige work is consolidating around data-centre AI, and the companies that built their names on consumer hardware are paying billions to get there.

**The risk**

Qualcomm is a late entrant to a market Nvidia owns and that AMD, Broadcom, and a wave of custom silicon from the hyperscalers themselves are already contesting. Buying software does not guarantee customers will adopt your chips. Modular's value lies precisely in its neutrality, supporting rivals' hardware too, which raises an awkward question: how hard will Qualcomm push a tool whose appeal is that it does not favour Qualcomm? Integrate it too tightly and it loses the neutrality that made it worth $4 billion. Leave it open and it helps competitors as much as it helps Qualcomm.

**What's next**

The deal still has to close, and Qualcomm has set itself a deadline of entering the data-centre market by year's end. Watch whether the promised Meta and Azure relationships turn into firm chip orders, and whether the Tenstorrent talks produce a second, far larger deal. For India's vast Qualcomm workforce, the more immediate signal is internal: the company that built itself on phones is now spending billions to be something else, and the engineers who follow the pivot will be the ones who define its next chapter."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
