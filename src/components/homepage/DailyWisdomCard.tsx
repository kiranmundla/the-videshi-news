import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

/* Daily Wisdom — picture-framed card for the homepage.
   Shows today's wisdom quote with teacher photo, rotating daily across traditions. */

interface WisdomEntry {
  id: string;
  teacher_name: string;
  tradition: string;
  quote: string;
  source_title: string | null;
  source_url: string | null;
  thumbnail_url: string | null;
  teacher_image_url: string | null;
  featured_date: string | null;
}

// Static teacher images — fallback when DB doesn't have one
const TEACHER_IMAGES: Record<string, string> = {
  "Sadhguru": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Sadhguru_2020.jpg/440px-Sadhguru_2020.jpg",
  "Sri Sri Ravi Shankar": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Sri_Sri_Ravi_Shankar_2016.jpg/440px-Sri_Sri_Ravi_Shankar_2016.jpg",
  "BK Shivani": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/BK_Shivani_at_Brahma_Kumaris.jpg/440px-BK_Shivani_at_Brahma_Kumaris.jpg",
  "Gaur Gopal Das": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Gaur_Gopal_Das.jpg/440px-Gaur_Gopal_Das.jpg",
  "Mooji": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Mooji_in_Monte_Sahaja.jpg/440px-Mooji_in_Monte_Sahaja.jpg",
  "Dalai Lama": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Dalailama1_20121014_4639.jpg/440px-Dalailama1_20121014_4639.jpg",
  "Thich Nhat Hanh": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Thich_Nhat_Hanh_12_%28cropped%29.jpg/440px-Thich_Nhat_Hanh_12_%28cropped%29.jpg",
  "Deepak Chopra": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Deepak_Chopra_2013_Shankbone.jpg/440px-Deepak_Chopra_2013_Shankbone.jpg",
  "Jay Shetty": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Jay_Shetty_in_2019.jpg/440px-Jay_Shetty_in_2019.jpg",
  "Eckhart Tolle": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Eckhart_Tolle_2013.jpg/440px-Eckhart_Tolle_2013.jpg",
  "Omar Suleiman": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Omar_Suleiman_%28imam%29.jpg/440px-Omar_Suleiman_%28imam%29.jpg",
  "Amma": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Amma_at_her_ashram.jpg/440px-Amma_at_her_ashram.jpg",
  "Pema Chödrön": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Pema_Chodron.jpg/440px-Pema_Chodron.jpg",
};

const TRADITION_ICONS: Record<string, string> = {
  "Hindu / Yoga": "🙏",
  "Buddhist": "☸️",
  "Interfaith / Modern": "✨",
  "Islamic": "☪️",
  "Sikh": "🙏",
  "Jain": "🙏",
};

export default function DailyWisdomCard() {
  const [wisdom, setWisdom] = useState<WisdomEntry | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchTodayWisdom() {
      try {
        const today = new Date().toISOString().split("T")[0];
        
        // Try to get today's featured wisdom
        const { data, error } = await supabase
          .from("daily_wisdom")
          .select("*")
          .eq("featured_date", today)
          .eq("is_approved", true)
          .limit(1)
          .single();

        if (error || !data) {
          // Fallback: get the most recent featured wisdom
          const { data: fallback } = await supabase
            .from("daily_wisdom")
            .select("*")
            .eq("is_approved", true)
            .not("featured_date", "is", null)
            .order("featured_date", { ascending: false })
            .limit(1)
            .single();
          
          if (fallback) setWisdom(fallback as WisdomEntry);
        } else {
          setWisdom(data as WisdomEntry);
        }
      } catch (err) {
        console.error("Failed to load daily wisdom:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchTodayWisdom();
  }, []);

  if (loading || !wisdom) return null;

  const teacherImg = wisdom.teacher_image_url || TEACHER_IMAGES[wisdom.teacher_name] || wisdom.thumbnail_url || "";
  const traditionIcon = TRADITION_ICONS[wisdom.tradition] || "🙏";

  return (
    <section className="daily-wisdom-homepage">
      <Link to="/daily-wisdom" className="daily-wisdom-card">
        {/* Left: teacher photo in a frame */}
        <div className="daily-wisdom-photo">
          {teacherImg ? (
            <img
              src={teacherImg}
              alt={wisdom.teacher_name}
              loading="lazy"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
          ) : (
            <div className="daily-wisdom-photo-placeholder">
              <span>{traditionIcon}</span>
            </div>
          )}
        </div>

        {/* Right: quote + attribution */}
        <div className="daily-wisdom-content">
          <div className="daily-wisdom-label">
            <span className="daily-wisdom-icon">🪷</span>
            Daily Wisdom
          </div>
          <blockquote className="daily-wisdom-quote">
            "{wisdom.quote}"
          </blockquote>
          <div className="daily-wisdom-teacher">
            — {wisdom.teacher_name}
            <span className="daily-wisdom-tradition">{wisdom.tradition}</span>
          </div>
        </div>
      </Link>
    </section>
  );
}
