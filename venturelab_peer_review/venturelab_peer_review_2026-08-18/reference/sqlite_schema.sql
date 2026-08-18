PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY,
    factory_hint TEXT,
    title TEXT NOT NULL,
    body_json TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    opportunity_id TEXT,
    claim_key TEXT,
    source_uri TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_family TEXT,
    retrieved_at TEXT NOT NULL,
    published_at TEXT,
    content_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    FOREIGN KEY(opportunity_id) REFERENCES opportunities(id)
);
CREATE INDEX IF NOT EXISTS idx_evidence_opp ON evidence(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_evidence_claim ON evidence(claim_key);

CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    factory_type TEXT NOT NULL,
    task_kind TEXT NOT NULL,
    state TEXT NOT NULL,
    input_json TEXT NOT NULL,
    result_json TEXT,
    idempotency_key TEXT UNIQUE,
    budget_usd REAL,
    quality_floor REAL NOT NULL DEFAULT 0.70,
    priority INTEGER NOT NULL DEFAULT 0,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    lease_owner TEXT,
    lease_until TEXT,
    external_runtime TEXT,
    external_task_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_jobs_state_priority
ON jobs(state, priority DESC, created_at);

CREATE TABLE IF NOT EXISTS job_dependencies (
    job_id TEXT NOT NULL,
    depends_on_job_id TEXT NOT NULL,
    PRIMARY KEY(job_id, depends_on_job_id),
    FOREIGN KEY(job_id) REFERENCES jobs(id),
    FOREIGN KEY(depends_on_job_id) REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS attempts (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    route_id TEXT,
    provider_id TEXT,
    model_id TEXT,
    skill_hash TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    exit_code INTEGER,
    failure_class TEXT,
    stdout_artifact_id TEXT,
    stderr_artifact_id TEXT,
    verifier_accepted INTEGER,
    cost_usd REAL,
    metrics_json TEXT,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);
CREATE INDEX IF NOT EXISTS idx_attempts_job ON attempts(job_id);

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    sha256 TEXT NOT NULL UNIQUE,
    media_type TEXT,
    size_bytes INTEGER NOT NULL,
    storage_uri TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS certificates (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    accepted INTEGER NOT NULL,
    checks_json TEXT NOT NULL,
    issued_at TEXT NOT NULL,
    FOREIGN KEY(job_id) REFERENCES jobs(id),
    FOREIGN KEY(artifact_id) REFERENCES artifacts(id)
);

CREATE TABLE IF NOT EXISTS events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_entity
ON events(entity_type, entity_id, seq);
