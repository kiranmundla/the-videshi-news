import { Link, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react";
import { formatLongDate } from "@/lib/articles";

const NAV = [
  { label: "Home", to: "/" },
  { label: "India", to: "/?c=India" },
  { label: "NRI Affairs", to: "/?c=NRI%20Affairs" },
  { label: "US-India", to: "/?c=US-India" },
  { label: "Business", to: "/?c=Business" },
  { label: "Culture", to: "/?c=Culture" },
  { label: "Sports", to: "/?c=Sports" },
  { label: "Voices", to: "/?c=Voices" },
];

export default function Masthead() {
  const [open, setOpen] = useState(false);
  const today = formatLongDate(new Date().toISOString());
  const { pathname } = useLocation();

  useEffect(() => setOpen(false), [pathname]);

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
          <button
            aria-label="Open menu"
            className="md:hidden p-2 -mr-2 text-foreground"
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
        <div className="md:hidden pb-3">
          <p className="smallcaps text-muted-foreground">{today}</p>
        </div>
        <div style={{ height: "0.5px" }} className="bg-rule w-full" />
        <nav className="hidden md:block">
          <ul className="flex flex-wrap gap-x-7 gap-y-2 py-3.5 text-[0.82rem] font-medium tracking-wide">
            {NAV.map((n) => (
              <li key={n.label}>
                <Link
                  to={n.to}
                  className="text-foreground/85 hover:text-primary transition-colors"
                >
                  {n.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <div style={{ height: "0.5px" }} className="hidden md:block bg-rule w-full" />
        {open && (
          <nav className="md:hidden py-3 border-b hairline">
            <ul className="flex flex-col gap-3 text-base">
              {NAV.map((n) => (
                <li key={n.label}>
                  <Link to={n.to} className="text-foreground/90 hover:text-primary">
                    {n.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        )}
      </div>
    </header>
  );
}
