CREATE TABLE IF NOT EXISTS workflow_specs (
  workflow_id text NOT NULL,
  version text NOT NULL,
  spec jsonb NOT NULL,
  spec_digest text NOT NULL,
  enabled boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (workflow_id, version)
);

CREATE TABLE IF NOT EXISTS schedules (
  schedule_id text PRIMARY KEY,
  workflow_id text NOT NULL,
  workflow_version text NOT NULL,
  schedule_expr text NOT NULL,
  timezone text NOT NULL DEFAULT 'UTC',
  jitter_seconds integer NOT NULL DEFAULT 0,
  max_overlap integer NOT NULL DEFAULT 1,
  catchup_policy text NOT NULL,
  budget_json jsonb NOT NULL DEFAULT '{}',
  enabled boolean NOT NULL DEFAULT true,
  next_due_at timestamptz,
  last_trigger_at timestamptz
);

CREATE TABLE IF NOT EXISTS workflow_runs (
  run_id text PRIMARY KEY,
  workflow_id text NOT NULL,
  workflow_version text NOT NULL,
  trigger_id text NOT NULL,
  state text NOT NULL,
  budget_json jsonb NOT NULL DEFAULT '{}',
  input_digest text,
  created_at timestamptz NOT NULL DEFAULT now(),
  started_at timestamptz,
  finished_at timestamptz,
  UNIQUE (workflow_id, workflow_version, trigger_id)
);

CREATE TABLE IF NOT EXISTS jobs (
  job_id text PRIMARY KEY,
  run_id text NOT NULL REFERENCES workflow_runs(run_id),
  node_id text NOT NULL,
  dedupe_key text NOT NULL UNIQUE,
  queue_class text NOT NULL,
  priority numeric NOT NULL DEFAULT 0,
  executor text NOT NULL,
  state text NOT NULL,
  input_json jsonb NOT NULL,
  input_digest text NOT NULL,
  output_schema_id text,
  available_at timestamptz NOT NULL DEFAULT now(),
  attempt_count integer NOT NULL DEFAULT 0,
  max_attempts integer NOT NULL DEFAULT 3,
  leased_by text,
  lease_expires_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS jobs_ready_idx
ON jobs(state, available_at, priority DESC, created_at, job_id);

CREATE TABLE IF NOT EXISTS job_dependencies (
  job_id text NOT NULL REFERENCES jobs(job_id),
  depends_on_job_id text NOT NULL REFERENCES jobs(job_id),
  requirement text NOT NULL DEFAULT 'SUCCEEDED',
  PRIMARY KEY (job_id, depends_on_job_id)
);

CREATE TABLE IF NOT EXISTS attempts (
  attempt_id text PRIMARY KEY,
  job_id text NOT NULL REFERENCES jobs(job_id),
  attempt_no integer NOT NULL,
  worker_id text NOT NULL,
  state text NOT NULL,
  started_at timestamptz NOT NULL DEFAULT now(),
  heartbeat_at timestamptz,
  finished_at timestamptz,
  error_class text,
  error_json jsonb,
  output_artifact_id text,
  UNIQUE(job_id, attempt_no)
);

CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id text PRIMARY KEY,
  media_type text NOT NULL,
  byte_size bigint NOT NULL,
  raw_sha256 text NOT NULL,
  canonical_sha256 text,
  storage_uri text NOT NULL,
  schema_id text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(raw_sha256, media_type)
);

CREATE TABLE IF NOT EXISTS events (
  seq bigserial PRIMARY KEY,
  event_id text NOT NULL UNIQUE,
  aggregate_type text NOT NULL,
  aggregate_id text NOT NULL,
  event_type text NOT NULL,
  occurred_at timestamptz NOT NULL DEFAULT now(),
  actor text NOT NULL,
  causation_id text,
  correlation_id text,
  payload jsonb NOT NULL,
  artifact_digest text,
  schema_version text NOT NULL
);

CREATE INDEX IF NOT EXISTS events_aggregate_idx
ON events(aggregate_type, aggregate_id, seq);

CREATE TABLE IF NOT EXISTS ledger_checkpoints (
  checkpoint_id text PRIMARY KEY,
  tree_size bigint NOT NULL,
  first_seq bigint NOT NULL,
  last_seq bigint NOT NULL,
  merkle_root text NOT NULL,
  previous_checkpoint_id text,
  checkpoint_json jsonb NOT NULL,
  signature text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS budget_accounts (
  budget_id text PRIMARY KEY,
  scope_type text NOT NULL,
  scope_id text NOT NULL,
  period_start timestamptz NOT NULL,
  period_end timestamptz NOT NULL,
  limit_usd numeric NOT NULL,
  reserved_usd numeric NOT NULL DEFAULT 0,
  spent_usd numeric NOT NULL DEFAULT 0,
  UNIQUE(scope_type, scope_id, period_start, period_end)
);

CREATE TABLE IF NOT EXISTS budget_reservations (
  reservation_id text PRIMARY KEY,
  budget_id text NOT NULL REFERENCES budget_accounts(budget_id),
  job_id text REFERENCES jobs(job_id),
  amount_usd numeric NOT NULL,
  state text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL
);

CREATE TABLE IF NOT EXISTS commit_intents (
  intent_id text PRIMARY KEY,
  job_id text NOT NULL REFERENCES jobs(job_id),
  effect_type text NOT NULL,
  target_ref text NOT NULL,
  expected_state_digest text,
  dependency_digest text NOT NULL,
  state text NOT NULL,
  external_effect_id text,
  created_at timestamptz NOT NULL DEFAULT now(),
  committed_at timestamptz
);
