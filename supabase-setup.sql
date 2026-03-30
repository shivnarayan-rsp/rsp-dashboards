-- ============================================================
-- MPS Dashboard — Supabase Setup
-- Run this in Supabase SQL Editor (once, before first use)
-- ============================================================

-- Table 1: MPS Actions tracker
CREATE TABLE IF NOT EXISTS mps_actions (
  id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  serial_no        TEXT,
  contract_no      TEXT,
  customer_name    TEXT,
  territory        TEXT,
  issue_type       TEXT CHECK (issue_type IN (
                     'margin_critical','high_visits','meter_anomaly',
                     'contract_renewal','account_review')),
  issue_detail     TEXT,
  suggested_action TEXT,
  assignee         TEXT CHECK (assignee IN ('Sridhar','Avi','Other')),
  due_date         DATE,
  status           TEXT DEFAULT 'Open' CHECK (status IN (
                     'Open','In Progress','Resolved')),
  notes            TEXT,
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Table 2: Major accounts QBR tracker
CREATE TABLE IF NOT EXISTS mps_accounts (
  id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_name    TEXT NOT NULL,
  bms_customer_id  INT,
  territory        TEXT,
  qbr_cadence      TEXT DEFAULT 'quarterly'
                     CHECK (qbr_cadence IN ('quarterly','biannual')),
  last_qbr_date    DATE,
  notes            TEXT,
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-update updated_at on mps_actions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER mps_actions_updated_at
  BEFORE UPDATE ON mps_actions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER mps_accounts_updated_at
  BEFORE UPDATE ON mps_accounts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE mps_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE mps_accounts ENABLE ROW LEVEL SECURITY;

-- Allow anon reads and writes (Vijendra to tighten per RSP pattern if needed)
CREATE POLICY "anon_all_mps_actions" ON mps_actions FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_mps_accounts" ON mps_accounts FOR ALL TO anon USING (true) WITH CHECK (true);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_mps_actions_status    ON mps_actions(status);
CREATE INDEX IF NOT EXISTS idx_mps_actions_serial    ON mps_actions(serial_no);
CREATE INDEX IF NOT EXISTS idx_mps_actions_assignee  ON mps_actions(assignee);
CREATE INDEX IF NOT EXISTS idx_mps_accounts_customer ON mps_accounts(customer_name);
