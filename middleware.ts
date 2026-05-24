import { next } from "@vercel/edge";

export const config = {
  matcher: [
    /*
     * Match all request paths EXCEPT:
     *  - /api/*      (API routes)
     *  - /_next/*    (Next internals, if any)
     *  - /assets/*   (Vite build assets)
     *  - static file extensions
     */
    "/((?!api/|_next/|_vercel/|assets/|src/|node_modules/|.*\\.(?:js|css|map|png|jpe?g|gif|svg|ico|webp|woff2?|ttf|eot|json|xml|txt|webmanifest|html)$).*)",
  ],
};

// ── Supabase credentials (public anon key – safe to expose) ────────────
const SUPABASE_URL =
  process.env.VITE_SUPABASE_URL ??
  process.env.SUPABASE_URL ??
  "https://lboecaekpynbpyijrbfz.supabase.co";
const SUPABASE_ANON_KEY =
  process.env.VITE_SUPABASE_PUBLISHABLE_KEY ??
  process.env.SUPABASE_ANON_KEY ??
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxib2VjYWVrcHluYnB5aWpyYmZ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc5NDc2NzQsImV4cCI6MjA5MzUyMzY3NH0.i2_CzXJEnIT2SZ9mx0j5OHh4rqewPwiLUogSrdM4HXY";

const SITE = "https://www.thevideshi.com";

// ── Bot detection ──────────────────────────────────────────────────────
const BOT_RE =
  /Googlebot|Bingbot|Slurp|DuckDuckBot|Baiduspider|YandexBot|facebookexternalhit|Twitterbot|LinkedInBot|WhatsApp|Applebot|Sogou|PetalBot|SemrushBot|AhrefsBot|MJ12bot|Bytespider/i;

function isBot(ua: string | null): boolean {
  return ua ? BOT_RE.test(ua) : false;
}

// ── Helpers ────────────────────────────────────────────────────────────
const esc = (s: string) =>
  s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

async function supaFetch(path: string): Promise<any> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    headers: {
      apikey: SUPABASE_ANON_KEY,
      Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
    },
  });
  if (!res.ok) return null;
  return res.json();
}

// ── Markdown-lite to plain text ────────────────────────────────────────
function mdToText(md: string): string {
  return md
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1")
    .replace(/!\[.*?\]\(.*?\)/g, "")
    .replace(/\[([^\]]+)\]\(.*?\)/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/^[-*+]\s/gm, "• ")
    .trim();
}

