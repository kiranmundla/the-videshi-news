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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "EB-5 Was the Indian Escape Hatch From the Green Card Backlog. It Just Slammed Shut Until October",
        "subheadline": "Washington has issued every EB-5 unreserved visa available to Indian applicants for the fiscal year. The investor route that thousands of backlogged professionals had pivoted to is now closed until the FY2027 reset.",
        "slug": make_slug("eb5-india-unreserved-exhausted-october-2026-investor-visa-backlog"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For Indian families who poured $800,000 or more into US projects to skip the decade-long EB-2/EB-3 wait, the one pathway sold as 'faster' has now hit the same per-country wall — and the set-aside categories they are rushing into may be next.",
        "tags": ["eb5", "green-card", "visa-bulletin", "investor-visa", "backlog"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "India-West", "url": "https://www.indiawest.com/news/eb-5-visa-limit-reached-for-indians-until-october/"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/indian-eb-5-visa-retrogression-warning-may-2026-update/"},
            {"name": "US Department of State — Visa Bulletin", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32269240/pexels-photo-32269240.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A US passport resting on hundred-dollar bills and credit cards, symbolising the EB-5 investor visa route",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The State Department has confirmed what immigration lawyers had been bracing for since spring: every EB-5 unreserved immigrant-investor visa available to Indian nationals for fiscal year 2026 has been issued. No more can be granted to Indian applicants until the new fiscal year begins on October 1, when the 2027 numbers reset.

For a community that has spent the better part of a decade watching the employment-based green card backlog calcify, the timing stings. EB-5 was supposed to be the way around the wait.

## The Route Everyone Pivoted To

The math behind the EB-5 surge is not complicated. Indian nationals on H-1B and L-1 visas routinely wait years — often well over a decade — for an EB-2 or EB-3 priority date to become current, a function of the per-country caps that limit any single nationality to roughly 7% of employment-based green cards each year. EB-5, the investor category that requires putting $800,000 into a targeted employment area or $1,050,000 elsewhere and creating ten US jobs, offered something the salaried tracks could not: a path that did not depend on an employer and, until recently, did not carry a crushing India-specific wait.

Indians noticed. Petitions from India rose from about 1,200 in FY2023 to more than 3,000 in FY2025, according to government data. Indians now account for roughly 22% of all EB-5 petitions filed worldwide since April 2022 — second only to China. A category that drew barely 4% of its filings from India five years ago has become, in effect, an Indian program.

That demand is exactly what exhausted the supply.

## What "Unavailable" Actually Means

The unreserved EB-5 category — the standard pool, as opposed to the set-asides created by the 2022 reform law — had its annual India allocation fully consumed by early June. The State Department's notice means consulates and USCIS cannot issue additional unreserved EB-5 visas to Indian applicants for the rest of FY2026. The July visa bulletin made the closure official, listing the category as unavailable for India alongside EB-2, which was exhausted back in May.

Crucially, this does not erase anyone's place in line. Petitions already filed keep their priority dates, and new petitions can still be lodged. What stops is final visa issuance — the last step that actually converts an approved case into a green card or an immigrant visa. Anyone hoping to complete that step before autumn is now waiting.

## The Set-Asides Are the New Crowd

The 2022 EB-5 Reform and Integrity Act carved out reserved visas for rural projects, high-unemployment areas, and infrastructure — and as of the June bulletin, all three remain current for India. That has set off a predictable stampede: lawyers and investors are steering new money toward the set-aside categories while the window stays open.

Charlie Oppenheim, the former chief of the State Department's Visa Office, has warned that this is how backlogs are born. "If demand from Indian nationals continues at this pace, we could see EB-5 backlogs form within reserved categories — just like they did in EB-2," he said. The set-asides are smaller pools by design; it does not take many Indian filers to fill them.

## A Deadline Stacked on a Closure

Layered on top is a statutory cliff that has nothing to do with the annual cap. Under the 2022 law, Regional Center EB-5 petitions filed on or before September 30, 2026 are grandfathered — USCIS must keep adjudicating them even if the Regional Center Program later lapses. Petitions filed after that date lose that protection. For Indian-born applicants weighing whether to file at all, that has turned the next three months into a compressed decision window: rush to lock in a priority date and grandfathering before the deadline, even as final issuance in the unreserved category is frozen until October.

## What It Means for Indian Families

The blunt takeaway for the diaspora is that EB-5 has stopped being the clean shortcut it was marketed as. The investment thresholds — $800,000 at minimum — were always steep, but families accepted them in exchange for speed. With the unreserved category now subject to the same per-country squeeze as EB-2, the premium buys less than it did even a year ago.

For those still considering it, the practical advice from practitioners is unchanged but more urgent: target a set-aside category while it is current, map the source of funds before moving any money to stay clear of FEMA and Liberalised Remittance Scheme pitfalls, and do not assume "investor visa" means "fast." For everyone else watching from the H-1B queue, the closure is one more reminder that in the US immigration system, the line forms behind India no matter which door you try."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A New USCIS Rule Means a Wrong Signature Can Sink Your Green Card — Even After It's Accepted",
        "subheadline": "From July 10, USCIS can reject or deny a filing for an invalid signature at any point, and copy-pasted or software-generated signatures may not count. Indians, who file the bulk of these petitions, have the most to lose.",
        "slug": make_slug("uscis-signature-rule-july-10-2026-invalid-signature-denial-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals file more H-1B, I-140 and adjustment petitions than any other group, often through staffing firms and consultants whose batch-signing habits are precisely what the new rule targets — meaning a clerical shortcut by an employer could now cost a worker their case and their priority date.",
        "tags": ["uscis", "h1b", "green-card", "i-140", "policy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reddy Neumann Brown PC", "url": "https://www.rnlawgroup.com/new-uscis-signature-rule-takes-effect-july-10-2026/"},
            {"name": "Holland & Hart LLP", "url": "https://www.hollandhart.com/new-uscis-signature-rule-could-put-immigration-filings-at-risk"},
            {"name": "Federal Register — DHS/USCIS Interim Final Rule", "url": "https://www.federalregister.gov/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/48148/document-agreement-documents-sign-48148.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A hand signing a legal document with a pen",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """It sounds like the kind of bureaucratic footnote you skim past. It is not. Starting July 10, 2026, US Citizenship and Immigration Services can reject or deny an immigration filing because of how it was signed — and it can do so even after the agency has already accepted the case and cashed the filing fee.

The Interim Final Rule, published in the Federal Register on May 11, formally authorizes USCIS to treat an invalid signature as grounds for denial at any stage of adjudication. For a population that files more employment-based petitions than any other, the diaspora needs to read the fine print.

## What the Rule Actually Does

Until now, a signature problem was usually a fixable hiccup. USCIS might issue a request for evidence or a notice of intent to deny, giving the applicant a chance to correct it. The new rule hardens that into a trapdoor. If the agency later determines a filing lacked a valid signature — including after acceptance — it can reject or deny the request outright.

The categories of signature the rule puts at risk are exactly the ones modern offices rely on. Copy-pasted signatures, rubber-stamped signatures, and software-generated signatures — the kind produced by DocuSign and similar tools — may all be considered invalid. The rule requires, in effect, that the right person actually sign, and that the signature be genuine rather than reproduced.

Because this was issued as an interim final rule rather than a proposed one, it becomes enforceable on July 10 regardless of the comments submitted during the public comment period, which closes the same day.

## Why USCIS Says It Is Doing This

The agency points to a sharp climb in bad signatures. Denials for signature reasons rose from 300 in FY2021 to 2,953 in FY2025, according to data published in the rule itself, and the Administrative Appeals Office has already worked through 758 appeals tied to copied signatures.

The rule cites two cases that read like cautionary tales. In one, an authorized signatory signed a blank sheet of paper and told a subordinate to copy that signature onto at least 20 Form I-129 petitions — the form used for H-1B and other work visas. In another, a consulting firm filed roughly 3,000 Form I-140 immigrant petitions with the signature pasted onto each one.

Read those two examples again and the diaspora exposure becomes obvious.

## The Indian Connection

Form I-129 and Form I-140 are the backbone of the Indian employment-immigration journey. The H-1B petition is an I-129; the employer's green card sponsorship runs through the I-140. Indian nationals receive the overwhelming majority of H-1B approvals each year and dominate the employment-based green card queues. A very large share of those petitions are filed not by individuals but by employers, staffing companies, and consultancies that process filings in volume.

Batch processing is where the danger lives. The behavior the rule was written to stamp out — one signature reproduced across dozens or thousands of forms — is precisely the kind of efficiency a high-volume filer might adopt without a second thought. The worker whose name is on the petition may never know how their employer's HR department or outside counsel actually executed the signature. Under the new rule, that worker bears the consequence: a denied I-140 does not just lose a filing fee, it can mean losing a hard-won priority date that took years to earn.

## What to Do Before July 10

Immigration practitioners are urging filers to treat the change as a process audit, not a paperwork detail.

- **Insist on wet or properly executed signatures.** For petitions filed on or after July 10, confirm that the actual authorized person signed, and that the method used would survive USCIS scrutiny.
- **Ask your employer how petitions are signed.** Workers relying on company-filed I-129 or I-140 petitions should ask, uncomfortable as it feels, how signatures are handled in batch filings.
- **Be cautious with e-signature tools.** Until there is clearer guidance, DocuSign-style signatures on USCIS filings carry risk; when in doubt, sign by hand.
- **Keep proof.** Retain evidence of how and when a form was signed, in case the agency questions it after acceptance.

The rule does not change who qualifies for a visa or a green card. It changes how easily a qualifying case can be thrown out on a technicality — and for a diaspora that files more of these forms than anyone, a technicality is not a small thing."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Consulates in the UAE Go Dark for Five Days — and 3.5 Million NRIs Have to Plan Around It",
        "subheadline": "Passport, visa and attestation services across the Emirates pause from June 26 to 30 as New Delhi hands the work to a new outsourced provider. Emergency cases continue; everything else waits for July 1.",
        "slug": make_slug("india-uae-passport-visa-services-pause-june-2026-al-hind-nri"),
        "category": "immigration",
        "vertical": "diaspora-services",
        "diaspora_angle": "The Gulf holds the largest concentration of overseas Indians anywhere, and a five-day blackout on passport and attestation services ripples straight into job contracts, school admissions and family travel for a community that depends on those documents to keep their lives running.",
        "tags": ["uae", "passport", "nri", "consular-services", "gulf"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AInvest", "url": "https://www.ainvest.com/news/indian-passport-visa-services-uae-pause-5-days-june-26/"},
            {"name": "Embassy of India, Abu Dhabi", "url": "https://www.indembassyuae.gov.in/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32176062/pexels-photo-32176062.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A close-up of passports at an airport, illustrating consular travel-document services",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For five days at the end of this month, the Indian community in the United Arab Emirates will not be able to renew a passport, lodge a visa application, or get a document attested through the usual channels. The Embassy of India in Abu Dhabi has confirmed that passport, visa and attestation services across the country will be suspended from June 26 to June 30 while the work transitions to a new outsourced service provider.

It is an administrative changeover, not a crisis. But in a country where Indians form the single largest expatriate group, even a five-day pause is the kind of thing that reorders a lot of calendars.

## What Is Changing

The handover replaces the existing providers with a single new operator, Al Hind Tours and Travel LLC. The incumbents — BLS International, which has handled passport and visa work, and SGIVS Global, which managed attestation — will stop accepting new applications after June 25. Al Hind takes over formally on July 1, when it will also launch a new online appointment portal.

The gap between the two systems is the blackout. During June 26 to 30, regular appointments will not be available. Emergency services, however, will continue to be offered directly by the embassy in Abu Dhabi and the Consulate General in Dubai — the carve-out that matters for anyone facing a genuine travel or medical emergency.

The embassy has given the community a set of channels for urgent help during the window: a toll-free number, 800 46342 (800 INDIA); a WhatsApp line at +971 54 309 0571; and email at pbsk.dubai@mea.gov.in. It has also urged residents to rely only on official communication, a standard caution whenever a provider switch creates room for misinformation and middlemen.

## Why This Lands Harder in the Gulf

To understand why a routine outsourcing change is news, look at the numbers behind it. The UAE is home to roughly 3.5 million Indians, one of the largest overseas Indian populations anywhere in the world. For this diaspora, consular paperwork is not occasional bureaucracy — it is the connective tissue of daily life.

A Gulf-based Indian's residency visa is tied to a valid passport. Job offers and renewals require attested educational certificates. School admissions for children, property transactions, family sponsorships, and travel home all run through the same document pipeline. When that pipeline pauses, even briefly, the effects fan out: a passport renewal that slips past a residency-visa deadline, an attestation that misses an employer's onboarding date, a family trip planned around a document that is not ready.

Unlike Indians in the US or UK, where immigration status tends to be employer- or study-linked and less dependent on frequent consular touchpoints, the Gulf model makes the consulate a recurring fixture. That is why a five-day suspension in Dubai or Abu Dhabi generates more anxiety than a comparable pause might in New York or London.

## The Practical Playbook

For NRIs in the Emirates, the message from the embassy amounts to: plan around the gap, and do not wait until the last minute.

- **File before June 25** if you have any application — passport renewal, visa, or attestation — that is due or close to due. After that date the existing providers stop accepting new work.
- **Check your dates now.** Anyone whose passport or residency visa expires in late June or early July should confirm there is enough runway, or move quickly before the cutoff.
- **Use emergency channels only for genuine emergencies.** The toll-free, WhatsApp and email lines are meant for urgent cases during the suspension, not routine queries.
- **Wait for July 1 for the new portal.** Al Hind's online appointment system goes live then; expect the usual early-rollout teething as a new operator absorbs the backlog that builds during the pause.

The transition is, in the long run, meant to streamline how millions of Indians in the UAE access government services. In the short run, it is a reminder of how much of diaspora life still runs on a passport, a stamp, and an appointment slot — and how a five-day gap in any of them is felt all the way from a labour camp in Abu Dhabi to a boardroom in Dubai."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
