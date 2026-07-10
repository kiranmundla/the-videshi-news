import type { VercelRequest, VercelResponse } from "@vercel/node";

/* ------------------------------------------------------------------ */
/* POST /api/import-event                                             */
/* Fetches an event URL, extracts structured data from JSON-LD,       */
/* OpenGraph, and common meta tags, returns pre-filled form fields.   */
/* ------------------------------------------------------------------ */

interface ImportedEvent {
  title?: string;
  date?: string;        // YYYY-MM-DD
  end_date?: string;    // YYYY-MM-DD
  time?: string;        // HH:MM
  venue_name?: string;
  city?: string;
  state?: string;
  description?: string;
  image_url?: string;
  ticket_url?: string;
  category?: string;
}

const UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";

/* ---- helpers ---- */

function meta(html: string, property: string): string | null {
  // match both property="..." and name="..."
  const re = new RegExp(
    `<meta[^>]+(?:property|name)=["']${property.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}["'][^>]+content=["']([^"']*?)["']`,
    "is",
  );
  const m = html.match(re);
  if (m) return decodeHtml(m[1].trim());
  // also match content first
  const re2 = new RegExp(
    `<meta[^>]+content=["']([^"']*?)["'][^>]+(?:property|name)=["']${property.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}["']`,
    "is",
  );
  const m2 = html.match(re2);
  return m2 ? decodeHtml(m2[1].trim()) : null;
}

function decodeHtml(s: string): string {
  return s
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x27;/g, "'")
    .replace(/&#x2F;/g, "/");
}

function extractTitle(html: string): string | null {
  const m = html.match(/<title[^>]*>([^<]+)<\/title>/i);
  return m ? decodeHtml(m[1].trim()) : null;
}

function parseDate(dateStr: string | null | undefined): { date?: string; time?: string } {
  if (!dateStr) return {};
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return {};
    const date = d.toISOString().slice(0, 10);
    const hours = d.getUTCHours().toString().padStart(2, "0");
    const mins = d.getUTCMinutes().toString().padStart(2, "0");
    const time = hours !== "00" || mins !== "00" ? `${hours}:${mins}` : undefined;
    return { date, time };
  } catch {
    return {};
  }
}

// US states abbreviation map
const STATE_ABBR: Record<string, string> = {
  alabama:"AL",alaska:"AK",arizona:"AZ",arkansas:"AR",california:"CA",
  colorado:"CO",connecticut:"CT",delaware:"DE",florida:"FL",georgia:"GA",
  hawaii:"HI",idaho:"ID",illinois:"IL",indiana:"IN",iowa:"IA",
  kansas:"KS",kentucky:"KY",louisiana:"LA",maine:"ME",maryland:"MD",
  massachusetts:"MA",michigan:"MI",minnesota:"MN",mississippi:"MS",missouri:"MO",
  montana:"MT",nebraska:"NE",nevada:"NV","new hampshire":"NH","new jersey":"NJ",
  "new mexico":"NM","new york":"NY","north carolina":"NC","north dakota":"ND",ohio:"OH",
  oklahoma:"OK",oregon:"OR",pennsylvania:"PA","rhode island":"RI","south carolina":"SC",
  "south dakota":"SD",tennessee:"TN",texas:"TX",utah:"UT",vermont:"VT",
  virginia:"VA",washington:"WA","west virginia":"WV",wisconsin:"WI",wyoming:"WY",
  "district of columbia":"DC",
};
const STATE_CODES = new Set(Object.values(STATE_ABBR));

