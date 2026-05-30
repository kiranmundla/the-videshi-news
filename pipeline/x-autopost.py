#!/usr/bin/env python3
"""Post Videshi articles to X as long-form Premium posts with images."""

import tweepy
import requests
import json
import os
import time
import tempfile
from datetime import datetime

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

# Load env files
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

sb_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# --- Tweepy clients ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Composed posts ---
posts = [
    {
        "article_id": "7c2b6722-102d-4d7b-8c59-edb8fe860046",
        "slug": "india-defence-secretary-shangri-la-bilateral-netherlands-australia-eu-indo-pacific-20260530",
        "image_url": "https://images.pexels.com/photos/36228703/pexels-photo-36228703.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "text": """🇮🇳 NEWS | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

India Ran Five Back-to-Back Defence Bilaterals at Shangri-La — Here's What Each One Delivered

India's Defence Secretary Rajesh Kumar Singh turned the sidelines of the 2026 Shangri-La Dialogue in Singapore into a full diplomatic sprint, holding five separate bilateral meetings in a single day with counterparts from the Netherlands, Australia, the EU, and other Indo-Pacific partners.

The engagements signal New Delhi's push to deepen military ties well beyond its traditional strategic circle — and they come at a moment when China's defence minister was conspicuously absent from the forum for the second consecutive year. With the Netherlands, Singh explored defence industrial collaboration, particularly around naval systems and cybersecurity. With Australia, both sides reviewed the Comprehensive Strategic Partnership and identified new areas for cooperation under the Quad framework.

The EU discussions focused on military interoperability — a natural fit as India courts European defence technology from fighter jets to secure communications. Earlier on Friday, Singh had addressed think tanks on India's defence innovation push, positioning the country as both a security provider and a manufacturing partner in the Indo-Pacific.

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ 5 bilateral meetings in one day at Asia's biggest defence forum
▸ Netherlands talks focused on naval systems and cybersecurity collaboration
▸ Australia's Defence Minister Richard Marles scheduled to visit India next
▸ China's defence minister absent from Shangri-La for the second straight year

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/india-defence-secretary-shangri-la-bilateral-netherlands-australia-eu-indo-pacific-20260530

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    },
    {
        "article_id": "11fba57b-8da0-41ab-a0ed-3a79fa655f35",
        "slug": "newark-delaney-hall-ice-detention-standoff-nj-state-police-immigration-enforcement-nri-20260530",
        "image_url": "https://images.pexels.com/photos/35108457/pexels-photo-35108457.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "text": """🇮🇳 NEWS | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

A Newark Detention Standoff Is Rewriting Immigration Enforcement Rules — And Legal Immigrants Are Paying Attention

A hunger strike by detained immigrants at Newark's Delaney Hall has escalated into one of the most significant state-vs-federal confrontations over immigration enforcement in the Trump era. New Jersey Governor Mikie Sherrill ordered state police to take control of the area outside the 1,000-bed GEO Group facility after confrontations between protesters and ICE agents turned violent — pepper spray deployed, one protester's foot caught under a truck wheel, and the FBI arresting an individual for threatening an ICE officer's family.

State troopers have now set up protected protest zones and vehicle checkpoints, with ICE agents withdrawing from the immediate perimeter. "We know what ICE has done in other states and that American citizens have lost their lives," Sherrill said, demanding the facility's closure entirely. DHS Secretary Markwayne Mullin pushed back, insisting conditions meet standards.

For the Indian diaspora — particularly those on H-1B, L-1, and other legal pathways — the standoff is a bellwether. When enforcement infrastructure expands and due process questions multiply at facilities holding people without clear legal resolution, the anxiety ripples well beyond the undocumented population.

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ NJ governor deployed state police after escalating violence outside the facility
▸ FBI arrested one protester for threats against an ICE officer's family
▸ Dueling pro-ICE and anti-ICE rallies expected Saturday — state police managing both
▸ Legal immigrants on work visas watching closely as enforcement debates intensify

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/newark-delaney-hall-ice-detention-standoff-nj-state-police-immigration-enforcement-nri-20260530

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    },
    {
        "article_id": "5c057290-44a3-4275-ba8b-73914c9b02a9",
        "slug": "sebi-fines-suzlon-energy-15-crore-financial-misreporting-chairman-penalty-20260530",
        "image_url": "https://images.pexels.com/photos/14902194/pexels-photo-14902194.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "text": """🇮🇳 NEWS | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

SEBI Slaps Suzlon Energy with ₹15.95 Crore Penalty — Chairman and Vice-Chairman Hit with Personal Fines Too

India's market regulator has dropped the hammer on Suzlon Energy. SEBI imposed a ₹15.95 crore ($1.68 million) penalty on the renewable energy giant for what it called serious lapses in financial disclosures — transactions with subsidiaries that inflated the company's net worth and "created a false picture of financial strength affecting market integrity."

But the regulator didn't stop at the corporate entity. Suzlon's chairman received a personal penalty of ₹5.75 crore and the vice-chairman ₹5.45 crore, on charges that they presided over the misreporting. The timing is awkward: Suzlon had spent years rehabilitating itself after defaulting on bonds in 2012, and its stock surged fivefold from 2020 lows as India's 500 GW renewable energy target gave the company a second life.

Now the SEBI order reopens uncomfortable questions. If the disclosures during the period under review were unreliable, investors will want to know whether the more recent numbers — the ones that powered that stock rally — can be trusted either.

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ ₹15.95 crore corporate penalty + personal fines for chairman (₹5.75 Cr) and vice-chairman (₹5.45 Cr)
▸ SEBI found subsidiary transactions inflated net worth, misleading investors
▸ Suzlon stock had surged 5x from 2020 lows during its recovery — now under fresh scrutiny
▸ Part of a broader SEBI enforcement wave (NDTV cleared in a separate case same day)

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/sebi-fines-suzlon-energy-15-crore-financial-misreporting-chairman-penalty-20260530

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    },
    {
        "article_id": "39713256-77dc-4df9-a29d-42fc4f37e975",
        "slug": "supreme-court-vinesh-phogat-asian-games-2026-trials-sports-judiciary-warning-20260530",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/da/Vinesh_Phogat.jpg",
        "text": """🇮🇳 NEWS | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

Supreme Court Clears Vinesh Phogat for Asian Games Trials — Then Tells All Courts to Stay Out of Sports

The Supreme Court on Friday gave Vinesh Phogat the green light to compete in the 2026 Asian Games selection trials, ending weeks of legal limbo — but the bench wasn't done. In some of the sharpest judicial commentary on sports governance in recent memory, Justice PS Narasimha warned that courts should not be dragged into competitive sporting decisions.

"This is not a medical college admission matter. These are national and international sporting events. Courts should not intervene in such cases in a manner that disrupts the entire schedule," the bench said. It told Phogat directly: "You are a brilliant athlete, but the nation comes first."

The ruling overturned a challenge by the Wrestling Federation of India, which had contested a Delhi High Court order permitting Phogat to enter the trials beginning May 30. For Phogat, it's the latest chapter in a career defined by extremes — Asian Games gold in 2018, the heartbreak of a 100-gram weight disqualification at the Paris 2024 Olympics, a brief stint in Haryana state politics, and now a return to the mat.

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ Vinesh Phogat cleared to compete in Asian Games 2026 selection trials starting May 30
▸ Supreme Court warned courts against "disrupting" sporting event schedules
▸ Wrestling Federation of India's challenge overturned
▸ Phogat returned to wrestling in early 2026 after resigning from Haryana state assembly

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/supreme-court-vinesh-phogat-asian-games-2026-trials-sports-judiciary-warning-20260530

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    },
]

# --- Post loop ---
results = []
log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")

for i, post in enumerate(posts):
    print(f"\n{'='*60}")
    print(f"Posting {i+1}/4: {post['slug'][:60]}...")
    
    # Download image
    media_id = None
    tmp_path = None
    try:
        img_resp = requests.get(post["image_url"], timeout=15)
        if img_resp.status_code == 200:
            suffix = ".jpg"
            if ".png" in post["image_url"]:
                suffix = ".png"
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix)
            with os.fdopen(tmp_fd, 'wb') as f:
                f.write(img_resp.content)
            media = api_v1.media_upload(filename=tmp_path)
            media_id = media.media_id
            print(f"  Image uploaded: media_id={media_id}")
        else:
            print(f"  Image download failed: {img_resp.status_code}")
    except Exception as e:
        print(f"  Image error (posting without): {e}")

    # Post tweet
    try:
        kwargs = {"text": post["text"]}
        if media_id:
            kwargs["media_ids"] = [media_id]
        response = client.create_tweet(**kwargs)
        tweet_id = response.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")

        # Update Supabase
        now_utc = datetime.utcnow().isoformat() + "Z"
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{post['article_id']}",
            headers=sb_headers,
            json={"tweeted_at": now_utc},
        )
        print(f"  Supabase update: {patch_resp.status_code}")

        # Log tweet
        tweet_log = {}
        if os.path.exists(log_path):
            with open(log_path) as f:
                tweet_log = json.load(f)
        tweet_log[str(tweet_id)] = {
            "article_id": post["article_id"],
            "slug": post["slug"],
            "posted_at": now_utc,
        }
        with open(log_path, "w") as f:
            json.dump(tweet_log, f, indent=2)

        results.append({"slug": post["slug"], "tweet_url": tweet_url, "status": "ok"})
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        results.append({"slug": post["slug"], "status": "error", "error": str(e)})
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    # Wait between posts
    if i < len(posts) - 1:
        print("  Waiting 30s...")
        time.sleep(30)

# --- Summary ---
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
ok = [r for r in results if r["status"] == "ok"]
err = [r for r in results if r["status"] == "error"]
print(f"Posted: {len(ok)}/{len(results)}")
for r in ok:
    print(f"  ✅ {r['tweet_url']}")
for r in err:
    print(f"  ❌ {r['slug']}: {r['error']}")
