import { useState, useEffect, useRef, useCallback } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { supabase } from "@/integrations/supabase/client";
import { generateSlug, formatEventDateLong, EVENT_CATEGORIES } from "@/lib/events";
import TurnstileWidget from "@/components/TurnstileWidget";

/* ================================================================== */
/* Constants                                                          */
/* ================================================================== */

const MAX_FILE_SIZE = 5 * 1024 * 1024;
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];

const US_STATES = [
  "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
  "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
  "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
  "VA","WA","WV","WI","WY","DC",
] as const;

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

const CAT_EMOJI: Record<string, string> = {
  Cultural:"🎭", Music:"🎵", Food:"🍛", Sports:"🏏", Community:"🤝",
  Festival:"🪔", Comedy:"😂", Dance:"💃", Religious:"🙏", Education:"🎓",
  Competition:"🏆", Entertainment:"🎶", Other:"📌",
};

/* Category auto-detection from title */
const CATEGORY_KEYWORDS: [string[], string][] = [
  [["garba","dandiya","raas","bhangra","salsa","dance","nachle","kathak","bharatanatyam"], "Dance"],
  [["concert","music","dj ","bollywood night","karaoke","sangeet","live band","singing"], "Music"],
  [["comedy","standup","stand-up","open mic","improv","laugh"], "Comedy"],
  [["cricket","kabaddi","badminton","sports","marathon","5k","run ","tournament","yoga","fitness"], "Sports"],
  [["puja","pooja","temple","havan","satsang","kirtan","bhajan","prayer","diwali","navratri","holi","ganesh","eid","gurudwara","purnima"], "Religious"],
  [["food","cooking","biryani","dinner","brunch","tasting","culinary","potluck","chai"], "Food"],
  [["festival","mela","fair","carnival","utsav","fest ","mahotsav"], "Festival"],
  [["workshop","seminar","class","lecture","education","hackathon","bootcamp","webinar"], "Education"],
  [["meetup","networking","community","volunteer","fundraiser","charity"], "Community"],
  [["cultural","classical","theater","theatre","play ","drama","art ","exhibition"], "Cultural"],
];

function detectCategory(title: string): string | null {
  const t = ` ${title.toLowerCase()} `;
  for (const [kws, cat] of CATEGORY_KEYWORDS) {
    if (kws.some(k => t.includes(k))) return cat;
  }
  return null;
}

/* ================================================================== */
/* Form types                                                         */
/* ================================================================== */

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
  title: "", date: "", end_date: "", time: "",
  city: "", state: "", venue_name: "", category: "",
  ticket_url: "", description: "", email: "",
};

const STORAGE_KEY = "videshi_submit_event_draft";

type ImagePreview = { id: string; file: File; url: string };
function createPreview(file: File): ImagePreview {
  return { id: crypto.randomUUID(), file, url: URL.createObjectURL(file) };
}

/* ================================================================== */
/* Main component                                                     */
/* ================================================================== */

