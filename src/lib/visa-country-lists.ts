/* ------------------------------------------------------------------ */
/* Full country lists for visa dashboard detail pages                  */
/* Organized by holder status × visa category                         */
/* ------------------------------------------------------------------ */

export type VisaCountryEntry = {
  country: string;
  notes?: string;
  flag?: string;
};

export type VisaListMeta = {
  title: string;
  subtitle: string;
  count: number;
  color: string;     // tailwind bg
  textColor: string;  // tailwind text
  emoji: string;
};

/* ================================================================== */
/* INDIAN PASSPORT                                                    */
/* ================================================================== */

export const IP_VISA_FREE: VisaCountryEntry[] = [
  { country: "Thailand", flag: "🇹🇭", notes: "60 days visa-free (was 30; check latest updates)" },
  { country: "Indonesia", flag: "🇮🇩", notes: "30 days visa-free on arrival" },
  { country: "Nepal", flag: "🇳🇵", notes: "Unlimited stay; no visa needed" },
  { country: "Bhutan", flag: "🇧🇹", notes: "Permit required but no visa; $100/day SDF" },
  { country: "Mauritius", flag: "🇲🇺", notes: "90 days visa-free" },
  { country: "Serbia", flag: "🇷🇸", notes: "30 days visa-free" },
  { country: "Fiji", flag: "🇫🇯", notes: "4 months visa-free" },
  { country: "Barbados", flag: "🇧🇧", notes: "6 months visa-free" },
  { country: "Dominica", flag: "🇩🇲", notes: "21 days visa-free" },
  { country: "Grenada", flag: "🇬🇩", notes: "3 months visa-free" },
  { country: "Haiti", flag: "🇭🇹", notes: "3 months visa-free" },
  { country: "Jamaica", flag: "🇯🇲", notes: "30 days visa-free" },
  { country: "St. Kitts & Nevis", flag: "🇰🇳", notes: "3 months visa-free" },
  { country: "St. Lucia", flag: "🇱🇨", notes: "6 weeks visa-free" },
  { country: "St. Vincent", flag: "🇻🇨", notes: "1 month visa-free" },
  { country: "Trinidad & Tobago", flag: "🇹🇹", notes: "90 days visa-free" },
  { country: "Vanuatu", flag: "🇻🇺", notes: "30 days visa-free" },
  { country: "Micronesia", flag: "🇫🇲", notes: "30 days visa-free" },
  { country: "El Salvador", flag: "🇸🇻", notes: "90 days visa-free (with valid US visa)" },
  { country: "Macao", flag: "🇲🇴", notes: "30 days visa-free" },
  { country: "Qatar", flag: "🇶🇦", notes: "30 days visa-free waiver" },
  { country: "Iran", flag: "🇮🇷", notes: "15 days visa-free for Indian nationals" },
  { country: "Senegal", flag: "🇸🇳", notes: "90 days visa-free" },
  { country: "Tunisia", flag: "🇹🇳", notes: "90 days visa-free" },
  { country: "Oman", flag: "🇴🇲", notes: "14 days visa-free (conditions apply)" },
];

export const IP_VOA: VisaCountryEntry[] = [
  { country: "Cambodia", flag: "🇰🇭", notes: "30 days; $30 fee at airport" },
  { country: "Laos", flag: "🇱🇦", notes: "30 days; $20–40 fee" },
  { country: "Madagascar", flag: "🇲🇬", notes: "90 days; ~$27 fee" },
  { country: "Seychelles", flag: "🇸🇨", notes: "30 days; free of charge" },
  { country: "Jordan", flag: "🇯🇴", notes: "30 days; ~40 JOD fee" },
  { country: "Maldives", flag: "🇲🇻", notes: "30 days; free tourist visa" },
  { country: "Myanmar", flag: "🇲🇲", notes: "30 days; $50 fee (Mandalay & Nay Pyi Taw)" },
  { country: "Tuvalu", flag: "🇹🇻", notes: "30 days; free on arrival" },
  { country: "Palau", flag: "🇵🇼", notes: "30 days; free on arrival" },
  { country: "East Timor / Timor-Leste", flag: "🇹🇱", notes: "30 days; $30 fee" },
  { country: "Guinea-Bissau", flag: "🇬🇼", notes: "90 days; varies" },
  { country: "Comoros", flag: "🇰🇲", notes: "45 days; fee applies" },
  { country: "Mozambique", flag: "🇲🇿", notes: "30 days; $50 fee" },
  { country: "Rwanda", flag: "🇷🇼", notes: "30 days; $50 fee" },
  { country: "Sierra Leone", flag: "🇸🇱", notes: "30 days; $80 fee" },
  { country: "Somalia", flag: "🇸🇴", notes: "30 days; $60 fee" },
  { country: "Togo", flag: "🇹🇬", notes: "7 days; ~$20 fee" },
  { country: "Uganda", flag: "🇺🇬", notes: "e-Visa or VOA; $50 fee" },
  { country: "Zimbabwe", flag: "🇿🇼", notes: "90 days; $30–55" },
  { country: "Bolivia", flag: "🇧🇴", notes: "90 days; ~$52 fee" },
  { country: "Cape Verde", flag: "🇨🇻", notes: "VOA at airport; fee applies" },
  { country: "Gabon", flag: "🇬🇦", notes: "e-Visa or VOA; €70" },
  { country: "Samoa", flag: "🇼🇸", notes: "60 days; free" },
  { country: "Tanzania", flag: "🇹🇿", notes: "VOA available; $50 fee" },
  { country: "Burundi", flag: "🇧🇮", notes: "VOA available; $40 fee" },
  { country: "Guinea", flag: "🇬🇳", notes: "VOA at Conakry airport" },
  { country: "Mauritania", flag: "🇲🇷", notes: "VOA at Nouakchott; ~€55" },
  { country: "Suriname", flag: "🇸🇷", notes: "Tourist card at airport; ~$25" },
  { country: "Marshall Islands", flag: "🇲🇭", notes: "30 days; free on arrival" },
  { country: "Montserrat", flag: "🇲🇸", notes: "VOA available" },
];

