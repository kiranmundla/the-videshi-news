#!/usr/bin/env python3
"""
Videshi News Writer — June 26, 2026 (16:30 UTC / 09:30 PDT run)
2 NEW articles, dedup-checked against last 3 days (40 news articles):
  1. "Passport is not proof of citizenship" — MEA clarification (June 24)
     ignites a national row; Tharoor wades in with a dual-citizenship/OCI
     solution; opposition fears NRC groundwork. NOT covered (passport FEE
     hike is covered; the citizenship-PROOF debate is not).
  2. India's digital-nomad moment — workations, Sikkim's Yakten "digital
     nomad village", India ranked world's most affordable nomad base yet
     still has NO digital-nomad visa, while 50+ countries court Indian
     remote workers. NOT covered.
"""
import os, json, requests, urllib.parse, subprocess, io, re
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
load_env(os.path.expanduser('~/workspace/.env.supabase'))
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

_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use","just",
    "here","need","know","quietly","almost","like","could","into","now","its","rare",
}

def _keywords(text):
    out = []
    for t in re.findall(r"[A-Za-z][A-Za-z'-]+", text or ""):
        tl = t.lower()
        if len(tl) >= 4 and tl not in _COMMONS_STOP:
            out.append(tl)
    return out

def commons_relevance_ok(commons_title, headline, topic=""):
    title_l = (commons_title or "").lower()
    if not title_l:
        return False
    kws = set(_keywords(headline)) | set(_keywords(topic))
    if not kws:
        return True
    return any(kw in title_l for kw in kws)

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
            pages = r.json().get("query", {}).get("pages", {})
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
                })
            if results:
                print(f"  \u2713 Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Commons error: {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}'")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None

def download_and_compress(url, slug):
    try:
        r_content = None
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
            if r.status_code == 200 and len(r.content) >= 5000:
                r_content = r.content
        except Exception:
            pass
        if r_content is None:
            tmp = f"/tmp/{slug}_src"
            subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=40, check=True)
            with open(tmp, "rb") as f:
                r_content = f.read()
            if len(r_content) < 5000:
                print(f"  \u26a0 Image too small after curl fallback")
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
            print(f"  \u26a0 Compressed too small")
            return None
        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        requests.delete(upload_url, headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY})
        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg", "x-upsert": "true"}, timeout=30)
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url[:80]}...")
            return public_url
        print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None

