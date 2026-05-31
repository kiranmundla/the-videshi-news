/**
 * Optimize image URLs for web delivery.
 * - Pexels: append auto-compress + width params (97%+ size reduction)
 * - Supabase storage: use transform API for resizing
 * - Others: return as-is
 */
export function optimizeImageUrl(url: string | null | undefined, width: number = 800): string {
  if (!url) return '';

  // Pexels images: use their CDN resize params
  if (url.includes('images.pexels.com')) {
    const baseUrl = url.split('?')[0];
    return `${baseUrl}?auto=compress&cs=tinysrgb&w=${width}&fit=crop`;
  }

  // Supabase storage images: pass through as-is (transform saves <3%, not worth the CLS/preload issues)

  return url;
}

// Preset sizes for different contexts
export const IMAGE_SIZES = {
  hero: 1200,      // Hero/featured image (above fold)
  card: 600,       // Article card
  thumbnail: 200,  // Small thumbnail
  gallery: 800,    // Gallery/carousel
} as const;
