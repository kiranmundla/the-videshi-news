#!/usr/bin/env python3
"""NRI World Writer — 2026-06-30 17:00 run"""
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


# ─────────────────────────────────────────────
# ARTICLE 1: Sriram Krishnan leaves the White House
# ─────────────────────────────────────────────

article1_body = """Sriram Krishnan's six-month stint as the White House's senior policy adviser on artificial intelligence ends today, making him the latest — and arguably the most consequential — Indian-American tech figure to rotate through the revolving door between Silicon Valley and Washington.

"This journey has been the privilege of a lifetime," Krishnan posted on X on June 6, announcing his departure date. "First and foremost, it has been an honor to serve under President Trump. Without his leadership, we would not be leading in the AI race."

## The résumé that landed in the West Wing

Born in Chennai, Krishnan cut his teeth at Microsoft on Windows Azure before holding senior product roles at Facebook, Twitter, Snap, and Yahoo. By the time Elon Musk tapped him to help steer the post-acquisition chaos at Twitter in 2022, he was already a general partner at Andreessen Horowitz, one of the Valley's most powerful venture firms. That proximity to the tech-right ecosystem — Marc Andreessen and Ben Horowitz were early and vocal Trump backers — made Krishnan a natural pick when the administration went shopping for an AI czar's right hand.

In Washington, Krishnan worked most closely with David Sacks, the investor who briefly served as Trump's AI and crypto czar before stepping down to co-chair the President's Council of Advisors on Science and Technology. Together, they shaped the administration's AI Action Plan, which prioritised data-centre construction and deregulation over the kind of safety-first guardrails favoured by many researchers. They also helped craft executive orders that challenged state-level AI regulations and floated the idea that the federal government could take equity stakes in major AI companies.

Krishnan's influence extended beyond domestic policy. He was named a TIME Person of the Year in 2025 as one of the "Architects of Artificial Intelligence," a designation shared with a handful of executives whose companies were rewriting the global technology order.

## What comes next

Krishnan will not be disappearing from the policy arena. According to The Washington Post, he is planning to launch an outside institution — described by sources as a pro-administration AI policy organisation — that will allow him to continue shaping the national AI conversation without the constraints of a government job. Sacks confirmed that Krishnan will remain connected to the White House as an outside adviser.

"Whether it is energy, data centres or a clear path for Americans to experience the benefits of AI, there are many tough issues we all need to navigate together," Krishnan said in his farewell post.

## What this means for the diaspora

Krishnan's trajectory — Chennai to Microsoft to Andreessen Horowitz to the West Wing — is a distinctly twenty-first-century version of the immigrant success story. But it also illustrates a more complicated truth about the Indian-American community's relationship with power in Washington.

The Indian diaspora has produced a remarkable concentration of corporate chieftains — Satya Nadella at Microsoft, Sundar Pichai at Alphabet, Shailesh Jejurikar at Procter & Gamble, Srini Gopalan at T-Mobile. Yet government and public-policy roles have been slower to attract the community's talent. Krishnan's appointment was celebrated as a breakthrough, a sign that Indian-Americans could shape not just corporate strategy but national policy.

His departure leaves a gap. No replacement has been announced, and the administration has given no indication that it will fill the role with another Indian-American. For a community that makes up 1.5 per cent of the American population but contributes roughly 6 per cent of federal tax revenue — a ratio Ambassador Atul Keshap cited at a recent FIIDS summit on Capitol Hill — the question of who holds the levers is not abstract.

As Congressman Raja Krishnamoorthi reminded a gathering of 135 Indian-American delegates in Washington this month: "If you don't have a seat at the table, you're on the menu."

Sriram Krishnan had a seat. What the diaspora does with the vacancy is the next chapter."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Diaspora's Highest-Ranking AI Voice in Washington Just Walked Out of the White House",
    "subheadline": "Sriram Krishnan's six-month run as Trump's senior AI policy adviser ends today. He's not done with Washington — he's just changing the address.",
    "slug": make_slug("sriram-krishnan-white-house-ai-adviser-departure-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Krishnan's trajectory from Chennai to the West Wing represents a new frontier for Indian-American influence — policy, not just corporate leadership — and his departure raises the question of who fills the gap.",
    "tags": ["nri", "diaspora", "indian-american", "ai-policy", "sriram-krishnan", "white-house", "technology"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/06/sriram-krishnan-is-leaving-his-role-as-white-house-ai-advisor/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/white-house-ai-policy-adviser-krishnan-leave-position-2026-06-07/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/white-house-ai-adviser-sriram-krishnan-to-step-down-at-end-of-june/article71075456.ece"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/who-is-sriram-krishnan-the-white-house-ai-adviser-set-to-step-down-in-june"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/da/MS200024.jpg",
    "image_caption": "Sriram Krishnan, who served as senior White House AI policy adviser",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ─────────────────────────────────────────────
# ARTICLE 2: NRI tax trap on gifts to parents
# ─────────────────────────────────────────────

article2_body = """A US-based NRI sent ₹11 lakh to his parents in India. It was a gift — the kind of routine cross-border transfer that millions of diaspora families make every year. But it turned into a six-year legal battle with the Indian tax authorities, one that was settled only when the Income Tax Appellate Tribunal (ITAT) finally ruled in his favour.

