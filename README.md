**final report in `__Report Analysing Australian Road Fatal Crash with a Data Warehouse__.pdf`**

**Select and Acquire Datasets**:

- Use the “Fatal Crashes – December 2024” and “Fatalities – December 2024” datasets. Also use “Dwelling Count Data” or “Population Data,” or introduce other relevant sources.

**Requirements Analysis**:

- Define the goal of the data warehouse: to help government and public stakeholders understand the importance of road safety and reduce traffic risks.
- Clarify the business questions the warehouse must answer, for example:
  - What factors most commonly lead to fatal crashes?
  - How do fatal crash counts trend in specific regions?
  - What is the proportion of different road users (e.g., drivers, pedestrians) in fatal crashes?

**Conceptual Schema Design**:

- Draw a Star Schema diagram to identify the data warehouse’s fact and dimension tables citeturn1search2.
- Identify at least eight dimensions, such as time, location, crash type, vehicle type, road conditions, weather conditions, driver age, and gender.
- Define the hierarchy and attributes of each dimension.

**Logical Schema Design**:

- Convert the conceptual model into a logical model, choosing a star or snowflake schema.
- Specify the fields for the fact table and each dimension table, and define their relationships.
- Ensure every table has a primary key, and that the fact table’s foreign keys reference the corresponding dimension table primary keys.

**Physical Schema Design**:

- Select a suitable DBMS (e.g., PostgreSQL).
- Create the actual tables in the DBMS based on your logical design.
- Plan performance optimizations such as indexing and partitioning.

**Data Cleaning and Loading**:

- Clean the raw data: handle missing values, duplicates, and outliers.
- Transform the cleaned data to fit the warehouse schema.
- Use ETL tools or write scripts to extract, transform, and load the data into the warehouse.

**Multidimensional Data Analysis and Visualization**:

- Use SQL queries or OLAP tools for multidimensional analysis to answer your business questions.
- Build dashboards and reports in Power BI or Tableau to present key insights.
- Include map visualizations to show geographic distribution and regional differences.

**Association Rule Mining**:

- Write Python code using an algorithm like Apriori or FP‑Growth for association rule mining.
- Analyze and interpret the top k rules involving “Road User,” ranked by lift and confidence.
- Explain these rules in clear, accessible language.
- Propose at least three actionable recommendations for government policy based on your findings.

**Report**:

- Compile the project report, including:
  - Background and objectives
  - Data description and preprocessing steps
  - Data warehouse design (with Star Schema diagram and database architecture)
  - Multidimensional analysis results and visualizations
  - Association rule mining methods, results, and recommendations
- Ensure the report is clear, well‑structured, and meets submission guidelines.

```
python3 -m venv venv
source venv/bin/activate
pip install openpyxl

```

- Initial dw design 

```mermaid
graph LR
    %% Define CSS styles for Fact and Dimension tables
    classDef fact fill:#f9f,stroke:#333,stroke-width:2px;
    classDef dim fill:#ccf,stroke:#333,stroke-width:1px;

    %% Core Fact Table
    F["fact_crash<br><br>
       crash_sk (PK)<br>
       crash_id<br>
       date_sk (FK)<br>
       time_sk (FK)<br>
       location_sk (FK)<br>
       remoteness_sk (FK)<br>
       vehicle_involvement_sk (FK)<br>
       road_type_sk (FK)<br>
       speed_limit_sk (FK)<br>
       crash_type_sk (FK)<br>
       --------------------<br>
       number_fatalities (Measure)"]:::fact

    %% Fatality Detail Fact Table
    FF["fact_fatality<br><br>
        fatality_sk (PK)<br>
        crash_sk (FK)<br>
        --------------------<br>
        Age (Degenerate Dim)<br>
        Gender (Degenerate Dim)<br>
        RoadUserType (Degenerate Dim)<br>
        fatality_count=1 (Measure)"]:::fact

    %% Dimension Tables (8 total)
    D_Date["dim_date<br><br>
            date_sk (PK)<br>
            full_date<br>
            year, month, day<br>
            day_name, is_weekday<br>
            is_christmas_period<br>
            is_easter_period"]:::dim

    D_Time["dim_time<br><br>
            time_sk (PK)<br>
            time_of_day (HH:MM)<br>
            hour_24<br>
            time_period (e.g., Morning)"]:::dim

    D_Location["dim_location<br><br>
                location_sk (PK)<br>
                lga_code, lga_name<br>
                state<br>
                sa4_name_2021<br>
                dwelling_count_2021"]:::dim

    D_Remoteness["dim_remoteness_area<br><br>
                  remoteness_sk (PK)<br>
                  remoteness_area_name"]:::dim

    D_Vehicle["dim_vehicle_involvement<br><br>
               vehicle_involvement_sk (PK)<br>
               bus_involved<br>
               heavy_rigid_truck_involved<br>
               articulated_truck_involved<br>
               description"]:::dim

    D_Road["dim_road_type<br><br>
            road_type_sk (PK)<br>
            national_road_type"]:::dim

    D_Speed["dim_speed_limit<br><br>
             speed_limit_sk (PK)<br>
             speed_limit (km/h)"]:::dim

    D_CrashType["dim_crash_type<br><br>
                 crash_type_sk (PK)<br>
                 crash_type (Single/Multiple)"]:::dim

    %% Supporting Fact Table (for Population) - Separate analysis context
    F_Pop["fact_lga_population<br><br>
           lga_population_pk (PK)<br>
           location_sk (FK)<br>
           year<br>
           estimated_resident_population"]:::fact

    %% Relationships (Dimension -> Core Fact)
    D_Date -- date_sk --> F
    D_Time -- time_sk --> F
    D_Location -- location_sk --> F
    D_Remoteness -- remoteness_sk --> F
    D_Vehicle -- vehicle_involvement_sk --> F
    D_Road -- road_type_sk --> F
    D_Speed -- speed_limit_sk --> F
    D_CrashType -- crash_type_sk --> F

    %% Relationship (Core Fact -> Fatality Detail Fact)
    F -- crash_sk --> FF

    %% Relationship for Population Data (Dimension -> Supporting Fact)
    D_Location -- location_sk --> F_Pop
```
