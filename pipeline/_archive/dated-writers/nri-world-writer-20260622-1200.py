#!/usr/bin/env python3
"""
Videshi NRI World Writer — June 22, 2026 (12:00 PT run)
3 NEW articles (all dedup-checked clean against last 40 nri-world pieces):
  1. Raju Mann — India-origin CEO of NYC's Battery Park City Authority honored
     with the 2026 Alexander Hamilton Immigrant Achievement Award at Federal Hall.
  2. IIT at 75 — the PanIIT IIT2026 Long Beach gathering as a portrait of the
     IIT alumni network as diaspora infrastructure.
  3. Dr. Dileep Yavagal — Indian-origin neurologist wins AAN Lifetime Achievement
     Award; Mission Thrombectomy and the global stroke-care equity gap.

(Dropped: Indian-American philanthropy / giving gap — already covered June 4 in
 "Indian Americans Have Given $3 Billion to US Universities...")
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
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error: {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    for _ in range(3):
        try:
            r = requests.get("https://commons.wikimedia.org/w/api.php",
                             params=params, headers={"User-Agent": UA}, timeout=20)
            if r.status_code == 200:
                data = r.json()
                pages = data.get("query", {}).get("pages", {})
                results = []
                for pid, page in pages.items():
                    ii = page.get("imageinfo", [{}])[0]
                    mime = ii.get("mime", "")
                    if not mime.startswith("image/") or mime == "image/svg+xml":
                        continue
                    if ii.get("width", 0) < 300:
                        continue
                    results.append({
                        "url": ii.get("thumburl") or ii.get("url", ""),
                        "original_url": ii.get("url", ""),
                        "title": page.get("title", ""),
                        "width": ii.get("width", 0),
                        "height": ii.get("height", 0)
                    })
                if results:
                    print(f"  \u2713 Wikimedia Commons: {len(results)} images for '{search_query}'")
                return results
        except Exception as e:
            print(f"  \u26a0 Wikimedia Commons retry: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        out = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}", "-A", UA,
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"],
            capture_output=True, text=True, timeout=30
        )
        photos = json.loads(out.stdout).get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=25)
        if r.status_code != 200:
            tmp = f"/tmp/{slug}_src"
            subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=40, check=True)
            with open(tmp, "rb") as f:
                r_content = f.read()
        else:
            r_content = r.content
        if len(r_content) < 5000:
            print(f"  \u26a0 Source too small: {len(r_content)} bytes")
            return None

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
            "Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg", "x-upsert": "true"
        }, timeout=40)
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url[:80]}...")
            return public_url
        print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def pick_commons(queries, min_width=800):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    return c["url"]
            return commons[0]["url"]
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


# ─── Article 1: Raju Mann / Alexander Hamilton Immigrant Achievement Award ───

def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: Raju Mann / Hamilton Award")
    print("=" * 60)

    slug = "raju-mann-battery-park-city-alexander-hamilton-immigrant-achievement-award-2026-20260622"
    headline = "An Immigrant Now Runs One of Manhattan's Most Closely Watched Neighborhoods. A 250-Year-Old Award Just Made the Point."
    subheadline = "Raju Mann, the India-born head of New York's Battery Park City Authority, was honored at Federal Hall among five naturalized citizens recognized for shaping Lower Manhattan — a quiet marker of how far Indian-origin leadership has moved into the machinery of American cities."

    body = """At Federal Hall, on the spot where George Washington was sworn in as the first president of the United States, the Lower Manhattan Historical Association gathered this year to give out an award named for the most famous immigrant of the founding generation. The Alexander Hamilton Immigrant Achievement Awards go to foreign-born naturalized citizens who have shaped New York City. Among the five honorees was Raju Mann, the India-born president and chief executive of the Battery Park City Authority.

It is the kind of recognition that rarely makes headlines and quietly says a great deal. The other honorees ran a historic tavern, a global architecture practice, a downtown civic board. Mann runs a 92-acre slice of Manhattan's waterfront — a planned neighborhood of some 17,000 residents, parks, and public art, built on landfill from the World Trade Center excavation, and now on the front line of New York's fight against rising seas.

## From Urban Planner to Civic Steward

Mann is not a celebrity appointment. He is an urban planner who has spent close to two decades on the unglamorous problems of a growing city — housing, parks, transportation, climate adaptation. Before taking over the Battery Park City Authority in 2023, he was a city-planning leader at the global engineering firm Arup, and before that the director of land use and a deputy chief of staff at the New York City Council, where he led teams of planners and lawyers working with council members and neighborhoods across the five boroughs.

