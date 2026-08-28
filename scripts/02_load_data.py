import snowflake.connector
import os

SNOWFLAKE_CONFIG = {
    "user": "SOUTHPAW21",
    "password": "Vande@20345678",
    "account": "qkxtana-ll44738",
    "warehouse": "COMPUTE_WH"
}

TABLE_FILES = [
    ("BATTERY_COMPONENTS", "@DATA_STAGE/BATTERY_COMPONENTS.csv"),
    ("BATTERY_SUPPLIER", "@DATA_STAGE/BATTERY_SUPPLIER.csv"),
    ("BATTERY_TYPE", "@DATA_STAGE/BATTERY_TYPE.csv"),
    ("DATE_VALUES_YEAR", "@DATA_STAGE/DATE_VALUES_YEAR.csv"),
    ("DTC_BATTERY_ERROR_CODES", "@DATA_STAGE/DTC_BATTERY_ERROR_CODES.csv"),
    ("PART_BATTERY", "@DATA_STAGE/PART_BATTERY.csv"),
    ("STATES_AND_ABBREVIATIONS", "@DATA_STAGE/STATES_AND_ABBREVIATIONS.csv"),
    ("VEHICLES", "@DATA_STAGE/VEHICLES.csv"),
    ("VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC", "@DATA_STAGE/VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC.csv"),
    ("WEATHER_DATA", "@DATA_STAGE/WEATHER_DATA.csv"),
    ("ZIP_CODE_INFO", "@DATA_STAGE/ZIP_CODE_INFO.csv")
]

