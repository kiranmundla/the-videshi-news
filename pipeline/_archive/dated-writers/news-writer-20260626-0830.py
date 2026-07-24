#!/usr/bin/env python3
"""
Videshi News Writer — June 26, 2026 (08:30 UTC / June 26 01:30 PDT run)
2 NEW articles, dedup-checked against last ~30 news articles:
  1. FIIDS Capitol Hill Day — nearly 200 Indian American delegates from 25
     states visited 125+ Congressional offices on June 23, 2026, the largest
     diaspora legislative advocacy push to date. Five policy priorities.
     Reps. Krishnamoorthi and Subramanyam urged the community into politics.
     NOT covered (the "seat at the table" article was about Sriram Krishnan
     leaving the White House AI role — different topic).
  2. Australia's under-16 social media ban — six months in, a new BMJ study
     finds little effect; PM Albanese says he'll stress-test and toughen the
     law. India is now Australia's #1 foreign-born group (971,020), so the
     ban squarely affects Indian-Australian families with teenagers. NOT
     covered.
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


# ─── Article 1: FIIDS Capitol Hill Day ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: FIIDS Capitol Hill Day — 200 delegates")
    print("="*60)

    slug = "fiids-capitol-hill-day-2026-200-indian-american-delegates-125-congressional-offices-us-india-immigration-20260623"
    headline = "200 Indian Americans Just Walked Into 125 Congressional Offices in a Single Day"
    subheadline = "The fourth annual FIIDS Capitol Hill Day on June 23 was the largest diaspora advocacy push yet \u2014 delegates from 25 states pressed lawmakers on US-India ties, high-skilled immigration and critical minerals, while Indian American Congressmen urged the community to stop watching from the sidelines and run for office."

    body = """On the morning of June 23, nearly 200 Indian American delegates fanned out across Capitol Hill and, by day's end, had walked through the doors of more than 125 Congressional offices. It was the fourth annual Capitol Hill Day organised by the Foundation for India and Indian Diaspora Studies (FIIDS), and by the organisers' count it was the largest such legislative effort the community has ever mounted \u2014 a coordinated, state-by-state lobbying operation rather than a one-off photo line outside the Capitol.

The delegates came from 25 states, a spread meant to drive home that the Indian American story is no longer concentrated in a few coastal tech hubs. Their pitch to lawmakers and Congressional staff was organised around five priorities: deeper Indo-Pacific trade and security cooperation, the US-India strategic partnership, recognition of Indian American contributions and concerns, reform of high-skilled immigration programmes, and long-term security of critical minerals supply chains.

## Turning Numbers Into Influence

"This is a moment to translate influence into policy impact," said Khanderao Kand, FIIDS Chief of Policy and Strategy. "Indian Americans contribute across technology, research, academia, hospitality, health care, small business and agriculture, and our community is engaged in ensuring that Congress understands the issues that matter most to America's future."

That framing \u2014 influence into impact \u2014 captures what makes this year's effort different. The Indian American community is routinely described as among the most educated and prosperous in the United States, but affluence and electoral weight are not the same thing. FIIDS structured the day to convert the community's economic footprint into something a Congressional staffer can act on: specific asks, tied to bills and budget lines, delivered in person across both parties' offices on a single coordinated day.

The agenda also maps neatly onto Washington's own preoccupations. Critical minerals and Indo-Pacific security are at the centre of US strategic planning, and high-skilled immigration reform speaks directly to the H-1B and green-card backlogs that have dogged Indian professionals for years. By aligning their asks with concerns Congress already takes seriously, delegates gave themselves a better chance of being heard on issues the community cares about most.

## "A Seat at the Table"

The advocacy meetings were paired with pointed remarks from Indian American lawmakers, who used the gathering to deliver a blunter message: show up, or be left out. Congressman Raja Krishnamoorthi, the Illinois Democrat, told the gathering that despite the community's success, Indian Americans are "facing new challenges," pointing to a rise in "anti-Hindu, anti-Indian, anti-desi hate." He cited an incident in Texas where a group tore up an Indian flag and told people of Indian origin to "go back."

