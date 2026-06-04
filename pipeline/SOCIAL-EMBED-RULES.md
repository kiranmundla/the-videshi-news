# Social Embed Rules — X & Instagram

## When to Embed

Embed a social post when **ALL** of these are true:
1. The article is about a specific person, organization, or event with an active social account
2. That account recently posted something directly relevant (photo, announcement, reaction)
3. The post adds visual or editorial value the article text alone doesn't capture

**One embed per article is ideal. Two max.** Don't pad articles with embeds.

## Which Platform to Use

| Article type | Platform | Why |
|---|---|---|
| **Celebrity news, film promotions, fashion, lifestyle** | Instagram | Celebrities post visual content here first |
| **Cricket, sports reactions, political statements** | X (Twitter) | Official accounts break news on X |
| **Tech announcements, company news** | X | CEOs and companies announce on X |
| **Food, travel, culture** | Instagram | Visual-first content |

When in doubt: **Instagram for visuals, X for statements.**

## How It Works

Place the full post URL on its own line in the article body. The frontend auto-detects and renders it as a lightweight embed.

```markdown
Deepika Padukone shared a behind-the-scenes look from the sets.

https://www.instagram.com/p/ABC123xyz/

The post quickly garnered millions of likes from fans worldwide.
```

```markdown
The BCCI confirmed the schedule in an official post.

https://x.com/BCCI/status/1929501934072586309

The announcement has been met with enthusiasm from fans.
```

## Finding the Right Post

### For X posts:
Search the web: `site:x.com @SpaceX Starship launch` or `site:x.com @BCCI IPL`

### For Instagram posts:
Search the web: `site:instagram.com deepikapadukone` + topic keywords
Or: `{celebrity name} instagram post {topic}` — news articles often link to the IG post directly

## Handle Registry

Check `~/workspace/the-videshi-news/pipeline/social-embed-registry.json` for verified handles by category. Each entry has `x`, `threads`, and/or `instagram` fields.

### Quick Reference — Instagram

| Celebrity | Handle |
|---|---|
| Deepika Padukone | @deepikapadukone |
| Alia Bhatt | @aliaabhatt |
| Shah Rukh Khan | @iamsrk |
| Priyanka Chopra | @priyankachopra |
| Ranveer Singh | @ranveersingh |
| Virat Kohli | @virat.kohli |
| Diljit Dosanjh | @diljitdosanjh |
| Akshay Kumar | @akshaykumar |

### Quick Reference — X

| Account | Handle |
|---|---|
| BCCI | @BCCI |
| PM Modi | @narendramodi |
| SpaceX | @SpaceX |
| Sundar Pichai | @sundarpichai |
| Virat Kohli | @imVkohli |

## Rules

1. **Only embed REAL posts** — verify the URL exists. Never fabricate a URL.
2. **Prefer posts with photos/videos** — they add visual value.
3. **Use the official account** — not fan pages or reshares.
4. **Recent posts only** — within 7 days for news, 30 days for features.
5. **Place the URL on its own line** — not inline with other text.
6. **Add context before the embed** — one sentence explaining what it shows.
7. **The embed is supplementary** — the article stands on its own without it.

## URL Formats

- X: `https://x.com/{handle}/status/{tweet_id}` (use `x.com`, not `twitter.com`)
- Instagram: `https://www.instagram.com/p/{shortcode}/` or `/reel/{shortcode}/`
