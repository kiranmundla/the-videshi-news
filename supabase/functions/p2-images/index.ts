import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import Anthropic from 'https://esm.sh/@anthropic-ai/sdk@0.27.0'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)
const anthropic = new Anthropic({
  apiKey: Deno.env.get('ANTHROPIC_API_KEY')!
})
const UNSPLASH_KEY = Deno.env.get('UNSPLASH_ACCESS_KEY')!
const PEXELS_KEY = Deno.env.get('PEXELS_API_KEY')!
const BUCKET = 'article-images'
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!

// ── Step 1: Claude extracts main entity + search query ────

async function extractEntityAndQuery(
  headline: string,
  vertical: string
): Promise<{ entity: string | null; query: string }> {
  const response = await anthropic.messages.create({
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 150,
    messages: [{
      role: 'user',
      content: `Given this news headline: "${headline}" (vertical: ${vertical})

Extract:
1. entity: The single most specific named entity (person, org, 
   place, product, event) that a photo search would find. 
   Examples: "Agni-5 missile", "Zepto company", "Reserve Bank 
   of India", "Vivek Ramaswamy". 
   Return null if no specific entity (e.g. generic policy story).
2. query: Best 4-6 word image search query for stock photos.
   Make it visual and specific. NOT generic like "India news".
   Examples: "India missile launch test", "Indian passport visa 
   application", "Zepto grocery delivery app India"

Reply JSON only: {"entity": "..." or null, "query": "..."}`
    }]
  })

  try {
    const text = (response.content[0] as any).text.trim()
    return JSON.parse(text)
  } catch {
    return { entity: null, query: `India ${vertical} news` }
  }
}

// ── Step 2a: Wikipedia lead image ─────────────────────────

async function getWikipediaImage(
  entity: string
): Promise<string | null> {
  try {
    const slug = encodeURIComponent(entity.replace(/\s+/g, '_'))
    const res = await fetch(
      `https://en.wikipedia.org/api/rest_v1/page/summary/${slug}`,
      { headers: { 'User-Agent': 'TheVideshi/1.0 (thevideshi.com)' } }
    )
    if (!res.ok) return null
    const data = await res.json()
    return data?.thumbnail?.source ?? data?.originalimage?.source ?? null
  } catch {
    return null
  }
}

// ── Step 2b: Wikimedia Commons search ─────────────────────

async function getWikimediaImages(
  query: string,
  limit = 8
): Promise<string[]> {
  try {
    const searchRes = await fetch(
      `https://commons.wikimedia.org/w/api.php?` +
      `action=query&list=search&srsearch=${encodeURIComponent(query)}` +
      `&srnamespace=6&srlimit=${limit}&format=json`,
      { headers: { 'User-Agent': 'TheVideshi/1.0 (thevideshi.com)' } }
    )
    if (!searchRes.ok) return []
    const searchData = await searchRes.json()
    const files: string[] = (searchData?.query?.search ?? [])
      .map((r: any) => r.title as string)
      .filter((t: string) => /\.(jpg|jpeg|png|webp)$/i.test(t))

    // Convert file titles to thumbnail URLs
    return files.map(title => {
      const filename = encodeURIComponent(title.replace('File:', ''))
      return `https://commons.wikimedia.org/wiki/Special:FilePath/${filename}?width=600`
    })
  } catch {
    return []
  }
}

// ── Step 2c: Scrape ALL meaningful images from source pages ─

