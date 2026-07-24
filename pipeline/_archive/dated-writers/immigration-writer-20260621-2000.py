#!/usr/bin/env python3
"""
Videshi Immigration Writer — June 21, 2026 (20:00 PT run)
2 NEW articles (status=review, is_editorial=False):
  1. US consulate visa appointment backlog in India (immigration)
  2. Visa-free / VOA destinations unlocked by holding a US visa or green card (travel)
Both use verified permanent Pexels hero images.
"""

import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            tmp = f"/tmp/{slug}_src"
            subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
            with open(tmp, "rb") as f:
                r_content = f.read()
            if len(r_content) < 5000:
                return None
        else:
            r_content = r.content

        from PIL import Image
        img = Image.open(io.BytesIO(r_content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()
        if len(compressed) < 5000:
            print(f"  \u26a0 Compressed too small: {len(compressed)} bytes")
            return None
        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        requests.delete(upload_url, headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY})
        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=30)
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url[:80]}...")
            return public_url
        print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
    return None


# ─── Article 1: US consulate visa appointment backlog in India ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: US visa appointment backlog in India")
    print("="*60)

    slug = "us-visa-appointment-backlog-india-consulates-work-visa-waits-20260621"
    headline = "The Hardest Part of an American Work Visa Right Now Isn't Approval \u2014 It's Getting an Appointment in India"
    subheadline = "Wait times for H and L work-visa interviews have climbed past 75 to 125 days across India's five US consulates, the old Kolkata escape valve has slammed shut, and visitor-visa slots have all but vanished in Mumbai and Delhi \u2014 leaving families to game the system or fly abroad to get stamped."

    body = """For Indian professionals with an approved American work visa in hand, the last obstacle between them and a flight to the United States is supposed to be a formality: a short interview at a US consulate to get the visa stamped into the passport. In the summer of 2026 that formality has become the bottleneck. Across India's five consular posts, the wait just to book an appointment for an H or L work visa now runs from roughly 75 days to more than 125, and the workarounds Indians have long relied on are disappearing one by one.

The squeeze matters far beyond the people standing in line. India sends more skilled workers to the United States than any other country, and the H-1B and L-1 pipelines that move engineers, managers and their families across the Pacific depend entirely on these stamping appointments. A petition approved by US Citizenship and Immigration Services means nothing until the consulate puts ink in the passport \u2014 and right now that ink is months away.

## The Numbers Behind the Wait

The State Department's own global wait-time tracker, last refreshed in mid-May, tells the story consulate by consulate, and outside trackers run by immigration law firms have logged similar figures through June. For work-visa categories, appointment waits have stretched well past two months and, at the worst-hit posts, past four. The picture for visitor visas is starker still: in Mumbai and New Delhi, the number of available B1/B2 slots has been hovering near zero, with the earliest openings pushed deep into the calendar. Chennai and Hyderabad have shown a thin trickle of slots, but nothing that resembles breathing room.

The collapse of Kolkata as a release valve is the detail that has rattled seasoned applicants most. For years, the eastern consulate was the open secret of Indian visa-hunting \u2014 a post where an appointment could sometimes be found in under two weeks while Mumbai and Delhi were booked solid. That gap has closed. Kolkata's work-visa wait has ballooned to roughly 126 days, putting it in line with everywhere else and erasing the one reliable shortcut in the system.

## Why the System Is Jammed

The basic problem is supply and demand. Demand for US visas from India has surged with the post-pandemic travel rebound and the steady growth of Indian hiring by American employers, but consular capacity has not kept pace. There has been no matching expansion of consular staff or interview windows to absorb the crush, so each newly released batch of appointments is gone within minutes, and applicants describe refreshing the booking portal for days.

The interview-waiver route \u2014 known to most applicants as "Dropbox" \u2014 was meant to relieve exactly this pressure by letting qualifying renewals skip the in-person interview entirely. But the government has tightened and reorganised it. Since early 2024, Dropbox processing for India was consolidated, with New Delhi handling a large share of the submissions, and the eligibility window for who qualifies has narrowed. Applicants can still submit documents free of charge at the main visa application centres, while a network of additional drop-off centres in cities such as Ahmedabad, Bangalore, Chandigarh, Cochin, Jalandhar and Pune accept paperwork for a convenience fee of around 1,200 rupees. Useful as it is, Dropbox only helps those who qualify for a waiver; first-time applicants and many others still need a scarce interview slot.

## The Workarounds, and Their Limits

With domestic appointments backed up for months, some applicants are turning to the "third-country national" option \u2014 booking an interview at a US consulate outside India, in places like Bangkok, Dubai or various European capitals, where wait times may be shorter. It can work, but it is not a free pass: it means paying for international travel, gambling on a foreign post's own appointment availability, and accepting the risk that an officer abroad may be less familiar with an applicant's profile or may decline to process a case better suited to the home country.

Families, meanwhile, are improvising. Parents booking visitor visas to attend a US graduation or to help with a new grandchild are finding the dates they need simply do not exist, and are either deferring trips or chasing emergency-appointment requests that are granted sparingly and case by case.

## Why It Matters for the Diaspora

For the Indian diaspora, the appointment backlog is a reminder that the hardest mile of the American journey is often the most mundane one. The community has spent years tracking lottery odds, wage rules and fee increases \u2014 the dramatic policy fights that dominate the headlines. But for the family waiting to reunite, the new hire whose start date keeps slipping, or the worker whose visa lapsed during a trip home, the binding constraint in mid-2026 is something far more prosaic: a calendar with no open dates. Until consular capacity catches up with Indian demand, the smartest move is to plan months ahead, keep checking for newly released slots, and treat that stamping appointment not as a formality but as the real finish line it has become."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    img_src = "https://images.pexels.com/photos/7235804/pexels-photo-7235804.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    final_img_url = download_and_compress(img_src, slug)
    img_caption = "A passport with a visa stamp; US work-visa interview waits now run past 75 to 125 days across India's consulates"
    img_attribution = "Photo by Nataliya Vaitkevich on Pexels"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "immigration",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "US Department of State \u2014 Global Visa Wait Times tool (visa appointment wait times by post, last updated 18-MAY-2026): interview wait times for visitor (B1/B2) and other nonimmigrant categories at Chennai, Hyderabad, Kolkata, Mumbai and New Delhi",
            "Fragomen \u2014 India: US visa appointment availability and processing updates: H/L work-visa appointment waits across Indian consulates; Dropbox (interview waiver) consolidation with New Delhi handling a large share since 2024; narrowed interview-waiver eligibility",
            "VisaVerge \u2014 reporting on US visa appointment backlogs in India: near-zero B1/B2 availability in Mumbai and New Delhi; Kolkata's work-visa wait rising to roughly 126 days, erasing its former role as a low-wait post; thin availability at Chennai and Hyderabad",
            "Khandelwal Law / India-based immigration advisories \u2014 Dropbox document drop-off network and fees: free submission at main visa application centres and an approximately Rs 1,200 convenience fee at additional drop-off centres in Ahmedabad, Bangalore, Chandigarh, Cochin, Jalandhar and Pune; third-country national (TCN) appointments as an alternative route"
        ]),
        "diaspora_angle": "India sends more skilled workers to the US than any other country, and every H-1B or L-1 hinges on a consular stamping appointment that now sits 75 to 125-plus days out; with Mumbai and Delhi visitor slots near zero and the old Kolkata shortcut gone, diaspora families face deferred reunions, slipping job start dates, and the costly gamble of getting stamped in a third country.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ─── Article 2: Visa-free travel unlocked by a US visa / green card ─

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Visa-free travel with a US visa / green card")
    print("="*60)

    slug = "us-visa-green-card-visa-free-travel-destinations-indian-passport-2026-20260621"
    headline = "Your US Visa Is a Second Passport in Disguise \u2014 Here's Where It Lets Indians Travel Without Applying for a Visa"
    subheadline = "A valid US visa or green card now opens the door to more than 40 countries for Indian passport holders, from Argentina and Mexico to the Caribbean and the Gulf \u2014 and the 2026 list has quietly grown, with Argentina, France and Germany easing rules this year."

    body = """For an Indian passport holder, the hardest part of travel is rarely the flight \u2014 it is the paperwork. The Indian passport, despite recent gains, still requires a visa for most of the world's wealthier destinations, which means appointments, fees and the familiar anxiety of waiting on an embassy's decision. But there is a workaround that many in the diaspora underuse: a valid US visa or a US green card functions, in dozens of countries, as a key that unlocks visa-free or visa-on-arrival entry. For the millions of Indians who already hold an H-1B, an F-1, a B1/B2 or a green card, that piece of American documentation is quietly a second passport.

