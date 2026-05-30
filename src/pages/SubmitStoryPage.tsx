import { useState, useRef } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import TurnstileWidget from "@/components/TurnstileWidget";
import { supabase } from "@/integrations/supabase/client";
import {
  STORY_CATEGORIES,
  YEARS_OPTIONS,
  getCategoryLabel,
  getCategoryEmoji,
} from "@/lib/stories";

const sb = supabase as any;
const MAX_PHOTO_SIZE = 5 * 1024 * 1024; // 5 MB
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];

type Step = "about" | "story" | "synthesizing" | "preview" | "verify" | "done";

function generateSlug(name: string): string {
  const base = name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 30)
    .replace(/-$/, "");
  return `${base}-${Math.random().toString(36).slice(2, 8)}`;
}

export default function SubmitStoryPage() {
  /* ── Step state ── */
  const [step, setStep] = useState<Step>("about");
  const [error, setError] = useState<string | null>(null);

  /* ── Step 1: About You ── */
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [city, setCity] = useState("");
  const [linkedin, setLinkedin] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const photoRef = useRef<HTMLInputElement>(null);

  /* ── Step 2: Your Story ── */
  const [category, setCategory] = useState("general");
  const [yearsInUs, setYearsInUs] = useState("");
  const [originCity, setOriginCity] = useState("");
  const [whatHappened, setWhatHappened] = useState("");
  const [howAffected, setHowAffected] = useState("");
  const [advice, setAdvice] = useState("");
  const [rawStory, setRawStory] = useState("");

  /* ── Turnstile ── */
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);

  /* ── Step 3: Preview ── */
  const [headline, setHeadline] = useState("");
  const [subheadline, setSubheadline] = useState("");
  const [body, setBody] = useState("");
  const [suspicionScore, setSuspicionScore] = useState(0);
  const [storyId, setStoryId] = useState<string | null>(null);
  const [storySlug, setStorySlug] = useState<string | null>(null);

  /* ── Step 4: Verify ── */
  const [otpCode, setOtpCode] = useState("");
  const [otpSending, setOtpSending] = useState(false);
  const [otpChecking, setOtpChecking] = useState(false);
  const [otpError, setOtpError] = useState<string | null>(null);

  /* ── Photo handling ── */
  function handlePhoto(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError("Please upload a JPG, PNG, or WebP image.");
      return;
    }
    if (file.size > MAX_PHOTO_SIZE) {
      setError("Photo must be under 5 MB.");
      return;
    }
    setError(null);
    setPhoto(file);
    setPhotoPreview(URL.createObjectURL(file));
  }

  /* ── Upload photo as base64 data URL (simple, no storage bucket needed) ── */
  async function uploadPhotoAsDataUrl(): Promise<string | null> {
    if (!photo) return null;
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result as string);
      reader.onerror = () => resolve(null);
      reader.readAsDataURL(photo);
    });
  }

  /* ── Step 1 → Step 2 ── */
  function handleStep1() {
    setError(null);
    if (!name.trim()) { setError("Please enter your name."); return; }
    if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("Please enter a valid email address.");
      return;
    }
    if (!photo) { setError("Please upload a photo — it makes your story personal."); return; }
    setStep("story");
  }

  /* ── Step 2 → Synthesize ── */
  async function handleStep2() {
    setError(null);
    if (!rawStory.trim() || rawStory.trim().length < 50) {
      setError("Please write at least a few sentences about your story.");
      return;
    }
    if (!turnstileToken) {
      setError("Please complete the bot verification.");
      return;
    }

    setStep("synthesizing");

    try {
      // 1. Upload photo
      const photoUrl = await uploadPhotoAsDataUrl();

      // 2. Create draft story in DB
      const slug = generateSlug(name);
      const { data: insertData, error: insertErr } = await sb
        .from("stories")
        .insert({
          author_name: name.trim(),
          author_email: email.trim().toLowerCase(),
          author_photo_url: photoUrl,
          author_city: city.trim() || null,
          author_linkedin: linkedin.trim() || null,
          category,
          raw_story: rawStory.trim(),
          prompt_what_happened: whatHappened.trim() || null,
          prompt_how_affected: howAffected.trim() || null,
          prompt_advice: advice.trim() || null,
          prompt_years_in_us: yearsInUs || null,
          prompt_origin_city: originCity.trim() || null,
          slug,
          status: "draft",
        })
        .select("id, slug")
        .single();

      if (insertErr) throw new Error(insertErr.message);
      setStoryId(insertData.id);
      setStorySlug(insertData.slug);

      // 3. Call synthesize edge function
      const { data: synthData, error: synthErr } = await sb.functions.invoke(
        "synthesize-story",
        {
          body: {
            raw_story: rawStory.trim(),
            author_name: name.trim(),
            category,
            prompt_what_happened: whatHappened.trim(),
            prompt_how_affected: howAffected.trim(),
            prompt_advice: advice.trim(),
            prompt_years_in_us: yearsInUs,
            prompt_origin_city: originCity.trim(),
            author_city: city.trim(),
          },
        }
      );

      if (synthErr) throw new Error(synthErr.message);

      const result = synthData;
      setHeadline(result.headline || "My Story");
      setSubheadline(result.subheadline || "");
      setBody(result.body || rawStory);
      setSuspicionScore(result.suspicion_score || 0);

      // 4. Update the story with synthesized content
      await sb
        .from("stories")
        .update({
          headline: result.headline,
          subheadline: result.subheadline,
          body: result.body,
          suspicion_score: result.suspicion_score || 0,
          updated_at: new Date().toISOString(),
        })
        .eq("id", insertData.id);

      setStep("preview");
    } catch (err: any) {
      console.error("Synthesis error:", err);
      setError(err.message || "Something went wrong. Please try again.");
      setStep("story");
    }
  }

  /* ── Preview → Send OTP ── */
  async function handleApprovePreview() {
    if (!storyId) return;
    setError(null);
    setOtpSending(true);

    try {
      // Save any edits the user made to headline/body
      await sb
        .from("stories")
        .update({
          headline,
          subheadline,
          body,
          updated_at: new Date().toISOString(),
        })
        .eq("id", storyId);

      // Send OTP
      const { error: otpErr } = await sb.functions.invoke("send-story-otp", {
        body: { story_id: storyId, email: email.trim().toLowerCase() },
      });

      if (otpErr) throw new Error(otpErr.message);
      setStep("verify");
    } catch (err: any) {
      setError(err.message || "Failed to send verification code.");
    } finally {
      setOtpSending(false);
    }
  }

  /* ── Verify OTP ── */
  async function handleVerifyOtp() {
    if (!storyId) return;
    setOtpError(null);
    setOtpChecking(true);

    try {
      const { data, error: verifyErr } = await sb.functions.invoke("verify-story-otp", {
        body: {
          story_id: storyId,
          email: email.trim().toLowerCase(),
          code: otpCode.trim(),
        },
      });

      if (verifyErr) throw new Error(verifyErr.message);
      if (data?.error) throw new Error(data.error);

      setStep("done");
    } catch (err: any) {
      setOtpError(err.message || "Invalid or expired code.");
    } finally {
      setOtpChecking(false);
    }
  }

  /* ── Rewrite handler ── */
  async function handleRewrite() {
    setStep("synthesizing");
    try {
      const { data: synthData, error: synthErr } = await sb.functions.invoke(
        "synthesize-story",
        {
          body: {
            raw_story: rawStory.trim(),
            author_name: name.trim(),
            category,
            prompt_what_happened: whatHappened.trim(),
            prompt_how_affected: howAffected.trim(),
            prompt_advice: advice.trim(),
            prompt_years_in_us: yearsInUs,
            prompt_origin_city: originCity.trim(),
            author_city: city.trim(),
          },
        }
      );

      if (synthErr) throw new Error(synthErr.message);

      setHeadline(synthData.headline || "My Story");
      setSubheadline(synthData.subheadline || "");
      setBody(synthData.body || rawStory);
      setSuspicionScore(synthData.suspicion_score || 0);
      setStep("preview");
    } catch (err: any) {
      setError(err.message || "Rewrite failed.");
      setStep("preview");
    }
  }

  /* ── Render ── */
  return (
    <>
      <Helmet>
        <title>Share Your Story | Diaspora Voices — The Videshi</title>
        <meta name="description" content="Share your personal story with the Indian diaspora community. We'll help you tell it beautifully." />
      </Helmet>

      <Masthead />
      <CategoryPills />

      <main className="container py-8 md:py-12 max-w-2xl mx-auto">
        {/* Progress bar */}
        <div className="flex items-center gap-2 mb-8">
          {["About You", "Your Story", "Preview", "Verify"].map((label, i) => {
            const stepIdx = { about: 0, story: 1, synthesizing: 2, preview: 2, verify: 3, done: 4 }[step] ?? 0;
            const isActive = i <= stepIdx;
            return (
              <div key={label} className="flex-1">
                <div className={`h-1.5 rounded-full transition-colors ${isActive ? "bg-primary" : "bg-muted"}`} />
                <p className={`text-xs mt-1 ${isActive ? "text-foreground font-medium" : "text-muted-foreground"}`}>{label}</p>
              </div>
            );
          })}
        </div>

        {/* ── Error banner ── */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════ */}
        {/* STEP 1: About You                                          */}
        {/* ════════════════════════════════════════════════════════════ */}
        {step === "about" && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h1 className="font-serif text-2xl md:text-3xl font-bold mb-2">Share Your Story</h1>
              <p className="text-muted-foreground">
                Let's start with a little about you. Don't worry, we'll help you tell your story beautifully.
              </p>
            </div>

            {/* Name */}
            <div>
              <label className="block text-sm font-medium mb-1.5">Your Name <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Priya Sharma"
                className="w-full px-4 py-3 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium mb-1.5">Email <span className="text-red-500">*</span></label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="priya@example.com"
                className="w-full px-4 py-3 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
              />
              <p className="text-xs text-muted-foreground mt-1">We'll send a verification code. Not displayed publicly.</p>
            </div>

            {/* Photo */}
            <div>
              <label className="block text-sm font-medium mb-1.5">Your Photo <span className="text-red-500">*</span></label>
              <p className="text-xs text-muted-foreground mb-2">A photo of you, your family, or something that represents your story.</p>
              {photoPreview ? (
                <div className="relative w-32 h-32 rounded-xl overflow-hidden border border-border">
                  <img src={photoPreview} alt="Preview" className="w-full h-full object-cover" />
                  <button
                    onClick={() => { setPhoto(null); setPhotoPreview(null); }}
                    className="absolute top-1 right-1 w-6 h-6 bg-black/60 text-white rounded-full flex items-center justify-center text-xs hover:bg-black/80"
                  >
                    ✕
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => photoRef.current?.click()}
                  className="w-full py-8 border-2 border-dashed border-border rounded-xl text-center hover:border-primary/40 transition-colors"
                >
                  <span className="text-3xl block mb-2">📷</span>
                  <span className="text-sm text-muted-foreground">Click to upload (JPG, PNG, WebP · max 5MB)</span>
                </button>
              )}
              <input ref={photoRef} type="file" accept="image/jpeg,image/png,image/webp" onChange={handlePhoto} className="hidden" />
            </div>

            {/* City */}
            <div>
              <label className="block text-sm font-medium mb-1.5">City you live in</label>
              <input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="e.g. San Francisco, CA"
                className="w-full px-4 py-3 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
              />
            </div>

            {/* LinkedIn */}
            <div>
              <label className="block text-sm font-medium mb-1.5">LinkedIn profile</label>
              <input
                type="url"
                value={linkedin}
                onChange={(e) => setLinkedin(e.target.value)}
                placeholder="https://linkedin.com/in/yourprofile"
                className="w-full px-4 py-3 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
              />
              <p className="text-xs text-muted-foreground mt-1">Optional — adds credibility to your story.</p>
            </div>

            <button
              onClick={handleStep1}
              className="w-full py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors"
            >
              Next: Your Story →
            </button>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════ */}
        {/* STEP 2: Your Story                                         */}
        {/* ════════════════════════════════════════════════════════════ */}
        {step === "story" && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h1 className="font-serif text-2xl md:text-3xl font-bold mb-2">Tell Us Your Story</h1>
              <p className="text-muted-foreground">
                Answer as many prompts as you'd like. The more details, the better we can tell your story.
              </p>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium mb-1.5">What's your story about? <span className="text-red-500">*</span></label>
              <div className="grid grid-cols-2 gap-2">
                {STORY_CATEGORIES.map((c) => (
                  <button
                    key={c.value}
                    onClick={() => setCategory(c.value)}
                    className={`px-3 py-2.5 rounded-lg border text-sm text-left transition-colors ${
                      category === c.value
                        ? "border-primary bg-primary/5 font-medium"
                        : "border-border hover:border-primary/30"
                    }`}
                  >
                    {c.emoji} {c.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Years in US */}
            <div>
              <label className="block text-sm font-medium mb-1.5">How long have you been in the US?</label>
              <select
                value={yearsInUs}
                onChange={(e) => setYearsInUs(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
              >
                <option value="">Select...</option>
                {YEARS_OPTIONS.map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>

            {/* Origin city */}
            <div>
              <label className="block text-sm font-medium mb-1.5">Where in India (or elsewhere) are you from?</label>
              <input
                type="text"
                value={originCity}
                onChange={(e) => setOriginCity(e.target.value)}
                placeholder="e.g. Hyderabad, Telangana"
                className="w-full px-4 py-3 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
              />
            </div>

            {/* What happened */}
            <div>
              <label className="block text-sm font-medium mb-1.5">What happened?</label>
              <p className="text-xs text-muted-foreground mb-1.5">2-3 sentences. The key event or experience at the heart of your story.</p>
              <textarea
                value={whatHappened}
                onChange={(e) => setWhatHappened(e.target.value)}
                rows={3}
                className="w-full px-4 py-3 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 resize-y"
                placeholder="e.g. I was stuck in India for 8 months because my H-1B visa appointment kept getting rescheduled..."
              />
            </div>

            {/* How affected */}
            <div>
              <label className="block text-sm font-medium mb-1.5">How did it affect you or your family?</label>
              <textarea
                value={howAffected}
                onChange={(e) => setHowAffected(e.target.value)}
                rows={3}
                className="w-full px-4 py-3 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 resize-y"
                placeholder="e.g. My kids had to switch schools, I nearly lost my job..."
              />
            </div>

            {/* Advice */}
            <div>
              <label className="block text-sm font-medium mb-1.5">What would you tell someone going through the same thing?</label>
              <textarea
                value={advice}
                onChange={(e) => setAdvice(e.target.value)}
                rows={2}
                className="w-full px-4 py-3 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 resize-y"
                placeholder="e.g. Keep all your documents ready, don't book flights until you have a confirmed appointment..."
              />
            </div>

            {/* Raw story */}
            <div>
              <label className="block text-sm font-medium mb-1.5">
                Tell us your story in your own words <span className="text-red-500">*</span>
              </label>
              <p className="text-xs text-muted-foreground mb-1.5">
                Don't worry about grammar or structure. Just write naturally — we'll help polish it.
              </p>
              <textarea
                value={rawStory}
                onChange={(e) => setRawStory(e.target.value)}
                rows={8}
                className="w-full px-4 py-3 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 resize-y"
                placeholder="Write freely here... your experience, your feelings, what you went through. It can be rough — we'll help make it shine."
              />
              <p className="text-xs text-muted-foreground mt-1 text-right">
                {rawStory.length} characters
              </p>
            </div>

            {/* Turnstile */}
            <TurnstileWidget
              onVerify={(token) => setTurnstileToken(token)}
              onExpire={() => setTurnstileToken(null)}
              className="flex justify-center"
            />

            <div className="flex gap-3">
              <button
                onClick={() => setStep("about")}
                className="px-6 py-3 border border-border rounded-lg text-sm font-medium hover:bg-muted transition-colors"
              >
                ← Back
              </button>
              <button
                onClick={handleStep2}
                disabled={!turnstileToken}
                className="flex-1 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                Preview My Story →
              </button>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════ */}
        {/* SYNTHESIZING                                               */}
        {/* ════════════════════════════════════════════════════════════ */}
        {step === "synthesizing" && (
          <div className="text-center py-20">
            <div className="w-12 h-12 border-3 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-6" />
            <h2 className="font-serif text-xl font-bold mb-2">Crafting your story...</h2>
            <p className="text-muted-foreground">
              Our AI is polishing your words while keeping your authentic voice. This takes about 10 seconds.
            </p>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════ */}
        {/* STEP 3: Preview                                            */}
        {/* ════════════════════════════════════════════════════════════ */}
        {step === "preview" && (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h1 className="font-serif text-2xl font-bold mb-2">Preview Your Story</h1>
              <p className="text-muted-foreground text-sm">
                This is how your story will look when published. You can edit anything before submitting.
              </p>
            </div>

            {/* Suspicion warning */}
            {suspicionScore > 70 && (
              <div className="p-4 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg text-amber-700 dark:text-amber-300 text-sm">
                ⚠️ We noticed some issues with your submission. Please make sure this is your genuine personal experience. Stories should be real and personal.
              </div>
            )}

            {/* Preview card */}
            <div className="border border-border rounded-xl overflow-hidden bg-card">
              {/* Author header */}
              <div className="p-6 flex items-center gap-4 border-b border-border">
                {photoPreview ? (
                  <img src={photoPreview} alt="" className="w-14 h-14 rounded-full object-cover" />
                ) : (
                  <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center text-xl font-bold text-primary">
                    {name[0]?.toUpperCase()}
                  </div>
                )}
                <div>
                  <p className="font-medium">{name}</p>
                  <p className="text-sm text-muted-foreground">
                    {city && `${city} · `}{getCategoryEmoji(category)} {getCategoryLabel(category)}
                  </p>
                </div>
              </div>

              {/* Headline (editable) */}
              <div className="p-6 pb-0">
                <input
                  type="text"
                  value={headline}
                  onChange={(e) => setHeadline(e.target.value)}
                  className="w-full font-serif text-2xl font-bold bg-transparent border-b border-dashed border-border pb-2 focus:outline-none focus:border-primary"
                />
              </div>

              {/* Subheadline (editable) */}
              <div className="px-6 pt-2">
                <input
                  type="text"
                  value={subheadline}
                  onChange={(e) => setSubheadline(e.target.value)}
                  placeholder="Subheadline..."
                  className="w-full text-muted-foreground italic bg-transparent border-b border-dashed border-border pb-2 text-sm focus:outline-none focus:border-primary"
                />
              </div>

              {/* Body (editable) */}
              <div className="p-6">
                <textarea
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  rows={16}
                  className="w-full bg-transparent text-sm leading-relaxed focus:outline-none resize-y border border-dashed border-border rounded-lg p-3 focus:border-primary"
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setStep("story")}
                className="px-4 py-3 border border-border rounded-lg text-sm font-medium hover:bg-muted transition-colors"
              >
                ← Edit Input
              </button>
              <button
                onClick={handleRewrite}
                className="px-4 py-3 border border-border rounded-lg text-sm font-medium hover:bg-muted transition-colors"
              >
                🔄 Rewrite
              </button>
              <button
                onClick={handleApprovePreview}
                disabled={otpSending}
                className="flex-1 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                {otpSending ? "Sending code..." : "Looks Good → Verify & Submit"}
              </button>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════ */}
        {/* STEP 4: Email Verification                                 */}
        {/* ════════════════════════════════════════════════════════════ */}
        {step === "verify" && (
          <div className="max-w-md mx-auto text-center space-y-6">
            <div>
              <span className="text-5xl block mb-4">📧</span>
              <h1 className="font-serif text-2xl font-bold mb-2">Check your email</h1>
              <p className="text-muted-foreground text-sm">
                We sent a 6-digit code to <strong>{email}</strong>. Enter it below to submit your story for review.
              </p>
            </div>

            <div>
              <input
                type="text"
                value={otpCode}
                onChange={(e) => {
                  const v = e.target.value.replace(/\D/g, "").slice(0, 6);
                  setOtpCode(v);
                  setOtpError(null);
                }}
                placeholder="000000"
                maxLength={6}
                className="w-48 mx-auto block text-center text-3xl tracking-[0.3em] font-mono px-4 py-3 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/40"
                autoFocus
              />
              {otpError && (
                <p className="text-red-500 text-sm mt-2">{otpError}</p>
              )}
            </div>

            <button
              onClick={handleVerifyOtp}
              disabled={otpCode.length !== 6 || otpChecking}
              className="w-full py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {otpChecking ? "Verifying..." : "Verify & Submit"}
            </button>

            <button
              onClick={handleApprovePreview}
              disabled={otpSending}
              className="text-sm text-muted-foreground underline hover:text-foreground transition-colors"
            >
              {otpSending ? "Sending..." : "Didn't get the code? Resend"}
            </button>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════ */}
        {/* DONE                                                       */}
        {/* ════════════════════════════════════════════════════════════ */}
        {step === "done" && (
          <div className="max-w-md mx-auto text-center space-y-6 py-8">
            <span className="text-6xl block">🎉</span>
            <h1 className="font-serif text-2xl font-bold">Story Submitted!</h1>
            <p className="text-muted-foreground leading-relaxed">
              Thank you for sharing your voice, <strong>{name.split(" ")[0]}</strong>. Your story has been submitted for review. We'll notify you at <strong>{email}</strong> when it's published.
            </p>
            <div className="bg-muted/30 border border-border rounded-xl p-5 text-sm text-muted-foreground leading-relaxed">
              <p className="font-medium text-foreground mb-1">What happens next?</p>
              <p>Our editorial team reviews every story to ensure quality and authenticity. Most stories are published within 24-48 hours.</p>
            </div>
            <div className="flex gap-3 justify-center">
              <Link
                to="/stories"
                className="px-6 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors text-sm"
              >
                Browse Stories
              </Link>
              <Link
                to="/"
                className="px-6 py-3 border border-border rounded-lg text-sm font-medium hover:bg-muted transition-colors"
              >
                Back to Home
              </Link>
            </div>
          </div>
        )}
      </main>

      <SiteFooter />
    </>
  );
}
