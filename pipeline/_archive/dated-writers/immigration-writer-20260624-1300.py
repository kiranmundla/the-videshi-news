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
        "headline": "Washington Just Opened a New Front in the Asylum Crackdown: Fining the Lawyers",
        "subheadline": "DHS has, for the first time, moved to fine an immigration attorney $250,000 over allegedly copy-paste asylum claims filed for Indian nationals. The chill will reach far beyond one lawyer.",
        "slug": make_slug("ice-dhs-fine-immigration-attorney-asylum-indian-nationals-doddamani"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals are the named subjects of the first-ever DHS attorney fine over asylum filings, and the chilling effect will ripple through the desi-heavy immigration bar that many on the H-1B-to-green-card path quietly rely on.",
        "tags": ["asylum", "ice", "dhs", "immigration-court", "fraud", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fox News", "url": "https://www.foxnews.com/politics/ice-opens-up-new-front-war-fraud-new-first-of-its-kind-policy-on-notice"},
            {"name": "ABC News / Seacoast", "url": "https://seacoastoldies.com/ice-fining-immigration-attorney-for-alleged-false-asylum-claims-a-first-for-the-agency/"}
        ]),
        "score_total": 82,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/6077447/pexels-photo-6077447.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A judge signs documents at a courtroom desk, representing immigration enforcement proceedings",
        "image_attribution": "Pexels",
        "published_at": now,
        "body": """The Trump administration has spent the better part of a year aiming its immigration enforcement machinery at employers, universities and visa holders. This week it pointed the gun somewhere new: at the lawyers.

On Tuesday, Homeland Security Investigations filed five notices of intent to fine attorney Vinod Doddamani, accusing him of submitting 64 fraudulent documents across 32 immigration cases. The proposed penalty is roughly a quarter of a million dollars. It is, by the government's own account, the first time the agency has ever sought to fine an attorney for the asylum claims he filed. The subjects of those claims, DHS noted pointedly, were "primarily Indian nationals."

### What DHS is alleging

According to the agency, Doddamani runs a nationwide practice built largely on asylum applications for Indian immigrants in immigration court. The filings, DHS says, were "identical or nearly identical in language and substance," sharing the same factual narrative and the same described persecution from one client to the next. In the government's telling, that template is the tell — a sign the stories were manufactured rather than lived.

Doddamani has not been criminally charged, and a notice of intent to fine is an opening salvo, not a verdict. His attorney has been contacted for comment and the case will play out through DHS's administrative process. But the legal theory underneath it is what matters for the diaspora, and it is new.

The action traces back to a memo issued last month by DHS General Counsel James Percival, who directed ICE lawyers to pursue penalties against attorneys filing false asylum claims in court. "Fraudulent asylum claims threaten the safety of Americans by overwhelming our burdened immigration system and delaying the removal of dangerous criminal aliens," Percival said, framing the fine as a warning shot. "Your days of abusing and defrauding our immigration system are over." On X, his message was blunter: fraudsters are "on notice."

### Why Indian Americans should pay attention

It would be easy to read this as a story about one allegedly bad actor. It is not, and the diaspora should resist that comfort.

The first reason is who is in the frame. Indian nationals are not incidental here — they are the named beneficiaries of the filings the government is calling fraudulent. That places the desi community squarely at the center of a precedent-setting enforcement action, and precedents have a way of being cited again.

The second reason is the chilling effect, which is the real point of a first-of-its-kind fine. The immigration bar that serves Indian families is large, and it does far more than asylum work — it shepherds H-1B extensions, green card adjustments, H-4 EADs and naturalization paperwork. When the government signals it will personally fine lawyers, the rational response across that bar is defensiveness: more caution, more screening of clients, higher fees to price in the new liability, and a reluctance to touch anything that smells like risk. Honest applicants with genuine claims can find themselves without representation, or paying a premium for it, simply because the legal market has repriced danger.

The third reason is the blurred line between fraud and aggressive lawyering. Template language and recycled country-conditions narratives are common in asylum practice, not necessarily because the claims are fake but because the persecution patterns in a given region genuinely rhyme. By treating similarity itself as evidence of fraud, the government sets a standard that competent, ethical attorneys may struggle to distinguish from their everyday work. That ambiguity is precisely what makes lawyers nervous.

### The bigger pattern

This fits a now-familiar template from the past year: ICE's claims of "uncontrolled" fraud involving thousands of foreign students and "phantom employees," the busts over fake degree certificates traced to Indian institutions, and the broader social-media vetting expansion. Each move widens the aperture of who can be held responsible — from the applicant, to the employer, to the school, and now to the attorney.

For Indian families weighing an asylum claim, the calculus has shifted. A weak or exaggerated case was always a gamble; now it carries the added risk of detonating your lawyer's livelihood, and of being held up as the next example. For the much larger group of Indians on employment-based paths, the immediate effect is subtler but real: the legal help they depend on just got more expensive and more skittish. In an immigration system where good counsel is often the difference between staying and leaving, that is not a small thing.

**Sources:** Fox News; ABC News."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Hundreds of Doctors Are Stuck at the Border of a July 30 Deadline. Many Are Indian",
        "subheadline": "A quiet logjam in the J-1 waiver program, layered on top of the $100,000 H-1B fee, threatens to keep international physicians — a large share of them Indian — out of the rural American hospitals that depend on them.",
        "slug": make_slug("j1-waiver-physician-cliff-july-30-h1b-fee-indian-doctors-rural"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian-trained physicians are a backbone of America's rural and safety-net hospitals, and a July 30 processing cliff plus the $100,000 H-1B fee could strand hundreds of them — and the patients who rely on them.",
        "tags": ["j1-waiver", "h1b", "physicians", "img", "rural-healthcare", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Medscape", "url": "https://www.medscape.com/viewarticle/delays-visa-program-threaten-hundreds-doctors"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/aapi-applauds-court-ruling-blocking-100000-h-1b-physician-visa-requirement/"},
            {"name": "AAMC", "url": "https://www.aamc.org/news/hospitals-and-health-systems-depend-h-1b-visa-sponsored-physicians-so-what-happens-now"}
        ]),
        "score_total": 78,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/6129450/pexels-photo-6129450.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Doctors and nurses interacting in a hospital hallway",
        "image_attribution": "Pexels",
        "published_at": now,
        "body": """The American healthcare system has a dependency it rarely advertises: in some rural counties, one in four, one in three, even one in two doctors trained abroad. A large share of them came from India. And right now, hundreds of those physicians are caught in a bureaucratic cliff that could keep them out of the hospitals waiting for them.

