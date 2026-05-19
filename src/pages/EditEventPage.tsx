import { useState, useCallback, useRef, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useParams } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { supabase } from "@/integrations/supabase/client";
import { getEventBySlug, generateSlug } from "@/lib/events";
import type { EventItem } from "@/lib/events";

/* ------------------------------------------------------------------ */
/* Constants                                                          */
/* ------------------------------------------------------------------ */
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
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
  "Entertainment","Community","Sports","Religious","Education","Competition","Other",
];

/* ------------------------------------------------------------------ */
/* Image preview helpers                                              */
/* ------------------------------------------------------------------ */
type ImagePreview = { id: string; file: File; url: string };

function createPreview(file: File): ImagePreview {
  return { id: crypto.randomUUID(), file, url: URL.createObjectURL(file) };
}

function validateImageFile(file: File): string | null {
  if (!ACCEPTED_TYPES.includes(file.type)) return "Only JPG, PNG, or WebP images are accepted.";
  if (file.size > MAX_FILE_SIZE) return `File "${file.name}" exceeds 5 MB.`;
  return null;
}

/* ------------------------------------------------------------------ */
/* Form data type                                                     */
/* ------------------------------------------------------------------ */
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
};

/* ------------------------------------------------------------------ */
/* Shared form field component                                        */
/* ------------------------------------------------------------------ */
const fieldClass =
  "w-full px-4 py-2.5 rounded-lg border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/40 transition-colors";
const labelClass = "block text-sm font-medium text-foreground mb-1.5";
const errorClass = "text-xs text-red-600 mt-1";

