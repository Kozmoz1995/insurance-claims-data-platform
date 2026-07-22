CREATE SCHEMA IF NOT EXISTS insurance_dw;

CREATE TABLE IF NOT EXISTS insurance_dw.dim_date (
    date_key        INTEGER PRIMARY KEY,
    full_date       DATE NOT NULL UNIQUE,
    year_number     SMALLINT NOT NULL,
    quarter_number  SMALLINT NOT NULL,
    month_number    SMALLINT NOT NULL,
    month_name      VARCHAR(12) NOT NULL,
    day_number      SMALLINT NOT NULL
);

CREATE TABLE IF NOT EXISTS insurance_dw.dim_policy (
    policy_key      BIGSERIAL PRIMARY KEY,
    policy_id       VARCHAR(64) NOT NULL UNIQUE,
    effective_from  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS insurance_dw.dim_vehicle (
    vehicle_key     BIGSERIAL PRIMARY KEY,
    vehicle_id      VARCHAR(64) NOT NULL UNIQUE,
    effective_from  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS insurance_dw.dim_location (
    location_key    BIGSERIAL PRIMARY KEY,
    city            VARCHAR(100) NOT NULL UNIQUE,
    country_code    CHAR(2) NOT NULL DEFAULT 'TR'
);

CREATE TABLE IF NOT EXISTS insurance_dw.fact_claim (
    claim_key       BIGSERIAL PRIMARY KEY,
    claim_id        VARCHAR(64) NOT NULL UNIQUE,
    policy_key      BIGINT NOT NULL REFERENCES insurance_dw.dim_policy(policy_key),
    vehicle_key     BIGINT NOT NULL REFERENCES insurance_dw.dim_vehicle(vehicle_key),
    accident_date_key INTEGER NOT NULL REFERENCES insurance_dw.dim_date(date_key),
    event_date_key  INTEGER NOT NULL REFERENCES insurance_dw.dim_date(date_key),
    location_key    BIGINT NOT NULL REFERENCES insurance_dw.dim_location(location_key),
    event_timestamp TIMESTAMPTZ NOT NULL,
    claim_type      VARCHAR(30) NOT NULL,
    claim_status    VARCHAR(30) NOT NULL,
    claim_amount    NUMERIC(16,2) NOT NULL CHECK (claim_amount >= 0),
    paid_amount     NUMERIC(16,2) NOT NULL CHECK (paid_amount >= 0 AND paid_amount <= claim_amount),
    source_system   VARCHAR(30) NOT NULL,
    loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fact_claim_event_date
    ON insurance_dw.fact_claim(event_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_claim_policy
    ON insurance_dw.fact_claim(policy_key);
