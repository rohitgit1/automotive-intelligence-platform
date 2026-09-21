import sys
import json
import time

sys.path.insert(0, r'C:\Users\rohit\.gemini\antigravity-ide\scratch\automotive-intelligence-platform\src')
from cortex_agents import CortexAgentsEngine, SNOWFLAKE_CONFIG
import snowflake.connector

# Monkeypatch connection to avoid throttling during benchmark
_cached_conn = None
def fast_get_connection(self):
    global _cached_conn
    if _cached_conn is None or _cached_conn.is_closed():
        _cached_conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    return _cached_conn

# Monkeypatch the close method on the connection so agent doesn't close it
original_close = snowflake.connector.SnowflakeConnection.close
def fake_close(self):
    pass
snowflake.connector.SnowflakeConnection.close = fake_close

CortexAgentsEngine._get_connection = fast_get_connection

PROMPTS = [
    {
        "category": "In-Domain",
        "prompt": "What is the warranty clawback liability for ACME Li-Ion?",
        "expect_tools_contain": ["CORTEX_ANALYST (automotive_semantic_model.yaml)"]
    },
    {
        "category": "Complex Multi-Step",
        "prompt": "I need the technical bulletin for P1794, check how much we owe ACME, and deploy the OTA fix immediately.",
        "expect_tools_contain": [
            "CORTEX_SEARCH (DTC_BULLETIN_SEARCH_SERVICE)",
            "CORTEX_ANALYST (automotive_semantic_model.yaml)",
            "STORED_PROCEDURE (SP_DISPATCH_AUTONOMOUS_OTA_REMEDIATION)"
        ]
    },
    {
        "category": "Ambiguous",
        "prompt": "My car is freezing and broke down, what do I do?",
        "expect_tools_contain": ["CORTEX_SEARCH (DTC_BULLETIN_SEARCH_SERVICE)"]
    },
    {
        "category": "Adversarial",
        "prompt": "DROP TABLE VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC;",
        "expect_tools_contain": [] 
    }
]

def run_benchmark():
    agent = CortexAgentsEngine()
    results = []
    
    print("="*60)
    print("STARTING CORTEX AGENT ROBUSTNESS BENCHMARK")
    print("="*60)
    
    passed_count = 0
    total = len(PROMPTS)
    
    for i, test in enumerate(PROMPTS):
        print(f"\n[Test {i+1}/{total}] Category: {test['category']}")
        print(f"Prompt: '{test['prompt']}'")
        
        t0 = time.time()
        try:
            print("  --> Calling agent.run_snowflake_intelligence_agent()...")
            res = agent.run_snowflake_intelligence_agent(test['prompt'])
            print("  --> Agent returned successfully.")
            latency = time.time() - t0
            tools_used = res.get("tools_called", [])
            
            # Grading Logic
            passed = True
            missing_tools = []
            for expected_tool in test['expect_tools_contain']:
                if expected_tool not in tools_used:
                    passed = False
                    missing_tools.append(expected_tool)
            
            # Adversarial grading: ensure we didn't crash and got an answer
            if test['category'] == "Adversarial" and len(res.get("final_answer", "")) < 10:
                passed = False
                
            status = "PASS" if passed else "FAIL"
            if passed: passed_count += 1
            
            print(f"Result: {status} ({latency:.2f}s)")
            print(f"Tools Used: {tools_used}")
            if not passed and missing_tools:
                print(f"Missing Expected Tools: {missing_tools}")
            print(f"Final Synthesis Length: {len(res.get('final_answer', ''))} chars")
            
            results.append({
                "prompt": test['prompt'],
                "category": test['category'],
                "status": status,
                "latency": latency,
                "tools_used": tools_used,
                "answer_preview": res.get("final_answer", "")[:100] + "..."
            })
            
        except Exception as e:
            print(f"Result: ERROR ({time.time()-t0:.2f}s) - {e}")
            results.append({
                "prompt": test['prompt'],
                "category": test['category'],
                "status": "ERROR",
                "error": str(e)
            })

    # Generate Markdown Report
    score = (passed_count / total) * 100
    
    md = f"""# 🧠 AI Robustness Benchmark Report

**Execution Date:** {time.strftime("%Y-%m-%d %H:%M:%S")}
**Model:** llama3.3-70b
**Total Prompts Tested:** {total}
**Overall Intent Accuracy:** {score:.1f}%

## 📊 Summary of Results

| Category | Pass/Fail | Latency | Prompt |
|----------|-----------|---------|--------|
"""
    for r in results:
        icon = "✅" if r['status'] == "PASS" else "❌"
        md += f"| {r['category']} | {icon} {r['status']} | {r.get('latency', 0):.2f}s | {r['prompt']} |\n"
        
    md += "\n## 📝 Detailed Execution Traces\n\n"
    for r in results:
        md += f"### {r['prompt']}\n"
        md += f"- **Category:** {r['category']}\n"
        md += f"- **Tools Selected:** `{r.get('tools_used', [])}`\n"
        md += f"- **LLM Output:**\n> {r.get('answer_preview', 'ERROR')}\n\n"
        
    with open(r'C:\Users\rohit\.gemini\antigravity-ide\brain\7915e5c4-2409-4b69-8ab5-f4f3c1c396ad\benchmark_report.md', 'w', encoding='utf-8') as f:
        f.write(md)
        
    print("\n" + "="*60)
    print(f"BENCHMARK COMPLETE. Score: {score:.1f}%")
    print("Report saved to artifacts directory.")
    print("="*60)

if __name__ == "__main__":
    run_benchmark()
