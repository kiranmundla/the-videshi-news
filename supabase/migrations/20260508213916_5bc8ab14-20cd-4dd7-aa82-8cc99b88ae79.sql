
INSERT INTO public.p2_feed_sources (name, url, type, layer, verticals, tier, notes) VALUES
('NDTV Top Stories','https://feeds.feedburner.com/ndtvnews-top-stories','rss','discovery',ARRAY['politics','economy','tech'],'A',NULL),
('The Hindu','https://thehindu.com/feeder/default.rss','rss','discovery',ARRAY['politics','economy','science'],'A',NULL),
('Indian Express','https://indianexpress.com/feed','rss','discovery',ARRAY['politics','economy','tech'],'A',NULL),
('Times of India','https://timesofindia.indiatimes.com/rssfeedstopstories.cms','rss','discovery',ARRAY['politics','culture','economy'],'A',NULL),
('Hindustan Times','https://hindustantimes.com/feeds/rss/india-news/rssfeed.xml','rss','discovery',ARRAY['politics','economy','culture'],'A',NULL),
('India Today','https://indiatoday.in/rss/1206578','rss','discovery',ARRAY['politics','culture','tech'],'A',NULL),
('Economic Times','https://economictimes.indiatimes.com/rssfeedsdefault.cms','rss','discovery',ARRAY['economy','tech','politics'],'A',NULL),
('Business Standard','https://business-standard.com/rss/latest.rss','rss','discovery',ARRAY['economy','tech'],'A',NULL),
('LiveMint','https://livemint.com/rss/rss.xml','rss','discovery',ARRAY['economy'],'A',NULL),
('The Print','https://theprint.in/feed','rss','discovery',ARRAY['politics','economy'],'A',NULL),
('The Wire','https://thewire.in/feed','rss','discovery',ARRAY['politics','diaspora'],'A',NULL),
('TOI NRI Section','https://timesofindia.indiatimes.com/nri/rssfeedstopstories.cms','rss','discovery',ARRAY['diaspora','immigration'],'A',NULL),
('New India Abroad','https://newindiaabroad.com/feed','rss','discovery',ARRAY['diaspora'],'A',NULL),
('NRI Pulse','https://nripulse.com/feed','rss','discovery',ARRAY['diaspora'],'B','already in ingest-rss'),
('ET Tech','https://economictimes.indiatimes.com/tech/rss.cms','rss','discovery',ARRAY['tech'],'B',NULL),
('PIB Press Releases','https://api.rss2json.com/v1/api.json?rss_url=https%3A%2F%2Fpib.gov.in%2FRssMain.aspx%3FModId%3D6%26Lang%3D1%26Regid%3D1','rss','primary',ARRAY['politics','economy','science','tech','diaspora'],'A','via rss2json proxy — same as existing ingest-rss setup'),
('RBI Press Releases','https://rbi.org.in/pressreleases_rss.xml','rss','primary',ARRAY['economy'],'A','already in ingest-rss'),
('SEBI RSS','https://sebi.gov.in/sebirss.xml','rss','primary',ARRAY['economy'],'A','filter: skip Recovery/Prohibitory orders, keep circulars'),
('USCIS News','https://www.uscis.gov/newsroom/news-releases','scrape','primary',ARRAY['immigration','diaspora'],'A','already in ingest-rss — highest diaspora value'),
('India.gov.in','https://services.india.gov.in/feed/index?ln=en','rss','primary',ARRAY['politics','economy'],'B',NULL)
ON CONFLICT (url) DO NOTHING;
