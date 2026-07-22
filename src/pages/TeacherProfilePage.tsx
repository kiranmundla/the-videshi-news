import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useParams } from "react-router-dom";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import { supabase } from "@/integrations/supabase/client";
import "./DailyWisdomPage.css";
import "./TeacherProfilePage.css";

interface Teacher {
  slug: string;
  name: string;
  tradition: string;
  bio: string | null;
  journey: string | null;
  youtube_url: string | null;
  website_url: string | null;
  image_url: string | null;
  org_name: string | null;
  is_org: boolean;
  born: string | null;
  origin: string | null;
  key_teachings: string | null;
  followers_desc: string | null;
  books: { title: string; amazon_url?: string; year?: number; excerpt?: string; cover_url?: string }[] | null;
}

interface WisdomEntry {
  id: string;
  teacher_name: string;
  tradition: string;
  quote: string;
  source_title: string | null;
  source_url: string | null;
  source_type: string | null;
  teacher_image_url: string | null;
  featured_date: string | null;
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

const TRADITION_COLORS: Record<string, string> = {
  "Hindu / Yoga": "#D4A843",
  "Buddhist": "#C0392B",
  "Interfaith / Modern": "#2980B9",
  "Islamic": "#27AE60",
  "Sikh": "#E67E22",
  "Jain": "#8E44AD",
};

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
}

function formatEventDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
}

