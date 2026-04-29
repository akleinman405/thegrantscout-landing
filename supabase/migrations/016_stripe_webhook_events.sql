-- Migration: Stripe webhook event ledger for idempotency.
-- Stripe can deliver the same event multiple times on retry. Without dedup, every retry
-- re-sends welcome emails and re-runs side effects. This table keys on Stripe's event_id
-- so the webhook handler can early-return on a duplicate.
-- Date: 2026-04-28

CREATE TABLE IF NOT EXISTS public.stripe_webhook_events (
  event_id TEXT PRIMARY KEY,
  event_type TEXT NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_received_at
  ON public.stripe_webhook_events(received_at DESC);

ALTER TABLE public.stripe_webhook_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all access" ON public.stripe_webhook_events FOR ALL USING (true) WITH CHECK (true);
