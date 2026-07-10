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
const STORAGE_KEY = "videshi_submit_event_draft";

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

/* City reverse-geocode from browser coords */
async function reverseGeoCity(lat: number, lng: number): Promise<{ city?: string; state?: string } | null> {
  try {
    const res = await fetch(`/api/geo?lat=${lat}&lng=${lng}`);
    if (!res.ok) return null;
    const data = await res.json();
    return { city: data.city || undefined, state: data.region || undefined };
  } catch {
    return null;
  }
}

/* ================================================================== */
/* Types                                                              */
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

const today = () => new Date().toISOString().slice(0, 10);

const INITIAL: FormData = {
  title: "", date: today(), end_date: "", time: "",
  city: "", state: "", venue_name: "", category: "",
  ticket_url: "", description: "", email: "",
};

type ImagePreview = { id: string; file: File; url: string };
function createPreview(file: File): ImagePreview {
  return { id: crypto.randomUUID(), file, url: URL.createObjectURL(file) };
}

type SynthesizedContent = { long_description: string | null; artist_info: string | null; venue_info: string | null };

/* ================================================================== */
/* Main component                                                     */
/* ================================================================== */

export default function SubmitEventPage() {
  /* ---- State ---- */
  const [mode, setMode] = useState<"post" | "manage">("post");
  const [form, setForm] = useState<FormData>(() => {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        return { ...INITIAL, ...parsed, date: parsed.date || today() };
      }
    } catch { /* ignore */ }
    return INITIAL;
  });
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [showMultiDay, setShowMultiDay] = useState(!!form.end_date);

  /* Steps */
  const [step, setStep] = useState<"form" | "synthesizing" | "preview" | "verify-email" | "verify-code" | "publishing" | "done">("form");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [publishedSlug, setPublishedSlug] = useState<string | null>(null);

  /* Import */
  const [importUrl, setImportUrl] = useState("");
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [importSuccess, setImportSuccess] = useState(false);
  const [importedImageUrl, setImportedImageUrl] = useState<string | null>(null);
  const [highlightFields, setHighlightFields] = useState<Set<string>>(new Set());

  /* Turnstile */
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);

  /* Email verification */
  const [verifyCode, setVerifyCode] = useState("");
  const [verifySending, setVerifySending] = useState(false);
  const [verifyChecking, setVerifyChecking] = useState(false);
  const [verifyError, setVerifyError] = useState<string | null>(null);

  /* Image */
  const [coverImage, setCoverImage] = useState<ImagePreview | null>(null);
  const [coverDragging, setCoverDragging] = useState(false);
  const coverInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  /* Synthesized content */
  const [synthesized, setSynthesized] = useState<SynthesizedContent | null>(null);

  /* State picker */
  const [stateSearch, setStateSearch] = useState("");
  const [stateOpen, setStateOpen] = useState(false);

  /* Geolocation status */
  const [geoAttempted, setGeoAttempted] = useState(false);

  /* Manage mode */
  const [manageEmail, setManageEmail] = useState("");
  const [manageStep, setManageStep] = useState<"email" | "otp" | "list">("email");
  const [manageOtp, setManageOtp] = useState("");
  const [manageSending, setManageSending] = useState(false);
  const [manageVerifying, setManageVerifying] = useState(false);
  const [manageError, setManageError] = useState<string | null>(null);
  const [myEvents, setMyEvents] = useState<any[]>([]);
  const [loadingEvents, setLoadingEvents] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  /* ---- Auto-save to sessionStorage ---- */
  useEffect(() => {
    try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(form)); } catch { /* ignore */ }
  }, [form]);

  /* ---- Geolocation pre-fill ---- */
  useEffect(() => {
    if (geoAttempted || form.city || form.state) return;
    setGeoAttempted(true);
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const geo = await reverseGeoCity(pos.coords.latitude, pos.coords.longitude);
        if (geo) {
          setForm(f => ({
            ...f,
            city: f.city || geo.city || "",
            state: f.state || geo.state || "",
          }));
        }
      },
      () => { /* denied — no problem */ },
      { timeout: 5000 },
    );
  }, [geoAttempted, form.city, form.state]);

  /* ---- Auto-detect category from title ---- */
  useEffect(() => {
    if (form.category) return;
    const detected = detectCategory(form.title);
    if (detected) setForm(f => ({ ...f, category: detected }));
  }, [form.title, form.category]);

  /* ---- Read URL mode param ---- */
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("mode") === "manage") setMode("manage");
  }, []);

  /* ---- Manage: Send OTP ---- */
  const handleManageSendOtp = async () => {
    const email = manageEmail.trim().toLowerCase();
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setManageError("Please enter a valid email");
      return;
    }
    setManageSending(true);
    setManageError(null);
    try {
      const { error } = await supabase.functions.invoke("send-email-verify", { body: { email } });
      if (error) throw error;
      setManageStep("otp");
    } catch (err: any) {
      setManageError(err.message || "Failed to send code");
    } finally {
      setManageSending(false);
    }
  };

  /* ---- Manage: Verify OTP & load events ---- */
  const handleManageVerifyOtp = async () => {
    const code = manageOtp.trim();
    if (code.length !== 6) return;
    setManageVerifying(true);
    setManageError(null);
    try {
      const { data, error } = await supabase.functions.invoke("verify-email-code", {
        body: { email: manageEmail.trim().toLowerCase(), code },
      });
      if (error) throw error;
      if (data && !data.verified) throw new Error(data.error || "Invalid code");
      setManageStep("list");
      await loadMyEvents();
    } catch (err: any) {
      setManageError(err.message || "Invalid code");
    } finally {
      setManageVerifying(false);
    }
  };

  /* ---- Manage: Load events for this email ---- */
  const loadMyEvents = async () => {
    setLoadingEvents(true);
    try {
      const sbRaw = supabase as unknown as { from: (t: string) => any };
      const { data, error } = await sbRaw
        .from("events")
        .select("id, title, date, end_date, time, city, state, category, image_url, slug, venue_name")
        .eq("organizer", manageEmail.trim().toLowerCase())
        .order("date", { ascending: false });
      if (error) throw error;
      setMyEvents(data || []);
    } catch {
      setManageError("Failed to load events");
    } finally {
      setLoadingEvents(false);
    }
  };

  /* ---- Manage: Delete event ---- */
  const handleDeleteEvent = async (id: string, title: string) => {
    if (!confirm(`Delete "${title}"? This can't be undone.`)) return;
    setDeletingId(id);
    try {
      const sbRaw = supabase as unknown as { from: (t: string) => any };
      const { error } = await sbRaw.from("events").delete().eq("id", id);
      if (error) throw error;
      setMyEvents(prev => prev.filter(e => e.id !== id));
    } catch (err: any) {
      setManageError(`Failed to delete: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  /* ---- Manage: Edit event (pre-fill form and switch to post mode) ---- */
  const handleEditEvent = (event: any) => {
    setForm({
      title: event.title || "",
      date: event.date || "",
      end_date: event.end_date || "",
      time: event.time || "",
      city: event.city || "",
      state: event.state || "",
      venue_name: event.venue_name || "",
      category: event.category || "",
      ticket_url: "",
      description: "",
      email: manageEmail.trim(),
    });
    setMode("post");
    setStep("form");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

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
    setHighlightFields(new Set());
    try {
      const res = await fetch("/api/import-event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const json = await res.json();
      if (!json.success) {
        setImportError(json.error || "Could not extract event details from that link.");
        setImporting(false);
        return;
      }
      const d = json.data;
      const filled = new Set<string>();
      const updates: Partial<FormData> = {};
      if (d.title) { updates.title = d.title; filled.add("title"); }
      if (d.date) { updates.date = d.date; filled.add("date"); }
      if (d.end_date) { updates.end_date = d.end_date; filled.add("end_date"); setShowMultiDay(true); }
      if (d.time) { updates.time = d.time; filled.add("time"); }
      if (d.city) { updates.city = d.city; filled.add("city"); }
      if (d.state) { updates.state = d.state; filled.add("state"); }
      if (d.venue_name) { updates.venue_name = d.venue_name; filled.add("venue_name"); }
      if (d.category) { updates.category = d.category; filled.add("category"); }
      if (d.ticket_url) { updates.ticket_url = d.ticket_url; filled.add("ticket_url"); }
      else if (!form.ticket_url) { updates.ticket_url = url; filled.add("ticket_url"); }
      if (d.description) { updates.description = (d.description || "").slice(0, 500); filled.add("description"); }
      if (d.image_url) setImportedImageUrl(d.image_url);

      setForm(f => ({ ...f, ...updates }));
      setHighlightFields(filled);
      setImportSuccess(true);

      // Clear highlight after animation
      setTimeout(() => setHighlightFields(new Set()), 2000);

      // Scroll to form
      setTimeout(() => {
        document.getElementById("event-form-section")?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 300);
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
    if (cameraInputRef.current) cameraInputRef.current.value = "";
  }, [coverImage]);

  /* Drag handlers */
  const dragHandlers = {
    onDragOver: (e: React.DragEvent) => { e.preventDefault(); setCoverDragging(true); },
    onDragEnter: (e: React.DragEvent) => { e.preventDefault(); setCoverDragging(true); },
    onDragLeave: () => setCoverDragging(false),
    onDrop: (e: React.DragEvent) => { e.preventDefault(); setCoverDragging(false); handleCoverSelect(e.dataTransfer.files); },
  };

  /* Image upload */
  async function uploadImage(file: File, slug: string): Promise<string | null> {
    const ext = file.name.split(".").pop() || "jpg";
    const path = `events/${slug}/cover-${Date.now()}.${ext}`;
    const sb = supabase as any;
    const { error } = await sb.storage.from("article-images").upload(path, file, {
      contentType: file.type, cacheControl: "31536000", upsert: false,
    });
    if (error) { console.error("Image upload error:", error); return null; }
    const { data } = sb.storage.from("article-images").getPublicUrl(path);
    return data?.publicUrl ?? null;
  }

  /* ---- Validate ---- */
  const validate = (): boolean => {
    const errs: Partial<Record<keyof FormData, string>> = {};
    if (!form.title.trim()) errs.title = "Give your event a name";
    if (!form.date) errs.date = "Pick a date";
    if (!form.city.trim()) errs.city = "Which city?";
    if (!form.state) errs.state = "Select a state";
    if (!form.email.trim()) errs.email = "We need your email to verify";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) errs.email = "That doesn't look like a valid email";
    if (form.ticket_url && !/^https?:\/\/.+/.test(form.ticket_url.trim())) errs.ticket_url = "Enter a valid URL starting with http://";
    if (form.end_date && form.end_date < form.date) errs.end_date = "End date should be after the start date";
    setErrors(errs);
    // Scroll to first error
    if (Object.keys(errs).length > 0) {
      const firstKey = Object.keys(errs)[0];
      document.getElementById(`field-${firstKey}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    return Object.keys(errs).length === 0;
  };

  /* ---- Submit → synthesize → preview ---- */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    if (!turnstileToken) { setSubmitError("Please complete the verification below."); return; }

    try {
      const tRes = await fetch("/api/verify-turnstile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: turnstileToken }),
      });
      const tData = await tRes.json();
      if (!tData.success) { setSubmitError("Verification failed — please try again."); setTurnstileToken(null); return; }
    } catch {
      setSubmitError("Verification failed — please try again.");
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

  /* ---- Publish ---- */
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

  /* ---- State picker helpers ---- */
  const filteredStates = stateSearch
    ? US_STATES.filter(s => {
        const q = stateSearch.toLowerCase();
        return s.toLowerCase().includes(q) || (STATE_NAMES[s] || "").toLowerCase().includes(q);
      })
    : [...US_STATES];

  /* ---- Progress ---- */
  const filledBasics = !!(form.title && form.date && form.city && form.state && form.email);
  const filledDetails = filledBasics && !!form.category;
  const filledAll = filledDetails;
  const currentStep = filledAll ? 3 : filledDetails ? 2 : filledBasics ? 2 : 1;

  /* Detect mobile */
  const isMobile = typeof window !== "undefined" && /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

  /* ================================================================ */
  /* RENDER: Done — Success state with event preview card             */
  /* ================================================================ */
  if (step === "done") {
    const dateStr = formatEventDateLong(form.date, form.end_date || undefined);
    const catEmoji = CAT_EMOJI[form.category || "Other"] || "📌";
    const heroImg = coverImage?.url || importedImageUrl;
    const fullUrl = publishedSlug ? `https://www.thevideshi.com/events/${publishedSlug}` : "";

    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Masthead /><CategoryPills />
        <main className="container flex-1 pt-8 pb-16 max-w-lg mx-auto px-4">
          <div className="text-center mb-8">
            <p className="text-6xl mb-4">🎉</p>
            <h2 className="font-serif text-2xl md:text-3xl text-foreground mb-2">Your Event Is Live!</h2>
            <p className="text-muted-foreground text-sm">Confirmation sent to <strong>{form.email}</strong>. You'll need this email to edit or delete your event.</p>
          </div>

          {/* Event preview card */}
          <div className="rounded-2xl overflow-hidden bg-card border border-border mb-6 shadow-sm">
            {heroImg ? (
              <div className="w-full h-44 overflow-hidden">
                <img src={heroImg} alt={form.title} className="w-full h-full object-cover" />
              </div>
            ) : (
              <div className="w-full h-28 bg-gradient-to-br from-primary/5 to-transparent flex items-center justify-center">
                <span className="text-5xl opacity-20 select-none">{catEmoji}</span>
              </div>
            )}
            <div className="px-5 py-4">
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">{catEmoji} {form.category || "Event"}</span>
                <span>·</span>
                <span>{dateStr}</span>
              </div>
              <h3 className="font-serif text-lg font-bold text-foreground mb-1 leading-snug">{form.title}</h3>
              {form.venue_name && <p className="text-sm text-muted-foreground">{form.venue_name}</p>}
              <p className="text-sm text-muted-foreground">{form.city}, {form.state}</p>
            </div>
          </div>

          {/* Share link */}
          {publishedSlug && (
            <div className="flex items-center gap-2 mb-6">
              <div className="flex-1 bg-muted/50 border border-border rounded-xl px-3.5 py-2.5 text-sm font-mono truncate text-foreground/70">
                {fullUrl.replace("https://", "")}
              </div>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(fullUrl);
                  const b = document.getElementById("_cpbtn");
                  if (b) { b.textContent = "Copied!"; setTimeout(() => { b.textContent = "Copy Link"; }, 2000); }
                }}
                id="_cpbtn"
                className="px-4 py-2.5 bg-primary text-primary-foreground text-sm font-medium rounded-xl hover:bg-primary/90 transition-colors whitespace-nowrap"
              >Copy Link</button>
            </div>
          )}

          {/* Share button */}
          {typeof navigator.share === "function" && (
            <button
              onClick={() => navigator.share({ title: form.title, url: fullUrl }).catch(() => {})}
              className="w-full py-3 mb-3 border border-border rounded-xl text-sm font-medium text-foreground hover:bg-muted/40 transition-colors flex items-center justify-center gap-2"
            >
              📤 Share This Event
            </button>
          )}

          <div className="flex flex-col gap-3">
            {publishedSlug && (
              <Link to={`/events/${publishedSlug}`} className="block w-full px-6 py-3.5 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-colors text-center">
                View Your Event →
              </Link>
            )}
            <button
              onClick={() => {
                setForm(INITIAL);
                setStep("form");
                setCoverImage(null);
                setImportedImageUrl(null);
                setImportUrl("");
                setImportSuccess(false);
                setPublishedSlug(null);
                setSynthesized(null);
                setTurnstileToken(null);
              }}
              className="w-full px-6 py-3 border border-border rounded-xl font-medium hover:bg-muted/40 transition-colors text-center"
            >
              + Post Another Event
            </button>
            <Link to="/events" className="block w-full px-6 py-3 text-sm text-muted-foreground hover:text-foreground transition-colors text-center">
              ← Back to Events
            </Link>
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
            <span className="inline-flex w-5 h-5 rounded-full bg-primary/10 items-center justify-center text-xs">✓</span>
            Here's how your event will look
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

          {/* Verification */}
          {(step === "verify-email" || step === "verify-code") && (
            <div className="bg-muted/30 border border-border rounded-xl p-5 mb-5">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">✉️</span>
                <h3 className="font-medium text-foreground">Quick email check</h3>
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
                    Enter the 6-digit code we sent to <strong>{form.email.trim()}</strong>
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
                Looks good — Publish! 🚀
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

  const hlClass = (field: string) => highlightFields.has(field) ? "ring-2 ring-green-400/60 bg-green-50/30 transition-all duration-700" : "";

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Helmet>
        <title>Post an Event — The Videshi</title>
        <meta name="description" content="Post your Indian community event on The Videshi — concerts, festivals, temple events, and more." />
      </Helmet>

      <Masthead /><CategoryPills />

      <main className="container flex-1 pt-6 md:pt-8 pb-32 md:pb-16 max-w-lg mx-auto px-4">
        {/* Back link */}
        <Link to="/events" className="text-sm text-primary hover:underline mb-4 inline-block">← Events</Link>

        {/* Mode toggle: Post / Manage */}
        <div className="flex bg-muted/40 rounded-xl p-1 mb-6">
          <button
            type="button"
            onClick={() => setMode("post")}
            className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              mode === "post" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Post Event
          </button>
          <button
            type="button"
            onClick={() => setMode("manage")}
            className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              mode === "manage" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Manage My Events
          </button>
        </div>

        {/* ============ MANAGE MODE ============ */}
        {mode === "manage" && (
          <div className="max-w-lg mx-auto">
            {manageStep === "email" && (
              <div className="rounded-2xl bg-gradient-to-b from-primary/[0.04] to-transparent border border-primary/10 p-6 md:p-8">
                <div className="text-center mb-5">
                  <p className="text-3xl mb-2">📋</p>
                  <h2 className="font-serif text-xl md:text-2xl text-foreground mb-1.5">Manage Your Events</h2>
                  <p className="text-muted-foreground text-sm">Enter the email you used when posting to find your events.</p>
                </div>
                <div className="space-y-3">
                  <input
                    type="email"
                    value={manageEmail}
                    onChange={e => { setManageEmail(e.target.value); setManageError(null); }}
                    placeholder="e.g. organizer@example.com"
                    className="w-full px-4 py-3.5 rounded-xl border border-border bg-background text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/40"
                    onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); handleManageSendOtp(); } }}
                    autoFocus
                  />
                  {manageError && <p className="text-sm text-red-600">{manageError}</p>}
                  <button
                    onClick={handleManageSendOtp}
                    disabled={manageSending || !manageEmail.trim()}
                    className="w-full py-3.5 bg-primary text-primary-foreground font-medium rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50"
                  >
                    {manageSending ? <Spinner label="Sending code…" /> : "Send Verification Code"}
                  </button>
                </div>
                <p className="text-xs text-muted-foreground mt-3 text-center">🔒 We'll send a code to verify it's you</p>
              </div>
            )}

            {manageStep === "otp" && (
              <div className="rounded-2xl bg-card border border-border p-6 md:p-8">
                <div className="text-center mb-5">
                  <h3 className="font-medium text-foreground mb-1">Enter verification code</h3>
                  <p className="text-sm text-muted-foreground">
                    We sent a 6-digit code to <strong>{manageEmail.trim()}</strong>
                  </p>
                </div>
                <div className="space-y-3">
                  <input
                    type="text"
                    inputMode="numeric"
                    maxLength={6}
                    value={manageOtp}
                    onChange={e => { setManageOtp(e.target.value.replace(/\D/g, "")); setManageError(null); }}
                    placeholder="000000"
                    className="w-full px-4 py-3.5 rounded-xl border border-border bg-background text-center text-lg font-mono tracking-[0.5em] text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                    autoFocus
                    onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); handleManageVerifyOtp(); } }}
                  />
                  {manageError && <p className="text-sm text-red-600 text-center">{manageError}</p>}
                  <button
                    onClick={handleManageVerifyOtp}
                    disabled={manageVerifying || manageOtp.length !== 6}
                    className="w-full py-3.5 bg-primary text-primary-foreground font-bold rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50"
                  >
                    {manageVerifying ? <Spinner label="Verifying…" /> : "Verify & View My Events"}
                  </button>
                  <div className="flex justify-center gap-4 text-sm pt-1">
                    <button type="button" onClick={handleManageSendOtp} disabled={manageSending} className="text-primary hover:underline disabled:opacity-50">
                      Resend code
                    </button>
                    <button type="button" onClick={() => { setManageStep("email"); setManageOtp(""); setManageError(null); }} className="text-muted-foreground hover:text-foreground">
                      ← Back
                    </button>
                  </div>
                </div>
              </div>
            )}

            {manageStep === "list" && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="font-serif text-xl text-foreground mb-0.5">Your Events</h2>
                    <p className="text-sm text-muted-foreground">{myEvents.length} event{myEvents.length !== 1 ? "s" : ""} found for {manageEmail.trim()}</p>
                  </div>
                  <button onClick={() => { setMode("post"); setForm(f => ({ ...f, email: manageEmail.trim() })); }}
                    className="px-3 py-1.5 text-sm font-medium text-primary border border-primary/30 hover:bg-primary/5 rounded-lg transition-colors">
                    + Post New
                  </button>
                </div>

                {loadingEvents && (
                  <div className="flex items-center justify-center py-12">
                    <Spinner label="Loading your events…" />
                  </div>
                )}

                {!loadingEvents && myEvents.length === 0 && (
                  <div className="text-center py-12 bg-muted/20 rounded-2xl">
                    <p className="text-3xl mb-2">📭</p>
                    <p className="text-muted-foreground mb-4">No events found for this email.</p>
                    <button onClick={() => { setMode("post"); setForm(f => ({ ...f, email: manageEmail.trim() })); }}
                      className="text-primary font-medium hover:underline">
                      Post your first event →
                    </button>
                  </div>
                )}

                {!loadingEvents && myEvents.map(event => {
                  const catEmoji = CAT_EMOJI[event.category || "Other"] || "📌";
                  const isPast = new Date(event.date) < new Date();
                  return (
                    <div key={event.id} className={`rounded-xl border border-border bg-card mb-3 overflow-hidden ${isPast ? "opacity-60" : ""}`}>
                      <div className="flex items-start gap-3 p-4">
                        {event.image_url ? (
                          <img src={event.image_url} alt="" className="w-16 h-16 rounded-lg object-cover flex-shrink-0" />
                        ) : (
                          <div className="w-16 h-16 rounded-lg bg-muted/40 flex items-center justify-center flex-shrink-0">
                            <span className="text-2xl">{catEmoji}</span>
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-foreground text-sm leading-snug line-clamp-2">{event.title}</h3>
                          <p className="text-xs text-muted-foreground mt-1">
                            {event.date} · {event.city}, {event.state}
                            {isPast && <span className="ml-2 text-xs bg-muted/60 px-1.5 py-0.5 rounded">Past</span>}
                          </p>
                        </div>
                      </div>
                      <div className="flex border-t border-border divide-x divide-border">
                        <button
                          onClick={() => handleEditEvent(event)}
                          className="flex-1 py-2.5 text-sm font-medium text-primary hover:bg-primary/5 transition-colors flex items-center justify-center gap-1.5"
                        >
                          ✏️ Edit
                        </button>
                        <button
                          onClick={() => handleDeleteEvent(event.id, event.title)}
                          disabled={deletingId === event.id}
                          className="flex-1 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20 transition-colors flex items-center justify-center gap-1.5 disabled:opacity-50"
                        >
                          {deletingId === event.id ? <Spinner label="Deleting…" size="sm" /> : "🗑️ Delete"}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ============ POST MODE ============ */}
        {mode === "post" && (<>

        {/* ============ HERO: Import Section ============ */}
        <div className="rounded-2xl bg-gradient-to-b from-primary/[0.04] to-transparent border border-primary/10 p-6 md:p-8 mb-8">
          <div className="text-center mb-5">
            <p className="text-3xl mb-2">🔗</p>
            <h1 className="font-serif text-xl md:text-2xl text-foreground mb-1.5">Already listed somewhere?</h1>
            <p className="text-muted-foreground text-sm">Paste the link and we'll fill everything in for you.</p>
          </div>

          <div className="flex gap-2">
            <input
              type="url"
              value={importUrl}
              onChange={e => { setImportUrl(e.target.value); setImportError(null); setImportSuccess(false); }}
              placeholder="e.g. https://eventbrite.com/e/garba-night..."
              className="flex-1 min-w-0 px-4 py-3.5 rounded-xl border border-border bg-background text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/40 transition-colors"
              onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); handleImport(); } }}
              onPaste={() => { setTimeout(handleImport, 100); }}
            />
            <button
              onClick={handleImport}
              disabled={importing || !importUrl.trim()}
              className="px-5 py-3.5 bg-primary text-primary-foreground font-medium text-sm rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50 whitespace-nowrap"
            >
              {importing ? <Spinner size="sm" /> : "Import"}
            </button>
          </div>

          {importing && (
            <div className="mt-4 flex items-center gap-2 text-sm text-primary">
              <span className="inline-block w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              ✨ Importing event details…
            </div>
          )}
          {importError && <p className="text-sm text-red-600 mt-3">{importError}</p>}
          {importSuccess && (
            <p className="text-sm text-green-600 mt-3 flex items-center gap-1.5">
              <span className="inline-flex w-5 h-5 rounded-full bg-green-100 items-center justify-center text-xs">✓</span>
              Got it! Review the details below and hit post.
            </p>
          )}
        </div>

        {/* Divider */}
        <div className="flex items-center gap-3 mb-8">
          <div className="h-px bg-border flex-1" />
          <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">or fill it in yourself</span>
          <div className="h-px bg-border flex-1" />
        </div>

        {/* ============ Progress Dots ============ */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {[1, 2, 3].map(s => (
            <div key={s} className={`flex items-center gap-1.5 ${s <= currentStep ? "text-primary" : "text-muted-foreground/40"}`}>
              <div className={`w-2.5 h-2.5 rounded-full transition-colors duration-300 ${
                s < currentStep ? "bg-primary" : s === currentStep ? "bg-primary/60" : "bg-muted-foreground/20"
              }`} />
              <span className="text-xs font-medium hidden sm:inline">
                {s === 1 ? "Basics" : s === 2 ? "Details" : "Finish"}
              </span>
            </div>
          ))}
        </div>

        {/* ============ FORM ============ */}
        <form onSubmit={handleSubmit} id="event-form-section">

          {/* ---- STEP 1: The Basics ---- */}
          <div className="mb-8">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-5 flex items-center gap-2">
              <span className="inline-flex w-5 h-5 rounded-full bg-primary/10 text-primary items-center justify-center text-xs font-bold">1</span>
              The basics
            </h2>

            {/* Event name */}
            <div className="mb-5" id="field-title">
              <label className="block text-sm font-medium text-foreground mb-1.5">
                What's your event called? <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                value={form.title}
                onChange={set("title")}
                placeholder='e.g. "Garba Night 2026"'
                className={`${inputClass(errors.title)} ${hlClass("title")}`}
                autoFocus={!importSuccess}
              />
              {errors.title && <ErrMsg msg={errors.title} />}
              {form.title && detectCategory(form.title) && !errors.title && (
                <p className="text-xs text-primary/70 mt-1.5 flex items-center gap-1 animate-fadeIn">
                  ✨ Auto-detected: {CAT_EMOJI[detectCategory(form.title) || ""] || ""} {detectCategory(form.title)}
                </p>
              )}
            </div>

            {/* Date + Time */}
            <div className="grid grid-cols-2 gap-3 mb-2">
              <div id="field-date">
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  When is it? <span className="text-red-400">*</span>
                </label>
                <input type="date" value={form.date} onChange={set("date")} className={`${inputClass(errors.date)} ${hlClass("date")}`} />
                {errors.date && <ErrMsg msg={errors.date} />}
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">What time?</label>
                <input type="time" value={form.time} onChange={set("time")} className={`${inputClass()} ${hlClass("time")}`} />
              </div>
            </div>

            {/* Multi-day toggle */}
            {!showMultiDay ? (
              <button type="button" onClick={() => setShowMultiDay(true)}
                className="text-xs text-primary/70 hover:text-primary mb-5 inline-block transition-colors">
                + It's a multi-day event
              </button>
            ) : (
              <div className="mb-5 animate-fadeIn" id="field-end_date">
                <label className="block text-sm font-medium text-foreground mb-1.5">Ends on</label>
                <input type="date" value={form.end_date} onChange={set("end_date")} className={`${inputClass(errors.end_date)} ${hlClass("end_date")}`} />
                {errors.end_date && <ErrMsg msg={errors.end_date} />}
              </div>
            )}

            {/* Location */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div id="field-city">
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  City <span className="text-red-400">*</span>
                </label>
                <input type="text" value={form.city} onChange={set("city")} placeholder="e.g. Sunnyvale"
                  className={`${inputClass(errors.city)} ${hlClass("city")}`} />
                {errors.city && <ErrMsg msg={errors.city} />}
              </div>
              <div className="relative" id="field-state">
                <label className="block text-sm font-medium text-foreground mb-1.5">
                  State <span className="text-red-400">*</span>
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
                  className={`${inputClass(errors.state)} ${hlClass("state")}`}
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
            <div className="mb-5">
              <label className="block text-sm font-medium text-foreground mb-1.5">Venue name</label>
              <input type="text" value={form.venue_name} onChange={set("venue_name")}
                placeholder="e.g. Hindu Temple of Silicon Valley" className={`${inputClass()} ${hlClass("venue_name")}`} />
            </div>

            {/* Email — in Step 1 because it's the ownership key */}
            <div className="mb-2" id="field-email">
              <label className="block text-sm font-medium text-foreground mb-1.5">
                Your email <span className="text-red-400">*</span>
              </label>
              <input type="email" value={form.email} onChange={set("email")}
                placeholder="e.g. organizer@example.com" className={`${inputClass(errors.email)} ${hlClass("email")}`} />
              {errors.email && <ErrMsg msg={errors.email} />}
              <p className="text-xs text-muted-foreground mt-1.5">🔒 You'll need this to edit or delete your event later — never shared publicly</p>
            </div>
          </div>

          {/* ---- STEP 2: Details ---- */}
          <div className={`mb-8 transition-all duration-500 ${filledBasics || importSuccess ? "opacity-100" : "opacity-40 pointer-events-none"}`}>
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-5 flex items-center gap-2">
              <span className="inline-flex w-5 h-5 rounded-full bg-primary/10 text-primary items-center justify-center text-xs font-bold">2</span>
              Add some details
            </h2>

            {/* Category pills */}
            <div className="mb-5">
              <label className="block text-sm font-medium text-foreground mb-2">What kind of event?</label>
              <div className="flex flex-wrap gap-2">
                {EVENT_CATEGORIES.map(cat => (
                  <button key={cat} type="button"
                    onClick={() => updateField("category", form.category === cat ? "" : cat)}
                    className={`inline-flex items-center gap-1 px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                      form.category === cat
                        ? "bg-primary text-primary-foreground shadow-sm scale-105"
                        : "bg-muted/60 text-foreground/70 hover:bg-muted active:scale-95"
                    } ${highlightFields.has("category") && form.category === cat ? "ring-2 ring-green-400/60" : ""}`}>
                    <span className="text-sm">{CAT_EMOJI[cat] || "📌"}</span>
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Description */}
            <div className="mb-5">
              <label className="block text-sm font-medium text-foreground mb-1.5">Tell people what to expect</label>
              <textarea
                value={form.description}
                onChange={set("description")}
                placeholder="e.g. Join us for an evening of garba and dandiya with live dhol, food stalls, and henna artists…"
                rows={3} maxLength={500}
                className={`${inputClass()} resize-none ${hlClass("description")}`}
              />
              <p className="text-xs text-muted-foreground mt-1 text-right">{form.description.length}/500</p>
            </div>

            {/* Ticket URL */}
            <div className="mb-2">
              <label className="block text-sm font-medium text-foreground mb-1.5">Ticket or RSVP link</label>
              <input type="url" value={form.ticket_url} onChange={set("ticket_url")}
                placeholder="e.g. https://eventbrite.com/..." className={`${inputClass(errors.ticket_url)} ${hlClass("ticket_url")}`} />
              {errors.ticket_url && <ErrMsg msg={errors.ticket_url} />}
            </div>
          </div>

          {/* ---- STEP 3: Image & Contact ---- */}
          <div className={`mb-8 transition-all duration-500 ${filledBasics || importSuccess ? "opacity-100" : "opacity-40 pointer-events-none"}`}>
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-5 flex items-center gap-2">
              <span className="inline-flex w-5 h-5 rounded-full bg-primary/10 text-primary items-center justify-center text-xs font-bold">3</span>
              Almost done
            </h2>

            {/* Cover image */}
            <div className="mb-5">
              <label className="block text-sm font-medium text-foreground mb-1.5">Add a photo</label>

              {/* Hidden file inputs */}
              <input ref={coverInputRef} type="file" accept="image/jpeg,image/png,image/webp"
                onChange={e => handleCoverSelect(e.target.files)} className="hidden" />
              <input ref={cameraInputRef} type="file" accept="image/*" capture="environment"
                onChange={e => handleCoverSelect(e.target.files)} className="hidden" />

              {(coverImage || importedImageUrl) ? (
                <div className="relative inline-block w-full">
                  <img src={coverImage?.url || importedImageUrl || ""}
                    alt="Cover" className="w-full h-40 object-cover rounded-xl border border-border" />
                  <button type="button" onClick={removeCover}
                    className="absolute top-2 right-2 w-8 h-8 bg-black/60 text-white rounded-full flex items-center justify-center text-sm backdrop-blur-sm hover:bg-black/80 transition-colors">
                    ✕
                  </button>
                  {importedImageUrl && !coverImage && (
                    <span className="absolute bottom-2 left-2 text-xs bg-black/60 text-white px-2 py-0.5 rounded-full backdrop-blur-sm">
                      Imported from link
                    </span>
                  )}
                </div>
              ) : isMobile ? (
                /* Mobile: separate camera + gallery buttons */
                <div className="flex gap-3">
                  <button type="button" onClick={() => cameraInputRef.current?.click()}
                    className="flex-1 flex flex-col items-center gap-1.5 py-5 rounded-xl border-2 border-dashed border-border hover:border-primary/50 active:scale-[0.98] transition-all">
                    <span className="text-2xl">📷</span>
                    <span className="text-xs text-muted-foreground font-medium">Take a photo</span>
                  </button>
                  <button type="button" onClick={() => coverInputRef.current?.click()}
                    className="flex-1 flex flex-col items-center gap-1.5 py-5 rounded-xl border-2 border-dashed border-border hover:border-primary/50 active:scale-[0.98] transition-all">
                    <span className="text-2xl">🖼️</span>
                    <span className="text-xs text-muted-foreground font-medium">Choose from gallery</span>
                  </button>
                </div>
              ) : (
                /* Desktop: drag & drop */
                <div
                  onClick={() => coverInputRef.current?.click()}
                  {...dragHandlers}
                  className={`flex flex-col items-center justify-center gap-2 py-8 rounded-xl border-2 border-dashed cursor-pointer transition-colors active:scale-[0.99] ${
                    coverDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                  }`}>
                  <span className="text-3xl">📷</span>
                  <span className="text-sm text-muted-foreground">Click to upload or drag & drop</span>
                  <span className="text-xs text-muted-foreground/60">JPG, PNG, or WebP · Max 5 MB</span>
                </div>
              )}
              <p className="text-xs text-muted-foreground mt-1.5">Optional — events with photos get 3× more views</p>
            </div>

{/* Email moved to Step 1 */}
          </div>

          {/* Turnstile */}
          {submitError && step === "form" && (
            <div className="rounded-xl bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm mb-4">{submitError}</div>
          )}

          <div className="mb-4">
            <TurnstileWidget onVerify={t => setTurnstileToken(t)} onExpire={() => setTurnstileToken(null)} className="mb-2" />
          </div>

          {/* Desktop submit */}
          <div className="hidden md:block">
            <button type="submit" disabled={step === "synthesizing" || !turnstileToken}
              className="w-full py-3.5 bg-primary text-primary-foreground rounded-xl font-bold text-base hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              {step === "synthesizing" ? <Spinner label="Preparing preview…" /> : "Post Your Event →"}
            </button>
          </div>
        </form>

        </>)}
      </main>

      {/* Sticky mobile submit — only in post mode */}
      {mode === "post" && (
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-background/95 backdrop-blur-md border-t border-border px-4 py-3 z-50">
        <button
          type="button"
          onClick={() => {
            const formEl = document.querySelector("form");
            if (formEl) formEl.requestSubmit();
          }}
          disabled={step === "synthesizing" || !turnstileToken}
          className="w-full py-3.5 bg-primary text-primary-foreground rounded-xl font-bold text-base hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {step === "synthesizing" ? <Spinner label="Preparing preview…" /> : "Post Your Event →"}
        </button>
      </div>
      )}

      <SiteFooter />

      {/* Inline animation styles */}
      <style>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
        .animate-fadeIn { animation: fadeIn 0.3s ease-out; }
      `}</style>
    </div>
  );
}

/* ================================================================== */
/* Helper components                                                  */
/* ================================================================== */

function ErrMsg({ msg }: { msg: string }) {
  return <p className="text-xs text-red-500 mt-1 flex items-center gap-1">⚠ {msg}</p>;
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
  return `w-full px-3.5 py-3 rounded-xl border text-sm text-foreground bg-background placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 transition-all duration-300 min-h-[44px] ${
    error
      ? "border-red-400 focus:ring-red-300 focus:border-red-400"
      : "border-border focus:ring-primary/40 focus:border-primary/40"
  }`;
}
