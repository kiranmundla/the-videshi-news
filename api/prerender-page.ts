// Universal prerender handler: serves fully-rendered HTML for ALL page types
// when hit by search engine bots. Replaces the articles-only prerender.
// Handles: homepage, categories, events, directory, classifieds, cars, static pages, articles.

import type { VercelRequest, VercelResponse } from "@vercel/node";

const SUPABASE_URL =
  process.env.VITE_SUPABASE_URL ??
  process.env.SUPABASE_URL ??
  "https://lboecaekpynbpyijrbfz.supabase.co";
const SUPABASE_KEY =
  process.env.VITE_SUPABASE_ANON_KEY ??
  process.env.SUPABASE_ANON_KEY ??
  "";

const SITE = "https://www.thevideshi.com";

// ── Helpers ────────────────────────────────────────────────────────────────

function esc(s: string): string {
  return (s || "")
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function stripMarkdown(body: string): string {
  return (body || "")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/^\s*[-*+]\s+/gm, "• ")
    .replace(/^\s*\d+\.\s+/gm, "")
    .replace(/^>\s+/gm, "")
    .replace(/```[\s\S]*?```/g, "")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/<[^>]+>/g, "")
    .trim();
}

function toParagraphs(text: string): string {
  return text
    .split(/\n{2,}/)
    .filter((p) => p.trim())
    .map((p) => `<p>${p.trim()}</p>`)
    .join("\n");
}

async function sbFetch(table: string, select: string, filters: string, limit = 20): Promise<any[]> {
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/${table}?select=${select}&${filters}&limit=${limit}`,
    {
      headers: {
        apikey: SUPABASE_KEY,
        Authorization: `Bearer ${SUPABASE_KEY}`,
      },
    }
  );
  if (!res.ok) return [];
  return res.json();
}

function pageShell(opts: {
  title: string;
  description: string;
  url: string;
  image?: string;
  type?: string;
  jsonLd?: object;
  body: string;
  canonical?: string;
  noindex?: boolean;
  publishedTime?: string;
  section?: string;
}): string {
  const ogType = opts.type || "website";
  const image = opts.image || `${SITE}/og-default.jpg`;
  const canonical = opts.canonical || opts.url;

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="google-site-verification" content="E0VUC85-cnXig_VCzitH3FtWGNZXYYznm2BVGy8MEJk">
<title>${esc(opts.title)}</title>
<meta name="description" content="${esc(opts.description)}">
${opts.noindex ? '<meta name="robots" content="noindex">' : ""}
<meta property="og:title" content="${esc(opts.title)}">
<meta property="og:description" content="${esc(opts.description)}">
<meta property="og:type" content="${ogType}">
<meta property="og:url" content="${esc(opts.url)}">
<meta property="og:image" content="${esc(image)}">
<meta property="og:site_name" content="The Videshi">
${opts.publishedTime ? `<meta property="article:published_time" content="${esc(opts.publishedTime)}">` : ""}
${opts.section ? `<meta property="article:section" content="${esc(opts.section)}">` : ""}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(opts.title)}">
<meta name="twitter:description" content="${esc(opts.description)}">
<meta name="twitter:image" content="${esc(image)}">
<link rel="canonical" href="${esc(canonical)}">
${opts.jsonLd ? `<script type="application/ld+json">${JSON.stringify(opts.jsonLd)}</script>` : ""}
</head>
<body>
<header>
  <h1><a href="${SITE}">The Videshi</a></h1>
  <p>News for the global Indian diaspora</p>
</header>
${opts.body}
<footer>
  <p>&copy; The Videshi. <a href="${SITE}">Homepage</a></p>
</footer>
</body>
</html>`;
}

// ── Route handlers ─────────────────────────────────────────────────────────