The logic is simple. Many countries reason that if the United States has already vetted a traveller thoroughly enough to issue a visa, they need not run the same checks again. So they waive their own visa requirement for Indian nationals who carry a valid US visa \u2014 and in 2026, the roster of places willing to do that has grown.

## What's New in 2026

The headline addition this year is Argentina. As of April 2026, Indian passport holders with a valid US visa \u2014 categories such as B1/B2, H-1B, O, P, E or J \u2014 or a US green card can enter Argentina without applying for a separate Argentine visa, opening up Patagonia, Buenos Aires and Iguazu to diaspora travellers who previously faced a full application. Europe has eased things too: France scrapped its airport transit visa requirement for Indian nationals in April 2026, and Germany followed in June, removing the transit-visa hurdle that used to trip up Indians connecting through Paris and Frankfurt on the way elsewhere.

## The Americas: Closer Than They Look

The Western Hemisphere is where a US visa pays off most. Mexico allows Indian passport holders with a valid US visa to enter without a Mexican visa, a long-standing rule that makes a Cancun or Mexico City trip dramatically simpler. Costa Rica and Panama both admit Indians holding a valid US visa for stays of around 30 days, putting Central America's beaches and rainforests within easy reach. Several Caribbean nations do the same or close to it \u2014 the Bahamas, Jamaica, Aruba, Curacao, the Cayman Islands, the British Virgin Islands, Antigua and St Kitts feature on the list of places that recognise US documentation to smooth entry for Indian visitors.

