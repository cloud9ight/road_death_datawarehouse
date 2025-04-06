CREATE TABLE fact_population_wide (
    -- Using the ID from your prepared data as the primary key
    State_Population_ID INT PRIMARY KEY, -- Assuming this is unique and suitable as PK

    -- Foreign Keys linking to dimension tables
    State_ID INT NOT NULL,
    Remoteness_ID INT NOT NULL,

    -- Population columns for each year
    -- Using underscore prefix as column names starting with numbers can be problematic
    _2001 INT NULL,
    _2002 INT NULL,
    _2003 INT NULL,
    _2004 INT NULL,
    _2005 INT NULL,
    _2006 INT NULL,
    _2007 INT NULL,
    _2008 INT NULL,
    _2009 INT NULL,
    _2010 INT NULL,
    _2011 INT NULL,
    _2012 INT NULL,
    _2013 INT NULL,
    _2014 INT NULL,
    _2015 INT NULL,
    _2016 INT NULL,
    _2017 INT NULL,
    _2018 INT NULL,
    _2019 INT NULL,
    _2020 INT NULL,
    _2021 INT NULL,
    _2022 INT NULL,
    _2023 INT NULL,


    -- CONSTRAINT to ensure the combination of State and Remoteness is unique
    -- This enforces that each row represents a unique geographic combination
    CONSTRAINT UQ_population_state_remoteness UNIQUE (State_ID, Remoteness_ID),

    -- FOREIGN KEY constraints linking to your dimension tables
    CONSTRAINT FK_popwide_dim_state FOREIGN KEY (State_ID)
        REFERENCES dim_state (State_ID), -- Assumes dim table is named dim_state

    CONSTRAINT FK_popwide_dim_remoteness FOREIGN KEY (Remoteness_ID)
        REFERENCES dim_remoteness (Remoteness_ID) -- Assumes dim table is named dim_remoteness
);

-- query to test
select *from fact_population_wide;

--Query 1: Get Population for a Specific State and Remoteness Area in a Specific Year
SELECT
    fpw._2022 -- Select the specific year column
FROM
    fact_population_wide fpw
WHERE
    fpw.State_ID = 1      -- Filter by State ID for NSW
    AND fpw.Remoteness_ID = 3; -- Filter by Remoteness ID for Major Cities

-- Query 2: Get Population Data for All Remoteness Areas within a Specific State for Recent Years
SELECT
    dr.Remoteness_Areas, -- Get the name from the dimension table
    fpw._2021,
    fpw._2022,
    fpw._2023
FROM
    fact_population_wide fpw
JOIN
    dim_remoteness dr ON fpw.Remoteness_ID = dr.Remoteness_ID -- Link to get names
WHERE
    fpw.State_ID = 3      -- Filter by State ID for Victoria
ORDER BY
    dr.Remoteness_Areas;  -- Order results for readability

-- Get Population Data for a Specific Remoteness Area across All States for a Specific Year
SELECT
    ds.State,           -- Get the state name from the dimension table
    fpw._2023           -- The population count for the specified year
FROM
    fact_population_wide fpw
JOIN
    dim_state ds ON fpw.State_ID = ds.State_ID -- Link to get state names
WHERE
    fpw.Remoteness_ID = 1 -- Filter by Remoteness ID for Inner Regional
ORDER BY
    ds.State;           -- Order results alphabetically by state

-- Query 4: Compare Population between Two Years for a Specific State/Remoteness Combination
SELECT
    ds.State,
    dr.Remoteness_Areas,
    fpw._2010 AS Population_2010,
    fpw._2020 AS Population_2020,
    (fpw._2020 - fpw._2010) AS Population_Change_2010_2020 -- Calculate the difference
FROM
    fact_population_wide fpw
JOIN
    dim_state ds ON fpw.State_ID = ds.State_ID
JOIN
    dim_remoteness dr ON fpw.Remoteness_ID = dr.Remoteness_ID
WHERE
    fpw.State_ID = 4      -- Filter for Queensland
    AND fpw.Remoteness_ID = 2; -- Filter for Outer 

-- Query 5: Calculate Total State Population for a Specific Year
SELECT
    ds.State,
    SUM(fpw._2023) AS Total_Population_2023 -- Sum the population for the year
FROM
    fact_population_wide fpw
JOIN
    dim_state ds ON fpw.State_ID = ds.State_ID
GROUP BY
    ds.State_ID, ds.State -- Group by state to sum correctly (include name in group by or use aggregate function)
ORDER BY
    Total_Population_2023 DESC; -- Show states with highest population first

-- query to check fact_crash
--Query: Get Total Crash Count and Total Population for NSW in 2023

-- Use CTEs to calculate each metric separately
WITH CrashCountNSW2023 AS (
    -- Calculate the total number of crashes in NSW for 2023
    SELECT
        COUNT(fc.Crash_ID) AS total_crashes
    FROM
        fact_crash fc
    JOIN
        dim_state ds ON fc.State_ID = ds.State_ID
    WHERE
        ds.State = 'NSW' -- Filter by state name
        AND fc.Year = 2023  -- Filter by year
),
PopulationNSW2023 AS (
    -- Calculate the total population for NSW in 2023
    -- Requires summing the population across all Remoteness areas for the state
    SELECT
        SUM(fpw._2023) AS total_population -- Directly reference the 2023 population column and sum it
    FROM
        fact_population_wide fpw
    JOIN
        dim_state ds ON fpw.State_ID = ds.State_ID
    WHERE
        ds.State = 'NSW' -- Filter by state name
)
-- Combine the results from the two CTEs for the final output
SELECT
    'NSW' AS State,               -- Display the state name
    2023 AS Year,                 -- Display the year
    cc.total_crashes,           -- Get the total crash count from the first CTE
    pt.total_population         -- Get the total population from the second CTE
FROM
    CrashCountNSW2023 cc,       -- Reference the first CTE
    PopulationNSW2023 pt;       -- Reference the second CTE