---
title: "**Project 1 Report: Analysing Australian Road Fatal Crash with a Data Warehouse**"
---

# **Project 1 Report: Analysing Australian Road Fatal Crash with a Data Warehouse**

## **1. Introduction**

### **1.1 Project Aim and Significance**

This project aims to design, implement, and utilize a data warehouse to analyze historical data on fatal road crashes in Australia. The significance of this work stems from the persistent challenge of road safety. Australia's road fatality rate, averaging 4.8 deaths per 100,000 people in 2023, lags behind top performers globally like Iceland (2.1 deaths per 100,000) [1]. With a 12-month total of 1327 road deaths nationally leading up to July 2024, representing a 10% increase from the prior year [2], there is a critical need for data-driven insights to understand contributing factors and inform effective safety interventions. This project seeks to leverage data warehousing and data mining techniques to uncover patterns and provide actionable recommendations towards reducing the national road toll.

### **1.2 Data Sources Used**

The primary data sources for this project are from the Australian Road Deaths Database (ARDD) [3, 4]:

- `bitre_fatal_crashes_dec2024.xlsx`
- `bitre_fatalities_dec2024.xlsx`
- `Population estimates by LGA, Significant Urban Area, Remoteness Area, Commonwealth Electoral Division and State Electoral Division, 2001 to 2023.xlsx`

Additionally, geospatial boundary data was utilized:

- `GeoJSON` files for Local Government Areas (LGA), and States (STE).

### **1.3 Methodology**

The project employed several key methodologies:

- **Dimensional Modeling:** Kimball's four-step process [7] guided the design of the data warehouse schema.
- **ETL (Extract, Transform, Load):** Processes were developed using Python with Pandas, Numpy library and Excel to clean, transform, and load data from source files into the PostgreSQL database.
- **Data Warehousing:** A relational database warehouse was implemented using PostgreSQL.
- **Data Visualization:** **Tableau** was used to create interactive dashboards visualizing key insights derived from business queries against the warehouse.
- **Association Rule Mining (ARM):** Python libraries ( `mlxtend`) were used to perform ARM to discover interesting relationships within the fatality data.

### **1.4 Report Structure**

This report details the project in the following sections: Section 2 outlines the data warehouse design process and the final schema. Section 3 presents the business questions the warehouse is designed to answer. Section 4 describes the ETL process in detail. Section 5 discusses the implementation and presents key visualizations. Section 6 details the association rule mining process, results, and recommendations. Section 7 concludes the report with a summary, limitations, and future work. Section 8 lists references, and Section 9 contains appendices.

## **2. Data Warehouse Design and Schema (Kimball's Steps)**

#### 2.1 Business Process Understanding -Process

The primary business process being modeled is the **recording and analysis of fatal road crashes** occurring within Australia. This involves capturing details about the crash event itself (when, where, how) and the resulting fatalities (who). A secondary, related process essential for contextual analysis (especially for calculating rates) is **tracking population distribution** across relevant geographical areas (State, Remoteness Area).

#### 2.2 Declare the Grain

The grain, or the level of detail represented by a single row, was defined for each fact table:

- **`fact_crash`:** The grain is one row per unique fatal crash event identified by `Crash_ID`.
- **`fact_fatalities`:** The grain is one row per unique fatality identified by `fatality_id`, linked to a specific crash via `Crash_ID`.
- **`fact_population_wide`:** The grain is one row per unique combination of State and Remoteness Area, containing population estimates as separate columns for the years 2001 to 2023.

#### **2.3 Conceptual Schema and StarNet Diagram**

A **Fact Constellation Schema** was chosen for the overall data warehouse structure, comprising multiple fact tables (`fact_crash`, `fact_fatalities`, `fact_population_wide`) that share some common dimension tables (e.g., `Dim_State`, `Dim_Remoteness`). The core analysis of crash events, centered around `fact_crash`, adheres to **Star Schema** principles. This hybrid approach was selected because:

- It naturally accommodates the different grains of data (crashes, individual fatalities, population counts).

- The Star Schema component for `fact_crash` offers simplicity and generally better query performance for common analyses compared to more normalized structures [7].

- Shared dimensions allow for integrated analysis across the different fact tables (e.g., linking crash locations to population data).

**[------StarNet Diagram Here------]**
_Figure 1: StarNet Diagram illustrating the Data Warehouse Schema._

**Explanation:** Figure 1 shows the logical structure of the warehouse. The fact tables (`fact_crash`, `fact_fatalities`, `fact_population_wide`) are central, containing measures and foreign keys. They connect to the surrounding dimension tables (`Dim_Time`, `dim_speed_limit`, etc.) via these keys. The diagram illustrates the attributes within each dimension and indicates concept hierarchies (e.g., within `Dim_Time`), visually representing the schema's capability to support analytical queries through slicing, dicing, and drill-down/roll-up operations.

#### **2.4 Dimension Table Design** (Kimball Step 3: Dimensions)

##### **2.4.1 `Dim_Time`**

```sql
CREATE TABLE Dim_Time (
    Time_ID SERIAL PRIMARY KEY,
    Time INTEGER, -- Represents the hour of the day (0-23)
    Time_of_Day VARCHAR(20),  -- e.g., Day, Night
    Time_Period VARCHAR(20)  -- e.g., Morning, Afternoon, Late Night
);
```

- **Purpose:** Describes the time-of-day aspects of a crash.
- **Attributes:** `Time_ID` (PK), `Time` (Hour), `Time_of_Day`, `Time_Period`.
- **Hierarchy:** `Time` (Hour) -> `Time_Period` -> `Time_of_Day`.
- **Rationale:** Simplified to focus on intra-day patterns. Date components (`Year`, `Month`, `Dayweek`) are kept in `fact_crash` for dimension simplicity.

##### **2.4.2 `dim_speed_limit`**

```sql
CREATE TABLE dim_speed_limit (
    Speed_ID INT PRIMARY KEY, -- Managed during ETL
    Speed_Value INT NOT NULL,    -- e.g., 50, 60, 100, 0 for unknown, 35 for <40
    Description VARCHAR(20) NOT NULL -- e.g., '50 km/h', 'Unknown', '<40 km/h'
);
```

