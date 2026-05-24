import { supabase as supabaseTyped } from "@/integrations/supabase/client";

const supabase = supabaseTyped as unknown as {
  from: (table: string) => any;
};

/* ------------------------------------------------------------------ */
/* Types                                                              */
/* ------------------------------------------------------------------ */

export type Region = {
  key: string;
  label: string;
  emoji: string;
};

export type Destination = {
  key: string;
  label: string;
  region: string;
  description: string;
  bestMonths: string;
  budget: string;
  visaStatus: "visa-free" | "voa" | "e-visa" | "visa-required";
  visaNote: string;
  hasGuide: boolean;
};

export type VisaDashboardCard = {
  key: string;
  emoji: string;
  label: string;
  color: string;      // tailwind bg color for accent
  textColor: string;   // tailwind text color
  count: number;
  topDestinations: string[];
  description: string;
};

/* ------------------------------------------------------------------ */
/* Regions                                                            */
/* ------------------------------------------------------------------ */

export const REGIONS: Region[] = [
  { key: "all", label: "All", emoji: "🌍" },
  { key: "india", label: "India", emoji: "🇮🇳" },
  { key: "southeast-asia", label: "Southeast Asia", emoji: "🌏" },
  { key: "mexico-caribbean", label: "Mexico & Caribbean", emoji: "🌴" },
  { key: "europe", label: "Europe", emoji: "🇪🇺" },
  { key: "usa-canada", label: "USA & Canada", emoji: "🇺🇸" },
  { key: "middle-east-africa", label: "Middle East & Africa", emoji: "🏜️" },
  { key: "oceania", label: "Oceania", emoji: "🌊" },
];

/* ------------------------------------------------------------------ */
/* Destinations                                                       */
/* ------------------------------------------------------------------ */

