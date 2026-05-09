INSERT INTO public.p2_feed_sources (name, url, type, layer, tier, is_active, verticals)
VALUES
  ('Indian Eagle News', 'https://www.indianeagle.com/travelbeats/feed/', 'rss', 'discovery', 'B', true, ARRAY['immigration','diaspora']),
  ('Desi Bulletin', 'https://www.desibulletin.com/feed/', 'rss', 'discovery', 'B', true, ARRAY['diaspora','immigration']),
  ('American Bazaar', 'https://www.americanbazaaronline.com/feed/', 'rss', 'discovery', 'A', true, ARRAY['diaspora','immigration','politics'])
ON CONFLICT DO NOTHING;