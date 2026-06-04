# X Post Embeds — Writer Instructions

## When to Embed X Posts

Embed an X (Twitter) post in your article when **ALL** of these are true:
1. The article is about a specific person, organization, or event that has an official X account
2. That account recently posted something directly relevant (announcement, photo, reaction)
3. The post adds value — a real photo, official statement, or data the article discusses

**DO NOT embed X posts just to pad articles.** One well-chosen embed per article is ideal. Two max.

## How It Works

Place the full X post URL on its own line in the article body markdown. The frontend auto-detects and renders it as a static embed (no heavy iframe).

```
The BCCI confirmed the schedule for the upcoming series.

https://x.com/BCCI/status/1929501934072586309

The announcement has been met with enthusiasm from fans across the diaspora.
```

## Finding the Right Post

You have two options:

### Option A: Search the web for recent posts from known accounts
```bash
# Search for recent X posts from a specific account about a topic
# Use web search results to find the actual tweet URL
# Example search queries:
# "site:x.com @SpaceX Starship launch"
# "site:x.com @BCCI IPL final"  
# "site:x.com @narendramodi G20"
```

### Option B: Use the social-embed-registry
Check `~/workspace/the-videshi-news/pipeline/social-embed-registry.json` for verified handles organized by category. Match the article's subject to a handle, then search for their recent posts.

## Category → Handle Mapping (Common Examples)

| Article About | Search for posts from |
|---|---|
| Indian cricket, IPL | @BCCI, @IPL, @RCBTweets, team accounts |
| Modi, Indian politics | @narendramodi, @PMOIndia, @MEAIndia |
| SpaceX, rockets | @SpaceX, @elonmusk |
| Google/Android/AI | @Google, @sundarpichai |
| Bollywood films | @iamsrk, @aliaa08, actor's handle |
| Tech companies | @Microsoft, @satyanadella, @sama |

## Rules

1. **Only embed REAL posts** — verify the URL exists. Never fabricate a tweet URL.
2. **Prefer posts with photos/videos** — they add visual value to the article.
3. **Use the official account** — not fan accounts or random users.
4. **Recent posts only** — within the last 7 days for news, 30 days for features.
5. **Place the URL on its own line** — not inline with other text.
6. **Add context before the embed** — a sentence explaining what the post shows/says.
7. **The embed is supplementary** — the article must stand on its own without it.

## URL Format

Always use the format: `https://x.com/{handle}/status/{tweet_id}`
- Use `x.com`, not `twitter.com`
- Include only the base URL, no query parameters
- The URL must contain `/status/` followed by a numeric ID
