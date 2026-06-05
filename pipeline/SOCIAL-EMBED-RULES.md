# Social Embed Rules — X (Twitter) Embeds Only

## Copyright — Non-Negotiable

- **NEVER download, store, or hotlink social media images** (`pbs.twimg.com`, `cdninstagram.com`, etc.)
- The ONLY legal way to show X/Twitter content is via the **react-tweet embed** — the official embed framework
- This renders the full tweet card (avatar, text, images, stats) — that's the deal for using their content
- Instagram iframes are also fine (official embed mechanism)

## When to Embed — Only Relevant Articles

**Most articles should NOT have a tweet embed.** Only add one when it genuinely strengthens the story.

✅ **Good candidates:**
- A person/org made a statement on X that IS the news (PM Modi tweets about a policy, BCCI announces a squad)
- A celebrity shared photos/video directly relevant to the story (Kohli celebrating a win)
- A tech CEO announced something on X (Sundar Pichai on a Google launch)
- Breaking news where an official X post is the primary source

❌ **Skip embeds for:**
- General news analysis or opinion pieces
- Immigration policy explainers (no one tweets usefully about visa processing)
- Food, travel, lifestyle features (a tweet rarely adds value here)
- Any article where the embed would feel forced or decorative
- Topics where no relevant official account tweeted about it recently

Embed a social post when **ALL** of these are true:
1. The article is about a specific person, organization, or event with an active X account
2. That account recently posted something directly relevant (photo, announcement, reaction)
3. The post adds editorial value the article text alone doesn't capture
4. **You found a REAL, VERIFIED tweet URL** via web search — not constructed or guessed

**One embed per article max. Zero is the default. An embed must earn its place.**

## Finding Real Tweet URLs — MANDATORY PROCESS

### Step 1: Search for the tweet
Use `browser_search` with queries like:
- `site:x.com @BCCI IPL final 2026`
- `site:x.com @narendramodi G7 summit`
- `@sundarpichai AI announcement x.com`

### Step 2: Verify the tweet exists
After finding a candidate URL, extract the tweet ID and verify:

```bash
bash ~/workspace/the-videshi-news/pipeline/verify-tweet.sh TWEET_ID
```

This returns `VALID|@handle|photos=N|videos=N|tweet text...` or `NOT_FOUND`.

**Only proceed if the script returns VALID.**

### Step 3: Confirm relevance
- The tweet text must actually be about the article's topic
- The tweet must be from the correct account (not a random reply)
- Prefer tweets with photos/videos — they add visual value

### Step 4: Insert into article body
Place the full URL on its own line:

```markdown
The BCCI confirmed the schedule in an official post.

https://x.com/BCCI/status/1929501934072586309

The announcement has been met with enthusiasm from fans.
```

## Rules

1. **NEVER fabricate a URL.** Do NOT guess or construct tweet IDs. Period.
2. **ALWAYS verify** with `verify-tweet.sh` before inserting.
3. **No embed is better than a fake embed.** A missing embed is invisible. "Tweet not found" damages credibility.
4. **No image hotlinking.** Never reference `pbs.twimg.com` URLs directly. The react-tweet component handles image display within its card.
5. **Use the official account** — not fan pages or reshares.
6. **Recent posts only** — within 7 days for news, 30 days for features.
7. **Place the URL on its own line** — not inline with other text.
8. **Add context before the embed** — one sentence explaining what it shows.
9. **The embed is supplementary** — the article stands on its own without it.

## Handle Registry

Check `~/workspace/the-videshi-news/pipeline/social-embed-registry.json` for verified handles by category.

### Quick Reference — X

| Account | Handle |
|---|---|
| BCCI | @BCCI |
| PM Modi | @narendramodi |
| SpaceX | @SpaceX |
| Sundar Pichai | @sundarpichai |
| Virat Kohli | @imVkohli |
| Elon Musk | @elonmusk |
| Sam Altman | @sama |

### Quick Reference — Instagram

| Celebrity | Handle |
|---|---|
| Deepika Padukone | @deepikapadukone |
| Alia Bhatt | @aliaabhatt |
| Shah Rukh Khan | @iamsrk |
| Priyanka Chopra | @priyankachopra |
| Virat Kohli | @virat.kohli |
| Diljit Dosanjh | @diljitdosanjh |

## URL Formats

- X: `https://x.com/{handle}/status/{tweet_id}` (use `x.com`, not `twitter.com`)
- Instagram: `https://www.instagram.com/p/{shortcode}/` or `/reel/{shortcode}/`
