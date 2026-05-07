ALTER TABLE public.articles
ADD COLUMN article_type text NOT NULL DEFAULT 'news'
CHECK (article_type IN ('news', 'feature'));

CREATE INDEX IF NOT EXISTS idx_articles_article_type ON public.articles(article_type);