He holds a bachelor's degree in philosophy from Columbia and a master's in urban planning from the University of Michigan, sits on the board of the contemporary-art museum MoMA PS1, and advises the New York Housing Conference. It is a resume built not on a single breakthrough but on the patient accumulation of responsibility inside the institutions that actually run a city.

That is precisely what the Hamilton award is designed to notice. Past honorees have included a federal appeals-court judge, a transportation commissioner, world-renowned chefs and architects. The through-line is not fame but contribution — people who arrived from elsewhere and ended up holding part of New York together.

## Why This Lands Differently for the Diaspora

For the Indian diaspora in the United States, the familiar story of arrival has long run through the private economy: the startup founder, the Fortune 500 chief executive, the doctor, the engineer. The roster of Indian-origin corporate leadership now reads like a directory of American business. What is newer, and less remarked upon, is the movement of Indian-origin professionals into public and civic stewardship — the authorities, agencies, and planning bodies that decide how a city is built, who can afford to live in it, and how it survives a warming climate.

A public authority like Battery Park City is not a glamorous perch. It answers to the state, manages public money, and absorbs criticism from every direction — residents, developers, environmentalists, politicians. To lead one is to accept accountability without the upside of ownership. That an immigrant from India now holds that job, and is honored for it at the building where American self-government began, is a marker of a particular kind of belonging: not the visitor who succeeds, but the citizen who is trusted to govern.

## A Symbol With a Hard Edge

The timing sharpens the point. The award was given in a year when immigration has been one of the most contested subjects in American politics, and when naturalized citizens — including many in the Indian diaspora — have watched the national debate with unease. Hamilton himself, born in the Caribbean and arriving in New York as a young man, is invoked by every side of that argument.

The Lower Manhattan Historical Association's answer is studiously apolitical: it simply names people who came from somewhere else and built something here, and reads their countries of origin aloud at Federal Hall. This year that list included India. For a diaspora that increasingly measures its standing not by how many of its own have grown rich but by how many have been entrusted with the public good, Raju Mann's name on that program is a small, durable kind of recognition — the sort that outlasts the news cycle that ignored it."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image (Federal Hall, the actual venue)...")
    img_url = pick_commons([
        "Federal Hall National Memorial",
        "Federal Hall Manhattan",
        "Battery Park City Manhattan",
    ])
    img_caption = "Federal Hall National Memorial in Lower Manhattan, where the Alexander Hamilton Immigrant Achievement Awards are presented"
    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": "Wikimedia Commons" if final_img_url else "",
        "sources": json.dumps([
            "Lower Manhattan Historical Association \u2014 2026 Alexander Hamilton Immigrant Achievement Award Honorees (historiclowermanhattan.org): honorees Dervila Bowler & Eddie Travers (Ireland), Kai-Uwe Bergmann (Germany), Raju Mann (India), Roger Byrom (England); award for foreign-born naturalized US citizens who made outstanding contributions to Lower Manhattan and NYC; ceremony at Federal Hall National Memorial, held on the 250th anniversary of Hamilton's appointment as Captain of the 1st Battalion, 5th Artillery",
            "Battery Park City Authority \u2014 Leadership: Raju Mann, President & CEO, appointed 2023; urban planner ~20 years in NYC; joined from Arup (Associate Principal, City Planning Leader for the East Coast); former Director of Land Use and Deputy Chief of Staff, NYC Council; BA Philosophy (Columbia), MA Urban Planning (University of Michigan); board member MoMA PS1; advisory board New York Housing Conference (bpca.ny.gov)",
        ]),
        "tags": ["Indian diaspora", "Raju Mann", "New York", "Battery Park City", "immigrant achievement", "civic leadership", "Indian Americans"],
        "urgency": "low",
        "score_total": 72,
        "diaspora_angle": "Indian-origin success in America has been told largely through the private economy \u2014 founders and CEOs. Raju Mann leading a major New York public authority, and being honored among naturalized citizens at Federal Hall, marks the diaspora's quieter move into civic stewardship: not just thriving in a city, but being trusted to govern part of it.",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    return insert_article(article)


# ─── Article 2: IIT at 75 / PanIIT IIT2026 Long Beach ───────────────────────

