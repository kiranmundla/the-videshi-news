import { useEffect, useState } from "react";
import ScrollWrap from "./ScrollWrap";

interface TweetEntry {
  tweet_url: string;
  handle: string;
  tweet_id: string;
  category: string;
  article_slug: string;
  article_headline: string;
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
  sundarpichai: "Sundar Pichai",
  satyanadella: "Satya Nadella",
  sama: "Sam Altman",
  elonmusk: "Elon Musk",
  tim_cook: "Tim Cook",
  nandannilekani: "Nandan Nilekani",
  iamsrk: "Shah Rukh Khan",
  priyankachopra: "Priyanka Chopra",
  deepikapadukone: "Deepika Padukone",
  akshaykumar: "Akshay Kumar",
  karanjohar: "Karan Johar",
  diljitdosanjh: "Diljit Dosanjh",
  aliaa08: "Alia Bhatt",
  srbachchan: "Amitabh Bachchan",
  ranveerofficial: "Ranveer Singh",
  arrahman: "AR Rahman",
  anushkasharma: "Anushka Sharma",
  ssrajamouli: "SS Rajamouli",
  tarak9999: "Jr NTR",
  alwaysramcharan: "Ram Charan",
  actorprabhas: "Prabhas",
  iamrashmika: "Rashmika Mandanna",
  beingsalmankhan: "Salman Khan",
  vickykaushal09: "Vicky Kaushal",
  shahidkapoor: "Shahid Kapoor",
  kritisanon: "Kriti Sanon",
  imvkohli: "Virat Kohli",
  imro45: "Rohit Sharma",
  sachin_rt: "Sachin Tendulkar",
  jaspritbumrah93: "Jasprit Bumrah",
  hardikpandya7: "Hardik Pandya",
  neeraj_chopra1: "Neeraj Chopra",
  sganguly99: "Sourav Ganguly",
  pvsindhu1: "PV Sindhu",
  mirzasania: "Sania Mirza",
  dgukesh: "D Gukesh",
  chetrisunil11: "Sunil Chhetri",
  smriti_mandhana: "Smriti Mandhana",
  rishabhpant17: "Rishabh Pant",
  shubmangill: "Shubman Gill",
  imjadeja: "Ravindra Jadeja",
  klrahul: "KL Rahul",
  realmanubhaker: "Manu Bhaker",
  nikhat_zareen: "Nikhat Zareen",
  harbhajan_singh: "Harbhajan Singh",
  mohammadkaif: "Mohammad Kaif",
  ajinkyarahane88: "Ajinkya Rahane",
  irfanpathan: "Irfan Pathan",
  juniorbachchan: "Abhishek Bachchan",
  anilkapoor: "Anil Kapoor",
  ajaydevgn: "Ajay Devgn",
  anupampkher: "Anupam Kher",
  sonamakapoor: "Sonam Kapoor",
  faroutakhtar: "Farhan Akhtar",
  aamirkhan: "Aamir Khan",
  mindykaling: "Mindy Kaling",
  hasanminhaj: "Hasan Minhaj",
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
  secblinken: "Antony Blinken",
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

/* Accent colours per category for the card top stripe */
const CATEGORY_ACCENTS: Record<string, string> = {
  technology: "#4527A0",
  entertainment: "#AD1457",
  sports: "#1B5E20",
  news: "#0B1D3A",
  immigration: "#B71C1C",
  "nri-world": "#E65100",
  "markets-finance": "#004D40",
  "world-leaders": "#1565C0",
};

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

  const displayLabel =
    label ||
    category.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  const accent = CATEGORY_ACCENTS[category] || "#0B1D3A";

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

        {/* Scroll strip */}
        <ScrollWrap className="v2-social-scroll">
          {tweets.map((t) => (
            <a
              key={t.tweet_id}
              href={t.tweet_url}
              target="_blank"
              rel="noopener noreferrer"
              className="v2-tweet-card group"
              style={{ '--tweet-accent': accent } as React.CSSProperties}
            >
              {/* Left accent bar via CSS ::before */}
              <div className="v2-tweet-card-stripe" />

              {/* Content */}
              <div className="v2-tweet-card-body">
                {/* Avatar + name block */}
                <div className="flex items-center gap-3 mb-3">
                  <div className="v2-tweet-avatar" style={{ background: accent }}>
                    {getInitials(t.handle)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="v2-tweet-name">{getDisplayName(t.handle)}</p>
                    <p className="v2-tweet-handle">@{t.handle}</p>
                  </div>
                  <svg
                    viewBox="0 0 24 24"
                    width="15"
                    height="15"
                    fill="#64748B"
                    className="flex-shrink-0 opacity-60 group-hover:opacity-100 transition-opacity"
                  >
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                  </svg>
                </div>

                {/* Tweet text */}
                <p className="v2-tweet-text">{t.article_headline}</p>

                {/* Footer */}
                <div className="v2-tweet-footer">
                  <span className="v2-tweet-cta group-hover:opacity-80 transition-opacity">
                    View on X
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: 3 }}>
                      <polyline points="9 6 15 12 9 18" />
                    </svg>
                  </span>
                </div>
              </div>
            </a>
          ))}
        </ScrollWrap>
      </div>
    </section>
  );
}
