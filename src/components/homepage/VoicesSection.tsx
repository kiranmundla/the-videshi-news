import { Link } from "react-router-dom";
import { Article } from "@/lib/articles";

/* Voices section — real stories from the diaspora.
   Currently uses placeholder author data since the stories table is empty.
   When stories are available, this will be driven by real DB data. */

interface VoiceStory {
  id: string;
  author: string;
  route: string;
  quote: string;
  tag: string;
  slug?: string;
}

interface Props {
  stories?: VoiceStory[];
}

const PLACEHOLDER_STORIES: VoiceStory[] = [
  {
    id: "vs-1",
    author: "Saurabh Mehta",
    route: "Mumbai → San Jose",
    quote:
      "After 11 years on H-1B and three green card denials, I finally got my approval notice. Here's what I wish someone told me on day one.",
    tag: "H-1B TO GREEN CARD · 12 MIN READ",
  },
  {
    id: "vs-2",
    author: "Arjun Krishnan",
    route: "Chennai → Vancouver",
    quote:
      "I left a $300K Tesla job in the Bay Area for Canadian PR. My American friends thought I was crazy, but here's why it made sense.",
    tag: "CANADA PR · 9 MIN READ",
  },
  {
    id: "vs-3",
    author: "Priya Nair",
    route: "Kochi → London",
    quote:
      "Building a restaurant in London's East End as a first-gen immigrant entrepreneur — the visa hurdles nobody warns you about.",
    tag: "UK ENTREPRENEUR · 8 MIN READ",
  },
  {
    id: "vs-4",
    author: "Rohan Desai",
    route: "Pune → Austin",
    quote:
      "We moved back to India after 8 years in the US, then returned to Austin within 18 months. The reverse culture shock nobody talks about.",
    tag: "REVERSE MIGRATION · 10 MIN READ",
  },
];

export default function VoicesSection({ stories }: Props) {
  const items = stories && stories.length > 0 ? stories : PLACEHOLDER_STORIES;

  return (
    <section className="v2-voices-section mb-0">
      <div className="container">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <h2
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            ✍️ Voices
          </h2>
          <Link
            to="/stories"
            className="text-[13px] font-semibold transition-opacity hover:opacity-70"
            style={{ color: "#D4A843" }}
          >
            Share your story →
          </Link>
        </div>
        <p className="text-sm text-muted-foreground mb-5">
          Real immigration journeys and diaspora experiences, told by the people
          who lived them.
        </p>

        {/* Scroll strip */}
        <div className="v2-voices-scroll">
          {items.map((s) => (
            <div
              key={s.id}
              className="flex-shrink-0 bg-white rounded-xl p-5 border"
              style={{
                width: 300,
                minWidth: 300,
                borderColor: "hsl(var(--rule))",
                boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
              }}
            >
              {/* Author */}
              <div className="flex items-center gap-3 mb-3">
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white"
                  style={{ background: "#D4A843" }}
                >
                  {s.author
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>
                <div>
                  <p className="text-sm font-bold" style={{ color: "#0B1D3A" }}>
                    {s.author}
                  </p>
                  <p className="text-xs text-muted-foreground">{s.route}</p>
                </div>
              </div>

              {/* Quote */}
              <blockquote
                className="font-serif text-[14px] italic leading-relaxed mb-3 pl-3"
                style={{
                  color: "#0B1D3A",
                  borderLeft: "3px solid #D4A843",
                }}
              >
                "{s.quote}"
              </blockquote>

              {/* Tag */}
              <p
                className="text-[10px] font-bold tracking-[1.2px] uppercase"
                style={{ color: "#D4A843" }}
              >
                {s.tag}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