The case, reported by the tax advisory platform TaxBuddy, is a cautionary tale for any NRI who has ever wired money home without thinking twice about paperwork. And given that India received roughly $138 billion in inward remittances in 2024 alone — the largest such flow in the world, according to the International Organization for Migration — there are a lot of people who should be paying attention.

## What went wrong

Under the Income-tax Act, gifts from specified relatives — parents, spouses, children, siblings — are completely exempt from taxation, regardless of the amount. There is no cap. Send ₹11 lakh or ₹11 crore: if it is a gift to a parent, it is not taxable income in the parent's hands.

The problem was documentation, or the lack of it. The tax authorities treated the transfer as "unexplained income" — a classification that invites scrutiny and potential penalties. Without adequate records establishing the source of the funds and the relationship between the sender and the recipient, the burden of proof fell on the NRI and his parents to demonstrate what should have been obvious.

Six years later, bank records confirmed that the transfer was legitimate. The tribunal dismissed the notice. But by that point, the family had spent years tangled in a bureaucratic process that most NRIs assume could never apply to them.

## The documentation checklist every NRI needs

Tax experts say the ₹11 lakh case is not an outlier. As the Indian tax department has grown more aggressive about scrutinising cross-border transactions — partly driven by India's commitments under the Common Reporting Standard (CRS) and the automatic exchange of financial information with over 100 jurisdictions — even routine family transfers are getting flagged.

The minimum documentation that every NRI should maintain for any significant remittance to India:

**Bank transfer receipts and SWIFT confirmations.** These establish the date, amount, and route of the transfer.

**Proof of overseas income.** Pay stubs, employment contracts, or business revenue records that show where the money came from. The tax department wants to see that the funds originated from legitimate earnings abroad, not from undisclosed Indian income.

**Relationship documents.** Birth certificates, marriage certificates, or other proof of relationship between the sender and recipient. This matters because the tax exemption for gifts applies only to "specified relatives" as defined under the Act.

**A gift deed.** Not strictly required by law for every transfer, but tax advisers overwhelmingly recommend it. A simple written declaration — signed by both parties, ideally notarised — stating that the transfer is a gift, the amount, the date, and the relationship. It costs almost nothing to prepare and can save years of hassle.

**Correct purpose code on the remittance.** When money enters India, the authorised dealer bank assigns a purpose code that indicates the nature of the transfer — family maintenance, education, gift, and so on. An incorrect or missing purpose code can trigger automatic verification flags.

## The NRE-NRO trap

One detail that catches many NRIs off guard: the type of Indian bank account the money lands in matters for tax purposes. NRE (Non-Resident External) accounts are designed for foreign earnings and offer tax-free interest. NRO (Non-Resident Ordinary) accounts are for income earned in India and are subject to taxation. Sending money to a parent's regular savings account — rather than routing it through the NRI's own NRE account first — can create an unnecessary paper trail that draws scrutiny.

## What the ITAT ruling actually settled

The tribunal did not change any law. It simply confirmed what the law already says: gifts between specified relatives are exempt, and bank records are sufficient evidence to establish the nature of the transaction. But the six-year delay is the point. Even when the law is on your side, the process itself is the punishment if your records are incomplete.

For the millions of NRIs who will send money home this year — to parents covering medical bills in Delhi, to siblings managing a family property in Hyderabad, to spouses maintaining a household in Bengaluru — the lesson is not that India's tax system is hostile. It is that the system is automated, indiscriminate, and entirely indifferent to your intentions. What it responds to is paper.

Keep the paper."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "He Sent ₹11 Lakh to His Parents. India's Tax Department Took Six Years to Believe It Was a Gift.",
    "subheadline": "A US-based NRI's routine family transfer turned into a protracted legal battle. The case is a masterclass in what every diaspora family sending money home gets wrong.",
    "slug": make_slug("nri-gift-tax-dispute-11-lakh-parents-itat-documentation"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Millions of NRIs send money to family in India every year with minimal documentation. This case shows exactly how that can go wrong — and what to do about it.",
    "tags": ["nri", "diaspora", "tax", "remittance", "income-tax", "itat", "gift", "documentation", "india"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Times Now World", "url": "https://www.timesnowworld.com/us-news/us-nri-income-tax-notice-transfer-parents-india-article-154781991"},
        {"name": "Livemint", "url": "https://www.livemint.com/money/personal-finance/buying-or-selling-property-in-india-as-an-nri-here-are-the-rules-you-should-know-11747296620917.html"},
        {"name": "TaxBuddy", "url": "https://www.taxbuddy.com/"}
    ]),
    "score_total": 76,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8962457/pexels-photo-8962457.jpeg",
    "image_caption": "Tax documents and a smartphone on a desk — the kind of paperwork NRIs ignore at their peril",
    "image_attribution": "Pexels",
    "body": article2_body,
}


# ─────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
