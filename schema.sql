-- Run this in Supabase SQL Editor

create table if not exists sessions (
  id text primary key,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists messages (
  id uuid default gen_random_uuid() primary key,
  session_id text references sessions(id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  created_at timestamptz default now()
);

create index if not exists messages_session_id_idx on messages(session_id, created_at);

create table if not exists wedding_profiles (
  session_id text primary key references sessions(id) on delete cascade,
  wedding_date date,
  city text,
  state text,
  guest_count int,
  total_budget numeric,
  ceremony_type text,
  priorities jsonb,
  dont_cares jsonb,
  profile_complete boolean default false,
  raw_summary text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
