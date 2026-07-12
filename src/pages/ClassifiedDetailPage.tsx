import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import {
  Share2,
  Link as LinkIcon,
  Check,
  MapPin,
  Clock,
  ChevronLeft,
  Send,
  Loader2,
  MessageCircle,
} from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { supabase } from "@/integrations/supabase/client";
import {
  Classified,
  getClassifiedBySlug,
  CATEGORY_ICONS,
  CATEGORY_COLORS,
  timeAgo,
} from "@/lib/classifieds";
import TurnstileWidget from "@/components/TurnstileWidget";

/* ------------------------------------------------------------------ */
/* Category fallback images                                           */
/* ------------------------------------------------------------------ */
const CAT_FALLBACK_IMG: Record<string, string> = {
  Services: "/images/classifieds/services.jpg",
  Housing: "/images/classifieds/housing.jpg",
  "For Sale": "/images/classifieds/for-sale.jpg",
  "Jobs & Gigs": "/images/classifieds/jobs.jpg",
  Community: "/images/classifieds/community.jpg",
};

function categoryFallbackImg(category: string): string {
  return CAT_FALLBACK_IMG[category] || CAT_FALLBACK_IMG["Community"];
}

const sb = supabase as any;

/* ------------------------------------------------------------------ */
/* Share buttons                                                      */
/* ------------------------------------------------------------------ */
function ShareButtons({ title, url }: { title: string; url: string }) {
  const [copied, setCopied] = useState(false);

  const shareWhatsApp = () =>
    window.open(
      `https://api.whatsapp.com/send?text=${encodeURIComponent(title + " — " + url)}`,
      "_blank",
    );

  const shareTwitter = () =>
    window.open(
      `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`,
      "_blank",
    );

  const copyLink = async () => {
    await navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={shareWhatsApp}
        className="p-2 rounded-lg border border-border hover:bg-muted/50 transition-colors"
        title="Share on WhatsApp"
      >
        <span className="text-lg">💬</span>
      </button>
      <button
        onClick={shareTwitter}
        className="p-2 rounded-lg border border-border hover:bg-muted/50 transition-colors"
        title="Share on X"
      >
        <span className="text-lg">𝕏</span>
      </button>
      <button
        onClick={copyLink}
        className="p-2 rounded-lg border border-border hover:bg-muted/50 transition-colors"
        title="Copy link"
      >
        {copied ? (
          <Check className="h-4 w-4 text-green-500" />
        ) : (
          <LinkIcon className="h-4 w-4" />
        )}
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Inquiry Form                                                       */
/* ------------------------------------------------------------------ */
function InquiryForm({ classified }: { classified: Classified }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [step, setStep] = useState<"form" | "verify" | "sending" | "done">("form");
  const [otpCode, setOtpCode] = useState("");
  const [otpSending, setOtpSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !message.trim()) {
      setError("Please fill in all fields");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("Please enter a valid email");
      return;
    }
    if (!turnstileToken) {
      setError("Please complete the bot verification.");
      return;
    }

    setOtpSending(true);
    setError(null);

    /* Server-side Turnstile verification */
    try {
      const tRes = await fetch("/api/verify-turnstile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: turnstileToken }),
      });
      const tData = await tRes.json();
      if (!tData.success) {
        setError("Bot verification failed. Please try again.");
        setTurnstileToken(null);
        setOtpSending(false);
        return;
      }
    } catch {
      setError("Bot verification failed. Please try again.");
      setTurnstileToken(null);
      setOtpSending(false);
      return;
    }

    /* Send OTP to the inquiry sender's email */
    try {
      const { data, error: fnErr } = await sb.functions.invoke(
        "send-inquiry-otp",
        { body: { email: email.trim().toLowerCase() } },
      );
      if (fnErr) throw new Error(data?.error || fnErr.message || "Failed to send code");
      if (data && !data.ok) throw new Error(data.error || "Failed to send code");
      setStep("verify");
    } catch (err: any) {
      setError(err.message || "Failed to send verification code. Please try again.");
    } finally {
      setOtpSending(false);
    }
  };

  const handleVerifyAndSend = async () => {
    if (!otpCode || otpCode.length !== 6) {
      setError("Please enter the 6-digit code");
      return;
    }
    setStep("sending");
    setError(null);

    /* Verify OTP */
    try {
      const { data: vData, error: vErr } = await sb.functions.invoke(
        "verify-inquiry-otp",
        { body: { email: email.trim().toLowerCase(), code: otpCode.trim() } },
      );
      if (vErr) throw new Error(vData?.error || vErr.message || "Verification failed");
      if (vData && !vData.success) throw new Error(vData.error || "Invalid or expired code");
    } catch (err: any) {
      setError(err.message || "Invalid or expired code. Please try again.");
      setStep("verify");
      return;
    }

    /* Send the actual inquiry */
    try {
      const { data, error: fnErr } = await sb.functions.invoke(
        "send-classified-inquiry",
        {
          body: {
            classified_id: classified.id,
            sender_name: name.trim(),
            sender_email: email.trim(),
            message: message.trim(),
          },
        },
      );
      if (fnErr) throw new Error(data?.error || fnErr.message || "Failed to send");
      if (data && !data.ok) throw new Error(data.error || "Failed to send");
      setStep("done");
    } catch (err: any) {
      setError(err.message || "Something went wrong. Please try again.");
      setStep("verify");
    }
  };

  if (step === "done") {
    return (
      <div className="border border-green-500/30 rounded-lg p-5 bg-green-500/5 space-y-2">
        <div className="flex items-center gap-2">
          <Check className="h-5 w-5 text-green-500" />
          <h2 className="font-semibold text-lg text-green-500">Inquiry Sent!</h2>
        </div>
        <p className="text-sm text-foreground/60">
          The poster will receive your message and can reply directly to your email.
          Your contact info is only shared with the poster.
        </p>
      </div>
    );
  }

  if (!open) {
    return (
      <div className="border border-border rounded-lg p-5 bg-card space-y-3">
        <h2 className="font-semibold text-lg">Interested?</h2>
        <p className="text-sm text-foreground/50">
          Send the poster a message — your email will only be shared with them so they can reply.
        </p>
        <button
          onClick={() => setOpen(true)}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-amber-600 text-white font-medium hover:bg-amber-700 transition-colors"
        >
          <MessageCircle className="h-4 w-4" />
          Send Inquiry
        </button>
      </div>
    );
  }

  const inputClass =
    "w-full px-3 py-2.5 rounded-lg border border-border bg-card text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/40";

  /* ---- OTP Verification Step ---- */
  if (step === "verify" || step === "sending") {
    return (
      <div className="border border-amber-500/30 rounded-lg p-5 bg-amber-500/5 space-y-4">
        <h2 className="font-semibold text-lg flex items-center gap-2">
          <MessageCircle className="h-5 w-5 text-amber-600" />
          Verify Your Email
        </h2>
        <p className="text-sm text-foreground/50">
          We sent a 6-digit code to <strong className="text-foreground/80">{email}</strong>.
          Enter it below to send your inquiry.
        </p>

        <div>
          <label className="block text-sm font-medium mb-1">
            Verification Code <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            inputMode="numeric"
            maxLength={6}
            value={otpCode}
            onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
            placeholder="000000"
            className={inputClass + " text-center text-2xl tracking-[0.3em] font-mono"}
            autoFocus
          />
        </div>

        {error && (
          <p className="text-sm text-red-400">{error}</p>
        )}

        <div className="flex gap-3">
          <button
            onClick={handleVerifyAndSend}
            disabled={step === "sending" || otpCode.length !== 6}
            className="flex-1 inline-flex items-center justify-center gap-2 py-3 rounded-lg bg-amber-600 text-white font-medium hover:bg-amber-700 transition-colors disabled:opacity-50"
          >
            {step === "sending" ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Verifying & Sending…
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                Verify & Send Inquiry
              </>
            )}
          </button>
          <button
            type="button"
            onClick={() => { setStep("form"); setOtpCode(""); setError(null); }}
            className="px-4 py-3 rounded-lg border border-border font-medium hover:bg-muted/30 transition-colors text-sm"
          >
            Back
          </button>
        </div>

        <p className="text-xs text-foreground/40">
          Didn't receive the code? Check your spam folder or{" "}
          <button
            type="button"
            onClick={() => { setStep("form"); setOtpCode(""); setError(null); }}
            className="underline hover:text-foreground/60"
          >
            go back
          </button>{" "}
          to resend.
        </p>
      </div>
    );
  }

  /* ---- Main Form Step ---- */
  return (
    <div className="border border-amber-500/30 rounded-lg p-5 bg-amber-500/5 space-y-4">
      <h2 className="font-semibold text-lg flex items-center gap-2">
        <MessageCircle className="h-5 w-5 text-amber-600" />
        Send Inquiry
      </h2>
      <p className="text-sm text-foreground/50">
        Your message will be sent to the poster. They'll get your name and email
        so they can reply — their contact info stays private.
      </p>

      <form onSubmit={handleSendOtp} className="space-y-3">
        <div>
          <label className="block text-sm font-medium mb-1">
            Your Name <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Full name"
            className={inputClass}
            maxLength={100}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Your Email <span className="text-red-400">*</span>
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className={inputClass}
          />
          <p className="text-xs text-foreground/40 mt-1">
            We'll send a verification code to this email before your inquiry goes through.
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Message <span className="text-red-400">*</span>
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Hi, I'm interested in this listing..."
            rows={4}
            className={inputClass + " resize-y"}
            maxLength={2000}
          />
        </div>

        {error && (
          <p className="text-sm text-red-400">{error}</p>
        )}

        <TurnstileWidget
          onVerify={(token) => setTurnstileToken(token)}
          onExpire={() => setTurnstileToken(null)}
          className="mb-2"
        />

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={otpSending || !turnstileToken}
            className="flex-1 inline-flex items-center justify-center gap-2 py-3 rounded-lg bg-amber-600 text-white font-medium hover:bg-amber-700 transition-colors disabled:opacity-50"
          >
            {otpSending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Sending Code…
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                Verify Email & Send
              </>
            )}
          </button>
          <button
            type="button"
            onClick={() => setOpen(false)}
            className="px-4 py-3 rounded-lg border border-border font-medium hover:bg-muted/30 transition-colors text-sm"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main page                                                          */
