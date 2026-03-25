-- Migration: Create subscribers table for self-service signup
-- Mirrors core.subscribers from local Postgres, adapted for Supabase (public schema)
-- Date: 2026-03-14

CREATE TABLE subscribers (
    id              BIGSERIAL PRIMARY KEY,

    -- Stripe
    stripe_customer_id    TEXT UNIQUE,
    stripe_subscription_id TEXT UNIQUE,
    subscription_status   VARCHAR(50) DEFAULT 'pending_payment'
        CHECK (subscription_status IN ('pending_payment', 'active', 'past_due', 'canceled', 'incomplete')),
    plan_type       VARCHAR(20) NOT NULL DEFAULT 'monthly'
        CHECK (plan_type IN ('monthly', 'annual')),

    -- Organization
    org_name        TEXT NOT NULL,
    ein             VARCHAR(10) NOT NULL,
    org_type        VARCHAR(100),

    -- Contact
    contact_name    TEXT NOT NULL,
    contact_email   TEXT NOT NULL,

    -- Mission & Focus
    mission         TEXT,
    focus_areas     TEXT[],
    programs        TEXT,
    populations     TEXT[],

    -- Geography & Capacity
    state           VARCHAR(2),
    city            TEXT,
    geographic_scope VARCHAR(50),
    annual_budget   VARCHAR(50),
    grant_size_seeking VARCHAR(50),
    grant_types     TEXT[],
    grant_capacity  VARCHAR(100),

    -- Preferences
    ntee_code       VARCHAR(10),
    known_funders   TEXT,
    timeframe       VARCHAR(50),
    additional_notes TEXT,

    -- Metadata
    signup_source   VARCHAR(50) DEFAULT 'website',
    dim_client_id   INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    canceled_at     TIMESTAMPTZ
);

CREATE INDEX idx_subscribers_ein ON subscribers(ein);
CREATE INDEX idx_subscribers_status ON subscribers(subscription_status);
CREATE INDEX idx_subscribers_email ON subscribers(contact_email);

-- RLS
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all access" ON subscribers FOR ALL USING (true) WITH CHECK (true);

-- Auto-update updated_at (reuse existing function from 001)
CREATE TRIGGER trg_subscribers_updated_at
  BEFORE UPDATE ON subscribers
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
