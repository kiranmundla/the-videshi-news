#!/usr/bin/env python3
"""
Videshi News Writer — June 22, 2026 (00:30 UTC run)
2 NEW articles:
  1. Pakistan's Khawaja Asif threatens war over Indus Waters Treaty amid water crisis (news / geopolitics)
  2. Manipur Kuki-Naga violence escalates; 14 killed, 11 villages burnt, KIM seeks PM intervention (news / conflict)
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

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"


# ─── Image sourcing functions ────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 600:
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
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  \u26a0 Download failed ({r.status_code}): {url[:80]}")
            try:
                tmp = f"/tmp/{slug}_src"
                subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
                with open(tmp, "rb") as f:
                    content = f.read()
                if len(content) < 5000:
                    return None
                r_content = content
            except Exception:
                return None
        else:
            r_content = r.content
        ct = r.headers.get("Content-Type", "") if r.status_code == 200 else "image/jpeg"
        if "image" not in ct and len(r_content) < 5000:
            print(f"  \u26a0 Not an image or too small: {ct}, {len(r_content)} bytes")
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
            print(f"  \u26a0 Compressed image too small: {len(compressed)} bytes")
            return None

        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"

        requests.delete(upload_url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY
        })

        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=30)

        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ─── Article 1: Pakistan war threat over Indus Waters Treaty ──────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Pakistan war threat over Indus Waters Treaty")
    print("="*60)

    slug = "pakistan-khawaja-asif-war-threat-india-indus-waters-treaty-suspension-water-crisis-20260621"
    headline = "Pakistan's Defence Minister Says It Will 'Go to War' With India Over Water. The Treaty Has Been Suspended Since Last Year."
    subheadline = "Khawaja Asif's latest threat lands as Pakistan battles a severe internal water crisis affecting nearly a third of its population — and as New Delhi keeps the 1960 Indus Waters Treaty firmly in abeyance, more than a year after the Pahalgam attack."

    body = """Pakistan's Defence Minister Khawaja Asif has threatened war against India over water, escalating the rhetoric around a treaty New Delhi suspended more than a year ago. Speaking to ARY News on Saturday, Asif declared: "The moment we feel that our national security — and water is part of our national security — is being threatened, we will go to war against India. Definitely." He added that military action would be on the table should Islamabad find evidence that India is acting at an "alarming speed" to disrupt Pakistan's water supplies.

The threat is the latest in a long string of provocative statements from Asif, but its timing is telling. It arrives even as his own government faces widespread domestic instability and an internal water crisis that experts attribute largely to mismanagement at home rather than to any Indian action. A severe shortage is now affecting nearly one-third of Pakistan's population, concentrated in the agrarian provinces of Sindh and Balochistan — the very heartland the Indus river system is meant to sustain.

The dispute traces back to the deadly April 2025 terror attack in Jammu and Kashmir's Pahalgam, in which 26 people were killed. In its immediate aftermath, India's Cabinet Committee on Security held the 1960 Indus Waters Treaty in abeyance, declaring that the World Bank-brokered pact would remain suspended until Pakistan took credible, verifiable steps to dismantle its cross-border terror infrastructure. India has not blinked since: New Delhi recently reiterated that its decision to keep the treaty suspended remains unchanged.

The treaty itself has long been a rare island of cooperation between the two nuclear-armed neighbours. Signed in 1960, it allocates the three western rivers — the Indus, Jhelum and Chenab — largely to Pakistan, and the three eastern rivers — the Ravi, Beas and Sutlej — to India. In practice, roughly 80 percent of the water in the Indus system flows to Pakistan, irrigating more than 80 percent of its agricultural land. For a country where farming underpins both the economy and food security, the river is a lifeline, which is why even the suspension of the treaty's data-sharing and cooperation mechanisms has rattled Islamabad.

Asif's own credibility on the issue was undercut during the same interview. While accusing New Delhi of "weaponising water," manipulating flows on the Chenab and withholding hydrological data, he admitted that despite earlier claims that Pakistani teams had carried out "around 115 inspections," he lacked any current information on what India had done over the past year. The gap between the alarm in his words and the thinness of his evidence has not gone unnoticed by Indian commentators, who read the war talk as a deflection from Pakistan's own failure to manage its water.

Islamabad's legal position is that India cannot walk away unilaterally. Pakistani officials, Asif among them, have repeatedly argued that the treaty has no exit clause and that the World Bank, as guarantor, remains a stakeholder — so New Delhi cannot lawfully terminate or suspend it on its own. India counters that it has placed the treaty "in abeyance" rather than terminated it, and ties any restoration to Pakistan ending its support for terrorism. The two readings have left the pact in a legal and diplomatic limbo with no clear path back.

For the Indian diaspora, the stakes are larger than another round of cross-border sabre-rattling. Water has now joined Kashmir and trade as a structural flashpoint between two nuclear powers, and threats of war — however hollow they may sound when paired with admissions of missing data — raise the baseline of risk for families with roots on both sides of the border. NRIs in the Gulf, North America and the UK watch these moments closely: a genuine military escalation in South Asia would ripple through remittance flows, travel plans, energy prices and the safety of relatives back home. For now, the more revealing story may be the one Asif tried to talk past — a water crisis that is largely Pakistan's own, dressed up as a grievance against its neighbour.

