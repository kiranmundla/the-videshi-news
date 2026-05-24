/* ------------------------------------------------------------------ */
/* Travel Visa Guides — Static data module                            */
/* Comprehensive visa guides for NRI travelers                        */
/* ------------------------------------------------------------------ */

export interface TravelVisaGuide {
  destination: string;
  slug: string;
  category: "europe" | "americas" | "asia" | "middle-east" | "oceania";
  overview: string;
  usCitizen: string;
  greenCard: string;
  h1b: string;
  indianPassport: string;
  consulates: string;
  applicationProcess: string;
  processingTimes: string;
  costs: string;
  tips: string;
  lastUpdated: string;
}

export const VISA_GUIDE_CATEGORIES = [
  { key: "europe", label: "Europe", emoji: "🇪🇺" },
  { key: "americas", label: "Americas", emoji: "🌎" },
  { key: "asia", label: "Asia", emoji: "🌏" },
  { key: "middle-east", label: "Middle East", emoji: "🏜️" },
  { key: "oceania", label: "Oceania", emoji: "🌊" },
] as const;

export const TRAVEL_VISA_GUIDES: TravelVisaGuide[] = [