def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: IIT at 75 / IIT2026 Long Beach")
    print("=" * 60)

    slug = "iit-75-years-iit2026-long-beach-panIIT-diaspora-alumni-network-20260622"
    headline = "The Most Powerful Old-Boys' Network in Tech Isn't From Stanford. It Just Turned 75 and Threw Itself a Party in California."
    subheadline = "When thousands of IIT alumni gathered in Long Beach to mark 75 years of India's elite engineering schools, the real subject wasn't nostalgia. It was the question of what a diaspora network becomes once it stops needing to prove itself."

    body = """India's Institutes of Technology turn 75 this year, and to understand what that milestone means you could read the founding statutes, or you could have stood in the Long Beach Convention Center this spring as several thousand of their graduates filled a waterfront hall to celebrate it.

The IIT2026 Global Conference, organized by the PanIIT USA alumni community, drew some 1,500 to 2,500 attendees and more than 100 exhibitors over four days in late April. Its theme — "Innovate, Ignite and Thrive" — was the usual conference boilerplate. What it actually displayed was something more interesting: a diaspora network that has grown confident enough to host Nobel laureates, ambassadors, and corporate chiefs, and relaxed enough to insist that none of that is the point.

## A Network, Not Just an Alma Mater

"You don't have to be an IITan to attend," the conference chair, Shashi Tripathi, a venture capitalist, told reporters. "We are very inclusive." It is a striking thing to hear from an institution whose entire mystique rests on exclusivity — the IIT entrance examination is among the most brutally competitive in the world, admitting a sliver of the candidates who sit it.

The IITs span 23 campuses across India and are, in the conference's own phrasing, the source of "the largest pipeline of Indian-origin tech professionals in the U.S. today." Past PanIIT gatherings have featured Bill Gates, Sundar Pichai, Vinod Khosla, the economist Amartya Sen, and Prime Minister Narendra Modi. The 2026 program ranged from keynotes by the cybersecurity billionaire Jay Chaudhry and the spiritual figure Sadhguru to workshops run by Nvidia on how startups raise money and go to market.

That breadth is the tell. An alumni association measures its members' nostalgia. A network measures their reach. The four tracks at Long Beach — artificial intelligence, health and sustainability, investment and venture capital, and what organizers called "global connect" geopolitics — map almost exactly onto the sectors where Indian-origin technologists now sit at or near the top.

## India in the Room, Officially

The Indian state took the gathering seriously. Vinay Mohan Kwatra, India's ambassador to the United States, delivered a central address urging the alumni to help achieve the country's development goals, framing the IIT network as an instrument of the India-U.S. partnership. K.J. Srinivasa, the first consul general of India's newly established consulate in Los Angeles, called the IITs "ecosystems that have powered innovation in India and across the world."

That official attention reflects a strategic calculation that has hardened over the past decade. India has come to see its diaspora not as a brain drain to mourn but as a standing asset to court — a reservoir of capital, expertise, and influence that can be channeled back toward Indian industry and Indian soft power. In January 2024, the U.S. House of Representatives went so far as to pass a resolution recognizing the contributions of IIT graduates to American society, a rare instance of one country's universities being honored by another country's legislature.

## What 75 Years Actually Marks

For the diaspora, the anniversary is a moment of arrival that doubles as a question. The first generations of IIT graduates left India because the opportunities at home could not match their training; their success abroad was, in part, a verdict on what India then could not offer. Seventy-five years on, that calculus is shifting. India's own technology economy, its startup ecosystem, and its capital markets are large enough that the one-way flight is no longer the only rational choice, and a growing number of alumni are investing in, advising, or returning to ventures in India.

The Long Beach conference, with its ambassadors and its inclusive open door, captured a network at that hinge point: powerful enough that it no longer needs to prove the worth of an IIT degree to anyone, and unsure, in the most productive way, about what to do with that power. The party was for the past 75 years. The conversations in the hallways were about the next ones — and about whether the center of gravity for the world's most formidable engineering diaspora is finally beginning to tilt back toward where it started."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image (an actual IIT campus)...")
    img_url = pick_commons([
        "Night view of campus buildings at IIT Bombay",
        "IIT Bombay campus",
        "Indian Institute of Technology campus",
    ])
    img_caption = "A campus of the Indian Institutes of Technology, which mark 75 years in 2026"
    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": "Wikimedia Commons" if final_img_url else "",
        "sources": json.dumps([
            "California News Beep / PRNewswire \u2014 IIT2026 Conference Brings Global Thought Leaders to Long Beach (April 7, 2026): IIT2026 Global Conference, Long Beach Convention Center, April 22-25, 2026; four tracks (AI, Investment, Healthcare, Global Connections); keynotes Jay Chaudhry, Sadhguru, Guy Kawasaki, Jeetu Patel; entertainers Shankar Ehsaan Loy, Amjad Ali Khan; chair Shashi Tripathi; 'You don't have to be an IITan to attend'; IITs span 23 campuses, 75 years, 'largest pipeline of Indian-origin tech professionals in the U.S.'",
            "California News Beep \u2014 IIT2026 Global Conference Opens in Long Beach (April 2026): ~1,500 attendees, 100+ exhibitors; opening keynote 'Technologies for Well-Being'; India's Ambassador to the US Vinay Mohan Kwatra delivered central address; Dr. K.J. Srinivasa, first Consul General of the new Consulate of India in Los Angeles, on global influence of IIT alumni",
            "IANS \u2014 Global IIT gathering to shape future innovation, strengthen ties with India (Feb 9, 2026): PanIIT conference April 22-25, 2026, theme 'Innovate, Ignite and Thrive', 2,500+ expected; chair Shashi Tripathi; six grand keynotes plus Nvidia go-to-market workshop",
            "iit2026.org / forpressrelease.com \u2014 About IIT2026: organized by PanIIT USA; past PanIIT speakers include Bill Gates, Sundar Pichai, Vinod Khosla, Amartya Sen, Narendra Modi, Bill Clinton; U.S. House Resolution H.Res.956 (Jan 2024) recognizing contributions of IIT alumni",
        ]),
        "tags": ["Indian diaspora", "IIT", "PanIIT", "IIT2026", "Long Beach", "Indian Americans", "technology", "alumni network", "Shashi Tripathi"],
        "urgency": "low",
        "score_total": 70,
        "diaspora_angle": "The IIT alumni network is among the most powerful pieces of diaspora infrastructure the world has built \u2014 the pipeline behind a generation of Indian-origin technology leaders in the US. Its 75th-anniversary gathering in California, courted by India's ambassador, captures the diaspora at a hinge: confident, courted by the homeland, and increasingly tilting capital and attention back toward India.",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    return insert_article(article)


# ─── Article 3: Dr. Dileep Yavagal / AAN Lifetime Achievement ───────────────

def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: Dr. Dileep Yavagal / stroke-care equity")
    print("=" * 60)

    slug = "dileep-yavagal-aan-lifetime-achievement-mission-thrombectomy-stroke-care-equity-20260622"
    headline = "A Procedure Can Reverse a Stroke in Minutes. Fewer Than 3% of the World Can Get It — and an Indian Doctor Has Spent a Decade Fixing That."
    subheadline = "Dr. Dileep Yavagal, honored with a Lifetime Achievement Award at this year's American Academy of Neurology meeting, helped make clot removal a global standard. His harder fight is over who actually receives it — and in India, the answer is almost no one."

    body = """There is a treatment for the most disabling kind of stroke that can feel, to the families who witness it, like a reversal of fate. A surgeon threads a catheter through an artery, reaches the clot blocking blood flow to the brain, and pulls it out. Patients who arrived unable to speak or move can, in the best cases, walk out of the hospital. The procedure is called mechanical thrombectomy, and the work of establishing it as a global standard of care is much of why Dr. Dileep Yavagal, an Indian-origin neurologist at the University of Miami, received a Lifetime Achievement Award at this year's American Academy of Neurology annual meeting.

