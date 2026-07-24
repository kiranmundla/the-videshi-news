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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Central Bank Is Paying NRIs Up to Seven Per Cent to Park Their Dollars at Home. Here Is the Catch.",
        "subheadline": "The Reserve Bank of India has opened a rare deposit window that eliminates currency risk for overseas Indians — but the fine print includes a three-year lock-in and a September deadline.",
        "slug": make_slug("rbi-fcnrb-nri-dollar-deposit-scheme-seven-percent"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Directly impacts NRI savings strategy — overseas Indians can now earn 5.5-7% on dollar deposits in India with zero currency risk, a significant premium over US savings accounts. The scheme specifically targets Gulf and US-based NRIs.",
        "tags": ["nri", "diaspora", "banking", "rbi", "fcnrb", "deposits", "remittances", "finance"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "IANS", "url": "https://ianslive.in/banks-register-rise-in-nri-deposits-under-rbis-new-scheme--20260703153303"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/money-and-banking/attracting-nri-inflows-rbi-temporarily-withdraws-interest-rate-ceiling-on-fresh-fcnrb-deposits-of-3-5-yr-tenor/article69704000.ece"},
            {"name": "Mint", "url": "https://www.livemint.com/money/personal-finance/why-fcnr-deposits-at-6-7-1-rates-are-attractive-for-nris-rbi-rate-cut-special-swap-window-11718539744222.html"},
            {"name": "Value Research Online", "url": "https://www.valueresearchonline.com/stories/nri-dollar-deposits/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Mumbai%2C_reserve_bank_of_india_02.jpg/1280px-Mumbai%2C_reserve_bank_of_india_02.jpg",
        "image_caption": "The Reserve Bank of India headquarters in Mumbai's Fort district",
        "image_attribution": "Wikimedia Commons",
        "body": """For most of the past decade, parking dollars in an Indian bank has been a poor proposition. After hedging costs, the rates on Foreign Currency Non-Resident Bank deposits — the standard instrument for NRIs who want to keep money in India without converting to rupees — hovered around 3 to 3.5 per cent. A US Treasury bill paid more. A high-yield savings account in America came close. The rational NRI kept the money where it was.

That arithmetic has changed, sharply and deliberately. In early June, the Reserve Bank of India announced it would absorb the full hedging cost on fresh FCNR(B) deposits with maturities of three to five years — the currency mismatch that normally eats into what banks can offer depositors is now sitting on the central bank's own balance sheet. Two weeks later, it went further: the interest rate ceiling on these deposits was temporarily scrapped altogether.

The result is a deposit window unlike anything NRIs have seen in years. Major banks — HDFC Bank, ICICI Bank, Axis Bank, Bank of Baroda — have hiked rates to around 6 to 6.5 per cent on three-to-five-year dollar deposits, a jump of roughly 300 basis points from where they stood in May. Smaller finance banks are advertising rates as high as 7.5 per cent.

## What the scheme actually offers

The mechanics are straightforward, which is part of the appeal. You deposit US dollars. You receive US dollars back at maturity. Interest accrues in the same currency. There is no rupee conversion at any point, which means there is no rupee depreciation risk — the perennial anxiety of NRIs who watched the currency slide from 60 to 85 against the dollar over the past decade.

The deposit window runs from June 8 to September 30, 2026. The minimum tenor is three years, the maximum five. Premature withdrawal is possible after one year, though at the bank's discretion. For eligible NRI and Overseas Citizen of India depositors, interest earned on FCNR(B) deposits is tax-exempt in India — a detail that makes the effective return even more competitive when compared with taxable US bank deposits.

Banks have already mobilised an estimated $3 to $4 billion through the revised scheme, according to an NDTV Profit report. Bankers expect the pace to accelerate through July and August as awareness spreads, with the Gulf region — home to millions of Indian expatriates — expected to contribute the largest share.

## Why the RBI is doing this

The generosity is not altruistic. India's balance of payments has been under quiet pressure. Net foreign direct investment was barely $1 billion in FY25. Portfolio investors pulled out $16.5 billion. The rupee has been under sustained stress, and the RBI's forex reserves, while substantial at $691 billion, have been deployed repeatedly to defend the currency.

Inward remittances from the diaspora — $138 billion in 2024, making India the world's largest recipient by a wide margin — have been a silver lining. But the composition of those flows matters. Consumption remittances support families; capital deposits shore up the banking system and the reserves. The FCNR(B) scheme is designed to pull more money into the second category.

The target is ambitious: bankers estimate the revised scheme could attract $40 to $50 billion in fresh deposits over time, a figure that would meaningfully replenish the reserves buffer and take pressure off the rupee.

## The fine print NRIs should read

The catch, predictably, is illiquidity. Three years is the minimum lock-in. If the US Federal Reserve raises rates unexpectedly, or a better opportunity emerges, the money stays in India. Premature withdrawal after one year is possible but not guaranteed, and it comes with a penalty.

There is also a question of deposit insurance. India's Deposit Insurance and Credit Guarantee Corporation covers up to ₹5 lakh — roughly $6,000 at current rates — per depositor per bank. For anyone considering a large deposit, that ceiling offers negligible protection.

The scheme also excludes transfers from Non-Resident Ordinary accounts to Non-Resident External accounts, a provision designed to ensure the money flowing in is genuinely new overseas capital, not a circular repackaging of funds already in the Indian banking system.

## What it means for the diaspora

For the estimated 35 million people of Indian heritage living abroad, the scheme is a rare moment when doing what the central bank wants also happens to be personally advantageous. A 6.5 per cent dollar return, tax-free, with sovereign backing, is competitive by any global standard — provided you can accept the lock-in.

The window closes on September 30. Banks are scrambling to reach NRI customers through relationship managers, overseas branches, and digital onboarding. For those sitting on dollar savings earmarked for India — a retirement home in Goa, a parent's medical fund, a property investment — the next three months are the best terms they are likely to see.

Whether the scheme achieves its $40-50 billion target depends on trust as much as rates. NRIs have been burned before by regulatory changes, repatriation hassles, and the glacial pace of Indian banking. The RBI is betting that 7 per cent is enough to overcome the scar tissue. For many in the diaspora, it just might be."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Eight Michelin Stars, a Whole Foods Aisle, and a Cancer Survivor's Dream: Indian Food's American Moment Is Here",
        "subheadline": "From a Sethi siblings' sauce line in every Whole Foods to a 7,500-square-foot Charlotte clubhouse run by a Hyderabad-trained chef, Indian cuisine is making its most ambitious play yet for the American mainstream.",
        "slug": make_slug("indian-cuisine-gymkhana-whole-foods-zamindars-clubhouse-america"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian-origin chefs and entrepreneurs are leading the mainstreaming of Indian cuisine in America — from Michelin-starred restaurants to grocery store aisles. The movement reflects how the diaspora is reshaping American food culture from within, not just opening ethnic restaurants but building national consumer brands.",
        "tags": ["nri", "diaspora", "indian-cuisine", "restaurants", "entrepreneurship", "food", "michelin", "whole-foods"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Restaurant Business Online", "url": "https://www.restaurantbusinessonline.com/operations/uk-based-indian-concept-gymkhana-brings-its-cpg-line-us"},
            {"name": "India West", "url": "https://indiawest.com/nyc-michelin-chef-opens-zamindars-clubhouse-in-charlotte/"},
            {"name": "JKS Restaurants", "url": "https://www.jksrestaurants.com/"},
            {"name": "CAVU Consumer Partners", "url": "https://www.cavuconsumerpartners.com/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/941869/pexels-photo-941869.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "image_caption": "Traditional Indian dishes featuring rich spices and regional flavours",
        "image_attribution": "Pexels",
        "body": """There is a moment in any cuisine's trajectory abroad when it stops being "ethnic food" and starts being just food. For Chinese cooking in America, that happened somewhere around the 1970s. For Japanese, the sushi revolution of the 1990s. For Thai, perhaps the 2000s. Indian food, despite being the cuisine of the world's largest diaspora, has been stubbornly stuck in the "ethnic" lane — beloved by millions, respected by critics, but boxed into a category that implied it was not quite ready for the centre of the American plate.

That is changing, and the evidence is no longer anecdotal. It is arriving in Whole Foods aisles, Michelin Guide pages, private equity term sheets, and the kind of restaurant spaces that announce ambition by their square footage alone.

## The grocery store play

This week, Gymkhana Fine Foods — the consumer products arm of London's JKS Restaurants — launched a line of simmer sauces and marinades in Whole Foods Markets nationally. The move is backed by an $8.5 million Series A funding round led by CAVU Consumer Partners, the venture firm co-founded by Rohan Oza, the investor known for backing Vitamin Water and appearing on "Shark Tank."

JKS, founded by siblings Jyotin, Karam, and Sunaina Sethi, is not a casual entrant. The group operates more than 30 restaurants across London and beyond, including Gymkhana, Trishna, and Brigadiers. Across the portfolio, JKS holds eight Michelin stars and six Bib Gourmand mentions — credentials that make it one of the most decorated Indian restaurant groups in the world.

"Each sauce, marinade and chutney has been created to deliver the same bold, authentic flavors found in our restaurants," Karam Sethi said in a statement. "As we expand into the U.S., from our first restaurant in Las Vegas in 2025 to the launch of Gymkhana Fine Foods across the country, our aim remains the same: to offer Indian cuisine in its purest form."

The Las Vegas debut — at the Aria Resort & Casino — was the Sethis' first foray into the American market. The Whole Foods rollout is the second, and arguably the more significant. A Michelin-starred restaurant impresses a city. A national grocery line reshapes how ordinary Americans cook.

## The restaurant that tells a different story

A thousand miles east of Las Vegas, a different kind of Indian restaurant opened in Charlotte, North Carolina, this month. Zamindar's Clubhouse occupies 7,500 square feet — an enormous footprint for any independent restaurant, let alone an Indian one in the American Southeast — with separate dining, bar, lounge, and patio areas designed around the social clubhouses that once served as gathering places across India.

The interiors tell the story: carved wood, brass accents, Jaipur carpets, Khirki-style arches, Kolkata-inspired window frames, vintage gramophones. It is not the beige-walled, buffet-line aesthetic that defined first-generation Indian restaurants in America. It is a statement.

Leading the kitchen is Vamshi Krishna Adi, whose journey traces the classic diaspora arc. Trained at the Culinary Academy in Hyderabad, he moved to the US, worked through Junoon and Rooh in San Francisco, then opened three restaurants in New York — including Ishq, which earned a Michelin Bib Gourmand shortly after opening.

The founder, David Pandoria, brings a story of a different kind. After a career in corporate sales and years as a DJ in the Southeast Asian American community, he was diagnosed with stage four squamous cell carcinoma in 2023. Treatment and recovery led him to leave corporate life entirely and bet everything on hospitality. "Every part of this place is intentional," the restaurant's concept materials note.

The menu ranges from Jalebi Chaat and Aslam Butter Chicken Wings to Calicut Mango Lobster Curry and Hyderabadi Chicken Dum Biryani — regional Indian cooking presented without apology or dilution, at price points that place it squarely in the American fine-casual segment.

## The money follows the moment

The capital flowing into Indian food in America is no longer incidental. Last year, L Catterton — the private equity firm backed by LVMH — invested in Dishoom, the London-based Indian restaurant group that is now expanding to the US. The Gymkhana CPG round adds $8.5 million more. Investors who once wouldn't touch Indian food beyond a franchise play are now writing serious cheques.

The pattern mirrors what happened with Japanese cuisine in the 2000s: first the critical acclaim, then the consumer products, then the institutional capital. Nobu begat grocery-store miso paste. Gymkhana may beget grocery-store garam masala.

## The diaspora's quiet revolution

What makes this moment distinctly diasporic — rather than merely culinary — is who is driving it. The Sethi siblings grew up between India and Britain, absorbing both culinary traditions. Vamshi Krishna Adi trained in Hyderabad before reinventing himself in New York. Even Rohan Oza, the investor backing the Gymkhana CPG line, is of Indian origin — a reminder that the capital, the creativity, and the customer base are all, increasingly, shaped by the same community.

For decades, Indian Americans opened restaurants as a survival strategy — a way to employ family, serve the community, make a living. What is happening now is different. It is Indian-origin entrepreneurs building national consumer brands, Indian-trained chefs earning Michelin recognition, and Indian flavours entering the same Whole Foods aisles as Rao's marinara and Momofuku chili crunch.

The American pantry is being rewritten. The authors, more often than not, carry an Indian passport in their desk drawer."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
