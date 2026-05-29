import { useRef, useState, useCallback, useEffect } from "react";

interface Champion {
  year: number;
  name: string;
  age: number;
  hometown: string;
  word: string;
  coChampion?: boolean;
  highlight?: boolean;
}

const CHAMPIONS: Champion[] = [
  { year: 1985, name: "Balu Natarajan", age: 13, hometown: "Chicago, IL", word: "milieu" },
  { year: 1988, name: "Rageshree Ramachandran", age: 14, hometown: "Sacramento, CA", word: "elegiacal" },
  { year: 1999, name: "Nupur Lala", age: 14, hometown: "Tampa, FL", word: "logorrhea" },
  { year: 2000, name: "George Abraham Thampy", age: 12, hometown: "St. Louis, MO", word: "demarche" },
  { year: 2002, name: "Pratyush Buddiga", age: 13, hometown: "Denver, CO", word: "prospicience" },
  { year: 2003, name: "Sai R. Gunturi", age: 14, hometown: "Dallas, TX", word: "pococurante" },
  { year: 2005, name: "Anurag Kashyap", age: 13, hometown: "San Diego, CA", word: "appoggiatura" },
  { year: 2008, name: "Sameer Mishra", age: 13, hometown: "West Lafayette, IN", word: "guerdon" },
  { year: 2009, name: "Kavya Shivashankar", age: 13, hometown: "Olathe, KS", word: "Laodicean" },
  { year: 2010, name: "Anamika Veeramani", age: 14, hometown: "Cleveland, OH", word: "stromuhr" },
  { year: 2011, name: "Sukanya Roy", age: 14, hometown: "Wilkes-Barre, PA", word: "cymotrichous" },
  { year: 2012, name: "Snigdha Nandipati", age: 14, hometown: "San Diego, CA", word: "guetapens" },
  { year: 2013, name: "Arvind Mahankali", age: 13, hometown: "New York, NY", word: "knaidel" },
  { year: 2014, name: "Sriram Hathwar", age: 14, hometown: "Corning, NY", word: "stichomythia", coChampion: true },
  { year: 2014, name: "Ansun Sujoe", age: 13, hometown: "Fort Worth, TX", word: "feuilleton", coChampion: true },
  { year: 2015, name: "Vanya Shivashankar", age: 13, hometown: "Olathe, KS", word: "scherenschnitte", coChampion: true },
  { year: 2015, name: "Gokul Venkatachalam", age: 14, hometown: "St. Louis, MO", word: "nunatak", coChampion: true },
  { year: 2016, name: "Jairam Hathwar", age: 13, hometown: "Corning, NY", word: "Feldenkrais", coChampion: true },
  { year: 2016, name: "Nihar Saireddy Janga", age: 11, hometown: "Austin, TX", word: "gesellschaft", coChampion: true },
  { year: 2017, name: "Ananya Vinay", age: 12, hometown: "Fresno, CA", word: "marocain" },
  { year: 2018, name: "Karthik Nemmani", age: 14, hometown: "McKinney, TX", word: "koinonia" },
  { year: 2019, name: "Rishik Gandhasri", age: 13, hometown: "San Jose, CA", word: "auslaut", coChampion: true },
  { year: 2019, name: "Saketh Sundar", age: 13, hometown: "Clarksville, MD", word: "bougainvillea", coChampion: true },
  { year: 2019, name: "Shruthika Padhy", age: 13, hometown: "Cherry Hill, NJ", word: "aiguillette", coChampion: true },
  { year: 2019, name: "Sohum Sukhatankar", age: 13, hometown: "Dallas, TX", word: "pendeloque", coChampion: true },
  { year: 2019, name: "Abhijay Kodali", age: 12, hometown: "Flower Mound, TX", word: "palama", coChampion: true },
  { year: 2019, name: "Rohan Raja", age: 13, hometown: "Irving, TX", word: "odylic", coChampion: true },
  { year: 2022, name: "Harini Logan", age: 14, hometown: "San Antonio, TX", word: "moorhen" },
  { year: 2023, name: "Dev Shah", age: 14, hometown: "Largo, FL", word: "psammophile" },
  { year: 2024, name: "Bruhat Soma", age: 12, hometown: "St. Petersburg, FL", word: "abseil" },
  { year: 2026, name: "Shrey Parikh", age: 14, hometown: "Rancho Cucamonga, CA", word: "bromocriptine", highlight: true },
];

const NAVY = "#1a1a2e";
const GOLD = "#d4a855";

