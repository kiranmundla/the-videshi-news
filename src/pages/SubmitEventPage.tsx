import { useState, useRef, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { supabase } from "@/integrations/supabase/client";
import { generateSlug, formatEventDateLong } from "@/lib/events";
import TurnstileWidget from "@/components/TurnstileWidget";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_ADDITIONAL = 5;

const US_STATES = [
  "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
  "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
  "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
  "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
  "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC",
];

const STATE_NAMES: Record<string, string> = {
  AL:"Alabama",AK:"Alaska",AZ:"Arizona",AR:"Arkansas",CA:"California",
  CO:"Colorado",CT:"Connecticut",DE:"Delaware",FL:"Florida",GA:"Georgia",
  HI:"Hawaii",ID:"Idaho",IL:"Illinois",IN:"Indiana",IA:"Iowa",
  KS:"Kansas",KY:"Kentucky",LA:"Louisiana",ME:"Maine",MD:"Maryland",
  MA:"Massachusetts",MI:"Michigan",MN:"Minnesota",MS:"Mississippi",MO:"Missouri",
  MT:"Montana",NE:"Nebraska",NV:"Nevada",NH:"New Hampshire",NJ:"New Jersey",
  NM:"New Mexico",NY:"New York",NC:"North Carolina",ND:"North Dakota",OH:"Ohio",
  OK:"Oklahoma",OR:"Oregon",PA:"Pennsylvania",RI:"Rhode Island",SC:"South Carolina",
  SD:"South Dakota",TN:"Tennessee",TX:"Texas",UT:"Utah",VT:"Vermont",
  VA:"Virginia",WA:"Washington",WV:"West Virginia",WI:"Wisconsin",WY:"Wyoming",
  DC:"District of Columbia",
};

const CATEGORIES = [
  "Entertainment",
  "Community",
  "Sports",
  "Religious",
  "Education",
  "Competition",
  "Other",
];

const CAT_EMOJI: Record<string, string> = {
  Cultural: "🎭", Music: "🎵", Food: "🍛", Sports: "🏏",
  Community: "🤝", Festival: "🪔", Comedy: "😂", Dance: "💃",
  Religious: "🙏", Education: "🎓", Competition: "🏆", Entertainment: "🎶",
  Other: "📌",
};

type FormData = {
  title: string;
  date: string;
  end_date: string;
  time: string;
  city: string;
  state: string;
  venue_name: string;
  category: string;
  ticket_url: string;
  description: string;
  email: string;
};

const INITIAL: FormData = {
  title: "",
  date: "",
  end_date: "",
  time: "",
  city: "",
  state: "",
  venue_name: "",
  category: "",
  ticket_url: "",
  description: "",
  email: "",
};

/* Synthesized content from AI */
type SynthesizedContent = {
  long_description: string | null;
  artist_info: string | null;
  venue_info: string | null;
};

/* ------------------------------------------------------------------ */
/* Image preview type                                                 */
/* ------------------------------------------------------------------ */
type ImagePreview = {
  id: string;
  file: File;
  url: string;
};

function createPreview(file: File): ImagePreview {
  return { id: crypto.randomUUID(), file, url: URL.createObjectURL(file) };
}

function validateImageFile(file: File): string | null {
  if (!ACCEPTED_TYPES.includes(file.type)) return "Only JPG, PNG, or WebP images are accepted.";
  if (file.size > MAX_FILE_SIZE) return `File "${file.name}" exceeds 5 MB.`;
  return null;
}

/* ------------------------------------------------------------------ */
/* Main component                                                     */
/* ------------------------------------------------------------------ */
export default function SubmitEventPage() {
  const [form, setForm] = useState<FormData>(INITIAL);
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});

  /* Step: "form" | "synthesizing" | "preview" | "verify-email" | "verify-code" | "publishing" | "done" */
  const [step, setStep] = useState<"form" | "synthesizing" | "preview" | "verify-email" | "verify-code" | "publishing" | "done">("form");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [publishedSlug, setPublishedSlug] = useState<string | null>(null);

  /* Turnstile bot protection */
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);

  /* Email verification state */
  const [verifyCode, setVerifyCode] = useState("");
  const [verifySending, setVerifySending] = useState(false);
  const [verifyChecking, setVerifyChecking] = useState(false);
  const [verifyError, setVerifyError] = useState<string | null>(null);

  /* Synthesized content */
  const [synthesized, setSynthesized] = useState<SynthesizedContent | null>(null);

  /* Image state */
  const [coverImage, setCoverImage] = useState<ImagePreview | null>(null);
  const [additionalImages, setAdditionalImages] = useState<ImagePreview[]>([]);
  const [imageError, setImageError] = useState<string | null>(null);
  const coverInputRef = useRef<HTMLInputElement>(null);
  const additionalInputRef = useRef<HTMLInputElement>(null);

  const set = (field: keyof FormData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setForm((f) => ({ ...f, [field]: e.target.value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  /* ---- Email verification: send code (called from Publish button) ---- */
  const handleSendVerifyCode = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const email = form.email.trim().toLowerCase();
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setVerifyError("Please enter a valid email address");
      return;
    }
    setVerifySending(true);
    setVerifyError(null);
    try {
      const { data, error } = await supabase.functions.invoke("send-email-verify", {
        body: { email },
      });
      if (error) throw new Error((data as any)?.error || error.message || "Failed to send code");
      if (data && !data.ok) throw new Error(data.error || "Failed to send code");
      setStep("verify-code");
    } catch (err: any) {
      setVerifyError(err.message || "Something went wrong");
    } finally {
      setVerifySending(false);
    }
  };

  /* ---- Email verification: check code then publish ---- */
  const handleCheckVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    const email = form.email.trim().toLowerCase();
    const code = verifyCode.trim();
    if (!code || code.length !== 6) {
      setVerifyError("Please enter the 6-digit code");
      return;
    }
    setVerifyChecking(true);
    setVerifyError(null);
    try {
      const { data, error } = await supabase.functions.invoke("verify-email-code", {
        body: { email, code },
      });
      if (error) throw new Error((data as any)?.error || error.message || "Verification failed");
      if (data && !data.verified) throw new Error(data.error || "Invalid code");
      /* Verified — now actually publish */
      await doPublish();
    } catch (err: any) {
      setVerifyError(err.message || "Invalid or expired code");
    } finally {
      setVerifyChecking(false);
    }
  };

  /* ---- Cover image handlers ---- */
  const handleCoverSelect = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return;
    setImageError(null);
    const file = files[0];
    const err = validateImageFile(file);
    if (err) { setImageError(err); return; }
    if (coverImage) URL.revokeObjectURL(coverImage.url);
    setCoverImage(createPreview(file));
  }, [coverImage]);

  const removeCover = useCallback(() => {
    if (coverImage) URL.revokeObjectURL(coverImage.url);
    setCoverImage(null);
    if (coverInputRef.current) coverInputRef.current.value = "";
  }, [coverImage]);

  /* ---- Additional images handlers ---- */
  const handleAdditionalSelect = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return;
    setImageError(null);
    const remaining = MAX_ADDITIONAL - additionalImages.length;
    if (remaining <= 0) {
      setImageError(`Maximum ${MAX_ADDITIONAL} additional images allowed.`);
      return;
    }
    const toAdd: ImagePreview[] = [];
    for (let i = 0; i < Math.min(files.length, remaining); i++) {
      const err = validateImageFile(files[i]);
      if (err) { setImageError(err); return; }
      toAdd.push(createPreview(files[i]));
    }
    if (files.length > remaining) {
      setImageError(`Only ${remaining} more image${remaining === 1 ? "" : "s"} can be added.`);
    }
    setAdditionalImages((prev) => [...prev, ...toAdd]);
    if (additionalInputRef.current) additionalInputRef.current.value = "";
  }, [additionalImages.length]);

  const removeAdditional = useCallback((id: string) => {
    setAdditionalImages((prev) => {
      const img = prev.find((p) => p.id === id);
      if (img) URL.revokeObjectURL(img.url);
      return prev.filter((p) => p.id !== id);
    });
  }, []);

  /* ---- Drag-and-drop helpers ---- */
  const [coverDragging, setCoverDragging] = useState(false);
  const [additionalDragging, setAdditionalDragging] = useState(false);

  const dragHandlers = (
    setDrag: (v: boolean) => void,
    onFiles: (files: FileList | null) => void,
  ) => ({
    onDragOver: (e: React.DragEvent) => { e.preventDefault(); setDrag(true); },
    onDragEnter: (e: React.DragEvent) => { e.preventDefault(); setDrag(true); },
    onDragLeave: () => setDrag(false),
    onDrop: (e: React.DragEvent) => { e.preventDefault(); setDrag(false); onFiles(e.dataTransfer.files); },
  });

  /* ---- Upload helper ---- */
  async function uploadImage(file: File, slug: string, prefix: string): Promise<string | null> {
    const ext = file.name.split(".").pop() || "jpg";
    const safeName = `${prefix}-${Date.now()}.${ext}`;
    const path = `events/${slug}/${safeName}`;

    const sb = supabase as any;
    const { error } = await sb.storage.from("article-images").upload(path, file, {
      contentType: file.type,
      cacheControl: "31536000",
      upsert: false,
    });
    if (error) {
      console.error("Image upload error:", error);
      return null;
    }
    const { data } = sb.storage.from("article-images").getPublicUrl(path);
    return data?.publicUrl ?? null;
  }

  /* ---- Validation ---- */
  const validate = (): boolean => {
    const errs: Partial<Record<keyof FormData, string>> = {};
    if (!form.title.trim()) errs.title = "Event name is required";
    if (!form.date) errs.date = "Date is required";
    if (!form.city.trim()) errs.city = "City is required";
    if (!form.state) errs.state = "State is required";
    if (!form.venue_name.trim()) errs.venue_name = "Venue is required";
    if (!form.category) errs.category = "Category is required";
    if (!form.email.trim()) {
      errs.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
      errs.email = "Please enter a valid email";
    }
    if (form.ticket_url && !/^https?:\/\/.+/.test(form.ticket_url.trim())) {
      errs.ticket_url = "Please enter a valid URL starting with http";
    }
    if (form.end_date && form.end_date < form.date) {
      errs.end_date = "End date must be on or after start date";
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  /* ---- Step 1: Preview (synthesize) ---- */
  const handlePreview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    /* Verify Turnstile token */
    if (!turnstileToken) {
      setSubmitError("Please complete the bot verification.");
      return;
    }
    try {
      const tRes = await fetch("/api/verify-turnstile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: turnstileToken }),
      });
      const tData = await tRes.json();
      if (!tData.success) {
        setSubmitError("Bot verification failed. Please try again.");
        setTurnstileToken(null);
        return;
      }
    } catch {
      setSubmitError("Bot verification failed. Please try again.");
      setTurnstileToken(null);
      return;
    }

    setStep("synthesizing");
    setSubmitError(null);

    try {
      const { data, error } = await supabase.functions.invoke("synthesize-event", {
        body: {
          title: form.title.trim(),
          date: form.date,
          end_date: form.end_date || null,
          time: form.time || null,
          city: form.city.trim(),
          state: form.state,
          venue_name: form.venue_name.trim(),
          category: form.category,
          description: form.description.trim(),
          ticket_url: form.ticket_url.trim() || null,
        },
      });

      if (error) throw error;

      setSynthesized({
        long_description: data?.long_description || form.description.trim() || null,
        artist_info: data?.artist_info || null,
        venue_info: data?.venue_info || null,
      });
      setStep("preview");
    } catch (err: any) {
      console.error("Synthesize error:", err);
      /* Graceful fallback — show preview with original content */
      setSynthesized({
        long_description: form.description.trim() || null,
        artist_info: null,
        venue_info: null,
      });
      setStep("preview");
    }
  };

  /* ---- Step 2: Publish button triggers email verification ---- */
  const handlePublish = async () => {
    setVerifyError(null);
    setVerifyCode("");
    setStep("verify-email");
    /* Send verification code to the email they entered */
    handleSendVerifyCode();
  };

  /* ---- Step 3: Actual publish (after email verified) ---- */
  const doPublish = async () => {
    setStep("publishing");
    setSubmitError(null);

    const slug = generateSlug(form.title.trim(), form.date);

    /* Upload images */
    let imageUrl: string | null = null;
    let venueImages: string[] = [];
    let imageNote = "";

    if (coverImage) {
      imageUrl = await uploadImage(coverImage.file, slug, "cover");
      if (!imageUrl) imageNote = "Cover image upload failed — we'll add it manually. ";
    }
    if (additionalImages.length > 0) {
      const results = await Promise.all(
        additionalImages.map((img, i) => uploadImage(img.file, slug, `photo-${i + 1}`))
      );
      venueImages = results.filter((u): u is string => u !== null);
      const failed = results.length - venueImages.length;
      if (failed > 0) imageNote += `${failed} additional image${failed > 1 ? "s" : ""} failed to upload.`;
    }

    const row: Record<string, unknown> = {
      title: form.title.trim(),
      date: form.date,
      end_date: form.end_date || null,
      time: form.time || null,
      city: form.city.trim(),
      state: form.state,
      venue_name: form.venue_name.trim(),
      category: form.category,
      ticket_url: form.ticket_url.trim() || null,
      description: form.description.trim() || null,
      long_description: synthesized?.long_description || null,
      artist_info: synthesized?.artist_info || null,
      venue_info: synthesized?.venue_info || null,
      source: "user_submitted",
      organizer: form.email.trim(),
      slug,
    };
    if (imageUrl) row.image_url = imageUrl;
    if (venueImages.length > 0) row.venue_images = venueImages;

    const sbRaw = supabase as unknown as { from: (t: string) => any };
    const { error } = await sbRaw.from("events").insert([row]);

    if (error) {
      console.error("Submit event error:", error);
      setSubmitError("Something went wrong. Please try again.");
      setStep("preview");
      return;
    }

    setPublishedSlug(slug);

    /* Send confirmation email (fire-and-forget — don't block on failure) */
    try {
      await supabase.functions.invoke("send-event-confirmation", {
        body: {
          title: form.title.trim(),
          slug,
          email: form.email.trim(),
          date: form.date,
          venue: form.venue_name.trim(),
          city: `${form.city.trim()}, ${form.state}`,
        },
      });
    } catch (emailErr) {
      console.error("Confirmation email failed:", emailErr);
      /* Non-blocking — event is already created */
    }

    setStep("done");
    if (imageNote) setSubmitError(imageNote);
  };

  /* ================================================================ */
  /* RENDER: Done (published)                                         */
  /* ================================================================ */
  if (step === "done") {
    const fullUrl = publishedSlug ? `thevideshi.com/events/${publishedSlug}` : "";
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 pt-8 md:pt-10 pb-16 max-w-2xl mx-auto">
          <div className="text-center py-20">
            <p className="text-5xl mb-4">🎉</p>
            <h2 className="font-serif text-2xl md:text-3xl text-foreground mb-3">
              Your Event Is Live!
            </h2>
            <p className="text-muted-foreground text-lg mb-3">
              We've sent a confirmation email with your event link.
            </p>
            <p className="text-muted-foreground text-sm mb-6">
              You can edit it anytime using the link in the email.
            </p>

            {/* Copyable event URL */}
            {publishedSlug && (
              <div className="flex items-center justify-center gap-2 mb-8 max-w-md mx-auto">
                <div className="flex-1 bg-muted/60 border border-border rounded-lg px-4 py-2.5 text-sm text-foreground/80 font-mono truncate text-left">
                  {fullUrl}
                </div>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(`https://${fullUrl}`);
                    const btn = document.getElementById("copy-url-btn");
                    if (btn) { btn.textContent = "Copied!"; setTimeout(() => { btn.textContent = "Copy"; }, 2000); }
                  }}
                  id="copy-url-btn"
                  className="px-4 py-2.5 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors whitespace-nowrap"
                >
                  Copy
                </button>
              </div>
            )}

            {submitError && (
              <p className="text-sm text-amber-600 mb-6">{submitError}</p>
            )}
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              {publishedSlug && (
                <Link
                  to={`/events/${publishedSlug}`}
                  className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
                >
                  View Your Event →
                </Link>
              )}
              <Link
                to="/events"
                className="px-6 py-3 border border-border rounded-lg font-medium hover:bg-muted/40 transition-colors"
              >
                Browse Events
              </Link>
            </div>
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  /* ================================================================ */
  /* RENDER: Preview                                                  */
  /* ================================================================ */
  if (step === "preview" || step === "verify-email" || step === "verify-code" || step === "publishing") {
    const dateStr = formatEventDateLong(form.date, form.end_date || undefined);
    const catEmoji = CAT_EMOJI[form.category || "Other"] || "📌";
    const description = synthesized?.long_description || form.description;

    return (
      <div className="min-h-screen flex flex-col">
        <Helmet>
          <title>Preview Your Event — The Videshi</title>
          <meta name="robots" content="noindex" />
        </Helmet>

        <Masthead />
        <CategoryPills />

        <main className="container flex-1 pt-8 md:pt-10 pb-16 max-w-4xl mx-auto px-4">
          <div className="mb-6">
            <p className="text-sm text-primary font-medium mb-2 flex items-center gap-2">
              <span className="inline-block w-6 h-6 rounded-full bg-primary/10 text-center text-xs leading-6 font-bold">2</span>
              Preview your event
            </p>
            <h1 className="font-serif text-2xl md:text-3xl text-foreground mb-1">
              Here's how your event will look
            </h1>
            <p className="text-muted-foreground text-sm">
              Review the details below. Our AI has enhanced your description to make it shine.
            </p>
          </div>

          {/* ---- Preview Card (dark, matching EventDetailPage) ---- */}
          <div className="rounded-2xl overflow-hidden bg-[#0a0a0a] text-white mb-8">

            {/* Hero image */}
            {coverImage ? (
              <div className="relative w-full max-h-[50vh] overflow-hidden">
                <img
                  src={coverImage.url}
                  alt={form.title}
                  className="w-full h-full object-contain bg-black"
                  style={{ maxHeight: "50vh" }}
                />
                <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-[#0a0a0a] to-transparent" />
              </div>
            ) : (
              <div className="relative w-full h-36 sm:h-44 bg-gradient-to-br from-white/5 to-transparent flex items-center justify-center">
                <span className="text-[6rem] opacity-15 select-none">{catEmoji}</span>
              </div>
            )}

            {/* Content */}
            <div className="px-6 sm:px-8 pb-8 -mt-4 relative z-10">
              {/* Category + Date */}
              <div className="flex flex-wrap items-center gap-3 mb-4">
                {form.category && (
                  <span className="text-sm font-medium text-white/40 uppercase tracking-widest">
                    {catEmoji} {form.category}
                  </span>
                )}
                <span className="text-sm text-white/30">•</span>
                <span className="text-sm text-white/60">{dateStr}</span>
                {form.time && (
                  <>
                    <span className="text-sm text-white/30">•</span>
                    <span className="text-sm text-white/60">{form.time}</span>
                  </>
                )}
              </div>

              {/* Title */}
              <h2 className="font-serif text-2xl sm:text-3xl md:text-4xl font-bold leading-[1.1] mb-4">
                {form.title}
              </h2>

              {/* Venue + City */}
              <div className="flex flex-wrap items-center gap-2 text-white/50 text-base mb-6">
                <span className="text-white/70 font-medium">{form.venue_name}</span>
                <span>·</span>
                <span>{form.city}, {form.state}</span>
              </div>

              {/* Ticket CTA */}
              {form.ticket_url && (
                <div className="mb-8">
                  <span className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white text-black font-bold text-sm">
                    Get Tickets
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" />
                    </svg>
                  </span>
                </div>
              )}

              {/* Divider */}
              <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent my-8" />

              {/* Description */}
              {description && (
                <section className="mb-8">
                  <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-white/30 mb-4">
                    About This Event
                  </h3>
                  <div className="text-white/70 text-[15px] leading-[1.85] whitespace-pre-line">
                    {description}
                  </div>
                </section>
              )}

              {/* Artist Info */}
              {synthesized?.artist_info && (
                <section className="mb-8">
                  <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-white/30 mb-4">
                    About the Artist
                  </h3>
                  <div className="text-white/70 text-[15px] leading-[1.85] whitespace-pre-line">
                    {synthesized.artist_info}
                  </div>
                </section>
              )}

              {/* Venue */}
              <section>
                <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-white/30 mb-4">
                  Venue
                </h3>
                <div className="rounded-xl bg-white/[0.03] border border-white/[0.06] p-5">
                  <p className="text-white font-semibold text-lg mb-1">{form.venue_name}</p>
                  <p className="text-white/40 text-sm mb-3">{form.city}, {form.state}</p>
                  {synthesized?.venue_info && (
                    <p className="text-white/60 text-sm leading-relaxed">{synthesized.venue_info}</p>
                  )}
                </div>
              </section>

              {/* Additional images */}
              {additionalImages.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-white/30 mb-4">
                    Photos
                  </h3>
                  <div className="flex gap-3 overflow-x-auto pb-3 scrollbar-none">
                    {additionalImages.map((img, i) => (
                      <div key={img.id} className="flex-shrink-0 w-[45%] sm:w-[30%] rounded-lg overflow-hidden">
                        <img
                          src={img.url}
                          alt={`Photo ${i + 1}`}
                          className="w-full h-44 object-cover"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* ---- Action buttons ---- */}
          {submitError && (
            <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm mb-4">
              {submitError}
            </div>
          )}

          {/* ---- Email Verification (shown after clicking Publish) ---- */}
          {(step === "verify-email" || step === "verify-code") && (
            <div className="bg-muted/30 border border-border rounded-xl p-6 mb-4">
              <div className="flex items-center gap-3 mb-2">
                <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-primary/10 text-primary text-xs font-bold">✉</span>
                <h2 className="font-serif text-lg text-foreground">Verify Your Email to Publish</h2>
              </div>

              {step === "verify-email" && (
                <>
                  <p className="text-sm text-muted-foreground mb-4">
                    We're sending a verification code to <strong>{form.email.trim()}</strong> to confirm your identity before publishing.
                  </p>
                  {verifySending && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span className="inline-block w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                      Sending verification code…
                    </div>
                  )}
                  {verifyError && (
                    <p className="text-sm text-red-600 mt-2">{verifyError}</p>
                  )}
                </>
              )}

              {step === "verify-code" && (
                <form onSubmit={handleCheckVerifyCode}>
                  <p className="text-sm text-muted-foreground mb-4">
                    We sent a 6-digit code to <strong>{form.email.trim()}</strong>. Check your inbox (and spam folder).
                  </p>

                  <div>
                    <label htmlFor="verify-code-input" className="block text-sm font-medium text-foreground mb-1.5">
                      Verification Code
                    </label>
                    <input
                      id="verify-code-input"
                      type="text"
                      inputMode="numeric"
                      maxLength={6}
                      value={verifyCode}
                      onChange={(e) => { setVerifyCode(e.target.value.replace(/\D/g, "").slice(0, 6)); setVerifyError(null); }}
                      placeholder="000000"
                      className={`${inputClass()} text-center text-2xl tracking-[0.3em] font-mono max-w-xs`}
                      autoFocus
                      required
                    />
                  </div>

                  {verifyError && (
                    <p className="text-sm text-red-600 mt-3">{verifyError}</p>
                  )}

                  <button
                    type="submit"
                    disabled={verifyChecking || verifyCode.length !== 6}
                    className="mt-4 w-full sm:w-auto px-8 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {verifyChecking ? (
                      <span className="inline-flex items-center gap-2 justify-center">
                        <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                        Verifying & Publishing…
                      </span>
                    ) : "Verify & Publish"}
                  </button>

                  <div className="mt-3 flex flex-wrap items-center gap-4">
                    <button
                      type="button"
                      onClick={() => handleSendVerifyCode()}
                      disabled={verifySending}
                      className="text-sm text-primary hover:underline disabled:opacity-50"
                    >
                      {verifySending ? "Resending…" : "Resend code"}
                    </button>
                    <button
                      type="button"
                      onClick={() => { setStep("preview"); setVerifyCode(""); setVerifyError(null); }}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      ← Back to preview
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => { setStep("form"); setSubmitError(null); setVerifyError(null); setVerifyCode(""); }}
              disabled={step === "publishing" || step === "verify-email"}
              className="flex-1 sm:flex-none px-8 py-3 border border-border rounded-lg font-medium hover:bg-muted/40 transition-colors disabled:opacity-50"
            >
              ✏️ Edit Details
            </button>
            {step !== "verify-email" && step !== "verify-code" && (
              <button
                onClick={handlePublish}
                disabled={step === "publishing"}
                className="flex-1 sm:flex-none px-8 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {step === "publishing" ? (
                  <span className="flex items-center gap-2 justify-center">
                    <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Publishing…
                  </span>
                ) : (
                  "✅ Publish Event"
                )}
              </button>
            )}
          </div>
        </main>

        <SiteFooter />
      </div>
    );
  }

  /* ================================================================ */
  /* RENDER: Form (step === "form" or "synthesizing")                 */
  /* ================================================================ */
  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>Submit an Event — The Videshi</title>
        <meta name="description" content="Submit your Indian community event to be featured on The Videshi." />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container flex-1 pt-8 md:pt-10 pb-16 max-w-2xl mx-auto px-4">
        <div className="mb-8">
          <Link to="/events" className="text-sm text-primary hover:underline mb-2 inline-block">
            ← Back to Events
          </Link>
          <h1 className="font-serif text-3xl md:text-4xl text-foreground mb-2">
            Submit Your Event
          </h1>
          <p className="text-muted-foreground">
            Share an upcoming Indian community event — concerts, festivals, temple events, community gatherings, and more.
          </p>
        </div>

        <form onSubmit={handlePreview} className="space-y-5">
          {/* Event Name */}
          <Field label="Event Name" required error={errors.title}>
            <input
              type="text"
              value={form.title}
              onChange={set("title")}
              placeholder="e.g. Diwali Mela at Sunnyvale Hindu Temple"
              className={inputClass(errors.title)}
            />
          </Field>

          {/* Dates row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Field label="Date" required error={errors.date}>
              <input
                type="date"
                value={form.date}
                onChange={set("date")}
                className={inputClass(errors.date)}
              />
            </Field>
            <Field label="End Date" error={errors.end_date}>
              <input
                type="date"
                value={form.end_date}
                onChange={set("end_date")}
                placeholder="For multi-day events"
                className={inputClass(errors.end_date)}
              />
            </Field>
            <Field label="Time">
              <input
                type="time"
                value={form.time}
                onChange={set("time")}
                className={inputClass()}
              />
            </Field>
          </div>

          {/* Location row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Field label="City" required error={errors.city}>
              <input
                type="text"
                value={form.city}
                onChange={set("city")}
                placeholder="e.g. Sunnyvale"
                className={inputClass(errors.city)}
              />
            </Field>
            <Field label="State" required error={errors.state}>
              <select
                value={form.state}
                onChange={set("state")}
                className={inputClass(errors.state)}
              >
                <option value="">Select state</option>
                {US_STATES.map((s) => (
                  <option key={s} value={s}>{STATE_NAMES[s] || s}</option>
                ))}
              </select>
            </Field>
            <Field label="Venue Name" required error={errors.venue_name}>
              <input
                type="text"
                value={form.venue_name}
                onChange={set("venue_name")}
                placeholder="e.g. Sunnyvale Hindu Temple"
                className={inputClass(errors.venue_name)}
              />
            </Field>
          </div>

          {/* Category */}
          <Field label="Category" required error={errors.category}>
            <select
              value={form.category}
              onChange={set("category")}
              className={inputClass(errors.category)}
            >
              <option value="">Select a category</option>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </Field>

          {/* Ticket URL */}
          <Field label="Ticket / Event URL" error={errors.ticket_url}>
            <input
              type="url"
              value={form.ticket_url}
              onChange={set("ticket_url")}
              placeholder="https://..."
              className={inputClass(errors.ticket_url)}
            />
          </Field>

          {/* Description */}
          <Field label="Brief Description">
            <textarea
              value={form.description}
              onChange={set("description")}
              placeholder="Tell us about this event in a few sentences — we'll enhance it for you..."
              rows={4}
              maxLength={500}
              className={inputClass()}
            />
            <p className="text-xs text-muted-foreground mt-1 text-right">
              {form.description.length}/500
            </p>
          </Field>

          {/* ---- Cover Image ---- */}
          <Field label="Cover Image">
            <input
              ref={coverInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(e) => handleCoverSelect(e.target.files)}
              className="hidden"
            />
            {coverImage ? (
              <div className="relative inline-block">
                <img
                  src={coverImage.url}
                  alt="Cover preview"
                  className="w-full max-w-xs h-40 object-cover rounded-lg border border-border"
                />
                <button
                  type="button"
                  onClick={removeCover}
                  className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs font-bold shadow hover:bg-red-600 transition-colors"
                  aria-label="Remove cover image"
                >
                  ✕
                </button>
              </div>
            ) : (
              <div
                onClick={() => coverInputRef.current?.click()}
                {...dragHandlers(setCoverDragging, handleCoverSelect)}
                className={`flex flex-col items-center justify-center gap-2 py-8 px-4 rounded-lg border-2 border-dashed cursor-pointer transition-colors ${
                  coverDragging
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50 hover:bg-muted/20"
                }`}
              >
                <span className="text-3xl">📷</span>
                <span className="text-sm text-muted-foreground text-center">
                  Click or drag an image here
                </span>
                <span className="text-xs text-muted-foreground/60">JPG, PNG, or WebP · Max 5 MB</span>
              </div>
            )}
            <p className="text-xs text-muted-foreground mt-1.5">
              This will be the main image for your event.
            </p>
          </Field>

          {/* ---- Additional Images ---- */}
          <Field label={`Additional Images (${additionalImages.length}/${MAX_ADDITIONAL})`}>
            <input
              ref={additionalInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              multiple
              onChange={(e) => handleAdditionalSelect(e.target.files)}
              className="hidden"
            />

            {additionalImages.length > 0 && (
              <div className="flex gap-3 overflow-x-auto pb-2 mb-3">
                {additionalImages.map((img) => (
                  <div key={img.id} className="relative flex-shrink-0">
                    <img
                      src={img.url}
                      alt="Preview"
                      className="w-20 h-20 object-cover rounded-lg border border-border"
                    />
                    <button
                      type="button"
                      onClick={() => removeAdditional(img.id)}
                      className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center text-[10px] font-bold shadow hover:bg-red-600 transition-colors"
                      aria-label="Remove image"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}

            {additionalImages.length < MAX_ADDITIONAL && (
              <div
                onClick={() => additionalInputRef.current?.click()}
                {...dragHandlers(setAdditionalDragging, handleAdditionalSelect)}
                className={`flex items-center justify-center gap-2 py-4 px-4 rounded-lg border-2 border-dashed cursor-pointer transition-colors ${
                  additionalDragging
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50 hover:bg-muted/20"
                }`}
              >
                <span className="text-lg">+</span>
                <span className="text-sm text-muted-foreground">
                  Add photos
                </span>
              </div>
            )}
            <p className="text-xs text-muted-foreground mt-1.5">
              Add photos of the venue, performers, or event details.
            </p>
          </Field>

          {/* Image error */}
          {imageError && (
            <div className="rounded-lg bg-amber-50 border border-amber-200 text-amber-700 px-4 py-3 text-sm">
              {imageError}
            </div>
          )}

          {/* Email */}
          <Field label="Your Email" required error={errors.email}>
            <input
              type="email"
              value={form.email}
              onChange={(e) => updateField("email", e.target.value)}
              placeholder="you@example.com"
              className={inputClass(errors.email)}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Not displayed publicly. We'll verify this email before publishing your event.
            </p>
          </Field>

          {submitError && step === "form" && (
            <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
              {submitError}
            </div>
          )}

          <TurnstileWidget
            onVerify={(token) => setTurnstileToken(token)}
            onExpire={() => setTurnstileToken(null)}
            className="mb-2"
          />

          <button
            type="submit"
            disabled={step === "synthesizing" || !turnstileToken}
            className="w-full sm:w-auto px-8 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {step === "synthesizing" ? (
              <span className="flex items-center gap-2 justify-center">
                <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                Preparing Preview…
              </span>
            ) : (
              "Preview Event →"
            )}
          </button>
        </form>
      </main>

      <SiteFooter />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Helper components                                                  */
/* ------------------------------------------------------------------ */

function Field({
  label,
  required,
  error,
  children,
}: {
  label: string;
  required?: boolean;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-foreground mb-1.5">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      {children}
      {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
    </div>
  );
}

function inputClass(error?: string): string {
  return `w-full px-3.5 py-2.5 rounded-lg border text-sm text-foreground bg-background placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 transition-colors ${
    error
      ? "border-red-400 focus:ring-red-300 focus:border-red-400"
      : "border-border focus:ring-primary/40 focus:border-primary/40"
  }`;
}
