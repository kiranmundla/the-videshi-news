import { useState, useRef, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { supabase } from "@/integrations/supabase/client";
import { generateSlug } from "@/lib/events";

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

/* ------------------------------------------------------------------ */
/* Image preview type                                                 */
/* ------------------------------------------------------------------ */
type ImagePreview = {
  id: string;
  file: File;
  url: string; // object URL for preview
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
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

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

  /* ---- Submit ---- */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setSubmitting(true);
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
      source: "user_submitted",
      organizer: form.email.trim(),
      slug,
    };
    if (imageUrl) row.image_url = imageUrl;
    if (venueImages.length > 0) row.venue_images = venueImages;

    const sbRaw = supabase as unknown as { from: (t: string) => any };
    const { error } = await sbRaw.from("events").insert([row]);

    setSubmitting(false);

    if (error) {
      console.error("Submit event error:", error);
      setSubmitError("Something went wrong. Please try again.");
    } else {
      setSubmitted(true);
      if (imageNote) setSubmitError(imageNote);
    }
  };

  /* ---- Success view ---- */
  if (submitted) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 pt-8 md:pt-10 pb-16 max-w-2xl mx-auto">
          <div className="text-center py-20">
            <p className="text-5xl mb-4">🎉</p>
            <h2 className="font-serif text-2xl md:text-3xl text-foreground mb-3">
              Thanks for submitting your event!
            </h2>
            <p className="text-muted-foreground text-lg mb-8">
              Your event will appear on The Videshi shortly. We may reach out to your email for additional details.
            </p>
            {submitError && (
              <p className="text-sm text-amber-600 mb-6">{submitError}</p>
            )}
            <div className="flex justify-center gap-4">
              <Link
                to="/events"
                className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
              >
                ← Back to Events
              </Link>
              <button
                onClick={() => { setSubmitted(false); setForm(INITIAL); setCoverImage(null); setAdditionalImages([]); setSubmitError(null); }}
                className="px-6 py-3 border border-border rounded-lg font-medium hover:bg-muted/40 transition-colors"
              >
                Submit Another
              </button>
            </div>
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  /* ---- Form view ---- */
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

        <form onSubmit={handleSubmit} className="space-y-5">
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
              placeholder="Tell us about this event in a few sentences..."
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

            {/* Thumbnails row */}
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
              onChange={set("email")}
              placeholder="you@example.com"
              className={inputClass(errors.email)}
            />
            <p className="text-xs text-muted-foreground mt-1">
              We may reach out for additional event details. Not displayed publicly.
            </p>
          </Field>

          {submitError && !submitted && (
            <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
              {submitError}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full sm:w-auto px-8 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? (
              <span className="flex items-center gap-2 justify-center">
                <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                Uploading & Submitting…
              </span>
            ) : (
              "Submit Event"
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
