import { supabase as supabaseTyped } from "@/integrations/supabase/client";

const supabase = supabaseTyped as unknown as {
  from: (table: string) => any;
};

/* ------------------------------------------------------------------ */
/* Types                                                              */
/* ------------------------------------------------------------------ */

export type VisaBulletinRow = {
  id: string;
  bulletin_month: number;
  bulletin_year: number;
  preference_type: string;
  category: string;
  chart_type: string;
  country: string;
  priority_date: string | null;
  status: string;
  created_at: string;
};

export type ConsulateWaitRow = {
  id: string;
  consulate: string;
  consulate_display: string;
  visa_type: string;
  visa_type_display: string;
  avg_wait_months: number | null;
  next_available_months: number | null;
  scraped_at: string;
  source_updated: string | null;
  created_at: string;
};

export type ProcessingTimeRow = {
  id: string;
  form_number: string;
  form_name: string;
  form_category: string | null;
  office: string;
  office_code: string;
  processing_time_months: number | null;
  estimated_range_low: number | null;
  estimated_range_high: number | null;
  scraped_at: string;
  created_at: string;
};

export type H1BDataRow = {
  id: string;
  fiscal_year: number;
  metric: string;
  value: string;
  source_url: string | null;
  updated_at: string;
};

export type ImmigrationGuide = {
  id: string;
  slug: string;
  title: string;
  subtitle: string | null;
  category: string;
  content: string;
  meta_description: string | null;
  featured_image: string | null;
  reading_time_min: number | null;
  last_updated: string;
  published: boolean;
  sort_order: number;
  created_at: string;
};

/* ------------------------------------------------------------------ */
/* INDIA consulate keys                                               */
/* ------------------------------------------------------------------ */

export const INDIA_CONSULATES = [
  "mumbai",
  "new_delhi",
  "chennai",
  "hyderabad",
  "kolkata",
] as const;

export const CONSULATE_DISPLAY: Record<string, string> = {
  mumbai: "Mumbai",
  new_delhi: "New Delhi",
  chennai: "Chennai",
  hyderabad: "Hyderabad",
  kolkata: "Kolkata",
};

/* ------------------------------------------------------------------ */
/* EB category metadata                                               */
/* ------------------------------------------------------------------ */

export const EB_CATEGORIES = [
  { key: "EB-1", label: "EB-1", desc: "Priority Workers (Extraordinary ability, outstanding professors, multinational managers)" },
  { key: "EB-2", label: "EB-2", desc: "Advanced Degree / Exceptional Ability (most H-1B holders)" },
  { key: "EB-3", label: "EB-3", desc: "Skilled Workers & Professionals (bachelor's degree)" },
  { key: "EB-5-Unreserved", label: "EB-5", desc: "Investor Visa ($800K–$1.05M investment)" },
] as const;

export const FAMILY_CATEGORIES = [
  { key: "F1", label: "F1", desc: "Unmarried Sons & Daughters of US Citizens" },
  { key: "F2A", label: "F2A", desc: "Spouses & Children of Permanent Residents" },
  { key: "F2B", label: "F2B", desc: "Unmarried Sons & Daughters (21+) of Permanent Residents" },
  { key: "F3", label: "F3", desc: "Married Sons & Daughters of US Citizens" },
  { key: "F4", label: "F4", desc: "Brothers & Sisters of Adult US Citizens" },
] as const;

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

const MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function formatPriorityDate(dateStr: string | null, status: string): string {
  if (status === "current") return "Current";
  if (status === "unavailable") return "Unavailable";
  if (!dateStr) return "N/A";
  const d = new Date(dateStr + "T00:00:00");
  return `${MONTH_NAMES[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
}

export function formatWaitMonths(m: number | null): string {
  if (m === null || m === undefined) return "N/A";
  if (m < 0.5) return "< 2 weeks";
  if (m === 0.5) return "2 weeks";
  return `${m} mo`;
}

export function waitColor(m: number | null): string {
  if (m === null) return "text-foreground/40";
  if (m < 2) return "text-green-500";
  if (m < 5) return "text-yellow-500";
  if (m < 8) return "text-orange-500";
  return "text-red-500";
}

export function waitBg(m: number | null): string {
  if (m === null) return "bg-foreground/5";
  if (m < 2) return "bg-green-500/10";
  if (m < 5) return "bg-yellow-500/10";
  if (m < 8) return "bg-orange-500/10";
  return "bg-red-500/10";
}

/** Compute movement in days between two priority dates. Positive = forward, Negative = retrogression */
export function computeMovement(current: string | null, previous: string | null, curStatus: string, prevStatus: string): { days: number; label: string; color: string; arrow: string } | null {
  if (curStatus === "current") return { days: 0, label: "Current", color: "text-green-500", arrow: "✓" };
  if (curStatus === "unavailable") return { days: 0, label: "Unavailable", color: "text-red-500", arrow: "✗" };
  if (!current || !previous) return null;
  const d1 = new Date(current + "T00:00:00").getTime();
  const d2 = new Date(previous + "T00:00:00").getTime();
  const diffDays = Math.round((d1 - d2) / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return { days: 0, label: "No change", color: "text-foreground/50", arrow: "—" };
  const months = Math.abs(Math.round(diffDays / 30));
  const label = months > 0 ? `${months} month${months > 1 ? "s" : ""}` : `${Math.abs(diffDays)} days`;
  if (diffDays > 0) return { days: diffDays, label: `+${label}`, color: "text-green-500", arrow: "▲" };
  return { days: diffDays, label: `-${label}`, color: "text-red-500", arrow: "▼" };
}

/* ------------------------------------------------------------------ */
/* Data fetching                                                      */
/* ------------------------------------------------------------------ */

/** Fetch latest 2 months of visa bulletin data for a given country + chart type */
export async function getVisaBulletin(
  country: string = "india",
  chartType: string = "final_action",
  prefType: string = "employment",
): Promise<VisaBulletinRow[]> {
  const { data, error } = await supabase
    .from("visa_bulletin")
    .select("*")
    .eq("country", country)
    .eq("chart_type", chartType)
    .eq("preference_type", prefType)
    .order("bulletin_year", { ascending: false })
    .order("bulletin_month", { ascending: false })
    .limit(100);
  if (error) {
    console.error("visa_bulletin fetch error:", error);
    return [];
  }
  return data || [];
}

/** Fetch all visa bulletin history for a specific category + country (for charts) */
export async function getVisaBulletinHistory(
  category: string,
  country: string = "india",
  chartType: string = "final_action",
  limit: number = 12,
): Promise<VisaBulletinRow[]> {
  const { data, error } = await supabase
    .from("visa_bulletin")
    .select("*")
    .eq("category", category)
    .eq("country", country)
    .eq("chart_type", chartType)
    .order("bulletin_year", { ascending: false })
    .order("bulletin_month", { ascending: false })
    .limit(limit);
  if (error) {
    console.error("visa_bulletin history error:", error);
    return [];
  }
  return data || [];
}

/** Fetch consulate wait times for India consulates */
export async function getConsulateWaitTimes(consulates?: string[]): Promise<ConsulateWaitRow[]> {
  let query = supabase
    .from("consulate_wait_times")
    .select("*")
    .order("scraped_at", { ascending: false });
  if (consulates) {
    query = query.in("consulate", consulates);
  }
  const { data, error } = await query.limit(200);
  if (error) {
    console.error("consulate_wait_times error:", error);
    return [];
  }
  return data || [];
}

/** Fetch USCIS processing times */
export async function getProcessingTimes(formNumber?: string): Promise<ProcessingTimeRow[]> {
  let query = supabase
    .from("uscis_processing_times")
    .select("*")
    .order("form_number")
    .order("office");
  if (formNumber) {
    query = query.eq("form_number", formNumber);
  }
  const { data, error } = await query.limit(200);
  if (error) {
    console.error("uscis_processing_times error:", error);
    return [];
  }
  return data || [];
}

/** Fetch H-1B data */
export async function getH1BData(): Promise<H1BDataRow[]> {
  const { data, error } = await supabase
    .from("h1b_data")
    .select("*")
    .order("fiscal_year", { ascending: false })
    .order("metric");
  if (error) {
    console.error("h1b_data error:", error);
    return [];
  }
  return data || [];
}

/** Fetch immigration guides */
export async function getImmigrationGuides(): Promise<ImmigrationGuide[]> {
  const { data, error } = await supabase
    .from("immigration_guides")
    .select("*")
    .eq("published", true)
    .order("sort_order")
    .order("title");
  if (error) {
    console.error("immigration_guides error:", error);
    return [];
  }
  return data || [];
}

/** Fetch single guide by slug */
export async function getGuideBySlug(slug: string): Promise<ImmigrationGuide | null> {
  const { data, error } = await supabase
    .from("immigration_guides")
    .select("*")
    .eq("slug", slug)
    .single();
  if (error) {
    console.error("immigration_guide fetch error:", error);
    return null;
  }
  return data;
}

/** Fetch immigration-related articles */
export async function getImmigrationNews(limit: number = 6): Promise<any[]> {
  const { data, error } = await supabase
    .from("p2_articles")
    .select("id,slug,headline,subheadline,image_url,category,published_at")
    .or("category.eq.immigration,category.eq.Immigration,category.ilike.%immigration%")
    .eq("status", "published")
    .order("published_at", { ascending: false })
    .limit(limit);
  if (error) {
    console.error("immigration news error:", error);
    return [];
  }
  // Map to expected shape with title/excerpt
  return (data || []).map((a: any) => ({
    ...a,
    title: a.headline || a.title,
    excerpt: a.subheadline || a.excerpt || "",
  }));
}

/* ------------------------------------------------------------------ */
/* Guide categories and placeholders                                  */
/* ------------------------------------------------------------------ */

export const GUIDE_CATEGORIES = [
  { key: "work-visas", label: "Work Visas", emoji: "💼" },
  { key: "green-card", label: "Green Card", emoji: "🟢" },
  { key: "citizenship", label: "Citizenship", emoji: "🇺🇸" },
  { key: "family", label: "Family", emoji: "👨‍👩‍👧‍👦" },
  { key: "indian-services", label: "Indian Services", emoji: "🇮🇳" },
  { key: "practical", label: "Practical & Financial", emoji: "💰" },
  { key: "forms", label: "Form Guides", emoji: "📝" },
] as const;

export const GUIDE_PLACEHOLDERS = [
  { slug: "h1b-visa-complete-guide", title: "H-1B Visa: Complete Guide", category: "work-visas", emoji: "💼" },
  { slug: "h4-ead-work-authorization", title: "H-4 EAD: Work Authorization for Spouses", category: "work-visas", emoji: "👩‍💼" },
  { slug: "l1-visa-intracompany-transfers", title: "L-1 Visa: Intracompany Transfers", category: "work-visas", emoji: "🏢" },
  { slug: "f1-to-h1b-transition", title: "F-1 to H-1B: Student to Worker", category: "work-visas", emoji: "🎓" },
  { slug: "o1-visa-extraordinary-ability", title: "O-1 Visa: Extraordinary Ability", category: "work-visas", emoji: "⭐" },
  { slug: "eb5-investor-visa", title: "EB-5 Investor Visa", category: "work-visas", emoji: "💵" },
  { slug: "green-card-employment-based", title: "Green Card: Employment-Based", category: "green-card", emoji: "🟢" },
  { slug: "eb2-vs-eb3-downgrade", title: "EB-2 vs EB-3: Should You Downgrade?", category: "green-card", emoji: "⚖️" },
  { slug: "perm-labor-certification", title: "PERM Labor Certification", category: "green-card", emoji: "📋" },
  { slug: "green-card-backlog-survival", title: "Surviving the 10-Year Wait", category: "green-card", emoji: "⏳" },
  { slug: "national-interest-waiver", title: "EB-2 NIW: Self-Petition", category: "green-card", emoji: "🏆" },
  { slug: "naturalization-guide", title: "Becoming a US Citizen", category: "citizenship", emoji: "🗳️" },
  { slug: "oci-card-guide", title: "OCI Card: Everything You Need to Know", category: "citizenship", emoji: "🇮🇳" },
  { slug: "parent-visitor-visa", title: "Getting Parents to America: B1/B2 Guide", category: "family", emoji: "✈️" },
  { slug: "family-green-card", title: "Sponsoring Family for Green Card", category: "family", emoji: "❤️" },
  { slug: "indian-passport-renewal", title: "Indian Passport Renewal in the US", category: "indian-services", emoji: "📕" },
  { slug: "surrender-certificate", title: "Indian Passport Surrender Certificate", category: "indian-services", emoji: "📄" },
  { slug: "power-of-attorney-india", title: "Power of Attorney for India Property", category: "indian-services", emoji: "🏠" },
  { slug: "tax-implications-nri", title: "NRI Tax Guide: US & India", category: "practical", emoji: "🧾" },
  { slug: "money-transfer-india", title: "Sending Money to India: Best Methods", category: "practical", emoji: "💸" },
  { slug: "social-security-india", title: "Social Security for Indian Americans", category: "practical", emoji: "🏛️" },
  { slug: "health-insurance-immigration", title: "Health Insurance During Immigration Limbo", category: "practical", emoji: "🏥" },
  { slug: "how-to-fill-i140", title: "How to Fill Form I-140: Step-by-Step", category: "forms", emoji: "📝" },
  { slug: "how-to-fill-i485", title: "How to Fill Form I-485: Step-by-Step", category: "forms", emoji: "📝" },
  { slug: "how-to-fill-i765", title: "How to Fill Form I-765: EAD Application", category: "forms", emoji: "📝" },
  { slug: "how-to-fill-i131", title: "How to Fill Form I-131: Travel Document", category: "forms", emoji: "📝" },
  { slug: "how-to-fill-n400", title: "How to Fill Form N-400: Citizenship", category: "forms", emoji: "📝" },
  { slug: "how-to-fill-i130", title: "How to Fill Form I-130: Family Petition", category: "forms", emoji: "📝" },
  { slug: "how-to-fill-ds160", title: "How to Fill DS-160: Visa Application", category: "forms", emoji: "📝" },
  { slug: "how-to-fill-i539", title: "How to Fill Form I-539: Change of Status", category: "forms", emoji: "📝" },
];

/* ------------------------------------------------------------------ */
/* Key forms for the processing times overview                        */
/* ------------------------------------------------------------------ */

export const KEY_FORMS = [
  { number: "I-140", name: "Immigrant Petition", desc: "Employer-sponsored green card petition" },
  { number: "I-485", name: "Adjustment of Status", desc: "Apply for green card while in the US" },
  { number: "I-765", name: "Employment Authorization (EAD)", desc: "Work permit while waiting" },
  { number: "I-131", name: "Travel Document", desc: "Advance Parole for international travel" },
  { number: "I-130", name: "Petition for Relative", desc: "Family-based immigration" },
  { number: "N-400", name: "Naturalization", desc: "Application for US citizenship" },
  { number: "I-539", name: "Change/Extend Status", desc: "H-4, B1/B2 extension, etc." },
  { number: "I-129", name: "Nonimmigrant Worker", desc: "H-1B, L-1, O-1 petitions" },
];