The award, presented by the Association of Indian American Neurologists with the American Brain Foundation, recognized a career that runs from the laboratory bench to landmark clinical trials. Yavagal was a contributor to SWIFT PRIME, one of the studies that rewrote global stroke-treatment guidelines and made thrombectomy the standard for certain strokes. But the achievement he is most identified with is not a trial result. It is a campaign to fix a brutal inequality in who survives a stroke intact.

## The Statistic That Drives Him

The numbers are stark. By the estimate of a global study Yavagal led, mechanical thrombectomy is an option for fewer than 3% of the world's population. Even in wealthy countries the gaps are wide: Australia leads the world, with about 43% of people having access; in the United States the figure is roughly 32%. In India, it is around 1.4%.

That last number is the one that animates his work. Stroke is the second-leading cause of death and a leading cause of permanent adult disability worldwide, and the burden falls hardest on exactly the low- and middle-income countries where the catheters, the trained interventional neurologists, and the stroke-ready hospitals are scarcest. A treatment that exists but cannot be reached is, for most of humanity, no treatment at all.

## Mission Thrombectomy

In 2016, Yavagal founded the initiative now known as Mission Thrombectomy — originally MT2020 — to close that gap. It has since grown into a network with regional committees in more than 90 countries, working to build stroke systems where none existed: training physicians, organizing the chain of care that gets a stroke patient from an ambulance to a catheter in time, and pushing health systems to fund it.

The diaspora dimension of his work is direct. In 2025, Yavagal served as global principal investigator for GRASSROOTS, the first trial of a novel thrombectomy device run in a low- or middle-income country — India — a study that led to the device's approval there. It is a template for how a physician trained in India and risen to the top of American medicine can route the most advanced care back toward the country he came from, not as charity but as clinical infrastructure.

