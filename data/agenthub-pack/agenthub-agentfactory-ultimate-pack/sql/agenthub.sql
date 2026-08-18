PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS agent_systems (
  system_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  runtime TEXT NOT NULL,
  manifest_json TEXT NOT NULL,
  maturity TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS architecture_builds (
  build_id TEXT PRIMARY KEY,
  system_id TEXT,
  source_repo TEXT,
  source_sha TEXT NOT NULL,
  manifest_sha256 TEXT NOT NULL,
  runtime_adapter TEXT NOT NULL,
  runtime_adapter_version TEXT NOT NULL,
  model_policy_sha256 TEXT,
  dependency_lock_sha256 TEXT,
  image_digest TEXT,
  build_json TEXT NOT NULL,
  state TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(system_id) REFERENCES agent_systems(system_id)
);

CREATE TABLE IF NOT EXISTS architecture_patterns (
  pattern_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  pattern_json TEXT NOT NULL,
  state TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS build_patterns (
  build_id TEXT NOT NULL,
  pattern_id TEXT NOT NULL,
  evidence_json TEXT NOT NULL,
  PRIMARY KEY(build_id, pattern_id),
  FOREIGN KEY(build_id) REFERENCES architecture_builds(build_id),
  FOREIGN KEY(pattern_id) REFERENCES architecture_patterns(pattern_id)
);

CREATE TABLE IF NOT EXISTS benchmark_suites (
  suite_id TEXT PRIMARY KEY,
  version TEXT NOT NULL,
  manifest_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assessments (
  assessment_id TEXT PRIMARY KEY,
  build_id TEXT NOT NULL,
  suite_id TEXT NOT NULL,
  benchmark_mode TEXT NOT NULL,
  status TEXT NOT NULL,
  metrics_json TEXT NOT NULL,
  evidence_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(build_id) REFERENCES architecture_builds(build_id),
  FOREIGN KEY(suite_id) REFERENCES benchmark_suites(suite_id)
);

CREATE TABLE IF NOT EXISTS architecture_lineage (
  child_build_id TEXT NOT NULL,
  parent_build_id TEXT NOT NULL,
  mutations_json TEXT NOT NULL,
  evidence_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY(child_build_id, parent_build_id),
  FOREIGN KEY(child_build_id) REFERENCES architecture_builds(build_id),
  FOREIGN KEY(parent_build_id) REFERENCES architecture_builds(build_id)
);

CREATE TABLE IF NOT EXISTS architecture_runs (
  run_id TEXT PRIMARY KEY,
  build_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  runtime_json TEXT NOT NULL,
  outcome_json TEXT,
  state TEXT NOT NULL,
  created_at TEXT NOT NULL,
  finished_at TEXT,
  FOREIGN KEY(build_id) REFERENCES architecture_builds(build_id)
);

CREATE TABLE IF NOT EXISTS architecture_candidates (
  candidate_id TEXT PRIMARY KEY,
  need_id TEXT NOT NULL,
  build_json TEXT NOT NULL,
  parent_ids_json TEXT NOT NULL,
  mutations_json TEXT NOT NULL,
  search_generation INTEGER NOT NULL DEFAULT 0,
  state TEXT NOT NULL,
  created_at TEXT NOT NULL
);
