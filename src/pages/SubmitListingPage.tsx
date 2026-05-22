import { useState, useRef, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { supabase } from "@/integrations/supabase/client";
import { DIRECTORY_CATEGORIES, CATEGORY_ICONS } from "@/lib/directory";
import TurnstileWidget from "@/components/TurnstileWidget";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];

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

/* ------------------------------------------------------------------ */
/* Slug generator                                                     */
/* ------------------------------------------------------------------ */
function generateListingSlug(name: string): string {
  const cleaned = name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+$/, "")
    .slice(0, 60)
    .replace(/-+$/, "");
  const suffix = Math.random().toString(36).slice(2, 8);
  return `${cleaned}-${suffix}`;
}

/* ------------------------------------------------------------------ */
/* Image preview                                                      */
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
/* Form type                                                          */
/* ------------------------------------------------------------------ */
type FormData = {
  name: string;
  category: string;
  subcategory: string;
  description: string;
  phone: string;
  email: string;
  website: string;
  address: string;
  city: string;
  state: string;
  zip: string;
  contact_email: string;
};

const INITIAL: FormData = {
  name: "",
  category: "",
  subcategory: "",
  description: "",
  phone: "",
  email: "",
  website: "",
  address: "",
  city: "",
  state: "",
  zip: "",
  contact_email: "",
};

