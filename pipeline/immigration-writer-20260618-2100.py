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

article1_body = """A federal judge in Boston has thrown out the $100,000 surcharge that the Trump administration slapped on new H-1B petitions, handing employers immediate relief and Indian professionals a moment of cautious optimism. But the more important fact about Judge Leo Sorokin's June 8 ruling is that it does not settle anything. It deepens a split between federal courts that now points in exactly one direction: the Supreme Court.

## What the ruling actually says

Sorokin, of the U.S. District Court for Massachusetts, vacated Presidential Proclamation 10973, the September 2025 order that bolted a $100,000 charge onto H-1B petitions filed for workers outside the United States. His reasoning was narrow and, for that reason, durable. The charge, he held, is a tax — not a regulatory fee — regardless of what the administration chose to call it.

The distinction matters. A regulatory fee recovers the cost of providing a service; it is compensatory. A tax raises revenue; it is fiscal. USCIS does not spend anything close to $100,000 adjudicating a single petition, so the figure bore no relationship to administrative cost. The label "regulatory payment" did not survive contact with the substance. And under Article I of the Constitution, the power to tax belongs to Congress, not the president.

Two further findings reinforced the result. The proclamation skipped the notice-and-comment rulemaking the Administrative Procedure Act requires, denying employers, hospitals and universities any chance to weigh in before their filing costs jumped more than thirteenfold. And it amounted to a separation-of-powers breach: the executive had imposed a heavy financial obligation on a defined class of private actors with no congressional authorisation.

## Why a win is not a settlement

Here is the catch. On December 23, 2025, Judge Beryl Howell in the District of Columbia reached the opposite conclusion in *Chamber of Commerce v. DHS*, treating the same charge as a permissible condition on entry. That case is on appeal, and in that proceeding the fee remains in effect until the proclamation expires on its own terms in September 2026. A third lawsuit, filed in San Francisco by religious and labour groups, could yet produce a third answer.

So the country now has two district courts saying opposite things about the same policy. If the First Circuit affirms Boston and the D.C. Circuit affirms Washington, the question lands squarely before the Supreme Court: does the president's authority to set conditions on entry stretch far enough to impose what is, in effect, a tax — without Congress signing off? The justices' February 2026 decision striking down the administration's tariffs supplies a framework, but it arose in trade law. Mapping it onto immigration requires the Court to say something it has not yet said out loud.

## What it means for Indians

Indians account for more than 70% of approved H-1B petitions in a typical year, which means no group has more riding on the outcome. The immediate practical effect of the Boston ruling is nationwide: as of June 8, USCIS cannot collect the $100,000 surcharge, and employers filing fresh petitions for workers abroad can do so at pre-proclamation rates of roughly $960 to $7,595. For Indian graduates waiting on cap-subject petitions before the June 30 filing deadline, that removes a barrier that had quietly frozen entry-level hiring.

But two cautions deserve underlining. First, the ruling says nothing about refunds. Indian employers and the workers who, in some cases, footed the bill between September 2025 and June 8 have no path to getting that money back from this decision. That will take separate litigation or agency guidance, neither of which is on the horizon. Anyone who paid should keep meticulous records.

Second, plan for reversal. The D.C. ruling points the other way, the government will almost certainly appeal to the First Circuit, and a stay pending appeal is not far-fetched given the conflicting outcomes below. A family weighing whether to travel, switch employers, or file now should treat the current relief as provisional, not permanent.

The broader principle is the one to watch. Courts are converging on a structural idea — that the executive cannot raise revenue without explicit congressional authorisation, whatever statute it invokes. The tariff case said it in trade. Boston says it in immigration. For the Indian diaspora, whose presence in America runs through a visa system increasingly governed by proclamation rather than legislation, the question of where executive power ends is no longer abstract. It is the difference between a $7,000 filing and a $107,000 one — and right now, the answer depends on which courthouse you are standing in.

**Sources:** LiveLaw, "Taxing Entry: H-1B Surcharge And Constitutional Limits On Executive Revenue Power"; Associated Press via Audacy, "Federal judge strikes down Trump's $100,000 fee on new H-1B visas." *State of California v. Mullin*, No. 1:25-cv-13829-LTS (D. Mass. June 8, 2026)."""

