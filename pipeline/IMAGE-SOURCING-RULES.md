# Image Sourcing Rules for The Videshi
# All writers MUST follow this. No shortcuts, no generic stock.

## The Rule
**You are a photo editor at a newspaper. Every image must be specifically relevant to the article.**

## Hierarchy (in order)
1. **Wikimedia Commons** — For any article about a PERSON, search Wikimedia for that person's actual photo. Most Indian politicians, celebrities, athletes, tech leaders have CC-licensed photos. Use: `https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={person_name}&gsrlimit=10&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1200&format=json`
2. **Social embeds** (entertainment/sports/tech only) — If the person is in `pipeline/celebrity-handles.json`, embed their recent relevant Instagram/X post in the article body (copyright-safe)
3. **Pexels** — ONLY as fallback, and ONLY with specific search terms that match the article. "Cannes film festival red carpet" is OK. "Movie" is NOT OK. "Netflix streaming" is NOT OK.
4. **No image** — Better than a wrong or generic image. Kiran's rule: **No image > wrong image**

## What NEVER to do
- Generic stock photos (popcorn for a movie article, laptop for a tech article, stethoscope for health)
- Pexels as first choice when the article is about a specific person
- Same image on multiple articles
- Images that don't match the article's actual subject
- Satellite/aerial/map images (filtered by BAD_ALT_RE in the pipeline)

## Skip list
Check `pipeline/image-skip-list.json` before sourcing. Articles in this list had images manually removed — don't re-source them.

## Upload format
- Hero: `{article_id}.jpg` to Supabase bucket `article-images`
- Gallery: `{article_id}_g1.jpg`, `{article_id}_g2.jpg` etc
- Set `image_attribution` = "The Videshi"
- Set `gallery_images` = JSON array of `[{"url": "...", "caption": "..."}]`
