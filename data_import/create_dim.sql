CREATE TABLE dim_vehicle_involvement (
    -- Surrogate Primary Key
    vehicle_involvement_sk BIGSERIAL PRIMARY KEY,

    -- Attributes based on source columns, mapping -9 to 'Unknown'
    bus_involved VARCHAR(10) NOT NULL
        CHECK (bus_involved IN ('Yes', 'No', 'Unknown')),

    heavy_rigid_truck_involved VARCHAR(10) NOT NULL
        CHECK (heavy_rigid_truck_involved IN ('Yes', 'No', 'Unknown')),

    articulated_truck_involved VARCHAR(10) NOT NULL
        CHECK (articulated_truck_involved IN ('Yes', 'No', 'Unknown')),

    -- Human-readable description of the combination
    description VARCHAR(255) NOT NULL,

    -- Ensure each combination of statuses is unique
    CONSTRAINT uq_vehicle_involvement_combo UNIQUE (bus_involved, heavy_rigid_truck_involved, articulated_truck_involved)
);


select*from dim_vehicle_involvement;

CREATE TABLE dim_road_type (
    road_type_sk BIGSERIAL PRIMARY KEY,
    national_road_type VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO dim_road_type (national_road_type) VALUES
('Access road'),
('Arterial Road'),
('Busway'),
('Collector Road'),
('Local Road'),
('National or State Highway'),
('Pedestrian Thoroughfare'),
('Sub-arterial Road'),
('Undetermined');

SELECT*FROM dim_road_type;

CREATE TABLE dim_crash_type (
    crash_type_sk BIGSERIAL PRIMARY KEY,
    crash_type VARCHAR(10) NOT NULL UNIQUE CHECK (crash_type IN ('Single', 'Multiple')) -- Added CHECK constraint as extra safety
);

SELECT*FROM dim_crash_type;

INSERT INTO dim_crash_type (crash_type) VALUES
('Single'),
('Multiple');

CREATE TABLE dim_speed_limit (
    speed_limit_sk BIGSERIAL PRIMARY KEY,
    speed_limit VARCHAR(15) NOT NULL UNIQUE -- Using VARCHAR to accommodate text like 'Unknown' and '<40'
);

INSERT INTO dim_speed_limit (speed_limit) VALUES
('5'),
('10'),
('15'),
('20'),
('25'),
('30'),
('40'),
('50'),
('60'),
('70'),
('75'),
('80'),
('90'),
('100'),
('110'),
('130'),
('<40'),
('Unknown'); 
select*from dim_speed_limit;

CREATE TABLE dim_remoteness_area (
    remoteness_sk BIGSERIAL PRIMARY KEY,
    remoteness_area_name VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO dim_remoteness_area (remoteness_area_name) VALUES
('Major Cities of Australia'),
('Inner Regional Australia'),
('Outer Regional Australia'),
('Remote Australia'),
('Very Remote Australia'),
('Unknown'); 