export const IP_E_VISA: VisaCountryEntry[] = [
  { country: "Turkey", flag: "🇹🇷", notes: "e-Visa online; $50; 30 days; approved instantly" },
  { country: "Sri Lanka", flag: "🇱🇰", notes: "ETA online; $35; 30 days" },
  { country: "Australia", flag: "🇦🇺", notes: "e-Visa subclass 600; processing 1–4 weeks" },
  { country: "Kenya", flag: "🇰🇪", notes: "eTA online; $30; 90 days" },
  { country: "UAE / Dubai", flag: "🇦🇪", notes: "e-Visa or VOA (14/30 days)" },
  { country: "Vietnam", flag: "🇻🇳", notes: "e-Visa online; $25; 30 days single entry" },
  { country: "New Zealand", flag: "🇳🇿", notes: "NZeTA; NZ$23; valid 2 years" },
  { country: "Egypt", flag: "🇪🇬", notes: "e-Visa online; $25; 30 days" },
  { country: "Bahrain", flag: "🇧🇭", notes: "e-Visa; ~14 BHD; 14 days" },
  { country: "Oman", flag: "🇴🇲", notes: "e-Visa; ~$13; 10–30 days" },
  { country: "Ethiopia", flag: "🇪🇹", notes: "e-Visa; $52; 30 days" },
  { country: "South Africa", flag: "🇿🇦", notes: "e-Visa pilot; processing varies" },
  { country: "Morocco", flag: "🇲🇦", notes: "e-Visa; processing 3–5 days" },
  { country: "Georgia", flag: "🇬🇪", notes: "e-Visa; $20; 30 days" },
  { country: "Azerbaijan", flag: "🇦🇿", notes: "ASAN e-Visa; $26; 30 days; approved in 3 days" },
  { country: "Uzbekistan", flag: "🇺🇿", notes: "e-Visa; free for some; 30 days" },
  { country: "Tajikistan", flag: "🇹🇯", notes: "e-Visa; $50; 45 days" },
  { country: "Malaysia", flag: "🇲🇾", notes: "eNTRI or e-Visa; 15–30 days" },
  { country: "Myanmar", flag: "🇲🇲", notes: "e-Visa; $50; 28 days tourist" },
  { country: "Singapore", flag: "🇸🇬", notes: "e-Visa through authorized agent" },
  { country: "South Korea", flag: "🇰🇷", notes: "K-ETA (if eligible); otherwise visa required" },
  { country: "Japan", flag: "🇯🇵", notes: "e-Visa pilot for tourism" },
  { country: "Armenia", flag: "🇦🇲", notes: "e-Visa; 120 days; free" },
  { country: "Côte d'Ivoire", flag: "🇨🇮", notes: "e-Visa; ~€73" },
  { country: "Djibouti", flag: "🇩🇯", notes: "e-Visa; $23; 31 days" },
  { country: "Cameroon", flag: "🇨🇲", notes: "e-Visa available" },
  { country: "Benin", flag: "🇧🇯", notes: "e-Visa; €50; 30 days" },
  { country: "Antigua & Barbuda", flag: "🇦🇬", notes: "e-Visa; $100; 30 days" },
  { country: "Zambia", flag: "🇿🇲", notes: "e-Visa; $50; 30 days" },
  { country: "Moldova", flag: "🇲🇩", notes: "e-Visa; free; 90 days" },
  { country: "Colombia", flag: "🇨🇴", notes: "e-Visa available" },
  { country: "Kyrgyzstan", flag: "🇰🇬", notes: "e-Visa; $40; 30 days" },
  { country: "Lesotho", flag: "🇱🇸", notes: "e-Visa available" },
  { country: "Papua New Guinea", flag: "🇵🇬", notes: "e-Visa; 60 days" },
  { country: "Russia", flag: "🇷🇺", notes: "e-Visa; free; 16 days (select ports)" },
  { country: "Saudi Arabia", flag: "🇸🇦", notes: "e-Visa for tourism; ~$120" },
  { country: "Taiwan", flag: "🇹🇼", notes: "e-Visa if holding valid US/Schengen visa" },
  { country: "Botswana", flag: "🇧🇼", notes: "e-Visa pilot" },
  { country: "Nigeria", flag: "🇳🇬", notes: "e-Visa; $80; 30 days" },
  { country: "Malawi", flag: "🇲🇼", notes: "e-Visa; $50; 30 days" },
];

