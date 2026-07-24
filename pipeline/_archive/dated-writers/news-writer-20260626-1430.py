#!/usr/bin/env python3
"""
Videshi News Writer — June 26, 2026 (14:30 UTC / 07:30 PDT run)
2 NEW articles, dedup-checked against last ~150 articles:
  1. Texas escalates H-1B enforcement beyond the federal level — "ghost
     office" probes, Paxton civil investigative demands, a House committee
     review, and the standing freeze on state-agency/university petitions
     through May 2027. State-level angle is NOT covered (federal H-1B fee,
     lottery, OPT bill are covered; Texas state action is not).
  2. Pax Silica II — 35 nations including India sign the Joint Statement on
     AI Opportunity in Washington (June 25); India deepens chip/AI/critical-
     minerals cooperation with the US. NOT covered.
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


# ─── Article 1: Texas escalates H-1B enforcement ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Texas H-1B enforcement escalation")
    print("="*60)

    slug = "texas-h1b-enforcement-ghost-offices-paxton-investigation-abbott-freeze-indian-workers-20260626"
    headline = "Texas Is Building Its Own H-1B Crackdown — and Indian Workers Are Caught in the Middle"
    subheadline = "A state has no power to run the H-1B program. That hasn't stopped Texas. With 'ghost office' probes, subpoenas to employers, a legislative review and a freeze on state hiring that runs to 2027, the country's H-1B fight now has a second front \u2014 one squarely aimed at the industry Indians dominate."

    body = """For decades, the H-1B visa was a fight conducted entirely in Washington \u2014 in the halls of Congress, the rule-making of federal agencies, and the annual lottery run out of a USCIS server farm. No state had a role, because no state has any legal authority over who gets a work visa. That is still technically true. And yet Texas, the second-largest state in the country and one of the biggest users of skilled-worker visas, is methodically building something that looks a great deal like its own H-1B enforcement regime.

The campaign began in January, when reports surfaced of alleged H-1B "ghost offices" \u2014 businesses sponsoring unusually large numbers of visa applicants while showing little or no sign of actual commercial activity. For a state already primed to scrutinize immigration, the reports were a spark. What has followed is a coordinated, multi-pronged push that immigration lawyers say is unlike anything attempted at the state level before.

## Three Fronts, One Target

The first front is the executive. Governor Greg Abbott ordered all state agencies and public universities to freeze new H-1B petitions \u2014 a halt that runs through May 31, 2027, the end of the next legislative session. "State government must lead by example and ensure that employment opportunities, particularly those funded with taxpayer dollars, are filled by Texans first," Abbott wrote to agency heads. He has openly questioned why taxpayer-funded institutions need foreign workers at all.

The second front is legal. Attorney General Ken Paxton has issued civil investigative demands \u2014 effectively subpoenas \u2014 to employers suspected of misrepresenting their operations through nonexistent or nonoperational worksites, compelling them to hand over employee rosters, financial records and descriptions of the services they actually provide.

The third front is legislative. Texas House Speaker Dustin Burrows has directed a committee to investigate whether the state has enough visibility into how employers use the H-1B program to spot patterns that affect the Texas workforce or raise security concerns.

## The Limits \u2014 and the Real Leverage

Here is the catch that lawyers keep returning to: at a structural level, no state can administer or enforce the H-1B program itself. Texas cannot revoke a visa or block a federal petition outright. Its enforcement is confined to underlying business conduct under consumer-protection law, which does not require proving any immigration violation at all.

So the freeze, while dramatic, is narrow. It does not touch the private sector, where the overwhelming majority of Texas H-1B jobs sit. Among the top 25 Texas employers of approved H-1B workers in the latest fiscal year, state entities and universities accounted for only about 5% of the total; the rest went to private firms from Cognizant to Oracle to Tesla. The real bite of the state campaign, analysts say, is economic and political: civil demands, reporting mandates, and the threat of tying state and local incentives to new eligibility rules create uncertainty that can chill hiring well beyond what any single order accomplishes.

There is also a federal tailwind. A US Department of Homeland Security rule has already restructured the H-1B lottery so that higher-wage petitions get better odds, and Congress is weighing the bipartisan H-1B and L-1 Visa Reform Act. The Texas actions don't create new legal authority, but they add momentum to a "fraud and abuse" framing that is increasingly shaping the national debate.

## Why It Matters for the Diaspora

