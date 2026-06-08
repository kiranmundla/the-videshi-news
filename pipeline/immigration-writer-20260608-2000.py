#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-08 20:00 UTC run"""

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

# ──────────────────────────────────────────────────
# ARTICLE 1: $100K H-1B Fee Struck Down
# ──────────────────────────────────────────────────

art1_body = """A federal judge in Boston has struck down the $100,000 fee that President Donald Trump imposed on new H-1B visa petitions last September, ruling that the charge amounted to an unlawful tax that Congress never authorised. The decision, handed down on Monday by U.S. District Judge Leo Sorokin, is the most significant legal blow yet to the administration's campaign to price foreign skilled workers out of the American labour market.

Sorokin's 42-page opinion in the case — brought by 20 Democratic state attorneys general — cut through the administration's semantic gymnastics. The White House had argued the payment was a "monetary penalty" the president could impose under immigration law. Sorokin disagreed. "The substance and application of the $100,000 payment reveal that it is a tax, regardless of what the payment is called," he wrote, citing the Supreme Court's February ruling that struck down Trump's sweeping tariffs under a national-emergency law. The same logic applied: the president cannot levy a tax without congressional authority.

## The Numbers Tell the Story

The fee's brief, chaotic tenure left a trail of damage. Since the proclamation took effect in September, USCIS received just 85 payments of the $100,000 charge — a figure that underscores how effectively the fee functioned as a deterrent rather than a revenue source. Employers that had previously paid $2,000 to $5,000 per H-1B petition simply stopped filing. Technology companies, universities, and healthcare systems all pulled back sponsorships, and several filed amicus briefs describing the operational fallout.

The programme offers 65,000 visas annually, with an additional 20,000 for workers holding advanced degrees. In a normal year, demand far exceeds supply. This year, the demand collapsed — not because employers no longer needed the talent, but because the price tag made sponsorship economically irrational for all but the most desperate hires.

## What This Means for Indian Workers

Indian nationals account for roughly 70 per cent of all H-1B approvals in a typical year, and Indian IT services firms — Infosys, TCS, Wipro, Cognizant — are among the programme's heaviest users. The $100,000 fee hit this ecosystem hardest. Several large Indian IT firms had already begun shifting project delivery to India rather than absorbing the fee, accelerating a trend that was reshaping the global technology supply chain.

The ruling does not guarantee immediate relief. The White House has signalled it will appeal. Spokesperson Taylor Rogers said the administration is "confident this order will be reversed," pointing to a December decision by a different judge in Washington, D.C., who upheld the fee. That case, brought by the U.S. Chamber of Commerce and the Association of American Universities, is already before the D.C. Circuit Court of Appeals.

## The Legal Landscape

Sorokin's ruling creates a circuit split — one federal judge has upheld the fee, another has struck it down. The divergence makes Supreme Court review increasingly likely, though not imminent. In the meantime, the Boston ruling vacates the fee "in its entirety," meaning employers filing in jurisdictions covered by Sorokin's order can proceed without paying the $100,000 charge.

For the roughly 400,000 Indian professionals currently working on H-1B visas in the United States, the ruling offers a measure of stability at a moment when virtually every other pathway — green cards, OPT, adjustment of status — is under assault. It does not solve the structural problems. EB-2 India priority dates remain stuck in 2014. The Chip Roy bill threatens to eliminate the H-1B's role as a green card stepping-stone entirely. USCIS processing times continue to lengthen.

But for employers weighing whether to sponsor their next hire, the calculus just changed. A $5,000 filing fee is a cost of doing business. A $100,000 fee was a shutdown notice. Monday's ruling, at least for now, tears up that notice."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Hundred-Thousand-Dollar Wall Just Fell — A Federal Judge Says Trump's H-1B Fee Is an Illegal Tax",
    "subheadline": "Judge Leo Sorokin's 42-page ruling in Boston vacates the fee that had reduced H-1B filings to a trickle, but the White House promises an appeal and a circuit split makes the Supreme Court the likely final arbiter.",
    "slug": make_slug("100k-h1b-fee-struck-down-judge-sorokin-illegal-tax"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals hold roughly 70% of all H-1B visas. The $100,000 fee had already pushed major Indian IT firms to shift operations back to India rather than pay it. This ruling reopens the door for employer-sponsored H-1B hires, though the appeal and circuit split mean the reprieve may be temporary.",
    "tags": ["h1b", "uscis", "100k-fee", "court-ruling", "trump", "immigration-law"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-08/"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/08/trump-h1b-visa-fee-struck-down/"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/65/2008_MoakleyCourthouse_Boston_2669012840.jpg",
    "image_caption": "The John Joseph Moakley Federal Courthouse in Boston, where Judge Sorokin issued the ruling",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}

# ──────────────────────────────────────────────────
# ARTICLE 2: $750 Fast-Track Visa Appointments
# ──────────────────────────────────────────────────

art2_body = """The State Department on Monday unveiled a new premium option for business and tourist visa applicants: pay $750 and get a consular interview appointment within 10 business days. The programme, published as a temporary final rule effective July 1, is aimed squarely at the FIFA World Cup, which kicks off in the United States this month. But for Indians navigating America's increasingly hostile visa infrastructure, the timing raises uncomfortable questions about who gets to buy their way to the front of the line.

