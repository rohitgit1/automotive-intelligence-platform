-- 03_create_views.sql: Unified Analytical Views for RCA and Forecasting
USE WAREHOUSE AUTOMOTIVE_WH;
USE DATABASE AUTOMOTIVE_INTELLIGENCE_DB;
USE SCHEMA PUBLIC;

-- 1. Daily Fleet Telemetry & Failure Time Series (Input for Forecasting & Monitoring)
CREATE OR REPLACE VIEW V_DAILY_FLEET_DTC_AGGREGATE AS
SELECT 
    v.date_values AS RECORD_DATE,
    COUNT(*) AS TOTAL_TELEMETRY_RECORDS,
    COUNT(CASE WHEN v.dtc_error_code IS NOT NULL AND v.dtc_error_code != 0 THEN 1 END) AS TOTAL_DTC_FAILURES,
    COUNT(DISTINCT v.car_id) AS ACTIVE_VEHICLES_COUNT,
    COUNT(DISTINCT CASE WHEN v.dtc_error_code IS NOT NULL AND v.dtc_error_code != 0 THEN v.car_id END) AS AFFECTED_VEHICLES_COUNT,
    AVG(v.avg_temp_f) AS AVG_AMBIENT_TEMP_F,
    AVG(v.dist_in_m) AS AVG_DISTANCE_METERS
FROM VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC v
GROUP BY v.date_values;

-- 2. Multi-Dimensional Root Cause Analysis View
CREATE OR REPLACE VIEW V_ROOT_CAUSE_CORRELATION AS
SELECT 
    v.car_id,
    v.vin,
    v.model_year,
    v.vehicle_config,
    v.state,
    v.city,
    v.zip,
    v.date_values AS record_date,
    v.dist_in_m,
    v.avg_temp_f,
    v.tot_precipitation_in,
    v.tot_snowfall_in,
    v.dtc_error_code,
    d.error_code,
    d.description AS error_description,
    pb.part_number,
    pb.mfg_year AS battery_mfg_year,
    pb.ah AS battery_amp_hours,
    pb.terminal,
    pb.temp_range_celsius,
    bs.name AS supplier_name,
    bs.state AS supplier_state,
    bt.name AS battery_type_name,
    bc.anode,
    bc.cathode,
    bc.electrolyte,
    CASE 
        WHEN v.avg_temp_f < 32.0 THEN 'Extreme Cold (<32F)'
        WHEN v.avg_temp_f > 85.0 THEN 'Extreme Heat (>85F)'
        ELSE 'Normal Temp (32-85F)'
    END AS TEMPERATURE_CATEGORY
FROM VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC v
LEFT JOIN DTC_BATTERY_ERROR_CODES d ON v.dtc_error_code = d.error_id
LEFT JOIN PART_BATTERY pb ON v.part_number = pb.part_number
LEFT JOIN BATTERY_SUPPLIER bs ON pb.supplier = bs.id
LEFT JOIN BATTERY_TYPE bt ON pb.type = bt.id
LEFT JOIN BATTERY_COMPONENTS bc ON bt.id = bc.battery_type;

-- 3. Supplier Quality Summary View
CREATE OR REPLACE VIEW V_SUPPLIER_QUALITY_METRICS AS
SELECT 
    supplier_name,
    battery_type_name,
    cathode,
    anode,
    COUNT(DISTINCT vin) AS TOTAL_VEHICLES,
    COUNT(CASE WHEN dtc_error_code IS NOT NULL AND dtc_error_code != 0 THEN 1 END) AS TOTAL_DTC_ERRORS,
    ROUND(
        COUNT(CASE WHEN dtc_error_code IS NOT NULL AND dtc_error_code != 0 THEN 1 END) * 100.0 / 
        NULLIF(COUNT(*), 0), 2
    ) AS FAILURE_RATE_PCT,
    AVG(avg_temp_f) AS AVG_OPERATING_TEMP_F,
    AVG(dist_in_m) AS AVG_DISTANCE_DRIVEN
FROM V_ROOT_CAUSE_CORRELATION
GROUP BY supplier_name, battery_type_name, cathode, anode;

-- 4. Vehicle Risk Profile View for 30-Day Failure Prediction
CREATE OR REPLACE VIEW V_VEHICLE_RISK_PROFILE AS
SELECT 
    v.car_id,
    v.vin,
    v.model_year,
    v.state,
    bs.name AS supplier_name,
    bc.cathode,
    COUNT(CASE WHEN v.dtc_error_code IS NOT NULL AND v.dtc_error_code != 0 THEN 1 END) AS HISTORICAL_DTC_COUNT,
    AVG(v.avg_temp_f) AS AVG_OPERATING_TEMP,
    MAX(v.date_values) AS LAST_TELEMETRY_DATE,
    CASE 
        WHEN COUNT(CASE WHEN v.dtc_error_code IS NOT NULL AND v.dtc_error_code != 0 THEN 1 END) >= 3 THEN 'CRITICAL RISK'
        WHEN COUNT(CASE WHEN v.dtc_error_code IS NOT NULL AND v.dtc_error_code != 0 THEN 1 END) >= 1 THEN 'HIGH RISK'
        ELSE 'MODERATE / LOW RISK'
    END AS PREDICTED_RISK_TIER
FROM VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC v
LEFT JOIN PART_BATTERY pb ON v.part_number = pb.part_number
LEFT JOIN BATTERY_SUPPLIER bs ON pb.supplier = bs.id
LEFT JOIN BATTERY_TYPE bt ON pb.type = bt.id
LEFT JOIN BATTERY_COMPONENTS bc ON bt.id = bc.battery_type
GROUP BY v.car_id, v.vin, v.model_year, v.state, bs.name, bc.cathode;
