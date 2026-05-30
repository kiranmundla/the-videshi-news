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
        <div>
          <p className="font-semibold text-sm mb-3">Follow Us</p>
          <div className="flex items-center gap-4">
            <a href="https://whatsapp.com/channel/0029VbDgeZ384OmDKJX0hn16" target="_blank" rel="noopener noreferrer" className="text-foreground/70 hover:text-foreground transition-colors" aria-label="Follow us on WhatsApp">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
              </svg>
            </a>
            <a href="https://x.com/thevideshi" target="_blank" rel="noopener noreferrer" className="text-foreground/70 hover:text-foreground transition-colors" aria-label="Follow us on X">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
              </svg>
            </a>
            <a href="https://instagram.com/the.videshi" target="_blank" rel="noopener noreferrer" className="text-foreground/70 hover:text-foreground transition-colors" aria-label="Follow us on Instagram">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
              </svg>
            </a>
            <a href="https://www.facebook.com/profile.php?id=1145353431990758" target="_blank" rel="noopener noreferrer" className="text-foreground/70 hover:text-foreground transition-colors" aria-label="Follow us on Facebook">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
            </a>
            <a href="https://youtube.com/@the.videshi" target="_blank" rel="noopener noreferrer" className="text-foreground/70 hover:text-foreground transition-colors" aria-label="Follow us on YouTube">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
              </svg>
            </a>
            <a href="https://threads.net/@the.videshi" target="_blank" rel="noopener noreferrer" className="text-foreground/70 hover:text-foreground transition-colors" aria-label="Follow us on Threads">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M12.186 24h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35 18.44 1.5 15.586 1.472 12.01v-.017c.03-3.579.879-6.43 2.525-8.482C5.845 1.205 8.6.024 12.18 0h.014c2.746.02 5.043.725 6.826 2.098 1.677 1.29 2.858 3.13 3.509 5.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54 2.717C4.307 6.504 3.616 8.914 3.59 12c.025 3.083.718 5.496 2.057 7.164 1.432 1.784 3.631 2.698 6.54 2.717 2.623-.02 4.358-.631 5.8-2.045 1.647-1.613 1.618-3.593 1.09-4.798-.348-.794-.947-1.44-1.722-1.872-.137 1.467-.544 2.632-1.228 3.469-.883 1.082-2.155 1.654-3.783 1.7-1.262-.035-2.335-.425-3.093-1.126-.797-.736-1.22-1.74-1.188-2.825.058-1.964 1.622-3.395 3.942-3.608.951-.087 1.916-.056 2.858.088-.112-.622-.336-1.1-.675-1.424-.505-.483-1.276-.73-2.29-.734h-.032c-.795.003-1.533.21-2.07.6-.416.3-.717.714-.89 1.214l-1.972-.636c.27-.776.775-1.433 1.49-1.932.937-.655 2.136-.996 3.465-1.004h.042c1.54.009 2.755.428 3.61 1.244.71.678 1.14 1.584 1.3 2.69.585.18 1.132.42 1.633.72 1.178.707 2.065 1.74 2.575 3.003.786 1.95.78 4.605-1.34 6.682-1.796 1.76-4.012 2.534-7.147 2.557zM8.67 15.822c-.022.656.218 1.22.676 1.643.518.478 1.264.734 2.16.756 1.104-.03 1.963-.405 2.554-1.129.478-.586.786-1.42.91-2.477-.67-.12-1.362-.17-2.047-.128-1.584.145-2.603.99-2.643 1.972-.002.044-.009.216-.009.216l-.001.004v.003l.004-.003-.003.006.004-.006-.003.006.004-.006-.003.006.004-.006-.003.006.004-.006-.003.006.004-.006-.003.006.004-.006-.003.006.004-.006-.004.006z"/>
              </svg>
            </a>
          </div>
        </div>
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
