import { useState, useRef, useCallback } from "react";

interface ZoomableImageProps {
  src: string;
  alt: string;
  className?: string;
  caption?: string;
}

/**
 * Tap to expand fullscreen, double-tap to zoom in/out, scroll to pan.
 * Drop-in replacement for any <img> that should be zoomable.
 */
export default function ZoomableImage({ src, alt, className = "", caption }: ZoomableImageProps) {
  const [expanded, setExpanded] = useState(false);
  const [zoomed, setZoomed] = useState(false);
  const lastTapRef = useRef(0);

  const handleImageInteraction = useCallback((e: React.TouchEvent | React.MouseEvent) => {
    e.stopPropagation();
    const now = Date.now();
    if (now - lastTapRef.current < 300) {
      setZoomed((z) => !z);
    }
    lastTapRef.current = now;
  }, []);

  const close = () => { setExpanded(false); setZoomed(false); };

  return (
    <>
      <img
        src={src}
        alt={alt}
        className={`${className} cursor-zoom-in`}
        onClick={() => setExpanded(true)}
        loading="lazy"
      />

      {expanded && (
        <div
          className="fixed inset-0 z-50 bg-black flex flex-col"
          onClick={close}
        >
          <div className="flex items-center justify-between px-4 py-3 shrink-0">
            {caption ? (
              <p className="text-white text-sm truncate mr-4">{caption}</p>
            ) : <span />}
            <button
              onClick={close}
              className="text-white text-2xl font-bold w-10 h-10 flex items-center justify-center shrink-0"
              aria-label="Close"
            >
              ✕
            </button>
          </div>
          <div
            className="flex-1 overflow-auto"
            style={{ WebkitOverflowScrolling: "touch" }}
          >
            <img
              src={src}
              alt={alt}
              className={`block transition-all duration-200 ${
                zoomed ? "w-[250vw] md:w-[180vw]" : "w-full md:max-w-4xl md:mx-auto"
              }`}
              onClick={handleImageInteraction}
              onTouchEnd={handleImageInteraction}
            />
          </div>
        </div>
      )}
    </>
  );
}
