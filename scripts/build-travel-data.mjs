#!/usr/bin/env node
/**
 * Curated travel-planner data for /travel — the single source behind:
 *   • the Holiday Planner (upcoming travel windows + book-by dates)
 *   • Destinations by Month ("best places to go in <month>")
 *   • the While-You're-in-India strip
 *   • per-destination cheapest-month / best-season facts on guide pages
 *
 * Seasonality facts are mainstream travel knowledge (peak / shoulder /
 * monsoon patterns), cross-checked against research/diaspora-travel-patterns.md
 * for festival dates and booking lead times. NO fares live here — fares come
 * only from public/data/flight-deals.json (real Duffel snapshots).
 *
 * Edit the curated objects below, then regenerate:
 *   node scripts/build-travel-data.mjs
 * Output: public/data/travel-by-month.json
 */
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const OUT = join(dirname(fileURLToPath(import.meta.url)), "..", "public", "data", "travel-by-month.json");

/* ------------------------------------------------------------------ */
/* Holiday windows — book_by = peak date minus ~120 days (research §5) */
/* ------------------------------------------------------------------ */
const holiday_windows = [
  {
    id: "thanksgiving-2026",
    name: "Thanksgiving",
    emoji: "🦃",
    start: "2026-11-25",
    end: "2026-11-29",
    peak: true,
    book_by: "2026-07-28",
    note: "The long weekend — a short US getaway, or the launchpad for a longer India run.",
  },
  {
    id: "christmas-2026",
    name: "Christmas & New Year",
    emoji: "🎄",
    start: "2026-12-20",
    end: "2027-01-03",
    peak: true,
    book_by: "2026-08-22",
    note: "The year's biggest travel window — winter break, family reunions, peak fares everywhere.",
  },
  {
    id: "spring-break-2027",
    name: "Spring Break",
    emoji: "🌸",
    start: "2027-03-13",
    end: "2027-03-21",
    peak: false,
    book_by: "2027-01-12",
    note: "School spring break — and Holi falls on Mar 22, so an India trip can catch both.",
  },
  {
    id: "summer-2027",
    name: "Summer Break",
    emoji: "☀️",
    start: "2027-06-12",
    end: "2027-07-25",
    peak: true,
    book_by: "2027-02-12",
    note: "The big family trip — school's out, wedding season in India, and the year's longest stays.",
  },
  {
    id: "diwali-2027",
    name: "Diwali",
    emoji: "🪔",
    start: "2027-10-22",
    end: "2027-11-07",
    peak: true,
    book_by: "2027-07-01",
    note: "Diwali falls on Friday, Oct 29, 2027 — the biggest family-reunion window of the year.",
  },
];

