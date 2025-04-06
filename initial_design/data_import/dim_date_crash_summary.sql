-- 1. Dimension: Date (Daily)
CREATE TABLE dim_date (
    date_sk BIGSERIAL PRIMARY KEY,           -- Surrogate Key
    full_date DATE NOT NULL UNIQUE,          -- Natural Key (e.g., '1989-01-01')
    year SMALLINT NOT NULL,
    month SMALLINT NOT NULL,                 -- 1-12
    day SMALLINT NOT NULL,                   -- 1-31
    month_name VARCHAR(10) NOT NULL,
    day_name VARCHAR(10) NOT NULL,           -- e.g., 'Sunday'
    day_of_week_iso SMALLINT NOT NULL,       -- 1=Monday, 7=Sunday
    is_weekday BOOLEAN NOT NULL,             -- True for Mon-Fri
    quarter SMALLINT NOT NULL,               -- 1-4
    year_month_display VARCHAR(8) NOT NULL,  -- 'YYYY-MM'
    year_quarter_display VARCHAR(8) NOT NULL -- 'YYYY-Qn'
    -- Holiday flags are NOT here; they describe the event context in the source.
);
CREATE INDEX idx_dim_date_full_date ON dim_date (full_date);

CREATE TABLE dim_daily_crash_summary (
    date_sk BIGINT PRIMARY KEY REFERENCES dim_date(date_sk), -- Date is the primary key here
	full_date VARCHAR(25) NOT NULL,
    number_of_fatal_crashes INT NOT NULL
);


