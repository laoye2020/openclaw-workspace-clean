CREATE TABLE IF NOT EXISTS pairs_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_id TEXT NOT NULL,
    pair_address TEXT NOT NULL,
    token_address TEXT NOT NULL,
    dex_id TEXT,
    liquidity_usd REAL NOT NULL DEFAULT 0,
    price_usd REAL NOT NULL DEFAULT 0,
    volume_h24 REAL NOT NULL DEFAULT 0,
    txns_h1_buys INTEGER NOT NULL DEFAULT 0,
    txns_h1_sells INTEGER NOT NULL DEFAULT 0,
    pair_created_at TEXT,
    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pairs_raw_token_address ON pairs_raw(token_address);
CREATE INDEX IF NOT EXISTS idx_pairs_raw_pair_address ON pairs_raw(pair_address);
CREATE INDEX IF NOT EXISTS idx_pairs_raw_fetched_at ON pairs_raw(fetched_at);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_raw_id INTEGER,
    chain_id TEXT NOT NULL,
    pair_address TEXT NOT NULL,
    token_address TEXT NOT NULL,
    liquidity_score REAL NOT NULL,
    txn_activity_score REAL NOT NULL,
    momentum_score REAL NOT NULL,
    final_score REAL NOT NULL,
    passed_filters INTEGER NOT NULL,
    filter_reasons TEXT NOT NULL,
    skipped_checks TEXT NOT NULL,
    risk_flags TEXT NOT NULL,
    holders INTEGER,
    top10_concentration REAL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(pair_raw_id) REFERENCES pairs_raw(id)
);

CREATE INDEX IF NOT EXISTS idx_signals_pair_address ON signals(pair_address);
CREATE INDEX IF NOT EXISTS idx_signals_token_address ON signals(token_address);
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON signals(created_at);
CREATE INDEX IF NOT EXISTS idx_signals_final_score ON signals(final_score);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id INTEGER,
    chain_id TEXT NOT NULL,
    pair_address TEXT NOT NULL,
    token_address TEXT NOT NULL,
    final_score REAL NOT NULL,
    message TEXT NOT NULL,
    dry_run INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at TEXT,
    FOREIGN KEY(signal_id) REFERENCES signals(id)
);

CREATE INDEX IF NOT EXISTS idx_alerts_pair_address ON alerts(pair_address);
CREATE INDEX IF NOT EXISTS idx_alerts_token_address ON alerts(token_address);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);

CREATE TABLE IF NOT EXISTS trade_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL,
    outcome TEXT,
    pnl_pct REAL,
    holding_minutes INTEGER,
    notes TEXT,
    reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(alert_id) REFERENCES alerts(id)
);

CREATE INDEX IF NOT EXISTS idx_trade_feedback_alert_id ON trade_feedback(alert_id);
