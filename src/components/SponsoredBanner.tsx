import { useEffect, useState } from "react";

interface SponsoredListing {
  id: string;
  title: string;
  description: string;
  image_url: string;
  contact_name: string;
  contact_email: string;
  slug: string;
  subcategory?: string;
}

export default function SponsoredBanner() {
  const [listing, setListing] = useState<SponsoredListing | null>(null);

  useEffect(() => {
    fetch("/data/classifieds.json")
      .then((r) => r.json())
      .then((data: SponsoredListing[]) => {
        const sponsored = data.filter(
          (c: any) => c.category === "Sponsored" && c.status === "active"
        );
        if (sponsored.length > 0) {
          // Pick a random one if multiple
          setListing(sponsored[Math.floor(Math.random() * sponsored.length)]);
        }
      })
      .catch(() => {});
  }, []);

  if (!listing) return null;

  const truncatedDesc = listing.description.length > 160
    ? listing.description.slice(0, 160).replace(/\s+\S*$/, "") + "…"
    : listing.description;

  return (
    <div className="mx-auto max-w-5xl px-4 my-6">
      <div className="relative overflow-hidden rounded-xl border border-stone-200 bg-gradient-to-r from-stone-50 to-amber-50/30">
        <div className="flex flex-col sm:flex-row items-stretch">
          {/* Image */}
          {listing.image_url && (
            <div className="sm:w-48 w-full h-48 sm:h-auto flex-shrink-0">
              <img
                src={listing.image_url}
                alt={listing.title}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
          )}

          {/* Content */}
          <div className="flex-1 p-4 sm:p-5 flex flex-col justify-center">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[10px] font-semibold tracking-widest uppercase text-amber-700 bg-amber-100 px-2 py-0.5 rounded">
                Sponsored
              </span>
              {listing.subcategory && (
                <span className="text-[10px] text-stone-400 uppercase tracking-wide">
                  {listing.subcategory}
                </span>
              )}
            </div>
            <h3 className="text-base sm:text-lg font-semibold text-[#0B1D3A] leading-snug mb-1.5">
              {listing.title}
            </h3>
            <p className="text-sm text-stone-600 leading-relaxed mb-3">
              {truncatedDesc}
            </p>
            <a
              href={`/classifieds/${listing.slug}`}
              className="inline-flex items-center text-sm font-medium text-[#A32D2F] hover:text-[#8a2426] transition-colors"
            >
              Learn more
              <svg className="w-3.5 h-3.5 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </a>
          </div>
        </div>

        {/* Subtle branding */}
        <div className="absolute top-2 right-3 text-[9px] text-stone-300 tracking-wide uppercase">
          Ad
        </div>
      </div>
    </div>
  );
}
