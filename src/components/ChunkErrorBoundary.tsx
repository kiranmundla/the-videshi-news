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
      const count = Number(sessionStorage.getItem(key + "_n") || 0);
      const last = Number(sessionStorage.getItem(key) || 0);
      const elapsed = Date.now() - last;

      // Auto-reload up to 3 times with increasing delay, then show prompt
      if (count < 3 && elapsed > 5_000) {
        sessionStorage.setItem(key, String(Date.now()));
        sessionStorage.setItem(key + "_n", String(count + 1));
        // Cache-busting navigation — reload() can re-serve stale chunks on mobile
        const url = new URL(window.location.href);
        url.searchParams.set("_cb", String(Date.now()));
        window.location.replace(url.toString());
        return;
      }
      // Reset counter after 2 minutes so future errors can auto-reload again
      if (elapsed > 120_000) {
        sessionStorage.setItem(key + "_n", "0");
      }
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", minHeight: "60vh", gap: 16, fontFamily: "var(--font-sans, sans-serif)" }}>
          <p style={{ color: "hsl(var(--muted-foreground))", fontSize: 15 }}>
            Something went wrong loading this page.
          </p>
          <button
            onClick={() => {
              // Reset retry counter and hard reload
              sessionStorage.setItem("chunk_reload_ts_n", "0");
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