- **Purpose:** Describes the posted speed limit at the crash location.
- **Attributes:** `Speed_ID` (PK), `Speed_Value`, `Description`.
- **Hierarchy:** None formally defined; conceptual grouping possible.
- **Rationale:** Captures speed limit, handling specific codes ('Unknown', '<40').

##### **2.4.3 `Dim_State`**

```sql
CREATE TABLE Dim_State (
    State_ID SERIAL PRIMARY KEY,
    State VARCHAR(3) NOT NULL  -- e.g., WA, NSW, VIC,...
);
```

- **Purpose:** Identifies the Australian state or territory.
- **Attributes:** `State_ID` (PK), `State` (Abbreviation).
- **Hierarchy:** State/Territory is the primary level.

##### **2.4.4 `Dim_Remoteness`**

```sql
CREATE TABLE Dim_Remoteness (
    Remoteness_ID SERIAL PRIMARY KEY,
    Remoteness_Areas TEXT NOT NULL  -- e.g., Major Cities, ..., Unknown
);
```

- **Purpose:** Classifies location based on remoteness.
- **Attributes:** `Remoteness_ID` (PK), `Remoteness_Areas`.
- **Hierarchy:** Follows ABS remoteness levels (treated as categories).

##### **2.4.5 `Dim_Road_Type`**

```sql
CREATE TABLE Dim_Road_Type (
    Road_ID SERIAL PRIMARY KEY,
    Road_Type VARCHAR(50)   -- e.g., Highway, Arterial, ..., Undetermined
);
```

- **Purpose:** Classifies the type of road.
- **Attributes:** `Road_ID` (PK), `Road_Type`.
- **Hierarchy:** None formally defined; conceptual grouping possible.

##### **2.4.6 `Dim_Crash_Type`**

```sql
CREATE TABLE Dim_Crash_Type (
    Crash_Type_ID SERIAL PRIMARY KEY,
    Crash_Type VARCHAR(10)  -- 'single'/'multiple' vehicle crash
);
```

- **Purpose:** High-level classification based on vehicle involvement.
- **Attributes:** `Crash_Type_ID` (PK), `Crash_Type`.
- **Hierarchy:** Basic binary: Single / Multiple.
- **Rationale:** Simplified from detailed ARDD crash types for high-level analysis.

##### **2.4.7 `dim_vehicle`**

```sql
CREATE TABLE dim_vehicle (
  vehicle_id     SERIAL PRIMARY KEY,
  bus_involved   SMALLINT,   -- 1:yes, 0:no, -9:unknown
  heavy_truck    SMALLINT,
  articulated_truck SMALLINT,
  Description TEXT
);
```

- **Purpose:** Describes involvement of specific large vehicle types.
- **Attributes:** `vehicle_id` (PK), flags for Bus, Heavy Truck, Articulated Truck involvement, `Description`.
- **Hierarchy:** None formally defined. Captures involvement profile.

##### **2.4.8 `Dim_Holiday`**

```sql
CREATE TABLE Dim_Holiday (
    Holiday_ID SERIAL PRIMARY KEY,
    Christmas_Flag VARCHAR(3),  -- yes/no
    Easter_Flag VARCHAR(3)     -- yes/no
);
```

- **Purpose:** Indicates if crash occurred during Christmas or Easter periods.
- **Attributes:** `Holiday_ID` (PK), `Christmas_Flag`, `Easter_Flag`.
- **Hierarchy:** None.
- **Rationale:** Focuses analysis on these specific high-travel periods.

#### **2.5 Fact Table Design** (Kimball Step 4: Facts)

**Fact tables design justified in section 2.6**

##### **2.5.1 `fact_crash`**

```sql
CREATE TABLE fact_crash (
    Crash_ID INT NOT NULL PRIMARY KEY, -- Assuming Crash_ID from source is unique PK
    Time_ID INT NOT NULL,
    Speed_ID INT NOT NULL,
    State_ID INT NOT NULL,
    Remoteness_ID INT NOT NULL,
    Road_type_ID INT NOT NULL,
    Crash_type_ID INT NOT NULL,
    Vehicle_ID INT NOT NULL,
    Holiday_ID INT NOT NULL,
    Month INT NOT NULL, -- Kept from source, links conceptually to Dim_Time if needed
    Year INT NOT NULL, -- Kept from source
    Dayweek VARCHAR NOT NULL, -- Kept from source
    LGA_name VARCHAR(255) NOT NULL, -- Degenerate Dimension
    Number_Fatalities INT NOT NULL, -- Measure
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
```

- **Grain:** One row per fatal crash event.
- **Measures:** `Number_Fatalities` (additive), Implicit `Crash_Count` (additive).
- **Foreign Keys:** Link to all 8 dimension tables.
- **Other Attributes:** `Month`, `Year`, `Dayweek` (kept from source), `LGA_name` (degenerate dimension).

##### **2.5.2 `fact_fatalities`**

```sql
CREATE TABLE fact_fatalities (
    fatality_id INT PRIMARY KEY,          -- Unique ID for each fatality record
    Crash_ID INT REFERENCES fact_crash(Crash_ID), -- Link to crash event
    Road_User VARCHAR(50),               -- Degenerate Dimension
    Gender VARCHAR(10),                  -- Degenerate Dimension ('Unknown' for -9)
    Age INT,                             -- Descriptive Measure / Degenerate Dim (-9 for 'Unknown')
    Age_Group VARCHAR(15)                -- Degenerate Dimension ('Unknown' for -9)
);
```

- **Grain:** One row per fatality.
- **Measures:** Implicit `Fatality_Count` (additive), `Age` (non-additive descriptive measure).
- **Foreign Keys:** `Crash_ID` links to `fact_crash`.
- **Degenerate Dimensions:** `Road_User`, `Gender`, `Age_Group`.

##### **2.5.3 `fact_population_wide`** (CITS5504 Specific)

```sql
CREATE TABLE fact_population_wide (
    State_Population_ID INT PRIMARY KEY, -- Assuming unique ID generated during ETL
    State_ID INT NOT NULL REFERENCES dim_state(State_ID),
    Remoteness_ID INT NOT NULL REFERENCES dim_remoteness(Remoteness_ID),
    -- Population columns (Measures)
    _2001 INT NULL, _2002 INT NULL, ..., _2023 INT NULL,
    CONSTRAINT UQ_population_state_remoteness UNIQUE (State_ID, Remoteness_ID)
);
```

