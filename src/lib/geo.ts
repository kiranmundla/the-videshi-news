/**
 * Shared geolocation / distance utilities.
 *
 * Used by Events, Directory, Classifieds, and Restaurants pages
 * for Near Me + zip-code distance sorting.
 */

/* ------------------------------------------------------------------ */
/* Distance helpers                                                    */
/* ------------------------------------------------------------------ */

/** Haversine distance in miles between two lat/lng points */
export function getDistanceMiles(
  lat1: number, lng1: number,
  lat2: number, lng2: number,
): number {
  const R = 3958.8; // Earth radius in miles
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

/** Format distance for display */
export function formatDistance(miles: number): string {
  if (miles < 1) return "< 1 mi";
  if (miles < 10) return `${miles.toFixed(1)} mi`;
  return `${Math.round(miles)} mi`;
}

/* ------------------------------------------------------------------ */
/* City coords (approximate, for listings without per-item lat/lng)   */
/* ------------------------------------------------------------------ */

export const CITY_COORDS: Record<string, { lat: number; lng: number }> = {
  // California — Bay Area
  "San Francisco": { lat: 37.7749, lng: -122.4194 },
  "San Jose":      { lat: 37.3382, lng: -121.8863 },
  "Oakland":       { lat: 37.8044, lng: -122.2712 },
  "Fremont":       { lat: 37.5485, lng: -121.9886 },
  "Sunnyvale":     { lat: 37.3688, lng: -122.0363 },
  "Santa Clara":   { lat: 37.3541, lng: -121.9552 },
  "Milpitas":      { lat: 37.4323, lng: -121.8996 },
  "Pleasanton":    { lat: 37.6624, lng: -121.8747 },
  "Union City":    { lat: 37.5934, lng: -122.0438 },
  "Dublin":        { lat: 37.7022, lng: -121.9358 },
  "Livermore":     { lat: 37.6819, lng: -121.7680 },
  "Cupertino":     { lat: 37.3230, lng: -122.0322 },
  "Mountain View": { lat: 37.3861, lng: -122.0839 },
  "Palo Alto":     { lat: 37.4419, lng: -122.1430 },
  "Redwood City":  { lat: 37.4852, lng: -122.2364 },
  "Berkeley":      { lat: 37.8716, lng: -122.2727 },
  "Hayward":       { lat: 37.6688, lng: -122.0808 },
  "San Mateo":     { lat: 37.5630, lng: -122.3255 },
  "Daly City":     { lat: 37.6879, lng: -122.4702 },
  "Newark":        { lat: 37.5296, lng: -122.0402 },
  "South San Francisco": { lat: 37.6547, lng: -122.4077 },
  "Los Gatos":     { lat: 37.2358, lng: -121.9624 },
  "San Ramon":     { lat: 37.7799, lng: -121.9780 },
  // California — LA
  "Los Angeles":   { lat: 34.0522, lng: -118.2437 },
  "Culver City":   { lat: 34.0211, lng: -118.3965 },
  "Santa Monica":  { lat: 34.0195, lng: -118.4912 },
  "Anaheim":       { lat: 33.8366, lng: -117.9143 },
  "Irvine":        { lat: 33.6846, lng: -117.8265 },
  "Pasadena":      { lat: 34.1478, lng: -118.1445 },
  "Cerritos":      { lat: 33.8583, lng: -118.0648 },
  "Torrance":      { lat: 33.8358, lng: -118.3406 },
  "Long Beach":    { lat: 33.7701, lng: -118.1937 },
  "Glendale":      { lat: 34.1425, lng: -118.2551 },
  "Calabasas":     { lat: 34.1367, lng: -118.6606 },
  // New York / New Jersey
  "New York":      { lat: 40.7128, lng: -74.0060 },
  "Brooklyn":      { lat: 40.6782, lng: -73.9442 },
  "Queens":        { lat: 40.7282, lng: -73.7949 },
  "Edison":        { lat: 40.5187, lng: -74.4121 },
  "Jersey City":   { lat: 40.7178, lng: -74.0431 },
  "Hoboken":       { lat: 40.7440, lng: -74.0324 },
  "Parsippany":    { lat: 40.8578, lng: -74.4260 },
  "Iselin":        { lat: 40.5751, lng: -74.3224 },
  "Hicksville":    { lat: 40.7682, lng: -73.5249 },
  "Jackson Heights": { lat: 40.7557, lng: -73.8831 },
  "Flushing":      { lat: 40.7654, lng: -73.8174 },
  // Texas — Dallas
  "Dallas":        { lat: 32.7767, lng: -96.7970 },
  "Plano":         { lat: 33.0198, lng: -96.6989 },
  "Irving":        { lat: 32.8141, lng: -96.9489 },
  "Frisco":        { lat: 33.1507, lng: -96.8236 },
  "Richardson":    { lat: 32.9483, lng: -96.7299 },
  "Garland":       { lat: 32.9126, lng: -96.6389 },
  "Arlington":     { lat: 32.7357, lng: -97.1081 },
  "Allen":         { lat: 33.1032, lng: -96.6706 },
  "Carrollton":    { lat: 32.9537, lng: -96.8903 },
  "Euless":        { lat: 32.8370, lng: -97.0820 },
  // Texas — Houston
  "Houston":       { lat: 29.7604, lng: -95.3698 },
  "Sugar Land":    { lat: 29.6197, lng: -95.6349 },
  "Katy":          { lat: 29.7858, lng: -95.8245 },
  "Stafford":      { lat: 29.6163, lng: -95.5577 },
  "Pearland":      { lat: 29.5636, lng: -95.2860 },
  // Illinois
  "Chicago":       { lat: 41.8781, lng: -87.6298 },
  "Schaumburg":    { lat: 42.0334, lng: -88.0834 },
  "Naperville":    { lat: 41.7508, lng: -88.1535 },
  "Aurora":        { lat: 41.7606, lng: -88.3201 },
  "Skokie":        { lat: 42.0324, lng: -87.7416 },
  // Washington
  "Seattle":       { lat: 47.6062, lng: -122.3321 },
  "Bellevue":      { lat: 47.6101, lng: -122.2015 },
  "Redmond":       { lat: 47.6740, lng: -122.1215 },
  "Kirkland":      { lat: 47.6815, lng: -122.2087 },
  // Georgia
  "Atlanta":       { lat: 33.7490, lng: -84.3880 },
  "Alpharetta":    { lat: 34.0754, lng: -84.2941 },
  "Duluth":        { lat: 34.0029, lng: -84.1447 },
  "Norcross":      { lat: 33.9410, lng: -84.2135 },
  "Decatur":       { lat: 33.7748, lng: -84.2963 },
  "Johns Creek":   { lat: 34.0289, lng: -84.1984 },
  // DC
  "Washington":    { lat: 38.9072, lng: -77.0369 },
  "Fairfax":       { lat: 38.8462, lng: -77.3064 },
  "Rockville":     { lat: 39.0840, lng: -77.1528 },
  "Bethesda":      { lat: 38.9847, lng: -77.0947 },
  "Tysons":        { lat: 38.9187, lng: -77.2311 },
  "Herndon":       { lat: 38.9696, lng: -77.3861 },
  "Vienna":        { lat: 38.9012, lng: -77.2653 },
  // Massachusetts
  "Boston":        { lat: 42.3601, lng: -71.0589 },
  "Cambridge":     { lat: 42.3736, lng: -71.1097 },
  // Michigan
  "Detroit":       { lat: 42.3314, lng: -83.0458 },
  "Troy":          { lat: 42.6064, lng: -83.1498 },
  "Novi":          { lat: 42.4801, lng: -83.4755 },
  // North Carolina
  "Charlotte":     { lat: 35.2271, lng: -80.8431 },
  "Raleigh":       { lat: 35.7796, lng: -78.6382 },
  "Durham":        { lat: 35.9940, lng: -78.8986 },
  // Pennsylvania
  "Philadelphia":  { lat: 39.9526, lng: -75.1652 },
  "Pittsburgh":    { lat: 40.4406, lng: -79.9959 },
  // Arizona
  "Phoenix":       { lat: 33.4484, lng: -112.0740 },
  "Scottsdale":    { lat: 33.4942, lng: -111.9261 },
  "Chandler":      { lat: 33.3062, lng: -111.8413 },
  "Tempe":         { lat: 33.4255, lng: -111.9400 },
  "Mesa":          { lat: 33.4152, lng: -111.8315 },
  // Others
  "Nashville":     { lat: 36.1627, lng: -86.7816 },
  "Denver":        { lat: 39.7392, lng: -104.9903 },
  "Columbus":      { lat: 39.9612, lng: -82.9988 },
  "Baltimore":     { lat: 39.2904, lng: -76.6122 },
  // Florida
  "Hollywood":     { lat: 26.0112, lng: -80.1495 },
  "Miami":         { lat: 25.7617, lng: -80.1918 },
  "Tampa":         { lat: 27.9506, lng: -82.4572 },
  "Orlando":       { lat: 28.5383, lng: -81.3792 },
  "Jacksonville":  { lat: 30.3322, lng: -81.6557 },
  "Fort Lauderdale": { lat: 26.1224, lng: -80.1373 },
};

/** Look up approximate coordinates for a city. Returns null if unknown. */
export function getCityCoords(city: string | null): { lat: number; lng: number } | null {
  if (!city) return null;
  return CITY_COORDS[city] || null;
}

/* ------------------------------------------------------------------ */
/* Zip code lookup (lazy-loaded)                                       */
/* ------------------------------------------------------------------ */

export type ZipInfo = {
  lat: number;
  lng: number;
  city: string;
  state: string;
};

let zipCache: Record<string, ZipInfo> | null = null;
let zipPromise: Promise<Record<string, ZipInfo>> | null = null;

/** Lazy-load the zip code database (~2.8 MB, only loaded on first use) */
export async function loadZipCodes(): Promise<Record<string, ZipInfo>> {
  if (zipCache) return zipCache;
  if (zipPromise) return zipPromise;
  zipPromise = fetch("/data/zipcodes.json")
    .then((r) => r.json())
    .then((data: Record<string, ZipInfo>) => {
      zipCache = data;
      return data;
    });
  return zipPromise;
}

/** Look up a single zip code. Returns null if not found. */
export async function lookupZip(zip: string): Promise<ZipInfo | null> {
  const db = await loadZipCodes();
  return db[zip] || null;
}
