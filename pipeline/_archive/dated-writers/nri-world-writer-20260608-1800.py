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
        "headline": "India Gave Foreign Funds a Tax Holiday on Government Bonds. It Forgot About Its Own Diaspora.",
        "subheadline": "A new ordinance exempts FPIs from tax on G-Sec interest and capital gains. Individual NRI investors, who have been asking for parity for years, are once again told to wait — or to find a workaround.",
        "slug": make_slug("india-gsec-tax-exemption-fpi-nri-investors-excluded"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NRI retail investors who hold or want to hold Indian government bonds are directly affected. The ordinance creates a two-tier system where institutional foreign money gets tax-free treatment while individual diaspora investors — contributing the same foreign capital — pay up to 20 per cent.",
        "tags": ["nri", "diaspora", "tax", "investment", "g-sec", "fpi", "rbi"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/no-blanket-exemption-like-fpi-to-retail-nri-investors-in-g%E2%80%90secs/article71072686.ece"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/"},
            {"name": "Capital Market", "url": "https://www.capitalmarket.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_02.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_02.jpg",
        "image_caption": "The Reserve Bank of India headquarters in Mumbai, where monetary and investment policy is shaped",
        "image_attribution": "Wikimedia Commons",
        "body": """India's government has handed foreign institutional investors a clean exemption from tax on government securities. Individual NRI investors got a polite reminder that they are not foreign enough to qualify.

The Income-tax (Amendment) Ordinance, 2026, promulgated on June 5, inserts two new entries — 13D and 13E — into Schedule IV of the Income-tax Act. Together, they exempt Foreign Portfolio Investors and the Bank for International Settlements from paying any income tax on interest earned from government securities or capital gains arising from their transfer. The exemption applies retrospectively from April 1, 2026.

The logic is straightforward: India wants to attract more stable, long-term foreign capital into its debt market. Forex reserves have slipped roughly six per cent in three months — from $728 billion to $682 billion — and the Finance Ministry is signalling that sovereign bonds need to offer globally competitive post-tax returns if pension funds, insurance companies, and sovereign wealth funds are to show up.

## What NRIs actually get

Nothing new. A senior government official, speaking to *The Hindu BusinessLine*, confirmed that NRI retail investors are not covered by the ordinance. If they invest in G-Secs on a standalone basis, the old rules apply: interest taxed at 20 per cent (except a reduced five per cent on certain notified rupee bonds), long-term capital gains at 12.5 per cent, and short-term gains at 20 per cent. Double Taxation Avoidance Agreement rates may lower the effective burden for some, but parity with FPIs is nowhere in sight.

Sandeep Sehgal, a tax partner at AKM Global, put it bluntly: "The recent ordinance removing these taxes is targeted squarely at foreign portfolio investors and the BIS, and does not, by itself, extend a similar blanket exemption to retail NRI investors in G-Secs."

Amarjeet Singh Arora of BDO India added that the government's immediate priority appears to be institutional portfolio flows, not retail or individual overseas investors. He noted, however, that "there may be some case for extending similar benefits to NRIs, who are equally contributing foreign capital to India," and predicted that industry bodies would lobby for exactly that.

## The GIFT City workaround

For NRIs willing to add a layer of complexity, a backdoor exists. SEBI has already relaxed rules to allow FPIs that invest solely in government securities to have NRI-only investor bases. In practice, this means an NRI in New Jersey or Dubai could invest through an offshore fund or a GIFT IFSC fund registered as an FPI — and enjoy the same tax exemption that a standalone NRI investment would not receive.

Nehal Sampat, a partner at Price Waterhouse & Co, confirmed the mechanics: "NRIs can benefit from the tax exemption announced for interest and capital gains from government securities for FPIs by investing in offshore funds and GIFT IFSC Funds registered as FPIs."

It works, but it is not exactly the zero-friction access that the diaspora has been asking for. Setting up or joining an FPI-registered fund requires compliance with SEBI and IFSCA regulations, KYC through IFSC banking units, and often a minimum investment that prices out smaller retail investors — precisely the demographic that India's "Viksit Bharat" rhetoric claims to be courting.

## A familiar pattern

This is not the first time NRI investors have watched institutional money get favourable treatment. The RBI recently doubled the equity investment limit for NRIs under the Portfolio Investment Scheme, but the KYC and account-opening friction remains so severe that many eligible investors never complete the process. India's $140 billion remittance pipeline — the world's largest, for the 25th consecutive year — keeps flowing, but the money largely moves through traditional banking and family transfers rather than through the kind of direct sovereign-debt participation the G-Sec exemption was designed to encourage.

The gap matters politically, too. The diaspora is 35 million strong, with an estimated annual income of $730 billion. They send home more money than any other expatriate community on the planet. Yet when it comes to investment policy, they remain a constituency that gets praised at Pravasi Bharatiya Divas and overlooked in the Finance Ministry's ordinances.

## What comes next

Industry bodies like FICCI and CII may push for a phased extension of the tax exemption to individual NRI investors, potentially beginning with those investing through the NRI Portfolio Investment Scheme. Whether the government moves before the Union Budget or waits for the next Pravasi Bharatiya Divas to make announcements is, as always, a question of political timing.

For now, the message to the diaspora is familiar: India wants your capital. It just prefers it wrapped in an institutional structure."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Built a Digital Portal to Turn the Diaspora Into a $500 Billion Trade Engine. Here's How It Works.",
        "subheadline": "At a gala in New Jersey, India's Consul General in New York unveiled a first-of-its-kind platform connecting Indian exporters directly with American buyers — and laid out the roadmap for 'Mission 500.'",
        "slug": make_slug("india-usa-trade-facilitation-portal-mission-500-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The portal positions the nearly four million Indian Americans as a 'living bridge' for bilateral trade, offering them a direct role in connecting Indian MSMEs and artisans with US buyers. It also reflects a shift from treating the diaspora as remittance senders to treating them as trade facilitators.",
        "tags": ["nri", "diaspora", "trade", "india-us", "mission-500", "glo-india", "msme"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/04/ambassador-pradhan-cites-new-trade-portal-as-central-to-mission-500-at-glo-india-gala/"},
            {"name": "South Asian Herald", "url": "https://southasianherald.com/"},
            {"name": "The Indian Panorama", "url": "https://www.theindianpanorama.news/global-indian-diaspora-alliance-glo-india-hosts-landmark-icons-of-impact-gala-in-new-jersey-honoring-leadership-and-legacy/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/India_Consulate_66_jeh.JPG/1280px-India_Consulate_66_jeh.JPG",
        "image_caption": "The Consulate General of India in New York, which developed the new trade facilitation portal",
        "image_attribution": "Wikimedia Commons",
        "body": """The numbers have been getting bigger for years. India-US bilateral trade hit $241 billion over the past year, making the United States India's largest trading partner for the fourth consecutive year. Both governments have signed off on an ambitious target they call "Mission 500" — more than doubling that figure to $500 billion by 2030.

What has been less clear is how exactly they plan to get there, especially for the thousands of small Indian manufacturers, artisans, and service providers who lack the networks or resources to break into the American market. At the inaugural GLO-INDIA "Icons of Impact" Gala in New Jersey, Ambassador Binaya S. Pradhan, Consul General of India in New York, offered a concrete answer: a new government-backed digital platform called the India-USA Trade Facilitation Portal.

## A marketplace with government backing

The portal, developed by the Consulate General itself, connects verified Indian exporters, manufacturers, artisans, startups, and service providers directly with US importers and buyers. It is free to use, and it is designed to do what decades of bilateral trade rhetoric have only promised — reduce the barriers that keep small and medium enterprises out of international markets.

The platform's feature set reads like a checklist of everything an Indian MSME founder would need and probably cannot afford: virtual exhibitions showcasing Indian products and services, webinars on US market trends and regulatory compliance, sector-specific networking opportunities, and dedicated market-entry guidance. There is a particular focus on three groups that have historically been locked out of cross-border trade: Micro, Small and Medium Enterprises, women-led businesses, and artisans under the One District One Product (ODOP) programme.

"Every great trade relationship is, at its heart, a relationship between people," Ambassador Pradhan told the audience of nearly 200 diaspora leaders. He described the Indian-American community — nearly four million strong, including doctors, business founders, professors, policymakers, and entrepreneurs — as uniquely positioned to serve as the connective tissue between the world's two largest democracies.

## The diaspora as trade infrastructure

The subtext of the portal's launch is a shift in how India thinks about its diaspora. For decades, the relationship has been defined by remittances — the $138 billion that flowed into India in 2025-26, keeping the country atop the global rankings for the 25th consecutive year. The new framing is different: the diaspora is not just a source of capital but a distribution network.

An Indian-American entrepreneur in Houston who knows both the chilli powder market in Andhra Pradesh and the wholesale grocery distribution chain in Texas is, in the Consulate's thinking, a trade facilitator that no government portal can replicate. What the portal can do is give that entrepreneur a vetted database of Indian suppliers, regulatory guidance, and market intelligence — the kind of infrastructure that previously required expensive consultants or personal connections.

The Consul (Trade) at the New York Consulate reinforced this during the event, describing the portal as "a trusted gateway connecting US importers with a carefully vetted database of Indian exporters" designed to foster "an ecosystem for shared growth."

## The $500 billion question

Whether Mission 500 is achievable by 2030 depends on factors far beyond any portal. The India-US bilateral trade agreement is still moving in tranches — Commerce Minister Piyush Goyal said earlier this year that tariffs on Indian goods entering the US would drop from 50 per cent to 18 per cent under the first tranche, but the formal agreement has yet to be finalised. Tariff uncertainty, regulatory divergence, and the sheer logistics of scaling trade across oceans remain formidable obstacles.

But the portal addresses a gap that trade agreements do not: discovery. India has 63 million MSMEs, many of which produce goods that would find ready buyers in the US if those buyers knew they existed. The portal's virtual exhibitions and sector-specific networking could, at scale, do for Indian trade what Alibaba did for Chinese manufacturing — make the supply side visible.

## More than trade at the gala

The GLO-INDIA event itself — the first "Icons of Impact" gala organised by the Global Indian Diaspora Alliance, a network with more than 18,000 members across five continents — honoured 11 diaspora leaders across business, healthcare, science, technology, and community service. Honorees included Roop Singh, CEO of Version 1 in Ireland and former CEO of the Birla Group; Dr. Navneet Puri, former Pfizer board director; Ajit Mannon, Chief Global Commercial Data, Digital and AI Officer at Johnson & Johnson; and Prof. Om Parkash Dhankher, agricultural biotechnology researcher at the University of Massachusetts Amherst.

Proclamations and citations arrived from the Governor of New Jersey, Congresswoman Mikie Sherrill, Governor Kathy Hochul of New York, and a roster of state legislators including Senators Linda Greenstein and Vin Gopal and Assemblyman Sterley Stanley. Three Indian-American mayors — Samip Joshi, Neena Singh, and Hemant Marathe — presented at the event, a quiet reminder that the diaspora's political infrastructure in the US is thickening at the local level even as national debates about immigration grow louder.

The portal is now live. Whether it becomes the plumbing for a $500 billion trade relationship or another well-intentioned government initiative that fades into the background will depend on whether the diaspora uses it. Ambassador Pradhan's pitch was direct: "Mentor entrepreneurs, facilitate business connections, and help create opportunities for smaller enterprises across India." The platform is built. The question is whether the bridge will carry traffic."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