function parseLocation(loc: string | null | undefined): { venue_name?: string; city?: string; state?: string } {
  if (!loc) return {};
  // Split by commas and clean
  const parts = loc.split(",").map(s => s.trim()).filter(Boolean);
  if (parts.length === 0) return {};

  let venue_name: string | undefined;
  let city: string | undefined;
  let state: string | undefined;

  // Try to find state in the last part
  const lastPart = parts[parts.length - 1];
  const stateCheck = lastPart.replace(/\d{5}.*/, "").trim(); // strip zip code
  if (STATE_CODES.has(stateCheck.toUpperCase()) && stateCheck.length <= 3) {
    state = stateCheck.toUpperCase();
    parts.pop();
  } else if (STATE_ABBR[stateCheck.toLowerCase()]) {
    state = STATE_ABBR[stateCheck.toLowerCase()];
    parts.pop();
  }

  // Also check second-to-last for "City, ST zip" patterns
  if (!state && parts.length >= 2) {
    const secondLast = parts[parts.length - 1];
    const m = secondLast.match(/^(.+?)\s+([A-Z]{2})\s*\d{0,5}/);
    if (m && STATE_CODES.has(m[2])) {
      state = m[2];
      parts[parts.length - 1] = m[1].trim();
    }
  }

  if (parts.length >= 3) {
    venue_name = parts[0];
    city = parts[parts.length - 1];
  } else if (parts.length === 2) {
    // Could be "Venue, City" or "City, State"
    if (!state) {
      // If no state found, second is likely city
      venue_name = parts[0];
      city = parts[1];
    } else {
      city = parts[1] || parts[0];
      venue_name = parts.length > 1 ? parts[0] : undefined;
    }
  } else if (parts.length === 1) {
    city = parts[0];
  }

  return { venue_name, city, state };
}

/* Category keywords detection */
const CATEGORY_KEYWORDS: [string[], string][] = [
  [["garba", "dandiya", "raas", "bhangra", "salsa", "dance", "nachle"], "Dance"],
  [["concert", "music", "dj ", "bollywood night", "karaoke", "sangeet", "live band"], "Music"],
  [["comedy", "standup", "stand-up", "open mic", "improv", "laugh"], "Comedy"],
  [["cricket", "kabaddi", "badminton", "sports", "marathon", "5k", "run ", "tournament"], "Sports"],
  [["puja", "temple", "havan", "satsang", "kirtan", "bhajan", "prayer", "diwali", "navratri", "holi", "ganesh", "eid", "gurudwara"], "Religious"],
  [["food", "cooking", "biryani", "dinner", "brunch", "tasting", "culinary"], "Food"],
  [["festival", "mela", "fair", "carnival", "utsav", "fest "], "Festival"],
  [["workshop", "seminar", "class", "lecture", "education", "hackathon", "bootcamp"], "Education"],
  [["meetup", "networking", "community", "volunteer", "fundraiser", "charity"], "Community"],
  [["cultural", "classical", "theater", "theatre", "play ", "drama", "art "], "Cultural"],
];

function detectCategory(title: string, description?: string): string | undefined {
  const text = `${title} ${description || ""}`.toLowerCase();
  for (const [keywords, cat] of CATEGORY_KEYWORDS) {
    if (keywords.some(k => text.includes(k))) return cat;
  }
  return undefined;
}

/* ---- JSON-LD extraction ---- */
function extractJsonLd(html: string): ImportedEvent {
  const result: ImportedEvent = {};
  // Find all JSON-LD blocks
  const re = /<script[^>]+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    try {
      const data = JSON.parse(m[1]);
      const events = Array.isArray(data) ? data : data["@graph"] ? data["@graph"] : [data];
      for (const evt of events) {
        if (evt["@type"] !== "Event" && evt["@type"] !== "SocialEvent" && evt["@type"] !== "MusicEvent" && evt["@type"] !== "DanceEvent") continue;
        result.title = evt.name || result.title;
        result.description = evt.description || result.description;
        result.image_url = typeof evt.image === "string" ? evt.image : evt.image?.url || result.image_url;
        result.ticket_url = evt.url || evt.offers?.url || result.ticket_url;

        const start = parseDate(evt.startDate);
        if (start.date) result.date = start.date;
        if (start.time) result.time = start.time;

        const end = parseDate(evt.endDate);
        if (end.date && end.date !== result.date) result.end_date = end.date;

        // Location
        const loc = evt.location;
        if (loc) {
          if (typeof loc === "string") {
            Object.assign(result, parseLocation(loc));
          } else {
            result.venue_name = loc.name || result.venue_name;
            const addr = loc.address;
            if (typeof addr === "string") {
              Object.assign(result, parseLocation(addr));
            } else if (addr) {
              result.city = addr.addressLocality || result.city;
              result.state = addr.addressRegion || result.state;
            }
          }
        }
        break; // use first Event found
      }
    } catch {
      // invalid JSON-LD, skip
    }
  }
  return result;
}

