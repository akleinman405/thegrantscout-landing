-- Create subscribers table for self-service signup
-- Run: psql -h localhost -U postgres -d thegrantscout -f scripts/001_create_subscribers.sql

CREATE TABLE IF NOT EXISTS core.subscribers (
    id              SERIAL PRIMARY KEY,
    -- Stripe
    stripe_customer_id    VARCHAR(255) UNIQUE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    subscription_status   VARCHAR(50) DEFAULT 'pending_payment'
        CHECK (subscription_status IN ('pending_payment', 'active', 'past_due', 'canceled', 'incomplete')),
    plan_type       VARCHAR(20) NOT NULL DEFAULT 'monthly'
        CHECK (plan_type IN ('monthly', 'annual')),

    -- Organization
    org_name        VARCHAR(500) NOT NULL,
    ein             VARCHAR(10) NOT NULL,
    org_type        VARCHAR(100),

    -- Contact
    contact_name    VARCHAR(255) NOT NULL,
    contact_email   VARCHAR(255) NOT NULL,

    -- Mission & Focus
    mission         TEXT,
    focus_areas     TEXT[],
    programs        TEXT,
    populations     TEXT[],

    -- Geography & Capacity
    state           VARCHAR(2),
    city            VARCHAR(255),
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

CREATE INDEX IF NOT EXISTS idx_subscribers_ein ON core.subscribers(ein);
CREATE INDEX IF NOT EXISTS idx_subscribers_status ON core.subscribers(subscription_status);
CREATE INDEX IF NOT EXISTS idx_subscribers_email ON core.subscribers(contact_email);