Indians receive roughly seven in ten H-1B visas issued each year, which means any squeeze on the program lands first and hardest on Indian professionals \u2014 and Texas is now home to one of the largest and fastest-growing Indian communities in America, concentrated in the tech corridors of Austin, Dallas and Houston. The state's public universities and medical centers, from the University of Texas to MD Anderson, employ hundreds of H-1B holders, many of them Indian researchers and physicians who now face a wall when their petitions come up for renewal. "The people will have to go home, or have to leave or find a job in another state," one Austin immigration attorney warned.

The deeper worry is contagion. Florida has pursued a similar pause for its public universities, and if a "Texans first" model spreads to other states, the diaspora could face a patchwork of local restrictions layered on top of an already tightening federal system. For an Indian family weighing a job offer in Texas, a green-card timeline that already stretches decades, and a child's school year that hangs on a visa stamp, the message from Austin is unsettling: the H-1B fight is no longer only in Washington. It has come to the statehouse."""

    topic = "Texas H-1B visa Abbott immigration"
    img_url = fetch_wikipedia_summary_image("Greg_Abbott")
    img_attribution = "Wikimedia Commons"
    img_caption = "Texas Governor Greg Abbott, who has frozen new H-1B petitions by state agencies and universities through May 2027"
    if not img_url:
        img_url, _ = pick_commons(["Greg Abbott governor", "Texas State Capitol", "Texas capitol Austin"], headline, topic)
    if not img_url:
        px = fetch_pexels_image("texas state capitol austin")
        if px:
            img_url = px; img_attribution = "Pexels"
            img_caption = "Texas is escalating its scrutiny of the H-1B visa program used heavily by Indian professionals"

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
            "Bloomberg Law (news.bloomberglaw.com, 25 June 2026) \u2014 'Texas Pushes H-1B Enforcement Beyond the Federal Status Quo': in January, reports of alleged H-1B 'ghost offices' (fraudulent businesses sponsoring unusually high numbers of applicants with little commercial activity) prompted state actions; Gov. Greg Abbott ordered all state agencies to halt H-1B applications for state employees through May 2027; AG Ken Paxton issued civil investigative demands to employers suspected of misrepresenting operations through nonexistent worksites, compelling employee rosters, financial information and service descriptions; House Speaker Dustin Burrows directed a legislative committee to investigate state visibility into employer H-1B use; no state has authority to administer or enforce the H-1B program itself; state enforcement limited to business conduct under consumer-protection law; Congress considering the bipartisan H-1B and L-1 Visa Reform Act of 2025; a DHS final rule restructured the lottery so higher-wage petitions get better odds.",
            "Bloomberg Law / Bloomberg Tax (news.bloomberglaw.com, Jan 2026) \u2014 'Texas Governor Halts H-1B Hiring at State Colleges, Agencies': Abbott ordered state agencies and public universities to immediately freeze new H-1B petitions; halt lasts through May 31, 2027 (end of next legislative session); does not affect private-sector companies; among the top 25 Texas H-1B employers, state entities including universities accounted for ~5% of the total, with most going to private firms such as Cognizant, Oracle and Tesla; major public users include the University of Texas and Texas A&M; at-risk facilities include UT Southwestern Medical Center and MD Anderson Cancer Center, which together employ hundreds of H-1B holders.",
            "Reuters (reuters.com, 27 Jan 2026) \u2014 'Texas governor halts new H-1B visa petitions by state agencies, public universities': Abbott directed agencies and universities to suspend new petitions and ordered an investigation; freeze lasts until May 31, 2027 with exceptions via Texas Workforce Commission permission; agencies given until March 27, 2026 to report petition counts, sponsored visa holders, countries of origin and job classifications; H-1B program offers 65,000 visas annually plus 20,000 for advanced-degree holders; Florida's Board of Governors separately sought to pause H-1B visas for public universities until January 2027; Trump imposed a $100,000 one-time fee for new H-1B applicants.",
            "The Texas Tribune / KPRC (Jan-Feb 2026) \u2014 'Texas has stopped state agencies and universities from filing new H-1B visa applications. Here's what that means.': experts say affected employees are a small but crucial share of the workforce in specialized roles difficult to source domestically; Austin immigration attorney Faye Kolly (McChesney Kolly) warned 'The people will have to go home, or have to leave or find a job in another state' and that state institutions will struggle to recruit; Abbott said in a radio interview he saw no reason for foreign workers at taxpayer-funded institutions."
        ]),
        "diaspora_angle": "Indians receive roughly 70% of H-1B visas, so Texas's new state-level enforcement \u2014 'ghost office' probes, AG subpoenas, a legislative review and a freeze on state and university hiring through May 2027 \u2014 lands first on Indian tech workers, researchers and physicians in the booming Austin-Dallas-Houston diaspora corridors, and threatens to spread a 'Texans first' patchwork of local restrictions on top of an already tightening federal H-1B system.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ─── Article 2: Pax Silica II — India + 34 nations sign AI Opportunity statement ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Pax Silica II AI summit")
    print("="*60)

    slug = "india-pax-silica-summit-washington-ai-opportunity-statement-35-nations-semiconductor-supply-chain-20260626"
    headline = "India Joins 34 Nations in Washington to Pick a Side in the Coming AI Order"
    subheadline = "At the second Pax Silica Summit, 35 countries signed a Joint Statement on AI Opportunity \u2014 a 'build first' manifesto for chips, compute and critical minerals. For a diaspora that already runs much of Silicon Valley, India's seat at the table is more than symbolic."

    body = """The contest to shape the artificial-intelligence era is increasingly being framed as a choice between two philosophies: regulate first, or build first. In Washington on Thursday, thirty-five nations \u2014 India among them \u2014 made their preference explicit, signing a Joint Statement on AI Opportunity at the second Pax Silica Summit and aligning behind what its organizers called a "pro-growth, pro-innovation" approach to the technology that will define the next century.

"The future of AI will not be determined by who regulates first," said Jacob Helberg, the US Under Secretary of State for Economic Affairs, who has become the initiative's most visible champion. "It will be determined by who builds first and builds the most capacity. More energy. More compute. More chips. More talent. More builders."

## What Pax Silica Is

Pax Silica is a US-led coalition aimed at building "trusted and resilient" supply chains for the hardware that powers AI \u2014 from the critical minerals dug out of the earth, to the silicon wafers fabricated in clean rooms, to the data centers where frontier models are trained and deployed. The name borrows from Pax Romana and Pax Britannica: the idea of an order held together, in this case, by who controls the silicon stack rather than by armies or navies.

At this second summit, the coalition widened considerably. Argentina, Germany, the Netherlands, Chile, Costa Rica, Greece, Kazakhstan, Panama and the European Union all joined on the sidelines, lending the bloc both industrial heft (the Dutch are home to the world's most advanced chip-equipment maker) and geographic spread. The underlying message is a pointed one: a refusal of what Helberg has elsewhere called "weaponized dependency" \u2014 shorthand for over-reliance on Chinese supply chains.

## India's Hand

India was represented by S Krishnan, Secretary of the Ministry of Electronics and Information Technology, alongside Nagaraj Naidu, Additional Secretary (Americas) at the Ministry of External Affairs, and a contingent of Indian industry. The delegation used the summit to push collaboration on semiconductors, AI and resilient technology supply chains, and the timing dovetails with a separate closed-door India-US roundtable, convened by the Indian Embassy with the US-India Strategic Partnership Forum, that brought officials and executives together on chips, critical minerals and AI. "Securing the foundations of AI together," the embassy posted.

India arrives with a genuine, if still nascent, hand to play. Through the India Semiconductor Mission, the country is trying to build an end-to-end chip ecosystem \u2014 design, fabrication, packaging, testing \u2014 rather than merely assemble imported parts. New Delhi reportedly plans to disburse around 71 billion rupees in fresh semiconductor incentives in fiscal 2027, ten chip plants are said to be underway, and Indian engineers already make up a striking share of the world's semiconductor designers. That last fact is the country's strongest card: in chips as in software, India's comparative advantage is talent.

## The Skeptic's Footnote

For all the soaring rhetoric, a joint statement is not a treaty. It binds no one to specific spending, timelines or technology transfers, and "pro-innovation" coalitions can dissolve as quickly as they form when commercial interests diverge. India, in particular, guards its strategic autonomy jealously and has resisted being slotted into any single bloc; signing a statement on AI opportunity is a long way from surrendering policy independence. The hard work \u2014 actually building fabs, securing mineral supply, and turning design talent into manufactured product \u2014 lies ahead, and India has missed semiconductor targets before.

## Why It Matters for the Diaspora

Few communities are as woven into the AI story as the Indian diaspora. Indian-origin executives run Google, Microsoft and a long list of the chip and cloud firms whose fortunes ride on exactly the supply chains Pax Silica is trying to secure. Indian engineers fill the design teams in Silicon Valley, Austin and Bengaluru alike. So when India formally aligns with a US-led technology bloc, it is not an abstraction for the diaspora \u2014 it is a development that touches their employers, their visas, and the cross-border careers many of them have built between the two countries.

A tighter India-US technology axis could mean more chip investment flowing both ways, deeper research ties, and \u2014 diaspora professionals will hope \u2014 a counterweight to the immigration headwinds buffeting Indian talent in America. It could also pull Indian engineers into a more openly contested geopolitical project, with all the export controls and security reviews that entails. Either way, the seat India took in Washington on Thursday signals where it intends to stand as the AI order is built. For a diaspora that helped build the last technology era, the next one is now being negotiated in rooms where, increasingly, Indians are on both sides of the table."""

    topic = "semiconductor chip AI India United States supply chain"
    img_url, _ = pick_commons([
        "semiconductor wafer fabrication clean room",
        "silicon wafer manufacturing",
        "integrated circuit chip macro",
        "data center servers",
    ], headline, topic)
    img_attribution = "Wikimedia Commons"
    img_caption = "A semiconductor wafer; India joined 34 nations in signing the Joint Statement on AI Opportunity at the Pax Silica Summit"
    if not img_url:
        px = fetch_pexels_image("semiconductor chip wafer technology")
        if px:
            img_url = px; img_attribution = "Pexels"
            img_caption = "India has aligned with a US-led bloc to secure chip and AI supply chains at the Pax Silica Summit"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Hindu BusinessLine (thehindubusinessline.com, 25-26 June 2026) \u2014 '35 nations, including India, sign statement on AI opportunity at Pax Silica Summit in US': at the second Pax Silica Summit in Washington on Thursday June 25, 2026, 35 nations signed the Joint Statement on AI Opportunity, aligning behind a 'pro-growth, pro-innovation' regulatory approach; US Under Secretary of State for Economic Affairs Jacob Helberg said it was 'a commitment to trusted supply chains, to mobilising the private sector, and the infrastructure that will power the next century'; Argentina, Germany, the Netherlands, Chile, Costa Rica, Greece, Kazakhstan, Panama and the EU joined on the sidelines; India represented by MeitY Secretary S Krishnan, MEA Additional Secretary (Americas) Nagaraj Naidu and Indian industry; delegation engaged on semiconductors, AI and resilient supply chains; Helberg: 'The future of AI will not be determined by who regulates first. It will be determined by who builds first and builds the most capacity. More energy. More compute. More chips. More talent. More builders.'",
            "The Indian EYE (theindianeye.com, 26 June 2026) \u2014 'India and US hold roundtable to build AI together': India and the US held a closed-door roundtable of senior officials and industry leaders to strengthen cooperation in AI, semiconductor supply chains and critical minerals; Indian Embassy posted 'Securing the foundations of AI together!'; Ambassador Vinay Mohan Kwatra, MeitY Secretary S Krishnan and US Deputy Under Secretary of Commerce Bill Guidera addressed Indian and US companies in chips, critical minerals and AI; organised by the Embassy with USISPF and Silverado Policy Accelerator; also attended by MEA Additional Secretary Nagaraj Naidu, USISPF President Mukesh Aghi and US DoE Deputy Assistant Secretary Christopher Saldana; discussions focused on shared investment barriers, durable demand signals and AI collaboration including frontier and application levels.",
            "DIGITIMES (apps.digitimes.com, 23-26 June 2026) \u2014 'News tagged South Asia': India reportedly plans to disburse INR71 billion in semiconductor incentives in fiscal 2027 to expand its local chip supply chain; Amazon announced an additional US$13 billion investment in India's AI and cloud infrastructure by 2030 on June 25; Teradyne expanding India presence with a new country manager.",
            "Press Information Bureau / Mirror Now (pib.gov.in, June 2026) \u2014 background on Pax Silica: India joined the US-led Pax Silica initiative securing AI and semiconductor supply chains; IT Minister Ashwini Vaishnaw noted ten semiconductor plants are underway and two-nanometre chips are being designed in India; US officials framed the coalition as rejecting 'weaponized dependency'; the India Semiconductor Mission aims to build an end-to-end ecosystem of design, manufacturing, packaging and testing, leveraging India's large base of chip-design engineers."
        ]),
        "diaspora_angle": "India joining 34 nations in signing the Joint Statement on AI Opportunity at the Pax Silica Summit deepens a US-India technology axis that runs straight through the diaspora \u2014 Indian-origin leaders run Google, Microsoft and major chip and cloud firms, and Indian engineers fill design teams from Silicon Valley to Bengaluru \u2014 promising more cross-border chip investment and research ties, a potential counterweight to immigration headwinds, but also pulling Indian talent into a more openly contested geopolitical project.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-26 14:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (Texas H-1B enforcement): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (Pax Silica II AI summit): {'OK id=' + str(id2) if id2 else 'FAILED'}")