export default function ChampionsTimeline() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const updateScrollButtons = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 10);
    setCanScrollRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 10);
  }, []);

  const scrollStrip = useCallback((direction: "left" | "right") => {
    const el = scrollRef.current;
    if (!el) return;
    const amount = el.clientWidth * 0.75;
    el.scrollBy({ left: direction === "right" ? amount : -amount, behavior: "smooth" });
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    updateScrollButtons();
    el.addEventListener("scroll", updateScrollButtons, { passive: true });
    window.addEventListener("resize", updateScrollButtons);
    return () => {
      el.removeEventListener("scroll", updateScrollButtons);
      window.removeEventListener("resize", updateScrollButtons);
    };
  }, [updateScrollButtons]);

  return (
    <section className="my-10 -mx-4 md:-mx-6 lg:-mx-8">
      <style>{`
        .champ-scroll::-webkit-scrollbar { display: none; }
        .champ-scroll { scrollbar-width: none; -ms-overflow-style: none; }
        .champ-card { transition: transform 0.2s ease, box-shadow 0.2s ease; }
        .champ-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.3); }
      `}</style>

      {/* Section heading */}
      <h2
        className="font-serif text-2xl md:text-3xl font-bold mb-1 px-4 md:px-6 lg:px-8"
        style={{ color: "inherit" }}
      >
        Every Indian American Champion: 1985–2026
      </h2>
      <p className="text-sm text-muted-foreground mb-5 px-4 md:px-6 lg:px-8">
        Scroll through four decades of dominance →
      </p>

      {/* Scroll container */}
      <div className="relative">
        {/* Left arrow */}
        {canScrollLeft && (
          <button
            onClick={() => scrollStrip("left")}
            aria-label="Scroll left"
            className="hidden md:flex absolute left-1 top-1/2 -translate-y-1/2 z-10 items-center justify-center"
            style={{
              width: 36,
              height: 36,
              borderRadius: "50%",
              background: "rgba(255,255,255,0.95)",
              border: "1px solid rgba(0,0,0,0.1)",
              boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
              cursor: "pointer",
            }}
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M9 2L4 7l5 5" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        )}

        {/* Right arrow */}
        {canScrollRight && (
          <button
            onClick={() => scrollStrip("right")}
            aria-label="Scroll right"
            className="hidden md:flex absolute right-1 top-1/2 -translate-y-1/2 z-10 items-center justify-center"
            style={{
              width: 36,
              height: 36,
              borderRadius: "50%",
              background: "rgba(255,255,255,0.95)",
              border: "1px solid rgba(0,0,0,0.1)",
              boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
              cursor: "pointer",
            }}
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M5 2l5 5-5 5" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        )}

        <div
          ref={scrollRef}
          className="champ-scroll flex gap-3 overflow-x-auto px-4 md:px-6 lg:px-8 pb-3"
          style={{
            scrollSnapType: "x proximity",
            WebkitOverflowScrolling: "touch",
          }}
        >
          {CHAMPIONS.map((c, i) => (
            <div
              key={`${c.year}-${c.name}-${i}`}
              className="champ-card flex-shrink-0 rounded-lg overflow-hidden"
              style={{
                width: 156,
                minHeight: 180,
                background: c.highlight ? GOLD : NAVY,
                borderTop: `3px solid ${c.highlight ? NAVY : GOLD}`,
                scrollSnapAlign: "start",
                padding: "14px 12px 12px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
              }}
            >
              {/* Top: Year + co-champion star */}
              <div>
                <div className="flex items-center gap-1.5">
                  <span
                    style={{
                      fontSize: 28,
                      fontWeight: 800,
                      lineHeight: 1,
                      color: c.highlight ? NAVY : GOLD,
                      fontFamily: "Inter, system-ui, sans-serif",
                    }}
                  >
                    {c.year}
                  </span>
                  {c.coChampion && (
                    <span
                      style={{
                        fontSize: 16,
                        color: c.highlight ? NAVY : GOLD,
                        lineHeight: 1,
                        marginTop: -4,
                      }}
                      title="Co-champion"
                    >
                      ★
                    </span>
                  )}
                </div>

                {/* Name */}
                <div
                  style={{
                    fontSize: 13,
                    fontWeight: 700,
                    color: c.highlight ? NAVY : "#fff",
                    marginTop: 8,
                    lineHeight: 1.3,
                  }}
                >
                  {c.name}
                </div>

                {/* Age + Hometown */}
                <div
                  style={{
                    fontSize: 10.5,
                    color: c.highlight ? "rgba(26,26,46,0.65)" : "rgba(255,255,255,0.5)",
                    marginTop: 4,
                    lineHeight: 1.4,
                  }}
                >
                  Age {c.age} · {c.hometown}
                </div>
              </div>

              {/* Bottom: Winning word */}
              <div
                style={{
                  fontSize: 11.5,
                  fontStyle: "italic",
                  color: c.highlight ? "rgba(26,26,46,0.8)" : "rgba(212,168,85,0.85)",
                  marginTop: 10,
                  lineHeight: 1.3,
                  wordBreak: "break-word",
                }}
              >
                {c.word}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer notes */}
      <div className="mt-4 px-4 md:px-6 lg:px-8 space-y-2">
        <p
          className="font-serif font-bold text-base md:text-lg"
          style={{ color: "inherit" }}
        >
          31 Indian American champions. 22 winning years. Out of 28 Bees since 1985.
        </p>
        <p className="text-xs text-muted-foreground">
          ★ = Co-champion &nbsp;·&nbsp; 2020: cancelled (COVID-19) &nbsp;·&nbsp; 2021: Zaila Avant-garde became the first African American champion &nbsp;·&nbsp; 2025: Faizan Zaki
        </p>
      </div>
    </section>
  );
}