- **Grain:** One row per State-Remoteness area combination.
- **Measures:** `_2001`...`_2023` (Population counts - semi-additive across geography, non-additive across time).
- **Foreign Keys:** `State_ID`, `Remoteness_ID` link to respective dimensions.

#### **2.6 Design Rationale: Attribute Placement and Degenerate Dimensions**

**Explaination**

A key consideration throughout the design process was balancing the principles of dimensional modeling with the specific analytical goals and data characteristics of this project. As data warehousing design is often open-ended with multiple valid solutions, certain decisions were made based on prioritizing a pragmatic approach focused on the intended analyses.

- Focus on `fact_crash` and Star Schema Core: **The primary analytical focus was centred on the crash event itself**, making fact_crash the natural core fact table, aligning well with Star Schema principles for analyzing crash circumstances (when, where, how, speed, etc.).

- Attributes in `fact_fatalities` (Gender, Age_Group, Road_User): While Gender, Age_Group, and Road_User represent categorical attributes describing the fatality, the decision was made not to create separate dimension tables for them. Instead, they are included directly within the fact_fatalities table, effectively acting as degenerate dimensions.

**Reasoning:**
The anticipated analysis scope for these specific attributes (visualizing distributions, filtering) was deemed manageable directly from the fact_fatalities table. Creating very simple dimension tables (e.g., a Gender dimension with just Male/Female/Unknown, no hierarchy) was considered potentially redundant, adding extra joins for limited analytical gain within the specific scope of this project. This approach simplifies the schema slightly for analyses focused solely on fatality demographics.

- Attributes in `fact_crash` (Year, Month, Dayweek, Number_Fatalities):

* Number_Fatalities is clearly the primary measure related to the crash event's severity.
* For the time components (Year, Month, Dayweek), these were intentionally kept as direct attributes in fact_crash rather than building a comprehensive Dim_Date dimension linked via a single date key.

Reasoning: The primary temporal analysis intended was focused on longer-term annual (Year) trends or potentially broad seasonal (Month) or weekly (Dayweek) patterns. Creating simple dimension tables for Month (ID 1-12) or Dayweek (ID 1-7) felt unnecessary, as the values themselves are inherently meaningful and low-cardinality. Building a full Dim_Date table (linking Year, Month, Day, DayOfWeek, etc.) would add complexity and potentially a very large dimension table, which seemed disproportionate given that highly granular, date-specific slicing (e.g., "fatalities on the 3rd Tuesday of every March") was not a primary analytical goal. Keeping Year, Month, and Dayweek directly facilitates straightforward filtering and grouping for the most common temporal queries relevant to this project.

We believe that this design reflects a pragmatic interpretation aimed at creating an effective and understandable warehouse tailored to the specific requirements and anticipated usage patterns of this road fatality analysis.

## **3. Analytical Capabilities: Business Questions**

#### **3.1 Target Business Questions**

The data warehouse is designed to answer questions such as:

1.  How did the quarterly fatality rate (fatalities per 100,000 population) change from 2021 to 2023 in WA compared to VIC?
2.  Which specific LGAs within 'Remote Australia' or 'Very Remote Australia' experienced the highest number of fatal crashes on 'National highway' or 'State highway' road types in 2023?
3.  What is the age group and gender distribution of pedestrian fatalities (`Road_User = 'Pedestrian'`) that occurred during 'Evening' or 'Late Night' time periods?
4.  Was the proportion of fatal crashes involving heavy vehicles higher during the Easter holiday period compared to non-Easter periods in speed zones of 100 km/h or more?
5.  In 'Major Cities' versus 'Outer Regional Australia', what is the average number of fatalities per crash for 'single' vehicle crashes compared to 'multiple' vehicle crashes?
6.  Across all states, what is the breakdown of fatalities by `Road_User` type occurring in 'Inner Regional Australia' for the year 2022?

#### **3.2 Query Footprints**

- **Q1:** Requires `fact_crash` (for fatality counts, Year, Month), `fact_population_wide` (population for State, Year), `Dim_State`.
- **Q2:** Requires `fact_crash` (crash count, LGA_name, Year, Road_type_ID FK, Remoteness_ID FK), `Dim_Remoteness`, `Dim_Road_Type`. Needs link to GeoJSON via `LGA_name`.
- **Q3:** Requires `fact_fatalities` (Age_Group, Gender, Road_User), `fact_crash` (linking via Crash_ID, Time_ID FK), `Dim_Time`.
- **Q4:** Requires `fact_crash` (linking, Speed_ID FK, Holiday_ID FK, Vehicle_ID FK), `Dim_Holiday`, `dim_vehicle`, `dim_speed_limit`.
- **Q5:** Requires `fact_crash` (Number_Fatalities, Remoteness_ID FK, Crash_Type_ID FK), `Dim_Remoteness`, `Dim_Crash_Type`.
- **Q6:** Requires `fact_fatalities` (Road_User), `fact_crash` (linking, Year, State_ID FK, Remoteness_ID FK), `Dim_State`, `Dim_Remoteness`.

## **4. Data Integration: ETL Process**

#### **4.1 Data Sources and Tools Used**

- **Sources:** ARDD XLSX files [3, 4], ABS Population XLSX [6], GeoJSON files [Source details].
- **Tools:** Python (Version [e.g., 3.9+]) with libraries including Pandas (for data manipulation), NumPy (for numerical operations), Psycopg2 (for PostgreSQL interaction), GeoPandas (for GeoJSON handling), PostgreSQL (Version [e.g., 14+]) as the database, [e.g., pgAdmin or DBeaver] for database management.

#### **4.2 ETL Workflow Overview**

The ETL process followed a standard workflow:

1.  **Extract:** Reading data from source Excel (XLSX) and GeoJSON files into Pandas/GeoPandas DataFrames.
2.  **Transform:** Cleaning data, handling missing/special values, standardizing formats, deriving new attributes, generating surrogate keys for dimensions, and structuring data according to the target warehouse schema.
3.  **Load:** Populating the dimension tables first, followed by the fact tables in the PostgreSQL database.
    _[Optionally insert a simple flowchart diagram of ETL process here]_

#### **4.3 Extraction Details**

