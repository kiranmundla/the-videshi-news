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

body1 = """While the Indian-American conversation stays glued to H-1B fees and green-card backlogs in Washington, New Delhi has been quietly redrawing the rules for the diaspora's own paperwork at home. A pair of notices issued this week tightens what Overseas Citizen of India (OCI) cardholders can do without prior permission — and adds a reporting duty most NRIs have never heard of.

## What changed this week

The Ministry of Home Affairs published the Immigration and Foreigners (Amendment) Order, 2026, on June 18, formally folding the term "Overseas Citizen of India Cardholder" into the country's immigration framework and aligning it with the Citizenship Act, 1955. On paper that reads like housekeeping. In practice it hard-wires OCI status into the same enforcement architecture the government uses for ordinary foreign nationals, complete with permit rules and a revised list of protected border zones in Rajasthan.

Alongside it, immigration advisories flagged renewed enforcement of an older requirement that many cardholders had treated as dormant. OCI holders who work as research scholars at universities, undertake journalistic activity, do certain missionary work, or want to visit a Protected, Restricted or Prohibited area must obtain special permission in advance — from the relevant Indian consular post, the Foreigners Regional Registration Office (FRRO), or another designated authority. Violations can expose not just the individual but the employing university or organisation to penalties that the government has pointedly left undefined.

## The reporting duty almost nobody follows

The change with the widest reach is the smallest in print. OCI cardholders living in India must now email the jurisdictional FRRO or Foreigners Registration Office whenever their permanent Indian address or their occupation changes. There is no fee and no in-person visit — an email with name, OCI number, passport number and the old and new details is enough. But there is also no broad public-awareness campaign, and the penalties for skipping it are unspecified.

This sits on top of a rule structure many cardholders misunderstand. OCI holders remain exempt from routine FRRO registration regardless of how long they stay — that much has not changed since 2021. What is changing is the expectation that they actively notify the state about the texture of their lives in India: where they live, what they do for a living, when they take up research or media work.

## Why this lands on the diaspora first

For the Indian American who carries an OCI card as a convenience — visa-free entry, the right to buy non-agricultural property, the ability to live in India indefinitely — the value proposition has always been "almost a citizen, minus the vote." This week's tightening nudges that bargain. The card now comes with more affirmative obligations and a sharper enforcement edge, even as full citizenship stays off the table.

The people most exposed are the ones who use the card most heavily: retirees who split the year between, say, New Jersey and Hyderabad; foreign-passport-holding spouses of Indian citizens running a household in India; and the growing cohort of diaspora academics and journalists who spend research stints at Indian institutions. For a Stanford-affiliated scholar planning fieldwork in India, "get prior permission" is no longer a footnote — it is a compliance step with institutional liability attached.

## The unsettling part: undefined penalties

Twice in this week's guidance, the consequence of non-compliance is described as "penalties" with no figure, no schedule, and no clear process. Immigration lawyers tend to read that as discretion, and discretion is precisely what makes diaspora families nervous in a year when the United States is revoking visas mid-stay and India is standing up a high-level committee on demographic change. Section 7D of the Citizenship Act already lets the government cancel an OCI registration for violating conditions — a power that, once triggered, is far harder to reverse than a missed email.

None of this amounts to a crackdown on the scale of what NRIs face at U.S. consulates. But it is a reminder that the diaspora now answers to two tightening systems at once. The OCI card was sold as the frictionless half of the deal. This week, New Delhi added a little friction — and left the size of the fine to the imagination.

## What to do now

The practical takeaways are unglamorous but cheap: keep your OCI passport details current online whenever you renew a passport, email your jurisdictional FRRO if your Indian address or occupation changes, and secure written permission before any research, journalism, missionary work, or travel to a protected area. In a regulatory climate where the penalty is "to be determined," the safest number to aim for is zero violations."""

