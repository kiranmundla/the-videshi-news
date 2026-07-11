import { useEffect, useState } from 'react';
import ScrollWrap from './ScrollWrap';

interface InstagramEmbed {
  shortcode: string;
  account: string;
  category: string;
  likes: number;
  caption_preview: string;
}

interface InstagramPhotoScrollProps {
  category: string;
  title?: string;
  label?: string;
}

export default function InstagramPhotoScroll({ category, title, label }: InstagramPhotoScrollProps) {
  const [embeds, setEmbeds] = useState<InstagramEmbed[]>([]);

  useEffect(() => {
    fetch('/data/instagram-embeds.json')
      .then(r => r.json())
      .then((data: InstagramEmbed[]) => {
        const filtered = data.filter(e => e.category === category);
        setEmbeds(filtered);
      })
      .catch(() => {});
  }, [category]);

  if (embeds.length === 0) return null;

  return (
    <section className="ig-photo-section">
      <div className="container">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="ig-photo-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
              <circle cx="12" cy="12" r="5"/>
              <circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/>
            </svg>
          </div>
          <span
            className="text-[11px] font-bold tracking-[1.5px] uppercase"
            style={{ color: '#64748B' }}
          >
            {label || 'Photos'}
          </span>
        </div>
        {title && <h3 className="ig-photo-title">{title}</h3>}
        <ScrollWrap className="ig-photo-scroll">
          {embeds.map((embed) => (
            <div key={embed.shortcode} className="ig-embed-card">
              <iframe
                src={`https://www.instagram.com/p/${embed.shortcode}/embed/`}
                width="300"
                height="600"
                frameBorder="0"
                scrolling="no"
                loading="lazy"
                title={`Instagram post by @${embed.account}`}
              />
            </div>
          ))}
        </ScrollWrap>
      </div>
    </section>
  );
}
