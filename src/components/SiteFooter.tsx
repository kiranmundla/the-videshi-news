import { Link } from "react-router-dom";
import NewsletterSignup from "./NewsletterSignup";

export default function SiteFooter({ lastUpdated }: { lastUpdated?: Date | null }) {
  return (
    <footer className="mt-20 border-t hairline">
      <div className="container py-10 grid gap-8 md:grid-cols-4">
        <div>
          <p className="font-serif text-2xl font-bold">The Videshi</p>
          <p className="italic text-muted-foreground text-sm mt-1">
            News for the global Indian diaspora
          </p>
        </div>
        <ul className="space-y-2 text-sm text-foreground/80">
          <li><Link to="/about" className="hover:text-primary">About</Link></li>
          <li><Link to="/contact" className="hover:text-primary">Contact</Link></li>
          <li><Link to="/privacy" className="hover:text-primary">Privacy Policy</Link></li>
          <li><Link to="/terms" className="hover:text-primary">Terms of Service</Link></li>
          <li>
            <a href="/rss.xml" className="hover:text-primary inline-flex items-center gap-1">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5">
                <path d="M6.18 15.64a2.18 2.18 0 012.18 2.18C8.36 19 7.38 20 6.18 20 5 20 4 19 4 17.82a2.18 2.18 0 012.18-2.18M4 4.44A15.56 15.56 0 0119.56 20h-2.83A12.73 12.73 0 004 7.27V4.44M4 10.1a9.9 9.9 0 019.9 9.9h-2.83A7.07 7.07 0 004 12.93V10.1z"/>
              </svg>
              RSS Feed
            </a>
          </li>
        </ul>
        <NewsletterSignup variant="footer" />
        <div className="text-xs text-muted-foreground md:text-right self-end space-y-1">
          {lastUpdated && (
            <p>
              Last updated:{" "}
              {lastUpdated.toLocaleString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
                hour: "numeric",
                minute: "2-digit",
              })}
            </p>
          )}
          <p>© {new Date().getFullYear()} The Videshi. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
