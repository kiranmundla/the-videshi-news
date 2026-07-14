import { useState } from "react";
import { Link } from "react-router-dom";
import { Article, formatShortDate } from "@/lib/articles";
import HeroImage, { isValidImage } from "@/components/HeroImage";

/* ── Sub-topic definitions per category ── */

export interface SubTopicDef {
  key: string;
  label: string;
  tags: string[]; // articles matching ANY of these tags go here
}

export const CATEGORY_SUBTOPICS: Record<string, SubTopicDef[]> = {
  immigration: [
    {
      key: "h1b",
      label: "H-1B & Work Visas",
      tags: [
        "h1b", "h4", "h4-ead", "indian-workers", "indian-it",
        "layoffs", "100k-fee", "fees", "tcs", "infosys",
        "dol", "perm", "fraud", "fy2027",
      ],
    },
    {
      key: "green-card",
      label: "Green Card & EB Categories",
      tags: [
        "green-card", "green card", "green-card-backlog", "backlog",
        "eb-2", "eb2", "eb-1a", "niw", "adjustment-of-status",
        "i-485", "visa-bulletin",
      ],
    },
    {
      key: "students",
      label: "Students & OPT",
      tags: [
        "opt", "f1-visa", "stem-opt", "student-visa",
        "indian-students", "students", "duration-of-status",
      ],
    },
    {
      key: "policy",
      label: "Policy & Enforcement",
      tags: [
        "uscis", "dhs", "ice", "deportation", "immigration-enforcement",
        "congress", "legislation", "immigration-policy", "supreme-court",
        "court-ruling", "doj", "chip-roy", "cbp", "social-media-vetting",
      ],
    },
    {
      key: "consular",
      label: "Visa Processing & Consular",
      tags: [
        "consulate", "consular-processing", "visa-stamping", "visa",
        "state-department", "citizenship", "eb5", "investor-visa",
      ],
    },
  ],
  technology: [
    {
      key: "ai",
      label: "Artificial Intelligence",
      tags: [
        "ai", "openai", "anthropic", "ai-agents", "ai-infrastructure",
        "enterprise-ai", "agentic-ai", "ai-policy", "chatgpt", "gpt",
        "machine-learning", "deep-learning", "generative-ai", "llm",
      ],
    },
    {
      key: "big-tech",
      label: "Big Tech",
      tags: [
        "google", "apple", "meta", "microsoft", "amazon", "nvidia",
        "tesla", "spacex", "netflix", "sundar-pichai", "satya-nadella",
        "jensen-huang", "tim-cook", "elon-musk", "mark-zuckerberg",
        "youtube", "instagram", "whatsapp",
      ],
    },
    {
      key: "semiconductors",
      label: "Semiconductors",
      tags: [
        "semiconductors", "semiconductor", "chips", "ai-chips",
        "intel", "amd", "qualcomm", "broadcom", "tsmc", "samsung",
        "micron", "sk-hynix", "sanjay-mehrotra", "memory-chips",
        "india-semiconductor", "make-in-india",
      ],
    },
    {
      key: "startups",
      label: "Startups & Unicorns",
      tags: [
        "indian-startups", "indian-startup", "startup", "startups",
        "ipo", "unicorn", "venture-capital", "fintech", "funding",
        "silicon-valley", "nri-investors", "y-combinator",
      ],
    },
    {
      key: "indian-it",
      label: "Indian IT & Services",
      tags: [
        "indian-it", "tcs", "infosys", "wipro", "hcltech",
        "tech-mahindra", "cognizant", "accenture", "it-services",
        "outsourcing", "gcc", "indian-engineers",
      ],
    },
  ],
};