/* ------------------------------------------------------------------ */
export default function ClassifiedDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [item, setItem] = useState<Classified | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    getClassifiedBySlug(slug).then((data) => {
      setItem(data);
      setLoading(false);
    });
  }, [slug]);

  if (loading) {
    return (
      <>
        <Masthead />
        <CategoryPills />
        <main className="container py-8">
          <div className="max-w-3xl mx-auto space-y-4 animate-pulse">
            <div className="h-6 w-48 bg-muted/30 rounded" />
            <div className="h-48 bg-muted/20 rounded-lg" />
            <div className="h-4 w-full bg-muted/20 rounded" />
            <div className="h-4 w-3/4 bg-muted/20 rounded" />
          </div>
        </main>
        <SiteFooter />
      </>
    );
  }

  if (!item) {
    return (
      <>
        <Helmet>
          <title>Classified Not Found — The Videshi</title>
        </Helmet>
        <Masthead />
        <CategoryPills />
        <main className="container py-16 text-center space-y-4">
          <p className="text-5xl">📋</p>
          <h1 className="text-2xl font-bold">Listing Not Found</h1>
          <p className="text-foreground/50">
            This classified may have expired or been removed.
          </p>
          <Link
            to="/classifieds"
            className="inline-flex items-center gap-1 text-primary hover:underline"
          >
            <ChevronLeft className="h-4 w-4" /> Browse all classifieds
          </Link>
        </main>
        <SiteFooter />
      </>
    );
  }

  const photos = item.photos?.length ? item.photos : [];
  const heroImage = item.image_url || (photos.length > 0 ? photos[0] : null);
  const galleryPhotos = photos.filter((p) => p !== heroImage);
  const catEmoji = CATEGORY_ICONS[item.category] || "📌";
  const catColor =
    CATEGORY_COLORS[item.category] || "bg-muted text-muted-foreground";
  const pageUrl = `https://www.thevideshi.com/classifieds/${item.slug}`;
  const locationStr = [item.city, item.state].filter(Boolean).join(", ");

  /* JSON-LD */
  const jsonLd: any = {
    "@context": "https://schema.org",
    "@type":
      item.category === "For Sale"
        ? "Product"
        : item.category === "Services"
          ? "Service"
          : item.category === "Jobs & Gigs"
            ? "JobPosting"
            : "Offer",
    name: item.title,
    description: item.description || item.title,
    url: pageUrl,
  };
  if (heroImage) jsonLd.image = heroImage;
  if (item.price && item.category === "For Sale") {
    jsonLd.offers = {
      "@type": "Offer",
      price: item.price,
      priceCurrency: "USD",
      offerCount: 1,
    };
  }
  if (item.category === "Jobs & Gigs") {
    jsonLd.datePosted = item.created_at;
    if (locationStr) {
      jsonLd.jobLocation = {
        "@type": "Place",
        address: locationStr,
      };
    }
  }

  return (
    <>
      <Helmet>
        <title>{item.title} — Classifieds | The Videshi</title>
        <meta
          name="description"
          content={
            item.description?.slice(0, 160) ||
            `${item.category} listing in ${locationStr}`
          }
        />
        <meta property="og:title" content={item.title} />
        <meta
          property="og:description"
          content={
            item.description?.slice(0, 160) ||
            `${item.category} listing on The Videshi`
          }
        />
        {heroImage && <meta property="og:image" content={heroImage} />}
        <meta property="og:type" content="website" />
        <meta property="og:url" content={pageUrl} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={item.title} />
        <meta
          name="twitter:description"
          content={
            item.description?.slice(0, 160) ||
            `${item.category} listing on The Videshi`
          }
        />
        {heroImage && <meta name="twitter:image" content={heroImage} />}
        <script type="application/ld+json">
          {JSON.stringify(jsonLd)}
        </script>
        <link rel="canonical" href={`https://www.thevideshi.com/classifieds/${slug}`} />
      </Helmet>      <Masthead />
      <CategoryPills />

      <main className="container py-6">
        <div className="max-w-3xl mx-auto space-y-5">
          {/* Back link */}
          <Link
            to="/classifieds"
            className="inline-flex items-center gap-1 text-sm text-foreground/50 hover:text-primary"
          >
            <ChevronLeft className="h-4 w-4" /> Back to classifieds
          </Link>

          {/* Header card — colored category bar + title + price */}
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            {/* Category color bar */}
            <div className={`px-5 py-3 flex flex-wrap items-center gap-2 ${catColor.replace('text-', 'border-l-4 border-l-').split(' ')[0]} bg-muted/30`}>
              <span className={`text-sm font-medium px-3 py-1 rounded-full ${catColor}`}>
                {catEmoji} {item.category}
              </span>
              {item.subcategory && (
                <span className="text-sm px-2.5 py-0.5 rounded-full bg-blue-600/20 text-blue-300 font-medium">
                  {item.subcategory}
                </span>
              )}
              {item.price && (
                <span className="text-sm font-bold px-3 py-1 rounded-md bg-amber-600/20 text-amber-500 ml-auto">
                  {item.price}
                </span>
              )}
            </div>

            {/* Title + Meta */}
            <div className="px-5 py-4 space-y-3">
              <h1 className="text-xl sm:text-2xl font-bold font-serif leading-tight">
                {item.title}
              </h1>

              <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                {locationStr && (
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3.5 w-3.5" />
                    {locationStr}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  Posted {timeAgo(item.created_at)}
                </span>
                {item.expires_at && (
                  <span className="text-muted-foreground/50">
                    Expires{" "}
                    {new Date(item.expires_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    })}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Hero image or category fallback */}
          <div className="relative w-full overflow-hidden rounded-lg">
            <img
              src={heroImage || categoryFallbackImg(item.category)}
              alt={item.title}
              className={heroImage ? "w-full h-full object-contain bg-black" : "w-full h-48 sm:h-56 object-cover opacity-60"}
              style={heroImage ? { maxHeight: "75vh" } : undefined}
            />
            {!heroImage && (
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-5xl">{catEmoji}</span>
              </div>
            )}
          </div>

          {/* Photo gallery */}
          {galleryPhotos.length > 0 && (
            <div className="flex gap-3 overflow-x-auto scrollbar-none -mx-1 px-1 pb-2">
              {galleryPhotos.map((url, i) => (
                <div
                  key={i}
                  className="flex-shrink-0 snap-start w-[85%] sm:w-[45%] lg:w-[30%] rounded-lg overflow-hidden"
                >
                  <img
                    src={url}
                    alt={`${item.title} — photo ${i + 2}`}
                    className="w-full h-44 sm:h-52 object-contain bg-white/5"
                    loading="lazy"
                  />
                </div>
              ))}
            </div>
          )}

          {/* Description card */}
          {item.description && (
            <div className="bg-card border border-border rounded-lg p-5">
              <h2 className="font-semibold text-base mb-3 flex items-center gap-2">
                <span className="text-lg">📋</span> Details
              </h2>
              <p className="whitespace-pre-wrap text-foreground/80 leading-relaxed text-sm">
                {item.description}
              </p>
            </div>
          )}

          {/* Location card */}
          {locationStr && (
            <div className="bg-card border border-border rounded-lg p-5 space-y-3">
              <h2 className="font-semibold text-base flex items-center gap-2">
                <MapPin className="h-4 w-4 text-primary" /> Location
              </h2>
              <p className="text-foreground/70 text-sm">
                {[item.city, item.state, item.zip].filter(Boolean).join(", ")}
              </p>
              <a
                href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(locationStr)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-sm text-primary hover:underline"
              >
                <MapPin className="h-3.5 w-3.5" />
                Get Directions
              </a>
            </div>
          )}

          {/* Inquiry form */}
          <InquiryForm classified={item} />

          {/* Share */}
          <div className="flex items-center justify-between border-t border-border pt-4">
            <ShareButtons title={item.title} url={pageUrl} />
          </div>
        </div>
      </main>

      <SiteFooter />
    </>
  );

}
