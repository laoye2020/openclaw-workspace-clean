ALTER TABLE signals ADD COLUMN rule_score REAL;
ALTER TABLE signals ADD COLUMN llm_score REAL;
ALTER TABLE signals ADD COLUMN llm_confidence REAL;
ALTER TABLE signals ADD COLUMN llm_provider TEXT;
ALTER TABLE signals ADD COLUMN llm_model TEXT;
ALTER TABLE signals ADD COLUMN llm_risk_comment TEXT;
ALTER TABLE signals ADD COLUMN llm_action_hint TEXT;
ALTER TABLE signals ADD COLUMN llm_reasons TEXT NOT NULL DEFAULT '[]';
ALTER TABLE signals ADD COLUMN llm_failed INTEGER NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS recheck_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_alert_id INTEGER NOT NULL,
    source_signal_id INTEGER,
    chain_id TEXT NOT NULL,
    pair_address TEXT NOT NULL,
    token_address TEXT NOT NULL,
    token_symbol TEXT NOT NULL,
    scheduled_minutes INTEGER NOT NULL,
    due_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TEXT,
    FOREIGN KEY(source_alert_id) REFERENCES alerts(id),
    FOREIGN KEY(source_signal_id) REFERENCES signals(id),
    UNIQUE(source_alert_id, scheduled_minutes)
);

CREATE INDEX IF NOT EXISTS idx_recheck_jobs_due_status
    ON recheck_jobs(status, due_at);
CREATE INDEX IF NOT EXISTS idx_recheck_jobs_token
    ON recheck_jobs(token_address, pair_address);

CREATE TABLE IF NOT EXISTS recheck_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL UNIQUE,
    source_alert_id INTEGER NOT NULL,
    signal_id INTEGER,
    chain_id TEXT NOT NULL,
    pair_address TEXT NOT NULL,
    token_address TEXT NOT NULL,
    token_symbol TEXT NOT NULL,
    scheduled_minutes INTEGER NOT NULL,
    status TEXT NOT NULL,
    initial_score REAL NOT NULL,
    score_5m REAL,
    score_15m REAL,
    current_score REAL NOT NULL,
    delta_from_initial REAL NOT NULL,
    delta_from_previous REAL NOT NULL,
    rule_score REAL,
    llm_score REAL,
    llm_confidence REAL,
    summary_line TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(job_id) REFERENCES recheck_jobs(id),
    FOREIGN KEY(source_alert_id) REFERENCES alerts(id),
    FOREIGN KEY(signal_id) REFERENCES signals(id)
);

CREATE INDEX IF NOT EXISTS idx_recheck_results_token
    ON recheck_results(token_address, pair_address);
CREATE INDEX IF NOT EXISTS idx_recheck_results_alert
    ON recheck_results(source_alert_id, scheduled_minutes);