export const DESTINATIONS: Destination[] = [
  // India
  { key: "rajasthan", label: "Rajasthan", region: "india", description: "Palaces, forts & desert culture", bestMonths: "Oct – Mar", budget: "$30–150/day", visaStatus: "visa-free", visaNote: "Indian passport: no visa", hasGuide: true },
  { key: "kerala", label: "Kerala", region: "india", description: "Backwaters, Ayurveda & spice hills", bestMonths: "Sep – Mar", budget: "$25–120/day", visaStatus: "visa-free", visaNote: "Indian passport: no visa", hasGuide: true },
  { key: "goa", label: "Goa", region: "india", description: "Beaches, nightlife & Portuguese charm", bestMonths: "Nov – Feb", budget: "$20–100/day", visaStatus: "visa-free", visaNote: "Indian passport: no visa", hasGuide: true },
  { key: "himachal-pradesh", label: "Himachal Pradesh", region: "india", description: "Mountain retreats & adventure treks", bestMonths: "Mar – Jun, Sep – Nov", budget: "$20–80/day", visaStatus: "visa-free", visaNote: "Indian passport: no visa", hasGuide: false },
  { key: "uttarakhand", label: "Uttarakhand", region: "india", description: "Spiritual heartland & Himalayan peaks", bestMonths: "Mar – Jun, Sep – Nov", budget: "$20–80/day", visaStatus: "visa-free", visaNote: "Indian passport: no visa", hasGuide: false },
  { key: "kashmir", label: "Kashmir", region: "india", description: "Dal Lake, houseboats & alpine meadows", bestMonths: "Apr – Oct", budget: "$25–100/day", visaStatus: "visa-free", visaNote: "Indian passport: no visa", hasGuide: false },
  { key: "tamil-nadu", label: "Tamil Nadu", region: "india", description: "Temples, Chettinad cuisine & hill stations", bestMonths: "Nov – Feb", budget: "$20–80/day", visaStatus: "visa-free", visaNote: "Indian passport: no visa", hasGuide: false },
  { key: "karnataka", label: "Karnataka", region: "india", description: "Bangalore, Mysore & Hampi ruins", bestMonths: "Oct – Feb", budget: "$20–90/day", visaStatus: "visa-free", visaNote: "Indian passport: no visa", hasGuide: false },
  { key: "northeast-india", label: "Northeast India", region: "india", description: "Untouched beauty, living root bridges", bestMonths: "Oct – Apr", budget: "$20–70/day", visaStatus: "visa-free", visaNote: "Indian passport: no visa (ILP needed for some states)", hasGuide: false },

  // Southeast Asia
  { key: "bali", label: "Bali", region: "southeast-asia", description: "Temples, rice terraces & surf", bestMonths: "Apr – Oct", budget: "$30–150/day", visaStatus: "visa-free", visaNote: "Free 30-day on arrival", hasGuide: true },
  { key: "thailand", label: "Thailand", region: "southeast-asia", description: "Street food, islands & temples", bestMonths: "Nov – Mar", budget: "$25–120/day", visaStatus: "visa-free", visaNote: "60-day visa-free for Indians", hasGuide: false },
  { key: "vietnam", label: "Vietnam", region: "southeast-asia", description: "Ha Long Bay, phở & motorbike roads", bestMonths: "Mar – May, Sep – Nov", budget: "$20–80/day", visaStatus: "e-visa", visaNote: "e-Visa available (30 days)", hasGuide: false },
  { key: "sri-lanka", label: "Sri Lanka", region: "southeast-asia", description: "Tea country, wildlife & ancient ruins", bestMonths: "Dec – Mar", budget: "$30–100/day", visaStatus: "e-visa", visaNote: "ETA online", hasGuide: true },
  { key: "maldives", label: "Maldives", region: "southeast-asia", description: "Overwater villas & crystal waters", bestMonths: "Nov – Apr", budget: "$80–500/day", visaStatus: "voa", visaNote: "Free 30-day on arrival", hasGuide: true },
  { key: "singapore", label: "Singapore", region: "southeast-asia", description: "Gardens, hawker food & futurism", bestMonths: "Year-round", budget: "$60–200/day", visaStatus: "visa-required", visaNote: "Visa required (or transit via US GC)", hasGuide: false },

  // Mexico & Caribbean
  { key: "cancun", label: "Cancún", region: "mexico-caribbean", description: "Turquoise water & Mayan ruins", bestMonths: "Dec – Apr", budget: "$50–200/day", visaStatus: "visa-free", visaNote: "Visa-free with valid US visa/GC", hasGuide: false },
  { key: "cabo", label: "Cabo San Lucas", region: "mexico-caribbean", description: "Desert meets ocean, luxury resorts", bestMonths: "Oct – May", budget: "$60–250/day", visaStatus: "visa-free", visaNote: "Visa-free with valid US visa/GC", hasGuide: false },
  { key: "riviera-maya", label: "Riviera Maya", region: "mexico-caribbean", description: "Cenotes, Tulum & boutique beaches", bestMonths: "Dec – Apr", budget: "$50–200/day", visaStatus: "visa-free", visaNote: "Visa-free with valid US visa/GC", hasGuide: false },
  { key: "puerto-vallarta", label: "Puerto Vallarta", region: "mexico-caribbean", description: "Pacific coast charm & art scene", bestMonths: "Nov – May", budget: "$40–150/day", visaStatus: "visa-free", visaNote: "Visa-free with valid US visa/GC", hasGuide: false },
  { key: "jamaica", label: "Jamaica", region: "mexico-caribbean", description: "Reggae, jerk chicken & Blue Mountains", bestMonths: "Nov – Apr", budget: "$50–200/day", visaStatus: "visa-free", visaNote: "Visa-free with valid US visa", hasGuide: false },
  { key: "dominican-republic", label: "Dominican Republic", region: "mexico-caribbean", description: "All-inclusive resorts & merengue", bestMonths: "Dec – Apr", budget: "$40–180/day", visaStatus: "visa-free", visaNote: "Tourist card on arrival ($10)", hasGuide: false },
  { key: "bahamas", label: "Bahamas", region: "mexico-caribbean", description: "Pink sand beaches & island hopping", bestMonths: "Dec – May", budget: "$60–300/day", visaStatus: "visa-required", visaNote: "Visa required for Indian passport", hasGuide: false },
  { key: "aruba", label: "Aruba", region: "mexico-caribbean", description: "One happy island — arid beaches & nightlife", bestMonths: "Year-round", budget: "$60–250/day", visaStatus: "visa-free", visaNote: "Visa-free with valid US visa", hasGuide: false },

  // Europe
  { key: "london", label: "London & UK", region: "europe", description: "History, theatre & afternoon tea", bestMonths: "May – Sep", budget: "$80–250/day", visaStatus: "visa-required", visaNote: "UK visa required", hasGuide: true },
  { key: "switzerland", label: "Switzerland", region: "europe", description: "Alps, chocolate & scenic trains", bestMonths: "Jun – Sep, Dec – Feb", budget: "$100–350/day", visaStatus: "visa-required", visaNote: "Schengen visa required", hasGuide: true },
  { key: "italy", label: "Italy", region: "europe", description: "Art, pasta & Amalfi Coast", bestMonths: "Apr – Jun, Sep – Oct", budget: "$60–200/day", visaStatus: "visa-required", visaNote: "Schengen visa required", hasGuide: false },
  { key: "france", label: "France", region: "europe", description: "Paris, Provence & world-class wine", bestMonths: "Apr – Jun, Sep – Oct", budget: "$70–250/day", visaStatus: "visa-required", visaNote: "Schengen visa required", hasGuide: false },
  { key: "spain", label: "Spain", region: "europe", description: "Tapas, flamenco & Mediterranean sun", bestMonths: "Apr – Jun, Sep – Oct", budget: "$50–180/day", visaStatus: "visa-required", visaNote: "Schengen visa required", hasGuide: false },
  { key: "greece", label: "Greece", region: "europe", description: "Santorini sunsets & ancient ruins", bestMonths: "May – Oct", budget: "$50–180/day", visaStatus: "visa-required", visaNote: "Schengen visa required", hasGuide: false },
  { key: "iceland", label: "Iceland", region: "europe", description: "Northern Lights & volcanic landscapes", bestMonths: "Jun – Aug, Sep – Mar (lights)", budget: "$80–300/day", visaStatus: "visa-required", visaNote: "Schengen visa required", hasGuide: false },
  { key: "portugal", label: "Portugal", region: "europe", description: "Pastel towns, fado & surf breaks", bestMonths: "Apr – Oct", budget: "$40–150/day", visaStatus: "visa-required", visaNote: "Schengen visa required", hasGuide: false },
  { key: "scandinavia", label: "Scandinavia", region: "europe", description: "Fjords, design & midnight sun", bestMonths: "Jun – Aug", budget: "$80–300/day", visaStatus: "visa-required", visaNote: "Schengen visa required", hasGuide: false },

  // USA & Canada
  { key: "hawaii", label: "Hawaii", region: "usa-canada", description: "Volcanos, surfing & luau feasts", bestMonths: "Apr – Oct", budget: "$80–300/day", visaStatus: "visa-free", visaNote: "Domestic travel (no visa needed)", hasGuide: false },
  { key: "national-parks", label: "National Parks", region: "usa-canada", description: "Yellowstone, Grand Canyon & Yosemite", bestMonths: "May – Sep", budget: "$50–200/day", visaStatus: "visa-free", visaNote: "Domestic travel (no visa needed)", hasGuide: false },
  { key: "new-york-city", label: "New York City", region: "usa-canada", description: "Broadway, pizza & skyline views", bestMonths: "Apr – Jun, Sep – Nov", budget: "$80–350/day", visaStatus: "visa-free", visaNote: "Domestic travel (no visa needed)", hasGuide: false },
  { key: "florida", label: "Florida", region: "usa-canada", description: "Theme parks, beaches & Everglades", bestMonths: "Nov – Apr", budget: "$50–250/day", visaStatus: "visa-free", visaNote: "Domestic travel (no visa needed)", hasGuide: false },
  { key: "alaska", label: "Alaska", region: "usa-canada", description: "Glaciers, bears & frontier wilderness", bestMonths: "Jun – Aug", budget: "$80–300/day", visaStatus: "visa-free", visaNote: "Domestic travel (no visa needed)", hasGuide: false },
  { key: "banff", label: "Banff & Canadian Rockies", region: "usa-canada", description: "Turquoise lakes & mountain grandeur", bestMonths: "Jun – Sep, Dec – Mar", budget: "$70–250/day", visaStatus: "visa-required", visaNote: "Canada eTA or visa needed", hasGuide: false },

  // Middle East & Africa
  { key: "dubai", label: "Dubai", region: "middle-east-africa", description: "Skyscrapers, souks & desert safaris", bestMonths: "Nov – Mar", budget: "$60–300/day", visaStatus: "e-visa", visaNote: "Visa on arrival (14/30 days)", hasGuide: false },
  { key: "abu-dhabi", label: "Abu Dhabi", region: "middle-east-africa", description: "Grand Mosque, Louvre & F1", bestMonths: "Nov – Mar", budget: "$60–250/day", visaStatus: "e-visa", visaNote: "Visa on arrival (14/30 days)", hasGuide: false },
  { key: "oman", label: "Oman", region: "middle-east-africa", description: "Wadis, fjords & Bedouin culture", bestMonths: "Oct – Mar", budget: "$40–150/day", visaStatus: "e-visa", visaNote: "e-Visa available", hasGuide: false },
  { key: "south-africa", label: "South Africa", region: "middle-east-africa", description: "Cape Town, safaris & wine country", bestMonths: "May – Sep", budget: "$40–180/day", visaStatus: "visa-required", visaNote: "Visa required for Indian passport", hasGuide: false },
  { key: "kenya", label: "Kenya Safari", region: "middle-east-africa", description: "Masai Mara, Big Five & Nairobi", bestMonths: "Jul – Oct", budget: "$50–300/day", visaStatus: "e-visa", visaNote: "e-Visa available", hasGuide: false },
  { key: "egypt", label: "Egypt", region: "middle-east-africa", description: "Pyramids, Nile cruises & Red Sea", bestMonths: "Oct – Apr", budget: "$30–120/day", visaStatus: "e-visa", visaNote: "e-Visa available", hasGuide: false },
  { key: "morocco", label: "Morocco", region: "middle-east-africa", description: "Medinas, Sahara & Atlas Mountains", bestMonths: "Mar – May, Sep – Nov", budget: "$30–120/day", visaStatus: "visa-required", visaNote: "Visa required for Indian passport", hasGuide: false },

  // Oceania
  { key: "new-zealand", label: "New Zealand", region: "oceania", description: "Fjords, Hobbiton & adrenaline capital", bestMonths: "Dec – Feb", budget: "$80–200/day", visaStatus: "e-visa", visaNote: "NZeTA required", hasGuide: true },
  { key: "australia", label: "Australia", region: "oceania", description: "Great Barrier Reef, outback & opera", bestMonths: "Sep – Nov, Mar – May", budget: "$70–250/day", visaStatus: "e-visa", visaNote: "e-Visa (subclass 601 or 651)", hasGuide: false },
  { key: "fiji", label: "Fiji", region: "oceania", description: "Coral reefs, bure stays & island time", bestMonths: "May – Oct", budget: "$50–250/day", visaStatus: "visa-free", visaNote: "4-month visa-free on arrival", hasGuide: false },
];