- Data was extracted from source files using Pandas `read_excel` for XLSX and GeoPandas `read_file` for GeoJSON.
- [Mention any specific sheets read, or initial filtering done at extraction, if any].

#### **4.4 Transformation Details**

This involved several key steps:

- **Data Cleaning:**
  - Handling `-9` (Unknown/Not Applicable): [Describe how -9 was handled *specifically* for columns like Age, Gender, Speed Limit, Vehicle flags. E.g., "Replaced -9 in Age with NULL", "Mapped -9 in Gender to 'Unknown'", "Kept -9 in vehicle flags as a valid state"].
  - Handling Blanks/NULLs: [Describe how other blanks/NULLs were handled. E.g., "Rows with NULL Crash_ID were dropped", "NULLs in non-critical descriptive fields were kept or replaced with 'Unknown'"].
  - Consistency Checks: [Describe any checks, e.g., ensuring Crash_ID exists in crash data before loading fatality data].
  - LGA Name Standardization: [Describe steps taken, e.g., "Trimmed whitespace", "Converted to uppercase", "Mapped known variations like 'City of...' to a standard name to match GeoJSON"].
- **Standardization:**
  - Date/Time Parsing: [Describe how date/time columns were parsed if complex, though Dim_Time is simple].
  - Data Type Conversion: Ensured numeric columns were integer/float, text columns were VARCHAR/TEXT.
- **Derivations:**
  - `Dim_Time`: Extracted hour from source time, derived `Time_of_Day` ('Day'/'Night') and `Time_Period` ('Morning', etc.) based on the hour. [Provide logic/code snippet].
  - `fact_fatalities`: Derived `Age_Group` from `Age` using predefined bins [Specify bins, e.g., 0-16, 17-25,...].
  - `Dim_Holiday`: Created flags based on checking crash dates against defined date ranges for Christmas and Easter. [Specify date ranges used].
  - `dim_vehicle`: Populated the `Description` field based on the flag values.
- **Surrogate Key Generation/Lookup:**
  - Dimension tables were populated first by selecting distinct attribute combinations from the source data. Surrogate keys (`SERIAL` or generated integers like for `dim_speed_limit`) were assigned.
  - During fact table loading, the corresponding dimension attributes from the source row were used to look up the correct surrogate key from the populated dimension table (e.g., using dictionary lookups or database joins). [Describe specific lookup method].
- **Data Merging/Linking:**
  - `fact_fatalities` linked to `fact_crash` using `Crash_ID`.
  - `fact_population_wide` data was cleaned, ensuring `State` and `Remoteness_Areas` matched the values used in `Dim_State` and `Dim_Remoteness` for joining.
  - GeoJSON data was prepared for joining based on the cleaned `LGA_name`.
- **Data Reduction:**
  - [Explicitly state which rows were removed and why. E.g., "A total of X rows (Y% of the initial crash dataset) were removed. This included Z rows missing essential location information (State or LGA Name after cleaning) and W rows missing critical time information, rendering them unsuitable for core analyses. This removal percentage (Y%) is below the 5% threshold."]. **Justify clearly why removal was necessary.**
    _[Insert key Python/Pandas code snippets and screenshots illustrating transformations, e.g., handling -9, deriving Time_Period, LGA name cleaning, surrogate key lookup logic]_

#### **4.5 Loading Strategy**

- Data was loaded into PostgreSQL in dependency order: Dimension tables were loaded first, followed by fact tables (`fact_crash`, `fact_fatalities`, `fact_population_wide`).
- [Describe loading method: E.g., "Used Python's Psycopg2 library with parameterized INSERT statements", or "Generated intermediate CSV files and used PostgreSQL's efficient `COPY FROM` command for bulk loading large tables"].

## **5. Implementation and Visualization**

#### **5.1 SQL Implementation Scripts Reference**

The complete, commented SQL scripts (`.sql` files) used to create the database schema (all `CREATE TABLE` statements) and potentially for bulk data loading (e.g., `COPY` commands) are provided as separate files in the submission package. _(Addresses SQL Script file - 5 marks)_

#### **5.2 Visualization Overview and Justify**

Interactive dashboard was created using Tableau to visualize the key insights derived from the data warehouse. The dashboard aims to provide more accessible overview of fatal crash trends, geographical distributions, and contributing factors based on the business questions defined in Section 3.1. The complete interactive dashboard is provided as a `.pdf` file in the submission package.

##### Explain chosen visualizations or metrics

When deciding how best to analyze the crash data over time, especially after incorporating the annual LGA population figures, different possibilities were considered. Initially, looking at very specific dates or months seemed like an option to spot spikes, perhaps around holidays (though our Dim_Holiday already covers major ones) or maybe after new rules came in. However, the effects of things like new laws or safety campaigns usually show up more gradually over the years. Focusing the main time-based analysis on the Year attribute felt like the right balance – it allows us to see these longer-term trends without getting lost in daily or monthly fluctuations that might just be noise.

With the population data available from 2001 onwards, comparing the growth rate of the population to the growth rate of fatalities for each LGA was another idea I explored. The thinking was, this might show if safety was improving or declining relative to how much the area was growing.

However, I decided against making this growth rate comparison the central part of the analysis, particularly for the LGA map. The main reason was the small number of fatalities in many LGAs each year. If an LGA goes from, say, one death one year to two the next, that's a 100% growth rate, which sounds dramatic but could easily be random chance. Comparing these jumpy fatality growth numbers to smoother population growth felt like it could give a skewed picture at the local level. Also, population size itself isn't a perfect measure of how much people are actually driving in an area.

Therefore, to get a clearer and more stable picture of the actual risk level across different areas, I chose to focus the primary geographic and temporal analysis (especially for the map) on the 'Fatality Rate per 100,000 Population' calculated for each LGA, each year. This standard measure directly compares the number of fatalities to the size of the community living there, making it much easier to fairly compare risk between a small town and a large city and to see where the relative danger is highest in any given year."

#### **5.3 Visualizations Answering Business Questions**

_(Addresses Visualize Queries - 5 marks)_

##### **5.3.1 Business Question 1 Visualization (State Fatality Rate Trends)**

