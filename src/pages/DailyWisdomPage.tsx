import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import { supabase } from "@/integrations/supabase/client";
import "./DailyWisdomPage.css";
import "./TeacherProfilePage.css";

interface WisdomEntry {
  id: string;
  teacher_name: string;
  tradition: string;
  quote: string;
  source_title: string | null;
  source_url: string | null;
  source_type: string | null;
  thumbnail_url: string | null;
  teacher_image_url: string | null;
  video_id: string | null;
  featured_date: string | null;
  created_at: string;
  teacher_slug: string | null;
}

interface Teacher {
  slug: string;
  name: string;
  tradition: string;
  image_url: string | null;
  is_org: boolean;
}

interface SpiritualEvent {
  id: string;
  title: string;
  date: string;
  time: string | null;
  venue_name: string | null;
  city: string | null;
  state: string | null;
  image_url: string | null;
  ticket_url: string | null;
  slug: string | null;
}

const TRADITION_ICONS: Record<string, string> = {
  "Hindu / Yoga": "🙏",
  "Buddhist": "☸️",
  "Interfaith / Modern": "✨",
  "Islamic": "☪️",
  "Sikh": "🙏",
  "Jain": "🙏",
};

const TRADITION_COLORS: Record<string, string> = {
  "Hindu / Yoga": "#D4A843",
  "Buddhist": "#C0392B",
  "Interfaith / Modern": "#2980B9",
  "Islamic": "#27AE60",
  "Sikh": "#E67E22",
  "Jain": "#8E44AD",
};

const TEACHER_IMAGES: Record<string, string> = {
  "Sadhguru": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Sadhguru-Jaggi-Vasudev.jpg/330px-Sadhguru-Jaggi-Vasudev.jpg",
  "Sri Sri Ravi Shankar": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Sri_Sri_Ravi_Shankar_-_new.jpg/330px-Sri_Sri_Ravi_Shankar_-_new.jpg",
  "Mooji": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Mooji_Wikipedia_Photo.jpg/330px-Mooji_Wikipedia_Photo.jpg",
  "Dalai Lama": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/The_Dalai_Lama_in_2012.jpg/330px-The_Dalai_Lama_in_2012.jpg",
  "Thich Nhat Hanh": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Thich_Nhat_Hanh_12_%28cropped%29.jpg/330px-Thich_Nhat_Hanh_12_%28cropped%29.jpg",
  "Deepak Chopra": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Deepak_Chopra_by_Gage_Skidmore.jpg/330px-Deepak_Chopra_by_Gage_Skidmore.jpg",
  "Jay Shetty": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Jay_Shetty_Headshot_2021.jpg/330px-Jay_Shetty_Headshot_2021.jpg",
  "Eckhart Tolle": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Eckhart_Tolle_front.jpg/330px-Eckhart_Tolle_front.jpg",
  "Omar Suleiman": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/ImamOmarSuleiman2.jpg/330px-ImamOmarSuleiman2.jpg",
  "Amma": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/M%C4%81t%C4%81_Amrit%C4%81nandamay%C4%AB_Dev%C4%AB.jpg/330px-M%C4%81t%C4%81_Amrit%C4%81nandamay%C4%AB_Dev%C4%AB.jpg",
  "Pema Chödrön": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Pema_chodron_2007_cropped.jpg/330px-Pema_chodron_2007_cropped.jpg",
  "BK Shivani": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/BK_Shivani.jpg/330px-BK_Shivani.jpg",
  "Gaur Gopal Das": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/GaurGopal_Das.jpg/330px-GaurGopal_Das.jpg",
  "S.N. Goenka": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/The_Kalyanmitra_Satyanarayan_Goenka_who_brought_Vipassana_Meditation_technique_to_India_after_2500_years_is_seen_with_his_wife_while_speaking_at_a_talk_on_%22Values_in_Education_-_Good_Governance_through_Vipassana_Meditation%22_in.jpg/330px-thumbnail.jpg",
  "Sri M": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Sri_M.jpg/330px-Sri_M.jpg",
};

// Spiritual event keywords for filtering
const SPIRITUAL_EVENT_KEYWORDS = [
  "yoga", "meditation", "vipassana", "spiritual", "satsang", "retreat",
  "kirtan", "bhajan", "mantra", "mindfulness", "pranayama", "dharma",
  "buddhist", "temple", "ashram", "guru", "swami", "sadhguru", "isha",
  "art of living", "brahma kumaris", "iskcon", "hare krishna",
  "dalai lama", "thich nhat hanh", "plum village", "goenka",
  "amma", "deepak chopra", "eckhart tolle", "byron katie",
  "sri sri", "mooji", "jay shetty", "pema chodron", "sri m",
  "reiki", "sound healing", "breathwork", "kundalini", "wellness retreat",
];

