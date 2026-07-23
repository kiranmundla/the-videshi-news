import { useEffect, useState } from "react";
import ScrollWrap from "./ScrollWrap";

interface TweetEntry {
  tweet_url: string;
  handle: string;
  tweet_id: string;
  category: string;
  article_slug: string;
  article_headline: string;
  photos?: string[];
}

interface SocialFeed {
  categories: Record<string, TweetEntry[]>;
}

interface TweetScrollProps {
  category: string;
  label?: string;
}

/* Known display names for VVIPs — avoid showing raw handles */
const DISPLAY_NAMES: Record<string, string> = {
  // Tech
  sundarpichai: "Sundar Pichai",
  satyanadella: "Satya Nadella",
  sama: "Sam Altman",
  elonmusk: "Elon Musk",
  tim_cook: "Tim Cook",
  nandannilekani: "Nandan Nilekani",
  // Bollywood
  iamsrk: "Shah Rukh Khan",
  priyankachopra: "Priyanka Chopra",
  akshaykumar: "Akshay Kumar",
  diljitdosanjh: "Diljit Dosanjh",
  aliaa08: "Alia Bhatt",
  srbachchan: "Amitabh Bachchan",
  arrahman: "AR Rahman",
  beingsalmankhan: "Salman Khan",
  shahidkapoor: "Shahid Kapoor",
  juniorbachchan: "Abhishek Bachchan",
  anilkapoor: "Anil Kapoor",
  ajaydevgn: "Ajay Devgn",
  faroutakhtar: "Farhan Akhtar",
  theaaryankartik: "Kartik Aaryan",
  varundhawan: "Varun Dhawan",
  // South stars
  ssrajamouli: "SS Rajamouli",
  tarak9999: "Jr NTR",
  alwaysramcharan: "Ram Charan",
  iamrashmika: "Rashmika Mandanna",
  // Diaspora entertainers
  jayshetty: "Jay Shetty",
  // Sports — Cricket
  imvkohli: "Virat Kohli",
  imro45: "Rohit Sharma",
  sachin_rt: "Sachin Tendulkar",
  sganguly99: "Sourav Ganguly",
  harbhajan_singh: "Harbhajan Singh",
  rishabhpant17: "Rishabh Pant",
  shubmangill: "Shubman Gill",
  mohammadkaif: "Mohammad Kaif",
  ajinkyarahane88: "Ajinkya Rahane",
  irfanpathan: "Irfan Pathan",
  // Sports — Olympic / other
  neeraj_chopra1: "Neeraj Chopra",
  pvsindhu1: "PV Sindhu",
  realmanubhaker: "Manu Bhaker",
  nikhat_zareen: "Nikhat Zareen",
  // Indian politics
  narendramodi: "Narendra Modi",
  drsjaishankar: "S Jaishankar",
  amitshah: "Amit Shah",
  nsitharaman: "Nirmala Sitharaman",
  rahulgandhi: "Rahul Gandhi",
  myogiadityanath: "Yogi Adityanath",
  mamataofficial: "Mamata Banerjee",
  arvindkejriwal: "Arvind Kejriwal",
  pmoindia: "PMO India",
  rashtrapatibhvn: "President of India",
  piyushgoyal: "Piyush Goyal",
  rajnathsingh: "Rajnath Singh",
  shashitharoor: "Shashi Tharoor",
  jpnadda: "JP Nadda",
  nitishkumar: "Nitish Kumar",
  // World leaders
  realdonaldtrump: "Donald Trump",
  vp: "JD Vance",
  whitehouse: "The White House",
  secrubio: "Marco Rubio",
  barackobama: "Barack Obama",
  michelleobama: "Michelle Obama",
  "10downingstreet": "10 Downing Street",
  rishisunak: "Rishi Sunak",
  justintrudeau: "Justin Trudeau",
  zelenskyyua: "Volodymyr Zelenskyy",
  emmanuelmacron: "Emmanuel Macron",
};

