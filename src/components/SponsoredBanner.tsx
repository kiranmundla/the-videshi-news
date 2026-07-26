import { useEffect, useState } from "react";

interface SponsoredListing {
  id: string;
  title: string;
  description: string;
  image_url: string;
  photos: string[];
  contact_name: string;
  contact_email: string;
  slug: string;
  subcategory?: string;
}

export default function SponsoredBanner() {
  const [listing, setListing] = useState<SponsoredListing | null>(null);
  const [activePhoto, setActivePhoto] = useState(0);

  useEffect(() => {
    fetch("/data/classifieds.json")
      .then((r) => r.json())
      .then((data: SponsoredListing[]) => {
        const sponsored = data.filter(
          (c: any) => c.category === "Sponsored" && c.status === "active"
        );
        if (sponsored.length > 0) {
          setListing(sponsored[Math.floor(Math.random() * sponsored.length)]);
        }
      })
      .catch(() => {});
  }, []);

  // Auto-rotate photos every 3s
  useEffect(() => {
    if (!listing?.photos?.length || listing.photos.length <= 1) return;
    const timer = setInterval(() => {
      setActivePhoto((p) => (p + 1) % listing.photos.length);
    }, 3000);
    return () => clearInterval(timer);
  }, [listing]);

  if (!listing) return null;

  const photos = listing.photos?.length ? listing.photos : listing.image_url ? [listing.image_url] : [];
  const truncatedDesc = listing.description.length > 180
    ? listing.description.slice(0, 180).replace(/\s+\S*$/, "") + "…"
    : listing.description;

  return (
    <div className="mx-auto max-w-5xl px-4 my-8">
      <div className="relative overflow-hidden rounded-xl border border-stone-200 bg-gradient-to-r from-stone-50 to-amber-50/30 shadow-sm">
        <div className="flex flex-col sm:flex-row items-stretch">
          {/* Photo carousel */}
          {photos.length > 0 && (
            <div className="relative sm:w-64 w-full h-80 sm:h-auto flex-shrink-0 overflow-hidden bg-stone-100">
              {photos.map((url, i) => (
                <img
                  key={url}
                  src={url}
                  alt={`${listing.title} - photo ${i + 1}`}
                  className="absolute inset-0 w-full h-full object-cover transition-opacity duration-700"
                  style={{ opacity: i === activePhoto ? 1 : 0 }}
                  loading={i === 0 ? "eager" : "lazy"}
                />
              ))}
              {photos.length > 1 && (
                <div className="absolute bottom-3 left-0 right-0 flex justify-center gap-1.5 z-10">
                  {photos.map((_, i) => (
                    <button
                      key={i}
                      onClick={() => setActivePhoto(i)}
                      className={`h-1.5 rounded-full transition-all ${
                        i === activePhoto
                          ? "bg-white w-4"
                          : "bg-white/50 hover:bg-white/70 w-1.5"
                      }`}
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Content */}
          <div className="flex-1 p-5 sm:p-6 flex flex-col justify-center">
            <div className="flex items-center gap-2 mb-2.5">
              <span className="text-[10px] font-semibold tracking-widest uppercase text-amber-700 bg-amber-100 px-2 py-0.5 rounded">
                Sponsored
              </span>
              {listing.subcategory && (
                <span className="text-[10px] text-stone-400 uppercase tracking-wide">
                  {listing.subcategory}
                </span>
              )}
            </div>
            <a href={`/classifieds/${listing.slug}`} className="block group">
              <h3 className="text-base sm:text-lg font-semibold text-[#0B1D3A] leading-snug mb-2 group-hover:text-[#A32D2F] transition-colors">
                {listing.title}
              </h3>
              <p className="text-sm text-stone-600 leading-relaxed mb-4">
                {truncatedDesc}
              </p>
            </a>
          </div>
        </div>

        {/* Ad marker */}
        <div className="absolute top-2.5 right-3 text-[9px] text-stone-300 tracking-wide uppercase">
          Ad
        </div>
      </div>
    </div>
  );
}
