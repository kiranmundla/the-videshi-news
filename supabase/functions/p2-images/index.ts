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

// ── Step 2c: og:image from source hunt URLs ───────────────

async function getOgImage(sourceUrl: string): Promise<string | null> {
  try {
    const res = await fetch(sourceUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; TheVideshi/1.0)',
      },
      signal: AbortSignal.timeout(5000),
    })
    if (!res.ok) return null
    const html = await res.text()

    // Parse og:image meta tag
    const match =
      html.match(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["']/i) ??
      html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+property=["']og:image["']/i)

    const url = match?.[1] ?? null
    if (!url || url.startsWith('data:')) return null

    // Resolve relative URLs
    if (url.startsWith('/')) {
      const base = new URL(sourceUrl)
      return `${base.origin}${url}`
    }
    return url
  } catch {
    return null
  }
}

// ── Step 2d: Unsplash search ──────────────────────────────

async function searchUnsplash(query: string, limit = 15): Promise<string[]> {
  try {
    const res = await fetch(
      `https://api.unsplash.com/search/photos?` +
      `query=${encodeURIComponent(query)}&per_page=${limit}` +
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

// ── Step 2e: Pexels search ────────────────────────────────

async function searchPexels(query: string, limit = 15): Promise<string[]> {
  try {
    const res = await fetch(
      `https://api.pexels.com/v1/search?` +
      `query=${encodeURIComponent(query)}&per_page=${limit}&orientation=landscape`,
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

// ── Step 2f: RSS photo feed ───────────────────────────────

async function getRSSPhotos(feedUrl: string, limit: number): Promise<string[]> {
  try {
    const res = await fetch(feedUrl, {
      headers: { 'User-Agent': 'TheVideshi/1.0' },
      signal: AbortSignal.timeout(8000),
    })
    if (!res.ok) return []
    const xml = await res.text()
    const urls: string[] = []

    const enclosureRegex = /<enclosure[^>]+url=["']([^"']+)["'][^>]+type=["']image[^"']*["']/gi
    let m: RegExpExecArray | null
    while ((m = enclosureRegex.exec(xml)) && urls.length < limit) {
      urls.push(m[1])
    }

    const mediaRegex = /<media:content[^>]+url=["']([^"']+)["']/gi
    while ((m = mediaRegex.exec(xml)) && urls.length < limit) {
      urls.push(m[1])
    }

    return urls
  } catch {
    return []
  }
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

async function claudePickBest(
  candidates: Array<{ url: string; source: string }>,
  headline: string,
  vertical: string
): Promise<string | null> {
  if (candidates.length === 0) return null

  // Fetch thumbnails in parallel (max 12 candidates for Vision)
  const subset = candidates.slice(0, 12)
  const thumbnails = await Promise.all(
    subset.map(async (c, i) => ({
      index: i,
      url: c.url,
      source: c.source,
      thumb: await fetchThumbnail(c.url),
    }))
  )

  const valid = thumbnails.filter(t => t.thumb !== null)
  if (valid.length === 0) return null

  // Build multi-image Claude message
  const imageBlocks = valid.flatMap((t, i) => [
    {
      type: 'text' as const,
      text: `Image ${i + 1} (source: ${t.source}):`,
    },
    {
      type: 'image' as const,
      source: {
        type: 'base64' as const,
        media_type: t.thumb!.mediaType,
        data: t.thumb!.base64,
      },
    },
  ])

  const response = await anthropic.messages.create({
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 100,
    messages: [{
      role: 'user',
      content: [
        ...imageBlocks,
        {
          type: 'text',
          text: `Article headline: "${headline}"
Vertical: ${vertical}
Platform: The Videshi — premium Indian diaspora news site

Which image number (1-${valid.length}) best represents this 
article as a thumbnail? Criteria:
- Directly relevant to the story subject
- Professional quality, publication-ready
- Not a generic stock photo unrelated to the topic
- Suitable for Indian-American news audience

If NO image is suitable (irrelevant, low quality, generic 
unrelated stock photo), reply 0.

Reply with a single number only.`,
        },
      ],
    }],
  })

  const pick = parseInt((response.content[0] as any).text.trim())
  if (isNaN(pick) || pick === 0 || pick > valid.length) return null
  return valid[pick - 1].url
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
      id, headline, vertical, tags,
      topic_id,
      p2_topics ( keywords )
    `)
    .is('image_url', null)
    .in('status', ['published', 'review'])
    .order('published_at', { ascending: false, nullsFirst: false })
    .limit(8)

  if (error || !articles || articles.length === 0) {
    return new Response(
      JSON.stringify({ ok: true, message: 'No articles need images' }),
      { headers: { 'Content-Type': 'application/json' } }
    )
  }

  const results: any[] = []

  for (const article of articles) {
    try {
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

      // ── Step 2: Load active image sources from videshi_sources registry
      const { data: imageSourcesRaw } = await supabase
        .from('videshi_sources')
        .select('*')
        .eq('is_active', true)
        .eq('pipeline_stage', 'image')
        .order('priority', { ascending: true })

      // Normalize fields so the rest of the loop matches the previous schema
      const imageSources = (imageSourcesRaw ?? []).map((s: any) => ({
        ...s,
        max_candidates: s.max_items ?? 10,
        good_for_verticals: s.verticals ?? [],
        skip_for_verticals: s.skip_verticals ?? [],
      }))

      function sourceAppliesToVertical(source: any, vertical: string): boolean {
        if (source.skip_for_verticals?.includes(vertical)) return false
        if (!source.good_for_verticals || source.good_for_verticals.length === 0) return true
        return source.good_for_verticals.includes(vertical)
      }

      const candidates: Array<{
        url: string
        source: string
        source_type: string
        priority: number
        source_id: string
      }> = []

      for (const source of imageSources) {
        if (!sourceAppliesToVertical(source, article.vertical)) continue

        let newCandidates: string[] = []
        // Accept both "wikipedia" and "img_wikipedia" style
        const stype = (source.source_type ?? '').replace(/^img_/, '')

        switch (stype) {
          case 'wikipedia':
            if (entity) {
              const img = await getWikipediaImage(entity)
              if (img) newCandidates = [img]
            }
            break
          case 'wikimedia':
            newCandidates = await getWikimediaImages(entity ?? query, source.max_candidates)
            break
          case 'og_image':
            for (const url of sourceUrls.slice(0, 3)) {
              const img = await getOgImage(url)
              if (img) newCandidates.push(img)
            }
            break
          case 'rss_photos':
            if (source.endpoint_url) {
              newCandidates = await getRSSPhotos(source.endpoint_url, source.max_candidates)
            }
            break
          case 'unsplash':
            newCandidates = await searchUnsplash(query, source.max_candidates)
            break
          case 'pexels':
            newCandidates = await searchPexels(query, source.max_candidates)
            break
          default:
            // Unknown source type (e.g. direct_url with API key) — skip silently
            break
        }

        candidates.push(...newCandidates.map(url => ({
          url,
          source: source.name,
          source_type: source.source_type,
          priority: source.priority,
        })))

        // Stop early if we already have enough high-priority candidates
        const tier1Count = candidates.filter(c => c.priority <= 25).length
        if (tier1Count >= 5) break
      }

      if (candidates.length === 0) {
        results.push({ headline: article.headline, status: 'no_candidates' })
        continue
      }

      // ── Step 3: Claude Vision picks best
      const winnerUrl = await claudePickBest(
        candidates,
        article.headline,
        article.vertical
      )

      if (!winnerUrl) {
        results.push({
          headline: article.headline,
          status: 'rejected',
          candidates: candidates.length,
        })
        continue
      }

      // ── Step 4: Download winner to Storage
      const storedUrl = await downloadToStorage(winnerUrl, article.id)

      if (storedUrl) {
        await supabase
          .from('p2_articles')
          .update({ image_url: storedUrl })
          .eq('id', article.id)

        const winner = candidates.find(c => c.url === winnerUrl)
        const winnerRank = candidates.findIndex(c => c.url === winnerUrl) + 1

        await supabase.from('p2_image_source_log').insert({
          article_id: article.id,
          image_source: winner?.source ?? null,
          source_type: winner?.source_type ?? null,
          candidates: candidates.length,
          winner_rank: winnerRank,
        })

        results.push({
          headline: article.headline,
          status: 'ok',
          source: winner?.source,
          source_type: winner?.source_type,
          candidates: candidates.length,
          winner_rank: winnerRank,
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
  const succeeded = results.filter(r => r.status === 'ok').length
  const rejected = results.filter(r => r.status === 'rejected').length

  await supabase.from('pipeline_alerts').insert({
    agent: 'p2-images',
    severity: 'info',
    error_type: null,
    message: `p2-images: ${succeeded} images sourced, ${rejected} rejected by Vision in ${elapsed}ms`,
  })

  return new Response(
    JSON.stringify({ ok: true, succeeded, rejected, elapsed, results }),
    { headers: { 'Content-Type': 'application/json' } }
  )
})
