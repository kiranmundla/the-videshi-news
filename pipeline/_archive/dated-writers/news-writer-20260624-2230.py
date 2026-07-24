#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (22:30 UTC run)
2 NEW articles, dedup-checked against last ~45 news articles:
  1. SCOTUS Blanche v. Lau: a 6-3 ruling (Thomas) that border officers need NOT
     have clear-and-convincing evidence of a "crime involving moral turpitude"
     before treating a returning green-card holder as an "applicant for
     admission" — making it easier to deny reentry and start removal. Distinct
     from the DC Circuit expedited-removal piece already published 2026-06-23.
  2. Canada eyes a "transformative" defence/aerospace partnership with India,
     per High Commissioner Chris Cooter — Canada's defence budget on a "hockey
     stick" toward 5% of GDP (~$500B extra by 2035), GSOIA framework, CANSEC
     surge. Distinct from all the India-Canada CEPA/trade coverage.
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


def pick_commons(queries, min_width=900):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            return pick["url"], pick.get("title", "")
    return None, ""


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


# \u2500\u2500\u2500 Article 1: SCOTUS Blanche v. Lau green-card reentry ruling \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: SCOTUS Blanche v. Lau green-card reentry ruling")
    print("="*60)

    slug = "supreme-court-blanche-lau-green-card-reentry-moral-turpitude-thomas-6-3-diaspora-20260624"
    headline = "The Supreme Court Just Made the Green Card a Little Less Secure at the Border"
    subheadline = "In a 6-3 ruling, the justices said immigration officers don't need clear evidence of a crime to treat a returning permanent resident as someone newly 'seeking admission' \u2014 a quiet shift with outsized stakes for the millions of Indians who hold green cards and travel home."

    body = """For decades, the working assumption among green-card holders has been simple: once you are a lawful permanent resident, the document in your wallet protects you when you come back through an American airport. The US Supreme Court has just complicated that assumption.

In a 6-3 decision in *Blanche v. Lau*, handed down this week, the court ruled that an immigration officer does not need "clear and convincing evidence" that a returning permanent resident has committed a "crime involving moral turpitude" before treating that person not as an admitted resident but as an "applicant for admission" \u2014 a status that strips away key protections and makes removal far easier. Justice Clarence Thomas, writing for the majority, said nothing in the Immigration and Nationality Act imposes that higher evidentiary bar on border officers making, in his words, "quick judgments on the spot."

## What the Case Was Actually About

The dispute centred on Muk Choi Lau, a Chinese national who became a lawful permanent resident in the mid-2000s. In 2012, while under indictment for third-degree trademark counterfeiting, Lau travelled abroad. When he returned, immigration officers paroled him into the country on temporary status rather than readmitting him as a permanent resident. After he was convicted, the Department of Homeland Security moved to remove him, arguing he had been "inadmissible" at the moment he tried to re-enter.

A federal appeals court, the Second Circuit, had sided with Lau, finding he should not have been paroled in the first place. The Supreme Court vacated that finding and sent the case back, holding that the government had "correctly regarded Lau as an applicant for admission." Crucially, the justices did not decide whether Lau's specific offence actually counted as a crime of moral turpitude \u2014 they decided something narrower and, for travellers, more consequential: how much proof an officer needs before flipping a green-card holder into the more vulnerable "seeking admission" category.

## A Sharp Dissent

The court's three liberal justices dissented. Justice Ketanji Brown Jackson warned that the decision "allows the Government to deem an LPR to be 'seeking an admission' first and justify the applicability of an exception later," undermining "the benefits and security that come with having a green card." The phrase captures the worry now rippling through immigration-law circles: that the ruling lets enforcement run ahead of evidence, with the proof sorted out afterward.

The decision lands in a week thick with immigration rulings. A separate federal appeals court cleared the Trump administration to expand fast-track "expedited removal" deeper into the country's interior, and the broader enforcement climate has grown markedly tougher. Against that backdrop, *Blanche v. Lau* is less a thunderclap than a tightening \u2014 one more turn of the screw at the border.

## Why It Matters for the Diaspora

There are more than three million people of Indian origin in the United States, and Indians make up one of the largest groups of green-card holders and green-card applicants in the country. For them, this is not an abstract debate about statutory interpretation. It is about the trip home for a wedding, a parent's illness, a festival \u2014 and the moment of re-entry that follows.

The practical takeaway from immigration attorneys is sobering but clear. A permanent resident with any pending charge, an old arrest, or even an unresolved legal question in their past now faces greater uncertainty at the border, because an officer can treat them as "seeking admission" on a lower threshold of suspicion. Lawyers are already advising green-card holders with any criminal history \u2014 however minor or however old \u2014 to consult counsel *before* travelling internationally, to carry documentation, and to understand that a guilty plea to a seemingly trivial offence can carry immigration consequences far heavier than the original penalty.

For a community that prizes the green card as the stable middle rung on the ladder to citizenship, the message of this ruling is uncomfortable: that rung is a little more slippery than it looked. The document still confers enormous rights. But the Supreme Court has just reminded its holders that those rights are tested most severely at exactly the moment they are coming home.
"""

    img_url, _ = pick_commons([
        "United States Supreme Court Building",
        "Supreme Court of the United States west facade",
        "US Supreme Court building Washington"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "The United States Supreme Court, which ruled 6-3 in Blanche v. Lau that border officers need not have clear evidence of a crime to treat a returning green-card holder as an applicant for admission"

    if not img_url:
        img_url = fetch_wikipedia_person_image("Clarence Thomas")
        img_caption = "Justice Clarence Thomas, who wrote the 6-3 majority opinion in Blanche v. Lau easing the standard for denying green-card holders reentry"

    if not img_url:
        px = fetch_pexels_image("airport immigration passport control")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A Supreme Court ruling has made re-entry at the US border more uncertain for green-card holders with any criminal history"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Bloomberg Law (news.bloomberglaw.com, June 2026) \u2014 'Justices Back Border Officers in Dispute Over Green Card Reentry': in a 6-3 ruling, the Supreme Court held that the Immigration and Nationality Act does not require border officers to have a conviction or confession to a crime involving moral turpitude before paroling lawful permanent residents into the country; Justice Clarence Thomas wrote for the court, declining to read a 'clear-and-convincing-evidence' burden into the statute; Justice Ketanji Brown Jackson dissented, joined by the court's liberals; the case involved Muk Choi Lau, a lawful permanent resident convicted of third-degree trademark counterfeiting, and was sent back to the Second Circuit without deciding whether his crime involved moral turpitude.",
            "Washington Examiner (washingtonexaminer.com, June 2026) \u2014 'Clarence Thomas hands DHS win on denying criminal immigrants entry into the country': the ruling in Blanche v. Lau concerns the standard for determining whether a legal permanent resident who committed a crime should be denied admission and subject to removal; Thomas wrote that DHS does not need clear and convincing evidence to consider a green-card holder an 'applicant for admission' for having committed a 'crime involving moral turpitude'; the decision makes it easier for immigration officials to deny entry and remove such immigrants.",
            "Daily Caller (dailycaller.com, June 2026) \u2014 'Supreme Court Rules In Favor Of Trump Admin On Government's Ability To Deny Admission To Green Card Holders': Blanche v. Lau overturned a Second Circuit ruling that border officials need 'clear and convincing evidence' of a crime before denying admission; the majority concluded Lau had been 'correctly charged with inadmissibility' as an alien 'seeking admission'; Justice Ketanji Brown Jackson's dissent, joined by Justices Sotomayor and Kagan, argued the decision lets the government deem an LPR to be 'seeking an admission' first and justify the exception later, undermining 'the benefits and security that come with having a green card.'",
            "CNN / Reuters (cnn.com, reuters.com, June 2026) \u2014 'Trump effort to expand speedy deportations of migrants can proceed, appeals court rules': in the same week, the DC Circuit Court of Appeals revived the administration's expansion of 'expedited removal' to undocumented immigrants in the interior who cannot prove two years' continuous presence, illustrating a broader tightening of US immigration enforcement around the Blanche v. Lau decision."
        ]),
        "diaspora_angle": "Indians are among the largest groups of US green-card holders and applicants, and for a community whose life revolves around trips home for weddings, festivals and family emergencies, the ruling makes re-entry riskier for any permanent resident with even a minor or old criminal matter \u2014 prompting attorneys to urge affected NRIs to seek legal advice before travelling internationally.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: Canada eyes transformative defence partnership with India \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Canada-India defence/aerospace partnership")
    print("="*60)

    slug = "canada-india-defence-aerospace-partnership-cooter-hockey-stick-5-percent-gdp-gsoia-diaspora-20260624"
    headline = "Canada Is About to Spend Half a Trillion on Defence. It Wants India to Build a Lot of It."
    subheadline = "Ottawa's military budget is on a 'hockey stick' toward 5% of GDP, and its envoy in New Delhi is openly courting Indian manufacturers \u2014 a pairing of Canadian technology and Indian scale that, just two years after a bitter diplomatic rupture, signals how far the relationship has swung back."

    body = """Two years ago, the India-Canada relationship was in open crisis, consumed by a diplomatic row over the killing of a Khalistani separatist on Canadian soil that saw both countries expel each other's diplomats. This week, Canada's top envoy in New Delhi was pitching Indian firms on a partnership to help build the next generation of Canadian fighter jets, warships and defence technology. The whiplash is the story.

Canadian High Commissioner to India Chris Cooter laid out a strikingly ambitious vision for defence and aerospace cooperation, anchored by a historic surge in Canadian military spending. Having recently crossed the NATO benchmark of 2% of GDP, Canada is now racing toward a 5% target \u2014 a trajectory Cooter described, fittingly, as "a Canadian hockey stick." For the world's ninth-largest economy, that curve translates into roughly $500 billion in additional defence spending by 2035.

## "We Have the Technology. We Don't Have the Scale."

The logic of the pitch is candid. "We have lots of advanced technology, but we don't have the scale, we don't have the market," Cooter said \u2014 a sentence that doubles as the entire rationale for turning to India. Canada brings high-end innovation in aerospace and defence; India brings manufacturing capacity, a vast domestic market, and a government determined to make defence production at home a strategic priority. Merge the two, the argument goes, and each side fixes the other's gap.

For now, the existing relationship is, in Cooter's own words, "very small" \u2014 a handful of companies clustered in aerospace and defence. But he framed that smallness as the opportunity, not the obstacle: a near-blank slate that Canada's spending wave can fill. He pointed to critical minerals, defence and aerospace as the sectors with the widest gulf between current trade and genuine potential.

## Building the Plumbing

Ambition is one thing; the unglamorous machinery of cooperation is another. Cooter emphasised the General Security of Information Agreement (GSOIA), a framework that lets companies in both countries share sensitive technical information securely \u2014 the kind of government-to-government plumbing that has to exist before any serious joint venture can. Negotiations on the GSOIA were launched following a commitment made in March by Prime Minister Narendra Modi and Canadian Prime Minister Mark Carney, and the two governments are now finalising the schedule for a high-level defence dialogue between their militaries and defence departments. Industrial appetite is already visible: the recent CANSEC defence-industry conference in Canada drew a notable surge in attendance and engagement.

The High Commissioner described the relationship as having entered a new, "reliable, process-driven" phase \u2014 diplomatic code for trust restored after the Nijjar-era freeze. That restored trust is being put to work beyond hardware, too, with both sides now coordinating against shared threats: the fentanyl precursor supply chain, and the international "scam centres" that prey on citizens of both countries.

## Why It Matters for the Diaspora

The Indo-Canadian community \u2014 some 1.8 million strong and one of the most influential diasporas in the country \u2014 has spent the past few years watching the bilateral relationship lurch from crisis to cautious thaw, often feeling caught in the middle. A defence and industrial partnership of this scale is, in a sense, the clearest signal yet that the two governments intend to rebuild on something more durable than warm words: shared money, shared supply chains and shared security interests.

It also carries concrete promise. A surge of Canadian defence investment paired with Indian manufacturing could mean jobs and contracts on both sides of the corridor \u2014 in aerospace hubs around Montreal and Toronto where Indo-Canadian engineers and entrepreneurs are heavily represented, and in India's expanding defence-industrial base. For the broader diaspora, it reflects a familiar pattern: Indian talent and capacity becoming indispensable to a Western economy's ambitions. The relationship that looked broken in 2024 is being rebuilt, this time with steel. The question now is whether the politics stay steady enough to let the hockey stick play out.
"""

    img_url = fetch_wikipedia_person_image("Chris Cooter")
    img_attribution = "Wikimedia Commons"
    img_caption = "Canadian High Commissioner to India Chris Cooter, who outlined an ambitious defence and aerospace partnership between Ottawa and New Delhi"

    if not img_url:
        img_url, _ = pick_commons([
            "Flag of Canada Flag of India",
            "Canada India flags",
            "CF-18 Hornet Royal Canadian Air Force",
            "aerospace manufacturing aircraft factory"
        ])
        img_caption = "Canada is courting Indian defence and aerospace manufacturers as its military budget climbs toward 5% of GDP"

    if not img_url:
        px = fetch_pexels_image("fighter jet aerospace defence")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Canada's surge in defence spending is opening opportunities for partnership with India's manufacturing base"

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
            "The Indian Eye (theindianeye.com, June 22, 2026) \u2014 'Canada eyes transformative defence partnership with India': Canadian High Commissioner to India Chris Cooter outlined a vision for deepened defence and aerospace cooperation anchored by Canada's defence budget climbing toward 5% of GDP, which he described as a 'Canadian hockey stick'; he projected roughly $500 billion in additional Canadian defence spending by 2035, said 'we have lots of advanced technology, but we don't have the scale, we don't have the market,' and emphasised the General Security of Information Agreement (GSOIA) as critical groundwork; negotiations followed a March commitment by PM Modi and PM Carney, with a high-level defence dialogue being scheduled and the CANSEC conference showing a surge in industrial interest.",
            "Devdiscourse / ANI (devdiscourse.com, June 2026) \u2014 \"'Very realistic': Canadian envoy to India Chris Cooter backs 2026 CEPA deadline\": Cooter said Canada has nearly $109 billion invested in India \u2014 almost 25% of its Indo-Pacific investment \u2014 while Indian investment in Canada stands around $11 billion; he called the commercial relationship 'modest' relative to its potential, naming critical minerals, defence and aerospace as growth areas, and noted Commerce Minister Piyush Goyal's recent visit with the largest-ever Indian business delegation to Canada.",
            "The Indian Eye (theindianeye.com, June 2026) \u2014 'India and Canada review energy cooperation at G7 Summit': at the Evian G7 Summit, PMs Modi and Carney reviewed bilateral ties, agreed to launch negotiations on a General Security of Information Agreement (GSOIA), welcomed defence-institution exchanges, and announced new platforms including Raisina Americas; bilateral trade stands near USD 8.5 billion with a target of USD 50 billion by 2030.",
            "Wikipedia (en.wikipedia.org) \u2014 '2023\u201325 Canada\u2013India diplomatic row': background on the diplomatic rupture between India and Canada following the 2023 killing of Khalistani separatist Hardeep Singh Nijjar on Canadian soil, which led to mutual expulsions of diplomats and froze the bilateral relationship before its recent thaw."
        ]),
        "diaspora_angle": "For the 1.8-million-strong Indo-Canadian community that lived through the Nijjar-era diplomatic freeze, a half-trillion-dollar Canadian defence build-up courting Indian manufacturers is the strongest sign yet that the two governments are rebuilding ties on durable foundations of shared industry and security \u2014 with potential jobs and contracts in Indo-Canadian aerospace hubs around Montreal and Toronto.",
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
