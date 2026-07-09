import { useState } from "react";

export default function NewsletterCTA() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !email.includes("@")) return;
    setStatus("loading");
    try {
      const resp = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      });
      if (resp.ok) {
        setStatus("success");
        setEmail("");
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  };

  if (status === "success") {
    return (
      <section className="v2-newsletter">
        <div className="container text-center py-4">
          <p className="text-sm font-medium" style={{ color: "#2E7D32" }}>
            ✓ You're subscribed! Welcome to the diaspora.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="v2-newsletter">
      <div className="container">
        <div className="v2-newsletter-inner flex items-center justify-between gap-6 flex-wrap">
          <div>
            <h3
              className="font-serif text-lg font-bold mb-0.5"
              style={{ color: "#0B1D3A" }}
            >
              Get the Morning Videshi
            </h3>
            <p className="text-sm text-muted-foreground">
              India's diaspora news, curated daily. Free.
            </p>
          </div>
          <form
            onSubmit={handleSubmit}
            className="flex gap-2 flex-shrink-0"
          >
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              className="px-3.5 py-2 rounded-md border text-sm min-w-[200px] focus:outline-none focus:ring-2 focus:ring-primary/30"
              style={{ borderColor: "#D4A843", background: "#fff" }}
            />
            <button
              type="submit"
              disabled={status === "loading"}
              className="px-5 py-2 rounded-md text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
              style={{ background: "#A32D2D" }}
            >
              {status === "loading" ? "…" : "Subscribe"}
            </button>
          </form>
        </div>
        {status === "error" && (
          <p className="text-xs text-red-500 mt-2 text-center">
            Something went wrong. Please try again.
          </p>
        )}
      </div>
    </section>
  );
}
