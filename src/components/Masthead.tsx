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
      </div>
    </header>
  );
}