function getDisplayName(handle: string): string {
  return DISPLAY_NAMES[handle.toLowerCase()] || handle;
}

function getInitials(handle: string): string {
  const name = DISPLAY_NAMES[handle.toLowerCase()];
  if (name) {
    const parts = name.split(" ");
    return parts.length > 1
      ? parts[0][0] + parts[parts.length - 1][0]
      : parts[0][0];
  }
  return handle.charAt(0).toUpperCase();
}

/** Decode common HTML entities from tweet text */
function decodeEntities(s: string): string {
  return s
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

/** Get tweet text from either field, strip trailing t.co URLs, skip URL-only tweets */
function getTweetText(t: TweetEntry): string {
  const raw = (t.article_headline || (t as any).text || "").trim();
  if (!raw) return "";
  // Strip trailing t.co links
  const cleaned = raw.replace(/\s*https?:\/\/t\.co\/\S+\s*$/g, "").trim();
  // If nothing left after stripping URLs, it was a URL-only tweet
  if (!cleaned) return "";
  return decodeEntities(cleaned);
}

export default function TweetScroll({ category, label }: TweetScrollProps) {
  const [tweets, setTweets] = useState<TweetEntry[]>([]);

  useEffect(() => {
    fetch(`/data/social-feed.json?v=${Date.now()}`)
      .then((r) => r.json())
      .then((data: SocialFeed) => {
        const catTweets = data.categories?.[category] || [];
        setTweets(catTweets);
      })
      .catch(() => {});
  }, [category]);

  if (tweets.length === 0) return null;

  // Only show tweets from recognized VVIP handles with actual text content
  const displayTweets = tweets.filter((t) => {
    // Must be a recognized handle
    if (!DISPLAY_NAMES[t.handle.toLowerCase()]) return false;
    // Must have usable text
    return getTweetText(t).length > 0;
  });
  if (displayTweets.length === 0) return null;

  const displayLabel =
    label ||
    category.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <section className="v2-social-strip">
      <div className="container">
        {/* Header */}
        <div className="flex items-center gap-2.5 mb-4">
          <div className="v2-social-x-badge">
            <svg viewBox="0 0 24 24" width="11" height="11" fill="currentColor">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
            </svg>
          </div>
          <span
            className="text-[11px] font-bold tracking-[1.5px] uppercase"
            style={{ color: "#64748B" }}
          >
            What people are saying · {displayLabel}
          </span>
        </div>

        {/* Quote strip scroll */}
        <ScrollWrap className="v2-social-scroll">
          {displayTweets.map((t) => (
            <a
              key={t.tweet_id}
              href={t.tweet_url}
              target="_blank"
              rel="noopener noreferrer"
              className="v2-tweet-quote group"
            >
              {/* Tweet text as quote */}
              <p className="v2-tweet-quote-text">
                "{getTweetText(t)}"
              </p>

              {/* Tweet image thumbnail */}
              {t.photos && t.photos.length > 0 && (
                <div className="v2-tweet-quote-img">
                  <img
                    src={t.photos[0]}
                    alt=""
                    loading="lazy"
                  />
                </div>
              )}

              {/* Attribution row */}
              <div className="v2-tweet-quote-attr">
                <div className="v2-tweet-quote-avatar">
                  {getInitials(t.handle)}
                </div>
                <div className="v2-tweet-quote-meta">
                  <span className="v2-tweet-quote-name">
                    {getDisplayName(t.handle)}
                  </span>
                  <span className="v2-tweet-quote-handle">@{t.handle}</span>
                </div>
                <svg
                  viewBox="0 0 24 24"
                  width="13"
                  height="13"
                  fill="#94A3B8"
                  className="flex-shrink-0 ml-auto opacity-50 group-hover:opacity-100 transition-opacity"
                >
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </div>
            </a>
          ))}
        </ScrollWrap>
      </div>
    </section>
  );
}
