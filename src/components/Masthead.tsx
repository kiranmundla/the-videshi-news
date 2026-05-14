import { Link } from "react-router-dom";
import { formatLongDate } from "@/lib/articles";

export default function Masthead() {
  const today = formatLongDate(new Date().toISOString());

  return (
    <header className="bg-background">
      <div className="container">
        <div className="flex items-end justify-between pt-8 pb-4 md:pt-10 md:pb-5">
          <Link to="/" className="block">
            <h1 className="font-serif font-black tracking-tight text-foreground leading-none text-[2.25rem] md:text-[3.25rem] lg:text-[3.75rem]">
              The Videshi
            </h1>
            <p className="italic text-muted-foreground text-xs md:text-sm mt-1.5">
              News for the global Indian diaspora
            </p>
          </Link>
          <div className="hidden md:block text-right">
            <p className="smallcaps text-muted-foreground">{today}</p>
          </div>
        </div>
        <div className="md:hidden pb-3">
          <p className="smallcaps text-muted-foreground">{today}</p>
        </div>
        <div style={{ height: "0.5px" }} className="bg-rule w-full" />
        <nav style={{ display: "flex", gap: "24px", paddingTop: "10px", paddingBottom: "10px", overflowX: "auto" }}>
          {[
            { label: "Home", path: "/" },
            { label: "Travel", path: "/travel" },
            { label: "Sports", path: "/sports" },
            { label: "Markets", path: "/markets-finance" },
            { label: "Technology", path: "/technology" },
            { label: "Entertainment", path: "/entertainment" },
          ].map((item) => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                fontFamily: "inherit",
                fontSize: "0.8rem",
                fontWeight: 600,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                color: "var(--foreground, #1a1a1a)",
                textDecoration: "none",
                whiteSpace: "nowrap",
                opacity: 0.7,
              }}
              onMouseEnter={(e) => (e.currentTarget.style.opacity = "1")}
              onMouseLeave={(e) => (e.currentTarget.style.opacity = "0.7")}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div style={{ height: "0.5px" }} className="bg-rule w-full" />
      </div>
    </header>
  );
}