### The deadline almost nobody is talking about

The pressure point is the J-1 waiver, the program that lets foreign physicians skip the requirement to return home for two years after their U.S. medical training — provided they agree to serve in a designated shortage area. It is the on-ramp through which thousands of international doctors reach underserved America before transitioning to H-1B status.

This year, that on-ramp is jammed. Physicians and immigration lawyers say the Department of Health and Human Services has slow-walked clinical J-1 waiver applications, and the consequences crystallize on July 30. Cases that don't advance to U.S. Citizenship and Immigration Services by that date risk falling out of sequence — and for affected doctors who need to re-enter the country, their employers would then face the new $100,000 H-1B fee.

"That's the cliff that this train is headed for," Charles Wintersteen, a Chicago-based health-workforce immigration attorney, told Medscape. HHS has not explained the delays or said how many applications are pending; a spokesperson said only that the department is "working diligently" and "implementing key process improvements."

The frustration in the medical bar is sharp. "Why would HHS want to take a program that is working — a program that places hundreds of U.S.-trained international physicians in highly underserved parts of the country every year — and slow-walk it into nonexistence?" asked Jennifer Minear, a Virginia health-workforce immigration lawyer. "How does that serve the public health? It is baffling."

### A reprieve on one front, a fee that still looms

There is one piece of good news. The proposed $100,000 charge as applied to physician visas was recently blocked in court, a ruling the American Association of Physicians of Indian Origin (AAPI) cheered. "This ruling restores fairness and stability to a system that thousands of international physicians depend upon," said AAPI President Dr. Amit Chakrabarty. "This is not a political victory — it is a healthcare victory."

But the relief is fragile. The underlying $100,000 fee has been a legal seesaw — struck down in Boston, temporarily reinstated on appeal, and now winding through multiple circuits with no settled outcome. Hospitals cannot plan around a number that changes with each docket entry, and several have already frozen physician recruitment rather than gamble on a six-figure liability that may or may not survive.

### Why this lands hard on the diaspora

For Indian Americans, this is not abstract policy — it is family, and it is access to care.

Indian-origin physicians are woven into the American medical story. International medical graduates make up roughly a quarter of practicing U.S. doctors, and they are concentrated exactly where the system is thinnest: a 2025 study found H-1B physicians account for nearly double the share of the workforce in rural counties versus urban ones, and they are heavily over-represented in the highest-poverty counties. AMA President Dr. Bobby Mukkamala — whose own radiologist father and pediatrician mother emigrated from India to Flint, Michigan, in 1970 — has warned that the new costs would gut hospitals like his.

The immediate human stakes fall on the doctors themselves, many of them Indian nationals who completed U.S. residencies, signed on to serve in shortage areas, and now sit in limbo as a deadline approaches that nobody at HHS will explain. A psychiatrist caught in the backlog described the dread of a career frozen by a missing approval.

But the second-order effect reaches every American who lives near one of these hospitals. When an Indian cardiologist can't reach the 86-bed rural hospital that recruited her, the vacancy doesn't get filled by a domestic graduate — it simply stays open. Longer waits, care farther from home, and in some towns no specialist at all. For a diaspora that has spent decades staffing the wards of small-town America, the July 30 cliff is a reminder of how quietly essential — and how easily disrupted — that contribution has become.

