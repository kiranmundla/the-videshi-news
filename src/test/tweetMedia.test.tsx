import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// react-tweet pulls a CSS module vitest's node pipeline can't load; the
// static-first paths under test never call the runtime hook.
vi.mock("react-tweet", () => ({
  useTweet: () => ({ data: undefined, isLoading: true, error: undefined }),
}));

// jsdom doesn't implement Element.scrollTo (the shared Lightbox calls
// it on open); real browsers have it.
(Element.prototype as unknown as { scrollTo: () => void }).scrollTo = () => {};
import { TweetPhotos, TweetVideoPlayer } from "@/components/TweetMedia";
import { MinimalTweetEmbed } from "@/components/SocialEmbed";
import type { TweetPhoto, TweetVideo, StaticTweet } from "@/lib/tweetMedia";

/* Fixtures mirror real syndication payloads captured 2026-10-31:
   - filmibeat 2116392868839592325: X mixed-media tweet (3 photos + video)
   - ANI 2116187900660601083: video tweet, 16:9, 0:55 */

const PHOTOS: TweetPhoto[] = [
  { url: "https://pbs.twimg.com/media/HV7wDW7akAA9u5G.jpg?format=jpg&name=large", width: 1024, height: 1280 },
  { url: "https://pbs.twimg.com/media/HV7wDXObMAAbHE2.jpg?format=jpg&name=large", width: 1024, height: 1280 },
  { url: "https://pbs.twimg.com/media/HV7wDW4b0AAdwuE.jpg?format=jpg&name=large", width: 1024, height: 1280 },
];

const ANI_VIDEO: TweetVideo = {
  poster: "https://pbs.twimg.com/amplify_video_thumb/2116187133878976513/img/OrelT60UM0zxZfNO.jpg",
  aspect: [16, 9],
  duration_ms: 54992,
  type: "video",
};

const FILMIBEAT_URL = "https://x.com/filmibeat/status/2116392868839592325";
const ANI_URL = "https://x.com/ANI/status/2116187900660601083";

const STATIC_MAP: Record<string, StaticTweet> = {
  "2116392868839592325": {
    id: "2116392868839592325",
    url: FILMIBEAT_URL,
    text: "From Desi Beats to Glamorous Looks, Priyanka-Nick’s LA Diwali Celebration Wins Hearts!😍\n\nPriyanka Chopra and Nick Jonas brought a touch of desi glamour to Los Angeles https://t.co/UuVzAnDYd3",
    created_at: "2026-10-31T04:52:35.000Z",
    favorite_count: 11,
    conversation_count: 0,
    user: { name: "FilmiBeat", screen_name: "filmibeat", avatar: "https://pbs.twimg.com/profile_images/1942924359313575936/iDUz6oVV_normal.jpg", verified: true, verified_type: null },
    photos: PHOTOS,
    video: { poster: "https://pbs.twimg.com/amplify_video_thumb/2116392815412510720/img/Tc7Hs1uf16reEQ.jpg", aspect: [4, 5], duration_ms: 30000, type: "video" },
    media_count: 4,
  },
  "2116187900660601083": {
    id: "2116187900660601083",
    url: ANI_URL,
    text: "#WATCH | Hyderabad | German Consul General in Chennai, Michael Hasper, says, \"Indo-German relations are thriving.\" https://t.co/UV7k4YAiHD",
    created_at: "2026-10-30T15:18:07.000Z",
    favorite_count: 9,
    conversation_count: 0,
    user: { name: "ANI", screen_name: "ANI", avatar: "https://pbs.twimg.com/profile_images/1497864299/ani_mic_logo_normal.jpg", verified: true, verified_type: "Business" },
    photos: [],
    video: ANI_VIDEO,
    media_count: 1,
  },
};

