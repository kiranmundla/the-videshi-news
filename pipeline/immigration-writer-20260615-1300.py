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

article1_body = """A signature is the most boring part of any immigration filing. Starting July 10, it may also be the most dangerous.

On May 11, the Department of Homeland Security published an interim final rule, codified at 8 CFR 103.2(a)(7)(ii)(A), that quietly rewrites the consequences of getting a signature wrong. Until now, a petition with a defective signature was usually *rejected* — returned unadjudicated, fee refunded, free to refile. Under the new rule, USCIS adjudicators gain explicit authority to *deny* such a filing instead: the fee is kept, the case is treated as decided against the petitioner, and there is no chance to fix the problem on the existing application.

The distinction sounds technical. It is not. A rejection is a do-over. A denial is a loss on the record.

## What counts as invalid

The rule draws a hard line around what a real signature is. Wet ink still works — and so do photocopies or scans of a wet-ink form, with USCIS reserving the right to later demand the original. What no longer works: typed names, signatures copied from another document, stamped signatures, and anything pasted in using software. The agency has signaled that copy-paste and certain Adobe-generated marks fall on the wrong side of the line, which puts a question mark over the DocuSign-style workflows many corporate immigration teams have leaned on for years.

Crucially, there is no cure mechanism. Under the old practice, an officer who spotted a questionable signature could issue a Request for Evidence and let the petitioner submit a corrected, wet-ink form. That door is closing. DHS expressly rejected a cure option, arguing that letting deficient filings be patched up would unfairly hold cap slots and priority dates ahead of properly signed petitions.

## Why this lands hardest on Indians

Indians are not singled out by the rule — but they are the population most exposed to it. Indian nationals account for more than 70% of approved H-1B petitions each year, and the H-1B is exactly the kind of high-volume, employer-filed petition where signature workflows are automated and a single template error can replicate across dozens of cases. The same is true of the I-140 immigrant petitions and I-485 adjustment applications that sit at the center of the EB-2 and EB-3 India backlog.

For a worker whose priority date has been waiting half a decade, a denial is not just a lost fee. If an extension or an adjustment filing is denied on a signature technicality rather than rejected, the timing can be brutal: a gap in status, a lost place in line, or a re-filing that lands behind everyone who signed correctly the first time. The people with the least slack — those near the end of a six-year H-1B clock, those with an I-485 pending — are the ones a paperwork denial can hurt most.

## What to do before July 10

The rule applies to any benefit request submitted on or after July 10, so the practical advice from immigration attorneys is unglamorous and urgent: audit your signature process now.

For individual filers, that means signing forms by hand, in ink, and resisting the temptation to reuse a scanned signature block across documents. For employers and the HR teams running high-volume H-1B and green-card programs, it means confirming that whatever e-signature tool they use produces something USCIS will accept — or reverting to wet ink for anything filed after the deadline. The cost of an extra printer run is trivial. The cost of a denied I-140 with a 2019 priority date is not.

The broader pattern is familiar to anyone tracking this administration's approach to legal immigration: not a dramatic ban, but a tightening of the procedural screws, where the burden of perfection shifts entirely onto the applicant. The $100,000 fee grabs headlines. A rule about how you sign your name will never trend. But for an Indian family whose future hinges on a pending petition, the second one may matter more."""

