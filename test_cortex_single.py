import time
from src.cortex_agents import CortexAgentsEngine

agent = CortexAgentsEngine()
print("Running run_snowflake_intelligence_agent with real Snowflake Cortex Search Preview + Llama 3.3 70B...", flush=True)
t0 = time.time()
res = agent.run_snowflake_intelligence_agent("Investigate P1794 failure on NMC811 battery packs and show supplier clawback")
print(f"Completed in {time.time()-t0:.2f}s!", flush=True)
print("Tools called:", res.get("tools_called"))
print("Steps:", len(res.get("steps", [])))
print("Bulletins:", len(res.get("bulletins", [])))
print("Data rows:", len(res.get("data", [])) if res.get("data") else 0)
print("Final answer:\n", res.get("final_answer"))