article2_body = """While the Indian diaspora in America frets over H-1B fees and green-card backlogs, New Delhi has quietly tightened its own rules for foreigners living in India — and the fine print reaches further into NRI and OCI households than the headline suggests. On June 1, the Ministry of Home Affairs notified the Immigration and Foreigners (Amendment) Rules, 2026, trimming a long-standing grace period and adding a new reporting duty for children who pick up foreign citizenship.

## The 14-day cushion is gone

The headline change is administrative but consequential. Until now, a foreign national who wanted to stay in India beyond their permitted period had a 14-day grace window to register with the local Foreigners Registration Officer (FRO). The amendment removes it.

Under the new framework, anyone on a visa that caps stay at 180 days, but who intends to remain longer, must register with the FRO *before* the initial 180-day period expires. The same applies to holders of longer-validity visas that carry a condition limiting any single stay to 180 days: register before the 180th day if you plan to stay on, whether continuously or cumulatively across a calendar year. And extensions past that limit will now be granted only in "emergent circumstances" — a deliberately narrow phrase.

For most short-term visitors this changes little. But for the slice of the diaspora that spends long stretches in India — retirees splitting the year between Edison and Hyderabad, foreign-passport-holding spouses of Indian citizens, professionals on extended assignments — the disappearance of the buffer raises the cost of a missed deadline. A clerical slip that was once forgivable within a fortnight now risks being an overstay.

## A new duty when a child becomes foreign

The second change cuts both ways. On the relief side, the amendment ends an old irritant: where either parent is an Indian citizen and wants the child to retain Indian citizenship, parents no longer have to notify the FRO of the child's birth. That removes a paperwork trap that had snagged mixed-nationality families.

But the rules add a fresh obligation pointing the other way. If a child born in India later acquires the citizenship of another country while still living in India, the parents must inform the FRO within 30 days of that acquisition. For diaspora families who return to India with young children and subsequently naturalise them abroad — or whose children acquire foreign citizenship by descent — this is a new compliance checkpoint that did not exist before.

## Why NRIs and OCI holders should read the fine print

It is tempting for Indian Americans to file this under "domestic Indian housekeeping." That would be a mistake. India does not recognise dual citizenship, and the people most likely to be caught by these rules are precisely those straddling two countries: an OCI cardholder is not a foreign national for many purposes, but a foreign-passport-holding spouse, parent or adult child living in India often is.

Consider the common scenarios. A U.S.-citizen spouse of an Indian national living in Bengaluru on a long-stay visa now has a harder registration deadline and no grace period. A green-card or citizenship-bound child born during a stint in India, who later takes American citizenship, triggers a 30-day reporting clock the family may not know is running. None of this is punitive on its face — the government frames it as "enhancing oversight" — but oversight regimes punish the uninformed, and diaspora families are disproportionately the uninformed here precisely because they assume Indian rules do not apply to them.

The practical takeaway is unglamorous but real: if your household includes a foreign passport and a long Indian stay, treat the FRO deadline like a visa expiry, not a formality. Mark the 180-day date. Track any change in a child's citizenship. And do not count on the old fortnight of slack, because it no longer exists.

The amendment does not overhaul India's immigration architecture, and lawyers who drafted explainers this week were careful to say so. But it tightens the bolts in exactly the places where diaspora families tend to be loosest — the long visits, the mixed-nationality marriages, the children who grow up across borders. For a community that prides itself on moving freely between two homes, the message from New Delhi is quiet but clear: the second home is keeping closer count.

**Sources:** Bar & Bench, "India's 2026 Immigration Rules: Stricter registration and new reporting for children of foreign nationals" (Dipak Rao and Nishita Arora, Singhania & Partners); Ministry of Home Affairs, Immigration and Foreigners (Amendment) Rules, 2026 (notified June 1, 2026)."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Judge Killed the $100,000 H-1B Fee. Why Indians Shouldn't Celebrate Just Yet",
        "subheadline": "A Boston court struck down Trump's surcharge nationwide on June 8 — but a conflicting D.C. ruling means the real fight is now headed for the Supreme Court, and nobody's getting refunds.",
        "slug": make_slug("h1b-100k-fee-struck-down-boston-circuit-split-supreme-court-refunds"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians make up over 70% of approved H-1B petitions, so no group has more riding on whether the $100,000 surcharge survives appeal — and the current relief is provisional, not permanent.",
        "tags": ["h1b", "uscis", "100k-fee", "supreme-court", "immigration", "litigation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "LiveLaw — Taxing Entry: H-1B Surcharge And Constitutional Limits On Executive Revenue Power", "url": "https://www.livelaw.in/articles/taxing-entry-h-1b-surcharge-constitutional-limits-executive-revenue-power-538019"},
            {"name": "Associated Press via Audacy — Federal judge strikes down Trump's $100,000 fee on new H-1B visas", "url": "https://www.audacy.com/news/national/federal-judge-strikes-down-trumps-100000-fee-on-new-h-1b-visas"},
            {"name": "NBC Palm Springs — Federal Judge Blocks $100,000 Fee on H-1B Visa Applications", "url": "https://nbcpalmsprings.com/2026/06/15/federal-judge-blocks-100000-fee-on-h-1b-visa-applications/"}
        ]),
        "score_total": 86,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36984937/pexels-photo-36984937.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The United States Supreme Court building, where the conflicting rulings on the H-1B surcharge are likely to be resolved",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Quietly Tightened Its Rules for Foreigners — and It Reaches NRI Families Too",
        "subheadline": "New Delhi's June 1 amendment scraps the 14-day registration grace period and adds a citizenship-reporting clock for children — small print that catches mixed-nationality diaspora households first.",
        "slug": make_slug("india-2026-immigration-rules-fro-registration-grace-period-nri-oci-children"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "OCI households with a foreign-passport-holding spouse, parent, or child living in India now face harder FRO deadlines and a new 30-day reporting duty — and diaspora families are most likely to assume the rules don't apply to them.",
        "tags": ["india", "oci", "fro", "nri", "immigration", "registration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Bar & Bench — India's 2026 Immigration Rules: Stricter registration and new reporting for children of foreign nationals", "url": "https://www.barandbench.com/leading-questions/indias-2026-immigration-rules-stricter-registration-and-new-reporting-for-children-of-foreign-nationals"},
            {"name": "Ministry of Home Affairs — Immigration and Foreigners (Amendment) Rules, 2026", "url": "https://www.mha.gov.in/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Indian_Passport_01.jpg/1280px-Indian_Passport_01.jpg",
        "image_caption": "An Indian passport; New Delhi's amended rules most affect foreign-passport-holding members of NRI and OCI households",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": article2_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']} ({wc} words): {e}")