export default function SubmitEventPage() {
  /* ---- State ---- */
  const [form, setForm] = useState<FormData>(() => {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY);
      if (saved) return { ...INITIAL, ...JSON.parse(saved) };
    } catch { /* ignore */ }
    return INITIAL;
  });
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [showMultiDay, setShowMultiDay] = useState(!!form.end_date);
  const [showDetails, setShowDetails] = useState(false);
  const [showImageEmail, setShowImageEmail] = useState(false);
  const [stateSearch, setStateSearch] = useState("");
  const [stateOpen, setStateOpen] = useState(false);

  /* Steps: "form" | "synthesizing" | "preview" | "verify-email" | "verify-code" | "publishing" | "done" */
  const [step, setStep] = useState<"form" | "synthesizing" | "preview" | "verify-email" | "verify-code" | "publishing" | "done">("form");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [publishedSlug, setPublishedSlug] = useState<string | null>(null);

  /* Import state */
  const [importUrl, setImportUrl] = useState("");
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [importSuccess, setImportSuccess] = useState(false);
  const [importedImageUrl, setImportedImageUrl] = useState<string | null>(null);

  /* Turnstile */
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);

  /* Email verification */
  const [verifyCode, setVerifyCode] = useState("");
  const [verifySending, setVerifySending] = useState(false);
  const [verifyChecking, setVerifyChecking] = useState(false);
  const [verifyError, setVerifyError] = useState<string | null>(null);

  /* Image state */
  const [coverImage, setCoverImage] = useState<ImagePreview | null>(null);
  const [coverDragging, setCoverDragging] = useState(false);
  const coverInputRef = useRef<HTMLInputElement>(null);

  /* Synthesized content (run after submit, in background) */
  type SynthesizedContent = { long_description: string | null; artist_info: string | null; venue_info: string | null };
  const [synthesized, setSynthesized] = useState<SynthesizedContent | null>(null);

  /* ---- Auto-save to sessionStorage ---- */
  useEffect(() => {
    try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(form)); } catch { /* ignore */ }
  }, [form]);

  /* ---- Auto-expand sections when fields are filled ---- */
  useEffect(() => {
    if (form.title && form.date && (form.city || form.state)) setShowDetails(true);
  }, [form.title, form.date, form.city, form.state]);

  useEffect(() => {
    if (form.category || form.description) setShowImageEmail(true);
  }, [form.category, form.description]);

  /* ---- Auto-detect category from title ---- */
  useEffect(() => {
    if (form.category) return; // don't override manual selection
    const detected = detectCategory(form.title);
    if (detected) setForm(f => ({ ...f, category: detected }));
  }, [form.title, form.category]);

  /* ---- Field updater ---- */
  const updateField = useCallback((field: keyof FormData, value: string) => {
    setForm(f => ({ ...f, [field]: value }));
    if (errors[field]) setErrors(prev => ({ ...prev, [field]: undefined }));
  }, [errors]);

  const set = (field: keyof FormData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) => updateField(field, e.target.value);

  /* ---- URL import ---- */
  const handleImport = async () => {
    const url = importUrl.trim();
    if (!url) return;
    if (!/^https?:\/\/.+/.test(url)) {
      setImportError("Please paste a valid URL starting with http:// or https://");
      return;
    }
    setImporting(true);
    setImportError(null);
    setImportSuccess(false);
    try {
      const res = await fetch("/api/import-event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const json = await res.json();
      if (!json.success) {
        setImportError(json.error || "Could not extract event details.");
        setImporting(false);
        return;
      }
      const d = json.data;
      setForm(f => ({
        ...f,
        title: d.title || f.title,
        date: d.date || f.date,
        end_date: d.end_date || f.end_date,
        time: d.time || f.time,
        city: d.city || f.city,
        state: d.state || f.state,
        venue_name: d.venue_name || f.venue_name,
        category: d.category || f.category,
        ticket_url: d.ticket_url || f.ticket_url || url,
        description: (d.description || "").slice(0, 500) || f.description,
      }));
      if (d.end_date) setShowMultiDay(true);
      if (d.image_url) setImportedImageUrl(d.image_url);
      setImportSuccess(true);
      setShowDetails(true);
      setShowImageEmail(true);
    } catch {
      setImportError("Something went wrong. Please try entering details manually.");
    } finally {
      setImporting(false);
    }
  };

  /* ---- Cover image handlers ---- */
  const handleCoverSelect = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (!ACCEPTED_TYPES.includes(file.type)) return;
    if (file.size > MAX_FILE_SIZE) return;
    if (coverImage) URL.revokeObjectURL(coverImage.url);
    setCoverImage(createPreview(file));
    setImportedImageUrl(null);
  }, [coverImage]);

  const removeCover = useCallback(() => {
    if (coverImage) URL.revokeObjectURL(coverImage.url);
    setCoverImage(null);
    setImportedImageUrl(null);
    if (coverInputRef.current) coverInputRef.current.value = "";
  }, [coverImage]);

  /* ---- Drag handlers ---- */
  const dragHandlers = {
    onDragOver: (e: React.DragEvent) => { e.preventDefault(); setCoverDragging(true); },
    onDragEnter: (e: React.DragEvent) => { e.preventDefault(); setCoverDragging(true); },
    onDragLeave: () => setCoverDragging(false),
    onDrop: (e: React.DragEvent) => { e.preventDefault(); setCoverDragging(false); handleCoverSelect(e.dataTransfer.files); },
  };

  /* ---- Image upload helper ---- */
  async function uploadImage(file: File, slug: string): Promise<string | null> {
    const ext = file.name.split(".").pop() || "jpg";
    const path = `events/${slug}/cover-${Date.now()}.${ext}`;
    const sb = supabase as any;
    const { error } = await sb.storage.from("article-images").upload(path, file, {
      contentType: file.type,
      cacheControl: "31536000",
      upsert: false,
    });
    if (error) { console.error("Image upload error:", error); return null; }
    const { data } = sb.storage.from("article-images").getPublicUrl(path);
    return data?.publicUrl ?? null;
  }

  /* ---- Validate ---- */
  const validate = (): boolean => {
    const errs: Partial<Record<keyof FormData, string>> = {};
    if (!form.title.trim()) errs.title = "Event name is required";
    if (!form.date) errs.date = "Date is required";
    if (!form.city.trim()) errs.city = "City is required";
    if (!form.state) errs.state = "State is required";
    if (!form.email.trim()) errs.email = "Email is required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) errs.email = "Please enter a valid email";
    if (form.ticket_url && !/^https?:\/\/.+/.test(form.ticket_url.trim())) errs.ticket_url = "Enter a valid URL";
    if (form.end_date && form.end_date < form.date) errs.end_date = "End date must be after start date";
    setErrors(errs);
    // Auto-expand sections that have errors
    if (errs.category || errs.description || errs.ticket_url) setShowDetails(true);
    if (errs.email) setShowImageEmail(true);
    return Object.keys(errs).length === 0;
  };

  /* ---- Submit: verify turnstile → synthesize → preview ---- */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    if (!turnstileToken) { setSubmitError("Please complete the bot verification."); return; }

    try {
      const tRes = await fetch("/api/verify-turnstile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: turnstileToken }),
      });
      const tData = await tRes.json();
      if (!tData.success) { setSubmitError("Bot verification failed. Please try again."); setTurnstileToken(null); return; }
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
          title: form.title.trim(), date: form.date,
          end_date: form.end_date || null, time: form.time || null,
          city: form.city.trim(), state: form.state,
          venue_name: form.venue_name.trim(), category: form.category,
          description: form.description.trim(), ticket_url: form.ticket_url.trim() || null,
        },
      });
      if (error) throw error;
      setSynthesized({
        long_description: data?.long_description || form.description.trim() || null,
        artist_info: data?.artist_info || null,
        venue_info: data?.venue_info || null,
      });
    } catch {
      setSynthesized({
        long_description: form.description.trim() || null,
        artist_info: null, venue_info: null,
      });
    }
    setStep("preview");
  };

  /* ---- Email verification ---- */
  const handleSendVerifyCode = async () => {
    const email = form.email.trim().toLowerCase();
    if (!email) return;
    setVerifySending(true);
    setVerifyError(null);
    try {
      const { data, error } = await supabase.functions.invoke("send-email-verify", { body: { email } });
      if (error) throw new Error((data as any)?.error || error.message);
      if (data && !data.ok) throw new Error(data.error || "Failed");
      setStep("verify-code");
    } catch (err: any) {
      setVerifyError(err.message || "Something went wrong");
    } finally {
      setVerifySending(false);
    }
  };

  const handleCheckVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = verifyCode.trim();
    if (!code || code.length !== 6) { setVerifyError("Enter the 6-digit code"); return; }
    setVerifyChecking(true);
    setVerifyError(null);
    try {
      const { data, error } = await supabase.functions.invoke("verify-email-code", {
        body: { email: form.email.trim().toLowerCase(), code },
      });
      if (error) throw new Error((data as any)?.error || error.message);
      if (data && !data.verified) throw new Error(data.error || "Invalid code");
      await doPublish();
    } catch (err: any) {
      setVerifyError(err.message || "Invalid or expired code");
    } finally {
      setVerifyChecking(false);
    }
  };

  const handlePublish = () => {
    setVerifyError(null);
    setVerifyCode("");
    setStep("verify-email");
    handleSendVerifyCode();
  };

  /* ---- Actual publish ---- */
  const doPublish = async () => {
    setStep("publishing");
    setSubmitError(null);
    const slug = generateSlug(form.title.trim(), form.date);

    let imageUrl: string | null = importedImageUrl || null;
    if (coverImage) {
      const uploaded = await uploadImage(coverImage.file, slug);
      if (uploaded) imageUrl = uploaded;
    }

    const row: Record<string, unknown> = {
      title: form.title.trim(),
      date: form.date,
      end_date: form.end_date || null,
      time: form.time || null,
      city: form.city.trim(),
      state: form.state,
      venue_name: form.venue_name.trim() || null,
      category: form.category || "Other",
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

    const sbRaw = supabase as unknown as { from: (t: string) => any };
    const { error } = await sbRaw.from("events").insert([row]);
    if (error) {
      console.error("Submit event error:", error);
      setSubmitError("Something went wrong. Please try again.");
      setStep("preview");
      return;
    }

    setPublishedSlug(slug);
    sessionStorage.removeItem(STORAGE_KEY);

    /* Confirmation email (fire-and-forget) */
    try {
      await supabase.functions.invoke("send-event-confirmation", {
        body: {
          title: form.title.trim(), slug, email: form.email.trim(),
          date: form.date, venue: form.venue_name.trim(),
          city: `${form.city.trim()}, ${form.state}`,
        },
      });
    } catch { /* non-blocking */ }

    setStep("done");
  };

  /* ---- Filtered states for searchable picker ---- */
  const filteredStates = stateSearch
    ? US_STATES.filter(s => {
        const q = stateSearch.toLowerCase();
        return s.toLowerCase().includes(q) || (STATE_NAMES[s] || "").toLowerCase().includes(q);
      })
    : [...US_STATES];

  /* ---- Progress (how much is filled) ---- */
  const filledBasics = !!(form.title && form.date && form.city && form.state);
  const filledDetails = filledBasics && !!form.category;
  const filledAll = filledDetails && !!form.email;
  const progressPct = filledAll ? 100 : filledDetails ? 66 : filledBasics ? 33 : 0;

  /* ================================================================ */
  /* RENDER: Done                                                     */
  /* ================================================================ */
  if (step === "done") {
    const fullUrl = publishedSlug ? `thevideshi.com/events/${publishedSlug}` : "";
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Masthead /><CategoryPills />
        <main className="container flex-1 pt-8 pb-16 max-w-lg mx-auto px-4">
          <div className="text-center py-16">
            <p className="text-6xl mb-5">🎉</p>
            <h2 className="font-serif text-2xl md:text-3xl text-foreground mb-3">Your Event Is Live!</h2>
            <p className="text-muted-foreground mb-2">We've sent a confirmation to your email.</p>
            {publishedSlug && (
              <div className="flex items-center gap-2 mt-6 mb-8 max-w-sm mx-auto">
                <div className="flex-1 bg-muted/60 border border-border rounded-lg px-3 py-2.5 text-sm font-mono truncate text-left text-foreground/80">
                  {fullUrl}
                </div>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(`https://${fullUrl}`);
                    const b = document.getElementById("_cpbtn");
                    if (b) { b.textContent = "Copied!"; setTimeout(() => { b.textContent = "Copy"; }, 2000); }
                  }}
                  id="_cpbtn"
                  className="px-4 py-2.5 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors whitespace-nowrap"
                >Copy</button>
              </div>
            )}
            <div className="flex flex-col gap-3 max-w-xs mx-auto">
              {publishedSlug && (
                <Link to={`/events/${publishedSlug}`} className="block w-full px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-colors text-center">
                  View Your Event →
                </Link>
              )}
              <Link to="/events" className="block w-full px-6 py-3 border border-border rounded-xl font-medium hover:bg-muted/40 transition-colors text-center">
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
  /* RENDER: Preview + Verification                                   */
  /* ================================================================ */
  if (step === "preview" || step === "verify-email" || step === "verify-code" || step === "publishing") {
    const dateStr = formatEventDateLong(form.date, form.end_date || undefined);
    const catEmoji = CAT_EMOJI[form.category || "Other"] || "📌";
    const desc = synthesized?.long_description || form.description;
    const heroImg = coverImage?.url || importedImageUrl;

    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Helmet><title>Preview — The Videshi</title><meta name="robots" content="noindex" /></Helmet>
        <Masthead /><CategoryPills />

        <main className="container flex-1 pt-6 pb-20 max-w-2xl mx-auto px-4">
          <p className="text-sm text-primary font-medium mb-4 flex items-center gap-2">
            <span className="inline-block w-5 h-5 rounded-full bg-primary/10 text-center text-[11px] leading-5 font-bold">✓</span>
            Preview
          </p>

          {/* Event preview card */}
          <div className="rounded-2xl overflow-hidden bg-[#0a0a0a] text-white mb-6">
            {heroImg ? (
              <div className="w-full max-h-[40vh] overflow-hidden">
                <img src={heroImg} alt={form.title} className="w-full h-full object-contain bg-black" style={{ maxHeight: "40vh" }} />
              </div>
            ) : (
              <div className="w-full h-32 bg-gradient-to-br from-white/5 to-transparent flex items-center justify-center">
                <span className="text-7xl opacity-15 select-none">{catEmoji}</span>
              </div>
            )}
            <div className="px-5 sm:px-7 pb-7 -mt-2 relative z-10">
              <div className="flex flex-wrap items-center gap-2 mb-3 text-sm text-white/50">
                {form.category && <span className="text-white/40 uppercase tracking-widest text-xs font-medium">{catEmoji} {form.category}</span>}
                <span>·</span>
                <span>{dateStr}</span>
                {form.time && <><span>·</span><span>{form.time}</span></>}
              </div>
              <h2 className="font-serif text-xl sm:text-2xl md:text-3xl font-bold leading-tight mb-3">{form.title}</h2>
              {form.venue_name && <p className="text-white/50 text-sm mb-1">{form.venue_name}</p>}
              <p className="text-white/40 text-sm">{form.city}, {form.state}</p>
              {desc && (
                <>
                  <div className="h-px bg-white/10 my-5" />
                  <p className="text-white/70 text-sm leading-relaxed whitespace-pre-line">{desc}</p>
                </>
              )}
            </div>
          </div>

          {/* Verification UI */}
          {(step === "verify-email" || step === "verify-code") && (
            <div className="bg-muted/30 border border-border rounded-xl p-5 mb-5">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">✉️</span>
                <h3 className="font-medium text-foreground">Verify your email</h3>
              </div>
              {step === "verify-email" && (
                <>
                  <p className="text-sm text-muted-foreground">Sending a code to <strong>{form.email.trim()}</strong>…</p>
                  {verifySending && <Spinner className="mt-3" label="Sending code…" />}
                  {verifyError && <p className="text-sm text-red-600 mt-2">{verifyError}</p>}
                </>
              )}
              {step === "verify-code" && (
                <form onSubmit={handleCheckVerifyCode} className="mt-3">
                  <p className="text-sm text-muted-foreground mb-3">
                    Enter the 6-digit code sent to <strong>{form.email.trim()}</strong>
                  </p>
                  <input
                    type="text" inputMode="numeric" maxLength={6}
                    value={verifyCode}
                    onChange={e => { setVerifyCode(e.target.value.replace(/\D/g, "").slice(0, 6)); setVerifyError(null); }}
                    placeholder="000000"
                    className="w-full max-w-[200px] px-4 py-3 rounded-xl border border-border bg-background text-center text-2xl tracking-[0.3em] font-mono text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                    autoFocus
                  />
                  {verifyError && <p className="text-sm text-red-600 mt-2">{verifyError}</p>}
                  <button type="submit" disabled={verifyChecking || verifyCode.length !== 6}
                    className="mt-4 w-full py-3.5 bg-primary text-primary-foreground font-medium rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50">
                    {verifyChecking ? <Spinner label="Verifying…" /> : "Verify & Publish"}
                  </button>
                  <div className="mt-3 flex gap-4 text-sm">
                    <button type="button" onClick={handleSendVerifyCode} disabled={verifySending} className="text-primary hover:underline disabled:opacity-50">
                      Resend code
                    </button>
                    <button type="button" onClick={() => { setStep("preview"); setVerifyCode(""); setVerifyError(null); }} className="text-muted-foreground hover:text-foreground">
                      ← Back
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

          {submitError && <div className="rounded-xl bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm mb-4">{submitError}</div>}

          <div className="flex flex-col gap-3">
            <button onClick={() => { setStep("form"); setSubmitError(null); setVerifyError(null); setVerifyCode(""); }}
              disabled={step === "publishing"} className="w-full py-3.5 border border-border rounded-xl font-medium hover:bg-muted/40 transition-colors disabled:opacity-50">
              ✏️ Edit Details
            </button>
            {step === "preview" && (
              <button onClick={handlePublish} disabled={step === "publishing"}
                className="w-full py-3.5 bg-primary text-primary-foreground rounded-xl font-bold text-base hover:bg-primary/90 transition-colors disabled:opacity-50">
                ✅ Publish Event
              </button>
            )}
            {step === "publishing" && <Spinner label="Publishing your event…" className="py-4" />}
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
    <div className="min-h-screen flex flex-col bg-background">
      <Helmet>
        <title>Post an Event — The Videshi</title>
        <meta name="description" content="Post your Indian community event on The Videshi — concerts, festivals, temple events, and more." />
      </Helmet>

      <Masthead /><CategoryPills />

      <main className="container flex-1 pt-6 md:pt-8 pb-28 md:pb-16 max-w-lg mx-auto px-4">
        {/* Back link + header */}
        <Link to="/events" className="text-sm text-primary hover:underline mb-3 inline-block">← Events</Link>
        <h1 className="font-serif text-2xl md:text-3xl text-foreground mb-1">Post Your Event</h1>
        <p className="text-muted-foreground text-sm mb-6">Share an Indian community event with thousands of readers.</p>

        {/* Progress bar */}
        <div className="h-1 bg-muted/50 rounded-full mb-8 overflow-hidden">
          <div className="h-full bg-primary rounded-full transition-all duration-500 ease-out" style={{ width: `${progressPct}%` }} />
        </div>

        {/* ============ IMPORT SECTION ============ */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">🔗</span>
            <h2 className="font-medium text-foreground text-sm">Have an event link? Import it</h2>
          </div>
          <div className="flex gap-2">
            <input
              type="url"
              value={importUrl}
              onChange={e => { setImportUrl(e.target.value); setImportError(null); setImportSuccess(false); }}
              placeholder="Paste Eventbrite, Meetup, or any event URL…"
              className="flex-1 min-w-0 px-3.5 py-3 rounded-xl border border-border bg-background text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/40 transition-colors"
              onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); handleImport(); } }}
            />
            <button
              onClick={handleImport}
              disabled={importing || !importUrl.trim()}
              className="px-5 py-3 bg-primary text-primary-foreground font-medium text-sm rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50 whitespace-nowrap"
            >
              {importing ? <Spinner label="" size="sm" /> : "Import"}
            </button>
          </div>
          {importError && <p className="text-sm text-red-600 mt-2">{importError}</p>}
          {importSuccess && (
            <p className="text-sm text-green-600 mt-2 flex items-center gap-1">
              <span>✓</span> Details imported! Review and fill in anything missing below.
            </p>
          )}
        </div>

        <div className="h-px bg-border mb-8" />

        {/* ============ FORM ============ */}
        <form onSubmit={handleSubmit}>

          {/* ---- STEP 1: The Basics ---- */}
          <SectionHeader emoji="1️⃣" label="The Basics" />

          {/* Event name */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-foreground mb-1.5">
              Event Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={form.title}
              onChange={set("title")}
              placeholder='e.g. "Garba Night in Dallas"'
              className={inputClass(errors.title)}
            />
            {errors.title && <ErrMsg msg={errors.title} />}
            {form.title && detectCategory(form.title) && !errors.title && (
              <p className="text-xs text-primary/70 mt-1">
                Auto-detected: {CAT_EMOJI[detectCategory(form.title) || ""] || ""} {detectCategory(form.title)}
              </p>
            )}
          </div>

          {/* Date row */}
          <div className="grid grid-cols-2 gap-3 mb-2">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">
                Date <span className="text-red-500">*</span>
              </label>
              <input type="date" value={form.date} onChange={set("date")} className={inputClass(errors.date)} />
              {errors.date && <ErrMsg msg={errors.date} />}
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Time</label>
              <input type="time" value={form.time} onChange={set("time")} className={inputClass()} />
            </div>
          </div>

          {/* Multi-day toggle */}
          {!showMultiDay ? (
            <button type="button" onClick={() => setShowMultiDay(true)}
              className="text-xs text-primary hover:underline mb-4 inline-block">
              + Multi-day event?
            </button>
          ) : (
            <div className="mb-4 transition-all duration-300">
              <label className="block text-sm font-medium text-foreground mb-1.5">End Date</label>
              <input type="date" value={form.end_date} onChange={set("end_date")} className={inputClass(errors.end_date)} />
              {errors.end_date && <ErrMsg msg={errors.end_date} />}
            </div>
          )}

          {/* Location */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">
                City <span className="text-red-500">*</span>
              </label>
              <input type="text" value={form.city} onChange={set("city")} placeholder="e.g. Sunnyvale"
                className={inputClass(errors.city)} />
              {errors.city && <ErrMsg msg={errors.city} />}
            </div>
            <div className="relative">
              <label className="block text-sm font-medium text-foreground mb-1.5">
                State <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.state ? `${form.state} — ${STATE_NAMES[form.state] || ""}` : stateSearch}
                onChange={e => {
                  setStateSearch(e.target.value);
                  if (form.state) updateField("state", "");
                  setStateOpen(true);
                }}
                onFocus={() => setStateOpen(true)}
                placeholder="Search state…"
                className={inputClass(errors.state)}
                autoComplete="off"
              />
              {errors.state && <ErrMsg msg={errors.state} />}
              {stateOpen && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setStateOpen(false)} />
                  <div className="absolute z-20 mt-1 w-full max-h-48 overflow-y-auto bg-card border border-border rounded-xl shadow-lg">
                    {filteredStates.length === 0 ? (
                      <p className="px-3 py-2 text-sm text-muted-foreground">No match</p>
                    ) : filteredStates.map(s => (
                      <button key={s} type="button"
                        onClick={() => { updateField("state", s); setStateSearch(""); setStateOpen(false); }}
                        className="w-full text-left px-3 py-2.5 text-sm hover:bg-muted/60 transition-colors flex items-center gap-2">
                        <span className="font-medium text-foreground">{s}</span>
                        <span className="text-muted-foreground text-xs">{STATE_NAMES[s]}</span>
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Venue */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-foreground mb-1.5">Venue</label>
            <input type="text" value={form.venue_name} onChange={set("venue_name")}
              placeholder="e.g. Hindu Temple, Convention Center…" className={inputClass()} />
          </div>

          {/* ---- STEP 2: Details (expandable) ---- */}
          <div className={`transition-all duration-300 overflow-hidden ${showDetails ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"}`}>
            <SectionHeader emoji="2️⃣" label="Details" />

            {/* Category pills */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-foreground mb-2">Category</label>
              <div className="flex flex-wrap gap-2">
                {EVENT_CATEGORIES.map(cat => (
                  <button key={cat} type="button"
                    onClick={() => updateField("category", form.category === cat ? "" : cat)}
                    className={`inline-flex items-center gap-1 px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                      form.category === cat
                        ? "bg-primary text-primary-foreground shadow-sm scale-105"
                        : "bg-muted/60 text-foreground/70 hover:bg-muted active:scale-95"
                    }`}>
                    <span className="text-sm">{CAT_EMOJI[cat] || "📌"}</span>
                    {cat}
                  </button>
                ))}
              </div>
              {errors.category && <ErrMsg msg={errors.category} />}
            </div>

            {/* Description */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-foreground mb-1.5">Description</label>
              <textarea
                value={form.description}
                onChange={set("description")}
                placeholder="Tell people what to expect…"
                rows={3} maxLength={500}
                className={`${inputClass()} resize-none`}
              />
              <p className="text-xs text-muted-foreground mt-1 text-right">{form.description.length}/500</p>
            </div>

            {/* Ticket URL */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-foreground mb-1.5">Ticket / RSVP Link</label>
              <input type="url" value={form.ticket_url} onChange={set("ticket_url")}
                placeholder="https://…" className={inputClass(errors.ticket_url)} />
              {errors.ticket_url && <ErrMsg msg={errors.ticket_url} />}
            </div>
          </div>

          {/* Manual expand button for details */}
          {!showDetails && (
            <button type="button" onClick={() => setShowDetails(true)}
              className="w-full py-3 mb-6 text-sm text-primary font-medium rounded-xl border border-dashed border-primary/30 hover:bg-primary/5 transition-colors">
              + Add category, description & ticket link
            </button>
          )}

          {/* ---- STEP 3: Image & Email (expandable) ---- */}
          <div className={`transition-all duration-300 overflow-hidden ${showImageEmail ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"}`}>
            <SectionHeader emoji="3️⃣" label="Image & Contact" />

            {/* Cover image */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-foreground mb-1.5">Cover Image</label>
              <input ref={coverInputRef} type="file" accept="image/jpeg,image/png,image/webp" capture="environment"
                onChange={e => handleCoverSelect(e.target.files)} className="hidden" />

              {(coverImage || importedImageUrl) ? (
                <div className="relative inline-block w-full">
                  <img src={coverImage?.url || importedImageUrl || ""}
                    alt="Cover" className="w-full h-40 object-cover rounded-xl border border-border" />
                  <button type="button" onClick={removeCover}
                    className="absolute top-2 right-2 w-7 h-7 bg-black/60 text-white rounded-full flex items-center justify-center text-xs backdrop-blur-sm hover:bg-black/80">
                    ✕
                  </button>
                  {importedImageUrl && !coverImage && (
                    <span className="absolute bottom-2 left-2 text-xs bg-black/60 text-white px-2 py-0.5 rounded-full backdrop-blur-sm">
                      Imported
                    </span>
                  )}
                </div>
              ) : (
                <div
                  onClick={() => coverInputRef.current?.click()}
                  {...dragHandlers}
                  className={`flex flex-col items-center justify-center gap-2 py-8 rounded-xl border-2 border-dashed cursor-pointer transition-colors active:scale-[0.98] ${
                    coverDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                  }`}>
                  <span className="text-3xl">📷</span>
                  <span className="text-sm text-muted-foreground">Tap to add a photo</span>
                  <span className="text-xs text-muted-foreground/60">JPG, PNG, or WebP · Max 5 MB</span>
                </div>
              )}
            </div>

            {/* Email */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-foreground mb-1.5">
                Your Email <span className="text-red-500">*</span>
              </label>
              <input type="email" value={form.email} onChange={set("email")}
                placeholder="you@example.com" className={inputClass(errors.email)} />
              {errors.email && <ErrMsg msg={errors.email} />}
              <p className="text-xs text-muted-foreground mt-1">Not displayed publicly. Used for verification and confirmation.</p>
            </div>
          </div>

          {/* Manual expand for image+email */}
          {!showImageEmail && (
            <button type="button" onClick={() => setShowImageEmail(true)}
              className="w-full py-3 mb-6 text-sm text-primary font-medium rounded-xl border border-dashed border-primary/30 hover:bg-primary/5 transition-colors">
              + Add image & your email
            </button>
          )}

          {/* Turnstile + errors */}
          {submitError && step === "form" && (
            <div className="rounded-xl bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm mb-4">{submitError}</div>
          )}

          <div className="mb-4">
            <TurnstileWidget onVerify={t => setTurnstileToken(t)} onExpire={() => setTurnstileToken(null)} className="mb-2" />
          </div>

          {/* Submit button — sticky on mobile */}
          <div className="hidden md:block">
            <button type="submit" disabled={step === "synthesizing" || !turnstileToken}
              className="w-full py-3.5 bg-primary text-primary-foreground rounded-xl font-bold text-base hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              {step === "synthesizing" ? <Spinner label="Preparing preview…" /> : "Post Your Event →"}
            </button>
          </div>
        </form>
      </main>

      {/* Sticky mobile submit bar */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-background/95 backdrop-blur-md border-t border-border px-4 py-3 z-50">
        <button
          type="button"
          onClick={(e) => {
            // Trigger form submit
            const formEl = document.querySelector("form");
            if (formEl) formEl.requestSubmit();
          }}
          disabled={step === "synthesizing" || !turnstileToken}
          className="w-full py-3.5 bg-primary text-primary-foreground rounded-xl font-bold text-base hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {step === "synthesizing" ? <Spinner label="Preparing preview…" /> : "Post Your Event →"}
        </button>
      </div>

      <SiteFooter />
    </div>
  );
}

/* ================================================================== */
/* Helper components                                                  */
/* ================================================================== */

function SectionHeader({ emoji, label }: { emoji: string; label: string }) {
  return (
    <div className="flex items-center gap-2 mb-4 mt-2">
      <span className="text-base">{emoji}</span>
      <h2 className="text-sm font-semibold text-foreground uppercase tracking-wide">{label}</h2>
    </div>
  );
}

function ErrMsg({ msg }: { msg: string }) {
  return <p className="text-xs text-red-500 mt-1">{msg}</p>;
}

function Spinner({ label, className, size }: { label?: string; className?: string; size?: "sm" }) {
  const dim = size === "sm" ? "w-4 h-4" : "w-4 h-4";
  return (
    <span className={`inline-flex items-center gap-2 justify-center text-sm ${className || ""}`}>
      <span className={`inline-block ${dim} border-2 border-current border-t-transparent rounded-full animate-spin`} />
      {label}
    </span>
  );
}

function inputClass(error?: string): string {
  return `w-full px-3.5 py-3 rounded-xl border text-sm text-foreground bg-background placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 transition-colors min-h-[44px] ${
    error
      ? "border-red-400 focus:ring-red-300 focus:border-red-400"
      : "border-border focus:ring-primary/40 focus:border-primary/40"
  }`;
}