/* ------------------------------------------------------------------ */
/* Visa Dashboard Data                                                */
/* ------------------------------------------------------------------ */

export const VISA_DASHBOARD: VisaDashboardCard[] = [
  {
    key: "visa-free",
    emoji: "🟢",
    label: "Visa-Free",
    color: "bg-green-500/10",
    textColor: "text-green-600",
    count: 25,
    topDestinations: ["Thailand", "Indonesia", "Mauritius", "Nepal", "Bhutan", "Serbia", "Fiji", "Maldives"],
    description: "Countries Indian passport holders can visit without any visa",
  },
  {
    key: "voa",
    emoji: "🟡",
    label: "Visa on Arrival",
    color: "bg-yellow-500/10",
    textColor: "text-yellow-600",
    count: 30,
    topDestinations: ["Cambodia", "Laos", "Madagascar", "Seychelles", "Jordan", "Maldives", "Myanmar", "Tuvalu"],
    description: "Get your visa stamped at the airport on landing",
  },
  {
    key: "e-visa",
    emoji: "🔵",
    label: "e-Visa Available",
    color: "bg-blue-500/10",
    textColor: "text-blue-600",
    count: 50,
    topDestinations: ["Turkey", "Sri Lanka", "Australia", "Kenya", "UAE", "Vietnam", "New Zealand", "Egypt"],
    description: "Apply online before you fly — approved in days",
  },
  {
    key: "us-gc-perks",
    emoji: "🇺🇸",
    label: "US Green Card Perks",
    color: "bg-purple-500/10",
    textColor: "text-purple-600",
    count: 35,
    topDestinations: ["Mexico", "Turkey", "Philippines", "Costa Rica", "Panama", "Colombia", "Georgia", "Albania"],
    description: "Countries NRIs can visit with a US Green Card or valid US visa — no separate visa needed",
  },
];

