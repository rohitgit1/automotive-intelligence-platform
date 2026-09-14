import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import snowflake.connector
from src.cortex_agents import SNOWFLAKE_CONFIG

def create_sp_and_stream():
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    cur = conn.cursor()

    print("1. Creating Stream VEHICLE_TELEMETRY_STREAM...")
    cur.execute("""
    CREATE OR REPLACE STREAM VEHICLE_TELEMETRY_STREAM 
    ON TABLE VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC
    """)
    print("Stream created successfully!")

    print("2. Creating Stored Procedure SP_DISPATCH_AUTONOMOUS_OTA_REMEDIATION...")
    sp_sql = """
CREATE OR REPLACE PROCEDURE SP_DISPATCH_AUTONOMOUS_OTA_REMEDIATION(
    FIRMWARE_VER VARCHAR,
    TARGET_VIN_COUNT FLOAT,
    RISK_FILTER VARCHAR,
    SAVINGS_USD FLOAT
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    new_campaign_id VARCHAR;
    hash_val VARCHAR;
BEGIN
    new_campaign_id := 'OTA-' || TO_VARCHAR(CURRENT_DATE(), 'YYYYMMDD') || '-' || SUBSTR(UUID_STRING(), 1, 6);
    hash_val := SHA2(new_campaign_id || FIRMWARE_VER, 256);
    
    INSERT INTO FLEET_OTA_CAMPAIGNS (
        CAMPAIGN_ID,
        FIRMWARE_VERSION,
        TARGET_SYSTEM,
        TARGET_VIN_COUNT,
        RISK_CRITERIA,
        BMS_TUNING_PARAMETERS,
        PROJECTED_FAILURE_REDUCTION_PCT,
        PROJECTED_SAVINGS_USD,
        DEPLOYED_AT,
        DEPLOYED_BY,
        SAFETY_HASH,
        STATUS
    )
    VALUES (
        :new_campaign_id,
        :FIRMWARE_VER,
        'Battery Thermal Management & Pre-Conditioning System',
        :TARGET_VIN_COUNT,
        :RISK_FILTER,
        PARSE_JSON('{"active_ptc_offset_c": 12.5, "delta_v_cutoff_mv": 28.0, "max_c_rate": 0.45}'),
        84.3,
        :SAVINGS_USD,
        CURRENT_TIMESTAMP(),
        'SNOWFLAKE_STORED_PROCEDURE',
        :hash_val,
        'DISPATCHED_ACTIVE'
    );
    
    RETURN 'SUCCESS: Dispatched campaign ' || :new_campaign_id || ' with SHA256: ' || :hash_val;
END;
$$;
"""
    cur.execute(sp_sql)
    print("Stored Procedure created successfully!")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_sp_and_stream()