body2 = """The diaspora's most stubborn demand is back on the table, and this time it is written into a formal resolution. At its convention, the Global Organization of People of Indian Origin (GOPIO) passed a resolution calling on New Delhi to grant full dual nationality to Overseas Citizen of India (OCI) cardholders — putting OCI holders "at par" with Indian citizens for doing business in India, and even extending Aadhaar to NRIs who remain Indian citizens.

It is a familiar ask with fresh urgency. For decades, the diaspora has wanted what India has always refused: genuine dual citizenship, complete with the vote and unqualified rights. The OCI card was the compromise — lifelong visa-free entry, the right to live and work in India indefinitely, property rights short of farmland. What it withholds is just as defining: no vote, no public office, no agricultural land, and, as this month's rule changes underline, a status that remains legally "foreign."

## Why the timing matters

The resolution lands in a week when both halves of the diaspora's life are tightening at once. In the United States, Indians on H-1Bs are watching a $100,000 fee fight wind toward the courts, EB-2 India has gone dark in the July visa bulletin, and consulates are booking interviews up to a year out. In India, the Ministry of Home Affairs has just folded OCI cardholders deeper into its immigration enforcement framework and added new reporting duties on address and occupation.

Caught between two systems that each treat them as outsiders, diaspora bodies are pressing the one government that calls them its own. GOPIO's resolution frames participation in India's growth — its "Suvarna Kaal," or golden era — as the prize, and full dual nationality as the unlock.

## What full dual nationality would actually change

The gap between OCI and citizenship is not academic. An OCI holder cannot vote in Indian elections, hold a constitutional office, or buy agricultural land. They face sector-specific limits on certain professional and business activities. And, as the 2026 amendments made clear, they are still foreign nationals who must seek prior permission for research, journalism, or visits to protected areas — and now must notify the FRRO when their address or occupation changes.

Full dual nationality, as GOPIO envisions it, would erase most of that — letting a software founder in Austin or a doctor in Manchester operate in India on the same footing as a resident citizen, Aadhaar and all. For a diaspora that sends tens of billions of dollars home in remittances each year and increasingly wants to invest, build, and retire in India, the friction is no longer sentimental. It is commercial.

## The wall India keeps rebuilding

The obstacle is constitutional and political, not clerical. India does not permit dual citizenship — the Constitution and the Citizenship Act, 1955 are built around single allegiance, and successive governments have treated that as settled. The 2026 citizenship rules went the other way on a related point, clarifying that a minor cannot simultaneously hold an Indian and a foreign passport, closing rather than opening the door.

That is why a convention resolution, however well-supported, is a long way from law. Granting true dual nationality would require Parliament to amend the citizenship framework and would reopen sensitive questions about voting rights, security clearances, and the meaning of allegiance — debates Indian governments have historically preferred to avoid.

## Why Indian Americans should still pay attention

Even if full dual nationality remains aspirational, the push shapes the incremental wins that actually arrive. The OCI card itself, the e-OCI digital registration rolled out this year, and periodic expansions of NRI banking and investment rights all emerged from exactly this kind of sustained diaspora lobbying. Resolutions like GOPIO's set the ceiling that negotiations work down from.

For the Indian American weighing whether to deepen roots in India — buy a second home, start a venture, plan a retirement that straddles two countries — the dual-nationality debate is the quiet variable underneath. It determines whether the card in their wallet stays a travel convenience or eventually becomes something closer to belonging. This week, the diaspora's organised voice asked, again, for the latter. New Delhi's answer, as ever, will come slowly — if at all."""

