#!/usr/bin/env python3
"""Immigration writer — July 5, 2026 01:00 AM run"""
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
# ARTICLE 1: July Visa Bulletin — EB-2 India Unavailable
# ─────────────────────────────────────────────

article1_body = """The July 2026 Visa Bulletin from the State Department dropped like a controlled demolition on Indian employment-based immigration. The most consequential line: EB-2 India is now marked "Unavailable" — meaning zero green cards will be issued in that category until the new fiscal year begins on 1 October.

That single letter, "U," affects hundreds of thousands of Indian professionals — software engineers, researchers, physicians, data scientists — who filed their I-140 petitions years ago and have been inching through a queue that already stretched beyond a decade. Their wait just got three months longer, at minimum.

## The Numbers

The July bulletin brought damage across the board for Indian nationals:

- **EB-2 India**: Unavailable. The final action date, which stood at 1 September 2013 in June, is now gone entirely. India's pro-rated EB-2 limit for FY 2026 has been exhausted.
- **EB-1 India**: Retrogressed two months, from 15 December 2022 to 15 October 2022. The State Department warned that EB-1 India could face further retrogression — or itself go unavailable — before September.
- **EB-3 India**: A half-month advance to 1 January 2014. Better than nothing, but the queue still stretches back more than twelve years.
- **EB-5 Unreserved India**: Also declared unavailable. India's pro-rated EB-5 limit is exhausted for the year.

Meanwhile, the rest of the world moved forward. EB-1 remains current for most countries. EB-2 is current for everyone except India and China. EB-3 advanced two full months for most applicants. China's EB-1 advanced two months and its EB-3 leapt forward by nearly five months. The disparity is not subtle.

## Why This Keeps Happening

The mechanism is the per-country cap — a provision of immigration law that limits any single country to roughly 7 per cent of employment-based immigrant visas, regardless of demand. India, which produces nearly three-quarters of all H-1B workers and a correspondingly outsized share of employment-based green card applications, slams into this ceiling every year.

The result is a structural mismatch. An Indian-born engineer and a Canadian-born engineer with identical qualifications, identical jobs, and identical filing dates face wildly different timelines. The Canadian's green card is processed in months. The Indian's takes a decade or more. The EAGLE Act, which would have eliminated per-country caps, failed again in Congress just days ago.

## The EB-2-to-EB-3 Downgrade Question

With EB-2 India shut down but EB-3 India still current to 1 January 2014, immigration attorneys report a surge in inquiries about "downgrading" — refiling under EB-3 to access its (barely) moving queue. The calculus is straightforward if grim: EB-3 India's final action date, stuck in 2014, is still a more reachable target than a category that simply does not exist until October.

The strategy carries trade-offs. EB-3 covers a broader pool of applicants and its own queue is glacial. But for someone whose EB-2 priority date falls before January 2014, a downgrade could mean the difference between filing an I-485 now and waiting until October — or later — for EB-2 to reopen.

## What Happens in October

The State Department has signalled that when FY 2027 numbers become available on 1 October, EB-2 India's final action date should advance to at least where it stood in May 2026. Analysts at VisaNation and Capitol Immigration Law Group expect a meaningful one-time jump, followed by the familiar pattern of slow creep and renewed retrogression as the new year's demand materialises.

EB-1 India is expected to correct as well, though the bulletin's explicit warning about further retrogression before September suggests the category remains fragile through the summer.

## What This Means for Indian Americans

For the roughly one million Indian nationals in the employment-based green card queue, the July bulletin is a reminder of how little has changed despite years of advocacy. The per-country cap remains. The EAGLE Act has failed repeatedly. The backlog grows faster than USCIS can process it.

The practical advice from immigration attorneys is consistent: prepare documentation now so you can file the moment numbers return in October. If you hold both an EB-2 and EB-3 approved petition with a priority date before January 2014, talk to your lawyer about interfiling. And if you are considering an EB-1A or NIW petition as an alternative path, the window for EB-1 India is narrowing — act before it closes too."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The State Department Shut EB-2 India for the Year. One Million People Just Hit a Wall",
    "subheadline": "The July 2026 Visa Bulletin declared EB-2 India unavailable, retrogressed EB-1 India by two months, and shut India's unreserved EB-5 category — leaving Indian green card applicants with no path forward until October.",
    "slug": make_slug("eb2-india-unavailable-july-visa-bulletin-green-card-wall"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Hundreds of thousands of Indian professionals in the US on H-1B visas face an extended wait for green cards as the EB-2 category — the most common path for skilled workers — is completely shut down until October 2026.",
    "tags": ["green-card", "eb-2", "eb-1", "visa-bulletin", "per-country-cap", "uscis", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Capitol Immigration Law Group", "url": "https://cilawgroup.com/news/2026/06/18/july-2026-visa-bulletin-uscis-continues-to-use-final-action-dates-for-eb-filings-causing-further-retrogression-for-india/"},
        {"name": "VisaNation Law Group (Immi-USA)", "url": "https://www.immi-usa.com/visa-bulletin/"},
        {"name": "South Asian Herald", "url": "https://southasianherald.com/us-visa-wall-gets-higher/"},
        {"name": "BAL Immigration News", "url": "https://www.bal.com/"},
        {"name": "U.S. Department of State Visa Bulletin", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
    "image_caption": "A USCIS Application Support Center in New York, where green card applicants attend biometrics appointments",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}

# ─────────────────────────────────────────────
# ARTICLE 2: $100K H-1B Fee — Circuit Split
# ─────────────────────────────────────────────

article2_body = """A federal judge in Boston struck down the Trump administration's $100,000 H-1B visa fee on 8 June, calling it an unlawful tax that Congress never authorised. The White House immediately appealed. A federal court in Washington, D.C. had previously declined to block the same fee. A third lawsuit is pending in San Francisco.

