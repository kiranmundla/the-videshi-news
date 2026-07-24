#!/usr/bin/env python3
"""
Immigration writer — 2026-06-15 04:00 UTC
Topics:
1. DOJ denaturalization push — Neeraj Sharma / Magnavision H-1B fraud case
2. US Embassy warns overstaying Indians face deportation — Newark Airport incident
"""
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
# ARTICLE 1: DOJ denaturalization push
# ─────────────────────────────────────────────

article1_body = """Washington has a new weapon in its immigration enforcement arsenal, and it cuts deeper than deportation. The Department of Justice has filed denaturalization actions against seventeen individuals in federal courts across the country — and one of the names on the list belongs to an Indian-born IT staffing operator from New Jersey whose H-1B fraud scheme reads like a cautionary tale for an entire industry.

Neeraj Sharma, fifty, ran Magnavision LLC out of Piscataway, New Jersey. Between 2015 and 2017, he signed and submitted eleven fraudulent H-1B visa petitions to USCIS. Each petition claimed that the foreign workers Sharma was sponsoring had full-time positions waiting for them at a major global financial institution. The petitions included letters on the bank's official letterhead, complete with forged signatures of its executives. None of the positions existed.

In December 2017, Sharma became a naturalised American citizen. On his application, under penalty of perjury, he declared that he had never committed a crime for which he was not arrested, never given false information to the US government, and never lied to gain immigration benefits. Every one of those assertions was false. He was subsequently convicted of visa fraud.

The DOJ is now seeking to revoke his citizenship entirely.

## The broader campaign

Sharma is not an isolated case. The seventeen denaturalization targets include sex offenders, drug traffickers, fraudsters, and individuals convicted of crimes they concealed during their citizenship applications. But USCIS guidance issued in December 2025 reportedly directed field offices to supply the DOJ's Office of Immigration Litigation with one hundred to two hundred denaturalization case referrals per month in fiscal year 2026. Between 1990 and 2017, the government averaged just eleven such cases per year.

The scale of the new effort is, by any historical measure, unprecedented.

"American citizenship is a privilege, not a right," the Washington Examiner editorial board wrote in response to the filings. USCIS Director Ur Jaddou had previously signalled that the agency would pursue citizenship revocation "aggressively" for individuals who obtained it through fraud or concealment.

## What this means for Indian Americans

Indians account for more than seventy per cent of all approved H-1B petitions annually. The community is also among the largest groups of newly naturalised citizens each year. That dual exposure — heavy reliance on the H-1B pipeline and a growing population of naturalised citizens — makes the denaturalization campaign acutely relevant.

Immigration attorneys say the immediate risk is limited to individuals who committed actual fraud. But the chilling effect is real. The message from Washington is clear: the government will look backward, and citizenship is no longer the finish line it once was.

For the thousands of Indian professionals who navigated the H-1B system honestly, who waited years in the green card backlog, and who took the oath of citizenship believing it was permanent — the Sharma case is a reminder that the system's enforcement arm now reaches further than ever before.

The practical takeaway is straightforward. Maintain meticulous records of every immigration filing. Keep copies of every petition, every LCA, every I-797 approval notice. If your employer filed H-1B petitions on your behalf, ensure the representations in those petitions were accurate. And if you are preparing for naturalisation, treat the application with the seriousness it demands — because the government now treats discrepancies as grounds to undo everything.

x-official:https://x.com/USCIS/status/1932480693278482618

## The staffing industry question

The Magnavision case also raises uncomfortable questions about the IT staffing model that has long been a gateway for Indian workers entering the US labour market. Sharma's scheme — fabricating job offers at a prestigious client, submitting forged documentation — is a pattern that federal investigators have pursued aggressively in recent years. Several Indian-owned staffing firms have faced similar charges.

The DOJ's willingness to pursue denaturalization, not just criminal penalties, signals that the consequences of H-1B fraud now extend to the ultimate sanction: loss of citizenship itself. For an industry that has already been under scrutiny for wage suppression and bench-time violations, this adds another layer of existential risk."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Washington Can Now Take Back Your Citizenship — Just Ask Neeraj Sharma",
    "subheadline": "The DOJ has filed to strip citizenship from seventeen naturalised Americans, including an Indian IT staffing boss who forged H-1B petitions. The denaturalization campaign is running at two hundred cases a month.",
    "slug": make_slug("doj-denaturalization-neeraj-sharma-h1b-fraud-citizenship"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian Americans are the largest group of H-1B beneficiaries and newly naturalised citizens — making them disproportionately exposed to an enforcement campaign that now treats citizenship as revocable.",
    "tags": ["denaturalization", "h1b-fraud", "uscis", "doj", "citizenship", "indian-americans"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "USCIS", "url": "https://www.uscis.gov/newsroom/news-releases/justice-department-moves-to-strip-us-citizenship-from-17-naturalized-sex-offenders-fraudsters-drug"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/opinion/editorials/3451889/american-citizenship-privilege-not-right/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/10/h-1b-visa-fraud-by-indian-leads-to-revocation-of-us-citizenship/"},
        {"name": "US Department of Justice", "url": "https://www.justice.gov/usao-nj/pr/owner-information-technology-staffing-company-charged-visa-and-naturalization-fraud"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/USCIS_July_4th_Naturalization_Ceremony_%2819227250219%29.jpg/1280px-USCIS_July_4th_Naturalization_Ceremony_%2819227250219%29.jpg",
    "image_caption": "A USCIS naturalization ceremony on July 4th, where new citizens take the oath of allegiance",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}

# ─────────────────────────────────────────────
# ARTICLE 2: US Embassy warning + Newark Airport detention
# ─────────────────────────────────────────────

article2_body = """The US Embassy in New Delhi posted a single sentence on X last week that read less like diplomatic communication and more like a threat: "If you remain in the United States beyond your authorized period of stay, you could be deported and could face a permanent ban on traveling to the United States in the future."

