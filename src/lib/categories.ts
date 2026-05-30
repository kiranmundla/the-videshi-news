export type CategoryDef = {
  slug: string;
  label: string;
  path: string;
  hasPipeline: boolean;
};

export const CATEGORIES: CategoryDef[] = [
  { slug: "news", label: "News", path: "/news", hasPipeline: true },
  { slug: "nri-world", label: "Indians Abroad", path: "/nri-world", hasPipeline: true },
  { slug: "lifestyle-health", label: "Lifestyle & Health", path: "/lifestyle-health", hasPipeline: true },
  { slug: "markets-finance", label: "Markets & Finance", path: "/markets-finance", hasPipeline: true },
  { slug: "technology", label: "Technology", path: "/technology", hasPipeline: true },
  { slug: "sports", label: "Sports", path: "/sports", hasPipeline: true },
  { slug: "entertainment", label: "Entertainment", path: "/entertainment", hasPipeline: true },
  { slug: "food", label: "Food", path: "/food", hasPipeline: true },
  { slug: "immigration", label: "Immigration", path: "/immigration", hasPipeline: false },
  { slug: "travel", label: "Travel", path: "/travel", hasPipeline: false },
  { slug: "cars", label: "Cars", path: "/cars", hasPipeline: false },
  { slug: "events", label: "Events", path: "/events", hasPipeline: false },
  { slug: "directory", label: "Directory", path: "/directory", hasPipeline: false },
  { slug: "classifieds", label: "Classifieds", path: "/classifieds", hasPipeline: false },
  { slug: "stories", label: "Voices", path: "/stories", hasPipeline: false },

];

export function getCategoryBySlug(slug: string) {
  return CATEGORIES.find((c) => c.slug === slug);
}