**Sources:** Medscape; The Indian Eye; AAMC."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "World Cup Fever Meets a 14-Month Visa Wait. India Gets a Fast Lane — With Strings",
        "subheadline": "FIFA PASS promises World Cup ticket holders a priority B1/B2 interview, and a separate $750 pilot offers a paid fast track. For Indians staring down some of the world's longest visa queues, neither is the shortcut it sounds like.",
        "slug": make_slug("fifa-pass-world-cup-visa-india-14-month-wait-750-fast-track-b1-b2"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "With U.S. visitor-visa waits in India stretching to 14 months, NRIs hoping to bring family over for the 2026 World Cup — or for any visit — face a new menu of priority options that speed up the appointment but not the approval.",
        "tags": ["b1-b2", "visa-wait-times", "fifa-pass", "world-cup", "consulate", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "U.S. Department of State", "url": "https://travel.state.gov/content/travel/en/us-visas/tourism-visit/fifa-world-cup-26-visas-pass-faq.html"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/destinations/international/us-to-offer-faster-visa-appointments-within-10-days-for-an-additional-fee"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/fifa-pass-explained-priority-u-s-visa-for-world-cup-fans/"}
        ]),
        "score_total": 70,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Close-up of an open passport displaying travel stamps",
        "image_attribution": "Pexels",
        "published_at": now,
        "body": """The 2026 World Cup is already underway across the United States, Canada and Mexico, and with it comes a familiar diaspora ritual: trying to get the family a U.S. visa before the moment passes. For Indians, the moment is unusually cruel. Visitor-visa interview waits in India have stretched to as long as 14 months — meaning a relative who applies today might get an interview after the trophy has been lifted.

Two new fast lanes are supposed to help. Neither does quite what its branding implies.

### FIFA PASS: free, but only for the right ticket

The State Department's FIFA Priority Appointment Scheduling System — FIFA PASS — lets World Cup ticket holders jump the B1/B2 interview queue. The mechanics are straightforward: buy a ticket directly from FIFA, opt in through your FIFA.com account, fill out the DS-160, pay the standard $185 fee, and answer "Yes" when asked at scheduling whether you hold a World Cup ticket. If your details match across forms, you unlock a priority appointment.

The catch is in the eligibility. The ticket must have been purchased directly from FIFA — the robust secondary market and third-party sellers may not qualify. And the program does exactly one thing: it speeds up scheduling. "Scheduling an interview appointment via FIFA PASS does not guarantee the visa will be issued," the State Department's FAQ states flatly. Every applicant still faces full security screening and must demonstrate genuine visitor intent and ties to home. The priority lane gets you the appointment; your preparation gets you the visa.

There is also a structural cost worth naming. Diverting consular capacity to ticket holders through July 2026 squeezes appointment availability for everyone else — the ordinary NRI family trying to visit for a wedding or a birth, with no match ticket to flash.

### The $750 fast track: a different door, a different crowd

Separately, the U.S. is launching a paid expedited pilot from July 1 to December 31, 2026: eligible B1/B2 applicants can pay $750 on top of the $185 fee to secure an interview within 10 business days. That is nearly four times the standard visa cost for the privilege of a faster slot — and, again, only a faster slot. "Background checks, administrative reviews, and final visa decisions will continue to follow the same processes and timelines as before," one summary of the pilot noted.

Crucially, the list of participating embassies and consulates has not been announced, so whether India — the country that arguably needs it most — will be included remains unknown. And the pilot is aimed at tourists and business visitors, not at H-1B or other work-visa applicants stuck in their own, separate consular bottleneck.

### What it means for Indians

Strip away the branding and the picture is clarifying. For a diaspora family with a relative holding a genuine FIFA ticket, FIFA PASS is a real and free advantage — opt in immediately, because the value of a priority slot rises every day the queue grows. For everyone else, the $750 pilot may eventually offer a paid escape from the 14-month wait, but only if India makes the list, only for visitor visas, and only for those willing to pay a steep premium for speed.

What none of this changes is the fundamental bottleneck. Both programs accelerate the calendar, not the decision. The 14-month wait is a symptom of a consular system in India that has been straining under enhanced vetting, mass appointment cancellations and reduced drop-box eligibility for over a year. Against that backdrop, a priority appointment is genuinely useful — and also a reminder that the U.S. has chosen to manage the crush with fast lanes for some rather than shorter lines for all.

For NRIs planning to bring parents over for a match, or simply for a long-overdue visit, the advice is unglamorous but firm: start now, treat any priority option as a scheduling tool rather than a guarantee, and prepare for the interview as if the fast lane counted for nothing. Because at the consular window, it does.

**Sources:** U.S. Department of State; Outlook Traveller; VisaVerge."""
    }
]

# word-count sanity check
for art in articles:
    wc = len(re.sub(r'[#*>`\[\]()]', ' ', art['body']).split())
    print(f"   ~{wc} words | {art['headline'][:50]}")

print("--- inserting ---")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