export const IP_US_GC_PERKS: VisaCountryEntry[] = [
  { country: "Mexico", flag: "🇲🇽", notes: "Visa-free with valid US visa or GC; 180 days" },
  { country: "Turkey", flag: "🇹🇷", notes: "e-Visa with valid US visa/GC; 30 days" },
  { country: "Philippines", flag: "🇵🇭", notes: "30 days visa-free with valid US visa" },
  { country: "Costa Rica", flag: "🇨🇷", notes: "30 days visa-free with valid US visa" },
  { country: "Panama", flag: "🇵🇦", notes: "30–180 days with valid US visa/GC" },
  { country: "Colombia", flag: "🇨🇴", notes: "90 days visa-free with valid US visa" },
  { country: "Georgia", flag: "🇬🇪", notes: "1 year visa-free with valid US visa/GC" },
  { country: "Albania", flag: "🇦🇱", notes: "90 days visa-free with valid US visa" },
  { country: "Bermuda", flag: "🇧🇲", notes: "Visa-free with valid US visa/GC" },
  { country: "Aruba", flag: "🇦🇼", notes: "30 days visa-free with valid US visa" },
  { country: "Peru", flag: "🇵🇪", notes: "Visa-free with valid US visa; 183 days" },
  { country: "Chile", flag: "🇨🇱", notes: "90 days visa-free with valid US visa" },
  { country: "Montenegro", flag: "🇲🇪", notes: "30 days with valid US visa" },
  { country: "North Macedonia", flag: "🇲🇰", notes: "15 days with valid US visa" },
  { country: "Kosovo", flag: "🇽🇰", notes: "15 days with valid US visa" },
  { country: "Bosnia & Herzegovina", flag: "🇧🇦", notes: "30 days with valid US visa" },
  { country: "Belize", flag: "🇧🇿", notes: "Visa-free with valid US visa; 30 days" },
  { country: "Guatemala", flag: "🇬🇹", notes: "90 days with valid US visa" },
  { country: "Honduras", flag: "🇭🇳", notes: "90 days with valid US visa" },
  { country: "El Salvador", flag: "🇸🇻", notes: "90 days visa-free with valid US visa" },
  { country: "Nicaragua", flag: "🇳🇮", notes: "90 days with valid US visa" },
  { country: "Dominican Republic", flag: "🇩🇴", notes: "Tourist card $10; no visa needed" },
  { country: "Taiwan", flag: "🇹🇼", notes: "Visa-free transit with valid US visa" },
  { country: "Curaçao", flag: "🇨🇼", notes: "30 days visa-free with valid US visa" },
  { country: "Bonaire", flag: "🇧🇶", notes: "Visa-free with valid US visa" },
  { country: "St. Maarten", flag: "🇸🇽", notes: "Visa-free with valid US visa" },
  { country: "Turks & Caicos", flag: "🇹🇨", notes: "90 days visa-free with valid US visa" },
  { country: "Paraguay", flag: "🇵🇾", notes: "Visa-free with valid US visa" },
  { country: "Uruguay", flag: "🇺🇾", notes: "Visa-free with valid US visa" },
  { country: "Ecuador", flag: "🇪🇨", notes: "90 days; US visa holders exempt" },
  { country: "Serbia", flag: "🇷🇸", notes: "30 days visa-free (Indian passport alone)" },
  { country: "Oman", flag: "🇴🇲", notes: "Visa on arrival with US GC; 14 days" },
  { country: "Bahrain", flag: "🇧🇭", notes: "e-Visa simplified with US visa" },
  { country: "South Korea", flag: "🇰🇷", notes: "Transit visa exemption with US visa (30 days)" },
  { country: "Malaysia", flag: "🇲🇾", notes: "Simplified eNTRI with US visa" },
];

/* ================================================================== */
/* US CITIZEN                                                         */
/* ================================================================== */

