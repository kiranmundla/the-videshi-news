#!/usr/bin/env python3
"""Immigration writer – 2026-07-02 05:00 PDT batch."""
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

# ─────────────────────────────────────────────
# ARTICLE 1: EAGLE Act killed in NDAA
# ─────────────────────────────────────────────

article1_body = """The EAGLE Act has died again — quietly, procedurally, and almost without debate.

Representative Ro Khanna, the Silicon Valley Democrat who has made per-country green card caps his signature immigration cause, tried to attach the Equal Access to Green Cards for Legal Employment Act to this year's National Defense Authorization Act. The Republican majority on the House committee said no, and the bill was not advanced for a vote.

It is the latest in a decade-long pattern. The EAGLE Act passed the House in 2022, drew a White House statement of support, and accumulated more than 350 "yes" votes across multiple Congresses. It has never become law.

## What the bill would do

The legislation targets a structural bottleneck that has turned the green card queue into a generational ordeal. Under current law, no single country's nationals can receive more than 7 per cent of employment-based green cards in a given year. The EAGLE Act would eliminate that cap entirely and raise the family-sponsored limit to 15 per cent.

The practical effect falls almost entirely on two populations: Indians and Chinese nationals, who together account for the vast majority of the employment-based backlog. The queue now exceeds one million approved petitions. For Indians in the EB-2 category — the workhorse classification for software engineers, data scientists, and healthcare professionals — estimated wait times run between 50 and 100 years.

That is not a misprint. A 30-year-old Indian engineer who filed an EB-2 petition today could, under current projections, receive a green card sometime between 2076 and 2126. The July 2026 Visa Bulletin made things worse: EB-2 India went "Unavailable," meaning zero green cards will be issued in that category until the new fiscal year begins in October.

## Why Khanna picked the NDAA

The defence bill is one of the few pieces of legislation that Congress passes every year without fail. Attaching immigration provisions to it is a time-honoured tactic — it sidesteps the committee jurisdiction fights that have killed standalone immigration reform for decades. Khanna argued that eliminating per-country caps is a national security issue: the United States cannot maintain its edge in semiconductor fabrication, artificial intelligence, and defence technology if its best engineers are trapped in a visa limbo that incentivises them to leave.

The Republican committee disagreed, or at least declined to engage with the argument. No detailed objection was placed on the record. The amendment was simply blocked.

## The political arithmetic

Opponents of the EAGLE Act have historically raised two objections. The first is that eliminating country caps would effectively hand every available green card to Indian and Chinese nationals for several years, freezing out applicants from smaller countries. The bill's nine-year transition period was designed to address this, reserving a portion of visas for nationals of other countries during the phase-out. The Heritage Foundation, among others, has argued that the transition mechanism is insufficient and that the bill creates national security risks by fast-tracking Chinese applicants.

The second objection is simpler: green card reform should not be done piecemeal while the southern border remains a political flashpoint. In the current Congress, that argument has proven decisive. Every Republican immigration priority in 2026 has centred on enforcement, deportation, and fee increases. Reform of legal immigration pathways has no constituency on the committee.

## What it means for the queue

For the roughly 400,000 Indian nationals waiting for an employment-based green card, the NDAA rejection means the status quo continues. They will remain on H-1B visas — renewable in three-year increments, tied to a specific employer, and subject to processing delays, fee increases, and the ever-present risk that a layoff triggers a 60-day countdown to leave the country.

Their children face a separate crisis. Under current law, dependents who "age out" — turning 21 before their parents' green card comes through — lose their place in line entirely and must find their own immigration pathway or leave. Given EB-2 India wait times, virtually every child of an Indian green card applicant will age out.

Khanna has signalled he will try again. The EAGLE Act has been introduced in some form in every Congress since 2011. It has never lacked bipartisan co-sponsors. What it has lacked, consistently, is a moment when immigration reform of any kind can command floor time.

That moment does not appear to be approaching."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The EAGLE Act Failed Again. The Green Card Queue Did Not Notice",
    "subheadline": "Ro Khanna tried to attach per-country cap reform to the defence bill. The Republican committee blocked it without debate, extending a decade of legislative near-misses for a million Indian applicants.",
    "slug": make_slug("eagle-act-ndaa-green-card-per-country-cap-khanna"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Over 400,000 Indian nationals in the EB-2 and EB-3 green card backlog are directly affected — the EAGLE Act was their best legislative hope to escape wait times that now stretch past a human lifetime.",
    "tags": ["eagle-act", "green-card", "per-country-cap", "ro-khanna", "ndaa", "eb-2", "backlog"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian EYE", "url": "https://theindianeye.com"},
        {"name": "Congress.gov — EAGLE Act (H.R.3648)", "url": "https://www.congress.gov/bill/117th-congress/house-bill/3648/all-info"},
        {"name": "White House Statement of Administration Policy on EAGLE Act", "url": "https://www.presidency.ucsb.edu/documents/statement-administration-policy-hr-3648-equal-access-green-cards-legal-employment-eagle-act"},
        {"name": "The Heritage Foundation", "url": "https://www.heritage.org"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/16/Ro_Khanna%2C_official_portrait%2C_115th_Congress_%283x4%29.jpg",
    "image_caption": "Representative Ro Khanna (D-CA), the EAGLE Act's lead sponsor in the House",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}

# ─────────────────────────────────────────────
# ARTICLE 2: 1,076 Indians deported in 2026
# ─────────────────────────────────────────────

article2_body = """The number sounds modest set against America's deportation machinery: 1,076 Indian nationals removed from the United States so far in 2026. But for a community that has built its American story around legal pathways — H-1B petitions, university admissions, employer sponsorship — the figure carries an uncomfortable weight.

