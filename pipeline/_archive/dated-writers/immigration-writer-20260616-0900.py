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

body1 = """A judge in Boston has knocked down the single most expensive obstacle the Trump administration ever placed in front of an H-1B petition. Whether that relief survives the year is a different question entirely.

On Monday, U.S. District Judge Leo Sorokin ruled that the $100,000 fee imposed on new H-1B petitions last September is an unlawful tax that Congress never authorized the president to levy. The fee, announced by proclamation and implemented by the Department of Homeland Security for any petition filed after September 21, 2025, had raised the cost of a single H-1B filing from a few thousand dollars to six figures. Sorokin, ruling in a suit brought by 20 Democratic state attorneys general, concluded that "the substance and application of the $100,000 payment reveal that it is a tax, regardless of what the payment is called."

The legal reasoning leans on a familiar source. Sorokin cited the Supreme Court's February decision striking down the administration's emergency-powers tariffs, reasoning that if the president cannot manufacture a tax out of trade law, he cannot manufacture one out of immigration law either. The Immigration and Nationality Act, the judge found, contains no delegation of Congress's taxing power to the executive branch.

## A win on paper, a patchwork in practice

For Indian professionals — who collect more than 70% of approved H-1B petitions every year — the ruling reads like the cavalry arriving. It is more complicated than that.

The Boston decision is a summary judgment, and so was an earlier ruling that went the other way. In December, a federal judge in Washington rejected the U.S. Chamber of Commerce's challenge to the same fee, leaving it in force. The Chamber has appealed. A third lawsuit, filed by religious and labor groups in San Francisco, is still pending. That sets up the real possibility of contradictory rulings across three appellate circuits — the kind of split that tends to end at the Supreme Court.

The White House has already signaled it will appeal. Spokeswoman Taylor Rogers said the administration is "confident this order will be reversed," noting that a Washington judge had upheld a nearly identical order. Until an appeals court or the Supreme Court resolves the conflict, the fee's legal status is, in practice, a coin toss that depends on which courtroom a given dispute lands in.

## What an Indian H-1B applicant should actually do

The honest answer is: wait, and document everything.

Employers who already paid the $100,000 fee on petitions filed after September 21 are now in limbo. Sorokin vacated the policy "in its entirety," which on its face means those payments were collected under an unlawful rule. But there is no refund mechanism in place, no USCIS guidance yet on how vacated-fee petitions will be treated, and an active appeal that could reinstate the charge. Anyone who paid should keep their receipts and filing records intact; if the ruling holds, those documents are the basis for any claim.

For applicants who have not yet filed, the calculus is murkier still. The fee was widely understood to apply to petitions for workers outside the United States, while those changing status from within — F-1 students moving to H-1B, for instance — were treated as exempt. That exemption logic matters less now that the fee itself is vacated, but it could snap back if an appeals court reinstates the policy. The weighted lottery, which now favors higher-wage positions, remains untouched by this ruling and is a separate fight.

The deeper lesson for the Indian diaspora is structural. The $100,000 fee was only ever a temporary proclamation, scheduled to expire in September 2026 even if no court had touched it. The instinct to treat any single ruling as the final word has burned applicants before — the on-again, off-again travel restrictions of 2025 taught that much. A vacated fee is good news. A vacated fee that three circuits are still arguing about is not a planning foundation.

## What comes next

Watch the First Circuit, where the administration's appeal of Sorokin's ruling will land, and watch whether the Justice Department seeks a stay that would let the fee stand while the appeal proceeds. A stay would effectively reverse Monday's relief within weeks. Watch, too, for any USCIS notice on how it will handle petitions filed during the fee window — that guidance, whenever it arrives, will tell Indian applicants and their employers far more about their money than the headline did.

For now, the most expensive line item in the H-1B program has been crossed out. The pencil is still hovering."""

