import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Analytics } from "@vercel/analytics/react";
import React, { Suspense } from "react";

// ── Keep Index (homepage) eagerly loaded for fastest first paint ──
import Index from "./pages/Index.tsx";
import NotFound from "./pages/NotFound.tsx";

// ── Loading fallback ──────────────────────────────────────────────
const PageLoader = () => (
  <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "60vh" }}>
    <div style={{ width: 32, height: 32, border: "3px solid #b8860b", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
    <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
  </div>
);

// ── Lazy-loaded pages (separate chunks, loaded on-demand) ─────────
const ArticlePage = React.lazy(() => import("./pages/ArticlePage.tsx"));
const CategoryPage = React.lazy(() => import("./pages/CategoryPage.tsx"));
const About = React.lazy(() => import("./pages/About.tsx"));
const Contact = React.lazy(() => import("./pages/Contact.tsx"));
const SearchPage = React.lazy(() => import("./pages/SearchPage.tsx"));
const Privacy = React.lazy(() => import("./pages/Privacy.tsx"));
const Terms = React.lazy(() => import("./pages/Terms.tsx"));
const TravelDestination = React.lazy(() => import("./pages/TravelDestination.tsx"));

// Events
const EventsPage = React.lazy(() => import("./pages/EventsPage.tsx"));
const EventDetailPage = React.lazy(() => import("./pages/EventDetailPage.tsx"));
const SubmitEventPage = React.lazy(() => import("./pages/SubmitEventPage.tsx"));
const EditEventPage = React.lazy(() => import("./pages/EditEventPage.tsx"));

// Directory
const DirectoryPage = React.lazy(() => import("./pages/DirectoryPage.tsx"));
const DirectoryDetailPage = React.lazy(() => import("./pages/DirectoryDetailPage.tsx"));
const SubmitListingPage = React.lazy(() => import("./pages/SubmitListingPage.tsx"));

// Classifieds
const ClassifiedsPage = React.lazy(() => import("./pages/ClassifiedsPage.tsx"));
const ClassifiedDetailPage = React.lazy(() => import("./pages/ClassifiedDetailPage.tsx"));
const SubmitClassifiedPage = React.lazy(() => import("./pages/SubmitClassifiedPage.tsx"));
const EditClassifiedPage = React.lazy(() => import("./pages/EditClassifiedPage.tsx"));

// Cars
const CarsPage = React.lazy(() => import("./pages/CarsPage.tsx"));
const CarDetailPage = React.lazy(() => import("./pages/CarDetailPage.tsx"));
const CarComparePage = React.lazy(() => import("./pages/CarComparePage.tsx"));
const LeaseDealsPage = React.lazy(() => import("./pages/LeaseDealsPage.tsx"));
const CarGuides = React.lazy(() => import("./pages/CarGuides.tsx"));

// Admin (rarely visited — always lazy)
const Admin = React.lazy(() => import("./pages/Admin.tsx"));
const AdminDashboard = React.lazy(() => import("./pages/admin/AdminDashboard.tsx"));
const AdminArticles = React.lazy(() => import("./pages/admin/AdminArticles.tsx"));
const AdminCars = React.lazy(() => import("./pages/admin/AdminCars.tsx"));
const AdminEvents = React.lazy(() => import("./pages/admin/AdminEvents.tsx"));
const AdminClassifieds = React.lazy(() => import("./pages/admin/AdminClassifieds.tsx"));
const AdminDirectory = React.lazy(() => import("./pages/admin/AdminDirectory.tsx"));
const SourcesPage = React.lazy(() => import("./pages/admin/SourcesPage.tsx"));
const PipelineLayout = React.lazy(() => import("./pages/pipeline/PipelineLayout.tsx"));
const FeedSourcesPage = React.lazy(() => import("./pages/pipeline/FeedSourcesPage.tsx"));
const TopicRadarPage = React.lazy(() => import("./pages/pipeline/TopicRadarPage.tsx"));
const ReviewQueuePage = React.lazy(() => import("./pages/pipeline/ReviewQueuePage.tsx"));
const RunLogPage = React.lazy(() => import("./pages/pipeline/RunLogPage.tsx"));

// ── Car guide wrapper (lazy-loaded as single chunk, renders correct guide) ──
const FirstCarGuide = React.lazy(() => import("./pages/CarGuides.tsx").then(m => ({ default: m.FirstCarGuide })));
const LeaseVsBuyGuide = React.lazy(() => import("./pages/CarGuides.tsx").then(m => ({ default: m.LeaseVsBuyGuide })));
const InsuranceGuide = React.lazy(() => import("./pages/CarGuides.tsx").then(m => ({ default: m.InsuranceGuide })));
const BestFamilySuvsGuide = React.lazy(() => import("./pages/CarGuides.tsx").then(m => ({ default: m.BestFamilySuvsGuide })));
const CarsUnder30KGuide = React.lazy(() => import("./pages/CarGuides.tsx").then(m => ({ default: m.CarsUnder30KGuide })));
const BestEVsGuide = React.lazy(() => import("./pages/CarGuides.tsx").then(m => ({ default: m.BestEVsGuide })));
const IndiaVsUSDrivingGuide = React.lazy(() => import("./pages/CarGuides.tsx").then(m => ({ default: m.IndiaVsUSDrivingGuide })));
const TechProfessionalsGuide = React.lazy(() => import("./pages/CarGuides.tsx").then(m => ({ default: m.TechProfessionalsGuide })));

const queryClient = new QueryClient();

const App = () => (
  <HelmetProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/about" element={<About />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/privacy" element={<Privacy />} />
              <Route path="/terms" element={<Terms />} />
              <Route path="/articles/:slug" element={<ArticlePage />} />
              <Route path="/travel/:destination" element={<TravelDestination />} />
              <Route path="/events" element={<EventsPage />} />
              <Route path="/events/submit" element={<SubmitEventPage />} />
              <Route path="/events/:slug/edit" element={<EditEventPage />} />
              <Route path="/events/:slug" element={<EventDetailPage />} />
              <Route path="/directory" element={<DirectoryPage />} />
              <Route path="/directory/submit" element={<SubmitListingPage />} />
              <Route path="/directory/:slug" element={<DirectoryDetailPage />} />
              <Route path="/classifieds" element={<ClassifiedsPage />} />
              <Route path="/classifieds/submit" element={<SubmitClassifiedPage />} />
              <Route path="/classifieds/:slug/edit" element={<EditClassifiedPage />} />
              <Route path="/classifieds/:slug" element={<ClassifiedDetailPage />} />
              <Route path="/cars" element={<CarsPage />} />
              <Route path="/cars/deals" element={<LeaseDealsPage />} />
              <Route path="/cars/compare" element={<CarComparePage />} />
              <Route path="/cars/guide/first-car-in-america" element={<FirstCarGuide />} />
              <Route path="/cars/guide/lease-vs-buy" element={<LeaseVsBuyGuide />} />
              <Route path="/cars/guide/insurance-for-new-immigrants" element={<InsuranceGuide />} />
              <Route path="/cars/guide/best-family-suvs" element={<BestFamilySuvsGuide />} />
              <Route path="/cars/guide/best-cars-under-30k" element={<CarsUnder30KGuide />} />
              <Route path="/cars/guide/best-evs-2026" element={<BestEVsGuide />} />
              <Route path="/cars/guide/india-vs-us-driving" element={<IndiaVsUSDrivingGuide />} />
              <Route path="/cars/guide/cars-for-tech-professionals" element={<TechProfessionalsGuide />} />
              <Route path="/cars/:slug" element={<CarDetailPage />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/admin/articles" element={<AdminArticles />} />
              <Route path="/admin/cars" element={<AdminCars />} />
              <Route path="/admin/events" element={<AdminEvents />} />
              <Route path="/admin/classifieds" element={<AdminClassifieds />} />
              <Route path="/admin/directory" element={<AdminDirectory />} />
              <Route path="/admin/featured" element={<Admin />} />
              <Route path="/admin/sources" element={<SourcesPage />} />
              <Route path="/admin/p2" element={<PipelineLayout />}>
                <Route index element={<FeedSourcesPage />} />
                <Route path="feeds" element={<FeedSourcesPage />} />
                <Route path="topics" element={<TopicRadarPage />} />
                <Route path="review" element={<ReviewQueuePage />} />
                <Route path="run" element={<RunLogPage />} />
              </Route>
              <Route path="/:category" element={<CategoryPage />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
        <Analytics />
      </TooltipProvider>
    </QueryClientProvider>
  </HelmetProvider>
);

export default App;
