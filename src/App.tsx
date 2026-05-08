import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Index from "./pages/Index.tsx";
import ArticlePage from "./pages/ArticlePage.tsx";
import CategoryPage from "./pages/CategoryPage.tsx";
import About from "./pages/About.tsx";
import Contact from "./pages/Contact.tsx";
import NotFound from "./pages/NotFound.tsx";
import Admin from "./pages/Admin.tsx";
import PipelineLayout from "./pages/pipeline/PipelineLayout.tsx";
import FeedSourcesPage from "./pages/pipeline/FeedSourcesPage.tsx";
import TopicRadarPage from "./pages/pipeline/TopicRadarPage.tsx";
import ReviewQueuePage from "./pages/pipeline/ReviewQueuePage.tsx";
import RunLogPage from "./pages/pipeline/RunLogPage.tsx";

const queryClient = new QueryClient();

const App = () => (
  <HelmetProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/articles/:slug" element={<ArticlePage />} />
            <Route path="/admin" element={<Admin />} />
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
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </HelmetProvider>
);

export default App;
