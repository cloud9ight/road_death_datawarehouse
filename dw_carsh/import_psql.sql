-- import data into dw tables using the psql command line 
-- \cd to my file path first

-- Dimension Tables 
\copy Dim_State FROM 'dim_state.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');

\copy Dim_Remoteness FROM 'dim_remoteness.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');

\copy Dim_Time FROM 'dim_time.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');

\copy dim_vehicle FROM 'dim_vehicle.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');

\copy Dim_Road_Type FROM 'dim_road_type.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');

\copy Dim_Crash_Type FROM 'dim_crash_type.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');

\copy Dim_Holiday FROM 'dim_holiday.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');

\copy dim_speed_limit FROM 'dim_speed_limit.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');


-- Fact Tables 

\copy fact_crash FROM 'fact_crash.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');

\copy fact_fatalities FROM 'fact_fatalities.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');

\copy fact_population_wide FROM 'fact_population_wide.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',');



