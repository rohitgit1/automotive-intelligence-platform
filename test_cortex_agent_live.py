import json
import time
from src.cortex_agents import CortexAgentsEngine

agent = CortexAgentsEngine()
queries = [
    "Investigate P1794 failure on NMC811 battery packs and show supplier clawback",
    "Which battery supplier has the highest sub-zero failure rate and what is the contractual warranty clawback amount?",
    "Explain the electrochemical mechanism of cathode crystallization in cold weather and recommend corrective firmware parameters"
]

for q in queries:
    print("\n" + "="*80)
    print("TESTING QUERY:", q)
    t0 = time.time()
    trace = agent.run_snowflake_intelligence_agent(q)
    elapsed = time.time() - t0
    print(f"Elapsed Time: {elapsed:.2f}s")
    print("Tools Called:", trace.get("tools_called"))
    print("Steps count:", len(trace.get("steps", [])))
    print("Bulletins count:", len(trace.get("bulletins", [])))
    print("Final Answer Preview:")
    print(trace.get("final_answer")[:300] + "...")