- **[Insert Screenshot of Line Chart showing quarterly fatality rate per 100k for WA vs VIC, 2021-2023]**
- _Figure 2: Quarterly Fatality Rate per 100k Population (WA vs VIC, 2021-2023)._
- **Chart Justification:** A line chart is appropriate for showing trends over time, clearly comparing the rate changes between the two states across quarters.
- **Key Insight:** [Describe what the chart shows, e.g., "The visualization indicates that while both states show seasonal fluctuations, State X consistently maintained a higher/lower fatality rate per capita than State Y during this period, with a noticeable peak/trough in Quarter Z of Year A."].

##### **5.3.2 Business Question 2 Visualization (Remote Highway Crashes - Map)**

- **[Insert Screenshot of Map Chart (Choropleth) showing crash counts or concentration on highways in remote LGAs for 2023]**
- _Figure 3: Fatal Highway Crashes in Remote/Very Remote LGAs (2023)._
- **Chart Justification:** A map chart (Choropleth map using LGA boundaries from GeoJSON) is essential (**compulsory requirement**) for visualizing the geographical distribution and concentration of crashes across different remote LGAs. Color intensity represents crash counts.
- **Key Insight:** [Describe what the map shows, e.g., "The map highlights specific LGAs such as [LGA Name 1] and [LGA Name 2] in [State] as having a significantly higher concentration of fatal crashes on highways within remote areas during 2023, suggesting potential geographical risk zones."].

##### **5.3.3 Business Question 3 Visualization (Pedestrian Fatality Demographics)**

- **[Insert Screenshot of Grouped Bar Chart showing age group/gender distribution for pedestrian fatalities at night]**
- _Figure 4: Age Group and Gender of Pedestrian Fatalities during Evening/Late Night._
- **Chart Justification:** A grouped bar chart effectively compares the counts across different age groups, with segmentation by gender, for the specific subset of pedestrian fatalities occurring during darker hours.
- **Key Insight:** [Describe what the chart shows, e.g., "The data reveals that the [Specific Age Group, e.g., 65+] age group represents the largest proportion of pedestrian fatalities during evening/late night periods, with a higher incidence among [Male/Female] individuals."].

##### **5.3.4 Business Question 4 Visualization (Holiday Heavy Vehicle Crashes)**

- **[Insert Screenshot of Bar Chart or Pie Chart comparing proportion of heavy vehicle crashes on holidays vs non-holidays in high-speed zones]**
- _Figure 5: Proportion of Fatal Crashes Involving Heavy Vehicles (>=100 km/h zones) during Easter vs Non-Easter Periods._
- **Chart Justification:** A bar chart comparing the percentage of relevant crashes (or two pie charts side-by-side) clearly illustrates whether the proportion involving heavy vehicles differs between Easter and non-Easter periods under the specified conditions.
- **Key Insight:** [Describe what the chart shows, e.g., "The analysis indicates that the proportion of fatal crashes involving heavy vehicles in high-speed zones was [higher/lower/not significantly different] during the Easter period compared to non-Easter periods, suggesting [potential increased risk / no specific holiday effect] for this scenario."].

##### **5.3.5 LGA Fatality Rate per 100,000 Population Map - addressing geographical risk distribution relative to population**

**This section corresponds to one of the visualizations answering a business question, specifically addressing geographical risk distribution relative to population.**

**Business Question Addressed:** Which Local Government Areas (LGAs) exhibit the highest relative risk of road fatalities when accounting for their population size, for a selected year?

**Rationale:** While maps showing raw fatality counts identify areas with the most incidents, they are heavily biased towards densely populated LGAs. Calculating the fatality rate per 100,000 population normalizes for population differences, providing a more equitable measure of road safety risk across diverse LGAs. Identifying LGAs with high fatality rates, even if absolute numbers are low, highlights areas where the risk relative to the resident population is significant, potentially indicating infrastructure issues, high through-traffic risks, or other localized factors needing attention. This visualization is crucial for targeted resource allocation and safety interventions.

**Data Sources and Fields Used:**

1.  **`fact_crash`:**

    - `Crash_ID`
    - `Number_Fatalities`: Aggregated to get fatality counts per LGA/Year.
    - `Year`: Used for filtering and linking to the population year.
    - `LGA_name`: Used as the primary key to link crash data to population and GeoJSON data.

2.  **`LGA_pop` (Excel Source - Wide Format):**
    - `LGA code` : The linking key.
    - Columns `2001`, `2002`, ..., `2023`: Contain the Estimated Resident Population (ERP) for each LGA for each year. These are accessed dynamically via a calculated field.
      **I extract and format this table from `Population estimates by LGA, Significant Urban Area, Remoteness Area, Commonwealth Electoral Division and State Electoral Division, 2001 to 2023.xlsx` sheet `Table 1`**
3.  **GeoJSON Source:**
    - `Geometry`: Provides the LGA boundary polygons for map rendering.
    - `LGA Code21`: Used to link the geographic shapes to the data.
    - `Ste Name21`: Used for filtering the map by state.

**Tableau Implementation Steps:**

1.  **Established relationships** :
2.  - `LGA_pop` related to `GeoJSON` on `LGA Code`
    - `fact_crash` related to `LGA_pop` on `LGA name`.
    - `fact_crash` related to `GeoJSON` source on `LGA name`
3.  **Parameter Creation:**
    - Created an Integer parameter named `[Select Year]` with allowable values restricted to the range 2001-2023 (matching available population data)
4.  **Calculated Field:**
    - **`[Selected Year Fatality Count (LGA)]`:**
      ```tableau
      // Calculates total fatalities for the selected year per LGA
      SUM(IF [Year] = [Select Year] THEN [Number_Fatalities] ELSE 0 END)
      ```
    - **`[Selected Year Population (LGA)]`:** (Using the unpivoted approach)

      ```tableau
      // Retrieves population for the selected year from the wide LGA_pop table
      MIN(
          CASE [Select Year]
              WHEN 2001 THEN [2001]
              WHEN 2002 THEN [2002]
              // ... includes all years from 2003 to 2022 ...
              WHEN 2023 THEN [2023]
              ELSE NULL
          END
      )
      ```

    - **`[Fatality Rate per 100k (LGA)]`:**
      ```tableau
      // Calculates the rate, handling potential division by zero
      IF [Selected Year Population (LGA)] > 0 THEN
          ([Selected Year Fatality Count (LGA)] * 100000) / [Selected Year Population (LGA)]
      ELSE
          NULL
      END
      ```