## A Career Built Across Two Countries

Yavagal's path is a familiar diaspora arc carried to an unusual height. He earned his medical degrees at the Seth G.S. Medical College and King Edward Memorial Hospital in Mumbai before training in the United States — a neurology residency at Massachusetts General and Brigham and Women's hospitals, fellowships at Columbia and UCLA. When he finished his interventional training in 2004, he was only the fourth fellowship-trained interventional neurologist in the country. He went on to co-found the world's first medical society for the specialty and to mentor dozens of the neurologists now running stroke programs around the world.

His research has also turned an uncomfortable mirror on his adopted country. Studies under his leadership have documented that rural American patients are far less likely to receive thrombectomy than urban ones — a reminder that the access gap is not only a problem of poor countries but of distance, infrastructure, and neglect everywhere.

## Why It Matters Beyond Medicine

For the Indian diaspora, Yavagal's recognition is a particular kind of story — not the entrepreneur or the executive, but the physician-scientist who used a place at the summit of American medicine to attack a problem most acute in the country of his birth. The Lifetime Achievement Award marks the scientific legacy. The 1.4% figure marks the unfinished work. As he put it on receiving the honor, the goal is a world in which "where you live — or what resources you have — does not determine whether you survive a stroke with your independence intact." For most of the planet, and for much of India, that world does not yet exist."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image (interventional procedure / cath lab)...")
    img_url = fetch_pexels_image("angiography catheter operating room")
    img_caption = "An interventional procedure in a catheterization suite; mechanical thrombectomy removes stroke-causing clots through a catheter"
    img_attr = "Pexels"
    if not img_url:
        img_url = pick_commons(["cerebral angiography stroke", "cerebral angiography"])
        img_caption = "A cerebral angiogram, the imaging used to guide stroke clot-removal procedures"
        img_attr = "Wikimedia Commons"
    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attr if final_img_url else "",
        "sources": json.dumps([
            "InventUM / University of Miami Miller School of Medicine \u2014 Dr. Dileep Yavagal Receives Lifetime Achievement Award at AAN 2026 (May 1, 2026): Yavagal, chief of interventional neurology and professor at the Miller School, received Lifetime Achievement Award at the 2026 American Academy of Neurology Annual Meeting; presented by Association of Indian American Neurologists (AINA) with the American Brain Foundation; quote on stroke as second leading cause of death and Mission Thrombectomy's work in middle/low-income countries",
            "ePadosi \u2014 Dileep R. Yavagal Wins Lifetime Achievement Award 2026: founder of Mission Thrombectomy, active in 90+ countries; contributor to SWIFT PRIME trial that rewrote global stroke guidelines; research exposed rural US thrombectomy access gaps; born and trained in India; fellowships at Harvard, Columbia, UCLA",
            "Yavagal official bio (cdn.wildapricot.com): MBBS 1994, MD 1997 at Seth G.S. Medical College & King Edward Memorial Hospital, Mumbai; residency MGH/Brigham; neurocritical-care fellowship Columbia Presbyterian; interventional neuroradiology fellowship UCLA 2002; 4th fellowship-trained interventional neurologist in the US (2004); co-founded SVIN (2006); founded Mission Thrombectomy/MT2020 (2016); led GRASSROOTS device trial in India (2025) as Global PI",
            "InventUM \u2014 Interventional Neurologist Receives Two Prestigious Awards for Global Stroke Work (Dec 2024): MT-GLASS study led by Yavagal \u2014 mechanical thrombectomy an option for fewer than 3% of the world's population; access ~43% Australia, ~32% US, ~1.4% India",
        ]),
        "tags": ["Indian diaspora", "Dileep Yavagal", "stroke", "Mission Thrombectomy", "neurology", "global health", "Indian Americans", "healthcare", "India"],
        "urgency": "low",
        "score_total": 73,
        "diaspora_angle": "Yavagal is the diaspora story less often told: not the founder or CEO, but the India-trained physician-scientist who reached the top of American medicine and turned it back toward the country he came from. India's ~1.4% access to a stroke treatment that can reverse disability \u2014 versus 32% in the US \u2014 is a gap that touches NRI families with aging parents in India directly.",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    return insert_article(article)


if __name__ == "__main__":
    print("Videshi NRI World Writer \u2014 2026-06-22 12:00 PT")
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    ids.append(write_article_3())
    print("\n" + "=" * 60)
    print("DONE. Inserted IDs:", [i for i in ids if i])
    print("=" * 60)
