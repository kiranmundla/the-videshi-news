import { useState, useRef, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { Upload, X, ChevronLeft, Loader2, Check, MapPin } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { supabase } from "@/integrations/supabase/client";
import TurnstileWidget from "@/components/TurnstileWidget";
import {
  CLASSIFIED_CATEGORIES,
  CATEGORY_ICONS,
  CATEGORY_COLORS,
  SUBCATEGORIES,
  generateClassifiedSlug,
} from "@/lib/classifieds";

const MAX_FILE_SIZE = 5 * 1024 * 1024;
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_PHOTOS = 3;

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

type FormData = {
  title: string;
  category: string;
  subcategory: string;
  description: string;
  price: string;
  contact_name: string;
  contact_email: string;
  contact_phone: string;
  city: string;
  state: string;
  zip: string;
};

const INITIAL: FormData = {
  title: "",
  category: "",
  subcategory: "",
  description: "",
  price: "",
  contact_name: "",
  contact_email: "",
  contact_phone: "",
  city: "",
  state: "",
  zip: "",
};

type ImagePreview = { id: string; file: File; url: string };
function createPreview(file: File): ImagePreview {
  return { id: crypto.randomUUID(), file, url: URL.createObjectURL(file) };
}

type Step = "form" | "preview" | "verify-email" | "verify-code" | "publishing" | "done";

const sb = supabase as any;

const inputClass =
  "w-full px-3 py-2.5 rounded-lg border border-border bg-card text-sm focus:outline-none focus:ring-2 focus:ring-primary/40";

export default function SubmitClassifiedPage() {
  const [step, setStep] = useState<Step>("form");
  const [form, setForm] = useState<FormData>(INITIAL);
  const [images, setImages] = useState<ImagePreview[]>([]);
  const [error, setError] = useState("");
  const [publishedSlug, setPublishedSlug] = useState("");
  const [copied, setCopied] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  /* Turnstile bot protection */
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);

  /* OTP state */
  const [verifyCode, setVerifyCode] = useState("");
  const [verifySending, setVerifySending] = useState(false);
  const [verifyChecking, setVerifyChecking] = useState(false);
  const [verifyError, setVerifyError] = useState<string | null>(null);

  const set = useCallback(
    (field: keyof FormData) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      setForm((f) => ({ ...f, [field]: e.target.value }));
      if (field === "category") setForm((f) => ({ ...f, subcategory: "" }));
    },
    [],
  );

  /* Image handling */
  const addImages = useCallback(
    (files: FileList | null) => {
      if (!files) return;
      const newPreviews: ImagePreview[] = [];
      for (let i = 0; i < files.length && images.length + newPreviews.length < MAX_PHOTOS; i++) {
        const f = files[i];
        if (!ACCEPTED_TYPES.includes(f.type)) continue;
        if (f.size > MAX_FILE_SIZE) continue;
        newPreviews.push(createPreview(f));
      }
      setImages((prev) => [...prev, ...newPreviews]);
    },
    [images.length],
  );

  const removeImage = useCallback((id: string) => {
    setImages((prev) => {
      const img = prev.find((p) => p.id === id);
      if (img) URL.revokeObjectURL(img.url);
      return prev.filter((p) => p.id !== id);
    });
  }, []);

  /* Validation */
  const validate = (): string | null => {
    if (!form.title.trim()) return "Title is required";
    if (!form.category) return "Category is required";
    if (!form.contact_email.trim()) return "Email is required (for verification & managing your listing)";
    if (!/\S+@\S+\.\S+/.test(form.contact_email)) return "Please enter a valid email";
    return null;
  };

  /* Preview */
  const goPreview = () => {
    const err = validate();
    if (err) { setError(err); return; }
    if (!turnstileToken) { setError("Please complete the bot verification."); return; }
    setError("");
    setStep("preview");
  };

  /* Start email verification */
  const startVerify = () => {
    setVerifyError(null);
    setVerifyCode("");
    setStep("verify-email");
  };

  /* Send verification code */
  const handleSendVerifyCode = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const email = form.contact_email.trim().toLowerCase();
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setVerifyError("Please enter a valid email address");
      return;
    }
    setVerifySending(true);
    setVerifyError(null);
    try {
      const { data, error } = await sb.functions.invoke("send-email-verify", {
        body: { email },
      });
      if (error) throw new Error(data?.error || error.message || "Failed to send code");
      if (data && !data.ok) throw new Error(data.error || "Failed to send code");
      setStep("verify-code");
    } catch (err: any) {
      setVerifyError(err.message || "Something went wrong");
    } finally {
      setVerifySending(false);
    }
  };

  /* Verify code then publish */
  const handleCheckVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    const email = form.contact_email.trim().toLowerCase();
    const code = verifyCode.trim();
    if (!code || code.length !== 6) {
      setVerifyError("Please enter the 6-digit code");
      return;
    }
    setVerifyChecking(true);
    setVerifyError(null);
    try {
      const { data, error } = await sb.functions.invoke("verify-email-code", {
        body: { email, code },
      });
      if (error) throw new Error(data?.error || error.message || "Verification failed");
      if (data && !data.verified) throw new Error(data.error || "Invalid code");
      /* Verified — now actually publish */
      await doPublish();
    } catch (err: any) {
      setVerifyError(err.message || "Invalid or expired code");
    } finally {
      setVerifyChecking(false);
    }
  };

  /* Actual publish (called after OTP verified) */
  const doPublish = async () => {
    setStep("publishing");
    setError("");

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
        setStep("preview");
        return;
      }
    } catch {
      setError("Bot verification failed. Please try again.");
      setTurnstileToken(null);
      setStep("preview");
      return;
    }

    try {
      const slug = generateClassifiedSlug(form.title);
      let imageUrl: string | null = null;
      const photoUrls: string[] = [];

      /* Upload images */
      for (const img of images) {
        const ext = img.file.name.split(".").pop() || "jpg";
        const path = `classifieds/${slug}/${img.id}.${ext}`;
        const { error: uploadErr } = await sb.storage
          .from("article-images")
          .upload(path, img.file, { cacheControl: "31536000", upsert: false });
        if (uploadErr) {
          console.error("Upload error:", uploadErr);
          continue;
        }
        const { data: urlData } = sb.storage
          .from("article-images")
          .getPublicUrl(path);
        if (urlData?.publicUrl) {
          photoUrls.push(urlData.publicUrl);
          if (!imageUrl) imageUrl = urlData.publicUrl;
        }
      }

      /* Insert */
      const row = {
        title: form.title.trim(),
        category: form.category,
        subcategory: form.subcategory || null,
        description: form.description.trim() || null,
        price: form.price.trim() || null,
        contact_name: form.contact_name.trim() || null,
        contact_email: form.contact_email.trim(),
        contact_phone: form.contact_phone.trim() || null,
        city: form.city.trim() || null,
        state: form.state || null,
        zip: form.zip.trim() || null,
        image_url: imageUrl,
        photos: photoUrls,
        slug,
        source: "user_submitted",
      };

      const { error: insertErr } = await sb.from("classifieds").insert([row]);
      if (insertErr) throw insertErr;

      setPublishedSlug(slug);
      setStep("done");
    } catch (err: any) {
      console.error("Publish error:", err);
      setError(err.message || "Something went wrong");
      setStep("preview");
    }
  };

  const liveUrl = `https://www.thevideshi.com/classifieds/${publishedSlug}`;
  const subcats = form.category ? SUBCATEGORIES[form.category] || [] : [];

  /* ---------------------------------------------------------------- */
  /* Render                                                           */
  /* ---------------------------------------------------------------- */
  return (
    <>
      <Helmet>
        <title>Post a Classified — The Videshi</title>
        <meta name="description" content="Post a classified ad for the Indian diaspora community — services, housing, items for sale, jobs, and more." />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container py-6">
        <div className="max-w-2xl mx-auto">
          {/* Back */}
          <Link
            to="/classifieds"
            className="inline-flex items-center gap-1 text-sm text-foreground/50 hover:text-primary mb-4"
          >
            <ChevronLeft className="h-4 w-4" /> Back to classifieds
          </Link>

          <h1 className="text-2xl font-bold font-serif mb-6">Post a Classified</h1>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* ============== FORM ============== */}
          {step === "form" && (
            <div className="space-y-5">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium mb-1.5">
                  Title <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={form.title}
                  onChange={set("title")}
                  placeholder="e.g. Looking for roommate in Sunnyvale"
                  className={inputClass}
                  maxLength={200}
                />
              </div>

              {/* Category + Subcategory */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5">
                    Category <span className="text-red-400">*</span>
                  </label>
                  <select
                    value={form.category}
                    onChange={set("category")}
                    className={inputClass}
                  >
                    <option value="">Select category</option>
                    {CLASSIFIED_CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {CATEGORY_ICONS[cat]} {cat}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5">Subcategory</label>
                  <select
                    value={form.subcategory}
                    onChange={set("subcategory")}
                    disabled={!subcats.length}
                    className={inputClass + " disabled:opacity-50"}
                  >
                    <option value="">Select subcategory</option>
                    {subcats.map((sub) => (
                      <option key={sub} value={sub}>{sub}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium mb-1.5">Description</label>
                <textarea
                  value={form.description}
                  onChange={set("description")}
                  rows={5}
                  placeholder="Describe what you're offering, looking for, or selling…"
                  className={inputClass + " resize-y"}
                />
              </div>

              {/* Price */}
              <div>
                <label className="block text-sm font-medium mb-1.5">Price</label>
                <input
                  type="text"
                  value={form.price}
                  onChange={set("price")}
                  placeholder='e.g. $500, Free, $25/hr, Negotiable'
                  className={inputClass}
                />
              </div>

              {/* Photos */}
              <div>
                <label className="block text-sm font-medium mb-1.5">
                  Photos <span className="text-foreground/40">(up to {MAX_PHOTOS})</span>
                </label>
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  multiple
                  className="hidden"
                  onChange={(e) => addImages(e.target.files)}
                />
                <div className="flex flex-wrap gap-3">
                  {images.map((img) => (
                    <div key={img.id} className="relative w-24 h-24 rounded-lg overflow-hidden border border-border">
                      <img src={img.url} alt="" className="w-full h-full object-cover" />
                      <button
                        onClick={() => removeImage(img.id)}
                        className="absolute top-1 right-1 p-0.5 rounded-full bg-black/60 text-white hover:bg-black/80"
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))}
                  {images.length < MAX_PHOTOS && (
                    <button
                      onClick={() => fileRef.current?.click()}
                      className="w-24 h-24 rounded-lg border-2 border-dashed border-border hover:border-primary/40 flex flex-col items-center justify-center gap-1 text-foreground/40 hover:text-primary/60 transition-colors"
                    >
                      <Upload className="h-5 w-5" />
                      <span className="text-xs">Add</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Location */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-sm font-medium mb-1.5">City</label>
                  <input
                    type="text"
                    value={form.city}
                    onChange={set("city")}
                    placeholder="City"
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5">State</label>
                  <select
                    value={form.state}
                    onChange={set("state")}
                    className={inputClass}
                  >
                    <option value="">State</option>
                    {US_STATES.map((s) => (
                      <option key={s} value={s}>{s} — {STATE_NAMES[s]}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5">ZIP</label>
                  <input
                    type="text"
                    value={form.zip}
                    onChange={set("zip")}
                    placeholder="ZIP"
                    maxLength={10}
                    className={inputClass}
                  />
                </div>
              </div>

              {/* Contact info */}
              <div className="space-y-4 border-t border-border pt-5">
                <h2 className="font-semibold">Your Contact Details</h2>
                <p className="text-sm text-foreground/40">
                  Your contact info is never shown publicly. Interested people will send inquiries through the platform, and you'll receive them at your email.
                </p>
                <div>
                  <label className="block text-sm font-medium mb-1.5">
                    Your Name
                    <span className="text-foreground/40 ml-1 font-normal">(never shown publicly)</span>
                  </label>
                  <input
                    type="text"
                    value={form.contact_name}
                    onChange={set("contact_name")}
                    placeholder="Full name"
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5">
                    Email <span className="text-red-400">*</span>
                    <span className="text-foreground/40 ml-1 font-normal">(for verification & receiving inquiries — never shown publicly)</span>
                  </label>
                  <input
                    type="email"
                    value={form.contact_email}
                    onChange={set("contact_email")}
                    placeholder="your@email.com"
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5">
                    Phone
                    <span className="text-foreground/40 ml-1 font-normal">(optional — for your records only, never shown publicly)</span>
                  </label>
                  <input
                    type="tel"
                    value={form.contact_phone}
                    onChange={set("contact_phone")}
                    placeholder="(555) 123-4567"
                    className={inputClass}
                  />
                </div>
              </div>

              {/* Turnstile */}
              <TurnstileWidget
                onVerify={(token) => setTurnstileToken(token)}
                onExpire={() => setTurnstileToken(null)}
                className="mb-2"
              />

              {/* Submit */}
              <button
                onClick={goPreview}
                disabled={!turnstileToken}
                className="w-full py-3 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Preview Listing
              </button>
            </div>
          )}

          {/* ============== PREVIEW ============== */}
          {(step === "preview" || step === "verify-email" || step === "verify-code" || step === "publishing") && (
            <div className="space-y-6">
              <p className="text-sm text-foreground/50">
                Review your listing before publishing:
              </p>

              {/* Preview card */}
              <div className="border border-border rounded-lg overflow-hidden bg-card">
                {images[0] && (
                  <div className="overflow-hidden">
                    <img
                      src={images[0].url}
                      alt="preview"
                      className="w-full max-h-64 object-contain bg-muted/10"
                    />
                  </div>
                )}
                <div className="p-4 space-y-2">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${CATEGORY_COLORS[form.category] || "bg-muted text-foreground/70"}`}>
                      {CATEGORY_ICONS[form.category]} {form.category}
                    </span>
                    {form.subcategory && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-muted/50 text-foreground/70">
                        {form.subcategory}
                      </span>
                    )}
                  </div>
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-semibold text-lg">{form.title}</h3>
                    {form.price && (
                      <span className="shrink-0 text-sm font-bold px-2.5 py-1 rounded-md bg-amber-100 text-amber-800">
                        {form.price}
                      </span>
                    )}
                  </div>
                  {form.description && (
                    <p className="text-sm text-foreground/60 line-clamp-3">{form.description}</p>
                  )}
                  <div className="flex items-center gap-3 text-xs text-foreground/50 pt-1">
                    {form.city && (
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {form.city}{form.state ? `, ${form.state}` : ""}
                      </span>
                    )}
                    <span>Just now</span>
                  </div>
                </div>
              </div>

              {/* Email verification section */}
              {(step === "verify-email" || step === "verify-code") && (
                <div className="border border-primary/30 rounded-lg p-5 bg-primary/5 space-y-4">
                  <h3 className="font-semibold">Verify your email</h3>

                  {step === "verify-email" && (
                    <>
                      <p className="text-sm text-foreground/60">
                        We'll send a 6-digit code to <strong>{form.contact_email}</strong> to verify your identity.
                      </p>
                      {verifySending && (
                        <div className="flex items-center gap-2 text-sm text-foreground/50">
                          <Loader2 className="h-4 w-4 animate-spin" /> Sending code…
                        </div>
                      )}
                      {verifyError && (
                        <p className="text-sm text-red-400">{verifyError}</p>
                      )}
                      <button
                        onClick={() => handleSendVerifyCode()}
                        disabled={verifySending}
                        className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
                      >
                        {verifySending ? "Sending…" : "Send Verification Code"}
                      </button>
                    </>
                  )}

                  {step === "verify-code" && (
                    <form onSubmit={handleCheckVerifyCode} className="space-y-3">
                      <p className="text-sm text-foreground/60">
                        Enter the 6-digit code we sent to <strong>{form.contact_email}</strong>
                      </p>
                      <div>
                        <label htmlFor="verify-code-input" className="block text-sm font-medium mb-1.5">
                          Verification Code
                        </label>
                        <input
                          id="verify-code-input"
                          type="text"
                          inputMode="numeric"
                          autoComplete="one-time-code"
                          value={verifyCode}
                          onChange={(e) => setVerifyCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                          placeholder="123456"
                          maxLength={6}
                          className={inputClass + " text-center text-lg tracking-widest font-mono"}
                        />
                      </div>
                      {verifyError && (
                        <p className="text-sm text-red-400">{verifyError}</p>
                      )}
                      <button
                        type="submit"
                        disabled={verifyChecking || verifyCode.length !== 6}
                        className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
                      >
                        {verifyChecking ? (
                          <span className="flex items-center justify-center gap-2">
                            <Loader2 className="h-4 w-4 animate-spin" /> Verifying & Publishing…
                          </span>
                        ) : (
                          "Verify & Publish"
                        )}
                      </button>
                    </form>
                  )}
                </div>
              )}

              {/* Buttons (only on initial preview) */}
              {step === "preview" && (
                <div className="flex gap-3">
                  <button
                    onClick={() => setStep("form")}
                    className="flex-1 py-3 rounded-lg border border-border font-medium hover:bg-muted/30 transition-colors"
                  >
                    ← Edit
                  </button>
                  <button
                    onClick={startVerify}
                    className="flex-1 py-3 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
                  >
                    Publish
                  </button>
                </div>
              )}

              {/* Publishing spinner */}
              {step === "publishing" && (
                <div className="flex flex-col items-center py-8 gap-4">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  <p className="text-foreground/60">Publishing your listing…</p>
                </div>
              )}
            </div>
          )}

          {/* ============== DONE ============== */}
          {step === "done" && (
            <div className="text-center py-12 space-y-5">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/10">
                <Check className="h-8 w-8 text-green-500" />
              </div>
              <h2 className="text-xl font-bold">Your listing is live!</h2>
              <p className="text-foreground/60 text-sm max-w-md mx-auto">
                It will stay active for 30 days. You can edit or delete it anytime using the email you provided.
              </p>
              <div className="flex items-center justify-center gap-2 bg-muted/30 rounded-lg px-4 py-2 max-w-md mx-auto">
                <span className="text-xs truncate flex-1 text-left">{liveUrl}</span>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(liveUrl);
                    setCopied(true);
                    setTimeout(() => setCopied(false), 2000);
                  }}
                  className="shrink-0 text-xs text-primary hover:underline"
                >
                  {copied ? "Copied!" : "Copy"}
                </button>
              </div>
              <div className="flex justify-center gap-3 pt-2">
                <Link
                  to={`/classifieds/${publishedSlug}`}
                  className="px-5 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
                >
                  View Your Listing
                </Link>
                <Link
                  to="/classifieds"
                  className="px-5 py-2.5 rounded-lg border border-border text-sm font-medium hover:bg-muted/30 transition-colors"
                >
                  Browse Classifieds
                </Link>
              </div>
            </div>
          )}
        </div>
      </main>

      <SiteFooter />
    </>
  );
}