/* ── SEO metadata per sub-topic ── */
export const SUB_TOPIC_SEO: Record<string, { title: string; description: string }> = {
  h1b: {
    title: "H-1B & Work Visa News for NRIs — The Videshi",
    description:
      "Latest H-1B visa news — fee changes, lottery updates, H-4 EAD, PERM processing, layoff impacts, and what it means for Indian workers in America.",
  },
  "green-card": {
    title: "Green Card & EB Category News — The Videshi",
    description:
      "Green card backlog updates, EB-2/EB-1A/NIW news, visa bulletin analysis, adjustment of status, and priority date movements for Indian immigrants.",
  },
  students: {
    title: "Student Visa & OPT News — The Videshi",
    description:
      "F-1 visa, OPT, STEM OPT news — policy changes, duration of status, Indian student trends, and what affects studying in the US.",
  },
  policy: {
    title: "Immigration Policy & Enforcement News — The Videshi",
    description:
      "USCIS policy updates, enforcement actions, congressional legislation, Supreme Court rulings, and immigration reform news affecting the Indian diaspora.",
  },
  consular: {
    title: "Visa Processing & Consular News — The Videshi",
    description:
      "Consular processing updates, visa stamping wait times, EB-5 investor visas, State Department policies, and embassy news for Indian applicants.",
  },
  ai: {
    title: "AI & Machine Learning News for NRIs — The Videshi",
    description:
      "Latest artificial intelligence, OpenAI, Anthropic, and machine learning news with diaspora impact — jobs, leadership, and what it means for Indians in tech.",
  },
  "big-tech": {
    title: "Big Tech News — Google, Apple, Meta, Microsoft, Nvidia — The Videshi",
    description:
      "Breaking news from Google, Apple, Meta, Microsoft, Amazon, Nvidia, Tesla, and SpaceX — company announcements, leadership, layoffs, and diaspora impact.",
  },
  semiconductors: {
    title: "Semiconductor & Chip Industry News for NRIs — The Videshi",
    description:
      "Semiconductor industry news — Intel, TSMC, Nvidia, Qualcomm, Micron, India's chip ambitions, and what it means for Indian engineers and investors.",
  },
  startups: {
    title: "Indian Startups, Unicorns & VC News — The Videshi",
    description:
      "Indian startup ecosystem news — unicorns, IPOs, venture capital, fintech, NRI founders in Silicon Valley, and funding rounds that matter.",
  },
  "indian-it": {
    title: "Indian IT & Services News — TCS, Infosys, Wipro, HCL — The Videshi",
    description:
      "Indian IT industry news — TCS, Infosys, Wipro, HCLTech, GCCs, outsourcing trends, hiring, and what it means for the diaspora workforce.",
  },
};

/* ── Lookup helpers ── */

export function getSubTopicDef(
  category: string,
  subtopicKey: string
): SubTopicDef | undefined {
  return CATEGORY_SUBTOPICS[category]?.find((s) => s.key === subtopicKey);
}

/* ── Helper: group articles by sub-topic ── */

function groupBySubTopic(
  articles: Article[],
  subtopics: SubTopicDef[]
): { def: SubTopicDef; articles: Article[] }[] {
  const used = new Set<string>();
  const groups: { def: SubTopicDef; articles: Article[] }[] = [];

  for (const def of subtopics) {
    const tagSet = new Set(def.tags);
    const matched = articles.filter((a) => {
      if (used.has(a.id)) return false;
      const articleTags = (a.tags ?? []).map((t: string) => t.toLowerCase());
      return articleTags.some((t: string) => tagSet.has(t));
    });
    matched.forEach((a) => used.add(a.id));
    if (matched.length > 0) {
      groups.push({ def, articles: matched });
    }
  }

  // "Other" bucket for unmatched articles
  const remaining = articles.filter((a) => !used.has(a.id));
  if (remaining.length > 0) {
    groups.push({
      def: { key: "other", label: "More Stories", tags: [] },
      articles: remaining,
    });
  }

  return groups;
}

/* ── Check if a category has sub-topics ── */
export function hasSubTopics(category: string): boolean {
  return category in CATEGORY_SUBTOPICS;
}

/* ── Sub-topic section component ── */

const INITIAL_COUNT = 4;
const ACCENT_COLORS: Record<string, string> = {
  h1b: "#D32F2F",
  "green-card": "#2E7D32",
  students: "#1565C0",
  policy: "#7B1FA2",
  consular: "#E65100",
  ai: "#7C3AED",
  "big-tech": "#1565C0",
  semiconductors: "#E65100",
  startups: "#2E7D32",
  "indian-it": "#4527A0",
  other: "#64748b",
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return "Just now";
  if (h < 24) return `${h}h ago`;
  return formatShortDate(iso);
}