export const US_VISA_FREE: VisaCountryEntry[] = [
  { country: "United Kingdom", flag: "🇬🇧", notes: "6 months visa-free" },
  { country: "EU / Schengen Area", flag: "🇪🇺", notes: "90 days in any 180-day period (ETIAS coming)" },
  { country: "Japan", flag: "🇯🇵", notes: "90 days visa-free" },
  { country: "South Korea", flag: "🇰🇷", notes: "90 days visa-free (K-ETA waived)" },
  { country: "Canada", flag: "🇨🇦", notes: "6 months visa-free" },
  { country: "Mexico", flag: "🇲🇽", notes: "180 days visa-free" },
  { country: "Singapore", flag: "🇸🇬", notes: "90 days visa-free" },
  { country: "Israel", flag: "🇮🇱", notes: "90 days visa-free" },
  { country: "Thailand", flag: "🇹🇭", notes: "30 days visa-free" },
  { country: "Indonesia / Bali", flag: "🇮🇩", notes: "30 days VOA or visa-free (check current rules)" },
  { country: "Philippines", flag: "🇵🇭", notes: "30 days visa-free" },
  { country: "Malaysia", flag: "🇲🇾", notes: "90 days visa-free" },
  { country: "Taiwan", flag: "🇹🇼", notes: "90 days visa-free" },
  { country: "Hong Kong", flag: "🇭🇰", notes: "90 days visa-free" },
  { country: "Brazil", flag: "🇧🇷", notes: "Visa-free (changed 2024); 90 days" },
  { country: "Argentina", flag: "🇦🇷", notes: "90 days visa-free" },
  { country: "Chile", flag: "🇨🇱", notes: "90 days visa-free" },
  { country: "Colombia", flag: "🇨🇴", notes: "90 days visa-free" },
  { country: "Peru", flag: "🇵🇪", notes: "183 days visa-free" },
  { country: "Costa Rica", flag: "🇨🇷", notes: "90 days visa-free" },
  { country: "Panama", flag: "🇵🇦", notes: "180 days visa-free" },
  { country: "Turkey", flag: "🇹🇷", notes: "90 days visa-free" },
  { country: "Georgia", flag: "🇬🇪", notes: "1 year visa-free" },
  { country: "Morocco", flag: "🇲🇦", notes: "90 days visa-free" },
  { country: "South Africa", flag: "🇿🇦", notes: "90 days visa-free" },
  { country: "UAE / Dubai", flag: "🇦🇪", notes: "Visa-free; 30 days (extendable)" },
  { country: "Qatar", flag: "🇶🇦", notes: "Visa-free; 30 days" },
  { country: "Oman", flag: "🇴🇲", notes: "14 days visa-free" },
  { country: "Bahamas", flag: "🇧🇸", notes: "90 days visa-free" },
  { country: "Jamaica", flag: "🇯🇲", notes: "30 days visa-free" },
  { country: "Dominican Republic", flag: "🇩🇴", notes: "Tourist card $10; no visa" },
  { country: "Barbados", flag: "🇧🇧", notes: "6 months visa-free" },
  { country: "Fiji", flag: "🇫🇯", notes: "4 months visa-free" },
  { country: "Maldives", flag: "🇲🇻", notes: "30 days tourist visa on arrival; free" },
  { country: "Serbia", flag: "🇷🇸", notes: "90 days visa-free" },
  { country: "Albania", flag: "🇦🇱", notes: "1 year visa-free" },
  { country: "Montenegro", flag: "🇲🇪", notes: "90 days visa-free" },
  { country: "Bosnia & Herzegovina", flag: "🇧🇦", notes: "90 days visa-free" },
  { country: "Ecuador", flag: "🇪🇨", notes: "90 days visa-free" },
  { country: "Uruguay", flag: "🇺🇾", notes: "90 days visa-free" },
];

export const US_VOA: VisaCountryEntry[] = [
  { country: "Ethiopia", flag: "🇪🇹", notes: "VOA at Addis Ababa; $52" },
  { country: "Madagascar", flag: "🇲🇬", notes: "90 days; ~$27 fee" },
  { country: "Comoros", flag: "🇰🇲", notes: "45 days; fee applies" },
  { country: "Tuvalu", flag: "🇹🇻", notes: "30 days; free" },
  { country: "Mozambique", flag: "🇲🇿", notes: "30 days; $50 fee" },
  { country: "Timor-Leste", flag: "🇹🇱", notes: "30 days; $30 fee" },
  { country: "Togo", flag: "🇹🇬", notes: "7 days; ~$20 fee" },
  { country: "Palau", flag: "🇵🇼", notes: "30 days; free on arrival" },
  { country: "Cambodia", flag: "🇰🇭", notes: "30 days; $30 fee" },
  { country: "Laos", flag: "🇱🇦", notes: "30 days; $35–42 fee" },
  { country: "Nepal", flag: "🇳🇵", notes: "VOA at Tribhuvan; $30 for 15 days" },
  { country: "Jordan", flag: "🇯🇴", notes: "30 days; ~40 JOD (free with Jordan Pass)" },
  { country: "Seychelles", flag: "🇸🇨", notes: "30 days; free" },
  { country: "Bolivia", flag: "🇧🇴", notes: "VOA; ~$160 reciprocity fee" },
  { country: "Rwanda", flag: "🇷🇼", notes: "30 days; $50 fee" },
  { country: "Tanzania", flag: "🇹🇿", notes: "VOA; $50 fee" },
  { country: "Zimbabwe", flag: "🇿🇼", notes: "90 days; $30–55" },
  { country: "Samoa", flag: "🇼🇸", notes: "60 days; free" },
  { country: "Uganda", flag: "🇺🇬", notes: "VOA; $50 fee" },
  { country: "Mauritania", flag: "🇲🇷", notes: "VOA at Nouakchott; ~€55" },
  { country: "Guinea-Bissau", flag: "🇬🇼", notes: "VOA; varies" },
  { country: "Burundi", flag: "🇧🇮", notes: "VOA; $40 fee" },
  { country: "Burkina Faso", flag: "🇧🇫", notes: "VOA at airport" },
  { country: "Cape Verde", flag: "🇨🇻", notes: "VOA at airport" },
  { country: "Djibouti", flag: "🇩🇯", notes: "VOA; $23" },
];

