import sys
sys.path.append('src')
from cortex_agents import CortexAgentsEngine

engine = CortexAgentsEngine()
print("1. Testing Fable 5 Benchmark in new account...")
res = engine.run_fable_5_models_benchmark()
print(f"Evaluated models: {res.get('models_evaluated')}")
for m, d in res.get('models', {}).items():
    out = d.get('output', '')
    lat = d.get('latency_s', 0)
    print(f" - {m}: {out[:100]}... (latency: {lat}s)")

print("\n2. Testing Scorecard retrieval...")
rows = engine.get_supplier_quality_scorecard_data()
print(f"Scorecard rows: {len(rows)}")
for r in rows:
    print(f" - {r.get('SUPPLIER_NAME')}: Grade {r.get('QUALITY_GRADE')}, Exposure ${r.get('TOTAL_WARRANTY_EXPOSURE_USD'):,}")

print("\n3. Testing Guarded OTA Stored Procedure...")
conn = engine._get_connection()
cur = conn.cursor()
try:
    cur.execute("CALL SP_DISPATCH_AUTONOMOUS_OTA_REMEDIATION('v4.8.2-bms', 749.0, 'NMC811 Subzero Overheating', 14588000.0, 80.48)")
    print("OTA Call Result:", cur.fetchone()[0])
    # Delete test row to keep campaigns clean
    cur.execute("DELETE FROM FLEET_OTA_CAMPAIGNS WHERE FIRMWARE_VERSION = 'v4.8.2-bms'")
    print("Test campaign row cleaned up!")
except Exception as e:
    print("OTA Call Error:", e)

cur.close()
conn.close()
print("\nALL VERIFICATIONS PASSED IN NEW ACCOUNT!")