/* ---- OG + meta extraction ---- */
function extractMeta(html: string): ImportedEvent {
  const result: ImportedEvent = {};
  result.title = meta(html, "og:title") || extractTitle(html) || undefined;
  result.description = meta(html, "og:description") || meta(html, "description") || undefined;
  result.image_url = meta(html, "og:image") || undefined;

  const startTime = meta(html, "event:start_time") || meta(html, "article:published_time");
  if (startTime) {
    const s = parseDate(startTime);
    if (s.date) result.date = s.date;
    if (s.time) result.time = s.time;
  }

  const endTime = meta(html, "event:end_time");
  if (endTime) {
    const e = parseDate(endTime);
    if (e.date && e.date !== result.date) result.end_date = e.date;
  }

  const loc = meta(html, "event:location") || meta(html, "og:locality");
  if (loc) Object.assign(result, parseLocation(loc));

  return result;
}

/* ---- main handler ---- */
export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ success: false, error: "Method not allowed" });
  }

  const { url } = req.body ?? {};
  if (!url || typeof url !== "string") {
    return res.status(400).json({ success: false, error: "Missing URL" });
  }

  // Basic URL validation
  let parsedUrl: URL;
  try {
    parsedUrl = new URL(url);
    if (!["http:", "https:"].includes(parsedUrl.protocol)) {
      return res.status(400).json({ success: false, error: "Invalid URL" });
    }
  } catch {
    return res.status(400).json({ success: false, error: "Invalid URL" });
  }

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);

    const response = await fetch(url, {
      headers: { "User-Agent": UA, Accept: "text/html,application/xhtml+xml,*/*" },
      signal: controller.signal,
      redirect: "follow",
    });
    clearTimeout(timeout);

    if (!response.ok) {
      return res.status(200).json({
        success: false,
        error: `Could not fetch URL (HTTP ${response.status})`,
      });
    }

    const html = await response.text();

    // Extract from JSON-LD first (most structured), then OG/meta as fallback
    const jsonLd = extractJsonLd(html);
    const ogMeta = extractMeta(html);

    // Merge: JSON-LD takes priority
    const data: ImportedEvent = {
      title: jsonLd.title || ogMeta.title,
      date: jsonLd.date || ogMeta.date,
      end_date: jsonLd.end_date || ogMeta.end_date,
      time: jsonLd.time || ogMeta.time,
      venue_name: jsonLd.venue_name || ogMeta.venue_name,
      city: jsonLd.city || ogMeta.city,
      state: jsonLd.state || ogMeta.state,
      description: jsonLd.description || ogMeta.description,
      image_url: jsonLd.image_url || ogMeta.image_url,
      ticket_url: jsonLd.ticket_url || ogMeta.ticket_url || url,
    };

    // Normalize state to abbreviation
    if (data.state && data.state.length > 2) {
      const abbr = STATE_ABBR[data.state.toLowerCase()];
      if (abbr) data.state = abbr;
    }

    // Clean description — strip HTML tags and truncate
    if (data.description) {
      data.description = data.description
        .replace(/<[^>]+>/g, " ")
        .replace(/\s+/g, " ")
        .trim()
        .slice(0, 500);
    }

    // Auto-detect category
    data.category = detectCategory(data.title || "", data.description);

    // Clean title — remove site suffix
    if (data.title) {
      data.title = data.title
        .replace(/\s*[|·–—]\s*(Eventbrite|Meetup|AllEvents|Facebook|Sulekha).*$/i, "")
        .trim();
    }

    return res.status(200).json({ success: true, data });
  } catch (err: any) {
    if (err.name === "AbortError") {
      return res.status(200).json({ success: false, error: "Request timed out. Try entering details manually." });
    }
    return res.status(200).json({ success: false, error: "Could not fetch event details. Try entering manually." });
  }
}
