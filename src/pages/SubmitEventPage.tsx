import { useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import { supabase } from "@/integrations/supabase/client";
import { generateSlug } from "@/lib/events";

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

export default function SubmitEventPage() {
  const [form, setForm] = useState<FormData>(INITIAL);
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const set = (field: keyof FormData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setForm((f) => ({ ...f, [field]: e.target.value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setSubmitting(true);
    setSubmitError(null);

    const slug = generateSlug(form.title.trim(), form.date);

    const row = {
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

    const sbRaw = supabase as unknown as { from: (t: string) => any };
    const { error } = await sbRaw.from("events").insert([row]);

    setSubmitting(false);

    if (error) {
      console.error("Submit event error:", error);
      setSubmitError("Something went wrong. Please try again.");
    } else {
      setSubmitted(true);
    }
  };

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
            <div className="flex justify-center gap-4">
              <Link
                to="/events"
                className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
              >
                ← Back to Events
              </Link>
              <button
                onClick={() => { setSubmitted(false); setForm(INITIAL); }}
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

          {submitError && (
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
                Submitting…
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