body2 = """The most consequential immigration fight for Indian doctors and nurses this year is not happening at a consulate. It is happening on Capitol Hill, in a bill that would do something the system has refused to do for two decades: stop letting employment green cards expire unused.

Legislation reintroduced in Congress would phase out the per-country quota for green cards and recapture visas that went unclaimed in prior years, channeling many of them to physicians and nurses. For Indian healthcare workers — who sit at the back of the longest backlog in the system — the bill is the rare proposal that targets exactly where they are stuck. Whether it moves is another matter, but the timing is not an accident. It lands as the H-1B program, the main pipeline for foreign-trained clinicians, is buckling under a separate set of pressures.

## A pipeline running dry

The numbers from the hospital side are stark. In a survey of more than 1,000 health systems conducted by the American Hospital Association, over 70% said they expect the $100,000 H-1B petition fee to directly affect patient care, and 64% said they would pause, defer, or limit recruitment because of it. Fifty-seven percent of the positions those hospitals would have filled with H-1B workers were clinical roles.

The effect is already visible in rural America. Northern Light Health, which serves 800,000 people across Maine, normally takes on four to eight new H-1B clinicians a year. This year, no one applied. Even if applicants had come forward, the system's administrators said they could not realistically absorb a $100,000 fee per hire. A federal judge struck that fee down on Monday, but the relief is under appeal and far from settled — and the structural backlog the recapture bill targets would remain even if the fee vanished tomorrow.

## Why this is an Indian story

Indians do not just dominate the H-1B program; they dominate its medical corner. Tens of thousands of Indian-trained physicians staff American hospitals, and the country-of-birth cap means an Indian doctor approved for a green card today can wait decades for one to actually become available. The June 2026 visa bulletin made the squeeze brutally literal: EB-2 India retrogressed by more than ten months to a final action date of September 1, 2013, and the State Department confirmed that EB-2 India had hit its annual per-country limit and would be unavailable until October 1.

Read that again. An Indian physician with an approved petition and a priority date after September 2013 currently has no green card number available at all. The recapture bill attacks this directly by abolishing the per-country ceiling that forces Indians into a queue no other nationality faces, and by pulling unused visas from past years back into circulation specifically for nurses and doctors. For an Indian clinician who has spent a decade on an H-1B renewing every three years, that is the difference between permanent residence in this lifetime and a wait that outlasts a career.

## The catch

Country-cap reform has a graveyard's worth of precedent. Versions of this idea have been introduced, debated, and quietly killed in nearly every Congress since 2011. The opposition is bipartisan and durable: smaller-volume countries resist losing their share, restrictionists resist any expansion, and the bill's fate usually hinges on whether it can be attached to something larger that has to pass.

What is different this time is the healthcare framing. By tying recapture to nurses and physicians — and arriving alongside hard AHA data on patient-care impact — the bill's sponsors are betting that a workforce argument travels further than an immigration argument. Hospitals in rural and Republican districts are the ones short of doctors, which gives the proposal a constituency it has historically lacked.

## What to watch

For Indian healthcare workers, three things matter in the coming weeks. First, whether the bill draws Republican co-sponsors from rural states — without them, it is a messaging exercise. Second, whether it gets folded into any year-end legislative package, which is how immigration provisions usually survive. Third, the July visa bulletin, which will show whether EB-2 India stays frozen and whether EB-3 inches forward at all.

The honest read: a standalone recapture bill rarely becomes law on its own. But the healthcare shortage is real, the data is on the table, and Indian clinicians are, for once, at the center of an argument that hospitals are willing to make for them. That is not nothing — it is just not yet a green card."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Boston Judge Just Voided the $100,000 H-1B Fee. Three Other Courts Could Bring It Back",
        "subheadline": "Judge Sorokin ruled the six-figure fee an unlawful tax, but an appeal and a looming circuit split mean Indian applicants who already paid are stuck in limbo.",
        "slug": make_slug("sorokin-ruling-voids-100k-h1b-fee-appeal-circuit-split-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians collect over 70% of approved H-1B petitions every year, so a fee that turns each filing into a six-figure bet — and the uncertainty over whether courts will keep it struck down — falls hardest on Indian professionals and the employers who sponsor them.",
        "tags": ["h1b", "uscis", "immigration", "h1b-fee", "visa-policy"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/government/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-15/"},
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/15/trump-h1b-visa-fee-struck-down-judge/"},
            {"name": "Associated Press (via Audacy)", "url": "https://www.audacy.com/news/federal-judge-strikes-down-trumps-100000-fee-on-new-h-1b-visas"},
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/16/mike-kennedy-protect-act-h1b-fee-sorokin-ruling/"}
        ]),
        "score_total": 86,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20185389/pexels-photo-20185389.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The columned facade of a United States federal courthouse, where the H-1B fee challenge was decided.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Green Card Bill That Could Finally Reach Indian Doctors Stuck Behind a Decade-Long Wall",
        "subheadline": "A push to scrap the per-country quota and recapture unused visas for nurses and physicians lands as the H-1B pipeline that feeds American hospitals runs dry.",
        "slug": make_slug("green-card-recapture-bill-per-country-cap-indian-doctors-nurses"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian-trained physicians and nurses staff American hospitals in large numbers but face a green card backlog measured in decades because of the per-country cap; a recapture bill aimed squarely at healthcare workers is the rare proposal that targets exactly where Indians are stuck.",
        "tags": ["green-card", "eb2", "eb3", "immigration", "healthcare", "visa-backlog"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/legislation-in-us-congress-to-phase-out-country-quota-for-green-cards/"},
            {"name": "American Hospital Association", "url": "https://www.aha.org/fact-sheets/impact-of-h-1b-filing-fee-on-the-health-care-workforce"},
            {"name": "Medscape", "url": "https://www.medscape.com/viewarticle/5-things-doctors-should-know-about-h-1b-visa-changes"},
            {"name": "JD Supra (Ogletree Deakins) — June 2026 Visa Bulletin", "url": "https://www.jdsupra.com/legalnews/uscis-requires-final-action-dates-for-june-2026/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4173244/pexels-photo-4173244.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A hospital corridor; American health systems rely heavily on foreign-trained clinicians, many of them from India.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body2
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   [{art['slug']}] words={wc} headline_len={len(art['headline'])}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
