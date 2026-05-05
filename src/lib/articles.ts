// Mock article data — schema mirrors the future Supabase `articles` table.
// Swap `getArticles()` / `getArticleBySlug()` to Supabase queries when Cloud is enabled.

export type Article = {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  body: string; // markdown
  category: string;
  hero_image_url: string;
  author: string;
  published_at: string; // ISO
  status: "published" | "draft";
  sources?: { label: string; url?: string }[];
};

const IMG = (q: string) =>
  `https://images.unsplash.com/${q}?auto=format&fit=crop&w=1600&q=70`;

const BODY_LONG = `
The streets of Edison, New Jersey tell a story that statistics alone cannot. Walk down Oak Tree Road on a Saturday afternoon and you will hear Gujarati, Tamil, Hindi, Punjabi — sometimes in a single conversation. Sweet shops display jalebis next to American flags. The diaspora, once defined by distance, is now defined by density.

## A generational shift

For the first wave of Indian immigrants who arrived after the 1965 Immigration Act, success was measured in degrees and assimilation. Their children — now in their thirties and forties — are rewriting the terms.

> "We don't have to choose anymore," says Priya Subramanian, a documentary filmmaker based in Brooklyn. "We can be fully American and fully Indian, sometimes in the same hour."

The numbers back her up. Indian-Americans are now the highest-earning ethnic group in the United States, with a median household income that exceeds $130,000. They lead Fortune 500 companies, run for Senate, and increasingly, shape the cultural conversation.

## Reverse migration, real questions

But prosperity has surfaced new tensions. A growing number of NRIs are returning to India — drawn by family, by Bengaluru's tech boom, by a sense that the country they left is not the country it is now. Others are leaving India for the first time, watching the rupee, the politics, and their own ambitions.

The diaspora is no longer one story. It is many, told in many accents, and we intend to listen carefully.
`;