def load_all_data():
    print("Connecting to Snowflake...")
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    cursor = conn.cursor()

    try:
        print("Setting up Warehouse, Database, and Schema...")
        cursor.execute("CREATE WAREHOUSE IF NOT EXISTS AUTOMOTIVE_WH WITH WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;")
        cursor.execute("USE WAREHOUSE AUTOMOTIVE_WH;")
        cursor.execute("CREATE DATABASE IF NOT EXISTS AUTOMOTIVE_INTELLIGENCE_DB;")
        cursor.execute("USE DATABASE AUTOMOTIVE_INTELLIGENCE_DB;")
        cursor.execute("USE SCHEMA PUBLIC;")

        cursor.execute("""
            CREATE FILE FORMAT IF NOT EXISTS CSVFORMAT 
            SKIP_HEADER = 1 
            TYPE = 'CSV'
            FIELD_OPTIONALLY_ENCLOSED_BY = '"';
        """)

        cursor.execute("""
            CREATE STAGE IF NOT EXISTS DATA_STAGE
            DIRECTORY = ( ENABLE = TRUE )
            FILE_FORMAT = CSVFORMAT 
            URL = 's3://sfquickstarts/sfguide_root_cause_analysis_for_vehicle_product_quality_with_snowflake/';
        """)

        cursor.execute("ALTER STAGE DATA_STAGE REFRESH;")

        print("\n--- Starting Data Ingestion into Snowflake ---")
        for table_name, file_stage_path in TABLE_FILES:
            print(f"Loading table {table_name} from {file_stage_path}...")
            
            # Use CREATE TABLE AS SELECT with INFER_SCHEMA
            copy_sql = f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM TABLE(
                INFER_SCHEMA(
                    LOCATION => '{file_stage_path}',
                    FILE_FORMAT => 'CSVFORMAT'
                )
            );
            """
            try:
                # Direct COPY INTO with ON_ERROR = 'CONTINUE' or automatic schema creation
                cursor.execute(f"""
                    CREATE OR REPLACE TABLE {table_name} USING TEMPLATE (
                        SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
                        FROM TABLE(INFER_SCHEMA(
                            LOCATION => '{file_stage_path}',
                            FILE_FORMAT => 'CSVFORMAT'
                        ))
                    );
                """)
                cursor.execute(f"""
                    COPY INTO {table_name}
                    FROM {file_stage_path}
                    FILE_FORMAT = (FORMAT_NAME = 'CSVFORMAT')
                    MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
                    ON_ERROR = 'CONTINUE';
                """)
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                print(f"✅ Table {table_name} loaded successfully with {row_count:,} rows.")
            except Exception as table_err:
                print(f"Attempting fallback CSV copy for {table_name}: {table_err}")
                # Fallback to simple ingestion if schema inference needs manual schema
                if table_name == "BATTERY_COMPONENTS":
                    cursor.execute("""
                        CREATE OR REPLACE TABLE BATTERY_COMPONENTS (
                            battery_type INT, anode VARCHAR, cathode VARCHAR, electrolyte VARCHAR
                        );
                    """)
                elif table_name == "BATTERY_SUPPLIER":
                    cursor.execute("""
                        CREATE OR REPLACE TABLE BATTERY_SUPPLIER (
                            id INT, name VARCHAR, state VARCHAR, latitude FLOAT, longitude FLOAT
                        );
                    """)
                elif table_name == "BATTERY_TYPE":
                    cursor.execute("""
                        CREATE OR REPLACE TABLE BATTERY_TYPE (
                            id INT, name VARCHAR
                        );
                    """)
                elif table_name == "DTC_BATTERY_ERROR_CODES":
                    cursor.execute("""
                        CREATE OR REPLACE TABLE DTC_BATTERY_ERROR_CODES (
                            error_id INT, error_code VARCHAR, description VARCHAR
                        );
                    """)
                elif table_name == "PART_BATTERY":
                    cursor.execute("""
                        CREATE OR REPLACE TABLE PART_BATTERY (
                            part_id INT, ah INT, amp_hours VARCHAR, terminal VARCHAR,
                            size_length_cm INT, mfg_year INT, part_number VARCHAR,
                            type INT, supplier INT, temp_range_celsius VARCHAR,
                            temp_range_fahrenheit VARCHAR, voltage_range VARCHAR,
                            recommended_charging_voltage_range VARCHAR,
                            recommended_charging_current_range VARCHAR,
                            overcharge_protection INT, overcurrent_protection INT,
                            discharge_current VARCHAR, cut_off_voltage VARCHAR
                        );
                    """)
                elif table_name == "VEHICLES":
                    cursor.execute("""
                        CREATE OR REPLACE TABLE VEHICLES (
                            car_id INT, vin VARCHAR, model_year INT, vehicle_config VARCHAR,
                            doors INT, state VARCHAR, state_ab VARCHAR, country VARCHAR,
                            part_number VARCHAR, battery_serial_number VARCHAR
                        );
                    """)
                elif table_name == "VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC":
                    cursor.execute("""
                        CREATE OR REPLACE TABLE VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC (
                            car_id INT, vin VARCHAR, model_year INT, vehicle_config VARCHAR,
                            doors INT, state VARCHAR, state_ab VARCHAR, city VARCHAR,
                            country VARCHAR, part_number VARCHAR, battery_serial_number VARCHAR,
                            zip VARCHAR, longitude FLOAT, latitude FLOAT, des_long FLOAT,
                            dest_lat FLOAT, dist_in_m FLOAT, record_counts INT,
                            date_values DATE, avg_temp_f FLOAT, avg_wind_speed_mph FLOAT,
                            tot_precipitation_in FLOAT, tot_snowfall_in FLOAT, dtc_error_code INT
                        );
                    """)
                elif table_name == "WEATHER_DATA":
                    cursor.execute("""
                        CREATE OR REPLACE TABLE WEATHER_DATA (
                            zip VARCHAR, date_values DATE, avg_temp_f FLOAT, avg_wind_speed_mph FLOAT,
                            tot_precipitation_in FLOAT, tot_snowfall_in FLOAT
                        );
                    """)
                elif table_name == "ZIP_CODE_INFO":
                    cursor.execute("""
                        CREATE OR REPLACE TABLE ZIP_CODE_INFO (
                            zip VARCHAR, city VARCHAR, state VARCHAR, state_ab VARCHAR,
                            latitude FLOAT, longitude FLOAT
                        );
                    """)
                elif table_name == "DATE_VALUES_YEAR":
                    cursor.execute("""
                        CREATE OR REPLACE TABLE DATE_VALUES_YEAR (
                            date_values DATE, day_of_week INT, month_name VARCHAR, year INT
                        );
                    """)
                elif table_name == "STATES_AND_ABBREVIATIONS":
                    cursor.execute("""
                        CREATE OR REPLACE TABLE STATES_AND_ABBREVIATIONS (
                            state VARCHAR, state_ab VARCHAR
                        );
                    """)
                
                cursor.execute(f"""
                    COPY INTO {table_name}
                    FROM {file_stage_path}
                    FILE_FORMAT = (FORMAT_NAME = 'CSVFORMAT')
                    ON_ERROR = 'CONTINUE';
                """)
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                print(f"✅ Fallback loaded {table_name} successfully with {row_count:,} rows.")

        print("\n🎉 All 11 hackathon tables ingested successfully!")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    load_all_data()