export const US_ETA_REQUIRED: VisaCountryEntry[] = [
  { country: "Australia", flag: "🇦🇺", notes: "ETA (subclass 601); $20 AUD; approved instantly" },
  { country: "Canada", flag: "🇨🇦", notes: "eTA for flights; $7 CAD; valid 5 years" },
  { country: "India", flag: "🇮🇳", notes: "e-Visa online; $25; 30 days (or 5yr tourist)" },
  { country: "Kenya", flag: "🇰🇪", notes: "eTA online; ~$30; 90 days" },
  { country: "New Zealand", flag: "🇳🇿", notes: "NZeTA; $23 NZD; valid 2 years" },
  { country: "Sri Lanka", flag: "🇱🇰", notes: "ETA online; $35; 30 days" },
  { country: "Oman", flag: "🇴🇲", notes: "e-Visa; ~$13; 30 days" },
  { country: "Egypt", flag: "🇪🇬", notes: "e-Visa; $25; 30 days" },
  { country: "Myanmar", flag: "🇲🇲", notes: "e-Visa; $50; 28 days" },
  { country: "Vietnam", flag: "🇻🇳", notes: "e-Visa; $25; 30 days" },
  { country: "Bahrain", flag: "🇧🇭", notes: "e-Visa; ~14 BHD" },
  { country: "Côte d'Ivoire", flag: "🇨🇮", notes: "e-Visa; ~€73" },
  { country: "Pakistan", flag: "🇵🇰", notes: "e-Visa; limited categories" },
  { country: "Zambia", flag: "🇿🇲", notes: "e-Visa; $50" },
  { country: "Cameroon", flag: "🇨🇲", notes: "e-Visa required" },
  { country: "Nigeria", flag: "🇳🇬", notes: "e-Visa; $80; 30 days" },
  { country: "Azerbaijan", flag: "🇦🇿", notes: "ASAN e-Visa; $26; 30 days" },
  { country: "Benin", flag: "🇧🇯", notes: "e-Visa; €50" },
  { country: "EU / Schengen (ETIAS)", flag: "🇪🇺", notes: "ETIAS coming soon; ~€7; pre-travel authorization" },
  { country: "UK (ETA)", flag: "🇬🇧", notes: "UK ETA rolling out for some nationalities" },
];

export const US_VISA_REQUIRED: VisaCountryEntry[] = [
  { country: "China", flag: "🇨🇳", notes: "Tourist visa (L visa); $140; 10-year available" },
  { country: "Russia", flag: "🇷🇺", notes: "e-Visa (16 days) or full visa; $40–160" },
  { country: "Saudi Arabia", flag: "🇸🇦", notes: "e-Visa for tourism; ~$120" },
  { country: "North Korea", flag: "🇰🇵", notes: "US citizens banned from travel since 2017" },
  { country: "Iran", flag: "🇮🇷", notes: "VOA possible but strongly discouraged for US citizens" },
  { country: "Afghanistan", flag: "🇦🇫", notes: "Visa required; no US consular services" },
  { country: "Libya", flag: "🇱🇾", notes: "Visa required; travel advisory Level 4" },
  { country: "Syria", flag: "🇸🇾", notes: "Visa required; no US consular services" },
  { country: "Yemen", flag: "🇾🇪", notes: "Visa required; travel advisory Level 4" },
  { country: "Cuba", flag: "🇨🇺", notes: "Tourist visa (specific travel categories only); $100" },
  { country: "Eritrea", flag: "🇪🇷", notes: "Visa required; difficult to obtain" },
  { country: "Turkmenistan", flag: "🇹🇲", notes: "Visa + letter of invitation required" },
  { country: "Bhutan", flag: "🇧🇹", notes: "Visa via licensed tour operator; $100/day SDF" },
  { country: "Algeria", flag: "🇩🇿", notes: "Visa required; apply at embassy" },
  { country: "Angola", flag: "🇦🇴", notes: "Visa required; e-Visa available" },
  { country: "Chad", flag: "🇹🇩", notes: "Visa required" },
  { country: "Congo (DRC)", flag: "🇨🇩", notes: "Visa required" },
  { country: "Equatorial Guinea", flag: "🇬🇶", notes: "Visa required" },
  { country: "Ghana", flag: "🇬🇭", notes: "Visa required; $60" },
  { country: "Mali", flag: "🇲🇱", notes: "Visa required" },
  { country: "Niger", flag: "🇳🇪", notes: "Visa required" },
  { country: "South Sudan", flag: "🇸🇸", notes: "Visa required; Level 4 advisory" },
  { country: "Sudan", flag: "🇸🇩", notes: "Visa required" },
  { country: "Central African Republic", flag: "🇨🇫", notes: "Visa required; Level 4 advisory" },
  { country: "Nauru", flag: "🇳🇷", notes: "Visa required" },
];

/* ================================================================== */
/* GREEN CARD (Indian passport + US GC)                               */
/* ================================================================== */

