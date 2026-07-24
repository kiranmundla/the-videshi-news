#!/usr/bin/env python3
import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ---- env ----
for cand in [Path.home()/".env.supabase", Path.home()/"workspace"/".env.supabase"]:
    if cand.exists():
        for line in cand.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break

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

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_image_to_supabase(jpeg_bytes, filename):
    r = requests.post(
        f"{SB_URL}/storage/v1/object/article-images/{filename}",
        headers={
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        },
        data=jpeg_bytes,
        timeout=60,
    )
    if r.status_code not in (200, 201):
        print(f"    WARN upload failed {r.status_code}: {r.text[:200]}")
        return None
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"

def host_image(src_url, article_id):
    """Download Pexels image, compress, upload to Supabase. Falls back to src_url."""
    try:
        resp = requests.get(src_url, timeout=60)
        if resp.status_code == 200 and len(resp.content) > 5000:
            jpeg = compress_image(resp.content)
            public = upload_image_to_supabase(jpeg, f"{article_id}.jpg")
            if public:
                print(f"    hosted -> {public}")
                return public
    except Exception as e:
        print(f"    WARN host_image error: {e}")
    print(f"    falling back to source url")
    return src_url

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ---------------------------------------------------------------------------
# ARTICLE 1 — The 200,000 who paid $100,000 (Mullin Senate testimony)
# ---------------------------------------------------------------------------
body1 = """When the Trump administration slapped a $100,000 charge on new H-1B petitions last autumn, the conventional wisdom in Indian tech circles was that the program was, for all practical purposes, finished. No employer, the reasoning went, would pay six figures on top of salary, legal fees and relocation just to import a coder. The number that Homeland Security Secretary Markwayne Mullin gave a Senate panel this month suggests the conventional wisdom was wrong — and the truth is, in its way, more unsettling.

Testifying before the Senate Appropriations Subcommittee on June 2, Mullin disclosed that of roughly 286,000 H-1B applications received so far in fiscal 2026, **more than 200,000 paid the $100,000 fee**. They did so, he explained, because it buys speed: a petition that carries the charge is processed in about 15 days, against the roughly seven and a half months an ordinary application now takes.

## What the number actually says

Strip away the politics and a blunt market signal remains. Roughly seven in ten employers confronted with a $100,000 toll chose to pay it rather than wait, walk away, or look elsewhere. That is not the behaviour of a program in collapse. It is the behaviour of one whose users — overwhelmingly the large technology firms and staffing companies that sponsor Indian talent — have concluded the worker is worth the premium and the delay is the real enemy.

For the Indian diaspora, which receives close to three-quarters of all H-1B visas, this cuts two ways. The reassuring reading is that demand for Indian engineers, data scientists and specialists has proved sticky enough to survive a price shock that was designed to kill it. The worrying reading is that the H-1B is quietly being rationed by wealth. A charge of this size is trivial for a trillion-dollar platform company and ruinous for a startup, a university spin-out or a small consultancy — precisely the employers where many first-generation Indian arrivals once got their start.

## The rural-doctor problem

The hearing exposed the fee's collateral damage in an unexpected quarter. Senator Susan Collins of Maine pressed Mullin on a hospital in Presque Isle, a remote town in the state's north, that had been forced to pay the $100,000 to recruit a surgeon from overseas. There is, she argued, "a huge difference between bringing in a computer expert from another country to work in wealthy California and Silicon Valley versus a much-needed surgeon to work at a rural hospital in northern Maine."

That distinction matters enormously to Indian-American medicine. Indian-trained physicians are a backbone of care in underserved and rural America, and many enter precisely through the H-1B route after residency. A flat six-figure charge lands hardest on the cash-strapped rural and community hospitals that depend on them, not on the deep-pocketed tech giants the fee was ostensibly aimed at. Senator Lisa Murkowski raised a parallel worry about teacher shortages in rural Alaska.

Mullin signalled he was open to carving out flexibility — examining "case-by-case" relief where a community can show no domestic professional is available. That is a long way from a formal exemption, but it is the first acknowledgment from the department that the fee is catching the wrong people.

## What it means for the diaspora

For Indian families weighing an American move, the testimony reframes the calculation. The $100,000 is not, in practice, a wall; it is a tollbooth, and the toll is being paid. But who can afford the toll increasingly determines who gets in. The likely effect is a tilt in the Indian H-1B pipeline away from smaller employers and early-career hires and toward established workers at well-capitalised firms — a narrower, wealthier, more corporate gate than the one previous generations passed through.

The fee also remains under legal challenge, with a federal court having questioned its lawfulness even as litigation continues, so its long-term survival is not assured. For now, though, the practical advice for Indian professionals and the employers courting them is unsentimental: the route is open, the price is real, and speed has become something money can buy. The 200,000 who paid have already made their choice."""

