-- Migration: community submissions queue
-- Run in Supabase Dashboard > SQL Editor (one-time).
-- Creates the moderation queue for user-submitted events and businesses.
-- NOTHING goes live without approval: the app inserts with status='pending',
-- and only the moderation script (service_role) can approve into live tables.

create table if not exists community_submissions (
  id uuid primary key default gen_random_uuid(),

  -- what is being submitted
  type text not null check (type in ('event', 'business')),
  status text not null default 'pending'
    check (status in ('pending', 'approved', 'rejected', 'spam')),

  -- common fields
  name text not null,
  description text,
  category text,

  -- location (both types)
  venue text,              -- events: venue name
  address text,
  city text,
  state text,              -- 2-letter US state
  zip text,

  -- event-specific
  event_date date,
  event_time text,         -- freeform, e.g. "7:00 PM"
  ticket_url text,

  -- business-specific
  phone text,
  website text,
  hours text,

  -- submitter (for follow-up, never displayed publicly)
  submitter_name text,
  submitter_email text,

  -- optional cover image (uploaded to storage by the form)
  image_url text,

  -- moderation bookkeeping
  source text not null default 'web-form',
  submitted_at timestamptz not null default now(),
  reviewed_at timestamptz,
  reviewed_by text,
  review_notes text,
  live_id uuid,            -- id of the row created in events/directory_listings on approval
  live_table text          -- 'events' or 'directory_listings'
);

create index if not exists idx_submissions_status
  on community_submissions (status, submitted_at desc);
create index if not exists idx_submissions_type_status
  on community_submissions (type, status);

-- Row Level Security:
--  * anon (public web form) may INSERT rows, but only as status='pending'.
--  * anon may NOT select, update, or delete (no policies = denied).
--  * service_role bypasses RLS -> moderation script approves/rejects.
alter table community_submissions enable row level security;

drop policy if exists "anon insert pending only" on community_submissions;
create policy "anon insert pending only"
  on community_submissions
  for insert to anon
  with check (status = 'pending');