function getTeacherImage(entry: WisdomEntry): string {
  return entry.teacher_image_url || TEACHER_IMAGES[entry.teacher_name] || entry.thumbnail_url || "";
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
}

function formatEventDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
}

export default function DailyWisdomPage() {
  const [entries, setEntries] = useState<WisdomEntry[]>([]);
  const [todayEntry, setTodayEntry] = useState<WisdomEntry | null>(null);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [spiritualEvents, setSpiritualEvents] = useState<SpiritualEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAll() {
      try {
        const today = new Date().toISOString().split("T")[0];

        // Fetch today's entry
        const { data: todayData } = await supabase
          .from("daily_wisdom")
          .select("*")
          .eq("featured_date", today)
          .eq("is_approved", true)
          .limit(1)
          .single();

        if (todayData) setTodayEntry(todayData as WisdomEntry);

        // Fetch all past entries
        const { data: allData } = await supabase
          .from("daily_wisdom")
          .select("*")
          .eq("is_approved", true)
          .not("featured_date", "is", null)
          .lte("featured_date", today)
          .order("featured_date", { ascending: false });

        if (allData) setEntries(allData as WisdomEntry[]);

        // Fetch all teachers
        const { data: teachersData } = await supabase
          .from("spiritual_teachers")
          .select("slug,name,tradition,image_url,is_org")
          .order("name");

        if (teachersData) setTeachers(teachersData as Teacher[]);

        // Fetch spiritual events using keyword matching
        const keywordFilter = SPIRITUAL_EVENT_KEYWORDS.slice(0, 20)
          .map(kw => `title.ilike.%${kw}%`)
          .join(",");

        const { data: eventsData } = await supabase
          .from("events")
          .select("id,title,date,time,venue_name,city,state,image_url,ticket_url,slug")
          .gte("date", today)
          .or(keywordFilter)
          .order("date", { ascending: true })
          .limit(10);

        if (eventsData) setSpiritualEvents(eventsData as SpiritualEvent[]);
      } catch (err) {
        console.error("Failed to load daily wisdom:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchAll();
  }, []);

  // Exclude today's entry from archive
  const archiveEntries = todayEntry
    ? entries.filter((e) => e.id !== todayEntry.id)
    : entries;

  return (
    <div className="min-h-screen flex flex-col" style={{ overflowX: 'hidden' }}>
      <Helmet>
        <title>Daily Wisdom — Spiritual Teachings | The Videshi</title>
        <meta name="description" content="Daily curated wisdom from spiritual masters across traditions — Hindu, Buddhist, Sikh, Islamic, and modern interfaith teachings. Teacher profiles, events, and more." />
      </Helmet>

      <Masthead />

      <main className="dw-page">
        {/* Hero / Today's Wisdom */}
        <section className="dw-hero">
          <div className="dw-hero-label">
            <span className="dw-hero-lotus">🪷</span>
            <h1>Daily Wisdom</h1>
            <p className="dw-hero-sub">Curated teachings from spiritual masters across traditions</p>
          </div>

          {todayEntry && (
            <div className="dw-today-card">
              <div className="dw-today-badge">Today's Wisdom</div>
              <div className="dw-today-inner">
                <Link to={todayEntry.teacher_slug ? `/daily-wisdom/teachers/${todayEntry.teacher_slug}` : "#"} className="dw-today-photo">
                  {getTeacherImage(todayEntry) ? (
                    <img src={getTeacherImage(todayEntry)} alt={todayEntry.teacher_name}
                      onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
                  ) : (
                    <div className="dw-today-photo-placeholder">
                      {TRADITION_ICONS[todayEntry.tradition] || "🙏"}
                    </div>
                  )}
                </Link>
                <div className="dw-today-content">
                  <blockquote className="dw-today-quote">
                    "{todayEntry.quote}"
                  </blockquote>
                  <div className="dw-today-attribution">
                    <Link
                      to={todayEntry.teacher_slug ? `/daily-wisdom/teachers/${todayEntry.teacher_slug}` : "#"}
                      className="dw-today-teacher-link"
                    >
                      — {todayEntry.teacher_name}
                    </Link>
                    <span className="dw-today-tradition" style={{ color: TRADITION_COLORS[todayEntry.tradition] }}>
                      {TRADITION_ICONS[todayEntry.tradition]} {todayEntry.tradition}
                    </span>
                  </div>
                  {todayEntry.source_url && (
                    <a href={todayEntry.source_url} target="_blank" rel="noopener noreferrer" className="dw-today-source">
                      {todayEntry.source_type === "youtube" ? "▶ Watch on YouTube" : "View Source"}
                      {todayEntry.source_title && ` — ${todayEntry.source_title}`}
                    </a>
                  )}
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Spiritual Events */}
        {spiritualEvents.length > 0 && (
          <section className="dw-events-section">
            <div className="dw-events-header">
              <h2 className="dw-events-title">🧘 Spiritual Events Near You</h2>
              <Link to="/events" className="dw-events-link">See all events →</Link>
            </div>
            <div className="dw-events-scroll">
              {spiritualEvents.map((evt) => (
                <a key={evt.id}
                  href={evt.ticket_url || `/events/${evt.slug}`}
                  target={evt.ticket_url ? "_blank" : undefined}
                  rel={evt.ticket_url ? "noopener noreferrer" : undefined}
                  className="dw-event-card">
                  {evt.image_url && (
                    <img src={evt.image_url} alt="" className="dw-event-img"
                      onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
                  )}
                  <div className="dw-event-body">
                    <div className="dw-event-name">{evt.title}</div>
                    <div className="dw-event-details">
                      {formatEventDate(evt.date)}
                      {evt.city ? ` · ${evt.city}` : ""}
                      {evt.state ? `, ${evt.state}` : ""}
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </section>
        )}

        {/* Teachers Grid */}
        {teachers.length > 0 && (
          <section className="dw-events-section">
            <div className="dw-events-header">
              <h2 className="dw-events-title">Spiritual Masters & Teachers</h2>
            </div>
            <div className="dw-teachers-grid">
              {teachers.map((t) => (
                <Link key={t.slug} to={`/daily-wisdom/teachers/${t.slug}`} className="dw-teacher-card">
                  <div className="dw-teacher-avatar">
                    {(t.image_url || TEACHER_IMAGES[t.name]) ? (
                      <img src={t.image_url || TEACHER_IMAGES[t.name]} alt={t.name}
                        onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
                    ) : (
                      <div className="dw-teacher-avatar-ph">
                        {TRADITION_ICONS[t.tradition] || "🙏"}
                      </div>
                    )}
                  </div>
                  <div className="dw-teacher-name">{t.name}</div>
                  <div className="dw-teacher-tradition" style={{ color: TRADITION_COLORS[t.tradition] }}>
                    {t.tradition}
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Archive grid */}
        <section className="dw-archive">
          <h2 className="dw-archive-title">Past Teachings</h2>
          {loading ? (
            <div className="dw-loading">Loading…</div>
          ) : archiveEntries.length === 0 ? (
            <div className="dw-empty">More teachings coming soon.</div>
          ) : (
            <div className="dw-archive-grid">
              {archiveEntries.map((entry) => (
                <div key={entry.id} className="dw-archive-card">
                  <Link
                    to={entry.teacher_slug ? `/daily-wisdom/teachers/${entry.teacher_slug}` : "#"}
                    className="dw-archive-card-top"
                  >
                    <div className="dw-archive-photo">
                      {getTeacherImage(entry) ? (
                        <img src={getTeacherImage(entry)} alt={entry.teacher_name}
                          onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
                      ) : (
                        <div className="dw-archive-photo-ph">
                          {TRADITION_ICONS[entry.tradition] || "🙏"}
                        </div>
                      )}
                    </div>
                    <div>
                      <div className="dw-archive-teacher">{entry.teacher_name}</div>
                      <div className="dw-archive-tradition" style={{ color: TRADITION_COLORS[entry.tradition] }}>
                        {entry.tradition}
                      </div>
                    </div>
                  </Link>
                  <blockquote className="dw-archive-quote">
                    "{entry.quote}"
                  </blockquote>
                  <div className="dw-archive-meta">
                    {entry.featured_date && (
                      <span className="dw-archive-date">{formatDate(entry.featured_date)}</span>
                    )}
                    {entry.source_url && (
                      <a href={entry.source_url} target="_blank" rel="noopener noreferrer" className="dw-archive-link">
                        {entry.source_type === "youtube" ? "▶" : "↗"}
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