const CATEGORIES: Record<string, string> = {
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

async function renderHomepage(): Promise<string> {
  const articles = await sbFetch(
    "p2_articles",
    "headline,subheadline,slug,category,image_url,published_at",
    "status=eq.published&order=published_at.desc",
    30
  );

  const articleLinks = articles
    .map(
      (a: any) =>
        `<li><a href="${SITE}/articles/${esc(a.slug)}">${esc(a.headline)}</a>
         <span>${esc(a.category || "")} · ${a.published_at ? new Date(a.published_at).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : ""}</span></li>`
    )
    .join("\n");

  const catLinks = Object.entries(CATEGORIES)
    .map(([slug, name]) => `<li><a href="${SITE}/${slug}">${name}</a></li>`)
    .join("\n");

  return pageShell({
    title: "The Videshi — News for the Global Indian Diaspora",
    description:
      "Breaking news, immigration updates, NRI stories, events, and community resources for Indians abroad. Updated every hour.",
    url: SITE,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "WebSite",
      name: "The Videshi",
      url: SITE,
      description: "News for the global Indian diaspora",
      publisher: {
        "@type": "Organization",
        name: "The Videshi",
        logo: { "@type": "ImageObject", url: `${SITE}/logo.png` },
      },
    },
    body: `
<main>
  <h2>Latest Stories</h2>
  <ul>${articleLinks}</ul>
  <h2>Sections</h2>
  <ul>${catLinks}</ul>
  <p><a href="${SITE}/events">Events</a> · <a href="${SITE}/directory">Directory</a> · <a href="${SITE}/classifieds">Classifieds</a> · <a href="${SITE}/cars">Cars</a></p>
</main>`,
  });
}

async function renderCategory(category: string): Promise<string | null> {
  const label = CATEGORIES[category];
  if (!label) return null;

  const articles = await sbFetch(
    "p2_articles",
    "headline,subheadline,slug,image_url,published_at",
    `status=eq.published&category=eq.${category}&order=published_at.desc`,
    30
  );

  const articleLinks = articles
    .map(
      (a: any) =>
        `<li><a href="${SITE}/articles/${esc(a.slug)}">${esc(a.headline)}</a>
         ${a.subheadline ? `<br><small>${esc(a.subheadline)}</small>` : ""}</li>`
    )
    .join("\n");

  return pageShell({
    title: `${label} — The Videshi`,
    description: `Latest ${label.toLowerCase()} stories for the Indian diaspora. Updated hourly.`,
    url: `${SITE}/${category}`,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "CollectionPage",
      name: `${label} — The Videshi`,
      url: `${SITE}/${category}`,
      publisher: { "@type": "Organization", name: "The Videshi" },
    },
    body: `
<main>
  <h2>${esc(label)}</h2>
  <ul>${articleLinks}</ul>
</main>`,
  });
}

// Try to find a published article by stripping date suffixes or hash tails
// from stale slugs that Google still crawls. Returns the published slug or null.
async function tryArticleSlugFallback(slug: string): Promise<string | null> {
  // Pattern 1: slug ends with -YYYYMMDD (e.g. -20260614)
  const dateMatch = slug.match(/^(.+)-(\d{8})$/);
  if (dateMatch) {
    const base = dateMatch[1];
    const rows = await sbFetch(
      "p2_articles", "slug",
      `slug=eq.${encodeURIComponent(base)}&status=eq.published`, 1
    );
    if (rows.length) return rows[0].slug;
    // Also try fuzzy: published article whose slug starts with the base
    const fuzzy = await sbFetch(
      "p2_articles", "slug",
      `slug=like.${encodeURIComponent(base)}*&status=eq.published&order=published_at.desc`, 1
    );
    if (fuzzy.length) return fuzzy[0].slug;
  }

  // Pattern 2: slug ends with a short random hash (e.g. -mp0h0f5z)
  const hashMatch = slug.match(/^(.+)-([a-z0-9]{6,10})$/);
  if (hashMatch) {
    const base = hashMatch[1];
    const rows = await sbFetch(
      "p2_articles", "slug",
      `slug=like.${encodeURIComponent(base)}*&status=eq.published&order=published_at.desc`, 1
    );
    if (rows.length) return rows[0].slug;
  }

  return null;
}