def fetch_wikipedia_summary_image(title):
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}",
                         headers={"User-Agent": UA}, timeout=10)
        if r.status_code == 200:
            d = r.json()
            img = d.get("originalimage", {}).get("source") or d.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image ({title}): {img[:70]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error: {e}")
    return None

def pick_commons(queries, headline, topic="", min_width=800):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        commons = [c for c in commons if commons_relevance_ok(c.get("title", ""), headline, topic)]
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            print(f"  \u2713 Commons pick: {pick.get('title','')}")
            return pick["url"], pick.get("title", "")
    return None, ""

def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
    return None


# ─── Article 1: Passport is not proof of citizenship — Tharoor + NRC fears ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Passport not proof of citizenship debate")
    print("="*60)

    slug = "india-passport-not-proof-of-citizenship-mea-clarification-tharoor-oci-dual-citizenship-nrc-fears-20260626"
    headline = "India Says Your Passport Doesn't Prove You're a Citizen. The Diaspora Should Read the Fine Print."
    subheadline = "A single line from a government official \u2014 a passport is a travel document, not proof of citizenship \u2014 has set off a national argument about who counts as Indian. Shashi Tharoor has stepped in with a fix, and for NRIs and OCI holders, the stakes are quietly personal."

    body = """It started with one sentence. An unnamed Ministry of External Affairs official, briefing reporters on Wednesday, said that an Indian passport is a travel document and not, by itself, proof of citizenship. Within hours the remark had detonated across Indian politics, drawing in the opposition, constitutional lawyers, retired diplomats and \u2014 inevitably \u2014 millions of Indians abroad who have always treated that little blue booklet as the surest evidence of who they are.

The government's position is narrowly, technically defensible. Citizenship in India is governed by the Citizenship Act of 1955; passports are issued under the Passports Act of 1967. Section 20 of the Passports Act explicitly lets the central government issue a passport "to a person who is not a citizen of India" if it judges this to be "in the public interest." A 2013 Bombay High Court ruling acknowledged the same. Officials and legal experts now argue that only a birth certificate or a citizenship certificate constitutes conclusive proof of Indian nationality. As former diplomat Nirupama Rao put it, a passport is the property of the government and can be confiscated, while citizenship is a right that cannot be taken away.

## Why a Technicality Became a Firestorm

If the law is so clear, why the uproar? Because legal accuracy and public confidence are not the same thing. A passport is issued only after the government has satisfied itself that the applicant is Indian. For an ordinary citizen, it is the single most trusted document they will ever hold to represent themselves before a foreign government. To be told, suddenly, that it is not proof of citizenship lands as something closer to a threat than a clarification.

The opposition has framed it exactly that way, alleging the government is laying the groundwork to "arbitrarily deny" citizenship to those who disagree with it \u2014 and many heard in the remark the distant echo of a nationwide National Register of Citizens. The pattern fuels the anxiety: Aadhaar is not proof of citizenship, PAN is not proof of citizenship, and now the passport joins the list. The obvious question, as one commentator wrote, becomes: then what is? The Election Commission, for its part, noted that a passport remains one of the twelve valid documents a voter can use to establish eligibility \u2014 a reminder that the "not proof" line is more legal hair-splitting than settled doctrine.

## Tharoor's Fix

Into this walked Shashi Tharoor, the Thiruvananthapuram MP and former UN under-secretary-general, who reframed the row as the moment to fix something he has pushed for years: a durable legal status for Indians abroad. Tharoor argued that Overseas Citizenship of India is itself a misnomer. "It is not citizenship, it is only a lifetime visa," he said, "and as we have seen, even that visa can be revoked by the government. We definitely need to revisit this policy and try and make it more durable." Many Indians, he noted, take a foreign passport for professional or practical reasons while their hearts remain in India, and the law should find "a legal formula" to recognize that \u2014 his long-standing call for some form of dual citizenship, which Article 9 of the Constitution and Section 9 of the Citizenship Act currently forbid.

## Why It Matters for the Diaspora

For NRIs and especially for the millions who hold OCI cards, this is not an abstract constitutional debate \u2014 it is a reminder of how thin their formal tie to India actually is. The MEA itself is explicit that OCI "is not to be misconstrued as dual citizenship" and confers no political rights: holders cannot vote, cannot hold constitutional office, and remain, in law, foreigners with a lifelong visa. The recent cancellation of OCI status for more than a hundred people sharpened the point that even that visa can be withdrawn.

So when New Delhi parses the difference between a travel document and citizenship, the diaspora has reason to pay attention. A first-generation migrant who clung to an Indian passport as a piece of identity, an OCI holder who assumed the card was "citizenship without the vote," a child born abroad to OCI parents who has found herself in a legal grey zone \u2014 all of them are touched by where these definitions land. Tharoor's intervention offers the diaspora a champion for a more secure status. Whether a government that has resisted dual citizenship for two decades is willing to listen is, for now, the open question."""

    topic = "Shashi Tharoor passport citizenship India parliament"
    img_url = fetch_wikipedia_summary_image("Shashi_Tharoor")
    img_attribution = "Wikimedia Commons"
    img_caption = "Congress MP Shashi Tharoor, who has urged a 'durable' legal status for Indians abroad amid the passport-citizenship debate"
    if not img_url:
        img_url, _ = pick_commons(["Shashi Tharoor", "Indian passport document", "Parliament of India building"], headline, topic)
        img_caption = "India's passport-citizenship debate has reignited questions about the legal status of Indians abroad"
    if not img_url:
        px = fetch_pexels_image("passport document travel")
        if px:
            img_url = px; img_attribution = "Pexels"
            img_caption = "India's clarification that a passport is not proof of citizenship has sparked a national debate"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "citizenship",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Business Standard / TBS News (tbsnews.net, 26 June 2026) \u2014 'Passport not proof of citizenship? India's legal position sparks debate': controversy after media reported, quoting an unnamed MEA official on Wednesday 24 June, that a passport is a travel document and not proof of citizenship; government said no new decision taken in 12 years; opposition alleges groundwork to 'arbitrarily deny' citizenship to those who disagree; Election Commission officials said passports remain among the 12 valid supporting documents voters can use to prove eligibility; cites Passports Act 1967 Section 20 (passports/travel documents may be issued to persons who are not citizens of India 'in the public interest') and Section 6(2)(a) (authority shall refuse a passport 'if the applicant is not a citizen of India').",
            "The Daily Jagran (thedailyjagran.com, 25 June 2026) \u2014 'Why Passport Isn't Proof Of Citizenship: MEA Clarification Revives Debate, 1967 Law And Bombay HC Verdict Offer Answers': government sources and legal experts, citing the Passports Act 1967 and Citizenship Act 1955, clarify only a birth certificate or citizenship certificate is valid proof of Indian citizenship; under Section 20 of the 1967 Act the central government can issue passports to non-citizens, upheld by a 2013 Bombay High Court verdict; the primary purpose of a passport is to act as a travel document and protect the holder's rights abroad; former diplomat Nirupama Rao said on X the passport is the government's property and can be confiscated, while citizenship is a right that can't be taken away.",
            "Devdiscourse / PTI (devdiscourse.com) \u2014 'Tharoor expresses limited support for dual citizenship proposal': Congress MP Shashi Tharoor said people living abroad must be allowed to keep their Indian passports and the issue requires 'more expansive understanding'; said he had taken up dual citizenship in the past without support from the present BJP government or the previous government; called OCI a misnomer \u2014 'It is not citizenship, is only a lifetime visa. And as we have seen with the BJP government, even that visa can be revoked'; said India must find 'a legal formula' to let citizens keep their passports when circumstances require a foreign passport, and that he would be a voice for dual citizenship in Parliament; dual citizenship is barred by Article 9 of the Constitution read with Section 9 of the Citizenship Act 1955.",
            "Tabla / Straits Times (tabla.com.sg) and India MEA \u2014 'OCIs are not dual citizens': the MEA website states 'OCI is not to be misconstrued as dual citizenship. It does not confer political rights' and OCI holders are not entitled to Article 16 public-employment equality; OCI is a lifelong multiple-entry visa, holders are foreigners who cannot vote, hold constitutional posts or have public-employment rights; recent controversy over cancellation of OCI status of more than 100 people; a 2021 Supreme Court petition argued the government had described OCI as effectively dual citizenship without political rights.",
            "LinkedIn analysis / Mondaq (June 2026) \u2014 commentary noting Aadhaar, PAN and now the passport have each been described as 'not proof of citizenship', prompting the question of what document does establish it, and a Delhi High Court order (15 May 2024, Justice Prathiba M Singh) finding a child born in India to OCI-cardholder parents faced de facto statelessness, illustrating gaps in the Citizenship Act framework."
        ]),
        "diaspora_angle": "For NRIs and the millions holding OCI cards, India's clarification that a passport is not proof of citizenship \u2014 and Tharoor's reminder that OCI is 'only a lifetime visa' that can be revoked \u2014 underscores how thin their formal legal tie to India really is, making the call for a durable dual-citizenship formula a directly personal stake for the diaspora.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ─── Article 2: India's digital-nomad moment ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India's digital-nomad moment")
    print("="*60)

    slug = "india-digital-nomads-workation-yakten-village-most-affordable-no-nomad-visa-countries-court-remote-workers-20260626"
    headline = "India Is the World's Cheapest Place to Work Remotely. It Still Won't Give Digital Nomads a Visa."
    subheadline = "A third of Indian travellers now want to work from a hillside or a beach, a Himalayan village has reinvented itself for laptops, and dozens of countries are courting Indian remote workers. The one place that hasn't built a door for them is India itself."

    body = """The idea of taking your job on the road \u2014 a "workation" \u2014 was, until recently, the stuff of the occasional extended holiday. It is now something close to a default aspiration for a generation of young Indian professionals. A survey by Thrillophilia and the Federation of Indian Chambers of Commerce & Industry (FICCI) found that 33 percent of Indian travellers now prefer to work remotely amid natural settings, a number that turns a lifestyle quirk into a genuine economic trend.

The shift has even reshaped the map. In 2025, Sikkim's Yakten, a quiet village in the hills of Pakyong district once known to nature lovers and trekkers, reinvented itself as India's first "digital nomad village" \u2014 courting a new kind of visitor armed with laptops and reliable Wi-Fi rather than hiking boots. Across the country, hospitality is rushing to follow, with work-friendly stays sprouting in the hills, on beaches and in quieter towns as hybrid and gig work makes location independence ordinary.

## The Paradox at the Centre

Here is the strange part. According to a report from Global Citizen Solutions, India ranks as the world's single most affordable country for digital nomads \u2014 a place where a remote worker's salary stretches further than almost anywhere on earth. And yet India does not offer a digital nomad visa. A foreigner who wants to live in Goa or Himachal and work for an overseas employer has no dedicated legal pathway to do so; the option simply doesn't exist.

That gap stands out precisely because the rest of the world has moved the other way. What began around 2021 with a handful of pioneer islands \u2014 Antigua & Barbuda, Bermuda, Croatia \u2014 has become a global scramble. Japan, South Korea and Turkey launched nomad visas in 2024; Spain, Taiwan, Bulgaria, Slovenia and the Philippines followed; Mauritius, Kenya, the UAE, Thailand, Malaysia, Colombia and Estonia now run programmes of their own. For these countries, the remote worker is an attractive migrant: high-earning, self-sufficient, and barred from competing for local jobs, since income must come from outside the host country.

## What This Means for the Indian Worker

For Indians, the nomad-visa boom cuts two ways. On one hand, it has thrown open the door to legal life abroad for the country's fast-growing remote workforce. Estonia's Type D nomad visa lets an Indian live in Tallinn for a year working for international clients, with Schengen access and \u2014 if they stay under 183 days \u2014 no Estonian tax. Most programmes ask for proof of remote income, typically between $1,500 and $4,000 a month: Croatia around \u20ac2,400, Costa Rica about $3,000, Estonia roughly \u20ac4,500. For a well-paid Indian engineer or freelancer, those thresholds are increasingly within reach.

On the other hand, the paperwork is tightening. In early 2026, the UAE doubled the bank-statement requirement for its Dubai remote-work visa from three to six months, effectively demanding half a year of steady income history and squeezing out the newly remote. The lesson for Indian applicants is that the window favours those with stable, documented earnings, and that each programme carries its own tax-residency traps that can turn a dream relocation into an expensive surprise.

## Why It Matters for the Diaspora

The digital nomad is, in a sense, a new species of NRI \u2014 not the engineer who emigrates on an H-1B and settles for good, but a worker who moves fluidly between countries, anchored to an Indian salary or Indian clients while living in Lisbon, Tallinn or Bali. As the visa headwinds buffet traditional routes like the H-1B and the student-to-work pipeline, the nomad path offers the diaspora a more flexible, lower-commitment way to live abroad without surrendering the Indian base \u2014 or the Indian passport \u2014 that, as this week's citizenship debate showed, still carries deep meaning.

The unanswered question is whether India will join the party. A country that is simultaneously the cheapest place on earth to work remotely and one of the largest exporters of remote talent has an obvious opening: a nomad visa of its own could draw foreign earners and their spending into its hill towns and beach districts, and signal that the traffic need not run only one way. For now, India is content to send digital nomads out into the world. The case for welcoming them in is only getting stronger."""

    topic = "digital nomad remote work laptop coworking workation"
    img_url, _ = pick_commons([
        "digital nomad working laptop cafe",
        "remote worker laptop mountains",
        "coworking space laptop",
        "freelancer working outdoors laptop",
    ], headline, topic)
    img_attribution = "Wikimedia Commons"
    img_caption = "A remote worker on a laptop; India ranks as the world's most affordable base for digital nomads"
    if not img_url:
        px = fetch_pexels_image("digital nomad laptop working remotely beach mountains")
        if px:
            img_url = px; img_attribution = "Pexels"
            img_caption = "A remote worker on a laptop; India ranks as the world's most affordable base for digital nomads"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-work",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Outlook Traveller (outlooktraveller.com, 24 June 2026) \u2014 'Work, Travel, Stay: Inside India's Growing Workation Culture And Where To Stay': a Thrillophilia\u2013FICCI survey found 33% of Indian travellers now prefer working remotely amid natural settings; workations have emerged as a defining post-pandemic travel trend driven by hybrid and gig work; in 2025 Sikkim's Yakten village (Pakyong district) became India's first 'digital nomad village', pivoting from nature/adventure tourism to attract remote workers with laptops.",
            "Mint / LiveMint (livemint.com) \u2014 'The rise of remote workers: Why countries are rolling out visas for digital nomads': Antigua & Barbuda, Bermuda and Croatia among first to introduce nomad visas around 2021; Japan, South Korea and Turkey in 2024, then Spain, Taiwan, Moldova, Bulgaria, Slovenia, Philippines; others include Mauritius, Kenya, UAE (Dubai), Thailand, Malaysia, South Africa, Namibia, Colombia, Uzbekistan; per Global Citizen Solutions, India ranks as the world's most affordable country for digital nomads but does NOT offer a digital nomad visa; most programmes require proof of remote work and a minimum income of roughly $1,500\u2013$4,000/month (Croatia ~\u20ac2,400, Costa Rica ~$3,000, Turkey ~$3,000 plus a degree).",
            "Jobbatical (jobbatical.com, 2026 guide) \u2014 'Estonia Digital Nomad Visa for Indians': Estonia's Type D digital nomad visa lets Indians live in Estonia for a year working for international clients; Schengen access for 90 days in any 180; staying under 183 days avoids Estonian tax so Indian/global income is untouched; monthly living costs cited around \u20b91.5\u20132 lakh; positioned as an alternative to pricier Thailand or colder Canada routes.",
            "The Traveler (thetraveler.org, 2026) \u2014 'Dubai Remote Work Visa Explained for Digital Nomads': in late January/February 2026 UAE authorities doubled the bank-statement requirement for the Dubai remote-work visa from three to six consecutive months, effectively raising the minimum overseas employment/business track record to six months and limiting newly remote employees; applicants must show an employment contract or business registration proving work is based outside the UAE, an employer no-objection letter, comprehensive UAE health insurance and sometimes a police clearance certificate.",
            "EY New Zealand (ey.com) \u2014 'Practical immigration index for global digital nomads': digital nomads are workers employed and salaried in a home country but working digitally from a host country; generally not permitted to earn remuneration from the host country and usually required to hold a permit or visa designed for qualifying remote foreigners; the EY 2024 Mobility Reimagined Survey found employers and employees agree remote and hybrid work will persist, sustaining demand for globally agile working."
        ]),
        "diaspora_angle": "The digital nomad is a new kind of NRI \u2014 moving fluidly between countries on an Indian salary rather than emigrating for good \u2014 and as H-1B and student-to-work routes tighten, dozens of nomad-visa programmes (Estonia, UAE, Spain, Thailand and more) offer the Indian diaspora a flexible, lower-commitment way to live abroad without giving up their Indian base, even as India itself, the world's cheapest nomad destination, still offers no such visa.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-26 16:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (Passport/citizenship debate + Tharoor): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (India digital nomads): {'OK id=' + str(id2) if id2 else 'FAILED'}")