5.  **Map Construction:**
    - In a new worksheet. Use `Geometry` (from GeoJSON) to generate the base map.
    - Dragged `LGA_name` onto the **Detail** shelf on the Marks card.
    - Dragged the calculated field `[Fatality Rate per 100k (LGA)]` onto the **Color** shelf.
    - Ensured the `[Select Year]` parameter control was shown.
6.  **Tooltip**
    - Edited the Tooltip to display `LGA_name`, the selected `Year` (from the parameter), the calculated `Selected Year Fatality Count (LGA)`, `Selected Year Population (LGA)`, and the formatted `Fatality Rate per 100k (LGA)`.

**Visualization:**

![image](https://hackmd.io/_uploads/Bk8xtEfCyg.png)
_Figure X: Road Fatality Rate per 100,000 Population by LGA for [2023]._

**Interpretation of Insights:**

This LGA-level fatality rate map for [2023] reveals considerable geographic variation in road safety risk relative to population. While most LGAs exhibit low-to-moderate rates, a number of sparsely populated regional and remote LGAs display markedly elevated rates (>50 in yellowish color or >100 per 100k in dark green).

But it is crucial to interpret these high rates with caution; they often reflect the significant statistical impact of even a single fatality within a very small resident population base, rather than necessarily indicating consistently extreme underlying risk for residents themselves. The specific LGAs appearing as high-rate 'hotspots' demonstrate considerable volatility year-on-year, suggesting these high rates in low-population areas may be driven by infrequent but high-consequence events, potentially involving through-traffic on major routes within those LGA boundaries.

Therefore, while highlighting areas where fatalities have a disproportionate impact relative to local population, this map underscores the need for analyzing multi-year trends and considering factors beyond resident population when assessing risk in geographically vast and sparsely populated regions like much of Australia

**Limitations:**

- Rates calculated for very low population LGAs can be volatile year-on-year due to small changes in fatality numbers having a large percentage impact.
- The rate reflects fatalities occurring _within_ the LGA boundary relative to the _resident_ population, not necessarily the residency of the person involved in the crash. High rates in some LGAs might be influenced by crashes involving non-residents on major highways passing through.

## **6. Data Mining: Association Rules for Road Safety**

#### **6.1 Data Preparation for ARM**

- Data for association rule mining was prepared by joining relevant attributes from `fact_crash` and `fact_fatalities`.
- Selected attributes included: [List attributes used, e.g., `State`, `Remoteness_Areas`, `Speed_Value` (grouped into Low/Medium/High), `Road_Type` (grouped), `Crash_Type` (single/multiple), `Time_of_Day`, `Time_Period`, `Christmas_Flag`, `Easter_Flag`, `bus_involved`, `heavy_truck`, `articulated_truck`, `Road_User`, `Gender`, `Age_Group`].
- Categorical attributes were transformed into a transactional format using one-hot encoding via Pandas `get_dummies`. Each row (representing a fatality) became a transaction, and each attribute-value pair (e.g., 'State=WA', 'Speed=High', 'Road_User=Driver') became an item.
- [Mention any specific filtering applied only for ARM, e.g., removing very rare categories].

#### **6.2 Algorithm Selection and Setup**

- The **[Apriori / FP-Growth]** algorithm was selected for mining frequent itemsets and association rules.
- **Justification:** [e.g., "Apriori was chosen due to its foundational nature and availability in the `mlxtend` library [8]. It guarantees finding all rules meeting the support/confidence thresholds."] OR ["FP-Growth was chosen for its potential efficiency advantage on large datasets by avoiding candidate generation [9], implemented via `mlxtend`."]
- The algorithm was implemented using the `mlxtend.frequent_patterns` library in Python.
- Mining Parameters:
  - `min_support` = [Specify value, e.g., 0.01 or 1%]. Rationale: [e.g., "Chosen after experimentation to capture reasonably frequent patterns without being overwhelmed by trivial ones."].
  - `min_confidence` = [Specify value, e.g., 0.5 or 50%]. Rationale: [e.g., "Set to ensure rules reflect a reasonably strong implication between items."].
  - Rules were generated using the `association_rules` function from `mlxtend`, typically using 'lift' as the metric for evaluating interestingness alongside confidence.

#### **6.3 Top Rule Analysis (Road User RHS)**

The following table presents the top [k=e.g., 5] association rules where a specific `Road_User` type is on the right-hand side (consequent), ranked primarily by **Lift** (descending), also showing Confidence and Support.

| Antecedents (LHS)                                                                     | Consequent (RHS)                                    | Support     | Confidence  | Lift        |
| :------------------------------------------------------------------------------------ | :-------------------------------------------------- | :---------- | :---------- | :---------- |
| **[Rule 1 Antecedent Items, e.g., {'Crash_Type=Pedestrian', 'Time_Of_Day=Night'}]**   | **{'Road_User=[Target User, e.g., Pedestrian]'}**   | **[Supp1]** | **[Conf1]** | **[Lift1]** |
| **[Rule 2 Antecedent Items, e.g., {'Vehicle_Type=Motorcycle', 'DayOfWeek=Weekend'}]** | **{'Road_User=[Target User, e.g., Motorcyclist]'}** | **[Supp2]** | **[Conf2]** | **[Lift2]** |
| **[Rule 3 Antecedent Items]**                                                         | **{'Road_User=[Target User]'}**                     | **[Supp3]** | **[Conf3]** | **[Lift3]** |
| **[Rule 4 Antecedent Items]**                                                         | **{'Road_User=[Target User]'}**                     | **[Supp4]** | **[Conf4]** | **[Lift4]** |
| **[Rule 5 Antecedent Items]**                                                         | **{'Road_User=[Target User]'}**                     | **[Supp5]** | **[Conf5]** | **[Lift5]** |
| _Table 1: Top 5 Association Rules with Road User Consequent (Ranked by Lift)._        |                                                     |             |             |             |
| _[Note: Replace bracketed placeholders with actual results. Ensure k >= 2]_           |                                                     |             |             |             |

#### **6.4 Rule Interpretation and Insights**

- **Rule 1 Interpretation:** [Explain Rule 1 in plain English based on results. E.g., "This rule indicates that when a fatal crash involves [LHS conditions], there is a [Conf1 * 100]% probability that the fatality was a [Target User]. This scenario occurs in [Supp1 * 100]% of all fatalities. The lift of [Lift1] suggests this outcome is [Lift1] times more likely under these conditions than overall."]
- **Rule 2 Interpretation:** [Explain Rule 2 similarly...]
- **Rule 3 Interpretation:** [Explain Rule 3 similarly...]
- **Rule 4 Interpretation:** [Explain Rule 4 similarly...]
- **Rule 5 Interpretation:** [Explain Rule 5 similarly...]
- **Overall Insights:** [Discuss the key patterns revealed. E.g., "The rules consistently highlight the elevated risk for [Target User 1] under [Condition Set A], particularly evidenced by high lift values. Similarly, [Target User 2] fatalities appear strongly associated with [Condition Set B]. Factors like [Time of Day / Road Type / Speed] frequently appear in high-confidence or high-lift rules for specific user types."]
- **Limitations/Challenges:** [If applicable, e.g., "While some interesting associations were found, many rules had lift values close to 1, suggesting weak associations. This could be due to data sparsity, the need for different attribute combinations, or limitations of ARM in capturing complex causal relationships. The chosen `min_support` might have excluded rarer but potentially significant patterns."]

#### **6.5 Recommendations for Government**

Based on the insights derived primarily from the association rule mining results (and supported by warehouse analysis):

1.  **Recommendation 1:** [State a specific, actionable recommendation linked directly to one or more strong rules. E.g., Based on Rule 1 linking nighttime pedestrian crashes to pedestrian deaths: "Enhance Pedestrian Nighttime Visibility Infrastructure: Prioritize investment in improved street lighting and marked crosswalks, particularly in [mention areas if rules showed patterns, e.g., urban centres/specific LGAs], and promote high-visibility clothing campaigns."]
2.  **Recommendation 2:** [State a second specific, actionable recommendation linked to different rules/insights. E.g., Based on Rule 2 linking weekend motorcycle use to motorcyclist deaths: "Targeted Weekend Motorcyclist Safety Campaigns: Develop and deploy awareness campaigns focusing on risks specific to weekend recreational riding (e.g., speed on curves, fatigue, protective gear checks) through relevant channels."]
3.  **Recommendation 3:** [State a third specific, actionable recommendation. E.g., Based on rules involving specific crash types/locations: "Conduct Road Safety Audits in High-Risk Corridors: Initiate targeted safety audits on [specific road types, e.g., remote highways] identified through data analysis as having high frequencies of [specific crash types, e.g., single vehicle run-off-road] associated with fatalities."]
4.  **(Optional) Recommendation 4:** [Add more if strong evidence supports them].

## **7. Conclusion**

#### **7.1 Summary of Key Findings**

This project successfully designed and implemented a data warehouse for Australian fatal road crash data, incorporating demographic context via population statistics. Key insights derived from querying and visualizing the warehouse data include [briefly mention 1-2 key findings from visualizations, e.g., specific trends, geographical hotspots]. Furthermore, association rule mining identified several significant patterns, such as [mention 1-2 key findings from ARM, e.g., the strong link between condition X and user type Y fatality]. These findings led to specific recommendations aimed at improving road safety.

#### **7.2 Project Limitations**

Several limitations should be acknowledged:

- **Data Granularity/Scope:** The ARDD data, while comprehensive for fatalities, lacks details on non-fatal crashes, weather conditions at the exact time, traffic volume, or specific road geometry features beyond basic type, limiting the depth of causal analysis.
- **Simplifications:** Dimension simplification (e.g., `Dim_Crash_Type`, `Dim_Holiday`) streamlined the model but reduced analytical detail in those areas.
- **ARM Limitations:** Association rules identify correlations, not necessarily causation. The transactional data format simplifies complex interactions.
- **ETL Assumptions:** Data cleaning and transformation involved necessary assumptions (e.g., handling specific codes, standardizing names) which could influence results.

#### **7.3 Future Work Suggestions**

Future work could enhance this analysis:

- **Incorporate Additional Data:** Integrate weather data, detailed road infrastructure data (e.g., curvature, gradient), traffic volume data, or non-fatal crash data for comparative analysis.
- **Advanced Analytics:** Employ predictive modeling (e.g., classification, regression) to identify crash risk factors or clustering techniques to discover distinct crash typologies.
- **Refine Dimensions:** Develop more comprehensive Time, Crash Type, or Location dimensions if more detailed source data becomes available.
- **Near Real-Time Analysis:** Explore possibilities for integrating more frequent data updates for monitoring emerging trends.

## **8. References** (IEEE Format)

[1] [Full citation for the EU data comparison source mentioned in the prompt]
[2] [Full citation for the Australian road toll source mentioned in the prompt]
[3] Australian Government Department of Infrastructure, Transport, Regional Development, Communications and the Arts. (Dec 2024). _Australian Road Deaths Database - ARDD: Fatal crashes—December 2024—XLSX_. [Online]. Available: [Provide URL if available or indicate source]
[4] Australian Government Department of Infrastructure, Transport, Regional Development, Communications and the Arts. (Dec 2024). _Australian Road Deaths Database - ARDD: Fatalities—December 2024—XLSX_. [Online]. Available: [Provide URL if available or indicate source]
[5] Australian Bureau of Statistics. (2021). _TableBuilder tool_ (for Dwelling Count Data). [Online]. Available: [ABS Website URL] (Accessed: [Date])
[6] Australian Bureau of Statistics. ([Date of publication]). _Population estimates by LGA, Significant Urban Area, Remoteness Area, Commonwealth Electoral Division and State Electoral Division, 2001 to 2023_. [Online]. Available: [ABS Website URL] (Accessed: [Date])
[7] R. Kimball and M. Ross, _The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling_, 3rd ed. Indianapolis, IN: Wiley, 2013.
[8] R. Agrawal and R. Srikant, "Fast algorithms for mining association rules," in _Proc. 20th Int. Conf. Very Large Data Bases (VLDB)_, Santiago, Chile, 1994, pp. 487–499.
[9] J. Han, J. Pei, and Y. Yin, "Mining frequent patterns without candidate generation," in _Proc. ACM SIGMOD Int. Conf. Management of Data_, Dallas, TX, USA, 2000, pp. 1–12.
[10] [Citation for Pandas library, e.g., The Pandas Development Team, "pandas-dev/pandas: Pandas," Zenodo, [DOI], [Year]. Check current citation guidelines.]
[11] [Citation for mlxtend library, e.g., S. Raschka, "Mlxtend: Providing machine learning and data science utilities and extensions to Python’s scientific computing stack," _J. Open Source Softw._, vol. 3, no. 24, p. 638, Apr. 2018. [DOI]]
[12] [Citation for GeoPandas library]
[13] [Citation for PostgreSQL]
[14] [Citation for Tableau/Power BI if documentation referred to]
[15] [Any other specific references used]

## **9. Appendices** (Optional)

- [e.g., Full ETL Python Script]
- [e.g., Full Association Rule Mining Script]
- [e.g., Detailed Data Cleaning Log]
- [e.g., Generative AI Usage Log (if applicable)]
- [**LGA Fatality Rate per 100,000 Population Map**]

**This section corresponds to one of the visualizations answering a business question, specifically addressing geographical risk distribution relative to population.**

**Business Question Addressed:** Which Local Government Areas (LGAs) exhibit the highest relative risk of road fatalities when accounting for their population size, for a selected year?

**Rationale:** While maps showing raw fatality counts identify areas with the most incidents, they are heavily biased towards densely populated LGAs. Calculating the fatality rate per 100,000 population normalizes for population differences, providing a more equitable measure of road safety risk across diverse LGAs. Identifying LGAs with high fatality rates, even if absolute numbers are low, highlights areas where the risk relative to the resident population is significant, potentially indicating infrastructure issues, high through-traffic risks, or other localized factors needing attention. This visualization is crucial for targeted resource allocation and safety interventions.

**Data Sources and Fields Used:**

1.  **`fact_crash`:**

    - `Crash_ID`
    - `Number_Fatalities`: Aggregated to get fatality counts per LGA/Year.
    - `Year`: Used for filtering and linking to the population year.
    - `LGA_name`: Used as the primary key to link crash data to population and GeoJSON data.

2.  **`LGA_pop` (Excel Source - Wide Format):**
    - `LGA code` : The linking key.
    - Columns `2001`, `2002`, ..., `2023`: Contain the Estimated Resident Population (ERP) for each LGA for each year. These are accessed dynamically via a calculated field.
      **I extract and format this table from `Population estimates by LGA, Significant Urban Area, Remoteness Area, Commonwealth Electoral Division and State Electoral Division, 2001 to 2023.xlsx` sheet `Table 1`**
3.  **GeoJSON Source:**
    - `Geometry`: Provides the LGA boundary polygons for map rendering.
    - `LGA Code21`: Used to link the geographic shapes to the data.
    - `Ste Name21`: Used for filtering the map by state.

**Tableau Implementation Steps:**

1.  **Established relationships** :
2.  - `LGA_pop` related to `GeoJSON` on `LGA Code`
    - `fact_crash` related to `LGA_pop` on `LGA name`.
    - `fact_crash` related to `GeoJSON` source on `LGA name`
3.  **Parameter Creation:**
    - Created an Integer parameter named `[Select Year]` with allowable values restricted to the range 2001-2023 (matching available population data)
4.  **Calculated Field:**
    - **`[Selected Year Fatality Count (LGA)]`:**
      ```tableau
      // Calculates total fatalities for the selected year per LGA
      SUM(IF [Year] = [Select Year] THEN [Number_Fatalities] ELSE 0 END)
      ```
    - **`[Selected Year Population (LGA)]`:** (Using the unpivoted approach)

      ```tableau
      // Retrieves population for the selected year from the wide LGA_pop table
      MIN(
          CASE [Select Year]
              WHEN 2001 THEN [2001]
              WHEN 2002 THEN [2002]
              // ... includes all years from 2003 to 2022 ...
              WHEN 2023 THEN [2023]
              ELSE NULL
          END
      )
      ```

    - **`[Fatality Rate per 100k (LGA)]`:**
      ```tableau
      // Calculates the rate, handling potential division by zero
      IF [Selected Year Population (LGA)] > 0 THEN
          ([Selected Year Fatality Count (LGA)] * 100000) / [Selected Year Population (LGA)]
      ELSE
          NULL
      END
      ```
5.  **Map Construction:**
    - In a new worksheet. Use `Geometry` (from GeoJSON) to generate the base map.
    - Dragged `LGA_name` onto the **Detail** shelf on the Marks card.
    - Dragged the calculated field `[Fatality Rate per 100k (LGA)]` onto the **Color** shelf.
    - Ensured the `[Select Year]` parameter control was shown.
6.  **Tooltip**
    - Edited the Tooltip to display `LGA_name`, the selected `Year` (from the parameter), the calculated `Selected Year Fatality Count (LGA)`, `Selected Year Population (LGA)`, and the formatted `Fatality Rate per 100k (LGA)`.

**Visualization:**

![image](https://hackmd.io/_uploads/Bk8xtEfCyg.png)
_Figure X: Road Fatality Rate per 100,000 Population by LGA for [2023]._

**Interpretation of Insights:**

This LGA-level fatality rate map for [2023] reveals considerable geographic variation in road safety risk relative to population. While most LGAs exhibit low-to-moderate rates, a number of sparsely populated regional and remote LGAs display markedly elevated rates (>50 in yellowish color or >100 per 100k in dark green).

But it is crucial to interpret these high rates with caution; they often reflect the significant statistical impact of even a single fatality within a very small resident population base, rather than necessarily indicating consistently extreme underlying risk for residents themselves. The specific LGAs appearing as high-rate 'hotspots' demonstrate considerable volatility year-on-year, suggesting these high rates in low-population areas may be driven by infrequent but high-consequence events, potentially involving through-traffic on major routes within those LGA boundaries.

Therefore, while highlighting areas where fatalities have a disproportionate impact relative to local population, this map underscores the need for analyzing multi-year trends and considering factors beyond resident population when assessing risk in geographically vast and sparsely populated regions like much of Australia

**Limitations:**

- Rates calculated for very low population LGAs can be volatile year-on-year due to small changes in fatality numbers having a large percentage impact.
- The rate reflects fatalities occurring _within_ the LGA boundary relative to the _resident_ population, not necessarily the residency of the person involved in the crash. High rates in some LGAs might be influenced by crashes involving non-residents on major highways passing through.

---
