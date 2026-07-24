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

article1_body = """The U.S. Embassy in New Delhi spent this weekend reminding Indians of something most of them would rather not think about: getting the visa was the easy part. Keeping it is now a permanent audition.

"U.S. visa screening does not stop after a visa is issued," the embassy posted on Saturday. "We continuously check visa holders to ensure they follow all U.S. laws and immigration rules — and we will revoke their visas and deport them if they don't." For a country that sends more people to America on work and study visas than almost anyone, the message was less a warning than a description of how the machinery now runs.

## The numbers behind the warning

The phrase doing the heavy lifting is "continuously check." The State Department revoked more than 100,000 visas in 2025, roughly 150% above the 40,000 it cancelled in 2024. That jump is not an accident of paperwork. It is the output of a new Continuous Vetting Center that runs about 55 million visa holders against law-enforcement and security databases on a rolling basis — the first time such a sweeping review has been pointed at people who already hold approved visas rather than at fresh applicants.

The practical effect is that a record which once sat quietly can now surface years later and trigger a cancellation. A dismissed misdemeanor, an old DUI, a minor police encounter that never went anywhere — any of these can now appear as a hit and start a review. So can losing the eligibility that justified the visa in the first place. For an H-1B holder, that includes the most ordinary event in a tech career: a layoff. Lose the job, and the legal ground under the visa starts to erode while the 60-day grace clock runs.

## Why this lands hardest on Indians

India is one of the largest sources of U.S. visa holders across every category — H-1B workers, F-1 students, and the families riding along on H-4 and F-2 status. A monitoring regime applied to "all visa holders" is, in raw numbers, disproportionately a regime applied to Indians, simply because there are so many of them in the pool.

The student channel shows where the scrutiny is heading. Since last month, anyone applying for an F, M, or J visa has been asked to set every social-media account to public so consular officers can vet it — looking, in the administration's words, for "any indications of hostility toward the citizens, culture, government, institutions or founding principles of the United States." Thousands of student visas were already revoked in a similar sweep earlier this year, several later shown to rest on faulty data that was never verified before the cancellation went out.

That is the quiet risk in continuous vetting: the system can be wrong, and the burden of proving it wrong falls on the visa holder, often after the damage is done.

## How a revocation actually reaches you

The cruelest feature is the lack of a clear knock on the door. A revocation can take effect without obvious notice. Some people learn of it only when they are denied boarding on a flight to the U.S., or pulled aside at a port of entry, because airlines and border officers receive real-time updates that the traveler does not.

Immigration lawyers now advise a defensive routine that would have seemed paranoid two years ago. Check the Consular Electronic Application Center status tracker before booking any international travel. Watch the email address on the DS-160, where the State Department sends revocation notices. Keep documentation of status, employment, and any resolved legal matter within reach. And treat any trip abroad — even a wedding in Hyderabad or a parent's funeral — as a decision with re-entry risk attached, not a routine flight.

## What's next

None of this changes the law on its face; the grounds for revocation under INA 221(i) and 22 CFR 41.122 have existed for years. What changed is enforcement capacity. A 55-million-record monitoring engine turns dormant authority into routine practice.

For the Indian professional weighing whether to switch jobs, contest a parking-adjacent citation, or fly home for a family emergency, the calculus is now permanently altered. The visa in the passport is no longer a settled fact. It is a status that has to be earned again every day — and one the government has built the tools to revisit at any moment."""

