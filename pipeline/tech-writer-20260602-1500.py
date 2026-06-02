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
        "headline": "UPI Just Processed ₹29.9 Lakh Crore in a Single Month. NRIs Can Now Use It in Seven Countries.",
        "subheadline": "India's digital payments rail hit a record 23.2 billion transactions in May, and cross-border UPI is quietly becoming the diaspora's most useful fintech export.",
        "slug": make_slug("upi-record-29-lakh-crore-may-nri-cross-border"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Cross-border UPI now works in UAE, Singapore, Bhutan, Nepal, Mauritius and more — the same countries where large NRI populations live and travel. WhatsApp Plus launched in India at ₹79/month, and PhonePe (47% market share) and Google Pay (34%) are the dominant players NRI families use daily.",
        "tags": ["upi", "digital-payments", "india-fintech", "nri", "cross-border", "phonpe", "google-pay"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/technology/tech-news/upi-transactions-hit-record-high-of-rs-29-9-lakh-crore-in-may"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/money-and-banking/upi-transactions-hit-record-high-of-299-lakh-cr-in-may/article69647821.ece"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/upi-transactions-jump-3-8-mom-in-may-cross-23-bn-mark/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/5239819/pexels-photo-5239819.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """India's Unified Payments Interface processed ₹29.9 lakh crore ($358 billion) across 23.2 billion transactions in May 2026 — both all-time records. The numbers, released by the National Payments Corporation of India, represent a 19 per cent year-on-year jump in value and a 24 per cent surge in volume from the 18.7 billion transactions logged in May 2025.

## What Drove the Spike

Summer travel and IPL 2026 were the obvious catalysts. But the more structural story is that UPI's average ticket size has steadily fallen — from ₹1,848 in 2021 to ₹1,313 in 2025 — which, counterintuitively, signals health. Smaller transactions mean deeper penetration into everyday commerce: chai stalls, auto-rickshaws, vegetable vendors. The payments rail that started as a bank-to-bank transfer tool now processes 748 million transactions per day.

PhonePe continues to dominate with 47 per cent market share, processing over 1,033 crore transactions in April alone. Google Pay holds steady at 34 per cent. Together, they account for more than 80 per cent of all UPI traffic — a concentration NPCI is quietly trying to dilute. The regulator is reportedly developing a shared UPI soundbox infrastructure to make merchants device-agnostic and encourage smaller players.

## The Cross-Border Play That Matters to NRIs

The number most Indian Americans should pay attention to is seven — the number of countries where UPI now works for international payments. The UAE, Singapore, Bhutan, Nepal, Mauritius, Sri Lanka, and France have all gone live with cross-border UPI acceptance. For the estimated 9.5 million NRIs in the Gulf states alone, this means paying at shops in Dubai or Singapore with a PhonePe or Google Pay QR scan tied to an Indian bank account.

Credit-on-UPI represents the next volume frontier. The feature — which allows users to make UPI payments drawn against pre-approved credit lines — is still in early innings, but it adds an entirely new transaction category onto existing rails. For NRI parents who maintain Indian bank accounts and regularly send money home, credit-on-UPI could eventually become a faster alternative to SWIFT transfers for recurring household expenses.

## Why Investors Should Watch PhonePe

PhonePe, majority-owned by Walmart, has been valued at $12 billion in its last funding round and is widely expected to pursue an IPO in 2026 or 2027. Its dominance in UPI gives it a distribution advantage that no amount of engineering can replicate — nearly half of all digital payments in the world's most populous country flow through its servers.

For NRI investors tracking India's fintech story, PhonePe is the most direct bet on UPI's continued ascent. Google Pay is embedded within Alphabet's broader financials and thus invisible to stock pickers. Paytm, once a distant third at 8 per cent market share, has stabilized under new management but remains a turnaround story.

## The Bigger Picture

India now processes more real-time digital transactions than any country on earth — more than the US, China, and Europe combined. The UPI rail is increasingly becoming India's most successful technology export, with conversations underway to bring it to more European and Southeast Asian markets. For the Indian diaspora, the practical implication is straightforward: the next time you visit home, leave the dollars in your wallet. Your phone already has the only payment method that matters."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Big Tech Is Hollowing Out AI Startups With Billion-Dollar Poaching Raids. Indian Researchers Are at the Centre.",
        "subheadline": "Microsoft, Meta, Google and Amazon are using 'reverse acquihires' to gut promising startups of their founders and top talent — paying AI researchers up to $1 billion while leaving rank-and-file employees with nothing.",
        "slug": make_slug("big-tech-reverse-acquihire-ai-talent-war-indian"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-origin AI researchers are among the most sought-after talent in Silicon Valley's poaching wars. The startups being hollowed out employ thousands of Indian engineers on H-1B visas whose equity is being vaporised in these deals. The trend threatens the startup culture that has been the primary wealth-creation vehicle for Indian tech professionals in America.",
        "tags": ["ai-talent", "silicon-valley", "reverse-acquihire", "startups", "h1b", "indian-engineers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/ai-researchers-hiring-spree-big-tech-5ad03ebd"},
            {"name": "Barchart", "url": "https://www.barchart.com/story/news/32936949/meta-is-launching-chatbot-subscriptions-meta-stock-bulls-need-a-way-to-justify-ai-costs"},
            {"name": "LinkedIn / Deepali Vyas", "url": "https://www.linkedin.com/posts/deepali-vyas_careeradvice-layoffs2026-aijobs-activity-7333520988291960832"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6806092/pexels-photo-6806092.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Silicon Valley has a new favourite move, and it is killing the ecosystem that made it great.

Microsoft, Meta, Google and Amazon have all adopted a tactic that insiders now call the "reverse acquihire." Instead of buying a promising AI startup outright — with all the regulatory headaches and integration costs that entails — they simply hire away the founders and top researchers, license the technology, and leave the remaining company to die or be absorbed by someone else.

The Wall Street Journal reported this week that the practice has reached an industrial scale. Microsoft did it with Inflection AI, poaching CEO Mustafa Suleyman to run its Copilot business and paying a $650 million licensing fee. Meta followed with a $14.8 billion investment in Scale AI that was really a mechanism to acquire CEO Alexandr Wang and his top team. Google gutted a startup called Windsurf in a $2.4 billion deal in July — some of the remaining staff reportedly cried in the office when they learned the terms.

## The Money Is Obscene, but Not for Everyone

Individual AI researchers are commanding packages that would make professional athletes blush. Some offers have reportedly reached as high as $1 billion. The logic is brutal: in a race that all four tech giants view as a once-in-a-generation opportunity, the cost of the best researchers is essentially infinite. They would rather overpay for ten people than lose the AI arms race.

The problem is that these deals are devastating for everyone who is not a founder or a top researcher. The rank-and-file engineers — the ones handling sales, marketing, platform reliability, or sitting in large engineering teams — get nothing resembling the payday they were promised when they joined a startup with equity.

"If you thought you had a share of a company and you actually didn't have a share of a company, there's a loss of trust," Jon Sakoda, founding partner at venture firm Decibel, told the Journal.

## Why Indian Engineers Should Be Worried

This is not an abstract Silicon Valley governance debate. It is a direct threat to the wealth-creation model that has driven Indian professional immigration to America for two decades.

The standard playbook has always been: arrive on an H-1B visa, join a startup or early-stage company, accumulate equity, ride the IPO or acquisition to financial freedom. That bargain depended on startups being acquired whole — with everyone's shares converting to cash or acquirer stock. The reverse acquihire breaks that compact. The founders get rich. The VCs get some return. The mid-level engineer on an H-1B gets a company that has been emptied of its most valuable people.

Thousands of Indian-origin engineers work at the exact kind of AI startups that are now being targeted. Many are on visa-dependent equity plans. When Google raids their employer for three people and the company dissolves, they do not just lose equity — they lose their visa clock, their green card queue position, and potentially their right to remain in the country.

## The Paradox for Big Tech

Microsoft, Alphabet, Meta and Amazon have collectively acquired more than 100 companies and invested in hundreds more since 2020. Many of their most important products — Android, AWS Graviton chips, Instagram — originated in acquisitions. The reverse acquihire may be cheaper and faster, but it corrodes the startup culture that produces the next generation of companies worth acquiring.

If the trend persists, talented engineers will rationally stop joining startups altogether and go straight to Big Tech, where the paycheque is guaranteed. Silicon Valley's innovation engine needs an army of people willing to take enormous risk for enormous reward. That bargain is crumbling, and Indian professionals — who have always been disproportionately willing to take that bet — may be the first to recalculate."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Meta Is Charging for WhatsApp, Instagram and Facebook. For Indian Families, It Starts at ₹79.",
        "subheadline": "Zuckerberg's company has launched paid subscription tiers across all three of its flagship apps, plus a two-tier AI subscription. The WhatsApp play is the one NRIs need to watch.",
        "slug": make_slug("meta-paid-subscriptions-whatsapp-instagram-facebook-nri"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "WhatsApp is the default communication infrastructure for the Indian diaspora — family group chats, business coordination, community organising. Its monetisation at ₹79/month in India and $2.99/month globally directly affects how 500 million Indian users and their NRI relatives communicate.",
        "tags": ["meta", "whatsapp", "instagram", "facebook", "subscriptions", "ai", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/beyond-ads-inside-metas-growing-ecosystem-of-paid-plans-across-whatsapp-instagram-facebook-and-ai-58765.htm"},
            {"name": "EurWeb", "url": "https://eurweb.com/2026/meta-introduces-paid-plans-for-facebook-instagram/"},
            {"name": "Barchart", "url": "https://www.barchart.com/story/news/32936949/meta-is-launching-chatbot-subscriptions-meta-stock-bulls-need-a-way-to-justify-ai-costs"},
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/02/why-launching-subscription-services-could-be-a-genius-move-for-meta/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/267389/pexels-photo-267389.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """For twenty years, Meta's business model has been elegantly simple: give everyone free apps, sell their attention to advertisers. That era is now officially ending.

Meta has launched paid subscription tiers across WhatsApp, Instagram and Facebook simultaneously — a global rollout that represents the company's most ambitious attempt to diversify revenue beyond advertising. On top of that, it is testing two AI-specific subscription plans under a new umbrella called Meta One.

The pricing: WhatsApp Plus at $2.99 per month (₹79 in India), Instagram Plus and Facebook Plus at $3.99 each, Meta One Plus at $7.99, and Meta One Premium at $19.99. The free versions of all three apps remain available. Nobody is being forced to pay.

## What You Get (and What You Do Not)

The consumer subscriptions are relatively modest. WhatsApp Plus offers custom themes, premium stickers, personalised ringtones, and additional chat pinning. Instagram Plus adds audience analytics, profile customisation, and expanded Story controls. Facebook Plus includes animated reactions, upgraded Story tools, and personalisation settings.

None of these touch core functionality. Messaging, calls, posting, and scrolling remain free. Meta's head of product, Naomi Gleit, described the plans as "premium features for those who want to unlock more" — the language of a company that knows it cannot afford to alienate 3.56 billion daily users.

The AI subscriptions are more consequential. Meta One Plus ($7.99) and Meta One Premium ($19.99) offer higher usage limits for Meta AI, the chatbot embedded across all three apps, plus advanced image and video generation tools. These are being tested first in Singapore, Guatemala, and Bolivia before a broader rollout.

## The WhatsApp Question

For the Indian diaspora, all of this orbits one app: WhatsApp.

WhatsApp is not a messaging app for Indian families — it is infrastructure. It is how parents in Delhi coordinate with children in New Jersey. It is how community organisations in Edison announce events. It is how small business owners across India manage supply chains, customer relationships, and payments. India alone accounts for roughly 500 million of WhatsApp's users, making it the single largest market by an enormous margin.

At ₹79 per month, WhatsApp Plus is priced low enough to attract heavy users but high enough to generate meaningful revenue at Indian scale. The customisation features are thin, but that is almost certainly by design. The playbook is familiar from other subscription businesses: launch with cosmetics, gradually migrate useful features behind the paywall, and watch the conversion rate climb.

NRIs should pay attention to what moves behind the paywall next. Group management tools, broadcast list expansion, and business-grade analytics are all features that power users would pay for — and that Meta could easily gate.

## The $145 Billion Problem

The subscription push is inseparable from Meta's financial reality. The company has told investors it expects to spend between $115 billion and $145 billion on capital expenditure in 2026, nearly all of it on AI infrastructure — data centres, custom chips, and the compute required to train and serve its AI models at scale.

That spending has to be justified to shareholders who have watched Meta's stock underperform while Nvidia and Alphabet have surged. Subscriptions are one answer: recurring revenue that Wall Street loves and that offsets the unpredictable economics of an advertising business tied to consumer sentiment.

The other answer is layoffs. Meta has filed WARN notices for 3,270 Bay Area positions with separations starting in July, and reports suggest the company may ultimately cut up to 20 per cent of its 79,000-person workforce. It is, in effect, asking users to pay more while simultaneously asking employees to leave.

## What NRI Investors Should Consider

Meta's subscription model is still nascent — the company does not break out subscriber numbers, and the revenue appears in an "Other" segment that accounts for less than 2 per cent of total quarterly revenue. The question is trajectory. If even 5 per cent of Meta's 3.56 billion daily users subscribe at an average of $4 per month, that is $8.5 billion in annual recurring revenue — a significant business by any standard.

For NRI portfolios with Meta exposure, the calculus is shifting from pure advertising growth to a blended model. The company that gave everything away for free is learning to charge. Whether its users will let it — especially in price-sensitive markets like India — remains the $145 billion question."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
