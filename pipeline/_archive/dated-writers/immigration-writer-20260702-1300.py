#!/usr/bin/env python3
"""Immigration news writer — July 2, 2026 run"""
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
        "headline": "Adjustment of Status Is Now 'Extraordinary.' Your Green Card Path Just Changed",
        "subheadline": "USCIS declared that adjusting immigration status inside the US is no longer routine — it is discretionary relief reserved for exceptional cases. For hundreds of thousands of Indians in the green card queue, the memo rewrites the rules mid-game.",
        "slug": make_slug("uscis-adjustment-of-status-extraordinary-green-card-india-h1b"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders with pending I-485 applications face heightened scrutiny and potential denial even if they meet every technical requirement, while those forced into consular processing must navigate 75-to-125-day appointment backlogs at Indian consulates.",
        "tags": ["adjustment-of-status", "green-card", "h1b", "uscis", "consular-processing", "i-485"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS", "url": "https://www.uscis.gov/newsroom/news-releases/us-citizenship-and-immigration-services-will-grant-adjustment-of-status-only-in-extraordinary"},
            {"name": "Nolo", "url": "https://www.nolo.com/legal-updates/immigration-law-updates-in-2026.html"},
            {"name": "Lexology", "url": "https://www.lexology.com/library/detail.aspx?g=uscis-adjustment-of-status-extraordinary-circumstances"},
            {"name": "VisaVerge", "url": "https://visaverge.com/immigration-news/adjustment-of-status-now-limited-to-extraordinary-cases/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/24/us-asks-foreign-nationals-to-apply-for-green-cards-from-home-country/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8061944/pexels-photo-8061944.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "US passports and immigration documents on a desk",
        "image_attribution": "Pexels",
        "body": """On May 22, USCIS issued Policy Memorandum PM-602-0199 — a dense, bureaucratic document that amounts to one of the most consequential shifts in US immigration processing in years. The agency declared that adjustment of status, the procedure that lets foreign nationals already living in the US apply for a green card without leaving the country, is now "an extraordinary form of relief" to be granted only in limited cases.

For decades, AOS has been the default. If you held an H-1B, had an approved I-140 petition, and your priority date was current, you filed Form I-485, attended a USCIS interview, and — eventually — received your green card. All without leaving American soil. The alternative, consular processing, meant flying to a US embassy abroad, scheduling an interview, and completing the process from your home country.

USCIS now says that consular processing was always supposed to be the standard path. AOS, it argues, was "never designed to supersede" it.

## What the Memo Actually Says

The policy memo stops short of abolishing AOS. Instead, it instructs officers to treat it as a discretionary exercise — one that applicants must affirmatively earn. Under the new framework, meeting every technical requirement of INA Section 245(a) is necessary but no longer sufficient. Applicants must now demonstrate why "administrative discretion should be favorably exercised" in their case.

Officers are told to weigh positive and negative factors including family ties, immigration status history, and moral character. The very decision to seek AOS rather than consular processing will itself be treated as a negative factor — the applicant's "attempt to avoid the ordinary consular immigrant visa process."

There is no effective date. Practitioners assume the policy applies immediately, including to the estimated 1.8 million I-485 applications already pending with USCIS.

## The H-1B Carve-Out — Sort Of

The critical nuance for Indian tech workers: USCIS acknowledges in the memo that dual-intent visa categories — H-1B and L-1 — "already allow foreign nationals to work in the United States while simultaneously pursuing permanent residency." Legal analysts at Lexology and Cozen O'Connor interpret this as a signal that H-1B holders can still file AOS without it being viewed as an inherently negative factor.

But "can still file" and "will be approved" are not the same thing. The memo directs officers to evaluate each case individually. More Requests for Evidence are expected. More Notices of Intent to Deny are likely. And when denials come, the memo requires officers to issue written decisions explaining why negative factors outweighed positive ones.

The Trump administration has reportedly signalled that applicants providing "economic benefit" to the United States would likely continue to receive AOS approval. Cold comfort for the thousands of Indians in non-STEM roles or at smaller companies that cannot demonstrate outsized economic impact.

## Non-Dual-Intent Applicants Are Hit Hardest

For Indians who entered on F-1 student visas, transitioned to OPT, and are now pursuing employment-based green cards, the memo is more directly threatening. F-1 is not a dual-intent visa — it presumes the student intends to leave. Seeking a green card through AOS could now be treated as evidence of misrepresented intent.

The same applies to those on B-1/B-2 visitor visas who married US citizens and sought to adjust status. USCIS frames such cases as exactly the kind of "loophole" the memo targets.

## The Consular Processing Reality

If AOS becomes less reliable, the fallback is consular processing — which means travelling to India for a visa interview. Current wait times at US consulates in India range from 75 days in some cities to over 400 days in others. Hyderabad and New Delhi have reported the longest delays, with employment-based visa appointments stretching beyond four months.

For an H-1B worker with a family, consular processing means weeks or months away from work, uncertain timelines, and the risk that administrative processing could extend the trip indefinitely. It also introduces a specific danger for anyone who has accumulated more than 180 days of unlawful presence in the US: departing the country triggers a three-year or ten-year bar on re-entry.

## What to Do Now

Immigration attorneys are advising clients to treat pending I-485 applications as if they require extra documentation. Letters from employers, evidence of community ties, volunteer work, tax records — anything that demonstrates positive equities should be assembled and ready.

For those who have not yet filed, the calculation has shifted. Filing AOS is still possible, but applicants should prepare a parallel consular processing strategy. The memo does not prohibit AOS; it makes the outcome less predictable.

The legal community expects lawsuits. Multiple advocacy groups have signalled they will challenge the memo as an arbitrary departure from decades of established practice. But litigation takes time. For the roughly 400,000 Indians with pending employment-based green card applications, the uncertainty is immediate."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "No Oath, No Ceremony. USCIS Scrapped Fourth of July Naturalisations for America's 250th",
        "subheadline": "In a year when the US celebrates 250 years of independence, the agency that makes new citizens has quietly cancelled its signature holiday tradition. For Indians who waited decades for this moment, the symbolism is hard to miss.",
        "slug": make_slug("uscis-cancels-fourth-july-naturalization-250th-indian-citizens"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are among the largest groups naturalising each year, often after 15-to-20-year waits in the employment-based green card backlog, and the cancellation of the tradition that celebrates their journey to citizenship lands as a pointed slight.",
        "tags": ["naturalization", "citizenship", "fourth-of-july", "uscis", "250th-anniversary"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Arizona Republic / azcentral", "url": "https://www.azcentral.com/story/news/local/phoenix/2026/07/02/no-citizenship-ceremonies-in-phoenix-this-fourth-of-july/"},
            {"name": "Nolo", "url": "https://www.nolo.com/legal-updates/immigration-law-updates-in-2026.html"},
            {"name": "USCIS", "url": "https://www.uscis.gov/newsroom/news-releases/uscis-proposes-raising-n-400-application-fees"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/2025_Naturalization_Ceremony-_Oath_of_Citizenship_%2854813641790%29.jpg/1280px-2025_Naturalization_Ceremony-_Oath_of_Citizenship_%2854813641790%29.jpg",
        "image_caption": "New US citizens take the oath of citizenship at a 2025 naturalization ceremony",
        "image_attribution": "Wikimedia Commons",
        "body": """Every Fourth of July for as long as anyone in the immigration bar can remember, US Citizenship and Immigration Services has held naturalization ceremonies. Immigrants — many of whom waited years or decades for the privilege — raised their right hands, recited the oath of allegiance, and became American citizens on the very day that celebrates the country's founding. In 2025, USCIS promoted large ceremonies across the country: 100 immigrants from 30 nations took the oath in Phoenix, another 100 from 41 countries in Mesa. It was the agency's tradition, and it ran like clockwork.

In 2026 — the 250th anniversary of the Declaration of Independence — USCIS has cancelled the tradition entirely.

## The Silence Is the Statement

No press release was issued. No explanation was offered. When the Arizona Republic contacted USCIS on June 29, a spokesperson declined to confirm whether ceremonies would be held and suggested reporters contact the federal courts instead. The federal court naturalization schedule for Phoenix, Tucson, and Yuma shows nothing on July 3 or July 4.

It is a quiet cancellation of a loud tradition. And it arrives in a year when USCIS has raised, proposed to raise, or otherwise tightened the conditions around virtually every immigration filing an applicant might submit.

## The Fee Wall Around Citizenship

The ceremony cancellation does not exist in isolation. In June 2026, USCIS published a proposed rule that would increase the Form N-400 naturalization filing fee from $760 to $1,330 for paper applications and from $710 to $1,280 for online filings. The fee for appealing a naturalization denial would jump from $830 to $1,475.

More consequentially, the proposed rule would eliminate most fee waivers and reduced-fee options for low-income applicants. Public comments are due by August 24, and a final rule will follow.

For an Indian immigrant who has spent 15 to 20 years in the EB-2 or EB-3 green card backlog, who has already paid the $100,000 H-1B fee (or the $2,965 I-129 petition fee, or both), who has funded premium processing, biometrics, and EAD renewals for a spouse — the N-400 fee hike is the capstone of a financial gauntlet that can exceed $150,000 over a career.

## Indians and the Citizenship Pipeline

India consistently ranks among the top five countries of origin for new US citizens. According to the Department of Homeland Security's most recent yearbook, over 65,000 Indian-born individuals naturalised in fiscal year 2023 alone. The pipeline from H-1B to green card to citizenship is the defining immigration journey for the Indian American professional class — and it is now longer, costlier, and less certain at every stage.

The employment-based green card backlog for Indian nationals currently stretches decades. EB-2 India went "unavailable" in the July 2026 Visa Bulletin — meaning no green cards will be issued in that category until at least October. The EB-3 final action date sits at December 2013. A worker who filed their labor certification in 2013 is, in mid-2026, still waiting.

Once a green card is finally obtained, the applicant must hold it for five years before becoming eligible to naturalise (three years if married to a US citizen). The wait, in total, routinely exceeds two decades.

The Fourth of July ceremony was, for many, the emotional endpoint of that journey. Not a bureaucratic step, but a public affirmation that the system — however slow, however expensive, however frustrating — ultimately delivered on its promise.

## What It Signals

Immigration advocacy groups have not been subtle in their interpretation. Monica Sandschafer, Arizona state director for Mi Familia Vota, called the cancellation "sad, but also consistent with actions and attitudes and values of this administration."

The broader context supports that reading. In the same period, USCIS declared adjustment of status "extraordinary relief," the administration proposed tripling immigration court appeal fees, and the Supreme Court handed the executive branch three significant immigration victories in a single week. The institutional message, transmitted across multiple channels simultaneously, is that legal immigration is tolerated but will not be celebrated.

## The Ceremony's Absence Speaks

There is something specific about a naturalization ceremony on the Fourth of July. It is one of the few moments when American immigration policy produces unambiguous joy. The new citizen holds a small flag. Their family takes photographs. A federal judge or USCIS officer reads a speech about what it means to join the republic. It is brief, formulaic, and — for the person who endured a decade-plus journey to reach it — profound.

In a year when that journey has been made harder at every turn, the decision not to hold the ceremony is not merely administrative. It is editorial.

The 250th anniversary of American independence will be marked by fireworks and parades and speeches about the country's founding ideals. In Phoenix, Mesa, Tucson, and Yuma — and, by the absence of any USCIS announcement, likely across the country — it will not be marked by the making of new citizens.

For the tens of thousands of Indian Americans who have spent their careers navigating this system, the omission registers. Not as policy. As posture."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