/* ------------------------------------------------------------------ */
/* Visa badge helpers                                                 */
/* ------------------------------------------------------------------ */

export function visaBadgeColor(status: Destination["visaStatus"]): string {
  switch (status) {
    case "visa-free": return "bg-green-500/15 text-green-700";
    case "voa": return "bg-yellow-500/15 text-yellow-700";
    case "e-visa": return "bg-blue-500/15 text-blue-700";
    case "visa-required": return "bg-red-500/12 text-red-600";
  }
}

export function visaBadgeLabel(status: Destination["visaStatus"]): string {
  switch (status) {
    case "visa-free": return "No visa";
    case "voa": return "Visa on arrival";
    case "e-visa": return "e-Visa";
    case "visa-required": return "Visa required";
  }
}

/* ------------------------------------------------------------------ */
/* Data fetching                                                      */
/* ------------------------------------------------------------------ */

export async function getTravelNews(limit: number = 10): Promise<any[]> {
  const { data, error } = await supabase
    .from("p2_articles")
    .select("id,slug,headline,subheadline,image_url,category,published_at")
    .or("category.eq.travel,category.eq.Travel,category.ilike.%travel%")
    .eq("status", "published")
    .order("published_at", { ascending: false })
    .limit(limit);
  if (error) {
    console.error("travel news error:", error);
    return [];
  }
  return (data || []).map((a: any) => ({
    ...a,
    title: a.headline || a.title,
    excerpt: a.subheadline || a.excerpt || "",
  }));
}
