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

scotus_body = """The Supreme Court has agreed to decide whether the government can hold noncitizens in detention for months — or years — without ever giving them a hearing to ask for release. For most Indian Americans, the case sounds like someone else's problem. It is not.

The case, *Genalo v. Black*, turns on two lawful permanent residents — green card holders — whom the government moved to deport after criminal convictions. One was held for seven months, the other for nearly two years, neither given a chance to argue before a judge that he was not a flight risk or a danger and should be let out on bond. The Second Circuit Court of Appeals in New York ruled in their favor, finding that the Fifth Amendment's due process clause requires a bond hearing once detention becomes "unreasonably prolonged," and that the burden falls on the government to justify keeping someone locked up. The Trump administration appealed, calling that reasoning "seriously misguided." The justices took the case in June and will hear it next term.

## What the case actually decides

Two questions are on the table. First, can immigration officials detain someone indefinitely while removal proceedings drag on, or must they offer a bond hearing once the detention stretches past what is reasonable? Second, if a hearing is required, who carries the burden — does the government have to prove with "clear and convincing evidence" that the person should stay detained, or does the detainee have to prove he deserves release?

The statute at issue mandates detention for noncitizens convicted of a defined list of crimes. The detail that should worry the diaspora is what the administration has done around that statute: it has reclassified broad categories of immigrants to sweep far more people into mandatory detention, a maneuver challenged repeatedly in lower courts and now drifting toward the high court.

## Why this reaches the green card line, not just the undocumented

There is a comfortable assumption among many Indian professionals that permanent residency is the finish line — that once the green card arrives, the years of visa anxiety are over. *Genalo v. Black* is a reminder that the card is a status, not a shield. Both men at the center of the case were lawful permanent residents. Both were detained without a bond hearing. The principle the Court is being asked to bless is that a green card holder facing removal can be held without the ordinary right to ask a judge for release.

Indians hold the largest backlog of employment-based green cards in the system — over a million are waiting — and a growing share have finally crossed into permanent residency after a decade or more. The category of "deportable green card holder" is wider than it sounds: an old conviction, a plea taken years ago without understanding the immigration consequences, or a charge later reclassified as an "aggravated felony" can all trigger removal proceedings. If the Court sides with the government, the people swept up could sit in detention for the length of those proceedings with no automatic right to a hearing.

## The track record is not encouraging

The Supreme Court has handed the administration a string of immigration wins on its emergency docket — allowing deportations to third countries, permitting the revocation of temporary status for hundreds of thousands of Venezuelans. A 2016 case raising a similar question ended with the Court ruling that federal law did not require bond hearings, though it pointedly declined to answer whether the Constitution does. *Genalo* puts that constitutional question squarely in front of the justices.

## What it means for the diaspora

For an Indian professional weighing whether to fight a removal case from inside the country or accept departure, the answer to this case changes the math entirely. A guaranteed bond hearing means the difference between defending yourself from home and defending yourself from a detention facility for the duration. Immigration attorneys advising green card holders with any criminal history — however old, however minor it once seemed — are watching this docket closely. The ruling will not come quickly; arguments fall in the next term, with a decision likely in 2027. But the question it settles is foundational: whether a green card, in the end, comes with the right to ask a judge to let you go home.

**Sources:** CNN, Reuters, Washington Examiner."""