# ---------------------------------------------------------------------------
# ARTICLE 2 — Dropbox / interview waiver eliminated for work-visa holders
# ---------------------------------------------------------------------------
body2 = """For more than a decade, the "dropbox" was the quiet mercy of the Indian visa experience. A worker renewing an H-1B, a student returning to an F-1, a spouse on an H-4 — if they qualified, they could submit their passport and paperwork at a designated centre and skip the in-person interview entirely. No dawn queue outside the consulate, no scramble for a scarce appointment slot, no day of leave burned. That mercy has now been withdrawn, and most of the diaspora has yet to absorb how completely.

Under State Department changes phased in from September 2, 2025 and consolidated by guidance effective October 1, the interview-waiver program has been narrowed to a sliver of applicants. For H-1B, L-1, O-1, E-3 and the F-1, J-1 and M-1 student categories — and their H-4 and L-2 dependents — **the dropbox no longer exists**. It does not matter whether the visa is still valid, recently expired, or was issued at the very consulate where the applicant is now applying. Everyone in these categories must now sit for an in-person interview.

## The age exemptions are gone too

The change that will surprise families most is the elimination of the long-standing age-based waivers. For years, children under 14 and applicants over 79 could bypass the interview as a matter of course. No longer. A toddler on an H-4 dependent visa and an elderly parent visiting on a renewed visa must now appear before a consular officer like everyone else — at posts where appointments are already booked months out.

What survives is a short list: diplomatic and official-category visas, a newly added carve-out for H-2A agricultural-worker renewals, and certain B-1/B-2 tourist and business renewals filed within 12 months of expiry by applicants who were over 18 when last issued and have never been refused. For the working diaspora, almost none of this applies.

## Why it bites in India specifically

India is where the dropbox did its heaviest lifting, and so India is where its removal hurts most. The country runs one of the largest US visa operations in the world, and consular wait times at posts such as Chennai, Hyderabad, Mumbai and New Delhi were already strained. Folding hundreds of thousands of routine renewals — people who under the old rules would never have needed a slot — back into the in-person queue is the bureaucratic equivalent of closing every express lane on a motorway at rush hour.

The procedural burden has grown as well. Applicants now navigate a two-step process: a biometrics appointment at an Offsite Facilitation Centre, then a full interview at the embassy or consulate. They are advised to arrive armed with employer letters, recent pay slips, client contracts and, for students, fresh I-20s — and to brace for the possibility of a 221(g) administrative hold that can add weeks. A routine renewal has become an event to plan a trip around.

## The compounding squeeze

For Indian H-1B workers, the timing is cruel. The dropbox is disappearing just as a separate domestic visa-renewal pilot — the program that would let some renew on US soil without flying home at all — remains months away and narrowly scoped. Until that arrives at scale, the only path to a new stamp runs through an Indian consulate, in person, in a queue that just got dramatically longer.

The practical consequences are immediate. A worker whose visa lapses while abroad can be stranded for weeks waiting on an interview, unable to return to a US job. Families planning summer trips to India face the real risk that a parent or child cannot secure a timely appointment for re-entry. Employers are being urged to plan travel far earlier, standardise their support letters, and build in buffers that did not used to be necessary.

The State Department frames the reset as a return to rigorous in-person screening to tighten identity and security checks. Whatever its merits on those grounds, the cost is being borne disproportionately by the very population that used the dropbox most heavily and most innocently — Indian professionals and their families, for whom a quick passport drop-off has turned back into a consular ordeal."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The $100,000 Toll Most Employers Paid Anyway: What Mullin\u2019s Numbers Reveal About the H-1B",
        "subheadline": "DHS told the Senate that more than 200,000 of fiscal 2026\u2019s 286,000 H-1B applicants paid the six-figure fee for faster processing \u2014 a sign the program isn\u2019t dying, but is being rationed by wealth.",
        "slug": make_slug("h1b-100k-fee-200000-paid-mullin-senate-testimony-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians receive close to three-quarters of all H-1B visas, so the revelation that 70% of applicants paid the $100,000 fee \u2014 and that it lands hardest on rural hospitals hiring Indian-trained doctors and on smaller employers \u2014 reshapes who from India can realistically reach America.",
        "tags": ["h1b", "h1b-fee", "uscis", "dhs", "mullin", "immigration", "indian-professionals"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine \u2014 Over 2 lakh applicants paid $100,000 for H-1B visas, says DHS Secretary Mullin", "url": "https://www.thehindubusinessline.com/news/over-2-lakh-applicants-paid-for-faster-h-1b-visa-processing-in-fy2026-dhs-says/article69649000.ece"},
            {"name": "American Bazaar \u2014 Over 200,000 H-1B applicants paid for fast-track processing in FY 2026", "url": "https://www.americanbazaaronline.com/2026/06/03/over-200000-h-1b-applicants-paid-for-fast-track-processing-in-fy-2026/"},
            {"name": "Bloomberg Law \u2014 Homeland\u2019s Mullin Signals Flexibility on $100,000 H-1B Visa Fees", "url": "https://news.bloomberglaw.com/daily-labor-report/homelands-mullin-signals-flexibility-on-100-000-h-1b-visa-fees"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_src": "https://images.pexels.com/photos/11624907/pexels-photo-11624907.jpeg?auto=compress&cs=tinysrgb&w=1400",
        "image_caption": "Stacks of US one-hundred-dollar bills \u2014 the H-1B premium fee now totals $100,000 per petition",
        "image_attribution": "Pexels",
        "body": body1,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Dropbox Is Closed: US Visa Renewals for Indians Now Mean an In-Person Interview \u2014 No Exceptions",
        "subheadline": "The interview-waiver route that let H-1B, student and dependent applicants skip the consulate is gone, and so are the under-14 and over-79 age waivers \u2014 forcing the entire diaspora back into India\u2019s already-jammed appointment queues.",
        "slug": make_slug("us-visa-dropbox-interview-waiver-eliminated-h1b-students-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India ran the world\u2019s heaviest dropbox volume, so ending interview waivers for H-1B, L-1, F-1 and dependent categories \u2014 plus the age exemptions for children and the elderly \u2014 throws hundreds of thousands of routine Indian renewals back into months-long consular queues.",
        "tags": ["visa-interview", "dropbox", "interview-waiver", "h1b", "f1-students", "h4", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge \u2014 H-1B Dropbox Eligibility Changes 2026: Everything You Need to Know", "url": "https://www.visaverge.com/news/h-1b-dropbox-eligibility-changes-2026/"},
            {"name": "Capitol Immigration Law Group \u2014 The Visa Interview Waiver (Dropbox) Process Drastically Narrowed", "url": "https://www.cilawgroup.com/news/the-visa-interview-waiver-dropbox-process-drastically-narrowed/"},
            {"name": "Murthy Law Firm \u2014 State Department Eliminating Most Dropbox Appointments", "url": "https://www.murthy.com/2025/07/28/state-department-eliminating-most-dropbox-appointments/"}
        ]),
        "score_total": 83,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_src": "https://images.pexels.com/photos/33500646/pexels-photo-33500646.jpeg?auto=compress&cs=tinysrgb&w=1400",
        "image_caption": "A United States diplomatic seal marks a US consular post \u2014 in-person interviews are now required for most visa renewals",
        "image_attribution": "Pexels",
        "body": body2,
    },
]

# word-count sanity
for a in articles:
    wc = len(a["body"].split())
    print(f"  [{wc} words] {a['headline'][:60]}")
print("---")

ok = 0
for art in articles:
    # host the image, then drop the helper-only key
    src = art.pop("image_src")
    art["image_url"] = host_image(src, art["id"])
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
        ok += 1
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")
print(f"\nInserted {ok}/{len(articles)} articles.")