article2_body = """The questions on a U.S. visa form used to be about you: where you work, why you are coming, how long you will stay. Increasingly, they are about your timeline — the one you post.

Since December 15, 2025, H-1B specialty-occupation workers and their H-4 dependent spouses and children have been pulled into the same expanded social-media screening regime that has applied to students for years. The DS-160 nonimmigrant visa application already asks applicants to list every social-media platform and username they have used over the past five years. What changed is the depth of the review behind that question — and who it now reaches.

## What officers are looking at

Consular officers reviewing H-1B and H-4 applicants may now examine public posts, photos, comments, group affiliations, tags, and shared content as part of identity verification and consistency checks against the visa petition. Passwords are not requested. But there is a sharper edge: setting an account to private, or limiting its visibility, can itself be read as an attempt to evade or hide activity. In practice, the safest posture has become the most exposed one — public profiles, openly reviewable.

The requirement applies across the board: first-time H-1B applicants, H-1B renewals, anyone doing visa stamping abroad, and H-4 dependents applying alongside them. Failure to make accounts reviewable can result in delays, administrative processing, or outright refusal.

## Why this is an Indian story

No diaspora is more affected. Indians hold the overwhelming majority of H-1B visas, and the H-4 category — spouses, overwhelmingly women, many of them highly educated professionals — is dominated by Indian families. For the hundreds of thousands of Indian nationals who travel home to renew a stamp or sponsor a spouse, the consular interview is an unavoidable choke point, and now a digital one.

The mechanics matter for ordinary life. An Indian engineer in New Jersey who flies to the Mumbai or Hyderabad consulate for stamping is now subject to a review of five years of online activity. An H-4 spouse applying for the first time faces the same scrutiny before she has even set foot in the country. A post critical of a government, an old account half-forgotten, an ambiguous photo — any of these can become a line of questioning, or a reason for the dreaded "administrative processing" that can strand a worker abroad for weeks while a project waits.

## The quiet behavioral shift

The deeper effect is not procedural but psychological. When the price of a private account is suspicion, and the price of a stray post is a delayed visa, people self-censor. Immigration lawyers report clients scrubbing timelines, deactivating dormant accounts, and agonizing over whether a years-old comment might be misread. For a community that built much of its American foothold on the H-1B, the message is unmistakable: your online life is now part of your file.

## What applicants should do

The practical guidance is consistent. List every platform used in the past five years on the DS-160 accurately — omissions are far more damaging than disclosures, and a missing account can be construed as misrepresentation. Keep profiles public rather than locking them down right before an interview, which can itself raise flags. Review old posts for anything that could appear inconsistent with the visa category — a tourist-style post on a work visa, say. And keep records that corroborate the petition: employment letters, role descriptions, anything that backs up the story the form tells.

None of this is unique to Indians in its letter. But in its weight, it falls on them first. The H-1B made the Indian-American professional class. The screen, increasingly, decides who gets to keep the visa that carries it."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Sign It Wrong After July 10 and USCIS Keeps Your Fee — and Your Case",
        "subheadline": "A new federal rule lets adjudicators deny, not just reject, immigration filings with invalid signatures. There is no second chance, and Indians file the most affected petitions.",
        "slug": make_slug("uscis-signature-rule-july-10-deny-not-reject-h1b-i140-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians file more than 70% of H-1B petitions and dominate the EB-2/EB-3 green-card queue, so a rule that turns a signature defect into an unappealable denial — with the fee kept and priority date at risk — hits the diaspora harder than any other group.",
        "tags": ["uscis", "h1b", "i-140", "signature-rule", "green-card", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Ogletree Deakins (JD Supra)", "url": "https://www.jdsupra.com/legalnews/uscis-rule-raises-stakes-for-signature-1234567/"},
            {"name": "Gibney Anthony & Flaherty LLP", "url": "https://www.gibney.com/uscis-issues-interim-final-rule-to-increase-scrutiny-of-signature-requirements/"},
            {"name": "Reddy Neumann Brown PC", "url": "https://www.rnlawgroup.com/new-uscis-signature-rule-takes-effect-july-10-2026/"},
            {"name": "Holland & Hart LLP", "url": "https://www.hollandhart.com/new-uscis-signature-rule-could-put-immigration-filings-at-risk"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/48148/document-agreement-documents-sign-48148.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A pen resting on a signed official document, illustrating the signature requirements at the center of the new USCIS rule",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your Social Media Is Now Part of Your H-1B File — and Going Private Can Backfire",
        "subheadline": "Since December, H-1B workers and H-4 spouses face the same expanded online screening long applied to students. Setting accounts private can itself be read as hiding something.",
        "slug": make_slug("h1b-h4-social-media-screening-ds160-public-profiles-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold the vast majority of H-1B visas and dominate the H-4 dependent category, so the expanded social-media vetting at consulates — where workers and spouses must travel to stamp visas — falls on Indian families more than any other community.",
        "tags": ["h1b", "h4", "social-media", "ds-160", "visa-stamping", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "American Federation of Teachers (AFT) Information Sheet", "url": "https://www.aft.org/sites/default/files/media/documents/2026/social-media-visa-requirements.pdf"},
            {"name": "U.S. Department of State — DS-160 Online Nonimmigrant Visa Application", "url": "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/forms/ds-160-online-nonimmigrant-visa-application.html"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5633334/pexels-photo-5633334.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A smartphone displaying social media applications, reflecting the expanded online vetting now applied to H-1B and H-4 visa applicants",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article2_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   words: {wc} | {art['headline'][:60]}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