async function renderArticle(slug: string): Promise<string | null> {
  const rows = await sbFetch(
    "p2_articles",
    "headline,subheadline,body,image_url,image_caption,slug,category,published_at,updated_at,is_editorial",
    `slug=eq.${encodeURIComponent(slug)}&status=eq.published`,
    1
  );
  if (!rows.length) return null;

  const a = rows[0];
  // If body is empty/null, treat as not-found to avoid soft 404
  if (!a.body || a.body.trim().length < 50) return null;

  const bodyHtml = toParagraphs(stripMarkdown(a.body || ""));
  const url = `${SITE}/articles/${a.slug}`;
  const pubDate = a.published_at || "";
  const modDate = a.updated_at || pubDate;
  const category = a.category || "News";
  const categoryPath = category.toLowerCase().replace(/\s+&\s+/g, "-").replace(/\s+/g, "-");

  return pageShell({
    title: `${a.headline} — The Videshi`,
    description: a.subheadline || "News for the global Indian diaspora",
    url,
    image: a.image_url,
    type: "article",
    publishedTime: pubDate,
    section: category,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "NewsArticle",
      headline: a.headline,
      description: a.subheadline || "",
      image: a.image_url || `${SITE}/og-default.jpg`,
      datePublished: pubDate,
      dateModified: modDate,
      articleSection: category,
      inLanguage: "en",
      isAccessibleForFree: true,
      author: { "@type": "Organization", name: "The Videshi" },
      publisher: {
        "@type": "Organization",
        name: "The Videshi",
        logo: { "@type": "ImageObject", url: `${SITE}/logo.png` },
      },
      mainEntityOfPage: { "@type": "WebPage", "@id": url },
    },
    body: `
<article>
  <h1>${esc(a.headline)}</h1>
  ${a.subheadline ? `<p><em>${esc(a.subheadline)}</em></p>` : ""}
  ${a.image_url ? `<img src="${esc(a.image_url)}" alt="${esc(a.headline)}">` : ""}
  <p>By Editor's Desk · ${pubDate ? new Date(pubDate).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" }) : ""}</p>
  ${bodyHtml}
</article>
<script type="application/ld+json">${JSON.stringify({
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: SITE },
    { "@type": "ListItem", position: 2, name: category, item: `${SITE}/${categoryPath}` },
    { "@type": "ListItem", position: 3, name: a.headline },
  ],
})}</script>`,
  });
}

async function renderEventsIndex(): Promise<string> {
  const today = new Date().toISOString().split("T")[0];
  const events = await sbFetch(
    "events",
    "title,slug,date,city,state,category,venue_name",
    `date=gte.${today}&order=date.asc`,
    50
  );

  const eventLinks = events
    .filter((e: any) => e.slug)
    .map(
      (e: any) =>
        `<li><a href="${SITE}/events/${esc(e.slug)}">${esc(e.title)}</a>
         <br><small>${esc(e.date || "")} · ${esc(e.city || "")}${e.state ? `, ${esc(e.state)}` : ""} · ${esc(e.category || "")}</small></li>`
    )
    .join("\n");

  return pageShell({
    title: "Desi Events Near You — The Videshi",
    description:
      "Discover Indian cultural events, concerts, festivals, community gatherings, and spiritual events across the US. Find Bollywood nights, desi comedy shows, and more.",
    url: `${SITE}/events`,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "CollectionPage",
      name: "Desi Events — The Videshi",
      url: `${SITE}/events`,
      description: "Indian diaspora events across the United States",
      publisher: { "@type": "Organization", name: "The Videshi" },
    },
    body: `
<main>
  <h2>Upcoming Desi Events</h2>
  <ul>${eventLinks}</ul>
</main>`,
  });
}

async function renderEventDetail(slug: string): Promise<string | null> {
  const rows = await sbFetch(
    "events",
    "title,slug,date,end_date,city,state,venue_name,category,long_description,artist_info,venue_info,ticket_url,latitude,longitude",
    `slug=eq.${encodeURIComponent(slug)}`,
    1
  );
  if (!rows.length) return null;

  const e = rows[0];
  const desc = e.long_description || e.title;
  const location = [e.venue_name, e.city, e.state].filter(Boolean).join(", ");

  return pageShell({
    title: `${e.title} — The Videshi Events`,
    description: `${e.title} at ${location}. ${e.date || ""}. Find tickets, venue info, and details.`,
    url: `${SITE}/events/${e.slug}`,
    type: "article",
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "Event",
      name: e.title,
      startDate: e.date,
      ...(e.end_date && { endDate: e.end_date }),
      location: {
        "@type": "Place",
        name: e.venue_name || "",
        address: {
          "@type": "PostalAddress",
          streetAddress: "",
          addressLocality: e.city || "",
          addressRegion: e.state || "",
          addressCountry: "US",
        },
        ...(e.latitude && { geo: { "@type": "GeoCoordinates", latitude: e.latitude, longitude: e.longitude } }),
      },
      ...(e.ticket_url && { offers: { "@type": "Offer", url: e.ticket_url } }),
      organizer: { "@type": "Organization", name: "The Videshi" },
    },
    body: `
<article>
  <h1>${esc(e.title)}</h1>
  <p><strong>Date:</strong> ${esc(e.date || "")}</p>
  <p><strong>Venue:</strong> ${esc(location)}</p>
  <p><strong>Category:</strong> ${esc(e.category || "")}</p>
  ${e.ticket_url ? `<p><a href="${esc(e.ticket_url)}">Get Tickets</a></p>` : ""}
  ${desc ? toParagraphs(stripMarkdown(desc)) : ""}
  ${e.artist_info ? `<h2>Artist Info</h2>${toParagraphs(stripMarkdown(e.artist_info))}` : ""}
  ${e.venue_info ? `<h2>Venue Info</h2>${toParagraphs(stripMarkdown(e.venue_info))}` : ""}
</article>`,
  });
}