export default function TeacherProfilePage() {
  const { slug } = useParams<{ slug: string }>();
  const [teacher, setTeacher] = useState<Teacher | null>(null);
  const [quotes, setQuotes] = useState<WisdomEntry[]>([]);
  const [events, setEvents] = useState<SpiritualEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!slug) return;

    async function fetchData() {
      try {
        // Fetch teacher profile
        const { data: teacherData } = await supabase
          .from("spiritual_teachers")
          .select("*")
          .eq("slug", slug)
          .single();

        if (teacherData) setTeacher(teacherData as Teacher);

        // Fetch their quotes
        const today = new Date().toISOString().split("T")[0];
        const { data: quotesData } = await supabase
          .from("daily_wisdom")
          .select("*")
          .eq("teacher_slug", slug)
          .eq("is_approved", true)
          .lte("featured_date", today)
          .order("featured_date", { ascending: false });

        if (quotesData) setQuotes(quotesData as WisdomEntry[]);

        // Fetch spiritual events matching teacher/org name
        if (teacherData) {
          const name = (teacherData as Teacher).name;
          const orgName = (teacherData as Teacher).org_name;
          // Search events by teacher name or org name in title or organizer
          const searchTerms = [name];
          if (orgName) searchTerms.push(orgName);
          const orFilter = searchTerms
            .flatMap(t => [`title.ilike.%${t}%`, `organizer.ilike.%${t}%`])
            .join(",");

          const { data: eventsData } = await supabase
            .from("events")
            .select("id,title,date,time,venue_name,city,state,image_url,ticket_url,slug")
            .gte("date", today)
            .or(orFilter)
            .order("date", { ascending: true })
            .limit(6);
          if (eventsData) setEvents(eventsData as SpiritualEvent[]);
        }
      } catch (err) {
        console.error("Failed to load teacher profile:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col" style={{ overflowX: 'hidden' }}>
        <Masthead />
        <main className="dw-page"><div className="dw-loading">Loading…</div></main>
        <SiteFooter />
      </div>
    );
  }

  if (!teacher) {
    return (
      <div className="min-h-screen flex flex-col" style={{ overflowX: 'hidden' }}>
        <Masthead />
        <main className="dw-page"><div className="dw-empty">Teacher not found.</div></main>
        <SiteFooter />
      </div>
    );
  }

  const teachings = teacher.key_teachings?.split(",").map(t => t.trim()) || [];

  return (
    <div className="min-h-screen flex flex-col" style={{ overflowX: 'hidden' }}>
      <Helmet>
        <title>{teacher.name} — Daily Wisdom | The Videshi</title>
        <meta name="description" content={teacher.bio || `Spiritual teachings from ${teacher.name}`} />
      </Helmet>

      <Masthead />

      <main className="dw-page">
        {/* Breadcrumb */}
        <nav className="tp-breadcrumb">
          <Link to="/daily-wisdom">← Daily Wisdom</Link>
        </nav>

        {/* Hero profile section */}
        <section className="tp-hero">
          <div className="tp-hero-photo-wrap">
            {teacher.image_url ? (
              <img src={teacher.image_url} alt={teacher.name} className="tp-hero-photo"
                onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
            ) : (
              <div className="tp-hero-photo-ph">🙏</div>
            )}
          </div>
          <div className="tp-hero-info">
            <h1 className="tp-hero-name">{teacher.name}</h1>
            <div className="tp-hero-tradition" style={{ color: TRADITION_COLORS[teacher.tradition] }}>
              {teacher.tradition}
            </div>
            {teacher.org_name && (
              <div className="tp-hero-org">{teacher.org_name}</div>
            )}
            <div className="tp-hero-meta">
              {teacher.born && <span>{teacher.is_org ? "Founded" : "Born"}: {teacher.born}</span>}
              {teacher.origin && <span>Origin: {teacher.origin}</span>}
            </div>
            {teacher.followers_desc && (
              <p className="tp-hero-followers">{teacher.followers_desc}</p>
            )}
            <div className="tp-hero-links">
              {teacher.youtube_url && (
                <a href={teacher.youtube_url} target="_blank" rel="noopener noreferrer" className="tp-link tp-link-yt">
                  ▶ YouTube
                </a>
              )}
              {teacher.website_url && (
                <a href={teacher.website_url} target="_blank" rel="noopener noreferrer" className="tp-link tp-link-web">
                  🌐 Website
                </a>
              )}
            </div>
          </div>
        </section>

        {/* Bio */}
        {teacher.bio && (
          <section className="tp-section">
            <h2 className="tp-section-title">About</h2>
            <p className="tp-bio-text">{teacher.bio}</p>
          </section>
        )}

        {/* Spiritual Journey */}
        {teacher.journey && (
          <section className="tp-section">
            <h2 className="tp-section-title">
              {teacher.is_org ? "The Story" : "Spiritual Journey"}
            </h2>
            <div className="tp-journey-card">
              <p className="tp-journey-text">{teacher.journey}</p>
            </div>
          </section>
        )}

        {/* Key Teachings */}
        {teachings.length > 0 && (
          <section className="tp-section">
            <h2 className="tp-section-title">Key Teachings</h2>
            <div className="tp-teachings-grid">
              {teachings.map((t, i) => (
                <span key={i} className="tp-teaching-pill">{t}</span>
              ))}
            </div>
          </section>
        )}

        {/* Books */}
        {teacher.books && teacher.books.length > 0 && (
          <section className="tp-section">
            <h2 className="tp-section-title">Books</h2>
            <div className="tp-books-grid">
              {teacher.books.map((book, i) => (
                <div key={i} className="tp-book-card">
                  {book.cover_url ? (
                    <img src={book.cover_url} alt={book.title} className="tp-book-cover"
                      onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
                  ) : (
                    <div className="tp-book-icon">📖</div>
                  )}
                  <div className="tp-book-info">
                    {book.amazon_url ? (
                      <a href={book.amazon_url} target="_blank" rel="noopener noreferrer" className="tp-book-title-link">{book.title}</a>
                    ) : (
                      <div className="tp-book-title">{book.title}</div>
                    )}
                    {book.year && <div className="tp-book-year">{book.year}</div>}
                    {book.excerpt && <div className="tp-book-excerpt">{book.excerpt}</div>}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Events */}
        {events.length > 0 && (
          <section className="tp-section">
            <h2 className="tp-section-title">Upcoming Events</h2>
            <div className="tp-events-list">
              {events.map((evt) => (
                <a key={evt.id} href={evt.ticket_url || `/events/${evt.slug}`}
                  target={evt.ticket_url ? "_blank" : undefined}
                  rel={evt.ticket_url ? "noopener noreferrer" : undefined}
                  className="tp-event-card">
                  <div className="tp-event-date-badge">
                    {formatEventDate(evt.date)}
                  </div>
                  <div className="tp-event-info">
                    <div className="tp-event-title">{evt.title}</div>
                    {(evt.city || evt.venue_name) && (
                      <div className="tp-event-venue">
                        {evt.venue_name}{evt.city ? `, ${evt.city}` : ""}{evt.state ? `, ${evt.state}` : ""}
                      </div>
                    )}
                  </div>
                  <span className="tp-event-arrow">→</span>
                </a>
              ))}
            </div>
          </section>
        )}

        {/* Quotes / Teachings */}
        <section className="tp-section">
          <h2 className="tp-section-title">
            {quotes.length > 0 ? "Teachings & Wisdom" : "Teachings Coming Soon"}
          </h2>
          {quotes.length > 0 ? (
            <div className="tp-quotes-list">
              {quotes.map((q) => (
                <div key={q.id} className="tp-quote-card">
                  <blockquote className="tp-quote-text">"{q.quote}"</blockquote>
                  <div className="tp-quote-meta">
                    {q.featured_date && (
                      <span className="tp-quote-date">{formatDate(q.featured_date)}</span>
                    )}
                    {q.source_url && (
                      <a href={q.source_url} target="_blank" rel="noopener noreferrer" className="tp-quote-source">
                        {q.source_type === "youtube" ? "▶ Watch" : q.source_type === "book" ? "📖 Source" : "↗ Source"}
                        {q.source_title && ` — ${q.source_title}`}
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="tp-empty">We're curating teachings from {teacher.name}. Check back soon.</p>
          )}
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