His prescription was political participation. "There's an old saying in Washington DC \u2014 if you don't have a seat at the table, you're on the menu," Krishnamoorthi said. "And none of you can afford to be on the menu, nor can our families, nor can our interests." He urged community members to run for office at every level, from city council to Congress, regardless of party: "I don't care if you're a Republican, Democrat, or Independent."

Congressman Suhas Subramanyam echoed the point, arguing that the most reliable way to address the community's concerns is to win seats in the rooms where decisions get made. The advocacy meetings were followed later in the day by the US-India Partnership Summit, which drew diplomats, elected officials and policy figures, including senior representatives from the State Department and the Embassy of India in Washington, to discuss the future of bilateral cooperation.

## Why It Matters for the Diaspora

For non-resident Indians watching from across the country and abroad, Capitol Hill Day is a marker of how the community is maturing politically. For decades, diaspora engagement with Washington ran largely through fundraising and the occasional cultural celebration. A 200-strong, multi-state delegation methodically working 125 offices in a day signals a shift toward sustained, organised advocacy \u2014 the kind of presence that lobbies for visas, trade terms and protection from hate as a matter of routine, not just in moments of crisis.

It also raises the stakes of the lawmakers' challenge. The issues most felt by the diaspora \u2014 immigration backlogs, the safety of families amid rising hostility, the strength of the US-India relationship \u2014 are precisely the ones that move faster when the community has its own people inside the institutions making the rules. The message from this year's gathering was that turning out for one day on the Hill is a start, and the next step is to keep showing up, and increasingly, to run."""

    img_url, ititle = pick_commons([
        "United States Capitol west front",
        "United States Capitol building",
        "United States Capitol dome",
        "US Capitol Washington",
        "United States Capitol"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "The United States Capitol. Nearly 200 Indian American delegates visited more than 125 Congressional offices during the fourth annual FIIDS Capitol Hill Day on June 23, 2026"

    if not img_url:
        px = fetch_pexels_image("united states capitol building washington")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Indian American delegates pressed lawmakers across more than 125 Congressional offices on June 23, 2026"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Nation Press (nationpress.com, 23 June 2026) \u2014 'Indian Americans descend on Capitol Hill with US-India agenda, 200 delegates from 25 states': nearly 200 Indian American delegates from 25 states visited 125+ Congressional offices on Tuesday 23 June for the fourth annual FIIDS Capitol Hill Day, the largest such advocacy effort to date; five priority areas (Indo-Pacific trade and security, US-India strategic partnership, Indian American contributions and concerns, high-skilled immigration reform, critical minerals supply-chain security); Khanderao Kand, FIIDS Chief of Policy and Strategy, quoted on translating influence into policy impact.",
            "IndiaWest (indiawest.com, ~20 June 2026) \u2014 'Indian Americans Take Priorities To Capitol Hill': nearly 200 delegates from 25 states set to meet lawmakers and Congressional staff on June 23 to advocate for stronger US-India ties, immigration reform, Indo-Pacific security and critical minerals supply-chain resilience; visits to 125+ congressional offices; followed by the US-India Partnership Summit later on June 23 with speakers including Bethany Morrison, Deputy Assistant Secretary of State, and Ambassador Mangya Khampa, Deputy Chief of Mission at the Embassy of India in Washington.",
            "The Hindu BusinessLine / Connected to India (thehindubusinessline.com, connectedtoindia.com, 24 June 2026) \u2014 'Indian-American lawmakers urge diaspora to enter politics amid rise in anti-India sentiment' / 'Get a seat at the table, so you don't end up on the menu': at the FIIDS Capitol Hill event, Congressman Raja Krishnamoorthi (D-Illinois) cited a rise in 'anti-Hindu, anti-Indian, anti-desi hate' (including a Texas incident where an Indian flag was torn up) and urged Indian Americans to run for office at all levels regardless of party, using the 'seat at the table / on the menu' line; Congressman Suhas Subramanyam echoed the call for representation in decision-making bodies."
        ]),
        "diaspora_angle": "The fourth annual FIIDS Capitol Hill Day on June 23, 2026 \u2014 nearly 200 Indian American delegates from 25 states working more than 125 Congressional offices in a single day \u2014 marks the diaspora's largest and most organised legislative advocacy push yet, pressing Washington on US-India ties, high-skilled immigration reform and critical minerals, while Indian American lawmakers urged the community to convert its economic weight into political power by running for office.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Australia's under-16 social media ban ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Australia under-16 social media ban, 6 months in")
    print("="*60)

    slug = "australia-under-16-social-media-ban-six-months-albanese-toughen-bmj-study-indian-australian-families-20260626"
    headline = "Australia's Under-16 Social Media Ban Isn't Working Yet \u2014 and Indian-Australian Families Have a Big Stake in What Happens Next"
    subheadline = "Six months after the world-first ban took effect, a new study finds teen use is little changed, and Prime Minister Anthony Albanese says he will toughen enforcement. With India now Australia's single largest source of migrants, the policy lands squarely on hundreds of thousands of diaspora households raising teenagers."

    body = """Six months ago, Australia did something no other country had tried: it banned children under 16 from holding accounts on the major social media platforms, putting the legal burden squarely on Instagram, YouTube, TikTok, Snapchat, X and others to keep young teenagers off their services. On Friday, Prime Minister Anthony Albanese signalled that the experiment is not delivering what he wanted \u2014 and that he intends to make the law tougher.

