#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-01 03:00 UTC run"""
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

import urllib.parse

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def validate_image(url):
    """Check image URL returns HTTP 200 with image content type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {url[:60]}... ({cl} bytes)")
            return True
        else:
            print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
            return False
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
        return False

# ──────────────────────────────────────────────
# Article 1: Meta MCI Employee Tracking
# Beat: Top Employer of Indian Tech Talent + AI/Privacy
# ──────────────────────────────────────────────

art1_id = str(uuid.uuid4())

# Image: Zuckerberg from Wikipedia (story is about his AI agents vision)
art1_img = fetch_wikipedia_person_image("Mark Zuckerberg")
if art1_img and not validate_image(art1_img):
    art1_img = None
if not art1_img:
    art1_img = "https://images.pexels.com/photos/60504/security-protection-anti-virus-software-60504.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

art1_body = """Meta is tracking every mouse click, keystroke, and menu navigation of its US-based employees. If you work at the company's Menlo Park headquarters — or remotely from your apartment in Sunnyvale — your employer now knows how you use your computer, down to the scroll wheel.

The programme is called the **Model Capability Initiative**, or MCI. According to internal documents reported by Reuters, the tool captures data from more than 200 applications and websites that employees interact with on company-managed devices. The stated purpose: train AI agents that can autonomously perform the kind of everyday software tasks that human workers currently handle.

In a statement, Meta spokesperson Dave Arnold said MCI focuses on "how people interact with computers, not the content on their screens." The company maintained that the tool is deployed only on US employees' devices and that safeguards protect sensitive information.

Employees are not reassured.

## The Bandwidth Problem — and the Bigger One

In the weeks since MCI's rollout, employees have reported that the tool consumes so much data that it has been burning through their home internet quotas — in some cases, an entire month's allocation in days, according to internal posts seen by Reuters. More than 500 employees have pushed back, according to reporting by Memeburn.

But the bandwidth complaints are a sideshow. The real issue is scope. Meta has acknowledged in internal Q&A documents that the tool captures the contents of emails and direct messages sent to US-based employees — regardless of where the sender is located. If a colleague in Dublin sends a message to someone in Mountain View, and that Mountain View employee has MCI enabled, the contents are captured.

That admission has put Meta on a collision course with Europe's General Data Protection Regulation. Privacy advocates argue that workplace communications cannot simply be repurposed for AI model training without a valid legal basis — and GDPR's purpose-limitation principle is explicit about this.

## Why Indian Tech Workers Should Pay Attention

Meta employs tens of thousands of Indian-origin workers across its US operations, many on H-1B visas. These employees now face an uncomfortable calculation: their daily work is being harvested to train AI agents designed to automate tasks like theirs, and they have limited ability to object.

An American citizen who dislikes the arrangement can quit and find another job. An H-1B holder who leaves has 60 days to secure a new sponsor or leave the country. With 92,000 tech layoffs already recorded in 2026 and hiring freezes at multiple major companies, that 60-day window is less a safety net and more a tightrope.

The dynamic is particularly pointed at Meta, which has already cut nearly 8,000 jobs this year while simultaneously pouring more than $115 billion into AI infrastructure. The company is, in effect, asking the employees it hasn't yet laid off to generate the training data for the systems that could make their roles redundant.

## The Precedent Problem

Meta is not the first company to monitor employee behaviour — corporate surveillance tools have existed for years. But MCI represents something qualitatively different: using workplace activity not for performance management, but as raw material for AI training. The distinction matters because it transforms every employee into an unpaid data contributor to Meta's most strategically important programme.

If MCI succeeds, other Big Tech companies will follow. Google, Amazon, and Microsoft all employ vast numbers of Indian-origin engineers, and each has its own AI agent programmes in development. The question of whether your employer can turn your daily work into AI training data — without meaningful consent, without additional compensation, and without the ability to opt out if your immigration status depends on your job — is about to become central to the tech industry's next chapter.

For now, Meta's position is that this is simply how AI models learn. For the tens of thousands of Indian workers whose clicks are being recorded, the learning curve is rather different."""

