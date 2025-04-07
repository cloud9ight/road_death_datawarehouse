-- reload speed_id
-- 1. drop speed_id fk
ALTER TABLE fact_crash
    ALTER CONSTRAINT fact_crash_speed_id_fkey DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE fact_crash DROP CONSTRAINT fact_crash_speed_id_fkey;

-- 2 create temp table

CREATE TABLE temp_correct_speeds (
    Crash_ID INT NOT NULL,         -- matche fact_crash.Crash_ID
    Correct_Speed_ID INT NOT NULL  -- matche fact_crash.Speed_ID and dim_speed_limit.Speed_ID
);

-- import correct csv to temp table and verify
SELECT COUNT(*) FROM temp_correct_speeds; -- Should match expected number of records
SELECT * FROM temp_correct_speeds LIMIT 10; 
-- Check if all Correct_Speed_ID values exist in dim_speed_limit
SELECT DISTINCT tcs.Correct_Speed_ID
FROM temp_correct_speeds tcs
LEFT JOIN dim_speed_limit dsl ON tcs.Correct_Speed_ID = dsl.Speed_ID
WHERE dsl.Speed_ID IS NULL; -- return NO rows -- all IDs are valid

CREATE INDEX idx_temp_correct_speeds_crash_id ON temp_correct_speeds (Crash_ID);
ANALYZE temp_correct_speeds;

-- update and check
UPDATE fact_crash fc
SET Speed_ID = tcs.Correct_Speed_ID
FROM temp_correct_speeds tcs
WHERE fc.Crash_ID = tcs.Crash_ID;

SELECT DISTINCT Speed_ID FROM fact_crash ORDER BY Speed_ID;  --match

SELECT COUNT(*) FROM fact_crash WHERE Speed_ID = 1;   --match raw data 1318rows for na


-- add fk back
ALTER TABLE fact_crash
ADD CONSTRAINT fk_fact_crash_speed 
FOREIGN KEY (Speed_ID) REFERENCES dim_speed_limit(Speed_ID);