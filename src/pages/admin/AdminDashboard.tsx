import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { Newspaper, Car, Calendar, Tag, Building2, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { supabase } from "@/integrations/supabase/client";
import AdminLayout from "@/components/admin/AdminLayout";

const sb = supabase as any;

type Counts = {
  articles: number;
  cars: number;
  events: number;
  classifieds: number;
  directory: number;
};

export default function AdminDashboard() {
  const [counts, setCounts] = useState<Counts>({ articles: 0, cars: 0, events: 0, classifieds: 0, directory: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [a, c, e, cl, d] = await Promise.all([
        sb.from("p2_articles").select("id", { count: "exact", head: true }),
        sb.from("cars").select("id", { count: "exact", head: true }),
        sb.from("events").select("id", { count: "exact", head: true }),
        sb.from("classifieds").select("id", { count: "exact", head: true }),
        sb.from("directory_listings").select("id", { count: "exact", head: true }),
      ]);
      setCounts({
        articles: a.count ?? 0,
        cars: c.count ?? 0,
        events: e.count ?? 0,
        classifieds: cl.count ?? 0,
        directory: d.count ?? 0,
      });
      setLoading(false);
    }
    load();
  }, []);

  const cards = [
    { label: "Articles", count: counts.articles, icon: Newspaper, to: "/admin/articles", color: "text-blue-400" },
    { label: "Cars", count: counts.cars, icon: Car, to: "/admin/cars", color: "text-amber-400" },
    { label: "Events", count: counts.events, icon: Calendar, to: "/admin/events", color: "text-purple-400" },
    { label: "Classifieds", count: counts.classifieds, icon: Tag, to: "/admin/classifieds", color: "text-green-400" },
    { label: "Directory", count: counts.directory, icon: Building2, to: "/admin/directory", color: "text-pink-400" },
  ];

  return (
    <AdminLayout>
      <Helmet><title>Admin Dashboard · The Videshi</title></Helmet>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Manage all content on The Videshi</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => (
            <Card key={i} className="animate-pulse"><CardContent className="p-6 h-24" /></Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {cards.map((c) => (
            <Link key={c.to} to={c.to}>
              <Card className="hover:border-primary/40 transition-colors cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">{c.label}</CardTitle>
                  <c.icon className={`h-5 w-5 ${c.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{c.count.toLocaleString()}</div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-muted-foreground" /> Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link to="/admin/articles" className="block text-sm text-primary hover:underline">→ Manage articles & images</Link>
            <Link to="/admin/cars" className="block text-sm text-primary hover:underline">→ Update car images & specs</Link>
            <Link to="/admin/events" className="block text-sm text-primary hover:underline">→ Feature/remove events</Link>
            <Link to="/admin/classifieds" className="block text-sm text-primary hover:underline">→ Review & moderate classifieds</Link>
            <Link to="/admin/directory" className="block text-sm text-primary hover:underline">→ Edit directory listings</Link>
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
}
