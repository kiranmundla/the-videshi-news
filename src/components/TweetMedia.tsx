import { useEffect, useRef, useState } from "react";
import PhotoScrollStrip from "@/components/PhotoScrollStrip";
import Lightbox from "@/components/Lightbox";
import XOfficialEmbed from "@/components/XOfficialEmbed";
import type { TweetPhoto, TweetVideo } from "@/lib/tweetMedia";

/* ── In-place X media for article tweet cards ───────────────────────
   Photos: rendered in place — a swipeable strip (PhotoScrollStrip:
   counter pill + arrows + peeking next photo, proximity snap,
   start-align, NO edge-fade overlays) when there is more than one,
   a single in-place photo otherwise; tapping any photo opens the
   shared full-screen Lightbox.

   Video: static poster + play button first; tapping play swaps in
   X's OFFICIAL embed (widgets.js) in place — click-to-load, so
   widgets.js is fetched only on tap, never on initial page load.
   If the widget produces no iframe within the watchdog window, we
   fall back to the previous behavior: the poster card links to X. */

function formatDuration(ms: number): string {
  if (!ms) return "";
  const total = Math.round(ms / 1000);
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function PlayBadge({ size = 56 }: { size?: number }) {
  return (
    <div
      style={{
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        width: size,
        height: size,
        borderRadius: "50%",
        background: "rgba(29, 161, 242, 0.92)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        boxShadow: "0 4px 18px rgba(0,0,0,0.35)",
        pointerEvents: "none",
      }}
    >
      <svg width={size * 0.42} height={size * 0.42} viewBox="0 0 24 24" fill="white">
        <path d="M8 5v14l11-7z" />
      </svg>
    </div>
  );
}

/* ── Photos ── */

interface TweetPhotosProps {
  photos: TweetPhoto[];
  tweetUrl: string;
  authorLabel?: string;
  dark?: boolean;
}

export function TweetPhotos({ photos, tweetUrl, authorLabel, dark }: TweetPhotosProps) {
  const [lbIndex, setLbIndex] = useState<number | null>(null);
  if (!photos.length) return null;

  const stripPhotos = photos.map((p) => ({ src: p.url, caption: "" }));
  const bg = dark ? "#0a0a0a" : "#f0eeeb";

  return (
    <>
      {photos.length === 1 ? (
        <button
          type="button"
          onClick={() => setLbIndex(0)}
          aria-label="View photo full screen"
          style={{
            display: "block",
            width: "100%",
            padding: 0,
            border: "none",
            background: bg,
            cursor: "zoom-in",
          }}
        >
          <img
            src={photos[0].url}
            alt=""
            loading="lazy"
            style={{
              width: "100%",
              height: "auto",
              maxHeight: 520,
              objectFit: "contain",
              display: "block",
              background: bg,
            }}
          />
        </button>
      ) : (
        <PhotoScrollStrip
          photos={stripPhotos}
          itemWidth={300}
          itemHeight={250}
          objectFit="cover"
          onPhotoClick={(_, i) => setLbIndex(i)}
        />
      )}

      <Lightbox
        open={lbIndex !== null}
        initialIndex={lbIndex ?? 0}
        count={photos.length}
        onClose={() => setLbIndex(null)}
        renderSlide={(i) => (
          <img
            src={photos[i]?.url || ""}
            alt=""
            draggable={false}
            style={
              {
                maxWidth: "calc(100vw - 40px)",
                maxHeight: "calc(100vh - 220px)",
                objectFit: "contain",
                borderRadius: "8px",
                userSelect: "none",
                WebkitUserSelect: "none",
              } as React.CSSProperties
            }
          />
        )}
        renderBelow={() => (
          <div style={{ padding: "10px 20px 0", textAlign: "center" }}>
            {authorLabel && (
              <div
                style={{
                  color: "rgba(255,255,255,0.65)",
                  fontSize: 12,
                  marginBottom: 10,
                }}
              >
                {authorLabel}
              </div>
            )}
            <a
              href={tweetUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                background: "#fff",
                color: "#000",
                fontSize: 13,
                fontWeight: 700,
                padding: "9px 20px",
                borderRadius: 999,
                textDecoration: "none",
              }}
            >
              View on X <span>↗</span>
            </a>
          </div>
        )}
      />
    </>
  );
}

/* ── Video (click-to-load official embed) ── */

interface TweetVideoPlayerProps {
  url: string;
  video: TweetVideo;
  dark?: boolean;
}

export function TweetVideoPlayer({ url, video, dark }: TweetVideoPlayerProps) {
  const [state, setState] = useState<"poster" | "embed" | "failed">("poster");
  const wrapRef = useRef<HTMLDivElement>(null);

  // Watchdog: the official widget replaces the blockquote with an
  // iframe. If that hasn't happened shortly after tap, fall back to
  // the link-out poster card instead of leaving a blank box.
  useEffect(() => {
    if (state !== "embed") return;
    const el = wrapRef.current;
    if (!el) return;
    let settled = false;
    const finish = (ok: boolean) => {
      if (settled) return;
      settled = true;
      observer.disconnect();
      clearTimeout(timer);
      if (!ok) setState("failed");
    };
    const check = () => {
      if (el.querySelector("iframe")) finish(true);
    };
    const observer = new MutationObserver(check);
    observer.observe(el, { childList: true, subtree: true });
    check();
    const timer = setTimeout(() => finish(!!el.querySelector("iframe")), 9000);
    return () => {
      settled = true;
      observer.disconnect();
      clearTimeout(timer);
    };
  }, [state]);

  const [aw, ah] = video.aspect?.length === 2 ? video.aspect : [16, 9];
  const duration = formatDuration(video.duration_ms);

  const posterInner = (
    <>
      <img
        src={video.poster}
        alt="Video thumbnail"
        loading="lazy"
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          display: "block",
        }}
      />
      <PlayBadge size={dark ? 60 : 52} />
      {duration && (
        <span
          style={{
            position: "absolute",
            right: 8,
            bottom: 8,
            background: "rgba(0,0,0,0.75)",
            color: "#fff",
            fontSize: 12,
            fontWeight: 600,
            padding: "2px 7px",
            borderRadius: 6,
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {duration}
        </span>
      )}
    </>
  );

  const posterBoxStyle: React.CSSProperties = {
    position: "relative",
    display: "block",
    width: "100%",
    aspectRatio: `${aw} / ${ah}`,
    maxHeight: 520,
    overflow: "hidden",
    background: "#000",
    border: "none",
    padding: 0,
  };

  if (state === "embed") {
    return (
      <div ref={wrapRef}>
        <XOfficialEmbed url={url} video bare />
        <div
          style={{
            textAlign: "center",
            fontSize: 12,
            color: dark ? "rgba(255,255,255,0.4)" : "#999",
            padding: "6px 0 2px",
          }}
        >
          Loading player from X…
        </div>
      </div>
    );
  }

  if (state === "failed") {
    // Graceful fallback = the pre-existing behavior: poster links to X.
    return (
      <div>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          style={{ ...posterBoxStyle, cursor: "pointer" }}
        >
          {posterInner}
        </a>
        <div
          style={{
            fontSize: 12,
            color: dark ? "rgba(255,255,255,0.45)" : "#999",
            padding: "6px 2px 0",
          }}
        >
          The X player couldn’t load here — tap the video to watch on X.
        </div>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={() => setState("embed")}
      aria-label="Play video"
      style={{ ...posterBoxStyle, cursor: "pointer" }}
    >
      {posterInner}
    </button>
  );
}