body3 = """The visa delay that stranded thousands of Indian professionals in India this year was supposed to be their problem. It is turning into their employers' problem too — and the bill could come from the Indian taxman.

When the U.S. State Department abruptly expanded social media screening for visa applicants in mid-December and rescheduled interview appointments, many H-1B workers who had flown to India to see family or renew their stamps found themselves unable to return. Some appointments slid as far out as 2027. With months to kill and jobs to keep, the obvious workaround was to keep working remotely from India. That workaround has a tax trap buried inside it.

## The "permanent establishment" problem

Under international tax principles, if an employee performs core business functions from a country for long enough, the foreign company they work for can be deemed to have a taxable presence there — a "permanent establishment." Once that threshold is crossed, the company can be required to pay corporate tax in India on the profits attributable to that activity and to comply with a thicket of local reporting obligations.

Tax advisers are warning U.S. employers that a stranded engineer writing code from Bengaluru for months is not a neutral act. "Allowing them to work remotely for an extended period could result in a so-called permanent taxable entity," KPMG India's national head of global mobility tax, Parizad Sirwalla, told Bloomberg Law, urging companies to analyse carefully what tasks workers can safely perform while in the country.

## Why this is an Indian-American story, specifically

India is the single largest source of H-1B workers — in December 2024, nearly 17,000 H-1B visas were issued in Chennai alone — so when consular screening seized up, the people stranded were overwhelmingly Indian nationals with U.S. jobs and U.S. lives. Their children's schooling stalled, their leases sat empty, and their employers were left improvising.

That makes the permanent-establishment risk a peculiarly diaspora dilemma. The worker wants to stay productive and keep the paycheck. The employer wants the work done. But the longer the arrangement runs, the more it looks, to Indian tax authorities, like the U.S. company is operating in India through that employee. The result is a standoff where doing the sensible thing — working remotely until the appointment clears — quietly accumulates liability for the firm.

## The options, none of them clean

Employers facing this have a short menu, and every item has a cost. They can cap the kind of work a stranded employee does, steering them away from revenue-generating or decision-making functions that strengthen a permanent-establishment claim — which often means paying someone to do less. They can put the worker on unpaid leave, which protects the company but punishes the employee. Or they can keep the arrangement and absorb the tax and compliance exposure, betting the stay will be short.

If the delay drags on and a company decides it cannot keep a stranded worker on payroll, the worker is thrown back into the broader H-1B nightmare: finding a new employer willing to sponsor them — and, if the rules tighten further, willing to shoulder the costs that come with new petitions in an increasingly expensive system.

## The wider squeeze

The tax wrinkle is one symptom of a deeper dysfunction. The same social-media-vetting policy that stranded these workers has lengthened consular waits across India, with Mumbai and Chennai booking first-time H-1B and H-4 interviews months out. Employers were already budgeting thousands of dollars per assignee for "visa runs" to third-country posts like Singapore or Warsaw. Now they have to factor in cross-border tax advice for employees who never intended to work from India in the first place.

For Indian Americans, the lesson is uncomfortable: a routine trip home to renew a visa can metastasise into a months-long limbo that complicates not just their own status but their employer's tax position. The advice from mobility specialists is to plan defensively — understand before you travel what remote work your employer will and won't permit from India, get the interview booked as early as possible, and treat a quick stamping trip as anything but quick.

The visa backlog was sold as an inconvenience. For the companies that employ India's skilled workforce, it is becoming a line item — and for the workers caught in it, one more reason that the path between two countries they belong to keeps getting narrower."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India Quietly Put OCI Cardholders on a Tighter Leash — and Most of the Diaspora Missed It",
        "subheadline": "New Delhi's June 18 amendment folds OCI status deeper into immigration enforcement and revives a reporting duty almost no cardholder follows — with penalties left deliberately undefined.",
        "slug": make_slug("oci-cardholders-tighter-enforcement-frro-reporting-amendment-2026-diaspora"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "OCI cardholders are the diaspora's main legal tie to India, and the new rules add reporting duties and permission requirements that hit NRIs who live, research, or retire part-time in India first.",
        "tags": ["oci", "india", "frro", "diaspora", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "SCC Times — Immigration & Foreigners Amendment Order 2026 Explained", "url": "https://www.scconline.com/blog/post/2026/06/19/immigration-foreigners-amendment-order-2026-explained/"},
            {"name": "Fragomen — Increased Enforcement and New Notification Rule for OCI Cardholders", "url": "https://www.fragomen.com/insights/increased-enforcement-and-new-notification-rule-for-overseas-citizen-of-india-cardholders.html"},
            {"name": "Mondaq — Citizenship Amendment Rules 2026: OCI Cardholders", "url": "https://www.mondaq.com/india/general-immigration/citizenship-amendment-rules-2026"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Overseas_Citizen_of_India_card.jpg/1280px-Overseas_Citizen_of_India_card.jpg",
        "image_caption": "An Overseas Citizen of India (OCI) card, the diaspora's primary legal link to India",
        "image_attribution": "Wikimedia Commons",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Diaspora's Oldest Demand Is Back: GOPIO Wants Full Dual Nationality, Not Just an OCI Card",
        "subheadline": "A convention resolution asks New Delhi to put OCI holders on par with citizens — landing in a week when the diaspora is squeezed by tightening rules in both Washington and India.",
        "slug": make_slug("gopio-resolution-full-dual-nationality-oci-citizenship-diaspora-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Full dual nationality would let Indian Americans live, invest, and retire in India on the same footing as citizens — the difference between the OCI card being a travel convenience or genuine belonging.",
        "tags": ["oci", "dual-nationality", "gopio", "diaspora", "citizenship"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — GOPIO Passes Resolution for Full Dual Nationality at The Convention", "url": "https://theindianeye.com/gopio-passes-resolution-for-full-dual-nationality-at-the-convention/"},
            {"name": "SCC Times — Citizenship (Amendment) Rules, 2026: OCI Registration", "url": "https://www.scconline.com/blog/post/2026/05/citizenship-amendment-rules-2026-oci-registration/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Indian_Passport_03.jpg/1280px-Indian_Passport_03.jpg",
        "image_caption": "An Indian passport — the citizenship document OCI cardholders are not entitled to hold",
        "image_attribution": "Wikimedia Commons",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Stranded in India on a Visa Delay, H-1B Workers Are Now a Tax Headache for Their Own Employers",
        "subheadline": "Months-long consular backlogs left thousands of Indian professionals working remotely from India — and tax advisers warn that can saddle their U.S. employers with an Indian tax bill.",
        "slug": make_slug("h1b-workers-stranded-india-visa-delay-permanent-establishment-tax-employers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the largest source of H-1B workers, so the visa backlog that stranded them now complicates not just their own status but their employers' tax exposure — making a routine trip home a corporate liability.",
        "tags": ["h1b", "india", "tax", "visa-backlog", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Bloomberg Law — H-1B Workers Stranded in India Create Tax Dilemma for Employers", "url": "https://news.bloomberglaw.com/daily-tax-report/h-1b-workers-stranded-in-india-create-tax-dilemma-for-employers"},
            {"name": "The Indian Eye — US Embassy in India warns visa screening continues after visa is granted", "url": "https://theindianeye.com/us-embassy-in-india-warns-visa-holders-that-visa-screening-continues-even-after-visa-is-granted/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/392265/pexels-photo-392265.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An international airport terminal, where stranded H-1B workers await rescheduled visa interviews",
        "image_attribution": "Pexels",
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']} ({wc} words)")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
