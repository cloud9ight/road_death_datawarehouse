CREATE TABLE Dim_Time (
    Time_ID SERIAL PRIMARY KEY,
    Time INTEGER,
    Time_of_Day VARCHAR(20),  -- Day/Night
    Time_Period VARCHAR(20)  -- SIX periods: Midnight, Early Morning, Morning, Afternoon, Evening, Late Night
);

CREATE TABLE dim_vehicle (
  vehicle_id     SERIAL PRIMARY KEY,
  bus_involved   SMALLINT   NULL,   -- 1:yes, 0:no, -9:unknown
  heavy_truck    SMALLINT   NULL,
  articulated_truck SMALLINT NULL,
  Description TEXT       -- e.g. Bus involvement unknown; Heavy rigid truck involvement unknown; Articulated truck involvement unknown
);

CREATE TABLE Dim_Road_Type (
    Road_ID SERIAL PRIMARY KEY,
    Road_Type VARCHAR(50)   -- include undermined road type
);


CREATE TABLE Dim_Crash_Type (
    Crash_Type_ID SERIAL PRIMARY KEY,
    Crash_Type VARCHAR(10)  -- single/multiple
);

CREATE TABLE Dim_Holiday (
    Holiday_ID SERIAL PRIMARY KEY,
    Christmas_Flag VARCHAR(3),  -- yes/no, total 3 combinations
    Easter_Flag VARCHAR(3)
);

CREATE TABLE dim_speed_limit (
    Speed_ID INT PRIMARY KEY,
    Speed_Value INT NOT NULL,    -- 0:unknown, 35:<40 detailed in description e.g. 90km/h
    Description VARCHAR(20) NOT NULL
);

CREATE TABLE Dim_Remoteness (
    Remoteness_ID SERIAL PRIMARY KEY,
    Remoteness_Areas TEXT NOT NULL  -- include unknown
);

CREATE TABLE Dim_State (
    State_ID SERIAL PRIMARY KEY,
    State VARCHAR(3) NOT NULL  -- total 8 states in abbreviation
);