"What we want to do is to make sure that the laws are as strong as possible and that they will withstand any legal challenges which are made," Albanese told the Australian Broadcasting Corporation, adding that a key focus would be ensuring the eSafety Commission, the country's internet regulator, is "sufficiently empowered to do the job." The comments followed a new study, published in the *BMJ*, which found that the measure \u2014 now six months old \u2014 has had little early effect on how much time teenagers actually spend on social media.

## A Bold Law, A Quiet Reality

When the ban went live last December, the early numbers looked dramatic. The eSafety Commissioner reported that platforms had deactivated roughly 4.7 million accounts belonging to under-16s in the first month alone, with Meta saying it removed some 550,000 underage accounts from Instagram, Facebook and Threads. It read like a swift, sweeping success.

The lived reality has been messier. The new research describes a period "characterized by limited implementation, incomplete compliance, and substantial circumvention," with parents and researchers alike reporting that teen social media use is little changed. Teenagers have found their way around the controls, and the platforms' age-assurance systems \u2014 some using AI to estimate age from photos, others asking users to upload government ID \u2014 have proven leaky.

The enforcement architecture, on paper, is severe. Companies that fail to take "reasonable steps" to weed out underage users face fines of up to A$49.5 million (about US$34 million). Crucially, the law penalises platforms, not parents or children. Australia has already accused Facebook, TikTok and YouTube of falling short of their obligations, and Communications Minister Anika Wells has been pointed: "Australia's world-leading social media laws are not failing. But big tech is failing to obey the laws." Reddit, for its part, has launched a High Court challenge to the ban, which remains in preliminary hearings.

## The World Is Watching \u2014 and Copying

Australia's law has become a template. Britain this month announced restrictions that go further still, extending to gaming and live-streaming platforms, while France, Spain and Norway have all weighed similar measures. That makes the Australian outcome a global test case: if the toughest-on-paper regime in the world struggles to change teen behaviour, governments everywhere will be recalibrating their own plans. Albanese's move to stress-test and strengthen the law is partly about making sure the policy survives the inevitable court fights and the platforms' warnings that bans simply push teenagers toward darker, unregulated corners of the internet.

## Why It Matters for the Diaspora

This is not a distant foreign-policy story for the Indian community \u2014 it is a household one. India is now the single largest source of Australia's overseas-born residents, overtaking England for the first time since records began in 1891. As of mid-2025, about 971,000 Australians were born in India, a figure that jumped by 55,000 in a single year and now makes up 3.5 per cent of the country's population. Layer in the Australian-born children of those migrants, and you have an enormous cohort of diaspora families raising exactly the teenagers this law is designed to govern.

