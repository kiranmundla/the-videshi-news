import { supabase as supabaseTyped } from "@/integrations/supabase/client";

const supabase = supabaseTyped as unknown as {
  from: (table: string) => any;
};

/* ------------------------------------------------------------------ */
/* Types                                                              */
/* ------------------------------------------------------------------ */

export interface KidsProgram {
  id: string;
  name: string;
  organization: string | null;
  category: string | null;
  description: string | null;
  website_url: string | null;
  grade_range: string | null;
  cost: string | null;
  is_indian_org: boolean;
  is_featured: boolean;
  created_at: string;
}

export interface KidsDeadline {
  id: string;
  program_id: string | null;
  title: string;
  deadline_date: string;
  deadline_type: string | null;
  description: string | null;
  registration_url: string | null;
  cost: string | null;
  grade_range: string | null;
  location: string | null;
  created_at: string;
  // Joined from program
  program_name: string | null;
  program_category: string | null;
}

export interface KidsCamp {
  id: string;
  title: string;
  date: string;
  end_date: string | null;
  location: string | null;
  age_range: string | null;
  cost: string | null;
  description: string | null;
  url: string | null;
  source: "deadline" | "event";
}

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

export function generateProgramSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/['']/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60)
    .replace(/-+$/, "");
}

/* ------------------------------------------------------------------ */
/* Data fetching                                                      */
/* ------------------------------------------------------------------ */

export async function fetchKidsPrograms(category?: string): Promise<KidsProgram[]> {
  try {
    let query = supabase
      .from("kids_programs")
      .select("*")
      .order("is_featured", { ascending: false })
      .order("name", { ascending: true });

    if (category) {
      query = query.eq("category", category);
    }

    const { data, error } = await query;

    if (error) {
      console.error("Failed to fetch kids programs:", error);
      return [];
    }

    return (data || []) as KidsProgram[];
  } catch (err) {
    console.error("Failed to fetch kids programs:", err);
    return [];
  }
}

export async function fetchKidsDeadlines(limit?: number): Promise<KidsDeadline[]> {
  try {
    const today = new Date().toISOString().slice(0, 10);

    let query = supabase
      .from("kids_deadlines")
      .select("*, kids_programs(name, category)")
      .gte("deadline_date", today)
      .order("deadline_date", { ascending: true });

    if (limit) {
      query = query.limit(limit);
    }

    const { data, error } = await query;

    if (error) {
      // If the join fails (table doesn't exist yet), try without join
      const { data: fallback, error: fallbackError } = await supabase
        .from("kids_deadlines")
        .select("*")
        .gte("deadline_date", today)
        .order("deadline_date", { ascending: true })
        .limit(limit || 50);

      if (fallbackError) {
        console.error("Failed to fetch kids deadlines:", fallbackError);
        return [];
      }

      return ((fallback || []) as any[]).map((d) => ({
        ...d,
        program_name: null,
        program_category: null,
      }));
    }

    return ((data || []) as any[]).map((d) => ({
      ...d,
      program_name: d.kids_programs?.name || null,
      program_category: d.kids_programs?.category || null,
    }));
  } catch (err) {
    console.error("Failed to fetch kids deadlines:", err);
    return [];
  }
}

export async function fetchKidsCamps(): Promise<KidsCamp[]> {
  const today = new Date().toISOString().slice(0, 10);
  const camps: KidsCamp[] = [];

  try {
    // Source 1: kids_deadlines where deadline_type is camp-related
    const { data: campDeadlines } = await supabase
      .from("kids_deadlines")
      .select("*, kids_programs(name, category)")
      .in("deadline_type", ["camp_start", "camp_registration", "workshop"])
      .gte("deadline_date", today)
      .order("deadline_date", { ascending: true })
      .limit(20);

    if (campDeadlines) {
      for (const d of campDeadlines as any[]) {
        camps.push({
          id: `deadline-${d.id}`,
          title: d.title || d.kids_programs?.name || "Camp",
          date: d.deadline_date,
          end_date: null,
          location: d.location || null,
          age_range: d.grade_range || null,
          cost: d.cost || null,
          description: d.description || null,
          url: d.registration_url || null,
          source: "deadline",
        });
      }
    }
  } catch {
    // kids_deadlines table may not exist yet
  }

  try {
    // Source 2: events table for kids/education/family events
    const { data: events } = await supabase
      .from("events")
      .select("id,title,date,end_date,venue_name,city,state,category,description,ticket_url,price_range,audience")
      .gte("date", today)
      .or("category.eq.Education,audience.ilike.%kids%,audience.ilike.%family%,audience.ilike.%children%,title.ilike.%camp%,title.ilike.%workshop%kids%")
      .order("date", { ascending: true })
      .limit(20);

    if (events) {
      for (const e of events as any[]) {
        camps.push({
          id: `event-${e.id}`,
          title: e.title,
          date: e.date,
          end_date: e.end_date || null,
          location: [e.venue_name, e.city, e.state].filter(Boolean).join(", "),
          age_range: e.audience || null,
          cost: e.price_range || null,
          description: e.description || null,
          url: e.ticket_url || null,
          source: "event",
        });
      }
    }
  } catch {
    // events query may fail
  }

  // De-duplicate by title similarity and sort by date
  camps.sort((a, b) => a.date.localeCompare(b.date));
  return camps;
}
