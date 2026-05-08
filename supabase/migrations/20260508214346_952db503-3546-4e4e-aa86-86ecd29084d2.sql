
UPDATE public.p2_feed_sources SET url = 'https://www.thehindu.com/feeder/default.rss'
  WHERE name = 'The Hindu';

UPDATE public.p2_feed_sources SET url = 'https://www.indiatoday.in/rss/home'
  WHERE name = 'India Today';

UPDATE public.p2_feed_sources SET url = 'https://www.business-standard.com/rss/home_page_top_stories.rss'
  WHERE name = 'Business Standard';

UPDATE public.p2_feed_sources
  SET url = 'http://feeds.bbci.co.uk/news/world/asia/india/rss.xml',
      name = 'BBC India'
  WHERE name = 'India.gov.in';
