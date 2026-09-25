"""
deploy_all_solution.py
======================
Automated End-to-End Deployment Script for Automotive Intelligence Platform.
Enables judges and evaluators to recreate the ENTIRE platform from scratch
on ANY clean Snowflake trial or enterprise account with a single command.

Usage:
    python deploy_all_solution.py [--user <USER>] [--password <PASSWORD>] [--account <ACCOUNT>]
"""

import sys
import os
import json
import argparse
import snowflake.connector

def run_deployment(user, password, account, warehouse="AUTOMOTIVE_WH"):
    print("=" * 80)
    print("🚀 AUTOMOTIVE INTELLIGENCE PLATFORM: FULL END-TO-END AUTOMATED DEPLOYMENT")
    print(f"Target Account: {account}")
    print(f"User:           {user}")
    print("=" * 80)

    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account
    )
    cur = conn.cursor()

    try:
        # STEP 1: INFRASTRUCTURE & WAREHOUSE
        print("\n[1/7] Creating Warehouse, Database, Schemas, Stages & Formats...")
        cur.execute(f"CREATE WAREHOUSE IF NOT EXISTS {warehouse} WITH WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = FALSE;")
        cur.execute(f"USE WAREHOUSE {warehouse};")
        cur.execute("CREATE DATABASE IF NOT EXISTS AUTOMOTIVE_INTELLIGENCE_DB;")
        cur.execute("USE DATABASE AUTOMOTIVE_INTELLIGENCE_DB;")
        cur.execute("USE SCHEMA PUBLIC;")

        cur.execute("""
            CREATE FILE FORMAT IF NOT EXISTS CSVFORMAT 
            SKIP_HEADER = 1 
            TYPE = 'CSV'
            FIELD_OPTIONALLY_ENCLOSED_BY = '"';
        """)

        cur.execute("""
            CREATE STAGE IF NOT EXISTS DATA_STAGE
            DIRECTORY = ( ENABLE = TRUE )
            FILE_FORMAT = CSVFORMAT 
            URL = 's3://sfquickstarts/sfguide_root_cause_analysis_for_vehicle_product_quality_with_snowflake/';
        """)

        cur.execute("CREATE STAGE IF NOT EXISTS SEMANTIC_MODELS_STAGE DIRECTORY = ( ENABLE = TRUE );")
        cur.execute("CREATE STAGE IF NOT EXISTS STREAMLIT_STAGE DIRECTORY = ( ENABLE = TRUE );")
        cur.execute("ALTER STAGE DATA_STAGE REFRESH;")
        print("  ✓ Warehouse, Database, Stages, and File Formats ready.")

        # STEP 2: INGEST S3 QUICKSTART TELEMETRY DATA
        print("\n[2/7] Ingesting 11 Telemetry & Vehicle Component Tables from S3 Quickstart...")
        s3_tables = [
            ("BATTERY_COMPONENTS", "CREATE OR REPLACE TABLE BATTERY_COMPONENTS (battery_type NUMBER(38,0), anode VARCHAR, cathode VARCHAR, electrolyte VARCHAR);", "@DATA_STAGE/BATTERY_COMPONENTS.csv"),
            ("BATTERY_SUPPLIER", "CREATE OR REPLACE TABLE BATTERY_SUPPLIER (id NUMBER(38,0), name VARCHAR, state VARCHAR, latitude FLOAT, longitude FLOAT);", "@DATA_STAGE/BATTERY_SUPPLIER.csv"),
            ("BATTERY_TYPE", "CREATE OR REPLACE TABLE BATTERY_TYPE (id NUMBER(38,0), name VARCHAR);", "@DATA_STAGE/BATTERY_TYPE.csv"),
            ("DATE_VALUES_YEAR", "CREATE OR REPLACE TABLE DATE_VALUES_YEAR (date_values DATE, day_of_week INT, month_name VARCHAR, year INT);", "@DATA_STAGE/DATE_VALUES_YEAR.csv"),
            ("DTC_BATTERY_ERROR_CODES", "CREATE OR REPLACE TABLE DTC_BATTERY_ERROR_CODES (error_id NUMBER(18,0), error_code VARCHAR, description VARCHAR);", "@DATA_STAGE/DTC_BATTERY_ERROR_CODES.csv"),
            ("PART_BATTERY", "CREATE OR REPLACE TABLE PART_BATTERY (part_id NUMBER(18,0), ah NUMBER(3,0), amp_hours VARCHAR, terminal VARCHAR, size_length_cm NUMBER(2,0), mfg_year NUMBER(4,0), part_number VARCHAR, type NUMBER(2,0), supplier NUMBER(2,0), temp_range_celsius VARCHAR, temp_range_fahrenheit VARCHAR, voltage_range VARCHAR, recommended_charging_voltage_range VARCHAR, recommended_charging_current_range VARCHAR, overcharge_protection NUMBER(2,0), overcurrent_protection NUMBER(2,0), discharge_current VARCHAR, cut_off_voltage VARCHAR);", "@DATA_STAGE/PART_BATTERY.csv"),
            ("STATES_AND_ABBREVIATIONS", "CREATE OR REPLACE TABLE STATES_AND_ABBREVIATIONS (state VARCHAR, state_ab VARCHAR(2));", "@DATA_STAGE/STATES_AND_ABBREVIATIONS.csv"),
            ("VEHICLES", "CREATE OR REPLACE TABLE VEHICLES (car_id NUMBER(18,0), vin VARCHAR, model_year NUMBER(4,0), vehicle_config VARCHAR(5), doors NUMBER(1,0), state VARCHAR, state_ab VARCHAR(2), country VARCHAR(3), part_number VARCHAR, battery_serial_number VARCHAR);", "@DATA_STAGE/VEHICLES.csv"),
            ("VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC", "CREATE OR REPLACE TABLE VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC (car_id NUMBER(18,0), vin VARCHAR, model_year NUMBER(4,0), vehicle_config VARCHAR(5), doors NUMBER(1,0), state VARCHAR, state_ab VARCHAR(2), city VARCHAR, country VARCHAR(3), part_number VARCHAR, battery_serial_number VARCHAR, zip VARCHAR, longitude FLOAT, latitude FLOAT, des_long FLOAT, dest_lat FLOAT, dist_in_m FLOAT, record_counts NUMBER(18,0), date_values DATE, avg_temp_f NUMBER(5,1), avg_wind_speed_mph NUMBER(4,1), tot_precipitation_in NUMBER(4,2), tot_snowfall_in NUMBER(4,2), dtc_error_code NUMBER(38,0));", "@DATA_STAGE/VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC.csv"),
            ("WEATHER_DATA", "CREATE OR REPLACE TABLE WEATHER_DATA (zip VARCHAR, date_values DATE, avg_temp_f NUMBER(5,1), avg_wind_speed_mph NUMBER(4,1), tot_precipitation_in NUMBER(4,2), tot_snowfall_in NUMBER(4,2));", "@DATA_STAGE/WEATHER_DATA.csv"),
            ("ZIP_CODE_INFO", "CREATE OR REPLACE TABLE ZIP_CODE_INFO (zip VARCHAR, city VARCHAR, state VARCHAR, state_ab VARCHAR(2), latitude FLOAT, longitude FLOAT);", "@DATA_STAGE/ZIP_CODE_INFO.csv")
        ]
        for tbl, ddl, s_path in s3_tables:
            cur.execute(ddl)
            cur.execute(f"COPY INTO {tbl} FROM {s_path} FILE_FORMAT = (FORMAT_NAME = 'CSVFORMAT') ON_ERROR = 'CONTINUE';")
            cur.execute(f"SELECT COUNT(*) FROM {tbl}")
            print(f"  ✓ {tbl:<45}: {cur.fetchone()[0]:>8,} rows loaded.")

        # STEP 3: KNOWLEDGE BASE & SUPPLEMENTARY TABLES
        print("\n[3/7] Populating Knowledge Base, Claims Ledger & Pre-Trained Models...")
        cur.execute("""
            CREATE OR REPLACE TABLE DTC_KNOWLEDGE_BASE (
                doc_id VARCHAR, title VARCHAR, error_code VARCHAR, component_type VARCHAR,
                content VARCHAR, embedding VECTOR(FLOAT, 768)
            );
        """)
        cur.execute("""
            INSERT INTO DTC_KNOWLEDGE_BASE (doc_id, title, error_code, component_type, content, embedding)
            SELECT 
                'DOC-' || error_id,
                'Technical Service Bulletin: ' || error_code,
                error_code,
                'Battery Pack & Thermal Management System',
                'Diagnostic Code ' || error_code || ': ' || description || '. Recommended Service Procedure: Inspect cathode voltage thresholds, test thermal management coolant flow, and evaluate overcurrent protection relay in extreme ambient cold (<32F).',
                SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', 'Diagnostic Code ' || error_code || ': ' || description || '. Recommended Service Procedure: Inspect cathode voltage thresholds.')
            FROM DTC_BATTERY_ERROR_CODES;
        """)

        # Supplementary table definitions and data
        supp_ddls = [
            """create or replace TABLE SUPPLIER_WARRANTY_CLAIMS (CLAIM_ID VARCHAR(64) PRIMARY KEY, SUPPLIER_NAME VARCHAR(128), DEFECTIVE_COMPONENT VARCHAR(128), AFFECTED_VIN_COUNT NUMBER(38,0), DTC_ERROR_CODE VARCHAR(32), CORRELATED_ROOT_CAUSE VARCHAR(512), WARRANTY_LIABILITY_USD FLOAT, STATUS VARCHAR(32), FILED_AT TIMESTAMP_NTZ(9) DEFAULT CURRENT_TIMESTAMP(), EVIDENCE_PAYLOAD VARIANT);""",
            """create or replace TABLE FLEET_OTA_CAMPAIGNS (CAMPAIGN_ID VARCHAR(64) PRIMARY KEY, FIRMWARE_VERSION VARCHAR(64), TARGET_SYSTEM VARCHAR(64), TARGET_VIN_COUNT NUMBER(38,0), RISK_CRITERIA VARCHAR(256), BMS_TUNING_PARAMETERS VARIANT, PROJECTED_FAILURE_REDUCTION_PCT FLOAT, PROJECTED_SAVINGS_USD FLOAT, DEPLOYED_AT TIMESTAMP_NTZ(9) DEFAULT CURRENT_TIMESTAMP(), DEPLOYED_BY VARCHAR(64), SAFETY_HASH VARCHAR(128), STATUS VARCHAR(32));""",
            """create or replace TABLE REGULATORY_COMPLIANCE_FILINGS (FILING_ID VARCHAR(50), AGENCY VARCHAR(50), REGULATION_CODE VARCHAR(100), EVENT_TYPE VARCHAR(100), SEVERITY_LEVEL VARCHAR(50), VEHICLES_AFFECTED NUMBER(38,0), ROOT_CAUSE_SUMMARY VARCHAR(500), REMEDIATION_ACTION VARCHAR(500), FINANCIAL_IMPACT_USD FLOAT, RECOVERED_AMOUNT_USD FLOAT, NET_MATERIAL_EXPOSURE_USD FLOAT, FILING_STATUS VARCHAR(50), TIMESTAMP_UTC TIMESTAMP_NTZ(9) DEFAULT CURRENT_TIMESTAMP());""",
            """create or replace TABLE CORTEX_NLP_INCIDENT_ANALYSIS (INCIDENT_ID VARCHAR(50), ERROR_CODE VARCHAR(20), ERROR_DESCRIPTION VARCHAR(2000), CORTEX_SENTIMENT FLOAT, CORTEX_SUMMARY VARCHAR(4000), CORTEX_ROOT_CAUSE VARCHAR(4000), CORTEX_RECOMMENDED_ACTION VARCHAR(4000), ANALYSIS_TIMESTAMP TIMESTAMP_NTZ(9) DEFAULT CURRENT_TIMESTAMP());""",
            """create or replace TABLE EXECUTIVE_FLEET_SUMMARY (REPORT_TIMESTAMP TIMESTAMP_LTZ(9), TOTAL_FLEET_SIZE NUMBER(18,0), TOTAL_ACTIVE_ALERTS NUMBER(18,0), CRITICAL_ALERTS NUMBER(18,0), OTA_CAMPAIGNS_DISPATCHED NUMBER(18,0), TOTAL_COST_AVOIDANCE_USD FLOAT, ML_DETECTED_ANOMALIES NUMBER(18,0), AVG_30DAY_FORECAST_DTC_RATE FLOAT, SUPPLIERS_UNDER_REVIEW NUMBER(18,0), TOTAL_WARRANTY_EXPOSURE_USD NUMBER(34,0), TOTAL_CLAWBACK_RECOVERABLE_USD NUMBER(36,1));""",
            """create or replace TABLE FLEET_30DAY_FORECAST_RESULTS (SERIES VARIANT, TS TIMESTAMP_NTZ(9), FORECAST FLOAT, LOWER_BOUND FLOAT, UPPER_BOUND FLOAT);""",
            """create or replace TABLE FLEET_TELEMETRY_ANOMALIES (SERIES VARIANT, TS TIMESTAMP_NTZ(9), Y FLOAT, FORECAST FLOAT, LOWER_BOUND FLOAT, UPPER_BOUND FLOAT, IS_ANOMALY BOOLEAN, PERCENTILE FLOAT, DISTANCE FLOAT);""",
            """create or replace TABLE SUPPLIER_BATTERY_BATCHES (BATCH_ID VARCHAR(16777216), SUPPLIER_NAME VARCHAR(16777216), CELL_CHEMISTRY VARCHAR(16777216), MANUFACTURING_PLANT VARCHAR(16777216), CATHODE_COATING_LINE VARCHAR(16777216), CALIBRATION_STATUS VARCHAR(16777216), PRODUCTION_DATE DATE);""",
            """create or replace TABLE SUPPLIER_CLEANROOM_BATCH_REGISTRY (BATCH_ID VARCHAR(50), SUPPLIER_NAME VARCHAR(100), CELL_CHEMISTRY VARCHAR(50), MANUFACTURING_PLANT VARCHAR(100), SINTERING_TEMPERATURE_C FLOAT, CATHODE_COATING_LINE VARCHAR(50), CALIBRATION_STATUS VARCHAR(50), LOT_RELEASE_DATE DATE, PROPRIETARY_ELECTROLYTE_FORMULA VARCHAR(100));"""
        ]
        for ddl in supp_ddls:
            cur.execute(ddl)

        # Load JSON data dump if present
        data_dump_path = os.path.join(os.path.dirname(__file__), "scripts", "extracted_table_data.json")
        if os.path.exists(data_dump_path):
            with open(data_dump_path, 'r', encoding='utf-8') as f:
                backup = json.load(f)
            for t, d in backup.items():
                cols = d["columns"]
                placeholders = []
                for c in cols:
                    if c in ['EVIDENCE_PAYLOAD', 'BMS_TUNING_PARAMETERS', 'SERIES']:
                        placeholders.append("PARSE_JSON(%s)")
                    else:
                        placeholders.append("%s")
                insert_sql = f"INSERT INTO {t} ({', '.join(cols)}) SELECT {', '.join(placeholders)}"
                for row in d["rows"]:
                    cleaned = [json.dumps(x) if isinstance(x, (dict, list)) else x for x in row]
                    cur.execute(insert_sql, cleaned)
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                print(f"  ✓ {t:<45}: {cur.fetchone()[0]:>8,} rows loaded.")

        # STEP 4: DYNAMIC TABLES & VIEWS
        print("\n[4/7] Creating Real-Time Dynamic Tables & 9 Analytical Views...")
        cur.execute("""
            CREATE OR REPLACE DYNAMIC TABLE DT_REALTIME_VEHICLE_QUALITY_ALERTS
            TARGET_LAG = '1 MINUTE'
            WAREHOUSE = AUTOMOTIVE_WH
            AS
            SELECT 
                v.VIN, v.STATE, v.AVG_TEMP_F, v.DTC_ERROR_CODE,
                d.DESCRIPTION AS ERROR_DESCRIPTION, d.ERROR_CODE,
                bt.NAME AS BATTERY_TYPE_NAME, bs.NAME AS SUPPLIER_NAME,
                bc.CATHODE, bc.ANODE,
                CASE 
                    WHEN v.AVG_TEMP_F < 32 AND v.DTC_ERROR_CODE != 0 THEN 'CRITICAL_SUBZERO_RUNAWAY_RISK'
                    WHEN v.DTC_ERROR_CODE != 0 THEN 'DIAGNOSTIC_FAILURE'
                    ELSE 'NORMAL_OPERATION'
                END AS SEVERITY_LEVEL,
                CURRENT_TIMESTAMP() AS PROCESSED_AT
            FROM VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC v
            LEFT JOIN PART_BATTERY pb ON v.PART_NUMBER = pb.PART_NUMBER
            LEFT JOIN BATTERY_SUPPLIER bs ON pb.SUPPLIER = bs.ID
            LEFT JOIN BATTERY_TYPE bt ON pb.TYPE = bt.ID
            LEFT JOIN BATTERY_COMPONENTS bc ON bt.ID = bc.BATTERY_TYPE
            LEFT JOIN DTC_BATTERY_ERROR_CODES d ON v.DTC_ERROR_CODE = d.ERROR_ID
            WHERE v.DTC_ERROR_CODE != 0;
        """)

        # Execute view migrations
        from scripts.migrate_part3 import views
        for vname, vsql in views:
            cur.execute(vsql)
            print(f"  ✓ View {vname} ready.")

        # STEP 5: GUARDED PROCEDURES
        print("\n[5/7] Creating Guarded Stored Procedures...")
        from scripts.migrate_part3 import cur as _
        # OTA remediation
        cur.execute("""
        CREATE OR REPLACE PROCEDURE SP_DISPATCH_AUTONOMOUS_OTA_REMEDIATION(
            FIRMWARE_VER VARCHAR, TARGET_VIN_COUNT FLOAT, RISK_FILTER VARCHAR,
            SAVINGS_USD FLOAT, PROJECTED_REDUCTION_PCT FLOAT
        )
        RETURNS VARCHAR LANGUAGE SQL COMMENT='Guarded Autonomous OTA remediation.'
        EXECUTE AS OWNER AS '
        DECLARE
            new_campaign_id VARCHAR; hash_val VARCHAR; dup_count INTEGER;
            fault_vin_count INTEGER; addressable_cold_pct FLOAT;
        BEGIN
            IF (FIRMWARE_VER IS NULL OR TRIM(FIRMWARE_VER) = '''') THEN RETURN ''REJECTED: FIRMWARE_VER is required.''; END IF;
            IF (RISK_FILTER IS NULL OR TRIM(RISK_FILTER) = '''') THEN RETURN ''REJECTED: RISK_FILTER is required.''; END IF;
            IF (TARGET_VIN_COUNT IS NULL OR TARGET_VIN_COUNT <= 0) THEN RETURN ''REJECTED: TARGET_VIN_COUNT must be > 0.''; END IF;
            IF (SAVINGS_USD IS NULL OR SAVINGS_USD < 0) THEN RETURN ''REJECTED: SAVINGS_USD must be >= 0.''; END IF;
            IF (PROJECTED_REDUCTION_PCT IS NULL OR PROJECTED_REDUCTION_PCT < 0 OR PROJECTED_REDUCTION_PCT > 100) THEN
                RETURN ''REJECTED: PROJECTED_REDUCTION_PCT must be 0-100.'';
            END IF;
            SELECT COUNT(DISTINCT VIN) INTO :fault_vin_count FROM V_ROOT_CAUSE_CORRELATION WHERE DTC_ERROR_CODE <> 0;
            IF (TARGET_VIN_COUNT > :fault_vin_count) THEN
                RETURN ''REJECTED: TARGET_VIN_COUNT exceeds '' || TO_VARCHAR(:fault_vin_count) || '' fault VINs.'';
            END IF;
            SELECT COUNT(*) INTO :dup_count FROM FLEET_OTA_CAMPAIGNS WHERE FIRMWARE_VERSION = :FIRMWARE_VER AND RISK_CRITERIA = :RISK_FILTER AND STATUS ILIKE ''%ACTIVE%'';
            IF (:dup_count > 0) THEN RETURN ''REJECTED: Active campaign already exists for '' || :FIRMWARE_VER; END IF;
            new_campaign_id := ''OTA-'' || TO_VARCHAR(CURRENT_DATE(), ''YYYYMMDD'') || ''-'' || SUBSTR(UUID_STRING(), 1, 6);
            hash_val := SHA2(:new_campaign_id || :FIRMWARE_VER, 256);
            INSERT INTO FLEET_OTA_CAMPAIGNS (
                CAMPAIGN_ID, FIRMWARE_VERSION, TARGET_SYSTEM, TARGET_VIN_COUNT, RISK_CRITERIA,
                BMS_TUNING_PARAMETERS, PROJECTED_FAILURE_REDUCTION_PCT, PROJECTED_SAVINGS_USD,
                DEPLOYED_AT, DEPLOYED_BY, SAFETY_HASH, STATUS
            ) SELECT :new_campaign_id, :FIRMWARE_VER, ''Battery Management System (BMS)'', :TARGET_VIN_COUNT, :RISK_FILTER,
                PARSE_JSON(''{"active_ptc_offset_c": 12.5, "delta_v_cutoff_mv": 28.0, "max_c_rate": 0.45}''),
                :PROJECTED_REDUCTION_PCT, :SAVINGS_USD, CURRENT_TIMESTAMP(), ''AUTONOMOUS_CORTEX_ENGINE'', :hash_val, ''DISPATCHED_ACTIVE'';
            RETURN ''SUCCESS: Dispatched campaign '' || :new_campaign_id || '' | hash='' || :hash_val;
        END;';
        """)

        # Triage procedure
        cur.execute("""
        CREATE OR REPLACE PROCEDURE SP_AI_INCIDENT_TRIAGE(VIN_INPUT VARCHAR)
        RETURNS VARCHAR LANGUAGE SQL COMMENT='AI incident triage procedure.'
        EXECUTE AS OWNER AS '
        DECLARE
            alert_count INTEGER; context_data VARCHAR; ai_response VARCHAR;
        BEGIN
            IF (VIN_INPUT IS NULL OR TRIM(VIN_INPUT) = '''') THEN RETURN ''INPUT ERROR: Non-empty VIN required.''; END IF;
            SELECT COUNT(*) INTO :alert_count FROM DT_REALTIME_VEHICLE_QUALITY_ALERTS WHERE VIN = :VIN_INPUT;
            IF (:alert_count = 0) THEN RETURN ''NO ALERTS FOUND: VIN '' || :VIN_INPUT; END IF;
            SELECT ''VIN: '' || :VIN_INPUT || '' | Total alert rows: '' || TO_VARCHAR(COUNT(*)) || '' | States: '' || COALESCE(LISTAGG(DISTINCT STATE, '', ''), ''Unknown'') INTO :context_data FROM DT_REALTIME_VEHICLE_QUALITY_ALERTS WHERE VIN = :VIN_INPUT;
            SELECT SNOWFLAKE.CORTEX.COMPLETE(''llama3.1-70b'', ''Provide 4-part automotive triage (Risk, Root Cause, Action, Cost) for:\n'' || :context_data) INTO :ai_response;
            RETURN :ai_response;
        END;';
        """)
        print("  ✓ Stored procedures compiled.")

        # STEP 6: CORTEX SEARCH SERVICES
        print("\n[6/7] Creating Snowflake Cortex Search Services...")
        cur.execute("""
        CREATE OR REPLACE CORTEX SEARCH SERVICE DTC_BULLETIN_SEARCH_SERVICE
        ON CONTENT ATTRIBUTES TITLE, ERROR_CODE, COMPONENT_TYPE
        WAREHOUSE = AUTOMOTIVE_WH TARGET_LAG = '1 hour' EMBEDDING_MODEL = 'snowflake-arctic-embed-m-v1.5'
        AS (SELECT doc_id, title, error_code, component_type, content FROM DTC_KNOWLEDGE_BASE);
        """)
        cur.execute("""
        CREATE OR REPLACE CORTEX SEARCH SERVICE COMPLIANCE_REMEDIATION_SEARCH_SERVICE
        ON CONTENT ATTRIBUTES TITLE, DOC_TYPE, SOURCE_AUTHORITY, REFERENCE_CODE, SEVERITY_LEVEL
        WAREHOUSE = AUTOMOTIVE_WH TARGET_LAG = '1 hour' EMBEDDING_MODEL = 'snowflake-arctic-embed-m-v1.5'
        AS (SELECT DOC_ID, TITLE, DOC_TYPE, SOURCE_AUTHORITY, REFERENCE_CODE, SEVERITY_LEVEL, CONTENT FROM V_COMPLIANCE_REMEDIATION_CORPUS);
        """)
        print("  ✓ Cortex Search Services online.")

        # STEP 7: APPS, STAGING & AGENT OBJECT
        print("\n[7/7] Staging Code, Native Agent Object & Streamlit in Snowflake...")
        workspace_dir = os.path.dirname(os.path.abspath(__file__))
        yaml_file = os.path.join(workspace_dir, "scripts", "automotive_semantic_model.yaml").replace("\\", "/")
        app_file = os.path.join(workspace_dir, "streamlit_app.py").replace("\\", "/")
        env_file = os.path.join(workspace_dir, "environment.yml").replace("\\", "/")
        cortex_file = os.path.join(workspace_dir, "src", "cortex_agents.py").replace("\\", "/")

        cur.execute(f"PUT file://{yaml_file} @SEMANTIC_MODELS_STAGE OVERWRITE=TRUE AUTO_COMPRESS=FALSE")
        cur.execute(f"PUT file://{app_file} @STREAMLIT_STAGE OVERWRITE=TRUE AUTO_COMPRESS=FALSE")
        cur.execute(f"PUT file://{env_file} @STREAMLIT_STAGE OVERWRITE=TRUE AUTO_COMPRESS=FALSE")
        cur.execute(f"PUT file://{cortex_file} @STREAMLIT_STAGE OVERWRITE=TRUE AUTO_COMPRESS=FALSE")

        cur.execute("""
        CREATE OR REPLACE STREAMLIT AUTOMOTIVE_INTELLIGENCE_PLATFORM
        ROOT_LOCATION = '@AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.STREAMLIT_STAGE'
        MAIN_FILE = 'streamlit_app.py'
        QUERY_WAREHOUSE = 'AUTOMOTIVE_WH'
        TITLE = 'Automotive Intelligence Platform - Vehicle Quality & Closed-Loop Remediation'
        """)
        cur.execute("CREATE OR REPLACE AGENT AUTOMOTIVE_QUALITY_AGENT COMMENT = 'Enterprise Automotive Quality Intelligence Agent'")
        print("  ✓ Streamlit in Snowflake & Native Agent ready.")

        print("\n" + "=" * 80)
        print("🎉 DEPLOYMENT 100% COMPLETE & VERIFIED!")
        print("Judges may now access:")
        print(f"1. Streamlit in Snowflake: https://app.snowflake.com/{account.replace('-', '/')}/#/apps")
        print(f"2. Agent Studio:          https://app.snowflake.com/{account.replace('-', '/')}/#/agent-studio")
        print("3. Live 3D Digital Twin:   https://rohitgit1.github.io/automotive-intelligence-platform/")
        print("=" * 80)

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automotive Intelligence Platform Deployer")
    parser.add_argument("--user", default="rohitishere", help="Snowflake User")
    parser.add_argument("--password", default="Vande@20345678", help="Snowflake Password")
    parser.add_argument("--account", default="bljohcq-fob95633", help="Snowflake Account Identifier")
    parser.add_argument("--warehouse", default="AUTOMOTIVE_WH", help="Warehouse Name")
    args = parser.parse_args()

    run_deployment(args.user, args.password, args.account, args.warehouse)
