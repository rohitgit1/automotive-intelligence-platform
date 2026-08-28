import sys
import json
import snowflake.connector
from cortex_agents import CortexAgentsEngine

SNOWFLAKE_CONFIG = {
    "user": "SOUTHPAW21",
    "password": "Vande@20345678",
    "account": "qkxtana-ll44738",
    "warehouse": "AUTOMOTIVE_WH",
    "database": "AUTOMOTIVE_INTELLIGENCE_DB",
    "schema": "PUBLIC"
}

def get_db_connection():
    return snowflake.connector.connect(**SNOWFLAKE_CONFIG)

def tool_get_fleet_health():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM VEHICLES")
        total_vehicles = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC WHERE dtc_error_code != 0")
        total_dtc_errors = cursor.fetchone()[0]
        cursor.execute("SELECT supplier_name, failure_rate_pct FROM V_SUPPLIER_QUALITY_METRICS ORDER BY failure_rate_pct DESC LIMIT 5")
        top_suppliers = [{"supplier": r[0], "failure_rate_pct": r[1]} for r in cursor.fetchall()]
        
        return {
            "status": "success",
            "total_vehicles": total_vehicles,
            "total_dtc_error_events": total_dtc_errors,
            "top_supplier_failure_rates": top_suppliers
        }
    finally:
        cursor.close()
        conn.close()

def tool_investigate_root_cause(supplier: str = None):
    engine = CortexAgentsEngine()
    rca_summary = engine.run_root_cause_analysis_agent(supplier_filter=supplier)
    return {
        "status": "success",
        "investigation_type": "Automated Cortex RCA Agent",
        "root_cause_summary": rca_summary
    }

def tool_forecast_30day_failures():
    engine = CortexAgentsEngine()
    forecast = engine.run_predictive_maintenance_agent(forecast_days=30)
    return {
        "status": "success",
        "horizon_days": 30,
        "predictive_maintenance_plan": forecast
    }

def process_mcp_request(request_raw: str):
    try:
        req = json.loads(request_raw)
        method = req.get("method")
        req_id = req.get("id", 1)

        if method == "initialize":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "Snowflake-Automotive-MCP-Server",
                        "version": "1.0.0"
                    }
                }
            })

        elif method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_fleet_health",
                            "description": "Get real-time automotive fleet health KPIs and DTC error rates.",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "investigate_root_cause",
                            "description": "Run Cortex Root Cause Analysis agent to correlate component defects and weather.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"supplier": {"type": "string", "description": "Optional supplier filter"}}
                            }
                        },
                        {
                            "name": "forecast_30day_failures",
                            "description": "Retrieve 30-day failure predictions and preventive recall recommendations.",
                            "inputSchema": {"type": "object", "properties": {}}
                        }
                    ]
                }
            })

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            if name == "get_fleet_health":
                res = tool_get_fleet_health()
            elif name == "investigate_root_cause":
                res = tool_investigate_root_cause(supplier=args.get("supplier"))
            elif name == "forecast_30day_failures":
                res = tool_forecast_30day_failures()
            else:
                res = {"error": f"Unknown tool: {name}"}

            return json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            })

        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": "Method not found"}
            })

    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}})

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing MCP Tools...")
        print("Fleet Health:", tool_get_fleet_health())
    else:
        # Standard MCP Stdio Loop
        for line in sys.stdin:
            line = line.strip()
            if line:
                response = process_mcp_request(line)
                sys.stdout.write(response + "\n")
                sys.stdout.flush()