export const GC_VISA_FREE: VisaCountryEntry[] = [
  { country: "Mexico", flag: "🇲🇽", notes: "180 days with valid US GC or visa" },
  { country: "Canada", flag: "🇨🇦", notes: "6 months; just need valid GC + passport" },
  { country: "Costa Rica", flag: "🇨🇷", notes: "30 days with valid US visa/GC" },
  { country: "Panama", flag: "🇵🇦", notes: "30–180 days with valid US visa/GC" },
  { country: "Philippines", flag: "🇵🇭", notes: "30 days visa-free with US GC" },
  { country: "Turkey", flag: "🇹🇷", notes: "e-Visa with US GC; $50; 30 days" },
  { country: "Georgia", flag: "🇬🇪", notes: "1 year visa-free with US GC" },
  { country: "Albania", flag: "🇦🇱", notes: "90 days with valid US visa/GC" },
  { country: "Colombia", flag: "🇨🇴", notes: "90 days with valid US visa/GC" },
  { country: "Peru", flag: "🇵🇪", notes: "183 days with valid US visa/GC" },
  { country: "Chile", flag: "🇨🇱", notes: "90 days with valid US visa" },
  { country: "Ecuador", flag: "🇪🇨", notes: "90 days; US GC holders exempt" },
  { country: "Bermuda", flag: "🇧🇲", notes: "Visa-free with US GC" },
  { country: "Aruba", flag: "🇦🇼", notes: "30 days visa-free with US visa/GC" },
  { country: "Curaçao", flag: "🇨🇼", notes: "30 days visa-free with US visa/GC" },
  { country: "Bonaire", flag: "🇧🇶", notes: "Visa-free with US visa/GC" },
  { country: "St. Maarten", flag: "🇸🇽", notes: "Visa-free with US visa/GC" },
  { country: "Turks & Caicos", flag: "🇹🇨", notes: "90 days with valid US visa/GC" },
  { country: "Belize", flag: "🇧🇿", notes: "30 days with valid US visa/GC" },
  { country: "Guatemala", flag: "🇬🇹", notes: "90 days with valid US visa" },
  { country: "Honduras", flag: "🇭🇳", notes: "90 days with valid US visa" },
  { country: "El Salvador", flag: "🇸🇻", notes: "90 days with valid US visa" },
  { country: "Nicaragua", flag: "🇳🇮", notes: "90 days with valid US visa" },
  { country: "Dominican Republic", flag: "🇩🇴", notes: "Tourist card $10; no visa needed" },
  { country: "Montenegro", flag: "🇲🇪", notes: "30 days with valid US visa/GC" },
  { country: "Bosnia & Herzegovina", flag: "🇧🇦", notes: "30 days with valid US visa/GC" },
  { country: "North Macedonia", flag: "🇲🇰", notes: "15 days with valid US visa/GC" },
  { country: "Kosovo", flag: "🇽🇰", notes: "15 days with valid US visa" },
  { country: "Paraguay", flag: "🇵🇾", notes: "Visa-free with US visa/GC" },
  { country: "Uruguay", flag: "🇺🇾", notes: "Visa-free with US visa/GC" },
  { country: "South Korea", flag: "🇰🇷", notes: "30 days transit exemption with US GC" },
  { country: "Serbia", flag: "🇷🇸", notes: "30 days visa-free (Indian passport alone)" },
  { country: "Thailand", flag: "🇹🇭", notes: "60 days visa-free (Indian passport alone)" },
  { country: "Indonesia", flag: "🇮🇩", notes: "30 days visa-free (Indian passport alone)" },
  { country: "Nepal", flag: "🇳🇵", notes: "Unlimited (Indian passport alone)" },
  { country: "Mauritius", flag: "🇲🇺", notes: "90 days visa-free (Indian passport alone)" },
  { country: "Fiji", flag: "🇫🇯", notes: "4 months visa-free (Indian passport alone)" },
  { country: "Oman", flag: "🇴🇲", notes: "14 days VOA with US GC" },
  { country: "Bahrain", flag: "🇧🇭", notes: "e-Visa simplified with US GC" },
  { country: "Malaysia", flag: "🇲🇾", notes: "eNTRI simplified with US GC" },
];

export const GC_VOA: VisaCountryEntry[] = [
  { country: "Bermuda", flag: "🇧🇲", notes: "Visa-free entry with US GC" },
  { country: "Maldives", flag: "🇲🇻", notes: "30 days tourist visa on arrival; free" },
  { country: "Seychelles", flag: "🇸🇨", notes: "30 days; free VOA" },
  { country: "Cambodia", flag: "🇰🇭", notes: "30 days; $30 VOA" },
  { country: "Laos", flag: "🇱🇦", notes: "30 days; $35–42 VOA" },
  { country: "Jordan", flag: "🇯🇴", notes: "30 days; ~40 JOD VOA" },
  { country: "Bolivia", flag: "🇧🇴", notes: "VOA; ~$52" },
  { country: "Madagascar", flag: "🇲🇬", notes: "90 days; ~$27 VOA" },
  { country: "Tanzania", flag: "🇹🇿", notes: "VOA; $50" },
  { country: "Rwanda", flag: "🇷🇼", notes: "30 days; $50 VOA" },
  { country: "Zimbabwe", flag: "🇿🇼", notes: "90 days; $30–55 VOA" },
  { country: "Montserrat", flag: "🇲🇸", notes: "VOA with US GC" },
  { country: "Suriname", flag: "🇸🇷", notes: "Tourist card; ~$25" },
  { country: "East Timor", flag: "🇹🇱", notes: "30 days; $30 VOA" },
  { country: "Palau", flag: "🇵🇼", notes: "30 days; free VOA" },
];

