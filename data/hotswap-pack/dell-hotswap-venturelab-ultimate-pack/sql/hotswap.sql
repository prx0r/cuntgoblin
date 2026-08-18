PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS hotswap_accounts (
  account_id TEXT PRIMARY KEY,
  provider_id TEXT NOT NULL,
  credential_ref TEXT,
  state TEXT NOT NULL,
  configured_at TEXT,
  last_verified_at TEXT,
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS hotswap_route_accounts (
  route_id TEXT NOT NULL,
  account_id TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY(route_id, account_id),
  FOREIGN KEY(account_id) REFERENCES hotswap_accounts(account_id)
);

CREATE TABLE IF NOT EXISTS hotswap_quota_windows (
  quota_id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  route_id TEXT,
  metric TEXT NOT NULL,
  limit_value REAL,
  window_kind TEXT NOT NULL,
  window_seconds INTEGER,
  reset_at TEXT,
  source TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(account_id) REFERENCES hotswap_accounts(account_id)
);

CREATE TABLE IF NOT EXISTS hotswap_quota_usage (
  usage_id TEXT PRIMARY KEY,
  quota_id TEXT NOT NULL,
  value REAL NOT NULL,
  request_id TEXT,
  observed_at TEXT NOT NULL,
  source TEXT NOT NULL,
  FOREIGN KEY(quota_id) REFERENCES hotswap_quota_windows(quota_id)
);

CREATE TABLE IF NOT EXISTS hotswap_quota_reservations (
  reservation_id TEXT PRIMARY KEY,
  quota_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  value REAL NOT NULL,
  state TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  FOREIGN KEY(quota_id) REFERENCES hotswap_quota_windows(quota_id)
);

CREATE TABLE IF NOT EXISTS hotswap_breakers (
  breaker_key TEXT PRIMARY KEY,
  state TEXT NOT NULL,
  failure_count INTEGER NOT NULL DEFAULT 0,
  open_until TEXT,
  last_error_class TEXT,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hotswap_task_cell_posteriors (
  cell_id TEXT NOT NULL,
  route_id TEXT NOT NULL,
  alpha REAL NOT NULL,
  beta REAL NOT NULL,
  trials REAL NOT NULL DEFAULT 0,
  successes REAL NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(cell_id, route_id)
);

CREATE TABLE IF NOT EXISTS hotswap_plans (
  plan_id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  task_spec_json TEXT NOT NULL,
  plan_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hotswap_outcomes (
  outcome_id TEXT PRIMARY KEY,
  plan_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  route_id TEXT NOT NULL,
  success INTEGER,
  evaluator_id TEXT,
  actual_cost REAL,
  input_tokens INTEGER,
  output_tokens INTEGER,
  latency_ms REAL,
  error_class TEXT,
  outcome_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hotswap_account_opportunities (
  opportunity_id TEXT PRIMARY KEY,
  provider_id TEXT NOT NULL,
  offer_id TEXT,
  state TEXT NOT NULL,
  projected_value REAL,
  setup_friction INTEGER,
  expires_at TEXT,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
