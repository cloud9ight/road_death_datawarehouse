-- Stores attributes related to the day of the week
CREATE TABLE dim_day_of_week (
    day_of_week_sk SMALLINT PRIMARY KEY, -- 1-7 or 0-6
    day_name VARCHAR(10) NOT NULL UNIQUE, -- 'Monday', 'Friday', etc.
    is_weekday BOOLEAN NOT NULL -- True/False
);

INSERT INTO dim_day_of_week (day_of_week_sk, day_name, is_weekday) VALUES
(1, 'Monday', TRUE),
(2, 'Tuesday', TRUE),
(3, 'Wednesday', TRUE),
(4, 'Thursday', TRUE),
(5, 'Friday', TRUE),
(6, 'Saturday', FALSE),
(7, 'Sunday', FALSE);

SELECT*FROM dim_day_of_week;

-- Stores attributes related to specific year and month combinations
CREATE TABLE dim_year_month (
    year_month_sk BIGSERIAL PRIMARY KEY,          -- Surrogate Key (auto-incrementing)
    year SMALLINT NOT NULL,                     -- Year (e.g., 1989, 2004)
    month SMALLINT NOT NULL CHECK (month BETWEEN 1 AND 12), -- Month number (1-12)
    month_name VARCHAR(10) NOT NULL,           -- Full name of the month ('January', 'February', etc.)
    year_month_display VARCHAR(8) NOT NULL,      -- Display format 'YYYY-MM' (e.g., '1989-01')
    quarter SMALLINT NOT NULL CHECK (quarter BETWEEN 1 AND 4), -- Calendar quarter (1-4)
    year_quarter_display VARCHAR(8) NOT NULL,   -- Display format 'YYYY-Qn' (e.g., '1989-Q1')

    -- Natural Key: Ensures each year/month combination is unique in the table
    CONSTRAINT uq_year_month UNIQUE (year, month)
);

select*from dim_year_month;