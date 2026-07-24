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
        "headline": "Your Tax Return May Soon Ask If You're a Citizen — And the IRS Already Leaked 42,000 Records to ICE",
        "subheadline": "The agency that promised to keep your data safe is now debating a citizenship checkbox on Form 1040. For Indians filing taxes on H-1B and green card tracks, the implications go well beyond a single tick mark.",
        "slug": make_slug("irs-citizenship-checkbox-form-1040-indian-immigrants"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Every Indian on an H-1B, L-1, or green card track files Form 1040. A citizenship checkbox would flag hundreds of thousands of Indian American taxpayers in IRS databases — creating a ready-made list that immigration enforcement agencies have already tried to access. Indians are among the most tax-compliant immigrant communities in the US; this move risks punishing compliance itself.",
        "tags": ["irs", "form-1040", "citizenship", "immigration", "h1b", "tax-compliance", "data-privacy"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/us-tax-officials-consider-adding-citizenship-question-tax-forms-2026-05-22/"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/law-order/3918927-exclusive-us-tax-officials-consider-adding-citizenship-question-to-tax-forms"},
            {"name": "USCIS Official", "url": "https://www.uscis.gov/newsroom/news-releases/us-citizenship-and-immigration-services-will-grant-adjustment-of-status-only-in-extraordinary"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7821551/pexels-photo-7821551.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "body": """The IRS is weighing whether to add a citizenship status question to next year's Form 1040 — the tax return filed by virtually every working adult in America, including the roughly 600,000 Indian nationals on H-1B visas and hundreds of thousands more on green card tracks.

According to a Reuters exclusive published on May 22, agency officials are considering two versions of the 2027 Form 1040. The first is a routine update reflecting recent tax law changes. The second adds a checkbox: "Check this box if you are a non-U.S. citizen or have dual citizenship."

The Treasury Department declined to comment. But the proposal sits within a broader pattern that should unsettle anyone in the Indian American community who files taxes — which is to say, nearly everyone.

## The Data the IRS Already Shared

This isn't a theoretical privacy concern. The IRS admitted in February 2026 that it had "erroneously" shared the personal data of more than 42,000 taxpayers with the Department of Homeland Security. That disclosure came during ongoing litigation after a federal judge blocked the IRS-DHS data pipeline in November 2025.

The backstory: throughout 2025, the Treasury Department and DHS spent months building a collaboration framework to share confidential taxpayer information with immigration enforcement. Advocacy groups filed suit. A federal judge shut it down. The government appealed. And then the IRS conceded it had already handed over tens of thousands of records anyway.

"It's just an effort to once again terrorize people with certain immigration statuses, and it's another step of turning the IRS into an agency that collaborates with immigration authorities rather than being an agency that enforces and administers the tax laws," said Nina Olson, executive director of the Center for Taxpayer Rights.

## Why a Checkbox Changes Everything

A checkbox might seem trivial. It isn't. Right now, the IRS can infer non-citizen status in some cases — for instance, taxpayers who file using an Individual Taxpayer Identification Number (ITIN) instead of a Social Security Number. But H-1B holders, green card applicants, and naturalized citizens with dual nationality all use SSNs. The IRS currently has no systematic way to distinguish them from US-born citizens in its databases.

A citizenship checkbox would create precisely that distinction. For the first time, the IRS would maintain a searchable, filterable database of every non-citizen and dual-citizen taxpayer in America — sortable, exportable, and one memo away from being shared with DHS, ICE, or any agency that asks.

IRS officials are also considering differentiating ITIN codes to denote a filer's immigration status, according to Reuters' sources. This would create a second, even more granular layer of immigration data embedded in the tax system.

## The Compliance Paradox

The Indian American community presents a stark illustration of how self-defeating this policy could be. Indians on work visas are among the most tax-compliant immigrant groups in the country — filing W-2s, paying Social Security and Medicare taxes they may never collect, and generally generating significant tax revenue for federal and state governments.

The Yale Budget Lab has estimated that lower tax compliance rates among immigrant communities — driven by exactly this kind of fear — could cost the federal government $313 billion in revenue over the next decade.

Tax preparers across the country reported in 2025 that immigrant clients were already frightened to file, spooked by the IRS-DHS data-sharing revelations. A citizenship checkbox would amplify that chill. The perverse outcome: the most compliant immigrants stop filing, revenue drops, and enforcement agencies get less data than they had before.

## What This Means for You

If you're on an H-1B, L-1, or any work visa and you file Form 1040 — which you are legally required to do — this proposal would ask you to affirmatively identify yourself as a non-citizen to the same agency that already shared taxpayer data with immigration enforcement.

If you're a green card holder with Indian citizenship, you'd check the box. If you're a naturalized US citizen who holds an OCI card, the "dual citizenship" language is ambiguous enough to create confusion.

Immigration attorneys are already advising clients to continue filing taxes normally and not to panic. But the structural incentive is unmistakable: the tax system, which was designed to be citizenship-blind by statute, is being slowly retrofitted into an immigration surveillance tool.

The proposal is not final. But the trajectory — IRS-DHS data sharing in 2025, the 42,000-record leak, and now a citizenship checkbox — suggests the direction of travel. For Indian Americans who've spent years building careers, paying taxes, and waiting in the world's longest green card backlog, the message is hard to miss: even compliance won't protect your privacy."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Trump Orders Banks to Flag Immigrant Customers — What the May 19 Executive Order Actually Does",
        "subheadline": "A new executive order directs banks to scrutinize accounts opened with ITINs and assess 'deportation risk' when extending credit. For Indian Americans, the ripple effects extend far beyond the undocumented.",
        "slug": make_slug("trump-bank-executive-order-immigration-itin-scrutiny"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "While most H-1B holders have SSNs and won't be directly flagged, the executive order affects the broader financial ecosystem Indian Americans rely on — from H-4 dependent spouses using ITINs to Indian-owned small businesses serving mixed-status communities. The order also signals that financial institutions are being recruited as de facto immigration enforcement partners.",
        "tags": ["executive-order", "banks", "itin", "immigration-enforcement", "h4-ead", "financial-access"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Tennessean / USA Today", "url": "https://www.tennessean.com/story/news/politics/2026/05/21/trump-order-bank-scrutiny-non-citizens-accounts/90196316007/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/us-tax-officials-consider-adding-citizenship-question-tax-forms-2026-05-22/"},
            {"name": "White House Executive Order", "url": "https://www.whitehouse.gov/presidential-actions/executive-order-protecting-the-financial-system/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/28279114/pexels-photo-28279114.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "body": """On May 19, President Trump signed an executive order directing banks to tighten scrutiny of customers tied to immigration — the latest move in an administration campaign to recruit the private sector into immigration enforcement.

The order, titled "Protecting America's Financial System from Illicit Activity," instructs the Treasury Secretary to issue advisories to financial institutions on identifying suspicious activity related to tax evasion, concealment of account ownership, off-the-books wage payments, labor trafficking, and the use of Individual Taxpayer Identification Numbers (ITINs) to open accounts without verified legal presence.

On paper, it targets financial crime. In practice, it directs banks to treat immigration status as a risk factor when deciding who gets a bank account, a credit card, or a mortgage.

## What the Order Actually Requires

The executive order does not ban non-citizens from banking. It doesn't mandate citizenship verification for every account holder. What it does is more subtle — and arguably more consequential.

Banks are now directed to identify and flag accounts where customers use ITINs or foreign-issued IDs rather than Social Security Numbers. They're told to evaluate "deportation risk" as a factor in assessing creditworthiness — the logic being that a borrower who might be removed from the country is a credit risk.

The order also encourages regulators to consider changes to the Bank Secrecy Act, potentially giving authorities expanded access to financial records during immigration-related investigations. Foreign consular ID cards — used by some immigrants to open bank accounts — are singled out for extra scrutiny.

## Who This Actually Hits

The primary target is undocumented immigrants who use ITINs for banking. But the blast radius is wider than that.

Consider H-4 visa holders — the spouses of H-1B workers, many of them Indian. Not all H-4 holders have Employment Authorization Documents (EADs), and those without work authorization typically use ITINs for tax filing and, in some cases, banking. Under the new order, their accounts could trigger enhanced review.

Indian-owned small businesses in heavily immigrant communities face a different kind of exposure. A desi grocery store or restaurant that serves a mixed-status customer base, processes payroll for workers on various visa types, or maintains business accounts with ITIN-linked transactions could find itself subject to increased reporting requirements and compliance costs.

Then there's the chilling effect. Trade groups warned before the signing that an order like this could lead to the "debanking" of millions of customers. "The bank regulators have always wanted as many financial transactions to go through the traditional financial systems," said Ed Mills, a Washington policy analyst with Raymond James. "This would have removed a lot of individuals from the financial system, which could create a national security risk as well."

## The Financial Surveillance Stack

The bank order doesn't exist in isolation. It's the third piece in what amounts to a financial surveillance architecture targeting immigrants:

First, the IRS-DHS data-sharing pipeline — in which the IRS admitted to handing over 42,000 taxpayer records to immigration enforcement before a federal judge shut it down. Second, the IRS is now considering adding a citizenship checkbox to next year's Form 1040. Third, this executive order recruits banks as frontline monitors of immigration status.

Together, these three moves create a system where an immigrant's tax filings, banking activity, and credit applications are all potential touchpoints for immigration enforcement — even for those legally present in the country.

## What Indian Americans Should Know

If you're on an H-1B with a Social Security Number, your bank account is unlikely to be directly affected. The order targets ITIN holders and alternative ID users, not SSN-based accounts.

But the order matters to the Indian American community in less direct ways. If your spouse is on an H-4 without an EAD and uses an ITIN, their financial activity just became subject to heightened scrutiny. If you run a business that employs people on various visa types, your payroll and business banking are now in the compliance crosshairs. If you wire money to family in India through services that also serve undocumented customers, those platforms may tighten their own verification procedures in response to the order.

The executive order is not law — it's a directive telling agencies and regulators how to interpret existing rules. But it sets the regulatory weather. Banks, which are already cautious about compliance, tend to over-correct when Washington signals enforcement priorities. The result is usually broader restrictions than the order technically requires, applied to more people than it technically targets.

For a community that has spent decades building financial lives in America — buying homes, starting businesses, saving for children's education — the signal is that the financial system is no longer neutral ground. It's becoming another front in immigration enforcement."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
