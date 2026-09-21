import time, json
import snowflake.connector
from src.cortex_agents import SNOWFLAKE_CONFIG

print("Step 1: Connecting to Snowflake...", flush=True)
conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
cur = conn.cursor()
print("Connected!", flush=True)

print("Step 2: Testing SEARCH_PREVIEW...", flush=True)
payload = json.dumps({
    "query": "Investigate P1794 failure on NMC811 battery packs and show supplier clawback",
    "columns": ["TITLE", "ERROR_CODE", "COMPONENT_TYPE", "CONTENT"],
    "limit": 3
})
cur.execute(f"SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW('AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.DTC_BULLETIN_SEARCH_SERVICE', '{payload}')")
search_res = cur.fetchone()[0]
print("SEARCH_PREVIEW success!", len(search_res), flush=True)

print("Step 3: Testing V_SUPPLIER_WARRANTY_LIABILITY query...", flush=True)
cur.execute("SELECT * FROM V_SUPPLIER_WARRANTY_LIABILITY LIMIT 3")
analyst_rows = cur.fetchall()
print(f"Analyst query success! {len(analyst_rows)} rows", flush=True)

print("Step 4: Testing Llama 3.3 70B COMPLETE call...", flush=True)
cur.execute("SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.3-70b', 'Provide an executive summary of P1794 failure and $25.48M supplier clawback in 2 sentences.')")
llm_res = cur.fetchone()[0]
print("LLM COMPLETE success! Length:", len(llm_res), flush=True)
print("Result:\n", llm_res)

cur.close()
conn.close()
print("ALL DIAGNOSTIC STEPS PASSED!", flush=True)
