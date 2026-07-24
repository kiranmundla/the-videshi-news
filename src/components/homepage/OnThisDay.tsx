import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";

interface OTDEntry {
  id: string;
  month: number;
  day: number;
  year: number;
  title: string;
  description: string;
  present_connection?: string | null;
  image_url?: string | null;
}

export default function OnThisDay() {
  const [entry, setEntry] = useState<OTDEntry | null>(null);

  useEffect(() => {
    (async () => {
      const now = new Date();
      const month = now.getMonth() + 1;
      const day = now.getDate();

      const { data } = await (supabase as any)
        .from("on_this_day")
        .select("id, month, day, year, title, description, present_connection, image_url")
        .eq("month", month)
        .eq("day", day)
        .limit(5);

      if (data && data.length > 0) {
        // Pick one deterministically by day-of-year so it's consistent for all users
        const idx = (month * 31 + day) % data.length;
        setEntry(data[idx]);
      }
    })();
  }, []);

  if (!entry) return null;

  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const dateLabel = `${monthNames[entry.month - 1]} ${entry.day}, ${entry.year}`;

  return (
    <section className="mb-14">
      <div className="container">
        <div className="flex items-center justify-between mb-4 pb-2 border-b-2" style={{ borderColor: "#0B1D3A" }}>
          <h2 className="text-[13px] font-bold tracking-[2px] uppercase" style={{ color: "#0B1D3A" }}>
            On This Day
          </h2>
          <span className="text-[11px] font-semibold text-muted-foreground tracking-wide">{dateLabel}</span>
        </div>

        <div className="flex gap-5 items-start">
          {entry.image_url && (
            <div className="hidden md:block w-[140px] min-w-[140px] h-[100px] rounded-lg overflow-hidden bg-neutral-100">
              <img
                src={entry.image_url}
                alt={entry.title}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <h3 className="font-serif text-lg font-bold leading-snug mb-1.5">{entry.title}</h3>
            <p className="text-sm text-foreground/80 leading-relaxed mb-1.5">{entry.description}</p>
            {entry.present_connection && (
              <p className="text-xs text-muted-foreground italic">{entry.present_connection}</p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
