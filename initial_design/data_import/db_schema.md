### **1. 事实表（Fact Table）：`fatal_crashes_fact`**

这个表包含事故的核心统计数据：

| 字段名           | 数据类型 | 说明              |
| ---------------- | -------- | ----------------- |
| crash_id         | INT (PK) | 事故唯一标识      |
| date_id          | INT (FK) | 关联日期维度      |
| location_id      | INT (FK) | 关联事故地点维    |
| vehicle_id       | INT (FK) | 关联车辆类型维度  |
| road_type_id     | INT (FK) | 关联道路类型维度  |
| total_fatalities | INT      | 死亡人数          |
| speed_limit      | INT      | 事故路段限速      |
| holiday_id       | INT (FK) | 关联节假日维度    |
| time_of_day      | VARCHAR  | 白天/晚上         |
| day_of_week      | VARCHAR  | 工作日/周末       |
| crash_type       | VARCHAR  | 单车事故/多车事故 |
|                  |          |                   |

------

### **2. 维度表（Dimension Tables）**

#### **（1）日期维度：`date_dim`**

| 字段名      | 数据类型 | 说明         |
| ----------- | -------- | ------------ |
| date_id     | INT (PK) | 日期唯一标识 |
| year        | INT      | 年份         |
| month       | INT      | 月份         |
| day_of_week | VARCHAR  | 星期几       |

------

#### **（2）地点维度：`location_dim`**

| 字段名              | 数据类型 | 说明                                                         |
| ------------------- | -------- | ------------------------------------------------------------ |
| location_id         | INT (PK) | 地点唯一标识                                                 |
| state               | VARCHAR  | 州（NSW, TAS等）                                             |
| national_remoteness | VARCHAR  | 偏远程度（Inner Regional Australia, Outer Regional Australia） |
| SA4_name            | VARCHAR  | SA4 统计区域名称                                             |
| national_LGA_name   | VARCHAR  | LGA 名称                                                     |

------

#### **（3）车辆维度：`vehicle_dim`**

| 字段名            | 数据类型 | 说明                 |
| ----------------- | -------- | -------------------- |
| vehicle_id        | INT (PK) | 车辆唯一标识         |
| bus_involvement   | BOOLEAN  | 是否有公交车         |
| heavy_rigid_truck | BOOLEAN  | 是否涉及重型刚性卡车 |
| articulated_truck | BOOLEAN  | 是否涉及铰接式卡车   |

------

#### **（4）道路类型维度：`road_type_dim`**

| 字段名             | 数据类型 | 说明                                                         |
| ------------------ | -------- | ------------------------------------------------------------ |
| road_type_id       | INT (PK) | 道路类型唯一标识                                             |
| national_road_type | VARCHAR  | 道路类型（Arterial Road, Local Road, National or State Highway） |

------

#### **（5）节假日维度：`holiday_dim`**

| 字段名           | 数据类型 | 说明             |
| ---------------- | -------- | ---------------- |
| holiday_id       | INT (PK) | 节假日唯一标识   |
| christmas_period | BOOLEAN  | 是否在圣诞节期间 |
| easter_period    | BOOLEAN  | 是否在复活节期间 |

------

### **3. 关系建模（Star Schema）**

你的数据仓库模型是一个 **星型模式（Star Schema）**，中心是 `fatal_crashes_fact` 事实表，其他维度表围绕它建立。

```mermaid
graph LR
    %% Define CSS styles for Fact and Dimension tables
    classDef fact fill:#f9f,stroke:#333,stroke-width:2px;
    classDef dim fill:#ccf,stroke:#333,stroke-width:1px;

    %% Fact Table
    F[fact_crash]:::fact

    %% Dimension Tables
    D_Date[dim_date]:::dim
    D_Time[dim_time]:::dim
    D_Location[dim_location]:::dim
    D_Vehicle[dim_vehicle_involvement]:::dim
    D_Road[dim_road_type]:::dim
    D_Speed[dim_speed_limit]:::dim
    D_CrashType[dim_crash_type]:::dim

    %% Supporting Fact Table (connected via Dimension)
    F_Pop[fact_lga_population]:::fact

    %% Relationships (Dimension -> Fact)
    D_Date -- date_sk --> F
    D_Time -- time_sk --> F
    D_Location -- location_sk --> F
    D_Vehicle -- vehicle_involvement_sk --> F
    D_Road -- road_type_sk --> F
    D_Speed -- speed_limit_sk --> F
    D_CrashType -- crash_type_sk --> F

    %% Relationship for Population Data (Dimension -> Supporting Fact)
    D_Location -- location_sk --> F_Pop

    %% Optional: If you had the fact_fatality table
    %% F_Fatality[fact_fatality]:::fact
    %% F -- crash_sk --> F_Fatality
```