art1 = {
    "id": art1_id,
    "headline": "Meta Is Recording Every Click Its Employees Make. Indian H-1B Workers Can't Afford to Object.",
    "subheadline": "The company's Model Capability Initiative captures mouse movements, keystrokes, and messages across 200+ apps to train AI agents — while tens of thousands of Indian-origin workers on visas have no realistic way to push back.",
    "slug": make_slug("meta-mci-employee-tracking-ai-h1b-workers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Tens of thousands of Indian-origin workers at Meta are on H-1B visas, meaning they cannot easily leave or object to workplace surveillance programmes like MCI. Their daily work is being harvested to train AI agents that could eventually automate their roles — while a 60-day grace period and frozen hiring market make the exit option nearly impossible.",
    "tags": ["meta", "ai", "h-1b", "workplace-surveillance", "privacy", "gdpr", "silicon-valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-tool-track-employee-mouse-clicks-collision-course-with-eu-privacy-rules-2026-05-29/"},
        {"name": "Engadget", "url": "https://www.engadget.com/big-tech/metas-employee-mouse-tracking-program-could-reportedly-violate-eu-privacy-laws-131507569.html"},
        {"name": "Memeburn", "url": "https://memeburn.com/2026/05/meta-tracks-keystrokes-ai-2026/"},
        {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/tech-news/metas-internal-monitoring-tool-raises-gdpr-concerns-across-european-privacy-regulators"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": art1_img,
    "is_editorial": False,
    "body": art1_body
}

# ──────────────────────────────────────────────
# Article 2: 92K Tech Layoffs + Apple Stability
# Beat: Top Employers / H-1B & Tech Immigration
# ──────────────────────────────────────────────

art2_id = str(uuid.uuid4())

# Image: Tim Cook from Wikipedia (Apple is the focus)
art2_img = fetch_wikipedia_person_image("Tim Cook")
if art2_img and not validate_image(art2_img):
    art2_img = None
if not art2_img:
    art2_img = "https://images.pexels.com/photos/5499551/pexels-photo-5499551.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

art2_body = """More than 92,000 technology workers have lost their jobs in 2026 so far. Meta has cut nearly 8,000. Microsoft, Amazon, and Salesforce have each conducted rounds of restructuring. The stated reason across the board: redirect resources toward artificial intelligence. The unstated reason: the people who built the last era of products are expensive, and AI infrastructure is more expensive still.

Through all of it, Apple has barely touched its workforce.

A new analysis by LatestLY, drawing on layoff tracking data, shows that Apple has remained "largely unaffected" by the industry's restructuring wave. The reason is not luck. It is a hiring discipline that now looks prescient.

## The 20 Per Cent Rule

During the pandemic, when remote work, e-commerce, and streaming demand surged, most major tech companies hired aggressively. Meta's headcount grew by roughly 60 per cent between 2020 and 2022. Amazon added hundreds of thousands of workers. Google, Microsoft, and Salesforce all expanded rapidly to meet what they believed was permanent demand.

Apple grew by approximately 20 per cent over the same period.

That restraint has eliminated the need for the mass corrections now playing out across the industry. While competitors are firing people to fund AI data centres, Apple is funding its AI push — including a dramatic Siri overhaul powered by Google's Gemini, expected at WWDC on June 8 — from existing operations and organic attrition.

## The H-1B Arithmetic

For Indian-origin tech workers in the United States, the layoff wave carries uniquely severe consequences. Indians make up roughly three-quarters of all H-1B visa holders, and the tech sector is the programme's largest employer. Every layoff creates not just job loss but a 60-day countdown: find a new sponsor, switch to another visa category, or leave the country.

The arithmetic has worsened in 2026. In the current H-1B lottery cycle, USCIS received 343,981 eligible registrations and selected just 120,141 — a roughly 35 per cent selection rate. For workers trying to re-enter the system after a layoff, the odds are not encouraging.

Meanwhile, community discussions and recent reporting highlight a grim reality for international students on OPT: some have submitted over 1,500 job applications without a single callback. Employers face significant administrative and financial burdens when sponsoring H-1B visas, and with AI tools reducing the need for junior engineers, many have simply stopped.

## Two Models of Growth

The divergence between Apple and its peers illustrates two fundamentally different approaches to the AI transition.

The first, practised by Meta, Microsoft, and to some extent Amazon, treats AI as a crisis requiring wholesale restructuring: cut headcount in established divisions, redirect the savings to AI infrastructure, and accept the human cost as a transition expense. Meta's $115 billion AI infrastructure spend this year is being funded partly by the employees who lost their jobs.

The second, Apple's approach, treats AI as an evolution that can be absorbed within a stable organisation. By not over-hiring during the boom, Apple avoided the bust. By partnering with Google for Gemini rather than building competing foundation models in-house, the company avoided the multi-billion-dollar infrastructure arms race.

Neither model is inherently superior — Meta's bet on open-source AI may ultimately prove transformative. But for the individual worker, especially one whose ability to remain in the country depends on continuous employment, the difference is existential.

## What Comes Next

The industry shows no sign of stabilising. OpenAI's new services venture has already spooked Indian IT stocks, with the sector falling to three-year lows. Infosys CEO Salil Parekh has seen his compensation rise to $8.69 million even as the company forecasts anaemic growth of 1.5 to 3.5 per cent for fiscal 2027. The message from leadership is clear: the people at the top will be fine.

For the 92,000 who have already been let go — and the hundreds of thousands on H-1B visas wondering if they are next — Apple's quiet discipline offers a lesson that the rest of the industry may have learned too late: the best layoff strategy is to never need one."""

art2 = {
    "id": art2_id,
    "headline": "92,000 Tech Workers Have Lost Their Jobs in 2026. Apple Has Barely Touched Its Workforce.",
    "subheadline": "While Meta, Microsoft, and Amazon restructure to fund AI, Apple's disciplined pandemic-era hiring has kept its workforce intact — a distinction that matters enormously to the tens of thousands of Indian H-1B holders caught in the crossfire.",
    "slug": make_slug("92000-tech-layoffs-2026-apple-workforce-h1b"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indians hold roughly three-quarters of all H-1B visas, and tech is the programme's largest employer sector. Every layoff triggers a 60-day grace period — find a new sponsor or leave the country. With the H-1B lottery selection rate at 35% and OPT students reporting zero callbacks after 1,500+ applications, Apple's workforce stability versus competitors' mass layoffs is an existential distinction for diaspora workers.",
    "tags": ["tech-layoffs", "apple", "h-1b", "meta", "microsoft", "amazon", "hiring", "ai-restructuring"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "LatestLY", "url": "https://www.latestly.com/technology/apple-maintains-workforce-stability-as-global-tech-layoffs-top-92000-amidst-ai-spending-frenzy-report-6714297.html"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/h-1b-opt-programs-under-fire-as-job-seekers-report-zero-callbacks-on-1500-applications-2505/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/what-if-ai-boom-goes-into-reverse-2026-05-29/"},
        {"name": "Singapore Informer", "url": "https://singaporeinformer.com/meta-leadership-triggers-layoffs-h-1b-visa-holders-face-uncertain-future/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": art2_img,
    "is_editorial": False,
    "body": art2_body
}

# ──────────────────────────────────────────────
# Insert
# ──────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
