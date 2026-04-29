-- Migration: Widen subscribers VARCHAR columns whose Zod limits exceeded their DB widths.
-- The Apr 22 "relax checkout validation" commit raised Zod limits on geographic_scope,
-- annual_budget, and grant_capacity to 100/100/200 respectively, but left the underlying
-- DB columns at 50/50/100. Today the form values are short dropdown picks so this never
-- triggers, but the moment any of them becomes free text we'd hit a silent insert
-- rejection (same bug class as the Apr 20 known_funders rename). Match DB to Zod.
-- Date: 2026-04-28

ALTER TABLE subscribers ALTER COLUMN geographic_scope TYPE VARCHAR(200);
ALTER TABLE subscribers ALTER COLUMN annual_budget TYPE VARCHAR(200);
ALTER TABLE subscribers ALTER COLUMN grant_capacity TYPE VARCHAR(300);