India's Ministry of External Affairs disclosed the number during a weekly press briefing. Spokesman Randhir Jaiswal was matter-of-fact: "I can share that 1,076 Indian nationals have been deported from the US so far this year. Last year, that number was 3,567."

The year-on-year comparison suggests a slower pace than 2025, when Trump's immigration enforcement apparatus was still ramping up. But 2026 is only half over. At the current rate, the full-year total would approach 2,200 — lower than last year but well above the pre-2025 baseline.

## Who is being deported

The deportees are not, for the most part, H-1B engineers caught in a bureaucratic slip. The MEA's language points to three categories: individuals with criminal records, those with undocumented status, and visa violators.

One case illustrates the enforcement profile. On 21 May, ICE Los Angeles apprehended Parminderpal Singh, a 26-year-old Indian national whose record included vehicle theft, grand theft, trespassing, and vandalism. Singh remains in custody pending removal. His case — young, criminal history, no legal immigration status — fits the template that ICE has been publicising across its social media accounts as proof that enforcement is targeted and justified.

But the deportation numbers also capture a greyer population: people who overstayed tourist visas, students who fell out of F-1 status, workers whose employers did not renew their petitions in time. For Indians, the line between "legal" and "illegal" can blur faster than most realise. An H-1B holder who is laid off has 60 days to find a new sponsor or leave. A student whose OPT expires without an H-1B selection has no grace period at all. The Trump administration's revived Notice to Appear posture means USCIS can now initiate removal proceedings the moment a benefit application is denied — even if the underlying employment-based case is meritorious.

## The diplomatic dance

New Delhi's response has been calibrated with visible care. India is not protesting the deportations. It is not demanding their halt. Instead, the MEA has framed the issue as a cooperative exercise in managed migration.

"We are in continuous dialogue with the US regarding migration and mobility to ensure that legal migration is facilitated while illegal migration is effectively curbed," Jaiswal said.

The phrasing is deliberate. India wants to preserve the H-1B pipeline, the student visa corridor, and the broader professional migration framework that sends roughly 280,000 skilled workers to the United States each year. Pushing back on deportations of individuals with criminal records or no legal status would risk the entire relationship. So India verifies nationality claims, accepts repatriation, and asks Washington for more visa slots in return.

The bilateral framework follows a predictable protocol. When US authorities identify an Indian national for removal, they refer the case to the Indian consulate. India conducts a background check, confirms nationality, and issues a travel document. The individual is then flown back, often on commercial flights.

## What NRIs should know

For the roughly four million Indian-born residents of the United States who hold valid immigration status, the deportation numbers are not a direct threat. But they are a signal.

First, enforcement discretion has narrowed. Under the current administration, USCIS officers have been instructed to issue Notices to Appear more liberally. A denied extension, a lapsed status, an employer who fails to file on time — any of these can now trigger removal proceedings rather than a simple denial letter.

Second, the community's demographics are shifting. The surge in irregular border crossings by Indian nationals — concentrated along the US-Mexico and US-Canada borders — has given anti-immigration lawmakers a new talking point. The narrative that Indians come only through "legal channels" is increasingly contested, and that contestation has consequences for the broader visa policy environment.

Third, India's cooperative posture on deportations is a strategic choice, not a permanent condition. New Delhi is trading compliance for leverage on legal migration. If that leverage fails to produce results — more visa slots, faster processing, lower fees — the political calculus in India could shift. The MEA is already facing domestic criticism for appearing too accommodating.

The 1,076 number will grow by October. The question for the diaspora is not whether it will, but what the number buys — and for whom."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "India Has Taken Back 1,076 Deportees This Year. It Is Not Complaining",
    "subheadline": "The MEA disclosed the deportation count without protest, trading compliance for leverage on legal migration. For NRIs, the numbers carry a quieter warning about how quickly status can slip.",
    "slug": make_slug("india-deportation-1076-mea-ice-enforcement-nri"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian Americans with valid status are not directly at risk, but narrower enforcement discretion, the 60-day H-1B grace period, and USCIS's revived NTA posture mean any lapse in status can now trigger removal proceedings.",
    "tags": ["deportation", "ice", "mea", "enforcement", "india-us", "h1b", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "LiveMint", "url": "https://www.livemint.com/news/world/how-trumps-immigration-crackdown-is-affecting-indians-1-076-deportations-in-2026-11780713075195.html"},
        {"name": "Ministry of External Affairs (India)", "url": "https://www.mea.gov.in"},
        {"name": "ICE Los Angeles (X/@ICElosangeles)", "url": "https://x.com/ICElosangeles"}
    ]),
    "score_total": 76,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A stamped passport — the paper trail that determines who stays and who goes",
    "image_attribution": "Pexels",
    "body": article2_body
}

# ─────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
