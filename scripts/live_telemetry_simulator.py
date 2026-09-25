import snowflake.connector
import time
import random
import datetime

SNOWFLAKE_CONFIG = {
    "user": "SOUTHPAW21",
    "password": "Vande@20345678",
    "account": "qkxtana-ll44738",
    "warehouse": "AUTOMOTIVE_WH",
    "database": "AUTOMOTIVE_INTELLIGENCE_DB",
    "schema": "PUBLIC"
}

def generate_telemetry_batch(batch_size=10):
    vins = [f"1G1RC6S59J{random.randint(1000000, 9999999)}" for _ in range(batch_size)]
    states = ["MI", "MN", "WI", "ND", "IL"]
    cities = ["Detroit", "Minneapolis", "Milwaukee", "Fargo", "Chicago"]
    suppliers = ["ACME Battery Energy Technologies, Inc."] * 8 + ["123 Battery Manufacturers"] * 2
    
    rows = []
    now = datetime.datetime.utcnow().isoformat()
    for i in range(batch_size):
        # Simulate severe cold soak causing P1794
        temp = random.uniform(-25.0, -15.0)
        dist = random.randint(1000, 50000)
        dtc = "P1794" if random.random() > 0.3 else "0" # High failure rate injected
        dtc_code = 1794 if dtc == "P1794" else 0
        desc = "Battery Voltage Circuit Malfunction" if dtc_code != 0 else "Nominal"
        
        row = (
            vins[i], states[i%len(states)], cities[i%len(cities)], now, 
            dist, temp, dtc_code, dtc, desc, suppliers[i]
        )
        rows.append(row)
    return rows

def run_simulator():
    print("Starting Live Automotive Telemetry Simulator...")
    print("Targeting: VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC")
    
    conn = None
    cur = None
    
    while True:
        try:
            if conn is None or conn.is_closed():
                conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
                cur = conn.cursor()
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Connected to Snowflake successfully.", flush=True)

            sql = """
            INSERT INTO VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC 
            (CAR_ID, VIN, MODEL_YEAR, VEHICLE_CONFIG, DOORS, STATE, STATE_AB, CITY, COUNTRY, 
             PART_NUMBER, BATTERY_SERIAL_NUMBER, ZIP, LONGITUDE, LATITUDE, DES_LONG, DEST_LAT, 
             DIST_IN_M, RECORD_COUNTS, DATE_VALUES, AVG_TEMP_F, AVG_WIND_SPEED_MPH, 
             TOT_PRECIPITATION_IN, TOT_SNOWFALL_IN, DTC_ERROR_CODE)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE(), %s, %s, %s, %s, %s)
            """
            
            insert_data = []
            for _ in range(15):
                car_id = random.randint(1, 10000)
                temp = random.uniform(-28.0, -12.0)
                dist = random.randint(100, 50000)
                is_fail = random.random() > 0.4
                dtc_error_code = 1794 if is_fail else 0
                
                # Use valid column lengths/types
                row = (
                    car_id, "7ieco7ie7iec77473", 2024, "sedan", 4, "Michigan", "MI", "Detroit", "USA",
                    "84AHC352021", "84AHC35202149651", "48201", -83.0458, 42.3314, -83.0, 42.3,
                    dist, 1, temp, 5.0, 0.0, 2.0, dtc_error_code
                )
                insert_data.append(row)
            
            cur.executemany(sql, insert_data)
            conn.commit()
            
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Injected {len(insert_data)} real-time sub-zero telemetry records (P1794 anomalies).", flush=True)
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\nSimulator stopped by user.", flush=True)
            break
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Telemetry simulator connection error: {e}. Reconnecting in 5s...", flush=True)
            if cur:
                try: cur.close()
                except Exception: pass
            if conn:
                try: conn.close()
                except Exception: pass
            conn = None
            cur = None
            time.sleep(5)
            
    if cur:
        try: cur.close()
        except Exception: pass
    if conn:
        try: conn.close()
        except Exception: pass

if __name__ == "__main__":
    run_simulator()
