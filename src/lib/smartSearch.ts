/**
 * Smart Search — client-side NLP-lite query parser for Events.
 *
 * Extracts structured intent from a natural-language query:
 *   "free garba near dallas this weekend"
 *   → { dateFilter: "weekend", cityHints: ["Dallas"], categoryHints: ["Dance"],
 *       priceFilter: "free", keywords: ["garba"] }
 */

/* ------------------------------------------------------------------ */
/* Types                                                              */
/* ------------------------------------------------------------------ */

export type DateFilterKey =
  | "today"
  | "tomorrow"
  | "weekend"
  | "week"
  | "month"
  | null;

export interface ParsedSearch {
  dateFilter: DateFilterKey;
  cityHints: string[];       // resolved city names (e.g. "San Francisco")
  stateHints: string[];      // resolved state codes (e.g. "NJ")
  categoryHints: string[];   // DB category values (e.g. "Music", "Dance")
  priceFilter: "free" | null;
  keywords: string[];        // remaining tokens for text matching
}

/* ------------------------------------------------------------------ */
/* City name shortcuts                                                */
/* ------------------------------------------------------------------ */

const CITY_ALIASES: Record<string, string[]> = {
  "sf":        ["San Francisco"],
  "san fran":  ["San Francisco"],
  "nyc":       ["New York"],
  "ny":        ["New York"],
  "la":        ["Los Angeles"],
  "dc":        ["Washington"],
  "bay area":  ["San Francisco", "San Jose", "Fremont", "Sunnyvale", "Oakland", "Palo Alto", "Santa Clara", "Milpitas"],
  "silicon valley": ["San Jose", "Sunnyvale", "Santa Clara", "Cupertino", "Mountain View", "Palo Alto"],
  "dfw":       ["Dallas", "Fort Worth", "Plano", "Irving", "Frisco"],
  "socal":     ["Los Angeles", "Irvine", "Anaheim", "San Diego"],
  "south florida": ["Miami", "Fort Lauderdale", "Hollywood"],
  "tri-state": ["New York", "Edison", "Jersey City", "Newark"],
};

const STATE_ALIASES: Record<string, string> = {
  "nj":           "NJ",
  "new jersey":   "NJ",
  "jersey":       "NJ",
  "california":   "CA",
  "texas":        "TX",
  "florida":      "FL",
  "georgia":      "GA",
  "illinois":     "IL",
  "pennsylvania": "PA",
  "ohio":         "OH",
  "michigan":     "MI",
  "virginia":     "VA",
  "maryland":     "MD",
  "massachusetts":"MA",
  "washington state": "WA",
  "connecticut":  "CT",
  "north carolina": "NC",
  "tennessee":    "TN",
  "colorado":     "CO",
  "arizona":      "AZ",
  "minnesota":    "MN",
  "indiana":      "IN",
  "oregon":       "OR",
};

/** Single-word city names that we can match directly */
const KNOWN_CITIES: string[] = [
  "Dallas", "Houston", "Chicago", "Seattle", "Atlanta", "Boston",
  "Denver", "Nashville", "Charlotte", "Philadelphia", "Baltimore",
  "Columbus", "Detroit", "Miami", "Tampa", "Orlando", "Jacksonville",
  "Phoenix", "Austin", "Portland", "Raleigh", "Durham", "Pittsburgh",
  "Edison", "Plano", "Fremont", "Irvine", "Sunnyvale",
];

/* ------------------------------------------------------------------ */
/* Category keywords                                                  */
/* ------------------------------------------------------------------ */

