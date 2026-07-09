import { Link } from "react-router-dom";
import { Article } from "@/lib/articles";

interface Props {
  article: Article | null;
}

export default function VoicesTeaser({ article }: Props) {
  if (!article) return null;

  return (
    <section className="mb-14">
      <div className="container">
        <div className="v2-voices-teaser">
          <p
            className="text-[10px] font-bold tracking-[1.5px] uppercase mb-3"
            style={{ color: "#D4A843" }}
          >
            ✍️ From Voices
          </p>
          <div className="flex items-start gap-4">
            <div className="flex-1 min-w-0">
              <blockquote className="font-serif text-[15px] italic leading-relaxed mb-2" style={{ color: "#0B1D3A" }}>
                "{article.excerpt || article.title}"
              </blockquote>
              <span className="text-xs text-muted-foreground">
                {article.author ?? "Community"} ·{" "}
                <Link
                  to={`/articles/${article.slug}`}
                  className="font-semibold hover:opacity-70 transition-opacity"
                  style={{ color: "#D4A843" }}
                >
                  Read full story →
                </Link>
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