async function renderDirectoryIndex(): Promise<string> {
  const listings = await sbFetch(
    "directory_listings",
    "name,slug,city,state,category,subcategory",
    "order=name.asc",
    50
  );

  const listingLinks = listings
    .map(
      (l: any) =>
        `<li><a href="${SITE}/directory/${esc(l.slug)}">${esc(l.name)}</a>
         <br><small>${esc(l.category || "")} · ${esc(l.city || "")}${l.state ? `, ${esc(l.state)}` : ""}</small></li>`
    )
    .join("\n");

  return pageShell({
    title: "Indian Business Directory — The Videshi",
    description:
      "Find Indian restaurants, grocery stores, temples, professionals, and community services across the US. The largest desi business directory.",
    url: `${SITE}/directory`,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "CollectionPage",
      name: "Indian Business Directory — The Videshi",
      url: `${SITE}/directory`,
      publisher: { "@type": "Organization", name: "The Videshi" },
    },
    body: `
<main>
  <h2>Indian Business Directory</h2>
  <ul>${listingLinks}</ul>
</main>`,
  });
}

async function renderDirectoryDetail(slug: string): Promise<string | null> {
  const rows = await sbFetch(
    "directory_listings",
    "name,slug,description,city,state,address,phone,website,category,subcategory,latitude,longitude",
    `slug=eq.${encodeURIComponent(slug)}`,
    1
  );
  if (!rows.length) return null;

  const l = rows[0];
  const location = [l.city, l.state].filter(Boolean).join(", ");

  return pageShell({
    title: `${l.name} — The Videshi Directory`,
    description: `${l.name} in ${location}. ${l.category || ""} — find address, phone, and details.`,
    url: `${SITE}/directory/${l.slug}`,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "LocalBusiness",
      name: l.name,
      description: l.description || "",
      address: {
        "@type": "PostalAddress",
        streetAddress: l.address || "",
        addressLocality: l.city || "",
        addressRegion: l.state || "",
        addressCountry: "US",
      },
      ...(l.phone && { telephone: l.phone }),
      ...(l.website && { url: l.website }),
      ...(l.latitude && { geo: { "@type": "GeoCoordinates", latitude: l.latitude, longitude: l.longitude } }),
    },
    body: `
<article>
  <h1>${esc(l.name)}</h1>
  <p><strong>Category:</strong> ${esc(l.category || "")}${l.subcategory ? ` — ${esc(l.subcategory)}` : ""}</p>
  <p><strong>Location:</strong> ${esc(l.address || "")}${location ? `, ${esc(location)}` : ""}</p>
  ${l.phone ? `<p><strong>Phone:</strong> ${esc(l.phone)}</p>` : ""}
  ${l.website ? `<p><strong>Website:</strong> <a href="${esc(l.website)}">${esc(l.website)}</a></p>` : ""}
  ${l.description ? toParagraphs(l.description) : ""}
</article>`,
  });
}

