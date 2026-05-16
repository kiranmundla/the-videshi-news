// Vercel Edge Middleware: serves OG-rich HTML to social crawlers
export const config = { matcher: '/articles/:slug*' };

const BOT_UA = /whatsapp|facebookexternalhit|twitterbot|linkedinbot|slackbot|telegrambot|discordbot|googlebot|bingbot/i;

export default function middleware(req) {
  const ua = req.headers.get('user-agent') || '';
  if (!BOT_UA.test(ua)) return;         // real users → SPA as normal

  const url = new URL(req.url);
  // Extract slug from /articles/some-slug-here
  const slug = url.pathname.replace(/^\/articles\//, '');
  if (!slug) return;

  // Rewrite to the serverless OG function
  const ogUrl = new URL(`/api/og?slug=${encodeURIComponent(slug)}`, req.url);
  return Response.redirect(ogUrl, 302);
}
