UPDATE public.p2_articles SET image_url = NULL
WHERE headline IN (
  'Your Instagram Is Now Part of Your US Visa File',
  'India Fires Agni-5 in Full-Range Test, Rattling Asia',
  'India''s EPFO 3.0 Will Let You Swipe an ATM Card for PF',
  'India''s Forex Reserves Drop $7.79 Billion to $690.69 Billion'
);