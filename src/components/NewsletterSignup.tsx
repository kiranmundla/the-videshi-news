import { useState } from "react";

export default function NewsletterSignup({ variant = "footer" }: { variant?: "footer" | "inline" }) {
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
      <div className={variant === "footer" ? "" : "my-8 text-center"}>
        <p className="text-sm text-green-600 dark:text-green-400 font-medium">
          ✓ You're subscribed! We'll keep you posted.
        </p>
      </div>
    );
  }

  if (variant === "inline") {
    return (
      <div className="my-10 py-8 px-6 border rounded-lg bg-foreground/[0.02] text-center max-w-2xl mx-auto">
        <h3 className="font-serif text-lg font-bold mb-1">Stay informed</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Get the latest diaspora news delivered to your inbox.
        </p>
        <form onSubmit={handleSubmit} className="flex gap-2 max-w-md mx-auto">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
            className="flex-1 px-3 py-2 rounded-md border border-foreground/20 bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
          />
          <button
            type="submit"
            disabled={status === "loading"}
            className="px-4 py-2 rounded-md bg-foreground text-background text-sm font-medium hover:bg-foreground/90 transition-colors disabled:opacity-50"
          >
            {status === "loading" ? "…" : "Subscribe"}
          </button>
        </form>
        {status === "error" && (
          <p className="text-xs text-red-500 mt-2">Something went wrong. Try again.</p>
        )}
      </div>
    );
  }

  // Footer variant
  return (
    <div>
      <p className="font-medium text-sm mb-2">Newsletter</p>
      <p className="text-xs text-muted-foreground mb-3">
        Diaspora news, delivered weekly.
      </p>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          required
          className="flex-1 min-w-0 px-3 py-1.5 rounded-md border border-foreground/20 bg-background text-xs focus:outline-none focus:ring-2 focus:ring-primary/40"
        />
        <button
          type="submit"
          disabled={status === "loading"}
          className="px-3 py-1.5 rounded-md bg-foreground text-background text-xs font-medium hover:bg-foreground/90 transition-colors disabled:opacity-50 whitespace-nowrap"
        >
          {status === "loading" ? "…" : "Subscribe"}
        </button>
      </form>
      {status === "error" && (
        <p className="text-xs text-red-500 mt-1">Something went wrong.</p>
      )}
    </div>
  );
}
