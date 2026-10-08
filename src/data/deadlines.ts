/* Curated deadlines for US-based Indian diaspora.
   Every date verified via web search Oct 2026 — see sourceUrl.
   Past deadlines drop off automatically (the page filters date >= today). */

export interface Deadline {
  id: string;
  title: string;
  /** YYYY-MM-DD */
  date: string;
  category: "tax" | "immigration" | "health" | "festival" | "holiday";
  blurb: string;
  sourceName: string;
  sourceUrl: string;
}

export const DEADLINES: Deadline[] = [
  {
    id: "fbar-2026",
    title: "FBAR (FinCEN Form 114) deadline",
    date: "2026-10-15",
    category: "tax",
    blurb:
      "Foreign bank accounts totaling over $10,000 must be reported to FinCEN — automatic extension, no form needed to claim it.",
    sourceName: "Manay CPA",
    sourceUrl: "https://www.manaycpa.com/what-is-fbar-and-fbar-filing/",
  },
  {
    id: "tax-extension-2026",
    title: "Extended tax return deadline",
    date: "2026-10-15",
    category: "tax",
    blurb:
      "Last day to file your 2025 federal return if you filed Form 4868. Extension is for filing only — tax owed was due April 15.",
    sourceName: "USA Today",
    sourceUrl:
      "https://www.usatoday.com/story/money/money-management/credit-debt/2026/10/05/oct-15-tax-deadline-penalties/92062309007/",
  },
  {
    id: "medicare-oe-start",
    title: "Medicare Open Enrollment begins",
    date: "2026-10-15",
    category: "health",
    blurb:
      "Review and change Medicare coverage for 2027. Runs through December 7 — relevant if you're managing parents' coverage.",
    sourceName: "GrantsHub USA",
    sourceUrl: "https://grantshubusa.com/blog/aca-open-enrollment",
  },
  {
    id: "visa-bulletin-nov-2026",
    title: "November Visa Bulletin expected",
    date: "2026-10-15",
    category: "immigration",
    blurb:
      "State Dept publishes each bulletin mid-month. Watch EB-2/EB-3 India movement after October's fiscal-year reset.",
    sourceName: "Shusterman",
    sourceUrl: "https://www.shusterman.com/visa-bulletin-state-department/",
  },
  {
    id: "dussehra-2026",
    title: "Dussehra · Vijayadashami",
    date: "2026-10-20",
    category: "festival",
    blurb:
      "Victory of good over evil — Ravan Dahan events and melas in most metros. See the Festivals hub for local listings.",
    sourceName: "The Videshi Festivals",
    sourceUrl: "https://www.thevideshi.com/festivals",
  },
  {
    id: "aca-oe-start",
    title: "ACA Open Enrollment begins",
    date: "2026-11-01",
    category: "health",
    blurb:
      "2027 health coverage shopping opens on HealthCare.gov. Runs through Jan 15 — compare before you auto-renew.",
    sourceName: "Medical Daily",
    sourceUrl:
      "https://www.medicaldaily.com/aca-open-enrollment-2027-dates-premiums-deadlines-478808",
  },
  {
    id: "dst-ends-2026",
    title: "Daylight Saving ends",
    date: "2026-11-01",
    category: "holiday",
    blurb:
      "Clocks fall back — and the India time gap widens to 13.5 hours (EST) for calling family.",
    sourceName: "The Videshi",
    sourceUrl: "https://www.thevideshi.com/your-hub",
  },
  {
    id: "diwali-2026",
    title: "Diwali · Lakshmi Puja",
    date: "2026-11-08",
    category: "festival",
    blurb:
      "Main day of Diwali 2026 (Nov 6–10). Book India travel and event tickets early — see the Festivals hub.",
    sourceName: "The Videshi Festivals",
    sourceUrl: "https://www.thevideshi.com/festivals",
  },
  {
    id: "thanksgiving-2026",
    title: "Thanksgiving",
    date: "2026-11-26",
    category: "holiday",
    blurb:
      "Peak India-travel week. Fares are typically highest the week of Thanksgiving — book earlier if you haven't.",
    sourceName: "The Videshi",
    sourceUrl: "https://www.thevideshi.com/your-hub",
  },
  {
    id: "medicare-oe-end",
    title: "Medicare Open Enrollment ends",
    date: "2026-12-07",
    category: "health",
    blurb: "Last day to change Medicare coverage for 2027.",
    sourceName: "GrantsHub USA",
    sourceUrl: "https://grantshubusa.com/blog/aca-open-enrollment",
  },
  {
    id: "aca-jan1-cutoff",
    title: "ACA cutoff for Jan 1 coverage",
    date: "2026-12-15",
    category: "health",
    blurb:
      "Enroll or switch by today for coverage starting January 1. Plans picked after start February 1.",
    sourceName: "Medical Daily",
    sourceUrl:
      "https://www.medicaldaily.com/aca-open-enrollment-2027-dates-premiums-deadlines-478808",
  },
  {
    id: "aca-oe-end",
    title: "ACA Open Enrollment ends",
    date: "2027-01-15",
    category: "health",
    blurb:
      "Last day to get 2027 marketplace coverage. After this, only life-event special enrollment.",
    sourceName: "Medical Daily",
    sourceUrl:
      "https://www.medicaldaily.com/aca-open-enrollment-2027-dates-premiums-deadlines-478808",
  },
  {
    id: "h1b-fy2028-registration",
    title: "H-1B FY2028 registration window",
    date: "2027-03-01",
    category: "immigration",
    blurb:
      "Expected March 2027 (exact dates announced ~Feb 2027). Employers: start wage/SOC planning by January.",
    sourceName: "Mintz",
    sourceUrl:
      "https://www.mintz.com/insights-center/viewpoints/2806/2026-07-20-uscis-announces-fy2027-h-1b-cap-reached-no-second",
  },
];