article2_body = """Standing at the G7 summit in Evian on June 17, President Donald Trump offered Indian professionals a sentence they have not heard much of late: "highly skilled Indians will get more opportunities." For an administration that has spent the past year making H-1B sponsorship more expensive and more uncertain, it was a striking change in tone — and Indians parsing it for meaning should be careful about how much weight a summit aside can hold.

## A signal, not a policy

Let us be precise about what happened. Trump made a favorable remark about skilled Indian talent on the sidelines of a summit where he and Indian officials said they were moving closer to a trade agreement. No formal immigration announcement followed. No proclamation, no USCIS guidance, no change to the visa bulletin. The H-1B cap remains exactly where it was — 85,000 slots, with 65,000 in the regular pool and 20,000 reserved for U.S. advanced-degree holders.

What the remark does is fit a pattern. The same administration that imposed a $100,000 supplemental fee on many overseas H-1B hires has also framed its policy as "merit-based" rather than anti-immigrant — a preference for the highest-paid technical workers over volume hiring by staffing firms. Read against that backdrop, "highly skilled Indians will get more opportunities" is less a promise of open doors than a description of who the administration wants walking through the narrower one it has built.

## The fine print already on the books

The structural changes matter far more than the summit soundbite. Effective February 27, 2026, the random H-1B lottery was replaced by a wage-weighted selection system that gives priority to higher wage levels. Level III and Level IV offers now hold the strongest position; entry-level Level I wages — the ones new graduates and recent OPT workers typically command — sit at the back of the queue.

That single change quietly redraws who benefits from any "more opportunities." A senior AI engineer at a top lab is in a far better spot than a 24-year-old fresh out of a master's program. The merit framing rewards those who already command high salaries, which in practice favors established professionals over the students India sends in the largest numbers.

## The COMPACT context

Trump's words also sat alongside the U.S.-India COMPACT framework discussed around the summit, an effort to deepen commercial and technology links between the two countries. If that framework produces anything concrete on mobility — a dedicated visa channel, faster processing for AI and biotech specialists, or a carve-out from the $100,000 fee for designated sectors — then the summit remark would look retrospectively like a preview. If it does not, it will read as diplomacy.

The honest answer today is that nothing has been signed. The COMPACT is a stated intention, and intentions at summits have a long history of not surviving contact with domestic politics.

## What it means for the diaspora

For Indians already in the U.S. on H-1B status, the practical takeaway is muted: a friendly remark changes none of the rules they live under, including the wage-weighted lottery, the fee fight winding through the courts, and the EB-2 backlog that pushed India's date back more than ten months in the June bulletin.

For prospective applicants, the signal is worth noting but not banking on. The administration is telling high-earning specialists in AI, biotech, defense, and advanced engineering that they are wanted. It is telling entry-level graduates, through the wage rules, that the path has narrowed. A summit compliment does not rewrite that arithmetic.

The right way to read June 17 is as a tone-setter ahead of a trade deal, not as immigration policy. Indians have learned the hard way over the past year to check the date on every claim about their status — and to trust the proclamation in force over the applause line at a podium. Until COMPACT produces text, "more opportunities" remains a sentiment, not a slot."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Visa in Your Passport Is No Longer a Settled Fact",
        "subheadline": "The U.S. Embassy's weekend warning that screening 'does not stop' after issuance is backed by a 55-million-record monitoring engine — and Indians make up an outsized share of who it watches.",
        "slug": make_slug("us-embassy-continuous-vetting-visa-revocation-surge-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold one of the largest shares of U.S. work and student visas, so a continuous-vetting regime aimed at 'all visa holders' falls disproportionately on the diaspora — and a layoff or an old dismissed charge can now trigger revocation years later.",
        "tags": ["visa-revocation", "continuous-vetting", "h1b", "f1", "uscis", "state-department"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/"},
            {"name": "Duane Morris Immigration Law", "url": "https://blogs.duanemorris.com/"},
            {"name": "Lexology", "url": "https://www.lexology.com/"},
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Close-up of an open passport showing travel stamps at an airport",
        "image_attribution": "Pexels",
        "body": article1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Trump Says 'Highly Skilled Indians' Will Get More Opportunities. Read the Fine Print First",
        "subheadline": "A favorable line at the G7 summit cheered Indian professionals — but no policy changed, and the wage-weighted lottery already decides who 'highly skilled' rewards.",
        "slug": make_slug("trump-g7-highly-skilled-indians-compact-wage-h1b-signal"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the largest source of H-1B applicants, so a presidential signal about 'skilled talent' is parsed closely — but the wage-weighted selection rules mean the benefit flows to high-earning senior specialists, not the entry-level graduates India sends in the largest numbers.",
        "tags": ["h1b", "trump", "g7", "us-india-compact", "wage-lottery", "merit-immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "People Matters", "url": "https://www.peoplematters.in/"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"},
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/13/Official_Presidential_Portrait_of_President_Donald_J._Trump_%282025%29_%28cropped%29%282%29.jpg",
        "image_caption": "Official presidential portrait of Donald J. Trump",
        "image_attribution": "Wikimedia Commons",
        "body": article2_body,
    },
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']} ({wc} words): {e}")