/* ------------------------------------------------------------------ */
/* Main component                                                     */
/* ------------------------------------------------------------------ */
export default function EditEventPage() {
  const { slug } = useParams<{ slug: string }>();

  /* Step state: "email" → "code" → "edit" → "done" */
  const [step, setStep] = useState<"loading" | "not_editable" | "email" | "code" | "edit" | "done">("loading");

  /* Event data */
  const [event, setEvent] = useState<EventItem | null>(null);

  /* Email / OTP state */
  const [email, setEmail] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [otpSending, setOtpSending] = useState(false);
  const [otpVerifying, setOtpVerifying] = useState(false);
  const [otpError, setOtpError] = useState<string | null>(null);

  /* Edit form state */
  const [form, setForm] = useState<FormData>({
    title: "", date: "", end_date: "", time: "", city: "", state: "",
    venue_name: "", category: "", ticket_url: "", description: "",
  });
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  /* Image state */
  const [coverImage, setCoverImage] = useState<ImagePreview | null>(null);
  const [existingCoverUrl, setExistingCoverUrl] = useState<string | null>(null);
  const [additionalImages, setAdditionalImages] = useState<ImagePreview[]>([]);
  const [existingAdditionalUrls, setExistingAdditionalUrls] = useState<string[]>([]);
  const [imageError, setImageError] = useState<string | null>(null);
  const coverInputRef = useRef<HTMLInputElement>(null);
  const additionalInputRef = useRef<HTMLInputElement>(null);

  /* Load event on mount */
  useEffect(() => {
    if (!slug) return;
    getEventBySlug(slug).then((ev) => {
      if (!ev) { setStep("not_editable"); return; }
      if (ev.source !== "user_submitted") { setStep("not_editable"); return; }
      setEvent(ev);
      setForm({
        title: ev.title || "",
        date: ev.date || "",
        end_date: ev.end_date || "",
        time: ev.time || "",
        city: ev.city || "",
        state: ev.state || "",
        venue_name: ev.venue_name || "",
        category: ev.category || "",
        ticket_url: ev.ticket_url || "",
        description: ev.description || "",
      });
      setExistingCoverUrl(ev.image_url || null);
      /* venue_images is JSONB — could be string[] or null */
      const vi = (ev as any).venue_images;
      if (Array.isArray(vi)) setExistingAdditionalUrls(vi);
      setStep("email");
    });
  }, [slug]);

  /* ---- Form helpers ---- */
  const set = (field: keyof FormData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setForm((f) => ({ ...f, [field]: e.target.value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }));
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
    setExistingCoverUrl(null); // replacing existing
  }, [coverImage]);

  const removeCover = useCallback(() => {
    if (coverImage) URL.revokeObjectURL(coverImage.url);
    setCoverImage(null);
    setExistingCoverUrl(null);
    if (coverInputRef.current) coverInputRef.current.value = "";
  }, [coverImage]);

  /* ---- Additional images handlers ---- */
  const handleAdditionalSelect = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return;
    setImageError(null);
    const totalExisting = existingAdditionalUrls.length + additionalImages.length;
    const remaining = MAX_ADDITIONAL - totalExisting;
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
  }, [additionalImages.length, existingAdditionalUrls.length]);

  const removeAdditional = useCallback((id: string) => {
    setAdditionalImages((prev) => {
      const img = prev.find((p) => p.id === id);
      if (img) URL.revokeObjectURL(img.url);
      return prev.filter((p) => p.id !== id);
    });
  }, []);

  const removeExistingAdditional = useCallback((url: string) => {
    setExistingAdditionalUrls((prev) => prev.filter((u) => u !== url));
  }, []);

  /* ---- Drag handlers ---- */
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
  async function uploadImage(file: File, eventSlug: string, prefix: string): Promise<string | null> {
    const ext = file.name.split(".").pop() || "jpg";
    const safeName = `${prefix}-${Date.now()}.${ext}`;
    const path = `events/${eventSlug}/${safeName}`;

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

  /* ================================================================ */
  /* Step 1: Send OTP                                                 */
  /* ================================================================ */
  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!event) return;
    setOtpError(null);
    setOtpSending(true);

    try {
      const { data, error } = await supabase.functions.invoke("send-event-otp", {
        body: { event_id: event.id, email: email.trim() },
      });
      if (error) throw new Error((data as any)?.error || error.message || "Failed to send code");
      if (data && !data.ok) throw new Error(data.error || "Failed to send code");
      setStep("code");
    } catch (err: any) {
      setOtpError(err.message || "Something went wrong");
    } finally {
      setOtpSending(false);
    }
  };

  /* ================================================================ */
  /* Step 2: Verify OTP                                               */
  /* ================================================================ */
  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!event) return;
    setOtpError(null);
    setOtpVerifying(true);

    try {
      const { data, error } = await supabase.functions.invoke("verify-event-otp", {
        body: { event_id: event.id, email: email.trim(), code: otpCode.trim() },
      });
      if (error) throw new Error((data as any)?.error || error.message || "Verification failed");
      if (data && !data.verified) throw new Error(data.error || "Invalid code");
      setStep("edit");
    } catch (err: any) {
      setOtpError(err.message || "Invalid or expired code");
    } finally {
      setOtpVerifying(false);
    }
  };

  /* ================================================================ */
  /* Step 3: Save edits                                               */
  /* ================================================================ */
  const validate = (): boolean => {
    const errs: Partial<Record<keyof FormData, string>> = {};
    if (!form.title.trim()) errs.title = "Event name is required";
    if (!form.date) errs.date = "Date is required";
    if (!form.city.trim()) errs.city = "City is required";
    if (!form.state) errs.state = "State is required";
    if (!form.venue_name.trim()) errs.venue_name = "Venue is required";
    if (!form.category) errs.category = "Category is required";
    if (form.ticket_url && !/^https?:\/\/.+/.test(form.ticket_url.trim())) {
      errs.ticket_url = "Please enter a valid URL starting with http";
    }
    if (form.end_date && form.end_date < form.date) {
      errs.end_date = "End date must be on or after start date";
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!event || !validate()) return;

    setSaving(true);
    setSaveError(null);

    const eventSlug = event.slug || generateSlug(event.title, event.date);

    /* Upload new images */
    let imageUrl: string | null = existingCoverUrl;
    let imageNote = "";

    if (coverImage) {
      const uploaded = await uploadImage(coverImage.file, eventSlug, "cover");
      if (uploaded) {
        imageUrl = uploaded;
      } else {
        imageNote = "Cover image upload failed. ";
      }
    }

    let venueImages: string[] = [...existingAdditionalUrls];
    if (additionalImages.length > 0) {
      const results = await Promise.all(
        additionalImages.map((img, i) => uploadImage(img.file, eventSlug, `photo-${i + 1}`))
      );
      venueImages = [...venueImages, ...results.filter((u): u is string => u !== null)];
      const failed = results.length - results.filter(Boolean).length;
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
      image_url: imageUrl,
      venue_images: venueImages.length > 0 ? venueImages : null,
    };

    const { error } = await supabase
      .from("events")
      .update(row)
      .eq("id", event.id);

    setSaving(false);

    if (error) {
      console.error("Update error:", error);
      setSaveError("Failed to save changes. Please try again.");
      return;
    }

    if (imageNote) setSaveError(imageNote);
    setStep("done");
  };

  /* ================================================================ */
  /* Render                                                           */
  /* ================================================================ */

  /* Loading state */
  if (step === "loading") {
    return (
      <div className="min-h-screen flex flex-col">
        <Helmet><title>Edit Event — The Videshi</title></Helmet>
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 flex items-center justify-center py-16">
          <div className="animate-pulse text-muted-foreground">Loading event…</div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  /* Not editable */
  if (step === "not_editable") {
    return (
      <div className="min-h-screen flex flex-col">
        <Helmet><title>Edit Event — The Videshi</title></Helmet>
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 max-w-lg py-16 text-center">
          <h1 className="font-serif text-2xl text-foreground mb-4">Cannot Edit This Event</h1>
          <p className="text-muted-foreground mb-6">
            Only user-submitted events can be edited. If you need changes, please{" "}
            <Link to="/contact" className="text-primary hover:underline">contact us</Link>.
          </p>
          <Link to="/events" className="text-primary hover:underline">← Back to Events</Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  /* Done */
  if (step === "done") {
    return (
      <div className="min-h-screen flex flex-col">
        <Helmet><title>Event Updated — The Videshi</title></Helmet>
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 max-w-lg py-16 text-center">
          <div className="text-5xl mb-4">✅</div>
          <h1 className="font-serif text-2xl text-foreground mb-3">Event Updated!</h1>
          <p className="text-muted-foreground mb-6">
            Your changes are live.
            {saveError && <span className="block text-amber-600 text-sm mt-2">{saveError}</span>}
          </p>
          <Link
            to={`/events/${slug}`}
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-colors"
          >
            View Your Event →
          </Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>Edit Event — The Videshi</title>
        <meta name="robots" content="noindex" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container flex-1 max-w-2xl py-10 md:py-16">
        <Link to={`/events/${slug}`} className="text-sm text-muted-foreground hover:text-primary transition-colors mb-6 inline-block">
          ← Back to event
        </Link>

        <h1 className="font-serif text-3xl text-foreground mb-2">Edit Event</h1>
        {event && (
          <p className="text-muted-foreground mb-8">
            {event.title}
          </p>
        )}

        {/* ============================================================ */}
        {/* Step 1: Email                                                */}
        {/* ============================================================ */}
        {step === "email" && (
          <form onSubmit={handleSendOtp} className="space-y-5">
            <div className="bg-muted/30 border border-border rounded-xl p-6">
              <h2 className="font-serif text-lg text-foreground mb-2">Verify Your Identity</h2>
              <p className="text-sm text-muted-foreground mb-5">
                Enter the email you used when submitting this event. We'll send a verification code.
              </p>

              <div>
                <label htmlFor="verify-email" className={labelClass}>Email Address</label>
                <input
                  id="verify-email"
                  type="email"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setOtpError(null); }}
                  placeholder="you@example.com"
                  className={fieldClass}
                  required
                />
              </div>

              {otpError && (
                <p className="text-sm text-red-600 mt-3">{otpError}</p>
              )}

              <button
                type="submit"
                disabled={otpSending || !email.trim()}
                className="mt-5 w-full px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {otpSending ? (
                  <span className="inline-flex items-center gap-2">
                    <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Sending Code…
                  </span>
                ) : "Send Verification Code"}
              </button>
            </div>
          </form>
        )}

        {/* ============================================================ */}
        {/* Step 2: OTP Code                                             */}
        {/* ============================================================ */}
        {step === "code" && (
          <form onSubmit={handleVerifyOtp} className="space-y-5">
            <div className="bg-muted/30 border border-border rounded-xl p-6">
              <h2 className="font-serif text-lg text-foreground mb-2">Enter Verification Code</h2>
              <p className="text-sm text-muted-foreground mb-5">
                We sent a 6-digit code to <strong>{email}</strong>. Check your inbox (and spam folder).
              </p>

              <div>
                <label htmlFor="otp-code" className={labelClass}>Verification Code</label>
                <input
                  id="otp-code"
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  value={otpCode}
                  onChange={(e) => { setOtpCode(e.target.value.replace(/\D/g, "").slice(0, 6)); setOtpError(null); }}
                  placeholder="000000"
                  className={`${fieldClass} text-center text-2xl tracking-[0.3em] font-mono`}
                  autoFocus
                  required
                />
              </div>

              {otpError && (
                <p className="text-sm text-red-600 mt-3">{otpError}</p>
              )}

              <button
                type="submit"
                disabled={otpVerifying || otpCode.length !== 6}
                className="mt-5 w-full px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {otpVerifying ? (
                  <span className="inline-flex items-center gap-2">
                    <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Verifying…
                  </span>
                ) : "Verify & Edit"}
              </button>

              <button
                type="button"
                onClick={() => { setStep("email"); setOtpCode(""); setOtpError(null); }}
                className="mt-3 w-full text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Use a different email
              </button>
            </div>
          </form>
        )}

        {/* ============================================================ */}
        {/* Step 3: Edit form                                            */}
        {/* ============================================================ */}
        {step === "edit" && (
          <form onSubmit={handleSave} className="space-y-5">
            {/* Title */}
            <div>
              <label htmlFor="edit-title" className={labelClass}>Event Name *</label>
              <input id="edit-title" type="text" value={form.title} onChange={set("title")}
                className={`${fieldClass} ${errors.title ? "border-red-400" : "border-border"}`} />
              {errors.title && <p className={errorClass}>{errors.title}</p>}
            </div>

            {/* Dates row */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label htmlFor="edit-date" className={labelClass}>Date *</label>
                <input id="edit-date" type="date" value={form.date} onChange={set("date")}
                  className={`${fieldClass} ${errors.date ? "border-red-400" : "border-border"}`} />
                {errors.date && <p className={errorClass}>{errors.date}</p>}
              </div>
              <div>
                <label htmlFor="edit-end-date" className={labelClass}>End Date</label>
                <input id="edit-end-date" type="date" value={form.end_date} onChange={set("end_date")}
                  className={`${fieldClass} ${errors.end_date ? "border-red-400" : "border-border"}`} />
                {errors.end_date && <p className={errorClass}>{errors.end_date}</p>}
              </div>
              <div>
                <label htmlFor="edit-time" className={labelClass}>Time</label>
                <input id="edit-time" type="time" value={form.time} onChange={set("time")}
                  className={`${fieldClass} border-border`} />
              </div>
            </div>

            {/* Location row */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label htmlFor="edit-city" className={labelClass}>City *</label>
                <input id="edit-city" type="text" value={form.city} onChange={set("city")}
                  className={`${fieldClass} ${errors.city ? "border-red-400" : "border-border"}`} />
                {errors.city && <p className={errorClass}>{errors.city}</p>}
              </div>
              <div>
                <label htmlFor="edit-state" className={labelClass}>State *</label>
                <select id="edit-state" value={form.state} onChange={set("state")}
                  className={`${fieldClass} ${errors.state ? "border-red-400" : "border-border"}`}>
                  <option value="">Select…</option>
                  {US_STATES.map((s) => <option key={s} value={s}>{s} — {STATE_NAMES[s]}</option>)}
                </select>
                {errors.state && <p className={errorClass}>{errors.state}</p>}
              </div>
              <div>
                <label htmlFor="edit-venue" className={labelClass}>Venue *</label>
                <input id="edit-venue" type="text" value={form.venue_name} onChange={set("venue_name")}
                  className={`${fieldClass} ${errors.venue_name ? "border-red-400" : "border-border"}`} />
                {errors.venue_name && <p className={errorClass}>{errors.venue_name}</p>}
              </div>
            </div>

            {/* Category + Ticket URL row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label htmlFor="edit-category" className={labelClass}>Category *</label>
                <select id="edit-category" value={form.category} onChange={set("category")}
                  className={`${fieldClass} ${errors.category ? "border-red-400" : "border-border"}`}>
                  <option value="">Select…</option>
                  {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
                {errors.category && <p className={errorClass}>{errors.category}</p>}
              </div>
              <div>
                <label htmlFor="edit-ticket" className={labelClass}>Ticket URL</label>
                <input id="edit-ticket" type="url" value={form.ticket_url} onChange={set("ticket_url")}
                  placeholder="https://…" className={`${fieldClass} ${errors.ticket_url ? "border-red-400" : "border-border"}`} />
                {errors.ticket_url && <p className={errorClass}>{errors.ticket_url}</p>}
              </div>
            </div>

            {/* Description */}
            <div>
              <label htmlFor="edit-desc" className={labelClass}>Description</label>
              <textarea id="edit-desc" value={form.description} onChange={set("description")}
                rows={3} maxLength={500} placeholder="Brief description of the event…"
                className={`${fieldClass} border-border resize-none`} />
              <p className="text-xs text-muted-foreground mt-1">{form.description.length}/500</p>
            </div>

            {/* ---- Cover Image ---- */}
            <div>
              <label className={labelClass}>Cover Image</label>
              <p className="text-xs text-muted-foreground mb-2">Main image for your event</p>

              {(existingCoverUrl || coverImage) ? (
                <div className="relative inline-block">
                  <img
                    src={coverImage?.url || existingCoverUrl!}
                    alt="Cover preview"
                    className="w-40 h-28 object-cover rounded-lg border border-border"
                  />
                  <button type="button" onClick={removeCover}
                    className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs hover:bg-red-600 transition-colors shadow-sm">
                    ✕
                  </button>
                </div>
              ) : (
                <div
                  {...dragHandlers(setCoverDragging, handleCoverSelect)}
                  onClick={() => coverInputRef.current?.click()}
                  className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                    coverDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                  }`}
                >
                  <p className="text-sm text-muted-foreground">
                    Drop an image here or <span className="text-primary">click to browse</span>
                  </p>
                  <p className="text-xs text-muted-foreground/60 mt-1">JPG, PNG, WebP · Max 5 MB</p>
                </div>
              )}
              <input ref={coverInputRef} type="file" accept="image/jpeg,image/png,image/webp"
                onChange={(e) => handleCoverSelect(e.target.files)} className="hidden" />
            </div>

            {/* ---- Additional Images ---- */}
            <div>
              <label className={labelClass}>Additional Images</label>
              <p className="text-xs text-muted-foreground mb-2">
                Venue, performers, or event details (up to {MAX_ADDITIONAL})
              </p>

              {/* Existing thumbnails */}
              {(existingAdditionalUrls.length > 0 || additionalImages.length > 0) && (
                <div className="flex gap-2 overflow-x-auto pb-2 mb-2">
                  {existingAdditionalUrls.map((url) => (
                    <div key={url} className="relative flex-shrink-0">
                      <img src={url} alt="" className="w-20 h-20 object-cover rounded-lg border border-border" />
                      <button type="button" onClick={() => removeExistingAdditional(url)}
                        className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center text-[10px] hover:bg-red-600 shadow-sm">
                        ✕
                      </button>
                    </div>
                  ))}
                  {additionalImages.map((img) => (
                    <div key={img.id} className="relative flex-shrink-0">
                      <img src={img.url} alt="" className="w-20 h-20 object-cover rounded-lg border border-border" />
                      <button type="button" onClick={() => removeAdditional(img.id)}
                        className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center text-[10px] hover:bg-red-600 shadow-sm">
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {(existingAdditionalUrls.length + additionalImages.length) < MAX_ADDITIONAL && (
                <div
                  {...dragHandlers(setAdditionalDragging, handleAdditionalSelect)}
                  onClick={() => additionalInputRef.current?.click()}
                  className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
                    additionalDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                  }`}
                >
                  <p className="text-sm text-muted-foreground">
                    + Add photos
                  </p>
                </div>
              )}
              <input ref={additionalInputRef} type="file" accept="image/jpeg,image/png,image/webp" multiple
                onChange={(e) => handleAdditionalSelect(e.target.files)} className="hidden" />
            </div>

            {imageError && (
              <p className="text-sm text-red-600">{imageError}</p>
            )}

            {saveError && (
              <p className="text-sm text-red-600">{saveError}</p>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={saving}
              className="w-full px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? (
                <span className="inline-flex items-center gap-2">
                  <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  Saving Changes…
                </span>
              ) : "Save Changes"}
            </button>
          </form>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
