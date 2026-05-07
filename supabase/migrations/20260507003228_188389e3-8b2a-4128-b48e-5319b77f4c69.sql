ALTER TABLE public.articles ADD COLUMN source_url text;
CREATE UNIQUE INDEX articles_source_url_key ON public.articles (source_url) WHERE source_url IS NOT NULL;