function SubTopicGroup({
  def,
  articles,
  category,
}: {
  def: SubTopicDef;
  articles: Article[];
  category: string;
}) {
  const visible = articles.slice(0, INITIAL_COUNT);
  const hasMore = articles.length > INITIAL_COUNT;
  const accent = ACCENT_COLORS[def.key] || "#64748b";

  return (
    <section className="mb-10">
      <div className="container">
        {/* Section header */}
        <div
          className="flex items-center justify-between mb-4 pb-2"
          style={{ borderBottom: `3px solid ${accent}` }}
        >
          <h3
            className="text-[13px] font-bold tracking-[2px] uppercase"
            style={{ color: "#0B1D3A" }}
          >
            {def.label}
          </h3>
          <span className="text-[11px] text-muted-foreground">
            {articles.length} {articles.length === 1 ? "story" : "stories"}
          </span>
        </div>

        {/* Lead + compact list */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
          {/* Lead card */}
          {visible[0] && (
            <Link to={`/articles/${visible[0].slug}`} className="group block">
              {isValidImage(visible[0].hero_image_url) && (
                <div
                  className="w-full bg-stone-100 overflow-hidden rounded-lg mb-3"
                  style={{ aspectRatio: "16/10" }}
                >
                  <HeroImage
                    src={visible[0].hero_image_url}
                    alt={visible[0].title}
                    loading="lazy"
                    className="w-full h-full object-cover group-hover:scale-[1.01] transition-transform duration-500"
                    style={{ objectPosition: "center 25%" }}
                  />
                </div>
              )}
              <h4 className="font-serif text-[20px] font-extrabold leading-[1.25] mb-1.5 group-hover:text-primary transition-colors">
                {visible[0].title}
              </h4>
              {visible[0].excerpt && (
                <p className="text-sm text-muted-foreground leading-relaxed line-clamp-2 mb-1">
                  {visible[0].excerpt}
                </p>
              )}
              <p className="text-xs text-muted-foreground">
                {timeAgo(visible[0].published_at)}
              </p>
            </Link>
          )}

          {/* Compact list */}
          <div className="flex flex-col">
            {visible.slice(1).map((a) => (
              <Link
                key={a.id}
                to={`/articles/${a.slug}`}
                className="group flex gap-3 py-3 border-b last:border-b-0 hover:bg-stone-50 transition-colors rounded"
                style={{ borderColor: "hsl(var(--rule))" }}
              >
                {isValidImage(a.hero_image_url) && (
                  <div className="w-[68px] min-w-[68px] h-[68px] bg-stone-100 rounded overflow-hidden">
                    <HeroImage
                      src={a.hero_image_url}
                      alt={a.title}
                      loading="lazy"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <h4 className="font-serif text-[15px] font-bold leading-snug group-hover:text-primary transition-colors line-clamp-2">
                    {a.title}
                  </h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    {timeAgo(a.published_at)}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* View more → links to sub-topic page */}
        {hasMore && def.key !== "other" && (
          <div className="text-center mt-4">
            <Link
              to={`/${category}/${def.key}`}
              className="text-[13px] font-semibold tracking-wide uppercase hover:opacity-80 transition-opacity"
              style={{ color: accent, textDecoration: "none" }}
            >
              View all {def.label} ({articles.length}) →
            </Link>
          </div>
        )}
        {hasMore && def.key === "other" && (
          <div className="text-center mt-4">
            <Link
              to={`/${category}`}
              className="text-[13px] font-semibold tracking-wide uppercase hover:opacity-80 transition-opacity"
              style={{ color: accent, textDecoration: "none" }}
            >
              View all {category} →
            </Link>
          </div>
        )}
      </div>
    </section>
  );
}

/* ── Main export: renders all sub-topic groups for a category ── */

export default function CategorySubTopics({
  category,
  articles,
}: {
  category: string;
  articles: Article[];
}) {
  const subtopics = CATEGORY_SUBTOPICS[category];
  if (!subtopics) return null;

  const groups = groupBySubTopic(articles, subtopics);

  return (
    <>
      {groups.map((g) => (
        <SubTopicGroup
          key={g.def.key}
          def={g.def}
          articles={g.articles}
          category={category}
        />
      ))}
    </>
  );
}
