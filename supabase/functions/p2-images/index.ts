import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import Anthropic from 'https://esm.sh/@anthropic-ai/sdk@0.27.0'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

const UNSPLASH_KEY = Deno.env.get('UNSPLASH_ACCESS_KEY')!
const PEXELS_KEY = Deno.env.get('PEXELS_API_KEY')!
const ANTHROPIC_KEY = Deno.env.get('ANTHROPIC_API_KEY')!
const BUCKET = 'article-images'
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!

const SKIP_IMAGE_VERTICALS = ['politics','economy','immigration','tech']

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

const VERTICAL_IMAGE_TERMS: Record<string, string> = {
  politics:      'India parliament New Delhi government',
  economy:       'Indian rupee finance economy',
  tech:          'India technology innovation',
  immigration:   'passport travel airport customs',
  diaspora:      'Indian American family community',
  science:       'rocket launch space research',
  culture:       'Indian festival celebration',
  sports:        'cricket India stadium',
  entertainment: 'Bollywood cinema film India',
}

const POOR_IMAGE_KEYWORDS = new Set([
  'epfo','pf','provident','repo','sebi','rbi','irdai',
  'monetary','fiscal','gazette','notification','circular',
  'agni','missile','icbm','nuclear','ballistic',
  'uscis','visa bulletin','h1b','eb2','gc','i-140'
])

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

async function fetchUnsplashMany(query: string, count: number): Promise<string[]> {
  try {
    const res = await fetch(
      `https://api.unsplash.com/photos/random?query=${encodeURIComponent(query)}&orientation=landscape&content_filter=high&count=${count}`,
      { headers: { Authorization: `Client-ID ${UNSPLASH_KEY}` } }
    )
    if (!res.ok) return []
    const data = await res.json()
    if (!Array.isArray(data)) return []
    return data.map((p: any) => p?.urls?.regular).filter(Boolean) as string[]
  } catch {
    return []
  }
}

async function fetchPexelsMany(query: string, count: number): Promise<string[]> {
  try {
    const res = await fetch(
      `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&per_page=${count}&orientation=landscape`,
      { headers: { Authorization: PEXELS_KEY } }
    )
    if (!res.ok) return []
    const data = await res.json()
    const photos = data?.photos ?? []
    return photos
      .map((p: any) => p?.src?.large2x ?? p?.src?.large)
      .filter(Boolean) as string[]
  } catch {
    return []
  }
}

async function scoreCandidates(urls: string[]): Promise<{ url: string | null; score: number }> {
  const client = new Anthropic({ apiKey: ANTHROPIC_KEY })

  let bestUrl: string | null = null
  let bestScore = 0

  for (const url of urls) {
    try {
      const res = await fetch(url)
      if (!res.ok) continue
      const buffer = await res.arrayBuffer()
      const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)))
      const contentType = res.headers.get('content-type') ?? 'image/jpeg'

      const response = await client.messages.create({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 100,
        messages: [{
          role: 'user',
          content: [
            {
              type: 'image',
              source: { type: 'base64', media_type: contentType as any, data: base64 }
            },
            {
              type: 'text',
              text: `Score this image 1-10 for use as a news article thumbnail. 
Consider: Is it clear and high quality? Does it look professional? 
Is it relevant for Indian diaspora news (avoid: generic stock photos 
of random Western people, abstract shapes, low resolution)?
Reply with ONLY a number 1-10.`
            }
          ]
        }]
      })

      const score = parseInt((response.content[0] as any).text.trim())
      if (!isNaN(score) && score > bestScore) {
        bestScore = score
        bestUrl = url
      }
    } catch {
      continue
    }
  }

  return { url: bestScore >= 8 ? bestUrl : null, score: bestScore }
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
    if (SKIP_IMAGE_VERTICALS.includes(article.vertical)) {
      results.push({ id: article.id, headline: article.headline, status: 'skipped_vertical', vertical: article.vertical })
      continue
    }

    let query = buildQuery(article.headline, article.tags ?? [], article.vertical)
    if (query.split(' ').some(w => POOR_IMAGE_KEYWORDS.has(w.toLowerCase()))) {
      query = VERTICAL_IMAGE_TERMS[article.vertical] ?? 'India news'
    }

    // Fetch 3 candidates: Unsplash first, supplement with Pexels
    const candidates: string[] = []
    candidates.push(...(await fetchUnsplashMany(query, 3)))
    if (candidates.length < 3) {
      const need = 3 - candidates.length
      candidates.push(...(await fetchPexelsMany(query, need)))
    }

    if (candidates.length === 0) {
      results.push({ id: article.id, headline: article.headline, status: 'no_candidates' })
      continue
    }

    const { url: bestUrl, score } = await scoreCandidates(candidates)

    if (!bestUrl) {
      // Score < 8 — leave image_url null, do not download
      results.push({ id: article.id, headline: article.headline, status: 'rejected_low_score', score, query })
      continue
    }

    const storedUrl = await downloadToStorage(bestUrl, article.id)

    if (!storedUrl) {
      await supabase.from('p2_articles').update({ image_url: bestUrl }).eq('id', article.id)
      results.push({ id: article.id, status: 'direct_url', score, query })
      continue
    }

    await supabase.from('p2_articles').update({ image_url: storedUrl }).eq('id', article.id)
    results.push({ id: article.id, headline: article.headline, status: 'ok', score, query })

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