## How It Works

The expedited appointment option applies exclusively to B-1 (business) and B-2 (tourist) visa applicants. After paying the standard visa application fee — currently $185 — applicants can add the $750 surcharge for a guaranteed interview slot within two weeks. The service will be offered only at select consular posts, which the State Department says it will identify on its website before the July 1 launch.

The mechanics are straightforward: pay more, wait less. The State Department framed the move as a response to "temporary surges in demand" driven by the World Cup, which is being co-hosted by the United States, Canada, and Mexico. FIFA projects millions of spectators will attend matches across 16 American cities, and many will need visas from countries without waiver agreements.

## The Indian Context

India is one of the highest-volume sources of B-1/B-2 visa applications in the world, and wait times at U.S. consulates in Mumbai, Delhi, Chennai, Hyderabad, and Kolkata have been painfully long for years. During the post-pandemic backlog, some applicants waited more than a year for an interview slot. The enhanced social-media vetting policy introduced last December made things worse, slashing daily interview capacity by as much as 40 per cent at some Indian posts and pushing rescheduled appointments out by 90 to 120 days.

For Indian families, B-2 visas are not a luxury. They are the way parents visit their children settled in America, the way grandparents meet newborn grandchildren, the way families gather for weddings and festivals. The idea of a $750 fast lane will appeal to those who can afford it — and sting those who cannot.

The programme's scope is deliberately narrow. It covers only B-1 and B-2 visas, not H-1B, H-4, L-1, F-1, or any employment or student category. Workers caught in the H-1B stamping nightmare — appointments cancelled, rescheduled to months later, visas revoked over old arrest records — get nothing from this announcement. The premium lane is reserved for short-term visitors, not the people whose lives and careers depend on the consular machinery.

## The Optics Problem

The juxtaposition is hard to ignore. The same administration that imposed a $100,000 fee on H-1B petitions — today struck down by a federal judge in Boston — is now offering expedited service for tourists willing to pay $750. The message, intended or not, is that America wants your vacation dollars but not your labour.

For the Indian tech worker whose H-1B stamping appointment was pushed from December to March, who is working remotely from India while their employer grows impatient, who watches FIFA fans get a two-week turnaround for a tourist visa — the policy feels like a pointed reminder of where skilled immigrants rank in the queue.

Whether the expedited option reaches Indian consular posts at all remains to be seen. The State Department said the service will launch at "a limited number of posts," without specifying which ones. If New Delhi and Mumbai are included, demand could overwhelm the programme before the World Cup's first match. If they are excluded, the announcement will register as yet another policy designed for everyone except the people who need consular efficiency the most.

The $750 fee is refundable if the appointment cannot be scheduled within the promised window. The visa itself, of course, is not guaranteed — applicants must still clear the interview and all security checks. For Indian applicants accustomed to the current system, the idea of a guaranteed timeline will feel almost radical, even at a price."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Seven Hundred and Fifty Dollars for a Two-Week Appointment — America Rolls Out a Fast Lane for Tourist Visas",
    "subheadline": "The State Department's new expedited B-1/B-2 visa appointment service launches July 1 for the FIFA World Cup, but Indians waiting months for H-1B stamping slots will not benefit.",
    "slug": make_slug("750-expedited-visa-appointment-b1-b2-fifa-world-cup"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "India is one of the highest-volume B-1/B-2 applicant countries. Indian families routinely wait months for visitor visas to see relatives in the US. The $750 fast lane may help some, but its exclusion of employment visa categories — while H-1B stamping waits stretch to 120 days — highlights the two-tier system Indian applicants face.",
    "tags": ["visa", "b1-b2", "state-department", "consular", "fifa-world-cup", "expedited-visa"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/us-offers-expedited-business-tourist-visa-services-for-750-fee"},
        {"name": "State Department Federal Register", "url": "https://www.federalregister.gov/"},
        {"name": "NPR / WAMC", "url": "https://www.wamc.org/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An open passport with various visa stamps from international travel",
    "image_attribution": "Pexels",
    "body": art2_body
}

# ──────────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text[:300]}")