// ── Markdown-lite to simple HTML ───────────────────────────────────────
function mdToHtml(md: string): string {
  const lines = md.split("\n");
  let html = "";
  let inList = false;
  for (const raw of lines) {
    const line = raw.trimEnd();
    // Headings
    const hMatch = line.match(/^(#{1,6})\s+(.*)/);
    if (hMatch) {
      if (inList) { html += "</ul>\n"; inList = false; }
      const level = hMatch[1].length;
      html += `<h${level}>${esc(hMatch[2])}</h${level}>\n`;
      continue;
    }
    // List items
    if (/^[-*+]\s/.test(line)) {
      if (!inList) { html += "<ul>\n"; inList = true; }
      html += `<li>${esc(line.replace(/^[-*+]\s/, ""))}</li>\n`;
      continue;
    }
    if (inList) { html += "</ul>\n"; inList = false; }
    // Blank line
    if (!line.trim()) { html += "\n"; continue; }
    // Paragraph
    let p = esc(line);
    p = p.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    p = p.replace(/\*([^*]+)\*/g, "<em>$1</em>");
    html += `<p>${p}</p>\n`;
  }
  if (inList) html += "</ul>\n";
  return html;
}

// ── Category label map ─────────────────────────────────────────────────
const CATEGORY_LABELS: Record<string, string> = {
  news: "News",
  "nri-world": "NRI World",
  travel: "Travel",
  "lifestyle-health": "Lifestyle & Health",
  "markets-finance": "Markets & Finance",
  technology: "Technology",
  sports: "Sports",
  entertainment: "Entertainment",
  food: "Food",
};

// ── Full prerender HTML builder ────────────────────────────────────────
function prerenderPage(opts: {
  title: string;
  description: string;
  canonical: string;
  image?: string;
  jsonLd?: object;
  bodyHtml: string;
}): Response {
  const { title, description, canonical, image, jsonLd, bodyHtml } = opts;
  const img = image || `${SITE}/og-default.jpg`;

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${esc(title)}</title>
  <meta name="description" content="${esc(description.slice(0, 300))}" />
  <link rel="canonical" href="${esc(canonical)}" />
  <meta property="og:title" content="${esc(title)}" />
  <meta property="og:description" content="${esc(description.slice(0, 300))}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="${esc(canonical)}" />
  <meta property="og:image" content="${esc(img)}" />
  <meta property="og:site_name" content="The Videshi" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="${esc(title)}" />
  <meta name="twitter:description" content="${esc(description.slice(0, 300))}" />
  <meta name="twitter:image" content="${esc(img)}" />
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
  ${jsonLd ? `<script type="application/ld+json">${JSON.stringify(jsonLd)}</script>` : ""}
  <style>
    body { font-family: Georgia, "Times New Roman", serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #1a1a1a; line-height: 1.7; }
    h1 { font-size: 2em; line-height: 1.2; margin-bottom: 0.3em; }
    h2 { font-size: 1.5em; margin-top: 1.5em; }
    h3 { font-size: 1.2em; margin-top: 1.2em; }
    img { max-width: 100%; height: auto; }
    .meta { color: #666; font-size: 0.9em; margin-bottom: 1.5em; }
    a { color: #b8860b; }
    nav { border-bottom: 1px solid #ddd; padding-bottom: 12px; margin-bottom: 24px; }
    nav a { margin-right: 16px; text-decoration: none; font-size: 0.95em; }
    footer { border-top: 1px solid #ddd; padding-top: 12px; margin-top: 40px; font-size: 0.85em; color: #888; }
    .card { border: 1px solid #eee; padding: 12px; margin-bottom: 12px; border-radius: 6px; }
    .card h3 { margin-top: 0; }
    ul { padding-left: 1.5em; }
    li { margin-bottom: 0.3em; }
  </style>
</head>
<body>
  <nav>
    <a href="/"><strong>The Videshi</strong></a>
    <a href="/events">Events</a>
    <a href="/directory">Directory</a>
    <a href="/classifieds">Classifieds</a>
    <a href="/cars">Cars</a>
  </nav>
  ${bodyHtml}
  <footer>
    <p>&copy; ${new Date().getFullYear()} The Videshi — News for the global Indian diaspora</p>
    <p><a href="${esc(canonical)}">View full interactive page</a></p>
  </footer>
</body>
</html>`;

  return new Response(html, {
    status: 200,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "public, max-age=300, s-maxage=86400, stale-while-revalidate=86400",
    },
  });
}

// ── Route handlers ─────────────────────────────────────────────────────

async function handleArticle(slug: string): Promise<Response | null> {
  const rows = await supaFetch(
    `p2_articles?select=headline,subheadline,body,image_url,category,published_at,slug&slug=eq.${encodeURIComponent(slug)}&status=eq.published&limit=1`
  );
  if (!rows || !rows[0]) return null;
  const a = rows[0];
  const catLabel = CATEGORY_LABELS[a.category] || a.category || "";
  const pubDate = a.published_at ? new Date(a.published_at).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" }) : "";
  const desc = a.subheadline || (a.body ? mdToText(a.body).slice(0, 300) : "");
  const canonical = `${SITE}/articles/${a.slug || slug}`;

  const bodyHtml = `
    <article>
      <h1>${esc(a.headline)}</h1>
      ${a.subheadline ? `<p class="meta"><em>${esc(a.subheadline)}</em></p>` : ""}
      <p class="meta">${catLabel ? esc(catLabel) + " · " : ""}${pubDate} · The Videshi</p>
      ${a.image_url ? `<img src="${esc(a.image_url)}" alt="${esc(a.headline)}" loading="lazy" />` : ""}
      <div>${a.body ? mdToHtml(a.body) : ""}</div>
    </article>`;

  return prerenderPage({
    title: `${a.headline} — The Videshi`,
    description: desc,
    canonical,
    image: a.image_url,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "NewsArticle",
      headline: a.headline,
      description: desc.slice(0, 300),
      image: a.image_url || `${SITE}/og-default.jpg`,
      url: canonical,
      datePublished: a.published_at,
      publisher: { "@type": "Organization", name: "The Videshi", url: SITE },
      mainEntityOfPage: { "@type": "WebPage", "@id": canonical },
    },
    bodyHtml,
  });
}

async function handleEvent(slug: string): Promise<Response | null> {
  const rows = await supaFetch(
    `events?select=title,date,time,venue_name,city,state,description,long_description,image_url,ticket_url,category,slug&slug=eq.${encodeURIComponent(slug)}&limit=1`
  );
  if (!rows || !rows[0]) return null;
  const e = rows[0];
  const dateStr = e.date ? new Date(e.date + "T00:00:00").toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" }) : "";
  const desc = e.description || (e.long_description ? mdToText(e.long_description).slice(0, 300) : `${e.title} in ${e.city}, ${e.state}`);
  const canonical = `${SITE}/events/${e.slug || slug}`;

  const bodyHtml = `
    <article>
      <h1>${esc(e.title)}</h1>
      <p class="meta">${dateStr}${e.time ? " at " + esc(e.time) : ""}</p>
      <p class="meta">${e.venue_name ? esc(e.venue_name) + " · " : ""}${esc(e.city || "")}, ${esc(e.state || "")}</p>
      ${e.image_url ? `<img src="${esc(e.image_url)}" alt="${esc(e.title)}" loading="lazy" />` : ""}
      ${e.long_description ? mdToHtml(e.long_description) : (e.description ? `<p>${esc(e.description)}</p>` : "")}
      ${e.ticket_url ? `<p><a href="${esc(e.ticket_url)}">Get Tickets</a></p>` : ""}
    </article>`;

  return prerenderPage({
    title: `${e.title} — The Videshi Events`,
    description: desc,
    canonical,
    image: e.image_url,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "Event",
      name: e.title,
      description: desc.slice(0, 300),
      startDate: e.date,
      location: {
        "@type": "Place",
        name: e.venue_name || "",
        address: { "@type": "PostalAddress", addressLocality: e.city, addressRegion: e.state },
      },
      image: e.image_url || `${SITE}/og-default.jpg`,
      url: canonical,
    },
    bodyHtml,
  });
}

async function handleDirectory(slug: string): Promise<Response | null> {
  const rows = await supaFetch(
    `directory_listings?select=name,category,subcategory,description,phone,email,website,address,city,state,zip,rating,review_count,hours,slug&slug=eq.${encodeURIComponent(slug)}&limit=1`
  );
  if (!rows || !rows[0]) return null;
  const d = rows[0];
  const desc = d.description || `${d.name} — ${d.category} in ${d.city}, ${d.state}`;
  const canonical = `${SITE}/directory/${d.slug || slug}`;

  let hoursHtml = "";
  if (d.hours && typeof d.hours === "object") {
    hoursHtml = "<h3>Hours</h3><ul>";
    for (const [day, hrs] of Object.entries(d.hours)) {
      hoursHtml += `<li><strong>${esc(day)}</strong>: ${esc(String(hrs))}</li>`;
    }
    hoursHtml += "</ul>";
  }

  const bodyHtml = `
    <article>
      <h1>${esc(d.name)}</h1>
      <p class="meta">${esc(d.category)}${d.subcategory ? " · " + esc(d.subcategory) : ""}</p>
      <p>${esc(d.address || "")}${d.city ? ", " + esc(d.city) : ""}${d.state ? ", " + esc(d.state) : ""} ${esc(d.zip || "")}</p>
      ${d.phone ? `<p>Phone: ${esc(d.phone)}</p>` : ""}
      ${d.website ? `<p>Website: <a href="${esc(d.website)}">${esc(d.website)}</a></p>` : ""}
      ${d.rating ? `<p>Rating: ${d.rating}/5${d.review_count ? ` (${d.review_count} reviews)` : ""}</p>` : ""}
      ${d.description ? `<p>${esc(d.description)}</p>` : ""}
      ${hoursHtml}
    </article>`;

  return prerenderPage({
    title: `${d.name} — The Videshi Directory`,
    description: desc.slice(0, 300),
    canonical,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "LocalBusiness",
      name: d.name,
      description: desc.slice(0, 300),
      address: {
        "@type": "PostalAddress",
        streetAddress: d.address,
        addressLocality: d.city,
        addressRegion: d.state,
        postalCode: d.zip,
      },
      telephone: d.phone,
      url: d.website || canonical,
      aggregateRating: d.rating ? { "@type": "AggregateRating", ratingValue: d.rating, reviewCount: d.review_count || 1 } : undefined,
    },
    bodyHtml,
  });
}

async function handleCar(slug: string): Promise<Response | null> {
  const rows = await supaFetch(
    `cars?select=name,brand,model,year,slug,msrp_low,msrp_high,mpg,seating,safety_rating,nri_take,pros,cons,image_url,lease_monthly,body_type,fuel_type&slug=eq.${encodeURIComponent(slug)}&limit=1`
  );
  if (!rows || !rows[0]) return null;
  const c = rows[0];
  const price = c.msrp_low ? `$${Number(c.msrp_low).toLocaleString()}${c.msrp_high ? ` – $${Number(c.msrp_high).toLocaleString()}` : ""}` : "";
  const desc = `${c.name} review for Indian Americans. ${price ? "Starting at " + price + ". " : ""}${c.nri_take ? c.nri_take.slice(0, 200) : ""}`;
  const canonical = `${SITE}/cars/${c.slug || slug}`;

  const bodyHtml = `
    <article>
      <h1>${esc(c.name)}</h1>
      <p class="meta">${esc(c.body_type || "")} · ${esc(c.fuel_type || "")} · ${c.year || ""}</p>
      ${c.image_url ? `<img src="${esc(c.image_url)}" alt="${esc(c.name)}" loading="lazy" />` : ""}
      ${price ? `<p><strong>MSRP:</strong> ${esc(price)}</p>` : ""}
      ${c.mpg ? `<p><strong>Fuel Economy:</strong> ${esc(c.mpg)}</p>` : ""}
      ${c.seating ? `<p><strong>Seating:</strong> ${c.seating}</p>` : ""}
      ${c.safety_rating ? `<p><strong>Safety Rating:</strong> ${c.safety_rating}/5</p>` : ""}
      ${c.lease_monthly ? `<p><strong>Lease:</strong> $${c.lease_monthly}/mo</p>` : ""}
      ${c.nri_take ? `<h2>NRI Take</h2><p>${esc(c.nri_take)}</p>` : ""}
      ${c.pros ? `<h2>Pros</h2><ul>${(c.pros as string[]).map((p: string) => `<li>${esc(p)}</li>`).join("")}</ul>` : ""}
      ${c.cons ? `<h2>Cons</h2><ul>${(c.cons as string[]).map((p: string) => `<li>${esc(p)}</li>`).join("")}</ul>` : ""}
    </article>`;

  return prerenderPage({
    title: `${c.name} Review — The Videshi Cars`,
    description: desc.slice(0, 300),
    canonical,
    image: c.image_url,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "Product",
      name: c.name,
      description: desc.slice(0, 300),
      image: c.image_url || `${SITE}/og-default.jpg`,
      brand: { "@type": "Brand", name: c.brand },
      offers: c.msrp_low
        ? { "@type": "Offer", priceCurrency: "USD", price: c.msrp_low, url: canonical }
        : undefined,
    },
    bodyHtml,
  });
}

async function handleClassified(slug: string): Promise<Response | null> {
  const rows = await supaFetch(
    `classifieds?select=title,description,category,subcategory,price,city,state,image_url,slug&slug=eq.${encodeURIComponent(slug)}&status=eq.active&limit=1`
  );
  if (!rows || !rows[0]) return null;
  const cl = rows[0];
  const desc = cl.description || `${cl.title} — ${cl.category} classified in ${cl.city}, ${cl.state}`;
  const canonical = `${SITE}/classifieds/${cl.slug || slug}`;

  const bodyHtml = `
    <article>
      <h1>${esc(cl.title)}</h1>
      <p class="meta">${esc(cl.category || "")}${cl.subcategory ? " · " + esc(cl.subcategory) : ""} · ${esc(cl.city || "")}, ${esc(cl.state || "")}</p>
      ${cl.price ? `<p><strong>Price:</strong> $${Number(cl.price).toLocaleString()}</p>` : ""}
      ${cl.image_url ? `<img src="${esc(cl.image_url)}" alt="${esc(cl.title)}" loading="lazy" />` : ""}
      ${cl.description ? `<p>${esc(cl.description)}</p>` : ""}
    </article>`;

  return prerenderPage({
    title: `${cl.title} — The Videshi Classifieds`,
    description: desc.slice(0, 300),
    canonical,
    bodyHtml,
  });
}

async function handleCategory(category: string): Promise<Response | null> {
  const label = CATEGORY_LABELS[category];
  if (!label) return null;

  const rows = await supaFetch(
    `p2_articles?select=headline,subheadline,slug,published_at,image_url&category=eq.${encodeURIComponent(category)}&status=eq.published&order=published_at.desc&limit=20`
  );
  if (!rows || !rows.length) return null;

  const canonical = `${SITE}/category/${category}`;
  let listHtml = "";
  for (const a of rows) {
    const date = a.published_at ? new Date(a.published_at).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : "";
    listHtml += `<div class="card">
      <h3><a href="/articles/${esc(a.slug)}">${esc(a.headline)}</a></h3>
      ${a.subheadline ? `<p>${esc(a.subheadline.slice(0, 200))}</p>` : ""}
      <p class="meta">${date}</p>
    </div>\n`;
  }

  return prerenderPage({
    title: `${label} — The Videshi`,
    description: `Latest ${label.toLowerCase()} articles for the Indian diaspora from The Videshi.`,
    canonical,
    bodyHtml: `<h1>${esc(label)}</h1>\n<p>Latest ${esc(label.toLowerCase())} coverage from The Videshi.</p>\n${listHtml}`,
  });
}

async function handleSectionListing(
  section: string,
  table: string,
  select: string,
  filter: string,
  titleField: string,
  slugPrefix: string,
  sectionTitle: string,
  sectionDesc: string,
): Promise<Response | null> {
  const rows = await supaFetch(`${table}?select=${select}&${filter}&limit=30`);
  if (!rows || !rows.length) return null;

  const canonical = `${SITE}/${section}`;
  let listHtml = "";
  for (const item of rows) {
    const name = item[titleField] || "";
    const slug = item.slug || "";
    const city = item.city || "";
    const state = item.state || "";
    listHtml += `<div class="card">
      <h3><a href="/${section}/${esc(slug)}">${esc(name)}</a></h3>
      ${city ? `<p class="meta">${esc(city)}${state ? ", " + esc(state) : ""}</p>` : ""}
    </div>\n`;
  }

  return prerenderPage({
    title: `${sectionTitle} — The Videshi`,
    description: sectionDesc,
    canonical,
    bodyHtml: `<h1>${esc(sectionTitle)}</h1>\n<p>${esc(sectionDesc)}</p>\n${listHtml}`,
  });
}

async function handleHomepage(): Promise<Response | null> {
  const rows = await supaFetch(
    `p2_articles?select=headline,subheadline,slug,category,published_at,image_url&status=eq.published&order=published_at.desc&limit=20`
  );
  if (!rows || !rows.length) return null;

  let listHtml = "";
  for (const a of rows) {
    const catLabel = CATEGORY_LABELS[a.category] || a.category || "";
    const date = a.published_at ? new Date(a.published_at).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : "";
    listHtml += `<div class="card">
      <h3><a href="/articles/${esc(a.slug)}">${esc(a.headline)}</a></h3>
      ${a.subheadline ? `<p>${esc(a.subheadline.slice(0, 200))}</p>` : ""}
      <p class="meta">${catLabel} · ${date}</p>
    </div>\n`;
  }

  return prerenderPage({
    title: "The Videshi — News for the global Indian diaspora",
    description: "The Videshi: editorial reporting and analysis for the global Indian diaspora — India, NRI affairs, US-India, business, culture, and voices.",
    canonical: SITE,
    bodyHtml: `
      <h1>The Videshi</h1>
      <p><em>News for the global Indian diaspora</em></p>
      <h2>Latest Articles</h2>
      ${listHtml}
      <h2>Explore</h2>
      <ul>
        <li><a href="/events">Events</a> — Community events near you</li>
        <li><a href="/directory">Directory</a> — Indian businesses across America</li>
        <li><a href="/classifieds">Classifieds</a> — Buy, sell, rent</li>
        <li><a href="/cars">Cars</a> — Car guides for NRIs</li>
      </ul>`,
  });
}

// ── SPA meta-tag injection (for regular users on article pages) ────────
type Article = {
  headline: string;
  subheadline: string | null;
  image_url: string | null;
  slug: string | null;
};

function injectMeta(html: string, article: Article, canonical: string, origin: string): string {
  const title = esc(`${article.headline} — The Videshi`);
  const desc = esc((article.subheadline ?? "").slice(0, 300));
  const rawImage =
    article.image_url && article.image_url.trim().length > 0
      ? article.image_url
      : `${origin}/og-default.jpg`;
  const image = esc(rawImage);

  const jsonLd = JSON.stringify({
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    headline: article.headline,
    description: (article.subheadline ?? "").slice(0, 300),
    image: rawImage,
    url: canonical,
    publisher: { "@type": "Organization", name: "The Videshi", url: origin },
    mainEntityOfPage: { "@type": "WebPage", "@id": canonical },
  });

  let out = html.replace(/<title>[\s\S]*?<\/title>/i, `<title>${title}</title>`);
  out = out.replace(
    /<meta\s+(?:name|property)=["'](?:description|og:title|og:description|og:type|og:image|og:url|twitter:card|twitter:title|twitter:description|twitter:image)["'][^>]*>\s*/gi,
    ""
  );

  const tags = [
    `<meta name="description" content="${desc}" />`,
    `<meta property="og:title" content="${esc(article.headline)}" />`,
    `<meta property="og:description" content="${desc}" />`,
    `<meta property="og:type" content="article" />`,
    `<meta property="og:url" content="${esc(canonical)}" />`,
    `<meta property="og:image" content="${image}" />`,
    `<meta property="og:site_name" content="The Videshi" />`,
    `<meta name="twitter:card" content="summary_large_image" />`,
    `<meta name="twitter:title" content="${esc(article.headline)}" />`,
    `<meta name="twitter:description" content="${desc}" />`,
    `<meta name="twitter:image" content="${image}" />`,
    `<link rel="canonical" href="${esc(canonical)}" />`,
    `<script type="application/ld+json">${jsonLd}</script>`,
  ].join("\n    ");

  out = out.replace(/<\/head>/i, `    ${tags}\n  </head>`);
  return out;
}

// ── Main middleware ────────────────────────────────────────────────────
export default async function middleware(request: Request) {
  const url = new URL(request.url);
  const path = url.pathname;
  const ua = request.headers.get("user-agent");

  // ─ Bot path: full prerendered HTML ─────────────────────────────────
  if (isBot(ua)) {
    try {
      let response: Response | null = null;

      // Homepage
      if (path === "/" || path === "") {
        response = await handleHomepage();
      }
      // Article detail
      else if (/^\/articles\/([^/]+)\/?$/.test(path)) {
        const slug = decodeURIComponent(path.match(/^\/articles\/([^/]+)/)![1]);
        response = await handleArticle(slug);
      }
      // Event detail
      else if (/^\/events\/([^/]+)\/?$/.test(path) && !/submit|edit/.test(path)) {
        const slug = decodeURIComponent(path.match(/^\/events\/([^/]+)/)![1]);
        response = await handleEvent(slug);
      }
      // Directory detail
      else if (/^\/directory\/([^/]+)\/?$/.test(path) && !/submit/.test(path)) {
        const slug = decodeURIComponent(path.match(/^\/directory\/([^/]+)/)![1]);
        response = await handleDirectory(slug);
      }
      // Car detail
      else if (/^\/cars\/([^/]+)\/?$/.test(path) && !/guide|deals|compare/.test(path)) {
        const slug = decodeURIComponent(path.match(/^\/cars\/([^/]+)/)![1]);
        response = await handleCar(slug);
      }
      // Classified detail
      else if (/^\/classifieds\/([^/]+)\/?$/.test(path) && !/submit|edit/.test(path)) {
        const slug = decodeURIComponent(path.match(/^\/classifieds\/([^/]+)/)![1]);
        response = await handleClassified(slug);
      }
      // Section landing: events
      else if (/^\/events\/?$/.test(path)) {
        const today = new Date().toISOString().split("T")[0];
        response = await handleSectionListing("events", "events", "title,slug,city,state,date", `date=gte.${today}&order=date.asc`, "title", "events", "Community Events", "Upcoming Indian community events across America.");
      }
      // Section landing: directory
      else if (/^\/directory\/?$/.test(path)) {
        response = await handleSectionListing("directory", "directory_listings", "name,slug,city,state,category", "order=rating.desc.nullslast", "name", "directory", "Indian Business Directory", "Find Indian businesses, doctors, attorneys, restaurants, and services across America.");
      }
      // Section landing: classifieds
      else if (/^\/classifieds\/?$/.test(path)) {
        response = await handleSectionListing("classifieds", "classifieds", "title,slug,city,state,category", "status=eq.active&order=created_at.desc", "title", "classifieds", "Classifieds", "Buy, sell, and rent within the Indian diaspora community.");
      }
      // Section landing: cars
      else if (/^\/cars\/?$/.test(path)) {
        response = await handleSectionListing("cars", "cars", "name,slug,city,state,brand", "order=sort_order.asc", "name", "cars", "Cars for NRIs", "Car buying guides, reviews, and lease deals for Indian Americans.");
      }
      // Category page (MUST be after section landings to avoid matching /events, /directory, etc.)
      else if (/^\/([a-z-]+)\/?$/.test(path)) {
        const cat = path.replace(/^\//, "").replace(/\/$/, "");
        if (CATEGORY_LABELS[cat]) {
          response = await handleCategory(cat);
        }
      }

      if (response) return response;
    } catch (e) {
      // Fall through to SPA on error
    }
    // Bot but no specific handler matched → fall through to SPA
  }

  // ─ Human path: SPA with meta-tag injection for article pages ───────
  const articleMatch = path.match(/^\/articles\/([^/]+)\/?$/);
  if (articleMatch) {
    const slug = decodeURIComponent(articleMatch[1]);
    const rows = await supaFetch(
      `p2_articles?select=headline,subheadline,image_url,slug&slug=eq.${encodeURIComponent(slug)}&status=eq.published&limit=1`
    );
    if (rows && rows[0]) {
      const article = rows[0] as Article;
      try {
        const shellRes = await fetch(new URL("/index.html", url.origin), {
          headers: { "x-middleware-shell": "1" },
        });
        if (shellRes.ok) {
          const html = await shellRes.text();
          const canonical = `${url.origin}/articles/${article.slug ?? slug}`;
          const transformed = injectMeta(html, article, canonical, url.origin);
          return new Response(transformed, {
            status: 200,
            headers: {
              "content-type": "text/html; charset=utf-8",
              "cache-control": "public, max-age=0, s-maxage=300, stale-while-revalidate=86400",
            },
          });
        }
      } catch {
        // Fall through
      }
    }
  }

  return next();
}
