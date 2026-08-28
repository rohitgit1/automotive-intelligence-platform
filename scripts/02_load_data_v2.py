import snowflake.connector

SNOWFLAKE_CONFIG = {
    "user": "SOUTHPAW21",
    "password": "Vande@20345678",
    "account": "qkxtana-ll44738",
    "warehouse": "COMPUTE_WH"
}

TABLE_SCHEMAS_AND_FILES = [
    ("BATTERY_COMPONENTS", """
        CREATE OR REPLACE TABLE BATTERY_COMPONENTS (
            battery_type NUMBER(38, 0), anode VARCHAR, cathode VARCHAR, electrolyte VARCHAR
        );
    """, "@DATA_STAGE/BATTERY_COMPONENTS.csv"),

    ("BATTERY_SUPPLIER", """
        CREATE OR REPLACE TABLE BATTERY_SUPPLIER (
            id NUMBER(38, 0), name VARCHAR, state VARCHAR, latitude FLOAT, longitude FLOAT
        );
    """, "@DATA_STAGE/BATTERY_SUPPLIER.csv"),

    ("BATTERY_TYPE", """
        CREATE OR REPLACE TABLE BATTERY_TYPE (
            id NUMBER(38, 0), name VARCHAR
        );
    """, "@DATA_STAGE/BATTERY_TYPE.csv"),

    ("DATE_VALUES_YEAR", """
        CREATE OR REPLACE TABLE DATE_VALUES_YEAR (
            date_values DATE, day_of_week INT, month_name VARCHAR, year INT
        );
    """, "@DATA_STAGE/DATE_VALUES_YEAR.csv"),

    ("DTC_BATTERY_ERROR_CODES", """
        CREATE OR REPLACE TABLE DTC_BATTERY_ERROR_CODES (
            error_id NUMBER(18, 0), error_code VARCHAR, description VARCHAR
        );
    """, "@DATA_STAGE/DTC_BATTERY_ERROR_CODES.csv"),

    ("PART_BATTERY", """
        CREATE OR REPLACE TABLE PART_BATTERY (
            part_id NUMBER(18, 0), ah NUMBER(3, 0), amp_hours VARCHAR, terminal VARCHAR,
            size_length_cm NUMBER(2, 0), mfg_year NUMBER(4, 0), part_number VARCHAR,
            type NUMBER(2, 0), supplier NUMBER(2, 0), temp_range_celsius VARCHAR,
            temp_range_fahrenheit VARCHAR, voltage_range VARCHAR,
            recommended_charging_voltage_range VARCHAR,
            recommended_charging_current_range VARCHAR,
            overcharge_protection NUMBER(2, 0), overcurrent_protection NUMBER(2, 0),
            discharge_current VARCHAR, cut_off_voltage VARCHAR
        );
    """, "@DATA_STAGE/PART_BATTERY.csv"),

    ("STATES_AND_ABBREVIATIONS", """
        CREATE OR REPLACE TABLE STATES_AND_ABBREVIATIONS (
            state VARCHAR, state_ab VARCHAR(2)
        );
    """, "@DATA_STAGE/STATES_AND_ABBREVIATIONS.csv"),

    ("VEHICLES", """
        CREATE OR REPLACE TABLE VEHICLES (
            car_id NUMBER(18, 0), vin VARCHAR, model_year NUMBER(4, 0), vehicle_config VARCHAR(5),
            doors NUMBER(1, 0), state VARCHAR, state_ab VARCHAR(2), country VARCHAR(3),
            part_number VARCHAR, battery_serial_number VARCHAR
        );
    """, "@DATA_STAGE/VEHICLES.csv"),

    ("VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC", """
        CREATE OR REPLACE TABLE VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC (
            car_id NUMBER(18, 0), vin VARCHAR, model_year NUMBER(4, 0), vehicle_config VARCHAR(5),
            doors NUMBER(1, 0), state VARCHAR, state_ab VARCHAR(2), city VARCHAR,
            country VARCHAR(3), part_number VARCHAR, battery_serial_number VARCHAR,
            zip VARCHAR, longitude FLOAT, latitude FLOAT, des_long FLOAT,
            dest_lat FLOAT, dist_in_m FLOAT, record_counts NUMBER(18, 0),
            date_values DATE, avg_temp_f NUMBER(5, 1), avg_wind_speed_mph NUMBER(4, 1),
            tot_precipitation_in NUMBER(4, 2), tot_snowfall_in NUMBER(4, 2), dtc_error_code NUMBER(38, 0)
        );
    """, "@DATA_STAGE/VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC.csv"),

    ("WEATHER_DATA", """
        CREATE OR REPLACE TABLE WEATHER_DATA (
            zip VARCHAR, date_values DATE, avg_temp_f NUMBER(5, 1), avg_wind_speed_mph NUMBER(4, 1),
            tot_precipitation_in NUMBER(4, 2), tot_snowfall_in NUMBER(4, 2)
        );
    """, "@DATA_STAGE/WEATHER_DATA.csv"),

    ("ZIP_CODE_INFO", """
        CREATE OR REPLACE TABLE ZIP_CODE_INFO (
            zip VARCHAR, city VARCHAR, state VARCHAR, state_ab VARCHAR(2),
            latitude FLOAT, longitude FLOAT
        );
    """, "@DATA_STAGE/ZIP_CODE_INFO.csv")
]

def load_data():
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

        print("\n--- Ingesting Tables into AUTOMOTIVE_INTELLIGENCE_DB ---")
        for table_name, create_ddl, stage_path in TABLE_SCHEMAS_AND_FILES:
            print(f"Creating & loading {table_name}...")
            cursor.execute(create_ddl)
            cursor.execute(f"""
                COPY INTO {table_name}
                FROM {stage_path}
                FILE_FORMAT = (FORMAT_NAME = 'CSVFORMAT')
                ON_ERROR = 'CONTINUE';
            """)
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            cnt = cursor.fetchone()[0]
            print(f"SUCCESS: {table_name} loaded with {cnt:,} rows.")

        print("\nAll 11 tables successfully loaded into Snowflake!")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    load_data()
