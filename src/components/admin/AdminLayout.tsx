import { useState, useEffect, type ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, Newspaper, Car, Calendar, Tag, Building2,
  LogOut, ChevronLeft, Menu, X,
} from "lucide-react";
import { isAdminAuthenticated, adminLogin, adminLogout } from "@/lib/adminAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const NAV_ITEMS = [
  { to: "/admin", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/admin/articles", icon: Newspaper, label: "Articles" },
  { to: "/admin/cars", icon: Car, label: "Cars" },
  { to: "/admin/events", icon: Calendar, label: "Events" },
  { to: "/admin/classifieds", icon: Tag, label: "Classifieds" },
  { to: "/admin/directory", icon: Building2, label: "Directory" },
];

function LoginGate({ onLogin }: { onLogin: () => void }) {
  const [pw, setPw] = useState("");
  const [error, setError] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (adminLogin(pw)) {
      onLogin();
    } else {
      setError(true);
      setTimeout(() => setError(false), 2000);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4 p-8 border border-border rounded-xl bg-card">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold">The Videshi</h1>
          <p className="text-sm text-muted-foreground mt-1">Admin Panel</p>
        </div>
        <Input
          type="password"
          placeholder="Admin password"
          value={pw}
          onChange={(e) => setPw(e.target.value)}
          className={error ? "border-red-500" : ""}
          autoFocus
        />
        {error && <p className="text-red-500 text-sm">Invalid password</p>}
        <Button type="submit" className="w-full">Sign In</Button>
      </form>
    </div>
  );
}

export default function AdminLayout({ children }: { children: ReactNode }) {
  const [authed, setAuthed] = useState(isAdminAuthenticated());
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => { setSidebarOpen(false); }, [location.pathname]);

  if (!authed) return <LoginGate onLogin={() => setAuthed(true)} />;

  return (
    <div className="min-h-screen bg-background flex">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 bg-card border-r border-border flex flex-col
        transform transition-transform duration-200 lg:translate-x-0
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
      `}>
        <div className="p-4 border-b border-border flex items-center justify-between">
          <Link to="/admin" className="font-bold text-lg">📰 Videshi CMS</Link>
          <button className="lg:hidden" onClick={() => setSidebarOpen(false)}>
            <X className="h-5 w-5" />
          </button>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const active = item.to === "/admin"
              ? location.pathname === "/admin"
              : location.pathname.startsWith(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  active
                    ? "bg-primary/10 text-primary"
                    : "text-foreground/70 hover:bg-muted hover:text-foreground"
                }`}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-3 border-t border-border space-y-1">
          <Link
            to="/"
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-foreground/70 hover:bg-muted"
          >
            <ChevronLeft className="h-4 w-4" /> Back to Site
          </Link>
          <button
            onClick={() => { adminLogout(); setAuthed(false); navigate("/admin"); }}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-red-400 hover:bg-red-500/10"
          >
            <LogOut className="h-4 w-4" /> Sign Out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 border-b border-border flex items-center px-4 gap-3 bg-card/50 lg:hidden">
          <button onClick={() => setSidebarOpen(true)}>
            <Menu className="h-5 w-5" />
          </button>
          <span className="font-semibold text-sm">Videshi CMS</span>
        </header>
        <main className="flex-1 p-4 md:p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
