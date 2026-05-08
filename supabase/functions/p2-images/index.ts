import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

const UNSPLASH_KEY = Deno.env.get('UNSPLASH_ACCESS_KEY')!
const PEXELS_KEY = Deno.env.get('PEXELS_API_KEY')!
const BUCKET = 'article-images'
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

const VERTICAL_IMAGE_TERMS: Record<string, string> = {
  politics:      'India parliament government Delhi',
  economy:       'India finance rupee stock market Mumbai',
  tech:          'India technology startup innovation',
  immigration:   'passport visa travel documents',
  diaspora:      'Indian American community diversity',
  science:       'India space research technology ISRO',
  culture:       'Indian culture festival celebration',
  sports:        'India cricket stadium sport',
  entertainment: 'Bollywood India cinema film',
}

function buildQuery(headline: string, tags: string[], vertical: string): string {
  const SKIP_TAGS = new Set([
    'india','news','breaking','latest','update',
    'government','policy','report','analysis'
  ])
  const goodTags = (tags ?? [])
    .filter(t => !SKIP_TAGS.has(t.toLowerCase()) && t.length > 3)
    .slice(0, 2)
  if (goodTags.length >= 2) {
    return goodTags.join(' ')
  }

  const stopWords = new Set([
    'the','a','an','in','on','at','to','for','of',
    'and','or','is','are','was','will','has','have',
    'its','this','that','with','from','by','as','up'
  ])
  const headlineWords = headline
    .replace(/[^a-zA-Z\s]/g, ' ')
    .split(/\s+/)
    .filter(w =>
      !stopWords.has(w.toLowerCase()) &&
      !SKIP_TAGS.has(w.toLowerCase()) &&
      w.length > 3
    )
    .slice(0, 3)
  if (headlineWords.length >= 2) {
    return headlineWords.join(' ')
  }

  return VERTICAL_IMAGE_TERMS[vertical] ?? 'India news'
}

async function fetchUnsplash(query: string): Promise<string | null> {
  try {
    const res = await fetch(
      `https://api.unsplash.com/photos/random?query=${encodeURIComponent(query)}&orientation=landscape&content_filter=high`,
      { headers: { Authorization: `Client-ID ${UNSPLASH_KEY}` } }
    )
    if (!res.ok) return null
    const data = await res.json()
    return data?.urls?.regular ?? null
  } catch {
    return null
  }
}

async function fetchPexels(query: string): Promise<string | null> {
  try {
    const res = await fetch(
      `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&per_page=5&orientation=landscape`,
      { headers: { Authorization: PEXELS_KEY } }
    )
    if (!res.ok) return null
    const data = await res.json()
    const photos = data?.photos ?? []
    if (photos.length === 0) return null
    const pick = photos[Math.floor(Math.random() * photos.length)]
    return pick?.src?.large2x ?? pick?.src?.large ?? null
  } catch {
    return null
  }
}

async function downloadToStorage(imageUrl: string, articleId: string): Promise<string | null> {
  try {
    const res = await fetch(imageUrl)
    if (!res.ok) return null
    const contentType = res.headers.get('content-type') ?? 'image/jpeg'
    const ext = contentType.includes('png') ? 'png' : 'jpg'
    const filename = `p2-${articleId}-${Date.now()}.${ext}`
    const buffer = await res.arrayBuffer()
    const { error } = await supabase.storage
      .from(BUCKET)
      .upload(filename, buffer, { contentType, upsert: false })
    if (error) return null
    return `${SUPABASE_URL}/storage/v1/object/public/${BUCKET}/${filename}`
  } catch {
    return null
  }
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })

  const startTime = Date.now()

  const { data: articles, error } = await supabase
    .from('p2_articles')
    .select('id, headline, tags, vertical')
    .is('image_url', null)
    .in('status', ['published', 'review'])
    .order('published_at', { ascending: false, nullsFirst: false })
    .limit(10)

  if (error || !articles || articles.length === 0) {
    return new Response(
      JSON.stringify({ ok: true, message: 'No articles need images' }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }

  const results: any[] = []

  for (const article of articles) {
    const query = buildQuery(article.headline, article.tags ?? [])

    let imageUrl = await fetchUnsplash(query)
    let source = 'unsplash'

    if (!imageUrl) {
      imageUrl = await fetchPexels(query)
      source = 'pexels'
    }

    if (!imageUrl) {
      const fallbackQuery = `India ${article.vertical}`
      imageUrl = (await fetchUnsplash(fallbackQuery)) ?? (await fetchPexels(fallbackQuery))
      source = 'fallback'
    }

    if (!imageUrl) {
      results.push({ id: article.id, headline: article.headline, status: 'no_image_found' })
      continue
    }

    const storedUrl = await downloadToStorage(imageUrl, article.id)

    if (!storedUrl) {
      await supabase.from('p2_articles').update({ image_url: imageUrl }).eq('id', article.id)
      results.push({ id: article.id, status: 'direct_url', source })
      continue
    }

    await supabase.from('p2_articles').update({ image_url: storedUrl }).eq('id', article.id)
    results.push({ id: article.id, headline: article.headline, status: 'ok', source, query })

    await new Promise(r => setTimeout(r, 300))
  }

  const elapsed = Date.now() - startTime
  const succeeded = results.filter(r => r.status === 'ok' || r.status === 'direct_url').length

  await supabase.from('pipeline_alerts').insert({
    agent: 'p2-images',
    severity: 'info',
    error_type: null,
    message: `p2-images: ${succeeded}/${articles.length} images fetched in ${elapsed}ms`,
  })

  return new Response(
    JSON.stringify({ ok: true, succeeded, total: articles.length, elapsed, results }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
})