denat_body = """The Justice Department plans to file at least 250 cases to strip naturalized Americans of their citizenship by October, a senior official told CNN — a pace that would, in a single year, rival the entire output of the previous two decades. For the Indian American community, among the largest naturalized populations in the country, the number is not an abstraction.

In under two months this year, the department has already filed 29 denaturalization cases against foreign-born citizens it accuses of fraudulently obtaining naturalization. To put that in perspective: between 2008 and June 2026, a total of 166 such complaints were filed, an annual average of fewer than ten, according to Syracuse University's Transactional Records Access Clearinghouse. The administration is not nudging the dial. It is breaking the instrument.

## How the machine is being built

Behind the surge is a quiet reallocation of legal firepower. The Justice Department has pulled civil litigators from divisions across the building — including teams assigned to fraud investigations, another stated priority — and redirected them to denaturalization work. Cases are also being routed to U.S. Attorney's offices already stretched thin. "This is a lawful tool that Congress has had on the books for decades," the senior DOJ official told CNN, framing the push as protecting "the integrity of American citizenship."

The mechanism matters. These are overwhelmingly *civil* denaturalization cases, not criminal ones. That distinction is the whole game: in a civil proceeding, there is no right to a court-appointed lawyer, the burden of proof is lower than "beyond a reasonable doubt," and the government can reach back decades. A naturalized citizen sued civilly must mount — and pay for — their own defense against the full resources of the federal government.

## The Indian cases are already landing

This is not hypothetical for the diaspora. On June 15, the U.S. Attorney's Office in Oregon filed a civil denaturalization complaint against Jaswinder Singh, a 54-year-old Oregon man from India, accusing him of using a second identity to obtain residency and, eventually, citizenship after an initial application was denied and a deportation order ignored. It is the first denaturalization case filed in Oregon during Trump's second term. Separately, the DOJ has pursued cases tied to alleged H-1B petition fraud, including a high-profile matter involving a citizen naturalized in 2017.

These cases tend to hinge on alleged misstatements or omissions in immigration filings — a discrepancy in a date, an undisclosed prior application, an identity question — sometimes from filings made twenty or thirty years ago. The legal theory is "illegally procured naturalization": that the citizenship was never validly obtained in the first place, and so can be undone.

## Why naturalized Indians should pay attention

Indians naturalize in large numbers and travel the long, document-heavy path from F-1 to OPT to H-1B to green card to citizenship — a paper trail spanning decades and dozens of forms. Each form is a sworn statement. A surge in denaturalization filings raises the stakes on the accuracy of every one of them, including those filed long ago under different circumstances, sometimes with the help of attorneys or agents whose work the applicant never independently verified.

The chilling part is structural. Naturalized citizens have always, in theory, been subject to denaturalization for fraud. What changes when the annual volume jumps from single digits to 250-plus is the felt security of the status. Citizenship has been the one rung on the immigration ladder that felt permanent. A campaign at this scale tells naturalized Americans that the rung can, in rare but rising cases, be sawed off.

## What to actually do

Immigration lawyers offer measured advice: this is a campaign aimed at cases with alleged material fraud, not a dragnet for ordinary citizens, and the vast majority of naturalized Indians have nothing to fear. But they also recommend that anyone with irregularities in their immigration history — an old denied application, a name or date discrepancy, a filing handled entirely by a third party — review their file with counsel rather than wait for a letter. Keep copies of old filings. Understand what was submitted in your name. For a community that has treated the citizenship certificate as the end of the immigration journey, the message from this docket is that the file never fully closes.

**Sources:** CNN, Statesman Journal, Transactional Records Access Clearinghouse (Syracuse University)."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Supreme Court Will Decide if a Green Card Comes With the Right to Ask a Judge for Release",
        "subheadline": "Genalo v. Black asks whether permanent residents can be detained for months without a bond hearing. For a diaspora finally crossing into the green-card line, the card is a status, not a shield.",
        "slug": make_slug("supreme-court-genalo-black-green-card-detention-bond-hearing-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold the largest employment-based green-card backlog and a growing number have finally reached permanent residency — a Supreme Court ruling against bond hearings would mean a green card holder facing removal could be detained for the length of proceedings with no automatic right to ask a judge for release.",
        "tags": ["green card", "supreme court", "detention", "immigration", "permanent residents"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CNN", "url": "https://www.cnn.com/2026/06/16/politics/supreme-court-migrants-bond-hearings"},
            {"name": "Reuters", "url": "https://www.reuters.com/legal/supreme-court-hear-trump-appeal-detention-immigrants-2026/"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/policy/courts/supreme-court-indefinite-detention-criminal-immigrants/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg/1280px-Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg",
        "image_caption": "The United States Supreme Court building at dusk in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "published_at": now,
        "body": scotus_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The DOJ Plans 250 Denaturalization Cases by October. Indian Americans Are in the Crosshairs",
        "subheadline": "Civil citizenship-stripping filings have jumped from single digits a year to a planned 250-plus — and the first Indian cases are already landing in court.",
        "slug": make_slug("doj-denaturalization-250-cases-citizenship-stripping-indian-americans"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are among the largest naturalized populations in the US and follow a decades-long, document-heavy path to citizenship — a surge in civil denaturalization filings raises the stakes on every sworn immigration form ever submitted, even those filed long ago.",
        "tags": ["denaturalization", "citizenship", "uscis", "doj", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CNN", "url": "https://www.cnn.com/2026/06/18/politics/denaturalization-cases-trump-administration"},
            {"name": "Statesman Journal", "url": "https://www.statesmanjournal.com/story/news/2026/06/16/federal-government-seeks-to-strip-citizenship-from-oregon-immigrant/"},
            {"name": "TRAC, Syracuse University", "url": "https://trac.syr.edu/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Citizenship_naturalization_ceremony_140703-N-WF272-030.jpg/1280px-Citizenship_naturalization_ceremony_140703-N-WF272-030.jpg",
        "image_caption": "New citizens take the Oath of Allegiance at a United States naturalization ceremony.",
        "image_attribution": "Wikimedia Commons",
        "published_at": now,
        "body": denat_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']} — {wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