const articles: Article[] = [
  {
    id: "1",
    slug: "edison-diaspora-density",
    title: "On Oak Tree Road, the diaspora has stopped explaining itself",
    excerpt:
      "Inside the New Jersey corridor where a generation of Indian-Americans is rewriting the rules of belonging — without asking permission.",
    body: BODY_LONG,
    category: "NRI Affairs",
    hero_image_url: IMG("photo-1524492412937-b28074a5d7da"),
    author: "Anjali Mehta",
    published_at: "2026-05-04T08:00:00Z",
    status: "published",
    sources: [
      { label: "Pew Research Center, 2024 Indian-American Survey" },
      { label: "U.S. Census Bureau, ACS 2023" },
    ],
  },
  {
    id: "2",
    slug: "rupee-tech-bengaluru-return",
    title: "Why Bengaluru is winning the talent it once lost",
    excerpt:
      "A quiet reverse migration is reshaping India's tech capital — and the salary expectations of an entire generation.",
    body: BODY_LONG,
    category: "Business",
    hero_image_url: IMG("photo-1596496050755-c923e73e42e1"),
    author: "Rohan Iyer",
    published_at: "2026-05-04T06:30:00Z",
    status: "published",
  },
  {
    id: "3",
    slug: "us-india-trade-2026",
    title: "The new architecture of US–India trade, explained",
    excerpt:
      "Tariffs, semiconductors, and a strategic embrace that both governments insist is not about China.",
    body: BODY_LONG,
    category: "US-India",
    hero_image_url: IMG("photo-1526778548025-fa2f459cd5c1"),
    author: "Vikram Shah",
    published_at: "2026-05-03T18:00:00Z",
    status: "published",
  },
  {
    id: "4",
    slug: "rupee-volatility-may",
    title: "The rupee's quiet month, and what it signals",
    excerpt:
      "After a turbulent spring, currency markets are pricing in a steadier RBI — for now.",
    body: BODY_LONG,
    category: "Money & Markets",
    hero_image_url: IMG("photo-1611974789855-9c2a0a7236a3"),
    author: "Neha Kapoor",
    published_at: "2026-05-03T12:00:00Z",
    status: "published",
  },
  {
    id: "5",
    slug: "sensex-record-close",
    title: "Sensex closes at a record as IT and banking diverge",
    excerpt:
      "A split-screen rally exposes how unevenly India's growth story is being priced.",
    body: BODY_LONG,
    category: "Money & Markets",
    hero_image_url: IMG("photo-1590283603385-17ffb3a7f29f"),
    author: "Aman Verma",
    published_at: "2026-05-03T10:00:00Z",
    status: "published",
  },
  {
    id: "6",
    slug: "tamil-cinema-global-stage",
    title: "Tamil cinema steps onto a global stage, on its own terms",
    excerpt:
      "The industry once dismissed as regional is now setting the template for what Indian film exports look like.",
    body: BODY_LONG,
    category: "Culture",
    hero_image_url: IMG("photo-1489599849927-2ee91cede3ba"),
    author: "Lakshmi Raman",
    published_at: "2026-05-02T20:00:00Z",
    status: "published",
  },
  {
    id: "7",
    slug: "diwali-london-mainstream",
    title: "How Diwali went mainstream in London — and what it cost",
    excerpt:
      "A festival's commercial embrace has divided a community that spent decades fighting to be seen.",
    body: BODY_LONG,
    category: "Culture",
    hero_image_url: IMG("photo-1604608672516-f1b9b1d1e1f1"),
    author: "Sana Qureshi",
    published_at: "2026-05-02T15:00:00Z",
    status: "published",
  },
  {
    id: "8",
    slug: "kerala-monsoon-shift",
    title: "Kerala's monsoon is arriving differently. Farmers are adapting first.",
    excerpt:
      "Climate scientists are catching up to what coastal villages have already learned to plan around.",
    body: BODY_LONG,
    category: "India",
    hero_image_url: IMG("photo-1469474968028-56623f02e42e"),
    author: "Arjun Pillai",
    published_at: "2026-05-02T09:00:00Z",
    status: "published",
  },
  {
    id: "9",
    slug: "long-read-second-generation",
    title:
      "The second generation grew up translating. Now they are writing the original.",
    excerpt:
      "A long read on the writers, founders, and lawmakers redefining what Indian-American means in 2026 — and the parents quietly trying to keep up.",
    body: BODY_LONG,
    category: "Voices",
    hero_image_url: IMG("photo-1531206715517-5c0ba140b2b8"),
    author: "Meera Krishnan",
    published_at: "2026-05-01T07:00:00Z",
    status: "published",
  },
  {
    id: "10",
    slug: "cricket-ipl-diaspora",
    title: "The IPL's diaspora viewership is now its fastest-growing market",
    excerpt:
      "Streaming numbers from North America are reshaping how the league sells itself.",
    body: BODY_LONG,
    category: "Sports",
    hero_image_url: IMG("photo-1531415074968-036ba1b575da"),
    author: "Karan Joshi",
    published_at: "2026-04-30T22:00:00Z",
    status: "published",
  },
  {
    id: "11",
    slug: "h1b-policy-shift",
    title: "An H-1B policy shift few are talking about — yet",
    excerpt:
      "A USCIS rule change scheduled for July could reset hiring math for thousands of Indian engineers.",
    body: BODY_LONG,
    category: "NRI Affairs",
    hero_image_url: IMG("photo-1454165804606-c3d57bc86b40"),
    author: "Devika Nair",
    published_at: "2026-04-30T16:00:00Z",
    status: "published",
  },
];

export function readingTime(markdown: string) {
  const words = markdown.trim().split(/\s+/).length;
  return Math.max(1, Math.round(words / 225));
}

export function formatLongDate(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  }).replace(",", " ·");
}

export function formatShortDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export async function getArticles(): Promise<Article[]> {
  return [...articles]
    .filter((a) => a.status === "published")
    .sort((a, b) => +new Date(b.published_at) - +new Date(a.published_at));
}

export async function getArticleBySlug(slug: string): Promise<Article | undefined> {
  return articles.find((a) => a.slug === slug && a.status === "published");
}

export async function getRelated(category: string, excludeSlug: string, limit = 3) {
  const all = await getArticles();
  return all.filter((a) => a.category === category && a.slug !== excludeSlug).slice(0, limit);
}
