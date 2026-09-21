import snowflake.connector, time
from src.cortex_agents import SNOWFLAKE_CONFIG
conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
cur = conn.cursor()
t0 = time.time()
print("Calling Cortex COMPLETE llama3.3-70b...", flush=True)
cur.execute("SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.3-70b', 'Why does NMC811 cathode degrade in freezing weather? Answer in 2 sentences.')")
res = cur.fetchone()[0]
print(f"Done in {time.time()-t0:.2f}s:\n{res}", flush=True)
cur.close()
conn.close()
