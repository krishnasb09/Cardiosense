create extension if not exists pg_trgm;

create table if not exists public.predictions (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  patient_name text not null,
  patient_id text,
  doctor_id uuid,
  risk_percentage numeric not null,
  risk_level text not null check (risk_level in ('Low', 'Medium', 'High')),
  status text not null,
  input_data jsonb not null,
  explainability jsonb not null default '[]'::jsonb,
  recommendations jsonb not null default '[]'::jsonb,
  doctor_notes text
);

alter table public.predictions enable row level security;

create policy "doctors and admins can read predictions"
on public.predictions
for select
to authenticated
using (
  coalesce(auth.jwt() -> 'user_metadata' ->> 'role', 'doctor') in ('doctor', 'admin')
);

create policy "doctors and admins can create predictions"
on public.predictions
for insert
to authenticated
with check (
  coalesce(auth.jwt() -> 'user_metadata' ->> 'role', 'doctor') in ('doctor', 'admin')
);

create index if not exists predictions_patient_name_idx on public.predictions using gin (patient_name gin_trgm_ops);
create index if not exists predictions_created_at_idx on public.predictions (created_at desc);
create index if not exists predictions_risk_level_idx on public.predictions (risk_level);