async function renderClassifiedsIndex(): Promise<string> {
  const now = new Date().toISOString();
  const items = await sbFetch(
    "classifieds",
    "title,slug,city,state,category,price",
    `status=eq.active&expires_at=gte.${now}&order=created_at.desc`,
    50
  );

  const itemLinks = items
    .map(
      (c: any) =>
        `<li><a href="${SITE}/classifieds/${esc(c.slug)}">${esc(c.title)}</a>
         <br><small>${esc(c.category || "")} · ${esc(c.city || "")}${c.state ? `, ${esc(c.state)}` : ""}${c.price ? ` · $${c.price}` : ""}</small></li>`
    )
    .join("\n");

  return pageShell({
    title: "Desi Classifieds — The Videshi",
    description:
      "Browse Indian community classifieds: housing, services, jobs, items for sale, and community postings across the US.",
    url: `${SITE}/classifieds`,
    body: `
<main>
  <h2>Desi Classifieds</h2>
  <ul>${itemLinks}</ul>
</main>`,
  });
}

async function renderClassifiedDetail(slug: string): Promise<string | null> {
  const rows = await sbFetch(
    "classifieds",
    "title,slug,description,city,state,category,price,created_at",
    `slug=eq.${encodeURIComponent(slug)}`,
    1
  );
  if (!rows.length) return null;

  const c = rows[0];
  const location = [c.city, c.state].filter(Boolean).join(", ");

  return pageShell({
    title: `${c.title} — The Videshi Classifieds`,
    description: `${c.title} in ${location}. ${c.category || ""} listing on The Videshi.`,
    url: `${SITE}/classifieds/${c.slug}`,
    body: `
<article>
  <h1>${esc(c.title)}</h1>
  <p><strong>Category:</strong> ${esc(c.category || "")}</p>
  <p><strong>Location:</strong> ${esc(location)}</p>
  ${c.price ? `<p><strong>Price:</strong> $${esc(String(c.price))}</p>` : ""}
  ${c.description ? toParagraphs(c.description) : ""}
</article>`,
  });
}

async function renderCarsIndex(): Promise<string> {
  const cars = await sbFetch(
    "cars",
    "name,slug,brand,category,price_range,fuel_type",
    "order=sort_order.asc",
    50
  );

  const carLinks = cars
    .map(
      (c: any) =>
        `<li><a href="${SITE}/cars/${esc(c.slug)}">${esc(c.name)}</a>
         <br><small>${esc(c.brand || "")} · ${esc(c.category || "")} · ${esc(c.price_range || "")}</small></li>`
    )
    .join("\n");

  const guideLinks = [
    { slug: "first-car-in-america", title: "Your First Car in America" },
    { slug: "lease-vs-buy", title: "Lease vs. Buy" },
    { slug: "insurance-for-new-immigrants", title: "Insurance for New Immigrants" },
    { slug: "best-family-suvs", title: "Best Family SUVs" },
    { slug: "best-cars-under-30k", title: "Best Cars Under $30K" },
    { slug: "best-evs-2026", title: "Best EVs 2026" },
    { slug: "india-vs-us-driving", title: "India vs US Driving" },
    { slug: "cars-for-tech-professionals", title: "Cars for Tech Professionals" },
  ]
    .map((g) => `<li><a href="${SITE}/cars/guide/${g.slug}">${g.title}</a></li>`)
    .join("\n");

  return pageShell({
    title: "Best Cars for Indians in America — The Videshi",
    description:
      "Car buying guide for Indian immigrants: best SUVs, sedans, EVs, lease deals, and expert guides for the Indian diaspora in the US.",
    url: `${SITE}/cars`,
    body: `
<main>
  <h2>Cars for the Indian Diaspora</h2>
  <ul>${carLinks}</ul>
  <h2>Buyer's Guides</h2>
  <ul>${guideLinks}</ul>
</main>`,
  });
}

