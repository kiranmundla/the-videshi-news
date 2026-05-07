-- Drop existing articles table (and any dependent objects)
drop table if exists public.articles cascade;

-- 1. RAW ARTICLES
create table public.raw_articles (
  id            uuid primary key default gen_random_uuid(),
  url           text not null unique,
  title         text not null,
  description   text,
  image_url     text,
  source_name   text not null,
  source_url    text,
  published_at  timestamptz,
  fetched_at    timestamptz default now(),
  processed     boolean default false,
  created_at    timestamptz default now()
);
create index raw_articles_processed_idx on public.raw_articles(processed, fetched_at desc);
create index raw_articles_fetched_at_idx on public.raw_articles(fetched_at desc);

-- 2. STORY GROUPS
create table public.story_groups (
  id              uuid primary key default gen_random_uuid(),
  priority        int not null,
  story_headline  text not null,
  category        text not null,
  source_count    int not null,
  sources         text[] not null,
  raw_article_ids uuid[] not null,
  best_article_id uuid references public.raw_articles(id),
  diaspora_relevant boolean default false,
  enriched        boolean default false,
  run_id          uuid not null,
  created_at      timestamptz default now()
);
create index story_groups_enriched_idx on public.story_groups(enriched, priority);
create index story_groups_category_idx on public.story_groups(category);
create index story_groups_created_at_idx on public.story_groups(created_at desc);

-- 3. ARTICLES
create table public.articles (
  id              uuid primary key default gen_random_uuid(),
  story_group_id  uuid references public.story_groups(id),
  title           text not null,
  slug            text unique,
  category        text not null,
  summary         text not null,
  body            text not null,
  nri_angle       text,
  sources_used    jsonb,
  image_url       text,
  published_at    timestamptz default now(),
  is_published    boolean default true,
  word_count      int,
  read_time_min   int,
  tags            text[],
  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);
create index articles_category_idx on public.articles(category, published_at desc);
create index articles_published_idx on public.articles(is_published, published_at desc);
create index articles_slug_idx on public.articles(slug);

-- 4. PIPELINE RUNS
create table public.pipeline_runs (
  id              uuid primary key default gen_random_uuid(),
  run_type        text not null,
  status          text not null,
  raw_fetched     int default 0,
  raw_new         int default 0,
  groups_created  int default 0,
  articles_created int default 0,
  error_message   text,
  started_at      timestamptz default now(),
  finished_at     timestamptz
);

-- 5. RLS
alter table public.raw_articles    enable row level security;
alter table public.story_groups    enable row level security;
alter table public.articles        enable row level security;
alter table public.pipeline_runs   enable row level security;

create policy "Public read articles"
  on public.articles for select
  using (is_published = true);

create policy "Service role full access articles"
  on public.articles for all
  using (auth.role() = 'service_role');

create policy "Service role full access raw"
  on public.raw_articles for all
  using (auth.role() = 'service_role');

create policy "Service role full access groups"
  on public.story_groups for all
  using (auth.role() = 'service_role');

create policy "Service role full access runs"
  on public.pipeline_runs for all
  using (auth.role() = 'service_role');