For many of those parents, the ban arrived as a kind of relief \u2014 outside validation for the screen-time battles already being fought at the dinner table. But the gap between the law's promise and its results leaves them in an uncomfortable spot. They cannot assume the platforms or the regulator will do the policing for them, and a tougher enforcement regime may soon mean more aggressive age checks, including ID and facial-estimation tools that raise their own privacy questions for families wary of handing over documents.

There is a sharper edge, too. The same period that saw this migration surge has also seen a documented rise in anti-migrant sentiment, with Indian communities reporting they feel specifically targeted at anti-immigration rallies. For diaspora parents, that adds urgency to the online-safety debate: keeping teenagers safe is not only about screen time but about what they are exposed to online. As Albanese moves to harden the law, Indian-Australian families are among those with the most direct stake in whether the second attempt works better than the first."""

    img_url, ititle = pick_commons([
        "Teenager using smartphone",
        "Smartphone social media apps",
        "Person holding smartphone apps",
        "Mobile phone social media icons",
        "Teenagers mobile phones"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "Australia's world-first ban bars under-16s from holding accounts on major social media platforms. A new study finds teen use is little changed six months in"

    if not img_url:
        px = fetch_pexels_image("teenager using smartphone social media apps")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Australia's under-16 social media ban is six months old; the government plans tougher enforcement"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters (reuters.com, 26 June 2026) \u2014 'Australia considers tougher enforcement of social media ban for teens': PM Anthony Albanese said on Friday he wants the under-16 social media ban as strong as possible and able to withstand legal challenges, with a focus on empowering the eSafety Commission; a new study found the six-month-old measure had little impact on teen use; the law bans platforms including Meta's Instagram and Google's YouTube from giving under-16s accounts; eSafety and Communications Minister Anika Wells preparing legal action against multiple platforms facing fines up to A$49.5 million (US$34 million); Reddit has launched a High Court challenge; ~4.7 million teen accounts were reported deactivated in the first month after the December 10, 2025 start.",
            "Phys.org / AFP citing BMJ (phys.org, 25 June 2026) \u2014 'Australia's under-16 social media ban shows little early effect on teen use: Research': BMJ study (Andy Burrows, DOI 10.1136/bmj-2026-100046) describes 'limited implementation, incomplete compliance, and substantial circumvention'; tech companies face fines up to A$49.5 million; Australia in March accused Facebook, TikTok and YouTube of failing obligations; Minister Anika Wells: 'Australia's world-leading social media laws are not failing. But big tech is failing to obey the laws'; platforms using AI age-estimation and government ID checks; minimum-age rule applies to YouTube, TikTok, Snapchat, X, Instagram, Facebook.",
            "Australian Bureau of Statistics / AAP (abs.gov.au, aapnews.aap.com.au, ~29 April 2026) \u2014 'Australia's population by country of birth, Jun 2025' / 'England overtaken as top migrant source for first time': India became the largest source of Australia's foreign-born residents, overtaking England for the first time since records began in 1891; India-born population rose by 55,000 to 971,020 at 30 June 2025, 3.5% of the total; overseas-born population reached a record 8.8 million (32%); report notes a rise in anti-migrant sentiment with Indian migrants feeling specifically targeted at anti-immigration rallies."
        ]),
        "diaspora_angle": "Six months after Australia's world-first ban on under-16 social media accounts, a new BMJ study finds teen use is little changed and PM Albanese is moving to toughen enforcement \u2014 a debate that lands directly on the diaspora, since India is now Australia's single largest source of migrants (971,020 India-born, up 55,000 in a year), meaning hundreds of thousands of Indian-Australian households raising teenagers have a direct stake in whether the law works and in the privacy trade-offs of stricter age checks.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-26 08:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (FIIDS Capitol Hill Day): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (Australia under-16 social media ban): {'OK id=' + str(id2) if id2 else 'FAILED'}")
