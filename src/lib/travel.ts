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

export type VisaStatus = "visa-free" | "voa" | "e-visa" | "visa-required";
export type VisaHolderStatus = "indian-passport" | "us-citizen" | "green-card";

export type VisaInfo = { status: VisaStatus; note: string };

export type Destination = {
  key: string;
  label: string;
  region: string;
  description: string;
  bestMonths: string;
  budget: string;
  visa: Record<VisaHolderStatus, VisaInfo>;
  hasGuide: boolean;
};

export type VisaDashboardCard = {
  key: string;
  emoji: string;
  label: string;
  color: string;
  textColor: string;
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
/* Helper to build visa record                                        */
/* ------------------------------------------------------------------ */
function v(
  ip: [VisaStatus, string],
  us: [VisaStatus, string],
  gc: [VisaStatus, string],
): Record<VisaHolderStatus, VisaInfo> {
  return {
    "indian-passport": { status: ip[0], note: ip[1] },
    "us-citizen": { status: us[0], note: us[1] },
    "green-card": { status: gc[0], note: gc[1] },
  };
}

/* ------------------------------------------------------------------ */
/* Destinations                                                       */
/* ------------------------------------------------------------------ */

export const DESTINATIONS: Destination[] = [
  // ── India ──────────────────────────────────────────────────────────
  { key: "rajasthan", label: "Rajasthan", region: "india", description: "Palaces, forts & desert culture", bestMonths: "Oct – Mar", budget: "$30–150/day",
    visa: v(["visa-free","No visa needed"],["e-visa","e-Visa required for India"],["visa-free","No visa (Indian citizen)"]), hasGuide: true },
  { key: "kerala", label: "Kerala", region: "india", description: "Backwaters, Ayurveda & spice hills", bestMonths: "Sep – Mar", budget: "$25–120/day",
    visa: v(["visa-free","No visa needed"],["e-visa","e-Visa required for India"],["visa-free","No visa (Indian citizen)"]), hasGuide: true },
  { key: "goa", label: "Goa", region: "india", description: "Beaches, nightlife & Portuguese charm", bestMonths: "Nov – Feb", budget: "$20–100/day",
    visa: v(["visa-free","No visa needed"],["e-visa","e-Visa required for India"],["visa-free","No visa (Indian citizen)"]), hasGuide: true },
  { key: "himachal-pradesh", label: "Himachal Pradesh", region: "india", description: "Mountain retreats & adventure treks", bestMonths: "Mar – Jun, Sep – Nov", budget: "$20–80/day",
    visa: v(["visa-free","No visa needed"],["e-visa","e-Visa required for India"],["visa-free","No visa (Indian citizen)"]), hasGuide: true },
  { key: "uttarakhand", label: "Uttarakhand", region: "india", description: "Spiritual heartland & Himalayan peaks", bestMonths: "Mar – Jun, Sep – Nov", budget: "$20–80/day",
    visa: v(["visa-free","No visa needed"],["e-visa","e-Visa required for India"],["visa-free","No visa (Indian citizen)"]), hasGuide: false },
  { key: "kashmir", label: "Kashmir", region: "india", description: "Dal Lake, houseboats & alpine meadows", bestMonths: "Apr – Oct", budget: "$25–100/day",
    visa: v(["visa-free","No visa needed"],["e-visa","e-Visa required for India"],["visa-free","No visa (Indian citizen)"]), hasGuide: true },
  { key: "tamil-nadu", label: "Tamil Nadu", region: "india", description: "Temples, Chettinad cuisine & hill stations", bestMonths: "Nov – Feb", budget: "$20–80/day",
    visa: v(["visa-free","No visa needed"],["e-visa","e-Visa required for India"],["visa-free","No visa (Indian citizen)"]), hasGuide: false },
  { key: "karnataka", label: "Karnataka", region: "india", description: "Bangalore, Mysore & Hampi ruins", bestMonths: "Oct – Feb", budget: "$20–90/day",
    visa: v(["visa-free","No visa needed"],["e-visa","e-Visa required for India"],["visa-free","No visa (Indian citizen)"]), hasGuide: false },
  { key: "northeast-india", label: "Northeast India", region: "india", description: "Untouched beauty, living root bridges", bestMonths: "Oct – Apr", budget: "$20–70/day",
    visa: v(["visa-free","No visa; ILP needed for some states"],["e-visa","e-Visa required for India"],["visa-free","No visa; ILP for some states"]), hasGuide: false },

  // ── Southeast Asia ─────────────────────────────────────────────────
  { key: "bali", label: "Bali", region: "southeast-asia", description: "Temples, rice terraces & surf", bestMonths: "Apr – Oct", budget: "$30–150/day",
    visa: v(["visa-free","30-day visa-free on arrival"],["visa-free","30-day visa-free"],["visa-free","30-day visa-free"]), hasGuide: true },
  { key: "thailand", label: "Thailand", region: "southeast-asia", description: "Street food, islands & temples", bestMonths: "Nov – Mar", budget: "$25–120/day",
    visa: v(["visa-free","60-day visa-free (recently changed to 30 days for some)"],["visa-free","30-day visa-free"],["visa-free","30-day visa-free"]), hasGuide: true },
  { key: "vietnam", label: "Vietnam", region: "southeast-asia", description: "Ha Long Bay, phở & motorbike roads", bestMonths: "Mar – May, Sep – Nov", budget: "$20–80/day",
    visa: v(["e-visa","e-Visa available (30 days)"],["visa-free","45-day visa-free"],["e-visa","e-Visa available (30 days)"]), hasGuide: true },
  { key: "sri-lanka", label: "Sri Lanka", region: "southeast-asia", description: "Tea country, wildlife & ancient ruins", bestMonths: "Dec – Mar", budget: "$30–100/day",
    visa: v(["e-visa","ETA online required"],["e-visa","ETA online required"],["e-visa","ETA online required"]), hasGuide: true },
  { key: "maldives", label: "Maldives", region: "southeast-asia", description: "Overwater villas & crystal waters", bestMonths: "Nov – Apr", budget: "$80–500/day",
    visa: v(["voa","Free 30-day VOA for all"],["voa","Free 30-day VOA"],["voa","Free 30-day VOA"]), hasGuide: true },
  { key: "singapore", label: "Singapore", region: "southeast-asia", description: "Gardens, hawker food & futurism", bestMonths: "Year-round", budget: "$60–200/day",
    visa: v(["visa-required","Visa required (96h transit w/ US visa)"],["visa-free","90-day visa-free"],["visa-required","Visa required; GC doesn't help"]), hasGuide: true },

  // ── Mexico & Caribbean ─────────────────────────────────────────────
  { key: "cancun", label: "Cancún", region: "mexico-caribbean", description: "Turquoise water & Mayan ruins", bestMonths: "Dec – Apr", budget: "$50–200/day",
    visa: v(["visa-free","Visa-free with valid US visa (180 days)"],["visa-free","180-day visa-free"],["visa-free","Visa-free with valid US GC"]), hasGuide: true },
  { key: "cabo", label: "Cabo San Lucas", region: "mexico-caribbean", description: "Desert meets ocean, luxury resorts", bestMonths: "Oct – May", budget: "$60–250/day",
    visa: v(["visa-free","Visa-free with valid US visa (180 days)"],["visa-free","180-day visa-free"],["visa-free","Visa-free with valid US GC"]), hasGuide: false },
  { key: "riviera-maya", label: "Riviera Maya", region: "mexico-caribbean", description: "Cenotes, Tulum & boutique beaches", bestMonths: "Dec – Apr", budget: "$50–200/day",
    visa: v(["visa-free","Visa-free with valid US visa (180 days)"],["visa-free","180-day visa-free"],["visa-free","Visa-free with valid US GC"]), hasGuide: false },
  { key: "puerto-vallarta", label: "Puerto Vallarta", region: "mexico-caribbean", description: "Pacific coast charm & art scene", bestMonths: "Nov – May", budget: "$40–150/day",
    visa: v(["visa-free","Visa-free with valid US visa (180 days)"],["visa-free","180-day visa-free"],["visa-free","Visa-free with valid US GC"]), hasGuide: false },
  { key: "jamaica", label: "Jamaica", region: "mexico-caribbean", description: "Reggae, jerk chicken & Blue Mountains", bestMonths: "Nov – Apr", budget: "$50–200/day",
    visa: v(["visa-required","Visa required (US visa doesn't help for Indians)"],["visa-free","30-day visa-free"],["visa-free","Visa-free with valid US visa"]), hasGuide: false },
  { key: "dominican-republic", label: "Dominican Republic", region: "mexico-caribbean", description: "All-inclusive resorts & merengue", bestMonths: "Dec – Apr", budget: "$40–180/day",
    visa: v(["voa","Tourist card on arrival ($10)"],["visa-free","30-day visa-free"],["voa","Tourist card on arrival ($10)"]), hasGuide: false },
  { key: "bahamas", label: "Bahamas", region: "mexico-caribbean", description: "Pink sand beaches & island hopping", bestMonths: "Dec – May", budget: "$60–300/day",
    visa: v(["visa-free","Visa-free with valid US visa"],["visa-free","90-day visa-free"],["visa-free","Visa-free with valid US GC"]), hasGuide: false },
  { key: "aruba", label: "Aruba", region: "mexico-caribbean", description: "One happy island — arid beaches & nightlife", bestMonths: "Year-round", budget: "$60–250/day",
    visa: v(["visa-free","Visa-free with valid US visa (180 days)"],["visa-free","30-day visa-free"],["visa-free","Visa-free with valid US visa"]), hasGuide: false },

  // ── Europe ─────────────────────────────────────────────────────────
  { key: "london", label: "London & UK", region: "europe", description: "History, theatre & afternoon tea", bestMonths: "May – Sep", budget: "$80–250/day",
    visa: v(["visa-required","UK visa required (US visa doesn't help)"],["visa-free","6-month visa-free"],["visa-required","UK visa required; GC doesn't help"]), hasGuide: true },
  { key: "switzerland", label: "Switzerland", region: "europe", description: "Alps, chocolate & scenic trains", bestMonths: "Jun – Sep, Dec – Feb", budget: "$100–350/day",
    visa: v(["visa-required","Schengen visa required (US visa doesn't help)"],["visa-free","90-day visa-free (Schengen)"],["visa-required","Schengen visa required; GC doesn't help"]), hasGuide: true },
  { key: "italy", label: "Italy", region: "europe", description: "Art, pasta & Amalfi Coast", bestMonths: "Apr – Jun, Sep – Oct", budget: "$60–200/day",
    visa: v(["visa-required","Schengen visa required (US visa doesn't help)"],["visa-free","90-day visa-free (Schengen)"],["visa-required","Schengen visa required; GC doesn't help"]), hasGuide: true },
  { key: "france", label: "France", region: "europe", description: "Paris, Provence & world-class wine", bestMonths: "Apr – Jun, Sep – Oct", budget: "$70–250/day",
    visa: v(["visa-required","Schengen visa required (US visa doesn't help)"],["visa-free","90-day visa-free (Schengen)"],["visa-required","Schengen visa required; GC doesn't help"]), hasGuide: true },
  { key: "spain", label: "Spain", region: "europe", description: "Tapas, flamenco & Mediterranean sun", bestMonths: "Apr – Jun, Sep – Oct", budget: "$50–180/day",
    visa: v(["visa-required","Schengen visa required (US visa doesn't help)"],["visa-free","90-day visa-free (Schengen)"],["visa-required","Schengen visa required; GC doesn't help"]), hasGuide: false },
  { key: "greece", label: "Greece", region: "europe", description: "Santorini sunsets & ancient ruins", bestMonths: "May – Oct", budget: "$50–180/day",
    visa: v(["visa-required","Schengen visa required (US visa doesn't help)"],["visa-free","90-day visa-free (Schengen)"],["visa-required","Schengen visa required; GC doesn't help"]), hasGuide: true },
  { key: "iceland", label: "Iceland", region: "europe", description: "Northern Lights & volcanic landscapes", bestMonths: "Jun – Aug, Sep – Mar (lights)", budget: "$80–300/day",
    visa: v(["visa-required","Schengen visa required (US visa doesn't help)"],["visa-free","90-day visa-free (Schengen)"],["visa-required","Schengen visa required; GC doesn't help"]), hasGuide: false },
  { key: "portugal", label: "Portugal", region: "europe", description: "Pastel towns, fado & surf breaks", bestMonths: "Apr – Oct", budget: "$40–150/day",
    visa: v(["visa-required","Schengen visa required (US visa doesn't help)"],["visa-free","90-day visa-free (Schengen)"],["visa-required","Schengen visa required; GC doesn't help"]), hasGuide: false },
  { key: "scandinavia", label: "Scandinavia", region: "europe", description: "Fjords, design & midnight sun", bestMonths: "Jun – Aug", budget: "$80–300/day",
    visa: v(["visa-required","Schengen visa required (US visa doesn't help)"],["visa-free","90-day visa-free (Schengen)"],["visa-required","Schengen visa required; GC doesn't help"]), hasGuide: false },

  // ── USA & Canada ───────────────────────────────────────────────────
  { key: "hawaii", label: "Hawaii", region: "usa-canada", description: "Volcanos, surfing & luau feasts", bestMonths: "Apr – Oct", budget: "$80–300/day",
    visa: v(["visa-free","Valid US visa — domestic travel"],["visa-free","Domestic — no visa"],["visa-free","Domestic — no visa"]), hasGuide: true },
  { key: "national-parks", label: "National Parks", region: "usa-canada", description: "Yellowstone, Grand Canyon & Yosemite", bestMonths: "May – Sep", budget: "$50–200/day",
    visa: v(["visa-free","Valid US visa — domestic travel"],["visa-free","Domestic — no visa"],["visa-free","Domestic — no visa"]), hasGuide: false },
  { key: "new-york-city", label: "New York City", region: "usa-canada", description: "Broadway, pizza & skyline views", bestMonths: "Apr – Jun, Sep – Nov", budget: "$80–350/day",
    visa: v(["visa-free","Valid US visa — domestic travel"],["visa-free","Domestic — no visa"],["visa-free","Domestic — no visa"]), hasGuide: false },
  { key: "florida", label: "Florida", region: "usa-canada", description: "Theme parks, beaches & Everglades", bestMonths: "Nov – Apr", budget: "$50–250/day",
    visa: v(["visa-free","Valid US visa — domestic travel"],["visa-free","Domestic — no visa"],["visa-free","Domestic — no visa"]), hasGuide: false },
  { key: "alaska", label: "Alaska", region: "usa-canada", description: "Glaciers, bears & frontier wilderness", bestMonths: "Jun – Aug", budget: "$80–300/day",
    visa: v(["visa-free","Valid US visa — domestic travel"],["visa-free","Domestic — no visa"],["visa-free","Domestic — no visa"]), hasGuide: false },
  { key: "banff", label: "Banff & Canadian Rockies", region: "usa-canada", description: "Turquoise lakes & mountain grandeur", bestMonths: "Jun – Sep, Dec – Mar", budget: "$70–250/day",
    visa: v(["visa-required","Visitor visa required (separate from US visa)"],["visa-free","eTA required (quick online)"],["visa-free","eTA required (quick online)"]), hasGuide: false },

  // ── Middle East & Africa ───────────────────────────────────────────
  { key: "dubai", label: "Dubai", region: "middle-east-africa", description: "Skyscrapers, souks & desert safaris", bestMonths: "Nov – Mar", budget: "$60–300/day",
    visa: v(["e-visa","14-day visa on arrival or e-visa"],["visa-free","30-day visa-free"],["e-visa","14-day visa on arrival; GC doesn't help"]), hasGuide: true },
  { key: "abu-dhabi", label: "Abu Dhabi", region: "middle-east-africa", description: "Grand Mosque, Louvre & F1", bestMonths: "Nov – Mar", budget: "$60–250/day",
    visa: v(["e-visa","14-day visa on arrival or e-visa"],["visa-free","30-day visa-free"],["e-visa","14-day visa on arrival; GC doesn't help"]), hasGuide: false },
  { key: "oman", label: "Oman", region: "middle-east-africa", description: "Wadis, fjords & Bedouin culture", bestMonths: "Oct – Mar", budget: "$40–150/day",
    visa: v(["e-visa","e-Visa available (10-day or 30-day)"],["visa-free","Visa-free on arrival"],["e-visa","e-Visa required; GC doesn't help"]), hasGuide: false },
  { key: "south-africa", label: "South Africa", region: "middle-east-africa", description: "Cape Town, safaris & wine country", bestMonths: "May – Sep", budget: "$40–180/day",
    visa: v(["visa-required","Visa required (US visa doesn't help)"],["visa-free","90-day visa-free"],["visa-required","Visa required; GC doesn't help"]), hasGuide: false },
  { key: "kenya", label: "Kenya Safari", region: "middle-east-africa", description: "Masai Mara, Big Five & Nairobi", bestMonths: "Jul – Oct", budget: "$50–300/day",
    visa: v(["e-visa","eTA available online"],["e-visa","eTA available online"],["e-visa","eTA available online"]), hasGuide: false },
  { key: "egypt", label: "Egypt", region: "middle-east-africa", description: "Pyramids, Nile cruises & Red Sea", bestMonths: "Oct – Apr", budget: "$30–120/day",
    visa: v(["e-visa","e-Visa available online"],["e-visa","e-Visa or visa on arrival ($25)"],["e-visa","e-Visa available online"]), hasGuide: false },
  { key: "morocco", label: "Morocco", region: "middle-east-africa", description: "Medinas, Sahara & Atlas Mountains", bestMonths: "Mar – May, Sep – Nov", budget: "$30–120/day",
    visa: v(["visa-required","Visa required (US visa doesn't help)"],["visa-free","90-day visa-free"],["visa-required","Visa required; GC doesn't help"]), hasGuide: false },

  // ── Oceania ────────────────────────────────────────────────────────
  { key: "new-zealand", label: "New Zealand", region: "oceania", description: "Fjords, Hobbiton & adrenaline capital", bestMonths: "Dec – Feb", budget: "$80–200/day",
    visa: v(["e-visa","NZeTA required"],["e-visa","NZeTA required"],["e-visa","NZeTA required"]), hasGuide: true },
  { key: "australia", label: "Australia", region: "oceania", description: "Great Barrier Reef, outback & opera", bestMonths: "Sep – Nov, Mar – May", budget: "$70–250/day",
    visa: v(["e-visa","e-Visa (subclass 600)"],["e-visa","ETA (subclass 601) — quick online"],["e-visa","e-Visa (subclass 600)"]), hasGuide: true },
  { key: "fiji", label: "Fiji", region: "oceania", description: "Coral reefs, bure stays & island time", bestMonths: "May – Oct", budget: "$50–250/day",
    visa: v(["visa-free","4-month visa-free on arrival"],["visa-free","4-month visa-free"],["visa-free","4-month visa-free"]), hasGuide: false },
];

/* ------------------------------------------------------------------ */
/* Visa Dashboard Data                                                */
/* ------------------------------------------------------------------ */

export const VISA_HOLDER_LABELS: Record<VisaHolderStatus, string> = {
  "indian-passport": "US Visa Holders (H-1B, L-1, B1/B2, F-1)",
  "us-citizen": "US Citizens",
  "green-card": "Green Card Holders",
};

export const VISA_DASHBOARD: VisaDashboardCard[] = [
  {
    key: "visa-free",
    emoji: "🟢",
    label: "Visa-Free",
    color: "bg-green-500/10",
    textColor: "text-green-600",
    count: 25,
    topDestinations: ["Thailand", "Indonesia", "Nepal", "Bhutan", "Fiji", "Mauritius", "Serbia", "Maldives"],
    description: "Countries you can visit without any visa — even without US status",
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
    label: "US Visa Perks",
    color: "bg-purple-500/10",
    textColor: "text-purple-600",
    count: 40,
    topDestinations: ["Mexico", "Turkey", "Philippines", "Costa Rica", "Panama", "Colombia", "Georgia", "Albania"],
    description: "Countries that grant entry specifically because of your valid US visa — no separate visa needed",
  },
];

export const VISA_DASHBOARD_US_CITIZEN: VisaDashboardCard[] = [
  {
    key: "visa-free",
    emoji: "🟢",
    label: "Visa-Free",
    color: "bg-green-500/10",
    textColor: "text-green-600",
    count: 185,
    topDestinations: ["EU / Schengen", "UK", "Japan", "Australia", "Canada", "Mexico", "South Korea", "Singapore"],
    description: "Most of the world is open visa-free for US passport holders",
  },
  {
    key: "voa",
    emoji: "🟡",
    label: "Visa on Arrival",
    color: "bg-yellow-500/10",
    textColor: "text-yellow-600",
    count: 35,
    topDestinations: ["Ethiopia", "Madagascar", "Comoros", "Tuvalu", "Mozambique", "Timor-Leste", "Togo", "Palau"],
    description: "Visa issued at the port of entry — mostly African & Pacific nations",
  },
  {
    key: "e-visa",
    emoji: "🔵",
    label: "e-Visa / ETA Required",
    color: "bg-blue-500/10",
    textColor: "text-blue-600",
    count: 25,
    topDestinations: ["Australia ETA", "Canada eTA", "India e-Visa", "Kenya eTA", "New Zealand NZeTA", "Sri Lanka", "Oman", "Turkey"],
    description: "Quick online authorization needed before travel",
  },
  {
    key: "visa-required",
    emoji: "🔴",
    label: "Visa Required",
    color: "bg-red-500/10",
    textColor: "text-red-600",
    count: 30,
    topDestinations: ["China", "Russia", "Brazil", "Saudi Arabia", "North Korea", "Iran", "Afghanistan", "Libya"],
    description: "Full visa application required — plan well in advance",
  },
];

export const VISA_DASHBOARD_GREEN_CARD: VisaDashboardCard[] = [
  {
    key: "visa-free-gc",
    emoji: "🟢",
    label: "Visa-Free (with GC)",
    color: "bg-green-500/10",
    textColor: "text-green-600",
    count: 40,
    topDestinations: ["Mexico", "Canada", "Costa Rica", "Panama", "Philippines", "Turkey", "Georgia", "Albania"],
    description: "Countries that waive visa for Indian passport holders with a valid US Green Card",
  },
  {
    key: "voa-gc",
    emoji: "🟡",
    label: "VOA (with GC)",
    color: "bg-yellow-500/10",
    textColor: "text-yellow-600",
    count: 15,
    topDestinations: ["Bermuda", "Aruba", "Curaçao", "Bonaire", "Montserrat", "Turks & Caicos", "BVI", "Dominica"],
    description: "Visa on arrival available for GC holders — mostly Caribbean islands",
  },
  {
    key: "e-visa-gc",
    emoji: "🔵",
    label: "e-Visa Available",
    color: "bg-blue-500/10",
    textColor: "text-blue-600",
    count: 50,
    topDestinations: ["Turkey", "Sri Lanka", "Australia", "Kenya", "UAE", "Vietnam", "New Zealand", "Egypt"],
    description: "Apply online — GC status may simplify the process",
  },
  {
    key: "visa-required-gc",
    emoji: "🔴",
    label: "Still Need Visa",
    color: "bg-red-500/10",
    textColor: "text-red-600",
    count: 25,
    topDestinations: ["Schengen / EU", "UK", "Japan", "Australia", "China", "Russia", "South Korea", "Brazil"],
    description: "US Green Card does not help — full visa application required",
  },
];

export const VISA_DASHBOARD_BY_STATUS: Record<VisaHolderStatus, VisaDashboardCard[]> = {
  "indian-passport": VISA_DASHBOARD,
  "us-citizen": VISA_DASHBOARD_US_CITIZEN,
  "green-card": VISA_DASHBOARD_GREEN_CARD,
};

/* ------------------------------------------------------------------ */
/* Visa badge helpers                                                 */
/* ------------------------------------------------------------------ */

export function visaBadgeColor(status: VisaStatus): string {
  switch (status) {
    case "visa-free": return "bg-green-500/15 text-green-700";
    case "voa": return "bg-yellow-500/15 text-yellow-700";
    case "e-visa": return "bg-blue-500/15 text-blue-700";
    case "visa-required": return "bg-red-500/12 text-red-600";
  }
}

export function visaBadgeLabel(status: VisaStatus): string {
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
