import { useState, useEffect, useCallback, useMemo } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { ChevronRight, CheckCircle, Clock, MapPin, Send, AlertTriangle } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import TurnstileWidget from "@/components/TurnstileWidget";

import {
  type ConsulateWaitRow,
  getConsulateWaitTimes,
  formatWaitMonths,
  waitColor,
  INDIA_CONSULATES,
  CONSULATE_DISPLAY,
} from "@/lib/immigration";

import {
  type VisaSighting,
  getVisaSightings,
  relativeTime,
  CONSULATES,
  CONSULATE_LABELS,
  VISA_TYPES,
  CONSULATE_COLORS,
} from "@/lib/visas";
import { supabase } from "@/integrations/supabase/client";

/* ------------------------------------------------------------------ */
/* Compact Wait-Time Strip (reuses immigration.ts data)               */
/* ------------------------------------------------------------------ */
function WaitTimeStrip({ data }: { data: ConsulateWaitRow[] }) {
  const grouped: Record<string, Record<string, ConsulateWaitRow>> = {};
  for (const row of data) {
    if (!INDIA_CONSULATES.includes(row.consulate as any)) continue;
    if (!grouped[row.consulate]) grouped[row.consulate] = {};
    if (!grouped[row.consulate][row.visa_type]) grouped[row.consulate][row.visa_type] = row;
  }

  const consulates = INDIA_CONSULATES.filter((c) => grouped[c]);
  consulates.sort((a, b) => {
    const aW = grouped[a]?.["B1B2"]?.next_available_months ?? 99;
    const bW = grouped[b]?.["B1B2"]?.next_available_months ?? 99;
    return aW - bW;
  });

  if (consulates.length === 0) return null;

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-border bg-blue-500/5">
        <div className="flex items-center gap-2">
          <span className="text-lg">🏛️</span>
          <h3 className="font-serif font-bold text-[15px]">Official Wait Times — India Consulates</h3>
        </div>
        <span className="text-[11px] text-foreground/50">via US State Dept</span>
      </div>
      <div className="divide-y divide-border">
        {consulates.map((c) => {
          const b1b2 = grouped[c]?.["B1B2"];
          const hlop = grouped[c]?.["H_L_O_P_Q"];
          const fmj = grouped[c]?.["F_M_J"];
          const b1Val = b1b2?.next_available_months ?? b1b2?.avg_wait_months ?? null;
          const hlVal = hlop?.next_available_months ?? null;
          const fmVal = fmj?.next_available_months ?? null;
          return (
            <div key={c} className="flex items-center justify-between px-4 py-2 hover:bg-foreground/[0.02] transition-colors">
              <div className="flex items-center gap-2.5">
                <div
                  className={`w-2 h-2 rounded-full ${
                    b1Val === null
                      ? "bg-gray-400"
                      : b1Val < 2
                        ? "bg-green-500"
                        : b1Val < 5
                          ? "bg-yellow-500"
                          : b1Val < 8
                            ? "bg-orange-500"
                            : "bg-red-500"
                  }`}
                />
                <span className="font-semibold text-sm">{CONSULATE_DISPLAY[c] || c}</span>
              </div>
              <div className="flex items-center gap-5 text-sm">
                <div className="text-right">
                  <span className={`font-mono font-semibold ${waitColor(b1Val)}`}>{formatWaitMonths(b1Val)}</span>
                  <p className="text-[10px] text-foreground/40 leading-tight">B1/B2</p>
                </div>
                <div className="text-right">
                  <span className={`font-mono font-semibold ${waitColor(hlVal)}`}>{formatWaitMonths(hlVal)}</span>
                  <p className="text-[10px] text-foreground/40 leading-tight">H/L/O/P</p>
                </div>
                <div className="text-right hidden sm:block">
                  <span className={`font-mono font-semibold ${waitColor(fmVal)}`}>{formatWaitMonths(fmVal)}</span>
                  <p className="text-[10px] text-foreground/40 leading-tight">F/M/J</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <Link
        to="/immigration/consulate-wait-times"
        className="flex items-center justify-center gap-1 px-4 py-2 text-sm text-primary font-medium border-t border-border hover:bg-primary/5 transition-colors"
      >
        Compare all consulates incl. third-country <ChevronRight className="h-4 w-4" />
      </Link>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Sighting Card                                                      */
/* ------------------------------------------------------------------ */
function SightingCard({ s }: { s: VisaSighting }) {
  const colors = CONSULATE_COLORS[s.consulate] ?? { bg: "bg-gray-500/10", text: "text-gray-600", border: "border-gray-500/20" };
  const dateRange =
    s.slots_date_start && s.slots_date_end
      ? `${new Date(s.slots_date_start).toLocaleDateString("en-US", { month: "short", day: "numeric" })} – ${new Date(s.slots_date_end).toLocaleDateString("en-US", { month: "short", day: "numeric" })}`
      : s.slots_date_start
        ? new Date(s.slots_date_start).toLocaleDateString("en-US", { month: "short", day: "numeric" })
        : null;

  return (
    <article className="bg-card border border-border rounded-xl p-4 hover:border-primary/30 transition-all duration-200 hover:shadow-md">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full ${colors.bg} ${colors.text} border ${colors.border}`}>
            <MapPin className="h-3 w-3" />
            {CONSULATE_LABELS[s.consulate] || s.consulate}
          </span>
          <span className="inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full bg-foreground/5 text-foreground/70">
            {s.visa_type}
          </span>
          {s.verified && (
            <span className="inline-flex items-center gap-0.5 text-[10px] font-bold uppercase tracking-wider text-green-600">
              <CheckCircle className="h-3 w-3" /> Verified
            </span>
          )}
        </div>
        <span className="text-[11px] text-foreground/40 whitespace-nowrap flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {relativeTime(s.created_at)}
        </span>
      </div>

      {dateRange && (
        <p className="text-xs font-semibold text-primary/80 mb-1.5">
          📅 Slots seen: {dateRange}
        </p>
      )}

      <p className="text-sm text-foreground/80 leading-relaxed">{s.description}</p>

      <p className="text-xs text-foreground/40 mt-2">
        🙏 <span className="font-medium text-foreground/60">{s.reporter_name}</span> · Thank you for spotting
      </p>
    </article>
  );
}

/* ------------------------------------------------------------------ */
/* Report Form (with OTP email verification)                          */
/* ------------------------------------------------------------------ */
function ReportForm({ onSubmitted }: { onSubmitted: () => void }) {
  const [consulate, setConsulate] = useState("");
  const [visaType, setVisaType] = useState("");
  const [dateStart, setDateStart] = useState("");
  const [dateEnd, setDateEnd] = useState("");
  const [description, setDescription] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // OTP state
  const [step, setStep] = useState<"form" | "otp">("form");
  const [otpCode, setOtpCode] = useState("");
  const [otpSending, setOtpSending] = useState(false);
  const [otpResendCooldown, setOtpResendCooldown] = useState(0);

  const isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
  const canSubmit = consulate && visaType && description.trim() && name.trim() && email.trim() && isValidEmail && turnstileToken && !submitting;

  // Cooldown timer
  useEffect(() => {
    if (otpResendCooldown <= 0) return;
    const t = setTimeout(() => setOtpResendCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [otpResendCooldown]);

  const sendOtp = async () => {
    setOtpSending(true);
    setError(null);
    try {
      const { data, error: fnErr } = await supabase.functions.invoke("send-sighting-otp", {
        body: { email: email.trim().toLowerCase() },
      });
      if (fnErr) throw new Error(fnErr.message || "Failed to send code");
      if (data?.error) throw new Error(data.error);
      setStep("otp");
      setOtpResendCooldown(60);
    } catch (e: any) {
      setError(e.message || "Failed to send verification code");
    } finally {
      setOtpSending(false);
    }
  };

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    await sendOtp();
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (otpCode.length !== 6) return;

    setSubmitting(true);
    setError(null);

    try {
      const { data, error: fnErr } = await supabase.functions.invoke("verify-sighting-otp", {
        body: {
          email: email.trim().toLowerCase(),
          code: otpCode,
          sighting_data: {
            consulate,
            visa_type: visaType,
            slots_date_start: dateStart || null,
            slots_date_end: dateEnd || null,
            description: description.trim(),
            reporter_name: name.trim(),
          },
        },
      });
      if (fnErr) throw new Error(fnErr.message || "Verification failed");
      if (data?.error) throw new Error(data.error);

      setSuccess(true);
      setStep("form");
      setOtpCode("");
      setConsulate("");
      setVisaType("");
      setDateStart("");
      setDateEnd("");
      setDescription("");
      onSubmitted();
      setTimeout(() => setSuccess(false), 5000);
    } catch (e: any) {
      setError(e.message || "Invalid or expired code");
    } finally {
      setSubmitting(false);
    }
  };

  const fieldClass =
    "w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors";

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <div className="px-5 py-4 border-b border-border bg-green-500/5">
        <h3 className="font-serif font-bold text-lg flex items-center gap-2">
          🛂 Report a Sighting
        </h3>
        <p className="text-sm text-foreground/60 mt-1">
          Saw open slots on <a href="https://www.usvisascheduling.com/" target="_blank" rel="noopener noreferrer" className="text-primary underline underline-offset-2 hover:text-primary/80">usvisascheduling.com</a>? Help the community by sharing what you found.
        </p>
      </div>

      <div className="p-5 space-y-4">
        {success && (
          <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-lg px-4 py-3 text-green-700 text-sm font-medium">
            <CheckCircle className="h-4 w-4 flex-shrink-0" />
            Sighting published — thank you! 🎉
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 text-red-700 text-sm">
            <AlertTriangle className="h-4 w-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {step === "form" ? (
          <form onSubmit={handleSendOtp} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
                  Consulate <span className="text-red-500">*</span>
                </label>
                <select value={consulate} onChange={(e) => setConsulate(e.target.value)} className={fieldClass} required>
                  <option value="">Select consulate…</option>
                  {CONSULATES.map((c) => (
                    <option key={c} value={c}>{CONSULATE_LABELS[c]}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
                  Visa Type <span className="text-red-500">*</span>
                </label>
                <select value={visaType} onChange={(e) => setVisaType(e.target.value)} className={fieldClass} required>
                  <option value="">Select type…</option>
                  {VISA_TYPES.map((v) => (
                    <option key={v} value={v}>{v}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
                  Slots From
                </label>
                <input type="date" value={dateStart} onChange={(e) => setDateStart(e.target.value)} className={fieldClass} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
                  Slots To
                </label>
                <input type="date" value={dateEnd} onChange={(e) => setDateEnd(e.target.value)} className={fieldClass} />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
                What did you see? <span className="text-red-500">*</span>
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                placeholder="e.g. 'Multiple B1/B2 slots opened up for August at Mumbai consulate, including same-day cancellation slots'"
                className={fieldClass + " resize-none"}
                required
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
                  Your Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="How should we credit you?"
                  className={fieldClass}
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
                  Email <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="We'll send a verification code"
                  className={fieldClass}
                  required
                />
              </div>
            </div>

            <TurnstileWidget
              onVerify={setTurnstileToken}
              onExpire={() => setTurnstileToken(null)}
              className="mt-2"
            />

            <button
              type="submit"
              disabled={!canSubmit || otpSending}
              className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground font-semibold text-sm py-3 px-6 rounded-lg hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              <Send className="h-4 w-4" />
              {otpSending ? "Sending code…" : "Verify & Publish"}
            </button>
          </form>
        ) : (
          /* OTP verification step */
          <form onSubmit={handleVerifyOtp} className="space-y-4">
            <div className="bg-blue-500/5 border border-blue-500/15 rounded-lg px-4 py-3">
              <p className="text-sm text-foreground/70">
                We sent a 6-digit code to <strong className="text-foreground/90">{email.trim()}</strong>
              </p>
              <p className="text-xs text-foreground/50 mt-1">Check your inbox (and spam folder). Code expires in 10 minutes.</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-foreground/70 mb-1.5 uppercase tracking-wider">
                Verification Code <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={6}
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                placeholder="000000"
                autoFocus
                className={fieldClass + " text-center text-2xl tracking-[0.5em] font-mono"}
                required
              />
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={otpCode.length !== 6 || submitting}
                className="flex-1 flex items-center justify-center gap-2 bg-primary text-primary-foreground font-semibold text-sm py-3 px-6 rounded-lg hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                <CheckCircle className="h-4 w-4" />
                {submitting ? "Verifying…" : "Confirm & Publish"}
              </button>
              <button
                type="button"
                onClick={() => { setStep("form"); setOtpCode(""); setError(null); }}
                className="px-4 py-3 text-sm font-medium text-foreground/60 hover:text-foreground/80 border border-border rounded-lg hover:bg-foreground/5 transition-colors"
              >
                ← Back
              </button>
            </div>

            <button
              type="button"
              onClick={sendOtp}
              disabled={otpResendCooldown > 0 || otpSending}
              className="w-full text-xs text-primary hover:text-primary/80 disabled:text-foreground/30 disabled:cursor-not-allowed transition-colors py-1"
            >
              {otpResendCooldown > 0 ? `Resend code in ${otpResendCooldown}s` : "Resend code"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Alert Signup Form (with OTP email verification)                    */
/* ------------------------------------------------------------------ */
function AlertSignupForm() {
  const [email, setEmail] = useState("");
  const [visaType, setVisaType] = useState("all");
  const [whatsapp, setWhatsapp] = useState("");
  const [step, setStep] = useState<"form" | "otp" | "done">("form");
  const [otpCode, setOtpCode] = useState("");
  const [sending, setSending] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [otpResendCooldown, setOtpResendCooldown] = useState(0);

  const isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());

  useEffect(() => {
    if (otpResendCooldown <= 0) return;
    const t = setTimeout(() => setOtpResendCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [otpResendCooldown]);

  const sendOtp = async () => {
    setSending(true);
    setError(null);
    try {
      const { data, error: fnErr } = await supabase.functions.invoke("send-alert-otp", {
        body: { email: email.trim().toLowerCase() },
      });
      if (fnErr) throw new Error(fnErr.message || "Failed to send code");
      if (data?.error) throw new Error(data.error);
      setStep("otp");
      setOtpResendCooldown(60);
    } catch (e: any) {
      setError(e.message || "Failed to send verification code");
    } finally {
      setSending(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValidEmail) return;
    await sendOtp();
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (otpCode.length !== 6) return;

    setVerifying(true);
    setError(null);
    try {
      const { data, error: fnErr } = await supabase.functions.invoke("verify-alert-otp", {
        body: {
          email: email.trim().toLowerCase(),
          code: otpCode,
          preferences: {
            visa_type: visaType,
            whatsapp: whatsapp || null,
          },
        },
      });
      if (fnErr) throw new Error(fnErr.message || "Verification failed");
      if (data?.error) throw new Error(data.error);
      setStep("done");
    } catch (e: any) {
      setError(e.message || "Invalid or expired code");
    } finally {
      setVerifying(false);
    }
  };

  const inputClass = "w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500/30 focus:border-green-500 transition-colors";

  return (
    <div className="bg-gradient-to-b from-green-500/10 to-emerald-500/5 border border-green-500/20 rounded-xl p-6">
      <h3 className="font-serif font-bold text-lg mb-1 flex items-center gap-2">
        🔔 Visa Slot Alerts
      </h3>
      <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-500/15 text-green-700 text-[10px] font-bold uppercase tracking-wider mb-2">
        Free during launch
      </div>
      <p className="text-sm text-foreground/60 leading-relaxed mb-4">
        Get notified instantly when new appointment slots open or when policy changes affect your visa type.
      </p>

      {error && (
        <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 text-red-700 text-xs mb-3">
          <AlertTriangle className="h-3 w-3 flex-shrink-0" />
          {error}
        </div>
      )}

      {step === "done" ? (
        <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-lg px-4 py-3 text-green-700 text-sm font-medium">
          <CheckCircle className="h-4 w-4 flex-shrink-0" />
          You're in! We'll notify you when slots open. 🎉
        </div>
      ) : step === "otp" ? (
        <form onSubmit={handleVerify} className="space-y-2">
          <div className="bg-blue-500/5 border border-blue-500/15 rounded-lg px-3 py-2">
            <p className="text-xs text-foreground/70">
              Code sent to <strong className="text-foreground/90">{email.trim()}</strong>
            </p>
          </div>
          <input
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={6}
            value={otpCode}
            onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
            placeholder="000000"
            autoFocus
            className={inputClass + " text-center text-xl tracking-[0.4em] font-mono"}
          />
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={otpCode.length !== 6 || verifying}
              className="flex-1 bg-green-600 text-white text-sm font-semibold py-2.5 rounded-lg hover:bg-green-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {verifying ? "Verifying…" : "Confirm"}
            </button>
            <button
              type="button"
              onClick={() => { setStep("form"); setOtpCode(""); setError(null); }}
              className="px-3 py-2.5 text-sm font-medium text-foreground/60 hover:text-foreground/80 border border-border rounded-lg hover:bg-foreground/5 transition-colors"
            >
              ←
            </button>
          </div>
          <button
            type="button"
            onClick={sendOtp}
            disabled={otpResendCooldown > 0 || sending}
            className="w-full text-xs text-green-700 hover:text-green-600 disabled:text-foreground/30 disabled:cursor-not-allowed transition-colors py-0.5"
          >
            {otpResendCooldown > 0 ? `Resend in ${otpResendCooldown}s` : "Resend code"}
          </button>
        </form>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-2">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className={inputClass}
            required
          />
          <div className="relative">
            <input type="tel" disabled placeholder="WhatsApp — coming soon" className="w-full rounded-lg border border-border bg-foreground/[0.03] px-3 py-2.5 text-sm text-foreground/30 cursor-not-allowed" />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-semibold uppercase tracking-wider text-foreground/30">Soon</span>
          </div>
          <select
            value={visaType}
            onChange={(e) => setVisaType(e.target.value)}
            className={inputClass + " text-foreground/70"}
          >
            <option value="all">All visa types</option>
            <option value="B1B2">B1/B2 (Visitor)</option>
            <option value="H-1B">H-1B</option>
            <option value="H-4">H-4</option>
            <option value="F-1">F-1 (Student)</option>
            <option value="L-1">L-1</option>
            <option value="O-1">O-1</option>
          </select>
          <button
            type="submit"
            disabled={!isValidEmail || sending}
            className="w-full bg-green-600 text-white text-sm font-semibold py-2.5 rounded-lg hover:bg-green-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {sending ? "Sending code…" : "Get Free Alerts"}
          </button>
        </form>
      )}
      <p className="text-[11px] text-foreground/40 mt-3 leading-relaxed">
        This is a premium service offered free during our launch period. No credit card needed.
      </p>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Slot Drop Patterns — Heatmap                                       */
/* ------------------------------------------------------------------ */

/** IST offset from UTC in hours */
const IST_OFFSET = 5.5;

/** Get user's UTC offset in hours (e.g. PST = -7, EST = -4) */
function getUserUTCOffset(): number {
  return -(new Date().getTimezoneOffset() / 60);
}

/** Get short timezone label like "PST", "EST", "IST" */
function getUserTZLabel(): string {
  try {
    const parts = new Intl.DateTimeFormat("en-US", { timeZoneName: "short" }).formatToParts(new Date());
    const tz = parts.find((p) => p.type === "timeZoneName");
    return tz?.value ?? "Local";
  } catch {
    return "Local";
  }
}

/** Convert an IST hour to user's local hour */
function istToLocal(istHour: number, userOffset: number): number {
  const utcHour = istHour - IST_OFFSET;
  let local = utcHour + userOffset;
  // Normalize to 0-24
  while (local < 0) local += 24;
  while (local >= 24) local -= 24;
  return local;
}

/** Format an hour as 12h string */
function fmtHour(h: number): string {
  const hr = Math.floor(h);
  const min = Math.round((h - hr) * 60);
  const ampm = hr >= 12 ? "PM" : "AM";
  const h12 = hr === 0 ? 12 : hr > 12 ? hr - 12 : hr;
  return min > 0 ? `${h12}:${min.toString().padStart(2, "0")} ${ampm}` : `${h12} ${ampm}`;
}

/** Build time blocks for a given timezone offset */
function buildTimeBlocks(userOffset: number, useIST: boolean) {
  const offset = useIST ? IST_OFFSET : userOffset;
  // Canonical blocks in IST
  const istBlocks = [
    { istStart: 22, istEnd: 2 },
    { istStart: 2,  istEnd: 6 },
    { istStart: 6,  istEnd: 12 },
    { istStart: 12, istEnd: 18 },
    { istStart: 18, istEnd: 22 },
  ];
  const labels = ["Late Night", "Early Morning", "Morning", "Afternoon", "Evening"];

  if (useIST) {
    return istBlocks.map((b, i) => ({
      label: labels[i],
      sublabel: `${fmtHour(b.istStart)} – ${fmtHour(b.istEnd)}`,
      start: b.istStart,
      end: b.istEnd,
    }));
  }

  // Convert to user's local TZ
  return istBlocks.map((b, i) => {
    const localStart = istToLocal(b.istStart, offset);
    const localEnd = istToLocal(b.istEnd, offset);
    return {
      label: labels[i],
      sublabel: `${fmtHour(localStart)} – ${fmtHour(localEnd)}`,
      start: b.istStart, // keep IST for data matching
      end: b.istEnd,
    };
  });
}

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] as const;

/** Try to extract hour (IST) from a sighting description. */
function extractISTHour(desc: string): number | null {
  const ampm = desc.match(/(\d{1,2})(?::(\d{2}))?\s*(AM|PM)\s*IST/i);
  if (ampm) {
    let h = parseInt(ampm[1], 10);
    const period = ampm[3].toUpperCase();
    if (period === "AM" && h === 12) h = 0;
    if (period === "PM" && h !== 12) h += 12;
    return h;
  }
  if (/midnight/i.test(desc)) return 0;
  return null;
}

/** Try to extract day-of-week from a sighting description. */
function extractDayOfWeek(desc: string, createdAt: string): number {
  const dayNames = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];
  const lower = desc.toLowerCase();
  for (let i = 0; i < dayNames.length; i++) {
    if (lower.includes(dayNames[i]) || lower.includes(dayNames[i].slice(0, 3))) {
      return i;
    }
  }
  const d = new Date(createdAt);
  const js = d.getUTCDay();
  return js === 0 ? 6 : js - 1;
}

function inTimeBlock(hour: number, block: { start: number; end: number }): boolean {
  if (block.start < block.end) {
    return hour >= block.start && hour < block.end;
  }
  return hour >= block.start || hour < block.end;
}

function SlotPatterns({ sightings, filterConsulate }: { sightings: VisaSighting[]; filterConsulate: string }) {
  const [heatConsulate, setHeatConsulate] = useState("");
  const [useIST, setUseIST] = useState(true);

  const userOffset = useMemo(() => getUserUTCOffset(), []);
  const userTZ = useMemo(() => getUserTZLabel(), []);
  const isUserIST = Math.abs(userOffset - IST_OFFSET) < 1; // within 1 hr of IST, default to IST

  const timeBlocks = useMemo(() => buildTimeBlocks(userOffset, useIST), [userOffset, useIST]);

  // Peak window in user's TZ
  const peakLabel = useMemo(() => {
    if (useIST) return "Wednesday – Thursday, 11 PM – 1 AM IST";
    const localStart = istToLocal(23, userOffset);
    const localEnd = istToLocal(1, userOffset);
    return `Wednesday – Thursday, ${fmtHour(localStart)} – ${fmtHour(localEnd)} ${userTZ}`;
  }, [useIST, userOffset, userTZ]);

  const activeSightings = useMemo(() => {
    const c = heatConsulate || filterConsulate;
    return c ? sightings.filter((s) => s.consulate === c) : sightings;
  }, [sightings, heatConsulate, filterConsulate]);

  // Build heatmap grid: [timeBlock][dayOfWeek] = count
  const { grid, maxCount } = useMemo(() => {
    const g: number[][] = timeBlocks.map(() => DAYS.map(() => 0));
    for (const s of activeSightings) {
      const hour = extractISTHour(s.description);
      const day = extractDayOfWeek(s.description, s.created_at);
      if (hour !== null) {
        for (let t = 0; t < timeBlocks.length; t++) {
          if (inTimeBlock(hour, timeBlocks[t])) {
            g[t][day]++;
            break;
          }
        }
      } else {
        g[0][day] += 0.5;
      }
    }
    let mx = 0;
    for (const row of g) for (const v of row) if (v > mx) mx = v;
    return { grid: g, maxCount: mx };
  }, [activeSightings, timeBlocks]);

  // Parse slot lifespans from descriptions
  const avgLifespan = useMemo(() => {
    const mins: number[] = [];
    for (const s of sightings) {
      const m = s.description.match(/(\d+)\s*min/i);
      if (m) mins.push(parseInt(m[1], 10));
      if (/under\s*5/i.test(s.description)) mins.push(4);
    }
    if (mins.length === 0) return null;
    return Math.round(mins.reduce((a, b) => a + b, 0) / mins.length);
  }, [sightings]);

  const cellColor = (val: number) => {
    if (val === 0 || maxCount === 0) return "bg-foreground/[0.03]";
    const intensity = val / maxCount;
    if (intensity > 0.75) return "bg-amber-500/70 text-amber-950";
    if (intensity > 0.5) return "bg-amber-500/45 text-amber-900";
    if (intensity > 0.25) return "bg-amber-500/25 text-amber-800";
    return "bg-amber-500/10 text-amber-700";
  };

  return (
    <section className="mb-6">
      <div className="bg-card border border-border rounded-xl overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-border bg-[#1a1a2e]/[0.03]">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h2 className="font-serif font-bold text-lg flex items-center gap-2">
                ⏰ When Do Slots Drop?
              </h2>
              <p className="text-xs text-foreground/50 mt-1">
                Heatmap of community sightings by day & time
                {!isUserIST && (
                  <button
                    onClick={() => setUseIST(!useIST)}
                    className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full border border-primary/20 text-primary hover:bg-primary/5 transition-colors text-[10px] font-semibold"
                  >
                    🌐 {useIST ? `Show in ${userTZ}` : "Show in IST"}
                  </button>
                )}
                {isUserIST && <span className="ml-1 text-foreground/35">(IST)</span>}
              </p>
            </div>
            <select
              value={heatConsulate}
              onChange={(e) => setHeatConsulate(e.target.value)}
              className="text-xs rounded-lg border border-border bg-background px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors sm:w-auto w-full"
            >
              <option value="">All Consulates</option>
              {CONSULATES.map((c) => (
                <option key={c} value={c}>{CONSULATE_LABELS[c]}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Key Insight Callout */}
        <div className="px-5 py-3 border-b border-border bg-amber-500/[0.06]">
          <div className="flex items-start gap-3">
            <span className="text-lg flex-shrink-0 mt-0.5">💡</span>
            <div>
              <p className="text-sm font-semibold text-foreground/85">
                Peak window: <span className="text-amber-600">{peakLabel}</span>
              </p>
              <p className="text-xs text-foreground/50 mt-0.5 leading-relaxed">
                Based on community reports and cross-referenced data, most new appointment slots appear during the late-night Wednesday window.{useIST ? " Set an alarm and refresh at midnight IST." : ` That's ${fmtHour(istToLocal(0, userOffset))} ${userTZ} for you.`}
              </p>
            </div>
          </div>
        </div>

        {/* Heatmap Grid */}
        <div className="p-5">
          <div className="overflow-x-auto -mx-2 px-2">
            <div className="min-w-[480px]">
              {/* Day headers */}
              <div className="grid grid-cols-[120px_repeat(7,1fr)] gap-1.5 mb-1.5">
                <div /> {/* empty corner */}
                {DAYS.map((d) => (
                  <div key={d} className={`text-center text-[11px] font-bold uppercase tracking-wider py-1.5 rounded-md ${
                    d === "Wed" || d === "Thu"
                      ? "text-amber-600 bg-amber-500/[0.08]"
                      : "text-foreground/40"
                  }`}>
                    {d}
                  </div>
                ))}
              </div>

              {/* Time block rows */}
              {timeBlocks.map((block, ti) => (
                <div key={block.label} className="grid grid-cols-[120px_repeat(7,1fr)] gap-1.5 mb-1.5">
                  <div className="flex flex-col justify-center pr-2 text-right">
                    <span className={`text-[11px] font-semibold leading-tight ${
                      ti === 0 ? "text-amber-600" : "text-foreground/60"
                    }`}>
                      {block.label}
                    </span>
                    <span className="text-[9px] text-foreground/35 leading-tight">{block.sublabel}</span>
                  </div>
                  {DAYS.map((d, di) => {
                    const val = grid[ti][di];
                    return (
                      <div
                        key={d}
                        className={`rounded-md h-10 flex items-center justify-center text-[11px] font-bold transition-colors ${cellColor(val)} ${
                          val > 0 ? "shadow-sm" : ""
                        }`}
                        title={`${d} ${block.sublabel}: ${Math.round(val)} sighting${val !== 1 ? "s" : ""}`}
                      >
                        {val > 0 ? Math.round(val) : ""}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>

          {/* Legend + Stats */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-4 pt-4 border-t border-border">
            {/* Legend */}
            <div className="flex items-center gap-2 text-[10px] text-foreground/50">
              <span>Less</span>
              <div className="flex gap-0.5">
                <div className="w-4 h-4 rounded bg-foreground/[0.03] border border-border" />
                <div className="w-4 h-4 rounded bg-amber-500/10" />
                <div className="w-4 h-4 rounded bg-amber-500/25" />
                <div className="w-4 h-4 rounded bg-amber-500/45" />
                <div className="w-4 h-4 rounded bg-amber-500/70" />
              </div>
              <span>More</span>
            </div>

            {/* Slot lifespan stat */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-red-500/8 border border-red-500/15 rounded-full px-3 py-1.5">
                <span className="text-xs">⚡</span>
                <span className="text-[11px] font-semibold text-red-600/80">
                  Slots last ~{avgLifespan ?? "5-10"} min on average
                </span>
              </div>
              <span className="text-[10px] text-foreground/35">
                {activeSightings.length} sighting{activeSightings.length !== 1 ? "s" : ""} analyzed
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* Main Page                                                          */
/* ------------------------------------------------------------------ */
export default function VisaTrackerPage() {
  const [sightings, setSightings] = useState<VisaSighting[]>([]);
  const [waitTimes, setWaitTimes] = useState<ConsulateWaitRow[]>([]);
  const [updates, setUpdates] = useState<{ id: string; date: string; label: string; headline: string; summary: string; severity: string; source: string }[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [filterConsulate, setFilterConsulate] = useState<string>("");
  const [filterVisa, setFilterVisa] = useState<string>("");

  const load = useCallback(async () => {
    const [s, w] = await Promise.all([getVisaSightings(), getConsulateWaitTimes([...INDIA_CONSULATES])]);
    setSightings(s);
    setWaitTimes(w);
    // Load updates from static JSON
    try {
      const res = await fetch("/data/visa-updates.json");
      if (res.ok) setUpdates(await res.json());
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = useMemo(() => {
    let results = sightings;
    if (filterConsulate) results = results.filter((s) => s.consulate === filterConsulate);
    if (filterVisa) results = results.filter((s) => s.visa_type === filterVisa);
    return results;
  }, [sightings, filterConsulate, filterVisa]);

  const pillClass = (active: boolean) =>
    `inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
      active
        ? "bg-primary text-primary-foreground shadow-sm"
        : "bg-foreground/5 text-foreground/60 hover:bg-foreground/10"
    }`;

  return (
    <>
      <Helmet>
        <title>US Visa Appointment Tracker — Community Slot Intelligence | The Videshi</title>
        <meta
          name="description"
          content="Community-powered US visa appointment slot tracker for India's 5 consulates. See real-time sightings, official wait times, and report open slots to help fellow Indians."
        />
        <meta property="og:title" content="US Visa Appointment Tracker — The Videshi" />
        <meta
          property="og:description"
          content="Track US visa appointment openings across India's 5 consulates. Community-sourced, real-time sighting reports."
        />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://www.thevideshi.com/immigration/visas" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8">
        {/* ── Hero ─────────────────────────────────────────── */}
        <section className="relative mb-6 -mx-4 px-6 py-12 md:py-16 rounded-2xl overflow-hidden bg-[#1a1a2e] border border-[#2a2a4a]/40">
          <div
            className="absolute inset-0 opacity-[0.06]"
            style={{
              backgroundImage:
                "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
            }}
          />
          <div className="absolute top-0 right-0 w-64 h-64 bg-green-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-amber-500/8 rounded-full blur-3xl" />

          <div className="relative z-10 max-w-3xl">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-bold uppercase tracking-widest text-amber-300 bg-amber-500/15 px-3 py-1 rounded-full">
                🛂 Community-Powered
              </span>
            </div>
            <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight leading-[1.1] text-white">
              US Visa Appointment<br />
              <span className="text-green-400">Tracker.</span>
            </h1>
            <p className="text-white/70 mt-4 text-base md:text-lg max-w-2xl leading-relaxed">
              Real-time slot sightings from the community for India's 5 US consulates.
              See what people are finding, and share what you see.
            </p>
            <div className="flex flex-wrap gap-3 mt-6">
              <a
                href="#report"
                className="inline-flex items-center gap-2 bg-green-500 text-white font-semibold text-sm py-2.5 px-6 rounded-full hover:bg-green-400 transition-colors shadow-lg shadow-green-500/20"
              >
                <Send className="h-4 w-4" />
                Report a Sighting
              </a>
              <Link
                to="/immigration"
                className="inline-flex items-center gap-2 bg-white/10 text-white/80 font-medium text-sm py-2.5 px-5 rounded-full hover:bg-white/15 transition-colors border border-white/10"
              >
                ← Immigration Hub
              </Link>
            </div>
          </div>
        </section>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : (
          <>
            {/* ── Official Wait Times ──────────────────────────── */}
            <section className="mb-6">
              <WaitTimeStrip data={waitTimes} />
              <p className="text-[10px] text-foreground/40 text-center mt-2 leading-relaxed">
                Source: US State Department · This tracker relies on community sightings, not automated scraping
              </p>
            </section>

            {/* ── Slot Drop Patterns ──────────────────────────── */}
            <SlotPatterns sightings={sightings} filterConsulate={filterConsulate} />

            {/* ── Latest Updates ──────────────────────────────── */}
            {updates.length > 0 && (
            <section className="mb-6">
              <div className="bg-card border border-border rounded-xl overflow-hidden">
                <div className="px-5 py-3 border-b border-border">
                  <h3 className="font-serif font-bold text-base flex items-center gap-2">
                    📰 Latest Updates
                  </h3>
                </div>
                <div className="divide-y divide-border">
                  {updates.map((u) => (
                    <div key={u.id} className="px-5 py-3 hover:bg-foreground/[0.02] transition-colors">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          {u.url ? (
                            <Link to={u.url} className="font-medium text-sm text-foreground/90 hover:text-primary transition-colors leading-snug line-clamp-2">
                              {u.headline} →
                            </Link>
                          ) : (
                            <p className="font-medium text-sm text-foreground/90 leading-snug line-clamp-2">{u.headline}</p>
                          )}
                          <p className="text-xs text-foreground/50 mt-0.5 line-clamp-1">{u.summary}</p>
                        </div>
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-primary/60 whitespace-nowrap pt-0.5">{u.label}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>
            )}

            {/* ── Notification + Guides Row ──────────────────── */}
            <section className="mb-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Visa Slot Alerts */}
              <AlertSignupForm />

              {/* Visa Guides */}
              <div className="bg-card border border-border rounded-xl p-6 flex flex-col">
                <h3 className="font-serif font-bold text-lg mb-4 flex items-center gap-2">
                  📚 Visa Guides
                </h3>
                <ul className="text-sm text-foreground/70 space-y-3 leading-relaxed flex-1">
                  <li><Link to="/immigration/guides/visa-interview-prep" className="flex items-center gap-2 hover:text-primary transition-colors">🏛️ Interview prep & document checklist →</Link></li>
                  <li><Link to="/immigration/guides/visa-interview-mistakes" className="flex items-center gap-2 hover:text-primary transition-colors">🚫 What NOT to say to the officer →</Link></li>
                  <li><Link to="/immigration/guides/social-media-screening" className="flex items-center gap-2 hover:text-primary transition-colors">📱 Social media screening guide →</Link></li>
                  <li><Link to="/immigration/guides/after-visa-interview" className="flex items-center gap-2 hover:text-primary transition-colors">📬 After your interview — what to expect →</Link></li>
                  <li><Link to="/immigration/guides/third-country-stamping" className="flex items-center gap-2 hover:text-primary transition-colors">🌍 Third-country stamping guide →</Link></li>
                </ul>
                <Link to="/immigration/guides" className="text-sm text-primary font-medium mt-4 flex items-center gap-1 hover:gap-2 transition-all">
                  Read all guides <ChevronRight className="h-4 w-4" />
                </Link>
              </div>
            </section>

            {/* ── Report a Sighting ──────────────────────────── */}
            <section className="mb-6" id="report">
              <ReportForm onSubmitted={load} />
            </section>

            {/* ── Community Sightings Feed ────────────────────── */}
            <section className="mb-6">
              <div className="flex items-center justify-between mb-5">
                <h2 className="font-serif text-xl font-bold flex items-center gap-2">
                  📡 Community Sightings
                  <span className="text-xs font-normal text-foreground/40 ml-1">
                    {filtered.length} report{filtered.length !== 1 && "s"}
                  </span>
                </h2>
              </div>

              {/* ── Filter Pills ──────────────────────────── */}
              <div className="mb-5 space-y-2">
                <div className="flex flex-wrap gap-2">
                  <button className={pillClass(!filterConsulate)} onClick={() => setFilterConsulate("")}>
                    All Consulates
                  </button>
                  {CONSULATES.map((c) => (
                    <button key={c} className={pillClass(filterConsulate === c)} onClick={() => setFilterConsulate(filterConsulate === c ? "" : c)}>
                      {CONSULATE_LABELS[c]}
                    </button>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2">
                  <button className={pillClass(!filterVisa)} onClick={() => setFilterVisa("")}>
                    All Types
                  </button>
                  {VISA_TYPES.map((v) => (
                    <button key={v} className={pillClass(filterVisa === v)} onClick={() => setFilterVisa(filterVisa === v ? "" : v)}>
                      {v}
                    </button>
                  ))}
                </div>
              </div>

              {/* ── Sighting Cards ─────────────────────────── */}
              <div className="space-y-3">
                {filtered.length === 0 ? (
                  <div className="text-center py-12 bg-card border border-border rounded-xl">
                    <p className="text-foreground/40 text-sm">No sightings match the current filters.</p>
                    <button
                      onClick={() => { setFilterConsulate(""); setFilterVisa(""); }}
                      className="mt-2 text-primary text-sm font-medium hover:underline"
                    >
                      Clear filters
                    </button>
                  </div>
                ) : (
                  filtered.map((s) => <SightingCard key={s.id} s={s} />)
                )}
              </div>
            </section>

            {/* ── Disclaimer ─────────────────────────────────── */}
            <div className="bg-amber-500/5 border border-amber-500/15 rounded-xl p-4 mb-6">
              <p className="text-[11px] text-foreground/50 leading-relaxed">
                <span className="font-semibold text-foreground/70">Data Source Note:</span>{" "}
                Official wait times are from the US State Department. Community sightings are
                user-reported observations — we never scrape or automate access to
                usvisascheduling.com. Slot availability changes rapidly; always verify on the
                official site before booking.
              </p>
            </div>
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