/* ------------------------------------------------------------------ */
/* Destination facts — cheapest month vs best season (guide pages)    */
/* ------------------------------------------------------------------ */
const destination_facts = {
  goa:                { cheapest_month: "Jun – Sep (monsoon)",            best_season: "Nov – Feb" },
  kerala:             { cheapest_month: "Jun – Aug (monsoon)",            best_season: "Dec – Feb" },
  rajasthan:          { cheapest_month: "May – Jun (peak heat)",          best_season: "Oct – Mar" },
  "himachal-pradesh": { cheapest_month: "Jul – Aug (monsoon)",            best_season: "Mar – Jun, Sep – Nov" },
  kashmir:            { cheapest_month: "Nov & late Mar (shoulder)",      best_season: "Apr – Oct" },
  "tamil-nadu":       { cheapest_month: "Apr – Jun (hot season)",         best_season: "Nov – Feb" },
  karnataka:          { cheapest_month: "Jun – Aug (monsoon)",            best_season: "Oct – Feb" },
  uttarakhand:        { cheapest_month: "Jul – Aug (monsoon)",            best_season: "Mar – Jun, Sep – Nov" },
  "northeast-india":  { cheapest_month: "Jun – Sep (heavy rains)",        best_season: "Oct – Apr" },
  thailand:           { cheapest_month: "May – Oct (rainy season)",       best_season: "Nov – Feb" },
  dubai:              { cheapest_month: "Jun – Aug (extreme heat)",       best_season: "Nov – Mar" },
  maldives:           { cheapest_month: "May – Oct (monsoon)",            best_season: "Nov – Apr" },
  "sri-lanka":        { cheapest_month: "May – Sep (southwest monsoon)",  best_season: "Dec – Mar" },
  cancun:             { cheapest_month: "Sep – Oct (hurricane season)",   best_season: "Dec – Apr" },
  hawaii:             { cheapest_month: "Late Jan – Feb, Sep – Oct (shoulder)", best_season: "Apr – Oct · whales Dec – Apr" },
  "new-zealand":      { cheapest_month: "May – Aug (winter)",             best_season: "Dec – Feb" },
  australia:          { cheapest_month: "Jun – Aug (southern winter)",    best_season: "Sep – Nov, Mar – May" },
  japan:              { cheapest_month: "Jan – Feb (cold, post-holiday)", best_season: "Mar – May, Oct – Nov" },
  vietnam:            { cheapest_month: "Jun – Aug (hot & rainy)",        best_season: "Mar – May, Sep – Nov" },
  bali:               { cheapest_month: "Nov – Mar (rainy season)",       best_season: "Apr – Oct" },
  iceland:            { cheapest_month: "Jan & Nov (darkest weeks)",      best_season: "Jun – Aug · Northern Lights Sep – Mar" },
  greece:             { cheapest_month: "Nov – Mar (islands wind down)",  best_season: "May – Oct" },
  florida:            { cheapest_month: "Jan & Aug – Sep",                best_season: "Nov – Apr" },
  banff:              { cheapest_month: "Apr – May & Nov (shoulder)",     best_season: "Jun – Sep · ski Dec – Mar" },
};

