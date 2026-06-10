#!/usr/bin/env python3
"""Post 4 Videshi articles to X with long-form posts and images."""

import json
import os
import sys
import time
import tempfile
import requests
import tweepy
from datetime import datetime, timezone

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            k, _, v = line.partition('=')
            env[k.strip()] = v.strip()
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]

SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# --- Tweepy setup ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Pre-composed posts ---
POSTS = [
    {
        "article_id": "3ff9cbff-c95f-4bf7-9a1a-955fdb350a14",
        "slug": "india-fertiliser-ministry-double-subsidy-iran-war-el-nino-food-crisis-20260610",
        "headline": "India's Fertiliser Ministry Wants to Double Its Subsidy Budget. The Fiscal Year Is Three Months Old.",
        "image_url": "https://images.pexels.com/photos/29039800/pexels-photo-29039800.jpeg?auto=compress&cs=tinysrgb&dpr=2",
        "text": """🇮🇳 NEWS | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

India Wants to Double Its Fertiliser Subsidy — And the Year Just Started

The fiscal year is barely three months old, and India's Department of Fertilisers has already asked the Finance Ministry to double its subsidy allocation. The request, first reported by Reuters, reveals how deeply the Iran war and the Strait of Hormuz blockade have disrupted India's agricultural supply chain. Urea, DAP, and potash prices are all surging, and New Delhi has already burned through ₹1.2 trillion ($12.6 billion) keeping fuel prices frozen.

The timing couldn't be worse. An El Niño pattern has pushed the southwest monsoon to an 18% deficit since its late arrival on June 4. Sea surface temperatures crossed the drought threshold on June 7, and every forecasting model points to continued warming. Sugar acreage is stagnating, carry-forward inventory is thinning, and the government just cancelled a planned export window. This is two crises converging — fiscal strain and a potential food security emergency — at exactly the same time.

For Indian households, the impact is direct. The fertiliser subsidy keeps farm input costs down, which keeps food affordable at the retail level. If the government can't absorb the shock, food inflation — already running hot — will accelerate further.

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ Fertiliser Ministry requests 2x subsidy allocation just 3 months into FY2026-27
▸ ₹1.2 trillion already spent keeping fuel prices frozen since the Iran war began
▸ Monsoon running at 18% deficit; El Niño threshold crossed on June 7
▸ Sugar exports cancelled as domestic buffer stock thins

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/india-fertiliser-ministry-double-subsidy-iran-war-el-nino-food-crisis-20260610

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    },
    {
        "article_id": "de21dfb4-d4e8-4f31-afac-135e60aaf474",
        "slug": "india-falls-seventh-global-stock-market-taiwan-south-korea-ai-foreign-outflows-20260610",
        "headline": "India Just Fell to Seventh in the Global Stock Market Rankings. AI Took Its Place.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
        "text": """🇮🇳 NEWS | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

India Slips to 7th in Global Stock Market Rankings — AI Did This

It happened quietly, in a matter of weeks. First Taiwan overtook India in total stock market capitalisation. Then South Korea. By early June, the world's fastest-growing major economy had slipped to seventh globally — behind the US, China, Japan, the UK, Taiwan, and South Korea. India's share in the MSCI Global Standard Index has contracted from a peak of 21% in September 2024 to just 12.3%.

The engine driving capital away is artificial intelligence. Taiwan's TSMC alone accounts for 40%+ of Taiwan's total market cap, posting $18 billion in Q1 net income — up 58% year-on-year. South Korea's Samsung and SK Hynix tell the same story. India has no equivalent. Its IT giants — Infosys, TCS, Wipro — are downstream integrators of AI, not the hardware providers that capture the investment flow. Foreign investors have pulled $26.4 billion from Indian equities in 2026, on pace to shatter last year's record outflow.

Not everyone is bearish. Some analysts argue India offers a "picks and shovels" play — power generation, cooling infrastructure, data centres — that underpins the broader AI ecosystem. But for now, the capital is chasing chips, not potential.

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ $26.4 billion in foreign outflows from Indian equities in 2026
▸ MSCI India weight down from 21% peak to 12.3%
▸ TSMC's Q1 net income: $18B (+58% YoY), dwarfing Indian IT
▸ Goldman Sachs upgraded Taiwan and South Korea last week

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/india-falls-seventh-global-stock-market-taiwan-south-korea-ai-foreign-outflows-20260610

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    },
    {
        "article_id": "4e89b47f-ab73-4949-8e85-b0db05a8f7ee",
        "slug": "us-cpi-inflation-three-year-high-may-2026-nri-impact-fed-rates-cost-of-living-20260610",
        "headline": "US Inflation Is About to Hit a Three-Year High. Every Indian Immigrant Should Pay Attention.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/84/Washington_D.C._-_Federal_Reserve_0001-0003_HDR.jpg",
        "text": """🇮🇳 NEWS | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

US Inflation About to Hit a 3-Year High — What It Means for Every NRI

Wednesday's CPI report is expected to show US consumer prices rose 4.2% year-on-year in May — the sharpest annual increase since April 2023 and the third straight month of acceleration. Monthly prices likely jumped 0.5%, following April's 0.6% surge. For 4.4 million Indian-born US residents, this isn't an abstract number. It's the gas bill, the grocery run, and the rent cheque.

The primary driver is energy. Gasoline surged 8.8% in May to $4.60 a gallon — up more than 50% since the Iran war triggered the Strait of Hormuz blockade in late February. Real wages have now declined for two consecutive months, meaning paychecks are shrinking in purchasing power even as nominal wages rise. This squeeze hits hardest in exactly the metros where Indian immigrants concentrate: the Bay Area, Seattle, New York, New Jersey, Dallas-Fort Worth, and the D.C. suburbs.

The Fed is boxed in. Markets are now pricing in the possibility of a rate hike — a dramatic reversal from the cuts investors expected six months ago. A hike would tighten mortgage rates further, hitting H-1B holders and green card applicants who are already navigating the most expensive housing market in a generation.

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ May CPI forecast: 4.2% YoY — highest since April 2023
▸ Gas prices up 50%+ since Iran war began; $4.60/gallon national average
▸ Real wages falling for 2nd consecutive month
▸ Markets now pricing in a potential Fed rate hike, not cuts

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/us-cpi-inflation-three-year-high-may-2026-nri-impact-fed-rates-cost-of-living-20260610

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    },
    {
        "article_id": "b45cc0a6-b57a-409a-8c66-6be65343b98a",
        "slug": "ecb-reschedules-england-india-t20i-timings-indian-viewership-financial-dependence-nri",
        "headline": "England Moved the Start Times. India's TV Audience Was the Reason.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Edgbaston_Cricket_Ground_2012.jpg/1280px-Edgbaston_Cricket_Ground_2012.jpg",
        "text": """🏏 SPORTS | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

England Shifted the Start Times. India's Viewers Were the Reason.

Three of five England-India T20I matches will now start at 5:30 PM local instead of 6:30 PM. The change — negotiated between the ECB, Sky Sports, and Sony Sports Network — was made for one reason: to catch Indian viewers at 10 PM IST rather than 11 PM, before they switch off for the night. It's a small adjustment that says the quiet part out loud.

The ECB's own financial report spells it out: England cricket's revenues are "inherently cyclical, reflecting the scheduling of high-value broadcast series by opposition." The board expects a profit this year — the year India tours. It expects losses in 2027, when Australia visits for the Ashes. The home of cricket loses money hosting its oldest rivalry and makes money hosting India. That's the modern economics of the sport.

The tour is already a sellout. All three ODI venues — Chester-le-Street, Manchester, the Oval — are gone. Only a few hundred T20I seats remain. Rohit Sharma and Virat Kohli are expected for the ODIs, while 15-year-old IPL sensation Vaibhav Sooryavanshi could make his international debut. Even the Ireland leg — two T20Is in Belfast — is sold out.

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ 3 of 5 T20Is moved to 5:30 PM local (10 PM IST) for Indian prime time
▸ ECB financial report projects profit for India tour, losses for 2027 Ashes
▸ All 3 ODIs sold out; Kohli and Rohit Sharma expected to feature
▸ 15-year-old Vaibhav Sooryavanshi could make his international debut

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/ecb-reschedules-england-india-t20i-timings-indian-viewership-financial-dependence-nri

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    },
]


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
            stream=True,
        )
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "")
        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "webp" in ct:
            ext = ".webp"
        elif "gif" in ct:
            ext = ".gif"
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in r.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        fsize = os.path.getsize(tmp.name)
        if fsize < 1000:
            print(f"  Image too small ({fsize} bytes), skipping image.")
            os.unlink(tmp.name)
            return None
        print(f"  Downloaded image: {fsize:,} bytes")
        return tmp.name
    except Exception as e:
        print(f"  Image download failed: {e}")
        return None


