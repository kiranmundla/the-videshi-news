import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Radio, Target, PenSquare, Settings } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Badge } from "@/components/ui/badge";
import { supabase } from "@/integrations/supabase/client";
import { Link } from "react-router-dom";

const items = [
  { title: "Feed Sources", url: "/pipeline/feeds", icon: Radio },
  { title: "Topic Radar", url: "/pipeline/topics", icon: Target },
  { title: "Review Queue", url: "/pipeline/review", icon: PenSquare, badgeKey: "review" },
  { title: "Run Log", url: "/pipeline/run", icon: Settings },
];

export default function PipelineLayout() {
  const { pathname } = useLocation();
  const { data: reviewCount = 0 } = useQuery({
    queryKey: ["pipeline-review-count"],
    queryFn: async () => {
      const { count } = await supabase
        .from("p2_articles")
        .select("*", { count: "exact", head: true })
        .eq("status", "review");
      return count ?? 0;
    },
    refetchInterval: 30000,
  });

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <Sidebar collapsible="icon">
          <SidebarContent>
            <div className="p-4 border-b border-border">
              <Link to="/" className="font-serif text-lg font-bold">The Videshi</Link>
              <p className="text-xs text-muted-foreground">Pipeline Admin</p>
            </div>
            <SidebarGroup>
              <SidebarGroupLabel>Pipeline</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {items.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton asChild isActive={pathname === item.url}>
                        <NavLink to={item.url} className="flex items-center gap-2">
                          <item.icon className="h-4 w-4" />
                          <span className="flex-1">{item.title}</span>
                          {item.badgeKey === "review" && reviewCount > 0 && (
                            <Badge variant="destructive" className="ml-auto h-5 px-1.5 text-[10px]">
                              {reviewCount}
                            </Badge>
                          )}
                        </NavLink>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
        </Sidebar>
        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-12 flex items-center border-b border-border px-3 gap-2">
            <SidebarTrigger />
            <span className="text-sm text-muted-foreground">News Pipeline</span>
          </header>
          <main className="flex-1 p-6 overflow-auto">
            <Outlet />
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