/* ------------------------------------------------------------------ */
/* Main component                                                     */
/* ------------------------------------------------------------------ */
export default function SubmitListingPage() {
  const [form, setForm] = useState<FormData>(INITIAL);
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [step, setStep] = useState<"form" | "preview" | "publishing" | "done">("form");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [publishedSlug, setPublishedSlug] = useState<string | null>(null);

  /* Turnstile bot protection */
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);

  /* Image state */
  const [coverImage, setCoverImage] = useState<ImagePreview | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  const coverInputRef = useRef<HTMLInputElement>(null);
  const [coverDragging, setCoverDragging] = useState(false);

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

  const dragHandlers = {
    onDragOver: (e: React.DragEvent) => { e.preventDefault(); setCoverDragging(true); },
    onDragEnter: (e: React.DragEvent) => { e.preventDefault(); setCoverDragging(true); },
    onDragLeave: () => setCoverDragging(false),
    onDrop: (e: React.DragEvent) => { e.preventDefault(); setCoverDragging(false); handleCoverSelect(e.dataTransfer.files); },
  };

  /* ---- Upload helper ---- */
  async function uploadImage(file: File, slug: string): Promise<string | null> {
    const ext = file.name.split(".").pop() || "jpg";
    const safeName = `cover-${Date.now()}.${ext}`;
    const path = `directory/${slug}/${safeName}`;

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
    if (!form.name.trim()) errs.name = "Business name is required";
    if (!form.category) errs.category = "Category is required";
    if (!form.city.trim()) errs.city = "City is required";
    if (!form.state) errs.state = "State is required";
    if (!form.contact_email.trim()) {
      errs.contact_email = "Your email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.contact_email.trim())) {
      errs.contact_email = "Please enter a valid email";
    }
    if (form.website && !/^https?:\/\/.+/.test(form.website.trim())) {
      errs.website = "Please enter a valid URL starting with http";
    }
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
      errs.email = "Please enter a valid email";
    }
    if (form.zip && !/^\d{5}(-\d{4})?$/.test(form.zip.trim())) {
      errs.zip = "Please enter a valid ZIP code";
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  /* ---- Preview ---- */
  const handlePreview = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    if (!turnstileToken) {
      setSubmitError("Please complete the bot verification.");
      return;
    }
    setStep("preview");
  };

  /* ---- Publish ---- */
  const handlePublish = async () => {
    setStep("publishing");
    setSubmitError(null);

    /* Server-side Turnstile verification */
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
        setStep("preview");
        return;
      }
    } catch {
      setSubmitError("Bot verification failed. Please try again.");
      setTurnstileToken(null);
      setStep("preview");
      return;
    }

    const slug = generateListingSlug(form.name.trim());

    /* Upload cover image */
    let imageUrl: string | null = null;
    if (coverImage) {
      imageUrl = await uploadImage(coverImage.file, slug);
    }

    const row: Record<string, unknown> = {
      name: form.name.trim(),
      category: form.category,
      subcategory: form.subcategory.trim() || null,
      description: form.description.trim() || null,
      phone: form.phone.trim() || null,
      email: form.email.trim() || null,
      website: form.website.trim() || null,
      address: form.address.trim() || null,
      city: form.city.trim(),
      state: form.state,
      zip: form.zip.trim() || null,
      image_url: imageUrl,
      source: "user_submitted",
      verified: false,
      featured: false,
      slug,
    };

    const sbRaw = supabase as unknown as { from: (t: string) => any };
    const { error } = await sbRaw.from("directory_listings").insert([row]);

    if (error) {
      console.error("Submit listing error:", error);
      setSubmitError("Something went wrong. Please try again.");
      setStep("preview");
      return;
    }

    setPublishedSlug(slug);
    setStep("done");
  };

  /* ================================================================ */
  /* RENDER: Done                                                     */
  /* ================================================================ */
  if (step === "done") {
    const fullUrl = publishedSlug ? `thevideshi.com/directory/${publishedSlug}` : "";
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <CategoryPills />
        <main className="container flex-1 pt-8 md:pt-10 pb-16 max-w-2xl mx-auto">
          <div className="text-center py-20">
            <p className="text-5xl mb-4">✅</p>
            <h2 className="font-serif text-2xl md:text-3xl text-foreground mb-3">
              Your Listing Is Live!
            </h2>
            <p className="text-muted-foreground text-lg mb-6">
              Your business has been added to the directory.
            </p>

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

            <div className="flex flex-col sm:flex-row justify-center gap-4">
              {publishedSlug && (
                <Link
                  to={`/directory/${publishedSlug}`}
                  className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
                >
                  View Your Listing →
                </Link>
              )}
              <Link
                to="/directory"
                className="px-6 py-3 border border-border rounded-lg font-medium hover:bg-muted/40 transition-colors"
              >
                Browse Directory
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
  if (step === "preview" || step === "publishing") {
    const catIcon = CATEGORY_ICONS[form.category] || "🏢";
    const loc = [form.city, form.state].filter(Boolean).join(", ");

    return (
      <div className="min-h-screen flex flex-col">
        <Helmet>
          <title>Preview Your Listing — The Videshi</title>
          <meta name="robots" content="noindex" />
        </Helmet>

        <Masthead />
        <CategoryPills />

        <main className="container flex-1 pt-8 md:pt-10 pb-16 max-w-2xl mx-auto px-4">
          <div className="mb-6">
            <p className="text-sm text-primary font-medium mb-2 flex items-center gap-2">
              <span className="inline-block w-6 h-6 rounded-full bg-primary/10 text-center text-xs leading-6 font-bold">2</span>
              Preview your listing
            </p>
            <h1 className="font-serif text-2xl md:text-3xl text-foreground mb-1">
              Here's how your listing will look
            </h1>
            <p className="text-muted-foreground text-sm">
              Review the details below before publishing.
            </p>
          </div>

          {/* Preview Card */}
          <div className="rounded-xl overflow-hidden bg-card border border-border mb-8">
            {/* Image */}
            {coverImage ? (
              <div className="w-full overflow-hidden">
                <img
                  src={coverImage.url}
                  alt={form.name}
                  className="w-full max-h-64 object-contain bg-muted/10"
                />
              </div>
            ) : (
              <div className="w-full h-24 bg-muted/30 flex items-center justify-center">
                <span className="text-4xl opacity-60">{catIcon}</span>
              </div>
            )}

            <div className="p-5 space-y-3">
              {/* Category badge */}
              <span className="inline-block px-2.5 py-1 rounded text-xs font-medium bg-primary/10 text-primary">
                {catIcon} {form.category}
              </span>

              {/* Name */}
              <h2 className="font-serif text-xl text-foreground">{form.name}</h2>

              {/* Location */}
              <p className="text-sm text-muted-foreground flex items-center gap-1.5">
                <span>📍</span> {form.address ? `${form.address}, ` : ""}{loc}{form.zip ? ` ${form.zip}` : ""}
              </p>

              {/* Description */}
              {form.description && (
                <p className="text-sm text-muted-foreground leading-relaxed">{form.description}</p>
              )}

              {/* Contact info */}
              <div className="pt-2 space-y-1.5 text-sm">
                {form.phone && (
                  <p className="flex items-center gap-2 text-muted-foreground">
                    <span>📞</span> {form.phone}
                  </p>
                )}
                {form.email && (
                  <p className="flex items-center gap-2 text-muted-foreground">
                    <span>✉️</span> {form.email}
                  </p>
                )}
                {form.website && (
                  <p className="flex items-center gap-2 text-muted-foreground">
                    <span>🌐</span> {form.website}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Error */}
          {submitError && (
            <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm mb-4">
              {submitError}
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => { setStep("form"); setSubmitError(null); }}
              disabled={step === "publishing"}
              className="flex-1 sm:flex-none px-8 py-3 border border-border rounded-lg font-medium hover:bg-muted/40 transition-colors disabled:opacity-50"
            >
              ✏️ Edit Details
            </button>
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
                "✅ Publish Listing"
              )}
            </button>
          </div>
        </main>

        <SiteFooter />
      </div>
    );
  }

  /* ================================================================ */
  /* RENDER: Form                                                     */
  /* ================================================================ */
  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>Submit a Listing — Desi Business Directory | The Videshi</title>
        <meta name="description" content="Add your business or professional practice to The Videshi's Indian & desi business directory." />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container flex-1 pt-8 md:pt-10 pb-16 max-w-2xl mx-auto px-4">
        <div className="mb-8">
          <Link to="/directory" className="text-sm text-primary hover:underline mb-2 inline-block">
            ← Back to Directory
          </Link>
          <h1 className="font-serif text-3xl md:text-4xl text-foreground mb-2">
            Submit Your Business
          </h1>
          <p className="text-muted-foreground">
            Add your business or professional practice to the desi directory — restaurants, doctors, attorneys, salons, tutors, and more.
          </p>
        </div>

        <form onSubmit={handlePreview} className="space-y-5">
          {/* Business Name */}
          <Field label="Business Name" required error={errors.name}>
            <input
              type="text"
              value={form.name}
              onChange={set("name")}
              placeholder="e.g. Patel Family Dentistry"
              className={inputClass(errors.name)}
            />
          </Field>

          {/* Category */}
          <Field label="Category" required error={errors.category}>
            <select
              value={form.category}
              onChange={set("category")}
              className={inputClass(errors.category)}
            >
              <option value="">Select a category</option>
              {DIRECTORY_CATEGORIES.map((c) => (
                <option key={c} value={c}>{CATEGORY_ICONS[c] || "🏢"} {c}</option>
              ))}
            </select>
          </Field>

          {/* Subcategory */}
          <Field label="Subcategory / Specialty">
            <input
              type="text"
              value={form.subcategory}
              onChange={set("subcategory")}
              placeholder="e.g. Dentist, Immigration Attorney, Catering..."
              className={inputClass()}
            />
          </Field>

          {/* Description */}
          <Field label="Description">
            <textarea
              value={form.description}
              onChange={set("description")}
              placeholder="A brief description of your business or services..."
              rows={4}
              maxLength={500}
              className={inputClass()}
            />
            <p className="text-xs text-muted-foreground mt-1 text-right">
              {form.description.length}/500
            </p>
          </Field>

          {/* Contact info row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Field label="Phone Number" error={errors.phone}>
              <input
                type="tel"
                value={form.phone}
                onChange={set("phone")}
                placeholder="(555) 123-4567"
                className={inputClass(errors.phone)}
              />
            </Field>
            <Field label="Business Email" error={errors.email}>
              <input
                type="email"
                value={form.email}
                onChange={set("email")}
                placeholder="info@yourbusiness.com"
                className={inputClass(errors.email)}
              />
            </Field>
          </div>

          {/* Website */}
          <Field label="Website" error={errors.website}>
            <input
              type="url"
              value={form.website}
              onChange={set("website")}
              placeholder="https://yourbusiness.com"
              className={inputClass(errors.website)}
            />
          </Field>

          {/* Address */}
          <Field label="Street Address">
            <input
              type="text"
              value={form.address}
              onChange={set("address")}
              placeholder="123 Main Street, Suite 100"
              className={inputClass()}
            />
          </Field>

          {/* City / State / Zip */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <Field label="City" required error={errors.city}>
              <input
                type="text"
                value={form.city}
                onChange={set("city")}
                placeholder="e.g. Fremont"
                className={inputClass(errors.city)}
              />
            </Field>
            <Field label="State" required error={errors.state}>
              <select
                value={form.state}
                onChange={set("state")}
                className={inputClass(errors.state)}
              >
                <option value="">Select</option>
                {US_STATES.map((s) => (
                  <option key={s} value={s}>{STATE_NAMES[s] || s}</option>
                ))}
              </select>
            </Field>
            <Field label="ZIP Code" error={errors.zip}>
              <input
                type="text"
                value={form.zip}
                onChange={set("zip")}
                placeholder="94536"
                maxLength={10}
                className={inputClass(errors.zip)}
              />
            </Field>
          </div>

          {/* Cover Image */}
          <Field label="Business Photo">
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
                {...dragHandlers}
                className={`flex flex-col items-center justify-center gap-2 py-8 px-4 rounded-lg border-2 border-dashed cursor-pointer transition-colors ${
                  coverDragging
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50 hover:bg-muted/20"
                }`}
              >
                <span className="text-3xl">📷</span>
                <span className="text-sm text-muted-foreground text-center">
                  Click or drag a photo here
                </span>
                <span className="text-xs text-muted-foreground/60">JPG, PNG, or WebP · Max 5 MB</span>
              </div>
            )}
            <p className="text-xs text-muted-foreground mt-1.5">
              A photo of your business, storefront, or logo.
            </p>
          </Field>

          {imageError && (
            <div className="rounded-lg bg-amber-50 border border-amber-200 text-amber-700 px-4 py-3 text-sm">
              {imageError}
            </div>
          )}

          {/* Divider */}
          <div className="h-px bg-border my-2" />

          {/* Contact email (your email — not displayed publicly) */}
          <Field label="Your Email" required error={errors.contact_email}>
            <input
              type="email"
              value={form.contact_email}
              onChange={set("contact_email")}
              placeholder="you@example.com"
              className={inputClass(errors.contact_email)}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Not displayed publicly. Used only if we need to contact you about this listing.
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
            disabled={!turnstileToken}
            className="w-full sm:w-auto px-8 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Preview Listing →
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
