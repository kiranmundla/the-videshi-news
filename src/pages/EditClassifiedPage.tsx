import { useState, useCallback, useRef, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { Link, useParams, useNavigate } from "react-router-dom";
import { Upload, X, ChevronLeft, Loader2, Trash2 } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { supabase } from "@/integrations/supabase/client";
import {
  Classified,
  getClassifiedBySlug,
  CLASSIFIED_CATEGORIES,
  CATEGORY_ICONS,
  SUBCATEGORIES,
} from "@/lib/classifieds";

const sb = supabase as any;

const MAX_PHOTOS = 10;
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

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

type Step = "loading" | "email" | "code" | "edit" | "deleted";

type FormData = {
  title: string;
  category: string;
  subcategory: string;
  description: string;
  price: string;
  contact_name: string;
  contact_phone: string;
  city: string;
  state: string;
  zip: string;
};

type NewImage = { id: string; file: File; url: string };
function createPreview(file: File): NewImage {
  return { id: crypto.randomUUID(), file, url: URL.createObjectURL(file) };
}

const inputClass =
  "w-full px-3 py-2.5 rounded-lg border border-border bg-card text-sm focus:outline-none focus:ring-2 focus:ring-primary/40";
const labelClass = "block text-sm font-medium mb-1.5";

export default function EditClassifiedPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const fileRef = useRef<HTMLInputElement>(null);

  const [item, setItem] = useState<Classified | null>(null);
  const [step, setStep] = useState<Step>("loading");
  const [email, setEmail] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [otpSending, setOtpSending] = useState(false);
  const [otpVerifying, setOtpVerifying] = useState(false);
  const [otpError, setOtpError] = useState<string | null>(null);
  const [form, setForm] = useState<FormData>({
    title: "", category: "", subcategory: "", description: "",
    price: "", contact_name: "", contact_phone: "",
    city: "", state: "", zip: "",
  });
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  /* ---- Photo state ---- */
  const [existingPhotos, setExistingPhotos] = useState<string[]>([]);
  const [newImages, setNewImages] = useState<NewImage[]>([]);
  // mainPhotoKey: either "existing:<url>" or "new:<id>" — null means first photo
  const [mainPhotoKey, setMainPhotoKey] = useState<string | null>(null);

  const totalPhotos = existingPhotos.length + newImages.length;

  /* Load item */
  useEffect(() => {
    if (!slug) return;
    getClassifiedBySlug(slug).then((data) => {
      if (data) {
        setItem(data);
        setForm({
          title: data.title || "",
          category: data.category || "",
          subcategory: data.subcategory || "",
          description: data.description || "",
          price: data.price || "",
          contact_name: data.contact_name || "",
          contact_phone: data.contact_phone || "",
          city: data.city || "",
          state: data.state || "",
          zip: data.zip || "",
        });
        // Load existing photos
        const photos = data.photos?.length ? data.photos : data.image_url ? [data.image_url] : [];
        setExistingPhotos(photos);
        // Mark the hero as main if it exists in photos
        if (data.image_url && photos.includes(data.image_url)) {
          setMainPhotoKey(`existing:${data.image_url}`);
        }
        setStep("email");
      } else {
        setStep("email");
      }
    });
  }, [slug]);

  const set = useCallback(
    (field: keyof FormData) =>
      (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        setForm((f) => ({ ...f, [field]: e.target.value }));
        if (field === "category") setForm((f) => ({ ...f, subcategory: "" }));
      },
    [],
  );

  /* ---- Photo handlers ---- */
  const addImages = useCallback(
    (files: FileList | null) => {
      if (!files) return;
      const newPreviews: NewImage[] = [];
      for (let i = 0; i < files.length && totalPhotos + newPreviews.length < MAX_PHOTOS; i++) {
        const f = files[i];
        if (!ACCEPTED_TYPES.includes(f.type)) continue;
        if (f.size > MAX_FILE_SIZE) continue;
        newPreviews.push(createPreview(f));
      }
      setNewImages((prev) => [...prev, ...newPreviews]);
    },
    [totalPhotos],
  );

  const removeExistingPhoto = useCallback((url: string) => {
    setExistingPhotos((prev) => prev.filter((p) => p !== url));
    setMainPhotoKey((cur) => (cur === `existing:${url}` ? null : cur));
  }, []);

  const removeNewImage = useCallback((id: string) => {
    setNewImages((prev) => {
      const img = prev.find((p) => p.id === id);
      if (img) URL.revokeObjectURL(img.url);
      return prev.filter((p) => p.id !== id);
    });
    setMainPhotoKey((cur) => (cur === `new:${id}` ? null : cur));
  }, []);

  /* Resolve which photo is main */
  const resolveMainKey = (): string | null => {
    if (mainPhotoKey) {
      // Make sure the main photo still exists
      if (mainPhotoKey.startsWith("existing:")) {
        const url = mainPhotoKey.slice("existing:".length);
        if (existingPhotos.includes(url)) return mainPhotoKey;
      } else if (mainPhotoKey.startsWith("new:")) {
        const id = mainPhotoKey.slice("new:".length);
        if (newImages.some((img) => img.id === id)) return mainPhotoKey;
      }
    }
    // Default to first available
    if (existingPhotos.length > 0) return `existing:${existingPhotos[0]}`;
    if (newImages.length > 0) return `new:${newImages[0].id}`;
    return null;
  };
  const effectiveMainKey = resolveMainKey();

  /* Send OTP */
  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!item) return;
    setOtpError(null);
    setOtpSending(true);
    try {
      const { data, error } = await sb.functions.invoke("send-classified-otp", {
        body: { classified_id: item.id, email: email.trim() },
      });
      if (error) throw new Error(data?.error || error.message || "Failed to send code");
      if (data && !data.ok) throw new Error(data.error || "Failed to send code");
      setStep("code");
    } catch (err: any) {
      setOtpError(err.message || "Something went wrong");
    } finally {
      setOtpSending(false);
    }
  };

  /* Verify OTP */
  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!item) return;
    setOtpError(null);
    setOtpVerifying(true);
    try {
      const { data, error } = await sb.functions.invoke("verify-classified-otp", {
        body: { classified_id: item.id, email: email.trim(), code: otpCode.trim() },
      });
      if (error) throw new Error(data?.error || error.message || "Verification failed");
      if (data && !data.verified) throw new Error(data.error || "Invalid code");
      setStep("edit");
    } catch (err: any) {
      setOtpError(err.message || "Invalid or expired code");
    } finally {
      setOtpVerifying(false);
    }
  };

  /* Save */
  const handleSave = async () => {
    if (!item) return;
    if (!form.title.trim()) { setError("Title is required"); return; }
    setSaving(true);
    setError(null);
    try {
      /* Upload new images */
      const uploadedUrls: string[] = [];
      const uploadSlug = item.slug || slug || "";
      for (const img of newImages) {
        const ext = img.file.name.split(".").pop() || "jpg";
        const path = `classifieds/${uploadSlug}/${img.id}.${ext}`;
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
        if (urlData?.publicUrl) uploadedUrls.push(urlData.publicUrl);
      }

      /* Build final photos array: existing (kept) + newly uploaded */
      const allPhotos = [...existingPhotos, ...uploadedUrls];

      /* Determine the main/hero image URL */
      let heroUrl: string | null = null;
      if (effectiveMainKey) {
        if (effectiveMainKey.startsWith("existing:")) {
          heroUrl = effectiveMainKey.slice("existing:".length);
        } else if (effectiveMainKey.startsWith("new:")) {
          const id = effectiveMainKey.slice("new:".length);
          const idx = newImages.findIndex((img) => img.id === id);
          if (idx >= 0 && idx < uploadedUrls.length) {
            // Map new image index to uploaded URL index
            // uploadedUrls order matches newImages order (sequential upload)
            heroUrl = uploadedUrls[idx];
          }
        }
      }
      if (!heroUrl && allPhotos.length > 0) heroUrl = allPhotos[0];

      /* Reorder: hero first */
      const orderedPhotos = heroUrl
        ? [heroUrl, ...allPhotos.filter((p) => p !== heroUrl)]
        : allPhotos;

      const { error: updateErr } = await sb
        .from("classifieds")
        .update({
          title: form.title.trim(),
          category: form.category,
          subcategory: form.subcategory || null,
          description: form.description.trim() || null,
          price: form.price.trim() || null,
          contact_name: form.contact_name.trim() || null,
          contact_phone: form.contact_phone.trim() || null,
          city: form.city.trim() || null,
          state: form.state || null,
          zip: form.zip.trim() || null,
          image_url: heroUrl,
          photos: orderedPhotos.length > 0 ? orderedPhotos : null,
          updated_at: new Date().toISOString(),
        })
        .eq("id", item.id);
      if (updateErr) throw updateErr;
      setSaved(true);
      setTimeout(() => navigate(`/classifieds/${item.slug}`), 1500);
    } catch (err: any) {
      setError(err.message || "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  /* Delete */
  const handleDelete = async () => {
    if (!item) return;
    if (!window.confirm("Are you sure you want to delete this listing? This cannot be undone.")) return;
    setDeleting(true);
    try {
      const { error: delErr } = await sb
        .from("classifieds")
        .update({ status: "deleted" })
        .eq("id", item.id);
      if (delErr) throw delErr;
      setStep("deleted");
    } catch (err: any) {
      setError(err.message || "Failed to delete");
      setDeleting(false);
    }
  };

  const subcats = form.category ? SUBCATEGORIES[form.category] || [] : [];

  return (
    <>
      <Helmet>
        <title>Edit Classified — The Videshi</title>
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container py-6">
        <div className="max-w-2xl mx-auto">
          <Link
            to={item ? `/classifieds/${item.slug}` : "/classifieds"}
            className="inline-flex items-center gap-1 text-sm text-foreground/50 hover:text-primary mb-4"
          >
            <ChevronLeft className="h-4 w-4" /> Back
          </Link>

          <h1 className="text-2xl font-bold font-serif mb-6">Edit / Delete Listing</h1>

          {/* Loading */}
          {step === "loading" && (
            <div className="flex justify-center py-16">
              <Loader2 className="h-6 w-6 animate-spin text-foreground/40" />
            </div>
          )}

          {/* Deleted */}
          {step === "deleted" && (
            <div className="text-center py-16 space-y-4">
              <p className="text-4xl">🗑️</p>
              <h2 className="text-xl font-bold">Listing Deleted</h2>
              <p className="text-foreground/50">Your listing has been removed.</p>
              <Link
                to="/classifieds"
                className="inline-flex items-center gap-1 text-primary hover:underline"
              >
                Browse classifieds
              </Link>
            </div>
          )}

          {/* Not found */}
          {step === "email" && !item && (
            <div className="text-center py-16 space-y-4">
              <p className="text-4xl">📋</p>
              <h2 className="text-xl font-bold">Listing Not Found</h2>
              <Link to="/classifieds" className="text-primary hover:underline">
                Browse classifieds
              </Link>
            </div>
          )}

          {/* Step 1: Email */}
          {step === "email" && item && (
            <form onSubmit={handleSendOtp} className="space-y-4 max-w-md">
              <p className="text-sm text-foreground/60">
                Enter the email you used when posting this listing. We'll send you a verification code.
              </p>
              <div>
                <label htmlFor="edit-email" className={labelClass}>Email</label>
                <input
                  id="edit-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className={inputClass}
                  required
                />
              </div>
              {otpError && <p className="text-sm text-red-400">{otpError}</p>}
              <button
                type="submit"
                disabled={otpSending || !email.trim()}
                className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                {otpSending ? (
                  <Loader2 className="h-4 w-4 animate-spin mx-auto" />
                ) : (
                  "Send Verification Code"
                )}
              </button>
            </form>
          )}

          {/* Step 2: Code */}
          {step === "code" && (
            <form onSubmit={handleVerifyOtp} className="space-y-4 max-w-md">
              <p className="text-sm text-foreground/60">
                Enter the 6-digit code we sent to <strong>{email}</strong>
              </p>
              <div>
                <label htmlFor="otp-code" className={labelClass}>Verification Code</label>
                <input
                  id="otp-code"
                  type="text"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                  placeholder="123456"
                  maxLength={6}
                  className={inputClass}
                  required
                />
              </div>
              {otpError && <p className="text-sm text-red-400">{otpError}</p>}
              <button
                type="submit"
                disabled={otpVerifying || otpCode.length !== 6}
                className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                {otpVerifying ? (
                  <Loader2 className="h-4 w-4 animate-spin mx-auto" />
                ) : (
                  "Verify"
                )}
              </button>
            </form>
          )}

          {/* Step 3: Edit form */}
          {step === "edit" && (
            <div className="space-y-5">
              {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                  {error}
                </div>
              )}

              {saved && (
                <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm">
                  ✓ Saved! Redirecting…
                </div>
              )}

              <div>
                <label className={labelClass}>Title</label>
                <input type="text" value={form.title} onChange={set("title")} className={inputClass} />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Category</label>
                  <select value={form.category} onChange={set("category")} className={inputClass}>
                    <option value="">Select</option>
                    {CLASSIFIED_CATEGORIES.map((c) => (
                      <option key={c} value={c}>{CATEGORY_ICONS[c]} {c}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className={labelClass}>Subcategory</label>
                  <select value={form.subcategory} onChange={set("subcategory")} disabled={!subcats.length} className={inputClass}>
                    <option value="">Select</option>
                    {subcats.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <label className={labelClass}>Description</label>
                <textarea value={form.description} onChange={set("description")} rows={5} className={inputClass + " resize-y"} />
              </div>

              <div>
                <label className={labelClass}>Price</label>
                <input type="text" value={form.price} onChange={set("price")} className={inputClass} />
              </div>

              {/* ---- Photos section ---- */}
              <div>
                <label className={labelClass}>
                  Photos <span className="text-foreground/40">(up to {MAX_PHOTOS})</span>
                </label>
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  multiple
                  className="hidden"
                  onChange={(e) => { addImages(e.target.files); if (fileRef.current) fileRef.current.value = ""; }}
                />
                <div className="flex flex-wrap gap-3">
                  {/* Existing photos */}
                  {existingPhotos.map((url) => {
                    const key = `existing:${url}`;
                    const isMain = effectiveMainKey === key;
                    return (
                      <div key={url} className="relative w-24 h-24 rounded-lg overflow-hidden border border-border group">
                        <img
                          src={url}
                          alt=""
                          className="w-full h-full object-cover cursor-pointer"
                          onClick={() => setMainPhotoKey(key)}
                        />
                        {isMain ? (
                          <span className="absolute bottom-0 left-0 right-0 bg-primary/90 text-white text-[10px] font-semibold text-center py-0.5 leading-tight">
                            ★ Main
                          </span>
                        ) : totalPhotos > 1 ? (
                          <span
                            className="absolute bottom-0 left-0 right-0 bg-black/60 text-white/70 text-[10px] text-center py-0.5 leading-tight opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                            onClick={(e) => { e.stopPropagation(); setMainPhotoKey(key); }}
                          >
                            Set as main
                          </span>
                        ) : null}
                        <button
                          type="button"
                          onClick={() => removeExistingPhoto(url)}
                          className="absolute top-1 right-1 p-0.5 rounded-full bg-black/60 text-white hover:bg-black/80"
                        >
                          <X className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    );
                  })}

                  {/* New images (not yet uploaded) */}
                  {newImages.map((img) => {
                    const key = `new:${img.id}`;
                    const isMain = effectiveMainKey === key;
                    return (
                      <div key={img.id} className="relative w-24 h-24 rounded-lg overflow-hidden border border-border group">
                        <img
                          src={img.url}
                          alt=""
                          className="w-full h-full object-cover cursor-pointer"
                          onClick={() => setMainPhotoKey(key)}
                        />
                        {isMain ? (
                          <span className="absolute bottom-0 left-0 right-0 bg-primary/90 text-white text-[10px] font-semibold text-center py-0.5 leading-tight">
                            ★ Main
                          </span>
                        ) : totalPhotos > 1 ? (
                          <span
                            className="absolute bottom-0 left-0 right-0 bg-black/60 text-white/70 text-[10px] text-center py-0.5 leading-tight opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                            onClick={(e) => { e.stopPropagation(); setMainPhotoKey(key); }}
                          >
                            Set as main
                          </span>
                        ) : null}
                        <button
                          type="button"
                          onClick={() => removeNewImage(img.id)}
                          className="absolute top-1 right-1 p-0.5 rounded-full bg-black/60 text-white hover:bg-black/80"
                        >
                          <X className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    );
                  })}

                  {/* Add button */}
                  {totalPhotos < MAX_PHOTOS && (
                    <button
                      type="button"
                      onClick={() => fileRef.current?.click()}
                      className="w-24 h-24 rounded-lg border-2 border-dashed border-border hover:border-primary/40 flex flex-col items-center justify-center gap-1 text-foreground/40 hover:text-primary/60 transition-colors"
                    >
                      <Upload className="h-5 w-5" />
                      <span className="text-xs">Add</span>
                    </button>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                <div className="col-span-2 sm:col-span-1">
                  <label className={labelClass}>City</label>
                  <input type="text" value={form.city} onChange={set("city")} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>State</label>
                  <select value={form.state} onChange={set("state")} className={inputClass}>
                    <option value="">State</option>
                    {US_STATES.map((s) => <option key={s} value={s}>{s} — {STATE_NAMES[s]}</option>)}
                  </select>
                </div>
                <div>
                  <label className={labelClass}>ZIP</label>
                  <input type="text" value={form.zip} onChange={set("zip")} maxLength={10} className={inputClass} />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>
                    Contact Name
                    <span className="text-foreground/40 ml-1 font-normal text-xs">(never shown publicly)</span>
                  </label>
                  <input type="text" value={form.contact_name} onChange={set("contact_name")} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>
                    Contact Phone
                    <span className="text-foreground/40 ml-1 font-normal text-xs">(never shown publicly)</span>
                  </label>
                  <input type="tel" value={form.contact_phone} onChange={set("contact_phone")} className={inputClass} />
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex-1 py-3 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                  {saving ? <Loader2 className="h-4 w-4 animate-spin mx-auto" /> : "Save Changes"}
                </button>
                <button
                  onClick={handleDelete}
                  disabled={deleting}
                  className="px-5 py-3 rounded-lg border border-red-500/30 text-red-400 font-medium hover:bg-red-500/10 transition-colors disabled:opacity-50"
                >
                  {deleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      <SiteFooter />
    </>
  );
}