export const GC_E_VISA: VisaCountryEntry[] = [
  { country: "Turkey", flag: "🇹🇷", notes: "e-Visa with US GC; $50; 30 days" },
  { country: "Sri Lanka", flag: "🇱🇰", notes: "ETA online; $35; 30 days" },
  { country: "Australia", flag: "🇦🇺", notes: "e-Visa subclass 600; Indian passport; 1–4 weeks" },
  { country: "Kenya", flag: "🇰🇪", notes: "eTA online; ~$30; 90 days" },
  { country: "UAE / Dubai", flag: "🇦🇪", notes: "e-Visa or VOA; 14/30 days" },
  { country: "Vietnam", flag: "🇻🇳", notes: "e-Visa; $25; 30 days" },
  { country: "New Zealand", flag: "🇳🇿", notes: "NZeTA; $23 NZD (Indian passport)" },
  { country: "Egypt", flag: "🇪🇬", notes: "e-Visa; $25; 30 days" },
  { country: "Oman", flag: "🇴🇲", notes: "e-Visa; ~$13; 30 days" },
  { country: "Bahrain", flag: "🇧🇭", notes: "e-Visa; ~14 BHD" },
  { country: "Azerbaijan", flag: "🇦🇿", notes: "ASAN e-Visa; $26; 30 days" },
  { country: "Georgia", flag: "🇬🇪", notes: "e-Visa; $20; 30 days (or visa-free with GC)" },
  { country: "Ethiopia", flag: "🇪🇹", notes: "e-Visa; $52; 30 days" },
  { country: "Morocco", flag: "🇲🇦", notes: "e-Visa; processing 3–5 days" },
  { country: "Saudi Arabia", flag: "🇸🇦", notes: "e-Visa for tourism; ~$120" },
  { country: "Russia", flag: "🇷🇺", notes: "e-Visa; free; 16 days (select ports)" },
  { country: "Malaysia", flag: "🇲🇾", notes: "eNTRI; 15–30 days" },
  { country: "Myanmar", flag: "🇲🇲", notes: "e-Visa; $50; 28 days" },
  { country: "Uzbekistan", flag: "🇺🇿", notes: "e-Visa; free for some; 30 days" },
  { country: "Tajikistan", flag: "🇹🇯", notes: "e-Visa; $50; 45 days" },
  { country: "Armenia", flag: "🇦🇲", notes: "e-Visa; 120 days; free" },
  { country: "Kyrgyzstan", flag: "🇰🇬", notes: "e-Visa; $40; 30 days" },
  { country: "Moldova", flag: "🇲🇩", notes: "e-Visa; free; 90 days" },
  { country: "Nigeria", flag: "🇳🇬", notes: "e-Visa; $80; 30 days" },
  { country: "Zambia", flag: "🇿🇲", notes: "e-Visa; $50; 30 days" },
];

export const GC_VISA_REQUIRED: VisaCountryEntry[] = [
  { country: "Schengen / EU", flag: "🇪🇺", notes: "US GC does NOT waive Schengen visa — full application required" },
  { country: "United Kingdom", flag: "🇬🇧", notes: "UK visa required; GC doesn't help" },
  { country: "Japan", flag: "🇯🇵", notes: "Visa required for Indian passport; GC doesn't help" },
  { country: "Australia", flag: "🇦🇺", notes: "e-Visa required; GC doesn't help (but speeds processing)" },
  { country: "China", flag: "🇨🇳", notes: "Visa required; apply with Indian passport" },
  { country: "Russia", flag: "🇷🇺", notes: "e-Visa available but GC doesn't waive requirements" },
  { country: "South Korea", flag: "🇰🇷", notes: "Visa required (transit exemption only with GC)" },
  { country: "Brazil", flag: "🇧🇷", notes: "Visa required for Indian passport holders" },
  { country: "Singapore", flag: "🇸🇬", notes: "Visa required; GC may simplify e-Visa process" },
  { country: "Taiwan", flag: "🇹🇼", notes: "Transit visa exemption only; full stay needs visa" },
  { country: "South Africa", flag: "🇿🇦", notes: "Visa required; e-Visa pilot" },
  { country: "New Zealand", flag: "🇳🇿", notes: "NZeTA required; GC doesn't waive" },
  { country: "Morocco", flag: "🇲🇦", notes: "Visa required for Indian passport" },
  { country: "Egypt", flag: "🇪🇬", notes: "e-Visa available; GC doesn't change requirements" },
  { country: "Saudi Arabia", flag: "🇸🇦", notes: "e-Visa for tourism; GC doesn't change process" },
  { country: "Iran", flag: "🇮🇷", notes: "Visa required" },
  { country: "Iraq", flag: "🇮🇶", notes: "Visa required" },
  { country: "Afghanistan", flag: "🇦🇫", notes: "Visa required; travel advisory" },
  { country: "North Korea", flag: "🇰🇵", notes: "Extremely restricted" },
  { country: "Libya", flag: "🇱🇾", notes: "Visa required; travel advisory" },
  { country: "Syria", flag: "🇸🇾", notes: "Visa required; travel advisory" },
  { country: "Cuba", flag: "🇨🇺", notes: "Check US restrictions; need tourist card" },
  { country: "Ghana", flag: "🇬🇭", notes: "Visa required; $60" },
  { country: "Algeria", flag: "🇩🇿", notes: "Visa required" },
  { country: "Angola", flag: "🇦🇴", notes: "Visa required" },
];

