import snowflake.connector
import json
from src.cortex_agents import SNOWFLAKE_CONFIG

conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
cur = conn.cursor()
try:
    search_payload = json.dumps({
        "query": "subzero battery pack P1794 voltage divergence",
        "columns": ["TITLE", "ERROR_CODE", "COMPONENT_TYPE", "CONTENT"],
        "limit": 3
    })
    sql = f"SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW('AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.DTC_BULLETIN_SEARCH_SERVICE', '{search_payload}')"
    cur.execute(sql)
    res = cur.fetchone()[0]
    print("CORTEX SEARCH_PREVIEW SUCCESS!")
    parsed = json.loads(res)
    print("Results returned:", len(parsed.get("results", [])))
    for r in parsed.get("results", []):
        print(f"- {r.get('TITLE')} ({r.get('ERROR_CODE')}): {r.get('CONTENT')[:80]}...")
except Exception as e:
    print("Error:", e)
finally:
    cur.close()
    conn.close()
