import sys
sys.path.append('src')
from cortex_agents import CortexAgentsEngine

engine = CortexAgentsEngine()
conn = engine._get_connection()
cur = conn.cursor()

print("=== 1. SNOWFLAKE TABLES & VIEWS ===")
cur.execute("""
    SELECT table_name, table_type 
    FROM information_schema.tables 
    WHERE table_schema = 'PUBLIC' 
    ORDER BY table_name
""")
for v in cur.fetchall():
    print(f"{v[0]:<45} | {v[1]}")

print("\n=== 2. PROCEDURES ===")
cur.execute("SHOW PROCEDURES IN SCHEMA PUBLIC")
cols = [col[0] for col in cur.description]
name_idx = cols.index('name') if 'name' in cols else 1
arg_idx = cols.index('arguments') if 'arguments' in cols else 2
for p in cur.fetchall():
    print(f"{p[name_idx]:<45} | arguments: {p[arg_idx]}")

print("\n=== 3. V_SUPPLIER_QUALITY_SCORECARD DDL ===")
try:
    cur.execute("SELECT GET_DDL('VIEW', 'PUBLIC.V_SUPPLIER_QUALITY_SCORECARD')")
    print(cur.fetchone()[0])
except Exception as e:
    print("Could not get view DDL:", e)

print("\n=== 4. SP_DISPATCH_AUTONOMOUS_OTA_REMEDIATION DDL ===")
try:
    cur.execute("SELECT GET_DDL('PROCEDURE', 'PUBLIC.SP_DISPATCH_AUTONOMOUS_OTA_REMEDIATION(VARCHAR, FLOAT, VARCHAR, FLOAT, FLOAT)')")
    print(cur.fetchone()[0])
except Exception as e:
    print("Could not get proc DDL:", e)

cur.close()
conn.close()