The coming weeks will test whether the rhetoric stays rhetorical. India has shown no sign of softening its position on the treaty, and Pakistan's domestic pressures are only mounting. In that combination — a suspended lifeline, a deepening shortage, and a minister reaching for the language of war — lies the uneasy arithmetic the subcontinent will have to live with for as long as the treaty stays frozen."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    person_img = fetch_wikipedia_person_image("Khawaja Muhammad Asif")
    if person_img:
        img_url = person_img
        img_caption = "Pakistan's Defence Minister Khawaja Asif, who threatened war with India over the suspended Indus Waters Treaty"
        img_attribution = "Wikimedia Commons"

    if not img_url:
        for q in ["Khawaja Asif Pakistan Defence Minister", "Indus river Pakistan", "Indus River Sindh Pakistan"]:
            commons = fetch_wikimedia_commons_images(q)
            if commons:
                img_url = commons[0]["url"]
                img_caption = "The Indus river system, at the centre of a suspended India-Pakistan water treaty"
                img_attribution = "Wikimedia Commons"
                break

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "New Kerala / ANI — 'The moment we feel...: Pakistan threatens war against India over Indus Water Treaty as water crisis exposes domestic failure' (June 21, 2026): Defence Minister Khawaja Asif told ARY News Pakistan will 'go to war against India' if it feels water/national security is threatened; comments amid Pakistan's internal water crisis affecting nearly one-third of population in Sindh and Balochistan; India suspended 1960 Indus Waters Treaty after April 2025 Pahalgam attack (26 killed); treaty allows Pakistan 80% of Indus basin water for agriculture; Asif accused India of weaponising water and manipulating Chenab flows but admitted lacking current inspection data despite claim of ~115 past inspections",
            "Inshorts — 'Pakistan threatens war with India over Indus Waters Treaty' (Sunday, June 21, 2026): Asif quote 'The moment we feel that our national security — and water is part of our national security — is being threatened, we'll go to war against India. Definitely.'; India recently said its decision to keep the Indus Waters Treaty in abeyance remains unchanged",
            "The Indian Eye — 'Pakistan backs terror, India suspends Indus Water Treaty': Treaty allocates Western Rivers (Indus, Jhelum, Chenab) to Pakistan and eastern rivers (Ravi, Beas, Sutlej) to India; allocates ~20% of Indus system water to India and ~80% to Pakistan; India's Cabinet Committee on Security held treaty in abeyance until Pakistan credibly ends backing of terrorism"
        ]),
        "diaspora_angle": "Water has now joined Kashmir and trade as a structural flashpoint between two nuclear-armed neighbours, and even hollow-sounding war threats raise the baseline of risk for diaspora families with roots on both sides of the border — a genuine escalation would ripple through remittances, travel, energy prices and the safety of relatives back home.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Manipur Kuki-Naga violence escalation ────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Manipur Kuki-Naga violence escalation")
    print("="*60)

    slug = "manipur-kuki-naga-violence-escalation-14-killed-11-villages-burnt-kuki-inpi-modi-memorandum-20260621"
    headline = "A Third Community Has Been Drawn Into Manipur's War. Now the Kukis Are Begging Modi to Step In."
    subheadline = "What began in 2023 as a Kuki-Meitei conflict has spread to the Nagas. With 14 Kuki civilians reported killed, 11 villages burnt and roads to the hills blockaded, Manipur's apex Kuki body has handed a memorandum to the Prime Minister warning of abandonment."

    body = """The ethnic conflict that has torn at India's northeastern state of Manipur since 2023 has entered a dangerous new phase, drawing in a third community and pushing the state's hill districts back toward the kind of bloodshed not seen since the original Kuki-Meitei clashes left hundreds dead. This time, the fault line runs between the Kuki and the Naga communities — and the body that speaks for the Kuki tribes has gone directly to the Prime Minister.

On June 19, Kuki Inpi Manipur (KIM), the apex body of the Kuki tribes, submitted a seven-point memorandum to Prime Minister Narendra Modi through the Deputy Commissioner of Kangpokpi district, seeking "urgent intervention regarding the deteriorating Kuki-Naga relations, targeted attacks on Kuki people, and the worsening security situation in Manipur." The memorandum, signed by KIM President Ch. Ajang Khongsai and General Secretary Paotinthang Lupheng, stated that 11 Kuki villages have been ravaged and burnt and 14 Kuki civilians have lost their lives in repeated attacks. It said the continued delay in addressing these incidents had deepened a sense of "victimisation, insecurity, and abandonment" among the Kuki people.

The Kuki-Naga rupture has been building for months. KIM traces the deterioration to a chain of incidents beginning on February 8, when the Kuki village of Litan Sareikong was allegedly burnt following a drunken altercation, prompting the retaliatory burning of a Litan-Tangkhul Naga village. On March 13, two Kuki men were allegedly abducted from Thawai Kuki village by cadres of the NSCN-IM, a powerful Naga insurgent group; Kuki villagers detained 21 Tangkhul individuals in response before releasing them, while the two abducted men were later reported killed. The most serious escalation came on May 13, when armed groups ambushed a delegation of religious leaders — killing three pastors and injuring five others — who had travelled to broker peace between the Kukis and the Nagas. The peacemakers became the spark for a wider war.

In the weeks that followed, the violence spiralled into mass hostage-taking and retaliatory attacks. Amnesty International, in a June 4 statement, said twenty people had been taken hostage by armed groups from the Kuki and Naga communities, calling it the most serious escalation since May 2023 and demanding the immediate, unconditional release of all civilians held. Earlier rounds saw dozens detained on both sides — at one point 28 Kuki and Naga civilians, 14 from each community, were handed over under tight security in the Senapati and Kangpokpi districts. KIM's memorandum cited a fresh death in Henglep on June 16 as evidence the cycle has not stopped.

Beyond the killings, the conflict has strangled the basic functioning of the state. Naga and Kuki groups have repeatedly blockaded the mountain highways that carry food, fuel and medicine into Manipur's hill regions, leaving entire districts cut off. Observers have described a state "slowly suffocating" — roads silent, trucks halted, supplies of rice, petrol and medicine choked off. For ordinary residents already exhausted by three years of unrest, the second-order crisis of blocked supply lines has at times been as punishing as the violence itself.

The broader Manipur conflict, which has simmered and flared since May 2023, has by various counts killed hundreds and displaced tens of thousands, with churches, homes and entire villages destroyed across the Meitei-Kuki divide. The entry of the Nagas — and the involvement of established insurgent networks like the NSCN-IM — complicates an already tangled web of land disputes, residency-rights claims and historical grievances. KIM's demands reportedly include the abrogation of a ceasefire arrangement and a political settlement, signalling how far trust has eroded between communities that must ultimately share the same hills.

For the diaspora, Manipur is a painful and often under-covered story. Many in the Kuki and Naga communities are Christian, and their plight has drawn the attention of faith-based and human-rights networks abroad, including Amnesty's international arm. Diaspora groups with roots in India's northeast have pressed for greater central intervention and humanitarian access, frustrated that a conflict of this scale has not commanded the national and global attention it warrants. The appeal directed at Modi crystallises that frustration: a community that feels forgotten, asking the highest office in the land to prove otherwise.

Whether that intervention comes — and in what form — will shape not only Manipur's immediate future but India's standing on how it protects its most vulnerable citizens. For now, the memorandum sits with the Prime Minister's office, the highways stay blockaded, and a state that has known too little peace waits to see whether anyone in Delhi is listening."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    for q in ["Manipur landscape India", "Manipur hills India", "Imphal Manipur", "Manipur map India"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "Manipur, where escalating Kuki-Naga violence has left 14 reported dead and 11 villages burnt"
            img_attribution = "Wikimedia Commons"
            break

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "conflict",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Kukiland Express — 'Kuki Inpi Manipur Seeks PM's Intervention on Naga Conflict, Civilian Killings' (June 19, 2026): KIM (apex body of Kuki tribes) submitted a 7-point memorandum to PM Modi via Deputy Commissioner Kangpokpi seeking urgent intervention on deteriorating Kuki-Naga relations; signed by President Ch. Ajang Khongsai and GS Paotinthang Lupheng; cites 11 Kuki villages burnt, 14 Kuki civilians killed, June 16 Henglep death; timeline — Feb 8 Litan Sareikong burning, March 13 abduction of two Kuki men by NSCN-IM (21 Tangkhul detained then released), May 13 ambush killing 3 pastors and injuring 5; KIM demands ceasefire abrogation and political settlement",
            "Amnesty International USA — 'India: Release All Hostages and End Cycle of Violence in Manipur' (June 4, 2026): twenty civilians taken hostage by armed groups from Kuki and Naga communities; conflict between Kuki and Meitei has expanded to involve a third group, the Nagas; described as most serious escalation since May 2023 when Kuki-Meitei clashes left hundreds dead; calls for immediate unconditional release of all hostages and independent investigations",
            "Adnan Khan, LinkedIn analysis 'Lifelines Cut: Manipur Starves Amid Naga-Kuki Clash' (June 5, 2026): Kuki and Naga groups clashing in hill regions over residency rights and territorial control since February 2026; May 13 ambush killed three church leaders who had led a Kuki Christian delegation to Nagaland to broker peace; highway blockades have paralysed transport of food, fuel and medicine across the region"
        ]),
        "diaspora_angle": "Many in Manipur's Kuki and Naga communities are Christian, and their plight has drawn faith-based and human-rights networks abroad; diaspora groups with northeastern roots have pressed for greater central intervention and humanitarian access, frustrated that a conflict of this scale has not commanded the national or global attention it warrants.",
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