## The Gulf, the Middle East and Asia

For the enormous Indian community in and around the Gulf, the US-visa benefit is genuinely useful. The United Arab Emirates offers visa-on-arrival to Indian passport holders who have a valid US visa or green card, a route many use for a quick Dubai stopover. Across Asia, a US visa eases entry to a string of destinations: it can support visa-on-arrival or simplified entry in places like Qatar and helps with transit and short stays in parts of Southeast Asia. Taiwan operates an online travel authorisation for Indians who hold a valid visa from the United States and other developed countries, and several others fold a US visa into their entry criteria.

## What It Doesn't Do \u2014 and How to Use It Right

The benefit comes with fine print that trips up the unprepared. The US visa must usually be valid \u2014 not expired \u2014 and in many cases must be a multiple-entry visa; some countries additionally require that the holder has already used the US visa to enter the United States at least once. Permitted stays are typically short, often 30 to 90 days, and the rules differ country by country and change without much fanfare, as the 2026 additions show. The golden rule is to verify the current requirement with the destination's official immigration source or the airline before booking, because carriers can deny boarding if the documents do not match the rule on the day of travel.

It is also worth keeping the bigger picture in view. India's own passport has been climbing: the latest rankings credit it with visa-free or visa-on-arrival access to a growing list of countries on its own, alongside a wide network of e-visa destinations. The US-visa hack sits on top of that, extending the map further for the slice of the diaspora that holds American documentation.

## Why It Matters for the Diaspora

For Indians living, studying or working in the United States, the implication is practical and immediate: the visa already stapled into the passport is a travel asset, not just a work permit. A summer break can stretch to Buenos Aires or Cancun without a fresh embassy queue; a Gulf-based professional can detour through Dubai on a US visa; a student can plan a Costa Rica reset between semesters. In a year when getting any new visa appointment has become an exercise in patience, knowing that the US visa already in hand opens 40-plus doors is one of the rare pieces of good news on the travel front \u2014 provided the traveller reads the fine print before they fly."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    img_src = "https://images.pexels.com/photos/7010170/pexels-photo-7010170.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    final_img_url = download_and_compress(img_src, slug)
    img_caption = "A passport resting on a world map; a valid US visa unlocks visa-free or visa-on-arrival entry to 40-plus countries for Indians"
    img_attribution = "Photo by Tima Miroshnichenko on Pexels"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "travel",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Wikipedia \u2014 'Visa requirements for Indian citizens' (continuously updated): countries that waive visa or grant visa-on-arrival to Indian passport holders who hold a valid US visa or green card; Argentina visa-free for Indians with a valid US visa (B1/B2, H-1B, O, P, E, J) or US green card effective April 2026; France removed airport transit visa requirement for Indians (April 2026); Germany removed airport transit visa requirement (June 2026)",
            "Wise.com \u2014 'Countries you can visit with a US visa (for Indian passport holders)': list including Mexico, Costa Rica (30 days), Panama (30 days), UAE (visa on arrival), and Caribbean nations; conditions such as validity and multiple-entry requirements",
            "Dainik Jagran / Jagran English \u2014 roundup of countries Indians can visit using a valid US visa: Mexico, Bahamas, Costa Rica, Panama, Taiwan online authorisation, and others, with notes on stay limits",
            "PolicyBazaar \u2014 'Visa-free and visa-on-arrival countries for Indian passport holders 2026' and US-visa-based entry: fine-print conditions (valid/multiple-entry US visa, prior US entry in some cases) and reminder to confirm with official sources before travel"
        ]),
        "diaspora_angle": "Millions of diaspora Indians already hold an H-1B, F-1, B1/B2 or green card; this piece is a practical service guide showing that the US visa in their passport doubles as a travel key to 40-plus countries \u2014 with 2026 additions like Argentina and eased France/Germany transit rules \u2014 just as fresh visa appointments have become almost impossible to get.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


if __name__ == "__main__":
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    print("\n" + "="*60)
    print(f"DONE. Inserted IDs: {[i for i in ids if i]}")
    print("="*60)