async function renderCarDetail(slug: string): Promise<string | null> {
  const rows = await sbFetch(
    "cars",
    "name,slug,brand,category,price_range,fuel_type,seating,description,pros,cons",
    `slug=eq.${encodeURIComponent(slug)}`,
    1
  );
  if (!rows.length) return null;

  const c = rows[0];

  return pageShell({
    title: `${c.name} Review — The Videshi Cars`,
    description: `${c.name} — ${c.price_range || ""}. ${c.category || ""} review for the Indian diaspora. Pros, cons, and buying tips.`,
    url: `${SITE}/cars/${c.slug}`,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "Product",
      name: c.name,
      brand: { "@type": "Brand", name: c.brand || "" },
      description: c.description || "",
    },
    body: `
<article>
  <h1>${esc(c.name)}</h1>
  <p><strong>Brand:</strong> ${esc(c.brand || "")} · <strong>Category:</strong> ${esc(c.category || "")}</p>
  <p><strong>Price:</strong> ${esc(c.price_range || "")} · <strong>Fuel:</strong> ${esc(c.fuel_type || "")} · <strong>Seating:</strong> ${esc(String(c.seating || ""))}</p>
  ${c.description ? toParagraphs(c.description) : ""}
  ${c.pros ? `<h2>Pros</h2><p>${esc(c.pros)}</p>` : ""}
  ${c.cons ? `<h2>Cons</h2><p>${esc(c.cons)}</p>` : ""}
</article>`,
  });
}

function renderStaticPage(path: string): string | null {
  const pages: Record<string, { title: string; description: string; body: string }> = {
    "/about": {
      title: "About The Videshi",
      description: "The Videshi is an AI-powered news platform for the global Indian diaspora, covering breaking news, immigration, NRI stories, events, and community resources.",
      body: "<h1>About The Videshi</h1><p>The Videshi is a news platform built for Indians abroad. We cover immigration policy, diaspora politics, cultural events, community services, and stories that matter to NRIs in the US, UK, Canada, and beyond.</p>",
    },
    "/contact": {
      title: "Contact The Videshi",
      description: "Get in touch with The Videshi team for tips, feedback, advertising, or partnerships.",
      body: "<h1>Contact Us</h1><p>Have a tip, feedback, or want to partner with us? Reach out to our team.</p>",
    },
    "/travel": {
      title: "Travel Guide for Indian Diaspora",
      description: "Travel guides, visa information, destination reviews, and travel tips for Indians abroad. Plan your next trip home or explore new destinations.",
      body: "<h1>Travel</h1><p>Destination guides, visa tips, and travel stories for the Indian diaspora.</p>",
    },
    "/immigration": {
      title: "Immigration News & Trackers",
      description: "Latest US immigration news, H-1B updates, green card tracker, visa bulletin, and policy changes affecting the Indian diaspora.",
      body: "<h1>Immigration</h1><p>Immigration news, visa updates, and policy tracking for Indians in America.</p>",
    },
    "/stories": {
      title: "Community Stories — The Videshi",
      description: "Real stories from the Indian diaspora: immigration journeys, career pivots, cultural experiences, and community voices.",
      body: "<h1>Community Stories</h1><p>Real stories from Indians abroad — share yours or read others.</p>",
    },
  };

  const page = pages[path];
  if (!page) return null;

  return pageShell({
    title: page.title + " — The Videshi",
    description: page.description,
    url: `${SITE}${path}`,
    body: `<main>${page.body}</main>`,
  });
}