/* ------------------------------------------------------------------ */
/* Destinations by month — Nov 2026 → Apr 2027                        */
/* group: "india" | "usa" | "international"                           */
/* ------------------------------------------------------------------ */
const months = [
  {
    month: "2026-11",
    label: "November 2026",
    picks: [
      { key: "goa", group: "india", why: "Beach season opens — dry, sunny days in the mid-80s, and Arpora's Saturday Night Market is back." },
      { key: "dubai", group: "international", why: "Peak season begins — 75–85°F days made for rooftops and desert safaris, before the December rush." },
      { key: "thailand", group: "international", why: "The cool, dry season starts — Bangkok and the islands at their most comfortable." },
      { key: "rajasthan", group: "india", why: "Post-monsoon and cool — and the Pushkar Camel Fair, one of India's great spectacles, falls this month." },
      { key: "hawaii", group: "usa", why: "Shoulder-season fares before the holidays, and the first humpback whales arrive off Maui." },
      { key: "maldives", group: "international", why: "The dry season begins — early-November rates still sit below the December peak." },
    ],
  },
  {
    month: "2026-12",
    label: "December 2026",
    picks: [
      { key: "cancun", group: "international", why: "Dry season at its best — turquoise water and mid-80s. Book the holiday weeks early." },
      { key: "kerala", group: "india", why: "Kerala at its finest — cool, green and post-monsoon. Houseboat season on the backwaters." },
      { key: "new-zealand", group: "international", why: "Southern-hemisphere summer — long days and peak hiking in Fiordland and the Southern Alps." },
      { key: "goa", group: "india", why: "Peak season — Christmas and New Year on the beach, India's biggest party week." },
      { key: "sri-lanka", group: "international", why: "The west and south coasts enter their dry season — Galle and Mirissa at their best." },
      { key: "florida", group: "usa", why: "Mild, dry winter — theme parks and beaches without the summer humidity and storms." },
    ],
  },
  {
    month: "2027-01",
    label: "January 2027",
    picks: [
      { key: "thailand", group: "international", why: "The coolest, driest month of the year — peak season across Bangkok, Chiang Mai and the islands." },
      { key: "goa", group: "india", why: "Peak season continues — warm seas and cool nights, and the New Year crowds thin after mid-month." },
      { key: "kerala", group: "india", why: "Backwaters at their best — a restorative add-on to a January family trip home." },
      { key: "dubai", group: "international", why: "Shopping-festival season with the year's best weather — mid-70s and sunny every day." },
      { key: "hawaii", group: "usa", why: "Peak whale-watching — humpbacks breach off Maui all winter long." },
      { key: "australia", group: "international", why: "Summer down under — Sydney and Melbourne at their warmest, festival season in full swing." },
    ],
  },
  {
    month: "2027-02",
    label: "February 2027",
    picks: [
      { key: "kerala", group: "india", why: "The last of the cool, dry weeks — and US–India fares dip after the holidays, well below December." },
      { key: "maldives", group: "international", why: "The driest month of the year — glassy seas and peak diving visibility." },
      { key: "cancun", group: "international", why: "Dry season continues, and the spring-break crowds haven't arrived yet." },
      { key: "iceland", group: "international", why: "Northern Lights season with the days finally lengthening — frozen waterfalls and dark-sky nights." },
      { key: "rajasthan", group: "india", why: "Desert-festival season around Jaisalmer, and cool evenings across the fort cities." },
      { key: "new-zealand", group: "international", why: "Late summer — warm seas, harvest season in the vineyards, fewer crowds once local schools return." },
    ],
  },
  {
    month: "2027-03",
    label: "March 2027",
    picks: [
      { key: "japan", group: "international", why: "Cherry-blossom season opens in late March — the most sought-after travel weeks of the year." },
      { key: "vietnam", group: "international", why: "The best all-round month — dry in the north, warm and sunny in the south." },
      { key: "himachal-pradesh", group: "india", why: "Spring in the hills — snow peaks on the horizon and rhododendrons in bloom." },
      { key: "hawaii", group: "usa", why: "Whale season continues into spring, with softer shoulder-season fares." },
      { key: "sri-lanka", group: "international", why: "The last dry-season weeks on the west and south coasts before the monsoon turns." },
      { key: "kerala", group: "india", why: "Warm and dry early in the month — catch the tail of the season before the April heat." },
    ],
  },
  {
    month: "2027-04",
    label: "April 2027",
    picks: [
      { key: "japan", group: "international", why: "Peak sakura moves north — Kyoto in early April, Hokkaido by month's end." },
      { key: "bali", group: "international", why: "The dry season begins — emerald rice terraces, and the summer crowds still two months away." },
      { key: "kashmir", group: "india", why: "Asia's largest tulip garden blooms in Srinagar, and the alpine meadows open up." },
      { key: "greece", group: "international", why: "Spring shoulder season — Athens and the islands warm up before the summer rush." },
      { key: "hawaii", group: "usa", why: "Whale season wraps up and warm, dry spring weather settles in." },
      { key: "vietnam", group: "international", why: "Dry and warm almost everywhere — the last month before summer heat and rains." },
    ],
  },
];

/* ------------------------------------------------------------------ */
/* While you're in India — add-on destinations for a family trip      */
/* ------------------------------------------------------------------ */
const in_india = [
  { key: "goa", blurb: "India's beach capital — decompress here after the long-haul flight in." },
  { key: "kerala", blurb: "Backwaters, houseboats and Ayurveda — India's most restorative state." },
  { key: "rajasthan", blurb: "Jaipur, Udaipur, Jodhpur — palaces and forts, best in the cool months." },
  { key: "himachal-pradesh", blurb: "Manali, Dharamshala, Shimla — the hill stations above the plains." },
  { key: "tamil-nadu", blurb: "Pondicherry's French quarter, Mahabalipuram's shore temples, Ooty's hills." },
  { key: "kashmir", blurb: "Dal Lake houseboats, Srinagar's gardens and alpine meadows." },
  { key: "karnataka", blurb: "Hampi's ruins, Mysore's palace and the coffee hills of Coorg." },
  { key: "uttarakhand", blurb: "Rishikesh, the Char Dham trailheads and front-row Himalayan views." },
];

const data = {
  generated_at: new Date().toISOString(),
  source: "scripts/build-travel-data.mjs (curated)",
  holiday_windows,
  destination_facts,
  months,
  in_india,
};

writeFileSync(OUT, JSON.stringify(data, null, 2) + "\n");
console.log(`Wrote ${OUT}: ${holiday_windows.length} windows, ${months.length} months, ${months.reduce((n, m) => n + m.picks.length, 0)} picks, ${in_india.length} in-India, ${Object.keys(destination_facts).length} destination facts`);
