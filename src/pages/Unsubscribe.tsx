import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CheckCircle2, MailX, Loader2 } from "lucide-react";

/**
 * /unsubscribe?email=..&token=..
 *
 * Confirm page for newsletter unsubscribes. GET never mutates state —
 * the actual unsubscribe happens via POST to /api/unsubscribe, which
 * verifies the HMAC token server-side. This keeps mailbox link scanners
 * (which prefetch URLs) from unsubscribing people.
 */
const UnsubscribePage = () => {
  const [searchParams] = useSearchParams();
  const email = searchParams.get("email") || "";
  const token = searchParams.get("token") || "";

  const [status, setStatus] = useState<"idle" | "working" | "done" | "error" | "invalid">(
    email && token ? "idle" : "invalid"
  );

  const confirm = async () => {
    setStatus("working");
    try {
      const resp = await fetch("/api/unsubscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, token }),
      });
      const data = await resp.json().catch(() => ({}));
      if (resp.ok && data.success) {
        setStatus("done");
      } else if (resp.status === 400) {
        setStatus("invalid");
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  };

  return (
    <div className="flex min-h-[70vh] items-center justify-center bg-muted px-4 py-16">
      <div className="w-full max-w-md rounded-xl bg-card p-8 text-center shadow-sm">
        {status === "invalid" && (
          <>
            <MailX className="mx-auto mb-4 h-10 w-10 text-muted-foreground" />
            <h1 className="mb-2 text-2xl font-bold">Invalid unsubscribe link</h1>
            <p className="mb-6 text-muted-foreground">
              This link isn't valid — it may be incomplete or tampered with.
              Please use the unsubscribe link from your newsletter email.
            </p>
            <Link to="/" className="text-primary underline hover:text-primary/90">
              Return to Home
            </Link>
          </>
        )}

        {status === "idle" && (
          <>
            <MailX className="mx-auto mb-4 h-10 w-10 text-primary" />
            <h1 className="mb-2 text-2xl font-bold">Unsubscribe?</h1>
            <p className="mb-6 text-muted-foreground">
              You'll stop receiving The Videshi newsletter at{" "}
              <span className="font-medium text-foreground">{email}</span>.
            </p>
            <button
              onClick={confirm}
              className="w-full rounded-lg bg-primary px-4 py-3 font-semibold text-primary-foreground transition hover:bg-primary/90"
            >
              Yes, unsubscribe me
            </button>
            <Link
              to="/"
              className="mt-4 inline-block text-sm text-muted-foreground underline hover:text-foreground"
            >
              Keep me subscribed
            </Link>
          </>
        )}

        {status === "working" && (
          <>
            <Loader2 className="mx-auto mb-4 h-10 w-10 animate-spin text-primary" />
            <p className="text-muted-foreground">Unsubscribing…</p>
          </>
        )}

        {status === "done" && (
          <>
            <CheckCircle2 className="mx-auto mb-4 h-10 w-10 text-green-600" />
            <h1 className="mb-2 text-2xl font-bold">You're unsubscribed</h1>
            <p className="mb-6 text-muted-foreground">
              You won't receive The Videshi newsletter anymore. Sorry to see you
              go — you're welcome back anytime.
            </p>
            <Link to="/" className="text-primary underline hover:text-primary/90">
              Return to Home
            </Link>
          </>
        )}

        {status === "error" && (
          <>
            <MailX className="mx-auto mb-4 h-10 w-10 text-destructive" />
            <h1 className="mb-2 text-2xl font-bold">Something went wrong</h1>
            <p className="mb-6 text-muted-foreground">
              We couldn't process your unsubscribe. Please try the link in your
              email again, or reply to any newsletter and we'll take care of it.
            </p>
            <button
              onClick={() => setStatus("idle")}
              className="text-primary underline hover:text-primary/90"
            >
              Try again
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default UnsubscribePage;
