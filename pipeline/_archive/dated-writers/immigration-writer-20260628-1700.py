#!/usr/bin/env python3
"""Immigration writer — 2026-06-28 17:00 run."""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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


# ─────────────────────────────────────────────
# Article 1: Tourist Visa Wait Times
# ─────────────────────────────────────────────

art1_body = """India's five US consulates have never been this clogged. New data show that interview wait times for B-1/B-2 visitor visas at Hyderabad and Mumbai have ballooned to roughly 9.5 months — among the longest anywhere in the world. New Delhi sits at 7.5 months. Chennai, historically the quickest post in the country, has climbed to 5.5 months. Only Kolkata, India's lowest-volume consulate, has managed any improvement.

For Indian Americans accustomed to flying parents over for a grandchild's birthday or a Thanksgiving visit, the numbers amount to a quiet crisis. A family in the Bay Area filing a visitor visa petition for elderly parents in Hyderabad today cannot reasonably expect an interview before April 2027.

## The Social-Media Bottleneck

The surge traces directly to a Department of State directive issued on December 15, 2025, that expanded screening measures for all H-1B and H-4 visa applicants — and, in practice, rippled across every visa category at Indian posts. Consular officers now review applicants' LinkedIn profiles, Instagram accounts, Facebook pages, and other social-media footprints before adjudicating a case.

The State Department explicitly told applicants to set their profiles to "public" and warned that deleting or altering material after filing could raise credibility or misrepresentation concerns. Officers are specifically instructed to scan LinkedIn for activities related to "misinformation, disinformation, fact-checking, compliance and online safety."

The screening protocol has not been limited to work visas. Consulates across India have begun rescheduling tourist visa appointments en masse, often pushing them 90 to 120 days later without formal notice. Administrative processing times — the murky period after an interview when a case undergoes additional scrutiny — have also lengthened, compounding delays for applicants flagged for any reason.

## Why Indian Americans Should Care

The visitor visa queue is often the single thread connecting Indian American families to their extended network back home. Aging parents who need to visit for medical reasons, grandparents hoping to spend time with American-born grandchildren, siblings attending weddings — all now face a timeline that makes spontaneous travel impossible and planned visits precarious.

The delays also undercut Indian Americans professionally. Business visitors, conference speakers, and short-term consultants from India now need to plan nearly a year ahead, putting American companies with Indian operations at a disadvantage relative to competitors who can bring talent in from countries with shorter queues.

Immigration attorneys are advising clients to file early, apply at whichever consulate has the shortest wait (Chennai, for now), and consider emergency appointment requests where the situation warrants. But those workarounds have limits — emergency slots are scarce, and consulates have discretion to reject requests they deem non-urgent.

## No Quick Fix in Sight

The Department of State has not set a timeline for normalising wait times. Staffing at Indian consulates remains constrained, and the enhanced vetting protocols show no sign of being rolled back. If anything, the current administration has signalled that more scrutiny, not less, is the direction of travel.

For Indian Americans who built lives straddling two countries, the message is uncomfortable: the bridge that once connected them to home now has a nine-month toll booth at the entrance.

*Data cited in this article reflects the most recent consulate-level wait-time reporting as of late June 2026.*"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Nine Months to See Your Parents. Indian Consulates Are the Slowest They Have Ever Been",
    "subheadline": "Hyderabad and Mumbai tourist visa queues have hit 9.5 months. New social-media screening is the main bottleneck — and there is no fix in sight.",
    "slug": make_slug("india-us-tourist-visa-wait-times-consulate-record-high"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian Americans trying to bring parents, grandparents, or siblings for visits face nearly year-long waits — the longest ever at Indian consulates.",
    "tags": ["visa-wait-times", "consulate", "tourist-visa", "india", "social-media-vetting"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "AInvest", "url": "https://www.ainvest.com/news/longer-tourist-visa-queues-hyderabad-mumbai-delhi-face-delays-2606/"},
        {"name": "Nolo — 2026 Immigration Legal Updates", "url": "https://www.nolo.com/legal-updates/2026-immigration-legal-updates"},
        {"name": "U.S. Embassy India — Nonimmigrant Visas", "url": "https://www.usembassy.gov/india/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Visitors_to_the_U.S._Embassy_New_Delhi_in_July_2023_13.jpg/1280px-Visitors_to_the_U.S._Embassy_New_Delhi_in_July_2023_13.jpg",
    "image_caption": "Visitors at the U.S. Embassy in New Delhi during a July 2023 event",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ─────────────────────────────────────────────
# Article 2: Senator Marshall / Per-Country Caps
# ─────────────────────────────────────────────

art2_body = """A Republican senator from Kansas is not the figure most Indian Americans would expect to champion their cause. Yet Roger Marshall stood before a packed audience of Indian Americans last week and called the country-based green-card cap "fundamentally unjust" — then pledged to lead a legislative push to kill it.