const CATEGORY_MAP: Record<string, string> = {
  // Music
  "concert":   "Music",
  "concerts":  "Music",
  "music":     "Music",
  "singing":   "Music",
  "singer":    "Music",
  "bollywood": "Music",
  "qawwali":   "Music",
  "ghazal":    "Music",
  "carnatic":  "Music",
  "hindustani":"Music",
  "bhajan":    "Music",

  // Comedy
  "comedy":    "Comedy",
  "standup":   "Comedy",
  "stand-up":  "Comedy",
  "comedian":  "Comedy",
  "jokes":     "Comedy",
  "funny":     "Comedy",

  // Dance
  "dance":     "Dance",
  "garba":     "Dance",
  "dandiya":   "Dance",
  "raas":      "Dance",
  "navratri":  "Dance",
  "kathak":    "Dance",
  "bharatanatyam": "Dance",
  "bhangra":   "Dance",

  // Food
  "food":      "Food",
  "dinner":    "Food",
  "brunch":    "Food",
  "cooking":   "Food",
  "chef":      "Food",
  "biryani":   "Food",
  "dosa":      "Food",
  "street food": "Food",
  "tasting":   "Food",

  // Religious / Spiritual
  "temple":    "Religious",
  "puja":      "Religious",
  "pooja":     "Religious",
  "prayer":    "Religious",
  "kirtan":    "Religious",
  "satsang":   "Religious",
  "mandir":    "Religious",
  "gurudwara": "Religious",
  "mosque":    "Religious",
  "church":    "Religious",
  "diwali":    "Religious",
  "holi":      "Religious",
  "eid":       "Religious",
  "ganesh":    "Religious",
  "durga":     "Religious",

  // Sports
  "cricket":   "Sports",
  "sports":    "Sports",
  "kabaddi":   "Sports",
  "badminton": "Sports",
  "soccer":    "Sports",
  "football":  "Sports",
  "marathon":  "Sports",
  "run":       "Sports",
  "yoga":      "Sports",

  // Cultural / Festival
  "festival":  "Festival",
  "mela":      "Festival",
  "fair":      "Festival",
  "cultural":  "Cultural",
  "heritage":  "Cultural",
  "art":       "Cultural",
  "exhibition":"Cultural",
  "film":      "Cultural",
  "movie":     "Cultural",
  "cinema":    "Cultural",

  // Education
  "workshop":  "Education",
  "seminar":   "Education",
  "webinar":   "Education",
  "class":     "Education",
  "course":    "Education",
  "training":  "Education",
  "talk":      "Education",
  "lecture":   "Education",
  "hackathon": "Education",

  // Community
  "meetup":    "Community",
  "networking":"Community",
  "fundraiser":"Community",
  "volunteer": "Community",
  "charity":   "Community",
};

/* ------------------------------------------------------------------ */
/* Date keywords                                                      */
/* ------------------------------------------------------------------ */

interface DatePattern {
  pattern: RegExp;
  filter: DateFilterKey;
}

const DATE_PATTERNS: DatePattern[] = [
  { pattern: /\b(this\s+)?weekend\b/i,    filter: "weekend" },
  { pattern: /\bthis\s+week\b/i,          filter: "week" },
  { pattern: /\bthis\s+month\b/i,         filter: "month" },
  { pattern: /\btonight\b/i,              filter: "today" },
  { pattern: /\btoday\b/i,                filter: "today" },
  { pattern: /\btomorrow\b/i,             filter: "tomorrow" },
  { pattern: /\btomrw\b/i,                filter: "tomorrow" },
];

/* ------------------------------------------------------------------ */
/* Location extraction patterns                                       */
/* ------------------------------------------------------------------ */

const LOCATION_PATTERNS: RegExp[] = [
  /\b(?:near|in|around|at)\s+(.+?)(?:\s+(?:this|today|tomorrow|tonight|weekend|week|month|free|$))/i,
  /\b(?:near|in|around|at)\s+(.+)$/i,
];

/* ------------------------------------------------------------------ */
/* Parser                                                             */
/* ------------------------------------------------------------------ */

