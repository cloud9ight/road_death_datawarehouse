CREATE TABLE fact_crash (
    Crash_ID INT NOT NULL, 
    Time_ID INT NOT NULL, 
    Speed_ID INT NOT NULL, 
    State_ID INT NOT NULL, 
    Remoteness_ID INT NOT NULL, 
    Road_type_ID INT NOT NULL, 
    Crash_type_ID INT NOT NULL, 
    Vehicle_ID INT NOT NULL, 
    Holiday_ID INT NOT NULL, 
    Month INT NOT NULL, 
    Year INT NOT NULL, 
    Dayweek INT NOT NULL, 
    LGA_name VARCHAR(255) NOT NULL, 
    Number_Fatalities INT NOT NULL, 
    PRIMARY KEY (Crash_ID),
    
    -- Foreign Keys
	FOREIGN KEY (Time_ID) REFERENCES dim_time(Time_ID),
	FOREIGN KEY (Speed_ID) REFERENCES dim_speed_limit(Speed_ID),
    FOREIGN KEY (State_ID) REFERENCES dim_state(State_ID),
	
    FOREIGN KEY (Remoteness_ID) REFERENCES dim_remoteness(Remoteness_ID),
    FOREIGN KEY (Road_type_ID) REFERENCES dim_road_type(Road_ID),
    FOREIGN KEY (Crash_type_ID) REFERENCES dim_crash_type(Crash_type_ID),
    FOREIGN KEY (Vehicle_ID) REFERENCES dim_vehicle(Vehicle_ID),
    FOREIGN KEY (Holiday_ID) REFERENCES dim_holiday(Holiday_ID)
);

ALTER TABLE fact_crash ALTER COLUMN Dayweek TYPE VARCHAR;

select*from fact_crash;

CREATE TABLE fact_fatalities (
    fatality_id INT PRIMARY KEY,          -- Unique ID for each fatality record
    Crash_ID INT,                         -- Reference to Crash_ID from the fact_crash table
    Road_User VARCHAR(50),               -- Road user (Driver, Passenger, etc.), with 'Unknown' for invalid values
    Gender VARCHAR(10),                  -- Gender of the individual involved, 'Unknown' for -9
    Age INT,                         -- Age of the individual, -9 FOR 'Unknown' 
    Age_Group VARCHAR(15),                -- Age Group (e.g., 17_to_25), 'Unknown' for -9
	FOREIGN KEY (Crash_ID) REFERENCES fact_crash(Crash_ID)  -- Reference to Crash_ID in the fact_crash table
);