async function scrapeSourceImages(
  sourceUrls: string[]
): Promise<Array<{url: string, attribution: string | null}>> {
  const results: Array<{url: string, attribution: string | null}> = []
  for (const sourceUrl of sourceUrls.slice(0, 5)) {
    try {
      const res = await fetch(sourceUrl, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; TheVideshi/1.0)',
          'Accept': 'text/html'
        },
        signal: AbortSignal.timeout(8000),
      })
      if (!res.ok) continue
      const html = await res.text()
      const pageImages: string[] = []

      // og:image and twitter:image
      const metaPatterns = [
        /property=["']og:image["'][^>]+content=["']([^"']+)["']/i,
        /content=["']([^"']+)["'][^>]+property=["']og:image["']/i,
        /name=["']twitter:image["'][^>]+content=["']([^"']+)["']/i,
        /content=["']([^"']+)["'][^>]+name=["']twitter:image["']/i,
      ]
      for (const pattern of metaPatterns) {
        const match = html.match(pattern)
        if (match?.[1] && !match[1].startsWith('data:')) {
          pageImages.push(match[1])
        }
      }

      // All img tags — try to isolate article body first
      let articleHtml = html
      const bodyPatterns = [
        /<article[^>]*>([\s\S]*?)<\/article>/i,
        /<div[^>]*class="[^"]*(?:content|body|article|press-release|release)[^"]*"[^>]*>([\s\S]*?)<\/div>/i,
        /<div[^>]*id="[^"]*(?:content|body|article|release)[^"]*"[^>]*>([\s\S]*?)<\/div>/i,
      ]
      for (const pattern of bodyPatterns) {
        const match = html.match(pattern)
        if (match?.[1]) { articleHtml = match[1]; break }
      }

      const imgRegex = /<img[^>]+src=["']([^"']+)["'][^>]*>/gi
      let imgMatch
      while ((imgMatch = imgRegex.exec(articleHtml)) !== null) {
        const tag = imgMatch[0]
        const url = imgMatch[1]
        if (url.startsWith('data:')) continue
        if (/icon|logo|avatar|sprite|pixel|tracking/i.test(url)) continue
        if (url.endsWith('.gif')) continue
        const w = parseInt(tag.match(/width=["']?(\d+)/i)?.[1] || '0')
        const h = parseInt(tag.match(/height=["']?(\d+)/i)?.[1] || '0')
        if ((w > 0 && w < 200) || (h > 0 && h < 150)) continue
        pageImages.push(url)
      }

      // srcset — highest resolution variant
      const srcsetRegex = /srcset=["']([^"']+)["']/gi
      let srcsetMatch
      while ((srcsetMatch = srcsetRegex.exec(articleHtml)) !== null) {
        const candidates = srcsetMatch[1].split(',')
          .map(s => {
            const parts = s.trim().split(/\s+/)
            return {
              url: parts[0],
              w: parseInt((parts[1] || '0').replace(/[wx]/g, ''))
            }
          })
          .filter(c => c.url && !c.url.startsWith('data:'))
          .sort((a, b) => b.w - a.w)
        if (candidates[0]?.url) pageImages.push(candidates[0].url)
      }

      // Resolve relative URLs
      const base = new URL(sourceUrl)
      const isGovt =
        /\.gov\.in|pib\.gov|uscis\.gov|rbi\.org\.in|sebi\.gov|ddnews\.gov/.test(sourceUrl)
      const attribution = isGovt ? 'Government of India' : null
      const seen = new Set<string>()
      for (const imgUrl of pageImages) {
        try {
          const resolved = imgUrl.startsWith('http')
            ? imgUrl
            : new URL(imgUrl, base.origin).href
          if (!seen.has(resolved)) {
            seen.add(resolved)
            results.push({ url: resolved, attribution })
          }
          if (results.length >= 15) break
        } catch { continue }
      }
    } catch { continue }
  }
  return results
}

// ── Step 2d: Unsplash search (15 candidates) ──────────────

async function searchUnsplash(query: string): Promise<string[]> {
  try {
    const res = await fetch(
      `https://api.unsplash.com/search/photos?` +
      `query=${encodeURIComponent(query)}&per_page=15` +
      `&orientation=landscape&content_filter=high`,
      { headers: { Authorization: `Client-ID ${UNSPLASH_KEY}` } }
    )
    if (!res.ok) return []
    const data = await res.json()
    return (data?.results ?? [])
      .map((p: any) => p?.urls?.small ?? p?.urls?.regular)
      .filter(Boolean)
  } catch {
    return []
  }
}

// ── Step 2e: Pexels search (15 candidates) ────────────────

async function searchPexels(query: string): Promise<string[]> {
  try {
    const res = await fetch(
      `https://api.pexels.com/v1/search?` +
      `query=${encodeURIComponent(query)}&per_page=15&orientation=landscape`,
      { headers: { Authorization: PEXELS_KEY } }
    )
    if (!res.ok) return []
    const data = await res.json()
    return (data?.photos ?? [])
      .map((p: any) => p?.src?.medium ?? p?.src?.large)
      .filter(Boolean)
  } catch {
    return []
  }
}

// ── Step 2f: Pixabay search ───────────────────────────────

async function searchPixabay(
  query: string,
  limit = 10
): Promise<Array<{url: string, attribution: string}>> {
  const PIXABAY_KEY = Deno.env.get('PIXABAY_API_KEY')
  if (!PIXABAY_KEY) return []

  try {
    const indiaQuery = query.toLowerCase().includes('india')
      ? query
      : query + ' India'

    const res = await fetch(
      'https://pixabay.com/api/?' +
      'key=' + PIXABAY_KEY +
      '&q=' + encodeURIComponent(indiaQuery) +
      '&per_page=' + limit +
      '&image_type=photo' +
      '&orientation=horizontal' +
      '&safesearch=true' +
      '&order=popular',
      { signal: AbortSignal.timeout(5000) }
    )
    if (!res.ok) return []
    const data = await res.json()
    return (data?.hits ?? []).map((p: any) => ({
      url: p.largeImageURL ?? p.webformatURL,
      attribution: 'Pixabay',
    })).filter((p: any) => p.url)
  } catch { return [] }
}

// ── Step 3: Fetch thumbnail as base64 ────────────────────

async function fetchThumbnail(
  url: string
): Promise<{ base64: string; mediaType: string } | null> {
  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': 'TheVideshi/1.0' },
      signal: AbortSignal.timeout(8000),
    })
    if (!res.ok) return null
    const contentType = res.headers.get('content-type') ?? 'image/jpeg'
    if (!contentType.startsWith('image/')) return null
    const buffer = await res.arrayBuffer()
    // Skip images > 500KB (too large for batch vision)
    if (buffer.byteLength > 500_000) return null
    const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)))
    const mediaType = contentType.split(';')[0] as any
    return { base64, mediaType }
  } catch {
    return null
  }
}

// ── Step 4: Claude Vision picks best candidate ────────────

type VisionResult = {
  url: string | null
  source: string | null
  pickIndex: number   // 1-based index of chosen candidate, 0 = rejected all
  score: number       // Claude's score for the winner (0 if rejected)
  candidatesEvaluated: number
}

async function claudePickBest(
  candidates: Array<{ url: string; source: string; attribution?: string | null }>,
  headline: string,
  vertical: string
): Promise<VisionResult> {
  if (candidates.length === 0) {
    return { url: null, source: null, pickIndex: 0, score: 0, candidatesEvaluated: 0 }
  }

  // Reorder: government/press release sources first,
  // then wikipedia/wikimedia, then stock photos last
  const reordered = [
    ...candidates.filter(c =>
      c.attribution?.includes('Government') ||
      c.attribution?.includes('PIB') ||
      c.attribution?.includes('Wikimedia')
    ),
    ...candidates.filter(c =>
      !c.attribution?.includes('Government') &&
      !c.attribution?.includes('PIB') &&
      !c.attribution?.includes('Wikimedia')
    )
  ]

  // Fetch thumbnails in parallel (max 12 candidates for Vision)
  const subset = reordered.slice(0, 12)
  const thumbnails = await Promise.all(
    subset.map(async (c, i) => ({
      index: i,
      url: c.url,
      source: c.source,
      thumb: await fetchThumbnail(c.url),
    }))
  )

  const valid = thumbnails.filter(t => t.thumb !== null)
  if (valid.length === 0) {
    return { url: null, source: null, pickIndex: 0, score: 0, candidatesEvaluated: 0 }
  }

  const imageMustShow = headline

  // Score each image individually so we get score + reason per image
  const scored = await Promise.all(valid.map(async (t) => {
    try {
      const resp = await anthropic.messages.create({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 200,
        messages: [{
          role: 'user',
          content: [
            {
              type: 'image' as const,
              source: {
                type: 'base64' as const,
                media_type: t.thumb!.mediaType,
                data: t.thumb!.base64,
              },
            },
            {
              type: 'text' as const,
              text: `Images are presented in priority order: government/press release photos first, stock photos last. Prefer earlier images unless they are completely wrong for the topic. A real event photo scores 2 points higher than an equivalent stock photo.

You are selecting a thumbnail for: '${headline}'

The image MUST show: ${imageMustShow}

Image source: ${t.source}
Vertical: ${vertical}

RULE 1 — SOURCE PRIORITY (apply before scoring):
If any candidate comes from a government press release, company press release, or official source (PIB, DRDO, Ministry, company website), that image gets +3 bonus added to its raw score. Real event photos beat stock photos even if less polished.

RULE 2 — AUTOMATIC TEXT-FIRST (score 0, skip all):
If headline contains any of these topics, return pick: 0 immediately without reviewing images:
- Military strikes, armed conflict, ceasefire
- Separatist movements, terrorism warnings
- Drug crisis, crime enforcement
- Sanctions, geopolitical conflict

RULE 3 — ENTITY MATCH REQUIRED:
Image must specifically show ${imageMustShow}. Generic India/Pakistan/Canada imagery scores max 4 even if visually beautiful.

RULE 4 — REJECT STOCK CLICHÉS:
Handshakes, lightbulbs, puzzle pieces, people at whiteboards, coin stacks → max score 3.

Score 9-10: Real event photo OR perfect entity match
Score 7-8: Good entity match, acceptable quality
Score 4-6: Loose connection, generic
Score 1-3: Wrong entity or stock cliché
Score 0: Automatic text-first (Rule 2)

Threshold: only accept score 8+.

Reply JSON: {pick: N, score: N, reason: 'one line'}`,
            },
          ],
        }],
      })

      const raw = (resp.content[0] as any).text.trim()
      const match = raw.match(/\{[\s\S]*\}/)
      if (!match) return { ...t, score: 0 }
      const parsed = JSON.parse(match[0])
      const score = Number(parsed.score) || 0
      return { ...t, score }
    } catch {
      return { ...t, score: 0 }
    }
  }))

  // Pick highest score; only accept if >= 8
  const best = scored.reduce((a, b) => (b.score > a.score ? b : a), scored[0])
  if (!best || best.score < 8) {
    return { url: null, source: null, pickIndex: 0, score: best?.score ?? 0, candidatesEvaluated: valid.length }
  }
  const pickIdx = valid.findIndex(v => v.url === best.url) + 1
  return {
    url: best.url,
    source: best.source,
    pickIndex: pickIdx,
    score: best.score,
    candidatesEvaluated: valid.length,
  }
}

// ── Step 5: Download winner to Supabase Storage ───────────

async function downloadToStorage(
  imageUrl: string,
  articleId: string
): Promise<string | null> {
  try {
    const res = await fetch(imageUrl, {
      headers: { 'User-Agent': 'TheVideshi/1.0' },
    })
    if (!res.ok) return null
    const contentType = res.headers.get('content-type') ?? 'image/jpeg'
    const ext = contentType.includes('png') ? 'png' : 'jpg'
    const filename = `p2-${articleId}-${Date.now()}.${ext}`
    const buffer = await res.arrayBuffer()

    const { error } = await supabase.storage
      .from(BUCKET)
      .upload(filename, buffer, { contentType, upsert: false })

    if (error) return imageUrl // fallback: use direct URL

    return `${SUPABASE_URL}/storage/v1/object/public/${BUCKET}/${filename}`
  } catch {
    return null
  }
}

// ── Main handler ──────────────────────────────────────────

Deno.serve(async () => {
  const startTime = Date.now()

  // Fetch articles needing images
  const { data: articles, error } = await supabase
    .from('p2_articles')
    .select(`
      id, headline, vertical, tags, image_must_show,
      topic_id,
      p2_topics ( keywords )
    `)
    .is('image_url', null)
    .eq('status', 'published')
    .order('published_at', { ascending: false, nullsFirst: false })
    .limit(8)

  if (error || !articles || articles.length === 0) {
    return new Response(
      JSON.stringify({ ok: true, message: 'No articles need images' }),
      { headers: { 'Content-Type': 'application/json' } }
    )
  }

  const results: any[] = []
  let skipped = 0

  // Track URLs already used across articles (DB + this run)
  const { data: usedImages } = await supabase
    .from('p2_articles')
    .select('image_url')
    .not('image_url', 'is', null)
  const usedUrls = new Set(
    (usedImages ?? []).map((a: any) => a.image_url)
  )

  const TEXT_FIRST_KEYWORDS = [
    'military', 'strike', 'operation sindoor',
    'ceasefire', 'missile', 'drone supply',
    'khalistan', 'separatist', 'terror',
    'drug crisis', 'sanctions', 'iran',
    'doctrine', 'armed conflict', 'warfare'
  ]

  for (const article of articles) {
    try {
      const headlineLower = article.headline.toLowerCase()
      const isTextFirst = TEXT_FIRST_KEYWORDS.some(
        kw => headlineLower.includes(kw)
      )
      if (isTextFirst || !(article as any).image_must_show) {
        skipped++
        results.push({
          headline: article.headline,
          status: 'text_first_by_topic'
        })
        continue
      }

      // Get source hunt URLs for this topic
      const { data: hunts } = await supabase
        .from('p2_source_hunts')
        .select('url')
        .eq('topic_id', article.topic_id)
        .not('url', 'is', null)
        .limit(3)

      const sourceUrls = (hunts ?? []).map(h => h.url)

      // ── Step 1: Claude extracts entity + query
      const { entity, query } = await extractEntityAndQuery(
        article.headline,
        article.vertical
      )

      // ── Step 2: Collect candidates from all tiers
      const candidates: Array<{ url: string; source: string; attribution: string | null }> = []

      // Tier 1a: Wikipedia entity image (highest relevance)
      if (entity) {
        const wikiImage = await getWikipediaImage(entity)
        if (wikiImage) candidates.push({ url: wikiImage, source: 'wikipedia', attribution: 'Wikimedia Commons' })

        // Tier 1b: Wikimedia Commons
        const commonsImages = await getWikimediaImages(entity, 6)
        candidates.push(...commonsImages.map(u => ({ url: u, source: 'wikimedia', attribution: 'Wikimedia Commons' })))
      }

      // Tier 2: scrape ALL meaningful images from source pages
      const sourceResults = await scrapeSourceImages(sourceUrls)
      for (const r of sourceResults) {
        candidates.push({ url: r.url, source: 'source-scrape', attribution: r.attribution })
      }

      // Tier 3: Unsplash + Pexels + Pixabay (if < 6 candidates so far)
      if (candidates.length < 6) {
        const [unsplashImages, pexelsImages, pixabayImages] = await Promise.all([
          searchUnsplash(query),
          searchPexels(query),
          searchPixabay(query, 10),
        ])
        candidates.push(...unsplashImages.map(u => ({ url: u, source: 'unsplash', attribution: null })))
        candidates.push(...pexelsImages.map(u => ({ url: u, source: 'pexels', attribution: null })))
        candidates.push(...pixabayImages.map(p => ({ url: p.url, source: 'pixabay', attribution: p.attribution })))
      }

      if (candidates.length === 0) {
        await supabase.from('videshi_image_log').insert({
          article_id: article.id,
          headline: article.headline,
          source_used: null,
          candidates_count: 0,
          vision_pick: 0,
          vision_score: 0,
        })
        results.push({ headline: article.headline, status: 'no_candidates' })
        continue
      }

      // ── Step 3: Claude Vision picks best (skip duplicates already used)
      let vision = await claudePickBest(
        candidates,
        article.headline,
        article.vertical
      )
      let remaining = candidates.slice()
      while (vision.url) {
        if (!usedUrls.has(vision.url)) break
        remaining = remaining.filter(c => c.url !== vision.url)
        if (remaining.length === 0) {
          vision = { url: null, source: null, pickIndex: 0, score: 0, candidatesEvaluated: 0 } as any
          break
        }
        vision = await claudePickBest(remaining, article.headline, article.vertical)
      }

      if (!vision.url) {
        await supabase.from('videshi_image_log').insert({
          article_id: article.id,
          headline: article.headline,
          source_used: null,
          candidates_count: candidates.length,
          vision_pick: 0,
          vision_score: vision.score,
        })
        results.push({
          headline: article.headline,
          status: 'rejected',
          candidates: candidates.length,
        })
        continue
      }

      // ── Step 4: Download winner to Storage
      const storedUrl = await downloadToStorage(vision.url, article.id)

      if (storedUrl) {
        const attribution =
          vision.source === 'wikipedia' || vision.source === 'wikimedia'
            ? 'Wikimedia Commons'
            : vision.source === 'unsplash'
            ? 'Unsplash'
            : vision.source === 'pexels'
            ? 'Pexels'
            : null
        await supabase
          .from('p2_articles')
          .update({ image_url: storedUrl, image_attribution: attribution })
          .eq('id', article.id)
        usedUrls.add(storedUrl)

        await supabase.from('videshi_image_log').insert({
          article_id: article.id,
          headline: article.headline,
          source_used: vision.source,
          candidates_count: candidates.length,
          vision_pick: vision.pickIndex,
          vision_score: vision.score,
        })

        results.push({
          headline: article.headline,
          status: 'ok',
          source: vision.source,
          candidates: candidates.length,
          vision_score: vision.score,
        })
      }

      // Delay between articles to respect rate limits
      await new Promise(r => setTimeout(r, 500))

    } catch (err: any) {
      await supabase.from('pipeline_alerts').insert({
        agent: 'p2-images',
        severity: 'error',
        error_type: 'image_error',
        message: `${article.headline}: ${err.message}`,
      })
      results.push({ headline: article.headline, status: 'error', error: err.message })
    }
  }

  const elapsed = Date.now() - startTime
  const sourced = results.filter(r => r.status === 'ok').length
  const rejected = results.filter(r => r.status === 'rejected').length
  const textFirst = results.filter(r => r.status === 'no_candidates' || r.status === 'rejected').length

  await supabase.from('pipeline_alerts').insert({
    agent: 'p2-images',
    severity: 'info',
    error_type: null,
    message: `p2-images: ${sourced} sourced, ${rejected} rejected by Vision, ${textFirst} text-first in ${elapsed}ms`,
  })

  return new Response(
    JSON.stringify({ ok: true, sourced, rejected, textFirst, elapsed, results }),
    { headers: { 'Content-Type': 'application/json' } }
  )
})