Three courts. Three potential outcomes. The makings of a circuit split that could send the most contentious immigration fee in American history to the Supreme Court.

## What Judge Sorokin Actually Said

U.S. District Judge Leo Sorokin, in *California v. Mullin*, did not merely find the fee excessive. He ruled it was not a fee at all — it was a tax, and only Congress has the power to levy taxes. The Trump administration had argued the $100,000 payment was a lawful penalty under the president's authority to restrict entry of foreign nationals he deems "detrimental to the interests of the United States."

Sorokin rejected this reasoning, citing the Supreme Court's February 2026 ruling that struck down Trump's sweeping tariffs. If the president lacked authority to levy a tax through tariff powers, he similarly lacked authority to levy one through immigration law, the judge wrote.

"Here, the substance and application of the $100,000 payment reveal that it is a tax, regardless of what the payment is called," Sorokin wrote in his ruling, which applies nationwide.

## The Healthcare Fallout

The ruling drew immediate celebration from the medical community. The American Association of Physicians of Indian Origin called it "a healthcare victory, not a political victory." AAPI President Dr. Amit Chakrabarty said the fee would have forced rural hospitals to withdraw job offers to international medical graduates who already fill one in four physician positions in the United States.

The American Medical Association echoed the sentiment. "At a time when communities across the country face physician shortages and growing barriers to care, we should be removing obstacles — not creating new ones," said AMA President Dr. Bobby Mukkamala.

The numbers back them up. International medical graduates make up approximately 25 per cent of the U.S. physician workforce. They are disproportionately concentrated in rural areas, safety-net hospitals, and underserved communities where American-trained doctors are reluctant to practise. A $100,000 fee per H-1B petition would have made hiring them economically unviable for many of these institutions.

## But the Fee Is Not Dead

Here is where it gets complicated. Judge Sorokin's ruling vacated the fee nationally. But the U.S. Chamber of Commerce's separate lawsuit in Washington, D.C. failed to block it — a federal judge there denied summary judgment against the fee, leaving it in effect through that circuit at least until September 2026, when the presidential proclamation is scheduled to expire.

The administration has appealed Sorokin's ruling. White House spokeswoman Taylor Rogers said the administration is "confident" the order will be reversed. "President Trump has clear legal authority to restrict entry of any class of aliens he determines is not in America's best interests," she said.

The third case, filed in San Francisco by religious groups and labour organisations, remains pending. If the Ninth Circuit reaches a different conclusion from the First Circuit (Boston) and the D.C. Circuit, a Supreme Court review becomes virtually inevitable.

## What This Means for Indian Workers

Indians hold roughly 73 per cent of all H-1B visas. Any fee imposed on the programme falls disproportionately on Indian professionals and the companies that employ them. Before the $100,000 fee was announced last September, a standard H-1B petition cost roughly $3,380 — a figure that already includes filing fees, the ACWIA training fee, the fraud prevention fee, and the asylum programme fee.

The thirty-fold increase threw the system into chaos. Employers froze petitions. Universities paused recruitment. IT services firms — Indian companies such as Infosys and TCS among them — scrambled to calculate whether sponsoring workers remained financially viable.

For now, Judge Sorokin's ruling provides relief. But with an active appeal and contradicting decisions across circuits, the uncertainty is far from resolved. Immigration attorneys are advising clients to file petitions at the standard fee while the ruling holds, but to budget for the possibility that the $100,000 fee could be reinstated on appeal.

The only certainty is that certainty is months away — and that the Supreme Court may ultimately have the final word."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Three Courts. Three Answers. The $100,000 H-1B Fee Is Heading for the Supreme Court",
    "subheadline": "A Boston judge struck it down as an unlawful tax. A D.C. court left it standing. A San Francisco case is pending. The circuit split over the most expensive visa fee in American history is now a matter for the justices.",
    "slug": make_slug("100000-h1b-fee-circuit-split-supreme-court-indian-doctors"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians hold 73 per cent of H-1B visas and would bear the brunt of a $100,000 fee that would make employer sponsorship economically unviable — particularly for the Indian physicians who fill one in four doctor positions across rural and underserved America.",
    "tags": ["h1b", "100000-fee", "court-ruling", "circuit-split", "uscis", "immigration", "indian-doctors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "AP News", "url": "https://apnews.com/article/h1b-visa-fee-trump-judge-struck-down"},
        {"name": "Healio", "url": "https://www.healio.com/news/primary-care/20260609-judge-overturns-h1b-visa-fee-barrier-to-foreignborn-physicians"},
        {"name": "Becker's Hospital Review", "url": "https://www.beckershospitalreview.com/workforce/judge-strikes-down-100k-h-1b-visa-fee.html"},
        {"name": "The Indian Eye (AAPI Statement)", "url": "https://theindianeye.com/"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
    "image_caption": "A hand holds an open passport displaying visa stamps, reflecting the bureaucratic journey H-1B workers navigate",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
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
