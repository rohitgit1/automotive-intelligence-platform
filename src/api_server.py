from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import snowflake.connector
import os
import json
import sys

sys.path.append(os.path.dirname(__file__))
from cortex_agents import CortexAgentsEngine

app = FastAPI(
    title="Automotive Intelligence Platform REST API",
    description="Enterprise REST & Webhook Gateway for Vehicle Telemetry, Cortex RCA, and 30-Day Failure Forecasting",
    version="1.0.0"
)

SNOWFLAKE_CONFIG = {
    "user": "SOUTHPAW21",
    "password": "Vande@20345678",
    "account": "qkxtana-ll44738",
    "warehouse": "AUTOMOTIVE_WH",
    "database": "AUTOMOTIVE_INTELLIGENCE_DB",
    "schema": "PUBLIC"
}

def get_db():
    return snowflake.connector.connect(**SNOWFLAKE_CONFIG)

class RcaRequest(BaseModel):
    supplier_filter: str | None = None
    error_code_filter: str | None = None

class AlertRequest(BaseModel):
    webhook_url: str
    severity: str = "CRITICAL"
    message: str

@app.get("/api/v1/fleet/health")
def get_fleet_health():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM VEHICLES")
        total_vehicles = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM VEHICLES_ZIPCODES_DISTANCES_DATES_WEATHER_DTC WHERE dtc_error_code != 0")
        dtc_errors = cursor.fetchone()[0]
        return {
            "status": "healthy",
            "total_connected_vehicles": total_vehicles,
            "total_dtc_error_events": dtc_errors,
            "platform_status": "ONLINE"
        }
    finally:
        cursor.close()
        conn.close()

@app.post("/api/v1/rca/investigate")
def run_rca(req: RcaRequest):
    engine = CortexAgentsEngine()
    summary = engine.run_root_cause_analysis_agent(
        supplier_filter=req.supplier_filter,
        error_code_filter=req.error_code_filter
    )
    return {
        "status": "success",
        "agent": "Cortex Root Cause Analysis Agent",
        "investigation_result": summary
    }

@app.get("/api/v1/forecast/30day")
def get_forecast():
    engine = CortexAgentsEngine()
    plan = engine.run_predictive_maintenance_agent(forecast_days=30)
    return {
        "status": "success",
        "horizon_days": 30,
        "predictive_maintenance_plan": plan
    }

@app.get("/api/v1/rag/search")
def cortex_rag_search(query: str):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM TABLE(SEARCH_DTC_KNOWLEDGE_BASE('{query.replace(\"'\", \"''\")}'))")
        rows = cursor.fetchall()
        results = [
            {"title": r[0], "error_code": r[1], "content": r[2], "similarity_score": round(r[3], 4)}
            for r in rows
        ]
        return {"query": query, "vector_search_results": results}
    except Exception as e:
        return {"query": query, "error": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.post("/api/v1/alerts/trigger")
def trigger_alert(req: AlertRequest):
    # Simulated webhook notification dispatch
    return {
        "status": "dispatched",
        "destination": req.webhook_url,
        "severity": req.severity,
        "payload": {
            "alert": "AUTOMOTIVE QUALITY TELEMETRY CRITICAL SPIKE",
            "message": req.message,
            "timestamp": "2026-08-29T03:46:00Z"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