export function parseSearchQuery(query: string): ParsedSearch {
  const result: ParsedSearch = {
    dateFilter: null,
    cityHints: [],
    stateHints: [],
    categoryHints: [],
    priceFilter: null,
    keywords: [],
  };

  if (!query.trim()) return result;

  let remaining = query.trim();

  // 1. Extract date filter
  for (const dp of DATE_PATTERNS) {
    if (dp.pattern.test(remaining)) {
      result.dateFilter = dp.filter;
      remaining = remaining.replace(dp.pattern, " ").trim();
      break;
    }
  }

  // 2. Extract "free" / price filter
  if (/\bfree\b/i.test(remaining)) {
    result.priceFilter = "free";
    remaining = remaining.replace(/\bfree\b/gi, " ").trim();
  }

  // 3. Extract location (multi-word aliases first, then patterns)
  const lowerRemaining = remaining.toLowerCase();

  // Check multi-word city aliases first (sorted longest first to avoid partial matches)
  const sortedAliases = Object.keys(CITY_ALIASES).sort((a, b) => b.length - a.length);
  for (const alias of sortedAliases) {
    const idx = lowerRemaining.indexOf(alias);
    if (idx !== -1) {
      result.cityHints.push(...CITY_ALIASES[alias]);
      remaining = remaining.slice(0, idx) + remaining.slice(idx + alias.length);
      break; // Only match one city alias
    }
  }

  // Check multi-word state aliases
  if (result.cityHints.length === 0) {
    const sortedStates = Object.keys(STATE_ALIASES).sort((a, b) => b.length - a.length);
    for (const alias of sortedStates) {
      const idx = remaining.toLowerCase().indexOf(alias);
      if (idx !== -1) {
        result.stateHints.push(STATE_ALIASES[alias]);
        remaining = remaining.slice(0, idx) + remaining.slice(idx + alias.length);
        break;
      }
    }
  }

  // If no alias matched, try "near/in <city>" patterns
  if (result.cityHints.length === 0 && result.stateHints.length === 0) {
    for (const pat of LOCATION_PATTERNS) {
      const m = remaining.match(pat);
      if (m && m[1]) {
        const locationText = m[1].trim();
        // Check if it's a known city
        const cityMatch = KNOWN_CITIES.find(
          (c) => c.toLowerCase() === locationText.toLowerCase()
        );
        if (cityMatch) {
          result.cityHints.push(cityMatch);
          remaining = remaining.replace(pat, " ").trim();
          break;
        }
        // Check city aliases
        const aliasMatch = CITY_ALIASES[locationText.toLowerCase()];
        if (aliasMatch) {
          result.cityHints.push(...aliasMatch);
          remaining = remaining.replace(pat, " ").trim();
          break;
        }
        // Check state aliases
        const stateMatch = STATE_ALIASES[locationText.toLowerCase()];
        if (stateMatch) {
          result.stateHints.push(stateMatch);
          remaining = remaining.replace(pat, " ").trim();
          break;
        }
      }
    }
  }

  // Remove dangling prepositions
  remaining = remaining.replace(/\b(near|in|around|at)\s*$/i, "").trim();
  remaining = remaining.replace(/\b(near|in|around|at)\s*,?\s*/i, " ").trim();

  // 4. Extract categories from remaining tokens
  const words = remaining.toLowerCase().split(/\s+/).filter(Boolean);
  const usedWords = new Set<string>();

  // Check multi-word category terms first
  const multiWordCategories = Object.keys(CATEGORY_MAP).filter((k) => k.includes(" "));
  for (const term of multiWordCategories) {
    if (remaining.toLowerCase().includes(term)) {
      const cat = CATEGORY_MAP[term];
      if (!result.categoryHints.includes(cat)) {
        result.categoryHints.push(cat);
      }
      remaining = remaining.replace(new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi"), " ").trim();
    }
  }

  // Check single-word category terms
  for (const word of words) {
    if (usedWords.has(word)) continue;
    const cat = CATEGORY_MAP[word];
    if (cat && !result.categoryHints.includes(cat)) {
      result.categoryHints.push(cat);
      usedWords.add(word);
    }
  }

  // 5. Remaining words are keywords for text search
  const finalWords = remaining
    .split(/\s+/)
    .filter(Boolean)
    .filter((w) => !usedWords.has(w.toLowerCase()))
    .filter((w) => !/^(near|in|around|at|the|and|or|for|a|an|to|of)$/i.test(w));

  result.keywords = finalWords;

  return result;
}

/* ------------------------------------------------------------------ */
/* Client-side fuzzy keyword matcher                                  */
/* ------------------------------------------------------------------ */

/**
 * Check if an event matches the remaining keywords (after structured
 * filters have been extracted). Each keyword must appear in at least
 * one of the event's text fields (partial match, case-insensitive).
 */
export function matchesKeywords(
  event: {
    title?: string | null;
    description?: string | null;
    long_description?: string | null;
    artist_info?: string | null;
    venue_name?: string | null;
    city?: string | null;
    organizer?: string | null;
  },
  keywords: string[],
): boolean {
  if (keywords.length === 0) return true;

  const haystack = [
    event.title,
    event.description,
    event.long_description,
    event.artist_info,
    event.venue_name,
    event.city,
    event.organizer,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  return keywords.every((kw) => haystack.includes(kw.toLowerCase()));
}

/* ------------------------------------------------------------------ */
/* Price filter matcher                                                */
/* ------------------------------------------------------------------ */

export function matchesFreeFilter(priceRange: string | null | undefined): boolean {
  if (!priceRange) return true; // no price listed = assume free
  const lower = priceRange.toLowerCase().trim();
  return (
    lower === "free" ||
    lower === "$0" ||
    lower === "$0.00" ||
    lower === "0" ||
    lower === "no cover" ||
    lower === ""
  );
}

/* ------------------------------------------------------------------ */
/* Date range helpers                                                 */
/* ------------------------------------------------------------------ */

function toDateStr(d: Date): string {
  return d.toISOString().slice(0, 10);
}

/**
 * Compute the date range for a given date filter key.
 */
export function getDateFilterRange(key: DateFilterKey): { from: string; to: string } | null {
  if (!key) return null;

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  switch (key) {
    case "today": {
      return { from: toDateStr(today), to: toDateStr(today) };
    }
    case "tomorrow": {
      const tmrw = new Date(today);
      tmrw.setDate(today.getDate() + 1);
      return { from: toDateStr(tmrw), to: toDateStr(tmrw) };
    }
    case "weekend": {
      const dow = today.getDay(); // 0=Sun, 6=Sat
      let sat: Date;
      if (dow === 6) {
        // It's Saturday — this weekend is today+tomorrow
        sat = new Date(today);
      } else if (dow === 0) {
        // It's Sunday — show next weekend
        sat = new Date(today);
        sat.setDate(today.getDate() + 6);
      } else {
        // Mon-Fri — upcoming Saturday
        sat = new Date(today);
        sat.setDate(today.getDate() + (6 - dow));
      }
      const sun = new Date(sat);
      sun.setDate(sat.getDate() + 1);
      return { from: toDateStr(sat), to: toDateStr(sun) };
    }
    case "week": {
      const endOfWeek = new Date(today);
      const dow = today.getDay();
      endOfWeek.setDate(today.getDate() + (7 - dow)); // next Sunday
      return { from: toDateStr(today), to: toDateStr(endOfWeek) };
    }
    case "month": {
      const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
      return { from: toDateStr(today), to: toDateStr(endOfMonth) };
    }
    default:
      return null;
  }
}

/* ------------------------------------------------------------------ */
/* Smart search chip labels                                           */
/* ------------------------------------------------------------------ */

const DATE_LABELS: Record<string, string> = {
  today: "📅 Today",
  tomorrow: "📅 Tomorrow",
  weekend: "📅 This Weekend",
  week: "📅 This Week",
  month: "📅 This Month",
};

export function getSmartChips(parsed: ParsedSearch): string[] {
  const chips: string[] = [];
  if (parsed.dateFilter) chips.push(DATE_LABELS[parsed.dateFilter] || `📅 ${parsed.dateFilter}`);
  if (parsed.cityHints.length > 0) {
    const label = parsed.cityHints.length <= 2
      ? parsed.cityHints.join(", ")
      : `${parsed.cityHints[0]} area`;
    chips.push(`📍 ${label}`);
  }
  if (parsed.stateHints.length > 0) chips.push(`📍 ${parsed.stateHints[0]}`);
  if (parsed.categoryHints.length > 0) {
    const emojis: Record<string, string> = {
      Music: "🎵", Comedy: "😂", Dance: "💃", Food: "🍛",
      Religious: "🙏", Sports: "🏏", Festival: "🪔", Cultural: "🎭",
      Education: "🎓", Community: "🤝",
    };
    for (const cat of parsed.categoryHints) {
      chips.push(`${emojis[cat] || "🎪"} ${cat}`);
    }
  }
  if (parsed.priceFilter === "free") chips.push("🆓 Free");
  return chips;
}
