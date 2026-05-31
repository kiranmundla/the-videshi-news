import { useEffect, useRef, useCallback } from "react";

/* ------------------------------------------------------------------ */
/* TypeScript declarations for Cloudflare Turnstile                    */
/* ------------------------------------------------------------------ */
declare global {
  interface Window {
    turnstile?: {
      render: (
        container: string | HTMLElement,
        options: {
          sitekey: string;
          callback?: (token: string) => void;
          "expired-callback"?: () => void;
          "error-callback"?: () => void;
          theme?: "light" | "dark" | "auto";
          size?: "normal" | "compact";
        },
      ) => string;
      remove: (widgetId: string) => void;
      reset: (widgetId: string) => void;
    };
  }
}

const SITE_KEY = "0x4AAAAAADUi3naGpJmwvfDh";

interface TurnstileWidgetProps {
  onVerify: (token: string) => void;
  onExpire?: () => void;
  className?: string;
}

export default function TurnstileWidget({
  onVerify,
  onExpire,
  className,
}: TurnstileWidgetProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const widgetIdRef = useRef<string | null>(null);
  const onVerifyRef = useRef(onVerify);
  const onExpireRef = useRef(onExpire);

  onVerifyRef.current = onVerify;
  onExpireRef.current = onExpire;

  const renderWidget = useCallback(() => {
    if (!containerRef.current || !window.turnstile) return;
    /* remove previous widget if it exists */
    if (widgetIdRef.current !== null) {
      try {
        window.turnstile.remove(widgetIdRef.current);
      } catch {
        /* ignore */
      }
      widgetIdRef.current = null;
    }
    widgetIdRef.current = window.turnstile.render(containerRef.current, {
      sitekey: SITE_KEY,
      callback: (token: string) => onVerifyRef.current(token),
      "expired-callback": () => onExpireRef.current?.(),
      theme: "dark",
      size: "normal",
    });
  }, []);

  useEffect(() => {
    /* Dynamically load the Turnstile script if not already present */
    function ensureScript(): Promise<void> {
      if (window.turnstile) return Promise.resolve();
      if (document.querySelector('script[src*="challenges.cloudflare.com/turnstile"]')) {
        // Script tag exists but hasn't loaded yet — poll for it
        return new Promise((resolve) => {
          const iv = setInterval(() => {
            if (window.turnstile) { clearInterval(iv); resolve(); }
          }, 200);
        });
      }
      return new Promise((resolve) => {
        const script = document.createElement("script");
        script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js";
        script.async = true;
        script.onload = () => {
          const iv = setInterval(() => {
            if (window.turnstile) { clearInterval(iv); resolve(); }
          }, 100);
        };
        document.head.appendChild(script);
      });
    }

    let cancelled = false;
    ensureScript().then(() => {
      if (!cancelled) renderWidget();
    });

    return () => {
      cancelled = true;
      if (widgetIdRef.current !== null && window.turnstile) {
        try {
          window.turnstile.remove(widgetIdRef.current);
        } catch {
          /* ignore */
        }
      }
    };
  }, [renderWidget]);

  return <div ref={containerRef} className={className} />;
}
