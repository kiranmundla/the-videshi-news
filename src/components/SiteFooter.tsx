import { Link } from "react-router-dom";

export default function SiteFooter({ lastUpdated }: { lastUpdated?: Date | null }) {
  return (
    <footer className="mt-20 border-t hairline">
      <div className="container py-10 grid gap-8 md:grid-cols-3">
        <div>
          <p className="font-serif text-2xl font-bold">The Videshi</p>
          <p className="italic text-muted-foreground text-sm mt-1">
            News for the global Indian diaspora
          </p>
        </div>
        <ul className="space-y-2 text-sm text-foreground/80">
          <li><Link to="/" className="hover:text-primary">About</Link></li>
          <li><Link to="/" className="hover:text-primary">Contact</Link></li>
          <li><Link to="/" className="hover:text-primary">Newsletter</Link></li>
        </ul>
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
