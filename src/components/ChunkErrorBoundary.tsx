import React from "react";

interface State {
  hasError: boolean;
}

/**
 * Catches lazy-load chunk failures (e.g. after a Vercel deploy invalidates
 * old hashes) and auto-reloads the page once. If it already retried,
 * shows a manual reload prompt.
 */
export default class ChunkErrorBoundary extends React.Component<
  { children: React.ReactNode },
  State
> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error) {
    const isChunkError =
      /loading chunk|failed to fetch dynamically imported module|importing a module script failed/i.test(
        error.message
      );

    if (isChunkError) {
      const key = "chunk_reload_ts";
      const last = Number(sessionStorage.getItem(key) || 0);
      // Auto-reload once per 30 seconds max to prevent loops
      if (Date.now() - last > 30_000) {
        sessionStorage.setItem(key, String(Date.now()));
        // Cache-busting navigation — reload() can re-serve stale chunks on mobile
        const url = new URL(window.location.href);
        url.searchParams.set("_cb", String(Date.now()));
        window.location.replace(url.toString());
        return;
      }
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", minHeight: "60vh", gap: 16, fontFamily: "var(--font-sans, sans-serif)" }}>
          <p style={{ color: "hsl(var(--muted-foreground))", fontSize: 15 }}>
            A newer version is available.
          </p>
          <button
            onClick={() => {
              // Cache-busting hard navigation
              const url = new URL(window.location.href);
              url.searchParams.set("_cb", String(Date.now()));
              window.location.replace(url.toString());
            }}
            style={{
              padding: "8px 20px",
              borderRadius: 8,
              border: "1px solid hsl(var(--border))",
              background: "hsl(var(--card))",
              cursor: "pointer",
              fontSize: 14,
              fontWeight: 600,
            }}
          >
            Reload page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
