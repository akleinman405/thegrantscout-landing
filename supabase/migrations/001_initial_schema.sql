-- TheGrantScout CRM Schema
-- Run against Supabase project

-- ============================================================
-- CORE ENTITIES
-- ============================================================

CREATE TABLE organizations (
  id          BIGSERIAL PRIMARY KEY,
  ein         VARCHAR(10) UNIQUE,
  name        TEXT NOT NULL,
  type        VARCHAR(20) NOT NULL CHECK (type IN ('client', 'lead', 'nonprofit', 'funder')),
  stage       VARCHAR(30) DEFAULT 'new',
  city        TEXT,
  state       VARCHAR(2),
  website     TEXT,
  phone       TEXT,
  ntee_code   VARCHAR(10),
  assets      BIGINT,
  annual_giving BIGINT,
  mission_text TEXT,
  source      VARCHAR(50) DEFAULT 'manual',
  created_at  TIMESTAMPTZ DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE people (
  id              BIGSERIAL PRIMARY KEY,
  org_id          BIGINT REFERENCES organizations(id) ON DELETE SET NULL,
  first_name      TEXT,
  last_name       TEXT,
  email           TEXT,
  phone           TEXT,
  title           TEXT,
  linkedin_url    TEXT UNIQUE,
  background      TEXT,
  source          VARCHAR(30) DEFAULT 'manual' CHECK (source IN ('manual', 'dripify', 'call_log', 'email_campaign')),
  dripify_import_id BIGINT,
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- ACTIVITY TRACKING
-- ============================================================

CREATE TABLE timeline_events (
  id          BIGSERIAL PRIMARY KEY,
  org_id      BIGINT REFERENCES organizations(id) ON DELETE CASCADE,
  person_id   BIGINT REFERENCES people(id) ON DELETE SET NULL,
  event_type  VARCHAR(30) NOT NULL CHECK (event_type IN ('call', 'email', 'linkedin', 'meeting', 'note', 'status_change', 'import')),
  summary     TEXT,
  details     JSONB DEFAULT '{}',
  occurred_at TIMESTAMPTZ DEFAULT now(),
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tasks (
  id           BIGSERIAL PRIMARY KEY,
  org_id       BIGINT REFERENCES organizations(id) ON DELETE SET NULL,
  person_id    BIGINT REFERENCES people(id) ON DELETE SET NULL,
  title        TEXT NOT NULL,
  due_date     DATE,
  urgency      VARCHAR(20) CHECK (urgency IN ('overdue', 'today', 'this_week', 'upcoming', 'no_date')),
  completed    BOOLEAN DEFAULT false,
  completed_at TIMESTAMPTZ,
  created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE follow_ups (
  id              BIGSERIAL PRIMARY KEY,
  org_id          BIGINT REFERENCES organizations(id) ON DELETE CASCADE,
  person_id       BIGINT REFERENCES people(id) ON DELETE SET NULL,
  action          TEXT NOT NULL,
  contact_email   TEXT,
  due_date        DATE,
  urgency         VARCHAR(20) CHECK (urgency IN ('overdue', 'today', 'this_week', 'upcoming', 'no_date')),
  completed       BOOLEAN DEFAULT false,
  completed_at    TIMESTAMPTZ,
  source_event_id BIGINT REFERENCES timeline_events(id) ON DELETE SET NULL,
  created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE meetings (
  id                  BIGSERIAL PRIMARY KEY,
  org_id              BIGINT REFERENCES organizations(id) ON DELETE SET NULL,
  person_id           BIGINT REFERENCES people(id) ON DELETE SET NULL,
  title               TEXT NOT NULL,
  meeting_date        TIMESTAMPTZ,
  duration_minutes    INT,
  fathom_recording_url TEXT,
  video_url           TEXT,
  summary             TEXT,
  action_items        JSONB DEFAULT '[]',
  created_at          TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- REPORTS
-- ============================================================

CREATE TABLE reports (
  id         BIGSERIAL PRIMARY KEY,
  org_id     BIGINT REFERENCES organizations(id) ON DELETE CASCADE,
  period     VARCHAR(20),
  due_date   DATE,
  status     VARCHAR(20) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'delivered', 'overdue')),
  file_url   TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- IMPORT TRACKING
-- ============================================================

CREATE TABLE dripify_imports (
  id             BIGSERIAL PRIMARY KEY,
  filename       TEXT NOT NULL,
  imported_at    TIMESTAMPTZ DEFAULT now(),
  stats_data     JSONB DEFAULT '{}',
  leads_matched  INT DEFAULT 0,
  leads_created  INT DEFAULT 0
);

-- ============================================================
-- NOTES
-- ============================================================

CREATE TABLE notes (
  id         BIGSERIAL PRIMARY KEY,
  org_id     BIGINT REFERENCES organizations(id) ON DELETE CASCADE,
  person_id  BIGINT REFERENCES people(id) ON DELETE SET NULL,
  content    TEXT,
  pinned     BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_organizations_type ON organizations(type);
CREATE INDEX idx_organizations_ein ON organizations(ein);
CREATE INDEX idx_people_org_id ON people(org_id);
CREATE INDEX idx_people_email ON people(email);
CREATE INDEX idx_timeline_events_org_id ON timeline_events(org_id);
CREATE INDEX idx_timeline_events_person_id ON timeline_events(person_id);
CREATE INDEX idx_timeline_events_occurred_at ON timeline_events(occurred_at DESC);
CREATE INDEX idx_tasks_completed ON tasks(completed) WHERE NOT completed;
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_follow_ups_completed ON follow_ups(completed) WHERE NOT completed;
CREATE INDEX idx_meetings_date ON meetings(meeting_date DESC);
CREATE INDEX idx_reports_org_id ON reports(org_id);
CREATE INDEX idx_notes_org_id ON notes(org_id);

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE people ENABLE ROW LEVEL SECURITY;
ALTER TABLE timeline_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE follow_ups ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE dripify_imports ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- Single-tenant CRM: allow full access via anon key (auth handled by app cookie layer)
-- service_role key bypasses RLS automatically, so no policy needed for server-side
CREATE POLICY "Allow all access" ON organizations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON people FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON timeline_events FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON tasks FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON follow_ups FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON meetings FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON reports FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON dripify_imports FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access" ON notes FOR ALL USING (true) WITH CHECK (true);

-- ============================================================
-- AUTO-UPDATE updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_people_updated_at BEFORE UPDATE ON people FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_notes_updated_at BEFORE UPDATE ON notes FOR EACH ROW EXECUTE FUNCTION update_updated_at();