def upload_media(img_path):
    """Upload image to X via v1.1 API."""
    try:
        media = api_v1.media_upload(filename=img_path)
        print(f"  Media uploaded: media_id={media.media_id}")
        return media
    except Exception as e:
        print(f"  Media upload failed: {e}")
        return None


# --- Tweet log ---
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
tweet_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        tweet_log = json.load(f)

posted = 0
errors = []
results = []

for i, post in enumerate(POSTS):
    print(f"\n{'='*60}")
    print(f"Article {i+1}/{len(POSTS)}: {post['headline'][:80]}")
    print(f"{'='*60}")

    # Download and upload image
    media_ids = None
    img_path = download_image(post["image_url"])
    if img_path:
        media = upload_media(img_path)
        if media:
            media_ids = [media.media_id]
        try:
            os.unlink(img_path)
        except:
            pass

    # Post tweet
    try:
        kwargs = {"text": post["text"]}
        if media_ids:
            kwargs["media_ids"] = media_ids
        response = client.create_tweet(**kwargs)
        tweet_id = response.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted! {tweet_url}")
        results.append({"slug": post["slug"], "tweet_url": tweet_url, "status": "ok"})

        # Update Supabase
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{post['article_id']}",
            headers=SB_HEADERS,
            json={"tweeted_at": now_utc},
            timeout=15,
        )
        if patch_resp.status_code < 300:
            print(f"  Supabase updated: tweeted_at={now_utc}")
        else:
            print(f"  Supabase update failed: {patch_resp.status_code} {patch_resp.text}")

        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": post["article_id"],
            "slug": post["slug"],
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "w") as f:
            json.dump(tweet_log, f, indent=2)

        posted += 1

    except Exception as e:
        err_msg = str(e)
        print(f"  ❌ Tweet failed: {err_msg}")
        errors.append({"slug": post["slug"], "error": err_msg})
        results.append({"slug": post["slug"], "status": "error", "error": err_msg})

    # Wait between posts (skip after last)
    if i < len(POSTS) - 1:
        print("  Waiting 30 seconds...")
        time.sleep(30)

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY: {posted}/{len(POSTS)} posted, {len(errors)} errors")
print(f"{'='*60}")
for r in results:
    if r["status"] == "ok":
        print(f"  ✅ {r['slug'][:60]} → {r['tweet_url']}")
    else:
        print(f"  ❌ {r['slug'][:60]} → {r['error'][:80]}")