/* ================================================================== */
/* Lookup map — status + category key → { meta, countries }           */
/* ================================================================== */

export type VisaListCategory = "visa-free" | "voa" | "e-visa" | "us-gc-perks" | "visa-free-gc" | "voa-gc" | "e-visa-gc" | "visa-required-gc" | "visa-required" | "e-visa-eta";

type VisaListData = {
  meta: VisaListMeta;
  countries: VisaCountryEntry[];
};

const ALL_LISTS: Record<string, Record<string, VisaListData>> = {
  "indian-passport": {
    "visa-free": {
      meta: { title: "Visa-Free Countries", subtitle: "for US Visa Holders (H-1B, B1/B2)", count: 25, color: "bg-green-500/10", textColor: "text-green-600", emoji: "🟢" },
      countries: IP_VISA_FREE,
    },
    "voa": {
      meta: { title: "Visa on Arrival Countries", subtitle: "for US Visa Holders (H-1B, B1/B2)", count: 30, color: "bg-yellow-500/10", textColor: "text-yellow-600", emoji: "🟡" },
      countries: IP_VOA,
    },
    "e-visa": {
      meta: { title: "e-Visa Available Countries", subtitle: "for US Visa Holders (H-1B, B1/B2)", count: 50, color: "bg-blue-500/10", textColor: "text-blue-600", emoji: "🔵" },
      countries: IP_E_VISA,
    },
    "us-gc-perks": {
      meta: { title: "US Green Card / Visa Perks", subtitle: "Countries accessible with valid US visa or Green Card", count: 35, color: "bg-purple-500/10", textColor: "text-purple-600", emoji: "🇺🇸" },
      countries: IP_US_GC_PERKS,
    },
  },
  "us-citizen": {
    "visa-free": {
      meta: { title: "Visa-Free Countries", subtitle: "for US Citizens", count: 185, color: "bg-green-500/10", textColor: "text-green-600", emoji: "🟢" },
      countries: US_VISA_FREE,
    },
    "voa": {
      meta: { title: "Visa on Arrival Countries", subtitle: "for US Citizens", count: 35, color: "bg-yellow-500/10", textColor: "text-yellow-600", emoji: "🟡" },
      countries: US_VOA,
    },
    "e-visa": {
      meta: { title: "e-Visa / ETA Required", subtitle: "for US Citizens", count: 25, color: "bg-blue-500/10", textColor: "text-blue-600", emoji: "🔵" },
      countries: US_ETA_REQUIRED,
    },
    "visa-required": {
      meta: { title: "Visa Required", subtitle: "for US Citizens", count: 30, color: "bg-red-500/10", textColor: "text-red-600", emoji: "🔴" },
      countries: US_VISA_REQUIRED,
    },
  },
  "green-card": {
    "visa-free-gc": {
      meta: { title: "Visa-Free Countries", subtitle: "for Green Card Holders", count: 40, color: "bg-green-500/10", textColor: "text-green-600", emoji: "🟢" },
      countries: GC_VISA_FREE,
    },
    "voa-gc": {
      meta: { title: "Visa on Arrival Countries", subtitle: "for Green Card Holders", count: 15, color: "bg-yellow-500/10", textColor: "text-yellow-600", emoji: "🟡" },
      countries: GC_VOA,
    },
    "e-visa-gc": {
      meta: { title: "e-Visa Available", subtitle: "for Green Card Holders", count: 50, color: "bg-blue-500/10", textColor: "text-blue-600", emoji: "🔵" },
      countries: GC_E_VISA,
    },
    "visa-required-gc": {
      meta: { title: "Still Need Visa", subtitle: "US Green Card does NOT help with these", count: 25, color: "bg-red-500/10", textColor: "text-red-600", emoji: "🔴" },
      countries: GC_VISA_REQUIRED,
    },
  },
};

export function getVisaList(status: string, category: string): VisaListData | null {
  return ALL_LISTS[status]?.[category] || null;
}

export function getVisaCategoriesForStatus(status: string): string[] {
  return Object.keys(ALL_LISTS[status] || {});
}

export function getAllStatusKeys(): string[] {
  return Object.keys(ALL_LISTS);
}