describe("TweetPhotos — in-place photo browsing", () => {
  it("renders a swipeable strip with the counter pill for >1 photo", () => {
    const { container } = render(
      <TweetPhotos photos={PHOTOS} tweetUrl={FILMIBEAT_URL} authorLabel="@filmibeat on X" />,
    );
    // Kiran's scroll signal: counter pill present
    expect(screen.getByText("1 / 3")).toBeInTheDocument();
    const imgs = Array.from(container.querySelectorAll("img")).filter((i) =>
      (i.getAttribute("src") || "").includes("pbs.twimg.com/media/"),
    );
    expect(imgs).toHaveLength(3);
    // Largest served size is used
    expect(imgs[0].getAttribute("src")).toContain("name=large");
  });

  it("opens the full-screen lightbox when a strip photo is tapped", async () => {
    const { container } = render(
      <TweetPhotos photos={PHOTOS} tweetUrl={FILMIBEAT_URL} authorLabel="@filmibeat on X" />,
    );
    const first = container.querySelector("img");
    expect(first).not.toBeNull();
    fireEvent.click(first!);
    // Lightbox footer carries the View on X attribution link
    const link = await screen.findByRole("link", { name: /View on X/ });
    expect(link.getAttribute("href")).toBe(FILMIBEAT_URL);
  });

  it("renders a single photo in place, tap opens the lightbox", async () => {
    render(<TweetPhotos photos={[PHOTOS[0]]} tweetUrl={FILMIBEAT_URL} />);
    const btn = screen.getByRole("button", { name: /full screen/i });
    expect(btn).toBeInTheDocument();
    fireEvent.click(btn);
    expect(await screen.findByRole("link", { name: /View on X/ })).toBeInTheDocument();
  });
});

describe("TweetVideoPlayer — click-to-load official embed", () => {
  afterEach(() => {
    vi.useRealTimers();
    document.getElementById("twitter-wjs")?.remove();
  });

  it("shows poster + play + duration, and does NOT load widgets.js", () => {
    const { container } = render(<TweetVideoPlayer url={ANI_URL} video={ANI_VIDEO} dark />);
    expect(screen.getByRole("button", { name: /play video/i })).toBeInTheDocument();
    expect(screen.getByText("0:55")).toBeInTheDocument();
    expect(container.querySelector("img")?.getAttribute("src")).toContain("amplify_video_thumb");
    // Speed rule: the X widget script must not be fetched before a tap
    expect(document.querySelector('script[src*="platform.x.com"]')).toBeNull();
  });

  it("tap swaps in the official embed (blockquote + widgets.js)", async () => {
    render(<TweetVideoPlayer url={ANI_URL} video={ANI_VIDEO} dark />);
    fireEvent.click(screen.getByRole("button", { name: /play video/i }));
    // XOfficialEmbed mounts: blockquote for widgets.js + the script tag
    expect(document.querySelector("blockquote.twitter-tweet")).not.toBeNull();
    expect(document.querySelector('script[src*="platform.x.com/widgets.js"]')).not.toBeNull();
  });

  it("falls back to the link-out poster card when the widget never renders", async () => {
    vi.useFakeTimers();
    render(<TweetVideoPlayer url={ANI_URL} video={ANI_VIDEO} dark />);
    fireEvent.click(screen.getByRole("button", { name: /play video/i }));
    expect(document.querySelector("blockquote.twitter-tweet")).not.toBeNull();
    // jsdom never executes widgets.js → no iframe → watchdog (9s) fires
    await act(async () => {
      vi.advanceTimersByTime(9500);
    });
    expect(screen.getByText(/couldn’t load here/)).toBeInTheDocument();
    const links = screen.getAllByRole("link");
    expect(links.some((l) => l.getAttribute("href") === ANI_URL)).toBe(true);
  });
});

describe("MinimalTweetEmbed — static-first rendering", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({ ok: true, json: async () => STATIC_MAP })),
    );
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders a mixed-media tweet from static JSON: photo strip AND video poster", async () => {
    const { container } = render(<MinimalTweetEmbed url={FILMIBEAT_URL} />);
    expect(
      await screen.findByText((c) => c.includes("Priyanka Chopra and Nick Jonas")),
    ).toBeInTheDocument();
    // Static JSON was the only fetch — no runtime syndication call
    expect(vi.mocked(fetch)).toHaveBeenCalledWith("/data/tweet-media.json");
    const mediaImgs = Array.from(container.querySelectorAll("img")).filter((i) =>
      (i.getAttribute("src") || "").includes("pbs.twimg.com/media/"),
    );
    expect(mediaImgs.length).toBe(3);
    expect(screen.getByText("1 / 3")).toBeInTheDocument();
    // Mixed media: the video poster + play button renders alongside photos
    expect(screen.getByRole("button", { name: /play video/i })).toBeInTheDocument();
    expect(screen.getByText("View on X →")).toBeInTheDocument();
  });

  it("renders a video tweet from static JSON with its duration chip", async () => {
    render(<MinimalTweetEmbed url={ANI_URL} />);
    expect(
      await screen.findByText((c) => c.includes("German Consul General")),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /play video/i })).toBeInTheDocument();
    expect(screen.getByText("0:55")).toBeInTheDocument();
    // widgets.js still untouched until a tap
    expect(document.querySelector('script[src*="platform.x.com"]')).toBeNull();
  });
});