The timing was not accidental. Days earlier, a viral video showed an Indian national from Haryana being physically restrained on the floor at Newark Liberty International Airport in New Jersey. The footage, which spread rapidly across Indian social media, prompted the Indian Consulate in New York, the Indian Embassy in Washington, and the Ministry of External Affairs in New Delhi to intervene simultaneously.

The man had entered the United States without a valid visa, according to the Indian Consulate. A court had already ordered his deportation. During transit at Newark, his behaviour was "deemed not conducive for travel," leading to his restraint and admission to a medical facility. He will be deported once declared fit to travel.

## The message behind the message

The Embassy's public warning and the Newark incident are two data points in a pattern that has become impossible to ignore. The Trump administration has systematically tightened enforcement against immigration violators of every category — from undocumented border crossers to visa overstayers to H-1B workers whose employers filed fraudulent petitions on their behalf.

For Indians specifically, the enforcement landscape has shifted dramatically. In April, DHS Secretary Kristi Noem reminded all foreign nationals present in the country for more than thirty days that the deadline to register under the Alien Registration Act had arrived. Failure to register is a criminal offence, punishable by fines, imprisonment, or both.

The registration requirement is not new — the law dates to 1940. What is new is that the current administration is actively enforcing it, and the Indian community, which includes an estimated seven hundred thousand undocumented immigrants according to various estimates, is squarely in the crosshairs.

## Newark: anatomy of a detention

The Newark Airport incident crystallised anxieties that have been building for months. The video showed two individuals holding a man on the ground — a scene that provoked outrage across Indian social media and prompted official diplomatic responses from three separate Indian government bodies within hours.

"We have come across social media posts claiming that an Indian national is facing difficulties at Newark Liberty International Airport. We are in touch with local authorities in this regard," the Indian Consulate General in New York posted on X. "The Consulate remains ever committed to the welfare of Indian Nationals."

India's Ministry of External Affairs subsequently confirmed that it had "formally raised the matter with the US Embassy in New Delhi." The Embassy in Washington and the Consulate in New York both engaged US authorities separately to ascertain the details.

The diplomatic scramble underscored how sensitive the issue has become for New Delhi, which must balance its strategic relationship with Washington against domestic political pressure to protect Indian nationals abroad.

## What overstaying actually means now

Under the current enforcement regime, the consequences of overstaying a US visa have become significantly more severe:

An overstay of more than 180 days triggers a three-year bar on re-entry. An overstay of more than a year triggers a ten-year bar. Repeated violations can result in a permanent ban. And under the Alien Registration Act enforcement push, even individuals who entered legally but failed to register face criminal liability.

For Indian students on F-1 visas whose OPT periods have expired, for H-1B workers in the sixty-day grace period between jobs, for dependents whose H-4 status hinges on a primary applicant's employment — the margin for error has shrunk to nearly nothing.

The practical advice from immigration attorneys is blunt: know your exact status expiration date, file extensions well before they are needed, and do not assume that a pending application protects you from removal. Under the current administration, it may not.

## The diplomatic tightrope

India's response to the Newark incident revealed the awkward position New Delhi occupies. Prime Minister Modi arrived at the G7 summit this week with an agenda that includes expanded H-1B access and visa facilitation for Indian professionals. Simultaneously, Indian nationals are being detained, restrained, and deported at US airports under circumstances that generate viral outrage at home.

The bilateral relationship is too valuable for either side to let immigration enforcement become a genuine diplomatic irritant. But the incidents are accumulating, and each one erodes the narrative — carefully cultivated by both governments — that the US welcomes Indian talent with open arms.

The Embassy's warning on X was, in its way, a kindness: a public signal that the rules have changed, and that Indians who test them will find no diplomatic safety net waiting."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Stay Too Long, Never Come Back — The US Embassy's Warning to Indians Is Not a Bluff",
    "subheadline": "A viral video of an Indian national restrained at Newark Airport, a blunt warning from the US Embassy in New Delhi, and a registration law from 1940 that Washington is suddenly enforcing. The message to overstaying Indians has never been clearer.",
    "slug": make_slug("us-embassy-warning-overstay-indians-newark-deportation"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "With an estimated seven hundred thousand undocumented Indians in the US and hundreds of thousands more on temporary visas, the crackdown on overstayers directly affects the community — from students to H-1B workers to undocumented residents.",
    "tags": ["overstay", "deportation", "us-embassy", "newark-airport", "alien-registration", "indian-nationals"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/12/detained-at-newark-airport-indian-national-to-be-deported-once-declared-fit-to-travel/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/12/us-warns-about-overstaying-indians-may-face-deportation-or-travel-ban/"},
        {"name": "US Embassy India (via X)", "url": "https://x.com/USAndIndia"},
        {"name": "CNN", "url": "https://www.cnn.com/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An open passport showing multiple visa stamps at an immigration checkpoint",
    "image_attribution": "Pexels",
    "body": article2_body
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