"We are telling the world's hardest-working immigrants that the line is 70 years long," Marshall said, according to the American Bazaar. "Not because of what you did, but because too many of you came from the same place."

The line is not literally 70 years. But it might as well be.

## The Arithmetic of Absurdity

Under the Immigration and Nationality Act, the United States issues roughly 140,000 employment-based green cards each year — a ceiling that has not moved since 1990. No single country can receive more than 7 percent of the total, which works out to about 9,800 visas per year for India.

The problem: India generates well over half of all employment-based demand. According to the 2026 Green Card Backlog Report by WorkVisa Guide, an estimated 700,000 Indian nationals are now stuck in the queue. That is more people than the entire population of Washington, D.C.

The per-country cap means India — with 1.4 billion people and a tech-workforce pipeline that feeds Silicon Valley, Wall Street, and American hospitals — receives the same annual allocation as Liechtenstein, population 39,000.

On May 26, the Department of State confirmed what many already suspected: all EB-2 immigrant visas for Indian applicants in fiscal year 2026 have been exhausted. The category is now marked "unavailable" in the July 2026 Visa Bulletin and will stay that way until October 1, when the new fiscal year resets the numbers.

## Why Marshall?

Marshall is a physician-turned-politician from the Great Bend, Kansas, area — not a traditional ally of the tech-industry immigration lobby. But his state is home to a growing Indian American professional community, and his brand of Republicanism has long emphasised merit-based immigration.

His pledge to eliminate per-country caps puts him in alignment with a bipartisan tradition. The Fairness for High-Skilled Immigrants Act has passed the House before — overwhelmingly, in 2019, by a 365-65 vote — and cleared the Senate unanimously in 2020. Both times, the two chambers failed to reconcile their versions before the legislative session expired.

A version of the bill was reintroduced in the current Congress. The House Judiciary Committee advanced it. But in a Washington consumed by border enforcement, budget fights, and an administration openly hostile to legal immigration expansion, the bill's prospects remain uncertain.

## What the Diaspora Wants to Hear

For Indian Americans, the green-card backlog is not an abstract policy debate. It is the H-1B engineer in Sunnyvale who filed an I-140 petition in 2012 and still cannot sponsor herself for permanent residency. It is the EB-2 applicant whose priority date is September 2013 — thirteen years ago — who now learns that even that date is no longer current.

The backlog shapes every major life decision: whether to buy a house, start a business, change jobs, or risk travelling to India and re-entering the United States. It keeps families in a permanent state of legal limbo, tied to a single employer for decades by a system that rewards patience over talent.

Marshall's rhetoric is welcome. But Indian Americans have heard these promises before — from both parties, across multiple administrations. The Fairness Act's graveyard is littered with bipartisan enthusiasm that never survived a conference committee.

The question is not whether the system is unjust. Even its defenders struggle to argue otherwise. The question is whether anyone in Washington will spend political capital to fix it — or whether 700,000 people will keep waiting for a line that moves at the speed of geological time."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "A Republican Senator Calls the Green-Card Backlog 'Fundamentally Unjust.' 700,000 Indians Are Still Waiting",
    "subheadline": "Roger Marshall pledged to eliminate per-country caps. The same promise has died in Congress twice before.",
    "slug": make_slug("roger-marshall-green-card-per-country-cap-india-700k-backlog"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "700,000 Indians are trapped in the employment-based green-card backlog. A Kansas Republican says the per-country cap is unjust — but legislative history suggests the fix will not come easy.",
    "tags": ["green-card", "per-country-cap", "roger-marshall", "eb2", "backlog", "fairness-act"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Times Now World", "url": "https://www.timesnowworld.com/us-news/eb2-visa-india-quota-elimination-roger-marshall-article-154771787"},
        {"name": "WorkVisa Guide — 2026 Green Card Backlog Report", "url": "https://www.workvisaguide.com/"},
        {"name": "Fragomen — House Passes Bill to Eliminate Per-Country Limits", "url": "https://www.fragomen.com/insights/house-passes-bill-to-eliminate-per-country-limits-on-employment-based-green-cards.html"},
        {"name": "The American Bazaar", "url": "https://www.americanbazaaronline.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Roger_Marshall_117th_Congress_portrait.jpg/330px-Roger_Marshall_117th_Congress_portrait.jpg",
    "image_caption": "Senator Roger Marshall (R-Kansas) in his official 117th Congress portrait",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}


# ─────────────────────────────────────────────
# Insert
# ─────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
