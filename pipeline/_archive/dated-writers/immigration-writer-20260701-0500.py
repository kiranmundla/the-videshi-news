#!/usr/bin/env python3
"""Immigration writer — 2026-07-01 05:00 PDT run."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ──────────────────────────────────────────────
# ARTICLE 1: F-1 Student Visa Crash
# ──────────────────────────────────────────────

art1_body = """The numbers are stark. Between May and August 2025, F-1 student visa issuances to Indian nationals fell 69 per cent compared to the same window a year earlier, according to a Chronicle of Higher Education analysis of State Department data. In July and August alone — the peak months for fall-intake processing — the decline was closer to 78 per cent. Indian students went from 41,336 F-1 visa grants to just 12,776.

The crash was not a blip. It was the steepest drop among any major source country, worse than China (down 33 per cent), Vietnam (down 17 per cent), or Nigeria (down 63 per cent). The global average fell 36 per cent. India's number fell off a cliff.

## What went wrong

Several forces converged. The Trump administration suspended visa interviews at US consulates for nearly a month in May 2025, creating a backlog that swallowed the entire summer intake cycle. Thousands of student visas were revoked in early 2025 amid broader immigration enforcement. And the social media vetting mandate — which requires all H-1B, H-4, F-1, and J-1 applicants to set their profiles to public — added weeks to processing times at Indian consulates in Chennai, Hyderabad, and Mumbai.

Then came the structural blow. On May 5, 2026, the Department of Homeland Security proposed eliminating the Duration of Status framework that has governed F-1 visas for decades. Under the current system, international students can remain in the US as long as they maintain their student status. The proposed rule would replace that with a fixed four-year admission period, after which any extension — including for post-graduation work — would require formal USCIS approval.

The grace period after a student's status ends would shrink from 60 days to 30, narrowing the window to find an employer willing to sponsor an H-1B petition.

## The OPT question

For Indian STEM students, the calculus has always been simple: spend $60,000 to $100,000 on a US degree, then recoup the investment through Optional Practical Training, which allows up to three years of post-graduation work. OPT is not a perk. It is the financial logic of the entire enterprise.

That logic is now under strain. Acting USCIS Director Robert Edlow has publicly stated his desire to end OPT. While no formal rule has been issued, the Duration of Status proposal chips away at the programme's foundations. Students who currently rely on Day-1 CPT — enrolling in a second master's programme to maintain work authorisation while waiting for the H-1B lottery — would find that route significantly narrower. DHS's proposal makes it harder to justify a second degree purely for immigration purposes.

"For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation,'" said Danielle Goldman, co-founder and CEO of Build, an immigration technology firm.

## The alternatives are getting crowded

Indian students are not simply staying home. They are redirecting. Applications to graduate management programmes in India rose 25 per cent in 2025. Western Europe — Germany, Ireland, France — saw a six-percentage-point rise in preference among Indian students in a single year, drawn by English-taught programmes, lower costs, and clearer post-study work rules. Asia-Pacific programmes reported 54 per cent higher international enrolment in fall 2025.

The irony is that some American universities, suddenly facing empty seats, are offering merit aid to international applicants for the first time. Carnegie Mellon, Purdue, and other schools that historically gave nothing to international students are now dangling scholarships.

But the GMAC's 2026 white paper, "The Great Re-Routing of Global Business Talent," found that nearly 90 per cent of US programmes reported India as the top country where students paid admission deposits but did not ultimately enrol — primarily due to visa delays, denials, or students holding multiple offers while waiting for clarity.

## Why this matters to you

If you are an Indian professional on an H-1B, this is not just a student problem. The F-1 pipeline feeds the H-1B pool. Fewer Indian students entering US universities today means fewer qualified H-1B candidates three to five years from now. It means your employer will have a smaller bench of talent to draw from, and it means the political constituency that argues H-1B holders "take American jobs" will grow louder as the visible presence of Indian professionals in the US shrinks.

