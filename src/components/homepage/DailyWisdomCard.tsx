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
