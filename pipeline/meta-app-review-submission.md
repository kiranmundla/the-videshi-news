# Meta App Review Submission — The Videshi Auto Post

## App Info
- **App Name:** The Videshi Auto Post
- **App ID:** 1225298439545084
- **Platform:** thevideshi.com (news publication)

---

## Permissions to Request

### 1. `instagram_content_publish`

**What this permission lets you do:**
Publish image posts, stories, and reels to our Instagram Business account (@the.videshi) programmatically via the Instagram Graph API.

**How our app uses this permission:**
The Videshi is an online news publication covering the Indian diaspora (thevideshi.com). We publish 30-50 news articles daily across categories including immigration, politics, sports, entertainment, and lifestyle. Our app automatically publishes select articles to our Instagram Business account to reach our audience on social media.

The workflow:
1. Our editorial system selects recently published articles from our database
2. For each article, it creates an image post using the article's editorial photo and a caption containing the headline
3. It publishes the post to our Instagram Business account (@the.videshi) using the Content Publishing API
4. The app posts to OUR OWN Instagram account only — it does not post to any third-party accounts

This is a first-party publishing tool for our own news publication, similar to how media companies like Reuters, BBC, or TechCrunch auto-publish articles to their social media accounts.

**Step-by-step instructions for the reviewer:**

1. Visit our website at https://www.thevideshi.com to see the news articles we publish
2. Visit our Instagram account @the.videshi to see the published posts — each post corresponds to an article on our website
3. The app creates a media container using POST /{ig-user-id}/media with image_url and caption
4. After processing, it publishes using POST /{ig-user-id}/media_publish with the creation_id
5. Each published Instagram post contains the article headline, a "link in bio" call-to-action, and relevant hashtags

**Screencast description (what to record — 30-60 seconds):**
- Open thevideshi.com, scroll through articles briefly
- Open Instagram app, show @the.videshi profile with published posts
- Show that each Instagram post matches an article on the website
- Show the Professional Dashboard confirming it's a Business account

---

### 2. `instagram_basic`

**What this permission lets you do:**
Read our Instagram Business account's profile information and media.

**How our app uses this permission:**
We use this permission to verify our Instagram Business account connection and read basic profile information (username, account ID) before publishing content. This is required for the content publishing workflow — we need to confirm the account is connected and retrieve the Instagram User ID to publish to.

**Step-by-step instructions for the reviewer:**

1. The app calls GET /me?fields=id,username to verify the connected Instagram account
2. This confirms the account is @the.videshi (ID: 28032566156343646)
3. The returned user ID is used in subsequent publishing API calls

---

## Verification Details

- **Business type:** Online news publication / media company
- **Website:** https://www.thevideshi.com
- **Instagram:** @the.videshi (Business account linked to "The Videshi" Facebook Page)
- **Facebook Page:** "The Videshi" (News & media website category)
- **Content type:** Original editorial journalism — news articles, not user-generated or scraped content
- **Posting frequency:** 3-6 posts per day to our own account
- **No third-party access:** This app only publishes to our own Instagram Business account. It is not a social media management platform and does not access any other users' accounts.

---

## Screen Recording Tips

Record a ~60 second screencast showing:

1. **Website** (10 sec): Open thevideshi.com, briefly show homepage with articles
2. **Instagram profile** (10 sec): Open @the.videshi in the Instagram app, show the published posts
3. **Match articles to posts** (15 sec): Show that an Instagram post headline matches an article on the website — tap into both to demonstrate
4. **Business account proof** (10 sec): Show Professional Dashboard or Settings → Account → Account type showing "Business"
5. **API call demo** (15 sec): Optional but helpful — show a terminal/Postman making a test API call to create a container and publish a post

Save as MP4, upload to the App Review form.