The 2019 GMAC survey found 57 per cent of non-US candidates preferred studying in America. By 2025, that figure had dropped to 42 per cent. The pipeline is not broken. It is being rerouted — and the destination is no longer guaranteed to be the United States."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "F-1 Visa Grants to Indian Students Fell 69 Per Cent. The H-1B Pipeline Will Feel It Next",
    "subheadline": "A collapsing student pipeline, a proposed end to Duration of Status, and an OPT programme on borrowed time are reshaping the calculus for every Indian family weighing an American degree.",
    "slug": make_slug("f1-visa-indian-students-69-percent-decline-h1b-pipeline"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Fewer Indian students entering US universities today means a smaller H-1B talent pool in three to five years, affecting employers, the political climate around skilled immigration, and the next generation of Indian professionals in America.",
    "tags": ["f1-visa", "indian-students", "opt", "stem-opt", "duration-of-status", "h1b-pipeline", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Collegedunia / Chronicle of Higher Education", "url": "https://collegedunia.com/usa/article/us-f1-visa-drop-69-what-indian-students-must-know-for-2026"},
        {"name": "ICEF Monitor", "url": "https://monitor.icef.com/2026/03/us-student-visa-issuances-fell-by-36-in-summer-2025-opt-uncertainty-among-factors-affecting-international-student-demand/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "GMAC 2026 White Paper", "url": "https://collegedunia.com/usa/article/us-f1-visa-drop-69-what-indian-students-must-know-for-2026"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7683694/pexels-photo-7683694.jpeg",
    "image_caption": "College students outside a modern university building",
    "image_attribution": "Pexels",
    "body": art1_body,
}


# ──────────────────────────────────────────────
# ARTICLE 2: GOPIO Letter to Trump on $100K Fee
# ──────────────────────────────────────────────

art2_body = """The Global Organization of People of Indian Origin has written to the White House asking President Trump to reconsider the $100,000 fee on new H-1B visa petitions — or, at the very least, reduce it substantially. The letter, signed jointly by GOPIO International Chairman Dr Thomas Abraham and President Prakash Shah, frames the appeal not as an Indian grievance but as an American economic argument.

"The H-1B visa program has long been an essential driver of American growth and innovation," the letter reads. "We urge the Administration to reconsider this significant fee increase, which we believe would run counter to the best interests of the United States."

It is a carefully calibrated move. GOPIO is not a scrappy advocacy group. It is the largest global network of the Indian diaspora, with chapters in dozens of countries and a membership base of naturalised American citizens. By addressing Trump as fellow stakeholders in American competitiveness — rather than as aggrieved immigrants — the organisation is testing whether the language of economic patriotism can cut through the administration's hardline stance.

## The economic case

The letter lays out a case that immigration economists have been making for years, but that rarely gets a hearing in Washington:

**Innovation and competitiveness.** A disproportionate share of H-1B professionals work in STEM fields — technology, biotech, engineering — where US companies face persistent talent shortages. Their work has contributed directly to new patents and groundbreaking technologies. Patents issued to F-1 students who later apply for H-1B visas generate revenues for the United States. If those patents and research move abroad, American citizens lose access to the intellectual property that their universities helped produce.

**Labour market complementarity.** H-1B professionals complement rather than displace American workers, GOPIO argues, by filling highly specialised roles that spur business expansion and create additional jobs for US citizens across industries.

**Fiscal contribution.** H-1B holders pay federal, state, and local taxes while being ineligible for most social welfare programmes — a net-positive fiscal contribution that the $100,000 fee would reduce by pricing out all but the largest employers.

## The fee's chilling effect

The numbers back the argument. As of February 15, 2026, USCIS had received just 85 payments of the $100,000 fee, according to an administration filing in the California v. Mullin litigation. Before the fee, a typical H-1B petition cost an employer $2,000 to $5,000. The hundredfold increase has not eliminated demand — OpenAI and a handful of well-capitalised technology firms have absorbed it — but it has effectively divided the H-1B market into two tiers: companies that can afford to pay and everyone else.

Startups, non-profits, rural hospitals, and university research labs cannot. The American Association of Physicians of Indian Origin, which represents more than 100,000 Indian-American doctors, has warned that the fee threatens physician recruitment in underserved and rural communities where international medical graduates fill critical gaps.

A federal judge struck down the fee on June 8 as an unlawful tax that Congress never authorised. But the government appealed, and a temporary stay on June 12 allowed USCIS to keep collecting the fee while the case proceeds in the First Circuit. For now, the $100,000 stands.

## Why GOPIO's letter matters

Indian Americans are the highest-earning ethnic group in the United States, with a median household income of roughly $150,000. They vote, they donate, and they organise. GOPIO's intervention is a signal that the community's civic infrastructure — which has historically preferred quiet influence to public advocacy — is shifting toward direct engagement.

The letter also serves a practical function. The Trump administration has shown itself responsive to economic arguments when they come from constituencies it considers allied. GOPIO's members are overwhelmingly naturalised citizens, many of them Republican donors and business owners. Their critique of the fee carries a different political valence than the same argument made by the ACLU or the National Immigration Law Center.

Whether the letter changes policy is another matter. The administration has signalled through Commerce Secretary Howard Lutnick that it intends to overhaul the H-1B programme entirely, replacing the lottery with a merit-based system and introducing a "gold card" residency programme for investors willing to put up $5 million. The $100,000 fee may be a negotiating chip — a maximalist opening position designed to make whatever replaces it look moderate by comparison.

But for the 600,000-odd Indian nationals currently in the H-1B queue, the fee is not an abstraction. It is the number that determines whether their employer renews their petition or lets them go. GOPIO's letter will not change that overnight. What it does is put the Indian American community's most established institution on the record — and on notice that silence is no longer an option."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "GOPIO Tells Trump the $100,000 H-1B Fee Will Hurt America More Than It Hurts India",
    "subheadline": "The largest global Indian diaspora organisation has written to the White House with an economic case against the fee — framing it as a threat to American competitiveness, not just an immigrant burden.",
    "slug": make_slug("gopio-letter-trump-100k-h1b-fee-american-competitiveness"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "GOPIO's intervention signals that Indian American civic organisations are shifting from quiet influence to direct advocacy, putting the community's most established institution on the record against a policy that affects hundreds of thousands of H-1B holders.",
    "tags": ["gopio", "h1b-fee", "100k-fee", "indian-american", "diaspora-advocacy", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/28/gopio-appeals-to-president-trump-to-reconsider-or-substantially-reduce-new-h1-b-fee-for-americas-interest/"},
        {"name": "Reuters", "url": "https://www.reuters.com/legal/government/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
        {"name": "WR Immigration / Wolfsdorf", "url": "https://wolfsdorf.com/court-temporarily-reinstates-uscis-authority-to-collect-100000-h-1b-consular-processing-fee-pending-appeal/"},
        {"name": "Fragomen", "url": "https://www.fragomen.com/insights/united-states-uscis-issues-guidelines-on-the-new-h-1b-fee.html"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/The_White_House%2C_Washington%2C_D.C._USA2.jpg/1280px-The_White_House%2C_Washington%2C_D.C._USA2.jpg",
    "image_caption": "The White House in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}


# ──────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