// ── Main handler ───────────────────────────────────────────────────────────

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const rawPath = (req.query.path as string) || "/";
  // Normalize: strip trailing slash, ensure leading slash
  const path = "/" + rawPath.replace(/^\/+/, "").replace(/\/+$/, "");

  let html: string | null = null;

  try {
    // Route matching (order matters — more specific first)
    if (path === "/" || path === "") {
      html = await renderHomepage();
    } else if (path === "/events") {
      html = await renderEventsIndex();
    } else if (path.startsWith("/events/submit") || path.startsWith("/events/") && path.endsWith("/edit")) {
      // Skip prerender for form pages
      html = null;
    } else if (path.startsWith("/events/")) {
      const slug = path.replace("/events/", "");
      html = await renderEventDetail(slug);
      // Past/deleted events → 410 Gone (tells Google to permanently deindex)
      if (!html) {
        res.status(410).send(`<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Event No Longer Available — The Videshi</title>
<meta name="robots" content="noindex"></head>
<body><h1>This event is no longer available</h1>
<p>This event has passed or been removed. <a href="${SITE}/events">Browse upcoming events</a></p></body></html>`);
        return;
      }
    } else if (path === "/directory") {
      html = await renderDirectoryIndex();
    } else if (path.startsWith("/directory/submit")) {
      html = null;
    } else if (path.startsWith("/directory/")) {
      const slug = path.replace("/directory/", "");
      html = await renderDirectoryDetail(slug);
      // Removed directory listings → 410 Gone
      if (!html) {
        res.status(410).send(`<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Listing No Longer Available — The Videshi</title>
<meta name="robots" content="noindex"></head>
<body><h1>This listing is no longer available</h1>
<p>This directory listing has been removed. <a href="${SITE}/directory">Browse the directory</a></p></body></html>`);
        return;
      }
    } else if (path === "/classifieds") {
      html = await renderClassifiedsIndex();
    } else if (path.startsWith("/classifieds/submit")) {
      html = null;
    } else if (path.startsWith("/classifieds/") && path.endsWith("/edit")) {
      html = null;
    } else if (path.startsWith("/classifieds/")) {
      const slug = path.replace("/classifieds/", "");
      html = await renderClassifiedDetail(slug);
      // Expired/deleted classifieds → 410 Gone
      if (!html) {
        res.status(410).send(`<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Listing No Longer Available — The Videshi</title>
<meta name="robots" content="noindex"></head>
<body><h1>This classified listing has expired</h1>
<p>This listing is no longer available. <a href="${SITE}/classifieds">Browse classifieds</a></p></body></html>`);
        return;
      }
    } else if (path === "/cars") {
      html = await renderCarsIndex();
    } else if (path.startsWith("/cars/guide/") || path === "/cars/deals" || path === "/cars/compare") {
      // Static car guide pages — render minimal SEO shell
      const guideSlug = path.replace("/cars/guide/", "");
      const guideTitles: Record<string, string> = {
        "first-car-in-america": "Your First Car in America — A Complete Guide for Indian Immigrants",
        "lease-vs-buy": "Lease vs Buy — Which Is Better for New Immigrants?",
        "insurance-for-new-immigrants": "Car Insurance Guide for New Indian Immigrants",
        "best-family-suvs": "Best Family SUVs for Indian Families in 2026",
        "best-cars-under-30k": "Best Cars Under $30K for Indian Immigrants",
        "best-evs-2026": "Best Electric Vehicles for Indians in America — 2026",
        "india-vs-us-driving": "India vs US Driving — What Every New Immigrant Needs to Know",
        "cars-for-tech-professionals": "Best Cars for Indian Tech Professionals in the US",
      };
      const title = guideTitles[guideSlug] || "Car Guide — The Videshi";
      html = pageShell({
        title: `${title} — The Videshi`,
        description: `${title}. Expert car buying advice for the Indian diaspora.`,
        url: `${SITE}${path}`,
        body: `<main><h1>${esc(title)}</h1><p>Expert car buying guide for the Indian diaspora in America.</p></main>`,
      });
    } else if (path.startsWith("/cars/")) {
      const slug = path.replace("/cars/", "");
      html = await renderCarDetail(slug);
    } else if (path.startsWith("/articles/")) {
      const slug = path.replace("/articles/", "");
      html = await renderArticle(slug);
      // If article not found, try slug fallback (date suffix / hash tail)
      if (!html) {
        const redirect = await tryArticleSlugFallback(slug);
        if (redirect) {
          res.setHeader("Location", `${SITE}/articles/${redirect}`);
          res.status(301).send(`Moved to /articles/${redirect}`);
          return;
        }
        // Check if article exists but isn't published (draft/archived/rejected/killed)
        // → 410 Gone to tell Google to deindex
        const exists = await sbFetch(
          "p2_articles", "slug,status",
          `slug=eq.${encodeURIComponent(slug)}`, 1
        );
        if (exists.length) {
          res.status(410).send(`<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Article No Longer Available — The Videshi</title>
<meta name="robots" content="noindex"></head>
<body><h1>This article is no longer available</h1>
<p><a href="${SITE}">Back to homepage</a></p></body></html>`);
          return;
        }
      }
    } else if (["/about", "/contact", "/travel", "/immigration", "/stories"].includes(path)) {
      html = renderStaticPage(path);
    } else if (path.startsWith("/immigration/")) {
      // Immigration sub-pages: /immigration/green-card, /immigration/h1b, etc.
      const subPage = path.replace("/immigration/", "");
      const immigrationPages: Record<string, { title: string; description: string }> = {
        "green-card": { title: "Green Card Tracker", description: "Track green card processing times, visa bulletin dates, and EB category wait times for Indian immigrants." },
        "h1b": { title: "H-1B Visa Hub", description: "H-1B visa news, lottery results, transfer guides, and cap-exempt strategies for Indian tech workers." },
        "consulate-wait-times": { title: "US Consulate Wait Times in India", description: "Current visa interview wait times at US consulates in India — Mumbai, Delhi, Chennai, Hyderabad, Kolkata." },
        "processing-times": { title: "USCIS Processing Times", description: "Latest USCIS processing times for green cards, H-1B, EAD, and other immigration forms." },
        "visas": { title: "Visa Tracker", description: "Track US visa bulletin dates, priority dates, and processing times for Indian immigrants." },
        "guides": { title: "Immigration Guides", description: "Step-by-step immigration guides for Indian immigrants: H-1B, green card, OPT, and more." },
      };
      const pg = immigrationPages[subPage];
      if (pg) {
        html = pageShell({
          title: `${pg.title} — The Videshi`,
          description: pg.description,
          url: `${SITE}${path}`,
          body: `<main><h1>${esc(pg.title)}</h1><p>${esc(pg.description)}</p></main>`,
        });
      }
    } else if (path.startsWith("/stories/") && !path.includes("submit")) {
      // Individual community stories
      const slug = path.replace("/stories/", "");
      const rows = await sbFetch("community_stories", "title,slug,excerpt,body", `slug=eq.${encodeURIComponent(slug)}`, 1).catch(() => []);
      if (rows.length) {
        const s = rows[0];
        html = pageShell({
          title: `${s.title} — Community Stories | The Videshi`,
          description: s.excerpt || "A community story from the Indian diaspora.",
          url: `${SITE}${path}`,
          type: "article",
          body: `<article><h1>${esc(s.title)}</h1>${s.body ? toParagraphs(stripMarkdown(s.body)) : ""}</article>`,
        });
      }
    } else if (path === "/world-cup") {
      html = pageShell({
        title: "FIFA World Cup 2026 — Live Scores, Schedule & NRI Guide | The Videshi",
        description: "Complete FIFA World Cup 2026 coverage for Indians in America: live scores, group standings, match schedule, highlights, and an NRI guide to attending matches.",
        url: `${SITE}/world-cup`,
        body: `<main><h1>FIFA World Cup 2026</h1><p>Live scores, standings, highlights, and NRI guide to the 2026 World Cup across the US, Canada, and Mexico.</p></main>`,
      });
    } else if (path.startsWith("/watch/")) {
      // Streaming picks detail pages
      html = pageShell({
        title: "What to Watch — The Videshi",
        description: "Streaming picks, reviews, and recommendations for the Indian diaspora.",
        url: `${SITE}${path}`,
        body: `<main><h1>What to Watch</h1><p>Streaming picks and reviews curated for the Indian diaspora.</p></main>`,
      });
    } else if (path.startsWith("/travel/")) {
      // Travel destination pages
      const dest = path.replace("/travel/", "").split("/")[0];
      html = pageShell({
        title: `Travel: ${dest.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase())} — The Videshi`,
        description: `Travel guide and tips for ${dest.replace(/-/g, " ")} — visa info, destinations, and recommendations for Indian travelers.`,
        url: `${SITE}${path}`,
        body: `<main><h1>Travel Guide</h1><p>Destination guides and tips for the Indian diaspora.</p></main>`,
      });
    } else if (CATEGORIES[path.replace("/", "")]) {
      // Category page: /news, /entertainment, etc.
      html = await renderCategory(path.replace("/", ""));
    } else if (path.startsWith("/admin")) {
      // Never prerender admin
      html = null;
    }

    if (html) {
      res.setHeader("Content-Type", "text/html; charset=utf-8");
      res.setHeader("Cache-Control", "s-maxage=3600, stale-while-revalidate=86400");
      res.status(200).send(html);
    } else {
      // Unknown route or form page — return 404 so Google doesn't soft-404
      res.status(404).send(`<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Page Not Found — The Videshi</title>
<meta name="robots" content="noindex"></head>
<body><h1>404 — Page not found</h1><p><a href="${SITE}">Back to homepage</a></p></body></html>`);
    }
  } catch (e) {
    console.error("Prerender error:", e);
    res.status(500).send("Error");
  }
}
