import { useState, useCallback } from "react";
import { supabase } from "@/integrations/supabase/client";
import { DIRECTORY_CATEGORIES, CATEGORY_ICONS } from "@/lib/directory";

const sb = supabase as any;

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

/* Extended categories for recommendations (includes "Event Venues" and "Other") */
const RECOMMEND_CATEGORIES = [...DIRECTORY_CATEGORIES, "Event Venues", "Other"];

type FormData = {
  business_name: string;
  category: string;
  city: string;
  state: string;
  phone: string;
  website: string;
  description: string;
  recommender_name: string;
  recommender_email: string;
  reason: string;
};

const INITIAL: FormData = {
  business_name: "",
  category: "",
  city: "",
  state: "",
  phone: "",
  website: "",
  description: "",
  recommender_name: "",
  recommender_email: "",
  reason: "",
};

export default function RecommendBusinessModal({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [form, setForm] = useState<FormData>(INITIAL);
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const set = useCallback(
    (field: keyof FormData) =>
      (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        setForm((f) => ({ ...f, [field]: e.target.value }));
        if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }));
      },
    [errors],
  );

  const validate = (): boolean => {
    const errs: Partial<Record<keyof FormData, string>> = {};
    if (!form.business_name.trim()) errs.business_name = "Business name is required";
    if (!form.category) errs.category = "Please select a category";
    if (!form.city.trim()) errs.city = "City is required";
    if (!form.state) errs.state = "State is required";
    if (form.website && !/^https?:\/\/.+/.test(form.website.trim()))
      errs.website = "URL should start with http:// or https://";
    if (form.recommender_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.recommender_email.trim()))
      errs.recommender_email = "Please enter a valid email";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    setSubmitError(null);

    const { error } = await sb.from("directory_recommendations").insert([
      {
        business_name: form.business_name.trim(),
        category: form.category,
        city: form.city.trim(),
        state: form.state,
        phone: form.phone.trim() || null,
        website: form.website.trim() || null,
        description: form.description.trim() || null,
        recommender_name: form.recommender_name.trim() || null,
        recommender_email: form.recommender_email.trim() || null,
        reason: form.reason.trim() || null,
      },
    ]);

    setSubmitting(false);

    if (error) {
      console.error("Recommendation submit error:", error);
      setSubmitError("Something went wrong. Please try again.");
      return;
    }

    setSubmitted(true);
  };

  const handleClose = () => {
    setForm(INITIAL);
    setErrors({});
    setSubmitError(null);
    setSubmitted(false);
    setSubmitting(false);
    onClose();
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={handleClose} />

      {/* Modal */}
      <div className="relative bg-card border border-border rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        {/* Close button */}
        <button
          onClick={handleClose}
          className="absolute top-3 right-3 w-8 h-8 flex items-center justify-center rounded-full hover:bg-muted/60 transition-colors text-muted-foreground z-10"
          aria-label="Close"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {submitted ? (
          /* ─── Success ─── */
          <div className="p-8 text-center">
            <p className="text-4xl mb-4">🙏</p>
            <h2 className="font-serif text-xl text-foreground mb-2">Thank You!</h2>
            <p className="text-muted-foreground text-sm mb-6">
              We'll review your recommendation and add it to the directory shortly.
            </p>
            <button
              onClick={handleClose}
              className="px-6 py-2.5 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors"
            >
              Close
            </button>
          </div>
        ) : (
          /* ─── Form ─── */
          <form onSubmit={handleSubmit} className="p-6">
            <div className="mb-5">
              <h2 className="font-serif text-xl text-foreground mb-1">Recommend a Business</h2>
              <p className="text-muted-foreground text-sm">
                Know a great Indian business or professional? Help the community find them.
              </p>
            </div>

            <div className="space-y-4">
              {/* Business Name */}
              <Field label="Business Name" required error={errors.business_name}>
                <input
                  type="text"
                  value={form.business_name}
                  onChange={set("business_name")}
                  placeholder="e.g. Patel Family Dentistry"
                  className={inputCls(errors.business_name)}
                />
              </Field>

              {/* Category */}
              <Field label="Category" required error={errors.category}>
                <select
                  value={form.category}
                  onChange={set("category")}
                  className={inputCls(errors.category)}
                >
                  <option value="">Select a category</option>
                  {RECOMMEND_CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {CATEGORY_ICONS[c] || "📌"} {c}
                    </option>
                  ))}
                </select>
              </Field>

              {/* City + State */}
              <div className="grid grid-cols-2 gap-3">
                <Field label="City" required error={errors.city}>
                  <input
                    type="text"
                    value={form.city}
                    onChange={set("city")}
                    placeholder="e.g. Fremont"
                    className={inputCls(errors.city)}
                  />
                </Field>
                <Field label="State" required error={errors.state}>
                  <select
                    value={form.state}
                    onChange={set("state")}
                    className={inputCls(errors.state)}
                  >
                    <option value="">Select</option>
                    {US_STATES.map((s) => (
                      <option key={s} value={s}>
                        {STATE_NAMES[s] || s}
                      </option>
                    ))}
                  </select>
                </Field>
              </div>

              {/* Phone + Website */}
              <div className="grid grid-cols-2 gap-3">
                <Field label="Phone" error={errors.phone}>
                  <input
                    type="tel"
                    value={form.phone}
                    onChange={set("phone")}
                    placeholder="(555) 123-4567"
                    className={inputCls(errors.phone)}
                  />
                </Field>
                <Field label="Website" error={errors.website}>
                  <input
                    type="url"
                    value={form.website}
                    onChange={set("website")}
                    placeholder="https://..."
                    className={inputCls(errors.website)}
                  />
                </Field>
              </div>

              {/* Description */}
              <Field label="Short Description">
                <textarea
                  value={form.description}
                  onChange={set("description")}
                  placeholder="What does this business do?"
                  rows={2}
                  maxLength={500}
                  className={inputCls()}
                />
                <p className="text-[11px] text-muted-foreground/60 mt-0.5 text-right">
                  {form.description.length}/500
                </p>
              </Field>

              {/* Divider */}
              <div className="h-px bg-border" />

              {/* Your Name */}
              <Field label="Your Name">
                <input
                  type="text"
                  value={form.recommender_name}
                  onChange={set("recommender_name")}
                  placeholder="Optional"
                  className={inputCls()}
                />
              </Field>

              {/* Your Email */}
              <Field label="Your Email" error={errors.recommender_email}>
                <input
                  type="email"
                  value={form.recommender_email}
                  onChange={set("recommender_email")}
                  placeholder="Optional — not displayed publicly"
                  className={inputCls(errors.recommender_email)}
                />
              </Field>

              {/* Reason */}
              <Field label="Why do you recommend this?">
                <textarea
                  value={form.reason}
                  onChange={set("reason")}
                  placeholder="What makes this business worth recommending?"
                  rows={2}
                  maxLength={300}
                  className={inputCls()}
                />
                <p className="text-[11px] text-muted-foreground/60 mt-0.5 text-right">
                  {form.reason.length}/300
                </p>
              </Field>
            </div>

            {submitError && (
              <div className="mt-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 text-sm">
                {submitError}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="mt-5 w-full px-6 py-3 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  Submitting…
                </span>
              ) : (
                "Submit Recommendation"
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
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
      <label className="block text-xs font-medium text-foreground/80 mb-1">
        {label}
        {required && <span className="text-red-400 ml-0.5">*</span>}
      </label>
      {children}
      {error && <p className="text-xs text-red-400 mt-0.5">{error}</p>}
    </div>
  );
}

function inputCls(error?: string): string {
  return `w-full px-3 py-2 rounded-lg border text-sm text-foreground bg-background placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 transition-colors ${
    error
      ? "border-red-400/60 focus:ring-red-400/30 focus:border-red-400"
      : "border-border focus:ring-primary/30 focus:border-primary/50"
  }`;
}
